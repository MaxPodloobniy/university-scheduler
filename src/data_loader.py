from pathlib import Path

import pandas as pd


def load_data_from_excel(data_dir="data/"):
    """Load subjects-per-group and teacher assignments from Excel files."""
    subjects_per_group = {}
    data_path_for_groups = Path(data_dir + 'groups/')

    if not data_path_for_groups.exists():
        raise FileNotFoundError(f"Directory {data_dir} does not exist")

    for excel_file in data_path_for_groups.glob("*.xlsx"):
        group_name = excel_file.stem
        df = pd.read_excel(excel_file)
        subjects_per_group[group_name] = dict(zip(df['Subject'], df['Min_Hours']))

    df_teachers = pd.read_excel(data_dir + 'Teachers.xlsx')
    teachers_dict = dict(zip(df_teachers['Subject'], df_teachers['Teacher']))

    if not subjects_per_group:
        raise ValueError(f"No Excel files found in {data_dir}")

    return teachers_dict, subjects_per_group
