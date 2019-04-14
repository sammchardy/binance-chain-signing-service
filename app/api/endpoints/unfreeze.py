from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException

from binance_chain.messages import UnFreezeMsg

from config.config import WalletConfig, UserSettings
from api.models.schema import SignFreezeSchema
from api.constants.constants import WalletPermission
from api.utils.wallet import get_wallet, increment_wallet_sequence
from api.security.auth import get_current_user, user_has_wallet_permission

router = APIRouter()


@router.post("/unfreeze/sign")
async def sign_unfreeze(
    freeze: SignFreezeSchema,
    req_wallet: WalletConfig = Depends(get_wallet),
    current_user: UserSettings = Depends(get_current_user)
):
    """Sign an unfreeze message, returning the hex data

    """
    if not req_wallet.has_permission(WalletPermission.FREEZE):
        raise HTTPException(status_code=403, detail=f"No permission {WalletPermission.FREEZE}")

    # check user has permission for this wallet
    if not user_has_wallet_permission(current_user, freeze.wallet_name, WalletPermission.FREEZE):
        raise HTTPException(
            status_code=403,
            detail=f"User has no permission {WalletPermission.FREEZE} on wallet {freeze.wallet_name}"
        )

    # create the message
    msg = UnFreezeMsg(
        wallet=req_wallet.wallet,
        **freeze.msg.dict()
    )

    return {'signed_msg': msg.to_hex_data()}


@router.post("/unfreeze/broadcast")
async def broadcast_unfreeze(
    freeze: SignFreezeSchema,
    background_tasks: BackgroundTasks,
    req_wallet: WalletConfig = Depends(get_wallet),
    current_user: UserSettings = Depends(get_current_user),
    sync: bool = True,
):
    """Sign and broadcast an unfreeze message to the exchange

    """
    if not req_wallet.has_permission(WalletPermission.TRADE):
        raise HTTPException(status_code=403, detail=f"No permission {WalletPermission.FREEZE}")

    # check user has permission for this wallet
    if not user_has_wallet_permission(current_user, freeze.wallet_name, WalletPermission.FREEZE):
        raise HTTPException(
            status_code=403,
            detail=f"User has no permission {WalletPermission.FREEZE} on wallet {freeze.wallet_name}"
        )

    # create the message
    msg = UnFreezeMsg(
        wallet=req_wallet.wallet,
        **freeze.msg.dict()
    )

    background_tasks.add_task(increment_wallet_sequence, req_wallet)
    return await req_wallet.broadcast_msg(msg.to_hex_data(), sync=sync)
