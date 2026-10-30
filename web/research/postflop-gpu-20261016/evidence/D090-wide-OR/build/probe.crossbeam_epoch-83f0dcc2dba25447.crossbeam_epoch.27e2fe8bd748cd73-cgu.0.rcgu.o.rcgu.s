	.def	@feat.00;
	.scl	3;
	.type	0;
	.endef
	.globl	@feat.00
@feat.00 = 0
	.file	"crossbeam_epoch.27e2fe8bd748cd73-cgu.0"
	.def	_RINvMs0_NtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync9once_lockINtB6_8OnceLockNtNtBa_9collector9CollectorE10initializeNvMs1_B1b_B19_3newEBa_.llvm.14389155381977926352;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMs0_NtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync9once_lockINtB6_8OnceLockNtNtBa_9collector9CollectorE10initializeNvMs1_B1b_B19_3newEBa_.llvm.14389155381977926352,unique,0
	.globl	_RINvMs0_NtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync9once_lockINtB6_8OnceLockNtNtBa_9collector9CollectorE10initializeNvMs1_B1b_B19_3newEBa_.llvm.14389155381977926352
	.p2align	4
_RINvMs0_NtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync9once_lockINtB6_8OnceLockNtNtBa_9collector9CollectorE10initializeNvMs1_B1b_B19_3newEBa_.llvm.14389155381977926352:
.Lfunc_begin0:
.seh_proc _RINvMs0_NtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync9once_lockINtB6_8OnceLockNtNtBa_9collector9CollectorE10initializeNvMs1_B1b_B19_3newEBa_.llvm.14389155381977926352
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	leaq	_RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default9collector9COLLECTOR.llvm.14389155381977926352(%rip), %rax
	movq	%rax, 48(%rsp)
	movl	_RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default9collector9COLLECTOR.llvm.14389155381977926352+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB0_1
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB0_1:
	leaq	48(%rsp), %rax
	movq	%rax, 56(%rsp)
	leaq	56(%rsp), %rax
	movq	%rax, 64(%rsp)
	leaq	anon.a32227af679a3ead67a5cb195479eba7.1.llvm.14389155381977926352(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default9collector9COLLECTOR.llvm.14389155381977926352+8(%rip), %rcx
	leaq	anon.a32227af679a3ead67a5cb195479eba7.2.llvm.14389155381977926352(%rip), %r9
	leaq	64(%rsp), %r8
	xorl	%edx, %edx
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	nop
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.Lfunc_end0:
	.seh_endproc

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalEEB1i_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalEEB1i_,unique,1
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalEEB1i_:
.Lfunc_begin1:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalEEB1i_
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$80, %rsp
	.seh_stackalloc 80
	leaq	80(%rsp), %rbp
	.seh_setframe %rbp, 80
	.seh_endprologue
	movq	$-2, -8(%rbp)
	movq	%rcx, %rax
	movq	512(%rcx), %rcx
	subq	$-128, %rax
	movq	%rax, -16(%rbp)
	andq	$-8, %rcx
	je	.LBB1_5
	leaq	_RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch5guard11unprotected11UNPROTECTED(%rip), %rsi
	.p2align	4
.LBB1_2:
	movq	(%rcx), %rdi
	movl	%edi, %eax
	andl	$7, %eax
	movq	%rax, -24(%rbp)
	cmpq	$1, %rax
	jne	.LBB1_6
.Ltmp2:
	movq	%rsi, %rdx
	callq	_RNvXs7_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5LocalINtNtNtB7_4sync4list9IsElementBL_E8finalize
	nop
.Ltmp3:
	andq	$-8, %rdi
	movq	%rdi, %rcx
	jne	.LBB1_2
.LBB1_5:
	movq	-16(%rbp), %rcx
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	jmp	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync5queue5QueueNtNtBI_8internal9SealedBagEEBI_
.LBB1_6:
.Ltmp0:
	leaq	anon.a32227af679a3ead67a5cb195479eba7.18(%rip), %rax
	movq	%rax, 40(%rsp)
	leaq	anon.a32227af679a3ead67a5cb195479eba7.16(%rip), %r8
	leaq	-24(%rbp), %rdx
	xorl	%ecx, %ecx
	xorl	%r9d, %r9d
	callq	_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedjjEB4_
	nop
.Ltmp1:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalEEB1i_@IMGREL
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalEEB1i_,unique,1
	.seh_endproc
	.def	"?dtor$8@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalEEB1i_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$8@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalEEB1i_@4HA":
.seh_proc "?dtor$8@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalEEB1i_@4HA"
.LBB1_8:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$48, %rsp
	.seh_stackalloc 48
	leaq	80(%rdx), %rbp
	.seh_endprologue
	movq	-16(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync5queue5QueueNtNtBI_8internal9SealedBagEEBI_
	nop
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end1:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalEEB1i_,unique,1
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalEEB1i_,unique,0
	.p2align	2, 0x0
$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalEEB1i_:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalEEB1i_@IMGREL
	.long	0
	.long	0
	.long	5
	.long	$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalEEB1i_@IMGREL
	.long	72
	.long	0
	.long	1
$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalEEB1i_:
	.long	-1
	.long	"?dtor$8@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalEEB1i_@4HA"@IMGREL
$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalEEB1i_:
	.long	.Lfunc_begin1@IMGREL
	.long	-1
	.long	.Ltmp2@IMGREL
	.long	0
	.long	.Ltmp3@IMGREL
	.long	-1
	.long	.Ltmp0@IMGREL
	.long	0
	.long	.Ltmp1@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalEEB1i_,unique,1

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync4list4ListNtNtBI_8internal5LocalEEBI_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync4list4ListNtNtBI_8internal5LocalEEBI_,unique,2
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync4list4ListNtNtBI_8internal5LocalEEBI_:
.Lfunc_begin2:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync4list4ListNtNtBI_8internal5LocalEEBI_
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$56, %rsp
	.seh_stackalloc 56
	.seh_endprologue
	movq	(%rcx), %rcx
	andq	$-8, %rcx
	je	.LBB2_4
	leaq	_RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch5guard11unprotected11UNPROTECTED(%rip), %rsi
	.p2align	4
.LBB2_2:
	movq	(%rcx), %rdi
	movl	%edi, %eax
	andl	$7, %eax
	movq	%rax, 48(%rsp)
	cmpq	$1, %rax
	jne	.LBB2_5
	movq	%rsi, %rdx
	callq	_RNvXs7_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5LocalINtNtNtB7_4sync4list9IsElementBL_E8finalize
	andq	$-8, %rdi
	movq	%rdi, %rcx
	jne	.LBB2_2
.LBB2_4:
	.seh_startepilogue
	addq	$56, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB2_5:
	leaq	anon.a32227af679a3ead67a5cb195479eba7.18(%rip), %rax
	movq	%rax, 40(%rsp)
	leaq	anon.a32227af679a3ead67a5cb195479eba7.16(%rip), %r8
	leaq	48(%rsp), %rdx
	xorl	%ecx, %ecx
	xorl	%r9d, %r9d
	callq	_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedjjEB4_
	ud2
.Lfunc_end2:
	.seh_endproc

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync5queue5QueueNtNtBI_8internal9SealedBagEEBI_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync5queue5QueueNtNtBI_8internal9SealedBagEEBI_,unique,3
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync5queue5QueueNtNtBI_8internal9SealedBagEEBI_:
.Lfunc_begin3:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync5queue5QueueNtNtBI_8internal9SealedBagEEBI_
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
	subq	$2128, %rsp
	.seh_stackalloc 2128
	.seh_endprologue
	movq	%rcx, %rsi
	movq	(%rcx), %rdx
	movq	%rdx, %rcx
	andq	$-8, %rcx
	movq	2064(%rcx), %r8
	movq	%r8, %r14
	andq	$-8, %r14
	je	.LBB3_4
	leaq	72(%rsp), %rdi
	leaq	40(%rsp), %rbx
	jmp	.LBB3_2
	.p2align	4
.LBB3_3:
	movq	(%rsi), %rdx
	movq	%rdx, %rcx
	andq	$-8, %rcx
	movq	2064(%rcx), %r8
	movq	%r8, %r14
	andq	$-8, %r14
	je	.LBB3_4
.LBB3_2:
	movq	%rdx, %rax
	lock		cmpxchgq	%r8, (%rsi)
	jne	.LBB3_3
	movq	128(%rsi), %rax
	cmpq	%rax, %rdx
	jne	.LBB3_6
	movq	%rdx, %rax
	lock		cmpxchgq	%r8, 128(%rsi)
.LBB3_6:
	callq	mi_free
	movq	(%r14), %r15
	addq	$8, %r14
	movq	%r15, 64(%rsp)
	movl	$2056, %r8d
	movq	%rdi, %rcx
	movq	%r14, %rdx
	callq	memcpy
	testq	%r15, %r15
	je	.LBB3_4
	movq	2112(%rsp), %r14
	cmpq	$65, %r14
	jae	.LBB3_8
	testq	%r14, %r14
	je	.LBB3_3
	shlq	$5, %r14
	xorl	%r15d, %r15d
	.p2align	4
.LBB3_12:
	movups	64(%rsp,%r15), %xmm0
	movups	80(%rsp,%r15), %xmm1
	movaps	%xmm1, 48(%rsp)
	movaps	%xmm0, 32(%rsp)
	movups	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352(%rip), %xmm0
	movups	%xmm0, 64(%rsp,%r15)
	movups	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352+16(%rip), %xmm0
	movups	%xmm0, 80(%rsp,%r15)
	movq	%rbx, %rcx
	callq	*32(%rsp)
	addq	$32, %r15
	cmpq	%r15, %r14
	jne	.LBB3_12
	jmp	.LBB3_3
.LBB3_4:
	movq	(%rsi), %rcx
	andq	$-8, %rcx
	callq	mi_free
	nop
	.seh_startepilogue
	addq	$2128, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	.seh_endepilogue
	retq
.LBB3_8:
	leaq	anon.a32227af679a3ead67a5cb195479eba7.15.llvm.14389155381977926352(%rip), %r9
	movl	$64, %r8d
	xorl	%ecx, %ecx
	movq	%r14, %rdx
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	ud2
.Lfunc_end3:
	.seh_endproc

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal5LocalEBF_.llvm.14389155381977926352;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal5LocalEBF_.llvm.14389155381977926352,unique,4
	.globl	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal5LocalEBF_.llvm.14389155381977926352
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal5LocalEBF_.llvm.14389155381977926352:
.Lfunc_begin4:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal5LocalEBF_.llvm.14389155381977926352
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
	movaps	%xmm7, 80(%rsp)
	.seh_savexmm %xmm7, 80
	movaps	%xmm6, 64(%rsp)
	.seh_savexmm %xmm6, 64
	.seh_endprologue
	movq	2064(%rcx), %rsi
	cmpq	$65, %rsi
	jae	.LBB4_5
	testq	%rsi, %rsi
	je	.LBB4_4
	movq	%rcx, %rdi
	addq	$16, %rdi
	shlq	$5, %rsi
	leaq	40(%rsp), %rbx
	xorl	%r14d, %r14d
	movups	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352(%rip), %xmm6
	movups	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352+16(%rip), %xmm7
	.p2align	4
.LBB4_3:
	movups	(%rdi,%r14), %xmm0
	movups	16(%rdi,%r14), %xmm1
	movaps	%xmm1, 48(%rsp)
	movaps	%xmm0, 32(%rsp)
	movups	%xmm6, (%rdi,%r14)
	movups	%xmm7, 16(%rdi,%r14)
	movq	%rbx, %rcx
	callq	*32(%rsp)
	addq	$32, %r14
	cmpq	%r14, %rsi
	jne	.LBB4_3
.LBB4_4:
	movaps	64(%rsp), %xmm6
	movaps	80(%rsp), %xmm7
	.seh_startepilogue
	addq	$104, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB4_5:
	leaq	anon.a32227af679a3ead67a5cb195479eba7.15.llvm.14389155381977926352(%rip), %r9
	movl	$64, %r8d
	xorl	%ecx, %ecx
	movq	%rsi, %rdx
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	ud2
.Lfunc_end4:
	.seh_endproc

	.def	_RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCINvB1f_13defer_destroyINtNtNtB9_4sync5queue4NodeNtNtB9_8internal9SealedBagEE0INtNtB9_6atomic5OwnedB2i_EE0EB9_.llvm.14389155381977926352;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCINvB1f_13defer_destroyINtNtNtB9_4sync5queue4NodeNtNtB9_8internal9SealedBagEE0INtNtB9_6atomic5OwnedB2i_EE0EB9_.llvm.14389155381977926352,unique,5
	.globl	_RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCINvB1f_13defer_destroyINtNtNtB9_4sync5queue4NodeNtNtB9_8internal9SealedBagEE0INtNtB9_6atomic5OwnedB2i_EE0EB9_.llvm.14389155381977926352
	.p2align	4
_RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCINvB1f_13defer_destroyINtNtNtB9_4sync5queue4NodeNtNtB9_8internal9SealedBagEE0INtNtB9_6atomic5OwnedB2i_EE0EB9_.llvm.14389155381977926352:
.Lfunc_begin5:
	movq	(%rcx), %rcx
	andq	$-8, %rcx
	jmp	mi_free
.Lfunc_end5:

	.def	_RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCINvB1f_13defer_destroyNtNtB9_8internal5LocalE0INtNtB9_6atomic5OwnedB2i_EE0EB9_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCINvB1f_13defer_destroyNtNtB9_8internal5LocalE0INtNtB9_6atomic5OwnedB2i_EE0EB9_,unique,6
	.p2align	4
_RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCINvB1f_13defer_destroyNtNtB9_8internal5LocalE0INtNtB9_6atomic5OwnedB2i_EE0EB9_:
.Lfunc_begin6:
.seh_proc _RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCINvB1f_13defer_destroyNtNtB9_8internal5LocalE0INtNtB9_6atomic5OwnedB2i_EE0EB9_
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
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
	movaps	%xmm7, -16(%rbp)
	.seh_savexmm %xmm7, 96
	movaps	%xmm6, -32(%rbp)
	.seh_savexmm %xmm6, 80
	.seh_endprologue
	movq	$-2, -40(%rbp)
	movq	(%rcx), %rax
	andq	$-128, %rax
	movq	%rax, -48(%rbp)
	movq	2064(%rax), %rsi
	cmpq	$65, %rsi
	jae	.LBB6_1
	testq	%rsi, %rsi
	je	.LBB6_7
	movq	-48(%rbp), %rax
	leaq	16(%rax), %rbx
	shlq	$5, %rsi
	addq	%rbx, %rsi
	leaq	-72(%rbp), %rdi
	movups	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352(%rip), %xmm6
	movups	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352+16(%rip), %xmm7
	.p2align	4
.LBB6_5:
	movups	(%rbx), %xmm0
	movups	16(%rbx), %xmm1
	movaps	%xmm1, -64(%rbp)
	movaps	%xmm0, -80(%rbp)
	movups	%xmm6, (%rbx)
	movups	%xmm7, 16(%rbx)
.Ltmp6:
	movq	%rdi, %rcx
	callq	*-80(%rbp)
	nop
.Ltmp7:
	addq	$32, %rbx
	cmpq	%rsi, %rbx
	jne	.LBB6_5
.LBB6_7:
	movq	-48(%rbp), %rcx
	callq	mi_free
	movaps	-32(%rbp), %xmm6
	movaps	-16(%rbp), %xmm7
	.seh_startepilogue
	addq	$120, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB6_1:
.Ltmp4:
	leaq	anon.a32227af679a3ead67a5cb195479eba7.15.llvm.14389155381977926352(%rip), %r9
	movl	$64, %r8d
	xorl	%ecx, %ecx
	movq	%rsi, %rdx
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	nop
.Ltmp5:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCINvB1f_13defer_destroyNtNtB9_8internal5LocalE0INtNtB9_6atomic5OwnedB2i_EE0EB9_@IMGREL
	.section	.text,"xr",one_only,_RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCINvB1f_13defer_destroyNtNtB9_8internal5LocalE0INtNtB9_6atomic5OwnedB2i_EE0EB9_,unique,6
	.seh_endproc
	.def	"?dtor$8@?0?_RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCINvB1f_13defer_destroyNtNtB9_8internal5LocalE0INtNtB9_6atomic5OwnedB2i_EE0EB9_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$8@?0?_RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCINvB1f_13defer_destroyNtNtB9_8internal5LocalE0INtNtB9_6atomic5OwnedB2i_EE0EB9_@4HA":
.seh_proc "?dtor$8@?0?_RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCINvB1f_13defer_destroyNtNtB9_8internal5LocalE0INtNtB9_6atomic5OwnedB2i_EE0EB9_@4HA"
.LBB6_8:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$72, %rsp
	.seh_stackalloc 72
	leaq	112(%rdx), %rbp
	movaps	%xmm7, 32(%rsp)
	.seh_savexmm %xmm7, 32
	movaps	%xmm6, 48(%rsp)
	.seh_savexmm %xmm6, 48
	.seh_endprologue
	movq	-48(%rbp), %rcx
	callq	mi_free
	movaps	48(%rsp), %xmm6
	movaps	32(%rsp), %xmm7
	.seh_startepilogue
	addq	$72, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end6:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCINvB1f_13defer_destroyNtNtB9_8internal5LocalE0INtNtB9_6atomic5OwnedB2i_EE0EB9_,unique,6
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCINvB1f_13defer_destroyNtNtB9_8internal5LocalE0INtNtB9_6atomic5OwnedB2i_EE0EB9_,unique,1
	.p2align	2, 0x0
$cppxdata$_RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCINvB1f_13defer_destroyNtNtB9_8internal5LocalE0INtNtB9_6atomic5OwnedB2i_EE0EB9_:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCINvB1f_13defer_destroyNtNtB9_8internal5LocalE0INtNtB9_6atomic5OwnedB2i_EE0EB9_@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCINvB1f_13defer_destroyNtNtB9_8internal5LocalE0INtNtB9_6atomic5OwnedB2i_EE0EB9_@IMGREL
	.long	72
	.long	0
	.long	1
$stateUnwindMap$_RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCINvB1f_13defer_destroyNtNtB9_8internal5LocalE0INtNtB9_6atomic5OwnedB2i_EE0EB9_:
	.long	-1
	.long	"?dtor$8@?0?_RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCINvB1f_13defer_destroyNtNtB9_8internal5LocalE0INtNtB9_6atomic5OwnedB2i_EE0EB9_@4HA"@IMGREL
$ip2state$_RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCINvB1f_13defer_destroyNtNtB9_8internal5LocalE0INtNtB9_6atomic5OwnedB2i_EE0EB9_:
	.long	.Lfunc_begin6@IMGREL
	.long	-1
	.long	.Ltmp6@IMGREL
	.long	0
	.long	.Ltmp5@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCINvB1f_13defer_destroyNtNtB9_8internal5LocalE0INtNtB9_6atomic5OwnedB2i_EE0EB9_,unique,6

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvMs0_NtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync9once_lockINtB16_8OnceLockNtNtB1a_9collector9CollectorE10initializeNvMs1_B2c_B2a_3newE0E0B1a_.llvm.14389155381977926352;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvMs0_NtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync9once_lockINtB16_8OnceLockNtNtB1a_9collector9CollectorE10initializeNvMs1_B2c_B2a_3newE0E0B1a_.llvm.14389155381977926352,unique,7
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvMs0_NtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync9once_lockINtB16_8OnceLockNtNtB1a_9collector9CollectorE10initializeNvMs1_B2c_B2a_3newE0E0B1a_.llvm.14389155381977926352
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvMs0_NtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync9once_lockINtB16_8OnceLockNtNtB1a_9collector9CollectorE10initializeNvMs1_B2c_B2a_3newE0E0B1a_.llvm.14389155381977926352:
.Lfunc_begin7:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvMs0_NtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync9once_lockINtB16_8OnceLockNtNtB1a_9collector9CollectorE10initializeNvMs1_B2c_B2a_3newE0E0B1a_.llvm.14389155381977926352
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rcx
	movq	(%rcx), %rax
	movq	$0, (%rcx)
	testq	%rax, %rax
	je	.LBB7_2
	movq	(%rax), %rsi
	callq	_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB7_2:
	leaq	anon.a32227af679a3ead67a5cb195479eba7.9(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end7:
	.seh_endproc

	.def	_RNSNvNCNKNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default6HANDLE0023___RUST_STD_INTERNAL_VAL3tls;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvNCNKNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default6HANDLE0023___RUST_STD_INTERNAL_VAL3tls,unique,8
	.globl	_RNSNvNCNKNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default6HANDLE0023___RUST_STD_INTERNAL_VAL3tls
	.p2align	4
_RNSNvNCNKNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default6HANDLE0023___RUST_STD_INTERNAL_VAL3tls:
.Lfunc_begin8:
	movl	_tls_index(%rip), %eax
	movq	%gs:88, %rcx
	movq	(%rcx,%rax,8), %rax
	leaq	_RNvNCNKNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default6HANDLE0023___RUST_STD_INTERNAL_VAL@SECREL32(%rax), %rax
	retq
.Lfunc_end8:

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once9call_onceNCINvMs0_NtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync9once_lockINtB1b_8OnceLockNtNtB1f_9collector9CollectorE10initializeNvMs1_B2h_B2f_3newE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1f_.llvm.14389155381977926352;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once9call_onceNCINvMs0_NtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync9once_lockINtB1b_8OnceLockNtNtB1f_9collector9CollectorE10initializeNvMs1_B2h_B2f_3newE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1f_.llvm.14389155381977926352,unique,9
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once9call_onceNCINvMs0_NtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync9once_lockINtB1b_8OnceLockNtNtB1f_9collector9CollectorE10initializeNvMs1_B2h_B2f_3newE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1f_.llvm.14389155381977926352
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once9call_onceNCINvMs0_NtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync9once_lockINtB1b_8OnceLockNtNtB1f_9collector9CollectorE10initializeNvMs1_B2h_B2f_3newE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1f_.llvm.14389155381977926352:
.Lfunc_begin9:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once9call_onceNCINvMs0_NtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync9once_lockINtB1b_8OnceLockNtNtB1f_9collector9CollectorE10initializeNvMs1_B2h_B2f_3newE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1f_.llvm.14389155381977926352
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rcx
	movq	(%rcx), %rax
	movq	$0, (%rcx)
	testq	%rax, %rax
	je	.LBB9_1
	movq	(%rax), %rsi
	callq	_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB9_1:
	leaq	anon.a32227af679a3ead67a5cb195479eba7.9(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end9:
	.seh_endproc

	.def	_RNvMNtCs3qjAvHHmxHz_15crossbeam_epoch5guardNtB2_5Guard5flush;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMNtCs3qjAvHHmxHz_15crossbeam_epoch5guardNtB2_5Guard5flush,unique,10
	.globl	_RNvMNtCs3qjAvHHmxHz_15crossbeam_epoch5guardNtB2_5Guard5flush
	.p2align	4
_RNvMNtCs3qjAvHHmxHz_15crossbeam_epoch5guardNtB2_5Guard5flush:
.Lfunc_begin10:
.seh_proc _RNvMNtCs3qjAvHHmxHz_15crossbeam_epoch5guardNtB2_5Guard5flush
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
	movl	$4144, %eax
	callq	__chkstk
	subq	%rax, %rsp
	.seh_stackalloc 4144
	.seh_endprologue
	movq	(%rcx), %rbx
	testq	%rbx, %rbx
	jne	.LBB10_1
	.seh_startepilogue
	addq	$4144, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	.seh_endepilogue
	retq
.LBB10_1:
	movq	%rcx, %rsi
	cmpq	$0, 2064(%rbx)
	je	.LBB10_10
	movq	8(%rbx), %r14
	movl	$96, %eax
	movups	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352+16(%rip), %xmm0
	movups	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352(%rip), %xmm1
	.p2align	4
.LBB10_3:
	movups	%xmm0, -40(%rsp,%rax)
	movups	%xmm1, -56(%rsp,%rax)
	movups	%xmm1, -24(%rsp,%rax)
	movups	%xmm0, -8(%rsp,%rax)
	movups	%xmm1, 8(%rsp,%rax)
	movups	%xmm0, 24(%rsp,%rax)
	movups	%xmm1, 40(%rsp,%rax)
	movups	%xmm0, 56(%rsp,%rax)
	subq	$-128, %rax
	cmpq	$2144, %rax
	jne	.LBB10_3
	leaq	16(%rbx), %rdi
	leaq	2088(%rsp), %rcx
	movl	$2056, %r8d
	movq	%rdi, %rdx
	callq	memcpy
	leaq	40(%rsp), %rdx
	movl	$2048, %r8d
	movq	%rdi, %rcx
	callq	memcpy
	movq	$0, 2064(%rbx)
	lock		orl	$0, (%rsp)
	movq	384(%r14), %r15
	movl	$2072, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB10_12
	movq	%rax, %rdi
	leaq	2088(%rsp), %rdx
	movl	$2056, %r8d
	movq	%rax, %rcx
	callq	memcpy
	movq	%r15, 2056(%rdi)
	movq	$0, 2064(%rdi)
	jmp	.LBB10_6
	.p2align	4
.LBB10_7:
	movq	%rcx, %rax
	lock		cmpxchgq	%r8, 256(%r14)
.LBB10_6:
	movq	256(%r14), %rcx
	movq	%rcx, %rdx
	andq	$-8, %rdx
	movq	2064(%rdx), %r8
	cmpq	$8, %r8
	jae	.LBB10_7
	xorl	%eax, %eax
	lock		cmpxchgq	%rdi, 2064(%rdx)
	jne	.LBB10_6
	movq	%rcx, %rax
	lock		cmpxchgq	%rdi, 256(%r14)
.LBB10_10:
	movq	8(%rbx), %rcx
	subq	$-128, %rcx
	movq	%rsi, %rdx
	.seh_startepilogue
	addq	$4144, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	.seh_endepilogue
	jmp	_RNvMs5_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_6Global7collect
.LBB10_12:
	movl	$8, %ecx
	movl	$2072, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	ud2
.Lfunc_end10:
	.seh_endproc

	.def	_RNvMs1_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9Collector8register;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs1_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9Collector8register,unique,11
	.globl	_RNvMs1_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9Collector8register
	.p2align	4
_RNvMs1_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9Collector8register:
.Lfunc_begin11:
.seh_proc _RNvMs1_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9Collector8register
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	movl	$4568, %eax
	callq	__chkstk
	subq	%rax, %rsp
	.seh_stackalloc 4568
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	andq	$-128, %rsp
	movq	%rsp, %rbx
	movq	%rbp, 4552(%rbx)
	movq	$-2, 4432(%rbp)
	movq	(%rcx), %rdi
	lock		incq	(%rdi)
	jle	.LBB11_5
	movl	$96, %eax
	movups	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352+16(%rip), %xmm0
	movups	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352(%rip), %xmm1
	.p2align	4
.LBB11_2:
	movups	%xmm0, 48(%rbx,%rax)
	movups	%xmm1, 32(%rbx,%rax)
	movups	%xmm1, 64(%rbx,%rax)
	movups	%xmm0, 80(%rbx,%rax)
	movups	%xmm1, 96(%rbx,%rax)
	movups	%xmm0, 112(%rbx,%rax)
	movups	%xmm1, 128(%rbx,%rax)
	movups	%xmm0, 144(%rbx,%rax)
	subq	$-128, %rax
	cmpq	$2144, %rax
	jne	.LBB11_2
	movq	$0, 2176(%rbx)
	movq	%rdi, 2184(%rbx)
	leaq	2192(%rbx), %rcx
	leaq	128(%rbx), %rdx
	movl	$2048, %r8d
	callq	memcpy
	xorps	%xmm0, %xmm0
	movaps	%xmm0, 4240(%rbx)
	movq	$1, 4256(%rbx)
	movq	$0, 4264(%rbx)
	movq	$0, 4352(%rbx)
	movl	$2304, %ecx
	movl	$128, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB11_4
	movq	%rax, %rsi
	leaq	2176(%rbx), %rdx
	movl	$2304, %r8d
	movq	%rax, %rcx
	callq	memcpy
	movq	512(%rdi), %rax
	.p2align	4
.LBB11_8:
	movq	%rax, (%rsi)
	lock		cmpxchgq	%rsi, 512(%rdi)
	jne	.LBB11_8
	movq	%rsi, %rax
	.seh_startepilogue
	leaq	4440(%rbp), %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB11_4:
.Ltmp8:
	movl	$128, %ecx
	movl	$2304, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp9:
.LBB11_5:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvMs1_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9Collector8register@IMGREL
	.section	.text,"xr",one_only,_RNvMs1_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9Collector8register,unique,11
	.seh_endproc
	.def	"?dtor$6@?0?_RNvMs1_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9Collector8register@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$6@?0?_RNvMs1_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9Collector8register@4HA":
.seh_proc "?dtor$6@?0?_RNvMs1_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9Collector8register@4HA"
.LBB11_6:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	128(%rdx), %rbp
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	leaq	2176(%rbx), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal5LocalEBF_.llvm.14389155381977926352
	nop
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end11:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs1_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9Collector8register,unique,11
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvMs1_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9Collector8register,unique,2
	.p2align	2, 0x0
$cppxdata$_RNvMs1_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9Collector8register:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNvMs1_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9Collector8register@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RNvMs1_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9Collector8register@IMGREL
	.long	4560
	.long	0
	.long	1
$stateUnwindMap$_RNvMs1_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9Collector8register:
	.long	-1
	.long	"?dtor$6@?0?_RNvMs1_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9Collector8register@4HA"@IMGREL
$ip2state$_RNvMs1_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9Collector8register:
	.long	.Lfunc_begin11@IMGREL
	.long	-1
	.long	.Ltmp8@IMGREL
	.long	0
	.long	.Ltmp9@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvMs1_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9Collector8register,unique,11

	.def	_RNvMs5_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_6Global11try_advance.llvm.14389155381977926352;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs5_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_6Global11try_advance.llvm.14389155381977926352,unique,12
	.globl	_RNvMs5_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_6Global11try_advance.llvm.14389155381977926352
	.p2align	4
_RNvMs5_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_6Global11try_advance.llvm.14389155381977926352:
.Lfunc_begin12:
.seh_proc _RNvMs5_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_6Global11try_advance.llvm.14389155381977926352
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
	movq	%rcx, %rdi
	movq	256(%rcx), %rsi
	lock		orl	$0, (%rsp)
	movq	%rdx, %rbx
	leaq	384(%rcx), %r14
	movq	384(%rcx), %r12
	movq	%r14, %r15
.LBB12_1:
	movq	%r12, %rax
	andq	$-8, %rax
	je	.LBB12_9
	movq	%r12, %rcx
	.p2align	4
.LBB12_3:
	movq	(%rax), %r12
	movl	%r12d, %edx
	andl	$7, %edx
	cmpl	$1, %edx
	jne	.LBB12_11
	andq	$-8, %r12
	movq	%rcx, %rax
	lock		cmpxchgq	%r12, (%r15)
	jne	.LBB12_5
	andq	$-8, %rcx
	movq	%rbx, %rdx
	callq	_RNvXs7_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5LocalINtNtNtB7_4sync4list9IsElementBL_E8finalize
	movq	%r12, %rcx
	testb	$7, %cl
	je	.LBB12_8
	jmp	.LBB12_13
	.p2align	4
.LBB12_5:
	movq	%rax, %rcx
	testb	$7, %cl
	jne	.LBB12_13
.LBB12_8:
	movq	%rcx, %rax
	testq	%rcx, %rcx
	jne	.LBB12_3
	jmp	.LBB12_9
	.p2align	4
.LBB12_11:
	movq	2176(%rax), %rcx
	movq	%rax, %r15
	testb	$1, %cl
	je	.LBB12_1
	andq	$-2, %rcx
	movq	%rax, %r15
	cmpq	%rsi, %rcx
	je	.LBB12_1
	jmp	.LBB12_10
.LBB12_9:
	#MEMBARRIER
	addq	$2, %rsi
	movq	%rsi, 256(%rdi)
	jmp	.LBB12_10
.LBB12_13:
	movq	(%r14), %rax
.LBB12_10:
	movq	%rsi, %rax
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
.Lfunc_end12:
	.seh_endproc

	.def	_RNvMs5_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_6Global7collect;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs5_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_6Global7collect,unique,13
	.globl	_RNvMs5_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_6Global7collect
	.p2align	4
_RNvMs5_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_6Global7collect:
.Lfunc_begin13:
.seh_proc _RNvMs5_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_6Global7collect
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
	movl	$4184, %eax
	callq	__chkstk
	subq	%rax, %rsp
	.seh_stackalloc 4184
	.seh_endprologue
	movq	%rdx, %rbx
	movq	%rcx, %rsi
	callq	_RNvMs5_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_6Global11try_advance.llvm.14389155381977926352
	movq	%rax, %r14
	movq	(%rbx), %rax
	movq	%rax, 40(%rsp)
	leaq	2128(%rsp), %r15
	leaq	72(%rsp), %r13
	xorl	%r12d, %r12d
	leaq	2120(%rsp), %rdi
	.p2align	4
.LBB13_1:
	movq	(%rsi), %rbx
	movq	%rbx, %rcx
	andq	$-8, %rcx
	movq	2064(%rcx), %rdx
	movq	%rdx, %rbp
	andq	$-8, %rbp
	je	.LBB13_26
	movq	2056(%rbp), %rax
	andq	$-2, %rax
	movq	%r14, %r8
	subq	%rax, %r8
	cmpq	$4, %r8
	jl	.LBB13_26
	movq	%rbx, %rax
	lock		cmpxchgq	%rdx, (%rsi)
	jne	.LBB13_1
	movq	128(%rsi), %rax
	cmpq	%rax, %rbx
	jne	.LBB13_5
	movq	%rbx, %rax
	lock		cmpxchgq	%rdx, 128(%rsi)
.LBB13_5:
	movq	40(%rsp), %rdx
	testq	%rdx, %rdx
	je	.LBB13_6
	movq	%r12, 48(%rsp)
	movq	2064(%rdx), %rax
	cmpq	$64, %rax
	movq	%rdx, %r13
	jb	.LBB13_17
	movq	%rsi, 56(%rsp)
	.p2align	4
.LBB13_9:
	movq	8(%r13), %r12
	movl	$96, %eax
	.p2align	4
.LBB13_10:
	movups	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352+16(%rip), %xmm0
	movups	%xmm0, -16(%rsp,%rax)
	movups	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352(%rip), %xmm1
	movups	%xmm1, -32(%rsp,%rax)
	movups	%xmm1, (%rsp,%rax)
	movups	%xmm0, 16(%rsp,%rax)
	movups	%xmm1, 32(%rsp,%rax)
	movups	%xmm0, 48(%rsp,%rax)
	movups	%xmm1, 64(%rsp,%rax)
	movups	%xmm0, 80(%rsp,%rax)
	subq	$-128, %rax
	cmpq	$2144, %rax
	jne	.LBB13_10
	movl	$2056, %r8d
	movq	%rdi, %rcx
	leaq	16(%r13), %r15
	movq	%r15, %rdx
	callq	memcpy
	movl	$2048, %r8d
	movq	%r15, %rcx
	leaq	64(%rsp), %rdx
	callq	memcpy
	movq	$0, 2064(%r13)
	lock		orl	$0, (%rsp)
	movq	384(%r12), %r15
	movl	$2072, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB13_27
	movq	%rax, %r13
	movq	%r14, %rsi
	movl	$2056, %r8d
	movq	%rax, %rcx
	movq	%rdi, %r14
	movq	%rdi, %rdx
	callq	memcpy
	movq	%r15, 2056(%r13)
	movq	$0, 2064(%r13)
	jmp	.LBB13_13
	.p2align	4
.LBB13_14:
	movq	%rcx, %rax
	lock		cmpxchgq	%r8, 256(%r12)
.LBB13_13:
	movq	256(%r12), %rcx
	movq	%rcx, %rdx
	andq	$-8, %rdx
	movq	2064(%rdx), %r8
	cmpq	$8, %r8
	jae	.LBB13_14
	xorl	%eax, %eax
	lock		cmpxchgq	%r13, 2064(%rdx)
	jne	.LBB13_13
	movq	%rcx, %rax
	lock		cmpxchgq	%r13, 256(%r12)
	movq	40(%rsp), %r13
	movq	2064(%r13), %rax
	cmpq	$63, %rax
	movq	%r14, %rdi
	movq	%rsi, %r14
	movq	56(%rsp), %rsi
	ja	.LBB13_9
.LBB13_17:
	shlq	$5, %rax
	leaq	16(%r13), %rcx
	leaq	_RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCINvB1f_13defer_destroyINtNtNtB9_4sync5queue4NodeNtNtB9_8internal9SealedBagEE0INtNtB9_6atomic5OwnedB2i_EE0EB9_.llvm.14389155381977926352(%rip), %rdx
	movq	%rdx, (%rcx,%rax)
	movq	%rbx, 8(%rcx,%rax)
	incq	2064(%r13)
	leaq	2128(%rsp), %r15
	leaq	72(%rsp), %r13
	movq	48(%rsp), %r12
	movq	(%rbp), %rbx
	testq	%rbx, %rbx
	jne	.LBB13_19
	jmp	.LBB13_26
.LBB13_6:
	callq	mi_free
	movq	(%rbp), %rbx
	testq	%rbx, %rbx
	je	.LBB13_26
.LBB13_19:
	addq	$8, %rbp
	movl	$2056, %r8d
	movq	%r15, %rcx
	movq	%rbp, %rdx
	callq	memcpy
	movq	%rbx, 2120(%rsp)
	movq	4168(%rsp), %rbx
	cmpq	$65, %rbx
	jae	.LBB13_20
	movq	%r12, %rbp
	testq	%rbx, %rbx
	je	.LBB13_25
	shlq	$5, %rbx
	xorl	%r12d, %r12d
	.p2align	4
.LBB13_24:
	movups	2120(%rsp,%r12), %xmm0
	movups	2136(%rsp,%r12), %xmm1
	movaps	%xmm1, 80(%rsp)
	movaps	%xmm0, 64(%rsp)
	movups	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352(%rip), %xmm0
	movups	%xmm0, 2120(%rsp,%r12)
	movups	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352+16(%rip), %xmm0
	movups	%xmm0, 2136(%rsp,%r12)
	movq	%r13, %rcx
	callq	*64(%rsp)
	addq	$32, %r12
	cmpq	%r12, %rbx
	jne	.LBB13_24
.LBB13_25:
	movq	%rbp, %r12
	incq	%r12
	cmpq	$8, %r12
	jne	.LBB13_1
.LBB13_26:
	.seh_startepilogue
	addq	$4184, %rsp
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
.LBB13_27:
	movl	$8, %ecx
	movl	$2072, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	ud2
.LBB13_20:
	leaq	anon.a32227af679a3ead67a5cb195479eba7.15.llvm.14389155381977926352(%rip), %r9
	movl	$64, %r8d
	xorl	%ecx, %ecx
	movq	%rbx, %rdx
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	ud2
.Lfunc_end13:
	.seh_endproc

	.def	_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local5defer;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local5defer,unique,14
	.globl	_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local5defer
	.p2align	4
_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local5defer:
.Lfunc_begin14:
.seh_proc _RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local5defer
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
	movl	$4184, %eax
	callq	__chkstk
	subq	%rax, %rsp
	.seh_stackalloc 4184
	movaps	%xmm7, 4160(%rsp)
	.seh_savexmm %xmm7, 4160
	movaps	%xmm6, 4144(%rsp)
	.seh_savexmm %xmm6, 4144
	.seh_endprologue
	movq	%rdx, %rbx
	movq	%rcx, %rsi
	leaq	16(%rcx), %rdi
	movq	2064(%rcx), %rax
	cmpq	$64, %rax
	jb	.LBB14_10
	movups	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352+16(%rip), %xmm6
	movups	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352(%rip), %xmm7
	leaq	2088(%rsp), %r14
	leaq	40(%rsp), %r15
	.p2align	4
.LBB14_2:
	movq	8(%rsi), %r13
	movl	$96, %eax
	.p2align	4
.LBB14_3:
	movups	%xmm6, -40(%rsp,%rax)
	movups	%xmm7, -56(%rsp,%rax)
	movups	%xmm7, -24(%rsp,%rax)
	movups	%xmm6, -8(%rsp,%rax)
	movups	%xmm7, 8(%rsp,%rax)
	movups	%xmm6, 24(%rsp,%rax)
	movups	%xmm7, 40(%rsp,%rax)
	movups	%xmm6, 56(%rsp,%rax)
	subq	$-128, %rax
	cmpq	$2144, %rax
	jne	.LBB14_3
	movl	$2056, %r8d
	movq	%r14, %rcx
	movq	%rdi, %rdx
	callq	memcpy
	movl	$2048, %r8d
	movq	%rdi, %rcx
	movq	%r15, %rdx
	callq	memcpy
	movq	$0, 2064(%rsi)
	lock		orl	$0, (%rsp)
	movq	384(%r13), %rbp
	movl	$2072, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB14_11
	movq	%rax, %r12
	movl	$2056, %r8d
	movq	%rax, %rcx
	movq	%r14, %rdx
	callq	memcpy
	movq	%rbp, 2056(%r12)
	movq	$0, 2064(%r12)
	jmp	.LBB14_6
	.p2align	4
.LBB14_7:
	movq	%rcx, %rax
	lock		cmpxchgq	%r8, 256(%r13)
.LBB14_6:
	movq	256(%r13), %rcx
	movq	%rcx, %rdx
	andq	$-8, %rdx
	movq	2064(%rdx), %r8
	cmpq	$8, %r8
	jae	.LBB14_7
	xorl	%eax, %eax
	lock		cmpxchgq	%r12, 2064(%rdx)
	jne	.LBB14_6
	movq	%rcx, %rax
	lock		cmpxchgq	%r12, 256(%r13)
	movq	2064(%rsi), %rax
	cmpq	$63, %rax
	ja	.LBB14_2
.LBB14_10:
	shlq	$5, %rax
	movups	(%rbx), %xmm0
	movups	16(%rbx), %xmm1
	movups	%xmm1, 16(%rdi,%rax)
	movups	%xmm0, (%rdi,%rax)
	incq	2064(%rsi)
	movaps	4144(%rsp), %xmm6
	movaps	4160(%rsp), %xmm7
	.seh_startepilogue
	addq	$4184, %rsp
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
.LBB14_11:
	movl	$8, %ecx
	movl	$2072, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	ud2
.Lfunc_end14:
	.seh_endproc

	.def	_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local5unpin;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local5unpin,unique,15
	.p2align	4
_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local5unpin:
.Lfunc_begin15:
	decq	2072(%rcx)
	jne	.LBB15_2
	movq	$0, 2176(%rcx)
	cmpq	$0, 2080(%rcx)
	je	_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize
.LBB15_2:
	retq
.Lfunc_end15:

	.def	_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize,unique,16
	.globl	_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize
	.p2align	4
_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize:
.Lfunc_begin16:
.seh_proc _RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	movl	$4160, %eax
	callq	__chkstk
	subq	%rax, %rsp
	.seh_stackalloc 4160
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	movq	$-2, 4024(%rbp)
	movq	$1, 2080(%rcx)
	movq	%rcx, -96(%rbp)
	movq	2072(%rcx), %rax
	cmpq	$-1, %rax
	movq	%rcx, 4016(%rbp)
	je	.LBB16_8
	movq	%rcx, %rdx
	leaq	1(%rax), %rcx
	movq	%rcx, 2072(%rdx)
	testq	%rax, %rax
	jne	.LBB16_4
	movq	4016(%rbp), %rdx
	movq	8(%rdx), %rax
	movq	384(%rax), %rcx
	orq	$1, %rcx
	xorl	%eax, %eax
	lock		cmpxchgq	%rcx, 2176(%rdx)
	#MEMBARRIER
	movq	2088(%rdx), %rax
	leaq	1(%rax), %rcx
	movq	%rcx, 2088(%rdx)
	testb	$127, %al
	je	.LBB16_3
.LBB16_4:
	movq	4016(%rbp), %r14
	movq	%r14, 4008(%rbp)
	movq	8(%r14), %rdi
	movl	$96, %eax
	movups	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352+16(%rip), %xmm0
	movups	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352(%rip), %xmm1
	.p2align	4
.LBB16_5:
	movups	%xmm0, 1880(%rbp,%rax)
	movups	%xmm1, 1864(%rbp,%rax)
	movups	%xmm1, 1896(%rbp,%rax)
	movups	%xmm0, 1912(%rbp,%rax)
	movups	%xmm1, 1928(%rbp,%rax)
	movups	%xmm0, 1944(%rbp,%rax)
	movups	%xmm1, 1960(%rbp,%rax)
	movups	%xmm0, 1976(%rbp,%rax)
	subq	$-128, %rax
	cmpq	$2144, %rax
	jne	.LBB16_5
	leaq	16(%r14), %rsi
	leaq	-96(%rbp), %rcx
	movl	$2056, %r8d
	movq	%rsi, %rdx
	callq	memcpy
	leaq	1960(%rbp), %rdx
	movl	$2048, %r8d
	movq	%rsi, %rcx
	callq	memcpy
	movq	$0, 2064(%r14)
	lock		orl	$0, (%rsp)
	movq	384(%rdi), %rbx
	movl	$2072, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB16_7
	movq	%rax, %rsi
	leaq	-96(%rbp), %rdx
	movl	$2056, %r8d
	movq	%rax, %rcx
	callq	memcpy
	movq	%rbx, 2056(%rsi)
	movq	$0, 2064(%rsi)
	jmp	.LBB16_11
	.p2align	4
.LBB16_12:
	movq	%rcx, %rax
	lock		cmpxchgq	%r8, 256(%rdi)
.LBB16_11:
	movq	256(%rdi), %rcx
	movq	%rcx, %rdx
	andq	$-8, %rdx
	movq	2064(%rdx), %r8
	cmpq	$8, %r8
	jae	.LBB16_12
	xorl	%eax, %eax
	lock		cmpxchgq	%rsi, 2064(%rdx)
	jne	.LBB16_11
	movq	%rcx, %rax
	lock		cmpxchgq	%rsi, 256(%rdi)
	decq	2072(%r14)
	jne	.LBB16_18
	movq	$0, 2176(%r14)
	cmpq	$0, 2080(%r14)
	je	.LBB16_17
.LBB16_18:
	movq	$0, 2080(%r14)
	movq	8(%r14), %rax
	lock		orq	$1, (%r14)
	movq	%rax, -96(%rbp)
	lock		decq	(%rax)
	jne	.LBB16_20
	#MEMBARRIER
	leaq	-96(%rbp), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalE9drop_slowBK_
	nop
.LBB16_20:
	.seh_startepilogue
	addq	$4160, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.LBB16_8:
.Ltmp14:
	leaq	anon.a32227af679a3ead67a5cb195479eba7.12(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	nop
.Ltmp15:
	jmp	.LBB16_9
.LBB16_7:
.Ltmp12:
	movl	$8, %ecx
	movl	$2072, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp13:
.LBB16_9:
	ud2
.LBB16_17:
	movq	%r14, %rcx
	callq	_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize
	jmp	.LBB16_18
.LBB16_3:
	movq	4016(%rbp), %rax
	movq	8(%rax), %rcx
	subq	$-128, %rcx
.Ltmp10:
	leaq	-96(%rbp), %rdx
	callq	_RNvMs5_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_6Global7collect
	nop
.Ltmp11:
	jmp	.LBB16_4
	.seh_handlerdata
	.long	$cppxdata$_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize@IMGREL
	.section	.text$unlikely,"xr",one_only,_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize,unique,16
	.seh_endproc
	.def	"?dtor$13@?0?_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$13@?0?_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize@4HA":
.seh_proc "?dtor$13@?0?_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize@4HA"
.LBB16_13:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	leaq	4008(%rbp), %rcx
	callq	_RNvXs_NtCs3qjAvHHmxHz_15crossbeam_epoch5guardNtB4_5GuardNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop
	nop
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text$unlikely,"xr",one_only,_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize,unique,16
	.seh_endproc
	.def	"?dtor$21@?0?_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$21@?0?_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize@4HA":
.seh_proc "?dtor$21@?0?_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize@4HA"
.LBB16_21:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movq	4016(%rbp), %rcx
	callq	_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local5unpin
	nop
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end16:
	.seh_handlerdata
	.section	.text$unlikely,"xr",one_only,_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize,unique,16
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize,unique,3
	.p2align	2, 0x0
$cppxdata$_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize:
	.long	429065506
	.long	2
	.long	$stateUnwindMap$_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize@IMGREL
	.long	0
	.long	0
	.long	6
	.long	$ip2state$_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize@IMGREL
	.long	4152
	.long	0
	.long	1
$stateUnwindMap$_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize:
	.long	-1
	.long	"?dtor$21@?0?_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize@4HA"@IMGREL
	.long	-1
	.long	"?dtor$13@?0?_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize@4HA"@IMGREL
$ip2state$_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize:
	.long	.Lfunc_begin16@IMGREL
	.long	-1
	.long	.Ltmp14@IMGREL
	.long	0
	.long	.Ltmp12@IMGREL
	.long	1
	.long	.Ltmp13@IMGREL
	.long	-1
	.long	.Ltmp10@IMGREL
	.long	0
	.long	.Ltmp11@IMGREL
	.long	-1
	.section	.text$unlikely,"xr",one_only,_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize,unique,16

	.def	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalE9drop_slowBK_;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalE9drop_slowBK_,unique,17
	.globl	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalE9drop_slowBK_
	.p2align	4
_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalE9drop_slowBK_:
.Lfunc_begin17:
.seh_proc _RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalE9drop_slowBK_
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$80, %rsp
	.seh_stackalloc 80
	leaq	80(%rsp), %rbp
	.seh_setframe %rbp, 80
	.seh_endprologue
	movq	$-2, -8(%rbp)
	movq	(%rcx), %rax
	leaq	128(%rax), %rcx
	movq	%rcx, -16(%rbp)
	movq	%rax, -24(%rbp)
	movq	512(%rax), %rcx
	andq	$-8, %rcx
	je	.LBB17_5
	leaq	_RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch5guard11unprotected11UNPROTECTED(%rip), %rsi
	.p2align	4
.LBB17_2:
	movq	(%rcx), %rdi
	movl	%edi, %eax
	andl	$7, %eax
	movq	%rax, -32(%rbp)
	cmpq	$1, %rax
	jne	.LBB17_9
.Ltmp18:
	movq	%rsi, %rdx
	callq	_RNvXs7_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5LocalINtNtNtB7_4sync4list9IsElementBL_E8finalize
	nop
.Ltmp19:
	andq	$-8, %rdi
	movq	%rdi, %rcx
	jne	.LBB17_2
.LBB17_5:
.Ltmp20:
	movq	-16(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync5queue5QueueNtNtBI_8internal9SealedBagEEBI_
	nop
.Ltmp21:
	movq	-24(%rbp), %rcx
	cmpq	$-1, %rcx
	je	.LBB17_16
	lock		decq	8(%rcx)
	jne	.LBB17_16
	#MEMBARRIER
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	jmp	mi_free
.LBB17_16:
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB17_9:
.Ltmp16:
	leaq	anon.a32227af679a3ead67a5cb195479eba7.18(%rip), %rax
	movq	%rax, 40(%rsp)
	leaq	anon.a32227af679a3ead67a5cb195479eba7.16(%rip), %r8
	leaq	-32(%rbp), %rdx
	xorl	%ecx, %ecx
	xorl	%r9d, %r9d
	callq	_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedjjEB4_
	nop
.Ltmp17:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalE9drop_slowBK_@IMGREL
	.section	.text,"xr",one_only,_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalE9drop_slowBK_,unique,17
	.seh_endproc
	.def	"?dtor$11@?0?_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalE9drop_slowBK_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$11@?0?_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalE9drop_slowBK_@4HA":
.seh_proc "?dtor$11@?0?_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalE9drop_slowBK_@4HA"
.LBB17_11:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$48, %rsp
	.seh_stackalloc 48
	leaq	80(%rdx), %rbp
	.seh_endprologue
	movq	-16(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync5queue5QueueNtNtBI_8internal9SealedBagEEBI_
	nop
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalE9drop_slowBK_,unique,17
	.seh_endproc
	.def	"?dtor$12@?0?_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalE9drop_slowBK_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$12@?0?_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalE9drop_slowBK_@4HA":
.seh_proc "?dtor$12@?0?_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalE9drop_slowBK_@4HA"
.LBB17_12:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$48, %rsp
	.seh_stackalloc 48
	leaq	80(%rdx), %rbp
	.seh_endprologue
	movq	-24(%rbp), %rcx
	cmpq	$-1, %rcx
	je	.LBB17_15
	lock		decq	8(%rcx)
	jne	.LBB17_15
	#MEMBARRIER
	callq	mi_free
	nop
.LBB17_15:
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end17:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalE9drop_slowBK_,unique,17
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalE9drop_slowBK_,unique,4
	.p2align	2, 0x0
$cppxdata$_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalE9drop_slowBK_:
	.long	429065506
	.long	2
	.long	$stateUnwindMap$_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalE9drop_slowBK_@IMGREL
	.long	0
	.long	0
	.long	5
	.long	$ip2state$_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalE9drop_slowBK_@IMGREL
	.long	72
	.long	0
	.long	1
$stateUnwindMap$_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalE9drop_slowBK_:
	.long	-1
	.long	"?dtor$12@?0?_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalE9drop_slowBK_@4HA"@IMGREL
	.long	0
	.long	"?dtor$11@?0?_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalE9drop_slowBK_@4HA"@IMGREL
$ip2state$_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalE9drop_slowBK_:
	.long	.Lfunc_begin17@IMGREL
	.long	-1
	.long	.Ltmp18@IMGREL
	.long	1
	.long	.Ltmp20@IMGREL
	.long	0
	.long	.Ltmp16@IMGREL
	.long	1
	.long	.Ltmp17@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalE9drop_slowBK_,unique,17

	.def	_RNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default9collector;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default9collector,unique,18
	.globl	_RNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default9collector
	.p2align	4
_RNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default9collector:
.Lfunc_begin18:
.seh_proc _RNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default9collector
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movl	_RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default9collector9COLLECTOR.llvm.14389155381977926352+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB18_1
	leaq	_RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default9collector9COLLECTOR.llvm.14389155381977926352(%rip), %rax
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.LBB18_1:
	callq	_RINvMs0_NtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync9once_lockINtB6_8OnceLockNtNtBa_9collector9CollectorE10initializeNvMs1_B1b_B19_3newEBa_.llvm.14389155381977926352
	leaq	_RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default9collector9COLLECTOR.llvm.14389155381977926352(%rip), %rax
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end18:
	.seh_endproc

	.def	_RNvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB6_8Deferred5NO_OP10no_op_call.llvm.14389155381977926352;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB6_8Deferred5NO_OP10no_op_call.llvm.14389155381977926352,unique,19
	.globl	_RNvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB6_8Deferred5NO_OP10no_op_call.llvm.14389155381977926352
	.p2align	4
_RNvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB6_8Deferred5NO_OP10no_op_call.llvm.14389155381977926352:
.Lfunc_begin19:
	retq
.Lfunc_end19:

	.def	_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default,unique,20
	.globl	_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default
	.p2align	4
_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default:
.Lfunc_begin20:
.seh_proc _RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$1120, %rsp
	.seh_stackalloc 1120
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	andq	$-128, %rsp
	movq	%rsp, %rbx
	movq	%rbp, 1104(%rbx)
	movq	$-2, 984(%rbp)
	movq	$0, 120(%rbx)
	movq	$0, 128(%rbx)
	movq	$0, 256(%rbx)
	movl	$2072, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB20_1
	movq	$0, 2064(%rax)
	movq	%rax, 128(%rbx)
	movq	%rax, 256(%rbx)
	leaq	512(%rbx), %rcx
	leaq	128(%rbx), %rdx
	movl	$256, %r8d
	callq	memcpy
	movq	$1, 384(%rbx)
	movq	$1, 392(%rbx)
	movq	$0, 768(%rbx)
	movq	$0, 896(%rbx)
	movl	$640, %ecx
	movl	$128, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB20_6
	leaq	384(%rbx), %rdx
	movl	$640, %r8d
	movq	%rax, %rcx
	movq	%rax, %rsi
	callq	memcpy
	movq	%rsi, %rax
	.seh_startepilogue
	leaq	992(%rbp), %rsp
	popq	%rbx
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB20_1:
.Ltmp24:
	movl	$8, %ecx
	movl	$2072, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp25:
	jmp	.LBB20_2
.LBB20_6:
.Ltmp22:
	movl	$128, %ecx
	movl	$640, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp23:
.LBB20_2:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default@IMGREL
	.section	.text,"xr",one_only,_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default,unique,20
	.seh_endproc
	.def	"?dtor$3@?0?_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$3@?0?_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default@4HA":
.seh_proc "?dtor$3@?0?_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default@4HA"
.LBB20_3:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	128(%rdx), %rbp
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	leaq	128(%rbx), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync5queue5QueueNtNtBI_8internal9SealedBagEEBI_
	nop
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default,unique,20
	.seh_endproc
	.def	"?dtor$4@?0?_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$4@?0?_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default@4HA":
.seh_proc "?dtor$4@?0?_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default@4HA"
.LBB20_4:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	128(%rdx), %rbp
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	leaq	120(%rbx), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync4list4ListNtNtBI_8internal5LocalEEBI_
	nop
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default,unique,20
	.seh_endproc
	.def	"?dtor$7@?0?_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$7@?0?_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default@4HA":
.seh_proc "?dtor$7@?0?_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default@4HA"
.LBB20_7:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	128(%rdx), %rbp
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	leaq	384(%rbx), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal6GlobalEEB1i_
	nop
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end20:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default,unique,20
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default,unique,5
	.p2align	2, 0x0
$cppxdata$_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default:
	.long	429065506
	.long	3
	.long	$stateUnwindMap$_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default@IMGREL
	.long	0
	.long	0
	.long	4
	.long	$ip2state$_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default@IMGREL
	.long	1112
	.long	0
	.long	1
$stateUnwindMap$_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default:
	.long	-1
	.long	"?dtor$4@?0?_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default@4HA"@IMGREL
	.long	0
	.long	"?dtor$3@?0?_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default@4HA"@IMGREL
	.long	-1
	.long	"?dtor$7@?0?_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default@4HA"@IMGREL
$ip2state$_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default:
	.long	.Lfunc_begin20@IMGREL
	.long	-1
	.long	.Ltmp24@IMGREL
	.long	1
	.long	.Ltmp22@IMGREL
	.long	2
	.long	.Ltmp23@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvXs0_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9CollectorNtNtCs8xEFJqa6dYS_4core7default7Default7default,unique,20

	.def	_RNvXs7_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5LocalINtNtNtB7_4sync4list9IsElementBL_E8finalize;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs7_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5LocalINtNtNtB7_4sync4list9IsElementBL_E8finalize,unique,21
	.globl	_RNvXs7_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5LocalINtNtNtB7_4sync4list9IsElementBL_E8finalize
	.p2align	4
_RNvXs7_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5LocalINtNtNtB7_4sync4list9IsElementBL_E8finalize:
.Lfunc_begin21:
.seh_proc _RNvXs7_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5LocalINtNtNtB7_4sync4list9IsElementBL_E8finalize
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
	movl	$4216, %eax
	callq	__chkstk
	subq	%rax, %rsp
	.seh_stackalloc 4216
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	movaps	%xmm7, 4064(%rbp)
	.seh_savexmm %xmm7, 4192
	movaps	%xmm6, 4048(%rbp)
	.seh_savexmm %xmm6, 4176
	.seh_endprologue
	movq	$-2, 4040(%rbp)
	movq	%rcx, %rax
	andq	$120, %rax
	movq	%rax, -80(%rbp)
	jne	.LBB21_22
	movq	(%rdx), %r15
	testq	%r15, %r15
	movq	%rcx, 4032(%rbp)
	je	.LBB21_2
	leaq	16(%r15), %rsi
	movq	2064(%r15), %rax
	cmpq	$64, %rax
	jb	.LBB21_20
	movups	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352+16(%rip), %xmm6
	movups	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352(%rip), %xmm7
	leaq	-80(%rbp), %rdi
	leaq	1984(%rbp), %rbx
	.p2align	4
.LBB21_12:
	movq	8(%r15), %r12
	movl	$96, %eax
	.p2align	4
.LBB21_13:
	movups	%xmm6, 1904(%rbp,%rax)
	movups	%xmm7, 1888(%rbp,%rax)
	movups	%xmm7, 1920(%rbp,%rax)
	movups	%xmm6, 1936(%rbp,%rax)
	movups	%xmm7, 1952(%rbp,%rax)
	movups	%xmm6, 1968(%rbp,%rax)
	movups	%xmm7, 1984(%rbp,%rax)
	movups	%xmm6, 2000(%rbp,%rax)
	subq	$-128, %rax
	cmpq	$2144, %rax
	jne	.LBB21_13
	movl	$2056, %r8d
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	callq	memcpy
	movl	$2048, %r8d
	movq	%rsi, %rcx
	movq	%rbx, %rdx
	callq	memcpy
	movq	$0, 2064(%r15)
	lock		orl	$0, (%rsp)
	movq	384(%r12), %r13
	movl	$2072, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB21_24
	movq	%rax, %r14
	movl	$2056, %r8d
	movq	%rax, %rcx
	movq	%rdi, %rdx
	callq	memcpy
	movq	%r13, 2056(%r14)
	movq	$0, 2064(%r14)
	jmp	.LBB21_16
	.p2align	4
.LBB21_17:
	movq	%rcx, %rax
	lock		cmpxchgq	%r8, 256(%r12)
.LBB21_16:
	movq	256(%r12), %rcx
	movq	%rcx, %rdx
	andq	$-8, %rdx
	movq	2064(%rdx), %r8
	cmpq	$8, %r8
	jae	.LBB21_17
	xorl	%eax, %eax
	lock		cmpxchgq	%r14, 2064(%rdx)
	jne	.LBB21_16
	movq	%rcx, %rax
	lock		cmpxchgq	%r14, 256(%r12)
	movq	2064(%r15), %rax
	cmpq	$63, %rax
	ja	.LBB21_12
.LBB21_20:
	shlq	$5, %rax
	leaq	_RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCINvB1f_13defer_destroyNtNtB9_8internal5LocalE0INtNtB9_6atomic5OwnedB2i_EE0EB9_(%rip), %rcx
	movq	%rcx, (%rsi,%rax)
	movq	4032(%rbp), %rcx
	movq	%rcx, 8(%rsi,%rax)
	incq	2064(%r15)
	jmp	.LBB21_21
.LBB21_2:
	movq	2064(%rcx), %rsi
	cmpq	$65, %rsi
	jae	.LBB21_3
	testq	%rsi, %rsi
	je	.LBB21_9
	movq	4032(%rbp), %rax
	leaq	16(%rax), %rbx
	shlq	$5, %rsi
	addq	%rbx, %rsi
	leaq	-72(%rbp), %rdi
	movups	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352(%rip), %xmm6
	movups	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352+16(%rip), %xmm7
	.p2align	4
.LBB21_7:
	movups	(%rbx), %xmm0
	movups	16(%rbx), %xmm1
	movaps	%xmm1, -64(%rbp)
	movaps	%xmm0, -80(%rbp)
	movups	%xmm6, (%rbx)
	movups	%xmm7, 16(%rbx)
.Ltmp28:
	movq	%rdi, %rcx
	callq	*-80(%rbp)
	nop
.Ltmp29:
	addq	$32, %rbx
	cmpq	%rsi, %rbx
	jne	.LBB21_7
.LBB21_9:
	movq	4032(%rbp), %rcx
	callq	mi_free
.LBB21_21:
	movaps	4048(%rbp), %xmm6
	movaps	4064(%rbp), %xmm7
	.seh_startepilogue
	addq	$4216, %rsp
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
.LBB21_24:
	movl	$8, %ecx
	movl	$2072, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	ud2
.LBB21_22:
	leaq	anon.a32227af679a3ead67a5cb195479eba7.7(%rip), %rax
	movq	%rax, 40(%rsp)
	movq	$35, 32(%rsp)
	leaq	_RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch5guard11unprotected11UNPROTECTED(%rip), %r8
	leaq	anon.a32227af679a3ead67a5cb195479eba7.5(%rip), %r9
	leaq	-80(%rbp), %rdx
	xorl	%ecx, %ecx
	callq	_RINvNtCs8xEFJqa6dYS_4core9panicking13assert_failedjjEB4_
	ud2
.LBB21_3:
.Ltmp26:
	leaq	anon.a32227af679a3ead67a5cb195479eba7.15.llvm.14389155381977926352(%rip), %r9
	movl	$64, %r8d
	xorl	%ecx, %ecx
	movq	%rsi, %rdx
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	nop
.Ltmp27:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvXs7_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5LocalINtNtNtB7_4sync4list9IsElementBL_E8finalize@IMGREL
	.section	.text,"xr",one_only,_RNvXs7_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5LocalINtNtNtB7_4sync4list9IsElementBL_E8finalize,unique,21
	.seh_endproc
	.def	"?dtor$23@?0?_RNvXs7_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5LocalINtNtNtB7_4sync4list9IsElementBL_E8finalize@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$23@?0?_RNvXs7_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5LocalINtNtNtB7_4sync4list9IsElementBL_E8finalize@4HA":
.seh_proc "?dtor$23@?0?_RNvXs7_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5LocalINtNtNtB7_4sync4list9IsElementBL_E8finalize@4HA"
.LBB21_23:
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
	subq	$88, %rsp
	.seh_stackalloc 88
	leaq	128(%rdx), %rbp
	movaps	%xmm7, 48(%rsp)
	.seh_savexmm %xmm7, 48
	movaps	%xmm6, 64(%rsp)
	.seh_savexmm %xmm6, 64
	.seh_endprologue
	movq	4032(%rbp), %rcx
	callq	mi_free
	movaps	64(%rsp), %xmm6
	movaps	48(%rsp), %xmm7
	.seh_startepilogue
	addq	$88, %rsp
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
.Lfunc_end21:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs7_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5LocalINtNtNtB7_4sync4list9IsElementBL_E8finalize,unique,21
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvXs7_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5LocalINtNtNtB7_4sync4list9IsElementBL_E8finalize,unique,6
	.p2align	2, 0x0
$cppxdata$_RNvXs7_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5LocalINtNtNtB7_4sync4list9IsElementBL_E8finalize:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNvXs7_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5LocalINtNtNtB7_4sync4list9IsElementBL_E8finalize@IMGREL
	.long	0
	.long	0
	.long	5
	.long	$ip2state$_RNvXs7_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5LocalINtNtNtB7_4sync4list9IsElementBL_E8finalize@IMGREL
	.long	4168
	.long	0
	.long	1
$stateUnwindMap$_RNvXs7_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5LocalINtNtNtB7_4sync4list9IsElementBL_E8finalize:
	.long	-1
	.long	"?dtor$23@?0?_RNvXs7_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5LocalINtNtNtB7_4sync4list9IsElementBL_E8finalize@4HA"@IMGREL
$ip2state$_RNvXs7_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5LocalINtNtNtB7_4sync4list9IsElementBL_E8finalize:
	.long	.Lfunc_begin21@IMGREL
	.long	-1
	.long	.Ltmp28@IMGREL
	.long	0
	.long	.Ltmp29@IMGREL
	.long	-1
	.long	.Ltmp26@IMGREL
	.long	0
	.long	.Ltmp27@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvXs7_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5LocalINtNtNtB7_4sync4list9IsElementBL_E8finalize,unique,21

	.def	_RNvXs_NtCs3qjAvHHmxHz_15crossbeam_epoch5guardNtB4_5GuardNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs_NtCs3qjAvHHmxHz_15crossbeam_epoch5guardNtB4_5GuardNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop,unique,22
	.p2align	4
_RNvXs_NtCs3qjAvHHmxHz_15crossbeam_epoch5guardNtB4_5GuardNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop:
.Lfunc_begin22:
	movq	(%rcx), %rcx
	testq	%rcx, %rcx
	je	.LBB22_3
	decq	2072(%rcx)
	jne	.LBB22_3
	movq	$0, 2176(%rcx)
	cmpq	$0, 2080(%rcx)
	je	_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize
.LBB22_3:
	retq
.Lfunc_end22:

	.section	.rdata,"dr",one_only,anon.a32227af679a3ead67a5cb195479eba7.0.llvm.14389155381977926352,unique,23
	.globl	anon.a32227af679a3ead67a5cb195479eba7.0.llvm.14389155381977926352
anon.a32227af679a3ead67a5cb195479eba7.0.llvm.14389155381977926352:
	.asciz	"C:\\Users\\there\\.cargo\\registry\\src\\index.crates.io-1949cf8c6b5b557f\\crossbeam-epoch-0.9.18\\src\\sync\\once_lock.rs"

	.section	.rdata,"dr",one_only,anon.a32227af679a3ead67a5cb195479eba7.1.llvm.14389155381977926352,unique,24
	.globl	anon.a32227af679a3ead67a5cb195479eba7.1.llvm.14389155381977926352
	.p2align	3, 0x0
anon.a32227af679a3ead67a5cb195479eba7.1.llvm.14389155381977926352:
	.quad	anon.a32227af679a3ead67a5cb195479eba7.0.llvm.14389155381977926352
	.asciz	"p\000\000\000\000\000\000\000B\000\000\000\023\000\000"

	.section	.rdata,"dr",one_only,anon.a32227af679a3ead67a5cb195479eba7.2.llvm.14389155381977926352,unique,25
	.globl	anon.a32227af679a3ead67a5cb195479eba7.2.llvm.14389155381977926352
	.p2align	3, 0x0
anon.a32227af679a3ead67a5cb195479eba7.2.llvm.14389155381977926352:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once9call_onceNCINvMs0_NtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync9once_lockINtB1b_8OnceLockNtNtB1f_9collector9CollectorE10initializeNvMs1_B2h_B2f_3newE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1f_.llvm.14389155381977926352
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvMs0_NtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync9once_lockINtB16_8OnceLockNtNtB1a_9collector9CollectorE10initializeNvMs1_B2c_B2a_3newE0E0B1a_.llvm.14389155381977926352

	.section	.rdata,"dr",one_only,anon.a32227af679a3ead67a5cb195479eba7.5,unique,26
anon.a32227af679a3ead67a5cb195479eba7.5:
	.ascii	"unaligned pointer"

	.section	.rdata,"dr",one_only,anon.a32227af679a3ead67a5cb195479eba7.6,unique,27
anon.a32227af679a3ead67a5cb195479eba7.6:
	.asciz	"C:\\Users\\there\\.cargo\\registry\\src\\index.crates.io-1949cf8c6b5b557f\\crossbeam-epoch-0.9.18\\src\\atomic.rs"

	.section	.rdata,"dr",one_only,anon.a32227af679a3ead67a5cb195479eba7.7,unique,28
	.p2align	3, 0x0
anon.a32227af679a3ead67a5cb195479eba7.7:
	.quad	anon.a32227af679a3ead67a5cb195479eba7.6
	.asciz	"h\000\000\000\000\000\000\000q\000\000\000\005\000\000"

	.section	.rdata,"dr",one_only,anon.a32227af679a3ead67a5cb195479eba7.8,unique,29
anon.a32227af679a3ead67a5cb195479eba7.8:
	.asciz	"/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\std\\src\\sync\\once.rs"

	.section	.rdata,"dr",one_only,anon.a32227af679a3ead67a5cb195479eba7.9,unique,30
	.p2align	3, 0x0
anon.a32227af679a3ead67a5cb195479eba7.9:
	.quad	anon.a32227af679a3ead67a5cb195479eba7.8
	.asciz	"L\000\000\000\000\000\000\000\246\000\000\0002\000\000"

	.section	.rdata,"dr",one_only,anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352,unique,31
	.globl	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352
	.p2align	3, 0x0
anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352:
	.quad	_RNvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB6_8Deferred5NO_OP10no_op_call.llvm.14389155381977926352
	.zero	24

	.section	.rdata,"dr",one_only,anon.a32227af679a3ead67a5cb195479eba7.11.llvm.14389155381977926352,unique,32
	.globl	anon.a32227af679a3ead67a5cb195479eba7.11.llvm.14389155381977926352
anon.a32227af679a3ead67a5cb195479eba7.11.llvm.14389155381977926352:
	.asciz	"C:\\Users\\there\\.cargo\\registry\\src\\index.crates.io-1949cf8c6b5b557f\\crossbeam-epoch-0.9.18\\src\\internal.rs"

	.section	.rdata,"dr",one_only,anon.a32227af679a3ead67a5cb195479eba7.12,unique,33
	.p2align	3, 0x0
anon.a32227af679a3ead67a5cb195479eba7.12:
	.quad	anon.a32227af679a3ead67a5cb195479eba7.11.llvm.14389155381977926352
	.asciz	"j\000\000\000\000\000\000\000\201\001\000\0009\000\000"

	.section	.tls$,"dw",one_only,_RNvNCNKNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default6HANDLE0023___RUST_STD_INTERNAL_VAL,unique,34
	.globl	_RNvNCNKNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default6HANDLE0023___RUST_STD_INTERNAL_VAL
	.p2align	3, 0x0
_RNvNCNKNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default6HANDLE0023___RUST_STD_INTERNAL_VAL:
	.zero	8
	.zero	1
	.zero	7

	.section	.rdata,"dr",one_only,_RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch5guard11unprotected11UNPROTECTED,unique,35
	.globl	_RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch5guard11unprotected11UNPROTECTED
	.p2align	3, 0x0
_RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch5guard11unprotected11UNPROTECTED:
	.zero	8

	.section	.data,"dw",one_only,_RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default9collector9COLLECTOR.llvm.14389155381977926352,unique,36
	.globl	_RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default9collector9COLLECTOR.llvm.14389155381977926352
	.p2align	3, 0x0
_RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default9collector9COLLECTOR.llvm.14389155381977926352:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.rdata,"dr",one_only,anon.a32227af679a3ead67a5cb195479eba7.15.llvm.14389155381977926352,unique,37
	.globl	anon.a32227af679a3ead67a5cb195479eba7.15.llvm.14389155381977926352
	.p2align	3, 0x0
anon.a32227af679a3ead67a5cb195479eba7.15.llvm.14389155381977926352:
	.quad	anon.a32227af679a3ead67a5cb195479eba7.11.llvm.14389155381977926352
	.asciz	"j\000\000\000\000\000\000\000w\000\000\000,\000\000"

	.section	.rdata,"dr",one_only,anon.a32227af679a3ead67a5cb195479eba7.16,unique,38
	.p2align	3, 0x0
anon.a32227af679a3ead67a5cb195479eba7.16:
	.asciz	"\001\000\000\000\000\000\000"

	.section	.rdata,"dr",one_only,anon.a32227af679a3ead67a5cb195479eba7.17,unique,39
anon.a32227af679a3ead67a5cb195479eba7.17:
	.asciz	"C:\\Users\\there\\.cargo\\registry\\src\\index.crates.io-1949cf8c6b5b557f\\crossbeam-epoch-0.9.18\\src\\sync\\list.rs"

	.section	.rdata,"dr",one_only,anon.a32227af679a3ead67a5cb195479eba7.18,unique,40
	.p2align	3, 0x0
anon.a32227af679a3ead67a5cb195479eba7.18:
	.quad	anon.a32227af679a3ead67a5cb195479eba7.17
	.asciz	"k\000\000\000\000\000\000\000\342\000\000\000\021\000\000"

	.section	.data,"dw",one_only,__imp_anon.a32227af679a3ead67a5cb195479eba7.0.llvm.14389155381977926352,unique,41
	.globl	__imp_anon.a32227af679a3ead67a5cb195479eba7.0.llvm.14389155381977926352
	.p2align	3, 0x0
__imp_anon.a32227af679a3ead67a5cb195479eba7.0.llvm.14389155381977926352:
	.quad	anon.a32227af679a3ead67a5cb195479eba7.0.llvm.14389155381977926352

	.section	.data,"dw",one_only,__imp_anon.a32227af679a3ead67a5cb195479eba7.1.llvm.14389155381977926352,unique,42
	.globl	__imp_anon.a32227af679a3ead67a5cb195479eba7.1.llvm.14389155381977926352
	.p2align	3, 0x0
__imp_anon.a32227af679a3ead67a5cb195479eba7.1.llvm.14389155381977926352:
	.quad	anon.a32227af679a3ead67a5cb195479eba7.1.llvm.14389155381977926352

	.section	.data,"dw",one_only,__imp_anon.a32227af679a3ead67a5cb195479eba7.2.llvm.14389155381977926352,unique,43
	.globl	__imp_anon.a32227af679a3ead67a5cb195479eba7.2.llvm.14389155381977926352
	.p2align	3, 0x0
__imp_anon.a32227af679a3ead67a5cb195479eba7.2.llvm.14389155381977926352:
	.quad	anon.a32227af679a3ead67a5cb195479eba7.2.llvm.14389155381977926352

	.section	.data,"dw",one_only,__imp_anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352,unique,44
	.globl	__imp_anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352
	.p2align	3, 0x0
__imp_anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352:
	.quad	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352

	.section	.data,"dw",one_only,__imp_anon.a32227af679a3ead67a5cb195479eba7.11.llvm.14389155381977926352,unique,45
	.globl	__imp_anon.a32227af679a3ead67a5cb195479eba7.11.llvm.14389155381977926352
	.p2align	3, 0x0
__imp_anon.a32227af679a3ead67a5cb195479eba7.11.llvm.14389155381977926352:
	.quad	anon.a32227af679a3ead67a5cb195479eba7.11.llvm.14389155381977926352

	.section	.data,"dw",one_only,__imp__RNvNCNKNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default6HANDLE0023___RUST_STD_INTERNAL_VAL,unique,46
	.globl	__imp__RNvNCNKNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default6HANDLE0023___RUST_STD_INTERNAL_VAL
	.p2align	3, 0x0
__imp__RNvNCNKNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default6HANDLE0023___RUST_STD_INTERNAL_VAL:
	.quad	_RNvNCNKNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default6HANDLE0023___RUST_STD_INTERNAL_VAL

	.section	.data,"dw",one_only,__imp__RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch5guard11unprotected11UNPROTECTED,unique,47
	.globl	__imp__RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch5guard11unprotected11UNPROTECTED
	.p2align	3, 0x0
__imp__RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch5guard11unprotected11UNPROTECTED:
	.quad	_RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch5guard11unprotected11UNPROTECTED

	.section	.data,"dw",one_only,__imp__RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default9collector9COLLECTOR.llvm.14389155381977926352,unique,48
	.globl	__imp__RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default9collector9COLLECTOR.llvm.14389155381977926352
	.p2align	3, 0x0
__imp__RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default9collector9COLLECTOR.llvm.14389155381977926352:
	.quad	_RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default9collector9COLLECTOR.llvm.14389155381977926352

	.section	.data,"dw",one_only,__imp_anon.a32227af679a3ead67a5cb195479eba7.15.llvm.14389155381977926352,unique,49
	.globl	__imp_anon.a32227af679a3ead67a5cb195479eba7.15.llvm.14389155381977926352
	.p2align	3, 0x0
__imp_anon.a32227af679a3ead67a5cb195479eba7.15.llvm.14389155381977926352:
	.quad	anon.a32227af679a3ead67a5cb195479eba7.15.llvm.14389155381977926352

	.section	.debug$S,"dr"
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp31-.Ltmp30
.Ltmp30:
	.short	.Ltmp33-.Ltmp32
.Ltmp32:
	.short	4353
	.long	0
	.asciz	"S:\\GTOpen-research\\postflop-gpu-20261016\\runs\\D090-wide-OR\\build\\probe.crossbeam_epoch-83f0dcc2dba25447.crossbeam_epoch.27e2fe8bd748cd73-cgu.0.rcgu.o.rcgu.o"
	.p2align	2, 0x0
.Ltmp33:
	.short	.Ltmp35-.Ltmp34
.Ltmp34:
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
.Ltmp35:
.Ltmp31:
	.p2align	2, 0x0
	.cv_filechecksums
	.cv_stringtable
	.long	241
	.long	.Ltmp37-.Ltmp36
.Ltmp36:
	.short	.Ltmp39-.Ltmp38
.Ltmp38:
	.short	4428
	.long	4099
	.p2align	2, 0x0
.Ltmp39:
.Ltmp37:
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
