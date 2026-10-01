"""只读解析 mini-swe-agent-1.1 轨迹，不执行其中的命令。"""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


class TrajectoryError(ValueError):
    """输入轨迹无法按支持的格式读取。"""


@dataclass(frozen=True)
class Event:
    """按原始消息顺序排列的事件，索引从零开始。"""

    index: int
    message_index: int
    kind: Literal["message", "tool_call", "tool_result", "exit"]
    role: str
    content: str | None = None
    tool_index: int | None = None
    call_id: str | None = None
    tool_name: str | None = None
    command: str | None = None
    returncode: int | None = None
    raw_output: str | None = None


@dataclass(frozen=True)
class Trajectory:
    """规范化轨迹及原文件身份；未返回调用不代表成功或失败。"""

    source: str
    source_sha256: str
    trajectory_format: str
    instance_id: str | None
    events: tuple[Event, ...]
    pending_call_ids: tuple[str, ...]


def _text(value: object, location: str, *, nonempty: bool = False) -> str:
    if not isinstance(value, str) or (nonempty and not value.strip()):
        raise TrajectoryError(f"{location} 必须是{'非空' if nonempty else ''}字符串")
    return value


def _object(value: object, location: str) -> dict:
    if not isinstance(value, dict):
        raise TrajectoryError(f"{location} 必须是对象")
    return value


def _normalize_response_messages(messages: list) -> list:
    """将固定的 Responses API 输出项规整为内部消息形状。"""
    normalized = []
    for index, value in enumerate(messages):
        if not isinstance(value, dict):
            raise TrajectoryError(f"messages[{index}] 必须是对象")
        if "role" in value:
            normalized.append(value)
            continue
        if value.get("type") == "function_call_output":
            normalized.append({"role": "tool", "tool_call_id": value.get("call_id"),
                               "content": value.get("output", ""),
                               "extra": value.get("extra", {})})
            continue
        output = value.get("output")
        if value.get("object") == "response" and isinstance(output, list):
            for item in output:
                if not isinstance(item, dict):
                    raise TrajectoryError(f"messages[{index}].output 项必须是对象")
                if item.get("type") == "function_call":
                    call_id = item.get("call_id")
                    if not isinstance(call_id, str) or not call_id.strip():
                        raise TrajectoryError(f"messages[{index}].function_call 缺少有效 call_id")
                    normalized.append({"role": "assistant", "content": "", "tool_calls": [{
                        "id": call_id,
                        "type": "function",
                        "function": {"name": item.get("name"),
                                     "arguments": item.get("arguments")},
                    }]})
                elif item.get("type") == "message":
                    texts = []
                    for content in item.get("content") or []:
                        if not isinstance(content, dict) or content.get("type") != "output_text":
                            raise TrajectoryError(f"messages[{index}].message 包含不支持的内容")
                        texts.append(_text(content.get("text"),
                                           f"messages[{index}].message.text"))
                    normalized.append({"role": "assistant", "content": "".join(texts),
                                      "tool_calls": []})
                elif item.get("type") != "reasoning":
                    raise TrajectoryError(f"messages[{index}].output 包含不支持的类型")
            continue
        raise TrajectoryError(f"messages[{index}] 包含不支持的角色")
    return normalized


