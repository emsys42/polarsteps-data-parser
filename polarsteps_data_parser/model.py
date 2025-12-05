import os
from dataclasses import dataclass
from datetime import datetime, date
from loguru import logger
from pathlib import Path
from typing import Self
from polarsteps_data_parser.utils import parse_date, find_folder_by_id, list_files_in_folder


@dataclass
class Location:
    """Location as tracked by the travel tracker."""

    lat: float
    lon: float
    time: datetime

    @classmethod
    def from_json(cls, data: dict) -> Self:
        """Parse object from JSON data."""
        return Location(lat=data["lat"], lon=data["lon"], time=parse_date(data["time"]))


@dataclass
class StepLocation:
    """Location as provided by a step."""

    lat: float
    lon: float
    name: str
    country: str

    @classmethod
    def from_json(cls, data: dict) -> Self:
        """Parse object from JSON data."""
        return StepLocation(
            lat=data["lat"],
            lon=data["lon"],
            name=data["name"],
            country=data["detail"],
        )


@dataclass
class Step:
    """Polarsteps Step object."""

    step_id: str
    name: str
    description: str
    location: StepLocation
    date: date
    photos: list[Path]
    videos: list[Path]

    @classmethod
    def from_json(cls, data: dict) -> Self:
        """Parse object from JSON data."""
        logger.debug(f"Parsing step {data['id']}")
        s = Step(
            step_id=data["id"],
            name=data["name"] or data["display_name"],
            description=data["description"],
            location=StepLocation.from_json(data["location"]),
            date=parse_date(data["start_time"]),
            photos=[],
            videos=[],
        )
        s.load_media()
        return s

    def load_media(self) -> None:
        """Load photos and videos for the step."""
        media_dir = find_folder_by_id(self.step_id)
        if media_dir is not None:
            self.photos = list_files_in_folder(os.path.join(media_dir,"photos"), dir_has_to_exist=False)
            self.videos = list_files_in_folder(os.path.join(media_dir,"videos"), dir_has_to_exist=False)
        logger.debug(f"Found {len(self.photos)} photos, {len(self.videos)} videos")


@dataclass
class Trip:
    """Polarsteps trip object."""

    name: str
    start_date: datetime
    end_date: datetime
    cover_photo_path: str
    steps: list[Step]

    @classmethod
    def from_json(cls, data: dict) -> Self:
        """Parse object from JSON data."""
        return Trip(
            name=data["name"],
            start_date=parse_date(data.get("start_date")),
            end_date=parse_date(data.get("end_date")),
            cover_photo_path=data["cover_photo_path"],
            steps=[Step.from_json(step) for step in data.get("all_steps")],
        )
