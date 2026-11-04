from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Notification Service", version="1.0.0")


class NotificationCreate(BaseModel):
    recipient: str = Field(..., min_length=3, max_length=100)
    message: str = Field(..., min_length=1, max_length=500)


class NotificationResponse(NotificationCreate):
    id: int
    status: Literal["accepted"]


notifications: list[NotificationResponse] = []


@app.get("/status")
def status():
    return {"service": "notification", "status": "running"}


@app.post("/notifications", response_model=NotificationResponse, status_code=201)
async def create_notification(notification: NotificationCreate):
    item = NotificationResponse(id=len(notifications) + 1, status="accepted", **notification.model_dump())
    notifications.append(item)
    return item


@app.get("/notifications", response_model=list[NotificationResponse])
def get_notifications():
    return notifications


@app.get("/notifications/{notification_id}", response_model=NotificationResponse)
def get_notification(notification_id: int):
    for item in notifications:
        if item.id == notification_id:
            return item
    raise HTTPException(status_code=404, detail="Notification not found")

@app.get("/test/error/{status_code}", summary="Сформировать тестовую ошибку")
def test_error(status_code: int):
    if not 400 <= status_code <= 599:
        raise HTTPException(status_code=422, detail="Use an HTTP error status from 400 to 599")
    raise HTTPException(status_code=status_code, detail="Test service error")
