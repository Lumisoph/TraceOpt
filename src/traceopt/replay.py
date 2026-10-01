"""在私有仓库副本中验证受限 cat 循环改写，不执行任意轨迹命令。"""

import base64
import hashlib
import math
import os
import posixpath
import shlex
import shutil
import signal
import stat
import subprocess
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .binding import DetectedLoop, detect_runtime_loops
from .trajectory import Trajectory


class ReplayError(ValueError):
    """重放前提或实际执行不满足验证要求。"""


@dataclass(frozen=True)
class Toolchain:
    bash: str
    cat: str
    find: str


@dataclass(frozen=True)
class StateEntry:
    path: str
    kind: str
    sha256: str | None
    size: int
    mode: int
    mtime_ns: int


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout_b64: str
    stderr_b64: str


@dataclass(frozen=True)
class ReplayReport:
    source_sha256: str
    prefix_sha256: str
    script: str
    tool_hashes: tuple[tuple[str, str], ...]
    original: tuple[CommandResult, ...]
    optimized: tuple[CommandResult, ...]
    initial_state: tuple[StateEntry, ...]
    original_state: tuple[StateEntry, ...]
    optimized_state: tuple[StateEntry, ...]
    equivalent: bool
    state_unchanged: bool
    matches_recording: bool
    successful: bool
    original_tool_boundaries: int
    optimized_tool_boundaries: int


def discover_toolchain() -> Toolchain:
    """发现本机 Bash 与标准工具；Windows 使用 Git 自带工具而非 WSL 启动器。"""
    if os.name == "nt":
        git = shutil.which("git")
        if git is None:
            raise ReplayError("重放需要已安装的 Git Bash、cat 和 find")
        root = Path(git).parent.parent
        tools = Toolchain(str(root / "bin/bash.exe"), str(root / "usr/bin/cat.exe"),
                          str(root / "usr/bin/find.exe"))
    else:
        tools = Toolchain(*(shutil.which(name) or "" for name in ("bash", "cat", "find")))
    if any(not Path(path).is_file() for path in (tools.bash, tools.cat, tools.find)):
        raise ReplayError("重放工具缺失：需要 Bash、cat 和 find")
    return tools


def snapshot_repository(repository: str | Path) -> tuple[StateEntry, ...]:
    """记录目录及普通文件，拒绝别名和特殊对象；忽略读取产生的 atime。"""
    root = Path(repository).absolute()
    entries = []

    def visit(path: Path) -> None:
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ReplayError("仓库含符号链接或重解析点，无法按普通路径模型重放")
        relative = path.relative_to(root).as_posix()
        if stat.S_ISDIR(info.st_mode):
            entries.append(StateEntry(relative, "directory", None, 0,
                                      stat.S_IMODE(info.st_mode), info.st_mtime_ns))
            for child in sorted(path.iterdir()):
                visit(child)
        elif stat.S_ISREG(info.st_mode):
            if info.st_nlink != 1:
                raise ReplayError("仓库含硬链接，无法按普通路径模型重放")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            entries.append(StateEntry(relative, "file", digest, info.st_size,
                                      stat.S_IMODE(info.st_mode), info.st_mtime_ns))
        else:
            raise ReplayError("仓库含特殊文件，拒绝重放")

    try:
        visit(root)
        if not entries or entries[0].kind != "directory":
            raise ReplayError("仓库路径必须是目录")
    except OSError as exc:
        raise ReplayError("无法读取仓库快照") from exc
    return tuple(entries)


def _environment(tools: Toolchain) -> dict[str, str]:
    result = {"PATH": str(Path(tools.cat).parent), "LANG": "C", "LC_ALL": "C",
              "MSYS2_ARG_CONV_EXCL": "*"}
    for key in ("SystemRoot", "WINDIR", "TEMP", "TMP"):
        if key in os.environ:
            result[key] = os.environ[key]
    return result


