from typing import Callable


def gen_method_endpoint(fn: Callable) -> Callable:
    print("Generating endpoint for method", fn)
    return fn
