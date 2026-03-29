from core.data_tools import pick_retrieval_tools


def test_pick_retrieval_tools_supports_korean_query():
    query = "\uc624\ub298 \uc0dd\uc0b0 \ubcf4\uc5ec\uc918"
    assert "production" in pick_retrieval_tools(query)
