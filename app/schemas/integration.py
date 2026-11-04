from typing import Literal

from pydantic import BaseModel, Field


class NotificationSendRequest(BaseModel):
    recipient: str = Field(..., min_length=3, max_length=100)
    message: str = Field(..., min_length=1, max_length=500)


class NotificationSendResponse(NotificationSendRequest):
    id: int
    status: Literal["accepted"]
