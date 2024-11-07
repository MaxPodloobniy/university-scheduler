from config import *

# ========================= ЗМІННІ =========================

def add_subject_slots(model, subjects_per_group):
    """Додавання змінних для кожної групи"""
    subject_slots = {}

    for group, subjects in subjects_per_group.items():
        subject_slots[group] = {}
        for subject, min_hours in subjects.items():
            for day in range(DAYS):
                for hour in range(HOURS_PER_DAY):
                    subject_slots[group][(subject, day, hour)] = model.NewBoolVar(f'{group}_{subject}_{day}_{hour}')

    return subject_slots

# ========================= ОБМЕЖЕННЯ =========================

def add_common_subject_constraints(model, subject_slots, subjects_per_group):
    """Обмеження для спільних занять."""
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


def add_minimum_hours_constraints(model, subject_slots, subjects_per_group):
    """Обмеження мінімальної кількості годин на предмет для кожної групи."""
    for group, subjects in subjects_per_group.items():
        for subject, min_hours in subjects.items():
            model.Add(
                sum(subject_slots[group][(subject, day, hour)] for day in range(DAYS) for hour in range(HOURS_PER_DAY)) >= min_hours
            )


def add_single_class_per_slot_constraints(model, subject_slots, subjects_per_group):
    """Обмеження: в кожному часовому слоті для кожної групи має бути не більше одного заняття."""
    for group in subjects_per_group:
        for day in range(DAYS):
            for hour in range(HOURS_PER_DAY):
                model.Add(
                    sum(subject_slots[group][(subject, day, hour)] for subject in subjects_per_group[group]) <= 1
                )


def add_minimal_subject_count_per_period(model, subject_slots, subjects_per_group):
    """Обмеження: за заданий період має відбутися мінімально така кількість лекцій по предмету для кожної групи"""
    for group, subjects in subjects_per_group.items():
        for subject, min_hours in subjects.items():
            subject_sum = 0
            for day in range(DAYS):
                for hour in range(HOURS_PER_DAY):
                    subject_sum += subject_slots[group][(subject, day, hour)]

            model.Add(subject_sum >= min_hours)


def add_max_subject_for_group_constraint(model, subject_slots, subjects_per_group):
    """Обмеження: в кожному часовому слоті для кожної групи має бути не більше одного заняття"""
    for group in subjects_per_group:
        for day in range(DAYS):
            for hour in range(HOURS_PER_DAY):
                model.Add(
                    sum(subject_slots[group][(subject, day, hour)] for subject in subjects_per_group[group]) <= 1
                )


def add_max_subjects_per_day_constraints(model, subject_slots, subjects_per_group):
    """Обмеження: не більше шести предметів на день для кожної групи."""
    for group in subjects_per_group:
        for day in range(DAYS):
            model.Add(
                sum(subject_slots[group][(subject, day, hour)] for subject in subjects_per_group[group] for hour in range(HOURS_PER_DAY)) <= 6
            )


def add_no_gaps_constraints(model, subject_slots, subjects_per_group):
    """Обмеження: уникати розривів у часі між заняттями для кожної групи і предмета."""
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


def add_non_adjacent_repeats_constraints(model, subject_slots, subjects_per_group):
    """Обмеження: один і той самий предмет не може повторюватися в сусідніх часових слотах для кожної групи."""
    for group in subjects_per_group:
        for subject in subjects_per_group[group]:
            for day in range(DAYS):
                for hour in range(HOURS_PER_DAY - 1):
                    # Якщо предмет запланований на годину "hour", то він не може бути запланований на "hour + 1"
                    model.AddImplication(
                        subject_slots[group][(subject, day, hour)],
                        subject_slots[group][(subject, day, hour + 1)].Not()
                    )


def add_max_two_same_subject_per_day_constraints(model, subject_slots, subjects_per_group):
    """Обмеження: не більше двох занять одного предмета на день для кожної групи."""
    for group in subjects_per_group:
        for subject in subjects_per_group[group]:
            for day in range(DAYS):
                model.Add(
                    sum(subject_slots[group][(subject, day, hour)] for hour in range(HOURS_PER_DAY)) <= 2
                )


def add_teacher_constraints(model, subject_slots, teachers_per_subject, subjects_per_group):
    """Add constraints to ensure a teacher doesn't teach more than one subject at the same time."""

    # Initialize slot variables for each teacher
    teacher_slots = {}

    # Loop through all groups and subjects to link them to teachers
    for group, subjects in teachers_per_subject.items():
        for subject, min_hours in subjects.items():
            teacher = subjects_per_group.get(subject)  # Get the teacher for the subject
            if teacher is None:
                continue  # Skip if there's no teacher assigned to the subject

            # Initialize dictionary for each teacher if not already created
            if teacher not in teacher_slots:
                teacher_slots[teacher] = {}

            # Add variables for each day and hour the teacher could teach
            for day in range(DAYS):
                for hour in range(HOURS_PER_DAY):
                    # Initialize variable for this day and hour if it doesn't exist
                    if (day, hour) not in teacher_slots[teacher]:
                        teacher_slots[teacher][(day, hour)] = model.NewBoolVar(f'{teacher}_{day}_{hour}')

                    # Ensure the teacher can only teach one subject at this time
                    if (subject, day, hour) in subject_slots[group]:
                        model.AddImplication(
                            subject_slots[group][(subject, day, hour)],
                            teacher_slots[teacher][(day, hour)]
                        )

    # Add primary constraint to prevent scheduling conflicts for each teacher
    for teacher, slots in teacher_slots.items():
        for (curr_day, curr_hour), var in slots.items():
            # Ensure a teacher can only teach one subject in a given time slot
            model.Add(sum(slots[(curr_day, curr_hour)] for (curr_day, curr_hour) in slots) <= 1)

    return teacher_slots




def add_all_constraints(model, subject_slots, subjects_per_group, teachers):
    add_common_subject_constraints(model, subject_slots, subjects_per_group)
    add_minimum_hours_constraints(model, subject_slots, subjects_per_group)
    add_single_class_per_slot_constraints(model, subject_slots, subjects_per_group)
    add_minimal_subject_count_per_period(model, subject_slots, subjects_per_group)
    add_max_subject_for_group_constraint(model, subject_slots, subjects_per_group)
    add_max_subjects_per_day_constraints(model, subject_slots, subjects_per_group)
    add_no_gaps_constraints(model, subject_slots, subjects_per_group)
    add_non_adjacent_repeats_constraints(model, subject_slots, subjects_per_group)
    add_max_two_same_subject_per_day_constraints(model, subject_slots, subjects_per_group)
    #add_teacher_constraints(model, subject_slots, subjects_per_group, teachers)


# ========================= ФУНКЦІЇ =========================

def minimize_slots_usage(model, subject_slots, subjects_per_group):
    """Логіка: мінімізувати використання часових слотів"""
    model.Minimize(
        sum(subject_slots[group][(subject, day, hour)]
            for group in subjects_per_group
            for subject in subjects_per_group[group]
            for day in range(DAYS)
            for hour in range(HOURS_PER_DAY))
    )
