import memcache
mc = memcache.Client(['127.0.0.1:11211',], debug=True)

mc.set('username', 'hello world', time=60)

print(mc.get('username'))
