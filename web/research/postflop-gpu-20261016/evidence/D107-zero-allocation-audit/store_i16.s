_RNvMs1_NtCsifJ2Jc9XidW_6solver5storeNtB5_5Store3i16:
.Lfunc_begin155:
.seh_proc _RNvMs1_NtCsifJ2Jc9XidW_6solver5storeNtB5_5Store3i16
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%r15
	.seh_pushreg %r15
	pushq	%r14
	.seh_pushreg %r14
	pushq	%r12
	.seh_pushreg %r12
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$64, %rsp
	.seh_stackalloc 64
	leaq	64(%rsp), %rbp
	.seh_setframe %rbp, 64
	.seh_endprologue
	movq	$-2, -8(%rbp)
	movq	%rcx, %rsi
	leaq	(%rdx,%rdx), %rbx
	testq	%rdx, %rdx
	sets	%al
	movabsq	$9223372036854775806, %rcx
	cmpq	%rcx, %rbx
	seta	%cl
	orb	%al, %cl
	je	.LBB155_3
	xorl	%r14d, %r14d
.LBB155_2:
	movq	%r14, %rcx
	movq	%rbx, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.LBB155_3:
	movq	%r8, %rdi
	movq	%rdx, %r15
	testq	%rbx, %rbx
	je	.LBB155_4
	movl	$2, %r14d
	movl	$2, %edx
	movq	%rbx, %rcx
	callq	mi_zalloc_aligned
	testq	%rax, %rax
	je	.LBB155_2
	movq	%rax, %r12
	jmp	.LBB155_7
.LBB155_4:
	movl	$2, %r12d
.LBB155_7:
	leaq	(,%rdi,4), %rbx
	movq	%rdi, %rax
	shrq	$62, %rax
	setne	%al
	movabsq	$9223372036854775804, %rcx
	cmpq	%rcx, %rbx
	seta	%cl
	orb	%al, %cl
	je	.LBB155_9
	xorl	%r14d, %r14d
.LBB155_13:
.Ltmp8214:
	movq	%r12, -16(%rbp)
	movq	%r15, -24(%rbp)
	movq	%r14, %rcx
	movq	%rbx, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp8215:
	ud2
.LBB155_9:
	testq	%rbx, %rbx
	je	.LBB155_10
	movl	$4, %r14d
	movl	$4, %edx
	movq	%rbx, %rcx
	callq	mi_zalloc_aligned
	testq	%rax, %rax
	jne	.LBB155_11
	jmp	.LBB155_13
.LBB155_10:
	movl	$4, %eax
.LBB155_11:
	movq	%r12, 8(%rsi)
	movq	%r15, 16(%rsi)
	movq	%r12, 24(%rsi)
	movq	%rax, 32(%rsi)
	movq	%rdi, 40(%rsi)
	movq	%rax, 48(%rsi)
	movq	$1, (%rsi)
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.long	$cppxdata$_RNvMs1_NtCsifJ2Jc9XidW_6solver5storeNtB5_5Store3i16@IMGREL
	.section	.text,"xr",one_only,_RNvMs1_NtCsifJ2Jc9XidW_6solver5storeNtB5_5Store3i16,unique,157
	.seh_endproc
