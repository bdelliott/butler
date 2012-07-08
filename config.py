import logging
import logging.config

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s: %(message)s '
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {},
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'butler': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        }
    }
}
def setup_logging():
    logging.config.dictConfig(LOGGING)
