from __future__ import annotations

import re
from dataclasses import dataclass
from html import unescape
from pathlib import Path
from typing import Iterable

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill

from summarize_100_case_results import CaseRow, load_cases


BASE_DIR = Path(__file__).resolve().parent
XLSX_PATH = BASE_DIR / "CASE_100_TEST_REPORT.xlsx"
DOCX_PATH = BASE_DIR / "CASE_100_TEST_REPORT.docx"


STATUS_SUCCESS = "성공"
STATUS_AMBIGUOUS = "애매"
STATUS_NEEDS_WORK = "개선필요"

GREEN_FILL = PatternFill(fill_type="solid", fgColor="E2F0D9")
YELLOW_FILL = PatternFill(fill_type="solid", fgColor="FFF2CC")
RED_FILL = PatternFill(fill_type="solid", fgColor="F4CCCC")
HEADER_FILL = PatternFill(fill_type="solid", fgColor="D9EAF7")


@dataclass
class ExportRow:
    case_id: str
    scenario: str
    question: str
    tool: str
    status: str
    reason: str
    summary: str
    answer: str
    table_top5: str
    pandas_logic: str


def _clean_text(value: str) -> str:
    text = unescape(value or "")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _flatten_table_html(table_html: str) -> str:
    if not table_html:
        return ""

    rows = re.findall(r"<tr>(.*?)</tr>", table_html, flags=re.IGNORECASE | re.DOTALL)
    if not rows:
        return _clean_text(table_html)

    flattened_rows: list[str] = []
    for row_html in rows:
        cells = re.findall(r"<t[dh]>(.*?)</t[dh]>", row_html, flags=re.IGNORECASE | re.DOTALL)
        cleaned_cells: list[str] = []
        for cell in cells:
            text = re.sub(r"<[^>]+>", " ", cell)
            text = _clean_text(text)
            if text:
                cleaned_cells.append(text)
        if cleaned_cells:
            flattened_rows.append(" | ".join(cleaned_cells))
    return "\n".join(flattened_rows)


def _expected_columns_from_question(question: str) -> list[str]:
    mapping = {
        "라인별": ["라인"],
        "MODE별": ["MODE"],
        "mode별": ["MODE"],
        "DEN별": ["DEN"],
        "den별": ["DEN"],
        "TECH별": ["TECH"],
        "tech별": ["TECH"],
        "공정군별": ["공정군"],
        "공정별": ["공정"],
        "주요 불량 유형별": ["주요불량유형"],
        "불량 유형별": ["주요불량유형"],
    }
    expected: list[str] = []
    for token, columns in mapping.items():
        if token in question:
            expected.extend(columns)
    return expected


def _contains_error_text(text: str) -> bool:
    tokens = [
        "지원하는 조회 또는 분석 범위를 벗어났습니다",
        "질문 분석 중 문제가 발생했습니다",
        "현재 결과 테이블에 없습니다",
        "Traceback",
        "KeyError",
        "실패",
        "오류",
    ]
    return any(token in text for token in tokens)


def _classify_case(case: CaseRow) -> tuple[str, str]:
    answer = _clean_text(case.answer)
    summary = _clean_text(case.summary)
    table_text = _flatten_table_html(case.table_html)
    pandas_logic = _clean_text(case.pandas_logic)
    question = _clean_text(case.question)
    tool = _clean_text(case.tool)

    if not tool or tool == "None":
        return STATUS_NEEDS_WORK, "실행된 tool 정보가 없어 실제 처리 경로를 확인하기 어렵습니다."

    if "현재 결과 테이블에 없습니다" in answer:
        return STATUS_SUCCESS, "없는 컬럼 요청을 명확하게 안내했습니다."

    if _contains_error_text(answer) or _contains_error_text(summary):
        return STATUS_NEEDS_WORK, "응답 또는 요약에 명시적인 오류/실패 문구가 포함되어 있습니다."

    if tool == "analyze_current_data" and not pandas_logic:
        return STATUS_NEEDS_WORK, "후속 분석인데 생성된 pandas 로직이 비어 있습니다."

    expected_columns = _expected_columns_from_question(question)
    searchable = "\n".join([answer, table_text, pandas_logic])
    for expected in expected_columns:
        if expected not in searchable:
            return STATUS_AMBIGUOUS, f"질문은 `{expected}` 기준 분석을 요구했지만 결과나 로직에서 그 기준이 분명하지 않습니다."

    if "상위" in question and tool == "analyze_current_data":
        if "head(" not in pandas_logic and "nlargest(" not in pandas_logic and "sort_values" not in pandas_logic:
            return STATUS_AMBIGUOUS, "질문은 상위 N개를 요구했지만 pandas 로직에서 상위 추출 의도가 충분히 드러나지 않습니다."

    return STATUS_SUCCESS, "질문 의도, 실행 tool, 결과 테이블, pandas 로직이 전반적으로 잘 연결됩니다."


