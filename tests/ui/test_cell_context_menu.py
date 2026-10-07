"""Tests for the context menu of table cells"""

import time
from typing import Any

from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver

from .basic_actions import ctrl_click, get_copied_texts, open_app, record_clipboard
from .example_tables import selection_example_ids
from .helpers import (
    get_column_index,
    get_tab,
    get_table_cell,
    screenshot_exception,
    wait_for_text_element,
)


def test_copy_cell_value_in_selected_view(
    webdriver: WebDriver,
    frontend_base_url: str,
    loaded_selection_example_dataset: Any,
    skip_tour: None,
) -> None:
    """
    test the copied text of a cell is the text of that cell when the table shows only
    the selected rows, so that the row of the view is not the row of the dataset
    """
    ids = selection_example_ids(40)
    with screenshot_exception(webdriver):
        open_app(webdriver, frontend_base_url)

        ctrl_click(webdriver, get_table_cell(webdriver, 7))
        ctrl_click(webdriver, get_table_cell(webdriver, 3))
        get_tab(webdriver, "Selected").click()

        cell = get_table_cell(webdriver, 1, get_column_index(webdriver, "id"))
        assert cell.text == ids[3]

        record_clipboard(webdriver)
        ActionChains(webdriver).context_click(cell).perform()
        wait_for_text_element(webdriver, "Copy Cell Value").click()
        time.sleep(0.5)
        assert get_copied_texts(webdriver) == [ids[3]]
