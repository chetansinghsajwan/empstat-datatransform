from datetime import datetime
from .logger import create_logger
import pandas as pd
import os
import re


# options to configure preparation stage
class Options:
    stage_folder = "out/stage"
    output_folder = "out/prep"


options = Options()

logger = create_logger("prep")


# Read the CSV files into pandas DataFrames
def load_stage_outputs():

    users_path = os.path.join(options.stage_folder, "users.csv")
    subjects_path = os.path.join(options.stage_folder, "subjects.csv")
    trainings_path = os.path.join(options.stage_folder, "trainings.csv")
    assessments_path = os.path.join(options.stage_folder, "assessments.csv")

    users = pd.read_csv(users_path)
    subjects = pd.read_csv(subjects_path)
    trainings = pd.read_csv(trainings_path)
    assessments = pd.read_csv(assessments_path)

    return users, subjects, trainings, assessments


# Validate and clean user records
def clean_users(users):
    cleaned_users = []
    for _, row in users.iterrows():
        # Trim spaces
        row = row.apply(lambda x: x.strip() if isinstance(x, str) else x)

        # Check for null or empty values
        if any(
            pd.isnull(
                row[
                    [
                        "id",
                        "email",
                        "first_name",
                        "middle_name",
                        "last_name",
                        "role",
                        "created_at",
                        "updated_at",
                    ]
                ]
            )
        ) or any(
            row[["id", "email", "first_name", "middle_name", "last_name", "role"]] == ""
        ):
            logger.debug(f"discarded user due to null or empty values: {row['id']}")
            continue

        # Clean user.id
        user_id = row["id"]
        if not validate_id(user_id):
            logger.debug(f"discarded user due to invalid id: {user_id}")
            continue
        prep_user = {"id": user_id.lower()}

        # Clean user.email
        email = row["email"]
        if not validate_email(email):
            logger.debug(f"discarded user due to invalid email: {user_id}")
            continue
        prep_user["email"] = email

        # Clean first_name, middle_name, last_name
        prep_user["first_name"] = row["first_name"].lower()
        prep_user["middle_name"] = row["middle_name"].lower()
        prep_user["last_name"] = row["last_name"].lower()

        # Clean role
        role = row["role"].lower()
        if role not in ["admin", "employee"]:
            logger.debug(f"discarded user due to invalid role: {user_id}")
            continue
        prep_user["role"] = role

        # Validate created_at and updated_at
        created_at = row["created_at"]
        updated_at = row["updated_at"]
        if not validate_datetime(created_at):
            logger.debug(f"discarded user due to invalid created_at: {user_id}")
            continue
        prep_user["created_at"] = created_at
        if not validate_datetime(updated_at) or updated_at <= created_at:
            logger.debug(f"discarded user due to invalid updated_at: {user_id}")
            continue
        prep_user["updated_at"] = updated_at

        cleaned_users.append(prep_user)

    return pd.DataFrame(cleaned_users)


