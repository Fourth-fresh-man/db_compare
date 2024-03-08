from typing import Callable

import yaml

RED: Callable[[str], str] = lambda text: f"\u001b[31m{text}\033\u001b[0m"
GREEN: Callable[[str], str] = lambda text: f"\u001b[32m{text}\033\u001b[0m"
WARNING: Callable[[str], str] = lambda text: f"\u001b[33m{text}\033\u001b[0m"


def load_url_config():
    with open('config.yml', 'r') as file:
        config = yaml.safe_load(file)

    old_database_config = config['database']['old_datasource']
    new_database_config = config['database']['new_datasource']
    ignore_column_list = config['database']['ignoreColumn']

    old_url = f"mysql+pymysql://{old_database_config['username']}:{old_database_config['password']}@{old_database_config['host']}:{old_database_config['port']}/{old_database_config['database']}"
    new_url = f"mysql+pymysql://{new_database_config['username']}:{new_database_config['password']}@{new_database_config['host']}:{new_database_config['port']}/{new_database_config['database']}"

    return old_url, new_url, ignore_column_list
