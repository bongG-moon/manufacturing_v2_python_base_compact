from dataclasses import asdict, dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class SubAgentSpec:
    key: str
    name: str
    priority: str
    mission: str
    why_now: str
    primary_inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    owned_modules: List[str] = field(default_factory=list)
    sample_prompts: List[str] = field(default_factory=list)


def get_system_analysis_snapshot() -> Dict[str, List[str]]:
    return {
        "strengths": [
            "Clear retrieval -> follow-up analysis split for conversational manufacturing workflows.",
            "Broad mock datasets covering production, target, defect, equipment, WIP, yield, hold, scrap, recipe, and lot trace.",
            "Session-scoped current_data and context make follow-up questions natural for operators and engineers.",
        ],
        "risks": [
            "Intent routing relies on keyword heuristics, so mixed questions can be misclassified.",
            "current_data stores multiple shapes of payload, which weakens contracts and raises regression risk.",
            "Multi-dataset analysis currently depends on simple shared-column joins without grain validation.",
            "LLM-driven parameter extraction and dataframe code generation need stronger deterministic guardrails.",
            "Several Korean strings appear mojibake in terminal output, indicating encoding hygiene issues.",
        ],
        "next_steps": [
            "Add specialist sub-agents around intent guardrails, semantic joins, RCA, dispatch optimization, and regression checks.",
            "Promote current_data/current_datasets into typed payload contracts before scaling more workflows.",
            "Add deterministic tests for routing, column validation, merge semantics, and safe code execution.",
        ],
    }


def get_recommended_sub_agents() -> List[SubAgentSpec]:
    return [
        SubAgentSpec(
            key="intent_context_guard",
            name="Intent & Context Guard Agent",
            priority="P0",
            mission="Classify each user turn into retrieval, follow-up transform, or multi-dataset analysis and manage context inheritance safely.",
            why_now="Routing accuracy is the control tower for the rest of the system. If intent is wrong, good datasets and good analysis code still produce the wrong answer.",
            primary_inputs=[
                "user_input",
                "recent chat history",
                "session context",
                "current_data metadata",
            ],
            outputs=[
                "query_mode decision",
                "context carry-over plan",
                "conflict flags",
                "confidence score",
            ],
            owned_modules=[
                "core/agent.py",
                "core/parameter_resolver.py",
                "core/filter_utils.py",
            ],
            sample_prompts=[
                "Decide whether this turn should retrieve fresh manufacturing data or transform the current table only.",
                "Check whether inherited date, process, or product filters should be kept, reset, or confirmed.",
            ],
        ),
        SubAgentSpec(
            key="semantic_join_planner",
            name="Semantic Join Planner Agent",
            priority="P0",
            mission="Validate dataset grain and choose safe join or pre-aggregation plans before cross-dataset KPI analysis runs.",
            why_now="Production vs target vs yield style comparisons become misleading when joins happen at incompatible levels such as process, line, lot, or equipment grain.",
            primary_inputs=[
                "selected dataset keys",
                "dataset column profiles",
                "join candidate columns",
                "user comparison intent",
            ],
            outputs=[
                "recommended join keys",
                "required pre-aggregation steps",
                "join strategy",
                "semantic warnings",
            ],
            owned_modules=[
                "core/agent.py",
                "core/data_tools.py",
                "core/data_analysis_engine.py",
            ],
            sample_prompts=[
                "Before merging production and target, verify the common grain and tell me whether aggregation is required first.",
                "Explain whether an outer join is safe for this question or whether line-level rollup should happen first.",
            ],
        ),
        SubAgentSpec(
            key="yield_defect_rca",
            name="Yield & Defect RCA Agent",
            priority="P1",
            mission="Drill down abnormal yield or defect patterns across process, product, line, equipment, and lot axes and propose likely causes with next checks.",
            why_now="The current service explains what happened, but manufacturing teams also need help with why it happened and what to inspect next.",
            primary_inputs=[
                "yield and defect datasets",
                "hold and lot trace context",
                "equipment status",
                "recipe conditions",
            ],
            outputs=[
                "ranked suspected drivers",
                "supporting slices and comparisons",
                "recommended validation checks",
                "operator-friendly summary",
            ],
            owned_modules=[
                "core/data_tools.py",
                "core/domain_knowledge.py",
                "core/data_analysis_engine.py",
            ],
            sample_prompts=[
                "Find which process family and product combination explains the yield drop most strongly and show the likely fail bin.",
                "Compare the abnormal group against a stable baseline and suggest the first three manufacturing checks.",
            ],
        ),
        SubAgentSpec(
            key="wip_dispatch_optimizer",
            name="WIP & Dispatch Optimization Agent",
            priority="P1",
            mission="Turn WIP, hold, target, and equipment signals into recommended dispatch priorities and recovery scenarios for daily operations.",
            why_now="This is the fastest path from a reporting chatbot to an operations assistant that helps line leaders decide what to run next.",
            primary_inputs=[
                "WIP status",
                "hold lots",
                "target data",
                "equipment utilization and downtime",
            ],
            outputs=[
                "priority queue by line or process",
                "recovery what-if scenarios",
                "throughput risk notes",
                "bottleneck summary",
            ],
            owned_modules=[
                "core/data_tools.py",
                "core/domain_knowledge.py",
            ],
            sample_prompts=[
                "Recommend the next dispatch order to reduce hold risk while protecting today's target.",
                "If one line recovers in two hours, estimate which WIP pockets should move first.",
            ],
        ),
        SubAgentSpec(
            key="quality_regression_guard",
            name="Quality Regression Guard Agent",
            priority="P1",
            mission="Run deterministic checks on routing, parameter extraction, join safety, and generated analysis plans to prevent silent regressions.",
            why_now="The service already depends on multiple LLM-assisted steps, so a lightweight automated guard is essential before adoption spreads inside the factory.",
            primary_inputs=[
                "representative question suite",
                "tool outputs",
                "analysis plans",
                "safe executor results",
            ],
            outputs=[
                "pass or fail summary",
                "regression diff by scenario",
                "high-risk prompts",
                "recommended fixes",
            ],
            owned_modules=[
                "core/agent.py",
                "core/analysis_llm.py",
                "core/safe_code_executor.py",
            ],
            sample_prompts=[
                "Validate that these benchmark questions still route to the correct retrieval tools and required filters.",
                "Detect when the generated pandas plan uses the wrong metric or misses a requested dimension.",
            ],
        ),
    ]


def build_sub_agent_cards() -> List[Dict[str, object]]:
    return [asdict(spec) for spec in get_recommended_sub_agents()]
