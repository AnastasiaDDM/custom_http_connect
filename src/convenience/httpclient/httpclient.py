from typing import Mapping, Self

import aiohttp
from ..logs import logs
from the_retry import retry


class ResponseError(Exception):
    pass


class HTTP():
    def __init__(
            self,
            retries_count: int,
            retries_sleep: float,
            timeout: float,
            maximum_body_size: int = 2 ** 24,
            retry_status_error: bool = True,
            logging_responsed_blocks: bool = True,
            expected_exception: BaseException | tuple[BaseException, ...] = BaseException,
            **kwargs: Mapping):
        self.retries_count = retries_count
        self.retries_sleep = retries_sleep
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.maximum_body_size = maximum_body_size
        self.retry_status_error = retry_status_error
        self.session = aiohttp.ClientSession(timeout=self.timeout, **kwargs)
        self.expected_exception = expected_exception
        self.logging_responsed_blocks = logging_responsed_blocks

    async def __aenter__(self):
        await self.session.__aenter__()

        return self

    async def __aexit__(self, exception_type, exception, traceback):
        await self.session.__aexit__(exception_type, exception, traceback)

    async def request(self, method, URL, **kwargs):
        @retry(
            expected_exception=self.expected_exception,
            attempts=self.retries_count,
            backoff=self.retries_sleep
        )
        async def _request(self: Self, method, URL, **kwargs):
            body = None

            logs.debug('Sending HTTP request', method=method, URL=URL, kwargs=kwargs)

            async with self.session.request(method, URL, **kwargs, verify_ssl=False) as response:
                body = b''

                while True:
                    block = await response.content.read(self.maximum_body_size - len(body))
                    body += block
                    if self.logging_responsed_blocks:
                        logs.debug('Received response block', block=block)

                    if response.content.at_eof():
                        break

                    if len(body) == self.maximum_body_size:
                        raise ResponseError('Response too big')

                if self.retry_status_error:
                    response.raise_for_status()

                return response, body

        return await _request(self, method, URL, **kwargs)
