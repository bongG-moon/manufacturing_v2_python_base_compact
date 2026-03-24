import random
from typing import Any, Dict, List, Optional

from .number_format import format_summary_quantity


PROCESS_SPECS = [
    {"family": "ASSY_PREP", "공정": "incoming_sort", "라인": "ASSY-L1"},
    {"family": "ASSY_PREP", "공정": "wafer_bake", "라인": "ASSY-L1"},
    {"family": "ASSY_PREP", "공정": "plasma_clean", "라인": "ASSY-L2"},
    {"family": "DIE_ATTACH", "공정": "epoxy_dispense", "라인": "DA-L1"},
    {"family": "DIE_ATTACH", "공정": "die_place", "라인": "DA-L1"},
    {"family": "DIE_ATTACH", "공정": "post_cure", "라인": "DA-L2"},
    {"family": "WIRE_BOND", "공정": "first_bond", "라인": "WB-L1"},
    {"family": "WIRE_BOND", "공정": "stitch_bond", "라인": "WB-L1"},
    {"family": "WIRE_BOND", "공정": "pull_test", "라인": "WB-L2"},
    {"family": "FLIP_CHIP", "공정": "flip_place", "라인": "FC-L1"},
    {"family": "FLIP_CHIP", "공정": "reflow", "라인": "FC-L1"},
    {"family": "FLIP_CHIP", "공정": "underfill_cure", "라인": "FC-L2"},
    {"family": "MOLD", "공정": "transfer_mold", "라인": "MOLD-L1"},
    {"family": "MOLD", "공정": "post_mold_cure", "라인": "MOLD-L1"},
    {"family": "MOLD", "공정": "marking", "라인": "MOLD-L2"},
    {"family": "SINGULATION", "공정": "saw_cut", "라인": "SAW-L1"},
    {"family": "SINGULATION", "공정": "laser_saw", "라인": "SAW-L2"},
    {"family": "TEST", "공정": "final_test", "라인": "TEST-L1"},
    {"family": "TEST", "공정": "burn_in", "라인": "TEST-L2"},
    {"family": "PACK_OUT", "공정": "tray_pack", "라인": "PKG-L1"},
    {"family": "PACK_OUT", "공정": "ship_release", "라인": "PKG-L2"},
]

PRODUCTS = [
    {"MODE": "DDR5_6400", "DEN": "16Gb", "TECH": "WB", "LEAD": "96L", "MCP_NO": "MCP-DR5-016G-2H"},
    {"MODE": "DDR5_5600", "DEN": "32Gb", "TECH": "WB", "LEAD": "128L", "MCP_NO": "MCP-DR5-032G-2H"},
    {"MODE": "LPDDR5X_8533", "DEN": "64Gb", "TECH": "FC", "LEAD": "168B", "MCP_NO": "MCP-LP5X-064G-4H"},
    {"MODE": "UFS3.1", "DEN": "128Gb", "TECH": "MCP", "LEAD": "153B", "MCP_NO": "MCP-UFS-128G-3H"},
    {"MODE": "PMIC", "DEN": "8Gb", "TECH": "WLCSP", "LEAD": "48L", "MCP_NO": "PMIC-008G-R2"},
    {"MODE": "CIS", "DEN": "16Gb", "TECH": "FO", "LEAD": "64L", "MCP_NO": "CIS-016G-R1"},
]

PRODUCT_TECH_FAMILY = {
    "WB": {"ASSY_PREP", "DIE_ATTACH", "WIRE_BOND", "MOLD", "SINGULATION", "TEST", "PACK_OUT"},
    "FC": {"ASSY_PREP", "FLIP_CHIP", "MOLD", "SINGULATION", "TEST", "PACK_OUT"},
    "FO": {"ASSY_PREP", "FLIP_CHIP", "MOLD", "TEST", "PACK_OUT"},
    "WLCSP": {"ASSY_PREP", "FLIP_CHIP", "TEST", "PACK_OUT"},
    "MCP": {"ASSY_PREP", "DIE_ATTACH", "WIRE_BOND", "MOLD", "TEST", "PACK_OUT"},
}

