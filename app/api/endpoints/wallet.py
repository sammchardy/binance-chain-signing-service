from fastapi import APIRouter, Depends


from config.config import WalletConfig
from api.utils.wallet import get_wallet

router = APIRouter()


@router.get("/wallet/resync")
async def wallet_resync(wallet_name: str, req_wallet: WalletConfig = Depends(get_wallet)):
    """Resynchronise the wallet to the chain

    Needed if the sequence gets out of sync

    """
    # req_wallet = await config.get_wallet(wallet_name)
    req_wallet.wallet.reload_account_sequence()

    return {}
