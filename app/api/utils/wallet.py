from fastapi import HTTPException
from starlette.requests import Request

from binance_chain.wallet import Wallet

from config.config import ServiceConfig, WalletConfig


async def increment_wallet_sequence(wallet: Wallet):
    wallet.increment_account_sequence()


async def get_wallet(request: Request) -> WalletConfig:
    """Checks IP restriction on wallet

    :param request:
    :return:
    """
    config = ServiceConfig()

    body_json = await request.json()
    wallet_name = body_json.get('wallet_name', None)
    if not wallet_name:
        raise HTTPException(status_code=400, detail="Expecting wallet_name parameter")

    wallet = await config.get_wallet(wallet_name, initialise=True)

    # if not wallet.ip_authorised(request.client.host):
    #     print(f'wallet not authorised from {request.client.host}')
    #     raise HTTPException(status_code=403, detail=f"Access denied {request.client.host}")

    return wallet
