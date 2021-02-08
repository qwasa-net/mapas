"""demodb builder"""
import logging
import db
import models


def generate_cities():
    mapa_data = {
        "name": "world map (equirectangular)",
        "w": 2160, "h": 1080,
        "path": "equirectangular.svg",
        "projection": 2,
        "type": 1
    }
    geo_data = [
        {"name": "SPB", "lng": 30.33509, "lat": 59.93428},
        {"name": "Mexico", "lng": -99.133208, "lat": 19.432608},
        {"name": "BKK", "lng": 100.750112, "lat": 13.689999},
        {"name": "Santiago", "lng": -70.673676, "lat": -33.447487},
        {"name": "london", "lng": -0.118092, "lat": 51.509865},
        {"name": "NY", "lng": -73.935242, "lat": 40.730610},
        {"name": "Z", "lng": 0, "lat": 0}
    ]
    return mapa_data, geo_data


def generate_testscreen(W=1280, H=720, N=5):
    mapa_data = {
        "name": "testscreen",
        "w": W,
        "h": H,
        "path": "testscreen.svg",
        "projection": 1,
        "type": 2
    }
    geo_data = []
    for i in range(N):
        for j in range(N):
            geo = {
                "name": f"{i}×{j}",
                "lng": W / N * (i + 0.5),
                "lat": H / N * (j + 0.5)
            }
            geo_data.append(geo)
    return mapa_data, geo_data


def main():
    """demodb builder"""

    db.DBStorage.connect(url="sqlite:///./db.sqlite", args={"check_same_thread": False})
    db.DBStorage.create_tables()
    db.DBStorage.show_tables()

    mapa_data, geo_data = generate_testscreen()
    mapa = models.Mapa(**mapa_data)
    db.DBStorage.save(mapa)
    for d in geo_data:
        geo = models.Geo(name=d['name'], lat=d["lat"], lng=d["lng"], mapa=mapa)
        db.DBStorage.save(geo)

    mapa_data, geo_data = generate_cities()
    mapa = models.Mapa(**mapa_data)
    db.DBStorage.save(mapa)
    for d in geo_data:
        geo = models.Geo(name=d['name'], lat=d["lat"], lng=d["lng"], mapa=mapa)
        db.DBStorage.save(geo)


if __name__ == "__main__":
    main()
