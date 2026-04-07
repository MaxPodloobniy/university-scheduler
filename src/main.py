from pathlib import Path

from ortools.sat.python import cp_model
from src.data_loader import load_data_from_excel
from src.model_handler import add_all_constraints, add_subject_slots, minimize_slots_usage
from src.visualizer import visualize_result_full


def main():
    # Create a model
    model = cp_model.CpModel()

    # Define the subjects for each group, theachers for each subject and their required number of hours
    project_root = Path(__file__).resolve().parent.parent
    teachers, subjects_per_group = load_data_from_excel(str(project_root / "data") + "/")

    # Add variables to model
    subject_slots = add_subject_slots(model, subjects_per_group)

    # Add constrains to model
    add_all_constraints(model, subject_slots, subjects_per_group, teachers)

    # Add minimization function
    minimize_slots_usage(model, subject_slots, subjects_per_group)

    schedule_solver = cp_model.CpSolver()
    status = schedule_solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for group in subjects_per_group:
            visualize_result_full(schedule_solver, subject_slots, subjects_per_group, teachers, group)
    else:
        print("No solution found")


if __name__ == "__main__":
    main()
