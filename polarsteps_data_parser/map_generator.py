import staticmaps
from pathlib import Path
import s2sphere


class GPSPoint:
    """A geographical point defined by latitude and longitude."""

    def __init__(self, lat: float, lon: float) -> None:
        self._latlng = staticmaps.create_latlng(lat, lon)

    @classmethod
    def from_tuples(cls, tuples: list[tuple[float, float]]) -> list["MapGenerator.Point"]:
        """Convert list of (lat, lon) tuples to list of Point objects."""
        return [cls(lat=lat, lon=lon) for lat, lon in tuples]

    @property
    def latlng(self) -> s2sphere.LatLng: # noqa: D102
        return self._latlng

    @property
    def lat(self) -> float: # noqa: D102
        return self._latlng.lat

    @property
    def lon(self) -> float: # noqa: D102
        return self._latlng.lng


class MapGenerator:
    """Generates static maps with markers and lines using the staticmaps library."""
    GPSPoint = GPSPoint

    TRANSPARENT = staticmaps.TRANSPARENT
    BLACK = staticmaps.BLACK
    WHITE = staticmaps.WHITE
    BLUE = staticmaps.BLUE
    BROWN = staticmaps.BROWN
    GREEN = staticmaps.GREEN
    ORANGE = staticmaps.ORANGE
    PURPLE = staticmaps.PURPLE
    RED = staticmaps.RED
    YELLOW = staticmaps.YELLOW

    PROVIDER_OSM = staticmaps.tile_provider_OSM
    PROVIDER_ARCGISWORLDIMAGERY = staticmaps.tile_provider_ArcGISWorldImagery
    PROVIDER_CARTONOLABELS = staticmaps.tile_provider_CartoNoLabels
    PROVIDER_CARTODARKNOLABELS = staticmaps.tile_provider_CartoDarkNoLabels
    PROVIDER_NONE = staticmaps.tile_provider_None

    def __init__(self, provider: staticmaps.TileProvider) -> None:
        self._context = staticmaps.Context()
        self._context.set_tile_provider(provider)
        self._def_width = 800
        self._ratio = 1.0
        self._symbol_color = self.RED

    def set_image_properties(self, width_pixels: int, ratio_y_over_x: float) -> None:
        """Set the image size and ratio for the generated map."""
        self._def_width = width_pixels
        self._ratio = ratio_y_over_x

    def set_zoom(self, zoom: int) -> None:  # noqa: D102
        self._context.set_zoom(zoom)

    def set_symbol_color(self, color: staticmaps.Color) -> None:  # noqa: D102
        self._symbol_color = color

    def add_line(self, begin: GPSPoint, end: GPSPoint, width: int) -> None:  # noqa: D102
        self._context.add_object(staticmaps.Line([begin, end], color=self._symbol_color, width=width))

    def add_multi_line(self, locations: list[GPSPoint], width: int) -> None:  # noqa: D102
        if len(locations) < 2:
            raise ValueError("At least two points are required to add a line.")
        self._context.add_object(
            staticmaps.Line([loc.latlng for loc in locations], color=self._symbol_color, width=width)
        )

    def add_location_marker(self, location: GPSPoint, marker_size: int) -> None:  # noqa: D102
        marker = staticmaps.Marker(location.latlng, size=marker_size)
        self._context.add_object(marker)

    def add_location_markers(self, locations: list[GPSPoint], marker_size: int) -> None:  # noqa: D102
        for location in locations:
            self.add_location_marker(location, marker_size)

    def write_to_png(self, output_filepath: Path) -> None:  # noqa: D102
        map_image = self._context.render_cairo(self._def_width, int(self._def_width / self._ratio))
        filename = output_filepath.as_posix()
        map_image.write_to_png(filename)


def test_map_generation() -> None:  # noqa: D103
    SINGLE_STEP_MAP_MARKER_SIZE = 12

    generator = MapGenerator(MapGenerator.PROVIDER_OSM)
    generator.set_zoom(8)
    generator.set_image_properties(width_pixels=1200, ratio_y_over_x=2 / 3)
    generator.set_symbol_color(MapGenerator.RED)

    generator.add_location_marker(GPSPoint(lat=52, lon=5), marker_size=SINGLE_STEP_MAP_MARKER_SIZE)
    generator.add_location_marker(GPSPoint(lat=52, lon=6), marker_size=SINGLE_STEP_MAP_MARKER_SIZE)
    generator.set_symbol_color(MapGenerator.BLUE)
    gps_points = GPSPoint.from_tuples([(52, 7), (53, 8), (54, 8), (55, 10)])
    generator.add_multi_line(gps_points, width=4)
    generator.add_location_markers(gps_points, marker_size=SINGLE_STEP_MAP_MARKER_SIZE)

    generator.write_to_png(Path("test_map.png"))


if __name__ == "__main__":
    test_map_generation()
