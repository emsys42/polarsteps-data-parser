import os
import sys
from pathlib import Path
from typing import Optional

import click
from loguru import logger

import polarsteps_data_parser.utils as utils
from polarsteps_data_parser.map_generator import MapGenerator
from polarsteps_data_parser.model import Location, Step, Trip
from polarsteps_data_parser.pdf_generator import PDFGenerator


class Const:
    """Application constants."""

    ALL_STEPS_KEYWORD = "all"
    ZOOM_LEVEL_SINGLE_STEP_VIEW_DEFAULT = 7
    ZOOM_LEVEL_SINGLE_STEP_VIEW_MIN = 0
    ZOOM_LEVEL_SINGLE_STEP_VIEW_MAX = 19
    IMAGE_SIZE_X_DEFAULT = 800
    IMAGE_SIZE_Y_DEFAULT = 600


class UserConfig:
    """User configuration constants."""

    def __init__(self, input_folder: str, output_folder: str, zoom_factor: str, image_pixel_size: str, step_numbers_to_process: list[int]) -> None:
        self._input_folder = input_folder
        self._output_folder = output_folder
        self._zoom_factor = int(zoom_factor)
        self._image_pixel_width, self._image_pixel_height = utils.decode_image_size(image_pixel_size)
        self._trip_map_filename_pattern = "trip_map.png"
        self._step_map_filename_pattern = "step_{step_number}_map.png"
        self._step_numbers_to_process = step_numbers_to_process

    @property
    def input_folder(self) -> str:  # noqa: D102
        return self._input_folder

    @property
    def output_folder(self) -> str:  # noqa: D102
        return self._output_folder

    @property
    def zoom_factor(self) -> int:  # noqa: D102
        return self._zoom_factor

    @property
    def image_pixel_width(self) -> int:  # noqa: D102
        return self._image_pixel_width

    @property
    def image_pixel_height(self) -> int:  # noqa: D102
        return self._image_pixel_height

    @property
    def ratio_x_over_y(self) -> float:  # noqa: D102
        return self.image_pixel_width / self.image_pixel_height

    @property
    def trip_map_filename_pattern(self) -> str:  # noqa: D102
        return self._trip_map_filename_pattern

    @property
    def step_map_filename_pattern(self) -> str:  # noqa: D102
        return self._step_map_filename_pattern

    @property
    def step_numbers_to_process(self) -> list[int]: # noqa: D102
        return self._step_numbers_to_process


def validate_zoom_factor(ctx, param, value) -> Optional[str]:
    """Validate zoom token where N is a number between ZOOM_LEVEL_SINGLE_STEP_VIEW_[MIN/MAX]."""
    try:
        zoom_factor = int(value)
    except ValueError:
        raise click.BadParameter(f"Zoom factor must be an integer. Given '{value}'.")

    if zoom_factor < Const.ZOOM_LEVEL_SINGLE_STEP_VIEW_MIN or zoom_factor > Const.ZOOM_LEVEL_SINGLE_STEP_VIEW_MAX:
        raise click.BadParameter(
            f"""Invalid zoom factor '{zoom_factor}'. It must be a number in range [{Const.ZOOM_LEVEL_SINGLE_STEP_VIEW_MIN} and {Const.ZOOM_LEVEL_SINGLE_STEP_VIEW_MAX}]."""
        )
    return value


def validate_image_size(ctx, param, value) -> Optional[str]:
    """Validate image size option value in format 'WIDTHxHEIGHT'."""
    try:
        _, _ = utils.decode_image_size(value)
    except ValueError:
        raise click.BadParameter(
            f"Image size must be in format 'WIDTHxHEIGHT' with positive integers. Given '{value}'."
        )
    return value


def validate_option_filter(ctx, param, value) -> Optional[str]:
    """Validate the step_map option value."""
    try:
        value = value.strip().lower()
        if value == Const.ALL_STEPS_KEYWORD:
            return value
        _ = utils.decode_step_filter(value)
    except ValueError as e:
        raise click.BadParameter(e)
    return value


def validate_option_map(ctx, param, value) -> Optional[str]:
    """Validate the generate_maps option value.

    Possible values are:
     --map trip: Create exactly one map for the entire trip:
                 Add a marker for each step (with respect to filter)´
     --map trip,wl: Same as 'trip' but additional add a line to marker of preceding step
     --map step: Create a map for each step (with respect to filter) with a marker for this step only
                 May be combine with '--zoom'.
    """
    if value is None:
        return value
    allowed_values = ["step", "trip", "wl"]
    value = value.strip().lower()
    for token in value.split(","):
        if token not in allowed_values:
            raise click.BadParameter(f"Invalid value for --map option. Allowed values are: {', '.join(allowed_values)}")
    return value


