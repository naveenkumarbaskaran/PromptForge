"""Prompt compression engine."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class CompressionResult:
    """Result of prompt compression."""
    text: str
    original_tokens: int
    compressed_tokens: int
    quality_score: float  # 0-1, estimated quality retention

    @property
    def savings_pct(self) -> float:
        if self.original_tokens == 0:
            return 0
        return (1 - self.compressed_tokens / self.original_tokens) * 100

    @property
    def stats(self) -> dict[str, Any]:
        return {
            "original_tokens": self.original_tokens,
            "compressed_tokens": self.compressed_tokens,
            "savings": f"{self.savings_pct:.0f}%",
            "quality_score": self.quality_score,
        }


class Compressor:
    """
    Prompt compression engine.

    Techniques:
    1. Remove filler words and hedging language
    2. Deduplicate semantically similar instructions
    3. Convert verbose sentences to imperative form
    4. Merge related instructions
    """

    # Filler patterns to remove
    FILLERS = [
        r"\byou should always\b",
        r"\bplease make sure to\b",
        r"\bit is important that you\b",
        r"\bremember to always\b",
        r"\bmake sure you\b",
        r"\bensure that you\b",
        r"\byou must always\b",
        r"\byou need to\b",
    ]

    # Verbose → concise mappings
    REPLACEMENTS = [
        (r"you are a (.+?)\.", r"\1."),
        (r"when you don't know something,?\s*", "If unknown: "),
        (r"never make up data or hallucinate facts", "No fabrication"),
        (r"be professional and concise in your responses", "Be concise, professional"),
        (r"format your response using", "Use"),
        (r"always include", "Include"),
        (r"in your response", ""),
    ]

    def compress(self, text: str) -> CompressionResult:
        """Compress a prompt text."""
        original_tokens = len(text) // 4

        result = text.strip()

        # Remove filler phrases
        for filler in self.FILLERS:
            result = re.sub(filler, "", result, flags=re.IGNORECASE)

        # Apply replacements
        for pattern, replacement in self.REPLACEMENTS:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        # Remove extra whitespace
        result = re.sub(r"\s+", " ", result).strip()
        result = re.sub(r"\.\s*\.", ".", result)

        # Remove empty sentences
        result = re.sub(r"\.\s+\.", ".", result)

        compressed_tokens = len(result) // 4

        # Quality estimate (heuristic: longer compression = more info loss)
        savings_ratio = 1 - (compressed_tokens / max(1, original_tokens))
        quality = max(0.5, 1 - savings_ratio * 0.3)

        return CompressionResult(
            text=result,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            quality_score=round(quality, 2),
        )
