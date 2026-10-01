"""白名单与保守拒绝的验收案例。"""

import re
from dataclasses import FrozenInstanceError

import pytest

from traceopt import analyze_command


@pytest.mark.parametrize("command,reads,writes", [
    ("cat a b", ("/repo/a", "/repo/b"), ()),
    ("head -n 5 a", ("/repo/a",), ()),
    ("tail -n 0 a", ("/repo/a",), ()),
    ("wc -l a", ("/repo/a",), ()),
    ("sort a", ("/repo/a",), ()),
    ("uniq a", ("/repo/a",), ()),
    ("grep -F -n needle a", ("/repo/a",), ()),
    ("rg --no-config --no-ignore -F needle a", ("/repo/a", "/repo"), ()),
    ("ls -la src", ("/repo/src",), ()),
    ("find src -type f", ("/repo/src",), ()),
    ("touch a", ("/repo/a",), ("/repo/a",)),
    ("mkdir -p a/b", (), ("/repo/a/b",)),
    ("rm -f a", (), ("/repo/a",)),
    ("cp a b", ("/repo/a",), ("/repo/b",)),
    ("mv a b", ("/repo/a",), ("/repo/a", "/repo/b")),
])
def test_supported_forms(command, reads, writes):
    effect = analyze_command(command, cwd="/repo")
    assert not effect.unknown, effect.reason
    assert effect.reads == reads
    assert effect.writes == writes
    assert effect.command == command
    with pytest.raises(FrozenInstanceError):
        effect.unknown = True


@pytest.mark.parametrize("command", [
    "cat", "head -c 5 a", "tail -f a", "wc --files0-from=x", "sort -o out a",
    "uniq a out", "grep -r x a", "rg needle a", "ls -R a", "find a -delete",
    "touch -r a b", "mkdir -m 777 a", "rm -rf a", "cp -r a b", "mv -t b a",
    "cat -", "cat a | wc -l", "cat a > b", "cat a; rm b", "cat $HOME/a",
    "cat $(pwd)", "cat `pwd`", "cat *.py", "cat 'a*b'", "cat a\nls b",
    "cat a # comment", "A=x cat a", "python x.py", "cat /dev/random",
    "cat /proc/self/environ", "cat /sys/a", "cat //host/a", "cat '\x00'",
    "cat 'broken", "head -n -1 a", "head -n a", "", "   ", "cat a --help",
])
def test_unknown_is_explicit_barrier(command):
    effect = analyze_command(command, cwd="/repo")
    assert effect.unknown
    assert effect.reason
    assert re.search("[\u4e00-\u9fff]", effect.reason)


def test_path_normalization():
    effect = analyze_command("cat 'a b' ./a/../c /absolute c", cwd="/repo/x/..")
    assert not effect.unknown
    assert effect.cwd == "/repo"
    assert effect.reads == ("/repo/a b", "/repo/c", "/absolute", "/repo/a")


def test_parent_traversal_keeps_directory_precondition():
    effect = analyze_command("rm a/../b", cwd="/repo")
    assert effect.reads == ("/repo/a",)
    assert effect.writes == ("/repo/b",)


def test_option_terminator_preserves_literal_filename():
    effect = analyze_command("cat -- -literal", cwd="/repo")
    assert not effect.unknown
    assert effect.reads == ("/repo/-literal",)
    assert analyze_command("cat -- -", cwd="/repo").unknown


@pytest.mark.parametrize("cwd", ["relative", "C:/repo", "//host/share", "/dev", "/a\x00"])
def test_cwd_must_be_explicit_posix_context(cwd):
    assert analyze_command("cat a", cwd=cwd).unknown


def test_analysis_does_not_execute(tmp_path):
    marker = tmp_path / "must-not-exist"
    effect = analyze_command(f"touch '{marker.as_posix()}'", cwd="/repo")
    assert not effect.unknown
    assert not marker.exists()
