from typing import Dict, List


# 이 파일은 "질문 해석"과 "데이터셋 메타정보"의 기준 사전입니다.
# 초보자가 새 데이터셋을 추가할 때는 먼저 이 파일에서
# 공정 / 제품 / 데이터셋 용어를 확인하면 전체 구조를 따라가기 쉽습니다.

FILTER_FIELDS = {
    "date": {"field_name": "날짜", "description": "작업일자 (YYYYMMDD)"},
    "process": {"field_name": "공정", "description": "제조 공정 또는 공정군"},
    "mode": {"field_name": "MODE", "description": "제품 / 품목 계열"},
    "den": {"field_name": "DEN", "description": "메모리 용량 또는 밀도"},
    "tech": {"field_name": "TECH", "description": "패키지 기술"},
    "lead": {"field_name": "LEAD", "description": "Lead / Ball 수"},
    "mcp_no": {"field_name": "MCP_NO", "description": "제품 또는 프로그램 코드"},
}


# 실제 데이터 생성에서도 그대로 쓰는 공정 기본 정의입니다.
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

PROCESS_GROUP_SYNONYMS = {
    "ASSY_PREP": ["assy prep", "prep", "assembly prep", "사전 준비", "전처리"],
    "DIE_ATTACH": ["die attach", "da", "d/a", "다이 어태치", "다이 부착"],
    "WIRE_BOND": ["wire bond", "wb", "w/b", "와이어 본딩"],
    "FLIP_CHIP": ["flip chip", "fcb", "fc", "플립칩"],
    "MOLD": ["mold", "molding", "몰드", "몰딩"],
    "SINGULATION": ["singulation", "saw", "laser saw", "절단", "싱귤레이션"],
    "TEST": ["test", "final test", "burn-in", "테스트", "검사"],
    "PACK_OUT": ["pack out", "ship", "출하", "포장"],
}


def _build_process_groups() -> Dict[str, Dict[str, List[str] | str]]:
    groups: Dict[str, Dict[str, List[str] | str]] = {}
    for spec in PROCESS_SPECS:
        family = spec["family"]
        if family not in groups:
            groups[family] = {
                "group_name": family,
                "synonyms": PROCESS_GROUP_SYNONYMS.get(family, []),
                "actual_values": [],
            }
        actual_values = groups[family]["actual_values"]
        if spec["공정"] not in actual_values:
            actual_values.append(spec["공정"])
    return groups


PROCESS_GROUPS = _build_process_groups()


# 실제 데이터 생성에서도 그대로 쓰는 대표 제품 정의입니다.
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

MODE_GROUPS = {
    "DDR5_6400": {"synonyms": ["ddr5 6400", "ddr5_6400"], "actual_values": ["DDR5_6400"]},
    "DDR5_5600": {"synonyms": ["ddr5 5600", "ddr5_5600"], "actual_values": ["DDR5_5600"]},
    "LPDDR5X_8533": {"synonyms": ["lpddr5x 8533", "lpddr5x_8533", "lp5x"], "actual_values": ["LPDDR5X_8533"]},
    "UFS3.1": {"synonyms": ["ufs3.1", "ufs 3.1"], "actual_values": ["UFS3.1"]},
    "PMIC": {"synonyms": ["pmic"], "actual_values": ["PMIC"]},
    "CIS": {"synonyms": ["cis", "camera sensor"], "actual_values": ["CIS"]},
}

DEN_GROUPS = {
    "8Gb": {"synonyms": ["8gb", "8 gb"], "actual_values": ["8Gb"]},
    "16Gb": {"synonyms": ["16gb", "16 gb"], "actual_values": ["16Gb"]},
    "32Gb": {"synonyms": ["32gb", "32 gb"], "actual_values": ["32Gb"]},
    "64Gb": {"synonyms": ["64gb", "64 gb"], "actual_values": ["64Gb"]},
    "128Gb": {"synonyms": ["128gb", "128 gb"], "actual_values": ["128Gb"]},
}

