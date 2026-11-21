import httpx
import pytest


@pytest.fixture(scope="session")
def web_client(lantern_target):
    with httpx.Client(
        base_url=lantern_target.base_url,
        timeout=lantern_target.deadline,
        trust_env=False,
        follow_redirects=False,
    ) as client:
        yield client


@pytest.mark.parametrize(
    ("route", "status"),
    [("/", 200), ("/health.json", 200), ("/missing-page", 404)],
    ids=["homepage", "health", "absent"],
)
def test_status_contract(web_client, route, status):
    observed = web_client.get(route)
    assert observed.status_code == status


def test_public_page_has_expected_identifier(web_client, lantern_target):
    response = web_client.get("/")
    assert response.status_code == 200
    assert lantern_target.expected_release in response.text


def test_health_document_identifies_the_same_release(web_client, lantern_target):
    response = web_client.get("/health.json")
    assert response.status_code == 200
    assert response.headers["content-type"].split(";")[0] == "application/json"
    document = response.json()
    assert isinstance(document, dict)
    assert document.get("status") == "available"
    assert document.get("release") == lantern_target.expected_release
