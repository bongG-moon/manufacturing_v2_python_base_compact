import random
from datetime import datetime
from typing import Any, Dict, List, Optional

from .dataset_contracts import get_dataset_label as get_contract_dataset_label
from .domain_knowledge import PROCESS_SPECS, PRODUCTS, PRODUCT_TECH_FAMILY
from .domain_registry import get_dataset_keyword_map
from .number_format import format_summary_quantity

DATASET_METADATA = get_dataset_keyword_map()

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

YIELD_FAIL_BINS_BY_FAMILY = {
    "ASSY_PREP": ["visual_fail", "contamination", "marking_ng"],
    "DIE_ATTACH": ["die_shift", "void_fail", "attach_miss"],
    "WIRE_BOND": ["nsop", "wire_open", "bond_lift"],
    "FLIP_CHIP": ["bump_open", "bridge", "warpage"],
    "MOLD": ["package_crack", "delamination", "void"],
    "SINGULATION": ["edge_crack", "chip_out", "burr"],
    "TEST": ["timing_fail", "leakage_fail", "iddq_fail"],
    "PACK_OUT": ["label_ng", "tray_mix", "packing_ng"],
}

HOLD_REASONS_BY_FAMILY = {
    "ASSY_PREP": ["incoming inspection hold", "material moisture check", "wafer ID mismatch"],
    "DIE_ATTACH": ["epoxy cure verification", "die attach void review", "recipe approval hold"],
    "WIRE_BOND": ["bond pull outlier", "capillary replacement hold", "loop height review"],
    "FLIP_CHIP": ["bump coplanarity review", "reflow profile hold", "underfill void review"],
    "MOLD": ["package crack review", "mold flash review", "compound trace hold"],
    "SINGULATION": ["edge crack review", "blade wear inspection", "chip out hold"],
    "TEST": ["yield review hold", "customer spec check", "retest approval"],
    "PACK_OUT": ["label verification", "shipping spec hold", "QA final release"],
}

HOLD_OWNERS = ["PE", "PIE", "QA", "Process", "Equipment", "Customer Quality"]

SCRAP_REASONS_BY_FAMILY = {
    "ASSY_PREP": ["incoming damage", "contamination", "moisture exposure"],
    "DIE_ATTACH": ["die crack", "missing die", "epoxy overflow"],
    "WIRE_BOND": ["wire short", "bond lift", "pad damage"],
    "FLIP_CHIP": ["bump bridge", "underfill void", "warpage"],
    "MOLD": ["mold crack", "delamination", "void"],
    "SINGULATION": ["chip out", "edge crack", "burr"],
    "TEST": ["electrical fail", "burn-in reject", "leakage fail"],
    "PACK_OUT": ["packing damage", "label NG", "qty mismatch"],
}

RECIPE_BASE_BY_FAMILY = {
    "ASSY_PREP": {"temp_c": 145, "pressure_kpa": 95, "process_time_sec": 420},
    "DIE_ATTACH": {"temp_c": 168, "pressure_kpa": 112, "process_time_sec": 510},
    "WIRE_BOND": {"temp_c": 132, "pressure_kpa": 88, "process_time_sec": 360},
    "FLIP_CHIP": {"temp_c": 238, "pressure_kpa": 126, "process_time_sec": 470},
    "MOLD": {"temp_c": 176, "pressure_kpa": 140, "process_time_sec": 780},
    "SINGULATION": {"temp_c": 72, "pressure_kpa": 65, "process_time_sec": 310},
    "TEST": {"temp_c": 35, "pressure_kpa": 0, "process_time_sec": 900},
    "PACK_OUT": {"temp_c": 28, "pressure_kpa": 0, "process_time_sec": 260},
}