# Validate and clean subject records
def clean_subjects(subjects):
    cleaned_subjects = []
    for _, row in subjects.iterrows():
        # Trim spaces
        row = row.apply(lambda x: x.strip() if isinstance(x, str) else x)

        # Check for null or empty values
        if any(
            pd.isnull(
                row[
                    [
                        "id",
                        "name",
                        "min_marks",
                        "max_marks",
                        "total_time",
                        "created_at",
                        "updated_at",
                    ]
                ]
            )
        ) or any(row[["id", "name"]] == ""):
            logger.debug(f"discarded subject due to null or empty values: {row["id"]}")
            continue

        # Clean id
        subject_id = row["id"]
        if not validate_id(subject_id):
            logger.debug(f"discarded subject due to invalid id: {subject_id}")
            continue

        # Clean name
        name = row["name"]
        if not re.match(
            r"^[A-Za-z\s]+$", name
        ):  # name should not contain symbols or numbers
            logger.debug(f"discarded subject due to invalid name: {subject_id}")
            continue

        # Clean min_marks, max_marks, total_time
        min_marks = row["min_marks"]
        max_marks = row["max_marks"]
        total_time = row["total_time"]
        if min_marks < 0 or max_marks < min_marks or total_time < 0:
            logger.debug(
                f"discarded subject due to invalid marks or total_time: {subject_id}"
            )
            continue

        # Validate created_at and updated_at
        created_at = row["created_at"]
        updated_at = row["updated_at"]
        if not validate_datetime(created_at):
            logger.debug(f"discarded subject due to invalid created_at: {subject_id}")
            continue
        if not validate_datetime(updated_at) or updated_at <= created_at:
            logger.debug(f"discarded subject due to invalid updated_at: {subject_id}")
            continue

        cleaned_subjects.append(
            {
                "id": subject_id.lower(),
                "name": name.strip(),
                "min_marks": min_marks,
                "max_marks": max_marks,
                "total_time": total_time,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )

    return pd.DataFrame(cleaned_subjects)


# Validate and clean training records
def clean_trainings(trainings, valid_subject_ids):
    cleaned_trainings = []
    for _, row in trainings.iterrows():
        # Trim spaces
        row = row.apply(lambda x: x.strip() if isinstance(x, str) else x)

        # Check for null or empty values
        if any(
            pd.isnull(
                row[
                    [
                        "id",
                        "name",
                        "mode",
                        "subject_id",
                        "started_at",
                        "ended_at",
                        "created_at",
                        "updated_at",
                    ]
                ]
            )
        ) or any(row[["id", "name", "mode", "subject_id"]] == ""):
            logger.debug(f"discarded training due to null or empty values: {row["id"]}")
            continue

        # Clean id
        training_id = row["id"]
        if not validate_id(training_id):
            logger.debug(f"discarded training due to invalid id: {training_id}")
            continue

        # Clean name
        name = row["name"]
        if not re.match(
            r"^[A-Za-z\s]+$", name
        ):  # name should not contain symbols or numbers
            logger.debug(f"discarded training due to invalid name: {training_id}")
            continue

        # Clean mode
        mode = row["mode"].lower()
        if mode not in ["online", "offline", "onsite"]:
            logger.debug(f"discarded training due to invalid mode: {training_id}")
            continue

        # Clean subject_id
        subject_id = row["subject_id"]
        if subject_id not in valid_subject_ids:
            logger.debug(f"discarded training due to invalid subject_id: {training_id}")
            continue

        # Validate started_at and ended_at
        started_at = row["started_at"]
        ended_at = row["ended_at"]
        if not validate_datetime(started_at):
            logger.debug(f"discarded training due to invalid started_at: {training_id}")
            continue
        if ended_at and ended_at <= started_at:
            logger.debug(f"discarded training due to invalid ended_at: {training_id}")
            continue

        # Validate created_at and updated_at
        created_at = row["created_at"]
        updated_at = row["updated_at"]
        if not validate_datetime(created_at):
            logger.debug(f"discarded training due to invalid created_at: {training_id}")
            continue
        if not validate_datetime(updated_at) or updated_at <= created_at:
            logger.debug(f"discarded training due to invalid updated_at: {training_id}")
            continue

        cleaned_trainings.append(
            {
                "id": training_id.lower(),
                "name": name.strip(),
                "mode": mode,
                "subject_id": subject_id,
                "started_at": started_at,
                "ended_at": ended_at,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )

    return pd.DataFrame(cleaned_trainings)


# Validate and clean assessment records
def clean_assessments(
    assessments,
    valid_user_ids,
    valid_training_ids,
    subject_max_marks,
    training_subject_map,
):
    cleaned_assessments = []
    for _, row in assessments.iterrows():
        # Trim spaces
        row = row.apply(lambda x: x.strip() if isinstance(x, str) else x)

        # Check for null or empty values
        if any(
            pd.isnull(row[["user_id", "training_id", "marks", "internet_allowed"]])
        ) or any(row[["user_id", "training_id", "marks", "internet_allowed"]] == ""):
            logger.debug(
                f"discarded assessment due to null or empty values: {row['user_id']}"
            )
            continue

        # Clean user_id
        user_id = row["user_id"]
        if user_id not in valid_user_ids:
            logger.debug(f"discarded assessment due to invalid user_id: {user_id}")
            continue

        # Clean training_id
        training_id = row["training_id"]
        if training_id not in valid_training_ids:
            logger.debug(f"discarded assessment due to invalid training_id: {user_id}")
            continue

        # Map training_id to subject_id
        subject_id = training_subject_map.get(training_id)
        if not subject_id:
            logger.debug(
                f"discarded assessment due to missing subject_id for: {user_id}"
            )
            continue

        # Clean marks
        marks = row["marks"]
        if not (
            isinstance(marks, (int, float))
            and marks >= 0
            and marks < subject_max_marks[subject_id]
        ):
            logger.debug(f"discarded assessment due to invalid marks: {user_id}")
            continue

        # Clean internet_allowed
        internet_allowed = row["internet_allowed"]
        if not isinstance(internet_allowed, bool):
            logger.debug(
                f"discarded assessment due to invalid internet_allowed value: {user_id}"
            )
            continue

        cleaned_assessments.append(
            {
                "user_id": user_id,
                "training_id": training_id,
                "marks": marks,
                "internet_allowed": internet_allowed,
            }
        )
    return pd.DataFrame(cleaned_assessments)


# Helper Functions
def validate_id(value):
    """Validate the ID to ensure it does not contain any symbols or spaces except '-' or '_'."""
    return bool(re.match(r"^[\w-]+$", value))


def validate_email(email):
    """Validate the email format."""
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email))


