from faker import Faker
import random
import csv
import os
from .logger import create_logger

logger = create_logger("fake")


# options to configure output
class Options:
    user_count = 10000
    subject_count = 100000
    training_count = 100000
    assessment_count = 100000
    user_roles = ["admin", "employee", "manager", "none"]
    training_modes = ["online", "offline", "onsite", "remote"]
    user_fields = [
        "id",
        "email",
        "first_name",
        "middle_name",
        "last_name",
        "role",
        "createdAt",
        "updatedAt",
    ]
    subject_fields = [
        "id",
        "name",
        "minMarks",
        "maxMarks",
        "totalTime",
        "trainingId",
        "createdBy",
        "createdAt",
        "updatedAt",
    ]
    training_fields = [
        "id",
        "name",
        "mode",
        "subjectId",
        "startedAt",
        "endedAt",
        "createdAt",
        "updatedAt",
    ]
    assessment_fields = ["userId", "trainingId", "marks", "internetAllowed"]
    out_dir = "out/inputs"
    user_file = "users.csv"
    subject_file = "subjects.csv"
    training_file = "trainings.csv"
    assessment_file = "assessments.csv"

    # Set the unclean ratio here (0 to 1, higher = more unclean data)
    unclean_ratio = 0.3


options = Options()


class Context:
    users = []
    subjects = []
    trainings = []
    assessments = []


context = Context()

fake = Faker()


# utility function to make choice between clean and unclean data
def make_choice(clean_value, unclean_value):

    return random.choices(
        [clean_value, unclean_value],
        weights=[1 - options.unclean_ratio, options.unclean_ratio],
    )[0]


# generate fake users with unclean data
def generate_users():

    for _ in range(options.user_count):
        user = {
            "id": make_choice(fake.uuid4(), None),  # Some IDs as null
            "email": make_choice(
                fake.email(),
                fake.email().replace("@", random.choice(["@$", "@-", "@.."])),
            ),
            "first_name": make_choice(
                fake.first_name(),
                (
                    fake.first_name().lower()
                    if random.choice([True, False])
                    else fake.first_name().upper()
                ),
            ),
            "middle_name": make_choice(
                fake.first_name(), random.choice([None, "", "123"])
            ),  # Random case or numbers
            "last_name": make_choice(
                fake.last_name(),
                random.choice([None, "", fake.last_name() + fake.random_letter()]),
            ),
            "role": make_choice(
                random.choice(options.user_roles[:2]), random.choice(options.user_roles)
            ),  # Invalid roles
            "createdAt": make_choice(
                fake.date_time_between(start_date="-2y", end_date="now"), "invalid-date"
            ),  # Invalid dates
            "updatedAt": make_choice(
                fake.date_time_between(start_date="-2y", end_date="now"), "bad-date"
            ),
        }

        context.users.append(user)


# generate fake subjects with unclean data
def generate_subjects():

    for _ in range(options.subject_count):
        subject = {
            "id": fake.uuid4(),
            "name": fake.word().capitalize(),
            "minMarks": make_choice(
                random.randint(0, 30), random.choice([random.randint(-10, 30), 10.5])
            ),  # Invalid numbers
            "maxMarks": make_choice(
                random.randint(60, 100), random.choice([None, "+120", "-90"])
            ),  # Invalid maxMarks
            "totalTime": make_choice(
                random.randint(60, 180), None
            ),  # Invalid totalTime
            "createdBy": make_choice(fake.uuid4(), None),  # Missing createdBy values
            "createdAt": make_choice(
                fake.date_time_between(start_date="-1y", end_date="now"), "bad-date"
            ),
            "updatedAt": make_choice(
                fake.date_time_between(start_date="-1y", end_date="now"), "invalid"
            ),
        }

        context.subjects.append(subject)


# generate fake trainings with unclean data
def generate_trainings():

    for _ in range(options.training_count):
        subject = random.choice(context.subjects)
        training = {
            "id": fake.uuid4(),
            "name": make_choice(fake.job().title(), fake.job().upper()),  # Random case
            "mode": make_choice(
                random.choice(options.training_modes[:2]),
                random.choice(options.training_modes),
            ),  # Invalid modes
            "subjectId": make_choice(subject["id"], None),  # Some missing subject IDs
            "startedAt": make_choice(
                fake.date_time_between(start_date="-1y", end_date="now"), "invalid-date"
            ),  # Invalid date
            "endedAt": make_choice(
                fake.date_time_between(start_date="now", end_date="+30d"), "wrong-date"
            ),
            "createdAt": make_choice(
                fake.date_time_between(start_date="-1y", end_date="now"), "invalid"
            ),
            "updatedAt": make_choice(
                fake.date_time_between(start_date="-1y", end_date="now"), "bad-date"
            ),
        }

        context.trainings.append(training)


# generate fake assessments with unclean data
def generate_assessments():

    for _ in range(options.assessment_count):
        user = random.choice(context.users)
        training = random.choice(context.trainings)
        assessment = {
            "userId": make_choice(
                user["id"], fake.uuid4()
            ),  # Invalid or non-existent user IDs
            "trainingId": make_choice(
                training["id"], fake.uuid4()
            ),  # Invalid or non-existent training IDs
            "marks": make_choice(
                random.randint(0, 100), random.choice([None, "+50"])
            ),  # Invalid marks
            "internetAllowed": make_choice(
                random.choice([True, False]), random.choice(["yes", "no", "123"])
            ),  # Invalid boolean values
        }

        context.assessments.append(assessment)


# save data to csv
def save_to_csv(data, filename, fieldnames):

    if not os.path.exists(options.out_dir):
        os.makedirs(options.out_dir)
    with open(f"{options.out_dir}/{filename}", mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


# main function
def run():

    logger.info(f"generating datasets with unclean_ratio '{options.unclean_ratio}'...")

    # generate datasets
    logger.info("generating users...")
    generate_users()
    logger.info(f"generating users done, count: {len(context.users)}")

    logger.info("generating subjects...")
    generate_subjects()
    logger.info(f"generating subjects done, count: {len(context.subjects)}")

    logger.info("generating trainings...")
    generate_trainings()
    logger.info(f"generating trainings done, count: {len(context.trainings)}")

    logger.info("generating assessments...")
    generate_assessments()
    logger.info(f"generating assessments done, count: {len(context.assessments)}")

    # save datasets to csv
    logger.info(f"writing users to csv file '{options.user_file}'...")
    save_to_csv(context.users, options.user_file, options.user_fields)
    logger.info(f"writing users to csv file done")

    logger.info(f"writing subjects to csv file '{options.subject_file}'...")
    save_to_csv(context.subjects, options.subject_file, options.subject_fields)
    logger.info(f"writing subjects to csv file done")

    logger.info(f"writing trainings to csv file '{options.training_file}'...")
    save_to_csv(context.trainings, options.training_file, options.training_fields)
    logger.info(f"writing trainings to csv file done")

    logger.info(f"writing assessments to csv file '{options.assessment_file}'...")
    save_to_csv(context.assessments, options.assessment_file, options.assessment_fields)
    logger.info(f"writing assessments to csv file done")


if __name__ == "__main__":
    run()
