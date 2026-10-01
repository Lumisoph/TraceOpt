"""最小 IR 的输入边界与关联不变量。"""

import hashlib
import json
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from traceopt import TrajectoryError, load_trajectory


def call(cid="a", command="pwd"):
    return {"id": cid, "type": "function", "function": {
        "name": "bash", "arguments": json.dumps({"command": command}),
    }}


def assistant(*calls):
    return {"role": "assistant", "content": None, "tool_calls": list(calls)}


def result(cid="a", **extra):
    return {"role": "tool", "content": "原始观察", "tool_call_id": cid, "extra": extra}


def write(tmp_path, messages, **fields):
    p = tmp_path / "轨迹.json"
    p.write_text(json.dumps({"trajectory_format": "mini-swe-agent-1.1",
                            "messages": messages, **fields}), encoding="utf-8")
    return p


def test_empty_and_immutable(tmp_path):
    trajectory = load_trajectory(write(tmp_path, []))
    assert trajectory.events == trajectory.pending_call_ids == ()
    assert trajectory.instance_id is None
    with pytest.raises(FrozenInstanceError):
        trajectory.source = "改写"


def test_multiple_calls_out_of_order_results_and_pending(tmp_path):
    p = write(tmp_path, [assistant(call("a"), call("b"), call("c")),
                         result("b", returncode=1, raw_output="失败"), result("a"),
                         {"role": "exit", "content": "终止"}])
    t = load_trajectory(p)
    assert [e.kind for e in t.events] == ["message", "tool_call", "tool_call", "tool_call",
                                         "tool_result", "tool_result", "exit"]
    assert [e.index for e in t.events] == list(range(7))
    assert [e.message_index for e in t.events] == [0, 0, 0, 0, 1, 2, 3]
    assert [e.tool_index for e in t.events[1:4]] == [0, 1, 2]
    assert t.events[4].call_id == "b"
    assert t.events[4].returncode == 1
    assert t.events[4].raw_output == "失败"
    assert t.events[5].returncode is None
    assert t.pending_call_ids == ("c",)
    with pytest.raises(FrozenInstanceError):
        t.events[0].content = "改写"


def test_no_execution_no_input_mutation_and_no_inferred_returncode(tmp_path):
    marker = tmp_path / "不应产生.txt"
    command = f'echo 不应执行 > "{marker}"'
    observation = result()
    observation["content"] = "<returncode>0</returncode>"
    p = write(tmp_path, [assistant(call(command=command)), observation])
    before = p.read_bytes()
    t = load_trajectory(p)
    assert p.read_bytes() == before
    assert not marker.exists()
    assert t.source_sha256 == hashlib.sha256(before).hexdigest()
    assert t.source == str(p.resolve())
    assert t.events[1].command == command
    assert t.events[2].returncode is None


@pytest.mark.parametrize("messages", [
    [result()],
    [assistant(call(), call())],
    [assistant(call()), result(), result()],
    [result(), assistant(call())],
    [{"role": "unknown", "content": ""}],
    [{"role": "user", "content": "", "tool_calls": [call()]}],
    [{"role": "user"}],
    [{"role": "user", "content": None}],
    [{"role": "assistant", "content": "", "tool_calls": {}}],
    [{"role": "assistant", "content": "", "function_call": {"name": "bash"}}],
    [assistant(call()), result(returncode=True)],
    [assistant(call()), result(raw_output=123)],
    [None],
])
def test_reject_malformed_messages(tmp_path, messages):
    with pytest.raises(TrajectoryError, match="[\u4e00-\u9fff]"):
        load_trajectory(write(tmp_path, messages))


@pytest.mark.parametrize("arguments", ["{", "[]", '{}', '{"command":1}',
                                         '{"command":""}', '{"command":"pwd","cwd":"/"}'])
def test_reject_invalid_arguments(tmp_path, arguments):
    item = call()
    item["function"]["arguments"] = arguments
    with pytest.raises(TrajectoryError):
        load_trajectory(write(tmp_path, [assistant(item)]))


def test_reject_unknown_tool(tmp_path):
    item = call()
    item["function"]["name"] = "python"
    with pytest.raises(TrajectoryError, match="仅支持 bash"):
        load_trajectory(write(tmp_path, [assistant(item)]))


@pytest.mark.parametrize("raw", [b"{", b"\xff", b"[]", b"{}",
                                  b'{"trajectory_format":"other","messages":[]}',
                                  b'{"trajectory_format":"mini-swe-agent-1.1","messages":{}}'])
def test_reject_invalid_document(tmp_path, raw):
    p = tmp_path / "bad.json"
    p.write_bytes(raw)
    with pytest.raises(TrajectoryError, match="[\u4e00-\u9fff]"):
        load_trajectory(p)


def test_missing_file(tmp_path):
    with pytest.raises(TrajectoryError, match="无法读取"):
        load_trajectory(tmp_path / "missing.json")


def test_responses_output_rejects_unknown_item(tmp_path):
    document = {"trajectory_format": "mini-swe-agent-1.1", "messages": [
        {"object": "response", "output": [{"type": "computer_call"}]},
    ]}
    with pytest.raises(TrajectoryError, match="不支持的类型"):
        load_trajectory(write(tmp_path, document["messages"]))


def test_responses_function_call_bad_arguments_is_rejected(tmp_path):
    document = {"trajectory_format": "mini-swe-agent-1.1", "messages": [
        {"object": "response", "output": [{"type": "function_call", "call_id": "c",
                                               "name": "bash", "arguments": "{}"}]},
    ]}
    with pytest.raises(TrajectoryError, match="command"):
        load_trajectory(write(tmp_path, document["messages"]))


def test_synthetic_fixture():
    t = load_trajectory(Path(__file__).parent / "fixtures" / "trajectory.json")
    assert [e.command for e in t.events if e.kind == "tool_call"] == ["pwd", "ls"]
    assert t.pending_call_ids == ("call-2",)
