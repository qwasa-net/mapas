FROM docker.io/library/python:3-slim

# get build tools, create user
RUN apt-get update && \
    apt-get install -y --no-install-recommends make wget unzip libsqlite3-0 sqlite3 && \
    groupadd mapas && \
    useradd --gid mapas --home-dir /mapas --create-home --shell /bin/false mapas

# app settings
EXPOSE 8000
USER mapas
WORKDIR /mapas/

ENV PYTHONPATH=.
ENV MAPA_DATABASE_URL='sqlite:////mapas/demodb.sqlite'
ENV MAPA_LISTEN_HOST='0.0.0.0'

# copy src
COPY --chown=mapas:mapas ./Makefile ./demodb.sqlite /mapas/
COPY --chown=mapas:mapas ./mapas /mapas/mapas

# build app
RUN cd /mapas/; chmod 775 -R /mapas/; ls -lh; make clean env build tests

# start
CMD ["/usr/bin/make", "--makefile=/mapas/Makefile", "--directory=/mapas", "start"]
