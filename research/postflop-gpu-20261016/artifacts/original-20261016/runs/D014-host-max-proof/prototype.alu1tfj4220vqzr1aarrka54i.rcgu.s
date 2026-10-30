	.def	@feat.00;
	.scl	3;
	.type	0;
	.endef
	.globl	@feat.00
@feat.00 = 0
	.file	"alu1tfj4220vqzr1aarrka54i"
	.def	_RNvCs1njKG4L9aB3_7___rustc12___rust_alloc;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvCs1njKG4L9aB3_7___rustc12___rust_alloc,unique,0
	.globl	_RNvCs1njKG4L9aB3_7___rustc12___rust_alloc
	.p2align	4
_RNvCs1njKG4L9aB3_7___rustc12___rust_alloc:
.Lfunc_begin0:
.seh_proc _RNvCs1njKG4L9aB3_7___rustc12___rust_alloc
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	cmpq	$17, %rdx
	jae	.LBB0_1
	xorl	%edx, %edx
	movq	%rcx, %r8
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	jmp	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
.LBB0_1:
	movq	%rdx, %rsi
	addq	%rdx, %rcx
	xorl	%edi, %edi
	xorl	%edx, %edx
	movq	%rcx, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	je	.LBB0_3
	leaq	-1(%rsi), %rcx
	movq	%rax, %rdx
	andq	%rax, %rcx
	subq	%rcx, %rsi
	addq	%rsi, %rax
	movq	%rdx, -8(%rdx,%rsi)
	movq	%rax, %rdi
.LBB0_3:
	movq	%rdi, %rax
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end0:
	.seh_endproc

	.def	_RNvCs1njKG4L9aB3_7___rustc14___rust_dealloc;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvCs1njKG4L9aB3_7___rustc14___rust_dealloc,unique,1
	.globl	_RNvCs1njKG4L9aB3_7___rustc14___rust_dealloc
	.p2align	4
_RNvCs1njKG4L9aB3_7___rustc14___rust_dealloc:
.Lfunc_begin1:
.seh_proc _RNvCs1njKG4L9aB3_7___rustc14___rust_dealloc
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	%rcx, %rsi
	cmpq	$17, %r8
	jb	.LBB1_2
	movq	-8(%rsi), %rsi
.LBB1_2:
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	rex64 jmpq	*__imp_HeapFree(%rip)
.Lfunc_end1:
	.seh_endproc

	.def	_RNvCs1njKG4L9aB3_7___rustc14___rust_realloc;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvCs1njKG4L9aB3_7___rustc14___rust_realloc,unique,2
	.globl	_RNvCs1njKG4L9aB3_7___rustc14___rust_realloc
	.p2align	4
_RNvCs1njKG4L9aB3_7___rustc14___rust_realloc:
.Lfunc_begin2:
.seh_proc _RNvCs1njKG4L9aB3_7___rustc14___rust_realloc
	pushq	%r15
	.seh_pushreg %r15
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	%r9, %rdi
	movq	%rcx, %rsi
	cmpq	$17, %r8
	jae	.LBB2_1
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	movq	%rdi, %r9
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	.seh_endepilogue
	rex64 jmpq	*__imp_HeapReAlloc(%rip)
.LBB2_1:
	movq	%r8, %r14
	movq	%rdx, %rbx
	addq	%rdi, %r8
	xorl	%r15d, %r15d
	xorl	%edx, %edx
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	je	.LBB2_3
	leaq	-1(%r14), %rcx
	movq	%rax, %rdx
	andq	%rax, %rcx
	subq	%rcx, %r14
	addq	%r14, %rax
	movq	%rdx, -8(%rdx,%r14)
	cmpq	%rbx, %rdi
	cmovbq	%rdi, %rbx
	movq	%rax, %rcx
	movq	%rsi, %rdx
	movq	%rbx, %r8
	movq	%rax, %r15
	callq	memcpy
	movq	-8(%rsi), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB2_3:
	movq	%r15, %rax
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	.seh_endepilogue
	retq
