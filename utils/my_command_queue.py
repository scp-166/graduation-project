"""
指令队列的单例，需要 import 使用
"""
import queue


class MyCommandQueue(queue.Queue):
    def __init__(self):
        super(MyCommandQueue, self).__init__()


my_command_queue = MyCommandQueue()
