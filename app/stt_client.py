#!/usr/bin/env python3
from vosk import Model, KaldiRecognizer, SetLogLevel
import os
import wave
import json
from .utils.psql_client import PostgresClient
from .utils.sftp_client import SftpClient
from datetime import datetime


class SpeechToTextClient:
    """
    Service that upload speech to text model and recognize audio
    """
    def __init__(self, config=None):
        if config is not None:
            self.init_app(config)
        else:
            self.stt_recognizer = None
            self.config = None
            self.sftp_client = None

    def recognize(self, body):
        remote_file_path = body
        try:
            dialogue_id = (remote_file_path.split('/')[1]).split('.')[0]
            print('Dialogue id is {}'.format(dialogue_id))
            local_file_path = os.path.join(self.sftp_client.download_path, remote_file_path.split('/')[1])
            self.sftp_client.download_file_local(local_file_path, remote_file_path)
        except Exception as e:
            print('Exception occured, wrong filename format {}'.format(remote_file_path))
            exit(1)

        recognition_result = []
        if self.stt_recognizer is not None:
            try:
                wf = wave.open(local_file_path, "rb")
                if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                    print("Audio file must be WAV format mono PCM.")
                    exit(1)

                while True:
                    data = wf.readframes(8000)
                    if len(data) == 0:
                        break
                    if self.stt_recognizer.AcceptWaveform(data):
                        recognition_chunk = json.loads(self.stt_recognizer.Result())
                        if 'result' in recognition_chunk.keys():
                            recognition_result.append(recognition_chunk['result'])
                    else:
                        recognition_chunk = json.loads(self.stt_recognizer.PartialResult())
                        if 'result' in recognition_chunk.keys():
                            recognition_result.append(recognition_chunk['result'])
                print("Recognition result {}".format(json.dumps(recognition_result)))
                for phrase in recognition_result:
                    for word in phrase:
                        word['word'] = word['word'].replace("'", ' ')

                recognition_result = self.process_sttresult(recognition_result)
                # print('Result is {}'.format(json.dumps(recognition_result)))

                psql_client = PostgresClient()
                psql_client.init_app(config=self.config)
                psql_client.update_stt_result(result=json.dumps(recognition_result, ensure_ascii=False), dialogue_id=dialogue_id)

                print('Deleting local path {}'.format(local_file_path))
                os.remove(local_file_path)
                print('Function finished, result of recognition {}'.format(recognition_result))
            except Exception as e:
                try:
                    psql_client = PostgresClient()
                    psql_client.init_app(config=self.config)
                    cur_time = datetime.utcnow()
                    creation_time = psql_client.get_creation_time(dialogue_id=dialogue_id)
                    if (cur_time - creation_time).total_seconds() / 3600 > 3.:
                        psql_client.update_error_status(dialogue_id)
                    print('Exception occured {}, recognition longs to musch period of time'.format(e))
                except:
                    exit(1)
        else:
            print('Please, init stt recognizer')

    def process_sttresult(self, stt_result):
        result = []
        for phrase in stt_result:
            for word in phrase:
                word_format = {}
                word_format['Word'] = word['word']
                word_format['Time'] = word['start']
                word_format['Duration'] = word['end'] - word['start']
                result.append(word_format)
        return result

    def init_app(self, config):
        SetLogLevel(0)
        model_path = config.MODEL_PATH
        rate = int(config.RATE)
        if not os.path.exists(model_path):
            print("Error in model path. Such directory does not exist!")
            exit(1)
        model = Model(model_path)
        self.stt_recognizer = KaldiRecognizer(model, rate)

        # self.psql_client = PostgresClient()
        # self.psql_client.init_app(config=config)

        self.sftp_client = SftpClient()
        self.sftp_client.init_app(config=config)

        self.config = config

