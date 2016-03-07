#include <cstdio>
#include <string>
#include <iostream>
#include <vector>
using namespace std;
class PMMManager {
public:
    virtual void test() = 0;
    virtual void *pmm_malloc(int size) = 0;
    virtual void pmm_free(long long *ptr) = 0;
    string name;
    void print_name() {
        cout << "now PMMManager is " << name << endl;
    }
};

// 每个内存块头部的定义：本块的大小，指向前一块的指针，指向后一块的指针
// base是本块数据的开始，头部信息存在base之前
#define SETSIZE(base, value) *(((long long *)base) - 1) = ((long long)value)
#define SETPREV(base, value) *(((long long *)base) - 2) = ((long long)value)
#define SETNEXT(base, value) *(((long long *)base) - 3) = ((long long)value)

#define GETSIZE(base) *(((long long *)base) - 1)
#define GETPREV(base) (long long *)(*(((long long *)base) - 2))
#define GETNEXT(base) (long long *)(*(((long long *)base) - 3))


class PMMManagerFirst : public PMMManager{
public:
    // 使用双向链表维护每一个内存块的头部
    // memory_block_start是内存块中地址最低的一块的地址
    // base只是一个区域头部结构，起到连接双向链表的首尾，使之成为循环链表的作用
    long long *base, *memory_block_start;

    static const int reserved_size = 24;        // 每个内存区域的头部长度为24字节
    static const int align = 4;                 // 4字节对齐

    PMMManagerFirst(int init_memory_size) {
        init_memory_size = upper_round(init_memory_size + reserved_size, align);    // 可分配区域的总大小
        cout << "init memory " << init_memory_size << " Byte" << endl;
        // 初始化指针
        long long *block_memory_base = (long long *)malloc(init_memory_size);
        memory_block_start = block_memory_base;
        block_memory_base = block_memory_base + 3;

        base = (long long *)malloc(reserved_size);
        base = base + 3;
        // 连接成为双向循环链表
        // 每一块的size包块这一块的24字节头部
        SETSIZE(block_memory_base, init_memory_size);
        SETPREV(block_memory_base, base);
        SETNEXT(block_memory_base, base);

        SETSIZE(base, reserved_size);
        SETPREV(base, block_memory_base);
        SETNEXT(base, block_memory_base);
    }

    void test_main(int id, int n, int *query_size, int *opt_type) {
        cout << "start test"<< id << endl;
        vector<char *> query_ans;

        for (int i = 0; i < n; i ++) {
            cout << "-------------------------------operation " << i << "-------------------------------" << endl;
            if (opt_type[i] == -1) {
                char *ans = (char *)pmm_malloc(query_size[i]);
                cout << "try to allocate size = " << query_size[i] << endl;
                if (ans != 0) {
                    cout << "   allocate offset " << (long long)ans - (long long)memory_block_start << endl;
                } else  {
                    cout << "cannot allocate" << endl;
                }
                query_ans.push_back(ans);
            } else {
                cout << "try to free size = " << query_size[opt_type[i]] << endl;
                pmm_free((long long *)query_ans[opt_type[i]]);
            }
            print_memory_block();
        }
    }
    // 作为检查，双向各遍历一遍链表
    // 打印每一个空闲区域的起止地址，是包括头部的24字节的
    void print_memory_block() {
        cout << "print in order memory" << endl << "    ";
        long long *ptr = GETNEXT(base);
        // 链表打印的形式为每个空闲内存块的地址区间，左闭右开
        for (; ptr != base; ptr = GETNEXT(ptr)) {
            cout << "[" << (long long)ptr - (long long)memory_block_start - reserved_size << " , " << 
                (long long)ptr - (long long)memory_block_start - reserved_size + GETSIZE(ptr) << ")  ";
        }
        cout << endl;
        cout << "print reversed memory" << endl << "    ";
        ptr = GETPREV(base);
        for (; ptr != base; ptr = GETPREV(ptr)) {
            cout << "[" << (long long)ptr - (long long)memory_block_start - reserved_size << " , " << 
                (long long)ptr - (long long)memory_block_start - reserved_size + GETSIZE(ptr) << ")  ";
        }
        cout << endl;
    }

