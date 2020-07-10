from config import config
from .rabbitmq_client import  RabbitMQClient
from .stt_client import SpeechToTextClient
from . import rabbitmq_client, stt_client


rabbitmq_client = RabbitMQClient()
stt_client = SpeechToTextClient()


def create_app(config_name):
    my_config = config[config_name]

    # init stt client
    stt_client.init_app(my_config)

    # init rabbitmq client
    rabbitmq_client.init_app(my_config, stt_client.recognize)

    return rabbitmq_client
