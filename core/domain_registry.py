from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List

from .dataset_contracts import get_dataset_label
from .filter_utils import normalize_text


DOMAIN_REGISTRY_DIR = Path(__file__).resolve().parents[1] / "reference_materials" / "domain_registry"


@dataclass
class DomainGroup:
    canonical: str
    synonyms: List[str] = field(default_factory=list)
    values: List[str] = field(default_factory=list)


@dataclass
class DatasetKeywordEntry:
    dataset_key: str
    label: str
    keywords: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class DomainRegistry:
    dataset_keywords: Dict[str, DatasetKeywordEntry]
    process_groups: Dict[str, DomainGroup]
    value_groups: Dict[str, Dict[str, DomainGroup]]
    notes: List[str] = field(default_factory=list)
    loaded_files: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


DEFAULT_DATASET_KEYWORDS = {
    "production": DatasetKeywordEntry("production", "생산", ["생산", "생산량", "실적", "production", "output"], "생산 실적"),
    "target": DatasetKeywordEntry("target", "목표", ["목표", "계획", "target", "plan"], "목표 수량"),
    "defect": DatasetKeywordEntry("defect", "불량", ["불량", "결함", "defect", "ng"], "불량률 및 불량 유형"),
    "equipment": DatasetKeywordEntry("equipment", "설비", ["설비", "장비", "가동률", "equipment", "downtime"], "설비 상태"),
    "wip": DatasetKeywordEntry("wip", "WIP", ["wip", "재공", "대기"], "재공 상태"),
    "yield": DatasetKeywordEntry("yield", "수율", ["수율", "yield", "합격률", "pass rate"], "수율 데이터"),
    "hold": DatasetKeywordEntry("hold", "홀드", ["홀드", "보류", "hold", "hold lot"], "홀드 lot"),
    "scrap": DatasetKeywordEntry("scrap", "스크랩", ["스크랩", "폐기", "scrap", "loss cost"], "스크랩 및 손실 비용"),
    "recipe": DatasetKeywordEntry("recipe", "레시피", ["레시피", "공정 조건", "recipe", "parameter"], "레시피 및 조건"),
    "lot_trace": DatasetKeywordEntry("lot_trace", "LOT 이력", ["lot", "lot trace", "lot 이력", "추적", "traceability"], "LOT trace"),
}

DEFAULT_PROCESS_GROUPS = {
    "ASSY_PREP": DomainGroup("ASSY_PREP", ["assy prep", "prep", "assembly prep", "사전 준비", "전처리"], ["incoming_sort", "wafer_bake", "plasma_clean"]),
    "DIE_ATTACH": DomainGroup("DIE_ATTACH", ["die attach", "da", "d/a", "다이 어태치", "다이 부착"], ["epoxy_dispense", "die_place", "post_cure"]),
    "WIRE_BOND": DomainGroup("WIRE_BOND", ["wire bond", "wb", "w/b", "와이어 본딩"], ["first_bond", "stitch_bond", "pull_test"]),
    "FLIP_CHIP": DomainGroup("FLIP_CHIP", ["flip chip", "fc", "플립칩"], ["flip_place", "reflow", "underfill_cure"]),
    "MOLD": DomainGroup("MOLD", ["mold", "molding", "몰드", "몰딩"], ["transfer_mold", "post_mold_cure", "marking"]),
    "SINGULATION": DomainGroup("SINGULATION", ["singulation", "saw", "절단", "싱귤레이션"], ["saw_cut", "laser_saw"]),
    "TEST": DomainGroup("TEST", ["test", "final test", "burn-in", "테스트", "검사"], ["final_test", "burn_in"]),
    "PACK_OUT": DomainGroup("PACK_OUT", ["pack out", "ship", "출하", "포장"], ["tray_pack", "ship_release"]),
}

