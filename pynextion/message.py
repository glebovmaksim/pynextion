# -*- coding: utf-8 -*-

import struct

from .exceptions import *


MESSAGE_CODES = {
    0x01: 'Successful execution of instruction',
    0x65: 'Touch event return data',
    0x66: 'Current page ID number returns',
    0x67: 'Touch coordinate data returns',
    0x68: 'Touch Event in sleep mode',
    0x70: 'String variable data returns',
    0x71: 'Numeric variable data returns',
    0x86: 'Device automatically enters into sleep mode',
    0x87: 'Device automatically wake up',
    0x88: 'System successful start up',
    0x89: 'Start SD card upgrade',
    0xfd: 'Data transparent transmit finished',
    0xfe: 'Data transparent transmit ready'
}


class Message(object):
    def __init__(self, status_code, data):
        self.status_code = status_code
        self.data = data
        self.parsed_data = None

    def raise_for_status(self):
        if self.status_code in EXCEPTION_CODES:
            if EXCEPTION_CODES[self.status_code]['exception_type']:
                raise EXCEPTION_CODES[self.status_code]['exception_type'](EXCEPTION_CODES[self.status_code]['text'])

    def parse(self):
        assert not self.parsed_data, 'Already parsed'

        if self.status_code in (0x01, 0x86, 0x87, 0x88, 0x89, 0xfd, 0xfe):
            return

        # check if message is error
        self.raise_for_status()

        # message is correct, let's parse data
        if self.status_code == 0x65:
            self.parsed_data = {'page_id': ord(self.data[0]),
                                'button_id': ord(self.data[1]),
                                'action': 'press' if self.data[2] == '\x01' else 'release'}

        elif self.status_code == 0x66:
            self.parsed_data = ord(self.data[0])

        elif self.status_code in (0x67, 0x68):
            self.parsed_data = {'x': struct.unpack("<h", self.data[0] + self.data[1]),
                                'y': struct.unpack("<h", self.data[2] + self.data[3]),
                                'action': 'press' if self.data[4] == '\x01' else 'release'}

        elif self.status_code == 0x70:
            return ''.join(self.data)

        elif self.status_code == 0x71:
            self.parsed_data = struct.unpack("<h", ''.join(self.data))

        else:
            raise MessageParseException('Unknown message code: %s', self.status_code)

        return self.parsed_data
