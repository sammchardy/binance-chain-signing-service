import os
import logging

import yaml
from fastapi import FastAPI
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from starlette.middleware.cors import CORSMiddleware

from config.config import ServiceConfig
from api.api import api_router

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


app = FastAPI(openapi_url="/api/v1/openapi.json")
config: ServiceConfig()


@app.on_event("startup")
async def startup_event():
    global config
    # load config
    with open('../config/config.yml', 'r') as ymlfile:
        config_yml = yaml.load(ymlfile, Loader=yaml.FullLoader)

    # convert settings to pydantic BaseSettings
    ServiceConfig.initialise_config(config=config_yml)

    logging.info("started up")


# @app.middleware("http")
# async def ip_whitelist_middleware(request: Request, call_next):
#     print(f"ip_whitelist_middleware: host: {request.client.host}")
#     wallet = getattr(request.state, 'wallet', None)
#     print(f"ip whitelist wallet: {wallet}")
#     if wallet and wallet.ip_whitelist:
#         if not wallet.ip_authorised(request.client.host):
#             raise HTTPException(status_code=403, detail=f"Access denied")
#     print('next middleware')
#     response = await call_next(request)
#     return response
#
#
# @app.middleware("http")
# async def wallet_middleware(request: Request, call_next):
#
#     print("wallet_middleware")
#     wallet_name = 'wallet_1'
#     # body = await request.body()
#     # print(f"body: {body}")
#     body_json = await request.json()
#     print(f"json: {body_json}")
#     wallet_name = body_json.get('wallet_name', None)
#     if wallet_name:
#         print(f"have wallet name: {wallet_name}")
#         wallet = await config.get_wallet(wallet_name, initialise=True)
#         if not wallet:
#             print("raising exception")
#             raise HTTPException(status_code=400, detail=f"Wallet name {wallet_name} invalid")
#
#         request.state.wallet = wallet
#     # print(f'next middleware: body:{request._body}')
#     response = await call_next(request)
#     return response

app.add_middleware(ProxyHeadersMiddleware)


class ProxyDebugHeadersMiddleware:
    def __init__(self, app, num_proxies=1):
        self.app = app
        self.num_proxies = num_proxies

    def __call__(self, scope):
        if scope["type"] in ("http", "websocket"):
            headers = dict(scope["headers"])
            logging.info(f"headers: {headers}")

        return self.app(scope)


app.add_middleware(ProxyDebugHeadersMiddleware)


@app.get("/")
def read_root():
    print("Index?")
    return {"Hello": "World"}

# CORS
origins = []

# Set all CORS enabled origins
if os.getenv("BACKEND_CORS_ORIGINS", None):
    origins_raw = os.getenv("BACKEND_CORS_ORIGINS", '').split(",")
    for origin in origins_raw:
        use_origin = origin.strip()
        origins.append(use_origin)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ),

app.include_router(api_router, prefix='/api')

# @app.get("/wallet/resync")
# async def wallet_resync(wallet_name: str, req_wallet: WalletConfig = Depends(get_wallet)):
#     """Resynchronise the wallet to the chain
#
#     Needed if the sequence gets out of sync
#
#     """
#     # req_wallet = await config.get_wallet(wallet_name)
#     req_wallet.wallet.reload_account_sequence()
#
#     return {}
# @app.post("/sign/order")
# async def sign_order(
#         sign_order: SignOrderSchema,
#         req_wallet: WalletConfig = Depends(get_wallet)
# ):
#     """Sign a new order message, returning the hex data
#
#     """
#
#     print("sign order")
#     if not req_wallet.has_permission(WalletPermission.TRADE):
#         raise HTTPException(status_code=403, detail=f"No permission {WalletPermission.TRADE}")
#
#     # create the message
#     msg = NewOrderMsg(
#         wallet=req_wallet.wallet,
#         **sign_order.msg.dict()
#     )
#
#     return {'signed_msg': msg.to_hex_data()}
#
#
# @app.post("/broadcast/order")
# async def broadcast_order(
#     sign_order: SignOrderSchema,
#     background_tasks: BackgroundTasks,
#     req_wallet: WalletConfig = Depends(get_wallet),
#     sync: bool = True,
# ):
#     """Sign and broadcast a new order message to the exchange
#
#     """
#     if not req_wallet.has_permission(WalletPermission.TRADE):
#         raise HTTPException(status_code=403, detail=f"No permission {WalletPermission.TRADE}")
#
#     # create the message
#     msg = NewOrderMsg(
#         wallet=req_wallet.wallet,
#         **sign_order.msg.dict()
#     )
#
#     background_tasks.add_task(increment_wallet_sequence, req_wallet)
#     return await req_wallet.broadcast_msg(msg.to_hex_data(), sync=sync)


# @app.post("/sign/cancel_order")
# async def sign_cancel_order(
#     cancel_order: CancelOrderSchema,
#     req_wallet: WalletConfig = Depends(get_wallet)
# ):
#     """Sign a cancel order message, returning the hex data
#
#     """
#     if not req_wallet.has_permission(WalletPermission.TRADE):
#         raise HTTPException(status_code=403, detail=f"No permission {WalletPermission.TRADE}")
#
#     # create the message
#     msg = CancelOrderMsg(
#         wallet=req_wallet.wallet,
#         **cancel_order.dict()
#     )
#
#     return {'signed_msg': msg.to_hex_data()}
#
#
# @app.post("/broadcast/cancel_order")
# async def broadcast_cancel_order(
#     order: CancelOrderSchema,
#     background_tasks: BackgroundTasks,
#     req_wallet: WalletConfig = Depends(get_wallet),
#     sync: bool = True
# ):
#     """Sign and broadcast a cancel order message to the exchange
#
#     """
#     if not req_wallet.has_permission(WalletPermission.TRADE):
#         raise HTTPException(status_code=403, detail=f"No permission {WalletPermission.TRADE}")
#
#     # create the message
#     msg = NewOrderMsg(
#         wallet=req_wallet.wallet,
#         **order.dict()
#     )
#
#     background_tasks.add_task(increment_wallet_sequence)
#     return await req_wallet.broadcast_msg(msg.to_hex_data(), sync=sync)
