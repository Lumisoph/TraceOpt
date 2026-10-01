"""验证精确跨度计分、受控标注、单因素消融与实际重放统计。"""

import json
import os
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from traceopt import detect_runtime_loops
from traceopt.binding import _detect_runtime_loops
from traceopt.evaluation import (
    _trajectory,
    naive_loops,
    run_evaluation,
    score_spans,
    validate_dataset,
)

DATASET = Path(__file__).parents[1] / "data/challenges/loops_v1.json"
DATA = json.loads(DATASET.read_text(encoding="utf-8"))


def test_metrics_exact_span_and_duplicate_predictions():
    result = score_spans([("a", "b"), ("c", "d")],
                         [("a", "b"), ("a", "b"), ("c", "d", "e")])
    assert result == {"tp": 1, "fp": 1, "fn": 1,
                      "precision": 0.5, "recall": 0.5, "f1": 0.5}


def test_metrics_empty_denominators_are_not_success():
    assert score_spans([], []) == {"tp": 0, "fp": 0, "fn": 0,
                                  "precision": None, "recall": None, "f1": None}
    assert score_spans([["a", "b"]], [])["f1"] == 0
    assert score_spans([], [["a", "b"]])["precision"] == 0


def test_dataset_has_independent_unique_annotations():
    cases = validate_dataset(DATA)
    assert len(cases) >= 40
    assert any(case["expected"] for case in cases)
    assert any(not case["expected"] for case in cases)


@pytest.mark.parametrize("case", DATA["cases"], ids=lambda case: case["id"])
def test_annotated_detection_challenge(case, tmp_path):
    trajectory, contexts = _trajectory(case, tmp_path)
    actual = [list(loop.call_ids) for loop in
              detect_runtime_loops(trajectory, cwd_by_call=contexts)]
    assert actual == case["expected"], case["rationale"]


def test_ablation_removes_only_dependency_guard(binding_trace):
    trace, contexts, _ = binding_trace(between=["touch src/a"])
    assert detect_runtime_loops(trace, cwd_by_call=contexts) == ()
    assert len(_detect_runtime_loops(trace, cwd_by_call=contexts,
                                    check_dependencies=False)) == 1
    failed, contexts, _ = binding_trace(returncode=1, between=["touch src/a"])
    assert _detect_runtime_loops(failed, cwd_by_call=contexts, check_dependencies=False) == ()
    plain, contexts, _ = binding_trace()
    assert detect_runtime_loops(plain, cwd_by_call=contexts) == _detect_runtime_loops(
        plain, cwd_by_call=contexts, check_dependencies=False)


def test_naive_baseline_ignores_failed_source(binding_trace):
    trace, contexts, _ = binding_trace(returncode=1)
    assert naive_loops(trace) == (("consumer-0", "consumer-1"),)
    assert detect_runtime_loops(trace, cwd_by_call=contexts) == ()


@pytest.mark.parametrize("path", ["../escape", "/absolute", "C:/drive", "src/a:stream",
                                  "src\\a", "src/NUL", "src/a.", "src/a "])
def test_dataset_rejects_unsafe_repository_paths(path):
    data = deepcopy(DATA)
    data["cases"][0]["repository"] = {path: "unsafe"}
    with pytest.raises(ValueError, match="路径"):
        validate_dataset(data)


def test_dataset_rejects_duplicate_id_and_bad_labels():
    data = deepcopy(DATA)
    data["cases"][1]["id"] = data["cases"][0]["id"]
    with pytest.raises(ValueError, match="重复"):
        validate_dataset(data)
    data = deepcopy(DATA)
    data["cases"][0]["expected"] = [["a", "nonexistent"]]
    with pytest.raises(ValueError, match="引用"):
        validate_dataset(data)


def test_actual_replay_denominator_includes_mismatch_and_error(tmp_path):
    selected = [case for case in DATA["cases"]
                if case["id"] in ("L001", "L006", "L014", "L015", "L016", "L017")]
    (tmp_path / "data.json").write_text(json.dumps({"schema_version": 1, "cases": selected}),
                                       encoding="utf-8")
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"schema_version": 1, "dataset": "data.json", "timeout": 10}),
                      encoding="utf-8")
    output = tmp_path / "run"
    result = run_evaluation(config, output)
    assert result["replay"] == {"attempted": 5, "successful": 1, "failed": 4,
                                "not_applicable": 1, "success_rate": 0.2}
    rows = json.loads((output / "raw.json").read_text(encoding="utf-8"))
    assert [row["replays"][0]["status"] for row in rows] == [
        "completed", "not_applicable", "completed", "error", "error", "error"]
    report = json.loads((output / "L014/replay-0.json").read_text(encoding="utf-8"))
    assert report["equivalent"] and not report["matches_recording"]
    assert run_evaluation(config, tmp_path / "rerun") == result
    with pytest.raises(FileExistsError):
        run_evaluation(config, output)


def test_no_candidates_has_null_replay_rate(tmp_path):
    data = {"schema_version": 1, "cases": [DATA["cases"][17]]}
    (tmp_path / "data.json").write_text(json.dumps(data), encoding="utf-8")
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"schema_version": 1, "dataset": "data.json", "timeout": 10}),
                      encoding="utf-8")
    summary = run_evaluation(config, tmp_path / "run")
    assert summary["replay"]["success_rate"] is None
    assert summary["replay"]["attempted"] == 0


@pytest.mark.parametrize("field", ["id", "command", "output", "returncode", "cwd"])
def test_all_required_call_fields_checked(field):
    data = deepcopy(DATA)
    del data["cases"][0]["steps"][0][field]
    with pytest.raises(ValueError, match="必需字段"):
        validate_dataset(data)


def test_explicit_null_fields_remain_valid():
    data = deepcopy(DATA)
    data["cases"][0]["steps"][0].update(output=None, cwd=None)
    assert validate_dataset(data) == data["cases"]


def test_evaluation_entry_reports_missing_field_without_traceback(tmp_path):
    data = {"schema_version": 1, "cases": [deepcopy(DATA["cases"][0])]}
    del data["cases"][0]["steps"][0]["cwd"]
    (tmp_path / "data.json").write_text(json.dumps(data), encoding="utf-8")
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"schema_version": 1, "dataset": "data.json", "timeout": 10}),
                      encoding="utf-8")
    script = Path(__file__).parents[1] / "experiments/evaluate.py"
    result = subprocess.run([sys.executable, str(script), str(config), str(tmp_path / "output")],
                            capture_output=True, env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    assert result.returncode == 2
    assert "调用缺少必需字段" in result.stderr.decode("utf-8")
    assert b"Traceback" not in result.stderr
    assert not (tmp_path / "output").exists()
