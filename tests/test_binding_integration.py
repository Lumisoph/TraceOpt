"""绑定 API 与轨迹加载器的完整衔接。"""

import json
from pathlib import Path

from traceopt import detect_runtime_loops, infer_loop_at, load_trajectory


def test_loaded_positive_trajectory_preserves_binding_provenance(binding_trace):
    trajectory, contexts, start = binding_trace()
    plan = infer_loop_at(trajectory, start, cwd_by_call=contexts)
    detected, = detect_runtime_loops(trajectory, cwd_by_call=contexts)
    assert detected.plan == plan
    observation = trajectory.events[plan.observation_event_index]
    assert observation.raw_output.split("\0")[:-1] == ["src/a", "src/b"]
    assert trajectory.events[plan.producer_event_index].call_id == observation.call_id


def test_real_source_is_not_assumed_to_contain_a_supported_loop():
    root = Path(__file__).resolve().parents[1]
    source = json.loads((root / "tests/fixtures/provenance.json").read_text(encoding="utf-8"))
    trajectory = load_trajectory(root / source["source"])
    assert trajectory.source_sha256 == source["sha256"]
    contexts = {e.call_id: "/testbed" for e in trajectory.events if e.kind == "tool_call"}
    assert detect_runtime_loops(trajectory, cwd_by_call=contexts) == ()
