import logging

import time

import os

import numpy as np
import tensorflow as tf  # Ensure TensorFlow is imported
from functools import wraps
import threading
logger = logging.getLogger('TraceLog')



Logging_enabled = False

# Thread-local storage for call depth
_local = threading.local()
# Thread-local storage for call depth
_local_prev = threading.local()

def decorate_all_class_methods():
    """
    If you smack the decorator argument "@decorate_all_class_methods(log_decorator(logging.INFO))" in front of a class it decorates all methods within the class :D
    """
    decorator = log_decorator(logging.INFO)

    def decorate(cls):
        for attr in cls.__dict__: # there's propably a better way to do this
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls
    return decorate



def generate_logger_file():
    log_folder = "logs"  # Name of the log folder
    timestamp = int(time.time())  # Current time in seconds
    log_filename = log_folder + f'/log_{timestamp}.log'

    # Create the log folder if it doesn't exist
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)


    logging.info(f"Created log folder: {log_folder}")

    logging.basicConfig(
        filename=log_filename,  # Log file name
        level=logging.INFO,            # Log level (INFO, DEBUG, ERROR, etc.)
        format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
        force=True
    )

    # Initialize call depth if not present
    if not hasattr(_local, 'call_depth'):
        _local.call_depth = 0

    # Initialize call depth if not present
    if not hasattr(_local_prev, 'call_depth'):
        _local_prev.call_depth = 0

    global Logging_enabled
    Logging_enabled = True




def log_decorator(level):
    def _decorator(fn):
        def _format_log_value(value):
            """Helper function to format the value for logging."""
            if isinstance(value, np.ndarray):
                return f"numpy.ndarray with shape {value.shape}, dtype {value.dtype}"
            elif isinstance(value, tf.Tensor):
                return f"tf.Tensor with shape {value.shape}, dtype {value.dtype}"
            elif isinstance(value, dict):
                return f"dict with keys: {list(value.keys())}"
            elif isinstance(value, tuple):
                return f"tuple with length: {len(value)}"
            elif isinstance(value, list):
                return f"list with length: {len(value)}"
            else:
                return f"type \"{type(value)}\" with value - {value}"

        @wraps(fn)
        def _decorated(*args, **kwargs):



            if Logging_enabled:
                # Format args and kwargs for logging
                formatted_args = [_format_log_value(arg) for arg in args]
                formatted_kwargs = {k: _format_log_value(v) for k, v in kwargs.items()}


                # Indentation based on call depth
                indent = "  " * _local.call_depth * 2

                if _local.call_depth != _local_prev.call_depth:
                    logger.info("")
                    _local_prev.call_depth = _local.call_depth


                # Log the function call with indentation
                logger.log(
                    level,
                    f"{indent} calling '{fn.__qualname__} with args: {formatted_args}, kwargs: {formatted_kwargs}",
                )

                # Increment call depth
                _local.call_depth += 1


            ret = fn(*args, **kwargs)


            if Logging_enabled:

                # Decrement call depth
                _local.call_depth -= 1
                
                # Format the return value for logging
                formatted_ret = _format_log_value(ret)

                if _local.call_depth != _local_prev.call_depth:
                    logger.info("")
                    _local_prev.call_depth = _local.call_depth

                # Log the function return with indentation
                logger.log(
                    level,
                    f"{indent} returning '{fn.__qualname__} with args: {formatted_args}, kwargs: {formatted_kwargs}, got return value: {formatted_ret}",
                )


            return ret
        return _decorated
    return _decorator