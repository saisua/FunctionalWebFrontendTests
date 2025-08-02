import inspect
from typing import Callable, Optional
from functools import partial

import reflex as rx


def mvu_check(
    callable: Optional[Callable] = None,
    triggers: Optional[list[str] | str] = None,
    else_triggers: Optional[list[str] | str] = None,
):
    if callable is None:
        return partial(
            mvu_check,
            triggers=triggers,
            else_triggers=else_triggers,
        )

    if triggers is None and else_triggers is None:
        return rx.event(callable)

    if triggers is None:
        triggers = list()
    elif isinstance(triggers, str):
        triggers = [triggers]

    if else_triggers is None:
        else_triggers = list()
    elif isinstance(else_triggers, str):
        else_triggers = [else_triggers]

    async def mvu_checker_wrapper(inst):
        results = list()
        if callable(inst):
            for trigger in triggers:
                result = getattr(inst, trigger)()

                if inspect.iscoroutine(result):
                    results.append(await result)
                else:
                    results.append(result)
        else:
            for trigger in else_triggers:
                result = getattr(inst, trigger, lambda: None)()

                if inspect.iscoroutine(result):
                    results.append(await result)
                else:
                    results.append(result)

        if len(results) == 0:
            return None
        elif len(results) == 1:
            return results[0]
        else:
            return results

    return mvu_checker_wrapper

