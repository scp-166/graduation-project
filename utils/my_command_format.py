"""
指令格式的单例
"""


class MyCommandFormat:
    def __init__(self, format='{"cmd_catg":%d, "catg":%d, "id":%d, "cmd":%d, "verf":"%s"}'):
        """
       自定义数据帧
        :param format:
        """
        # 此处偷懒不做判断
        self._my_format = format  # 注意值为字符串时需要括号括起来

    @property
    def my_format(self):
        return self._my_format


my_command_format = MyCommandFormat()

