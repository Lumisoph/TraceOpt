"""按真实轨迹结构构造最小绑定测试输入。"""

import json

import pytest

from traceopt import load_trajectory


@pytest.fixture
def binding_trace(tmp_path):
    def make(*, output="src/a\0src/b\0", commands=None, returncode=0,
             producer="find src -type f -print0", between=(), consumer_outputs=None):
        messages = []

        def add(cid, command, raw, code):
            messages.append({"role": "assistant", "content": "调用", "tool_calls": [
                {"id": cid, "type": "function", "function": {
                    "name": "bash", "arguments": json.dumps({"command": command})}}]})
            messages.append({"role": "tool", "content": "观察", "tool_call_id": cid,
                             "extra": {"returncode": code, "raw_output": raw}})

        add("producer", producer, output, returncode)
        for i, command in enumerate(between):
            add(f"between-{i}", command, "", 0)
        body_commands = commands if commands is not None else ["cat src/a", "cat src/b"]
        for i, command in enumerate(body_commands):
            raw = consumer_outputs[i] if consumer_outputs else "内容"
            add(f"consumer-{i}", command, raw, 0)
        document = {"trajectory_format": "mini-swe-agent-1.1", "messages": messages}
        path = tmp_path / "binding.traj.json"
        path.write_text(json.dumps(document), encoding="utf-8")
        trajectory = load_trajectory(path)
        contexts = {e.call_id: "/repo" for e in trajectory.events if e.kind == "tool_call"}
        start = next((e.index for e in trajectory.events if e.call_id == "consumer-0"
                      and e.kind == "tool_call"), None)
        return trajectory, contexts, start

    return make
