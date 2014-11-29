from itertools import izip, imap
from functools import partial

from .connection import ConnectionPool
from .errors import *  # noqa


def single_str(result):
    if result:
        return result[0]


def single_bool(result):
    if result:
        return True
    return False


def single_int(result):
    if not result:
        return -1
    return int(result[0])


def list_str(result):
    if not result:
        return []
    return result


def dict_str(result):
    if not result:
        return {}
    it = iter(result)
    return dict(izip(it, it))


def dict_int(result):
    if not result:
        return {}
    it = iter(result)
    return dict(izip(it, imap(int, it)))


class SSDBClient(object):

    translators = {
        'auth': single_bool,
        'set': single_bool,
        'setx': single_bool,
        'expire': single_bool,
        'ttl': single_int,
        'setnx': single_bool,
        'get': single_str,
        'getset': single_str,
        'del': single_bool,
        'inc': single_int,
        'exists': single_bool,
        'getbit': single_int,
        'setbit': single_bool,
        'countbit': single_int,
        'substr': single_str,
        'strlen': single_int,
        'keys': list_str,
        'scan': dict_str,
        'rscan': dict_str,
        'multi_set': single_bool,
        'multi_get': dict_str,
        'multi_del': single_bool,
        'hset': single_bool,
        'hget': single_str,
        'hdel': single_bool,
        'hincr': single_int,
        'hexists': single_bool,
        'hsize': single_int,
        'hlist': list_str,
        'hkeys': list_str,
        'hgetall': dict_str,
        'hscan': dict_str,
        'hrscan': dict_str,
        'hclear': single_int,
        'multi_hset': single_bool,
        'multi_hget': dict_str,
        'multi_hdel': single_bool,
        'zset': single_bool,
        'zget': single_int,
        'zdel': single_bool,
        'zincr': single_int,
        'zexists': single_bool,
        'zsize': single_int,
        'zlist': list_str,
        'zkeys': list_str,
        'zscan': dict_int,
        'zrscan': dict_int,
        'zrank': single_int,
        'zrrank': single_int,
        'zrange': dict_int,
        'zrrange': dict_int,
        'zclear': single_int,
        'zcount': single_int,
        'zsum': single_int,
        'zavg': single_int,
        'zremrangebyrank': single_int,
        'zremrangebyscore': single_int,
        'multi_zset': single_bool,
        'multi_zget': dict_int,
        'multi_zdel': single_bool,
        'qsize': single_int,
        'qlist': list_str,
        'qrlist': list_str,
        'qclear': single_bool,
        'qfront': single_str,
        'qback': single_str,
        'qget': single_str,
        'qset': single_bool,
        'qrange': list_str,
        'qslice': list_str,
        'qpush': single_int,
        'qpush_back': single_int,
        'qpop': single_str,
        'qpop_front': single_str,
        'qpop_back': single_str,
        'qtrim_front': single_int,
        'qtrim_back': single_int,
        'dbsize': single_int,
        'info': dict_str
    }

    def __init__(self, host='localhost', port=8888, password=None):
        self.pool = ConnectionPool(host=host, port=port, password=password)

    def execute_command(self, cmd, *args):
        parameters = []
        for arg in args:
            if isinstance(arg, list) or isinstance(arg, tuple):
                for k in arg:
                    parameters.append(k)
            elif isinstance(arg, dict):
                for k, v in arg.items():
                    parameters.append(k)
                    parameters.append(v)
            else:
                parameters.append(arg)
        connection = self.pool.get_connection()
        connection.send_command(cmd, *map(str, parameters))
        result = connection.get_result()
        tr = self.translators.get(cmd)
        if not tr:
            return result
        return tr(result)

    def delete(self, key):
        return self.execute_command('del', key)

    def __getattr__(self, cmd):
        return partial(self.execute_command, cmd)

    def destroy(self):
        self.pool.disconnect()
