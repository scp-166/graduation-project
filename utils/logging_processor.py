"""
对logging的一点小封装
"""
import os
import time
import logging
import multiprocessing
import re

"""
%(levelno)s：打印日志级别的数值
%(levelname)s：打印日志级别的名称
%(pathname)s：打印当前执行程序的路径，其实就是sys.argv[0]
%(filename)s：打印当前执行程序名
%(funcName)s：打印日志的当前函数
%(lineno)d：打印日志的当前行号
%(asctime)s：打印日志的时间
%(thread)d：打印线程ID
%(threadName)s：打印线程名称
%(process)d：打印进程ID
%(message)s：打印日志信息
"""


class LoggingProcessor:
    def __init__(self, name, prefix=os.pardir):
        self._logger_level = self.DEBUG
        self._handler_level = self.DEBUG
        self._formatter_conf = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        self.name = name
        self.logger = logging.getLogger(self.name)
        self.handler = logging.FileHandler(prefix+os.sep+'logging_info'+os.sep+self.name+'_log.txt', encoding='utf-8', mode='w')
        self.formatter = logging.Formatter(self.formatter_conf)

        # 初始化内容
        self._init_attribute()

    @property
    def logger_level(self):
        return self._logger_level

    @property
    def handler_level(self):
        return self._handler_level

    @property
    def formatter_conf(self):
        return self._formatter_conf

    @logger_level.setter
    def logger_level(self, logger_level):
        if not self._is_right(logger_level):
            print("设置错误，请设置正确的日志级别")
            return
        self.logger_level = logger_level
        self._init_attribute()

    @handler_level.setter
    def handler_level(self, handler_level):
        if not self._is_right(handler_level):
            print("设置错误，请设置正确的日志级别")
            return
        self.handler_level = handler_level
        self._init_attribute()

    @formatter_conf.setter
    def formatter_conf(self, formatter_conf):
        # 如果可以，用一个正则判断 %()s
        if not isinstance(formatter_conf, str):
            print("请设置字符串")
        pattern = r'%[(](.*?)[)]s'
        mode_list = re.findall(pattern, formatter_conf)
        print(mode_list)
        if mode_list:  # 匹配到内容
            for mode in mode_list:
                if mode not in self.get_all_mode_list():  # 判断mode是否有问题
                    print("内容有问题")
                    return
            self._formatter_conf = formatter_conf
            print(self._formatter_conf)
            self._init_attribute()
        else:
            print("内容错误，请重新设置")

    def _is_right(self, setting):
        """
        判断setting是不是属于正确的日志级别
        :param setting:
        :return:
        """
        for i in self.get_all_level():
            if setting == i:
                return True
        return False

    def _init_level(self):
        """
        初始化logger和handler的等级
        :return:
        """
        self.logger.setLevel(level=self.logger_level)
        self.handler.setLevel(level=self.handler_level)

    def _init_add_attribute(self):
        """
        给handler添加formatter
        给logger添加handler
        :return:
        """
        self.formatter = logging.Formatter(self.formatter_conf)
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

    def _init_attribute(self):
        """
        给logger等初始化全部功能
        :return:
        """
        self._init_level()
        self._init_add_attribute()

    def write_log(self, info='测试语句', level=logging.DEBUG) :
        """
        写日志
        :param level:
        :param info:
        :return:
        """
        self.logger.log(level, info)

    def get_all_level(self):
        """
        获得所有的日志级别
        :return:
        """
        return [self.INFO, self.DEBUG, self.WARNING, self.ERROR, self.CRITICAL]

    def get_all_mode_list(self):
        """
        formatter需要的格式字符内容
        :return:
        """
        return ['name', 'levelno', 'levelname', 'pathname', 'filename', 'funcName', '1ineno', 'asctime', 'thread', 'threadName', 'process', 'message']

    @ property
    def DEBUG(self):
        return logging.DEBUG

    @property
    def INFO(self):
        return logging.INFO

    @property
    def WARNING(self):
        return logging.WARNING

    @property
    def ERROR(self):
        return logging.ERROR

    @property
    def CRITICAL(self):
        return logging.CRITICAL


def process1():
    print('process1!')
    logger = LoggingProcessor('process1')
    for i in range(10):
        logger.write_log('process1的debug', logger.DEBUG)
    print('process1 over')


def process2():
    print('process2!')
    logger = LoggingProcessor('process2')
    for i in range(10):
        logger.write_log('process2的debug', logger.DEBUG)
    print('process2 over')


if __name__ == '__main__':
    """
    just demo
    """
    t = multiprocessing.Process(target=process1, args=())
    t.daemon = True
    t.start()
    t = multiprocessing.Process(target=process2, args=())
    t.daemon = True
    t.start()
    try:
        while True:
           time.sleep(5)
    except KeyboardInterrupt:
        print("终了")
        exit(0)

