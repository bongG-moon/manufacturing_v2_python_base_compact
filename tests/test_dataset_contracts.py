from core.dataset_contracts import (
    find_missing_required_params,
    format_available_datasets_message,
    format_missing_params_message,
    get_dataset_label,
)


def test_dataset_label_lookup():
    assert get_dataset_label("production") == "생산"


def test_missing_required_params_detects_date():
    missing = find_missing_required_params(["production", "target"], {"process_name": ["die_place"]})
    assert missing == {"production": ["date"], "target": ["date"]}


def test_optional_date_dataset_does_not_require_date():
    missing = find_missing_required_params(["recipe", "lot_trace"], {"process_name": ["die_place"]})
    assert missing == {}


def test_missing_params_message_is_user_friendly():
    message = format_missing_params_message(["production"], {"process_name": ["die_place"]})
    assert message is not None
    assert "생산" in message
    assert "조회 날짜" in message


def test_available_datasets_message_lists_known_datasets():
    message = format_available_datasets_message()
    assert "생산" in message
    assert "LOT 이력" in message
