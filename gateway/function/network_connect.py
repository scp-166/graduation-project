import time
from os import pardir
import queue
import threading
from multiprocessing import Process

from websocket import create_connection
import websocket

from utils import custom_exception
from utils.cache_process import cookie_cache_processor, terminal_cache_processor
from utils.logging_processor import LoggingProcessor
from .session_token import auth_processor


class NetWorkProcess(Process):
    def __init__(self, data_process_queue, command_process_queue, error_queue):
        super(NetWorkProcess, self).__init__()
        self.data_process_queue = data_process_queue
        self.command_process_queue = command_process_queue
        self.error_queue = error_queue

    def run(self):
        logging_processor = LoggingProcessor('NetWorkProcess', prefix=pardir)
        import socket
        try:
            ws1 = create_connection("ws://127.0.0.1:8000/echo/")
        except socket.timeout:
            self.error_queue.put(custom_exception.NetWorkProcessError(custom_desc='ws1 is socket.timeout!'))
            return
        except TimeoutError:
            self.error_queue.put(custom_exception.NetWorkProcessError(custom_desc='ws1 is TimeoutError!'))
            return
        except ConnectionRefusedError:
            self.error_queue.put(custom_exception.NetWorkProcessError(custom_desc='ConnectionRefusedError! ws1无法连接上后台'))
            return
        except Exception as e:
            self.error_queue.put(custom_exception.NetWorkProcessError(custom_desc='ws 创建中发现了未知的错误: {}'.format(str(e))))
            return

        try:
            ws2 = create_connection("ws://127.0.0.1:8000/is_active/")
        except socket.timeout:
            self.error_queue.put(custom_exception.NetWorkProcessError(custom_desc='ws2 is socket.timeout!'))
            return
        except TimeoutError:
            self.error_queue.put(custom_exception.NetWorkProcessError(custom_desc='ws2 is TimeoutError!'))
            return
        except ConnectionRefusedError:
            self.error_queue.put(custom_exception.NetWorkProcessError(custom_desc='ConnectionRefusedError! ws2无法连接上后台'))
            return
        except Exception as e:
            self.error_queue.put(custom_exception.NetWorkProcessError(custom_desc=' ws2 创建中发现了未知的错误: {}'.format(str(e))))
            return

        try:
            q = queue.Queue()

            send_thread = threading.Thread(target=send_to_server, args=(ws1, self.data_process_queue, q, logging_processor))
            received_thread = threading.Thread(target=received_from_server,
                                               args=(ws1, self.command_process_queue, q, logging_processor))
            ask_alive_thread = threading.Thread(target=ask_alive, args=(ws2, q, logging_processor))
            get_token_thread = threading.Thread(target=get_token, args=(q, logging_processor))

            send_thread.setDaemon(True)  # 子线程会跟着退出
            received_thread.setDaemon(True)
            ask_alive_thread.setDaemon(True)
            get_token_thread.setDaemon(True)

            send_thread.start()  # 启动
            received_thread.start()
            # ask_alive_thread.start()
            get_token_thread.start()

            while True:
                if q.empty():
                    pass
                else:
                    print("要给break了")
                    raise q.get()  # 抛出子线程的异常
                    break
                if not send_thread.is_alive():
                    print("发送子线程结束")
                    return
                if not received_thread.is_alive():
                    print("接收子线程结束")
                    return
                # if not ask_alive_thread.is_alive():
                #     print("状态发送子线程结束")
                #     return
                if not get_token_thread.is_alive():
                    print("获取token子线程结束")
                    return

        except Exception as e:
            self.error_queue.put(
                custom_exception.NetWorkProcessError(custom_desc='network_connect中出现未知错误: {}'.format(str(e))))

        finally:
            ws1.close()
            ws2.close()
            token_processor.close()
            print("network_connect结束")


def send_to_server(ws, data_process_queue, q, logging_processor):
    """
    将处理好的数据发送给后台
    :param ws: websocket对象
    :param data_process_queue: 数据处理队列
    :param q: 进程内异常队列
    :param logging_processor: 进程内logging包装类对象
    :return:
    """
    try:
        while True:
            if ws.connected:  # websocket保持连接时
                processed_info = data_process_queue.get()  # json-like str
                ws.send(processed_info, opcode=websocket.ABNF.OPCODE_TEXT)  # 发送
                time.sleep(1)  # 一秒发送一次
    except ConnectionAbortedError as e:
        logging_processor.write_log("send_to_server: {}".format(str(e)))
        q.put(custom_exception.NetWorkProcessError(custom_desc='send_to_server中出现了connectAbortedError'))
    except ConnectionRefusedError as e:
        logging_processor.write_log("send_to_server: {}".format(str(e)))
        q.put(custom_exception.NetWorkProcessError(custom_desc='send_to_server中出现了connectRefusedError!后台未响应连接!'))
    except websocket._exceptions.WebSocketConnectionClosedException as e:
        logging_processor.write_log("send_to_server: {}".format(str(e)))
        q.put(custom_exception.NetWorkProcessError(custom_desc='send_to_server中出现了WebSocketConnectionClosedException'))
    except Exception as e:
        logging_processor.write_log("send_to_server: {}".format(str(e)))
        q.put(custom_exception.NetWorkProcessError(custom_desc='send_to_server中出现了未知的错误: {}'.format(str(e))))


