# Custom helper functions for this project
from helper_functions import retry

# external dependencies
from decimal import Decimal
import re
from selenium.webdriver.common.by import By
from time import sleep

# Logging
import logging
logger = logging.getLogger(__name__)


def usaa(driver, **kwargs):
    member_id = kwargs['usaa_member_id']
    password = kwargs['usaa_password']
    pin = kwargs['usaa_pin']

    usaa_login(driver, member_id, password, pin)
    data = usaa_get_data(driver)
    usaa_logout(driver)

    return data


@retry(max_tries=3, logger=logger)
def usaa_login(driver: object, member_id: str, password: str, pin: str) -> None:
    """Log in to USAA

    This function modifies the state of `driver` so it is logged in to USAA and on the credentialed user's homepage.

    Args:
        driver (selenium webdriver): controls the chromium webpage
        member_id (str): usaa login credential
        password (str): usaa login password
        pin (str): usaa login pin

    Returns:
        None: driver state is logged in to USAA
    """
    wait_time = 3  # seconds
    usaa_url = 'https://www.usaa.com/my/logon'
    driver.get(usaa_url)

    # username
    sleep(wait_time)
    driver.find_element(By.NAME, 'memberId').send_keys(member_id)
    driver.find_element(By.CLASS_NAME, 'submit-btn').click()
    sleep(wait_time)

    # password
    driver.find_element(By.NAME, 'password').send_keys(password)
    driver.find_element(By.CLASS_NAME, 'pass-submit-btn').click()
    sleep(wait_time)

    # MFA - choose PIN as method
    driver.find_element(By.CLASS_NAME, 'more-options-link').click()
    sleep(wait_time)
    driver.find_element(By.CSS_SELECTOR, '[aria-label="Use my PIN"]').click()
    sleep(wait_time)

    # MFA - input PIN
    driver.find_element(By.NAME, 'pin').send_keys(pin)
    driver.find_element(By.CLASS_NAME, 'miam-btn-next').click()
    sleep(wait_time)


@retry(max_tries=2, logger=logger)
def usaa_get_data(driver):
    """Get data from USAA's website

    Gather balance for:
        USAA CLASSIC CHECKING
        Signature Visa (balance should always be negative)
        Savings Buffer
        Rental Cashflow
        Long Term Savings
        1236 ROSLYN ST (current market value)
        12204 W APPLEWOOD KNOLLS DR (current market value)

    Args:
        driver: selenium webdriver, logged in to USAA's homepage

    Returns:
        dict: data of {name: balance} for each entry from USAA
    """
    data = {}
    for product_name, product_label, product_balance in zip(
            driver.find_elements(By.CLASS_NAME, 'product-name'),
            driver.find_elements(By.CLASS_NAME, 'product-label'),
            driver.find_elements(By.CLASS_NAME, 'product-balance'),
    ):
        # for Home Value Monitoring, use the home label as the "name"
        if product_name.text.strip() == 'Home Value Monitoring':
            name = product_label.text
        else:
            name = product_name.text
        name = name.strip()

        # If the product_balance is negative, there are two lines of information, where the first spells it out
        # "negative" for screen readers.  In that case, drop the first line and make the resulting value negative.
        if product_balance.text.strip().startswith('Negative $'):
            balance = -1 * Decimal(re.sub(r'[^\d.]', '', product_balance.text.split('\n')[1]))
        else:
            balance = Decimal(re.sub(r'[^\d.]', '', product_balance.text))

        logger.info(f'{name}: {balance}')
        data[name] = balance

    return data


@retry(max_tries=3, exceptions=AssertionError, logger=logger)
def usaa_logout(driver):
    # click on logout
    driver.find_element(By.CLASS_NAME, 'usaa-globalHeader-utilityButton--logon').click()

    # check that we've actually logged out
    assert 'Log On' == driver.find_element(By.CLASS_NAME, 'usaa-globalHeader-utilityButton--logon').text
