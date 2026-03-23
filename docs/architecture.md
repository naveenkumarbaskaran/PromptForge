# PromptForge Architecture

## Compression Pipeline

```mermaid
flowchart LR
    A[Raw Prompt\n~4200 tokens] --> B[Filler Removal]
    B --> C[Deduplication]
    C --> D[Imperative Conversion]
    D --> E[Merge Related]
    E --> F[Compressed\n~1600 tokens]

    B -->|"-30%"| B2["Remove: 'you should always',\n'make sure to', 'remember to'"]
    C -->|"-15%"| C2["Merge: 'be concise' + 'be brief'\n→ single instruction"]
    D -->|"-10%"| D2["'You should format using tables'\n→ 'Use tables'"]
    E -->|"-7%"| E2["Combine adjacent\nrelated sentences"]
```

## Version Control Flow

```mermaid
sequenceDiagram
    participant Dev
    participant Registry
    participant ABTest
    participant Production

    Dev->>Registry: register(planner@1.0)
    Dev->>Registry: register(planner@1.1, evolved)
    
    Dev->>ABTest: create test (1.0 vs 1.1)
    
    loop Until significant
        Production->>ABTest: pick_variant()
        ABTest-->>Production: "control" or "treatment"
        Production->>ABTest: record(variant, success)
    end
    
    ABTest-->>Dev: winner = "1.1" (p < 0.05)
    Dev->>Registry: promote 1.1 to active
    Dev->>Registry: archive 1.0
```

## Linting Decision Tree

```mermaid
flowchart TD
    INPUT[Prompt Text] --> L1{Contains\ncontradictions?}
    L1 -->|Yes| W1[⚠️ Warning: Contradicting instructions]
    L1 -->|No| L2{Has\nredundancies?}
    
    L2 -->|Yes| I1[ℹ️ Info: Redundant phrases]
    L2 -->|No| L3{Vague\nlanguage?}
    
    L3 -->|Yes| I2[ℹ️ Info: Use imperative form]
    L3 -->|No| L4{Too long?\n>500 tokens}
    
    L4 -->|Yes| W2[⚠️ Warning: Consider compression]
    L4 -->|No| L5{Has role\ndefinition?}
    
    L5 -->|No| I3[ℹ️ Info: Add role definition]
    L5 -->|Yes| OK[✅ Clean prompt]

    style W1 fill:#ffd93d,color:#333
    style W2 fill:#ffd93d,color:#333
    style OK fill:#6bcb77,color:#fff
```

## Cost Impact

```mermaid
xychart-beta
    title "Token Cost Before vs After PromptForge Optimization"
    x-axis ["System Prompt", "Tool Schemas", "History", "User Query", "Total"]
    y-axis "Tokens" 0 --> 8000
    bar [4200, 3000, 2500, 200, 9900]
    bar [1600, 3000, 1500, 200, 6300]
```

| Component | Before | After | Savings |
|-----------|--------|-------|---------|
| System Prompt | 4,200 | 1,600 | **62%** |
| History (windowed) | 2,500 | 1,500 | **40%** |
| Tool Schemas | 3,000 | 3,000 | 0% |
| **Total per request** | **9,900** | **6,300** | **36%** |
| **Monthly cost (10K req)** | **$247** | **$157** | **$90 saved** |
