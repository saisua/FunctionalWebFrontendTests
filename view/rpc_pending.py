from typing import Callable


def add_rpc_pending(name: str) -> Callable:
    def _t(self):
        pass

    return _t
