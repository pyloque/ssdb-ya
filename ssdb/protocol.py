from cStringIO import StringIO

from .errors import *  # noqa


class SimpleCoder(object):

    def __init__(self, sock):
        self.sock = sock
        self.fp = sock.makefile('r')

    def encode(self, *args):
        if not args:
            raise RequestError('empty request')
        buf = StringIO()
        for arg in args:
            if isinstance(arg, str):
                buf.write('%s\n%s\n' % (len(arg), arg))  # write string
            else:
                raise RequestError(
                    'request type %s is not allowed', str(type(arg)))
        buf.write('\n')
        return buf.getvalue()

    def readline(self):
        try:
            line = self.fp.readline()
        except socket.timeout:
            raise TimeoutError('read socket timeout')
        except socket.error as ex:
            raise ConnectionError('read socket error: %s' % str(ex))
        if not line:
            raise ConnectionError('socket is closed')
        if line[-1] != '\n':
            raise self.error(line)
        return line[:-1]

    def read(self, length):
        if length <= 0:
            return
        try:
            return self.fp.read(length)
        except socket.timeout:
            raise TimeoutError('read socket timeout')
        except socket.error as ex:
            raise ConnectionError('read socket error: %s' % str(ex))

    def response(self):
        result = []
        while True:
            block = self.block()
            if block is None:
                break
            result.append(block)
        if not result:
            self.error('empty response')
        status, result = result[0], result[1:]
        if status == 'ok':
            return result
        elif status == 'not_found':
            return
        else:
            raise ServerError('%s %s' % (status, repr(result)))

    def block(self):
        line = self.readline()
        if not line:
            return
        if not line.isdigit():
            self.error(line)
        length = int(line)
        result = ''
        if length:
            result = self.read(length)
        ln = self.read(1)
        if ln != '\n':
            self.error('%s %s' % (result, ln))
        return result

    def error(self, line):
        raise ResponseError('response illegal: %s' % line)
