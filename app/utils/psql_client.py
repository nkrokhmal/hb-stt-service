import psycopg2
from tenacity import retry, wait_exponential, stop_after_attempt
from typing import Callable


def reconnect(f: Callable):
    def wrapper(client, *args, **kwargs):
        if not client.connected():
            client.connect()
        try:
            return f(client, *args, **kwargs)
        except psycopg2.Error as e:
            print('Reconnect exception occured {}'.format(e))
            client.close()
            raise
    return wrapper


class PostgresClient:

    def __init__(self, config=None):
        if config is not None:
            self.init_app(config)
        else:
            self.client = None
            self._dbname = None
            self._username = None
            self._password = None
            self._host = None

    def init_app(self, config):
        self._dbname = config.PSQL_DB
        self._username = config.PSQL_USERNAME
        self._password = config.PSQL_PASSWORD
        self._host = config.PSQL_HOST
        self.client = psycopg2.connect(dbname=self._dbname,
                                       user=self._username,
                                       password=self._password,
                                       host=self._host)

        print('Connection established {}'.format(self.connected()))

    def connected(self) -> bool:
        return self.client and self.client.closed == 0

    def close(self):
        if self.connected():
            try:
                self.client.close()
            except Exception as e:
                print('Exception occured while closing connection {}'.format(e))
                pass
        self.client = None

    def connect(self):
        self.close()
        self.client = psycopg2.connect(dbname=self._dbname,
                                       user=self._username,
                                       password=self._password,
                                       host=self._host)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def update_error_status(self, dialogue_id):
        if self.client is not None:
            cur = self.client.cursor()
            req = 'UPDATE "{}" SET  "StatusId" = 8 WHERE "DialogueId" = \'{}\'' \
                .format('FileAudioDialogues', dialogue_id)
            cur.execute(req)
            self.client.commit()
            cur.close()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(max=10))
    @reconnect
    def update_stt_result(self, result, dialogue_id):
        if self.client is not None:
            cur = self.client.cursor()
            req = 'UPDATE "{}" SET  "StatusId" = 7, "STTResult" = \'{}\' WHERE "DialogueId" = \'{}\' and "StatusId" = 6'\
                .format('FileAudioDialogues', result, dialogue_id)
            cur.execute(req)
            self.client.commit()
            cur.close()