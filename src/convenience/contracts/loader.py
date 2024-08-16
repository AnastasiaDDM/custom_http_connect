'''Модели первой версии API.'''
import typing

from pydantic import BaseModel, Field


class GetOrderStatusItem(BaseModel):
    TheirItemId: str
    BoughtCount: int = Field(ge=0, lt=2 ** 63)


class GetOrderStatusRequest(BaseModel):
    OrderId: int = Field(ge=-2 ** 63, le=2 ** 63 - 1)
    TheirPharmacyId: str | None = Field(None, max_length=256)
    TheirOrderId: str = Field(max_length=256)
    TheirStatusId: int | None = Field(None, ge=-2 ** 63, lt=2 ** 63)


class GetOrderStatusResponseSuccess(BaseModel):
    Result: typing.Literal['success'] = 'success'
    StatusId: typing.Literal[-1, 0, 1, 2, 3, 4]
    TheirStatusId: int = Field(ge=-2 ** 63, lt=2 ** 63)
    TheirItems: list[GetOrderStatusItem] | None = Field(None)


class GetOrderStatusResponseError(BaseModel):
    Result: typing.Literal['error'] = 'error'
    Message: str


GetOrderStatusResponse = GetOrderStatusResponseSuccess | GetOrderStatusResponseError


class CancelOrderRequest(BaseModel):
    order_ID: int = Field(ge=-2 ** 63, le=2 ** 63 - 1)
    their_order_ID: str = Field(max_length=256)
    TheirPharmacyId: str | None = Field(None, max_length=256)
    client_phone: str | None = Field(None)


class CancelOrderResponseSuccess(BaseModel):
    Result: typing.Literal['success'] = 'success'


class TransientErrorResponse(BaseModel):
    Result: typing.Literal['transient_error'] = 'transient_error'
    Message: str


class CancelOrderResponseRejected(BaseModel):
    Result: typing.Literal['order_cancel_rejected'] = 'order_cancel_rejected'
    Message: str


class OrderRejectedErrorResponse(BaseModel):
    Result: typing.Literal['order_rejected'] = 'order_rejected'
    Message: str


class SendOrderItemsResponse(BaseModel):
    TheirId: str
    Price: str
    Count: int = Field(ge=0, lt=2 ** 63)


class SendOrderResponseSuccess(BaseModel):
    Result: typing.Literal['success'] = 'success'
    TheirOrderId: str = Field(max_length=256)
    Items: list[SendOrderItemsResponse]
