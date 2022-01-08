import hashlib
from datetime import datetime

from elasticsearch import Elasticsearch, helpers

from my_sunpower_plus.logger import get_logger


class ESClient:
    def __init__(self):
        self.client = Elasticsearch()
        self.logger = get_logger()

    def index_devices(self, devices: list) -> None:
        documents = []
        for device in devices:
            documents.append(
                self._create_device_document(device)
            )
        self._write_documents(documents)

    def _write_documents(self, documents: list) -> None:
        resp = helpers.bulk(self.client, documents, True)
        self.logger.info(resp)

    @staticmethod
    def _create_device_document(device: dict) -> dict:
        data_time = datetime.fromisoformat(device['DATATIME'])
        device_type = device['DEVICE_TYPE']

        # Format id.
        _id = device_type + '-' + device['SERIAL'] + '-' + data_time.isoformat()
        _id = hashlib.sha256(_id.encode('utf-8')).hexdigest()

        # Format index.
        _index = device_type.replace(' ', '-').strip().lower()
        _index += "-" + '{:04d}'.format(data_time.year)
        _index += '-' + '{:02d}'.format(data_time.month)
        _index += '-' + '{:02d}'.format(data_time.day)

        _source = {}
        # Convert keys to lowercase.
        for key in device.keys():
            _source[key.lower()] = device[key]

        return {
            '_id': _id,
            '_index': _index,
            '_source': _source
        }
