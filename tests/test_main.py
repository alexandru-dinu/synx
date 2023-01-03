import ast

from hypothesis import given, settings
from hypothesis import strategies as st

from synx.synx import Expr, generate_single, parse_grammar
from tests.conftest import DATA_DIR


def test_parse_all_grammars():
    """
    Parsing all grammars yields an AST in the form of `{symbol_name (str): Expr}`
    """
    for path in DATA_DIR.glob("**/*.bnf"):
        grammar = parse_grammar(path)
        assert isinstance(grammar, dict)
        for k, v in grammar.items():
            assert isinstance(k, str)
            assert isinstance(v, Expr)


@settings(max_examples=1_000)
@given(
    num_trials=st.integers(min_value=10, max_value=100),
    max_depth=st.integers(min_value=1, max_value=20),
)
def test_generate_simple_expr(num_trials, max_depth):
    """
    Generating simple expressions.
    """
    grammar = parse_grammar(DATA_DIR / "expr_rec.bnf")

    for _ in range(num_trials):
        s = "".join(generate_single(grammar, start="<expr>", max_depth=max_depth))
        expr = ast.parse(s, mode="eval")
        assert isinstance(expr, ast.Expression)
