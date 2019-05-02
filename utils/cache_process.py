"""
对cache的管理
"""
from redis import Redis
import time as sys_time


class WarningValueCacheProcessor:
    def __init__(self):
        self.redis_cli = Redis(host='127.0.0.1', port=6379)
        self.name = 'have_been_set_warning_value_terminals'
        self.times_key = 'warning_times'  # 扩展名称1
        self.value_key = 'warning_value'  # 扩展名称2
        self.max_time = 10  # 顶峰次数
        # 调用自身函数时请使用原key

    def set_terminal_warning_value(self, key, value):
        """
        设置指定终端预警值
        :param key:
        :param value:
        :return:
        """
        new_key = key + self.value_key
        self.redis_cli.set(new_key, value)

    def get_terminal_warning_value(self, key):
        """
        获得指定终端的预警值
        :param key:
        :return:
        """
        new_key = key + self.value_key
        return self.redis_cli.get(new_key).decode() if self.redis_cli.get(new_key) is not None else None

    def add_terminal_warning_times_once(self, key, time=10):
        """
        增加指定终端预警一次
        :param key:
        :param value:
        :param time: 仅十秒，和self.max_times相关
        :return:
        """
        new_key = key + self.times_key  # 补充键名称
        if self.get_terminal_warning_times(key) is None:  # 没有则添加
            self.redis_cli.set(new_key, 1, time)
        else:
            count = self.get_terminal_warning_times(key)  # 有则加次数
            if int(count)+1 > self.max_time:  # 超过警戒线
                print("设备{}在{}时刻连续超过预警线{}共{}次,请即使处理!".
                      format(key, sys_time.localtime(sys_time.time()),
                             self.get_terminal_warning_value(key), self.max_time))
                self.redis_cli.set(new_key, 1, time)
            else:
                self.redis_cli.set(new_key, int(count)+1, time)

    def get_terminal_warning_times(self, key):
        """
        获得指定终端预警次数
        :param key:
        :return:
        """
        new_key = key + self.times_key  # 补充键名称
        return self.redis_cli.get(new_key).decode() if self.redis_cli.get(new_key) is not None else None

    def add_have_been_set_warning_value_terminal(self, value):
        """
        添加被预警过的终端
        :param value:
        :param time:
        :return:
        """
        self.redis_cli.sadd(self.name, value)

    def get_all_have_been_set_warning_value_terminal_name(self):
        """
        获得所有被预警过的终端的名称
        :return:
        """
        return [i.decode() for i in self.redis_cli.smembers(self.name)]


class TerminalCacheProcessor:
    def __init__(self):
        self.redis_cli = Redis(host='127.0.0.1', port=6379)
        self.name = 'active_terminal'

    def set_terminal_status(self, key, value, time=10):
        """
        key对应的终端是否处于激活状态
        :param key:
        :param value:
        :param time:
        :return:
        """
        self.redis_cli.set(key, value, ex=time)

    def get_terminal_status(self, key):
        return self.redis_cli.get(key)

    def add_terminal(self, value, time=5):
        """
        曾经存在过的终端
        :param value:
        :param time:
        :return:
        """
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


warning_value_cache_processor = WarningValueCacheProcessor()
terminal_cache_processor = TerminalCacheProcessor()
cookie_cache_processor = CookieCacheProcessor()

if __name__ == '__main__':
    cookie_cache_processor.set_verification('cookies')
    print(cookie_cache_processor.get_verification())