DEFECTS_BY_FAMILY = {
    "ASSY_PREP": ["particle", "contamination", "moisture_exceed", "bake_fail"],
    "DIE_ATTACH": ["die_shift", "die_tilt", "void", "epoxy_bleed", "missing_die"],
    "WIRE_BOND": ["nsop", "lifted_bond", "heel_crack", "wire_sweep", "short_wire"],
    "FLIP_CHIP": ["bump_open", "bump_short", "underfill_void", "warpage", "bridge"],
    "MOLD": ["flash", "short_shot", "delamination", "mold_crack", "void"],
    "SINGULATION": ["chip_out", "edge_crack", "burr", "saw_mark"],
    "TEST": ["open_fail", "short_fail", "leakage_fail", "timing_fail", "iddq_fail"],
    "PACK_OUT": ["wrong_label", "tray_mixup", "tape_damage", "qty_mismatch"],
}

EQUIPMENT_SPECS = [
    {"설비ID": "DA-01", "설비명": "ASM Die Bonder", "라인": "DA-L1", "공정": "die_place", "family": "DIE_ATTACH"},
    {"설비ID": "DA-02", "설비명": "Datacon Epoxy Dispenser", "라인": "DA-L1", "공정": "epoxy_dispense", "family": "DIE_ATTACH"},
    {"설비ID": "WB-01", "설비명": "K&S Wire Bonder", "라인": "WB-L1", "공정": "first_bond", "family": "WIRE_BOND"},
    {"설비ID": "WB-03", "설비명": "K&S Stitch Bonder", "라인": "WB-L1", "공정": "stitch_bond", "family": "WIRE_BOND"},
    {"설비ID": "FC-02", "설비명": "Flip Chip Placer", "라인": "FC-L1", "공정": "flip_place", "family": "FLIP_CHIP"},
    {"설비ID": "MOLD-01", "설비명": "Transfer Mold Press", "라인": "MOLD-L1", "공정": "transfer_mold", "family": "MOLD"},
    {"설비ID": "SAW-02", "설비명": "Laser Saw", "라인": "SAW-L2", "공정": "laser_saw", "family": "SINGULATION"},
    {"설비ID": "TST-04", "설비명": "Final Test Handler", "라인": "TEST-L1", "공정": "final_test", "family": "TEST"},
    {"설비ID": "PKG-AOI-01", "설비명": "Pack-out AOI", "라인": "PKG-L1", "공정": "tray_pack", "family": "PACK_OUT"},
]

DOWNTIME_BY_FAMILY = {
    "DIE_ATTACH": ["PM overdue", "vacuum leak", "nozzle clog", "vision align fail"],
    "WIRE_BOND": ["capillary wear", "bond force drift", "recipe mismatch", "material shortage"],
    "FLIP_CHIP": ["reflow temp alarm", "underfill clog", "robot home error", "MES down"],
    "MOLD": ["mold clamp abnormal", "heater temp alarm", "changeover", "engineer call"],
    "SINGULATION": ["blade wear", "load port jam", "coolant low", "vision mark fail"],
    "TEST": ["handler jam", "socket wear", "contact fail", "lot hold by QA"],
    "PACK_OUT": ["label printer fault", "tray shortage", "scanner error", "qty mismatch check"],
}

WIP_STATUS_BY_FAMILY = {
    "DIE_ATTACH": ["QUEUED", "RUNNING", "WAIT_CURE", "WAIT_WB", "HOLD"],
    "WIRE_BOND": ["QUEUED", "RUNNING", "WAIT_AOI", "WAIT_TEST", "REWORK"],
    "FLIP_CHIP": ["QUEUED", "RUNNING", "WAIT_UNDERFILL", "WAIT_MOLD", "HOLD"],
    "MOLD": ["QUEUED", "RUNNING", "WAIT_POST_CURE", "WAIT_SAW", "REWORK"],
    "SINGULATION": ["QUEUED", "RUNNING", "WAIT_TEST", "SCRAP_HOLD"],
    "TEST": ["QUEUED", "RUNNING", "WAIT_RETEST", "WAIT_PACKOUT", "HOLD"],
    "PACK_OUT": ["QUEUED", "RUNNING", "WAIT_QA", "SHIP_READY", "COMPLETE"],
    "ASSY_PREP": ["QUEUED", "RUNNING", "WAIT_MATERIAL", "WAIT_EQUIP"],
}


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


