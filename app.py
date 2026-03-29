import time

import streamlit as st

from core.agent import run_agent
from ui_renderer import (
    init_session_state,
    render_available_datasets,
    render_context,
    render_domain_registry,
    render_sub_agent_blueprint,
    render_tool_results,
    sync_context,
)


st.set_page_config(page_title="Compact Manufacturing Chat", layout="wide")


def _get_saved_chat_history():
    return [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]


def _render_saved_chat_history() -> None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("tool_results"):
                render_tool_results(message["tool_results"])


def _build_failure_result(message: str):
    return {
        "response": message,
        "tool_results": [],
        "current_data": st.session_state.current_data,
        "extracted_params": {},
    }


def _run_chat_turn(user_input: str):
    started_at = time.perf_counter()
    try:
        result = run_agent(
            user_input=user_input,
            chat_history=_get_saved_chat_history(),
            context=st.session_state.context,
            current_data=st.session_state.current_data,
        )
    except Exception as exc:
        result = _build_failure_result(
            "The agent could not complete this turn. Please retry after checking the LLM/API configuration."
        )
        result["error_detail"] = str(exc)
    result["latency_seconds"] = round(time.perf_counter() - started_at, 3)

    tool_results = result.get("tool_results", [])
    extracted_params = result.get("extracted_params", {})
    if tool_results:
        sync_context(extracted_params)

    st.session_state.current_data = result.get("current_data")
    return result


def main() -> None:
    init_session_state()

    st.title("Compact Manufacturing Chat")
    st.caption("Manufacturing retrieval plus follow-up dataframe analysis for production, quality, WIP, equipment, and lot workflows.")

    col_left, col_right = st.columns([5, 2])
    with col_left:
        render_context()
    with col_right:
        st.session_state.detail_mode = st.toggle(
            "Engineer detail mode",
            value=bool(st.session_state.get("detail_mode", False)),
            help="Show analysis code and open result panels by default.",
        )

    render_available_datasets()
    render_domain_registry()
    render_sub_agent_blueprint()
    _render_saved_chat_history()

    user_input = st.chat_input(
        "Examples: Show today's production / Compare the current result by MODE top 3 / Summarize hold lots by process"
    )
    if not user_input:
        return

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    result = _run_chat_turn(user_input)
    response = result.get("response", "No response was generated.")
    tool_results = result.get("tool_results", [])

    with st.chat_message("assistant"):
        st.markdown(response)
        if result.get("error_detail") and st.session_state.get("detail_mode"):
            st.caption(f"Error detail: {result['error_detail']}")
        if st.session_state.get("detail_mode"):
            st.caption(f"Latency: {result.get('latency_seconds', 0)}s")
        if tool_results:
            render_tool_results(tool_results)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
            "tool_results": tool_results,
        }
    )


if __name__ == "__main__":
    main()
