# coding:utf-8
# 使用信号量实现读者写者问题

from threading import Thread, Semaphore
from time import sleep
# 输出信息列表
output_list = []

WriteMutex = Semaphore(1)
Rcount = 0
CountMutex = Semaphore(1)

def writer_read_first(_name, des):
    name = str(_name)
    sleep(des[0])
    # start work
    output_list.append(("writer", name, "init"))

    global WriteMutex
    output_list.append(("writer", name, "acquire write mutex"))
    WriteMutex.acquire()
    output_list.append(("writer", name, "start writing"))
    sleep(des[1])
    output_list.append(("writer", name, "end writing"))
    WriteMutex.release()
    output_list.append(("writer", name, "release write mutext"))

def reader_read_first(_name, des):
    name = str(_name)
    sleep(des[0])
    # start work
    output_list.append(("reader", name, "init"))

    global CountMutex, Rcount, WriteMutex

    output_list.append(("reader", name, "acquire count mutex"))
    CountMutex.acquire()
    if (Rcount == 0):
        output_list.append(("reader", name, "acquire write mutex"))
        WriteMutex.acquire()
    Rcount += 1
    CountMutex.release()
    output_list.append(("reader", name, "release count mutex"))

    output_list.append(("reader", name, "start reading"))
    sleep(des[1])
    output_list.append(("reader", name, "end reading"))

    output_list.append(("reader", name, "acquire count mutex"))
    CountMutex.acquire()
    Rcount -= 1
    if (Rcount == 0):
        WriteMutex.release()
        output_list.append(("reader", name, "release write mutex"))
    CountMutex.release()
    output_list.append(("reader", name, "release count mutex"))

QueueMutex = Semaphore(1)
Wcount = 0
WCountMutex = Semaphore(1)

def writer_write_first(_name, des):
    name = str(_name)
    sleep(des[0])
    # start work
    output_list.append(("writer", name, "init"))

    global WriteMutex, QueueMutex, Wcount, WCountMutex

    output_list.append(("writer", name, "acquire count mutex"))
    WCountMutex.acquire()
    if Wcount == 0:
        output_list.append(("writer", name, "acquire queue mutex"))
        QueueMutex.acquire()
    Wcount += 1
    WCountMutex.release()
    output_list.append(("writer", name, "release count mutex"))

    output_list.append(("writer", name, "acquire write mutex"))
    WriteMutex.acquire()
    output_list.append(("writer", name, "start writing"))
    sleep(des[1])
    output_list.append(("writer", name, "end writing"))
    WriteMutex.release()
    output_list.append(("writer", name, "release write mutex"))

    output_list.append(("writer", name, "acquire count mutex"))
    WCountMutex.acquire()
    Wcount -= 1
    if Wcount == 0:
        output_list.append(("writer", name, "release queue mutex"))
        QueueMutex.release()
    WCountMutex.release()
    output_list.append(("writer", name, "release count mutex"))

def reader_write_first(_name, des):
    name = str(_name)
    sleep(des[0])
    # start work
    output_list.append(("reader", name, "init"))

    global CountMutex, Rcount, QueueMutex

    output_list.append(("reader", name, "acquire queue mutex"))
    QueueMutex.acquire()

    output_list.append(("reader", name, "acquire count mutex"))
    CountMutex.acquire()
    if (Rcount == 0):
        output_list.append(("reader", name, "acquire write mutex"))
        WriteMutex.acquire()
    Rcount += 1
    CountMutex.release()
    output_list.append(("reader", name, "release count mutex"))

    output_list.append(("reader", name, "release queue mutex"))
    QueueMutex.release()

    output_list.append(("reader", name, "start reading"))
    sleep(des[1])
    output_list.append(("reader", name, "end reading"))

    output_list.append(("reader", name, "acquire count mutex"))
    CountMutex.acquire()
    Rcount -= 1
    if (Rcount == 0):
        WriteMutex.release()
        output_list.append(("reader", name, "release write mutex"))
    CountMutex.release()
    output_list.append(("reader", name, "release count mutex"))


SPACESIZE = 20
def space(st):
    for i in range(SPACESIZE - len(st)):
        st += " "
    return st

# 正式模拟开始
input_buff = raw_input("read first ? Y/N\n")

if input_buff[0] == "Y" or input_buff[0] == "y":
    read_first = 1
else:
    read_first = 0

print "simulating"

# start time, last time
reader = [
    (0, 3),
    (1, 1),
    (2.5, 3)
]

writer = [
    (0.8, 1),
    (2, 2),
    (2.1, 3)
]

threads = []


for i in range(len(reader)):
    if read_first == 1:
        threads.append(Thread(target = reader_read_first, args = (i, reader[i])))
    else:
        threads.append(Thread(target = reader_write_first, args = (i, reader[i])))
    

for i in range(len(writer)):
    if read_first == 1:
        threads.append(Thread(target = writer_read_first, args = (i, writer[i])))
    else:
        threads.append(Thread(target = writer_write_first, args = (i, writer[i])))
    

for i in threads:
    i.setDaemon(True)   # 设置为主线程结束时，把子线程杀死
    i.start()

for i in threads:
    i.join()     # 等待全部线程结束

# 全部线程结束后，输出运行过程追踪信息

p = ""
for i in range(len(reader)):
    p = p + space("reader_" + str(i))
for i in range(len(writer)):
    p = p + space("writer_" + str(i))
print p

for i in output_list:
    p = ""
    if i[0] == "reader":
        j = int(i[1])
        prev = j * SPACESIZE
        for z in range(prev):
            p += " "
        p += space(i[2])
        print p
    else:
        j = int(i[1])
        prev = j * SPACESIZE + len(reader) * SPACESIZE
        for z in range(prev):
            p += " "
        p += space(i[2])
        print p




