from threading import Timer

from my_sunpower_plus.es.client import ESClient
from my_sunpower_plus.loader import load_configuration
from my_sunpower_plus.logger import get_logger
from my_sunpower_plus.pvs6.client import PVS6Client


class MySunpowerPlus:
    def __init__(self) -> None:
        self.config = load_configuration()
        self.logger = get_logger()

        self.pvs_client = PVS6Client(self.config.pvs6)
        self.es_client = ESClient()

        self._timer = None
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    def start(self, skip_delay=False) -> None:
        if not self.is_running:
            delay = 0 if skip_delay else self.config.interval
            self._timer = Timer(delay, self._run)
            self._timer.start()
            self._running = True

    def stop(self) -> None:
        self._timer.cancel()
        self._running = False

    def _run(self) -> None:
        self._running = False
        self.start()

        # Poll device information.
        devices = self.pvs_client.get_device_list()
        self.es_client.index_devices(devices)
