#!/usr/bin/env python3

import struct
from enum import Enum

b = lambda s, x: [b for b in struct.pack(s, x)]
b2 = lambda x: b('H', x)
b4 = lambda x: b('I', x)
b8 = lambda x: b('L', x)
bstr = lambda x: [ord(b) for b in x] + [0]

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

    def to_bytes(self):
        ret = []

        ret.extend(b4(self.name))
        ret.extend(b4(self.type.value))
        ret.extend(b8(self.flags))
        ret.extend(b8(self.addr))
        ret.extend(b8(self.offset))
        ret.extend(b8(self.size))
        ret.extend(b4(self.link))
        ret.extend(b4(self.info))
        ret.extend(b8(self.addralign))
        ret.extend(b8(self.entsize))

        return ret

class SymbolTableBind(Enum):
    STB_LOCAL = 0
    STB_GLOBAL = 1
    STB_WEAK = 2
    STB_LOOS = 10
    STB_HIOS = 12
    STB_LOPROC = 13
    STB_HIPROC = 15

class SymbolTableType(Enum):
    STT_NOTYPE = 0
    STT_OBJECT = 1
    STT_FUNC = 2
    STT_SECTION = 3
    STT_FILE = 4
    STT_COMMON = 5
    STT_TLS = 6
    STT_LOOS = 10
    STT_HIOS = 12
    STT_LOPROC = 13
    STT_HIPROC = 15

class SymbolTableOther(Enum):
    STV_DEFAULT = 0
    STV_INTERNAL = 1
    STV_HIDDEN = 2
    STV_PROTECTED = 3
    STV_EXPORTED = 4
    STV_SINGLETON = 5
    STV_ELIMINATE = 6

class SymbolTableEntry(object):

    def __init__(self):
        self.name = 0
        self.info = SymbolTableType.STT_NOTYPE
        self.other = SymbolTableOther.STV_DEFAULT
        self.section_header_index = 0
        self.value = 0
        self.size = 0

    def set_type(self, b, t):
        self.info = (b << 4) | t

    @property
    def info_type(self):
        return self.info & 0xf

    @info_type.setter
    def info_type(self, t):
        self.info = self.set_type(self.info_bind, t)

    @property
    def info_bind(self):
        return self.info >> 4

    @info_bind.setter
    def info_bind(self, b):
        self.info = self.set_type(b, self.info_type)

    def to_bytes(self):
        ret = []

        ret.extend(b4(self.name))

        if hasattr(self.info, 'value'):
            ret.append(self.info.value)
        else:
            ret.append(self.info)

        ret.append(self.other.value)
        ret.extend(b2(self.section_header_index))
        ret.extend(b8(self.value))
        ret.extend(b8(self.size))

        return ret

output = []

# +0 (4 bytes) EI_MAG
output.extend([0x7f, ord('E'), ord('L'), ord('F')])

# +4 (1 byte) EI_CLASS
output.append(CLASS.BITS_64.value)

# +5 (1 byte) EI_DATA
output.append(DATA.ENDIANNESS_LITTLE.value)

# +6 (1 byte) EI_VERSION
output.append(1)

# +7 (1 byte) EI_OSABI
output.append(ABI.SYSTEM_V.value)

# +8 (1 byte) EI_ABIVERSION
output.append(0)

# +9 (7 bytes) EI_PAD
output.extend([0, 0, 0, 0, 0, 0, 0])

# +16 (2 bytes) e_type
output.extend(b2(TYPE.EXECUTABLE.value))

# +18 (2 bytes) e_machine
output.extend(b2(ISA.X86_64.value))

# +20 (4 bytes) e_version
output.extend(b4(1))

# +24 (8 bytes) e_entry
output.extend(b8(4194432))

# +32 (8 bytes) e_phoff
output.extend(b8(64))

# +40 (8 bytes) e_shoff
output.extend(b8(384))

# +48 (4 bytes) e_flags
output.extend([0, 0, 0, 0])

# +52 (2 bytes) e_ehsize
output.extend(b2(64))

# +54 (2 bytes) e_phentsize
output.extend(b2(56))

# +56 (2 bytes) e_phnum
output.extend(b2(1))

# +58 (2 bytes) e_shentsize
output.extend(b2(64))

# +60 (2 bytes) e_shnum
output.extend(b2(5))

# +62 (2 bytes) e_shstrndx
output.extend(b2(2))

# +64 (4 bytes) p_type
output.extend(b4(SEGMENT_TYPE.LOAD.value))

# +68 (4 bytes) p_flags
output.extend(b4(5))

# +72 (8 bytes) p_offset
output.extend(b8(0))

# +80 (8 bytes) p_vaddr
output.extend(b8(4194304))

# +88 (8 bytes) p_paddr
output.extend(b8(4194304))

# +96 (8 bytes) p_filesz
output.extend(b8(140))

# +104 (8 bytes) p_memsz
output.extend(b8(140))

# +112 (8 bytes) p_align
output.extend(b8(2097152))

