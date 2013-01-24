from __future__ import print_function

import socket
import threading

from .Voos_message_pb2 import VoosMsg


class KarotzIOHandler(threading.Thread):

    def __init__(self, socket, event_callback=None):
        super(KarotzIOHandler, self).__init__()
        self.daemon = True
        self._socket = socket
        self._event_callback = event_callback

        self._callbacks = {}
        self._conditions = {}
        self._responses = {}

    def send_synchronous(self, msg, timeout=None):
        #print('send_synchronous()', self._msg_to_print(msg))
        if msg.id in self._conditions:
            raise RuntimeError('Message id collision for conditions: %s' % msg.id)
        condition = threading.Condition()
        self._conditions[msg.id] = condition

        condition.acquire()
        self.send(msg, self._callback_synchronous)

        try:
            #print('  wait()')
            condition.wait(timeout)
        except RuntimeError:
            #print('  wait() timed out')
            self._conditions.pop(msg.id)
            return None
        finally:
            condition.release()
        return self._responses.pop(msg.id)

    def _callback_synchronous(self, msg):
        #print('_callback_synchronous()', self._msg_to_print(msg))
        condition = self._conditions.pop(msg.correlationId, None)
        if condition:
            if msg.id in self._responses:
                raise RuntimeError('Response id collision: %s' % msg.id)
            self._responses[msg.correlationId] = msg
            condition.acquire()
            condition.notify()
            condition.release()

    def send(self, msg, callback=None):
        #print('_send()', self._msg_to_print(msg))

        if callback:
            if msg.id in self._callbacks:
                raise RuntimeError('Message id collision for callbacks: %s' % msg.id)
            self._callbacks[msg.id] = callback

        packet = self._build_packet(msg)
        self._socket.send(packet)

    def _build_packet(self, msg):
        packet_data = msg.SerializeToString()
        msg_size = msg.ByteSize()
        packet_header = ''
        for _ in range(3, -1, -1):
            packet_header = chr(msg_size % 256) + packet_header
            msg_size /= 256
        if msg_size != 0:
            assert(False)
        #print('  packet_header:', self._bytes_to_print(packet_header))
        #print('  packet_data:', '4 + %d bytes' % msg.ByteSize(), self._bytes_to_print(packet_data))
        return packet_header + packet_data

    def run(self):
        # process all incoming jobs
        while True:
            msg = self._receive_msg()
            if msg:
                self._receive_callback(msg)

    def _receive_msg(self):
        #print('_receive_msg()')
        packet = self._receive_packet()
        if not packet:
            return None
        #print('_receive_msg() received packet')
        msg = VoosMsg.FromString(packet)
        #print('  msg:', self._msg_to_print(msg))
        return msg

    def _receive_packet(self):
        #print('_receive_packet()')
        try:
            packet_header = self._socket.recv(4)
            #print('  packet_header:', self._bytes_to_print(packet_header))
            msg_size = 0
            for i in range(4):
                msg_size += ord(packet_header[i])
                if i < 3:
                    msg_size *= 256
            #print('  packet_data:', '4 + %d bytes' % msg_size)
            packet_data = self._socket.recv(msg_size)
            #print('  packet_data:', self._bytes_to_print(packet_data))
        except socket.timeout:
            packet_data = None
        return packet_data

    def _receive_callback(self, msg):
        callback = self._callbacks.pop(msg.correlationId, None)
        if callback:
            #print('callback()')
            callback(msg)
        elif msg.buttonCallback.IsInitialized() or msg.rfidCallback.IsInitialized():
            #print('event_callback()')
            if self._event_callback:
                self._event_callback(msg)
        #else:
            #print('ignoring incoming packet', self._msg_to_print(msg))

    def _msg_to_print(self, msg):
        if not msg:
            return str(msg)
        fields = []
        for desc, value in msg.ListFields():
            fields.append('%s: %s' % (desc.name, value))
        return ', '.join(fields)

    def _bytes_to_print(self, data):
        hex_data = ''
        for byte in data:
            hv = hex(ord(byte)).replace('0x', '')
            if len(hv) == 1:
                hex_data += '0'
            hex_data += hv
        return ' '.join([hex_data[i:i + 2] for i in range(0, len(hex_data), 2)])
