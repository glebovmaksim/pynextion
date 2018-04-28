# -*- coding: utf-8 -*-

# noinspection PyPackageRequirements
import serial
import binascii
import time

import threading

from .exceptions import UnexpectedMessageCode
from .message import Message


class Nextion(object):
    RED = 63488
    BLUE = 31
    GRAY = 33840
    BLACK = 0
    WHITE = 65535
    GREEN = 2016
    BROWN = 48192
    YELLOW = 65504

    _ser = debug = None
    _keep_listening = True
    _message_listener = None
    _last_message = None

    def __init__(self, port, debug=False, baud_rate=9600):
        self._ser = serial.Serial(port=port,
                                  baudrate=baud_rate,
                                  xonxoff=True,
                                  exclusive=True,
                                  timeout=0)  # non_blocking mode
        self.debug = debug
        self._message_listener = threading.Thread(target=self._nx_read_messages)
        self._message_listener.start()
        self.set_variable('bkcmd', 3)

    def close(self):
        self._keep_listening = False

    def set_brightness(self, name):
        self.set_variable('dim', name)

    def set_page(self, name):
        msg = self._nx_write('page ' + str(name))
        msg.raise_for_status()

    def get_current_page(self):
        msg = self._nx_write('sendme')
        return msg.parse()

    def refresh(self, elem):
        msg = self._nx_write('ref %s' % elem)
        msg.raise_for_status()

    def get_attr(self, elem, attr):
        msg = self._nx_write('get %s.%s' % (elem, attr))
        return msg.parse()

    def set_attr(self, elem, attr, value):
        msg = self._nx_write('%s.%s=%s' % (elem, attr, value))
        msg.raise_for_status()

    def clear_screen(self, color):
        msg = self._nx_write('cls %s' % color)
        msg.raise_for_status()

    def draw_picture(self, x, y, pic_id, width=None, height=None):
        if not width or not height:
            msg = self._nx_write('pic %s,%s,%s' % (x, y, pic_id))
        else:
            msg = self._nx_write('picq %s,%s,%s,%s,%s' % (x, y, pic_id, width, height))
        msg.raise_for_status()

    def draw_string(self, x1, y1, x2, y2, font_id, font_color, background_color,
                    x_center, y_center, sta, string):
        msg = self._nx_write('xstr %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % (
            x1, y1, x2 - x1, y2 - y1, font_id, font_color, background_color, x_center, y_center, sta, string))
        msg.raise_for_status()

    def draw_line(self, x1, y1, x2, y2, color):
        msg = self._nx_write('line %s,%s,%s,%s,%s' % (x1, y1, x2, y2, color))
        msg.raise_for_status()

    def draw_rectangle(self, x1, y1, x2, y2, color):
        msg = self._nx_write('draw %s,%s,%s,%s,%s' % (x1, y1, x2, y2, color))
        msg.raise_for_status()

    def draw_box(self, x1, y1, x2, y2, color):
        msg = self._nx_write('fill %s,%s,%s,%s,%s' % (x1, y1, x2 - x1, y2 - y1, color))
        msg.raise_for_status()

    def draw_circle(self, x, y, r, color, fill=False):
        if not fill:
            msg = self._nx_write('cir %s,%s,%s,%s' % (x, y, r, color))
        else:
            msg = self._nx_write('cirs %s,%s,%s,%s' % (x, y, r, color))
        msg.raise_for_status()

    def set_variable(self, key, value):
        msg = self._nx_write(key + '=' + str(value))
        msg.raise_for_status()

    def _nx_write(self, cmd):
        if self.debug:
            print('Bytes waiting in output buffer: %s' % self._ser.out_waiting)
        self._ser.write(chr(255) * 3 + cmd + chr(255) * 3)
        # FIXME
        time.sleep(1)
        msg = self._last_message
        return msg

    def _nx_read_messages(self, timeout=-1):
        buf = ''
        start_time = time.time()

        # nextion chunk size is 8 byte
        try:
            while self._keep_listening:
                if timeout != -1 and time.time() - start_time > timeout:
                    raise serial.SerialTimeoutException

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
                    # got end of message
                    status_code = ord(buf[0])
                    message_data = buf[1:end_message_index]
                    buf = buf[end_message_index + 3:]
                    self._last_message = Message(status_code, message_data)
                    if self.debug:
                        print('New message received: %s' % self._last_message)
                    # trying to find one more message
                    end_message_index = buf.find('\xff' * 3)

        except KeyboardInterrupt:
            pass

    def add_message_listener(self, callback):
        # TODO
        pass
