from typing import Callable

from django.http import HttpRequest, JsonResponse


def gen_attr_endpoint(
    cls: type,
    attr: str
) -> Callable[[HttpRequest], JsonResponse]:
    print("Generating endpoint for attr", attr)

    def _attr_endpoint(
        request: HttpRequest,
        *,
        attr: str = attr
    ) -> JsonResponse:
        sent_data = dict(
            data=getattr(cls, attr),
        )

        if cls._rpc_pending:
            sent_data['_rpc_calls'] = list(map(list, cls._rpc_pending))
            cls._rpc_pending.clear()

        return JsonResponse(sent_data, status=201)

    return _attr_endpoint
