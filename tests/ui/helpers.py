"""Helpers for ui-tests"""

import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterator, List

import pytest
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


class LoadingIsStillDisplayed(Exception):
    """raised when loading is still display and element is hidden"""


class NoMatchingElementsFound(Exception):
    """raised when no elements matching the query were found"""


class NoMatchingElementIsDisplayed(Exception):
    """raised when all matching elements are invisible"""


class ElementNotAvailable(Exception):
    """ "Raised when the GUI element is not available for any reason"""


@contextmanager
def screenshot_exception(webdriver: WebDriver) -> Iterator[None]:
    """catch exception and make a screenshot"""
    try:
        yield
    except Exception as e:
        new_screenshots_folder = Path(pytest.results_folder) / "screenshots"  # type: ignore[attr-defined]
        now = time.strftime("%Y%m%d-%H%M%S")
        new_screenshot_path = (
            new_screenshots_folder
            / f"Exception_{now}_{e.__class__.__name__}_{pytest.browser_name}.png"  # type: ignore[attr-defined]
        )
        webdriver.save_screenshot(str(new_screenshot_path))

        print(f"=== Exception logged into {new_screenshot_path} at {now} ===")
        print(e)
        print("=== browser logs ===")
        try:
            log = list(webdriver.get_log("browser"))
            for entry in log:
                print(entry)
        except:  # noqa: E722
            pass
        print("=========================================")

        raise e


def _wait_for_element(
    webdriver: WebDriver, getter: Callable, element_name: str, timeout: int
) -> WebElement:
    """use the given getter method to find a web element and wait until it is displayed"""

    def find_visible_element() -> WebElement:
        elements = getter()
        if _is_loading_circle_displayed(webdriver):
            raise LoadingIsStillDisplayed
        if len(elements) == 0:
            raise NoMatchingElementsFound
        for found_element in elements:
            if found_element.is_displayed():
                return found_element
        raise NoMatchingElementIsDisplayed

    start_time = datetime.now()
    current_time = start_time
    last_exception = None

    while (current_time - start_time).seconds < timeout:
        try:
            return find_visible_element()
        except (
            StaleElementReferenceException,
            NoMatchingElementsFound,
            NoMatchingElementIsDisplayed,
            LoadingIsStillDisplayed,
            NoSuchElementException,
        ) as exception:
            last_exception = exception
        current_time = datetime.now()
        time.sleep(0.3)

    raise ElementNotAvailable(
        f"Could not find element '{element_name}' "
        f"last exception ({type(last_exception)}): {last_exception}"
    )


def wait_for_tagged_element(
    webdriver: WebDriver, data_test_tag: str, timeout: int = 20
) -> WebElement:
    """wait for an element with the given data-test-tag"""
    time.sleep(0.3)
    return _wait_for_element(
        webdriver,
        lambda: webdriver.find_elements(
            by=By.CSS_SELECTOR, value=f"[data-test-tag='{data_test_tag}']"
        ),
        f"data-test-tag={data_test_tag}",
        timeout,
    )


def wait_for_css_element(
    webdriver: WebDriver, css_selector: str, timeout: int = 20
) -> WebElement:
    """wait for a visible element matching the css selector"""
    time.sleep(0.3)
    return _wait_for_element(
        webdriver,
        lambda: webdriver.find_elements(by=By.CSS_SELECTOR, value=css_selector),
        f"css selector {css_selector}",
        timeout,
    )


def wait_for_text_element(
    webdriver: WebDriver, text: str, timeout: int = 20
) -> WebElement:
    """wait for a visible element with the given text, e.g. an entry of a menu"""
    time.sleep(0.3)
    return _wait_for_element(
        webdriver,
        lambda: webdriver.find_elements(
            by=By.XPATH, value=f"//*[contains(text(), '{text}')]"
        ),
        f"element with text '{text}'",
        timeout,
    )


def get_table_cell(webdriver: WebDriver, row: int, column: int = 0) -> WebElement:
    """get the table cell in the given row and column of the current table view"""
    return wait_for_css_element(
        webdriver, f"div[data-rowindex='{row}'][data-columnindex='{column}']"
    )


def get_column_index(webdriver: WebDriver, name: str) -> int:
    """get the index of the visible table column with the given name"""
    wait_for_css_element(webdriver, "div[data-rowindex='-1']")
    for header in webdriver.find_elements(
        by=By.CSS_SELECTOR, value="div[data-rowindex='-1']"
    ):
        if header.text.strip() == name:
            return int(header.get_attribute("data-columnindex"))
    raise ElementNotAvailable(f"Could not find the column '{name}'")


def get_visible_column_names(webdriver: WebDriver) -> List[str]:
    """get the names of the visible table columns, from left to right"""
    wait_for_css_element(webdriver, "div[data-rowindex='-1']")
    headers = webdriver.find_elements(
        by=By.CSS_SELECTOR, value="div[data-rowindex='-1']"
    )
    headers.sort(key=lambda header: int(header.get_attribute("data-columnindex")))
    return [header.text.strip() for header in headers]


def get_selected_count(webdriver: WebDriver) -> int:
    """get the number of selected rows, shown in the tab of the table"""
    from ._autogenerated_ui_elements import DataTestTags

    return int(
        wait_for_tagged_element(webdriver, DataTestTags.DATAGRID_SELECTED_COUNT).text
    )


def _is_loading_circle_displayed(webdriver: WebDriver) -> bool:
    """Check if loading circle is displayed"""
    from ._autogenerated_ui_elements import DataTestTags

    loading_circles = webdriver.find_elements(
        by=By.CSS_SELECTOR,
        value=f"[data-test-tag='{DataTestTags.GLOBAL_LOADING_INDICATOR}']",
    )
    return any(elem.is_displayed() for elem in loading_circles)


def get_tab(driver: WebDriver, tab_text: str) -> WebElement:
    """get a spotlight tab (e.g. All/Filtered/Selected or  Details or Scatterplot/Similarities"""
    button_text = _wait_for_element(
        driver,
        lambda: driver.find_elements(
            by=By.XPATH, value=f"//*[contains(text(), '{tab_text}')]"
        ),
        f"get_tab by text '{tab_text}'",
        10,
    )
    filtered_tab = button_text.find_element(by=By.XPATH, value="./..")
    return filtered_tab
