import argparse
import os
import random
import sys
from dataclasses import dataclass, field
from itertools import count
from pathlib import Path

import exrex
from rich import print

"""
The BNF ADT defined using Haskell syntax:
```
data Expr = Terminal String | Symbol String | And [Expr] | Or [Expr]
```

In Python it's a bit verbose to translate this definition.
Also, it would be nice to have some sort of _macro_ that can generate
the code for dataclasses given a Haskell-like ADT definition.

Alternatively, we could have used enums to represent the `kind` of the expression
and define an expression object as a dataclass with the following fields:
```
kind: enum[Terminal, Symbol, And, Or]
union(
    name: str        # for literals & symbols
    children: [Expr] # for And & Or
)
```
"""


class Special:
    DEF = "::="
    AND_SEP = " "
    OR_SEP = "|"


@dataclass
class Expr:
    pass


@dataclass
class Terminal(Expr):
    atom: str
    is_re: bool = False  # distinguish b/w regex and literal, e.g.: r"[0-9]+" and "+"


@dataclass
class Symbol(Expr):
    atom: str


@dataclass
class And(Expr):
    children: list[Expr] = field(default_factory=list)


@dataclass
class Or(Expr):
    children: list[Expr] = field(default_factory=list)


"""
AST: mapping <symbol> names to expressions (substitution rules).
"""
Grammar = dict[str, Expr]


def _exit_with_error(
    msg: str, file: os.PathLike | None = None, line: int | None = None
) -> None:
    err = f"ERROR: {msg}"

    if file is not None and line is not None:
        print(f"{file}:{line}: {err}", file=sys.stderr)
    else:
        print(err, file=sys.stderr)

    exit(1)


def is_quote(c: str) -> bool:
    return c in ('"', "'")


def syntax_aware_split(x: str, sep: str) -> list[str]:
    """
    Split a string by `sep` accounting for literals.

    TODO: write a more idiomatic version.
    """
    groups: list[list[str]] = []
    cur: list[str] = []
    in_paren = False
    m = len(sep)
    i = 0

    while i < len(x):
        try:
            if x[i : i + m] == sep and not in_paren:
                groups.append(cur)
                cur = []
                i += m
                continue
        except IndexError as e:
            _exit_with_error(str(e))

        # TODO: differentiate b/w ' and "
        if is_quote(x[i]):
            in_paren ^= True

        cur.append(x[i])
        i += 1

    if cur:
        groups.append(cur)

    return ["".join(g) for g in groups]


def parse_atomic(x: str) -> Expr:
    match list(x):
        case ['"', *ss, '"'] | ["'", *ss, "'"]:
            return Terminal(atom="".join(ss), is_re=False)

        case ["r", '"', *ss, '"'] | ["r", "'", *ss, "'"]:
            return Terminal(atom=r"".join(ss), is_re=True)

        case ["<", *_, ">"]:
            return Symbol(atom=x)

        case _:
            _exit_with_error(f"Invalid atom: {x}")

    assert False, "unreachable"


def parse_and(x: str) -> Expr:
    values = [
        parse_atomic(item.strip())
        for item in syntax_aware_split(x, sep=Special.AND_SEP)
    ]
    if len(values) == 1:
        return values[0]
    else:
        return And(children=values)


def parse_or(x: str) -> Expr:
    values = [
        parse_and(item.strip()) for item in syntax_aware_split(x, sep=Special.OR_SEP)
    ]
    if len(values) == 1:
        return values[0]
    else:
        return Or(children=values)


def parse_grammar(input_file: Path) -> Grammar:
    grammar = {}

    with open(input_file) as fp:
        lines = [x.strip() for x in fp]

    for i, line in enumerate(lines, start=1):
        try:
            sym, rule = map(
                lambda x: x.strip(), syntax_aware_split(line, sep=Special.DEF)
            )
        except ValueError:
            _exit_with_error(f"could not parse {line=}", file=input_file, line=i)

        grammar[sym] = parse_or(rule)

    return dict(grammar)


def generate_single(
    grammar: Grammar, start: str, max_depth: int, verbose: bool = False
) -> list[str]:
    """
    Generate a single list of tokens from the `grammar`, given the `start` symbol.
    """

    def _inner(expr: Expr, depth: int = 0) -> list[str] | None:
        if depth == max_depth:
            return None

        if verbose:
            print(f'[{depth}]{" " * depth}>{expr}')

        match expr:
            case Or() as x:
                assert x.children is not None
                return _inner(random.choice(x.children), depth)

            case And() as x:
                assert x.children is not None
                out = []
                for c in x.children:
                    if (y := _inner(c, depth + 1)) is not None:
                        out.extend(y)
                    else:
                        return None
                return out

            case Terminal() as x:
                assert x.atom is not None
                return [exrex.getone(x.atom)] if x.is_re else [x.atom]

            case Symbol() as x:
                assert x.atom is not None
                if x.atom not in grammar:
                    _exit_with_error(
                        f"Symbol {x.atom} is not part of the grammar. Available symbols: {list(grammar.keys())}"
                    )
                return _inner(grammar[x.atom], depth)

            case _:
                _exit_with_error(f"Invalid expression: {expr}")

        assert False, "unreachable"

    for k in count(1):
        if (out := _inner(Symbol(atom=start))) is not None:
            if verbose:
                print(f"Computed in {k} trial(s)")
            return out


def main(args):
    grammar = parse_grammar(args.input_file)
    # print(grammar)
    out = generate_single(grammar, args.start, args.max_depth, args.verbose)
    # print(out)
    print("".join(out))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Generate random strings given a BNF grammar.")
    parser.add_argument(
        "-f", "--input-file", type=Path, required=True, help="Path to the BNF."
    )
    parser.add_argument(
        "-s", "--start", type=str, required=True, help="Starting symbol."
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
