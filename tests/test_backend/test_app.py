"""
    Tests for the renumics spotlight app
"""

import math
import json
import datetime
from fastapi.testclient import TestClient


def test_read_length(testclient: TestClient) -> None:
    """test length can be read and returns float"""
    response = testclient.get("/api/table/")
    generation_id = json.loads(response.text)["generation_id"]
    response = testclient.get(f"/api/table/length/42?generation_id={generation_id}")
    assert not math.isnan(float(response.text))
    assert response.status_code == 200


def test_read_image(testclient: TestClient) -> None:
    """test image can be read an returns data"""
    generation_id = json.loads(testclient.get("/api/table/").text)["generation_id"]
    response = testclient.get(f"/api/table/image/47?generation_id={generation_id}")
    assert len(response.text) > 100
    assert response.status_code == 200


def test_read_encoded(testclient: TestClient) -> None:
    """test encoded can be read an returns data"""
    generation_id = json.loads(testclient.get("/api/table/").text)["generation_id"]
    response = testclient.get(f"/api/table/encoded/2?generation_id={generation_id}")
    assert len(json.loads(response.text)) > 10
    assert response.status_code == 200


def test_read_mesh(testclient: TestClient) -> None:
    """test mesh can be read an returns data"""
    generation_id = json.loads(testclient.get("/api/table/").text)["generation_id"]
    response = testclient.get(f"/api/table/mesh/6?generation_id={generation_id}")
    assert len(response.text) > 1000
    assert response.status_code == 200


def test_read_audio(testclient: TestClient) -> None:
    """test mesh can be read an returns data"""
    generation_id = json.loads(testclient.get("/api/table/").text)["generation_id"]
    response = testclient.get(f"/api/table/audio/13?generation_id=0{generation_id}")
    assert len(response.text) > 1000
    assert response.status_code == 200


def test_read_now(testclient: TestClient) -> None:
    """test 'now' can be read an returns datetime"""
    generation_id = json.loads(testclient.get("/api/table/").text)["generation_id"]
    response = testclient.get(f"/api/table/now/1?generation_id={generation_id}")
    assert response.status_code == 200
    assert datetime.datetime.fromisoformat(response.text) < datetime.datetime.utcnow()


def test_read_table(testclient: TestClient) -> None:
    """test full table can be read an returns data"""
    response = testclient.get("/api/table/")
    assert response.status_code == 200
    assert len(response.text) > 1000
