import argparse
import random
import sys
from dataclasses import dataclass
from pathlib import Path

from rich import print

"""
The BNF ADT defined using Haskell syntax:
```
data Expr = Literal String | Symbol String | And [Expr] | Or [Expr]
```

In Python it's a bit verbose to translate this definition.
Also, it would be nice to have some sort of _macro_ that can generate
the code for dataclasses given a Haskell-like ADT definition.

Alternatively, we could have used enums to represent the `kind` of the expression
and define an expression object as a dataclass with the following fields:
```
kind: enum[Literal, Symbol, And, Or]
union(
    name: str        # for literals & symbols
    children: [Expr] # for And & Or
)
```
"""


@dataclass
class Expr:
    # union
    atom: str = None
    children: list = None


@dataclass
class Literal(Expr):
    pass


@dataclass
class Symbol(Expr):
    pass


@dataclass
class And(Expr):
    pass


@dataclass
class Or(Expr):
    pass


"""
AST: mapping <symbol> names to expressions (substitution rules).
"""
Grammar = dict[str, Expr]


def parse_atomic(x: str) -> Expr:
    match x[0]:
        case '"' | "'":
            return Literal(atom=x.strip()[1:-1])
        case "<":
            return Symbol(atom=x)
        case _:
            raise ValueError(f"Invalid atom: {x}")


def parse_and(x: str) -> Expr:
    """
    TODO: careful when splitting by sep that can be part of literals.
    """
    values = [parse_atomic(item.strip()) for item in x.split(" ")]
    if len(values) == 1:
        return values[0]
    else:
        return And(children=values)


def parse_or(x: str) -> Expr:
    """
    TODO: careful when splitting by sep that can be part of literals.
    """
    values = [parse_and(item.strip()) for item in x.split("|")]
    if len(values) == 1:
        return values[0]
    else:
        return Or(children=values)


def parse_grammar(input_file: Path) -> Grammar:
    grammar = {}

    with open(args.input_file) as fp:
        lines = [x.strip() for x in fp]

    for i, line in enumerate(lines, start=1):
        try:
            # TODO: careful when splitting by sep that can be part of literals.
            sym, rule = map(lambda x: x.strip(), line.split("::="))
        except ValueError:
            print(f"{input_file}:{i}: ERROR: could not parse {line=}", file=sys.stderr)
            exit(1)

        grammar[sym] = parse_or(rule)

    return dict(grammar)


def generate_single(
    grammar: Grammar, start: str, max_depth: int, verbose: bool = False
) -> list[str]:
    """
    Generate a single list of tokens from the `grammar`, given the `start` symbol.
    """

    def _inner(expr, depth=0):
        if depth == max_depth:
            return []

        if verbose:
            print(f'{"  " * depth}>{expr}')

        match expr:
            case Or() as x:
                return _inner(random.choice(x.children), depth + 1)

            case And() as x:
                return sum((_inner(c, depth + 1) for c in x.children), [])

            case Literal() as x:
                return [x.atom]

            case Symbol() as x:
                if x.atom not in grammar:
                    raise ValueError(f"Symbol {x.atom} is not part of the grammar")
                return _inner(grammar[x.atom], depth)

    return _inner(Symbol(atom=start))


def main(args):
    grammar = parse_grammar(args.input_file)
    # print(grammar)
    out = generate_single(
        grammar, start="<start>", max_depth=args.max_depth, verbose=args.verbose
    )
    # print(out)
    print("".join(out))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Hello")
    parser.add_argument(
        "-f", "--input-file", type=Path, required=True, help="Path to the BNF."
    )
    parser.add_argument(
        "-d",
        "--max-depth",
        type=int,
        default=5,
        help="Max depth when generating a string from the grammar.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Whether to show debug info during generation.",
    )
    args = parser.parse_args()

    main(args)
