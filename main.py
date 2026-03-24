from fastapi import FastAPI
from app.api.v1.wordforms import router as router_wordforms


app = FastAPI()

app.include_router(router=router_wordforms, prefix='/api/v1', tags=['wordforms'])


