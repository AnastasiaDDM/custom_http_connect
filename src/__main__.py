'''Главный модуль сервиса.'''
import asyncio
import sys

from .convenience.httpclient import httpclient
from .convenience.logs import logs
from prometheus_async.aio.web import start_http_server
import uvicorn

from . import api
from . import config


async def main():
    '''Метод запуска сервиса.'''
    server = uvicorn.Server(uvicorn.Config(
        api.app,
        host='0.0.0.0',
        port=8000,
        log_config=None)
    )

    async with (
        httpclient.HTTP(
            config.HTTP_RETRIES_COUNT,
            config.HTTP_RETRIES_SLEEP,
            config.HTTP_TIMEOUT
        ) as http,
        httpclient.HTTP(
            config.HTTP_RETRIES_COUNT_ORDER,
            config.HTTP_RETRIES_SLEEP_ORDER,
            config.HTTP_TIMEOUT_ORDER
        ) as order_http,
        asyncio.TaskGroup() as task_group
    ):
        api.app.order_http = order_http
        api.app.http = http

        task_group.create_task(server.serve(), name='API')
        task_group.create_task(start_http_server(port=config.METRICS_PORT), name='metrics')

        logs.info('Initialization finished')

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except BaseException:
        logs.exception_caught('Uncaught exception')
        sys.exit(1)