    void test() {
        cout << "start test" << endl;
        // 测试设计:
        // 首先分配三块，他们的大小都会被填充为4字节对齐
        // 释放中间一小块后，空间不足以分配出50字节
        // 再次释放一块后，能够自动合并，使得能够分配出更大的区域
        int n = 7;                                  // 测试中的操作数
        int query_size[] = {45, 37, 55, 0, 50, 0, 85};     // 分配的空间大小
        int opt_type[] = {-1, -1, -1, 1, -1, 0, -1};       // 操作类型：-1为分配，其余为释放的指针编号。先分配的指针编号为0，顺次递增。 
        test_main(1, n, query_size, opt_type);
    }

    int upper_round(int size, int mod) {
        if (size % mod == 0)
            return size;
        return size - size % mod + mod;
    }
    // 本函数在base后插入结点block
    void add_next(long long *base, long long *block) {
        SETNEXT(block, GETNEXT(base));
        SETPREV(block, base);
        SETPREV(GETNEXT(base), block);
        SETNEXT(base, block);
    }
    // 本函数删除base结点
    void del(long long *base) {
        SETNEXT(GETPREV(base), GETNEXT(base));
        SETPREV(GETNEXT(base), GETPREV(base));
    }

    void *pmm_malloc(int size) {
        long long *ptr = GETNEXT(base);
        int real_size = upper_round(size + reserved_size, align);
        cout << "real size " << real_size << endl;
        for (; ptr != base; ptr = GETNEXT(ptr)) {
            int block_size = GETSIZE(ptr);
            if (block_size >= real_size) {
                if (block_size >= real_size + reserved_size) {
                    // 则空间足够分成两个块
                    // 前半块是分配的空间，后半块是碎片，依然空闲
                    long long *smaller_block = ptr + real_size / sizeof(long long); // 后半块的开头
                    // 把分配出去的块从空闲表中拆除
                    SETSIZE(smaller_block, GETSIZE(ptr) - real_size);
                    SETNEXT(GETPREV(ptr), smaller_block);
                    SETPREV(GETNEXT(ptr), smaller_block);
                    SETPREV(smaller_block, GETPREV(ptr));
                    SETNEXT(smaller_block, GETNEXT(ptr));
                    SETSIZE(ptr, real_size);
                    return ptr;
                } else {
                    // 空间不够分成两块，直接拆除
                    del(ptr);
                    SETSIZE(ptr, real_size);
                    return ptr;
                }
                break;
            }
        }
        return 0;
    }
    // 向后合并
    void merge(long long *ptr__) {
        char *ptr = (char *)ptr__;

        while (GETNEXT(ptr) != base) {
            // 判断本块的下一块是不是空闲链表中的下一块，如果是，则可以直接合并
            char *next_start = ptr + GETSIZE(ptr);
            if (next_start == ((char *)GETNEXT(ptr))) {
                SETSIZE(ptr, GETSIZE(ptr) + GETSIZE(GETNEXT(ptr)));
                del(GETNEXT(ptr));
            } else
                break;
        }
    }

    void pmm_free(long long *ptr) {
        long long *temp = GETNEXT(base), *smaller = 0;
        // 寻找比被释放的ptr小的最大的指针smaller
        for (; temp != base; temp = GETNEXT(temp)) {
            if (temp < ptr) {
                smaller = temp;
            } else 
                break;
        }
        if (smaller != 0) {
            // 释放的指针前面还有一块，则插入链表
            add_next(smaller, ptr);
            // merge是向后合并。所以要找到前一块，并尝试merge前一块：如果相邻则合并成功
            merge(smaller);
            merge(ptr);
        } else {
            // 释放的指针作为头指针
            add_next(base, ptr);
            merge(ptr);
        }
    }
};

int main() {
    PMMManagerFirst *a = new PMMManagerFirst(230);
    a->test();
}