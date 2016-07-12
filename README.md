mc
==

Ever feel like assembly is just too high level? Tired of all those ugly letters
and fragments of words?? Now, thanks to recent scientific discoveries and brand
new technology, you can write machine code in hex!

Why write something nasty and hard to understand like this:

```asm
    mov rax, 60
    mov rdi, 77
    syscall
```

When you could write this!

```mc
    48 b8 3c 00 00 00 00 00 00 00
    48 bf 4d 00 00 00 00 00 00 00
    0f 05
```

Much clearer isn't it? Now you can finally be a productive programmer. You're
welcome!
