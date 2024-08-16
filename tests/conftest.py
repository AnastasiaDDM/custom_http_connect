'''Конфигурация для тестов.'''
import json

import pytest

# Переменные окружения
mp = pytest.MonkeyPatch()
mp.setenv('PARTNERAPI_HTTP_TIMEOUT', '30')
mp.setenv('PARTNERAPI_HTTP_RETRIES_COUNT', '3')
mp.setenv('PARTNERAPI_HTTP_RETRIES_SLEEP', '30')
mp.setenv('PARTNERAPI_HTTP_TIMEOUT_ORDER', '10')
mp.setenv('PARTNERAPI_HTTP_RETRIES_COUNT_ORDER', '1')
mp.setenv('PARTNERAPI_HTTP_RETRIES_SLEEP_ORDER', '0')
mp.setenv('PARTNERAPI_URL', 'http://url.ru')
mp.setenv('PARTNERAPI_RABBITMQ_TIMEOUT', '30')
mp.setenv('PARTNERAPI_RABBITMQ_RETRIES_COUNT', '3')
mp.setenv('PARTNERAPI_RABBITMQ_RETRIES_SLEEP', '30')
mp.setenv('PARTNERAPI_SOURCE_PROJECT_ID', '9')
mp.setenv('PARTNERAPI_KODPOST', '116897')
mp.setenv('PARTNERAPI_METRICS_PORT', '23241')

# Переменные для тестов
PARTNERAPI_ORDER_ID = '123456'

PARTNERAPI_ORDER_RAW_RESPONSE = json.dumps({
    'status': 'ok',
    'order_id': PARTNERAPI_ORDER_ID
}).encode('utf-8')

PARTNERAPI_ORDER_ERROR_RAW_RESPONSE = json.dumps({
    'status': 'error',
    'errors': 'Internal server error'
}).encode('utf-8')

PARTNERAPI_FIND_ORDERS_EMPTY_RAW_RESPONSE = json.dumps({
    'data': {
        'ids': []
    }
}).encode('utf-8')

PARTNERAPI_ALREADY_EXISTS_ORDER_ID = '654321'

PARTNERAPI_FIND_ORDERS_RAW_RESPONSE = json.dumps({
    'data': {
        'ids': [PARTNERAPI_ALREADY_EXISTS_ORDER_ID]
    }
}).encode('utf-8')
