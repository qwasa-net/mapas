"""sqlalchemy models definitions."""
import math

from sqlalchemy import JSON, Column, Float, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Geo(Base):
    """Geo -- geo object with mane and coordinates."""

    __tablename__ = "geos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=255), index=True)
    lat = Column(Float)
    lng = Column(Float)
    poly = Column(Text)
    extra = Column(JSON)

    def distance(self, lat: float, lng: float, radius: float = 6371) -> float:
        """
        Calculate the great circle distance between two points on the earth.

        lat,lng — specified in decimal degrees,
        radius = 6371  — radius of earth in kilometers(use 3956 for miles).
        src: https://stackoverflow.com/questions/4913349/
        """
        # convert decimal degrees to radians
        lng1, lat1, lng2, lat2 = map(math.radians, [self.lng, self.lat, lng, lat])
        # haversine formula
        dlon, dlat = lng2 - lng1, lat2 - lat1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        return c * radius


class Mapa(Base):
    """Mapa -- map image file."""

    __tablename__ = "mapas"

    # id and name of the map
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=255), index=True)

    # map projection type
    EQUIRECTANGULAR, MERCATOR = 1, 2
    projection = Column(Integer, default=EQUIRECTANGULAR)

    # map canvas file path (svg)
    path = Column(String(length=255), index=True)

    # map canvas width×height (ignore uncropped parts)
    w = Column(Integer, default=360)
    h = Column(Integer, default=180)

    # map canvas offset (x,y)
    ox = Column(Integer, default=0)
    oy = Column(Integer, default=0)

    def project_xy(self, geo: "Geo") -> (float, float):
        """Calculate a point (x,y) on the map canvas from geo coordinates."""

        if self.projection == Mapa.EQUIRECTANGULAR:
            x = (180 + geo.lng) / 360
            y = (90 - geo.lat) / 180
            return x, y

        if self.projection == Mapa.MERCATOR:
            raise Exception("not implemented yet!")

        raise Exception("unknown projection type!")

    def project_lnglat(self, x: float, y: float) -> (float, float):
        """Calculate geo coordinates from the point on the canvas (x,y)."""

        if self.projection == Mapa.EQUIRECTANGULAR:
            lng = -180 + x * 360
            lat = 90 - y * 180
            return lng, lat

        if self.projection == Mapa.MERCATOR:
            raise Exception("not implemented yet!")

        raise Exception("unknown projection type!")
