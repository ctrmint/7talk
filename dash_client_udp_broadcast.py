from dash_support import *
import binascii, socket, struct, sys, random
# --------------------------------------------------
# Revised UDP Broadcast version
# --------------------------------------------------

class DataPacket(object):
    """
        ___ UDP Data packet class___
        Instantiated for each packet sent via UDP from the client to the server (Dash display)

        packet contains 4 elements.
            msg_type - positional int from the list of text labels (data_value_labels)
                                                                                used on the Dash and represents data.
            counter - counter 1 - PACKET_COUNTER_LIMIT, incremented per packet, added for monitoring packet reception.
            msg_label - string from (data_value_labels) corresponding to the index value of msg_type.
            msg_value - data value being sent, currently integar, needs revising to support floats etc.

        method send is used construct and pack the data.

        method transmit is used transmit data over a socket to SERVER_ADDR / SERVER_UDP_PORT

        removed previous index use and table.

    """

    def __init__(self, fmt, msg_label, msg_value):
        self.counter = 0
        self.fmt = fmt
        self.msg_label = str(msg_label).ljust(20, " ")
        self.msg_label_b = bytearray(self.msg_label.encode('utf-8'))
        self.msg_value = msg_value
        self.value = (self.counter, self.msg_label_b, self.msg_value)
        self.packed_msg = self.fmt.pack(*self.value)

    def send(self, host, port):
        value = (self.counter, self.msg_label_b, self.msg_value)
        packed_msg = self.fmt.pack(*value)
        self.transmit(packed_msg, host, port)

    def transmit(self, payload, host, port):             # revised broadcast solution, host not required, needs removing
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(1)
        sock.sendto(payload, ('<broadcast>', port))
        return

    def __str__(self):
        return str(self.__class__) + '\n' + '\n'.join(('{} = {}'.format(item,
                                                                        self.__dict__[item]) for item in self.__dict__))



class SendDataController(object):                          # Pretty basic at the moment, just manages the packet counter
    def __init__(self, counter_dict = {}):                     # @ instantiation set up a tracking dictionary
        self.counter_dict = counter_dict                       # This will track instances of each msg type
                                                               # handy for tracking message loss etc.

    def send_packet(self, packet, host, port):
        PACKET_COUNTER_LIMIT = 999
        if packet.msg_label not in self.counter_dict:          # has msg_type (index) been seen before and added to dict
            self.counter_dict.update({packet.msg_label: 0})    # Nope, so add a kv pair to dictionary for msg type index

        current_val = self.counter_dict[packet.msg_label]       # Now inc kv pair to illustrate first msg
        new_val = current_val + 1                              # or 2nd, 3rd and so on.
        if new_val > PACKET_COUNTER_LIMIT : new_val = 0
        self.counter_dict[packet.msg_label] = new_val           # this probably wants to be more efficient!

        packet.counter = new_val                               # now set counter in the packet.
        packet.send(host, port)

    def __str__(self):
        return str(self.__class__) + '\n' + '\n'.join(('{} = {}'.format(item,
                                                                        self.__dict__[item]) for item in self.__dict__))
