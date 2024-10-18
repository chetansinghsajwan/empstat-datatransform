import pandas as pd
import os
from .logger import create_logger

logger = create_logger("report")


class Options:
    prep_dir = "out/prep"
    report_dir = "out/report"


options = Options()


def generate_report(users, subjects, trainings, assessments):
    """Generate the performance report by merging users, subjects, trainings, and assessments."""

    # Merge assessments with trainings on 'training_id'
    assessments_trainings = pd.merge(
        assessments, trainings, left_on="training_id", right_on="id", how="left"
    )

    # Merge the above result with subjects on 'subject_id'
    assessments_trainings_subjects = pd.merge(
        assessments_trainings, subjects, left_on="subject_id", right_on="id", how="left"
    )

    # Merge the result with users on 'user_id'
    report_data = pd.merge(
        assessments_trainings_subjects,
        users,
        left_on="user_id",
        right_on="id",
        how="left",
    )

    # Create 'is_passed' column: True if 'marks' >= 'max_marks'
    report_data["is_passed"] = report_data["marks"] >= report_data["max_marks"]

    # Select relevant columns for the report
    report_data = report_data[
        [
            "user_id",
            "email",
            "first_name",
            "last_name",
            "training_id",
            "name_x",  # Training name
            "subject_id",
            "name_y",  # Subject name
            "marks",
            "max_marks",
            "is_passed",  # True if 'marks' >= 'max_marks', else False
        ]
    ]

    return report_data


def save_report(report_data, report_file_path):
    """Save the final report to CSV."""
    report_data.to_csv(report_file_path, index=False)
    logger.info(f"Report saved to {report_file_path}")


def run():

    # Create report dir if it doesn't exist
    os.makedirs(options.report_dir, exist_ok=True)

    logger.info("Loading staged data...")

    # Load all staged data
    prep_users_path = os.path.join(options.prep_dir, "users.csv")
    prep_subjects_path = os.path.join(options.prep_dir, "subjects.csv")
    prep_trainings_path = os.path.join(options.prep_dir, "trainings.csv")
    prep_assessments_path = os.path.join(options.prep_dir, "assessments.csv")

    users = pd.read_csv(prep_users_path)
    subjects = pd.read_csv(prep_subjects_path)
    trainings = pd.read_csv(prep_trainings_path)
    assessments = pd.read_csv(prep_assessments_path)

    logger.info("Generating report...")

    # Generate the performance report
    report_data = generate_report(users, subjects, trainings, assessments)

    # Define the report file path
    report_file_path = os.path.join(options.report_dir, "report.csv")

    # Save the report
    save_report(report_data, report_file_path)

    logger.info("Report generation completed.")


if __name__ == "__main__":
    run()