def _run(argv: list[str], cwd: Path, environment: dict[str, str], timeout: float):
    options = ({"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW}
               if os.name == "nt" else {"start_new_session": True})
    try:
        with subprocess.Popen(argv, cwd=cwd, env=environment, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, **options) as process:
            try:
                stdout, stderr = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired as exc:
                if os.name == "nt":
                    subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                                   capture_output=True, timeout=5)
                else:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                if process.poll() is None:
                    process.kill()
                process.communicate(timeout=5)
                raise ReplayError("重放超时，本次执行未通过验证") from exc
            return process.returncode, stdout, stderr
    except OSError as exc:
        raise ReplayError("无法启动重放工具") from exc


def _result(code: int, stdout: bytes, stderr: bytes) -> CommandResult:
    return CommandResult(code, base64.b64encode(stdout).decode("ascii"),
                         base64.b64encode(stderr).decode("ascii"))


def _relative(path: str, virtual_root: str) -> str:
    if (not path.startswith("/") or ".." in PurePosixPath(path).parts
            or "\\" in path or "\x00" in path or posixpath.normpath(path) != path):
        raise ReplayError("虚拟路径必须规范且不能包含父目录跳转")
    try:
        relative = PurePosixPath(path).relative_to(virtual_root).as_posix()
    except ValueError as exc:
        raise ReplayError("轨迹路径超出提供的虚拟仓库根") from exc
    if os.name == "nt" and any(":" in part for part in PurePosixPath(relative).parts):
        raise ReplayError("虚拟路径含 Windows 不支持的驱动器或数据流语法")
    return relative


def _script(paths: tuple[str, ...]) -> str:
    # 路径只作为安全引用的数据，循环正文固定，不拼入轨迹的任意代码。
    return ("#!/usr/bin/env bash\nset -u\nrepo=$1\nartifacts=$2\ncat_bin=$3\nindex=0\n"
            + "for relative in " + shlex.join(paths) + "; do\n"
            + '  "$cat_bin" -- "$repo/$relative" > "$artifacts/$index.stdout" '
              '2> "$artifacts/$index.stderr"\n'
            + "  code=$?\n"
            + '  printf "%s\\n" "$code" > "$artifacts/$index.status"\n'
            + "  index=$((index + 1))\ndone\n")


