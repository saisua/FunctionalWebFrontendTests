from typing import Callable, Optional
import inspect  # noqa: F401
from functools import partial

import reflex as rx  # noqa: F401


EMPTY_LIST = list()


EVENT_FN = """
@rx.event
async def {}(self):
    generators = list()
    for check_fn in check_before:
        check_result = getattr(self, check_fn)()

        if inspect.iscoroutine(check_result):
            check_result = await check_result

        if check_result is not None:
            generators.append(check_result)

    for generator in generators:
        if inspect.isasyncgen(generator):
            async for value in generator:
                yield value
        else:
            for value in generator:
                yield value

    result = callable(self)

    if inspect.iscoroutine(result):
        result = await result

    generators.clear()
    for check_fn in check_after:
        check_result = getattr(self, check_fn)()

        if inspect.iscoroutine(check_result):
            check_result = await check_result

        if check_result is not None:
            generators.append(check_result)

    for generator in generators:
        if inspect.isasyncgen(generator):
            async for value in generator:
                yield value
        else:
            for value in generator:
                yield value
"""


def mvu_event(
    callable: Optional[Callable] = None,
    *args,
    check_before: Optional[list[str] | str] = None,
    check_after: Optional[list[str] | str] = None,
    **kwargs,
):
    if callable is None:
        return partial(
            mvu_event,
            check_before=check_before,
            check_after=check_after,
            *args,
            **kwargs,
        )

    if check_before is None and check_after is None:
        return rx.event(callable, *args, **kwargs)

    if check_before is None:
        check_before = list()
    elif isinstance(check_before, str):
        check_before = [check_before]

    if check_after is None:
        check_after = list()
    elif isinstance(check_after, str):
        check_after = [check_after]

    exec(
        EVENT_FN.format(callable.__name__),
        {**globals(), **locals()},
        locals(),
    )

    return locals()[callable.__name__]
