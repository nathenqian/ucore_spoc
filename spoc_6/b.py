from memory import *

addr = 0x03df
print "virtual address is " + str(hex(addr))
index_dir = 0x11;
pde = 0b111110000000000
pde_result = mem[index_dir][(addr & pde) >> 10]
print "    pde index : " + str(hex((addr & pde) >> 10)) + \
    "   pde content : (value = " + str(hex(pde_result & 0b01111111)) + \
    " valid = " + str((pde_result & 0b10000000) >> 7) + ")"
if ((pde_result & 0b10000000) >> 7 == 1):
    pte = 0b1111100000
    pte_addr = ((pde_result & 0b01111111) << 5) + ((addr & pte) >> 5)
    pte_result = mem[pte_addr >> 5][pte_addr & 0b11111]
    print "        ptd index : " + str(hex(((addr & pte) >> 5))) + \
        "   pte content : (value = " + str(hex(pte_result & 0b01111111)) + \
        " valid = " + str((pte_result & 0b10000000) >> 7) + ")"
    if ((pte_result & 0b10000000) >> 7) == 1:
        print "            translate to physical addr : " + \
            hex(((pte_result & 0b01111111) << 5) + (addr & 0b11111)) + \
            " --> value : " + str(hex(mem[((pte_result & 0b01111111))][addr & 0b11111]))        

