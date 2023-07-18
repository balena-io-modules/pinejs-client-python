from typing import Any, Dict
import pytest
from .helper import assert_compile
from datetime import datetime


def filter_test(input: Any, output: str):
    resource = "test"
    count_output = resource + "/$count?$filter=" + output
    output = resource + "?$filter=" + output

    assert_compile({"resource": resource, "options": {"$filter": input}}, output)

    assert_compile(
        {"resource": f"{resource}/$count", "options": {"$filter": input}}, count_output
    )

    assert_compile(
        {"resource": f"{resource}", "options": {"$count": {"$filter": input}}},
        count_output,
    )


def test_filters():
    filter_test({"a": "b", "d": "e"}, "(a eq 'b') and (d eq 'e')")

    filter_test(
        {
            "a": "b'c",
            "d": "e''f'''g",
        },
        "(a eq 'b''c') and (d eq 'e''''f''''''g')",
    )


def test_operators():
    def operator_test(operator: str):
        def create_filter(f: Any) -> Dict[str, Any]:
            return {f"${operator}": f}

        filter_test(
            create_filter(
                {
                    "a": {"@": "b"},
                    "c": {"@": "d"},
                }
            ),
            f"(a eq @b) {operator} (c eq @d)",
        )

        filter_test(
            create_filter(
                {
                    "a": "b",
                    "c": "d",
                }
            ),
            f"(a eq 'b') {operator} (c eq 'd')",
        )

        filter_test(
            create_filter([{"a": "b"}, {"c": "d"}]), f"(a eq 'b') {operator} (c eq 'd')"
        )

        filter_test({"a": create_filter("b")}, f"a {operator} 'b'")

        filter_test({"a": create_filter(["b", "c"])}, f"a eq ('b' {operator} 'c')")

        filter_test(
            {"a": create_filter({"b": "c", "d": "e"})},
            f"a eq ((b eq 'c') {operator} (d eq 'e'))",
        )

        filter_test({"a": create_filter({"$": "b"})}, f"a {operator} b")

        filter_test({"a": create_filter({"$": ["b", "c"]})}, f"a {operator} b/c")

        raw_date_time = "datetime'2015-10-20T14%3A04%3A05.374Z'"
        filter_test(
            {"a": create_filter({"$raw": raw_date_time})},
            f"a {operator} ({raw_date_time})",
        )

        with pytest.raises(Exception) as err:
            filter_test({"a": create_filter({"$duration": "P6D"})}, "")
        assert "Expected type for $duration, got: <class 'str'>" in str(err)

        filter_test(
            {
                "a": create_filter(
                    {
                        "$duration": {
                            "negative": True,
                            "days": 6,
                            "hours": 23,
                            "minutes": 59,
                            "seconds": 59.9999,
                        }
                    }
                )
            },
            f"a {operator} duration'-P6DT23H59M59.9999S'",
        )

        filter_test(
            {"a": create_filter({"$duration": {"days": 6}})},
            f"a {operator} duration'P6D'",
        )

        filter_test(
            {"a": create_filter({"$duration": {"hours": 23}})},
            f"a {operator} duration'PT23H'",
        )

        filter_test(
            {"a": create_filter({"$duration": {"seconds": 10}})},
            f"a {operator} duration'PT10S'",
        )

        filter_test(
            {"a": create_filter({"$duration": {"minutes": 1}})},
            f"a {operator} duration'PT1M'",
        )

        filter_test(
            {
                "a": create_filter(
                    {
                        "$sub": [
                            {"$now": {}},
                            {
                                "$duration": {
                                    "days": 6,
                                    "hours": 23,
                                    "minutes": 59,
                                    "seconds": 59.9999,
                                },
                            },
                        ],
                    }
                ),
            },
            f"a {operator} (now() sub duration'P6DT23H59M59.9999S')",
        )

        filter_test(
            {"a": create_filter({"$or": [{"$": "b"}, {"$": "c"}]})},
            f"a {operator} (b or c)",
        )

    operator_test("ne")
    operator_test("eq")
    operator_test("gt")
    operator_test("ge")
    operator_test("lt")
    operator_test("le")
    operator_test("add")
    operator_test("sub")
    operator_test("mul")
    operator_test("div")
    operator_test("mod")


