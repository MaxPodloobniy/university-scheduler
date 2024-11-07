# University Course Scheduler

A sophisticated scheduling system that leverages Google OR-Tools to create optimal university timetables. 
This project intelligently handles complex academic scheduling challenges while maintaining balance between 
educational requirements and resource constraints.

## Overview

This automated scheduling solution transforms the traditionally complex and time-consuming task of university 
timetable creation into an efficient, optimized process. By implementing advanced constraint programming techniques, 
the system generates conflict-free schedules that respect both academic requirements and resource limitations.

## Key Features

- Automated timetable generation
- Intelligent conflict resolution
- Group schedule optimization
- Balanced course distribution
- Customizable scheduling constraints

## Technology

Built with Python, utilizing Google OR-Tools for constraint programming and optimization. This combination provides 
a robust foundation for handling complex scheduling scenarios while maintaining high performance and reliability.

## Project Structure

```plaintext
project_folder/ 
├── main.py              # Main file to run the program
├── config.py            # Configuration file with global variables (DAYS, HOURS_PER_DAY, etc.)
├── visualizer.py        # Visualization functions for displaying schedule results
├── model_handler.py     # Module to define model variables and constraints
├── excel_loader.py      # Module to load data from Excel files
├── data/                
│   ├── group1_schedule.xlsx  # Schedule data for Group 1
│   ├── group2_schedule.xlsx  # Schedule data for Group 2
│   ├── group3_schedule.xlsx  # Schedule data for Group 3
│   └── group4_schedule.xlsx  # Schedule data for Group 4
└── requirements.txt     # List of required Python packages
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MaxPodloobniy/university-scheduler.git
   cd university-scheduler
   ```

2. **Install dependencies:**
   Ensure Python is installed (recommended version ≥3.7).

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The `config.py` file contains global variables which can be modified to suit your needs:
- `DAYS`: Number of days in a week (e.g., `5`).
- `HOURS_PER_DAY`: Number of hours in a day.
- `START_HOUR`: Start hour for classes.

In the `data/` directory, you’ll find Excel files with scheduling information for each group (`group1_schedule.xlsx`, 
`group2_schedule.xlsx`, etc.). These files can be edited or new ones can be added for additional groups.

## Module Descriptions

### 1. `main.py`

The main module which:
   - Loads schedule data from Excel files using `excel_loader.py`.
   - Creates the optimization model and applies constraints via `model_handler.py`.
   - Finds an optimal solution using `Google OR-Tools` (module `cp_model.CpSolver`).
   - Calls visualization functions to display the schedule.

### 2. `config.py`

Contains essential project parameters, including `DAYS`, `HOURS_PER_DAY`, `START_HOUR`, which define the scheduling 
time limits.

### 3. `visualizer.py`

Contains the `visualize_result` function, which displays the schedule for each group. It shows classes in their 
respective time slots for each day, using color-coding for both subjects and teachers.

### 4. `model_handler.py`

Contains functions for adding variables and constraints:
   - `add_subject_slots`: Creates variables for each subject, group, day, and hour.
   - `add_max_subject_for_group_constraint`: Constraint ensuring each group can only have one class at any given time.

### 5. `excel_loader.py`

Loads class schedule data from Excel files for each group and creates the `subjects_per_group` and `teachers_per_subject` dictionaries, which are used to configure variables and constraints in the model.

## Data Structure Examples

**subjects_per_group** – dictionary with groups and the number of classes:
```python
subjects_per_group = {
    "group2": {
        'English': 3,
        'Computer Systems': 3,
        'Comp Vision': 4,
    },
    "group3": {
        'Algorithms for electronic voting': 4,
        'Data science fundamentals': 3,
        'Network and protocols': 3,
    }
}
```

**teachers_per_subject** – dictionary with subjects and assigned teachers:
```python
teachers_per_subject = {
    'English': 'Teacher A',
    'Computer Systems': 'Teacher B',
    'Comp Vision': 'Teacher C',
    'Algorithms for electronic voting': 'Teacher D',
    'Data science fundamentals': 'Teacher B',
    'Network and protocols': 'Teacher C'
}
```

## Running the Program

Run the following command to start the project:
```bash
python main.py
```

### Visualization Example

For each group, a chart will be generated with days on the horizontal axis and time slots on the vertical axis. Each class will be displayed in its designated slot, with subject and teacher labels.

## Environment Requirements

- Python ≥3.7
- Google OR-Tools
- Matplotlib

## Common Issues

1. **"No solution found":** Check that all model constraints are correctly defined, and ensure that the data in the Excel files corresponds with the `config.py` settings.
2. **Excel data errors:** If new groups or subjects are not loading, check that the structure of the `group_schedule.xlsx` files matches the expected format.

## License

This project is open-source and intended for educational and research purposes.
