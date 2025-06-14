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
    log_format = "%(log_color)s[%(asctime)s] [%(levelname)-8s] [%(name)s] - %(message)s%(reset)s"  # Added %(reset)s at the end
    date_format = "%d-%m-%Y %H:%M:%S"

    formatter = TimezoneFormatter(
        log_format,
        datefmt=date_format,
        reset=True,
        log_colors={
            'DEBUG': 'white',
            'INFO': 'white',  # Set INFO to white as well
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        },
        secondary_log_colors={},
        style='%'
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Keep root at DEBUG to capture all levels

    # CRITICAL: Ensure existing handlers are cleared, especially important for reloaders
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Add the new stream handler with the custom formatter
    stream_handler = colorlog.StreamHandler()  # Use colorlog.StreamHandler directly
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    # --- Silence verbose third-party loggers if not actively debugging them ---
    # Uvicorn's access logs (HTTP requests)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)  # Changed to INFO to see common requests, but not DEBUG

    # Uvicorn's general logger
    logging.getLogger("uvicorn").setLevel(logging.INFO)  # Set Uvicorn to INFO to reduce noise

    # PyMongo's loggers can be very verbose at DEBUG level
    logging.getLogger("pymongo.connection").setLevel(logging.INFO)
    logging.getLogger("pymongo.topology").setLevel(logging.INFO)
    logging.getLogger("pymongo.serverSelection").setLevel(logging.INFO)
    logging.getLogger("pymongo.command").setLevel(logging.INFO)

    logger = logging.getLogger(__name__)
    logger.info("Colorized logging configured with GMT+7 timezone and DEBUG level.")