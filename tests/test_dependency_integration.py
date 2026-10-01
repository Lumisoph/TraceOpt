"""轨迹到依赖的映射及上下文约束。"""

import json
from pathlib import Path

import pytest

from traceopt import analyze_trajectory, load_trajectory


def test_missing_context_is_unknown_and_unknown_ids_rejected():
    t = load_trajectory(Path(__file__).parent / "fixtures/trajectory.json")
    analysis = analyze_trajectory(t, cwd_by_call={})
    assert analysis.call_ids == ("call-1", "call-2")
    assert analysis.event_indices == (3, 4)
    assert all(e.unknown for e in analysis.effects)
    assert [e.kind for e in analysis.edges] == ["BARRIER"]
    with pytest.raises(ValueError, match="不存在"):
        analyze_trajectory(t, cwd_by_call={"typo": "/repo"})


def test_real_trajectory_has_traceable_nodes_and_barriers():
    root = Path(__file__).resolve().parents[1]
    source = json.loads((root / "tests/fixtures/provenance.json").read_text(encoding="utf-8"))
    trajectory = load_trajectory(root / source["source"])
    assert trajectory.source_sha256 == source["sha256"]
    calls = [e for e in trajectory.events if e.kind == "tool_call"]
    analysis = analyze_trajectory(trajectory, cwd_by_call={e.call_id: "/testbed" for e in calls})
    assert analysis.source_sha256 == trajectory.source_sha256
    assert analysis.call_ids == tuple(e.call_id for e in calls)
    assert analysis.event_indices == tuple(e.index for e in calls)
    assert tuple(e.command for e in analysis.effects) == tuple(e.command for e in calls)
    assert set(trajectory.pending_call_ids).issubset(analysis.call_ids)
    assert all(e.source < e.target for e in analysis.edges)
    edge_keys = {(e.source, e.target, e.kind) for e in analysis.edges}
    for i, effect in enumerate(analysis.effects):
        if effect.unknown:
            for j in range(len(calls)):
                if i != j:
                    assert (min(i, j), max(i, j), "BARRIER") in edge_keys
