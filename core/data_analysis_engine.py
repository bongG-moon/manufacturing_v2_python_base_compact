import json
import re
from typing import Any, Dict, List, Tuple

from langchain_core.messages import HumanMessage, SystemMessage

from .analysis_contracts import DatasetProfile, PreprocessPlan
from .config import get_llm
from .domain_knowledge import build_domain_knowledge_prompt
from .filter_utils import normalize_text
from .safe_code_executor import execute_safe_dataframe_code


DIMENSION_ALIAS_MAP = {
    "공정": {"공정", "process"},
    "라인": {"라인", "line"},
    "MODE": {"mode", "모드", "제품"},
    "DEN": {"den", "density", "용량"},
    "TECH": {"tech", "기술"},
    "LEAD": {"lead"},
    "MCP_NO": {"mcp", "mcp_no"},
    "공정군": {"공정군", "process family", "family"},
    "상태": {"상태", "status"},
    "주요불량유형": {"주요불량유형", "불량유형", "defect type"},
}


def _extract_columns(data: List[Dict[str, Any]]) -> List[str]:
    columns: List[str] = []
    for row in data:
        for key in row.keys():
            name = str(key)
            if name not in columns:
                columns.append(name)
    return columns


def _dataset_profile(data: List[Dict[str, Any]]) -> DatasetProfile:
    return {
        "columns": _extract_columns(data),
        "row_count": len(data),
        "sample_rows": list(data[:3]),
    }


def _extract_text_from_response(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts)
    return str(content)


def _extract_json_payload(text: str) -> Dict[str, Any]:
    cleaned = str(text or "").strip()
    if "```json" in cleaned:
        cleaned = cleaned.split("```json", 1)[1].split("```", 1)[0]
    elif "```" in cleaned:
        cleaned = cleaned.split("```", 1)[1].split("```", 1)[0]

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return {}

    try:
        return json.loads(cleaned[start : end + 1])
    except Exception:
        return {}


def _find_requested_dimensions(query_text: str) -> List[str]:
    normalized_query = normalize_text(query_text)
    requested: List[str] = []

    for canonical_name, aliases in DIMENSION_ALIAS_MAP.items():
        if any(normalize_text(alias) in normalized_query for alias in aliases):
            requested.append(canonical_name)

    for pattern in [r"([A-Za-z가-힣_]+)\s*별로", r"([A-Za-z가-힣_]+)\s*기준"]:
        for token in re.findall(pattern, query_text):
            token = str(token).strip()
            if not token or token in {"그룹", "데이터", "결과", "상위", "하위"}:
                continue

            resolved_name = None
            for canonical_name, aliases in DIMENSION_ALIAS_MAP.items():
                alias_candidates = {canonical_name, *aliases}
                if any(normalize_text(token) == normalize_text(alias) for alias in alias_candidates):
                    resolved_name = canonical_name
                    break

            requested.append(resolved_name or token)

    return list(dict.fromkeys(requested))


def _find_missing_dimensions(query_text: str, columns: List[str]) -> List[str]:
    available = set(columns)
    requested = _find_requested_dimensions(query_text)
    return [column for column in requested if column not in available]


def _format_missing_column_message(missing_columns: List[str], columns: List[str]) -> str:
    available_preview = ", ".join(columns[:12])
    missing_preview = ", ".join(missing_columns)
    return (
        f"요청하신 컬럼(조건) `{missing_preview}`은 현재 결과 테이블에 없습니다. "
        f"현재 사용할 수 있는 주요 컬럼은 `{available_preview}` 입니다."
    )


def _find_metric_column(columns: List[str], query_text: str) -> str:
    normalized = normalize_text(query_text)
    candidates = ["production", "target", "defect_rate", "불량수량", "가동률", "재공수량"]

    for candidate in candidates:
        if normalize_text(candidate) in normalized and candidate in columns:
            return candidate

    for candidate in candidates:
        if candidate in columns:
            return candidate

    return columns[-1]


def _parse_top_n(text: str, default: int = 5) -> int:
    match = re.search(r"(\d+)", str(text or ""))
    if match:
        return max(1, min(50, int(match.group(1))))
    return default


def _minimal_fallback_plan(query_text: str, data: List[Dict[str, Any]]) -> PreprocessPlan:
    columns = _extract_columns(data)
    metric_column = _find_metric_column(columns, query_text)
    sort_order = "asc" if any(token in normalize_text(query_text) for token in ["하위", "최소", "낮은"]) else "desc"
    top_n = _parse_top_n(query_text, default=5)
    return {
        "intent": "basic sort fallback",
        "operations": ["sort_values", "head"],
        "output_columns": columns,
        "sort_by": metric_column,
        "sort_order": sort_order,
        "top_n": top_n,
        "metric_column": metric_column,
        "warnings": ["LLM code generation failed. Minimal fallback was used."],
        "source": "fallback",
        "code": (
            f"result = df.sort_values(by={metric_column!r}, "
            f"ascending={str(sort_order == 'asc')}).head({top_n})"
        ),
    }


