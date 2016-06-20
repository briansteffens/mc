#!/usr/bin/env python3

from enum import Enum

class CLASS(Enum):
    BITS_32 = 1
    BITS_64 = 2

class DATA(Enum):
    ENDIANNESS_LITTLE = 1
    ENDIANNESS_BIG = 2

class TYPE(Enum):
    RELOCATABLE = 1
    EXECUTABLE = 2
    SHARED = 3
    CORE = 4

class ABI(Enum):
    SYSTEM_V = 0x00

class ISA(Enum):
    NONE = 0x00
    SPARC = 0x02
    X86 = 0x03
    MIPS = 0x08
    POWERPC = 0x14
    ARM = 0x28
    SUPERH = 0x2a
    IA64 = 0x32
    X86_64 = 0x3e
    AARCH64 = 0xb7

ei_magic = [0x7f, ord('E'), ord('L'), ord('F')]
ei_class = CLASS.BITS_64
ei_data = DATA.ENDIANNESS_LITTLE
ei_version = 1
ei_osabi = ABI.SYSTEM_V
ei_abiversion = 0
ei_pad = [0, 0, 0, 0, 0, 0, 0]

e_type = TYPE.EXECUTABLE
e_machine = ISA.X86_64
e_version = 1
e_entry = 4194432
e_phoff = 0x40 if ei_class == CLASS.BITS_64 else 0x34
e_shoff = 384
e_flags = 0
e_ehsize = 64 if ei_class == CLASS.BITS_64 else 52
e_ehsize = 64 if ei_class == CLASS.BITS_64 else 52
e_phentsize = 56
e_phnum = 1
e_shentsize = 64
e_shnum = 5
e_shstrndx = 2

class SEGMENT_TYPE(Enum):
    NULL    = 0x00000000
    LOAD    = 0x00000001
    DYNAMIC = 0x00000002
    INTERP  = 0x00000003
    NOTE    = 0x00000004
    SHLIB   = 0x00000005
    PHDR    = 0x00000006
    LOOS    = 0x60000000
    HIOS    = 0x6fffffff
    LOPROC  = 0x70000000
    HIPROC  = 0x7fffffff

class SECTION_TYPE(Enum):
    NULL     = 0x00000000
    PROGBITS = 0x00000001
    SYMTAB   = 0x00000002
    STRTAB   = 0x00000003
    RELA     = 0x00000004
    HASH     = 0x00000005
    DYNAMIC  = 0x00000006
    NOTE     = 0x00000007
    NOBITS   = 0x00000008
    REL      = 0x00000009
    SHLIB    = 0x00000010
    DYNSYM   = 0x00000011
    LOOS     = 0x60000000
    HIOS     = 0x6fffffff
    LOPROC   = 0x70000000
    HIPROC   = 0x7fffffff
    LOUSER   = 0x80000000
    HIUSER   = 0xffffffff

p_type = SEGMENT_TYPE.LOAD
p_flags = 5
p_offset = 0
p_vaddr = 4194304
p_paddr = 4194304
p_filesz = 140
p_memsz = 140
p_align = 2097152
# 0x78

# 0x180 - 0x00 section header entry? if all zeroes, it could be
# 0x1c0 - 0x1b section header entry
#   name: 27 (.text)
#   type: 1 (progbits)
#   flags: 6
#   addr: 4194432
#   offset: 128
#   size: 12
#   link: 0
#   info: 0
#   addralign: 16
#   entsize: 0
# 0x200 - 0x11 section header entry
#   name: 17 (shstrtab)
#   type: 3 (strtab)
#   flags: 0
#   addr: 0
#   offset: 348 (0x15c)
#   size: 33
#   link: 0
#   info: 0
#   addralign: 1
#   entsize: 0
# 0x240 - 0x01 section header entry
#   name: 1
#   type: 2 (symtab)
#   flags: 0
#   addr: 0
#   offset: 144
#   size: 168
#   link: 4
#   info: 3
#   addralign: 8
#   entsize: 24
# 0x280 - 0x09 section header entry
#   name: 9 (.strtab)
#   type: 3 (strtab)
#   flags: 0
#   addr: 0
#   offset: 312
#   size: 36
#   link: 0
#   info: 0
#   addralign: 1
#   entsize: 0
