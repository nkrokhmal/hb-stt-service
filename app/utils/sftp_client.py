import pysftp
from io import BytesIO


class SftpClient(object):
    def __init__(self, config=None):
        if config is not None:
            self.init_app(config)
        else:
            self.sftp_client = None
            self.upload_path = None
            self.download_path = None
            self.host = None

    def init_app(self, config):
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        self.host = config.SFTP_HOST
        self.sftp_client = pysftp.Connection(
            host=config.SFTP_HOST,
            username=config.SFTP_USERNAME,
            password=config.SFTP_PASSWORD,
            cnopts=cnopts)
        self.upload_path = config.SFTP_BASE_PATH
        self.download_path = config.SFTP_DOWNLOAD_PATH

    def download_file(self, remote_path):
        file = BytesIO()
        self.sftp_client.getfo(self.upload_path + remote_path, file)
        file.seek(0)
        return file

    def download_file_local(self, local_path, remote_path):
        print('Downloading from {}'.format(self.upload_path + remote_path))
        self.sftp_client.get(self.upload_path + remote_path, localpath=local_path)