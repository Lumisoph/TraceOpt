"""从前缀观察构造路径绑定计划，再独立检查后续命令的结构匹配。"""

import hashlib
import json
import posixpath
import shlex
from collections.abc import Mapping
from dataclasses import asdict, dataclass

from .dependency import build_dependencies
from .semantics import CommandEffect, analyze_command
from .trajectory import Event, Trajectory


@dataclass(frozen=True)
class LoopPlan:
    producer_call_id: str
    producer_event_index: int
    observation_event_index: int
    first_call_id: str
    prefix_end_index: int
    cwd: str
    paths: tuple[str, ...]
    template_prefix: tuple[str, ...]
    predicted_argv: tuple[tuple[str, ...], ...]
    prefix_sha256: str


@dataclass(frozen=True)
class DetectedLoop:
    plan: LoopPlan
    call_ids: tuple[str, ...]
    event_indices: tuple[int, ...]


def _body(event: Event, cwd: str) -> tuple[tuple[str, ...], str] | None:
    effect = analyze_command(event.command, cwd=cwd)
    if effect.unknown or effect.writes:
        return None
    argv = effect.argv
    supported = (
        (argv[0] in ("cat", "sort", "uniq") and len(argv) == 2)
        or (argv[0] in ("head", "tail") and (len(argv) == 2
            or (len(argv) == 4 and argv[1] == "-n")))
        or (argv[0] == "wc" and (len(argv) == 2
            or (len(argv) == 3 and argv[1] in ("-l", "-w", "-c"))))
    )
    if not supported:
        return None
    return argv[:-1], posixpath.normpath(posixpath.join(effect.cwd, argv[-1]))


def _paths(raw: str | None, cwd: str, root: str) -> tuple[str, ...] | None:
    if not raw or not raw.endswith("\x00"):
        return None
    values = raw[:-1].split("\x00")
    if len(values) < 2 or any(not v for v in values):
        return None
    paths = []
    for value in values:
        effect = analyze_command(shlex.join(("cat", value)), cwd=cwd)
        if effect.unknown:
            return None
        path = posixpath.normpath(posixpath.join(cwd, value))
        if path == root or not (root == "/" or path.startswith(root + "/")):
            return None
        paths.append(path)
    if len(set(paths)) != len(paths):
        return None
    return tuple(paths)


def infer_loop_at(
    trajectory: Trajectory, start_event_index: int, *, cwd_by_call: Mapping[str, str],
) -> LoopPlan | None:
    """仅读取截至指定消费者调用的前缀，不以未来输出推断参数。"""
    return _infer_loop_at(trajectory, start_event_index, cwd_by_call=cwd_by_call,
                          check_dependencies=True)


def _infer_loop_at(
    trajectory: Trajectory, start_event_index: int, *, cwd_by_call: Mapping[str, str],
    check_dependencies: bool,
) -> LoopPlan | None:
    if (type(start_event_index) is not int or start_event_index < 0
            or start_event_index >= len(trajectory.events)):
        raise ValueError("首调用事件索引无效")
    prefix = trajectory.events[:start_event_index + 1]
    first = prefix[-1]
    if first.kind != "tool_call":
        raise ValueError("起点必须是工具调用事件")
    cwd = cwd_by_call.get(first.call_id, "")
    body = _body(first, cwd)
    if body is None:
        return None
    cwd = analyze_command(first.command, cwd=cwd).cwd
    template, first_path = body
    calls = {e.call_id: e for e in prefix if e.kind == "tool_call"}
    completed = {e.call_id for e in prefix if e.kind == "tool_result"}
    if any(cid not in completed for cid in calls if cid != first.call_id):
        return None
    for observation in reversed(prefix[:-1]):
        if observation.kind != "tool_result" or observation.returncode != 0:
            continue
        producer = calls.get(observation.call_id)
        if producer is None:
            continue
        producer_effect = analyze_command(
            producer.command, cwd=cwd_by_call.get(producer.call_id, ""))
        argv = producer_effect.argv
        if (producer_effect.unknown or len(argv) != 5 or argv[0] != "find"
                or argv[2:] != ("-type", "f", "-print0")):
            continue
        root = posixpath.normpath(posixpath.join(producer_effect.cwd, argv[1]))
        paths = _paths(observation.raw_output, producer_effect.cwd, root)
        if paths is None or paths[0] != first_path:
            continue
        between = [e for e in prefix if observation.index < e.index < first.index]
        if any(e.kind == "exit" or e.role in ("user", "system") for e in between):
            continue
        effects = [analyze_command(e.command, cwd=cwd_by_call.get(e.call_id, ""))
                   for e in between if e.kind == "tool_call"]
        guard = CommandEffect("枚举与绑定资源", (), cwd, reads=(root, *paths))
        if check_dependencies and any(
            e.target == len(effects) for e in build_dependencies([*effects, guard])
        ):
            continue
        predicted = tuple((*template, path) for path in paths)
        if any(analyze_command(shlex.join(args), cwd=cwd).unknown for args in predicted):
            continue
        payload = {
            "events": [asdict(e) for e in prefix],
            "cwd_by_call": {cid: cwd_by_call.get(cid) for cid in calls},
        }
        digest = hashlib.sha256(json.dumps(payload, ensure_ascii=True, sort_keys=True,
                                           separators=(",", ":")).encode("utf-8")).hexdigest()
        return LoopPlan(producer.call_id, producer.index, observation.index, first.call_id,
                        first.index, cwd, paths, template, predicted, digest)
    return None


def detect_runtime_loops(
    trajectory: Trajectory, *, cwd_by_call: Mapping[str, str],
) -> tuple[DetectedLoop, ...]:
    """匹配完整连续的消费调用；匹配结果不是未来 LLM 行为或执行安全证明。"""
    return _detect_runtime_loops(trajectory, cwd_by_call=cwd_by_call, check_dependencies=True)


def _detect_runtime_loops(
    trajectory: Trajectory, *, cwd_by_call: Mapping[str, str], check_dependencies: bool,
) -> tuple[DetectedLoop, ...]:
    """评估消融的内部入口；生产接口与重放验证始终检查依赖。"""
    calls = [e for e in trajectory.events if e.kind == "tool_call"]
    detected = []
    cursor = 0
    while cursor < len(calls):
        plan = _infer_loop_at(trajectory, calls[cursor].index, cwd_by_call=cwd_by_call,
                              check_dependencies=check_dependencies)
        if plan is None:
            cursor += 1
            continue
        window = calls[cursor:cursor + len(plan.paths)]
        valid = len(window) == len(plan.paths)
        for call, expected in zip(window, plan.predicted_argv, strict=False):
            context = cwd_by_call.get(call.call_id, "")
            body = _body(call, context)
            valid = valid and body is not None
            if body is not None:
                valid = valid and (*body[0], body[1]) == expected
                valid = valid and analyze_command(call.command, cwd=context).cwd == plan.cwd
        if valid:
            valid = not any(e.kind == "exit" or e.role in ("user", "system") for e in
                            trajectory.events[window[0].index + 1:window[-1].index])
        if valid:
            detected.append(DetectedLoop(plan, tuple(e.call_id for e in window),
                                         tuple(e.index for e in window)))
            cursor += len(window)
        else:
            cursor += 1
    return tuple(detected)
