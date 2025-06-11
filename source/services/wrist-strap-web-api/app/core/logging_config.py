# File: app/core/logging_config.py

import logging
import colorlog
from datetime import datetime, timezone, timedelta

# Define the local timezone (GMT+7 for Vietnam)
LOCAL_TIMEZONE = timezone(timedelta(hours=7))


class TimezoneFormatter(colorlog.ColoredFormatter):
    """Custom logging formatter to apply colors and convert timestamps to a local timezone."""

    def converter(self, timestamp):
        dt_utc = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return dt_utc.astimezone(LOCAL_TIMEZONE)

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            s = dt.isoformat(timespec='milliseconds')
        return s


def setup_logging():
    """
    Configures the root logger for the application using colorlog.
    """
    # --- UPDATED: Moved '%(log_color)s' to the front to color the entire line ---
    log_format = "%(log_color)s[%(asctime)s] [%(levelname)-8s] [%(name)s] - %(message)s"
    date_format = "%d-%m-%Y %H:%M:%S"

    formatter = TimezoneFormatter(
        log_format,
        datefmt=date_format,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'white',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        },
        secondary_log_colors={},
        style='%'
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    handler = colorlog.StreamHandler()
    handler.setFormatter(formatter)

    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    root_logger.addHandler(handler)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    logging.info("Colorized logging configured with GMT+7 timezone.")