METROLOGY_ITEMS_BY_FAMILY = {
    "ASSY_PREP": ["surface_particles", "wafer_warp"],
    "DIE_ATTACH": ["die_shift_um", "attach_void_pct"],
    "WIRE_BOND": ["loop_height_um", "pull_strength_gf"],
    "FLIP_CHIP": ["bump_height_um", "coplanarity_um"],
    "MOLD": ["package_thickness_mm", "warpage_um"],
    "SINGULATION": ["saw_street_um", "edge_chipping_um"],
    "TEST": ["contact_resistance_mohm", "current_leakage_ua"],
    "PACK_OUT": ["label_offset_mm", "tray_flatness_mm"],
}

LOT_STATUS_FLOW = ["WAIT", "RUNNING", "MOVE_OUT", "HOLD", "REWORK", "COMPLETE"]


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
    # 생산/목표/불량/설비/WIP가 모두 같은 필터 규칙을 쓰도록 공통 함수로 분리했습니다.
    # 이렇게 해야 데이터 종류가 달라도 같은 질문이 같은 방식으로 동작합니다.
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
    # 모든 공정에 모든 제품을 붙이면 비현실적인 조합이 생길 수 있으므로
    # TECH와 공정군의 호환성을 먼저 확인한 뒤 데이터 행을 생성합니다.
    for spec in PROCESS_SPECS:
        for product in PRODUCTS:
            if spec["family"] in PRODUCT_TECH_FAMILY.get(product["TECH"], set()):
                yield spec, product


def _make_lot_id(date: str, family: str, index: int) -> str:
    family_code = family.replace("_", "")[:4]
    return f"LOT-{date[-4:]}-{family_code}-{index:03d}"


def _resolve_query_date(params: Dict[str, Any]) -> str:
    raw_date = params.get("date")
    if raw_date:
        return str(raw_date)
    return datetime.now().strftime("%Y%m%d")


def get_production_data(params: Dict[str, Any]) -> Dict[str, Any]:
    # 실제 DB 대신 재현 가능한 mock 데이터를 만듭니다.
    # 날짜를 seed로 사용해 같은 날짜 질문에는 같은 결과가 나오도록 했습니다.
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
            }
        )
    rows = _apply_common_filters(rows, params)
    total = sum(int(item["production"]) for item in rows)
    return {
        "success": True,
        "tool_name": "get_production_data",
        "data": rows,
        "summary": f"총 {len(rows)}건, 총 생산량 {format_summary_quantity(total)}",
    }


def get_target_data(params: Dict[str, Any]) -> Dict[str, Any]:
    # 목표 데이터는 생산 데이터와 같은 축을 사용하되 값만 목표치로 둡니다.
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
            }
        )
    rows = _apply_common_filters(rows, params)
    total = sum(int(item["target"]) for item in rows)
    return {
        "success": True,
        "tool_name": "get_target_data",
        "data": rows,
        "summary": f"총 {len(rows)}건, 총 목표량 {format_summary_quantity(total)}",
    }


def get_defect_rate(params: Dict[str, Any]) -> Dict[str, Any]:
    # 불량 데이터는 검사수량, 불량수량, 불량률을 함께 만들어
    # 후속 질문에서 정렬/그룹화/비교가 가능하도록 구성합니다.
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
    return {
        "success": True,
        "tool_name": "get_defect_rate",
        "data": rows,
        "summary": f"총 {len(rows)}건, 평균 불량률 {avg_rate:.2f}%",
    }


def get_equipment_status(params: Dict[str, Any]) -> Dict[str, Any]:
    # 설비 데이터는 시간 합계와 가동률을 같이 제공해
    # "가동률 낮은 순" 같은 질문을 바로 처리할 수 있게 합니다.
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
    return {
        "success": True,
        "tool_name": "get_equipment_status",
        "data": rows,
        "summary": f"총 {len(rows)}건, 평균 가동률 {avg_util:.1f}%",
    }


