import random
from datetime import datetime
from typing import Any, Dict, List, Optional


PROCESSES = [
    "INPUT", "DS1", "DS2", "DS3", "DS4",
    "D/A1", "D/A2", "D/A3", "D/A4", "D/A5",
    "W/B1", "W/B2", "W/B3", "W/B4", "W/B5",
    "FCB1", "FCB2", "FCB3", "FCB4", "FCB5",
    "SHIP PKT",
]
PRODUCTS = [
    {"MODE": "DDR4", "DEN": "256G", "TECH": "LC", "LEAD": "128", "MCP_NO": "A-410"},
    {"MODE": "DDR4", "DEN": "512G", "TECH": "LC", "LEAD": "128", "MCP_NO": "A-411"},
    {"MODE": "DDR5", "DEN": "256G", "TECH": "LC", "LEAD": "192", "MCP_NO": "A-520"},
    {"MODE": "DDR5", "DEN": "512G", "TECH": "FO", "LEAD": "192", "MCP_NO": "A-521"},
    {"MODE": "DDR5", "DEN": "1T", "TECH": "FO", "LEAD": "256", "MCP_NO": "A-587"},
    {"MODE": "LPDDR5", "DEN": "256G", "TECH": "FC", "LEAD": "192", "MCP_NO": "A-630"},
    {"MODE": "LPDDR5", "DEN": "512G", "TECH": "FC", "LEAD": "256", "MCP_NO": "A-631"},
]
LINES = [
    {"라인": "A라인", "capacity": 5000},
    {"라인": "B라인", "capacity": 6000},
    {"라인": "C라인", "capacity": 4000},
]


def _stable_seed(date_text: str, offset: int = 0) -> int:
    normalized = str(date_text or "").strip()
    if normalized.isdigit():
        return int(normalized) + offset
    return sum(ord(ch) for ch in normalized) + offset


def _as_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    text = str(value).strip()
    return [text] if text else []


def _matches_process(process: str, process_name: Any) -> bool:
    allowed = _as_list(process_name)
    if not allowed:
        return True
    normalized_process = process.replace("/", "").upper()
    return any(item.replace("/", "").upper() in normalized_process for item in allowed)


def _matches_line(line_name: str, line_filter: Any) -> bool:
    allowed = _as_list(line_filter)
    if not allowed:
        return True
    return any(item in line_name for item in allowed)


def _matches_product(row: Dict[str, Any], product_name: Optional[str]) -> bool:
    if not product_name:
        return True
    query = str(product_name).strip().lower()
    searchable = [
        str(row.get("MODE", "")).lower(),
        str(row.get("DEN", "")).lower(),
        str(row.get("TECH", "")).lower(),
        str(row.get("MCP_NO", "")).lower(),
        str(row.get("LEAD", "")).lower(),
        f"{row.get('MODE', '')} {row.get('DEN', '')} {row.get('TECH', '')}".lower(),
    ]
    return any(query in value for value in searchable)


def _apply_common_filters(rows: List[Dict[str, Any]], params: Dict[str, Any]) -> List[Dict[str, Any]]:
    filtered = []
    for row in rows:
        if not _matches_process(str(row.get("공정", "")), params.get("process_name")):
            continue
        if not _matches_line(str(row.get("라인", "")), params.get("line_name")):
            continue
        if not _matches_product(row, params.get("product_name")):
            continue
        for field, column in [("mode", "MODE"), ("den", "DEN"), ("tech", "TECH"), ("lead", "LEAD"), ("mcp_no", "MCP_NO")]:
            allowed = _as_list(params.get(field))
            if allowed and str(row.get(column, "")).strip() not in allowed:
                break
        else:
            filtered.append(row)
    return filtered


def get_production_data(params: Dict[str, Any]) -> Dict[str, Any]:
    date = str(params["date"])
    random.seed(_stable_seed(date))
    rows: List[Dict[str, Any]] = []
    for process in PROCESSES:
        for product in PRODUCTS:
            for line in LINES:
                rows.append(
                    {
                        "날짜": date,
                        "공정": process,
                        "MODE": product["MODE"],
                        "DEN": product["DEN"],
                        "TECH": product["TECH"],
                        "LEAD": product["LEAD"],
                        "MCP_NO": product["MCP_NO"],
                        "라인": line["라인"],
                        "production": int(line["capacity"] * random.uniform(0.05, 0.16)),
                        "단위": "K",
                    }
                )
    rows = _apply_common_filters(rows, params)
    total = sum(int(item["production"]) for item in rows)
    return {"success": True, "tool_name": "get_production_data", "data": rows, "summary": f"총 {len(rows)}건, 총 생산량 {total:,} K"}


def get_target_data(params: Dict[str, Any]) -> Dict[str, Any]:
    date = str(params["date"])
    rows: List[Dict[str, Any]] = []
    for process in PROCESSES:
        for product in PRODUCTS:
            for line in LINES:
                rows.append(
                    {
                        "날짜": date,
                        "공정": process,
                        "MODE": product["MODE"],
                        "DEN": product["DEN"],
                        "TECH": product["TECH"],
                        "LEAD": product["LEAD"],
                        "MCP_NO": product["MCP_NO"],
                        "라인": line["라인"],
                        "target": line["capacity"],
                        "단위": "K",
                    }
                )
    rows = _apply_common_filters(rows, params)
    total = sum(int(item["target"]) for item in rows)
    return {"success": True, "tool_name": "get_target_data", "data": rows, "summary": f"총 {len(rows)}건, 총 목표량 {total:,} K"}


