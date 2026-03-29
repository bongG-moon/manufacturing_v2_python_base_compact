from typing import Any, Dict, List

from .data_tools import get_dataset_label, pick_retrieval_tools
from .filter_utils import normalize_text


RETRIEVAL_CUES = [
    "\uc870\ud68c",
    "\ubcf4\uc5ec",
    "\uac00\uc838\uc640",
    "\ubd88\ub7ec\uc640",
    "\ub370\uc774\ud130",
    "\ud604\ud669",
    "\uc624\ub298",
    "\uc5b4\uc81c",
    "\ub0a0\uc9dc",
]
FOLLOWUP_CUES = [
    "\uc0c1\uc704",
    "\ud558\uc704",
    "\uc815\ub82c",
    "\uadf8\ub8f9",
    "\uadf8\ub8f9\ud654",
    "\ube44\uad50",
    "\uc694\uc57d",
    "\ud544\ud130",
    "sort",
    "group",
    "compare",
]
CURRENT_RESULT_CUES = [
    "\ud604\uc7ac \uacb0\uacfc",
    "\uc774 \uacb0\uacfc",
    "\uc704 \uacb0\uacfc",
    "\ubc29\uae08",
    "\uadf8 \uacb0\uacfc",
    "current result",
]
RESET_CUES = ["\uc0c8\ub85c", "\ub2e4\uc2dc", "\ub2e4\ub978", "\uc2e0\uaddc"]


def _has_rows(current_data: Dict[str, Any] | None) -> bool:
    return bool(isinstance(current_data, dict) and isinstance(current_data.get("data"), list) and current_data.get("data"))


def _get_current_columns(current_data: Dict[str, Any] | None) -> List[str]:
    if not isinstance(current_data, dict):
        return []
    columns = current_data.get("columns", [])
    if isinstance(columns, list):
        return [str(column) for column in columns]
    return []


def classify_query_mode(user_input: str, current_data: Dict[str, Any] | None) -> Dict[str, Any]:
    normalized = normalize_text(user_input)
    retrieval_keys = pick_retrieval_tools(user_input)
    has_current_rows = _has_rows(current_data)
    current_columns = _get_current_columns(current_data)

    if not has_current_rows:
        return {
            "mode": "retrieval",
            "reason": "No current table is available, so the next turn must retrieve data.",
            "confidence": "high",
            "retrieval_keys": retrieval_keys,
        }

    retrieval_score = 0
    followup_score = 1

    if retrieval_keys:
        retrieval_score += len(retrieval_keys) * 3
    if any(token in normalized for token in RETRIEVAL_CUES):
        retrieval_score += 2
    if any(token in normalized for token in RESET_CUES):
        retrieval_score += 1

    if any(token in normalized for token in FOLLOWUP_CUES):
        followup_score += 2
    if any(token in normalized for token in CURRENT_RESULT_CUES):
        followup_score += 2
    if not retrieval_keys:
        followup_score += 1

    mentioned_columns = [column for column in current_columns if normalize_text(column) and normalize_text(column) in normalized]
    if mentioned_columns and not retrieval_keys:
        followup_score += 1

    if retrieval_score > followup_score:
        mode = "retrieval"
    elif followup_score > retrieval_score:
        mode = "followup_transform"
    else:
        mode = "retrieval" if retrieval_keys else "followup_transform"

    score_gap = abs(retrieval_score - followup_score)
    confidence = "high" if score_gap >= 3 else "medium" if score_gap >= 1 else "low"
    reason = (
        f"retrieval_score={retrieval_score}, followup_score={followup_score}, "
        f"retrieval_keys={retrieval_keys}, mentioned_columns={mentioned_columns}"
    )
    return {
        "mode": mode,
        "reason": reason,
        "confidence": confidence,
        "retrieval_keys": retrieval_keys,
    }


def should_ask_route_clarification(routing: Dict[str, Any], current_data: Dict[str, Any] | None) -> bool:
    return _has_rows(current_data) and routing.get("confidence") == "low"


def build_route_clarification_message(routing: Dict[str, Any], current_data: Dict[str, Any] | None) -> str:
    retrieval_keys = [str(key) for key in routing.get("retrieval_keys", [])]
    dataset_labels = [get_dataset_label(key) for key in retrieval_keys]
    current_columns = _get_current_columns(current_data)

    lines = ["이번 질문이 새 데이터 조회인지, 현재 결과 후속 분석인지 애매합니다."]
    if dataset_labels:
        lines.append(f"- 새 조회로 해석한 후보 데이터: {', '.join(dataset_labels)}")
    if current_columns:
        lines.append(f"- 현재 결과 컬럼: {', '.join(current_columns[:8])}")
    lines.append("다음처럼 짧게 다시 말해 주세요.")
    lines.append("- 새 조회: 오늘 목표 데이터 조회")
    lines.append("- 후속 분석: 현재 결과를 공정별 상위 3개로 정렬")
    return "\n".join(lines)
