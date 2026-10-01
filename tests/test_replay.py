"""受限重放、输入保护和错误边界。"""

import base64
import os
import stat
from dataclasses import replace

import pytest

from traceopt import (
    ReplayError,
    detect_runtime_loops,
    discover_toolchain,
    replay_cat_loop,
    snapshot_repository,
)
from traceopt.replay import _environment, _run


@pytest.fixture
def replay_case(tmp_path, binding_trace):
    root = tmp_path / "repository"
    (root / "src").mkdir(parents=True)
    (root / "src/a").write_bytes(b"alpha\n")
    (root / "src/b").write_bytes(b"beta\n")
    trajectory, contexts, _ = binding_trace(consumer_outputs=["alpha\n", "beta\n"])
    loop, = detect_runtime_loops(trajectory, cwd_by_call=contexts)
    return root, trajectory, contexts, loop


def replay(case, **kwargs):
    root, trajectory, contexts, loop = case
    return replay_cat_loop(trajectory, loop, repository=root, virtual_root="/repo",
                           cwd_by_call=contexts, **kwargs)


def test_actual_batch_equivalence_and_source_unchanged(replay_case):
    before = snapshot_repository(replay_case[0])
    report = replay(replay_case)
    assert report.successful and report.equivalent and report.matches_recording
    assert report.state_unchanged
    assert report.original == report.optimized
    assert [base64.b64decode(r.stdout_b64) for r in report.original] == [b"alpha\n", b"beta\n"]
    assert report.initial_state == report.original_state == report.optimized_state == before
    assert snapshot_repository(replay_case[0]) == before
    assert (report.original_tool_boundaries, report.optimized_tool_boundaries) == (2, 1)
    assert "for relative in" in report.script
    assert len(report.tool_hashes) == 3


def test_history_mismatch_is_not_successful(replay_case):
    root, trajectory, contexts, loop = replay_case
    events = tuple(replace(e, raw_output="不同的历史输出") if e.call_id == "consumer-1"
                   and e.kind == "tool_result" else e for e in trajectory.events)
    changed = replace(trajectory, events=events)
    report = replay_cat_loop(changed, loop, repository=root, virtual_root="/repo",
                             cwd_by_call=contexts)
    assert report.equivalent
    assert not report.matches_recording
    assert not report.successful


def test_changed_enumeration_is_rejected(replay_case):
    (replay_case[0] / "src/c").write_text("new", encoding="utf-8")
    with pytest.raises(ReplayError, match="枚举结果"):
        replay(replay_case)


def test_hardlinks_rejected_before_execution(replay_case, monkeypatch):
    root = replay_case[0]
    os.link(root / "src/a", root / "alias")
    monkeypatch.setattr("traceopt.replay._run", lambda *a, **k: pytest.fail("不应执行"))
    with pytest.raises(ReplayError, match="硬链接"):
        replay(replay_case)


def test_tampered_plan_and_escape_rejected(replay_case, monkeypatch):
    root, trajectory, contexts, loop = replay_case
    monkeypatch.setattr("traceopt.replay._run", lambda *a, **k: pytest.fail("不应执行"))
    forged = replace(loop, plan=replace(loop.plan, paths=("/outside",)))
    with pytest.raises(ReplayError, match="不一致"):
        replay_cat_loop(trajectory, forged, repository=root, virtual_root="/repo",
                         cwd_by_call=contexts)
    with pytest.raises(ReplayError, match="超出"):
        replay_cat_loop(trajectory, loop, repository=root, virtual_root="/repo/src/a",
                         cwd_by_call=contexts)


def test_missing_history_is_rejected(replay_case):
    root, trajectory, contexts, loop = replay_case
    events = tuple(replace(e, raw_output=None) if e.call_id == "consumer-1"
                   and e.kind == "tool_result" else e for e in trajectory.events)
    with pytest.raises(ReplayError, match="完整成功"):
        replay_cat_loop(replace(trajectory, events=events), loop, repository=root,
                         virtual_root="/repo", cwd_by_call=contexts)


@pytest.mark.parametrize("timeout", [0, -1, float("nan"), float("inf"), "5", True])
def test_invalid_timeout(replay_case, timeout):
    with pytest.raises(ReplayError, match="超时"):
        replay(replay_case, timeout=timeout)


def test_actual_timeout_is_not_a_pass(tmp_path):
    tools = discover_toolchain()
    with pytest.raises(ReplayError, match="超时"):
        _run([tools.bash, "--noprofile", "--norc", "-c", "while :; do :; done"],
             tmp_path, _environment(tools), 0.1)


def test_missing_tools_is_an_error(monkeypatch):
    monkeypatch.setattr("traceopt.replay.shutil.which", lambda name: None)
    with pytest.raises(ReplayError, match="工具缺失|需要已安装"):
        discover_toolchain()


def test_snapshot_detects_changes(tmp_path):
    (tmp_path / "file").write_bytes(b"old")
    before = snapshot_repository(tmp_path)
    (tmp_path / "file").write_bytes(b"new")
    (tmp_path / "empty").mkdir()
    after = snapshot_repository(tmp_path)
    assert before != after
    assert any(e.path == "empty" and e.kind == "directory" for e in after)


def test_readonly_files_are_preserved(replay_case):
    path = replay_case[0] / "src/a"
    path.chmod(stat.S_IREAD)
    try:
        before = snapshot_repository(replay_case[0])
        assert replay(replay_case).successful
        assert snapshot_repository(replay_case[0]) == before
    finally:
        path.chmod(stat.S_IREAD | stat.S_IWRITE)


def test_other_templates_are_not_executable(replay_case, binding_trace):
    trajectory, contexts, _ = binding_trace(commands=["head src/a", "head src/b"])
    loop, = detect_runtime_loops(trajectory, cwd_by_call=contexts)
    with pytest.raises(ReplayError, match="只支持单文件 cat"):
        replay_cat_loop(trajectory, loop, repository=replay_case[0], virtual_root="/repo",
                         cwd_by_call=contexts)


def test_parent_operand_is_not_normalized_away(replay_case, binding_trace):
    trajectory, contexts, _ = binding_trace(commands=["cat src/missing/../a", "cat src/b"])
    loop, = detect_runtime_loops(trajectory, cwd_by_call=contexts)
    with pytest.raises(ReplayError, match="父目录跳转"):
        replay_cat_loop(trajectory, loop, repository=replay_case[0], virtual_root="/repo",
                         cwd_by_call=contexts)
