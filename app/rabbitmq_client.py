import pika

class RabbitMQClient:
    def __init__(self, config=None):
        if config is not None:
            self.init_app(config)
        else:
            self.channel_name = None
            self.channel = None

    def init_app(self, config):
        host = config.RABBITMQ_HOST
        vhost = config.RABBITMQ_VHOST
        username = config.RABBITMQ_USERNAME
        password = config.RABBITMQ_PASSWORD
        port = config.RABBITMQ_PORT
        self.channel_name = config.RABBITMQ_QUEUE_NAME

        credentials = pika.PlainCredentials(username=username, password=password)
        rabbitmq_params = pika.ConnectionParameters(host=host, virtual_host=vhost, port=port,
                                                    credentials=credentials
                                                    )
        connection = pika.BlockingConnection(parameters=rabbitmq_params)
        self.channel = connection.channel()
        self.channel.queue_declare(queue=self.channel_name)

    def set_channel_callback(self, callback):
        self.channel.basic_consume(
            queue=self.channel_name, on_message_callback=callback, auto_ack=True)

    def start_consuming(self):
        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()





