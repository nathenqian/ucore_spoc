# coding:utf-8
import sys

if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1][0:2] != "0x" or sys.argv[2][0:2] != "0x":
        print "Usage: virtual_address pyhsical_address(in hex, e.g., 0xcd82c07c 0x0c20907c)"
        sys.exit(0)


    virtual_address = int(sys.argv[1][2:], 16)              # 虚拟地址
    physical_addr = int(sys.argv[2][2:], 16)                # 物理地址

    pde_index = (virtual_address & 0xffc00000) >> 22        # 一级页表（页目录）的索引是高10位

    pte_addr = pde_index - 0x300 + 1                        # 根据题目条件直接计算表项中的内容，即页表高22位地址

    pde_ctx = (pte_addr << 12) + 3                          # 根据内容扩展成表项的格式，即填上标志位

    pte_index = (virtual_address & 0x003FF000) >> 12        # 二级页表的索引是中间10位

    pp_addr = physical_addr >> 12                           # 物理页地址是物理地址的高20位

    pte_ctx = (pp_addr << 12) + 3                           # 扩展成页表项的形式，即填上标志位

    print 'va 0x%08x, pa 0x%08x, pde_idx 0x%08x, pde_ctx 0x%08x, pte_idx 0x%08x, pte_ctx 0x%08x' \
         % (virtual_address, physical_addr, pde_index, pde_ctx, pte_index, pte_ctx)