#!/usr/bin/python
# -*- coding: UTF-8 -*-

import logging.config

from data_migrator import PACKAGE_NAME

_LOG = logging.getLogger(PACKAGE_NAME)
def default_logger():
    return _LOG

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)-15s %(levelname)s %(message)s',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'default',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        PACKAGE_NAME: {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }
}

def configure_logging(config=DEFAULT_LOGGING):
    logging.config.dictConfig(config)
    return logging.getLogger(PACKAGE_NAME)
