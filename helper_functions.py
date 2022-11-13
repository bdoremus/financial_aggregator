from functools import partial, wraps


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
                        raise e

                    if logger is not None:
                        logger.warning(f'{e}: retrying {max_tries - trials} more times')
        return wrapper

    return retry_decorator
