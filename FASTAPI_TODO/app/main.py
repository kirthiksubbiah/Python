from fastapi import FastAPI
from app.routes.todo import router as todo_router

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(todo_router)
