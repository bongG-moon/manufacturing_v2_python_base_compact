from dataclasses import dataclass, field
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class DatasetContract:
    key: str
    label: str
    description: str
    required_params: List[str] = field(default_factory=list)
    optional_params: List[str] = field(default_factory=list)
    date_policy: str = "required"
    default_group_by: List[str] = field(default_factory=list)


DATASET_CONTRACTS: Dict[str, DatasetContract] = {
    "production": DatasetContract(
        key="production",
        label="생산",
        description="생산 실적 조회",
        required_params=["date"],
        optional_params=["process_name", "product_name", "line_name", "mode", "den", "tech", "lead", "mcp_no"],
        default_group_by=["공정", "MODE", "라인"],
    ),
    "target": DatasetContract(
        key="target",
        label="목표",
        description="목표 수량 조회",
        required_params=["date"],
        optional_params=["process_name", "product_name", "line_name", "mode", "den", "tech", "lead", "mcp_no"],
        default_group_by=["공정", "MODE", "라인"],
    ),
    "defect": DatasetContract(
        key="defect",
        label="불량",
        description="불량률 및 불량 유형 조회",
        required_params=["date"],
        optional_params=["process_name", "product_name", "line_name", "mode", "den", "tech", "lead", "mcp_no"],
        default_group_by=["공정", "공정군", "MODE"],
    ),
    "equipment": DatasetContract(
        key="equipment",
        label="설비",
        description="설비 가동률 및 비가동 사유 조회",
        required_params=["date"],
        optional_params=["process_name", "line_name"],
        default_group_by=["라인", "공정"],
    ),
    "wip": DatasetContract(
        key="wip",
        label="WIP",
        description="재공 및 대기 상태 조회",
        required_params=["date"],
        optional_params=["process_name", "product_name", "line_name", "mode", "den", "tech"],
        default_group_by=["공정", "공정군", "라인"],
    ),
    "yield": DatasetContract(
        key="yield",
        label="수율",
        description="수율 및 주요 fail bin 조회",
        required_params=["date"],
        optional_params=["process_name", "product_name", "line_name", "mode", "den", "tech", "lead", "mcp_no"],
        default_group_by=["공정", "공정군", "MODE"],
    ),
    "hold": DatasetContract(
        key="hold",
        label="홀드",
        description="홀드 lot 및 사유 조회",
        required_params=["date"],
        optional_params=["process_name", "product_name", "line_name", "mode", "den", "tech", "mcp_no"],
        default_group_by=["공정", "공정군", "라인"],
    ),
    "scrap": DatasetContract(
        key="scrap",
        label="스크랩",
        description="스크랩 수량 및 loss cost 조회",
        required_params=["date"],
        optional_params=["process_name", "product_name", "line_name", "mode", "den", "tech", "mcp_no"],
        default_group_by=["공정", "공정군", "MODE"],
    ),
    "recipe": DatasetContract(
        key="recipe",
        label="레시피",
        description="공정 조건 및 레시피 조회",
        required_params=[],
        optional_params=["process_name", "product_name", "line_name", "mode", "den", "tech"],
        date_policy="optional",
        default_group_by=["공정", "라인"],
    ),
    "lot_trace": DatasetContract(
        key="lot_trace",
        label="LOT 이력",
        description="lot trace 및 route 상태 조회",
        required_params=[],
        optional_params=["process_name", "product_name", "line_name", "mode", "den", "tech", "mcp_no"],
        date_policy="optional",
        default_group_by=["공정", "공정군", "라인"],
    ),
}


PARAM_LABELS = {
    "date": "조회 날짜",
    "process_name": "공정",
    "product_name": "제품",
    "line_name": "라인",
    "mode": "MODE",
    "den": "DEN",
    "tech": "TECH",
    "lead": "LEAD",
    "mcp_no": "MCP",
}


def get_dataset_contract(dataset_key: str) -> DatasetContract | None:
    return DATASET_CONTRACTS.get(dataset_key)


def get_dataset_label(dataset_key: str) -> str:
    contract = get_dataset_contract(dataset_key)
    return contract.label if contract else dataset_key


def list_dataset_contracts() -> List[DatasetContract]:
    return list(DATASET_CONTRACTS.values())


def list_dataset_labels(dataset_keys: Iterable[str] | None = None) -> List[str]:
    keys = dataset_keys if dataset_keys is not None else DATASET_CONTRACTS.keys()
    return [get_dataset_label(key) for key in keys]


def find_missing_required_params(dataset_keys: Iterable[str], extracted_params: Dict[str, object]) -> Dict[str, List[str]]:
    missing: Dict[str, List[str]] = {}
    for dataset_key in dataset_keys:
        contract = get_dataset_contract(dataset_key)
        if not contract:
            continue
        missing_fields = [field for field in contract.required_params if not extracted_params.get(field)]
        if missing_fields:
            missing[dataset_key] = missing_fields
    return missing


def format_missing_params_message(dataset_keys: Iterable[str], extracted_params: Dict[str, object]) -> str | None:
    missing = find_missing_required_params(dataset_keys, extracted_params)
    if not missing:
        return None

    lines = ["조회에 필요한 조건이 부족합니다."]
    for dataset_key, fields in missing.items():
        label = get_dataset_label(dataset_key)
        field_labels = ", ".join(PARAM_LABELS.get(field, field) for field in fields)
        lines.append(f"- {label}: {field_labels}")
    lines.append("예: 오늘 생산 보여줘 / 20260324 목표 조회")
    return "\n".join(lines)


def format_available_datasets_message() -> str:
    lines = ["어떤 데이터를 조회할지 판단하지 못했습니다. 현재 조회 가능한 데이터는 아래와 같습니다."]
    for contract in list_dataset_contracts():
        lines.append(f"- {contract.label}: {contract.description}")
    return "\n".join(lines)
