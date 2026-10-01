"""QA 验证前缀读取、外部指令与未完成调用屏障。"""

from dataclasses import replace

from traceopt import detect_runtime_loops, infer_loop_at


def test_future_cwd_is_never_read_during_prefix_inference(binding_trace):
    trajectory, contexts, start = binding_trace()

    class PrefixOnly(dict):
        def get(self, key, default=None):
            assert key != "consumer-1", "前缀推断读取了未来上下文"
            return super().get(key, default)

    assert infer_loop_at(trajectory, start, cwd_by_call=PrefixOnly(contexts)) is not None


def test_new_user_instruction_prevents_suffix_matching(binding_trace):
    trajectory, contexts, _ = binding_trace()
    events = tuple(replace(e, role="user", content="改变目标") if e.index == 6 else e
                   for e in trajectory.events)
    assert detect_runtime_loops(replace(trajectory, events=events), cwd_by_call=contexts) == ()


def test_unfinished_intervening_call_blocks_plan(binding_trace):
    trajectory, contexts, start = binding_trace(between=["cat /elsewhere/file"])
    events = tuple(replace(e, kind="message", role="assistant")
                   if e.kind == "tool_result" and e.call_id == "between-0" else e
                   for e in trajectory.events)
    assert infer_loop_at(replace(trajectory, events=events), start, cwd_by_call=contexts) is None
