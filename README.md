# PARTNERAPI

Сервис интеграции с API партнера.
Содержит 2 версии API. Обе версии включают в себя методы создания заказа, получения статуса заказа и отмену заказа пользователем.

## Запуск сервиса

Для запуска необходимо указать следующие переменные среды:

```
PARTNERAPI_HTTP_TIMEOUT=30
PARTNERAPI_HTTP_RETRIES_COUNT=3
PARTNERAPI_HTTP_RETRIES_SLEEP=30

PARTNERAPI_HTTP_TIMEOUT_ORDER=10
PARTNERAPI_HTTP_RETRIES_COUNT_ORDER=1
PARTNERAPI_HTTP_RETRIES_SLEEP_ORDER=0

PARTNERAPI_URL=''

PARTNERAPI_RABBITMQ_TIMEOUT=30 # Таймаут RabbitMQ
PARTNERAPI_RABBITMQ_RETRIES_COUNT=3 # Количество повторных попыток при ошибке RabbitMQ, -1 для бесконечного количества попыток
PARTNERAPI_RABBITMQ_RETRIES_SLEEP=30 # Ожидание между попытками

PARTNERAPI_SOURCE_PROJECT_ID=8
PARTNERAPI_KODPOST=116897 # Код поставщика, под которым зведена сеть Партнера

PARTNERAPI_METRICS_PORT= # Порт внутри контейнера для снятия метрик
```

На порту 8000 находится API сервиса.


## API Версия 2

### Метод POST `/v2/orders/`

Создает заказ.

На вход передается json

```json lines
{
  "order_id": 10,
  "date": "2024-06-20T03:14:44.615Z",
  "client": {
    "name": "Test",
    "phone": "79997772211",
    "email": "example@example.com"
  },
  "their_pharmacy_id": "1086",
  "order_type": 2,
  "items": [
    {
      "their_id": "58",
      "price": 10,
      "count": 10
    },
    {
      "their_id": "21737",
      "price": 10,
      "count": 12
    }
  ],
  "comment": "",
  "extra": {
  }
}

```

Структура ответа (общая ошибка на стороне сервиса связи с партнером):

```json lines
{
  "result": "error",
  "data": {
    "partner_error": true,
    "service_error": null,
    "quantity_errors": null,
    "price_errors": null
  }
}
```

### Метод GET `/v2/orders/{order_id}`

Получает статус заказа.

order_id: (тип int) идентификатор заказа в нашей системе

their_order_id: (тип str) идентификатор заказа в системе партнера

Ответ:

```json lines
{
  "result": "success",
  "status_id": 3,
  "their_status_id": 2,
  "their_items": null
}
```

### Метод DELETE `/v2/orders/`

Отменяет заказ.

На вход передается json

```json lines
{
  "order_id": 1,
  "their_order_id": "1"
}
```
Ответ
```json lines
{
  "result": "success"
}

```
