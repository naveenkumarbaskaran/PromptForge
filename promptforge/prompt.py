"""Prompt model with versioning and metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time


@dataclass
class Prompt:
    """
    A versioned prompt with metadata.

    Supports template variables, token estimation, and evolution tracking.
    """

    name: str
    version: str
    template: str
    variables: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    parent_version: str | None = None

    @property
    def token_estimate(self) -> int:
        """Approximate token count."""
        return max(1, len(self.template) // 4)

    @property
    def key(self) -> str:
        """Unique identifier: name@version."""
        return f"{self.name}@{self.version}"

    def render(self, **kwargs: str) -> str:
        """Render template with variables."""
        result = self.template
        for var in self.variables:
            placeholder = "{" + var + "}"
            if var in kwargs:
                result = result.replace(placeholder, kwargs[var])
        return result

    def evolve(self, version: str, template: str | None = None, **kwargs: Any) -> Prompt:
        """Create a new version derived from this prompt."""
        return Prompt(
            name=self.name,
            version=version,
            template=template or self.template,
            variables=kwargs.get("variables", self.variables),
            metadata=kwargs.get("metadata", {}),
            parent_version=self.version,
        )

    def diff(self, other: Prompt) -> dict[str, Any]:
        """Compare this prompt with another version."""
        return {
            "name": self.name,
            "from_version": self.version,
            "to_version": other.version,
            "token_change": other.token_estimate - self.token_estimate,
            "char_change": len(other.template) - len(self.template),
            "template_changed": self.template != other.template,
            "variables_changed": self.variables != other.variables,
        }
