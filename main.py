from model_handler import add_all_constraints, minimize_slots_usage, add_subject_slots
from data_loader import load_data_from_excel
from visualizer import visualize_result
from ortools.sat.python import cp_model


def main():
    # Створення моделі
    model = cp_model.CpModel()

    # Визначення предметів для кожної групи та їх мінімальна кількість годин
    teachers, subjects_per_group = load_data_from_excel('data/')
    print('Teachers added')

    # Додаємо змінні
    subject_slots = add_subject_slots(model, subjects_per_group)
    print('Subjects added')

    # Додаємо обмеження
    add_all_constraints(model, subject_slots, subjects_per_group, teachers)
    print('Constraints added')

    # Додаємо функцію мінімізації
    minimize_slots_usage(model, subject_slots, subjects_per_group)
    print('Minimize function added')

    # Виклик розв'язувача
    schedule_solver = cp_model.CpSolver()
    print('Solver created')
    status = schedule_solver.Solve(model)

    # Вивід результату
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for group in subjects_per_group:
            visualize_result(schedule_solver, subject_slots, subjects_per_group, teachers, group)
    else:
        print("Рішення не знайдено")


if __name__ == "__main__":
    main()