def replay_cat_loop(
    trajectory: Trajectory, loop: DetectedLoop, *, repository: str | Path,
    virtual_root: str, cwd_by_call: Mapping[str, str], timeout: float = 10,
    tools: Toolchain | None = None,
) -> ReplayReport:
    """重放候选片段；输入仓库是该片段初始状态，不是整个会话的初始状态。"""
    if type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0:
        raise ReplayError("超时必须是正的有限秒数")
    if loop not in detect_runtime_loops(trajectory, cwd_by_call=cwd_by_call):
        raise ReplayError("循环计划与当前轨迹或上下文不一致")
    if loop.plan.template_prefix != ("cat",):
        raise ReplayError("当前可执行改写只支持单文件 cat 模板")
    _relative(virtual_root, virtual_root)
    relative_paths = tuple(_relative(path, virtual_root) for path in loop.plan.paths)
    original_paths = []
    for index in loop.event_indices:
        event = trajectory.events[index]
        operand = shlex.split(event.command)[1]
        if ".." in PurePosixPath(operand).parts:
            raise ReplayError("原始操作数含父目录跳转，拒绝改写")
        original_paths.append(_relative(posixpath.normpath(posixpath.join(
            cwd_by_call[event.call_id], operand)), virtual_root))
    recorded = {e.call_id: e for e in trajectory.events if e.kind == "tool_result"}
    if any(cid not in recorded or recorded[cid].returncode != 0
           or recorded[cid].raw_output is None for cid in loop.call_ids):
        raise ReplayError("消费者缺少完整成功的历史结果，无法核对重放")
    producer = trajectory.events[loop.plan.producer_event_index]
    producer_root = shlex.split(producer.command)[1]
    producer_relative = _relative(posixpath.normpath(posixpath.join(
        cwd_by_call[producer.call_id], producer_root)), virtual_root)
    source = Path(repository).absolute()
    initial = snapshot_repository(source)
    tools = tools or discover_toolchain()
    environment = _environment(tools)
    try:
        tool_hashes = tuple((name, hashlib.sha256(Path(path).read_bytes()).hexdigest())
                            for name, path in (("bash", tools.bash), ("cat", tools.cat),
                                               ("find", tools.find)))
        script = _script(relative_paths)
        with tempfile.TemporaryDirectory(prefix="traceopt-replay-") as directory:
            temporary_root = Path(directory).resolve()
            baseline, workspace, artifacts = (temporary_root / name for name in
                                               ("baseline", "workspace", "artifacts"))
            shutil.copytree(source, baseline)
            shutil.copytree(baseline, workspace)
            artifacts.mkdir()
            if (snapshot_repository(baseline) != initial
                    or snapshot_repository(workspace) != initial):
                raise ReplayError("仓库复制后状态不一致，拒绝重放")
            code, output, _ = _run([tools.find, (workspace / producer_relative).as_posix(),
                                   "-type", "f", "-print0"], workspace, environment, timeout)
            if code != 0 or not output.endswith(b"\0"):
                raise ReplayError("重新枚举路径失败")
            observed_paths = tuple(Path(item.decode("utf-8")).relative_to(workspace).as_posix()
                                   for item in output[:-1].split(b"\0"))
            if observed_paths != relative_paths:
                raise ReplayError("当前仓库枚举结果与前缀绑定不一致")
            original = tuple(_result(*_run([tools.cat, "--", (workspace / path).as_posix()],
                                          workspace, environment, timeout))
                             for path in original_paths)
            original_state = snapshot_repository(workspace)
            # 仅删除本次创建的固定 workspace；核对解析路径后才递归清理。
            if workspace.resolve().parent != temporary_root or workspace.name != "workspace":
                raise ReplayError("临时工作目录越界，拒绝清理")
            for entry in original_state:
                target = workspace / entry.path
                if entry.kind == "directory":
                    target.chmod(entry.mode | stat.S_IWUSR | stat.S_IXUSR)
                elif os.name == "nt":
                    target.chmod(entry.mode | stat.S_IWRITE)
            shutil.rmtree(workspace)
            shutil.copytree(baseline, workspace)
            if snapshot_repository(workspace) != initial:
                raise ReplayError("优化执行前未能恢复相同初始状态")
            script_path = temporary_root / "rewrite.sh"
            script_path.write_text(script, encoding="utf-8", newline="\n")
            code, _, stderr = _run([tools.bash, "--noprofile", "--norc", script_path.as_posix(),
                                    workspace.as_posix(), artifacts.as_posix(),
                                    Path(tools.cat).as_posix()], workspace, environment, timeout)
            if code != 0 or stderr:
                raise ReplayError("批处理脚本执行失败")
            optimized = tuple(_result(int((artifacts / f"{i}.status").read_text()),
                                      (artifacts / f"{i}.stdout").read_bytes(),
                                      (artifacts / f"{i}.stderr").read_bytes())
                              for i in range(len(relative_paths)))
            optimized_state = snapshot_repository(workspace)
        if snapshot_repository(source) != initial:
            raise ReplayError("重放期间源仓库发生变化，证据无效")
    except ReplayError:
        raise
    except (OSError, UnicodeError, ValueError) as exc:
        raise ReplayError("重放文件或输出无法读取") from exc
    state_unchanged = initial == original_state == optimized_state
    equivalent = original == optimized and state_unchanged
    try:
        matches = all(
            base64.b64decode(result.stdout_b64) == recorded[cid].raw_output.encode("utf-8")
            and result.returncode == recorded[cid].returncode
            for cid, result in zip(loop.call_ids, original, strict=True))
    except UnicodeError as exc:
        raise ReplayError("历史输出不能表示为 UTF-8，无法核对记录") from exc
    successful = equivalent and matches and all(result.returncode == 0 for result in original)
    return ReplayReport(trajectory.source_sha256, loop.plan.prefix_sha256, script, tool_hashes,
                        original, optimized, initial, original_state, optimized_state,
                        equivalent, state_unchanged, matches, successful, len(original), 1)
