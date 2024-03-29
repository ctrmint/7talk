#!/usr/bin/env python
# coding: utf-8
# ----------------------------------------------------------------------------------------------------------------------
# CAN data class and various rx related code.
# ----------------------------------------------------------------------------------------------------------------------
from __future__ import print_function
import can, sys
import binascii
from itertools import count
from dash_support import *


class Can_val(object):
    """  A class to represent the data processed by the dash """
    _ids = count(0)
    buffer_limit = buffer_limit
    debug_print = debug_view

    def __init__(self, name, rx_val):
        self.name = name
        self.rx_val = rx_val
        self.buffer = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.long_buffer = []
        self.high_val = 0.0
        self.avg_val = 0.0
        self.rx_val_inc = True

        if len(self.long_buffer) == 0:
            self.high_val = self.rx_val
            self.avg_val = self.rx_val

    def set_change(self, value):
        self.rx_val = value
        if len(self.buffer) > Can_val.buffer_limit:
            self.buffer.pop(0)
        self.buffer.append(self.rx_val)
        self.change_val()
        return

    def test_change(self, value):
        self.rx_val = self.rx_val + value
        if len(self.buffer) > Can_val.buffer_limit:
            self.buffer.pop(0)
        self.buffer.append(self.rx_val)
        self.change_val()
        return

    def reset_current_val(self, value):
        self.rx_val = value
        if len(self.buffer) > Can_val.buffer_limit:
            self.buffer.pop(0)
        self.buffer.append(self.rx_val)
        self.change_val()
        return

    def wipe(self):
        self.buffer.clear()
        self.long_buffer.clear()
        self.high_val = 0
        self.avg_val = 0
        self.set_change(0)
        return

    def is_high(self):
        if self.rx_val > self.high_val:
            self.high_val = self.rx_val
        return

    def is_increasing(self):
        if self.rx_val < self.buffer[(len(self.buffer))-2]:
            self.rx_val_inc = False
        else:
            self.rx_val_inc = True
        return

    def calc_avg(self):
        self.avg_val = sum(self.long_buffer) / len(self.long_buffer)
        return

    def print_debug(self):
        print(str("----------------------------------------------------------------------------------------------"))
        print('Data name: {:s}'.format(self.name))
        print('Rx value: {:f}'.format(self.rx_val))
        print('Buffer content: {:s}'.format(str(self.buffer)))
        print('Buffer Length: {:d}'.format(len(self.buffer)))
        print('Buffer previous value: {:d}'.format(self.buffer[(len(self.buffer)) - 2]))
        print('Rx value increasing: {:b}'.format(self.rx_val_inc))
        print('Highest value: {:f}'.format(self.high_val))
        print('Average value: {:f}'.format(self.avg_val))
        print('Long buffer: {:s}'.format(str(self.long_buffer)))
        return

    def change_val(self):
        if len(self.long_buffer) == int(sys.maxsize)-1:
            self.long_buffer.pop(0)
        self.long_buffer.append(self.rx_val)
        self.is_increasing()
        self.is_high()
        self.calc_avg()
        if Can_val.debug_print:
            self.print_debug()
        return

    def __str__(self):
        return str(self.__class__) + '\n' + '\n'.join(('{} = {}'.format(item,
                                                                        self.__dict__[item]) for item in self.__dict__))


class Rpmval(Can_val):
    """ Rpm value class"""
    def __init__(self, name, rx_val):
        super(Rpmval, self).__init__(name, rx_val)
