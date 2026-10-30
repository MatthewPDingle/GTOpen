	.def	@feat.00;
	.scl	3;
	.type	0;
	.endef
	.globl	@feat.00
@feat.00 = 0
	.file	"prototype.1ab0bb7343479e38-cgu.0"
	.def	_RINvCs2i4to50FHNk_9prototype3addReEB2_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvCs2i4to50FHNk_9prototype3addReEB2_,unique,0
	.p2align	4
_RINvCs2i4to50FHNk_9prototype3addReEB2_:
.Lfunc_begin0:
.seh_proc _RINvCs2i4to50FHNk_9prototype3addReEB2_
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$104, %rsp
	.seh_stackalloc 104
	leaq	96(%rsp), %rbp
	.seh_setframe %rbp, 96
	.seh_endprologue
	movq	$-2, (%rbp)
	movq	%r9, %r14
	movq	%r8, %rdi
	movq	%rdx, %rbx
	movq	%rcx, %rsi
	xorl	%edx, %edx
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	movq	%r14, -8(%rbp)
	movq	%rax, -16(%rbp)
	je	.LBB0_1
	movq	%rax, %r15
	movq	%rax, %rcx
	movq	%rbx, %rdx
	movq	%rdi, %r8
	callq	memcpy
	movq	%rdi, -64(%rbp)
	movq	%r15, -56(%rbp)
	movq	%rdi, -48(%rbp)
	movq	16(%r14), %rax
	movq	%rax, -24(%rbp)
	movups	(%r14), %xmm0
	movups	%xmm0, -40(%rbp)
	movq	16(%rsi), %rdi
	cmpq	(%rsi), %rdi
	jne	.LBB0_8
.Ltmp2:
	movq	%rsi, %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	nop
.Ltmp3:
.LBB0_8:
	movq	8(%rsi), %rax
	leaq	(%rdi,%rdi,2), %rcx
	shlq	$4, %rcx
	movups	-64(%rbp), %xmm0
	movups	-48(%rbp), %xmm1
	movups	-32(%rbp), %xmm2
	movups	%xmm2, 32(%rax,%rcx)
	movups	%xmm1, 16(%rax,%rcx)
	movups	%xmm0, (%rax,%rcx)
	incq	%rdi
	movq	%rdi, 16(%rsi)
	.seh_startepilogue
	addq	$104, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
.LBB0_1:
.Ltmp0:
	movl	$1, %ecx
	movq	%rdi, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp1:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RINvCs2i4to50FHNk_9prototype3addReEB2_@IMGREL
	.section	.text,"xr",one_only,_RINvCs2i4to50FHNk_9prototype3addReEB2_,unique,0
	.seh_endproc
	.def	"?dtor$3@?0?_RINvCs2i4to50FHNk_9prototype3addReEB2_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$3@?0?_RINvCs2i4to50FHNk_9prototype3addReEB2_@4HA":
.seh_proc "?dtor$3@?0?_RINvCs2i4to50FHNk_9prototype3addReEB2_@4HA"
.LBB0_3:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	96(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, -16(%rbp)
	jne	.LBB0_5
	movq	-8(%rbp), %rax
	cmpq	$0, (%rax)
	je	.LBB0_5
	movq	-8(%rbp), %rax
	movq	8(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	nop
.LBB0_5:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvCs2i4to50FHNk_9prototype3addReEB2_,unique,0
	.seh_endproc
	.def	"?dtor$10@?0?_RINvCs2i4to50FHNk_9prototype3addReEB2_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$10@?0?_RINvCs2i4to50FHNk_9prototype3addReEB2_@4HA":
.seh_proc "?dtor$10@?0?_RINvCs2i4to50FHNk_9prototype3addReEB2_@4HA"
.LBB0_10:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	96(%rdx), %rbp
	.seh_endprologue
	leaq	-64(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs2i4to50FHNk_9prototype4CaseEBD_
	nop
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end0:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvCs2i4to50FHNk_9prototype3addReEB2_,unique,0
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvCs2i4to50FHNk_9prototype3addReEB2_,unique,0
	.p2align	2, 0x0
$cppxdata$_RINvCs2i4to50FHNk_9prototype3addReEB2_:
	.long	429065506
	.long	2
	.long	$stateUnwindMap$_RINvCs2i4to50FHNk_9prototype3addReEB2_@IMGREL
	.long	0
	.long	0
	.long	4
	.long	$ip2state$_RINvCs2i4to50FHNk_9prototype3addReEB2_@IMGREL
	.long	96
	.long	0
	.long	1
$stateUnwindMap$_RINvCs2i4to50FHNk_9prototype3addReEB2_:
	.long	-1
	.long	"?dtor$3@?0?_RINvCs2i4to50FHNk_9prototype3addReEB2_@4HA"@IMGREL
	.long	0
	.long	"?dtor$10@?0?_RINvCs2i4to50FHNk_9prototype3addReEB2_@4HA"@IMGREL
$ip2state$_RINvCs2i4to50FHNk_9prototype3addReEB2_:
	.long	.Lfunc_begin0@IMGREL
	.long	-1
	.long	.Ltmp2@IMGREL
	.long	1
	.long	.Ltmp0@IMGREL
	.long	0
	.long	.Ltmp1@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvCs2i4to50FHNk_9prototype3addReEB2_,unique,0

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecIBC_fEEECs2i4to50FHNk_9prototype;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecIBC_fEEECs2i4to50FHNk_9prototype,unique,1
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecIBC_fEEECs2i4to50FHNk_9prototype:
.Lfunc_begin1:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecIBC_fEEECs2i4to50FHNk_9prototype
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
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	%rcx, %rdi
	movq	8(%rcx), %rsi
	movq	16(%rcx), %r14
	testq	%r14, %r14
	je	.LBB1_5
	leaq	8(%rsi), %r15
	movq	__imp_GetProcessHeap(%rip), %r12
	movq	__imp_HeapFree(%rip), %r13
	jmp	.LBB1_2
	.p2align	4
.LBB1_4:
	addq	$24, %r15
	decq	%r14
	je	.LBB1_5
.LBB1_2:
	cmpq	$0, -8(%r15)
	je	.LBB1_4
	movq	(%r15), %rbx
	callq	*%r12
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rbx, %r8
	callq	*%r13
	jmp	.LBB1_4
.LBB1_5:
	cmpq	$0, (%rdi)
	je	.LBB1_6
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r13
	popq	%r14
	popq	%r15
	.seh_endepilogue
	rex64 jmpq	*__imp_HeapFree(%rip)
.LBB1_6:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r13
	popq	%r14
	popq	%r15
	.seh_endepilogue
	retq
.Lfunc_end1:
	.seh_endproc

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs2i4to50FHNk_9prototype4CaseEBD_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs2i4to50FHNk_9prototype4CaseEBD_,unique,2
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs2i4to50FHNk_9prototype4CaseEBD_:
.Lfunc_begin2:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs2i4to50FHNk_9prototype4CaseEBD_
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	%rcx, %rsi
	cmpq	$0, (%rcx)
	je	.LBB2_2
	movq	8(%rsi), %rdi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rdi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB2_2:
	cmpq	$0, 24(%rsi)
	je	.LBB2_3
	movq	32(%rsi), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	rex64 jmpq	*__imp_HeapFree(%rip)
.LBB2_3:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end2:
	.seh_endproc

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCse0R8cuyqEa_3std3env4ArgsECs2i4to50FHNk_9prototype;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCse0R8cuyqEa_3std3env4ArgsECs2i4to50FHNk_9prototype,unique,3
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCse0R8cuyqEa_3std3env4ArgsECs2i4to50FHNk_9prototype:
.Lfunc_begin3:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCse0R8cuyqEa_3std3env4ArgsECs2i4to50FHNk_9prototype
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
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	%rcx, %rsi
	movq	8(%rcx), %rbx
	movq	24(%rcx), %r14
	subq	%rbx, %r14
	je	.LBB3_5
	shrq	$5, %r14
	addq	$8, %rbx
	movq	__imp_GetProcessHeap(%rip), %r15
	movq	__imp_HeapFree(%rip), %r12
	jmp	.LBB3_2
	.p2align	4
.LBB3_4:
	addq	$32, %rbx
	decq	%r14
	je	.LBB3_5
.LBB3_2:
	cmpq	$0, -8(%rbx)
	je	.LBB3_4
	movq	(%rbx), %rdi
	callq	*%r15
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rdi, %r8
	callq	*%r12
	jmp	.LBB3_4
.LBB3_5:
	cmpq	$0, 16(%rsi)
	je	.LBB3_6
	movq	(%rsi), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r14
	popq	%r15
	.seh_endepilogue
	rex64 jmpq	*__imp_HeapFree(%rip)
.LBB3_6:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r14
	popq	%r15
	.seh_endepilogue
	retq
.Lfunc_end3:
	.seh_endproc

	.def	_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedINtNtCsfQUUnEvlYZE_5alloc3vec3VecmEBM_ECs2i4to50FHNk_9prototype;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedINtNtCsfQUUnEvlYZE_5alloc3vec3VecmEBM_ECs2i4to50FHNk_9prototype,unique,4
_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedINtNtCsfQUUnEvlYZE_5alloc3vec3VecmEBM_ECs2i4to50FHNk_9prototype:
.Lfunc_begin4:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedINtNtCsfQUUnEvlYZE_5alloc3vec3VecmEBM_ECs2i4to50FHNk_9prototype
	subq	$88, %rsp
	.seh_stackalloc 88
	.seh_endprologue
	leaq	72(%rsp), %rax
	movq	%rcx, (%rax)
	leaq	80(%rsp), %r9
	movq	%rdx, (%r9)
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.34(%rip), %rcx
	movq	%rcx, 56(%rsp)
	movq	%r8, 48(%rsp)
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.33(%rip), %rcx
	movq	%rcx, 40(%rsp)
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.3(%rip), %r8
	movq	%r8, 32(%rsp)
	xorl	%ecx, %ecx
	movq	%rax, %rdx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking19assert_failed_inner
	ud2
.Lfunc_end4:
	.seh_endproc

	.def	_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedINtNtCsfQUUnEvlYZE_5alloc3vec3VecsEBM_ECs2i4to50FHNk_9prototype;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedINtNtCsfQUUnEvlYZE_5alloc3vec3VecsEBM_ECs2i4to50FHNk_9prototype,unique,5
_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedINtNtCsfQUUnEvlYZE_5alloc3vec3VecsEBM_ECs2i4to50FHNk_9prototype:
.Lfunc_begin5:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedINtNtCsfQUUnEvlYZE_5alloc3vec3VecsEBM_ECs2i4to50FHNk_9prototype
	subq	$88, %rsp
	.seh_stackalloc 88
	.seh_endprologue
	leaq	72(%rsp), %rax
	movq	%rcx, (%rax)
	leaq	80(%rsp), %r9
	movq	%rdx, (%r9)
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.30(%rip), %rcx
	movq	%rcx, 56(%rsp)
	movq	%r8, 48(%rsp)
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.29(%rip), %rcx
	movq	%rcx, 40(%rsp)
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.4(%rip), %r8
	movq	%r8, 32(%rsp)
	xorl	%ecx, %ecx
	movq	%rax, %rdx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking19assert_failed_inner
	ud2
.Lfunc_end5:
	.seh_endproc

	.def	_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedINtNtCsfQUUnEvlYZE_5alloc3vec3VectEBM_ECs2i4to50FHNk_9prototype;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedINtNtCsfQUUnEvlYZE_5alloc3vec3VectEBM_ECs2i4to50FHNk_9prototype,unique,6
_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedINtNtCsfQUUnEvlYZE_5alloc3vec3VectEBM_ECs2i4to50FHNk_9prototype:
.Lfunc_begin6:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedINtNtCsfQUUnEvlYZE_5alloc3vec3VectEBM_ECs2i4to50FHNk_9prototype
	subq	$88, %rsp
	.seh_stackalloc 88
	.seh_endprologue
	leaq	72(%rsp), %rax
	movq	%rcx, (%rax)
	leaq	80(%rsp), %r9
	movq	%rdx, (%r9)
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.32(%rip), %rcx
	movq	%rcx, 56(%rsp)
	movq	%r8, 48(%rsp)
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.31(%rip), %rcx
	movq	%rcx, 40(%rsp)
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.5(%rip), %r8
	movq	%r8, 32(%rsp)
	xorl	%ecx, %ecx
	movq	%rax, %rdx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking19assert_failed_inner
	ud2
.Lfunc_end6:
	.seh_endproc

	.def	_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedmmECs2i4to50FHNk_9prototype;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedmmECs2i4to50FHNk_9prototype,unique,7
_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedmmECs2i4to50FHNk_9prototype:
.Lfunc_begin7:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedmmECs2i4to50FHNk_9prototype
	subq	$88, %rsp
	.seh_stackalloc 88
	.seh_endprologue
	movq	128(%rsp), %r11
	leaq	72(%rsp), %rax
	movq	%rcx, (%rax)
	leaq	80(%rsp), %r10
	movq	%rdx, (%r10)
	movq	%r11, 56(%rsp)
	movq	%r9, 48(%rsp)
	movq	%r8, 40(%rsp)
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.0(%rip), %r8
	movq	%r8, 32(%rsp)
	xorl	%ecx, %ecx
	movq	%rax, %rdx
	movq	%r10, %r9
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking19assert_failed_inner
	ud2
.Lfunc_end7:
	.seh_endproc

	.def	_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedttECs2i4to50FHNk_9prototype;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedttECs2i4to50FHNk_9prototype,unique,8
_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedttECs2i4to50FHNk_9prototype:
.Lfunc_begin8:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedttECs2i4to50FHNk_9prototype
	subq	$88, %rsp
	.seh_stackalloc 88
	.seh_endprologue
	leaq	72(%rsp), %rax
	movq	%rcx, (%rax)
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.35(%rip), %rcx
	leaq	80(%rsp), %r10
	movq	%rcx, (%r10)
	movq	%r9, 56(%rsp)
	movq	%r8, 48(%rsp)
	movq	%rdx, 40(%rsp)
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.2(%rip), %r8
	movq	%r8, 32(%rsp)
	xorl	%ecx, %ecx
	movq	%rax, %rdx
	movq	%r10, %r9
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking19assert_failed_inner
	ud2
.Lfunc_end8:
	.seh_endproc

	.def	_RINvNtNtCse0R8cuyqEa_3std3sys9backtrace28___rust_begin_short_backtraceFEuuECs2i4to50FHNk_9prototype;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtNtCse0R8cuyqEa_3std3sys9backtrace28___rust_begin_short_backtraceFEuuECs2i4to50FHNk_9prototype,unique,9
	.p2align	4
_RINvNtNtCse0R8cuyqEa_3std3sys9backtrace28___rust_begin_short_backtraceFEuuECs2i4to50FHNk_9prototype:
.Lfunc_begin9:
.seh_proc _RINvNtNtCse0R8cuyqEa_3std3sys9backtrace28___rust_begin_short_backtraceFEuuECs2i4to50FHNk_9prototype
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	callq	*%rcx
	nop
	#APP
	#NO_APP
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end9:
	.seh_endproc

	.def	_RNCINvNtCse0R8cuyqEa_3std2rt10lang_startuE0Cs2i4to50FHNk_9prototype;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvNtCse0R8cuyqEa_3std2rt10lang_startuE0Cs2i4to50FHNk_9prototype,unique,10
	.p2align	4
_RNCINvNtCse0R8cuyqEa_3std2rt10lang_startuE0Cs2i4to50FHNk_9prototype:
.Lfunc_begin10:
.seh_proc _RNCINvNtCse0R8cuyqEa_3std2rt10lang_startuE0Cs2i4to50FHNk_9prototype
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rcx
	callq	_RINvNtNtCse0R8cuyqEa_3std3sys9backtrace28___rust_begin_short_backtraceFEuuECs2i4to50FHNk_9prototype
	xorl	%eax, %eax
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end10:
	.seh_endproc

	.def	_RNSNvYNCINvNtCse0R8cuyqEa_3std2rt10lang_startuE0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableCs2i4to50FHNk_9prototype;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvNtCse0R8cuyqEa_3std2rt10lang_startuE0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableCs2i4to50FHNk_9prototype,unique,11
	.p2align	4
_RNSNvYNCINvNtCse0R8cuyqEa_3std2rt10lang_startuE0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableCs2i4to50FHNk_9prototype:
.Lfunc_begin11:
.seh_proc _RNSNvYNCINvNtCse0R8cuyqEa_3std2rt10lang_startuE0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableCs2i4to50FHNk_9prototype
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rcx
	callq	_RINvNtNtCse0R8cuyqEa_3std3sys9backtrace28___rust_begin_short_backtraceFEuuECs2i4to50FHNk_9prototype
	xorl	%eax, %eax
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end11:
	.seh_endproc

	.def	_RNvCs2i4to50FHNk_9prototype4main;
	.scl	2;
	.type	32;
	.endef
	.globl	__xmm@6572756c6961662d7463656a6e692d2d
	.section	.rdata,"dr",discard,__xmm@6572756c6961662d7463656a6e692d2d
	.p2align	4, 0x0
__xmm@6572756c6961662d7463656a6e692d2d:
	.byte	45
	.byte	45
	.byte	105
	.byte	110
	.byte	106
	.byte	101
	.byte	99
	.byte	116
	.byte	45
	.byte	102
	.byte	97
	.byte	105
	.byte	108
	.byte	117
	.byte	114
	.byte	101
	.globl	__xmm@80000001000000018000000000000000
	.section	.rdata,"dr",discard,__xmm@80000001000000018000000000000000
	.p2align	4, 0x0
__xmm@80000001000000018000000000000000:
	.long	0
	.long	2147483648
	.long	1
	.long	2147483649
	.globl	__xmm@8080000000800000807fffff007fffff
	.section	.rdata,"dr",discard,__xmm@8080000000800000807fffff007fffff
	.p2align	4, 0x0
__xmm@8080000000800000807fffff007fffff:
	.long	8388607
	.long	2155872255
	.long	8388608
	.long	2155872256
	.globl	__xmm@ff7fffff7f7fffffbf8000003f800000
	.section	.rdata,"dr",discard,__xmm@ff7fffff7f7fffffbf8000003f800000
	.p2align	4, 0x0
__xmm@ff7fffff7f7fffffbf8000003f800000:
	.long	1065353216
	.long	3212836864
	.long	2139095039
	.long	4286578687
	.globl	__xmm@ffc001237fc00000ff8000007f800000
	.section	.rdata,"dr",discard,__xmm@ffc001237fc00000ff8000007f800000
	.p2align	4, 0x0
__xmm@ffc001237fc00000ff8000007f800000:
	.long	2139095040
	.long	4286578688
	.long	2143289344
	.long	4290773283
	.globl	__xmm@00000000000000030000000000000002
	.section	.rdata,"dr",discard,__xmm@00000000000000030000000000000002
	.p2align	4, 0x0
__xmm@00000000000000030000000000000002:
	.quad	2
	.quad	3
	.globl	__xmm@00000000000000010000000000000000
	.section	.rdata,"dr",discard,__xmm@00000000000000010000000000000000
	.p2align	4, 0x0
__xmm@00000000000000010000000000000000:
	.byte	0
	.byte	0
	.byte	0
	.byte	0
	.byte	0
	.byte	0
	.byte	0
	.byte	0
	.byte	1
	.byte	0
	.byte	0
	.byte	0
	.byte	0
	.byte	0
	.byte	0
	.byte	0
	.globl	__xmm@00000000000000010000000000000001
	.section	.rdata,"dr",discard,__xmm@00000000000000010000000000000001
	.p2align	4, 0x0
__xmm@00000000000000010000000000000001:
	.quad	1
	.quad	1
	.globl	__xmm@80000000800000008000000080000000
	.section	.rdata,"dr",discard,__xmm@80000000800000008000000080000000
	.p2align	4, 0x0
__xmm@80000000800000008000000080000000:
	.long	0x80000000
	.long	0x80000000
	.long	0x80000000
	.long	0x80000000
	.globl	__xmm@00000000000000080000000000000008
	.section	.rdata,"dr",discard,__xmm@00000000000000080000000000000008
	.p2align	4, 0x0
__xmm@00000000000000080000000000000008:
	.quad	8
	.quad	8
	.globl	__real@80000000
	.section	.rdata,"dr",discard,__real@80000000
	.p2align	2, 0x0
__real@80000000:
	.long	0x80000000
	.globl	__real@bf800000
	.section	.rdata,"dr",discard,__real@bf800000
	.p2align	2, 0x0
__real@bf800000:
	.long	0xbf800000
	.globl	__xmm@00000003000000020000000100000000
	.section	.rdata,"dr",discard,__xmm@00000003000000020000000100000000
	.p2align	4, 0x0
__xmm@00000003000000020000000100000000:
	.long	0
	.long	1
	.long	2
	.long	3
	.globl	__xmm@00000081000000800000007f0000007e
	.section	.rdata,"dr",discard,__xmm@00000081000000800000007f0000007e
	.p2align	4, 0x0
__xmm@00000081000000800000007f0000007e:
	.long	126
	.long	127
	.long	128
	.long	129
	.globl	__xmm@0000fffd00007ffd00003fff000003ff
	.section	.rdata,"dr",discard,__xmm@0000fffd00007ffd00003fff000003ff
	.p2align	4, 0x0
__xmm@0000fffd00007ffd00003fff000003ff:
	.long	1023
	.long	16383
	.long	32765
	.long	65533
	.globl	__real@3f000000
	.section	.rdata,"dr",discard,__real@3f000000
	.p2align	2, 0x0
__real@3f000000:
	.long	0x3f000000
	.globl	__xmm@00800000007fffff0000000200000001
	.section	.rdata,"dr",discard,__xmm@00800000007fffff0000000200000001
	.p2align	4, 0x0
__xmm@00800000007fffff0000000200000001:
	.long	1
	.long	2
	.long	8388607
	.long	8388608
	.globl	__xmm@0000000000000000bf0000003f000000
	.section	.rdata,"dr",discard,__xmm@0000000000000000bf0000003f000000
	.p2align	4, 0x0
__xmm@0000000000000000bf0000003f000000:
	.long	0x3f000000
	.long	0xbf000000
	.zero	4
	.zero	4
	.globl	__xmm@00000000000000008000000000000000
	.section	.rdata,"dr",discard,__xmm@00000000000000008000000000000000
	.p2align	4, 0x0
__xmm@00000000000000008000000000000000:
	.long	0x00000000
	.long	0x80000000
	.zero	4
	.zero	4
	.globl	__xmm@0000000000000000ff8000017fc00123
	.section	.rdata,"dr",discard,__xmm@0000000000000000ff8000017fc00123
	.p2align	4, 0x0
__xmm@0000000000000000ff8000017fc00123:
	.long	0x7fc00123
	.long	0xff800001
	.zero	4
	.zero	4
	.globl	__xmm@8080000000800000ff7fffff7f7fffff
	.section	.rdata,"dr",discard,__xmm@8080000000800000ff7fffff7f7fffff
	.p2align	4, 0x0
__xmm@8080000000800000ff7fffff7f7fffff:
	.long	0x7f7fffff
	.long	0xff7fffff
	.long	0x00800000
	.long	0x80800000
	.globl	__xmm@bf8000003f8000008000000100000001
	.section	.rdata,"dr",discard,__xmm@bf8000003f8000008000000100000001
	.p2align	4, 0x0
__xmm@bf8000003f8000008000000100000001:
	.long	0x00000001
	.long	0x80000001
	.long	0x3f800000
	.long	0xbf800000
	.globl	__real@3d000000
	.section	.rdata,"dr",discard,__real@3d000000
	.p2align	2, 0x0
__real@3d000000:
	.long	0x3d000000
	.globl	__xmm@ff7fffff7f7fffff00800000007fffff
	.section	.rdata,"dr",discard,__xmm@ff7fffff7f7fffff00800000007fffff
	.p2align	4, 0x0
__xmm@ff7fffff7f7fffff00800000007fffff:
	.long	8388607
	.long	8388608
	.long	2139095039
	.long	4286578687
	.globl	__xmm@7f8000017fc01234ff8000007f800000
	.section	.rdata,"dr",discard,__xmm@7f8000017fc01234ff8000007f800000
	.p2align	4, 0x0
__xmm@7f8000017fc01234ff8000007f800000:
	.long	2139095040
	.long	4286578688
	.long	2143294004
	.long	2139095041
	.globl	__xmm@a55aa55aa55aa55aa55aa55aa55aa55a
	.section	.rdata,"dr",discard,__xmm@a55aa55aa55aa55aa55aa55aa55aa55a
	.p2align	4, 0x0
__xmm@a55aa55aa55aa55aa55aa55aa55aa55a:
	.short	42330
	.short	42330
	.short	42330
	.short	42330
	.short	42330
	.short	42330
	.short	42330
	.short	42330
	.globl	__real@3c800000
	.section	.rdata,"dr",discard,__real@3c800000
	.p2align	2, 0x0
__real@3c800000:
	.long	0x3c800000
	.globl	__xmm@7fffffff7fffffff7fffffff7fffffff
	.section	.rdata,"dr",discard,__xmm@7fffffff7fffffff7fffffff7fffffff
	.p2align	4, 0x0
__xmm@7fffffff7fffffff7fffffff7fffffff:
	.long	0x7fffffff
	.long	0x7fffffff
	.long	0x7fffffff
	.long	0x7fffffff
	.globl	__xmm@daa66d2c7ddf743f3c6ef372fe94f82a
	.section	.rdata,"dr",discard,__xmm@daa66d2c7ddf743f3c6ef372fe94f82a
	.p2align	4, 0x0
__xmm@daa66d2c7ddf743f3c6ef372fe94f82a:
	.quad	4354685564936845354
	.quad	-2691343689449507777
	.globl	__xmm@9e3779b97f4a7c150000000000000000
	.section	.rdata,"dr",discard,__xmm@9e3779b97f4a7c150000000000000000
	.p2align	4, 0x0
__xmm@9e3779b97f4a7c150000000000000000:
	.byte	0
	.byte	0
	.byte	0
	.byte	0
	.byte	0
	.byte	0
	.byte	0
	.byte	0
	.byte	21
	.byte	124
	.byte	74
	.byte	127
	.byte	185
	.byte	121
	.byte	55
	.byte	158
	.globl	__xmm@9e3779b97f4a7c159e3779b97f4a7c15
	.section	.rdata,"dr",discard,__xmm@9e3779b97f4a7c159e3779b97f4a7c15
	.p2align	4, 0x0
__xmm@9e3779b97f4a7c159e3779b97f4a7c15:
	.quad	-7046029254386353131
	.quad	-7046029254386353131
	.globl	__xmm@00000000bf58476d00000000bf58476d
	.section	.rdata,"dr",discard,__xmm@00000000bf58476d00000000bf58476d
	.p2align	4, 0x0
__xmm@00000000bf58476d00000000bf58476d:
	.quad	3210233709
	.quad	3210233709
	.globl	__xmm@bf58476d1ce4e5b9bf58476d1ce4e5b9
	.section	.rdata,"dr",discard,__xmm@bf58476d1ce4e5b9bf58476d1ce4e5b9
	.p2align	4, 0x0
__xmm@bf58476d1ce4e5b9bf58476d1ce4e5b9:
	.quad	-4658895280553007687
	.quad	-4658895280553007687
	.globl	__xmm@0000000094d049bb0000000094d049bb
	.section	.rdata,"dr",discard,__xmm@0000000094d049bb0000000094d049bb
	.p2align	4, 0x0
__xmm@0000000094d049bb0000000094d049bb:
	.quad	2496678331
	.quad	2496678331
	.globl	__xmm@94d049bb133111eb94d049bb133111eb
	.section	.rdata,"dr",discard,__xmm@94d049bb133111eb94d049bb133111eb
	.p2align	4, 0x0
__xmm@94d049bb133111eb94d049bb133111eb:
	.quad	-7723592293110705685
	.quad	-7723592293110705685
	.globl	__xmm@78dde6e5fd29f05478dde6e5fd29f054
	.section	.rdata,"dr",discard,__xmm@78dde6e5fd29f05478dde6e5fd29f054
	.p2align	4, 0x0
__xmm@78dde6e5fd29f05478dde6e5fd29f054:
	.quad	8709371129873690708
	.quad	8709371129873690708
	.globl	__real@ba800000
	.section	.rdata,"dr",discard,__real@ba800000
	.p2align	2, 0x0
__real@ba800000:
	.long	0xba800000
	.globl	__real@3a800000
	.section	.rdata,"dr",discard,__real@3a800000
	.p2align	2, 0x0
__real@3a800000:
	.long	0x3a800000
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.globl	_RNvCs2i4to50FHNk_9prototype4main
	.p2align	4
_RNvCs2i4to50FHNk_9prototype4main:
.Lfunc_begin12:
.seh_proc _RNvCs2i4to50FHNk_9prototype4main
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
	subq	$1016, %rsp
	.seh_stackalloc 1016
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	movdqa	%xmm13, 864(%rbp)
	.seh_savexmm %xmm13, 992
	movdqa	%xmm12, 848(%rbp)
	.seh_savexmm %xmm12, 976
	movdqa	%xmm11, 832(%rbp)
	.seh_savexmm %xmm11, 960
	movdqa	%xmm10, 816(%rbp)
	.seh_savexmm %xmm10, 944
	movdqa	%xmm9, 800(%rbp)
	.seh_savexmm %xmm9, 928
	movdqa	%xmm8, 784(%rbp)
	.seh_savexmm %xmm8, 912
	movaps	%xmm7, 768(%rbp)
	.seh_savexmm %xmm7, 896
	movaps	%xmm6, 752(%rbp)
	.seh_savexmm %xmm6, 880
	.seh_endprologue
	movq	$-2, 744(%rbp)
	leaq	176(%rbp), %rsi
	movq	%rsi, %rcx
	callq	_RNvNtCse0R8cuyqEa_3std3env7args_os
	leaq	480(%rbp), %rdi
	movdqa	__xmm@6572756c6961662d7463656a6e692d2d(%rip), %xmm6
	movq	__imp_GetProcessHeap(%rip), %r15
	movq	__imp_HeapFree(%rip), %r12
	jmp	.LBB12_1
	.p2align	4
.LBB12_8:
	testb	%r14b, %r14b
	jne	.LBB12_9
.LBB12_1:
.Ltmp4:
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	callq	_RNvXsc_NtCse0R8cuyqEa_3std3envNtB5_4ArgsNtNtNtNtCs8xEFJqa6dYS_4core4iter6traits8iterator8Iterator4next
	nop
.Ltmp5:
	movq	480(%rbp), %r13
	cmpq	$-1, %r13
	je	.LBB12_9
	movq	488(%rbp), %rbx
	cmpq	$16, 496(%rbp)
	jne	.LBB12_4
	movdqu	(%rbx), %xmm0
	pcmpeqb	%xmm6, %xmm0
	pmovmskb	%xmm0, %eax
	cmpl	$65535, %eax
	sete	%r14b
	testq	%r13, %r13
	jne	.LBB12_7
	jmp	.LBB12_8
	.p2align	4
.LBB12_4:
	xorl	%r14d, %r14d
	testq	%r13, %r13
	je	.LBB12_8
.LBB12_7:
	callq	*%r15
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rbx, %r8
	callq	*%r12
	jmp	.LBB12_8
.LBB12_9:
	movq	184(%rbp), %rdi
	movq	200(%rbp), %rbx
	subq	%rdi, %rbx
	je	.LBB12_14
	shrq	$5, %rbx
	addq	$8, %rdi
	jmp	.LBB12_11
	.p2align	4
.LBB12_13:
	addq	$32, %rdi
	decq	%rbx
	je	.LBB12_14
.LBB12_11:
	cmpq	$0, -8(%rdi)
	je	.LBB12_13
	movq	(%rdi), %rsi
	callq	*%r15
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*%r12
	jmp	.LBB12_13
.LBB12_14:
	movq	%r13, 168(%rbp)
	cmpq	$0, 192(%rbp)
	je	.LBB12_16
	movq	176(%rbp), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_16:
	movq	$0, 648(%rbp)
	movq	$8, 656(%rbp)
	movq	$0, 664(%rbp)
	movaps	__xmm@80000001000000018000000000000000(%rip), %xmm7
	movaps	%xmm7, 176(%rbp)
	movaps	__xmm@8080000000800000807fffff007fffff(%rip), %xmm0
	movaps	%xmm0, 192(%rbp)
	movaps	__xmm@ff7fffff7f7fffffbf8000003f800000(%rip), %xmm0
	movaps	%xmm0, 208(%rbp)
	movdqa	__xmm@ffc001237fc00000ff8000007f800000(%rip), %xmm0
	movdqa	%xmm0, 224(%rbp)
	movabsq	$-36028790584901631, %rax
	movq	%rax, 240(%rbp)
	movq	$0, 480(%rbp)
	movq	$4, 488(%rbp)
	movq	$0, 496(%rbp)
.Ltmp6:
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.11(%rip), %rdx
	leaq	648(%rbp), %rcx
	leaq	480(%rbp), %r9
	movl	$5, %r8d
	callq	_RINvCs2i4to50FHNk_9prototype3addReEB2_
	nop
.Ltmp7:
	xorl	%r13d, %r13d
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.12(%rip), %rsi
	leaq	480(%rbp), %rdi
	leaq	400(%rbp), %rbx
	jmp	.LBB12_18
	.p2align	4
.LBB12_42:
	addq	$4, %r13
	movq	656(%rbp), %rax
	leaq	(%r12,%r12,2), %rcx
	shlq	$4, %rcx
	movdqu	480(%rbp), %xmm0
	movdqu	496(%rbp), %xmm1
	movdqu	512(%rbp), %xmm2
	movdqu	%xmm2, 32(%rax,%rcx)
	movdqu	%xmm1, 16(%rax,%rcx)
	movdqu	%xmm0, (%rax,%rcx)
	incq	%r12
	movq	%r12, 664(%rbp)
.LBB12_18:
	cmpq	$72, %r13
	je	.LBB12_19
	movl	176(%rbp,%r13), %eax
	movl	%eax, 456(%rbp)
	leaq	456(%rbp), %rax
	movq	%rax, 400(%rbp)
	leaq	_RNvXsu_NtNtCs8xEFJqa6dYS_4core3fmt3nummNtB7_8LowerHex3fmt(%rip), %rax
	movq	%rax, 408(%rbp)
.Ltmp8:
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	movq	%rbx, %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp9:
	movq	480(%rbp), %r14
	movq	488(%rbp), %r15
	movq	496(%rbp), %r12
	movl	$4, %r8d
	xorl	%edx, %edx
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	movq	%r15, 696(%rbp)
	movq	%r14, 712(%rbp)
	movq	%rax, 736(%rbp)
	je	.LBB12_38
	movss	456(%rbp), %xmm0
	movss	%xmm0, (%rax)
	movq	%r14, 480(%rbp)
	movq	%r15, 488(%rbp)
	movq	%r12, 496(%rbp)
	movq	$1, 504(%rbp)
	movq	%rax, 512(%rbp)
	movq	$1, 520(%rbp)
	movq	664(%rbp), %r12
	cmpq	648(%rbp), %r12
	jne	.LBB12_42
.Ltmp10:
	leaq	648(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	nop
.Ltmp11:
	jmp	.LBB12_42
.LBB12_19:
	movq	$0, 728(%rbp)
	movabsq	$-9223231297218904063, %r14
	movdqa	__xmm@80000000800000008000000080000000(%rip), %xmm6
	movd	__real@80000000(%rip), %xmm8
	movdqa	__xmm@00000000000000030000000000000002(%rip), %xmm9
	movdqa	__xmm@00000000000000010000000000000000(%rip), %xmm10
	movdqa	__xmm@00000000000000010000000000000001(%rip), %xmm11
	pxor	%xmm12, %xmm12
	movdqa	__xmm@00000000000000080000000000000008(%rip), %xmm13
	xorl	%esi, %esi
	cmpq	$232, %rsi
	je	.LBB12_21
.LBB12_48:
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.13(%rip), %rax
	movq	%rsi, 712(%rbp)
	movq	(%rsi,%rax), %rax
	movq	%rax, 456(%rbp)
	leaq	456(%rbp), %rax
	movq	%rax, 400(%rbp)
	leaq	_RNvXsi_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impjNtB9_7Display3fmt(%rip), %rax
	movq	%rax, 408(%rbp)
.Ltmp14:
	leaq	480(%rbp), %rcx
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.14(%rip), %rdx
	leaq	400(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp15:
	movq	480(%rbp), %r15
	movq	488(%rbp), %rbx
	movq	456(%rbp), %rsi
	leaq	(,%rsi,4), %r13
	movq	%rsi, %rax
	shrq	$62, %rax
	setne	%al
	movabsq	$9223372036854775804, %rcx
	cmpq	%rcx, %r13
	seta	%cl
	orb	%al, %cl
	movq	%rbx, 704(%rbp)
	movq	%r15, 696(%rbp)
	jne	.LBB12_57
	movq	496(%rbp), %rdi
	testq	%r13, %r13
	je	.LBB12_51
	xorl	%edx, %edx
	movq	%r13, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rsi, %rcx
	testq	%rax, %rax
	je	.LBB12_56
	testq	%rsi, %rsi
	jne	.LBB12_53
	jmp	.LBB12_64
.LBB12_51:
	movl	$4, %eax
	xorl	%ecx, %ecx
	testq	%rsi, %rsi
	je	.LBB12_64
.LBB12_53:
	cmpq	$8, %rsi
	jae	.LBB12_58
	xorl	%edx, %edx
	jmp	.LBB12_61
.LBB12_58:
	movq	%rsi, %rdx
	movabsq	$4611686018427387896, %r8
	andq	%r8, %rdx
	xorl	%r8d, %r8d
	movdqa	%xmm10, %xmm0
	movdqa	%xmm9, %xmm1
	.p2align	4
.LBB12_59:
	movdqa	%xmm0, %xmm2
	pand	%xmm11, %xmm2
	movdqa	%xmm1, %xmm3
	pand	%xmm11, %xmm3
	packuswb	%xmm3, %xmm2
	pcmpeqd	%xmm12, %xmm2
	pandn	%xmm6, %xmm2
	movdqu	%xmm2, (%rax,%r8,4)
	movdqu	%xmm2, 16(%rax,%r8,4)
	addq	$8, %r8
	paddq	%xmm13, %xmm0
	paddq	%xmm13, %xmm1
	cmpq	%r8, %rdx
	jne	.LBB12_59
	.p2align	4
.LBB12_60:
	cmpq	%rdx, %rsi
	je	.LBB12_64
.LBB12_61:
	pxor	%xmm0, %xmm0
	testb	$1, %dl
	je	.LBB12_63
	movdqa	%xmm8, %xmm0
.LBB12_63:
	movd	%xmm0, (%rax,%rdx,4)
	incq	%rdx
	jmp	.LBB12_60
	.p2align	4
.LBB12_64:
	movq	%r15, 480(%rbp)
	movq	%rbx, 488(%rbp)
	movq	%rdi, 496(%rbp)
	movq	%rcx, 504(%rbp)
	movq	%rax, 512(%rbp)
	movq	%rsi, 520(%rbp)
	movq	664(%rbp), %rax
	movq	%rax, 736(%rbp)
	cmpq	648(%rbp), %rax
	jne	.LBB12_66
.Ltmp16:
	leaq	648(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	nop
.Ltmp17:
.LBB12_66:
	movq	656(%rbp), %rbx
	movq	736(%rbp), %rcx
	leaq	(%rcx,%rcx,2), %rax
	shlq	$4, %rax
	movdqu	480(%rbp), %xmm0
	movdqu	496(%rbp), %xmm1
	movdqu	512(%rbp), %xmm2
	movdqu	%xmm2, 32(%rbx,%rax)
	movdqu	%xmm1, 16(%rbx,%rax)
	movdqu	%xmm0, (%rbx,%rax)
	leaq	1(%rcx), %rdi
	movq	%rdi, 664(%rbp)
	leaq	456(%rbp), %rax
	movq	%rax, 400(%rbp)
	leaq	_RNvXsi_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impjNtB9_7Display3fmt(%rip), %rax
	movq	%rax, 408(%rbp)
.Ltmp18:
	leaq	480(%rbp), %rcx
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.15(%rip), %rdx
	leaq	400(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp19:
	movq	480(%rbp), %rax
	movq	%rax, 696(%rbp)
	movq	488(%rbp), %r15
	movq	496(%rbp), %r12
	testq	%r13, %r13
	je	.LBB12_68
	xorl	%edx, %edx
	movq	%r13, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rax, %rcx
	movq	%rsi, %r9
	testq	%rax, %rax
	je	.LBB12_73
	testq	%rsi, %rsi
	jne	.LBB12_70
	jmp	.LBB12_78
.LBB12_68:
	movl	$4, %ecx
	xorl	%r9d, %r9d
	testq	%rsi, %rsi
	je	.LBB12_78
.LBB12_70:
	cmpq	$1, %rsi
	jne	.LBB12_74
	xorl	%r8d, %r8d
	jmp	.LBB12_77
.LBB12_74:
	movq	%rsi, %r10
	movabsq	$4611686018427387902, %rax
	andq	%rax, %r10
	xorl	%r8d, %r8d
	movabsq	$-2049638230412172401, %r11
	.p2align	4
.LBB12_75:
	movq	%r8, %rax
	mulq	%r11
	shrq	%rdx
	andq	$-8, %rdx
	leaq	(%rdx,%rdx,8), %rax
	negq	%rax
	addq	%rbp, %rax
	addq	$176, %rax
	movss	(%rax,%r8,4), %xmm0
	movss	%xmm0, (%rcx,%r8,4)
	movd	4(%rax,%r8,4), %xmm0
	movd	%xmm0, 4(%rcx,%r8,4)
	addq	$2, %r8
	cmpq	%r8, %r10
	jne	.LBB12_75
	testb	$1, %sil
	je	.LBB12_78
.LBB12_77:
	movq	%r8, %rax
	movabsq	$-2049638230412172401, %rdx
	mulq	%rdx
	shrq	$4, %rdx
	addl	%edx, %edx
	leal	(%rdx,%rdx,8), %eax
	movl	%r8d, %edx
	subl	%eax, %edx
	movd	176(%rbp,%rdx,4), %xmm0
	movd	%xmm0, (%rcx,%r8,4)
.LBB12_78:
	movq	696(%rbp), %rax
	movq	%rax, 480(%rbp)
	movq	%r15, 488(%rbp)
	movq	%r12, 496(%rbp)
	movq	%r9, 504(%rbp)
	movq	%rcx, 512(%rbp)
	movq	%rsi, 520(%rbp)
	cmpq	648(%rbp), %rdi
	jne	.LBB12_81
.Ltmp22:
	movq	%r15, 704(%rbp)
	leaq	648(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	nop
.Ltmp23:
	movq	656(%rbp), %rbx
.LBB12_81:
	leaq	(%rdi,%rdi,2), %rax
	shlq	$4, %rax
	movdqu	480(%rbp), %xmm0
	movdqu	496(%rbp), %xmm1
	movdqu	512(%rbp), %xmm2
	movdqu	%xmm2, 32(%rbx,%rax)
	movdqu	%xmm1, 16(%rbx,%rax)
	movdqu	%xmm0, (%rbx,%rax)
	movq	736(%rbp), %rax
	leaq	2(%rax), %rdi
	movq	%rdi, 664(%rbp)
	leaq	456(%rbp), %rax
	movq	%rax, 400(%rbp)
	leaq	_RNvXsi_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impjNtB9_7Display3fmt(%rip), %rax
	movq	%rax, 408(%rbp)
.Ltmp24:
	leaq	480(%rbp), %rcx
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.16(%rip), %rdx
	leaq	400(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp25:
	movq	480(%rbp), %rax
	movq	%rax, 696(%rbp)
	movq	488(%rbp), %r15
	movq	496(%rbp), %r12
	testq	%r13, %r13
	je	.LBB12_83
	xorl	%edx, %edx
	movq	%r13, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rsi, %rcx
	testq	%rax, %rax
	je	.LBB12_88
	testq	%rsi, %rsi
	jne	.LBB12_85
	jmp	.LBB12_93
.LBB12_83:
	movl	$4, %eax
	xorl	%ecx, %ecx
	testq	%rsi, %rsi
	je	.LBB12_93
.LBB12_85:
	leaq	-1(%rsi), %r8
	movl	%esi, %edx
	andl	$3, %edx
	cmpq	$3, %r8
	jae	.LBB12_89
	xorl	%r8d, %r8d
	jmp	.LBB12_92
.LBB12_89:
	movq	%rsi, %r9
	movabsq	$4611686018427387900, %r8
	andq	%r8, %r9
	movd	232(%rbp), %xmm0
	movd	236(%rbp), %xmm1
	movd	240(%rbp), %xmm2
	movd	244(%rbp), %xmm3
	xorl	%r8d, %r8d
	.p2align	4
.LBB12_90:
	movd	%xmm0, (%rax,%r8,4)
	movd	%xmm1, 4(%rax,%r8,4)
	movd	%xmm2, 8(%rax,%r8,4)
	movd	%xmm3, 12(%rax,%r8,4)
	addq	$4, %r8
	cmpq	%r8, %r9
	jne	.LBB12_90
	testq	%rdx, %rdx
	je	.LBB12_93
	.p2align	4
.LBB12_92:
	movl	%r8d, %r9d
	andl	$3, %r9d
	movd	232(%rbp,%r9,4), %xmm0
	movd	%xmm0, (%rax,%r8,4)
	incq	%r8
	decq	%rdx
	jne	.LBB12_92
.LBB12_93:
	movq	696(%rbp), %rdx
	movq	%rdx, 480(%rbp)
	movq	%r15, 488(%rbp)
	movq	%r12, 496(%rbp)
	movq	%rcx, 504(%rbp)
	movq	%rax, 512(%rbp)
	movq	%rsi, 520(%rbp)
	cmpq	648(%rbp), %rdi
	jne	.LBB12_96
.Ltmp28:
	movq	%r15, 704(%rbp)
	leaq	648(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	nop
.Ltmp29:
	movq	656(%rbp), %rbx
.LBB12_96:
	leaq	(%rdi,%rdi,2), %rax
	shlq	$4, %rax
	movups	480(%rbp), %xmm0
	movdqu	496(%rbp), %xmm1
	movdqu	512(%rbp), %xmm2
	movdqu	%xmm2, 32(%rbx,%rax)
	movdqu	%xmm1, 16(%rbx,%rax)
	movups	%xmm0, (%rbx,%rax)
	movq	736(%rbp), %rax
	addq	$3, %rax
	movq	%rax, 696(%rbp)
	movq	%rax, 664(%rbp)
	leaq	456(%rbp), %rax
	movq	%rax, 400(%rbp)
	leaq	_RNvXsi_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impjNtB9_7Display3fmt(%rip), %rax
	movq	%rax, 408(%rbp)
.Ltmp30:
	leaq	480(%rbp), %rcx
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.17(%rip), %rdx
	leaq	400(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp31:
	movq	480(%rbp), %rax
	movq	%rax, 704(%rbp)
	movq	488(%rbp), %rdi
	movq	496(%rbp), %r12
	testq	%r13, %r13
	je	.LBB12_98
	xorl	%edx, %edx
	movq	%r13, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rax, %rcx
	movq	%rsi, %r15
	testq	%rax, %rax
	je	.LBB12_103
	testq	%rsi, %rsi
	movq	696(%rbp), %r13
	jne	.LBB12_100
	jmp	.LBB12_109
.LBB12_98:
	movl	$4, %ecx
	xorl	%r15d, %r15d
	testq	%rsi, %rsi
	movq	696(%rbp), %r13
	je	.LBB12_109
.LBB12_100:
	cmpq	$1, %rsi
	jne	.LBB12_104
	xorl	%r8d, %r8d
	jmp	.LBB12_108
.LBB12_104:
	movq	%r12, 640(%rbp)
	movq	%rdi, 680(%rbp)
	leaq	4(%rcx), %r13
	movq	%rsi, %rdi
	movabsq	$4611686018427387902, %rax
	andq	%rax, %rdi
	negq	%rdi
	movl	$1, %r9d
	movl	$2, %r12d
	xorl	%r8d, %r8d
	xorl	%r10d, %r10d
	.p2align	4
.LBB12_105:
	movq	%r10, %rax
	mulq	%r14
	movq	%rdx, %r11
	shrq	$15, %r11
	movq	%r11, %rax
	shlq	$16, %rax
	subq	%rax, %r11
	addq	%r9, %r11
	movq	%r9, %rax
	mulq	%r14
	shrq	$15, %rdx
	movq	%rdx, %rax
	shlq	$16, %rax
	subq	%rax, %rdx
	addq	%r12, %rdx
	xorps	%xmm0, %xmm0
	cvtsi2ss	%r11, %xmm0
	xorps	%xmm6, %xmm0
	movss	%xmm0, -4(%r13)
	xorps	%xmm0, %xmm0
	cvtsi2ss	%rdx, %xmm0
	addq	$2, %r10
	xorps	%xmm6, %xmm0
	movss	%xmm0, (%r13)
	addq	$-2, %r8
	addq	$8, %r13
	addq	$2, %r9
	addq	$2, %r12
	cmpq	%r8, %rdi
	jne	.LBB12_105
	testb	$1, %sil
	movl	$0, %eax
	movq	%rax, 728(%rbp)
	movq	680(%rbp), %rdi
	movq	696(%rbp), %r13
	movq	640(%rbp), %r12
	je	.LBB12_109
	negq	%r8
.LBB12_108:
	movq	%r8, %rax
	mulq	%r14
	shrq	$15, %rdx
	movl	%edx, %eax
	shll	$16, %eax
	subl	%eax, %edx
	leal	(%r8,%rdx), %eax
	incl	%eax
	xorps	%xmm0, %xmm0
	cvtsi2ss	%eax, %xmm0
	xorps	%xmm6, %xmm0
	movss	%xmm0, (%rcx,%r8,4)
.LBB12_109:
	movq	704(%rbp), %rax
	movq	%rax, 480(%rbp)
	movq	%rdi, 488(%rbp)
	movq	%r12, 496(%rbp)
	movq	%r15, 504(%rbp)
	movq	%rcx, 512(%rbp)
	movq	%rsi, 520(%rbp)
	cmpq	648(%rbp), %r13
	movq	712(%rbp), %rsi
	jne	.LBB12_112
.Ltmp34:
	movq	%rdi, 680(%rbp)
	leaq	648(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	nop
.Ltmp35:
	movq	656(%rbp), %rbx
.LBB12_112:
	addq	$8, %rsi
	leaq	(,%r13,2), %rax
	addq	%r13, %rax
	shlq	$4, %rax
	movdqu	480(%rbp), %xmm0
	movdqu	496(%rbp), %xmm1
	movdqu	512(%rbp), %xmm2
	movdqu	%xmm2, 32(%rbx,%rax)
	movdqu	%xmm1, 16(%rbx,%rax)
	movdqu	%xmm0, (%rbx,%rax)
	movq	736(%rbp), %rax
	addq	$4, %rax
	movq	%rax, 664(%rbp)
	cmpq	$232, %rsi
	jne	.LBB12_48
.LBB12_21:
	xorl	%r13d, %r13d
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.18(%rip), %rsi
	leaq	480(%rbp), %rdi
	leaq	400(%rbp), %rbx
	movd	__real@bf800000(%rip), %xmm8
	jmp	.LBB12_22
	.p2align	4
.LBB12_135:
	addq	$4, %r13
	movq	656(%rbp), %rax
	leaq	(%r12,%r12,2), %rcx
	shlq	$4, %rcx
	movdqu	480(%rbp), %xmm0
	movdqu	496(%rbp), %xmm1
	movdqu	512(%rbp), %xmm2
	movdqu	%xmm2, 32(%rax,%rcx)
	movdqu	%xmm1, 16(%rax,%rcx)
	movdqu	%xmm0, (%rax,%rcx)
	incq	%r12
	movq	%r12, 664(%rbp)
.LBB12_22:
	cmpq	$72, %r13
	je	.LBB12_141
	movl	176(%rbp,%r13), %eax
	movl	%eax, 456(%rbp)
	leaq	456(%rbp), %rax
	movq	%rax, 400(%rbp)
	leaq	_RNvXsu_NtNtCs8xEFJqa6dYS_4core3fmt3nummNtB7_8LowerHex3fmt(%rip), %rax
	movq	%rax, 408(%rbp)
.Ltmp38:
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	movq	%rbx, %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp39:
	movq	480(%rbp), %r14
	movq	488(%rbp), %r15
	movq	496(%rbp), %r12
	movl	$16, %r8d
	xorl	%edx, %edx
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	movq	%r15, 696(%rbp)
	movq	%r14, 712(%rbp)
	movq	%rax, 736(%rbp)
	je	.LBB12_25
	movss	456(%rbp), %xmm0
	movl	$1065353216, (%rax)
	movss	%xmm0, 4(%rax)
	movq	%xmm8, 8(%rax)
	movq	%r14, 480(%rbp)
	movq	%r15, 488(%rbp)
	movq	%r12, 496(%rbp)
	movq	$4, 504(%rbp)
	movq	%rax, 512(%rbp)
	movq	$4, 520(%rbp)
	movq	664(%rbp), %r12
	cmpq	648(%rbp), %r12
	jne	.LBB12_135
.Ltmp40:
	leaq	648(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	nop
.Ltmp41:
	jmp	.LBB12_135
.LBB12_141:
	movq	$2, 152(%rbp)
	movabsq	$281470681776127, %rax
	movq	%rax, 160(%rbp)
	leaq	504(%rbp), %r15
	xorl	%eax, %eax
	movdqa	__xmm@00000003000000020000000100000000(%rip), %xmm9
	movdqa	__xmm@00000081000000800000007f0000007e(%rip), %xmm10
	movdqa	__xmm@0000fffd00007ffd00003fff000003ff(%rip), %xmm11
	leaq	480(%rbp), %rdi
	movss	__real@3f000000(%rip), %xmm8
	leaq	608(%rbp), %r14
	jmp	.LBB12_142
	.p2align	4
.LBB12_234:
	movq	656(%rbp), %rax
	leaq	(%rsi,%rsi,2), %rcx
	shlq	$4, %rcx
	movdqa	480(%rbp), %xmm0
	movdqa	496(%rbp), %xmm1
	movdqa	512(%rbp), %xmm2
	movdqu	%xmm2, 32(%rax,%rcx)
	movdqu	%xmm1, 16(%rax,%rcx)
	movdqu	%xmm0, (%rax,%rcx)
	incq	%rsi
	movq	%rsi, 664(%rbp)
	movq	%r13, %rax
.LBB12_142:
	cmpq	$2, %rax
	je	.LBB12_145
	leaq	1(%rax), %r13
	movq	%r13, 144(%rbp)
	movl	160(%rbp,%rax,4), %eax
	movl	%eax, 48(%rbp)
	movl	$4, %r8d
	xorl	%edx, %edx
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	je	.LBB12_144
	movl	48(%rbp), %ecx
	xorps	%xmm0, %xmm0
	cvtsi2ss	%rcx, %xmm0
	movss	%xmm0, (%rax)
	movq	$1, 608(%rbp)
	movq	%rax, 616(%rbp)
	movq	$1, 624(%rbp)
	movq	$12, 488(%rbp)
	movdqu	%xmm9, 496(%rbp)
	movdqu	%xmm10, 512(%rbp)
	movdqu	%xmm11, 528(%rbp)
	movl	$1, %ebx
	xorl	%esi, %esi
.LBB12_220:
	movl	48(%rbp), %ecx
	.p2align	4
.LBB12_221:
	cmpq	$12, %rsi
	je	.LBB12_231
	movl	496(%rbp,%rsi,4), %edx
	incq	%rsi
	cmpl	%ecx, %edx
	jae	.LBB12_221
	movq	%rsi, 480(%rbp)
	movl	%edx, %ecx
	xorps	%xmm0, %xmm0
	cvtsi2ss	%rcx, %xmm0
	addss	%xmm8, %xmm0
	movd	%xmm0, %ecx
	leal	-1(%rcx), %edx
	incl	%ecx
	movq	$3, 408(%rbp)
	movl	%edx, 416(%rbp)
	movss	%xmm0, 420(%rbp)
	movl	%ecx, 424(%rbp)
	xorl	%ecx, %ecx
	jmp	.LBB12_224
	.p2align	4
.LBB12_230:
	pxor	%xmm6, %xmm12
	movq	616(%rbp), %rax
	movd	%xmm12, 4(%rax,%rbx,4)
	addq	$2, %rbx
	movq	%rbx, 624(%rbp)
	movq	%r12, %rcx
.LBB12_224:
	cmpq	$3, %rcx
	je	.LBB12_220
	leaq	1(%rcx), %r12
	movq	%r12, 400(%rbp)
	movd	416(%rbp,%rcx,4), %xmm12
	cmpq	608(%rbp), %rbx
	jne	.LBB12_228
	movb	$1, 726(%rbp)
.Ltmp44:
	movq	%r14, %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecfE8grow_oneCs2i4to50FHNk_9prototype
	nop
.Ltmp45:
	movq	616(%rbp), %rax
.LBB12_228:
	movd	%xmm12, (%rax,%rbx,4)
	leaq	1(%rbx), %rax
	movq	%rax, 624(%rbp)
	cmpq	608(%rbp), %rax
	jne	.LBB12_230
	movb	$1, 726(%rbp)
.Ltmp46:
	movq	%r14, %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecfE8grow_oneCs2i4to50FHNk_9prototype
	nop
.Ltmp47:
	jmp	.LBB12_230
	.p2align	4
.LBB12_231:
	leaq	48(%rbp), %rax
	movq	%rax, 480(%rbp)
	leaq	_RNvXs8_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impmNtB9_7Display3fmt(%rip), %rax
	movq	%rax, 488(%rbp)
	movb	$1, 726(%rbp)
.Ltmp48:
	leaq	456(%rbp), %rcx
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.23(%rip), %rdx
	movq	%rdi, %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp49:
	movq	624(%rbp), %rax
	movq	%rax, 16(%r15)
	movups	608(%rbp), %xmm0
	movups	%xmm0, (%r15)
	movups	456(%rbp), %xmm0
	movaps	%xmm0, 480(%rbp)
	movq	472(%rbp), %rax
	movq	%rax, 496(%rbp)
	movq	664(%rbp), %rsi
	cmpq	648(%rbp), %rsi
	jne	.LBB12_234
.Ltmp50:
	leaq	648(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	nop
.Ltmp51:
	jmp	.LBB12_234
.LBB12_145:
	movq	$6, 408(%rbp)
	movdqa	__xmm@00800000007fffff0000000200000001(%rip), %xmm0
	movdqu	%xmm0, 416(%rbp)
	movabsq	$288230376185266176, %rax
	movq	%rax, 432(%rbp)
	xorl	%eax, %eax
	leaq	480(%rbp), %rdi
	leaq	608(%rbp), %rbx
	movsd	__xmm@0000000000000000bf0000003f000000(%rip), %xmm9
	movsd	__xmm@00000000000000008000000000000000(%rip), %xmm10
	movq	__xmm@0000000000000000ff8000017fc00123(%rip), %xmm11
	jmp	.LBB12_146
	.p2align	4
.LBB12_213:
	movq	656(%rbp), %rax
	leaq	(%r12,%r12,2), %rcx
	shlq	$4, %rcx
	movdqu	480(%rbp), %xmm0
	movdqu	496(%rbp), %xmm1
	movdqu	512(%rbp), %xmm2
	movdqu	%xmm2, 32(%rax,%rcx)
	movdqu	%xmm1, 16(%rax,%rcx)
	movdqu	%xmm0, (%rax,%rcx)
	incq	%r12
	movq	%r12, 664(%rbp)
	movq	%r15, %rax
.LBB12_146:
	cmpq	$6, %rax
	je	.LBB12_150
	leaq	1(%rax), %r15
	movq	%r15, 400(%rbp)
	movl	416(%rbp,%rax,4), %r12d
	movl	%r12d, 144(%rbp)
	leaq	144(%rbp), %rax
	movq	%rax, 608(%rbp)
	leaq	_RNvXsu_NtNtCs8xEFJqa6dYS_4core3fmt3nummNtB7_8LowerHex3fmt(%rip), %rax
	movq	%rax, 616(%rbp)
.Ltmp54:
	movq	%rdi, %rcx
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.22(%rip), %rdx
	movq	%rbx, %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp55:
	movq	480(%rbp), %rsi
	movq	488(%rbp), %r14
	movq	496(%rbp), %r13
	movl	$32, %r8d
	xorl	%edx, %edx
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	movq	%r14, 696(%rbp)
	movq	%rsi, 712(%rbp)
	movq	%rax, 736(%rbp)
	je	.LBB12_149
	movd	%r12d, %xmm0
	movsldup	%xmm0, %xmm1
	xorps	%xmm6, %xmm0
	mulps	%xmm9, %xmm1
	movaps	%xmm10, %xmm2
	movlhps	%xmm1, %xmm2
	movl	%r12d, (%rax)
	movss	%xmm0, 4(%rax)
	movups	%xmm2, 8(%rax)
	movq	%xmm11, 24(%rax)
	movq	%rsi, 480(%rbp)
	movq	%r14, 488(%rbp)
	movq	%r13, 496(%rbp)
	movq	$8, 504(%rbp)
	movq	%rax, 512(%rbp)
	movq	$8, 520(%rbp)
	movq	664(%rbp), %r12
	cmpq	648(%rbp), %r12
	jne	.LBB12_213
.Ltmp56:
	leaq	648(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	nop
.Ltmp57:
	jmp	.LBB12_213
.LBB12_150:
	movl	$40, %r8d
	xorl	%edx, %edx
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	je	.LBB12_151
	movaps	__xmm@8080000000800000ff7fffff7f7fffff(%rip), %xmm0
	movups	%xmm0, (%rax)
	movaps	__xmm@bf8000003f8000008000000100000001(%rip), %xmm0
	movups	%xmm0, 16(%rax)
	movsd	__xmm@00000000000000008000000000000000(%rip), %xmm0
	movsd	%xmm0, 32(%rax)
	movq	$10, 480(%rbp)
	movq	%rax, 488(%rbp)
	movq	$10, 496(%rbp)
.Ltmp60:
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.19(%rip), %rdx
	leaq	648(%rbp), %rcx
	leaq	480(%rbp), %r9
	movl	$19, %r8d
	callq	_RINvCs2i4to50FHNk_9prototype3addReEB2_
	nop
.Ltmp61:
	movq	$65537, 416(%rbp)
	movq	$131071, 424(%rbp)
	xorl	%ebx, %ebx
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.21(%rip), %r12
	leaq	480(%rbp), %rcx
	leaq	608(%rbp), %rdi
	movabsq	$13520701739831091, %r14
	movss	__real@3d000000(%rip), %xmm9
	xorl	%r15d, %r15d
	cmpq	$2, %r15
	je	.LBB12_162
.LBB12_155:
	movq	%r15, %r13
	movq	416(%rbp,%r15,8), %rax
	movq	%rax, 144(%rbp)
	leaq	144(%rbp), %rax
	movq	%rax, 608(%rbp)
	leaq	_RNvXsi_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impjNtB9_7Display3fmt(%rip), %rax
	movq	%rax, 616(%rbp)
.Ltmp62:
	movq	%r12, %rdx
	movq	%rdi, %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp63:
	movq	480(%rbp), %rax
	movq	%rax, 736(%rbp)
	movq	488(%rbp), %rax
	movq	%rax, 712(%rbp)
	movq	144(%rbp), %rsi
	leaq	(,%rsi,4), %r15
	movq	%rsi, %rax
	shrq	$62, %rax
	setne	%al
	movabsq	$9223372036854775804, %rcx
	cmpq	%rcx, %r15
	seta	%cl
	orb	%al, %cl
	jne	.LBB12_197
	movq	496(%rbp), %r9
	testq	%r15, %r15
	je	.LBB12_158
	xorl	%edx, %edx
	movq	%r15, %r8
	movq	%r9, %rbx
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rbx, %r9
	xorl	%ebx, %ebx
	movq	%rax, %rcx
	movq	%rsi, %r10
	testq	%rax, %rax
	je	.LBB12_196
	testq	%rsi, %rsi
	movq	%r13, %r15
	jne	.LBB12_160
	jmp	.LBB12_203
.LBB12_158:
	movl	$4, %ecx
	xorl	%r10d, %r10d
	testq	%rsi, %rsi
	movq	%r13, %r15
	je	.LBB12_203
.LBB12_160:
	cmpq	$1, %rsi
	jne	.LBB12_198
	xorl	%r8d, %r8d
	jmp	.LBB12_202
.LBB12_198:
	movq	%r10, 728(%rbp)
	movq	%r9, 696(%rbp)
	leaq	4(%rcx), %r15
	movq	%rsi, %rdi
	movabsq	$4611686018427387902, %rax
	andq	%rax, %rdi
	negq	%rdi
	movl	$-2046, %ebx
	movl	$-2045, %r11d
	movl	$1, %r9d
	xorl	%r8d, %r8d
	xorl	%r10d, %r10d
	.p2align	4
.LBB12_199:
	movq	%r10, %rax
	mulq	%r14
	movq	%r10, %rax
	subq	%rdx, %rax
	shrq	%rax
	addq	%rdx, %rax
	shrq	$11, %rax
	imull	$4093, %eax, %eax
	movl	%ebx, %r12d
	subl	%eax, %r12d
	movq	%r9, %rax
	mulq	%r14
	movq	%r9, %rax
	subq	%rdx, %rax
	shrq	%rax
	addq	%rdx, %rax
	shrq	$11, %rax
	imull	$4093, %eax, %eax
	xorps	%xmm0, %xmm0
	cvtsi2ss	%r12d, %xmm0
	movl	%r11d, %edx
	subl	%eax, %edx
	mulss	%xmm9, %xmm0
	movss	%xmm0, -4(%r15)
	addq	$2, %r10
	xorps	%xmm0, %xmm0
	cvtsi2ss	%edx, %xmm0
	mulss	%xmm9, %xmm0
	movss	%xmm0, (%r15)
	addq	$-2, %r8
	addq	$8, %r15
	addl	$2, %ebx
	addl	$2, %r11d
	addq	$2, %r9
	cmpq	%r8, %rdi
	jne	.LBB12_199
	testb	$1, %sil
	leaq	608(%rbp), %rdi
	movl	$0, %ebx
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.21(%rip), %r12
	movq	%r13, %r15
	movq	696(%rbp), %r9
	movq	728(%rbp), %r10
	je	.LBB12_203
	negq	%r8
.LBB12_202:
	movq	%r8, %rax
	mulq	%r14
	movq	%r8, %rax
	subq	%rdx, %rax
	shrq	%rax
	addq	%rdx, %rax
	shrq	$11, %rax
	imull	$4093, %eax, %eax
	movl	%r8d, %edx
	subl	%eax, %edx
	addl	$-2046, %edx
	xorps	%xmm0, %xmm0
	cvtsi2ss	%edx, %xmm0
	mulss	%xmm9, %xmm0
	movss	%xmm0, (%rcx,%r8,4)
.LBB12_203:
	movq	736(%rbp), %rax
	movq	%rax, 480(%rbp)
	movq	712(%rbp), %rax
	movq	%rax, 488(%rbp)
	movq	%r9, 496(%rbp)
	movq	%r10, 504(%rbp)
	movq	%rcx, 512(%rbp)
	movq	%rsi, 520(%rbp)
	movq	664(%rbp), %rsi
	cmpq	648(%rbp), %rsi
	jne	.LBB12_205
.Ltmp64:
	leaq	648(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	nop
.Ltmp65:
.LBB12_205:
	incq	%r15
	movq	656(%rbp), %rax
	leaq	(%rsi,%rsi,2), %rcx
	shlq	$4, %rcx
	movups	480(%rbp), %xmm0
	movdqu	496(%rbp), %xmm1
	movdqu	512(%rbp), %xmm2
	movdqu	%xmm2, 32(%rax,%rcx)
	movdqu	%xmm1, 16(%rax,%rcx)
	movups	%xmm0, (%rax,%rcx)
	incq	%rsi
	movq	%rsi, 664(%rbp)
	leaq	480(%rbp), %rcx
	cmpq	$2, %r15
	jne	.LBB12_155
.LBB12_162:
	movabsq	$6840158756896436237, %rbx
	leaq	648(%rbp), %r12
	movabsq	$-7046029254386353131, %r13
	movabsq	$-4658895280553007687, %rcx
	movabsq	$-7723592293110705685, %rdx
	leaq	.LJTI12_0(%rip), %r14
	movss	__real@3a800000(%rip), %xmm9
	movss	__real@ba800000(%rip), %xmm10
	xorl	%r15d, %r15d
	cmpq	$2047, %r15
	ja	.LBB12_240
.LBB12_164:
	movq	%r15, 144(%rbp)
	testb	$1, %r15b
	jne	.LBB12_165
	imull	$18079, %r15d, %eax
	shrl	$19, %eax
	leal	(%rax,%rax,8), %ecx
	leal	(%rcx,%rcx,2), %ecx
	addl	%eax, %eax
	addl	%ecx, %eax
	movl	%r15d, %ecx
	subl	%eax, %ecx
	movzwl	%cx, %eax
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.13(%rip), %rcx
	movq	(%rcx,%rax,8), %rdi
	jmp	.LBB12_167
.LBB12_165:
	addq	%r13, %rbx
	movq	%rbx, %rax
	shrq	$30, %rax
	xorq	%rbx, %rax
	imulq	%rcx, %rax
	movq	%rax, %rdi
	shrq	$27, %rdi
	xorq	%rax, %rdi
	imulq	%rdx, %rdi
	movq	%rdi, %rax
	shrq	$63, %rax
	shrq	$32, %rdi
	xorq	%rax, %rdi
	movq	%rdi, %rax
	movl	$4290777085, %ecx
	imulq	%rcx, %rax
	shrq	$43, %rax
	movl	%eax, %ecx
	shll	$11, %eax
	leal	(%rax,%rcx,2), %eax
	subl	%eax, %edi
.LBB12_167:
	movl	%r15d, %eax
	andl	$7, %eax
	movq	%rax, 608(%rbp)
	leaq	(,%rdi,4), %rsi
	movq	%rdi, %rax
	shrq	$62, %rax
	setne	%al
	movabsq	$9223372036854775804, %rcx
	cmpq	%rcx, %rsi
	seta	%cl
	orb	%al, %cl
	jne	.LBB12_168
	testq	%rsi, %rsi
	je	.LBB12_170
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rdi, 712(%rbp)
	movq	%rax, 736(%rbp)
	testq	%rax, %rax
	jne	.LBB12_171
	jmp	.LBB12_176
.LBB12_170:
	movl	$4, %eax
	movq	%rax, 736(%rbp)
	movq	$0, 712(%rbp)
.LBB12_171:
	testq	%rdi, %rdi
	je	.LBB12_186
	movq	%rbx, %rdx
	xorl	%eax, %eax
	movabsq	$-4658895280553007687, %r11
	movabsq	$-7723592293110705685, %rsi
	jmp	.LBB12_173
.LBB12_184:
	movl	%ecx, %edx
	imulq	$954437177, %rdx, %rdx
	shrq	$34, %rdx
	addl	%edx, %edx
	leal	(%rdx,%rdx,8), %edx
	subl	%edx, %ecx
	movl	176(%rbp,%rcx,4), %ecx
.LBB12_185:
	movq	736(%rbp), %rdx
	movl	%ecx, (%rdx,%rax,4)
	incq	%rax
	movq	%rbx, %rdx
	cmpq	%rax, %rdi
	je	.LBB12_186
.LBB12_173:
	leaq	(%rdx,%r13), %rbx
	movq	%rbx, %rcx
	shrq	$30, %rcx
	xorq	%rbx, %rcx
	imulq	%r11, %rcx
	movq	%rcx, %r8
	shrq	$27, %r8
	xorq	%rcx, %r8
	imulq	%rsi, %r8
	movq	%r8, %rcx
	shrq	$63, %rcx
	shrq	$32, %r8
	xorl	%r8d, %ecx
	movq	608(%rbp), %r8
	cmpq	$6, %r8
	ja	.LBB12_178
	movslq	(%r14,%r8,4), %r8
	addq	%r14, %r8
	jmpq	*%r8
.LBB12_179:
	andl	$-2139095041, %ecx
	movabsq	$4354685564936845354, %r8
	addq	%r8, %rdx
	movq	%rdx, %r9
	shrq	$30, %r9
	xorq	%rdx, %r9
	imulq	%r11, %r9
	movq	%r9, %r8
	shrq	$27, %r8
	xorq	%r9, %r8
	imulq	%rsi, %r8
	movq	%r8, %r9
	shrq	$63, %r9
	movq	%r8, %r10
	shrq	$32, %r10
	xorl	%r10d, %r9d
	shrq	$33, %r8
	movl	$2164392969, %r10d
	imulq	%r10, %r8
	shrq	$38, %r8
	movl	%r8d, %r10d
	shll	$8, %r10d
	addl	%r8d, %r8d
	subl	%r10d, %r8d
	addl	%r9d, %r8d
	shll	$23, %r8d
	addl	%r8d, %ecx
	addl	$8388608, %ecx
	movq	%rdx, %rbx
	jmp	.LBB12_185
.LBB12_180:
	andl	$-2143289345, %ecx
	jmp	.LBB12_185
.LBB12_181:
	andl	$-2139095041, %ecx
	orl	$2130706432, %ecx
	jmp	.LBB12_185
.LBB12_178:
	movl	%ecx, %edx
	movl	$2147516417, %r8d
	imulq	%r8, %rdx
	shrq	$47, %rdx
	movl	%edx, %r8d
	shll	$16, %r8d
	subl	%r8d, %edx
	addl	%edx, %ecx
	addl	$-32767, %ecx
	xorps	%xmm0, %xmm0
	cvtsi2ss	%ecx, %xmm0
	addss	%xmm8, %xmm0
	movd	%xmm0, %ecx
	jmp	.LBB12_185
.LBB12_182:
	movl	%ecx, %edx
	imulq	$208618821, %rdx, %rdx
	shrq	$32, %rdx
	movl	%ecx, %r8d
	subl	%edx, %r8d
	shrl	%r8d
	addl	%edx, %r8d
	shrl	$19, %r8d
	imull	$1000003, %r8d, %edx
	subl	%edx, %ecx
	xorps	%xmm0, %xmm0
	cvtsi2ss	%ecx, %xmm0
	mulss	%xmm9, %xmm0
	movd	%xmm0, %ecx
	jmp	.LBB12_185
.LBB12_183:
	movl	%ecx, %edx
	imulq	$208618821, %rdx, %rdx
	shrq	$32, %rdx
	movl	%ecx, %r8d
	subl	%edx, %r8d
	shrl	%r8d
	addl	%edx, %r8d
	shrl	$19, %r8d
	imull	$1000003, %r8d, %edx
	subl	%edx, %ecx
	xorps	%xmm0, %xmm0
	cvtsi2ss	%ecx, %xmm0
	mulss	%xmm10, %xmm0
	movd	%xmm0, %ecx
	jmp	.LBB12_185
.LBB12_186:
	leaq	144(%rbp), %rax
	movq	%rax, 480(%rbp)
	leaq	_RNvXsi_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impjNtB9_7Display3fmt(%rip), %rax
	movq	%rax, 488(%rbp)
	leaq	608(%rbp), %rcx
	movq	%rcx, 496(%rbp)
	movq	%rax, 504(%rbp)
	movb	$1, 675(%rbp)
.Ltmp142:
	leaq	400(%rbp), %rcx
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.20(%rip), %rdx
	leaq	480(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp143:
	movq	416(%rbp), %rax
	movq	%rax, 496(%rbp)
	movups	400(%rbp), %xmm0
	movaps	%xmm0, 480(%rbp)
	movq	712(%rbp), %rax
	movq	%rax, 504(%rbp)
	movq	736(%rbp), %rax
	movq	%rax, 512(%rbp)
	movq	%rdi, 520(%rbp)
	movq	664(%rbp), %rsi
	cmpq	648(%rbp), %rsi
	jne	.LBB12_189
.Ltmp144:
	movq	%r12, %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	nop
.Ltmp145:
.LBB12_189:
	incq	%r15
	movq	656(%rbp), %rax
	leaq	(%rsi,%rsi,2), %rcx
	shlq	$4, %rcx
	movaps	480(%rbp), %xmm0
	movdqa	496(%rbp), %xmm1
	movdqa	512(%rbp), %xmm2
	movdqu	%xmm2, 32(%rax,%rcx)
	movdqu	%xmm1, 16(%rax,%rcx)
	movups	%xmm0, (%rax,%rcx)
	incq	%rsi
	movq	%rsi, 664(%rbp)
	movabsq	$-4658895280553007687, %rcx
	movabsq	$-7723592293110705685, %rdx
	cmpq	$2047, %r15
	jbe	.LBB12_164
.LBB12_240:
	movq	664(%rbp), %r13
	movq	%r13, 384(%rbp)
	movups	648(%rbp), %xmm0
	movaps	%xmm0, 368(%rbp)
	movq	%r13, -40(%rbp)
	movaps	%xmm7, 480(%rbp)
	movaps	__xmm@ff7fffff7f7fffff00800000007fffff(%rip), %xmm0
	movaps	%xmm0, 496(%rbp)
	movaps	__xmm@7f8000017fc01234ff8000007f800000(%rip), %xmm0
	movaps	%xmm0, 512(%rbp)
	xorl	%edx, %edx
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.44(%rip), %r15
	leaq	176(%rbp), %r12
	xorl	%r8d, %r8d
	xorl	%eax, %eax
	testb	$1, %r8b
	movabsq	$9223372036854775804, %rcx
	jne	.LBB12_243
.LBB12_242:
	cmpq	$21, %rax
	jae	.LBB12_243
	leaq	1(%rax), %r9
	cmpq	$20, %rax
	sete	%r8b
	cmoveq	%rax, %r9
	movq	%rax, 456(%rbp)
	xorl	%edi, %edi
	cmpq	%rax, %rdi
	jae	.LBB12_410
.LBB12_411:
	movq	%rdi, 400(%rbp)
	incq	%rdi
	xorl	%r10d, %r10d
	cmpq	$48, %r10
	je	.LBB12_749
.LBB12_413:
	movl	480(%rbp,%r10), %eax
	movl	%eax, 608(%rbp)
	movq	456(%rbp), %r14
	leaq	(,%r14,4), %rsi
	movq	%r14, %rax
	shrq	$62, %rax
	setne	%al
	cmpq	%rcx, %rsi
	seta	%cl
	orb	%al, %cl
	jne	.LBB12_425
	movq	%r10, 704(%rbp)
	movq	%r9, 728(%rbp)
	movq	%r8, 696(%rbp)
	xorl	%r13d, %r13d
	testq	%rsi, %rsi
	je	.LBB12_415
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%r14, 736(%rbp)
	testq	%rax, %rax
	jne	.LBB12_416
	jmp	.LBB12_424
.LBB12_415:
	movl	$4, %eax
	movq	$0, 736(%rbp)
.LBB12_416:
	cmpq	$2, %r14
	jb	.LBB12_426
	movl	$1, %ecx
	movq	%rax, %r10
	cmpq	$9, %r14
	jb	.LBB12_421
	leaq	-1(%r14), %rdx
	movq	%rdx, %r8
	andq	$-8, %r8
	leaq	(%rax,%r8,4), %r10
	leaq	1(%r8), %rcx
	xorl	%r9d, %r9d
.LBB12_419:
	movups	%xmm6, (%rax,%r9,4)
	movups	%xmm6, 16(%rax,%r9,4)
	addq	$8, %r9
	cmpq	%r9, %r8
	jne	.LBB12_419
	cmpq	%r8, %rdx
	je	.LBB12_427
.LBB12_421:
	movq	%r14, %rdx
	subq	%rcx, %rdx
.LBB12_422:
	movl	$-2147483648, (%r10)
	addq	$4, %r10
	decq	%rdx
	jne	.LBB12_422
	jmp	.LBB12_427
.LBB12_426:
	movq	%rax, %r10
	testq	%r14, %r14
	je	.LBB12_428
.LBB12_427:
	movl	$-2147483648, (%r10)
.LBB12_428:
	movq	400(%rbp), %rcx
	cmpq	%r14, %rcx
	movq	%rax, 712(%rbp)
	jae	.LBB12_438
	movss	608(%rbp), %xmm7
	movss	%xmm7, (%rax,%rcx,4)
	leaq	456(%rbp), %rax
	movq	%rax, 176(%rbp)
	leaq	_RNvXsi_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impjNtB9_7Display3fmt(%rip), %rax
	movq	%rax, 184(%rbp)
	leaq	400(%rbp), %rcx
	movq	%rcx, 192(%rbp)
	movq	%rax, 200(%rbp)
	leaq	608(%rbp), %rax
	movq	%rax, 208(%rbp)
	leaq	_RNvXsu_NtNtCs8xEFJqa6dYS_4core3fmt3nummNtB7_8LowerHex3fmt(%rip), %rax
	movq	%rax, 216(%rbp)
	movb	$1, 727(%rbp)
.Ltmp70:
	leaq	-64(%rbp), %rcx
	movq	%r15, %rdx
	movq	%r12, %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp71:
	movups	-64(%rbp), %xmm0
	movaps	%xmm0, 176(%rbp)
	movq	-48(%rbp), %rax
	movq	%rax, 192(%rbp)
	movq	736(%rbp), %rax
	movq	%rax, 200(%rbp)
	movq	712(%rbp), %rax
	movq	%rax, 208(%rbp)
	movq	%r14, 216(%rbp)
	movq	384(%rbp), %r12
	cmpq	368(%rbp), %r12
	jne	.LBB12_432
.Ltmp72:
	leaq	368(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	nop
.Ltmp73:
.LBB12_432:
	movq	376(%rbp), %rsi
	leaq	(%r12,%r12,2), %rax
	shlq	$4, %rax
	movaps	176(%rbp), %xmm0
	movaps	192(%rbp), %xmm1
	movdqa	208(%rbp), %xmm2
	movdqu	%xmm2, 32(%rsi,%rax)
	movups	%xmm1, 16(%rsi,%rax)
	movups	%xmm0, (%rsi,%rax)
	leaq	1(%r12), %rdx
	movq	%rdx, 384(%rbp)
	movq	456(%rbp), %r14
	leaq	(,%r14,4), %r15
	movq	%r14, %rax
	shrq	$62, %rax
	setne	%al
	movabsq	$9223372036854775804, %rcx
	cmpq	%rcx, %r15
	seta	%cl
	orb	%al, %cl
	jne	.LBB12_442
	movq	%rdx, 392(%rbp)
	movq	%r12, 640(%rbp)
	testq	%r15, %r15
	je	.LBB12_434
	xorl	%edx, %edx
	movq	%r15, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%r14, 632(%rbp)
	movq	%rax, 680(%rbp)
	testq	%rax, %rax
	jne	.LBB12_435
	jmp	.LBB12_441
.LBB12_434:
	movl	$4, %eax
	movq	%rax, 680(%rbp)
	movq	$0, 632(%rbp)
.LBB12_435:
	testq	%r14, %r14
	je	.LBB12_448
	cmpq	$1, %r14
	jne	.LBB12_443
	xorl	%ecx, %ecx
	jmp	.LBB12_447
.LBB12_443:
	movq	680(%rbp), %rax
	leaq	4(%rax), %r10
	movq	%r14, %r11
	movabsq	$4611686018427387902, %rax
	andq	%rax, %r11
	negq	%r11
	movq	$-1, %r13
	movl	$1, %r8d
	xorl	%ecx, %ecx
	xorl	%r9d, %r9d
	movabsq	$-6148914691236517205, %rbx
.LBB12_444:
	movq	%r9, %rax
	mulq	%rbx
	shrq	%rdx
	leaq	(%rdx,%rdx,2), %r12
	movq	%r13, %r15
	movq	%r8, %rax
	mulq	%rbx
	subq	%r12, %r15
	shrq	%rdx
	leaq	(%rdx,%rdx,2), %rax
	movq	%r9, %rdx
	xorps	%xmm0, %xmm0
	cvtsi2ss	%r15, %xmm0
	subq	%rax, %rdx
	xorps	%xmm1, %xmm1
	cvtsi2ss	%rdx, %xmm1
	movss	%xmm0, -4(%r10)
	addq	$2, %r9
	movss	%xmm1, (%r10)
	addq	$-2, %rcx
	addq	$8, %r10
	addq	$2, %r13
	addq	$2, %r8
	cmpq	%rcx, %r11
	jne	.LBB12_444
	testb	$1, %r14b
	je	.LBB12_448
	negq	%rcx
.LBB12_447:
	movq	%rcx, %rax
	movabsq	$-6148914691236517205, %rdx
	mulq	%rdx
	shrq	%rdx
	leal	(%rdx,%rdx,2), %eax
	notl	%eax
	addl	%ecx, %eax
	xorps	%xmm0, %xmm0
	cvtsi2ss	%eax, %xmm0
	movq	680(%rbp), %rax
	movss	%xmm0, (%rax,%rcx,4)
.LBB12_448:
	movq	400(%rbp), %rcx
	cmpq	%r14, %rcx
	jae	.LBB12_454
	movq	680(%rbp), %rbx
	movss	%xmm7, (%rbx,%rcx,4)
	leaq	456(%rbp), %rax
	movq	%rax, 176(%rbp)
	leaq	_RNvXsi_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impjNtB9_7Display3fmt(%rip), %rax
	movq	%rax, 184(%rbp)
	leaq	400(%rbp), %rcx
	movq	%rcx, 192(%rbp)
	movq	%rax, 200(%rbp)
	leaq	608(%rbp), %rax
	movq	%rax, 208(%rbp)
	leaq	_RNvXsu_NtNtCs8xEFJqa6dYS_4core3fmt3nummNtB7_8LowerHex3fmt(%rip), %rax
	movq	%rax, 216(%rbp)
	movb	$1, 695(%rbp)
.Ltmp76:
	leaq	-88(%rbp), %rcx
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.46(%rip), %rdx
	leaq	176(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp77:
	movabsq	$9223372036854775804, %rcx
	movups	-88(%rbp), %xmm0
	movaps	%xmm0, 176(%rbp)
	movq	-72(%rbp), %rax
	movq	%rax, 192(%rbp)
	movq	632(%rbp), %rax
	movq	%rax, 200(%rbp)
	movq	%rbx, 208(%rbp)
	movq	%r14, 216(%rbp)
	movq	392(%rbp), %rax
	cmpq	368(%rbp), %rax
	jne	.LBB12_453
.Ltmp78:
	leaq	368(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	nop
.Ltmp79:
	movq	376(%rbp), %rsi
	movabsq	$9223372036854775804, %rcx
	movq	392(%rbp), %rax
.LBB12_453:
	movq	704(%rbp), %r10
	addq	$4, %r10
	leaq	(%rax,%rax,2), %rax
	shlq	$4, %rax
	movaps	176(%rbp), %xmm0
	movdqa	192(%rbp), %xmm1
	movdqa	208(%rbp), %xmm2
	movdqu	%xmm2, 32(%rsi,%rax)
	movdqu	%xmm1, 16(%rsi,%rax)
	movups	%xmm0, (%rsi,%rax)
	movq	640(%rbp), %r13
	addq	$2, %r13
	movq	%r13, 384(%rbp)
	xorl	%edx, %edx
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.44(%rip), %r15
	leaq	176(%rbp), %r12
	movq	696(%rbp), %r8
	movq	728(%rbp), %r9
	cmpq	$48, %r10
	jne	.LBB12_413
.LBB12_749:
	movq	456(%rbp), %rax
	cmpq	%rax, %rdi
	jb	.LBB12_411
.LBB12_410:
	movq	%r9, %rax
	testb	$1, %r8b
	movabsq	$9223372036854775804, %rcx
	je	.LBB12_242
.LBB12_243:
	movabsq	$6840158756896383001, %rbx
	xorl	%esi, %esi
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.42(%rip), %rdi
	leaq	176(%rbp), %r15
	movaps	__xmm@daa66d2c7ddf743f3c6ef372fe94f82a(%rip), %xmm6
	movaps	__xmm@9e3779b97f4a7c150000000000000000(%rip), %xmm7
	movaps	__xmm@9e3779b97f4a7c159e3779b97f4a7c15(%rip), %xmm8
	movdqa	__xmm@00000000bf58476d00000000bf58476d(%rip), %xmm9
	movdqa	__xmm@bf58476d1ce4e5b9bf58476d1ce4e5b9(%rip), %xmm10
	movdqa	__xmm@0000000094d049bb0000000094d049bb(%rip), %xmm11
	movdqa	__xmm@94d049bb133111eb94d049bb133111eb(%rip), %xmm12
	movdqa	__xmm@78dde6e5fd29f05478dde6e5fd29f054(%rip), %xmm13
	jmp	.LBB12_244
.LBB12_38:
.Ltmp12:
	movl	$4, %ecx
	movl	$4, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp13:
	jmp	.LBB12_39
.LBB12_168:
	xorl	%ecx, %ecx
.LBB12_177:
.Ltmp146:
	movq	%rsi, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp147:
	jmp	.LBB12_39
.LBB12_25:
.Ltmp42:
	movl	$4, %ecx
	movl	$16, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp43:
	jmp	.LBB12_39
.LBB12_144:
.Ltmp52:
	movl	$4, %ecx
	movl	$4, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp53:
	jmp	.LBB12_39
.LBB12_149:
.Ltmp58:
	movl	$4, %ecx
	movl	$32, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp59:
	jmp	.LBB12_39
.LBB12_391:
	incq	%rsi
	movq	376(%rbp), %rax
	leaq	(,%r13,2), %rcx
	addq	%r13, %rcx
	shlq	$4, %rcx
	movaps	176(%rbp), %xmm0
	movdqa	192(%rbp), %xmm1
	movdqa	208(%rbp), %xmm2
	movdqu	%xmm2, 32(%rax,%rcx)
	movdqu	%xmm1, 16(%rax,%rcx)
	movups	%xmm0, (%rax,%rcx)
	incq	%r13
	movq	%r13, 384(%rbp)
.LBB12_244:
	cmpq	$4096, %rsi
	jae	.LBB12_245
	movq	%rsi, 400(%rbp)
	cmpq	$128, %rsi
	jae	.LBB12_385
	movq	%rsi, %r12
	jmp	.LBB12_386
.LBB12_385:
	movabsq	$-7046029254386353131, %rax
	addq	%rax, %rbx
	movq	%rbx, %rax
	shrq	$30, %rax
	xorq	%rbx, %rax
	movabsq	$-4658895280553007687, %rcx
	imulq	%rcx, %rax
	movq	%rax, %r12
	shrq	$27, %r12
	xorq	%rax, %r12
	movabsq	$-7723592293110705685, %rax
	imulq	%rax, %r12
	movq	%r12, %rax
	shrq	$63, %rax
	shrq	$32, %r12
	xorq	%rax, %r12
	imulq	$4192257, %r12, %rax
	shrq	$34, %rax
	movl	%eax, %ecx
	shll	$12, %eax
	leal	(%rax,%rcx,2), %eax
	subl	%eax, %r12d
.LBB12_386:
	testq	%r12, %r12
	movq	%r12, 712(%rbp)
	je	.LBB12_387
	leaq	(,%r12,4), %r14
	xorl	%edx, %edx
	movq	%r14, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rax, 736(%rbp)
	testq	%rax, %rax
	je	.LBB12_401
	cmpq	$4, %r12
	jae	.LBB12_397
	movq	%rbx, %rcx
	xorl	%eax, %eax
	jmp	.LBB12_395
.LBB12_387:
	movl	$4, %eax
	movq	%rax, 736(%rbp)
	jmp	.LBB12_388
.LBB12_397:
	movl	%r12d, %eax
	andl	$2147483644, %eax
	movq	%rax, %rcx
	movabsq	$-7046029254386353131, %rdx
	imulq	%rdx, %rcx
	addq	%rbx, %rcx
	movq	%rbx, %xmm0
	pshufd	$68, %xmm0, %xmm0
	movdqa	%xmm0, %xmm1
	paddq	%xmm6, %xmm1
	paddq	%xmm7, %xmm0
	andq	$-16, %r14
	xorl	%edx, %edx
	movq	736(%rbp), %r8
.LBB12_398:
	movdqa	%xmm0, %xmm2
	paddq	%xmm8, %xmm2
	movdqa	%xmm1, %xmm3
	paddq	%xmm8, %xmm3
	movdqa	%xmm3, %xmm5
	psrlq	$30, %xmm5
	movdqa	%xmm2, %xmm4
	psrlq	$30, %xmm4
	pxor	%xmm2, %xmm4
	pxor	%xmm3, %xmm5
	movdqa	%xmm5, %xmm2
	pmuludq	%xmm9, %xmm2
	movdqa	%xmm5, %xmm3
	psrlq	$32, %xmm3
	pmuludq	%xmm10, %xmm3
	paddq	%xmm2, %xmm3
	psllq	$32, %xmm3
	pmuludq	%xmm10, %xmm5
	paddq	%xmm3, %xmm5
	movdqa	%xmm4, %xmm2
	pmuludq	%xmm9, %xmm2
	movdqa	%xmm4, %xmm3
	psrlq	$32, %xmm3
	pmuludq	%xmm10, %xmm3
	paddq	%xmm2, %xmm3
	psllq	$32, %xmm3
	pmuludq	%xmm10, %xmm4
	paddq	%xmm3, %xmm4
	movdqa	%xmm4, %xmm2
	psrlq	$27, %xmm2
	movdqa	%xmm5, %xmm3
	psrlq	$27, %xmm3
	pxor	%xmm5, %xmm3
	pxor	%xmm4, %xmm2
	movdqa	%xmm2, %xmm4
	pmuludq	%xmm11, %xmm4
	movdqa	%xmm2, %xmm5
	psrlq	$32, %xmm5
	pmuludq	%xmm12, %xmm5
	paddq	%xmm4, %xmm5
	psllq	$32, %xmm5
	pmuludq	%xmm12, %xmm2
	paddq	%xmm5, %xmm2
	movdqa	%xmm3, %xmm4
	pmuludq	%xmm11, %xmm4
	movdqa	%xmm3, %xmm5
	psrlq	$32, %xmm5
	pmuludq	%xmm12, %xmm5
	paddq	%xmm4, %xmm5
	psllq	$32, %xmm5
	pmuludq	%xmm12, %xmm3
	paddq	%xmm5, %xmm3
	movdqa	%xmm3, %xmm4
	psrlq	$63, %xmm4
	movdqa	%xmm2, %xmm5
	psrlq	$63, %xmm5
	psrlq	$32, %xmm3
	pxor	%xmm4, %xmm3
	psrlq	$32, %xmm2
	pxor	%xmm5, %xmm2
	shufps	$136, %xmm3, %xmm2
	movups	%xmm2, (%r8,%rdx)
	paddq	%xmm13, %xmm0
	paddq	%xmm13, %xmm1
	addq	$16, %rdx
	cmpq	%rdx, %r14
	jne	.LBB12_398
	cmpq	%rax, %r12
	jne	.LBB12_395
	movq	%rcx, %rbx
	jmp	.LBB12_388
.LBB12_395:
	movq	%rcx, %rbx
	movabsq	$-7046029254386353131, %r8
	movabsq	$-4658895280553007687, %r9
	movabsq	$-7723592293110705685, %r10
	movq	736(%rbp), %r11
.LBB12_396:
	addq	%r8, %rbx
	movq	%rbx, %rcx
	shrq	$30, %rcx
	xorq	%rbx, %rcx
	imulq	%r9, %rcx
	movq	%rcx, %rdx
	shrq	$27, %rdx
	xorq	%rcx, %rdx
	imulq	%r10, %rdx
	movq	%rdx, %rcx
	shrq	$63, %rcx
	shrq	$32, %rdx
	xorl	%edx, %ecx
	movl	%ecx, (%r11,%rax,4)
	incq	%rax
	cmpq	%rax, %r12
	jne	.LBB12_396
.LBB12_388:
	leaq	400(%rbp), %rax
	movq	%rax, 176(%rbp)
	leaq	_RNvXsi_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impjNtB9_7Display3fmt(%rip), %rax
	movq	%rax, 184(%rbp)
	movb	$1, 673(%rbp)
.Ltmp138:
	leaq	48(%rbp), %rcx
	movq	%rdi, %rdx
	movq	%r15, %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp139:
	movups	48(%rbp), %xmm0
	movaps	%xmm0, 176(%rbp)
	movq	64(%rbp), %rax
	movq	%rax, 192(%rbp)
	movq	712(%rbp), %rax
	movq	%rax, 200(%rbp)
	movq	736(%rbp), %rcx
	movq	%rcx, 208(%rbp)
	movq	%rax, 216(%rbp)
	cmpq	368(%rbp), %r13
	jne	.LBB12_391
.Ltmp140:
	leaq	368(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	nop
.Ltmp141:
	jmp	.LBB12_391
.LBB12_151:
.Ltmp148:
	movl	$4, %ecx
	movl	$40, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp149:
	jmp	.LBB12_39
.LBB12_245:
	movabsq	$-3750763034362895579, %rax
	movq	%rax, 112(%rbp)
	movq	%rax, 96(%rbp)
	movq	%rax, 88(%rbp)
	movq	$0, 80(%rbp)
	movq	$0, 352(%rbp)
	movq	376(%rbp), %rax
	movq	%rax, 104(%rbp)
	movq	%r13, 640(%rbp)
	testq	%r13, %r13
	je	.LBB12_246
	movq	640(%rbp), %rax
	leaq	(%rax,%rax,2), %rcx
	shlq	$4, %rcx
	movq	104(%rbp), %rax
	addq	%rax, %rcx
	movq	%rcx, 32(%rbp)
	movq	$0, 40(%rbp)
	movabsq	$1099511628211, %r15
	movdqa	__xmm@a55aa55aa55aa55aa55aa55aa55aa55a(%rip), %xmm9
	movq	%rax, 704(%rbp)
	jmp	.LBB12_276
.LBB12_381:
	movq	24(%rbp), %rax
	movq	%rax, 704(%rbp)
	cmpq	32(%rbp), %rax
	je	.LBB12_259
.LBB12_276:
	movq	704(%rbp), %rcx
	movq	40(%rcx), %rax
	movq	%rax, 736(%rbp)
	addq	%rax, 80(%rbp)
	movq	16(%rcx), %rcx
	movl	%ecx, %r11d
	shrl	$16, %r11d
	movl	%ecx, %r10d
	shrl	$24, %r10d
	movq	%rcx, %r9
	shrq	$32, %r9
	movq	%rcx, %r8
	shrq	$40, %r8
	movq	%rcx, %rdx
	shrq	$48, %rdx
	movq	%rcx, %rax
	shrq	$56, %rax
	movzbl	%cl, %esi
	xorq	88(%rbp), %rsi
	imulq	%r15, %rsi
	movzbl	%ch, %edi
	xorq	%rsi, %rdi
	imulq	%r15, %rdi
	movzbl	%r11b, %r11d
	xorq	%rdi, %r11
	imulq	%r15, %r11
	xorq	%r10, %r11
	imulq	%r15, %r11
	movzbl	%r9b, %r9d
	xorq	%r11, %r9
	imulq	%r15, %r9
	movzbl	%r8b, %r8d
	xorq	%r9, %r8
	imulq	%r15, %r8
	movzbl	%dl, %r9d
	xorq	%r8, %r9
	imulq	%r15, %r9
	xorq	%rax, %r9
	imulq	%r15, %r9
	testq	%rcx, %rcx
	je	.LBB12_277
	movq	704(%rbp), %rax
	movq	8(%rax), %rdx
	movq	%rcx, %r10
	movq	%rdx, %r8
	andq	$7, %r10
	je	.LBB12_279
.LBB12_280:
	movzbl	(%r8), %eax
	incq	%r8
	xorq	%r9, %rax
	imulq	%r15, %rax
	movq	%rax, %r9
	decq	%r10
	jne	.LBB12_280
	jmp	.LBB12_281
.LBB12_277:
	movq	%r9, %rax
	jmp	.LBB12_284
.LBB12_279:
	movq	%r9, %rax
.LBB12_281:
	cmpq	$8, %rcx
	jb	.LBB12_284
	addq	%rcx, %rdx
.LBB12_283:
	movzbl	(%r8), %ecx
	xorq	%rax, %rcx
	imulq	%r15, %rcx
	movzbl	1(%r8), %eax
	xorq	%rcx, %rax
	imulq	%r15, %rax
	movzbl	2(%r8), %ecx
	xorq	%rax, %rcx
	imulq	%r15, %rcx
	movzbl	3(%r8), %eax
	xorq	%rcx, %rax
	imulq	%r15, %rax
	movzbl	4(%r8), %ecx
	xorq	%rax, %rcx
	imulq	%r15, %rcx
	movzbl	5(%r8), %eax
	xorq	%rcx, %rax
	imulq	%r15, %rax
	movzbl	6(%r8), %ecx
	xorq	%rax, %rcx
	imulq	%r15, %rcx
	movzbl	7(%r8), %eax
	addq	$8, %r8
	xorq	%rcx, %rax
	imulq	%r15, %rax
	cmpq	%rdx, %r8
	jne	.LBB12_283
.LBB12_284:
	movq	736(%rbp), %rbx
	movl	%ebx, %r9d
	shrl	$16, %r9d
	movl	%ebx, %r11d
	shrl	$24, %r11d
	movq	%rbx, %r8
	shrq	$32, %r8
	movq	%rbx, %rdx
	shrq	$40, %rdx
	movq	%rbx, %rcx
	shrq	$48, %rcx
	movq	%rbx, %r10
	shrq	$56, %r10
	movzbl	%bl, %r14d
	xorq	%r14, %rax
	imulq	%r15, %rax
	movzbl	%bh, %edi
	xorq	%rdi, %rax
	imulq	%r15, %rax
	movzbl	%r9b, %r9d
	xorq	%r9, %rax
	imulq	%r15, %rax
	xorq	%r11, %rax
	imulq	%r15, %rax
	movzbl	%r8b, %r8d
	xorq	%r8, %rax
	imulq	%r15, %rax
	movzbl	%dl, %edx
	xorq	%rdx, %rax
	imulq	%r15, %rax
	movzbl	%cl, %ecx
	xorq	%rcx, %rax
	imulq	%r15, %rax
	xorq	%r10, %rax
	imulq	%r15, %rax
	movq	%rax, 88(%rbp)
	movq	112(%rbp), %rsi
	xorq	%r14, %rsi
	imulq	%r15, %rsi
	movq	%rdi, -16(%rbp)
	xorq	%rdi, %rsi
	imulq	%r15, %rsi
	movq	%r9, -8(%rbp)
	xorq	%r9, %rsi
	imulq	%r15, %rsi
	movq	%r11, -24(%rbp)
	xorq	%r11, %rsi
	imulq	%r15, %rsi
	movq	%r8, (%rbp)
	xorq	%r8, %rsi
	imulq	%r15, %rsi
	movq	%rdx, 8(%rbp)
	xorq	%rdx, %rsi
	imulq	%r15, %rsi
	movq	%rcx, 16(%rbp)
	xorq	%rcx, %rsi
	imulq	%r15, %rsi
	movq	%r10, -32(%rbp)
	xorq	%r10, %rsi
	imulq	%r15, %rsi
	movq	%rsi, 112(%rbp)
	testq	%rbx, %rbx
	je	.LBB12_285
	movq	704(%rbp), %rax
	movq	32(%rax), %rbx
	movq	736(%rbp), %rax
	leaq	(,%rax,4), %r8
	xorl	%edx, %edx
	movq	%r8, 120(%rbp)
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rax, 360(%rbp)
	testq	%rax, %rax
	je	.LBB12_309
	cmpq	$8, 736(%rbp)
	setb	%al
	movq	360(%rbp), %rcx
	subq	%rbx, %rcx
	cmpq	$32, %rcx
	setb	%cl
	orb	%al, %cl
	je	.LBB12_289
	xorl	%eax, %eax
	movq	736(%rbp), %rdx
	movq	360(%rbp), %r9
	jmp	.LBB12_292
.LBB12_285:
	movq	$0, 648(%rbp)
	movq	$4, 656(%rbp)
	movq	$0, 664(%rbp)
	movl	$4, %eax
	movq	%rax, 360(%rbp)
	movq	$0, 120(%rbp)
	jmp	.LBB12_300
.LBB12_289:
	movq	736(%rbp), %rcx
	movq	%rcx, %rax
	movabsq	$2305843009213693944, %rdx
	andq	%rdx, %rax
	leaq	(,%rcx,4), %rcx
	andq	$-32, %rcx
	xorl	%edx, %edx
	movq	360(%rbp), %r9
.LBB12_290:
	movups	(%rbx,%rdx), %xmm0
	movdqu	16(%rbx,%rdx), %xmm1
	movups	%xmm0, (%r9,%rdx)
	movdqu	%xmm1, 16(%r9,%rdx)
	addq	$32, %rdx
	cmpq	%rdx, %rcx
	jne	.LBB12_290
	movq	736(%rbp), %rdx
	cmpq	%rax, %rdx
	je	.LBB12_297
.LBB12_292:
	movq	%rax, %rcx
	andq	$3, %rdx
	je	.LBB12_295
	movq	%rax, %rcx
.LBB12_294:
	movl	(%rbx,%rcx,4), %r8d
	movl	%r8d, (%r9,%rcx,4)
	incq	%rcx
	decq	%rdx
	jne	.LBB12_294
.LBB12_295:
	movq	736(%rbp), %rdx
	subq	%rdx, %rax
	cmpq	$-4, %rax
	ja	.LBB12_297
.LBB12_296:
	movl	(%rbx,%rcx,4), %eax
	movl	%eax, (%r9,%rcx,4)
	movl	4(%rbx,%rcx,4), %eax
	movl	%eax, 4(%r9,%rcx,4)
	movl	8(%rbx,%rcx,4), %eax
	movl	%eax, 8(%r9,%rcx,4)
	movl	12(%rbx,%rcx,4), %eax
	movl	%eax, 12(%r9,%rcx,4)
	addq	$4, %rcx
	cmpq	%rcx, %rdx
	jne	.LBB12_296
.LBB12_297:
	movq	%rdx, 648(%rbp)
	movq	%r9, 656(%rbp)
	movq	%rdx, 664(%rbp)
	xorl	%eax, %eax
	movq	120(%rbp), %r10
.LBB12_298:
	movl	(%r9,%rax), %edx
	movl	%edx, %ecx
	movzbl	%dl, %r8d
	movzbl	%dh, %ebx
	shrl	$16, %edx
	shrl	$24, %ecx
	xorq	%rsi, %r8
	imulq	%r15, %r8
	xorq	%r8, %rbx
	imulq	%r15, %rbx
	movzbl	%dl, %esi
	xorq	%rbx, %rsi
	imulq	%r15, %rsi
	xorq	%rcx, %rsi
	imulq	%r15, %rsi
	addq	$4, %rax
	cmpq	%rax, %r10
	jne	.LBB12_298
	movq	%rsi, 112(%rbp)
.LBB12_300:
	movq	736(%rbp), %rax
	leaq	12(,%rax,2), %r8
	xorl	%edx, %edx
	movq	%r8, 712(%rbp)
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rax, 680(%rbp)
	testq	%rax, %rax
	je	.LBB12_310
	movq	736(%rbp), %rdx
	leaq	5(%rdx), %rbx
	movl	$1, %ecx
	movq	680(%rbp), %r10
	movq	%r10, %rax
	cmpq	$11, %rdx
	jb	.LBB12_305
	movq	%rbx, %rdx
	movabsq	$4611686018427387888, %rax
	andq	%rax, %rdx
	leaq	(%r10,%rdx,2), %rax
	leaq	1(%rdx), %rcx
	leaq	(%rbx,%rbx), %r8
	andq	$-32, %r8
	xorl	%r9d, %r9d
.LBB12_303:
	movdqu	%xmm9, (%r10,%r9)
	movdqu	%xmm9, 16(%r10,%r9)
	addq	$32, %r9
	cmpq	%r9, %r8
	jne	.LBB12_303
	cmpq	%rdx, %rbx
	je	.LBB12_307
.LBB12_305:
	movq	736(%rbp), %rdx
	subq	%rcx, %rdx
	addq	$6, %rdx
.LBB12_306:
	movw	$-23206, (%rax)
	addq	$2, %rax
	decq	%rdx
	jne	.LBB12_306
.LBB12_307:
	movq	736(%rbp), %rcx
	leaq	6(%rcx), %rsi
	movw	$-23206, (%rax)
	movq	%rsi, 144(%rbp)
	movq	%r10, 152(%rbp)
	movq	%rsi, 160(%rbp)
	xorl	%edx, %edx
	movq	712(%rbp), %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rax, 696(%rbp)
	testq	%rax, %rax
	je	.LBB12_308
	movq	%rsi, 608(%rbp)
	movq	696(%rbp), %rcx
	movq	%rcx, 616(%rbp)
	movq	680(%rbp), %rdx
	movq	712(%rbp), %rdi
	movq	%rdi, %r8
	callq	memcpy
	movq	%rsi, 624(%rbp)
	xorl	%edx, %edx
	movq	%rdi, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rax, 392(%rbp)
	testq	%rax, %rax
	je	.LBB12_324
	movl	$1, %ecx
	movq	392(%rbp), %r10
	movq	%r10, %rax
	cmpq	$11, 736(%rbp)
	jb	.LBB12_320
	movq	%rbx, %rdx
	movabsq	$4611686018427387888, %rax
	andq	%rax, %rdx
	leaq	(%r10,%rdx,2), %rax
	leaq	1(%rdx), %rcx
	leaq	(%rbx,%rbx), %r8
	andq	$-32, %r8
	xorl	%r9d, %r9d
.LBB12_318:
	movdqu	%xmm9, (%r10,%r9)
	movdqu	%xmm9, 16(%r10,%r9)
	addq	$32, %r9
	cmpq	%r9, %r8
	jne	.LBB12_318
	cmpq	%rdx, %rbx
	je	.LBB12_322
.LBB12_320:
	movq	736(%rbp), %rdx
	subq	%rcx, %rdx
	addq	$6, %rdx
.LBB12_321:
	movw	$-23206, (%rax)
	addq	$2, %rax
	decq	%rdx
	jne	.LBB12_321
.LBB12_322:
	movw	$-23206, (%rax)
	movq	%rsi, 456(%rbp)
	movq	%r10, 464(%rbp)
	movq	%rsi, 472(%rbp)
	xorl	%edx, %edx
	movq	712(%rbp), %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rax, 728(%rbp)
	testq	%rax, %rax
	je	.LBB12_323
	movq	%rsi, 400(%rbp)
	movq	728(%rbp), %rdi
	movq	%rdi, 408(%rbp)
	movq	%rdi, %rcx
	movq	392(%rbp), %rbx
	movq	%rbx, %rdx
	movq	712(%rbp), %r8
	callq	memcpy
	movq	%rsi, 416(%rbp)
	movq	704(%rbp), %r12
	movq	32(%r12), %rcx
	movq	40(%r12), %rdx
	movq	680(%rbp), %r8
	addq	$6, %r8
	movq	736(%rbp), %r13
	movq	%r13, %r9
	callq	d014_baseline_i16
	movaps	%xmm0, %xmm6
	movq	32(%r12), %rcx
	movq	40(%r12), %rdx
	movq	696(%rbp), %rax
	leaq	6(%rax), %r8
	movq	%r8, 632(%rbp)
	movq	%r13, %r9
	callq	d014_candidate_i16
	movaps	%xmm0, %xmm7
	movq	32(%r12), %rcx
	movq	40(%r12), %rdx
	addq	$6, %rbx
	movq	%rbx, %r8
	movq	%r13, %r9
	callq	d014_baseline_u16
	movaps	%xmm0, %xmm8
	movq	32(%r12), %rcx
	movq	40(%r12), %rdx
	leaq	6(%rdi), %r8
	movq	%r13, %r9
	callq	d014_candidate_u16
	cmpq	$-1, 168(%rbp)
	je	.LBB12_331
	movq	40(%rbp), %rax
	xorb	$1, %al
	testb	$1, %al
	je	.LBB12_331
	cmpq	$0, 736(%rbp)
	je	.LBB12_331
	movq	632(%rbp), %rax
	xorb	$1, (%rax)
	movb	$1, %al
	movq	%rax, 40(%rbp)
.LBB12_331:
	movss	%xmm7, 76(%rbp)
	movss	%xmm6, 128(%rbp)
	movd	%xmm7, %ebx
	movd	%xmm6, %eax
	cmpl	%eax, %ebx
	jne	.LBB12_332
	movss	%xmm0, 72(%rbp)
	movss	%xmm8, 128(%rbp)
	movd	%xmm0, %ecx
	movd	%xmm8, %eax
	cmpl	%eax, %ecx
	jne	.LBB12_335
	movq	%rcx, %r12
	movq	696(%rbp), %rcx
	movq	680(%rbp), %rdx
	movq	712(%rbp), %r8
	callq	memcmp
	testl	%eax, %eax
	jne	.LBB12_337
	movq	728(%rbp), %rcx
	movq	392(%rbp), %rdx
	movq	712(%rbp), %r8
	callq	memcmp
	testl	%eax, %eax
	jne	.LBB12_748
	movq	704(%rbp), %rax
	addq	$48, %rax
	movq	%rax, 24(%rbp)
	movq	736(%rbp), %rax
	leaq	3(%rax), %r8
	movb	$1, %cl
	movq	352(%rbp), %rax
	xorl	%edx, %edx
	movq	696(%rbp), %r11
	movq	728(%rbp), %rdi
.LBB12_340:
	movl	%ecx, %r9d
	cmpq	$3, %rdx
	setb	%cl
	andb	%r9b, %cl
	cmpb	$1, %cl
	jne	.LBB12_342
	leaq	1(%rdx), %r9
	movq	%r8, %r10
	jmp	.LBB12_344
.LBB12_342:
	cmpq	%rsi, %r8
	jae	.LBB12_346
	leaq	1(%r8), %r10
	movq	%rdx, %r9
	movq	%r8, %rdx
.LBB12_344:
	movzwl	(%r11,%rdx,2), %r8d
	movw	%r8w, 128(%rbp)
	cmpl	$42330, %r8d
	jne	.LBB12_345
	cmpw	$-23206, (%rdi,%rdx,2)
	jne	.LBB12_384
	addq	$2, %rax
	movq	%r9, %rdx
	movq	%r10, %r8
	jmp	.LBB12_340
.LBB12_346:
	movq	%rax, 352(%rbp)
	movq	704(%rbp), %rax
	movq	40(%rax), %rcx
	movq	%rcx, 448(%rbp)
	testq	%rcx, %rcx
	je	.LBB12_347
	movq	704(%rbp), %rax
	movq	32(%rax), %r13
	movq	448(%rbp), %rax
	leaq	(,%rax,4), %rsi
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rax, 632(%rbp)
	testq	%rax, %rax
	je	.LBB12_363
	cmpq	$8, 448(%rbp)
	setb	%al
	movq	632(%rbp), %rcx
	subq	%r13, %rcx
	cmpq	$32, %rcx
	setb	%cl
	orb	%al, %cl
	je	.LBB12_355
	xorl	%eax, %eax
	jmp	.LBB12_358
.LBB12_347:
	movl	$4, %eax
	movq	%rax, 632(%rbp)
	jmp	.LBB12_348
.LBB12_355:
	movq	448(%rbp), %rax
	andq	$-8, %rax
	xorl	%ecx, %ecx
	movq	632(%rbp), %rdx
.LBB12_356:
	movups	(%r13,%rcx,4), %xmm0
	movdqu	16(%r13,%rcx,4), %xmm1
	movups	%xmm0, (%rdx,%rcx,4)
	movdqu	%xmm1, 16(%rdx,%rcx,4)
	addq	$8, %rcx
	cmpq	%rcx, %rax
	jne	.LBB12_356
	cmpq	%rax, 448(%rbp)
	je	.LBB12_348
.LBB12_358:
	movq	448(%rbp), %rdx
	movq	%rax, %rcx
	andq	$3, %rdx
	movq	632(%rbp), %r9
	je	.LBB12_361
	movq	%rax, %rcx
.LBB12_360:
	movl	(%r13,%rcx,4), %r8d
	movl	%r8d, (%r9,%rcx,4)
	incq	%rcx
	decq	%rdx
	jne	.LBB12_360
.LBB12_361:
	movq	448(%rbp), %rdx
	subq	%rdx, %rax
	cmpq	$-4, %rax
	ja	.LBB12_348
.LBB12_362:
	movl	(%r13,%rcx,4), %eax
	movl	%eax, (%r9,%rcx,4)
	movl	4(%r13,%rcx,4), %eax
	movl	%eax, 4(%r9,%rcx,4)
	movl	8(%r13,%rcx,4), %eax
	movl	%eax, 8(%r9,%rcx,4)
	movl	12(%r13,%rcx,4), %eax
	movl	%eax, 12(%r9,%rcx,4)
	addq	$4, %rcx
	cmpq	%rcx, %rdx
	jne	.LBB12_362
.LBB12_348:
	movq	448(%rbp), %rcx
	movq	%rcx, 176(%rbp)
	movq	632(%rbp), %rax
	movq	%rax, 184(%rbp)
	movq	%rcx, 192(%rbp)
	cmpq	%rcx, 736(%rbp)
	jne	.LBB12_351
	movq	360(%rbp), %rcx
	movq	632(%rbp), %rdx
	movq	120(%rbp), %r8
	callq	memcmp
	testl	%eax, %eax
	jne	.LBB12_350
	cmpq	$0, 736(%rbp)
	je	.LBB12_366
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	632(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_366:
	xorq	96(%rbp), %r14
	imulq	%r15, %r14
	xorq	-16(%rbp), %r14
	imulq	%r15, %r14
	xorq	-8(%rbp), %r14
	imulq	%r15, %r14
	xorq	-24(%rbp), %r14
	imulq	%r15, %r14
	xorq	(%rbp), %r14
	imulq	%r15, %r14
	xorq	8(%rbp), %r14
	imulq	%r15, %r14
	xorq	16(%rbp), %r14
	imulq	%r15, %r14
	xorq	-32(%rbp), %r14
	imulq	%r15, %r14
	testb	$1, 736(%rbp)
	jne	.LBB12_371
	movq	696(%rbp), %rax
	jmp	.LBB12_372
.LBB12_371:
	movq	696(%rbp), %rdx
	movzwl	(%rdx), %eax
	movzbl	%al, %ecx
	shrl	$8, %eax
	xorq	%rcx, %r14
	imulq	%r15, %r14
	xorq	%rax, %r14
	imulq	%r15, %r14
	leaq	2(%rdx), %rax
.LBB12_372:
	movq	696(%rbp), %rcx
	addq	712(%rbp), %rcx
.LBB12_373:
	movzwl	(%rax), %edx
	movzbl	%dl, %r8d
	shrl	$8, %edx
	xorq	%r14, %r8
	imulq	%r15, %r8
	xorq	%rdx, %r8
	imulq	%r15, %r8
	movzwl	2(%rax), %edx
	movzbl	%dl, %r14d
	shrl	$8, %edx
	xorq	%r8, %r14
	imulq	%r15, %r14
	xorq	%rdx, %r14
	imulq	%r15, %r14
	addq	$4, %rax
	cmpq	%rcx, %rax
	jne	.LBB12_373
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	696(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
	movzbl	%bl, %eax
	xorq	%rax, %r14
	imulq	%r15, %r14
	movzbl	%bh, %eax
	xorq	%r14, %rax
	imulq	%r15, %rax
	movl	%ebx, %ecx
	shrl	$16, %ecx
	movzbl	%cl, %ecx
	xorq	%rax, %rcx
	imulq	%r15, %rcx
	shrl	$24, %ebx
	xorq	%rcx, %rbx
	imulq	%r15, %rbx
	testb	$1, 736(%rbp)
	jne	.LBB12_376
	movq	728(%rbp), %rax
	jmp	.LBB12_377
.LBB12_376:
	movq	728(%rbp), %rdx
	movzwl	(%rdx), %eax
	movzbl	%al, %ecx
	shrl	$8, %eax
	xorq	%rcx, %rbx
	imulq	%r15, %rbx
	xorq	%rax, %rbx
	imulq	%r15, %rbx
	leaq	2(%rdx), %rax
.LBB12_377:
	movq	728(%rbp), %rcx
	addq	712(%rbp), %rcx
.LBB12_378:
	movzwl	(%rax), %edx
	movzbl	%dl, %r8d
	shrl	$8, %edx
	xorq	%rbx, %r8
	imulq	%r15, %r8
	xorq	%rdx, %r8
	imulq	%r15, %r8
	movzwl	2(%rax), %edx
	movzbl	%dl, %ebx
	shrl	$8, %edx
	xorq	%r8, %rbx
	imulq	%r15, %rbx
	xorq	%rdx, %rbx
	imulq	%r15, %rbx
	addq	$4, %rax
	cmpq	%rcx, %rax
	jne	.LBB12_378
	movq	__imp_GetProcessHeap(%rip), %rsi
	callq	*%rsi
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	728(%rbp), %r8
	movq	__imp_HeapFree(%rip), %rdi
	callq	*%rdi
	movq	%r12, %rdx
	movzbl	%dl, %eax
	xorq	%rax, %rbx
	imulq	%r15, %rbx
	movzbl	%dh, %eax
	xorq	%rbx, %rax
	imulq	%r15, %rax
	movl	%edx, %ecx
	shrl	$16, %ecx
	movzbl	%cl, %ecx
	xorq	%rax, %rcx
	imulq	%r15, %rcx
	shrl	$24, %edx
	xorq	%rcx, %rdx
	imulq	%r15, %rdx
	movq	%rdx, 96(%rbp)
	callq	*%rsi
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	392(%rbp), %r8
	callq	*%rdi
	callq	*%rsi
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	680(%rbp), %r8
	callq	*%rdi
	cmpq	$0, 736(%rbp)
	je	.LBB12_381
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	360(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
	jmp	.LBB12_381
.LBB12_246:
	xorl	%eax, %eax
	jmp	.LBB12_260
.LBB12_345:
	movq	%rax, 352(%rbp)
	movq	704(%rbp), %rax
	movq	%rax, 176(%rbp)
	leaq	_RNvXsq_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt(%rip), %rax
	movq	%rax, 184(%rbp)
.Ltmp98:
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.38(%rip), %rdx
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.39(%rip), %r9
	leaq	128(%rbp), %rcx
	leaq	176(%rbp), %r8
	callq	_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedttECs2i4to50FHNk_9prototype
	nop
.Ltmp99:
	jmp	.LBB12_39
.LBB12_384:
	leaq	(%rdi,%rdx,2), %rcx
	movq	%rax, 352(%rbp)
	movq	704(%rbp), %rax
	movq	%rax, 176(%rbp)
	leaq	_RNvXsq_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt(%rip), %rax
	movq	%rax, 184(%rbp)
.Ltmp100:
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.36(%rip), %rdx
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.37(%rip), %r9
	leaq	176(%rbp), %r8
	callq	_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedttECs2i4to50FHNk_9prototype
	nop
.Ltmp101:
	jmp	.LBB12_39
.LBB12_259:
	movq	80(%rbp), %rax
	addq	%rax, %rax
.LBB12_260:
	movq	640(%rbp), %rcx
	movq	%rcx, 608(%rbp)
	movq	%rax, 456(%rbp)
	leaq	(%rcx,%rcx), %rax
	movq	%rax, 400(%rbp)
	leaq	-40(%rbp), %rax
	movq	%rax, 176(%rbp)
	leaq	_RNvXsi_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impjNtB9_7Display3fmt(%rip), %rcx
	movq	%rcx, 184(%rbp)
	leaq	608(%rbp), %rax
	movq	%rax, 192(%rbp)
	movq	%rcx, 200(%rbp)
	leaq	80(%rbp), %rax
	movq	%rax, 208(%rbp)
	movq	%rcx, 216(%rbp)
	leaq	456(%rbp), %rax
	movq	%rax, 224(%rbp)
	movq	%rcx, 232(%rbp)
	leaq	400(%rbp), %rax
	movq	%rax, 240(%rbp)
	movq	%rcx, 248(%rbp)
	leaq	352(%rbp), %rax
	movq	%rax, 256(%rbp)
	movq	%rcx, 264(%rbp)
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.40(%rip), %rax
	movq	%rax, 272(%rbp)
	leaq	_RNvXsC_NtNtCs8xEFJqa6dYS_4core3fmt3numyNtB7_8LowerHex3fmt(%rip), %rax
	movq	%rax, 280(%rbp)
	leaq	88(%rbp), %rcx
	movq	%rcx, 288(%rbp)
	movq	%rax, 296(%rbp)
	leaq	112(%rbp), %rcx
	movq	%rcx, 304(%rbp)
	movq	%rax, 312(%rbp)
	leaq	96(%rbp), %rcx
	movq	%rcx, 320(%rbp)
	movq	%rax, 328(%rbp)
.Ltmp110:
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.41(%rip), %rcx
	leaq	176(%rbp), %rdx
	callq	_RNvNtNtCse0R8cuyqEa_3std2io5stdio6__print
	nop
.Ltmp111:
	cmpq	$0, 640(%rbp)
	je	.LBB12_268
	movq	104(%rbp), %rax
	leaq	32(%rax), %rdi
	jmp	.LBB12_263
.LBB12_267:
	addq	$48, %rdi
	decq	640(%rbp)
	je	.LBB12_268
.LBB12_263:
	cmpq	$0, -32(%rdi)
	je	.LBB12_265
	movq	-24(%rdi), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_265:
	cmpq	$0, -8(%rdi)
	je	.LBB12_267
	movq	(%rdi), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	jmp	.LBB12_267
.LBB12_268:
	cmpq	$0, 368(%rbp)
	je	.LBB12_270
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	104(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_270:
	leaq	176(%rbp), %rdi
	movq	%rdi, %rcx
	callq	_RNvNtCse0R8cuyqEa_3std3env7args_os
	leaq	480(%rbp), %r14
	movabsq	$3271424703783251245, %rbx
	jmp	.LBB12_271
.LBB12_469:
	testb	%r15b, %r15b
	jne	.LBB12_470
.LBB12_271:
.Ltmp112:
	movq	%r14, %rcx
	movq	%rdi, %rdx
	callq	_RNvXsc_NtCse0R8cuyqEa_3std3envNtB5_4ArgsNtNtNtNtCs8xEFJqa6dYS_4core4iter6traits8iterator8Iterator4next
	nop
.Ltmp113:
	movq	480(%rbp), %rax
	cmpq	$-1, %rax
	je	.LBB12_478
	movq	488(%rbp), %rsi
	cmpq	$12, 496(%rbp)
	jne	.LBB12_274
	movq	(%rsi), %rcx
	xorq	%rbx, %rcx
	movl	8(%rsi), %edx
	xorq	$2037149295, %rdx
	orq	%rcx, %rdx
	sete	%r15b
	jmp	.LBB12_467
.LBB12_274:
	xorl	%r15d, %r15d
.LBB12_467:
	testq	%rax, %rax
	je	.LBB12_469
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	jmp	.LBB12_469
.LBB12_478:
	movq	184(%rbp), %rdi
	movq	200(%rbp), %rbx
	subq	%rdi, %rbx
	je	.LBB12_483
	shrq	$5, %rbx
	addq	$8, %rdi
	jmp	.LBB12_480
.LBB12_482:
	addq	$32, %rdi
	decq	%rbx
	je	.LBB12_483
.LBB12_480:
	cmpq	$0, -8(%rdi)
	je	.LBB12_482
	movq	(%rdi), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	jmp	.LBB12_482
.LBB12_483:
	cmpq	$0, 192(%rbp)
	je	.LBB12_485
	movq	176(%rbp), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_485:
	movq	$0, 480(%rbp)
	movq	$14, 488(%rbp)
	movq	$512, 496(%rbp)
	movq	$514, 504(%rbp)
	movq	$638, 512(%rbp)
	movq	$682, 520(%rbp)
	movq	$768, 528(%rbp)
	movq	$771, 536(%rbp)
	movq	$957, 544(%rbp)
	movq	$1023, 552(%rbp)
	movq	$1024, 560(%rbp)
	movq	$1366, 568(%rbp)
	movq	$1536, 576(%rbp)
	movq	$2048, 584(%rbp)
	movq	$2049, 592(%rbp)
	movq	$2732, 600(%rbp)
	movabsq	$6840158756896394953, %rax
	movq	%rax, 696(%rbp)
	movq	$0, 640(%rbp)
	leaq	_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtReNtB6_7Display3fmtCs2i4to50FHNk_9prototype(%rip), %r14
	movaps	__xmm@7fffffff7fffffff7fffffff7fffffff(%rip), %xmm6
	movss	__real@3c800000(%rip), %xmm7
	movq	$0, 168(%rbp)
.LBB12_486:
	movq	168(%rbp), %rcx
	movq	496(%rbp,%rcx,8), %rax
	incq	%rcx
	movq	%rcx, 168(%rbp)
	movq	%rax, 368(%rbp)
	movq	$0, 400(%rbp)
	movq	$2, 408(%rbp)
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.7(%rip), %rax
	movq	%rax, 416(%rbp)
	movq	$13, 424(%rbp)
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.49(%rip), %rax
	movq	%rax, 432(%rbp)
	movq	$6, 440(%rbp)
	movq	$0, 680(%rbp)
.LBB12_487:
	movq	680(%rbp), %rax
	shlq	$4, %rax
	leaq	416(%rbp), %rcx
	movups	(%rcx,%rax), %xmm0
	movups	%xmm0, 48(%rbp)
	movl	$192, %r8d
	xorl	%edx, %edx
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rax, 728(%rbp)
	testq	%rax, %rax
	je	.LBB12_497
	incq	680(%rbp)
	movq	$0, 736(%rbp)
.LBB12_489:
	movq	368(%rbp), %rbx
	leaq	(,%rbx,4), %rsi
	movq	%rbx, %rax
	shrq	$62, %rax
	setne	%al
	movabsq	$9223372036854775804, %rcx
	cmpq	%rcx, %rsi
	seta	%cl
	orb	%al, %cl
	jne	.LBB12_506
	testq	%rsi, %rsi
	je	.LBB12_491
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rbx, %rcx
	testq	%rax, %rax
	jne	.LBB12_492
	jmp	.LBB12_505
.LBB12_491:
	movl	$4, %eax
	xorl	%ecx, %ecx
.LBB12_492:
	testq	%rbx, %rbx
	je	.LBB12_509
	xorl	%edx, %edx
	jmp	.LBB12_494
.LBB12_507:
	movabsq	$-7046029254386353131, %r8
	movq	696(%rbp), %r9
	addq	%r8, %r9
	movq	%r9, %r8
	shrq	$30, %r8
	movq	%r9, 696(%rbp)
	xorq	%r9, %r8
	movabsq	$-4658895280553007687, %r9
	imulq	%r9, %r8
	movq	%r8, %r9
	shrq	$27, %r9
	xorq	%r8, %r9
	movabsq	$-7723592293110705685, %r8
	imulq	%r8, %r9
	movq	%r9, %r8
	shrq	$63, %r8
	shrq	$32, %r9
	xorl	%r9d, %r8d
	imulq	$1407367847, %r8, %r9
	shrq	$48, %r9
	imull	$200001, %r9d, %r9d
	negl	%r9d
	addl	%r9d, %r8d
	addl	$-100000, %r8d
	xorps	%xmm0, %xmm0
	cvtsi2ss	%r8d, %xmm0
	mulss	%xmm7, %xmm0
	movss	%xmm0, (%rax,%rdx,4)
	incq	%rdx
	cmpq	%rdx, %rbx
	je	.LBB12_509
.LBB12_494:
	cmpq	$13, 56(%rbp)
	jne	.LBB12_507
	movq	48(%rbp), %r8
	movq	(%r8), %r9
	movabsq	$7311146993788874608, %r10
	xorq	%r10, %r9
	movq	5(%r8), %r8
	movabsq	$8030592661815916137, %r10
	xorq	%r10, %r8
	orq	%r9, %r8
	jne	.LBB12_507
	xorps	%xmm0, %xmm0
	movss	%xmm0, (%rax,%rdx,4)
	incq	%rdx
	cmpq	%rdx, %rbx
	jne	.LBB12_494
.LBB12_509:
	movq	736(%rbp), %r9
	leaq	(%r9,%r9,2), %rdx
	incq	%r9
	movq	728(%rbp), %r8
	movq	%rcx, (%r8,%rdx,8)
	movq	%rax, 8(%r8,%rdx,8)
	movq	%rbx, 16(%r8,%rdx,8)
	movq	%r9, 736(%rbp)
	cmpq	$8, %r9
	jne	.LBB12_489
	movq	368(%rbp), %rcx
	testq	%rcx, %rcx
	je	.LBB12_511
	cmpq	$2000000, %rcx
	ja	.LBB12_530
	movl	$2000000, %eax
	xorl	%edx, %edx
	divl	%ecx
	jmp	.LBB12_532
.LBB12_530:
	xorl	%eax, %eax
.LBB12_532:
	cmpq	$1025, %rax
	movl	$1024, %ecx
	cmovbq	%rcx, %rax
	movq	%rax, -64(%rbp)
	movq	$0, 608(%rbp)
	movq	$2, 616(%rbp)
	movw	$1, 624(%rbp)
	movq	$0, 704(%rbp)
	jmp	.LBB12_533
.LBB12_704:
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	736(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
	cmpq	$2, 704(%rbp)
	movl	$1, %eax
	movq	%rax, 704(%rbp)
	je	.LBB12_658
.LBB12_533:
	movq	704(%rbp), %rax
	movzbl	624(%rbp,%rax), %esi
	movl	$192, %r8d
	xorl	%edx, %edx
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rax, 736(%rbp)
	testq	%rax, %rax
	je	.LBB12_534
	movq	$8, 176(%rbp)
	movq	736(%rbp), %rax
	movq	%rax, 184(%rbp)
	movq	728(%rbp), %rax
	movq	16(%rax), %rbx
	movl	$4, %edi
	movl	$4, %r12d
	testq	%rbx, %rbx
	je	.LBB12_550
	movq	728(%rbp), %rax
	movq	8(%rax), %r13
	leaq	(,%rbx,4), %r15
	xorl	%edx, %edx
	movq	%r15, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	je	.LBB12_554
	movq	%rax, %r12
	testb	%sil, %sil
	je	.LBB12_539
	movq	%r12, %rcx
	movq	%r13, %rdx
	movq	%r15, %r8
	callq	memcpy
	jmp	.LBB12_550
.LBB12_539:
	cmpq	$8, %rbx
	setb	%al
	movq	%r12, %rcx
	subq	%r13, %rcx
	cmpq	$32, %rcx
	setb	%cl
	orb	%al, %cl
	je	.LBB12_541
	xorl	%eax, %eax
	jmp	.LBB12_544
.LBB12_541:
	movq	%rbx, %rax
	andq	$-8, %rax
	xorl	%ecx, %ecx
.LBB12_542:
	movups	(%r13,%rcx,4), %xmm0
	movups	16(%r13,%rcx,4), %xmm1
	andps	%xmm6, %xmm0
	andps	%xmm6, %xmm1
	movups	%xmm0, (%r12,%rcx,4)
	movups	%xmm1, 16(%r12,%rcx,4)
	addq	$8, %rcx
	cmpq	%rcx, %rax
	jne	.LBB12_542
	cmpq	%rax, %rbx
	je	.LBB12_550
.LBB12_544:
	movq	%rbx, %rdx
	movq	%rax, %rcx
	andq	$3, %rdx
	je	.LBB12_547
	movq	%rax, %rcx
.LBB12_546:
	movl	(%r13,%rcx,4), %r8d
	movl	$2147483647, %r9d
	andl	%r9d, %r8d
	movl	%r8d, (%r12,%rcx,4)
	incq	%rcx
	decq	%rdx
	jne	.LBB12_546
.LBB12_547:
	subq	%rbx, %rax
	cmpq	$-4, %rax
	ja	.LBB12_550
.LBB12_548:
	movl	(%r13,%rcx,4), %eax
	movl	$2147483647, %edx
	andl	%edx, %eax
	movl	%eax, (%r12,%rcx,4)
	movl	4(%r13,%rcx,4), %eax
	andl	%edx, %eax
	movl	%eax, 4(%r12,%rcx,4)
	movl	8(%r13,%rcx,4), %eax
	andl	%edx, %eax
	movl	%eax, 8(%r12,%rcx,4)
	movl	12(%r13,%rcx,4), %eax
	andl	%edx, %eax
	movl	%eax, 12(%r12,%rcx,4)
	addq	$4, %rcx
	cmpq	%rcx, %rbx
	jne	.LBB12_548
.LBB12_550:
	movq	736(%rbp), %rax
	movq	%rbx, (%rax)
	movq	%r12, 8(%rax)
	movq	%rbx, 16(%rax)
	movq	728(%rbp), %rax
	movq	40(%rax), %rbx
	testq	%rbx, %rbx
	je	.LBB12_567
	movq	728(%rbp), %rax
	movq	32(%rax), %r12
	leaq	(,%rbx,4), %r15
	xorl	%edx, %edx
	movq	%r15, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	je	.LBB12_552
	movq	%rax, %rdi
	testb	%sil, %sil
	je	.LBB12_556
	movq	%rdi, %rcx
	movq	%r12, %rdx
	movq	%r15, %r8
	callq	memcpy
	jmp	.LBB12_567
.LBB12_556:
	cmpq	$8, %rbx
	setb	%al
	movq	%rdi, %rcx
	subq	%r12, %rcx
	cmpq	$32, %rcx
	setb	%cl
	orb	%al, %cl
	je	.LBB12_558
	xorl	%eax, %eax
	jmp	.LBB12_561
.LBB12_558:
	movq	%rbx, %rax
	andq	$-8, %rax
	xorl	%ecx, %ecx
.LBB12_559:
	movups	(%r12,%rcx,4), %xmm0
	movups	16(%r12,%rcx,4), %xmm1
	andps	%xmm6, %xmm0
	andps	%xmm6, %xmm1
	movups	%xmm0, (%rdi,%rcx,4)
	movups	%xmm1, 16(%rdi,%rcx,4)
	addq	$8, %rcx
	cmpq	%rcx, %rax
	jne	.LBB12_559
	cmpq	%rax, %rbx
	je	.LBB12_567
.LBB12_561:
	movq	%rbx, %rdx
	movq	%rax, %rcx
	andq	$3, %rdx
	je	.LBB12_564
	movq	%rax, %rcx
.LBB12_563:
	movl	(%r12,%rcx,4), %r8d
	movl	$2147483647, %r9d
	andl	%r9d, %r8d
	movl	%r8d, (%rdi,%rcx,4)
	incq	%rcx
	decq	%rdx
	jne	.LBB12_563
.LBB12_564:
	subq	%rbx, %rax
	cmpq	$-4, %rax
	ja	.LBB12_567
.LBB12_565:
	movl	(%r12,%rcx,4), %eax
	movl	$2147483647, %edx
	andl	%edx, %eax
	movl	%eax, (%rdi,%rcx,4)
	movl	4(%r12,%rcx,4), %eax
	andl	%edx, %eax
	movl	%eax, 4(%rdi,%rcx,4)
	movl	8(%r12,%rcx,4), %eax
	andl	%edx, %eax
	movl	%eax, 8(%rdi,%rcx,4)
	movl	12(%r12,%rcx,4), %eax
	andl	%edx, %eax
	movl	%eax, 12(%rdi,%rcx,4)
	addq	$4, %rcx
	cmpq	%rcx, %rbx
	jne	.LBB12_565
.LBB12_567:
	movq	736(%rbp), %rax
	movq	%rbx, 24(%rax)
	movq	%rdi, 32(%rax)
	movq	%rbx, 40(%rax)
	movq	728(%rbp), %rax
	movq	64(%rax), %rbx
	movl	$4, %edi
	movl	$4, %r12d
	testq	%rbx, %rbx
	je	.LBB12_582
	movq	728(%rbp), %rax
	movq	56(%rax), %r13
	leaq	(,%rbx,4), %r15
	xorl	%edx, %edx
	movq	%r15, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	je	.LBB12_569
	movq	%rax, %r12
	testb	%sil, %sil
	je	.LBB12_571
	movq	%r12, %rcx
	movq	%r13, %rdx
	movq	%r15, %r8
	callq	memcpy
	jmp	.LBB12_582
.LBB12_571:
	cmpq	$8, %rbx
	setb	%al
	movq	%r12, %rcx
	subq	%r13, %rcx
	cmpq	$32, %rcx
	setb	%cl
	orb	%al, %cl
	je	.LBB12_573
	xorl	%eax, %eax
	jmp	.LBB12_576
.LBB12_573:
	movq	%rbx, %rax
	andq	$-8, %rax
	xorl	%ecx, %ecx
.LBB12_574:
	movups	(%r13,%rcx,4), %xmm0
	movups	16(%r13,%rcx,4), %xmm1
	andps	%xmm6, %xmm0
	andps	%xmm6, %xmm1
	movups	%xmm0, (%r12,%rcx,4)
	movups	%xmm1, 16(%r12,%rcx,4)
	addq	$8, %rcx
	cmpq	%rcx, %rax
	jne	.LBB12_574
	cmpq	%rax, %rbx
	je	.LBB12_582
.LBB12_576:
	movq	%rbx, %rdx
	movq	%rax, %rcx
	andq	$3, %rdx
	je	.LBB12_579
	movq	%rax, %rcx
.LBB12_578:
	movl	(%r13,%rcx,4), %r8d
	movl	$2147483647, %r9d
	andl	%r9d, %r8d
	movl	%r8d, (%r12,%rcx,4)
	incq	%rcx
	decq	%rdx
	jne	.LBB12_578
.LBB12_579:
	subq	%rbx, %rax
	cmpq	$-4, %rax
	ja	.LBB12_582
.LBB12_580:
	movl	(%r13,%rcx,4), %eax
	movl	$2147483647, %edx
	andl	%edx, %eax
	movl	%eax, (%r12,%rcx,4)
	movl	4(%r13,%rcx,4), %eax
	andl	%edx, %eax
	movl	%eax, 4(%r12,%rcx,4)
	movl	8(%r13,%rcx,4), %eax
	andl	%edx, %eax
	movl	%eax, 8(%r12,%rcx,4)
	movl	12(%r13,%rcx,4), %eax
	andl	%edx, %eax
	movl	%eax, 12(%r12,%rcx,4)
	addq	$4, %rcx
	cmpq	%rcx, %rbx
	jne	.LBB12_580
.LBB12_582:
	movq	736(%rbp), %rax
	movq	%rbx, 48(%rax)
	movq	%r12, 56(%rax)
	movq	%rbx, 64(%rax)
	movq	728(%rbp), %rax
	movq	88(%rax), %rbx
	testq	%rbx, %rbx
	je	.LBB12_597
	movq	728(%rbp), %rax
	movq	80(%rax), %r12
	leaq	(,%rbx,4), %r15
	xorl	%edx, %edx
	movq	%r15, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	je	.LBB12_584
	movq	%rax, %rdi
	testb	%sil, %sil
	je	.LBB12_586
	movq	%rdi, %rcx
	movq	%r12, %rdx
	movq	%r15, %r8
	callq	memcpy
	jmp	.LBB12_597
.LBB12_586:
	cmpq	$8, %rbx
	setb	%al
	movq	%rdi, %rcx
	subq	%r12, %rcx
	cmpq	$32, %rcx
	setb	%cl
	orb	%al, %cl
	je	.LBB12_588
	xorl	%eax, %eax
	jmp	.LBB12_591
.LBB12_588:
	movq	%rbx, %rax
	andq	$-8, %rax
	xorl	%ecx, %ecx
.LBB12_589:
	movups	(%r12,%rcx,4), %xmm0
	movups	16(%r12,%rcx,4), %xmm1
	andps	%xmm6, %xmm0
	andps	%xmm6, %xmm1
	movups	%xmm0, (%rdi,%rcx,4)
	movups	%xmm1, 16(%rdi,%rcx,4)
	addq	$8, %rcx
	cmpq	%rcx, %rax
	jne	.LBB12_589
	cmpq	%rax, %rbx
	je	.LBB12_597
.LBB12_591:
	movq	%rbx, %rdx
	movq	%rax, %rcx
	andq	$3, %rdx
	je	.LBB12_594
	movq	%rax, %rcx
.LBB12_593:
	movl	(%r12,%rcx,4), %r8d
	movl	$2147483647, %r9d
	andl	%r9d, %r8d
	movl	%r8d, (%rdi,%rcx,4)
	incq	%rcx
	decq	%rdx
	jne	.LBB12_593
.LBB12_594:
	subq	%rbx, %rax
	cmpq	$-4, %rax
	ja	.LBB12_597
.LBB12_595:
	movl	(%r12,%rcx,4), %eax
	movl	$2147483647, %edx
	andl	%edx, %eax
	movl	%eax, (%rdi,%rcx,4)
	movl	4(%r12,%rcx,4), %eax
	andl	%edx, %eax
	movl	%eax, 4(%rdi,%rcx,4)
	movl	8(%r12,%rcx,4), %eax
	andl	%edx, %eax
	movl	%eax, 8(%rdi,%rcx,4)
	movl	12(%r12,%rcx,4), %eax
	andl	%edx, %eax
	movl	%eax, 12(%rdi,%rcx,4)
	addq	$4, %rcx
	cmpq	%rcx, %rbx
	jne	.LBB12_595
.LBB12_597:
	movq	736(%rbp), %rax
	movq	%rbx, 72(%rax)
	movq	%rdi, 80(%rax)
	movq	%rbx, 88(%rax)
	movq	728(%rbp), %rax
	movq	112(%rax), %rbx
	movl	$4, %edi
	movl	$4, %r12d
	testq	%rbx, %rbx
	je	.LBB12_612
	movq	728(%rbp), %rax
	movq	104(%rax), %r13
	leaq	(,%rbx,4), %r15
	xorl	%edx, %edx
	movq	%r15, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	je	.LBB12_599
	movq	%rax, %r12
	testb	%sil, %sil
	je	.LBB12_601
	movq	%r12, %rcx
	movq	%r13, %rdx
	movq	%r15, %r8
	callq	memcpy
	jmp	.LBB12_612
.LBB12_601:
	cmpq	$8, %rbx
	setb	%al
	movq	%r12, %rcx
	subq	%r13, %rcx
	cmpq	$32, %rcx
	setb	%cl
	orb	%al, %cl
	je	.LBB12_603
	xorl	%eax, %eax
	jmp	.LBB12_606
.LBB12_603:
	movq	%rbx, %rax
	andq	$-8, %rax
	xorl	%ecx, %ecx
.LBB12_604:
	movups	(%r13,%rcx,4), %xmm0
	movups	16(%r13,%rcx,4), %xmm1
	andps	%xmm6, %xmm0
	andps	%xmm6, %xmm1
	movups	%xmm0, (%r12,%rcx,4)
	movups	%xmm1, 16(%r12,%rcx,4)
	addq	$8, %rcx
	cmpq	%rcx, %rax
	jne	.LBB12_604
	cmpq	%rax, %rbx
	je	.LBB12_612
.LBB12_606:
	movq	%rbx, %rdx
	movq	%rax, %rcx
	andq	$3, %rdx
	je	.LBB12_609
	movq	%rax, %rcx
.LBB12_608:
	movl	(%r13,%rcx,4), %r8d
	movl	$2147483647, %r9d
	andl	%r9d, %r8d
	movl	%r8d, (%r12,%rcx,4)
	incq	%rcx
	decq	%rdx
	jne	.LBB12_608
.LBB12_609:
	subq	%rbx, %rax
	cmpq	$-4, %rax
	ja	.LBB12_612
.LBB12_610:
	movl	(%r13,%rcx,4), %eax
	movl	$2147483647, %edx
	andl	%edx, %eax
	movl	%eax, (%r12,%rcx,4)
	movl	4(%r13,%rcx,4), %eax
	andl	%edx, %eax
	movl	%eax, 4(%r12,%rcx,4)
	movl	8(%r13,%rcx,4), %eax
	andl	%edx, %eax
	movl	%eax, 8(%r12,%rcx,4)
	movl	12(%r13,%rcx,4), %eax
	andl	%edx, %eax
	movl	%eax, 12(%r12,%rcx,4)
	addq	$4, %rcx
	cmpq	%rcx, %rbx
	jne	.LBB12_610
.LBB12_612:
	movq	736(%rbp), %rax
	movq	%rbx, 96(%rax)
	movq	%r12, 104(%rax)
	movq	%rbx, 112(%rax)
	movq	728(%rbp), %rax
	movq	136(%rax), %rbx
	testq	%rbx, %rbx
	je	.LBB12_627
	movq	728(%rbp), %rax
	movq	128(%rax), %r12
	leaq	(,%rbx,4), %r15
	xorl	%edx, %edx
	movq	%r15, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	je	.LBB12_614
	movq	%rax, %rdi
	testb	%sil, %sil
	je	.LBB12_616
	movq	%rdi, %rcx
	movq	%r12, %rdx
	movq	%r15, %r8
	callq	memcpy
	jmp	.LBB12_627
.LBB12_616:
	cmpq	$8, %rbx
	setb	%al
	movq	%rdi, %rcx
	subq	%r12, %rcx
	cmpq	$32, %rcx
	setb	%cl
	orb	%al, %cl
	je	.LBB12_618
	xorl	%eax, %eax
	jmp	.LBB12_621
.LBB12_618:
	movq	%rbx, %rax
	andq	$-8, %rax
	xorl	%ecx, %ecx
.LBB12_619:
	movups	(%r12,%rcx,4), %xmm0
	movups	16(%r12,%rcx,4), %xmm1
	andps	%xmm6, %xmm0
	andps	%xmm6, %xmm1
	movups	%xmm0, (%rdi,%rcx,4)
	movups	%xmm1, 16(%rdi,%rcx,4)
	addq	$8, %rcx
	cmpq	%rcx, %rax
	jne	.LBB12_619
	cmpq	%rax, %rbx
	je	.LBB12_627
.LBB12_621:
	movq	%rbx, %rdx
	movq	%rax, %rcx
	andq	$3, %rdx
	je	.LBB12_624
	movq	%rax, %rcx
.LBB12_623:
	movl	(%r12,%rcx,4), %r8d
	movl	$2147483647, %r9d
	andl	%r9d, %r8d
	movl	%r8d, (%rdi,%rcx,4)
	incq	%rcx
	decq	%rdx
	jne	.LBB12_623
.LBB12_624:
	subq	%rbx, %rax
	cmpq	$-4, %rax
	ja	.LBB12_627
.LBB12_625:
	movl	(%r12,%rcx,4), %eax
	movl	$2147483647, %edx
	andl	%edx, %eax
	movl	%eax, (%rdi,%rcx,4)
	movl	4(%r12,%rcx,4), %eax
	andl	%edx, %eax
	movl	%eax, 4(%rdi,%rcx,4)
	movl	8(%r12,%rcx,4), %eax
	andl	%edx, %eax
	movl	%eax, 8(%rdi,%rcx,4)
	movl	12(%r12,%rcx,4), %eax
	andl	%edx, %eax
	movl	%eax, 12(%rdi,%rcx,4)
	addq	$4, %rcx
	cmpq	%rcx, %rbx
	jne	.LBB12_625
.LBB12_627:
	movq	736(%rbp), %rax
	movq	%rbx, 120(%rax)
	movq	%rdi, 128(%rax)
	movq	%rbx, 136(%rax)
	movq	728(%rbp), %rax
	movq	160(%rax), %rbx
	testq	%rbx, %rbx
	je	.LBB12_628
	movq	728(%rbp), %rax
	movq	152(%rax), %r12
	leaq	(,%rbx,4), %r15
	xorl	%edx, %edx
	movq	%r15, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	je	.LBB12_630
	movq	%rax, %rdi
	testb	%sil, %sil
	je	.LBB12_632
	movq	%rdi, %rcx
	movq	%r12, %rdx
	movq	%r15, %r8
	callq	memcpy
	jmp	.LBB12_643
.LBB12_628:
	movl	$4, %edi
	jmp	.LBB12_643
.LBB12_632:
	cmpq	$8, %rbx
	setb	%al
	movq	%rdi, %rcx
	subq	%r12, %rcx
	cmpq	$32, %rcx
	setb	%cl
	orb	%al, %cl
	je	.LBB12_634
	xorl	%eax, %eax
	jmp	.LBB12_637
.LBB12_634:
	movq	%rbx, %rax
	andq	$-8, %rax
	xorl	%ecx, %ecx
.LBB12_635:
	movups	(%r12,%rcx,4), %xmm0
	movups	16(%r12,%rcx,4), %xmm1
	andps	%xmm6, %xmm0
	andps	%xmm6, %xmm1
	movups	%xmm0, (%rdi,%rcx,4)
	movups	%xmm1, 16(%rdi,%rcx,4)
	addq	$8, %rcx
	cmpq	%rcx, %rax
	jne	.LBB12_635
	cmpq	%rax, %rbx
	je	.LBB12_643
.LBB12_637:
	movq	%rbx, %rdx
	movq	%rax, %rcx
	andq	$3, %rdx
	je	.LBB12_640
	movq	%rax, %rcx
.LBB12_639:
	movl	(%r12,%rcx,4), %r8d
	movl	$2147483647, %r9d
	andl	%r9d, %r8d
	movl	%r8d, (%rdi,%rcx,4)
	incq	%rcx
	decq	%rdx
	jne	.LBB12_639
.LBB12_640:
	subq	%rbx, %rax
	cmpq	$-4, %rax
	ja	.LBB12_643
.LBB12_641:
	movl	(%r12,%rcx,4), %eax
	movl	$2147483647, %edx
	andl	%edx, %eax
	movl	%eax, (%rdi,%rcx,4)
	movl	4(%r12,%rcx,4), %eax
	andl	%edx, %eax
	movl	%eax, 4(%rdi,%rcx,4)
	movl	8(%r12,%rcx,4), %eax
	andl	%edx, %eax
	movl	%eax, 8(%rdi,%rcx,4)
	movl	12(%r12,%rcx,4), %eax
	andl	%edx, %eax
	movl	%eax, 12(%rdi,%rcx,4)
	addq	$4, %rcx
	cmpq	%rcx, %rbx
	jne	.LBB12_641
.LBB12_643:
	incq	704(%rbp)
	movq	736(%rbp), %rax
	movq	%rbx, 144(%rax)
	movq	%rdi, 152(%rax)
	movq	%rbx, 160(%rax)
	movq	728(%rbp), %rax
	movq	184(%rax), %r13
	testq	%r13, %r13
	je	.LBB12_678
	movq	728(%rbp), %rax
	movq	176(%rax), %rbx
	leaq	(,%r13,4), %r15
	xorl	%edx, %edx
	movq	%r15, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	je	.LBB12_645
	movq	%rax, %rdi
	testb	%sil, %sil
	je	.LBB12_647
	movq	%rdi, %rcx
	movq	%rbx, %rdx
	movq	%r15, %r8
	callq	memcpy
	movq	736(%rbp), %rax
	leaq	168(%rax), %rbx
	movq	%r13, 168(%rax)
	movq	%rax, %r15
	addq	$176, %r15
	movq	%rdi, 176(%rax)
	movq	%r13, 184(%rax)
	jmp	.LBB12_683
.LBB12_678:
	movq	736(%rbp), %rax
	leaq	168(%rax), %rbx
	movq	$0, 168(%rax)
	movq	%rax, %r15
	addq	$176, %r15
	movq	$4, 176(%rax)
	movq	$0, 184(%rax)
	testb	%sil, %sil
	je	.LBB12_679
.LBB12_683:
	movq	%r15, 344(%rbp)
	movq	%rbx, 336(%rbp)
.Ltmp120:
	movl	$32, %r8d
	leaq	d014_baseline_i16(%rip), %rcx
	movq	736(%rbp), %rdx
	callq	_RNvCs2i4to50FHNk_9prototype7bench_i
	nop
.Ltmp121:
	movsd	%xmm0, 176(%rbp)
	leaq	176(%rbp), %rax
	#APP
	#NO_APP
	movq	%r15, 344(%rbp)
	movq	%rbx, 336(%rbp)
.Ltmp122:
	movl	$32, %r8d
	leaq	d014_candidate_i16(%rip), %rcx
	movq	736(%rbp), %rdx
	callq	_RNvCs2i4to50FHNk_9prototype7bench_i
	nop
.Ltmp123:
	movsd	%xmm0, 176(%rbp)
	leaq	176(%rbp), %rax
	#APP
	#NO_APP
	jmp	.LBB12_686
.LBB12_647:
	cmpq	$8, %r13
	setb	%al
	movq	%rdi, %rcx
	subq	%rbx, %rcx
	cmpq	$32, %rcx
	setb	%cl
	orb	%al, %cl
	je	.LBB12_649
	xorl	%eax, %eax
	jmp	.LBB12_652
.LBB12_649:
	movq	%r13, %rax
	andq	$-8, %rax
	xorl	%ecx, %ecx
.LBB12_650:
	movups	(%rbx,%rcx,4), %xmm0
	movups	16(%rbx,%rcx,4), %xmm1
	andps	%xmm6, %xmm0
	andps	%xmm6, %xmm1
	movups	%xmm0, (%rdi,%rcx,4)
	movups	%xmm1, 16(%rdi,%rcx,4)
	addq	$8, %rcx
	cmpq	%rcx, %rax
	jne	.LBB12_650
	cmpq	%rax, %r13
	je	.LBB12_657
.LBB12_652:
	movq	%r13, %rdx
	movq	%rax, %rcx
	andq	$3, %rdx
	je	.LBB12_655
	movq	%rax, %rcx
.LBB12_654:
	movl	(%rbx,%rcx,4), %r8d
	movl	$2147483647, %r9d
	andl	%r9d, %r8d
	movl	%r8d, (%rdi,%rcx,4)
	incq	%rcx
	decq	%rdx
	jne	.LBB12_654
.LBB12_655:
	subq	%r13, %rax
	cmpq	$-4, %rax
	ja	.LBB12_657
.LBB12_656:
	movl	(%rbx,%rcx,4), %eax
	movl	$2147483647, %edx
	andl	%edx, %eax
	movl	%eax, (%rdi,%rcx,4)
	movl	4(%rbx,%rcx,4), %eax
	andl	%edx, %eax
	movl	%eax, 4(%rdi,%rcx,4)
	movl	8(%rbx,%rcx,4), %eax
	andl	%edx, %eax
	movl	%eax, 8(%rdi,%rcx,4)
	movl	12(%rbx,%rcx,4), %eax
	andl	%edx, %eax
	movl	%eax, 12(%rdi,%rcx,4)
	addq	$4, %rcx
	cmpq	%rcx, %r13
	jne	.LBB12_656
.LBB12_657:
	movq	736(%rbp), %rax
	leaq	168(%rax), %rbx
	movq	%r13, 168(%rax)
	movq	%rax, %r15
	addq	$176, %r15
	movq	%rdi, 176(%rax)
	movq	%r13, 184(%rax)
.LBB12_679:
	movq	%r15, 344(%rbp)
	movq	%rbx, 336(%rbp)
.Ltmp116:
	movl	$32, %r8d
	leaq	d014_baseline_u16(%rip), %rcx
	movq	736(%rbp), %rdx
	callq	_RNvCs2i4to50FHNk_9prototype7bench_i
	nop
.Ltmp117:
	movsd	%xmm0, 176(%rbp)
	leaq	176(%rbp), %rax
	#APP
	#NO_APP
	movq	%r15, 344(%rbp)
	movq	%rbx, 336(%rbp)
.Ltmp118:
	movl	$32, %r8d
	leaq	d014_candidate_u16(%rip), %rcx
	movq	736(%rbp), %rdx
	callq	_RNvCs2i4to50FHNk_9prototype7bench_i
	nop
.Ltmp119:
	movsd	%xmm0, 176(%rbp)
	leaq	176(%rbp), %rax
	#APP
	#NO_APP
.LBB12_686:
	xorl	%r13d, %r13d
	jmp	.LBB12_687
.LBB12_750:
	movl	712(%rbp), %eax
	movl	%eax, %r13d
.LBB12_687:
	cmpl	$9, %r13d
	jae	.LBB12_688
	leal	1(%r13), %eax
	movl	%eax, 712(%rbp)
	movl	%r13d, 128(%rbp)
	andb	$1, %r13b
	movl	%r13d, %eax
	xorb	$1, %al
	movq	$2, 464(%rbp)
	movb	%r13b, 472(%rbp)
	movb	%al, 473(%rbp)
	xorl	%eax, %eax
	cmpq	$2, %rax
	je	.LBB12_750
.LBB12_724:
	leaq	1(%rax), %rdi
	movq	%rdi, 456(%rbp)
	movzbl	472(%rbp,%rax), %r12d
	movq	-64(%rbp), %r8
	testb	%sil, %sil
	je	.LBB12_725
	leaq	d014_candidate_i16(%rip), %rcx
	testb	%r12b, %r12b
	jne	.LBB12_731
	leaq	d014_baseline_i16(%rip), %rcx
.LBB12_731:
	movq	%r15, 344(%rbp)
	movq	%rbx, 336(%rbp)
.Ltmp126:
	movq	736(%rbp), %rdx
	callq	_RNvCs2i4to50FHNk_9prototype7bench_i
	nop
.Ltmp127:
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.52(%rip), %rax
	jmp	.LBB12_733
.LBB12_725:
	leaq	d014_candidate_u16(%rip), %rcx
	testb	%r12b, %r12b
	jne	.LBB12_727
	leaq	d014_baseline_u16(%rip), %rcx
.LBB12_727:
	movq	%r15, 344(%rbp)
	movq	%rbx, 336(%rbp)
.Ltmp124:
	movq	736(%rbp), %rdx
	callq	_RNvCs2i4to50FHNk_9prototype7bench_i
	nop
.Ltmp125:
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.51(%rip), %rax
.LBB12_733:
	movsd	%xmm0, -88(%rbp)
	movq	%rax, 648(%rbp)
	movq	$3, 656(%rbp)
	movb	%r13b, 352(%rbp)
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.54(%rip), %rax
	testb	%r12b, %r12b
	jne	.LBB12_735
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.53(%rip), %rax
.LBB12_735:
	movq	%rax, 144(%rbp)
	movzbl	%r12b, %eax
	orq	$8, %rax
	movq	%rax, 152(%rbp)
	leaq	648(%rbp), %rax
	movq	%rax, 176(%rbp)
	movq	%r14, 184(%rbp)
	leaq	48(%rbp), %rax
	movq	%rax, 192(%rbp)
	movq	%r14, 200(%rbp)
	leaq	368(%rbp), %rax
	movq	%rax, 208(%rbp)
	leaq	_RNvXsi_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impjNtB9_7Display3fmt(%rip), %rax
	movq	%rax, 216(%rbp)
	leaq	128(%rbp), %rcx
	movq	%rcx, 224(%rbp)
	leaq	_RNvXs9_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3implNtB9_7Display3fmt(%rip), %rcx
	movq	%rcx, 232(%rbp)
	leaq	352(%rbp), %rcx
	movq	%rcx, 240(%rbp)
	leaq	_RNvXsg_NtCs8xEFJqa6dYS_4core3fmtbNtB5_7Display3fmt(%rip), %rcx
	movq	%rcx, 248(%rbp)
	leaq	144(%rbp), %rcx
	movq	%rcx, 256(%rbp)
	movq	%r14, 264(%rbp)
	leaq	-64(%rbp), %rcx
	movq	%rcx, 272(%rbp)
	movq	%rax, 280(%rbp)
	leaq	-88(%rbp), %rax
	movq	%rax, 288(%rbp)
	leaq	_RNvXs7_NtNtCs8xEFJqa6dYS_4core3fmt5floatdNtB7_7Display3fmt(%rip), %rax
	movq	%rax, 296(%rbp)
	movq	%r15, 344(%rbp)
	movq	%rbx, 336(%rbp)
.Ltmp128:
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.55(%rip), %rcx
	leaq	176(%rbp), %rdx
	callq	_RNvNtNtCse0R8cuyqEa_3std2io5stdio6__print
	nop
.Ltmp129:
	movq	%rdi, %rax
	cmpq	$2, %rax
	jne	.LBB12_724
	jmp	.LBB12_750
.LBB12_688:
	movq	736(%rbp), %rax
	cmpq	$0, (%rax)
	je	.LBB12_690
	movq	736(%rbp), %rax
	movq	8(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_690:
	movq	736(%rbp), %rax
	cmpq	$0, 24(%rax)
	je	.LBB12_692
	movq	736(%rbp), %rax
	movq	32(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_692:
	movq	736(%rbp), %rax
	cmpq	$0, 48(%rax)
	je	.LBB12_694
	movq	736(%rbp), %rax
	movq	56(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_694:
	movq	736(%rbp), %rax
	cmpq	$0, 72(%rax)
	je	.LBB12_696
	movq	736(%rbp), %rax
	movq	80(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_696:
	movq	736(%rbp), %rax
	cmpq	$0, 96(%rax)
	je	.LBB12_698
	movq	736(%rbp), %rax
	movq	104(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_698:
	movq	736(%rbp), %rax
	cmpq	$0, 120(%rax)
	je	.LBB12_700
	movq	736(%rbp), %rax
	movq	128(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_700:
	movq	736(%rbp), %rax
	cmpq	$0, 144(%rax)
	je	.LBB12_702
	movq	736(%rbp), %rax
	movq	152(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_702:
	cmpq	$0, (%rbx)
	je	.LBB12_704
	movq	(%r15), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	jmp	.LBB12_704
.LBB12_658:
	movq	728(%rbp), %rax
	cmpq	$0, (%rax)
	je	.LBB12_660
	movq	728(%rbp), %rax
	movq	8(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_660:
	movq	728(%rbp), %rax
	cmpq	$0, 24(%rax)
	je	.LBB12_662
	movq	728(%rbp), %rax
	movq	32(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_662:
	movq	728(%rbp), %rax
	cmpq	$0, 48(%rax)
	je	.LBB12_664
	movq	728(%rbp), %rax
	movq	56(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_664:
	movq	728(%rbp), %rax
	cmpq	$0, 72(%rax)
	je	.LBB12_666
	movq	728(%rbp), %rax
	movq	80(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_666:
	movq	728(%rbp), %rax
	cmpq	$0, 96(%rax)
	je	.LBB12_668
	movq	728(%rbp), %rax
	movq	104(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_668:
	movq	728(%rbp), %rax
	cmpq	$0, 120(%rax)
	je	.LBB12_670
	movq	728(%rbp), %rax
	movq	128(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_670:
	movq	728(%rbp), %rax
	cmpq	$0, 144(%rax)
	je	.LBB12_672
	movq	728(%rbp), %rax
	movq	152(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_672:
	movq	728(%rbp), %rax
	cmpq	$0, 168(%rax)
	je	.LBB12_674
	movq	728(%rbp), %rax
	movq	176(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_674:
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	728(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
	cmpq	$2, 680(%rbp)
	movl	$1, %eax
	movq	%rax, 680(%rbp)
	jne	.LBB12_487
	cmpq	$14, 168(%rbp)
	jne	.LBB12_486
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.10(%rip), %rcx
	movl	$139, %edx
	callq	_RNvNtNtCse0R8cuyqEa_3std2io5stdio6__print
	jmp	.LBB12_677
.LBB12_470:
	movq	184(%rbp), %rdi
	movq	200(%rbp), %rbx
	subq	%rdi, %rbx
	je	.LBB12_475
	shrq	$5, %rbx
	addq	$8, %rdi
	jmp	.LBB12_472
.LBB12_474:
	addq	$32, %rdi
	decq	%rbx
	je	.LBB12_475
.LBB12_472:
	cmpq	$0, -8(%rdi)
	je	.LBB12_474
	movq	(%rdi), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	jmp	.LBB12_474
.LBB12_475:
	cmpq	$0, 192(%rbp)
	je	.LBB12_677
	movq	176(%rbp), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_677:
	movaps	752(%rbp), %xmm6
	movaps	768(%rbp), %xmm7
	movaps	784(%rbp), %xmm8
	movaps	800(%rbp), %xmm9
	movaps	816(%rbp), %xmm10
	movaps	832(%rbp), %xmm11
	movaps	848(%rbp), %xmm12
	movaps	864(%rbp), %xmm13
	.seh_startepilogue
	addq	$1016, %rsp
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
.LBB12_56:
	movl	$4, %eax
	movq	%rax, 728(%rbp)
.LBB12_57:
	movb	$1, 679(%rbp)
.Ltmp36:
	movq	728(%rbp), %rcx
	movq	%r13, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp37:
	jmp	.LBB12_39
.LBB12_73:
	movq	%r15, 704(%rbp)
	movb	$1, 678(%rbp)
.Ltmp20:
	movl	$4, %ecx
	movq	%r13, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp21:
	jmp	.LBB12_39
.LBB12_88:
	movq	%r15, 704(%rbp)
	movb	$1, 677(%rbp)
.Ltmp26:
	movl	$4, %ecx
	movq	%r13, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp27:
	jmp	.LBB12_39
.LBB12_103:
	movq	%rdi, 680(%rbp)
	movb	$1, 676(%rbp)
.Ltmp32:
	movl	$4, %ecx
	movq	%r13, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp33:
	jmp	.LBB12_39
.LBB12_196:
	movl	$4, %ebx
.LBB12_197:
	movb	$1, 674(%rbp)
.Ltmp66:
	movq	%rbx, %rcx
	movq	%r15, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp67:
	jmp	.LBB12_39
.LBB12_332:
	movq	704(%rbp), %rax
	movq	%rax, 176(%rbp)
	leaq	_RNvXsq_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt(%rip), %rax
	movq	%rax, 184(%rbp)
.Ltmp86:
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.26(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.25(%rip), %r8
	leaq	76(%rbp), %rcx
	leaq	128(%rbp), %rdx
	leaq	176(%rbp), %r9
	callq	_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedmmECs2i4to50FHNk_9prototype
	nop
.Ltmp87:
	jmp	.LBB12_39
.LBB12_335:
	movq	704(%rbp), %rax
	movq	%rax, 176(%rbp)
	leaq	_RNvXsq_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt(%rip), %rax
	movq	%rax, 184(%rbp)
.Ltmp88:
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.28(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.27(%rip), %r8
	leaq	72(%rbp), %rcx
	leaq	128(%rbp), %rdx
	leaq	176(%rbp), %r9
	callq	_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedmmECs2i4to50FHNk_9prototype
	nop
.Ltmp89:
	jmp	.LBB12_39
.LBB12_337:
	movq	704(%rbp), %rax
	movq	%rax, 176(%rbp)
	leaq	_RNvXsq_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt(%rip), %rax
	movq	%rax, 184(%rbp)
.Ltmp90:
	leaq	608(%rbp), %rcx
	leaq	144(%rbp), %rdx
	leaq	176(%rbp), %r8
	callq	_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedINtNtCsfQUUnEvlYZE_5alloc3vec3VecsEBM_ECs2i4to50FHNk_9prototype
	nop
.Ltmp91:
	jmp	.LBB12_39
.LBB12_748:
	movq	704(%rbp), %rax
	movq	%rax, 176(%rbp)
	leaq	_RNvXsq_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt(%rip), %rax
	movq	%rax, 184(%rbp)
.Ltmp92:
	leaq	400(%rbp), %rcx
	leaq	456(%rbp), %rdx
	leaq	176(%rbp), %r8
	callq	_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedINtNtCsfQUUnEvlYZE_5alloc3vec3VectEBM_ECs2i4to50FHNk_9prototype
	nop
.Ltmp93:
	jmp	.LBB12_39
.LBB12_350:
	movq	736(%rbp), %rax
	movq	%rax, 448(%rbp)
.LBB12_351:
	movq	704(%rbp), %rax
	movq	%rax, 128(%rbp)
	leaq	_RNvXsq_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt(%rip), %rax
	movq	%rax, 136(%rbp)
.Ltmp96:
	leaq	648(%rbp), %rcx
	leaq	176(%rbp), %rdx
	leaq	128(%rbp), %r8
	callq	_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedINtNtCsfQUUnEvlYZE_5alloc3vec3VecmEBM_ECs2i4to50FHNk_9prototype
	nop
.Ltmp97:
	jmp	.LBB12_39
.LBB12_176:
	movl	$4, %ecx
	jmp	.LBB12_177
.LBB12_438:
	movb	$1, 727(%rbp)
.Ltmp68:
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.43(%rip), %r8
	movq	%r14, %rdx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	nop
.Ltmp69:
	jmp	.LBB12_39
.LBB12_401:
.Ltmp136:
	movl	$4, %ecx
	movq	%r14, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp137:
	jmp	.LBB12_39
.LBB12_424:
	movl	$4, %edx
.LBB12_425:
.Ltmp82:
	movq	%rdx, %rcx
	movq	%rsi, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp83:
	jmp	.LBB12_39
.LBB12_454:
	movb	$1, 695(%rbp)
.Ltmp74:
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.45(%rip), %r8
	movq	%r14, %rdx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	nop
.Ltmp75:
	jmp	.LBB12_39
.LBB12_310:
.Ltmp108:
	movl	$2, %ecx
	movq	712(%rbp), %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp109:
	jmp	.LBB12_39
.LBB12_308:
.Ltmp106:
	movl	$2, %ecx
	movq	712(%rbp), %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp107:
	jmp	.LBB12_39
.LBB12_324:
.Ltmp104:
	movl	$2, %ecx
	movq	712(%rbp), %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp105:
	jmp	.LBB12_39
.LBB12_323:
.Ltmp102:
	movl	$2, %ecx
	movq	712(%rbp), %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp103:
	jmp	.LBB12_39
.LBB12_441:
	movl	$4, %r13d
.LBB12_442:
	movb	$0, 727(%rbp)
.Ltmp80:
	movq	%r13, %rcx
	movq	%r15, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp81:
	jmp	.LBB12_39
.LBB12_309:
.Ltmp84:
	movl	$4, %ecx
	movq	120(%rbp), %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp85:
	jmp	.LBB12_39
.LBB12_363:
.Ltmp94:
	movl	$4, %ecx
	movq	%rsi, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp95:
	jmp	.LBB12_39
.LBB12_497:
	movl	$8, %ecx
	movl	$192, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.LBB12_534:
.Ltmp130:
	movl	$8, %ecx
	movl	$192, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp131:
	jmp	.LBB12_39
.LBB12_505:
	movl	$4, %eax
	movq	%rax, 640(%rbp)
.LBB12_506:
.Ltmp134:
	movq	640(%rbp), %rcx
	movq	%rsi, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp135:
	jmp	.LBB12_39
.LBB12_552:
	movl	$1, %eax
	jmp	.LBB12_553
.LBB12_569:
	movl	$2, %eax
	jmp	.LBB12_553
.LBB12_584:
	movl	$3, %eax
	jmp	.LBB12_553
.LBB12_599:
	movl	$4, %eax
	jmp	.LBB12_553
.LBB12_614:
	movl	$5, %eax
	jmp	.LBB12_553
.LBB12_630:
	movl	$6, %eax
	jmp	.LBB12_553
.LBB12_645:
	movl	$7, %eax
.LBB12_553:
	movq	%rax, 640(%rbp)
.LBB12_554:
.Ltmp114:
	movl	$4, %ecx
	movq	%r15, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp115:
	jmp	.LBB12_39
.LBB12_511:
.Ltmp132:
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.50(%rip), %rcx
	callq	_RNvNtNtCs8xEFJqa6dYS_4core9panicking11panic_const23panic_const_div_by_zero
	nop
.Ltmp133:
.LBB12_39:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvCs2i4to50FHNk_9prototype4main@IMGREL
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$26@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$26@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$26@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_26:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movdqa	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movdqa	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	movq	656(%rbp), %rsi
	movq	664(%rbp), %rbx
	testq	%rbx, %rbx
	movq	__imp_GetProcessHeap(%rip), %r15
	movq	__imp_HeapFree(%rip), %r12
	je	.LBB12_33
	leaq	32(%rsi), %r14
	jmp	.LBB12_28
	.p2align	4
.LBB12_32:
	addq	$48, %r14
	decq	%rbx
	je	.LBB12_33
.LBB12_28:
	cmpq	$0, -32(%r14)
	je	.LBB12_30
	movq	-24(%r14), %rdi
	callq	*%r15
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rdi, %r8
	callq	*%r12
.LBB12_30:
	cmpq	$0, -8(%r14)
	je	.LBB12_32
	movq	(%r14), %rdi
	callq	*%r15
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rdi, %r8
	callq	*%r12
	jmp	.LBB12_32
.LBB12_33:
	cmpq	$0, 648(%rbp)
	je	.LBB12_35
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_35:
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movaps	64(%rsp), %xmm11
	movaps	48(%rsp), %xmm12
	movaps	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$43@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$43@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$43@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_43:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movdqa	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movdqa	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	cmpq	$0, 736(%rbp)
	jne	.LBB12_44
	cmpq	$0, 712(%rbp)
	je	.LBB12_47
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	696(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_47:
	movdqa	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movdqa	112(%rsp), %xmm8
	movdqa	96(%rsp), %xmm9
	movdqa	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
.LBB12_44:
	movdqa	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movdqa	112(%rsp), %xmm8
	movdqa	96(%rsp), %xmm9
	movdqa	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$113@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$113@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$113@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_113:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movdqa	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	cmpb	$0, 676(%rbp)
	je	.LBB12_114
	cmpq	$0, 704(%rbp)
	je	.LBB12_117
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	680(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_117:
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movaps	64(%rsp), %xmm11
	movaps	48(%rsp), %xmm12
	movaps	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
.LBB12_114:
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movaps	64(%rsp), %xmm11
	movaps	48(%rsp), %xmm12
	movaps	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$118@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$118@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$118@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_118:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movdqa	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movdqa	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	cmpb	$0, 677(%rbp)
	je	.LBB12_119
	cmpq	$0, 696(%rbp)
	je	.LBB12_122
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	704(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_122:
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movaps	64(%rsp), %xmm11
	movaps	48(%rsp), %xmm12
	movaps	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
.LBB12_119:
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movaps	64(%rsp), %xmm11
	movaps	48(%rsp), %xmm12
	movaps	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$123@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$123@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$123@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_123:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movdqa	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movdqa	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	cmpb	$0, 678(%rbp)
	je	.LBB12_124
	cmpq	$0, 696(%rbp)
	je	.LBB12_127
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	704(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_127:
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movaps	64(%rsp), %xmm11
	movaps	48(%rsp), %xmm12
	movaps	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
.LBB12_124:
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movaps	64(%rsp), %xmm11
	movaps	48(%rsp), %xmm12
	movaps	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$128@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$128@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$128@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_128:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movdqa	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	cmpb	$0, 679(%rbp)
	je	.LBB12_129
	cmpq	$0, 696(%rbp)
	je	.LBB12_132
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	704(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_132:
	movdqa	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movdqa	112(%rsp), %xmm8
	movdqa	96(%rsp), %xmm9
	movdqa	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
.LBB12_129:
	movdqa	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movdqa	112(%rsp), %xmm8
	movdqa	96(%rsp), %xmm9
	movdqa	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$136@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$136@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$136@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_136:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movdqa	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	cmpq	$0, 736(%rbp)
	jne	.LBB12_137
	cmpq	$0, 712(%rbp)
	je	.LBB12_140
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	696(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_140:
	movdqa	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movdqa	112(%rsp), %xmm8
	movdqa	96(%rsp), %xmm9
	movdqa	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
.LBB12_137:
	movdqa	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movdqa	112(%rsp), %xmm8
	movdqa	96(%rsp), %xmm9
	movdqa	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$190@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$190@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$190@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_190:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movaps	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movaps	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	cmpb	$0, 675(%rbp)
	je	.LBB12_191
	cmpq	$0, 712(%rbp)
	je	.LBB12_194
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	736(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_194:
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movaps	64(%rsp), %xmm11
	movaps	48(%rsp), %xmm12
	movaps	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
.LBB12_191:
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movaps	64(%rsp), %xmm11
	movaps	48(%rsp), %xmm12
	movaps	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$206@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$206@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$206@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_206:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movaps	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movaps	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	cmpb	$0, 674(%rbp)
	je	.LBB12_207
	cmpq	$0, 736(%rbp)
	je	.LBB12_210
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	712(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_210:
	movdqa	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movdqa	112(%rsp), %xmm8
	movdqa	96(%rsp), %xmm9
	movdqa	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
.LBB12_207:
	movdqa	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movdqa	112(%rsp), %xmm8
	movdqa	96(%rsp), %xmm9
	movdqa	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$214@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$214@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$214@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_214:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movaps	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movaps	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	cmpq	$0, 736(%rbp)
	jne	.LBB12_215
	cmpq	$0, 712(%rbp)
	je	.LBB12_218
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	696(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_218:
	movdqa	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movdqa	112(%rsp), %xmm8
	movdqa	96(%rsp), %xmm9
	movdqa	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
.LBB12_215:
	movdqa	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movdqa	112(%rsp), %xmm8
	movdqa	96(%rsp), %xmm9
	movdqa	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$235@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$235@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$235@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_235:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	cmpb	$0, 726(%rbp)
	je	.LBB12_236
	cmpq	$0, 608(%rbp)
	je	.LBB12_239
	movq	616(%rbp), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_239:
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movaps	64(%rsp), %xmm11
	movaps	48(%rsp), %xmm12
	movaps	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
.LBB12_236:
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movaps	64(%rsp), %xmm11
	movaps	48(%rsp), %xmm12
	movaps	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$247@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$247@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$247@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_247:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movaps	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movaps	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	movq	376(%rbp), %rsi
	movq	384(%rbp), %rbx
	testq	%rbx, %rbx
	movq	__imp_GetProcessHeap(%rip), %r15
	movq	__imp_HeapFree(%rip), %r12
	je	.LBB12_254
	leaq	32(%rsi), %r14
	jmp	.LBB12_249
.LBB12_253:
	addq	$48, %r14
	decq	%rbx
	je	.LBB12_254
.LBB12_249:
	cmpq	$0, -32(%r14)
	je	.LBB12_251
	movq	-24(%r14), %rdi
	callq	*%r15
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rdi, %r8
	callq	*%r12
.LBB12_251:
	cmpq	$0, -8(%r14)
	je	.LBB12_253
	movq	(%r14), %rdi
	callq	*%r15
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rdi, %r8
	callq	*%r12
	jmp	.LBB12_253
.LBB12_254:
	cmpq	$0, 368(%rbp)
	je	.LBB12_256
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_256:
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movaps	64(%rsp), %xmm11
	movaps	48(%rsp), %xmm12
	movaps	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$311@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$311@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$311@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_311:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	cmpq	$0, 736(%rbp)
	je	.LBB12_313
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	360(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_313:
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$314@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$314@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$314@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_314:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	680(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movdqa	96(%rsp), %xmm9
	movdqa	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$325@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$325@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$325@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_325:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	696(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movdqa	96(%rsp), %xmm9
	movdqa	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$326@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$326@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$326@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_326:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	392(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movdqa	96(%rsp), %xmm9
	movdqa	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$327@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$327@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$327@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_327:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	728(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movdqa	96(%rsp), %xmm9
	movdqa	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$368@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$368@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$368@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_368:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	cmpq	$0, 448(%rbp)
	je	.LBB12_370
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	632(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_370:
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movdqa	96(%rsp), %xmm9
	movdqa	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$402@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$402@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$402@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_402:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	leaq	176(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs2i4to50FHNk_9prototype4CaseEBD_
	movb	$0, 673(%rbp)
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movdqa	96(%rsp), %xmm9
	movdqa	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$403@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$403@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$403@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_403:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	cmpb	$0, 673(%rbp)
	je	.LBB12_404
	cmpq	$0, 712(%rbp)
	je	.LBB12_407
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	736(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_407:
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
.LBB12_404:
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$439@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$439@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$439@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_439:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movaps	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movaps	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	leaq	176(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs2i4to50FHNk_9prototype4CaseEBD_
	movb	$0, 727(%rbp)
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$455@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$455@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$455@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_455:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movaps	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movaps	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	leaq	176(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs2i4to50FHNk_9prototype4CaseEBD_
	movb	$0, 695(%rbp)
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$456@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$456@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$456@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_456:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movaps	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movaps	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	cmpb	$0, 695(%rbp)
	je	.LBB12_457
	cmpq	$0, 632(%rbp)
	je	.LBB12_460
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	680(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_460:
	movb	$0, 727(%rbp)
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
.LBB12_457:
	movb	$0, 727(%rbp)
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$461@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$461@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$461@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_461:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movaps	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movaps	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	cmpb	$0, 727(%rbp)
	je	.LBB12_462
	cmpq	$0, 736(%rbp)
	je	.LBB12_465
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	712(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_465:
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movaps	64(%rsp), %xmm11
	movaps	48(%rsp), %xmm12
	movaps	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
.LBB12_462:
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movaps	64(%rsp), %xmm11
	movaps	48(%rsp), %xmm12
	movaps	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$477@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$477@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$477@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_477:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	leaq	176(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCse0R8cuyqEa_3std3env4ArgsECs2i4to50FHNk_9prototype
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movaps	64(%rsp), %xmm11
	movaps	48(%rsp), %xmm12
	movaps	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$498@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$498@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$498@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_498:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	cmpq	$0, 736(%rbp)
	je	.LBB12_503
	movq	728(%rbp), %rdi
	addq	$8, %rdi
	jmp	.LBB12_500
.LBB12_502:
	addq	$24, %rdi
	decq	736(%rbp)
	je	.LBB12_503
.LBB12_500:
	cmpq	$0, -8(%rdi)
	je	.LBB12_502
	movq	(%rdi), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	jmp	.LBB12_502
.LBB12_503:
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	728(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movaps	64(%rsp), %xmm11
	movaps	48(%rsp), %xmm12
	movaps	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$512@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$512@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$512@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_512:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	movq	728(%rbp), %rax
	cmpq	$0, (%rax)
	je	.LBB12_514
	movq	728(%rbp), %rax
	movq	8(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_514:
	movq	728(%rbp), %rax
	cmpq	$0, 24(%rax)
	je	.LBB12_516
	movq	728(%rbp), %rax
	movq	32(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_516:
	movq	728(%rbp), %rax
	cmpq	$0, 48(%rax)
	je	.LBB12_518
	movq	728(%rbp), %rax
	movq	56(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_518:
	movq	728(%rbp), %rax
	cmpq	$0, 72(%rax)
	je	.LBB12_520
	movq	728(%rbp), %rax
	movq	80(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_520:
	movq	728(%rbp), %rax
	cmpq	$0, 96(%rax)
	je	.LBB12_522
	movq	728(%rbp), %rax
	movq	104(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_522:
	movq	728(%rbp), %rax
	cmpq	$0, 120(%rax)
	je	.LBB12_524
	movq	728(%rbp), %rax
	movq	128(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_524:
	movq	728(%rbp), %rax
	cmpq	$0, 144(%rax)
	je	.LBB12_526
	movq	728(%rbp), %rax
	movq	152(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_526:
	movq	728(%rbp), %rax
	cmpq	$0, 168(%rax)
	je	.LBB12_528
	movq	728(%rbp), %rax
	movq	176(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_528:
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	728(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movaps	64(%rsp), %xmm11
	movaps	48(%rsp), %xmm12
	movaps	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$535@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$535@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$535@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_535:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	movq	640(%rbp), %rax
	movq	%rax, 192(%rbp)
	leaq	176(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecIBC_fEEECs2i4to50FHNk_9prototype
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movdqa	96(%rsp), %xmm9
	movdqa	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$705@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$705@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$705@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_705:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	movq	336(%rbp), %rbx
	movq	344(%rbp), %rdi
	movq	168(%rbp), %rax
	movq	%rax, 480(%rbp)
	movq	680(%rbp), %rax
	movq	%rax, 400(%rbp)
	movq	704(%rbp), %rax
	movq	%rax, 608(%rbp)
	movq	736(%rbp), %rax
	cmpq	$0, (%rax)
	jne	.LBB12_706
	movq	736(%rbp), %rax
	cmpq	$0, 24(%rax)
	jne	.LBB12_708
.LBB12_709:
	movq	736(%rbp), %rax
	cmpq	$0, 48(%rax)
	jne	.LBB12_710
.LBB12_711:
	movq	736(%rbp), %rax
	cmpq	$0, 72(%rax)
	jne	.LBB12_712
.LBB12_713:
	movq	736(%rbp), %rax
	cmpq	$0, 96(%rax)
	jne	.LBB12_714
.LBB12_715:
	movq	736(%rbp), %rax
	cmpq	$0, 120(%rax)
	jne	.LBB12_716
.LBB12_717:
	movq	736(%rbp), %rax
	cmpq	$0, 144(%rax)
	jne	.LBB12_718
.LBB12_719:
	cmpq	$0, (%rbx)
	je	.LBB12_721
.LBB12_720:
	movq	(%rdi), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_721:
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	736(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movdqa	96(%rsp), %xmm9
	movdqa	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
.LBB12_706:
	movq	736(%rbp), %rax
	movq	8(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	movq	736(%rbp), %rax
	cmpq	$0, 24(%rax)
	je	.LBB12_709
.LBB12_708:
	movq	736(%rbp), %rax
	movq	32(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	movq	736(%rbp), %rax
	cmpq	$0, 48(%rax)
	je	.LBB12_711
.LBB12_710:
	movq	736(%rbp), %rax
	movq	56(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	movq	736(%rbp), %rax
	cmpq	$0, 72(%rax)
	je	.LBB12_713
.LBB12_712:
	movq	736(%rbp), %rax
	movq	80(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	movq	736(%rbp), %rax
	cmpq	$0, 96(%rax)
	je	.LBB12_715
.LBB12_714:
	movq	736(%rbp), %rax
	movq	104(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	movq	736(%rbp), %rax
	cmpq	$0, 120(%rax)
	je	.LBB12_717
.LBB12_716:
	movq	736(%rbp), %rax
	movq	128(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	movq	736(%rbp), %rax
	cmpq	$0, 144(%rax)
	je	.LBB12_719
.LBB12_718:
	movq	736(%rbp), %rax
	movq	152(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	cmpq	$0, (%rbx)
	jne	.LBB12_720
	jmp	.LBB12_721
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$737@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$737@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$737@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_737:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movdqa	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movdqa	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	leaq	176(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCse0R8cuyqEa_3std3env4ArgsECs2i4to50FHNk_9prototype
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movaps	64(%rsp), %xmm11
	movaps	48(%rsp), %xmm12
	movaps	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$738@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$738@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$738@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_738:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movdqa	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movdqa	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	leaq	480(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs2i4to50FHNk_9prototype4CaseEBD_
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movaps	64(%rsp), %xmm11
	movaps	48(%rsp), %xmm12
	movaps	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$739@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$739@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$739@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_739:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movdqa	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movdqa	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	leaq	480(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs2i4to50FHNk_9prototype4CaseEBD_
	movb	$0, 679(%rbp)
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movaps	64(%rsp), %xmm11
	movaps	48(%rsp), %xmm12
	movaps	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$740@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$740@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$740@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_740:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movdqa	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movdqa	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	leaq	480(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs2i4to50FHNk_9prototype4CaseEBD_
	movb	$0, 678(%rbp)
	movdqa	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movdqa	112(%rsp), %xmm8
	movdqa	96(%rsp), %xmm9
	movdqa	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$741@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$741@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$741@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_741:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movdqa	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movdqa	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	leaq	480(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs2i4to50FHNk_9prototype4CaseEBD_
	movb	$0, 677(%rbp)
	movdqa	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movdqa	112(%rsp), %xmm8
	movdqa	96(%rsp), %xmm9
	movdqa	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$742@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$742@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$742@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_742:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movdqa	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	leaq	480(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs2i4to50FHNk_9prototype4CaseEBD_
	movb	$0, 676(%rbp)
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movdqa	112(%rsp), %xmm8
	movdqa	96(%rsp), %xmm9
	movdqa	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$743@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$743@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$743@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_743:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movdqa	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	leaq	480(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs2i4to50FHNk_9prototype4CaseEBD_
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movaps	64(%rsp), %xmm11
	movaps	48(%rsp), %xmm12
	movaps	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$744@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$744@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$744@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_744:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movaps	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movaps	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	leaq	480(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs2i4to50FHNk_9prototype4CaseEBD_
	movb	$0, 675(%rbp)
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$745@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$745@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$745@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_745:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movaps	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movaps	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	leaq	480(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs2i4to50FHNk_9prototype4CaseEBD_
	movb	$0, 674(%rbp)
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movaps	64(%rsp), %xmm11
	movaps	48(%rsp), %xmm12
	movaps	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$746@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$746@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$746@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_746:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movaps	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movaps	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	leaq	480(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs2i4to50FHNk_9prototype4CaseEBD_
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
	movaps	80(%rsp), %xmm10
	movaps	64(%rsp), %xmm11
	movaps	48(%rsp), %xmm12
	movaps	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$747@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$747@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$747@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_747:
	movq	%rdx, 16(%rsp)
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rdx), %rbp
	movdqa	%xmm13, 32(%rsp)
	.seh_savexmm %xmm13, 32
	movdqa	%xmm12, 48(%rsp)
	.seh_savexmm %xmm12, 48
	movdqa	%xmm11, 64(%rsp)
	.seh_savexmm %xmm11, 64
	movdqa	%xmm10, 80(%rsp)
	.seh_savexmm %xmm10, 80
	movdqa	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	leaq	480(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs2i4to50FHNk_9prototype4CaseEBD_
	movb	$0, 726(%rbp)
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movdqa	96(%rsp), %xmm9
	movdqa	80(%rsp), %xmm10
	movdqa	64(%rsp), %xmm11
	movdqa	48(%rsp), %xmm12
	movdqa	32(%rsp), %xmm13
	.seh_startepilogue
	addq	$168, %rsp
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
.Lfunc_end12:
	.section	.rdata,"dr",associative,_RNvCs2i4to50FHNk_9prototype4main,unique,13
	.p2align	2, 0x0
.LJTI12_0:
	.long	.LBB12_185-.LJTI12_0
	.long	.LBB12_179-.LJTI12_0
	.long	.LBB12_180-.LJTI12_0
	.long	.LBB12_181-.LJTI12_0
	.long	.LBB12_184-.LJTI12_0
	.long	.LBB12_182-.LJTI12_0
	.long	.LBB12_183-.LJTI12_0
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvCs2i4to50FHNk_9prototype4main,unique,1
	.p2align	2, 0x0
$cppxdata$_RNvCs2i4to50FHNk_9prototype4main:
	.long	429065506
	.long	40
	.long	$stateUnwindMap$_RNvCs2i4to50FHNk_9prototype4main@IMGREL
	.long	0
	.long	0
	.long	66
	.long	$ip2state$_RNvCs2i4to50FHNk_9prototype4main@IMGREL
	.long	872
	.long	0
	.long	1
$stateUnwindMap$_RNvCs2i4to50FHNk_9prototype4main:
	.long	-1
	.long	"?dtor$737@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	-1
	.long	"?dtor$26@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	1
	.long	"?dtor$235@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	2
	.long	"?dtor$747@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	1
	.long	"?dtor$214@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	4
	.long	"?dtor$746@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	1
	.long	"?dtor$206@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	6
	.long	"?dtor$745@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	1
	.long	"?dtor$190@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	8
	.long	"?dtor$744@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	1
	.long	"?dtor$136@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	10
	.long	"?dtor$743@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	1
	.long	"?dtor$128@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	12
	.long	"?dtor$739@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	1
	.long	"?dtor$123@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	14
	.long	"?dtor$740@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	1
	.long	"?dtor$118@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	16
	.long	"?dtor$741@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	1
	.long	"?dtor$113@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	18
	.long	"?dtor$742@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	1
	.long	"?dtor$43@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	20
	.long	"?dtor$738@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	-1
	.long	"?dtor$247@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	22
	.long	"?dtor$461@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	23
	.long	"?dtor$456@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	24
	.long	"?dtor$455@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	23
	.long	"?dtor$439@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	22
	.long	"?dtor$403@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	27
	.long	"?dtor$402@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	22
	.long	"?dtor$311@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	29
	.long	"?dtor$314@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	30
	.long	"?dtor$325@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	31
	.long	"?dtor$326@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	32
	.long	"?dtor$327@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	33
	.long	"?dtor$368@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	-1
	.long	"?dtor$477@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	-1
	.long	"?dtor$498@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	-1
	.long	"?dtor$512@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	37
	.long	"?dtor$705@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	37
	.long	"?dtor$535@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
$ip2state$_RNvCs2i4to50FHNk_9prototype4main:
	.long	.Lfunc_begin12@IMGREL
	.long	-1
	.long	.Ltmp4@IMGREL
	.long	0
	.long	.Ltmp5@IMGREL
	.long	-1
	.long	.Ltmp6@IMGREL
	.long	1
	.long	.Ltmp10@IMGREL
	.long	21
	.long	.Ltmp14@IMGREL
	.long	1
	.long	.Ltmp16@IMGREL
	.long	13
	.long	.Ltmp18@IMGREL
	.long	1
	.long	.Ltmp22@IMGREL
	.long	15
	.long	.Ltmp24@IMGREL
	.long	1
	.long	.Ltmp28@IMGREL
	.long	17
	.long	.Ltmp30@IMGREL
	.long	1
	.long	.Ltmp34@IMGREL
	.long	19
	.long	.Ltmp38@IMGREL
	.long	1
	.long	.Ltmp40@IMGREL
	.long	11
	.long	.Ltmp44@IMGREL
	.long	2
	.long	.Ltmp50@IMGREL
	.long	3
	.long	.Ltmp54@IMGREL
	.long	1
	.long	.Ltmp56@IMGREL
	.long	5
	.long	.Ltmp60@IMGREL
	.long	1
	.long	.Ltmp64@IMGREL
	.long	7
	.long	.Ltmp142@IMGREL
	.long	8
	.long	.Ltmp144@IMGREL
	.long	9
	.long	.Ltmp70@IMGREL
	.long	23
	.long	.Ltmp72@IMGREL
	.long	26
	.long	.Ltmp76@IMGREL
	.long	24
	.long	.Ltmp78@IMGREL
	.long	25
	.long	.Ltmp12@IMGREL
	.long	20
	.long	.Ltmp146@IMGREL
	.long	1
	.long	.Ltmp42@IMGREL
	.long	10
	.long	.Ltmp52@IMGREL
	.long	1
	.long	.Ltmp58@IMGREL
	.long	4
	.long	.Ltmp138@IMGREL
	.long	27
	.long	.Ltmp140@IMGREL
	.long	28
	.long	.Ltmp148@IMGREL
	.long	1
	.long	.Ltmp149@IMGREL
	.long	-1
	.long	.Ltmp98@IMGREL
	.long	33
	.long	.Ltmp110@IMGREL
	.long	22
	.long	.Ltmp111@IMGREL
	.long	-1
	.long	.Ltmp112@IMGREL
	.long	35
	.long	.Ltmp113@IMGREL
	.long	-1
	.long	.Ltmp120@IMGREL
	.long	38
	.long	.Ltmp129@IMGREL
	.long	-1
	.long	.Ltmp36@IMGREL
	.long	12
	.long	.Ltmp20@IMGREL
	.long	14
	.long	.Ltmp26@IMGREL
	.long	16
	.long	.Ltmp32@IMGREL
	.long	18
	.long	.Ltmp66@IMGREL
	.long	6
	.long	.Ltmp86@IMGREL
	.long	33
	.long	.Ltmp96@IMGREL
	.long	34
	.long	.Ltmp68@IMGREL
	.long	23
	.long	.Ltmp136@IMGREL
	.long	22
	.long	.Ltmp74@IMGREL
	.long	24
	.long	.Ltmp108@IMGREL
	.long	29
	.long	.Ltmp106@IMGREL
	.long	30
	.long	.Ltmp104@IMGREL
	.long	31
	.long	.Ltmp102@IMGREL
	.long	32
	.long	.Ltmp80@IMGREL
	.long	23
	.long	.Ltmp84@IMGREL
	.long	22
	.long	.Ltmp94@IMGREL
	.long	33
	.long	.Ltmp95@IMGREL
	.long	-1
	.long	.Ltmp130@IMGREL
	.long	37
	.long	.Ltmp134@IMGREL
	.long	36
	.long	.Ltmp114@IMGREL
	.long	39
	.long	.Ltmp132@IMGREL
	.long	37
	.long	.Ltmp133@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12

	.def	_RNvCs2i4to50FHNk_9prototype7bench_i;
	.scl	3;
	.type	32;
	.endef
	.globl	__real@41cdcd6500000000
	.section	.rdata,"dr",discard,__real@41cdcd6500000000
	.p2align	3, 0x0
__real@41cdcd6500000000:
	.quad	0x41cdcd6500000000
	.globl	__xmm@00000000000000004530000043300000
	.section	.rdata,"dr",discard,__xmm@00000000000000004530000043300000
	.p2align	4, 0x0
__xmm@00000000000000004530000043300000:
	.long	1127219200
	.long	1160773632
	.long	0
	.long	0
	.globl	__xmm@45300000000000004330000000000000
	.section	.rdata,"dr",discard,__xmm@45300000000000004330000000000000
	.p2align	4, 0x0
__xmm@45300000000000004330000000000000:
	.quad	0x4330000000000000
	.quad	0x4530000000000000
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype7bench_i,unique,14
	.p2align	4
_RNvCs2i4to50FHNk_9prototype7bench_i:
.Lfunc_begin13:
.seh_proc _RNvCs2i4to50FHNk_9prototype7bench_i
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
	subq	$120, %rsp
	.seh_stackalloc 120
	leaq	112(%rsp), %rbp
	.seh_setframe %rbp, 112
	.seh_endprologue
	movq	$-2, (%rbp)
	movq	%r8, %rsi
	movq	%rdx, %rdi
	movq	%rcx, %rbx
	movq	16(%rdx), %r15
	testq	%r15, %r15
	je	.LBB13_1
	leaq	(%r15,%r15), %r14
	movl	$8, %edx
	movq	%r14, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	jne	.LBB13_3
	movl	$2, %ecx
	movq	%r14, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.LBB13_1:
	movl	$2, %eax
.LBB13_3:
	movq	%r15, -48(%rbp)
	movq	%rax, -40(%rbp)
	movq	%r15, -32(%rbp)
.Ltmp150:
	callq	_RNvMNtCse0R8cuyqEa_3std4timeNtB2_7Instant3now
	movq	%rax, -56(%rbp)
	movl	%edx, -20(%rbp)
.Ltmp151:
	xorl	%r12d, %r12d
	leaq	-72(%rbp), %r13
	leaq	-16(%rbp), %r14
	leaq	-48(%rbp), %r15
	cmpq	%rsi, %r12
	jae	.LBB13_6
	.p2align	4
.LBB13_16:
	movl	%r12d, %eax
	andl	$7, %eax
	leaq	(%rax,%rax,2), %rax
	movups	8(%rdi,%rax,8), %xmm0
	movups	%xmm0, -72(%rbp)
	#APP
	#NO_APP
	movupd	-40(%rbp), %xmm0
	movupd	%xmm0, -16(%rbp)
	#APP
	#NO_APP
	movq	-72(%rbp), %rcx
	movq	-64(%rbp), %rdx
	movq	-16(%rbp), %r8
	movq	-8(%rbp), %r9
.Ltmp156:
	callq	*%rbx
	nop
.Ltmp157:
	incq	%r12
	movss	%xmm0, -16(%rbp)
	#APP
	#NO_APP
	movq	%r15, -16(%rbp)
	#APP
	#NO_APP
	cmpq	%rsi, %r12
	jb	.LBB13_16
.LBB13_6:
.Ltmp152:
	callq	_RNvMNtCse0R8cuyqEa_3std4timeNtB2_7Instant3now
	nop
.Ltmp153:
	movq	%rax, -16(%rbp)
	movl	%edx, -8(%rbp)
.Ltmp154:
	leaq	-16(%rbp), %rcx
	movq	-56(%rbp), %rdx
	movl	-20(%rbp), %r8d
	callq	_RNvMNtCse0R8cuyqEa_3std4timeNtB2_7Instant22checked_duration_since
	nop
.Ltmp155:
	movq	%rax, %rdi
	movl	%edx, %ebx
	xorl	%r15d, %r15d
	cmpl	$-1, %edx
	cmovnel	%edx, %r15d
	cmpq	$0, -48(%rbp)
	je	.LBB13_10
	movq	-40(%rbp), %r14
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%r14, %r8
	callq	*__imp_HeapFree(%rip)
.LBB13_10:
	cvtsi2sd	%r15d, %xmm4
	movsd	__real@41cdcd6500000000(%rip), %xmm2
	divsd	%xmm2, %xmm4
	movq	__xmm@00000000000000004530000043300000(%rip), %xmm3
	movapd	__xmm@45300000000000004330000000000000(%rip), %xmm1
	xorpd	%xmm0, %xmm0
	cmpl	$-1, %ebx
	je	.LBB13_12
	movq	%rdi, %xmm5
	punpckldq	%xmm3, %xmm5
	subpd	%xmm1, %xmm5
	movapd	%xmm5, %xmm0
	unpckhpd	%xmm5, %xmm0
	addsd	%xmm5, %xmm0
.LBB13_12:
	addsd	%xmm4, %xmm0
	mulsd	%xmm2, %xmm0
	movq	%rsi, %xmm2
	punpckldq	%xmm3, %xmm2
	subpd	%xmm1, %xmm2
	movapd	%xmm2, %xmm1
	unpckhpd	%xmm2, %xmm1
	addsd	%xmm2, %xmm1
	divsd	%xmm1, %xmm0
	.seh_startepilogue
	addq	$120, %rsp
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
	.seh_handlerdata
	.long	$cppxdata$_RNvCs2i4to50FHNk_9prototype7bench_i@IMGREL
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype7bench_i,unique,14
	.seh_endproc
	.def	"?dtor$13@?0?_RNvCs2i4to50FHNk_9prototype7bench_i@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$13@?0?_RNvCs2i4to50FHNk_9prototype7bench_i@4HA":
.seh_proc "?dtor$13@?0?_RNvCs2i4to50FHNk_9prototype7bench_i@4HA"
.LBB13_13:
	movq	%rdx, 16(%rsp)
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	112(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, -48(%rbp)
	je	.LBB13_15
	movq	-40(%rbp), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	nop
.LBB13_15:
	.seh_startepilogue
	addq	$40, %rsp
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
.Lfunc_end13:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype7bench_i,unique,14
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvCs2i4to50FHNk_9prototype7bench_i,unique,2
	.p2align	2, 0x0
$cppxdata$_RNvCs2i4to50FHNk_9prototype7bench_i:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNvCs2i4to50FHNk_9prototype7bench_i@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RNvCs2i4to50FHNk_9prototype7bench_i@IMGREL
	.long	112
	.long	0
	.long	1
$stateUnwindMap$_RNvCs2i4to50FHNk_9prototype7bench_i:
	.long	-1
	.long	"?dtor$13@?0?_RNvCs2i4to50FHNk_9prototype7bench_i@4HA"@IMGREL
$ip2state$_RNvCs2i4to50FHNk_9prototype7bench_i:
	.long	.Lfunc_begin13@IMGREL
	.long	-1
	.long	.Ltmp150@IMGREL
	.long	0
	.long	.Ltmp155@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype7bench_i,unique,14

	.def	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_,unique,15
	.p2align	4
_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_:
.Lfunc_begin14:
.seh_proc _RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movq	%rcx, %rsi
	movq	(%rcx), %rdx
	leaq	(%rdx,%rdx), %rax
	cmpq	$5, %rax
	movl	$4, %edi
	cmovaeq	%rax, %rdi
	movq	8(%rcx), %r8
	movq	$48, 40(%rsp)
	movq	$8, 32(%rsp)
	leaq	48(%rsp), %rcx
	movq	%rdi, %r9
	callq	_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCs2i4to50FHNk_9prototype
	cmpl	$1, 48(%rsp)
	je	.LBB14_1
	movq	56(%rsp), %rax
	movq	%rax, 8(%rsi)
	movq	%rdi, (%rsi)
	.seh_startepilogue
	addq	$72, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB14_1:
	movq	56(%rsp), %rcx
	movq	64(%rsp), %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.Lfunc_end14:
	.seh_endproc

	.def	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecfE8grow_oneCs2i4to50FHNk_9prototype;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecfE8grow_oneCs2i4to50FHNk_9prototype,unique,16
	.p2align	4
_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecfE8grow_oneCs2i4to50FHNk_9prototype:
.Lfunc_begin15:
.seh_proc _RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecfE8grow_oneCs2i4to50FHNk_9prototype
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movq	%rcx, %rsi
	movq	(%rcx), %rdx
	leaq	(%rdx,%rdx), %rax
	cmpq	$5, %rax
	movl	$4, %edi
	cmovaeq	%rax, %rdi
	movq	8(%rcx), %r8
	movq	$4, 40(%rsp)
	movq	$4, 32(%rsp)
	leaq	48(%rsp), %rcx
	movq	%rdi, %r9
	callq	_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCs2i4to50FHNk_9prototype
	cmpl	$1, 48(%rsp)
	je	.LBB15_1
	movq	56(%rsp), %rax
	movq	%rax, 8(%rsi)
	movq	%rdi, (%rsi)
	.seh_startepilogue
	addq	$72, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB15_1:
	movq	56(%rsp), %rcx
	movq	64(%rsp), %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.Lfunc_end15:
	.seh_endproc

	.def	_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCs2i4to50FHNk_9prototype;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCs2i4to50FHNk_9prototype,unique,17
	.p2align	4
_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCs2i4to50FHNk_9prototype:
.Lfunc_begin16:
.seh_proc _RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCs2i4to50FHNk_9prototype
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
	movq	%r9, %rax
	movq	%rdx, %r9
	movq	%rcx, %rsi
	movq	112(%rsp), %r15
	mulq	120(%rsp)
	movq	%rax, %rdi
	seto	%al
	movabsq	$-9223372036854775808, %rcx
	subq	%r15, %rcx
	cmpq	%rcx, %rdi
	seta	%cl
	orb	%al, %cl
	movl	$1, %r14d
	je	.LBB16_2
	movl	$8, %eax
	xorl	%edi, %edi
	jmp	.LBB16_10
.LBB16_2:
	testq	%r9, %r9
	je	.LBB16_4
	movq	%r8, %rbx
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rbx, %r8
	movq	%rdi, %r9
	callq	*__imp_HeapReAlloc(%rip)
	testq	%rax, %rax
	jne	.LBB16_6
	jmp	.LBB16_9
.LBB16_4:
	testq	%rdi, %rdi
	je	.LBB16_5
	xorl	%edx, %edx
	movq	%rdi, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	jne	.LBB16_6
.LBB16_9:
	movq	%r15, 8(%rsi)
	movl	$16, %eax
	jmp	.LBB16_10
.LBB16_5:
	movq	%r15, %rax
.LBB16_6:
	movq	%rax, 8(%rsi)
	movl	$16, %eax
	xorl	%r14d, %r14d
.LBB16_10:
	movq	%rdi, (%rsi,%rax)
	movq	%r14, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	.seh_endepilogue
	retq
.Lfunc_end16:
	.seh_endproc

	.def	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRINtNtCsfQUUnEvlYZE_5alloc3vec3VecmENtB6_5Debug3fmtCs2i4to50FHNk_9prototype;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRINtNtCsfQUUnEvlYZE_5alloc3vec3VecmENtB6_5Debug3fmtCs2i4to50FHNk_9prototype,unique,18
	.p2align	4
_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRINtNtCsfQUUnEvlYZE_5alloc3vec3VecmENtB6_5Debug3fmtCs2i4to50FHNk_9prototype:
.Lfunc_begin17:
.seh_proc _RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRINtNtCsfQUUnEvlYZE_5alloc3vec3VecmENtB6_5Debug3fmtCs2i4to50FHNk_9prototype
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
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$104, %rsp
	.seh_stackalloc 104
	.seh_endprologue
	movq	%rdx, %rsi
	movq	(%rcx), %rax
	movq	8(%rax), %r12
	movq	16(%rax), %r13
	movq	(%rdx), %rdi
	movq	8(%rdx), %rbx
	movq	24(%rbx), %r14
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.207.llvm.17490583796818522722(%rip), %rdx
	movl	$1, %r8d
	movq	%rdi, %rcx
	callq	*%r14
	movl	%eax, %ecx
	testq	%r13, %r13
	je	.LBB17_20
	movq	%r12, 48(%rsp)
	movb	$1, %al
	testb	%cl, %cl
	jne	.LBB17_8
	testb	$-128, 18(%rsi)
	jne	.LBB17_3
	leaq	48(%rsp), %rcx
	movq	%rsi, %rdx
	callq	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRmNtB6_5Debug3fmtCs2i4to50FHNk_9prototype
	cmpq	$1, %r13
	je	.LBB17_9
	jmp	.LBB17_10
.LBB17_3:
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.41.llvm.17490583796818522722(%rip), %rdx
	movl	$1, %r8d
	movq	%rdi, %rcx
	callq	*%r14
	movl	%eax, %ecx
	movb	$1, %al
	testb	%cl, %cl
	jne	.LBB17_8
	movb	$1, 47(%rsp)
	movq	%rdi, 80(%rsp)
	movq	%rbx, 88(%rsp)
	leaq	47(%rsp), %rax
	movq	%rax, 96(%rsp)
	movq	16(%rsi), %rax
	movq	%rax, 72(%rsp)
	leaq	80(%rsp), %rax
	movq	%rax, 56(%rsp)
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.99.llvm.17490583796818522722(%rip), %rax
	movq	%rax, 64(%rsp)
	leaq	48(%rsp), %rcx
	leaq	56(%rsp), %rdx
	callq	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRmNtB6_5Debug3fmtCs2i4to50FHNk_9prototype
	testb	%al, %al
	je	.LBB17_5
	movb	$1, %al
.LBB17_8:
	cmpq	$1, %r13
	jne	.LBB17_10
.LBB17_9:
	movl	%eax, %ecx
.LBB17_20:
	movb	$1, %al
	testb	%cl, %cl
	jne	.LBB17_22
	movq	(%rsi), %rcx
	movq	8(%rsi), %rax
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.63.llvm.17490583796818522722(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	nop
.LBB17_22:
	.seh_startepilogue
	addq	$104, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r13
	popq	%r14
	popq	%r15
	.seh_endepilogue
	retq
.LBB17_5:
	movq	56(%rsp), %rcx
	movq	64(%rsp), %rax
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.38.llvm.17490583796818522722(%rip), %rdx
	movl	$2, %r8d
	callq	*24(%rax)
	cmpq	$1, %r13
	je	.LBB17_9
.LBB17_10:
	shlq	$2, %r13
	addq	$4, %r12
	addq	$-4, %r13
	leaq	48(%rsp), %rbx
	leaq	47(%rsp), %rbp
	leaq	80(%rsp), %r15
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.99.llvm.17490583796818522722(%rip), %rdi
	leaq	56(%rsp), %r14
	jmp	.LBB17_11
.LBB17_16:
	movb	$1, %cl
	.p2align	4
.LBB17_19:
	addq	$4, %r12
	movl	%ecx, %eax
	addq	$-4, %r13
	je	.LBB17_20
.LBB17_11:
	movq	%r12, 48(%rsp)
	movb	$1, %cl
	testb	$1, %al
	jne	.LBB17_19
	testb	$-128, 18(%rsi)
	jne	.LBB17_15
	movq	(%rsi), %rcx
	movq	8(%rsi), %rax
	movl	$2, %r8d
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.35.llvm.17490583796818522722(%rip), %rdx
	callq	*24(%rax)
	movb	$1, %cl
	testb	%al, %al
	jne	.LBB17_19
	movq	%rbx, %rcx
	movq	%rsi, %rdx
	callq	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRmNtB6_5Debug3fmtCs2i4to50FHNk_9prototype
	jmp	.LBB17_18
	.p2align	4
.LBB17_15:
	movb	$1, 47(%rsp)
	movups	(%rsi), %xmm0
	movaps	%xmm0, 80(%rsp)
	movq	%rbp, 96(%rsp)
	movq	16(%rsi), %rax
	movq	%rax, 72(%rsp)
	movq	%r15, 56(%rsp)
	movq	%rdi, 64(%rsp)
	movq	%rbx, %rcx
	movq	%r14, %rdx
	callq	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRmNtB6_5Debug3fmtCs2i4to50FHNk_9prototype
	testb	%al, %al
	jne	.LBB17_16
	movq	56(%rsp), %rcx
	movq	64(%rsp), %rax
	movl	$2, %r8d
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.38.llvm.17490583796818522722(%rip), %rdx
	callq	*24(%rax)
.LBB17_18:
	movl	%eax, %ecx
	jmp	.LBB17_19
.Lfunc_end17:
	.seh_endproc

	.def	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRINtNtCsfQUUnEvlYZE_5alloc3vec3VecsENtB6_5Debug3fmtCs2i4to50FHNk_9prototype;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRINtNtCsfQUUnEvlYZE_5alloc3vec3VecsENtB6_5Debug3fmtCs2i4to50FHNk_9prototype,unique,19
	.p2align	4
_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRINtNtCsfQUUnEvlYZE_5alloc3vec3VecsENtB6_5Debug3fmtCs2i4to50FHNk_9prototype:
.Lfunc_begin18:
.seh_proc _RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRINtNtCsfQUUnEvlYZE_5alloc3vec3VecsENtB6_5Debug3fmtCs2i4to50FHNk_9prototype
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
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$104, %rsp
	.seh_stackalloc 104
	.seh_endprologue
	movq	%rdx, %rsi
	movq	(%rcx), %rax
	movq	8(%rax), %r12
	movq	16(%rax), %r13
	movq	(%rdx), %rdi
	movq	8(%rdx), %rbx
	movq	24(%rbx), %r14
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.207.llvm.17490583796818522722(%rip), %rdx
	movl	$1, %r8d
	movq	%rdi, %rcx
	callq	*%r14
	movl	%eax, %ecx
	testq	%r13, %r13
	je	.LBB18_20
	movq	%r12, 48(%rsp)
	movb	$1, %al
	testb	%cl, %cl
	jne	.LBB18_8
	testb	$-128, 18(%rsi)
	jne	.LBB18_3
	leaq	48(%rsp), %rcx
	movq	%rsi, %rdx
	callq	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRsNtB6_5Debug3fmtCs2i4to50FHNk_9prototype
	cmpq	$1, %r13
	je	.LBB18_9
	jmp	.LBB18_10
.LBB18_3:
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.41.llvm.17490583796818522722(%rip), %rdx
	movl	$1, %r8d
	movq	%rdi, %rcx
	callq	*%r14
	movl	%eax, %ecx
	movb	$1, %al
	testb	%cl, %cl
	jne	.LBB18_8
	movb	$1, 47(%rsp)
	movq	%rdi, 80(%rsp)
	movq	%rbx, 88(%rsp)
	leaq	47(%rsp), %rax
	movq	%rax, 96(%rsp)
	movq	16(%rsi), %rax
	movq	%rax, 72(%rsp)
	leaq	80(%rsp), %rax
	movq	%rax, 56(%rsp)
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.99.llvm.17490583796818522722(%rip), %rax
	movq	%rax, 64(%rsp)
	leaq	48(%rsp), %rcx
	leaq	56(%rsp), %rdx
	callq	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRsNtB6_5Debug3fmtCs2i4to50FHNk_9prototype
	testb	%al, %al
	je	.LBB18_5
	movb	$1, %al
.LBB18_8:
	cmpq	$1, %r13
	jne	.LBB18_10
.LBB18_9:
	movl	%eax, %ecx
.LBB18_20:
	movb	$1, %al
	testb	%cl, %cl
	jne	.LBB18_22
	movq	(%rsi), %rcx
	movq	8(%rsi), %rax
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.63.llvm.17490583796818522722(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	nop
.LBB18_22:
	.seh_startepilogue
	addq	$104, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r13
	popq	%r14
	popq	%r15
	.seh_endepilogue
	retq
.LBB18_5:
	movq	56(%rsp), %rcx
	movq	64(%rsp), %rax
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.38.llvm.17490583796818522722(%rip), %rdx
	movl	$2, %r8d
	callq	*24(%rax)
	cmpq	$1, %r13
	je	.LBB18_9
.LBB18_10:
	addq	%r13, %r13
	addq	$2, %r12
	addq	$-2, %r13
	leaq	48(%rsp), %rbx
	leaq	47(%rsp), %rbp
	leaq	80(%rsp), %r15
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.99.llvm.17490583796818522722(%rip), %rdi
	leaq	56(%rsp), %r14
	jmp	.LBB18_11
.LBB18_16:
	movb	$1, %cl
	.p2align	4
.LBB18_19:
	addq	$2, %r12
	movl	%ecx, %eax
	addq	$-2, %r13
	je	.LBB18_20
.LBB18_11:
	movq	%r12, 48(%rsp)
	movb	$1, %cl
	testb	$1, %al
	jne	.LBB18_19
	testb	$-128, 18(%rsi)
	jne	.LBB18_15
	movq	(%rsi), %rcx
	movq	8(%rsi), %rax
	movl	$2, %r8d
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.35.llvm.17490583796818522722(%rip), %rdx
	callq	*24(%rax)
	movb	$1, %cl
	testb	%al, %al
	jne	.LBB18_19
	movq	%rbx, %rcx
	movq	%rsi, %rdx
	callq	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRsNtB6_5Debug3fmtCs2i4to50FHNk_9prototype
	jmp	.LBB18_18
	.p2align	4
.LBB18_15:
	movb	$1, 47(%rsp)
	movups	(%rsi), %xmm0
	movaps	%xmm0, 80(%rsp)
	movq	%rbp, 96(%rsp)
	movq	16(%rsi), %rax
	movq	%rax, 72(%rsp)
	movq	%r15, 56(%rsp)
	movq	%rdi, 64(%rsp)
	movq	%rbx, %rcx
	movq	%r14, %rdx
	callq	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRsNtB6_5Debug3fmtCs2i4to50FHNk_9prototype
	testb	%al, %al
	jne	.LBB18_16
	movq	56(%rsp), %rcx
	movq	64(%rsp), %rax
	movl	$2, %r8d
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.38.llvm.17490583796818522722(%rip), %rdx
	callq	*24(%rax)
.LBB18_18:
	movl	%eax, %ecx
	jmp	.LBB18_19
.Lfunc_end18:
	.seh_endproc

	.def	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRINtNtCsfQUUnEvlYZE_5alloc3vec3VectENtB6_5Debug3fmtCs2i4to50FHNk_9prototype;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRINtNtCsfQUUnEvlYZE_5alloc3vec3VectENtB6_5Debug3fmtCs2i4to50FHNk_9prototype,unique,20
	.p2align	4
_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRINtNtCsfQUUnEvlYZE_5alloc3vec3VectENtB6_5Debug3fmtCs2i4to50FHNk_9prototype:
.Lfunc_begin19:
.seh_proc _RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRINtNtCsfQUUnEvlYZE_5alloc3vec3VectENtB6_5Debug3fmtCs2i4to50FHNk_9prototype
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
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$104, %rsp
	.seh_stackalloc 104
	.seh_endprologue
	movq	%rdx, %rsi
	movq	(%rcx), %rax
	movq	8(%rax), %r12
	movq	16(%rax), %r13
	movq	(%rdx), %rdi
	movq	8(%rdx), %rbx
	movq	24(%rbx), %r14
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.207.llvm.17490583796818522722(%rip), %rdx
	movl	$1, %r8d
	movq	%rdi, %rcx
	callq	*%r14
	movl	%eax, %ecx
	testq	%r13, %r13
	je	.LBB19_20
	movq	%r12, 48(%rsp)
	movb	$1, %al
	testb	%cl, %cl
	jne	.LBB19_8
	testb	$-128, 18(%rsi)
	jne	.LBB19_3
	leaq	48(%rsp), %rcx
	movq	%rsi, %rdx
	callq	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRtNtB6_5Debug3fmtCs2i4to50FHNk_9prototype
	cmpq	$1, %r13
	je	.LBB19_9
	jmp	.LBB19_10
.LBB19_3:
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.41.llvm.17490583796818522722(%rip), %rdx
	movl	$1, %r8d
	movq	%rdi, %rcx
	callq	*%r14
	movl	%eax, %ecx
	movb	$1, %al
	testb	%cl, %cl
	jne	.LBB19_8
	movb	$1, 47(%rsp)
	movq	%rdi, 80(%rsp)
	movq	%rbx, 88(%rsp)
	leaq	47(%rsp), %rax
	movq	%rax, 96(%rsp)
	movq	16(%rsi), %rax
	movq	%rax, 72(%rsp)
	leaq	80(%rsp), %rax
	movq	%rax, 56(%rsp)
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.99.llvm.17490583796818522722(%rip), %rax
	movq	%rax, 64(%rsp)
	leaq	48(%rsp), %rcx
	leaq	56(%rsp), %rdx
	callq	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRtNtB6_5Debug3fmtCs2i4to50FHNk_9prototype
	testb	%al, %al
	je	.LBB19_5
	movb	$1, %al
.LBB19_8:
	cmpq	$1, %r13
	jne	.LBB19_10
.LBB19_9:
	movl	%eax, %ecx
.LBB19_20:
	movb	$1, %al
	testb	%cl, %cl
	jne	.LBB19_22
	movq	(%rsi), %rcx
	movq	8(%rsi), %rax
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.63.llvm.17490583796818522722(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	nop
.LBB19_22:
	.seh_startepilogue
	addq	$104, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r13
	popq	%r14
	popq	%r15
	.seh_endepilogue
	retq
.LBB19_5:
	movq	56(%rsp), %rcx
	movq	64(%rsp), %rax
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.38.llvm.17490583796818522722(%rip), %rdx
	movl	$2, %r8d
	callq	*24(%rax)
	cmpq	$1, %r13
	je	.LBB19_9
.LBB19_10:
	addq	%r13, %r13
	addq	$2, %r12
	addq	$-2, %r13
	leaq	48(%rsp), %rbx
	leaq	47(%rsp), %rbp
	leaq	80(%rsp), %r15
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.99.llvm.17490583796818522722(%rip), %rdi
	leaq	56(%rsp), %r14
	jmp	.LBB19_11
.LBB19_16:
	movb	$1, %cl
	.p2align	4
.LBB19_19:
	addq	$2, %r12
	movl	%ecx, %eax
	addq	$-2, %r13
	je	.LBB19_20
.LBB19_11:
	movq	%r12, 48(%rsp)
	movb	$1, %cl
	testb	$1, %al
	jne	.LBB19_19
	testb	$-128, 18(%rsi)
	jne	.LBB19_15
	movq	(%rsi), %rcx
	movq	8(%rsi), %rax
	movl	$2, %r8d
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.35.llvm.17490583796818522722(%rip), %rdx
	callq	*24(%rax)
	movb	$1, %cl
	testb	%al, %al
	jne	.LBB19_19
	movq	%rbx, %rcx
	movq	%rsi, %rdx
	callq	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRtNtB6_5Debug3fmtCs2i4to50FHNk_9prototype
	jmp	.LBB19_18
	.p2align	4
.LBB19_15:
	movb	$1, 47(%rsp)
	movups	(%rsi), %xmm0
	movaps	%xmm0, 80(%rsp)
	movq	%rbp, 96(%rsp)
	movq	16(%rsi), %rax
	movq	%rax, 72(%rsp)
	movq	%r15, 56(%rsp)
	movq	%rdi, 64(%rsp)
	movq	%rbx, %rcx
	movq	%r14, %rdx
	callq	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRtNtB6_5Debug3fmtCs2i4to50FHNk_9prototype
	testb	%al, %al
	jne	.LBB19_16
	movq	56(%rsp), %rcx
	movq	64(%rsp), %rax
	movl	$2, %r8d
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.38.llvm.17490583796818522722(%rip), %rdx
	callq	*24(%rax)
.LBB19_18:
	movl	%eax, %ecx
	jmp	.LBB19_19
.Lfunc_end19:
	.seh_endproc

	.def	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRmNtB6_5Debug3fmtCs2i4to50FHNk_9prototype;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRmNtB6_5Debug3fmtCs2i4to50FHNk_9prototype,unique,21
	.p2align	4
_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRmNtB6_5Debug3fmtCs2i4to50FHNk_9prototype:
.Lfunc_begin20:
.seh_proc _RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRmNtB6_5Debug3fmtCs2i4to50FHNk_9prototype
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$64, %rsp
	.seh_stackalloc 64
	.seh_endprologue
	movq	(%rcx), %rax
	movl	16(%rdx), %ecx
	testl	$33554432, %ecx
	jne	.LBB20_11
	testl	$67108864, %ecx
	jne	.LBB20_13
	movl	(%rax), %ecx
	movl	$10, %r8d
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.203.llvm.17490583796818522722(%rip), %rax
	movl	%ecx, %r9d
	cmpl	$1000, %ecx
	jb	.LBB20_5
	movl	$3518437209, %r10d
	movl	%ecx, %r11d
	.p2align	4
.LBB20_4:
	movl	%r11d, %r9d
	imulq	%r10, %r9
	shrq	$45, %r9
	imull	$10000, %r9d, %esi
	movl	%r11d, %edi
	subl	%esi, %edi
	imull	$5243, %edi, %esi
	shrl	$19, %esi
	imull	$100, %esi, %ebx
	subl	%ebx, %edi
	movzwl	%di, %edi
	movzwl	(%rax,%rsi,2), %esi
	movd	%esi, %xmm0
	pinsrw	$1, (%rax,%rdi,2), %xmm0
	movd	%xmm0, 50(%rsp,%r8)
	addq	$-4, %r8
	cmpl	$9999999, %r11d
	movl	%r9d, %r11d
	ja	.LBB20_4
.LBB20_5:
	cmpl	$9, %r9d
	jbe	.LBB20_7
	movzwl	%r9w, %r10d
	shrl	$2, %r10d
	imull	$5243, %r10d, %r10d
	shrl	$17, %r10d
	imull	$100, %r10d, %r11d
	subl	%r11d, %r9d
	movzwl	%r9w, %r9d
	movzwl	(%rax,%r9,2), %r9d
	movw	%r9w, 52(%rsp,%r8)
	addq	$-2, %r8
	movl	%r10d, %r9d
.LBB20_7:
	testl	%ecx, %ecx
	je	.LBB20_9
	testl	%r9d, %r9d
	je	.LBB20_10
.LBB20_9:
	andl	$15, %r9d
	movzbl	1(%rax,%r9,2), %eax
	movb	%al, 53(%rsp,%r8)
	decq	%r8
.LBB20_10:
	movl	$10, %eax
	subq	%r8, %rax
	leaq	(%rsp,%r8), %rcx
	addq	$54, %rcx
	movq	%rax, 40(%rsp)
	movq	%rcx, 32(%rsp)
	movl	$1, %r8d
	movq	%rdx, %rcx
	movb	$1, %dl
	xorl	%r9d, %r9d
	jmp	.LBB20_16
.LBB20_11:
	movl	(%rax), %r9d
	xorl	%eax, %eax
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.1.llvm.17490583796818522722(%rip), %rcx
	movl	%r9d, %r8d
	.p2align	4
.LBB20_12:
	shrl	$4, %r8d
	andl	$15, %r9d
	movzbl	(%r9,%rcx), %r9d
	movb	%r9b, 61(%rsp,%rax)
	decq	%rax
	movl	%r8d, %r9d
	testl	%r8d, %r8d
	jne	.LBB20_12
	jmp	.LBB20_15
.LBB20_13:
	movl	(%rax), %r9d
	xorl	%eax, %eax
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.415.llvm.17490583796818522722(%rip), %rcx
	movl	%r9d, %r8d
	.p2align	4
.LBB20_14:
	shrl	$4, %r8d
	andl	$15, %r9d
	movzbl	(%r9,%rcx), %r9d
	movb	%r9b, 61(%rsp,%rax)
	decq	%rax
	movl	%r8d, %r9d
	testl	%r8d, %r8d
	jne	.LBB20_14
.LBB20_15:
	leaq	(%rsp,%rax), %rcx
	addq	$62, %rcx
	negq	%rax
	movq	%rax, 40(%rsp)
	movq	%rcx, 32(%rsp)
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.401.llvm.17490583796818522722(%rip), %r8
	movl	$2, %r9d
	movq	%rdx, %rcx
	movb	$1, %dl
.LBB20_16:
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter12pad_integral
	nop
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end20:
	.seh_endproc

	.def	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRsNtB6_5Debug3fmtCs2i4to50FHNk_9prototype;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRsNtB6_5Debug3fmtCs2i4to50FHNk_9prototype,unique,22
	.p2align	4
_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRsNtB6_5Debug3fmtCs2i4to50FHNk_9prototype:
.Lfunc_begin21:
.seh_proc _RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRsNtB6_5Debug3fmtCs2i4to50FHNk_9prototype
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movq	%rdx, %rax
	movq	(%rcx), %rcx
	movl	16(%rdx), %edx
	testl	$33554432, %edx
	jne	.LBB21_4
	testl	$67108864, %edx
	jne	.LBB21_7
	movzwl	(%rcx), %ecx
	movl	%ecx, %edx
	negw	%dx
	cmovsw	%cx, %dx
	movzwl	%dx, %r9d
	cmpl	$1000, %r9d
	jb	.LBB21_12
	shrl	$4, %r9d
	imull	$839, %r9d, %r9d
	shrl	$19, %r9d
	imull	$10000, %r9d, %r8d
	subl	%r8d, %edx
	movzwl	%dx, %r8d
	shrl	$2, %r8d
	imull	$5243, %r8d, %r8d
	shrl	$17, %r8d
	imull	$100, %r8d, %r10d
	subl	%r10d, %edx
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.203.llvm.17490583796818522722(%rip), %r10
	movzwl	%dx, %edx
	movzwl	(%r10,%r8,2), %r8d
	movd	%r8d, %xmm0
	pinsrw	$1, (%r10,%rdx,2), %xmm0
	movd	%xmm0, 60(%rsp)
	movl	$1, %r8d
	jmp	.LBB21_14
.LBB21_4:
	movzwl	(%rcx), %edx
	xorl	%ecx, %ecx
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.1.llvm.17490583796818522722(%rip), %r8
	.p2align	4
.LBB21_5:
	movzwl	%dx, %r9d
	movl	%r9d, %edx
	shrl	$4, %edx
	andl	$15, %r9d
	movzbl	(%r9,%r8), %r9d
	movb	%r9b, 67(%rsp,%rcx)
	decq	%rcx
	testl	%edx, %edx
	jne	.LBB21_5
	leaq	(%rsp,%rcx), %rdx
	addq	$68, %rdx
	jmp	.LBB21_10
.LBB21_7:
	movzwl	(%rcx), %edx
	xorl	%ecx, %ecx
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.415.llvm.17490583796818522722(%rip), %r8
	.p2align	4
.LBB21_8:
	movzwl	%dx, %r9d
	movl	%r9d, %edx
	shrl	$4, %edx
	andl	$15, %r9d
	movzbl	(%r9,%r8), %r9d
	movb	%r9b, 71(%rsp,%rcx)
	decq	%rcx
	testl	%edx, %edx
	jne	.LBB21_8
	leaq	(%rsp,%rcx), %rdx
	addq	$72, %rdx
.LBB21_10:
	negq	%rcx
	movq	%rcx, 40(%rsp)
	movq	%rdx, 32(%rsp)
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.401.llvm.17490583796818522722(%rip), %r8
	movl	$2, %r9d
	movq	%rax, %rcx
	movb	$1, %dl
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter12pad_integral
	nop
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB21_12:
	movl	$5, %r8d
	cmpw	$10, %dx
	jb	.LBB21_15
	shrl	$2, %r9d
	imull	$5243, %r9d, %r9d
	shrl	$17, %r9d
	imull	$100, %r9d, %r8d
	subl	%r8d, %edx
	movzwl	%dx, %edx
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.203.llvm.17490583796818522722(%rip), %r8
	movzwl	(%r8,%rdx,2), %edx
	movw	%dx, 62(%rsp)
	movl	$3, %r8d
.LBB21_14:
	movl	%r9d, %edx
.LBB21_15:
	testw	%dx, %dx
	sete	%r9b
	testw	%cx, %cx
	setne	%r10b
	testb	%r9b, %r10b
	jne	.LBB21_17
	andl	$15, %edx
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.203.llvm.17490583796818522722(%rip), %r9
	movzbl	1(%r9,%rdx,2), %edx
	movb	%dl, 58(%rsp,%r8)
	decq	%r8
.LBB21_17:
	testw	%cx, %cx
	setns	%dl
	movl	$5, %ecx
	subq	%r8, %rcx
	addq	%rsp, %r8
	addq	$59, %r8
	movq	%rcx, 40(%rsp)
	movq	%r8, 32(%rsp)
	movl	$1, %r8d
	movq	%rax, %rcx
	xorl	%r9d, %r9d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter12pad_integral
	nop
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.Lfunc_end21:
	.seh_endproc

	.def	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRtNtB6_5Debug3fmtCs2i4to50FHNk_9prototype;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRtNtB6_5Debug3fmtCs2i4to50FHNk_9prototype,unique,23
	.p2align	4
_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRtNtB6_5Debug3fmtCs2i4to50FHNk_9prototype:
.Lfunc_begin22:
.seh_proc _RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRtNtB6_5Debug3fmtCs2i4to50FHNk_9prototype
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movq	(%rcx), %rax
	movl	16(%rdx), %ecx
	testl	$33554432, %ecx
	jne	.LBB22_4
	testl	$67108864, %ecx
	jne	.LBB22_7
	movzwl	(%rax), %eax
	cmpl	$1000, %eax
	jb	.LBB22_12
	movzwl	%ax, %ecx
	shrl	$4, %ecx
	imull	$839, %ecx, %ecx
	shrl	$19, %ecx
	imull	$10000, %ecx, %r8d
	movl	%eax, %r9d
	subl	%r8d, %r9d
	movzwl	%r9w, %r8d
	shrl	$2, %r8d
	imull	$5243, %r8d, %r8d
	shrl	$17, %r8d
	imull	$100, %r8d, %r10d
	subl	%r10d, %r9d
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.203.llvm.17490583796818522722(%rip), %r10
	movzwl	%r9w, %r9d
	movzwl	(%r10,%r8,2), %r8d
	movd	%r8d, %xmm0
	pinsrw	$1, (%r10,%r9,2), %xmm0
	movd	%xmm0, 60(%rsp)
	movl	$1, %r8d
	jmp	.LBB22_14
.LBB22_4:
	movzwl	(%rax), %ecx
	xorl	%eax, %eax
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.1.llvm.17490583796818522722(%rip), %r8
	.p2align	4
.LBB22_5:
	movzwl	%cx, %r9d
	movl	%r9d, %ecx
	shrl	$4, %ecx
	andl	$15, %r9d
	movzbl	(%r9,%r8), %r9d
	movb	%r9b, 67(%rsp,%rax)
	decq	%rax
	testl	%ecx, %ecx
	jne	.LBB22_5
	leaq	(%rsp,%rax), %rcx
	addq	$68, %rcx
	jmp	.LBB22_10
.LBB22_7:
	movzwl	(%rax), %ecx
	xorl	%eax, %eax
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.415.llvm.17490583796818522722(%rip), %r8
	.p2align	4
.LBB22_8:
	movzwl	%cx, %r9d
	movl	%r9d, %ecx
	shrl	$4, %ecx
	andl	$15, %r9d
	movzbl	(%r9,%r8), %r9d
	movb	%r9b, 71(%rsp,%rax)
	decq	%rax
	testl	%ecx, %ecx
	jne	.LBB22_8
	leaq	(%rsp,%rax), %rcx
	addq	$72, %rcx
.LBB22_10:
	negq	%rax
	movq	%rax, 40(%rsp)
	movq	%rcx, 32(%rsp)
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.401.llvm.17490583796818522722(%rip), %r8
	movl	$2, %r9d
	movq	%rdx, %rcx
	movb	$1, %dl
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter12pad_integral
	nop
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB22_12:
	movl	$5, %r8d
	movl	%eax, %ecx
	cmpw	$10, %ax
	jb	.LBB22_14
	movzwl	%ax, %ecx
	shrl	$2, %ecx
	imull	$5243, %ecx, %ecx
	shrl	$17, %ecx
	imull	$100, %ecx, %r8d
	movl	%eax, %r9d
	subl	%r8d, %r9d
	movzwl	%r9w, %r8d
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.203.llvm.17490583796818522722(%rip), %r9
	movzwl	(%r9,%r8,2), %r8d
	movw	%r8w, 62(%rsp)
	movl	$3, %r8d
.LBB22_14:
	testw	%cx, %cx
	sete	%r9b
	testw	%ax, %ax
	setne	%al
	testb	%r9b, %al
	jne	.LBB22_16
	andl	$15, %ecx
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.203.llvm.17490583796818522722(%rip), %rax
	movzbl	1(%rax,%rcx,2), %eax
	movb	%al, 58(%rsp,%r8)
	decq	%r8
.LBB22_16:
	movl	$5, %eax
	subq	%r8, %rax
	leaq	(%rsp,%r8), %rcx
	addq	$59, %rcx
	movq	%rax, 40(%rsp)
	movq	%rcx, 32(%rsp)
	movl	$1, %r8d
	movq	%rdx, %rcx
	movb	$1, %dl
	xorl	%r9d, %r9d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter12pad_integral
	nop
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.Lfunc_end22:
	.seh_endproc

	.def	_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtReNtB6_7Display3fmtCs2i4to50FHNk_9prototype;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtReNtB6_7Display3fmtCs2i4to50FHNk_9prototype,unique,24
	.p2align	4
_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtReNtB6_7Display3fmtCs2i4to50FHNk_9prototype:
.Lfunc_begin23:
	movq	%rdx, %rax
	movq	(%rcx), %rdx
	movq	8(%rcx), %r8
	movq	%rax, %rcx
	jmp	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
.Lfunc_end23:

	.def	_RNvXsq_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXsq_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt,unique,25
	.p2align	4
_RNvXsq_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt:
.Lfunc_begin24:
	movq	%rdx, %rax
	movq	8(%rcx), %rdx
	movq	16(%rcx), %r8
	movq	%rax, %rcx
	jmp	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
.Lfunc_end24:

	.def	d014_baseline_i16;
	.scl	2;
	.type	32;
	.endef
	.globl	__real@46fffe00
	.section	.rdata,"dr",discard,__real@46fffe00
	.p2align	2, 0x0
__real@46fffe00:
	.long	0x46fffe00
	.globl	__real@c7000000
	.section	.rdata,"dr",discard,__real@c7000000
	.p2align	2, 0x0
__real@c7000000:
	.long	0xc7000000
	.section	.text,"xr",one_only,d014_baseline_i16,unique,26
	.globl	d014_baseline_i16
	.p2align	4
d014_baseline_i16:
.Lfunc_begin25:
.seh_proc d014_baseline_i16
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
	subq	$184, %rsp
	.seh_stackalloc 184
	movaps	%xmm14, 160(%rsp)
	.seh_savexmm %xmm14, 160
	movaps	%xmm13, 144(%rsp)
	.seh_savexmm %xmm13, 144
	movaps	%xmm12, 128(%rsp)
	.seh_savexmm %xmm12, 128
	movaps	%xmm11, 112(%rsp)
	.seh_savexmm %xmm11, 112
	movaps	%xmm10, 96(%rsp)
	.seh_savexmm %xmm10, 96
	movaps	%xmm9, 80(%rsp)
	.seh_savexmm %xmm9, 80
	movaps	%xmm8, 64(%rsp)
	.seh_savexmm %xmm8, 64
	movaps	%xmm7, 48(%rsp)
	.seh_savexmm %xmm7, 48
	movaps	%xmm6, 32(%rsp)
	.seh_savexmm %xmm6, 32
	.seh_endprologue
	movq	%r9, %rsi
	movq	%r8, %rdi
	movq	%rcx, %rbx
	testq	%rdx, %rdx
	je	.LBB25_1
	leaq	(,%rdx,4), %rcx
	addq	$-4, %rcx
	xorps	%xmm0, %xmm0
	movq	%rbx, %rax
	cmpq	$28, %rcx
	jb	.LBB25_6
	shrq	$2, %rcx
	incq	%rcx
	movq	%rcx, %r8
	andq	$-8, %r8
	leaq	(%rbx,%r8,4), %rax
	xorps	%xmm0, %xmm0
	xorl	%r9d, %r9d
	movaps	__xmm@7fffffff7fffffff7fffffff7fffffff(%rip), %xmm1
	xorps	%xmm2, %xmm2
	.p2align	4
.LBB25_4:
	movups	(%rbx,%r9,4), %xmm3
	movups	16(%rbx,%r9,4), %xmm4
	andps	%xmm1, %xmm3
	andps	%xmm1, %xmm4
	movaps	%xmm0, %xmm5
	maxps	%xmm3, %xmm0
	movaps	%xmm0, %xmm3
	cmpunordps	%xmm0, %xmm3
	andps	%xmm3, %xmm5
	andnps	%xmm0, %xmm3
	movaps	%xmm3, %xmm0
	orps	%xmm5, %xmm0
	movaps	%xmm2, %xmm3
	maxps	%xmm4, %xmm2
	movaps	%xmm2, %xmm4
	cmpunordps	%xmm2, %xmm4
	andps	%xmm4, %xmm3
	andnps	%xmm2, %xmm4
	movaps	%xmm4, %xmm2
	orps	%xmm3, %xmm2
	addq	$8, %r9
	cmpq	%r9, %r8
	jne	.LBB25_4
	movaps	%xmm0, %xmm1
	maxps	%xmm2, %xmm1
	movaps	%xmm1, %xmm2
	cmpunordps	%xmm1, %xmm2
	andps	%xmm2, %xmm0
	andnps	%xmm1, %xmm2
	orps	%xmm0, %xmm2
	pshufd	$255, %xmm2, %xmm1
	pshufd	$238, %xmm2, %xmm3
	pshufd	$245, %xmm2, %xmm4
	movaps	%xmm2, %xmm0
	cmpunordss	%xmm2, %xmm0
	movaps	%xmm0, %xmm5
	andps	%xmm4, %xmm5
	maxss	%xmm2, %xmm4
	andnps	%xmm4, %xmm0
	orps	%xmm5, %xmm0
	movdqa	%xmm3, %xmm2
	maxss	%xmm0, %xmm2
	cmpunordss	%xmm0, %xmm0
	movaps	%xmm0, %xmm4
	andnps	%xmm2, %xmm4
	andps	%xmm3, %xmm0
	orps	%xmm4, %xmm0
	movdqa	%xmm1, %xmm2
	maxss	%xmm0, %xmm2
	cmpunordss	%xmm0, %xmm0
	movaps	%xmm0, %xmm3
	andnps	%xmm2, %xmm3
	andps	%xmm1, %xmm0
	orps	%xmm3, %xmm0
	cmpq	%r8, %rcx
	je	.LBB25_8
.LBB25_6:
	leaq	(%rbx,%rdx,4), %rcx
	movaps	__xmm@7fffffff7fffffff7fffffff7fffffff(%rip), %xmm1
	movaps	%xmm0, %xmm2
	.p2align	4
.LBB25_7:
	movss	(%rax), %xmm0
	addq	$4, %rax
	andps	%xmm1, %xmm0
	movaps	%xmm2, %xmm3
	maxss	%xmm0, %xmm3
	movaps	%xmm3, %xmm0
	cmpunordss	%xmm3, %xmm0
	movaps	%xmm0, %xmm4
	andnps	%xmm3, %xmm4
	andps	%xmm2, %xmm0
	orps	%xmm4, %xmm0
	movaps	%xmm0, %xmm2
	cmpq	%rcx, %rax
	jne	.LBB25_7
	jmp	.LBB25_8
.LBB25_1:
	xorps	%xmm0, %xmm0
.LBB25_8:
	movd	%xmm0, %eax
	testl	%eax, %eax
	setns	%cl
	movl	%eax, %r8d
	andl	$2147483647, %r8d
	addl	$-8388608, %r8d
	cmpl	$2130706432, %r8d
	setb	%r8b
	andb	%cl, %r8b
	decl	%eax
	cmpl	$8388607, %eax
	setb	%al
	orb	%r8b, %al
	je	.LBB25_9
	cmpq	%rsi, %rdx
	cmovbq	%rdx, %rsi
	testq	%rsi, %rsi
	je	.LBB25_19
	movss	__real@46fffe00(%rip), %xmm11
	movaps	%xmm11, %xmm12
	movaps	%xmm0, %xmm10
	divss	%xmm0, %xmm12
	cmpq	$4, %rsi
	jae	.LBB25_13
	xorl	%r14d, %r14d
	jmp	.LBB25_16
.LBB25_9:
	addq	%rsi, %rsi
	movq	%rdi, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	memset
	xorps	%xmm0, %xmm0
	jmp	.LBB25_19
.LBB25_13:
	movabsq	$2305843009213693948, %r14
	andq	%rsi, %r14
	movaps	%xmm12, %xmm13
	shufps	$0, %xmm12, %xmm13
	leaq	(%rsi,%rsi), %r15
	andq	$-8, %r15
	xorl	%r12d, %r12d
	movss	__real@c7000000(%rip), %xmm14
	.p2align	4
.LBB25_14:
	movups	(%rbx,%r12,2), %xmm7
	mulps	%xmm13, %xmm7
	movaps	%xmm7, %xmm0
	shufps	$255, %xmm7, %xmm0
	callq	rintf
	movaps	%xmm0, %xmm6
	movaps	%xmm7, %xmm0
	unpckhpd	%xmm7, %xmm0
	callq	rintf
	movaps	%xmm0, %xmm8
	unpcklps	%xmm6, %xmm8
	movaps	%xmm7, %xmm0
	callq	rintf
	movaps	%xmm0, %xmm9
	movshdup	%xmm7, %xmm0
	callq	rintf
	movaps	%xmm14, %xmm1
	maxss	%xmm0, %xmm1
	movaps	%xmm11, %xmm0
	minss	%xmm1, %xmm0
	cvttss2si	%xmm0, %eax
	movaps	%xmm14, %xmm0
	maxss	%xmm9, %xmm0
	movaps	%xmm11, %xmm1
	minss	%xmm0, %xmm1
	cvttss2si	%xmm1, %ecx
	movd	%ecx, %xmm0
	pinsrw	$1, %eax, %xmm0
	movaps	%xmm14, %xmm1
	maxss	%xmm8, %xmm1
	movaps	%xmm11, %xmm2
	minss	%xmm1, %xmm2
	cvttss2si	%xmm2, %eax
	pinsrw	$2, %eax, %xmm0
	movaps	%xmm14, %xmm1
	maxss	%xmm6, %xmm1
	movaps	%xmm11, %xmm2
	minss	%xmm1, %xmm2
	cvttss2si	%xmm2, %eax
	pinsrw	$3, %eax, %xmm0
	movq	%xmm0, (%rdi,%r12)
	addq	$8, %r12
	cmpq	%r12, %r15
	jne	.LBB25_14
	cmpq	%r14, %rsi
	je	.LBB25_18
.LBB25_16:
	movss	__real@c7000000(%rip), %xmm6
	.p2align	4
.LBB25_17:
	leaq	1(%r14), %r15
	movss	(%rbx,%r14,4), %xmm0
	mulss	%xmm12, %xmm0
	callq	rintf
	movaps	%xmm6, %xmm1
	maxss	%xmm0, %xmm1
	movaps	%xmm11, %xmm0
	minss	%xmm1, %xmm0
	cvttss2si	%xmm0, %eax
	movw	%ax, (%rdi,%r14,2)
	movq	%r15, %r14
	cmpq	%r15, %rsi
	jne	.LBB25_17
.LBB25_18:
	movaps	%xmm10, %xmm0
.LBB25_19:
	movaps	32(%rsp), %xmm6
	movaps	48(%rsp), %xmm7
	movaps	64(%rsp), %xmm8
	movaps	80(%rsp), %xmm9
	movaps	96(%rsp), %xmm10
	movaps	112(%rsp), %xmm11
	movaps	128(%rsp), %xmm12
	movaps	144(%rsp), %xmm13
	movaps	160(%rsp), %xmm14
	.seh_startepilogue
	addq	$184, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r14
	popq	%r15
	.seh_endepilogue
	retq
.Lfunc_end25:
	.seh_endproc

	.def	d014_baseline_u16;
	.scl	2;
	.type	32;
	.endef
	.globl	__real@477fff00
	.section	.rdata,"dr",discard,__real@477fff00
	.p2align	2, 0x0
__real@477fff00:
	.long	0x477fff00
	.section	.text,"xr",one_only,d014_baseline_u16,unique,27
	.globl	d014_baseline_u16
	.p2align	4
d014_baseline_u16:
.Lfunc_begin26:
.seh_proc d014_baseline_u16
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
	subq	$184, %rsp
	.seh_stackalloc 184
	movaps	%xmm14, 160(%rsp)
	.seh_savexmm %xmm14, 160
	movaps	%xmm13, 144(%rsp)
	.seh_savexmm %xmm13, 144
	movaps	%xmm12, 128(%rsp)
	.seh_savexmm %xmm12, 128
	movaps	%xmm11, 112(%rsp)
	.seh_savexmm %xmm11, 112
	movaps	%xmm10, 96(%rsp)
	.seh_savexmm %xmm10, 96
	movaps	%xmm9, 80(%rsp)
	.seh_savexmm %xmm9, 80
	movaps	%xmm8, 64(%rsp)
	.seh_savexmm %xmm8, 64
	movaps	%xmm7, 48(%rsp)
	.seh_savexmm %xmm7, 48
	movaps	%xmm6, 32(%rsp)
	.seh_savexmm %xmm6, 32
	.seh_endprologue
	movq	%r9, %rsi
	movq	%r8, %rdi
	movq	%rcx, %rbx
	testq	%rdx, %rdx
	je	.LBB26_1
	leaq	(,%rdx,4), %rcx
	addq	$-4, %rcx
	xorps	%xmm0, %xmm0
	movq	%rbx, %rax
	cmpq	$28, %rcx
	jb	.LBB26_6
	shrq	$2, %rcx
	incq	%rcx
	movq	%rcx, %r8
	andq	$-8, %r8
	leaq	(%rbx,%r8,4), %rax
	xorps	%xmm0, %xmm0
	xorl	%r9d, %r9d
	xorps	%xmm1, %xmm1
	.p2align	4
.LBB26_4:
	movups	(%rbx,%r9,4), %xmm2
	movups	16(%rbx,%r9,4), %xmm3
	movaps	%xmm0, %xmm4
	maxps	%xmm2, %xmm0
	movaps	%xmm0, %xmm2
	cmpunordps	%xmm0, %xmm2
	andps	%xmm2, %xmm4
	andnps	%xmm0, %xmm2
	movaps	%xmm2, %xmm0
	orps	%xmm4, %xmm0
	movaps	%xmm1, %xmm2
	maxps	%xmm3, %xmm1
	movaps	%xmm1, %xmm3
	cmpunordps	%xmm1, %xmm3
	andps	%xmm3, %xmm2
	andnps	%xmm1, %xmm3
	movaps	%xmm3, %xmm1
	orps	%xmm2, %xmm1
	addq	$8, %r9
	cmpq	%r9, %r8
	jne	.LBB26_4
	movaps	%xmm0, %xmm2
	maxps	%xmm1, %xmm2
	movaps	%xmm2, %xmm1
	cmpunordps	%xmm2, %xmm1
	andps	%xmm1, %xmm0
	andnps	%xmm2, %xmm1
	orps	%xmm0, %xmm1
	pshufd	$255, %xmm1, %xmm2
	pshufd	$238, %xmm1, %xmm3
	pshufd	$245, %xmm1, %xmm4
	movaps	%xmm1, %xmm0
	cmpunordss	%xmm1, %xmm0
	movaps	%xmm0, %xmm5
	andps	%xmm4, %xmm5
	maxss	%xmm1, %xmm4
	andnps	%xmm4, %xmm0
	orps	%xmm5, %xmm0
	movdqa	%xmm3, %xmm1
	maxss	%xmm0, %xmm1
	cmpunordss	%xmm0, %xmm0
	movaps	%xmm0, %xmm4
	andnps	%xmm1, %xmm4
	andps	%xmm3, %xmm0
	orps	%xmm4, %xmm0
	movdqa	%xmm2, %xmm1
	maxss	%xmm0, %xmm1
	cmpunordss	%xmm0, %xmm0
	movaps	%xmm0, %xmm3
	andnps	%xmm1, %xmm3
	andps	%xmm2, %xmm0
	orps	%xmm3, %xmm0
	cmpq	%r8, %rcx
	je	.LBB26_8
.LBB26_6:
	leaq	(%rbx,%rdx,4), %rcx
	movaps	%xmm0, %xmm1
	.p2align	4
.LBB26_7:
	movaps	%xmm1, %xmm2
	maxss	(%rax), %xmm2
	addq	$4, %rax
	movaps	%xmm2, %xmm0
	cmpunordss	%xmm2, %xmm0
	movaps	%xmm0, %xmm3
	andnps	%xmm2, %xmm3
	andps	%xmm1, %xmm0
	orps	%xmm3, %xmm0
	movaps	%xmm0, %xmm1
	cmpq	%rcx, %rax
	jne	.LBB26_7
	jmp	.LBB26_8
.LBB26_1:
	xorps	%xmm0, %xmm0
.LBB26_8:
	movd	%xmm0, %eax
	testl	%eax, %eax
	setns	%cl
	movl	%eax, %r8d
	andl	$2147483647, %r8d
	addl	$-8388608, %r8d
	cmpl	$2130706432, %r8d
	setb	%r8b
	andb	%cl, %r8b
	decl	%eax
	cmpl	$8388607, %eax
	setb	%al
	orb	%r8b, %al
	je	.LBB26_9
	cmpq	%rsi, %rdx
	cmovbq	%rdx, %rsi
	testq	%rsi, %rsi
	je	.LBB26_19
	movss	__real@477fff00(%rip), %xmm11
	movaps	%xmm11, %xmm12
	movaps	%xmm0, %xmm10
	divss	%xmm0, %xmm12
	cmpq	$4, %rsi
	jae	.LBB26_13
	xorl	%r14d, %r14d
	jmp	.LBB26_16
.LBB26_9:
	addq	%rsi, %rsi
	movq	%rdi, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	memset
	xorps	%xmm0, %xmm0
	jmp	.LBB26_19
.LBB26_13:
	movabsq	$2305843009213693948, %r14
	andq	%rsi, %r14
	movaps	%xmm12, %xmm13
	shufps	$0, %xmm12, %xmm13
	leaq	(%rsi,%rsi), %r15
	andq	$-8, %r15
	xorl	%r12d, %r12d
	xorps	%xmm14, %xmm14
	.p2align	4
.LBB26_14:
	movups	(%rbx,%r12,2), %xmm7
	maxps	%xmm14, %xmm7
	mulps	%xmm13, %xmm7
	movaps	%xmm7, %xmm0
	shufps	$255, %xmm7, %xmm0
	callq	rintf
	movaps	%xmm0, %xmm6
	movaps	%xmm7, %xmm0
	unpckhpd	%xmm7, %xmm0
	callq	rintf
	movaps	%xmm0, %xmm8
	unpcklps	%xmm6, %xmm8
	movaps	%xmm7, %xmm0
	callq	rintf
	movaps	%xmm0, %xmm9
	movshdup	%xmm7, %xmm0
	callq	rintf
	xorps	%xmm1, %xmm1
	maxss	%xmm0, %xmm1
	movaps	%xmm11, %xmm0
	minss	%xmm1, %xmm0
	cvttss2si	%xmm0, %eax
	xorps	%xmm0, %xmm0
	maxss	%xmm9, %xmm0
	movaps	%xmm11, %xmm1
	minss	%xmm0, %xmm1
	cvttss2si	%xmm1, %ecx
	movd	%ecx, %xmm0
	pinsrw	$1, %eax, %xmm0
	xorps	%xmm1, %xmm1
	maxss	%xmm8, %xmm1
	movaps	%xmm11, %xmm2
	minss	%xmm1, %xmm2
	cvttss2si	%xmm2, %eax
	pinsrw	$2, %eax, %xmm0
	xorps	%xmm1, %xmm1
	maxss	%xmm6, %xmm1
	movaps	%xmm11, %xmm2
	minss	%xmm1, %xmm2
	cvttss2si	%xmm2, %eax
	pinsrw	$3, %eax, %xmm0
	movq	%xmm0, (%rdi,%r12)
	addq	$8, %r12
	cmpq	%r12, %r15
	jne	.LBB26_14
	cmpq	%r14, %rsi
	je	.LBB26_18
.LBB26_16:
	xorps	%xmm6, %xmm6
	.p2align	4
.LBB26_17:
	leaq	1(%r14), %r15
	movss	(%rbx,%r14,4), %xmm0
	maxss	%xmm6, %xmm0
	mulss	%xmm12, %xmm0
	callq	rintf
	xorps	%xmm1, %xmm1
	maxss	%xmm0, %xmm1
	movaps	%xmm11, %xmm0
	minss	%xmm1, %xmm0
	cvttss2si	%xmm0, %eax
	movw	%ax, (%rdi,%r14,2)
	movq	%r15, %r14
	cmpq	%r15, %rsi
	jne	.LBB26_17
.LBB26_18:
	movaps	%xmm10, %xmm0
.LBB26_19:
	movaps	32(%rsp), %xmm6
	movaps	48(%rsp), %xmm7
	movaps	64(%rsp), %xmm8
	movaps	80(%rsp), %xmm9
	movaps	96(%rsp), %xmm10
	movaps	112(%rsp), %xmm11
	movaps	128(%rsp), %xmm12
	movaps	144(%rsp), %xmm13
	movaps	160(%rsp), %xmm14
	.seh_startepilogue
	addq	$184, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r14
	popq	%r15
	.seh_endepilogue
	retq
.Lfunc_end26:
	.seh_endproc

	.def	d014_candidate_i16;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,d014_candidate_i16,unique,28
	.globl	d014_candidate_i16
	.p2align	4
d014_candidate_i16:
.Lfunc_begin27:
.seh_proc d014_candidate_i16
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
	subq	$264, %rsp
	.seh_stackalloc 264
	movaps	%xmm15, 240(%rsp)
	.seh_savexmm %xmm15, 240
	movaps	%xmm14, 224(%rsp)
	.seh_savexmm %xmm14, 224
	movaps	%xmm13, 208(%rsp)
	.seh_savexmm %xmm13, 208
	movaps	%xmm12, 192(%rsp)
	.seh_savexmm %xmm12, 192
	movaps	%xmm11, 176(%rsp)
	.seh_savexmm %xmm11, 176
	movaps	%xmm10, 160(%rsp)
	.seh_savexmm %xmm10, 160
	movaps	%xmm9, 144(%rsp)
	.seh_savexmm %xmm9, 144
	movaps	%xmm8, 128(%rsp)
	.seh_savexmm %xmm8, 128
	movaps	%xmm7, 112(%rsp)
	.seh_savexmm %xmm7, 112
	movaps	%xmm6, 96(%rsp)
	.seh_savexmm %xmm6, 96
	.seh_endprologue
	movq	%r9, %rsi
	movq	%r8, %rdi
	movq	%rcx, %rbx
	movabsq	$2305843009213693948, %r14
	movq	%rdx, %rax
	andq	%r14, %rax
	je	.LBB27_1
	leaq	-4(%rdx), %r9
	xorps	%xmm0, %xmm0
	movq	%rbx, %rcx
	movq	%rax, %r8
	cmpq	$28, %r9
	jb	.LBB27_6
	shrq	$2, %r9
	incq	%r9
	movq	%r9, %r10
	andq	$-8, %r10
	movq	%r10, %rcx
	shlq	$4, %rcx
	addq	%rbx, %rcx
	leaq	(,%r10,4), %r11
	movq	%rax, %r8
	subq	%r11, %r8
	leaq	64(%rbx), %r11
	xorps	%xmm6, %xmm6
	movq	%r10, %r15
	xorps	%xmm8, %xmm8
	xorps	%xmm4, %xmm4
	xorps	%xmm5, %xmm5
	xorps	%xmm13, %xmm13
	movaps	%xmm0, 32(%rsp)
	movaps	%xmm0, 64(%rsp)
	movaps	%xmm0, 48(%rsp)
	.p2align	4
.LBB27_4:
	movaps	%xmm4, 80(%rsp)
	movups	-64(%r11), %xmm0
	movups	-48(%r11), %xmm9
	movups	-32(%r11), %xmm14
	movups	-16(%r11), %xmm15
	movups	32(%r11), %xmm11
	movups	(%r11), %xmm2
	movaps	__xmm@7fffffff7fffffff7fffffff7fffffff(%rip), %xmm3
	andps	%xmm3, %xmm9
	andps	%xmm3, %xmm0
	andps	%xmm3, %xmm14
	andps	%xmm3, %xmm15
	movaps	%xmm15, %xmm7
	movlhps	%xmm14, %xmm7
	movaps	%xmm0, %xmm12
	unpcklps	%xmm9, %xmm12
	shufps	$36, %xmm7, %xmm12
	movups	16(%r11), %xmm10
	andps	%xmm3, %xmm10
	andps	%xmm3, %xmm2
	andps	%xmm3, %xmm11
	movups	48(%r11), %xmm1
	andps	%xmm3, %xmm1
	movaps	%xmm1, %xmm7
	movlhps	%xmm11, %xmm7
	movaps	%xmm13, %xmm4
	movaps	%xmm2, %xmm13
	unpcklps	%xmm10, %xmm13
	shufps	$36, %xmm7, %xmm13
	movaps	64(%rsp), %xmm7
	movaps	%xmm7, %xmm3
	maxps	%xmm12, %xmm3
	movaps	%xmm7, %xmm12
	movaps	%xmm3, %xmm7
	cmpunordps	%xmm3, %xmm7
	andps	%xmm7, %xmm12
	andnps	%xmm3, %xmm7
	orps	%xmm12, %xmm7
	movaps	%xmm7, 64(%rsp)
	movaps	48(%rsp), %xmm7
	movaps	%xmm7, %xmm3
	maxps	%xmm13, %xmm3
	movaps	%xmm3, %xmm12
	cmpunordps	%xmm3, %xmm12
	andps	%xmm12, %xmm7
	andnps	%xmm3, %xmm12
	orps	%xmm7, %xmm12
	movaps	%xmm12, 48(%rsp)
	movaps	%xmm14, %xmm3
	unpcklps	%xmm15, %xmm3
	movaps	%xmm9, %xmm7
	shufps	$17, %xmm0, %xmm7
	shufps	$226, %xmm3, %xmm7
	movaps	%xmm11, %xmm3
	unpcklps	%xmm1, %xmm3
	movaps	%xmm10, %xmm12
	shufps	$17, %xmm2, %xmm12
	shufps	$226, %xmm3, %xmm12
	movaps	%xmm4, %xmm3
	maxps	%xmm7, %xmm3
	movaps	%xmm3, %xmm13
	cmpunordps	%xmm3, %xmm13
	andps	%xmm13, %xmm4
	andnps	%xmm3, %xmm13
	orps	%xmm4, %xmm13
	movaps	32(%rsp), %xmm7
	movaps	%xmm7, %xmm3
	maxps	%xmm12, %xmm3
	movaps	%xmm3, %xmm12
	cmpunordps	%xmm3, %xmm12
	andps	%xmm12, %xmm7
	andnps	%xmm3, %xmm12
	orps	%xmm7, %xmm12
	movaps	%xmm12, 32(%rsp)
	movaps	%xmm15, %xmm3
	unpckhpd	%xmm14, %xmm3
	movaps	%xmm0, %xmm7
	unpckhps	%xmm9, %xmm7
	shufps	$36, %xmm3, %xmm7
	movaps	%xmm1, %xmm3
	unpckhpd	%xmm11, %xmm3
	movaps	%xmm2, %xmm12
	unpckhps	%xmm10, %xmm12
	shufps	$36, %xmm3, %xmm12
	movaps	80(%rsp), %xmm4
	movaps	%xmm4, %xmm3
	maxps	%xmm7, %xmm3
	movaps	%xmm4, %xmm7
	movaps	%xmm3, %xmm4
	cmpunordps	%xmm3, %xmm4
	andps	%xmm4, %xmm7
	andnps	%xmm3, %xmm4
	orps	%xmm7, %xmm4
	movaps	%xmm5, %xmm3
	maxps	%xmm12, %xmm3
	movaps	%xmm5, %xmm7
	movaps	%xmm3, %xmm5
	cmpunordps	%xmm3, %xmm5
	andps	%xmm5, %xmm7
	andnps	%xmm3, %xmm5
	orps	%xmm7, %xmm5
	unpckhps	%xmm15, %xmm14
	shufps	$51, %xmm0, %xmm9
	shufps	$226, %xmm14, %xmm9
	unpckhps	%xmm1, %xmm11
	shufps	$51, %xmm2, %xmm10
	shufps	$226, %xmm11, %xmm10
	movaps	%xmm6, %xmm0
	maxps	%xmm9, %xmm6
	movaps	%xmm6, %xmm1
	cmpunordps	%xmm6, %xmm1
	andps	%xmm1, %xmm0
	andnps	%xmm6, %xmm1
	movaps	%xmm1, %xmm6
	orps	%xmm0, %xmm6
	movaps	%xmm8, %xmm0
	maxps	%xmm10, %xmm8
	movaps	%xmm8, %xmm1
	cmpunordps	%xmm8, %xmm1
	andps	%xmm1, %xmm0
	andnps	%xmm8, %xmm1
	movaps	%xmm1, %xmm8
	orps	%xmm0, %xmm8
	subq	$-128, %r11
	addq	$-8, %r15
	jne	.LBB27_4
	movaps	%xmm6, %xmm0
	maxps	%xmm8, %xmm0
	movaps	%xmm0, %xmm1
	cmpunordps	%xmm0, %xmm1
	andps	%xmm1, %xmm6
	andnps	%xmm0, %xmm1
	orps	%xmm6, %xmm1
	pshufd	$255, %xmm1, %xmm0
	pshufd	$238, %xmm1, %xmm2
	pshufd	$245, %xmm1, %xmm3
	movaps	%xmm1, %xmm6
	cmpunordss	%xmm1, %xmm6
	movaps	%xmm6, %xmm7
	andps	%xmm3, %xmm7
	maxss	%xmm1, %xmm3
	andnps	%xmm3, %xmm6
	orps	%xmm7, %xmm6
	movdqa	%xmm2, %xmm1
	maxss	%xmm6, %xmm1
	cmpunordss	%xmm6, %xmm6
	movaps	%xmm6, %xmm3
	andnps	%xmm1, %xmm3
	andps	%xmm2, %xmm6
	orps	%xmm3, %xmm6
	movdqa	%xmm0, %xmm1
	maxss	%xmm6, %xmm1
	cmpunordss	%xmm6, %xmm6
	movaps	%xmm6, %xmm2
	andnps	%xmm1, %xmm2
	andps	%xmm0, %xmm6
	orps	%xmm2, %xmm6
	movaps	%xmm4, %xmm0
	maxps	%xmm5, %xmm0
	movaps	%xmm0, %xmm1
	cmpunordps	%xmm0, %xmm1
	andps	%xmm1, %xmm4
	andnps	%xmm0, %xmm1
	orps	%xmm4, %xmm1
	pshufd	$255, %xmm1, %xmm0
	pshufd	$238, %xmm1, %xmm2
	pshufd	$245, %xmm1, %xmm3
	movaps	%xmm1, %xmm4
	cmpunordss	%xmm1, %xmm4
	movaps	%xmm4, %xmm5
	andps	%xmm3, %xmm5
	maxss	%xmm1, %xmm3
	andnps	%xmm3, %xmm4
	orps	%xmm5, %xmm4
	movdqa	%xmm2, %xmm1
	maxss	%xmm4, %xmm1
	cmpunordss	%xmm4, %xmm4
	movaps	%xmm4, %xmm3
	andnps	%xmm1, %xmm3
	andps	%xmm2, %xmm4
	orps	%xmm3, %xmm4
	movdqa	%xmm0, %xmm1
	maxss	%xmm4, %xmm1
	cmpunordss	%xmm4, %xmm4
	movaps	%xmm4, %xmm2
	andnps	%xmm1, %xmm2
	andps	%xmm0, %xmm4
	orps	%xmm2, %xmm4
	unpcklps	%xmm6, %xmm4
	movaps	%xmm13, %xmm0
	maxps	32(%rsp), %xmm0
	movaps	%xmm0, %xmm1
	cmpunordps	%xmm0, %xmm1
	andps	%xmm1, %xmm13
	andnps	%xmm0, %xmm1
	orps	%xmm13, %xmm1
	pshufd	$255, %xmm1, %xmm0
	pshufd	$238, %xmm1, %xmm3
	pshufd	$245, %xmm1, %xmm5
	movaps	%xmm1, %xmm2
	cmpunordss	%xmm1, %xmm2
	movaps	%xmm2, %xmm6
	andps	%xmm5, %xmm6
	maxss	%xmm1, %xmm5
	andnps	%xmm5, %xmm2
	orps	%xmm6, %xmm2
	movdqa	%xmm3, %xmm1
	maxss	%xmm2, %xmm1
	cmpunordss	%xmm2, %xmm2
	movaps	%xmm2, %xmm5
	andnps	%xmm1, %xmm5
	andps	%xmm3, %xmm2
	orps	%xmm5, %xmm2
	movdqa	%xmm0, %xmm1
	maxss	%xmm2, %xmm1
	cmpunordss	%xmm2, %xmm2
	movaps	%xmm2, %xmm3
	andnps	%xmm1, %xmm3
	andps	%xmm0, %xmm2
	orps	%xmm3, %xmm2
	movaps	64(%rsp), %xmm3
	movaps	%xmm3, %xmm0
	maxps	48(%rsp), %xmm0
	movaps	%xmm0, %xmm1
	cmpunordps	%xmm0, %xmm1
	andps	%xmm1, %xmm3
	andnps	%xmm0, %xmm1
	orps	%xmm3, %xmm1
	pshufd	$255, %xmm1, %xmm3
	pshufd	$238, %xmm1, %xmm5
	pshufd	$245, %xmm1, %xmm6
	movaps	%xmm1, %xmm0
	cmpunordss	%xmm1, %xmm0
	movaps	%xmm0, %xmm7
	andps	%xmm6, %xmm7
	maxss	%xmm1, %xmm6
	andnps	%xmm6, %xmm0
	orps	%xmm7, %xmm0
	movdqa	%xmm5, %xmm1
	maxss	%xmm0, %xmm1
	cmpunordss	%xmm0, %xmm0
	movaps	%xmm0, %xmm6
	andnps	%xmm1, %xmm6
	andps	%xmm5, %xmm0
	orps	%xmm6, %xmm0
	movdqa	%xmm3, %xmm1
	maxss	%xmm0, %xmm1
	cmpunordss	%xmm0, %xmm0
	movaps	%xmm0, %xmm5
	andnps	%xmm1, %xmm5
	andps	%xmm3, %xmm0
	orps	%xmm5, %xmm0
	unpcklps	%xmm2, %xmm0
	movlhps	%xmm4, %xmm0
	cmpq	%r10, %r9
	je	.LBB27_8
.LBB27_6:
	xorl	%r9d, %r9d
	movaps	__xmm@7fffffff7fffffff7fffffff7fffffff(%rip), %xmm1
	movaps	%xmm0, %xmm2
	.p2align	4
.LBB27_7:
	movups	(%rcx,%r9,4), %xmm0
	andps	%xmm1, %xmm0
	movaps	%xmm2, %xmm3
	maxps	%xmm0, %xmm3
	movaps	%xmm3, %xmm0
	cmpunordps	%xmm3, %xmm0
	andps	%xmm0, %xmm2
	andnps	%xmm3, %xmm0
	orps	%xmm2, %xmm0
	addq	$4, %r9
	movaps	%xmm0, %xmm2
	cmpq	%r9, %r8
	jne	.LBB27_7
.LBB27_8:
	movshdup	%xmm0, %xmm1
	movaps	%xmm0, %xmm2
	maxss	%xmm1, %xmm2
	movaps	%xmm2, %xmm1
	cmpunordss	%xmm2, %xmm1
	movaps	%xmm1, %xmm3
	andnps	%xmm2, %xmm3
	andps	%xmm0, %xmm1
	orps	%xmm3, %xmm1
	movaps	%xmm0, %xmm2
	unpckhpd	%xmm0, %xmm2
	movaps	%xmm1, %xmm3
	maxss	%xmm2, %xmm3
	movaps	%xmm3, %xmm2
	cmpunordss	%xmm3, %xmm2
	andps	%xmm2, %xmm1
	andnps	%xmm3, %xmm2
	orps	%xmm1, %xmm2
	shufps	$255, %xmm0, %xmm0
	movaps	%xmm2, %xmm1
	maxss	%xmm0, %xmm1
	movaps	%xmm1, %xmm0
	cmpunordss	%xmm1, %xmm0
	andps	%xmm0, %xmm2
	andnps	%xmm1, %xmm0
	orps	%xmm2, %xmm0
	leal	(,%rdx,4), %r8d
	andl	$12, %r8d
	jne	.LBB27_10
	jmp	.LBB27_17
.LBB27_1:
	xorps	%xmm0, %xmm0
	leal	(,%rdx,4), %r8d
	andl	$12, %r8d
	je	.LBB27_17
.LBB27_10:
	leaq	(%rbx,%rax,4), %rax
	leaq	-4(%r8), %r9
	cmpq	$28, %r9
	jae	.LBB27_12
	movq	%rax, %rcx
	jmp	.LBB27_15
.LBB27_12:
	shrq	$2, %r9
	incq	%r9
	movq	%r9, %r10
	andq	$-8, %r10
	leaq	(%rax,%r10,4), %rcx
	shufps	$0, %xmm0, %xmm0
	movq	%rdx, %r11
	andq	$-4, %r11
	leaq	(%rbx,%r11,4), %r11
	addq	$16, %r11
	xorl	%r15d, %r15d
	movaps	__xmm@7fffffff7fffffff7fffffff7fffffff(%rip), %xmm1
	movaps	%xmm0, %xmm2
	.p2align	4
.LBB27_13:
	movups	-16(%r11,%r15,4), %xmm3
	movups	(%r11,%r15,4), %xmm4
	andps	%xmm1, %xmm3
	andps	%xmm1, %xmm4
	movaps	%xmm0, %xmm5
	maxps	%xmm3, %xmm0
	movaps	%xmm0, %xmm3
	cmpunordps	%xmm0, %xmm3
	andps	%xmm3, %xmm5
	andnps	%xmm0, %xmm3
	movaps	%xmm3, %xmm0
	orps	%xmm5, %xmm0
	movaps	%xmm2, %xmm3
	maxps	%xmm4, %xmm2
	movaps	%xmm2, %xmm4
	cmpunordps	%xmm2, %xmm4
	andps	%xmm4, %xmm3
	andnps	%xmm2, %xmm4
	movaps	%xmm4, %xmm2
	orps	%xmm3, %xmm2
	addq	$8, %r15
	cmpq	%r15, %r10
	jne	.LBB27_13
	movaps	%xmm0, %xmm1
	maxps	%xmm2, %xmm1
	movaps	%xmm1, %xmm2
	cmpunordps	%xmm1, %xmm2
	andps	%xmm2, %xmm0
	andnps	%xmm1, %xmm2
	orps	%xmm0, %xmm2
	pshufd	$255, %xmm2, %xmm1
	pshufd	$238, %xmm2, %xmm3
	pshufd	$245, %xmm2, %xmm4
	movaps	%xmm2, %xmm0
	cmpunordss	%xmm2, %xmm0
	movaps	%xmm0, %xmm5
	andps	%xmm4, %xmm5
	maxss	%xmm2, %xmm4
	andnps	%xmm4, %xmm0
	orps	%xmm5, %xmm0
	movdqa	%xmm3, %xmm2
	maxss	%xmm0, %xmm2
	cmpunordss	%xmm0, %xmm0
	movaps	%xmm0, %xmm4
	andnps	%xmm2, %xmm4
	andps	%xmm3, %xmm0
	orps	%xmm4, %xmm0
	movdqa	%xmm1, %xmm2
	maxss	%xmm0, %xmm2
	cmpunordss	%xmm0, %xmm0
	movaps	%xmm0, %xmm3
	andnps	%xmm2, %xmm3
	andps	%xmm1, %xmm0
	orps	%xmm3, %xmm0
	cmpq	%r10, %r9
	je	.LBB27_17
.LBB27_15:
	addq	%r8, %rax
	movaps	__xmm@7fffffff7fffffff7fffffff7fffffff(%rip), %xmm1
	movaps	%xmm0, %xmm2
	.p2align	4
.LBB27_16:
	movss	(%rcx), %xmm0
	addq	$4, %rcx
	andps	%xmm1, %xmm0
	movaps	%xmm2, %xmm3
	maxss	%xmm0, %xmm3
	movaps	%xmm3, %xmm0
	cmpunordss	%xmm3, %xmm0
	movaps	%xmm0, %xmm4
	andnps	%xmm3, %xmm4
	andps	%xmm2, %xmm0
	orps	%xmm4, %xmm0
	movaps	%xmm0, %xmm2
	cmpq	%rax, %rcx
	jne	.LBB27_16
.LBB27_17:
	movd	%xmm0, %eax
	testl	%eax, %eax
	setns	%cl
	movl	%eax, %r8d
	andl	$2147483647, %r8d
	addl	$-8388608, %r8d
	cmpl	$2130706432, %r8d
	setb	%r8b
	andb	%cl, %r8b
	decl	%eax
	cmpl	$8388607, %eax
	setb	%al
	orb	%r8b, %al
	je	.LBB27_18
	cmpq	%rsi, %rdx
	cmovbq	%rdx, %rsi
	testq	%rsi, %rsi
	je	.LBB27_28
	movss	__real@46fffe00(%rip), %xmm11
	movaps	%xmm11, %xmm12
	movaps	%xmm0, %xmm10
	divss	%xmm0, %xmm12
	cmpq	$4, %rsi
	jae	.LBB27_24
	xorl	%r14d, %r14d
	jmp	.LBB27_22
.LBB27_18:
	addq	%rsi, %rsi
	movq	%rdi, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	memset
	xorps	%xmm0, %xmm0
	jmp	.LBB27_28
.LBB27_24:
	andq	%rsi, %r14
	movaps	%xmm12, %xmm13
	shufps	$0, %xmm12, %xmm13
	leaq	(%rsi,%rsi), %r15
	andq	$-8, %r15
	xorl	%r12d, %r12d
	movss	__real@c7000000(%rip), %xmm14
	.p2align	4
.LBB27_25:
	movups	(%rbx,%r12,2), %xmm7
	mulps	%xmm13, %xmm7
	movaps	%xmm7, %xmm0
	shufps	$255, %xmm7, %xmm0
	callq	rintf
	movaps	%xmm0, %xmm6
	movaps	%xmm7, %xmm0
	unpckhpd	%xmm7, %xmm0
	callq	rintf
	movaps	%xmm0, %xmm8
	unpcklps	%xmm6, %xmm8
	movaps	%xmm7, %xmm0
	callq	rintf
	movaps	%xmm0, %xmm9
	movshdup	%xmm7, %xmm0
	callq	rintf
	movaps	%xmm14, %xmm1
	maxss	%xmm0, %xmm1
	movaps	%xmm11, %xmm0
	minss	%xmm1, %xmm0
	cvttss2si	%xmm0, %eax
	movaps	%xmm14, %xmm0
	maxss	%xmm9, %xmm0
	movaps	%xmm11, %xmm1
	minss	%xmm0, %xmm1
	cvttss2si	%xmm1, %ecx
	movd	%ecx, %xmm0
	pinsrw	$1, %eax, %xmm0
	movaps	%xmm14, %xmm1
	maxss	%xmm8, %xmm1
	movaps	%xmm11, %xmm2
	minss	%xmm1, %xmm2
	cvttss2si	%xmm2, %eax
	pinsrw	$2, %eax, %xmm0
	movaps	%xmm14, %xmm1
	maxss	%xmm6, %xmm1
	movaps	%xmm11, %xmm2
	minss	%xmm1, %xmm2
	cvttss2si	%xmm2, %eax
	pinsrw	$3, %eax, %xmm0
	movq	%xmm0, (%rdi,%r12)
	addq	$8, %r12
	cmpq	%r12, %r15
	jne	.LBB27_25
	cmpq	%r14, %rsi
	je	.LBB27_27
.LBB27_22:
	movss	__real@c7000000(%rip), %xmm6
	.p2align	4
.LBB27_23:
	leaq	1(%r14), %r15
	movss	(%rbx,%r14,4), %xmm0
	mulss	%xmm12, %xmm0
	callq	rintf
	movaps	%xmm6, %xmm1
	maxss	%xmm0, %xmm1
	movaps	%xmm11, %xmm0
	minss	%xmm1, %xmm0
	cvttss2si	%xmm0, %eax
	movw	%ax, (%rdi,%r14,2)
	movq	%r15, %r14
	cmpq	%r15, %rsi
	jne	.LBB27_23
.LBB27_27:
	movaps	%xmm10, %xmm0
.LBB27_28:
	movaps	96(%rsp), %xmm6
	movaps	112(%rsp), %xmm7
	movaps	128(%rsp), %xmm8
	movaps	144(%rsp), %xmm9
	movaps	160(%rsp), %xmm10
	movaps	176(%rsp), %xmm11
	movaps	192(%rsp), %xmm12
	movaps	208(%rsp), %xmm13
	movaps	224(%rsp), %xmm14
	movaps	240(%rsp), %xmm15
	.seh_startepilogue
	addq	$264, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r14
	popq	%r15
	.seh_endepilogue
	retq
.Lfunc_end27:
	.seh_endproc

	.def	d014_candidate_u16;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,d014_candidate_u16,unique,29
	.globl	d014_candidate_u16
	.p2align	4
d014_candidate_u16:
.Lfunc_begin28:
.seh_proc d014_candidate_u16
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
	subq	$264, %rsp
	.seh_stackalloc 264
	movaps	%xmm15, 240(%rsp)
	.seh_savexmm %xmm15, 240
	movaps	%xmm14, 224(%rsp)
	.seh_savexmm %xmm14, 224
	movaps	%xmm13, 208(%rsp)
	.seh_savexmm %xmm13, 208
	movaps	%xmm12, 192(%rsp)
	.seh_savexmm %xmm12, 192
	movaps	%xmm11, 176(%rsp)
	.seh_savexmm %xmm11, 176
	movaps	%xmm10, 160(%rsp)
	.seh_savexmm %xmm10, 160
	movaps	%xmm9, 144(%rsp)
	.seh_savexmm %xmm9, 144
	movaps	%xmm8, 128(%rsp)
	.seh_savexmm %xmm8, 128
	movaps	%xmm7, 112(%rsp)
	.seh_savexmm %xmm7, 112
	movaps	%xmm6, 96(%rsp)
	.seh_savexmm %xmm6, 96
	.seh_endprologue
	movq	%r9, %rsi
	movq	%r8, %rdi
	movq	%rcx, %rbx
	movabsq	$2305843009213693948, %r14
	movq	%rdx, %rax
	andq	%r14, %rax
	je	.LBB28_1
	leaq	-4(%rdx), %r9
	xorps	%xmm0, %xmm0
	movq	%rbx, %rcx
	movq	%rax, %r8
	cmpq	$28, %r9
	jb	.LBB28_7
	shrq	$2, %r9
	incq	%r9
	movq	%r9, %r10
	andq	$-8, %r10
	movq	%r10, %rcx
	shlq	$4, %rcx
	addq	%rbx, %rcx
	leaq	(,%r10,4), %r11
	movq	%rax, %r8
	subq	%r11, %r8
	leaq	64(%rbx), %r11
	xorps	%xmm6, %xmm6
	movq	%r10, %r15
	xorps	%xmm7, %xmm7
	xorps	%xmm4, %xmm4
	xorps	%xmm5, %xmm5
	xorps	%xmm12, %xmm12
	xorps	%xmm13, %xmm13
	xorps	%xmm14, %xmm14
	xorps	%xmm15, %xmm15
	.p2align	4
.LBB28_4:
	movaps	%xmm14, 32(%rsp)
	movaps	%xmm15, 48(%rsp)
	movaps	%xmm12, 64(%rsp)
	movaps	%xmm13, 80(%rsp)
	movups	-64(%r11), %xmm9
	movups	-48(%r11), %xmm8
	movups	-32(%r11), %xmm11
	movups	-16(%r11), %xmm13
	movaps	%xmm13, %xmm10
	movlhps	%xmm11, %xmm10
	movaps	%xmm9, %xmm14
	unpcklps	%xmm8, %xmm14
	shufps	$36, %xmm10, %xmm14
	movaps	%xmm11, %xmm10
	unpcklps	%xmm13, %xmm10
	movaps	%xmm8, %xmm12
	shufps	$17, %xmm9, %xmm12
	shufps	$226, %xmm10, %xmm12
	movaps	%xmm13, %xmm15
	unpckhpd	%xmm11, %xmm15
	movaps	%xmm9, %xmm10
	unpckhps	%xmm8, %xmm10
	shufps	$36, %xmm15, %xmm10
	unpckhps	%xmm13, %xmm11
	shufps	$51, %xmm9, %xmm8
	shufps	$226, %xmm11, %xmm8
	movups	16(%r11), %xmm9
	movups	32(%r11), %xmm0
	movups	48(%r11), %xmm3
	movaps	%xmm3, %xmm11
	movlhps	%xmm0, %xmm11
	movups	(%r11), %xmm15
	movaps	%xmm15, %xmm2
	unpcklps	%xmm9, %xmm2
	shufps	$36, %xmm11, %xmm2
	movaps	%xmm0, %xmm11
	unpcklps	%xmm3, %xmm11
	movaps	%xmm9, %xmm13
	shufps	$17, %xmm15, %xmm13
	shufps	$226, %xmm11, %xmm13
	movaps	%xmm3, %xmm1
	unpckhpd	%xmm0, %xmm1
	movaps	%xmm15, %xmm11
	unpckhps	%xmm9, %xmm11
	shufps	$36, %xmm1, %xmm11
	unpckhps	%xmm3, %xmm0
	shufps	$51, %xmm15, %xmm9
	shufps	$226, %xmm0, %xmm9
	movaps	32(%rsp), %xmm1
	movaps	%xmm1, %xmm0
	maxps	%xmm14, %xmm0
	movaps	%xmm0, %xmm3
	cmpunordps	%xmm0, %xmm3
	andps	%xmm3, %xmm1
	andnps	%xmm0, %xmm3
	movaps	%xmm3, %xmm14
	orps	%xmm1, %xmm14
	movaps	48(%rsp), %xmm1
	movaps	%xmm1, %xmm0
	maxps	%xmm2, %xmm1
	movaps	%xmm1, %xmm2
	cmpunordps	%xmm1, %xmm2
	andps	%xmm2, %xmm0
	andnps	%xmm1, %xmm2
	movaps	%xmm2, %xmm15
	orps	%xmm0, %xmm15
	movaps	64(%rsp), %xmm1
	movaps	%xmm1, %xmm0
	maxps	%xmm12, %xmm1
	movaps	%xmm1, %xmm2
	cmpunordps	%xmm1, %xmm2
	andps	%xmm2, %xmm0
	andnps	%xmm1, %xmm2
	movaps	%xmm2, %xmm12
	orps	%xmm0, %xmm12
	movaps	80(%rsp), %xmm1
	movaps	%xmm1, %xmm0
	maxps	%xmm13, %xmm1
	movaps	%xmm1, %xmm2
	cmpunordps	%xmm1, %xmm2
	andps	%xmm2, %xmm0
	andnps	%xmm1, %xmm2
	movaps	%xmm2, %xmm13
	orps	%xmm0, %xmm13
	movaps	%xmm4, %xmm0
	maxps	%xmm10, %xmm4
	movaps	%xmm4, %xmm1
	cmpunordps	%xmm4, %xmm1
	andps	%xmm1, %xmm0
	andnps	%xmm4, %xmm1
	movaps	%xmm1, %xmm4
	orps	%xmm0, %xmm4
	movaps	%xmm5, %xmm0
	maxps	%xmm11, %xmm5
	movaps	%xmm5, %xmm1
	cmpunordps	%xmm5, %xmm1
	andps	%xmm1, %xmm0
	andnps	%xmm5, %xmm1
	movaps	%xmm1, %xmm5
	orps	%xmm0, %xmm5
	movaps	%xmm6, %xmm0
	maxps	%xmm8, %xmm6
	movaps	%xmm6, %xmm1
	cmpunordps	%xmm6, %xmm1
	andps	%xmm1, %xmm0
	andnps	%xmm6, %xmm1
	movaps	%xmm1, %xmm6
	orps	%xmm0, %xmm6
	movaps	%xmm7, %xmm0
	maxps	%xmm9, %xmm7
	movaps	%xmm7, %xmm1
	cmpunordps	%xmm7, %xmm1
	andps	%xmm1, %xmm0
	andnps	%xmm7, %xmm1
	movaps	%xmm1, %xmm7
	orps	%xmm0, %xmm7
	subq	$-128, %r11
	addq	$-8, %r15
	jne	.LBB28_4
	movaps	%xmm6, %xmm0
	maxps	%xmm7, %xmm0
	movaps	%xmm0, %xmm1
	cmpunordps	%xmm0, %xmm1
	andps	%xmm1, %xmm6
	andnps	%xmm0, %xmm1
	orps	%xmm6, %xmm1
	pshufd	$255, %xmm1, %xmm0
	pshufd	$238, %xmm1, %xmm2
	pshufd	$245, %xmm1, %xmm3
	movaps	%xmm1, %xmm6
	cmpunordss	%xmm1, %xmm6
	movaps	%xmm6, %xmm7
	andps	%xmm3, %xmm7
	maxss	%xmm1, %xmm3
	andnps	%xmm3, %xmm6
	orps	%xmm7, %xmm6
	movdqa	%xmm2, %xmm1
	maxss	%xmm6, %xmm1
	cmpunordss	%xmm6, %xmm6
	movaps	%xmm6, %xmm3
	andnps	%xmm1, %xmm3
	andps	%xmm2, %xmm6
	orps	%xmm3, %xmm6
	movdqa	%xmm0, %xmm1
	maxss	%xmm6, %xmm1
	cmpunordss	%xmm6, %xmm6
	movaps	%xmm6, %xmm2
	andnps	%xmm1, %xmm2
	andps	%xmm0, %xmm6
	orps	%xmm2, %xmm6
	movaps	%xmm4, %xmm0
	maxps	%xmm5, %xmm0
	movaps	%xmm0, %xmm1
	cmpunordps	%xmm0, %xmm1
	andps	%xmm1, %xmm4
	andnps	%xmm0, %xmm1
	orps	%xmm4, %xmm1
	pshufd	$255, %xmm1, %xmm0
	pshufd	$238, %xmm1, %xmm2
	pshufd	$245, %xmm1, %xmm3
	movaps	%xmm1, %xmm4
	cmpunordss	%xmm1, %xmm4
	movaps	%xmm4, %xmm5
	andps	%xmm3, %xmm5
	maxss	%xmm1, %xmm3
	andnps	%xmm3, %xmm4
	orps	%xmm5, %xmm4
	movdqa	%xmm2, %xmm1
	maxss	%xmm4, %xmm1
	cmpunordss	%xmm4, %xmm4
	movaps	%xmm4, %xmm3
	andnps	%xmm1, %xmm3
	andps	%xmm2, %xmm4
	orps	%xmm3, %xmm4
	movdqa	%xmm0, %xmm1
	maxss	%xmm4, %xmm1
	cmpunordss	%xmm4, %xmm4
	movaps	%xmm4, %xmm2
	andnps	%xmm1, %xmm2
	andps	%xmm0, %xmm4
	orps	%xmm2, %xmm4
	movaps	%xmm12, %xmm0
	maxps	%xmm13, %xmm0
	movaps	%xmm0, %xmm1
	cmpunordps	%xmm0, %xmm1
	andps	%xmm1, %xmm12
	andnps	%xmm0, %xmm1
	orps	%xmm12, %xmm1
	pshufd	$255, %xmm1, %xmm0
	pshufd	$238, %xmm1, %xmm3
	pshufd	$245, %xmm1, %xmm5
	movaps	%xmm1, %xmm2
	cmpunordss	%xmm1, %xmm2
	movaps	%xmm2, %xmm7
	andps	%xmm5, %xmm7
	maxss	%xmm1, %xmm5
	andnps	%xmm5, %xmm2
	orps	%xmm7, %xmm2
	movdqa	%xmm3, %xmm1
	maxss	%xmm2, %xmm1
	cmpunordss	%xmm2, %xmm2
	movaps	%xmm2, %xmm5
	andnps	%xmm1, %xmm5
	andps	%xmm3, %xmm2
	orps	%xmm5, %xmm2
	movdqa	%xmm0, %xmm1
	maxss	%xmm2, %xmm1
	cmpunordss	%xmm2, %xmm2
	movaps	%xmm2, %xmm3
	andnps	%xmm1, %xmm3
	andps	%xmm0, %xmm2
	orps	%xmm3, %xmm2
	movaps	%xmm14, %xmm0
	maxps	%xmm15, %xmm0
	movaps	%xmm0, %xmm1
	cmpunordps	%xmm0, %xmm1
	andps	%xmm1, %xmm14
	andnps	%xmm0, %xmm1
	orps	%xmm14, %xmm1
	pshufd	$255, %xmm1, %xmm3
	pshufd	$238, %xmm1, %xmm5
	pshufd	$245, %xmm1, %xmm7
	movaps	%xmm1, %xmm0
	cmpunordss	%xmm1, %xmm0
	movaps	%xmm0, %xmm8
	andps	%xmm7, %xmm8
	maxss	%xmm1, %xmm7
	andnps	%xmm7, %xmm0
	orps	%xmm8, %xmm0
	movdqa	%xmm5, %xmm1
	maxss	%xmm0, %xmm1
	cmpunordss	%xmm0, %xmm0
	movaps	%xmm0, %xmm7
	andnps	%xmm1, %xmm7
	andps	%xmm5, %xmm0
	orps	%xmm7, %xmm0
	movdqa	%xmm3, %xmm1
	maxss	%xmm0, %xmm1
	cmpunordss	%xmm0, %xmm0
	movaps	%xmm0, %xmm5
	andnps	%xmm1, %xmm5
	andps	%xmm3, %xmm0
	orps	%xmm5, %xmm0
	cmpq	%r10, %r9
	je	.LBB28_10
	unpcklps	%xmm6, %xmm4
	unpcklps	%xmm2, %xmm0
	movlhps	%xmm4, %xmm0
.LBB28_7:
	xorl	%r9d, %r9d
	.p2align	4
.LBB28_8:
	movups	(%rcx,%r9,4), %xmm1
	movaps	%xmm0, %xmm2
	maxps	%xmm1, %xmm0
	movaps	%xmm0, %xmm1
	cmpunordps	%xmm0, %xmm1
	andps	%xmm1, %xmm2
	andnps	%xmm0, %xmm1
	movaps	%xmm1, %xmm0
	orps	%xmm2, %xmm0
	addq	$4, %r9
	cmpq	%r9, %r8
	jne	.LBB28_8
	movaps	%xmm0, %xmm6
	shufps	$255, %xmm0, %xmm6
	movaps	%xmm0, %xmm4
	unpckhpd	%xmm0, %xmm4
	movshdup	%xmm0, %xmm2
.LBB28_10:
	movaps	%xmm0, %xmm1
	maxss	%xmm2, %xmm1
	movaps	%xmm1, %xmm2
	cmpunordss	%xmm1, %xmm2
	movaps	%xmm2, %xmm3
	andnps	%xmm1, %xmm3
	andps	%xmm0, %xmm2
	orps	%xmm3, %xmm2
	movaps	%xmm2, %xmm0
	maxss	%xmm4, %xmm0
	movaps	%xmm0, %xmm1
	cmpunordss	%xmm0, %xmm1
	andps	%xmm1, %xmm2
	andnps	%xmm0, %xmm1
	orps	%xmm2, %xmm1
	movaps	%xmm1, %xmm2
	maxss	%xmm6, %xmm2
	movaps	%xmm2, %xmm0
	cmpunordss	%xmm2, %xmm0
	andps	%xmm0, %xmm1
	andnps	%xmm2, %xmm0
	orps	%xmm1, %xmm0
	leal	(,%rdx,4), %r8d
	andl	$12, %r8d
	jne	.LBB28_12
	jmp	.LBB28_19
.LBB28_1:
	xorps	%xmm0, %xmm0
	leal	(,%rdx,4), %r8d
	andl	$12, %r8d
	je	.LBB28_19
.LBB28_12:
	leaq	(%rbx,%rax,4), %rax
	leaq	-4(%r8), %r9
	cmpq	$28, %r9
	jae	.LBB28_14
	movq	%rax, %rcx
	jmp	.LBB28_17
.LBB28_14:
	shrq	$2, %r9
	incq	%r9
	movq	%r9, %r10
	andq	$-8, %r10
	leaq	(%rax,%r10,4), %rcx
	shufps	$0, %xmm0, %xmm0
	movq	%rdx, %r11
	andq	$-4, %r11
	leaq	(%rbx,%r11,4), %r11
	addq	$16, %r11
	xorl	%r15d, %r15d
	movaps	%xmm0, %xmm1
	.p2align	4
.LBB28_15:
	movups	-16(%r11,%r15,4), %xmm2
	movups	(%r11,%r15,4), %xmm3
	movaps	%xmm0, %xmm4
	maxps	%xmm2, %xmm0
	movaps	%xmm0, %xmm2
	cmpunordps	%xmm0, %xmm2
	andps	%xmm2, %xmm4
	andnps	%xmm0, %xmm2
	movaps	%xmm2, %xmm0
	orps	%xmm4, %xmm0
	movaps	%xmm1, %xmm2
	maxps	%xmm3, %xmm1
	movaps	%xmm1, %xmm3
	cmpunordps	%xmm1, %xmm3
	andps	%xmm3, %xmm2
	andnps	%xmm1, %xmm3
	movaps	%xmm3, %xmm1
	orps	%xmm2, %xmm1
	addq	$8, %r15
	cmpq	%r15, %r10
	jne	.LBB28_15
	movaps	%xmm0, %xmm2
	maxps	%xmm1, %xmm2
	movaps	%xmm2, %xmm1
	cmpunordps	%xmm2, %xmm1
	andps	%xmm1, %xmm0
	andnps	%xmm2, %xmm1
	orps	%xmm0, %xmm1
	pshufd	$255, %xmm1, %xmm2
	pshufd	$238, %xmm1, %xmm3
	pshufd	$245, %xmm1, %xmm4
	movaps	%xmm1, %xmm0
	cmpunordss	%xmm1, %xmm0
	movaps	%xmm0, %xmm5
	andps	%xmm4, %xmm5
	maxss	%xmm1, %xmm4
	andnps	%xmm4, %xmm0
	orps	%xmm5, %xmm0
	movdqa	%xmm3, %xmm1
	maxss	%xmm0, %xmm1
	cmpunordss	%xmm0, %xmm0
	movaps	%xmm0, %xmm4
	andnps	%xmm1, %xmm4
	andps	%xmm3, %xmm0
	orps	%xmm4, %xmm0
	movdqa	%xmm2, %xmm1
	maxss	%xmm0, %xmm1
	cmpunordss	%xmm0, %xmm0
	movaps	%xmm0, %xmm3
	andnps	%xmm1, %xmm3
	andps	%xmm2, %xmm0
	orps	%xmm3, %xmm0
	cmpq	%r10, %r9
	je	.LBB28_19
.LBB28_17:
	addq	%r8, %rax
	movaps	%xmm0, %xmm1
	.p2align	4
.LBB28_18:
	movaps	%xmm1, %xmm2
	maxss	(%rcx), %xmm2
	addq	$4, %rcx
	movaps	%xmm2, %xmm0
	cmpunordss	%xmm2, %xmm0
	movaps	%xmm0, %xmm3
	andnps	%xmm2, %xmm3
	andps	%xmm1, %xmm0
	orps	%xmm3, %xmm0
	movaps	%xmm0, %xmm1
	cmpq	%rax, %rcx
	jne	.LBB28_18
.LBB28_19:
	movd	%xmm0, %eax
	testl	%eax, %eax
	setns	%cl
	movl	%eax, %r8d
	andl	$2147483647, %r8d
	addl	$-8388608, %r8d
	cmpl	$2130706432, %r8d
	setb	%r8b
	andb	%cl, %r8b
	decl	%eax
	cmpl	$8388607, %eax
	setb	%al
	orb	%r8b, %al
	je	.LBB28_20
	cmpq	%rsi, %rdx
	cmovbq	%rdx, %rsi
	testq	%rsi, %rsi
	je	.LBB28_30
	movss	__real@477fff00(%rip), %xmm11
	movaps	%xmm11, %xmm12
	movaps	%xmm0, %xmm10
	divss	%xmm0, %xmm12
	cmpq	$4, %rsi
	jae	.LBB28_26
	xorl	%r14d, %r14d
	jmp	.LBB28_24
.LBB28_20:
	addq	%rsi, %rsi
	movq	%rdi, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	memset
	xorps	%xmm0, %xmm0
	jmp	.LBB28_30
.LBB28_26:
	andq	%rsi, %r14
	movaps	%xmm12, %xmm13
	shufps	$0, %xmm12, %xmm13
	leaq	(%rsi,%rsi), %r15
	andq	$-8, %r15
	xorl	%r12d, %r12d
	xorps	%xmm14, %xmm14
	.p2align	4
.LBB28_27:
	movups	(%rbx,%r12,2), %xmm7
	maxps	%xmm14, %xmm7
	mulps	%xmm13, %xmm7
	movaps	%xmm7, %xmm0
	shufps	$255, %xmm7, %xmm0
	callq	rintf
	movaps	%xmm0, %xmm6
	movaps	%xmm7, %xmm0
	unpckhpd	%xmm7, %xmm0
	callq	rintf
	movaps	%xmm0, %xmm8
	unpcklps	%xmm6, %xmm8
	movaps	%xmm7, %xmm0
	callq	rintf
	movaps	%xmm0, %xmm9
	movshdup	%xmm7, %xmm0
	callq	rintf
	xorps	%xmm1, %xmm1
	maxss	%xmm0, %xmm1
	movaps	%xmm11, %xmm0
	minss	%xmm1, %xmm0
	cvttss2si	%xmm0, %eax
	xorps	%xmm0, %xmm0
	maxss	%xmm9, %xmm0
	movaps	%xmm11, %xmm1
	minss	%xmm0, %xmm1
	cvttss2si	%xmm1, %ecx
	movd	%ecx, %xmm0
	pinsrw	$1, %eax, %xmm0
	xorps	%xmm1, %xmm1
	maxss	%xmm8, %xmm1
	movaps	%xmm11, %xmm2
	minss	%xmm1, %xmm2
	cvttss2si	%xmm2, %eax
	pinsrw	$2, %eax, %xmm0
	xorps	%xmm1, %xmm1
	maxss	%xmm6, %xmm1
	movaps	%xmm11, %xmm2
	minss	%xmm1, %xmm2
	cvttss2si	%xmm2, %eax
	pinsrw	$3, %eax, %xmm0
	movq	%xmm0, (%rdi,%r12)
	addq	$8, %r12
	cmpq	%r12, %r15
	jne	.LBB28_27
	cmpq	%r14, %rsi
	je	.LBB28_29
.LBB28_24:
	xorps	%xmm6, %xmm6
	.p2align	4
.LBB28_25:
	leaq	1(%r14), %r15
	movss	(%rbx,%r14,4), %xmm0
	maxss	%xmm6, %xmm0
	mulss	%xmm12, %xmm0
	callq	rintf
	xorps	%xmm1, %xmm1
	maxss	%xmm0, %xmm1
	movaps	%xmm11, %xmm0
	minss	%xmm1, %xmm0
	cvttss2si	%xmm0, %eax
	movw	%ax, (%rdi,%r14,2)
	movq	%r15, %r14
	cmpq	%r15, %rsi
	jne	.LBB28_25
.LBB28_29:
	movaps	%xmm10, %xmm0
.LBB28_30:
	movaps	96(%rsp), %xmm6
	movaps	112(%rsp), %xmm7
	movaps	128(%rsp), %xmm8
	movaps	144(%rsp), %xmm9
	movaps	160(%rsp), %xmm10
	movaps	176(%rsp), %xmm11
	movaps	192(%rsp), %xmm12
	movaps	208(%rsp), %xmm13
	movaps	224(%rsp), %xmm14
	movaps	240(%rsp), %xmm15
	.seh_startepilogue
	addq	$264, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r14
	popq	%r15
	.seh_endepilogue
	retq
.Lfunc_end28:
	.seh_endproc

	.def	main;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,main,unique,30
	.globl	main
	.p2align	4
main:
.Lfunc_begin29:
.seh_proc main
	subq	$56, %rsp
	.seh_stackalloc 56
	.seh_endprologue
	movq	%rdx, %r9
	movslq	%ecx, %r8
	leaq	_RNvCs2i4to50FHNk_9prototype4main(%rip), %rax
	movq	%rax, 48(%rsp)
	movb	$0, 32(%rsp)
	leaq	anon.dbe199b31d7695c3f4c2a183a6173b83.6(%rip), %rdx
	leaq	48(%rsp), %rcx
	callq	_RNvNtCse0R8cuyqEa_3std2rt19lang_start_internal
	nop
	.seh_startepilogue
	addq	$56, %rsp
	.seh_endepilogue
	retq
.Lfunc_end29:
	.seh_endproc

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.0,unique,31
	.p2align	3, 0x0
anon.dbe199b31d7695c3f4c2a183a6173b83.0:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRmNtB6_5Debug3fmtCs2i4to50FHNk_9prototype

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.2,unique,32
	.p2align	3, 0x0
anon.dbe199b31d7695c3f4c2a183a6173b83.2:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRtNtB6_5Debug3fmtCs2i4to50FHNk_9prototype

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.3,unique,33
	.p2align	3, 0x0
anon.dbe199b31d7695c3f4c2a183a6173b83.3:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRINtNtCsfQUUnEvlYZE_5alloc3vec3VecmENtB6_5Debug3fmtCs2i4to50FHNk_9prototype

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.4,unique,34
	.p2align	3, 0x0
anon.dbe199b31d7695c3f4c2a183a6173b83.4:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRINtNtCsfQUUnEvlYZE_5alloc3vec3VecsENtB6_5Debug3fmtCs2i4to50FHNk_9prototype

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.5,unique,35
	.p2align	3, 0x0
anon.dbe199b31d7695c3f4c2a183a6173b83.5:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRINtNtCsfQUUnEvlYZE_5alloc3vec3VectENtB6_5Debug3fmtCs2i4to50FHNk_9prototype

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.6,unique,36
	.p2align	3, 0x0
anon.dbe199b31d7695c3f4c2a183a6173b83.6:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvNtCse0R8cuyqEa_3std2rt10lang_startuE0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableCs2i4to50FHNk_9prototype
	.quad	_RNCINvNtCse0R8cuyqEa_3std2rt10lang_startuE0Cs2i4to50FHNk_9prototype
	.quad	_RNCINvNtCse0R8cuyqEa_3std2rt10lang_startuE0Cs2i4to50FHNk_9prototype

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.7,unique,37
anon.dbe199b31d7695c3f4c2a183a6173b83.7:
	.ascii	"positive_zero"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.8,unique,38
anon.dbe199b31d7695c3f4c2a183a6173b83.8:
	.ascii	"--proof-only"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.9,unique,39
anon.dbe199b31d7695c3f4c2a183a6173b83.9:
	.ascii	"--inject-failure"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.10,unique,40
anon.dbe199b31d7695c3f4c2a183a6173b83.10:
	.ascii	"{\"stage\":\"complete\",\"diagnostic_only\":true,\"end_to_end_claim\":false}\n"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.11,unique,41
anon.dbe199b31d7695c3f4c2a183a6173b83.11:
	.ascii	"empty"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.12,unique,42
anon.dbe199b31d7695c3f4c2a183a6173b83.12:
	.asciz	"\nsingleton_\303 \000\000i\b\000"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.13,unique,43
	.p2align	3, 0x0
anon.dbe199b31d7695c3f4c2a183a6173b83.13:
	.asciz	"\000\000\000\000\000\000\000\000\001\000\000\000\000\000\000\000\002\000\000\000\000\000\000\000\003\000\000\000\000\000\000\000\007\000\000\000\000\000\000\000\017\000\000\000\000\000\000\000\020\000\000\000\000\000\000\000\021\000\000\000\000\000\000\000\037\000\000\000\000\000\000\000 \000\000\000\000\000\000\000!\000\000\000\000\000\000\000?\000\000\000\000\000\000\000@\000\000\000\000\000\000\000A\000\000\000\000\000\000\000\177\000\000\000\000\000\000\000\200\000\000\000\000\000\000\000\201\000\000\000\000\000\000\000\377\000\000\000\000\000\000\000\000\001\000\000\000\000\000\000\001\001\000\000\000\000\000\000\377\001\000\000\000\000\000\000\000\002\000\000\000\000\000\000\001\002\000\000\000\000\000\000\377\003\000\000\000\000\000\000\000\004\000\000\000\000\000\000\001\004\000\000\000\000\000\000\377\017\000\000\000\000\000\000\000\020\000\000\000\000\000\000\001\020\000\000\000\000\000"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.14,unique,44
anon.dbe199b31d7695c3f4c2a183a6173b83.14:
	.asciz	"\rsigned_zeros_\300"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.15,unique,45
anon.dbe199b31d7695c3f4c2a183a6173b83.15:
	.asciz	"\016special_cycle_\300"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.16,unique,46
anon.dbe199b31d7695c3f4c2a183a6173b83.16:
	.asciz	"\ball_nan_\300"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.17,unique,47
anon.dbe199b31d7695c3f4c2a183a6173b83.17:
	.asciz	"\rnegative_u16_\300"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.18,unique,48
anon.dbe199b31d7695c3f4c2a183a6173b83.18:
	.asciz	"\rmixed_finite_\303 \000\000i\b\000"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.19,unique,49
anon.dbe199b31d7695c3f4c2a183a6173b83.19:
	.ascii	"max_finite_and_tiny"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.20,unique,50
anon.dbe199b31d7695c3f4c2a183a6173b83.20:
	.asciz	"\007random_\303 \000\000i\004\000\006_mode_\300"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.21,unique,51
anon.dbe199b31d7695c3f4c2a183a6173b83.21:
	.asciz	"\nlong_tail_\300"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.22,unique,52
anon.dbe199b31d7695c3f4c2a183a6173b83.22:
	.asciz	"\013tiny_scale_\303 \000\000i\b\000"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.23,unique,53
anon.dbe199b31d7695c3f4c2a183a6173b83.23:
	.asciz	"\022ties_adjacent_max_\300"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.24,unique,54
anon.dbe199b31d7695c3f4c2a183a6173b83.24:
	.asciz	"prototype.rs"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.25,unique,55
anon.dbe199b31d7695c3f4c2a183a6173b83.25:
	.asciz	"\ni16 scale \300"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.26,unique,56
	.p2align	3, 0x0
anon.dbe199b31d7695c3f4c2a183a6173b83.26:
	.quad	anon.dbe199b31d7695c3f4c2a183a6173b83.24
	.asciz	"\f\000\000\000\000\000\000\000R\000\000\000\t\000\000"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.27,unique,57
anon.dbe199b31d7695c3f4c2a183a6173b83.27:
	.asciz	"\nu16 scale \300"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.28,unique,58
	.p2align	3, 0x0
anon.dbe199b31d7695c3f4c2a183a6173b83.28:
	.quad	anon.dbe199b31d7695c3f4c2a183a6173b83.24
	.asciz	"\f\000\000\000\000\000\000\000S\000\000\000\t\000\000"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.29,unique,59
anon.dbe199b31d7695c3f4c2a183a6173b83.29:
	.asciz	"\ni16 words \300"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.30,unique,60
	.p2align	3, 0x0
anon.dbe199b31d7695c3f4c2a183a6173b83.30:
	.quad	anon.dbe199b31d7695c3f4c2a183a6173b83.24
	.asciz	"\f\000\000\000\000\000\000\000T\000\000\000\t\000\000"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.31,unique,61
anon.dbe199b31d7695c3f4c2a183a6173b83.31:
	.asciz	"\nu16 words \300"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.32,unique,62
	.p2align	3, 0x0
anon.dbe199b31d7695c3f4c2a183a6173b83.32:
	.quad	anon.dbe199b31d7695c3f4c2a183a6173b83.24
	.asciz	"\f\000\000\000\000\000\000\000U\000\000\000\t\000\000"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.33,unique,63
anon.dbe199b31d7695c3f4c2a183a6173b83.33:
	.asciz	"\013input bits \300"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.34,unique,64
	.p2align	3, 0x0
anon.dbe199b31d7695c3f4c2a183a6173b83.34:
	.quad	anon.dbe199b31d7695c3f4c2a183a6173b83.24
	.asciz	"\f\000\000\000\000\000\000\000[\000\000\000\t\000\000"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.35,unique,65
	.p2align	1, 0x0
anon.dbe199b31d7695c3f4c2a183a6173b83.35:
	.ascii	"Z\245"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.36,unique,66
anon.dbe199b31d7695c3f4c2a183a6173b83.36:
	.asciz	"\nu16 guard \300"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.37,unique,67
	.p2align	3, 0x0
anon.dbe199b31d7695c3f4c2a183a6173b83.37:
	.quad	anon.dbe199b31d7695c3f4c2a183a6173b83.24
	.asciz	"\f\000\000\000\000\000\000\000X\000\000\000\r\000\000"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.38,unique,68
anon.dbe199b31d7695c3f4c2a183a6173b83.38:
	.asciz	"\ni16 guard \300"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.39,unique,69
	.p2align	3, 0x0
anon.dbe199b31d7695c3f4c2a183a6173b83.39:
	.quad	anon.dbe199b31d7695c3f4c2a183a6173b83.24
	.asciz	"\f\000\000\000\000\000\000\000W\000\000\000\r\000\000"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.40,unique,70
	.p2align	3, 0x0
anon.dbe199b31d7695c3f4c2a183a6173b83.40:
	.ascii	"\r\360\026\020& \355^"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.41,unique,71
anon.dbe199b31d7695c3f4c2a183a6173b83.41:
	.asciz	"+{\"stage\":\"proof\",\"exact\":true,\"d010_cases\":\300\022,\"cases_per_type\":\300\023,\"values_per_type\":\300\024,\"q_words_compared\":\300\027,\"scale_bits_compared\":\300\027,\"guard_words_checked\":\300%,\"input_bits_unchanged\":true,\"seed\":\"\303 \000\000i\020\000\031\",\"case_manifest_fnv64\":\"\303 \000\000i\020\000\021\",\"input_fnv64\":\"\303 \000\000i\020\000\022\",\"output_fnv64\":\"\303 \000\000i\020\000\003\"}\n"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.42,unique,72
anon.dbe199b31d7695c3f4c2a183a6173b83.42:
	.asciz	"\rextra_random_\300"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.43,unique,73
	.p2align	3, 0x0
anon.dbe199b31d7695c3f4c2a183a6173b83.43:
	.quad	anon.dbe199b31d7695c3f4c2a183a6173b83.24
	.asciz	"\f\000\000\000\000\000\000\000+\000\000\000\027\000\000"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.44,unique,74
anon.dbe199b31d7695c3f4c2a183a6173b83.44:
	.asciz	"\013lane_tail_n\300\003_at\300\001_\303 \000\000i\b\000"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.45,unique,75
	.p2align	3, 0x0
anon.dbe199b31d7695c3f4c2a183a6173b83.45:
	.quad	anon.dbe199b31d7695c3f4c2a183a6173b83.24
	.asciz	"\f\000\000\000\000\000\000\000.\000\000\000\027\000\000"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.46,unique,76
anon.dbe199b31d7695c3f4c2a183a6173b83.46:
	.asciz	"\fmixed_lane_n\300\003_at\300\001_\303 \000\000i\b\000"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.49,unique,77
anon.dbe199b31d7695c3f4c2a183a6173b83.49:
	.ascii	"finite"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.50,unique,78
	.p2align	3, 0x0
anon.dbe199b31d7695c3f4c2a183a6173b83.50:
	.quad	anon.dbe199b31d7695c3f4c2a183a6173b83.24
	.asciz	"\f\000\000\000\000\000\000\000\177\000\000\000\030\000\000"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.51,unique,79
anon.dbe199b31d7695c3f4c2a183a6173b83.51:
	.ascii	"u16"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.52,unique,80
anon.dbe199b31d7695c3f4c2a183a6173b83.52:
	.ascii	"i16"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.53,unique,81
anon.dbe199b31d7695c3f4c2a183a6173b83.53:
	.ascii	"baseline"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.54,unique,82
anon.dbe199b31d7695c3f4c2a183a6173b83.54:
	.ascii	"four_lane"

	.section	.rdata,"dr",one_only,anon.dbe199b31d7695c3f4c2a183a6173b83.55,unique,83
anon.dbe199b31d7695c3f4c2a183a6173b83.55:
	.asciz	"\032{\"stage\":\"timing\",\"type\":\"\300\n\",\"mode\":\"\300\013\",\"length\":\300\b,\"pair\":\300\023,\"candidate_first\":\300\f,\"variant\":\"\300\t\",\"reps\":\300\020,\"ns_per_block\":\305 \000\000p\006\000\002}\n"

	.section	.debug$S,"dr"
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp159-.Ltmp158
.Ltmp158:
	.short	.Ltmp161-.Ltmp160
.Ltmp160:
	.short	4353
	.long	0
	.asciz	"prototype.prototype.1ab0bb7343479e38-cgu.0.rcgu.o"
	.p2align	2, 0x0
.Ltmp161:
	.short	.Ltmp163-.Ltmp162
.Ltmp162:
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
.Ltmp163:
.Ltmp159:
	.p2align	2, 0x0
	.cv_filechecksums
	.cv_stringtable
	.long	241
	.long	.Ltmp165-.Ltmp164
.Ltmp164:
	.short	.Ltmp167-.Ltmp166
.Ltmp166:
	.short	4428
	.long	4099
	.p2align	2, 0x0
.Ltmp167:
.Ltmp165:
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
	.globl	_fltused
