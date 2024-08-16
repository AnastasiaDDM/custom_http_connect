'''Модуль обработки заказов 2 версия.'''
from decimal import Decimal
import json
import re

import aiohttp
from ..convenience.contracts.loaders.input import Order
from ..convenience.contracts.loaders.output import (
    CancelOrderResponseRejected, CancelOrderResponseSuccess, DataError,
    GetOrderStatusResponseError, GetOrderStatusResponseSuccess,
    ListItemsPriceError, ListItemsQuantityError, PriceErrorItem, QuantityErrorItem,
    SendOrderResponseError, SendOrderResponseSuccess, TransientErrorResponse
)
from ..convenience.httpclient.httpclient import HTTP
from ..convenience.logs import logs
from .. import config, metrics

MAPPING_DICT = {
    'created': 0,
    'accepted': 1,
    'delivery': 1,
    'in_shop': 4,
    'done': 2,
    'cancelled': 3
}


def _get_detail_from_errors(errors_items: dict, order: Order):
    '''Метод обработки ошибок по цене и кол-ву от партнера.'''
    # Детализированный список ошибок по товарам
    quantity_errors_items = []
    price_errors_items = []

    list_items_quantity_error = None
    list_items_price_error = None

    ordered_items = {}
    # Формирование структуры данных с данными о товарах в заказе
    for item in order.items:
        ordered_items[item.their_id] = {'price': item.price, 'count': item.count}

    # По каждому товару обрабатываем текст об ошибке
    for item_id, mssg_error in errors_items.items():
        # Товар не найден у партнера
        if mssg_error[0] == 'Item not found':
            # Устанавливаем доступное кол-во в 0
            quantity_errors_items.append(
                QuantityErrorItem(
                    their_id=str(item_id),
                    ordered=int(ordered_items[item_id]['count']),
                    available=0
                )
            )
        # Запрошено недоступное кол-во
        elif mssg_error[0] == 'Wrong quantity':
            # Зафиксируем id товара, но available не будем устанавливать
            quantity_errors_items.append(
                QuantityErrorItem(
                    their_id=str(item_id),
                    ordered=int(ordered_items[item_id]['count']),
                    available=None
                )
            )

        # Некорректная цена
        elif 'Wrong price' in mssg_error[0]:

            # Пример mssg_error[0] = 'Wrong price: current price is 455.23 or NONE'
            all_prices = re.findall(r'NONE|[0-9]*[.,]?[0-9]+', mssg_error[0])
            available_price = 0

            # Проверяем тип заказа
            if order.order_type == 2:
                # Берем цену бронирования (1 цена)
                try:
                    available_price = Decimal(all_prices[0])
                except Exception:
                    pass
            else:
                # Берем цену предзаказа (2 цена)
                try:
                    available_price = Decimal(all_prices[1])
                except Exception:
                    pass

            if available_price == 0:
                # Устанавливаем доступное кол-во в 0
                quantity_errors_items.append(
                    QuantityErrorItem(
                        their_id=str(item_id),
                        ordered=int(ordered_items[item_id]['count']),
                        available=0
                    )
                )
            else:
                # Фиксируем информацию об ошибке по цене
                price_errors_items.append(
                    PriceErrorItem(
                        their_id=str(item_id),
                        ordered=Decimal(ordered_items[item_id]['price']),
                        available=available_price
                    )
                )

    # Формирование модели ошибки для ответа
    if len(quantity_errors_items) > 0:
        list_items_quantity_error = ListItemsQuantityError(
            items=quantity_errors_items
        )

    if len(price_errors_items) > 0:
        list_items_price_error = ListItemsPriceError(
            items=price_errors_items
        )

    if list_items_quantity_error is None and list_items_price_error is None:
        # Возникла необработанная ошибка, выбрасываем исключение
        # Выше ловим его и отправляет обшую партнерскую ошибку
        raise Exception

    return list_items_quantity_error, list_items_price_error


