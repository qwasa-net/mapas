"""API points."""
import datetime as dt

import fastapi

import db
import schemas
import settings

router = fastapi.APIRouter()

media_base = settings.get("media_base", "media/")


@router.get("/task", response_model=schemas.Task)
async def get_any_task():
    """
    Get random ask from the database.
    """

    geo = db.Storage.get_geo(geo_id=None)  # None -- get random

    if not geo:
        raise fastapi.HTTPException(status_code=404)

    data = {
        "ts": dt.datetime.now().timestamp(),
        "id": geo.id,
        "text": geo.name,
        "mapa": {
            "path": media_base + geo.mapa.path,
            "id": geo.mapa.id,
            "w": geo.mapa.w,
            "h": geo.mapa.h,
            "projection": geo.mapa.projection,
        },
    }

    return data


@router.post("/answer", response_model=schemas.Result)
async def check_answer(answer: schemas.Answer) -> schemas.Result:
    """
    Check the Answer.
    Fetch the geo point, calculate distance and score.
    """

    geo = db.Storage.get_geo(geo_id=answer.task_id)

    if not geo:
        raise fastapi.HTTPException(status_code=404)

    lng0, lat0 = geo.project_lnglat(answer.x, answer.y)
    distance = geo.distance(lng0, lat0)
    x, y = geo.project_xy()

    data = {"rc": 0, "distance": distance, "x": x, "y": y}

    return data
