# -*- coding: utf-8 -*-


class NextionException(Exception):
    pass


class MessageParseException(NextionException):
    pass


class MessageTimeout(NextionException):
    pass


class UnexpectedMessageCode(NextionException):
    pass


EXCEPTION_CODES = {
    0x00: {'text': 'Invalid instruction',
           'exception_type': NextionException},
    0x02: {'text': 'Component ID invalid',
           'exception_type': NextionException},
    0x03: {'text': 'Page ID invalid',
           'exception_type': NextionException},
    0x04: {'text': 'Picture ID invalid',
           'exception_type': NextionException},
    0x05: {'text': 'Font ID invalid',
           'exception_type': NextionException},
    0x11: {'text': 'Baud rate setting invalid',
           'exception_type': NextionException},
    0x12: {'text': 'Curve control ID number or channel number is invalid',
           'exception_type': NextionException},
    0x1a: {'text': 'Variable name invalid',
           'exception_type': NextionException},
    0x1b: {'text': 'Variable operation invalid',
           'exception_type': NextionException},
    0x1c: {'text': 'Failed to assign',
           'exception_type': NextionException},
    0x1d: {'text': 'Operate EEPROM failed',
           'exception_type': NextionException},
    0x1e: {'text': 'Parameter quantity invalid',
           'exception_type': NextionException},
    0x1f: {'text': 'IO operation failed',
           'exception_type': NextionException},
    0x20: {'text': 'Undefined escape characters',
           'exception_type': NextionException},
    0x23: {'text': 'Too long variable name',
           'exception_type': NextionException}
}
