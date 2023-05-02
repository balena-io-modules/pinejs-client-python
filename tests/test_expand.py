from .helper import assert_compile
from typing import Any
import pytest


def expand_test(input: Any, output: str):
    resource = "test"
    output = f"{resource}?$expand={output}"

    assert_compile({"resource": resource, "options": {"$expand": input}}, output)


def test_expand_string():
    expand_test("a", "a")


def test_expand_array():
    expand_test(["a"], "a")
    expand_test(["a", "b"], "a,b")


def test_expand_object():
    with pytest.raises(Exception) as err:
        expand_test({"a": "b"}, "")
    assert "'$expand: a: b' is invalid, use '$expand: a: $expand: $b' instead" in str(
        err
    )

    with pytest.raises(Exception) as err:
        expand_test({"a": "b", "c": "d"}, "")
    assert "'$expand: a: b' is invalid, use '$expand: a: $expand: $b' instead" in str(
        err
    )

    with pytest.raises(Exception) as err:
        expand_test([{"a": "b"}], "")
    assert "'$expand: a: b' is invalid, use '$expand: a: $expand: $b' instead" in str(
        err
    )

    with pytest.raises(Exception) as err:
        expand_test([{"a": "b"}, {"c": "d"}], "")
    assert "'$expand: a: b' is invalid, use '$expand: a: $expand: $b' instead" in str(
        err
    )

    with pytest.raises(Exception) as err:
        expand_test({"a": ["b", "c"]}, "")
    assert "'$expand: a: [...]' is invalid, use '$expand: a: {...}' instead." in str(
        err
    )

    with pytest.raises(Exception) as err:
        expand_test({"a": [{"b": "c"}, {"d": "e"}]}, "")
    assert "'$expand: a: [...]' is invalid, use '$expand: a: {...}' instead." in str(
        err
    )

    with pytest.raises(Exception) as err:
        expand_test({"a": [{"b": "c"}, {"d": "e"}]}, "")
    assert "'$expand: a: [...]' is invalid, use '$expand: a: {...}' instead." in str(
        err
    )

    expand_test(
        {
            "a": {"$filter": {"b": "c"}},
        },
        "a($filter=b eq 'c')",
    )

    expand_test(
        {
            "a": {
                "$select": ["b", "c"],
            },
        },
        "a($select=b,c)",
    )

    expand_test(
        {
            "a": {
                "$filter": {"b": "c"},
                "$select": ["d", "e"],
            },
        },
        "a($filter=b eq 'c';$select=d,e)",
    )

    with pytest.raises(Exception) as err:
        expand_test(
            {
                "a": {
                    "b": "c",
                    "$filter": {"d": "e"},
                    "$select": ["f", "g"],
                },
            },
            "",
        )
    assert (
        "$expand: a: $b: ...' is invalid, use '$expand: a: $expand:b: ...' instead."
        in str(err)
    )

    with pytest.raises(Exception) as err:
        expand_test(
            {
                "a": [
                    {"$filter": {"b": "c"}},
                    {"$filter": {"d": "e"}, "$select": ["f", "g"]},
                ],
            },
            "",
        )

    assert "'$expand: a: [...]' is invalid, use '$expand: a: {...}' instead." in str(
        err
    )

    expand_test(
        {
            "a": {
                "$expand": "b",
            },
        },
        "a($expand=b)",
    )

    expand_test(
        {
            "a": {
                "$expand": {
                    "b": {
                        "$expand": "c",
                    },
                },
            },
        },
        "a($expand=b($expand=c))",
    )

    expand_test(
        {
            "a": {
                "$expand": {
                    "b": {
                        "$expand": "c",
                        "$select": ["d", "e"],
                    },
                },
            },
        },
        "a($expand=b($expand=c;$select=d,e))",
    )

    with pytest.raises(Exception) as err:
        expand_test(
            {
                "a/$count": {"$filter": {"b": "c"}},
            },
            "",
        )
    assert (
        "'`$expand: { 'a/$count': {...} }` is deprecated, please use`$expand: { a: { $count: {...} } }` instead."
        in str(err)
    )

    expand_test(
        {
            "a": {"$count": {"$filter": {"b": "c"}}},
        },
        "a/$count($filter=b eq 'c')",
    )

    with pytest.raises(Exception) as err:
        expand_test(
            {
                "a": {
                    "$count": {
                        "$select": "a",
                        "$filter": {"b": "c"},
                    },
                },
            },
            "",
        )
    assert (
        "using OData options other than $filter in a '$expand: { a: { $count: {...} } }'"
        " is not allowed, please remove them." in str(err)
    )

    expand_test(
        {
            "a": {"$expand": "b/$count"},
        },
        "a($expand=b/$count)",
    )

    expand_test(
        {
            "a": {"$expand": {"b": {"$count": {}}}},
        },
        "a($expand=b/$count)",
    )

    expand_test(
        {
            "a": {"$expand": ["b/$count", "c"]},
        },
        "a($expand=b/$count,c)",
    )

    expand_test(
        {
            "a": {"$expand": [{"b": {"$count": {}}}, "c"]},
        },
        "a($expand=b/$count,c)",
    )

    expand_test(
        {
            "a": {
                "$expand": {
                    "b": {
                        "$expand": "c/$count",
                        "$filter": {"d": "e"},
                    },
                },
            },
        },
        "a($expand=b($expand=c/$count;$filter=d eq 'e'))",
    )

    expand_test(
        {
            "a": {
                "$expand": {
                    "b": {
                        "$expand": {"c": {"$count": {}}},
                        "$filter": {"d": "e"},
                    },
                },
            },
        },
        "a($expand=b($expand=c/$count;$filter=d eq 'e'))",
    )
