logger_config = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'file_format': {
            'format': '{asctime} - {levelname} - {name} - {module}:{funcName}:{lineno}- {message}',
            'style': '{'
        }
    },
    'handlers': {
        'file_handler': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'file_format',
            'filename': 'error.log'
        }
    },
    'loggers': {
        'app_logger': {
            'level': 'DEBUG',
            'handlers': ['file_handler']
            # 'propagate': False
        }
    }

    # 'filters': {},
    # 'root': {}   # '': {}
    # 'incremental': True
}