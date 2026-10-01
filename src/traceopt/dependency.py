"""有序 Effect 的保守依赖分析，不推断执行安全性。"""

import posixpath
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal

from .semantics import CommandEffect, analyze_command
from .trajectory import Trajectory


@dataclass(frozen=True)
class Dependency:
    """序号指向输入 Effect；资源对是直接冲突的证据。"""

    source: int
    target: int
    kind: Literal["RAW", "WAR", "WAW", "BARRIER"]
    left_resource: str | None = None
    right_resource: str | None = None


@dataclass(frozen=True)
class TrajectoryAnalysis:
    source_sha256: str
    call_ids: tuple[str, ...]
    event_indices: tuple[int, ...]
    effects: tuple[CommandEffect, ...]
    edges: tuple[Dependency, ...]


def _validate_resource(path: str) -> None:
    if (not isinstance(path, str) or not path.startswith("/") or path.startswith("//")
            or "\\" in path or "\x00" in path or posixpath.normpath(path) != path):
        raise ValueError("Effect 资源必须是规范 POSIX 绝对路径")


def _overlaps(left: str, right: str) -> bool:
    return (left == right or left == "/" or right == "/"
            or left.startswith(right + "/") or right.startswith(left + "/"))


def build_dependencies(effects: Sequence[CommandEffect]) -> tuple[Dependency, ...]:
    """按原顺序比较所有调用对，保留直接冲突，未知端点形成屏障。"""
    effects = tuple(effects)
    for effect in effects:
        if not isinstance(effect, CommandEffect):
            raise ValueError("输入必须是 CommandEffect 序列")
        if not effect.unknown:
            for resource in (*effect.reads, *effect.writes):
                _validate_resource(resource)
    edges = []
    for i, before in enumerate(effects):
        for j in range(i + 1, len(effects)):
            after = effects[j]
            if before.unknown or after.unknown:
                edges.append(Dependency(i, j, "BARRIER"))
                continue
            for kind, lefts, rights in [
                ("RAW", before.writes, after.reads),
                ("WAR", before.reads, after.writes),
                ("WAW", before.writes, after.writes),
            ]:
                for left in sorted(set(lefts)):
                    for right in sorted(set(rights)):
                        if _overlaps(left, right):
                            edges.append(Dependency(i, j, kind, left, right))
    return tuple(edges)


def analyze_trajectory(
    trajectory: Trajectory, *, cwd_by_call: Mapping[str, str],
) -> TrajectoryAnalysis:
    """只使用显式逐调用 cwd，缺失上下文保守标记为未知。"""
    calls = tuple(event for event in trajectory.events if event.kind == "tool_call")
    call_ids = tuple(event.call_id for event in calls)
    if set(cwd_by_call) - set(call_ids):
        raise ValueError("工作目录映射包含轨迹中不存在的调用 ID")
    effects = tuple(analyze_command(event.command, cwd=cwd_by_call.get(event.call_id, ""))
                    for event in calls)
    return TrajectoryAnalysis(
        trajectory.source_sha256, call_ids, tuple(event.index for event in calls),
        effects, build_dependencies(effects),
    )
