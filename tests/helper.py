from pine_client import PinejsClientCore
from typing import Any, Optional


class MyClient(PinejsClientCore):
    def _request(self, method: str, url: str, body: Optional[Any] = None) -> Any:
        pass


pine = MyClient("balena-test")


def assert_compile(input: Any, output: str):
    print(pine.compile(input))
    assert pine.compile(input) == output