def get_wip_status(params: Dict[str, Any]) -> Dict[str, Any]:
    # WIP는 재공수량과 상태를 함께 보여줘야
    # HOLD만 보기, 상위 재공 보기 같은 후속 질문이 가능합니다.
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
    return {
        "success": True,
        "tool_name": "get_wip_status",
        "data": rows,
        "summary": f"총 {len(rows)}건, 총 WIP {format_summary_quantity(total)} EA, 대기/홀드 {delayed}건",
    }


def get_yield_data(params: Dict[str, Any]) -> Dict[str, Any]:
    # 수율 데이터는 생산/불량과 함께 자주 비교되므로
    # tested_qty, pass_qty, yield_rate를 같은 행에 담아 둡니다.
    date = str(params["date"])
    random.seed(_stable_seed(date, 5000))
    rows: List[Dict[str, Any]] = []
    for spec, product in _iter_valid_process_product_pairs():
        tested_qty = random.randint(2200, 7800)
        base_yield = 98.8 if spec["family"] in {"ASSY_PREP", "PACK_OUT"} else 96.5
        if spec["family"] in {"WIRE_BOND", "TEST"}:
            base_yield = 94.5
        yield_rate = round(max(82.0, min(99.9, random.uniform(base_yield - 4.5, base_yield + 1.2))), 2)
        pass_qty = int(tested_qty * yield_rate / 100)
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
                "tested_qty": tested_qty,
                "pass_qty": pass_qty,
                "yield_rate": yield_rate,
                "dominant_fail_bin": random.choice(YIELD_FAIL_BINS_BY_FAMILY[spec["family"]]),
            }
        )
    rows = _apply_common_filters(rows, params)
    avg_yield = sum(float(item["yield_rate"]) for item in rows) / len(rows) if rows else 0.0
    return {
        "success": True,
        "tool_name": "get_yield_data",
        "data": rows,
        "summary": f"총 {len(rows)}건, 평균 수율 {avg_yield:.2f}%",
    }


def get_hold_lot_data(params: Dict[str, Any]) -> Dict[str, Any]:
    # Hold 데이터는 "왜 멈췄는지"를 보여주는 운영성 데이터입니다.
    # 공정/제품 조건과 함께 hold 이유, owner, 경과 시간을 같이 담습니다.
    date = str(params["date"])
    random.seed(_stable_seed(date, 6000))
    rows: List[Dict[str, Any]] = []
    for index, (spec, product) in enumerate(_iter_valid_process_product_pairs(), start=1):
        if random.random() < 0.45:
            continue
        rows.append(
            {
                "날짜": date,
                "lot_id": _make_lot_id(date, spec["family"], index),
                "공정": spec["공정"],
                "공정군": spec["family"],
                "MODE": product["MODE"],
                "DEN": product["DEN"],
                "TECH": product["TECH"],
                "MCP_NO": product["MCP_NO"],
                "라인": spec["라인"],
                "hold_qty": random.randint(80, 1800),
                "hold_reason": random.choice(HOLD_REASONS_BY_FAMILY[spec["family"]]),
                "hold_owner": random.choice(HOLD_OWNERS),
                "hold_hours": round(random.uniform(1.5, 42.0), 1),
                "hold_status": random.choice(["OPEN", "REVIEW", "WAIT_DISPOSITION"]),
            }
        )
    rows = _apply_common_filters(rows, params)
    total_hold = sum(int(item["hold_qty"]) for item in rows)
    return {
        "success": True,
        "tool_name": "get_hold_lot_data",
        "data": rows,
        "summary": f"총 {len(rows)}건, 총 홀드 수량 {format_summary_quantity(total_hold)}, 평균 홀드 시간 {sum(float(item['hold_hours']) for item in rows) / len(rows):.1f}h" if rows else "총 0건, 총 홀드 수량 0",
    }


