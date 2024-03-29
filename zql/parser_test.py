import pytest
from zql.parser import parse_to_ast, query_to_tokens, ZqlParserError


def test_query_to_tokens():
    raw = " HI\ni,   LIKE\rit "
    actual = query_to_tokens(raw)
    expected = ["hi", "i", ",", "like", "it"]
    assert actual == expected


def test_missing_select():
    with pytest.raises(ZqlParserError) as err:
        parse_to_ast("hello")
        
        actual = str(err.value)
        expected = "Expected `its giving`, not `hello`."
        assert actual == expected


def test_missing_select_expr():
    with pytest.raises(ZqlParserError) as err:
        parse_to_ast("its giving")
        
        actual = str(err.value)
        expected = "Expected expression, not ``."
        assert actual == expected


def test_missing_from_after_expr():
    with pytest.raises(ZqlParserError) as err:
        parse_to_ast("its giving a from")
        
        actual = str(err.value)
        expected = "Expected `yass`, not `from`."
        assert actual == expected


def test_missing_from_after_expr_list():
    with pytest.raises(ZqlParserError) as err:
        parse_to_ast("its giving a, b from")
        
        actual = str(err.value)
        expected = "Expected `yass`, not `from`."
        assert actual == expected


def test_missing_table():
    with pytest.raises(ZqlParserError) as err:
        parse_to_ast("its giving a yass")
        
        actual = str(err.value)
        expected = "Expected table, not ``."
        assert actual == expected


def test_missing_limit():
    with pytest.raises(ZqlParserError) as err:
        parse_to_ast("its giving a yass table say")
        
        actual = str(err.value)
        expected = "Expected `say less`, not `say`."
        assert actual == expected


def test_missing_limit_amount():
    with pytest.raises(ZqlParserError) as err:
        parse_to_ast("its giving a yass table say less")
        
        actual = str(err.value)
        expected = "Expected integer, not ``."
        assert actual == expected


def test_missing_limit_amount_integer():
    with pytest.raises(ZqlParserError) as err:
        parse_to_ast("its giving a yass table say less five")
        
        actual = str(err.value)
        expected = "Expected integer, not `five`."
        assert actual == expected


def test_missing_terminal():
    with pytest.raises(ZqlParserError) as err:
        parse_to_ast("its giving a yass table say less 5")
        
        actual = str(err.value)
        expected = "You're cappin bro. Expected no cap, not ``."
        assert actual == expected


def test_missing_terminal_full():
    with pytest.raises(ZqlParserError) as err:
        parse_to_ast("its giving a yass table say less 5 no")
        
        actual = str(err.value)
        expected = "You're cappin bro. Expected no cap, not `no`."
        assert actual == expected


def test_missing_select_expr_list():
    with pytest.raises(ZqlParserError) as err:
        parse_to_ast("its giving a,")
        
        actual = str(err.value)
        expected = "Expected expression, not ``."
        assert actual == expected


def test_parse_to_ast_simple_select():
    raw_query = """
    its giving a, b
    yass example
    no cap
    """
    actual = parse_to_ast(raw_query)
    expected = {
        "type": "query",
        "children": [
            {
                "type": "select",
                "children": [
                    {"type": "expression", "value": "a"},
                    {"type": "expression", "value": "b"},
                ],
            },
            {
                "type": "from",
                "children": [{"type": "expression", "value": "example"}],
            },
            {"type": "terminal"},
        ]
    }
    assert actual == expected


def test_parse_to_ast_simple_select_with_limit():
    raw_query = """
    its giving a, b
    yass example
    say less 10
    no cap
    """
    actual = parse_to_ast(raw_query)
    expected = {
        "type": "query",
        "children": [
            {
                "type": "select",
                "children": [
                    {"type": "expression", "value": "a"},
                    {"type": "expression", "value": "b"},
                ],
            },
            {
                "type": "from",
                "children": [{"type": "expression", "value": "example"}],
            },
            {
                "type": "limit",
                "children": [{"type": "integer", "value": "10"}],
            },
            {"type": "terminal"},
        ]
    }
    assert actual == expected


def test_parse_to_ast_select_with_no_from():
    raw_query = """
    its giving 6
    no cap
    """
    actual = parse_to_ast(raw_query)
    expected = {
        "type": "query",
        "children": [
            {
                "type": "select",
                "children": [
                    {"type": "expression", "value": "6"},
                ],
            },
            {"type": "terminal"},
        ]
    }
    assert actual == expected


def test_parse_to_ast_where_clause_single_filter():
    raw_query = """
    its giving a
    yass example
    tfw a be b
    no cap
    """
    actual = parse_to_ast(raw_query)
    expected = {
        "type": "query",
        "children": [
            {
                "type": "select",
                "children": [
                    {"type": "expression", "value": "a"},
                ],
            },
            {
                "type": "from",
                "children": [{"type": "expression", "value": "example"}],
            },
            {
                "type": "where",
                "children": [
                    {
                        "type": "filter",
                        "value": "=",
                        "children": [
                            {"type": "expression", "value": "a"},
                            {"type": "expression", "value": "b"}
                        ]
                    }
                ]
            },
            {"type": "terminal"},
        ]
    }
    assert actual == expected


def test_parse_to_ast_where_clause_multi_filter():
    raw_query = """
    its giving a
    yass example
    tfw a be b
    fax a sike c
    uh b be c
    no cap
    """
    actual = parse_to_ast(raw_query)
    expected_where = {
        "type": "filter_branch",
        "value": "OR",
        "children": [
            {
                "type": "filter_branch",
                "value": "AND",
                "children": [
                    {
                        "type": "filter",
                        "value": "=",
                        "children": [
                            {"type": "expression", "value": "a"},
                            {"type": "expression", "value": "b"}
                        ]
                    },
                    {
                        "type": "filter",
                        "value": "!=",
                        "children": [
                            {"type": "expression", "value": "a"},
                            {"type": "expression", "value": "c"}
                        ]
                    }
                ]
            },
            {
                "type": "filter",
                "value": "=",
                "children": [
                    {"type": "expression", "value": "b"},
                    {"type": "expression", "value": "c"}
                ]
            }
        ]
    }
    expected = {
        "type": "query",
        "children": [
            {
                "type": "select",
                "children": [
                    {"type": "expression", "value": "a"},
                ],
            },
            {
                "type": "from",
                "children": [{"type": "expression", "value": "example"}],
            },
            {
                "type": "where",
                "children": [expected_where]
            },
            {"type": "terminal"},
        ]
    }
    assert actual == expected
