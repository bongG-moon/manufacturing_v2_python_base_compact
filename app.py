from typing import Any, Dict, List

import pandas as pd
import streamlit as st

from core.agent import run_agent
from core.number_format import format_rows_for_display


st.set_page_config(page_title="Compact Manufacturing Chat", layout="wide")

def _empty_context() -> Dict[str, Any]:
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


def _format_display_dataframe(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    formatted_rows, _ = format_rows_for_display(rows)
    return pd.DataFrame(formatted_rows)


def _render_applied_params(applied_params: Dict[str, Any]) -> None:
    label_map = {
        "date": "날짜",
        "process_name": "공정",
        "product_name": "제품",
        "line_name": "라인",
        "mode": "MODE",
        "den": "DEN",
        "tech": "TECH",
        "lead": "LEAD",
        "mcp_no": "MCP",
        "group_by": "그룹 기준",
    }
    for key, value in applied_params.items():
        if value in (None, "", []):
            continue
        rendered = ", ".join(str(item) for item in value) if isinstance(value, list) else str(value)
        st.markdown(f"- **{label_map.get(key, key)}**: {rendered}")


def init_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_data" not in st.session_state:
        st.session_state.current_data = None
    if "context" not in st.session_state:
        st.session_state.context = _empty_context()


def render_context() -> None:
    context = st.session_state.get("context", {})
    active = []
    label_map = [
        ("date", "날짜"),
        ("process_name", "공정"),
        ("product_name", "제품"),
        ("line_name", "라인"),
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
        st.info("현재 조회 조건 | " + " / ".join(active))


def render_tool_results(tool_results: List[Dict[str, Any]]) -> None:
    for result in tool_results:
        if not result.get("success"):
            st.error(result.get("error_message", "오류가 발생했습니다."))
            continue

        title = f"{result.get('tool_name', 'result')} | {result.get('summary', '')}"
        with st.expander(title, expanded=True):
            data = result.get("data", [])
            if data:
                st.markdown("**분석 결과 테이블**")
                st.dataframe(_format_display_dataframe(data), width="stretch", hide_index=True)

            st.markdown("**이번 요청에 반영된 조건**")
            _render_applied_params(result.get("applied_params", {}))

            if result.get("tool_name") == "analyze_current_data":
                analysis_plan = result.get("analysis_plan", {})
                source_label = {
                    "llm": "LLM이 질의를 해석해 pandas 전처리 계획을 생성했습니다.",
                    "heuristic": "규칙 기반으로 pandas 전처리 계획을 생성했습니다.",
                }.get(str(result.get("analysis_logic", "")).lower(), "")

                st.markdown("**이번 분석 요약**")
                if source_label:
                    st.markdown(f"- **계획 생성 방식**: {source_label}")
                if analysis_plan.get("intent"):
                    st.markdown(f"- **분석 유형**: {analysis_plan.get('intent')}")
                if analysis_plan.get("operations"):
                    st.markdown(f"- **적용 작업**: {', '.join(analysis_plan.get('operations', []))}")
                if analysis_plan.get("group_by_columns"):
                    st.markdown(f"- **기준 컬럼**: {', '.join(analysis_plan.get('group_by_columns', []))}")
                if analysis_plan.get("metric_column"):
                    st.markdown(f"- **집계 지표**: {analysis_plan.get('metric_column')}")
                st.markdown(f"- **결과 행 수**: {len(data)}행")

                st.markdown("**생성된 pandas 코드**")
                st.code(result.get("generated_code", ""), language="python")


def sync_context(extracted_params: Dict[str, Any]) -> None:
    for field in ["date", "process_name", "product_name", "line_name", "mode", "den", "tech", "lead", "mcp_no"]:
        value = extracted_params.get(field)
        if value:
            st.session_state.context[field] = value


def main() -> None:
    init_session_state()
    st.title("제조 데이터 채팅 분석")
    st.caption("생산, 목표, 불량, 설비, WIP 조회 후 현재 결과를 이어서 분석할 수 있습니다.")
    render_context()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("tool_results"):
                render_tool_results(message["tool_results"])

    user_input = st.chat_input("예: 오늘 생산량 보여줘 / 그 결과를 MODE별로 상위 3개만 정리해줘")
    if not user_input:
        return

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    result = run_agent(
        user_input=user_input,
        chat_history=[{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages[:-1]],
        context=st.session_state.context,
        current_data=st.session_state.current_data,
    )

    response = result.get("response", "응답을 생성하지 못했습니다.")
    tool_results = result.get("tool_results", [])
    extracted_params = result.get("extracted_params", {})

    if tool_results:
        sync_context(extracted_params)

    with st.chat_message("assistant"):
        st.markdown(response)
        if tool_results:
            render_tool_results(tool_results)

    st.session_state.messages.append({"role": "assistant", "content": response, "tool_results": tool_results})
    st.session_state.current_data = result.get("current_data")


if __name__ == "__main__":
    main()
