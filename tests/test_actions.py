from .helper import assert_compile
import pytest

def test_bound_action():
    assert_compile({
        "resource": "a",
        "id": 1,
        "action": "act"
    }, "a(1)/act")

def test_unbound_action():
    assert_compile({
        "resource": "a",
        "action": "act"
    }, "a/act")

def test_bound_action_with_named_id():
    assert_compile({
        "resource": "a",
        "id": { "b": "c" },
        "action": "act"
    }, "a(b='c')/act")
