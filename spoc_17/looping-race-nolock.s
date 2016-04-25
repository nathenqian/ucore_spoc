# assumes %bx has loop count in it
.var mutex
.main
.top

#获得锁
.acquire
mov  $1, %ax        
xchg %ax, mutex     # atomic swap of 1 and mutex
test $0, %ax        # if we get 0 back: lock is free!
jne  .acquire       # if not, try again

# critical section 临界区代码
mov 2000, %ax  # get the value at the address
add $1, %ax    # increment it
mov %ax, 2000  # store it back
# leave
mov $0, mutex
# see if we're still looping
sub  $1, %bx
test $0, %bx
jgt .top    
#这里将ax放在cx，输出cx结果，答案中jgt .showresult的次数就是ax的值
mov %ax, %cx
.showresult
sub $1, %cx
test $0, %cx
jgt .showresult

halt
