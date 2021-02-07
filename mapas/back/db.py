"""Storage (with some DB via SQLAlchemy)"""
import random
import typing

import sqlalchemy

from models import Base, Geo, Mapa


class DBStorage:
    """RDB-based storage. Note -- all main methods are class methods."""

    engine = None
    sess = None
    _cache_geos_size = 0

    def __init__(self):
        pass

    @classmethod
    def connect(cls, url: str, args: typing.Dict = None):
        """Connect to DataBase"""
        cls.engine = sqlalchemy.create_engine(url, connect_args=args or {})
        cls.sessmaker = sqlalchemy.orm.sessionmaker(bind=cls.engine,
                                                    autocommit=False,
                                                    autoflush=False)

    @classmethod
    def cache_geos_size(cls):
        """
        Get size of the Geos table to fetch random element fast.
        Should be updates every time new Geo object is added.
        """
        s = cls.sess or cls.sessmaker()
        cls._cache_geos_size = s.query(Geo).count()

    @classmethod
    def get_geo(cls, geo_id: typing.Optional[int] = None) -> Geo:
        """
        Get a Geo object by id, if geo_id is `None` -- get random object.
        Returns: Geo object or None if nothing found
        """

        s = cls.sess or cls.sessmaker()

        if not geo_id:
            if not cls._cache_geos_size:
                cls.cache_geos_size()
            geo_id = random.randrange(1, cls._cache_geos_size + 1)

        geo = s.query(Geo).filter(Geo.id == geo_id).first()

        return geo

    @classmethod
    def save_geo(cls, geo: Geo):
        """Save Goe object."""
        s = cls.sess or cls.sessmaker()
        s.add(geo)
        s.commit()

    @classmethod
    def get_mapa(cls, mapa_id: typing.Optional[int] = None) -> Mapa:
        """
        Get a Mapa object by id, if mapa_id is `None` -- get first one.
        Returns: Mapa object or None if nothing found.
        """

        s = cls.sess or cls.sessmaker()

        mapa = s.query(Mapa)
        if mapa_id is not None:
            mapa = mapa.filter(Mapa.id == mapa_id)

        return mapa.first()

    @classmethod
    def save_mapa(cls, mapa: Mapa):
        """Save Mapa object."""
        s = cls.sess or cls.sessmaker()
        s.add(mapa)
        s.commit()

    @classmethod
    def create_tables(cls):
        """Init database."""
        Base.metadata.create_all(cls.engine)

    @classmethod
    def drop_tables(cls):
        """Delete all tables from the database."""
        Base.metadata.drop_all(cls.engine)

    @classmethod
    def show_tables(cls):
        """Print all available tables."""
        for tbl in cls.engine.table_names():
            print(tbl)


class Storage(DBStorage):
    """
    Currently the only available storage is DataBase.
    """
