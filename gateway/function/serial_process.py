from os import pardir
import serial
from multiprocessing import Process

from utils.logging_processor import LoggingProcessor
from utils import custom_exception


class SerialProcess(Process):
    def __init__(self, data_process_queue, command_process_queue, error_queue):
        """
        串口处理
        :param data_process_queue: 数据处理管道
        :param command_process_queue: 指令处理管道
        :param error_queue: 错误处理管道
        """
        super(SerialProcess, self).__init__()
        self.data_process_queue = data_process_queue
        self.command_process_queue = command_process_queue
        self.error_queue = error_queue

    def run(self):
        logging_processor = LoggingProcessor('SerialReceived', prefix=pardir)
        try:
            # 根据配置文件打开串口
            with open('./serial.conf') as f:
                local_serial_ports = eval(f.read())
            if not local_serial_ports and [i for i in local_serial_ports if
                                           i in ['windows_serial_port', 'linux_serial_port']]:
                raise custom_exception.SerialProcessError(custom_desc='没有目标串口端口号')

            # 打开串口
            local_serial_port = local_serial_ports['windows_serial_port']
            try:
                lora_serial = serial.Serial(local_serial_port, 9600)  # 初始化串口
            except serial.serialutil.SerialException:
                raise custom_exception.SerialProcessError(custom_desc="无法打开目标串口:{}".format(local_serial_port))

        except Exception as e:
            self.error_queue.put(e)
            return

        try:
            while True:
                count = lora_serial.inWaiting()  # 串口接收
                if count:
                    ret = lora_serial.readline()  # readline接受0a
                    logging_processor.write_log("serial_process中的ret为: {}".format(ret))
                    self.data_process_queue.put(ret)  # 将数据存进 数据处理队列 中

                if not self.command_process_queue.empty():
                    ret = self.command_process_queue.get()  # 从 串口写队列 拿出指令
                    logging_processor.write_log("要发送的指令:{}".format(ret))
                    lora_serial.write(ret)
        except Exception as e:
            if lora_serial.is_open:
                lora_serial.close()
            self.error_queue.put(custom_exception.SerialProcessError(custom_desc=str(e)))
        finally:
            if lora_serial.is_open:
                lora_serial.close()
            logging_processor.write_log('串口处理结束', logging_processor.WARNING)


if __name__ == '__main__':
    pass
