import pytest
from zql.grammar import AstParseError, get_tokens, parse_grammar, parse_ast


FORMULA_GRAMMAR_CONTENT = r"""
    root     : formula
             ;
    formula  : expr operator expr
             | expr
             ;
    expr     : open formula close
             | word
             | number
             ;
    open     : "("
             ;
    close    : ")"
             ;
    word     : r[a-zA-Z][\w$]*
             ;
    number   : r[0-9]+
             ;
    operator : "+"
             | "-"
             | "*"
             | "/"
             ;
"""
FORMULA_GRAMMAR = parse_grammar(FORMULA_GRAMMAR_CONTENT)


def test_get_tokens():
    source = """
    (A + 12) - 0
    """
    actual = get_tokens(source)
    expected = ["(", "a", "+", "12", ")", "-", "0"]
    assert actual == expected


def test_parse_grammar_formula():
    actual = parse_grammar(FORMULA_GRAMMAR_CONTENT)
    expected = {
        "root": [
            {"sequence": ["formula"]},
        ],
        "formula": [
            {"sequence": ["expr", "operator", "expr"]},
            {"sequence": ["expr"]},
        ],
        "expr": [
            {"sequence": ["open", "formula", "close"]},
            {"sequence": ["word"]},
            {"sequence": ["number"]},
        ],
        "open": [
            {"literal": "("},
        ],
        "close": [
            {"literal": ")"},
        ],
        "word": [
            {"regex": r"[a-zA-Z][\w$]*"},
        ],
        "number": [
            {"regex": r"[0-9]+"},
        ],
        "operator": [
            {"literal": "+"},
            {"literal": "-"},
            {"literal": "*"},
            {"literal": "/"},
        ],
    }
    assert actual == expected


def test_parse_ast_formula_simple():
    actual = parse_ast(FORMULA_GRAMMAR, "7 * c")
    expected = {
        "type": "formula",
        "children": [
            {
                "type": "expr",
                "children": [
                    {"type": "number", "value": "7"}
                ],
            },
            {
                "type": "operator",
                "value": "*"
            },
            {
                "type": "expr",
                "children": [
                    {"type": "word", "value": "c"}
                ],
            },
        ],
    }
    assert actual == expected
    

def test_parse_ast_formula_nested():
    actual = parse_ast(FORMULA_GRAMMAR, "(A + 12) - 0")

    expected = {
        "type": "formula",
        "children": [
            {
                "type": "expr",
                "children": [
                    {"type": "open", "value": "("},
                    {
                        "type": "formula",
                        "children": [
                            {
                                "type": "expr",
                                "children": [
                                    {"type": "word", "value": "a"}
                                ],
                            },
                            {
                                "type": "operator",
                                "value": "+"
                            },
                            {
                                "type": "expr",
                                "children": [
                                    {"type": "number", "value": "12"}
                                ],
                            },
                        ],
                    },
                    {"type": "close", "value": ")"},
                ],
            },
            {"type": "operator", "value": "-"},
            {
                "type": "expr",
                "children": [
                    {"type": "number", "value": "0"}
                ],
            },
        ],
    }
    assert actual == expected


def test_parse_ast_formula_fail_first_token():
    with pytest.raises(AstParseError) as err:
        parse_ast(FORMULA_GRAMMAR, "_7 * c")
    actual = str(err.value)
    expected = "Expected `_7` to match `[0-9]+`."
    assert actual == expected


def test_parse_ast_formula_fail_unparsed_tokens_remain():
    with pytest.raises(AstParseError) as err:
        parse_ast(FORMULA_GRAMMAR, "7 * c + 3")
    actual = str(err.value)
    expected = "Satisfied `root` rule, but unparsed tokens remain: ['+', '3']"
    assert actual == expected


def test_parse_ast_formula_fail_no_source():
    with pytest.raises(AstParseError) as err:
        parse_ast(FORMULA_GRAMMAR, "")
    actual = str(err.value)
    expected = "Expected match for `[0-9]+`, not end of input."
    assert actual == expected