'''Модуль обработки заказов 1 версия.'''
import json

import aiohttp
from ..convenience.contracts.loader import (
    CancelOrderResponseRejected, CancelOrderResponseSuccess, TransientErrorResponse
)
from ..convenience.httpclient.httpclient import HTTP
from ..convenience.logs import logs
from .. import common, config, metrics

MAPPING_DICT = {
    'created': 0,
    'accepted': 1,
    'delivery': 1,
    'in_shop': 4,
    'done': 2,
    'cancelled': 3
}


class RejectedOrderException(Exception):
    '''Исключение по заказу.'''


async def create_order(create_order_http, http, our_order: common.Order):
    '''Создание заказа.'''
    _, body = await http.request(
        'GET',
        config.URL + f'/find-orders?external_id={our_order.OrderId}'
    )
    result = json.loads(body)
    ids = result['data']['ids']
    if len(ids) != 0:
        return str(min(ids))
    else:
        form = aiohttp.FormData([
            ('shop_id', our_order.TheirPharmacyId),
            ('phone', our_order.Client.Phone),
            ('first_name', our_order.Client.FIO),
            ('email', our_order.Client.EMail),
            ('external_id', our_order.OrderId)
        ])
        for item in our_order.Items:
            form.add_field('ids[]', item.TheirId)
            form.add_field('quantity[]', item.Count)
            form.add_field('prices[]', item.Price)

        logs.debug('Sending order to Partner', order_ID=our_order.OrderId)
        _, body = await create_order_http.request(
            'POST',
            config.URL + '/create',
            data=form
        )
        result_dict = json.loads(body)
        if result_dict['status'] == 'ok':
            logs.debug(
                'Order is created SUCCESSFUL',
                order_ID=our_order.OrderId,
                their_order_ID=result_dict['order_id']
            )
            return str(result_dict['order_id'])
        elif result_dict['status'] == 'error':
            errors = result_dict.get('errors')
            logs.error('Remote API rejected order', result=errors)
            raise RejectedOrderException(errors)
        else:
            logs.error('ERROR while creating order')
            raise Exception('Invalid answer from remote API')


async def get_order(http, order_status: common.StatusRequestModel):
    '''Получение статуса заказа.'''
    logs.debug('Getting order info from Partner', order_ID=order_status.OrderId)
    _, body = await http.request(
        'GET',
        config.URL + f'/orders-data?order_ids={order_status.TheirOrderId}'
    )
    result_dict = json.loads(body)
    errors = result_dict.get('errors')
    if result_dict['status'] == 'ok':
        logs.debug('Getting order info: Succesful', order_ID=order_status.OrderId)
        their_order_status = result_dict['data'][order_status.TheirOrderId]['status']
        our_order_status = MAPPING_DICT.get(their_order_status, -1)
        if our_order_status == -1:
            logs.error('Order status mapping error', their_status=their_order_status)
            metrics.order_status_mapping_error.labels(config.PROJECT_NAME).inc()
        return True, result_dict['status'], our_order_status, our_order_status
    else:
        return False, str(errors), None, None


async def cancel_order(http: HTTP, order_ID: int, their_order_ID: str):
    '''Метод отмены заказа у партнера.'''
    try:
        payload = {"order_id": str(their_order_ID)}

        # Запрос к API партнера
        _, body = await http.request(
            'POST',
            config.URL + '/cancel',
            data=payload
        )

        result_dict = json.loads(body)

        # Корректный ответ (статус 'ok')
        if result_dict.get('status') == 'ok':
            logs.info(
                'Order cancelled',
                their_order_ID=their_order_ID,
                order_ID=order_ID
            )
            return CancelOrderResponseSuccess()

        errors = result_dict.get('errors')
        # Некорректная бизнес-логика
        if errors[0] == 'cancellation not allowed':
            return CancelOrderResponseRejected(Message=str(errors))

        # Ошибка временная
        return TransientErrorResponse(Message=str(errors))

    except Exception as ex:
        logs.exception_caught(
            'HTTP response error',
            their_order_ID=their_order_ID,
            order_ID=order_ID
        )
        return TransientErrorResponse(Message=str(ex))
