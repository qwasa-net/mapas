"""sqlalchemy models definitions."""
import math

from sqlalchemy import JSON, Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

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
    mapa_id = Column(Integer, ForeignKey('mapas.id'))
    mapa = relationship("Mapa", back_populates="geos")

    def project_xy(self) -> (float, float):
        """Calculate a point (x,y) on the map canvas from geo coordinates."""
        return self.mapa.project_xy(self.lng, self.lat)

    def project_lnglat(self, x: float = None, y: float = None) -> (float, float):
        """Calculate geo coordinates from the point on the canvas (x,y)."""
        return self.mapa.project_xy(x if x is not None else self.lng,
                                    y if y is not None else self.lat)

    def distance(self, lng: float, lat: float) -> float:
        """Get distanse for some (lng,lat) point"""
        return self.mapa.distance(self.lng, self.lat, lng, lat)


class Mapa(Base):
    """Mapa -- map image file."""

    __tablename__ = "mapas"

    # id and name of the map
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=255), index=True)

    # map projection type
    SQUARE, EQUIRECTANGULAR, MERCATOR = 1, 2, 3
    projection = Column(Integer, default=EQUIRECTANGULAR)

    WORLDMAP, CANVAS = 1, 2
    type = Column(Integer, default=CANVAS)

    # map canvas file path (svg)
    path = Column(String(length=255), index=True)

    # map canvas width×height (ignore uncropped parts)
    w = Column(Integer, default=360)
    h = Column(Integer, default=180)

    # map canvas offset (x,y)
    ox = Column(Integer, default=0)
    oy = Column(Integer, default=0)

    geos = relationship("Geo", back_populates="mapa")

    def project_xy(self, lng: float, lat: float) -> (float, float):
        """Calculate a point (x,y) on the map canvas from geo coordinates."""

        if self.projection == Mapa.SQUARE:
            x = lng / self.w
            y = lat / self.h
            return x, y

        if self.projection == Mapa.EQUIRECTANGULAR:
            x = (180 + lng) / 360
            y = (90 - lat) / 180
            return x, y

        if self.projection == Mapa.MERCATOR:
            raise Exception("not implemented yet!")

        raise Exception("unknown projection type!")

    def project_lnglat(self, x: float, y: float) -> (float, float):
        """Calculate geo coordinates from the point on the canvas (x,y)."""

        if self.projection == Mapa.SQUARE:
            lng = x * self.w
            lat = y * self.h
            return lng, lat

        if self.projection == Mapa.EQUIRECTANGULAR:
            lng = -180 + x * 360
            lat = 90 - y * 180
            return lng, lat

        if self.projection == Mapa.MERCATOR:
            raise Exception("not implemented yet!")

        raise Exception("unknown projection type!")

    def distance(self,
                 lat1: float, lng1: float,
                 lat2: float, lng2: float,
                 radius: float = 6371) -> float:
        """
        Calculate the great circle distance between two points on the earth.

        For World Maps:
        lat,lng — specified in decimal degrees,
        radius = 6371  — radius of earth in kilometers (use 3956 for miles).
        src: https://stackoverflow.com/questions/4913349/
        """

        if self.type == Mapa.CANVAS:
            return math.sqrt((lat1 - lat2)**2 + (lng1 - lng2)**2)

        if self.type == Mapa.WORLDMAP:
            # convert decimal degrees to radians
            lng1, lat1, lng2, lat2 = map(math.radians, [lng1, lat1, lng2, lat2])
            # haversine formula
            dlon, dlat = lng2 - lng1, lat2 - lat1
            a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
            c = 2 * math.asin(math.sqrt(a))
            return c * radius

        raise Exception("unknown map type!")
