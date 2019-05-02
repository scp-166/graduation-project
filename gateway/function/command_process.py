import json
from os import pardir
from multiprocessing import Process

from utils.cache_process import cookie_cache_processor, warning_value_cache_processor
from utils.logging_processor import LoggingProcessor
from utils import custom_exception


class CommandProcess(Process):
    def __init__(self, network_process_queue, serial_write_queue, error_queue):
        """
        指令处理
        :param network_process_queue: 网络处理完毕后的指令管道
        :param serial_write_queue: 串口写管道
        :param error_queue: 错误处理管道
        """
        super(CommandProcess, self).__init__()
        self.network_process_queue = network_process_queue
        self.serial_write_queue = serial_write_queue
        self.error_queue = error_queue

    def run(self):
        logging_processor = LoggingProcessor('CommandProcess', prefix=pardir)
        with open('./category.conf') as f:
            terminal_categories = eval(f.read())
        try:
            while True:
                verification = cookie_cache_processor.get_verification()  # 每次都读取缓存中的验证码
                logging_processor.write_log(
                    "command_process中的verf为: {}".format(verification))

                command = self.network_process_queue.get()  # 从后台指令管道中获取指令
                logging_processor.write_log(
                    "command_process中的原command为: {}".format(command))

                command = json.loads(command)  # 加载指令为dict
                logging_processor.write_log(
                    "command_process中的转换后的command为: {}".format(command))

                server_verification = command.get('verf')  # 获取后台验证码
                logging_processor.write_log(
                    "command_process中的server_verification为: {}".format(
                        server_verification))

                if server_verification and verification == server_verification:  # 验证相同才通过
                    ret = command.get('cmd_catg', None)  # 获得指令类别
                    if ret == 0:  # 仅响应模式 'cmd_caty':0
                        if not command.get('data_received', None):
                            logging_processor.write_log('数据传输成功')
                    elif ret and ret == 1:  # 指令模式 'cmd_caty':1
                        category = command.get('catg', 0)
                        id = command.get('id', 0)
                        cmd = command.get('cmd', 0)
                        end = 'ffff9a0a'  # 结束符

                        rets = [category, id, cmd]
                        process_command = ''.join(['%02x' % ret for ret in
                                                   rets]) + end  # 拼接指令为hex-like str
                        logging_processor.write_log(
                            '拼接的指令为: {}'.format(process_command))

                        # 扔进管道写队列
                        self.serial_write_queue.put(
                            bytes.fromhex(process_command))
                    elif ret and ret == 2:  # 设置预警值模式
                        category = command.get('catg', 0)
                        id = command.get('id', 0)
                        cmd = command.get('cmd', 0)
                        # category_name+category_id+terminal_id
                        key = terminal_categories[
                                 category] + "%02d" % category + "%02d" % id  # 目标键值对
                        # 添加进已被预警终端缓存
                        warning_value_cache_processor.add_have_been_set_warning_value_terminal(key)

                        # 给指定终端设置预警值
                        warning_value_cache_processor.set_terminal_warning_value(key, cmd)

                        logging_processor.write_log("设置{}预警值为{}".format(key, warning_value_cache_processor.get_terminal_warning_value(key)))

                    else:
                        logging_processor.write_log("非关联的指令模式")
                else:
                    logging_processor.write_log("后台验证失败")

        except Exception as e:
            self.error_queue.put(
                custom_exception.CommandProcessError(
                    custom_desc='CommandProcess中出现了未知的错误: {}'.format(str(e))))

        finally:
            logging_processor.write_log("指令处理函数结束",
                                        level=logging_processor.WARNING)
