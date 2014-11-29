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
    client.delete(prefix % 'abc')
    assert client.get(prefix % 'abc') is None


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
