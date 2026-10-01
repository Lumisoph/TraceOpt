"""捕获真实工具输出，再保存受控 cat 循环的可复现重放证据。"""

import json
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

from traceopt import detect_runtime_loops, discover_toolchain, load_trajectory, replay_cat_loop


def main() -> None:
    if len(sys.argv) != 2:
        raise ValueError("用法：python examples/replay_demo.py 新建输出目录")
    output = Path(sys.argv[1]).absolute()
    output.mkdir(parents=True, exist_ok=False)
    repository = output / "initial_repo"
    (repository / "src").mkdir(parents=True)
    (repository / "src/a").write_bytes(b"alpha\n")
    (repository / "src/b").write_bytes(b"beta\n")
    tools = discover_toolchain()
    messages = []

    def capture(cid, command, argv):
        result = subprocess.run(argv, cwd=repository, capture_output=True, check=True)
        raw = result.stdout.decode("utf-8")
        messages.extend([
            {"role": "assistant", "content": "受控工具执行", "tool_calls": [
                {"id": cid, "type": "function", "function": {
                    "name": "bash", "arguments": json.dumps({"command": command})}}]},
            {"role": "tool", "tool_call_id": cid, "content": raw,
             "extra": {"returncode": result.returncode, "raw_output": raw}},
        ])
        return raw

    paths = capture("producer", "find src -type f -print0",
                    [tools.find, "src", "-type", "f", "-print0"]).split("\0")[:-1]
    for i, path in enumerate(paths):
        capture(f"consumer-{i}", f"cat {path}", [tools.cat, "--", path])
    source = output / "capture.traj.json"
    source.write_text(json.dumps({"trajectory_format": "mini-swe-agent-1.1", "messages": messages},
                                 ensure_ascii=False, indent=2), encoding="utf-8")
    trajectory = load_trajectory(source)
    contexts = {e.call_id: "/repo" for e in trajectory.events if e.kind == "tool_call"}
    loop, = detect_runtime_loops(trajectory, cwd_by_call=contexts)
    report = replay_cat_loop(trajectory, loop, repository=repository, virtual_root="/repo",
                             cwd_by_call=contexts, tools=tools)
    (output / "report.json").write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2),
                                         encoding="utf-8")
    (output / "rewrite.sh").write_text(report.script, encoding="utf-8", newline="\n")
    print(json.dumps({"successful": report.successful, "report": str(output / "report.json")},
                     ensure_ascii=True))
    if not report.successful:
        raise ValueError("重放结果未通过验证")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(f"演示失败：{exc}", file=sys.stderr)
        raise SystemExit(2) from None