DEFAULT_VALUE_GROUPS = {
    "mode": {
        "DDR5_6400": DomainGroup("DDR5_6400", ["ddr5 6400", "ddr5_6400"], ["DDR5_6400"]),
        "DDR5_5600": DomainGroup("DDR5_5600", ["ddr5 5600", "ddr5_5600"], ["DDR5_5600"]),
        "LPDDR5X_8533": DomainGroup("LPDDR5X_8533", ["lpddr5x 8533", "lpddr5x_8533", "lp5x"], ["LPDDR5X_8533"]),
        "UFS3.1": DomainGroup("UFS3.1", ["ufs3.1", "ufs 3.1"], ["UFS3.1"]),
        "PMIC": DomainGroup("PMIC", ["pmic"], ["PMIC"]),
        "CIS": DomainGroup("CIS", ["cis", "camera sensor"], ["CIS"]),
    },
    "den": {
        "8Gb": DomainGroup("8Gb", ["8gb", "8 gb"], ["8Gb"]),
        "16Gb": DomainGroup("16Gb", ["16gb", "16 gb"], ["16Gb"]),
        "32Gb": DomainGroup("32Gb", ["32gb", "32 gb"], ["32Gb"]),
        "64Gb": DomainGroup("64Gb", ["64gb", "64 gb"], ["64Gb"]),
        "128Gb": DomainGroup("128Gb", ["128gb", "128 gb"], ["128Gb"]),
    },
    "tech": {
        "WB": DomainGroup("WB", ["wb", "wire bond"], ["WB"]),
        "FC": DomainGroup("FC", ["fc", "flip chip"], ["FC"]),
        "FO": DomainGroup("FO", ["fo", "fan-out"], ["FO"]),
        "WLCSP": DomainGroup("WLCSP", ["wlcsp"], ["WLCSP"]),
        "MCP": DomainGroup("MCP", ["mcp"], ["MCP"]),
    },
}


def _split_cell(text: str) -> List[str]:
    return [item.strip() for item in str(text or "").split(",") if item.strip()]


