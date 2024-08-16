'''Модуль конфигурации env.'''
import os

PROJECT_NAME = 'PartnerAPI'

options = {
    'HTTP_TIMEOUT': float,
    'HTTP_RETRIES_COUNT': int,
    'HTTP_RETRIES_SLEEP': float,

    'HTTP_TIMEOUT_ORDER': float,
    'HTTP_RETRIES_COUNT_ORDER': int,
    'HTTP_RETRIES_SLEEP_ORDER': float,

    'URL': str,

    'RABBITMQ_TIMEOUT': float,
    'RABBITMQ_RETRIES_COUNT': int,
    'RABBITMQ_RETRIES_SLEEP': float,

    'SOURCE_PROJECT_ID': int,
    'KODPOST': int,

    'METRICS_PORT': int
}

variables = globals()

for name in options:
    variables[name] = options[name](os.environ[f'{PROJECT_NAME.upper()}_{name}'])
