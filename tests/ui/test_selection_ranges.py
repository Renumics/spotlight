"""Tests for selecting a range of rows"""

from typing import Any, List

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from .basic_actions import ctrl_click, open_app, shift_click
from .example_tables import selection_example_ids
from .helpers import (
    get_column_index,
    get_selected_count,
    get_tab,
    get_table_cell,
    screenshot_exception,
)


def get_listed_ids(driver: WebDriver) -> List[str]:
    """get the ids of the rows the table lists, from the first row down"""
    id_column = get_column_index(driver, "id")
    cells = driver.find_elements(
        by=By.CSS_SELECTOR, value=f"div[data-columnindex='{id_column}']"
    )
    rows = [(int(cell.get_attribute("data-rowindex")), cell.text) for cell in cells]
    return [text for row, text in sorted(rows) if row >= 0]


def test_shift_click_over_a_selected_row_selects_it_once(
    webdriver: WebDriver,
    frontend_base_url: str,
    loaded_selection_example_dataset: Any,
    skip_tour: None,
) -> None:
    """
    test a range of rows that holds an already selected row does not select that row
    twice, which would list it twice in the Selected tab
    """
    ids = selection_example_ids(40)
    with screenshot_exception(webdriver):
        open_app(webdriver, frontend_base_url)

        # the range from the last selected row, row 4, down to row 8 holds row 6
        ctrl_click(webdriver, get_table_cell(webdriver, 2))
        ctrl_click(webdriver, get_table_cell(webdriver, 6))
        ctrl_click(webdriver, get_table_cell(webdriver, 4))
        shift_click(webdriver, get_table_cell(webdriver, 8))

        assert get_selected_count(webdriver) == 6
        get_tab(webdriver, "Selected").click()
        assert get_listed_ids(webdriver) == [ids[row] for row in (2, 6, 4, 5, 7, 8)]
