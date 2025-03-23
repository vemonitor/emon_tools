"""
Module for creating initial data in the database.

This module sets up logging, initializes the database using the
`init_db` function, and provides a main function to run the
initialization.
"""
import logging
from sqlmodel import Session
from backend.core.db import init_db
from backend.core.database import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    """
    Initialize the database.

    This function creates a database session and calls the `init_db`
    function to set up the initial database schema and data.
    """
    with Session(engine) as session:
        init_db(session)


def main() -> None:
    """
    Create initial data for the database.

    This function logs the start of the data creation process, calls the
    `init` function to perform the database initialization, and then logs
    the completion of the data creation process.
    """
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
