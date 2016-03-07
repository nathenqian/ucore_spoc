# struct pmm_manager {
#     const char *name;                                 // XXX_pmm_manager's name
#     void (*init)(void);                               // initialize internal description&management data structure
#                                                       // (free block list, number of free block) of XXX_pmm_manager 
#     void (*init_memmap)(struct Page *base, size_t n); // setup description&management data structcure according to
#                                                       // the initial free physical memory space 
#     struct Page *(*alloc_pages)(size_t n);            // allocate >=n pages, depend on the allocation algorithm 
#     void (*free_pages)(struct Page *base, size_t n);  // free >=n pages with "base" addr of Page descriptor structures(memlayout.h)
#     size_t (*nr_free_pages)(void);                    // return the number of free pages 
#     void (*check)(void);                              // check the correctness of XXX_pmm_manager 
# };

class ListEntry():
    def __init__(self, data):
        self.data = data
        self.next = self
        self.prev = self
    def add_next(self, next_block):
        next_block.prev = self
        next_block.next = self.next
        self.next.prev = next_block
        self.next = next_block

class PMMManager:
    def __init__(self, memorys):
        self.list_head = ListEntry((0, 0))
        for memory_block in memorys:
            self.list.prev.add_next(memory)
    def 