def _build_export_rows() -> list[ExportRow]:
    export_rows: list[ExportRow] = []
    for case in load_cases():
        status, reason = _classify_case(case)
        export_rows.append(
            ExportRow(
                case_id=_clean_text(case.case_id),
                scenario=_clean_text(case.scenario),
                question=_clean_text(case.question),
                tool=_clean_text(case.tool),
                status=status,
                reason=reason,
                summary=_clean_text(case.summary),
                answer=_clean_text(case.answer),
                table_top5=_flatten_table_html(case.table_html),
                pandas_logic=_clean_text(case.pandas_logic),
            )
        )
    return export_rows


def _make_sheet_name(name: str, used_names: set[str]) -> str:
    base = re.sub(r"[:\\\\/?*\\[\\]]", "_", name).strip() or "Scenario"
    base = base[:31]
    candidate = base
    suffix = 2
    while candidate in used_names:
        suffix_text = f"_{suffix}"
        candidate = f"{base[:31 - len(suffix_text)]}{suffix_text}"
        suffix += 1
    used_names.add(candidate)
    return candidate


def _write_dataframe(writer: pd.ExcelWriter, sheet_name: str, df: pd.DataFrame) -> None:
    df.to_excel(writer, sheet_name=sheet_name, index=False)
    ws = writer.sheets[sheet_name]
    ws.auto_filter.ref = ws.dimensions
    ws.freeze_panes = "A2"

    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")

    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.fill = HEADER_FILL

    for column_cells in ws.columns:
        values = ["" if cell.value is None else str(cell.value) for cell in column_cells]
        width = min(max(len(max(values, key=len)) + 2, 12), 60)
        ws.column_dimensions[column_cells[0].column_letter].width = width


def _apply_status_colors(writer: pd.ExcelWriter, sheet_name: str, status_column_name: str = "상태") -> None:
    ws = writer.sheets[sheet_name]
    status_col_idx = None
    for idx, cell in enumerate(ws[1], start=1):
        if cell.value == status_column_name:
            status_col_idx = idx
            break

    if status_col_idx is None:
        return

    for row in range(2, ws.max_row + 1):
        status_value = ws.cell(row=row, column=status_col_idx).value
        fill = None
        if status_value == STATUS_SUCCESS:
            fill = GREEN_FILL
        elif status_value == STATUS_AMBIGUOUS:
            fill = YELLOW_FILL
        elif status_value == STATUS_NEEDS_WORK:
            fill = RED_FILL

        if fill:
            for col in range(1, ws.max_column + 1):
                ws.cell(row=row, column=col).fill = fill


def _build_summary_dataframe(export_rows: Iterable[ExportRow]) -> pd.DataFrame:
    rows = list(export_rows)
    total = len(rows)
    success = sum(1 for row in rows if row.status == STATUS_SUCCESS)
    ambiguous = sum(1 for row in rows if row.status == STATUS_AMBIGUOUS)
    needs_work = sum(1 for row in rows if row.status == STATUS_NEEDS_WORK)

    return pd.DataFrame(
        [
            {"구분": "총 케이스", "값": total},
            {"구분": "성공", "값": success},
            {"구분": "애매", "값": ambiguous},
            {"구분": "개선필요", "값": needs_work},
        ]
    )


