# coding:utf-8
import os
import random
import numpy as np
import itertools

class Bankers(object):
    def __init__(self, totalResource):
        #initiating
        self.RESOURCE = totalResource

    def SignProcesses(self, max_, allocated_):
        self.max = max_
        self.allocated = allocated_
        self.need = self.CalcNeed()
        self.avaliable = self.CalcAvaliable()
        self.finished = [False] * len(self.allocated)

    def Difference(self, a, b):
        #return matrix subtracted from a by b
        res = []
        for i in range(len(a)):
            tmp = []
            for j in range(len(a[i])):
                tmp.append(a[i][j] - b[i][j])
            res.append(tmp)
        return res

    def CalcNeed(self):
        #calc request by subtracting signed matrix from max matrix
        return self.Difference(self.max, self.allocated)

    def CalcAvaliable(self):
        """Calc Avaliable Resource"""
        a = self.allocated
        res = []
        for j in range(len(a[0])):
            tmp = 0
            for i in range(len(a)):
                tmp += a[i][j]
            res.append(self.RESOURCE[j] - tmp)
        return res

    def ExecuteProcess(self, index):

        #check if less avaliable than Request
        # 2013011413 高思达, 2013011402 钱迪晨
        for i in range(len(self.allocated[0])):
            if (self.need[index][i] > self.avaliable[i]):
                return False
        #check END here

        #allocating what they need. 只进行资源分配，即做好了执行的准备。但没有执行。
        # 2013011413 高思达, 2013011402 钱迪晨
        for i in range(len(self.allocated[0])):
            self.allocated[index][i] += self.need[index][i]
            self.need[index][i] = 0
        self.avaliable = self.CalcAvaliable()
        # self.need = self.CalcNeed()
        # 给出的CalcNeed实现十分简单，只能在初始化的时候用一次。后面分配完都得手动改成0.
        return True
        #allocating END here

    def TempSafeCheckAfterRelease(self):
        #check if at least one request can be done after previous process done. not check whole sequances.
        #if every element of Requests can't accepted after previous process done, this mean it is not safe state
        # 2013011413 高思达, 2013011402 钱迪晨
        for i in range(len(self.allocated)):
            valid_cnt = 0
            for j in range(len(self.allocated[0])):
                if self.need[i][j] <= self.avaliable[j]:
                    valid_cnt += 1
            if valid_cnt == len(self.allocated[0]):
                return True
        return False
        #check END here

    def print_matrixes(self):
        print "_____________________________________________"
        print "MAX\t\tAllocated\tNeed"
        for idx in range(len(self.max)):
            print "%s\t%s\t%s" % (self.max[idx],self.allocated[idx], self.need[idx])
        print "_____________________________________________"
        print "Resources:"
        print "Total: %s\tAvailable: %s\n" % (self.RESOURCE, self.avaliable)

    def ReleasingProcess(self, index):
        for i in range(0, len(self.RESOURCE)):
            self.finished[index] = True
            self.allocated[index][i] = 0
        self.avaliable = self.CalcAvaliable()

    def Execute(self):
        i = 0
        # get all permutation of processes
        # 得到了所有可能的排列 0, 1 2, ..., procnum - 1
        perm = itertools.permutations(range(procnum), procnum)
        permArray = np.asarray(list(perm))

        for arr in permArray:
            for i in arr:
                if self.finished[i] == False:
                    print "Executing..."
                    print "Request: "
                    print self.need[i]
                    # check if less avaliable than Request
                    if self.ExecuteProcess(i):
                        print "Dispatching Done..."

                        self.print_matrixes()

                        print "-----Releasing Process------"

                        self.ReleasingProcess(i)

                        self.print_matrixes()

                        #check if at least one request can be done after previous process done. not check whole sequances.
                        #if every element of Requests can't accepted after previous process done, this mean it is not safe state
                        # 任意时刻发现无法继续了，都能认为任意一种序列都不行。
                        # 即，只要资源足够都可以立即执行，之后释放的资源可以让需求更大的人执行（这样做并不会对后面的进程有害）。
                        if not (self.TempSafeCheckAfterRelease()):
                            print "SAFE STATE: NOT SAFE - There are no sequances can avoid Deadlock"
                            return False
                        processes.append(i)
                    else:
                        print "HOLD: not enough Resource"

                if i == len(self.allocated) - 1:
                    i = 0
                else:
                    i += 1

                check = True
                for k in range(0, len(self.allocated)):
                    if self.finished[k] == False:
                        check = False
                        break
                if check == True:
                    return True
                    break
        #every permutation of processes is false
        return False

