from src.config import Config


def add_subject_slots(model, subjects_per_group, config: Config):
    """Create a boolean variable for each (group, subject, day, hour) combination."""
    subject_slots: dict[str, dict] = {}

    for group, subjects in subjects_per_group.items():
        subject_slots[group] = {}
        for subject, min_hours in subjects.items():
            for day in range(config.days):
                for hour in range(config.hours_per_day):
                    subject_slots[group][(subject, day, hour)] = model.NewBoolVar(f'{group}_{subject}_{day}_{hour}')

    return subject_slots


def add_common_subject_constraints(model, subject_slots, subjects_per_group, config: Config):
    """Force common subjects to occupy the same time slot across all groups."""
    common_slots: dict[str, dict] = {}
    for subject in config.common_subjects:
        common_slots[subject] = {}
        for day in range(config.days):
            for hour in range(config.hours_per_day):
                common_slots[subject][(day, hour)] = model.NewBoolVar(f'{subject}_{day}_{hour}')
                for group in subjects_per_group:
                    if subject in subjects_per_group[group]:
                        model.Add(subject_slots[group][(subject, day, hour)] == common_slots[subject][(day, hour)])


def add_minimum_hours_constraints(model, subject_slots, subjects_per_group, config: Config):
    """Ensure each subject meets its minimum required hours per group."""
    for group, subjects in subjects_per_group.items():
        for subject, min_hours in subjects.items():
            model.Add(
                sum(
                    subject_slots[group][(subject, day, hour)]
                    for day in range(config.days)
                    for hour in range(config.hours_per_day)
                ) >= min_hours
            )


def add_single_class_per_slot_constraints(model, subject_slots, subjects_per_group, config: Config):
    """Allow at most one subject per time slot for each group."""
    for group in subjects_per_group:
        for day in range(config.days):
            for hour in range(config.hours_per_day):
                model.Add(
                    sum(subject_slots[group][(subject, day, hour)] for subject in subjects_per_group[group]) <= 1
                )


def add_minimal_subject_count_per_period(model, subject_slots, subjects_per_group, config: Config):
    """Ensure the minimum number of lectures per subject across the entire period."""
    for group, subjects in subjects_per_group.items():
        for subject, min_hours in subjects.items():
            subject_sum = 0
            for day in range(config.days):
                for hour in range(config.hours_per_day):
                    subject_sum += subject_slots[group][(subject, day, hour)]

            model.Add(subject_sum >= min_hours)


def add_max_subjects_per_day_constraints(model, subject_slots, subjects_per_group, config: Config):
    """Limit the number of classes per day for each group."""
    for group in subjects_per_group:
        for day in range(config.days):
            model.Add(
                sum(
                    subject_slots[group][(subject, day, hour)]
                    for subject in subjects_per_group[group]
                    for hour in range(config.hours_per_day)
                ) <= config.max_subjects_per_day
            )


def add_no_gaps_constraints(model, subject_slots, subjects_per_group, config: Config):
    """Prevent scheduling gaps between consecutive hours for a subject."""
    for group in subjects_per_group:
        for subject in subjects_per_group[group]:
            for day in range(config.days):
                for hour in range(1, config.hours_per_day - 1):
                    model.AddBoolOr([
                        subject_slots[group][(subject, day, hour - 1)],
                        subject_slots[group][(subject, day, hour + 1)].Not(),
                        subject_slots[group][(subject, day, hour)]
                    ])


def add_non_adjacent_repeats_constraints(model, subject_slots, subjects_per_group, config: Config):
    """Prevent the same subject from being scheduled in consecutive time slots."""
    for group in subjects_per_group:
        for subject in subjects_per_group[group]:
            for day in range(config.days):
                for hour in range(config.hours_per_day - 1):
                    model.AddImplication(
                        subject_slots[group][(subject, day, hour)],
                        subject_slots[group][(subject, day, hour + 1)].Not()
                    )


def add_max_two_same_subject_per_day_constraints(model, subject_slots, subjects_per_group, config: Config):
    """Limit each subject to at most one lesson per day for each group."""
    for group in subjects_per_group:
        for subject in subjects_per_group[group]:
            for day in range(config.days):
                model.Add(
                    sum(subject_slots[group][(subject, day, hour)] for hour in range(config.hours_per_day)) <= 1
                )


def add_teacher_constraints(model, subject_slots, teachers_per_subject, subjects_per_group, config: Config):
    """Ensure a teacher is not assigned to multiple classes at the same time."""
    teacher_busy_slots: dict[str, dict] = {}

    for group, subjects in subjects_per_group.items():
        for subject, hours in subjects.items():
            teacher = teachers_per_subject.get(subject)
            if teacher is None:
                continue

            if teacher not in teacher_busy_slots:
                teacher_busy_slots[teacher] = {}

            for day in range(config.days):
                for hour in range(config.hours_per_day):
                    if subject in config.common_subjects:
                        if (day, hour) not in teacher_busy_slots[teacher]:
                            teacher_busy_slots[teacher][(day, hour)] = []

                        common_slot_var = subject_slots[group].get((subject, day, hour))
                        if common_slot_var is not None:
                            teacher_busy_slots[teacher][(day, hour)].append(common_slot_var)
                    else:
                        if (subject, day, hour) in subject_slots[group]:
                            subject_slot = subject_slots[group][(subject, day, hour)]
                            if (day, hour) not in teacher_busy_slots[teacher]:
                                teacher_busy_slots[teacher][(day, hour)] = []

                            teacher_busy_slots[teacher][(day, hour)].append(subject_slot)

    for teacher, slots in teacher_busy_slots.items():
        for (day, hour), slot_vars in slots.items():
            if len(slot_vars) > 1:
                model.Add(sum(slot_vars) <= 1)

    return teacher_busy_slots


def add_all_constraints(model, subject_slots, subjects_per_group, teachers, config: Config):
    add_common_subject_constraints(model, subject_slots, subjects_per_group, config)
    add_minimum_hours_constraints(model, subject_slots, subjects_per_group, config)
    add_single_class_per_slot_constraints(model, subject_slots, subjects_per_group, config)
    add_minimal_subject_count_per_period(model, subject_slots, subjects_per_group, config)
    add_max_subjects_per_day_constraints(model, subject_slots, subjects_per_group, config)
    add_no_gaps_constraints(model, subject_slots, subjects_per_group, config)
    add_non_adjacent_repeats_constraints(model, subject_slots, subjects_per_group, config)
    add_max_two_same_subject_per_day_constraints(model, subject_slots, subjects_per_group, config)
    # add_teacher_constraints(model, subject_slots, teachers, subjects_per_group, config)


def minimize_slots_usage(model, subject_slots, subjects_per_group, config: Config):
    """Minimize the total number of used time slots across all groups."""
    model.Minimize(
        sum(subject_slots[group][(subject, day, hour)]
            for group in subjects_per_group
            for subject in subjects_per_group[group]
            for day in range(config.days)
            for hour in range(config.hours_per_day))
    )
