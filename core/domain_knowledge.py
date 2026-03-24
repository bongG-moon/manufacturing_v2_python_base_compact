FILTER_FIELDS = {
    "date": {"field_name": "날짜", "description": "작업일자 (YYYYMMDD)"},
    "process": {"field_name": "공정", "description": "제조 공정. 그룹 또는 개별 공정 가능"},
    "mode": {"field_name": "MODE", "description": "제품 모드 (DDR4, DDR5, LPDDR5)"},
    "den": {"field_name": "DEN", "description": "제품 용량 (256G, 512G, 1T)"},
    "tech": {"field_name": "TECH", "description": "기술 유형 (LC, FO, FC)"},
    "lead": {"field_name": "LEAD", "description": "Lead/Ball 개수"},
    "mcp_no": {"field_name": "MCP_NO", "description": "제품 코드 (예: A-410)"},
}

PROCESS_GROUPS = {
    "DP": {
        "group_name": "DP (Die Prep)",
        "synonyms": ["DP", "D/P", "Die Prep", "다이프렙", "다이 프렙"],
        "actual_values": ["INPUT", "DS1", "DS2", "DS3", "DS4"],
    },
    "DA": {
        "group_name": "DA (Die Attach)",
        "synonyms": ["DA", "D/A", "Die Attach", "다이어태치", "다이 어태치", "다이본딩"],
        "actual_values": ["D/A1", "D/A2", "D/A3", "D/A4", "D/A5"],
    },
    "WB": {
        "group_name": "WB (Wire Bonding)",
        "synonyms": ["WB", "W/B", "Wire Bonding", "와이어본딩", "와이어 본딩"],
        "actual_values": ["W/B1", "W/B2", "W/B3", "W/B4", "W/B5"],
    },
    "FCB": {
        "group_name": "FCB (Flip Chip Bonding)",
        "synonyms": ["FCB", "Flip Chip", "플립칩", "플립 칩"],
        "actual_values": ["FCB1", "FCB2", "FCB3", "FCB4", "FCB5"],
    },
    "SHIP": {
        "group_name": "SHIP",
        "synonyms": ["SHIP", "출하", "PKG OUT"],
        "actual_values": ["SHIP PKT"],
    },
}

MODE_GROUPS = {
    "DDR4": {"synonyms": ["DDR4", "DDR 4"], "actual_values": ["DDR4"]},
    "DDR5": {"synonyms": ["DDR5", "DDR 5"], "actual_values": ["DDR5"]},
    "LPDDR5": {"synonyms": ["LPDDR5", "LP DDR5", "LP5"], "actual_values": ["LPDDR5"]},
}

DEN_GROUPS = {
    "256G": {"synonyms": ["256G", "256Gb"], "actual_values": ["256G"]},
    "512G": {"synonyms": ["512G", "512Gb"], "actual_values": ["512G"]},
    "1T": {"synonyms": ["1T", "1Tb", "1TB"], "actual_values": ["1T"]},
}

TECH_GROUPS = {
    "LC": {"synonyms": ["LC"], "actual_values": ["LC"]},
    "FO": {"synonyms": ["FO", "Fan-Out", "fan-out"], "actual_values": ["FO"]},
    "FC": {"synonyms": ["FC", "Flip Chip"], "actual_values": ["FC"]},
}


def build_domain_knowledge_prompt() -> str:
    lines = []
    lines.append("제조 도메인 필터 추출 규칙")
    lines.append("")
    lines.append("사용 가능한 필터 필드:")
    for key, value in FILTER_FIELDS.items():
        lines.append(f"- {value['field_name']} ({key}): {value['description']}")

    lines.append("")
    lines.append("공정 그룹 매핑:")
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
    lines.append("규칙:")
    lines.append("- 그룹명으로 질문하면 actual_values 전체를 필터 값으로 사용한다.")
    lines.append("- 개별 공정명으로 질문하면 해당 공정만 사용한다.")
    lines.append("- 명시되지 않은 필드는 null로 둔다.")
    return "\n".join(lines)
