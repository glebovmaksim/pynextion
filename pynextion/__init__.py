# -*- coding: utf-8 -*-

# noinspection PyPackageRequirements
import serial
import binascii
import threading

from concurrent.futures import ThreadPoolExecutor

from .exceptions import UnexpectedMessageCode
from .message import Message
from .utils import wait_for_result


class Nextion(object):
    RED = 63488
    BLUE = 31
    GRAY = 33840
    BLACK = 0
    WHITE = 65535
    GREEN = 2016
    BROWN = 48192
    YELLOW = 65504

    keep_listening = True

    message_listeners = {}

    def __init__(self, port, debug=False, baud_rate=9600, timeout=5, serving_threads=5):
        self._ser = serial.Serial(port=port,
                                  baudrate=baud_rate,
                                  xonxoff=True,
                                  exclusive=True,
                                  timeout=0)  # non_blocking mode
        self.debug = debug
        self.timeout = timeout
        self._message_listener = threading.Thread(target=self._nx_read_messages)
        self._message_listener.start()

        self._callback_executor = ThreadPoolExecutor(serving_threads)
        self.set_variable('bkcmd', 3)

    def close(self):
        self.keep_listening = False
        self._callback_executor.shutdown()

    def set_brightness(self, name):
        self.set_variable('dim', name)

    def set_page(self, name):
        self._nx_write('page ' + str(name))

    def set_visibility(self, elem, is_visible):
        self._nx_write('vis %s, %s' % (elem, is_visible))

    def set_touch_function(self, elem, is_touchable):
        self._nx_write('tsw %s, %s' % (elem, is_touchable))

    @wait_for_result((0x66, ))
    def get_current_page(self):
        self._nx_write('sendme')

    def refresh(self, elem):
        self._nx_write('ref %s' % elem)

    @wait_for_result((0x70, 0x71))
    def get_attr(self, elem, attr):
        self._nx_write('get %s.%s' % (elem, attr))

    def set_attr(self, elem, attr, value):
        self._nx_write('%s.%s=%s' % (elem, attr, value))

    def set_variable(self, key, value):
        self._nx_write(key + '=' + str(value))

    def clear_screen(self, color):
        self._nx_write('cls %s' % color)

    def reset(self):
        self._nx_write('rest')

    def draw_picture(self, x, y, pic_id, width=None, height=None):
        if not width or not height:
            self._nx_write('pic %s,%s,%s' % (x, y, pic_id))
        else:
            self._nx_write('picq %s,%s,%s,%s,%s' % (x, y, pic_id, width, height))

    def draw_string(self, x1, y1, x2, y2, font_id, font_color, background_color,
                    x_center, y_center, sta, string):
        self._nx_write('xstr %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % (
            x1, y1, x2 - x1, y2 - y1, font_id, font_color, background_color, x_center, y_center, sta, string))

    def draw_line(self, x1, y1, x2, y2, color):
        self._nx_write('line %s,%s,%s,%s,%s' % (x1, y1, x2, y2, color))

    def draw_rectangle(self, x1, y1, x2, y2, color):
        self._nx_write('draw %s,%s,%s,%s,%s' % (x1, y1, x2, y2, color))

    def draw_box(self, x1, y1, x2, y2, color):
        self._nx_write('fill %s,%s,%s,%s,%s' % (x1, y1, x2 - x1, y2 - y1, color))

    def draw_circle(self, x, y, r, color, fill=False):
        if not fill:
            self._nx_write('cir %s,%s,%s,%s' % (x, y, r, color))
        else:
            self._nx_write('cirs %s,%s,%s,%s' % (x, y, r, color))

    def eval_code(self, code):
        """
        Can't return values for now
        """
        self._nx_write(code)

    def _nx_write(self, cmd):
        if self.debug:
            print('Bytes waiting in output buffer: %s' % self._ser.out_waiting)
        self._ser.write(chr(255) * 3 + cmd + chr(255) * 3)

    def _nx_read_messages(self):
        buf = ''

        # nextion chunk size is 8 byte
        while self.keep_listening:
            if not self._ser.in_waiting:
                continue

            if self.debug:
                print('Bytes waiting in input buffer: %s' % self._ser.in_waiting)

            # between 'in_waiting' and 'read' data loss can happened if CPU is busy
            try:
                ascii_message = self._ser.read(self._ser.in_waiting)
            except serial.SerialException as ex:
                print('Exception: %s' % str(ex))
                continue

            if self.debug:
                print('Plain ASCII message: %s' % binascii.hexlify(ascii_message))

            buf += ascii_message
            end_message_index = buf.find('\xff' * 3)
            while end_message_index != -1:
                # got end of the message
                status_code = ord(buf[0])
                message_data = buf[1:end_message_index]
                buf = buf[end_message_index + 3:]
                msg = Message(status_code, message_data)
                if self.debug:
                    print('New message received: %s' % msg)
                self._notify_listener(msg)
                # trying to find one more message
                end_message_index = buf.find('\xff' * 3)

    def _notify_listener(self, msg):
            if self.debug:
                print(self.message_listeners)
            listeners = []
            if msg.status_code in self.message_listeners:
                listeners = self.message_listeners[msg.status_code]
            if 255 in self.message_listeners:
                listeners.extend(self.message_listeners[255])
            for listener in listeners:
                if self.debug:
                    print('Submit message %s to callback %s' % (msg, listener))
                self._callback_executor.submit(listener, self, msg)

    def add_message_listener(self, listener, status_codes=(255,)):
        """
        If status_code is not 255 then only messages with
        that particular code will be send to callback.
        Status code with 255 code means subscription to all messages.

        If permanent = False, then only first message will be send
        to callback, after that subscription will be removed.
        If permanent = True, then subscription remains until
        remove_message_listener is not called.
        """
        for status_code in status_codes:
            listeners = self.message_listeners.setdefault(status_code, [])
            if listener not in listeners:
                listeners.append(listener)

    def remove_message_listener(self, listener, status_codes):
        for status_code in status_codes:
            if status_code in self.message_listeners:
                listeners = self.message_listeners[status_code]
                if listener in listeners:
                    listeners.remove(listener)
                    if not listeners:
                        self.message_listeners.pop(status_code)
