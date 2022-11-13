"""
Gather personal financial information by scraping each website with beautifulsoup.
"""

# Selenium
import undetected_chromedriver.v2 as uc  # port of selenium that websites don't think is a bot
from selenium.webdriver.chrome.service import Service
# Selenium Error handling
# from selenium.common.exceptions import NoSuchElementException, WebDriverException
# from urllib3.exceptions import MaxRetryError
# from requests.exceptions import ConnectionError, ReadTimeout

# External imports
from pathlib import Path
from time import sleep

# Internal imports
from websites.usaa import usaa
from helper_functions import get_env_vars

# Logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    # Open browser
    options = uc.ChromeOptions()
    service = Service("./chromedriver")
    driver = uc.Chrome(options=options, service=service, user_data_dir=Path('temp_selenium.profile'))

    try:
        usaa(driver, **get_env_vars('usaa'))
    finally:
        # ensure the driver window always gets closed
        sleep(1)
        driver.quit()


if __name__ == '__main__':
    main()
