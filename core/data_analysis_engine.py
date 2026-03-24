import json
import re
from typing import Any, Dict, List, Tuple

from langchain_core.messages import HumanMessage, SystemMessage

from .analysis_contracts import DatasetProfile, PreprocessPlan
from .config import get_llm
from .filter_utils import normalize_text
from .safe_code_executor import execute_safe_dataframe_code


DIMENSION_ALIAS_MAP = {
    "공정": {"공정", "process"},
    "라인": {"라인", "line"},
    "MODE": {"mode", "모드", "제품"},
    "DEN": {"den", "density", "밀도"},
    "TECH": {"tech", "기술"},
    "LEAD": {"lead"},
    "MCP_NO": {"mcp", "mcp_no"},
}


def _extract_columns(data: List[Dict[str, Any]]) -> List[str]:
    columns: List[str] = []
    for row in data:
        for key in row.keys():
            name = str(key)
            if name not in columns:
                columns.append(name)
    return columns


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
        return json.loads(cleaned[start:end + 1])
    except Exception:
        return {}


def _dataset_profile(data: List[Dict[str, Any]]) -> DatasetProfile:
    return {"columns": _extract_columns(data), "row_count": len(data), "sample_rows": list(data[:3])}


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


def _find_dimension_columns_from_query(query_text: str, columns: List[str]) -> List[str]:
    normalized_query = normalize_text(query_text)
    matched: List[str] = []
    for column in columns:
        column_norm = normalize_text(column)
        if column_norm in normalized_query:
            matched.append(column)
            continue
        aliases = DIMENSION_ALIAS_MAP.get(column, {column})
        if any(normalize_text(alias) in normalized_query for alias in aliases):
            matched.append(column)
    return list(dict.fromkeys(matched))


def _parse_top_n(text: str, default: int = 5) -> int:
    match = re.search(r"(\d+)", str(text or ""))
    if match:
        return max(1, min(50, int(match.group(1))))
    return default


def _parse_top_n_per_group(text: str) -> int | None:
    query = str(text or "")
    normalized = normalize_text(query)
    if not any(token in normalized for token in ["각", "그룹별", "별로", "each"]):
        return None
    for pattern in [re.compile(r"상위\s*(\d+)\s*개씩"), re.compile(r"하위\s*(\d+)\s*개씩")]:
        match = pattern.search(query)
        if match:
            return max(1, min(20, int(match.group(1))))
    return None


def _heuristic_plan(query_text: str, data: List[Dict[str, Any]]) -> PreprocessPlan:
    columns = _extract_columns(data)
    metric_column = _find_metric_column(columns, query_text)
    group_by_columns = _find_dimension_columns_from_query(query_text, columns)
    top_n = _parse_top_n(query_text, default=5)
    top_n_per_group = _parse_top_n_per_group(query_text)
    sort_order = "asc" if any(token in normalize_text(query_text) for token in ["하위", "최소", "최저"]) else "desc"

    if group_by_columns:
        plan: PreprocessPlan = {
            "intent": f"{', '.join(group_by_columns)} 기준 그룹 집계",
            "operations": ["groupby", "sort"],
            "output_columns": group_by_columns + [metric_column],
            "group_by_columns": group_by_columns,
            "sort_by": metric_column,
            "sort_order": sort_order,
            "metric_column": metric_column,
            "warnings": [],
            "source": "heuristic",
        }
        if top_n_per_group:
            plan["top_n_per_group"] = top_n_per_group
            plan["partition_by_columns"] = group_by_columns
            plan["operations"].append("top_n_per_group")
        else:
            plan["top_n"] = top_n
            plan["operations"].append("top_n")
        return plan

    return {
        "intent": "현재 데이터 상위/하위 조회",
        "operations": ["sort", "top_n"],
        "output_columns": columns,
        "sort_by": metric_column,
        "sort_order": sort_order,
        "top_n": top_n,
        "metric_column": metric_column,
        "warnings": [],
        "source": "heuristic",
    }


