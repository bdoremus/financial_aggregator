"""
A variety of functions which get reused across other modules.
"""

from dotenv import dotenv_values
from functools import wraps


def retry(max_tries: int = 1, exceptions: Exception = Exception, logger=None):
    """Build a retry decorator

    Return a decorator to retry a function a certain number of times, given (or not) specific exception types, while
    logging retries as a warning.

    Args:
      max_tries (int): the number of times to retry the function
      exceptions (Exception): only retry if these exceptions are raised.  If none, retry on any exception
      logger (Logging.logger): the logger to use when logging the exceptions which cause a retry

    Returns:
        decorator: the decorator which can be used to retry a function
    """
    def retry_decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):
            trials = 0
            while trials < max_tries:
                trials += 1
                try:
                    return function(*args, **kwargs)
                except exceptions as e:
                    if trials >= max_tries:
                        logger.error(f'{e}: max tries ({max_tries}) reached for "{function.__qualname__}"' 
                                     ', raising exception')
                        raise e

                    if logger is not None:
                        logger.warning(f'{e}: retrying "{function.__qualname__}" {max_tries - trials} more times')
        return wrapper

    return retry_decorator


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