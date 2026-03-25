from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.v1.queue import router as router_queue
from app.service.wordforms import start_worker, delete_dirs



@asynccontextmanager
async def lifespan(_: FastAPI):
    start_worker()
    yield
    delete_dirs()

app = FastAPI(lifespan=lifespan)
app.include_router(router=router_queue, prefix='/api/v1', tags=['queue'])


