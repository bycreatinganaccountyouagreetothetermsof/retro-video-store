from datetime import datetime

VIDEO_TITLE = "A Brand New Video"
VIDEO_ID = 1
VIDEO_INVENTORY = 1
VIDEO_RELEASE_DATE = "01-01-2001"

CUSTOMER_NAME = "A Brand New Customer"
CUSTOMER_ID = 1
CUSTOMER_POSTAL_CODE = "12345"
CUSTOMER_PHONE = "123-123-1234"


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


def test_overdue_rentals(client, one_checked_out_video):
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
