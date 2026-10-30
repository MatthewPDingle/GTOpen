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
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.36(%rip), %rcx
	movq	%rcx, 56(%rsp)
	movq	%r8, 48(%rsp)
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.35(%rip), %rcx
	movq	%rcx, 40(%rsp)
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.3(%rip), %r8
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
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.32(%rip), %rcx
	movq	%rcx, 56(%rsp)
	movq	%r8, 48(%rsp)
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.31(%rip), %rcx
	movq	%rcx, 40(%rsp)
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.4(%rip), %r8
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
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.34(%rip), %rcx
	movq	%rcx, 56(%rsp)
	movq	%r8, 48(%rsp)
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.33(%rip), %rcx
	movq	%rcx, 40(%rsp)
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.5(%rip), %r8
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
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.0(%rip), %r8
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
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.37(%rip), %rcx
	leaq	80(%rsp), %r10
	movq	%rcx, (%r10)
	movq	%r9, 56(%rsp)
	movq	%r8, 48(%rsp)
	movq	%rdx, 40(%rsp)
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.2(%rip), %r8
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
	movq	_RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache5CACHE(%rip), %rax
	testq	%rax, %rax
	je	.LBB12_1
	testl	$1024, %eax
	je	.LBB12_740
.LBB12_3:
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.11(%rip), %rcx
	movl	$175, %edx
	callq	_RNvNtNtCse0R8cuyqEa_3std2io5stdio6__print
	leaq	192(%rbp), %rsi
	movq	%rsi, %rcx
	callq	_RNvNtCse0R8cuyqEa_3std3env7args_os
	leaq	480(%rbp), %rdi
	movdqa	__xmm@6572756c6961662d7463656a6e692d2d(%rip), %xmm6
	movq	__imp_GetProcessHeap(%rip), %r15
	movq	__imp_HeapFree(%rip), %r12
	jmp	.LBB12_4
	.p2align	4
.LBB12_11:
	testb	%r14b, %r14b
	jne	.LBB12_12
.LBB12_4:
.Ltmp4:
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	callq	_RNvXsc_NtCse0R8cuyqEa_3std3envNtB5_4ArgsNtNtNtNtCs8xEFJqa6dYS_4core4iter6traits8iterator8Iterator4next
	nop
.Ltmp5:
	movq	480(%rbp), %r13
	cmpq	$-1, %r13
	je	.LBB12_12
	movq	488(%rbp), %rbx
	cmpq	$16, 496(%rbp)
	jne	.LBB12_7
	movdqu	(%rbx), %xmm0
	pcmpeqb	%xmm6, %xmm0
	pmovmskb	%xmm0, %eax
	cmpl	$65535, %eax
	sete	%r14b
	testq	%r13, %r13
	jne	.LBB12_10
	jmp	.LBB12_11
	.p2align	4
.LBB12_7:
	xorl	%r14d, %r14d
	testq	%r13, %r13
	je	.LBB12_11
.LBB12_10:
	callq	*%r15
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rbx, %r8
	callq	*%r12
	jmp	.LBB12_11
.LBB12_12:
	movq	200(%rbp), %rdi
	movq	216(%rbp), %rbx
	subq	%rdi, %rbx
	je	.LBB12_17
	shrq	$5, %rbx
	addq	$8, %rdi
	jmp	.LBB12_14
	.p2align	4
.LBB12_16:
	addq	$32, %rdi
	decq	%rbx
	je	.LBB12_17
.LBB12_14:
	cmpq	$0, -8(%rdi)
	je	.LBB12_16
	movq	(%rdi), %rsi
	callq	*%r15
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*%r12
	jmp	.LBB12_16
.LBB12_17:
	movq	%r13, 184(%rbp)
	cmpq	$0, 208(%rbp)
	je	.LBB12_19
	movq	192(%rbp), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_19:
	movq	$0, 656(%rbp)
	movq	$8, 664(%rbp)
	movq	$0, 672(%rbp)
	movaps	__xmm@80000001000000018000000000000000(%rip), %xmm7
	movaps	%xmm7, 192(%rbp)
	movaps	__xmm@8080000000800000807fffff007fffff(%rip), %xmm0
	movaps	%xmm0, 208(%rbp)
	movaps	__xmm@ff7fffff7f7fffffbf8000003f800000(%rip), %xmm0
	movaps	%xmm0, 224(%rbp)
	movdqa	__xmm@ffc001237fc00000ff8000007f800000(%rip), %xmm0
	movdqa	%xmm0, 240(%rbp)
	movabsq	$-36028790584901631, %rax
	movq	%rax, 256(%rbp)
	movq	$0, 480(%rbp)
	movq	$4, 488(%rbp)
	movq	$0, 496(%rbp)
.Ltmp6:
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.13(%rip), %rdx
	leaq	656(%rbp), %rcx
	leaq	480(%rbp), %r9
	movl	$5, %r8d
	callq	_RINvCs2i4to50FHNk_9prototype3addReEB2_
	nop
.Ltmp7:
	xorl	%r13d, %r13d
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.14(%rip), %rsi
	leaq	480(%rbp), %rdi
	leaq	408(%rbp), %rbx
	jmp	.LBB12_21
	.p2align	4
.LBB12_45:
	addq	$4, %r13
	movq	664(%rbp), %rax
	leaq	(%r12,%r12,2), %rcx
	shlq	$4, %rcx
	movdqu	480(%rbp), %xmm0
	movdqu	496(%rbp), %xmm1
	movdqu	512(%rbp), %xmm2
	movdqu	%xmm2, 32(%rax,%rcx)
	movdqu	%xmm1, 16(%rax,%rcx)
	movdqu	%xmm0, (%rax,%rcx)
	incq	%r12
	movq	%r12, 672(%rbp)
.LBB12_21:
	cmpq	$72, %r13
	je	.LBB12_22
	movl	192(%rbp,%r13), %eax
	movl	%eax, 456(%rbp)
	leaq	456(%rbp), %rax
	movq	%rax, 408(%rbp)
	leaq	_RNvXsu_NtNtCs8xEFJqa6dYS_4core3fmt3nummNtB7_8LowerHex3fmt(%rip), %rax
	movq	%rax, 416(%rbp)
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
	je	.LBB12_41
	movss	456(%rbp), %xmm0
	movss	%xmm0, (%rax)
	movq	%r14, 480(%rbp)
	movq	%r15, 488(%rbp)
	movq	%r12, 496(%rbp)
	movq	$1, 504(%rbp)
	movq	%rax, 512(%rbp)
	movq	$1, 520(%rbp)
	movq	672(%rbp), %r12
	cmpq	656(%rbp), %r12
	jne	.LBB12_45
