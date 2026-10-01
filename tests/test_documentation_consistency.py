"""权威项目文档的一致性检查。"""
import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
AUTHORITATIVE = (
    ROOT / "README.md",
    ROOT / "CLAIMS.md",
    ROOT / "PROJECT_STATE.md",
    ROOT / "PROJECT_INDEX.md",
    ROOT / "docs/architecture/canonical_ir.md",
    ROOT / "docs/architecture/overview.md",
    ROOT / "docs/architecture/INDEX.md",
    ROOT / "docs/release_audit.md",
    ROOT / "RELEASE_HANDOFF.md",
)


def test_authoritative_docs_have_no_placeholder_lines() -> None:
    for path in AUTHORITATIVE:
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"^#{1,6} .*\?{3,}", text, re.MULTILINE), path
        assert "`n`n" not in text, path
        assert "`r`n" not in text, path


def test_current_iteration_and_capabilities_are_consistent() -> None:
    state = (ROOT / ".traceopt/state.yaml").read_text(encoding="utf-8")
    index = (ROOT / "PROJECT_INDEX.md").read_text(encoding="utf-8")
    project_state = (ROOT / "PROJECT_STATE.md").read_text(encoding="utf-8")
    match = re.search(r"^iteration:\s*(\d+)$", state, re.MULTILINE)
    assert match, "state.yaml \u7f3a\u5c11\u5f53\u524d iteration"
    iteration = int(match.group(1))
    iter_tag = f"iter_{iteration:03d}"
    assert re.search(r"phase: (planning|development|qa|finalizing)\n", state)
    assert f"iterations/{iter_tag}/PLAN.md" in state
    assert f"\u5f53\u524d\u8f6e\u6b21\uff1a{iter_tag}" in index
    assert re.search(
        rf"\u5f53\u524d {iter_tag} / (planning|development|qa|finalizing)",
        project_state,
    )
    assert "BUG-002 OPEN" not in project_state
    assert "VERIFIED_FIXED" in state
    assert "鐠" not in state
    assert "闁" not in state
    assert "tests/test_evaluation_qa.py" in state
    assert "tests/test_response_qa.py" in state


def test_release_snapshot_points_to_verified_evidence() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    index = (ROOT / "PROJECT_INDEX.md").read_text(encoding="utf-8")
    assert "发布候选已在独立环境完成安装" in readme
    assert "iterations/iter_019/QA_REPORT.md" in readme
    assert "iterations/iter_019/QA_REPORT.md" in index
    assert "正在最终验证" not in readme
    audit = (ROOT / "docs/release_audit.md").read_text(encoding="utf-8")
    assert "pyproject.toml` 中为 `0.1.0`" in audit
    assert "尚不能分发" not in audit
    assert "下一轮需明确发布版本" not in audit
    assert "没有 GitHub 远程发布" in audit
    handoff = (ROOT / "RELEASE_HANDOFF.md").read_text(encoding="utf-8")
    assert "0.1.0" in handoff
    assert "881efd39dfa3be0389a9e95fdf1405f7b2ef2afc980d95070f11a114d63f2c96" in handoff
    assert "尚未发布到 GitHub" in handoff


def test_replay_boundary_is_explicit() -> None:
    for path in AUTHORITATIVE:
        text = path.read_text(encoding="utf-8")
        if path.name in {"README.md", "CLAIMS.md", "PROJECT_STATE.md", "canonical_ir.md"}:
            assert "LLM conversation replay" in text
    canonical = (ROOT / "docs/architecture/canonical_ir.md").read_text(encoding="utf-8")
    assert "未知 output 类型" in canonical
    assert "response/output/function_call/function_call_output" in canonical


def test_markdown_links_in_authoritative_docs_exist() -> None:
    pattern = re.compile(r"\[[^\]]+\]\(([^)#]+)")
    for path in AUTHORITATIVE:
        for target in pattern.findall(path.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "#")):
                continue
            assert (path.parent / target).resolve().exists(), (path, target)



