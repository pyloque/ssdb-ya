from ssdb import SSDBClient

if __name__ == '__main__':
    client = SSDBClient()
    print client.get('abc')
    print client.set('abc', 'test')
    print client.get('abc')
    print client.delete('abc')
    print client.multi_zset('abc', {'a': 5, 'b': 6, 'c': 7})
    print client.multi_zget('abc', ['a', 'b', 'c'])
    print client.zclear('abc')
    print client.multi_hset('abc', {'a': 'x', 'b': 'y', 'c': 'z'})
    print client.multi_hget('abc', ['a', 'b', 'c'])
    print client.hclear('abc')
    client.destroy()