def test_functions():
    def function_test(fn_name: str):
        def create_filter(f: Any) -> Dict[str, Any]:
            return {f"${fn_name}": f}

        filter_test(create_filter(None), f"{fn_name}()")

        filter_test(
            create_filter({"a": "b", "c": "d"}), f"{fn_name}(a eq 'b',c eq 'd')"
        )

        filter_test(
            create_filter([{"a": "b"}, {"c": "d"}]), f"{fn_name}(a eq 'b',c eq 'd')"
        )

        filter_test({"a": create_filter("b")}, f"{fn_name}(a,'b')")

        filter_test({"a": create_filter(["b", "c"])}, f"a eq {fn_name}('b','c')")

        filter_test(
            {"a": create_filter({"b": "c", "d": "e"})},
            f"a eq {fn_name}(b eq 'c',d eq 'e')",
        )

    function_test("contains")
    function_test("endswith")
    function_test("startswith")
    function_test("length")
    function_test("indexof")
    function_test("substring")
    function_test("tolower")
    function_test("toupper")
    function_test("trim")
    function_test("concat")
    function_test("year")
    function_test("month")
    function_test("day")
    function_test("hour")
    function_test("minute")
    function_test("second")
    function_test("fractionalseconds")
    function_test("date")
    function_test("time")
    function_test("totaloffsetminutes")
    function_test("now")
    function_test("maxdatetime")
    function_test("mindatetime")
    function_test("totalseconds")
    function_test("round")
    function_test("floor")
    function_test("ceiling")
    function_test("isof")
    function_test("cast")


def test_operands():
    filter_test({"a": "b"}, "a eq 'b'")
    filter_test({"a": 1}, "a eq 1")
    filter_test({"a": True}, "a eq true")
    filter_test({"a": False}, "a eq false")
    filter_test({"a": None}, "a eq null")

    d = datetime(1995, 12, 21)
    filter_test({"a": d}, "a eq datetime'1995-12-21T00:00:00.0Z'")


def test_mixing_operators():
    filter_test(
        {
            "$ne": [
                {
                    "$eq": {
                        "a": "b",
                        "c": "d",
                    },
                },
                {"e": "f"},
            ],
        },
        "((a eq 'b') eq (c eq 'd')) ne (e eq 'f')",
    )

    filter_test(
        [
            {
                "$eq": {
                    "a": "b",
                    "c": "d",
                },
            },
            {
                "$ne": {
                    "e": "f",
                    "g": "h",
                },
            },
        ],
        "((a eq 'b') eq (c eq 'd')) or ((e eq 'f') ne (g eq 'h'))",
    )

    filter_test(
        {
            "$ne": [
                {
                    "$eq": [{"a": "b"}, {"d": "e"}],
                },
                {"c": "d"},
            ],
        },
        "((a eq 'b') eq (d eq 'e')) ne (c eq 'd')",
    )

    filter_test(
        {
            "a": {
                "b": "c",
            },
        },
        "a/b eq 'c'",
    )

    filter_test(
        {
            "a": {
                "b": "c",
                "d": "e",
            },
        },
        "(a/b eq 'c') and (a/d eq 'e')",
    )

    filter_test(
        {
            "a": [{"b": "c"}, {"d": "e"}],
        },
        "a eq ((b eq 'c') or (d eq 'e'))",
    )

    filter_test(
        {
            "a": ["c", "d"],
        },
        "a eq ('c' or 'd')",
    )

    filter_test(
        {
            "a": {
                "b": ["c", "d"],
            },
        },
        "a/b eq ('c' or 'd')",
    )

    filter_test(
        {
            "a": [{"b": "c"}, "d"],
        },
        "a eq ((b eq 'c') or 'd')",
    )

    filter_test(
        {
            "a": {
                "b": "c",
                "$eq": "d",
            },
        },
        "(a/b eq 'c') and (a eq 'd')",
    )

    with pytest.raises(Exception) as err:
        filter_test({"@": True}, "")
    assert "Parameter alias reference must be a string, got" in str(err)

    filter_test({"$raw": "(a/b eq 'c' and a eq 'd')"}, "((a/b eq 'c' and a eq 'd'))")

    with pytest.raises(Exception) as err:
        filter_test({"$raw": True}, "")
    # TODO: check why the error above has a different error than the node client

    filter_test([{"$raw": "a ge b"}, {"$raw": "a le c"}], "(a ge b) or (a le c)")

    filter_test(
        {
            "a": {
                "b": [{"$raw": "c ge d"}, {"$raw": "d le e"}],
            },
        },
        "a/b eq ((c ge d) or (d le e))",
    )

    filter_test(
        {
            "a": {
                "b": {
                    "$and": [{"$raw": "c ge d"}, {"$raw": "e le f"}],
                }
            },
        },
        "a/b eq ((c ge d) and (e le f))",
    )


