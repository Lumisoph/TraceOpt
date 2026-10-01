"""QA：Responses 适配的关联、内容拒绝和事件顺序。"""

import json

import pytest

from traceopt import TrajectoryError, load_trajectory


def load(tmp_path, items):
    path = tmp_path / "response.json"
    path.write_text(json.dumps({
        "trajectory_format": "mini-swe-agent-1.1",
        "messages": [{"object": "response", "output": items}],
    }), encoding="utf-8")
    return load_trajectory(path)


def test_item_id_cannot_substitute_missing_call_id(tmp_path):
    with pytest.raises(TrajectoryError):
        load(tmp_path, [{"type": "function_call", "id": "fc-object-id", "name": "bash",
                         "arguments": '{"command":"cat a"}'}])


def test_unknown_message_content_cannot_be_silently_dropped(tmp_path):
    with pytest.raises(TrajectoryError):
        load(tmp_path, [{"type": "message", "role": "assistant",
                         "content": [{"type": "unknown_content", "data": "不可丢弃"}]}])


def test_later_text_is_not_moved_before_earlier_call(tmp_path):
    trace = load(tmp_path, [
        {"type": "function_call", "call_id": "a", "name": "bash",
         "arguments": '{"command":"cat a"}'},
        {"type": "message", "role": "assistant",
         "content": [{"type": "output_text", "text": "调用之后的文本"}]},
    ])
    call = next(e for e in trace.events if e.kind == "tool_call")
    text = next(e for e in trace.events if e.content == "调用之后的文本")
    assert call.index < text.index
