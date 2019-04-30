"""
对cache的管理
"""
from redis import Redis


class TerminalCacheProcessor:
    def __init__(self):
        self.redis_cli = Redis(host='127.0.0.1', port=6379)
        self.name = 'terminal'

    def set_terminal_status(self, key, value, time=10):
        self.redis_cli.set(key, value, ex=time)

    def get_terminal_status(self, key):
        return self.redis_cli.get(key)

    def add_terminal(self, value, time=5):
        self.redis_cli.sadd(self.name, value)
        self.redis_cli.expire(self.name, time)

    def get_all_terminal_name(self):
        return [i.decode() for i in self.redis_cli.smembers(self.name)]


class CookieCacheProcessor:
    def __init__(self):
        self.redis_cli = Redis(host='127.0.0.1', port=6379)
        self.name = 'verification'


    def set_verification(self, value, time=60):
        """
        设置验证码
        :param value:  值
        :param time:  过期时间 默认60s
        :return:
        """
        self.redis_cli.set(self.name, value, ex=time)

    def _get_verification_with_bytes(self):
        return self.redis_cli.get(self.name)

    def get_verification(self):
        verification = self._get_verification_with_bytes()
        if verification:
            return verification.decode()


terminal_cache_processor = TerminalCacheProcessor()
cookie_cache_processor = CookieCacheProcessor()

if __name__ == '__main__':
    cookie_cache_processor.set_verification('cookies')
    print(cookie_cache_processor.get_verification())



