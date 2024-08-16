'''Тесты для сервиса (заказы) 2 версии.'''
from unittest.mock import AsyncMock

from src.routers.v2 import cancel_order, create_order
import pytest

from .conftest import (
    ORDER_CANCEL_REQUEST, ORDER_SEND_REQUEST_TWO_ITEMS, ORDER_SEND_REQUEST_TYPE_ORDER,
    ORDER_SEND_REQUEST_TYPE_RESERVE, ORDER_SEND_RESPONSE_PARTNER_ERROR,
    ORDER_SEND_RESPONSE_PRICE_ERROR_TYPE_RESERVE, ORDER_SEND_RESPONSE_QUANTITY_ERROR_0,
    ORDER_SEND_RESPONSE_QUANTITY_ERROR_WRONG, ORDER_SEND_RESPONSE_QUANTITY_PRICE_ERROR,
    ORDER_SEND_RESPONSE_SUCCESS
)
from ..conftest import (
    PARTNERAPI_ALREADY_EXISTS_ORDER_ID, PARTNERAPI_FIND_ORDERS_EMPTY_RAW_RESPONSE,
    PARTNERAPI_FIND_ORDERS_RAW_RESPONSE, PARTNERAPI_ORDER_ID, PARTNERAPI_ORDER_RAW_RESPONSE
)


