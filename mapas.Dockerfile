FROM docker.io/library/python:3-slim

EXPOSE 8000

ENV PYTHONPATH=.
ENV MAPA_DATABASE_URL='sqlite:///mapas/citydb.sqlite'
ENV MAPA_LISTEN_HOST='0.0.0.0'

# get build tools, create user
RUN apt-get update && \
    apt-get install -y --no-install-recommends make wget unzip libsqlite3-0 sqlite3 && \
    groupadd mapas && \
    useradd --gid mapas --home-dir /mapas --create-home --shell /bin/false mapas

USER mapas
WORKDIR /mapas/

# copy src
COPY --chown=mapas:mapas ./Makefile /mapas/
COPY --chown=mapas:mapas ./mapas /mapas/mapas

# build app
RUN cd /mapas/; ls -lh; make clean env build citydb tests

# start
CMD ["/usr/bin/make", "--makefile=/mapas/Makefile", "--directory=/mapas", "start"]
