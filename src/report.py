import os
import pandas as pd
from .logger import create_logger
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

prep_folder = "out/prep"
db_url = os.getenv("EMPSTAT_DATABASE_URL")
logger = create_logger("report")


class Source:
    """Class to manage a source CSV file."""

    def __init__(self, file_path):
        self.file_path = file_path

    def load_csv(self):
        """Load the CSV file into a pandas DataFrame."""
        if os.path.exists(self.file_path):
            dataframe = pd.read_csv(self.file_path)
            logger.info(f"Loaded {self.file_path} into DataFrame.")
            return dataframe
        else:
            logger.info(f"File {self.file_path} does not exist.")
            return None


class Destination:
    """Class to manage the PostgreSQL database connection and data insertion."""

    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        self.engine.connect()

    def insert_data(self, dataframe, table_name):
        """Insert DataFrame data into the specified PostgreSQL table."""
        if dataframe is not None and not dataframe.empty:
            dataframe.to_sql(table_name, self.engine, if_exists="append", index=False)
            logger.info(f"Inserted data into {table_name} table.")
        else:
            logger.info(f"No data to insert into {table_name} table.")


def load_source(file_name: str) -> Source:
    file_path = os.path.join(prep_folder, file_name) + ".csv"
    return Source(file_path)


def run():

    # connecting to the database
    logger.info(f"connecting to database '{db_url}'...")
    destination = Destination(db_url)
    logger.info(f"connecting to database done successfully.")

    # loading sources
    logger.info(f"loading datasets from sources...")
    prep_users = load_source("users").load_csv()
    prep_subjects = load_source("subjects").load_csv()
    prep_trainings = load_source("trainings").load_csv()
    prep_assessments = load_source("assessments").load_csv()
    logger.info(f"loading datasets from sources done.")

    # writing to database
    logger.info(f"writing datasets to destination...")
    destination.insert_data(prep_users, "users")
    destination.insert_data(prep_subjects, "subjects")
    destination.insert_data(prep_trainings, "trainings")
    destination.insert_data(prep_assessments, "assessments")
    logger.info(f"writing datasets to destination done.")


if __name__ == "__main__":
    run()
