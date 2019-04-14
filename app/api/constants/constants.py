from enum import Enum


class WalletPermission(str, Enum):
    TRADE = 'trade'
    TRANSFER = 'transfer'
    FREEZE = 'freeze'
