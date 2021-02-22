"""pydantic schemas."""
from typing import Optional

import pydantic


class Mapa(pydantic.BaseModel):
    """pydantic schema for DB Map model."""

    id: int
    path: str
    projection: Optional[int]
    w: Optional[int]
    h: Optional[int]


class Geo(pydantic.BaseModel):
    """pydantic schema for DB Geo model."""

    id: Optional[int]
    name: str
    lat: float
    lng: float
    poly: str
    extra: str


class Task(pydantic.BaseModel):
    """pydantic schema for API Task."""

    id: int
    ts: int
    text: str
    mapa: Mapa


class Answer(pydantic.BaseModel):
    """pydantic schema for API Answer."""

    x: float
    y: float
    task_id: int


class Result(pydantic.BaseModel):
    """pydantic schema for API Result."""

    x: float
    y: float
    distance: float
    score: Optional[int]
    rc: int
