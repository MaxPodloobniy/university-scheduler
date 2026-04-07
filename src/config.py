import argparse
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    days: int = 10
    start_hour: int = 9
    hours_per_day: int = 7
    max_subjects_per_day: int = 6
    subjects: list[str] = field(default_factory=list)
    common_subjects: list[str] = field(default_factory=list)

    @classmethod
    def load(cls, args: argparse.Namespace, toml_path: str | None = None) -> "Config":
        if toml_path is None:
            toml_path = str(Path(__file__).resolve().parent.parent / "config.toml")

        with open(toml_path, "rb") as f:
            data = tomllib.load(f)

        return cls(
            days=args.days,
            start_hour=args.start_hour,
            hours_per_day=args.hours_per_day,
            max_subjects_per_day=args.max_subjects_per_day,
            subjects=data.get("subjects", []),
            common_subjects=data.get("common_subjects", []),
        )
