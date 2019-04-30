import queue
from threading import Thread
import time

flag = True  # 是否还在通信
q = queue.Queue(maxsize=5)


def put_forever(index):
    for i in range(1000):
        t = time.time()
        print("{}存放了时间为 {}".format(index,t))
        q.put(t)
        # time.sleep(0.5)


def processing(count):
    while flag:
        if q.full():
            print("满了，扔出队列首: {}".format(q.get()))
            count += 1
            if count > 99995:
                print(count)


if __name__ == '__main__':
    count = 0
    t = Thread(target=processing, args=(count,))
    t.start()

    list1 = []
    for i in range(100):
        t = Thread(target=put_forever, args=(i,))
        t.start()
        list1.append(t)

    for i in list1:
        i.join()



