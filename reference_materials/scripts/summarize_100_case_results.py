from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import List

SCRIPT_DIR = Path(__file__).resolve().parent
REFERENCE_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = REFERENCE_DIR.parent
REPORTS_DIR = REFERENCE_DIR / "reports"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

REPORT_PATH = REPORTS_DIR / "CASE_100_TEST_REPORT.md"
SUMMARY_PATH = REPORTS_DIR / "CASE_100_SUMMARY.md"
QUALITY_PATH = REPORTS_DIR / "CASE_100_QUALITY_REVIEW.md"


@dataclass
class CaseRow:
    case_id: str
    scenario: str
    question: str
    tool: str
    summary: str
    answer: str
    table_html: str
    pandas_logic: str


class MainTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.table_depth = 0
        self.main_table_started = False
        self.current_main_row: List[str] | None = None
        self.current_cell: List[str] | None = None
        self.rows: List[List[str]] = []
        self.capture_cell = False

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.table_depth += 1
            if self.table_depth == 1:
                self.main_table_started = True
        if not self.main_table_started:
            return
        if self.table_depth == 1 and tag == "tr":
            self.current_main_row = []
        elif self.table_depth == 1 and tag in {"td", "th"} and self.current_main_row is not None:
            self.current_cell = []
            self.capture_cell = True
        elif self.capture_cell and self.current_cell is not None and tag == "pre":
            self.current_cell.append("\n")

    def handle_endtag(self, tag):
        if not self.main_table_started:
            return
        if self.table_depth == 1 and tag in {"td", "th"} and self.current_main_row is not None and self.current_cell is not None:
            self.current_main_row.append("".join(self.current_cell).strip())
            self.current_cell = None
            self.capture_cell = False
        elif self.table_depth == 1 and tag == "tr" and self.current_main_row is not None:
            if self.current_main_row and self.current_main_row[0] != "Case ID":
                self.rows.append(self.current_main_row)
            self.current_main_row = None
        if tag == "table":
            self.table_depth -= 1

    def handle_data(self, data):
        if self.capture_cell and self.current_cell is not None:
            self.current_cell.append(data)


def load_cases() -> List[CaseRow]:
    parser = MainTableParser()
    parser.feed(REPORT_PATH.read_text(encoding="utf-8"))
    rows: List[CaseRow] = []
    seen = set()
    for raw in parser.rows:
        if len(raw) < 8:
            continue
        case_id = raw[0]
        if not re.fullmatch(r"\d{3}", case_id):
            continue
        if case_id in seen:
            continue
        seen.add(case_id)
        rows.append(CaseRow(*raw[:8]))
    rows.sort(key=lambda row: int(row.case_id))
    return rows


def expected_column_from_question(question: str) -> str | None:
    mapping = {
        "라인별": "라인",
        "MODE별": "MODE",
        "mode별": "MODE",
        "DEN별": "DEN",
        "den별": "DEN",
        "TECH별": "TECH",
        "tech별": "TECH",
        "공정군별": "공정군",
        "공정별": "공정",
        "주요 불량 유형별": "주요불량유형",
    }
    for token, column in mapping.items():
        if token in question:
            return column
    return None


def classify_case(row: CaseRow) -> str:
    if row.tool in {"", "None"}:
        return "개선필요"
    if "실패" in row.answer or "실패" in row.summary or "오류" in row.answer:
        return "개선필요"
    if "현재 결과 테이블에 없습니다" in row.answer:
        return "성공"

    expected = expected_column_from_question(row.question)
    if expected and row.pandas_logic not in {"", "-"}:
        if expected not in row.pandas_logic and expected not in row.answer and expected not in row.table_html:
            return "애매"
    return "성공"


def summarize_cases(rows: List[CaseRow]) -> str:
    status_counter = Counter(classify_case(row) for row in rows)
    tool_counter = Counter(row.tool for row in rows)
    scenario_counter = Counter(row.scenario for row in rows)

    lines = [
        "# 100 Case Summary",
        "",
        f"- 총 케이스 수: {len(rows)}",
        f"- 성공: {status_counter['성공']}",
        f"- 애매: {status_counter['애매']}",
        f"- 개선필요: {status_counter['개선필요']}",
        "",
        "## Tool 분포",
    ]
    for tool, count in tool_counter.most_common():
        lines.append(f"- {tool}: {count}")

    lines.extend(["", "## 시나리오 분포"])
    for scenario, count in scenario_counter.items():
        lines.append(f"- {scenario}: {count}")

    lines.extend(["", "## 애매 케이스"])
    for row in rows:
        if classify_case(row) == "애매":
            lines.append(f"- Case {row.case_id}: {row.question}")
            lines.append(f"  - Tool: {row.tool}")
            lines.append(f"  - Summary: {row.summary}")

    lines.extend(["", "## 개선필요 케이스"])
    for row in rows:
        if classify_case(row) == "개선필요":
            lines.append(f"- Case {row.case_id}: {row.question}")
            lines.append(f"  - Tool: {row.tool}")
            lines.append(f"  - Summary: {row.summary}")
            lines.append(f"  - Answer: {row.answer[:200]}")

    return "\n".join(lines)


def quality_review(rows: List[CaseRow]) -> str:
    issues = defaultdict(list)

    for row in rows:
        expected = expected_column_from_question(row.question)
        if expected and row.pandas_logic not in {"", "-"}:
            if expected not in row.pandas_logic and expected not in row.answer and expected not in row.table_html:
                issues["질문 의도와 다른 그룹 기준"].append(row)
        if row.tool == "analyze_current_data" and row.pandas_logic in {"", "-"} and "현재 결과 테이블에 없습니다" not in row.answer:
            issues["후속 분석인데 pandas 로직이 없음"].append(row)
        if "실패" in row.answer or "오류" in row.answer:
            issues["응답에 오류 문구 포함"].append(row)

    lines = [
        "# 100 Case Quality Review",
        "",
        "이 문서는 실패는 아니지만 해석이 애매하거나 추가 보정이 필요한 케이스를 정리한 문서입니다.",
    ]

    if not issues:
        lines.append("")
        lines.append("- 명확한 문제를 자동 기준으로 찾지 못했습니다.")
        return "\n".join(lines)

    for issue, cases in issues.items():
        lines.extend(["", f"## {issue}"])
        unique_cases = []
        seen = set()
        for row in cases:
            if row.case_id in seen:
                continue
            seen.add(row.case_id)
            unique_cases.append(row)
        for row in unique_cases[:30]:
            lines.append(f"- Case {row.case_id}: {row.question}")
            lines.append(f"  - Tool: {row.tool}")
            lines.append(f"  - Pandas Logic: {row.pandas_logic or '-'}")
            lines.append(f"  - Answer Preview: {row.answer[:220]}")

    lines.extend(["", "## 해석 가이드"])
    lines.append("- `성공`: 질문 의도, tool 선택, 후속 분석 흐름이 전반적으로 자연스러운 케이스")
    lines.append("- `애매`: 실패는 아니지만 그룹 기준이나 해석 결과가 질문 의도와 완전히 맞는지 검토가 필요한 케이스")
    lines.append("- `개선필요`: 실행 실패, 오류 문구, 또는 pandas 분석 자체가 충분히 생성되지 않은 케이스")
    return "\n".join(lines)


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_cases()
    SUMMARY_PATH.write_text(summarize_cases(rows), encoding="utf-8")
    QUALITY_PATH.write_text(quality_review(rows), encoding="utf-8")
    print(f"Saved {SUMMARY_PATH}")
    print(f"Saved {QUALITY_PATH}")


if __name__ == "__main__":
    main()