TECH_GROUPS = {
    "WB": {"synonyms": ["wb", "wire bond"], "actual_values": ["WB"]},
    "FC": {"synonyms": ["fc", "flip chip"], "actual_values": ["FC"]},
    "FO": {"synonyms": ["fo", "fan-out"], "actual_values": ["FO"]},
    "WLCSP": {"synonyms": ["wlcsp"], "actual_values": ["WLCSP"]},
    "SiP": {"synonyms": ["sip", "si-p"], "actual_values": ["SiP"]},
    "MCP": {"synonyms": ["mcp"], "actual_values": ["MCP"]},
}


# retrieval dataset 메타정보도 기준 사전에 둡니다.
# data_tools는 label / keywords를 여기서 읽고, 실제 함수만 연결합니다.
DATASET_METADATA = {
    "production": {"label": "생산", "keywords": ["생산", "production", "실적"]},
    "target": {"label": "목표", "keywords": ["목표", "target", "계획"]},
    "defect": {"label": "불량", "keywords": ["불량", "defect", "결함"]},
    "equipment": {"label": "설비", "keywords": ["설비", "가동률", "equipment", "downtime"]},
    "wip": {"label": "WIP", "keywords": ["wip", "재공", "대기"]},
    "yield": {"label": "수율", "keywords": ["수율", "yield", "pass rate", "합격률"]},
    "hold": {"label": "홀드", "keywords": ["hold", "홀드", "보류 lot", "hold lot"]},
    "scrap": {"label": "스크랩", "keywords": ["scrap", "스크랩", "폐기", "loss cost", "손실비용"]},
    "recipe": {"label": "레시피", "keywords": ["recipe", "레시피", "공정 조건", "조건값", "parameter", "파라미터"]},
    "lot_trace": {"label": "LOT 이력", "keywords": ["lot", "lot trace", "lot 이력", "추적", "traceability", "로트"]},
}


def build_domain_knowledge_prompt() -> str:
    lines = []
    lines.append("제조 도메인 필터 추출 규칙")
    lines.append("")
    lines.append("사용 가능한 필터 필드:")
    for key, value in FILTER_FIELDS.items():
        lines.append(f"- {value['field_name']} ({key}): {value['description']}")

    lines.append("")
    lines.append("공정군 매핑:")
    for group in PROCESS_GROUPS.values():
        lines.append(
            f"- {group['group_name']}: synonyms={', '.join(group['synonyms'])} -> values={', '.join(group['actual_values'])}"
        )

    lines.append("")
    lines.append("MODE 그룹:")
    for group_id, group in MODE_GROUPS.items():
        lines.append(f"- {group_id}: {', '.join(group['synonyms'])} -> {', '.join(group['actual_values'])}")

    lines.append("")
    lines.append("DEN 그룹:")
    for group_id, group in DEN_GROUPS.items():
        lines.append(f"- {group_id}: {', '.join(group['synonyms'])} -> {', '.join(group['actual_values'])}")

    lines.append("")
    lines.append("TECH 그룹:")
    for group_id, group in TECH_GROUPS.items():
        lines.append(f"- {group_id}: {', '.join(group['synonyms'])} -> {', '.join(group['actual_values'])}")

    lines.append("")
    lines.append("반도체 운영 데이터셋 관련 용어:")
    for dataset_name, meta in DATASET_METADATA.items():
        lines.append(f"- {dataset_name}: {', '.join(meta['keywords'])}")

    lines.append("")
    lines.append("규칙:")
    lines.append("- 공정군으로 질문하면 actual_values 전체를 필터 값으로 사용한다.")
    lines.append("- 개별 공정/스텝명으로 질문하면 해당 값만 사용한다.")
    lines.append("- 명시되지 않은 필드는 null로 둔다.")
    lines.append("- 후속 분석에서는 현재 테이블 컬럼과 도메인 지식을 함께 참고한다.")
    return "\n".join(lines)
