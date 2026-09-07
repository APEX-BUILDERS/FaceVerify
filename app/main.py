from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import FACES_DIR
from app.db import init_db
from app.services.chain_service import ensure_genesis_block


def app_error(status_code: int, message: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail=message)


app = FastAPI(title="FaceVerify")
app.mount("/storage/faces", StaticFiles(directory=FACES_DIR), name="faces")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.on_event("startup")
def startup() -> None:
    init_db()
    ensure_genesis_block()


from app.routers import chain, face, pipeline, search  # noqa: E402

app.include_router(face.router)
app.include_router(search.router)
app.include_router(chain.router)
app.include_router(pipeline.router)
app.mount("/", StaticFiles(directory="web", html=True), name="web")
