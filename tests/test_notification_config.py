import pytest
from pydantic import ValidationError

from app.config import Settings


@pytest.mark.parametrize(
    "field,value",
    [
        ("notification_max_attempts", 0),
        ("notification_max_attempts", -1),
        ("notification_timeout_seconds", 0),
        ("notification_retry_delay_seconds", -0.1),
    ],
)
def test_invalid_notification_limits_are_rejected(field, value):
    with pytest.raises(ValidationError):
        Settings(**{field: value})


def test_one_attempt_is_allowed():
    assert Settings(notification_max_attempts=1).notification_max_attempts == 1
