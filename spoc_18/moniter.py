from threading import Thread, Condition, Lock
# output_list_lock = Lock()
from time import sleep
output_list = []

SPACESIZE = 20

class Information:
    def __init__(self):
        self.iswriting = 0
        self.isreading = 0
        self.waitreading = 0
        self.waitwriting = 0

infor = Information()
lock = Lock()
toread = Condition(lock)
towrite = Condition(lock)

def space(st):
    for i in range(SPACESIZE - len(st)):
        st += " "
    return st

def writer_read_first(_name, des):
    name = str(_name)
    sleep(des[0])
    # start work
    output_list.append(("writer", name, "init"))
    # sleep(0.1)
    global lock, infor, toread, towrite
    lock.acquire()
    output_list.append(("writer", name, "lock"))
    while infor.isreading + infor.iswriting > 0:
        output_list.append(("writer", name, "wait"))
        infor.waitwriting += 1
        towrite.wait()
        infor.waitwriting -= 1

    infor.iswriting += 1
    output_list.append(("writer", name, "start writing"))
    lock.release()
    sleep(des[1])
    output_list.append(("writer", name, "end writing"))

    lock.acquire()
    infor.iswriting -= 1;

    if infor.waitreading > 0:
        toread.notify_all()
    elif infor.waitwriting > 0:
        towrite.notify()
    lock.release()


def reader_read_first(_name, des):
    name = str(_name)
    sleep(des[0])
    # start work
    output_list.append(("reader", name, "init"))

    global lock, infor, toread, towrite
    lock.acquire()
    output_list.append(("reader", name, "lock"))
    while infor.iswriting > 0:
        output_list.append(("reader", name, "wait"))
        infor.waitreading += 1
        toread.wait()
        infor.waitreading -= 1

    infor.isreading += 1
    output_list.append(("reader", name, "start reading"))
    lock.release()
    sleep(des[1])
    output_list.append(("reader", name, "end reading"))

    lock.acquire()
    infor.isreading -= 1;

    if infor.waitwriting > 0 and infor.isreading == 0:
        towrite.notify()
    lock.release()

def writer_write_first(_name, des):
    name = str(_name)
    sleep(des[0])
    # start work
    output_list.append(("writer", name, "init"))
    # sleep(0.1)
    global lock, infor, toread, towrite
    lock.acquire()
    output_list.append(("writer", name, "lock"))
    while infor.isreading + infor.iswriting > 0:
        output_list.append(("writer", name, "wait"))
        infor.waitwriting += 1
        towrite.wait()
        infor.waitwriting -= 1

    infor.iswriting += 1
    output_list.append(("writer", name, "start writing"))
    lock.release()
    sleep(des[1])
    output_list.append(("writer", name, "end writing"))

    lock.acquire()
    infor.iswriting -= 1;


    if infor.waitwriting > 0:
        towrite.notify()
    elif infor.waitreading > 0:
        toread.notify_all()
    lock.release()


def reader_write_first(_name, des):
    name = str(_name)
    sleep(des[0])
    # start work
    output_list.append(("reader", name, "init"))
    # sleep(0.1)

    global lock, infor, toread, towrite
    lock.acquire()
    output_list.append(("reader", name, "lock"))
    while infor.iswriting > 0 or infor.waitwriting > 0:
        output_list.append(("reader", name, "wait"))
        infor.waitreading += 1
        toread.wait()
        infor.waitreading -= 1

    infor.isreading += 1
    output_list.append(("reader", name, "start reading"))
    lock.release()
    sleep(des[1])
    output_list.append(("reader", name, "end reading"))

    lock.acquire()
    infor.isreading -= 1;

    if infor.waitwriting > 0 and infor.isreading == 0:
        towrite.notify()
    lock.release()

input_buff = raw_input("read first ? Y/N\n")

if input_buff[0] == "Y" or input_buff[0] == "y":
    read_first = 1
else:
    read_first = 0

print "simulating"

reader = [
#start time last time
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
    i.setDaemon(True)
    i.start()

for i in threads:
    i.join()

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