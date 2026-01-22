# Phase 4: Aggregation & Publishing

> Multi-Agent Debate System với Quality Gate Scoring

## Overview

Phase 4 biến JSON data từ các phases trước thành System Design Documents chuyên nghiệp.

## Architecture

```
Phase 3 Data → Multi-Agent Debate → Quality Gate → Export SDD
                  ↓                     ↓
            White/Black/Green      Pydantic Check
            Hat Review             (depth ≥8, cases ≥5)
```

## Usage

```bash
# CLI
python src/main.py --mode phase4 "Hệ thống đăng nhập"

# Python API
from src.aggregation import export_sdd, DebateOrchestrator, DebateConfig
from src.agents import create_white_hat_agent, create_black_hat_agent

orchestrator = DebateOrchestrator(DebateConfig())
orchestrator.register_agent("white", create_white_hat_agent())
orchestrator.register_agent("black", create_black_hat_agent())

result = export_sdd(data, template, output_path="./output")
```

## Quality Gate Thresholds

Theo PRODUCT_VISION.md:
- depth_score: ≥ 8.0/10
- edge_case_coverage: ≥ 5 scenarios
- technical_feasibility: 100%
- logic_consistency: 0 contradictions
- no_ai_speak: 0 instances

## File Structure

```
src/
├── quality/
│   └── gate.py              # Quality Gate scoring
├── agents/
│   └── multi_agent_roles.py # White/Black/Green/Editor agents
├── templates/
│   └── sdd_template.py       # Master template
└── aggregation/
    ├── debate_orchestrator.py # Multi-agent debate
    └── export.py              # Export with QG enforcement
```
