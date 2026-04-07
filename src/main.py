import argparse
from pathlib import Path

from ortools.sat.python import cp_model

from src.config import Config
from src.data_loader import load_data_from_excel
from src.model_handler import add_all_constraints, add_subject_slots, minimize_slots_usage
from src.visualizer import visualize_result_full


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="University course scheduler")
    parser.add_argument("--days", type=int, default=10, help="number of scheduling days (default: 10)")
    parser.add_argument("--start-hour", type=int, default=9, help="first class hour (default: 9)")
    parser.add_argument("--hours-per-day", type=int, default=7, help="teaching hours per day (default: 7)")
    parser.add_argument("--max-subjects-per-day", type=int, default=6, help="max subjects per day (default: 6)")
    return parser.parse_args()


def main():
    args = parse_args()
    config = Config.load(args)

    model = cp_model.CpModel()

    project_root = Path(__file__).resolve().parent.parent
    teachers, subjects_per_group = load_data_from_excel(str(project_root / "data") + "/")

    subject_slots = add_subject_slots(model, subjects_per_group, config)
    add_all_constraints(model, subject_slots, subjects_per_group, teachers, config)
    minimize_slots_usage(model, subject_slots, subjects_per_group, config)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for group in subjects_per_group:
            visualize_result_full(solver, subject_slots, subjects_per_group, teachers, group, config)
    else:
        print("No solution found")


if __name__ == "__main__":
    main()
