"""QA 对抗检查：规范化不得消除资源前提。"""

from traceopt import analyze_command


def test_copy_target_parent_traversal_is_read_dependency():
    effect = analyze_command("cp src a/b/../../out", cwd="/repo")
    assert not effect.unknown
    assert effect.reads == ("/repo/src", "/repo/a/b", "/repo/a")
    assert effect.writes == ("/repo/out",)


def test_special_resource_cannot_be_hidden_by_parent_normalization():
    assert analyze_command("cat /dev/../repo/a", cwd="/repo").unknown


def test_quoted_substitution_is_conservatively_unknown():
    effect = analyze_command("grep -F '$(touch marker)' file", cwd="/repo")
    assert effect.unknown
    assert effect.reason
