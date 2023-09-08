"""
Test Spotlight external data cache and clear cache behaviour.
"""

import json
import shutil

import requests

from renumics import spotlight


def test_external_data_cache(non_existing_image_df_viewer: spotlight.Viewer) -> None:
    """
    Test loading non-existing external data, cache it and clear cache.
    """
    assert non_existing_image_df_viewer.df is not None
    image_path = non_existing_image_df_viewer.df["image"][0]
    app_url = str(non_existing_image_df_viewer)

    response = requests.get(app_url + "api/table/", timeout=5)
    assert response.status_code == 200
    assert len(response.text) > 200
    generation_id = json.loads(response.text)["generation_id"]

    response = requests.get(
        f"{app_url}api/table/image/0?generation_id={generation_id}", timeout=5
    )
    assert response.status_code == 422
    assert json.loads(response.text)["type"] == "ConversionFailed"

    shutil.copyfile("data/images/nature-360p.jpg", image_path)
    response = requests.get(
        f"{app_url}api/table/image/0?generation_id={generation_id}", timeout=5
    )
    assert response.status_code == 200
    first_image_content = response.content
    assert len(first_image_content) == 19355

    shutil.copyfile("data/images/nature-720p.jpg", image_path)
    response = requests.get(
        f"{app_url}api/table/image/0?generation_id={generation_id}", timeout=5
    )
    assert response.status_code == 200
    assert response.content == first_image_content

    spotlight.clear_caches()
    response = requests.get(
        f"{app_url}api/table/image/0?generation_id={generation_id}", timeout=5
    )
    assert response.status_code == 200
    second_image_content = response.content
    assert len(second_image_content) == 70143
    assert second_image_content != first_image_content

    shutil.copyfile("data/audio/1.wav", image_path)
    response = requests.get(
        f"{app_url}api/table/image/0?generation_id={generation_id}", timeout=5
    )
    assert response.status_code == 200
    assert response.content == second_image_content

    spotlight.clear_caches()
    response = requests.get(
        f"{app_url}api/table/image/0?generation_id={generation_id}", timeout=5
    )
    assert response.status_code == 422
    assert json.loads(response.text)["type"] == "ConversionFailed"
