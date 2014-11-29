Yet Another Python Client For ssdb
-----------------------------------

http://ssdb.io

```
    client = SSDBClient()
    client.get('abc')
    client.set('abc', 'test')
    client.get('abc')
    client.delete('abc')
    client.multi_zset('abc', {'a': 5, 'b': 6, 'c': 7})
    client.multi_zget('abc', ['a', 'b', 'c'])
    client.zclear('abc')
    client.multi_hset('abc', {'a': 'x', 'b': 'y', 'c': 'z'})
    client.multi_hget('abc', ['a', 'b', 'c'])
    client.hclear('abc')
    client.destroy()
```
