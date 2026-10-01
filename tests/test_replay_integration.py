"""实际工具输出 → 加载 → 绑定 → 改写重放的受控执行证据。"""

import subprocess

from traceopt import detect_runtime_loops, discover_toolchain, replay_cat_loop


def test_live_tool_capture_and_replay(tmp_path, binding_trace):
    root = tmp_path / "live-repository"
    (root / "src").mkdir(parents=True)
    (root / "src/a").write_bytes(b"first\n")
    (root / "src/b").write_bytes(b"second\n")
    tools = discover_toolchain()
    producer = subprocess.run([tools.find, "src", "-type", "f", "-print0"], cwd=root,
                              capture_output=True, check=True)
    paths = producer.stdout.decode("utf-8").split("\0")[:-1]
    outputs = [subprocess.run([tools.cat, "--", path], cwd=root, capture_output=True,
                              check=True).stdout.decode("utf-8") for path in paths]
    trajectory, contexts, _ = binding_trace(output=producer.stdout.decode("utf-8"),
                                            commands=[f"cat {p}" for p in paths],
                                            consumer_outputs=outputs)
    loop, = detect_runtime_loops(trajectory, cwd_by_call=contexts)
    report = replay_cat_loop(trajectory, loop, repository=root, virtual_root="/repo",
                             cwd_by_call=contexts, tools=tools)
    assert report.successful
    assert report.original == report.optimized
