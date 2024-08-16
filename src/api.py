'''API-роутер сервиса.'''
from fastapi import FastAPI
from .config import PROJECT_NAME
from .routers.v1 import router as router_v1
from .routers.v2 import router as router_v2

app = FastAPI(title=PROJECT_NAME)

app.include_router(router_v1, tags=['Версия 1'])
app.include_router(router_v2, prefix='/v2/orders', tags=['Версия 2'])
