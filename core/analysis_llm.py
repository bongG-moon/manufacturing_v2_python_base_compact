import json
from typing import Any, Dict, List, Tuple

from langchain_core.messages import HumanMessage, SystemMessage

from .analysis_contracts import PreprocessPlan
from .analysis_helpers import dataset_profile
from .config import get_llm
from .domain_knowledge import build_domain_knowledge_prompt


def extract_text_from_response(content: Any) -> str:
    # 모델 SDK가 문자열 또는 파트 리스트를 반환할 수 있으므로
    # 이후 로직이 항상 문자열만 다루도록 여기서 통일합니다.
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
    # 모델이 JSON 앞뒤로 설명이나 코드펜스를 붙여도
    # 실제 JSON 블록만 잘라서 파싱하기 위한 함수입니다.
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
    # 후속 분석의 핵심 프롬프트입니다.
    # 현재 컬럼, 샘플 행, 도메인 지식을 함께 주고
    # LLM이 직접 pandas 코드를 작성하도록 유도합니다.
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
- If the user asks for average/mean, most common/mode, max, min, sum, count, or ratio by a group,
  use groupby + agg and create derived result columns directly in code.
- Treat Korean synonyms like "불량율" and "불량률" as the same concept.
- If a column named `defect_rate` exists and the user asks for "불량율" or "불량률",
  prefer aggregating `defect_rate` rather than `불량수량`.
- Treat expressions like "최빈 불량case", "최빈 불량 case", "대표 불량" as a request to summarize
  the most common value in column `주요불량유형` when that column exists.

Manufacturing domain hints:
{build_domain_knowledge_prompt()}

Dataset profile:
{json.dumps(profile, ensure_ascii=False)}

User question:
{query_text}
{retry_section}

Good aggregation example:
- If columns include `공정군`, `defect_rate`, `주요불량유형` and the user asks
  "공정군별로 그룹화해서 불량율이랑 최빈 불량case를 정리해줘"
  then a good code shape is:
  result = df.groupby('공정군', as_index=False).agg(
      평균_불량율=('defect_rate', 'mean'),
      최빈_불량유형=('주요불량유형', lambda s: s.mode().iloc[0] if not s.mode().empty else None)
  )

Good comparison example:
- If columns include `production` and `target` and the user asks for achievement rate by process,
  a good code shape is:
  grouped = df.groupby('공정', as_index=False).agg(production=('production', 'sum'), target=('target', 'sum'))
  grouped['achievement_rate'] = grouped['production'] / grouped['target']
  result = grouped

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
    # LLM 응답을 "실행기와 UI가 공통으로 이해할 수 있는 계획 객체"로 변환합니다.
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
