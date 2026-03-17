"""Prompt linter — detect contradictions, redundancy, and issues."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class LintIssue:
    """A prompt quality issue."""
    severity: str  # "error", "warning", "info"
    message: str
    line: int | None = None


class Linter:
    """
    Prompt quality linter.

    Detects:
    - Contradicting instructions (concise vs detailed)
    - Redundant phrases (same instruction twice)
    - Vague language (might, maybe, try to)
    - Missing role definition
    - Excessive length warnings
    """

    # Contradiction pairs
    CONTRADICTIONS = [
        (r"\bconcise\b|\bbrief\b|\bshort\b", r"\bdetailed\b|\bthorough\b|\bcomprehensive\b"),
        (r"\balways\b", r"\bnever\b"),
        (r"\bformal\b", r"\bcasual\b|\binformal\b"),
    ]

    # Redundancy patterns (semantically equivalent)
    REDUNDANCIES = [
        [r"\bconcise\b", r"\bbrief\b", r"\bshort\b"],
        [r"\bhelpful\b", r"\bassist\b", r"\bhelp\b"],
        [r"\bdon't hallucinate\b", r"\bno fabrication\b", r"\bdon't make up\b"],
    ]

    # Vague language
    VAGUE_PATTERNS = [
        (r"\btry to\b", "Use imperative: 'do X' instead of 'try to X'"),
        (r"\bmaybe\b|\bperhaps\b", "Vague: be definitive in instructions"),
        (r"\bif possible\b", "Ambiguous: specify when it IS possible"),
        (r"\bsort of\b|\bkind of\b", "Vague qualifier: be specific"),
    ]

    def check(self, prompt: str) -> list[LintIssue]:
        """Lint a prompt and return all issues."""
        issues: list[LintIssue] = []

        # Check contradictions
        for pattern_a, pattern_b in self.CONTRADICTIONS:
            if re.search(pattern_a, prompt, re.IGNORECASE) and re.search(pattern_b, prompt, re.IGNORECASE):
                match_a = re.search(pattern_a, prompt, re.IGNORECASE)
                match_b = re.search(pattern_b, prompt, re.IGNORECASE)
                issues.append(LintIssue(
                    severity="warning",
                    message=f"Contradicting instructions: '{match_a.group()}' vs '{match_b.group()}'",
                ))

        # Check redundancies
        for group in self.REDUNDANCIES:
            matches = [re.search(p, prompt, re.IGNORECASE) for p in group]
            found = [m.group() for m in matches if m]
            if len(found) >= 2:
                issues.append(LintIssue(
                    severity="info",
                    message=f"Redundant: '{found[0]}' and '{found[1]}' say the same thing",
                ))

        # Check vague language
        for pattern, suggestion in self.VAGUE_PATTERNS:
            if re.search(pattern, prompt, re.IGNORECASE):
                issues.append(LintIssue(
                    severity="info",
                    message=suggestion,
                ))

        # Check length
        token_est = len(prompt) // 4
        if token_est > 500:
            issues.append(LintIssue(
                severity="warning",
                message=f"Prompt is ~{token_est} tokens. Consider compression (target: <200).",
            ))

        # Check for role definition
        if not re.search(r"\byou are\b|\brole:\b|\bact as\b", prompt, re.IGNORECASE):
            issues.append(LintIssue(
                severity="info",
                message="No explicit role definition found. Consider adding 'You are a...'",
            ))

        return issues
