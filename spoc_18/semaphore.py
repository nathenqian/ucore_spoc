# coding:utf-8
# 使用信号量实现读者写者问题

import threading

global WriteMutex = threading.Semaphore(1)
global Rcount = 0
global CountMutex = threading.Semaphore(1)

class Writer(threading.Thread):

    def __init__(self, threadName):
        threading.Thread.__init__(self, name=threadName)

    def run(self):
        WriteMutex.acquire()
        print "write"
        WriteMutex.release()

class Reader(threading.Thread):

    def __init__(self, threadName):
        threading.Thread.__init__(self, name=threadName)

    def run(self):
        CountMutex.acquire()
        if (Rcount == 0):
            WriteMutex.acquire()
        Rcount += 1
        CountMutex.release()

        print "read"

        CountMutex.acquire()
        Rcount -= 1
        if (Rcount == 0):
            WriteMutex.release()
        CountMutex.release()

if (__name__ == '__main__'):




