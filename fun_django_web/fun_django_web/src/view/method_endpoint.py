from typing import Callable
import json

from django.http import JsonResponse, HttpRequest


def gen_method_endpoint(
    user_session_cls: type,
    fn: Callable,
) -> Callable[[object], JsonResponse]:
    print("Generating endpoint for method", fn)

    _fn_name = fn.__name__
    del fn

    def _method_endpoint(
        request: HttpRequest,
        *,
        _fn_name: str = _fn_name
    ) -> JsonResponse:
        user_session = user_session_cls(request.session)

        if request.body:
            data = getattr(user_session, _fn_name)(
                **json.loads(request.body)
            )
        else:
            data = getattr(user_session, _fn_name)()

        sent_data = dict(
            data=data,
        )

        if user_session._rpc_pending:
            sent_data['_rpc_calls'] = list(map(
                list,
                user_session._rpc_pending
            ))
            user_session._rpc_pending.clear()

        print(f"{sent_data=}")
        print(f"session={dict(request.session.items())}")

        return JsonResponse(sent_data, status=201)

    return _method_endpoint  # pyright: ignore[reportReturnType]
