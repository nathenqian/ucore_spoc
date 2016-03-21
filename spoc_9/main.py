from optparse import OptionParser

parser = OptionParser()
parser.add_option('-t', '--delta_time', default='3', help='delta time',  action='store', type='int', dest='delta_t')

(options, args) = parser.parse_args()
delta_t = options.delta_t

test_list = [0, 1, 2, 1, 0, 2, 3, 1, 3]
# delta_t = 3
memory_page = {}
total_miss = 0

# 设计思路：
# 我们每访问一页（即该页进入窗口），就对它的“访问次数”加1
# 窗口移动出去时，把它的“访问次数”减1，则小于等于0的是无效的页

def remove_page(memory, index):
    memory[index] -= 1

def has_page(memory, index):
    if index in memory and memory[index] > 0:
        return True
    return False

def add_page(memory, index):
    if index not in memory:
        memory[index] = 0
    memory[index] += 1

for t in range(0, len(test_list)):
    # 找到刚刚失效的位置
    last_index = t - delta_t
    # 如果该位置存在，删掉它
    if last_index >= 0:
        remove_page(memory_page, test_list[last_index])
    if has_page(memory_page, test_list[t]):
        print "hit page %s" % (str(test_list[t]))
    else:
        total_miss += 1
        print "can't hit page %s total miss = %s" % (str(test_list[t]), str(total_miss))
    add_page(memory_page, test_list[t])
