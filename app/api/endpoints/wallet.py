from fastapi import APIRouter, Depends, HTTPException


from config.config import WalletConfig, UserSettings
from api.utils.wallet import get_wallet
from api.models.schema import WalletSchema
from api.constants.constants import WalletPermission
from api.security.auth import get_current_user, user_has_wallet_permission

router = APIRouter()


@router.post("/wallet/resync")
async def wallet_resync(
    wallet_req: WalletSchema,
    req_wallet: WalletConfig = Depends(get_wallet),
    current_user: UserSettings = Depends(get_current_user)
):
    """Resynchronise the wallet to the chain

    Needed if the sequence gets out of sync

    """
    if not req_wallet.has_permission(WalletPermission.TRADE):
        raise HTTPException(status_code=403, detail=f"No permission {WalletPermission.RESYNC}")

    # check user has permission for this wallet
    if not user_has_wallet_permission(current_user, wallet_req.wallet_name, WalletPermission.RESYNC):
        raise HTTPException(
            status_code=403,
            detail=f"User has no permission {WalletPermission.RESYNC} on wallet {wallet_req.wallet_name}"
        )

    req_wallet.wallet.reload_account_sequence()

    return {}
