# pynextion
A Python library for Nextion smart display management

Source:
http://wiki.iteadstudio.com/Nextion_Instruction_Set

# Data flow example

Nextion chunk size is 8 byte.

70 68656c6c6f ffff
                  ff = 8 + 1
67 005600c501 ffff
                  ff 65 000101 ffffff = 8 + 8

3 messages, 4 read() operations.