async def create_order(create_order_http, http, our_order: Order):
    '''Метод отправки заказа партнеру.'''
    # Проверяем не создан ли уже заказ с таким id
    _, body = await http.request(
        'GET',
        config.URL + f'/find-orders?external_id={our_order.order_id}'
    )
    result = json.loads(body)
    ids = result['data']['ids']
    if len(ids) != 0:

        # Возвращаем ранее созданный заказ
        return SendOrderResponseSuccess(
            their_order_id=str(min(ids)),
            items=our_order.items
        )

    # Формирование тела запроса на создание заказа
    form = aiohttp.FormData([
        ('shop_id', our_order.their_pharmacy_id),
        ('phone', our_order.client.phone),
        ('first_name', our_order.client.name),
        ('email', our_order.client.email),
        ('external_id', our_order.order_id)
    ])
    for item in our_order.items:
        form.add_field('ids[]', item.their_id)
        form.add_field('quantity[]', item.count)
        form.add_field('prices[]', item.price)

    logs.debug('Sending order to Partner', order_ID=our_order.order_id)

    # Отправка запроса
    _, body = await create_order_http.request(
        'POST',
        config.URL + '/create',
        data=form
    )
    result_dict = json.loads(body)

    # Заказ успешно создан
    if result_dict['status'] == 'ok':
        logs.debug(
            'Order is created SUCCESSFUL',
            order_ID=our_order.order_id,
            their_order_ID=result_dict['order_id']
        )
        return SendOrderResponseSuccess(
            their_order_id=str(result_dict['order_id']),
            items=our_order.items
        )

    # Заказ не создан - ошибка
    elif result_dict['status'] == 'error':

        # Обработка ошибок по товарам,
        # если таких нет - исключение выдаст партнерскую ошибку
        errors_items = result_dict['errors']['items']

        # Детализируем информацию об остатках каждого товара
        quantity_errors_items, price_errors_items = _get_detail_from_errors(
            errors_items,
            our_order
        )

        logs.error(
            'Quantity or Price errors while creating order',
            quantity_errors_items=str(quantity_errors_items),
            price_errors_items=str(price_errors_items)
        )
        return SendOrderResponseError(
            data=DataError(
                quantity_errors=quantity_errors_items,
                price_errors=price_errors_items
            )
        )

    raise Exception('Invalid answer from remote API')


async def get_order_status(http: HTTP, order_id: int, their_order_id: str):
    '''Метод получения статуса заказа от партнера.'''
    try:
        logs.debug('Getting order info from Partner', order_ID=order_id)
        _, body = await http.request(
            'GET',
            config.URL + f'/orders-data?order_ids={their_order_id}'
        )
        result_dict = json.loads(body)

        if result_dict['status'] == 'ok':
            logs.debug('Getting order info: Succesful', order_ID=order_id)
            their_order_status = result_dict['data'][their_order_id]['status']
            our_order_status = MAPPING_DICT.get(their_order_status, -1)
            if our_order_status == -1:
                logs.error('Order status mapping error', their_status=their_order_status)
                metrics.order_status_mapping_error.labels(config.PROJECT_NAME).inc()

            return GetOrderStatusResponseSuccess(
                status_id=our_order_status,
                their_status_id=our_order_status
            )

        else:
            errors = result_dict.get('errors')
            raise Exception(errors)

    except Exception as e:
        logs.exception_caught(
            'Error while getting order status',
            order_ID=order_id,
            error=str(e)
        )
        return GetOrderStatusResponseError(
            message=str(e)
        )


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
            return CancelOrderResponseRejected(message=str(errors))

        # Ошибка временная
        return TransientErrorResponse(message=str(errors))

    except Exception as ex:
        logs.exception_caught(
            'HTTP response error',
            their_order_ID=their_order_ID,
            order_ID=order_ID
        )
        return TransientErrorResponse(message=str(ex))