def _build_llm_prompt(
    query_text: str,
    data: List[Dict[str, Any]],
    retry_error: str = "",
    previous_code: str = "",
) -> str:
    profile = _dataset_profile(data)
    retry_section = ""
    if retry_error:
        retry_section = f"""
Previous generated code failed.
Failure reason:
{retry_error}

Previous code:
{previous_code}

Write a corrected pandas transformation.
"""

    return f"""You generate pandas code for follow-up analysis on an already retrieved manufacturing dataframe.
Return JSON only.

Authority rules:
- The generated pandas code is the primary execution path.
- Do not rely on predefined templates.
- Work only on dataframe `df`.
- Always assign the final DataFrame to `result`.
- Do not import anything.
- Do not use files, network, shell, eval, exec, OS APIs, plotting, or database access.
- Use only pandas operations on existing columns.
- Never invent missing columns.
- If the user requests a column that does not exist, leave code empty and add a warning.
- Prefer concise, readable code.
- If grouping, sorting, filtering, ranking, top-N-per-group, or derived columns are needed, express them directly in code.

Manufacturing domain hints:
{build_domain_knowledge_prompt()}

Dataset profile:
{json.dumps(profile, ensure_ascii=False)}

User question:
{query_text}
{retry_section}

Return this schema:
{{
  "intent": "short summary",
  "operations": ["groupby", "sort_values"],
  "output_columns": ["MODE", "production"],
  "group_by_columns": ["MODE"],
  "partition_by_columns": [],
  "filters": [],
  "sort_by": "production",
  "sort_order": "desc",
  "top_n": 5,
  "top_n_per_group": 3,
  "metric_column": "production",
  "warnings": [],
  "code": "result = df.copy()"
}}
"""


def _build_llm_plan(query_text: str, data: List[Dict[str, Any]], retry_error: str = "", previous_code: str = "") -> Tuple[PreprocessPlan | None, str]:
    try:
        llm = get_llm()
        prompt = _build_llm_prompt(query_text, data, retry_error=retry_error, previous_code=previous_code)
        response = llm.invoke(
            [
                SystemMessage(content="Generate safe pandas dataframe transformation code."),
                HumanMessage(content=prompt),
            ]
        )
        parsed = _extract_json_payload(_extract_text_from_response(response.content))
        code = str(parsed.get("code", "") or "").strip()

        plan: PreprocessPlan = {
            "intent": str(parsed.get("intent", "current data preprocessing")).strip() or "current data preprocessing",
            "operations": [str(item).strip() for item in (parsed.get("operations") or []) if str(item).strip()],
            "output_columns": [str(item).strip() for item in (parsed.get("output_columns") or []) if str(item).strip()],
            "group_by_columns": [str(item).strip() for item in (parsed.get("group_by_columns") or []) if str(item).strip()],
            "partition_by_columns": [str(item).strip() for item in (parsed.get("partition_by_columns") or []) if str(item).strip()],
            "filters": parsed.get("filters") or [],
            "sort_by": str(parsed.get("sort_by", "")).strip(),
            "sort_order": str(parsed.get("sort_order", "")).strip() or "desc",
            "metric_column": str(parsed.get("metric_column", "")).strip(),
            "warnings": [str(item).strip() for item in (parsed.get("warnings") or []) if str(item).strip()],
            "code": code,
            "source": "llm_primary" if not retry_error else "llm_retry",
        }
        if isinstance(parsed.get("top_n"), int):
            plan["top_n"] = parsed["top_n"]
        if isinstance(parsed.get("top_n_per_group"), int):
            plan["top_n_per_group"] = parsed["top_n_per_group"]

        if not code:
            return None, "llm_empty_code"
        return plan, "llm_primary" if not retry_error else "llm_retry"
    except Exception:
        return None, "llm_failed"


def _validate_plan_columns(plan: PreprocessPlan, columns: List[str]) -> List[str]:
    required_columns: List[str] = []
    for field_name in ["group_by_columns", "partition_by_columns", "output_columns"]:
        for column in plan.get(field_name, []) or []:
            if column is None:
                continue
            column_name = str(column).strip()
            if column_name and column_name.lower() != "none":
                required_columns.append(column_name)

    for field_name in ["sort_by", "metric_column"]:
        raw_value = plan.get(field_name, "")
        if raw_value is None:
            continue
        column_name = str(raw_value).strip()
        if column_name and column_name.lower() != "none":
            required_columns.append(column_name)

    unique_required = list(dict.fromkeys(required_columns))
    return [column for column in unique_required if column not in columns]


