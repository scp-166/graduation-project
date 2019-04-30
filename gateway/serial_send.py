import serial
import time
import binascii
import threading

s = serial.Serial('com5', 9600)

channel = '000604' 


def send_data1():
    for i in range(10):
        received_data = bytes.fromhex('02011a0101ffff9c0a')  # fromhex 需要字符串
        print(received_data)
        s.write(received_data)  # write要求bytes
        time.sleep(1)


def send_data2():
    for i in range(10):
        received_data = bytes.fromhex('0301470101ffff9c0a')  # fromhex 需要字符串
        print(received_data)
        s.write(received_data)  # write要求bytes
        time.sleep(1)


def received_data():
    while True:
        ret = s.inWaiting()
        if ret:
            data = s.read(ret)
            print(data)


if __name__ == '__main__':
    try:

        t1 = threading.Thread(target=received_data, args=())
        t1.setDaemon(True)
        t1.start()

        t = threading.Thread(target=send_data1, args=())
        t.setDaemon(True)
        t.start()

        t = threading.Thread(target=send_data2, args=())
        t.setDaemon(True)
        t.start()

        while True:
            time.sleep(2)

    except KeyboardInterrupt:
        print("收到了")
        exit(0)
