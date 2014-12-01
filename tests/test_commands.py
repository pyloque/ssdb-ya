import time

from pytest import fixture, raises

from ssdb import SSDBClient, errors


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


def test_invalid_command(client, prefix):
    with raises(errors.ServerError):
        client.invalid('a', 'b', 'c')


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
    assert client.zexists(prefix % 'abc', 'x')
    client.zincr(prefix % 'abc', 'x', 20)
    assert client.zget(prefix % 'abc', 'x') == 30
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
    assert client.hexists(prefix % 'abc', 'x')
    client.hset(prefix % 'abc', 'x', 2)
    assert client.hget(prefix % 'abc', 'x') == '2'
    client.hincr(prefix % 'abc', 'x', 3)
    assert client.hget(prefix % 'abc', 'x') == '5'
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


def test_multi(client, prefix):
    data = {'x': 'a', 'y': 'b', 'z': 'c'}
    client.multi_set(data)
    values = client.multi_get(data.keys())
    assert values == data
    client.multi_del(data.keys())
    values = client.multi_get(data.keys())
    assert values == {}


def test_scan(client, prefix):
    data = {prefix % 'abc' + str(i): str(i) for i in range(10)}
    client.multi_set(data)
    values = client.keys(prefix % 'abc3', prefix % 'abc6', 10)
    assert values == [prefix % 'abc4', prefix % 'abc5', prefix % 'abc6']
    values = client.scan(prefix % 'abc3', prefix % 'abc6', 10)
    assert values == {
        prefix % 'abc4': '4',
        prefix % 'abc5': '5',
        prefix % 'abc6': '6'
    }
    values = client.rscan(prefix % 'abc6', prefix % 'abc3', 10)
    assert values == {
        prefix % 'abc5': '5',
        prefix % 'abc4': '4',
        prefix % 'abc3': '3'
    }
