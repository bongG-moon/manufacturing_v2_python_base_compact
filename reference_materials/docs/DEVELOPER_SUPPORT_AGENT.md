# Developer Support Agent

This is not a product agent inside the manufacturing service.

It is a development helper role for implementation work on this repository.

## Python Beginner Support Agent

- Purpose: help keep the code understandable for maintainers who are not comfortable with Python yet
- Scope:
  - simplify control flow
  - prefer explicit names over clever shorthand
  - add short comments that explain why a step exists
  - update docs when new modules or data concepts are added
  - flag code that would be hard for a beginner to debug safely

## When to use it

Use this helper whenever we:

- refactor `core/agent.py`
- change parameter extraction or routing logic
- add a new dataset tool
- add a new product sub-agent
- rewrite UI or operator-facing behavior

## Practical rules

- Keep functions small and single-purpose.
- Make entry flow easy to trace: `app.py -> core.agent -> data tool / analysis engine`.
- Avoid hidden side effects.
- Prefer beginner-readable conditionals over compressed logic.
- Write docs as if the next maintainer is seeing Python code for the first time.
