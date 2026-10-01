"""受控循环挑战集评估；检测计分与真实重放分别记录。"""

import hashlib
import json
import platform
import re
import shlex
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

from .binding import _detect_runtime_loops, detect_runtime_loops
from .replay import ReplayError, replay_cat_loop
from .trajectory import load_trajectory


def _hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _write(path, value):
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def score_spans(expected, predicted):
    """按完整调用序列精确匹配，重复预测去重，未定义的比率返回空值。"""
    expected, predicted = {tuple(x) for x in expected}, {tuple(x) for x in predicted}
    tp, fp, fn = len(expected & predicted), len(predicted - expected), len(expected - predicted)
    return _metrics(tp, fp, fn)


def _metrics(tp, fp, fn):
    return {
        "tp": tp, "fp": fp, "fn": fn,
        "precision": tp / (tp + fp) if tp + fp else None,
        "recall": tp / (tp + fn) if tp + fn else None,
        "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None,
    }


def naive_loops(trajectory):
    """朴素基线：连续调用的词法参数前缀相同即视为循环，不检查来源或依赖。"""
    runs, ids, previous = [], [], None
    for event in trajectory.events:
        if event.kind != "tool_call":
            continue
        try:
            argv = shlex.split(event.command)
        except ValueError:
            argv = []
        prefix = tuple(argv[:-1]) if len(argv) >= 2 else None
        if prefix is None or prefix != previous:
            if len(ids) >= 2:
                runs.append(tuple(ids))
            ids = []
        if prefix is not None:
            ids.append(event.call_id)
        previous = prefix
    if len(ids) >= 2:
        runs.append(tuple(ids))
    return tuple(runs)


def _relative_file(value):
    if not isinstance(value, str):
        raise ValueError("仓库文件路径必须是字符串")
    path = PurePosixPath(value)
    if (not value or value == "." or path.is_absolute() or path.as_posix() != value
            or any(p in (".", "..") or not re.fullmatch(r"[\w .-]+", p)
                   or p.endswith((".", " "))
                   or p.split(".")[0].upper() in
                   {"CON", "PRN", "AUX", "NUL", *[f"COM{i}" for i in range(10)],
                    *[f"LPT{i}" for i in range(10)]} for p in path.parts)):
        raise ValueError("仓库文件必须使用普通、安全的相对路径")
    return path


