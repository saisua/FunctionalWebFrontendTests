from .test2_back import router as test2_back
from .test5_back import router as test5_back

routers = [
    test2_back,
    test5_back,
]

__all__ = [
    "routers",
]
