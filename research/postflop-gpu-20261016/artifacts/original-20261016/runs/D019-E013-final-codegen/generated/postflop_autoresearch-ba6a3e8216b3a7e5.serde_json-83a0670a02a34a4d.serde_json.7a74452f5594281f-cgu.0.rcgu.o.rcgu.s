	.def	@feat.00;
	.scl	3;
	.type	0;
	.endef
	.globl	@feat.00
@feat.00 = 0
	.file	"serde_json.7a74452f5594281f-cgu.0"
	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNvXsy_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtBK_8IntoIterpppENtNtNtB4_3ops4drop4Drop4drop9DropGuardNtNtBQ_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueNtNtBQ_5alloc6GlobalEEB2R_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNvXsy_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtBK_8IntoIterpppENtNtNtB4_3ops4drop4Drop4drop9DropGuardNtNtBQ_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueNtNtBQ_5alloc6GlobalEEB2R_,unique,0
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNvXsy_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtBK_8IntoIterpppENtNtNtB4_3ops4drop4Drop4drop9DropGuardNtNtBQ_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueNtNtBQ_5alloc6GlobalEEB2R_:
.Lfunc_begin0:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNvXsy_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtBK_8IntoIterpppENtNtNtB4_3ops4drop4Drop4drop9DropGuardNtNtBQ_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueNtNtBQ_5alloc6GlobalEEB2R_
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$56, %rsp
	.seh_stackalloc 56
	.seh_endprologue
	movq	(%rcx), %rsi
	leaq	32(%rsp), %rcx
	movq	%rsi, %rdx
	callq	_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_
	movq	32(%rsp), %rbx
	testq	%rbx, %rbx
	je	.LBB0_5
	leaq	32(%rsp), %rdi
	jmp	.LBB0_2
	.p2align	4
.LBB0_4:
	shlq	$5, %r14
	addq	%r14, %rbx
	movq	%rbx, %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	callq	_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_
	movq	32(%rsp), %rbx
	testq	%rbx, %rbx
	je	.LBB0_5
.LBB0_2:
	movq	48(%rsp), %r14
	leaq	(%r14,%r14,2), %rax
	cmpq	$0, 360(%rbx,%rax,8)
	je	.LBB0_4
	leaq	(%rbx,%rax,8), %rax
	addq	$360, %rax
	movq	8(%rax), %rcx
	callq	mi_free
	jmp	.LBB0_4
.LBB0_5:
	.seh_startepilogue
	addq	$56, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.Lfunc_end0:
	.seh_endproc

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5error9ErrorCodeEBF_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5error9ErrorCodeEBF_,unique,1
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5error9ErrorCodeEBF_:
.Lfunc_begin1:
	movq	(%rcx), %rax
	testq	%rax, %rax
	je	.LBB1_3
	cmpl	$1, %eax
	jne	.LBB1_2
	movq	8(%rcx), %rax
	movl	%eax, %ecx
	andl	$3, %ecx
	leal	-2(%rcx), %edx
	cmpl	$2, %edx
	jb	.LBB1_2
	testq	%rcx, %rcx
	je	.LBB1_2
	leaq	-1(%rax), %rcx
	rex64 jmpq	*23(%rax)
.LBB1_3:
	cmpq	$0, 16(%rcx)
	je	.LBB1_2
	movq	8(%rcx), %rcx
	jmp	mi_free
.LBB1_2:
	retq
.Lfunc_end1:

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5error9ErrorImplEBF_.llvm.16186315980599473920;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5error9ErrorImplEBF_.llvm.16186315980599473920,unique,2
	.globl	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5error9ErrorImplEBF_.llvm.16186315980599473920
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5error9ErrorImplEBF_.llvm.16186315980599473920:
.Lfunc_begin2:
	movq	(%rcx), %rax
	cmpq	$1, %rax
	je	.LBB2_4
	testq	%rax, %rax
	jne	.LBB2_6
	cmpq	$0, 16(%rcx)
	je	.LBB2_6
	movq	8(%rcx), %rcx
	jmp	mi_free
.LBB2_4:
	movq	8(%rcx), %rax
	movl	%eax, %ecx
	andl	$3, %ecx
	leal	-2(%rcx), %edx
	cmpl	$2, %edx
	jb	.LBB2_6
	testq	%rcx, %rcx
	jne	.LBB2_7
.LBB2_6:
	retq
.LBB2_7:
	leaq	-1(%rax), %rcx
	rex64 jmpq	*23(%rax)
.Lfunc_end2:

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920,unique,3
	.globl	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920:
.Lfunc_begin3:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920
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
	subq	$176, %rsp
	.seh_stackalloc 176
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	movq	$-2, 40(%rbp)
	movzbl	(%rcx), %eax
	cmpl	$3, %eax
	jae	.LBB3_1
.LBB3_12:
	.seh_startepilogue
	addq	$176, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.LBB3_1:
	je	.LBB3_13
	cmpl	$4, %eax
	jne	.LBB3_3
	movq	16(%rcx), %rax
	movq	%rcx, 16(%rbp)
	movq	24(%rcx), %rcx
	movq	%rcx, 8(%rbp)
	movq	$0, 24(%rbp)
	movq	%rax, 32(%rbp)
	movq	%rax, %rcx
	.p2align	4
.LBB3_17:
	movq	24(%rbp), %rax
	cmpq	%rax, 8(%rbp)
	je	.LBB3_26
	incq	%rax
	movq	%rax, 24(%rbp)
	leaq	32(%rcx), %rsi
.Ltmp0:
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920
	nop
.Ltmp1:
	movq	%rsi, %rcx
	jmp	.LBB3_17
.LBB3_13:
	cmpq	$0, 8(%rcx)
	je	.LBB3_12
	movq	16(%rcx), %rcx
	jmp	.LBB3_15
.LBB3_3:
	movq	8(%rcx), %r8
	testq	%r8, %r8
	je	.LBB3_4
	movq	16(%rcx), %rdx
	movq	24(%rcx), %rax
	movq	$0, -88(%rbp)
	movq	%r8, -80(%rbp)
	movq	%rdx, -72(%rbp)
	movq	$0, -56(%rbp)
	movq	%r8, -48(%rbp)
	movq	%rdx, -40(%rbp)
	movl	$1, %ecx
	jmp	.LBB3_6
.LBB3_26:
	movq	16(%rbp), %rax
	cmpq	$0, 8(%rax)
	je	.LBB3_12
	movq	32(%rbp), %rcx
.LBB3_15:
	.seh_startepilogue
	addq	$176, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	jmp	mi_free
.LBB3_4:
	xorl	%ecx, %ecx
	xorl	%eax, %eax
.LBB3_6:
	movq	%rcx, -96(%rbp)
	movq	%rcx, -64(%rbp)
	movq	%rax, -32(%rbp)
	leaq	-24(%rbp), %rcx
	leaq	-96(%rbp), %rsi
	movq	%rsi, %rdx
	callq	_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_
	movq	-24(%rbp), %rbx
	testq	%rbx, %rbx
	je	.LBB3_12
	leaq	-24(%rbp), %rdi
	.p2align	4
.LBB3_8:
	movq	-8(%rbp), %r14
	movq	%rsi, (%rbp)
	leaq	(%r14,%r14,2), %rax
	cmpq	$0, 360(%rbx,%rax,8)
	je	.LBB3_10
	leaq	(%rbx,%rax,8), %rax
	addq	$360, %rax
	movq	8(%rax), %rcx
	callq	mi_free
	nop
.LBB3_10:
.Ltmp2:
	shlq	$5, %r14
	addq	%r14, %rbx
	movq	%rbx, %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920
	nop
.Ltmp3:
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	callq	_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_
	movq	-24(%rbp), %rbx
	testq	%rbx, %rbx
	jne	.LBB3_8
	jmp	.LBB3_12
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920@IMGREL
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920,unique,3
	.seh_endproc
	.def	"?dtor$19@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$19@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920@4HA":
.seh_proc "?dtor$19@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920@4HA"
.LBB3_19:
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
	movq	32(%rbp), %rsi
	movq	24(%rbp), %rdi
	cmpq	8(%rbp), %rdi
	je	.LBB3_22
	.p2align	4
.LBB3_21:
	movq	%rdi, %rcx
	shlq	$5, %rcx
	addq	%rsi, %rcx
	incq	%rdi
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920
	cmpq	8(%rbp), %rdi
	jne	.LBB3_21
.LBB3_22:
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
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920,unique,3
	.seh_endproc
	.def	"?dtor$23@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$23@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920@4HA":
.seh_proc "?dtor$23@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920@4HA"
.LBB3_23:
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
	movq	16(%rbp), %rax
	cmpq	$0, 8(%rax)
	je	.LBB3_25
	movq	32(%rbp), %rcx
	callq	mi_free
	nop
.LBB3_25:
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
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920,unique,3
	.seh_endproc
	.def	"?dtor$28@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$28@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920@4HA":
.seh_proc "?dtor$28@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920@4HA"
.LBB3_28:
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
	movq	%rbp, %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNvXsy_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtBK_8IntoIterpppENtNtNtB4_3ops4drop4Drop4drop9DropGuardNtNtBQ_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueNtNtBQ_5alloc6GlobalEEB2R_
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
.Lfunc_end3:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920,unique,3
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920,unique,0
	.p2align	2, 0x0
$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920:
	.long	429065506
	.long	3
	.long	$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920@IMGREL
	.long	0
	.long	0
	.long	5
	.long	$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920@IMGREL
	.long	168
	.long	0
	.long	1
$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920:
	.long	-1
	.long	"?dtor$28@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920@4HA"@IMGREL
	.long	-1
	.long	"?dtor$23@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920@4HA"@IMGREL
	.long	1
	.long	"?dtor$19@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920@4HA"@IMGREL
$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920:
	.long	.Lfunc_begin3@IMGREL
	.long	-1
	.long	.Ltmp0@IMGREL
	.long	2
	.long	.Ltmp1@IMGREL
	.long	-1
	.long	.Ltmp2@IMGREL
	.long	0
	.long	.Ltmp3@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920,unique,3

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsfQUUnEvlYZE_5alloc6string6StringECsavOST1yGCNT_10serde_json;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsfQUUnEvlYZE_5alloc6string6StringECsavOST1yGCNT_10serde_json,unique,4
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsfQUUnEvlYZE_5alloc6string6StringECsavOST1yGCNT_10serde_json:
.Lfunc_begin4:
	cmpq	$0, (%rcx)
	je	.LBB4_1
	movq	8(%rcx), %rcx
	jmp	mi_free
.LBB4_1:
	retq
.Lfunc_end4:

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueTNtNtCsfQUUnEvlYZE_5alloc6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueEEB1i_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueTNtNtCsfQUUnEvlYZE_5alloc6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueEEB1i_,unique,5
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueTNtNtCsfQUUnEvlYZE_5alloc6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueEEB1i_:
.Lfunc_begin5:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueTNtNtCsfQUUnEvlYZE_5alloc6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueEEB1i_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	cmpq	$0, (%rcx)
	je	.LBB5_2
	movq	8(%rcx), %rax
	movq	%rcx, %rsi
	movq	%rax, %rcx
	callq	mi_free
	movq	%rsi, %rcx
.LBB5_2:
	addq	$24, %rcx
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	jmp	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920
.Lfunc_end5:
	.seh_endproc

	.def	_RINvNtCsavOST1yGCNT_10serde_json4read20parse_unicode_escapeNtB2_9SliceReadEB4_;
	.scl	3;
	.type	32;
	.endef
	.globl	__xmm@0000000000000000000000003f3f3fff
	.section	.rdata,"dr",discard,__xmm@0000000000000000000000003f3f3fff
	.p2align	4, 0x0
__xmm@0000000000000000000000003f3f3fff:
	.byte	255
	.byte	63
	.byte	63
	.byte	63
	.zero	1
	.zero	1
	.zero	1
	.zero	1
	.zero	1
	.zero	1
	.zero	1
	.zero	1
	.zero	1
	.zero	1
	.zero	1
	.zero	1
	.globl	__xmm@000000000000000000000000808080f0
	.section	.rdata,"dr",discard,__xmm@000000000000000000000000808080f0
	.p2align	4, 0x0
__xmm@000000000000000000000000808080f0:
	.byte	240
	.byte	128
	.byte	128
	.byte	128
	.zero	1
	.zero	1
	.zero	1
	.zero	1
	.zero	1
	.zero	1
	.zero	1
	.zero	1
	.zero	1
	.zero	1
	.zero	1
	.zero	1
	.section	.text$unlikely,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read20parse_unicode_escapeNtB2_9SliceReadEB4_,unique,6
	.p2align	4
_RINvNtCsavOST1yGCNT_10serde_json4read20parse_unicode_escapeNtB2_9SliceReadEB4_:
.Lfunc_begin6:
.seh_proc _RINvNtCsavOST1yGCNT_10serde_json4read20parse_unicode_escapeNtB2_9SliceReadEB4_
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
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	8(%rcx), %rbx
	movq	16(%rcx), %r14
	movq	%rbx, %rax
	subq	%r14, %rax
	jb	.LBB6_42
	movq	%rdx, %rsi
	movq	%rcx, %rdi
	cmpq	$3, %rax
	jbe	.LBB6_4
	movq	(%rdi), %rax
	movzbl	(%rax,%r14), %ecx
	movzbl	1(%rax,%r14), %edx
	movzbl	2(%rax,%r14), %r8d
	movzbl	3(%rax,%r14), %eax
	addq	$4, %r14
	movq	%r14, 16(%rdi)
	leaq	_RNvNtCsavOST1yGCNT_10serde_json4read4HEX1(%rip), %r9
	leaq	_RNvNtCsavOST1yGCNT_10serde_json4read4HEX0(%rip), %r10
	movzwl	(%r10,%rdx,2), %edx
	movswl	(%r9,%r8,2), %r8d
	movswl	(%r10,%rax,2), %r10d
	orw	(%r9,%rcx,2), %dx
	movswl	%dx, %eax
	shll	$8, %eax
	orl	%r8d, %eax
	orl	%r10d, %eax
	js	.LBB6_6
	movw	%ax, 42(%rsp)
	movw	$0, 40(%rsp)
	cmpw	$1, 40(%rsp)
	je	.LBB6_5
	jmp	.LBB6_7
.LBB6_4:
	movq	%rbx, 16(%rdi)
	movq	$4, 56(%rsp)
	leaq	40(%rsp), %rcx
	leaq	56(%rsp), %r8
	movq	%rdi, %rdx
	callq	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_
	movq	%rbx, %r14
	cmpw	$1, 40(%rsp)
	jne	.LBB6_7
	jmp	.LBB6_5
.LBB6_6:
	movq	$12, 56(%rsp)
	leaq	40(%rsp), %rcx
	leaq	56(%rsp), %r8
	movq	%rdi, %rdx
	callq	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_
	cmpw	$1, 40(%rsp)
	je	.LBB6_5
.LBB6_7:
	movzwl	42(%rsp), %r15d
	movl	%r15d, %eax
	andl	$64512, %eax
	cmpl	$56320, %eax
	jne	.LBB6_9
.LBB6_8:
	movq	$20, 56(%rsp)
	jmp	.LBB6_32
.LBB6_9:
	leal	9216(%r15), %eax
	movzwl	%ax, %eax
	cmpl	$64512, %eax
	jae	.LBB6_14
	movzwl	%r15w, %edi
	cmpl	$128, %edi
	jae	.LBB6_16
	movq	16(%rsi), %rdi
	cmpq	(%rsi), %rdi
	jne	.LBB6_13
	movq	%rsi, %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVechE8grow_oneB7_
.LBB6_13:
	movq	8(%rsi), %rax
	movb	%r15b, (%rax,%rdi)
	incq	%rdi
	movq	%rdi, 16(%rsi)
	xorl	%eax, %eax
	jmp	.LBB6_33
.LBB6_14:
	movq	(%rdi), %r12
	cmpq	%rbx, %r14
	jae	.LBB6_19
	movzbl	(%r12,%r14), %ecx
	leaq	1(%r14), %rax
	movq	%rax, 16(%rdi)
	cmpb	$92, %cl
	je	.LBB6_22
	jmp	.LBB6_31
.LBB6_16:
	movq	(%rsi), %rax
	movq	16(%rsi), %rdx
	subq	%rdx, %rax
	cmpq	$3, %rax
	jbe	.LBB6_43
	movq	8(%rsi), %rax
	addq	%rdx, %rax
	cmpl	$2048, %edi
	jae	.LBB6_44
.LBB6_18:
	movl	%r15d, %ecx
	shrl	$6, %ecx
	orb	$-64, %cl
	movl	$2, %r8d
	jmp	.LBB6_45
.LBB6_19:
	movq	$4, 56(%rsp)
	leaq	40(%rsp), %rcx
	leaq	56(%rsp), %r8
	movq	%rdi, %rdx
	callq	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_
	cmpb	$1, 40(%rsp)
	je	.LBB6_5
	movzbl	41(%rsp), %ecx
	leaq	1(%r14), %rax
	movq	%rax, 16(%rdi)
	cmpb	$92, %cl
	jne	.LBB6_31
.LBB6_22:
	cmpq	%rbx, %rax
	jae	.LBB6_28
	movzbl	(%r12,%rax), %eax
	leaq	2(%r14), %rcx
	movq	%rcx, 16(%rdi)
	cmpb	$117, %al
	jne	.LBB6_31
.LBB6_24:
	movq	%rbx, %rax
	subq	%rcx, %rax
	jb	.LBB6_47
	cmpq	$3, %rax
	jbe	.LBB6_34
	movzbl	2(%r12,%r14), %eax
	movzbl	3(%r12,%r14), %ecx
	movzbl	4(%r12,%r14), %edx
	movzbl	5(%r12,%r14), %r8d
	addq	$6, %r14
	movq	%r14, 16(%rdi)
	leaq	_RNvNtCsavOST1yGCNT_10serde_json4read4HEX1(%rip), %r9
	leaq	_RNvNtCsavOST1yGCNT_10serde_json4read4HEX0(%rip), %r10
	movzwl	(%r10,%rcx,2), %ecx
	movswl	(%r9,%rdx,2), %edx
	movswl	(%r10,%r8,2), %r8d
	orw	(%r9,%rax,2), %cx
	movswl	%cx, %eax
	shll	$8, %eax
	orl	%edx, %eax
	orl	%r8d, %eax
	js	.LBB6_35
	movw	%ax, 42(%rsp)
	movw	$0, 40(%rsp)
	jmp	.LBB6_37
.LBB6_28:
	movq	$4, 56(%rsp)
	leaq	40(%rsp), %rcx
	leaq	56(%rsp), %r8
	movq	%rdi, %rdx
	callq	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_
	cmpb	$0, 40(%rsp)
	jne	.LBB6_5
	movzbl	41(%rsp), %eax
	leaq	2(%r14), %rcx
	movq	%rcx, 16(%rdi)
	cmpb	$117, %al
	je	.LBB6_24
.LBB6_31:
	movq	$23, 56(%rsp)
.LBB6_32:
	leaq	56(%rsp), %rdx
	movq	%rdi, %rcx
	callq	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_
	jmp	.LBB6_33
.LBB6_34:
	movq	%rbx, 16(%rdi)
	movq	$4, 56(%rsp)
	jmp	.LBB6_36
.LBB6_35:
	movq	$12, 56(%rsp)
.LBB6_36:
	leaq	40(%rsp), %rcx
	leaq	56(%rsp), %r8
	movq	%rdi, %rdx
	callq	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_
.LBB6_37:
	cmpb	$0, 40(%rsp)
	je	.LBB6_39
.LBB6_5:
	movq	48(%rsp), %rax
.LBB6_33:
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r14
	popq	%r15
	.seh_endepilogue
	retq
.LBB6_39:
	movzwl	42(%rsp), %ebx
	leal	8192(%rbx), %eax
	movzwl	%ax, %eax
	cmpl	$64512, %eax
	jb	.LBB6_8
	addl	$10240, %r15d
	movzwl	%r15w, %edi
	shll	$10, %edi
	leal	9216(%rbx), %eax
	movzwl	%ax, %eax
	movl	%edi, %ecx
	orl	%eax, %edi
	leal	(%rcx,%rax), %ebp
	addl	$65536, %ebp
	movq	(%rsi), %rax
	movq	16(%rsi), %rdx
	subq	%rdx, %rax
	cmpq	$3, %rax
	jbe	.LBB6_48
.LBB6_41:
	movq	8(%rsi), %rax
	movl	%ebp, %ecx
	shrl	$18, %ecx
	shrl	$4, %ebp
	andl	$65280, %ebp
	orl	%ecx, %ebp
	shll	$10, %edi
	andl	$16711680, %edi
	orl	%ebp, %edi
	shll	$24, %ebx
	orl	%edi, %ebx
	movd	%ebx, %xmm0
	pand	__xmm@0000000000000000000000003f3f3fff(%rip), %xmm0
	por	__xmm@000000000000000000000000808080f0(%rip), %xmm0
	movd	%xmm0, (%rax,%rdx)
	addq	$4, %rdx
	jmp	.LBB6_46
.LBB6_42:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.108(%rip), %r9
	movq	%r14, %rcx
	movq	%rbx, %rdx
	movq	%rbx, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	ud2
.LBB6_43:
	movl	$4, %r8d
	movq	%rsi, %rcx
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECsavOST1yGCNT_10serde_json
	movq	16(%rsi), %rdx
	movq	8(%rsi), %rax
	addq	%rdx, %rax
	cmpl	$2048, %edi
	jb	.LBB6_18
.LBB6_44:
	movl	%edi, %ecx
	shrl	$12, %ecx
	orb	$-32, %cl
	shrl	$6, %edi
	andb	$63, %dil
	orb	$-128, %dil
	movb	%dil, 1(%rax)
	movl	$3, %r8d
.LBB6_45:
	movb	%cl, (%rax)
	andb	$63, %r15b
	orb	$-128, %r15b
	movb	%r15b, -1(%rax,%r8)
	addq	%r8, %rdx
.LBB6_46:
	movq	%rdx, 16(%rsi)
	xorl	%eax, %eax
	jmp	.LBB6_33
.LBB6_47:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.108(%rip), %r9
	movq	%rbx, %rdx
	movq	%rbx, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	ud2
.LBB6_48:
	movl	$4, %r8d
	movq	%rsi, %rcx
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECsavOST1yGCNT_10serde_json
	movq	16(%rsi), %rdx
	jmp	.LBB6_41
.Lfunc_end6:
	.seh_endproc

	.def	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_,unique,7
	.p2align	4
_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_:
.Lfunc_begin7:
.seh_proc _RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_
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
	subq	$56, %rsp
	.seh_stackalloc 56
	leaq	48(%rsp), %rbp
	.seh_setframe %rbp, 48
	.seh_endprologue
	movq	$-2, (%rbp)
	movq	%r8, -16(%rbp)
	movq	16(%rdx), %rdi
	movq	8(%rdx), %rbx
	cmpq	%rbx, %rdi
	ja	.LBB7_9
	movq	%rcx, %rsi
	movq	(%rdx), %r14
	leaq	(%r14,%rdi), %r8
	movq	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw2FN(%rip), %rax
	movb	$1, -1(%rbp)
.Ltmp4:
	movb	$10, %cl
	movq	%r14, %rdx
	callq	*%rax
	nop
.Ltmp5:
	cmpq	$1, %rax
	jne	.LBB7_3
	subq	%r14, %rdx
	leaq	1(%rdx), %r15
	cmpq	%rbx, %rdx
	jb	.LBB7_4
	movb	$1, -1(%rbp)
.Ltmp6:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920(%rip), %r9
	xorl	%ecx, %ecx
	movq	%r15, %rdx
	movq	%rbx, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	nop
.Ltmp7:
	jmp	.LBB7_10
.LBB7_3:
	xorl	%r15d, %r15d
.LBB7_4:
	leaq	(%r14,%r15), %r8
	movq	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw2FN(%rip), %rax
	movb	$1, -1(%rbp)
.Ltmp8:
	movb	$10, %cl
	movq	%r14, %rdx
	callq	*%rax
	nop
.Ltmp9:
	incq	%rax
	subq	%r15, %rdi
	movb	$0, -1(%rbp)
.Ltmp10:
	movq	-16(%rbp), %rcx
	movq	%rax, %rdx
	movq	%rdi, %r8
	callq	_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax
	nop
.Ltmp11:
	movq	%rax, 8(%rsi)
	movq	$2, (%rsi)
	.seh_startepilogue
	addq	$56, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
.LBB7_9:
	movb	$1, -1(%rbp)
.Ltmp12:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.48.llvm.16186315980599473920(%rip), %r9
	xorl	%ecx, %ecx
	movq	%rdi, %rdx
	movq	%rbx, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	nop
.Ltmp13:
.LBB7_10:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_@IMGREL
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_,unique,7
	.seh_endproc
	.def	"?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_@4HA":
.seh_proc "?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_@4HA"
.LBB7_11:
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
	leaq	48(%rdx), %rbp
	.seh_endprologue
	cmpb	$0, -1(%rbp)
	jne	.LBB7_12
.LBB7_13:
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
.LBB7_12:
	movq	-16(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5error9ErrorCodeEBF_
	jmp	.LBB7_13
.Lfunc_end7:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_,unique,7
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_,unique,1
	.p2align	2, 0x0
$cppxdata$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_@IMGREL
	.long	48
	.long	0
	.long	1
$stateUnwindMap$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_:
	.long	-1
	.long	"?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_@4HA"@IMGREL
$ip2state$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_:
	.long	.Lfunc_begin7@IMGREL
	.long	-1
	.long	.Ltmp4@IMGREL
	.long	0
	.long	.Ltmp13@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_,unique,7

	.def	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_,unique,8
	.p2align	4
_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_:
.Lfunc_begin8:
.seh_proc _RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_
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
	subq	$56, %rsp
	.seh_stackalloc 56
	leaq	48(%rsp), %rbp
	.seh_setframe %rbp, 48
	.seh_endprologue
	movq	$-2, (%rbp)
	movq	%r8, -16(%rbp)
	movq	16(%rdx), %rdi
	movq	8(%rdx), %rbx
	cmpq	%rbx, %rdi
	ja	.LBB8_9
	movq	%rcx, %rsi
	movq	(%rdx), %r14
	leaq	(%r14,%rdi), %r8
	movq	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw2FN(%rip), %rax
	movb	$1, -1(%rbp)
.Ltmp14:
	movb	$10, %cl
	movq	%r14, %rdx
	callq	*%rax
	nop
.Ltmp15:
	cmpq	$1, %rax
	jne	.LBB8_3
	subq	%r14, %rdx
	leaq	1(%rdx), %r15
	cmpq	%rbx, %rdx
	jb	.LBB8_4
	movb	$1, -1(%rbp)
.Ltmp16:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920(%rip), %r9
	xorl	%ecx, %ecx
	movq	%r15, %rdx
	movq	%rbx, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	nop
.Ltmp17:
	jmp	.LBB8_10
.LBB8_3:
	xorl	%r15d, %r15d
.LBB8_4:
	leaq	(%r14,%r15), %r8
	movq	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw2FN(%rip), %rax
	movb	$1, -1(%rbp)
.Ltmp18:
	movb	$10, %cl
	movq	%r14, %rdx
	callq	*%rax
	nop
.Ltmp19:
	incq	%rax
	subq	%r15, %rdi
	movb	$0, -1(%rbp)
.Ltmp20:
	movq	-16(%rbp), %rcx
	movq	%rax, %rdx
	movq	%rdi, %r8
	callq	_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax
	nop
.Ltmp21:
	movq	%rax, 8(%rsi)
	movb	$1, (%rsi)
	.seh_startepilogue
	addq	$56, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
.LBB8_9:
	movb	$1, -1(%rbp)
.Ltmp22:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.48.llvm.16186315980599473920(%rip), %r9
	xorl	%ecx, %ecx
	movq	%rdi, %rdx
	movq	%rbx, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	nop
.Ltmp23:
.LBB8_10:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_@IMGREL
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_,unique,8
	.seh_endproc
	.def	"?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_@4HA":
.seh_proc "?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_@4HA"
.LBB8_11:
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
	leaq	48(%rdx), %rbp
	.seh_endprologue
	cmpb	$0, -1(%rbp)
	jne	.LBB8_12
.LBB8_13:
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
.LBB8_12:
	movq	-16(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5error9ErrorCodeEBF_
	jmp	.LBB8_13
.Lfunc_end8:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_,unique,8
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_,unique,2
	.p2align	2, 0x0
$cppxdata$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_@IMGREL
	.long	48
	.long	0
	.long	1
$stateUnwindMap$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_:
	.long	-1
	.long	"?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_@4HA"@IMGREL
$ip2state$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_:
	.long	.Lfunc_begin8@IMGREL
	.long	-1
	.long	.Ltmp14@IMGREL
	.long	0
	.long	.Ltmp23@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_,unique,8

	.def	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_,unique,9
	.p2align	4
_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_:
.Lfunc_begin9:
.seh_proc _RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_
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
	subq	$56, %rsp
	.seh_stackalloc 56
	leaq	48(%rsp), %rbp
	.seh_setframe %rbp, 48
	.seh_endprologue
	movq	$-2, (%rbp)
	movq	%r8, -16(%rbp)
	movq	16(%rdx), %rdi
	movq	8(%rdx), %rbx
	cmpq	%rbx, %rdi
	ja	.LBB9_9
	movq	%rcx, %rsi
	movq	(%rdx), %r14
	leaq	(%r14,%rdi), %r8
	movq	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw2FN(%rip), %rax
	movb	$1, -1(%rbp)
.Ltmp24:
	movb	$10, %cl
	movq	%r14, %rdx
	callq	*%rax
	nop
.Ltmp25:
	cmpq	$1, %rax
	jne	.LBB9_3
	subq	%r14, %rdx
	leaq	1(%rdx), %r15
	cmpq	%rbx, %rdx
	jb	.LBB9_4
	movb	$1, -1(%rbp)
.Ltmp26:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920(%rip), %r9
	xorl	%ecx, %ecx
	movq	%r15, %rdx
	movq	%rbx, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	nop
.Ltmp27:
	jmp	.LBB9_10
.LBB9_3:
	xorl	%r15d, %r15d
.LBB9_4:
	leaq	(%r14,%r15), %r8
	movq	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw2FN(%rip), %rax
	movb	$1, -1(%rbp)
.Ltmp28:
	movb	$10, %cl
	movq	%r14, %rdx
	callq	*%rax
	nop
.Ltmp29:
	incq	%rax
	subq	%r15, %rdi
	movb	$0, -1(%rbp)
.Ltmp30:
	movq	-16(%rbp), %rcx
	movq	%rax, %rdx
	movq	%rdi, %r8
	callq	_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax
	nop
.Ltmp31:
	movq	%rax, 8(%rsi)
	movw	$1, (%rsi)
	.seh_startepilogue
	addq	$56, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
.LBB9_9:
	movb	$1, -1(%rbp)
.Ltmp32:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.48.llvm.16186315980599473920(%rip), %r9
	xorl	%ecx, %ecx
	movq	%rdi, %rdx
	movq	%rbx, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	nop
.Ltmp33:
.LBB9_10:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_@IMGREL
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_,unique,9
	.seh_endproc
	.def	"?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_@4HA":
.seh_proc "?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_@4HA"
.LBB9_11:
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
	leaq	48(%rdx), %rbp
	.seh_endprologue
	cmpb	$0, -1(%rbp)
	jne	.LBB9_12
.LBB9_13:
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
.LBB9_12:
	movq	-16(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5error9ErrorCodeEBF_
	jmp	.LBB9_13
.Lfunc_end9:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_,unique,9
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_,unique,3
	.p2align	2, 0x0
$cppxdata$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_@IMGREL
	.long	48
	.long	0
	.long	1
$stateUnwindMap$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_:
	.long	-1
	.long	"?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_@4HA"@IMGREL
$ip2state$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_:
	.long	.Lfunc_begin9@IMGREL
	.long	-1
	.long	.Ltmp24@IMGREL
	.long	0
	.long	.Ltmp33@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_,unique,9

	.def	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_,unique,10
	.p2align	4
_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_:
.Lfunc_begin10:
.seh_proc _RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_
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
	subq	$64, %rsp
	.seh_stackalloc 64
	leaq	64(%rsp), %rbp
	.seh_setframe %rbp, 64
	.seh_endprologue
	movq	$-2, -8(%rbp)
	movq	%rdx, -24(%rbp)
	movq	16(%rcx), %rsi
	movq	8(%rcx), %rdi
	cmpq	%rdi, %rsi
	ja	.LBB10_9
	movq	(%rcx), %rbx
	leaq	(%rbx,%rsi), %r8
	movq	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw2FN(%rip), %rax
	movb	$1, -9(%rbp)
.Ltmp34:
	movb	$10, %cl
	movq	%rbx, %rdx
	callq	*%rax
	nop
.Ltmp35:
	cmpq	$1, %rax
	jne	.LBB10_3
	subq	%rbx, %rdx
	leaq	1(%rdx), %r14
	cmpq	%rdi, %rdx
	jb	.LBB10_4
	movb	$1, -9(%rbp)
.Ltmp36:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920(%rip), %r9
	xorl	%ecx, %ecx
	movq	%r14, %rdx
	movq	%rdi, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	nop
.Ltmp37:
	jmp	.LBB10_10
.LBB10_3:
	xorl	%r14d, %r14d
.LBB10_4:
	leaq	(%rbx,%r14), %r8
	movq	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw2FN(%rip), %rax
	movb	$1, -9(%rbp)
.Ltmp38:
	movb	$10, %cl
	movq	%rbx, %rdx
	callq	*%rax
	nop
.Ltmp39:
	incq	%rax
	subq	%r14, %rsi
	movb	$0, -9(%rbp)
.Ltmp40:
	movq	-24(%rbp), %rcx
	movq	%rax, %rdx
	movq	%rsi, %r8
	callq	_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax
	nop
.Ltmp41:
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.LBB10_9:
	movb	$1, -9(%rbp)
.Ltmp42:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.48.llvm.16186315980599473920(%rip), %r9
	xorl	%ecx, %ecx
	movq	%rsi, %rdx
	movq	%rdi, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	nop
.Ltmp43:
.LBB10_10:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_@IMGREL
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_,unique,10
	.seh_endproc
	.def	"?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_@4HA":
.seh_proc "?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_@4HA"
.LBB10_11:
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
	leaq	64(%rdx), %rbp
	.seh_endprologue
	cmpb	$0, -9(%rbp)
	jne	.LBB10_12
.LBB10_13:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.LBB10_12:
	movq	-24(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5error9ErrorCodeEBF_
	jmp	.LBB10_13
.Lfunc_end10:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_,unique,10
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_,unique,4
	.p2align	2, 0x0
$cppxdata$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_@IMGREL
	.long	56
	.long	0
	.long	1
$stateUnwindMap$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_:
	.long	-1
	.long	"?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_@4HA"@IMGREL
$ip2state$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_:
	.long	.Lfunc_begin10@IMGREL
	.long	-1
	.long	.Ltmp34@IMGREL
	.long	0
	.long	.Ltmp43@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_,unique,10

	.def	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECsavOST1yGCNT_10serde_json;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECsavOST1yGCNT_10serde_json,unique,11
	.p2align	4
_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECsavOST1yGCNT_10serde_json:
.Lfunc_begin11:
.seh_proc _RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECsavOST1yGCNT_10serde_json
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	addq	%r8, %rdx
	jb	.LBB11_1
	movq	%rcx, %rsi
	movq	(%rcx), %rax
	leaq	(%rax,%rax), %rcx
	cmpq	%rcx, %rdx
	cmovaq	%rdx, %rcx
	cmpq	$9, %rcx
	movl	$8, %edi
	cmovaeq	%rcx, %rdi
	movq	8(%rsi), %r8
	movq	$1, 40(%rsp)
	movq	$1, 32(%rsp)
	leaq	48(%rsp), %rcx
	movq	%rax, %rdx
	movq	%rdi, %r9
	callq	_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCsavOST1yGCNT_10serde_json
	cmpl	$1, 48(%rsp)
	je	.LBB11_3
	movq	56(%rsp), %rax
	movq	%rax, 8(%rsi)
	movq	%rdi, (%rsi)
	.seh_startepilogue
	addq	$72, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB11_1:
	xorl	%ecx, %ecx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.LBB11_3:
	movq	56(%rsp), %rcx
	movq	64(%rsp), %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.Lfunc_end11:
	.seh_endproc

	.def	_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_,unique,12
	.p2align	4
_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_:
.Lfunc_begin12:
.seh_proc _RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_
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
	movq	%rdx, %rsi
	movzbl	(%rcx), %eax
	leaq	.LJTI12_0(%rip), %rdx
	movslq	(%rdx,%rax,4), %rax
	addq	%rdx, %rax
	movq	%rsi, -8(%rbp)
	jmpq	*%rax
.LBB12_1:
	movq	(%rsi), %rax
	movq	(%rax), %r14
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.33(%rip), %rdx
	movl	$4, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_211
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdi
	leaq	.LJTI12_16(%rip), %r15
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.33(%rip), %rbx
	xorl	%esi, %esi
	movl	$255, %r12d
	jmp	.LBB12_5
	.p2align	4
.LBB12_3:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB12_180
.LBB12_4:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movl	$4, %r8d
	movq	%rbx, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_212
.LBB12_5:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rdi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB12_6:
	cmpb	$35, 16(%rax)
	je	.LBB12_4
	jmp	.LBB12_180
	.p2align	4
.LBB12_7:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB12_4
	jmp	.LBB12_180
	.p2align	4
.LBB12_8:
	cmpb	$35, 31(%rax)
	jne	.LBB12_180
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_4
.LBB12_10:
	movq	16(%rcx), %rdi
	movq	24(%rcx), %rax
	movq	%rax, -16(%rbp)
	movq	(%rsi), %rax
	movq	%rax, -24(%rbp)
	movq	(%rax), %r15
	movq	(%r15), %rcx
	movq	8(%r15), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.25(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_44
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rbx
	leaq	.LJTI12_6(%rip), %r13
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.25(%rip), %r14
	movl	$255, %esi
	jmp	.LBB12_14
	.p2align	4
.LBB12_12:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r12
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r12, %rax
	testb	%cl, %cl
	je	.LBB12_180
.LBB12_13:
	movq	(%r15), %rcx
	movq	8(%r15), %rax
	movl	$1, %r8d
	movq	%r14, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_44
.LBB12_14:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rbx, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r13,%rcx,4), %rcx
	addq	%r13, %rcx
	jmpq	*%rcx
.LBB12_15:
	cmpb	$35, 16(%rax)
	je	.LBB12_13
	jmp	.LBB12_180
	.p2align	4
.LBB12_16:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%esi, %ecx
	cmpb	$35, %cl
	je	.LBB12_13
	jmp	.LBB12_180
	.p2align	4
.LBB12_17:
	cmpb	$35, 31(%rax)
	jne	.LBB12_180
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_13
.LBB12_19:
	movq	(%rsi), %rbx
	movq	8(%rcx), %rax
	cmpq	$2, %rax
	je	.LBB12_89
	cmpl	$1, %eax
	jne	.LBB12_99
	movq	16(%rcx), %rsi
	movq	%rsi, %rcx
	negq	%rcx
	cmovsq	%rsi, %rcx
	leaq	-80(%rbp), %rdx
	callq	_RNvXsu_Cs1KvuFdKMjOj_4itoayNtB5_8Unsigned3fmt
	testq	%rsi, %rsi
	js	.LBB12_195
	cmpq	$20, %rax
	je	.LBB12_211
	movl	$20, %esi
	movq	%rax, %rcx
	jmp	.LBB12_197
.LBB12_24:
	movq	16(%rcx), %rdx
	movq	24(%rcx), %r8
	movq	(%rsi), %rcx
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
	jmp	_RNvXs1_NtCsavOST1yGCNT_10serde_json3serQINtB5_10SerializerQNtNvXs_NtB7_5valueNtB12_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterENtNtCslmkRZor3pUd_10serde_core3ser10Serializer13serialize_strB7_
.LBB12_25:
	movq	(%rsi), %rax
	movq	(%rax), %r14
	cmpb	$0, 1(%rcx)
	je	.LBB12_77
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.32(%rip), %rdx
	movl	$4, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_211
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdi
	leaq	.LJTI12_15(%rip), %r15
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.32(%rip), %rbx
	xorl	%esi, %esi
	movl	$255, %r12d
	jmp	.LBB12_30
	.p2align	4
.LBB12_28:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB12_180
.LBB12_29:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movl	$4, %r8d
	movq	%rbx, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_212
.LBB12_30:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rdi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB12_31:
	cmpb	$35, 16(%rax)
	je	.LBB12_29
	jmp	.LBB12_180
	.p2align	4
.LBB12_32:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB12_29
	jmp	.LBB12_180
	.p2align	4
.LBB12_33:
	cmpb	$35, 31(%rax)
	jne	.LBB12_180
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_29
.LBB12_35:
	movq	%rcx, -24(%rbp)
	movq	24(%rcx), %rax
	movq	%rax, -16(%rbp)
	movq	(%rsi), %r14
	movq	(%r14), %r15
	movq	(%r15), %rcx
	movq	8(%r15), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.26(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_54
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdi
	leaq	.LJTI12_1(%rip), %r12
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.26(%rip), %rbx
	movl	$255, %r13d
	jmp	.LBB12_39
	.p2align	4
.LBB12_37:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %rsi
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%rsi, %rax
	movq	-8(%rbp), %rsi
	testb	%cl, %cl
	je	.LBB12_180
.LBB12_38:
	movq	(%r15), %rcx
	movq	8(%r15), %rax
	movl	$1, %r8d
	movq	%rbx, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_54
.LBB12_39:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rdi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r12,%rcx,4), %rcx
	addq	%r12, %rcx
	jmpq	*%rcx
.LBB12_40:
	cmpb	$35, 16(%rax)
	je	.LBB12_38
	jmp	.LBB12_180
	.p2align	4
.LBB12_41:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r13d, %ecx
	cmpb	$35, %cl
	je	.LBB12_38
	jmp	.LBB12_180
	.p2align	4
.LBB12_42:
	cmpb	$35, 31(%rax)
	jne	.LBB12_180
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_38
.LBB12_44:
	cmpq	$0, -16(%rbp)
	setne	%r15b
	jne	.LBB12_64
	movq	-24(%rbp), %rax
	movq	(%rax), %r12
	movq	(%r12), %rcx
	movq	8(%r12), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.29(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_64
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rbx
	leaq	.LJTI12_7(%rip), %r13
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.29(%rip), %r14
	jmp	.LBB12_49
	.p2align	4
.LBB12_47:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %rsi
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%rsi, %rax
	testb	%cl, %cl
	je	.LBB12_180
.LBB12_48:
	movq	(%r12), %rcx
	movq	8(%r12), %rax
	movl	$1, %r8d
	movq	%r14, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_64
.LBB12_49:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rbx, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r13,%rcx,4), %rcx
	addq	%r13, %rcx
	jmpq	*%rcx
.LBB12_50:
	cmpb	$35, 16(%rax)
	je	.LBB12_48
	jmp	.LBB12_180
	.p2align	4
.LBB12_51:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	movl	$255, %edx
	cmovael	%edx, %ecx
	cmpb	$35, %cl
	je	.LBB12_48
	jmp	.LBB12_180
	.p2align	4
.LBB12_52:
	cmpb	$35, 31(%rax)
	jne	.LBB12_180
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_48
.LBB12_54:
	movb	$1, %cl
	movq	-16(%rbp), %rdi
	testq	%rdi, %rdi
	jne	.LBB12_123
	movq	(%r14), %r14
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.24(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_121
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdi
	leaq	.LJTI12_2(%rip), %r15
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.24(%rip), %rbx
	movl	$255, %r12d
	jmp	.LBB12_59
	.p2align	4
.LBB12_57:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %rsi
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%rsi, %rax
	movq	-8(%rbp), %rsi
	testb	%cl, %cl
	je	.LBB12_180
.LBB12_58:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movl	$1, %r8d
	movq	%rbx, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_122
.LBB12_59:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rdi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB12_60:
	cmpb	$35, 16(%rax)
	je	.LBB12_58
	jmp	.LBB12_180
	.p2align	4
.LBB12_61:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB12_58
	jmp	.LBB12_180
	.p2align	4
.LBB12_62:
	cmpb	$35, 31(%rax)
	jne	.LBB12_180
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_58
.LBB12_64:
	movq	-16(%rbp), %rax
	movq	%rax, %r12
	shlq	$5, %r12
	addq	%rdi, %r12
	testq	%rax, %rax
	sete	%cl
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.34(%rip), %rbx
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %r14
	leaq	.LJTI12_8(%rip), %rsi
	jmp	.LBB12_66
	.p2align	4
.LBB12_65:
	leaq	32(%rdi), %r13
	movq	%rdi, %rcx
	movq	-8(%rbp), %rdx
	callq	_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_
	xorl	%r15d, %r15d
	movl	$0, %ecx
	movq	%r13, %rdi
	testq	%rax, %rax
	jne	.LBB12_88
.LBB12_66:
	cmpq	%r12, %rdi
	je	.LBB12_86
	testb	$1, %r15b
	jne	.LBB12_65
	movq	-8(%rbp), %rax
	movq	(%rax), %rax
	movq	(%rax), %r15
	jmp	.LBB12_70
	.p2align	4
.LBB12_69:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB12_180
.LBB12_70:
	movq	(%r15), %rcx
	movq	8(%r15), %rax
	movl	$1, %r8d
	movq	%rbx, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_65
	movl	$9, %r8d
	movb	$41, %cl
	movq	%r14, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%rsi,%rcx,4), %rcx
	addq	%rsi, %rcx
	jmpq	*%rcx
.LBB12_72:
	cmpb	$35, 16(%rax)
	je	.LBB12_70
	jmp	.LBB12_180
	.p2align	4
.LBB12_73:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	movl	$255, %edx
	cmovael	%edx, %ecx
	cmpb	$35, %cl
	je	.LBB12_70
	jmp	.LBB12_180
	.p2align	4
.LBB12_74:
	cmpb	$35, 31(%rax)
	jne	.LBB12_180
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_70
.LBB12_77:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.31(%rip), %rdx
	movl	$5, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_211
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdi
	leaq	.LJTI12_14(%rip), %r15
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.31(%rip), %rbx
	xorl	%esi, %esi
	movl	$255, %r12d
	jmp	.LBB12_81
	.p2align	4
.LBB12_79:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB12_180
.LBB12_80:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movl	$5, %r8d
	movq	%rbx, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_212
.LBB12_81:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rdi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB12_82:
	cmpb	$35, 16(%rax)
	je	.LBB12_80
	jmp	.LBB12_180
	.p2align	4
.LBB12_83:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB12_80
	jmp	.LBB12_180
	.p2align	4
.LBB12_84:
	cmpb	$35, 31(%rax)
	jne	.LBB12_180
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_80
.LBB12_86:
	testb	$1, %cl
	jne	.LBB12_211
	movq	-8(%rbp), %rax
	movq	(%rax), %rax
	movq	(%rax), %r14
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.29(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_211
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdi
	leaq	.LJTI12_9(%rip), %r15
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.29(%rip), %rbx
	xorl	%esi, %esi
	movl	$255, %r12d
	jmp	.LBB12_116
.LBB12_114:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB12_180
.LBB12_115:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movl	$1, %r8d
	movq	%rbx, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_212
.LBB12_116:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rdi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB12_117:
	cmpb	$35, 16(%rax)
	je	.LBB12_115
	jmp	.LBB12_180
.LBB12_118:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB12_115
	jmp	.LBB12_180
.LBB12_119:
	cmpb	$35, 31(%rax)
	jne	.LBB12_180
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_115
.LBB12_89:
	movq	16(%rcx), %xmm0
	movq	%xmm0, %rax
	movabsq	$9223372036854775807, %rcx
	andq	%rax, %rcx
	movabsq	$9218868437227405312, %rax
	cmpq	%rax, %rcx
	jl	.LBB12_184
	movq	(%rbx), %r14
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.33(%rip), %rdx
	movl	$4, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_211
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdi
	leaq	.LJTI12_11(%rip), %r15
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.33(%rip), %rbx
	xorl	%esi, %esi
	movl	$255, %r12d
	jmp	.LBB12_94
.LBB12_92:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB12_180
.LBB12_93:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movl	$4, %r8d
	movq	%rbx, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_212
.LBB12_94:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rdi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB12_95:
	cmpb	$35, 16(%rax)
	je	.LBB12_93
	jmp	.LBB12_180
.LBB12_96:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB12_93
	jmp	.LBB12_180
.LBB12_97:
	cmpb	$35, 31(%rax)
	jne	.LBB12_180
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_93
.LBB12_99:
	movq	16(%rcx), %rcx
	leaq	-80(%rbp), %rdx
	callq	_RNvXsu_Cs1KvuFdKMjOj_4itoayNtB5_8Unsigned3fmt
	movq	%rax, %rsi
	subq	$20, %rsi
	je	.LBB12_211
	negq	%rsi
	leaq	(%rax,%rbp), %rdi
	addq	$-80, %rdi
	movq	(%rbx), %r14
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movq	%rdi, %rdx
	movq	%rsi, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_211
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rbx
	leaq	.LJTI12_13(%rip), %r15
	movl	$255, %r12d
	jmp	.LBB12_104
.LBB12_102:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB12_213
.LBB12_103:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movq	%rdi, %rdx
	movq	%rsi, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_211
.LBB12_104:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rbx, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB12_105:
	cmpb	$35, 16(%rax)
	je	.LBB12_103
	jmp	.LBB12_213
.LBB12_106:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB12_103
	jmp	.LBB12_213
.LBB12_107:
	cmpb	$35, 31(%rax)
	jne	.LBB12_213
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_103
.LBB12_121:
	xorl	%ecx, %ecx
	jmp	.LBB12_123
.LBB12_122:
	xorl	%ecx, %ecx
	movq	-16(%rbp), %rdi
.LBB12_123:
	movq	-24(%rbp), %rax
	movq	8(%rax), %rdx
	movq	16(%rax), %r13
	testq	%rdx, %rdx
	cmoveq	%rdx, %rdi
	setne	%r8b
	xorl	%r15d, %r15d
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rbx
	leaq	.LJTI12_4(%rip), %r14
	jmp	.LBB12_125
	.p2align	4
.LBB12_124:
	shlq	$5, %r13
	addq	%r13, %r12
	movq	%r12, %rcx
	movq	-8(%rbp), %rsi
	movq	%rsi, %rdx
	callq	_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_
	movb	$2, %cl
	movb	$1, %r8b
	movl	$0, %edx
	testq	%rax, %rax
	movq	-16(%rbp), %rdi
	movq	-32(%rbp), %r13
	jne	.LBB12_88
.LBB12_125:
	subq	$1, %rdi
	jb	.LBB12_170
	testb	$1, %r8b
	je	.LBB12_216
	testq	%r15, %r15
	je	.LBB12_130
	movq	%rdi, -16(%rbp)
	movzwl	626(%r15), %eax
	cmpq	%rax, %r13
	jae	.LBB12_139
.LBB12_129:
	movq	%r15, %r12
	jmp	.LBB12_141
	.p2align	4
.LBB12_130:
	testq	%r13, %r13
	je	.LBB12_135
	movq	%r13, %rax
	movq	%rdx, %r15
	andq	$7, %rax
	je	.LBB12_136
	xorl	%edx, %edx
	.p2align	4
.LBB12_133:
	movq	632(%r15), %r15
	incq	%rdx
	cmpq	%rdx, %rax
	jne	.LBB12_133
	movq	%r13, %rax
	subq	%rdx, %rax
	cmpq	$8, %r13
	jae	.LBB12_137
	jmp	.LBB12_138
.LBB12_135:
	movq	%rdx, %r15
	jmp	.LBB12_138
.LBB12_136:
	movq	%r13, %rax
	cmpq	$8, %r13
	jb	.LBB12_138
	.p2align	4
.LBB12_137:
	movq	632(%r15), %rdx
	movq	632(%rdx), %rdx
	movq	632(%rdx), %rdx
	movq	632(%rdx), %rdx
	movq	632(%rdx), %rdx
	movq	632(%rdx), %rdx
	movq	632(%rdx), %rdx
	movq	632(%rdx), %r15
	addq	$-8, %rax
	jne	.LBB12_137
.LBB12_138:
	xorl	%r13d, %r13d
	xorl	%edx, %edx
	movq	%rdi, -16(%rbp)
	movzwl	626(%r15), %eax
	cmpq	%rax, %r13
	jb	.LBB12_129
	.p2align	4
.LBB12_139:
	movq	352(%r15), %r12
	testq	%r12, %r12
	je	.LBB12_214
	incq	%rdx
	movzwl	624(%r15), %r13d
	movq	%r12, %r15
	cmpw	626(%r12), %r13w
	jae	.LBB12_139
.LBB12_141:
	testq	%rdx, %rdx
	je	.LBB12_146
	leaq	(%r12,%r13,8), %rax
	addq	$640, %rax
	movq	%rdx, %r8
	andq	$7, %r8
	je	.LBB12_147
	xorl	%r9d, %r9d
	.p2align	4
.LBB12_144:
	movq	(%rax), %r15
	leaq	632(%r15), %rax
	incq	%r9
	cmpq	%r9, %r8
	jne	.LBB12_144
	movq	%rdx, %r8
	subq	%r9, %r8
	cmpq	$8, %rdx
	jb	.LBB12_150
	.p2align	4
.LBB12_149:
	movq	(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %r15
	leaq	632(%r15), %rax
	addq	$-8, %r8
	jne	.LBB12_149
.LBB12_150:
	movq	$0, -32(%rbp)
	jmp	.LBB12_151
	.p2align	4
.LBB12_146:
	leaq	1(%r13), %rax
	movq	%rax, -32(%rbp)
	movq	%r12, %r15
.LBB12_151:
	leaq	(,%r13,2), %rax
	addq	%r13, %rax
	movq	368(%r12,%rax,8), %rdx
	movq	%rdx, -24(%rbp)
	movq	376(%r12,%rax,8), %rax
	movq	%rax, -40(%rbp)
	cmpb	$1, %cl
	jne	.LBB12_162
.LBB12_152:
	movq	-8(%rbp), %rsi
	movq	(%rsi), %rcx
	movq	-24(%rbp), %rdx
	movq	-40(%rbp), %r8
	callq	_RNvXs1_NtCsavOST1yGCNT_10serde_json3serQINtB5_10SerializerQNtNvXs_NtB7_5valueNtB12_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterENtNtCslmkRZor3pUd_10serde_core3ser10Serializer13serialize_strB7_
	testq	%rax, %rax
	jne	.LBB12_88
	movq	(%rsi), %rax
	movq	(%rax), %rsi
	movq	(%rsi), %rcx
	movq	8(%rsi), %rax
	movl	$1, %r8d
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.35(%rip), %rdi
	jmp	.LBB12_156
	.p2align	4
.LBB12_154:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %rdi
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%rdi, %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.35(%rip), %rdi
	testb	%cl, %cl
	je	.LBB12_180
.LBB12_155:
	movq	(%rsi), %rcx
	movq	8(%rsi), %rax
	movl	$1, %r8d
.LBB12_156:
	movq	%rdi, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_124
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rbx, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r14,%rcx,4), %rcx
	addq	%r14, %rcx
	jmpq	*%rcx
.LBB12_158:
	cmpb	$35, 16(%rax)
	je	.LBB12_155
	jmp	.LBB12_180
	.p2align	4
.LBB12_159:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	movl	$255, %edx
	cmovael	%edx, %ecx
	cmpb	$35, %cl
	je	.LBB12_155
	jmp	.LBB12_180
	.p2align	4
.LBB12_160:
	cmpb	$35, 31(%rax)
	jne	.LBB12_180
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_155
	.p2align	4
.LBB12_162:
	movq	-8(%rbp), %rax
	movq	(%rax), %rax
	movq	(%rax), %rdi
	jmp	.LBB12_164
	.p2align	4
.LBB12_163:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rax
	movq	%rsi, %rcx
	shrq	$32, %rcx
	callq	*16(%rax)
	testb	%al, %al
	je	.LBB12_207
.LBB12_164:
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	movl	$1, %r8d
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.34(%rip), %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_152
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rbx, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movq	%rax, %rsi
	andl	$3, %eax
	leaq	.LJTI12_3(%rip), %rcx
	movslq	(%rcx,%rax,4), %rax
	addq	%rcx, %rax
	jmpq	*%rax
.LBB12_166:
	cmpb	$35, 16(%rsi)
	je	.LBB12_164
	jmp	.LBB12_207
	.p2align	4
.LBB12_167:
	movq	%rsi, %rax
	shrq	$32, %rax
	cmpq	$43, %rax
	movl	$255, %ecx
	cmovael	%ecx, %eax
	cmpb	$35, %al
	je	.LBB12_164
	jmp	.LBB12_207
	.p2align	4
.LBB12_168:
	cmpb	$35, 31(%rsi)
	jne	.LBB12_207
	movq	%rsi, %rcx
	decq	%rcx
	callq	*23(%rsi)
	jmp	.LBB12_164
	.p2align	4
.LBB12_147:
	movq	%rdx, %r8
	cmpq	$8, %rdx
	jb	.LBB12_150
	jmp	.LBB12_149
.LBB12_88:
	movq	%rax, %rsi
	jmp	.LBB12_212
.LBB12_170:
	testb	%cl, %cl
	je	.LBB12_211
	movq	(%rsi), %rax
	movq	(%rax), %r14
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.24(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_211
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdi
	leaq	.LJTI12_5(%rip), %r15
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.24(%rip), %rbx
	xorl	%esi, %esi
	movl	$255, %r12d
	jmp	.LBB12_175
.LBB12_173:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB12_180
.LBB12_174:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movl	$1, %r8d
	movq	%rbx, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_212
.LBB12_175:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rdi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB12_176:
	cmpb	$35, 16(%rax)
	je	.LBB12_174
	jmp	.LBB12_180
.LBB12_177:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB12_174
	jmp	.LBB12_180
.LBB12_178:
	cmpb	$35, 31(%rax)
	jne	.LBB12_180
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_174
.LBB12_180:
	movq	%rax, %rcx
.LBB12_181:
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
	jmp	_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io
.LBB12_184:
	leaq	-80(%rbp), %rdi
	movq	%rdi, %rdx
	callq	_RNvXs_NtCs6FhewopUhnE_4zmij7privatedNtB4_6Sealed20write_to_zmij_buffer
	movq	%rax, %rsi
	subq	%rdi, %rsi
	je	.LBB12_211
	movq	(%rbx), %r14
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	-80(%rbp), %rdx
	movq	%rsi, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_211
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdi
	leaq	.LJTI12_10(%rip), %r15
	leaq	-80(%rbp), %rbx
	movl	$255, %r12d
	jmp	.LBB12_189
.LBB12_187:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB12_213
.LBB12_188:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movq	%rbx, %rdx
	movq	%rsi, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_211
.LBB12_189:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rdi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB12_190:
	cmpb	$35, 16(%rax)
	je	.LBB12_188
	jmp	.LBB12_213
.LBB12_191:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB12_188
	jmp	.LBB12_213
.LBB12_192:
	cmpb	$35, 31(%rax)
	jne	.LBB12_213
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_188
.LBB12_195:
	leaq	-1(%rax), %rcx
	cmpq	$19, %rcx
	ja	.LBB12_217
	movb	$45, -80(%rbp,%rcx)
	movl	$21, %esi
.LBB12_197:
	subq	%rax, %rsi
	leaq	(%rcx,%rbp), %rdi
	addq	$-80, %rdi
	movq	(%rbx), %r14
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movq	%rdi, %rdx
	movq	%rsi, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_211
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rbx
	leaq	.LJTI12_12(%rip), %r15
	movl	$255, %r12d
	jmp	.LBB12_201
.LBB12_199:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB12_213
.LBB12_200:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movq	%rdi, %rdx
	movq	%rsi, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_211
.LBB12_201:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rbx, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB12_202:
	cmpb	$35, 16(%rax)
	je	.LBB12_200
	jmp	.LBB12_213
.LBB12_203:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB12_200
	jmp	.LBB12_213
.LBB12_204:
	cmpb	$35, 31(%rax)
	jne	.LBB12_213
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_200
.LBB12_211:
	xorl	%esi, %esi
.LBB12_212:
	movq	%rsi, %rax
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
.LBB12_207:
	movq	%rsi, %rcx
	jmp	.LBB12_181
.LBB12_213:
	movq	%rax, %rcx
	callq	_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io
	movq	%rax, %rsi
	jmp	.LBB12_212
.LBB12_214:
.Ltmp44:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.43(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	nop
.Ltmp45:
	ud2
.LBB12_216:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.130(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB12_217:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.129(%rip), %r8
	movl	$20, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_@IMGREL
	.section	.text,"xr",one_only,_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_,unique,12
	.seh_endproc
	.def	"?dtor$218@?0?_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$218@?0?_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_@4HA":
.seh_proc "?dtor$218@?0?_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_@4HA"
.LBB12_218:
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
	ud2
.Lfunc_end12:
	.section	.rdata,"dr",associative,_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_,unique,13
	.p2align	2, 0x0
.LJTI12_0:
	.long	.LBB12_1-.LJTI12_0
	.long	.LBB12_25-.LJTI12_0
	.long	.LBB12_19-.LJTI12_0
	.long	.LBB12_24-.LJTI12_0
	.long	.LBB12_10-.LJTI12_0
	.long	.LBB12_35-.LJTI12_0
.LJTI12_1:
	.long	.LBB12_40-.LJTI12_1
	.long	.LBB12_42-.LJTI12_1
	.long	.LBB12_37-.LJTI12_1
	.long	.LBB12_41-.LJTI12_1
.LJTI12_2:
	.long	.LBB12_60-.LJTI12_2
	.long	.LBB12_62-.LJTI12_2
	.long	.LBB12_57-.LJTI12_2
	.long	.LBB12_61-.LJTI12_2
.LJTI12_3:
	.long	.LBB12_166-.LJTI12_3
	.long	.LBB12_168-.LJTI12_3
	.long	.LBB12_163-.LJTI12_3
	.long	.LBB12_167-.LJTI12_3
.LJTI12_4:
	.long	.LBB12_158-.LJTI12_4
	.long	.LBB12_160-.LJTI12_4
	.long	.LBB12_154-.LJTI12_4
	.long	.LBB12_159-.LJTI12_4
.LJTI12_5:
	.long	.LBB12_176-.LJTI12_5
	.long	.LBB12_178-.LJTI12_5
	.long	.LBB12_173-.LJTI12_5
	.long	.LBB12_177-.LJTI12_5
.LJTI12_6:
	.long	.LBB12_15-.LJTI12_6
	.long	.LBB12_17-.LJTI12_6
	.long	.LBB12_12-.LJTI12_6
	.long	.LBB12_16-.LJTI12_6
.LJTI12_7:
	.long	.LBB12_50-.LJTI12_7
	.long	.LBB12_52-.LJTI12_7
	.long	.LBB12_47-.LJTI12_7
	.long	.LBB12_51-.LJTI12_7
.LJTI12_8:
	.long	.LBB12_72-.LJTI12_8
	.long	.LBB12_74-.LJTI12_8
	.long	.LBB12_69-.LJTI12_8
	.long	.LBB12_73-.LJTI12_8
.LJTI12_9:
	.long	.LBB12_117-.LJTI12_9
	.long	.LBB12_119-.LJTI12_9
	.long	.LBB12_114-.LJTI12_9
	.long	.LBB12_118-.LJTI12_9
.LJTI12_10:
	.long	.LBB12_190-.LJTI12_10
	.long	.LBB12_192-.LJTI12_10
	.long	.LBB12_187-.LJTI12_10
	.long	.LBB12_191-.LJTI12_10
.LJTI12_11:
	.long	.LBB12_95-.LJTI12_11
	.long	.LBB12_97-.LJTI12_11
	.long	.LBB12_92-.LJTI12_11
	.long	.LBB12_96-.LJTI12_11
.LJTI12_12:
	.long	.LBB12_202-.LJTI12_12
	.long	.LBB12_204-.LJTI12_12
	.long	.LBB12_199-.LJTI12_12
	.long	.LBB12_203-.LJTI12_12
.LJTI12_13:
	.long	.LBB12_105-.LJTI12_13
	.long	.LBB12_107-.LJTI12_13
	.long	.LBB12_102-.LJTI12_13
	.long	.LBB12_106-.LJTI12_13
.LJTI12_14:
	.long	.LBB12_82-.LJTI12_14
	.long	.LBB12_84-.LJTI12_14
	.long	.LBB12_79-.LJTI12_14
	.long	.LBB12_83-.LJTI12_14
.LJTI12_15:
	.long	.LBB12_31-.LJTI12_15
	.long	.LBB12_33-.LJTI12_15
	.long	.LBB12_28-.LJTI12_15
	.long	.LBB12_32-.LJTI12_15
.LJTI12_16:
	.long	.LBB12_6-.LJTI12_16
	.long	.LBB12_8-.LJTI12_16
	.long	.LBB12_3-.LJTI12_16
	.long	.LBB12_7-.LJTI12_16
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_,unique,12
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_,unique,5
	.p2align	2, 0x0
$cppxdata$_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_@IMGREL
	.long	112
	.long	0
	.long	1
$stateUnwindMap$_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_:
	.long	-1
	.long	"?dtor$218@?0?_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_@4HA"@IMGREL
$ip2state$_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_:
	.long	.Lfunc_begin12@IMGREL
	.long	-1
	.long	.Ltmp44@IMGREL
	.long	0
	.long	.Ltmp45@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_,unique,12

	.def	_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_,unique,14
	.p2align	4
_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_:
.Lfunc_begin13:
.seh_proc _RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_
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
	subq	$152, %rsp
	.seh_stackalloc 152
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	movq	$-2, 16(%rbp)
	movq	%rdx, %r9
	movzbl	(%rcx), %eax
	leaq	.LJTI13_0(%rip), %rdx
	movslq	(%rdx,%rax,4), %rax
	addq	%rdx, %rax
	jmpq	*%rax
.LBB13_1:
	movq	(%r9), %rax
	movq	(%rax), %r14
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.33(%rip), %rdx
	movl	$4, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB13_177
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rsi
	leaq	.LJTI13_16(%rip), %r15
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.33(%rip), %rdi
	xorl	%ebx, %ebx
	movl	$255, %r12d
	jmp	.LBB13_5
	.p2align	4
.LBB13_3:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB13_179
.LBB13_4:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movl	$4, %r8d
	movq	%rdi, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB13_178
.LBB13_5:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rsi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB13_6:
	cmpb	$35, 16(%rax)
	je	.LBB13_4
	jmp	.LBB13_179
	.p2align	4
.LBB13_7:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB13_4
	jmp	.LBB13_179
	.p2align	4
.LBB13_8:
	cmpb	$35, 31(%rax)
	jne	.LBB13_179
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB13_4
.LBB13_10:
	movq	16(%rcx), %rax
	movq	%rax, (%rbp)
	movq	24(%rcx), %rax
	movq	%rax, -8(%rbp)
	movq	(%r9), %rbx
	incq	24(%r9)
	movq	%r9, 8(%rbp)
	movb	$0, 32(%r9)
	movq	(%rbx), %rsi
	movq	(%rsi), %rcx
	movq	8(%rsi), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.25(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB13_44
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %r14
	leaq	.LJTI13_6(%rip), %rdi
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.25(%rip), %r15
	movl	$255, %r12d
	jmp	.LBB13_14
	.p2align	4
.LBB13_12:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB13_179
.LBB13_13:
	movq	(%rsi), %rcx
	movq	8(%rsi), %rax
	movl	$1, %r8d
	movq	%r15, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB13_44
.LBB13_14:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%r14, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%rdi,%rcx,4), %rcx
	addq	%rdi, %rcx
	jmpq	*%rcx
.LBB13_15:
	cmpb	$35, 16(%rax)
	je	.LBB13_13
	jmp	.LBB13_179
	.p2align	4
.LBB13_16:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB13_13
	jmp	.LBB13_179
	.p2align	4
.LBB13_17:
	cmpb	$35, 31(%rax)
	jne	.LBB13_179
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB13_13
.LBB13_19:
	movq	(%r9), %rbx
	movq	8(%rcx), %rax
	cmpq	$2, %rax
	je	.LBB13_153
	cmpl	$1, %eax
	jne	.LBB13_163
	movq	16(%rcx), %rsi
	movq	%rsi, %rcx
	negq	%rcx
	cmovsq	%rsi, %rcx
	leaq	-96(%rbp), %rdx
	callq	_RNvXsu_Cs1KvuFdKMjOj_4itoayNtB5_8Unsigned3fmt
	testq	%rsi, %rsi
	js	.LBB13_191
	cmpq	$20, %rax
	je	.LBB13_177
	movl	$20, %esi
	movq	%rax, %rcx
	jmp	.LBB13_193
.LBB13_24:
	movq	16(%rcx), %rdx
	movq	24(%rcx), %r8
	movq	(%r9), %rcx
	.seh_startepilogue
	addq	$152, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r13
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	jmp	_RNvXs1_NtCsavOST1yGCNT_10serde_json3serQINtB5_10SerializerQNtNvXs_NtB7_5valueNtB12_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterENtNtCslmkRZor3pUd_10serde_core3ser10Serializer13serialize_strB7_
.LBB13_25:
	movq	(%r9), %rax
	movq	(%rax), %r14
	cmpb	$0, 1(%rcx)
	je	.LBB13_141
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.32(%rip), %rdx
	movl	$4, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB13_177
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rsi
	leaq	.LJTI13_15(%rip), %r15
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.32(%rip), %rdi
	xorl	%ebx, %ebx
	movl	$255, %r12d
	jmp	.LBB13_30
	.p2align	4
.LBB13_28:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB13_179
.LBB13_29:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movl	$4, %r8d
	movq	%rdi, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB13_178
.LBB13_30:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rsi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB13_31:
	cmpb	$35, 16(%rax)
	je	.LBB13_29
	jmp	.LBB13_179
	.p2align	4
.LBB13_32:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB13_29
	jmp	.LBB13_179
	.p2align	4
.LBB13_33:
	cmpb	$35, 31(%rax)
	jne	.LBB13_179
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB13_29
.LBB13_35:
	movq	%rcx, -16(%rbp)
	movq	24(%rcx), %rax
	movq	%rax, (%rbp)
	movq	(%r9), %rdi
	incq	24(%r9)
	movq	%r9, 8(%rbp)
	movb	$0, 32(%r9)
	movq	(%rdi), %r15
	movq	(%r15), %rcx
	movq	8(%r15), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.26(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB13_76
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rbx
	leaq	.LJTI13_1(%rip), %r12
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.26(%rip), %r14
	movl	$255, %r13d
	jmp	.LBB13_39
	.p2align	4
.LBB13_37:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %rsi
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%rsi, %rax
	testb	%cl, %cl
	je	.LBB13_179
.LBB13_38:
	movq	(%r15), %rcx
	movq	8(%r15), %rax
	movl	$1, %r8d
	movq	%r14, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB13_76
.LBB13_39:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rbx, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r12,%rcx,4), %rcx
	addq	%r12, %rcx
	jmpq	*%rcx
.LBB13_40:
	cmpb	$35, 16(%rax)
	je	.LBB13_38
	jmp	.LBB13_179
	.p2align	4
.LBB13_41:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r13d, %ecx
	cmpb	$35, %cl
	je	.LBB13_38
	jmp	.LBB13_179
	.p2align	4
.LBB13_42:
	cmpb	$35, 31(%rax)
	jne	.LBB13_179
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB13_38
.LBB13_44:
	movq	8(%rbp), %rsi
	leaq	8(%rsi), %rcx
	movq	-8(%rbp), %rdx
	testq	%rdx, %rdx
	je	.LBB13_150
	movq	%rcx, -32(%rbp)
	shlq	$5, %rdx
	movq	(%rbp), %rdi
	addq	%rdi, %rdx
	movb	$1, %al
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %r12
	leaq	.LJTI13_9(%rip), %r13
	movq	%rdx, -8(%rbp)
.LBB13_46:
	movq	%rdi, (%rbp)
	movq	(%rsi), %rcx
	movq	%rcx, -16(%rbp)
	movq	(%rcx), %rbx
	testb	$1, %al
	jne	.LBB13_48
	jmp	.LBB13_55
	.p2align	4
.LBB13_47:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %rsi
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%rsi, %rax
	testb	%cl, %cl
	je	.LBB13_179
.LBB13_48:
	movq	(%rbx), %rcx
	movq	8(%rbx), %rax
	movl	$1, %r8d
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.23(%rip), %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB13_61
	movl	$9, %r8d
	movb	$41, %cl
	movq	%r12, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	leaq	.LJTI13_8(%rip), %rdx
	movslq	(%rdx,%rcx,4), %rcx
	addq	%rdx, %rcx
	jmpq	*%rcx
.LBB13_50:
	cmpb	$35, 16(%rax)
	je	.LBB13_48
	jmp	.LBB13_179
	.p2align	4
.LBB13_51:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	movl	$255, %edx
	cmovael	%edx, %ecx
	cmpb	$35, %cl
	je	.LBB13_48
	jmp	.LBB13_179
	.p2align	4
.LBB13_52:
	cmpb	$35, 31(%rax)
	jne	.LBB13_179
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB13_48
	.p2align	4
.LBB13_54:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %rsi
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%rsi, %rax
	testb	%cl, %cl
	je	.LBB13_179
.LBB13_55:
	movq	(%rbx), %rcx
	movq	8(%rbx), %rax
	movl	$2, %r8d
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.27(%rip), %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB13_61
	movl	$9, %r8d
	movb	$41, %cl
	movq	%r12, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	leaq	.LJTI13_7(%rip), %rdx
	movslq	(%rdx,%rcx,4), %rcx
	addq	%rdx, %rcx
	jmpq	*%rcx
.LBB13_57:
	cmpb	$35, 16(%rax)
	je	.LBB13_55
	jmp	.LBB13_179
	.p2align	4
.LBB13_58:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	movl	$255, %edx
	cmovael	%edx, %ecx
	cmpb	$35, %cl
	je	.LBB13_55
	jmp	.LBB13_179
	.p2align	4
.LBB13_59:
	cmpb	$35, 31(%rax)
	jne	.LBB13_179
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB13_55
	.p2align	4
.LBB13_61:
	movq	8(%rbp), %rax
	movq	24(%rax), %rax
	movq	%rax, -40(%rbp)
	testq	%rax, %rax
	je	.LBB13_73
	movq	8(%rbp), %rax
	movq	16(%rax), %rbx
	testq	%rbx, %rbx
	je	.LBB13_73
	movq	8(%rbp), %rax
	movq	8(%rax), %r14
	xorl	%esi, %esi
	jmp	.LBB13_65
	.p2align	4
.LBB13_64:
	incq	%rsi
	cmpq	-40(%rbp), %rsi
	je	.LBB13_73
.LBB13_65:
	movq	-16(%rbp), %rax
	movq	(%rax), %r15
	jmp	.LBB13_67
	.p2align	4
.LBB13_66:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %rdi
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%rdi, %rax
	testb	%cl, %cl
	je	.LBB13_179
.LBB13_67:
	movq	(%r15), %rcx
	movq	8(%r15), %rax
	movq	%r14, %rdx
	movq	%rbx, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB13_64
	movl	$9, %r8d
	movb	$41, %cl
	movq	%r12, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r13,%rcx,4), %rcx
	addq	%r13, %rcx
	jmpq	*%rcx
.LBB13_69:
	cmpb	$35, 16(%rax)
	je	.LBB13_67
	jmp	.LBB13_179
	.p2align	4
.LBB13_70:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	movl	$255, %edx
	cmovael	%edx, %ecx
	cmpb	$35, %cl
	je	.LBB13_67
	jmp	.LBB13_179
	.p2align	4
.LBB13_71:
	cmpb	$35, 31(%rax)
	jne	.LBB13_179
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB13_67
	.p2align	4
.LBB13_73:
	movq	(%rbp), %rdi
	movq	%rdi, %rcx
	movq	8(%rbp), %rsi
	movq	%rsi, %rdx
	callq	_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_
	testq	%rax, %rax
	jne	.LBB13_202
	addq	$32, %rdi
	movb	$1, 32(%rsi)
	xorl	%eax, %eax
	movq	-8(%rbp), %rdx
	cmpq	%rdx, %rdi
	jne	.LBB13_46
	movq	(%rsi), %rdx
	movq	-32(%rbp), %rcx
	jmp	.LBB13_151
.LBB13_76:
	movq	8(%rbp), %r10
	leaq	8(%r10), %rcx
	cmpq	$0, (%rbp)
	je	.LBB13_152
	movq	%rcx, -48(%rbp)
	movq	-16(%rbp), %rsi
	movq	8(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB13_174
	movq	16(%rsi), %r9
	movb	$1, %al
	xorl	%r13d, %r13d
.LBB13_79:
	testq	%r13, %r13
	je	.LBB13_82
	movzwl	626(%r13), %edx
	cmpq	%rdx, %r9
	jae	.LBB13_92
.LBB13_81:
	movq	%r13, %r15
	movq	%r9, %r11
	jmp	.LBB13_94
.LBB13_82:
	testq	%r9, %r9
	je	.LBB13_87
	movq	%r9, %rdx
	movq	%rcx, %r13
	andq	$7, %rdx
	je	.LBB13_88
	xorl	%r8d, %r8d
	.p2align	4
.LBB13_85:
	movq	632(%r13), %r13
	incq	%r8
	cmpq	%r8, %rdx
	jne	.LBB13_85
	movq	%r9, %rcx
	subq	%r8, %rcx
	jmp	.LBB13_89
.LBB13_87:
	movq	%rcx, %r13
	jmp	.LBB13_91
.LBB13_88:
	movq	%r9, %rcx
.LBB13_89:
	cmpq	$8, %r9
	jb	.LBB13_91
	.p2align	4
.LBB13_90:
	movq	632(%r13), %rdx
	movq	632(%rdx), %rdx
	movq	632(%rdx), %rdx
	movq	632(%rdx), %rdx
	movq	632(%rdx), %rdx
	movq	632(%rdx), %rdx
	movq	632(%rdx), %rdx
	movq	632(%rdx), %r13
	addq	$-8, %rcx
	jne	.LBB13_90
.LBB13_91:
	xorl	%r9d, %r9d
	xorl	%ecx, %ecx
	movzwl	626(%r13), %edx
	cmpq	%rdx, %r9
	jb	.LBB13_81
	.p2align	4
.LBB13_92:
	movq	352(%r13), %r15
	testq	%r15, %r15
	je	.LBB13_206
	incq	%rcx
	movzwl	624(%r13), %r11d
	movq	%r15, %r13
	cmpw	626(%r15), %r11w
	jae	.LBB13_92
.LBB13_94:
	testq	%rcx, %rcx
	je	.LBB13_101
	leaq	(%r15,%r11,8), %rdx
	addq	$640, %rdx
	movq	%rcx, %r8
	andq	$7, %r8
	je	.LBB13_140
	xorl	%r9d, %r9d
	.p2align	4
.LBB13_97:
	movq	(%rdx), %r13
	leaq	632(%r13), %rdx
	incq	%r9
	cmpq	%r9, %r8
	jne	.LBB13_97
	movq	%rcx, %r8
	subq	%r9, %r8
	cmpq	$8, %rcx
	jb	.LBB13_100
	.p2align	4
.LBB13_99:
	movq	(%rdx), %rcx
	movq	632(%rcx), %rcx
	movq	632(%rcx), %rcx
	movq	632(%rcx), %rcx
	movq	632(%rcx), %rcx
	movq	632(%rcx), %rcx
	movq	632(%rcx), %rcx
	movq	632(%rcx), %r13
	leaq	632(%r13), %rdx
	addq	$-8, %r8
	jne	.LBB13_99
.LBB13_100:
	movq	$0, -24(%rbp)
	jmp	.LBB13_102
.LBB13_101:
	leaq	1(%r11), %rcx
	movq	%rcx, -24(%rbp)
	movq	%r15, %r13
.LBB13_102:
	movq	%r11, -56(%rbp)
	leaq	(%r11,%r11,2), %rcx
	movq	368(%r15,%rcx,8), %rdx
	movq	%rdx, -8(%rbp)
	movq	376(%r15,%rcx,8), %rcx
	movq	%rcx, -32(%rbp)
	movq	(%r10), %rcx
	movq	%rcx, -16(%rbp)
	movq	(%rcx), %rdi
	testb	$1, %al
	jne	.LBB13_104
	jmp	.LBB13_111
	.p2align	4
.LBB13_103:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rax
	movq	%rbx, %rcx
	shrq	$32, %rcx
	callq	*16(%rax)
	testb	%al, %al
	je	.LBB13_173
.LBB13_104:
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	movl	$1, %r8d
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.23(%rip), %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB13_117
	movl	$9, %r8d
	movb	$41, %cl
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movq	%rax, %rbx
	andl	$3, %eax
	leaq	.LJTI13_3(%rip), %rcx
	movslq	(%rcx,%rax,4), %rax
	addq	%rcx, %rax
	jmpq	*%rax
.LBB13_106:
	cmpb	$35, 16(%rbx)
	je	.LBB13_104
	jmp	.LBB13_173
	.p2align	4
.LBB13_107:
	movq	%rbx, %rax
	shrq	$32, %rax
	cmpq	$43, %rax
	movl	$255, %ecx
	cmovael	%ecx, %eax
	cmpb	$35, %al
	je	.LBB13_104
	jmp	.LBB13_173
	.p2align	4
.LBB13_108:
	cmpb	$35, 31(%rbx)
	jne	.LBB13_173
	movq	%rbx, %rcx
	decq	%rcx
	callq	*23(%rbx)
	jmp	.LBB13_104
	.p2align	4
.LBB13_110:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rax
	movq	%rbx, %rcx
	shrq	$32, %rcx
	callq	*16(%rax)
	testb	%al, %al
	je	.LBB13_173
.LBB13_111:
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	movl	$2, %r8d
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.27(%rip), %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB13_117
	movl	$9, %r8d
	movb	$41, %cl
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movq	%rax, %rbx
	andl	$3, %eax
	leaq	.LJTI13_2(%rip), %rcx
	movslq	(%rcx,%rax,4), %rax
	addq	%rcx, %rax
	jmpq	*%rax
.LBB13_113:
	cmpb	$35, 16(%rbx)
	je	.LBB13_111
	jmp	.LBB13_173
	.p2align	4
.LBB13_114:
	movq	%rbx, %rax
	shrq	$32, %rax
	cmpq	$43, %rax
	movl	$255, %ecx
	cmovael	%ecx, %eax
	cmpb	$35, %al
	je	.LBB13_111
	jmp	.LBB13_173
	.p2align	4
.LBB13_115:
	cmpb	$35, 31(%rbx)
	jne	.LBB13_173
	movq	%rbx, %rcx
	decq	%rcx
	callq	*23(%rbx)
	jmp	.LBB13_111
.LBB13_117:
	movq	8(%rbp), %rax
	movq	24(%rax), %rax
	movq	%rax, -40(%rbp)
	testq	%rax, %rax
	je	.LBB13_129
	movq	8(%rbp), %rax
	movq	16(%rax), %rdi
	testq	%rdi, %rdi
	je	.LBB13_129
	movq	8(%rbp), %rax
	movq	8(%rax), %r12
	xorl	%r14d, %r14d
	jmp	.LBB13_121
	.p2align	4
.LBB13_120:
	incq	%r14
	cmpq	-40(%rbp), %r14
	je	.LBB13_129
.LBB13_121:
	movq	-16(%rbp), %rax
	movq	(%rax), %rsi
	jmp	.LBB13_123
	.p2align	4
.LBB13_122:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rax
	movq	%rbx, %rcx
	shrq	$32, %rcx
	callq	*16(%rax)
	testb	%al, %al
	je	.LBB13_173
.LBB13_123:
	movq	(%rsi), %rcx
	movq	8(%rsi), %rax
	movq	%r12, %rdx
	movq	%rdi, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB13_120
	movl	$9, %r8d
	movb	$41, %cl
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movq	%rax, %rbx
	andl	$3, %eax
	leaq	.LJTI13_4(%rip), %rcx
	movslq	(%rcx,%rax,4), %rax
	addq	%rcx, %rax
	jmpq	*%rax
.LBB13_125:
	cmpb	$35, 16(%rbx)
	je	.LBB13_123
	jmp	.LBB13_173
	.p2align	4
.LBB13_126:
	movq	%rbx, %rax
	shrq	$32, %rax
	cmpq	$43, %rax
	movl	$255, %ecx
	cmovael	%ecx, %eax
	cmpb	$35, %al
	je	.LBB13_123
	jmp	.LBB13_173
	.p2align	4
.LBB13_127:
	cmpb	$35, 31(%rbx)
	jne	.LBB13_173
	movq	%rbx, %rcx
	decq	%rcx
	callq	*23(%rbx)
	jmp	.LBB13_123
.LBB13_129:
	movq	8(%rbp), %rsi
	movq	(%rsi), %rcx
	movq	-8(%rbp), %rdx
	movq	-32(%rbp), %r8
	callq	_RNvXs1_NtCsavOST1yGCNT_10serde_json3serQINtB5_10SerializerQNtNvXs_NtB7_5valueNtB12_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterENtNtCslmkRZor3pUd_10serde_core3ser10Serializer13serialize_strB7_
	testq	%rax, %rax
	jne	.LBB13_202
	movq	(%rsi), %rax
	movq	(%rax), %rdi
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	movl	$2, %r8d
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.28(%rip), %rbx
	movq	%rbx, %rdx
	callq	*24(%rax)
	testb	%al, %al
	leaq	.LJTI13_5(%rip), %r14
	jne	.LBB13_135
.LBB13_131:
	movq	-56(%rbp), %rax
	shlq	$5, %rax
	addq	%rax, %r15
	movq	%r15, %rcx
	movq	8(%rbp), %rsi
	movq	%rsi, %rdx
	callq	_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_
	testq	%rax, %rax
	jne	.LBB13_202
	xorl	%eax, %eax
	movb	$1, 32(%rsi)
	movl	$0, %ecx
	decq	(%rbp)
	movq	%rsi, %r10
	movq	-24(%rbp), %r9
	jne	.LBB13_79
	jmp	.LBB13_174
	.p2align	4
.LBB13_133:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %rsi
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%rsi, %rax
	testb	%cl, %cl
	je	.LBB13_179
.LBB13_134:
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	movl	$2, %r8d
	movq	%rbx, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB13_131
.LBB13_135:
	movl	$9, %r8d
	movb	$41, %cl
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r14,%rcx,4), %rcx
	addq	%r14, %rcx
	jmpq	*%rcx
.LBB13_136:
	cmpb	$35, 16(%rax)
	je	.LBB13_134
	jmp	.LBB13_179
	.p2align	4
.LBB13_137:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	movl	$255, %edx
	cmovael	%edx, %ecx
	cmpb	$35, %cl
	je	.LBB13_134
	jmp	.LBB13_179
	.p2align	4
.LBB13_138:
	cmpb	$35, 31(%rax)
	jne	.LBB13_179
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB13_134
.LBB13_140:
	movq	%rcx, %r8
	cmpq	$8, %rcx
	jae	.LBB13_99
	jmp	.LBB13_100
.LBB13_141:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.31(%rip), %rdx
	movl	$5, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB13_177
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rsi
	leaq	.LJTI13_14(%rip), %r15
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.31(%rip), %rdi
	xorl	%ebx, %ebx
	movl	$255, %r12d
	jmp	.LBB13_145
	.p2align	4
.LBB13_143:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB13_179
.LBB13_144:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movl	$5, %r8d
	movq	%rdi, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB13_178
.LBB13_145:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rsi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB13_146:
	cmpb	$35, 16(%rax)
	je	.LBB13_144
	jmp	.LBB13_179
	.p2align	4
.LBB13_147:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB13_144
	jmp	.LBB13_179
	.p2align	4
.LBB13_148:
	cmpb	$35, 31(%rax)
	jne	.LBB13_179
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB13_144
.LBB13_150:
	movq	%rbx, %rdx
.LBB13_151:
	callq	_RINvXsd_NtCsavOST1yGCNT_10serde_json3serNtB6_15PrettyFormatterNtB6_9Formatter9end_arrayQNtNvXs_NtB8_5valueNtB1v_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEB8_
	jmp	.LBB13_176
.LBB13_152:
	movq	%rdi, %rdx
	jmp	.LBB13_175
.LBB13_153:
	movq	16(%rcx), %xmm0
	movq	%xmm0, %rax
	movabsq	$9223372036854775807, %rcx
	andq	%rax, %rcx
	movabsq	$9218868437227405312, %rax
	cmpq	%rax, %rcx
	jl	.LBB13_181
	movq	(%rbx), %r14
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.33(%rip), %rdx
	movl	$4, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB13_177
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rsi
	leaq	.LJTI13_11(%rip), %r15
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.33(%rip), %rdi
	xorl	%ebx, %ebx
	movl	$255, %r12d
	jmp	.LBB13_158
.LBB13_156:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB13_179
.LBB13_157:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movl	$4, %r8d
	movq	%rdi, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB13_178
.LBB13_158:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rsi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB13_159:
	cmpb	$35, 16(%rax)
	je	.LBB13_157
	jmp	.LBB13_179
.LBB13_160:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB13_157
	jmp	.LBB13_179
.LBB13_161:
	cmpb	$35, 31(%rax)
	jne	.LBB13_179
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB13_157
.LBB13_163:
	movq	16(%rcx), %rcx
	leaq	-96(%rbp), %rdx
	callq	_RNvXsu_Cs1KvuFdKMjOj_4itoayNtB5_8Unsigned3fmt
	movq	%rax, %rsi
	subq	$20, %rsi
	je	.LBB13_177
	negq	%rsi
	leaq	(%rax,%rbp), %rdi
	addq	$-96, %rdi
	movq	(%rbx), %r14
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movq	%rdi, %rdx
	movq	%rsi, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB13_177
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rbx
	leaq	.LJTI13_13(%rip), %r15
	movl	$255, %r12d
	jmp	.LBB13_168
.LBB13_166:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB13_205
.LBB13_167:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movq	%rdi, %rdx
	movq	%rsi, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB13_177
.LBB13_168:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rbx, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB13_169:
	cmpb	$35, 16(%rax)
	je	.LBB13_167
	jmp	.LBB13_205
.LBB13_170:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB13_167
	jmp	.LBB13_205
.LBB13_171:
	cmpb	$35, 31(%rax)
	jne	.LBB13_205
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB13_167
.LBB13_173:
	movq	%rbx, %rcx
	jmp	.LBB13_180
.LBB13_174:
	movq	(%r10), %rdx
	movq	-48(%rbp), %rcx
.LBB13_175:
	callq	_RINvXsd_NtCsavOST1yGCNT_10serde_json3serNtB6_15PrettyFormatterNtB6_9Formatter10end_objectQNtNvXs_NtB8_5valueNtB1x_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEB8_
.LBB13_176:
	testq	%rax, %rax
	jne	.LBB13_179
.LBB13_177:
	xorl	%ebx, %ebx
.LBB13_178:
	movq	%rbx, %rax
	.seh_startepilogue
	addq	$152, %rsp
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
.LBB13_179:
	movq	%rax, %rcx
.LBB13_180:
	.seh_startepilogue
	addq	$152, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r13
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	jmp	_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io
.LBB13_181:
	leaq	-96(%rbp), %rdi
	movq	%rdi, %rdx
	callq	_RNvXs_NtCs6FhewopUhnE_4zmij7privatedNtB4_6Sealed20write_to_zmij_buffer
	movq	%rax, %rsi
	subq	%rdi, %rsi
	je	.LBB13_177
	movq	(%rbx), %r14
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	-96(%rbp), %rdx
	movq	%rsi, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB13_177
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdi
	leaq	.LJTI13_10(%rip), %r15
	leaq	-96(%rbp), %rbx
	movl	$255, %r12d
	jmp	.LBB13_186
.LBB13_184:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB13_205
.LBB13_185:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movq	%rbx, %rdx
	movq	%rsi, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB13_177
.LBB13_186:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rdi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB13_187:
	cmpb	$35, 16(%rax)
	je	.LBB13_185
	jmp	.LBB13_205
.LBB13_188:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB13_185
	jmp	.LBB13_205
.LBB13_189:
	cmpb	$35, 31(%rax)
	jne	.LBB13_205
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB13_185
.LBB13_191:
	leaq	-1(%rax), %rcx
	cmpq	$19, %rcx
	ja	.LBB13_208
	movb	$45, -96(%rbp,%rcx)
	movl	$21, %esi
.LBB13_193:
	subq	%rax, %rsi
	leaq	(%rcx,%rbp), %rdi
	addq	$-96, %rdi
	movq	(%rbx), %r14
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movq	%rdi, %rdx
	movq	%rsi, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB13_177
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rbx
	leaq	.LJTI13_12(%rip), %r15
	movl	$255, %r12d
	jmp	.LBB13_197
.LBB13_195:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB13_205
.LBB13_196:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movq	%rdi, %rdx
	movq	%rsi, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB13_177
.LBB13_197:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rbx, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB13_198:
	cmpb	$35, 16(%rax)
	je	.LBB13_196
	jmp	.LBB13_205
.LBB13_199:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB13_196
	jmp	.LBB13_205
.LBB13_200:
	cmpb	$35, 31(%rax)
	jne	.LBB13_205
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB13_196
.LBB13_202:
	movq	%rax, %rbx
	jmp	.LBB13_178
.LBB13_205:
	movq	%rax, %rcx
	callq	_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io
	movq	%rax, %rbx
	jmp	.LBB13_178
.LBB13_206:
.Ltmp46:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.43(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	nop
.Ltmp47:
	ud2
.LBB13_208:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.129(%rip), %r8
	movl	$20, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_@IMGREL
	.section	.text,"xr",one_only,_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_,unique,14
	.seh_endproc
	.def	"?dtor$209@?0?_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$209@?0?_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_@4HA":
.seh_proc "?dtor$209@?0?_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_@4HA"
.LBB13_209:
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	ud2
.Lfunc_end13:
	.section	.rdata,"dr",associative,_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_,unique,15
	.p2align	2, 0x0
.LJTI13_0:
	.long	.LBB13_1-.LJTI13_0
	.long	.LBB13_25-.LJTI13_0
	.long	.LBB13_19-.LJTI13_0
	.long	.LBB13_24-.LJTI13_0
	.long	.LBB13_10-.LJTI13_0
	.long	.LBB13_35-.LJTI13_0
.LJTI13_1:
	.long	.LBB13_40-.LJTI13_1
	.long	.LBB13_42-.LJTI13_1
	.long	.LBB13_37-.LJTI13_1
	.long	.LBB13_41-.LJTI13_1
.LJTI13_2:
	.long	.LBB13_113-.LJTI13_2
	.long	.LBB13_115-.LJTI13_2
	.long	.LBB13_110-.LJTI13_2
	.long	.LBB13_114-.LJTI13_2
.LJTI13_3:
	.long	.LBB13_106-.LJTI13_3
	.long	.LBB13_108-.LJTI13_3
	.long	.LBB13_103-.LJTI13_3
	.long	.LBB13_107-.LJTI13_3
.LJTI13_4:
	.long	.LBB13_125-.LJTI13_4
	.long	.LBB13_127-.LJTI13_4
	.long	.LBB13_122-.LJTI13_4
	.long	.LBB13_126-.LJTI13_4
.LJTI13_5:
	.long	.LBB13_136-.LJTI13_5
	.long	.LBB13_138-.LJTI13_5
	.long	.LBB13_133-.LJTI13_5
	.long	.LBB13_137-.LJTI13_5
.LJTI13_6:
	.long	.LBB13_15-.LJTI13_6
	.long	.LBB13_17-.LJTI13_6
	.long	.LBB13_12-.LJTI13_6
	.long	.LBB13_16-.LJTI13_6
.LJTI13_7:
	.long	.LBB13_57-.LJTI13_7
	.long	.LBB13_59-.LJTI13_7
	.long	.LBB13_54-.LJTI13_7
	.long	.LBB13_58-.LJTI13_7
.LJTI13_8:
	.long	.LBB13_50-.LJTI13_8
	.long	.LBB13_52-.LJTI13_8
	.long	.LBB13_47-.LJTI13_8
	.long	.LBB13_51-.LJTI13_8
.LJTI13_9:
	.long	.LBB13_69-.LJTI13_9
	.long	.LBB13_71-.LJTI13_9
	.long	.LBB13_66-.LJTI13_9
	.long	.LBB13_70-.LJTI13_9
.LJTI13_10:
	.long	.LBB13_187-.LJTI13_10
	.long	.LBB13_189-.LJTI13_10
	.long	.LBB13_184-.LJTI13_10
	.long	.LBB13_188-.LJTI13_10
.LJTI13_11:
	.long	.LBB13_159-.LJTI13_11
	.long	.LBB13_161-.LJTI13_11
	.long	.LBB13_156-.LJTI13_11
	.long	.LBB13_160-.LJTI13_11
.LJTI13_12:
	.long	.LBB13_198-.LJTI13_12
	.long	.LBB13_200-.LJTI13_12
	.long	.LBB13_195-.LJTI13_12
	.long	.LBB13_199-.LJTI13_12
.LJTI13_13:
	.long	.LBB13_169-.LJTI13_13
	.long	.LBB13_171-.LJTI13_13
	.long	.LBB13_166-.LJTI13_13
	.long	.LBB13_170-.LJTI13_13
.LJTI13_14:
	.long	.LBB13_146-.LJTI13_14
	.long	.LBB13_148-.LJTI13_14
	.long	.LBB13_143-.LJTI13_14
	.long	.LBB13_147-.LJTI13_14
.LJTI13_15:
	.long	.LBB13_31-.LJTI13_15
	.long	.LBB13_33-.LJTI13_15
	.long	.LBB13_28-.LJTI13_15
	.long	.LBB13_32-.LJTI13_15
.LJTI13_16:
	.long	.LBB13_6-.LJTI13_16
	.long	.LBB13_8-.LJTI13_16
	.long	.LBB13_3-.LJTI13_16
	.long	.LBB13_7-.LJTI13_16
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_,unique,14
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_,unique,6
	.p2align	2, 0x0
$cppxdata$_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_@IMGREL
	.long	144
	.long	0
	.long	1
$stateUnwindMap$_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_:
	.long	-1
	.long	"?dtor$209@?0?_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_@4HA"@IMGREL
$ip2state$_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_:
	.long	.Lfunc_begin13@IMGREL
	.long	-1
	.long	.Ltmp46@IMGREL
	.long	0
	.long	.Ltmp47@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_,unique,14

	.def	_RINvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB6_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error6customNtNtCs8xEFJqa6dYS_4core3fmt9ArgumentsEB8_.llvm.16186315980599473920;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB6_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error6customNtNtCs8xEFJqa6dYS_4core3fmt9ArgumentsEB8_.llvm.16186315980599473920,unique,16
	.globl	_RINvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB6_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error6customNtNtCs8xEFJqa6dYS_4core3fmt9ArgumentsEB8_.llvm.16186315980599473920
	.p2align	4
_RINvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB6_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error6customNtNtCs8xEFJqa6dYS_4core3fmt9ArgumentsEB8_.llvm.16186315980599473920:
.Lfunc_begin14:
.seh_proc _RINvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB6_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error6customNtNtCs8xEFJqa6dYS_4core3fmt9ArgumentsEB8_.llvm.16186315980599473920
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$64, %rsp
	.seh_stackalloc 64
	.seh_endprologue
	movq	%rdx, %rsi
	movq	%rcx, %rdi
	testb	$1, %sil
	jne	.LBB14_1
	leaq	40(%rsp), %rcx
	movq	%rdi, %rdx
	movq	%rsi, %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	jmp	.LBB14_7
.LBB14_1:
	shrq	%rsi
	je	.LBB14_2
	movl	$1, %edx
	movq	%rsi, %rcx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB14_8
	movq	%rax, %rbx
	movq	%rax, %rcx
	movq	%rdi, %rdx
	movq	%rsi, %r8
	callq	memcpy
	jmp	.LBB14_5
.LBB14_2:
	movl	$1, %ebx
.LBB14_5:
	movq	%rsi, 40(%rsp)
	movq	%rbx, 48(%rsp)
	movq	%rsi, 56(%rsp)
.LBB14_7:
	leaq	40(%rsp), %rcx
	callq	_RNvNtCsavOST1yGCNT_10serde_json5error10make_error
	nop
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB14_8:
	movl	$1, %ecx
	movq	%rsi, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.Lfunc_end14:
	.seh_endproc

	.def	_RINvXsd_NtCsavOST1yGCNT_10serde_json3serNtB6_15PrettyFormatterNtB6_9Formatter10end_objectQNtNvXs_NtB8_5valueNtB1x_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEB8_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvXsd_NtCsavOST1yGCNT_10serde_json3serNtB6_15PrettyFormatterNtB6_9Formatter10end_objectQNtNvXs_NtB8_5valueNtB1x_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEB8_,unique,17
	.p2align	4
_RINvXsd_NtCsavOST1yGCNT_10serde_json3serNtB6_15PrettyFormatterNtB6_9Formatter10end_objectQNtNvXs_NtB8_5valueNtB1x_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEB8_:
.Lfunc_begin15:
.seh_proc _RINvXsd_NtCsavOST1yGCNT_10serde_json3serNtB6_15PrettyFormatterNtB6_9Formatter10end_objectQNtNvXs_NtB8_5valueNtB1x_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEB8_
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
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	16(%rcx), %r15
	decq	%r15
	movq	%r15, 16(%rcx)
	cmpb	$0, 24(%rcx)
	je	.LBB15_22
	movq	%rcx, %rdi
	movq	%rdx, 32(%rsp)
	movq	(%rdx), %r12
	movq	(%r12), %rcx
	movq	8(%r12), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.23(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB15_10
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rbx
	leaq	.LJTI15_0(%rip), %r13
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.23(%rip), %r14
	movl	$255, %esi
	jmp	.LBB15_5
	.p2align	4
.LBB15_3:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %rbp
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%rbp, %rax
	testb	%cl, %cl
	je	.LBB15_33
.LBB15_4:
	movq	(%r12), %rcx
	movq	8(%r12), %rax
	movl	$1, %r8d
	movq	%r14, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB15_10
.LBB15_5:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rbx, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r13,%rcx,4), %rcx
	addq	%r13, %rcx
	jmpq	*%rcx
.LBB15_6:
	cmpb	$35, 16(%rax)
	je	.LBB15_4
	jmp	.LBB15_33
	.p2align	4
.LBB15_7:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%esi, %ecx
	cmpb	$35, %cl
	je	.LBB15_4
	jmp	.LBB15_33
	.p2align	4
.LBB15_8:
	cmpb	$35, 31(%rax)
	jne	.LBB15_33
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB15_4
.LBB15_10:
	testq	%r15, %r15
	movq	32(%rsp), %rdx
	je	.LBB15_22
	movq	8(%rdi), %rbx
	testq	%rbx, %rbx
	je	.LBB15_22
	movq	(%rdi), %rdi
	xorl	%r12d, %r12d
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %r14
	leaq	.LJTI15_1(%rip), %r13
	jmp	.LBB15_14
	.p2align	4
.LBB15_13:
	incq	%r12
	cmpq	%r15, %r12
	movq	32(%rsp), %rdx
	je	.LBB15_22
.LBB15_14:
	movq	(%rdx), %rbp
	jmp	.LBB15_16
	.p2align	4
.LBB15_15:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %rsi
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%rsi, %rax
	testb	%cl, %cl
	je	.LBB15_33
.LBB15_16:
	movq	(%rbp), %rcx
	movq	8(%rbp), %rax
	movq	%rdi, %rdx
	movq	%rbx, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB15_13
	movl	$9, %r8d
	movb	$41, %cl
	movq	%r14, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r13,%rcx,4), %rcx
	addq	%r13, %rcx
	jmpq	*%rcx
.LBB15_18:
	cmpb	$35, 16(%rax)
	je	.LBB15_16
	jmp	.LBB15_33
	.p2align	4
.LBB15_19:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	movl	$255, %edx
	cmovael	%edx, %ecx
	cmpb	$35, %cl
	je	.LBB15_16
	jmp	.LBB15_33
	.p2align	4
.LBB15_20:
	cmpb	$35, 31(%rax)
	jne	.LBB15_33
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB15_16
.LBB15_22:
	movq	(%rdx), %rbx
	movq	(%rbx), %rcx
	movq	8(%rbx), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.24(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB15_32
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rsi
	leaq	.LJTI15_2(%rip), %r14
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.24(%rip), %rdi
	movl	$255, %ebp
	jmp	.LBB15_26
	.p2align	4
.LBB15_24:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r15
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r15, %rax
	testb	%cl, %cl
	je	.LBB15_33
.LBB15_25:
	movq	(%rbx), %rcx
	movq	8(%rbx), %rax
	movl	$1, %r8d
	movq	%rdi, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB15_32
.LBB15_26:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rsi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r14,%rcx,4), %rcx
	addq	%r14, %rcx
	jmpq	*%rcx
.LBB15_27:
	cmpb	$35, 16(%rax)
	je	.LBB15_25
	jmp	.LBB15_33
	.p2align	4
.LBB15_28:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%ebp, %ecx
	cmpb	$35, %cl
	je	.LBB15_25
	jmp	.LBB15_33
	.p2align	4
.LBB15_29:
	cmpb	$35, 31(%rax)
	jne	.LBB15_33
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB15_25
.LBB15_32:
	xorl	%eax, %eax
.LBB15_33:
	.seh_startepilogue
	addq	$40, %rsp
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
.Lfunc_end15:
	.section	.rdata,"dr",associative,_RINvXsd_NtCsavOST1yGCNT_10serde_json3serNtB6_15PrettyFormatterNtB6_9Formatter10end_objectQNtNvXs_NtB8_5valueNtB1x_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEB8_,unique,18
	.p2align	2, 0x0
.LJTI15_0:
	.long	.LBB15_6-.LJTI15_0
	.long	.LBB15_8-.LJTI15_0
	.long	.LBB15_3-.LJTI15_0
	.long	.LBB15_7-.LJTI15_0
.LJTI15_1:
	.long	.LBB15_18-.LJTI15_1
	.long	.LBB15_20-.LJTI15_1
	.long	.LBB15_15-.LJTI15_1
	.long	.LBB15_19-.LJTI15_1
.LJTI15_2:
	.long	.LBB15_27-.LJTI15_2
	.long	.LBB15_29-.LJTI15_2
	.long	.LBB15_24-.LJTI15_2
	.long	.LBB15_28-.LJTI15_2
	.section	.text,"xr",one_only,_RINvXsd_NtCsavOST1yGCNT_10serde_json3serNtB6_15PrettyFormatterNtB6_9Formatter10end_objectQNtNvXs_NtB8_5valueNtB1x_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEB8_,unique,17
	.seh_endproc

	.def	_RINvXsd_NtCsavOST1yGCNT_10serde_json3serNtB6_15PrettyFormatterNtB6_9Formatter9end_arrayQNtNvXs_NtB8_5valueNtB1v_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEB8_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvXsd_NtCsavOST1yGCNT_10serde_json3serNtB6_15PrettyFormatterNtB6_9Formatter9end_arrayQNtNvXs_NtB8_5valueNtB1v_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEB8_,unique,19
	.p2align	4
_RINvXsd_NtCsavOST1yGCNT_10serde_json3serNtB6_15PrettyFormatterNtB6_9Formatter9end_arrayQNtNvXs_NtB8_5valueNtB1v_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEB8_:
.Lfunc_begin16:
.seh_proc _RINvXsd_NtCsavOST1yGCNT_10serde_json3serNtB6_15PrettyFormatterNtB6_9Formatter9end_arrayQNtNvXs_NtB8_5valueNtB1v_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEB8_
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
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	16(%rcx), %r15
	decq	%r15
	movq	%r15, 16(%rcx)
	cmpb	$0, 24(%rcx)
	je	.LBB16_22
	movq	%rcx, %rdi
	movq	%rdx, 32(%rsp)
	movq	(%rdx), %r12
	movq	(%r12), %rcx
	movq	8(%r12), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.23(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB16_10
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rbx
	leaq	.LJTI16_0(%rip), %r13
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.23(%rip), %r14
	movl	$255, %esi
	jmp	.LBB16_5
	.p2align	4
.LBB16_3:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %rbp
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%rbp, %rax
	testb	%cl, %cl
	je	.LBB16_33
.LBB16_4:
	movq	(%r12), %rcx
	movq	8(%r12), %rax
	movl	$1, %r8d
	movq	%r14, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB16_10
.LBB16_5:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rbx, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r13,%rcx,4), %rcx
	addq	%r13, %rcx
	jmpq	*%rcx
.LBB16_6:
	cmpb	$35, 16(%rax)
	je	.LBB16_4
	jmp	.LBB16_33
	.p2align	4
.LBB16_7:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%esi, %ecx
	cmpb	$35, %cl
	je	.LBB16_4
	jmp	.LBB16_33
	.p2align	4
.LBB16_8:
	cmpb	$35, 31(%rax)
	jne	.LBB16_33
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB16_4
.LBB16_10:
	testq	%r15, %r15
	movq	32(%rsp), %rdx
	je	.LBB16_22
	movq	8(%rdi), %rbx
	testq	%rbx, %rbx
	je	.LBB16_22
	movq	(%rdi), %rdi
	xorl	%r12d, %r12d
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %r14
	leaq	.LJTI16_1(%rip), %r13
	jmp	.LBB16_14
	.p2align	4
.LBB16_13:
	incq	%r12
	cmpq	%r15, %r12
	movq	32(%rsp), %rdx
	je	.LBB16_22
.LBB16_14:
	movq	(%rdx), %rbp
	jmp	.LBB16_16
	.p2align	4
.LBB16_15:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %rsi
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%rsi, %rax
	testb	%cl, %cl
	je	.LBB16_33
.LBB16_16:
	movq	(%rbp), %rcx
	movq	8(%rbp), %rax
	movq	%rdi, %rdx
	movq	%rbx, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB16_13
	movl	$9, %r8d
	movb	$41, %cl
	movq	%r14, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r13,%rcx,4), %rcx
	addq	%r13, %rcx
	jmpq	*%rcx
.LBB16_18:
	cmpb	$35, 16(%rax)
	je	.LBB16_16
	jmp	.LBB16_33
	.p2align	4
.LBB16_19:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	movl	$255, %edx
	cmovael	%edx, %ecx
	cmpb	$35, %cl
	je	.LBB16_16
	jmp	.LBB16_33
	.p2align	4
.LBB16_20:
	cmpb	$35, 31(%rax)
	jne	.LBB16_33
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB16_16
.LBB16_22:
	movq	(%rdx), %rbx
	movq	(%rbx), %rcx
	movq	8(%rbx), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.29(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB16_32
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rsi
	leaq	.LJTI16_2(%rip), %r14
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.29(%rip), %rdi
	movl	$255, %ebp
	jmp	.LBB16_26
	.p2align	4
.LBB16_24:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r15
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r15, %rax
	testb	%cl, %cl
	je	.LBB16_33
.LBB16_25:
	movq	(%rbx), %rcx
	movq	8(%rbx), %rax
	movl	$1, %r8d
	movq	%rdi, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB16_32
.LBB16_26:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rsi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r14,%rcx,4), %rcx
	addq	%r14, %rcx
	jmpq	*%rcx
.LBB16_27:
	cmpb	$35, 16(%rax)
	je	.LBB16_25
	jmp	.LBB16_33
	.p2align	4
.LBB16_28:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%ebp, %ecx
	cmpb	$35, %cl
	je	.LBB16_25
	jmp	.LBB16_33
	.p2align	4
.LBB16_29:
	cmpb	$35, 31(%rax)
	jne	.LBB16_33
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB16_25
.LBB16_32:
	xorl	%eax, %eax
.LBB16_33:
	.seh_startepilogue
	addq	$40, %rsp
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
.Lfunc_end16:
	.section	.rdata,"dr",associative,_RINvXsd_NtCsavOST1yGCNT_10serde_json3serNtB6_15PrettyFormatterNtB6_9Formatter9end_arrayQNtNvXs_NtB8_5valueNtB1v_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEB8_,unique,20
	.p2align	2, 0x0
.LJTI16_0:
	.long	.LBB16_6-.LJTI16_0
	.long	.LBB16_8-.LJTI16_0
	.long	.LBB16_3-.LJTI16_0
	.long	.LBB16_7-.LJTI16_0
.LJTI16_1:
	.long	.LBB16_18-.LJTI16_1
	.long	.LBB16_20-.LJTI16_1
	.long	.LBB16_15-.LJTI16_1
	.long	.LBB16_19-.LJTI16_1
.LJTI16_2:
	.long	.LBB16_27-.LJTI16_2
	.long	.LBB16_29-.LJTI16_2
	.long	.LBB16_24-.LJTI16_2
	.long	.LBB16_28-.LJTI16_2
	.section	.text,"xr",one_only,_RINvXsd_NtCsavOST1yGCNT_10serde_json3serNtB6_15PrettyFormatterNtB6_9Formatter9end_arrayQNtNvXs_NtB8_5valueNtB1v_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEB8_,unique,19
	.seh_endproc

	.def	_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io,unique,21
	.globl	_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io
	.p2align	4
_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io:
.Lfunc_begin17:
.seh_proc _RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$80, %rsp
	.seh_stackalloc 80
	leaq	80(%rsp), %rbp
	.seh_setframe %rbp, 80
	.seh_endprologue
	movq	$-2, -8(%rbp)
	movq	$1, -48(%rbp)
	movq	%rcx, -40(%rbp)
	xorps	%xmm0, %xmm0
	movups	%xmm0, -24(%rbp)
	movl	$40, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB17_1
	movq	-16(%rbp), %rcx
	movq	%rcx, 32(%rax)
	movups	-48(%rbp), %xmm0
	movups	-32(%rbp), %xmm1
	movups	%xmm1, 16(%rax)
	movups	%xmm0, (%rax)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.LBB17_1:
.Ltmp48:
	movl	$8, %ecx
	movl	$40, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp49:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io@IMGREL
	.section	.text$unlikely,"xr",one_only,_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io,unique,21
	.seh_endproc
	.def	"?dtor$3@?0?_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$3@?0?_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io@4HA":
.seh_proc "?dtor$3@?0?_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io@4HA"
.LBB17_3:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	80(%rdx), %rbp
	.seh_endprologue
	leaq	-48(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5error9ErrorImplEBF_.llvm.16186315980599473920
	nop
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end17:
	.seh_handlerdata
	.section	.text$unlikely,"xr",one_only,_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io,unique,21
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io,unique,7
	.p2align	2, 0x0
$cppxdata$_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io@IMGREL
	.long	72
	.long	0
	.long	1
$stateUnwindMap$_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io:
	.long	-1
	.long	"?dtor$3@?0?_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io@4HA"@IMGREL
$ip2state$_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io:
	.long	.Lfunc_begin17@IMGREL
	.long	-1
	.long	.Ltmp48@IMGREL
	.long	0
	.long	.Ltmp49@IMGREL
	.long	-1
	.section	.text$unlikely,"xr",one_only,_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io,unique,21

	.def	_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax,unique,22
	.globl	_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax
	.p2align	4
_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax:
.Lfunc_begin18:
.seh_proc _RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$80, %rsp
	.seh_stackalloc 80
	leaq	80(%rsp), %rbp
	.seh_setframe %rbp, 80
	.seh_endprologue
	movq	$-2, -8(%rbp)
	movq	16(%rcx), %rax
	movq	%rax, -32(%rbp)
	movups	(%rcx), %xmm0
	movaps	%xmm0, -48(%rbp)
	movq	%rdx, -24(%rbp)
	movq	%r8, -16(%rbp)
	movl	$40, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB18_1
	movq	-16(%rbp), %rcx
	movq	%rcx, 32(%rax)
	movaps	-48(%rbp), %xmm0
	movaps	-32(%rbp), %xmm1
	movups	%xmm1, 16(%rax)
	movups	%xmm0, (%rax)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.LBB18_1:
.Ltmp50:
	movl	$8, %ecx
	movl	$40, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp51:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax@IMGREL
	.section	.text$unlikely,"xr",one_only,_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax,unique,22
	.seh_endproc
	.def	"?dtor$3@?0?_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$3@?0?_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax@4HA":
.seh_proc "?dtor$3@?0?_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax@4HA"
.LBB18_3:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	80(%rdx), %rbp
	.seh_endprologue
	leaq	-48(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5error9ErrorImplEBF_.llvm.16186315980599473920
	nop
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end18:
	.seh_handlerdata
	.section	.text$unlikely,"xr",one_only,_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax,unique,22
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax,unique,8
	.p2align	2, 0x0
$cppxdata$_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax@IMGREL
	.long	72
	.long	0
	.long	1
$stateUnwindMap$_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax:
	.long	-1
	.long	"?dtor$3@?0?_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax@4HA"@IMGREL
$ip2state$_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax:
	.long	.Lfunc_begin18@IMGREL
	.long	-1
	.long	.Ltmp50@IMGREL
	.long	0
	.long	.Ltmp51@IMGREL
	.long	-1
	.section	.text$unlikely,"xr",one_only,_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax,unique,22

	.def	_RNvMs2_NtCsavOST1yGCNT_10serde_json2deNtB5_12ParserNumber12invalid_type;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs2_NtCsavOST1yGCNT_10serde_json2deNtB5_12ParserNumber12invalid_type,unique,23
	.globl	_RNvMs2_NtCsavOST1yGCNT_10serde_json2deNtB5_12ParserNumber12invalid_type
	.p2align	4
_RNvMs2_NtCsavOST1yGCNT_10serde_json2deNtB5_12ParserNumber12invalid_type:
.Lfunc_begin19:
.seh_proc _RNvMs2_NtCsavOST1yGCNT_10serde_json2deNtB5_12ParserNumber12invalid_type
	subq	$56, %rsp
	.seh_stackalloc 56
	.seh_endprologue
	movq	(%rcx), %rax
	testq	%rax, %rax
	je	.LBB19_4
	cmpl	$1, %eax
	jne	.LBB19_5
	movq	8(%rcx), %rax
	movq	%rax, 40(%rsp)
	movb	$1, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error12invalid_type
	nop
	.seh_startepilogue
	addq	$56, %rsp
	.seh_endepilogue
	retq
.LBB19_4:
	movsd	8(%rcx), %xmm0
	movsd	%xmm0, 40(%rsp)
	movb	$3, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error12invalid_type
	nop
	.seh_startepilogue
	addq	$56, %rsp
	.seh_endepilogue
	retq
.LBB19_5:
	movq	8(%rcx), %rax
	movq	%rax, 40(%rsp)
	movb	$2, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error12invalid_type
	nop
	.seh_startepilogue
	addq	$56, %rsp
	.seh_endepilogue
	retq
.Lfunc_end19:
	.seh_endproc

	.def	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_,unique,24
	.p2align	4
_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_:
.Lfunc_begin20:
.seh_proc _RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_
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
	subq	$64, %rsp
	.seh_stackalloc 64
	leaq	64(%rsp), %rbp
	.seh_setframe %rbp, 64
	.seh_endprologue
	movq	$-2, -8(%rbp)
	movq	%rdx, -24(%rbp)
	movq	32(%rcx), %rdi
	movq	40(%rcx), %rsi
	incq	%rsi
	cmpq	%rdi, %rsi
	cmovaeq	%rdi, %rsi
	movq	24(%rcx), %rbx
	leaq	(%rbx,%rsi), %r8
	movq	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw2FN(%rip), %rax
	movb	$1, -9(%rbp)
.Ltmp52:
	movb	$10, %cl
	movq	%rbx, %rdx
	callq	*%rax
	nop
.Ltmp53:
	cmpq	$1, %rax
	jne	.LBB20_2
	subq	%rbx, %rdx
	leaq	1(%rdx), %r14
	cmpq	%rdi, %rdx
	jb	.LBB20_3
	movb	$1, -9(%rbp)
.Ltmp54:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920(%rip), %r9
	xorl	%ecx, %ecx
	movq	%r14, %rdx
	movq	%rdi, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	nop
.Ltmp55:
	ud2
.LBB20_2:
	xorl	%r14d, %r14d
.LBB20_3:
	leaq	(%rbx,%r14), %r8
	movq	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw2FN(%rip), %rax
	movb	$1, -9(%rbp)
.Ltmp56:
	movb	$10, %cl
	movq	%rbx, %rdx
	callq	*%rax
	nop
.Ltmp57:
	incq	%rax
	subq	%r14, %rsi
	movb	$0, -9(%rbp)
.Ltmp58:
	movq	-24(%rbp), %rcx
	movq	%rax, %rdx
	movq	%rsi, %r8
	callq	_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax
	nop
.Ltmp59:
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.long	$cppxdata$_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_@IMGREL
	.section	.text$unlikely,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_,unique,24
	.seh_endproc
	.def	"?dtor$9@?0?_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$9@?0?_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_@4HA":
.seh_proc "?dtor$9@?0?_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_@4HA"
.LBB20_9:
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
	leaq	64(%rdx), %rbp
	.seh_endprologue
	cmpb	$0, -9(%rbp)
	jne	.LBB20_10
.LBB20_11:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.LBB20_10:
	movq	-24(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5error9ErrorCodeEBF_
	jmp	.LBB20_11
.Lfunc_end20:
	.seh_handlerdata
	.section	.text$unlikely,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_,unique,24
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_,unique,9
	.p2align	2, 0x0
$cppxdata$_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_@IMGREL
	.long	56
	.long	0
	.long	1
$stateUnwindMap$_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_:
	.long	-1
	.long	"?dtor$9@?0?_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_@4HA"@IMGREL
$ip2state$_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_:
	.long	.Lfunc_begin20@IMGREL
	.long	-1
	.long	.Ltmp52@IMGREL
	.long	0
	.long	.Ltmp59@IMGREL
	.long	-1
	.section	.text$unlikely,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_,unique,24

	.def	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE14parse_exponentB7_;
	.scl	3;
	.type	32;
	.endef
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
	.globl	__real@7fe1ccf385ebc8a0
	.section	.rdata,"dr",discard,__real@7fe1ccf385ebc8a0
	.p2align	3, 0x0
__real@7fe1ccf385ebc8a0:
	.quad	0x7fe1ccf385ebc8a0
	.globl	__xmm@80000000000000008000000000000000
	.section	.rdata,"dr",discard,__xmm@80000000000000008000000000000000
	.p2align	4, 0x0
__xmm@80000000000000008000000000000000:
	.quad	0x8000000000000000
	.quad	0x8000000000000000
	.section	.text,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE14parse_exponentB7_,unique,25
	.p2align	4
_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE14parse_exponentB7_:
.Lfunc_begin21:
.seh_proc _RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE14parse_exponentB7_
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$64, %rsp
	.seh_stackalloc 64
	.seh_endprologue
	movq	32(%rdx), %rsi
	movq	40(%rdx), %r11
	leaq	1(%r11), %r10
	movq	%r10, 40(%rdx)
	movb	$1, %al
	cmpq	%rsi, %r10
	jae	.LBB21_5
	movq	24(%rdx), %rax
	movzbl	(%rax,%r10), %edi
	movb	$1, %al
	cmpl	$43, %edi
	je	.LBB21_4
	cmpl	$45, %edi
	jne	.LBB21_5
	xorl	%eax, %eax
.LBB21_4:
	addq	$2, %r11
	movq	%r11, 40(%rdx)
	movq	%r11, %r10
.LBB21_5:
	cmpq	%rsi, %r10
	jae	.LBB21_8
	movq	24(%rdx), %rdi
	movzbl	(%rdi,%r10), %r11d
	leaq	1(%r10), %rbx
	movq	%rbx, 40(%rdx)
	addb	$-48, %r11b
	cmpb	$10, %r11b
	jae	.LBB21_7
	movzbl	%r11b, %r11d
	cmpq	%rsi, %rbx
	jae	.LBB21_13
	movl	$1, %ebx
	subq	%rsi, %rbx
	addq	$2, %r10
	jmp	.LBB21_12
	.p2align	4
.LBB21_33:
	movzbl	%sil, %esi
	leal	(%r11,%r11,4), %r11d
	leal	(%rsi,%r11,2), %r11d
	leaq	(%rbx,%r10), %rsi
	incq	%rsi
	incq	%r10
	cmpq	$2, %rsi
	je	.LBB21_13
.LBB21_12:
	movzbl	-1(%rdi,%r10), %esi
	addb	$-48, %sil
	cmpb	$10, %sil
	jae	.LBB21_13
	movq	%r10, 40(%rdx)
	cmpl	$214748363, %r11d
	jle	.LBB21_33
	cmpl	$214748364, %r11d
	jne	.LBB21_34
	cmpb	$7, %sil
	jbe	.LBB21_33
.LBB21_34:
	testq	%r9, %r9
	sete	%r9b
	movb	%al, 32(%rsp)
	callq	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE23parse_exponent_overflowB7_
	jmp	.LBB21_29
.LBB21_13:
	movl	128(%rsp), %r10d
	testb	%al, %al
	je	.LBB21_14
	leal	(%r10,%r11), %eax
	sarl	$31, %eax
	addl	$-2147483648, %eax
	addl	%r11d, %r10d
	jmp	.LBB21_16
.LBB21_14:
	xorl	%eax, %eax
	cmpl	%r11d, %r10d
	setns	%al
	addl	$2147483647, %eax
	subl	%r11d, %r10d
.LBB21_16:
	cmovol	%eax, %r10d
	movq	%r9, %xmm1
	punpckldq	__xmm@00000000000000004530000043300000(%rip), %xmm1
	subpd	__xmm@45300000000000004330000000000000(%rip), %xmm1
	movapd	%xmm1, %xmm0
	unpckhpd	%xmm1, %xmm0
	addsd	%xmm1, %xmm0
	movl	%r10d, %eax
	negl	%eax
	cmovsl	%r10d, %eax
	cmpl	$309, %eax
	jb	.LBB21_21
	xorpd	%xmm1, %xmm1
	movsd	__real@7fe1ccf385ebc8a0(%rip), %xmm2
	.p2align	4
.LBB21_18:
	ucomisd	%xmm1, %xmm0
	jne	.LBB21_19
	jnp	.LBB21_23
.LBB21_19:
	testl	%r10d, %r10d
	jns	.LBB21_27
	divsd	%xmm2, %xmm0
	addl	$308, %r10d
	movl	%r10d, %eax
	negl	%eax
	cmovsl	%r10d, %eax
	cmpl	$309, %eax
	jae	.LBB21_18
.LBB21_21:
	movl	%eax, %eax
	leaq	_RNvNtCsavOST1yGCNT_10serde_json2de5POW10(%rip), %r9
	movsd	(%r9,%rax,8), %xmm1
	testl	%r10d, %r10d
	js	.LBB21_22
	mulsd	%xmm1, %xmm0
	movq	%xmm0, %rax
	movabsq	$9223372036854775807, %r9
	andq	%rax, %r9
	movabsq	$9218868437227405312, %rax
	cmpq	%rax, %r9
	je	.LBB21_27
.LBB21_23:
	testb	%r8b, %r8b
	jne	.LBB21_25
.LBB21_24:
	xorpd	__xmm@80000000000000008000000000000000(%rip), %xmm0
.LBB21_25:
	movsd	%xmm0, 8(%rcx)
	xorl	%eax, %eax
.LBB21_28:
	movq	%rax, (%rcx)
.LBB21_29:
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB21_22:
	divsd	%xmm1, %xmm0
	testb	%r8b, %r8b
	je	.LBB21_24
	jmp	.LBB21_25
.LBB21_8:
	movq	$5, 40(%rsp)
.LBB21_9:
	leaq	40(%rsp), %rax
	movq	%rcx, %rsi
	movq	%rdx, %rcx
	movq	%rax, %rdx
	callq	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_
	movq	%rax, 8(%rsi)
	movq	$1, (%rsi)
	jmp	.LBB21_29
.LBB21_27:
	movq	$14, 40(%rsp)
	leaq	40(%rsp), %rax
	movq	%rcx, %rsi
	movq	%rdx, %rcx
	movq	%rax, %rdx
	callq	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_
	movq	%rsi, %rcx
	movq	%rax, 8(%rsi)
	movl	$1, %eax
	jmp	.LBB21_28
.LBB21_7:
	movq	$13, 40(%rsp)
	jmp	.LBB21_9
.Lfunc_end21:
	.seh_endproc

	.def	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE18parse_long_integerB7_;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE18parse_long_integerB7_,unique,26
	.globl	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE18parse_long_integerB7_
	.p2align	4
_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE18parse_long_integerB7_:
.Lfunc_begin22:
.seh_proc _RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE18parse_long_integerB7_
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
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movq	32(%rdx), %rbx
	movq	40(%rdx), %r10
	xorl	%edi, %edi
	movq	%r10, %r14
	subq	%rbx, %r14
	jae	.LBB22_8
	movq	24(%rdx), %rsi
	movl	%ebx, %edi
	subl	%r10d, %edi
	leal	-1(%rbx), %r11d
	leaq	(%rsi,%r10), %r15
	xorl	%eax, %eax
	.p2align	4
.LBB22_2:
	movzbl	(%r15,%rax), %r12d
	leal	-48(%r12), %ebp
	cmpb	$10, %bpl
	jae	.LBB22_3
	leaq	(%r10,%rax), %r12
	incq	%r12
	movq	%r12, 40(%rdx)
	incq	%rax
	addq	$-2, %r11
	movq	%r14, %r12
	addq	%rax, %r12
	jne	.LBB22_2
	jmp	.LBB22_8
.LBB22_3:
	cmpl	$46, %r12d
	je	.LBB22_18
	cmpl	$69, %r12d
	je	.LBB22_37
	cmpl	$101, %r12d
	je	.LBB22_37
	movl	%eax, %edi
.LBB22_8:
	movq	%r9, %xmm1
	punpckldq	__xmm@00000000000000004530000043300000(%rip), %xmm1
	subpd	__xmm@45300000000000004330000000000000(%rip), %xmm1
	movapd	%xmm1, %xmm0
	unpckhpd	%xmm1, %xmm0
	addsd	%xmm1, %xmm0
	movl	%edi, %eax
	negl	%eax
	cmovsl	%edi, %eax
	cmpl	$309, %eax
	jb	.LBB22_13
	xorpd	%xmm1, %xmm1
	movsd	__real@7fe1ccf385ebc8a0(%rip), %xmm2
	.p2align	4
.LBB22_10:
	ucomisd	%xmm1, %xmm0
	jne	.LBB22_11
	jnp	.LBB22_15
.LBB22_11:
	testl	%edi, %edi
	jns	.LBB22_35
	divsd	%xmm2, %xmm0
	addl	$308, %edi
	movl	%edi, %eax
	negl	%eax
	cmovsl	%edi, %eax
	cmpl	$309, %eax
	jae	.LBB22_10
.LBB22_13:
	movl	%eax, %eax
	leaq	_RNvNtCsavOST1yGCNT_10serde_json2de5POW10(%rip), %r9
	movsd	(%r9,%rax,8), %xmm1
	testl	%edi, %edi
	js	.LBB22_14
.LBB22_34:
	mulsd	%xmm1, %xmm0
	movq	%xmm0, %rax
	movabsq	$9223372036854775807, %r9
	andq	%rax, %r9
	movabsq	$9218868437227405312, %rax
	cmpq	%rax, %r9
	jne	.LBB22_15
.LBB22_35:
	movq	$14, 48(%rsp)
	leaq	48(%rsp), %rax
	movq	%rcx, %rsi
	movq	%rdx, %rcx
	movq	%rax, %rdx
	callq	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_
	movq	%rax, 8(%rsi)
	movl	$1, %eax
	movq	%rax, (%rsi)
	movq	%rsi, %rax
	jmp	.LBB22_39
.LBB22_18:
	leaq	(%r10,%rax), %rdi
	incq	%rdi
	movq	%rdi, 40(%rdx)
	cmpq	%rbx, %rdi
	jae	.LBB22_26
	leaq	(%r10,%rax), %r14
	addq	$2, %r14
	movabsq	$1844674407370955160, %r15
	movl	$1, %edi
	subl	%ebx, %edi
	addq	%r10, %rdi
	addq	%rax, %rdi
	movl	$1, %r12d
	subq	%rbx, %r12
	xorl	%ebx, %ebx
	jmp	.LBB22_20
	.p2align	4
.LBB22_43:
	movzbl	%r13b, %r13d
	movq	%r14, 40(%rdx)
	leaq	(%r9,%r9,4), %r9
	leaq	(,%r9,2), %r9
	addq	%r13, %r9
	incl	%ebx
	leaq	(%r12,%r14), %r13
	incq	%r13
	incq	%r14
	cmpq	$2, %r13
	je	.LBB22_24
.LBB22_20:
	movzbl	-1(%rsi,%r14), %ebp
	leal	-48(%rbp), %r13d
	cmpb	$10, %r13b
	jae	.LBB22_21
	cmpq	%r15, %r9
	jbe	.LBB22_43
	leaq	1(%r15), %rbp
	cmpq	%rbp, %r9
	jne	.LBB22_44
	cmpb	$5, %r13b
	jbe	.LBB22_43
.LBB22_44:
	subl	%ebx, %eax
	movl	%eax, 32(%rsp)
	movq	%rcx, %rsi
	callq	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE22parse_decimal_overflowB7_
	jmp	.LBB22_38
.LBB22_21:
	testl	%ebx, %ebx
	je	.LBB22_22
	subl	%ebx, %eax
	orl	$32, %ebp
	cmpl	$101, %ebp
	jne	.LBB22_28
.LBB22_37:
	movl	%eax, 32(%rsp)
	movq	%rcx, %rsi
	callq	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE14parse_exponentB7_
.LBB22_38:
	movq	%rsi, %rax
	jmp	.LBB22_39
.LBB22_24:
	testl	%edi, %edi
	je	.LBB22_26
	subl	%r11d, %r10d
	movl	%r10d, %eax
.LBB22_28:
	movq	%r9, %xmm1
	punpckldq	__xmm@00000000000000004530000043300000(%rip), %xmm1
	subpd	__xmm@45300000000000004330000000000000(%rip), %xmm1
	movapd	%xmm1, %xmm0
	unpckhpd	%xmm1, %xmm0
	addsd	%xmm1, %xmm0
	movl	%eax, %r9d
	negl	%r9d
	cmovsl	%eax, %r9d
	cmpl	$309, %r9d
	jb	.LBB22_33
	xorpd	%xmm1, %xmm1
	movsd	__real@7fe1ccf385ebc8a0(%rip), %xmm2
	.p2align	4
.LBB22_30:
	ucomisd	%xmm1, %xmm0
	jne	.LBB22_31
	jnp	.LBB22_15
.LBB22_31:
	testl	%eax, %eax
	jns	.LBB22_35
	divsd	%xmm2, %xmm0
	addl	$308, %eax
	movl	%eax, %r9d
	negl	%r9d
	cmovsl	%eax, %r9d
	cmpl	$309, %r9d
	jae	.LBB22_30
.LBB22_33:
	movl	%r9d, %r9d
	leaq	_RNvNtCsavOST1yGCNT_10serde_json2de5POW10(%rip), %r10
	movsd	(%r10,%r9,8), %xmm1
	testl	%eax, %eax
	jns	.LBB22_34
.LBB22_14:
	divsd	%xmm1, %xmm0
.LBB22_15:
	testb	%r8b, %r8b
	jne	.LBB22_17
	xorpd	__xmm@80000000000000008000000000000000(%rip), %xmm0
.LBB22_17:
	movsd	%xmm0, 8(%rcx)
	xorl	%eax, %eax
	movq	%rax, (%rcx)
	movq	%rcx, %rax
.LBB22_39:
	.seh_startepilogue
	addq	$72, %rsp
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
.LBB22_26:
	movq	$5, 48(%rsp)
	jmp	.LBB22_23
.LBB22_22:
	movq	$13, 48(%rsp)
.LBB22_23:
	leaq	48(%rsp), %rax
	movq	%rcx, %rsi
	movq	%rdx, %rcx
	movq	%rax, %rdx
	callq	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_
	movq	%rax, 8(%rsi)
	movq	$1, (%rsi)
	movq	%rsi, %rax
	jmp	.LBB22_39
.Lfunc_end22:
	.seh_endproc

	.def	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE22parse_decimal_overflowB7_;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE22parse_decimal_overflowB7_,unique,27
	.globl	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE22parse_decimal_overflowB7_
	.p2align	4
_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE22parse_decimal_overflowB7_:
.Lfunc_begin23:
.seh_proc _RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE22parse_decimal_overflowB7_
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$64, %rsp
	.seh_stackalloc 64
	.seh_endprologue
	movl	128(%rsp), %eax
	movq	32(%rdx), %r10
	movq	40(%rdx), %r11
	cmpq	%r10, %r11
	jae	.LBB23_5
	movq	24(%rdx), %rsi
	negq	%r10
	incq	%r11
	.p2align	4
.LBB23_2:
	movzbl	-1(%rsi,%r11), %edi
	leal	-48(%rdi), %ebx
	cmpb	$9, %bl
	ja	.LBB23_4
	movq	%r11, 40(%rdx)
	leaq	(%r10,%r11), %rdi
	incq	%rdi
	incq	%r11
	cmpq	$1, %rdi
	jne	.LBB23_2
	jmp	.LBB23_5
.LBB23_4:
	orl	$32, %edi
	cmpl	$101, %edi
	jne	.LBB23_5
	movl	%eax, 32(%rsp)
	movq	%rcx, %rsi
	callq	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE14parse_exponentB7_
	movq	%rsi, %rax
	jmp	.LBB23_18
.LBB23_5:
	movq	%r9, %xmm1
	punpckldq	__xmm@00000000000000004530000043300000(%rip), %xmm1
	subpd	__xmm@45300000000000004330000000000000(%rip), %xmm1
	movapd	%xmm1, %xmm0
	unpckhpd	%xmm1, %xmm0
	addsd	%xmm1, %xmm0
	movl	%eax, %r9d
	negl	%r9d
	cmovsl	%eax, %r9d
	cmpl	$309, %r9d
	jb	.LBB23_10
	xorpd	%xmm1, %xmm1
	movsd	__real@7fe1ccf385ebc8a0(%rip), %xmm2
	.p2align	4
.LBB23_7:
	ucomisd	%xmm1, %xmm0
	jne	.LBB23_8
	jnp	.LBB23_12
.LBB23_8:
	testl	%eax, %eax
	jns	.LBB23_16
	divsd	%xmm2, %xmm0
	addl	$308, %eax
	movl	%eax, %r9d
	negl	%r9d
	cmovsl	%eax, %r9d
	cmpl	$309, %r9d
	jae	.LBB23_7
.LBB23_10:
	movl	%r9d, %r9d
	leaq	_RNvNtCsavOST1yGCNT_10serde_json2de5POW10(%rip), %r10
	movsd	(%r10,%r9,8), %xmm1
	testl	%eax, %eax
	js	.LBB23_11
	mulsd	%xmm1, %xmm0
	movq	%xmm0, %rax
	movabsq	$9223372036854775807, %r9
	andq	%rax, %r9
	movabsq	$9218868437227405312, %rax
	cmpq	%rax, %r9
	je	.LBB23_16
.LBB23_12:
	testb	%r8b, %r8b
	jne	.LBB23_14
.LBB23_13:
	xorpd	__xmm@80000000000000008000000000000000(%rip), %xmm0
.LBB23_14:
	movsd	%xmm0, 8(%rcx)
	xorl	%eax, %eax
.LBB23_17:
	movq	%rax, (%rcx)
	movq	%rcx, %rax
.LBB23_18:
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB23_11:
	divsd	%xmm1, %xmm0
	testb	%r8b, %r8b
	je	.LBB23_13
	jmp	.LBB23_14
.LBB23_16:
	movq	$14, 40(%rsp)
	leaq	40(%rsp), %rax
	movq	%rcx, %rsi
	movq	%rdx, %rcx
	movq	%rax, %rdx
	callq	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_
	movq	%rsi, %rcx
	movq	%rax, 8(%rsi)
	movl	$1, %eax
	jmp	.LBB23_17
.Lfunc_end23:
	.seh_endproc

	.def	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE23parse_exponent_overflowB7_;
	.scl	2;
	.type	32;
	.endef
	.globl	__real@8000000000000000
	.section	.rdata,"dr",discard,__real@8000000000000000
	.p2align	3, 0x0
__real@8000000000000000:
	.quad	0x8000000000000000
	.section	.text$unlikely,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE23parse_exponent_overflowB7_,unique,28
	.globl	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE23parse_exponent_overflowB7_
	.p2align	4
_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE23parse_exponent_overflowB7_:
.Lfunc_begin24:
.seh_proc _RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE23parse_exponent_overflowB7_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$64, %rsp
	.seh_stackalloc 64
	.seh_endprologue
	movq	%rcx, %rax
	movzbl	112(%rsp), %ecx
	xorb	$1, %cl
	orb	%r9b, %cl
	cmpb	$1, %cl
	jne	.LBB24_9
	movq	32(%rdx), %rcx
	movq	40(%rdx), %r9
	cmpq	%rcx, %r9
	jae	.LBB24_5
	movq	24(%rdx), %r10
	negq	%rcx
	incq	%r9
	.p2align	4
.LBB24_3:
	movzbl	-1(%r10,%r9), %r11d
	addb	$-48, %r11b
	cmpb	$10, %r11b
	jae	.LBB24_5
	movq	%r9, 40(%rdx)
	leaq	(%rcx,%r9), %r11
	incq	%r11
	incq	%r9
	cmpq	$1, %r11
	jne	.LBB24_3
.LBB24_5:
	xorps	%xmm0, %xmm0
	testb	%r8b, %r8b
	jne	.LBB24_7
	movsd	__real@8000000000000000(%rip), %xmm0
.LBB24_7:
	movsd	%xmm0, 8(%rax)
	xorl	%ecx, %ecx
	movq	%rcx, (%rax)
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB24_9:
	movq	$14, 40(%rsp)
	leaq	40(%rsp), %r8
	movq	%rdx, %rcx
	movq	%r8, %rdx
	movq	%rax, %rsi
	callq	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_
	movq	%rax, %rcx
	movq	%rsi, %rax
	movq	%rcx, 8(%rsi)
	movl	$1, %ecx
	movq	%rcx, (%rax)
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end24:
	.seh_endproc

	.def	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_,unique,29
	.p2align	4
_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_:
.Lfunc_begin25:
.seh_proc _RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_
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
	subq	$64, %rsp
	.seh_stackalloc 64
	leaq	64(%rsp), %rbp
	.seh_setframe %rbp, 64
	.seh_endprologue
	movq	$-2, -8(%rbp)
	movq	%rdx, -24(%rbp)
	movq	40(%rcx), %rsi
	movq	32(%rcx), %rdi
	cmpq	%rdi, %rsi
	ja	.LBB25_9
	movq	24(%rcx), %rbx
	leaq	(%rbx,%rsi), %r8
	movq	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw2FN(%rip), %rax
	movb	$1, -9(%rbp)
.Ltmp60:
	movb	$10, %cl
	movq	%rbx, %rdx
	callq	*%rax
	nop
.Ltmp61:
	cmpq	$1, %rax
	jne	.LBB25_3
	subq	%rbx, %rdx
	leaq	1(%rdx), %r14
	cmpq	%rdi, %rdx
	jb	.LBB25_4
	movb	$1, -9(%rbp)
.Ltmp62:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920(%rip), %r9
	xorl	%ecx, %ecx
	movq	%r14, %rdx
	movq	%rdi, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	nop
.Ltmp63:
	jmp	.LBB25_10
.LBB25_3:
	xorl	%r14d, %r14d
.LBB25_4:
	leaq	(%rbx,%r14), %r8
	movq	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw2FN(%rip), %rax
	movb	$1, -9(%rbp)
.Ltmp64:
	movb	$10, %cl
	movq	%rbx, %rdx
	callq	*%rax
	nop
.Ltmp65:
	incq	%rax
	subq	%r14, %rsi
	movb	$0, -9(%rbp)
.Ltmp66:
	movq	-24(%rbp), %rcx
	movq	%rax, %rdx
	movq	%rsi, %r8
	callq	_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax
	nop
.Ltmp67:
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.LBB25_9:
	movb	$1, -9(%rbp)
.Ltmp68:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.48.llvm.16186315980599473920(%rip), %r9
	xorl	%ecx, %ecx
	movq	%rsi, %rdx
	movq	%rdi, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	nop
.Ltmp69:
.LBB25_10:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_@IMGREL
	.section	.text$unlikely,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_,unique,29
	.seh_endproc
	.def	"?dtor$11@?0?_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$11@?0?_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_@4HA":
.seh_proc "?dtor$11@?0?_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_@4HA"
.LBB25_11:
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
	leaq	64(%rdx), %rbp
	.seh_endprologue
	cmpb	$0, -9(%rbp)
	jne	.LBB25_12
.LBB25_13:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.LBB25_12:
	movq	-24(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5error9ErrorCodeEBF_
	jmp	.LBB25_13
.Lfunc_end25:
	.seh_handlerdata
	.section	.text$unlikely,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_,unique,29
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_,unique,10
	.p2align	2, 0x0
$cppxdata$_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_@IMGREL
	.long	56
	.long	0
	.long	1
$stateUnwindMap$_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_:
	.long	-1
	.long	"?dtor$11@?0?_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_@4HA"@IMGREL
$ip2state$_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_:
	.long	.Lfunc_begin25@IMGREL
	.long	-1
	.long	.Ltmp60@IMGREL
	.long	0
	.long	.Ltmp69@IMGREL
	.long	-1
	.section	.text$unlikely,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_,unique,29

	.def	_RNvMs3_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceRead14skip_to_escape;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceRead14skip_to_escape,unique,30
	.p2align	4
_RNvMs3_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceRead14skip_to_escape:
.Lfunc_begin26:
.seh_proc _RNvMs3_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceRead14skip_to_escape
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
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	8(%rcx), %rdx
	movq	16(%rcx), %rax
	cmpq	%rdx, %rax
	je	.LBB26_9
	jae	.LBB26_10
	movq	(%rcx), %r8
	movzbl	(%r8,%rax), %r9d
	cmpl	$34, %r9d
	je	.LBB26_9
	cmpl	$92, %r9d
	je	.LBB26_9
	cmpb	$32, %r9b
	jb	.LBB26_9
	leaq	1(%rax), %r9
	movq	%r9, 32(%rsp)
	subq	%r9, %rdx
	movabsq	$9223372036854775800, %r11
	andq	%rdx, %r11
	negq	%r11
	movl	$7, %r10d
	subq	%rax, %r10
	addq	%rax, %r8
	movl	$1, %eax
	movabsq	$-2314885530818453536, %rsi
	movabsq	$2459565876494606882, %rdi
	movabsq	$-72340172838076673, %rbx
	movabsq	$6655295901103053916, %r14
	movabsq	$-9187201950435737472, %r15
	.p2align	4
.LBB26_6:
	leaq	(%r11,%rax), %r12
	cmpq	$1, %r12
	je	.LBB26_11
	movq	(%r8,%rax), %r12
	movq	%r12, %r13
	notq	%r13
	leaq	(%r12,%rsi), %rbp
	movq	%r12, %r9
	xorq	%rdi, %r9
	addq	%rbx, %r9
	orq	%rbp, %r9
	xorq	%r14, %r12
	addq	%rbx, %r12
	orq	%r9, %r12
	andq	%r13, %r12
	addq	$8, %rax
	addq	$-8, %r10
	andq	%r15, %r12
	je	.LBB26_6
	rep		bsfq	%r12, %rax
	shrl	$3, %eax
	subq	%r10, %rax
	movq	%rax, 16(%rcx)
.LBB26_9:
	.seh_startepilogue
	addq	$40, %rsp
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
.LBB26_11:
	andq	$-8, %rdx
	addq	32(%rsp), %rdx
	movq	%rdx, 16(%rcx)
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r13
	popq	%r14
	popq	%r15
	.seh_endepilogue
	jmp	_RNvMs3_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceRead19skip_to_escape_slow
.LBB26_10:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.46(%rip), %r8
	movq	%rax, %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	ud2
.Lfunc_end26:
	.seh_endproc

	.def	_RNvMs3_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceRead19skip_to_escape_slow;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceRead19skip_to_escape_slow,unique,31
	.p2align	4
_RNvMs3_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceRead19skip_to_escape_slow:
.Lfunc_begin27:
	movq	8(%rcx), %rax
	movq	16(%rcx), %rdx
	cmpq	%rax, %rdx
	jae	.LBB27_6
	movq	(%rcx), %r8
	negq	%rax
	incq	%rdx
	.p2align	4
.LBB27_2:
	movzbl	-1(%r8,%rdx), %r9d
	cmpl	$34, %r9d
	je	.LBB27_6
	cmpl	$92, %r9d
	je	.LBB27_6
	cmpb	$32, %r9b
	jb	.LBB27_6
	movq	%rdx, 16(%rcx)
	leaq	(%rax,%rdx), %r9
	incq	%r9
	incq	%rdx
	cmpq	$1, %r9
	jne	.LBB27_2
.LBB27_6:
	retq
.Lfunc_end27:

	.def	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtNtCsavOST1yGCNT_10serde_json5value5ValueE8grow_oneBQ_;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtNtCsavOST1yGCNT_10serde_json5value5ValueE8grow_oneBQ_,unique,32
	.globl	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtNtCsavOST1yGCNT_10serde_json5value5ValueE8grow_oneBQ_
	.p2align	4
_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtNtCsavOST1yGCNT_10serde_json5value5ValueE8grow_oneBQ_:
.Lfunc_begin28:
.seh_proc _RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtNtCsavOST1yGCNT_10serde_json5value5ValueE8grow_oneBQ_
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
	movq	$32, 40(%rsp)
	movq	$8, 32(%rsp)
	leaq	48(%rsp), %rcx
	movq	%rdi, %r9
	callq	_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCsavOST1yGCNT_10serde_json
	cmpl	$1, 48(%rsp)
	je	.LBB28_1
	movq	56(%rsp), %rax
	movq	%rax, 8(%rsi)
	movq	%rdi, (%rsi)
	.seh_startepilogue
	addq	$72, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB28_1:
	movq	56(%rsp), %rcx
	movq	64(%rsp), %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.Lfunc_end28:
	.seh_endproc

	.def	_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCsavOST1yGCNT_10serde_json;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCsavOST1yGCNT_10serde_json,unique,33
	.p2align	4
_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCsavOST1yGCNT_10serde_json:
.Lfunc_begin29:
.seh_proc _RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCsavOST1yGCNT_10serde_json
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
	.seh_endprologue
	movq	%r9, %rax
	movq	%rdx, %r9
	movq	%rcx, %rsi
	movq	112(%rsp), %rbx
	mulq	120(%rsp)
	movq	%rax, %rdi
	seto	%al
	movabsq	$-9223372036854775808, %rcx
	subq	%rbx, %rcx
	cmpq	%rcx, %rdi
	seta	%cl
	orb	%al, %cl
	movl	$1, %r14d
	je	.LBB29_2
	movl	$8, %eax
	xorl	%edi, %edi
	jmp	.LBB29_10
.LBB29_2:
	testq	%r9, %r9
	je	.LBB29_4
	movq	%r8, %rcx
	movq	%rdi, %rdx
	movq	%rbx, %r8
	callq	mi_realloc_aligned
	testq	%rax, %rax
	jne	.LBB29_6
	jmp	.LBB29_9
.LBB29_4:
	testq	%rdi, %rdi
	je	.LBB29_5
	movq	%rdi, %rcx
	movq	%rbx, %rdx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	jne	.LBB29_6
.LBB29_9:
	movq	%rbx, 8(%rsi)
	movl	$16, %eax
	jmp	.LBB29_10
.LBB29_5:
	movq	%rbx, %rax
.LBB29_6:
	movq	%rax, 8(%rsi)
	movl	$16, %eax
	xorl	%r14d, %r14d
.LBB29_10:
	movq	%rdi, (%rsi,%rax)
	movq	%r14, (%rsi)
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.Lfunc_end29:
	.seh_endproc

	.def	_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_,unique,34
	.p2align	4
_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_:
.Lfunc_begin30:
.seh_proc _RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	32(%rsp), %rbp
	.seh_setframe %rbp, 32
	.seh_endprologue
	movq	$-2, (%rbp)
	movq	%rcx, %rsi
	movq	64(%rdx), %rax
	testq	%rax, %rax
	je	.LBB30_1
	decq	%rax
	movq	%rax, 64(%rdx)
	cmpl	$1, (%rdx)
	jne	.LBB30_49
	movq	8(%rdx), %rcx
	testq	%rcx, %rcx
	je	.LBB30_21
	movq	16(%rdx), %rdi
	movq	24(%rdx), %rbx
	movzwl	626(%rcx), %eax
	cmpq	%rax, %rbx
	jae	.LBB30_31
.LBB30_30:
	movq	%rcx, %r14
	testq	%rdi, %rdi
	je	.LBB30_36
.LBB30_39:
	leaq	(%r14,%rbx,8), %rax
	addq	$640, %rax
	movq	%rdi, %r8
	andq	$7, %r8
	je	.LBB30_40
	xorl	%r10d, %r10d
	.p2align	4
.LBB30_42:
	movq	(%rax), %rcx
	leaq	632(%rcx), %rax
	incq	%r10
	cmpq	%r10, %r8
	jne	.LBB30_42
	movq	%rdi, %r9
	subq	%r10, %r9
	xorl	%r8d, %r8d
	cmpq	$8, %rdi
	jae	.LBB30_45
	jmp	.LBB30_37
.LBB30_1:
	movq	(%rdx), %r9
	movq	8(%rdx), %rcx
	movq	16(%rdx), %rax
	movq	24(%rdx), %r8
	movq	$0, (%rdx)
	cmpq	$1, %r9
	jne	.LBB30_17
	testq	%rcx, %rcx
	je	.LBB30_3
.LBB30_13:
	movq	352(%rcx), %rax
	testq	%rax, %rax
	je	.LBB30_14
	.p2align	4
.LBB30_15:
	movq	%rax, %rdi
	callq	mi_free
	movq	352(%rdi), %rax
	movq	%rdi, %rcx
	testq	%rax, %rax
	jne	.LBB30_15
	jmp	.LBB30_16
.LBB30_21:
	movq	16(%rdx), %rcx
	movq	24(%rdx), %rax
	testq	%rax, %rax
	je	.LBB30_28
	movq	%rax, %r8
	andq	$7, %r8
	je	.LBB30_23
	xorl	%r9d, %r9d
	.p2align	4
.LBB30_25:
	movq	632(%rcx), %rcx
	incq	%r9
	cmpq	%r9, %r8
	jne	.LBB30_25
	movq	%rax, %r8
	subq	%r9, %r8
	cmpq	$8, %rax
	jb	.LBB30_28
	.p2align	4
.LBB30_50:
	movq	632(%rcx), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rcx
	addq	$-8, %r8
	jne	.LBB30_50
.LBB30_28:
	movq	$1, (%rdx)
	xorl	%ebx, %ebx
	xorl	%edi, %edi
	movzwl	626(%rcx), %eax
	cmpq	%rax, %rbx
	jb	.LBB30_30
.LBB30_31:
	movq	%rdx, %r15
	.p2align	4
.LBB30_32:
	movq	352(%rcx), %r14
	testq	%r14, %r14
	je	.LBB30_46
	incq	%rdi
	movzwl	624(%rcx), %ebx
	callq	mi_free
	movq	%r14, %rcx
	cmpw	626(%r14), %bx
	jae	.LBB30_32
	movq	%r15, %rdx
	testq	%rdi, %rdi
	jne	.LBB30_39
.LBB30_36:
	leaq	1(%rbx), %r8
	movq	%r14, %rcx
	jmp	.LBB30_37
.LBB30_40:
	movq	%rdi, %r9
	xorl	%r8d, %r8d
	cmpq	$8, %rdi
	jb	.LBB30_37
	.p2align	4
.LBB30_45:
	movq	(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rcx
	leaq	632(%rcx), %rax
	addq	$-8, %r9
	jne	.LBB30_45
.LBB30_37:
	movq	%rcx, 8(%rdx)
	movq	$0, 16(%rdx)
	movq	%r8, 24(%rdx)
	movq	%r14, (%rsi)
	movq	%rdi, 8(%rsi)
	movq	%rbx, 16(%rsi)
	jmp	.LBB30_38
.LBB30_3:
	testq	%r8, %r8
	je	.LBB30_4
	movq	%r8, %rcx
	andq	$7, %rcx
	je	.LBB30_6
	xorl	%r9d, %r9d
	.p2align	4
.LBB30_8:
	movq	632(%rax), %rax
	incq	%r9
	cmpq	%r9, %rcx
	jne	.LBB30_8
	movq	%r8, %rdx
	subq	%r9, %rdx
	jmp	.LBB30_10
.LBB30_14:
	movq	%rcx, %rdi
.LBB30_16:
	movq	%rdi, %rcx
	callq	mi_free
.LBB30_17:
	movq	$0, (%rsi)
.LBB30_38:
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
.LBB30_23:
	movq	%rax, %r8
	cmpq	$8, %rax
	jae	.LBB30_50
	jmp	.LBB30_28
.LBB30_4:
	movq	%rax, %rcx
	jmp	.LBB30_13
.LBB30_6:
	movq	%r8, %rdx
.LBB30_10:
	movq	%rax, %rcx
	cmpq	$8, %r8
	jb	.LBB30_13
	movq	%rax, %rcx
	.p2align	4
.LBB30_12:
	movq	632(%rcx), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rcx
	addq	$-8, %rdx
	jne	.LBB30_12
	jmp	.LBB30_13
.LBB30_46:
	callq	mi_free
	nop
.Ltmp70:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.36(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	nop
.Ltmp71:
	ud2
.LBB30_49:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.13(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_@IMGREL
	.section	.text,"xr",one_only,_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_,unique,34
	.seh_endproc
	.def	"?dtor$48@?0?_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$48@?0?_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_@4HA":
.seh_proc "?dtor$48@?0?_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_@4HA"
.LBB30_48:
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
	leaq	32(%rdx), %rbp
	.seh_endprologue
	ud2
.Lfunc_end30:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_,unique,34
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_,unique,11
	.p2align	2, 0x0
$cppxdata$_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_@IMGREL
	.long	32
	.long	0
	.long	1
$stateUnwindMap$_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_:
	.long	-1
	.long	"?dtor$48@?0?_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_@4HA"@IMGREL
$ip2state$_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_:
	.long	.Lfunc_begin30@IMGREL
	.long	-1
	.long	.Ltmp70@IMGREL
	.long	0
	.long	.Ltmp71@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_,unique,34

	.def	_RNvNtCsavOST1yGCNT_10serde_json5error10make_error;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNtCsavOST1yGCNT_10serde_json5error10make_error,unique,35
	.globl	_RNvNtCsavOST1yGCNT_10serde_json5error10make_error
	.p2align	4
_RNvNtCsavOST1yGCNT_10serde_json5error10make_error:
.Lfunc_begin31:
.seh_proc _RNvNtCsavOST1yGCNT_10serde_json5error10make_error
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
	subq	$200, %rsp
	.seh_stackalloc 200
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	movq	$-2, 64(%rbp)
	movq	8(%rcx), %rdx
	movq	%rcx, 32(%rbp)
	movq	16(%rcx), %rsi
	movb	$0, 63(%rbp)
.Ltmp72:
	movq	$9, 32(%rsp)
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.54(%rip), %r9
	leaq	-72(%rbp), %rcx
	movq	%rdx, 48(%rbp)
	movq	%rsi, %r8
	callq	_RNvMsu_NtNtCs8xEFJqa6dYS_4core3str7patternNtB5_11StrSearcher3new
	nop
.Ltmp73:
	cmpb	$0, -72(%rbp)
	je	.LBB31_17
	cmpq	$-1, -16(%rbp)
	movq	(%rbp), %rax
	movq	8(%rbp), %r8
	movq	16(%rbp), %r9
	movq	24(%rbp), %rdx
	je	.LBB31_21
	movq	-24(%rbp), %r14
	movq	%r14, %r11
	subq	%rdx, %r11
	cmpq	%r8, %r11
	jae	.LBB31_56
	movq	-40(%rbp), %r10
	movq	-56(%rbp), %rdi
	movq	-48(%rbp), %rcx
	movq	%rcx, 40(%rbp)
	movq	-8(%rbp), %r15
	jmp	.LBB31_5
.LBB31_17:
	cmpb	$0, -46(%rbp)
	jne	.LBB31_56
	movzbl	-47(%rbp), %eax
	movq	-56(%rbp), %r9
	testq	%r9, %r9
	je	.LBB31_40
	movq	(%rbp), %rcx
	movq	8(%rbp), %rdx
	cmpq	%rdx, %r9
	jae	.LBB31_41
	cmpb	$-64, (%rcx,%r9)
	movq	48(%rbp), %r15
	jge	.LBB31_42
	jmp	.LBB31_69
	.p2align	4
.LBB31_10:
	subq	%rdi, %r14
	leaq	(%r14,%r13), %r11
	incq	%r11
.LBB31_11:
	movq	%rdx, %r15
	movq	%r11, %r14
	subq	%rdx, %r11
	cmpq	%r8, %r11
	jae	.LBB31_56
.LBB31_5:
	movzbl	(%rax,%r11), %ecx
	btq	%rcx, %r10
	jae	.LBB31_11
	cmpq	%rdi, %r15
	movq	%rdi, %rcx
	cmovbq	%r15, %rcx
	decq	%rcx
	leaq	(%rax,%r11), %r12
	.p2align	4
.LBB31_7:
	cmpq	$-1, %rcx
	je	.LBB31_12
	cmpq	%rdx, %rcx
	jae	.LBB31_165
	movzbl	(%r9,%rcx), %ebx
	leaq	-1(%rcx), %r13
	cmpb	(%r12,%rcx), %bl
	movq	%r13, %rcx
	je	.LBB31_7
	jmp	.LBB31_10
	.p2align	4
.LBB31_12:
	movq	%rdi, %rcx
	.p2align	4
.LBB31_13:
	cmpq	%r15, %rcx
	jae	.LBB31_48
	cmpq	%rdx, %rcx
	jae	.LBB31_166
	movzbl	(%r9,%rcx), %r13d
	cmpb	(%r12,%rcx), %r13b
	leaq	1(%rcx), %rcx
	je	.LBB31_13
	movq	40(%rbp), %r15
	subq	%r15, %r14
	movq	%r14, %r11
	movq	%r11, %r14
	subq	%rdx, %r11
	cmpq	%r8, %r11
	jb	.LBB31_5
	jmp	.LBB31_56
.LBB31_21:
	movq	-24(%rbp), %rdi
	movq	%rdi, %r11
	subq	%rdx, %r11
	cmpq	%r8, %r11
	jae	.LBB31_56
	movq	-40(%rbp), %r10
	movq	-56(%rbp), %rcx
	movq	-48(%rbp), %rbx
	movq	%rbx, 40(%rbp)
	leaq	-1(%rcx), %rbx
	movq	%rbx, -80(%rbp)
	cmpq	%rdx, %rbx
	jb	.LBB31_32
	testq	%rcx, %rcx
	je	.LBB31_51
	movzbl	(%rax,%r11), %ecx
	btq	%rcx, %r10
	jb	.LBB31_28
	subq	%rdx, %rdi
	subq	%rdx, %rdi
	.p2align	4
.LBB31_26:
	cmpq	%r8, %rdi
	jae	.LBB31_56
	movzbl	(%rax,%rdi), %ecx
	subq	%rdx, %rdi
	btq	%rcx, %r10
	jae	.LBB31_26
.LBB31_28:
	movb	$0, 63(%rbp)
.Ltmp80:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.17(%rip), %r8
	movq	-80(%rbp), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	nop
.Ltmp81:
	jmp	.LBB31_169
.LBB31_30:
	movq	%r11, %r15
.LBB31_31:
	movq	%r15, %r11
	subq	%rdx, %r11
	movq	%r15, %rdi
	cmpq	%r8, %r11
	jae	.LBB31_56
.LBB31_32:
	movzbl	(%rax,%r11), %r14d
	btq	%r14, %r10
	jae	.LBB31_30
	leaq	-1(%rcx), %rbx
	leaq	(%rbx,%r11), %r12
	movq	%rdi, %r15
	movq	%rcx, %r14
	movq	%rcx, %r13
	.p2align	4
.LBB31_34:
	subq	$1, %r13
	jb	.LBB31_36
	movzbl	-1(%r9,%r14), %ebx
	decq	%r15
	movq	%r13, %r14
	cmpb	(%rax,%r12), %bl
	leaq	-1(%r12), %r12
	je	.LBB31_34
	jmp	.LBB31_31
.LBB31_36:
	leaq	(%rax,%r11), %r14
	movq	%rcx, %r15
	.p2align	4
.LBB31_37:
	cmpq	%r15, %rdx
	je	.LBB31_48
	movzbl	(%r9,%r15), %r12d
	cmpb	(%r14,%r15), %r12b
	leaq	1(%r15), %r15
	je	.LBB31_37
	subq	40(%rbp), %rdi
	movq	%rdi, %r15
	jmp	.LBB31_31
.LBB31_40:
	xorl	%r11d, %r11d
	testb	$1, %al
	movq	48(%rbp), %r15
	jne	.LBB31_74
	jmp	.LBB31_89
.LBB31_41:
	movq	48(%rbp), %r15
	jne	.LBB31_69
.LBB31_42:
	movzbl	-1(%rcx,%r9), %r8d
	movzbl	%r8b, %r8d
	testb	%r8b, %r8b
	js	.LBB31_45
	testb	$1, %al
	je	.LBB31_62
.LBB31_44:
	movq	%r9, %r11
	jmp	.LBB31_74
.LBB31_45:
	movzbl	-2(%rcx,%r9), %r10d
	cmpb	$-65, %r10b
	jg	.LBB31_49
	movzbl	-3(%rcx,%r9), %r11d
	cmpb	$-65, %r11b
	jg	.LBB31_59
	movzbl	-4(%rcx,%r9), %edi
	andl	$7, %edi
	shll	$6, %edi
	andl	$63, %r11d
	orl	%edi, %r11d
	jmp	.LBB31_60
.LBB31_49:
	andl	$31, %r10d
	jmp	.LBB31_61
.LBB31_50:
	movq	%r11, %rdi
	subq	%rdx, %r11
	cmpq	%r8, %r11
	jae	.LBB31_56
.LBB31_51:
	movzbl	(%rax,%r11), %ecx
	btq	%rcx, %r10
	jae	.LBB31_50
	leaq	(%rax,%r11), %rcx
	xorl	%ebx, %ebx
	.p2align	4
.LBB31_53:
	cmpq	%rbx, %rdx
	je	.LBB31_48
	movzbl	(%r9,%rbx), %r14d
	cmpb	(%rcx,%rbx), %r14b
	leaq	1(%rbx), %rbx
	je	.LBB31_53
	subq	40(%rbp), %rdi
	movq	%rdi, %r11
	subq	%rdx, %r11
	cmpq	%r8, %r11
	jb	.LBB31_51
.LBB31_56:
	xorl	%edi, %edi
	xorl	%ebx, %ebx
.LBB31_57:
	movq	48(%rbp), %r15
	jmp	.LBB31_91
.LBB31_48:
	movq	48(%rbp), %r15
.LBB31_74:
	leaq	9(%r11), %rax
	movq	%rax, %r8
	testq	%r8, %r8
	je	.LBB31_78
	.p2align	4
.LBB31_75:
	cmpq	%rsi, %r8
	jae	.LBB31_77
	cmpb	$-64, (%r15,%r8)
	jge	.LBB31_78
	jmp	.LBB31_167
	.p2align	4
.LBB31_77:
	jne	.LBB31_167
.LBB31_78:
	cmpq	%r8, %rsi
	je	.LBB31_81
	movzbl	(%r15,%r8), %ecx
	addb	$-48, %cl
	cmpb	$10, %cl
	jae	.LBB31_82
	incq	%r8
	testq	%r8, %r8
	jne	.LBB31_75
	jmp	.LBB31_78
.LBB31_81:
	movq	%rsi, %r9
	testq	%r8, %r8
	jne	.LBB31_83
	jmp	.LBB31_87
.LBB31_82:
	movq	%r8, %r9
	testq	%r8, %r8
	je	.LBB31_87
.LBB31_83:
	cmpq	%r9, %rsi
	jbe	.LBB31_86
	cmpb	$-65, (%r15,%r9)
	jg	.LBB31_87
.LBB31_85:
	movb	$0, 63(%rbp)
.Ltmp84:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.57(%rip), %rax
	movq	%rax, 32(%rsp)
	movq	%r15, %rcx
	movq	%rsi, %rdx
	movq	%r9, %r8
	movq	%rsi, %r9
	callq	_RNvNtCs8xEFJqa6dYS_4core3str16slice_error_fail
	nop
.Ltmp85:
	jmp	.LBB31_169
.LBB31_86:
	jne	.LBB31_85
.LBB31_87:
	movq	%rsi, %rcx
	subq	%r9, %rcx
	cmpq	$8, %rcx
	jb	.LBB31_89
	movabsq	$2336925607749706528, %rcx
	cmpq	%rcx, (%r15,%r9)
	je	.LBB31_98
.LBB31_89:
	xorl	%edi, %edi
.LBB31_90:
	xorl	%ebx, %ebx
.LBB31_91:
	movq	%r15, %rax
	movq	32(%rbp), %rcx
	cmpq	%rsi, (%rcx)
	jbe	.LBB31_96
	testq	%rsi, %rsi
	je	.LBB31_95
	movl	$1, %r8d
	movq	%r15, %rcx
	movq	%rsi, %rdx
	callq	mi_realloc_aligned
	testq	%rax, %rax
	jne	.LBB31_96
.Ltmp94:
	movl	$1, %ecx
	movq	%rsi, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp95:
	jmp	.LBB31_169
.LBB31_95:
	movq	%r15, %rcx
	callq	mi_free
	movl	$1, %eax
.LBB31_96:
	movq	$0, -72(%rbp)
	movq	%rax, -64(%rbp)
	movq	%rsi, -56(%rbp)
	movq	%rdi, -48(%rbp)
	movq	%rbx, -40(%rbp)
	movl	$40, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB31_162
	movq	-40(%rbp), %rcx
	movq	%rcx, 32(%rax)
	movups	-72(%rbp), %xmm0
	movups	-56(%rbp), %xmm1
	movups	%xmm1, 16(%rax)
	movups	%xmm0, (%rax)
	.seh_startepilogue
	addq	$200, %rsp
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
.LBB31_98:
	leaq	8(%r9), %r8
	movq	%r8, %r10
	testq	%r10, %r10
	je	.LBB31_102
	.p2align	4
.LBB31_99:
	cmpq	%rsi, %r10
	jae	.LBB31_101
	cmpb	$-64, (%r15,%r10)
	jge	.LBB31_102
	jmp	.LBB31_168
	.p2align	4
.LBB31_101:
	jne	.LBB31_168
.LBB31_102:
	cmpq	%r10, %rsi
	je	.LBB31_105
	movzbl	(%r15,%r10), %ecx
	addb	$-48, %cl
	cmpb	$10, %cl
	jae	.LBB31_106
	incq	%r10
	testq	%r10, %r10
	jne	.LBB31_99
	jmp	.LBB31_102
.LBB31_105:
	movq	%rsi, %r10
	jmp	.LBB31_107
.LBB31_106:
	cmpq	%rsi, %r10
	jb	.LBB31_89
.LBB31_107:
	movq	%r9, %rbx
	subq	%rax, %rbx
	jb	.LBB31_164
	testq	%rax, %rax
	je	.LBB31_110
	cmpb	$-64, (%r15,%rax)
	jl	.LBB31_164
.LBB31_110:
	cmpb	$-65, (%r15,%r9)
	jle	.LBB31_164
	cmpq	$1, %rbx
	je	.LBB31_114
	testq	%rbx, %rbx
	jne	.LBB31_117
	movq	%rbx, %rdi
	jmp	.LBB31_91
.LBB31_114:
	movzbl	(%r15,%rax), %ecx
	xorl	%edi, %edi
	cmpl	$43, %ecx
	je	.LBB31_90
	cmpl	$45, %ecx
	je	.LBB31_90
	jmp	.LBB31_118
.LBB31_117:
	movzbl	(%r15,%rax), %ecx
.LBB31_118:
	xorl	%eax, %eax
	cmpb	$43, %cl
	sete	%al
	movq	%rax, %rcx
	negq	%rcx
	subq	%rax, %rbx
	cmpq	$17, %rbx
	jae	.LBB31_123
	testq	%rbx, %rbx
	je	.LBB31_130
	addq	%r15, %rax
	addq	$9, %rax
	addq	%r9, %rcx
	addq	$-9, %rcx
	xorl	%ebx, %ebx
	movq	%r11, %rdx
	xorl	%edi, %edi
.LBB31_121:
	movzbl	(%rax,%rdx), %r14d
	addl	$-48, %r14d
	cmpl	$9, %r14d
	ja	.LBB31_139
	leaq	(%rdi,%rdi,4), %rdi
	movl	%r14d, %r14d
	leaq	(%r14,%rdi,2), %rdi
	incq	%rdx
	cmpq	%rdx, %rcx
	jne	.LBB31_121
	jmp	.LBB31_131
.LBB31_59:
	andl	$15, %r11d
.LBB31_60:
	shll	$6, %r11d
	andl	$63, %r10d
	orl	%r11d, %r10d
.LBB31_61:
	shll	$6, %r10d
	andl	$63, %r8d
	orl	%r10d, %r8d
	testb	$1, %al
	jne	.LBB31_44
.LBB31_62:
	movq	$-1, %r11
	cmpl	$128, %r8d
	jb	.LBB31_65
	movq	$-2, %r11
	cmpl	$2048, %r8d
	jb	.LBB31_65
	xorl	%r11d, %r11d
	cmpl	$65536, %r8d
	setb	%r11b
	orq	$-4, %r11
.LBB31_65:
	addq	%r9, %r11
	je	.LBB31_70
	cmpq	%rdx, %r11
	jae	.LBB31_71
	cmpb	$-64, (%rcx,%r11)
	jge	.LBB31_72
.LBB31_68:
	movq	%r11, %r9
.LBB31_69:
	movb	$0, 63(%rbp)
.Ltmp74:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.134(%rip), %rax
	movq	%rax, 32(%rsp)
	xorl	%r8d, %r8d
	callq	_RNvNtCs8xEFJqa6dYS_4core3str16slice_error_fail
	nop
.Ltmp75:
	jmp	.LBB31_169
.LBB31_70:
	xorl	%r11d, %r11d
	jmp	.LBB31_74
.LBB31_71:
	jne	.LBB31_68
.LBB31_72:
	cmpb	$0, -1(%rcx,%r11)
	jns	.LBB31_74
	cmpb	$-65, -2(%rcx,%r11)
	jmp	.LBB31_74
.LBB31_123:
	addq	%r9, %rcx
	addq	$-9, %rcx
	leaq	(%rax,%r15), %r14
	addq	$9, %r14
	xorl	%ebx, %ebx
	movl	$10, %r15d
	movq	%r11, %r12
	xorl	%edi, %edi
.LBB31_124:
	cmpq	%r12, %rcx
	je	.LBB31_160
	movq	%rdi, %rax
	mulq	%r15
	jo	.LBB31_128
	movq	%rax, %rdi
	movzbl	(%r14,%r12), %edx
	addl	$-48, %edx
	addq	%rdx, %rdi
	setb	%al
	cmpl	$9, %edx
	ja	.LBB31_128
	incq	%r12
	testb	%al, %al
	je	.LBB31_124
.LBB31_128:
	xorl	%edi, %edi
	jmp	.LBB31_57
.LBB31_130:
	xorl	%edi, %edi
.LBB31_131:
	movq	%r10, %rax
	subq	%r8, %rax
	jb	.LBB31_161
.LBB31_132:
	cmpq	%rsi, %r10
	ja	.LBB31_161
	cmpq	%rsi, %r8
	je	.LBB31_136
	testq	%r8, %r8
	je	.LBB31_136
	cmpb	$-65, (%r15,%r8)
	jle	.LBB31_161
.LBB31_136:
	cmpq	$1, %rax
	je	.LBB31_140
	testq	%rax, %rax
	jne	.LBB31_143
	movq	%rax, %rdi
	movq	%rax, %rbx
	jmp	.LBB31_91
.LBB31_140:
	movzbl	(%r15,%r8), %ecx
	xorl	%ebx, %ebx
	cmpl	$43, %ecx
	je	.LBB31_139
	cmpl	$45, %ecx
	jne	.LBB31_144
.LBB31_139:
	xorl	%edi, %edi
	jmp	.LBB31_91
.LBB31_143:
	movzbl	(%r15,%r8), %ecx
.LBB31_144:
	xorl	%edx, %edx
	cmpb	$43, %cl
	sete	%dl
	movq	%rdx, %rcx
	negq	%rcx
	subq	%rdx, %rax
	cmpq	$17, %rax
	jae	.LBB31_149
	testq	%rax, %rax
	je	.LBB31_155
	leaq	(%rdx,%r15), %rax
	addq	$8, %rax
	addq	%r10, %rcx
	addq	$-8, %rcx
	xorl	%ebx, %ebx
.LBB31_147:
	movzbl	(%rax,%r9), %edx
	addl	$-48, %edx
	cmpl	$9, %edx
	ja	.LBB31_89
	leaq	(%rbx,%rbx,4), %r8
	movl	%edx, %edx
	leaq	(%rdx,%r8,2), %rbx
	incq	%r9
	cmpq	%r9, %rcx
	jne	.LBB31_147
	jmp	.LBB31_156
.LBB31_149:
	addq	%r10, %rcx
	addq	$-8, %rcx
	leaq	(%rdx,%r15), %r8
	addq	$8, %r8
	movl	$10, %r10d
	xorl	%ebx, %ebx
.LBB31_150:
	cmpq	%r9, %rcx
	je	.LBB31_156
	movq	%rbx, %rax
	mulq	%r10
	jo	.LBB31_89
	movq	%rax, %rbx
	movzbl	(%r8,%r9), %edx
	addl	$-48, %edx
	addq	%rdx, %rbx
	setb	%al
	cmpl	$9, %edx
	ja	.LBB31_89
	incq	%r9
	testb	%al, %al
	je	.LBB31_150
	jmp	.LBB31_89
.LBB31_155:
	xorl	%ebx, %ebx
.LBB31_156:
	cmpq	%rsi, %r11
	ja	.LBB31_91
	testq	%r11, %r11
	setne	%al
	cmpq	%rsi, %r11
	setb	%cl
	andb	%al, %cl
	cmpb	$1, %cl
	jne	.LBB31_163
	cmpb	$-65, (%r15,%r11)
	movq	%r11, %rsi
	jg	.LBB31_91
	movb	$0, 63(%rbp)
.Ltmp88:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.45(%rip), %rcx
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.62(%rip), %r8
	movl	$48, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking5panic
	nop
.Ltmp89:
	jmp	.LBB31_169
.LBB31_160:
	movq	48(%rbp), %r15
	movq	%r10, %rax
	subq	%r8, %rax
	jae	.LBB31_132
.LBB31_161:
	movb	$0, 63(%rbp)
.Ltmp90:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.61(%rip), %rax
	movq	%rax, 32(%rsp)
	movq	%r15, %rcx
	movq	%rsi, %rdx
	movq	%r10, %r9
	callq	_RNvNtCs8xEFJqa6dYS_4core3str16slice_error_fail
	nop
.Ltmp91:
	jmp	.LBB31_169
.LBB31_162:
.Ltmp96:
	movl	$8, %ecx
	movl	$40, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp97:
	jmp	.LBB31_169
.LBB31_163:
	movq	%r11, %rsi
	jmp	.LBB31_91
.LBB31_164:
	movb	$0, 63(%rbp)
.Ltmp92:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.60(%rip), %rcx
	movq	%rcx, 32(%rsp)
	movq	%r15, %rcx
	movq	%rsi, %rdx
	movq	%rax, %r8
	callq	_RNvNtCs8xEFJqa6dYS_4core3str16slice_error_fail
	nop
.Ltmp93:
	jmp	.LBB31_169
.LBB31_165:
	movb	$0, 63(%rbp)
.Ltmp76:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.17(%rip), %r8
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	nop
.Ltmp77:
	jmp	.LBB31_169
.LBB31_166:
	movb	$0, 63(%rbp)
.Ltmp78:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.16(%rip), %r8
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	nop
.Ltmp79:
	jmp	.LBB31_169
.LBB31_167:
	movb	$0, 63(%rbp)
.Ltmp82:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.56(%rip), %rax
	movq	%rax, 32(%rsp)
	movq	%r15, %rcx
	movq	%rsi, %rdx
	movq	%rsi, %r9
	callq	_RNvNtCs8xEFJqa6dYS_4core3str16slice_error_fail
	nop
.Ltmp83:
	jmp	.LBB31_169
.LBB31_168:
	movb	$0, 63(%rbp)
.Ltmp86:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.59(%rip), %rax
	movq	%rax, 32(%rsp)
	movq	%r15, %rcx
	movq	%rsi, %rdx
	movq	%r10, %r8
	movq	%rsi, %r9
	callq	_RNvNtCs8xEFJqa6dYS_4core3str16slice_error_fail
	nop
.Ltmp87:
.LBB31_169:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvNtCsavOST1yGCNT_10serde_json5error10make_error@IMGREL
	.section	.text,"xr",one_only,_RNvNtCsavOST1yGCNT_10serde_json5error10make_error,unique,35
	.seh_endproc
	.def	"?dtor$170@?0?_RNvNtCsavOST1yGCNT_10serde_json5error10make_error@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$170@?0?_RNvNtCsavOST1yGCNT_10serde_json5error10make_error@4HA":
.seh_proc "?dtor$170@?0?_RNvNtCsavOST1yGCNT_10serde_json5error10make_error@4HA"
.LBB31_170:
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movq	48(%rbp), %rcx
	callq	mi_free
	movb	$1, 63(%rbp)
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvNtCsavOST1yGCNT_10serde_json5error10make_error,unique,35
	.seh_endproc
	.def	"?dtor$171@?0?_RNvNtCsavOST1yGCNT_10serde_json5error10make_error@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$171@?0?_RNvNtCsavOST1yGCNT_10serde_json5error10make_error@4HA":
.seh_proc "?dtor$171@?0?_RNvNtCsavOST1yGCNT_10serde_json5error10make_error@4HA"
.LBB31_171:
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movb	$1, 63(%rbp)
	leaq	-72(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5error9ErrorImplEBF_.llvm.16186315980599473920
	movb	$1, 63(%rbp)
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvNtCsavOST1yGCNT_10serde_json5error10make_error,unique,35
	.seh_endproc
	.def	"?dtor$172@?0?_RNvNtCsavOST1yGCNT_10serde_json5error10make_error@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$172@?0?_RNvNtCsavOST1yGCNT_10serde_json5error10make_error@4HA":
.seh_proc "?dtor$172@?0?_RNvNtCsavOST1yGCNT_10serde_json5error10make_error@4HA"
.LBB31_172:
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpb	$0, 63(%rbp)
	jne	.LBB31_175
	movq	32(%rbp), %rax
	cmpq	$0, (%rax)
	je	.LBB31_175
	movq	48(%rbp), %rcx
	callq	mi_free
	nop
.LBB31_175:
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
.Lfunc_end31:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvNtCsavOST1yGCNT_10serde_json5error10make_error,unique,35
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvNtCsavOST1yGCNT_10serde_json5error10make_error,unique,12
	.p2align	2, 0x0
$cppxdata$_RNvNtCsavOST1yGCNT_10serde_json5error10make_error:
	.long	429065506
	.long	3
	.long	$stateUnwindMap$_RNvNtCsavOST1yGCNT_10serde_json5error10make_error@IMGREL
	.long	0
	.long	0
	.long	7
	.long	$ip2state$_RNvNtCsavOST1yGCNT_10serde_json5error10make_error@IMGREL
	.long	192
	.long	0
	.long	1
$stateUnwindMap$_RNvNtCsavOST1yGCNT_10serde_json5error10make_error:
	.long	-1
	.long	"?dtor$172@?0?_RNvNtCsavOST1yGCNT_10serde_json5error10make_error@4HA"@IMGREL
	.long	0
	.long	"?dtor$171@?0?_RNvNtCsavOST1yGCNT_10serde_json5error10make_error@4HA"@IMGREL
	.long	0
	.long	"?dtor$170@?0?_RNvNtCsavOST1yGCNT_10serde_json5error10make_error@4HA"@IMGREL
$ip2state$_RNvNtCsavOST1yGCNT_10serde_json5error10make_error:
	.long	.Lfunc_begin31@IMGREL
	.long	-1
	.long	.Ltmp72@IMGREL
	.long	0
	.long	.Ltmp94@IMGREL
	.long	2
	.long	.Ltmp74@IMGREL
	.long	0
	.long	.Ltmp96@IMGREL
	.long	1
	.long	.Ltmp92@IMGREL
	.long	0
	.long	.Ltmp87@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvNtCsavOST1yGCNT_10serde_json5error10make_error,unique,35

	.def	_RNvXs1_NtCsavOST1yGCNT_10serde_json3serQINtB5_10SerializerQNtNvXs_NtB7_5valueNtB12_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterENtNtCslmkRZor3pUd_10serde_core3ser10Serializer13serialize_strB7_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1_NtCsavOST1yGCNT_10serde_json3serQINtB5_10SerializerQNtNvXs_NtB7_5valueNtB12_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterENtNtCslmkRZor3pUd_10serde_core3ser10Serializer13serialize_strB7_,unique,36
	.p2align	4
_RNvXs1_NtCsavOST1yGCNT_10serde_json3serQINtB5_10SerializerQNtNvXs_NtB7_5valueNtB12_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterENtNtCslmkRZor3pUd_10serde_core3ser10Serializer13serialize_strB7_:
.Lfunc_begin32:
.seh_proc _RNvXs1_NtCsavOST1yGCNT_10serde_json3serQINtB5_10SerializerQNtNvXs_NtB7_5valueNtB12_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterENtNtCslmkRZor3pUd_10serde_core3ser10Serializer13serialize_strB7_
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
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movq	%r8, %rsi
	movq	%rdx, %rbx
	movq	%rcx, 48(%rsp)
	movq	(%rcx), %rdi
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.30(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB32_8
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %r14
	leaq	.LJTI32_0(%rip), %r12
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.30(%rip), %r15
	movl	$255, %ebp
	jmp	.LBB32_2
	.p2align	4
.LBB32_62:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB32_63
.LBB32_7:
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	movl	$1, %r8d
	movq	%r15, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB32_8
.LBB32_2:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%r14, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r12,%rcx,4), %rcx
	addq	%r12, %rcx
	jmpq	*%rcx
.LBB32_4:
	cmpb	$35, 16(%rax)
	je	.LBB32_7
	jmp	.LBB32_63
	.p2align	4
.LBB32_3:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%ebp, %ecx
	cmpb	$35, %cl
	je	.LBB32_7
	jmp	.LBB32_63
	.p2align	4
.LBB32_5:
	cmpb	$35, 31(%rax)
	jne	.LBB32_63
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB32_7
.LBB32_8:
	leaq	_RNvNtCsavOST1yGCNT_10serde_json3ser6ESCAPE(%rip), %rbp
.LBB32_9:
	xorl	%r14d, %r14d
	.p2align	4
.LBB32_10:
	cmpq	%r14, %rsi
	je	.LBB32_11
	movq	%r14, %r13
	movzbl	(%rbx,%r14), %r12d
	movzbl	(%r12,%rbp), %edi
	incq	%r14
	testb	%dil, %dil
	je	.LBB32_10
	cmpq	$1, %r14
	je	.LBB32_34
	movq	48(%rsp), %rax
	movq	(%rax), %r15
	movq	(%r15), %rcx
	movq	8(%r15), %rax
	movq	%rbx, %rdx
	movq	%r13, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB32_34
	movq	%rbx, 64(%rsp)
	jmp	.LBB32_27
	.p2align	4
.LBB32_28:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rsi, %rbx
	movq	%rbp, %rsi
	movq	%rax, %rbp
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%rbp, %rax
	movq	%rsi, %rbp
	movq	%rbx, %rsi
	movq	64(%rsp), %rbx
	testb	%cl, %cl
	je	.LBB32_63
.LBB32_33:
	movq	(%r15), %rcx
	movq	8(%r15), %rax
	movq	%rbx, %rdx
	movq	%r13, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB32_34
.LBB32_27:
	movl	$9, %r8d
	movb	$41, %cl
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	leaq	.LJTI32_1(%rip), %rdx
	movslq	(%rdx,%rcx,4), %rcx
	addq	%rdx, %rcx
	jmpq	*%rcx
.LBB32_30:
	cmpb	$35, 16(%rax)
	je	.LBB32_33
	jmp	.LBB32_63
	.p2align	4
.LBB32_29:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	movl	$255, %edx
	cmovael	%edx, %ecx
	cmpb	$35, %cl
	je	.LBB32_33
	jmp	.LBB32_63
	.p2align	4
.LBB32_31:
	cmpb	$35, 31(%rax)
	jne	.LBB32_63
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB32_33
	.p2align	4
.LBB32_34:
	cmpb	$117, %dil
	jne	.LBB32_43
	movl	%r12d, %eax
	andl	$15, %eax
	shrl	$4, %r12d
	leaq	_RNvNvNtNtCsavOST1yGCNT_10serde_json3ser9Formatter17write_char_escape10HEX_DIGITS(%rip), %rdx
	movzbl	(%r12,%rdx), %ecx
	movzbl	(%rax,%rdx), %eax
	movl	$808482140, 56(%rsp)
	movb	%cl, 60(%rsp)
	movb	%al, 61(%rsp)
	movq	48(%rsp), %rax
	movq	(%rax), %rdi
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	movl	$6, %r8d
	leaq	56(%rsp), %r12
	movq	%r12, %rdx
	callq	*24(%rax)
	testb	%al, %al
	leaq	.LJTI32_3(%rip), %r13
	jne	.LBB32_36
	jmp	.LBB32_52
	.p2align	4
.LBB32_37:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r15
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r15, %rax
	testb	%cl, %cl
	je	.LBB32_53
.LBB32_42:
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	movl	$6, %r8d
	movq	%r12, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB32_52
.LBB32_36:
	movl	$9, %r8d
	movb	$41, %cl
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r13,%rcx,4), %rcx
	addq	%r13, %rcx
	jmpq	*%rcx
.LBB32_39:
	cmpb	$35, 16(%rax)
	je	.LBB32_42
	jmp	.LBB32_53
	.p2align	4
.LBB32_38:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	movl	$255, %edx
	cmovael	%edx, %ecx
	cmpb	$35, %cl
	je	.LBB32_42
	jmp	.LBB32_53
	.p2align	4
.LBB32_40:
	cmpb	$35, 31(%rax)
	jne	.LBB32_53
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB32_42
	.p2align	4
.LBB32_43:
	movb	$92, 46(%rsp)
	movb	%dil, 47(%rsp)
	movq	48(%rsp), %rax
	movq	(%rax), %rdi
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	movl	$2, %r8d
	leaq	46(%rsp), %r12
	movq	%r12, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB32_52
	leaq	.LJTI32_2(%rip), %r13
	jmp	.LBB32_45
	.p2align	4
.LBB32_46:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r15
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r15, %rax
	testb	%cl, %cl
	je	.LBB32_53
.LBB32_51:
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	movl	$2, %r8d
	movq	%r12, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB32_52
.LBB32_45:
	movl	$9, %r8d
	movb	$41, %cl
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r13,%rcx,4), %rcx
	addq	%r13, %rcx
	jmpq	*%rcx
.LBB32_48:
	cmpb	$35, 16(%rax)
	je	.LBB32_51
	jmp	.LBB32_53
	.p2align	4
.LBB32_47:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	movl	$255, %edx
	cmovael	%edx, %ecx
	cmpb	$35, %cl
	je	.LBB32_51
	jmp	.LBB32_53
	.p2align	4
.LBB32_49:
	cmpb	$35, 31(%rax)
	jne	.LBB32_53
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB32_51
	.p2align	4
.LBB32_52:
	xorl	%eax, %eax
.LBB32_53:
	addq	%r14, %rbx
	subq	%r14, %rsi
	testq	%rax, %rax
	je	.LBB32_9
.LBB32_63:
	movq	%rax, %rcx
	callq	_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io
	movq	%rax, %rsi
	jmp	.LBB32_64
.LBB32_11:
	testq	%rsi, %rsi
	je	.LBB32_21
	movq	48(%rsp), %rax
	movq	(%rax), %rdi
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	movq	%rbx, %rdx
	movq	%rsi, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB32_21
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %r14
	leaq	.LJTI32_4(%rip), %r15
	movl	$255, %ebp
	jmp	.LBB32_14
	.p2align	4
.LBB32_15:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r12
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r12, %rax
	testb	%cl, %cl
	je	.LBB32_63
.LBB32_20:
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	movq	%rbx, %rdx
	movq	%rsi, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB32_21
.LBB32_14:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%r14, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB32_17:
	cmpb	$35, 16(%rax)
	je	.LBB32_20
	jmp	.LBB32_63
	.p2align	4
.LBB32_16:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%ebp, %ecx
	cmpb	$35, %cl
	je	.LBB32_20
	jmp	.LBB32_63
	.p2align	4
.LBB32_18:
	cmpb	$35, 31(%rax)
	jne	.LBB32_63
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB32_20
.LBB32_21:
	movq	48(%rsp), %rax
	movq	(%rax), %r14
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.30(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB32_22
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdi
	leaq	.LJTI32_5(%rip), %r15
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.30(%rip), %rbx
	xorl	%esi, %esi
	movl	$255, %ebp
	jmp	.LBB32_55
	.p2align	4
.LBB32_56:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r12
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r12, %rax
	testb	%cl, %cl
	je	.LBB32_63
.LBB32_61:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movl	$1, %r8d
	movq	%rbx, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB32_64
.LBB32_55:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rdi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB32_58:
	cmpb	$35, 16(%rax)
	je	.LBB32_61
	jmp	.LBB32_63
	.p2align	4
.LBB32_57:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%ebp, %ecx
	cmpb	$35, %cl
	je	.LBB32_61
	jmp	.LBB32_63
	.p2align	4
.LBB32_59:
	cmpb	$35, 31(%rax)
	jne	.LBB32_63
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB32_61
.LBB32_22:
	xorl	%esi, %esi
.LBB32_64:
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$72, %rsp
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
.Lfunc_end32:
	.section	.rdata,"dr",associative,_RNvXs1_NtCsavOST1yGCNT_10serde_json3serQINtB5_10SerializerQNtNvXs_NtB7_5valueNtB12_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterENtNtCslmkRZor3pUd_10serde_core3ser10Serializer13serialize_strB7_,unique,37
	.p2align	2, 0x0
.LJTI32_0:
	.long	.LBB32_4-.LJTI32_0
	.long	.LBB32_5-.LJTI32_0
	.long	.LBB32_62-.LJTI32_0
	.long	.LBB32_3-.LJTI32_0
.LJTI32_1:
	.long	.LBB32_30-.LJTI32_1
	.long	.LBB32_31-.LJTI32_1
	.long	.LBB32_28-.LJTI32_1
	.long	.LBB32_29-.LJTI32_1
.LJTI32_2:
	.long	.LBB32_48-.LJTI32_2
	.long	.LBB32_49-.LJTI32_2
	.long	.LBB32_46-.LJTI32_2
	.long	.LBB32_47-.LJTI32_2
.LJTI32_3:
	.long	.LBB32_39-.LJTI32_3
	.long	.LBB32_40-.LJTI32_3
	.long	.LBB32_37-.LJTI32_3
	.long	.LBB32_38-.LJTI32_3
.LJTI32_4:
	.long	.LBB32_17-.LJTI32_4
	.long	.LBB32_18-.LJTI32_4
	.long	.LBB32_15-.LJTI32_4
	.long	.LBB32_16-.LJTI32_4
.LJTI32_5:
	.long	.LBB32_58-.LJTI32_5
	.long	.LBB32_59-.LJTI32_5
	.long	.LBB32_56-.LJTI32_5
	.long	.LBB32_57-.LJTI32_5
	.section	.text,"xr",one_only,_RNvXs1_NtCsavOST1yGCNT_10serde_json3serQINtB5_10SerializerQNtNvXs_NtB7_5valueNtB12_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterENtNtCslmkRZor3pUd_10serde_core3ser10Serializer13serialize_strB7_,unique,36
	.seh_endproc

	.def	_RNvXs1_NtCsavOST1yGCNT_10serde_json5errorNtB5_9ErrorCodeNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1_NtCsavOST1yGCNT_10serde_json5errorNtB5_9ErrorCodeNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt,unique,38
	.globl	_RNvXs1_NtCsavOST1yGCNT_10serde_json5errorNtB5_9ErrorCodeNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt
	.p2align	4
_RNvXs1_NtCsavOST1yGCNT_10serde_json5errorNtB5_9ErrorCodeNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt:
.Lfunc_begin33:
	movq	(%rcx), %rax
	leaq	.LJTI33_0(%rip), %r8
	movslq	(%r8,%rax,4), %rax
	addq	%r8, %rax
	jmpq	*%rax
.LBB33_1:
	movq	8(%rcx), %rax
	movq	16(%rcx), %r8
	movq	(%rdx), %rcx
	movq	8(%rdx), %rdx
	movq	24(%rdx), %r9
	movq	%rax, %rdx
	rex64 jmpq	*%r9
.LBB33_17:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.91(%rip), %rdx
	movl	$62, %r8d
	rex64 jmpq	*%rax
.LBB33_15:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.89(%rip), %rdx
	movl	$19, %r8d
	rex64 jmpq	*%rax
.LBB33_12:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.86(%rip), %rdx
	movl	$12, %r8d
	rex64 jmpq	*%rax
.LBB33_5:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.79(%rip), %rdx
	movl	$26, %r8d
	rex64 jmpq	*%rax
.LBB33_13:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.87(%rip), %rdx
	movl	$14, %r8d
	rex64 jmpq	*%rax
.LBB33_10:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.84(%rip), %rdx
	movl	$14, %r8d
	rex64 jmpq	*%rax
.LBB33_25:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.99(%rip), %rdx
	movl	$24, %r8d
	rex64 jmpq	*%rax
.LBB33_3:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.77(%rip), %rdx
	movl	$24, %r8d
	rex64 jmpq	*%rax
.LBB33_16:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.90(%rip), %rdx
	movl	$26, %r8d
	rex64 jmpq	*%rax
.LBB33_4:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.78(%rip), %rdx
	movl	$27, %r8d
	rex64 jmpq	*%rax
.LBB33_8:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.82(%rip), %rdx
	movl	$19, %r8d
	rex64 jmpq	*%rax
.LBB33_2:
	addq	$8, %rcx
	jmp	_RNvXs3_NtNtCs8xEFJqa6dYS_4core2io5errorNtB5_5ErrorNtNtB9_3fmt7Display3fmt
.LBB33_18:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.92(%rip), %rdx
	movl	$20, %r8d
	rex64 jmpq	*%rax
.LBB33_21:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.95(%rip), %rdx
	movl	$36, %r8d
	rex64 jmpq	*%rax
.LBB33_6:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.80(%rip), %rdx
	movl	$25, %r8d
	rex64 jmpq	*%rax
.LBB33_22:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.96(%rip), %rdx
	movl	$14, %r8d
	rex64 jmpq	*%rax
.LBB33_14:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.88(%rip), %rdx
	movl	$14, %r8d
	rex64 jmpq	*%rax
.LBB33_7:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.81(%rip), %rdx
	movl	$12, %r8d
	rex64 jmpq	*%rax
.LBB33_19:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.93(%rip), %rdx
	movl	$52, %r8d
	rex64 jmpq	*%rax
.LBB33_11:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.85(%rip), %rdx
	movl	$14, %r8d
	rex64 jmpq	*%rax
.LBB33_9:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.83(%rip), %rdx
	movl	$19, %r8d
	rex64 jmpq	*%rax
.LBB33_23:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.97(%rip), %rdx
	movl	$19, %r8d
	rex64 jmpq	*%rax
.LBB33_20:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.94(%rip), %rdx
	movl	$44, %r8d
	rex64 jmpq	*%rax
.LBB33_24:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.98(%rip), %rdx
	movl	$28, %r8d
	rex64 jmpq	*%rax
.Lfunc_end33:
	.section	.rdata,"dr",associative,_RNvXs1_NtCsavOST1yGCNT_10serde_json5errorNtB5_9ErrorCodeNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt,unique,39
	.p2align	2, 0x0
.LJTI33_0:
	.long	.LBB33_1-.LJTI33_0
	.long	.LBB33_2-.LJTI33_0
	.long	.LBB33_3-.LJTI33_0
	.long	.LBB33_4-.LJTI33_0
	.long	.LBB33_5-.LJTI33_0
	.long	.LBB33_6-.LJTI33_0
	.long	.LBB33_7-.LJTI33_0
	.long	.LBB33_8-.LJTI33_0
	.long	.LBB33_9-.LJTI33_0
	.long	.LBB33_10-.LJTI33_0
	.long	.LBB33_11-.LJTI33_0
	.long	.LBB33_12-.LJTI33_0
	.long	.LBB33_13-.LJTI33_0
	.long	.LBB33_14-.LJTI33_0
	.long	.LBB33_15-.LJTI33_0
	.long	.LBB33_16-.LJTI33_0
	.long	.LBB33_17-.LJTI33_0
	.long	.LBB33_18-.LJTI33_0
	.long	.LBB33_19-.LJTI33_0
	.long	.LBB33_20-.LJTI33_0
	.long	.LBB33_21-.LJTI33_0
	.long	.LBB33_22-.LJTI33_0
	.long	.LBB33_23-.LJTI33_0
	.long	.LBB33_24-.LJTI33_0
	.long	.LBB33_25-.LJTI33_0

	.def	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtReNtB6_5Debug3fmtCsavOST1yGCNT_10serde_json;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtReNtB6_5Debug3fmtCsavOST1yGCNT_10serde_json,unique,40
	.p2align	4
_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtReNtB6_5Debug3fmtCsavOST1yGCNT_10serde_json:
.Lfunc_begin34:
	movq	%rdx, %r8
	movq	(%rcx), %rax
	movq	8(%rcx), %rdx
	movq	%rax, %rcx
	jmp	_RNvXsh_NtCs8xEFJqa6dYS_4core3fmteNtB5_5Debug3fmt
.Lfunc_end34:

	.def	_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtRDNtNtCslmkRZor3pUd_10serde_core2de8ExpectedEL_NtB6_7Display3fmtCsavOST1yGCNT_10serde_json.llvm.16186315980599473920;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtRDNtNtCslmkRZor3pUd_10serde_core2de8ExpectedEL_NtB6_7Display3fmtCsavOST1yGCNT_10serde_json.llvm.16186315980599473920,unique,41
	.globl	_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtRDNtNtCslmkRZor3pUd_10serde_core2de8ExpectedEL_NtB6_7Display3fmtCsavOST1yGCNT_10serde_json.llvm.16186315980599473920
	.p2align	4
_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtRDNtNtCslmkRZor3pUd_10serde_core2de8ExpectedEL_NtB6_7Display3fmtCsavOST1yGCNT_10serde_json.llvm.16186315980599473920:
.Lfunc_begin35:
	movq	(%rcx), %rax
	movq	8(%rcx), %rcx
	movq	24(%rcx), %r8
	movq	%rax, %rcx
	rex64 jmpq	*%r8
.Lfunc_end35:

	.def	_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtReNtB6_7Display3fmtCsavOST1yGCNT_10serde_json;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtReNtB6_7Display3fmtCsavOST1yGCNT_10serde_json,unique,42
	.p2align	4
_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtReNtB6_7Display3fmtCsavOST1yGCNT_10serde_json:
.Lfunc_begin36:
	movq	%rdx, %rax
	movq	(%rcx), %rdx
	movq	8(%rcx), %r8
	movq	%rax, %rcx
	jmp	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
.Lfunc_end36:

	.def	_RNvXs2_NtNtCsavOST1yGCNT_10serde_json5value5indexNtB5_4TypeNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs2_NtNtCsavOST1yGCNT_10serde_json5value5indexNtB5_4TypeNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt,unique,43
	.globl	_RNvXs2_NtNtCsavOST1yGCNT_10serde_json5value5indexNtB5_4TypeNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt
	.p2align	4
_RNvXs2_NtNtCsavOST1yGCNT_10serde_json5value5indexNtB5_4TypeNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt:
.Lfunc_begin37:
	movq	(%rcx), %rax
	movzbl	(%rax), %eax
	leaq	.LJTI37_0(%rip), %rcx
	movslq	(%rcx,%rax,4), %rax
	addq	%rcx, %rax
	jmpq	*%rax
.LBB37_1:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.33(%rip), %rdx
	movl	$4, %r8d
	rex64 jmpq	*%rax
.LBB37_5:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.103(%rip), %rdx
	movl	$5, %r8d
	rex64 jmpq	*%rax
.LBB37_3:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.101(%rip), %rdx
	movl	$6, %r8d
	rex64 jmpq	*%rax
.LBB37_4:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.102(%rip), %rdx
	movl	$6, %r8d
	rex64 jmpq	*%rax
.LBB37_2:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.100(%rip), %rdx
	movl	$7, %r8d
	rex64 jmpq	*%rax
.LBB37_6:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.104(%rip), %rdx
	movl	$6, %r8d
	rex64 jmpq	*%rax
.Lfunc_end37:
	.section	.rdata,"dr",associative,_RNvXs2_NtNtCsavOST1yGCNT_10serde_json5value5indexNtB5_4TypeNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt,unique,44
	.p2align	2, 0x0
.LJTI37_0:
	.long	.LBB37_1-.LJTI37_0
	.long	.LBB37_2-.LJTI37_0
	.long	.LBB37_3-.LJTI37_0
	.long	.LBB37_4-.LJTI37_0
	.long	.LBB37_5-.LJTI37_0
	.long	.LBB37_6-.LJTI37_0

	.def	_RNvXs4_NtNtCsavOST1yGCNT_10serde_json5value3serNtB5_12SerializeMapNtNtCslmkRZor3pUd_10serde_core3ser12SerializeMap3end;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs4_NtNtCsavOST1yGCNT_10serde_json5value3serNtB5_12SerializeMapNtNtCslmkRZor3pUd_10serde_core3ser12SerializeMap3end,unique,45
	.globl	_RNvXs4_NtNtCsavOST1yGCNT_10serde_json5value3serNtB5_12SerializeMapNtNtCslmkRZor3pUd_10serde_core3ser12SerializeMap3end
	.p2align	4
_RNvXs4_NtNtCsavOST1yGCNT_10serde_json5value3serNtB5_12SerializeMapNtNtCslmkRZor3pUd_10serde_core3ser12SerializeMap3end:
.Lfunc_begin38:
.seh_proc _RNvXs4_NtNtCsavOST1yGCNT_10serde_json5value3serNtB5_12SerializeMapNtNtCslmkRZor3pUd_10serde_core3ser12SerializeMap3end
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$64, %rsp
	.seh_stackalloc 64
	.seh_endprologue
	movq	%rcx, %rsi
	movq	40(%rdx), %rax
	movq	%rax, 56(%rsp)
	movups	24(%rdx), %xmm0
	movups	%xmm0, 40(%rsp)
	movb	$5, (%rcx)
	movups	33(%rsp), %xmm0
	movq	48(%rsp), %rax
	movq	56(%rsp), %rcx
	movups	%xmm0, 1(%rsi)
	movq	%rax, 16(%rsi)
	movq	%rcx, 24(%rsi)
	cmpq	$0, (%rdx)
	jle	.LBB38_2
	movq	8(%rdx), %rcx
	callq	mi_free
.LBB38_2:
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end38:
	.seh_endproc

	.def	_RNvXs5_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceReadNtB5_4Read10ignore_str;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs5_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceReadNtB5_4Read10ignore_str,unique,46
	.globl	_RNvXs5_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceReadNtB5_4Read10ignore_str
	.p2align	4
_RNvXs5_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceReadNtB5_4Read10ignore_str:
.Lfunc_begin39:
.seh_proc _RNvXs5_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceReadNtB5_4Read10ignore_str
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
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movq	%rcx, %rsi
	callq	_RNvMs3_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceRead14skip_to_escape
	movq	8(%rsi), %r14
	movq	16(%rsi), %rcx
	cmpq	%r14, %rcx
	jne	.LBB39_4
.LBB39_1:
	movq	$4, 48(%rsp)
.LBB39_2:
	leaq	48(%rsp), %rdx
	movq	%rsi, %rcx
	callq	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_
	nop
.LBB39_3:
	.seh_startepilogue
	addq	$72, %rsp
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
.LBB39_4:
	leaq	.LJTI39_0(%rip), %r12
	leaq	_RNvNtCsavOST1yGCNT_10serde_json4read4HEX0(%rip), %rbp
	leaq	32(%rsp), %rdi
	leaq	48(%rsp), %rbx
	jmp	.LBB39_7
.LBB39_17:
	movzbl	(%r13,%r15), %eax
	movzbl	1(%r13,%r15), %ecx
	movzbl	2(%r13,%r15), %edx
	movzbl	3(%r13,%r15), %r8d
	addq	$4, %r15
	movq	%r15, 16(%rsi)
	movzwl	(%rbp,%rcx,2), %ecx
	leaq	_RNvNtCsavOST1yGCNT_10serde_json4read4HEX1(%rip), %r9
	orw	(%r9,%rax,2), %cx
	orw	(%r9,%rdx,2), %cx
	orw	(%rbp,%r8,2), %cx
	js	.LBB39_19
	movw	$0, 32(%rsp)
	cmpw	$1, 32(%rsp)
	je	.LBB39_25
	.p2align	4
.LBB39_14:
	movq	%rsi, %rcx
	callq	_RNvMs3_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceRead14skip_to_escape
	movq	8(%rsi), %r14
	movq	16(%rsi), %rcx
	cmpq	%r14, %rcx
	je	.LBB39_1
.LBB39_7:
	cmpq	%r14, %rcx
	jae	.LBB39_27
	movq	(%rsi), %r13
	movzbl	(%r13,%rcx), %eax
	cmpl	$92, %eax
	jne	.LBB39_20
	leaq	1(%rcx), %r15
	movq	%r15, 16(%rsi)
	cmpq	%r14, %r15
	jae	.LBB39_11
	movzbl	1(%r13,%rcx), %eax
	addq	$2, %rcx
	movq	%rcx, 16(%rsi)
	movq	%rcx, %r15
	movzbl	%al, %eax
	addl	$-34, %eax
	cmpl	$83, %eax
	jbe	.LBB39_13
	jmp	.LBB39_24
	.p2align	4
.LBB39_11:
	movq	$4, 48(%rsp)
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	movq	%rbx, %r8
	callq	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_
	cmpb	$0, 32(%rsp)
	jne	.LBB39_25
	movzbl	33(%rsp), %eax
	movzbl	%al, %eax
	addl	$-34, %eax
	cmpl	$83, %eax
	ja	.LBB39_24
.LBB39_13:
	movslq	(%r12,%rax,4), %rax
	addq	%r12, %rax
	jmpq	*%rax
.LBB39_15:
	movq	%r14, %rax
	subq	%r15, %rax
	jb	.LBB39_26
	cmpq	$3, %rax
	ja	.LBB39_17
	movq	%r14, 16(%rsi)
	movq	$4, 48(%rsp)
	jmp	.LBB39_6
.LBB39_19:
	movq	$12, 48(%rsp)
.LBB39_6:
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	movq	%rbx, %r8
	callq	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_
	cmpw	$1, 32(%rsp)
	jne	.LBB39_14
.LBB39_25:
	movq	40(%rsp), %rax
	jmp	.LBB39_3
.LBB39_20:
	cmpl	$34, %eax
	jne	.LBB39_22
	incq	%rcx
	movq	%rcx, 16(%rsi)
	xorl	%eax, %eax
	jmp	.LBB39_3
.LBB39_22:
	movq	$16, 48(%rsp)
	jmp	.LBB39_2
.LBB39_24:
	movq	$12, 48(%rsp)
	jmp	.LBB39_2
.LBB39_26:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.108(%rip), %r9
	movq	%r15, %rcx
	movq	%r14, %rdx
	movq	%r14, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	ud2
.LBB39_27:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.107(%rip), %r8
	movq	%r14, %rdx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	ud2
.Lfunc_end39:
	.section	.rdata,"dr",associative,_RNvXs5_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceReadNtB5_4Read10ignore_str,unique,47
	.p2align	2, 0x0
.LJTI39_0:
	.long	.LBB39_14-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_14-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_14-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_14-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_14-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_14-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_14-.LJTI39_0
	.long	.LBB39_24-.LJTI39_0
	.long	.LBB39_14-.LJTI39_0
	.long	.LBB39_15-.LJTI39_0
	.section	.text,"xr",one_only,_RNvXs5_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceReadNtB5_4Read10ignore_str,unique,46
	.seh_endproc

	.def	_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt,unique,48
	.globl	_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt
	.p2align	4
_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt:
.Lfunc_begin40:
.seh_proc _RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	movq	$-2, 32(%rbp)
	movq	%rdx, %rsi
	movq	(%rcx), %rdi
	movq	$0, (%rbp)
	movq	$1, 8(%rbp)
	movq	$0, 16(%rbp)
	movq	$1610612768, -64(%rbp)
	movq	%rbp, %rax
	movq	%rax, -80(%rbp)
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.114(%rip), %rax
	movq	%rax, -72(%rbp)
.Ltmp98:
	leaq	-80(%rbp), %rdx
	movq	%rdi, %rcx
	callq	_RNvXs1_NtCsavOST1yGCNT_10serde_json5errorNtB5_9ErrorCodeNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt
	nop
.Ltmp99:
	testb	%al, %al
	jne	.LBB40_2
	movq	16(%rbp), %rax
	movq	%rax, -16(%rbp)
	movups	(%rbp), %xmm0
	movaps	%xmm0, -32(%rbp)
	leaq	24(%rdi), %rax
	addq	$32, %rdi
	leaq	-32(%rbp), %rcx
	movq	%rcx, -80(%rbp)
	leaq	_RNvXsr_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt(%rip), %rcx
	movq	%rcx, -72(%rbp)
	movq	%rax, -64(%rbp)
	leaq	_RNvXsi_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impjNtB9_7Display3fmt(%rip), %rax
	movq	%rax, -56(%rbp)
	movq	%rdi, -48(%rbp)
	movq	%rax, -40(%rbp)
	movq	(%rsi), %rcx
	movq	8(%rsi), %rdx
.Ltmp100:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.109(%rip), %r8
	leaq	-80(%rbp), %r9
	callq	_RNvNtCs8xEFJqa6dYS_4core3fmt5write
	nop
.Ltmp101:
	cmpq	$0, -32(%rbp)
	je	.LBB40_13
	movq	-24(%rbp), %rcx
	movl	%eax, %ebx
	callq	mi_free
	movl	%ebx, %eax
.LBB40_13:
	.seh_startepilogue
	addq	$168, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB40_2:
.Ltmp102:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.117(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.115(%rip), %rcx
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.44(%rip), %r9
	leaq	31(%rbp), %r8
	movl	$55, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core6result13unwrap_failed
	nop
.Ltmp103:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt@IMGREL
	.section	.text,"xr",one_only,_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt,unique,48
	.seh_endproc
	.def	"?dtor$4@?0?_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$4@?0?_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt@4HA":
.seh_proc "?dtor$4@?0?_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt@4HA"
.LBB40_4:
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
	cmpq	$0, (%rbp)
	je	.LBB40_6
	movq	8(%rbp), %rcx
	callq	mi_free
	nop
.LBB40_6:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt,unique,48
	.seh_endproc
	.def	"?dtor$7@?0?_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$7@?0?_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt@4HA":
.seh_proc "?dtor$7@?0?_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt@4HA"
.LBB40_7:
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
	cmpq	$0, -32(%rbp)
	je	.LBB40_9
	movq	-24(%rbp), %rcx
	callq	mi_free
	nop
.LBB40_9:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end40:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt,unique,48
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt,unique,13
	.p2align	2, 0x0
$cppxdata$_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt:
	.long	429065506
	.long	2
	.long	$stateUnwindMap$_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt@IMGREL
	.long	0
	.long	0
	.long	5
	.long	$ip2state$_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt@IMGREL
	.long	160
	.long	0
	.long	1
$stateUnwindMap$_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt:
	.long	-1
	.long	"?dtor$4@?0?_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt@4HA"@IMGREL
	.long	-1
	.long	"?dtor$7@?0?_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt@4HA"@IMGREL
$ip2state$_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt:
	.long	.Lfunc_begin40@IMGREL
	.long	-1
	.long	.Ltmp98@IMGREL
	.long	0
	.long	.Ltmp100@IMGREL
	.long	1
	.long	.Ltmp102@IMGREL
	.long	0
	.long	.Ltmp103@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt,unique,48

	.def	_RNvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error12invalid_type;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error12invalid_type,unique,49
	.globl	_RNvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error12invalid_type
	.p2align	4
_RNvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error12invalid_type:
.Lfunc_begin41:
.seh_proc _RNvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error12invalid_type
	subq	$104, %rsp
	.seh_stackalloc 104
	.seh_endprologue
	movq	%rdx, 32(%rsp)
	movq	%r8, 40(%rsp)
	movq	16(%rcx), %rax
	movq	%rax, 96(%rsp)
	movups	(%rcx), %xmm0
	movaps	%xmm0, 80(%rsp)
	leaq	80(%rsp), %rax
	movq	%rax, 48(%rsp)
	leaq	_RNvXs8_NtCsavOST1yGCNT_10serde_json5errorNtB5_14JsonUnexpectedNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt(%rip), %rax
	movq	%rax, 56(%rsp)
	leaq	32(%rsp), %rax
	movq	%rax, 64(%rsp)
	leaq	_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtRDNtNtCslmkRZor3pUd_10serde_core2de8ExpectedEL_NtB6_7Display3fmtCsavOST1yGCNT_10serde_json.llvm.16186315980599473920(%rip), %rax
	movq	%rax, 72(%rsp)
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.111.llvm.16186315980599473920(%rip), %rcx
	leaq	48(%rsp), %rdx
	callq	_RINvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB6_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error6customNtNtCs8xEFJqa6dYS_4core3fmt9ArgumentsEB8_.llvm.16186315980599473920
	nop
	.seh_startepilogue
	addq	$104, %rsp
	.seh_endepilogue
	retq
.Lfunc_end41:
	.seh_endproc

	.def	_RNvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error13invalid_value;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error13invalid_value,unique,50
	.globl	_RNvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error13invalid_value
	.p2align	4
_RNvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error13invalid_value:
.Lfunc_begin42:
.seh_proc _RNvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error13invalid_value
	subq	$104, %rsp
	.seh_stackalloc 104
	.seh_endprologue
	movq	%rdx, 32(%rsp)
	movq	%r8, 40(%rsp)
	movq	16(%rcx), %rax
	movq	%rax, 96(%rsp)
	movups	(%rcx), %xmm0
	movaps	%xmm0, 80(%rsp)
	leaq	80(%rsp), %rax
	movq	%rax, 48(%rsp)
	leaq	_RNvXs8_NtCsavOST1yGCNT_10serde_json5errorNtB5_14JsonUnexpectedNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt(%rip), %rax
	movq	%rax, 56(%rsp)
	leaq	32(%rsp), %rax
	movq	%rax, 64(%rsp)
	leaq	_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtRDNtNtCslmkRZor3pUd_10serde_core2de8ExpectedEL_NtB6_7Display3fmtCsavOST1yGCNT_10serde_json.llvm.16186315980599473920(%rip), %rax
	movq	%rax, 72(%rsp)
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.112.llvm.16186315980599473920(%rip), %rcx
	leaq	48(%rsp), %rdx
	callq	_RINvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB6_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error6customNtNtCs8xEFJqa6dYS_4core3fmt9ArgumentsEB8_.llvm.16186315980599473920
	nop
	.seh_startepilogue
	addq	$104, %rsp
	.seh_endepilogue
	retq
.Lfunc_end42:
	.seh_endproc

	.def	_RNvXs6_NtNtCsavOST1yGCNT_10serde_json5value3serNtB5_12SerializeMapNtNtCslmkRZor3pUd_10serde_core3ser15SerializeStruct3end;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs6_NtNtCsavOST1yGCNT_10serde_json5value3serNtB5_12SerializeMapNtNtCslmkRZor3pUd_10serde_core3ser15SerializeStruct3end,unique,51
	.globl	_RNvXs6_NtNtCsavOST1yGCNT_10serde_json5value3serNtB5_12SerializeMapNtNtCslmkRZor3pUd_10serde_core3ser15SerializeStruct3end
	.p2align	4
_RNvXs6_NtNtCsavOST1yGCNT_10serde_json5value3serNtB5_12SerializeMapNtNtCslmkRZor3pUd_10serde_core3ser15SerializeStruct3end:
.Lfunc_begin43:
.seh_proc _RNvXs6_NtNtCsavOST1yGCNT_10serde_json5value3serNtB5_12SerializeMapNtNtCslmkRZor3pUd_10serde_core3ser15SerializeStruct3end
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$64, %rsp
	.seh_stackalloc 64
	.seh_endprologue
	movq	%rcx, %rsi
	movq	40(%rdx), %rax
	movq	%rax, 56(%rsp)
	movups	24(%rdx), %xmm0
	movups	%xmm0, 40(%rsp)
	movb	$5, (%rcx)
	movups	33(%rsp), %xmm0
	movq	48(%rsp), %rax
	movq	56(%rsp), %rcx
	movups	%xmm0, 1(%rsi)
	movq	%rax, 16(%rsi)
	movq	%rcx, 24(%rsi)
	cmpq	$0, (%rdx)
	jle	.LBB43_2
	movq	8(%rdx), %rcx
	callq	mi_free
.LBB43_2:
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end43:
	.seh_endproc

	.def	_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read10ignore_str;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read10ignore_str,unique,52
	.globl	_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read10ignore_str
	.p2align	4
_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read10ignore_str:
.Lfunc_begin44:
	jmp	_RNvXs5_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceReadNtB5_4Read10ignore_str
.Lfunc_end44:

	.def	_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read13peek_position;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read13peek_position,unique,53
	.globl	_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read13peek_position
	.p2align	4
_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read13peek_position:
.Lfunc_begin45:
.seh_proc _RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read13peek_position
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
	.seh_endprologue
	movq	(%rcx), %rdi
	movq	8(%rcx), %rbx
	movq	16(%rcx), %rsi
	incq	%rsi
	cmpq	%rbx, %rsi
	cmovaeq	%rbx, %rsi
	leaq	(%rdi,%rsi), %r8
	movq	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw2FN(%rip), %rax
	movb	$10, %cl
	movq	%rdi, %rdx
	callq	*%rax
	cmpq	$1, %rax
	jne	.LBB45_1
	subq	%rdi, %rdx
	leaq	1(%rdx), %r14
	cmpq	%rbx, %rdx
	jb	.LBB45_2
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920(%rip), %r9
	xorl	%ecx, %ecx
	movq	%r14, %rdx
	movq	%rbx, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	ud2
.LBB45_1:
	xorl	%r14d, %r14d
.LBB45_2:
	leaq	(%rdi,%r14), %r8
	movq	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw2FN(%rip), %rax
	movb	$10, %cl
	movq	%rdi, %rdx
	callq	*%rax
	incq	%rax
	subq	%r14, %rsi
	movq	%rsi, %rdx
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.Lfunc_end45:
	.seh_endproc

	.def	_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read8position;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read8position,unique,54
	.globl	_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read8position
	.p2align	4
_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read8position:
.Lfunc_begin46:
.seh_proc _RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read8position
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
	.seh_endprologue
	movq	16(%rcx), %rsi
	movq	8(%rcx), %rdi
	cmpq	%rdi, %rsi
	ja	.LBB46_6
	movq	(%rcx), %rbx
	leaq	(%rbx,%rsi), %r8
	movq	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw2FN(%rip), %rax
	movb	$10, %cl
	movq	%rbx, %rdx
	callq	*%rax
	cmpq	$1, %rax
	jne	.LBB46_2
	subq	%rbx, %rdx
	leaq	1(%rdx), %r14
	cmpq	%rdi, %rdx
	jb	.LBB46_3
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920(%rip), %r9
	xorl	%ecx, %ecx
	movq	%r14, %rdx
	movq	%rdi, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	ud2
.LBB46_2:
	xorl	%r14d, %r14d
.LBB46_3:
	leaq	(%rbx,%r14), %r8
	movq	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw2FN(%rip), %rax
	movb	$10, %cl
	movq	%rbx, %rdx
	callq	*%rax
	incq	%rax
	subq	%r14, %rsi
	movq	%rsi, %rdx
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB46_6:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.48.llvm.16186315980599473920(%rip), %r9
	xorl	%ecx, %ecx
	movq	%rsi, %rdx
	movq	%rdi, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	ud2
.Lfunc_end46:
	.seh_endproc

	.def	_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read9parse_str;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read9parse_str,unique,55
	.globl	_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read9parse_str
	.p2align	4
_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read9parse_str:
.Lfunc_begin47:
.seh_proc _RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read9parse_str
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
	subq	$88, %rsp
	.seh_stackalloc 88
	.seh_endprologue
	movq	%r8, %rbx
	movq	%rdx, %rdi
	movq	%rcx, 40(%rsp)
.LBB47_1:
	movq	16(%rdi), %r14
	movq	%rdi, %rcx
	callq	_RNvMs3_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceRead14skip_to_escape
	movq	8(%rdi), %r15
	movq	16(%rdi), %rsi
	cmpq	%r15, %rsi
	je	.LBB47_6
	jae	.LBB47_8
	movq	(%rdi), %rbp
	movzbl	(%rbp,%rsi), %eax
	cmpl	$92, %eax
	jne	.LBB47_4
	movq	%rsi, %r13
	subq	%r14, %r13
	jb	.LBB47_59
	movq	(%rbx), %rax
	movq	16(%rbx), %r12
	subq	%r12, %rax
	cmpq	%rax, %r13
	ja	.LBB47_22
	cmpq	%r14, %rsi
	je	.LBB47_25
.LBB47_24:
	addq	%rbp, %r14
	movq	8(%rbx), %rcx
	addq	%r12, %rcx
	movq	%r14, %rdx
	movq	%r13, %r8
	callq	memcpy
.LBB47_25:
	addq	%r13, %r12
	movq	%r12, 16(%rbx)
	leaq	1(%rsi), %rax
	movq	%rax, 16(%rdi)
	cmpq	%r15, %rax
	jae	.LBB47_27
	movzbl	1(%rbp,%rsi), %eax
	addq	$2, %rsi
	movq	%rsi, 16(%rdi)
	movzbl	%al, %eax
	addl	$-34, %eax
	cmpl	$83, %eax
	jbe	.LBB47_30
	jmp	.LBB47_31
	.p2align	4
.LBB47_27:
	movq	$4, 48(%rsp)
	leaq	72(%rsp), %rcx
	movq	%rdi, %rdx
	leaq	48(%rsp), %r8
	callq	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_
	cmpb	$0, 72(%rsp)
	jne	.LBB47_60
	movzbl	73(%rsp), %eax
	movzbl	%al, %eax
	addl	$-34, %eax
	cmpl	$83, %eax
	ja	.LBB47_31
.LBB47_30:
	leaq	.LJTI47_0(%rip), %rcx
	movslq	(%rcx,%rax,4), %rax
	addq	%rcx, %rax
	jmpq	*%rax
.LBB47_32:
	cmpq	(%rbx), %r12
	jne	.LBB47_34
	movq	%rbx, %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVechE8grow_oneB7_
.LBB47_34:
	movq	8(%rbx), %rax
	movb	$34, (%rax,%r12)
	jmp	.LBB47_35
.LBB47_45:
	cmpq	(%rbx), %r12
	jne	.LBB47_47
	movq	%rbx, %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVechE8grow_oneB7_
.LBB47_47:
	movq	8(%rbx), %rax
	movb	$12, (%rax,%r12)
	jmp	.LBB47_35
.LBB47_48:
	cmpq	(%rbx), %r12
	jne	.LBB47_50
	movq	%rbx, %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVechE8grow_oneB7_
.LBB47_50:
	movq	8(%rbx), %rax
	movb	$10, (%rax,%r12)
	jmp	.LBB47_35
.LBB47_42:
	cmpq	(%rbx), %r12
	jne	.LBB47_44
	movq	%rbx, %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVechE8grow_oneB7_
.LBB47_44:
	movq	8(%rbx), %rax
	movb	$8, (%rax,%r12)
	jmp	.LBB47_35
.LBB47_36:
	cmpq	(%rbx), %r12
	jne	.LBB47_38
	movq	%rbx, %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVechE8grow_oneB7_
.LBB47_38:
	movq	8(%rbx), %rax
	movb	$92, (%rax,%r12)
	jmp	.LBB47_35
.LBB47_39:
	cmpq	(%rbx), %r12
	jne	.LBB47_41
	movq	%rbx, %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVechE8grow_oneB7_
.LBB47_41:
	movq	8(%rbx), %rax
	movb	$47, (%rax,%r12)
	jmp	.LBB47_35
.LBB47_51:
	cmpq	(%rbx), %r12
	jne	.LBB47_53
	movq	%rbx, %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVechE8grow_oneB7_
.LBB47_53:
	movq	8(%rbx), %rax
	movb	$13, (%rax,%r12)
	jmp	.LBB47_35
.LBB47_54:
	cmpq	(%rbx), %r12
	jne	.LBB47_56
	movq	%rbx, %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVechE8grow_oneB7_
.LBB47_56:
	movq	8(%rbx), %rax
	movb	$9, (%rax,%r12)
	.p2align	4
.LBB47_35:
	incq	%r12
	movq	%r12, 16(%rbx)
	xorl	%eax, %eax
	testq	%rax, %rax
	je	.LBB47_1
	jmp	.LBB47_61
.LBB47_22:
	movq	%rbx, %rcx
	movq	%r12, %rdx
	movq	%r13, %r8
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECsavOST1yGCNT_10serde_json
	movq	16(%rbx), %r12
	jmp	.LBB47_24
.LBB47_57:
	movq	%rdi, %rcx
	movq	%rbx, %rdx
	callq	_RINvNtCsavOST1yGCNT_10serde_json4read20parse_unicode_escapeNtB2_9SliceReadEB4_
	testq	%rax, %rax
	je	.LBB47_1
	jmp	.LBB47_61
.LBB47_31:
	movq	$12, 48(%rsp)
	leaq	48(%rsp), %rdx
	movq	%rdi, %rcx
	callq	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_
.LBB47_61:
	movq	40(%rsp), %rsi
	movq	%rax, 8(%rsi)
	movq	$2, (%rsi)
	jmp	.LBB47_62
.LBB47_4:
	cmpl	$34, %eax
	jne	.LBB47_5
	movq	16(%rbx), %r12
	testq	%r12, %r12
	je	.LBB47_15
	movq	%rsi, %r13
	subq	%r14, %r13
	jb	.LBB47_63
	movq	(%rbx), %rax
	subq	%r12, %rax
	cmpq	%rax, %r13
	ja	.LBB47_12
	cmpq	%r14, %rsi
	je	.LBB47_19
.LBB47_18:
	addq	%r14, %rbp
	movq	8(%rbx), %rcx
	addq	%r12, %rcx
	movq	%rbp, %rdx
	movq	%r13, %r8
	callq	memcpy
.LBB47_19:
	addq	%r13, %r12
	movq	%r12, 16(%rbx)
	incq	%rsi
	movq	%rsi, 16(%rdi)
	movq	8(%rbx), %rax
	movq	40(%rsp), %rsi
	movq	$1, (%rsi)
	movq	%rax, 8(%rsi)
	movq	%r12, 16(%rsi)
	jmp	.LBB47_62
.LBB47_6:
	movq	$4, 48(%rsp)
	jmp	.LBB47_7
.LBB47_5:
	incq	%rsi
	movq	%rsi, 16(%rdi)
	movq	$16, 48(%rsp)
.LBB47_7:
	leaq	48(%rsp), %r8
	movq	40(%rsp), %rsi
	movq	%rsi, %rcx
	movq	%rdi, %rdx
	callq	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_
.LBB47_62:
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$88, %rsp
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
.LBB47_60:
	movq	80(%rsp), %rax
	jmp	.LBB47_61
.LBB47_15:
	movq	%rsi, %rax
	subq	%r14, %rax
	jb	.LBB47_13
	addq	%r14, %rbp
	incq	%rsi
	movq	%rsi, 16(%rdi)
	movq	40(%rsp), %rsi
	movq	$0, (%rsi)
	movq	%rbp, 8(%rsi)
	movq	%rax, 16(%rsi)
	jmp	.LBB47_62
.LBB47_59:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.4(%rip), %r9
.LBB47_14:
	movq	%r14, %rcx
	movq	%rsi, %rdx
	movq	%r15, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	ud2
.LBB47_63:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.3(%rip), %r9
	jmp	.LBB47_14
.LBB47_13:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.2(%rip), %r9
	jmp	.LBB47_14
.LBB47_12:
	movq	%rbx, %rcx
	movq	%r12, %rdx
	movq	%r13, %r8
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECsavOST1yGCNT_10serde_json
	movq	16(%rbx), %r12
	jmp	.LBB47_18
.LBB47_8:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.1(%rip), %r8
	movq	%rsi, %rcx
	movq	%r15, %rdx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	ud2
.Lfunc_end47:
	.section	.rdata,"dr",associative,_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read9parse_str,unique,56
	.p2align	2, 0x0
.LJTI47_0:
	.long	.LBB47_32-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_39-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_36-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_42-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_45-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_48-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_51-.LJTI47_0
	.long	.LBB47_31-.LJTI47_0
	.long	.LBB47_54-.LJTI47_0
	.long	.LBB47_57-.LJTI47_0
	.section	.text,"xr",one_only,_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read9parse_str,unique,55
	.seh_endproc

	.def	_RNvXs8_NtCsavOST1yGCNT_10serde_json5errorNtB5_14JsonUnexpectedNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs8_NtCsavOST1yGCNT_10serde_json5errorNtB5_14JsonUnexpectedNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt,unique,57
	.globl	_RNvXs8_NtCsavOST1yGCNT_10serde_json5errorNtB5_14JsonUnexpectedNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt
	.p2align	4
_RNvXs8_NtCsavOST1yGCNT_10serde_json5errorNtB5_14JsonUnexpectedNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt:
.Lfunc_begin48:
.seh_proc _RNvXs8_NtCsavOST1yGCNT_10serde_json5errorNtB5_14JsonUnexpectedNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$88, %rsp
	.seh_stackalloc 88
	.seh_endprologue
	movzbl	(%rcx), %eax
	cmpl	$3, %eax
	je	.LBB48_3
	cmpl	$7, %eax
	jne	.LBB48_5
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.33(%rip), %rdx
	movl	$4, %r8d
	.seh_startepilogue
	addq	$88, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	rex64 jmpq	*%rax
.LBB48_3:
	movq	8(%rcx), %xmm0
	movq	%xmm0, %rax
	movabsq	$9223372036854775807, %rcx
	andq	%rax, %rcx
	movabsq	$9218868437227405311, %r8
	cmpq	%r8, %rcx
	jle	.LBB48_7
	movq	%rax, %rcx
	shlq	$12, %rcx
	xorl	%r8d, %r8d
	testq	%rax, %rax
	sets	%r8b
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.119(%rip), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.120(%rip), %r9
	cmovnsq	%rax, %r9
	addq	$3, %r8
	testq	%rcx, %rcx
	movl	$3, %eax
	cmoveq	%r8, %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.121(%rip), %rsi
	cmoveq	%r9, %rsi
	jmp	.LBB48_8
.LBB48_5:
	movq	16(%rcx), %rax
	movq	%rax, 80(%rsp)
	movups	(%rcx), %xmm0
	movaps	%xmm0, 64(%rsp)
	leaq	64(%rsp), %rcx
	callq	_RNvXNtCslmkRZor3pUd_10serde_core2deNtB2_10UnexpectedNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt
	nop
	.seh_startepilogue
	addq	$88, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB48_7:
	leaq	64(%rsp), %rsi
	movq	%rdx, %rdi
	movq	%rsi, %rdx
	callq	_RNvXs_NtCs6FhewopUhnE_4zmij7privatedNtB4_6Sealed20write_to_zmij_buffer
	movq	%rdi, %rdx
	subq	%rsi, %rax
.LBB48_8:
	movq	%rsi, 32(%rsp)
	movq	%rax, 40(%rsp)
	leaq	32(%rsp), %rax
	movq	%rax, 48(%rsp)
	leaq	_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtReNtB6_7Display3fmtCsavOST1yGCNT_10serde_json(%rip), %rax
	movq	%rax, 56(%rsp)
	movq	(%rdx), %rcx
	movq	8(%rdx), %rdx
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.113(%rip), %r8
	leaq	48(%rsp), %r9
	callq	_RNvNtCs8xEFJqa6dYS_4core3fmt5write
	nop
	.seh_startepilogue
	addq	$88, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end48:
	.seh_endproc

	.def	_RNvXsK_NtCs8xEFJqa6dYS_4core3fmtNtB5_5ErrorNtB5_5Debug3fmt;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXsK_NtCs8xEFJqa6dYS_4core3fmtNtB5_5ErrorNtB5_5Debug3fmt,unique,58
	.p2align	4
_RNvXsK_NtCs8xEFJqa6dYS_4core3fmtNtB5_5ErrorNtB5_5Debug3fmt:
.Lfunc_begin49:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.118(%rip), %rdx
	movl	$5, %r8d
	rex64 jmpq	*%rax
.Lfunc_end49:

	.def	_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write10write_char;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write10write_char,unique,59
	.p2align	4
_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write10write_char:
.Lfunc_begin50:
.seh_proc _RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write10write_char
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	16(%rcx), %rsi
	movl	$1, %edi
	cmpl	$128, %edx
	jb	.LBB50_3
	movl	$2, %edi
	cmpl	$2048, %edx
	jb	.LBB50_3
	cmpl	$65536, %edx
	movl	$4, %edi
	sbbq	$0, %rdi
.LBB50_3:
	movq	(%rcx), %rax
	subq	%rsi, %rax
	cmpq	%rax, %rdi
	ja	.LBB50_4
	movq	8(%rcx), %rax
	cmpl	$128, %edx
	jae	.LBB50_6
.LBB50_12:
	movb	%dl, (%rax,%rsi)
	jmp	.LBB50_11
.LBB50_4:
	movq	%rcx, %rbx
	movl	%edx, %ebp
	movq	%rsi, %rdx
	movq	%rdi, %r8
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECsavOST1yGCNT_10serde_json
	movl	%ebp, %edx
	movq	%rbx, %rcx
	movq	8(%rcx), %rax
	cmpl	$128, %edx
	jb	.LBB50_12
.LBB50_6:
	movl	%edx, %r8d
	andb	$63, %r8b
	orb	$-128, %r8b
	movl	%edx, %r9d
	shrl	$6, %r9d
	cmpl	$2048, %edx
	jae	.LBB50_8
	orb	$-64, %r9b
	movb	%r9b, (%rax,%rsi)
	movb	%r8b, 1(%rax,%rsi)
	jmp	.LBB50_11
.LBB50_8:
	andb	$63, %r9b
	orb	$-128, %r9b
	movl	%edx, %r10d
	shrl	$12, %r10d
	cmpl	$65535, %edx
	ja	.LBB50_10
	orb	$-32, %r10b
	movb	%r10b, (%rax,%rsi)
	movb	%r9b, 1(%rax,%rsi)
	movb	%r8b, 2(%rax,%rsi)
	jmp	.LBB50_11
.LBB50_10:
	andb	$63, %r10b
	orb	$-128, %r10b
	shrl	$18, %edx
	orb	$-16, %dl
	movb	%dl, (%rax,%rsi)
	movb	%r10b, 1(%rax,%rsi)
	movb	%r9b, 2(%rax,%rsi)
	movb	%r8b, 3(%rax,%rsi)
.LBB50_11:
	addq	%rsi, %rdi
	movq	%rdi, 16(%rcx)
	xorl	%eax, %eax
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end50:
	.seh_endproc

	.def	_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_str;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_str,unique,60
	.p2align	4
_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_str:
.Lfunc_begin51:
.seh_proc _RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_str
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
	.seh_endprologue
	movq	%r8, %rsi
	movq	%rcx, %rdi
	movq	(%rcx), %rax
	movq	16(%rcx), %rbx
	subq	%rbx, %rax
	cmpq	%rax, %r8
	ja	.LBB51_1
	testq	%rsi, %rsi
	je	.LBB51_4
.LBB51_3:
	movq	8(%rdi), %rcx
	addq	%rbx, %rcx
	movq	%rsi, %r8
	callq	memcpy
.LBB51_4:
	addq	%rsi, %rbx
	movq	%rbx, 16(%rdi)
	xorl	%eax, %eax
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB51_1:
	movq	%rdi, %rcx
	movq	%rdx, %r14
	movq	%rbx, %rdx
	movq	%rsi, %r8
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECsavOST1yGCNT_10serde_json
	movq	%r14, %rdx
	movq	16(%rdi), %rbx
	jmp	.LBB51_3
.Lfunc_end51:
	.seh_endproc

	.def	_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt,unique,61
	.globl	_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt
	.p2align	4
_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt:
.Lfunc_begin52:
.seh_proc _RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$104, %rsp
	.seh_stackalloc 104
	leaq	96(%rsp), %rbp
	.seh_setframe %rbp, 96
	.seh_endprologue
	movq	$-2, (%rbp)
	testl	$8388608, 16(%rdx)
	movq	%rdx, -16(%rbp)
	leaq	-16(%rbp), %rax
	jne	.LBB52_6
	movq	%rax, -56(%rbp)
	leaq	-56(%rbp), %rdx
	callq	_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_
	testq	%rax, %rax
	je	.LBB52_12
	movq	%rax, %rsi
	movq	(%rax), %rax
	cmpq	$1, %rax
	jne	.LBB52_8
	movq	8(%rsi), %rax
	movl	%eax, %ecx
	andl	$3, %ecx
	leal	-2(%rcx), %edx
	cmpl	$2, %edx
	jb	.LBB52_18
	testq	%rcx, %rcx
	je	.LBB52_18
	movq	%rsi, -8(%rbp)
	leaq	-1(%rax), %rcx
.Ltmp106:
	callq	*23(%rax)
	nop
.Ltmp107:
	jmp	.LBB52_17
.LBB52_6:
	movq	%rax, -56(%rbp)
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.18(%rip), %rax
	movq	%rax, -48(%rbp)
	movq	$2, -40(%rbp)
	movq	$0, -32(%rbp)
	movb	$0, -24(%rbp)
	leaq	-56(%rbp), %rdx
	callq	_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_
	testq	%rax, %rax
	je	.LBB52_12
	movq	%rax, %rsi
	movq	(%rax), %rax
	cmpq	$1, %rax
	je	.LBB52_14
.LBB52_8:
	testq	%rax, %rax
	jne	.LBB52_18
	cmpq	$0, 16(%rsi)
	je	.LBB52_18
	movq	8(%rsi), %rcx
	callq	mi_free
	jmp	.LBB52_18
.LBB52_12:
	xorl	%eax, %eax
	.seh_startepilogue
	addq	$104, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB52_14:
	movq	8(%rsi), %rax
	movl	%eax, %ecx
	andl	$3, %ecx
	leal	-2(%rcx), %edx
	cmpl	$2, %edx
	jb	.LBB52_18
	testq	%rcx, %rcx
	je	.LBB52_18
	movq	%rsi, -8(%rbp)
	leaq	-1(%rax), %rcx
.Ltmp104:
	callq	*23(%rax)
	nop
.Ltmp105:
.LBB52_17:
	movq	-8(%rbp), %rsi
.LBB52_18:
	movq	%rsi, %rcx
	callq	mi_free
	movb	$1, %al
	.seh_startepilogue
	addq	$104, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.long	$cppxdata$_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt@IMGREL
	.section	.text,"xr",one_only,_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt,unique,61
	.seh_endproc
	.def	"?dtor$19@?0?_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$19@?0?_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt@4HA":
.seh_proc "?dtor$19@?0?_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt@4HA"
.LBB52_19:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	96(%rdx), %rbp
	.seh_endprologue
	movq	-8(%rbp), %rcx
	callq	mi_free
	nop
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt,unique,61
	.seh_endproc
	.def	"?dtor$20@?0?_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$20@?0?_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt@4HA":
.seh_proc "?dtor$20@?0?_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt@4HA"
.LBB52_20:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	96(%rdx), %rbp
	.seh_endprologue
	movq	-8(%rbp), %rcx
	callq	mi_free
	nop
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end52:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt,unique,61
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt,unique,14
	.p2align	2, 0x0
$cppxdata$_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt:
	.long	429065506
	.long	2
	.long	$stateUnwindMap$_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt@IMGREL
	.long	0
	.long	0
	.long	5
	.long	$ip2state$_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt@IMGREL
	.long	96
	.long	0
	.long	1
$stateUnwindMap$_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt:
	.long	-1
	.long	"?dtor$20@?0?_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt@4HA"@IMGREL
	.long	-1
	.long	"?dtor$19@?0?_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt@4HA"@IMGREL
$ip2state$_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt:
	.long	.Lfunc_begin52@IMGREL
	.long	-1
	.long	.Ltmp106@IMGREL
	.long	0
	.long	.Ltmp107@IMGREL
	.long	-1
	.long	.Ltmp104@IMGREL
	.long	1
	.long	.Ltmp105@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt,unique,61

	.def	_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value3serNtB4_10SerializerNtNtCslmkRZor3pUd_10serde_core3ser10Serializer13serialize_seq;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value3serNtB4_10SerializerNtNtCslmkRZor3pUd_10serde_core3ser10Serializer13serialize_seq,unique,62
	.globl	_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value3serNtB4_10SerializerNtNtCslmkRZor3pUd_10serde_core3ser10Serializer13serialize_seq
	.p2align	4
_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value3serNtB4_10SerializerNtNtCslmkRZor3pUd_10serde_core3ser10Serializer13serialize_seq:
.Lfunc_begin53:
.seh_proc _RNvXs_NtNtCsavOST1yGCNT_10serde_json5value3serNtB4_10SerializerNtNtCslmkRZor3pUd_10serde_core3ser10Serializer13serialize_seq
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
	.seh_endprologue
	xorl	%edi, %edi
	testb	$1, %dl
	cmoveq	%rdi, %r8
	movq	%r8, %rsi
	shlq	$5, %rsi
	movq	%r8, %rax
	shrq	$59, %rax
	setne	%al
	movabsq	$9223372036854775800, %rdx
	cmpq	%rdx, %rsi
	seta	%dl
	orb	%al, %dl
	je	.LBB53_1
.LBB53_6:
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.LBB53_1:
	testq	%rsi, %rsi
	je	.LBB53_2
	movl	$8, %edi
	movl	$8, %edx
	movq	%rcx, %rbx
	movq	%rsi, %rcx
	movq	%r8, %r14
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB53_6
	movq	%r14, %rdx
	movq	%rbx, %rcx
	jmp	.LBB53_5
.LBB53_2:
	movl	$8, %eax
	xorl	%edx, %edx
.LBB53_5:
	movq	%rdx, (%rcx)
	movq	%rax, 8(%rcx)
	movq	$0, 16(%rcx)
	movq	%rcx, %rax
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.Lfunc_end53:
	.seh_endproc

	.def	_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value3serNtB4_10SerializerNtNtCslmkRZor3pUd_10serde_core3ser10Serializer15serialize_tuple;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value3serNtB4_10SerializerNtNtCslmkRZor3pUd_10serde_core3ser10Serializer15serialize_tuple,unique,63
	.globl	_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value3serNtB4_10SerializerNtNtCslmkRZor3pUd_10serde_core3ser10Serializer15serialize_tuple
	.p2align	4
_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value3serNtB4_10SerializerNtNtCslmkRZor3pUd_10serde_core3ser10Serializer15serialize_tuple:
.Lfunc_begin54:
.seh_proc _RNvXs_NtNtCsavOST1yGCNT_10serde_json5value3serNtB4_10SerializerNtNtCslmkRZor3pUd_10serde_core3ser10Serializer15serialize_tuple
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
	.seh_endprologue
	movq	%rdx, %rsi
	shlq	$5, %rsi
	movq	%rdx, %rax
	shrq	$59, %rax
	setne	%al
	movabsq	$9223372036854775800, %r8
	cmpq	%r8, %rsi
	seta	%r8b
	orb	%al, %r8b
	je	.LBB54_3
	xorl	%edi, %edi
.LBB54_2:
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.LBB54_3:
	testq	%rsi, %rsi
	je	.LBB54_4
	movq	%rdx, %rbx
	movq	%rcx, %r14
	movl	$8, %edi
	movl	$8, %edx
	movq	%rsi, %rcx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB54_2
	movq	%r14, %rcx
	jmp	.LBB54_7
.LBB54_4:
	movl	$8, %eax
	xorl	%ebx, %ebx
.LBB54_7:
	movq	%rbx, (%rcx)
	movq	%rax, 8(%rcx)
	movq	$0, 16(%rcx)
	movq	%rcx, %rax
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.Lfunc_end54:
	.seh_endproc

	.def	_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value4fromNtB6_5ValueINtNtCs8xEFJqa6dYS_4core7convert4FromdE4from;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value4fromNtB6_5ValueINtNtCs8xEFJqa6dYS_4core7convert4FromdE4from,unique,64
	.globl	_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value4fromNtB6_5ValueINtNtCs8xEFJqa6dYS_4core7convert4FromdE4from
	.p2align	4
_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value4fromNtB6_5ValueINtNtCs8xEFJqa6dYS_4core7convert4FromdE4from:
.Lfunc_begin55:
.seh_proc _RNvXs_NtNtCsavOST1yGCNT_10serde_json5value4fromNtB6_5ValueINtNtCs8xEFJqa6dYS_4core7convert4FromdE4from
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$64, %rsp
	.seh_stackalloc 64
	.seh_endprologue
	movq	%rcx, %rsi
	movq	%xmm1, %rax
	movabsq	$9223372036854775807, %rcx
	andq	%rax, %rcx
	movabsq	$9218868437227405312, %rax
	movb	$0, 32(%rsp)
	cmpq	%rax, %rcx
	jl	.LBB55_2
	movzbl	32(%rsp), %eax
	movq	33(%rsp), %rcx
	movl	41(%rsp), %edx
	movzwl	45(%rsp), %r8d
	movzbl	47(%rsp), %r9d
	movups	48(%rsp), %xmm0
	movups	%xmm0, 16(%rsi)
	movb	%al, (%rsi)
	movq	%rcx, 1(%rsi)
	movl	%edx, 9(%rsi)
	movw	%r8w, 13(%rsi)
	movb	%r9b, 15(%rsi)
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB55_2:
	movq	$2, 8(%rsi)
	movq	%xmm1, 16(%rsi)
	movb	$2, (%rsi)
	leaq	32(%rsp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end55:
	.seh_endproc

	.def	_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index10index_into;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index10index_into,unique,65
	.globl	_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index10index_into
	.p2align	4
_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index10index_into:
.Lfunc_begin56:
.seh_proc _RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index10index_into
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
	subq	$56, %rsp
	.seh_stackalloc 56
	.seh_endprologue
	cmpb	$5, (%r8)
	jne	.LBB56_1
	movq	8(%r8), %r14
	testq	%r14, %r14
	je	.LBB56_1
	movq	%rdx, %r15
	movq	%rcx, %rdi
	movq	16(%r8), %rax
	movq	%rax, 40(%rsp)
.LBB56_5:
	leaq	360(%r14), %rax
	movzwl	626(%r14), %ecx
	leaq	-32(%r14), %rbx
	movq	%rcx, 48(%rsp)
	leal	(,%rcx,8), %ecx
	leaq	(%rcx,%rcx,2), %rbp
	movq	$-1, %r12
	.p2align	4
.LBB56_6:
	testq	%rbp, %rbp
	je	.LBB56_7
	leaq	24(%rax), %r13
	movq	8(%rax), %rdx
	movq	16(%rax), %r8
	movq	%r15, %rsi
	subq	%r8, %rsi
	cmovbq	%r15, %r8
	movq	%rdi, %rcx
	callq	memcmp
	cltq
	testl	%eax, %eax
	cmovneq	%rax, %rsi
	testq	%rsi, %rsi
	sets	%al
	setg	%cl
	subb	%al, %cl
	addq	$32, %rbx
	incq	%r12
	addq	$-24, %rbp
	movq	%r13, %rax
	cmpb	$1, %cl
	je	.LBB56_6
	movzbl	%cl, %eax
	testl	%eax, %eax
	je	.LBB56_2
	jmp	.LBB56_10
	.p2align	4
.LBB56_7:
	movq	48(%rsp), %r12
.LBB56_10:
	movq	40(%rsp), %rax
	subq	$1, %rax
	jb	.LBB56_1
	movq	%rax, 40(%rsp)
	movq	632(%r14,%r12,8), %r14
	jmp	.LBB56_5
.LBB56_1:
	xorl	%ebx, %ebx
.LBB56_2:
	movq	%rbx, %rax
	.seh_startepilogue
	addq	$56, %rsp
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
.Lfunc_end56:
	.seh_endproc

	.def	_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert,unique,66
	.globl	_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert
	.p2align	4
_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert:
.Lfunc_begin57:
.seh_proc _RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert
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
	subq	$472, %rsp
	.seh_stackalloc 472
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	movq	$-2, 336(%rbp)
	movq	%r8, %rbx
	movq	%rdx, %r14
	movq	%rcx, %rsi
	movq	%rcx, -64(%rbp)
	movq	%rdx, -56(%rbp)
	movzbl	(%r8), %eax
	testl	%eax, %eax
	jne	.LBB57_3
.Ltmp108:
	movq	%rbx, %rcx
	movq	%rbx, 264(%rbp)
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920
	nop
.Ltmp109:
	movq	264(%rbp), %rbx
	movb	$5, (%rbx)
	movq	$0, 8(%rbx)
	movq	$0, 24(%rbx)
	jmp	.LBB57_4
.LBB57_3:
	cmpl	$5, %eax
	jne	.LBB57_90
.LBB57_4:
	testq	%r14, %r14
	jns	.LBB57_7
	xorl	%edi, %edi
.LBB57_6:
	movq	%rdi, %rcx
	movq	%r14, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.LBB57_7:
	je	.LBB57_21
	movl	$1, %edi
	movl	$1, %edx
	movq	%r14, %rcx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB57_6
	movq	%rax, %r15
	movq	%rax, %rcx
	movq	%rsi, %rdx
	movq	%r14, %r8
	callq	memcpy
	movq	8(%rbx), %rsi
	testq	%rsi, %rsi
	je	.LBB57_22
.LBB57_10:
	movq	%r15, 296(%rbp)
	movq	%r14, 328(%rbp)
	movq	%rbx, 264(%rbp)
	movq	16(%rbx), %rdi
	movq	%rdi, 152(%rbp)
	movq	%rsi, 160(%rbp)
	movq	%rsi, %rax
.LBB57_11:
	leaq	360(%rax), %rcx
	movq	%rax, 304(%rbp)
	movzwl	626(%rax), %r13d
	leal	(,%r13,8), %eax
	leaq	(%rax,%rax,2), %r14
	movl	$32, %ebx
	movq	$-1, %r12
	movq	%rcx, 312(%rbp)
	.p2align	4
.LBB57_12:
	testq	%r14, %r14
	je	.LBB57_15
	leaq	24(%rcx), %r15
	movq	8(%rcx), %rdx
	movq	16(%rcx), %r8
	movq	328(%rbp), %rax
	movq	%rax, %rsi
	subq	%r8, %rsi
	cmovbq	%rax, %r8
	movq	296(%rbp), %rcx
	callq	memcmp
	cltq
	testl	%eax, %eax
	cmovneq	%rax, %rsi
	testq	%rsi, %rsi
	sets	%cl
	setg	%al
	subb	%cl, %al
	addq	$-32, %rbx
	incq	%r12
	addq	$-24, %r14
	movq	%r15, %rcx
	cmpb	$1, %al
	je	.LBB57_12
	movzbl	%al, %eax
	testl	%eax, %eax
	jne	.LBB57_16
	jmp	.LBB57_18
	.p2align	4
.LBB57_15:
	movq	%r13, %r12
.LBB57_16:
	movq	304(%rbp), %rax
	subq	$1, %rdi
	jb	.LBB57_26
	movq	632(%rax,%r12,8), %rax
	jmp	.LBB57_11
.LBB57_18:
	cmpq	$0, 328(%rbp)
	movq	304(%rbp), %r12
	je	.LBB57_20
	movq	296(%rbp), %rcx
	callq	mi_free
.LBB57_20:
	movb	$0, 120(%rbp)
	subq	%rbx, %r12
	leaq	120(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920
	jmp	.LBB57_25
.LBB57_21:
	movl	$1, %r15d
	movq	8(%rbx), %rsi
	testq	%rsi, %rsi
	jne	.LBB57_10
.LBB57_22:
	movb	$0, 120(%rbp)
	movl	$632, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB57_91
	movq	$0, 352(%rax)
	movq	%rax, 8(%rbx)
	movq	$0, 16(%rbx)
	movw	$1, 626(%rax)
	movq	%r14, 360(%rax)
	movq	%r15, 368(%rax)
	movq	%r14, 376(%rax)
	movups	120(%rbp), %xmm0
	movups	136(%rbp), %xmm1
	movups	%xmm0, (%rax)
	movups	%xmm1, 16(%rax)
	xorl	%r12d, %r12d
.LBB57_24:
	incq	24(%rbx)
	shlq	$5, %r12
	addq	%rax, %r12
.LBB57_25:
	movq	%r12, %rax
	.seh_startepilogue
	addq	$472, %rsp
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
.LBB57_26:
	movb	$0, 120(%rbp)
	cmpw	$11, %r13w
	jae	.LBB57_29
	leaq	(%r12,%r12,2), %rax
	movq	312(%rbp), %rcx
	leaq	(%rcx,%rax,8), %r14
	cmpq	%r12, %r13
	jbe	.LBB57_31
	leaq	1(%r12), %rdi
	leaq	(%rdi,%rdi,2), %rax
	leaq	(%rcx,%rax,8), %rcx
	movl	%r13d, %ebx
	subl	%r12d, %ebx
	leal	(,%rbx,8), %eax
	leaq	(%rax,%rax,2), %r8
	movq	%r14, %rdx
	callq	memmove
	movq	328(%rbp), %rax
	movq	%rax, (%r14)
	movq	296(%rbp), %rcx
	movq	%rcx, 8(%r14)
	movq	%rax, 16(%r14)
	movups	120(%rbp), %xmm0
	movups	136(%rbp), %xmm1
	movaps	%xmm1, 32(%rbp)
	movaps	%xmm0, 16(%rbp)
	movq	%r12, %rdx
	shlq	$5, %rdx
	movq	304(%rbp), %rsi
	addq	%rsi, %rdx
	shlq	$5, %rdi
	addq	%rsi, %rdi
	shll	$5, %ebx
	movq	%rdi, %rcx
	movq	%rbx, %r8
	callq	memmove
	jmp	.LBB57_32
.LBB57_29:
	cmpq	$5, %r12
	jae	.LBB57_33
	movl	$4, %r14d
	movl	$0, 320(%rbp)
	movq	312(%rbp), %rbx
	jmp	.LBB57_38
.LBB57_31:
	movq	328(%rbp), %rax
	movq	%rax, (%r14)
	movq	296(%rbp), %rcx
	movq	%rcx, 8(%r14)
	movq	%rax, 16(%r14)
	movups	120(%rbp), %xmm0
	movups	136(%rbp), %xmm1
	movaps	%xmm1, 32(%rbp)
	movaps	%xmm0, 16(%rbp)
	movq	304(%rbp), %rsi
.LBB57_32:
	incl	%r13d
	movq	%r12, %rax
	shlq	$5, %rax
	movaps	16(%rbp), %xmm0
	movaps	32(%rbp), %xmm1
	movups	%xmm1, 16(%rsi,%rax)
	movups	%xmm0, (%rsi,%rax)
	movw	%r13w, 626(%rsi)
	movq	%rsi, %rax
	jmp	.LBB57_73
.LBB57_33:
	movq	312(%rbp), %rbx
	je	.LBB57_36
	cmpq	$6, %r12
	jne	.LBB57_37
	movl	$5, %r14d
	movb	$1, %al
	movl	%eax, 320(%rbp)
	xorl	%r12d, %r12d
	jmp	.LBB57_38
.LBB57_36:
	movl	$0, 320(%rbp)
	movq	%r12, %r14
	jmp	.LBB57_38
.LBB57_37:
	addq	$-7, %r12
	movl	$6, %r14d
	movb	$1, %al
	movl	%eax, 320(%rbp)
.LBB57_38:
	movl	$632, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB57_97
	movq	%rax, %r15
	movq	$0, 352(%rax)
	movq	304(%rbp), %rsi
	movzwl	626(%rsi), %eax
	movq	%r14, %rdi
	notq	%rdi
	addq	%rax, %rdi
	movw	%di, 626(%r15)
	leaq	(%r14,%r14,2), %rax
	movq	(%rbx,%rax,8), %rcx
	movq	%rcx, 280(%rbp)
	movq	8(%rbx,%rax,8), %rcx
	movq	%rcx, 288(%rbp)
	movq	16(%rbx,%rax,8), %rax
	movq	%rax, 248(%rbp)
	movq	%r14, %r13
	shlq	$5, %r13
	movups	(%rsi,%r13), %xmm0
	movups	16(%rsi,%r13), %xmm1
	movaps	%xmm1, 32(%rbp)
	movaps	%xmm0, 16(%rbp)
	cmpq	$12, %rdi
	jae	.LBB57_96
	movq	%rbx, %rcx
	addq	%rsi, %r13
	leaq	1(%r14), %rbx
	leaq	(%rbx,%rbx,2), %rax
	leaq	(%rcx,%rax,8), %rdx
	leaq	360(%r15), %rcx
	leaq	(,%rdi,8), %rax
	leaq	(%rax,%rax,2), %r8
	callq	memcpy
	shlq	$5, %rbx
	addq	%rsi, %rbx
	shlq	$5, %rdi
	movq	%r15, %rcx
	movq	%rbx, %rdx
	movq	%rdi, %r8
	callq	memcpy
	movw	%r14w, 626(%rsi)
	movups	(%r13), %xmm0
	movups	16(%r13), %xmm1
	movaps	%xmm0, -16(%rbp)
	movaps	%xmm1, (%rbp)
	cmpb	$0, 320(%rbp)
	movq	%r15, %r13
	movq	%r15, %rax
	cmoveq	%rsi, %rax
	movzwl	626(%rax), %r15d
	movzwl	%r15w, %edi
	leaq	(%r12,%r12,2), %rcx
	leaq	(%rax,%rcx,8), %r14
	addq	$360, %r14
	cmpq	%r12, %rdi
	movq	%rax, 272(%rbp)
	jbe	.LBB57_42
	addq	$360, %rax
	leaq	1(%r12), %rbx
	leaq	(%rbx,%rbx,2), %rcx
	leaq	(%rax,%rcx,8), %rcx
	subl	%r12d, %edi
	leal	(,%rdi,8), %eax
	leaq	(%rax,%rax,2), %r8
	movq	%r14, %rdx
	callq	memmove
	movq	328(%rbp), %rax
	movq	%rax, (%r14)
	movq	296(%rbp), %rcx
	movq	%rcx, 8(%r14)
	movq	%rax, 16(%r14)
	movups	120(%rbp), %xmm0
	movups	136(%rbp), %xmm1
	movaps	%xmm1, 32(%rbp)
	movaps	%xmm0, 16(%rbp)
	movq	%r12, %rdx
	shlq	$5, %rdx
	addq	272(%rbp), %rdx
	shlq	$5, %rbx
	addq	272(%rbp), %rbx
	shll	$5, %edi
	movq	%rbx, %rcx
	movq	%rdi, %r8
	callq	memmove
	movq	272(%rbp), %rax
	jmp	.LBB57_43
.LBB57_42:
	movq	328(%rbp), %rcx
	movq	%rcx, (%r14)
	movq	296(%rbp), %rdx
	movq	%rdx, 8(%r14)
	movq	%rcx, 16(%r14)
	movups	120(%rbp), %xmm0
	movups	136(%rbp), %xmm1
	movaps	%xmm1, 32(%rbp)
	movaps	%xmm0, 16(%rbp)
.LBB57_43:
	movq	152(%rbp), %rsi
	incl	%r15d
	movq	%r12, %rcx
	shlq	$5, %rcx
	movaps	16(%rbp), %xmm0
	movaps	32(%rbp), %xmm1
	movups	%xmm1, 16(%rax,%rcx)
	movups	%xmm0, (%rax,%rcx)
	movw	%r15w, 626(%rax)
	movaps	-16(%rbp), %xmm0
	movaps	(%rbp), %xmm1
	movaps	%xmm1, -32(%rbp)
	movaps	%xmm0, -48(%rbp)
	movq	280(%rbp), %r14
	cmpq	$-1, %r14
	movq	304(%rbp), %r11
	je	.LBB57_73
	movaps	-48(%rbp), %xmm0
	movaps	-32(%rbp), %xmm1
	movaps	%xmm1, 208(%rbp)
	movaps	%xmm0, 192(%rbp)
	movq	352(%r11), %rcx
	testq	%rcx, %rcx
	je	.LBB57_74
	movq	$0, 224(%rbp)
	movq	248(%rbp), %rdx
	movq	288(%rbp), %r9
	movq	%r13, %r10
	movq	%r14, %r13
.LBB57_46:
	movq	%rdx, 232(%rbp)
	movzwl	624(%r11), %edx
	movq	%rcx, %rsi
	movzwl	%dx, %r8d
	movzwl	626(%rcx), %ebx
	cmpq	$11, %rbx
	movq	%r10, 176(%rbp)
	movq	%r13, 240(%rbp)
	movq	%rbx, 168(%rbp)
	jb	.LBB57_79
	cmpw	$5, %dx
	movq	%r9, 184(%rbp)
	jae	.LBB57_49
	movq	%r8, 312(%rbp)
	movl	$4, %eax
	movq	%rax, 320(%rbp)
	xorl	%r14d, %r14d
	jmp	.LBB57_54
.LBB57_49:
	je	.LBB57_52
	cmpl	$6, %r8d
	jne	.LBB57_53
	movb	$1, %r14b
	movl	$5, %eax
	movq	%rax, 320(%rbp)
	movq	$0, 312(%rbp)
	jmp	.LBB57_54
.LBB57_52:
	xorl	%r14d, %r14d
	movq	%r8, 312(%rbp)
	movq	%r8, 320(%rbp)
	jmp	.LBB57_54
.LBB57_53:
	addq	$-7, %r8
	movq	%r8, 312(%rbp)
	movb	$1, %r14b
	movl	$6, %eax
	movq	%rax, 320(%rbp)
.LBB57_54:
	movl	$728, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB57_94
	movq	%rax, %rdi
	movl	%r14d, 116(%rbp)
	movq	$0, 352(%rdi)
	movzwl	626(%rsi), %eax
	movq	320(%rbp), %rcx
	movq	%rcx, %rbx
	notq	%rbx
	addq	%rax, %rbx
	movw	%bx, 626(%rdi)
	leaq	(%rcx,%rcx,2), %rax
	movq	360(%rsi,%rax,8), %rdx
	movq	%rdx, 280(%rbp)
	movq	368(%rsi,%rax,8), %rdx
	movq	%rdx, 288(%rbp)
	movq	376(%rsi,%rax,8), %rax
	movq	%rax, 248(%rbp)
	movl	%ecx, %r13d
	shll	$5, %r13d
	movups	(%rsi,%r13), %xmm0
	movups	16(%rsi,%r13), %xmm1
	movaps	%xmm1, (%rbp)
	movaps	%xmm0, -16(%rbp)
	cmpq	$12, %rbx
	movq	%rdi, 256(%rbp)
	jae	.LBB57_92
	leaq	360(%rsi), %rax
	addq	%rsi, %r13
	movq	%rsi, 304(%rbp)
	leaq	1(%rcx), %r14
	leaq	(%r14,%r14,2), %rcx
	leaq	(%rax,%rcx,8), %rdx
	leaq	360(%rdi), %rcx
	leaq	(,%rbx,8), %rax
	leaq	(%rax,%rax,2), %r8
	callq	memcpy
	shll	$5, %r14d
	addq	304(%rbp), %r14
	shlq	$5, %rbx
	movq	%rdi, %rcx
	movq	%r14, %rdx
	movq	304(%rbp), %rsi
	movq	%rbx, %r8
	callq	memcpy
	movq	320(%rbp), %r10
	movw	%r10w, 626(%rsi)
	movups	(%r13), %xmm0
	movups	16(%r13), %xmm1
	leaq	40(%rbp), %rax
	movups	%xmm0, (%rax)
	movups	%xmm1, 16(%rax)
	movq	280(%rbp), %rax
	movq	%rax, 16(%rbp)
	movq	288(%rbp), %rax
	movq	%rax, 24(%rbp)
	movq	248(%rbp), %rax
	movq	%rax, 32(%rbp)
	movzwl	626(%rdi), %ebx
	leaq	1(%rbx), %r8
	cmpq	$11, %rbx
	ja	.LBB57_93
	movzwl	168(%rbp), %eax
	subl	%r10d, %eax
	cmpl	%r8d, %eax
	movq	224(%rbp), %rax
	movl	116(%rbp), %r14d
	jne	.LBB57_95
	incq	%rax
	movq	%rax, 224(%rbp)
	leaq	632(%rdi), %rcx
	leaq	(%rsi,%r10,8), %rdx
	addq	$640, %rdx
	shll	$3, %r8d
	callq	memcpy
	xorl	%eax, %eax
	movq	256(%rbp), %r15
	.p2align	4
.LBB57_59:
	movq	%rax, %rcx
	cmpq	%rbx, %rax
	adcq	$0, %rax
	movq	632(%r15,%rcx,8), %rdx
	movq	%r15, 352(%rdx)
	movw	%cx, 624(%rdx)
	cmpq	%rbx, %rcx
	jae	.LBB57_61
	cmpq	%rbx, %rax
	jbe	.LBB57_59
.LBB57_61:
	leaq	40(%rbp), %rax
	movups	(%rax), %xmm0
	movups	16(%rax), %xmm1
	movaps	%xmm1, -32(%rbp)
	movaps	%xmm0, -48(%rbp)
	testb	%r14b, %r14b
	cmoveq	%rsi, %rdi
	movzwl	626(%rdi), %r13d
	movq	312(%rbp), %r8
	leaq	1(%r8), %rbx
	movq	%r13, %rsi
	leaq	(%r8,%r8,2), %rax
	leaq	(%rdi,%rax,8), %r14
	addq	$360, %r14
	subq	%r8, %rsi
	jbe	.LBB57_63
	leaq	360(%rdi), %rax
	leaq	(%rbx,%rbx,2), %rcx
	leaq	(%rax,%rcx,8), %rcx
	movl	%r13d, %r15d
	subl	%r8d, %r15d
	leal	(,%r15,8), %eax
	movq	%rax, 320(%rbp)
	leaq	(%rax,%rax,2), %r8
	movq	%r14, %rdx
	callq	memmove
	movq	240(%rbp), %rax
	movq	%rax, (%r14)
	movq	184(%rbp), %rax
	movq	%rax, 8(%r14)
	movq	232(%rbp), %rax
	movq	%rax, 16(%r14)
	movq	%rsi, %r14
	movq	312(%rbp), %rsi
	shlq	$5, %rsi
	leaq	(%rdi,%rsi), %rdx
	movq	%rbx, %rcx
	shlq	$5, %rcx
	addq	%rdi, %rcx
	shll	$5, %r15d
	movq	%r15, %r8
	movq	256(%rbp), %r15
	callq	memmove
	movaps	192(%rbp), %xmm0
	movaps	208(%rbp), %xmm1
	movups	%xmm0, (%rdi,%rsi)
	movups	%xmm1, 16(%rdi,%rsi)
	movq	%r14, %rsi
	leaq	632(%rdi,%rbx,8), %rdx
	movq	312(%rbp), %rax
	leaq	(%rdi,%rax,8), %rcx
	addq	$648, %rcx
	movq	320(%rbp), %r8
	callq	memmove
	movq	312(%rbp), %r8
	jmp	.LBB57_64
.LBB57_63:
	movq	240(%rbp), %rax
	movq	%rax, (%r14)
	movq	184(%rbp), %rax
	movq	%rax, 8(%r14)
	movq	232(%rbp), %rax
	movq	%rax, 16(%r14)
	movq	%r8, %rax
	shlq	$5, %rax
	movaps	192(%rbp), %xmm0
	movaps	208(%rbp), %xmm1
	movups	%xmm1, 16(%rdi,%rax)
	movups	%xmm0, (%rdi,%rax)
.LBB57_64:
	movq	272(%rbp), %rax
	movq	176(%rbp), %r9
	leal	1(%r13), %edx
	leaq	2(%r13), %rcx
	movq	%r9, 640(%rdi,%r8,8)
	movw	%dx, 626(%rdi)
	cmpl	%ecx, %ebx
	movq	304(%rbp), %r11
	movq	280(%rbp), %r14
	jae	.LBB57_71
	subl	%r8d, %r13d
	incl	%r13d
	andl	$3, %r13d
	je	.LBB57_69
	leaq	(%rdi,%r8,8), %r8
	addq	$640, %r8
	xorl	%edx, %edx
	.p2align	4
.LBB57_67:
	movq	(%r8,%rdx,8), %r9
	movq	%rdi, 352(%r9)
	leal	(%rbx,%rdx), %r10d
	movw	%r10w, 624(%r9)
	incq	%rdx
	cmpq	%rdx, %r13
	jne	.LBB57_67
	addq	%rdx, %rbx
.LBB57_69:
	cmpl	$3, %esi
	jb	.LBB57_71
	.p2align	4
.LBB57_70:
	movq	632(%rdi,%rbx,8), %rdx
	movq	%rdi, 352(%rdx)
	movw	%bx, 624(%rdx)
	movq	640(%rdi,%rbx,8), %rdx
	movq	%rdi, 352(%rdx)
	leal	1(%rbx), %r8d
	movw	%r8w, 624(%rdx)
	movq	648(%rdi,%rbx,8), %rdx
	movq	%rdi, 352(%rdx)
	leal	2(%rbx), %r8d
	movw	%r8w, 624(%rdx)
	movq	656(%rdi,%rbx,8), %rdx
	movq	%rdi, 352(%rdx)
	leal	3(%rbx), %r8d
	movw	%r8w, 624(%rdx)
	addq	$4, %rbx
	cmpq	%rcx, %rbx
	jne	.LBB57_70
.LBB57_71:
	movaps	-48(%rbp), %xmm0
	movaps	-32(%rbp), %xmm1
	movaps	%xmm1, -80(%rbp)
	movaps	%xmm0, -96(%rbp)
	cmpq	$-1, %r14
	je	.LBB57_73
	movaps	-96(%rbp), %xmm0
	movaps	-80(%rbp), %xmm1
	movaps	%xmm1, 208(%rbp)
	movaps	%xmm0, 192(%rbp)
	movq	352(%r11), %rcx
	movq	248(%rbp), %rbx
	movq	%rbx, %rdx
	movq	288(%rbp), %rdi
	movq	%rdi, %r9
	movq	%r15, %r10
	movq	%r14, %r13
	testq	%rcx, %rcx
	movq	152(%rbp), %rsi
	jne	.LBB57_46
	jmp	.LBB57_75
.LBB57_74:
	movq	$0, 224(%rbp)
	movq	%r13, %r15
	movq	288(%rbp), %rdi
	movq	248(%rbp), %rbx
.LBB57_75:
	movaps	192(%rbp), %xmm0
	movaps	208(%rbp), %xmm1
	movups	%xmm1, 56(%rbp)
	movups	%xmm0, 40(%rbp)
	movq	%r14, 16(%rbp)
	movq	%rdi, 24(%rbp)
	movq	%rbx, 32(%rbp)
	movq	%r11, 72(%rbp)
	movq	224(%rbp), %r13
	movq	%r13, 80(%rbp)
	movq	%r15, 88(%rbp)
	movq	%r13, 96(%rbp)
	movl	$728, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB57_98
	movq	$0, 352(%rax)
	movw	$0, 626(%rax)
	movq	160(%rbp), %rdx
	movq	%rdx, 632(%rax)
	movq	%rsi, %rcx
	incq	%rcx
	movq	%rax, %r8
	movq	272(%rbp), %rax
	je	.LBB57_99
	movq	%r8, 352(%rdx)
	movw	$0, 624(%rdx)
	movq	264(%rbp), %rdx
	movq	%r8, 8(%rdx)
	movq	%rcx, 16(%rdx)
	cmpq	%rsi, %r13
	jne	.LBB57_100
	movw	$1, 626(%r8)
	movq	%r14, 360(%r8)
	movq	%rdi, 368(%r8)
	movq	%rbx, 376(%r8)
	movaps	192(%rbp), %xmm0
	movaps	208(%rbp), %xmm1
	movups	%xmm0, (%r8)
	movups	%xmm1, 16(%r8)
	movq	%r15, 640(%r8)
	movq	%r8, 352(%r15)
	movw	$1, 624(%r15)
	movq	264(%rbp), %rbx
	jmp	.LBB57_24
.LBB57_79:
	leal	1(%rbx), %r11d
	leaq	1(%r8), %rdi
	leaq	(%r8,%r8,2), %rcx
	movq	%rsi, %r15
	leaq	(%rsi,%rcx,8), %r14
	addq	$360, %r14
	cmpw	%bx, %dx
	jae	.LBB57_81
	leaq	360(%r15), %rax
	leaq	(%rdi,%rdi,2), %rcx
	leaq	(%rax,%rcx,8), %rcx
	movq	168(%rbp), %rbx
	subq	%r8, %rbx
	leaq	(,%rbx,8), %rax
	movq	%rax, 296(%rbp)
	movq	%r8, %r13
	leaq	(%rax,%rax,2), %r8
	movq	%r14, %rdx
	movq	%r9, %rsi
	movl	%r11d, 328(%rbp)
	callq	memmove
	movq	240(%rbp), %rax
	movq	%rax, (%r14)
	movq	%rsi, 8(%r14)
	movq	232(%rbp), %rax
	movq	%rax, 16(%r14)
	movl	%r13d, %esi
	shll	$5, %esi
	leaq	(%r15,%rsi), %rdx
	movl	%edi, %ecx
	shll	$5, %ecx
	addq	%r15, %rcx
	shlq	$5, %rbx
	movq	%rbx, %r8
	movq	168(%rbp), %rbx
	callq	memmove
	movaps	192(%rbp), %xmm0
	movaps	208(%rbp), %xmm1
	movups	%xmm0, (%r15,%rsi)
	movups	%xmm1, 16(%r15,%rsi)
	leaq	(%r15,%rdi,8), %rdx
	addq	$632, %rdx
	leaq	(%r15,%r13,8), %rcx
	addq	$648, %rcx
	movq	296(%rbp), %r8
	callq	memmove
	movl	328(%rbp), %r11d
	movq	176(%rbp), %r10
	movq	%r13, %r8
	movq	272(%rbp), %rax
	jmp	.LBB57_82
.LBB57_81:
	movq	%r13, (%r14)
	movq	%r9, 8(%r14)
	movq	232(%rbp), %rcx
	movq	%rcx, 16(%r14)
	movl	%r8d, %ecx
	shll	$5, %ecx
	movaps	192(%rbp), %xmm0
	movaps	208(%rbp), %xmm1
	movups	%xmm1, 16(%r15,%rcx)
	movups	%xmm0, (%r15,%rcx)
.LBB57_82:
	movq	%r15, %rsi
	leaq	2(%rbx), %rcx
	movq	%r10, 640(%r15,%r8,8)
	movw	%r11w, 626(%r15)
	cmpl	%ecx, %edi
	jae	.LBB57_73
	movl	%ebx, %edx
	subl	%r8d, %edx
	incl	%edx
	subq	%r8, %rbx
	andl	$3, %edx
	je	.LBB57_87
	leaq	(%rsi,%r8,8), %r9
	addq	$640, %r9
	xorl	%r8d, %r8d
.LBB57_85:
	movq	(%r9,%r8,8), %r10
	movq	%rsi, 352(%r10)
	leal	(%rdi,%r8), %r11d
	movw	%r11w, 624(%r10)
	incq	%r8
	cmpq	%r8, %rdx
	jne	.LBB57_85
	addq	%r8, %rdi
.LBB57_87:
	cmpl	$3, %ebx
	jb	.LBB57_73
.LBB57_88:
	movq	632(%rsi,%rdi,8), %rdx
	movq	%rsi, 352(%rdx)
	movw	%di, 624(%rdx)
	movq	640(%rsi,%rdi,8), %rdx
	movq	%rsi, 352(%rdx)
	leal	1(%rdi), %r8d
	movw	%r8w, 624(%rdx)
	movq	648(%rsi,%rdi,8), %rdx
	movq	%rsi, 352(%rdx)
	leal	2(%rdi), %r8d
	movw	%r8w, 624(%rdx)
	movq	656(%rsi,%rdi,8), %rdx
	movq	%rsi, 352(%rdx)
	leal	3(%rdi), %r8d
	movw	%r8w, 624(%rdx)
	addq	$4, %rdi
	cmpq	%rcx, %rdi
	jne	.LBB57_88
.LBB57_73:
	movq	264(%rbp), %rbx
	jmp	.LBB57_24
.LBB57_90:
	movq	%rbx, -16(%rbp)
	leaq	-64(%rbp), %rax
	movq	%rax, 16(%rbp)
	leaq	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtReNtB6_5Debug3fmtCsavOST1yGCNT_10serde_json(%rip), %rax
	movq	%rax, 24(%rbp)
	leaq	-16(%rbp), %rax
	movq	%rax, 32(%rbp)
	leaq	_RNvXs2_NtNtCsavOST1yGCNT_10serde_json5value5indexNtB5_4TypeNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt(%rip), %rax
	movq	%rax, 40(%rbp)
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.123(%rip), %rcx
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.124(%rip), %r8
	leaq	16(%rbp), %rdx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking9panic_fmt
	ud2
.LBB57_91:
.Ltmp128:
	movq	%rsi, 160(%rbp)
	movq	%r15, 296(%rbp)
	movq	%r14, 328(%rbp)
	movl	$8, %ecx
	movl	$632, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp129:
	jmp	.LBB57_101
.LBB57_92:
.Ltmp112:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.49(%rip), %r9
	movl	$11, %r8d
	xorl	%ecx, %ecx
	movq	%rbx, %rdx
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	nop
.Ltmp113:
	jmp	.LBB57_101
.LBB57_93:
.Ltmp114:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.11(%rip), %r9
	movq	%r8, %rdx
	movl	$12, %r8d
	xorl	%ecx, %ecx
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	nop
.Ltmp115:
	jmp	.LBB57_101
.LBB57_94:
.Ltmp118:
	movl	$8, %ecx
	movl	$728, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp119:
	jmp	.LBB57_101
.LBB57_95:
.Ltmp116:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.19(%rip), %rcx
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.20(%rip), %r8
	movl	$40, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking5panic
	nop
.Ltmp117:
	jmp	.LBB57_101
.LBB57_96:
.Ltmp110:
	movq	%r15, 256(%rbp)
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.49(%rip), %r9
	movl	$11, %r8d
	xorl	%ecx, %ecx
	movq	%rdi, %rdx
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	nop
.Ltmp111:
	jmp	.LBB57_101
.LBB57_97:
.Ltmp126:
	movl	$8, %ecx
	movl	$632, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp127:
	jmp	.LBB57_101
.LBB57_98:
.Ltmp124:
	movl	$8, %ecx
	movl	$728, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp125:
	jmp	.LBB57_101
.LBB57_99:
.Ltmp122:
	movq	%r8, 328(%rbp)
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.8(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	nop
.Ltmp123:
	jmp	.LBB57_101
.LBB57_100:
.Ltmp120:
	movq	%r14, 280(%rbp)
	movq	%rdi, 288(%rbp)
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.52(%rip), %rcx
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.53(%rip), %r8
	movl	$48, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking5panic
	nop
.Ltmp121:
.LBB57_101:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@IMGREL
	.section	.text,"xr",one_only,_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert,unique,66
	.seh_endproc
	.def	"?dtor$102@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$102@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA":
.seh_proc "?dtor$102@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA"
.LBB57_102:
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movq	264(%rbp), %rax
	movb	$5, (%rax)
	movq	$0, 8(%rax)
	movq	$0, 24(%rax)
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert,unique,66
	.seh_endproc
	.def	"?dtor$103@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$103@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA":
.seh_proc "?dtor$103@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA"
.LBB57_103:
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	leaq	40(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920
	cmpq	$0, 280(%rbp)
	je	.LBB57_105
	movq	288(%rbp), %rcx
	callq	mi_free
	nop
.LBB57_105:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert,unique,66
	.seh_endproc
	.def	"?dtor$106@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$106@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA":
.seh_proc "?dtor$106@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA"
.LBB57_106:
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movq	328(%rbp), %rcx
	callq	mi_free
	nop
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert,unique,66
	.seh_endproc
	.def	"?dtor$107@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$107@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA":
.seh_proc "?dtor$107@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA"
.LBB57_107:
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	ud2
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert,unique,66
	.seh_endproc
	.def	"?dtor$108@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$108@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA":
.seh_proc "?dtor$108@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA"
.LBB57_108:
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	leaq	16(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920
	cmpq	$0, 280(%rbp)
	je	.LBB57_110
	movq	288(%rbp), %rcx
	callq	mi_free
	nop
.LBB57_110:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert,unique,66
	.seh_endproc
	.def	"?dtor$111@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$111@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA":
.seh_proc "?dtor$111@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA"
.LBB57_111:
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movq	256(%rbp), %rcx
	callq	mi_free
	nop
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert,unique,66
	.seh_endproc
	.def	"?dtor$112@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$112@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA":
.seh_proc "?dtor$112@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA"
.LBB57_112:
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	leaq	120(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920
	cmpq	$0, 328(%rbp)
	je	.LBB57_114
	movq	296(%rbp), %rcx
	callq	mi_free
	nop
.LBB57_114:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert,unique,66
	.seh_endproc
	.def	"?dtor$115@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$115@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA":
.seh_proc "?dtor$115@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA"
.LBB57_115:
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	leaq	-16(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920
	cmpq	$0, 280(%rbp)
	je	.LBB57_117
	movq	288(%rbp), %rcx
	callq	mi_free
	nop
.LBB57_117:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert,unique,66
	.seh_endproc
	.def	"?dtor$118@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$118@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA":
.seh_proc "?dtor$118@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA"
.LBB57_118:
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	leaq	16(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueTNtNtCsfQUUnEvlYZE_5alloc6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueEEB1i_
	nop
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert,unique,66
	.seh_endproc
	.def	"?dtor$119@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$119@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA":
.seh_proc "?dtor$119@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA"
.LBB57_119:
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movq	256(%rbp), %rcx
	callq	mi_free
	nop
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert,unique,66
	.seh_endproc
	.def	"?dtor$120@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$120@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA":
.seh_proc "?dtor$120@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA"
.LBB57_120:
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	leaq	192(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920
	cmpq	$0, 240(%rbp)
	je	.LBB57_122
	movq	184(%rbp), %rcx
	callq	mi_free
	nop
.LBB57_122:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert,unique,66
	.seh_endproc
	.def	"?dtor$123@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$123@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA":
.seh_proc "?dtor$123@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA"
.LBB57_123:
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 160(%rbp)
	je	.LBB57_125
.LBB57_124:
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
.LBB57_125:
	leaq	120(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5value5ValueEBF_.llvm.16186315980599473920
	cmpq	$0, 328(%rbp)
	je	.LBB57_124
	movq	296(%rbp), %rcx
	callq	mi_free
	jmp	.LBB57_124
.Lfunc_end57:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert,unique,66
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert,unique,15
	.p2align	2, 0x0
$cppxdata$_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert:
	.long	429065506
	.long	12
	.long	$stateUnwindMap$_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@IMGREL
	.long	0
	.long	0
	.long	14
	.long	$ip2state$_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@IMGREL
	.long	464
	.long	0
	.long	1
$stateUnwindMap$_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert:
	.long	-1
	.long	"?dtor$102@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA"@IMGREL
	.long	-1
	.long	"?dtor$123@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA"@IMGREL
	.long	1
	.long	"?dtor$120@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA"@IMGREL
	.long	2
	.long	"?dtor$119@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA"@IMGREL
	.long	3
	.long	"?dtor$118@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA"@IMGREL
	.long	3
	.long	"?dtor$115@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA"@IMGREL
	.long	1
	.long	"?dtor$103@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA"@IMGREL
	.long	1
	.long	"?dtor$112@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA"@IMGREL
	.long	7
	.long	"?dtor$111@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA"@IMGREL
	.long	8
	.long	"?dtor$108@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA"@IMGREL
	.long	-1
	.long	"?dtor$107@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA"@IMGREL
	.long	10
	.long	"?dtor$106@?0?_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert@4HA"@IMGREL
$ip2state$_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert:
	.long	.Lfunc_begin57@IMGREL
	.long	-1
	.long	.Ltmp108@IMGREL
	.long	0
	.long	.Ltmp109@IMGREL
	.long	-1
	.long	.Ltmp128@IMGREL
	.long	1
	.long	.Ltmp112@IMGREL
	.long	5
	.long	.Ltmp114@IMGREL
	.long	4
	.long	.Ltmp118@IMGREL
	.long	2
	.long	.Ltmp116@IMGREL
	.long	4
	.long	.Ltmp110@IMGREL
	.long	9
	.long	.Ltmp126@IMGREL
	.long	7
	.long	.Ltmp124@IMGREL
	.long	10
	.long	.Ltmp122@IMGREL
	.long	11
	.long	.Ltmp120@IMGREL
	.long	6
	.long	.Ltmp121@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value5indexeNtB4_5Index15index_or_insert,unique,66

	.def	_RNvXsr_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXsr_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt,unique,67
	.p2align	4
_RNvXsr_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt:
.Lfunc_begin58:
	movq	%rdx, %r8
	movq	8(%rcx), %rax
	movq	16(%rcx), %rdx
	movq	%rax, %rcx
	jmp	_RNvXsh_NtCs8xEFJqa6dYS_4core3fmteNtB5_5Debug3fmt
.Lfunc_end58:

	.def	_RNvYNtNtCsfQUUnEvlYZE_5alloc6string6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_fmtCsavOST1yGCNT_10serde_json;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvYNtNtCsfQUUnEvlYZE_5alloc6string6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_fmtCsavOST1yGCNT_10serde_json,unique,68
	.p2align	4
_RNvYNtNtCsfQUUnEvlYZE_5alloc6string6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_fmtCsavOST1yGCNT_10serde_json:
.Lfunc_begin59:
	movq	%r8, %r9
	movq	%rdx, %r8
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.114(%rip), %rdx
	jmp	_RNvNtCs8xEFJqa6dYS_4core3fmt5write
.Lfunc_end59:

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920,unique,69
	.globl	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920:
	.asciz	"C:\\Users\\there\\.cargo\\registry\\src\\index.crates.io-1949cf8c6b5b557f\\serde_json-1.0.150\\src\\read.rs"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.1,unique,70
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.1:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920
	.asciz	"b\000\000\000\000\000\000\000\000\002\000\000\023\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.2,unique,71
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.2:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920
	.asciz	"b\000\000\000\000\000\000\000\005\002\000\0003\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.3,unique,72
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.3:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920
	.asciz	"b\000\000\000\000\000\000\000\t\002\000\000>\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.4,unique,73
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.4:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920
	.asciz	"b\000\000\000\000\000\000\000\017\002\000\000:\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.7,unique,74
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.7:
	.asciz	"/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\alloc\\src\\collections\\btree\\node.rs"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.8,unique,75
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.8:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.7
	.asciz	"[\000\000\000\000\000\000\000\360\000\000\000M\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.11,unique,76
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.11:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.7
	.asciz	"[\000\000\000\000\000\000\000\023\005\000\000$\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.12,unique,77
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.12:
	.asciz	"/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\alloc\\src\\collections\\btree\\navigate.rs"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.13,unique,78
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.13:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.12
	.asciz	"_\000\000\000\000\000\000\000\306\000\000\000'\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.14,unique,79
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.14:
	.asciz	"/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\str\\pattern.rs"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.16,unique,80
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.16:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.14
	.asciz	"O\000\000\000\000\000\000\000V\006\000\000\024\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.17,unique,81
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.17:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.14
	.asciz	"O\000\000\000\000\000\000\000E\006\000\000\024\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.18,unique,82
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.18:
	.zero	2,32

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.19,unique,83
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.19:
	.ascii	"assertion failed: src.len() == dst.len()"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.20,unique,84
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.20:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.7
	.asciz	"[\000\000\000\000\000\000\000T\007\000\000\005\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.23,unique,85
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.23:
	.byte	10

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.24,unique,86
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.24:
	.byte	125

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.25,unique,87
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.25:
	.byte	91

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.26,unique,88
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.26:
	.byte	123

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.27,unique,89
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.27:
	.ascii	",\n"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.28,unique,90
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.28:
	.ascii	": "

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.29,unique,91
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.29:
	.byte	93

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.30,unique,92
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.30:
	.byte	34

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.31,unique,93
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.31:
	.ascii	"false"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.32,unique,94
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.32:
	.ascii	"true"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.33,unique,95
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.33:
	.ascii	"null"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.34,unique,96
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.34:
	.byte	44

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.35,unique,97
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.35:
	.byte	58

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.36,unique,98
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.36:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.12
	.asciz	"_\000\000\000\000\000\000\000X\002\000\0000\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.43,unique,99
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.43:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.12
	.asciz	"_\000\000\000\000\000\000\000\026\002\000\000/\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.44,unique,100
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.44:
	.asciz	"\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\001\000\000\000\000\000\000"
	.quad	_RNvXsK_NtCs8xEFJqa6dYS_4core3fmtNtB5_5ErrorNtB5_5Debug3fmt

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.45,unique,101
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.45:
	.ascii	"assertion failed: self.is_char_boundary(new_len)"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.46,unique,102
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.46:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920
	.asciz	"b\000\000\000\000\000\000\000\263\001\000\000\032\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920,unique,103
	.globl	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920
	.asciz	"b\000\000\000\000\000\000\000\253\001\000\000=\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.48.llvm.16186315980599473920,unique,104
	.globl	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.48.llvm.16186315980599473920
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.48.llvm.16186315980599473920:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920
	.asciz	"b\000\000\000\000\000\000\000\246\001\000\000E\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.49,unique,105
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.49:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.7
	.asciz	"[\000\000\000\000\000\000\000\320\004\000\000#\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.52,unique,106
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.52:
	.ascii	"assertion failed: edge.height == self.height - 1"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.53,unique,107
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.53:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.7
	.asciz	"[\000\000\000\000\000\000\000\266\002\000\000\t\000\000"

	.section	.rdata,"dr",one_only,_RNvNtCsavOST1yGCNT_10serde_json4read4HEX0,unique,108
	.globl	_RNvNtCsavOST1yGCNT_10serde_json4read4HEX0
	.p2align	1, 0x0
_RNvNtCsavOST1yGCNT_10serde_json4read4HEX0:
	.ascii	"\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\000\000\001\000\002\000\003\000\004\000\005\000\006\000\007\000\b\000\t\000\377\377\377\377\377\377\377\377\377\377\377\377\377\377\n\000\013\000\f\000\r\000\016\000\017\000\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\n\000\013\000\f\000\r\000\016\000\017\000\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377"

	.section	.rdata,"dr",one_only,_RNvNtCsavOST1yGCNT_10serde_json4read4HEX1,unique,109
	.globl	_RNvNtCsavOST1yGCNT_10serde_json4read4HEX1
	.p2align	1, 0x0
_RNvNtCsavOST1yGCNT_10serde_json4read4HEX1:
	.ascii	"\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\000\000\020\000 \0000\000@\000P\000`\000p\000\200\000\220\000\377\377\377\377\377\377\377\377\377\377\377\377\377\377\240\000\260\000\300\000\320\000\340\000\360\000\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\240\000\260\000\300\000\320\000\340\000\360\000\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.54,unique,110
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.54:
	.ascii	" at line "

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.55,unique,111
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.55:
	.asciz	"C:\\Users\\there\\.cargo\\registry\\src\\index.crates.io-1949cf8c6b5b557f\\serde_json-1.0.150\\src\\error.rs"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.56,unique,112
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.56:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.55
	.asciz	"c\000\000\000\000\000\000\000\367\001\000\000!\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.57,unique,113
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.57:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.55
	.asciz	"c\000\000\000\000\000\000\000\373\001\000\000\f\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.58,unique,114
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.58:
	.ascii	" column "

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.59,unique,115
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.59:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.55
	.asciz	"c\000\000\000\000\000\000\000\002\002\000\000!\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.60,unique,116
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.60:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.55
	.asciz	"c\000\000\000\000\000\000\000\013\002\000\000*\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.61,unique,117
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.61:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.55
	.asciz	"c\000\000\000\000\000\000\000\017\002\000\000,\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.62,unique,118
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.62:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.55
	.asciz	"c\000\000\000\000\000\000\000\024\002\000\000\t\000\000"

	.section	.rdata,"dr",one_only,_RNvNvXs3_NtNtCsavOST1yGCNT_10serde_json5value5indexNtB9_5ValueINtNtNtCs8xEFJqa6dYS_4core3ops5index5IndexpE5index4NULL,unique,119
	.globl	_RNvNvXs3_NtNtCsavOST1yGCNT_10serde_json5value5indexNtB9_5ValueINtNtNtCs8xEFJqa6dYS_4core3ops5index5IndexpE5index4NULL
	.p2align	3, 0x0
_RNvNvXs3_NtNtCsavOST1yGCNT_10serde_json5value5indexNtB9_5ValueINtNtNtCs8xEFJqa6dYS_4core3ops5index5IndexpE5index4NULL:
	.zero	1
	.zero	31

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63,unique,120
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63:
	.ascii	"fmt error"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.70,unique,121
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.70:
	.asciz	"C:\\Users\\there\\.cargo\\registry\\src\\index.crates.io-1949cf8c6b5b557f\\serde_json-1.0.150\\src\\value\\index.rs"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.77,unique,122
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.77:
	.ascii	"EOF while parsing a list"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.78,unique,123
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.78:
	.ascii	"EOF while parsing an object"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.79,unique,124
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.79:
	.ascii	"EOF while parsing a string"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.80,unique,125
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.80:
	.ascii	"EOF while parsing a value"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.81,unique,126
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.81:
	.ascii	"expected `:`"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.82,unique,127
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.82:
	.ascii	"expected `,` or `]`"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.83,unique,128
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.83:
	.ascii	"expected `,` or `}`"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.84,unique,129
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.84:
	.ascii	"expected ident"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.85,unique,130
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.85:
	.ascii	"expected value"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.86,unique,131
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.86:
	.ascii	"expected `\"`"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.87,unique,132
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.87:
	.ascii	"invalid escape"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.88,unique,133
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.88:
	.ascii	"invalid number"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.89,unique,134
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.89:
	.ascii	"number out of range"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.90,unique,135
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.90:
	.ascii	"invalid unicode code point"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.91,unique,136
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.91:
	.ascii	"control character (\\u0000-\\u001F) found while parsing a string"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.92,unique,137
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.92:
	.ascii	"key must be a string"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.93,unique,138
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.93:
	.ascii	"invalid value: expected key to be a number in quotes"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.94,unique,139
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.94:
	.ascii	"float key must be finite (got NaN or +/-inf)"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.95,unique,140
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.95:
	.ascii	"lone leading surrogate in hex escape"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.96,unique,141
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.96:
	.ascii	"trailing comma"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.97,unique,142
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.97:
	.ascii	"trailing characters"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.98,unique,143
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.98:
	.ascii	"unexpected end of hex escape"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.99,unique,144
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.99:
	.ascii	"recursion limit exceeded"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.100,unique,145
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.100:
	.ascii	"boolean"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.101,unique,146
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.101:
	.ascii	"number"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.102,unique,147
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.102:
	.ascii	"string"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.103,unique,148
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.103:
	.ascii	"array"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.104,unique,149
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.104:
	.ascii	"object"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.107,unique,150
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.107:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920
	.asciz	"b\000\000\000\000\000\000\000\\\002\000\000\023\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.108,unique,151
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.108:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920
	.asciz	"b\000\000\000\000\000\000\000n\002\000\000\031\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.109,unique,152
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.109:
	.asciz	"\006Error(\300\b, line: \300\n, column: \300\001)"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.110,unique,153
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.110:
	.asciz	"C:\\Users\\there\\.cargo\\registry\\src\\index.crates.io-1949cf8c6b5b557f\\itoa-1.0.18\\src\\lib.rs"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.111.llvm.16186315980599473920,unique,154
	.globl	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.111.llvm.16186315980599473920
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.111.llvm.16186315980599473920:
	.asciz	"\016invalid type: \300\013, expected \300"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.112.llvm.16186315980599473920,unique,155
	.globl	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.112.llvm.16186315980599473920
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.112.llvm.16186315980599473920:
	.asciz	"\017invalid value: \300\013, expected \300"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.113,unique,156
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.113:
	.asciz	"\020floating point `\300\001`"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.114,unique,157
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.114:
	.quad	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsfQUUnEvlYZE_5alloc6string6StringECsavOST1yGCNT_10serde_json
	.asciz	"\030\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_str
	.quad	_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write10write_char
	.quad	_RNvYNtNtCsfQUUnEvlYZE_5alloc6string6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_fmtCsavOST1yGCNT_10serde_json

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.115,unique,158
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.115:
	.ascii	"a Display implementation returned an error unexpectedly"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.116,unique,159
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.116:
	.asciz	"/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\alloc\\src\\string.rs"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.117,unique,160
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.117:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.116
	.asciz	"K\000\000\000\000\000\000\000\177\013\000\000\016\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.118,unique,161
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.118:
	.ascii	"Error"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.119,unique,162
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.119:
	.ascii	"inf"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.120,unique,163
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.120:
	.ascii	"-inf"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.121,unique,164
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.121:
	.ascii	"NaN"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.123,unique,165
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.123:
	.asciz	"\022cannot access key \300\t in JSON \300"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.124,unique,166
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.124:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.70
	.asciz	"i\000\000\000\000\000\000\000f\000\000\000\022\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.129,unique,167
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.129:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.110
	.asciz	"Z\000\000\000\000\000\000\000\274\000\000\000\001\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.130,unique,168
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.130:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.12
	.asciz	"_\000\000\000\000\000\000\000\241\000\000\000$\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.134,unique,169
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.134:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.14
	.asciz	"O\000\000\000\000\000\000\000\277\004\000\000$\000\000"

	.section	.rdata,"dr",one_only,_RNvNtCsavOST1yGCNT_10serde_json3ser6ESCAPE,unique,170
	.globl	_RNvNtCsavOST1yGCNT_10serde_json3ser6ESCAPE
_RNvNtCsavOST1yGCNT_10serde_json3ser6ESCAPE:
	.asciz	"uuuuuuuubtnufruuuuuuuuuuuuuuuuuu\000\000\"\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\\\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000"

	.section	.rdata,"dr",one_only,_RNvNvNtNtCsavOST1yGCNT_10serde_json3ser9Formatter17write_char_escape10HEX_DIGITS,unique,171
	.globl	_RNvNvNtNtCsavOST1yGCNT_10serde_json3ser9Formatter17write_char_escape10HEX_DIGITS
_RNvNvNtNtCsavOST1yGCNT_10serde_json3ser9Formatter17write_char_escape10HEX_DIGITS:
	.ascii	"0123456789abcdef"

	.section	.rdata,"dr",one_only,_RNvNtCsavOST1yGCNT_10serde_json2de5POW10,unique,172
	.globl	_RNvNtCsavOST1yGCNT_10serde_json2de5POW10
	.p2align	3, 0x0
_RNvNtCsavOST1yGCNT_10serde_json2de5POW10:
	.ascii	"\000\000\000\000\000\000\360?\000\000\000\000\000\000$@\000\000\000\000\000\000Y@\000\000\000\000\000@\217@\000\000\000\000\000\210\303@\000\000\000\000\000j\370@\000\000\000\000\200\204.A\000\000\000\000\320\022cA\000\000\000\000\204\327\227A\000\000\000\000e\315\315A\000\000\000 _\240\002B\000\000\000\350vH7B\000\000\000\242\224\032mB\000\000@\345\2340\242B\000\000\220\036\304\274\326B\000\0004&\365k\fC\000\200\3407y\303AC\000\240\330\205W4vC\000\310Ngm\301\253C\000=\221`\344X\341C@\214\265x\035\257\025DP\357\342\326\344\032KD\222\325M\006\317\360\200D\366J\341\307\002-\265D\264\235\331yCx\352D\221\002(,*\213 E5\0032\267\364\255TE\002\204\376\344q\331\211E\201\022\037/\347'\300E!\327\346\372\3401\364E\352\214\2409Y>)F$\260\b\210\357\215_F\027n\005\265\265\270\223F\234\311F\"\343\246\310F\003|\330\352\233\320\376F\202M\307raB3G\343 y\317\371\022hG\033iWC\270\027\236G\261\241\026*\323\316\322G\035J\234\364\207\202\007H\245\\\303\361)c=H\347\031\0327\372]rHa\240\340\304x\365\246Hy\310\030\366\326\262\334HL}\317Y\306\357\021I\236\\C\360\267kFI\3063T\354\245\006|I\\\240\264\263'\204\261Is\310\241\2401\345\345I\217:\312\b~^\033J\232d~\305\016\033QJ\300\375\335v\322a\205J0}\225\024G\272\272J>n\335ll\264\360J\316\311\024\210\207\341$KA\374\031j\351\031ZK\251=P\3421P\220K\023M\344Z>d\304KW`\235\361M}\371Km\270\004n\241\334/LD\363\302\344\344\351cL\025\260\363\035^\344\230L\033\234p\245u\035\317L\221af\207ir\003M\365\371?\351\003O8Mr\370\217\343\304bnMG\3739\016\273\375\242M\031z\310\321)\275\327M\237\230:Ft\254\rNd\237\344\253\310\213BN=\307\335\326\272.wN\f9\225\214i\372\254N\247C\335\367\201\034\342N\221\224\324u\242\243\026O\265\271I\023\213LLO\021\024\016\354\326\257\201O\026\231\021\247\314\033\266O[\377\325\320\277\242\353O\231\277\205\342\267E!P\177/'\333%\227UP_\373\360Q\357\374\212P\033\2356\223\025\336\300PbD\004\370\232\025\365P{U\005\266\001[*QmU\303\021\341x`Q\310*4V\031\227\224Qz5\301\253\337\274\311Ql\301X\313\013\026\000R\307\361.\276\216\0334R9\256\272mr\"iR\307Y)\t\017k\237R\035\330\271e\351\242\323R$N(\277\243\213\bS\255a\362\256\214\256>S\f}W\355\027-sSO\\\255\350]\370\247Sc\263\330bu\366\335S\036p\307]\t\272\022T%L9\265\213hGT.\237\207\242\256B}T}\303\224%\255I\262T\\\364\371n\030\334\346Tsq\270\212\036\223\034U\350F\263\026\363\333QU\242\030`\334\357R\206U\312\036x\323\253\347\273U?\023+d\313p\361U\016\3305=\376\314%V\022N\203\314=@[V\313\020\322\237&\b\221V\376\224\306G0J\305V=:\270Y\274\234\372Vf$\023\270\365\2410W\200\355\027&s\312dW\340\350\235\357\017\375\231W\214\261\302\365)>\320W\357]3s\264M\004Xk5\000\220!a9X\305B\000\364i\271oX\273)\2008\342\323\243X*4\240\306\332\310\330X5AHx\021\373\016Y\301(-\353\352\\CY\361r\370\245%4xY\255\217v\017/A\256Y\314\031\252i\275\350\342Y?\240\024\304\354\242\027ZO\310\031\365\247\213MZ2\0350\371Hw\202Z~$|7\033\025\267Z\236-[\005b\332\354Z\202\374XC}\b\"[\243;/\224\234\212V[\214\n;\271C-\214[\227\346\304SJ\234\301[= \266\350\\\003\366[M\250\343\"4\204+\\0I\316\225\2402a\\|\333A\273H\177\225\\[R\022\352\032\337\312\\ysK\322p\313\000]WP\336\006M\3764]m\344\225H\340=j]\304\256]-\254f\240]u\032\2658W\200\324]\022a\342\006m\240\t^\253|M$D\004@^\326\333`-U\005t^\314\022\271x\252\006\251^\177W\347\026UH\337^\257\226P.5\215\023_[\274\344y\202pH_r\353]\030\243\214~_'\263:\357\345\027\263_\361_\tk\337\335\347_\355\267\313EW\325\035`\364R\237\213V\245R`\261'\207.\254N\207`\235\361(:W\"\275`\002\227Y\204v5\362`\303\374o%\324\302&a\364\373\313.\211s\\ax}?\2755\310\221a\326\\\217,C:\306a\f4\263\367\323\310\373a\207\000\320z\204]1b\251\000\204\231\345\264eb\324\000\345\377\036\"\233b\204 \357_S\365\320b\245\350\3527\2502\005c\317\242\345ER\177:c\301\205\257k\223\217pc2g\233Fx\263\244c\376@BXV\340\331c\237h)\3675,\020d\306\302\363tC7Ddx\2630R\024EydV\340\274fY\226\257d6\f6\340\367\275\343dC\217C\330u\255\030e\024sTN\323\330Ne\354\307\364\020\204G\203e\350\3711\025e\031\270eax~Z\276\037\356e=\013\217\370\326\323\"f\f\316\262\266\314\210Wf\217\201_\344\377j\215f\371\260\273\356\337b\302f8\235j\352\227\373\366f\206D\005\345}\272,g\324J#\257\216\364ag\211\035\354Z\262q\226g\353$\247\361\036\016\314g\023w\bW\323\210\001h\327\224\312,\b\3535h\r:\3757\312ekhHD\376b\236\037\241hZ\325\275\373\205g\325h\261J\255zg\301\ni\257N\254\254\340\270@iZb\327\327\030\347ti\361:\315\r\337 \252i\326D\240h\213T\340i\fV\310B\256i\024j\217kz\323\031\204Ijs\006YH \345\177j\b\2447-4\357\263j\n\215\2058\001\353\350jL\360\246\206\301%\037k0V(\364\230wSk\273k21\177U\210k\252\006\177\375\336j\276k*do^\313\002\363k5=\0136~\303'l\202\f\216\303]\264]l\321\3078\232\272\220\222l\306\371\306@\3514\307l7\270\370\220#\002\375l#s\233:V!2m\353OB\311\253\251fm\346\343\222\273\026T\234mp\316;5\216\264\321m\f\302\212\302\261!\006n\217r-3\036\252;n\231g\374\337RJqn\177\201\373\227\347\234\245n\337a\372}!\004\333n,}\274\356\224\342\020ov\234k*:\033Eo\224\203\006\265\bbzo=\022$qE}\260o\314\026m\315\226\234\344o\177\\\310\200\274\303\031p\3179}\320U\032PpC\210\234D\353 \204pT\252\303\025&)\271p\351\2244\233os\357p\021\335\000\301%\250#qV\024A1/\222XqkY\221\375\272\266\216q\343\327z\33642\303q\334\215\031\026\302\376\367qS\361\237\233r\376-r\324\366C\241\007\277br\211\364\224\211\311n\227r\2531\372\353{J\315r\013_|s\215N\002s\315v[\3200\3426s\201Tr\004\275\232ls\320t\307\"\266\340\241s\004Ry\253\343X\326s\206\246W\226\034\357\013t\024\310\366\335quAt\030ztU\316\322ut\236\230\321\352\201G\253tc\377\3022\261\f\341t<\277s\177\335O\025u\013\257P\337\324\243Jugm\222\013e\246\200u\300\bwN\376\317\264u\361\312\024\342\375\003\352u\326\376L\255~B v\214>\240X\036STv/N\310\356\345g\211v\273azj\337\301\277v\025}\214\242+\331\363vZ\234/\213v\317(wp\203\373-T\003_w&2\275\234\024b\223w\260~\354\303\231:\310w\\\236\3474@I\376w\371\302\020!\310\3552x\270\363T):\251gx\2450\252\263\210\223\235xg^Jp5|\322x\001\366\\\314B\033\007y\2023t\177\023\342<y1\240\250/L\rry=\310\222;\237\220\246yMzw\n\3074\334yp\254\212f\374\240\021z\214W-\200;\tFzo\2558`\212\213{zel#|67\261z\177G,\033\004\205\345z^Y\367!E\346\032{\333\227:5\353\317P{\322=\211\002\346\003\205{F\215+\203\337D\272{L8\373\261\013k\360{_\006z\236\316\205$|\366\207\030FB\247Y|\372T\317k\211\b\220|8*\303\306\253\n\304|\307\364s\270V\r\371|\370\361\220f\254P/};\227\032\300k\222c}\n=!\260\006w\230}L\214)\\\310\224\316}\260\367\2319\375\034\003~\234u\000\210<\3447~\003\223\000\252K\335m~\342[@JO\252\242~\332r\320\034\343T\327~\220\217\004\344\033*\r\177\272\331\202nQ:B\177)\220#\312\345\310v\1773t\254<\037{\254\177\240\310\353\205\363\314\341\177"

	.section	.data,"dw",one_only,__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920,unique,173
	.globl	__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920
	.p2align	3, 0x0
__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920

	.section	.data,"dw",one_only,__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920,unique,174
	.globl	__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920
	.p2align	3, 0x0
__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920

	.section	.data,"dw",one_only,__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.48.llvm.16186315980599473920,unique,175
	.globl	__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.48.llvm.16186315980599473920
	.p2align	3, 0x0
__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.48.llvm.16186315980599473920:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.48.llvm.16186315980599473920

	.section	.data,"dw",one_only,__imp__RNvNtCsavOST1yGCNT_10serde_json4read4HEX0,unique,176
	.globl	__imp__RNvNtCsavOST1yGCNT_10serde_json4read4HEX0
	.p2align	3, 0x0
__imp__RNvNtCsavOST1yGCNT_10serde_json4read4HEX0:
	.quad	_RNvNtCsavOST1yGCNT_10serde_json4read4HEX0

	.section	.data,"dw",one_only,__imp__RNvNtCsavOST1yGCNT_10serde_json4read4HEX1,unique,177
	.globl	__imp__RNvNtCsavOST1yGCNT_10serde_json4read4HEX1
	.p2align	3, 0x0
__imp__RNvNtCsavOST1yGCNT_10serde_json4read4HEX1:
	.quad	_RNvNtCsavOST1yGCNT_10serde_json4read4HEX1

	.section	.data,"dw",one_only,__imp__RNvNvXs3_NtNtCsavOST1yGCNT_10serde_json5value5indexNtB9_5ValueINtNtNtCs8xEFJqa6dYS_4core3ops5index5IndexpE5index4NULL,unique,178
	.globl	__imp__RNvNvXs3_NtNtCsavOST1yGCNT_10serde_json5value5indexNtB9_5ValueINtNtNtCs8xEFJqa6dYS_4core3ops5index5IndexpE5index4NULL
	.p2align	3, 0x0
__imp__RNvNvXs3_NtNtCsavOST1yGCNT_10serde_json5value5indexNtB9_5ValueINtNtNtCs8xEFJqa6dYS_4core3ops5index5IndexpE5index4NULL:
	.quad	_RNvNvXs3_NtNtCsavOST1yGCNT_10serde_json5value5indexNtB9_5ValueINtNtNtCs8xEFJqa6dYS_4core3ops5index5IndexpE5index4NULL

	.section	.data,"dw",one_only,__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.111.llvm.16186315980599473920,unique,179
	.globl	__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.111.llvm.16186315980599473920
	.p2align	3, 0x0
__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.111.llvm.16186315980599473920:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.111.llvm.16186315980599473920

	.section	.data,"dw",one_only,__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.112.llvm.16186315980599473920,unique,180
	.globl	__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.112.llvm.16186315980599473920
	.p2align	3, 0x0
__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.112.llvm.16186315980599473920:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.112.llvm.16186315980599473920

	.section	.data,"dw",one_only,__imp__RNvNtCsavOST1yGCNT_10serde_json3ser6ESCAPE,unique,181
	.globl	__imp__RNvNtCsavOST1yGCNT_10serde_json3ser6ESCAPE
	.p2align	3, 0x0
__imp__RNvNtCsavOST1yGCNT_10serde_json3ser6ESCAPE:
	.quad	_RNvNtCsavOST1yGCNT_10serde_json3ser6ESCAPE

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCsavOST1yGCNT_10serde_json3ser9Formatter17write_char_escape10HEX_DIGITS,unique,182
	.globl	__imp__RNvNvNtNtCsavOST1yGCNT_10serde_json3ser9Formatter17write_char_escape10HEX_DIGITS
	.p2align	3, 0x0
__imp__RNvNvNtNtCsavOST1yGCNT_10serde_json3ser9Formatter17write_char_escape10HEX_DIGITS:
	.quad	_RNvNvNtNtCsavOST1yGCNT_10serde_json3ser9Formatter17write_char_escape10HEX_DIGITS

	.section	.data,"dw",one_only,__imp__RNvNtCsavOST1yGCNT_10serde_json2de5POW10,unique,183
	.globl	__imp__RNvNtCsavOST1yGCNT_10serde_json2de5POW10
	.p2align	3, 0x0
__imp__RNvNtCsavOST1yGCNT_10serde_json2de5POW10:
	.quad	_RNvNtCsavOST1yGCNT_10serde_json2de5POW10

	.section	.debug$S,"dr"
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp131-.Ltmp130
.Ltmp130:
	.short	.Ltmp133-.Ltmp132
.Ltmp132:
	.short	4353
	.long	0
	.asciz	"S:\\GTOpen-research\\postflop-gpu-20261016\\build\\release\\deps\\postflop_autoresearch-ba6a3e8216b3a7e5.serde_json-83a0670a02a34a4d.serde_json.7a74452f5594281f-cgu.0.rcgu.o.rcgu.o"
	.p2align	2, 0x0
.Ltmp133:
	.short	.Ltmp135-.Ltmp134
.Ltmp134:
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
.Ltmp135:
.Ltmp131:
	.p2align	2, 0x0
	.cv_filechecksums
	.cv_stringtable
	.long	241
	.long	.Ltmp137-.Ltmp136
.Ltmp136:
	.short	.Ltmp139-.Ltmp138
.Ltmp138:
	.short	4428
	.long	4099
	.p2align	2, 0x0
.Ltmp139:
.Ltmp137:
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
