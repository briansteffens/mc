#!/usr/bin/env python3

import os
import sys
import stat
import struct
from enum import Enum

if len(sys.argv) != 2:
    print("Usage: ./mc.py <filename>")

b = lambda s, x: [b for b in struct.pack(s, x)]
b2 = lambda x: b("H", x)
b4 = lambda x: b("I", x)
b8 = lambda x: b("L", x)
bstr = lambda x: [ord(b) for b in x] + [0]

def pad(start, alignment):
    ret = 0

    while True:
        if (start + ret) % alignment == 0:
            return ret

        ret += 1

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

class ProgramHeader(object):

    def __init__(self):
        self.p_type = PT_NULL
        self.p_flags = 0
        self.p_offset = 0
        self.p_vaddr = 0
        self.p_paddr = 0
        self.p_filesz = 0
        self.p_memsz = 0
        self.p_align = 0

    def to_bytes(self):
        ret = []

        ret.extend(b4(self.p_type))
        ret.extend(b4(self.p_flags))
        ret.extend(b8(self.p_offset))
        ret.extend(b8(self.p_vaddr))
        ret.extend(b8(self.p_paddr))
        ret.extend(b8(self.p_filesz))
        ret.extend(b8(self.p_memsz))
        ret.extend(b8(self.p_align))

        return ret

class SectionHeader(object):

    def __init__(self):
        self.name = None
        self.name_offset = 0
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

        ret.extend(b4(self.name_offset))
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

# program source --------------------------------------------------------------

with open(sys.argv[1]) as f:
    source = f.readlines()

section = "code"

source_bytes = {
    "code": [],
    "data": []
}

for line in source:
    line = line.split(";")[0].strip()

    if not line:
        continue

    if line.endswith(":"):
        section = line[:-1]
        continue

    if section not in source_bytes:
        print("Line not in section: {}".format(line))
        sys.exit(1)

    source_bytes[section] += [int(b, 16) for b in line.split()]

program_bytes = source_bytes["code"]
data_bytes = source_bytes["data"]


# symtab ----------------------------------------------------------------------

# symtab + 0 (24 bytes) symtab0
symtab0 = SymbolTableEntry()

# symtab + 24 (24 bytes) symtab1
symtab1 = SymbolTableEntry()
symtab1.info = STT_SECTION
symtab1.section_header_index = 1
symtab1.value = 4194432 # >> 4194480 (+48)

# symtab + 48 (24 bytes) symtab2
symtab2 = SymbolTableEntry()
symtab2.name = "add.asm"
symtab2.info = STT_FILE
symtab2.section_header_index = 65521

# symtab + 72 (24 bytes) symtab3
symtab3 = SymbolTableEntry()
symtab3.name = "_start"
symtab3.info = 16 # ?
symtab3.section_header_index = 1

# symtab + 96 (24 bytes) symtab4
symtab4 = SymbolTableEntry()
symtab4.name = "__bss_start"
symtab4.info = 16 # ?
symtab4.section_header_index = 5
symtab4.value = 6291596 # >> 6291658 (+64)

# symtab + 120 (24 bytes) symtab5
symtab5 = SymbolTableEntry()
symtab5.name = "_edata"
symtab5.info = 16 # ?
symtab5.section_header_index = 5
symtab5.value = 6291596 # >> 62915658 (+64)

# symtab + 144 (24 bytes) symtab6
symtab6 = SymbolTableEntry()
symtab6.name = "_end"
symtab6.info = 16 # ?
symtab6.section_header_index = 5
symtab6.value = 6291600 # >> 6291664 (+64)

# symtab + 168 (24 bytes) symtab7
symtab7 = SymbolTableEntry()
symtab7.info = STT_SECTION
symtab7.section_header_index = 5

# symtab + 192 (24 bytes) symtab8
symtab8 = SymbolTableEntry()
symtab8.name = "text"
symtab8.section_header_index = 5

