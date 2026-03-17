"""Version-controlled prompt registry."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import json
import os

from promptforge.prompt import Prompt


@dataclass
class PromptRegistry:
    """
    Git-like prompt version control.

    Stores prompts by name with full version history.
    Supports file-based persistence (YAML/JSON).
    """

    storage_path: str | None = None
    _prompts: dict[str, list[Prompt]] = field(default_factory=dict)

    def register(self, prompt: Prompt) -> None:
        """Register a new prompt version."""
        if prompt.name not in self._prompts:
            self._prompts[prompt.name] = []

        # Prevent duplicate versions
        existing = [p.version for p in self._prompts[prompt.name]]
        if prompt.version in existing:
            raise ValueError(f"Version {prompt.version} already exists for {prompt.name}")

        self._prompts[prompt.name].append(prompt)

    def get(self, name: str, version: str | None = None) -> Prompt | None:
        """Get a prompt by name and optional version (latest if omitted)."""
        if name not in self._prompts:
            return None

        versions = self._prompts[name]
        if not versions:
            return None

        if version:
            return next((p for p in versions if p.version == version), None)

        return versions[-1]  # latest

    def get_latest(self, name: str) -> Prompt | None:
        """Get the latest version of a prompt."""
        return self.get(name)

    def history(self, name: str) -> list[Prompt]:
        """Get full version history for a prompt."""
        return self._prompts.get(name, [])

    def list_prompts(self) -> list[str]:
        """List all prompt names."""
        return list(self._prompts.keys())

    def rollback(self, name: str, version: str) -> Prompt | None:
        """Rollback to a specific version (makes it the active version)."""
        target = self.get(name, version)
        if target:
            # Create a new version that's a copy of the target
            new_version = f"{version}-rollback"
            rolled = target.evolve(version=new_version)
            self.register(rolled)
            return rolled
        return None

    def export_json(self, filepath: str) -> None:
        """Export all prompts to JSON."""
        data = {}
        for name, versions in self._prompts.items():
            data[name] = [
                {
                    "version": p.version,
                    "template": p.template,
                    "variables": p.variables,
                    "metadata": p.metadata,
                    "token_estimate": p.token_estimate,
                }
                for p in versions
            ]
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
