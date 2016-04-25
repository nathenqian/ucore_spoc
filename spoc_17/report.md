#在简化X86虚拟机上实现同步互斥 实验报告

钱迪晨2013011402 高思达 2013011413

文件说明：

* `looping-race-nolock.s`：为原本的同名文件加上了同步互斥机制，是本实验的主体。
* `old-loop-nolock.s`：原本无互斥机制的程序的拷贝，作为对照实验。
* `command`：实验脚本，可以直接运行得到下面介绍的输出结果。
* `X86.py`：X86虚拟机。

###1 实现要点

* 基于已有的无锁的循环代码`looping-race-nolock.s`，我们为它加上同步互斥机制。

* 首先，实现进入临界区的代码，即获得锁的部分`.acquire`。实现的关键是使用X86硬件提供的原子操作指令。在我们的实现中，使用的是“交换”指令。与1进行交换，是和MOOC中所讲的Test and Set操作等价的操作。具体实现代码如下：

```
# 进入临界区，获得锁
.acquire
mov  $1, %ax        
xchg %ax, mutex     # atomic swap of 1 and mutex
test $0, %ax        # if we get 0 back: lock is free!
jne  .acquire       # if not, try again
```

其中，`mutex`是共享的互斥锁变量。把1和它交换，检查换出的值。如果换出的是1，表明锁被占用，继续循环等待（这次交换也没有改变`mutex`的值）。如果换出的是0，表明之前锁没有被占用，且现在锁被改成了1，即当前进程获得了锁，也就可以进入临界区代码了。

注意，由于循环体是临界区代码，临界区的进入代码`.acquire`必须放在循环体内部（即`.top`的下面）。

* 临界区代码就是原本的循环体，取出内存中的树并对它加1，然后再保存回内存。

* 临界区的退出代码即把`mutex`改成0，释放互斥锁。注意，临界区退出的代码应该紧邻临界区（即紧邻对共享资源的操作），即在判断循环条件的代码之前。

###2 实验结果输出

运行command脚本（`bash command`）可以看到以下三组结果。

* 对于原始的无锁程序`old-loop-nolock.s`，如果使用两个线程运行，即命令行命令为：

```
python x86.py -p old-loop-nolock.s -a bx=2 -t 2 -M 2000 -i 2 -c
```

运行的结果为：

```
 2000          Thread 0                Thread 1         

    0   
    0   1000 mov 2000, %ax
    0   1001 add $1, %ax
    0   ------ Interrupt ------  ------ Interrupt ------  
    0                            1000 mov 2000, %ax
    0                            1001 add $1, %ax
    0   ------ Interrupt ------  ------ Interrupt ------  
    1   1002 mov %ax, 2000
    1   1003 sub  $1, %bx
    1   ------ Interrupt ------  ------ Interrupt ------  
    1                            1002 mov %ax, 2000
    1                            1003 sub  $1, %bx
    1   ------ Interrupt ------  ------ Interrupt ------  
    1   1004 test $0, %bx
    1   1005 jgt .top
    1   ------ Interrupt ------  ------ Interrupt ------  
    1                            1004 test $0, %bx
    1                            1005 jgt .top
    1   ------ Interrupt ------  ------ Interrupt ------  
    1   1000 mov 2000, %ax
    1   1001 add $1, %ax
    1   ------ Interrupt ------  ------ Interrupt ------  
    1                            1000 mov 2000, %ax
    1                            1001 add $1, %ax
    1   ------ Interrupt ------  ------ Interrupt ------  
    2   1002 mov %ax, 2000
    2   1003 sub  $1, %bx
    2   ------ Interrupt ------  ------ Interrupt ------  
    2                            1002 mov %ax, 2000
    2                            1003 sub  $1, %bx
    2   ------ Interrupt ------  ------ Interrupt ------  
    2   1004 test $0, %bx
    2   1005 jgt .top
    2   ------ Interrupt ------  ------ Interrupt ------  
    2                            1004 test $0, %bx
    2                            1005 jgt .top
    2   ------ Interrupt ------  ------ Interrupt ------  
    2   1006 halt
    2   ----- Halt;Switch -----  ----- Halt;Switch -----  
    2                            1006 halt
```