def get_defect_rate(params: Dict[str, Any]) -> Dict[str, Any]:
    date = str(params["date"])
    random.seed(_stable_seed(date, 2000))
    defect_types = ["surface", "wire", "bonding", "chip", "other"]
    rows: List[Dict[str, Any]] = []
    for process in PROCESSES:
        for product in PRODUCTS:
            inspection_qty = random.randint(3000, 8000)
            defect_qty = int(inspection_qty * random.uniform(0.005, 0.03))
            defect_rate = round((defect_qty / inspection_qty) * 100, 2)
            rows.append(
                {
                    "날짜": date,
                    "공정": process,
                    "MODE": product["MODE"],
                    "DEN": product["DEN"],
                    "TECH": product["TECH"],
                    "LEAD": product["LEAD"],
                    "MCP_NO": product["MCP_NO"],
                    "inspection_qty": inspection_qty,
                    "불량수량": defect_qty,
                    "defect_rate": defect_rate,
                    "주요불량유형": random.choice(defect_types),
                }
            )
    rows = _apply_common_filters(rows, params)
    avg_rate = sum(float(item["defect_rate"]) for item in rows) / len(rows) if rows else 0.0
    return {"success": True, "tool_name": "get_defect_rate", "data": rows, "summary": f"총 {len(rows)}건, 평균 불량률 {avg_rate:.2f}%"}


def get_equipment_status(params: Dict[str, Any]) -> Dict[str, Any]:
    date = str(params["date"])
    random.seed(_stable_seed(date, 3000))
    equipment_list = [
        {"설비ID": "EQ001", "설비명": "다이본더-1", "라인": "A라인", "공정": "D/A1"},
        {"설비ID": "EQ002", "설비명": "다이본더-2", "라인": "A라인", "공정": "D/A2"},
        {"설비ID": "EQ003", "설비명": "와이어본더-1", "라인": "B라인", "공정": "W/B1"},
        {"설비ID": "EQ004", "설비명": "와이어본더-2", "라인": "B라인", "공정": "W/B2"},
        {"설비ID": "EQ005", "설비명": "플립칩본더-1", "라인": "C라인", "공정": "FCB1"},
        {"설비ID": "EQ006", "설비명": "몰딩기-1", "라인": "C라인", "공정": "SHIP PKT"},
    ]
    rows = []
    for equip in equipment_list:
        util = round(random.uniform(60, 100), 1)
        planned = 24.0
        actual = round(planned * util / 100, 1)
        rows.append(
            {
                "날짜": date,
                "설비ID": equip["설비ID"],
                "설비명": equip["설비명"],
                "라인": equip["라인"],
                "공정": equip["공정"],
                "planned_hours": planned,
                "actual_hours": actual,
                "가동률": util,
                "비가동사유": "none" if util > 90 else random.choice(["maintenance", "material_wait", "changeover"]),
            }
        )
    rows = _apply_common_filters(rows, params)
    avg_util = sum(float(item["가동률"]) for item in rows) / len(rows) if rows else 0.0
    return {"success": True, "tool_name": "get_equipment_status", "data": rows, "summary": f"총 {len(rows)}대, 평균 가동률 {avg_util:.1f}%"}


def get_wip_status(params: Dict[str, Any]) -> Dict[str, Any]:
    date = str(params["date"])
    random.seed(_stable_seed(date, 4000))
    rows = []
    for process in PROCESSES:
        product = random.choice(PRODUCTS)
        line = random.choice(LINES)
        wait_time = random.randint(5, 120)
        rows.append(
            {
                "날짜": date,
                "공정": process,
                "MODE": product["MODE"],
                "DEN": product["DEN"],
                "TECH": product["TECH"],
                "라인": line["라인"],
                "재공수량": random.randint(200, 2000),
                "avg_wait_minutes": wait_time,
                "상태": "정상" if wait_time < 60 else "지연",
            }
        )
    rows = _apply_common_filters(rows, params)
    total = sum(int(item["재공수량"]) for item in rows)
    delayed = sum(1 for item in rows if item["상태"] == "지연")
    return {"success": True, "tool_name": "get_wip_status", "data": rows, "summary": f"총 {len(rows)}건, 총 WIP {total:,} EA, 지연 {delayed}건"}


RETRIEVAL_TOOL_MAP = {
    "production": get_production_data,
    "target": get_target_data,
    "defect": get_defect_rate,
    "equipment": get_equipment_status,
    "wip": get_wip_status,
}


def pick_retrieval_tool(query_text: str) -> str | None:
    query = str(query_text or "").lower()
    if any(token in query for token in ["설비", "가동률", "장비"]):
        return "equipment"
    if any(token in query for token in ["wip", "재공", "대기"]):
        return "wip"
    if any(token in query for token in ["불량", "defect"]):
        return "defect"
    if any(token in query for token in ["목표", "target"]):
        return "target"
    if any(token in query for token in ["생산", "production", "실적"]):
        return "production"
    return None
