'''Конфигурация для тестов.'''
from datetime import datetime
from decimal import Decimal
import json

from src.convenience.contracts.loader import CancelOrderRequest
from src import common

from ..conftest import PARTNERAPI_ORDER_ID

OUR_ORDER = common.Order(
    OrderId=123456,
    Date=datetime.now(),
    Client=common.Client(
        FIO='Тест',
        Phone='+79797979797',
        EMail='test@bagov.net',
    ),
    TheirPharmacyId='12',
    Reserve=2,
    Items=[common.Item(
        TheirId='369617',
        Price=Decimal(100),
        Count=1
    )],
    Comment='Тестовый заказ',
    Extra={}
)


def create_partner_status_response(their_status):
    return json.dumps({
        'status': 'ok',
        'data': {
            PARTNERAPI_ORDER_ID: {
                'status': their_status
            }
        }
    }).encode('utf-8')


OUR_STATUS_REQUEST = common.StatusRequestModel(
    OrderId=123456,
    TheirOrderId=PARTNERAPI_ORDER_ID
)

ORDER_CANCEL_REQUEST = CancelOrderRequest(
    order_ID=int(PARTNERAPI_ORDER_ID),
    their_order_ID=PARTNERAPI_ORDER_ID
)
