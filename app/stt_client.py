#!/usr/bin/env python3
from vosk import Model, KaldiRecognizer, SetLogLevel
import os
import wave
import json
from .utils.psql_client import PostgresClient
from .utils.sftp_client import SftpClient


class SpeechToTextClient:
    """
    Service that upload speech to text model and recognize audio
    """
    def __init__(self, config=None):
        if config is not None:
            self.init_app(config)
        else:
            self.stt_recognizer = None

    def recognize(self, ch, method, properties, body):
        remote_file_path = body.decode("utf-8")
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
                    data = wf.readframes(4000)
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
                for phrase in recognition_result:
                    for word in phrase:
                        word['word'] = word['word'].replace("'", ' ')
                self.psql_client.update_stt_result(result=json.dumps(recognition_result), dialogue_id=dialogue_id)
                print('Function finished, result of recognition {}'.format(recognition_result))
            except Exception as e:
                self.psql_client.update_error_status(dialogue_id)
                print('Exception occured {}'.format(e))
                # return recognition_result
        else:
            print('Please, init stt recognizer')

    def init_app(self, config):
        SetLogLevel(0)
        model_path = config.MODEL_PATH
        rate = int(config.RATE)
        if not os.path.exists(model_path):
            print("Error in model path. Such directory does not exist!")
            exit(1)
        model = Model(model_path)
        self.stt_recognizer = KaldiRecognizer(model, rate)

        self.psql_client = PostgresClient()
        self.psql_client.init_app(config=config)

        self.sftp_client = SftpClient()
        self.sftp_client.init_app(config=config)

