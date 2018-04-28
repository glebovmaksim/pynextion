# -*- coding: utf-8 -*-

# noinspection PyPackageRequirements
import serial
import time

from queue import Queue

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

    _ser = debug = BUFFER_SIZE = None
    _message_buffer = []

    def __init__(self, port, debug=False, baud_rate=9600, buffer_size=10):
        self._ser = serial.Serial(port=port,
                                  baudrate=baud_rate,
                                  xonxoff=True,
                                  exclusive=True,
                                  timeout=0)  # non_blocking mode
        self.debug = debug
        self.BUFFER_SIZE = Queue(buffer_size)
        self.set_variable('bkcmd', 3)

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
        msg = self._nx_read_message()
        return msg

    def _nx_read_message(self=None, timeout=5):
        data = []
        status_code = None
        data_end_count = 0
        start_time = time.time()

        if self.debug:
            print('Bytes waiting in input buffer: %s' % self._ser.in_waiting)

        while True:
            if timeout != -1 and time.time() - start_time > timeout:
                raise serial.SerialTimeoutException

            if not self._ser.in_waiting:
                continue

            try:
                ascii_char = self._ser.read()
            except serial.SerialException as ex:
                print(str(ex))
                continue

            if ascii_char is None or ascii_char == "":
                continue

            if ascii_char == '\xff' and not status_code and len(data) == 0:
                continue

            if not status_code:
                # первый байт, который не \xff - это код сообщения
                status_code = ord(ascii_char)
                continue

            if ascii_char == '\xff':
                data_end_count = data_end_count + 1
                if data_end_count == 3:
                    break
            else:
                data_end_count = 0
                data.append(ascii_char)
                if self.debug is True:
                    print(''.join(data))

        return Message(status_code, data)

    def _read(self):
        try:
            while True:
                print(self._nx_read_message(timeout=-1).parse())
        except KeyboardInterrupt:
            pass

    def add_message_listener(self, callback):
        # TODO
        pass

