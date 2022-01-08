import json
import re
from datetime import datetime

import urllib3

from my_sunpower_plus.errors import SerializationError, ValidationError
from my_sunpower_plus.logger import get_logger
from my_sunpower_plus.pvs6.config import PVS6Configuration

client = urllib3.PoolManager()

DATETIME_REGEX = re.compile(
    '(?P<year>\\d{4}),(?P<month>\\d{2}),(?P<day>\\d{2}),'
    '(?P<hour>\\d{2}),(?P<minute>\\d{2}),(?P<second>\\d{2})'
)


class PVS6Client:
    def __init__(self, config: PVS6Configuration):
        self.config = config
        self.logger = get_logger()

    def get_device_list(self) -> list:
        http = 'http' if not self.config.get_ssl else 'https'
        host = self.config.get_host.strip('/')
        url = self.config.get_url.strip('/')

        full_url = f'{http}://{host}/{url}?Command=DeviceList'
        self.logger.info(f'GET {full_url}')
        resp = client.request('GET', full_url)
        self.logger.info(f'RESPONSE {resp.status} -> {resp.data}')

        if resp.status != 200:
            raise IOError(f'PVS6 Response Failure')

        body = json.loads(
            resp.data.decode('utf-8')
        )

        devices = []
        for device in body['devices']:
            try:
                self.validate_device(device)
                devices.append(device)
            except:
                self.logger.exception('Skipping invalid device.')

        return devices

    @staticmethod
    def validate_device(device: dict) -> None:
        if not device:
            raise ValidationError('Device is not defined!')

        keys = device.keys()
        for key in keys:
            value = device[key]

            match key:
                case 'CURTIME' | 'DATATIME':
                    try:
                        device[key] = PVS6Client.reformat_datetime(value)
                    except:
                        raise ValidationError(f'Invalid value \'{value}\' for \'{key}\'. Expected datetime.')

                case 't_htsnk_degc' | 'dl_uptime' | 'dl_comm_err' | 'dl_mem_used' | 'dl_err_count' | \
                     'dl_scan_time' | 'dl_flash_avail' | 'dl_skipped_scans' | 'dl_untransmitted' | \
                     'ct_scl_fctr':
                    try:
                        device[key] = int(value)
                    except:
                        raise ValidationError(f'Invalid value \'{value}\' for \'{key}\'. Expected int.')

                case 'freq_hz' | 'v_mppt1_v' | 'i_mppt1_a' | 'i_3phsum_a' | 'p_mppt1_kw' | \
                     'p_3phsum_kw' | 'vln_3phavg_v' | 'ltea_3phsum_kwh' | 'dl_cpu_load' | \
                     'tot_pf_rto' | 's_3phsum_kva' | 'q_3phsum_kvar' | 'i1_a' | 'i2_a' | \
                     'v1n_v' | 'v2n_v' | 'v12_v' | 'p1_kw' | 'p2_kw' | 'neg_ltea_3phsum_kwh' | \
                     'pos_ltea_3phsum_kwh' | 'net_ltea_3phsum_kwh':
                    try:
                        device[key] = float(value)
                    except:
                        raise ValidationError(f'Invalid value \'{value}\' for \'{key}\'. Expected float.')

                case _:
                    pass

    @staticmethod
    def reformat_datetime(value: str) -> str:
        match = DATETIME_REGEX.match(value)
        if not match:
            raise SerializationError(f'Invalid date/time value \'{value}\'')

        utc_timestamp = float(datetime(
            int(match.group('year')), int(match.group('month')), int(match.group('day')),
            int(match.group('hour')), int(match.group('minute')), int(match.group('second')),
            tzinfo=datetime.utcnow().astimezone().tzinfo
        ).strftime('%s'))
        return datetime.fromtimestamp(utc_timestamp).isoformat()
