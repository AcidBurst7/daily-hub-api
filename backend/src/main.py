import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.web import (
    auth,
    task,
    board,
    user
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost", "127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
# app.include_router(weather_forecast.router)
app.include_router(auth.router)
app.include_router(board.router)
app.include_router(task.router)


if __name__ == "__main__":
    uvicorn.run("backend.src.main:app", reload=True)
