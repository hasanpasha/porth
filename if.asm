segment .text
global _start
dump:
    push    rbp
    mov     rbp, rsp
    sub     rsp, 64
    mov     QWORD  [rbp-56], rdi
    mov     BYTE  [rbp-17], 10
    mov     DWORD  [rbp-4], 30
.L2:
    sub     DWORD  [rbp-4], 1
    mov     rcx, QWORD  [rbp-56]
    mov     rdx, -3689348814741910323
    mov     rax, rcx
    mul     rdx
    shr     rdx, 3
    mov     rax, rdx
    sal     rax, 2
    add     rax, rdx
    add     rax, rax
    sub     rcx, rax
    mov     rdx, rcx
    mov     eax, edx
    add     eax, 48
    mov     edx, eax
    mov     eax, DWORD  [rbp-4]
    cdqe
    mov     BYTE  [rbp-48+rax], dl
    mov     rax, QWORD  [rbp-56]
    mov     rdx, -3689348814741910323
    mul     rdx
    mov     rax, rdx
    shr     rax, 3
    mov     QWORD  [rbp-56], rax
    cmp     QWORD  [rbp-56], 0
    jne     .L2
    mov     eax, 32
    sub     eax, DWORD  [rbp-4]
    cdqe
    lea     rcx, [rbp-48]
    mov     edx, DWORD  [rbp-4]
    movsx   rdx, edx
    add     rcx, rdx
    mov     rdx, rax
    mov     rsi, rcx
    mov     edi, 1
    mov     rax, 0x1
    syscall
;;    call    write
    nop
    leave
    ret
_start:
	;; -- push 10 --
	push 10
	;; -- push 20 --
	push 20
	;; -- plus --
	pop rax
	pop rbx
	add rax, rbx
	push rax
	;; -- push 30 --
	push 30
	;; -- equal --
	mov rcx, 0
	mov rdx, 1
	pop rax
	pop rbx
	cmp rax, rbx
	cmove rcx, rdx
	push rcx
	;; -- dump --
	pop rdi
	call dump
	;; -- push 10 --
	push 10
	;; -- push 20 --
	push 20
	;; -- minux --
	pop rax
	pop rbx
	sub rbx, rax
	push rbx
	;; -- push 30 --
	push 30
	;; -- equal --
	mov rcx, 0
	mov rdx, 1
	pop rax
	pop rbx
	cmp rax, rbx
	cmove rcx, rdx
	push rcx
	;; -- dump --
	pop rdi
	call dump
	;; -- push 30 --
	push 30
	;; -- push 10 --
	push 10
	;; -- plus --
	pop rax
	pop rbx
	add rax, rbx
	push rax
	;; -- push 9 --
	push 9
	;; -- minux --
	pop rax
	pop rbx
	sub rbx, rax
	push rbx
	;; -- push 30 --
	push 30
	;; -- equal --
	mov rcx, 0
	mov rdx, 1
	pop rax
	pop rbx
	cmp rax, rbx
	cmove rcx, rdx
	push rcx
	;; -- dump --
	pop rdi
	call dump
	mov rax, 0x3c
	mov rdi, 0x0
	syscall
