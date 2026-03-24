from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any, Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.agent import run_agent
from core.number_format import format_rows_for_display


@dataclass
class Scenario:
    name: str
    turns: List[str]


SCENARIOS: List[Scenario] = [
    Scenario("생산 기본 흐름", ["오늘 생산량 보여줘", "상위 5개만 보여줘", "공정군별로 그룹화해줘", "MODE별로 그룹화해줘", "라인별로 그룹화해줘"]),
    Scenario("생산 공정군 필터", ["오늘 DIE_ATTACH 공정 생산량 보여줘", "상위 5개만 보여줘", "공정별로 그룹화해줘", "라인별로 그룹화해줘", "MODE별로 그룹화해줘"]),
    Scenario("생산 제품 필터", ["오늘 LPDDR5X_8533 생산량 보여줘", "공정군별로 그룹화해줘", "상위 5개만 보여줘", "TECH별로 그룹화해줘", "라인별로 그룹화해줘"]),
    Scenario("생산 조건 후 재필터", ["오늘 생산량 보여줘", "LPDDR5X_8533만 보여줘", "공정군별로 그룹화해줘", "상위 5개만 보여줘", "공정별로 그룹화해줘"]),
    Scenario("생산 복합 그룹", ["오늘 생산량 보여줘", "mode, den, tech별로 그룹화해주고 그룹별로 상위 3개씩만 보여줘", "공정군별로 그룹화해줘", "상위 5개만 보여줘", "라인별로 그룹화해줘"]),
    Scenario("목표 기본 흐름", ["오늘 목표 보여줘", "상위 5개만 보여줘", "공정군별로 그룹화해줘", "MODE별로 그룹화해줘", "라인별로 그룹화해줘"]),
    Scenario("목표 공정군 필터", ["오늘 TEST 공정 목표 보여줘", "상위 5개만 보여줘", "공정별로 그룹화해줘", "라인별로 그룹화해줘", "MODE별로 그룹화해줘"]),
    Scenario("목표 제품 필터", ["오늘 UFS3.1 목표 보여줘", "공정군별로 그룹화해줘", "상위 5개만 보여줘", "TECH별로 그룹화해줘", "라인별로 그룹화해줘"]),
    Scenario("불량 기본 흐름", ["오늘 불량 보여줘", "불량률 높은 순으로 정렬해줘", "주요불량유형별로 그룹화해줘", "공정군별로 그룹화해줘", "상위 5개만 보여줘"]),
    Scenario("불량 공정군 필터", ["오늘 WIRE_BOND 공정 불량 보여줘", "불량률 높은 순으로 정렬해줘", "주요불량유형별로 그룹화해줘", "상위 5개만 보여줘", "MODE별로 그룹화해줘"]),
    Scenario("불량 제품 필터", ["오늘 LPDDR5X_8533 불량 보여줘", "불량률 높은 순으로 정렬해줘", "주요불량유형별로 그룹화해줘", "공정군별로 그룹화해줘", "상위 5개만 보여줘"]),
    Scenario("불량 주제 전환", ["오늘 LPDDR5X_8533 생산량 보여줘", "불량 보여줘", "불량률 높은 순으로 정렬해줘", "공정군별로 그룹화해줘", "상위 5개만 보여줘"]),
    Scenario("설비 기본 흐름", ["오늘 설비 가동률 보여줘", "가동률 낮은 순으로 정렬해줘", "공정군별로 그룹화해줘", "라인별로 그룹화해줘", "상위 5개만 보여줘"]),
    Scenario("설비 공정군 필터", ["오늘 TEST 설비 상태 보여줘", "가동률 낮은 순으로 정렬해줘", "라인별로 그룹화해줘", "상위 5개만 보여줘", "공정별로 그룹화해줘"]),
    Scenario("설비 주제 전환", ["오늘 TEST 공정 WIP 보여줘", "설비 상태도 보여줘", "가동률 낮은 순으로 정렬해줘", "상위 5개만 보여줘", "라인별로 그룹화해줘"]),
    Scenario("WIP 기본 흐름", ["오늘 WIP 보여줘", "재공수량 상위 10개만 보여줘", "공정군별로 그룹화해줘", "MODE별로 그룹화해줘", "라인별로 그룹화해줘"]),
    Scenario("WIP 공정군 필터", ["오늘 TEST 공정 WIP 보여줘", "재공수량 상위 10개만 보여줘", "공정별로 그룹화해줘", "상위 5개만 보여줘", "MODE별로 그룹화해줘"]),
    Scenario("WIP 상태성 후속", ["오늘 WIP 보여줘", "HOLD 상태만 보여줘", "공정군별로 그룹화해줘", "재공수량 상위 5개만 보여줘", "라인별로 그룹화해줘"]),
    Scenario("WIP 제품 필터", ["오늘 LPDDR5X_8533 WIP 보여줘", "재공수량 상위 10개만 보여줘", "공정군별로 그룹화해줘", "상위 5개만 보여줘", "라인별로 그룹화해줘"]),
    Scenario("혼합 전환 종합", ["오늘 생산량 보여줘", "LPDDR5X_8533만 보여줘", "불량 보여줘", "불량률 높은 순으로 정렬해줘", "공정군별로 그룹화해줘"]),
]


def _sync_context(context: Dict[str, Any], extracted_params: Dict[str, Any]) -> None:
    for field in ["date", "process_name", "product_name", "line_name", "mode", "den", "tech", "lead", "mcp_no"]:
        value = extracted_params.get(field)
        if value:
            context[field] = value


