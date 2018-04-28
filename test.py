import pynextion

nextion = pynextion.Nextion('/dev/ttyAMA0', True)
print(nextion.get_attr('b0', 'txt'))

nextion.set_variable('sendxy', 1)
