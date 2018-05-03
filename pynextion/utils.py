# -*- coding: utf-8 -*-

import threading

from .exceptions import MessageTimeout, OperationIsNotPermitted


def wait_for_result(status_codes):
    def decorator(func):
        def func_wrapper(*args, **kwargs):
            self = args[0]
            if not self._message_reader.is_alive():
                raise OperationIsNotPermitted('Calling to this method require active listener')

            got_result = threading.Event()

            # noinspection PyUnusedLocal
            def callback(nextion, msg):
                got_result.result = msg.parse()
                got_result.set()
                nextion.remove_message_listener(callback, status_codes)

            self.add_message_listener(callback,
                                      status_codes=status_codes)
            func(*args, **kwargs)
            got_result.wait(timeout=self.timeout)
            if not hasattr(got_result, 'result'):
                raise MessageTimeout
            return got_result.result
        return func_wrapper
    return decorator
