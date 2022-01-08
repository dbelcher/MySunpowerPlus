import signal
import sys
import time

from my_sunpower_plus.app import MySunpowerPlus
from my_sunpower_plus.logger import get_logger

logger = get_logger()

if __name__ == '__main__':
    app = MySunpowerPlus()


    def shutdown(sig, frame):
        app.stop()
        sys.exit(0)


    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    app.start(True)
    while True:
        time.sleep(1)
