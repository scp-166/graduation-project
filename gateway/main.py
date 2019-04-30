import sys
sys.path.append("..")
import multiprocessing

from function.command_process import CommandProcess
from function.data_process import DataProcess
from function.network_connect import *
from function.serial_process import SerialProcess

if __name__ == '__main__':
    serial_process__and_data_process_queue = multiprocessing.Queue()  # 队列1 LoRa串口接收函数和数据处理函数
    data_process_and_network_process_queue = multiprocessing.Queue()  # 队列2 数据处理函数和数据发送函数
    network_process_and_command_process_queue = multiprocessing.Queue()  # 队列3 指令接收函数和指令处理函数
    command_process_and_serial_process_queue = multiprocessing.Queue()  # 队列4 指令处理函数和LoRa串口接受函数
    error = multiprocessing.Queue()  # 存放自定义异常的队列
    try:

        t1 = SerialProcess(serial_process__and_data_process_queue, command_process_and_serial_process_queue, error)
        t1.daemon = True
        t1.start()

        alist = list()
        for i in range(2):
            t = DataProcess(serial_process__and_data_process_queue, data_process_and_network_process_queue, error)
            t.daemon = True
            alist.append(t)

        for i in alist:
            i.start()

        t3 = CommandProcess(network_process_and_command_process_queue, command_process_and_serial_process_queue, error)
        t3.daemon = True
        t3.start()

        t4 = NetWorkProcess(data_process_and_network_process_queue, network_process_and_command_process_queue, error)
        t4.daemon = True
        t4.start()

        while True:
            try:
                raise error.get()
            except custom_exception.SerialProcessError as e:
                print(e)
                raise KeyboardInterrupt
            except custom_exception.DataProcessError as e:
                print(e)
                raise KeyboardInterrupt
            except custom_exception.NetWorkProcessError as e:
                print(e)
                raise KeyboardInterrupt
            except custom_exception.CommandProcessError as e:
                print(e)
                raise KeyboardInterrupt
            except Exception as e:
                print(e)
                raise KeyboardInterrupt

    except KeyboardInterrupt:
        print("一秒后退出")
        time.sleep(1)
        serial_process__and_data_process_queue.close()
        data_process_and_network_process_queue.close()
        network_process_and_command_process_queue.close()
        command_process_and_serial_process_queue.close()
        error.close()
        print("程序退出")
        sys.exit()
