Yet Another Python Client For ssdb
-----------------------------------

http://ssdb.io

```
    client = SSDBClient()
    client.get('abc')
    client.set('abc', 'test')
    client.exists('abc')
    client.delete('abc')
    client.setx('abc', 'test', 2)
    client.expire('abc', 2)
    client.ttl('abc')
    client.multi_zset('abc', {'a': 5, 'b': 6, 'c': 7})
    client.multi_zget('abc', ['a', 'b', 'c'])  # return {'a': 5, 'b': 6, 'c': 7}
    client.multi_zget('abc', 'a', 'b', 'c')  # return {'a': 5, 'b': 6, 'c': 7}
    client.zclear('abc')
    client.multi_hset('abc', {'a': 'x', 'b': 'y', 'c': 'z'})
    client.multi_hget('abc', ['a', 'b', 'c'])  # return {'a': 'x', 'b': 'y', 'c': 'z'}
    client.multi_hget('abc', 'a', 'b', 'c')  # return {'a': 'x', 'b': 'y', 'c': 'z'}
    client.hclear('abc')
    client.qpush('abc', 'x')
    client.qpop('abc')
    client.qsize()
    client.dbsize()
    client.multi_set({'x': '1', 'y': '2', 'z': '3'})
    client.multi_get(['x', 'y', 'z'])
    client.multi_get('x', 'y', 'z')
    client.destroy()
```

install ssdb in localhost with default settings

run full testcases with following commands

```
    virtualenv .py
    source hello
    easy_install pytest
    python setup.py test
```
