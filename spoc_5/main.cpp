#include <cstdio>
#include <string>
#include <iostream>
using namespace std;
class PMMManager {
public:
    virtual void test();
    virtual void *pmm_malloc(int size);
    virtual void pmm_free(void *ptr);
    string name;
    void print_name() {
        cout << "now PMMManager is " << name << endl;
    }
};

#define SETSIZE(base, value) *(((long long *)base) - 1) = ((long long)value)
#define SETPREV(base, value) *(((long long *)base) - 2) = ((long long)value)
#define SETNEXT(base, value) *(((long long *)base) - 3) = ((long long)value)

#define GETSIZE(base) *(((long long *)base) - 1)
#define GETPREV(base) (long long *)(*(((long long *)base) - 2))
#define GETNEXT(base) (long long *)(*(((long long *)base) - 3))


class PMMManagerFirst : public PMMManager{
public:
    long long *base;
    // size of byte
    const int reserved_size = 24;
    PMMManagerFirst(int init_memory_size) {
        long long *block_memory_base = (long long *)malloc(init_memory_size);
        block_memory_base = block_memory_base + 3;

        base = (long long *)malloc(24);

        SETSIZE(block_memory_base, init_memory_size - 4);
        SETPREV(block_memory_base, base);
        SETNEXT(block_memory_base, base);

        SETPREV(base, block_memory_base);
        SETNEXT(base, block_memory_base);
    }

    void test() {

    }

    const int align = 4;
    int upper_round(int size, int mod) {
        if (size % mod == 0)
            return size;
        return size - size % mod + mod;
    }

    void add_next(long long *base, long long *block) {
        SETNEXT(block, GETNEXT(base));
        SETPREV(block, base);
        SETNEXT(base, block);
        SETPREV(GETNEXT(base), block);
    }

    void del(long long *base) {
        SETNEXT(GETPREV(base), GETNEXT(base));
        SETPREV(GETNEXT(base), GETPREV(base));
    }

    void *pmm_malloc(int size) {
        long long *ptr = GETNEXT(base);
        int real_size = upper_round(size + reserved_size, align);
        for (; ptr != base; ptr = GETNEXT(ptr)) {
            int block_size = GETSIZE(ptr);
            if (block_size >= real_size) {
                if (block_size >= real_size + reserved_size) {
                    // can split into two memory blocks.
                    // one reserved for query, one is smaller.
                    long long *smaller_block = ptr + real_size / 8;
                    SETNEXT(GETPREV(ptr), smaller_block);
                    SETPREV(GETNEXT(ptr), smaller_block);
                    SETPREV(smaller_block, GETPREV(ptr));
                    SETNEXT(smaller_block, GETNEXT(ptr));
                    return ptr;
                } else {
                    del(ptr);
                    return ptr;
                }
                break;
            }
        }
        return 0;
    }

    void merge(long long *ptr__) {
        char *ptr = (char *)ptr__;

        while (GETNEXT(ptr) != base) {
            char *end = ptr - reserved_size + GETSIZE(ptr);
            if (end == ((char *)GETNEXT(ptr))) {
                SETSIZE(ptr, GETSIZE(ptr) + GETSIZE(GETNEXT(ptr)));
                del(GETNEXT(ptr));
            } else
                break;
        }
    }

    void pmm_free(long long *ptr) {
        long long *temp = GETNEXT(base), *smaller = 0;
        for (; temp != base; temp = GETNEXT(base)) {
            if (temp < ptr) {
                smaller = temp;
            } else 
                break;
        }
        if (smaller != 0) {
            // can find one smaller
            add_next(smaller, ptr);
            merge(smaller);
            merge(ptr);
        } else {
            // ptr is smaller
            add_next(base, ptr);
            merge(ptr);
        }
    }
};

int main() {

}