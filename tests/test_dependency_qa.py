"""QA：未来信息、屏障可达性和路径边界对抗测试。"""

from traceopt import analyze_command, build_dependencies


def test_future_commands_do_not_change_prefix_edges():
    effects = [analyze_command(c, cwd="/repo") for c in
               ["rm a", "cat a", "touch b", "python unknown", "mv a b"]]
    prefix_edges = build_dependencies(effects[:3])
    assert tuple(e for e in build_dependencies(effects) if e.target < 3) == prefix_edges


def test_barrier_provides_path_between_otherwise_disjoint_calls():
    effects = [analyze_command(c, cwd="/repo") for c in ["cat a", "unknown", "cat b"]]
    edges = build_dependencies(effects)
    reachable = {0}
    for edge in edges:
        if edge.source in reachable:
            reachable.add(edge.target)
    assert reachable == {0, 1, 2}
    assert all(e.kind == "BARRIER" for e in edges)


def test_unicode_directory_boundary_does_not_create_false_prefix_conflict():
    effects = [analyze_command(c, cwd="/repo") for c in
               ["rm 数据", "cat 数据库/a", "cat 数据/a"]]
    edges = build_dependencies(effects)
    assert [(e.source, e.target, e.kind) for e in edges] == [(0, 2, "RAW")]
