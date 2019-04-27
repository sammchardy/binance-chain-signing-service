from fastapi import APIRouter, Depends, BackgroundTasks, Body

from binance_chain.messages import CancelOrderMsg

from config.config import WalletConfig, UserSettings
from api.models.schema import SignCancelOrderSchema
from api.constants.constants import WalletPermission
from api.utils.wallet import get_wallet, increment_wallet_sequence
from api.security.auth import get_current_user, assert_user_has_wallet_permission, assert_wallet_has_permission
from api.utils.logging import log_broadcast_transaction, log_sign_transaction

router = APIRouter()


@router.post("/order/cancel/sign/")
async def sign_cancel_order(
    cancel_order: SignCancelOrderSchema = Body(
        ...,
        example={
            "msg": {
                "order_id": "<order_id>",
                "symbol": "ANN-457_BNB"
            },
            "wallet_name": "wallet_1"
        }
    ),
    req_wallet: WalletConfig = Depends(get_wallet),
    current_user: UserSettings = Depends(get_current_user)
):
    """Sign a cancel order message, returning the hex data

    """
    assert_wallet_has_permission(req_wallet, WalletPermission.TRADE)
    assert_user_has_wallet_permission(current_user, cancel_order.wallet_name, WalletPermission.TRADE)

    # create the message
    msg = CancelOrderMsg(
        wallet=req_wallet.wallet,
        **cancel_order.msg.dict()
    )

    log_sign_transaction(current_user, req_wallet, msg)

    return {'signed_msg': msg.to_hex_data()}


@router.post("/order/cancel/broadcast")
async def broadcast_cancel_order(
    background_tasks: BackgroundTasks,
    cancel_order: SignCancelOrderSchema = Body(
        ...,
        example={
            "msg": {
                "order_id": "<order_id>",
                "symbol": "ANN-457_BNB"
            },
            "wallet_name": "wallet_1"
        }
    ),
    req_wallet: WalletConfig = Depends(get_wallet),
    current_user: UserSettings = Depends(get_current_user),
    sync=True
):
    """Sign and broadcast a cancel order message to the exchange

    """
    assert_wallet_has_permission(req_wallet, WalletPermission.TRADE)
    assert_user_has_wallet_permission(current_user, cancel_order.wallet_name, WalletPermission.TRADE)

    # create the message
    msg = CancelOrderMsg(
        wallet=req_wallet.wallet,
        **cancel_order.msg.dict()
    )

    log_broadcast_transaction(current_user, req_wallet, msg)

    background_tasks.add_task(increment_wallet_sequence)
    return await req_wallet.broadcast_msg(msg.to_hex_data(), sync=sync)
