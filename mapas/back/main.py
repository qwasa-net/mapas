"""Setup app, start server."""
import os

import fastapi
from fastapi.staticfiles import StaticFiles

import api
import db
import settings

# create application
mapapp = fastapi.FastAPI()

# add API points
mapapp.include_router(api.router)

# add static files (in dev/test mode)
if static_path := settings.get("serve_static"):
    mount_path = "/" + os.path.basename(os.path.normpath(static_path))
    mapapp.mount(mount_path, StaticFiles(directory=static_path), name="static")

# init database connection
if database_url := settings.get("database_url"):
    db.Storage.connect(database_url, {})


def main():
    """Start server if launched from terminal as a script"""

    uvicorn.run(
        "main:mapapp",
        host=settings.get("listen_host") or "127.0.0.1",
        port=settings.get("listen_port") or 8000,
        reload=True,
        debug=True,
        log_level="debug",
    )


if __name__ == "__main__":
    import uvicorn
    main()
