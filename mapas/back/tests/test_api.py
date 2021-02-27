"""Basic API tests (pytest)."""
import math

import db
import models
from fastapi.testclient import TestClient
from main import mapapp

client = TestClient(mapapp)

W, H, N = 100, 150, 100


def setup_module():
    """Tests setup -- init database"""
    # db.Storage.connect("sqlite:///:memory:", {})
    db.Storage.create_tables()
    mapa_data = {"name": "map", "w": W, "h": H, "path": "map.svg", "type": 2, "projection": 1}
    db.Storage.save(models.Mapa(**mapa_data))
    for i in range(N):
        geo_data = {"name": f"{i}", "lng": W / N * i, "lat": H / N * i, "mapa_id": 1}
        db.Storage.save(models.Geo(**geo_data))


def test_read_index():
    """Test GET / (index page)"""
    rsp = client.get("/")
    assert rsp.status_code == 404


def test_read_task():
    """Test GET /task (any random task)"""
    rsp = client.get("/api/task")
    assert rsp.status_code == 200
    data = rsp.json()
    assert 'id' in data
    assert 'text' in data
    assert 'mapa' in data
    assert 'path' in data['mapa']
    geo = db.Storage.get_geo(geo_id=data.get('id'))
    assert geo is not None
    return data, geo


def test_get_test_post_answer():
    """Test GET /task and POST /answer"""
    task, geo = test_read_task()
    x, y = geo.project_xy()
    answer = {"task_id": task.get('id'), "mapa_id": 0, "x": x, "y": y}
    rsp = client.post("/api/answer", json=answer)
    assert rsp.status_code == 200
    data = rsp.json()
    assert 'score' in data
    assert 'distance' in data
    assert data.get('distance') < 1e-5


def test_get_test_post_answer_offset():
    """Test GET /task and POST /answer"""
    # use geo.id=(0,0); post answer=(1,1)
    answer = {"task_id": 1, "x": 1, "y": 1}
    rsp = client.post("/api/answer", json=answer)
    assert rsp.status_code == 200
    data = rsp.json()
    assert 'score' in data
    assert 'distance' in data
    assert abs(data.get('distance') - math.sqrt(W**2 + H**2)) < 1e-5


def test_post_answer_badids():
    """Test POST /answer (bad ids)"""
    answer = {"task_id": -1, "x": 0.33, "y": 0.25}
    rsp = client.post("/api/answer", json=answer)
    assert rsp.status_code == 404


def test_post_answer_invalid():
    """Test POST /answer (invalid)"""
    rsp = client.post("/api/answer")
    assert rsp.status_code == 422


def test_read_all():
    """Test GET /task (get all tasks)"""
    task_ids = set()
    while len(task_ids) < N:
        rsp = client.get("/api/task")
        assert rsp.status_code == 200
        data = rsp.json()
        assert 'id' in data
        task_ids.add(data.get('id'))
