from typing import Any, Dict
import pytest
from .helper import assert_compile


def id_test(input: Any, output: str):
    resource = "test"
    output = f"{resource}({output})"

    assert_compile({"resource": resource, "id": input}, output)


def option_test(option: str, input: Any, output: str):
    resource = "test"

    output = f"{resource}?{option}={output}"

    options: Dict[str, Any] = {}
    options[option] = input

    assert_compile({"resource": resource, "options": options}, output)


def orderby_test(input: Any, output: str):
    return option_test("$orderby", input, output)


def top_test(input: Any, output: Any):
    return option_test("$top", input, output)


def skip_test(input: Any, output: Any):
    return option_test("$skip", input, output)


def format_test(input: Any, output: str):
    return option_test("$format", input, output)


def select_test(input: Any, output: str):
    return option_test("$select", input, output)


def custom_test(input: Any, output: str):
    return option_test("custom", input, output)


def param_test(input: Any, output: str):
    return option_test("@param", input, output)


def test_id():
    id_test(1, "1")

    id_test("Bob", "'Bob'")
    id_test({"@": "param"}, "@param")
    id_test(
        {
            "a": 1,
            "b": 2,
        },
        "a=1,b=2",
    )
    id_test(
        {
            "a": "Bob",
            "b": "Smith",
        },
        "a='Bob',b='Smith'",
    )
    id_test(
        {
            "a": {"@": "param1"},
            "b": {"@": "param2"},
        },
        "a=@param1,b=@param2",
    )


def test_orderby():
    orderby_test("a", "a")

    orderby_test(["a", "b"], "a,b")

    orderby_test({"a": "desc"}, "a desc")

    orderby_test([{"a": "desc"}, {"b": "asc"}], "a desc,b asc")

    with pytest.raises(Exception) as err:
        orderby_test([["a"]], "")
    assert "'$orderby' cannot have nested arrays" in str(err)

    with pytest.raises(Exception) as err:
        orderby_test({"a": "x"}, "")
    assert "'$orderby' direction must be 'asc' or 'desc'" in str(err)

    with pytest.raises(Exception) as err:
        orderby_test({"a": "asc", "b": "desc"}, "")
    assert "'$orderby' objects must have exactly one element, got 2 elements" in str(
        err
    )

    with pytest.raises(Exception) as err:
        orderby_test([], "")
    assert "'$orderby' arrays have to have at least 1 element" in str(err)

    with pytest.raises(Exception) as err:
        orderby_test(1, "")
    assert "'$orderby' option has to be either a string, array, or object" in str(err)

    orderby_test({"a": {"$count": {}}, "$dir": "desc"}, "a/$count desc")

    orderby_test(
        {"a": {"$count": {"$filter": {"d": "e"}}}, "$dir": "desc"},
        "a/$count($filter=d eq 'e') desc",
    )

    orderby_test(
        [
            {
                "a": {"$count": {"$filter": {"d": "e"}}},
                "$dir": "desc",
            },
            {
                "b": {"$count": {}},
                "$dir": "desc",
            },
            {
                "c": "asc",
            },
        ],
        "a/$count($filter=d eq 'e') desc,b/$count desc,c asc",
    )

    with pytest.raises(Exception) as err:
        orderby_test({"a": {"$count": {}}}, "")
    assert (
        "'$orderby' objects should either use the '{ a: 'asc' }' or the'$orderby: { a: { $count: ... }, $dir: 'asc' }'"
        " notation" in str(err)
    )

    with pytest.raises(Exception) as err:
        orderby_test({"a": {"$filter": {"d": "e"}}, "$dir": "desc"}, "")
    assert (
        "When using $orderby: { a: { $count: ... }, $dir: 'asc' } you can only specify $count, got ['$filter']"
        in str(err)
    )

    with pytest.raises(Exception) as err:
        orderby_test({"a": {"$count": {"$expand": "e"}}, "$dir": "desc"}, "")
    assert (
        "When using $orderby: { a: { $count: ... }, $dir: 'asc' } you can only specify $filter in the $count,"
        " got ['$expand']" in str(err)
    )

    with pytest.raises(Exception) as err:
        orderby_test(
            {"a": {"$count": {"$expand": "e", "$filter": {"d": "e"}}}, "$dir": "desc"},
            "",
        )
    assert (
        "When using $orderby: { a: { $count: ... }, $dir: 'asc' } you can only specify $filter in the $count, got"
        " ['$expand', '$filter']" in str(err)
    )


def test_top():
    top_test(1, 1)

    with pytest.raises(Exception) as err:
        top_test("1", "")
    assert "'$top' option has to be a number" in str(err)


def test_skip():
    skip_test(1, 1)

    with pytest.raises(Exception) as err:
        skip_test("1", "")
    assert "'$skip' option has to be a number" in str(err)


def test_format():
    format_test("json;metadata=full", "json;metadata=full")
    format_test("json;metadata=none", "json;metadata=none")


def test_select():
    select_test("a", "a")
    select_test(["a", "b"], "a,b")

    with pytest.raises(Exception) as err:
        select_test([], "")
    assert "'$select' arrays have to have at least 1 element" in str(err)

    with pytest.raises(Exception) as err:
        select_test(1, "")
    assert "'$select' option has to be either a string or array" in str(err)


def test_custom():
    custom_test("a", "a")
    custom_test(1, "1")
    custom_test(True, "true")


def test_param():
    param_test("test", "'test'")
    param_test(1, "1")

    with pytest.raises(Exception) as err:
        param_test({}, "")

    assert "Unknown type for parameter alias option '@param'" in str(err)
