import pytest
from src.data_loader import load_data_from_excel


class TestLoadDataFromExcel:
    def test_returns_correct_structure(self):
        teachers, subjects_per_group = load_data_from_excel("data/")

        assert isinstance(teachers, dict)
        assert isinstance(subjects_per_group, dict)
        assert len(subjects_per_group) > 0

        for group_name, subjects in subjects_per_group.items():
            assert isinstance(group_name, str)
            assert isinstance(subjects, dict)
            for subject, hours in subjects.items():
                assert isinstance(subject, str)
                assert isinstance(hours, (int, float))
                assert hours > 0

    def test_teachers_dict_has_string_values(self):
        teachers, _ = load_data_from_excel("data/")

        for subject, teacher in teachers.items():
            assert isinstance(subject, str)
            assert isinstance(teacher, str)

    def test_missing_directory_raises_error(self):
        with pytest.raises(FileNotFoundError):
            load_data_from_excel("nonexistent_directory/")

    def test_empty_directory_raises_error(self, tmp_path):
        empty_groups_dir = tmp_path / "groups"
        empty_groups_dir.mkdir()
        teachers_file = tmp_path / "Teachers.xlsx"
        teachers_file.touch()

        with pytest.raises((ValueError, Exception)):
            load_data_from_excel(str(tmp_path) + "/")
