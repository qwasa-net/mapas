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
    mapapp.mount(mount_path, StaticFiles(directory=static_path, html=True), name="static")

# handle index (in dev/test mode)
if redirect_index := settings.get("redirect_index"):
    mapapp.get("/")(
        lambda: fastapi.responses.RedirectResponse(redirect_index, status_code=301)
    )

# init database connection
if database_url := settings.get("database_url"):
    db.Storage.connect(database_url, {})


def main():
    """Start server if launched from terminal as a script"""

    uvicorn.run(
        "main:mapapp",
        host=settings.get("listen_host", "127.0.0.1"),
        port=settings.get("listen_port", 8000),
        reload=True,
        debug=True,
        log_level="debug",
    )


if __name__ == "__main__":
    import uvicorn
    main()
