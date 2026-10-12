from sentence_transformers import sentence_transformer

import logging

import time

import os

import numpy as np
import tensorflow as tf  # Ensure TensorFlow is imported
from functools import wraps
import threading

from ollama import ChatResponse
logger = logging.getLogger('TraceLog')



Logging_enabled = False

# Thread-local storage for call depth
_local = threading.local()
# Thread-local storage for call depth
_local_prev = threading.local()


def ignore_logging(fn):
    """
    Marker decorator to tell decorate_all_class_methods to skip this specific method.
    """
    fn._ignore_logging = True
    return fn


def decorate_all_class_methods(cls):
    """
    A simple decorator that iterates through all methods of a class 
    and applies the log_decorator unless marked with @ignore_logging.
    """
    # We initialize the log_decorator here with the desired level
    decorator = log_decorator(logging.INFO)

    for attr in cls.__dict__:
        method = getattr(cls, attr)
        if callable(method):
            # Respect the @ignore_logging marker
            if getattr(method, '_ignore_logging', False):
                continue 
            
            setattr(cls, attr, decorator(method))
            
    return cls


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

            # 1. Handle ChatResponse (Extract content AND thinking)
            if isinstance(value, ChatResponse):
                msg = getattr(value, 'message', None)
                if msg:
                    content = getattr(msg, 'content', 'No content')
                    thinking = getattr(msg, 'thinking', 'No thinking')
                    tool_calls = getattr(msg, 'tool_calls', 'No tools')
                    # We use f-strings to keep the newlines exactly as they are in the source
                    return f"[ChatResponse] model={value.model}\nCONTENT:\n{content}\nTHINKING:\n{thinking}\nTOOL CALLS:\n{tool_calls}"
                return f"[ChatResponse] model={value.model}, msg=None"

            """Helper function to format the value for logging."""
            if value is None:
                return "[None]"

            # 1. Handle Heavy Data Structures (Summary only)
            if isinstance(value, np.ndarray):
                return f"[ndarray] shape {value.shape}, dtype {value.dtype}"
            
            if isinstance(value, tf.Tensor):
                return f"[tensor] shape={value.shape}, dtype={value.dtype}"
            
            if isinstance(value, dict):
                return f"[dict] keys={list(value.keys())}"
            
            if isinstance(value, (list, tuple)):
                if len(value) > 0:
                    # Take first 2 elements, convert to string, and slice each to 10 chars
                    preview_items = [str(v)[:10] for v in value[:2]]
                    preview = f"[{', '.join(preview_items)}]"
                else:
                    preview = "empty"
                
                return f"[{type(value).__name__}] len={len(value)}, preview={preview}"

            if isinstance(value, bytes):
                preview = value[:4].hex(' ') 
                return f"[bytes] len={len(value)}, preview=[{preview}...]"

            # 3. Regular Strings (Just return them as-is)
            if isinstance(value, str):
                return f"[str] {value}"

            
            # 3. Fallback for everything else
            return f"[{type(value).__name__}] {value}"

        @wraps(fn)
        def _decorated(*args, **kwargs):



            if Logging_enabled:
                # Format args and kwargs for logging
                formatted_args_list = [_format_log_value(arg) for arg in args]
                formatted_kwargs_dict = {k: _format_log_value(v) for k, v in kwargs.items()}

                args_str = ", ".join(formatted_args_list) if formatted_args_list else "None"
                kwargs_str = ", ".join([f"{k}={v}" for k, v in formatted_kwargs_dict.items()]) if formatted_kwargs_dict else "None"


                # Indentation based on call depth
                indent = "  " * _local.call_depth * 2

                if _local.call_depth != _local_prev.call_depth:
                    logger.info("")
                    _local_prev.call_depth = _local.call_depth


                # 3. Log using the joined strings, NOT the list/dict objects
                logger.log(
                    level,
                    f"{indent} calling '{fn.__qualname__}' with args: {args_str}, kwargs: {kwargs_str}",
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

                # 4. Use the joined strings here as well
                # Re-use the strings we created at the start of the function
                logger.log(
                    level,
                    f"{indent} returning '{fn.__qualname__}' with args: {args_str}, kwargs: {kwargs_str}, got return value: {formatted_ret}",
                )


            return ret
        return _decorated
    return _decorator