def _llm_preprocess_plan(query_text: str, data: List[Dict[str, Any]]) -> Tuple[PreprocessPlan | None, str]:
    profile = _dataset_profile(data)
    prompt = f"""You are generating pandas preprocessing code for a manufacturing assistant.
Return JSON only.

Rules:
- Work only on dataframe df.
- Always assign the final DataFrame to result.
- No imports, files, network, shell, eval, exec, or OS APIs.
- Prefer short readable pandas code.
- If the user asks for group별 상위 N개, express that in both structure fields and code.

Dataset profile:
{json.dumps(profile, ensure_ascii=False)}

User question:
{query_text}

Return:
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
}}"""
    try:
        llm = get_llm()
        response = llm.invoke([SystemMessage(content="Generate safe pandas preprocessing code."), HumanMessage(content=prompt)])
        parsed = _extract_json_payload(_extract_text_from_response(response.content))
        code = str(parsed.get("code", "")).strip()
        if not code:
            return None, "llm_failed"
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
            "source": "llm",
        }
        if isinstance(parsed.get("top_n"), int):
            plan["top_n"] = parsed["top_n"]
        if isinstance(parsed.get("top_n_per_group"), int):
            plan["top_n_per_group"] = parsed["top_n_per_group"]
        return plan, "llm"
    except Exception:
        return None, "llm_failed"


def build_analysis_plan(query_text: str, data: List[Dict[str, Any]]) -> Tuple[PreprocessPlan, str]:
    plan, source = _llm_preprocess_plan(query_text, data)
    if plan:
        return plan, source
    return _heuristic_plan(query_text, data), "heuristic"


def compile_analysis_plan_to_code(plan: PreprocessPlan) -> str:
    if plan.get("code"):
        return str(plan["code"]).strip()

    group_by_columns = [str(col).strip() for col in (plan.get("group_by_columns") or []) if str(col).strip()]
    metric_column = str(plan.get("metric_column", "")).strip()
    ascending = str(plan.get("sort_order", "desc")).lower() == "asc"

    if group_by_columns and metric_column:
        top_n_per_group = plan.get("top_n_per_group")
        top_n = int(plan.get("top_n", 5))
        if isinstance(top_n_per_group, int) and top_n_per_group > 0:
            partition_by = [str(col).strip() for col in (plan.get("partition_by_columns") or []) if str(col).strip()]
            if not partition_by and len(group_by_columns) > 1:
                partition_by = group_by_columns[:-1]
            return f"""
group_cols = {group_by_columns!r}
metric_col = {metric_column!r}
partition_cols = {partition_by!r}
ascending = {ascending!r}
top_n_per_group = {top_n_per_group!r}
grouped = df.groupby(group_cols, dropna=False)[metric_col].sum().reset_index()
if partition_cols:
    grouped['_rank'] = grouped.sort_values(metric_col, ascending=ascending).groupby(partition_cols).cumcount() + 1
    result = grouped[grouped['_rank'] <= top_n_per_group].drop(columns=['_rank']).sort_values(group_cols, ascending=True)
else:
    result = grouped.sort_values(metric_col, ascending=ascending).head(top_n_per_group)
""".strip()
        return f"""
group_cols = {group_by_columns!r}
metric_col = {metric_column!r}
ascending = {ascending!r}
top_n = {top_n!r}
result = df.groupby(group_cols, dropna=False)[metric_col].sum().reset_index().sort_values(metric_col, ascending=ascending).head(top_n)
""".strip()

    sort_by = str(plan.get("sort_by", metric_column)).strip() or metric_column
    return f"result = df.sort_values({sort_by!r}, ascending={ascending!r}).head({int(plan.get('top_n', 5))!r})"


def execute_analysis_query(query_text: str, data: List[Dict[str, Any]], source_tool_name: str = "") -> Dict[str, Any]:
    if not data:
        return {"success": False, "tool_name": "analyze_current_data", "source_tool_name": source_tool_name, "error_message": "분석할 데이터가 없습니다.", "data": []}

    plan, plan_source = build_analysis_plan(query_text, data)
    generated_code = compile_analysis_plan_to_code(plan)
    execution_result = execute_safe_dataframe_code(data=data, code=generated_code)
    if not execution_result.get("success"):
        return {
            "success": False,
            "tool_name": "analyze_current_data",
            "source_tool_name": source_tool_name,
            "error_message": execution_result.get("error_message", "코드 실행에 실패했습니다."),
            "data": [],
            "analysis_plan": plan,
            "generated_code": generated_code,
        }

    result_data = execution_result.get("data", [])
    return {
        "success": True,
        "tool_name": "analyze_current_data",
        "source_tool_name": source_tool_name,
        "data": result_data,
        "summary": f"현재 데이터 분석 결과: {len(result_data)}행",
        "analysis_plan": plan,
        "analysis_logic": plan_source,
        "generated_code": generated_code,
        "dataset_profile": _dataset_profile(data),
    }
