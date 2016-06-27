code:
    b8 3c 00 00 00  ; mov rax, 60
    bf 4d 00 00 00  ; mov rdi, 77
    48 83 c7 03     ; add rdi, 3
    48 83 c7 08     ; add rdi, 8
    0f 05           ; syscall
