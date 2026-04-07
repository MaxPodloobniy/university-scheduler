import pytest
from ortools.sat.python import cp_model

from src.config import Config
from src.model_handler import (
    add_max_subjects_per_day_constraints,
    add_minimum_hours_constraints,
    add_non_adjacent_repeats_constraints,
    add_single_class_per_slot_constraints,
    add_subject_slots,
)


@pytest.fixture
def config():
    return Config(days=10, start_hour=9, hours_per_day=7, max_subjects_per_day=6)


@pytest.fixture
def simple_schedule():
    """Minimal schedule data for testing constraints."""
    return {
        "group1": {
            "Math": 2,
            "Physics": 1,
        },
    }


@pytest.fixture
def model():
    return cp_model.CpModel()


def _solve(model: cp_model.CpModel) -> cp_model.CpSolver:
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE), "Solver found no solution"
    return solver


class TestAddSubjectSlots:
    def test_creates_variables_for_all_combinations(self, model, simple_schedule, config):
        slots = add_subject_slots(model, simple_schedule, config)

        assert "group1" in slots
        for subject in simple_schedule["group1"]:
            for day in range(config.days):
                for hour in range(config.hours_per_day):
                    assert (subject, day, hour) in slots["group1"]

    def test_variable_count_matches_expected(self, model, simple_schedule, config):
        slots = add_subject_slots(model, simple_schedule, config)

        num_subjects = len(simple_schedule["group1"])
        expected = num_subjects * config.days * config.hours_per_day
        assert len(slots["group1"]) == expected


class TestSingleClassPerSlotConstraint:
    def test_no_two_subjects_in_same_slot(self, model, simple_schedule, config):
        slots = add_subject_slots(model, simple_schedule, config)
        add_minimum_hours_constraints(model, slots, simple_schedule, config)
        add_single_class_per_slot_constraints(model, slots, simple_schedule, config)

        solver = _solve(model)

        for day in range(config.days):
            for hour in range(config.hours_per_day):
                active = sum(
                    solver.Value(slots["group1"][(subj, day, hour)])
                    for subj in simple_schedule["group1"]
                )
                assert active <= 1, f"Multiple subjects at day={day}, hour={hour}"


class TestMinimumHoursConstraint:
    def test_each_subject_meets_minimum(self, model, simple_schedule, config):
        slots = add_subject_slots(model, simple_schedule, config)
        add_minimum_hours_constraints(model, slots, simple_schedule, config)
        add_single_class_per_slot_constraints(model, slots, simple_schedule, config)

        solver = _solve(model)

        for subject, min_hours in simple_schedule["group1"].items():
            total = sum(
                solver.Value(slots["group1"][(subject, day, hour)])
                for day in range(config.days)
                for hour in range(config.hours_per_day)
            )
            assert total >= min_hours, f"{subject}: got {total} hours, need >= {min_hours}"


class TestMaxSubjectsPerDayConstraint:
    def test_respects_daily_limit(self, model, config):
        heavy_schedule = {
            "group1": {f"Subject_{i}": 3 for i in range(8)},
        }
        slots = add_subject_slots(model, heavy_schedule, config)
        add_minimum_hours_constraints(model, slots, heavy_schedule, config)
        add_single_class_per_slot_constraints(model, slots, heavy_schedule, config)
        add_max_subjects_per_day_constraints(model, slots, heavy_schedule, config)

        solver = _solve(model)

        for day in range(config.days):
            daily_total = sum(
                solver.Value(slots["group1"][(subj, day, hour)])
                for subj in heavy_schedule["group1"]
                for hour in range(config.hours_per_day)
            )
            assert daily_total <= config.max_subjects_per_day, f"Day {day}: {daily_total} subjects"


class TestNonAdjacentRepeatsConstraint:
    def test_same_subject_not_in_adjacent_slots(self, model, simple_schedule, config):
        slots = add_subject_slots(model, simple_schedule, config)
        add_minimum_hours_constraints(model, slots, simple_schedule, config)
        add_single_class_per_slot_constraints(model, slots, simple_schedule, config)
        add_non_adjacent_repeats_constraints(model, slots, simple_schedule, config)

        solver = _solve(model)

        for subject in simple_schedule["group1"]:
            for day in range(config.days):
                for hour in range(config.hours_per_day - 1):
                    current = solver.Value(slots["group1"][(subject, day, hour)])
                    next_slot = solver.Value(slots["group1"][(subject, day, hour + 1)])
                    assert not (current == 1 and next_slot == 1), (
                        f"{subject} repeated at day={day}, hours={hour}-{hour + 1}"
                    )
