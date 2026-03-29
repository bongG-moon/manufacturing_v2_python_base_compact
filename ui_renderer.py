from typing import Any, Dict, List

import pandas as pd
import streamlit as st

from core.dataset_contracts import list_dataset_contracts
from core.domain_registry import get_domain_registry_summary
from core.number_format import format_rows_for_display
from core.sub_agents import build_sub_agent_cards, get_system_analysis_snapshot


def empty_context() -> Dict[str, Any]:
    return {
        "date": None,
        "process_name": None,
        "product_name": None,
        "line_name": None,
        "mode": None,
        "den": None,
        "tech": None,
        "lead": None,
        "mcp_no": None,
    }


def init_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_data" not in st.session_state:
        st.session_state.current_data = None
    if "context" not in st.session_state:
        st.session_state.context = empty_context()
    if "detail_mode" not in st.session_state:
        st.session_state.detail_mode = False


def format_display_dataframe(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    formatted_rows, _ = format_rows_for_display(rows)
    return pd.DataFrame(formatted_rows)


def dataframe_to_csv_bytes(rows: List[Dict[str, Any]]) -> bytes:
    return format_display_dataframe(rows).to_csv(index=False).encode("utf-8-sig")


def render_applied_params(applied_params: Dict[str, Any]) -> None:
    label_map = {
        "date": "Date",
        "process_name": "Process",
        "product_name": "Product",
        "line_name": "Line",
        "mode": "MODE",
        "den": "DEN",
        "tech": "TECH",
        "lead": "LEAD",
        "mcp_no": "MCP",
    }
    for key, value in applied_params.items():
        if value in (None, "", []):
            continue
        rendered = ", ".join(str(item) for item in value) if isinstance(value, list) else str(value)
        st.markdown(f"- **{label_map.get(key, key)}**: {rendered}")


def render_context() -> None:
    context = st.session_state.get("context", {})
    active = []
    label_map = [
        ("date", "Date"),
        ("process_name", "Process"),
        ("product_name", "Product"),
        ("line_name", "Line"),
        ("mode", "MODE"),
        ("den", "DEN"),
        ("tech", "TECH"),
        ("lead", "LEAD"),
        ("mcp_no", "MCP"),
    ]
    for field, label in label_map:
        value = context.get(field)
        if value:
            rendered = ", ".join(str(item) for item in value) if isinstance(value, list) else str(value)
            active.append(f"{label}: {rendered}")
    if active:
        st.info("Active query context | " + " / ".join(active))


def render_available_datasets() -> None:
    with st.expander("Available Datasets", expanded=False):
        for contract in list_dataset_contracts():
            required = ", ".join(contract.required_params) if contract.required_params else "none"
            st.markdown(f"- **{contract.label}**: {contract.description} | required: `{required}`")


def render_domain_registry() -> None:
    summary = get_domain_registry_summary()
    with st.expander("Domain Registry", expanded=False):
        st.markdown("**How to add domain terms without coding**")
        st.markdown(
            "1. Create a new Markdown file under `reference_materials/domain_registry/`\n"
            "2. Fill in one or more tables for dataset keywords, process groups, or value groups\n"
            "3. Refresh the app and check this panel for loaded files and warnings"
        )
        st.code(
            "# Example\n"
            "## Dataset Keywords\n"
            "| dataset_key | label | keywords | description |\n"
            "|---|---|---|---|\n"
            "| production | 생산 | 생산, 생산량, 일일 생산 | 생산 실적 조회 |\n\n"
            "## Process Groups\n"
            "| group | synonyms | values |\n"
            "|---|---|---|\n"
            "| DIE_ATTACH | die attach, da, 다이 어태치 | epoxy_dispense, die_place, post_cure |\n\n"
            "## Value Groups\n"
            "| field | canonical | synonyms | values |\n"
            "|---|---|---|---|\n"
            "| tech | WB | wb, wire bond | WB |",
            language="markdown",
        )

        loaded_files = summary.get("loaded_files", [])
        if loaded_files:
            st.markdown("**Loaded files**")
            for name in loaded_files:
                st.markdown(f"- {name}")
        else:
            st.caption("No custom domain files loaded. Using built-in defaults.")

        warnings = summary.get("warnings", [])
        if warnings:
            st.markdown("**Registry warnings**")
            for warning in warnings:
                st.warning(str(warning))

        st.markdown("**Dataset keywords**")
        dataset_rows = []
        for dataset_key, meta in summary.get("dataset_keywords", {}).items():
            dataset_rows.append(
                {
                    "dataset_key": dataset_key,
                    "label": meta.get("label", ""),
                    "keywords": ", ".join(meta.get("keywords", [])),
                }
            )
        if dataset_rows:
            st.dataframe(pd.DataFrame(dataset_rows), width="stretch", hide_index=True)

        st.markdown("**Process groups**")
        process_rows = []
        for group, meta in summary.get("process_groups", {}).items():
            process_rows.append(
                {
                    "group": group,
                    "synonyms": ", ".join(meta.get("synonyms", [])),
                    "values": ", ".join(meta.get("values", [])),
                }
            )
        if process_rows:
            st.dataframe(pd.DataFrame(process_rows), width="stretch", hide_index=True)


def render_sub_agent_blueprint() -> None:
    snapshot = get_system_analysis_snapshot()
    cards = build_sub_agent_cards()

    with st.expander("Recommended Sub Agents", expanded=False):
        st.markdown("**Current service assessment**")
        st.markdown("**Strengths**")
        for item in snapshot.get("strengths", []):
            st.markdown(f"- {item}")

        st.markdown("**Current risks**")
        for item in snapshot.get("risks", []):
            st.markdown(f"- {item}")

        st.markdown("**Recommended implementation order**")
        for item in snapshot.get("next_steps", []):
            st.markdown(f"- {item}")

        st.markdown("**Sub-agent catalog**")
        for card in cards:
            st.markdown(f"### {card['priority']} | {card['name']}")
            st.markdown(str(card["mission"]))
            st.markdown(f"- Why now: {card['why_now']}")
            st.markdown(f"- Inputs: {', '.join(card.get('primary_inputs', []))}")
            st.markdown(f"- Outputs: {', '.join(card.get('outputs', []))}")
            st.markdown(f"- Ownership: {', '.join(card.get('owned_modules', []))}")


def render_analysis_summary(result: Dict[str, Any], row_count: int) -> None:
    analysis_plan = result.get("analysis_plan", {})
    transformation_summary = result.get("transformation_summary", {})
    source_label = {
        "llm_primary": "Primary LLM-generated pandas plan.",
        "llm_retry": "Retry LLM-generated pandas plan after execution failure.",
        "minimal_fallback": "Minimal deterministic fallback plan.",
    }.get(str(result.get("analysis_logic", "")).lower(), "")

    st.markdown("**Analysis summary**")
    if source_label:
        st.markdown(f"- **Plan source**: {source_label}")
    if analysis_plan.get("intent"):
        st.markdown(f"- **Intent**: {analysis_plan.get('intent')}")
    if transformation_summary.get("group_by_columns"):
        st.markdown(f"- **Group by**: {', '.join(transformation_summary.get('group_by_columns', []))}")
    if transformation_summary.get("metric_column"):
        st.markdown(f"- **Metric**: {transformation_summary.get('metric_column')}")
    if transformation_summary.get("sort_by"):
        st.markdown(
            f"- **Sort**: {transformation_summary.get('sort_by')} ({transformation_summary.get('sort_order', 'desc')})"
        )
    if transformation_summary.get("top_n"):
        st.markdown(f"- **Top N**: {transformation_summary.get('top_n')}")
    if transformation_summary.get("top_n_per_group"):
        st.markdown(f"- **Top N per group**: {transformation_summary.get('top_n_per_group')}")
    if transformation_summary.get("input_row_count") is not None:
        st.markdown(
            f"- **Rows**: {transformation_summary.get('input_row_count')} -> "
            f"{transformation_summary.get('output_row_count', row_count)}"
        )
    st.markdown(f"- **Result rows**: {row_count}")


def render_table_artifact(title: str, artifact: Dict[str, Any], key_prefix: str, expanded: bool = False) -> None:
    rows = artifact.get("data", [])
    if not isinstance(rows, list) or not rows:
        return

    with st.expander(title, expanded=expanded):
        if artifact.get("summary"):
            st.caption(str(artifact["summary"]))
        st.markdown(f"- **Rows**: {artifact.get('row_count', len(rows))}")
        columns = artifact.get("columns", [])
        if columns:
            st.markdown(f"- **Columns**: {', '.join(str(column) for column in columns)}")
        st.dataframe(format_display_dataframe(rows), width="stretch", hide_index=True)
        st.download_button(
            label=f"Download {title} CSV",
            data=dataframe_to_csv_bytes(rows),
            file_name=f"{key_prefix}.csv",
            mime="text/csv",
            key=f"download-{key_prefix}",
        )


def render_tool_results(tool_results: List[Dict[str, Any]]) -> None:
    expanded = bool(st.session_state.get("detail_mode", False))

    for index, result in enumerate(tool_results):
        if not result.get("success"):
            st.error(result.get("error_message", "An error occurred."))
            continue

        title = f"{result.get('tool_name', 'result')} | {result.get('summary', '')}"
        with st.expander(title, expanded=expanded):
            data = result.get("data", [])
            if data:
                st.markdown("**Result table**")
                st.dataframe(format_display_dataframe(data), width="stretch", hide_index=True)
                st.download_button(
                    label="Download result CSV",
                    data=dataframe_to_csv_bytes(data),
                    file_name=f"result_{index}.csv",
                    mime="text/csv",
                    key=f"download-result-{index}",
                )

            st.markdown("**Applied parameters**")
            render_applied_params(result.get("applied_params", {}))

            if result.get("source_tables"):
                st.markdown("**Source tables used**")
                for artifact_index, artifact in enumerate(result.get("source_tables", [])):
                    render_table_artifact(
                        str(artifact.get("label", f"source_{artifact_index + 1}")),
                        artifact,
                        f"source-{index}-{artifact_index}",
                    )

            analysis_base_table = result.get("analysis_base_table")
            if isinstance(analysis_base_table, dict):
                st.markdown("**Joined table used for analysis**")
                analysis_base_info = result.get("analysis_base_info", {})
                join_columns = analysis_base_info.get("join_columns", [])
                if join_columns:
                    st.caption("Join keys: " + ", ".join(str(column) for column in join_columns))
                render_table_artifact("Analysis Base Table", analysis_base_table, f"analysis-base-{index}")

            if result.get("tool_name") == "analyze_current_data":
                render_analysis_summary(result, len(data))
                if expanded:
                    st.markdown("**Generated pandas code**")
                    st.code(result.get("generated_code", ""), language="python")


def sync_context(extracted_params: Dict[str, Any]) -> None:
    for field in ["date", "process_name", "product_name", "line_name", "mode", "den", "tech", "lead", "mcp_no"]:
        value = extracted_params.get(field)
        if value:
            st.session_state.context[field] = value
