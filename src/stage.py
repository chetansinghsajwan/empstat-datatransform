import os
import pandas as pd
from .logger import create_logger


class Options:
    input_dir = "out/input"
    stage_dir = "out/stage"


options = Options()

logger = create_logger("stage")


def load_users(input_file_path, stage_file_path):

    df = pd.read_csv(input_file_path)

    # Select the relevant columns
    df = df.filter(
        items=[
            "id",
            "email",
            "first_name",
            "middle_name",
            "last_name",
            "role",
            "createdAt",
            "updatedAt",
        ]
    )

    # Rename headers to snake_case
    df.rename(
        columns={
            "userId": "user_id",
            "firstName": "first_name",
            "middleName": "middle_name",
            "lastName": "last_name",
            "createdAt": "created_at",
            "updatedAt": "updated_at",
        },
        inplace=True,
    )

    df.to_csv(stage_file_path, index=False)


def load_subjects(input_file_path, stage_file_path):

    df = pd.read_csv(input_file_path)

    # Select the relevant columns
    df = df.filter(
        items=[
            "id",
            "name",
            "minMarks",
            "maxMarks",
            "totalTime",
            "createdBy",
            "createdAt",
            "updatedAt",
        ]
    )

    # Rename headers to snake_case
    df.rename(
        columns={
            "minMarks": "min_marks",
            "maxMarks": "max_marks",
            "totalTime": "total_time",
            "createdBy": "created_by",
            "createdAt": "created_at",
            "updatedAt": "updated_at",
        },
        inplace=True,
    )

    df.to_csv(stage_file_path, index=False)


def load_trainings(input_file_path, stage_file_path):

    df = pd.read_csv(input_file_path)

    # Select the relevant columns
    df = df.filter(
        items=[
            "id",
            "name",
            "mode",
            "subjectId",
            "startedAt",
            "endedAt",
            "createdAt",
            "updatedAt",
        ]
    )

    # Rename headers to snake_case
    df.rename(
        columns={
            "subjectId": "subject_id",
            "startedAt": "started_at",
            "endedAt": "ended_at",
            "createdAt": "created_at",
            "updatedAt": "updated_at",
        },
        inplace=True,
    )

    df.to_csv(stage_file_path, index=False)


def load_assessments(input_file_path, stage_file_path):

    df = pd.read_csv(input_file_path)

    # Select the relevant columns
    df = df.filter(items=["userId", "trainingId", "marks", "internetAllowed"])

    # Rename headers to snake_case
    df.rename(
        columns={
            "userId": "user_id",
            "trainingId": "training_id",
            "internetAllowed": "internet_allowed",
        },
        inplace=True,
    )

    df.to_csv(stage_file_path, index=False)


def run():

    # create stage dir if does not exist already
    os.makedirs(options.stage_dir, exist_ok=True)

    # loading users
    logger.info("loading users...")
    input_users_path = os.path.join(options.input_dir, "users.csv")
    stage_users_path = os.path.join(options.stage_dir, "users.csv")
    try:
        load_users(input_users_path, stage_users_path)
    except Exception as ex:
        logger.info(f"loading users failed, error: {ex}.")
        raise ex

    logger.info("loading users done.")

    # loading subjects
    logger.info("loading subjects...")
    input_subjects_path = os.path.join(options.input_dir, "subjects.csv")
    stage_subjects_path = os.path.join(options.stage_dir, "subjects.csv")
    try:
        load_subjects(input_subjects_path, stage_subjects_path)
    except Exception as ex:
        logger.info(f"loading subjects failed, error: {ex}.")
        raise ex

    logger.info("loading subjects done.")

    # loading trainings
    logger.info("loading trainings...")
    input_trainings_path = os.path.join(options.input_dir, "trainings.csv")
    stage_trainings_path = os.path.join(options.stage_dir, "trainings.csv")
    try:
        load_trainings(input_trainings_path, stage_trainings_path)
    except Exception as ex:
        logger.info(f"loading trainings failed, error: {ex}.")

    logger.info("loading trainings done.")

    # loading assessments
    logger.info("loading assessments...")
    input_assessments_path = os.path.join(options.input_dir, "assessments.csv")
    stage_assessments_path = os.path.join(options.stage_dir, "assessments.csv")
    try:
        load_assessments(input_assessments_path, stage_assessments_path)
    except Exception as ex:
        logger.info(f"loading assessments failed, error: {ex}.")

    logger.info("loading assessments done.")


if __name__ == "__main__":
    run()