可以看到，线程0取出数据加完，在保存之前就切换到了线程1，线程1又取出老数据，做了同样的加法。这样，再写回内存时，两个进程写的数据一样，相当于白加一次。于是，虽然加了4次，当内存里的数据只是2。这是打断了不应打断的原子操作的后果。

* 对于我们修改后的`looping-race-nolock.s`程序，在相同的命令行选项下运行，就能得到正确的结果。命令如下：

```
python x86.py -p looping-race-nolock.s -a bx=2 -t 2 -M 2000 -i 2 -c
```

输出如下：

```
2000          Thread 0                Thread 1         

    0   
    0   1000 mov  $1, %ax
    0   1001 xchg %ax, mutex
    0   ------ Interrupt ------  ------ Interrupt ------  
    0                            1000 mov  $1, %ax
    0                            1001 xchg %ax, mutex
    0   ------ Interrupt ------  ------ Interrupt ------  
    0   1002 test $0, %ax
    0   1003 jne  .acquire
    0   ------ Interrupt ------  ------ Interrupt ------  
    0                            1002 test $0, %ax
    0                            1003 jne  .acquire
    0   ------ Interrupt ------  ------ Interrupt ------  
    0   1004 mov 2000, %ax
    0   1005 add $1, %ax
    0   ------ Interrupt ------  ------ Interrupt ------  
    0                            1000 mov  $1, %ax
    0                            1001 xchg %ax, mutex
    0   ------ Interrupt ------  ------ Interrupt ------  
    1   1006 mov %ax, 2000
    1   1007 mov $0, mutex
    1   ------ Interrupt ------  ------ Interrupt ------  
    1                            1002 test $0, %ax
    1                            1003 jne  .acquire
    1   ------ Interrupt ------  ------ Interrupt ------  
    1   1008 sub  $1, %bx
    1   1009 test $0, %bx
    1   ------ Interrupt ------  ------ Interrupt ------  
    1                            1000 mov  $1, %ax
    1                            1001 xchg %ax, mutex
    1   ------ Interrupt ------  ------ Interrupt ------  
    1   1010 jgt .top
    1   1000 mov  $1, %ax
    1   ------ Interrupt ------  ------ Interrupt ------  
    1                            1002 test $0, %ax
    1                            1003 jne  .acquire
    1   ------ Interrupt ------  ------ Interrupt ------  
    1   1001 xchg %ax, mutex
    1   1002 test $0, %ax
    1   ------ Interrupt ------  ------ Interrupt ------  
    1                            1004 mov 2000, %ax
    1                            1005 add $1, %ax
    1   ------ Interrupt ------  ------ Interrupt ------  
    1   1003 jne  .acquire
    1   1000 mov  $1, %ax
    1   ------ Interrupt ------  ------ Interrupt ------  
    2                            1006 mov %ax, 2000
    2                            1007 mov $0, mutex
    2   ------ Interrupt ------  ------ Interrupt ------  
    2   1001 xchg %ax, mutex
    2   1002 test $0, %ax
    2   ------ Interrupt ------  ------ Interrupt ------  
    2                            1008 sub  $1, %bx
    2                            1009 test $0, %bx
    2   ------ Interrupt ------  ------ Interrupt ------  
    2   1003 jne  .acquire
    2   1004 mov 2000, %ax
    2   ------ Interrupt ------  ------ Interrupt ------  
    2                            1010 jgt .top
    2                            1000 mov  $1, %ax
    2   ------ Interrupt ------  ------ Interrupt ------  
    2   1005 add $1, %ax
    3   1006 mov %ax, 2000
    3   ------ Interrupt ------  ------ Interrupt ------  
    3                            1001 xchg %ax, mutex
    3                            1002 test $0, %ax
    3   ------ Interrupt ------  ------ Interrupt ------  
    3   1007 mov $0, mutex
    3   1008 sub  $1, %bx
    3   ------ Interrupt ------  ------ Interrupt ------  
    3                            1003 jne  .acquire
    3                            1000 mov  $1, %ax
    3   ------ Interrupt ------  ------ Interrupt ------  
    3   1009 test $0, %bx
    3   1010 jgt .top
    3   ------ Interrupt ------  ------ Interrupt ------  
    3                            1001 xchg %ax, mutex
    3                            1002 test $0, %ax
    3   ------ Interrupt ------  ------ Interrupt ------  
    3   1011 halt
    3   ----- Halt;Switch -----  ----- Halt;Switch -----  
    3                            1003 jne  .acquire
    3   ------ Interrupt ------  ------ Interrupt ------  
    3                            1004 mov 2000, %ax
    3                            1005 add $1, %ax
    3   ------ Interrupt ------  ------ Interrupt ------  
    4                            1006 mov %ax, 2000
    4                            1007 mov $0, mutex
    4   ------ Interrupt ------  ------ Interrupt ------  
    4                            1008 sub  $1, %bx
    4                            1009 test $0, %bx
    4   ------ Interrupt ------  ------ Interrupt ------  
    4                            1010 jgt .top
    4                            1011 halt
```

