from typing import Callable


def gen_build_script(fn: Callable) -> Callable:
    return fn
