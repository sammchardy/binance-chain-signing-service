from fastapi import APIRouter, Depends, BackgroundTasks, Body

from binance_chain.messages import NewOrderMsg

from config.config import WalletConfig, UserSettings
from api.models.schema import SignOrderSchema
from api.constants.constants import WalletPermission
from api.utils.wallet import get_wallet, increment_wallet_sequence
from api.security.auth import get_current_user, assert_user_has_wallet_permission, assert_wallet_has_permission
from api.utils.logging import log_broadcast_transaction, log_sign_transaction

router = APIRouter()


@router.post("/order/sign")
async def sign_order(
    signed_order: SignOrderSchema = Body(
        ...,
        example={
            "msg": {
                "order_type": "LIMIT",
                "price": 0.000396,
                "quantity": 10,
                "side": "buy",
                "symbol": "ANN-457_BNB",
                "time_in_force": "GTE"
            },
            "wallet_name": "wallet_1"
        },
    ),
    req_wallet: WalletConfig = Depends(get_wallet),
    current_user: UserSettings = Depends(get_current_user)
):
    """Sign a new order message, returning the hex data

    """
    assert_wallet_has_permission(req_wallet, WalletPermission.TRADE)
    assert_user_has_wallet_permission(current_user, signed_order.wallet_name, WalletPermission.TRADE)

    # create the message
    msg = NewOrderMsg(
        wallet=req_wallet.wallet,
        **signed_order.msg.dict()
    )

    log_sign_transaction(current_user, req_wallet, msg)

    return {'signed_msg': msg.to_hex_data()}


@router.post("/order/broadcast")
async def broadcast_order(
    background_tasks: BackgroundTasks,
    signed_order: SignOrderSchema = Body(
        ...,
        example={
            "msg": {
                "order_type": "LIMIT",
                "price": 0.000396,
                "quantity": 10,
                "side": "buy",
                "symbol": "ANN-457_BNB",
                "time_in_force": "GTE"
            },
            "wallet_name": "wallet_1"
        },
    ),
    req_wallet: WalletConfig = Depends(get_wallet),
    current_user: UserSettings = Depends(get_current_user),
    sync: bool = True,
):
    """Sign and broadcast a new order message to the exchange

    """
    assert_wallet_has_permission(req_wallet, WalletPermission.TRADE)
    assert_user_has_wallet_permission(current_user, signed_order.wallet_name, WalletPermission.TRADE)

    # create the message
    msg = NewOrderMsg(
        wallet=req_wallet.wallet,
        **signed_order.msg.dict()
    )

    log_broadcast_transaction(current_user, req_wallet, msg)

    background_tasks.add_task(increment_wallet_sequence, req_wallet)
    return await req_wallet.broadcast_msg(msg.to_hex_data(), sync=sync)
