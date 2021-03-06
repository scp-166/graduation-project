import re
from os import pardir
import binascii
from multiprocessing import Process

from utils import custom_exception
from utils.cache_process import cookie_cache_processor, terminal_cache_processor, warning_value_cache_processor
from utils.logging_processor import LoggingProcessor


class DataProcess(Process):
    def __init__(self, serial_read_queue, network_queue, error_queue):
        """
        数据处理
        :param serial_read_queue:
        :param network_queue:
        :param error_queue:
        """
        super(DataProcess, self).__init__()
        self.serial_read_queue = serial_read_queue
        self.network_queue = network_queue
        self.error_queue = error_queue

    def run(self):
        logging_processor = LoggingProcessor('ProcessData', prefix=pardir)
        # 根据配置文件读取分类
        with open('./category.conf') as f:
            terminal_categories = eval(f.read())

        re_pattern = r"([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})([0-9]{2})"
        info_pattern = '{"type":%d, "id":%d, "data":%0.2f, "status":%d, "verf":"%s"}'  # json中值为字符串时需要双引号括起来

        try:
            while True:
                verification = cookie_cache_processor.get_verification()  # 到时候改为用户cookies
                logging_processor.write_log("process_data中的verf为: {}".format(verification))
                ret = self.serial_read_queue.get()  # 从队列中获取串口原样数据
                logging_processor.write_log("process_data中的ret为: {}".format(ret))
                to_decimal_data = str(binascii.hexlify(ret))[2:-1]  # 内容16进制转十进制,str会把开头的b'和末尾的'给同样字符化，所以要去掉
                logging_processor.write_log("process_data中的to_decimal_data为: {}".format(to_decimal_data))
                # 检查类别
                if len(to_decimal_data) == (10 + 8) and to_decimal_data.endswith('ffff9c0a'):
                    ret = re.match(re_pattern, to_decimal_data)  # 对数据进行匹配
                    if ret:  # 正则匹配到需要的数据
                        re_temporary_saved = ret.groups()  # 存储匹配到的值
                        category = re_temporary_saved[0]
                        id = re_temporary_saved[1]

                        # 将终端的信息缓存 terminal_name+category_id+terminal_id
                        key = terminal_categories[int(category)] + category + id  # 目标键值对
                        terminal_cache_processor.set_terminal_status(key, 1, time=1)  # 终端存活1s
                        # 存储进缓存
                        terminal_cache_processor.add_terminal(key)  # 存储曾经存在过的终端名

                        category = int(category)
                        id = int(id)
                        integer = ord(
                            binascii.unhexlify(re_temporary_saved[2]))  # unhexlify('07'->'\x07') ord('\x07'->7)
                        decimal = ord(binascii.unhexlify(re_temporary_saved[3]))
                        data = integer + decimal / 100  # 将整数和小数整合起来

                        # 如果超过预警值，加一次
                        if data >= float(warning_value_cache_processor.get_terminal_warning_value(key)):
                            warning_value_cache_processor.add_terminal_warning_times_once(key)


                        status = int(re_temporary_saved[4])
                        # 对数据进格式化
                        info = info_pattern % (category, id, data, status, verification)  # json格式的str
                        logging_processor.write_log('格式化的内容: {}'.format(info))
                        # 下面要存储进队列中
                        self.network_queue.put(info)
                    else:
                        pass
        except Exception as e:
            self.error_queue.put(custom_exception.DataProcessError(custom_desc=str(e)))
        finally:
            logging_processor.write_log("数据处理结束", level=logging_processor.WARNING)


if __name__ == '__main__':
    pass
