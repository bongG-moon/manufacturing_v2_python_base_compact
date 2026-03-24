from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from core.agent import run_agent


REPORT_PATH = Path("ISSUE_10_RETEST_REPORT.md")


@dataclass
class RetestCase:
    case_id: str
    title: str
    turns: List[str]
    expectation: str


CASES: List[RetestCase] = [
    RetestCase(
        "R01",
        "집계 후 없는 MODE 컬럼 요청",
        ["오늘 목표 보여줘", "공정군별로 그룹화해줘", "MODE별로 그룹화해줘"],
        "마지막 질문에서 MODE 컬럼이 현재 결과에 없다는 안내가 나와야 함",
    ),
    RetestCase(
        "R02",
        "집계 후 없는 라인 컬럼 요청",
        ["오늘 목표 보여줘", "공정군별로 그룹화해줘", "라인별로 정리해줘"],
        "마지막 질문에서 라인 컬럼이 현재 결과에 없다는 안내가 나와야 함",
    ),
    RetestCase(
        "R03",
        "현재 데이터에 아예 없는 담당자 컬럼 요청",
        ["오늘 생산량 보여줘", "담당자별로 정리해줘"],
        "담당자 컬럼이 없다는 안내가 나와야 함",
    ),
    RetestCase(
        "R04",
        "생산 데이터 공정군 그룹화 성공",
        ["오늘 생산량 보여줘", "공정군별로 그룹화해줘"],
        "공정군 기준 groupby가 정상 수행되어야 함",
    ),
    RetestCase(
        "R05",
        "생산 데이터 라인 그룹화 성공",
        ["오늘 생산량 보여줘", "라인별로 그룹화해줘"],
        "라인 기준 groupby가 정상 수행되어야 함",
    ),
    RetestCase(
        "R06",
        "복합 그룹 후 상위 N 성공",
        ["오늘 생산량 보여줘", "mode, den, tech별로 그룹화해주고 그룹별로 상위 3개씩만 보여줘"],
        "복합 groupby + top_n_per_group 이 정상 수행되어야 함",
    ),
    RetestCase(
        "R07",
        "불량 집계 후 없는 MODE 요청",
        ["오늘 불량 보여줘", "주요불량유형별로 그룹화해줘", "MODE별로 그룹화해줘"],
        "마지막 질문에서 MODE 컬럼이 현재 결과에 없다는 안내가 나와야 함",
    ),
    RetestCase(
        "R08",
        "WIP 집계 후 없는 MODE 요청",
        ["오늘 WIP 보여줘", "공정군별로 그룹화해줘", "MODE별로 그룹화해줘"],
        "마지막 질문에서 MODE 컬럼이 현재 결과에 없다는 안내가 나와야 함",
    ),
    RetestCase(
        "R09",
        "설비 집계 후 없는 라인 요청",
        ["오늘 설비 가동률 보여줘", "공정군별로 그룹화해줘", "라인별로 정리해줘"],
        "마지막 질문에서 라인 컬럼이 현재 결과에 없다는 안내가 나와야 함",
    ),
    RetestCase(
        "R10",
        "주제 전환 후 para 승계",
        ["오늘 LPDDR5X_8533 생산량 보여줘", "불량 보여줘"],
        "날짜와 제품 조건이 승계된 불량 조회가 정상 수행되어야 함",
    ),
]


def _run_case(case: RetestCase) -> Dict[str, Any]:
    chat_history: List[Dict[str, str]] = []
    context: Dict[str, Any] = {}
    current_data: Dict[str, Any] | None = None
    last_result: Dict[str, Any] | None = None

    for question in case.turns:
        last_result = run_agent(
            user_input=question,
            chat_history=chat_history,
            context=context,
            current_data=current_data,
        )
        current_data = last_result.get("current_data")
        chat_history.append({"role": "user", "content": question})
        chat_history.append({"role": "assistant", "content": last_result.get("response", "")})

        extracted = last_result.get("extracted_params", {})
        for field in ["date", "process_name", "product_name", "line_name", "mode", "den", "tech", "lead", "mcp_no"]:
            value = extracted.get(field)
            if value:
                context[field] = value

    first_result = (last_result or {}).get("tool_results", [{}])[0] if (last_result or {}).get("tool_results") else {}
    return {
        "case_id": case.case_id,
        "title": case.title,
        "turns": case.turns,
        "expectation": case.expectation,
        "response": (last_result or {}).get("response", ""),
        "tool_name": first_result.get("tool_name", ""),
        "error_message": first_result.get("error_message", ""),
        "summary": first_result.get("summary", ""),
        "generated_code": first_result.get("generated_code", ""),
        "data_rows": len(first_result.get("data", []) or []),
    }


def _judge(result: Dict[str, Any]) -> str:
    response = str(result["response"])
    expectation = str(result["expectation"])
    code = str(result["generated_code"])
    tool_name = str(result["tool_name"])

    if "없다는 안내" in expectation:
        return "PASS" if "현재 결과 테이블에 없습니다" in response else "FAIL"
    if "정상 수행" in expectation:
        if tool_name != "analyze_current_data" and "조회" not in expectation:
            return "FAIL"
        if "정상 수행" in expectation and result["error_message"]:
            return "FAIL"
        if "groupby" in expectation.lower() or "groupby" in code.lower():
            return "PASS" if code else "FAIL"
        return "PASS"
    if "승계" in expectation:
        return "PASS" if tool_name and not result["error_message"] else "FAIL"
    return "CHECK"


def _build_report(results: List[Dict[str, Any]]) -> str:
    lines = [
        "# Issue-Focused 10 Case Retest Report",
        "",
        "| Case ID | 제목 | 기대 결과 | 실제 Tool | 판정 | 응답 요약 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    for result in results:
        lines.append(
            f"| {result['case_id']} | {result['title']} | {result['expectation']} | {result['tool_name'] or '-'} | {_judge(result)} | {str(result['response']).replace('|', '/')} |"
        )

    lines.extend(["", "## 상세 결과"])
    for result in results:
        lines.extend(
            [
                "",
                f"### {result['case_id']} - {result['title']}",
                f"- 질문 흐름: {' -> '.join(result['turns'])}",
                f"- 기대 결과: {result['expectation']}",
                f"- 실제 Tool: {result['tool_name'] or '-'}",
                f"- 판정: {_judge(result)}",
                f"- Summary: {result['summary'] or '-'}",
                f"- Error: {result['error_message'] or '-'}",
                f"- Data Rows: {result['data_rows']}",
                f"- Pandas Code: `{result['generated_code'] or '-'}`",
                f"- Final Response: {result['response'] or '-'}",
            ]
        )

    return "\n".join(lines)


def main() -> None:
    results = [_run_case(case) for case in CASES]
    REPORT_PATH.write_text(_build_report(results), encoding="utf-8")
    print(f"Saved {REPORT_PATH}")
    for result in results:
        print(result["case_id"], _judge(result), result["title"])


if __name__ == "__main__":
    main()
