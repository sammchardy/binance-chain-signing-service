from fastapi import APIRouter

from api.endpoints import order, transfer, cancel_order, wallet, auth, freeze, unfreeze

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(order.router)
api_router.include_router(transfer.router)
api_router.include_router(cancel_order.router)
api_router.include_router(freeze.router)
api_router.include_router(wallet.router)
