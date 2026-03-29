from core.sub_agents import get_recommended_sub_agents, get_system_analysis_snapshot


def test_recommended_sub_agents_have_five_entries():
    agents = get_recommended_sub_agents()
    assert len(agents) == 5
    assert agents[0].priority == "P0"
    assert agents[0].key == "intent_context_guard"


def test_system_snapshot_has_expected_sections():
    snapshot = get_system_analysis_snapshot()
    assert set(snapshot.keys()) == {"strengths", "risks", "next_steps"}
    assert snapshot["strengths"]
    assert snapshot["risks"]
    assert snapshot["next_steps"]
