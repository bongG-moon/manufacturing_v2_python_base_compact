import streamlit as st

from core.agent import run_agent
from ui_helpers import init_session_state, render_context, render_tool_results, sync_context


st.set_page_config(page_title="Compact Manufacturing Chat", layout="wide")


def _build_chat_history():
    # The agent only needs role/content pairs, so we strip UI-only fields here.
    return [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]


def _render_chat_history() -> None:
    # Re-render previous turns on every Streamlit rerun.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("tool_results"):
                render_tool_results(message["tool_results"])


def _run_turn(user_input: str):
    # This is the single place where the UI calls the backend agent.
    result = run_agent(
        user_input=user_input,
        chat_history=_build_chat_history(),
        context=st.session_state.context,
        current_data=st.session_state.current_data,
    )

    tool_results = result.get("tool_results", [])
    extracted_params = result.get("extracted_params", {})
    if tool_results:
        # Save resolved filters so the next question can inherit them.
        sync_context(extracted_params)

    # Save the latest dataset or transformed view for follow-up questions.
    st.session_state.current_data = result.get("current_data")
    return result


def main() -> None:
    init_session_state()

    st.title("제조 데이터 채팅 분석")
    st.caption("생산, 목표, 불량, 설비, WIP 조회와 현재 결과 기반 후속 분석을 지원합니다.")
    render_context()
    _render_chat_history()

    user_input = st.chat_input("예: 오늘 생산량 보여줘 / 그 결과를 MODE별로 상위 3개만 정리해줘")
    if not user_input:
        return

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    result = _run_turn(user_input)
    response = result.get("response", "응답을 생성하지 못했습니다.")
    tool_results = result.get("tool_results", [])

    with st.chat_message("assistant"):
        st.markdown(response)
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
