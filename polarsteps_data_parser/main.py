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


def validate_option_filter(ctx, param, value) -> str | None:
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

def validate_option_map(ctx, param, value) -> bool:
    """Validate the generate_maps option value.
    Possible values are:
     --map trip: Genau eine Map generieren:
                    Einem Marker für jedem Step (filter beachten) hinzufügen
                    Optional Linie zum vorherigen Step hinzufügen  
     --map step: Für jeden Step (filter beachten):
                    Eine Map mit genau einem Marker für den Step generieren
     --map trip,wl: <trip> + Linie zum vorherigen Step hinzufügen  
    """
    if value is None:
        return value
    allowed_values = ["step", "trip", "wl"]
    value = value.strip().lower()
    for token in value.split(","):
        if token not in allowed_values:
            raise click.BadParameter(
                f"Invalid value for --map option. Allowed values are: {', '.join(allowed_values)}"
            )
    return value

@click.command()
@click.option(
    "--input-folder",
    "input_folder",
    type=click.Path(exists=True),
    required=True,
    help="""The folder which contains `trip.json` and `locations.json`.
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
     'wl' to add walking line between steps.""", 
     callback=validate_option_map,
)
@click.option("--stat", "statistics", is_flag=True, default=False, help="Print statistic of input files.", type=bool)
@click.option(
    "--filter",
    "step_filter",
    is_flag=False,
    # maybe use  'flag_value=ALL_STEPS_KEYWORD,' in combination with '# default=None'
    default=None,
    help="Specify which steps to process as list (e.g. '2,6') or range (e.g. '5-7') or combinations thereof. " \
    "Otherwise all existing steps are processed.",
    callback=validate_option_filter,
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
) -> None:
    """Entry point for the application."""
    # note: its ensured that both folders <input_folder> and <output_folder> exist by click options

    configure_logger(loglevel)

    trip = load_trip_data(Path(input_folder), "trip.json")
    locations = load_location_data(Path(input_folder), "locations.json")

    if statistics:
        generate_statistics(trip, locations)

    steps_to_process = calulate_steps_to_process(step_filter, trip)

    if pdf_filename is not None:
        generate_pdf(trip, output_folder, pdf_filename, steps_to_process)

    if generate_maps and "step" in generate_maps:
        generate_distinct_map_for_selected_steps(output_folder, steps_to_process)

    if generate_maps and "trip" in generate_maps:
        generate_single_map_for_selected_steps(output_folder, generate_maps, steps_to_process)


def generate_statistics(trip: Trip, locations: list[MapGenerator.GPSPoint]) -> None:  # noqa: D103
    """Generate and print statistics about the trip and location data."""
    click.echo(f"Trip name: {trip.name}")
    click.echo(f"Number of steps: {len(trip.steps)}")
    total_photos = sum(len(step.photos) for step in trip.steps)
    total_videos = sum(len(step.videos) for step in trip.steps)
    click.echo(f"Total photos: {total_photos}")
    click.echo(f"Total videos: {total_videos}")
    click.echo(f"Number of GPS points in locations file: {len(locations)}")


def generate_pdf(trip: Trip, output_path: Path, filename: str, steps_to_process: list[Step]) -> None:  # noqa: D103
    output_file = Path(os.path.join(output_path, filename))
    progress_bar = click.progressbar(
        length=len(steps_to_process), label=f"Generating PDF for {len(steps_to_process)} steps into {output_file}"
    )
    pdf_generator = PDFGenerator(output_file.as_posix())
    pdf_generator.generate_pdf(trip, progress_bar, steps_to_process)


def generate_distinct_map_for_selected_steps(output_folder: str, steps_to_process: list[Step]) -> None:  # noqa: D103
    progress_bar = click.progressbar(
        length=len(steps_to_process),
        label=f"Generating maps for {len(steps_to_process)} steps into folder {output_folder}",
    )
    with progress_bar as visible_bar:
        for i, step_to_process in enumerate(steps_to_process):
            generate_distinct_map_for_selected_step(output_folder, i+1, step_to_process)
            visible_bar.update(i)


def generate_distinct_map_for_selected_step(output_folder: str, number_of_step: int, step: Step) -> None:  # noqa: D103
    output_map_path = Path(os.path.join(output_folder, f"step_{number_of_step}_map.png"))
    logger.debug(f"Generating map for step {number_of_step} into {output_map_path}")
    map_generator: MapGenerator = build_map_generator("DETAIL_VIEW")
    gps_point = MapGenerator.GPSPoint(lat=step.location.lat, lon=step.location.lon)
    map_generator.add_location_marker(gps_point, marker_size=12)
    map_generator.write_to_png(output_map_path)


def generate_single_map_for_selected_steps(output_folder:str, generate_maps:str, steps_to_process:Step)-> None:  # noqa: D103
    output_map_path = Path(os.path.join(output_folder, "trip_map.png"))
    logger.info(f"Generating map for selected steps into {output_map_path}")

    progress_bar = click.progressbar(
        length=1,
        label=f"Generating map for selected steps into {output_map_path}",
    )
    with progress_bar as visible_bar:
        map_generator: MapGenerator = build_map_generator("SATTELITE_VIEW")
        gps_points = MapGenerator.GPSPoint.from_tuples(
                [(step.location.lat, step.location.lon) for step in steps_to_process]
            )
        if "wl" in generate_maps:
            map_generator.set_symbol_color(MapGenerator.BLUE)
            map_generator.add_multi_line(gps_points, width=4)

        map_generator.add_location_markers(gps_points, marker_size=12)
        map_generator.write_to_png(output_map_path)
        visible_bar.update(1)


def build_map_generator(style:str) -> MapGenerator:  # noqa: D103
    map_generator = None
    match style:
        case "DETAIL_VIEW":
            # maybe load different map styles based on config
            map_generator = MapGenerator(MapGenerator.PROVIDER_OSM)
            map_generator.set_zoom(3)
            map_generator.set_image_properties(width_pixels=1200, ratio_y_over_x=2 / 3)

        case "SATTELITE_VIEW":
            map_generator = MapGenerator(MapGenerator.PROVIDER_ARCGISWORLDIMAGERY)
            # let generator select a suitable zoom level
        case _:
            raise ValueError(f"Unknown map style '{style}'")

    return map_generator

def configure_logger(loglevel: str) -> None:  # noqa: D103
    logger.remove()
    if loglevel is not None:
        requested_level = loglevel
        logger.add(sys.stderr, level=requested_level)
        logger.debug(f"logger set to loglevel '{loglevel}'")


def calulate_steps_to_process(step_filter: str, trip: Trip) -> list[Step]:  # noqa: D103
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
    return [trip.steps[i-1] for i in steps_to_generate]


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
