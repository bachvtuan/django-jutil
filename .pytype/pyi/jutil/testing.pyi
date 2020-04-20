# (generated with --quick)

from typing import Any, Tuple

APIClient: Any
Token: Any
User: Any
json: module

class DefaultTestSetupMixin:
    api_client: Any
    token: Any
    user: Any
    verbose: bool
    def add_test_user(self, email: str = ..., password: str = ...) -> None: ...
    def debug_print(self, *args, **kw) -> None: ...
    def delete(self, path: str, data: dict, **kw) -> dict: ...
    def get(self, path: str, data: dict, **kw) -> dict: ...
    def patch(self, path: str, data: dict, **kw) -> dict: ...
    def post(self, path: str, data: dict, **kw) -> dict: ...
    def put(self, path: str, data: dict, **kw) -> dict: ...
    def request(self, method: str, path: str, data: dict, **kw) -> Tuple[dict, int]: ...
