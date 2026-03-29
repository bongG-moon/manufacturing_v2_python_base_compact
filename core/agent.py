import json
from typing import Any, Dict, List, Literal

import pandas as pd
from langchain_core.messages import HumanMessage, SystemMessage

from .config import SYSTEM_PROMPT, get_llm
from .data_analysis_engine import execute_analysis_query
from .data_tools import build_current_datasets, execute_retrieval_tools, pick_retrieval_tools
from .dataset_contracts import (
    format_available_datasets_message,
    format_missing_params_message,
    get_dataset_label,
)
from .filter_utils import normalize_text
from .intent_router import build_route_clarification_message, classify_query_mode, should_ask_route_clarification
from .number_format import format_rows_for_display
from .parameter_resolver import resolve_required_params


QueryMode = Literal["retrieval", "followup_transform"]

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
]

FOLLOWUP_HINT_TOKENS = [
    "상위",
    "하위",
    "정렬",
    "그룹",
    "그룹화",
    "비교",
    "요약",
    "필터",
    "top",
    "sort",
    "group",
    "compare",
    "summary",
]

RETRIEVAL_CUE_TOKENS = [
    "조회",
    "보여",
    "가져와",
    "불러와",
    "데이터",
    "오늘",
    "어제",
    "날짜",
    "현황",
]


def _build_recent_chat_text(chat_history: List[Dict[str, str]], max_messages: int = 6) -> str:
    if not chat_history:
        return "(no recent chat)"

    lines = []
    for message in chat_history[-max_messages:]:
        content = str(message.get("content", "")).strip()
        if content:
            lines.append(f"- {message.get('role', 'unknown')}: {content}")
    return "\n".join(lines) if lines else "(no recent chat)"


def _extract_columns_from_rows(rows: List[Dict[str, Any]], max_scan_rows: int = 20) -> List[str]:
    columns = set()
    for row in rows[:max_scan_rows]:
        if isinstance(row, dict):
            columns.update(row.keys())
    return sorted(str(column) for column in columns)


def _get_current_table_columns(current_data: Dict[str, Any] | None) -> List[str]:
    if not isinstance(current_data, dict):
        return []

    cached_columns = current_data.get("columns")
    if isinstance(cached_columns, list) and cached_columns:
        return [str(column) for column in cached_columns]

    rows = current_data.get("data", [])
    if not isinstance(rows, list):
        return []
    return _extract_columns_from_rows(rows)


def _has_current_data(current_data: Dict[str, Any] | None) -> bool:
    return bool(isinstance(current_data, dict) and isinstance(current_data.get("data"), list) and current_data.get("data"))


def _collect_applied_params(extracted_params: Dict[str, Any]) -> Dict[str, Any]:
    return {field: extracted_params.get(field) for field in APPLIED_PARAM_FIELDS if extracted_params.get(field)}


def _finalize_table_result(result: Dict[str, Any]) -> Dict[str, Any]:
    rows = result.get("data", [])
    if isinstance(rows, list):
        result["row_count"] = len(rows)
        result["columns"] = _extract_columns_from_rows(rows)
    else:
        result["row_count"] = 0
        result["columns"] = []
    return result


def _build_table_artifact(label: str, rows: List[Dict[str, Any]], summary: str = "") -> Dict[str, Any]:
    return {
        "label": label,
        "summary": summary,
        "row_count": len(rows),
        "columns": _extract_columns_from_rows(rows),
        "data": rows,
    }