def _build_reason_dataframe(export_rows: Iterable[ExportRow]) -> pd.DataFrame:
    rows = [
        {
            "Case ID": row.case_id,
            "상태": row.status,
            "시나리오": row.scenario,
            "질문": row.question,
            "사유": row.reason,
        }
        for row in export_rows
        if row.status != STATUS_SUCCESS
    ]
    return pd.DataFrame(rows)


def _write_excel() -> None:
    export_rows = _build_export_rows()
    all_cases_df = pd.DataFrame(
        [
            {
                "Case ID": row.case_id,
                "시나리오": row.scenario,
                "질문": row.question,
                "Tool": row.tool,
                "상태": row.status,
                "사유": row.reason,
                "Summary": row.summary,
                "답변 내용": row.answer,
                "테이블 상위 5개": row.table_top5,
                "Pandas Logic": row.pandas_logic,
            }
            for row in export_rows
        ]
    )

    summary_df = _build_summary_dataframe(export_rows)
    review_df = _build_reason_dataframe(export_rows)

    with pd.ExcelWriter(XLSX_PATH, engine="openpyxl") as writer:
        _write_dataframe(writer, "100_CASES", all_cases_df)
        _apply_status_colors(writer, "100_CASES")

        _write_dataframe(writer, "SUMMARY", summary_df)
        _write_dataframe(writer, "QUALITY_REVIEW", review_df)
        _apply_status_colors(writer, "QUALITY_REVIEW")

        used_sheet_names = {"100_CASES", "SUMMARY", "QUALITY_REVIEW"}
        scenarios = sorted({row.scenario for row in export_rows})
        for scenario in scenarios:
            scenario_df = all_cases_df[all_cases_df["시나리오"] == scenario].copy()
            sheet_name = _make_sheet_name(scenario, used_sheet_names)
            _write_dataframe(writer, sheet_name, scenario_df)
            _apply_status_colors(writer, sheet_name)


def _write_docx() -> bool:
    try:
        from docx import Document
    except Exception:
        return False

    export_rows = _build_export_rows()
    document = Document()
    document.add_heading("100 Case Test Report", level=1)
    document.add_paragraph("질문, 답변, 상위 5개 테이블, pandas 로직, 상태 판정과 사유를 한 문서에서 보기 쉽게 정리한 보고서입니다.")

    document.add_heading("Summary", level=2)
    summary_df = _build_summary_dataframe(export_rows)
    for _, row in summary_df.iterrows():
        document.add_paragraph(f"{row['구분']}: {row['값']}")

    document.add_heading("Quality Review", level=2)
    review_df = _build_reason_dataframe(export_rows)
    if review_df.empty:
        document.add_paragraph("애매 또는 개선필요 케이스가 없습니다.")
    else:
        for _, row in review_df.iterrows():
            document.add_paragraph(f"Case {row['Case ID']} | {row['상태']} | {row['질문']}")
            document.add_paragraph(f"사유: {row['사유']}")

    document.add_heading("Cases", level=2)
    for row in export_rows:
        document.add_heading(f"Case {row.case_id} - {row.scenario}", level=3)
        document.add_paragraph(f"질문: {row.question}")
        document.add_paragraph(f"Tool: {row.tool}")
        document.add_paragraph(f"상태: {row.status}")
        document.add_paragraph(f"사유: {row.reason}")
        document.add_paragraph(f"Summary: {row.summary}")
        document.add_paragraph(f"답변 내용: {row.answer}")
        document.add_paragraph("테이블 상위 5개")
        document.add_paragraph(row.table_top5 or "결과 없음")
        document.add_paragraph("Pandas Logic")
        document.add_paragraph(row.pandas_logic or "-")

    document.save(DOCX_PATH)
    return True


def main() -> None:
    _write_excel()
    docx_created = _write_docx()
    print(f"Saved Excel report to {XLSX_PATH}")
    if docx_created:
        print(f"Saved Word report to {DOCX_PATH}")
    else:
        print("Word report skipped: python-docx is not installed.")


if __name__ == "__main__":
    main()
