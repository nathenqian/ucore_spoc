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

#define SETSIZE(base, value) *(((long long *)base) - 1) = ((long long)value)
#define SETPREV(base, value) *(((long long *)base) - 2) = ((long long)value)
#define SETNEXT(base, value) *(((long long *)base) - 3) = ((long long)value)

#define GETSIZE(base) *(((long long *)base) - 1)
#define GETPREV(base) (long long *)(*(((long long *)base) - 2))
#define GETNEXT(base) (long long *)(*(((long long *)base) - 3))


class PMMManagerFirst : public PMMManager{
public:
    long long *base, *memory_block_start;
    // size of byte
    const int reserved_size = 24;
    PMMManagerFirst(int init_memory_size) {
        init_memory_size = upper_round(init_memory_size, 4);
        cout << "init memory " << init_memory_size << " Byte" << endl;
        long long *block_memory_base = (long long *)malloc(init_memory_size);
        memory_block_start = block_memory_base;
        block_memory_base = block_memory_base + 3;

        base = (long long *)malloc(24);
        base = base + 3;
        SETSIZE(block_memory_base, init_memory_size - 4);
        SETPREV(block_memory_base, base);
        SETNEXT(block_memory_base, base);

        SETPREV(base, block_memory_base);
        SETNEXT(base, block_memory_base);
    }

    void test_main(int id, int n, int *query_size, int *opt_type, int *result) {
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
                    cout << "cant allocate" << endl;
                }
                query_ans.push_back(ans);
            } else {
                cout << "try to free size = " << query_size[opt_type[i]] << endl;
                pmm_free((long long *)query_ans[opt_type[i]]);
            }
            print_memory_block();
        }
    }

    void print_memory_block() {
        cout << "print in order memory" << endl << "    ";
        long long *ptr = GETNEXT(base);
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
        int n = 5;
        int query_size[] = {45, 55, 55, 0, 50};
        int opt_type[] = {-1, -1, -1, 0, -1};
        int result[] = {0, 1, -1, -1, 2};
        test_main(1, n, query_size, opt_type, result);
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
        SETPREV(GETNEXT(base), block);
        SETNEXT(base, block);
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

                    SETSIZE(smaller_block, GETSIZE(ptr) - real_size);
                    SETNEXT(GETPREV(ptr), smaller_block);
                    SETPREV(GETNEXT(ptr), smaller_block);
                    SETPREV(smaller_block, GETPREV(ptr));
                    SETNEXT(smaller_block, GETNEXT(ptr));
                    SETSIZE(ptr, real_size);
                    return ptr;
                } else {
                    del(ptr);
                    SETSIZE(ptr, real_size);
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
    PMMManagerFirst *a = new PMMManagerFirst(230);
    a->test();
}