可见，由于使用了同步互斥机制，可以在两个线程共4次循环之后正确地把内存加到4。观察具体的执行过程发现，由于每2条指令打断一次，线程1发生了微弱的饥饿现象，检查到第三次之后才首次得到锁。

* 为了避免饥饿现象，我们重新进行了一次实验，这次的中断设为每4条指令进行一次，即运行如下指令：

```
python x86.py -p looping-race-nolock.s -a bx=2 -t 2 -M 2000 -i 4 -c
```

可见，线程1的饥饿现象得到了缓解，检查到第二次就得到了锁。程序的整体运行时间也得到了缩短，说明时间片的长度在同步互斥机制下能够影响调度效率（通过打断位置的变化，影响等待互斥锁的时间）。

```
2000          Thread 0                Thread 1         

    0   
    0   1000 mov  $1, %ax
    0   1001 xchg %ax, mutex
    0   1002 test $0, %ax
    0   1003 jne  .acquire
    0   ------ Interrupt ------  ------ Interrupt ------  
    0                            1000 mov  $1, %ax
    0                            1001 xchg %ax, mutex
    0                            1002 test $0, %ax
    0                            1003 jne  .acquire
    0   ------ Interrupt ------  ------ Interrupt ------  
    0   1004 mov 2000, %ax
    0   1005 add $1, %ax
    1   1006 mov %ax, 2000
    1   1007 mov $0, mutex
    1   ------ Interrupt ------  ------ Interrupt ------  
    1                            1000 mov  $1, %ax
    1                            1001 xchg %ax, mutex
    1                            1002 test $0, %ax
    1                            1003 jne  .acquire
    1   ------ Interrupt ------  ------ Interrupt ------  
    1   1008 sub  $1, %bx
    1   1009 test $0, %bx
    1   1010 jgt .top
    1   1000 mov  $1, %ax
    1   ------ Interrupt ------  ------ Interrupt ------  
    1                            1004 mov 2000, %ax
    1                            1005 add $1, %ax
    2                            1006 mov %ax, 2000
    2                            1007 mov $0, mutex
    2   ------ Interrupt ------  ------ Interrupt ------  
    2   1001 xchg %ax, mutex
    2   1002 test $0, %ax
    2   1003 jne  .acquire
    2   1004 mov 2000, %ax
    2   ------ Interrupt ------  ------ Interrupt ------  
    2                            1008 sub  $1, %bx
    2                            1009 test $0, %bx
    2                            1010 jgt .top
    2                            1000 mov  $1, %ax
    2   ------ Interrupt ------  ------ Interrupt ------  
    2   1005 add $1, %ax
    3   1006 mov %ax, 2000
    3   1007 mov $0, mutex
    3   1008 sub  $1, %bx
    3   ------ Interrupt ------  ------ Interrupt ------  
    3                            1001 xchg %ax, mutex
    3                            1002 test $0, %ax
    3                            1003 jne  .acquire
    3                            1004 mov 2000, %ax
    3   ------ Interrupt ------  ------ Interrupt ------  
    3   1009 test $0, %bx
    3   1010 jgt .top
    3   1011 halt
    3   ----- Halt;Switch -----  ----- Halt;Switch -----  
    3                            1005 add $1, %ax
    3   ------ Interrupt ------  ------ Interrupt ------  
    4                            1006 mov %ax, 2000
    4                            1007 mov $0, mutex
    4                            1008 sub  $1, %bx
    4                            1009 test $0, %bx
    4   ------ Interrupt ------  ------ Interrupt ------  
    4                            1010 jgt .top
    4                            1011 halt
```

