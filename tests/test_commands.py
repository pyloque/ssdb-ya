import time

from pytest import fixture

from ssdb import SSDBClient


@fixture(scope='module')
def client(request):
    client = SSDBClient()

    def destroy():
        client.destroy()
    request.addfinalizer(destroy)
    return client


@fixture(scope='module')
def prefix():
    import os
    import base64
    return base64.b64encode(os.urandom(64)) + ':%s'


def test_getset(client, prefix):
    client.set(prefix % 'abc', 'zhangyue')
    assert client.get(prefix % 'abc') == 'zhangyue'
    assert client.exists(prefix % 'abc')
    client.delete(prefix % 'abc')
    assert client.get(prefix % 'abc') is None
    assert client.exists(prefix % 'abc') is False


def test_setx(client, prefix):
    client.setx(prefix % 'abc', 'zhangyue', 1)
    assert client.get(prefix % 'abc') == 'zhangyue'
    time.sleep(1.1)
    assert client.get(prefix % 'abc') is None


def test_expire(client, prefix):
    client.set(prefix % 'abc', 'zhangyue')
    client.expire(prefix % 'abc', 2)
    time.sleep(0.5)
    assert client.get(prefix % 'abc') == 'zhangyue'
    assert client.ttl(prefix % 'abc') == 1
    time.sleep(1.6)
    assert client.get(prefix % 'abc') is None


def test_setnx(client, prefix):
    client.set(prefix % 'abc', 'zhangyue')
    client.setnx(prefix % 'abc', 'will not set')
    assert client.get(prefix % 'abc', 'zhangyue')
    client.delete(prefix % 'abc')
    client.setnx(prefix % 'abc', 'willset')
    assert client.get(prefix % 'abc', 'willset')
    client.delete(prefix % 'abc')


def test_zset(client, prefix):
    client.zset(prefix % 'abc', 'x', 10)
    client.zset(prefix % 'abc', 'y', 100)
    client.zset(prefix % 'abc', 'z', 1000)
    values = client.multi_zget(prefix % 'abc', ['x', 'y', 'z'])
    size = client.zsize(prefix % 'abc')
    assert values == {'x': 10, 'y': 100, 'z': 1000}
    assert size == 3
    client.zclear(prefix % 'abc')
    size = client.zsize(prefix % 'abc')
    assert size == 0


def test_hset(client, prefix):
    client.hset(prefix % 'abc', 'x', 'good')
    client.hset(prefix % 'abc', 'y', 'bad')
    client.hset(prefix % 'abc', 'z', 'evil')
    values = client.multi_hget(prefix % 'abc', ['x', 'y', 'z'])
    size = client.hsize(prefix % 'abc')
    assert values == {'x': 'good', 'y': 'bad', 'z': 'evil'}
    assert size == 3
    client.hclear(prefix % 'abc')
    size = client.zsize(prefix % 'abc')
    assert size == 0


def test_queue(client, prefix):
    client.qpush(prefix % 'abc', 'x')
    client.qpush(prefix % 'abc', 'y')
    client.qpush(prefix % 'abc', 'z')
    assert client.qsize(prefix % 'abc') == 3
    assert client.qpop(prefix % 'abc') == 'x'
    assert client.qpop(prefix % 'abc') == 'y'
    assert client.qpop(prefix % 'abc') == 'z'
    assert client.qsize(prefix % 'abc') == 0


def test_str(client, prefix):
    client.setbit(prefix % 'abc', 0, 1)
    client.setbit(prefix % 'abc', 1, 0)
    client.setbit(prefix % 'abc', 2, 1)
    assert client.getbit(prefix % 'abc', 0) == 1
    assert client.getbit(prefix % 'abc', 1) == 0
    assert client.getbit(prefix % 'abc', 2) == 1
    assert client.countbit(prefix % 'abc') == 2
    client.set(prefix % 'abc', 'abcdefg')
    assert client.strlen(prefix % 'abc', 7)
    assert client.substr(prefix % 'abc', 2, 3) == 'cde'
