import argparse
import json
import os

from my_sunpower_plus.config import Configuration


def app_path() -> str:
    return os.path.realpath(os.path.join(
        os.path.dirname(os.path.realpath(__file__)), ""
    ))


def load_configuration() -> Configuration:
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config',
                        help='Path to configuration file.')

    args = parser.parse_args()

    # Load configuration file.
    config = {}
    if args.config:
        path = args.config.strip()
        if not os.path.isabs(path):
            path = os.path.normpath(
                os.path.join(app_path(), path)
            )
        if not os.path.exists(path):
            raise IOError(f'Path does not exist: \'{path}\'')
        if not os.path.isfile(path):
            raise IOError(f'Path must reference a file: \'{path}\'')
        with open(path, 'r') as file:
            config = json.load(file)

    return Configuration(config)
