from ortools.sat.python import cp_model
import matplotlib.pyplot as plt
from config import *


# Функція для візуалізації розкладу для кожної групи
def visualize_result(solver, subject_slots, group_name):
    fig, ax = plt.subplots(figsize=(15, 8))
    colors = plt.cm.tab20.colors  # Вибір кольорів для різних предметів

    for i, subject in enumerate(subjects_per_group[group_name]):
        scheduled_slots = [(day, hour) for day in range(DAYS) for hour in range(HOURS_PER_DAY)
                           if solver.Value(subject_slots[group_name][(subject, day, hour)]) == 1]

        for slot in scheduled_slots:
            day, hour = slot
            ax.broken_barh([(day, 1)], (START_HOUR + hour, 1),
                           facecolors=colors[i % len(colors)],
                           label=subject if slot == scheduled_slots[0] else "")

    ax.set_xlabel('Дні')
    ax.set_ylabel('Години')
    ax.set_xticks(range(0, DAYS))
    ax.set_yticks(range(START_HOUR, START_HOUR + HOURS_PER_DAY))
    ax.grid(True)
    ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1), title='Предмети')
    plt.show()


# Створення моделі
model = cp_model.CpModel()



# Визначення предметів для кожної групи та їх мінімальна кількість годин
subjects_per_group = {
    "group1": {
        'English': 3,
        'Economics': 2,
        'Data Science': 4,
    },
    "group2": {
        'English': 3,
        'Computer Systems': 3,
        'Comp Vision': 4,
    },
    "group3": {
        'Algorithms for electronic voting': 4,
        'Data science fundamentals': 3,
        'Network and protocols': 3,
    },
    "group4": {
        'Engineering computer graphics': 3,
        'Simulation modelling': 4,
        'Internet of things technologies': 4,
    }
}



# ========================= ЗМІННІ =========================

# Додавання змінних для кожної групи
subject_slots = {}

for group, subjects in subjects_per_group.items():
    subject_slots[group] = {}
    for subject, min_hours in subjects.items():
        for day in range(DAYS):
            for hour in range(HOURS_PER_DAY):
                subject_slots[group][(subject, day, hour)] = model.NewBoolVar(f'{group}_{subject}_{day}_{hour}')


# ========================= ОБМЕЖЕННЯ =========================

# Обмеження для спільних занять
common_slots = {}
for subject in COMMON_SUBJECTS:
    common_slots[subject] = {}
    for day in range(DAYS):
        for hour in range(HOURS_PER_DAY):
            # Змінна для спільного слоту, яку використовують всі групи
            common_slots[subject][(day, hour)] = model.NewBoolVar(f'{subject}_{day}_{hour}')
            # Зв'язок з кожною групою (спільний слот може бути використаний тільки одночасно всіма групами)
            for group in subjects_per_group:
                if subject in subjects_per_group[group]:
                    model.Add(subject_slots[group][(subject, day, hour)] == common_slots[subject][(day, hour)])

# Обмеження мінімальної кількості годин на предмет для кожної групи
for group, subjects in subjects_per_group.items():
    for subject, min_hours in subjects.items():
        model.Add(
            sum(subject_slots[group][(subject, day, hour)] for day in range(DAYS) for hour in range(HOURS_PER_DAY)) >= min_hours
        )

# Обмеження: в кожному часовому слоті для кожної групи має бути не більше одного заняття
for group in subjects_per_group:
    for day in range(DAYS):
        for hour in range(HOURS_PER_DAY):
            model.Add(
                sum(subject_slots[group][(subject, day, hour)] for subject in subjects_per_group[group]) <= 1
            )

# Обмеження: за заданий період має відбутися мінімально така кількість лекцій по предмету для кожної групи
for group, subjects in subjects_per_group.items():
    for subject, min_hours in subjects.items():
        subject_sum = 0
        for day in range(DAYS):
            for hour in range(HOURS_PER_DAY):
                subject_sum += subject_slots[group][(subject, day, hour)]

        model.Add(subject_sum >= min_hours)

# Обмеження: в кожному часовому слоті для кожної групи має бути не більше одного заняття
for group in subjects_per_group:
    for day in range(DAYS):
        for hour in range(HOURS_PER_DAY):
            model.Add(
                sum(subject_slots[group][(subject, day, hour)] for subject in subjects_per_group[group]) <= 1
            )

# Обмеження: не більше чотирьох предметів на день для кожної групи
for group in subjects_per_group:
    for day in range(DAYS):
        model.Add(
            sum(subject_slots[group][(subject, day, hour)] for subject in subjects_per_group[group] for hour in range(HOURS_PER_DAY)) <= 4
        )

# Обмеження: уникати розривів у часі між заняттями для кожної групи і предмета
for group in subjects_per_group:
    for subject in subjects_per_group[group]:
        for day in range(DAYS):
            for hour in range(1, HOURS_PER_DAY - 1):
                # Якщо заняття заплановане в поточний і наступний час, попереднє також повинно бути заповнене
                model.AddBoolOr([
                    subject_slots[group][(subject, day, hour - 1)],
                    subject_slots[group][(subject, day, hour + 1)].Not(),
                    subject_slots[group][(subject, day, hour)]
                ])

# Обмеження: один і той самий предмет не може повторюватися в сусідніх часових слотах для кожної групи
for group in subjects_per_group:
    for subject in subjects_per_group[group]:
        for day in range(DAYS):
            for hour in range(HOURS_PER_DAY - 1):
                # Якщо предмет запланований на годину "hour", то він не може бути запланований на "hour + 1"
                model.AddImplication(
                    subject_slots[group][(subject, day, hour)],
                    subject_slots[group][(subject, day, hour + 1)].Not()
                )

# Обмеження: не більше двох занять одного предмета на день для кожної групи
for group in subjects_per_group:
    for subject in subjects_per_group[group]:
        for day in range(DAYS):
            model.Add(
                sum(subject_slots[group][(subject, day, hour)] for hour in range(HOURS_PER_DAY)) <= 2
            )


# ========================= ФУНКЦІЇ =========================

# Логіка: мінімізувати використання часових слотів
model.Minimize(
    sum(subject_slots[group][(subject, day, hour)]
        for group in subjects_per_group
        for subject in subjects_per_group[group]
        for day in range(DAYS)
        for hour in range(HOURS_PER_DAY))
)

# Виклик розв'язувача
schedule_solver = cp_model.CpSolver()
status = schedule_solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    for group in subjects_per_group:
        visualize_result(schedule_solver, subject_slots, group)
else:
    print("Рішення не знайдено")
