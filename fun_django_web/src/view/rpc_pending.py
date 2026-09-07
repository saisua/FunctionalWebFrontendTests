from typing import Callable


def add_rpc_pending(name: str) -> Callable:
    print("Generating method for pending rpc call", name)

    def _add_rpc_pending_wrapper(self, name: str = name, **kwargs):
        self._rpc_pending.append([name, kwargs])

    return _add_rpc_pending_wrapper
