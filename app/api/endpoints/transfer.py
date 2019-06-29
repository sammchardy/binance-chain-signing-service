from fastapi import APIRouter, Depends, BackgroundTasks, Body

from binance_chain.messages import TransferMsg

from config.config import WalletConfig, UserSettings
from api.models.schema import SignTransferSchema
from api.constants.constants import WalletPermission
from api.utils.wallet import get_wallet, increment_wallet_sequence
from api.security.auth import get_current_user, assert_user_has_wallet_permission, assert_wallet_has_permission
from api.utils.logging import log_broadcast_transaction, log_sign_transaction

router = APIRouter()


@router.post("/transfer/sign")
async def sign_transfer(
    transfer: SignTransferSchema = Body(
        ...,
        example={
            "msg": {
                "symbol": "BNB",
                "amount": 1,
                "to_address": "<to address>"
            },
            "wallet_name": "wallet_1",
            "memo": "Thanks for the beer"
        }
    ),
    req_wallet: WalletConfig = Depends(get_wallet),
    current_user: UserSettings = Depends(get_current_user)
):
    """Sign a transfer message, returning the hex data

    """
    assert_wallet_has_permission(req_wallet, WalletPermission.TRANSFER)
    assert_user_has_wallet_permission(current_user, transfer.wallet_name, WalletPermission.TRANSFER)

    # create the message
    msg = TransferMsg(
        wallet=req_wallet.wallet,
        **transfer.msg.dict()
    )

    log_sign_transaction(current_user, req_wallet, msg)

    return {'signed_msg': msg.to_hex_data()}


@router.post("/transfer/broadcast")
async def broadcast_transfer(
    background_tasks: BackgroundTasks,
    transfer: SignTransferSchema = Body(
        ...,
        example={
            "msg": {
                "symbol": "BNB",
                "amount": 1,
                "to_address": "<to address>"
            },
            "wallet_name": "wallet_1"
        }
    ),
    req_wallet: WalletConfig = Depends(get_wallet),
    current_user: UserSettings = Depends(get_current_user),
    sync: bool = True,
):
    """Sign and broadcast a transfer message to the exchange

    """
    assert_wallet_has_permission(req_wallet, WalletPermission.TRANSFER)
    assert_user_has_wallet_permission(current_user, transfer.wallet_name, WalletPermission.TRANSFER)

    # create the message
    msg = TransferMsg(
        wallet=req_wallet.wallet,
        **transfer.msg.dict()
    )

    log_broadcast_transaction(current_user, req_wallet, msg)

    background_tasks.add_task(increment_wallet_sequence, req_wallet)
    return await req_wallet.broadcast_msg(msg.to_hex_data(), sync=sync)
