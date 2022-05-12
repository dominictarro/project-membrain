"""
Logging initialization
"""
import logging
import logging.config
import os

import yaml

LOG_ENV = 'LOGGING_CONFIGURATION'
log_file = os.getenv(LOG_ENV)
if log_file is None:
    print(f"Environment variable '{LOG_ENV}' does not exist")
    exit(1)

try:
    with open(log_file, 'r') as fo:
        cfg: dict = yaml.safe_load(fo)
except OSError as e:
    # TODO something
    ...
    exit(1)

logging.config.dictConfig(cfg)
