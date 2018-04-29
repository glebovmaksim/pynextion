# -*- coding: utf-8 -*-

import threading


def wait_for_result(status_codes):
    def decorator(func):
        def func_wrapper(*args, **kwargs):
            got_result = threading.Event()

            # noinspection PyUnusedLocal
            def callback(nextion, msg):
                got_result.result = msg.parse()
                got_result.set()

            args[0].add_message_listener(callback,
                                         status_codes=status_codes,
                                         is_permanent=False)
            func(*args, **kwargs)
            got_result.wait()
            return got_result.result

        return func_wrapper
    return decorator
