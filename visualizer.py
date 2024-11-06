import matplotlib.pyplot as plt
from config import *

# Функція для візуалізації розкладу для кожної групи
def visualize_result(solver, subject_slots, subjects_per_group, teachers_per_subject, group_name):
    fig, ax = plt.subplots(figsize=(15, 8))
    colors = plt.cm.tab20.colors  # Вибір кольорів для різних предметів

    for i, subject in enumerate(subjects_per_group[group_name]):
        # Отримуємо ім'я викладача для предмета
        teacher = teachers_per_subject.get(subject, "Unknown")
        # Формуємо текст для виведення в графіку
        label_text = f"{subject} ({teacher})"

        # Знаходимо часові слоти, коли заняття заплановано
        scheduled_slots = [(day, hour) for day in range(DAYS) for hour in range(HOURS_PER_DAY)
                           if solver.Value(subject_slots[group_name][(subject, day, hour)]) == 1]

        for slot in scheduled_slots:
            day, hour = slot
            # Додаємо кожен запланований слот до графіку
            ax.broken_barh([(day, 1)], (START_HOUR + hour, 1),
                           facecolors=colors[i % len(colors)],
                           label=label_text if slot == scheduled_slots[0] else "")

    ax.set_xlabel('Дні')
    ax.set_ylabel('Години')
    ax.set_xticks(range(0, DAYS))
    ax.set_yticks(range(START_HOUR, START_HOUR + HOURS_PER_DAY))
    ax.grid(True)
    ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1), title='Предмети (Викладач)')
    plt.show()

