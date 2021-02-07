"""API points."""
import datetime as dt

import fastapi

import db
import schemas

router = fastapi.APIRouter()


@router.get("/task", response_model=schemas.Task)
async def get_any_task():
    """
    Get random ask from the database.
    """

    mapa = db.Storage.get_mapa()
    geo = db.Storage.get_geo(geo_id=None)  # None -- get random

    if not geo or not mapa:
        raise fastapi.HTTPException(status_code=404)

    data = {
        "ts": dt.datetime.now().timestamp(),
        "id": geo.id,
        "text": geo.name,
        "mapa": {
            "path": mapa.path,
            "id": mapa.id,
            "w": mapa.w,
            "h": mapa.h,
            "projection": mapa.projection,
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
    mapa = db.Storage.get_mapa(mapa_id=answer.mapa_id)

    if not geo or not mapa:
        raise fastapi.HTTPException(status_code=404)

    lng0, lat0 = mapa.project_lnglat(answer.x, answer.y)
    distance = geo.distance(lng0, lat0)
    x, y = mapa.project_xy(geo)

    data = {"rc": 0, "distance": distance, "x": x, "y": y}

    return data
