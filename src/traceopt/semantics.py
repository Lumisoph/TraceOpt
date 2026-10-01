"""受限 POSIX 单命令的词法路径 Effect；未知语义必须作为屏障。"""

import posixpath
import shlex
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandEffect:
    """路径资源覆盖自身和后代；不解析链接或外部环境。"""

    command: str
    argv: tuple[str, ...]
    cwd: str
    reads: tuple[str, ...] = ()
    writes: tuple[str, ...] = ()
    unknown: bool = False
    reason: str = ""


def _path(value: str, cwd: str) -> str:
    if not value or value == "-" or "\x00" in value or value.startswith("//"):
        raise ValueError("路径为空、标准输入或含特殊形式")
    path = posixpath.normpath(posixpath.join(cwd, value))
    if any(path == prefix or path.startswith(prefix + "/")
           for prefix in ("/dev", "/proc", "/sys")):
        raise ValueError("特殊设备或系统路径不在支持范围")
    return path


def _traversal_reads(value: str, cwd: str) -> tuple[str, ...]:
    """保留被 .. 消去的目录前提，避免丢失路径可达性依赖。"""
    current = "/" if value.startswith("/") else cwd
    reads = []
    for part in value.split("/"):
        if part == "..":
            reads.append(_path(current, "/"))
        current = posixpath.normpath(posixpath.join(current, part))
    return tuple(reads)


def analyze_command(command: str, *, cwd: str) -> CommandEffect:
    """识别白名单形式，不读取文件，不执行程序；未知返回中文原因。"""
    argv: tuple[str, ...] = ()
    try:
        if not isinstance(command, str) or not isinstance(cwd, str):
            raise ValueError("命令和工作目录必须是字符串")
        if not cwd.startswith("/") or cwd.startswith("//") or "\\" in cwd:
            raise ValueError("必须提供明确的 POSIX 绝对工作目录")
        cwd = _path(cwd, "/")
        if any(c in command for c in "$`|;&<>()[]{}*?~#\n\r\\\x00"):
            raise ValueError("包含不支持的 shell 控制、展开或转义语法")
        try:
            argv = tuple(shlex.split(command, posix=True))
        except ValueError as exc:
            raise ValueError("命令引号未闭合或语法无法解析") from exc
        if not argv:
            raise ValueError("命令不能为空")
        name, *args = argv
        options: list[str] = []
        options_ended = False
        while args and args[0].startswith("-"):
            option = args.pop(0)
            if option == "--":
                options_ended = True
                break
            if name in ("head", "tail") and option == "-n":
                if not args or not args[0].isascii() or not args[0].isdigit():
                    raise ValueError("-n 必须跟随非负十进制行数")
                args.pop(0)
            options.append(option)
        allowed = {
            "cat": set(), "head": {"-n"}, "tail": {"-n"},
            "wc": {"-l", "-w", "-c"}, "sort": set(), "uniq": set(),
            "grep": {"-n", "-i", "-F"},
            "rg": {"--no-config", "--no-ignore", "-n", "-i", "-F"},
            "ls": {"-a", "-l", "-la"}, "find": set(), "touch": set(),
            "mkdir": {"-p"}, "rm": {"-f"}, "cp": set(), "mv": set(),
        }
        if name not in allowed:
            raise ValueError("命令不在支持白名单中")
        if any(option not in allowed[name] for option in options):
            raise ValueError("命令包含不支持的选项")
        if name == "rg" and not {"--no-config", "--no-ignore"}.issubset(options):
            raise ValueError("rg 必须显式禁用配置和忽略规则")
        if name in ("grep", "rg"):
            if not args:
                raise ValueError("搜索命令缺少模式")
            args.pop(0)
        if name == "find":
            if len(args) not in (3, 4) or args[1:3] != ["-type", "f"] or (
                    len(args) == 4 and args[3] != "-print0"):
                raise ValueError("find 仅支持 PATH -type f，可追加 -print0")
            args = args[:1]
        if not args or (not options_ended and any(arg.startswith("-") for arg in args)):
            raise ValueError("必须显式提供路径，且不支持后置选项或标准输入")
        if name in ("sort", "uniq") and len(args) != 1:
            raise ValueError("此命令只支持一个输入文件")
        if name in ("cp", "mv") and len(args) != 2:
            raise ValueError("复制或移动必须提供一个源和一个目标")
        paths = tuple(dict.fromkeys(_path(arg, cwd) for arg in args))
        reads, writes = paths, ()
        if name in ("mkdir", "rm"):
            reads, writes = (), paths
        elif name == "touch":
            reads, writes = paths, paths
        elif name in ("cp", "mv"):
            source, target = (_path(arg, cwd) for arg in args)
            reads = (source,)
            writes = (target,) if name == "cp" else tuple(dict.fromkeys((source, target)))
        elif name == "rg":
            reads = tuple(dict.fromkeys((*paths, cwd)))
        traversal = (path for arg in args for path in _traversal_reads(arg, cwd))
        reads = tuple(dict.fromkeys((*reads, *traversal)))
        return CommandEffect(command, argv, cwd, reads, writes)
    except ValueError as exc:
        return CommandEffect(command, argv, cwd, unknown=True, reason=str(exc))
