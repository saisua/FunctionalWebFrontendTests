from typing import Callable


def add_rpc_pending(name: str) -> Callable:
    print("Generating method for pending rpc call", name)

    def _t():
        pass

    return _t
