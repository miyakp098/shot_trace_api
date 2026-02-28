from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.endpoint.media import router as media_router


app = FastAPI(
    title="Shot Trace API",
    description="Example endpoints for Swagger / OpenAPI",
    version="0.1.0",
)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


app.include_router(media_router)
