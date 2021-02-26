"""
https://download.geonames.org/export/dump/
The data format is tab-delimited text in utf8 encoding.
"""

import sys

import db
import models
import settings


def read_city(infile):
    """
    Read citiesXXXX.txt, put into list, sort by population.


    The main 'geoname' table has the following fields :
    ---------------------------------------------------
    geonameid         : integer id of record in geonames database
    name              : name of geographical point (utf8) varchar(200)
    asciiname         : name of geographical point in plain ascii characters, varchar(200)
    alternatenames    : alternatenames, comma separated, ascii names automatically transliterated, …
    latitude          : latitude in decimal degrees (wgs84)
    longitude         : longitude in decimal degrees (wgs84)
    feature class     : see http://www.geonames.org/export/codes.html, char(1)
    feature code      : see http://www.geonames.org/export/codes.html, varchar(10)
    country code      : ISO-3166 2-letter country code, 2 characters
    cc2               : alternate country codes, comma separated, ISO-3166 2-letter country code, 200 characters
    admin1 code       : fipscode (subject to change to iso code), see exceptions below, see file admin1Codes.txt …
    admin2 code       : code for the second administrative division, a county in the US, see file admin2Codes.txt; …
    admin3 code       : code for third level administrative division, varchar(20)
    admin4 code       : code for fourth level administrative division, varchar(20)
    population        : bigint (8 byte int)
    elevation         : in meters, integer
    dem               : digital elevation model …
    timezone          : the iana timezone id (see file timeZone.txt) varchar(40)
    modification date : date of last modification in yyyy-MM-dd format
    """

    cities = []
    for line in infile:
        parts = line.split('\t')
        cities.append(parts)

    # sort by population
    cities.sort(key=lambda x: int(x[14]) if x[14].isdigit() else 0, reverse=True)

    return cities


def read_country(country_file):
    """
    Read countriesInfo.txt file, create dictionary.

    ISO
    ISO3
    ISO-Numeric
    fips
    Country
    Capital
    Area(in sq km)
    Population
    Continent
    tld
    CurrencyCode
    CurrencyName
    Phone
    Postal Code Format
    Postal Code Regex
    Languages
    geonameid
    neighbours
    EquivalentFipsCode
    """

    countries = {}
    for line in country_file:
        if line.startswith('#'):
            continue
        parts = line.split('\t')
        countries[parts[0]] = parts

    return countries


def generate_geos(cities, countries):
    """
    Generate map and geo points data.
    """

    mapa_data = {
        "name": "world map (equirectangular)",
        "w": 2160, "h": 1080,
        "path": "map-equirectangular.svg",
        "projection": 2,
        "type": 1
    }

    geo_data = []
    for i, c in enumerate(cities):

        # add only country capitales and 500 largest cities

        is_capital = c[1] == countries.get(c[8], [False] * 6)[5]
        if i > 500 and not is_capital:
            continue

        print(c[0], c[1], c[8], countries.get(c[8])[4], "*" if is_capital else "", c[14])

        geo = {
            "name": "{} ({})".format(c[1], countries.get(c[8])[4]),
            "lng": float(c[5]),
            "lat": float(c[4]),
        }

        geo_data.append(geo)

    return mapa_data, geo_data


def main():
    city_file = open(sys.argv[1], 'r')
    cities = read_city(city_file)

    country_file = open(sys.argv[2], 'r')
    countries = read_country(country_file)

    dbname = (settings.get("database_url")
              or (len(sys.argv) < 2 and sys.argv[1])
              or "sqlite:///./db.sqlite")

    db.Storage.connect(url=dbname)
    db.Storage.create_tables()
    db.Storage.show_tables()

    mapa_data, geo_data = generate_geos(cities, countries)
    mapa = models.Mapa(**mapa_data)
    db.Storage.save(mapa)
    for g in geo_data:
        g.update(mapa=mapa)
        geo = models.Geo(**g)
        db.Storage.save(geo)


if __name__ == "__main__":
    main()
