"""
Gather personal financial information by scraping each website with beautifulsoup.
"""

import undetected_chromedriver.v2 as uc  # port of selenium that websites don't think is a bot
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

from decimal import Decimal
from dotenv import dotenv_values
import logging
from pathlib import Path
import re
import time

# Error handling
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from urllib3.exceptions import MaxRetryError
from requests.exceptions import ConnectionError, ReadTimeout


def main():
    # Open browser
    options = uc.ChromeOptions()
    # options.headless = True
    service = Service("./chromedriver")
    driver = uc.Chrome(options=options, service=service, user_data_dir=Path('temp_selenium.profile'))

    try:
        usaa(driver)
    except:
        raise
    finally:
        input("hit any key to exit")
        driver.quit()


def get_env_vars(key_prefix: str = None):
    """Returns variables from .env file.

    Pulls environmental variables from ./.env file.  Returns any variable prefixed by: key_prefix + '_'

    Args:
        key_prefix (str): Only return env vars prefixed by this string + '_'

    Returns:
        dict: relevant env vars
    """
    return {
        key: value
        for key, value in dotenv_values().items()
        if key_prefix is None or key.startswith(key_prefix + '_')
    }


def usaa(driver):
    usaa_login(driver)
    data = usaa_get_data(driver)

    return data


def usaa_login(driver):
    """Log in to USAA

    This function modifies the state of `driver` so it is logged in to USAA and on the credentialed user's homepage.
    It requires the following entries to be in the `./.env` file:
        usaa_member_id=****
        usaa_password=****
        usaa_pin=####

    Args:
        driver: selenium webdriver

    Returns:
        None: driver state is logged in to USAA
    """
    wait_time = 5  # seconds
    usaa_vars = get_env_vars('usaa')
    usaa_url = 'https://www.usaa.com/my/logon'
    driver.get(usaa_url)

    # username
    time.sleep(wait_time)
    driver.find_element(By.NAME, 'memberId').send_keys(usaa_vars['usaa_member_id'])
    driver.find_element(By.CLASS_NAME, 'submit-btn').click()
    time.sleep(wait_time)

    # password
    driver.find_element(By.NAME, 'password').send_keys(usaa_vars['usaa_password'])
    driver.find_element(By.CLASS_NAME, 'pass-submit-btn').click()
    time.sleep(wait_time)

    # MFA - choose PIN as method
    driver.find_element(By.CLASS_NAME, 'more-options-link').click()
    time.sleep(wait_time)
    driver.find_element(By.CSS_SELECTOR, '[aria-label="Use my PIN"]').click()
    time.sleep(wait_time)

    # MFA - input PIN
    driver.find_element(By.NAME, 'pin').send_keys(usaa_vars['usaa_pin'])
    driver.find_element(By.CLASS_NAME, 'miam-btn-next').click()
    time.sleep(wait_time)


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

        logging.info(f'{name}: {balance}')
        data[name] = balance

    return data


if __name__ == '__main__':
    main()
