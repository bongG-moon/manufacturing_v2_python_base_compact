import json
from datetime import datetime, timedelta
from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage

from .analysis_contracts import RequiredParams
from .config import SYSTEM_PROMPT, get_llm
from .domain_knowledge import build_domain_knowledge_prompt


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


def _parse_json_block(text: str) -> Dict[str, Any]:
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


def _inherit_from_context(extracted_params: RequiredParams, context: Dict[str, Any] | None) -> RequiredParams:
    if not isinstance(context, dict):
        return extracted_params
    if not extracted_params.get("date") and context.get("date"):
        extracted_params["date"] = context["date"]
        extracted_params["date_inherited"] = True
    for field in ["process_name", "product_name", "line_name", "mode", "den", "tech", "lead", "mcp_no"]:
        if extracted_params.get(field):
            continue
        if not context.get(field):
            continue
        extracted_params[field] = context[field]
        inherited_key = "process_inherited" if field == "process_name" else "product_inherited" if field == "product_name" else "line_inherited" if field == "line_name" else f"{field}_inherited"
        extracted_params[inherited_key] = True
    return extracted_params


def _fallback_date(text: str) -> str | None:
    lower = str(text or "").lower()
    now = datetime.now()
    if "오늘" in lower or "today" in lower:
        return now.strftime("%Y%m%d")
    if "어제" in lower or "yesterday" in lower:
        return (now - timedelta(days=1)).strftime("%Y%m%d")
    return None


def resolve_required_params(
    user_input: str,
    chat_history_text: str,
    current_data_columns: List[str],
    context: Dict[str, Any] | None = None,
) -> RequiredParams:
    today = datetime.now().strftime("%Y%m%d")
    domain_prompt = build_domain_knowledge_prompt()
    prompt = f"""You are extracting retrieval parameters for a manufacturing data assistant.
Return JSON only.

Rules:
- Extract only retrieval-safe fields and grouping hints.
- Normalize today/yesterday into YYYYMMDD.
- Use domain knowledge to expand process groups.
- If a value is not explicit, return null.

Domain knowledge:
{domain_prompt}

Recent chat:
{chat_history_text}

Available current-data columns:
{", ".join(current_data_columns) if current_data_columns else "(none)"}

Today's date:
{today}

User question:
{user_input}

Return only:
{{
  "date": "YYYYMMDD or null",
  "process": ["value"] or null,
  "product_name": "string or null",
  "line_name": "string or null",
  "mode": ["value"] or null,
  "den": ["value"] or null,
  "tech": ["value"] or null,
  "lead": "string or null",
  "mcp_no": "string or null",
  "group_by": "column or null"
}}"""

    parsed: Dict[str, Any] = {}
    try:
        llm = get_llm()
        response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])
        parsed = _parse_json_block(_extract_text_from_response(response.content))
    except Exception:
        parsed = {}

    extracted_params: RequiredParams = {
        "date": parsed.get("date") or _fallback_date(user_input),
        "process_name": parsed.get("process"),
        "product_name": parsed.get("product_name"),
        "line_name": parsed.get("line_name"),
        "group_by": parsed.get("group_by"),
        "metrics": [],
        "mode": parsed.get("mode"),
        "den": parsed.get("den"),
        "tech": parsed.get("tech"),
        "lead": parsed.get("lead"),
        "mcp_no": parsed.get("mcp_no"),
    }
    return _inherit_from_context(extracted_params, context)
