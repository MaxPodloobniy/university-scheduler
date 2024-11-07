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


import matplotlib.pyplot as plt
from config import *

def visualize_result_test(solver, subject_slots, subjects_per_group, teachers_per_subject, group_name):
    fig, ax = plt.subplots(figsize=(15, 8))
    colors = plt.cm.tab20.colors  # Вибір кольорів для різних предметів

    # День тижня (з пустими для вихідних)
    weekdays_labels = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд", "Пн", "Вт", "Ср", "Чт", "Пт"]
    days_with_weekends = list(range(12))  # Усього 12 слотів (включаючи пусті суботу та неділю)

    for i, subject in enumerate(subjects_per_group[group_name]):
        teacher = teachers_per_subject.get(subject, "Unknown")
        label_text = f"{subject} ({teacher})"

        scheduled_slots = [(day, hour) for day in range(DAYS) for hour in range(HOURS_PER_DAY)
                           if solver.Value(subject_slots[group_name][(subject, day, hour)]) == 1]

        for slot in scheduled_slots:
            day, hour = slot
            # Додаємо заняття до графіку, додаючи зсув, щоб пропустити вихідні
            plot_day = day + (day // 5) * 2  # Зсув на два дні після п'ятниці
            ax.broken_barh([(plot_day, 1)], (START_HOUR + hour, 1),
                           facecolors=colors[i % len(colors)],
                           label=label_text if slot == scheduled_slots[0] else "")

    ax.set_xlabel('Дні тижня')
    ax.set_ylabel('Час')
    ax.set_xticks(range(len(days_with_weekends)))
    ax.set_xticklabels(weekdays_labels)  # Встановлення назв днів
    ax.set_yticks(range(START_HOUR, START_HOUR + HOURS_PER_DAY))
    ax.set_yticklabels([f"{hour}:00" for hour in range(START_HOUR, START_HOUR + HOURS_PER_DAY)])  # Формат часу
    ax.grid(True)
    ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1), title='Предмети (Викладач)')
    plt.show()
