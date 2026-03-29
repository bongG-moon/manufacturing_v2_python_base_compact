from core.safe_code_executor import execute_safe_dataframe_code, validate_python_code


def test_blocks_pandas_read_io_calls():
    ok, error = validate_python_code("result = pd.read_csv('dummy.csv')")
    assert not ok
    assert "read_csv" in str(error)


def test_blocks_dataframe_write_io_calls():
    ok, error = validate_python_code("df.to_csv('out.csv')\nresult = df")
    assert not ok
    assert "to_csv" in str(error)


def test_allows_lambda_for_grouped_mode_like_logic():
    ok, error = validate_python_code(
        "result = df.groupby('group', as_index=False).agg(top_value=('value', lambda s: s.max()))"
    )
    assert ok, error


def test_executes_simple_dataframe_plan():
    result = execute_safe_dataframe_code(
        "result = df.groupby('group', as_index=False).agg(total=('value', 'sum'))",
        [{"group": "A", "value": 1}, {"group": "A", "value": 2}, {"group": "B", "value": 3}],
    )
    assert result["success"] is True
    assert result["data"] == [{"group": "A", "total": 3}, {"group": "B", "total": 3}]
