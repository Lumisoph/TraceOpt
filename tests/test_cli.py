"""通过真实子进程验证命令行契约。"""

import json
import shutil
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

import pytest

from traceopt import analyze_trajectory, load_trajectory

FIXTURE = Path(__file__).parent / "fixtures" / "trajectory.json"


def run_cli(*args, console=False):
    if console:
        executable = shutil.which("traceopt")
        if executable is None:
            pytest.skip("??????? traceopt ?????")
        command = [executable]
    else:
        command = [sys.executable, "-m", "traceopt"]
    return subprocess.run([*command, *map(str, args)], capture_output=True, encoding="utf-8")


@pytest.mark.parametrize("console", [False, True])
def test_inspect(console):
    result = run_cli("inspect", FIXTURE, console=console)
    assert result.returncode == 0
    assert result.stderr == ""
    data = json.loads(result.stdout)
    assert data["schema_version"] == 1
    assert data["message_count"] == 5
    assert data["event_count"] == 7
    assert data["tool_call_count"] == 2
    assert data["tool_result_count"] == 1
    assert data["pending_call_ids"] == ["call-2"]
    assert data["source_sha256"] == load_trajectory(FIXTURE).source_sha256


def test_export_matches_api():
    result = run_cli("export", FIXTURE)
    assert result.returncode == 0
    expected = json.loads(json.dumps({"schema_version": 1, **asdict(load_trajectory(FIXTURE))}))
    assert json.loads(result.stdout) == expected
    assert "人工测试样本" in result.stdout


@pytest.mark.parametrize("action", ["inspect", "export"])
def test_file_output(tmp_path, action):
    target = tmp_path / "中文.json"
    result = run_cli(action, FIXTURE, "--output", target)
    assert result.returncode == 0
    assert result.stdout == result.stderr == ""
    assert json.loads(target.read_text(encoding="utf-8")) == json.loads(
        run_cli(action, FIXTURE).stdout)


def test_never_overwrite_input_or_existing_file(tmp_path):
    target = tmp_path / "已有文件.json"
    target.write_bytes(b"important")
    for path in [FIXTURE, target]:
        before = path.read_bytes()
        result = run_cli("export", FIXTURE, "--output", path)
        assert result.returncode == 2
        assert "不能覆盖" in result.stderr
        assert result.stdout == ""
        assert path.read_bytes() == before


def test_missing_output_directory(tmp_path):
    result = run_cli("export", FIXTURE, "--output", tmp_path / "missing" / "out.json")
    assert result.returncode == 2
    assert "无法写入" in result.stderr


@pytest.mark.parametrize("args", [[], ["unknown"], ["inspect"], ["inspect", "--unknown"]])
def test_bad_arguments(args):
    result = run_cli(*args)
    assert result.returncode == 2
    assert "参数无效" in result.stderr
    assert "Traceback" not in result.stderr
    assert result.stdout == ""


def test_bad_input_does_not_create_output(tmp_path):
    source = tmp_path / "bad.json"
    source.write_text("{", encoding="utf-8")
    output = tmp_path / "out.json"
    result = run_cli("export", source, "--output", output)
    assert result.returncode == 2
    assert "有效的 UTF-8 JSON" in result.stderr
    assert not output.exists()
    result = run_cli("inspect", tmp_path / "missing.json")
    assert result.returncode == 2
    assert "无法读取" in result.stderr


def test_help():
    result = run_cli("--help")
    assert result.returncode == 0
    assert "子命令" in result.stdout
    assert "用法：" in result.stdout
    assert result.stderr == ""


def test_analyze_matches_explicit_context_api():
    result = run_cli("analyze", FIXTURE, "--cwd", "/repo")
    assert result.returncode == 0
    trajectory = load_trajectory(FIXTURE)
    analysis = analyze_trajectory(trajectory, cwd_by_call={"call-1": "/repo", "call-2": "/repo"})
    expected = json.loads(json.dumps({"schema_version": 1, "cwd_policy": "explicit_fixed",
                                     **asdict(analysis)}))
    assert json.loads(result.stdout) == expected


@pytest.mark.parametrize("args", [[], ["--cwd", "relative"], ["--cwd", "C:/repo"]])
def test_analyze_requires_valid_context(args):
    result = run_cli("analyze", FIXTURE, *args)
    assert result.returncode == 2
    assert result.stdout == ""
    assert "错误" in result.stderr


def test_analyze_output_does_not_overwrite(tmp_path):
    target = tmp_path / "analysis.json"
    result = run_cli("analyze", FIXTURE, "--cwd", "/repo", "--output", target)
    assert result.returncode == 0
    before = target.read_bytes()
    result = run_cli("analyze", FIXTURE, "--cwd", "/repo", "--output", target)
    assert result.returncode == 2
    assert target.read_bytes() == before


def test_analyze_reports_known_raw_dependency(tmp_path):
    source = tmp_path / "known.json"
    calls = [{"id": str(i), "type": "function", "function": {
        "name": "bash", "arguments": json.dumps({"command": command})}}
        for i, command in enumerate(["cp source.txt target.txt", "cat target.txt"])]
    source.write_text(json.dumps({"trajectory_format": "mini-swe-agent-1.1", "messages": [
        {"role": "assistant", "content": "", "tool_calls": calls}]}), encoding="utf-8")
    result = run_cli("analyze", source, "--cwd", "/repo")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["edges"] == [{"source": 0, "target": 1, "kind": "RAW",
                              "left_resource": "/repo/target.txt",
                              "right_resource": "/repo/target.txt"}]
