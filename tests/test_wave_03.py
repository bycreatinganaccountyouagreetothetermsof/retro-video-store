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
