import os


class Config:
    RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST')
    RABBITMQ_VHOST = os.environ.get('RABBITMQ_VHOST')
    RABBITMQ_USERNAME = os.environ.get('RABBITMQ_USERNAME')
    RABBITMQ_PASSWORD = os.environ.get('RABBITMQ_PASSWORD')
    RABBITMQ_PORT = os.environ.get('RABBITMQ_PORT')
    RABBITMQ_QUEUE_NAME = os.environ.get('RABBITMQ_QUEUE_NAME')
    MODEL_PATH = os.environ.get('MODEL_PATH') or 'model'
    SFTP_HOST = os.environ.get('SFTP_HOST')
    SFTP_USERNAME = os.environ.get('SFTP_USERNAME')
    SFTP_PASSWORD = os.environ.get('SFTP_PASSWORD')
    SFTP_BASE_PATH = os.environ.get('SFTP_BASE_PATH')
    SFTP_DOWNLOAD_PATH = os.environ.get('SFTP_DOWNLOAD_PATH')
    PSQL_DB = os.environ.get('PSQL_DB')
    PSQL_USERNAME = os.environ.get('PSQL_USERNAME')
    PSQL_PASSWORD = os.environ.get('PSQL_PASSWORD')
    PSQL_HOST = os.environ.get('PSQL_HOST')
    RATE = os.environ.get('RATE') or '16000'


class Production(Config):
    TYPE = 'PRODUCTION'


class Debug(Production):
    TYPE = 'Production'


config = {
    'production': Production,
    'debug': Debug
}