def validate_datetime(date_string):
    """Validate datetime format."""
    try:
        datetime.fromisoformat(date_string)
        return True
    except ValueError:
        return False


def run():
    stage_users, stage_subjects, stage_trainings, stage_assessments = (
        load_stage_outputs()
    )

    # clean users
    prep_users = clean_users(stage_users)
    user_discard_count = stage_users.size - prep_users.size
    logger.info(
        f"cleaned users, count: {prep_users.size}, discarded: {user_discard_count}"
    )

    # clean subjects
    prep_subjects = clean_subjects(stage_subjects)
    subject_discard_count = stage_subjects.size - prep_subjects.size
    logger.info(
        f"cleaned subjects, count: {prep_subjects.size}, discarded: {subject_discard_count}"
    )

    valid_subject_ids = prep_subjects["id"].tolist()

    # clean trainings
    prep_trainings = clean_trainings(stage_trainings, valid_subject_ids)
    training_discard_count = stage_trainings.size - prep_trainings.size
    logger.info(
        f"cleaned trainings, count: {prep_trainings.size}, discarded: {training_discard_count}"
    )

    valid_user_ids = prep_users["id"].tolist()
    valid_training_ids = prep_trainings["id"].tolist()
    subject_max_marks = prep_subjects.set_index("id")["max_marks"].to_dict()
    training_subject_map = prep_trainings.set_index("id")["subject_id"].to_dict()

    # clean assessments
    prep_assessments = clean_assessments(
        stage_assessments,
        valid_user_ids,
        valid_training_ids,
        subject_max_marks,
        training_subject_map,
    )
    assessment_discard_count = stage_assessments.size - prep_assessments.size
    logger.info(
        f"cleaned assessments, count: {prep_assessments.size}, discarded: {assessment_discard_count}"
    )

    if not os.path.exists(options.output_folder):
        os.makedirs(options.output_folder)

    # csv file paths
    prep_users_path = os.path.join(options.output_folder, "users.csv")
    prep_subjects_path = os.path.join(options.output_folder, "subjects.csv")
    prep_trainings_path = os.path.join(options.output_folder, "trainings.csv")
    prep_assessments_path = os.path.join(options.output_folder, "assessments.csv")

    # save cleaned data to csv files
    prep_users.to_csv(prep_users_path, index=False)
    prep_subjects.to_csv(prep_subjects_path, index=False)
    prep_trainings.to_csv(prep_trainings_path, index=False)
    prep_assessments.to_csv(prep_assessments_path, index=False)

    logger.info("data cleaning completed and saved to output folder.")


if __name__ == "__main__":
    run()