def get_scrap_data(params: Dict[str, Any]) -> Dict[str, Any]:
    # Scrap 데이터는 loss cost까지 같이 넣어 두면
    # 생산, 불량과 함께 비용 관점 질문에도 쓸 수 있습니다.
    date = str(params["date"])
    random.seed(_stable_seed(date, 7000))
    rows: List[Dict[str, Any]] = []
    for spec, product in _iter_valid_process_product_pairs():
        input_qty = random.randint(1800, 7200)
        scrap_qty = int(input_qty * random.uniform(0.002, 0.028))
        scrap_rate = round((scrap_qty / input_qty) * 100, 2)
        loss_cost = int(scrap_qty * random.uniform(1.8, 8.5))
        rows.append(
            {
                "날짜": date,
                "공정": spec["공정"],
                "공정군": spec["family"],
                "MODE": product["MODE"],
                "DEN": product["DEN"],
                "TECH": product["TECH"],
                "MCP_NO": product["MCP_NO"],
                "라인": spec["라인"],
                "scrap_qty": scrap_qty,
                "scrap_rate": scrap_rate,
                "scrap_reason": random.choice(SCRAP_REASONS_BY_FAMILY[spec["family"]]),
                "loss_cost_usd": loss_cost,
            }
        )
    rows = _apply_common_filters(rows, params)
    total_scrap = sum(int(item["scrap_qty"]) for item in rows)
    total_cost = sum(int(item["loss_cost_usd"]) for item in rows)
    return {
        "success": True,
        "tool_name": "get_scrap_data",
        "data": rows,
        "summary": f"총 {len(rows)}건, 총 스크랩 {format_summary_quantity(total_scrap)}, 총 손실비용 ${total_cost:,}",
    }


def get_recipe_condition_data(params: Dict[str, Any]) -> Dict[str, Any]:
    # 공정 조건/레시피 이력은 품질 이슈 원인을 설명할 때 자주 필요합니다.
    # 초보자도 읽기 쉽게 각 공정당 한 행에 핵심 파라미터를 묶어 둡니다.
    date = _resolve_query_date(params)
    random.seed(_stable_seed(date, 8000))
    rows: List[Dict[str, Any]] = []
    for spec, product in _iter_valid_process_product_pairs():
        base = RECIPE_BASE_BY_FAMILY[spec["family"]]
        rows.append(
            {
                "날짜": date,
                "공정": spec["공정"],
                "공정군": spec["family"],
                "MODE": product["MODE"],
                "DEN": product["DEN"],
                "TECH": product["TECH"],
                "라인": spec["라인"],
                "recipe_id": f"RC-{spec['family'][:3]}-{random.randint(10, 99)}",
                "recipe_version": f"v{random.randint(1, 3)}.{random.randint(0, 9)}",
                "temp_c": round(base["temp_c"] + random.uniform(-6, 6), 1),
                "pressure_kpa": round(max(0, base["pressure_kpa"] + random.uniform(-12, 12)), 1),
                "process_time_sec": int(base["process_time_sec"] + random.uniform(-60, 60)),
                "operator_id": f"OP-{random.randint(100, 999)}",
            }
        )
    rows = _apply_common_filters(rows, params)
    return {
        "success": True,
        "tool_name": "get_recipe_condition_data",
        "data": rows,
        "summary": f"총 {len(rows)}건, 공정 조건/레시피 이력 조회 완료",
    }


