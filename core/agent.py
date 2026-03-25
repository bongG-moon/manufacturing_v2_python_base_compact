import json
from typing import Any, Dict, List, Literal

import pandas as pd
from langchain_core.messages import HumanMessage, SystemMessage

from .config import SYSTEM_PROMPT, get_llm
from .data_analysis_engine import execute_analysis_query
from .data_tools import build_current_datasets, execute_retrieval_tools, pick_retrieval_tools
from .filter_utils import normalize_text
from .number_format import format_rows_for_display
from .parameter_resolver import resolve_required_params


QueryMode = Literal["retrieval", "followup_transform"]

# UI와 리포트에서 공통으로 보여 줄 "실제 반영 조건" 목록입니다.
APPLIED_PARAM_FIELDS = [
    "date",
    "process_name",
    "product_name",
    "line_name",
    "mode",
    "den",
    "tech",
    "lead",
    "mcp_no",
    "group_by",
]


def _build_recent_chat_text(chat_history: List[Dict[str, str]], max_messages: int = 6) -> str:
    # 최근 대화 몇 개만 프롬프트에 넣어야
    # 비용을 줄이고 현재 질문과 관련된 맥락만 유지할 수 있습니다.
    if not chat_history:
        return "(이전 대화 없음)"

    lines = []
    for msg in chat_history[-max_messages:]:
        content = str(msg.get("content", "")).strip()
        if content:
            lines.append(f"- {msg.get('role', 'unknown')}: {content}")
    return "\n".join(lines) if lines else "(이전 대화 없음)"


def _get_current_table_columns(current_data: Dict[str, Any] | None) -> List[str]:
    # 후속 질문은 현재 표에 있는 컬럼으로만 분석할 수 있으므로
    # 먼저 현재 표의 컬럼 목록을 추출합니다.
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
    # current_data가 있으면 후속 pandas 분석이 가능하다는 뜻입니다.
    return bool(isinstance(current_data, dict) and isinstance(current_data.get("data"), list) and current_data.get("data"))


def _collect_applied_params(extracted_params: Dict[str, Any]) -> Dict[str, Any]:
    # 내부적으로 많은 정보가 오가더라도
    # 사용자에게는 실제 반영된 조건만 보여 주는 것이 이해하기 쉽습니다.
    return {field: extracted_params.get(field) for field in APPLIED_PARAM_FIELDS if extracted_params.get(field)}


def _looks_like_new_data_request(query_text: str) -> bool:
    # 질문이 "새 데이터를 가져오려는 것인지" 아니면
    # "현재 표를 다시 가공하려는 것인지"를 가볍게 판단하는 1차 규칙입니다.
    normalized = normalize_text(query_text)
    retrieval_keys = pick_retrieval_tools(query_text)
    retrieval_tokens = ["생산", "목표", "불량", "설비", "가동률", "재공", "wip", "오늘", "어제", "조회"]
    transform_tokens = ["상위", "하위", "그룹", "정렬", "비교", "요약", "필터", "기준", "별로"]

    # 서로 다른 원본 데이터셋이 2개 이상 보이면 현재 표 가공보다 "새 조회" 가능성이 훨씬 큽니다.
    if len(retrieval_keys) >= 2:
        return True

    # "조회/데이터/보여줘" 같은 표현이 있으면 새로 가져오겠다는 의도로 보는 편이 안전합니다.
    if retrieval_keys and any(token in normalized for token in ["조회", "데이터", "보여", "알려"]):
        return True

    return any(token in normalized for token in retrieval_tokens) and not any(token in normalized for token in transform_tokens)


def _prune_followup_params(user_input: str, extracted_params: Dict[str, Any]) -> Dict[str, Any]:
    # 후속 분석에서는 예전 조회 조건을 무조건 다시 적용하지 않습니다.
    # 사용자가 명시적으로 필터를 요청한 경우에만 해당 조건을 유지합니다.
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


def _choose_query_mode(user_input: str, current_data: Dict[str, Any] | None) -> QueryMode:
    # 메인 분기 규칙:
    # - current_data가 있고 새 조회처럼 안 보이면 후속 분석
    # - 그 외에는 새 조회
    if _has_current_data(current_data) and not _looks_like_new_data_request(user_input):
        return "followup_transform"
    return "retrieval"


