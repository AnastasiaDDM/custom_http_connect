'''Конфигурация для тестов методов 2 версии.'''
from copy import deepcopy
from datetime import datetime

from src.convenience.contracts.loaders.input import CancelOrderRequest, Order, OrderClient, OrderItem
from src.convenience.contracts.loaders.output import (
    DataError, ListItemsPriceError,
    ListItemsQuantityError, PriceErrorItem, QuantityErrorItem,
    SendOrderResponseError, SendOrderResponseSuccess
)

# Создание заказа
_ORDER_SEND_ITEMS = [OrderItem(
    their_id='21737',
    price='300',
    count=20
)]

_ORDER_SEND_ITEMS_LIST = [
    OrderItem(
        their_id='21737',
        price='300',
        count=20
    ),
    OrderItem(
        their_id='58598',
        price='400.5',
        count=1
    )
]

_QUANTITY_ERROR_ITEM = QuantityErrorItem(
    their_id='21737',
    ordered=20,
    available=0
)

_PRICE_ERROR_ITEM = PriceErrorItem(
    their_id='58598',
    ordered=400.50,
    available=641.52
)

ORDER_SEND_REQUEST_TYPE_ORDER = Order(
    order_id=123456,
    date=datetime.now(),
    client=OrderClient(
        name='Тест',
        phone='79797979797',
        email='test@bagov.net',
    ),
    their_pharmacy_id='902484',
    order_type=1,
    items=_ORDER_SEND_ITEMS,
    comment='Тестовый заказ',
    extra={}
)

ORDER_SEND_REQUEST_TYPE_RESERVE = deepcopy(ORDER_SEND_REQUEST_TYPE_ORDER)
ORDER_SEND_REQUEST_TYPE_RESERVE.order_type = 2

ORDER_SEND_REQUEST_TWO_ITEMS = deepcopy(ORDER_SEND_REQUEST_TYPE_RESERVE)
ORDER_SEND_REQUEST_TWO_ITEMS.items = _ORDER_SEND_ITEMS_LIST

ORDER_SEND_RESPONSE_SUCCESS = SendOrderResponseSuccess(
    their_order_id='123456',
    items=_ORDER_SEND_ITEMS
)

ORDER_SEND_RESPONSE_PARTNER_ERROR = SendOrderResponseError(
    data=DataError(
        partner_error=True
    )
)

ORDER_SEND_RESPONSE_QUANTITY_ERROR_0 = SendOrderResponseError(
    data=DataError(
        quantity_errors=ListItemsQuantityError(
            items=[_QUANTITY_ERROR_ITEM]
        )
    )
)

ORDER_SEND_RESPONSE_QUANTITY_ERROR_WRONG = SendOrderResponseError(
    data=DataError(
        quantity_errors=ListItemsQuantityError(
            items=[
                QuantityErrorItem(
                    their_id='21737',
                    ordered=20,
                    available=None
                )
            ]
        )
    )
)

ORDER_SEND_RESPONSE_QUANTITY_ERROR_TYPE_ORDER = SendOrderResponseError(
    data=DataError(
        quantity_errors=ListItemsQuantityError(
            items=[
                QuantityErrorItem(
                    their_id='21737',
                    ordered=20,
                    available=None
                )
            ]
        )
    )
)

ORDER_SEND_RESPONSE_PRICE_ERROR_TYPE_RESERVE = SendOrderResponseError(
    data=DataError(
        price_errors=ListItemsPriceError(
            items=[_PRICE_ERROR_ITEM]
        )
    )
)

ORDER_SEND_RESPONSE_QUANTITY_PRICE_ERROR = SendOrderResponseError(
    data=DataError(
        quantity_errors=ListItemsQuantityError(
            items=[_QUANTITY_ERROR_ITEM]
        ),
        price_errors=ListItemsPriceError(
            items=[_PRICE_ERROR_ITEM]
        )
    )
)

# Отмена заказа
ORDER_CANCEL_REQUEST = CancelOrderRequest(
    order_id='123456',
    their_order_id='123456'
)