def _match_any(target: str, allowed: Any) -> bool:
    values = _as_list(allowed)
    if not values:
        return True
    normalized_target = target.replace("/", "").lower()
    return any(str(item).replace("/", "").lower() in normalized_target for item in values)


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
        if not _match_any(str(row.get("공정", "")), params.get("process_name")):
            continue
        if not _match_any(str(row.get("라인", "")), params.get("line_name")):
            continue
        if not _matches_product(row, params.get("product_name")):
            continue
        if not _match_any(str(row.get("MODE", "")), params.get("mode")):
            continue
        if not _match_any(str(row.get("DEN", "")), params.get("den")):
            continue
        if not _match_any(str(row.get("TECH", "")), params.get("tech")):
            continue
        if not _match_any(str(row.get("LEAD", "")), params.get("lead")):
            continue
        if not _match_any(str(row.get("MCP_NO", "")), params.get("mcp_no")):
            continue
        filtered.append(row)
    return filtered


def _iter_valid_process_product_pairs():
    for spec in PROCESS_SPECS:
        for product in PRODUCTS:
            if spec["family"] in PRODUCT_TECH_FAMILY.get(product["TECH"], set()):
                yield spec, product


def get_production_data(params: Dict[str, Any]) -> Dict[str, Any]:
    date = str(params["date"])
    random.seed(_stable_seed(date))
    rows: List[Dict[str, Any]] = []
    for spec, product in _iter_valid_process_product_pairs():
        base = 3000 if spec["family"] in {"ASSY_PREP", "DIE_ATTACH"} else 2200
        variation = random.uniform(0.55, 1.15)
        qty = int(base * variation)
        rows.append(
            {
                "날짜": date,
                "공정": spec["공정"],
                "공정군": spec["family"],
                "MODE": product["MODE"],
                "DEN": product["DEN"],
                "TECH": product["TECH"],
                "LEAD": product["LEAD"],
                "MCP_NO": product["MCP_NO"],
                "라인": spec["라인"],
                "production": qty,
                "단위": "K",
            }
        )
    rows = _apply_common_filters(rows, params)
    total = sum(int(item["production"]) for item in rows)
    return {"success": True, "tool_name": "get_production_data", "data": rows, "summary": f"총 {len(rows)}건, 총 생산량 {format_summary_quantity(total)}"}


def get_target_data(params: Dict[str, Any]) -> Dict[str, Any]:
    date = str(params["date"])
    rows: List[Dict[str, Any]] = []
    for spec, product in _iter_valid_process_product_pairs():
        target = 3600 if spec["family"] in {"ASSY_PREP", "DIE_ATTACH"} else 2600
        rows.append(
            {
                "날짜": date,
                "공정": spec["공정"],
                "공정군": spec["family"],
                "MODE": product["MODE"],
                "DEN": product["DEN"],
                "TECH": product["TECH"],
                "LEAD": product["LEAD"],
                "MCP_NO": product["MCP_NO"],
                "라인": spec["라인"],
                "target": target,
                "단위": "K",
            }
        )
    rows = _apply_common_filters(rows, params)
    total = sum(int(item["target"]) for item in rows)
    return {"success": True, "tool_name": "get_target_data", "data": rows, "summary": f"총 {len(rows)}건, 총 목표량 {format_summary_quantity(total)}"}


