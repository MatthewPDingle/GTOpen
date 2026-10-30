_RNvMs1_NtCsifJ2Jc9XidW_6solver5storeNtB5_5Store3u16:
.Lfunc_begin156:
.seh_proc _RNvMs1_NtCsifJ2Jc9XidW_6solver5storeNtB5_5Store3u16
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
	je	.LBB156_3
	xorl	%r14d, %r14d
.LBB156_2:
	movq	%r14, %rcx
	movq	%rbx, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.LBB156_3:
	movq	%r8, %rdi
	movq	%rdx, %r15
	testq	%rbx, %rbx
	je	.LBB156_4
	movl	$2, %r14d
	movl	$2, %edx
	movq	%rbx, %rcx
	callq	mi_zalloc_aligned
	testq	%rax, %rax
	je	.LBB156_2
	movq	%rax, %r12
	jmp	.LBB156_7
.LBB156_4:
	movl	$2, %r12d
.LBB156_7:
	leaq	(,%rdi,4), %rbx
	movq	%rdi, %rax
	shrq	$62, %rax
	setne	%al
	movabsq	$9223372036854775804, %rcx
	cmpq	%rcx, %rbx
	seta	%cl
	orb	%al, %cl
	je	.LBB156_9
	xorl	%r14d, %r14d
.LBB156_13:
.Ltmp8216:
	movq	%r12, -16(%rbp)
	movq	%r15, -24(%rbp)
	movq	%r14, %rcx
	movq	%rbx, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp8217:
	ud2
.LBB156_9:
	testq	%rbx, %rbx
	je	.LBB156_10
	movl	$4, %r14d
	movl	$4, %edx
	movq	%rbx, %rcx
	callq	mi_zalloc_aligned
	testq	%rax, %rax
	jne	.LBB156_11
	jmp	.LBB156_13
.LBB156_10:
	movl	$4, %eax
.LBB156_11:
	movq	%r12, 8(%rsi)
	movq	%r15, 16(%rsi)
	movq	%r12, 24(%rsi)
	movq	%rax, 32(%rsi)
	movq	%rdi, 40(%rsi)
	movq	%rax, 48(%rsi)
	movq	$2, (%rsi)
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
	.long	$cppxdata$_RNvMs1_NtCsifJ2Jc9XidW_6solver5storeNtB5_5Store3u16@IMGREL
	.section	.text,"xr",one_only,_RNvMs1_NtCsifJ2Jc9XidW_6solver5storeNtB5_5Store3u16,unique,158
	.seh_endproc
