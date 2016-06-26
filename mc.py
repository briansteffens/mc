#!/usr/bin/env python3

import struct
from enum import Enum

b = lambda s, x: [b for b in struct.pack(s, x)]
b2 = lambda x: b('H', x)
b4 = lambda x: b('I', x)
b8 = lambda x: b('L', x)
bstr = lambda x: [ord(b) for b in x] + [0]

# EI_CLASS: 64-bit
ELFCLASS64 = 2

# EI_DATA: little-endian
ELFDATA2LSB = 1

# EI_VERSION: current
EV_CURRENT = 1

# EI_OSABI: UNIX System V ABI
ELFOSABI_SYSV = 0

# e_type values
ET_NONE = 0     # Unknown
ET_REL  = 1     # Relocatable
ET_EXEC = 2     # Executable
ET_DYN  = 3     # Shared (dynamic) object
ET_CORE = 4     # Core file

# e_machine values
EM_X86_64 = 0x3e

# p_type values (segment types)
PT_NULL    = 0          # Unused
PT_LOAD    = 1          # Loadable segment
PT_DYNAMIC = 2          # Dynamic linking information
PT_INTERP  = 3          # Interpreter path
PT_NOTE    = 4          # Auxiliary information
PT_SHLIB   = 5          # Unspecified / invalid
PT_PHDR    = 6          # Locates the program header table
PT_LOPROC  = 0x70000000 # Start of processor-specific semantics
PT_HIPROC  = 0x7fffffff # End of processor-specific semantics

# p_flags - segment flags
PF_R = 4 # Readable
PF_W = 2 # Writable
PF_X = 1 # Executable

# sh_type - section type
SHT_NULL     = 0
SHT_PROGBITS = 1
SHT_SYMTAB   = 2
SHT_STRTAB   = 3
SHT_RELA     = 4
SHT_HASH     = 5
SHT_DYNAMIC  = 6
SHT_NOTE     = 7
SHT_NOBITS   = 8
SHT_REL      = 9
SHT_SHLIB    = 10
SHT_LOPROC   = 0x70000000
SHT_HIPROC   = 0x7fffffff
SHT_LOUSER   = 0x80000000
SHT_HIUSER   = 0xffffffff

# st_info values (symbol type)
STT_NOTYPE  = 0
STT_OBJECT  = 1
STT_FUNC    = 2
STT_SECTION = 3
STT_FILE    = 4
STT_LOPROC  = 13
STT_HIPROC  = 15

# st_info values (symbol binding)
STB_LOCAL = 0
STB_GLOBAL = 1
STB_WEAK = 2
STB_LOPROC = 13
STB_HIPROC = 15

# st_other values (symbol visibility)
STV_DEFAULT = 0
STV_INTERNAL = 1
STV_HIDDEN = 2
STV_PROTECTED = 3

class SectionHeader(object):

    def __init__(self):
        self.name = 0
        self.type = SHT_NULL
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
        ret.extend(b4(self.type))
        ret.extend(b8(self.flags))
        ret.extend(b8(self.addr))
        ret.extend(b8(self.offset))
        ret.extend(b8(self.size))
        ret.extend(b4(self.link))
        ret.extend(b4(self.info))
        ret.extend(b8(self.addralign))
        ret.extend(b8(self.entsize))

        return ret

class SymbolTableEntry(object):

    def __init__(self):
        self.name = None
        self.name_offset = 0
        self.info = STT_NOTYPE
        self.other = STV_DEFAULT
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

        ret.extend(b4(self.name_offset))
        ret.append(self.info)
        ret.append(self.other)
        ret.extend(b2(self.section_header_index))
        ret.extend(b8(self.value))
        ret.extend(b8(self.size))

        return ret

e_shoff = 388

output = []

# header ----------------------------------------------------------------------

# +0 (4 bytes) EI_MAG
output.extend([0x7f, ord('E'), ord('L'), ord('F')])

# +4 (1 byte) EI_CLASS
output.append(ELFCLASS64)

# +5 (1 byte) EI_DATA
output.append(ELFDATA2LSB)

# +6 (1 byte) EI_VERSION
output.append(EV_CURRENT)

# +7 (1 byte) EI_OSABI
output.append(ELFOSABI_SYSV)

# +8 (1 byte) EI_ABIVERSION
output.append(0)

# +9 (7 bytes) EI_PAD
output.extend([0, 0, 0, 0, 0, 0, 0])

# +16 (2 bytes) e_type
output.extend(b2(ET_EXEC))

# +18 (2 bytes) e_machine
output.extend(b2(EM_X86_64))

# +20 (4 bytes) e_version
output.extend(b4(EV_CURRENT))

# +24 (8 bytes) e_entry
output.extend(b8(4194432))

# +32 (8 bytes) e_phoff
output.extend(b8(64))

# +40 (8 bytes) e_shoff
output.extend(b8(e_shoff))

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

# ? ---------------------------------------------------------------------------

# +64 (4 bytes) p_type
output.extend(b4(PT_LOAD))

# +68 (4 bytes) p_flags
output.extend(b4(PF_R | PF_X))

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

# program code ----------------------------------------------------------------

# code + 0 (16 bytes) code section
output.extend([0xb8, 0x3c, 0, 0, 0])    # mov rax, 60
output.extend([0xbf, 0x4d, 0, 0, 0])    # mov rdi, 77
output.extend([0x48, 0x83, 0xc7, 0x03]) # add rdi, 3
output.extend([0x0f, 0x05])             # syscall

