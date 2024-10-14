import os
import shutil
from logger import create_logger

inputs_dir = "out/inputs"
stage_dir = "out/stage"
csv_files = ["users.csv", "subjects.csv", "trainings.csv", "assessments.csv"]

logger = create_logger("stage")

# create stage directory if it doesn't exist
os.makedirs(stage_dir, exist_ok=True)

# move the CSV files to the stage directory
for file_name in csv_files:

    inputs_file_path = os.path.join(inputs_dir, file_name)
    stage_file_path = os.path.join(stage_dir, file_name)

    if os.path.exists(inputs_file_path):
        shutil.move(inputs_file_path, stage_file_path)
        logger.info(f"moved file '{file_name}'")
