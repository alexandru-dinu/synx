import ast
from pathlib import Path

import pytest


@pytest.fixture
def data_dir():
    return Path(__file__).parents[1] / "grammars"


def safe_eval(expr: str):
    return eval(compile(ast.parse(expr, mode="eval"), "<node>", "eval"), {}, {})