.Ltmp10:
	leaq	656(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	nop
.Ltmp11:
	jmp	.LBB12_45
.LBB12_22:
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
	je	.LBB12_24
.LBB12_51:
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.15(%rip), %rax
	movq	%rsi, 712(%rbp)
	movq	(%rsi,%rax), %rax
	movq	%rax, 456(%rbp)
	leaq	456(%rbp), %rax
	movq	%rax, 408(%rbp)
	leaq	_RNvXsi_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impjNtB9_7Display3fmt(%rip), %rax
	movq	%rax, 416(%rbp)
.Ltmp14:
	leaq	480(%rbp), %rcx
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.16(%rip), %rdx
	leaq	408(%rbp), %r8
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
	movq	%rbx, 688(%rbp)
	movq	%r15, 696(%rbp)
	jne	.LBB12_60
	movq	496(%rbp), %rdi
	testq	%r13, %r13
	je	.LBB12_54
	xorl	%edx, %edx
	movq	%r13, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rsi, %rcx
	testq	%rax, %rax
	je	.LBB12_59
	testq	%rsi, %rsi
	jne	.LBB12_56
	jmp	.LBB12_67
.LBB12_54:
	movl	$4, %eax
	xorl	%ecx, %ecx
	testq	%rsi, %rsi
	je	.LBB12_67
.LBB12_56:
	cmpq	$8, %rsi
	jae	.LBB12_61
	xorl	%edx, %edx
	jmp	.LBB12_64
.LBB12_61:
	movq	%rsi, %rdx
	movabsq	$4611686018427387896, %r8
	andq	%r8, %rdx
	xorl	%r8d, %r8d
	movdqa	%xmm10, %xmm0
	movdqa	%xmm9, %xmm1
	.p2align	4
.LBB12_62:
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
	jne	.LBB12_62
	.p2align	4
.LBB12_63:
	cmpq	%rdx, %rsi
	je	.LBB12_67
.LBB12_64:
	pxor	%xmm0, %xmm0
	testb	$1, %dl
	je	.LBB12_66
	movdqa	%xmm8, %xmm0
.LBB12_66:
	movd	%xmm0, (%rax,%rdx,4)
	incq	%rdx
	jmp	.LBB12_63
	.p2align	4
.LBB12_67:
	movq	%r15, 480(%rbp)
	movq	%rbx, 488(%rbp)
	movq	%rdi, 496(%rbp)
	movq	%rcx, 504(%rbp)
	movq	%rax, 512(%rbp)
	movq	%rsi, 520(%rbp)
	movq	672(%rbp), %rax
	movq	%rax, 736(%rbp)
	cmpq	656(%rbp), %rax
	jne	.LBB12_69
.Ltmp16:
	leaq	656(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	nop
.Ltmp17:
.LBB12_69:
	movq	664(%rbp), %rbx
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
	movq	%rdi, 672(%rbp)
	leaq	456(%rbp), %rax
	movq	%rax, 408(%rbp)
	leaq	_RNvXsi_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impjNtB9_7Display3fmt(%rip), %rax
	movq	%rax, 416(%rbp)
.Ltmp18:
	leaq	480(%rbp), %rcx
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.17(%rip), %rdx
	leaq	408(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp19:
	movq	480(%rbp), %rax
	movq	%rax, 696(%rbp)
	movq	488(%rbp), %r15
	movq	496(%rbp), %r12
	testq	%r13, %r13
	je	.LBB12_71
	xorl	%edx, %edx
	movq	%r13, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rax, %rcx
	movq	%rsi, %r9
	testq	%rax, %rax
	je	.LBB12_76
	testq	%rsi, %rsi
	jne	.LBB12_73
	jmp	.LBB12_81
.LBB12_71:
	movl	$4, %ecx
	xorl	%r9d, %r9d
	testq	%rsi, %rsi
	je	.LBB12_81
.LBB12_73:
	cmpq	$1, %rsi
	jne	.LBB12_77
	xorl	%r8d, %r8d
	jmp	.LBB12_80
.LBB12_77:
	movq	%rsi, %r10
	movabsq	$4611686018427387902, %rax
	andq	%rax, %r10
	xorl	%r8d, %r8d
	movabsq	$-2049638230412172401, %r11
	.p2align	4
.LBB12_78:
	movq	%r8, %rax
	mulq	%r11
	shrq	%rdx
	andq	$-8, %rdx
	leaq	(%rdx,%rdx,8), %rax
	negq	%rax
	addq	%rbp, %rax
	addq	$192, %rax
	movss	(%rax,%r8,4), %xmm0
	movss	%xmm0, (%rcx,%r8,4)
	movd	4(%rax,%r8,4), %xmm0
	movd	%xmm0, 4(%rcx,%r8,4)
	addq	$2, %r8
	cmpq	%r8, %r10
	jne	.LBB12_78
	testb	$1, %sil
	je	.LBB12_81
.LBB12_80:
	movq	%r8, %rax
	movabsq	$-2049638230412172401, %rdx
	mulq	%rdx
	shrq	$4, %rdx
	addl	%edx, %edx
	leal	(%rdx,%rdx,8), %eax
	movl	%r8d, %edx
	subl	%eax, %edx
	movd	192(%rbp,%rdx,4), %xmm0
	movd	%xmm0, (%rcx,%r8,4)
.LBB12_81:
	movq	696(%rbp), %rax
	movq	%rax, 480(%rbp)
	movq	%r15, 488(%rbp)
	movq	%r12, 496(%rbp)
	movq	%r9, 504(%rbp)
	movq	%rcx, 512(%rbp)
	movq	%rsi, 520(%rbp)
	cmpq	656(%rbp), %rdi
	jne	.LBB12_84
.Ltmp22:
	movq	%r15, 688(%rbp)
	leaq	656(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	nop
.Ltmp23:
	movq	664(%rbp), %rbx
.LBB12_84:
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
	movq	%rdi, 672(%rbp)
	leaq	456(%rbp), %rax
	movq	%rax, 408(%rbp)
	leaq	_RNvXsi_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impjNtB9_7Display3fmt(%rip), %rax
	movq	%rax, 416(%rbp)
.Ltmp24:
	leaq	480(%rbp), %rcx
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.18(%rip), %rdx
	leaq	408(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp25:
	movq	480(%rbp), %rax
	movq	%rax, 696(%rbp)
	movq	488(%rbp), %r15
	movq	496(%rbp), %r12
	testq	%r13, %r13
	je	.LBB12_86
	xorl	%edx, %edx
	movq	%r13, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rsi, %rcx
	testq	%rax, %rax
	je	.LBB12_91
	testq	%rsi, %rsi
	jne	.LBB12_88
	jmp	.LBB12_96
.LBB12_86:
	movl	$4, %eax
	xorl	%ecx, %ecx
	testq	%rsi, %rsi
	je	.LBB12_96
.LBB12_88:
	leaq	-1(%rsi), %r8
	movl	%esi, %edx
	andl	$3, %edx
	cmpq	$3, %r8
	jae	.LBB12_92
	xorl	%r8d, %r8d
	jmp	.LBB12_95
.LBB12_92:
	movq	%rsi, %r9
	movabsq	$4611686018427387900, %r8
	andq	%r8, %r9
	movd	248(%rbp), %xmm0
	movd	252(%rbp), %xmm1
	movd	256(%rbp), %xmm2
	movd	260(%rbp), %xmm3
	xorl	%r8d, %r8d
	.p2align	4
.LBB12_93:
	movd	%xmm0, (%rax,%r8,4)
	movd	%xmm1, 4(%rax,%r8,4)
	movd	%xmm2, 8(%rax,%r8,4)
	movd	%xmm3, 12(%rax,%r8,4)
	addq	$4, %r8
	cmpq	%r8, %r9
	jne	.LBB12_93
	testq	%rdx, %rdx
	je	.LBB12_96
	.p2align	4
.LBB12_95:
	movl	%r8d, %r9d
	andl	$3, %r9d
	movd	248(%rbp,%r9,4), %xmm0
	movd	%xmm0, (%rax,%r8,4)
	incq	%r8
	decq	%rdx
	jne	.LBB12_95
.LBB12_96:
	movq	696(%rbp), %rdx
	movq	%rdx, 480(%rbp)
	movq	%r15, 488(%rbp)
	movq	%r12, 496(%rbp)
	movq	%rcx, 504(%rbp)
	movq	%rax, 512(%rbp)
	movq	%rsi, 520(%rbp)
	cmpq	656(%rbp), %rdi
	jne	.LBB12_99
.Ltmp28:
	movq	%r15, 688(%rbp)
	leaq	656(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	nop
.Ltmp29:
	movq	664(%rbp), %rbx
.LBB12_99:
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
	movq	%rax, 672(%rbp)
	leaq	456(%rbp), %rax
	movq	%rax, 408(%rbp)
	leaq	_RNvXsi_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impjNtB9_7Display3fmt(%rip), %rax
	movq	%rax, 416(%rbp)
.Ltmp30:
	leaq	480(%rbp), %rcx
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.19(%rip), %rdx
	leaq	408(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp31:
	movq	480(%rbp), %rax
	movq	%rax, 688(%rbp)
	movq	488(%rbp), %rdi
	movq	496(%rbp), %r12
	testq	%r13, %r13
	je	.LBB12_101
	xorl	%edx, %edx
	movq	%r13, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rax, %rcx
	movq	%rsi, %r15
	testq	%rax, %rax
	je	.LBB12_106
	testq	%rsi, %rsi
	movq	696(%rbp), %r13
	jne	.LBB12_103
	jmp	.LBB12_112
.LBB12_101:
	movl	$4, %ecx
	xorl	%r15d, %r15d
	testq	%rsi, %rsi
	movq	696(%rbp), %r13
	je	.LBB12_112
.LBB12_103:
	cmpq	$1, %rsi
	jne	.LBB12_107
	xorl	%r8d, %r8d
	jmp	.LBB12_111
.LBB12_107:
	movq	%r12, 648(%rbp)
	movq	%rdi, 640(%rbp)
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
.LBB12_108:
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
	jne	.LBB12_108
	testb	$1, %sil
	movl	$0, %eax
	movq	%rax, 728(%rbp)
	movq	640(%rbp), %rdi
	movq	696(%rbp), %r13
	movq	648(%rbp), %r12
	je	.LBB12_112
	negq	%r8
.LBB12_111:
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
.LBB12_112:
	movq	688(%rbp), %rax
	movq	%rax, 480(%rbp)
	movq	%rdi, 488(%rbp)
	movq	%r12, 496(%rbp)
	movq	%r15, 504(%rbp)
	movq	%rcx, 512(%rbp)
	movq	%rsi, 520(%rbp)
	cmpq	656(%rbp), %r13
	movq	712(%rbp), %rsi
	jne	.LBB12_115
.Ltmp34:
	movq	%rdi, 640(%rbp)
	leaq	656(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	nop
.Ltmp35:
	movq	664(%rbp), %rbx
.LBB12_115:
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
	movq	%rax, 672(%rbp)
	cmpq	$232, %rsi
	jne	.LBB12_51
.LBB12_24:
	xorl	%r13d, %r13d
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.20(%rip), %rsi
	leaq	480(%rbp), %rdi
	leaq	408(%rbp), %rbx
	movd	__real@bf800000(%rip), %xmm8
	jmp	.LBB12_25
	.p2align	4
.LBB12_138:
	addq	$4, %r13
	movq	664(%rbp), %rax
	leaq	(%r12,%r12,2), %rcx
	shlq	$4, %rcx
	movdqu	480(%rbp), %xmm0
	movdqu	496(%rbp), %xmm1
	movdqu	512(%rbp), %xmm2
	movdqu	%xmm2, 32(%rax,%rcx)
	movdqu	%xmm1, 16(%rax,%rcx)
	movdqu	%xmm0, (%rax,%rcx)
	incq	%r12
	movq	%r12, 672(%rbp)
.LBB12_25:
	cmpq	$72, %r13
	je	.LBB12_144
	movl	192(%rbp,%r13), %eax
	movl	%eax, 456(%rbp)
	leaq	456(%rbp), %rax
	movq	%rax, 408(%rbp)
	leaq	_RNvXsu_NtNtCs8xEFJqa6dYS_4core3fmt3nummNtB7_8LowerHex3fmt(%rip), %rax
	movq	%rax, 416(%rbp)
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
	je	.LBB12_28
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
	movq	672(%rbp), %r12
	cmpq	656(%rbp), %r12
	jne	.LBB12_138
.Ltmp40:
	leaq	656(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	nop
.Ltmp41:
	jmp	.LBB12_138
.LBB12_144:
	movq	$2, 160(%rbp)
	movabsq	$281470681776127, %rax
	movq	%rax, 168(%rbp)
	leaq	504(%rbp), %r15
	xorl	%eax, %eax
	movdqa	__xmm@00000003000000020000000100000000(%rip), %xmm9
	movdqa	__xmm@00000081000000800000007f0000007e(%rip), %xmm10
	movdqa	__xmm@0000fffd00007ffd00003fff000003ff(%rip), %xmm11
	leaq	480(%rbp), %rdi
	movss	__real@3f000000(%rip), %xmm8
	leaq	616(%rbp), %r14
	jmp	.LBB12_145
	.p2align	4
.LBB12_237:
	movq	664(%rbp), %rax
	leaq	(%rsi,%rsi,2), %rcx
	shlq	$4, %rcx
	movdqa	480(%rbp), %xmm0
	movdqa	496(%rbp), %xmm1
	movdqa	512(%rbp), %xmm2
	movdqu	%xmm2, 32(%rax,%rcx)
	movdqu	%xmm1, 16(%rax,%rcx)
	movdqu	%xmm0, (%rax,%rcx)
	incq	%rsi
	movq	%rsi, 672(%rbp)
	movq	%r13, %rax
.LBB12_145:
	cmpq	$2, %rax
	je	.LBB12_148
	leaq	1(%rax), %r13
	movq	%r13, 152(%rbp)
	movl	168(%rbp,%rax,4), %eax
	movl	%eax, 64(%rbp)
	movl	$4, %r8d
	xorl	%edx, %edx
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	je	.LBB12_147
	movl	64(%rbp), %ecx
	xorps	%xmm0, %xmm0
	cvtsi2ss	%rcx, %xmm0
	movss	%xmm0, (%rax)
	movq	$1, 616(%rbp)
	movq	%rax, 624(%rbp)
	movq	$1, 632(%rbp)
	movq	$12, 488(%rbp)
	movdqu	%xmm9, 496(%rbp)
	movdqu	%xmm10, 512(%rbp)
	movdqu	%xmm11, 528(%rbp)
	movl	$1, %ebx
	xorl	%esi, %esi
.LBB12_223:
	movl	64(%rbp), %ecx
	.p2align	4
.LBB12_224:
	cmpq	$12, %rsi
	je	.LBB12_234
	movl	496(%rbp,%rsi,4), %edx
	incq	%rsi
	cmpl	%ecx, %edx
	jae	.LBB12_224
	movq	%rsi, 480(%rbp)
	movl	%edx, %ecx
	xorps	%xmm0, %xmm0
	cvtsi2ss	%rcx, %xmm0
	addss	%xmm8, %xmm0
	movd	%xmm0, %ecx
	leal	-1(%rcx), %edx
	incl	%ecx
	movq	$3, 416(%rbp)
	movl	%edx, 424(%rbp)
	movss	%xmm0, 428(%rbp)
	movl	%ecx, 432(%rbp)
	xorl	%ecx, %ecx
	jmp	.LBB12_227
	.p2align	4
.LBB12_233:
	pxor	%xmm6, %xmm12
	movq	624(%rbp), %rax
	movd	%xmm12, 4(%rax,%rbx,4)
	addq	$2, %rbx
	movq	%rbx, 632(%rbp)
	movq	%r12, %rcx
.LBB12_227:
	cmpq	$3, %rcx
	je	.LBB12_223
	leaq	1(%rcx), %r12
	movq	%r12, 408(%rbp)
	movd	424(%rbp,%rcx,4), %xmm12
	cmpq	616(%rbp), %rbx
	jne	.LBB12_231
	movb	$1, 726(%rbp)
.Ltmp44:
	movq	%r14, %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecfE8grow_oneCs2i4to50FHNk_9prototype
	nop
.Ltmp45:
	movq	624(%rbp), %rax
.LBB12_231:
	movd	%xmm12, (%rax,%rbx,4)
	leaq	1(%rbx), %rax
	movq	%rax, 632(%rbp)
	cmpq	616(%rbp), %rax
	jne	.LBB12_233
	movb	$1, 726(%rbp)
.Ltmp46:
	movq	%r14, %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecfE8grow_oneCs2i4to50FHNk_9prototype
	nop
.Ltmp47:
	jmp	.LBB12_233
	.p2align	4
.LBB12_234:
	leaq	64(%rbp), %rax
	movq	%rax, 480(%rbp)
	leaq	_RNvXs8_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impmNtB9_7Display3fmt(%rip), %rax
	movq	%rax, 488(%rbp)
	movb	$1, 726(%rbp)
.Ltmp48:
	leaq	456(%rbp), %rcx
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.25(%rip), %rdx
	movq	%rdi, %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp49:
	movq	632(%rbp), %rax
	movq	%rax, 16(%r15)
	movups	616(%rbp), %xmm0
	movups	%xmm0, (%r15)
	movups	456(%rbp), %xmm0
	movaps	%xmm0, 480(%rbp)
	movq	472(%rbp), %rax
	movq	%rax, 496(%rbp)
	movq	672(%rbp), %rsi
	cmpq	656(%rbp), %rsi
	jne	.LBB12_237
.Ltmp50:
	leaq	656(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	nop
.Ltmp51:
	jmp	.LBB12_237
.LBB12_148:
	movq	$6, 416(%rbp)
	movdqa	__xmm@00800000007fffff0000000200000001(%rip), %xmm0
	movdqu	%xmm0, 424(%rbp)
	movabsq	$288230376185266176, %rax
	movq	%rax, 440(%rbp)
	xorl	%eax, %eax
	leaq	480(%rbp), %rdi
	leaq	616(%rbp), %rbx
	movsd	__xmm@0000000000000000bf0000003f000000(%rip), %xmm9
	movsd	__xmm@00000000000000008000000000000000(%rip), %xmm10
	movq	__xmm@0000000000000000ff8000017fc00123(%rip), %xmm11
	jmp	.LBB12_149
	.p2align	4
.LBB12_216:
	movq	664(%rbp), %rax
	leaq	(%r12,%r12,2), %rcx
	shlq	$4, %rcx
	movdqu	480(%rbp), %xmm0
	movdqu	496(%rbp), %xmm1
	movdqu	512(%rbp), %xmm2
	movdqu	%xmm2, 32(%rax,%rcx)
	movdqu	%xmm1, 16(%rax,%rcx)
	movdqu	%xmm0, (%rax,%rcx)
	incq	%r12
	movq	%r12, 672(%rbp)
	movq	%r15, %rax
.LBB12_149:
	cmpq	$6, %rax
	je	.LBB12_153
	leaq	1(%rax), %r15
	movq	%r15, 408(%rbp)
	movl	424(%rbp,%rax,4), %r12d
	movl	%r12d, 152(%rbp)
	leaq	152(%rbp), %rax
	movq	%rax, 616(%rbp)
	leaq	_RNvXsu_NtNtCs8xEFJqa6dYS_4core3fmt3nummNtB7_8LowerHex3fmt(%rip), %rax
	movq	%rax, 624(%rbp)
.Ltmp54:
	movq	%rdi, %rcx
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.24(%rip), %rdx
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
	je	.LBB12_152
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
	movq	672(%rbp), %r12
	cmpq	656(%rbp), %r12
	jne	.LBB12_216
.Ltmp56:
	leaq	656(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	nop
.Ltmp57:
	jmp	.LBB12_216
.LBB12_153:
	movl	$40, %r8d
	xorl	%edx, %edx
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	je	.LBB12_154
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
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.21(%rip), %rdx
	leaq	656(%rbp), %rcx
	leaq	480(%rbp), %r9
	movl	$19, %r8d
	callq	_RINvCs2i4to50FHNk_9prototype3addReEB2_
	nop
.Ltmp61:
	movq	$65537, 424(%rbp)
	movq	$131071, 432(%rbp)
	xorl	%ebx, %ebx
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.23(%rip), %r12
	leaq	480(%rbp), %rcx
	leaq	616(%rbp), %rdi
	movabsq	$13520701739831091, %r14
	movss	__real@3d000000(%rip), %xmm9
	xorl	%r15d, %r15d
	cmpq	$2, %r15
	je	.LBB12_165
.LBB12_158:
	movq	%r15, %r13
	movq	424(%rbp,%r15,8), %rax
	movq	%rax, 152(%rbp)
	leaq	152(%rbp), %rax
	movq	%rax, 616(%rbp)
	leaq	_RNvXsi_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impjNtB9_7Display3fmt(%rip), %rax
	movq	%rax, 624(%rbp)
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
	movq	152(%rbp), %rsi
	leaq	(,%rsi,4), %r15
	movq	%rsi, %rax
	shrq	$62, %rax
	setne	%al
	movabsq	$9223372036854775804, %rcx
	cmpq	%rcx, %r15
	seta	%cl
	orb	%al, %cl
	jne	.LBB12_200
	movq	496(%rbp), %r9
	testq	%r15, %r15
	je	.LBB12_161
	xorl	%edx, %edx
	movq	%r15, %r8
	movq	%r9, %rbx
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rbx, %r9
	xorl	%ebx, %ebx
	movq	%rax, %rcx
	movq	%rsi, %r10
	testq	%rax, %rax
	je	.LBB12_199
	testq	%rsi, %rsi
	movq	%r13, %r15
	jne	.LBB12_163
	jmp	.LBB12_206
.LBB12_161:
	movl	$4, %ecx
	xorl	%r10d, %r10d
	testq	%rsi, %rsi
	movq	%r13, %r15
	je	.LBB12_206
.LBB12_163:
	cmpq	$1, %rsi
	jne	.LBB12_201
	xorl	%r8d, %r8d
	jmp	.LBB12_205
.LBB12_201:
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
.LBB12_202:
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
	jne	.LBB12_202
	testb	$1, %sil
	leaq	616(%rbp), %rdi
	movl	$0, %ebx
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.23(%rip), %r12
	movq	%r13, %r15
	movq	696(%rbp), %r9
	movq	728(%rbp), %r10
	je	.LBB12_206
	negq	%r8
.LBB12_205:
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
.LBB12_206:
	movq	736(%rbp), %rax
	movq	%rax, 480(%rbp)
	movq	712(%rbp), %rax
	movq	%rax, 488(%rbp)
	movq	%r9, 496(%rbp)
	movq	%r10, 504(%rbp)
	movq	%rcx, 512(%rbp)
	movq	%rsi, 520(%rbp)
	movq	672(%rbp), %rsi
	cmpq	656(%rbp), %rsi
	jne	.LBB12_208
.Ltmp64:
	leaq	656(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	nop
.Ltmp65:
.LBB12_208:
	incq	%r15
	movq	664(%rbp), %rax
	leaq	(%rsi,%rsi,2), %rcx
	shlq	$4, %rcx
	movups	480(%rbp), %xmm0
	movdqu	496(%rbp), %xmm1
	movdqu	512(%rbp), %xmm2
	movdqu	%xmm2, 32(%rax,%rcx)
	movdqu	%xmm1, 16(%rax,%rcx)
	movups	%xmm0, (%rax,%rcx)
	incq	%rsi
	movq	%rsi, 672(%rbp)
	leaq	480(%rbp), %rcx
	cmpq	$2, %r15
	jne	.LBB12_158
.LBB12_165:
	movabsq	$6840158756896436237, %rbx
	leaq	656(%rbp), %r12
	movabsq	$-7046029254386353131, %r13
	movabsq	$-4658895280553007687, %rcx
	movabsq	$-7723592293110705685, %rdx
	leaq	.LJTI12_0(%rip), %r14
	movss	__real@3a800000(%rip), %xmm9
	movss	__real@ba800000(%rip), %xmm10
	xorl	%r15d, %r15d
	cmpq	$2047, %r15
	ja	.LBB12_243
.LBB12_167:
	movq	%r15, 152(%rbp)
	testb	$1, %r15b
	jne	.LBB12_168
	imull	$18079, %r15d, %eax
	shrl	$19, %eax
	leal	(%rax,%rax,8), %ecx
	leal	(%rcx,%rcx,2), %ecx
	addl	%eax, %eax
	addl	%ecx, %eax
	movl	%r15d, %ecx
	subl	%eax, %ecx
	movzwl	%cx, %eax
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.15(%rip), %rcx
	movq	(%rcx,%rax,8), %rdi
	jmp	.LBB12_170
.LBB12_168:
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
.LBB12_170:
	movl	%r15d, %eax
	andl	$7, %eax
	movq	%rax, 616(%rbp)
	leaq	(,%rdi,4), %rsi
	movq	%rdi, %rax
	shrq	$62, %rax
	setne	%al
	movabsq	$9223372036854775804, %rcx
	cmpq	%rcx, %rsi
	seta	%cl
	orb	%al, %cl
	jne	.LBB12_171
	testq	%rsi, %rsi
	je	.LBB12_173
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rdi, 712(%rbp)
	movq	%rax, 736(%rbp)
	testq	%rax, %rax
	jne	.LBB12_174
	jmp	.LBB12_179
.LBB12_173:
	movl	$4, %eax
	movq	%rax, 736(%rbp)
	movq	$0, 712(%rbp)
.LBB12_174:
	testq	%rdi, %rdi
	je	.LBB12_189
	movq	%rbx, %rdx
	xorl	%eax, %eax
	movabsq	$-4658895280553007687, %r11
	movabsq	$-7723592293110705685, %rsi
	jmp	.LBB12_176
.LBB12_187:
	movl	%ecx, %edx
	imulq	$954437177, %rdx, %rdx
	shrq	$34, %rdx
	addl	%edx, %edx
	leal	(%rdx,%rdx,8), %edx
	subl	%edx, %ecx
	movl	192(%rbp,%rcx,4), %ecx
.LBB12_188:
	movq	736(%rbp), %rdx
	movl	%ecx, (%rdx,%rax,4)
	incq	%rax
	movq	%rbx, %rdx
	cmpq	%rax, %rdi
	je	.LBB12_189
.LBB12_176:
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
	movq	616(%rbp), %r8
	cmpq	$6, %r8
	ja	.LBB12_181
	movslq	(%r14,%r8,4), %r8
	addq	%r14, %r8
	jmpq	*%r8
.LBB12_182:
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
	jmp	.LBB12_188
.LBB12_183:
	andl	$-2143289345, %ecx
	jmp	.LBB12_188
.LBB12_184:
	andl	$-2139095041, %ecx
	orl	$2130706432, %ecx
	jmp	.LBB12_188
.LBB12_181:
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
	jmp	.LBB12_188
.LBB12_185:
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
	jmp	.LBB12_188
.LBB12_186:
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
	jmp	.LBB12_188
.LBB12_189:
	leaq	152(%rbp), %rax
	movq	%rax, 480(%rbp)
	leaq	_RNvXsi_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impjNtB9_7Display3fmt(%rip), %rax
	movq	%rax, 488(%rbp)
	leaq	616(%rbp), %rcx
	movq	%rcx, 496(%rbp)
	movq	%rax, 504(%rbp)
	movb	$1, 683(%rbp)
.Ltmp146:
	leaq	408(%rbp), %rcx
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.22(%rip), %rdx
	leaq	480(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp147:
	movq	424(%rbp), %rax
	movq	%rax, 496(%rbp)
	movups	408(%rbp), %xmm0
	movaps	%xmm0, 480(%rbp)
	movq	712(%rbp), %rax
	movq	%rax, 504(%rbp)
	movq	736(%rbp), %rax
	movq	%rax, 512(%rbp)
	movq	%rdi, 520(%rbp)
	movq	672(%rbp), %rsi
	cmpq	656(%rbp), %rsi
	jne	.LBB12_192
.Ltmp148:
	movq	%r12, %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	nop
.Ltmp149:
.LBB12_192:
	incq	%r15
	movq	664(%rbp), %rax
	leaq	(%rsi,%rsi,2), %rcx
	shlq	$4, %rcx
	movaps	480(%rbp), %xmm0
	movdqa	496(%rbp), %xmm1
	movdqa	512(%rbp), %xmm2
	movdqu	%xmm2, 32(%rax,%rcx)
	movdqu	%xmm1, 16(%rax,%rcx)
	movups	%xmm0, (%rax,%rcx)
	incq	%rsi
	movq	%rsi, 672(%rbp)
	movabsq	$-4658895280553007687, %rcx
	movabsq	$-7723592293110705685, %rdx
	cmpq	$2047, %r15
	jbe	.LBB12_167
.LBB12_243:
	movq	672(%rbp), %r13
	movq	%r13, 400(%rbp)
	movups	656(%rbp), %xmm0
	movaps	%xmm0, 384(%rbp)
	movq	%r13, -40(%rbp)
	movaps	%xmm7, 480(%rbp)
	movaps	__xmm@ff7fffff7f7fffff00800000007fffff(%rip), %xmm0
	movaps	%xmm0, 496(%rbp)
	movaps	__xmm@7f8000017fc01234ff8000007f800000(%rip), %xmm0
	movaps	%xmm0, 512(%rbp)
	xorl	%edx, %edx
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.46(%rip), %r14
	leaq	192(%rbp), %r12
	xorl	%r8d, %r8d
	xorl	%eax, %eax
	movabsq	$-6148914691236517205, %r15
	testb	$1, %r8b
	jne	.LBB12_246
.LBB12_245:
	cmpq	$21, %rax
	jae	.LBB12_246
	leaq	1(%rax), %r9
	cmpq	$20, %rax
	sete	%r8b
	cmoveq	%rax, %r9
	movq	%rax, 456(%rbp)
	xorl	%edi, %edi
	cmpq	%rax, %rdi
	jae	.LBB12_413
.LBB12_414:
	movq	%rdi, 408(%rbp)
	incq	%rdi
	xorl	%r10d, %r10d
	cmpq	$48, %r10
	je	.LBB12_753
.LBB12_416:
	movl	480(%rbp,%r10), %eax
	movl	%eax, 616(%rbp)
	movq	456(%rbp), %rbx
	leaq	(,%rbx,4), %rsi
	movq	%rbx, %rax
	shrq	$62, %rax
	setne	%al
	movabsq	$9223372036854775804, %rcx
	cmpq	%rcx, %rsi
	seta	%cl
	orb	%al, %cl
	jne	.LBB12_428
	movq	%r10, 688(%rbp)
	movq	%r9, 728(%rbp)
	movq	%r8, 696(%rbp)
	xorl	%r13d, %r13d
	testq	%rsi, %rsi
	je	.LBB12_418
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rbx, 736(%rbp)
	testq	%rax, %rax
	jne	.LBB12_419
	jmp	.LBB12_427
.LBB12_418:
	movl	$4, %eax
	movq	$0, 736(%rbp)
.LBB12_419:
	cmpq	$2, %rbx
	jb	.LBB12_429
	movl	$1, %ecx
	movq	%rax, %r10
	cmpq	$9, %rbx
	jb	.LBB12_424
	leaq	-1(%rbx), %rdx
	movq	%rdx, %r8
	andq	$-8, %r8
	leaq	(%rax,%r8,4), %r10
	leaq	1(%r8), %rcx
	xorl	%r9d, %r9d
.LBB12_422:
	movups	%xmm6, (%rax,%r9,4)
	movups	%xmm6, 16(%rax,%r9,4)
	addq	$8, %r9
	cmpq	%r9, %r8
	jne	.LBB12_422
	cmpq	%r8, %rdx
	je	.LBB12_430
.LBB12_424:
	movq	%rbx, %rdx
	subq	%rcx, %rdx
.LBB12_425:
	movl	$-2147483648, (%r10)
	addq	$4, %r10
	decq	%rdx
	jne	.LBB12_425
	jmp	.LBB12_430
.LBB12_429:
	movq	%rax, %r10
	testq	%rbx, %rbx
	je	.LBB12_431
.LBB12_430:
	movl	$-2147483648, (%r10)
.LBB12_431:
	movq	408(%rbp), %rcx
	cmpq	%rbx, %rcx
	movq	%rax, 712(%rbp)
	jae	.LBB12_441
	movss	616(%rbp), %xmm7
	movss	%xmm7, (%rax,%rcx,4)
	leaq	456(%rbp), %rax
	movq	%rax, 192(%rbp)
	leaq	_RNvXsi_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impjNtB9_7Display3fmt(%rip), %rax
	movq	%rax, 200(%rbp)
	leaq	408(%rbp), %rcx
	movq	%rcx, 208(%rbp)
	movq	%rax, 216(%rbp)
	leaq	616(%rbp), %rax
	movq	%rax, 224(%rbp)
	leaq	_RNvXsu_NtNtCs8xEFJqa6dYS_4core3fmt3nummNtB7_8LowerHex3fmt(%rip), %rax
	movq	%rax, 232(%rbp)
	movb	$1, 727(%rbp)
.Ltmp70:
	leaq	-64(%rbp), %rcx
	movq	%r14, %rdx
	movq	%r12, %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp71:
	movups	-64(%rbp), %xmm0
	movaps	%xmm0, 192(%rbp)
	movq	-48(%rbp), %rax
	movq	%rax, 208(%rbp)
	movq	736(%rbp), %rax
	movq	%rax, 216(%rbp)
	movq	712(%rbp), %rax
	movq	%rax, 224(%rbp)
	movq	%rbx, 232(%rbp)
	movq	400(%rbp), %r12
	cmpq	384(%rbp), %r12
	jne	.LBB12_435
.Ltmp72:
	leaq	384(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	nop
.Ltmp73:
.LBB12_435:
	movq	392(%rbp), %rsi
	leaq	(%r12,%r12,2), %rax
	shlq	$4, %rax
	movaps	192(%rbp), %xmm0
	movaps	208(%rbp), %xmm1
	movdqa	224(%rbp), %xmm2
	movdqu	%xmm2, 32(%rsi,%rax)
	movups	%xmm1, 16(%rsi,%rax)
	movups	%xmm0, (%rsi,%rax)
	leaq	1(%r12), %rdx
	movq	%rdx, 400(%rbp)
	movq	456(%rbp), %rbx
	leaq	(,%rbx,4), %r14
	movq	%rbx, %rax
	shrq	$62, %rax
	setne	%al
	movabsq	$9223372036854775804, %rcx
	cmpq	%rcx, %r14
	seta	%cl
	orb	%al, %cl
	jne	.LBB12_445
	movq	%rdx, 648(%rbp)
	movq	%r12, 176(%rbp)
	testq	%r14, %r14
	je	.LBB12_437
	xorl	%edx, %edx
	movq	%r14, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rbx, 608(%rbp)
	movq	%rax, 640(%rbp)
	testq	%rax, %rax
	jne	.LBB12_438
	jmp	.LBB12_444
.LBB12_437:
	movl	$4, %eax
	movq	%rax, 640(%rbp)
	movq	$0, 608(%rbp)
.LBB12_438:
	testq	%rbx, %rbx
	je	.LBB12_451
	cmpq	$1, %rbx
	jne	.LBB12_446
	xorl	%ecx, %ecx
	jmp	.LBB12_450
.LBB12_446:
	movq	640(%rbp), %rax
	leaq	4(%rax), %r10
	movq	%rbx, %r11
	movabsq	$4611686018427387902, %rax
	andq	%rax, %r11
	negq	%r11
	movq	$-1, %r13
	movl	$1, %r8d
	xorl	%ecx, %ecx
	xorl	%r9d, %r9d
.LBB12_447:
	movq	%r9, %rax
	mulq	%r15
	shrq	%rdx
	leaq	(%rdx,%rdx,2), %r12
	movq	%r13, %r14
	movq	%r8, %rax
	mulq	%r15
	subq	%r12, %r14
	shrq	%rdx
	leaq	(%rdx,%rdx,2), %rax
	movq	%r9, %rdx
	xorps	%xmm0, %xmm0
	cvtsi2ss	%r14, %xmm0
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
	jne	.LBB12_447
	testb	$1, %bl
	je	.LBB12_451
	negq	%rcx
.LBB12_450:
	movq	%rcx, %rax
	movabsq	$-6148914691236517205, %rdx
	mulq	%rdx
	shrq	%rdx
	leal	(%rdx,%rdx,2), %eax
	notl	%eax
	addl	%ecx, %eax
	xorps	%xmm0, %xmm0
	cvtsi2ss	%eax, %xmm0
	movq	640(%rbp), %rax
	movss	%xmm0, (%rax,%rcx,4)
.LBB12_451:
	movq	408(%rbp), %rcx
	cmpq	%rbx, %rcx
	jae	.LBB12_457
	movq	640(%rbp), %r14
	movss	%xmm7, (%r14,%rcx,4)
	leaq	456(%rbp), %rax
	movq	%rax, 192(%rbp)
	leaq	_RNvXsi_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impjNtB9_7Display3fmt(%rip), %rax
	movq	%rax, 200(%rbp)
	leaq	408(%rbp), %rcx
	movq	%rcx, 208(%rbp)
	movq	%rax, 216(%rbp)
	leaq	616(%rbp), %rax
	movq	%rax, 224(%rbp)
	leaq	_RNvXsu_NtNtCs8xEFJqa6dYS_4core3fmt3nummNtB7_8LowerHex3fmt(%rip), %rax
	movq	%rax, 232(%rbp)
	movb	$1, 711(%rbp)
.Ltmp76:
	leaq	-88(%rbp), %rcx
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.48(%rip), %rdx
	leaq	192(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp77:
	movups	-88(%rbp), %xmm0
	movaps	%xmm0, 192(%rbp)
	movq	-72(%rbp), %rax
	movq	%rax, 208(%rbp)
	movq	608(%rbp), %rax
	movq	%rax, 216(%rbp)
	movq	%r14, 224(%rbp)
	movq	%rbx, 232(%rbp)
	movq	648(%rbp), %rax
	cmpq	384(%rbp), %rax
	jne	.LBB12_456
.Ltmp78:
	leaq	384(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	nop
.Ltmp79:
	movq	392(%rbp), %rsi
	movq	648(%rbp), %rax
.LBB12_456:
	movq	688(%rbp), %r10
	addq	$4, %r10
	leaq	(%rax,%rax,2), %rax
	shlq	$4, %rax
	movaps	192(%rbp), %xmm0
	movdqa	208(%rbp), %xmm1
	movdqa	224(%rbp), %xmm2
	movdqu	%xmm2, 32(%rsi,%rax)
	movdqu	%xmm1, 16(%rsi,%rax)
	movups	%xmm0, (%rsi,%rax)
	movq	176(%rbp), %r13
	addq	$2, %r13
	movq	%r13, 400(%rbp)
	xorl	%edx, %edx
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.46(%rip), %r14
	leaq	192(%rbp), %r12
	movq	696(%rbp), %r8
	movq	728(%rbp), %r9
	cmpq	$48, %r10
	jne	.LBB12_416
.LBB12_753:
	movq	456(%rbp), %rax
	cmpq	%rax, %rdi
	jb	.LBB12_414
.LBB12_413:
	movq	%r9, %rax
	testb	$1, %r8b
	je	.LBB12_245
.LBB12_246:
	movabsq	$6840158756896383001, %r15
	xorl	%esi, %esi
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.44(%rip), %rdi
	leaq	192(%rbp), %rbx
	movaps	__xmm@daa66d2c7ddf743f3c6ef372fe94f82a(%rip), %xmm6
	movaps	__xmm@9e3779b97f4a7c150000000000000000(%rip), %xmm7
	movaps	__xmm@9e3779b97f4a7c159e3779b97f4a7c15(%rip), %xmm8
	movdqa	__xmm@00000000bf58476d00000000bf58476d(%rip), %xmm9
	movdqa	__xmm@bf58476d1ce4e5b9bf58476d1ce4e5b9(%rip), %xmm10
	movdqa	__xmm@0000000094d049bb0000000094d049bb(%rip), %xmm11
	movdqa	__xmm@94d049bb133111eb94d049bb133111eb(%rip), %xmm12
	movdqa	__xmm@78dde6e5fd29f05478dde6e5fd29f054(%rip), %xmm13
	jmp	.LBB12_247
.LBB12_41:
.Ltmp12:
	movl	$4, %ecx
	movl	$4, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp13:
	jmp	.LBB12_42
.LBB12_171:
	xorl	%ecx, %ecx
.LBB12_180:
.Ltmp150:
	movq	%rsi, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp151:
	jmp	.LBB12_42
.LBB12_28:
.Ltmp42:
	movl	$4, %ecx
	movl	$16, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp43:
	jmp	.LBB12_42
.LBB12_147:
.Ltmp52:
	movl	$4, %ecx
	movl	$4, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp53:
	jmp	.LBB12_42
.LBB12_152:
.Ltmp58:
	movl	$4, %ecx
	movl	$32, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp59:
	jmp	.LBB12_42
.LBB12_1:
	callq	_RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache21detect_and_initialize
	testl	$1024, %eax
	jne	.LBB12_3
.LBB12_740:
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.10(%rip), %rcx
	movl	$133, %edx
	callq	_RNvNtNtCse0R8cuyqEa_3std2io5stdio6__print
	movl	$3, %ecx
	callq	_RNvNtCse0R8cuyqEa_3std7process4exit
	ud2
.LBB12_394:
	incq	%rsi
	movq	392(%rbp), %rax
	leaq	(,%r13,2), %rcx
	addq	%r13, %rcx
	shlq	$4, %rcx
	movaps	192(%rbp), %xmm0
	movdqa	208(%rbp), %xmm1
	movdqa	224(%rbp), %xmm2
	movdqu	%xmm2, 32(%rax,%rcx)
	movdqu	%xmm1, 16(%rax,%rcx)
	movups	%xmm0, (%rax,%rcx)
	incq	%r13
	movq	%r13, 400(%rbp)
.LBB12_247:
	cmpq	$4096, %rsi
	jae	.LBB12_248
	movq	%rsi, 408(%rbp)
	cmpq	$128, %rsi
	jae	.LBB12_388
	movq	%rsi, %r12
	jmp	.LBB12_389
.LBB12_388:
	movabsq	$-7046029254386353131, %rax
	addq	%rax, %r15
	movq	%r15, %rax
	shrq	$30, %rax
	xorq	%r15, %rax
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
.LBB12_389:
	testq	%r12, %r12
	movq	%r12, 712(%rbp)
	je	.LBB12_390
	leaq	(,%r12,4), %r14
	xorl	%edx, %edx
	movq	%r14, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rax, 736(%rbp)
	testq	%rax, %rax
	je	.LBB12_404
	cmpq	$4, %r12
	jae	.LBB12_400
	movq	%r15, %rcx
	xorl	%eax, %eax
	jmp	.LBB12_398
.LBB12_390:
	movl	$4, %eax
	movq	%rax, 736(%rbp)
	jmp	.LBB12_391
.LBB12_400:
	movl	%r12d, %eax
	andl	$2147483644, %eax
	movq	%rax, %rcx
	movabsq	$-7046029254386353131, %rdx
	imulq	%rdx, %rcx
	addq	%r15, %rcx
	movq	%r15, %xmm0
	pshufd	$68, %xmm0, %xmm0
	movdqa	%xmm0, %xmm1
	paddq	%xmm6, %xmm1
	paddq	%xmm7, %xmm0
	andq	$-16, %r14
	xorl	%edx, %edx
	movq	736(%rbp), %r8
.LBB12_401:
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
	jne	.LBB12_401
	cmpq	%rax, %r12
	jne	.LBB12_398
	movq	%rcx, %r15
	jmp	.LBB12_391
.LBB12_398:
	movq	%rcx, %r15
	movabsq	$-7046029254386353131, %r8
	movabsq	$-4658895280553007687, %r9
	movabsq	$-7723592293110705685, %r10
	movq	736(%rbp), %r11
.LBB12_399:
	addq	%r8, %r15
	movq	%r15, %rcx
	shrq	$30, %rcx
	xorq	%r15, %rcx
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
	jne	.LBB12_399
.LBB12_391:
	leaq	408(%rbp), %rax
	movq	%rax, 192(%rbp)
	leaq	_RNvXsi_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impjNtB9_7Display3fmt(%rip), %rax
	movq	%rax, 200(%rbp)
	movb	$1, 681(%rbp)
.Ltmp142:
	leaq	64(%rbp), %rcx
	movq	%rdi, %rdx
	movq	%rbx, %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp143:
	movups	64(%rbp), %xmm0
	movaps	%xmm0, 192(%rbp)
	movq	80(%rbp), %rax
	movq	%rax, 208(%rbp)
	movq	712(%rbp), %rax
	movq	%rax, 216(%rbp)
	movq	736(%rbp), %rcx
	movq	%rcx, 224(%rbp)
	movq	%rax, 232(%rbp)
	cmpq	384(%rbp), %r13
	jne	.LBB12_394
.Ltmp144:
	leaq	384(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtCs2i4to50FHNk_9prototype4CaseE8grow_oneBO_
	nop
.Ltmp145:
	jmp	.LBB12_394
.LBB12_154:
.Ltmp152:
	movl	$4, %ecx
	movl	$40, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp153:
	jmp	.LBB12_42
.LBB12_248:
	movabsq	$-3750763034362895579, %rax
	movq	%rax, 120(%rbp)
	movq	%rax, 112(%rbp)
	movq	%rax, 104(%rbp)
	movq	$0, 96(%rbp)
	movq	$0, 376(%rbp)
	movq	392(%rbp), %rax
	movq	%r13, 176(%rbp)
	leaq	(,%r13,2), %rcx
	addq	%r13, %rcx
	shlq	$4, %rcx
	addq	%rax, %rcx
	movq	%rcx, 32(%rbp)
	movq	$0, 48(%rbp)
	movabsq	$1099511628211, %rdi
	movaps	__xmm@a55aa55aa55aa55aa55aa55aa55aa55a(%rip), %xmm9
	movq	%rax, 56(%rbp)
	movq	%rax, %rcx
	jmp	.LBB12_249
.LBB12_384:
	movq	%r12, %rcx
.LBB12_249:
	cmpq	32(%rbp), %rcx
	je	.LBB12_250
	movq	40(%rcx), %rax
	movq	%rax, 736(%rbp)
	addq	%rax, 96(%rbp)
	movq	%rcx, 712(%rbp)
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
	xorq	104(%rbp), %rsi
	imulq	%rdi, %rsi
	movzbl	%ch, %ebx
	xorq	%rsi, %rbx
	imulq	%rdi, %rbx
	movzbl	%r11b, %r11d
	xorq	%rbx, %r11
	imulq	%rdi, %r11
	xorq	%r10, %r11
	imulq	%rdi, %r11
	movzbl	%r9b, %r9d
	xorq	%r11, %r9
	imulq	%rdi, %r9
	movzbl	%r8b, %r8d
	xorq	%r9, %r8
	imulq	%rdi, %r8
	movzbl	%dl, %r9d
	xorq	%r8, %r9
	imulq	%rdi, %r9
	xorq	%rax, %r9
	imulq	%rdi, %r9
	testq	%rcx, %rcx
	je	.LBB12_278
	movq	712(%rbp), %rax
	movq	8(%rax), %rdx
	movq	%rcx, %r10
	movq	%rdx, %r8
	andq	$7, %r10
	je	.LBB12_280
.LBB12_281:
	movzbl	(%r8), %eax
	incq	%r8
	xorq	%r9, %rax
	imulq	%rdi, %rax
	movq	%rax, %r9
	decq	%r10
	jne	.LBB12_281
	jmp	.LBB12_282
.LBB12_278:
	movq	%r9, %rax
	jmp	.LBB12_285
.LBB12_280:
	movq	%r9, %rax
.LBB12_282:
	cmpq	$8, %rcx
	jb	.LBB12_285
	addq	%rcx, %rdx
.LBB12_284:
	movzbl	(%r8), %ecx
	xorq	%rax, %rcx
	imulq	%rdi, %rcx
	movzbl	1(%r8), %eax
	xorq	%rcx, %rax
	imulq	%rdi, %rax
	movzbl	2(%r8), %ecx
	xorq	%rax, %rcx
	imulq	%rdi, %rcx
	movzbl	3(%r8), %eax
	xorq	%rcx, %rax
	imulq	%rdi, %rax
	movzbl	4(%r8), %ecx
	xorq	%rax, %rcx
	imulq	%rdi, %rcx
	movzbl	5(%r8), %eax
	xorq	%rcx, %rax
	imulq	%rdi, %rax
	movzbl	6(%r8), %ecx
	xorq	%rax, %rcx
	imulq	%rdi, %rcx
	movzbl	7(%r8), %eax
	addq	$8, %r8
	xorq	%rcx, %rax
	imulq	%rdi, %rax
	cmpq	%rdx, %r8
	jne	.LBB12_284
.LBB12_285:
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
	imulq	%rdi, %rax
	movzbl	%bh, %esi
	xorq	%rsi, %rax
	movq	%rsi, %r15
	imulq	%rdi, %rax
	movzbl	%r9b, %r9d
	xorq	%r9, %rax
	imulq	%rdi, %rax
	xorq	%r11, %rax
	imulq	%rdi, %rax
	movzbl	%r8b, %r8d
	xorq	%r8, %rax
	imulq	%rdi, %rax
	movzbl	%dl, %edx
	xorq	%rdx, %rax
	imulq	%rdi, %rax
	movzbl	%cl, %ecx
	xorq	%rcx, %rax
	imulq	%rdi, %rax
	xorq	%r10, %rax
	imulq	%rdi, %rax
	movq	%rax, 104(%rbp)
	movq	120(%rbp), %rsi
	xorq	%r14, %rsi
	imulq	%rdi, %rsi
	movq	%r15, -16(%rbp)
	xorq	%r15, %rsi
	imulq	%rdi, %rsi
	movq	%r9, -8(%rbp)
	xorq	%r9, %rsi
	imulq	%rdi, %rsi
	movq	%r11, -24(%rbp)
	xorq	%r11, %rsi
	imulq	%rdi, %rsi
	movq	%r8, (%rbp)
	xorq	%r8, %rsi
	imulq	%rdi, %rsi
	movq	%rdx, 8(%rbp)
	xorq	%rdx, %rsi
	imulq	%rdi, %rsi
	movq	%rcx, 16(%rbp)
	xorq	%rcx, %rsi
	imulq	%rdi, %rsi
	movq	%r10, -32(%rbp)
	xorq	%r10, %rsi
	imulq	%rdi, %rsi
	movq	%rsi, 120(%rbp)
	testq	%rbx, %rbx
	je	.LBB12_286
	movq	712(%rbp), %rax
	movq	32(%rax), %rbx
	movq	736(%rbp), %rax
	leaq	(,%rax,4), %r8
	xorl	%edx, %edx
	movq	%r8, 128(%rbp)
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rax, 608(%rbp)
	testq	%rax, %rax
	je	.LBB12_310
	cmpq	$8, 736(%rbp)
	setb	%al
	movq	608(%rbp), %rcx
	subq	%rbx, %rcx
	cmpq	$32, %rcx
	setb	%cl
	orb	%al, %cl
	je	.LBB12_290
	xorl	%eax, %eax
	movq	736(%rbp), %rdx
	movq	608(%rbp), %r9
	jmp	.LBB12_293
.LBB12_286:
	movq	$0, 656(%rbp)
	movq	$4, 664(%rbp)
	movq	$0, 672(%rbp)
	movl	$4, %eax
	movq	%rax, 608(%rbp)
	movq	$0, 128(%rbp)
	jmp	.LBB12_301
.LBB12_290:
	movq	736(%rbp), %rcx
	movq	%rcx, %rax
	movabsq	$2305843009213693944, %rdx
	andq	%rdx, %rax
	leaq	(,%rcx,4), %rcx
	andq	$-32, %rcx
	xorl	%edx, %edx
	movq	608(%rbp), %r9
.LBB12_291:
	movups	(%rbx,%rdx), %xmm0
	movdqu	16(%rbx,%rdx), %xmm1
	movups	%xmm0, (%r9,%rdx)
	movdqu	%xmm1, 16(%r9,%rdx)
	addq	$32, %rdx
	cmpq	%rdx, %rcx
	jne	.LBB12_291
	movq	736(%rbp), %rdx
	cmpq	%rax, %rdx
	je	.LBB12_298
.LBB12_293:
	movq	%rax, %rcx
	andq	$3, %rdx
	je	.LBB12_296
	movq	%rax, %rcx
.LBB12_295:
	movl	(%rbx,%rcx,4), %r8d
	movl	%r8d, (%r9,%rcx,4)
	incq	%rcx
	decq	%rdx
	jne	.LBB12_295
.LBB12_296:
	movq	736(%rbp), %rdx
	subq	%rdx, %rax
	cmpq	$-4, %rax
	ja	.LBB12_298
.LBB12_297:
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
	jne	.LBB12_297
.LBB12_298:
	movq	%rdx, 656(%rbp)
	movq	%r9, 664(%rbp)
	movq	%rdx, 672(%rbp)
	xorl	%eax, %eax
	movq	128(%rbp), %r10
.LBB12_299:
	movl	(%r9,%rax), %edx
	movl	%edx, %ecx
	movzbl	%dl, %r8d
	movzbl	%dh, %ebx
	shrl	$16, %edx
	shrl	$24, %ecx
	xorq	%rsi, %r8
	imulq	%rdi, %r8
	xorq	%r8, %rbx
	imulq	%rdi, %rbx
	movzbl	%dl, %esi
	xorq	%rbx, %rsi
	imulq	%rdi, %rsi
	xorq	%rcx, %rsi
	imulq	%rdi, %rsi
	addq	$4, %rax
	cmpq	%rax, %r10
	jne	.LBB12_299
	movq	%rsi, 120(%rbp)
.LBB12_301:
	movq	736(%rbp), %rbx
	leaq	12(,%rbx,2), %r8
	xorl	%edx, %edx
	movq	%r8, %r13
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	je	.LBB12_311
	movq	%rax, %r10
	leaq	5(%rbx), %rsi
	movl	$1, %ecx
	cmpq	$11, %rbx
	jb	.LBB12_306
	movq	%rsi, %rdx
	movabsq	$4611686018427387888, %rax
	andq	%rax, %rdx
	leaq	(%r10,%rdx,2), %rax
	leaq	1(%rdx), %rcx
	leaq	(%rsi,%rsi), %r8
	andq	$-32, %r8
	xorl	%r9d, %r9d
.LBB12_304:
	movups	%xmm9, (%r10,%r9)
	movups	%xmm9, 16(%r10,%r9)
	addq	$32, %r9
	cmpq	%r9, %r8
	jne	.LBB12_304
	cmpq	%rdx, %rsi
	je	.LBB12_308
.LBB12_306:
	movq	736(%rbp), %rdx
	subq	%rcx, %rdx
	addq	$6, %rdx
.LBB12_307:
	movw	$-23206, (%rax)
	addq	$2, %rax
	decq	%rdx
	jne	.LBB12_307
.LBB12_308:
	movq	736(%rbp), %rcx
	leaq	6(%rcx), %r15
	movw	$-23206, (%rax)
	movq	%r15, 152(%rbp)
	movq	%r10, 160(%rbp)
	movq	%r15, 168(%rbp)
	xorl	%edx, %edx
	movq	%r13, %r12
	movq	%r13, %r8
	movq	%r10, %rbx
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	movq	%rbx, 688(%rbp)
	je	.LBB12_309
	movq	%r15, 616(%rbp)
	movq	%rax, 624(%rbp)
	movq	%rax, 696(%rbp)
	movq	%rax, %rcx
	movq	%rbx, %rdx
	movq	%r12, %r8
	callq	memcpy
	movq	%r15, 632(%rbp)
	xorl	%edx, %edx
	movq	%r12, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	je	.LBB12_325
	movq	%rax, %rbx
	movl	$1, %ecx
	cmpq	$11, 736(%rbp)
	jb	.LBB12_321
	movq	%rsi, %rdx
	movabsq	$4611686018427387888, %rax
	andq	%rax, %rdx
	leaq	(%rbx,%rdx,2), %rax
	leaq	1(%rdx), %rcx
	leaq	(%rsi,%rsi), %r8
	andq	$-32, %r8
	xorl	%r9d, %r9d
.LBB12_319:
	movups	%xmm9, (%rbx,%r9)
	movups	%xmm9, 16(%rbx,%r9)
	addq	$32, %r9
	cmpq	%r9, %r8
	jne	.LBB12_319
	cmpq	%rdx, %rsi
	je	.LBB12_323
.LBB12_321:
	movq	736(%rbp), %rdx
	subq	%rcx, %rdx
	addq	$6, %rdx
.LBB12_322:
	movw	$-23206, (%rax)
	addq	$2, %rax
	decq	%rdx
	jne	.LBB12_322
.LBB12_323:
	movw	$-23206, (%rax)
	movq	%r15, 456(%rbp)
	movq	%rbx, 464(%rbp)
	movq	%r15, 472(%rbp)
	xorl	%edx, %edx
	movq	%r13, %rsi
	movq	%r13, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	movq	%rbx, 640(%rbp)
	je	.LBB12_324
	movq	%r15, 408(%rbp)
	movq	%rax, 416(%rbp)
	movq	%rax, 648(%rbp)
	movq	%rax, %rcx
	movq	%rbx, %rdx
	movq	%rsi, %r8
	callq	memcpy
	movq	%r15, 424(%rbp)
	movq	712(%rbp), %rsi
	movq	32(%rsi), %rcx
	movq	40(%rsi), %rdx
	movq	688(%rbp), %r8
	addq	$6, %r8
	movq	736(%rbp), %rbx
	movq	%rbx, %r9
	callq	d015_baseline_i16
	movaps	%xmm0, %xmm6
	movq	32(%rsi), %rcx
	movq	40(%rsi), %rdx
	movq	696(%rbp), %rax
	leaq	6(%rax), %rsi
.Ltmp86:
	movq	%rsi, %r8
	movq	%rbx, %r9
	callq	d015_candidate_i16
	nop
.Ltmp87:
	movaps	%xmm0, %xmm7
	movq	712(%rbp), %r12
	movq	32(%r12), %rcx
	movq	40(%r12), %rdx
	movq	640(%rbp), %r8
	addq	$6, %r8
	movq	736(%rbp), %rbx
	movq	%rbx, %r9
	callq	d015_baseline_u16
	movaps	%xmm0, %xmm8
	movq	32(%r12), %rcx
	movq	40(%r12), %rdx
	movq	648(%rbp), %rax
	leaq	6(%rax), %r8
.Ltmp88:
	movq	%rbx, %r9
	callq	d015_candidate_u16
	nop
.Ltmp89:
	cmpq	$-1, 184(%rbp)
	je	.LBB12_334
	movq	48(%rbp), %rax
	xorb	$1, %al
	testb	$1, %al
	je	.LBB12_334
	cmpq	$0, 736(%rbp)
	je	.LBB12_334
	xorb	$1, (%rsi)
	movb	$1, %al
	movq	%rax, 48(%rbp)
.LBB12_334:
	movss	%xmm7, 92(%rbp)
	movss	%xmm6, 136(%rbp)
	movd	%xmm7, %ebx
	movd	%xmm6, %eax
	cmpl	%eax, %ebx
	jne	.LBB12_335
	movss	%xmm0, 88(%rbp)
	movss	%xmm8, 136(%rbp)
	movd	%xmm0, %ecx
	movd	%xmm8, %eax
	movq	%rcx, 24(%rbp)
	cmpl	%eax, %ecx
	jne	.LBB12_338
	movq	696(%rbp), %rcx
	movq	688(%rbp), %rdx
	movq	%r13, %r12
	movq	%r13, %r8
	callq	memcmp
	testl	%eax, %eax
	jne	.LBB12_340
	movq	648(%rbp), %rsi
	movq	%rsi, %rcx
	movq	640(%rbp), %rdx
	movq	%r12, %r8
	callq	memcmp
	testl	%eax, %eax
	jne	.LBB12_752
	movq	712(%rbp), %rax
	leaq	48(%rax), %r12
	movq	736(%rbp), %rax
	leaq	3(%rax), %r8
	movb	$1, %cl
	movq	376(%rbp), %rax
	xorl	%edx, %edx
	movq	696(%rbp), %r11
.LBB12_343:
	movl	%ecx, %r9d
	cmpq	$3, %rdx
	setb	%cl
	andb	%r9b, %cl
	cmpb	$1, %cl
	jne	.LBB12_345
	leaq	1(%rdx), %r9
	movq	%r8, %r10
	jmp	.LBB12_347
.LBB12_345:
	cmpq	%r15, %r8
	jae	.LBB12_349
	leaq	1(%r8), %r10
	movq	%rdx, %r9
	movq	%r8, %rdx
.LBB12_347:
	movzwl	(%r11,%rdx,2), %r8d
	movw	%r8w, 136(%rbp)
	cmpl	$42330, %r8d
	jne	.LBB12_348
	cmpw	$-23206, (%rsi,%rdx,2)
	jne	.LBB12_387
	addq	$2, %rax
	movq	%r9, %rdx
	movq	%r10, %r8
	jmp	.LBB12_343
.LBB12_349:
	movq	%rax, 376(%rbp)
	movq	712(%rbp), %rax
	movq	40(%rax), %rcx
	movq	%rcx, 728(%rbp)
	testq	%rcx, %rcx
	je	.LBB12_350
	movq	712(%rbp), %rax
	movq	32(%rax), %r15
	movq	728(%rbp), %rax
	leaq	(,%rax,4), %rsi
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	je	.LBB12_366
	movq	%rax, %rdx
	cmpq	$8, 728(%rbp)
	setb	%al
	movq	%rdx, %rcx
	subq	%r15, %rcx
	cmpq	$32, %rcx
	setb	%cl
	orb	%al, %cl
	je	.LBB12_358
	xorl	%eax, %eax
	jmp	.LBB12_361
.LBB12_350:
	movl	$4, %edx
	jmp	.LBB12_351
.LBB12_358:
	movq	728(%rbp), %rax
	andq	$-8, %rax
	xorl	%ecx, %ecx
	movq	%rdx, %r8
.LBB12_359:
	movups	(%r15,%rcx,4), %xmm0
	movdqu	16(%r15,%rcx,4), %xmm1
	movups	%xmm0, (%r8,%rcx,4)
	movdqu	%xmm1, 16(%r8,%rcx,4)
	addq	$8, %rcx
	cmpq	%rcx, %rax
	jne	.LBB12_359
	cmpq	%rax, 728(%rbp)
	je	.LBB12_351
.LBB12_361:
	movq	728(%rbp), %r9
	movq	%rax, %rcx
	andq	$3, %r9
	je	.LBB12_364
	movq	%rax, %rcx
.LBB12_363:
	movl	(%r15,%rcx,4), %r8d
	movl	%r8d, (%rdx,%rcx,4)
	incq	%rcx
	decq	%r9
	jne	.LBB12_363
.LBB12_364:
	movq	728(%rbp), %r8
	subq	%r8, %rax
	cmpq	$-4, %rax
	ja	.LBB12_351
.LBB12_365:
	movl	(%r15,%rcx,4), %eax
	movl	%eax, (%rdx,%rcx,4)
	movl	4(%r15,%rcx,4), %eax
	movl	%eax, 4(%rdx,%rcx,4)
	movl	8(%r15,%rcx,4), %eax
	movl	%eax, 8(%rdx,%rcx,4)
	movl	12(%r15,%rcx,4), %eax
	movl	%eax, 12(%rdx,%rcx,4)
	addq	$4, %rcx
	cmpq	%rcx, %r8
	jne	.LBB12_365
.LBB12_351:
	movq	728(%rbp), %rax
	movq	%rax, 192(%rbp)
	movq	%rdx, 200(%rbp)
	movq	%rax, 208(%rbp)
	cmpq	%rax, 736(%rbp)
	jne	.LBB12_354
	movq	608(%rbp), %rcx
	movq	%rdx, %rsi
	movq	128(%rbp), %r8
	callq	memcmp
	testl	%eax, %eax
	jne	.LBB12_353
	cmpq	$0, 736(%rbp)
	je	.LBB12_369
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_369:
	xorq	112(%rbp), %r14
	imulq	%rdi, %r14
	xorq	-16(%rbp), %r14
	imulq	%rdi, %r14
	xorq	-8(%rbp), %r14
	imulq	%rdi, %r14
	xorq	-24(%rbp), %r14
	imulq	%rdi, %r14
	xorq	(%rbp), %r14
	imulq	%rdi, %r14
	xorq	8(%rbp), %r14
	imulq	%rdi, %r14
	xorq	16(%rbp), %r14
	imulq	%rdi, %r14
	xorq	-32(%rbp), %r14
	imulq	%rdi, %r14
	testb	$1, 736(%rbp)
	jne	.LBB12_374
	movq	696(%rbp), %rsi
	movq	%rsi, %rax
	jmp	.LBB12_375
.LBB12_374:
	movq	696(%rbp), %rsi
	movzwl	(%rsi), %eax
	movzbl	%al, %ecx
	shrl	$8, %eax
	xorq	%rcx, %r14
	imulq	%rdi, %r14
	xorq	%rax, %r14
	imulq	%rdi, %r14
	leaq	2(%rsi), %rax
.LBB12_375:
	movq	%rsi, %rcx
	addq	%r13, %rcx
.LBB12_376:
	movzwl	(%rax), %edx
	movzbl	%dl, %r8d
	shrl	$8, %edx
	xorq	%r14, %r8
	imulq	%rdi, %r8
	xorq	%rdx, %r8
	imulq	%rdi, %r8
	movzwl	2(%rax), %edx
	movzbl	%dl, %r14d
	shrl	$8, %edx
	xorq	%r8, %r14
	imulq	%rdi, %r14
	xorq	%rdx, %r14
	imulq	%rdi, %r14
	addq	$4, %rax
	cmpq	%rcx, %rax
	jne	.LBB12_376
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	movzbl	%bl, %eax
	xorq	%rax, %r14
	imulq	%rdi, %r14
	movzbl	%bh, %eax
	xorq	%r14, %rax
	imulq	%rdi, %rax
	movl	%ebx, %ecx
	shrl	$16, %ecx
	movzbl	%cl, %ecx
	xorq	%rax, %rcx
	imulq	%rdi, %rcx
	shrl	$24, %ebx
	xorq	%rcx, %rbx
	imulq	%rdi, %rbx
	testb	$1, 736(%rbp)
	jne	.LBB12_379
	movq	648(%rbp), %r14
	movq	%r14, %rax
	jmp	.LBB12_380
.LBB12_379:
	movq	648(%rbp), %r14
	movzwl	(%r14), %eax
	movzbl	%al, %ecx
	shrl	$8, %eax
	xorq	%rcx, %rbx
	imulq	%rdi, %rbx
	xorq	%rax, %rbx
	imulq	%rdi, %rbx
	leaq	2(%r14), %rax
.LBB12_380:
	movq	%r14, %rcx
	addq	%r13, %rcx
.LBB12_381:
	movzwl	(%rax), %edx
	movzbl	%dl, %r8d
	shrl	$8, %edx
	xorq	%rbx, %r8
	imulq	%rdi, %r8
	xorq	%rdx, %r8
	imulq	%rdi, %r8
	movzwl	2(%rax), %edx
	movzbl	%dl, %ebx
	shrl	$8, %edx
	xorq	%r8, %rbx
	imulq	%rdi, %rbx
	xorq	%rdx, %rbx
	imulq	%rdi, %rbx
	addq	$4, %rax
	cmpq	%rcx, %rax
	jne	.LBB12_381
	movq	__imp_GetProcessHeap(%rip), %rsi
	callq	*%rsi
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%r14, %r8
	movq	__imp_HeapFree(%rip), %r14
	callq	*%r14
	movq	24(%rbp), %rdx
	movzbl	%dl, %eax
	xorq	%rax, %rbx
	imulq	%rdi, %rbx
	movzbl	%dh, %eax
	xorq	%rbx, %rax
	imulq	%rdi, %rax
	movl	%edx, %ecx
	shrl	$16, %ecx
	movzbl	%cl, %ecx
	xorq	%rax, %rcx
	imulq	%rdi, %rcx
	shrl	$24, %edx
	xorq	%rcx, %rdx
	imulq	%rdi, %rdx
	movq	%rdx, 112(%rbp)
	callq	*%rsi
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	640(%rbp), %r8
	callq	*%r14
	callq	*%rsi
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	688(%rbp), %r8
	callq	*%r14
	cmpq	$0, 736(%rbp)
	je	.LBB12_384
	callq	*%rsi
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	608(%rbp), %r8
	callq	*%r14
	jmp	.LBB12_384
.LBB12_250:
	movq	176(%rbp), %rcx
	movq	%rcx, 616(%rbp)
	movq	96(%rbp), %rax
	addq	%rax, %rax
	movq	%rax, 456(%rbp)
	leaq	(%rcx,%rcx), %rax
	movq	%rax, 408(%rbp)
	leaq	-40(%rbp), %rax
	movq	%rax, 192(%rbp)
	leaq	_RNvXsi_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impjNtB9_7Display3fmt(%rip), %rcx
	movq	%rcx, 200(%rbp)
	leaq	616(%rbp), %rax
	movq	%rax, 208(%rbp)
	movq	%rcx, 216(%rbp)
	leaq	96(%rbp), %rax
	movq	%rax, 224(%rbp)
	movq	%rcx, 232(%rbp)
	leaq	456(%rbp), %rax
	movq	%rax, 240(%rbp)
	movq	%rcx, 248(%rbp)
	leaq	408(%rbp), %rax
	movq	%rax, 256(%rbp)
	movq	%rcx, 264(%rbp)
	leaq	376(%rbp), %rax
	movq	%rax, 272(%rbp)
	movq	%rcx, 280(%rbp)
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.42(%rip), %rax
	movq	%rax, 288(%rbp)
	leaq	_RNvXsC_NtNtCs8xEFJqa6dYS_4core3fmt3numyNtB7_8LowerHex3fmt(%rip), %rax
	movq	%rax, 296(%rbp)
	leaq	104(%rbp), %rcx
	movq	%rcx, 304(%rbp)
	movq	%rax, 312(%rbp)
	leaq	120(%rbp), %rcx
	movq	%rcx, 320(%rbp)
	movq	%rax, 328(%rbp)
	leaq	112(%rbp), %rcx
	movq	%rcx, 336(%rbp)
	movq	%rax, 344(%rbp)
.Ltmp114:
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.43(%rip), %rcx
	leaq	192(%rbp), %rdx
	callq	_RNvNtNtCse0R8cuyqEa_3std2io5stdio6__print
	nop
.Ltmp115:
	cmpq	$0, 176(%rbp)
	je	.LBB12_258
	movq	56(%rbp), %rax
	leaq	32(%rax), %rdi
	jmp	.LBB12_253
.LBB12_257:
	addq	$48, %rdi
	decq	176(%rbp)
	je	.LBB12_258
.LBB12_253:
	cmpq	$0, -32(%rdi)
	je	.LBB12_255
	movq	-24(%rdi), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_255:
	cmpq	$0, -8(%rdi)
	je	.LBB12_257
	movq	(%rdi), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	jmp	.LBB12_257
.LBB12_258:
	cmpq	$0, 384(%rbp)
	je	.LBB12_260
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	56(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_260:
	leaq	192(%rbp), %rdi
	movq	%rdi, %rcx
	callq	_RNvNtCse0R8cuyqEa_3std3env7args_os
	leaq	480(%rbp), %rbx
	movabsq	$3271424703783251245, %r14
	jmp	.LBB12_261
.LBB12_472:
	testb	%r15b, %r15b
	jne	.LBB12_473
.LBB12_261:
.Ltmp116:
	movq	%rbx, %rcx
	movq	%rdi, %rdx
	callq	_RNvXsc_NtCse0R8cuyqEa_3std3envNtB5_4ArgsNtNtNtNtCs8xEFJqa6dYS_4core4iter6traits8iterator8Iterator4next
	nop
.Ltmp117:
	movq	480(%rbp), %rax
	cmpq	$-1, %rax
	je	.LBB12_481
	movq	488(%rbp), %rsi
	cmpq	$12, 496(%rbp)
	jne	.LBB12_264
	movq	(%rsi), %rcx
	xorq	%r14, %rcx
	movl	8(%rsi), %edx
	xorq	$2037149295, %rdx
	orq	%rcx, %rdx
	sete	%r15b
	jmp	.LBB12_470
.LBB12_264:
	xorl	%r15d, %r15d
.LBB12_470:
	testq	%rax, %rax
	je	.LBB12_472
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	jmp	.LBB12_472
.LBB12_348:
	movq	%rax, 376(%rbp)
	movq	712(%rbp), %rax
	movq	%rax, 192(%rbp)
	leaq	_RNvXsq_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt(%rip), %rax
	movq	%rax, 200(%rbp)
.Ltmp102:
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.40(%rip), %rdx
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.41(%rip), %r9
	leaq	136(%rbp), %rcx
	leaq	192(%rbp), %r8
	callq	_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedttECs2i4to50FHNk_9prototype
	nop
.Ltmp103:
	jmp	.LBB12_42
.LBB12_387:
	leaq	(%rsi,%rdx,2), %rcx
	movq	%rax, 376(%rbp)
	movq	712(%rbp), %rax
	movq	%rax, 192(%rbp)
	leaq	_RNvXsq_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt(%rip), %rax
	movq	%rax, 200(%rbp)
.Ltmp104:
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.38(%rip), %rdx
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.39(%rip), %r9
	leaq	192(%rbp), %r8
	callq	_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedttECs2i4to50FHNk_9prototype
	nop
.Ltmp105:
	jmp	.LBB12_42
.LBB12_481:
	movq	200(%rbp), %rdi
	movq	216(%rbp), %rbx
	subq	%rdi, %rbx
	je	.LBB12_486
	shrq	$5, %rbx
	addq	$8, %rdi
	jmp	.LBB12_483
.LBB12_485:
	addq	$32, %rdi
	decq	%rbx
	je	.LBB12_486
.LBB12_483:
	cmpq	$0, -8(%rdi)
	je	.LBB12_485
	movq	(%rdi), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	jmp	.LBB12_485
.LBB12_486:
	cmpq	$0, 208(%rbp)
	je	.LBB12_488
	movq	192(%rbp), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_488:
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
	movq	$0, 648(%rbp)
	leaq	_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtReNtB6_7Display3fmtCs2i4to50FHNk_9prototype(%rip), %r14
	movaps	__xmm@7fffffff7fffffff7fffffff7fffffff(%rip), %xmm6
	movss	__real@3c800000(%rip), %xmm7
	movq	$0, 184(%rbp)
.LBB12_489:
	movq	184(%rbp), %rcx
	movq	496(%rbp,%rcx,8), %rax
	incq	%rcx
	movq	%rcx, 184(%rbp)
	movq	%rax, 384(%rbp)
	movq	$0, 408(%rbp)
	movq	$2, 416(%rbp)
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.7(%rip), %rax
	movq	%rax, 424(%rbp)
	movq	$13, 432(%rbp)
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.51(%rip), %rax
	movq	%rax, 440(%rbp)
	movq	$6, 448(%rbp)
	movq	$0, 640(%rbp)
.LBB12_490:
	movq	640(%rbp), %rax
	shlq	$4, %rax
	leaq	424(%rbp), %rcx
	movups	(%rcx,%rax), %xmm0
	movups	%xmm0, 64(%rbp)
	movl	$192, %r8d
	xorl	%edx, %edx
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rax, 728(%rbp)
	testq	%rax, %rax
	je	.LBB12_500
	incq	640(%rbp)
	movq	$0, 736(%rbp)
.LBB12_492:
	movq	384(%rbp), %rbx
	leaq	(,%rbx,4), %rsi
	movq	%rbx, %rax
	shrq	$62, %rax
	setne	%al
	movabsq	$9223372036854775804, %rcx
	cmpq	%rcx, %rsi
	seta	%cl
	orb	%al, %cl
	jne	.LBB12_509
	testq	%rsi, %rsi
	je	.LBB12_494
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rbx, %rcx
	testq	%rax, %rax
	jne	.LBB12_495
	jmp	.LBB12_508
.LBB12_494:
	movl	$4, %eax
	xorl	%ecx, %ecx
.LBB12_495:
	testq	%rbx, %rbx
	je	.LBB12_512
	xorl	%edx, %edx
	jmp	.LBB12_497
.LBB12_510:
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
	je	.LBB12_512
.LBB12_497:
	cmpq	$13, 72(%rbp)
	jne	.LBB12_510
	movq	64(%rbp), %r8
	movq	(%r8), %r9
	movabsq	$7311146993788874608, %r10
	xorq	%r10, %r9
	movq	5(%r8), %r8
	movabsq	$8030592661815916137, %r10
	xorq	%r10, %r8
	orq	%r9, %r8
	jne	.LBB12_510
	xorps	%xmm0, %xmm0
	movss	%xmm0, (%rax,%rdx,4)
	incq	%rdx
	cmpq	%rdx, %rbx
	jne	.LBB12_497
.LBB12_512:
	movq	736(%rbp), %r9
	leaq	(%r9,%r9,2), %rdx
	incq	%r9
	movq	728(%rbp), %r8
	movq	%rcx, (%r8,%rdx,8)
	movq	%rax, 8(%r8,%rdx,8)
	movq	%rbx, 16(%r8,%rdx,8)
	movq	%r9, 736(%rbp)
	cmpq	$8, %r9
	jne	.LBB12_492
	movq	384(%rbp), %rcx
	testq	%rcx, %rcx
	je	.LBB12_514
	cmpq	$2000000, %rcx
	ja	.LBB12_533
	movl	$2000000, %eax
	xorl	%edx, %edx
	divl	%ecx
	jmp	.LBB12_535
.LBB12_533:
	xorl	%eax, %eax
.LBB12_535:
	cmpq	$1025, %rax
	movl	$1024, %ecx
	cmovbq	%rcx, %rax
	movq	%rax, -64(%rbp)
	movq	$0, 616(%rbp)
	movq	$2, 624(%rbp)
	movw	$1, 632(%rbp)
	movq	$0, 688(%rbp)
	jmp	.LBB12_536
.LBB12_707:
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	736(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
	cmpq	$2, 688(%rbp)
	movl	$1, %eax
	movq	%rax, 688(%rbp)
	je	.LBB12_661
.LBB12_536:
	movq	688(%rbp), %rax
	movzbl	632(%rbp,%rax), %esi
	movl	$192, %r8d
	xorl	%edx, %edx
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	movq	%rax, 736(%rbp)
	testq	%rax, %rax
	je	.LBB12_537
	movq	$8, 192(%rbp)
	movq	736(%rbp), %rax
	movq	%rax, 200(%rbp)
	movq	728(%rbp), %rax
	movq	16(%rax), %rbx
	movl	$4, %edi
	movl	$4, %r12d
	testq	%rbx, %rbx
	je	.LBB12_553
	movq	728(%rbp), %rax
	movq	8(%rax), %r13
	leaq	(,%rbx,4), %r15
	xorl	%edx, %edx
	movq	%r15, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	je	.LBB12_557
	movq	%rax, %r12
	testb	%sil, %sil
	je	.LBB12_542
	movq	%r12, %rcx
	movq	%r13, %rdx
	movq	%r15, %r8
	callq	memcpy
	jmp	.LBB12_553
.LBB12_542:
	cmpq	$8, %rbx
	setb	%al
	movq	%r12, %rcx
	subq	%r13, %rcx
	cmpq	$32, %rcx
	setb	%cl
	orb	%al, %cl
	je	.LBB12_544
	xorl	%eax, %eax
	jmp	.LBB12_547
.LBB12_544:
	movq	%rbx, %rax
	andq	$-8, %rax
	xorl	%ecx, %ecx
.LBB12_545:
	movups	(%r13,%rcx,4), %xmm0
	movups	16(%r13,%rcx,4), %xmm1
	andps	%xmm6, %xmm0
	andps	%xmm6, %xmm1
	movups	%xmm0, (%r12,%rcx,4)
	movups	%xmm1, 16(%r12,%rcx,4)
	addq	$8, %rcx
	cmpq	%rcx, %rax
	jne	.LBB12_545
	cmpq	%rax, %rbx
	je	.LBB12_553
.LBB12_547:
	movq	%rbx, %rdx
	movq	%rax, %rcx
	andq	$3, %rdx
	je	.LBB12_550
	movq	%rax, %rcx
.LBB12_549:
	movl	(%r13,%rcx,4), %r8d
	movl	$2147483647, %r9d
	andl	%r9d, %r8d
	movl	%r8d, (%r12,%rcx,4)
	incq	%rcx
	decq	%rdx
	jne	.LBB12_549
.LBB12_550:
	subq	%rbx, %rax
	cmpq	$-4, %rax
	ja	.LBB12_553
.LBB12_551:
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
	jne	.LBB12_551
.LBB12_553:
	movq	736(%rbp), %rax
	movq	%rbx, (%rax)
	movq	%r12, 8(%rax)
	movq	%rbx, 16(%rax)
	movq	728(%rbp), %rax
	movq	40(%rax), %rbx
	testq	%rbx, %rbx
	je	.LBB12_570
	movq	728(%rbp), %rax
	movq	32(%rax), %r12
	leaq	(,%rbx,4), %r15
	xorl	%edx, %edx
	movq	%r15, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	je	.LBB12_555
	movq	%rax, %rdi
	testb	%sil, %sil
	je	.LBB12_559
	movq	%rdi, %rcx
	movq	%r12, %rdx
	movq	%r15, %r8
	callq	memcpy
	jmp	.LBB12_570
.LBB12_559:
	cmpq	$8, %rbx
	setb	%al
	movq	%rdi, %rcx
	subq	%r12, %rcx
	cmpq	$32, %rcx
	setb	%cl
	orb	%al, %cl
	je	.LBB12_561
	xorl	%eax, %eax
	jmp	.LBB12_564
.LBB12_561:
	movq	%rbx, %rax
	andq	$-8, %rax
	xorl	%ecx, %ecx
.LBB12_562:
	movups	(%r12,%rcx,4), %xmm0
	movups	16(%r12,%rcx,4), %xmm1
	andps	%xmm6, %xmm0
	andps	%xmm6, %xmm1
	movups	%xmm0, (%rdi,%rcx,4)
	movups	%xmm1, 16(%rdi,%rcx,4)
	addq	$8, %rcx
	cmpq	%rcx, %rax
	jne	.LBB12_562
	cmpq	%rax, %rbx
	je	.LBB12_570
.LBB12_564:
	movq	%rbx, %rdx
	movq	%rax, %rcx
	andq	$3, %rdx
	je	.LBB12_567
	movq	%rax, %rcx
.LBB12_566:
	movl	(%r12,%rcx,4), %r8d
	movl	$2147483647, %r9d
	andl	%r9d, %r8d
	movl	%r8d, (%rdi,%rcx,4)
	incq	%rcx
	decq	%rdx
	jne	.LBB12_566
.LBB12_567:
	subq	%rbx, %rax
	cmpq	$-4, %rax
	ja	.LBB12_570
.LBB12_568:
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
	jne	.LBB12_568
.LBB12_570:
	movq	736(%rbp), %rax
	movq	%rbx, 24(%rax)
	movq	%rdi, 32(%rax)
	movq	%rbx, 40(%rax)
	movq	728(%rbp), %rax
	movq	64(%rax), %rbx
	movl	$4, %edi
	movl	$4, %r12d
	testq	%rbx, %rbx
	je	.LBB12_585
	movq	728(%rbp), %rax
	movq	56(%rax), %r13
	leaq	(,%rbx,4), %r15
	xorl	%edx, %edx
	movq	%r15, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	je	.LBB12_572
	movq	%rax, %r12
	testb	%sil, %sil
	je	.LBB12_574
	movq	%r12, %rcx
	movq	%r13, %rdx
	movq	%r15, %r8
	callq	memcpy
	jmp	.LBB12_585
.LBB12_574:
	cmpq	$8, %rbx
	setb	%al
	movq	%r12, %rcx
	subq	%r13, %rcx
	cmpq	$32, %rcx
	setb	%cl
	orb	%al, %cl
	je	.LBB12_576
	xorl	%eax, %eax
	jmp	.LBB12_579
.LBB12_576:
	movq	%rbx, %rax
	andq	$-8, %rax
	xorl	%ecx, %ecx
.LBB12_577:
	movups	(%r13,%rcx,4), %xmm0
	movups	16(%r13,%rcx,4), %xmm1
	andps	%xmm6, %xmm0
	andps	%xmm6, %xmm1
	movups	%xmm0, (%r12,%rcx,4)
	movups	%xmm1, 16(%r12,%rcx,4)
	addq	$8, %rcx
	cmpq	%rcx, %rax
	jne	.LBB12_577
	cmpq	%rax, %rbx
	je	.LBB12_585
.LBB12_579:
	movq	%rbx, %rdx
	movq	%rax, %rcx
	andq	$3, %rdx
	je	.LBB12_582
	movq	%rax, %rcx
.LBB12_581:
	movl	(%r13,%rcx,4), %r8d
	movl	$2147483647, %r9d
	andl	%r9d, %r8d
	movl	%r8d, (%r12,%rcx,4)
	incq	%rcx
	decq	%rdx
	jne	.LBB12_581
.LBB12_582:
	subq	%rbx, %rax
	cmpq	$-4, %rax
	ja	.LBB12_585
.LBB12_583:
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
	jne	.LBB12_583
.LBB12_585:
	movq	736(%rbp), %rax
	movq	%rbx, 48(%rax)
	movq	%r12, 56(%rax)
	movq	%rbx, 64(%rax)
	movq	728(%rbp), %rax
	movq	88(%rax), %rbx
	testq	%rbx, %rbx
	je	.LBB12_600
	movq	728(%rbp), %rax
	movq	80(%rax), %r12
	leaq	(,%rbx,4), %r15
	xorl	%edx, %edx
	movq	%r15, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	je	.LBB12_587
	movq	%rax, %rdi
	testb	%sil, %sil
	je	.LBB12_589
	movq	%rdi, %rcx
	movq	%r12, %rdx
	movq	%r15, %r8
	callq	memcpy
	jmp	.LBB12_600
.LBB12_589:
	cmpq	$8, %rbx
	setb	%al
	movq	%rdi, %rcx
	subq	%r12, %rcx
	cmpq	$32, %rcx
	setb	%cl
	orb	%al, %cl
	je	.LBB12_591
	xorl	%eax, %eax
	jmp	.LBB12_594
.LBB12_591:
	movq	%rbx, %rax
	andq	$-8, %rax
	xorl	%ecx, %ecx
.LBB12_592:
	movups	(%r12,%rcx,4), %xmm0
	movups	16(%r12,%rcx,4), %xmm1
	andps	%xmm6, %xmm0
	andps	%xmm6, %xmm1
	movups	%xmm0, (%rdi,%rcx,4)
	movups	%xmm1, 16(%rdi,%rcx,4)
	addq	$8, %rcx
	cmpq	%rcx, %rax
	jne	.LBB12_592
	cmpq	%rax, %rbx
	je	.LBB12_600
.LBB12_594:
	movq	%rbx, %rdx
	movq	%rax, %rcx
	andq	$3, %rdx
	je	.LBB12_597
	movq	%rax, %rcx
.LBB12_596:
	movl	(%r12,%rcx,4), %r8d
	movl	$2147483647, %r9d
	andl	%r9d, %r8d
	movl	%r8d, (%rdi,%rcx,4)
	incq	%rcx
	decq	%rdx
	jne	.LBB12_596
.LBB12_597:
	subq	%rbx, %rax
	cmpq	$-4, %rax
	ja	.LBB12_600
.LBB12_598:
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
	jne	.LBB12_598
.LBB12_600:
	movq	736(%rbp), %rax
	movq	%rbx, 72(%rax)
	movq	%rdi, 80(%rax)
	movq	%rbx, 88(%rax)
	movq	728(%rbp), %rax
	movq	112(%rax), %rbx
	movl	$4, %edi
	movl	$4, %r12d
	testq	%rbx, %rbx
	je	.LBB12_615
	movq	728(%rbp), %rax
	movq	104(%rax), %r13
	leaq	(,%rbx,4), %r15
	xorl	%edx, %edx
	movq	%r15, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	je	.LBB12_602
	movq	%rax, %r12
	testb	%sil, %sil
	je	.LBB12_604
	movq	%r12, %rcx
	movq	%r13, %rdx
	movq	%r15, %r8
	callq	memcpy
	jmp	.LBB12_615
.LBB12_604:
	cmpq	$8, %rbx
	setb	%al
	movq	%r12, %rcx
	subq	%r13, %rcx
	cmpq	$32, %rcx
	setb	%cl
	orb	%al, %cl
	je	.LBB12_606
	xorl	%eax, %eax
	jmp	.LBB12_609
.LBB12_606:
	movq	%rbx, %rax
	andq	$-8, %rax
	xorl	%ecx, %ecx
.LBB12_607:
	movups	(%r13,%rcx,4), %xmm0
	movups	16(%r13,%rcx,4), %xmm1
	andps	%xmm6, %xmm0
	andps	%xmm6, %xmm1
	movups	%xmm0, (%r12,%rcx,4)
	movups	%xmm1, 16(%r12,%rcx,4)
	addq	$8, %rcx
	cmpq	%rcx, %rax
	jne	.LBB12_607
	cmpq	%rax, %rbx
	je	.LBB12_615
.LBB12_609:
	movq	%rbx, %rdx
	movq	%rax, %rcx
	andq	$3, %rdx
	je	.LBB12_612
	movq	%rax, %rcx
.LBB12_611:
	movl	(%r13,%rcx,4), %r8d
	movl	$2147483647, %r9d
	andl	%r9d, %r8d
	movl	%r8d, (%r12,%rcx,4)
	incq	%rcx
	decq	%rdx
	jne	.LBB12_611
.LBB12_612:
	subq	%rbx, %rax
	cmpq	$-4, %rax
	ja	.LBB12_615
.LBB12_613:
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
	jne	.LBB12_613
.LBB12_615:
	movq	736(%rbp), %rax
	movq	%rbx, 96(%rax)
	movq	%r12, 104(%rax)
	movq	%rbx, 112(%rax)
	movq	728(%rbp), %rax
	movq	136(%rax), %rbx
	testq	%rbx, %rbx
	je	.LBB12_630
	movq	728(%rbp), %rax
	movq	128(%rax), %r12
	leaq	(,%rbx,4), %r15
	xorl	%edx, %edx
	movq	%r15, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	je	.LBB12_617
	movq	%rax, %rdi
	testb	%sil, %sil
	je	.LBB12_619
	movq	%rdi, %rcx
	movq	%r12, %rdx
	movq	%r15, %r8
	callq	memcpy
	jmp	.LBB12_630
.LBB12_619:
	cmpq	$8, %rbx
	setb	%al
	movq	%rdi, %rcx
	subq	%r12, %rcx
	cmpq	$32, %rcx
	setb	%cl
	orb	%al, %cl
	je	.LBB12_621
	xorl	%eax, %eax
	jmp	.LBB12_624
.LBB12_621:
	movq	%rbx, %rax
	andq	$-8, %rax
	xorl	%ecx, %ecx
.LBB12_622:
	movups	(%r12,%rcx,4), %xmm0
	movups	16(%r12,%rcx,4), %xmm1
	andps	%xmm6, %xmm0
	andps	%xmm6, %xmm1
	movups	%xmm0, (%rdi,%rcx,4)
	movups	%xmm1, 16(%rdi,%rcx,4)
	addq	$8, %rcx
	cmpq	%rcx, %rax
	jne	.LBB12_622
	cmpq	%rax, %rbx
	je	.LBB12_630
.LBB12_624:
	movq	%rbx, %rdx
	movq	%rax, %rcx
	andq	$3, %rdx
	je	.LBB12_627
	movq	%rax, %rcx
.LBB12_626:
	movl	(%r12,%rcx,4), %r8d
	movl	$2147483647, %r9d
	andl	%r9d, %r8d
	movl	%r8d, (%rdi,%rcx,4)
	incq	%rcx
	decq	%rdx
	jne	.LBB12_626
.LBB12_627:
	subq	%rbx, %rax
	cmpq	$-4, %rax
	ja	.LBB12_630
.LBB12_628:
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
	jne	.LBB12_628
.LBB12_630:
	movq	736(%rbp), %rax
	movq	%rbx, 120(%rax)
	movq	%rdi, 128(%rax)
	movq	%rbx, 136(%rax)
	movq	728(%rbp), %rax
	movq	160(%rax), %rbx
	testq	%rbx, %rbx
	je	.LBB12_631
	movq	728(%rbp), %rax
	movq	152(%rax), %r12
	leaq	(,%rbx,4), %r15
	xorl	%edx, %edx
	movq	%r15, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	je	.LBB12_633
	movq	%rax, %rdi
	testb	%sil, %sil
	je	.LBB12_635
	movq	%rdi, %rcx
	movq	%r12, %rdx
	movq	%r15, %r8
	callq	memcpy
	jmp	.LBB12_646
.LBB12_631:
	movl	$4, %edi
	jmp	.LBB12_646
.LBB12_635:
	cmpq	$8, %rbx
	setb	%al
	movq	%rdi, %rcx
	subq	%r12, %rcx
	cmpq	$32, %rcx
	setb	%cl
	orb	%al, %cl
	je	.LBB12_637
	xorl	%eax, %eax
	jmp	.LBB12_640
.LBB12_637:
	movq	%rbx, %rax
	andq	$-8, %rax
	xorl	%ecx, %ecx
.LBB12_638:
	movups	(%r12,%rcx,4), %xmm0
	movups	16(%r12,%rcx,4), %xmm1
	andps	%xmm6, %xmm0
	andps	%xmm6, %xmm1
	movups	%xmm0, (%rdi,%rcx,4)
	movups	%xmm1, 16(%rdi,%rcx,4)
	addq	$8, %rcx
	cmpq	%rcx, %rax
	jne	.LBB12_638
	cmpq	%rax, %rbx
	je	.LBB12_646
.LBB12_640:
	movq	%rbx, %rdx
	movq	%rax, %rcx
	andq	$3, %rdx
	je	.LBB12_643
	movq	%rax, %rcx
.LBB12_642:
	movl	(%r12,%rcx,4), %r8d
	movl	$2147483647, %r9d
	andl	%r9d, %r8d
	movl	%r8d, (%rdi,%rcx,4)
	incq	%rcx
	decq	%rdx
	jne	.LBB12_642
.LBB12_643:
	subq	%rbx, %rax
	cmpq	$-4, %rax
	ja	.LBB12_646
.LBB12_644:
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
	jne	.LBB12_644
.LBB12_646:
	incq	688(%rbp)
	movq	736(%rbp), %rax
	movq	%rbx, 144(%rax)
	movq	%rdi, 152(%rax)
	movq	%rbx, 160(%rax)
	movq	728(%rbp), %rax
	movq	184(%rax), %r13
	testq	%r13, %r13
	je	.LBB12_681
	movq	728(%rbp), %rax
	movq	176(%rax), %rbx
	leaq	(,%r13,4), %r15
	xorl	%edx, %edx
	movq	%r15, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	je	.LBB12_648
	movq	%rax, %rdi
	testb	%sil, %sil
	je	.LBB12_650
	movq	%rdi, %rcx
	movq	%rbx, %rdx
	movq	%r15, %r8
	callq	memcpy
	movq	736(%rbp), %rax
	leaq	168(%rax), %r15
	movq	%r13, 168(%rax)
	movq	%rax, %rbx
	addq	$176, %rbx
	movq	%rdi, 176(%rax)
	movq	%r13, 184(%rax)
	jmp	.LBB12_686
.LBB12_681:
	movq	736(%rbp), %rax
	leaq	168(%rax), %r15
	movq	$0, 168(%rax)
	movq	%rax, %rbx
	addq	$176, %rbx
	movq	$4, 176(%rax)
	movq	$0, 184(%rax)
	testb	%sil, %sil
	je	.LBB12_682
.LBB12_686:
	movq	%rbx, 368(%rbp)
	movq	%r15, 360(%rbp)
.Ltmp124:
	movl	$32, %r8d
	leaq	d015_baseline_i16(%rip), %rcx
	movq	736(%rbp), %rdx
	callq	_RNvCs2i4to50FHNk_9prototype7bench_i
	nop
.Ltmp125:
	movsd	%xmm0, 192(%rbp)
	leaq	192(%rbp), %rax
	#APP
	#NO_APP
	movq	%rbx, 368(%rbp)
	movq	%r15, 360(%rbp)
.Ltmp126:
	movl	$32, %r8d
	leaq	d015_candidate_i16(%rip), %rcx
	movq	736(%rbp), %rdx
	callq	_RNvCs2i4to50FHNk_9prototype7bench_i
	nop
.Ltmp127:
	movsd	%xmm0, 192(%rbp)
	leaq	192(%rbp), %rax
	#APP
	#NO_APP
	jmp	.LBB12_689
.LBB12_650:
	cmpq	$8, %r13
	setb	%al
	movq	%rdi, %rcx
	subq	%rbx, %rcx
	cmpq	$32, %rcx
	setb	%cl
	orb	%al, %cl
	je	.LBB12_652
	xorl	%eax, %eax
	jmp	.LBB12_655
.LBB12_652:
	movq	%r13, %rax
	andq	$-8, %rax
	xorl	%ecx, %ecx
.LBB12_653:
	movups	(%rbx,%rcx,4), %xmm0
	movups	16(%rbx,%rcx,4), %xmm1
	andps	%xmm6, %xmm0
	andps	%xmm6, %xmm1
	movups	%xmm0, (%rdi,%rcx,4)
	movups	%xmm1, 16(%rdi,%rcx,4)
	addq	$8, %rcx
	cmpq	%rcx, %rax
	jne	.LBB12_653
	cmpq	%rax, %r13
	je	.LBB12_660
.LBB12_655:
	movq	%r13, %rdx
	movq	%rax, %rcx
	andq	$3, %rdx
	je	.LBB12_658
	movq	%rax, %rcx
.LBB12_657:
	movl	(%rbx,%rcx,4), %r8d
	movl	$2147483647, %r9d
	andl	%r9d, %r8d
	movl	%r8d, (%rdi,%rcx,4)
	incq	%rcx
	decq	%rdx
	jne	.LBB12_657
.LBB12_658:
	subq	%r13, %rax
	cmpq	$-4, %rax
	ja	.LBB12_660
.LBB12_659:
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
	jne	.LBB12_659
.LBB12_660:
	movq	736(%rbp), %rax
	leaq	168(%rax), %r15
	movq	%r13, 168(%rax)
	movq	%rax, %rbx
	addq	$176, %rbx
	movq	%rdi, 176(%rax)
	movq	%r13, 184(%rax)
.LBB12_682:
	movq	%rbx, 368(%rbp)
	movq	%r15, 360(%rbp)
.Ltmp120:
	movl	$32, %r8d
	leaq	d015_baseline_u16(%rip), %rcx
	movq	736(%rbp), %rdx
	callq	_RNvCs2i4to50FHNk_9prototype7bench_i
	nop
.Ltmp121:
	movsd	%xmm0, 192(%rbp)
	leaq	192(%rbp), %rax
	#APP
	#NO_APP
	movq	%rbx, 368(%rbp)
	movq	%r15, 360(%rbp)
.Ltmp122:
	movl	$32, %r8d
	leaq	d015_candidate_u16(%rip), %rcx
	movq	736(%rbp), %rdx
	callq	_RNvCs2i4to50FHNk_9prototype7bench_i
	nop
.Ltmp123:
	movsd	%xmm0, 192(%rbp)
	leaq	192(%rbp), %rax
	#APP
	#NO_APP
.LBB12_689:
	xorl	%r13d, %r13d
	jmp	.LBB12_690
.LBB12_754:
	movl	712(%rbp), %eax
	movl	%eax, %r13d
.LBB12_690:
	cmpl	$9, %r13d
	jae	.LBB12_691
	leal	1(%r13), %eax
	movl	%eax, 712(%rbp)
	movl	%r13d, 136(%rbp)
	andb	$1, %r13b
	movl	%r13d, %eax
	xorb	$1, %al
	movq	$2, 464(%rbp)
	movb	%r13b, 472(%rbp)
	movb	%al, 473(%rbp)
	xorl	%eax, %eax
	cmpq	$2, %rax
	je	.LBB12_754
.LBB12_727:
	leaq	1(%rax), %rdi
	movq	%rdi, 456(%rbp)
	movzbl	472(%rbp,%rax), %r12d
	movq	-64(%rbp), %r8
	testb	%sil, %sil
	je	.LBB12_728
	leaq	d015_candidate_i16(%rip), %rcx
	testb	%r12b, %r12b
	jne	.LBB12_734
	leaq	d015_baseline_i16(%rip), %rcx
.LBB12_734:
	movq	%rbx, 368(%rbp)
	movq	%r15, 360(%rbp)
.Ltmp130:
	movq	736(%rbp), %rdx
	callq	_RNvCs2i4to50FHNk_9prototype7bench_i
	nop
.Ltmp131:
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.54(%rip), %rax
	jmp	.LBB12_736
.LBB12_728:
	leaq	d015_candidate_u16(%rip), %rcx
	testb	%r12b, %r12b
	jne	.LBB12_730
	leaq	d015_baseline_u16(%rip), %rcx
.LBB12_730:
	movq	%rbx, 368(%rbp)
	movq	%r15, 360(%rbp)
.Ltmp128:
	movq	736(%rbp), %rdx
	callq	_RNvCs2i4to50FHNk_9prototype7bench_i
	nop
.Ltmp129:
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.53(%rip), %rax
.LBB12_736:
	movsd	%xmm0, -88(%rbp)
	movq	%rax, 656(%rbp)
	movq	$3, 664(%rbp)
	movb	%r13b, 376(%rbp)
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.56(%rip), %rax
	testb	%r12b, %r12b
	jne	.LBB12_738
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.55(%rip), %rax
.LBB12_738:
	movq	%rax, 152(%rbp)
	xorb	$1, %r12b
	movzbl	%r12b, %eax
	leaq	(%rax,%rax,2), %rax
	addq	$5, %rax
	movq	%rax, 160(%rbp)
	leaq	656(%rbp), %rax
	movq	%rax, 192(%rbp)
	movq	%r14, 200(%rbp)
	leaq	64(%rbp), %rax
	movq	%rax, 208(%rbp)
	movq	%r14, 216(%rbp)
	leaq	384(%rbp), %rax
	movq	%rax, 224(%rbp)
	leaq	_RNvXsi_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impjNtB9_7Display3fmt(%rip), %rax
	movq	%rax, 232(%rbp)
	leaq	136(%rbp), %rcx
	movq	%rcx, 240(%rbp)
	leaq	_RNvXs9_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3implNtB9_7Display3fmt(%rip), %rcx
	movq	%rcx, 248(%rbp)
	leaq	376(%rbp), %rcx
	movq	%rcx, 256(%rbp)
	leaq	_RNvXsg_NtCs8xEFJqa6dYS_4core3fmtbNtB5_7Display3fmt(%rip), %rcx
	movq	%rcx, 264(%rbp)
	leaq	152(%rbp), %rcx
	movq	%rcx, 272(%rbp)
	movq	%r14, 280(%rbp)
	leaq	-64(%rbp), %rcx
	movq	%rcx, 288(%rbp)
	movq	%rax, 296(%rbp)
	leaq	-88(%rbp), %rax
	movq	%rax, 304(%rbp)
	leaq	_RNvXs7_NtNtCs8xEFJqa6dYS_4core3fmt5floatdNtB7_7Display3fmt(%rip), %rax
	movq	%rax, 312(%rbp)
	movq	%rbx, 368(%rbp)
	movq	%r15, 360(%rbp)
.Ltmp132:
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.57(%rip), %rcx
	leaq	192(%rbp), %rdx
	callq	_RNvNtNtCse0R8cuyqEa_3std2io5stdio6__print
	nop
.Ltmp133:
	movq	%rdi, %rax
	cmpq	$2, %rax
	jne	.LBB12_727
	jmp	.LBB12_754
.LBB12_691:
	movq	736(%rbp), %rax
	cmpq	$0, (%rax)
	je	.LBB12_693
	movq	736(%rbp), %rax
	movq	8(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_693:
	movq	736(%rbp), %rax
	cmpq	$0, 24(%rax)
	je	.LBB12_695
	movq	736(%rbp), %rax
	movq	32(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_695:
	movq	736(%rbp), %rax
	cmpq	$0, 48(%rax)
	je	.LBB12_697
	movq	736(%rbp), %rax
	movq	56(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_697:
	movq	736(%rbp), %rax
	cmpq	$0, 72(%rax)
	je	.LBB12_699
	movq	736(%rbp), %rax
	movq	80(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_699:
	movq	736(%rbp), %rax
	cmpq	$0, 96(%rax)
	je	.LBB12_701
	movq	736(%rbp), %rax
	movq	104(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_701:
	movq	736(%rbp), %rax
	cmpq	$0, 120(%rax)
	je	.LBB12_703
	movq	736(%rbp), %rax
	movq	128(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_703:
	movq	736(%rbp), %rax
	cmpq	$0, 144(%rax)
	je	.LBB12_705
	movq	736(%rbp), %rax
	movq	152(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_705:
	cmpq	$0, (%r15)
	je	.LBB12_707
	movq	(%rbx), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	jmp	.LBB12_707
.LBB12_661:
	movq	728(%rbp), %rax
	cmpq	$0, (%rax)
	je	.LBB12_663
	movq	728(%rbp), %rax
	movq	8(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_663:
	movq	728(%rbp), %rax
	cmpq	$0, 24(%rax)
	je	.LBB12_665
	movq	728(%rbp), %rax
	movq	32(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_665:
	movq	728(%rbp), %rax
	cmpq	$0, 48(%rax)
	je	.LBB12_667
	movq	728(%rbp), %rax
	movq	56(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_667:
	movq	728(%rbp), %rax
	cmpq	$0, 72(%rax)
	je	.LBB12_669
	movq	728(%rbp), %rax
	movq	80(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_669:
	movq	728(%rbp), %rax
	cmpq	$0, 96(%rax)
	je	.LBB12_671
	movq	728(%rbp), %rax
	movq	104(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_671:
	movq	728(%rbp), %rax
	cmpq	$0, 120(%rax)
	je	.LBB12_673
	movq	728(%rbp), %rax
	movq	128(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_673:
	movq	728(%rbp), %rax
	cmpq	$0, 144(%rax)
	je	.LBB12_675
	movq	728(%rbp), %rax
	movq	152(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_675:
	movq	728(%rbp), %rax
	cmpq	$0, 168(%rax)
	je	.LBB12_677
	movq	728(%rbp), %rax
	movq	176(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_677:
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	728(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
	cmpq	$2, 640(%rbp)
	movl	$1, %eax
	movq	%rax, 640(%rbp)
	jne	.LBB12_490
	cmpq	$14, 184(%rbp)
	jne	.LBB12_489
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.12(%rip), %rcx
	movl	$139, %edx
	callq	_RNvNtNtCse0R8cuyqEa_3std2io5stdio6__print
	jmp	.LBB12_680
.LBB12_473:
	movq	200(%rbp), %rdi
	movq	216(%rbp), %rbx
	subq	%rdi, %rbx
	je	.LBB12_478
	shrq	$5, %rbx
	addq	$8, %rdi
	jmp	.LBB12_475
.LBB12_477:
	addq	$32, %rdi
	decq	%rbx
	je	.LBB12_478
.LBB12_475:
	cmpq	$0, -8(%rdi)
	je	.LBB12_477
	movq	(%rdi), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	jmp	.LBB12_477
.LBB12_478:
	cmpq	$0, 208(%rbp)
	je	.LBB12_680
	movq	192(%rbp), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_680:
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
.LBB12_59:
	movl	$4, %eax
	movq	%rax, 728(%rbp)
.LBB12_60:
	movb	$1, 687(%rbp)
.Ltmp36:
	movq	728(%rbp), %rcx
	movq	%r13, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp37:
	jmp	.LBB12_42
.LBB12_76:
	movq	%r15, 688(%rbp)
	movb	$1, 686(%rbp)
.Ltmp20:
	movl	$4, %ecx
	movq	%r13, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp21:
	jmp	.LBB12_42
.LBB12_91:
	movq	%r15, 688(%rbp)
	movb	$1, 685(%rbp)
.Ltmp26:
	movl	$4, %ecx
	movq	%r13, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp27:
	jmp	.LBB12_42
.LBB12_106:
	movq	%rdi, 640(%rbp)
	movb	$1, 684(%rbp)
.Ltmp32:
	movl	$4, %ecx
	movq	%r13, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp33:
	jmp	.LBB12_42
.LBB12_335:
	movq	712(%rbp), %rax
	movq	%rax, 192(%rbp)
	leaq	_RNvXsq_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt(%rip), %rax
	movq	%rax, 200(%rbp)
.Ltmp90:
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.28(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.27(%rip), %r8
	leaq	92(%rbp), %rcx
	leaq	136(%rbp), %rdx
	leaq	192(%rbp), %r9
	callq	_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedmmECs2i4to50FHNk_9prototype
	nop
.Ltmp91:
	jmp	.LBB12_42
.LBB12_338:
	movq	712(%rbp), %rax
	movq	%rax, 192(%rbp)
	leaq	_RNvXsq_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt(%rip), %rax
	movq	%rax, 200(%rbp)
.Ltmp92:
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.30(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.29(%rip), %r8
	leaq	88(%rbp), %rcx
	leaq	136(%rbp), %rdx
	leaq	192(%rbp), %r9
	callq	_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedmmECs2i4to50FHNk_9prototype
	nop
.Ltmp93:
	jmp	.LBB12_42
.LBB12_340:
	movq	712(%rbp), %rax
	movq	%rax, 192(%rbp)
	leaq	_RNvXsq_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt(%rip), %rax
	movq	%rax, 200(%rbp)
.Ltmp94:
	leaq	616(%rbp), %rcx
	leaq	152(%rbp), %rdx
	leaq	192(%rbp), %r8
	callq	_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedINtNtCsfQUUnEvlYZE_5alloc3vec3VecsEBM_ECs2i4to50FHNk_9prototype
	nop
.Ltmp95:
	jmp	.LBB12_42
.LBB12_752:
	movq	712(%rbp), %rax
	movq	%rax, 192(%rbp)
	leaq	_RNvXsq_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt(%rip), %rax
	movq	%rax, 200(%rbp)
.Ltmp96:
	leaq	408(%rbp), %rcx
	leaq	456(%rbp), %rdx
	leaq	192(%rbp), %r8
	callq	_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedINtNtCsfQUUnEvlYZE_5alloc3vec3VectEBM_ECs2i4to50FHNk_9prototype
	nop
.Ltmp97:
	jmp	.LBB12_42
.LBB12_353:
	movq	736(%rbp), %rax
	movq	%rax, 728(%rbp)
	movq	%rsi, %rdx
.LBB12_354:
	movq	%rdx, 40(%rbp)
	movq	712(%rbp), %rax
	movq	%rax, 136(%rbp)
	leaq	_RNvXsq_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt(%rip), %rax
	movq	%rax, 144(%rbp)
.Ltmp100:
	leaq	656(%rbp), %rcx
	leaq	192(%rbp), %rdx
	leaq	136(%rbp), %r8
	callq	_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedINtNtCsfQUUnEvlYZE_5alloc3vec3VecmEBM_ECs2i4to50FHNk_9prototype
	nop
.Ltmp101:
	jmp	.LBB12_42
.LBB12_199:
	movl	$4, %ebx
.LBB12_200:
	movb	$1, 682(%rbp)
.Ltmp66:
	movq	%rbx, %rcx
	movq	%r15, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp67:
	jmp	.LBB12_42
.LBB12_179:
	movl	$4, %ecx
	jmp	.LBB12_180
.LBB12_441:
	movb	$1, 727(%rbp)
.Ltmp68:
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.45(%rip), %r8
	movq	%rbx, %rdx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	nop
.Ltmp69:
	jmp	.LBB12_42
.LBB12_404:
.Ltmp140:
	movl	$4, %ecx
	movq	%r14, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp141:
	jmp	.LBB12_42
.LBB12_427:
	movl	$4, %edx
.LBB12_428:
.Ltmp82:
	movq	%rdx, %rcx
	movq	%rsi, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp83:
	jmp	.LBB12_42
.LBB12_311:
.Ltmp112:
	movl	$2, %ecx
	movq	%r13, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp113:
	jmp	.LBB12_42
.LBB12_309:
.Ltmp110:
	movl	$2, %ecx
	movq	%r12, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp111:
	jmp	.LBB12_42
.LBB12_325:
.Ltmp108:
	movl	$2, %ecx
	movq	%r13, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp109:
	jmp	.LBB12_42
.LBB12_324:
.Ltmp106:
	movl	$2, %ecx
	movq	%rsi, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp107:
	jmp	.LBB12_42
.LBB12_457:
	movb	$1, 711(%rbp)
.Ltmp74:
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.47(%rip), %r8
	movq	%rbx, %rdx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	nop
.Ltmp75:
	jmp	.LBB12_42
.LBB12_310:
.Ltmp84:
	movl	$4, %ecx
	movq	128(%rbp), %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp85:
	jmp	.LBB12_42
.LBB12_444:
	movl	$4, %r13d
.LBB12_445:
	movb	$0, 727(%rbp)
.Ltmp80:
	movq	%r13, %rcx
	movq	%r14, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp81:
	jmp	.LBB12_42
.LBB12_366:
.Ltmp98:
	movl	$4, %ecx
	movq	%rsi, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp99:
	jmp	.LBB12_42
.LBB12_500:
	movl	$8, %ecx
	movl	$192, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.LBB12_537:
.Ltmp134:
	movl	$8, %ecx
	movl	$192, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp135:
	jmp	.LBB12_42
.LBB12_508:
	movl	$4, %eax
	movq	%rax, 648(%rbp)
.LBB12_509:
.Ltmp138:
	movq	648(%rbp), %rcx
	movq	%rsi, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp139:
	jmp	.LBB12_42
.LBB12_555:
	movl	$1, %eax
	jmp	.LBB12_556
.LBB12_572:
	movl	$2, %eax
	jmp	.LBB12_556
.LBB12_587:
	movl	$3, %eax
	jmp	.LBB12_556
.LBB12_602:
	movl	$4, %eax
	jmp	.LBB12_556
.LBB12_617:
	movl	$5, %eax
	jmp	.LBB12_556
.LBB12_633:
	movl	$6, %eax
	jmp	.LBB12_556
.LBB12_648:
	movl	$7, %eax
.LBB12_556:
	movq	%rax, 648(%rbp)
.LBB12_557:
.Ltmp118:
	movl	$4, %ecx
	movq	%r15, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp119:
	jmp	.LBB12_42
.LBB12_514:
.Ltmp136:
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.52(%rip), %rcx
	callq	_RNvNtNtCs8xEFJqa6dYS_4core9panicking11panic_const23panic_const_div_by_zero
	nop
.Ltmp137:
.LBB12_42:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvCs2i4to50FHNk_9prototype4main@IMGREL
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$29@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$29@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$29@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_29:
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
	movq	664(%rbp), %rsi
	movq	672(%rbp), %rbx
	testq	%rbx, %rbx
	movq	__imp_GetProcessHeap(%rip), %r15
	movq	__imp_HeapFree(%rip), %r12
	je	.LBB12_36
	leaq	32(%rsi), %r14
	jmp	.LBB12_31
	.p2align	4
.LBB12_35:
	addq	$48, %r14
	decq	%rbx
	je	.LBB12_36
.LBB12_31:
	cmpq	$0, -32(%r14)
	je	.LBB12_33
	movq	-24(%r14), %rdi
	callq	*%r15
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rdi, %r8
	callq	*%r12
.LBB12_33:
	cmpq	$0, -8(%r14)
	je	.LBB12_35
	movq	(%r14), %rdi
	callq	*%r15
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rdi, %r8
	callq	*%r12
	jmp	.LBB12_35
.LBB12_36:
	cmpq	$0, 656(%rbp)
	je	.LBB12_38
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_38:
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
	.def	"?dtor$46@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$46@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$46@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_46:
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
	jne	.LBB12_47
	cmpq	$0, 712(%rbp)
	je	.LBB12_50
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	696(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_50:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$116@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$116@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$116@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_116:
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
	cmpb	$0, 684(%rbp)
	je	.LBB12_117
	cmpq	$0, 688(%rbp)
	je	.LBB12_120
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	640(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_120:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$121@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$121@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$121@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_121:
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
	cmpb	$0, 685(%rbp)
	je	.LBB12_122
	cmpq	$0, 696(%rbp)
	je	.LBB12_125
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	688(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_125:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$126@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$126@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$126@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_126:
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
	cmpb	$0, 686(%rbp)
	je	.LBB12_127
	cmpq	$0, 696(%rbp)
	je	.LBB12_130
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	688(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_130:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$131@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$131@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$131@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_131:
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
	cmpb	$0, 687(%rbp)
	je	.LBB12_132
	cmpq	$0, 696(%rbp)
	je	.LBB12_135
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	688(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_135:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$139@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$139@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$139@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_139:
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
	jne	.LBB12_140
	cmpq	$0, 712(%rbp)
	je	.LBB12_143
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	696(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_143:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$193@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$193@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$193@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_193:
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
	cmpb	$0, 683(%rbp)
	je	.LBB12_194
	cmpq	$0, 712(%rbp)
	je	.LBB12_197
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	736(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_197:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$209@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$209@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$209@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_209:
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
	cmpb	$0, 682(%rbp)
	je	.LBB12_210
	cmpq	$0, 736(%rbp)
	je	.LBB12_213
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	712(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_213:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$217@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$217@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$217@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_217:
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
	jne	.LBB12_218
	cmpq	$0, 712(%rbp)
	je	.LBB12_221
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	696(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_221:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$238@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$238@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$238@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_238:
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
	je	.LBB12_239
	cmpq	$0, 616(%rbp)
	je	.LBB12_242
	movq	624(%rbp), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_242:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$265@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$265@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$265@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_265:
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
	movq	392(%rbp), %rsi
	movq	400(%rbp), %rbx
	testq	%rbx, %rbx
	movq	__imp_GetProcessHeap(%rip), %r15
	movq	__imp_HeapFree(%rip), %r12
	je	.LBB12_272
	leaq	32(%rsi), %r14
	jmp	.LBB12_267
.LBB12_271:
	addq	$48, %r14
	decq	%rbx
	je	.LBB12_272
.LBB12_267:
	cmpq	$0, -32(%r14)
	je	.LBB12_269
	movq	-24(%r14), %rdi
	callq	*%r15
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rdi, %r8
	callq	*%r12
.LBB12_269:
	cmpq	$0, -8(%r14)
	je	.LBB12_271
	movq	(%r14), %rdi
	callq	*%r15
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rdi, %r8
	callq	*%r12
	jmp	.LBB12_271
.LBB12_272:
	cmpq	$0, 384(%rbp)
	je	.LBB12_274
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_274:
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
	.def	"?dtor$312@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$312@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$312@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_312:
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
	je	.LBB12_314
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	608(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_314:
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
	.def	"?dtor$315@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$315@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$315@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_315:
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
	movaps	%xmm9, 96(%rsp)
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
	movq	688(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
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
	movaps	%xmm9, 96(%rsp)
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
	movaps	96(%rsp), %xmm9
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
	movaps	%xmm9, 96(%rsp)
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
	movq	640(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
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
	.def	"?dtor$328@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$328@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$328@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_328:
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
	movaps	%xmm9, 96(%rsp)
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
	movq	648(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
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
	.def	"?dtor$371@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$371@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$371@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_371:
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
	movaps	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	cmpq	$0, 728(%rbp)
	je	.LBB12_373
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	40(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_373:
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
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
	.def	"?dtor$405@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$405@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$405@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_405:
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
	leaq	192(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs2i4to50FHNk_9prototype4CaseEBD_
	movb	$0, 681(%rbp)
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
	.def	"?dtor$406@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$406@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$406@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_406:
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
	cmpb	$0, 681(%rbp)
	je	.LBB12_407
	cmpq	$0, 712(%rbp)
	je	.LBB12_410
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	736(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_410:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$442@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$442@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$442@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_442:
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
	leaq	192(%rbp), %rcx
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
	.def	"?dtor$458@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$458@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$458@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_458:
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
	leaq	192(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs2i4to50FHNk_9prototype4CaseEBD_
	movb	$0, 711(%rbp)
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
	.def	"?dtor$459@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$459@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$459@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_459:
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
	cmpb	$0, 711(%rbp)
	je	.LBB12_460
	cmpq	$0, 608(%rbp)
	je	.LBB12_463
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	640(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_463:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$464@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$464@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$464@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_464:
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
	je	.LBB12_465
	cmpq	$0, 736(%rbp)
	je	.LBB12_468
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	712(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_468:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs2i4to50FHNk_9prototype4main,unique,12
	.seh_endproc
	.def	"?dtor$480@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$480@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$480@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_480:
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
	movaps	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	leaq	192(%rbp), %rcx
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
	.def	"?dtor$501@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$501@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$501@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_501:
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
	je	.LBB12_506
	movq	728(%rbp), %rdi
	addq	$8, %rdi
	jmp	.LBB12_503
.LBB12_505:
	addq	$24, %rdi
	decq	736(%rbp)
	je	.LBB12_506
.LBB12_503:
	cmpq	$0, -8(%rdi)
	je	.LBB12_505
	movq	(%rdi), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	jmp	.LBB12_505
.LBB12_506:
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
	.def	"?dtor$515@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$515@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$515@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_515:
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
	movaps	%xmm9, 96(%rsp)
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
	je	.LBB12_517
	movq	728(%rbp), %rax
	movq	8(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_517:
	movq	728(%rbp), %rax
	cmpq	$0, 24(%rax)
	je	.LBB12_519
	movq	728(%rbp), %rax
	movq	32(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_519:
	movq	728(%rbp), %rax
	cmpq	$0, 48(%rax)
	je	.LBB12_521
	movq	728(%rbp), %rax
	movq	56(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_521:
	movq	728(%rbp), %rax
	cmpq	$0, 72(%rax)
	je	.LBB12_523
	movq	728(%rbp), %rax
	movq	80(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_523:
	movq	728(%rbp), %rax
	cmpq	$0, 96(%rax)
	je	.LBB12_525
	movq	728(%rbp), %rax
	movq	104(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_525:
	movq	728(%rbp), %rax
	cmpq	$0, 120(%rax)
	je	.LBB12_527
	movq	728(%rbp), %rax
	movq	128(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_527:
	movq	728(%rbp), %rax
	cmpq	$0, 144(%rax)
	je	.LBB12_529
	movq	728(%rbp), %rax
	movq	152(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_529:
	movq	728(%rbp), %rax
	cmpq	$0, 168(%rax)
	je	.LBB12_531
	movq	728(%rbp), %rax
	movq	176(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_531:
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
	.def	"?dtor$538@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$538@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$538@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_538:
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
	movaps	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	movq	648(%rbp), %rax
	movq	%rax, 208(%rbp)
	leaq	192(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecIBC_fEEECs2i4to50FHNk_9prototype
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
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
	.def	"?dtor$708@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$708@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$708@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_708:
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
	movaps	%xmm9, 96(%rsp)
	.seh_savexmm %xmm9, 96
	movaps	%xmm8, 112(%rsp)
	.seh_savexmm %xmm8, 112
	movaps	%xmm7, 128(%rsp)
	.seh_savexmm %xmm7, 128
	movaps	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	movq	360(%rbp), %rbx
	movq	368(%rbp), %rdi
	movq	184(%rbp), %rax
	movq	%rax, 480(%rbp)
	movq	640(%rbp), %rax
	movq	%rax, 408(%rbp)
	movq	688(%rbp), %rax
	movq	%rax, 616(%rbp)
	movq	736(%rbp), %rax
	cmpq	$0, (%rax)
	jne	.LBB12_709
	movq	736(%rbp), %rax
	cmpq	$0, 24(%rax)
	jne	.LBB12_711
.LBB12_712:
	movq	736(%rbp), %rax
	cmpq	$0, 48(%rax)
	jne	.LBB12_713
.LBB12_714:
	movq	736(%rbp), %rax
	cmpq	$0, 72(%rax)
	jne	.LBB12_715
.LBB12_716:
	movq	736(%rbp), %rax
	cmpq	$0, 96(%rax)
	jne	.LBB12_717
.LBB12_718:
	movq	736(%rbp), %rax
	cmpq	$0, 120(%rax)
	jne	.LBB12_719
.LBB12_720:
	movq	736(%rbp), %rax
	cmpq	$0, 144(%rax)
	jne	.LBB12_721
.LBB12_722:
	cmpq	$0, (%rbx)
	je	.LBB12_724
.LBB12_723:
	movq	(%rdi), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
.LBB12_724:
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	736(%rbp), %r8
	callq	*__imp_HeapFree(%rip)
	movaps	144(%rsp), %xmm6
	movaps	128(%rsp), %xmm7
	movaps	112(%rsp), %xmm8
	movaps	96(%rsp), %xmm9
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
.LBB12_709:
	movq	736(%rbp), %rax
	movq	8(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	movq	736(%rbp), %rax
	cmpq	$0, 24(%rax)
	je	.LBB12_712
.LBB12_711:
	movq	736(%rbp), %rax
	movq	32(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	movq	736(%rbp), %rax
	cmpq	$0, 48(%rax)
	je	.LBB12_714
.LBB12_713:
	movq	736(%rbp), %rax
	movq	56(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	movq	736(%rbp), %rax
	cmpq	$0, 72(%rax)
	je	.LBB12_716
.LBB12_715:
	movq	736(%rbp), %rax
	movq	80(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	movq	736(%rbp), %rax
	cmpq	$0, 96(%rax)
	je	.LBB12_718
.LBB12_717:
	movq	736(%rbp), %rax
	movq	104(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	movq	736(%rbp), %rax
	cmpq	$0, 120(%rax)
	je	.LBB12_720
.LBB12_719:
	movq	736(%rbp), %rax
	movq	128(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	movq	736(%rbp), %rax
	cmpq	$0, 144(%rax)
	je	.LBB12_722
.LBB12_721:
	movq	736(%rbp), %rax
	movq	152(%rax), %rsi
	callq	*__imp_GetProcessHeap(%rip)
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	cmpq	$0, (%rbx)
	jne	.LBB12_723
	jmp	.LBB12_724
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
	leaq	192(%rbp), %rcx
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
	movdqa	%xmm6, 144(%rsp)
	.seh_savexmm %xmm6, 144
	.seh_endprologue
	leaq	480(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs2i4to50FHNk_9prototype4CaseEBD_
	movb	$0, 687(%rbp)
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
	movb	$0, 686(%rbp)
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
	movb	$0, 685(%rbp)
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
	movb	$0, 684(%rbp)
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
	.def	"?dtor$748@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$748@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$748@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_748:
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
	movb	$0, 683(%rbp)
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
	.def	"?dtor$749@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$749@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$749@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_749:
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
	movb	$0, 682(%rbp)
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
	.def	"?dtor$750@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$750@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$750@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_750:
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
	.def	"?dtor$751@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$751@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA":
.seh_proc "?dtor$751@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"
.LBB12_751:
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
	.long	.LBB12_188-.LJTI12_0
	.long	.LBB12_182-.LJTI12_0
	.long	.LBB12_183-.LJTI12_0
	.long	.LBB12_184-.LJTI12_0
	.long	.LBB12_187-.LJTI12_0
	.long	.LBB12_185-.LJTI12_0
	.long	.LBB12_186-.LJTI12_0
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
	.long	69
	.long	$ip2state$_RNvCs2i4to50FHNk_9prototype4main@IMGREL
	.long	872
	.long	0
	.long	1
$stateUnwindMap$_RNvCs2i4to50FHNk_9prototype4main:
	.long	-1
	.long	"?dtor$741@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	-1
	.long	"?dtor$29@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	1
	.long	"?dtor$238@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	2
	.long	"?dtor$751@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	1
	.long	"?dtor$217@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	4
	.long	"?dtor$750@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	1
	.long	"?dtor$209@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	6
	.long	"?dtor$749@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	1
	.long	"?dtor$193@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	8
	.long	"?dtor$748@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	1
	.long	"?dtor$139@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	10
	.long	"?dtor$747@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	1
	.long	"?dtor$131@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	12
	.long	"?dtor$743@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	1
	.long	"?dtor$126@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	14
	.long	"?dtor$744@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	1
	.long	"?dtor$121@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	16
	.long	"?dtor$745@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	1
	.long	"?dtor$116@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	18
	.long	"?dtor$746@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	1
	.long	"?dtor$46@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	20
	.long	"?dtor$742@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	-1
	.long	"?dtor$265@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	22
	.long	"?dtor$464@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	23
	.long	"?dtor$459@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	24
	.long	"?dtor$458@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	23
	.long	"?dtor$442@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	22
	.long	"?dtor$406@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	27
	.long	"?dtor$405@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	22
	.long	"?dtor$312@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	29
	.long	"?dtor$315@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	30
	.long	"?dtor$326@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	31
	.long	"?dtor$327@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	32
	.long	"?dtor$328@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	33
	.long	"?dtor$371@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	-1
	.long	"?dtor$480@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	-1
	.long	"?dtor$501@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	-1
	.long	"?dtor$515@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	37
	.long	"?dtor$708@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
	.long	37
	.long	"?dtor$538@?0?_RNvCs2i4to50FHNk_9prototype4main@4HA"@IMGREL
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
	.long	.Ltmp146@IMGREL
	.long	8
	.long	.Ltmp148@IMGREL
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
	.long	.Ltmp150@IMGREL
	.long	1
	.long	.Ltmp42@IMGREL
	.long	10
	.long	.Ltmp52@IMGREL
	.long	1
	.long	.Ltmp58@IMGREL
	.long	4
	.long	.Ltmp59@IMGREL
	.long	-1
	.long	.Ltmp142@IMGREL
	.long	27
	.long	.Ltmp144@IMGREL
	.long	28
	.long	.Ltmp152@IMGREL
	.long	1
	.long	.Ltmp153@IMGREL
	.long	-1
	.long	.Ltmp86@IMGREL
	.long	33
	.long	.Ltmp89@IMGREL
	.long	-1
	.long	.Ltmp114@IMGREL
	.long	22
	.long	.Ltmp115@IMGREL
	.long	-1
	.long	.Ltmp116@IMGREL
	.long	35
	.long	.Ltmp102@IMGREL
	.long	33
	.long	.Ltmp105@IMGREL
	.long	-1
	.long	.Ltmp124@IMGREL
	.long	38
	.long	.Ltmp133@IMGREL
	.long	-1
	.long	.Ltmp36@IMGREL
	.long	12
	.long	.Ltmp20@IMGREL
	.long	14
	.long	.Ltmp26@IMGREL
	.long	16
	.long	.Ltmp32@IMGREL
	.long	18
	.long	.Ltmp90@IMGREL
	.long	33
	.long	.Ltmp100@IMGREL
	.long	34
	.long	.Ltmp66@IMGREL
	.long	6
	.long	.Ltmp68@IMGREL
	.long	23
	.long	.Ltmp140@IMGREL
	.long	22
	.long	.Ltmp112@IMGREL
	.long	29
	.long	.Ltmp110@IMGREL
	.long	30
	.long	.Ltmp108@IMGREL
	.long	31
	.long	.Ltmp106@IMGREL
	.long	32
	.long	.Ltmp74@IMGREL
	.long	24
	.long	.Ltmp84@IMGREL
	.long	22
	.long	.Ltmp80@IMGREL
	.long	23
	.long	.Ltmp98@IMGREL
	.long	33
	.long	.Ltmp99@IMGREL
	.long	-1
	.long	.Ltmp134@IMGREL
	.long	37
	.long	.Ltmp138@IMGREL
	.long	36
	.long	.Ltmp118@IMGREL
	.long	39
	.long	.Ltmp136@IMGREL
	.long	37
	.long	.Ltmp137@IMGREL
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
.Ltmp154:
	callq	_RNvMNtCse0R8cuyqEa_3std4timeNtB2_7Instant3now
	movq	%rax, -56(%rbp)
	movl	%edx, -20(%rbp)
.Ltmp155:
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
.Ltmp160:
	callq	*%rbx
	nop
.Ltmp161:
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
.Ltmp156:
	callq	_RNvMNtCse0R8cuyqEa_3std4timeNtB2_7Instant3now
	nop
.Ltmp157:
	movq	%rax, -16(%rbp)
	movl	%edx, -8(%rbp)
.Ltmp158:
	leaq	-16(%rbp), %rcx
	movq	-56(%rbp), %rdx
	movl	-20(%rbp), %r8d
	callq	_RNvMNtCse0R8cuyqEa_3std4timeNtB2_7Instant22checked_duration_since
	nop
.Ltmp159:
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
	.long	.Ltmp154@IMGREL
	.long	0
	.long	.Ltmp159@IMGREL
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

	.def	d015_baseline_i16;
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
	.section	.text,"xr",one_only,d015_baseline_i16,unique,26
	.globl	d015_baseline_i16
	.p2align	4
d015_baseline_i16:
.Lfunc_begin25:
.seh_proc d015_baseline_i16
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

	.def	d015_baseline_u16;
	.scl	2;
	.type	32;
	.endef
	.globl	__real@477fff00
	.section	.rdata,"dr",discard,__real@477fff00
	.p2align	2, 0x0
__real@477fff00:
	.long	0x477fff00
	.section	.text,"xr",one_only,d015_baseline_u16,unique,27
	.globl	d015_baseline_u16
	.p2align	4
d015_baseline_u16:
.Lfunc_begin26:
.seh_proc d015_baseline_u16
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

	.def	d015_candidate_i16;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,d015_candidate_i16,unique,28
	.globl	d015_candidate_i16
	.p2align	4
d015_candidate_i16:
.Lfunc_begin27:
.seh_proc d015_candidate_i16
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
	movq	_RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache5CACHE(%rip), %rax
	testq	%rax, %rax
	je	.LBB27_1
	testl	$1024, %eax
	jne	.LBB27_23
.LBB27_3:
	testq	%rdx, %rdx
	je	.LBB27_4
	leaq	(,%rdx,4), %rcx
	addq	$-4, %rcx
	xorps	%xmm0, %xmm0
	movq	%rbx, %rax
	cmpq	$28, %rcx
	jb	.LBB27_9
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
.LBB27_7:
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
	jne	.LBB27_7
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
	je	.LBB27_11
.LBB27_9:
	leaq	(%rbx,%rdx,4), %rcx
	movaps	__xmm@7fffffff7fffffff7fffffff7fffffff(%rip), %xmm1
	movaps	%xmm0, %xmm2
	.p2align	4
.LBB27_10:
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
	jne	.LBB27_10
	jmp	.LBB27_11
.LBB27_4:
	xorps	%xmm0, %xmm0
.LBB27_11:
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
	je	.LBB27_12
	cmpq	%rsi, %rdx
	cmovbq	%rdx, %rsi
	testq	%rsi, %rsi
	je	.LBB27_22
	movss	__real@46fffe00(%rip), %xmm11
	movaps	%xmm11, %xmm12
	movaps	%xmm0, %xmm10
	divss	%xmm0, %xmm12
	cmpq	$4, %rsi
	jae	.LBB27_18
	xorl	%r14d, %r14d
	jmp	.LBB27_16
.LBB27_12:
	addq	%rsi, %rsi
	movq	%rdi, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	memset
	xorps	%xmm0, %xmm0
	jmp	.LBB27_22
.LBB27_18:
	movabsq	$2305843009213693948, %r14
	andq	%rsi, %r14
	movaps	%xmm12, %xmm13
	shufps	$0, %xmm12, %xmm13
	leaq	(%rsi,%rsi), %r15
	andq	$-8, %r15
	xorl	%r12d, %r12d
	movss	__real@c7000000(%rip), %xmm14
	.p2align	4
.LBB27_19:
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
	jne	.LBB27_19
	cmpq	%r14, %rsi
	je	.LBB27_21
.LBB27_16:
	movss	__real@c7000000(%rip), %xmm6
	.p2align	4
.LBB27_17:
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
	jne	.LBB27_17
.LBB27_21:
	movaps	%xmm10, %xmm0
.LBB27_22:
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
.LBB27_1:
	movq	%rdx, %r14
	callq	_RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache21detect_and_initialize
	movq	%r14, %rdx
	testl	$1024, %eax
	je	.LBB27_3
.LBB27_23:
	movq	%rbx, %rcx
	movq	%rdi, %r8
	movq	%rsi, %r9
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
	jmp	d015_sse41_i16
.Lfunc_end27:
	.seh_endproc

	.def	d015_candidate_u16;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,d015_candidate_u16,unique,29
	.globl	d015_candidate_u16
	.p2align	4
d015_candidate_u16:
.Lfunc_begin28:
.seh_proc d015_candidate_u16
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
	movq	_RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache5CACHE(%rip), %rax
	testq	%rax, %rax
	je	.LBB28_1
	testl	$1024, %eax
	jne	.LBB28_23
.LBB28_3:
	testq	%rdx, %rdx
	je	.LBB28_4
	leaq	(,%rdx,4), %rcx
	addq	$-4, %rcx
	xorps	%xmm0, %xmm0
	movq	%rbx, %rax
	cmpq	$28, %rcx
	jb	.LBB28_9
	shrq	$2, %rcx
	incq	%rcx
	movq	%rcx, %r8
	andq	$-8, %r8
	leaq	(%rbx,%r8,4), %rax
	xorps	%xmm0, %xmm0
	xorl	%r9d, %r9d
	xorps	%xmm1, %xmm1
	.p2align	4
.LBB28_7:
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
	jne	.LBB28_7
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
	je	.LBB28_11
.LBB28_9:
	leaq	(%rbx,%rdx,4), %rcx
	movaps	%xmm0, %xmm1
	.p2align	4
.LBB28_10:
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
	jne	.LBB28_10
	jmp	.LBB28_11
.LBB28_4:
	xorps	%xmm0, %xmm0
.LBB28_11:
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
	je	.LBB28_12
	cmpq	%rsi, %rdx
	cmovbq	%rdx, %rsi
	testq	%rsi, %rsi
	je	.LBB28_22
	movss	__real@477fff00(%rip), %xmm11
	movaps	%xmm11, %xmm12
	movaps	%xmm0, %xmm10
	divss	%xmm0, %xmm12
	cmpq	$4, %rsi
	jae	.LBB28_18
	xorl	%r14d, %r14d
	jmp	.LBB28_16
.LBB28_12:
	addq	%rsi, %rsi
	movq	%rdi, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	memset
	xorps	%xmm0, %xmm0
	jmp	.LBB28_22
.LBB28_18:
	movabsq	$2305843009213693948, %r14
	andq	%rsi, %r14
	movaps	%xmm12, %xmm13
	shufps	$0, %xmm12, %xmm13
	leaq	(%rsi,%rsi), %r15
	andq	$-8, %r15
	xorl	%r12d, %r12d
	xorps	%xmm14, %xmm14
	.p2align	4
.LBB28_19:
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
	jne	.LBB28_19
	cmpq	%r14, %rsi
	je	.LBB28_21
.LBB28_16:
	xorps	%xmm6, %xmm6
	.p2align	4
.LBB28_17:
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
	jne	.LBB28_17
.LBB28_21:
	movaps	%xmm10, %xmm0
.LBB28_22:
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
.LBB28_1:
	movq	%rdx, %r14
	callq	_RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache21detect_and_initialize
	movq	%r14, %rdx
	testl	$1024, %eax
	je	.LBB28_3
.LBB28_23:
	movq	%rbx, %rcx
	movq	%rdi, %r8
	movq	%rsi, %r9
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
	jmp	d015_sse41_u16
.Lfunc_end28:
	.seh_endproc

	.def	d015_sse41_i16;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,d015_sse41_i16,unique,30
	.globl	d015_sse41_i16
	.p2align	4
d015_sse41_i16:
.Lfunc_begin29:
.seh_proc d015_sse41_i16
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$96, %rsp
	.seh_stackalloc 96
	movaps	%xmm9, 80(%rsp)
	.seh_savexmm %xmm9, 80
	movaps	%xmm8, 64(%rsp)
	.seh_savexmm %xmm8, 64
	movdqa	%xmm7, 48(%rsp)
	.seh_savexmm %xmm7, 48
	movaps	%xmm6, 32(%rsp)
	.seh_savexmm %xmm6, 32
	.seh_endprologue
	testq	%rdx, %rdx
	je	.LBB29_1
	leaq	(,%rdx,4), %r10
	addq	$-4, %r10
	xorps	%xmm1, %xmm1
	movq	%rcx, %rax
	cmpq	$28, %r10
	jb	.LBB29_6
	shrq	$2, %r10
	incq	%r10
	movq	%r10, %r11
	andq	$-8, %r11
	leaq	(%rcx,%r11,4), %rax
	xorps	%xmm2, %xmm2
	xorl	%esi, %esi
	movaps	__xmm@7fffffff7fffffff7fffffff7fffffff(%rip), %xmm1
	xorps	%xmm3, %xmm3
	.p2align	4
.LBB29_4:
	movaps	%xmm3, %xmm4
	movaps	%xmm2, %xmm5
	movups	(%rcx,%rsi,4), %xmm0
	movups	16(%rcx,%rsi,4), %xmm6
	andps	%xmm1, %xmm0
	andps	%xmm1, %xmm6
	maxps	%xmm0, %xmm2
	movaps	%xmm2, %xmm0
	cmpunordps	%xmm2, %xmm0
	blendvps	%xmm0, %xmm5, %xmm2
	maxps	%xmm6, %xmm3
	movaps	%xmm3, %xmm0
	cmpunordps	%xmm3, %xmm0
	blendvps	%xmm0, %xmm4, %xmm3
	addq	$8, %rsi
	cmpq	%rsi, %r11
	jne	.LBB29_4
	movaps	%xmm2, %xmm1
	maxps	%xmm3, %xmm1
	movaps	%xmm1, %xmm0
	cmpunordps	%xmm1, %xmm0
	blendvps	%xmm0, %xmm2, %xmm1
	movaps	%xmm1, %xmm4
	movaps	%xmm1, %xmm5
	unpckhpd	%xmm1, %xmm5
	movshdup	%xmm1, %xmm3
	movaps	%xmm3, %xmm2
	maxss	%xmm1, %xmm2
	cmpunordss	%xmm1, %xmm1
	movaps	%xmm1, %xmm0
	blendvps	%xmm0, %xmm3, %xmm2
	movaps	%xmm5, %xmm3
	maxss	%xmm2, %xmm3
	cmpunordss	%xmm2, %xmm2
	movaps	%xmm2, %xmm0
	blendvps	%xmm0, %xmm5, %xmm3
	shufps	$255, %xmm4, %xmm4
	movaps	%xmm4, %xmm1
	maxss	%xmm3, %xmm1
	cmpunordss	%xmm3, %xmm3
	movaps	%xmm3, %xmm0
	blendvps	%xmm0, %xmm4, %xmm1
	cmpq	%r11, %r10
	je	.LBB29_8
.LBB29_6:
	leaq	(%rcx,%rdx,4), %r10
	movaps	__xmm@7fffffff7fffffff7fffffff7fffffff(%rip), %xmm2
	movaps	%xmm1, %xmm3
	.p2align	4
.LBB29_7:
	movss	(%rax), %xmm0
	addq	$4, %rax
	andps	%xmm2, %xmm0
	maxss	%xmm0, %xmm1
	movaps	%xmm1, %xmm0
	cmpunordss	%xmm1, %xmm0
	blendvps	%xmm0, %xmm3, %xmm1
	movaps	%xmm1, %xmm3
	cmpq	%r10, %rax
	jne	.LBB29_7
	jmp	.LBB29_8
.LBB29_1:
	xorps	%xmm1, %xmm1
.LBB29_8:
	movd	%xmm1, %eax
	testl	%eax, %eax
	setns	%r10b
	movl	%eax, %r11d
	andl	$2147483647, %r11d
	addl	$-8388608, %r11d
	cmpl	$2130706432, %r11d
	setb	%r11b
	andb	%r10b, %r11b
	decl	%eax
	cmpl	$8388607, %eax
	setb	%al
	orb	%r11b, %al
	je	.LBB29_9
	cmpq	%r9, %rdx
	cmovbq	%rdx, %r9
	testq	%r9, %r9
	je	.LBB29_18
	movss	__real@46fffe00(%rip), %xmm0
	movaps	%xmm0, %xmm2
	divss	%xmm1, %xmm2
	cmpq	$8, %r9
	jae	.LBB29_13
	xorl	%eax, %eax
	jmp	.LBB29_16
.LBB29_9:
	addq	%r9, %r9
	movq	%r8, %rcx
	xorl	%edx, %edx
	movq	%r9, %r8
	callq	memset
	xorps	%xmm1, %xmm1
	jmp	.LBB29_18
.LBB29_13:
	movabsq	$2305843009213693944, %rax
	andq	%r9, %rax
	movaps	%xmm2, %xmm3
	shufps	$0, %xmm2, %xmm3
	leaq	(%r9,%r9), %rdx
	andq	$-16, %rdx
	xorl	%r10d, %r10d
	movss	__real@c7000000(%rip), %xmm4
	.p2align	4
.LBB29_14:
	movups	(%rcx,%r10,2), %xmm5
	mulps	%xmm3, %xmm5
	roundps	$4, %xmm5, %xmm6
	movshdup	%xmm6, %xmm5
	movaps	%xmm4, %xmm7
	maxss	%xmm5, %xmm7
	movaps	%xmm0, %xmm5
	minss	%xmm7, %xmm5
	cvttss2si	%xmm5, %r11d
	movups	16(%rcx,%r10,2), %xmm7
	movaps	%xmm4, %xmm5
	maxss	%xmm6, %xmm5
	movaps	%xmm0, %xmm8
	minss	%xmm5, %xmm8
	cvttss2si	%xmm8, %esi
	movd	%esi, %xmm5
	pinsrw	$1, %r11d, %xmm5
	movaps	%xmm6, %xmm8
	unpckhpd	%xmm6, %xmm8
	movaps	%xmm4, %xmm9
	maxss	%xmm8, %xmm9
	movaps	%xmm0, %xmm8
	minss	%xmm9, %xmm8
	cvttss2si	%xmm8, %r11d
	pinsrw	$2, %r11d, %xmm5
	mulps	%xmm3, %xmm7
	shufps	$255, %xmm6, %xmm6
	movaps	%xmm4, %xmm8
	maxss	%xmm6, %xmm8
	movaps	%xmm0, %xmm6
	minss	%xmm8, %xmm6
	cvttss2si	%xmm6, %r11d
	roundps	$4, %xmm7, %xmm6
	pinsrw	$3, %r11d, %xmm5
	movshdup	%xmm6, %xmm7
	movaps	%xmm4, %xmm8
	maxss	%xmm7, %xmm8
	movaps	%xmm0, %xmm7
	minss	%xmm8, %xmm7
	cvttss2si	%xmm7, %r11d
	movaps	%xmm4, %xmm7
	maxss	%xmm6, %xmm7
	movaps	%xmm0, %xmm8
	minss	%xmm7, %xmm8
	cvttss2si	%xmm8, %esi
	movd	%esi, %xmm7
	pinsrw	$1, %r11d, %xmm7
	movaps	%xmm6, %xmm8
	unpckhpd	%xmm6, %xmm8
	movaps	%xmm4, %xmm9
	maxss	%xmm8, %xmm9
	movaps	%xmm0, %xmm8
	minss	%xmm9, %xmm8
	cvttss2si	%xmm8, %r11d
	pinsrw	$2, %r11d, %xmm7
	shufps	$255, %xmm6, %xmm6
	movaps	%xmm4, %xmm8
	maxss	%xmm6, %xmm8
	movaps	%xmm0, %xmm6
	minss	%xmm8, %xmm6
	cvttss2si	%xmm6, %r11d
	pinsrw	$3, %r11d, %xmm7
	punpcklqdq	%xmm7, %xmm5
	movdqu	%xmm5, (%r8,%r10)
	addq	$16, %r10
	cmpq	%r10, %rdx
	jne	.LBB29_14
	cmpq	%rax, %r9
	je	.LBB29_18
.LBB29_16:
	movss	__real@c7000000(%rip), %xmm3
	.p2align	4
.LBB29_17:
	movss	(%rcx,%rax,4), %xmm4
	mulss	%xmm2, %xmm4
	roundss	$4, %xmm4, %xmm4
	movaps	%xmm3, %xmm5
	maxss	%xmm4, %xmm5
	movaps	%xmm0, %xmm4
	minss	%xmm5, %xmm4
	cvttss2si	%xmm4, %edx
	movw	%dx, (%r8,%rax,2)
	incq	%rax
	cmpq	%rax, %r9
	jne	.LBB29_17
.LBB29_18:
	movaps	%xmm1, %xmm0
	movaps	32(%rsp), %xmm6
	movaps	48(%rsp), %xmm7
	movaps	64(%rsp), %xmm8
	movaps	80(%rsp), %xmm9
	.seh_startepilogue
	addq	$96, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end29:
	.seh_endproc

	.def	d015_sse41_u16;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,d015_sse41_u16,unique,31
	.globl	d015_sse41_u16
	.p2align	4
d015_sse41_u16:
.Lfunc_begin30:
.seh_proc d015_sse41_u16
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$96, %rsp
	.seh_stackalloc 96
	movaps	%xmm9, 80(%rsp)
	.seh_savexmm %xmm9, 80
	movaps	%xmm8, 64(%rsp)
	.seh_savexmm %xmm8, 64
	movdqa	%xmm7, 48(%rsp)
	.seh_savexmm %xmm7, 48
	movaps	%xmm6, 32(%rsp)
	.seh_savexmm %xmm6, 32
	.seh_endprologue
	testq	%rdx, %rdx
	je	.LBB30_1
	leaq	(,%rdx,4), %r10
	addq	$-4, %r10
	xorps	%xmm1, %xmm1
	movq	%rcx, %rax
	cmpq	$28, %r10
	jb	.LBB30_6
	shrq	$2, %r10
	incq	%r10
	movq	%r10, %r11
	andq	$-8, %r11
	leaq	(%rcx,%r11,4), %rax
	xorps	%xmm2, %xmm2
	xorl	%esi, %esi
	xorps	%xmm3, %xmm3
	.p2align	4
.LBB30_4:
	movaps	%xmm3, %xmm1
	movaps	%xmm2, %xmm4
	movups	(%rcx,%rsi,4), %xmm0
	movups	16(%rcx,%rsi,4), %xmm5
	maxps	%xmm0, %xmm2
	movaps	%xmm2, %xmm0
	cmpunordps	%xmm2, %xmm0
	blendvps	%xmm0, %xmm4, %xmm2
	maxps	%xmm5, %xmm3
	movaps	%xmm3, %xmm0
	cmpunordps	%xmm3, %xmm0
	blendvps	%xmm0, %xmm1, %xmm3
	addq	$8, %rsi
	cmpq	%rsi, %r11
	jne	.LBB30_4
	movaps	%xmm2, %xmm1
	maxps	%xmm3, %xmm1
	movaps	%xmm1, %xmm0
	cmpunordps	%xmm1, %xmm0
	blendvps	%xmm0, %xmm2, %xmm1
	movaps	%xmm1, %xmm4
	movaps	%xmm1, %xmm5
	unpckhpd	%xmm1, %xmm5
	movshdup	%xmm1, %xmm3
	movaps	%xmm3, %xmm2
	maxss	%xmm1, %xmm2
	cmpunordss	%xmm1, %xmm1
	movaps	%xmm1, %xmm0
	blendvps	%xmm0, %xmm3, %xmm2
	movaps	%xmm5, %xmm3
	maxss	%xmm2, %xmm3
	cmpunordss	%xmm2, %xmm2
	movaps	%xmm2, %xmm0
	blendvps	%xmm0, %xmm5, %xmm3
	shufps	$255, %xmm4, %xmm4
	movaps	%xmm4, %xmm1
	maxss	%xmm3, %xmm1
	cmpunordss	%xmm3, %xmm3
	movaps	%xmm3, %xmm0
	blendvps	%xmm0, %xmm4, %xmm1
	cmpq	%r11, %r10
	je	.LBB30_8
.LBB30_6:
	leaq	(%rcx,%rdx,4), %r10
	movaps	%xmm1, %xmm2
	.p2align	4
.LBB30_7:
	maxss	(%rax), %xmm1
	addq	$4, %rax
	movaps	%xmm1, %xmm0
	cmpunordss	%xmm1, %xmm0
	blendvps	%xmm0, %xmm2, %xmm1
	movaps	%xmm1, %xmm2
	cmpq	%r10, %rax
	jne	.LBB30_7
	jmp	.LBB30_8
.LBB30_1:
	xorps	%xmm1, %xmm1
.LBB30_8:
	movd	%xmm1, %eax
	testl	%eax, %eax
	setns	%r10b
	movl	%eax, %r11d
	andl	$2147483647, %r11d
	addl	$-8388608, %r11d
	cmpl	$2130706432, %r11d
	setb	%r11b
	andb	%r10b, %r11b
	decl	%eax
	cmpl	$8388607, %eax
	setb	%al
	orb	%r11b, %al
	je	.LBB30_9
	cmpq	%r9, %rdx
	cmovbq	%rdx, %r9
	testq	%r9, %r9
	je	.LBB30_18
	movss	__real@477fff00(%rip), %xmm0
	movaps	%xmm0, %xmm2
	divss	%xmm1, %xmm2
	cmpq	$8, %r9
	jae	.LBB30_13
	xorl	%eax, %eax
	jmp	.LBB30_16
.LBB30_9:
	addq	%r9, %r9
	movq	%r8, %rcx
	xorl	%edx, %edx
	movq	%r9, %r8
	callq	memset
	xorps	%xmm1, %xmm1
	jmp	.LBB30_18
.LBB30_13:
	movabsq	$2305843009213693944, %rax
	andq	%r9, %rax
	movaps	%xmm2, %xmm3
	shufps	$0, %xmm2, %xmm3
	leaq	(%r9,%r9), %rdx
	andq	$-16, %rdx
	xorl	%r10d, %r10d
	xorps	%xmm4, %xmm4
	.p2align	4
.LBB30_14:
	movups	(%rcx,%r10,2), %xmm5
	movups	16(%rcx,%r10,2), %xmm6
	maxps	%xmm4, %xmm5
	mulps	%xmm3, %xmm5
	roundps	$4, %xmm5, %xmm7
	movshdup	%xmm7, %xmm5
	xorps	%xmm8, %xmm8
	maxss	%xmm5, %xmm8
	movaps	%xmm0, %xmm5
	minss	%xmm8, %xmm5
	cvttss2si	%xmm5, %r11d
	maxps	%xmm4, %xmm6
	xorps	%xmm5, %xmm5
	maxss	%xmm7, %xmm5
	movaps	%xmm0, %xmm8
	minss	%xmm5, %xmm8
	cvttss2si	%xmm8, %esi
	movd	%esi, %xmm5
	pinsrw	$1, %r11d, %xmm5
	movaps	%xmm7, %xmm8
	unpckhpd	%xmm7, %xmm8
	xorps	%xmm9, %xmm9
	maxss	%xmm8, %xmm9
	movaps	%xmm0, %xmm8
	minss	%xmm9, %xmm8
	cvttss2si	%xmm8, %r11d
	pinsrw	$2, %r11d, %xmm5
	mulps	%xmm3, %xmm6
	shufps	$255, %xmm7, %xmm7
	xorps	%xmm8, %xmm8
	maxss	%xmm7, %xmm8
	movaps	%xmm0, %xmm7
	minss	%xmm8, %xmm7
	cvttss2si	%xmm7, %r11d
	roundps	$4, %xmm6, %xmm6
	pinsrw	$3, %r11d, %xmm5
	movshdup	%xmm6, %xmm7
	xorps	%xmm8, %xmm8
	maxss	%xmm7, %xmm8
	movaps	%xmm0, %xmm7
	minss	%xmm8, %xmm7
	cvttss2si	%xmm7, %r11d
	xorps	%xmm7, %xmm7
	maxss	%xmm6, %xmm7
	movaps	%xmm0, %xmm8
	minss	%xmm7, %xmm8
	cvttss2si	%xmm8, %esi
	movd	%esi, %xmm7
	pinsrw	$1, %r11d, %xmm7
	movaps	%xmm6, %xmm8
	unpckhpd	%xmm6, %xmm8
	xorps	%xmm9, %xmm9
	maxss	%xmm8, %xmm9
	movaps	%xmm0, %xmm8
	minss	%xmm9, %xmm8
	cvttss2si	%xmm8, %r11d
	pinsrw	$2, %r11d, %xmm7
	shufps	$255, %xmm6, %xmm6
	xorps	%xmm8, %xmm8
	maxss	%xmm6, %xmm8
	movaps	%xmm0, %xmm6
	minss	%xmm8, %xmm6
	cvttss2si	%xmm6, %r11d
	pinsrw	$3, %r11d, %xmm7
	punpcklqdq	%xmm7, %xmm5
	movdqu	%xmm5, (%r8,%r10)
	addq	$16, %r10
	cmpq	%r10, %rdx
	jne	.LBB30_14
	cmpq	%rax, %r9
	je	.LBB30_18
.LBB30_16:
	xorps	%xmm3, %xmm3
	.p2align	4
.LBB30_17:
	movss	(%rcx,%rax,4), %xmm4
	maxss	%xmm3, %xmm4
	mulss	%xmm2, %xmm4
	roundss	$4, %xmm4, %xmm4
	xorps	%xmm5, %xmm5
	maxss	%xmm4, %xmm5
	movaps	%xmm0, %xmm4
	minss	%xmm5, %xmm4
	cvttss2si	%xmm4, %edx
	movw	%dx, (%r8,%rax,2)
	incq	%rax
	cmpq	%rax, %r9
	jne	.LBB30_17
.LBB30_18:
	movaps	%xmm1, %xmm0
	movaps	32(%rsp), %xmm6
	movaps	48(%rsp), %xmm7
	movaps	64(%rsp), %xmm8
	movaps	80(%rsp), %xmm9
	.seh_startepilogue
	addq	$96, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end30:
	.seh_endproc

	.def	main;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,main,unique,32
	.globl	main
	.p2align	4
main:
.Lfunc_begin31:
.seh_proc main
	subq	$56, %rsp
	.seh_stackalloc 56
	.seh_endprologue
	movq	%rdx, %r9
	movslq	%ecx, %r8
	leaq	_RNvCs2i4to50FHNk_9prototype4main(%rip), %rax
	movq	%rax, 48(%rsp)
	movb	$0, 32(%rsp)
	leaq	anon.d497bd2ae5be347895e1f15ef3d10337.6(%rip), %rdx
	leaq	48(%rsp), %rcx
	callq	_RNvNtCse0R8cuyqEa_3std2rt19lang_start_internal
	nop
	.seh_startepilogue
	addq	$56, %rsp
	.seh_endepilogue
	retq
.Lfunc_end31:
	.seh_endproc

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.0,unique,33
	.p2align	3, 0x0
anon.d497bd2ae5be347895e1f15ef3d10337.0:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRmNtB6_5Debug3fmtCs2i4to50FHNk_9prototype

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.2,unique,34
	.p2align	3, 0x0
anon.d497bd2ae5be347895e1f15ef3d10337.2:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRtNtB6_5Debug3fmtCs2i4to50FHNk_9prototype

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.3,unique,35
	.p2align	3, 0x0
anon.d497bd2ae5be347895e1f15ef3d10337.3:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRINtNtCsfQUUnEvlYZE_5alloc3vec3VecmENtB6_5Debug3fmtCs2i4to50FHNk_9prototype

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.4,unique,36
	.p2align	3, 0x0
anon.d497bd2ae5be347895e1f15ef3d10337.4:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRINtNtCsfQUUnEvlYZE_5alloc3vec3VecsENtB6_5Debug3fmtCs2i4to50FHNk_9prototype

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.5,unique,37
	.p2align	3, 0x0
anon.d497bd2ae5be347895e1f15ef3d10337.5:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRINtNtCsfQUUnEvlYZE_5alloc3vec3VectENtB6_5Debug3fmtCs2i4to50FHNk_9prototype

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.6,unique,38
	.p2align	3, 0x0
anon.d497bd2ae5be347895e1f15ef3d10337.6:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvNtCse0R8cuyqEa_3std2rt10lang_startuE0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableCs2i4to50FHNk_9prototype
	.quad	_RNCINvNtCse0R8cuyqEa_3std2rt10lang_startuE0Cs2i4to50FHNk_9prototype
	.quad	_RNCINvNtCse0R8cuyqEa_3std2rt10lang_startuE0Cs2i4to50FHNk_9prototype

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.7,unique,39
anon.d497bd2ae5be347895e1f15ef3d10337.7:
	.ascii	"positive_zero"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.8,unique,40
anon.d497bd2ae5be347895e1f15ef3d10337.8:
	.ascii	"--proof-only"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.9,unique,41
anon.d497bd2ae5be347895e1f15ef3d10337.9:
	.ascii	"--inject-failure"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.10,unique,42
anon.d497bd2ae5be347895e1f15ef3d10337.10:
	.ascii	"{\"stage\":\"unsupported\",\"sse4_1\":false,\"candidate_executed\":false}\n"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.11,unique,43
anon.d497bd2ae5be347895e1f15ef3d10337.11:
	.ascii	"{\"stage\":\"feature_gate\",\"sse4_1\":true,\"runtime_guarded\":true,\"portable_fallback\":true}\n"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.12,unique,44
anon.d497bd2ae5be347895e1f15ef3d10337.12:
	.ascii	"{\"stage\":\"complete\",\"diagnostic_only\":true,\"end_to_end_claim\":false}\n"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.13,unique,45
anon.d497bd2ae5be347895e1f15ef3d10337.13:
	.ascii	"empty"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.14,unique,46
anon.d497bd2ae5be347895e1f15ef3d10337.14:
	.asciz	"\nsingleton_\303 \000\000i\b\000"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.15,unique,47
	.p2align	3, 0x0
anon.d497bd2ae5be347895e1f15ef3d10337.15:
	.asciz	"\000\000\000\000\000\000\000\000\001\000\000\000\000\000\000\000\002\000\000\000\000\000\000\000\003\000\000\000\000\000\000\000\007\000\000\000\000\000\000\000\017\000\000\000\000\000\000\000\020\000\000\000\000\000\000\000\021\000\000\000\000\000\000\000\037\000\000\000\000\000\000\000 \000\000\000\000\000\000\000!\000\000\000\000\000\000\000?\000\000\000\000\000\000\000@\000\000\000\000\000\000\000A\000\000\000\000\000\000\000\177\000\000\000\000\000\000\000\200\000\000\000\000\000\000\000\201\000\000\000\000\000\000\000\377\000\000\000\000\000\000\000\000\001\000\000\000\000\000\000\001\001\000\000\000\000\000\000\377\001\000\000\000\000\000\000\000\002\000\000\000\000\000\000\001\002\000\000\000\000\000\000\377\003\000\000\000\000\000\000\000\004\000\000\000\000\000\000\001\004\000\000\000\000\000\000\377\017\000\000\000\000\000\000\000\020\000\000\000\000\000\000\001\020\000\000\000\000\000"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.16,unique,48
anon.d497bd2ae5be347895e1f15ef3d10337.16:
	.asciz	"\rsigned_zeros_\300"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.17,unique,49
anon.d497bd2ae5be347895e1f15ef3d10337.17:
	.asciz	"\016special_cycle_\300"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.18,unique,50
anon.d497bd2ae5be347895e1f15ef3d10337.18:
	.asciz	"\ball_nan_\300"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.19,unique,51
anon.d497bd2ae5be347895e1f15ef3d10337.19:
	.asciz	"\rnegative_u16_\300"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.20,unique,52
anon.d497bd2ae5be347895e1f15ef3d10337.20:
	.asciz	"\rmixed_finite_\303 \000\000i\b\000"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.21,unique,53
anon.d497bd2ae5be347895e1f15ef3d10337.21:
	.ascii	"max_finite_and_tiny"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.22,unique,54
anon.d497bd2ae5be347895e1f15ef3d10337.22:
	.asciz	"\007random_\303 \000\000i\004\000\006_mode_\300"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.23,unique,55
anon.d497bd2ae5be347895e1f15ef3d10337.23:
	.asciz	"\nlong_tail_\300"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.24,unique,56
anon.d497bd2ae5be347895e1f15ef3d10337.24:
	.asciz	"\013tiny_scale_\303 \000\000i\b\000"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.25,unique,57
anon.d497bd2ae5be347895e1f15ef3d10337.25:
	.asciz	"\022ties_adjacent_max_\300"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.26,unique,58
anon.d497bd2ae5be347895e1f15ef3d10337.26:
	.asciz	"prototype.rs"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.27,unique,59
anon.d497bd2ae5be347895e1f15ef3d10337.27:
	.asciz	"\ni16 scale \300"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.28,unique,60
	.p2align	3, 0x0
anon.d497bd2ae5be347895e1f15ef3d10337.28:
	.quad	anon.d497bd2ae5be347895e1f15ef3d10337.26
	.asciz	"\f\000\000\000\000\000\000\000R\000\000\000\t\000\000"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.29,unique,61
anon.d497bd2ae5be347895e1f15ef3d10337.29:
	.asciz	"\nu16 scale \300"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.30,unique,62
	.p2align	3, 0x0
anon.d497bd2ae5be347895e1f15ef3d10337.30:
	.quad	anon.d497bd2ae5be347895e1f15ef3d10337.26
	.asciz	"\f\000\000\000\000\000\000\000S\000\000\000\t\000\000"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.31,unique,63
anon.d497bd2ae5be347895e1f15ef3d10337.31:
	.asciz	"\ni16 words \300"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.32,unique,64
	.p2align	3, 0x0
anon.d497bd2ae5be347895e1f15ef3d10337.32:
	.quad	anon.d497bd2ae5be347895e1f15ef3d10337.26
	.asciz	"\f\000\000\000\000\000\000\000T\000\000\000\t\000\000"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.33,unique,65
anon.d497bd2ae5be347895e1f15ef3d10337.33:
	.asciz	"\nu16 words \300"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.34,unique,66
	.p2align	3, 0x0
anon.d497bd2ae5be347895e1f15ef3d10337.34:
	.quad	anon.d497bd2ae5be347895e1f15ef3d10337.26
	.asciz	"\f\000\000\000\000\000\000\000U\000\000\000\t\000\000"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.35,unique,67
anon.d497bd2ae5be347895e1f15ef3d10337.35:
	.asciz	"\013input bits \300"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.36,unique,68
	.p2align	3, 0x0
anon.d497bd2ae5be347895e1f15ef3d10337.36:
	.quad	anon.d497bd2ae5be347895e1f15ef3d10337.26
	.asciz	"\f\000\000\000\000\000\000\000[\000\000\000\t\000\000"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.37,unique,69
	.p2align	1, 0x0
anon.d497bd2ae5be347895e1f15ef3d10337.37:
	.ascii	"Z\245"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.38,unique,70
anon.d497bd2ae5be347895e1f15ef3d10337.38:
	.asciz	"\nu16 guard \300"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.39,unique,71
	.p2align	3, 0x0
anon.d497bd2ae5be347895e1f15ef3d10337.39:
	.quad	anon.d497bd2ae5be347895e1f15ef3d10337.26
	.asciz	"\f\000\000\000\000\000\000\000X\000\000\000\r\000\000"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.40,unique,72
anon.d497bd2ae5be347895e1f15ef3d10337.40:
	.asciz	"\ni16 guard \300"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.41,unique,73
	.p2align	3, 0x0
anon.d497bd2ae5be347895e1f15ef3d10337.41:
	.quad	anon.d497bd2ae5be347895e1f15ef3d10337.26
	.asciz	"\f\000\000\000\000\000\000\000W\000\000\000\r\000\000"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.42,unique,74
	.p2align	3, 0x0
anon.d497bd2ae5be347895e1f15ef3d10337.42:
	.ascii	"\r\360\026\020& \355^"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.43,unique,75
anon.d497bd2ae5be347895e1f15ef3d10337.43:
	.asciz	"+{\"stage\":\"proof\",\"exact\":true,\"d010_cases\":\300\022,\"cases_per_type\":\300\023,\"values_per_type\":\300\024,\"q_words_compared\":\300\027,\"scale_bits_compared\":\300\027,\"guard_words_checked\":\300%,\"input_bits_unchanged\":true,\"seed\":\"\303 \000\000i\020\000\031\",\"case_manifest_fnv64\":\"\303 \000\000i\020\000\021\",\"input_fnv64\":\"\303 \000\000i\020\000\022\",\"output_fnv64\":\"\303 \000\000i\020\000\003\"}\n"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.44,unique,76
anon.d497bd2ae5be347895e1f15ef3d10337.44:
	.asciz	"\rextra_random_\300"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.45,unique,77
	.p2align	3, 0x0
anon.d497bd2ae5be347895e1f15ef3d10337.45:
	.quad	anon.d497bd2ae5be347895e1f15ef3d10337.26
	.asciz	"\f\000\000\000\000\000\000\000+\000\000\000\027\000\000"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.46,unique,78
anon.d497bd2ae5be347895e1f15ef3d10337.46:
	.asciz	"\013lane_tail_n\300\003_at\300\001_\303 \000\000i\b\000"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.47,unique,79
	.p2align	3, 0x0
anon.d497bd2ae5be347895e1f15ef3d10337.47:
	.quad	anon.d497bd2ae5be347895e1f15ef3d10337.26
	.asciz	"\f\000\000\000\000\000\000\000.\000\000\000\027\000\000"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.48,unique,80
anon.d497bd2ae5be347895e1f15ef3d10337.48:
	.asciz	"\fmixed_lane_n\300\003_at\300\001_\303 \000\000i\b\000"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.51,unique,81
anon.d497bd2ae5be347895e1f15ef3d10337.51:
	.ascii	"finite"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.52,unique,82
	.p2align	3, 0x0
anon.d497bd2ae5be347895e1f15ef3d10337.52:
	.quad	anon.d497bd2ae5be347895e1f15ef3d10337.26
	.asciz	"\f\000\000\000\000\000\000\000\177\000\000\000\030\000\000"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.53,unique,83
anon.d497bd2ae5be347895e1f15ef3d10337.53:
	.ascii	"u16"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.54,unique,84
anon.d497bd2ae5be347895e1f15ef3d10337.54:
	.ascii	"i16"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.55,unique,85
anon.d497bd2ae5be347895e1f15ef3d10337.55:
	.ascii	"baseline"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.56,unique,86
anon.d497bd2ae5be347895e1f15ef3d10337.56:
	.ascii	"sse41"

	.section	.rdata,"dr",one_only,anon.d497bd2ae5be347895e1f15ef3d10337.57,unique,87
anon.d497bd2ae5be347895e1f15ef3d10337.57:
	.asciz	"\032{\"stage\":\"timing\",\"type\":\"\300\n\",\"mode\":\"\300\013\",\"length\":\300\b,\"pair\":\300\023,\"candidate_first\":\300\f,\"variant\":\"\300\t\",\"reps\":\300\020,\"ns_per_block\":\305 \000\000p\006\000\002}\n"

	.section	.debug$S,"dr"
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp163-.Ltmp162
.Ltmp162:
	.short	.Ltmp165-.Ltmp164
.Ltmp164:
	.short	4353
	.long	0
	.asciz	"prototype.prototype.1ab0bb7343479e38-cgu.0.rcgu.o"
	.p2align	2, 0x0
.Ltmp165:
	.short	.Ltmp167-.Ltmp166
.Ltmp166:
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
.Ltmp167:
.Ltmp163:
	.p2align	2, 0x0
	.cv_filechecksums
	.cv_stringtable
	.long	241
	.long	.Ltmp169-.Ltmp168
.Ltmp168:
	.short	.Ltmp171-.Ltmp170
.Ltmp170:
	.short	4428
	.long	4099
	.p2align	2, 0x0
.Ltmp171:
.Ltmp169:
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
