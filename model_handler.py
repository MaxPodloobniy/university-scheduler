from config import *

# ========================= VARIABLES =========================

def add_subject_slots(model, subjects_per_group):
    """Adding variables for each group"""
    subject_slots = {}

    for group, subjects in subjects_per_group.items():
        subject_slots[group] = {}
        for subject, min_hours in subjects.items():
            for day in range(DAYS):
                for hour in range(HOURS_PER_DAY):
                    subject_slots[group][(subject, day, hour)] = model.NewBoolVar(f'{group}_{subject}_{day}_{hour}')

    return subject_slots

# ========================= CONSTRAINTS =========================

def add_common_subject_constraints(model, subject_slots, subjects_per_group):
    """Limitations for joint classes."""
    common_slots = {}
    for subject in COMMON_SUBJECTS:
        common_slots[subject] = {}
        for day in range(DAYS):
            for hour in range(HOURS_PER_DAY):
                # Variable for a shared slot used by all groups
                common_slots[subject][(day, hour)] = model.NewBoolVar(f'{subject}_{day}_{hour}')
                # Communication with each group (a common slot can only be used simultaneously by all groups)
                for group in subjects_per_group:
                    if subject in subjects_per_group[group]:
                        model.Add(subject_slots[group][(subject, day, hour)] == common_slots[subject][(day, hour)])


def add_minimum_hours_constraints(model, subject_slots, subjects_per_group):
    """Limitation of the minimum number of hours per subject for each group."""
    for group, subjects in subjects_per_group.items():
        for subject, min_hours in subjects.items():
            model.Add(
                sum(subject_slots[group][(subject, day, hour)] for day in range(DAYS) for hour in range(HOURS_PER_DAY)) >= min_hours
            )


def add_single_class_per_slot_constraints(model, subject_slots, subjects_per_group):
    """Restrictions: there should be no more than one lesson in each time slot for each group."""
    for group in subjects_per_group:
        for day in range(DAYS):
            for hour in range(HOURS_PER_DAY):
                model.Add(
                    sum(subject_slots[group][(subject, day, hour)] for subject in subjects_per_group[group]) <= 1
                )


def add_minimal_subject_count_per_period(model, subject_slots, subjects_per_group):
    """Restrictions: during a given period, the least the following number of lectures
    on the subject for each group must take place"""
    for group, subjects in subjects_per_group.items():
        for subject, min_hours in subjects.items():
            subject_sum = 0
            for day in range(DAYS):
                for hour in range(HOURS_PER_DAY):
                    subject_sum += subject_slots[group][(subject, day, hour)]

            model.Add(subject_sum >= min_hours)


def add_max_subjects_per_day_constraints(model, subject_slots, subjects_per_group):
    """Limitations: no more than six items per day for each group."""
    for group in subjects_per_group:
        for day in range(DAYS):
            model.Add(
                sum(subject_slots[group][(subject, day, hour)] for subject in subjects_per_group[group] for hour in range(HOURS_PER_DAY)) <= MAX_SUBJECTS_PER_DAY
            )


def add_no_gaps_constraints(model, subject_slots, subjects_per_group):
    """Limitations: avoid gaps in time between classes for each group and subject."""
    for group in subjects_per_group:
        for subject in subjects_per_group[group]:
            for day in range(DAYS):
                for hour in range(1, HOURS_PER_DAY - 1):
                    # If a lesson is scheduled for the current and next time, the previous one must also be filled in
                    model.AddBoolOr([
                        subject_slots[group][(subject, day, hour - 1)],
                        subject_slots[group][(subject, day, hour + 1)].Not(),
                        subject_slots[group][(subject, day, hour)]
                    ])