def _as_html_table(rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return "<div>결과 없음</div>"

    display_rows, _ = format_rows_for_display(rows[:5])
    if not display_rows:
        return "<div>결과 없음</div>"

    columns = list(display_rows[0].keys())
    parts = ["<table border='1' cellspacing='0' cellpadding='4'>", "<thead><tr>"]
    for column in columns:
        parts.append(f"<th>{escape(str(column))}</th>")
    parts.append("</tr></thead><tbody>")
    for row in display_rows:
        parts.append("<tr>")
        for column in columns:
            parts.append(f"<td>{escape(str(row.get(column, '')))}</td>")
        parts.append("</tr>")
    parts.append("</tbody></table>")
    return "".join(parts)


def _render_result_row(case_id: int, scenario_name: str, question: str, result: Dict[str, Any]) -> str:
    tool_results = result.get("tool_results", [])
    first_result = tool_results[0] if tool_results else {}
    answer = result.get("response", "")
    pandas_logic = first_result.get("generated_code", "") if first_result.get("tool_name") == "analyze_current_data" else "-"
    top_rows = first_result.get("data", []) if isinstance(first_result.get("data"), list) else []
    table_html = _as_html_table(top_rows)
    tool_name = first_result.get("tool_name", "-")
    summary = first_result.get("summary", "")

    return (
        "<tr>"
        f"<td>{case_id:03d}</td>"
        f"<td>{escape(scenario_name)}</td>"
        f"<td>{escape(question)}</td>"
        f"<td>{escape(tool_name)}</td>"
        f"<td>{escape(summary)}</td>"
        f"<td>{escape(answer)}</td>"
        f"<td>{table_html}</td>"
        f"<td><pre>{escape(pandas_logic)}</pre></td>"
        "</tr>"
    )


def _run_scenario(scenario: Scenario, start_case_id: int) -> tuple[list[str], int]:
    context: Dict[str, Any] = {}
    current_data: Dict[str, Any] | None = None
    chat_history: List[Dict[str, str]] = []
    rows: List[str] = []
    case_id = start_case_id

    for question in scenario.turns:
        result = run_agent(
            user_input=question,
            chat_history=chat_history,
            context=context,
            current_data=current_data,
        )
        rows.append(_render_result_row(case_id, scenario.name, question, result))

        _sync_context(context, result.get("extracted_params", {}))
        current_data = result.get("current_data")
        chat_history.append({"role": "user", "content": question})
        chat_history.append({"role": "assistant", "content": result.get("response", "")})
        case_id += 1

    return rows, case_id


def build_report() -> str:
    parts = [
        "# 100 Case Test Report",
        "",
        "- 총 100개 질문 케이스를 순차 실행한 결과입니다.",
        "- 컬럼: Case ID / 시나리오 / 질문 / Tool / Summary / 답변 / 테이블 상위 5개 / Pandas Logic",
        "",
        "<table border='1' cellspacing='0' cellpadding='6'>",
        "<thead><tr>"
        "<th>Case ID</th>"
        "<th>시나리오</th>"
        "<th>질문</th>"
        "<th>Tool</th>"
        "<th>Summary</th>"
        "<th>답변 내용</th>"
        "<th>테이블 상위 5개</th>"
        "<th>Pandas Logic</th>"
        "</tr></thead><tbody>",
    ]

    next_case_id = 1
    for scenario in SCENARIOS:
        rows, next_case_id = _run_scenario(scenario, next_case_id)
        parts.extend(rows)

    parts.append("</tbody></table>")
    return "\n".join(parts)


def write_report_incrementally(output_path: Path) -> None:
    header = [
        "# 100 Case Test Report",
        "",
        "- 총 100개 질문 케이스를 순차 실행한 결과입니다.",
        "- 컬럼: Case ID / 시나리오 / 질문 / Tool / Summary / 답변 / 테이블 상위 5개 / Pandas Logic",
        "",
        "<table border='1' cellspacing='0' cellpadding='6'>",
        "<thead><tr>"
        "<th>Case ID</th>"
        "<th>시나리오</th>"
        "<th>질문</th>"
        "<th>Tool</th>"
        "<th>Summary</th>"
        "<th>답변 내용</th>"
        "<th>테이블 상위 5개</th>"
        "<th>Pandas Logic</th>"
        "</tr></thead><tbody>",
    ]
    output_path.write_text("\n".join(header) + "\n", encoding="utf-8")

    scenario_jobs: List[tuple[Scenario, int]] = []
    next_case_id = 1
    for scenario in SCENARIOS:
        scenario_jobs.append((scenario, next_case_id))
        next_case_id += len(scenario.turns)

    collected_rows: Dict[int, List[str]] = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(_run_scenario, scenario, start_case_id): start_case_id
            for scenario, start_case_id in scenario_jobs
        }
        for future in as_completed(futures):
            start_case_id = futures[future]
            rows, _ = future.result()
            collected_rows[start_case_id] = rows
            print(f"completed scenario starting at case {start_case_id:03d}")

    with output_path.open("a", encoding="utf-8") as f:
        for start_case_id in sorted(collected_rows.keys()):
            f.write("\n".join(collected_rows[start_case_id]))
            f.write("\n")

    with output_path.open("a", encoding="utf-8") as f:
        f.write("</tbody></table>\n")


def main() -> None:
    output_path = Path("CASE_100_TEST_REPORT.md")
    write_report_incrementally(output_path)
    print(f"Saved report to {output_path}")


if __name__ == "__main__":
    main()
