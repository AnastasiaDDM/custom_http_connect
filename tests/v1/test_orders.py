'''Тесты для сервиса (заказы) 1 версии.'''
from unittest.mock import AsyncMock

from src.convenience.contracts.loader import (
    CancelOrderResponseRejected, CancelOrderResponseSuccess, TransientErrorResponse
)
from src.orders.v1 import (
    create_order, get_order, MAPPING_DICT, RejectedOrderException
)
from src.routers.v1 import cancel_order
import pytest

from .conftest import (
    create_partner_status_response, ORDER_CANCEL_REQUEST, OUR_ORDER, OUR_STATUS_REQUEST
)
from ..conftest import (
    PARTNERAPI_ALREADY_EXISTS_ORDER_ID,
    PARTNERAPI_FIND_ORDERS_EMPTY_RAW_RESPONSE, PARTNERAPI_FIND_ORDERS_RAW_RESPONSE,
    PARTNERAPI_ORDER_ERROR_RAW_RESPONSE, PARTNERAPI_ORDER_ID,
    PARTNERAPI_ORDER_RAW_RESPONSE
)


@pytest.mark.asyncio
class TestOrders:
    '''Класс тестирования заказов.'''

    async def test_create_order_success(self):
        # Имитируем успешный ответ от Партнера о том, что заказа с заданным нашим ID не найдено
        mocked_http = AsyncMock()
        mocked_http.request.return_value = (None, PARTNERAPI_FIND_ORDERS_EMPTY_RAW_RESPONSE)

        # Имитируем успешный ответ от Партнера о созданном заказе
        mocked_create_order_http = AsyncMock()
        mocked_create_order_http.request.return_value = (None, PARTNERAPI_ORDER_RAW_RESPONSE)

        result = await create_order(mocked_create_order_http, mocked_http, OUR_ORDER)
        # Проверяем, что в ответе вернулся номер заказа
        assert result == PARTNERAPI_ORDER_ID

    async def test_create_order_already_exists(self):
        # Имитируем успешный ответ от Партнера о том, что заказ с заданным нашим найден
        mocked_http = AsyncMock()
        mocked_http.request.return_value = (None, PARTNERAPI_FIND_ORDERS_RAW_RESPONSE)

        mocked_create_order_http = AsyncMock()

        result = await create_order(mocked_create_order_http, mocked_http, OUR_ORDER)
        # Проверяем, что в ответе вернулся номер ранее созданного заказа
        assert result == PARTNERAPI_ALREADY_EXISTS_ORDER_ID

    async def test_create_order_reject(self):
        # Имитируем успешный ответ от Партнера о том, что заказа с заданным нашим ID не найдено
        mocked_http = AsyncMock()
        mocked_http.request.return_value = (None, PARTNERAPI_FIND_ORDERS_EMPTY_RAW_RESPONSE)

        # Имитируем ответ от Партнера с ошибкой
        mocked_create_order_http = AsyncMock()
        mocked_create_order_http.request.return_value = (None, PARTNERAPI_ORDER_ERROR_RAW_RESPONSE)

        try:
            await create_order(mocked_create_order_http, mocked_http, OUR_ORDER)
        except RejectedOrderException as error:
            # Проверяем, что вызвано нужное исключение
            assert isinstance(error, RejectedOrderException)

    async def test_get_order_success(self):
        # Имитируем успешный ответ от Партнера
        mocked_http = AsyncMock()

        mocked_response = AsyncMock()
        mocked_response.status = 200

        # Для каждого чужого статуса проверяем корректность перевода в наш
        for their_status in MAPPING_DICT:
            mocked_http.request.return_value = (
                mocked_response, create_partner_status_response(their_status)
            )
            _, _, _, our_order_status = await get_order(
                mocked_http, OUR_STATUS_REQUEST
            )

            assert our_order_status == MAPPING_DICT.get(their_status)

    async def test_get_order_unknown_status(self):
        # Имитируем успешный ответ от Партнера с неизвестным статусом
        mocked_http = AsyncMock()

        mocked_response = AsyncMock()
        mocked_response.status = 200

        their_status = 'unknown-status'

        mocked_http.request.return_value = (
            mocked_response, create_partner_status_response(their_status)
        )
        _, _, _, our_order_status = await get_order(
            mocked_http, OUR_STATUS_REQUEST
        )

        # Проверяем, что вернулся наш статус, равный -1
        assert our_order_status == -1

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
        assert result == CancelOrderResponseSuccess()

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
        assert result.Result == CancelOrderResponseRejected(Message='').Result

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
        assert result.Result == TransientErrorResponse(Message='').Result
