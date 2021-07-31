from typing import Optional

import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from celery import Celery

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

celeryApp = Celery('persona',
                    broker="amqp://stephenbaione:zThG$a$&75f720@localhost/stephen_vhost",
                    backend="mongodb://127.0.0.1:27017",
                    task_track_started=True,
                    include=["persona.core.tasks"])
                
app.include_router(UserRouter)
app.include_router(SpotifyAuthRouter)
app.include_router(SpotifyUserRouter)

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/test/{test_id}")
async def read_item(test_id: int, q: Optional[str] = None):
    return {"test_id": test_id, "q": q}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
