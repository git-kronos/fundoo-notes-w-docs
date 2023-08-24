import logging

from django.conf import settings

log_config = settings.LOG_CONFIG
format = log_config.get("format")
level = log_config.get("level", logging.DEBUG)
datefmt = log_config.get("datefmt")
filename = log_config.get("filename")


def get_logger(
    file=filename,
    level=level,
    format=format,
    datefmt=datefmt,
):
    logging.basicConfig(
        filename=file,
        level=level,
        format=format,
        datefmt=datefmt,
    )
    return logging.getLogger()