symtab = [
    symtab0,
    symtab1,
    symtab2,
    symtab3,
    symtab4,
    symtab5,
    symtab6,
    symtab7,
    symtab8
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

# section headers -------------------------------------------------------------

# e_shoff + 0 - 0x00 section header entry
sh_zero = SectionHeader()

# e_shoff + 64 - 0x1b section header entry
sh_text = SectionHeader()
sh_text.name = "text"
sh_text.type = SHT_PROGBITS
sh_text.flags = 6
sh_text.addr = 4194432
sh_text.addralign = 16

# e_shoff + 128 - 0x11 section header entry
sh_shstrtab = SectionHeader()
sh_shstrtab.name = "shstrtab"
sh_shstrtab.type = SHT_STRTAB
sh_shstrtab.flags = 0
sh_shstrtab.addr = 0
sh_shstrtab.addralign = 1

# e_shoff + 192 - 0x01 section header entry
sh_symtab = SectionHeader()
sh_symtab.name = "symtab"
sh_symtab.type = SHT_SYMTAB
sh_symtab.link = 4
sh_symtab.info = 3
sh_symtab.addralign = 8
sh_symtab.entsize = 24

# e_shoff + 256 - 0x09 section header entry
sh_strtab = SectionHeader()
sh_strtab.name = "strtab"
sh_strtab.type = SHT_STRTAB
sh_strtab.addralign = 1

# e_shoff + 320 - data section
sh_data = SectionHeader()
sh_data.name = "data"
sh_data.type = SHT_PROGBITS
sh_data.flags = 3
sh_data.addralign = 4

section_headers = [
    sh_zero,
    sh_text,
    sh_shstrtab,
    sh_symtab,
    sh_strtab,
    sh_data
]

# shstrtab --------------------------------------------------------------------

# Build shstrtab and set section header name offsets
shstrtab = []
offset = 1

for sh in section_headers:
    if sh.name is None:
        continue

    shstrtab.append(sh.name)
    sh.name_offset = offset
    offset += len(sh.name) + 2

# Render shstrtab binary
shstrtab_bytes = [0]

for s in shstrtab:
    shstrtab_bytes.append(0x2e) # TODO: unknown
    shstrtab_bytes.extend(bstr(s))

# program headers -------------------------------------------------------------

code_header = ProgramHeader()
code_header.p_type = PT_LOAD
code_header.p_flags = PF_R | PF_X
code_header.p_offset = 0
code_header.p_vaddr = 4194304
code_header.p_paddr = 4194304
code_header.p_align = 2097152

data_header = ProgramHeader()
data_header.p_type = PT_LOAD
data_header.p_flags = PF_R | PF_W
data_header.p_filesz = len(data_bytes)
data_header.p_memsz = len(data_bytes)
data_header.p_align = 2097152

program_headers = [
    code_header,
    data_header
]

program_header_byte_count = len(program_headers) * 56

# final calculations ----------------------------------------------------------

symtab_byte_count = len(symtab) * 24

sh_text.size = len(program_bytes)
sh_data.size = len(data_bytes)
sh_symtab.size = len(symtab_bytes)
sh_strtab.size = len(strtab_bytes)
sh_shstrtab.size = len(shstrtab_bytes)

sh_text.offset = 64 + program_header_byte_count

sh_data.offset = sh_text.offset + sh_text.size
pad_data = pad(sh_data.offset, 4)
sh_data.offset += pad_data

sh_symtab.offset = sh_data.offset + sh_data.size
pad_symtab = pad(sh_symtab.offset, 8)
sh_symtab.offset += pad_symtab

sh_strtab.offset = sh_symtab.offset + sh_symtab.size
sh_shstrtab.offset = sh_strtab.offset + sh_strtab.size

e_shoff = (
    64 +
    program_header_byte_count +
    len(program_bytes) +
    pad_data +
    len(data_bytes) +
    pad_symtab +
    len(symtab_bytes) +
    len(strtab_bytes) +
    len(shstrtab_bytes)
)

pad_section_headers = pad(e_shoff, 4)
e_shoff += pad_section_headers

code_header.p_filesz = sh_text.offset + sh_text.size
code_header.p_memsz = code_header.p_filesz

data_header.p_vaddr = data_header.p_align * 3 + sh_data.offset
data_header.p_paddr = data_header.p_vaddr
symtab7.value = data_header.p_vaddr
symtab8.value = data_header.p_vaddr
sh_data.addr = data_header.p_vaddr

entry_point = code_header.p_vaddr + sh_text.offset
symtab3.value = entry_point

data_header.p_offset = sh_data.offset

# Render section headers
section_headers_bytes = []

for sh in section_headers:
    section_headers_bytes.extend(sh.to_bytes())

# Render program header
program_header_bytes = []

for ph in program_headers:
    program_header_bytes.extend(ph.to_bytes())

# Render symtab
symtab_bytes = []

for st in symtab:
    symtab_bytes.extend(st.to_bytes())

# output ----------------------------------------------------------------------

output = []

# header ----------------------------------------------------------------------

# +0 (4 bytes) EI_MAG
output.extend([0x7f, ord("E"), ord("L"), ord("F")])

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
output.extend(b8(entry_point))

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
output.extend(b2(len(program_headers)))

# +58 (2 bytes) e_shentsize
output.extend(b2(64))

# +60 (2 bytes) e_shnum
output.extend(b2(len(section_headers)))

# +62 (2 bytes) e_shstrndx
output.extend(b2(2)) # >> 3

output.extend(program_header_bytes)
output.extend(program_bytes)
output.extend([0 for i in range(pad_data)])
output.extend(data_bytes)
output.extend([0 for i in range(pad_symtab)])
output.extend(symtab_bytes)
output.extend(strtab_bytes)
output.extend(shstrtab_bytes)
output.extend([0 for i in range(pad_section_headers)])
output.extend(section_headers_bytes)

output_fn = sys.argv[1]

if output_fn.endswith(".mc"):
    output_fn = output_fn.replace(".mc", "")

output_fn += ".a"

with open(output_fn, "wb") as f:
    f.write(bytes(output))

output_stat = os.stat(output_fn)
os.chmod(output_fn, output_stat.st_mode | stat.S_IEXEC)