def _build_source_table_artifacts(tool_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    artifacts: List[Dict[str, Any]] = []
    for result in tool_results:
        rows = result.get("data", [])
        if not isinstance(rows, list):
            continue
        label = result.get("dataset_label") or get_dataset_label(str(result.get("dataset_key", "")))
        artifacts.append(_build_table_artifact(str(label), rows, str(result.get("summary", ""))))
    return artifacts


def _looks_like_new_data_request(query_text: str) -> bool:
    normalized = normalize_text(query_text)
    retrieval_keys = pick_retrieval_tools(query_text)

    if len(retrieval_keys) >= 2:
        return True
    if retrieval_keys and any(token in normalized for token in RETRIEVAL_CUE_TOKENS):
        return True
    if retrieval_keys and not any(token in normalized for token in FOLLOWUP_HINT_TOKENS):
        return True
    return False


def _prune_followup_params(user_input: str, extracted_params: Dict[str, Any]) -> Dict[str, Any]:
    normalized = normalize_text(user_input)
    cleaned = dict(extracted_params or {})
    filter_fields = ["process_name", "product_name", "line_name", "mode", "den", "tech", "lead", "mcp_no"]
    explicit_filter_intent = any(
        token in normalized for token in ["필터", "조건", "공정", "라인", "mode", "den", "tech", "lead", "mcp"]
    )
    if not explicit_filter_intent:
        for field in filter_fields:
            cleaned[field] = None
    return cleaned


def _choose_query_mode(user_input: str, current_data: Dict[str, Any] | None) -> QueryMode:
    routing = classify_query_mode(user_input, current_data)
    return str(routing.get("mode", "retrieval"))  # type: ignore[return-value]


def _looks_like_combined_analysis_request(query_text: str) -> bool:
    normalized = normalize_text(query_text)
    return any(token in normalized for token in ["비교", "달성", "차이", "그룹", "정렬", "상위", "하위", "compare"])


def _build_analysis_base_table(tool_results: List[Dict[str, Any]]) -> Dict[str, Any]:
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

        frames.append(df[available_dimensions + metric_columns].copy())
        source_names.append(str(result.get("tool_name", "unknown")))

    if not frames:
        return {
            "success": False,
            "tool_name": "analysis_base_table",
            "error_message": "공통 분석용 테이블을 만들지 못했습니다.",
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
                "error_message": "데이터셋 간 공통 join 축이 부족해 결합할 수 없습니다.",
                "data": [],
            }
        join_columns = next_join_columns
        merged_df = merged_df.merge(next_df, on=join_columns, how="outer")

    merged_df = merged_df.where(pd.notnull(merged_df), None)
    merged_rows = merged_df.to_dict(orient="records")
    return {
        "success": True,
        "tool_name": "analysis_base_table",
        "data": merged_rows,
        "summary": f"분석용 결합 테이블 생성 완료: {len(merged_rows)} rows",
        "source_tool_names": source_names,
        "join_columns": join_columns,
        "columns": _extract_columns_from_rows(merged_rows),
        "row_count": len(merged_rows),
    }


def _build_multi_dataset_overview(tool_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    overview_rows = []
    for result in tool_results:
        overview_rows.append(
            {
                "dataset": result.get("dataset_label", result.get("dataset_key", "")),
                "rows": len(result.get("data", [])) if isinstance(result.get("data", []), list) else 0,
                "summary": result.get("summary", ""),
            }
        )

    return _finalize_table_result(
        {
            "success": True,
            "tool_name": "multi_dataset_overview",
            "data": overview_rows,
            "summary": f"복수 데이터셋 조회 완료: {len(overview_rows)} datasets",
        }
    )


def _format_result_preview(result: Dict[str, Any], max_rows: int = 5) -> str:
    rows = result.get("data", [])
    if not isinstance(rows, list) or not rows:
        return "(empty)"

    preview_rows, _ = format_rows_for_display([row for row in rows[:max_rows] if isinstance(row, dict)])
    return json.dumps(preview_rows, ensure_ascii=False, indent=2)


def _build_response_prompt(user_input: str, result: Dict[str, Any], chat_history: List[Dict[str, str]]) -> str:
    return f"""제조 데이터 조회/분석 결과를 설명해 주세요.

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
1. 현재 결과 테이블 기준으로만 설명하세요.
2. 원본 전체 데이터를 본 것처럼 답하지 마세요.
3. 3~5문장으로 짧고 명확하게 설명하세요.
4. 숫자 단위 K/M는 다시 잘못 해석하지 마세요.
"""


def _generate_response(user_input: str, result: Dict[str, Any], chat_history: List[Dict[str, str]]) -> str:
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


def _run_multi_retrieval(
    user_input: str,
    chat_history: List[Dict[str, str]],
    current_data: Dict[str, Any] | None,
    extracted_params: Dict[str, Any],
    retrieval_keys: List[str],
) -> Dict[str, Any]:
    missing_message = format_missing_params_message(retrieval_keys, extracted_params)
    if missing_message:
        return {
            "response": missing_message,
            "tool_results": [],
            "current_data": current_data,
            "extracted_params": extracted_params,
            "awaiting_analysis_choice": bool(_has_current_data(current_data)),
        }

    source_results = [_finalize_table_result(result) for result in execute_retrieval_tools(retrieval_keys, extracted_params)]
    for result in source_results:
        if result.get("success"):
            result["original_tool_name"] = result.get("tool_name")
            result["applied_params"] = _collect_applied_params(extracted_params)
            if result.get("dataset_key"):
                result["dataset_label"] = get_dataset_label(str(result["dataset_key"]))

    failed_results = [result for result in source_results if not result.get("success")]
    if failed_results:
        return {
            "response": failed_results[0].get("error_message", "복수 데이터 조회 중 오류가 발생했습니다."),
            "tool_results": source_results,
            "current_data": current_data,
            "extracted_params": extracted_params,
            "awaiting_analysis_choice": bool(_has_current_data(current_data)),
        }

    current_datasets = build_current_datasets(source_results)
    source_artifacts = _build_source_table_artifacts(source_results)

    if _looks_like_combined_analysis_request(user_input):
        analysis_base = _build_analysis_base_table(source_results)
        if not analysis_base.get("success"):
            overview_result = _build_multi_dataset_overview(source_results)
            overview_result["current_datasets"] = current_datasets
            overview_result["source_tables"] = source_artifacts
            overview_result["applied_params"] = _collect_applied_params(extracted_params)
            return {
                "response": analysis_base.get("error_message", "공통 분석용 결합 테이블을 만들 수 없습니다."),
                "tool_results": [*source_results, overview_result],
                "current_data": overview_result,
                "extracted_params": extracted_params,
                "awaiting_analysis_choice": True,
            }

        analysis_result = _finalize_table_result(
            execute_analysis_query(
                query_text=user_input,
                data=analysis_base.get("data", []),
                source_tool_name=analysis_base.get("tool_name", ""),
            )
        )
        if analysis_result.get("success"):
            analysis_result["original_tool_name"] = "+".join(retrieval_keys)
            analysis_result["applied_params"] = _collect_applied_params(extracted_params)
            analysis_result["current_datasets"] = current_datasets
            analysis_result["source_tables"] = source_artifacts
            analysis_result["analysis_base_table"] = _build_table_artifact(
                "분석 결합 테이블",
                analysis_base.get("data", []),
                str(analysis_base.get("summary", "")),
            )
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
        overview_result["current_datasets"] = current_datasets
        overview_result["source_tables"] = source_artifacts
        overview_result["applied_params"] = _collect_applied_params(extracted_params)
        return {
            "response": analysis_result.get("error_message", "복수 데이터셋 분석에 실패했습니다."),
            "tool_results": [*source_results, overview_result],
            "current_data": overview_result,
            "extracted_params": extracted_params,
            "awaiting_analysis_choice": True,
        }

    overview_result = _build_multi_dataset_overview(source_results)
    overview_result["current_datasets"] = current_datasets
    overview_result["source_tables"] = source_artifacts
    overview_result["applied_params"] = _collect_applied_params(extracted_params)
    return {
        "response": _generate_response(user_input, overview_result, chat_history),
        "tool_results": [*source_results, overview_result],
        "current_data": overview_result,
        "extracted_params": extracted_params,
        "awaiting_analysis_choice": True,
    }


def _run_followup_analysis(
    user_input: str,
    chat_history: List[Dict[str, str]],
    current_data: Dict[str, Any],
    extracted_params: Dict[str, Any],
) -> Dict[str, Any]:
    cleaned_params = _prune_followup_params(user_input, extracted_params)
    result = _finalize_table_result(
        execute_analysis_query(
            query_text=user_input,
            data=current_data.get("data", []),
            source_tool_name=current_data.get("original_tool_name") or current_data.get("tool_name", ""),
        )
    )

    if result.get("success"):
        result["original_tool_name"] = current_data.get("original_tool_name") or current_data.get("tool_name", "")
        result["applied_params"] = _collect_applied_params(cleaned_params)
        result["current_datasets"] = current_data.get("current_datasets", {})
        result["source_tables"] = current_data.get("source_tables", [])
        result["analysis_base_table"] = _build_table_artifact(
            "분석 입력 테이블",
            current_data.get("data", []),
            str(current_data.get("summary", "")),
        )

    return {
        "response": _generate_response(user_input, result, chat_history)
        if result.get("success")
        else result.get("error_message", "분석에 실패했습니다."),
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
    routing = classify_query_mode(user_input, current_data)
    retrieval_keys = list(routing.get("retrieval_keys", [])) or pick_retrieval_tools(user_input)
    retrieval_key = retrieval_keys[0] if retrieval_keys else None

    if not retrieval_key:
        return {
            "response": format_available_datasets_message(),
            "tool_results": [],
            "current_data": current_data,
            "extracted_params": extracted_params,
            "awaiting_analysis_choice": bool(_has_current_data(current_data)),
        }

    if len(retrieval_keys) > 1:
        return _run_multi_retrieval(user_input, chat_history, current_data, extracted_params, retrieval_keys)

    missing_message = format_missing_params_message([retrieval_key], extracted_params)
    if missing_message:
        return {
            "response": missing_message,
            "tool_results": [],
            "current_data": current_data,
            "extracted_params": extracted_params,
            "awaiting_analysis_choice": bool(_has_current_data(current_data)),
        }

    result = _finalize_table_result(execute_retrieval_tools([retrieval_key], extracted_params)[0])
    if result.get("success"):
        result["original_tool_name"] = result.get("tool_name")
        result["applied_params"] = _collect_applied_params(extracted_params)
        result["dataset_label"] = get_dataset_label(retrieval_key)
        result["current_datasets"] = build_current_datasets([result])
        result["source_tables"] = _build_source_table_artifacts([result])

    return {
        "response": _generate_response(user_input, result, chat_history)
        if result.get("success")
        else result.get("error_message", "조회에 실패했습니다."),
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
    chat_history = chat_history or []
    context = context or {}
    current_data = current_data if isinstance(current_data, dict) else None

    extracted_params = resolve_required_params(
        user_input=user_input,
        chat_history_text=_build_recent_chat_text(chat_history),
        current_data_columns=_get_current_table_columns(current_data),
        context=context,
    )

    routing = classify_query_mode(user_input, current_data)
    if should_ask_route_clarification(routing, current_data):
        return {
            "response": build_route_clarification_message(routing, current_data),
            "tool_results": [],
            "current_data": current_data,
            "extracted_params": extracted_params,
            "awaiting_analysis_choice": bool(_has_current_data(current_data)),
        }

    mode = str(routing.get("mode", "retrieval"))
    if mode == "followup_transform" and isinstance(current_data, dict):
        return _run_followup_analysis(user_input, chat_history, current_data, extracted_params)

    return _run_retrieval(user_input, chat_history, current_data, extracted_params)
