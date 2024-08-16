'''Модуль метрик для лоадера.'''
import prometheus_client

orders_created_counter = prometheus_client.Counter(
    'orders_created_counter',
    'How many orders was created',
    ['service']
)

orders_creating_errors_counter = prometheus_client.Counter(
    'orders_creating_errors_counter',
    'How many errors raised while creating order',
    ['service']
)

order_changing_status_counter = prometheus_client.Counter(
    'order_changing_status_counter',
    'How many times status of order was changed including service',
    ['service']
)

order_status_mapping_error = prometheus_client.Counter(
    'order_status_mapping_error',
    'How many errors raised while mapping order status',
    ['service']
)