def get_defect_rate(params: Dict[str, Any]) -> Dict[str, Any]:
    date = str(params["date"])
    random.seed(_stable_seed(date, 2000))
    rows: List[Dict[str, Any]] = []
    for spec, product in _iter_valid_process_product_pairs():
        inspection_qty = random.randint(2500, 8000)
        family = spec["family"]
        rate_floor = 0.004 if family in {"ASSY_PREP", "PACK_OUT"} else 0.008
        rate_ceiling = 0.018 if family in {"TEST", "WIRE_BOND"} else 0.028
        defect_qty = int(inspection_qty * random.uniform(rate_floor, rate_ceiling))
        defect_rate = round((defect_qty / inspection_qty) * 100, 2)
        rows.append(
            {
                "날짜": date,
                "공정": spec["공정"],
                "공정군": family,
                "MODE": product["MODE"],
                "DEN": product["DEN"],
                "TECH": product["TECH"],
                "LEAD": product["LEAD"],
                "MCP_NO": product["MCP_NO"],
                "inspection_qty": inspection_qty,
                "불량수량": defect_qty,
                "defect_rate": defect_rate,
                "주요불량유형": random.choice(DEFECTS_BY_FAMILY[family]),
            }
        )
    rows = _apply_common_filters(rows, params)
    avg_rate = sum(float(item["defect_rate"]) for item in rows) / len(rows) if rows else 0.0
    return {"success": True, "tool_name": "get_defect_rate", "data": rows, "summary": f"총 {len(rows)}건, 평균 불량률 {avg_rate:.2f}%"}


def get_equipment_status(params: Dict[str, Any]) -> Dict[str, Any]:
    date = str(params["date"])
    random.seed(_stable_seed(date, 3000))
    rows = []
    for equip in EQUIPMENT_SPECS:
        util = round(random.uniform(62, 97), 1)
        planned = 24.0
        actual = round(planned * util / 100, 1)
        rows.append(
            {
                "날짜": date,
                "설비ID": equip["설비ID"],
                "설비명": equip["설비명"],
                "라인": equip["라인"],
                "공정": equip["공정"],
                "공정군": equip["family"],
                "planned_hours": planned,
                "actual_hours": actual,
                "가동률": util,
                "비가동사유": "none" if util > 90 else random.choice(DOWNTIME_BY_FAMILY[equip["family"]]),
            }
        )
    rows = _apply_common_filters(rows, params)
    avg_util = sum(float(item["가동률"]) for item in rows) / len(rows) if rows else 0.0
    return {"success": True, "tool_name": "get_equipment_status", "data": rows, "summary": f"총 {len(rows)}대, 평균 가동률 {avg_util:.1f}%"}


def get_wip_status(params: Dict[str, Any]) -> Dict[str, Any]:
    date = str(params["date"])
    random.seed(_stable_seed(date, 4000))
    rows = []
    for spec, product in _iter_valid_process_product_pairs():
        wait_time = random.randint(10, 240)
        status = random.choice(WIP_STATUS_BY_FAMILY[spec["family"]])
        rows.append(
            {
                "날짜": date,
                "공정": spec["공정"],
                "공정군": spec["family"],
                "MODE": product["MODE"],
                "DEN": product["DEN"],
                "TECH": product["TECH"],
                "라인": spec["라인"],
                "재공수량": random.randint(150, 2600),
                "avg_wait_minutes": wait_time,
                "상태": status,
            }
        )
    rows = _apply_common_filters(rows, params)
    total = sum(int(item["재공수량"]) for item in rows)
    delayed = sum(1 for item in rows if item["상태"] in {"HOLD", "REWORK", "WAIT_QA", "WAIT_EQUIP", "WAIT_MATERIAL"})
    return {"success": True, "tool_name": "get_wip_status", "data": rows, "summary": f"총 {len(rows)}건, 총 WIP {format_summary_quantity(total)} EA, 대기/홀드 {delayed}건"}


RETRIEVAL_TOOL_MAP = {
    "production": get_production_data,
    "target": get_target_data,
    "defect": get_defect_rate,
    "equipment": get_equipment_status,
    "wip": get_wip_status,
}


def pick_retrieval_tool(query_text: str) -> str | None:
    query = str(query_text or "").lower()
    if any(token in query for token in ["설비", "가동률", "장비", "downtime"]):
        return "equipment"
    if any(token in query for token in ["wip", "재공", "대기", "hold"]):
        return "wip"
    if any(token in query for token in ["불량", "defect", "결함"]):
        return "defect"
    if any(token in query for token in ["목표", "target", "계획"]):
        return "target"
    if any(token in query for token in ["생산", "production", "실적"]):
        return "production"
    return None