def get_lot_trace_data(params: Dict[str, Any]) -> Dict[str, Any]:
    # Lot trace 데이터는 공정 이력과 상태를 함께 보여줘
    # "어느 공정에서 오래 멈췄는지" 같은 질문에 쓰기 좋습니다.
    date = _resolve_query_date(params)
    random.seed(_stable_seed(date, 9000))
    rows: List[Dict[str, Any]] = []
    for index, (spec, product) in enumerate(_iter_valid_process_product_pairs(), start=1):
        if random.random() < 0.35:
            continue
        rows.append(
            {
                "날짜": date,
                "lot_id": _make_lot_id(date, spec["family"], index),
                "wafer_id": f"WF-{random.randint(1000, 9999)}",
                "공정": spec["공정"],
                "공정군": spec["family"],
                "MODE": product["MODE"],
                "DEN": product["DEN"],
                "TECH": product["TECH"],
                "MCP_NO": product["MCP_NO"],
                "라인": spec["라인"],
                "route_step": random.randint(3, 28),
                "current_status": random.choice(LOT_STATUS_FLOW),
                "elapsed_hours": round(random.uniform(2.0, 96.0), 1),
                "next_process": random.choice([item["공정"] for item in PROCESS_SPECS if item["family"] == spec["family"]]),
                "hold_reason": random.choice(HOLD_REASONS_BY_FAMILY[spec["family"]]) if random.random() < 0.25 else "none",
            }
        )
    rows = _apply_common_filters(rows, params)
    avg_elapsed = sum(float(item["elapsed_hours"]) for item in rows) / len(rows) if rows else 0.0
    return {
        "success": True,
        "tool_name": "get_lot_trace_data",
        "data": rows,
        "summary": f"총 {len(rows)}건, 평균 체류 시간 {avg_elapsed:.1f}h",
    }


DATASET_TOOL_FUNCTIONS = {
    "production": get_production_data,
    "target": get_target_data,
    "defect": get_defect_rate,
    "equipment": get_equipment_status,
    "wip": get_wip_status,
    "yield": get_yield_data,
    "hold": get_hold_lot_data,
    "scrap": get_scrap_data,
    "recipe": get_recipe_condition_data,
    "lot_trace": get_lot_trace_data,
}


DATASET_REGISTRY = {
    # 질문 해석용 label/keywords는 기준 사전(domain_knowledge)에 두고,
    # 여기서는 "어떤 함수가 실제 데이터를 만든다"만 연결합니다.
    dataset_key: {
        "label": DATASET_METADATA[dataset_key]["label"],
        "tool_name": tool_fn.__name__,
        "tool": tool_fn,
        "keywords": DATASET_METADATA[dataset_key]["keywords"],
    }
    for dataset_key, tool_fn in DATASET_TOOL_FUNCTIONS.items()
}

RETRIEVAL_TOOL_MAP = {key: meta["tool"] for key, meta in DATASET_REGISTRY.items()}


def get_dataset_label(dataset_key: str) -> str:
    dataset_meta = DATASET_REGISTRY.get(dataset_key, {})
    return str(dataset_meta.get("label", dataset_key))


def pick_retrieval_tools(query_text: str) -> List[str]:
    # 등록부를 기준으로 질의에 포함된 데이터 주제를 찾습니다.
    # 새 tool이 생겨도 keywords만 등록하면 같은 로직을 그대로 재사용할 수 있습니다.
    query = str(query_text or "").lower()
    selected: List[str] = []

    for dataset_key, dataset_meta in DATASET_REGISTRY.items():
        keywords = dataset_meta.get("keywords", [])
        if any(token in query for token in keywords):
            selected.append(dataset_key)

    # "홀드 lot"는 보통 홀드된 lot 목록을 뜻하는 경우가 많아서,
    # 사용자가 trace/이력까지 명시하지 않으면 hold 조회를 우선합니다.
    explicit_trace_tokens = ["trace", "이력", "추적", "traceability"]
    if "hold" in selected and "lot_trace" in selected and not any(token in query for token in explicit_trace_tokens):
        selected = [item for item in selected if item != "lot_trace"]

    return selected


def pick_retrieval_tool(query_text: str) -> str | None:
    selected = pick_retrieval_tools(query_text)
    return selected[0] if selected else None


def execute_retrieval_tools(dataset_keys: List[str], params: Dict[str, Any]) -> List[Dict[str, Any]]:
    # agent는 "어떤 데이터를 가져와야 하는가"만 결정하고,
    # 실제 조회 실행은 이 함수에 맡기면 더 읽기 쉽습니다.
    results: List[Dict[str, Any]] = []
    for dataset_key in dataset_keys:
        dataset_meta = DATASET_REGISTRY.get(dataset_key)
        if not dataset_meta:
            continue

        result = dataset_meta["tool"](params)
        if isinstance(result, dict):
            result["dataset_key"] = dataset_key
            result["dataset_label"] = dataset_meta["label"]
        results.append(result)
    return results


