from synx.synx import Expr, parse_grammar


def test_parse_ok(data_dir):
    """
    Test that parsing a grammar yields an AST in the form of
    a mapping from symbol names (str) to expressions.
    """
    for path in data_dir.glob("**/*.bnf"):
        grammar = parse_grammar(path)
        assert isinstance(grammar, dict)
        for k, v in grammar.items():
            assert isinstance(k, str)
            assert isinstance(v, Expr)
