import json
import os
from datetime import datetime
from pathlib import Path


def load_json_from_file(path: Path) -> dict:
    """Load content from file and convert to JSON object.

    Args:
        path: path to file

    Returns:
        dict: parsed JSON
    """
    with open(path, "r") as file:
        return json.load(file)


def parse_date(date: str) -> datetime:
    """Convert a string containing a timestamp to a datetime object.

    Args:
        date: unix timestamp

    Returns:
        datetime: timestamp parsed to a datetime object

    """
    timestamp = float(date)
    date_time = datetime.fromtimestamp(timestamp)
    return date_time


def find_folder_by_id(folder_id: str, input_folder: Path) -> Path | None:
    """Finds and returns the path of a folder within the base_directory that matches the given folder_id."""
    if input_folder.exists() is False:
        return None

    for folder in input_folder.iterdir():
        if folder.is_dir() and folder.name.endswith(f"_{folder_id}"):
            return folder

    return None


def find_media_files_of_step(step_id: str, input_folder: Path) -> None:
    """Load photos and videos for a given step."""
    found_photos = []
    found_videos = []
    media_dir = find_folder_by_id(step_id, input_folder)
    if media_dir is not None:
        found_photos = list_files_in_folder(os.path.join(media_dir, "photos"), dir_has_to_exist=False)
        found_videos = list_files_in_folder(os.path.join(media_dir, "videos"), dir_has_to_exist=False)
    return found_photos, found_videos


def list_files_in_folder(folder_path: Path, dir_has_to_exist: bool = True) -> list[Path]:
    """List all files in the given folder.

    Args:
        folder_path (str or Path): The path of the folder to list files from.
        dir_has_to_exist (bool): raise exception if path does not exist.

    Returns:
        List[Path]: A list of Path objects representing the files in the folder.

    """
    folder = Path(folder_path)

    if not folder.is_dir():
        if dir_has_to_exist:
            raise NotADirectoryError(f"{folder_path} is not a valid directory")
        return []

    return [file for file in folder.iterdir() if file.is_file()]