def _build_transformation_summary(
    plan: PreprocessPlan,
    input_rows: int,
    output_rows: int,
    analysis_logic: str,
) -> Dict[str, Any]:
    return {
        "analysis_logic": analysis_logic,
        "input_row_count": input_rows,
        "output_row_count": output_rows,
        "group_by_columns": plan.get("group_by_columns", []),
        "partition_by_columns": plan.get("partition_by_columns", []),
        "metric_column": plan.get("metric_column", ""),
        "sort_by": plan.get("sort_by", ""),
        "sort_order": plan.get("sort_order", ""),
        "top_n": plan.get("top_n"),
        "top_n_per_group": plan.get("top_n_per_group"),
        "output_columns": plan.get("output_columns", []),
        "warnings": plan.get("warnings", []),
    }


def _execute_plan(plan: PreprocessPlan, data: List[Dict[str, Any]]) -> Dict[str, Any]:
    return execute_safe_dataframe_code(str(plan.get("code", "")).strip(), data)


def execute_analysis_query(query_text: str, data: List[Dict[str, Any]], source_tool_name: str = "") -> Dict[str, Any]:
    if not data:
        return {
            "success": False,
            "tool_name": "analyze_current_data",
            "error_message": "분석할 현재 데이터가 없습니다.",
            "data": [],
        }

    columns = _extract_columns(data)
    missing_dimensions = _find_missing_dimensions(query_text, columns)
    if missing_dimensions:
        return {
            "success": False,
            "tool_name": "analyze_current_data",
            "error_message": _format_missing_column_message(missing_dimensions, columns),
            "data": [],
            "missing_columns": missing_dimensions,
            "available_columns": columns,
        }

    plan, analysis_logic = _build_llm_plan(query_text, data)
    if plan is None:
        plan = _minimal_fallback_plan(query_text, data)
        analysis_logic = "minimal_fallback"

    plan_missing_columns = _validate_plan_columns(plan, columns)
    if plan_missing_columns:
        return {
            "success": False,
            "tool_name": "analyze_current_data",
            "error_message": _format_missing_column_message(plan_missing_columns, columns),
            "data": [],
            "analysis_plan": plan,
            "analysis_logic": analysis_logic,
            "missing_columns": plan_missing_columns,
            "available_columns": columns,
        }

    executed = _execute_plan(plan, data)
    if not executed.get("success") and str(plan.get("source")) == "llm_primary":
        retry_plan, retry_logic = _build_llm_plan(
            query_text,
            data,
            retry_error=str(executed.get("error_message", "")),
            previous_code=str(plan.get("code", "")),
        )
        if retry_plan is not None:
            retry_missing_columns = _validate_plan_columns(retry_plan, columns)
            if not retry_missing_columns:
                retry_executed = _execute_plan(retry_plan, data)
                if retry_executed.get("success"):
                    result_rows = retry_executed.get("data", [])
                    return {
                        "success": True,
                        "tool_name": "analyze_current_data",
                        "data": result_rows,
                        "summary": f"현재 데이터 분석 결과: {len(result_rows)}행",
                        "analysis_plan": retry_plan,
                        "analysis_logic": retry_logic,
                        "generated_code": retry_plan.get("code", ""),
                        "source_tool_name": source_tool_name,
                        "transformation_summary": _build_transformation_summary(
                            retry_plan,
                            input_rows=len(data),
                            output_rows=len(result_rows),
                            analysis_logic=retry_logic,
                        ),
                    }
                executed = retry_executed
                plan = retry_plan
                analysis_logic = retry_logic

    if not executed.get("success"):
        error_message = str(executed.get("error_message", "분석 코드 실행에 실패했습니다."))
        if "KeyError" in error_message:
            missing_from_error = plan_missing_columns or missing_dimensions or ["요청 컬럼"]
            error_message = _format_missing_column_message(missing_from_error, columns)

        return {
            "success": False,
            "tool_name": "analyze_current_data",
            "error_message": error_message,
            "data": [],
            "analysis_plan": plan,
            "analysis_logic": analysis_logic,
            "generated_code": plan.get("code", ""),
            "missing_columns": plan_missing_columns,
            "available_columns": columns,
        }

    result_rows = executed.get("data", [])
    return {
        "success": True,
        "tool_name": "analyze_current_data",
        "data": result_rows,
        "summary": f"현재 데이터 분석 결과: {len(result_rows)}행",
        "analysis_plan": plan,
        "analysis_logic": analysis_logic,
        "generated_code": plan.get("code", ""),
        "source_tool_name": source_tool_name,
        "transformation_summary": _build_transformation_summary(
            plan,
            input_rows=len(data),
            output_rows=len(result_rows),
            analysis_logic=analysis_logic,
        ),
    }
