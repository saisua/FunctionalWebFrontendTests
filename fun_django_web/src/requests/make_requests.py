from typing import Literal
import asyncio  # noqa: F401
from functools import partial  # noqa: F401
import json
import re

from pyodide.http import pyfetch  # pyright: ignore[reportMissingImports]

import js  # pyright: ignore[reportMissingImports]


csrf_cookie_pattern = re.compile(r"(?:^|;)csrftoken=([^;]+)(?:;|$)")


def __get_csrf_token() -> str:
    if (m := csrf_cookie_pattern.search(js.document.cookie)):
        return m.group(1)  # pyright: ignore[reportReturnType]
    raise ValueError("No CSRF token found")


async def make_request(
    url: str,
    *,
    method: Literal['GET', 'POST', 'PUT', 'DELETE'],
    _csrf_token: str = __get_csrf_token(),
    **kwargs
):
    response = await pyfetch(
        url,
        method=method,
        body=json.dumps(kwargs, default=str),
        headers={
            "Content-Type": "application/json",
            "X-CSRFToken": _csrf_token,
        }
    )

    if response.ok:
        data: dict = await response.json()

        if (_rpc_calls := data.pop('_rpc_calls', None)):
            for _rpc_call, _rpc_kwargs in _rpc_calls:
                if 'view' in globals() and hasattr(view, _rpc_call):  # noqa: F821,E501  # pyright: ignore[reportUndefinedVariable]
                    _rpc_call_fn = getattr(
                        view,  # noqa: F821,E501  # pyright: ignore[reportUndefinedVariable]
                        _rpc_call,
                    )
                else:
                    _rpc_call_fn = globals()[_rpc_call]

                _rpc_call_fn(**_rpc_kwargs)

        data = data['data']
        print(f"Result: {data}")
        return data
    else:
        print(f"Error: {response.status}")
