#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging.config

from data_migrator import PACKAGE_NAME

_LOG = logging.getLogger(PACKAGE_NAME)


def default_logger():
    '''returns the default logger for this package'''
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


def configure_logging(config=None):
    '''configure logger

    Args:
        config: if not set defaults to DEFAULT_LOGGING settings
    '''
    if not config:
        config = DEFAULT_LOGGING
    logging.config.dictConfig(config)
    return logging.getLogger(PACKAGE_NAME)
