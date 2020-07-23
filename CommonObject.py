"""
Function: Code for common functions and libraries
Python Ver: 2.7
Author: Taewoo Kim
Contact: twkim0812@gmail.com
"""

import numpy as np
import socket, json


def r2d(rad):
    return rad * (180.0/np.pi)


def d2r(deg):
    return deg * (np.pi/180.0)


class SocketCom:
    def __init__(self, ipAddr, portNum):
        self.ipAddr = ipAddr
        self.portNum = portNum
        self.sock = None
        self.addr = ''

        self.read_buffer = ''

    def open_host(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.ipAddr, self.portNum))
        self.sock.listen(4)  # total number of clients to access this server.
        conn, addr = self.sock.accept()
        self.sock = conn
        self.addr = addr

    def socket_connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.ipAddr, self.portNum))

    def write_socket(self, objects):
        data = json.dumps(objects).encode('utf-8')
        self.sock.sendall(data)

    def read_socket(self, cut_start=None, cut_end=None):
        frac = ''
        while len(self.read_buffer) < 5000:
            if not cut_start or not cut_end:
                frac = self.read_buffer
                self.read_buffer = ''
                break
            try:
                i1 = self.read_buffer.index(cut_start)
                i2 = self.read_buffer.index(cut_end)
                frac = self.read_buffer[i1:i2+1]
                self.read_buffer = self.read_buffer[i2+1:]
                break
            except ValueError:
                self.read_buffer += self.sock.recv(1024).decode('utf-8')  # Python3.x: byte, Python2.x: string, decode from byte to unicode
                continue

        # return frac
        return json.loads(frac)   # for Python 3.x

    # Only for the Choregraphe_Train.py
    def read_socket2(self, cut_start=None, cut_end=None):
        frac = ''
        while len(self.read_buffer) < 5000:
            self.read_buffer += json.loads(self.sock.recv(1024).decode(
                'utf-8'))  # Python3.x: byte, Python2.x: string, decode from byte to unicode

            print('type: ', type(self.read_buffer), 'len: ', len(self.read_buffer), 'buffer: ', self.read_buffer)
            if not cut_start or not cut_end:
                frac = self.read_buffer
                self.read_buffer = ''
                print 'if not!!'
                break
            try:
                i1 = self.read_buffer.index(cut_start)
                i2 = self.read_buffer.index(cut_end)
                frac = self.read_buffer[i1:i2 + 1]
                self.read_buffer = self.read_buffer[i2 + 1:]
                print 'try!!!'
                break
            except ValueError:
                continue
        # print('type: ', type(frac), 'len: ', len(frac), 'frac: ', frac)
        # print('type: ', type(self.read_buffer), 'len: ', len(self.read_buffer), 'buffer: ', self.read_buffer)
        return frac
        # return json.loads(frac)   # for Python 3.x

    def socket_close(self):
        if self.sock:
            self.sock.close()
