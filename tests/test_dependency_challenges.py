"""完整检查人工标注的依赖挑战集，不从实现生成真值。"""

import json
from pathlib import Path

import pytest

from traceopt import analyze_command, build_dependencies

DATA = json.loads((Path(__file__).resolve().parents[1]
                   / "data/challenges/dependency_v1.json").read_text(encoding="utf-8"))


def test_challenge_dataset_has_labels_and_unique_ids():
    cases = DATA["cases"]
    assert len(cases) >= 40
    assert len({c["id"] for c in cases}) == len(cases)
    assert all(c["annotation"] and c["commands"] for c in cases)


@pytest.mark.parametrize("case", DATA["cases"], ids=lambda case: case["id"])
def test_challenge_edges(case):
    effects = [analyze_command(c, cwd=case["cwd"]) for c in case["commands"]]
    actual = {f"{edge.source}:{edge.target}:{edge.kind}" for edge in build_dependencies(effects)}
    assert actual == set(case["expected_edges"]), case["annotation"]
