import ast
import multiprocessing
from typing import Any, Dict, List, Tuple

import pandas as pd


FORBIDDEN_NAMES = {
    "open",
    "exec",
    "eval",
    "compile",
    "__import__",
    "getattr",
    "setattr",
    "delattr",
    "globals",
    "locals",
    "vars",
    "os",
    "sys",
    "subprocess",
    "socket",
    "requests",
    "httpx",
}

FORBIDDEN_ATTRS = {
    "read_csv",
    "read_excel",
    "read_json",
    "read_html",
    "read_xml",
    "read_sql",
    "read_sql_query",
    "read_sql_table",
    "read_parquet",
    "read_pickle",
    "read_feather",
    "to_csv",
    "to_excel",
    "to_json",
    "to_html",
    "to_xml",
    "to_sql",
    "to_parquet",
    "to_pickle",
    "to_feather",
    "save",
    "load",
}

FORBIDDEN_NODES = (
    ast.Import,
    ast.ImportFrom,
    ast.With,
    ast.Try,
    ast.While,
    ast.AsyncFunctionDef,
    ast.ClassDef,
    ast.Delete,
)

SAFE_BUILTINS = {
    "len": len,
    "min": min,
    "max": max,
    "sum": sum,
    "sorted": sorted,
    "abs": abs,
    "round": round,
    "str": str,
    "int": int,
    "float": float,
    "list": list,
}

EXECUTION_TIMEOUT_SECONDS = 3


def _has_result_assignment(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "result":
                    return True
        if isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == "result":
                return True
    return False


def _call_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return ""


def _validate_calls(tree: ast.AST) -> Tuple[bool, str | None]:
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        call_name = _call_name(node)
        if call_name in FORBIDDEN_NAMES:
            return False, f"Forbidden function call: {call_name}"
        if call_name in FORBIDDEN_ATTRS:
            return False, f"Forbidden dataframe or IO call: {call_name}"
    return True, None


def validate_python_code(code: str) -> Tuple[bool, str | None]:
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return False, f"Generated pandas code has syntax error: {exc}"

    for node in ast.walk(tree):
        if isinstance(node, FORBIDDEN_NODES):
            return False, f"Forbidden syntax detected: {type(node).__name__}"
        if isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            return False, f"Forbidden name detected: {node.id}"
        if isinstance(node, ast.Attribute):
            if node.attr.startswith("__"):
                return False, "Dunder attribute access is not allowed."
            if node.attr in FORBIDDEN_ATTRS:
                return False, f"Forbidden attribute access detected: {node.attr}"

    ok, call_error = _validate_calls(tree)
    if not ok:
        return False, call_error

    if not _has_result_assignment(tree):
        return False, "Generated pandas code must assign the final DataFrame to `result`."

    return True, None


def _execute_worker(code: str, data: List[Dict[str, Any]], queue: multiprocessing.Queue) -> None:
    df = pd.DataFrame(data or [])
    local_vars = {"df": df.copy(), "pd": pd, "result": None}
    safe_globals = {"__builtins__": SAFE_BUILTINS}

    try:
        exec(code, safe_globals, local_vars)
    except Exception as exc:
        queue.put({"success": False, "error_message": f"Analysis code execution failed: {exc}", "data": []})
        return

    result = local_vars.get("result")
    if result is None:
        queue.put({"success": False, "error_message": "Analysis code did not populate result.", "data": []})
        return

    if isinstance(result, pd.Series):
        result = result.to_frame().reset_index()

    if not isinstance(result, pd.DataFrame):
        queue.put({"success": False, "error_message": "Analysis result must be a DataFrame.", "data": []})
        return

    result = result.where(pd.notnull(result), None)
    queue.put({"success": True, "data": result.to_dict(orient="records")})


def execute_safe_dataframe_code(code: str, data: List[Dict[str, Any]]) -> Dict[str, Any]:
    ok, error = validate_python_code(code)
    if not ok:
        return {"success": False, "error_message": error, "data": []}

    ctx = multiprocessing.get_context("spawn")
    queue = ctx.Queue()
    process = ctx.Process(target=_execute_worker, args=(code, data, queue))
    process.start()
    process.join(EXECUTION_TIMEOUT_SECONDS)

    if process.is_alive():
        process.terminate()
        process.join()
        return {
            "success": False,
            "error_message": f"Analysis code timed out after {EXECUTION_TIMEOUT_SECONDS} seconds.",
            "data": [],
        }

    if queue.empty():
        return {"success": False, "error_message": "Analysis worker exited without returning a result.", "data": []}
    return queue.get()