def _parse_markdown_table(lines: List[str]) -> List[Dict[str, str]]:
    table_lines = [line.strip() for line in lines if line.strip().startswith("|")]
    if len(table_lines) < 2:
        return []

    header = [cell.strip() for cell in table_lines[0].strip("|").split("|")]
    rows: List[Dict[str, str]] = []
    for line in table_lines[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(header):
            continue
        rows.append(dict(zip(header, cells)))
    return rows


def _read_section_map(path: Path) -> Dict[str, List[str]]:
    sections: Dict[str, List[str]] = {"__root__": []}
    current_section = "__root__"
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            current_section = line[3:].strip().lower()
            sections[current_section] = []
            continue
        sections.setdefault(current_section, []).append(line)
    return sections


def _merge_group(target: Dict[str, DomainGroup], canonical: str, synonyms: Iterable[str], values: Iterable[str]) -> None:
    existing = target.get(canonical)
    if not existing:
        target[canonical] = DomainGroup(canonical, list(dict.fromkeys(synonyms)), list(dict.fromkeys(values)))
        return
    existing.synonyms = list(dict.fromkeys([*existing.synonyms, *synonyms]))
    existing.values = list(dict.fromkeys([*existing.values, *values]))


def _apply_markdown_file(path: Path, registry: DomainRegistry) -> None:
    sections = _read_section_map(path)
    registry.loaded_files.append(path.name)

    root_lines = [line.strip() for line in sections.get("__root__", []) if line.strip() and not line.startswith("# ")]
    if root_lines:
        registry.notes.append(" ".join(root_lines))

    dataset_rows = _parse_markdown_table(sections.get("dataset keywords", []))
    for row in dataset_rows:
        dataset_key = row.get("dataset_key", "").strip()
        if not dataset_key:
            continue
        existing = registry.dataset_keywords.get(dataset_key)
        label = row.get("label", "").strip() or (existing.label if existing else get_dataset_label(dataset_key))
        keywords = _split_cell(row.get("keywords", ""))
        description = row.get("description", "").strip() or (existing.description if existing else "")
        if existing:
            existing.keywords = list(dict.fromkeys([*existing.keywords, *keywords]))
            existing.description = description or existing.description
            existing.label = label or existing.label
        else:
            registry.dataset_keywords[dataset_key] = DatasetKeywordEntry(dataset_key, label, keywords, description)

    process_rows = _parse_markdown_table(sections.get("process groups", []))
    for row in process_rows:
        canonical = row.get("group", "").strip()
        if not canonical:
            continue
        _merge_group(
            registry.process_groups,
            canonical,
            _split_cell(row.get("synonyms", "")),
            _split_cell(row.get("values", "")),
        )

    value_rows = _parse_markdown_table(sections.get("value groups", []))
    for row in value_rows:
        field = row.get("field", "").strip().lower()
        canonical = row.get("canonical", "").strip()
        if not field or not canonical:
            continue
        registry.value_groups.setdefault(field, {})
        _merge_group(
            registry.value_groups[field],
            canonical,
            _split_cell(row.get("synonyms", "")),
            _split_cell(row.get("values", "")),
        )

    note_lines = [line.strip() for line in sections.get("notes", []) if line.strip() and not line.startswith("|")]
    if note_lines:
        registry.notes.append(" ".join(note_lines))


def _detect_conflicts(registry: DomainRegistry) -> List[str]:
    warnings: List[str] = []

    keyword_owner: Dict[str, str] = {}
    for dataset_key, entry in registry.dataset_keywords.items():
        for keyword in entry.keywords:
            normalized = normalize_text(keyword)
            existing = keyword_owner.get(normalized)
            if existing and existing != dataset_key:
                warnings.append(f"Dataset keyword conflict: `{keyword}` is used by both `{existing}` and `{dataset_key}`.")
            keyword_owner[normalized] = dataset_key

    for group_type, groups in [("process", registry.process_groups), *[(field, groups) for field, groups in registry.value_groups.items()]]:
        synonym_owner: Dict[str, str] = {}
        for canonical, group in groups.items():
            for synonym in [canonical, *group.synonyms]:
                normalized = normalize_text(synonym)
                existing = synonym_owner.get(normalized)
                if existing and existing != canonical:
                    warnings.append(f"{group_type} synonym conflict: `{synonym}` is used by both `{existing}` and `{canonical}`.")
                synonym_owner[normalized] = canonical

    return warnings


def load_domain_registry() -> DomainRegistry:
    registry = DomainRegistry(
        dataset_keywords={
            key: DatasetKeywordEntry(value.dataset_key, value.label, list(value.keywords), value.description)
            for key, value in DEFAULT_DATASET_KEYWORDS.items()
        },
        process_groups={
            key: DomainGroup(value.canonical, list(value.synonyms), list(value.values))
            for key, value in DEFAULT_PROCESS_GROUPS.items()
        },
        value_groups={
            field: {
                key: DomainGroup(group.canonical, list(group.synonyms), list(group.values))
                for key, group in groups.items()
            }
            for field, groups in DEFAULT_VALUE_GROUPS.items()
        },
    )

    if DOMAIN_REGISTRY_DIR.exists():
        for path in sorted(DOMAIN_REGISTRY_DIR.glob("*.md")):
            if path.name.lower() in {"readme.md", "template.md"}:
                continue
            _apply_markdown_file(path, registry)

    registry.warnings = _detect_conflicts(registry)
    return registry


def get_dataset_keyword_map() -> Dict[str, Dict[str, object]]:
    registry = load_domain_registry()
    return {
        key: {
            "label": entry.label,
            "keywords": entry.keywords,
            "description": entry.description,
        }
        for key, entry in registry.dataset_keywords.items()
    }


def build_domain_knowledge_prompt() -> str:
    registry = load_domain_registry()
    lines: List[str] = []
    lines.append("Manufacturing domain extraction guide")
    lines.append("")
    lines.append("Dataset keywords:")
    for dataset_key, entry in registry.dataset_keywords.items():
        lines.append(f"- {dataset_key} ({entry.label}): {', '.join(entry.keywords)}")

    lines.append("")
    lines.append("Process groups:")
    for group in registry.process_groups.values():
        lines.append(f"- {group.canonical}: synonyms={', '.join(group.synonyms)} -> values={', '.join(group.values)}")

    for field, groups in registry.value_groups.items():
        lines.append("")
        lines.append(f"{field.upper()} groups:")
        for group in groups.values():
            lines.append(f"- {group.canonical}: synonyms={', '.join(group.synonyms)} -> values={', '.join(group.values)}")

    if registry.notes:
        lines.append("")
        lines.append("Notes:")
        for note in registry.notes:
            lines.append(f"- {note}")

    return "\n".join(lines)


def get_domain_registry_summary() -> Dict[str, object]:
    registry = load_domain_registry()
    return {
        "loaded_files": registry.loaded_files,
        "dataset_keywords": get_dataset_keyword_map(),
        "process_groups": {
            key: {"synonyms": value.synonyms, "values": value.values}
            for key, value in registry.process_groups.items()
        },
        "value_groups": {
            field: {key: {"synonyms": value.synonyms, "values": value.values} for key, value in groups.items()}
            for field, groups in registry.value_groups.items()
        },
        "notes": registry.notes,
        "warnings": registry.warnings,
    }
