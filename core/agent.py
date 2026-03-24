import json
from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage

from .config import SYSTEM_PROMPT, get_llm
from .data_analysis_engine import execute_analysis_query
from .data_tools import RETRIEVAL_TOOL_MAP, pick_retrieval_tool
from .filter_utils import normalize_text
from .parameter_resolver import resolve_required_params


def _format_chat_history(chat_history: List[Dict[str, str]], max_messages: int = 6) -> str:
    if not chat_history:
        return "(이전 대화 없음)"
    lines = []
    for msg in chat_history[-max_messages:]:
        content = str(msg.get("content", "")).strip()
        if content:
            lines.append(f"- {msg.get('role', 'unknown')}: {content}")
    return "\n".join(lines) if lines else "(이전 대화 없음)"


def _extract_current_data_columns(current_data: Dict[str, Any] | None) -> List[str]:
    if not isinstance(current_data, dict):
        return []
    rows = current_data.get("data", [])
    if not isinstance(rows, list):
        return []
    columns = set()
    for row in rows:
        if isinstance(row, dict):
            columns.update(row.keys())
    return sorted(columns)


def _has_current_data(current_data: Dict[str, Any] | None) -> bool:
    return bool(isinstance(current_data, dict) and isinstance(current_data.get("data"), list) and current_data.get("data"))


def _looks_like_fresh_retrieval(query_text: str) -> bool:
    normalized = normalize_text(query_text)
    retrieval_tokens = ["생산", "목표", "불량", "설비", "가동률", "재공", "wip", "오늘", "어제", "조회"]
    transform_tokens = ["상위", "하위", "그룹", "그룹화", "정렬", "비교", "요약", "필터", "기준", "별로"]
    return any(token in normalized for token in retrieval_tokens) and not any(token in normalized for token in transform_tokens)


def _prune_followup_params(user_input: str, extracted_params: Dict[str, Any]) -> Dict[str, Any]:
    normalized = normalize_text(user_input)
    cleaned = dict(extracted_params or {})
    filter_fields = ["process_name", "product_name", "line_name", "mode", "den", "tech", "lead", "mcp_no"]
    explicit_filter_intent = any(
        token in normalized for token in ["만", "필터", "조건", "공정", "라인", "mode", "den", "tech", "lead", "mcp"]
    )
    if not explicit_filter_intent:
        for field in filter_fields:
            cleaned[field] = None
    return cleaned


def _format_result_preview(result: Dict[str, Any], max_rows: int = 5) -> str:
    rows = result.get("data", [])
    if not isinstance(rows, list) or not rows:
        return "없음"
    return json.dumps(rows[:max_rows], ensure_ascii=False, indent=2)


def _generate_response(user_input: str, result: Dict[str, Any], chat_history: List[Dict[str, str]]) -> str:
    prompt = f"""사용자에게 제조 데이터 분석 결과를 설명해 주세요.

사용자 질문:
{user_input}

최근 대화:
{_format_chat_history(chat_history)}

현재 결과 요약:
{result.get('summary', '')}

현재 결과 건수:
{len(result.get('data', []))}건

현재 결과 미리보기:
{_format_result_preview(result)}

분석 계획:
{json.dumps(result.get('analysis_plan', {}), ensure_ascii=False)}

규칙:
1. 반드시 현재 결과 테이블 기준으로만 설명하세요.
2. 원본 전체 데이터 기준처럼 말하지 마세요.
3. 사용자의 요청이 그룹화, 상위 N, 정렬이라면 그 결과 구조를 짚어 주세요.
4. 3~5문장 정도로 짧고 명확하게 답하세요.
"""
    try:
        llm = get_llm()
        response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])
        if isinstance(response.content, str):
            return response.content
        if isinstance(response.content, list):
            return "\n".join(str(item.get("text", "")) if isinstance(item, dict) else str(item) for item in response.content)
        return str(response.content)
    except Exception:
        return f"{result.get('summary', '결과를 확인했습니다.')} 아래 표를 함께 확인해 주세요."


def run_agent(
    user_input: str,
    chat_history: List[Dict[str, str]] | None = None,
    context: Dict[str, Any] | None = None,
    current_data: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    chat_history = chat_history or []
    context = context or {}
    current_data = current_data if isinstance(current_data, dict) else None

    extracted_params = resolve_required_params(
        user_input=user_input,
        chat_history_text=_format_chat_history(chat_history),
        current_data_columns=_extract_current_data_columns(current_data),
        context=context,
    )

    if _has_current_data(current_data) and not _looks_like_fresh_retrieval(user_input):
        extracted_params = _prune_followup_params(user_input, extracted_params)
        result = execute_analysis_query(
            query_text=user_input,
            data=current_data.get("data", []),
            source_tool_name=current_data.get("original_tool_name") or current_data.get("tool_name", ""),
        )
        if result.get("success"):
            result["original_tool_name"] = current_data.get("original_tool_name") or current_data.get("tool_name", "")
            result["applied_params"] = {
                field: extracted_params.get(field)
                for field in ["date", "process_name", "product_name", "line_name", "mode", "den", "tech", "lead", "mcp_no", "group_by"]
                if extracted_params.get(field)
            }
            return {
                "response": _generate_response(user_input, result, chat_history),
                "tool_results": [result],
                "current_data": result,
                "extracted_params": extracted_params,
                "awaiting_analysis_choice": True,
            }

    retrieval_key = pick_retrieval_tool(user_input)
    if not retrieval_key:
        return {
            "response": "질문에서 어떤 원본 데이터를 조회해야 할지 판단하기 어려웠습니다. 생산, 목표, 불량, 설비, WIP 중 하나를 포함해 다시 말씀해 주세요.",
            "tool_results": [],
            "current_data": current_data,
            "extracted_params": extracted_params,
            "awaiting_analysis_choice": bool(_has_current_data(current_data)),
        }

    if not extracted_params.get("date"):
        return {
            "response": "조회 날짜가 필요합니다. 예: 오늘, 어제, 20260324",
            "tool_results": [],
            "current_data": current_data,
            "extracted_params": extracted_params,
            "awaiting_analysis_choice": bool(_has_current_data(current_data)),
        }

    result = RETRIEVAL_TOOL_MAP[retrieval_key](extracted_params)
    if result.get("success"):
        result["original_tool_name"] = result.get("tool_name")
        result["applied_params"] = {
            field: extracted_params.get(field)
            for field in ["date", "process_name", "product_name", "line_name", "mode", "den", "tech", "lead", "mcp_no", "group_by"]
            if extracted_params.get(field)
        }
    return {
        "response": _generate_response(user_input, result, chat_history) if result.get("success") else result.get("error_message", "조회에 실패했습니다."),
        "tool_results": [result],
        "current_data": result if result.get("success") else current_data,
        "extracted_params": extracted_params,
        "awaiting_analysis_choice": bool(result.get("success")),
    }
