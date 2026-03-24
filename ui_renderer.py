from typing import Any, Dict, List

import pandas as pd
import streamlit as st

from core.number_format import format_rows_for_display


def empty_context() -> Dict[str, Any]:
    # context는 "다음 질문으로 넘길 핵심 조건 저장소"입니다.
    # current_data가 실제 표 데이터라면, context는 날짜/공정/제품 같은 요약 정보만 저장합니다.
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
    # Streamlit은 이벤트마다 스크립트를 다시 실행하므로
    # 세션 상태가 없으면 매번 새 대화처럼 동작하게 됩니다.
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_data" not in st.session_state:
        st.session_state.current_data = None
    if "context" not in st.session_state:
        st.session_state.context = empty_context()


def format_display_dataframe(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    # 계산은 원본 숫자로 하고,
    # 화면에 보여줄 때만 K/M 단위 포맷을 적용합니다.
    formatted_rows, _ = format_rows_for_display(rows)
    return pd.DataFrame(formatted_rows)


def render_applied_params(applied_params: Dict[str, Any]) -> None:
    # 내부 파라미터 이름은 개발자용이므로
    # 사용자 화면에서는 읽기 쉬운 라벨로 바꿔 보여줍니다.
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


def render_context() -> None:
    # 현재 이어지고 있는 조건을 항상 위에 보여주면
    # 후속 질문이 왜 그렇게 해석되는지 사용자가 이해하기 쉽습니다.
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


def render_analysis_summary(result: Dict[str, Any], row_count: int) -> None:
    # 후속 분석에서는 코드만 보여주는 것보다
    # 어떤 기준으로 그룹화/정렬되었는지 요약이 더 중요합니다.
    analysis_plan = result.get("analysis_plan", {})
    transformation_summary = result.get("transformation_summary", {})
    source_label = {
        "llm_primary": "LLM이 직접 pandas 코드를 생성했습니다.",
        "llm_retry": "LLM이 실행 오류를 보고 pandas 코드를 다시 생성했습니다.",
        "minimal_fallback": "LLM 실패 후 최소 fallback 로직을 사용했습니다.",
    }.get(str(result.get("analysis_logic", "")).lower(), "")

    st.markdown("**이번 분석 요약**")
    if source_label:
        st.markdown(f"- **계획 생성 방식**: {source_label}")
    if analysis_plan.get("intent"):
        st.markdown(f"- **분석 유형**: {analysis_plan.get('intent')}")
    if transformation_summary.get("group_by_columns"):
        st.markdown(f"- **그룹 기준**: {', '.join(transformation_summary.get('group_by_columns', []))}")
    if transformation_summary.get("metric_column"):
        st.markdown(f"- **기준 지표**: {transformation_summary.get('metric_column')}")
    if transformation_summary.get("sort_by"):
        st.markdown(f"- **정렬**: {transformation_summary.get('sort_by')} ({transformation_summary.get('sort_order', 'desc')})")
    if transformation_summary.get("top_n"):
        st.markdown(f"- **상위 N**: {transformation_summary.get('top_n')}")
    if transformation_summary.get("top_n_per_group"):
        st.markdown(f"- **그룹별 상위 N**: {transformation_summary.get('top_n_per_group')}")
    if transformation_summary.get("input_row_count") is not None:
        st.markdown(
            f"- **행 변화**: {transformation_summary.get('input_row_count')}행 -> {transformation_summary.get('output_row_count', row_count)}행"
        )
    st.markdown(f"- **결과 행 수**: {row_count}행")


def render_tool_results(tool_results: List[Dict[str, Any]]) -> None:
    # 조회 결과와 후속 분석 결과를 같은 형태로 렌더링하면
    # 사용자 입장에서 화면이 더 일관되게 느껴집니다.
    for result in tool_results:
        if not result.get("success"):
            st.error(result.get("error_message", "오류가 발생했습니다."))
            continue

        title = f"{result.get('tool_name', 'result')} | {result.get('summary', '')}"
        with st.expander(title, expanded=True):
            data = result.get("data", [])
            if data:
                st.markdown("**분석 결과 테이블**")
                st.dataframe(format_display_dataframe(data), width="stretch", hide_index=True)

            st.markdown("**이번 요청에 반영된 조건**")
            render_applied_params(result.get("applied_params", {}))

            if result.get("tool_name") == "analyze_current_data":
                # 후속 분석일 때만 "왜 이런 표가 나왔는지"를 추가로 설명합니다.
                render_analysis_summary(result, len(data))
                st.markdown("**생성된 pandas 코드**")
                st.code(result.get("generated_code", ""), language="python")


def sync_context(extracted_params: Dict[str, Any]) -> None:
    # 빈 값으로 기존 context를 덮어쓰지 않기 위해
    # 값이 있을 때만 세션에 저장합니다.
    for field in ["date", "process_name", "product_name", "line_name", "mode", "den", "tech", "lead", "mcp_no"]:
        value = extracted_params.get(field)
        if value:
            st.session_state.context[field] = value
