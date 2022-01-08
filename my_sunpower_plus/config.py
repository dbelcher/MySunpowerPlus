from my_sunpower_plus.logger import get_logger
from my_sunpower_plus.pvs6.config import PVS6Configuration


class Configuration:
    def __init__(self, config: dict) -> None:
        self.config = config or {}
        self.logger = get_logger()

    @property
    def interval(self) -> int:
        # Interval in seconds.
        return self.config.get('INTERVAL', 300)

    @property
    def pvs6(self) -> PVS6Configuration:
        return PVS6Configuration(self.config.get('PVS6', {}))
