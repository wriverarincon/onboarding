from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver

class FindElements:
    def waitUntilFound(driver: WebDriver, selector: str, locator: str = 'css_selector') -> WebElement:
        '''
        Will wait 60 seconds for the element to appear before throwing an exception.
        If wait is not necessary, use tryToFind().
        '''
        locator = getattr(By, locator.upper())
        element = None
        WAIT = WebDriverWait(driver, 30)

        try_count = 0
        while try_count <= 3:
            try:
                element = WAIT.until(EC.presence_of_element_located(
                    (locator, selector)
                    )
                )
            except TimeoutException:
                try_count += 1
        return element
    
    def tryToFind(driver: WebDriver, selector: str, locator: str = 'css_selector') -> WebElement | None:
        '''
        Used when one is sure the element is there and can be interacted with, meaning
        waiting for it is not necessary. Use waitUntilFound() otherwise.
        '''
        locator = getattr(By, locator.upper())
        try:
            element = driver.find_element(locator, selector)
            return element
        except NoSuchElementException:
            return 'The element was not found.'
