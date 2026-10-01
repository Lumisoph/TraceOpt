"""QA 检查文件别名与非默认终端编码。"""

import json
import os
import subprocess
import sys
from pathlib import Path


def test_output_hardlink_cannot_overwrite_source(tmp_path):
    source = tmp_path / "source.json"
    source.write_bytes((Path(__file__).parent / "fixtures/trajectory.json").read_bytes())
    alias = tmp_path / "alias.json"
    os.link(source, alias)
    before = source.read_bytes()
    result = subprocess.run(
        [sys.executable, "-m", "traceopt", "export", str(source), "--output", str(alias)],
        capture_output=True, encoding="utf-8")
    assert result.returncode == 2
    assert "不能覆盖" in result.stderr
    assert source.read_bytes() == alias.read_bytes() == before


def test_utf8_even_with_ascii_environment():
    source = Path(__file__).parent / "fixtures/trajectory.json"
    env = {**os.environ, "PYTHONIOENCODING": "ascii"}
    result = subprocess.run(
        [sys.executable, "-m", "traceopt", "export", str(source)],
        env=env, capture_output=True)
    assert result.returncode == 0
    assert json.loads(result.stdout.decode("utf-8"))["events"][0]["content"] == "人工测试样本"
