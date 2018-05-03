import os
from setuptools import setup


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


setup(
    name='pynextion',
    version='0.0.1',
    author='Glebov Maksim',
    author_email='glebovmaksim@gmail.com',
    description='Python library for Nextion display interactions',
    license='Apache 2.0',
    url='http://packages.python.org/pynextion',
    packages=['pynextion'],
    long_description=read('README.md'),
    install_requires=['pyserial>=3.4', 'futures>=3.2.0'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'License :: OSI Approved :: Apache 2.0 License',
    ],
)
