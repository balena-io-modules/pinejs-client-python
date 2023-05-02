from pine_client import PinejsClientCore
from typing import Any

pine = PinejsClientCore("balena")


def assert_compile(input: Any, output: str):
    print(pine.compile(input))
    assert pine.compile(input) == output