# +120 (8 bytes) TODO: unknown
output.extend([0, 0, 0, 0, 0, 0, 0, 0])

# +128 (12 bytes) code section
output.extend([0xb8, 0x3c, 0, 0, 0]) # mov rax, 60
output.extend([0xbf, 0x4d, 0, 0, 0]) # mov rdi, 99
output.extend([0x0f, 0x05])          # syscall

# +140 (4 bytes) TODO: unknown
output.extend([0, 0, 0, 0])

# +144 (24 bytes) symtab0
symtab0 = SymbolTableEntry()
output.extend(symtab0.to_bytes())

# +168 (24 bytes) symtab1
symtab1 = SymbolTableEntry()
symtab1.info = SymbolTableType.STT_SECTION
symtab1.section_header_index = 1
symtab1.value = 4194432
output.extend(symtab1.to_bytes())

# +192 (24 bytes) symtab2
symtab2 = SymbolTableEntry()
symtab2.name = 1 # exit77.asm
symtab2.info = SymbolTableType.STT_FILE
symtab2.section_header_index = 65521
output.extend(symtab2.to_bytes())

# +216 (24 bytes) symtab3
symtab3 = SymbolTableEntry()
symtab3.name = 17 # _start?
symtab3.info = 16 # ?
symtab3.section_header_index = 1
symtab3.value = 4194432
output.extend(symtab3.to_bytes())

# +240 (24 bytes) symtab4
symtab4 = SymbolTableEntry()
symtab4.name = 12 # __bss_start
symtab4.info = 16 # ?
symtab4.section_header_index = 1
symtab4.value = 6291596
output.extend(symtab4.to_bytes())

# +264 (24 bytes) symtab5
symtab5 = SymbolTableEntry()
symtab5.name = 24 # _edata
symtab5.info = 16 # ?
symtab5.section_header_index = 1
symtab5.value = 6291596
output.extend(symtab5.to_bytes())

# +288 (24 bytes) symtab6
symtab6 = SymbolTableEntry()
symtab6.name = 31 # _end
symtab6.info = 16 # ?
symtab6.section_header_index = 1
symtab6.value = 6291600
output.extend(symtab6.to_bytes())

# strtab ----------------------------------------------------------------------

# +312 (1 byte)
output.append(0)

# +313 (11 bytes) first string
output.extend(bstr("exit77.asm"))

# +324 (12 bytes) second string
output.extend(bstr("__bss_start"))

# +336 (7 bytes) third string
output.extend(bstr("_edata"))

# +343 (5 bytes) fourth string
output.extend(bstr("_end"))

# shstrtab --------------------------------------------------------------------

# +348 (1 byte) # TODO: unknown
output.append(0)

# +349 (1 byte) # TODO: unknown (all these 0x2e bytes)
output.append(0x2e)

# +350 (7 bytes)
output.extend(bstr("symtab"))

# +357 (1 byte)
output.append(0x2e)

# +358 (7 bytes)
output.extend(bstr("strtab"))

# +365 (1 byte)
output.append(0x2e)

# +366 (9 bytes)
output.extend(bstr("shstrtab"))

# +375 (1 byte)
output.append(0x2e)

# +376 (5 bytes)
output.extend(bstr("text"))

# +381 (3 bytes) # TODO: unknown
output.extend([0, 0, 0])

# section headers -------------------------------------------------------------

# +384 - 0x00 section header entry
sh_zero = SectionHeader()
output.extend(sh_zero.to_bytes())

# +448 - 0x1b section header entry
sh_text = SectionHeader()
sh_text.name = 27
sh_text.type = SECTION_TYPE.PROGBITS
sh_text.flags = 6
sh_text.addr = 4194432
sh_text.offset = 128
sh_text.size = 12
sh_text.addralign = 16
output.extend(sh_text.to_bytes())

# +512 - 0x11 section header entry
sh_shstrtab = SectionHeader()
sh_shstrtab.name = 17
sh_shstrtab.type = SECTION_TYPE.STRTAB
sh_shstrtab.flags = 0
sh_shstrtab.addr = 0
sh_shstrtab.offset = 348
sh_shstrtab.size = 33
sh_shstrtab.addralign = 1
output.extend(sh_shstrtab.to_bytes())

# +576 - 0x01 section header entry
sh_symtab = SectionHeader()
sh_symtab.name = 1
sh_symtab.type = SECTION_TYPE.SYMTAB
sh_symtab.offset = 144
sh_symtab.size = 168
sh_symtab.link = 4
sh_symtab.info = 3
sh_symtab.addralign = 8
sh_symtab.entsize = 24
output.extend(sh_symtab.to_bytes())

# +640 - 0x09 section header entry
sh_strtab = SectionHeader()
sh_strtab.name = 9
sh_strtab.type = SECTION_TYPE.STRTAB
sh_strtab.offset = 312
sh_strtab.size = 36
sh_strtab.addralign = 1
output.extend(sh_strtab.to_bytes())

with open('output', 'wb') as f:
    f.write(bytes(output))