@pytest.mark.asyncio
class TestOrders2:
    '''Класс тестирования заказов V2.'''

    async def test_create_order_success(self):
        '''Тест создания заказа - успешный ответ.'''
        # Мокаем request
        mocked_api_request = AsyncMock()

        # Имитируем успешный ответ от Партнера о том, что заказ с заданным нами ID не найден
        mocked_api_request.app.http.request.return_value = (
            None,
            PARTNERAPI_FIND_ORDERS_EMPTY_RAW_RESPONSE
        )
        # Имитируем успешный ответ от Партнера о созданном заказе
        mocked_api_request.app.order_http.request.return_value = (
            None,
            PARTNERAPI_ORDER_RAW_RESPONSE
        )

        result = await create_order(mocked_api_request, ORDER_SEND_REQUEST_TYPE_ORDER)
        # Проверяем, что в ответе вернулся номер заказа
        assert result.their_order_id == PARTNERAPI_ORDER_ID
        assert result == ORDER_SEND_RESPONSE_SUCCESS

    async def test_create_exists_order_success(self):
        '''Тест создания существующего заказа - успешный ответ.'''
        # Мокаем request
        mocked_api_request = AsyncMock()

        # Имитируем успешный ответ от Партнера о том, что заказ с заданным нами ID найден
        mocked_api_request.app.http.request.return_value = (
            None,
            PARTNERAPI_FIND_ORDERS_RAW_RESPONSE
        )

        result = await create_order(mocked_api_request, ORDER_SEND_REQUEST_TYPE_ORDER)
        # Проверяем, что в ответе вернулся номер заказа
        assert result.their_order_id == PARTNERAPI_ALREADY_EXISTS_ORDER_ID

    @pytest.mark.parametrize('order_http_body', [
        # Общая ошибка в сервисе запроса к партнеру
        (Exception),
        # Вызвана не кол-вом и не ценой
        (b'{"status":"error","errors":{"phone":"Required format 79XXXXXXXXX"}}'),
        # Неизвестная ошибка по товарам
        (b'{"status":"error","errors":{"items":{"21737":["Unknown answer from items."]}}}'),
        # Неизвестный ответ от партнера
        (b'{"status":"unknown_answer"}')
    ])
    async def test_create_order_partner_error(self, order_http_body):
        '''Тест создания заказа - ошибка партнера в лоадере.'''
        # Мокаем request
        mocked_api_request = AsyncMock()

        # Имитируем успешный ответ от Партнера о том, что заказ с заданным нами ID не найден
        mocked_api_request.app.http.request.return_value = (
            None,
            PARTNERAPI_FIND_ORDERS_EMPTY_RAW_RESPONSE
        )
        # Подставляем параметры в body-ответ от Партнера при запросе на создание заказа
        mocked_api_request.app.order_http.request.return_value = (
            None,
            order_http_body
        )

        result = await create_order(mocked_api_request, ORDER_SEND_REQUEST_TYPE_ORDER)
        assert result == ORDER_SEND_RESPONSE_PARTNER_ERROR

    @pytest.mark.parametrize('order_http_body, response_result', [
        (
            # Товар не найден
            b'{"status":"error","errors":{"items":{"21737":["Item not found"]}}}',
            ORDER_SEND_RESPONSE_QUANTITY_ERROR_0
        ),
        (
            # Неверное кол-во
            b'{"status":"error","errors":{"items":{"21737":["Wrong quantity"]}}}',
            ORDER_SEND_RESPONSE_QUANTITY_ERROR_WRONG
        ),
        (
            # Ошибка по цене (тип предзаказ (1)).
            # В нашей системе обрабатываем как ошибку по кол-ву.
            # В ответе: 1 цена - бронирование, 2 цена - предзаказ
            # NONE говорит о том, что у партнера товар закончился (ошибка по кол-ву)
            b'{"status":"error","errors":{"items":{"21737":["Wrong price: current price is 641.52 or NONE"]}}}',
            ORDER_SEND_RESPONSE_QUANTITY_ERROR_0
        )
    ])
    async def test_create_order_quantity_error(self, order_http_body, response_result):
        '''Тест создания заказа - ошибка по количеству.'''
        # Мокаем request
        mocked_api_request = AsyncMock()

        # Имитируем успешный ответ от Партнера о том, что заказ с заданным нами ID не найден
        mocked_api_request.app.http.request.return_value = (
            None,
            PARTNERAPI_FIND_ORDERS_EMPTY_RAW_RESPONSE
        )
        # Подставляем параметры в body-ответ от Партнера при запросе на создание заказа
        mocked_api_request.app.order_http.request.return_value = (
            None,
            order_http_body
        )

        result = await create_order(mocked_api_request, ORDER_SEND_REQUEST_TYPE_ORDER)
        # Сравниваем полученный результат с переданным в параметрах объектом response_result
        assert result == response_result

    async def test_create_order_price_error_type_reserve(self):
        '''Тест создания заказа - ошибка по цене (тип бронирование (2)).'''
        # Мокаем request
        mocked_api_request = AsyncMock()

        # Имитируем успешный ответ от Партнера о том, что заказ с заданным нами ID не найден
        mocked_api_request.app.http.request.return_value = (
            None,
            PARTNERAPI_FIND_ORDERS_EMPTY_RAW_RESPONSE
        )
        # Имитируем ответ с ошибкой от Партнера
        # В ответе: 1 цена - бронирование, 2 цена - предзаказ
        mocked_api_request.app.order_http.request.return_value = (
            None,
            b'{"status":"error","errors":{"items":{"21737":["Wrong price: current price is 641.52 or NONE"]}}}'
        )

        result = await create_order(mocked_api_request, ORDER_SEND_REQUEST_TYPE_RESERVE)
        result == ORDER_SEND_RESPONSE_PRICE_ERROR_TYPE_RESERVE

    async def test_create_order_quantity_price_error(self):
        '''Тест создания заказа - ошибка по цене и кол-ву (тип бронирование (2)).'''
        # Мокаем request
        mocked_api_request = AsyncMock()

        # Имитируем успешный ответ от Партнера о том, что заказ с заданным нами ID не найден
        mocked_api_request.app.http.request.return_value = (
            None,
            PARTNERAPI_FIND_ORDERS_EMPTY_RAW_RESPONSE
        )
        # Имитируем ответ с ошибкой от Партнера
        # В ответе: 1 цена - бронирование, 2 цена - предзаказ
        mocked_api_request.app.order_http.request.return_value = (
            None,
            b'''{"status":"error","errors":{"items":{"21737":["Item not found"],
            "58598":["Wrong price: current price is 641.52 or 750.00"]}}}'''
        )

        result = await create_order(mocked_api_request, ORDER_SEND_REQUEST_TWO_ITEMS)
        result == ORDER_SEND_RESPONSE_QUANTITY_PRICE_ERROR

    async def test_cancel_order_success(self):
        '''Тест отмены заказа - успешный ответ.'''
        # Мокаем request
        mocked_api_request = AsyncMock()

        # Имитируем успешный ответ от Партнера (response, body)
        mocked_api_request.app.order_http.request.return_value = (
            None,
            b'{"status": "ok", "data": []}'
        )

        result = await cancel_order(mocked_api_request, ORDER_CANCEL_REQUEST)
        assert result.result == 'success'

    async def test_cancel_order_rejected(self):
        '''Тест отмены заказа - невозможно по ограничениям логики.'''
        # Мокаем request
        mocked_api_request = AsyncMock()

        # Имитируем ошибочный ответ от Партнера (response, body)
        mocked_api_request.app.order_http.request.return_value = (
            None,
            b'{"status": "error", "errors": ["cancellation not allowed"]}'
        )

        result = await cancel_order(mocked_api_request, ORDER_CANCEL_REQUEST)
        assert result.result == 'order_cancel_rejected'

    async def test_cancel_order_transient_error(self):
        '''Тест отмены заказа - временная ошибка.'''
        # Мокаем request
        mocked_api_request = AsyncMock()

        # Имитируем ошибочный ответ от Партнера (response, body)
        mocked_api_request.app.order_http.request.return_value = (
            None,
            b'{"status": "error", "errors": []}'
        )

        result = await cancel_order(mocked_api_request, ORDER_CANCEL_REQUEST)
        assert result.result == 'transient_error'
