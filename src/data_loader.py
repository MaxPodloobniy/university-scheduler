import pandas as pd
from pathlib import Path


def load_data_from_excel(data_dir="data/"):
    """Завантажує дані з Excel файлів для всіх груп."""

    subjects_per_group = {}
    data_path_for_groups = Path(data_dir+'groups/')

    # Перевірка існування директорії
    if not data_path_for_groups.exists():
        raise FileNotFoundError(f"Директорія {data_dir} не існує")

    # Обробка Excel файлів всіх груп в директорії
    for excel_file in data_path_for_groups.glob("*.xlsx"):
        # Отримання назви групи з імені файлу
        group_name = excel_file.stem  # Наприклад, з "group1.xlsx" отримаємо "group1"

        df = pd.read_excel(excel_file)

        # Створення словника предметів для групи
        subjects_dict = dict(zip(df['Subject'], df['Min_Hours']))
        subjects_per_group[group_name] = subjects_dict

    # Завантажимо дані про вчителів
    df_teachers = pd.read_excel(data_dir+'Teachers.xlsx')
    teachers_dict = dict(zip(df_teachers['Subject'], df_teachers['Teacher']))

    # Перевірка, чи були завантажені дані
    if not subjects_per_group:
        raise ValueError(f"Не знайдено жодного Excel файлу в директорії {data_dir}")

    return teachers_dict, subjects_per_group