def received_from_server(ws, command_process_queue, q, logging_processor):
    """
    将处理好的数据发送给后台
    :param ws: websocket对象
    :param command_process_queue: 指令处理队列
    :param q: 进程内异常队列
    :param logging_processor: 进程内logging包装类对象
    :return:
    """
    try:
        while True:
            if ws.connected:
                ret = ws.recv()
                command_process_queue.put(ret)  # 将从服务器收到的数据加载进queue中
    except ConnectionAbortedError as e:
        logging_processor.write_log("received_from_server: {}".format(str(e)))
        q.put(custom_exception.NetWorkProcessError(custom_desc='received_from_server中出现了connectAbortedError'))
    except ConnectionRefusedError as e:
        logging_processor.write_log("received_from_server: {}".format(str(e)))
        q.put(custom_exception.NetWorkProcessError(custom_desc='received_from_server中出现了connectRefusedError!后台未响应连接!'))
    except websocket._exceptions.WebSocketConnectionClosedException as e:
        logging_processor.write_log("received_from_server: {}".format(str(e)))
        q.put(custom_exception.NetWorkProcessError(
            custom_desc='received_from_server中出现了WebSocketConnectionClosedException'))
    except Exception as e:
        logging_processor.write_log("received_from_server: {}".format(str(e)))
        q.put(custom_exception.NetWorkProcessError(custom_desc='received_from_server中出现了未知的错误: {}'.format(str(e))))


def ask_alive(ws, q, logging_processor):
    """
    响应存在
    将处理好的数据发送给后台
    :param ws: websocket对象
    :param q: 进程内异常队列
    :param logging_processor: 进程内logging包装类对象
    :return:
    """
    verification = cookie_cache_processor.get_verification()  # 到时候改为用户cookies
    try:
        while True:
            if ws.connected:
                # 设置网关的状态
                terminal_cache_processor.add_terminal('Pi')
                terminal_cache_processor.set_terminal_status('Pi', 1)
                # 从缓存中读取终端信息
                for name in terminal_cache_processor.get_all_terminal_name():  # 读取所有终端名
                    if terminal_cache_processor.get_terminal_status(name):  # 判断终端是否存在
                        ws.send('{"alive":1, "name":"%s", "verf":"%s"}' % (name, verification),
                                opcode=websocket.ABNF.OPCODE_TEXT)  # 定时发送状态
                        logging_processor.write_log('ask_alive存在回应: {}'.format(ws.recv()))

                time.sleep(2)  # 延时一下,10s左右表示存在
    except ConnectionAbortedError as e:
        logging_processor.write_log("ask_alive: {}".format(str(e)))
        q.put(custom_exception.NetWorkProcessError(custom_desc='ask_alive中出现了connectAbortedError'))
    except ConnectionRefusedError as e:
        logging_processor.write_log("ask_alive: {}".format(str(e)))
        q.put(custom_exception.NetWorkProcessError(custom_desc='ask_alive中出现了connectRefusedError!后台未响应连接!'))
    except websocket._exceptions.WebSocketConnectionClosedException as  e:
        logging_processor.write_log("ask_alive: {}".format(str(e)))
        q.put(custom_exception.NetWorkProcessError(custom_desc='ask_alive中出现了WebSocketConnectionClosedException'))
    except Exception as e:
        logging_processor.write_log("ask_alive: {}".format(str(e)))
        q.put(custom_exception.NetWorkProcessError(custom_desc='ask_alive中出现了未知的错误: {}'.format(str(e))))


def get_token(q, logging_processor):
    """
    获取token值，并设置在缓存中
    :return:
    """
    try:
        while True:
            auth_processor.telephone = 17875512067
            auth_processor.password = 'abc666666'
            if cookie_cache_processor.get_verification() is None:
                auth_processor.get_token()
            time.sleep(1)
    except Exception as e:
        q.put(custom_exception.NetWorkProcessError(custom_desc='get_token中出现了未知的错误: {}'.format(str(e))))
        logging_processor.write_log("get_token出现异常: {}".format(str(e)))
    finally:
        auth_processor.close()


if __name__ == '__main__':
    pass
