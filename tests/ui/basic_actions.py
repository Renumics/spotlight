"""basic user itections to be used during tests"""

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from .helpers import wait_for_tagged_element


def set_selection_mode(driver: WebDriver, mode: str) -> None:
    """pick the global selection tool ('rectangular' or 'lasso') in the app bar"""
    wait_for_tagged_element(driver, "selection-mode-dropdown").click()
    # the menu entry only exists while the dropdown is open, and picking an
    # entry closes the dropdown again
    wait_for_tagged_element(driver, f"selection-mode-{mode}").click()


def select_points_similaritymap(
    driver: WebDriver, selection_width: float = 0.5
) -> None:
    """select point in similarity map with the rectangular tool"""
    wait_for_tagged_element(driver, "similaritymap")
    # the selection tool is a global, persisted setting, so it has to be set
    # explicitly instead of relying on the default
    set_selection_mode(driver, "rectangular")
    element = driver.find_element(
        by=By.CSS_SELECTOR, value="[data-test-tag='similaritymap']"
    )

    actions = ActionChains(driver)
    height, width = element.size["height"], element.size["width"]
    actions.move_to_element(element).move_by_offset(
        0.45 * width, 0.45 * height
    ).click_and_hold().move_by_offset(
        -selection_width * width, -0.99 * height
    ).release().perform()


def select_points_similaritymap_lasso(driver: WebDriver) -> None:
    """select points in similarity map with the lasso tool"""
    wait_for_tagged_element(driver, "similaritymap")
    set_selection_mode(driver, "lasso")
    element = driver.find_element(
        by=By.CSS_SELECTOR, value="[data-test-tag='similaritymap']"
    )

    actions = ActionChains(driver)
    height, width = element.size["height"], element.size["width"]
    # Trace a box in several segments. The intermediate moves are required
    # because a lasso needs at least three vertices to enclose an area.
    actions.move_to_element(element).move_by_offset(
        0.45 * width, 0.45 * height
    ).click_and_hold()
    for offset_x, offset_y in ((-0.9, 0.0), (0.0, -0.9), (0.9, 0.0), (0.0, 0.9)):
        actions.move_by_offset(offset_x * width, offset_y * height)
    actions.release().perform()
