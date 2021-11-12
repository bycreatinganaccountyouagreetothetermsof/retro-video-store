import pytest
from app.models.video import Video
from app.models.customer import Customer
from app import db
from datetime import datetime
import json

VIDEO_TITLE = "A Brand New Video"
VIDEO_ID = 1
VIDEO_INVENTORY = 1
VIDEO_RELEASE_DATE = "01-01-2001"

CUSTOMER_NAME = "A Brand New Customer"
CUSTOMER_ID = 1
CUSTOMER_POSTAL_CODE = "12345"
CUSTOMER_PHONE = "123-123-1234"


@pytest.fixture
def ten_videos(app):
    for i in range(2000, 1990, -1):
        db.session.add(
            Video(
                title=VIDEO_TITLE,
                release_date=f"01-01-{i}",  # dates receding
                total_inventory=VIDEO_INVENTORY,
            )
        )
    db.session.commit()


@pytest.fixture
def twenty_customers(app):
    for i in range(20):
        db.session.add(
            Customer(
                name=chr(90 - i) + CUSTOMER_NAME,
                postal_code=CUSTOMER_POSTAL_CODE,
                phone=CUSTOMER_PHONE,
            )
        )
    db.session.commit()


@pytest.fixture
def five_overdue_five_returned(app, client, twenty_customers, ten_videos):
    for i in range(10):
        response = client.post(
            "/rentals/check-out", json={"customer_id": i, "video_id": i}
        )
    for i in range(5):
        response = client.post(
            "/rentals/check-in", json={"customer_id": i, "video_id": i}
        )


def test_video_pagination(client, ten_videos):
    # Act
    response = client.get("/videos?n=5&p=1")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert len(response_body) == 5


def test_video_sorting(client, ten_videos):
    # Act
    response = client.get("/videos?sort=release_date")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    response_body[0]["id"] == 10


def test_video_sorting_with_pagination(client, ten_videos):
    # Act
    response = client.get("/videos?sort=release_date&n=5&p=2")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert len(response_body) == 5
    assert response_body[0]["id"] == 5


def test_customer_sorting_with_pagination(client, twenty_customers):
    # Act
    response = client.get("/customers?sort=name&n=10&p=2")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert len(response_body) == 10
    assert response_body[0]["id"] == 10


def test_one_overdue_rental(client, one_checked_out_video):
    response = client.get("/rentals/overdue")
    response_body = response.get_json()

    assert response.status_code == 200
    assert len(response_body) == 1

    overdue = response_body[0]
    assert overdue["video_id"] == VIDEO_ID
    assert overdue["title"] == VIDEO_TITLE
    assert overdue["customer_id"] == CUSTOMER_ID
    assert overdue["name"] == CUSTOMER_NAME
    assert overdue["postal_code"] == CUSTOMER_POSTAL_CODE
    assert "checkout_date" in overdue
    assert (
        datetime.strptime(overdue["due_date"], "%a, %d %b %Y %H:%M:%S GMT").date()
        <= datetime.today().date()
    )


def test_some_returned_some_overdue_rentals(client, five_overdue_five_returned):
    response = client.get("/rentals/overdue")
    response_body = response.get_json()

    assert response.status_code == 200
    assert len(response_body) == 5

    for overdue in response_body:
        assert "checkout_date" in overdue
        assert (
            datetime.strptime(overdue["due_date"], "%a, %d %b %Y %H:%M:%S GMT").date()
            <= datetime.today().date()
        )


def test_get_video_history(client, five_overdue_five_returned):
    response = client.get("/videos/1/history")
    response_body = response.get_json()

    assert response.status_code == 200
    assert len(response_body) == 1
    customer = response_body[0]
    assert "customer_id" in customer
    assert "name" in customer
    assert "postal_code" in customer
    assert "checkout_date" in customer
    assert "due_date" in customer


def test_get_customer_history(client, five_overdue_five_returned):
    response = client.get("/customers/1/history")
    response_body = response.get_json()

    assert response.status_code == 200
    assert len(response_body) == 1

    video = response_body[0]
    assert "title" in video
    assert "checkout_date" in video
    assert "due_date" in video


"""cli tests"""

import requests
import rvsclient.__main__ as rvsclient


@pytest.fixture
def runner(app, capture_requests):
    return app.test_cli_runner()


@pytest.fixture
def capture_requests(monkeypatch, client):
    monkeypatch.setattr(requests, "get", client.get)
    monkeypatch.setattr(requests, "post", client.post)


def test_cli_no_args(runner):
    result = runner.invoke(rvsclient.cli)
    assert result.exit_code == 0


def test_cli_no_args_json(runner):
    result = runner.invoke(rvsclient.cli, args=["--json"])
    assert result.exit_code == 2


def test_cli_videos_no_args(runner, one_video):
    result = runner.invoke(rvsclient.cli, args=["videos"])
    assert result.exit_code == 0
    assert result.output.startswith("Retrieved 1 videos:\n")


def test_cli_videos_arg_id(runner, one_video):
    result = runner.invoke(rvsclient.videos, args=["1"])
    assert result.exit_code == 0
    assert result.output.startswith("Video id: 1\n")


def test_cli_json_videos_no_args(runner, one_video):
    result = runner.invoke(rvsclient.cli, args=["--json", "videos"])
    assert result.exit_code == 0
    response_body = json.loads(result.output)
    assert len(response_body) == 1
    assert response_body[0]["title"] == VIDEO_TITLE
    assert response_body[0]["id"] == VIDEO_ID
    assert response_body[0]["total_inventory"] == VIDEO_INVENTORY


def test_cli_json_videos_arg_id(runner, one_video):
    result = runner.invoke(rvsclient.cli, args=["--json", "videos", "1"])
    assert result.exit_code == 0
    response_body = json.loads(result.output)
    assert len(response_body) == 4
    assert response_body["title"] == VIDEO_TITLE
    assert response_body["id"] == VIDEO_ID
    assert response_body["total_inventory"] == VIDEO_INVENTORY


def test_cli_customers_no_args(runner, one_customer):
    result = runner.invoke(rvsclient.cli, args=["customers"])
    assert result.exit_code == 0
    assert result.output.startswith("Retrieved 1 customers:\n")


def test_cli_customers_arg_id(runner, one_customer):
    result = runner.invoke(rvsclient.customers, args=["1"])
    assert result.exit_code == 0
    assert result.output.startswith("Customer id: 1\n")


def test_cli_rentals_arg_overdue(runner, five_overdue_five_returned):
    result = runner.invoke(rvsclient.cli, args=["rentals", "overdue"])
    assert result.exit_code == 0
    assert result.output.startswith("Test\nRetrieved 5 overdue rentals:\n\t")


def test_cli_rentals_arg_history(runner, five_overdue_five_returned):
    result = runner.invoke(rvsclient.cli, args=["rentals", "history"])
    assert result.exit_code == 0
