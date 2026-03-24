import streamlit as st

from core.agent import run_agent
from ui_renderer import init_session_state, render_context, render_tool_results, sync_context


st.set_page_config(page_title="Compact Manufacturing Chat", layout="wide")


def _get_saved_chat_history():
    # 세션에는 UI용 정보도 같이 들어 있으므로,
    # 에이전트에 넘길 최소 정보(role/content)만 추려서 전달합니다.
    return [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]


def _render_saved_chat_history() -> None:
    # Streamlit은 상호작용 때마다 파일을 다시 실행하므로,
    # 이전 메시지를 다시 그려 주지 않으면 화면이 비어 보이게 됩니다.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("tool_results"):
                render_tool_results(message["tool_results"])


def _run_chat_turn(user_input: str):
    # UI가 백엔드를 호출하는 지점을 이 함수 하나로 모아 두면
    # 이후 로깅, 예외 처리, 성능 측정 추가가 쉬워집니다.
    result = run_agent(
        user_input=user_input,
        chat_history=_get_saved_chat_history(),
        context=st.session_state.context,
        current_data=st.session_state.current_data,
    )

    tool_results = result.get("tool_results", [])
    extracted_params = result.get("extracted_params", {})
    if tool_results:
        # 이번 턴에서 추출한 조건을 저장해 두면
        # 다음 질문에서 날짜/공정/제품 조건을 이어받을 수 있습니다.
        sync_context(extracted_params)

    # current_data는 "사용자가 방금 보고 있는 표"입니다.
    # 후속 질문은 이 데이터를 기준으로 pandas 분석을 수행합니다.
    st.session_state.current_data = result.get("current_data")
    return result


def main() -> None:
    # 세션 상태 초기화는 앱의 시작점입니다.
    # 이 단계가 없으면 대화와 현재 테이블이 매번 초기화됩니다.
    init_session_state()

    st.title("제조 데이터 채팅 분석")
    st.caption("생산, 목표, 불량, 설비, WIP 조회와 현재 결과 기반 후속 분석을 지원합니다.")
    render_context()
    _render_saved_chat_history()

    user_input = st.chat_input("예: 오늘 생산량 보여줘 / 그 결과를 MODE별로 상위 3개만 정리해줘")
    if not user_input:
        return

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    result = _run_chat_turn(user_input)
    # 응답 텍스트와 표 데이터를 같이 저장해야
    # 이후 rerun에서도 같은 대화 화면을 그대로 복원할 수 있습니다.
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