def load_trajectory(path: str | Path) -> Trajectory:
    """读取 UTF-8 JSON 文件并校验调用关联，失败时抛出中文错误。"""
    source = Path(path).resolve()
    try:
        raw = source.read_bytes()
    except OSError as exc:
        raise TrajectoryError(f"无法读取轨迹文件：{source}") from exc
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TrajectoryError(f"轨迹不是有效的 UTF-8 JSON：{source}") from exc
    data = _object(data, "轨迹顶层")
    if data.get("trajectory_format") != "mini-swe-agent-1.1":
        raise TrajectoryError("不支持的 trajectory_format，仅支持 mini-swe-agent-1.1")
    messages = data.get("messages")
    if not isinstance(messages, list):
        raise TrajectoryError("messages 必须是数组")
    messages = _normalize_response_messages(messages)
    instance_id = data.get("instance_id")
    if instance_id is not None:
        _text(instance_id, "instance_id", nonempty=True)

    events: list[Event] = []
    calls: dict[str, str] = {}
    completed: set[str] = set()
    for mi, value in enumerate(messages):
        location = f"messages[{mi}]"
        message = _object(value, location)
        role = message.get("role")
        if role not in ("system", "user", "assistant", "tool", "exit"):
            raise TrajectoryError(f"{location} 包含不支持的角色")
        if "content" not in message:
            raise TrajectoryError(f"{location} 缺少 content")
        content = message["content"]
        if content is not None or role != "assistant":
            _text(content, f"{location}.content")
        if message.get("function_call") is not None:
            raise TrajectoryError(f"{location} 不支持旧式 function_call")
        tool_calls = message.get("tool_calls")
        if tool_calls is not None and not isinstance(tool_calls, list):
            raise TrajectoryError(f"{location}.tool_calls 必须是数组或 null")
        if tool_calls and role != "assistant":
            raise TrajectoryError(f"{location} 只有 assistant 可以发起工具调用")
        if role != "tool" and message.get("tool_call_id") is not None:
            raise TrajectoryError(f"{location} 只有 tool 可以引用 tool_call_id")

        if role == "tool":
            call_id = _text(message.get("tool_call_id"), f"{location}.tool_call_id")
            if call_id not in calls:
                raise TrajectoryError(f"{location} 引用了尚未出现的工具调用")
            if call_id in completed:
                raise TrajectoryError(f"{location} 重复返回同一工具调用的结果")
            extra = _object(message.get("extra", {}), f"{location}.extra")
            returncode = extra.get("returncode")
            if returncode is not None and type(returncode) is not int:
                raise TrajectoryError(f"{location}.extra.returncode 必须是整数或 null")
            raw_output = extra.get("raw_output")
            if raw_output is not None:
                _text(raw_output, f"{location}.extra.raw_output")
            events.append(Event(
                index=len(events), message_index=mi, kind="tool_result", role=role,
                content=content, call_id=call_id, tool_name=calls[call_id],
                returncode=returncode, raw_output=raw_output,
            ))
            completed.add(call_id)
            continue

        events.append(Event(
            index=len(events), message_index=mi,
            kind="exit" if role == "exit" else "message", role=role, content=content,
        ))
        for ti, value in enumerate(tool_calls or []):
            call_location = f"{location}.tool_calls[{ti}]"
            call = _object(value, call_location)
            call_id = _text(call.get("id"), f"{call_location}.id", nonempty=True)
            if call_id in calls:
                raise TrajectoryError(f"{call_location} 工具调用 ID 重复")
            if call.get("type") != "function":
                raise TrajectoryError(f"{call_location} 仅支持 function 调用")
            function = _object(call.get("function"), f"{call_location}.function")
            if function.get("name") != "bash":
                raise TrajectoryError(f"{call_location} 仅支持 bash 工具")
            arguments = _text(function.get("arguments"), f"{call_location}.arguments")
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError as exc:
                raise TrajectoryError(f"{call_location} 参数不是有效 JSON") from exc
            arguments = _object(arguments, f"{call_location}.arguments")
            if set(arguments) != {"command"}:
                raise TrajectoryError(f"{call_location} 参数必须且只能包含 command")
            command = _text(arguments["command"], f"{call_location}.command", nonempty=True)
            calls[call_id] = "bash"
            events.append(Event(
                index=len(events), message_index=mi, kind="tool_call", role=role,
                tool_index=ti, call_id=call_id, tool_name="bash", command=command,
            ))

    return Trajectory(
        source=str(source), source_sha256=hashlib.sha256(raw).hexdigest(),
        trajectory_format=data["trajectory_format"], instance_id=instance_id,
        events=tuple(events), pending_call_ids=tuple(cid for cid in calls if cid not in completed),
    )
