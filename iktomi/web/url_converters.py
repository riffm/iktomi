# -*- coding: utf-8 -*-

from inspect import isclass
from datetime import datetime

__all__ = ['ConvertError', 'default_converters', 'Converter', 'String',
           'Integer', 'Any', 'Date']


class ConvertError(Exception):

    @property
    def converter(self):
        return self.args[0]

    @property
    def value(self):
        return self.args[1]


class Converter(object):
    '''A base class for urlconverters'''

    regex = '[.a-zA-Z0-9:@&+$,_%%-]+'

    def to_python(self, value, env=None):
        '''
        Accepts unicode url part and returns python object.
        Should be implemented in subclasses
        '''
        raise NotImplementedError()

    def to_url(self, value):
        '''
        Accepts python object and returns unicode prepared to be used
        in url building.
        Should be implemented in subclasses
        '''
        raise NotImplementedError()


class String(Converter):
    '''
    Unquotes urlencoded string.
    '''

    min = 1
    max = None

    def __init__(self, min=None, max=None):
        self.min = min if min is not None else self.min
        self.max = max or self.max

    def to_python(self, value, env=None):
        self.check_len(value)
        return value

    def to_url(self, value):
        return unicode(value)

    def check_len(self, value):
        length = len(value)
        if length < self.min or self.max and length > self.max:
            raise ConvertError(self, value)


class Integer(Converter):
    '''
    Extracts integer value from url part.
    '''

    regex = '[1-9]\d*'

    def to_python(self, value, env=None):
        try:
            value = int(value)
        except ValueError:
            raise ConvertError(self, value)
        else:
            return value

    def to_url(self, value):
        return str(value)


class Any(Converter):

    def __init__(self, *values):
        self.values = values

    def to_python(self, value, env=None):
        if value in self.values:
            return value
        raise ConvertError(self, value)

    def to_url(self, value):
        return unicode(value)


class Date(Converter):

    format = "%Y-%m-%d"

    def __init__(self, format=None):
        if format is not None:
            self.format = format

    def to_python(self, value, env=None):
        try:
            return datetime.strptime(value, self.format).date()
        except ValueError:
            raise ConvertError(self, value)

    def to_url(self, value):
        return value.strftime(self.format)


default_converters = {'string': String,
                      'int': Integer,
                      'any': Any,
                      'date': Date}

# assert all defined converters are registered
for item in globals().values():
    if isclass(item) and \
       issubclass(item, Converter) and \
       not item is Converter:
        assert item in default_converters.values(), item

