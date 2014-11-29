# -*- coding: utf-8 -*-

import os
import socket
import threading

from Queue import LifoQueue, Full, Empty

from .errors import *  # noqa
from .protocal import SimpleCoder  # noqa


class Connection(object):

    def __init__(
        self, host='localhost', port='8888', password=None,
            coder_class=SimpleCoder, connect_timeout=5, timeout=5):
        self.host = host
        self.port = port
        self.password = password
        self.pid = os.getpid()
        self.coder_class = coder_class
        self.connect_timeout = connect_timeout
        self.timeout = timeout
        self.sock = None
        self.connect()

    def connect(self):
        if self.sock:
            return
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.settimeout(self.connect_timeout)
            sock.connect((self.host, self.port))
            sock.settimeout(self.timeout)
        except socket.error as ex:
            raise ConnectionError(
                'connection cannot be established: %s', str(ex))
        self.sock = sock
        self.on_connect()

    def on_connect(self):
        self.coder = self.coder_class(self.sock)
        if not self.password:
            return
        self.send_command('auth', self.password)

    def send_command(self, *args):
        try:
            self.sock.sendall(self.coder.encode(*args))
        except socket.timeout:
            raise TimeoutError('write socket timeout')
        except socket.error as ex:
            self.disconnect()
            raise ConnectionError(
                'write socket error, close socket: %s' % str(ex))
        except Exception as ex:
            self.disconnect()
            raise SSDBError('unknow error, close socket: %s', str(ex))

    def get_result(self):
        try:
            return self.coder.response()
        except (ConnectionError, ResponseError, TimeoutError) as ex:
            self.disconnect()
            raise ex

    def disconnect(self):
        if self.sock is None:
            return
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        except socket.error:
            pass
        self.sock = None

    def __del__(self):
        self.disconnect()


class ConnectionPool(object):

    def __init__(
        self, connection_class=Connection,
            max_connections=1024, timeout=5, **connection_kwargs):
        self.connection_class = connection_class
        self.max_connections = max_connections
        self.connection_kwargs = connection_kwargs
        self.timeout = timeout
        self.connections = []
        self.reset()

    def ensure_safe(self):
        if self.pid != os.getpid():
            with self.ensure_lock:  # lock for concurrent threadings
                if self.pid == os.getpid():  # double check
                    return
                self.disconnect()
                self.reset()

    def get_connection(self):
        self.ensure_safe()
        try:
            connection = self.queue.get(block=True, timeout=self.timeout)
        except Empty:
            raise ConnectionError('connection pool is full')
        if not connection:
            connection = self.make_connection()
        return connection

    def make_connection(self):
        connection = self.connection_class(**self.connection_kwargs)
        self.connections.append(connection)
        return connection

    def release(self, connection):
        self.ensure_safe()
        if connection.pid != self.pid:
            return
        try:
            self.queue.put_nowait(connection)
        except Full:
            pass

    def reset(self):
        self.pid = os.getpid()
        self.ensure_lock = threading.Lock()
        self.disconnect()
        # LifoQueue make use of released connections
        self.queue = LifoQueue(self.max_connections)
        self.connections = []
        while True:
            try:
                self.queue.put_nowait(None)
            except Full:
                break

    def disconnect(self):
        for connection in self.connections:
            connection.disconnect()