# code + 16 (4 bytes) TODO: unknown
output.extend([0, 0, 0, 0])

# symtab ----------------------------------------------------------------------

# symtab + 0 (24 bytes) symtab0
symtab0 = SymbolTableEntry()

# symtab + 24 (24 bytes) symtab1
symtab1 = SymbolTableEntry()
symtab1.info = STT_SECTION
symtab1.section_header_index = 1
symtab1.value = 4194432

# symtab + 48 (24 bytes) symtab2
symtab2 = SymbolTableEntry()
symtab2.name = "exit77.asm"
symtab2.info = STT_FILE
symtab2.section_header_index = 65521

# symtab + 72 (24 bytes) symtab3
symtab3 = SymbolTableEntry()
symtab3.name = "_start"
symtab3.info = 16 # ?
symtab3.section_header_index = 1
symtab3.value = 4194432

# symtab + 96 (24 bytes) symtab4
symtab4 = SymbolTableEntry()
symtab4.name = "__bss_start"
symtab4.info = 16 # ?
symtab4.section_header_index = 1
symtab4.value = 6291596

# symtab + 120 (24 bytes) symtab5
symtab5 = SymbolTableEntry()
symtab5.name = "_edata"
symtab5.info = 16 # ?
symtab5.section_header_index = 1
symtab5.value = 6291596

# symtab + 144 (24 bytes) symtab6
symtab6 = SymbolTableEntry()
symtab6.name = "_end"
symtab6.info = 16 # ?
symtab6.section_header_index = 1
symtab6.value = 6291600

symtab = [
    symtab0,
    symtab1,
    symtab2,
    symtab3,
    symtab4,
    symtab5,
    symtab6
]

# strtab ----------------------------------------------------------------------

# Grab strings from symtab
strtab = [st.name for st in symtab if st.name]

# Deduplicate strings. If a string ends with another string it's considered
# a duplicate since we can set an offset to partway through a string.
duplicates = []

for si in range(len(strtab)):
    s = strtab[si]

    for s2i in range(len(strtab)):
        if si == s2i:
            continue

        s2 = strtab[s2i]

        if s2.endswith(s):
            if s not in duplicates:
                duplicates.append(s)

for d in duplicates:
    strtab.remove(d)

# Set offsets in symtab
offset = 1

for s in strtab:
    for st in symtab:
        if st.name is None or st.name_offset != 0:
            continue

        if s.endswith(st.name):
            st.name_offset = offset + s.find(st.name)

    offset += len(s) + 1

# Render strtab binary
strtab_bytes = [0]

for s in strtab:
    strtab_bytes.extend(bstr(s))

# render symtab ---------------------------------------------------------------

symtab_bytes = []

for st in symtab:
    symtab_bytes.extend(st.to_bytes())

output.extend(symtab_bytes)
output.extend(strtab_bytes)

# shstrtab --------------------------------------------------------------------

# shstrtab + 0 (1 byte) # TODO: unknown
output.append(0)

# shstrtab + 1 (1 byte) # TODO: unknown (all these 0x2e bytes)
output.append(0x2e)

# shstrtab + 2 (7 bytes)
output.extend(bstr("symtab"))

# shstrtab + 9 (1 byte)
output.append(0x2e)

# shstrtab + 10 (7 bytes)
output.extend(bstr("strtab"))

# shstrtab + 17 (1 byte)
output.append(0x2e)

# shstrtab + 18 (9 bytes)
output.extend(bstr("shstrtab"))

# shstrtab + 27 (1 byte)
output.append(0x2e)

# shstrtab + 28 (5 bytes)
output.extend(bstr("text"))

# shstrtab + 33 (3 bytes) # TODO: unknown
output.extend([0, 0, 0])

# section headers -------------------------------------------------------------

# e_shoff + 0 - 0x00 section header entry
sh_zero = SectionHeader()
output.extend(sh_zero.to_bytes())

# e_shoff + 64 - 0x1b section header entry
sh_text = SectionHeader()
sh_text.name = 27
sh_text.type = SHT_PROGBITS
sh_text.flags = 6
sh_text.addr = 4194432
sh_text.offset = 128
sh_text.size = 12
sh_text.addralign = 16
output.extend(sh_text.to_bytes())

# e_shoff + 128 - 0x11 section header entry
sh_shstrtab = SectionHeader()
sh_shstrtab.name = 17
sh_shstrtab.type = SHT_STRTAB
sh_shstrtab.flags = 0
sh_shstrtab.addr = 0
sh_shstrtab.offset = 352
sh_shstrtab.size = 33
sh_shstrtab.addralign = 1
output.extend(sh_shstrtab.to_bytes())

# e_shoff + 192 - 0x01 section header entry
sh_symtab = SectionHeader()
sh_symtab.name = 1
sh_symtab.type = SHT_SYMTAB
sh_symtab.offset = 148
sh_symtab.size = 168
sh_symtab.link = 4
sh_symtab.info = 3
sh_symtab.addralign = 8
sh_symtab.entsize = 24
output.extend(sh_symtab.to_bytes())

# e_shoff + 256 - 0x09 section header entry
sh_strtab = SectionHeader()
sh_strtab.name = 9
sh_strtab.type = SHT_STRTAB
sh_strtab.offset = 316
sh_strtab.size = 36
sh_strtab.addralign = 1
output.extend(sh_strtab.to_bytes())

with open('output', 'wb') as f:
    f.write(bytes(output))
