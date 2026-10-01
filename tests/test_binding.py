"""绑定与前缀构造的明确验收边界。"""

from dataclasses import FrozenInstanceError, replace

import pytest

from traceopt import analyze_command, detect_runtime_loops, infer_loop_at


def test_plan_and_detected_source_identity(binding_trace):
    t, cwd, start = binding_trace()
    plan = infer_loop_at(t, start, cwd_by_call=cwd)
    assert plan.producer_call_id == "producer"
    assert plan.producer_event_index == 1
    assert plan.observation_event_index == 2
    assert plan.prefix_end_index == start
    assert plan.paths == ("/repo/src/a", "/repo/src/b")
    assert plan.predicted_argv == (("cat", "/repo/src/a"), ("cat", "/repo/src/b"))
    detected, = detect_runtime_loops(t, cwd_by_call=cwd)
    assert detected.plan == plan
    assert detected.call_ids == ("consumer-0", "consumer-1")
    assert detected.event_indices == (4, 7)
    with pytest.raises(FrozenInstanceError):
        plan.cwd = "/other"


@pytest.mark.parametrize("template", ["cat", "head", "head -n 3", "tail -n 4", "wc -l",
                                     "sort", "uniq"])
def test_supported_templates(binding_trace, template):
    t, cwd, start = binding_trace(commands=[f"{template} src/a", f"{template} src/b"])
    assert infer_loop_at(t, start, cwd_by_call=cwd) is not None
    assert len(detect_runtime_loops(t, cwd_by_call=cwd)) == 1


def test_three_paths_spaces_and_absolute_forms(binding_trace):
    t, cwd, start = binding_trace(output="src/a b\0/repo/src/c\0src/d\0", commands=[
        "cat 'src/a b'", "cat /repo/src/c", "cat ./src/d"])
    plan = infer_loop_at(t, start, cwd_by_call=cwd)
    assert plan.paths == ("/repo/src/a b", "/repo/src/c", "/repo/src/d")
    assert len(detect_runtime_loops(t, cwd_by_call=cwd)) == 1


@pytest.mark.parametrize("output", [None, "", "src/a\n src/b\n", "src/a\0", "src/a\0src/b",
                                  "src/a\0\0", "src/a\0src/a\0", "src/a\0./src/a\0",
                                  "src/a\0../escape\0", "src/a\0src/$(evil)\0",
                                  "src/a\0src/b\nname\0"])
def test_invalid_source_lists_rejected(binding_trace, output):
    t, cwd, start = binding_trace(output=output)
    assert infer_loop_at(t, start, cwd_by_call=cwd) is None


@pytest.mark.parametrize("code", [1, -1, None])
def test_failed_or_unknown_producer_rejected(binding_trace, code):
    t, cwd, start = binding_trace(returncode=code)
    assert infer_loop_at(t, start, cwd_by_call=cwd) is None


def test_newline_find_output_is_not_accepted(binding_trace):
    t, cwd, start = binding_trace(producer="find src -type f")
    assert infer_loop_at(t, start, cwd_by_call=cwd) is None


@pytest.mark.parametrize("between", [["touch src/a"], ["rm src"], ["unknown command"]])
def test_prefix_conflicts_and_unknown_calls_rejected(binding_trace, between):
    t, cwd, start = binding_trace(between=between)
    assert infer_loop_at(t, start, cwd_by_call=cwd) is None


@pytest.mark.parametrize("between", [["cat src/a"], ["touch /elsewhere/a"]])
def test_nonconflicting_completed_prefix_allowed(binding_trace, between):
    t, cwd, start = binding_trace(between=between)
    assert infer_loop_at(t, start, cwd_by_call=cwd) is not None


@pytest.mark.parametrize("commands", [["cat src/a"], ["cat src/b", "cat src/a"],
                                    ["head -n 2 src/a", "head -n 3 src/b"],
                                    ["cat src/a", "ls src", "cat src/b"]])
def test_nonmatching_suffix_rejected(binding_trace, commands):
    t, cwd, _ = binding_trace(commands=commands)
    assert detect_runtime_loops(t, cwd_by_call=cwd) == ()


def test_missing_context_and_unfinished_prefix_rejected(binding_trace):
    t, cwd, start = binding_trace()
    assert infer_loop_at(t, start, cwd_by_call={}) is None
    events = tuple(replace(e, kind="message") if e.kind == "tool_result" else e for e in t.events)
    assert infer_loop_at(replace(t, events=events), start, cwd_by_call=cwd) is None


def test_plan_uses_prefix_only_and_survives_truncation(binding_trace):
    original, cwd, start = binding_trace()
    altered, future_cwd, _ = binding_trace(commands=["cat src/a", "touch unrelated"],
                                          consumer_outputs=["future secret", "other secret"])
    future_cwd["consumer-1"] = "/future"
    assert original.source_sha256 != altered.source_sha256
    expected = infer_loop_at(original, start, cwd_by_call=cwd)
    assert expected is not None
    assert infer_loop_at(altered, start, cwd_by_call=future_cwd) == expected
    prefix = replace(original, events=original.events[:start + 1], source_sha256="irrelevant")
    assert infer_loop_at(prefix, start, cwd_by_call=cwd) == expected
    assert detect_runtime_loops(prefix, cwd_by_call=cwd) == ()


def test_find_print0_has_same_filesystem_effect():
    plain = analyze_command("find src -type f", cwd="/repo")
    nul = analyze_command("find src -type f -print0", cwd="/repo")
    assert not nul.unknown
    assert (nul.reads, nul.writes) == (plain.reads, plain.writes)


def test_invalid_start_index(binding_trace):
    t, cwd, _ = binding_trace()
    for start in [-1, 999, True, 0]:
        with pytest.raises(ValueError, match="[\u4e00-\u9fff]"):
            infer_loop_at(t, start, cwd_by_call=cwd)
