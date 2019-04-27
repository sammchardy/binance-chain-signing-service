import logging
import json

from config.config import WalletConfig, UserSettings
from binance_chain.messages import Msg


def log_sign_transaction(user: UserSettings, wallet: WalletConfig, msg: Msg):

    logging.info(
        f"User:{user.username} Wallet: {wallet.name} signed: {type(msg).__name__} with {json.dumps(msg.to_dict())}"
    )


def log_broadcast_transaction(user: UserSettings, wallet: WalletConfig, msg: Msg):
    logging.info(
        f"User:{user.username} Wallet: {wallet.name} broadcast: {type(msg).__name__} with {json.dumps(msg.to_dict())}"
    )
