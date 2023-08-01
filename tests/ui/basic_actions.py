"""basic user itections to be used during tests"""
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from .helpers import wait_for_tagged_element


def select_points_similaritymap(
    driver: WebDriver, selection_width: float = 0.5
) -> None:
    """select point in similarity map"""
    wait_for_tagged_element(driver, "similaritymap")
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
