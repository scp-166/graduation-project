from utils.my_command_queue import my_command_queue
from utils.my_command_format import my_command_format


def write_command(command_category, category, id, command, verification):
    """
    写入指令进队列中
    :param command_category: 指令类别
    :param category: 终端类别
    :param id: 终端编号
    :param command: 具体命令
    :param verification: 验证码
    :return:
    """
    print("write_command: ", my_command_queue)
    my_command_queue.put(my_command_format.my_format % (command_category, category, id, command, verification))


def get_command():
    """
    从队列中获取指令
    :return:
    """
    print("get_command: ", my_command_queue)
    return my_command_queue.get()


if __name__ == '__main__':
    write_command(1,1,1,1,'cookies')
    ret = get_command()
    print(ret)
    print(type(ret))
    import json
    ret = json.loads(ret)
    print(ret)
    print(type(ret))
    pass







