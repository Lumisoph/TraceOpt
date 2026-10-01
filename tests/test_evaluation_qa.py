"""QA 补充输入缺失与跨平台路径冲突的对抗检查。"""

import json
from copy import deepcopy
from pathlib import Path

import pytest

from traceopt.evaluation import run_evaluation, validate_dataset

DATA = json.loads((Path(__file__).parents[1] / "data/challenges/loops_v1.json")
                  .read_text(encoding="utf-8"))


@pytest.mark.parametrize("field", ["output", "cwd"])
def test_missing_required_call_field_rejected_before_creating_output(tmp_path, field):
    data = {"schema_version": 1, "cases": [deepcopy(DATA["cases"][0])]}
    del data["cases"][0]["steps"][0][field]
    (tmp_path / "data.json").write_text(json.dumps(data), encoding="utf-8")
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"schema_version": 1, "dataset": "data.json", "timeout": 10}),
                      encoding="utf-8")
    with pytest.raises(ValueError, match="字段"):
        run_evaluation(config, tmp_path / "output")
    assert not (tmp_path / "output").exists()


@pytest.mark.parametrize("files", [{"src/a": "", "src/A": ""},
                                   {"src": "", "src/a": ""}])
def test_repository_case_and_parent_collisions_rejected(files):
    data = deepcopy(DATA)
    data["cases"][0]["repository"] = files
    with pytest.raises(ValueError, match="重复|冲突"):
        validate_dataset(data)
