"""QA：真实目录别名和 Bash 启动注入边界。"""

import os
import shlex
import subprocess

import pytest

from traceopt import ReplayError, detect_runtime_loops, replay_cat_loop, snapshot_repository


def test_directory_alias_is_rejected(tmp_path):
    root = tmp_path / "repository"
    target = root / "real"
    target.mkdir(parents=True)
    (target / "file").write_bytes(b"safe")
    alias = root / "alias"
    if os.name == "nt":
        subprocess.run(["cmd", "/c", "mklink", "/J", str(alias), str(target)],
                       capture_output=True, check=True)
    else:
        alias.symlink_to(target, target_is_directory=True)
    try:
        with pytest.raises(ReplayError, match="链接或重解析点"):
            snapshot_repository(root)
        assert (target / "file").read_bytes() == b"safe"
    finally:
        if os.name == "nt":
            alias.rmdir()
        else:
            alias.unlink()


def test_bash_env_injection_does_not_run(tmp_path, binding_trace, monkeypatch):
    root = tmp_path / "repository"
    (root / "src").mkdir(parents=True)
    (root / "src/a").write_bytes(b"a")
    (root / "src/b").write_bytes(b"b")
    marker = tmp_path / "injected"
    startup = tmp_path / "startup.sh"
    startup.write_text(f"printf bad > {shlex.quote(marker.as_posix())}\n", encoding="utf-8")
    monkeypatch.setenv("BASH_ENV", str(startup))
    trajectory, contexts, _ = binding_trace(consumer_outputs=["a", "b"])
    loop, = detect_runtime_loops(trajectory, cwd_by_call=contexts)
    report = replay_cat_loop(trajectory, loop, repository=root, virtual_root="/repo",
                             cwd_by_call=contexts)
    assert report.successful
    assert not marker.exists()
