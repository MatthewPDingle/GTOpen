_RNvMs1_NtCsifJ2Jc9XidW_6solver3cfrNtB5_6Solver12with_storage:
.Lfunc_begin145:
.seh_proc _RNvMs1_NtCsifJ2Jc9XidW_6solver3cfrNtB5_6Solver12with_storage
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%r15
	.seh_pushreg %r15
	pushq	%r14
	.seh_pushreg %r14
	pushq	%r13
	.seh_pushreg %r13
	pushq	%r12
	.seh_pushreg %r12
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$424, %rsp
	.seh_stackalloc 424
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	movq	$-2, 288(%rbp)
	movl	%r8d, %ebx
	movq	%rcx, %rsi
	movq	1088(%rdx), %r15
	movq	1144(%rdx), %r14
	movq	1152(%rdx), %rdi
	movq	%rdx, 216(%rbp)
	movq	%rdx, 88(%rbp)
	testb	%r8b, %r8b
	je	.LBB145_5
.Ltmp8128:
	leaq	224(%rbp), %rcx
	movq	%r14, %rdx
	movq	%r15, %r8
	callq	_RNvMs1_NtCsifJ2Jc9XidW_6solver5storeNtB5_5Store3i16
	nop
.Ltmp8129:
.Ltmp8130:
	leaq	96(%rbp), %rcx
	movq	%rdi, %rdx
	movq	%r15, %r8
	callq	_RNvMs1_NtCsifJ2Jc9XidW_6solver5storeNtB5_5Store3i16
	nop
.Ltmp8131:
	movq	272(%rbp), %rax
	movq	%rax, 16(%rbp)
	movups	224(%rbp), %xmm0
	movups	240(%rbp), %xmm1
	movups	256(%rbp), %xmm2
	movaps	%xmm2, (%rbp)
	movaps	%xmm1, -16(%rbp)
	movaps	%xmm0, -32(%rbp)
	movups	96(%rbp), %xmm0
	movups	112(%rbp), %xmm1
	movups	128(%rbp), %xmm2
	movups	%xmm0, 24(%rbp)
	movups	%xmm1, 40(%rbp)
	movups	%xmm2, 56(%rbp)
	movq	144(%rbp), %rax
	movq	%rax, 72(%rbp)
.Ltmp8132:
	leaq	-88(%rbp), %rcx
	movq	%r14, %rdx
	movq	%r15, %r8
	callq	_RNvMs1_NtCsifJ2Jc9XidW_6solver5storeNtB5_5Store3u16
	nop
.Ltmp8133:
.Ltmp8134:
	leaq	224(%rbp), %rcx
	movq	%rdi, %rdx
	movq	%r15, %r8
	callq	_RNvMs1_NtCsifJ2Jc9XidW_6solver5storeNtB5_5Store3u16
	nop
.Ltmp8135:
.LBB145_27:
	movq	-40(%rbp), %rax
	movq	%rax, 144(%rbp)
	movups	-88(%rbp), %xmm0
	movups	-72(%rbp), %xmm1
	movups	-56(%rbp), %xmm2
	movaps	%xmm2, 128(%rbp)
	movaps	%xmm1, 112(%rbp)
	movaps	%xmm0, 96(%rbp)
	movq	224(%rbp), %rax
	movq	232(%rbp), %rcx
	movq	240(%rbp), %rdx
	movq	248(%rbp), %r8
	movups	256(%rbp), %xmm0
	movq	%rax, 152(%rbp)
	movq	%rcx, 160(%rbp)
	movq	%rdx, 168(%rbp)
	movq	%r8, 176(%rbp)
	movups	%xmm0, 184(%rbp)
	movq	272(%rbp), %rax
	movq	%rax, 200(%rbp)
	movl	_tls_index(%rip), %eax
	movq	%gs:88, %rcx
	movq	(%rcx,%rax,8), %rax
	leaq	_RNvNCNKNvNvMNtNtCse0R8cuyqEa_3std4hash6randomNtBa_11RandomState3new4KEYS0s_023___RUST_STD_INTERNAL_VAL@SECREL32(%rax), %rdi
	cmpb	$1, _RNvNCNKNvNvMNtNtCse0R8cuyqEa_3std4hash6randomNtBa_11RandomState3new4KEYS0s_023___RUST_STD_INTERNAL_VAL@SECREL32+16(%rax)
	jne	.LBB145_41
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
.LBB145_42:
	leaq	1(%rcx), %rdx
	leaq	2(%rcx), %r8
	movq	%r8, (%rdi)
	movq	216(%rbp), %r8
	movq	%r8, 224(%rsi)
	movb	%bl, 340(%rsi)
	movaps	-32(%rbp), %xmm0
	movaps	-16(%rbp), %xmm1
	movaps	(%rbp), %xmm2
	movaps	16(%rbp), %xmm3
	movups	%xmm0, (%rsi)
	movups	%xmm1, 16(%rsi)
	movups	%xmm2, 32(%rsi)
	movups	%xmm3, 48(%rsi)
	movaps	32(%rbp), %xmm0
	movups	%xmm0, 64(%rsi)
	movaps	48(%rbp), %xmm0
	movups	%xmm0, 80(%rsi)
	movaps	64(%rbp), %xmm0
	movups	%xmm0, 96(%rsi)
	movaps	96(%rbp), %xmm0
	movaps	112(%rbp), %xmm1
	movaps	128(%rbp), %xmm2
	movaps	144(%rbp), %xmm3
	movups	%xmm0, 112(%rsi)
	movups	%xmm1, 128(%rsi)
	movups	%xmm2, 144(%rsi)
	movups	%xmm3, 160(%rsi)
	movaps	160(%rbp), %xmm0
	movups	%xmm0, 176(%rsi)
	movaps	176(%rbp), %xmm0
	movups	%xmm0, 192(%rsi)
	movaps	192(%rbp), %xmm0
	movups	%xmm0, 208(%rsi)
	movq	$0, 328(%rsi)
	movl	$0, 336(%rsi)
	movb	$0, 343(%rsi)
	movups	anon.ccb92d8c524d1431f7adfaf125cb7e9d.84(%rip), %xmm0
	movups	%xmm0, 232(%rsi)
	movups	anon.ccb92d8c524d1431f7adfaf125cb7e9d.84+16(%rip), %xmm1
	movups	%xmm1, 248(%rsi)
	movq	%rcx, 264(%rsi)
	movq	%rax, 272(%rsi)
	movups	%xmm1, 296(%rsi)
	movups	%xmm0, 280(%rsi)
	movq	%rdx, 312(%rsi)
	movq	%rax, 320(%rsi)
	movw	$1, 341(%rsi)
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$424, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r13
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
.LBB145_5:
	leaq	(,%r14,4), %r15
	movq	%r14, %rax
	shrq	$62, %rax
	setne	%al
	movabsq	$9223372036854775804, %r13
	cmpq	%r13, %r15
	seta	%cl
	orb	%al, %cl
	je	.LBB145_7
	xorl	%r12d, %r12d
