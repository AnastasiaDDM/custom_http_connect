'''Модуль для общих моделей 1 версии API.'''
import datetime
import decimal

from pydantic import BaseModel, Field


class Item(BaseModel):
    '''Модель товара.'''

    TheirId: str
    Price: decimal.Decimal = Field(gt=0)
    Count: int = Field(ge=1, lt=2 ** 31)


class Client(BaseModel):
    '''Модель клиента.'''

    FIO: str
    Phone: str
    EMail: str


class Order(BaseModel):
    '''Модель заказа.'''

    OrderId: int = Field(ge=-2 ** 31, lt=2 ** 31)
    Date: datetime.datetime
    Client: Client
    TheirPharmacyId: str
    Reserve: int
    Items: list[Item] = Field(min_length=1)
    Extra: dict


class StatusRequestModel(BaseModel):
    '''Модель запроса статуса заказа у партнера.'''

    OrderId: int = Field(ge=-2 ** 31, lt=2 ** 31)
    TheirOrderId: str
    TheirStatusId: int | None = Field(None, ge=-2 ** 31, lt=2 ** 31)
