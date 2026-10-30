	.def	@feat.00;
	.scl	3;
	.type	0;
	.endef
	.globl	@feat.00
@feat.00 = 0
	.file	"crossbeam_utils.3dd90c96c2eaf6b7-cgu.0"
	.def	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecjE8grow_oneCs5jdj61sQu57_15crossbeam_utils;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecjE8grow_oneCs5jdj61sQu57_15crossbeam_utils,unique,0
	.globl	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecjE8grow_oneCs5jdj61sQu57_15crossbeam_utils
	.p2align	4
_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecjE8grow_oneCs5jdj61sQu57_15crossbeam_utils:
.Lfunc_begin0:
.seh_proc _RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecjE8grow_oneCs5jdj61sQu57_15crossbeam_utils
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rdx
	callq	_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner14grow_amortizedCs5jdj61sQu57_15crossbeam_utils
	cmpq	$-1, %rax
	jne	.LBB0_1
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.LBB0_1:
	movq	%rax, %rcx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.Lfunc_end0:
	.seh_endproc

	.def	_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCs5jdj61sQu57_15crossbeam_utils;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCs5jdj61sQu57_15crossbeam_utils,unique,1
	.p2align	4
_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCs5jdj61sQu57_15crossbeam_utils:
.Lfunc_begin1:
.seh_proc _RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCs5jdj61sQu57_15crossbeam_utils
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	%rcx, %rsi
	leaq	(,%r9,8), %rdi
	shrq	$61, %r9
	setne	%al
	movabsq	$9223372036854775800, %rcx
	cmpq	%rcx, %rdi
	seta	%cl
	movl	$1, %ebx
	orb	%al, %cl
	je	.LBB1_2
	movl	$8, %eax
	xorl	%edi, %edi
	jmp	.LBB1_8
.LBB1_2:
	testq	%rdx, %rdx
	je	.LBB1_4
	movq	%r8, %rcx
	movl	$8, %r8d
	movq	%rdi, %rdx
	callq	mi_realloc_aligned
	testq	%rax, %rax
	je	.LBB1_6
.LBB1_7:
	movq	%rax, 8(%rsi)
	movl	$16, %eax
	xorl	%ebx, %ebx
	jmp	.LBB1_8
.LBB1_4:
	movl	$8, %edx
	movq	%rdi, %rcx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	jne	.LBB1_7
.LBB1_6:
	movq	$8, 8(%rsi)
	movl	$16, %eax
.LBB1_8:
	movq	%rdi, (%rsi,%rax)
	movq	%rbx, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end1:
	.seh_endproc

	.def	_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner14grow_amortizedCs5jdj61sQu57_15crossbeam_utils;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner14grow_amortizedCs5jdj61sQu57_15crossbeam_utils,unique,2
	.p2align	4
_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner14grow_amortizedCs5jdj61sQu57_15crossbeam_utils:
.Lfunc_begin2:
.seh_proc _RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner14grow_amortizedCs5jdj61sQu57_15crossbeam_utils
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$56, %rsp
	.seh_stackalloc 56
	.seh_endprologue
	movq	%rcx, %rsi
	incq	%rdx
	movq	(%rcx), %rax
	leaq	(%rax,%rax), %rcx
	cmpq	%rcx, %rdx
	cmovbeq	%rcx, %rdx
	cmpq	$5, %rdx
	movl	$4, %edi
	cmovaeq	%rdx, %rdi
	movq	8(%rsi), %r8
	leaq	32(%rsp), %rcx
	movq	%rax, %rdx
	movq	%rdi, %r9
	callq	_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCs5jdj61sQu57_15crossbeam_utils
	cmpb	$0, 32(%rsp)
	je	.LBB2_2
	movq	40(%rsp), %rax
	movq	48(%rsp), %rdx
	.seh_startepilogue
	addq	$56, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB2_2:
	movq	40(%rsp), %rax
	movq	%rax, 8(%rsi)
	movq	%rdi, (%rsi)
	movq	$-1, %rax
	.seh_startepilogue
	addq	$56, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end2:
	.seh_endproc

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
	.asciz	"S:\\GTOpen-research\\postflop-gpu-20261016\\runs\\D089-zero-scan-codegen\\build\\postflop-codegen.crossbeam_utils-f12feddf568a8de6.crossbeam_utils.3dd90c96c2eaf6b7-cgu.0.rcgu.o.rcgu.o"
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
	.short	0x6e
	.short	0x1605
	.long	0x0
	.asciz	"/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\alloc\\src\\lib.rs\\@\\alloc.b8a7db27d8b7bce8-cgu.0"
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
