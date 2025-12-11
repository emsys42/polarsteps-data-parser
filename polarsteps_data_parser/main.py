import os
import sys
from pathlib import Path

import click
from loguru import logger

from polarsteps_data_parser.map_generator import MapGenerator
from polarsteps_data_parser.model import Location, Trip, Step
from polarsteps_data_parser.pdf_generator import PDFGenerator
import polarsteps_data_parser.utils as utils

ALL_STEPS_KEYWORD = "all"


def validate_selected_steps(ctx, param, value) -> str | None:
    """Validate the step_map option value."""
    if value is None:
        return ALL_STEPS_KEYWORD
    try:
        value = value.strip().lower()
        if value == ALL_STEPS_KEYWORD:
            return value
        _ = utils.decode_step_filter(value)
    except ValueError as e:
        raise click.BadParameter(e)
    return value


@click.command()
@click.option(
    "--input-folder",
    "input_folder",
    type=click.Path(exists=True),
    required=True,
    help="""
    The input folder should contain the Polarsteps data export of a single trip. This folder contains
    both `trip.json` and `locations.json`.""",
)
@click.option(
    "--output-folder",
    "output_folder",
    is_flag=False,
    default=None,
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
    "--log",
    "loglevel",
    is_flag=False,
    default=None,
    help="Produce detailed output.",
    type=click.Choice(["INFO", "DEBUG"]),
)
@click.option(
    "--filter",
    "step_filter",
    is_flag=False,
    # maybe use  'flag_value=ALL_STEPS_KEYWORD,' in combination with '# default=None'
    default=None,
    help="Specify which steps to process as list (e.g. '2,6') or range (e.g. '5-7') or combinations thereof. " \
    "Otherwise all existing steps are processed.",
    callback=validate_selected_steps,
)
@click.option(
    "--map", "generate_maps", is_flag=True, default=False, help="Generate maps for selected steps.", type=bool
)
@click.option("--stat", "statistics", is_flag=True, default=False, help="Print statistic of input files.", type=bool)
def cli(
    input_folder: str,
    output_folder: str,
    pdf_filename: str,
    loglevel: str,
    statistics: bool,
    step_filter: str,
    generate_maps: bool,
) -> None:
    """Entry point for the application."""
    configure_logger(loglevel)

    if not Path(input_folder).exists():
        raise FileNotFoundError(f"Folder {input_folder} does not exist.")

    if output_folder is None:
        output_folder = os.getcwd()
        logger.debug(f"No output folder specified. Using current working directory: {output_folder}")
    else:
        if not Path(output_folder).exists():
            raise FileNotFoundError(f"Folder {output_folder} does not exist.")

    # Load and process trip data
    trip = load_trip_data(Path(input_folder), "trip.json")

    # Load and process locations data
    locations = load_location_data(Path(input_folder), "locations.json")

    if statistics:
        generate_statistics(trip, locations)

    steps_to_process = calulate_steps_to_process(step_filter, trip)

    if pdf_filename is not None:
        generate_pdf(trip, output_folder, pdf_filename, steps_to_process)

    if generate_maps:
        generate_maps_for_steps(output_folder, trip, steps_to_process)


def generate_statistics(trip: Trip, locations: list[MapGenerator.GPSPoint]) -> None:  # noqa: D103
    """Generate and print statistics about the trip and location data."""
    click.echo(f"Trip name: {trip.name}")
    click.echo(f"Number of steps: {len(trip.steps)}")
    total_photos = sum(len(step.photos) for step in trip.steps)
    total_videos = sum(len(step.videos) for step in trip.steps)
    click.echo(f"Total photos: {total_photos}")
    click.echo(f"Total videos: {total_videos}")
    click.echo(f"Number of GPS points in locations file: {len(locations)}")


def generate_pdf(trip: Trip, output_path: Path, filename: str, steps_to_process: list[int]) -> None:  # noqa: D103
    output_file = Path(os.path.join(output_path, filename))
    progress_bar = click.progressbar(
        length=len(steps_to_process), label=f"Generating PDF for {len(steps_to_process)} steps into {output_file}"
    )
    pdf_generator = PDFGenerator(output_file.as_posix())
    pdf_generator.generate_pdf(trip, progress_bar, steps_to_process)


def generate_maps_for_steps(output_folder: str, trip: Trip, steps_to_process: list[int]) -> None:  # noqa: D103
    progress_bar = click.progressbar(
        length=len(steps_to_process),
        label=f"Generating maps for {len(steps_to_process)} steps into folder {output_folder}",
    )
    with progress_bar as visible_bar:
        for number_of_step_to_generate in steps_to_process:
            index_of_step_to_generate = number_of_step_to_generate - 1
            step = trip.steps[index_of_step_to_generate]
            generate_map_for_step(output_folder, number_of_step_to_generate, step)
            visible_bar.update(number_of_step_to_generate)


def generate_map_for_step(output_folder: str, number_of_step_to_generate: int, step: Step) -> None:  # noqa: D103
    if step is None:
        raise RuntimeError(f"Step {number_of_step_to_generate} not found in trip data. This should not happen.")
    logger.debug(f"Generating map for step {number_of_step_to_generate} at location {step.location}")
    map_generator = MapGenerator(MapGenerator.PROVIDER_OSM)
    map_generator.set_zoom(8)
    map_generator.set_image_properties(width_pixels=1200, ratio_y_over_x=2 / 3)
    map_generator.set_symbol_color(MapGenerator.RED)
    gps_point = MapGenerator.GPSPoint(lat=step.location.lat, lon=step.location.lon)
    map_generator.add_location_marker(gps_point, marker_size=12)
    output_map_path = Path(os.path.join(output_folder, f"step_{number_of_step_to_generate}_map.png"))
    map_generator.write_to_png(output_map_path)
    logger.info(f"Map for step {number_of_step_to_generate} written to {output_map_path}")


def configure_logger(loglevel: str) -> None:  # noqa: D103
    logger.remove()
    if loglevel is not None:
        requested_level = loglevel
        logger.add(sys.stderr, level=requested_level)
        logger.debug(f"logger set to loglevel '{loglevel}'")


def calulate_steps_to_process(step_filter: str, trip: Trip) -> list[int]:  # noqa: D103
    if step_filter == ALL_STEPS_KEYWORD:
        steps_to_generate = range(1, len(trip.steps) + 1)
    else:
        steps_to_generate = utils.decode_step_filter(step_filter)
    min_step_to_generate = steps_to_generate[0]
    max_step_to_generate = steps_to_generate[-1]
    if min_step_to_generate < 1:
        raise ValueError(f"Filter is invalid. Step number must be >= 1. Given '{min_step_to_generate}'.")
    if max_step_to_generate > len(trip.steps):
        raise ValueError(
            f"Filter is invalid. Given step number '{max_step_to_generate}' exceeds the number \
            of existing ({len(trip.steps)}) steps."
        )
    return steps_to_generate


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
