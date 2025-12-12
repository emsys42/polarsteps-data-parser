from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Self

from loguru import logger

import polarsteps_data_parser.utils as utils


@dataclass
class Location:
    """Location as tracked by the travel tracker."""

    lat: float
    lon: float
    time: datetime

    @classmethod
    def from_json(cls, data: dict) -> Self:
        """Parse object from JSON data."""
        return Location(lat=data["lat"], lon=data["lon"], time=utils.parse_date(data["time"]))


def load_locations_from_file(file: Path) -> list[Location]:
    """Load all locations of a trip in Polarsteps which are located in file 'locations.json'."""
    if not file.exists():
        raise FileNotFoundError(f"File '{file}' does not exist.")
    location_data_json = utils.load_json_from_file(file)
    locations = [Location.from_json(data) for data in location_data_json["locations"]]
    return locations


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
            date=utils.parse_date(data["start_time"]),
            photos=[],
            videos=[],
        )
        return s

    def lookup_media_files(self, input_folder: Path) -> None:
        """Search for photos and videos for all steps in the file system."""
        if self.step_id is None or self.step_id == "":
            raise ValueError("Step ID is '{self.step_id}', cannot lookup media files.")
        photos, videos = utils.find_media_files_of_step(self.step_id, input_folder)
        self.photos = photos
        self.videos = videos
        return len(photos), len(videos)


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
            start_date=utils.parse_date(data.get("start_date")),
            end_date=utils.parse_date(data.get("end_date")),
            cover_photo_path=data["cover_photo_path"],
            steps=[Step.from_json(step) for step in data.get("all_steps")],
        )


    def lookup_media_files(self, input_folder: Path) -> tuple[int, int]:
        """Search for photos and videos for all steps in the file system."""
        found_fotos = 0
        found_videos = 0
        for step in self.steps:
            new_fotos, new_videos = step.lookup_media_files(input_folder)
            found_fotos += new_fotos
            found_videos += new_videos
        logger.debug(f"Found {found_fotos} photos and {found_videos} videos for trip '{self.name}'")
        return found_fotos, found_videos


    def get_step(self, step_number: int) -> Step:
        """Get step by its number (1-based)."""
        if step_number < 1 or step_number > len(self.steps):
            raise IndexError(f"Step number {step_number} is out of range for trip with {len(self.steps)} steps.")
        return self.steps[step_number - 1]


def load_trip_from_file(file: Path) -> Trip:  # noqa: D103
    if not file.exists():
        raise FileNotFoundError(f"File {file} does not exist.")
    trip_data_json = utils.load_json_from_file(file)
    trip = Trip.from_json(trip_data_json)
    trip.lookup_media_files(file.parent)
    return trip