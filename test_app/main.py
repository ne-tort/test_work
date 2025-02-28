from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from test_app.routes.v1.wallets import router_wallet
import logging

app = FastAPI()
logging.basicConfig(level=logging.CRITICAL)
app.include_router(router_wallet, prefix="/api/v1", tags=["wallets"])

@app.get("/")
async def root():
    return RedirectResponse(url="/redoc")


