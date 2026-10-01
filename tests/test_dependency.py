"""依赖类型、资源证据和方向不变量。"""

from dataclasses import FrozenInstanceError

import pytest

from traceopt import CommandEffect, analyze_command, build_dependencies


def effect(reads=(), writes=(), unknown=False):
    return CommandEffect("人工 Effect", (), "/repo", reads, writes, unknown)


def test_all_hazards_and_resource_witnesses():
    edges = build_dependencies([effect(("/a",), ("/a",)), effect(("/a",), ("/a",))])
    assert [e.kind for e in edges] == ["RAW", "WAR", "WAW"]
    assert all((e.source, e.target, e.left_resource, e.right_resource)
               == (0, 1, "/a", "/a") for e in edges)
    with pytest.raises(FrozenInstanceError):
        edges[0].source = 2


@pytest.mark.parametrize("left,right,expected", [
    ("/a", "/a/b", True), ("/a/b", "/a", True), ("/", "/a", True),
    ("/a", "/", True), ("/a", "/ab", False), ("/a/b", "/a/c", False),
])
def test_subtree_overlap(left, right, expected):
    edges = build_dependencies([effect(writes=(left,)), effect(reads=(right,))])
    assert bool(edges) == expected


def test_read_read_empty_and_disjoint():
    assert build_dependencies([]) == ()
    assert build_dependencies([effect()]) == ()
    assert build_dependencies([effect(("/a",)), effect(("/a",))]) == ()
    assert build_dependencies([effect(writes=("/a",)), effect(writes=("/b",))]) == ()


def test_unknown_is_global_order_barrier():
    edges = build_dependencies([effect(("/a",)), effect(unknown=True),
                                effect(("/b",)), effect(("/c",))])
    assert [(e.source, e.target, e.kind) for e in edges] == [
        (0, 1, "BARRIER"), (1, 2, "BARRIER"), (1, 3, "BARRIER")]
    assert all(e.left_resource is None and e.right_resource is None for e in edges)


def test_stable_deduplicated_resource_order():
    edges = build_dependencies([effect(writes=("/b", "/a", "/a")), effect(reads=("/",))])
    assert [(e.left_resource, e.right_resource) for e in edges] == [("/a", "/"), ("/b", "/")]
    assert edges == build_dependencies([effect(writes=("/a", "/b")), effect(reads=("/",))])


@pytest.mark.parametrize("path", ["relative", "/a/../b", "/a/", "//a", "C:/a", "/a\x00"])
def test_malformed_manual_resource_is_rejected(path):
    with pytest.raises(ValueError, match="规范 POSIX"):
        build_dependencies([effect(reads=(path,))])


def test_parent_traversal_dependency_is_retained():
    effects = [analyze_command(c, cwd="/repo") for c in ["mkdir a", "cat a/../b"]]
    assert any(e.kind == "RAW" and e.right_resource == "/repo/a"
               for e in build_dependencies(effects))


def test_wrong_effect_type_is_rejected():
    with pytest.raises(ValueError, match="CommandEffect"):
        build_dependencies([None])
