import pytest
from pydantic import ValidationError

from app.schemas.auth import UserRegister
from app.schemas.services import ServiceCreate, ServiceEndpointUpdate


def test_service_values_are_normalized() -> None:
    service = ServiceCreate(
        name="  Monitoring API  ",
        type="  monitoring  ",
        status="running",
    )
    assert service.name == "Monitoring API"
    assert service.type == "monitoring"


def test_unknown_status_is_rejected() -> None:
    with pytest.raises(ValidationError):
        ServiceCreate(name="Test Service", type="application", status="unknown")


@pytest.mark.parametrize(
    ("value", "is_valid"),
    [
        ("https://example.com", True),
        ("https://example.com/api", True),
        ("abc", False),
        ("", False),
    ],
)
def test_endpoint_url_length(value: str, is_valid: bool) -> None:
    if is_valid:
        assert ServiceEndpointUpdate(endpoint_url=value).endpoint_url == value
    else:
        with pytest.raises(ValidationError):
            ServiceEndpointUpdate(endpoint_url=value)


def test_username_is_normalized() -> None:
    user = UserRegister(username="  Student02  ", password="cloud12345")
    assert user.username == "student02"
