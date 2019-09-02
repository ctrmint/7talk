#!/usr/bin/env python
# coding: utf-8
# --------------------------------------------------------------------------------
# CAN data class and various rx related code.
# --------------------------------------------------------------------------------
from __future__ import print_function
import can, sys
import binascii
from itertools import count
from dash_support import *


class Rec_Msg(can.Message):
    """A simple class for the received message"""

    _ids = count(0)                             # packet counter
    arb_counter = {}

    def __init__(self, timestamp, arbitration_id, is_extended_id, is_remote_frame, is_error_frame, channel, dlc,
                 data, is_fd, bitrate_switch):
        super().__init__(timestamp, arbitration_id, is_extended_id, is_remote_frame, is_error_frame, channel, dlc,
                         data, is_fd, bitrate_switch)
        self.rx_val = 0
        self.msg_status = False
        self.data_list = []
        self.rough_str = ""
        self.data_hexstring = []
        self.id_hexstring = "0x00000"
        self.id = next(self._ids)               # increment packet counter
        self.same = True
        self.hex_arbitration_id = hex(self.arbitration_id)

        if self.hex_arbitration_id in self.arb_counter:
            self.arb_counter[self.hex_arbitration_id] += 1
        else:
            if len(self.arb_counter) < 20:
                self.arb_counter[self.hex_arbitration_id] = 1
            else:
                self.arb_counter.popitem()

        if self.dlc > 0:
            self.data_hexstring = binascii.hexlify(self.data)
            for b in self.data:
                self.data_list.append(format(b, "02x"))
                self.rough_str += format(b, "02x")+"."
            self.rough_str = self.rough_str[0:-1]


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
        self.rx_val = 0
        self.buffer.clear()
        self.long_buffer.clear()
        self.high_val = 0
        self.avg_val = 0
        self.change_val()
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


class CoolantTemp(Can_val):
    """ Coolant Temperature class"""
    def __init__(self, name, rx_val):
        super(CoolantTemp, self).__init__(name, rx_val)


class TPSSite(Can_val):
    """ TPS Site class"""
    def __init__(self, name, rx_val):
        super(TPSSite, self).__init__(name, rx_val)


def process_can_message(msgtoprocess):
    rpm_val = "0"
    if str(msgtoprocess).startswith("03.81.") and str(msgtoprocess).endswith(".f8.7c"):
        rpm_val = str(msgtoprocess[9:11]).join(str(msgtoprocess[12:14]))
        print(str(msgtoprocess))
    return str(int(rpm_val, 16))


def receive_can_frame(bus):
    mymessage = Rec_Msg(0.0, 0, False, False, False, 0, 0, [0x00], False, False)
    backupmessage = mymessage
    return_counter = ret_count_val
    control = True
    while control:
        try:
            message = bus.recv(timeout=1)
            if message:
                mymessage = Rec_Msg(message.timestamp, message.arbitration_id, message.is_extended_id,
                                    message.is_remote_frame, message.is_error_frame, message.channel, message.dlc,
                                    message.data, message.is_fd, message.bitrate_switch)
        except can.CanError:
            pass

        if mymessage.dlc == 8:
            mymessage.msg_status = True
            control = False
        else:
            if return_counter > 0:
                return_counter -= 1
            else:
                control = False
                mymessage = backupmessage

    return mymessage.rough_str, mymessage.hex_arbitration_id, mymessage.data_hexstring