@click.command()
@click.option(
    "--input-folder",
    "input_folder",
    type=click.Path(exists=True),
    required=True,
    help="""The folder which contains 'trip.json' and 'locations.json'.
    It's inside the Polarsteps data export of a single trip.""",
)
@click.option(
    "--output-folder",
    "output_folder",
    type=click.Path(exists=True),
    is_flag=False,
    default=os.getcwd(),
    help="The folder where to create artefacts. If not specified, the current working directory is used.",
)
@click.option(
    "--pdf",
    "pdf_filename",
    is_flag=False,
    default=None,
    help="Whether to generate a PDF. Specify name of PDF file to create.",
)
@click.option(
    "--map",
    "generate_maps",
    is_flag=False,
    default=None,
    help="""Generate maps for selected steps. Possible values are a comma-separated list of:
     'step' to generate a map for each step.
     'trip' to generate a single map for the entire trip.
     'wl' to add walking line between steps. In combination with 'trip' only""",
    callback=validate_option_map,
)
@click.option(
    "--zoom",
    "zoom_factor",
    is_flag=False,
    default=str(Const.ZOOM_LEVEL_SINGLE_STEP_VIEW_DEFAULT),
    help=f"Specify zoom factor in range [{Const.ZOOM_LEVEL_SINGLE_STEP_VIEW_MIN} "
    + f"and {Const.ZOOM_LEVEL_SINGLE_STEP_VIEW_MAX}]. Only used in combination with '--map step'.",
    callback=validate_zoom_factor,
    show_default=True,
)
@click.option(
    "--image-size",
    "image_size_x_y",
    is_flag=False,
    default=f"{Const.IMAGE_SIZE_X_DEFAULT}x{Const.IMAGE_SIZE_Y_DEFAULT}",
    help="Specify image size in pixel when creating maps in format WIDTHxHEIGHT. Used in combination with '--map'.",
    callback=validate_image_size,
    show_default=True,
)
@click.option("--stat", "statistics", is_flag=True, default=False, help="Print statistic of input files.", type=bool)
@click.option(
    "--filter",
    "step_filter",
    is_flag=False,
    default=Const.ALL_STEPS_KEYWORD,
    help="Specify which steps to process as list (e.g. '2,6') or range (e.g. '5-7') or combinations thereof. "
    "Otherwise all existing steps are processed.",
    callback=validate_option_filter,
    show_default=True,
)
@click.option(
    "--log",
    "loglevel",
    is_flag=False,
    default=None,
    help="Produce detailed output.",
    type=click.Choice(["INFO", "DEBUG"]),
)
def cli(
    input_folder: str,
    output_folder: str,
    pdf_filename: str,
    loglevel: str,
    statistics: bool,
    step_filter: str,
    generate_maps: bool,
    zoom_factor: int,
    image_size_x_y: str,
) -> None:
    """Entry point for the application."""
    # note: its ensured that both folders <input_folder> and <output_folder> exist by click options

    configure_logger(loglevel)

    trip = load_trip_data(Path(input_folder), "trip.json")
    locations = load_location_data(Path(input_folder), "locations.json")

    config = UserConfig(input_folder, output_folder, zoom_factor, image_size_x_y, calulate_steps_to_process(step_filter, trip))

    if statistics:
        generate_statistics(trip, locations)

    if pdf_filename is not None:
        generate_pdf(config, trip, pdf_filename)

    if generate_maps and "step" in generate_maps:
        generate_distinct_map_for_selected_steps(config, trip)

    if generate_maps and "trip" in generate_maps:
        generate_single_map_for_selected_steps(config, trip, generate_maps)


def generate_statistics(trip: Trip, locations: list[MapGenerator.GPSPoint]) -> None:  # noqa: D103
    """Generate and print statistics about the trip and location data."""
    click.echo(f"Trip name: {trip.name}")
    click.echo(f"Number of steps: {len(trip.steps)}")
    total_photos = sum(len(step.photos) for step in trip.steps)
    total_videos = sum(len(step.videos) for step in trip.steps)
    click.echo(f"Total photos: {total_photos}")
    click.echo(f"Total videos: {total_videos}")
    click.echo(f"Number of GPS points in locations file: {len(locations)}")


def generate_pdf(config: UserConfig, trip: Trip, filename: str) -> None:  # noqa: D103
    output_path = Path(os.path.join(config.output_folder, filename))
    progress_bar = click.progressbar(
        length=len(config.step_numbers_to_process),
        label=f"Generating PDF for {len(config.step_numbers_to_process)} steps into {output_path}",
    )
    pdf_generator = PDFGenerator(output_path.as_posix())
    pdf_generator.generate_pdf(trip, progress_bar, config.step_numbers_to_process)


def generate_distinct_map_for_selected_steps(config: UserConfig, trip: Trip) -> None:  # noqa: D103
    progress_bar = click.progressbar(
        length=len(config.step_numbers_to_process),
        label=f"Generating maps for {len(config.step_numbers_to_process)} steps into folder {config.output_folder}",
    )
    with progress_bar as visible_bar:
        for zero_based_index, step_number in enumerate(config.step_numbers_to_process):
            step = trip.get_step(step_number)
            generate_distinct_map_for_selected_step(config, step_number, step)
            visible_bar.update(zero_based_index + 1)


