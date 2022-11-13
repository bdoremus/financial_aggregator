"""
Gather personal financial information by scraping each website with beautifulsoup.
"""

import undetected_chromedriver.v2 as uc  # port of selenium that websites don't think is a bot
from selenium.webdriver.chrome.service import Service

from dotenv import dotenv_values
from pathlib import Path
from time import sleep

# Error handling
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from urllib3.exceptions import MaxRetryError
from requests.exceptions import ConnectionError, ReadTimeout


# Pages
from websites.usaa import usaa

# Logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    # Open browser
    options = uc.ChromeOptions()
    # options.headless = True
    service = Service("./chromedriver")
    driver = uc.Chrome(options=options, service=service, user_data_dir=Path('temp_selenium.profile'))

    try:
        usaa(driver, **get_env_vars('usaa'))
    except:
        raise
    finally:
        sleep(1)
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


if __name__ == '__main__':
    main()
