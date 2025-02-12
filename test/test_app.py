import json
import pytest
from io import BytesIO
import app as docker_app  # Import the module to access both app and client

@pytest.fixture
def client():
    with docker_app.app.test_client() as client:
        yield client

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Server is running!" in response.data

def test_missing_payload_build(client):
    response = client.post('/build', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_valid_payload_build(monkeypatch, client):
    # Dummy build function that returns a tuple: (image, build_logs)
    def dummy_build(*args, **kwargs):
        dummy_image = {"dummy": "image"}
        dummy_logs = [b"Step 1/1 : FROM python:3.8\n"]
        return (dummy_image, dummy_logs)

    # Dummy push function that returns an iterator over push logs
    def dummy_push(*args, **kwargs):
        return iter([b"Pushed image"])

    # Patch the docker client methods
    monkeypatch.setattr(docker_app.client.images, "build", dummy_build)
    monkeypatch.setattr(docker_app.client.images, "push", dummy_push)

    payload = {
        "dockerfile": "FROM python:3.8\nCMD echo Hello World",
        "image_tag": "dummyregistry/myimage:latest"
    }
    response = client.post('/build', json=payload)
    data = json.loads(response.data)

    assert response.status_code == 200
    assert data.get("message") == "Image built and pushed successfully"
    assert data.get("image_tag") == payload["image_tag"]

def test_valid_payload_build_file(monkeypatch, client):
    def dummy_build(*args, **kwargs):
        dummy_image = {"dummy": "image"}
        dummy_logs = [b"Step 1/1 : FROM python:3.8\n"]
        return (dummy_image, dummy_logs)

    def dummy_push(*args, **kwargs):
        return iter([b"Pushed image"])

    monkeypatch.setattr(docker_app.client.images, "build", dummy_build)
    monkeypatch.setattr(docker_app.client.images, "push", dummy_push)

    # Prepare the file data as if it were uploaded via multipart/form-data
    data = {
        "image_tag": "dummyregistry/myimage:latest"
    }
    dockerfile_content = b"FROM python:3.8\nCMD echo Hello World"
    dockerfile_file = BytesIO(dockerfile_content)
    dockerfile_file.name = "Dockerfile"  # Set a filename so Flask can detect it

    response = client.post(
        '/build_file',
        data={'dockerfile': dockerfile_file, 'image_tag': data["image_tag"]},
        content_type='multipart/form-data'
    )
    data_response = json.loads(response.data)

    assert response.status_code == 200
    assert data_response.get("message") == "Image built and pushed successfully"
    assert data_response.get("image_tag") == data["image_tag"]
