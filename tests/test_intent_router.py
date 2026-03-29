from core.intent_router import build_route_clarification_message, classify_query_mode, should_ask_route_clarification


def test_intent_router_prefers_retrieval_without_current_data():
    result = classify_query_mode("오늘 생산 보여줘", None)
    assert result["mode"] == "retrieval"


def test_intent_router_prefers_followup_when_current_data_exists():
    current_data = {
        "data": [{"공정": "die_place", "production": 100}],
        "columns": ["공정", "production"],
    }
    result = classify_query_mode("공정별 상위 3개로 정렬해줘", current_data)
    assert result["mode"] == "followup_transform"


def test_intent_router_prefers_retrieval_when_new_dataset_is_explicit():
    current_data = {
        "data": [{"공정": "die_place", "production": 100}],
        "columns": ["공정", "production"],
    }
    result = classify_query_mode("오늘 목표 데이터 다시 조회해줘", current_data)
    assert result["mode"] == "retrieval"


def test_intent_router_low_confidence_triggers_clarification():
    current_data = {
        "data": [{"공정": "die_place", "production": 100}],
        "columns": ["공정", "production"],
    }
    result = classify_query_mode("목표 비교", current_data)
    assert result["confidence"] == "low"
    assert should_ask_route_clarification(result, current_data) is True
    message = build_route_clarification_message(result, current_data)
    assert "애매합니다" in message
    assert "새 조회" in message
