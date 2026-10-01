"""使用本地真实轨迹逐项核对，缺少样本时明确失败。"""

import hashlib
import json
from pathlib import Path

import pytest

from traceopt import TrajectoryError, load_trajectory


def _assert_real_mapping(provenance):
    root = Path(__file__).resolve().parents[1]
    path = root / provenance["source"]
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == provenance["sha256"]
    original = json.loads(raw)
    trajectory = load_trajectory(path)
    assert trajectory.source_sha256 == provenance["sha256"]
    assert trajectory.instance_id == original["instance_id"]
    cursor = 0
    calls = []
    returned = set()
    for mi, message in enumerate(original["messages"]):
        event = trajectory.events[cursor]
        assert event.message_index == mi
        assert event.role == message["role"]
        assert event.content == message["content"]
        expected_kind = {"tool": "tool_result", "exit": "exit"}.get(message["role"], "message")
        assert event.kind == expected_kind
        if message["role"] == "tool":
            assert event.call_id == message["tool_call_id"]
            assert event.returncode == message["extra"]["returncode"]
            assert event.raw_output == message["extra"]["raw_output"]
            returned.add(event.call_id)
        cursor += 1
        for ti, call in enumerate(message.get("tool_calls") or []):
            event = trajectory.events[cursor]
            assert event.kind == "tool_call"
            assert (event.message_index, event.tool_index) == (mi, ti)
            assert event.call_id == call["id"]
            assert event.tool_name == call["function"]["name"]
            assert event.command == json.loads(call["function"]["arguments"])["command"]
            calls.append(event.call_id)
            cursor += 1
    assert cursor == len(trajectory.events)
    assert [e.index for e in trajectory.events] == list(range(cursor))
    assert trajectory.pending_call_ids == tuple(cid for cid in calls if cid not in returned)
    assert path.read_bytes() == raw


def test_real_trajectory_mapping():
    provenance = json.loads((Path(__file__).parent / "fixtures/provenance.json").read_text(
        encoding="utf-8"))
    _assert_real_mapping(provenance)


@pytest.mark.parametrize("source", json.loads(
    (Path(__file__).parent / "fixtures/cli_sources.json").read_text(encoding="utf-8")),
    ids=lambda source: source["name"])
def test_additional_real_sources(source):
    if source["supported"]:
        if source["name"] == "gpt-5.2-responses-api":
            path = Path(__file__).resolve().parents[1] / source["source"]
            trajectory = load_trajectory(path)
            original = json.loads(path.read_text(encoding="utf-8"))
            expected_calls = sum(
                item.get("type") == "function_call"
                for message in original["messages"]
                for item in (message.get("output") or [])
                if isinstance(item, dict)
            )
            assert sum(event.kind == "tool_call" for event in trajectory.events) == expected_calls
            assert all(event.tool_name == "bash" for event in trajectory.events
                       if event.kind == "tool_call")
            assert trajectory.pending_call_ids == ("call_Fkorj7VHSmEzH5FYRmGr7niA",)
        else:
            _assert_real_mapping(source)
    else:
        path = Path(__file__).resolve().parents[1] / source["source"]
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == source["sha256"]
        with pytest.raises(TrajectoryError, match="不支持的角色"):
            load_trajectory(path)
        assert path.read_bytes() == raw
