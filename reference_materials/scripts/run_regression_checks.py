import sys
from pathlib import Path
from typing import Any, Dict, List

SCRIPT_DIR = Path(__file__).resolve().parent
REFERENCE_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = REFERENCE_DIR.parent
REPORTS_DIR = REFERENCE_DIR / "reports"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.agent import run_agent


SCENARIOS: Dict[str, List[str]] = {
    "기본 조회": ["오늘 생산량 보여줘"],
    "공정군 도메인 추출": ["오늘 WIRE_BOND 공정 불량 보여줘"],
    "후속 그룹 분석": ["오늘 생산량 보여줘", "mode, den, tech별로 그룹화해주고 그룹별로 상위 3개씩만 보여줘"],
    "필터 후 재분석": ["오늘 생산량 보여줘", "LPDDR5X_8533만 보여줘", "공정군별로 그룹화해줘"],
    "주제 전환과 para 승계": ["오늘 LPDDR5X_8533 생산량 보여줘", "불량 보여줘"],
    "다른 데이터 주제 연결": ["오늘 TEST 공정 WIP 보여줘", "설비 상태도 보여줘"],
    "정렬 분석": ["오늘 불량 보여줘", "불량률 높은 순으로 정렬해줘"],
    "상위 N 분석": ["오늘 WIP 보여줘", "재공수량 상위 10개만 보여줘"],
}


def _sync_context(context: Dict[str, Any], extracted_params: Dict[str, Any]) -> None:
    for field in ["date", "process_name", "product_name", "line_name", "mode", "den", "tech", "lead", "mcp_no"]:
        value = extracted_params.get(field)
        if value:
            context[field] = value


def _run_turns(turns: List[str]) -> List[Dict[str, Any]]:
    context: Dict[str, Any] = {}
    current_data: Dict[str, Any] | None = None
    chat_history: List[Dict[str, str]] = []
    results: List[Dict[str, Any]] = []

    for user_input in turns:
        result = run_agent(
            user_input=user_input,
            chat_history=chat_history,
            context=context,
            current_data=current_data,
        )
        tool_results = result.get("tool_results", [])
        first_result = tool_results[0] if tool_results else {}

        results.append(
            {
                "question": user_input,
                "tool_name": first_result.get("tool_name"),
                "row_count": len(first_result.get("data", [])) if first_result.get("data") else 0,
                "summary": first_result.get("summary", ""),
                "extracted_params": result.get("extracted_params", {}),
                "applied_params": first_result.get("applied_params", {}),
                "analysis_plan": first_result.get("analysis_plan", {}),
                "generated_code": first_result.get("generated_code", ""),
                "response_preview": result.get("response", "")[:280].replace("\n", " "),
            }
        )

        _sync_context(context, result.get("extracted_params", {}))
        current_data = result.get("current_data")
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": result.get("response", "")})

    return results


def _render_report() -> str:
    lines: List[str] = ["# Regression Check Report", ""]
    for scenario_name, turns in SCENARIOS.items():
        lines.append(f"## {scenario_name}")
        for item in _run_turns(turns):
            lines.append(f"### 질문: {item['question']}")
            lines.append(f"- tool: {item['tool_name']}")
            lines.append(f"- row_count: {item['row_count']}")
            lines.append(f"- summary: {item['summary']}")
            lines.append(f"- extracted_params: {item['extracted_params']}")
            if item["applied_params"]:
                lines.append(f"- applied_params: {item['applied_params']}")
            if item["analysis_plan"]:
                lines.append(f"- analysis_plan: {item['analysis_plan']}")
            if item["generated_code"]:
                lines.append("```python")
                lines.append(item["generated_code"])
                lines.append("```")
            lines.append(f"- response_preview: {item['response_preview']}")
            lines.append("")
    return "\n".join(lines)


def main() -> None:
    report = _render_report()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = REPORTS_DIR / "REGRESSION_CHECK_REPORT.md"
    output_path.write_text(report, encoding="utf-8")
    print(f"Saved report to {output_path}")


if __name__ == "__main__":
    main()
