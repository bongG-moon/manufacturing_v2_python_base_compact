# Sub-Agent Blueprint

This document captures the recommended product sub-agents for the compact manufacturing service itself.

## Why sub-agents now

The current service is already useful for:

- retrieval of manufacturing datasets
- follow-up dataframe analysis on the current result
- conversational context carry-over

The next bottlenecks are no longer only "can it answer at all" but also:

- can it route user intent safely
- can it compare multiple datasets without semantic mistakes
- can it help engineers diagnose yield and defect issues
- can it support dispatch and recovery decisions
- can it protect the service from silent regressions

## Recommended product sub-agents

### 1. Intent & Context Guard Agent

- Priority: `P0`
- Goal: decide whether a user turn is a fresh retrieval, a follow-up transform, or a multi-dataset comparison
- Main ownership:
  - `core/agent.py`
  - `core/parameter_resolver.py`
  - context inheritance policy
- Expected outputs:
  - query mode
  - inherited filter plan
  - conflict flags
  - confidence score

### 2. Semantic Join Planner Agent

- Priority: `P0`
- Goal: validate dataset grain before multi-dataset KPI analysis
- Main ownership:
  - `core/data_tools.py`
  - `core/agent.py`
  - `core/data_analysis_engine.py`
- Expected outputs:
  - join keys
  - pre-aggregation requirement
  - join strategy
  - semantic warnings

### 3. Yield & Defect RCA Agent

- Priority: `P1`
- Goal: explain why a yield or defect issue happened, not only what happened
- Main ownership:
  - yield, defect, hold, lot trace, equipment, recipe datasets
- Expected outputs:
  - ranked suspected drivers
  - supporting drill-downs
  - next checks for engineers

### 4. WIP & Dispatch Optimization Agent

- Priority: `P1`
- Goal: recommend what should move next to protect throughput and target attainment
- Main ownership:
  - WIP, hold, target, equipment datasets
- Expected outputs:
  - dispatch priority
  - bottleneck view
  - recovery what-if scenarios

### 5. Quality Regression Guard Agent

- Priority: `P1`
- Goal: prevent regressions in routing, parameter extraction, join safety, and generated analysis plans
- Main ownership:
  - `tests/`
  - `core/safe_code_executor.py`
  - benchmark scenarios
- Expected outputs:
  - pass or fail summary
  - regression diff
  - high-risk prompts

## Suggested rollout order

1. Implement `Intent & Context Guard Agent`
2. Implement `Semantic Join Planner Agent`
3. Add `Quality Regression Guard Agent`
4. Add `Yield & Defect RCA Agent`
5. Add `WIP & Dispatch Optimization Agent`

## Minimum integration pattern

Each product sub-agent should expose:

- a narrow mission
- explicit inputs
- explicit outputs
- a confidence or warning channel
- deterministic fallbacks where possible

This keeps the current app compact while making future multi-agent orchestration much easier.
