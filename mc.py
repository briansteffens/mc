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

class SectionHeader(object):

    def __init__(self):
        self.name = 0
        self.type = SECTION_TYPE.NULL
        self.flags = 0
        self.addr = 0
        self.offset = 0
        self.size = 0
        self.link = 0
        self.info = 0
        self.addralign = 0
        self.entsize = 0

# 0x180 - 0x00 section header entry? if all zeroes, it could be
sh_zero = SectionHeader()

# 0x1c0 - 0x1b section header entry
sh_text = SectionHeader()
sh_text.name = 27
sh_text.type = SECTION_TYPE.PROGBITS
sh_text.flags = 6
sh_text.addr = 4194432
sh_text.offset = 128
sh_text.size = 12
sh_text.addralign = 16

# 0x200 - 0x11 section header entry
sh_shstrtab = SectionHeader()
sh_shstrtab.name = 17
sh_shstrtab.type = SECTION_TYPE.STRTAB
sh_shstrtab.flags = 0
sh_shstrtab.addr = 0
sh_shstrtab.offset = 348
sh_shstrtab.size = 33
sh_shstrtab.addralign = 1

# 0x240 - 0x01 section header entry
sh_symtab.name = 1
sh_symtab.type = SECTION_TYPE.SYMTAB
sh_symtab.offset = 144
sh_symtab.size = 168
sh_symtab.link = 4
sh_symtab.info = 3
sh_symtab.addralign = 8
sh_symtab.entsize = 24

# 0x280 - 0x09 section header entry
sh_strtab.name = 9
sh_strtab.type = SECTION_TYPE.STRTAB
sh_strtab.offset = 312
sh_strtab.size = 36
sh_strtab.addralign = 1

section_headers = [
    sh_zero,
    sh_text,
    sh_shstrtab,
    sh_symtab,
    sh_strtab
]
