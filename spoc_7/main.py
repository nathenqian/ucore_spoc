# coding:utf-8
import sys

def tohex(i):
    return str(hex(i))

if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1][0:2] != "0x" or sys.argv[2][0:2] != "0x":
        print "Usage: virtual_address(in hex, e.g., 0x03df)"
        sys.exit(0)


    virtual_address = int(sys.argv[1][2:], 16) # 虚拟地址
    phy_addr = int(sys.argv[2][2:], 16)

    pde_index = (virtual_address & 0xffc00000) >> 22

    pde_ctx = pde_index - 0x300 + 1

    pte_addr = pde_ctx << 12

    pte_index = (virtual_address & 0x003FF000) >> 12

    pte_ctx = phy_addr >> 12

    print "va = " + tohex(virtual_address) + " pa = " + tohex(phy_addr) + \
        " pde_idx = " + tohex(pde_index)  + " pde_ctx = " + tohex((pde_ctx << 12) + 3) + \
        " pte_index = " + tohex(pte_index) + " pte_ctx = " + tohex((pte_ctx << 12) + 3)