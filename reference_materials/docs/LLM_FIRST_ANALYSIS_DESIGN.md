# LLM-First Follow-up Analysis Design

## Goal

Turn follow-up analysis into:

1. `current_data` is available
2. LLM writes pandas code directly for the user request
3. schema checks and safe execution validate that code
4. if execution fails, retry once with the runtime error
5. only use a minimal fallback for very basic sorting/top-N cases

The main point is to avoid hard-coded analysis templates for cases such as:

- group by
- multi-column group by
- top N per group
- derived columns
- custom filtering and sorting

## Previous structure

The old flow was hybrid:

- LLM generated a plan
- internal template code often rebuilt the pandas logic
- fallback logic handled many structured cases directly

That made the system more stable, but less flexible for unexpected follow-up requests.

## New structure

### 1. LLM code is the primary execution path

The prompt now tells the model:

- do not invent columns
- write pandas directly against `df`
- assign final output to `result`
- handle grouping, ranking, filtering, sorting, and top-N-per-group directly in code

### 2. Schema preflight still runs before execution

We still check:

- requested dimensions mentioned by the user
- columns referenced by the generated plan

If a requested column is not present in the current table, the service returns a clear user-facing message instead of a generic failure.

### 3. Safe execution is stricter

The executor now:

- blocks unsafe syntax and names
- requires a real `result = ...` assignment
- returns structured execution errors

### 4. One retry on failure

If the first LLM-generated code fails at runtime, we send:

- the original question
- the dataset profile
- the runtime error
- the previous code

back to the LLM and ask for corrected code.

### 5. Minimal fallback only

If LLM generation completely fails, the system uses only a minimal fallback:

- choose a metric column
- sort
- head(N)

This fallback is intentionally small so the analysis behavior stays mostly LLM-driven.

## Why this is better

- More flexible for unplanned question patterns
- Better fit for evolving follow-up requests
- Less need to keep adding special-case logic
- Still safe enough because schema checks and AST validation remain in place

## Tradeoff

This design depends more on LLM quality than before.

That means:

- more flexibility
- slightly less deterministic behavior

To balance that, we keep:

- missing-column detection
- safe AST validation
- one retry loop
- transformation summary for debugging
