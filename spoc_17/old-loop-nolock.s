# 原始的无锁代码作为对照
# assumes %bx has loop count in it

.main
.top    
# critical section
mov 2000, %ax  # get the value at the address
add $1, %ax    # increment it
mov %ax, 2000  # store it back

# see if we're still looping
sub  $1, %bx
test $0, %bx
jgt .top    

halt