import psycopg2

class PostgresClient:
    def __init__(self, config=None):
        if config is not None:
            self.init_app(config)
        else:
            self.client = None

    def init_app(self, config):
        dbname = config.PSQL_DB
        username = config.PSQL_USERNAME
        password = config.PSQL_PASSWORD
        host = config.PSQL_HOST
        self.client = psycopg2.connect(dbname=dbname, user=username, password=password, host=host)

    def update_error_status(self, dialogue_id):
        if self.client is not None:
            cur = self.client.cursor()
            req = 'UPDATE "{}" SET  "StatusId" = 8 WHERE "DialogueId" = \'{}\'' \
                .format('FileAudioDialogues', dialogue_id)
            print(req)
            cur.execute(req)
            self.client.commit()
            cur.close()

    def update_stt_result(self, result, dialogue_id):
        if self.client is not None:
            print(type(result))
            cur = self.client.cursor()
            req = 'UPDATE "{}" SET  "StatusId" = 7, "STTResult" = \'{}\' WHERE "DialogueId" = \'{}\' and "StatusId" = 6'\
                .format('FileAudioDialogues', result, dialogue_id)
            print(req)
            cur.execute(req)
            self.client.commit()
            cur.close()