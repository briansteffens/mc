data:

;   H  e  l  l  o  ,     w  o  r  l  d  !  \n
    48 65 6c 6c 6f 2c 20 77 6f 72 6c 64 21 0a

;   G  r  e  e  t  i  n  g  s  !  \n
    47 72 65 65 74 69 6e 67 73 21 0a

code:
    48 b8 01 00 00 00 00 00 00 00       ; mov rax, 1
    48 b8 01 00 00 00 00 00 00 00       ; mov rax, 1
    48 bf 01 00 00 00 00 00 00 00       ; mov rdi, 1
    48 be +0                            ; mov rsi, [data + 0]
    48 ba 0e 00 00 00 00 00 00 00       ; mov rdx, 14
    0f 05                               ; syscall

    48 b8 01 00 00 00 00 00 00 00       ; mov rax, 1
    48 b8 01 00 00 00 00 00 00 00       ; mov rax, 1
    48 bf 01 00 00 00 00 00 00 00       ; mov rdi, 1
    48 be +14                           ; mov rsi, [data + 14]
    48 ba 0e 00 00 00 00 00 00 00       ; mov rdx, 11
    0f 05                               ; syscall

    48 b8 3c 00 00 00 00 00 00 00       ; mov rax, 60
    48 bf 4d 00 00 00 00 00 00 00       ; mov rdi, 77
    0f 05                               ; syscall
