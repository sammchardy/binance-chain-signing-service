from decimal import Decimal

from pydantic import BaseModel

from binance_chain.constants import TimeInForce, OrderSide, OrderType


class OrderSchema(BaseModel):
    symbol: str
    time_in_force: TimeInForce
    order_type: OrderType
    side: OrderSide
    price: Decimal
    quantity: Decimal


class SignOrderSchema(BaseModel):
    msg: OrderSchema
    wallet_name: str


class CancelOrderSchema(BaseModel):
    symbol: str
    order_id: str
    wallet_name: str


class SignCancelOrderSchema(BaseModel):
    msg: CancelOrderSchema
    wallet_name: str


class TransferSchema(BaseModel):
    to_address: str
    amount: Decimal
    symbol: str


class SignTransferSchema(BaseModel):
    msg: TransferSchema
    wallet_name: str


class FreezeSchema(BaseModel):
    amount: Decimal
    symbol: str


class SignFreezeSchema(BaseModel):
    msg: TransferSchema
    wallet_name: str
