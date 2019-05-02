import abc


class BaseBridge:
    """
    前后端websocket通信
    需要区分功能
        树莓派 发送 数据给后端
        后端 定时发指令 给 树莓派
        前端 控制 指令

    """

    def __init__(self, websocket):
        """初始化内容"""
        self._websocket = websocket
        self._tasks = []  # 需要执行的任务

    @abc.abstractmethod
    def open(self):
        """
        假如有初始化
        :return:
        """

    @abc.abstractmethod
    def _forward_inbound(self):
        """
        前端->后端
        :param channel:
        :return:
        """

    @abc.abstractmethod
    def _forward_outbound(self, flag):
        """
        后端->前端
        :param channel:
        :return:
        """

    @abc.abstractmethod
    def close(self):
        """
        结束桥接会话
        :return:
        """

    def start(self):
        """
        启动
        :return:
        """


