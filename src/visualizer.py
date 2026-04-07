import matplotlib.pyplot as plt

from src.config import Config


def visualize_result(solver, subject_slots, subjects_per_group, teachers_per_subject, group_name, config: Config):
    """Render a simple schedule chart for a single group."""
    fig, ax = plt.subplots(figsize=(15, 8))
    cmap = plt.colormaps["tab20"]
    colors = cmap.colors  # type: ignore[attr-defined]

    for i, subject in enumerate(subjects_per_group[group_name]):
        teacher = teachers_per_subject.get(subject, "Unknown")
        label_text = f"{subject} ({teacher})"

        scheduled_slots = [
            (day, hour)
            for day in range(config.days)
            for hour in range(config.hours_per_day)
            if solver.Value(subject_slots[group_name][(subject, day, hour)]) == 1
        ]

        for slot in scheduled_slots:
            day, hour = slot
            ax.broken_barh([(day, 1)], (config.start_hour + hour, 1),
                           facecolors=colors[i % len(colors)],
                           label=label_text if slot == scheduled_slots[0] else "")

    ax.set_xlabel('Days')
    ax.set_ylabel('Hours')
    ax.set_xticks(range(0, config.days))
    ax.set_yticks(range(config.start_hour, config.start_hour + config.hours_per_day))
    ax.grid(True)
    ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1), title='Subjects (Teacher)')
    plt.show()


def visualize_result_full(solver, subject_slots, subjects_per_group, teachers_per_subject, group_name, config: Config):
    """Render a two-week schedule chart with weekends gaps for a single group."""
    fig, ax = plt.subplots(figsize=(15, 8))
    cmap = plt.colormaps["tab20"]
    colors = cmap.colors  # type: ignore[attr-defined]

    weekdays_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun", "Mon", "Tue", "Wed", "Thu", "Fri"]
    days_with_weekends = list(range(12))

    for i, subject in enumerate(subjects_per_group[group_name]):
        teacher = teachers_per_subject.get(subject, "Unknown")
        label_text = f"{subject} ({teacher})"

        scheduled_slots = [
            (day, hour)
            for day in range(config.days)
            for hour in range(config.hours_per_day)
            if solver.Value(subject_slots[group_name][(subject, day, hour)]) == 1
        ]

        for slot in scheduled_slots:
            day, hour = slot
            plot_day = day + (day // 5) * 2  # offset to skip weekends
            ax.broken_barh([(plot_day, 1)], (config.start_hour + hour, 1),
                           facecolors=colors[i % len(colors)],
                           label=label_text if slot == scheduled_slots[0] else "")

    ax.set_xlabel('Day of the week')
    ax.set_ylabel('Time')
    ax.set_xticks(range(len(days_with_weekends)))
    ax.set_xticklabels(weekdays_labels)
    ax.set_yticks(range(config.start_hour, config.start_hour + config.hours_per_day))
    ax.set_yticklabels([f"{hour}:00" for hour in range(config.start_hour, config.start_hour + config.hours_per_day)])
    ax.grid(True)
    ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1), title='Subjects (Teacher)')
    plt.show()
