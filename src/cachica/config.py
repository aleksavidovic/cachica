import logging
import os
import sys
import json

# Custom JSON Formatter
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "funcName": record.funcName,
            "lineNo": record.lineno,
        }
        # Add exception info if present
        if record.exc_info:
            log_record['exc_info'] = self.formatException(record.exc_info)
        
        # Add extra fields passed to the logger
        if hasattr(record, 'extra_data'):
            log_record.update(record.extra_data)
            
        return json.dumps(log_record)

def get_logging_config(log_level_str: str = "INFO"):
    """
    Returns a dictionary for logging.config.dictConfig.
    Sets log level from LOG_LEVEL env var, defaulting to INFO.
    """
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JsonFormatter,
            },
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "level": "DEBUG", # Let the logger control the level
                "formatter": "json" if os.getenv("LOG_FORMAT") == "json" else "simple",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            "my_app": { # Your app's logger
                "handlers": ["stdout"],
                "level": log_level,
                "propagate": False, # Don't pass logs to the root logger
            },
            # Example for a noisy third-party library
            "uvicorn.access": {
                "handlers": ["stdout"],
                "level": "WARNING",
                "propagate": False,
            },
        },
        "root": { # Catch-all for everything else
            "handlers": ["stdout"],
            "level": log_level,
        },
    }
    return config
