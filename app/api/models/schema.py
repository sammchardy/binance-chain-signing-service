from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Schema

from binance_chain.constants import TimeInForce, OrderSide, OrderType


class OrderSchema(BaseModel):
    symbol: str = Schema(..., description="Trading pair full name")
    time_in_force: TimeInForce = Schema(
        ...,
        title="Time in force",
        description="GTE (Good till expire) or IOC (Immediate or Cancel)"
    )
    order_type: OrderType = Schema(..., title="Order type", description="LIMIT is the only valid order type")
    side: OrderSide = Schema(..., title="Order side", description="buy or sell")
    price: Decimal = Schema(..., title="Price", description="Price to place order", gt=0)
    quantity: Decimal = Schema(..., title="Quantity", description="Quantity of the order", gt=0)


class SignOrderSchema(BaseModel):
    msg: OrderSchema
    wallet_name: str = Schema(..., title="Wallet name", description="Name of wallet to sign msg with")


class CancelOrderSchema(BaseModel):
    symbol: str = Schema(..., description="Trading pair full name")
    order_id: str = Schema(..., title="Order id")


class SignCancelOrderSchema(BaseModel):
    msg: CancelOrderSchema
    wallet_name: str = Schema(..., title="Wallet name", description="Name of wallet to sign msg with")


class TransferSchema(BaseModel):
    to_address: str = Schema(..., title="Address to transfer tokens to")
    amount: Decimal = Schema(..., title="Amount to transfer", gt=0)
    symbol: str = Schema(..., title="Symbol to transfer")
    memo: Optional[str] = Schema(..., title="Memo to include in transfer")


class SignTransferSchema(BaseModel):
    msg: TransferSchema
    wallet_name: str = Schema(..., title="Wallet name", description="Name of wallet to sign msg with")


class FreezeSchema(BaseModel):
    amount: Decimal = Schema(..., title="Amount of token", gt=0)
    symbol: str = Schema(..., title="Symbol of token")


class SignFreezeSchema(BaseModel):
    msg: TransferSchema
    wallet_name: str = Schema(..., title="Wallet name", description="Name of wallet to sign msg with")


class WalletSchema(BaseModel):
    wallet_name: str = Schema(..., title="Wallet name", description="Name of wallet")