def _looks_like_combined_analysis_request(query_text: str) -> bool:
    # 여러 원본 데이터를 같이 조회한 뒤, 바로 비교/달성율/차이 계산을 원하는지 판단합니다.
    normalized = normalize_text(query_text)
    analysis_tokens = ["대비", "달성", "달성율", "달성률", "비교", "차이", "그룹", "별로", "기준", "요약", "정렬", "상위", "하위", "순으로", "큰 순", "낮은 순"]
    return any(token in normalized for token in analysis_tokens)


def _build_analysis_base_table(tool_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    # 여러 데이터셋을 바로 억지로 합치는 대신,
    # "질문 분석에 쓸 수 있는 공통 테이블이 있으면 만든다"는 개념으로 사용합니다.
    # 이렇게 이름을 바꾸면 merge 자체가 목적이 아니라 분석 준비 단계라는 점이 더 잘 보입니다.
    dimension_columns = ["날짜", "공정", "공정군", "MODE", "DEN", "TECH", "LEAD", "MCP_NO", "라인"]
    frames: List[pd.DataFrame] = []
    source_names: List[str] = []

    for result in tool_results:
        rows = result.get("data", [])
        if not isinstance(rows, list) or not rows:
            continue

        df = pd.DataFrame(rows)
        available_dimensions = [column for column in dimension_columns if column in df.columns]
        metric_columns = [column for column in df.columns if column not in available_dimensions]
        if not available_dimensions or not metric_columns:
            continue

        keep_columns = available_dimensions + metric_columns
        frames.append(df[keep_columns].copy())
        source_names.append(result.get("tool_name", "unknown"))

    if not frames:
        return {
            "success": False,
            "tool_name": "analysis_base_table",
            "error_message": "여러 조회 결과에서 공통 분석용 테이블을 만들지 못했습니다.",
            "data": [],
        }

    merged_df = frames[0]
    join_columns = [column for column in dimension_columns if column in merged_df.columns]

    for next_df in frames[1:]:
        next_join_columns = [column for column in join_columns if column in next_df.columns]
        if not next_join_columns:
            return {
                "success": False,
                "tool_name": "analysis_base_table",
                "error_message": "여러 조회 결과 사이에 공통 키 컬럼이 부족해 함께 분석할 수 없습니다.",
                "data": [],
            }
        join_columns = next_join_columns
        merged_df = merged_df.merge(next_df, on=join_columns, how="outer")

    merged_df = merged_df.where(pd.notnull(merged_df), None)
    merged_rows = merged_df.to_dict(orient="records")
    source_label = ", ".join(source_names)
    return {
        "success": True,
        "tool_name": "analysis_base_table",
        "data": merged_rows,
        "summary": f"복수 조회 분석용 테이블 생성: {source_label}, 총 {len(merged_rows)}행",
        "source_tool_names": source_names,
        "join_columns": join_columns,
    }


def _build_multi_dataset_overview(tool_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    # 여러 원본 데이터를 한 번에 요청했지만 바로 계산까지 하지 않는 경우,
    # 사용자에게 어떤 데이터셋이 준비되었는지 먼저 보여주는 용도의 간단한 표입니다.
    overview_rows = []
    for result in tool_results:
        overview_rows.append(
            {
                "데이터셋": result.get("dataset_label", result.get("dataset_key", "")),
                "행수": len(result.get("data", [])) if isinstance(result.get("data"), list) else 0,
                "요약": result.get("summary", ""),
            }
        )

    return {
        "success": True,
        "tool_name": "multi_dataset_overview",
        "data": overview_rows,
        "summary": f"복수 데이터셋 조회 완료: 총 {len(overview_rows)}개",
    }


def _run_multi_retrieval(
    user_input: str,
    chat_history: List[Dict[str, str]],
    current_data: Dict[str, Any] | None,
    extracted_params: Dict[str, Any],
    retrieval_keys: List[str],
) -> Dict[str, Any]:
    # 범용 다중 조회 경로:
    # 1) 등록부 기준으로 필요한 원본 tool 실행
    # 2) 각 결과를 current_datasets 형태로 보관
    # 3) 질문이 비교/달성율 성격이면 공통 분석용 테이블을 만든 뒤 pandas 분석 수행
    source_results = execute_retrieval_tools(retrieval_keys, extracted_params)
    for result in source_results:
        if result.get("success"):
            result["original_tool_name"] = result.get("tool_name")
            result["applied_params"] = _collect_applied_params(extracted_params)

    failed_results = [result for result in source_results if not result.get("success")]
    if failed_results:
        first_error = failed_results[0]
        return {
            "response": first_error.get("error_message", "복수 조회 중 오류가 발생했습니다."),
            "tool_results": source_results,
            "current_data": current_data,
            "extracted_params": extracted_params,
            "awaiting_analysis_choice": bool(_has_current_data(current_data)),
        }

    current_datasets = build_current_datasets(source_results)

    if _looks_like_combined_analysis_request(user_input):
        analysis_base = _build_analysis_base_table(source_results)
        if not analysis_base.get("success"):
            overview_result = _build_multi_dataset_overview(source_results)
            overview_result["current_datasets"] = current_datasets
            overview_result["applied_params"] = _collect_applied_params(extracted_params)
            return {
                "response": analysis_base.get(
                    "error_message",
                    "여러 데이터셋을 함께 분석할 공통 기준을 찾지 못했습니다.",
                ),
                "tool_results": [*source_results, overview_result],
                "current_data": overview_result,
                "extracted_params": extracted_params,
                "awaiting_analysis_choice": True,
            }

        analysis_result = execute_analysis_query(
            query_text=user_input,
            data=analysis_base.get("data", []),
            source_tool_name=analysis_base.get("tool_name", ""),
        )
        if analysis_result.get("success"):
            analysis_result["original_tool_name"] = "+".join(retrieval_keys)
            analysis_result["applied_params"] = _collect_applied_params(extracted_params)
            analysis_result["current_datasets"] = current_datasets
            analysis_result["analysis_base_info"] = {
                "join_columns": analysis_base.get("join_columns", []),
                "source_tool_names": analysis_base.get("source_tool_names", []),
            }
            return {
                "response": _generate_response(user_input, analysis_result, chat_history),
                "tool_results": [*source_results, analysis_result],
                "current_data": analysis_result,
                "extracted_params": extracted_params,
                "awaiting_analysis_choice": True,
            }

        overview_result = _build_multi_dataset_overview(source_results)
        overview_result["original_tool_name"] = "+".join(retrieval_keys)
        overview_result["applied_params"] = _collect_applied_params(extracted_params)
        overview_result["current_datasets"] = current_datasets
        return {
            "response": analysis_result.get(
                "error_message",
                "복수 데이터셋 분석에 실패했습니다.",
            ),
            "tool_results": [*source_results, overview_result],
            "current_data": overview_result,
            "extracted_params": extracted_params,
            "awaiting_analysis_choice": True,
        }

    overview_result = _build_multi_dataset_overview(source_results)
    overview_result["original_tool_name"] = "+".join(retrieval_keys)
    overview_result["applied_params"] = _collect_applied_params(extracted_params)
    overview_result["current_datasets"] = current_datasets

    return {
        "response": _generate_response(user_input, overview_result, chat_history),
        "tool_results": [*source_results, overview_result],
        "current_data": overview_result,
        "extracted_params": extracted_params,
        "awaiting_analysis_choice": True,
    }


def _format_result_preview(result: Dict[str, Any], max_rows: int = 5) -> str:
    # 전체 데이터를 프롬프트에 넣으면 너무 길어지므로
    # 앞부분 몇 줄만 보기 좋은 형태로 잘라서 사용합니다.
    rows = result.get("data", [])
    if not isinstance(rows, list) or not rows:
        return "없음"

    preview_rows, _ = format_rows_for_display([row for row in rows[:max_rows] if isinstance(row, dict)])
    return json.dumps(preview_rows, ensure_ascii=False, indent=2)


def _build_response_prompt(user_input: str, result: Dict[str, Any], chat_history: List[Dict[str, str]]) -> str:
    # LLM이 "원본 전체 데이터"가 아니라
    # "지금 화면에 있는 결과 테이블"을 기준으로 답하도록 강하게 유도합니다.
    return f"""사용자에게 제조 데이터 분석 결과를 설명해 주세요.

사용자 질문:
{user_input}

최근 대화:
{_build_recent_chat_text(chat_history)}

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
3. 그룹화, 상위 N, 정렬 요청이면 그 결과 구조를 직접 설명하세요.
4. preview에 이미 K 또는 M 단위가 붙은 값은 다시 단위를 덧붙이지 마세요.
5. 예를 들어 2.8K를 2,800K처럼 쓰면 안 됩니다.
6. 3~5문장 정도로 짧고 명확하게 답하세요.
"""


def _generate_response(user_input: str, result: Dict[str, Any], chat_history: List[Dict[str, str]]) -> str:
    # 조회와 후속 분석 모두 같은 스타일로 답하도록
    # 응답 생성 로직을 한 함수로 통일했습니다.
    prompt = _build_response_prompt(user_input, result, chat_history)
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


def _run_followup_analysis(
    user_input: str,
    chat_history: List[Dict[str, str]],
    current_data: Dict[str, Any],
    extracted_params: Dict[str, Any],
) -> Dict[str, Any]:
    # 이 경로는 "현재 테이블을 다시 가공"하는 후속 분석 전용 경로입니다.
    cleaned_params = _prune_followup_params(user_input, extracted_params)
    result = execute_analysis_query(
        query_text=user_input,
        data=current_data.get("data", []),
        source_tool_name=current_data.get("original_tool_name") or current_data.get("tool_name", ""),
    )

    if result.get("success"):
        result["original_tool_name"] = current_data.get("original_tool_name") or current_data.get("tool_name", "")
        result["applied_params"] = _collect_applied_params(cleaned_params)

    return {
        "response": _generate_response(user_input, result, chat_history) if result.get("success") else result.get("error_message", "분석에 실패했습니다."),
        "tool_results": [result] if result else [],
        "current_data": result if result.get("success") else current_data,
        "extracted_params": cleaned_params,
        "awaiting_analysis_choice": bool(result.get("success")),
    }


def _run_retrieval(
    user_input: str,
    chat_history: List[Dict[str, str]],
    current_data: Dict[str, Any] | None,
    extracted_params: Dict[str, Any],
) -> Dict[str, Any]:
    # 이 경로는 생산/목표/불량/설비/WIP 중 어떤 원본 데이터를
    # 새로 가져와야 하는지 결정하고 실행합니다.
    retrieval_keys = pick_retrieval_tools(user_input)
    retrieval_key = retrieval_keys[0] if retrieval_keys else None
    if not retrieval_key:
        return {
            "response": "어떤 데이터를 조회할지 판단하지 못했습니다. 생산, 목표, 불량, 설비, WIP, 수율, 홀드, 스크랩, 레시피, LOT 이력 중 하나를 포함해 다시 질문해 주세요.",
            "tool_results": [],
            "current_data": current_data,
            "extracted_params": extracted_params,
            "awaiting_analysis_choice": bool(_has_current_data(current_data)),
        }

    if not extracted_params.get("date"):
        return {
            "response": "조회 날짜를 찾지 못했습니다. 예: 오늘, 어제, 20260324",
            "tool_results": [],
            "current_data": current_data,
            "extracted_params": extracted_params,
            "awaiting_analysis_choice": bool(_has_current_data(current_data)),
        }

    if len(retrieval_keys) > 1:
        return _run_multi_retrieval(user_input, chat_history, current_data, extracted_params, retrieval_keys)

    result = execute_retrieval_tools([retrieval_key], extracted_params)[0]
    if result.get("success"):
        result["original_tool_name"] = result.get("tool_name")
        result["applied_params"] = _collect_applied_params(extracted_params)

    return {
        "response": _generate_response(user_input, result, chat_history) if result.get("success") else result.get("error_message", "조회에 실패했습니다."),
        "tool_results": [result],
        "current_data": result if result.get("success") else current_data,
        "extracted_params": extracted_params,
        "awaiting_analysis_choice": bool(result.get("success")),
    }


def run_agent(
    user_input: str,
    chat_history: List[Dict[str, str]] | None = None,
    context: Dict[str, Any] | None = None,
    current_data: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    # 메인 파이프라인
    # 1) 질문에서 필수 조건 추출
    # 2) retrieval / follow-up 모드 결정
    # 3) 선택된 경로 실행
    chat_history = chat_history or []
    context = context or {}
    current_data = current_data if isinstance(current_data, dict) else None

    extracted_params = resolve_required_params(
        user_input=user_input,
        chat_history_text=_build_recent_chat_text(chat_history),
        current_data_columns=_get_current_table_columns(current_data),
        context=context,
    )

    mode = _choose_query_mode(user_input, current_data)
    if mode == "followup_transform" and isinstance(current_data, dict):
        return _run_followup_analysis(user_input, chat_history, current_data, extracted_params)

    return _run_retrieval(user_input, chat_history, current_data, extracted_params)
