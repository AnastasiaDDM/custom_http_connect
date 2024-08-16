'''Ендпоинты методов 2 версии.'''
from ..convenience.contracts.loaders.input import CancelOrderRequest, Order
from ..convenience.contracts.loaders.output import DataError, SendOrderResponseError
from fastapi import APIRouter, Request
from ..convenience.logs import logs
from ..orders import v2 as orders

router = APIRouter()


@router.post('/')
async def create_order(
    request: Request,
    order: Order
):
    '''
    Создание заказа.

    Аргументы:
        order (Order): объект для создания заказа

    Возвращаемый результат:
        (SendOrderResponseSuccess | SendOrderResponseError):
        SendOrderResponseSuccess при успешном создании заказа
        SendOrderResponseError, если создание заказа не удалось выполнить
    '''
    try:
        return await orders.create_order(request.app.order_http, request.app.http, order)
    except Exception as e:
        logs.exception_caught('Error while creating order', error=str(e))
        return SendOrderResponseError(
            data=DataError(partner_error=True)
        )


@router.get('/')
async def get_order_status(
    request: Request,
    order_id: int,
    their_order_id: str
):
    '''
    Получение статуса заказа.

    GET-параметры:
        order_id (int): id заказа в нашей системе
        their_order_id (str): id заказа в системе партнера

    Возвращаемый результат:
        (GetOrderStatusResponseSuccess | GetOrderStatusResponseError):
        GetOrderStatusResponseSuccess при успешном получении статуса заказа
        GetOrderStatusResponseError, если не удалось получить статус
    '''
    return await orders.get_order_status(request.app.http, order_id, their_order_id)


@router.delete('/')
async def cancel_order(
    request: Request,
    order_data: CancelOrderRequest
):
    '''
    Отмена заказа.

    Аргументы:
        order_data (CancelOrderRequest): объект для отмены заказа

    Возвращаемый результат:
        (CancelOrderResponseSuccess | CancelOrderResponseRejected):
        CancelOrderResponseSuccess при успешной отмене заказа
        CancelOrderResponseRejected, если отмену не удалось выполнить

    Исключения:
        TransientErrorResponse: ошибка при отмене заказа.
    '''
    return await orders.cancel_order(
        request.app.order_http,
        order_data.order_id,
        order_data.their_order_id
    )
