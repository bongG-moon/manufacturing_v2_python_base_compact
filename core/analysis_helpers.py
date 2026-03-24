import re
from typing import Any, Dict, List

from .analysis_contracts import DatasetProfile, PreprocessPlan
from .filter_utils import normalize_text


DIMENSION_ALIAS_MAP = {
    # 사용자는 "라인", "line", "공정군"처럼 다양한 표현을 섞어 쓰므로
    # 같은 의미의 축을 한 이름으로 정리한 표입니다.
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


def extract_columns(data: List[Dict[str, Any]]) -> List[str]:
    columns: List[str] = []
    for row in data:
        for key in row.keys():
            name = str(key)
            if name not in columns:
                columns.append(name)
    return columns


def dataset_profile(data: List[Dict[str, Any]]) -> DatasetProfile:
    # LLM에 전체 데이터 대신 컬럼 목록, 행 수, 샘플 몇 줄만 주어
    # 비용을 줄이고 프롬프트를 짧게 유지합니다.
    return {
        "columns": extract_columns(data),
        "row_count": len(data),
        "sample_rows": list(data[:3]),
    }


def find_metric_column(columns: List[str], query_text: str) -> str:
    normalized = normalize_text(query_text)
    candidates = ["production", "target", "defect_rate", "불량수량", "가동률", "재공수량"]

    for candidate in candidates:
        if normalize_text(candidate) in normalized and candidate in columns:
            return candidate

    for candidate in candidates:
        if candidate in columns:
            return candidate

    return columns[-1]


def find_requested_dimensions(query_text: str) -> List[str]:
    # "MODE별", "라인 기준", "공정군별" 같은 표현에서
    # 사용자가 어떤 축으로 묶고 싶은지 먼저 읽어냅니다.
    normalized_query = normalize_text(query_text)
    requested: List[str] = []

    for canonical_name, aliases in DIMENSION_ALIAS_MAP.items():
        if any(normalize_text(alias) in normalized_query for alias in aliases):
            requested.append(canonical_name)

    for pattern in [r"([A-Za-z가-힣0-9_]+)\s*별로", r"([A-Za-z가-힣0-9_]+)\s*기준"]:
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


def find_missing_dimensions(query_text: str, columns: List[str]) -> List[str]:
    # 현재 표에 없는 컬럼을 요청하면
    # LLM 코드 생성까지 가지 않고 바로 안내 문구를 주는 편이 더 낫습니다.
    available = set(columns)
    requested = find_requested_dimensions(query_text)
    return [column for column in requested if column not in available]


def format_missing_column_message(missing_columns: List[str], columns: List[str]) -> str:
    available_preview = ", ".join(columns[:12])
    missing_preview = ", ".join(missing_columns)
    return (
        f"요청하신 컬럼(조건) `{missing_preview}`은 현재 결과 테이블에 없습니다. "
        f"현재 사용할 수 있는 주요 컬럼은 `{available_preview}` 입니다."
    )


def parse_top_n(text: str, default: int = 5) -> int:
    match = re.search(r"(\d+)", str(text or ""))
    if match:
        return max(1, min(50, int(match.group(1))))
    return default


def minimal_fallback_plan(query_text: str, data: List[Dict[str, Any]]) -> PreprocessPlan:
    # LLM이 실패했을 때도 최소한의 정렬 + 상위 N 정도는 수행하도록
    # 아주 얇은 fallback 로직을 남겨 둡니다.
    columns = extract_columns(data)
    metric_column = find_metric_column(columns, query_text)
    sort_order = "asc" if any(token in normalize_text(query_text) for token in ["하위", "최소", "낮은"]) else "desc"
    top_n = parse_top_n(query_text, default=5)
    return {
        "intent": "기본 정렬 fallback",
        "operations": ["sort_values", "head"],
        "output_columns": columns,
        "sort_by": metric_column,
        "sort_order": sort_order,
        "top_n": top_n,
        "metric_column": metric_column,
        "warnings": ["LLM 코드 생성에 실패해 최소 fallback 로직을 사용했습니다."],
        "source": "fallback",
        "code": (
            f"result = df.sort_values(by={metric_column!r}, "
            f"ascending={str(sort_order == 'asc')}).head({top_n})"
        ),
    }


def validate_plan_columns(plan: PreprocessPlan, columns: List[str]) -> List[str]:
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


def build_transformation_summary(
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
