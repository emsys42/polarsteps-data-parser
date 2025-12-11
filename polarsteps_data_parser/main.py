import click
import os
import sys
from loguru import logger
from pathlib import Path

from polarsteps_data_parser.model import Location, Trip
from polarsteps_data_parser.pdf_generator import PDFGenerator
from polarsteps_data_parser.utils import load_json_from_file


@click.command()
@click.option(
    "--input-folder",
    type=click.Path(exists=True),
    required=True,
    help="""
    The input folder should contain the Polarsteps data export of a single trip. Make sure the folder contains
    a `trip.json` and `locations.json`.""",
)
@click.option(
    "--pdf",
    "pdf_output_file",
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
@click.option("--stat", "statistics", is_flag=True, default=False, help="Print statistic of input files.", type=bool)
def cli(input_folder: str, pdf_output_file: str, loglevel: str, statistics: bool) -> None:
    """Entry point for the application."""
    configure_logger(loglevel)

    # Load and process trip data
    trip_data_path = Path(os.path.join(input_folder, "trip.json"))
    trip = load_trip_data(trip_data_path)

    # Load and process locations data
    location_data_path = Path(os.path.join(input_folder, "locations.json"))
    all_location = load_location_data(location_data_path)

    if statistics:
        click.echo(f"Trip name: {trip.name}")
        click.echo(f"Number of steps: {len(trip.steps)}")
        total_photos = sum(len(step.photos) for step in trip.steps)
        total_videos = sum(len(step.videos) for step in trip.steps)
        click.echo(f"Total photos: {total_photos}")
        click.echo(f"Total videos: {total_videos}")
        click.echo(f"Number of GPS points in locations file: {len(all_location)}")

    if pdf_output_file is not None:
        generate_pdf(trip, pdf_output_file)


def generate_pdf(trip: Trip, output_file: str) -> None:  # noqa: D103
    progress_bar = click.progressbar(
        length=len(trip.steps), label=f"Generating PDF for {len(trip.steps)} steps into {output_file}"
    )
    pdf_generator = PDFGenerator(output_file)
    pdf_generator.generate_pdf(trip, progress_bar)


def configure_logger(loglevel: str) -> None:  # noqa: D103
    logger.remove()
    if loglevel is not None:
        requested_level = loglevel
        logger.add(sys.stderr, level=requested_level)
        logger.debug(f"logger set to loglevel '{loglevel}'")


def load_location_data(path: Path) -> list[Location]:  # noqa: D103
    if not path.exists():
        raise FileNotFoundError(f"File '{path}' does not exist.")
    location_data = load_json_from_file(path)
    all_location = [Location.from_json(data) for data in location_data["locations"]]
    return all_location


def load_trip_data(path: Path) -> Trip:  # noqa: D103
    if not path.exists():
        raise FileNotFoundError(f"File {path} does not exist.")
    trip_data = load_json_from_file(path)
    trip = Trip.from_json(trip_data)
    return trip


if __name__ == "__main__":
    cli()
