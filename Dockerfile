FROM python:3 AS base

WORKDIR /app/

COPY requirements.txt .

RUN pip install -r requirements.txt && pip cache purge && rm requirements.txt

COPY src/ ./src

ARG VERSION
ARG BUILD_NUMBER

ENV CONVENIENCE_LOGS_SERVICE=custom_http_connect
ENV CONVENIENCE_LOGS_VERSION=${VERSION}
ENV CONVENIENCE_LOGS_BUILD_NUMBER=${BUILD_NUMBER}

ENTRYPOINT ["python", "-m"]
CMD ["src"]

FROM base AS tests

COPY tests tests
COPY .coveragerc ./

CMD ["pytest", "-vv", "--cov"]

FROM base AS debug

FROM base AS production
