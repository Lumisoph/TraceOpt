"""QA 从标注和原始产物独立重算，不调用产品计分函数。"""

import base64
import hashlib
import json
import sys
from pathlib import Path


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def verify(root):
    data = read(root / "dataset.json")
    rows = read(root / "raw.json")
    summary = read(root / "summary.json")
    cases = {c["id"]: c for c in data["cases"]}
    assert len(rows) == len(cases) == summary["cases"]
    assert len({r["id"] for r in rows}) == len(rows)
    assert {r["id"] for r in rows} == set(cases)
    attempted = succeeded = excluded = 0
    totals = {key: [0, 0, 0] for key in summary["methods"]}
    for row in rows:
        case = cases[row["id"]]
        assert row["expected"] == case["expected"]
        truth = {tuple(span) for span in case["expected"]}
        for method, spans in row["predictions"].items():
            predictions = {tuple(span) for span in spans}
            counts = [len(truth & predictions), len(predictions - truth),
                      len(truth - predictions)]
            assert counts == [row["scores"][method][k] for k in ("tp", "fp", "fn")]
            totals[method] = [a + b for a, b in zip(totals[method], counts, strict=True)]
        assert len(row["replays"]) == len(row["predictions"]["production"])
        for replay, span in zip(row["replays"], row["predictions"]["production"], strict=True):
            assert replay["call_ids"] == span
            if replay["status"] == "not_applicable":
                excluded += 1
                continue
            attempted += 1
            if replay["status"] == "error":
                assert replay["error"] and replay["successful"] is False
                continue
            report = read(root / replay["report"])
            same_state = report["initial_state"] == report["original_state"]
            same_state = same_state and report["initial_state"] == report["optimized_state"]
            equivalent = same_state and report["original"] == report["optimized"]
            calls = {s["id"]: s for s in case["steps"] if "id" in s}
            history = all(base64.b64decode(item["stdout_b64"]) ==
                          calls[cid]["output"].encode("utf-8") and
                          item["returncode"] == calls[cid]["returncode"]
                          for cid, item in zip(span, report["original"], strict=True))
            success = equivalent and history and all(
                item["returncode"] == 0 for item in report["original"])
            assert report["state_unchanged"] == same_state
            assert report["equivalent"] == equivalent
            assert report["matches_recording"] == history
            assert report["successful"] == replay["successful"] == success
            succeeded += int(success)
    for method, (tp, fp, fn) in totals.items():
        assert summary["methods"][method] == dict(
            tp=tp, fp=fp, fn=fn, precision=tp/(tp+fp) if tp+fp else None,
            recall=tp/(tp+fn) if tp+fn else None,
            f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None)
    assert summary["replay"] == dict(attempted=attempted, successful=succeeded,
                                    failed=attempted-succeeded, not_applicable=excluded,
                                    success_rate=succeeded/attempted if attempted else None)
    manifest = read(root / "manifest.json")
    for name, digest in manifest["source_hashes"].items():
        assert hashlib.sha256((Path("src/traceopt") / name).read_bytes()).hexdigest() == digest
    for key in ("config", "dataset"):
        actual = hashlib.sha256(Path(manifest[key]).read_bytes()).hexdigest()
        assert actual == manifest[key+"_sha256"]
    return summary, {r["id"]: r["predictions"] for r in rows}


first, second = map(Path, sys.argv[1:])
assert verify(first) == verify(second)
print("两次评估的预测与汇总一致；独立重算所有跨度、重放分母和执行报告布尔结论通过。")
