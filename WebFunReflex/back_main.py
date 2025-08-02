from fastapi import FastAPI

from .api import routers

app = FastAPI(
    title="WebFunReflex",
    description="WebFunReflex API",
    version="0.1.0",
)

for router in routers:
    app.include_router(router)
