# `synx`

[![Build](https://github.com/alexandru-dinu/synx/actions/workflows/main.yml/badge.svg)](https://github.com/alexandru-dinu/synx/actions/workflows/main.yml)

Generate random strings given a grammar in [BNF][1].

The name "synx" (pronounced "syn-x"; rhymes with "synapse") is a wordplay on "syn*ta*x". `synx` can be used to construct fuzzy _syntactical_ tests, e.g. checking whether a parser for a given grammar is correct [^1].

## Usage
```
usage: Generate random strings given a BNF grammar. [-h] -f INPUT_FILE -s
                                                    START [-d MAX_DEPTH] [-v]

options:
  -h, --help            show this help message and exit
  -f INPUT_FILE, --input-file INPUT_FILE
                        Path to the BNF.
  -s START, --start START
                        Starting symbol.
  -d MAX_DEPTH, --max-depth MAX_DEPTH
                        Max depth when generating a string from the grammar.
  -v, --verbose         Whether to show debug info during generation.
```

## Example
Here is a simple example of a non-recursive grammar:
```
<expr> ::= <num> <op> <num>
<num>  ::= r"[1-9][0-9]{0,5}"
<op>   ::= "+" | "-"
```
- symbol `<num>` is marked as a regex pattern, because it starts with `r"`
- symbol `<op>` is a string literal: either `+` or `-`

Parsing this grammar yields the following AST:
```python
{
    '<expr>': And(
        atom=None,
        children=[
            Symbol(atom='<num>', children=None),
            Symbol(atom='<op>', children=None),
            Symbol(atom='<num>', children=None)
        ]
    ),
    '<num>': Terminal(atom='[1-9][0-9]{0,5}', children=None, is_re=True),
    '<op>': Or(
        atom=None,
        children=[
            Terminal(atom='+', children=None, is_re=False),
            Terminal(atom='-', children=None, is_re=False)
        ]
    )
}
```
which can be used to generate strings from:
```console
$ python synx/synx.py -f grammars/expr.bnf -s "<expr>"
87662+14
```

Generating random strings from regular expressions is done using the [exrex][2] package.

[1]: https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form
[2]: https://github.com/asciimoo/exrex
[^1]: Inspired by [@rexim](https://github.com/rexim) on a [twitch stream](https://www.twitch.tv/videos/1693721389)
