"""Tests for selecting rows in the table by mouse"""

import time
from typing import Any

from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver

from .basic_actions import open_app
from .example_tables import selection_example_ids
from .helpers import (
    get_column_index,
    get_selected_count,
    get_tab,
    get_table_cell,
    screenshot_exception,
)


def test_press_and_release_in_different_cells_selects_pressed_row(
    webdriver: WebDriver,
    frontend_base_url: str,
    loaded_selection_example_dataset: Any,
    skip_tour: None,
) -> None:
    """
    test a click that ends in the cell below the one it began in selects the row it began in
    (and not the first row)
    """
    with screenshot_exception(webdriver):
        open_app(webdriver, frontend_base_url)
        cell = get_table_cell(webdriver, 4)
        height = cell.size["height"]

        # press 2 px above the lower border of the row, release 2 px below it:
        # a movement too short to be a drag
        ActionChains(webdriver).move_to_element_with_offset(
            cell, 5, height // 2 - 2
        ).click_and_hold().move_by_offset(0, 4).release().perform()
        time.sleep(0.5)

        assert get_selected_count(webdriver) == 1
        get_tab(webdriver, "Selected").click()
        id_column = get_column_index(webdriver, "id")
        assert (
            get_table_cell(webdriver, 0, id_column).text == selection_example_ids(40)[4]
        )
