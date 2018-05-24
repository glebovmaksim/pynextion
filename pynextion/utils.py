# -*- coding: utf-8 -*-

import threading

from .exceptions import MessageTimeout, OperationIsNotPermitted


def wait_for_result(status_codes):
    def decorator(func):
        def func_wrapper(*args, **kwargs):
            self = args[0]
            if not self._message_reader.is_alive():
                raise OperationIsNotPermitted('Calling to this method require active listener')

            result = threading.Event()

            # noinspection PyUnusedLocal
            def callback(nextion, msg):
                nextion.remove_message_listener(callback, status_codes)
                result.parsed_data = msg.parse()
                result.set()

            self.add_message_listener(callback,
                                      status_codes=status_codes)
            func(*args, **kwargs)
            result.wait(timeout=self.timeout)
            if not hasattr(result, 'parsed_data'):
                raise MessageTimeout('No response, check logs for errors')
            return result.parsed_data
        return func_wrapper
    return decorator
