import json
from typing import Any, Dict, List, Tuple

from langchain_core.messages import HumanMessage, SystemMessage

from .analysis_contracts import PreprocessPlan
from .analysis_schema import dataset_profile
from .config import get_llm
from .domain_knowledge import build_domain_knowledge_prompt


def extract_text_from_response(content: Any) -> str:
    # LLM SDKs can return either plain text or a list of text parts.
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


def extract_json_payload(text: str) -> Dict[str, Any]:
    # We ask the model for JSON, but still defensively strip code fences.
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


def build_llm_prompt(
    query_text: str,
    data: List[Dict[str, Any]],
    retry_error: str = "",
    previous_code: str = "",
) -> str:
    # The prompt gives the model everything it needs to write pandas directly:
    # user question, current schema, sample rows, and domain hints.
    profile = dataset_profile(data)
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


def build_llm_plan(
    query_text: str,
    data: List[Dict[str, Any]],
    retry_error: str = "",
    previous_code: str = "",
) -> Tuple[PreprocessPlan | None, str]:
    # Convert the LLM JSON into one consistent internal plan object.
    try:
        llm = get_llm()
        prompt = build_llm_prompt(query_text, data, retry_error=retry_error, previous_code=previous_code)
        response = llm.invoke(
            [
                SystemMessage(content="Generate safe pandas dataframe transformation code."),
                HumanMessage(content=prompt),
            ]
        )
        parsed = extract_json_payload(extract_text_from_response(response.content))
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