def add_non_adjacent_repeats_constraints(model, subject_slots, subjects_per_group):
    """Restriction: the same subject cannot be repeated in adjacent time slots for each group."""
    for group in subjects_per_group:
        for subject in subjects_per_group[group]:
            for day in range(DAYS):
                for hour in range(HOURS_PER_DAY - 1):
                    # If a subject is scheduled for ‘hour’, it cannot be scheduled for ‘hour + 1’
                    model.AddImplication(
                        subject_slots[group][(subject, day, hour)],
                        subject_slots[group][(subject, day, hour + 1)].Not()
                    )


def add_max_two_same_subject_per_day_constraints(model, subject_slots, subjects_per_group):
    """Limitations: no more than one lesson of one subject per day for each group."""
    for group in subjects_per_group:
        for subject in subjects_per_group[group]:
            for day in range(DAYS):
                model.Add(
                    sum(subject_slots[group][(subject, day, hour)] for hour in range(HOURS_PER_DAY)) <= 1
                )


def add_teacher_constraints(model, subject_slots, teachers_per_subject, subjects_per_group):
    """Add constraints to ensure a teacher doesn't teach more than one subject at the same time across groups, with shared handling for common subjects."""
    teacher_busy_slots = {}

    for group, subjects in subjects_per_group.items():
        for subject, hours in subjects.items():
            teacher = teachers_per_subject.get(subject)
            if teacher is None:
                continue

            # Initialize busy slots for each teacher if not already initialized
            if teacher not in teacher_busy_slots:
                teacher_busy_slots[teacher] = {}

            for day in range(DAYS):
                for hour in range(HOURS_PER_DAY):
                    # Check if subject is common and handle shared slots for groups
                    if subject in COMMON_SUBJECTS:
                        # Use shared slot across groups for common subjects
                        if (day, hour) not in teacher_busy_slots[teacher]:
                            teacher_busy_slots[teacher][(day, hour)] = []

                        # Each common subject slot is the same across all groups
                        common_slot_var = subject_slots[group].get((subject, day, hour))
                        if common_slot_var is not None:
                            teacher_busy_slots[teacher][(day, hour)].append(common_slot_var)
                    else:
                        # Handle non-common subjects separately for each group
                        if (subject, day, hour) in subject_slots[group]:
                            subject_slot = subject_slots[group][(subject, day, hour)]
                            if (day, hour) not in teacher_busy_slots[teacher]:
                                teacher_busy_slots[teacher][(day, hour)] = []

                            teacher_busy_slots[teacher][(day, hour)].append(subject_slot)

    # Add constraints: enforce only one active teaching slot per teacher per time slot
    for teacher, slots in teacher_busy_slots.items():
        for (day, hour), slot_vars in slots.items():
            if len(slot_vars) > 1:
                # Add constraint that only one of the slots can be active
                model.Add(sum(slot_vars) <= 1)

    return teacher_busy_slots





def add_all_constraints(model, subject_slots, subjects_per_group, teachers):
    add_common_subject_constraints(model, subject_slots, subjects_per_group)
    add_minimum_hours_constraints(model, subject_slots, subjects_per_group)
    add_single_class_per_slot_constraints(model, subject_slots, subjects_per_group)
    add_minimal_subject_count_per_period(model, subject_slots, subjects_per_group)
    add_max_subjects_per_day_constraints(model, subject_slots, subjects_per_group)
    add_no_gaps_constraints(model, subject_slots, subjects_per_group)
    add_non_adjacent_repeats_constraints(model, subject_slots, subjects_per_group)
    add_max_two_same_subject_per_day_constraints(model, subject_slots, subjects_per_group)
    # add_teacher_constraints(model, subject_slots, teachers, subjects_per_group)


# ========================= FUNCTIONS =========================

def minimize_slots_usage(model, subject_slots, subjects_per_group):
    """Logic: minimise the use of time slots"""
    model.Minimize(
        sum(subject_slots[group][(subject, day, hour)]
            for group in subjects_per_group
            for subject in subjects_per_group[group]
            for day in range(DAYS)
            for hour in range(HOURS_PER_DAY))
    )