def generate_distinct_map_for_selected_step(config: UserConfig, step_number: int, step: Step) -> None:  # noqa: D103
    filename = config.step_map_filename_pattern.format(step_number=step_number)
    output_path = Path(os.path.join(config.output_folder, filename))
    logger.debug(f"Generating map for step {step_number} into {output_path}")
    map_generator: MapGenerator = build_map_generator(config, "SINGLE_STEP_VIEW")
    gps_point = MapGenerator.GPSPoint(lat=step.location.lat, lon=step.location.lon)
    map_generator.add_location_marker(gps_point, marker_size=12)
    map_generator.write_to_png(output_path)


def generate_single_map_for_selected_steps(config: UserConfig, trip: Trip, generate_maps: str) -> None:  # noqa: D103
    output_path = Path(os.path.join(config.output_folder, config.trip_map_filename_pattern))
    logger.info(f"Generating map for selected steps into {output_path}")

    progress_bar = click.progressbar(
        length=1,
        label=f"Generating map for selected steps into {output_path}",
    )
    with progress_bar as visible_bar:
        map_generator: MapGenerator = build_map_generator(config, "SATELLITE_VIEW")
        gps_tuples = []
        for step_number in config.step_numbers_to_process:
            step_location = trip.get_step(step_number).location
            gps_tuples.append((step_location.lat, step_location.lon))
        gps_points = MapGenerator.GPSPoint.from_tuples(gps_tuples)
        if "wl" in generate_maps:
            map_generator.set_symbol_color(MapGenerator.BLUE)
            map_generator.add_multi_line(gps_points, width=4)
        map_generator.add_location_markers(gps_points, marker_size=12)
        map_generator.write_to_png(output_path)
        visible_bar.update(1)


def build_map_generator(config: UserConfig, style: str) -> MapGenerator:  # noqa: D103
    map_generator = None
    match style:
        case "SINGLE_STEP_VIEW":
            map_generator = MapGenerator(MapGenerator.PROVIDER_OSM)
            map_generator.set_zoom(config.zoom_factor)
            map_generator.set_image_properties(config.image_pixel_width, config.ratio_x_over_y)

        case "SATELLITE_VIEW":
            map_generator = MapGenerator(MapGenerator.PROVIDER_ARCGISWORLDIMAGERY)
            # Don't specify zoom factor. Generator will select a suitable one.
            map_generator.set_image_properties(config.image_pixel_width, config.ratio_x_over_y)

        case _:
            raise ValueError(f"Unknown map style '{style}'")

    return map_generator


def configure_logger(loglevel: str) -> None:  # noqa: D103
    logger.remove()
    if loglevel is not None:
        requested_level = loglevel
        logger.add(sys.stderr, level=requested_level)
        logger.debug(f"logger set to loglevel '{loglevel}'")


def calulate_steps_to_process(step_filter: str, trip: Trip) -> list[int]:  # noqa: D103
    if step_filter == Const.ALL_STEPS_KEYWORD:
        steps_to_process = range(1, len(trip.steps) + 1)
    else:
        steps_to_process = utils.decode_step_filter(step_filter)
    min_step_to_process = steps_to_process[0]
    max_step_to_process = steps_to_process[-1]
    if min_step_to_process < 1:
        raise ValueError(f"Filter is invalid. Step number must be >= 1. Given '{min_step_to_process}'.")
    if max_step_to_process > len(trip.steps):
        raise ValueError(
            f"Filter is invalid. Given step number '{max_step_to_process}' exceeds the number \
            of existing ({len(trip.steps)}) steps."
        )
    return steps_to_process


def load_location_data(input_folder: Path, trip_data_json_filename: str) -> list[Location]:  # noqa: D103
    location_data_json_file = Path(os.path.join(input_folder, trip_data_json_filename))
    if not location_data_json_file.exists():
        raise FileNotFoundError(f"File '{location_data_json_file}' does not exist.")
    location_data_json = utils.load_json_from_file(location_data_json_file)
    locations = [Location.from_json(data) for data in location_data_json["locations"]]
    return locations


def load_trip_data(input_folder: Path, trip_data_json_filename: str) -> Trip:  # noqa: D103
    trip_data_json_file = Path(os.path.join(input_folder, trip_data_json_filename))
    if not trip_data_json_file.exists():
        raise FileNotFoundError(f"File {trip_data_json_file} does not exist.")
    trip_data_json = utils.load_json_from_file(trip_data_json_file)
    trip = Trip.from_json(trip_data_json)
    trip.lookup_media_files(input_folder)
    return trip


if __name__ == "__main__":
    cli()