def build_current_datasets(tool_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    # 여러 원본 데이터를 동시에 조회했을 때,
    # 각 데이터셋을 이름별로 보관해 두면 이후 분석 전략을 바꾸기 쉽습니다.
    datasets: Dict[str, Any] = {}
    for result in tool_results:
        dataset_key = result.get("dataset_key")
        if not dataset_key:
            continue

        rows = result.get("data", [])
        first_row = rows[0] if isinstance(rows, list) and rows else {}
        datasets[dataset_key] = {
            "label": result.get("dataset_label", get_dataset_label(str(dataset_key))),
            "tool_name": result.get("tool_name"),
            "summary": result.get("summary", ""),
            "row_count": len(rows) if isinstance(rows, list) else 0,
            "columns": list(first_row.keys()) if isinstance(first_row, dict) else [],
            "data": rows if isinstance(rows, list) else [],
        }
    return datasets


def get_dataset_registry() -> Dict[str, Dict[str, Any]]:
    keyword_map = get_dataset_keyword_map()
    registry: Dict[str, Dict[str, Any]] = {}
    for dataset_key, tool_fn in DATASET_TOOL_FUNCTIONS.items():
        keyword_meta = keyword_map.get(dataset_key, {})
        registry[dataset_key] = {
            "label": str(keyword_meta.get("label", get_contract_dataset_label(dataset_key))),
            "tool_name": tool_fn.__name__,
            "tool": tool_fn,
            "keywords": list(keyword_meta.get("keywords", [])),
        }
    return registry


def get_dataset_label(dataset_key: str) -> str:
    dataset_meta = get_dataset_registry().get(dataset_key, {})
    return str(dataset_meta.get("label", dataset_key))


def pick_retrieval_tools(query_text: str) -> List[str]:
    query = str(query_text or "").lower()
    selected: List[str] = []
    dataset_registry = get_dataset_registry()

    for dataset_key, dataset_meta in dataset_registry.items():
        keywords = dataset_meta.get("keywords", [])
        if any(token in query for token in keywords):
            selected.append(dataset_key)

    explicit_trace_tokens = ["trace", "이력", "추적", "traceability"]
    if "hold" in selected and "lot_trace" in selected and not any(token in query for token in explicit_trace_tokens):
        selected = [item for item in selected if item != "lot_trace"]

    return selected


def pick_retrieval_tool(query_text: str) -> str | None:
    selected = pick_retrieval_tools(query_text)
    return selected[0] if selected else None


def execute_retrieval_tools(dataset_keys: List[str], params: Dict[str, Any]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    dataset_registry = get_dataset_registry()
    for dataset_key in dataset_keys:
        dataset_meta = dataset_registry.get(dataset_key)
        if not dataset_meta:
            continue

        result = dataset_meta["tool"](params)
        if isinstance(result, dict):
            result["dataset_key"] = dataset_key
            result["dataset_label"] = dataset_meta["label"]
        results.append(result)
    return results


def pick_retrieval_tools(query_text: str) -> List[str]:
    query = str(query_text or "").lower()
    selected: List[str] = []
    dataset_registry = get_dataset_registry()

    for dataset_key, dataset_meta in dataset_registry.items():
        keywords = dataset_meta.get("keywords", [])
        if any(str(token).lower() in query for token in keywords):
            selected.append(dataset_key)

    explicit_trace_tokens = ["trace", "\uc774\ub825", "\ucd94\uc801", "traceability"]
    if "hold" in selected and "lot_trace" in selected and not any(token in query for token in explicit_trace_tokens):
        selected = [item for item in selected if item != "lot_trace"]

    return selected


def pick_retrieval_tool(query_text: str) -> str | None:
    selected = pick_retrieval_tools(query_text)
    return selected[0] if selected else None
