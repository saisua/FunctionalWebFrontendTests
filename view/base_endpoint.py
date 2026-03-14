from typing import Callable


def gen_base_endpoint(fn: Callable) -> Callable:
    return fn
