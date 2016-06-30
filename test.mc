code:
    b8 01 00 00 00                      ; mov rax, 1
    bf 01 00 00 00                      ; mov rdi, 1
    48 be dc 00 60 00 00 00 00 00       ; mov rsi, 6291676
    ba 0e 00 00 00                      ; mov rdx, 14
    0f 05                               ; syscall

    b8 3c 00 00 00                      ; mov rax, 60
    bf 4d 00 00 00                      ; mov rdi, 77
    bf 4e 00 00 00
    0f 05                               ; syscall
