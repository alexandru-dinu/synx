import argparse
import random
import sys
from collections import defaultdict
from pathlib import Path

"""
<sym>: R1 | ... | Rn # OR
Ri: r1 ... rm        # AND
"""

# TODO: change to own class & kinds
Grammar = dict[str, list[list[str]]]


def parse_grammar(input_file: Path) -> Grammar:
    grammar = defaultdict(list)

    with open(args.input_file) as fp:
        lines = [x.strip() for x in fp]

    for i, line in enumerate(lines, start=1):
        # parse <sym> ::= rule
        try:
            sym, rules = map(lambda x: x.strip(), line.split("::="))
        except ValueError:
            print(f"{input_file}:{i}: ERROR: could not parse {line=}", file=sys.stderr)
            exit(1)

        # parse <rule> into a list of sub-rules (OR)
        # TODO: what if "|" is part of a string literal?
        # TODO: what if " " is part of a string literal?
        # TODO: mark string literals, e.g. (<KIND>, value)
        or_rules = list(map(lambda x: x.strip().split(), rules.split("|")))
        grammar[sym].extend(or_rules)

    return dict(grammar)


def generate_single(grammar: Grammar) -> str:
    # TODO: mark explicit start (will be easy when making Grammar into own class)
    # FIXME: for now, this is a simple, hardcoded, PoC

    max_depth = 5

    def inner(sym, depth=0):
        if depth == max_depth:
            return []

        out = []
        rule = random.choice(grammar[sym])

        for x in rule:
            print(f"{'  ' * depth}{sym} ::= {x} of {rule}")
            if x[0] == x[-1] == '"':  # terminal; TODO: change to <KIND>
                out.append(x[1:-1])
            else:
                assert x[0] == "<" and x[-1] == ">"  # non-terminal
                out.extend(inner(x, depth + 1))
        return out

    return inner("<start>")


def main(args):
    grammar = parse_grammar(args.input_file)
    # print_json(data=grammar)
    out = generate_single(grammar)
    print("".join(out))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Hello")
    parser.add_argument(
        "-f", "--input-file", type=Path, required=True, help="Path to the BNF."
    )
    args = parser.parse_args()

    main(args)
