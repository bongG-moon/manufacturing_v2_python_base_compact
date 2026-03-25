FILTER_FIELDS = {
    "date": {"field_name": "날짜", "description": "작업일자 (YYYYMMDD)"},
    "process": {"field_name": "공정", "description": "제조 공정 또는 공정군"},
    "mode": {"field_name": "MODE", "description": "제품 / 품목 계열"},
    "den": {"field_name": "DEN", "description": "메모리 용량 또는 밀도"},
    "tech": {"field_name": "TECH", "description": "패키지 기술"},
    "lead": {"field_name": "LEAD", "description": "Lead / Ball 수"},
    "mcp_no": {"field_name": "MCP_NO", "description": "제품 또는 프로그램 코드"},
}

PROCESS_GROUPS = {
    "ASSY_PREP": {
        "group_name": "ASSY_PREP",
        "synonyms": ["assy prep", "prep", "assembly prep", "사전 준비", "전처리"],
        "actual_values": ["incoming_sort", "wafer_bake", "plasma_clean", "tape_attach"],
    },
    "DIE_ATTACH": {
        "group_name": "DIE_ATTACH",
        "synonyms": ["die attach", "da", "d/a", "다이 어태치", "다이 부착"],
        "actual_values": ["epoxy_dispense", "die_place", "tack_cure", "post_cure"],
    },
    "WIRE_BOND": {
        "group_name": "WIRE_BOND",
        "synonyms": ["wire bond", "wb", "w/b", "와이어 본딩"],
        "actual_values": ["first_bond", "second_bond", "stitch_bond", "pull_test"],
    },
    "FLIP_CHIP": {
        "group_name": "FLIP_CHIP",
        "synonyms": ["flip chip", "fcb", "fc", "플립칩"],
        "actual_values": ["bump_prep", "flip_place", "reflow", "underfill_cure"],
    },
    "MOLD": {
        "group_name": "MOLD",
        "synonyms": ["mold", "molding", "몰드", "몰딩"],
        "actual_values": ["transfer_mold", "post_mold_cure", "deflash", "marking"],
    },
    "SINGULATION": {
        "group_name": "SINGULATION",
        "synonyms": ["singulation", "saw", "laser saw", "절단", "싱귤레이션"],
        "actual_values": ["saw_cut", "laser_saw", "edge_inspect"],
    },
    "TEST": {
        "group_name": "TEST",
        "synonyms": ["test", "final test", "burn-in", "테스트", "검사"],
        "actual_values": ["pre_test", "final_test", "burn_in", "scan_test"],
    },
    "PACK_OUT": {
        "group_name": "PACK_OUT",
        "synonyms": ["pack out", "ship", "출하", "포장"],
        "actual_values": ["visual_inspect", "tray_pack", "reel_pack", "ship_release"],
    },
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

SEMICON_DATASET_HINTS = {
    "yield": ["수율", "yield", "pass rate", "합격률"],
    "hold": ["hold", "홀드", "보류 lot", "hold lot"],
    "scrap": ["scrap", "스크랩", "폐기", "loss cost", "손실비용"],
    "recipe": ["recipe", "레시피", "공정 조건", "조건값", "parameter", "파라미터"],
    "lot_trace": ["lot", "lot trace", "lot 이력", "traceability", "로트"],
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
    for dataset_name, synonyms in SEMICON_DATASET_HINTS.items():
        lines.append(f"- {dataset_name}: {', '.join(synonyms)}")

    lines.append("")
    lines.append("규칙:")
    lines.append("- 공정군으로 질문하면 actual_values 전체를 필터 값으로 사용한다.")
    lines.append("- 개별 공정/스텝명으로 질문하면 해당 값만 사용한다.")
    lines.append("- 명시되지 않은 필드는 null로 둔다.")
    lines.append("- 후속 분석에서는 현재 테이블 컬럼과 도메인 지식을 함께 참고한다.")
    return "\n".join(lines)
