import pytest
import requests

# from click.testing import CliRunner
from flask.cli import with_appcontext

from rvsclient.__main__ import cli, videos


@pytest.fixture
def runner(app, capture_requests):
    return app.test_cli_runner()


@pytest.fixture
def capture_requests(monkeypatch, client):
    monkeypatch.setattr(requests, "get", client.get)
    monkeypatch.setattr(requests, "post", client.post)


def test_cli_no_args(runner):
    result = runner.invoke(cli)
    assert result.exit_code == 0


def test_cli_videos_no_arg(runner, one_video):
    result = runner.invoke(videos)
    assert result.exit_code == 0
