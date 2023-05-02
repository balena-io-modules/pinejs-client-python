from typing import Any, Dict
from .helper import assert_compile


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

    # filter_test(
    #     {
    #         a: {
    #             b: 'c',
    #         },
    #     },
    #     "a/b eq 'c'",
    # );

    # filter_test(
    #     {
    #         a: {
    #             b: 'c',
    #             d: 'e',
    #         },
    #     },
    #     "(a/b eq 'c') and (a/d eq 'e')",
    # );

    # filter_test(
    #     {
    #         a: [{ b: 'c' }, { d: 'e' }],
    #     },
    #     "a eq ((b eq 'c') or (d eq 'e'))",
    # );

    # filter_test(
    #     {
    #         a: ['c', 'd'],
    #     },
    #     "a eq ('c' or 'd')",
    # );

    # filter_test(
    #     {
    #         a: {
    #             b: ['c', 'd'],
    #         },
    #     },
    #     "a/b eq ('c' or 'd')",
    # );

    # filter_test(
    #     {
    #         a: [{ b: 'c' }, 'd'],
    #     },
    #     "a eq ((b eq 'c') or 'd')",
    # );

    # filter_test(
    #     {
    #         a: {
    #             b: 'c',
    #             $eq: 'd',
    #         },
    #     },
    #     "(a/b eq 'c') and (a eq 'd')",
    # );
