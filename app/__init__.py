from config import config
from .rabbitmq_client import  RabbitMQClient
from .stt_client import SpeechToTextClient
from . import rabbitmq_client, stt_client


rabbitmq_client = RabbitMQClient()
stt_client = SpeechToTextClient()


def create_app(config_name):
    my_config = config[config_name]
    print(my_config.RABBITMQ_HOST)
    print(my_config.RABBITMQ_PASSWORD)
    print(my_config.RABBITMQ_VHOST)
    print(my_config.RABBITMQ_PORT)
    print(my_config.RABBITMQ_QUEUE_NAME)

    # init stt client
    stt_client.init_app(my_config)

    # init rabbitmq client
    rabbitmq_client.init_app(my_config)
    rabbitmq_client.set_channel_callback(stt_client.recognize)

    return rabbitmq_client
