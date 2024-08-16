'''Модели исходящих ответов.'''
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field

from .input import OrderItem


class QuantityErrorItem(BaseModel):
    '''Модель расшифровки ошибки по количеству товара.'''

    their_id: str                                           # ид товара у партнера
    ordered: int | None = Field(None, ge=0, lt=2 ** 63)     # переданное значение
    available: int | None = Field(None, ge=0, lt=2 ** 63)   # доступное значение


class PriceErrorItem(BaseModel):
    '''Модель расшифровки ошибки по цене товара.'''

    their_id: str                                           # ид товара у партнера
    ordered: Decimal | None = Field(None, gt=0)             # переданное значение
    available: Decimal | None = Field(None, gt=0)           # доступное значение


class ListItemsQuantityError(BaseModel):
    '''Модель списка ошибок по количеству товаров.'''

    items: list[QuantityErrorItem] | None


class ListItemsPriceError(BaseModel):
    '''Модель списка ошибок по цене товаров.'''

    items: list[PriceErrorItem] | None


class DataError(BaseModel):
    '''Модель списка ошибок отправки заказа.'''

    partner_error: Optional[Literal[True]] = None           # ошибка работы c API-партнера
    service_error: Optional[Literal[True]] = None           # ошибка работы сервиса
    quantity_errors: ListItemsQuantityError | None = None   # недостаточное количество товара
    price_errors: ListItemsPriceError | None = None         # изменилась стоимость товаров


class SendOrderResponseError(BaseModel):
    '''Модель ошибочного ответа отправки заказа.'''

    result: str = 'error'
    data: DataError


class SendOrderResponseSuccess(BaseModel):
    '''Модель успешного ответа отправки заказа.'''

    result: Literal['success'] = 'success'
    their_order_id: str = Field(max_length=256)
    items: list[OrderItem]


class GetOrderStatusItem(BaseModel):
    '''Модель товаров при получении статуса заказа.'''

    their_item_id: str
    bought_count: int = Field(ge=0, lt=2 ** 63)


class GetOrderStatusResponseSuccess(BaseModel):
    '''Модель успешного ответа получения статуса заказа.'''

    result: Literal['success'] = 'success'
    status_id: Literal[-1, 0, 1, 2, 3, 4]
    their_status_id: int = Field(ge=-2 ** 63, lt=2 ** 63)
    their_items: list[GetOrderStatusItem] | None = Field(None)


class GetOrderStatusResponseError(BaseModel):
    '''Модель ошибочного ответа получения статуса заказа.'''

    result: Literal['error'] = 'error'
    message: str


GetOrderStatusResponse = GetOrderStatusResponseSuccess | GetOrderStatusResponseError


class CancelOrderResponseSuccess(BaseModel):
    '''Модель успешного ответа отмены заказа.'''

    result: Literal['success'] = 'success'


class CancelOrderResponseRejected(BaseModel):
    '''Модель ошибочного ответа отмены заказа.'''

    result: Literal['order_cancel_rejected'] = 'order_cancel_rejected'
    message: str


class TransientErrorResponse(BaseModel):
    '''Модель ответа временной ошибкой.'''

    result: Literal['transient_error'] = 'transient_error'
    message: str


class OrderRejectedErrorResponse(BaseModel):
    '''Модель ошибочного ответа отправки заказа.'''

    result: Literal['order_rejected'] = 'order_rejected'
    message: str
