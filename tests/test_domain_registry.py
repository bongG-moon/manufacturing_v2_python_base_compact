from core.domain_registry import get_dataset_keyword_map, get_domain_registry_summary, load_domain_registry


def test_domain_registry_loads_sample_file():
    registry = load_domain_registry()
    assert "sample_custom_domain.md" in registry.loaded_files


def test_domain_registry_exposes_dataset_keywords():
    keyword_map = get_dataset_keyword_map()
    assert "production" in keyword_map
    assert "생산" == keyword_map["production"]["label"]
    assert any("일일 생산" == keyword for keyword in keyword_map["production"]["keywords"])


def test_domain_registry_summary_contains_process_groups():
    summary = get_domain_registry_summary()
    assert "DIE_ATTACH" in summary["process_groups"]
