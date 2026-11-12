import copy

import pytest

from app.services.reporting import build_service_report
from scripts.profile_service_report import create_dataset
from scripts.service_report_baseline import build_service_report as baseline


@pytest.mark.parametrize(
    "services,types",
    [
        create_dataset(200, 20),
        ([], []),
        ([{"id": 1, "name": "a", "status": "running", "type_id": 9}], []),
        (
            [{"id": 1, "name": "a", "status": "running", "type_id": 9}],
            [{"id": 9, "name": "first"}, {"id": 9, "name": "second"}],
        ),
    ],
)
def test_report_equivalence_and_no_mutation(services, types):
    original = copy.deepcopy((services, types))
    assert build_service_report(services, types) == baseline(services, types)
    assert (services, types) == original
