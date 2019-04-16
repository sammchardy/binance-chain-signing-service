from fastapi import APIRouter, Depends, Path


from config.config import WalletConfig, UserSettings
from api.utils.wallet import get_wallet
from api.models.schema import WalletSchema
from api.constants.constants import WalletPermission
from api.security.auth import get_current_user, assert_user_has_wallet_permission, assert_wallet_has_permission

router = APIRouter()


@router.post("/wallet/resync")
async def wallet_resync(
    wallet_req: WalletSchema,
    req_wallet: WalletConfig = Depends(get_wallet),
    current_user: UserSettings = Depends(get_current_user)
):
    """Resynchronise the wallet to the chain

    Needed if the sequence of the wallet gets out of sync

    """
    assert_wallet_has_permission(req_wallet, WalletPermission.RESYNC)
    assert_user_has_wallet_permission(current_user, wallet_req.wallet_name, WalletPermission.RESYNC)

    req_wallet.wallet.reload_account_sequence()

    return {}


@router.get("/wallet")
async def wallet_info(
    current_user: UserSettings = Depends(get_current_user)
):
    """Get detail info for all wallets the authenticated user can access"""

    w_info = current_user.get_wallet_info()

    return w_info


@router.get("/wallet/{wallet_name}")
async def wallet_info(
    wallet_name: str = Path(..., title="Name of wallet"),
    current_user: UserSettings = Depends(get_current_user)
):
    """Get detail info for the specified wallet"""

    w_info = current_user.get_wallet_info(wallet_name)

    if not w_info:
        return {"detail": f"Not authorised to access wallet {wallet_name}"}

    return w_info[0]
