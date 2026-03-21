"""Tests for PromptForge."""

import pytest
from promptforge import Prompt, PromptRegistry, Compressor, Linter, LintIssue, ABTest


class TestPrompt:
    def test_create(self):
        p = Prompt(name="test", version="1.0", template="Hello {name}")
        assert p.key == "test@1.0"

    def test_token_estimate(self):
        p = Prompt(name="test", version="1.0", template="x" * 400)
        assert p.token_estimate == 100

    def test_render(self):
        p = Prompt(name="test", version="1.0", template="Hello {name}, your order is {order_id}.",
                   variables=["name", "order_id"])
        result = p.render(name="Naveen", order_id="4002310")
        assert "Naveen" in result
        assert "4002310" in result

    def test_evolve(self):
        p = Prompt(name="test", version="1.0", template="original")
        p2 = p.evolve(version="1.1", template="improved")
        assert p2.version == "1.1"
        assert p2.parent_version == "1.0"
        assert p2.template == "improved"

    def test_diff(self):
        p1 = Prompt(name="test", version="1.0", template="short")
        p2 = Prompt(name="test", version="1.1", template="much longer template here")
        diff = p1.diff(p2)
        assert diff["token_change"] > 0
        assert diff["template_changed"] is True


class TestRegistry:
    def test_register_and_get(self):
        reg = PromptRegistry()
        p = Prompt(name="planner", version="1.0", template="Plan: {query}")
        reg.register(p)
        assert reg.get("planner") == p

    def test_get_specific_version(self):
        reg = PromptRegistry()
        p1 = Prompt(name="planner", version="1.0", template="v1")
        p2 = Prompt(name="planner", version="2.0", template="v2")
        reg.register(p1)
        reg.register(p2)
        assert reg.get("planner", "1.0").template == "v1"
        assert reg.get("planner", "2.0").template == "v2"

    def test_get_latest(self):
        reg = PromptRegistry()
        reg.register(Prompt(name="x", version="1.0", template="old"))
        reg.register(Prompt(name="x", version="2.0", template="new"))
        assert reg.get_latest("x").version == "2.0"

    def test_duplicate_version_raises(self):
        reg = PromptRegistry()
        reg.register(Prompt(name="x", version="1.0", template="t"))
        with pytest.raises(ValueError):
            reg.register(Prompt(name="x", version="1.0", template="t2"))

    def test_history(self):
        reg = PromptRegistry()
        reg.register(Prompt(name="x", version="1.0", template="a"))
        reg.register(Prompt(name="x", version="1.1", template="b"))
        reg.register(Prompt(name="x", version="2.0", template="c"))
        assert len(reg.history("x")) == 3

    def test_list_prompts(self):
        reg = PromptRegistry()
        reg.register(Prompt(name="a", version="1.0", template=""))
        reg.register(Prompt(name="b", version="1.0", template=""))
        assert set(reg.list_prompts()) == {"a", "b"}

    def test_rollback(self):
        reg = PromptRegistry()
        reg.register(Prompt(name="x", version="1.0", template="good"))
        reg.register(Prompt(name="x", version="2.0", template="bad"))
        rolled = reg.rollback("x", "1.0")
        assert rolled is not None
        assert rolled.template == "good"
        assert "rollback" in rolled.version


class TestCompressor:
    def test_basic_compression(self):
        c = Compressor()
        result = c.compress("You should always be concise. Make sure you include the order number.")
        assert result.compressed_tokens < result.original_tokens
        assert result.savings_pct > 0

    def test_filler_removal(self):
        c = Compressor()
        result = c.compress("You should always respond quickly. Remember to always be polite.")
        assert "should always" not in result.text
        assert "remember to always" not in result.text.lower()

    def test_quality_score(self):
        c = Compressor()
        result = c.compress("A simple short prompt.")
        assert 0.5 <= result.quality_score <= 1.0

    def test_stats(self):
        c = Compressor()
        result = c.compress("You are a helpful assistant that helps users.")
        stats = result.stats
        assert "original_tokens" in stats
        assert "savings" in stats


class TestLinter:
    def test_contradiction_detected(self):
        linter = Linter()
        issues = linter.check("Be concise. Provide detailed explanations.")
        assert any("Contradict" in i.message for i in issues)

    def test_redundancy_detected(self):
        linter = Linter()
        issues = linter.check("Be concise and brief in responses.")
        assert any("Redundant" in i.message for i in issues)

    def test_vague_language(self):
        linter = Linter()
        issues = linter.check("Try to help the user. Maybe include examples.")
        assert any("Vague" in i.message or "imperative" in i.message for i in issues)

    def test_long_prompt_warning(self):
        linter = Linter()
        issues = linter.check("x " * 1000)
        assert any("tokens" in i.message for i in issues)

    def test_clean_prompt_no_issues(self):
        linter = Linter()
        issues = linter.check("You are a maintenance analyst. Report order status concisely.")
        # May have info-level but no warnings/errors
        warnings = [i for i in issues if i.severity in ("warning", "error")]
        assert len(warnings) == 0


class TestABTest:
    def test_record_and_summary(self):
        test = ABTest(
            name="test",
            variants={"a": "prompt@1.0", "b": "prompt@2.0"},
            min_samples=5,
        )
        for _ in range(10):
            test.record("a", 0.8)
            test.record("b", 0.9)

        summary = test.summary()
        assert summary["winner"] == "b"
        assert summary["significant"] is True

    def test_not_significant(self):
        test = ABTest(name="test", variants={"a": "p@1", "b": "p@2"}, min_samples=100)
        test.record("a", 1.0)
        assert test.is_significant is False

    def test_pick_variant(self):
        test = ABTest(name="test", variants={"a": "p@1", "b": "p@2"})
        variant = test.pick_variant()
        assert variant in ("a", "b")
