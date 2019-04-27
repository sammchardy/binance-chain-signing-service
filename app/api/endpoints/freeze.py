from fastapi import APIRouter, Depends, BackgroundTasks, Body

from binance_chain.messages import FreezeMsg

from config.config import WalletConfig, UserSettings
from api.models.schema import SignFreezeSchema
from api.constants.constants import WalletPermission
from api.utils.wallet import get_wallet, increment_wallet_sequence
from api.security.auth import get_current_user, assert_user_has_wallet_permission, assert_wallet_has_permission
from api.utils.logging import log_broadcast_transaction, log_sign_transaction

router = APIRouter()


@router.post("/freeze/sign")
async def sign_freeze(
    freeze: SignFreezeSchema = Body(
        ...,
        example={
            "msg": {
                "symbol": "BNB",
                "amount": 1,
            },
            "wallet_name": "wallet_1"
        }
    ),
    req_wallet: WalletConfig = Depends(get_wallet),
    current_user: UserSettings = Depends(get_current_user)
):
    """Sign a freeze message, returning the hex data

    """
    assert_wallet_has_permission(req_wallet, WalletPermission.FREEZE)
    assert_user_has_wallet_permission(current_user, freeze.wallet_name, WalletPermission.FREEZE)

    # create the message
    msg = FreezeMsg(
        wallet=req_wallet.wallet,
        **freeze.msg.dict()
    )

    log_sign_transaction(current_user, req_wallet, msg)

    return {'signed_msg': msg.to_hex_data()}


@router.post("/freeze/broadcast")
async def broadcast_freeze(
    background_tasks: BackgroundTasks,
    freeze: SignFreezeSchema = Body(
        ...,
        example={
            "msg": {
                "symbol": "BNB",
                "amount": 1,
            },
            "wallet_name": "wallet_1"
        }
    ),
    req_wallet: WalletConfig = Depends(get_wallet),
    current_user: UserSettings = Depends(get_current_user),
    sync: bool = True,
):
    """Sign and broadcast a freeze message to the exchange

    """
    assert_wallet_has_permission(req_wallet, WalletPermission.FREEZE)
    assert_user_has_wallet_permission(current_user, freeze.wallet_name, WalletPermission.FREEZE)

    # create the message
    msg = FreezeMsg(
        wallet=req_wallet.wallet,
        **freeze.msg.dict()
    )

    log_broadcast_transaction(current_user, req_wallet, msg)

    background_tasks.add_task(increment_wallet_sequence, req_wallet)
    return await req_wallet.broadcast_msg(msg.to_hex_data(), sync=sync)
