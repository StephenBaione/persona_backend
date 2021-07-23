from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from service.routes.user import router as UserRouter
from external_services.spotify.routes.auth import router as SpotifyAuthRouter
from external_services.spotify.routes.user import router as SpotifyUserRouter

app = FastAPI()

origins = [
    "http://localhost:8100",
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

app.include_router(UserRouter)
app.include_router(SpotifyAuthRouter)
app.include_router(SpotifyUserRouter)

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/test/{test_id}")
async def read_item(test_id: int, q: Optional[str] = None):
    return {"test_id": test_id, "q": q}
