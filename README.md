<div align="center">

<img src="assets/banner.svg" alt="PromptForge" width="700">

# 🔨 PromptForge

**Enterprise Prompt Engineering Toolkit — Version Control, A/B Testing, and Compression**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-35%20passed-brightgreen.svg)]()

*Manage, version, test, and optimize system prompts at scale. Built for teams shipping LLM-powered products where prompt quality directly impacts revenue.*

</div>

---

## The Problem

Your prompt started at 200 tokens and now it's **4,200 tokens** because:
- Everyone added "just one more instruction"
- Nobody knows which version performed best
- No A/B testing — changes go live on vibes
- Duplicate instructions bloat cost with zero value

## The Solution

```python
from promptforge import PromptRegistry, Prompt, ABTest

# Version-controlled prompts
registry = PromptRegistry("./prompts")

planner_v1 = Prompt(
    name="planner",
    version="1.0",
    template="You are a maintenance planner. Given {query}, create a plan.",
    variables=["query"],
    metadata={"tokens": 45, "author": "naveen"},
)

# Register and track
registry.register(planner_v1)
registry.register(planner_v1.evolve(
    version="1.1",
    template="You plan maintenance tasks. Query: {query}. Output JSON plan.",
    metadata={"tokens": 38, "change": "compressed + JSON output"},
))

# A/B test between versions
test = ABTest(
    name="planner_compression",
    variants={"control": "planner@1.0", "treatment": "planner@1.1"},
    metric="task_success_rate",
    min_samples=100,
)
```

## Features

| Feature | Description |
|---------|-------------|
| **Version Control** | Git-like prompt versioning with diff, rollback, and blame |
| **A/B Testing** | Statistical testing between prompt variants (chi-square, t-test) |
| **Compression** | Reduce prompt tokens by 30-60% without quality loss |
| **Template Engine** | Variables, conditionals, includes (Jinja2-like) |
| **Cost Scoring** | Automatic token counting and per-prompt cost estimation |
| **Diff View** | Side-by-side prompt comparison with token impact |
| **Prompt Linting** | Detect contradictions, redundancy, and vague instructions |
| **Export** | YAML/JSON prompt libraries for CI/CD integration |

## Quick Start

```bash
pip install promptforge
```

### Compression

```python
from promptforge import Compressor

compressor = Compressor()

original = """
You are a maintenance order analyst for SAP systems.
You help plant managers understand the status of their maintenance orders.
You should always be professional and concise in your responses.
When you don't know something, say "I don't have that information".
Never make up data or hallucinate facts about maintenance orders.
Always include the order number in your response.
Format your response using markdown tables when showing multiple items.
"""

compressed = compressor.compress(original)
print(compressed.text)
# "Maintenance order analyst for SAP. Help plant managers with order status.
#  Rules: concise, professional, no fabrication. Include order #. Use markdown tables."

print(compressed.stats)
# {"original_tokens": 89, "compressed_tokens": 34, "savings": "62%", "quality_score": 0.94}
```

### Prompt Linting

```python
from promptforge import Linter

linter = Linter()
issues = linter.check("""
You are helpful. Be concise.
Always provide detailed explanations.
Be brief in your responses.
""")
# [
#   LintIssue(severity="warning", message="Contradicting instructions: 'concise' vs 'detailed explanations'"),
#   LintIssue(severity="info", message="Redundant: 'concise' and 'brief' say the same thing"),
# ]
```

## Architecture

```
promptforge/
├── registry.py      # Version-controlled prompt store
├── prompt.py        # Prompt model with metadata
├── compressor.py    # Token reduction engine
├── linter.py        # Contradiction & redundancy detection
├── ab_test.py       # Statistical A/B testing
├── template.py      # Variable substitution engine
├── scoring.py       # Quality & cost scoring
└── exporters/       # YAML, JSON, Markdown export
```

## Documentation

- [Architecture & Design](docs/architecture.md)
- [Compression Algorithms](docs/compression.md)
- [A/B Testing Guide](docs/ab-testing.md)

## License

MIT