def validate_dataset(data):
    """验证有限的人工挑战集格式；不执行其中的命令文本。"""
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("挑战集版本无效")
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("挑战集必须包含非空案例列表")
    seen = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("挑战案例必须是对象")
        cid = case.get("id")
        if not isinstance(cid, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", cid) or cid in seen:
            raise ValueError("案例 ID 无效或重复")
        seen.add(cid)
        if not isinstance(case.get("rationale"), str) or not case["rationale"].strip():
            raise ValueError("案例必须有人工标注理由")
        steps = case.get("steps")
        if not isinstance(steps, list) or not steps:
            raise ValueError("案例步骤必须是非空列表")
        calls = []
        for step in steps:
            if not isinstance(step, dict):
                raise ValueError("步骤必须是对象")
            if step.get("role") in ("user", "system"):
                if not isinstance(step.get("content"), str):
                    raise ValueError("消息内容必须是字符串")
                continue
            if not {"id", "command", "output", "returncode", "cwd"} <= step.keys():
                raise ValueError("调用缺少必需字段：id、command、output、returncode、cwd")
            call_id = step.get("id")
            if (not isinstance(call_id, str) or not call_id or call_id in calls
                    or not isinstance(step.get("command"), str)
                    or not isinstance(step.get("output"), (str, type(None)))
                    or type(step.get("returncode")) is not int
                    or not isinstance(step.get("cwd"), (str, type(None)))):
                raise ValueError("调用字段无效或 ID 重复")
            calls.append(call_id)
        spans = case.get("expected")
        if not isinstance(spans, list):
            raise ValueError("人工循环标签必须是列表")
        seen_spans = set()
        for span in spans:
            if (not isinstance(span, list) or len(span) < 2
                    or any(not isinstance(cid, str) or cid not in calls for cid in span)):
                raise ValueError("循环标签必须引用至少两个已有调用")
            start = calls.index(span[0])
            if calls[start:start + len(span)] != span or tuple(span) in seen_spans:
                raise ValueError("循环标签必须连续且不重复")
            seen_spans.add(tuple(span))
        files = case.get("repository")
        if not isinstance(files, dict):
            raise ValueError("案例必须提供片段初始仓库文件映射")
        normalized = set()
        for name, content in files.items():
            path = _relative_file(name)
            lower = path.as_posix().casefold()
            if lower in normalized or not isinstance(content, str):
                raise ValueError("仓库文件重复或内容不是 UTF-8 文本")
            normalized.add(lower)
        if any(str(parent).casefold() in normalized for name in files
               for parent in PurePosixPath(name).parents if str(parent) != "."):
            raise ValueError("仓库文件与父目录冲突")
    return cases


def _trajectory(case, folder):
    messages, contexts = [], {}
    for step in case["steps"]:
        if step.get("role") in ("user", "system"):
            messages.append({"role": step["role"], "content": step["content"]})
            continue
        cid = step["id"]
        if step["cwd"] is not None:
            contexts[cid] = step["cwd"]
        messages.extend([
            {"role": "assistant", "content": "人工挑战步骤", "tool_calls": [
                {"id": cid, "type": "function", "function": {
                    "name": "bash", "arguments": json.dumps({"command": step["command"]})}}]},
            {"role": "tool", "tool_call_id": cid, "content": step["output"] or "",
             "extra": {"returncode": step["returncode"], "raw_output": step["output"]}},
        ])
    path = folder / "input.traj.json"
    _write(path, {"trajectory_format": "mini-swe-agent-1.1", "messages": messages})
    return load_trajectory(path), contexts


def run_evaluation(config_path, output):
    """独占创建结果目录；中断不生成汇总，不自动注册 verified。"""
    config_path, output = Path(config_path).absolute(), Path(output).absolute()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if (not isinstance(config, dict) or set(config) != {"schema_version", "dataset", "timeout"}
            or config["schema_version"] != 1 or not isinstance(config["dataset"], str)
            or type(config["timeout"]) not in (int, float)
            or not 0 < config["timeout"] <= 120):
        raise ValueError("评估配置无效：需要版本、数据集路径与 0～120 秒超时")
    dataset_path = (config_path.parent / config["dataset"]).resolve()
    data = json.loads(dataset_path.read_text(encoding="utf-8"))
    cases = validate_dataset(data)
    output.mkdir(parents=True, exist_ok=False)
    _write(output / "config.json", config)
    _write(output / "dataset.json", data)
    source_dir = Path(__file__).parent
    manifest = {
        "schema_version": 1, "scope": "人工设计受控挑战集，非生产分布或模型成本实验",
        "python": sys.version, "platform": platform.platform(),
        "command": [sys.executable, *sys.argv], "cwd": str(Path.cwd()),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "config": str(config_path), "config_sha256": _hash(config_path),
        "dataset": str(dataset_path), "dataset_sha256": _hash(dataset_path),
        "source_hashes": {p.name: _hash(p) for p in sorted(source_dir.glob("*.py"))},
        "scoring_unit": "案例 ID 与完整连续调用 ID 序列；微平均；重复跨度去重",
        "replay_denominator": "生产检测的全部 cat 候选；错误和历史不符均计入失败",
    }
    _write(output / "manifest.json", manifest)
    raw, attempted, succeeded, excluded = [], 0, 0, 0
    totals = {name: {"tp": 0, "fp": 0, "fn": 0}
              for name in ("production", "naive", "no_dependency_guard")}
    for case in cases:
        folder = output / case["id"]
        folder.mkdir()
        trajectory, contexts = _trajectory(case, folder)
        loops = detect_runtime_loops(trajectory, cwd_by_call=contexts)
        predictions = {
            "production": [loop.call_ids for loop in loops],
            "naive": naive_loops(trajectory),
            "no_dependency_guard": [loop.call_ids for loop in _detect_runtime_loops(
                trajectory, cwd_by_call=contexts, check_dependencies=False)],
        }
        row = {"id": case["id"], "rationale": case["rationale"],
               "expected": case["expected"], "predictions": predictions, "scores": {},
               "trajectory_sha256": trajectory.source_sha256, "replays": []}
        for method, spans in predictions.items():
            metrics = score_spans(case["expected"], spans)
            row["scores"][method] = metrics
            for key in ("tp", "fp", "fn"):
                totals[method][key] += metrics[key]
        repository = folder / "initial_repo"
        repository.mkdir()
        for name, content in case["repository"].items():
            path = repository.joinpath(*PurePosixPath(name).parts)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content.encode("utf-8"))
        for index, loop in enumerate(loops):
            record = {"call_ids": loop.call_ids}
            if loop.plan.template_prefix != ("cat",):
                excluded += 1
                record.update(status="not_applicable", reason="当前重放器仅支持 cat 模板")
            else:
                attempted += 1
                try:
                    report = replay_cat_loop(trajectory, loop, repository=repository,
                                             virtual_root="/repo", cwd_by_call=contexts,
                                             timeout=config["timeout"])
                except (ReplayError, OSError) as exc:
                    record.update(status="error", successful=False, error=str(exc))
                else:
                    report_name = f"replay-{index}.json"
                    _write(folder / report_name, asdict(report))
                    record.update(status="completed", successful=report.successful,
                                  report=f"{case['id']}/{report_name}")
                    succeeded += int(report.successful)
            row["replays"].append(record)
        raw.append(row)
        _write(folder / "result.json", row)
    summary = {
        "schema_version": 1, "cases": len(cases),
        "positive_cases": sum(bool(c["expected"]) for c in cases),
        "expected_loops": sum(len(c["expected"]) for c in cases),
        "methods": {name: _metrics(**counts) for name, counts in totals.items()},
        "replay": {"attempted": attempted, "successful": succeeded,
                   "failed": attempted - succeeded, "not_applicable": excluded,
                   "success_rate": succeeded / attempted if attempted else None},
    }
    _write(output / "raw.json", raw)
    _write(output / "summary.json", summary)
    return summary