.Lfunc_end2:
	.seh_endproc

	.def	_RNvCs1njKG4L9aB3_7___rustc19___rust_alloc_zeroed;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvCs1njKG4L9aB3_7___rustc19___rust_alloc_zeroed,unique,3
	.globl	_RNvCs1njKG4L9aB3_7___rustc19___rust_alloc_zeroed
	.p2align	4
_RNvCs1njKG4L9aB3_7___rustc19___rust_alloc_zeroed:
.Lfunc_begin3:
.seh_proc _RNvCs1njKG4L9aB3_7___rustc19___rust_alloc_zeroed
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	cmpq	$17, %rdx
	jae	.LBB3_2
	movl	$8, %edx
	movq	%rcx, %r8
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	jmp	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
.LBB3_2:
	movq	%rdx, %rsi
	addq	%rdx, %rcx
	movl	$8, %edx
	movq	%rcx, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	je	.LBB3_4
	leaq	-1(%rsi), %rcx
	movq	%rax, %rdx
	andq	%rax, %rcx
	subq	%rcx, %rsi
	addq	%rsi, %rax
	movq	%rdx, -8(%rdx,%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB3_4:
	xorl	%eax, %eax
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end3:
	.seh_endproc

	.def	_RNvCs1njKG4L9aB3_7___rustc35___rust_no_alloc_shim_is_unstable_v2;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvCs1njKG4L9aB3_7___rustc35___rust_no_alloc_shim_is_unstable_v2,unique,4
	.globl	_RNvCs1njKG4L9aB3_7___rustc35___rust_no_alloc_shim_is_unstable_v2
	.p2align	4
_RNvCs1njKG4L9aB3_7___rustc35___rust_no_alloc_shim_is_unstable_v2:
.Lfunc_begin4:
	retq
.Lfunc_end4:

	.section	.debug$S,"dr"
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp1-.Ltmp0
.Ltmp0:
	.short	.Ltmp3-.Ltmp2
.Ltmp2:
	.short	4353
	.long	0
	.asciz	"prototype.alu1tfj4220vqzr1aarrka54i.rcgu.o"
	.p2align	2, 0x0
.Ltmp3:
	.short	.Ltmp5-.Ltmp4
.Ltmp4:
	.short	4412
	.long	21
	.short	208
	.short	1
	.short	98
	.short	1
	.short	0
	.short	22018
	.short	0
	.short	0
	.short	0
	.asciz	"clang LLVM (rustc version 1.98.1 (48a229cea 2026-09-01))"
	.p2align	2, 0x0
.Ltmp5:
.Ltmp1:
	.p2align	2, 0x0
	.cv_filechecksums
	.cv_stringtable
	.long	241
	.long	.Ltmp7-.Ltmp6
.Ltmp6:
	.short	.Ltmp9-.Ltmp8
.Ltmp8:
	.short	4428
	.long	4099
	.p2align	2, 0x0
.Ltmp9:
.Ltmp7:
	.p2align	2, 0x0
	.section	.debug$T,"dr"
	.p2align	2, 0x0
	.long	4
	.short	0x36
	.short	0x1605
	.long	0x0
	.asciz	"/rustc/48a229ceaefd4985c50990b14116b6d856af0985"
	.short	0x6a
	.short	0x1605
	.long	0x0
	.asciz	"/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\std\\src\\lib.rs\\@\\std.2a1f8e54e2930f4-cgu.0"
	.byte	241
	.short	0xa
	.short	0x1605
	.long	0x0
	.byte	0
	.byte	243
	.byte	242
	.byte	241
	.short	0x1a
	.short	0x1603
	.short	0x5
	.long	0x1000
	.long	0x1002
	.long	0x1001
	.long	0x1002
	.long	0x1002
	.byte	242
	.byte	241