def getmax():
    res = []
    for j in range(procnum):
        tmp = []
        for i in range(len(total_resources)):
            randnum = random.random()
            remain_max = 0
            if j > 0:
                remain_max = total_resources[i]
                for k in range(j):
                    remain_max = remain_max - res[k][i]
                if remain_max < 0:
                    remain_max = 0
            else:
                remain_max = total_resources[i]
            tmp.append((int)(randnum * remain_max * 0.8))
        res.append(tmp)
    return res

def getallocated():
    res = []
    for j in range(procnum):
        tmp = []
        for i in range(len(total_resources)):
            randnum = random.random()
            remain = 0
            if j > 0:
                remain = max[j][i]
                for k in range(j):
                    remain = remain - res[k][i]
                if remain < 0:
                    remain = 0
            else:
                remain = max[j][i]
            tmp.append((int)(randnum * remain))
        res.append(tmp)
    return res

print "start here"
'''
# random seed
seed = 2
random.seed(seed)
# the number of process list
procnum = 3
# the number of type of resource
resnum =  4
# the max total value of resource
restotalval = 30
# the total resources list
total_resources = []
# the total processes
processes = []
# set the real total value of resource in total_resources
for i in range(resnum):
    total_resources.append((int)(restotalval * random.random()))
# init the Banker
b = Bankers(total_resources)
# get the max request values of resources from process （随机生成一个合理的请求矩阵）
max = getmax()
# get the already gotted values of resources from process （随机生成一个已分配的矩阵）
allocated = getallocated()
# init need matrix, available vector  注册为算法相应数据结构的初始值
b.SignProcesses(max, allocated)
# print all theses matrixes
b.print_matrixes()
# executing Banker algorithm
result = b.Execute()
# show results
if result:
    print "SUCCESS proc lists ", processes
else:
    print "Failed"
'''

procnum = 3
total_resources = [28, 28, 1, 2]
processes = []
b = Bankers(total_resources)

max = [
    [18, 16, 0, 0],
    [4, 5, 0, 0],
    [2, 2, 0, 1],
]
allocated = [
    [17, 8, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
]
b.SignProcesses(max, allocated)
b.print_matrixes()
result=b.Execute()
if result:
    print "SUCCESS proc lists ",processes
else:
    print "Failed"

'''
total_resources = [6, 5, 7, 6]
processes = []
b = Bankers(total_resources)

max = [
    [3, 3, 2, 2],
    [1, 2, 3, 4],
    [1, 3, 5, 0],
]
allocated = [
    [1, 2, 2, 1],
    [1, 0, 3, 3],
    [1, 2, 1, 0],
]
b.SignProcesses(max, allocated)
b.print_matrixes()
result=b.Execute()
if result:
    print "SUCCESS proc lists ",processes
else:
    print "Failed"
'''
#
#
# total_resources = [10, 10, 8, 5]
# processes=[]
# b = Bankers(total_resources)
# max = [
#         [10, 8, 2,5],
#         [6, 1, 3,1],
#         [3, 1, 4,2],
#         [5, 4, 2,1]
#     ]
# allocated = [
#         [3, 0, 0,3],
#         [1, 1, 2,0],
#         [2, 1, 2,1],
#         [0, 0, 2,0]
#     ]
# b.SignProcesses(max, allocated)
# b.print_matrixes()
# result=b.Execute()
# if result:
#     print "SUCCESS proc lists ",processes
# else:
#     print "Failed"
