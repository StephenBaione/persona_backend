from typing import Optional

from fastapi import FastAPI

from service.routes.user import router as UserRouter

app = FastAPI()

app.include_router(UserRouter)

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/test/{test_id}")
async def read_item(test_id: int, q: Optional[str] = None):
    return {"test_id": test_id, "q": q}


