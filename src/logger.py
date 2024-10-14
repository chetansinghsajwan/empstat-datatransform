import logging
import sys


def create_logger(name):
    """Set up a logger with the specified name."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create a console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)

    # Create a formatter and set it for the handler
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(console)

    return logger
