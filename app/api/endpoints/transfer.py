from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException

from binance_chain.messages import TransferMsg

from config.config import WalletConfig, UserSettings
from api.models.schema import SignTransferSchema
from api.constants.constants import WalletPermission
from api.utils.wallet import get_wallet, increment_wallet_sequence
from api.security.auth import get_current_user, user_has_wallet_permission

router = APIRouter()


@router.post("/transfer/sign")
async def sign_transfer(
    transfer: SignTransferSchema,
    req_wallet: WalletConfig = Depends(get_wallet),
    current_user: UserSettings = Depends(get_current_user)
):
    """Sign a transfer message, returning the hex data

    """
    if not req_wallet.has_permission(WalletPermission.TRADE):
        raise HTTPException(status_code=403, detail=f"No permission {WalletPermission.TRANSFER}")

    # check user has permission for this wallet
    if not user_has_wallet_permission(current_user, transfer.wallet_name, WalletPermission.TRANSFER):
        raise HTTPException(
            status_code=403,
            detail=f"User has no permission {WalletPermission.TRANSFER} on wallet {transfer.wallet_name}"
        )

    # create the message
    msg = TransferMsg(
        wallet=req_wallet.wallet,
        **transfer.msg.dict()
    )

    return {'signed_msg': msg.to_hex_data()}


@router.post("/transfer/broadcast")
async def broadcast_transfer(
    transfer: SignTransferSchema,
    background_tasks: BackgroundTasks,
    req_wallet: WalletConfig = Depends(get_wallet),
    current_user: UserSettings = Depends(get_current_user),
    sync: bool = True,
):
    """Sign and broadcast a transfer message to the exchange

    """
    if not req_wallet.has_permission(WalletPermission.TRADE):
        raise HTTPException(status_code=403, detail=f"No permission {WalletPermission.TRANSFER}")

    # check user has permission for this wallet
    if not user_has_wallet_permission(current_user, transfer.wallet_name, WalletPermission.TRANSFER):
        raise HTTPException(
            status_code=403,
            detail=f"User has no permission {WalletPermission.TRANSFER} on wallet {transfer.wallet_name}"
        )

    # create the message
    msg = TransferMsg(
        wallet=req_wallet.wallet,
        **transfer.msg.dict()
    )

    background_tasks.add_task(increment_wallet_sequence, req_wallet)
    return await req_wallet.broadcast_msg(msg.to_hex_data(), sync=sync)