def test_raw_arrays():
    filter_test(
        {
            "$raw": ["a/b eq $1 and a eq $2", "c", "d"],
        },
        "(a/b eq ('c') and a eq ('d'))",
    )

    with pytest.raises(Exception) as err:
        filter_test({"$raw": [True]}, "")
    assert "First element of array for $raw must be a string" in str(err)

    filter_test(
        {
            "$raw": [
                "a/b eq $1 and a eq $2",
                {"c": "d"},
                {
                    "$add": [1, 2],
                },
            ],
        },
        "(a/b eq (c eq 'd') and a eq (1 add 2))",
    )

    filter_test(
        {
            "$raw": ["a/b eq $1", {"$raw": "$"}],
        },
        "(a/b eq (($$)))",
    )

    filter_test(
        {
            "$raw": [
                "a/b eq $10 and a eq $1",
            ]
            + [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        },
        "(a/b eq (10) and a eq (1))",
    )


def test_raw_objects():
    # TODO: check why I dont work with int keys
    filter_test(
        {
            "$raw": {
                "$string": "a/b eq $1 and a eq $2",
                "1": "c",
                "2": "d",
            },
        },
        "(a/b eq ('c') and a eq ('d'))",
    )

    with pytest.raises(Exception) as err:
        filter_test(
            {
                "$raw": {
                    "$string": True,
                },
            },
            "",
        )

    assert "$string element of object for $raw must be a string" in str(err)

    with pytest.raises(Exception) as err:
        filter_test(
            {
                "$raw": {
                    "$string": "",
                    "$invalid": "",
                },
            },
            "",
        )

    assert "$raw param names must contain only [a-zA-Z0-9], got" in str(err)

    filter_test(
        {
            "$raw": {
                "$string": "a/b eq $1 and a eq $2",
                "1": {"c": "d"},
                "2": {"$add": [1, 2]},
            },
        },
        "(a/b eq (c eq 'd') and a eq (1 add 2))",
    )

    filter_test(
        {
            "$raw": {
                "$string": "a/b eq $1",
                "1": {"$raw": "$"},
            },
        },
        "(a/b eq (($$)))",
    )

    filter_test(
        {
            "$raw": {
                "$string": "a/b eq $10 and a eq $1",
                "1": 1,
                "10": 10,
            },
        },
        "(a/b eq (10) and a eq (1))",
    )

    filter_test(
        {
            "$raw": {
                "$string": "a eq $a and b eq $b or b eq $b2",
                "a": "a",
                "b": "b",
                "b2": "b2",
            },
        },
        "(a eq ('a') and b eq ('b') or b eq ('b2'))",
    )


def test_and():
    filter_test(
        {
            "a": {
                "b": {
                    "$and": ["c", "d"],
                },
            },
        },
        "a/b eq ('c' and 'd')",
    )

    filter_test(
        {
            "a": {
                "b": {
                    "$and": [{"c": "d"}, {"e": "f"}],
                },
            },
        },
        "a/b eq ((c eq 'd') and (e eq 'f'))",
    )


def test_or():
    filter_test(
        {
            "a": {
                "b": {
                    "$or": ["c", "d"],
                },
            },
        },
        "a/b eq ('c' or 'd')",
    )

    filter_test(
        {
            "a": {
                "b": {
                    "$or": [{"c": "d"}, {"e": "f"}],
                },
            },
        },
        "a/b eq ((c eq 'd') or (e eq 'f'))",
    )


def test_in():
    filter_test(
        {
            "a": {
                "b": {
                    "$in": ["c"],
                },
            },
        },
        "a/b in ('c')",
    )

    filter_test(
        {
            "a": {
                "b": {
                    "$in": ["c", "d"],
                },
            },
        },
        "a/b in ('c', 'd')",
    )

    filter_test(
        {
            "a": {
                "b": {
                    "$in": [{"c": "d"}, {"e": "f"}],
                },
            },
        },
        "(a/b/c eq 'd') or (a/b/e eq 'f')",
    )

    filter_test(
        {
            "a": {
                "b": {
                    "$in": {
                        "c": "d",
                    },
                },
            },
        },
        "a/b/c eq 'd'",
    )

    filter_test(
        {
            "a": {
                "b": {
                    "$in": {
                        "c": "d",
                        "e": "f",
                    },
                },
            },
        },
        "(a/b/c eq 'd') or (a/b/e eq 'f')",
    )

    filter_test(
        {
            "a": {
                "b": {
                    "$in": "c",
                },
            },
        },
        "a/b eq 'c'",
    )


def test_not():
    filter_test({"$not": "a"}, "not('a')")

    filter_test(
        {
            "$not": {
                "a": "b",
            },
        },
        "not(a eq 'b')",
    )

    filter_test(
        {
            "$not": {
                "a": "b",
                "c": "d",
            },
        },
        "not((a eq 'b') and (c eq 'd'))",
    )

    filter_test(
        {
            "$not": [{"a": "b"}, {"c": "d"}],
        },
        "not((a eq 'b') or (c eq 'd'))",
    )

    filter_test(
        {
            "a": {
                "$not": "b",
            },
        },
        "a eq not('b')",
    )

    filter_test(
        {
            "a": {
                "$not": ["b", "c"],
            },
        },
        "a eq not('b' or 'c')",
    )

    filter_test(
        {
            "a": {
                "$not": {
                    "b": "c",
                    "d": "e",
                },
            },
        },
        "a eq not((b eq 'c') and (d eq 'e'))",
    )

    filter_test(
        {
            "a": {
                "$not": [{"b": "c"}, {"d": "e"}],
            },
        },
        "a eq not((b eq 'c') or (d eq 'e'))",
    )


def test_dollar():
    filter_test(
        {
            "a": {
                "$": "b",
            },
        },
        "a eq b",
    )

    filter_test(
        {
            "a": {
                "b": {
                    "$": "c",
                },
            },
        },
        "a/b eq c",
    )

    filter_test(
        {
            "a": {
                "b": {
                    "$": ["c", "d"],
                },
            },
        },
        "a/b eq c/d",
    )


def test_counter():
    filter_test(
        {
            "$eq": [{"$": "a/$count"}, 1],
        },
        "a/$count eq 1",
    )

    filter_test({"a": {"$count": 1}}, "a/$count eq 1")

    filter_test(
        {
            "$eq": [{"$": ["a", "$count"]}, 1],
        },
        "a/$count eq 1",
    )

    filter_test(
        {
            "$lt": [{"a": {"$count": {}}}, 1],
        },
        "a/$count lt 1",
    )

    filter_test(
        {
            "$lt": [{"a": {"$count": {"$filter": {"b": "c"}}}}, 1],
        },
        "a/$count($filter=b eq 'c') lt 1",
    )


def test_one_param_func():
    filter_test(
        {
            "$eq": [{"$tolower": {"$": "a"}}, {"$tolower": "b"}],
        },
        "tolower(a) eq tolower('b')",
    )


def test_lambdas():
    def test_lambda(operator: str):
        def create_filter(f: Any) -> Dict[str, Any]:
            return {operator: f}

        filter_test(
            {"a": create_filter({"$alias": "b", "$expr": {"b": {"c": "d"}}})},
            f"a/{operator[1:]}(b:b/c eq 'd')",
        )

        with pytest.raises(Exception):
            filter_test(
                {
                    "a": create_filter(
                        {
                            "$expr": {
                                "b": {"c": "d"},
                            },
                        }
                    ),
                },
                "",
            )
        # TODO: better error handling
        # assert f"Lambda expression ({operator}) has no alias defined." in str(err)

        with pytest.raises(Exception):
            filter_test(
                {
                    "a": create_filter(
                        {
                            "$alias": "b",
                        }
                    ),
                },
                "",
            )
        # TODO: better error handling
        # assert f"Lambda expression ({operator}) has no expr defined." in str(err)

        filter_test(
            {
                "a": create_filter(
                    {
                        "$alias": "al",
                        "$expr": {"$eq": [{"al": {"b": {"$count": {}}}}, 1]},
                    }
                ),
            },
            f"a/{operator[1:]}(al:al/b/$count eq 1)",
        )

        filter_test(
            {
                "a": create_filter(
                    {
                        "$alias": "al",
                        "$expr": {
                            "$eq": [
                                {"al": {"b": {"$count": {"$filter": {"c": "d"}}}}},
                                1,
                            ]
                        },
                    }
                ),
            },
            f"a/{operator[1:]}(al:al/b/$count($filter=c eq 'd') eq 1)",
        )

    test_lambda("$any")
    test_lambda("$all")
