'''Ендпоинты методов 1 версии.'''
from ..convenience.contracts.loader import (
    CancelOrderRequest, GetOrderStatusResponseError, GetOrderStatusResponseSuccess,
    OrderRejectedErrorResponse, SendOrderResponseSuccess, TransientErrorResponse
)
from fastapi import APIRouter, Request
from ..convenience.logs import logs
from .. import common, config, metrics
from ..orders import v1 as orders

router = APIRouter()


@router.post('/SendOrder')
async def send_order(request: Request, order: common.Order):
    '''Отправка заказа партнеру.'''
    http = request.app.http
    create_order_http = request.app.order_http
    try:
        their_order_id = await orders.create_order(create_order_http, http, order)
    except orders.RejectedOrderException as e:
        logs.exception_caught('Error while order sending to API')
        metrics.orders_creating_errors_counter.labels(config.PROJECT_NAME).inc()
        return OrderRejectedErrorResponse(Message=str(e))

    except Exception:
        logs.exception_caught('Error while define existing of order')
        metrics.orders_creating_errors_counter.labels(config.PROJECT_NAME).inc()
        return TransientErrorResponse(Message='HTTP response error')

    items = []

    for item in order.Items:
        items.append({
            'TheirId': item.TheirId,
            'Price': str(item.Price),
            'Count': item.Count
        })

    metrics.orders_created_counter.labels(config.PROJECT_NAME).inc()
    return SendOrderResponseSuccess(TheirOrderId=their_order_id, Items=items)


@router.post('/GetOrderStatus')
async def get_order_status(request: Request, order_status: common.StatusRequestModel):
    '''Получение статуса заказа.'''
    result, message, their_order_status, our_order_status = await orders.get_order(
        request.app.http,
        order_status
    )
    if result:
        if order_status.TheirStatusId != their_order_status:
            metrics.order_changing_status_counter.labels(config.PROJECT_NAME).inc()
        return GetOrderStatusResponseSuccess(
            StatusId=our_order_status,
            TheirStatusId=their_order_status
        )
    else:
        return GetOrderStatusResponseError(Message=message)


@router.post('/cancel_order')
async def cancel_order(
        request: Request,
        arguments: CancelOrderRequest
):
    '''
    Отмена заказа.

    Аргументы:
        request (Request): запрос
        arguments (CancelOrderRequest): объект для отмены заказа

    Возвращаемый результат:
        (CancelOrderResponseSuccess | CancelOrderResponseRejected):
        CancelOrderResponseSuccess при успешной отмене заказа
        CancelOrderResponseRejected, если отмену не удалось выполнить

    Исключения:
        TransientErrorResponse: ошибка при отмене заказа.
    '''
    return await orders.cancel_order(
        request.app.order_http,
        arguments.order_ID,
        arguments.their_order_ID
    )
