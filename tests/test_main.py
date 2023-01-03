from synx.synx import Expr, generate_single, parse_grammar
from tests.conftest import safe_eval


def test_parse_all_grammars(data_dir):
    """
    Parsing all grammars yields an AST in the form of `{symbol_name (str): Expr}`
    """
    for path in data_dir.glob("**/*.bnf"):
        grammar = parse_grammar(path)
        assert isinstance(grammar, dict)
        for k, v in grammar.items():
            assert isinstance(k, str)
            assert isinstance(v, Expr)


def test_generate_simple_expr(data_dir):
    """
    Generating simple expressions.
    """
    grammar = parse_grammar(data_dir / "expr.bnf")

    for _ in range(100):
        s = "".join(generate_single(grammar, start="<expr>", max_depth=2))
        assert isinstance(safe_eval(s), int)
