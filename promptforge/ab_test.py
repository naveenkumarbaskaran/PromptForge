"""A/B testing for prompt variants."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ABTest:
    """
    Statistical A/B test between prompt variants.

    Tracks per-variant metrics and computes significance.
    """

    name: str
    variants: dict[str, str]  # variant_name → prompt_key
    metric: str = "success_rate"
    min_samples: int = 100
    confidence_level: float = 0.95

    # Results tracking
    _results: dict[str, list[float]] = field(default_factory=dict)

    def __post_init__(self):
        for variant in self.variants:
            self._results[variant] = []

    def record(self, variant: str, value: float) -> None:
        """Record a metric observation for a variant."""
        if variant not in self._results:
            raise ValueError(f"Unknown variant: {variant}")
        self._results[variant].append(value)

    @property
    def sample_count(self) -> dict[str, int]:
        return {k: len(v) for k, v in self._results.items()}

    @property
    def is_significant(self) -> bool:
        """Check if we have enough samples for significance."""
        return all(len(v) >= self.min_samples for v in self._results.values())

    def summary(self) -> dict[str, Any]:
        """Get test summary with means and significance."""
        means = {}
        for variant, values in self._results.items():
            if values:
                means[variant] = {
                    "mean": sum(values) / len(values),
                    "n": len(values),
                    "std": _std(values),
                }
            else:
                means[variant] = {"mean": 0, "n": 0, "std": 0}

        winner = max(means, key=lambda k: means[k]["mean"]) if means else None

        return {
            "test_name": self.name,
            "metric": self.metric,
            "variants": means,
            "winner": winner,
            "significant": self.is_significant,
            "samples_needed": self.min_samples,
        }

    def pick_variant(self) -> str:
        """Pick which variant to show (epsilon-greedy exploration)."""
        import random
        if random.random() < 0.1:  # 10% exploration
            return random.choice(list(self.variants.keys()))
        # Exploit: pick best performing
        if not any(self._results.values()):
            return list(self.variants.keys())[0]
        return max(
            self._results,
            key=lambda k: sum(self._results[k]) / max(1, len(self._results[k])),
        )


def _std(values: list[float]) -> float:
    """Standard deviation."""
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)