.LBB145_13:
.Ltmp8126:
	movq	%r12, %rcx
	movq	%r15, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp8127:
	jmp	.LBB145_14
.LBB145_7:
	testq	%r15, %r15
	je	.LBB145_8
	movl	$4, %r12d
	movl	$4, %edx
	movq	%r15, %rcx
	callq	mi_zalloc_aligned
	testq	%rax, %rax
	jne	.LBB145_9
	jmp	.LBB145_13
.LBB145_8:
	movl	$4, %eax
.LBB145_9:
	movq	%rax, 232(%rbp)
	movq	%r14, 240(%rbp)
	movq	%rax, 248(%rbp)
	movq	$0, 224(%rbp)
	leaq	(,%rdi,4), %r12
	movq	%rdi, %rax
	shrq	$62, %rax
	setne	%al
	cmpq	%r13, %r12
	seta	%cl
	orb	%al, %cl
	je	.LBB145_18
	xorl	%r13d, %r13d
.LBB145_11:
.Ltmp8124:
	movq	%r13, %rcx
	movq	%r12, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp8125:
	jmp	.LBB145_14
.LBB145_18:
	movl	$4, %ecx
	movl	$4, %eax
	testq	%r12, %r12
	je	.LBB145_21
	movl	$4, %r13d
	movl	$4, %edx
	movq	%r12, %rcx
	callq	mi_zalloc_aligned
	testq	%rax, %rax
	je	.LBB145_11
	movl	$4, %ecx
.LBB145_21:
	movq	%rax, 104(%rbp)
	movq	%rdi, 112(%rbp)
	movq	%rax, 120(%rbp)
	movq	$0, 96(%rbp)
	movups	224(%rbp), %xmm0
	movups	240(%rbp), %xmm1
	movups	256(%rbp), %xmm2
	movaps	%xmm0, -32(%rbp)
	movaps	%xmm1, -16(%rbp)
	movaps	%xmm2, (%rbp)
	movq	272(%rbp), %rax
	movq	%rax, 16(%rbp)
	movups	128(%rbp), %xmm0
	movups	%xmm0, 56(%rbp)
	movq	144(%rbp), %rax
	movq	%rax, 72(%rbp)
	movq	96(%rbp), %rax
	movq	%rax, 24(%rbp)
	movq	104(%rbp), %rax
	movq	%rax, 32(%rbp)
	movups	112(%rbp), %xmm0
	movups	%xmm0, 40(%rbp)
	testq	%r14, %r14
	je	.LBB145_24
	movl	$4, %edx
	movq	%r15, %rcx
	callq	mi_zalloc_aligned
	testq	%rax, %rax
	je	.LBB145_36
	movq	%rax, %rcx
.LBB145_24:
	movq	%rcx, -80(%rbp)
	movq	%r14, -72(%rbp)
	movq	%rcx, -64(%rbp)
	movq	$0, -88(%rbp)
	testq	%r12, %r12
	je	.LBB145_25
	movl	$4, %edx
	movq	%r12, %rcx
	callq	mi_zalloc_aligned
	testq	%rax, %rax
	jne	.LBB145_26
.Ltmp8122:
	movl	$4, %ecx
	movq	%r12, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp8123:
	jmp	.LBB145_14
.LBB145_25:
	movl	$4, %eax
.LBB145_26:
	movq	%rax, 232(%rbp)
	movq	%rdi, 240(%rbp)
	movq	%rax, 248(%rbp)
	movq	$0, 224(%rbp)
	jmp	.LBB145_27
.LBB145_41:
	xorps	%xmm0, %xmm0
	movaps	%xmm0, 224(%rbp)
	leaq	224(%rbp), %rcx
	movl	$16, %edx
	callq	*__imp_ProcessPrng(%rip)
	movq	224(%rbp), %rcx
	movq	232(%rbp), %rax
	movq	%rax, 8(%rdi)
	movb	$1, 16(%rdi)
	jmp	.LBB145_42
.LBB145_36:
.Ltmp8120:
	movl	$4, %ecx
	movq	%r15, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp8121:
.LBB145_14:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvMs1_NtCsifJ2Jc9XidW_6solver3cfrNtB5_6Solver12with_storage@IMGREL
	.section	.text,"xr",one_only,_RNvMs1_NtCsifJ2Jc9XidW_6solver3cfrNtB5_6Solver12with_storage,unique,146
	.seh_endproc
