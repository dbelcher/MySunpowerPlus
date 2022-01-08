from my_sunpower_plus.logger import get_logger


class PVS6Configuration:
    def __init__(self, config: dict) -> None:
        self.config = config or {}
        self.logger = get_logger()

    @property
    def get_host(self) -> str:
        return self.config.get('HOST', '172.27.153.1')

    @property
    def get_url(self) -> str:
        return self.config.get('URL', '/cgi-bin/dl_cgi')

    @property
    def get_ssl(self) -> bool:
        return self.config.get('SSL', False)
