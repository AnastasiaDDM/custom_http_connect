'''Модели входящих запросов.'''
from datetime import datetime
from decimal import Decimal
from enum import IntEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class OrderClient(BaseModel):
    '''Модель данных о клиенте.'''

    name: str                                           # ФИО покупателя
    phone: str                                          # телефон покупателя
    email: str                                          # email покупателя


class OrderItem(BaseModel):
    '''Модель данных о товаре в заказе.'''

    their_id: str | None = Field(None, max_length=256)  # ид заказа в агрегаторе
    price: Decimal = Field(gt=0)                        # стоимость товара
    count: int = Field(ge=1, lt=2 ** 31)                # количество товара
    part: str | None = Field(None, max_length=256)      # партия товара


class OrderTypeEnum(IntEnum):
    '''Модель типов заказов.'''

    order = 1       # тип предзаказ
    reserve = 2     # тип бронирование


class Order(BaseModel):
    '''Модель запроса создания заказа общая.'''

    model_config = ConfigDict(use_enum_values=True)

    order_id: int                                       # ид заказа
    date: datetime                                      # дата заказа
    client: OrderClient                                 # данные клиента
    their_pharmacy_id: str                              # ид аптеки
    order_type: OrderTypeEnum                           # тип заказа 1=предзаказ, 2=бронирование
    items: list[OrderItem]                              # содержимое заказа
    comment: str | None                                 # коментарий к заказу
    extra: dict                                         # доп. инфо


class PreOrderTypeOrder(Order):
    '''Модель запроса создания заказа с типом предзаказ.'''

    order_type: Literal[OrderTypeEnum.order] = OrderTypeEnum.order


class ReserveTypeOrder(Order):
    '''Модель запроса создания заказа с типом бронирование.'''

    order_type: Literal[OrderTypeEnum.reserve] = OrderTypeEnum.reserve


class GetOrderStatusRequest(BaseModel):
    '''Модель запроса получения статуса заказа.'''

    order_id: int = Field(ge=-2 ** 63, le=2 ** 63 - 1)
    their_order_id: str = Field(max_length=256)
    their_pharmacy_id: str | None = Field(None, max_length=256)
    their_status_id: int | None = Field(None, ge=-2 ** 63, lt=2 ** 63)


class CancelOrderRequest(BaseModel):
    '''Модель запроса отмены заказа.'''

    order_id: int = Field(ge=-2 ** 63, le=2 ** 63 - 1)
    their_order_id: str = Field(max_length=256)
    their_pharmacy_id: str | None = Field(None, max_length=256)
    client_phone: str | None = None
