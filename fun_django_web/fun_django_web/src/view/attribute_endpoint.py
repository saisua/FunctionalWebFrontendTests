from typing import Callable


def gen_attr_endpoint(attr: str) -> Callable:
    print("Generating endpoint for attr", attr)

    def _wrapper(self):
        pass
    return _wrapper
