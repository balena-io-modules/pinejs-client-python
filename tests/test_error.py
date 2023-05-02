import pytest
from .helper import assert_compile


def test_throw_unrecognised_operator():
    with pytest.raises(Exception) as err:
        assert_compile(
            {"resource": "test", "options": {"$filter": {"$foobar": "fails"}}}, ""
        )
    assert "Unrecognised operator: '$foobar'" in str(err)


# TODO: Python has no differentiation from None such as null/undefined
# # so this test does not translate
# def test_throw_null_id():
#     with pytest.raises(Exception) as err:
#         assert_compile({"resource": "test", "id": None}, "")
#     assert "If the id property is set it must be non-null" in str(err)
