from fastapi import APIRouter, HTTPException
from app.schemas import TodoCreate, TodoResponse

router = APIRouter(prefix="/todos", tags=["todos"])
fake_db = []
next_id = 1


def get_todo_or_404(todo_id: int):
    for todo in fake_db:
        if todo["id"] == todo_id:
            return todo
    return None

@router.post("/", response_model=TodoResponse)
def create_todo(todo: TodoCreate):
    global next_id
    new_todo = {"id": next_id, **todo.dict()}
    fake_db.append(new_todo)
    next_id += 1
    return new_todo

@router.get("/", response_model=list[TodoResponse])
def list_todos():
    return fake_db


@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int):
    todo = get_todo_or_404(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, updated: TodoCreate):
    todo = get_todo_or_404(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo["title"] = updated.title
    todo["completed"] = updated.completed
    return todo


@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    todo = get_todo_or_404(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    fake_db.remove(todo)
