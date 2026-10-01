"""TraceOpt：工具调用轨迹分析。"""

from .binding import DetectedLoop, LoopPlan, detect_runtime_loops, infer_loop_at
from .dependency import Dependency, TrajectoryAnalysis, analyze_trajectory, build_dependencies
from .replay import (
           ReplayError,
           ReplayReport,
           discover_toolchain,
           replay_cat_loop,
           snapshot_repository,
)
from .semantics import CommandEffect, analyze_command
from .trajectory import Event, Trajectory, TrajectoryError, load_trajectory

__all__ = ["CommandEffect", "analyze_command", "Event", "Trajectory", "TrajectoryError",
           "load_trajectory", "Dependency", "TrajectoryAnalysis", "analyze_trajectory",
           "build_dependencies", "LoopPlan", "DetectedLoop", "infer_loop_at",
           "detect_runtime_loops", "ReplayError", "ReplayReport", "discover_toolchain",
           "replay_cat_loop", "snapshot_repository"]
