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
	.section	.text$unlikely,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read20parse_unicode_escapeNtB2_9SliceReadEB4_,unique,5
	.p2align	4
_RINvNtCsavOST1yGCNT_10serde_json4read20parse_unicode_escapeNtB2_9SliceReadEB4_:
.Lfunc_begin5:
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
	jb	.LBB5_42
	movq	%rdx, %rsi
	movq	%rcx, %rdi
	cmpq	$3, %rax
	jbe	.LBB5_4
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
	js	.LBB5_6
	movw	%ax, 42(%rsp)
	movw	$0, 40(%rsp)
	cmpw	$1, 40(%rsp)
	je	.LBB5_5
	jmp	.LBB5_7
.LBB5_4:
	movq	%rbx, 16(%rdi)
	movq	$4, 56(%rsp)
	leaq	40(%rsp), %rcx
	leaq	56(%rsp), %r8
	movq	%rdi, %rdx
	callq	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_
	movq	%rbx, %r14
	cmpw	$1, 40(%rsp)
	jne	.LBB5_7
	jmp	.LBB5_5
.LBB5_6:
	movq	$12, 56(%rsp)
	leaq	40(%rsp), %rcx
	leaq	56(%rsp), %r8
	movq	%rdi, %rdx
	callq	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_
	cmpw	$1, 40(%rsp)
	je	.LBB5_5
.LBB5_7:
	movzwl	42(%rsp), %r15d
	movl	%r15d, %eax
	andl	$64512, %eax
	cmpl	$56320, %eax
	jne	.LBB5_9
.LBB5_8:
	movq	$20, 56(%rsp)
	jmp	.LBB5_32
.LBB5_9:
	leal	9216(%r15), %eax
	movzwl	%ax, %eax
	cmpl	$64512, %eax
	jae	.LBB5_14
	movzwl	%r15w, %edi
	cmpl	$128, %edi
	jae	.LBB5_16
	movq	16(%rsi), %rdi
	cmpq	(%rsi), %rdi
	jne	.LBB5_13
	movq	%rsi, %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVechE8grow_oneB7_
.LBB5_13:
	movq	8(%rsi), %rax
	movb	%r15b, (%rax,%rdi)
	incq	%rdi
	movq	%rdi, 16(%rsi)
	xorl	%eax, %eax
	jmp	.LBB5_33
.LBB5_14:
	movq	(%rdi), %r12
	cmpq	%rbx, %r14
	jae	.LBB5_19
	movzbl	(%r12,%r14), %ecx
	leaq	1(%r14), %rax
	movq	%rax, 16(%rdi)
	cmpb	$92, %cl
	je	.LBB5_22
	jmp	.LBB5_31
.LBB5_16:
	movq	(%rsi), %rax
	movq	16(%rsi), %rdx
	subq	%rdx, %rax
	cmpq	$3, %rax
	jbe	.LBB5_43
	movq	8(%rsi), %rax
	addq	%rdx, %rax
	cmpl	$2048, %edi
	jae	.LBB5_44
.LBB5_18:
	movl	%r15d, %ecx
	shrl	$6, %ecx
	orb	$-64, %cl
	movl	$2, %r8d
	jmp	.LBB5_45
.LBB5_19:
	movq	$4, 56(%rsp)
	leaq	40(%rsp), %rcx
	leaq	56(%rsp), %r8
	movq	%rdi, %rdx
	callq	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_
	cmpb	$1, 40(%rsp)
	je	.LBB5_5
	movzbl	41(%rsp), %ecx
	leaq	1(%r14), %rax
	movq	%rax, 16(%rdi)
	cmpb	$92, %cl
	jne	.LBB5_31
.LBB5_22:
	cmpq	%rbx, %rax
	jae	.LBB5_28
	movzbl	(%r12,%rax), %eax
	leaq	2(%r14), %rcx
	movq	%rcx, 16(%rdi)
	cmpb	$117, %al
	jne	.LBB5_31
.LBB5_24:
	movq	%rbx, %rax
	subq	%rcx, %rax
	jb	.LBB5_47
	cmpq	$3, %rax
	jbe	.LBB5_34
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
	js	.LBB5_35
	movw	%ax, 42(%rsp)
	movw	$0, 40(%rsp)
	jmp	.LBB5_37
.LBB5_28:
	movq	$4, 56(%rsp)
	leaq	40(%rsp), %rcx
	leaq	56(%rsp), %r8
	movq	%rdi, %rdx
	callq	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_
	cmpb	$0, 40(%rsp)
	jne	.LBB5_5
	movzbl	41(%rsp), %eax
	leaq	2(%r14), %rcx
	movq	%rcx, 16(%rdi)
	cmpb	$117, %al
	je	.LBB5_24
.LBB5_31:
	movq	$23, 56(%rsp)
.LBB5_32:
	leaq	56(%rsp), %rdx
	movq	%rdi, %rcx
	callq	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_
	jmp	.LBB5_33
.LBB5_34:
	movq	%rbx, 16(%rdi)
	movq	$4, 56(%rsp)
	jmp	.LBB5_36
.LBB5_35:
	movq	$12, 56(%rsp)
.LBB5_36:
	leaq	40(%rsp), %rcx
	leaq	56(%rsp), %r8
	movq	%rdi, %rdx
	callq	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_
.LBB5_37:
	cmpb	$0, 40(%rsp)
	je	.LBB5_39
.LBB5_5:
	movq	48(%rsp), %rax
.LBB5_33:
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
.LBB5_39:
	movzwl	42(%rsp), %ebx
	leal	8192(%rbx), %eax
	movzwl	%ax, %eax
	cmpl	$64512, %eax
	jb	.LBB5_8
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
	jbe	.LBB5_48
.LBB5_41:
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
	jmp	.LBB5_46
.LBB5_42:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.108(%rip), %r9
	movq	%r14, %rcx
	movq	%rbx, %rdx
	movq	%rbx, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	ud2
.LBB5_43:
	movl	$4, %r8d
	movq	%rsi, %rcx
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECsavOST1yGCNT_10serde_json
	movq	16(%rsi), %rdx
	movq	8(%rsi), %rax
	addq	%rdx, %rax
	cmpl	$2048, %edi
	jb	.LBB5_18
.LBB5_44:
	movl	%edi, %ecx
	shrl	$12, %ecx
	orb	$-32, %cl
	shrl	$6, %edi
	andb	$63, %dil
	orb	$-128, %dil
	movb	%dil, 1(%rax)
	movl	$3, %r8d
.LBB5_45:
	movb	%cl, (%rax)
	andb	$63, %r15b
	orb	$-128, %r15b
	movb	%r15b, -1(%rax,%r8)
	addq	%r8, %rdx
.LBB5_46:
	movq	%rdx, 16(%rsi)
	xorl	%eax, %eax
	jmp	.LBB5_33
.LBB5_47:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.108(%rip), %r9
	movq	%rbx, %rdx
	movq	%rbx, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	ud2
.LBB5_48:
	movl	$4, %r8d
	movq	%rsi, %rcx
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECsavOST1yGCNT_10serde_json
	movq	16(%rsi), %rdx
	jmp	.LBB5_41
.Lfunc_end5:
	.seh_endproc

	.def	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_,unique,6
	.p2align	4
_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_:
.Lfunc_begin6:
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
	ja	.LBB6_9
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
	jne	.LBB6_3
	subq	%r14, %rdx
	leaq	1(%rdx), %r15
	cmpq	%rbx, %rdx
	jb	.LBB6_4
	movb	$1, -1(%rbp)
.Ltmp6:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920(%rip), %r9
	xorl	%ecx, %ecx
	movq	%r15, %rdx
	movq	%rbx, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	nop
.Ltmp7:
	jmp	.LBB6_10
.LBB6_3:
	xorl	%r15d, %r15d
.LBB6_4:
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
.LBB6_9:
	movb	$1, -1(%rbp)
.Ltmp12:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.48.llvm.16186315980599473920(%rip), %r9
	xorl	%ecx, %ecx
	movq	%rdi, %rdx
	movq	%rbx, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	nop
.Ltmp13:
.LBB6_10:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_@IMGREL
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_,unique,6
	.seh_endproc
	.def	"?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_@4HA":
.seh_proc "?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_@4HA"
.LBB6_11:
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
	jne	.LBB6_12
.LBB6_13:
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
.LBB6_12:
	movq	-16(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5error9ErrorCodeEBF_
	jmp	.LBB6_13
.Lfunc_end6:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_,unique,6
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
	.long	.Lfunc_begin6@IMGREL
	.long	-1
	.long	.Ltmp4@IMGREL
	.long	0
	.long	.Ltmp13@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_,unique,6

	.def	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_,unique,7
	.p2align	4
_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_:
.Lfunc_begin7:
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
	ja	.LBB7_9
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
	jne	.LBB7_3
	subq	%r14, %rdx
	leaq	1(%rdx), %r15
	cmpq	%rbx, %rdx
	jb	.LBB7_4
	movb	$1, -1(%rbp)
.Ltmp16:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920(%rip), %r9
	xorl	%ecx, %ecx
	movq	%r15, %rdx
	movq	%rbx, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	nop
.Ltmp17:
	jmp	.LBB7_10
.LBB7_3:
	xorl	%r15d, %r15d
.LBB7_4:
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
.LBB7_9:
	movb	$1, -1(%rbp)
.Ltmp22:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.48.llvm.16186315980599473920(%rip), %r9
	xorl	%ecx, %ecx
	movq	%rdi, %rdx
	movq	%rbx, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	nop
.Ltmp23:
.LBB7_10:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_@IMGREL
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_,unique,7
	.seh_endproc
	.def	"?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_@4HA":
.seh_proc "?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_@4HA"
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
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_,unique,7
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
	.long	.Lfunc_begin7@IMGREL
	.long	-1
	.long	.Ltmp14@IMGREL
	.long	0
	.long	.Ltmp23@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_,unique,7

	.def	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_,unique,8
	.p2align	4
_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_:
.Lfunc_begin8:
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
	ja	.LBB8_9
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
	jne	.LBB8_3
	subq	%r14, %rdx
	leaq	1(%rdx), %r15
	cmpq	%rbx, %rdx
	jb	.LBB8_4
	movb	$1, -1(%rbp)
.Ltmp26:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920(%rip), %r9
	xorl	%ecx, %ecx
	movq	%r15, %rdx
	movq	%rbx, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	nop
.Ltmp27:
	jmp	.LBB8_10
.LBB8_3:
	xorl	%r15d, %r15d
.LBB8_4:
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
.LBB8_9:
	movb	$1, -1(%rbp)
.Ltmp32:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.48.llvm.16186315980599473920(%rip), %r9
	xorl	%ecx, %ecx
	movq	%rdi, %rdx
	movq	%rbx, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	nop
.Ltmp33:
.LBB8_10:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_@IMGREL
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_,unique,8
	.seh_endproc
	.def	"?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_@4HA":
.seh_proc "?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_@4HA"
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
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_,unique,8
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
	.long	.Lfunc_begin8@IMGREL
	.long	-1
	.long	.Ltmp24@IMGREL
	.long	0
	.long	.Ltmp33@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_,unique,8

	.def	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_,unique,9
	.p2align	4
_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_:
.Lfunc_begin9:
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
	ja	.LBB9_9
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
	jne	.LBB9_3
	subq	%rbx, %rdx
	leaq	1(%rdx), %r14
	cmpq	%rdi, %rdx
	jb	.LBB9_4
	movb	$1, -9(%rbp)
.Ltmp36:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920(%rip), %r9
	xorl	%ecx, %ecx
	movq	%r14, %rdx
	movq	%rdi, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	nop
.Ltmp37:
	jmp	.LBB9_10
.LBB9_3:
	xorl	%r14d, %r14d
.LBB9_4:
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
.LBB9_9:
	movb	$1, -9(%rbp)
.Ltmp42:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.48.llvm.16186315980599473920(%rip), %r9
	xorl	%ecx, %ecx
	movq	%rsi, %rdx
	movq	%rdi, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	nop
.Ltmp43:
.LBB9_10:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_@IMGREL
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_,unique,9
	.seh_endproc
	.def	"?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_@4HA":
.seh_proc "?dtor$11@?0?_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_@4HA"
.LBB9_11:
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
	jne	.LBB9_12
.LBB9_13:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.LBB9_12:
	movq	-24(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5error9ErrorCodeEBF_
	jmp	.LBB9_13
.Lfunc_end9:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_,unique,9
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
	.long	.Lfunc_begin9@IMGREL
	.long	-1
	.long	.Ltmp34@IMGREL
	.long	0
	.long	.Ltmp43@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_,unique,9

	.def	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECsavOST1yGCNT_10serde_json;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECsavOST1yGCNT_10serde_json,unique,10
	.p2align	4
_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECsavOST1yGCNT_10serde_json:
.Lfunc_begin10:
.seh_proc _RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECsavOST1yGCNT_10serde_json
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	addq	%r8, %rdx
	jb	.LBB10_1
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
	je	.LBB10_3
	movq	56(%rsp), %rax
	movq	%rax, 8(%rsi)
	movq	%rdi, (%rsi)
	.seh_startepilogue
	addq	$72, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB10_1:
	xorl	%ecx, %ecx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.LBB10_3:
	movq	56(%rsp), %rcx
	movq	64(%rsp), %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.Lfunc_end10:
	.seh_endproc

	.def	_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_,unique,11
	.p2align	4
_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_:
.Lfunc_begin11:
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
	leaq	.LJTI11_0(%rip), %rdx
	movslq	(%rdx,%rax,4), %rax
	addq	%rdx, %rax
	movq	%rsi, -8(%rbp)
	jmpq	*%rax
.LBB11_1:
	movq	(%rsi), %rax
	movq	(%rax), %r14
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.33(%rip), %rdx
	movl	$4, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB11_211
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdi
	leaq	.LJTI11_16(%rip), %r15
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.33(%rip), %rbx
	xorl	%esi, %esi
	movl	$255, %r12d
	jmp	.LBB11_5
	.p2align	4
.LBB11_3:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB11_180
.LBB11_4:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movl	$4, %r8d
	movq	%rbx, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB11_212
.LBB11_5:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rdi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB11_6:
	cmpb	$35, 16(%rax)
	je	.LBB11_4
	jmp	.LBB11_180
	.p2align	4
.LBB11_7:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB11_4
	jmp	.LBB11_180
	.p2align	4
.LBB11_8:
	cmpb	$35, 31(%rax)
	jne	.LBB11_180
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB11_4
.LBB11_10:
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
	je	.LBB11_44
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rbx
	leaq	.LJTI11_6(%rip), %r13
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.25(%rip), %r14
	movl	$255, %esi
	jmp	.LBB11_14
	.p2align	4
.LBB11_12:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r12
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r12, %rax
	testb	%cl, %cl
	je	.LBB11_180
.LBB11_13:
	movq	(%r15), %rcx
	movq	8(%r15), %rax
	movl	$1, %r8d
	movq	%r14, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB11_44
.LBB11_14:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rbx, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r13,%rcx,4), %rcx
	addq	%r13, %rcx
	jmpq	*%rcx
.LBB11_15:
	cmpb	$35, 16(%rax)
	je	.LBB11_13
	jmp	.LBB11_180
	.p2align	4
.LBB11_16:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%esi, %ecx
	cmpb	$35, %cl
	je	.LBB11_13
	jmp	.LBB11_180
	.p2align	4
.LBB11_17:
	cmpb	$35, 31(%rax)
	jne	.LBB11_180
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB11_13
.LBB11_19:
	movq	(%rsi), %rbx
	movq	8(%rcx), %rax
	cmpq	$2, %rax
	je	.LBB11_89
	cmpl	$1, %eax
	jne	.LBB11_99
	movq	16(%rcx), %rsi
	movq	%rsi, %rcx
	negq	%rcx
	cmovsq	%rsi, %rcx
	leaq	-80(%rbp), %rdx
	callq	_RNvXsu_Cs1KvuFdKMjOj_4itoayNtB5_8Unsigned3fmt
	testq	%rsi, %rsi
	js	.LBB11_195
	cmpq	$20, %rax
	je	.LBB11_211
	movl	$20, %esi
	movq	%rax, %rcx
	jmp	.LBB11_197
.LBB11_24:
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
.LBB11_25:
	movq	(%rsi), %rax
	movq	(%rax), %r14
	cmpb	$0, 1(%rcx)
	je	.LBB11_77
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.32(%rip), %rdx
	movl	$4, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB11_211
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdi
	leaq	.LJTI11_15(%rip), %r15
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.32(%rip), %rbx
	xorl	%esi, %esi
	movl	$255, %r12d
	jmp	.LBB11_30
	.p2align	4
.LBB11_28:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB11_180
.LBB11_29:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movl	$4, %r8d
	movq	%rbx, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB11_212
.LBB11_30:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rdi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB11_31:
	cmpb	$35, 16(%rax)
	je	.LBB11_29
	jmp	.LBB11_180
	.p2align	4
.LBB11_32:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB11_29
	jmp	.LBB11_180
	.p2align	4
.LBB11_33:
	cmpb	$35, 31(%rax)
	jne	.LBB11_180
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB11_29
.LBB11_35:
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
	je	.LBB11_54
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdi
	leaq	.LJTI11_1(%rip), %r12
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.26(%rip), %rbx
	movl	$255, %r13d
	jmp	.LBB11_39
	.p2align	4
.LBB11_37:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %rsi
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%rsi, %rax
	movq	-8(%rbp), %rsi
	testb	%cl, %cl
	je	.LBB11_180
.LBB11_38:
	movq	(%r15), %rcx
	movq	8(%r15), %rax
	movl	$1, %r8d
	movq	%rbx, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB11_54
.LBB11_39:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rdi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r12,%rcx,4), %rcx
	addq	%r12, %rcx
	jmpq	*%rcx
.LBB11_40:
	cmpb	$35, 16(%rax)
	je	.LBB11_38
	jmp	.LBB11_180
	.p2align	4
.LBB11_41:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r13d, %ecx
	cmpb	$35, %cl
	je	.LBB11_38
	jmp	.LBB11_180
	.p2align	4
.LBB11_42:
	cmpb	$35, 31(%rax)
	jne	.LBB11_180
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB11_38
.LBB11_44:
	cmpq	$0, -16(%rbp)
	setne	%r15b
	jne	.LBB11_64
	movq	-24(%rbp), %rax
	movq	(%rax), %r12
	movq	(%r12), %rcx
	movq	8(%r12), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.29(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB11_64
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rbx
	leaq	.LJTI11_7(%rip), %r13
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.29(%rip), %r14
	jmp	.LBB11_49
	.p2align	4
.LBB11_47:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %rsi
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%rsi, %rax
	testb	%cl, %cl
	je	.LBB11_180
.LBB11_48:
	movq	(%r12), %rcx
	movq	8(%r12), %rax
	movl	$1, %r8d
	movq	%r14, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB11_64
.LBB11_49:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rbx, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r13,%rcx,4), %rcx
	addq	%r13, %rcx
	jmpq	*%rcx
.LBB11_50:
	cmpb	$35, 16(%rax)
	je	.LBB11_48
	jmp	.LBB11_180
	.p2align	4
.LBB11_51:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	movl	$255, %edx
	cmovael	%edx, %ecx
	cmpb	$35, %cl
	je	.LBB11_48
	jmp	.LBB11_180
	.p2align	4
.LBB11_52:
	cmpb	$35, 31(%rax)
	jne	.LBB11_180
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB11_48
.LBB11_54:
	movb	$1, %cl
	movq	-16(%rbp), %rdi
	testq	%rdi, %rdi
	jne	.LBB11_123
	movq	(%r14), %r14
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.24(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB11_121
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdi
	leaq	.LJTI11_2(%rip), %r15
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.24(%rip), %rbx
	movl	$255, %r12d
	jmp	.LBB11_59
	.p2align	4
.LBB11_57:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %rsi
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%rsi, %rax
	movq	-8(%rbp), %rsi
	testb	%cl, %cl
	je	.LBB11_180
.LBB11_58:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movl	$1, %r8d
	movq	%rbx, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB11_122
.LBB11_59:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rdi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB11_60:
	cmpb	$35, 16(%rax)
	je	.LBB11_58
	jmp	.LBB11_180
	.p2align	4
.LBB11_61:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB11_58
	jmp	.LBB11_180
	.p2align	4
.LBB11_62:
	cmpb	$35, 31(%rax)
	jne	.LBB11_180
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB11_58
.LBB11_64:
	movq	-16(%rbp), %rax
	movq	%rax, %r12
	shlq	$5, %r12
	addq	%rdi, %r12
	testq	%rax, %rax
	sete	%cl
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.34(%rip), %rbx
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %r14
	leaq	.LJTI11_8(%rip), %rsi
	jmp	.LBB11_66
	.p2align	4
.LBB11_65:
	leaq	32(%rdi), %r13
	movq	%rdi, %rcx
	movq	-8(%rbp), %rdx
	callq	_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_
	xorl	%r15d, %r15d
	movl	$0, %ecx
	movq	%r13, %rdi
	testq	%rax, %rax
	jne	.LBB11_88
.LBB11_66:
	cmpq	%r12, %rdi
	je	.LBB11_86
	testb	$1, %r15b
	jne	.LBB11_65
	movq	-8(%rbp), %rax
	movq	(%rax), %rax
	movq	(%rax), %r15
	jmp	.LBB11_70
	.p2align	4
.LBB11_69:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB11_180
.LBB11_70:
	movq	(%r15), %rcx
	movq	8(%r15), %rax
	movl	$1, %r8d
	movq	%rbx, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB11_65
	movl	$9, %r8d
	movb	$41, %cl
	movq	%r14, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%rsi,%rcx,4), %rcx
	addq	%rsi, %rcx
	jmpq	*%rcx
.LBB11_72:
	cmpb	$35, 16(%rax)
	je	.LBB11_70
	jmp	.LBB11_180
	.p2align	4
.LBB11_73:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	movl	$255, %edx
	cmovael	%edx, %ecx
	cmpb	$35, %cl
	je	.LBB11_70
	jmp	.LBB11_180
	.p2align	4
.LBB11_74:
	cmpb	$35, 31(%rax)
	jne	.LBB11_180
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB11_70
.LBB11_77:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.31(%rip), %rdx
	movl	$5, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB11_211
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdi
	leaq	.LJTI11_14(%rip), %r15
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.31(%rip), %rbx
	xorl	%esi, %esi
	movl	$255, %r12d
	jmp	.LBB11_81
	.p2align	4
.LBB11_79:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB11_180
.LBB11_80:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movl	$5, %r8d
	movq	%rbx, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB11_212
.LBB11_81:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rdi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB11_82:
	cmpb	$35, 16(%rax)
	je	.LBB11_80
	jmp	.LBB11_180
	.p2align	4
.LBB11_83:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB11_80
	jmp	.LBB11_180
	.p2align	4
.LBB11_84:
	cmpb	$35, 31(%rax)
	jne	.LBB11_180
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB11_80
.LBB11_86:
	testb	$1, %cl
	jne	.LBB11_211
	movq	-8(%rbp), %rax
	movq	(%rax), %rax
	movq	(%rax), %r14
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.29(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB11_211
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdi
	leaq	.LJTI11_9(%rip), %r15
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.29(%rip), %rbx
	xorl	%esi, %esi
	movl	$255, %r12d
	jmp	.LBB11_116
.LBB11_114:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB11_180
.LBB11_115:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movl	$1, %r8d
	movq	%rbx, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB11_212
.LBB11_116:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rdi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB11_117:
	cmpb	$35, 16(%rax)
	je	.LBB11_115
	jmp	.LBB11_180
.LBB11_118:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB11_115
	jmp	.LBB11_180
.LBB11_119:
	cmpb	$35, 31(%rax)
	jne	.LBB11_180
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB11_115
.LBB11_89:
	movq	16(%rcx), %xmm0
	movq	%xmm0, %rax
	movabsq	$9223372036854775807, %rcx
	andq	%rax, %rcx
	movabsq	$9218868437227405312, %rax
	cmpq	%rax, %rcx
	jl	.LBB11_184
	movq	(%rbx), %r14
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.33(%rip), %rdx
	movl	$4, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB11_211
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdi
	leaq	.LJTI11_11(%rip), %r15
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.33(%rip), %rbx
	xorl	%esi, %esi
	movl	$255, %r12d
	jmp	.LBB11_94
.LBB11_92:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB11_180
.LBB11_93:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movl	$4, %r8d
	movq	%rbx, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB11_212
.LBB11_94:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rdi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB11_95:
	cmpb	$35, 16(%rax)
	je	.LBB11_93
	jmp	.LBB11_180
.LBB11_96:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB11_93
	jmp	.LBB11_180
.LBB11_97:
	cmpb	$35, 31(%rax)
	jne	.LBB11_180
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB11_93
.LBB11_99:
	movq	16(%rcx), %rcx
	leaq	-80(%rbp), %rdx
	callq	_RNvXsu_Cs1KvuFdKMjOj_4itoayNtB5_8Unsigned3fmt
	movq	%rax, %rsi
	subq	$20, %rsi
	je	.LBB11_211
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
	je	.LBB11_211
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rbx
	leaq	.LJTI11_13(%rip), %r15
	movl	$255, %r12d
	jmp	.LBB11_104
.LBB11_102:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB11_213
.LBB11_103:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movq	%rdi, %rdx
	movq	%rsi, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB11_211
.LBB11_104:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rbx, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB11_105:
	cmpb	$35, 16(%rax)
	je	.LBB11_103
	jmp	.LBB11_213
.LBB11_106:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB11_103
	jmp	.LBB11_213
.LBB11_107:
	cmpb	$35, 31(%rax)
	jne	.LBB11_213
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB11_103
.LBB11_121:
	xorl	%ecx, %ecx
	jmp	.LBB11_123
.LBB11_122:
	xorl	%ecx, %ecx
	movq	-16(%rbp), %rdi
.LBB11_123:
	movq	-24(%rbp), %rax
	movq	8(%rax), %rdx
	movq	16(%rax), %r13
	testq	%rdx, %rdx
	cmoveq	%rdx, %rdi
	setne	%r8b
	xorl	%r15d, %r15d
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rbx
	leaq	.LJTI11_4(%rip), %r14
	jmp	.LBB11_125
	.p2align	4
.LBB11_124:
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
	jne	.LBB11_88
.LBB11_125:
	subq	$1, %rdi
	jb	.LBB11_170
	testb	$1, %r8b
	je	.LBB11_216
	testq	%r15, %r15
	je	.LBB11_130
	movq	%rdi, -16(%rbp)
	movzwl	626(%r15), %eax
	cmpq	%rax, %r13
	jae	.LBB11_139
.LBB11_129:
	movq	%r15, %r12
	jmp	.LBB11_141
	.p2align	4
.LBB11_130:
	testq	%r13, %r13
	je	.LBB11_135
	movq	%r13, %rax
	movq	%rdx, %r15
	andq	$7, %rax
	je	.LBB11_136
	xorl	%edx, %edx
	.p2align	4
.LBB11_133:
	movq	632(%r15), %r15
	incq	%rdx
	cmpq	%rdx, %rax
	jne	.LBB11_133
	movq	%r13, %rax
	subq	%rdx, %rax
	cmpq	$8, %r13
	jae	.LBB11_137
	jmp	.LBB11_138
.LBB11_135:
	movq	%rdx, %r15
	jmp	.LBB11_138
.LBB11_136:
	movq	%r13, %rax
	cmpq	$8, %r13
	jb	.LBB11_138
	.p2align	4
.LBB11_137:
	movq	632(%r15), %rdx
	movq	632(%rdx), %rdx
	movq	632(%rdx), %rdx
	movq	632(%rdx), %rdx
	movq	632(%rdx), %rdx
	movq	632(%rdx), %rdx
	movq	632(%rdx), %rdx
	movq	632(%rdx), %r15
	addq	$-8, %rax
	jne	.LBB11_137
.LBB11_138:
	xorl	%r13d, %r13d
	xorl	%edx, %edx
	movq	%rdi, -16(%rbp)
	movzwl	626(%r15), %eax
	cmpq	%rax, %r13
	jb	.LBB11_129
	.p2align	4
.LBB11_139:
	movq	352(%r15), %r12
	testq	%r12, %r12
	je	.LBB11_214
	incq	%rdx
	movzwl	624(%r15), %r13d
	movq	%r12, %r15
	cmpw	626(%r12), %r13w
	jae	.LBB11_139
.LBB11_141:
	testq	%rdx, %rdx
	je	.LBB11_146
	leaq	(%r12,%r13,8), %rax
	addq	$640, %rax
	movq	%rdx, %r8
	andq	$7, %r8
	je	.LBB11_147
	xorl	%r9d, %r9d
	.p2align	4
.LBB11_144:
	movq	(%rax), %r15
	leaq	632(%r15), %rax
	incq	%r9
	cmpq	%r9, %r8
	jne	.LBB11_144
	movq	%rdx, %r8
	subq	%r9, %r8
	cmpq	$8, %rdx
	jb	.LBB11_150
	.p2align	4
.LBB11_149:
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
	jne	.LBB11_149
.LBB11_150:
	movq	$0, -32(%rbp)
	jmp	.LBB11_151
	.p2align	4
.LBB11_146:
	leaq	1(%r13), %rax
	movq	%rax, -32(%rbp)
	movq	%r12, %r15
.LBB11_151:
	leaq	(,%r13,2), %rax
	addq	%r13, %rax
	movq	368(%r12,%rax,8), %rdx
	movq	%rdx, -24(%rbp)
	movq	376(%r12,%rax,8), %rax
	movq	%rax, -40(%rbp)
	cmpb	$1, %cl
	jne	.LBB11_162
.LBB11_152:
	movq	-8(%rbp), %rsi
	movq	(%rsi), %rcx
	movq	-24(%rbp), %rdx
	movq	-40(%rbp), %r8
	callq	_RNvXs1_NtCsavOST1yGCNT_10serde_json3serQINtB5_10SerializerQNtNvXs_NtB7_5valueNtB12_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterENtNtCslmkRZor3pUd_10serde_core3ser10Serializer13serialize_strB7_
	testq	%rax, %rax
	jne	.LBB11_88
	movq	(%rsi), %rax
	movq	(%rax), %rsi
	movq	(%rsi), %rcx
	movq	8(%rsi), %rax
	movl	$1, %r8d
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.35(%rip), %rdi
	jmp	.LBB11_156
	.p2align	4
.LBB11_154:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %rdi
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%rdi, %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.35(%rip), %rdi
	testb	%cl, %cl
	je	.LBB11_180
.LBB11_155:
	movq	(%rsi), %rcx
	movq	8(%rsi), %rax
	movl	$1, %r8d
.LBB11_156:
	movq	%rdi, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB11_124
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rbx, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r14,%rcx,4), %rcx
	addq	%r14, %rcx
	jmpq	*%rcx
.LBB11_158:
	cmpb	$35, 16(%rax)
	je	.LBB11_155
	jmp	.LBB11_180
	.p2align	4
.LBB11_159:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	movl	$255, %edx
	cmovael	%edx, %ecx
	cmpb	$35, %cl
	je	.LBB11_155
	jmp	.LBB11_180
	.p2align	4
.LBB11_160:
	cmpb	$35, 31(%rax)
	jne	.LBB11_180
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB11_155
	.p2align	4
.LBB11_162:
	movq	-8(%rbp), %rax
	movq	(%rax), %rax
	movq	(%rax), %rdi
	jmp	.LBB11_164
	.p2align	4
.LBB11_163:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rax
	movq	%rsi, %rcx
	shrq	$32, %rcx
	callq	*16(%rax)
	testb	%al, %al
	je	.LBB11_207
.LBB11_164:
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	movl	$1, %r8d
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.34(%rip), %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB11_152
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rbx, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movq	%rax, %rsi
	andl	$3, %eax
	leaq	.LJTI11_3(%rip), %rcx
	movslq	(%rcx,%rax,4), %rax
	addq	%rcx, %rax
	jmpq	*%rax
.LBB11_166:
	cmpb	$35, 16(%rsi)
	je	.LBB11_164
	jmp	.LBB11_207
	.p2align	4
.LBB11_167:
	movq	%rsi, %rax
	shrq	$32, %rax
	cmpq	$43, %rax
	movl	$255, %ecx
	cmovael	%ecx, %eax
	cmpb	$35, %al
	je	.LBB11_164
	jmp	.LBB11_207
	.p2align	4
.LBB11_168:
	cmpb	$35, 31(%rsi)
	jne	.LBB11_207
	movq	%rsi, %rcx
	decq	%rcx
	callq	*23(%rsi)
	jmp	.LBB11_164
	.p2align	4
.LBB11_147:
	movq	%rdx, %r8
	cmpq	$8, %rdx
	jb	.LBB11_150
	jmp	.LBB11_149
.LBB11_88:
	movq	%rax, %rsi
	jmp	.LBB11_212
.LBB11_170:
	testb	%cl, %cl
	je	.LBB11_211
	movq	(%rsi), %rax
	movq	(%rax), %r14
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.24(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB11_211
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdi
	leaq	.LJTI11_5(%rip), %r15
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.24(%rip), %rbx
	xorl	%esi, %esi
	movl	$255, %r12d
	jmp	.LBB11_175
.LBB11_173:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB11_180
.LBB11_174:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movl	$1, %r8d
	movq	%rbx, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB11_212
.LBB11_175:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rdi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB11_176:
	cmpb	$35, 16(%rax)
	je	.LBB11_174
	jmp	.LBB11_180
.LBB11_177:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB11_174
	jmp	.LBB11_180
.LBB11_178:
	cmpb	$35, 31(%rax)
	jne	.LBB11_180
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB11_174
.LBB11_180:
	movq	%rax, %rcx
.LBB11_181:
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
.LBB11_184:
	leaq	-80(%rbp), %rdi
	movq	%rdi, %rdx
	callq	_RNvXs_NtCs6FhewopUhnE_4zmij7privatedNtB4_6Sealed20write_to_zmij_buffer
	movq	%rax, %rsi
	subq	%rdi, %rsi
	je	.LBB11_211
	movq	(%rbx), %r14
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	-80(%rbp), %rdx
	movq	%rsi, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB11_211
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdi
	leaq	.LJTI11_10(%rip), %r15
	leaq	-80(%rbp), %rbx
	movl	$255, %r12d
	jmp	.LBB11_189
.LBB11_187:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB11_213
.LBB11_188:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movq	%rbx, %rdx
	movq	%rsi, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB11_211
.LBB11_189:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rdi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB11_190:
	cmpb	$35, 16(%rax)
	je	.LBB11_188
	jmp	.LBB11_213
.LBB11_191:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB11_188
	jmp	.LBB11_213
.LBB11_192:
	cmpb	$35, 31(%rax)
	jne	.LBB11_213
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB11_188
.LBB11_195:
	leaq	-1(%rax), %rcx
	cmpq	$19, %rcx
	ja	.LBB11_217
	movb	$45, -80(%rbp,%rcx)
	movl	$21, %esi
.LBB11_197:
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
	je	.LBB11_211
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rbx
	leaq	.LJTI11_12(%rip), %r15
	movl	$255, %r12d
	jmp	.LBB11_201
.LBB11_199:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB11_213
.LBB11_200:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movq	%rdi, %rdx
	movq	%rsi, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB11_211
.LBB11_201:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rbx, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB11_202:
	cmpb	$35, 16(%rax)
	je	.LBB11_200
	jmp	.LBB11_213
.LBB11_203:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB11_200
	jmp	.LBB11_213
.LBB11_204:
	cmpb	$35, 31(%rax)
	jne	.LBB11_213
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB11_200
.LBB11_211:
	xorl	%esi, %esi
.LBB11_212:
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
.LBB11_207:
	movq	%rsi, %rcx
	jmp	.LBB11_181
.LBB11_213:
	movq	%rax, %rcx
	callq	_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io
	movq	%rax, %rsi
	jmp	.LBB11_212
.LBB11_214:
.Ltmp44:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.43(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	nop
.Ltmp45:
	ud2
.LBB11_216:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.130(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB11_217:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.129(%rip), %r8
	movl	$20, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_@IMGREL
	.section	.text,"xr",one_only,_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_,unique,11
	.seh_endproc
	.def	"?dtor$218@?0?_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$218@?0?_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_@4HA":
.seh_proc "?dtor$218@?0?_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_@4HA"
.LBB11_218:
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
.Lfunc_end11:
	.section	.rdata,"dr",associative,_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_,unique,12
	.p2align	2, 0x0
.LJTI11_0:
	.long	.LBB11_1-.LJTI11_0
	.long	.LBB11_25-.LJTI11_0
	.long	.LBB11_19-.LJTI11_0
	.long	.LBB11_24-.LJTI11_0
	.long	.LBB11_10-.LJTI11_0
	.long	.LBB11_35-.LJTI11_0
.LJTI11_1:
	.long	.LBB11_40-.LJTI11_1
	.long	.LBB11_42-.LJTI11_1
	.long	.LBB11_37-.LJTI11_1
	.long	.LBB11_41-.LJTI11_1
.LJTI11_2:
	.long	.LBB11_60-.LJTI11_2
	.long	.LBB11_62-.LJTI11_2
	.long	.LBB11_57-.LJTI11_2
	.long	.LBB11_61-.LJTI11_2
.LJTI11_3:
	.long	.LBB11_166-.LJTI11_3
	.long	.LBB11_168-.LJTI11_3
	.long	.LBB11_163-.LJTI11_3
	.long	.LBB11_167-.LJTI11_3
.LJTI11_4:
	.long	.LBB11_158-.LJTI11_4
	.long	.LBB11_160-.LJTI11_4
	.long	.LBB11_154-.LJTI11_4
	.long	.LBB11_159-.LJTI11_4
.LJTI11_5:
	.long	.LBB11_176-.LJTI11_5
	.long	.LBB11_178-.LJTI11_5
	.long	.LBB11_173-.LJTI11_5
	.long	.LBB11_177-.LJTI11_5
.LJTI11_6:
	.long	.LBB11_15-.LJTI11_6
	.long	.LBB11_17-.LJTI11_6
	.long	.LBB11_12-.LJTI11_6
	.long	.LBB11_16-.LJTI11_6
.LJTI11_7:
	.long	.LBB11_50-.LJTI11_7
	.long	.LBB11_52-.LJTI11_7
	.long	.LBB11_47-.LJTI11_7
	.long	.LBB11_51-.LJTI11_7
.LJTI11_8:
	.long	.LBB11_72-.LJTI11_8
	.long	.LBB11_74-.LJTI11_8
	.long	.LBB11_69-.LJTI11_8
	.long	.LBB11_73-.LJTI11_8
.LJTI11_9:
	.long	.LBB11_117-.LJTI11_9
	.long	.LBB11_119-.LJTI11_9
	.long	.LBB11_114-.LJTI11_9
	.long	.LBB11_118-.LJTI11_9
.LJTI11_10:
	.long	.LBB11_190-.LJTI11_10
	.long	.LBB11_192-.LJTI11_10
	.long	.LBB11_187-.LJTI11_10
	.long	.LBB11_191-.LJTI11_10
.LJTI11_11:
	.long	.LBB11_95-.LJTI11_11
	.long	.LBB11_97-.LJTI11_11
	.long	.LBB11_92-.LJTI11_11
	.long	.LBB11_96-.LJTI11_11
.LJTI11_12:
	.long	.LBB11_202-.LJTI11_12
	.long	.LBB11_204-.LJTI11_12
	.long	.LBB11_199-.LJTI11_12
	.long	.LBB11_203-.LJTI11_12
.LJTI11_13:
	.long	.LBB11_105-.LJTI11_13
	.long	.LBB11_107-.LJTI11_13
	.long	.LBB11_102-.LJTI11_13
	.long	.LBB11_106-.LJTI11_13
.LJTI11_14:
	.long	.LBB11_82-.LJTI11_14
	.long	.LBB11_84-.LJTI11_14
	.long	.LBB11_79-.LJTI11_14
	.long	.LBB11_83-.LJTI11_14
.LJTI11_15:
	.long	.LBB11_31-.LJTI11_15
	.long	.LBB11_33-.LJTI11_15
	.long	.LBB11_28-.LJTI11_15
	.long	.LBB11_32-.LJTI11_15
.LJTI11_16:
	.long	.LBB11_6-.LJTI11_16
	.long	.LBB11_8-.LJTI11_16
	.long	.LBB11_3-.LJTI11_16
	.long	.LBB11_7-.LJTI11_16
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_,unique,11
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
	.long	.Lfunc_begin11@IMGREL
	.long	-1
	.long	.Ltmp44@IMGREL
	.long	0
	.long	.Ltmp45@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_,unique,11

	.def	_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_,unique,13
	.p2align	4
_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_:
.Lfunc_begin12:
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
	leaq	.LJTI12_0(%rip), %rdx
	movslq	(%rdx,%rax,4), %rax
	addq	%rdx, %rax
	jmpq	*%rax
.LBB12_1:
	movq	(%r9), %rax
	movq	(%rax), %r14
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.33(%rip), %rdx
	movl	$4, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_177
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rsi
	leaq	.LJTI12_16(%rip), %r15
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.33(%rip), %rdi
	xorl	%ebx, %ebx
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
	je	.LBB12_179
.LBB12_4:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movl	$4, %r8d
	movq	%rdi, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_178
.LBB12_5:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rsi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB12_6:
	cmpb	$35, 16(%rax)
	je	.LBB12_4
	jmp	.LBB12_179
	.p2align	4
.LBB12_7:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB12_4
	jmp	.LBB12_179
	.p2align	4
.LBB12_8:
	cmpb	$35, 31(%rax)
	jne	.LBB12_179
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_4
.LBB12_10:
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
	je	.LBB12_44
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %r14
	leaq	.LJTI12_6(%rip), %rdi
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.25(%rip), %r15
	movl	$255, %r12d
	jmp	.LBB12_14
	.p2align	4
.LBB12_12:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB12_179
.LBB12_13:
	movq	(%rsi), %rcx
	movq	8(%rsi), %rax
	movl	$1, %r8d
	movq	%r15, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_44
.LBB12_14:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%r14, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%rdi,%rcx,4), %rcx
	addq	%rdi, %rcx
	jmpq	*%rcx
.LBB12_15:
	cmpb	$35, 16(%rax)
	je	.LBB12_13
	jmp	.LBB12_179
	.p2align	4
.LBB12_16:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB12_13
	jmp	.LBB12_179
	.p2align	4
.LBB12_17:
	cmpb	$35, 31(%rax)
	jne	.LBB12_179
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_13
.LBB12_19:
	movq	(%r9), %rbx
	movq	8(%rcx), %rax
	cmpq	$2, %rax
	je	.LBB12_153
	cmpl	$1, %eax
	jne	.LBB12_163
	movq	16(%rcx), %rsi
	movq	%rsi, %rcx
	negq	%rcx
	cmovsq	%rsi, %rcx
	leaq	-96(%rbp), %rdx
	callq	_RNvXsu_Cs1KvuFdKMjOj_4itoayNtB5_8Unsigned3fmt
	testq	%rsi, %rsi
	js	.LBB12_191
	cmpq	$20, %rax
	je	.LBB12_177
	movl	$20, %esi
	movq	%rax, %rcx
	jmp	.LBB12_193
.LBB12_24:
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
.LBB12_25:
	movq	(%r9), %rax
	movq	(%rax), %r14
	cmpb	$0, 1(%rcx)
	je	.LBB12_141
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.32(%rip), %rdx
	movl	$4, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_177
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rsi
	leaq	.LJTI12_15(%rip), %r15
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.32(%rip), %rdi
	xorl	%ebx, %ebx
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
	je	.LBB12_179
.LBB12_29:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movl	$4, %r8d
	movq	%rdi, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_178
.LBB12_30:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rsi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB12_31:
	cmpb	$35, 16(%rax)
	je	.LBB12_29
	jmp	.LBB12_179
	.p2align	4
.LBB12_32:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB12_29
	jmp	.LBB12_179
	.p2align	4
.LBB12_33:
	cmpb	$35, 31(%rax)
	jne	.LBB12_179
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_29
.LBB12_35:
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
	je	.LBB12_76
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rbx
	leaq	.LJTI12_1(%rip), %r12
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.26(%rip), %r14
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
	testb	%cl, %cl
	je	.LBB12_179
.LBB12_38:
	movq	(%r15), %rcx
	movq	8(%r15), %rax
	movl	$1, %r8d
	movq	%r14, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_76
.LBB12_39:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rbx, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r12,%rcx,4), %rcx
	addq	%r12, %rcx
	jmpq	*%rcx
.LBB12_40:
	cmpb	$35, 16(%rax)
	je	.LBB12_38
	jmp	.LBB12_179
	.p2align	4
.LBB12_41:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r13d, %ecx
	cmpb	$35, %cl
	je	.LBB12_38
	jmp	.LBB12_179
	.p2align	4
.LBB12_42:
	cmpb	$35, 31(%rax)
	jne	.LBB12_179
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_38
.LBB12_44:
	movq	8(%rbp), %rsi
	leaq	8(%rsi), %rcx
	movq	-8(%rbp), %rdx
	testq	%rdx, %rdx
	je	.LBB12_150
	movq	%rcx, -32(%rbp)
	shlq	$5, %rdx
	movq	(%rbp), %rdi
	addq	%rdi, %rdx
	movb	$1, %al
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %r12
	leaq	.LJTI12_9(%rip), %r13
	movq	%rdx, -8(%rbp)
.LBB12_46:
	movq	%rdi, (%rbp)
	movq	(%rsi), %rcx
	movq	%rcx, -16(%rbp)
	movq	(%rcx), %rbx
	testb	$1, %al
	jne	.LBB12_48
	jmp	.LBB12_55
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
	je	.LBB12_179
.LBB12_48:
	movq	(%rbx), %rcx
	movq	8(%rbx), %rax
	movl	$1, %r8d
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.23(%rip), %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_61
	movl	$9, %r8d
	movb	$41, %cl
	movq	%r12, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	leaq	.LJTI12_8(%rip), %rdx
	movslq	(%rdx,%rcx,4), %rcx
	addq	%rdx, %rcx
	jmpq	*%rcx
.LBB12_50:
	cmpb	$35, 16(%rax)
	je	.LBB12_48
	jmp	.LBB12_179
	.p2align	4
.LBB12_51:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	movl	$255, %edx
	cmovael	%edx, %ecx
	cmpb	$35, %cl
	je	.LBB12_48
	jmp	.LBB12_179
	.p2align	4
.LBB12_52:
	cmpb	$35, 31(%rax)
	jne	.LBB12_179
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_48
	.p2align	4
.LBB12_54:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %rsi
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%rsi, %rax
	testb	%cl, %cl
	je	.LBB12_179
.LBB12_55:
	movq	(%rbx), %rcx
	movq	8(%rbx), %rax
	movl	$2, %r8d
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.27(%rip), %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_61
	movl	$9, %r8d
	movb	$41, %cl
	movq	%r12, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	leaq	.LJTI12_7(%rip), %rdx
	movslq	(%rdx,%rcx,4), %rcx
	addq	%rdx, %rcx
	jmpq	*%rcx
.LBB12_57:
	cmpb	$35, 16(%rax)
	je	.LBB12_55
	jmp	.LBB12_179
	.p2align	4
.LBB12_58:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	movl	$255, %edx
	cmovael	%edx, %ecx
	cmpb	$35, %cl
	je	.LBB12_55
	jmp	.LBB12_179
	.p2align	4
.LBB12_59:
	cmpb	$35, 31(%rax)
	jne	.LBB12_179
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_55
	.p2align	4
.LBB12_61:
	movq	8(%rbp), %rax
	movq	24(%rax), %rax
	movq	%rax, -40(%rbp)
	testq	%rax, %rax
	je	.LBB12_73
	movq	8(%rbp), %rax
	movq	16(%rax), %rbx
	testq	%rbx, %rbx
	je	.LBB12_73
	movq	8(%rbp), %rax
	movq	8(%rax), %r14
	xorl	%esi, %esi
	jmp	.LBB12_65
	.p2align	4
.LBB12_64:
	incq	%rsi
	cmpq	-40(%rbp), %rsi
	je	.LBB12_73
.LBB12_65:
	movq	-16(%rbp), %rax
	movq	(%rax), %r15
	jmp	.LBB12_67
	.p2align	4
.LBB12_66:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %rdi
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%rdi, %rax
	testb	%cl, %cl
	je	.LBB12_179
.LBB12_67:
	movq	(%r15), %rcx
	movq	8(%r15), %rax
	movq	%r14, %rdx
	movq	%rbx, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_64
	movl	$9, %r8d
	movb	$41, %cl
	movq	%r12, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r13,%rcx,4), %rcx
	addq	%r13, %rcx
	jmpq	*%rcx
.LBB12_69:
	cmpb	$35, 16(%rax)
	je	.LBB12_67
	jmp	.LBB12_179
	.p2align	4
.LBB12_70:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	movl	$255, %edx
	cmovael	%edx, %ecx
	cmpb	$35, %cl
	je	.LBB12_67
	jmp	.LBB12_179
	.p2align	4
.LBB12_71:
	cmpb	$35, 31(%rax)
	jne	.LBB12_179
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_67
	.p2align	4
.LBB12_73:
	movq	(%rbp), %rdi
	movq	%rdi, %rcx
	movq	8(%rbp), %rsi
	movq	%rsi, %rdx
	callq	_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_
	testq	%rax, %rax
	jne	.LBB12_202
	addq	$32, %rdi
	movb	$1, 32(%rsi)
	xorl	%eax, %eax
	movq	-8(%rbp), %rdx
	cmpq	%rdx, %rdi
	jne	.LBB12_46
	movq	(%rsi), %rdx
	movq	-32(%rbp), %rcx
	jmp	.LBB12_151
.LBB12_76:
	movq	8(%rbp), %r10
	leaq	8(%r10), %rcx
	cmpq	$0, (%rbp)
	je	.LBB12_152
	movq	%rcx, -48(%rbp)
	movq	-16(%rbp), %rsi
	movq	8(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB12_174
	movq	16(%rsi), %r9
	movb	$1, %al
	xorl	%r13d, %r13d
.LBB12_79:
	testq	%r13, %r13
	je	.LBB12_82
	movzwl	626(%r13), %edx
	cmpq	%rdx, %r9
	jae	.LBB12_92
.LBB12_81:
	movq	%r13, %r15
	movq	%r9, %r11
	jmp	.LBB12_94
.LBB12_82:
	testq	%r9, %r9
	je	.LBB12_87
	movq	%r9, %rdx
	movq	%rcx, %r13
	andq	$7, %rdx
	je	.LBB12_88
	xorl	%r8d, %r8d
	.p2align	4
.LBB12_85:
	movq	632(%r13), %r13
	incq	%r8
	cmpq	%r8, %rdx
	jne	.LBB12_85
	movq	%r9, %rcx
	subq	%r8, %rcx
	jmp	.LBB12_89
.LBB12_87:
	movq	%rcx, %r13
	jmp	.LBB12_91
.LBB12_88:
	movq	%r9, %rcx
.LBB12_89:
	cmpq	$8, %r9
	jb	.LBB12_91
	.p2align	4
.LBB12_90:
	movq	632(%r13), %rdx
	movq	632(%rdx), %rdx
	movq	632(%rdx), %rdx
	movq	632(%rdx), %rdx
	movq	632(%rdx), %rdx
	movq	632(%rdx), %rdx
	movq	632(%rdx), %rdx
	movq	632(%rdx), %r13
	addq	$-8, %rcx
	jne	.LBB12_90
.LBB12_91:
	xorl	%r9d, %r9d
	xorl	%ecx, %ecx
	movzwl	626(%r13), %edx
	cmpq	%rdx, %r9
	jb	.LBB12_81
	.p2align	4
.LBB12_92:
	movq	352(%r13), %r15
	testq	%r15, %r15
	je	.LBB12_206
	incq	%rcx
	movzwl	624(%r13), %r11d
	movq	%r15, %r13
	cmpw	626(%r15), %r11w
	jae	.LBB12_92
.LBB12_94:
	testq	%rcx, %rcx
	je	.LBB12_101
	leaq	(%r15,%r11,8), %rdx
	addq	$640, %rdx
	movq	%rcx, %r8
	andq	$7, %r8
	je	.LBB12_140
	xorl	%r9d, %r9d
	.p2align	4
.LBB12_97:
	movq	(%rdx), %r13
	leaq	632(%r13), %rdx
	incq	%r9
	cmpq	%r9, %r8
	jne	.LBB12_97
	movq	%rcx, %r8
	subq	%r9, %r8
	cmpq	$8, %rcx
	jb	.LBB12_100
	.p2align	4
.LBB12_99:
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
	jne	.LBB12_99
.LBB12_100:
	movq	$0, -24(%rbp)
	jmp	.LBB12_102
.LBB12_101:
	leaq	1(%r11), %rcx
	movq	%rcx, -24(%rbp)
	movq	%r15, %r13
.LBB12_102:
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
	jne	.LBB12_104
	jmp	.LBB12_111
	.p2align	4
.LBB12_103:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rax
	movq	%rbx, %rcx
	shrq	$32, %rcx
	callq	*16(%rax)
	testb	%al, %al
	je	.LBB12_173
.LBB12_104:
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	movl	$1, %r8d
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.23(%rip), %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_117
	movl	$9, %r8d
	movb	$41, %cl
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movq	%rax, %rbx
	andl	$3, %eax
	leaq	.LJTI12_3(%rip), %rcx
	movslq	(%rcx,%rax,4), %rax
	addq	%rcx, %rax
	jmpq	*%rax
.LBB12_106:
	cmpb	$35, 16(%rbx)
	je	.LBB12_104
	jmp	.LBB12_173
	.p2align	4
.LBB12_107:
	movq	%rbx, %rax
	shrq	$32, %rax
	cmpq	$43, %rax
	movl	$255, %ecx
	cmovael	%ecx, %eax
	cmpb	$35, %al
	je	.LBB12_104
	jmp	.LBB12_173
	.p2align	4
.LBB12_108:
	cmpb	$35, 31(%rbx)
	jne	.LBB12_173
	movq	%rbx, %rcx
	decq	%rcx
	callq	*23(%rbx)
	jmp	.LBB12_104
	.p2align	4
.LBB12_110:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rax
	movq	%rbx, %rcx
	shrq	$32, %rcx
	callq	*16(%rax)
	testb	%al, %al
	je	.LBB12_173
.LBB12_111:
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	movl	$2, %r8d
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.27(%rip), %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_117
	movl	$9, %r8d
	movb	$41, %cl
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movq	%rax, %rbx
	andl	$3, %eax
	leaq	.LJTI12_2(%rip), %rcx
	movslq	(%rcx,%rax,4), %rax
	addq	%rcx, %rax
	jmpq	*%rax
.LBB12_113:
	cmpb	$35, 16(%rbx)
	je	.LBB12_111
	jmp	.LBB12_173
	.p2align	4
.LBB12_114:
	movq	%rbx, %rax
	shrq	$32, %rax
	cmpq	$43, %rax
	movl	$255, %ecx
	cmovael	%ecx, %eax
	cmpb	$35, %al
	je	.LBB12_111
	jmp	.LBB12_173
	.p2align	4
.LBB12_115:
	cmpb	$35, 31(%rbx)
	jne	.LBB12_173
	movq	%rbx, %rcx
	decq	%rcx
	callq	*23(%rbx)
	jmp	.LBB12_111
.LBB12_117:
	movq	8(%rbp), %rax
	movq	24(%rax), %rax
	movq	%rax, -40(%rbp)
	testq	%rax, %rax
	je	.LBB12_129
	movq	8(%rbp), %rax
	movq	16(%rax), %rdi
	testq	%rdi, %rdi
	je	.LBB12_129
	movq	8(%rbp), %rax
	movq	8(%rax), %r12
	xorl	%r14d, %r14d
	jmp	.LBB12_121
	.p2align	4
.LBB12_120:
	incq	%r14
	cmpq	-40(%rbp), %r14
	je	.LBB12_129
.LBB12_121:
	movq	-16(%rbp), %rax
	movq	(%rax), %rsi
	jmp	.LBB12_123
	.p2align	4
.LBB12_122:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rax
	movq	%rbx, %rcx
	shrq	$32, %rcx
	callq	*16(%rax)
	testb	%al, %al
	je	.LBB12_173
.LBB12_123:
	movq	(%rsi), %rcx
	movq	8(%rsi), %rax
	movq	%r12, %rdx
	movq	%rdi, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_120
	movl	$9, %r8d
	movb	$41, %cl
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movq	%rax, %rbx
	andl	$3, %eax
	leaq	.LJTI12_4(%rip), %rcx
	movslq	(%rcx,%rax,4), %rax
	addq	%rcx, %rax
	jmpq	*%rax
.LBB12_125:
	cmpb	$35, 16(%rbx)
	je	.LBB12_123
	jmp	.LBB12_173
	.p2align	4
.LBB12_126:
	movq	%rbx, %rax
	shrq	$32, %rax
	cmpq	$43, %rax
	movl	$255, %ecx
	cmovael	%ecx, %eax
	cmpb	$35, %al
	je	.LBB12_123
	jmp	.LBB12_173
	.p2align	4
.LBB12_127:
	cmpb	$35, 31(%rbx)
	jne	.LBB12_173
	movq	%rbx, %rcx
	decq	%rcx
	callq	*23(%rbx)
	jmp	.LBB12_123
.LBB12_129:
	movq	8(%rbp), %rsi
	movq	(%rsi), %rcx
	movq	-8(%rbp), %rdx
	movq	-32(%rbp), %r8
	callq	_RNvXs1_NtCsavOST1yGCNT_10serde_json3serQINtB5_10SerializerQNtNvXs_NtB7_5valueNtB12_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterENtNtCslmkRZor3pUd_10serde_core3ser10Serializer13serialize_strB7_
	testq	%rax, %rax
	jne	.LBB12_202
	movq	(%rsi), %rax
	movq	(%rax), %rdi
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	movl	$2, %r8d
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.28(%rip), %rbx
	movq	%rbx, %rdx
	callq	*24(%rax)
	testb	%al, %al
	leaq	.LJTI12_5(%rip), %r14
	jne	.LBB12_135
.LBB12_131:
	movq	-56(%rbp), %rax
	shlq	$5, %rax
	addq	%rax, %r15
	movq	%r15, %rcx
	movq	8(%rbp), %rsi
	movq	%rsi, %rdx
	callq	_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_
	testq	%rax, %rax
	jne	.LBB12_202
	xorl	%eax, %eax
	movb	$1, 32(%rsi)
	movl	$0, %ecx
	decq	(%rbp)
	movq	%rsi, %r10
	movq	-24(%rbp), %r9
	jne	.LBB12_79
	jmp	.LBB12_174
	.p2align	4
.LBB12_133:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %rsi
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%rsi, %rax
	testb	%cl, %cl
	je	.LBB12_179
.LBB12_134:
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	movl	$2, %r8d
	movq	%rbx, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_131
.LBB12_135:
	movl	$9, %r8d
	movb	$41, %cl
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r14,%rcx,4), %rcx
	addq	%r14, %rcx
	jmpq	*%rcx
.LBB12_136:
	cmpb	$35, 16(%rax)
	je	.LBB12_134
	jmp	.LBB12_179
	.p2align	4
.LBB12_137:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	movl	$255, %edx
	cmovael	%edx, %ecx
	cmpb	$35, %cl
	je	.LBB12_134
	jmp	.LBB12_179
	.p2align	4
.LBB12_138:
	cmpb	$35, 31(%rax)
	jne	.LBB12_179
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_134
.LBB12_140:
	movq	%rcx, %r8
	cmpq	$8, %rcx
	jae	.LBB12_99
	jmp	.LBB12_100
.LBB12_141:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.31(%rip), %rdx
	movl	$5, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_177
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rsi
	leaq	.LJTI12_14(%rip), %r15
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.31(%rip), %rdi
	xorl	%ebx, %ebx
	movl	$255, %r12d
	jmp	.LBB12_145
	.p2align	4
.LBB12_143:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB12_179
.LBB12_144:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movl	$5, %r8d
	movq	%rdi, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_178
.LBB12_145:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rsi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB12_146:
	cmpb	$35, 16(%rax)
	je	.LBB12_144
	jmp	.LBB12_179
	.p2align	4
.LBB12_147:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB12_144
	jmp	.LBB12_179
	.p2align	4
.LBB12_148:
	cmpb	$35, 31(%rax)
	jne	.LBB12_179
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_144
.LBB12_150:
	movq	%rbx, %rdx
.LBB12_151:
	callq	_RINvXsd_NtCsavOST1yGCNT_10serde_json3serNtB6_15PrettyFormatterNtB6_9Formatter9end_arrayQNtNvXs_NtB8_5valueNtB1v_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEB8_
	jmp	.LBB12_176
.LBB12_152:
	movq	%rdi, %rdx
	jmp	.LBB12_175
.LBB12_153:
	movq	16(%rcx), %xmm0
	movq	%xmm0, %rax
	movabsq	$9223372036854775807, %rcx
	andq	%rax, %rcx
	movabsq	$9218868437227405312, %rax
	cmpq	%rax, %rcx
	jl	.LBB12_181
	movq	(%rbx), %r14
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.33(%rip), %rdx
	movl	$4, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_177
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rsi
	leaq	.LJTI12_11(%rip), %r15
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.33(%rip), %rdi
	xorl	%ebx, %ebx
	movl	$255, %r12d
	jmp	.LBB12_158
.LBB12_156:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB12_179
.LBB12_157:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movl	$4, %r8d
	movq	%rdi, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_178
.LBB12_158:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rsi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB12_159:
	cmpb	$35, 16(%rax)
	je	.LBB12_157
	jmp	.LBB12_179
.LBB12_160:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB12_157
	jmp	.LBB12_179
.LBB12_161:
	cmpb	$35, 31(%rax)
	jne	.LBB12_179
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_157
.LBB12_163:
	movq	16(%rcx), %rcx
	leaq	-96(%rbp), %rdx
	callq	_RNvXsu_Cs1KvuFdKMjOj_4itoayNtB5_8Unsigned3fmt
	movq	%rax, %rsi
	subq	$20, %rsi
	je	.LBB12_177
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
	je	.LBB12_177
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rbx
	leaq	.LJTI12_13(%rip), %r15
	movl	$255, %r12d
	jmp	.LBB12_168
.LBB12_166:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB12_205
.LBB12_167:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movq	%rdi, %rdx
	movq	%rsi, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_177
.LBB12_168:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rbx, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB12_169:
	cmpb	$35, 16(%rax)
	je	.LBB12_167
	jmp	.LBB12_205
.LBB12_170:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB12_167
	jmp	.LBB12_205
.LBB12_171:
	cmpb	$35, 31(%rax)
	jne	.LBB12_205
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_167
.LBB12_173:
	movq	%rbx, %rcx
	jmp	.LBB12_180
.LBB12_174:
	movq	(%r10), %rdx
	movq	-48(%rbp), %rcx
.LBB12_175:
	callq	_RINvXsd_NtCsavOST1yGCNT_10serde_json3serNtB6_15PrettyFormatterNtB6_9Formatter10end_objectQNtNvXs_NtB8_5valueNtB1x_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEB8_
.LBB12_176:
	testq	%rax, %rax
	jne	.LBB12_179
.LBB12_177:
	xorl	%ebx, %ebx
.LBB12_178:
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
.LBB12_179:
	movq	%rax, %rcx
.LBB12_180:
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
.LBB12_181:
	leaq	-96(%rbp), %rdi
	movq	%rdi, %rdx
	callq	_RNvXs_NtCs6FhewopUhnE_4zmij7privatedNtB4_6Sealed20write_to_zmij_buffer
	movq	%rax, %rsi
	subq	%rdi, %rsi
	je	.LBB12_177
	movq	(%rbx), %r14
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	-96(%rbp), %rdx
	movq	%rsi, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_177
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdi
	leaq	.LJTI12_10(%rip), %r15
	leaq	-96(%rbp), %rbx
	movl	$255, %r12d
	jmp	.LBB12_186
.LBB12_184:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB12_205
.LBB12_185:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movq	%rbx, %rdx
	movq	%rsi, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_177
.LBB12_186:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rdi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB12_187:
	cmpb	$35, 16(%rax)
	je	.LBB12_185
	jmp	.LBB12_205
.LBB12_188:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB12_185
	jmp	.LBB12_205
.LBB12_189:
	cmpb	$35, 31(%rax)
	jne	.LBB12_205
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_185
.LBB12_191:
	leaq	-1(%rax), %rcx
	cmpq	$19, %rcx
	ja	.LBB12_208
	movb	$45, -96(%rbp,%rcx)
	movl	$21, %esi
.LBB12_193:
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
	je	.LBB12_177
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rbx
	leaq	.LJTI12_12(%rip), %r15
	movl	$255, %r12d
	jmp	.LBB12_197
.LBB12_195:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB12_205
.LBB12_196:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movq	%rdi, %rdx
	movq	%rsi, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB12_177
.LBB12_197:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rbx, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB12_198:
	cmpb	$35, 16(%rax)
	je	.LBB12_196
	jmp	.LBB12_205
.LBB12_199:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%r12d, %ecx
	cmpb	$35, %cl
	je	.LBB12_196
	jmp	.LBB12_205
.LBB12_200:
	cmpb	$35, 31(%rax)
	jne	.LBB12_205
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB12_196
.LBB12_202:
	movq	%rax, %rbx
	jmp	.LBB12_178
.LBB12_205:
	movq	%rax, %rcx
	callq	_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io
	movq	%rax, %rbx
	jmp	.LBB12_178
.LBB12_206:
.Ltmp46:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.43(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	nop
.Ltmp47:
	ud2
.LBB12_208:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.129(%rip), %r8
	movl	$20, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_@IMGREL
	.section	.text,"xr",one_only,_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_,unique,13
	.seh_endproc
	.def	"?dtor$209@?0?_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$209@?0?_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_@4HA":
.seh_proc "?dtor$209@?0?_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_@4HA"
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	128(%rdx), %rbp
	.seh_endprologue
	ud2
.Lfunc_end12:
	.section	.rdata,"dr",associative,_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_,unique,14
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
	.long	.LBB12_113-.LJTI12_2
	.long	.LBB12_115-.LJTI12_2
	.long	.LBB12_110-.LJTI12_2
	.long	.LBB12_114-.LJTI12_2
.LJTI12_3:
	.long	.LBB12_106-.LJTI12_3
	.long	.LBB12_108-.LJTI12_3
	.long	.LBB12_103-.LJTI12_3
	.long	.LBB12_107-.LJTI12_3
.LJTI12_4:
	.long	.LBB12_125-.LJTI12_4
	.long	.LBB12_127-.LJTI12_4
	.long	.LBB12_122-.LJTI12_4
	.long	.LBB12_126-.LJTI12_4
.LJTI12_5:
	.long	.LBB12_136-.LJTI12_5
	.long	.LBB12_138-.LJTI12_5
	.long	.LBB12_133-.LJTI12_5
	.long	.LBB12_137-.LJTI12_5
.LJTI12_6:
	.long	.LBB12_15-.LJTI12_6
	.long	.LBB12_17-.LJTI12_6
	.long	.LBB12_12-.LJTI12_6
	.long	.LBB12_16-.LJTI12_6
.LJTI12_7:
	.long	.LBB12_57-.LJTI12_7
	.long	.LBB12_59-.LJTI12_7
	.long	.LBB12_54-.LJTI12_7
	.long	.LBB12_58-.LJTI12_7
.LJTI12_8:
	.long	.LBB12_50-.LJTI12_8
	.long	.LBB12_52-.LJTI12_8
	.long	.LBB12_47-.LJTI12_8
	.long	.LBB12_51-.LJTI12_8
.LJTI12_9:
	.long	.LBB12_69-.LJTI12_9
	.long	.LBB12_71-.LJTI12_9
	.long	.LBB12_66-.LJTI12_9
	.long	.LBB12_70-.LJTI12_9
.LJTI12_10:
	.long	.LBB12_187-.LJTI12_10
	.long	.LBB12_189-.LJTI12_10
	.long	.LBB12_184-.LJTI12_10
	.long	.LBB12_188-.LJTI12_10
.LJTI12_11:
	.long	.LBB12_159-.LJTI12_11
	.long	.LBB12_161-.LJTI12_11
	.long	.LBB12_156-.LJTI12_11
	.long	.LBB12_160-.LJTI12_11
.LJTI12_12:
	.long	.LBB12_198-.LJTI12_12
	.long	.LBB12_200-.LJTI12_12
	.long	.LBB12_195-.LJTI12_12
	.long	.LBB12_199-.LJTI12_12
.LJTI12_13:
	.long	.LBB12_169-.LJTI12_13
	.long	.LBB12_171-.LJTI12_13
	.long	.LBB12_166-.LJTI12_13
	.long	.LBB12_170-.LJTI12_13
.LJTI12_14:
	.long	.LBB12_146-.LJTI12_14
	.long	.LBB12_148-.LJTI12_14
	.long	.LBB12_143-.LJTI12_14
	.long	.LBB12_147-.LJTI12_14
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
	.section	.text,"xr",one_only,_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_,unique,13
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
	.long	.Lfunc_begin12@IMGREL
	.long	-1
	.long	.Ltmp46@IMGREL
	.long	0
	.long	.Ltmp47@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_,unique,13

	.def	_RINvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB6_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error6customNtNtCs8xEFJqa6dYS_4core3fmt9ArgumentsEB8_.llvm.16186315980599473920;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB6_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error6customNtNtCs8xEFJqa6dYS_4core3fmt9ArgumentsEB8_.llvm.16186315980599473920,unique,15
	.globl	_RINvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB6_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error6customNtNtCs8xEFJqa6dYS_4core3fmt9ArgumentsEB8_.llvm.16186315980599473920
	.p2align	4
_RINvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB6_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error6customNtNtCs8xEFJqa6dYS_4core3fmt9ArgumentsEB8_.llvm.16186315980599473920:
.Lfunc_begin13:
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
	jne	.LBB13_1
	leaq	40(%rsp), %rcx
	movq	%rdi, %rdx
	movq	%rsi, %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	jmp	.LBB13_7
.LBB13_1:
	shrq	%rsi
	je	.LBB13_2
	movl	$1, %edx
	movq	%rsi, %rcx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB13_8
	movq	%rax, %rbx
	movq	%rax, %rcx
	movq	%rdi, %rdx
	movq	%rsi, %r8
	callq	memcpy
	jmp	.LBB13_5
.LBB13_2:
	movl	$1, %ebx
.LBB13_5:
	movq	%rsi, 40(%rsp)
	movq	%rbx, 48(%rsp)
	movq	%rsi, 56(%rsp)
.LBB13_7:
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
.LBB13_8:
	movl	$1, %ecx
	movq	%rsi, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.Lfunc_end13:
	.seh_endproc

	.def	_RINvXsd_NtCsavOST1yGCNT_10serde_json3serNtB6_15PrettyFormatterNtB6_9Formatter10end_objectQNtNvXs_NtB8_5valueNtB1x_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEB8_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvXsd_NtCsavOST1yGCNT_10serde_json3serNtB6_15PrettyFormatterNtB6_9Formatter10end_objectQNtNvXs_NtB8_5valueNtB1x_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEB8_,unique,16
	.p2align	4
_RINvXsd_NtCsavOST1yGCNT_10serde_json3serNtB6_15PrettyFormatterNtB6_9Formatter10end_objectQNtNvXs_NtB8_5valueNtB1x_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEB8_:
.Lfunc_begin14:
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
	je	.LBB14_22
	movq	%rcx, %rdi
	movq	%rdx, 32(%rsp)
	movq	(%rdx), %r12
	movq	(%r12), %rcx
	movq	8(%r12), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.23(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB14_10
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rbx
	leaq	.LJTI14_0(%rip), %r13
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.23(%rip), %r14
	movl	$255, %esi
	jmp	.LBB14_5
	.p2align	4
.LBB14_3:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %rbp
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%rbp, %rax
	testb	%cl, %cl
	je	.LBB14_33
.LBB14_4:
	movq	(%r12), %rcx
	movq	8(%r12), %rax
	movl	$1, %r8d
	movq	%r14, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB14_10
.LBB14_5:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rbx, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r13,%rcx,4), %rcx
	addq	%r13, %rcx
	jmpq	*%rcx
.LBB14_6:
	cmpb	$35, 16(%rax)
	je	.LBB14_4
	jmp	.LBB14_33
	.p2align	4
.LBB14_7:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%esi, %ecx
	cmpb	$35, %cl
	je	.LBB14_4
	jmp	.LBB14_33
	.p2align	4
.LBB14_8:
	cmpb	$35, 31(%rax)
	jne	.LBB14_33
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB14_4
.LBB14_10:
	testq	%r15, %r15
	movq	32(%rsp), %rdx
	je	.LBB14_22
	movq	8(%rdi), %rbx
	testq	%rbx, %rbx
	je	.LBB14_22
	movq	(%rdi), %rdi
	xorl	%r12d, %r12d
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %r14
	leaq	.LJTI14_1(%rip), %r13
	jmp	.LBB14_14
	.p2align	4
.LBB14_13:
	incq	%r12
	cmpq	%r15, %r12
	movq	32(%rsp), %rdx
	je	.LBB14_22
.LBB14_14:
	movq	(%rdx), %rbp
	jmp	.LBB14_16
	.p2align	4
.LBB14_15:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %rsi
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%rsi, %rax
	testb	%cl, %cl
	je	.LBB14_33
.LBB14_16:
	movq	(%rbp), %rcx
	movq	8(%rbp), %rax
	movq	%rdi, %rdx
	movq	%rbx, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB14_13
	movl	$9, %r8d
	movb	$41, %cl
	movq	%r14, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r13,%rcx,4), %rcx
	addq	%r13, %rcx
	jmpq	*%rcx
.LBB14_18:
	cmpb	$35, 16(%rax)
	je	.LBB14_16
	jmp	.LBB14_33
	.p2align	4
.LBB14_19:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	movl	$255, %edx
	cmovael	%edx, %ecx
	cmpb	$35, %cl
	je	.LBB14_16
	jmp	.LBB14_33
	.p2align	4
.LBB14_20:
	cmpb	$35, 31(%rax)
	jne	.LBB14_33
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB14_16
.LBB14_22:
	movq	(%rdx), %rbx
	movq	(%rbx), %rcx
	movq	8(%rbx), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.24(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB14_32
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rsi
	leaq	.LJTI14_2(%rip), %r14
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.24(%rip), %rdi
	movl	$255, %ebp
	jmp	.LBB14_26
	.p2align	4
.LBB14_24:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r15
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r15, %rax
	testb	%cl, %cl
	je	.LBB14_33
.LBB14_25:
	movq	(%rbx), %rcx
	movq	8(%rbx), %rax
	movl	$1, %r8d
	movq	%rdi, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB14_32
.LBB14_26:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rsi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r14,%rcx,4), %rcx
	addq	%r14, %rcx
	jmpq	*%rcx
.LBB14_27:
	cmpb	$35, 16(%rax)
	je	.LBB14_25
	jmp	.LBB14_33
	.p2align	4
.LBB14_28:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%ebp, %ecx
	cmpb	$35, %cl
	je	.LBB14_25
	jmp	.LBB14_33
	.p2align	4
.LBB14_29:
	cmpb	$35, 31(%rax)
	jne	.LBB14_33
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB14_25
.LBB14_32:
	xorl	%eax, %eax
.LBB14_33:
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
.Lfunc_end14:
	.section	.rdata,"dr",associative,_RINvXsd_NtCsavOST1yGCNT_10serde_json3serNtB6_15PrettyFormatterNtB6_9Formatter10end_objectQNtNvXs_NtB8_5valueNtB1x_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEB8_,unique,17
	.p2align	2, 0x0
.LJTI14_0:
	.long	.LBB14_6-.LJTI14_0
	.long	.LBB14_8-.LJTI14_0
	.long	.LBB14_3-.LJTI14_0
	.long	.LBB14_7-.LJTI14_0
.LJTI14_1:
	.long	.LBB14_18-.LJTI14_1
	.long	.LBB14_20-.LJTI14_1
	.long	.LBB14_15-.LJTI14_1
	.long	.LBB14_19-.LJTI14_1
.LJTI14_2:
	.long	.LBB14_27-.LJTI14_2
	.long	.LBB14_29-.LJTI14_2
	.long	.LBB14_24-.LJTI14_2
	.long	.LBB14_28-.LJTI14_2
	.section	.text,"xr",one_only,_RINvXsd_NtCsavOST1yGCNT_10serde_json3serNtB6_15PrettyFormatterNtB6_9Formatter10end_objectQNtNvXs_NtB8_5valueNtB1x_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEB8_,unique,16
	.seh_endproc

	.def	_RINvXsd_NtCsavOST1yGCNT_10serde_json3serNtB6_15PrettyFormatterNtB6_9Formatter9end_arrayQNtNvXs_NtB8_5valueNtB1v_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEB8_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvXsd_NtCsavOST1yGCNT_10serde_json3serNtB6_15PrettyFormatterNtB6_9Formatter9end_arrayQNtNvXs_NtB8_5valueNtB1v_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEB8_,unique,18
	.p2align	4
_RINvXsd_NtCsavOST1yGCNT_10serde_json3serNtB6_15PrettyFormatterNtB6_9Formatter9end_arrayQNtNvXs_NtB8_5valueNtB1v_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEB8_:
.Lfunc_begin15:
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
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.29(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB15_32
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rsi
	leaq	.LJTI15_2(%rip), %r14
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.29(%rip), %rdi
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
	.section	.rdata,"dr",associative,_RINvXsd_NtCsavOST1yGCNT_10serde_json3serNtB6_15PrettyFormatterNtB6_9Formatter9end_arrayQNtNvXs_NtB8_5valueNtB1v_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEB8_,unique,19
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
	.section	.text,"xr",one_only,_RINvXsd_NtCsavOST1yGCNT_10serde_json3serNtB6_15PrettyFormatterNtB6_9Formatter9end_arrayQNtNvXs_NtB8_5valueNtB1v_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEB8_,unique,18
	.seh_endproc

	.def	_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io,unique,20
	.globl	_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io
	.p2align	4
_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io:
.Lfunc_begin16:
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
	je	.LBB16_1
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
.LBB16_1:
.Ltmp48:
	movl	$8, %ecx
	movl	$40, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp49:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io@IMGREL
	.section	.text$unlikely,"xr",one_only,_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io,unique,20
	.seh_endproc
	.def	"?dtor$3@?0?_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$3@?0?_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io@4HA":
.seh_proc "?dtor$3@?0?_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io@4HA"
.LBB16_3:
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
.Lfunc_end16:
	.seh_handlerdata
	.section	.text$unlikely,"xr",one_only,_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io,unique,20
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
	.long	.Lfunc_begin16@IMGREL
	.long	-1
	.long	.Ltmp48@IMGREL
	.long	0
	.long	.Ltmp49@IMGREL
	.long	-1
	.section	.text$unlikely,"xr",one_only,_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io,unique,20

	.def	_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax,unique,21
	.globl	_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax
	.p2align	4
_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax:
.Lfunc_begin17:
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
	je	.LBB17_1
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
.LBB17_1:
.Ltmp50:
	movl	$8, %ecx
	movl	$40, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp51:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax@IMGREL
	.section	.text$unlikely,"xr",one_only,_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax,unique,21
	.seh_endproc
	.def	"?dtor$3@?0?_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$3@?0?_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax@4HA":
.seh_proc "?dtor$3@?0?_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax@4HA"
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
	.section	.text$unlikely,"xr",one_only,_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax,unique,21
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
	.long	.Lfunc_begin17@IMGREL
	.long	-1
	.long	.Ltmp50@IMGREL
	.long	0
	.long	.Ltmp51@IMGREL
	.long	-1
	.section	.text$unlikely,"xr",one_only,_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error6syntax,unique,21

	.def	_RNvMs2_NtCsavOST1yGCNT_10serde_json2deNtB5_12ParserNumber12invalid_type;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs2_NtCsavOST1yGCNT_10serde_json2deNtB5_12ParserNumber12invalid_type,unique,22
	.globl	_RNvMs2_NtCsavOST1yGCNT_10serde_json2deNtB5_12ParserNumber12invalid_type
	.p2align	4
_RNvMs2_NtCsavOST1yGCNT_10serde_json2deNtB5_12ParserNumber12invalid_type:
.Lfunc_begin18:
.seh_proc _RNvMs2_NtCsavOST1yGCNT_10serde_json2deNtB5_12ParserNumber12invalid_type
	subq	$56, %rsp
	.seh_stackalloc 56
	.seh_endprologue
	movq	(%rcx), %rax
	testq	%rax, %rax
	je	.LBB18_4
	cmpl	$1, %eax
	jne	.LBB18_5
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
.LBB18_4:
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
.LBB18_5:
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
.Lfunc_end18:
	.seh_endproc

	.def	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_,unique,23
	.p2align	4
_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_:
.Lfunc_begin19:
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
	jne	.LBB19_2
	subq	%rbx, %rdx
	leaq	1(%rdx), %r14
	cmpq	%rdi, %rdx
	jb	.LBB19_3
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
.LBB19_2:
	xorl	%r14d, %r14d
.LBB19_3:
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
	.section	.text$unlikely,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_,unique,23
	.seh_endproc
	.def	"?dtor$9@?0?_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$9@?0?_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_@4HA":
.seh_proc "?dtor$9@?0?_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_@4HA"
.LBB19_9:
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
	jne	.LBB19_10
.LBB19_11:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.LBB19_10:
	movq	-24(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5error9ErrorCodeEBF_
	jmp	.LBB19_11
.Lfunc_end19:
	.seh_handlerdata
	.section	.text$unlikely,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_,unique,23
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
	.long	.Lfunc_begin19@IMGREL
	.long	-1
	.long	.Ltmp52@IMGREL
	.long	0
	.long	.Ltmp59@IMGREL
	.long	-1
	.section	.text$unlikely,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_,unique,23

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
	.section	.text,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE14parse_exponentB7_,unique,24
	.p2align	4
_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE14parse_exponentB7_:
.Lfunc_begin20:
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
	jae	.LBB20_5
	movq	24(%rdx), %rax
	movzbl	(%rax,%r10), %edi
	movb	$1, %al
	cmpl	$43, %edi
	je	.LBB20_4
	cmpl	$45, %edi
	jne	.LBB20_5
	xorl	%eax, %eax
.LBB20_4:
	addq	$2, %r11
	movq	%r11, 40(%rdx)
	movq	%r11, %r10
.LBB20_5:
	cmpq	%rsi, %r10
	jae	.LBB20_8
	movq	24(%rdx), %rdi
	movzbl	(%rdi,%r10), %r11d
	leaq	1(%r10), %rbx
	movq	%rbx, 40(%rdx)
	addb	$-48, %r11b
	cmpb	$10, %r11b
	jae	.LBB20_7
	movzbl	%r11b, %r11d
	cmpq	%rsi, %rbx
	jae	.LBB20_13
	movl	$1, %ebx
	subq	%rsi, %rbx
	addq	$2, %r10
	jmp	.LBB20_12
	.p2align	4
.LBB20_33:
	movzbl	%sil, %esi
	leal	(%r11,%r11,4), %r11d
	leal	(%rsi,%r11,2), %r11d
	leaq	(%rbx,%r10), %rsi
	incq	%rsi
	incq	%r10
	cmpq	$2, %rsi
	je	.LBB20_13
.LBB20_12:
	movzbl	-1(%rdi,%r10), %esi
	addb	$-48, %sil
	cmpb	$10, %sil
	jae	.LBB20_13
	movq	%r10, 40(%rdx)
	cmpl	$214748363, %r11d
	jle	.LBB20_33
	cmpl	$214748364, %r11d
	jne	.LBB20_34
	cmpb	$7, %sil
	jbe	.LBB20_33
.LBB20_34:
	testq	%r9, %r9
	sete	%r9b
	movb	%al, 32(%rsp)
	callq	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE23parse_exponent_overflowB7_
	jmp	.LBB20_29
.LBB20_13:
	movl	128(%rsp), %r10d
	testb	%al, %al
	je	.LBB20_14
	leal	(%r10,%r11), %eax
	sarl	$31, %eax
	addl	$-2147483648, %eax
	addl	%r11d, %r10d
	jmp	.LBB20_16
.LBB20_14:
	xorl	%eax, %eax
	cmpl	%r11d, %r10d
	setns	%al
	addl	$2147483647, %eax
	subl	%r11d, %r10d
.LBB20_16:
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
	jb	.LBB20_21
	xorpd	%xmm1, %xmm1
	movsd	__real@7fe1ccf385ebc8a0(%rip), %xmm2
	.p2align	4
.LBB20_18:
	ucomisd	%xmm1, %xmm0
	jne	.LBB20_19
	jnp	.LBB20_23
.LBB20_19:
	testl	%r10d, %r10d
	jns	.LBB20_27
	divsd	%xmm2, %xmm0
	addl	$308, %r10d
	movl	%r10d, %eax
	negl	%eax
	cmovsl	%r10d, %eax
	cmpl	$309, %eax
	jae	.LBB20_18
.LBB20_21:
	movl	%eax, %eax
	leaq	_RNvNtCsavOST1yGCNT_10serde_json2de5POW10(%rip), %r9
	movsd	(%r9,%rax,8), %xmm1
	testl	%r10d, %r10d
	js	.LBB20_22
	mulsd	%xmm1, %xmm0
	movq	%xmm0, %rax
	movabsq	$9223372036854775807, %r9
	andq	%rax, %r9
	movabsq	$9218868437227405312, %rax
	cmpq	%rax, %r9
	je	.LBB20_27
.LBB20_23:
	testb	%r8b, %r8b
	jne	.LBB20_25
.LBB20_24:
	xorpd	__xmm@80000000000000008000000000000000(%rip), %xmm0
.LBB20_25:
	movsd	%xmm0, 8(%rcx)
	xorl	%eax, %eax
.LBB20_28:
	movq	%rax, (%rcx)
.LBB20_29:
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB20_22:
	divsd	%xmm1, %xmm0
	testb	%r8b, %r8b
	je	.LBB20_24
	jmp	.LBB20_25
.LBB20_8:
	movq	$5, 40(%rsp)
.LBB20_9:
	leaq	40(%rsp), %rax
	movq	%rcx, %rsi
	movq	%rdx, %rcx
	movq	%rax, %rdx
	callq	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_
	movq	%rax, 8(%rsi)
	movq	$1, (%rsi)
	jmp	.LBB20_29
.LBB20_27:
	movq	$14, 40(%rsp)
	leaq	40(%rsp), %rax
	movq	%rcx, %rsi
	movq	%rdx, %rcx
	movq	%rax, %rdx
	callq	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_
	movq	%rsi, %rcx
	movq	%rax, 8(%rsi)
	movl	$1, %eax
	jmp	.LBB20_28
.LBB20_7:
	movq	$13, 40(%rsp)
	jmp	.LBB20_9
.Lfunc_end20:
	.seh_endproc

	.def	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE18parse_long_integerB7_;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE18parse_long_integerB7_,unique,25
	.globl	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE18parse_long_integerB7_
	.p2align	4
_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE18parse_long_integerB7_:
.Lfunc_begin21:
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
	jae	.LBB21_8
	movq	24(%rdx), %rsi
	movl	%ebx, %edi
	subl	%r10d, %edi
	leal	-1(%rbx), %r11d
	leaq	(%rsi,%r10), %r15
	xorl	%eax, %eax
	.p2align	4
.LBB21_2:
	movzbl	(%r15,%rax), %r12d
	leal	-48(%r12), %ebp
	cmpb	$10, %bpl
	jae	.LBB21_3
	leaq	(%r10,%rax), %r12
	incq	%r12
	movq	%r12, 40(%rdx)
	incq	%rax
	addq	$-2, %r11
	movq	%r14, %r12
	addq	%rax, %r12
	jne	.LBB21_2
	jmp	.LBB21_8
.LBB21_3:
	cmpl	$46, %r12d
	je	.LBB21_18
	cmpl	$69, %r12d
	je	.LBB21_37
	cmpl	$101, %r12d
	je	.LBB21_37
	movl	%eax, %edi
.LBB21_8:
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
	jb	.LBB21_13
	xorpd	%xmm1, %xmm1
	movsd	__real@7fe1ccf385ebc8a0(%rip), %xmm2
	.p2align	4
.LBB21_10:
	ucomisd	%xmm1, %xmm0
	jne	.LBB21_11
	jnp	.LBB21_15
.LBB21_11:
	testl	%edi, %edi
	jns	.LBB21_35
	divsd	%xmm2, %xmm0
	addl	$308, %edi
	movl	%edi, %eax
	negl	%eax
	cmovsl	%edi, %eax
	cmpl	$309, %eax
	jae	.LBB21_10
.LBB21_13:
	movl	%eax, %eax
	leaq	_RNvNtCsavOST1yGCNT_10serde_json2de5POW10(%rip), %r9
	movsd	(%r9,%rax,8), %xmm1
	testl	%edi, %edi
	js	.LBB21_14
.LBB21_34:
	mulsd	%xmm1, %xmm0
	movq	%xmm0, %rax
	movabsq	$9223372036854775807, %r9
	andq	%rax, %r9
	movabsq	$9218868437227405312, %rax
	cmpq	%rax, %r9
	jne	.LBB21_15
.LBB21_35:
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
	jmp	.LBB21_39
.LBB21_18:
	leaq	(%r10,%rax), %rdi
	incq	%rdi
	movq	%rdi, 40(%rdx)
	cmpq	%rbx, %rdi
	jae	.LBB21_26
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
	jmp	.LBB21_20
	.p2align	4
.LBB21_43:
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
	je	.LBB21_24
.LBB21_20:
	movzbl	-1(%rsi,%r14), %ebp
	leal	-48(%rbp), %r13d
	cmpb	$10, %r13b
	jae	.LBB21_21
	cmpq	%r15, %r9
	jbe	.LBB21_43
	leaq	1(%r15), %rbp
	cmpq	%rbp, %r9
	jne	.LBB21_44
	cmpb	$5, %r13b
	jbe	.LBB21_43
.LBB21_44:
	subl	%ebx, %eax
	movl	%eax, 32(%rsp)
	movq	%rcx, %rsi
	callq	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE22parse_decimal_overflowB7_
	jmp	.LBB21_38
.LBB21_21:
	testl	%ebx, %ebx
	je	.LBB21_22
	subl	%ebx, %eax
	orl	$32, %ebp
	cmpl	$101, %ebp
	jne	.LBB21_28
.LBB21_37:
	movl	%eax, 32(%rsp)
	movq	%rcx, %rsi
	callq	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE14parse_exponentB7_
.LBB21_38:
	movq	%rsi, %rax
	jmp	.LBB21_39
.LBB21_24:
	testl	%edi, %edi
	je	.LBB21_26
	subl	%r11d, %r10d
	movl	%r10d, %eax
.LBB21_28:
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
	jb	.LBB21_33
	xorpd	%xmm1, %xmm1
	movsd	__real@7fe1ccf385ebc8a0(%rip), %xmm2
	.p2align	4
.LBB21_30:
	ucomisd	%xmm1, %xmm0
	jne	.LBB21_31
	jnp	.LBB21_15
.LBB21_31:
	testl	%eax, %eax
	jns	.LBB21_35
	divsd	%xmm2, %xmm0
	addl	$308, %eax
	movl	%eax, %r9d
	negl	%r9d
	cmovsl	%eax, %r9d
	cmpl	$309, %r9d
	jae	.LBB21_30
.LBB21_33:
	movl	%r9d, %r9d
	leaq	_RNvNtCsavOST1yGCNT_10serde_json2de5POW10(%rip), %r10
	movsd	(%r10,%r9,8), %xmm1
	testl	%eax, %eax
	jns	.LBB21_34
.LBB21_14:
	divsd	%xmm1, %xmm0
.LBB21_15:
	testb	%r8b, %r8b
	jne	.LBB21_17
	xorpd	__xmm@80000000000000008000000000000000(%rip), %xmm0
.LBB21_17:
	movsd	%xmm0, 8(%rcx)
	xorl	%eax, %eax
	movq	%rax, (%rcx)
	movq	%rcx, %rax
.LBB21_39:
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
.LBB21_26:
	movq	$5, 48(%rsp)
	jmp	.LBB21_23
.LBB21_22:
	movq	$13, 48(%rsp)
.LBB21_23:
	leaq	48(%rsp), %rax
	movq	%rcx, %rsi
	movq	%rdx, %rcx
	movq	%rax, %rdx
	callq	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE10peek_errorB7_
	movq	%rax, 8(%rsi)
	movq	$1, (%rsi)
	movq	%rsi, %rax
	jmp	.LBB21_39
.Lfunc_end21:
	.seh_endproc

	.def	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE22parse_decimal_overflowB7_;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE22parse_decimal_overflowB7_,unique,26
	.globl	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE22parse_decimal_overflowB7_
	.p2align	4
_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE22parse_decimal_overflowB7_:
.Lfunc_begin22:
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
	jae	.LBB22_5
	movq	24(%rdx), %rsi
	negq	%r10
	incq	%r11
	.p2align	4
.LBB22_2:
	movzbl	-1(%rsi,%r11), %edi
	leal	-48(%rdi), %ebx
	cmpb	$9, %bl
	ja	.LBB22_4
	movq	%r11, 40(%rdx)
	leaq	(%r10,%r11), %rdi
	incq	%rdi
	incq	%r11
	cmpq	$1, %rdi
	jne	.LBB22_2
	jmp	.LBB22_5
.LBB22_4:
	orl	$32, %edi
	cmpl	$101, %edi
	jne	.LBB22_5
	movl	%eax, 32(%rsp)
	movq	%rcx, %rsi
	callq	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE14parse_exponentB7_
	movq	%rsi, %rax
	jmp	.LBB22_18
.LBB22_5:
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
	jb	.LBB22_10
	xorpd	%xmm1, %xmm1
	movsd	__real@7fe1ccf385ebc8a0(%rip), %xmm2
	.p2align	4
.LBB22_7:
	ucomisd	%xmm1, %xmm0
	jne	.LBB22_8
	jnp	.LBB22_12
.LBB22_8:
	testl	%eax, %eax
	jns	.LBB22_16
	divsd	%xmm2, %xmm0
	addl	$308, %eax
	movl	%eax, %r9d
	negl	%r9d
	cmovsl	%eax, %r9d
	cmpl	$309, %r9d
	jae	.LBB22_7
.LBB22_10:
	movl	%r9d, %r9d
	leaq	_RNvNtCsavOST1yGCNT_10serde_json2de5POW10(%rip), %r10
	movsd	(%r10,%r9,8), %xmm1
	testl	%eax, %eax
	js	.LBB22_11
	mulsd	%xmm1, %xmm0
	movq	%xmm0, %rax
	movabsq	$9223372036854775807, %r9
	andq	%rax, %r9
	movabsq	$9218868437227405312, %rax
	cmpq	%rax, %r9
	je	.LBB22_16
.LBB22_12:
	testb	%r8b, %r8b
	jne	.LBB22_14
.LBB22_13:
	xorpd	__xmm@80000000000000008000000000000000(%rip), %xmm0
.LBB22_14:
	movsd	%xmm0, 8(%rcx)
	xorl	%eax, %eax
.LBB22_17:
	movq	%rax, (%rcx)
	movq	%rcx, %rax
.LBB22_18:
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB22_11:
	divsd	%xmm1, %xmm0
	testb	%r8b, %r8b
	je	.LBB22_13
	jmp	.LBB22_14
.LBB22_16:
	movq	$14, 40(%rsp)
	leaq	40(%rsp), %rax
	movq	%rcx, %rsi
	movq	%rdx, %rcx
	movq	%rax, %rdx
	callq	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_
	movq	%rsi, %rcx
	movq	%rax, 8(%rsi)
	movl	$1, %eax
	jmp	.LBB22_17
.Lfunc_end22:
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
	.section	.text$unlikely,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE23parse_exponent_overflowB7_,unique,27
	.globl	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE23parse_exponent_overflowB7_
	.p2align	4
_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE23parse_exponent_overflowB7_:
.Lfunc_begin23:
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
	jne	.LBB23_9
	movq	32(%rdx), %rcx
	movq	40(%rdx), %r9
	cmpq	%rcx, %r9
	jae	.LBB23_5
	movq	24(%rdx), %r10
	negq	%rcx
	incq	%r9
	.p2align	4
.LBB23_3:
	movzbl	-1(%r10,%r9), %r11d
	addb	$-48, %r11b
	cmpb	$10, %r11b
	jae	.LBB23_5
	movq	%r9, 40(%rdx)
	leaq	(%rcx,%r9), %r11
	incq	%r11
	incq	%r9
	cmpq	$1, %r11
	jne	.LBB23_3
.LBB23_5:
	xorps	%xmm0, %xmm0
	testb	%r8b, %r8b
	jne	.LBB23_7
	movsd	__real@8000000000000000(%rip), %xmm0
.LBB23_7:
	movsd	%xmm0, 8(%rax)
	xorl	%ecx, %ecx
	movq	%rcx, (%rax)
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB23_9:
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
.Lfunc_end23:
	.seh_endproc

	.def	_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_,unique,28
	.p2align	4
_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_:
.Lfunc_begin24:
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
	ja	.LBB24_9
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
	jne	.LBB24_3
	subq	%rbx, %rdx
	leaq	1(%rdx), %r14
	cmpq	%rdi, %rdx
	jb	.LBB24_4
	movb	$1, -9(%rbp)
.Ltmp62:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920(%rip), %r9
	xorl	%ecx, %ecx
	movq	%r14, %rdx
	movq	%rdi, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	nop
.Ltmp63:
	jmp	.LBB24_10
.LBB24_3:
	xorl	%r14d, %r14d
.LBB24_4:
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
.LBB24_9:
	movb	$1, -9(%rbp)
.Ltmp68:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.48.llvm.16186315980599473920(%rip), %r9
	xorl	%ecx, %ecx
	movq	%rsi, %rdx
	movq	%rdi, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	nop
.Ltmp69:
.LBB24_10:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_@IMGREL
	.section	.text$unlikely,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_,unique,28
	.seh_endproc
	.def	"?dtor$11@?0?_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$11@?0?_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_@4HA":
.seh_proc "?dtor$11@?0?_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_@4HA"
.LBB24_11:
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
	jne	.LBB24_12
.LBB24_13:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.LBB24_12:
	movq	-24(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsavOST1yGCNT_10serde_json5error9ErrorCodeEBF_
	jmp	.LBB24_13
.Lfunc_end24:
	.seh_handlerdata
	.section	.text$unlikely,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_,unique,28
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
	.long	.Lfunc_begin24@IMGREL
	.long	-1
	.long	.Ltmp60@IMGREL
	.long	0
	.long	.Ltmp69@IMGREL
	.long	-1
	.section	.text$unlikely,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json2deINtB5_12DeserializerNtNtB7_4read7StrReadE5errorB7_,unique,28

	.def	_RNvMs3_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceRead14skip_to_escape;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceRead14skip_to_escape,unique,29
	.p2align	4
_RNvMs3_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceRead14skip_to_escape:
.Lfunc_begin25:
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
	je	.LBB25_9
	jae	.LBB25_10
	movq	(%rcx), %r8
	movzbl	(%r8,%rax), %r9d
	cmpl	$34, %r9d
	je	.LBB25_9
	cmpl	$92, %r9d
	je	.LBB25_9
	cmpb	$32, %r9b
	jb	.LBB25_9
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
.LBB25_6:
	leaq	(%r11,%rax), %r12
	cmpq	$1, %r12
	je	.LBB25_11
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
	je	.LBB25_6
	rep		bsfq	%r12, %rax
	shrl	$3, %eax
	subq	%r10, %rax
	movq	%rax, 16(%rcx)
.LBB25_9:
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
.LBB25_11:
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
.LBB25_10:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.46(%rip), %r8
	movq	%rax, %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	ud2
.Lfunc_end25:
	.seh_endproc

	.def	_RNvMs3_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceRead19skip_to_escape_slow;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs3_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceRead19skip_to_escape_slow,unique,30
	.p2align	4
_RNvMs3_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceRead19skip_to_escape_slow:
.Lfunc_begin26:
	movq	8(%rcx), %rax
	movq	16(%rcx), %rdx
	cmpq	%rax, %rdx
	jae	.LBB26_6
	movq	(%rcx), %r8
	negq	%rax
	incq	%rdx
	.p2align	4
.LBB26_2:
	movzbl	-1(%r8,%rdx), %r9d
	cmpl	$34, %r9d
	je	.LBB26_6
	cmpl	$92, %r9d
	je	.LBB26_6
	cmpb	$32, %r9b
	jb	.LBB26_6
	movq	%rdx, 16(%rcx)
	leaq	(%rax,%rdx), %r9
	incq	%r9
	incq	%rdx
	cmpq	$1, %r9
	jne	.LBB26_2
.LBB26_6:
	retq
.Lfunc_end26:

	.def	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtNtCsavOST1yGCNT_10serde_json5value5ValueE8grow_oneBQ_;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtNtCsavOST1yGCNT_10serde_json5value5ValueE8grow_oneBQ_,unique,31
	.globl	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtNtCsavOST1yGCNT_10serde_json5value5ValueE8grow_oneBQ_
	.p2align	4
_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtNtCsavOST1yGCNT_10serde_json5value5ValueE8grow_oneBQ_:
.Lfunc_begin27:
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
	je	.LBB27_1
	movq	56(%rsp), %rax
	movq	%rax, 8(%rsi)
	movq	%rdi, (%rsi)
	.seh_startepilogue
	addq	$72, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB27_1:
	movq	56(%rsp), %rcx
	movq	64(%rsp), %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.Lfunc_end27:
	.seh_endproc

	.def	_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCsavOST1yGCNT_10serde_json;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCsavOST1yGCNT_10serde_json,unique,32
	.p2align	4
_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCsavOST1yGCNT_10serde_json:
.Lfunc_begin28:
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
	je	.LBB28_2
	movl	$8, %eax
	xorl	%edi, %edi
	jmp	.LBB28_10
.LBB28_2:
	testq	%r9, %r9
	je	.LBB28_4
	movq	%r8, %rcx
	movq	%rdi, %rdx
	movq	%rbx, %r8
	callq	mi_realloc_aligned
	testq	%rax, %rax
	jne	.LBB28_6
	jmp	.LBB28_9
.LBB28_4:
	testq	%rdi, %rdi
	je	.LBB28_5
	movq	%rdi, %rcx
	movq	%rbx, %rdx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	jne	.LBB28_6
.LBB28_9:
	movq	%rbx, 8(%rsi)
	movl	$16, %eax
	jmp	.LBB28_10
.LBB28_5:
	movq	%rbx, %rax
.LBB28_6:
	movq	%rax, 8(%rsi)
	movl	$16, %eax
	xorl	%r14d, %r14d
.LBB28_10:
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
.Lfunc_end28:
	.seh_endproc

	.def	_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_,unique,33
	.p2align	4
_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_:
.Lfunc_begin29:
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
	je	.LBB29_1
	decq	%rax
	movq	%rax, 64(%rdx)
	cmpl	$1, (%rdx)
	jne	.LBB29_49
	movq	8(%rdx), %rcx
	testq	%rcx, %rcx
	je	.LBB29_21
	movq	16(%rdx), %rdi
	movq	24(%rdx), %rbx
	movzwl	626(%rcx), %eax
	cmpq	%rax, %rbx
	jae	.LBB29_31
.LBB29_30:
	movq	%rcx, %r14
	testq	%rdi, %rdi
	je	.LBB29_36
.LBB29_39:
	leaq	(%r14,%rbx,8), %rax
	addq	$640, %rax
	movq	%rdi, %r8
	andq	$7, %r8
	je	.LBB29_40
	xorl	%r10d, %r10d
	.p2align	4
.LBB29_42:
	movq	(%rax), %rcx
	leaq	632(%rcx), %rax
	incq	%r10
	cmpq	%r10, %r8
	jne	.LBB29_42
	movq	%rdi, %r9
	subq	%r10, %r9
	xorl	%r8d, %r8d
	cmpq	$8, %rdi
	jae	.LBB29_45
	jmp	.LBB29_37
.LBB29_1:
	movq	(%rdx), %r9
	movq	8(%rdx), %rcx
	movq	16(%rdx), %rax
	movq	24(%rdx), %r8
	movq	$0, (%rdx)
	cmpq	$1, %r9
	jne	.LBB29_17
	testq	%rcx, %rcx
	je	.LBB29_3
.LBB29_13:
	movq	352(%rcx), %rax
	testq	%rax, %rax
	je	.LBB29_14
	.p2align	4
.LBB29_15:
	movq	%rax, %rdi
	callq	mi_free
	movq	352(%rdi), %rax
	movq	%rdi, %rcx
	testq	%rax, %rax
	jne	.LBB29_15
	jmp	.LBB29_16
.LBB29_21:
	movq	16(%rdx), %rcx
	movq	24(%rdx), %rax
	testq	%rax, %rax
	je	.LBB29_28
	movq	%rax, %r8
	andq	$7, %r8
	je	.LBB29_23
	xorl	%r9d, %r9d
	.p2align	4
.LBB29_25:
	movq	632(%rcx), %rcx
	incq	%r9
	cmpq	%r9, %r8
	jne	.LBB29_25
	movq	%rax, %r8
	subq	%r9, %r8
	cmpq	$8, %rax
	jb	.LBB29_28
	.p2align	4
.LBB29_50:
	movq	632(%rcx), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rcx
	addq	$-8, %r8
	jne	.LBB29_50
.LBB29_28:
	movq	$1, (%rdx)
	xorl	%ebx, %ebx
	xorl	%edi, %edi
	movzwl	626(%rcx), %eax
	cmpq	%rax, %rbx
	jb	.LBB29_30
.LBB29_31:
	movq	%rdx, %r15
	.p2align	4
.LBB29_32:
	movq	352(%rcx), %r14
	testq	%r14, %r14
	je	.LBB29_46
	incq	%rdi
	movzwl	624(%rcx), %ebx
	callq	mi_free
	movq	%r14, %rcx
	cmpw	626(%r14), %bx
	jae	.LBB29_32
	movq	%r15, %rdx
	testq	%rdi, %rdi
	jne	.LBB29_39
.LBB29_36:
	leaq	1(%rbx), %r8
	movq	%r14, %rcx
	jmp	.LBB29_37
.LBB29_40:
	movq	%rdi, %r9
	xorl	%r8d, %r8d
	cmpq	$8, %rdi
	jb	.LBB29_37
	.p2align	4
.LBB29_45:
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
	jne	.LBB29_45
.LBB29_37:
	movq	%rcx, 8(%rdx)
	movq	$0, 16(%rdx)
	movq	%r8, 24(%rdx)
	movq	%r14, (%rsi)
	movq	%rdi, 8(%rsi)
	movq	%rbx, 16(%rsi)
	jmp	.LBB29_38
.LBB29_3:
	testq	%r8, %r8
	je	.LBB29_4
	movq	%r8, %rcx
	andq	$7, %rcx
	je	.LBB29_6
	xorl	%r9d, %r9d
	.p2align	4
.LBB29_8:
	movq	632(%rax), %rax
	incq	%r9
	cmpq	%r9, %rcx
	jne	.LBB29_8
	movq	%r8, %rdx
	subq	%r9, %rdx
	jmp	.LBB29_10
.LBB29_14:
	movq	%rcx, %rdi
.LBB29_16:
	movq	%rdi, %rcx
	callq	mi_free
.LBB29_17:
	movq	$0, (%rsi)
.LBB29_38:
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
.LBB29_23:
	movq	%rax, %r8
	cmpq	$8, %rax
	jae	.LBB29_50
	jmp	.LBB29_28
.LBB29_4:
	movq	%rax, %rcx
	jmp	.LBB29_13
.LBB29_6:
	movq	%r8, %rdx
.LBB29_10:
	movq	%rax, %rcx
	cmpq	$8, %r8
	jb	.LBB29_13
	movq	%rax, %rcx
	.p2align	4
.LBB29_12:
	movq	632(%rcx), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rax
	movq	632(%rax), %rcx
	addq	$-8, %rdx
	jne	.LBB29_12
	jmp	.LBB29_13
.LBB29_46:
	callq	mi_free
	nop
.Ltmp70:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.36(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	nop
.Ltmp71:
	ud2
.LBB29_49:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.13(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_@IMGREL
	.section	.text,"xr",one_only,_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_,unique,33
	.seh_endproc
	.def	"?dtor$48@?0?_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$48@?0?_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_@4HA":
.seh_proc "?dtor$48@?0?_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_@4HA"
.LBB29_48:
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
.Lfunc_end29:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_,unique,33
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
	.long	.Lfunc_begin29@IMGREL
	.long	-1
	.long	.Ltmp70@IMGREL
	.long	0
	.long	.Ltmp71@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvMsz_NtNtNtCsfQUUnEvlYZE_5alloc11collections5btree3mapINtB5_8IntoIterNtNtBb_6string6StringNtNtCsavOST1yGCNT_10serde_json5value5ValueE10dying_nextB1w_,unique,33

	.def	_RNvNtCsavOST1yGCNT_10serde_json5error10make_error;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNtCsavOST1yGCNT_10serde_json5error10make_error,unique,34
	.globl	_RNvNtCsavOST1yGCNT_10serde_json5error10make_error
	.p2align	4
_RNvNtCsavOST1yGCNT_10serde_json5error10make_error:
.Lfunc_begin30:
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
	je	.LBB30_17
	cmpq	$-1, -16(%rbp)
	movq	(%rbp), %rax
	movq	8(%rbp), %r8
	movq	16(%rbp), %r9
	movq	24(%rbp), %rdx
	je	.LBB30_21
	movq	-24(%rbp), %r14
	movq	%r14, %r11
	subq	%rdx, %r11
	cmpq	%r8, %r11
	jae	.LBB30_56
	movq	-40(%rbp), %r10
	movq	-56(%rbp), %rdi
	movq	-48(%rbp), %rcx
	movq	%rcx, 40(%rbp)
	movq	-8(%rbp), %r15
	jmp	.LBB30_5
.LBB30_17:
	cmpb	$0, -46(%rbp)
	jne	.LBB30_56
	movzbl	-47(%rbp), %eax
	movq	-56(%rbp), %r9
	testq	%r9, %r9
	je	.LBB30_40
	movq	(%rbp), %rcx
	movq	8(%rbp), %rdx
	cmpq	%rdx, %r9
	jae	.LBB30_41
	cmpb	$-64, (%rcx,%r9)
	movq	48(%rbp), %r15
	jge	.LBB30_42
	jmp	.LBB30_69
	.p2align	4
.LBB30_10:
	subq	%rdi, %r14
	leaq	(%r14,%r13), %r11
	incq	%r11
.LBB30_11:
	movq	%rdx, %r15
	movq	%r11, %r14
	subq	%rdx, %r11
	cmpq	%r8, %r11
	jae	.LBB30_56
.LBB30_5:
	movzbl	(%rax,%r11), %ecx
	btq	%rcx, %r10
	jae	.LBB30_11
	cmpq	%rdi, %r15
	movq	%rdi, %rcx
	cmovbq	%r15, %rcx
	decq	%rcx
	leaq	(%rax,%r11), %r12
	.p2align	4
.LBB30_7:
	cmpq	$-1, %rcx
	je	.LBB30_12
	cmpq	%rdx, %rcx
	jae	.LBB30_165
	movzbl	(%r9,%rcx), %ebx
	leaq	-1(%rcx), %r13
	cmpb	(%r12,%rcx), %bl
	movq	%r13, %rcx
	je	.LBB30_7
	jmp	.LBB30_10
	.p2align	4
.LBB30_12:
	movq	%rdi, %rcx
	.p2align	4
.LBB30_13:
	cmpq	%r15, %rcx
	jae	.LBB30_48
	cmpq	%rdx, %rcx
	jae	.LBB30_166
	movzbl	(%r9,%rcx), %r13d
	cmpb	(%r12,%rcx), %r13b
	leaq	1(%rcx), %rcx
	je	.LBB30_13
	movq	40(%rbp), %r15
	subq	%r15, %r14
	movq	%r14, %r11
	movq	%r11, %r14
	subq	%rdx, %r11
	cmpq	%r8, %r11
	jb	.LBB30_5
	jmp	.LBB30_56
.LBB30_21:
	movq	-24(%rbp), %rdi
	movq	%rdi, %r11
	subq	%rdx, %r11
	cmpq	%r8, %r11
	jae	.LBB30_56
	movq	-40(%rbp), %r10
	movq	-56(%rbp), %rcx
	movq	-48(%rbp), %rbx
	movq	%rbx, 40(%rbp)
	leaq	-1(%rcx), %rbx
	movq	%rbx, -80(%rbp)
	cmpq	%rdx, %rbx
	jb	.LBB30_32
	testq	%rcx, %rcx
	je	.LBB30_51
	movzbl	(%rax,%r11), %ecx
	btq	%rcx, %r10
	jb	.LBB30_28
	subq	%rdx, %rdi
	subq	%rdx, %rdi
	.p2align	4
.LBB30_26:
	cmpq	%r8, %rdi
	jae	.LBB30_56
	movzbl	(%rax,%rdi), %ecx
	subq	%rdx, %rdi
	btq	%rcx, %r10
	jae	.LBB30_26
.LBB30_28:
	movb	$0, 63(%rbp)
.Ltmp80:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.17(%rip), %r8
	movq	-80(%rbp), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	nop
.Ltmp81:
	jmp	.LBB30_169
.LBB30_30:
	movq	%r11, %r15
.LBB30_31:
	movq	%r15, %r11
	subq	%rdx, %r11
	movq	%r15, %rdi
	cmpq	%r8, %r11
	jae	.LBB30_56
.LBB30_32:
	movzbl	(%rax,%r11), %r14d
	btq	%r14, %r10
	jae	.LBB30_30
	leaq	-1(%rcx), %rbx
	leaq	(%rbx,%r11), %r12
	movq	%rdi, %r15
	movq	%rcx, %r14
	movq	%rcx, %r13
	.p2align	4
.LBB30_34:
	subq	$1, %r13
	jb	.LBB30_36
	movzbl	-1(%r9,%r14), %ebx
	decq	%r15
	movq	%r13, %r14
	cmpb	(%rax,%r12), %bl
	leaq	-1(%r12), %r12
	je	.LBB30_34
	jmp	.LBB30_31
.LBB30_36:
	leaq	(%rax,%r11), %r14
	movq	%rcx, %r15
	.p2align	4
.LBB30_37:
	cmpq	%r15, %rdx
	je	.LBB30_48
	movzbl	(%r9,%r15), %r12d
	cmpb	(%r14,%r15), %r12b
	leaq	1(%r15), %r15
	je	.LBB30_37
	subq	40(%rbp), %rdi
	movq	%rdi, %r15
	jmp	.LBB30_31
.LBB30_40:
	xorl	%r11d, %r11d
	testb	$1, %al
	movq	48(%rbp), %r15
	jne	.LBB30_74
	jmp	.LBB30_89
.LBB30_41:
	movq	48(%rbp), %r15
	jne	.LBB30_69
.LBB30_42:
	movzbl	-1(%rcx,%r9), %r8d
	movzbl	%r8b, %r8d
	testb	%r8b, %r8b
	js	.LBB30_45
	testb	$1, %al
	je	.LBB30_62
.LBB30_44:
	movq	%r9, %r11
	jmp	.LBB30_74
.LBB30_45:
	movzbl	-2(%rcx,%r9), %r10d
	cmpb	$-65, %r10b
	jg	.LBB30_49
	movzbl	-3(%rcx,%r9), %r11d
	cmpb	$-65, %r11b
	jg	.LBB30_59
	movzbl	-4(%rcx,%r9), %edi
	andl	$7, %edi
	shll	$6, %edi
	andl	$63, %r11d
	orl	%edi, %r11d
	jmp	.LBB30_60
.LBB30_49:
	andl	$31, %r10d
	jmp	.LBB30_61
.LBB30_50:
	movq	%r11, %rdi
	subq	%rdx, %r11
	cmpq	%r8, %r11
	jae	.LBB30_56
.LBB30_51:
	movzbl	(%rax,%r11), %ecx
	btq	%rcx, %r10
	jae	.LBB30_50
	leaq	(%rax,%r11), %rcx
	xorl	%ebx, %ebx
	.p2align	4
.LBB30_53:
	cmpq	%rbx, %rdx
	je	.LBB30_48
	movzbl	(%r9,%rbx), %r14d
	cmpb	(%rcx,%rbx), %r14b
	leaq	1(%rbx), %rbx
	je	.LBB30_53
	subq	40(%rbp), %rdi
	movq	%rdi, %r11
	subq	%rdx, %r11
	cmpq	%r8, %r11
	jb	.LBB30_51
.LBB30_56:
	xorl	%edi, %edi
	xorl	%ebx, %ebx
.LBB30_57:
	movq	48(%rbp), %r15
	jmp	.LBB30_91
.LBB30_48:
	movq	48(%rbp), %r15
.LBB30_74:
	leaq	9(%r11), %rax
	movq	%rax, %r8
	testq	%r8, %r8
	je	.LBB30_78
	.p2align	4
.LBB30_75:
	cmpq	%rsi, %r8
	jae	.LBB30_77
	cmpb	$-64, (%r15,%r8)
	jge	.LBB30_78
	jmp	.LBB30_167
	.p2align	4
.LBB30_77:
	jne	.LBB30_167
.LBB30_78:
	cmpq	%r8, %rsi
	je	.LBB30_81
	movzbl	(%r15,%r8), %ecx
	addb	$-48, %cl
	cmpb	$10, %cl
	jae	.LBB30_82
	incq	%r8
	testq	%r8, %r8
	jne	.LBB30_75
	jmp	.LBB30_78
.LBB30_81:
	movq	%rsi, %r9
	testq	%r8, %r8
	jne	.LBB30_83
	jmp	.LBB30_87
.LBB30_82:
	movq	%r8, %r9
	testq	%r8, %r8
	je	.LBB30_87
.LBB30_83:
	cmpq	%r9, %rsi
	jbe	.LBB30_86
	cmpb	$-65, (%r15,%r9)
	jg	.LBB30_87
.LBB30_85:
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
	jmp	.LBB30_169
.LBB30_86:
	jne	.LBB30_85
.LBB30_87:
	movq	%rsi, %rcx
	subq	%r9, %rcx
	cmpq	$8, %rcx
	jb	.LBB30_89
	movabsq	$2336925607749706528, %rcx
	cmpq	%rcx, (%r15,%r9)
	je	.LBB30_98
.LBB30_89:
	xorl	%edi, %edi
.LBB30_90:
	xorl	%ebx, %ebx
.LBB30_91:
	movq	%r15, %rax
	movq	32(%rbp), %rcx
	cmpq	%rsi, (%rcx)
	jbe	.LBB30_96
	testq	%rsi, %rsi
	je	.LBB30_95
	movl	$1, %r8d
	movq	%r15, %rcx
	movq	%rsi, %rdx
	callq	mi_realloc_aligned
	testq	%rax, %rax
	jne	.LBB30_96
.Ltmp94:
	movl	$1, %ecx
	movq	%rsi, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp95:
	jmp	.LBB30_169
.LBB30_95:
	movq	%r15, %rcx
	callq	mi_free
	movl	$1, %eax
.LBB30_96:
	movq	$0, -72(%rbp)
	movq	%rax, -64(%rbp)
	movq	%rsi, -56(%rbp)
	movq	%rdi, -48(%rbp)
	movq	%rbx, -40(%rbp)
	movl	$40, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB30_162
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
.LBB30_98:
	leaq	8(%r9), %r8
	movq	%r8, %r10
	testq	%r10, %r10
	je	.LBB30_102
	.p2align	4
.LBB30_99:
	cmpq	%rsi, %r10
	jae	.LBB30_101
	cmpb	$-64, (%r15,%r10)
	jge	.LBB30_102
	jmp	.LBB30_168
	.p2align	4
.LBB30_101:
	jne	.LBB30_168
.LBB30_102:
	cmpq	%r10, %rsi
	je	.LBB30_105
	movzbl	(%r15,%r10), %ecx
	addb	$-48, %cl
	cmpb	$10, %cl
	jae	.LBB30_106
	incq	%r10
	testq	%r10, %r10
	jne	.LBB30_99
	jmp	.LBB30_102
.LBB30_105:
	movq	%rsi, %r10
	jmp	.LBB30_107
.LBB30_106:
	cmpq	%rsi, %r10
	jb	.LBB30_89
.LBB30_107:
	movq	%r9, %rbx
	subq	%rax, %rbx
	jb	.LBB30_164
	testq	%rax, %rax
	je	.LBB30_110
	cmpb	$-64, (%r15,%rax)
	jl	.LBB30_164
.LBB30_110:
	cmpb	$-65, (%r15,%r9)
	jle	.LBB30_164
	cmpq	$1, %rbx
	je	.LBB30_114
	testq	%rbx, %rbx
	jne	.LBB30_117
	movq	%rbx, %rdi
	jmp	.LBB30_91
.LBB30_114:
	movzbl	(%r15,%rax), %ecx
	xorl	%edi, %edi
	cmpl	$43, %ecx
	je	.LBB30_90
	cmpl	$45, %ecx
	je	.LBB30_90
	jmp	.LBB30_118
.LBB30_117:
	movzbl	(%r15,%rax), %ecx
.LBB30_118:
	xorl	%eax, %eax
	cmpb	$43, %cl
	sete	%al
	movq	%rax, %rcx
	negq	%rcx
	subq	%rax, %rbx
	cmpq	$17, %rbx
	jae	.LBB30_123
	testq	%rbx, %rbx
	je	.LBB30_130
	addq	%r15, %rax
	addq	$9, %rax
	addq	%r9, %rcx
	addq	$-9, %rcx
	xorl	%ebx, %ebx
	movq	%r11, %rdx
	xorl	%edi, %edi
.LBB30_121:
	movzbl	(%rax,%rdx), %r14d
	addl	$-48, %r14d
	cmpl	$9, %r14d
	ja	.LBB30_139
	leaq	(%rdi,%rdi,4), %rdi
	movl	%r14d, %r14d
	leaq	(%r14,%rdi,2), %rdi
	incq	%rdx
	cmpq	%rdx, %rcx
	jne	.LBB30_121
	jmp	.LBB30_131
.LBB30_59:
	andl	$15, %r11d
.LBB30_60:
	shll	$6, %r11d
	andl	$63, %r10d
	orl	%r11d, %r10d
.LBB30_61:
	shll	$6, %r10d
	andl	$63, %r8d
	orl	%r10d, %r8d
	testb	$1, %al
	jne	.LBB30_44
.LBB30_62:
	movq	$-1, %r11
	cmpl	$128, %r8d
	jb	.LBB30_65
	movq	$-2, %r11
	cmpl	$2048, %r8d
	jb	.LBB30_65
	xorl	%r11d, %r11d
	cmpl	$65536, %r8d
	setb	%r11b
	orq	$-4, %r11
.LBB30_65:
	addq	%r9, %r11
	je	.LBB30_70
	cmpq	%rdx, %r11
	jae	.LBB30_71
	cmpb	$-64, (%rcx,%r11)
	jge	.LBB30_72
.LBB30_68:
	movq	%r11, %r9
.LBB30_69:
	movb	$0, 63(%rbp)
.Ltmp74:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.134(%rip), %rax
	movq	%rax, 32(%rsp)
	xorl	%r8d, %r8d
	callq	_RNvNtCs8xEFJqa6dYS_4core3str16slice_error_fail
	nop
.Ltmp75:
	jmp	.LBB30_169
.LBB30_70:
	xorl	%r11d, %r11d
	jmp	.LBB30_74
.LBB30_71:
	jne	.LBB30_68
.LBB30_72:
	cmpb	$0, -1(%rcx,%r11)
	jns	.LBB30_74
	cmpb	$-65, -2(%rcx,%r11)
	jmp	.LBB30_74
.LBB30_123:
	addq	%r9, %rcx
	addq	$-9, %rcx
	leaq	(%rax,%r15), %r14
	addq	$9, %r14
	xorl	%ebx, %ebx
	movl	$10, %r15d
	movq	%r11, %r12
	xorl	%edi, %edi
.LBB30_124:
	cmpq	%r12, %rcx
	je	.LBB30_160
	movq	%rdi, %rax
	mulq	%r15
	jo	.LBB30_128
	movq	%rax, %rdi
	movzbl	(%r14,%r12), %edx
	addl	$-48, %edx
	addq	%rdx, %rdi
	setb	%al
	cmpl	$9, %edx
	ja	.LBB30_128
	incq	%r12
	testb	%al, %al
	je	.LBB30_124
.LBB30_128:
	xorl	%edi, %edi
	jmp	.LBB30_57
.LBB30_130:
	xorl	%edi, %edi
.LBB30_131:
	movq	%r10, %rax
	subq	%r8, %rax
	jb	.LBB30_161
.LBB30_132:
	cmpq	%rsi, %r10
	ja	.LBB30_161
	cmpq	%rsi, %r8
	je	.LBB30_136
	testq	%r8, %r8
	je	.LBB30_136
	cmpb	$-65, (%r15,%r8)
	jle	.LBB30_161
.LBB30_136:
	cmpq	$1, %rax
	je	.LBB30_140
	testq	%rax, %rax
	jne	.LBB30_143
	movq	%rax, %rdi
	movq	%rax, %rbx
	jmp	.LBB30_91
.LBB30_140:
	movzbl	(%r15,%r8), %ecx
	xorl	%ebx, %ebx
	cmpl	$43, %ecx
	je	.LBB30_139
	cmpl	$45, %ecx
	jne	.LBB30_144
.LBB30_139:
	xorl	%edi, %edi
	jmp	.LBB30_91
.LBB30_143:
	movzbl	(%r15,%r8), %ecx
.LBB30_144:
	xorl	%edx, %edx
	cmpb	$43, %cl
	sete	%dl
	movq	%rdx, %rcx
	negq	%rcx
	subq	%rdx, %rax
	cmpq	$17, %rax
	jae	.LBB30_149
	testq	%rax, %rax
	je	.LBB30_155
	leaq	(%rdx,%r15), %rax
	addq	$8, %rax
	addq	%r10, %rcx
	addq	$-8, %rcx
	xorl	%ebx, %ebx
.LBB30_147:
	movzbl	(%rax,%r9), %edx
	addl	$-48, %edx
	cmpl	$9, %edx
	ja	.LBB30_89
	leaq	(%rbx,%rbx,4), %r8
	movl	%edx, %edx
	leaq	(%rdx,%r8,2), %rbx
	incq	%r9
	cmpq	%r9, %rcx
	jne	.LBB30_147
	jmp	.LBB30_156
.LBB30_149:
	addq	%r10, %rcx
	addq	$-8, %rcx
	leaq	(%rdx,%r15), %r8
	addq	$8, %r8
	movl	$10, %r10d
	xorl	%ebx, %ebx
.LBB30_150:
	cmpq	%r9, %rcx
	je	.LBB30_156
	movq	%rbx, %rax
	mulq	%r10
	jo	.LBB30_89
	movq	%rax, %rbx
	movzbl	(%r8,%r9), %edx
	addl	$-48, %edx
	addq	%rdx, %rbx
	setb	%al
	cmpl	$9, %edx
	ja	.LBB30_89
	incq	%r9
	testb	%al, %al
	je	.LBB30_150
	jmp	.LBB30_89
.LBB30_155:
	xorl	%ebx, %ebx
.LBB30_156:
	cmpq	%rsi, %r11
	ja	.LBB30_91
	testq	%r11, %r11
	setne	%al
	cmpq	%rsi, %r11
	setb	%cl
	andb	%al, %cl
	cmpb	$1, %cl
	jne	.LBB30_163
	cmpb	$-65, (%r15,%r11)
	movq	%r11, %rsi
	jg	.LBB30_91
	movb	$0, 63(%rbp)
.Ltmp88:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.45(%rip), %rcx
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.62(%rip), %r8
	movl	$48, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking5panic
	nop
.Ltmp89:
	jmp	.LBB30_169
.LBB30_160:
	movq	48(%rbp), %r15
	movq	%r10, %rax
	subq	%r8, %rax
	jae	.LBB30_132
.LBB30_161:
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
	jmp	.LBB30_169
.LBB30_162:
.Ltmp96:
	movl	$8, %ecx
	movl	$40, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp97:
	jmp	.LBB30_169
.LBB30_163:
	movq	%r11, %rsi
	jmp	.LBB30_91
.LBB30_164:
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
	jmp	.LBB30_169
.LBB30_165:
	movb	$0, 63(%rbp)
.Ltmp76:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.17(%rip), %r8
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	nop
.Ltmp77:
	jmp	.LBB30_169
.LBB30_166:
	movb	$0, 63(%rbp)
.Ltmp78:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.16(%rip), %r8
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	nop
.Ltmp79:
	jmp	.LBB30_169
.LBB30_167:
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
	jmp	.LBB30_169
.LBB30_168:
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
.LBB30_169:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvNtCsavOST1yGCNT_10serde_json5error10make_error@IMGREL
	.section	.text,"xr",one_only,_RNvNtCsavOST1yGCNT_10serde_json5error10make_error,unique,34
	.seh_endproc
	.def	"?dtor$170@?0?_RNvNtCsavOST1yGCNT_10serde_json5error10make_error@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$170@?0?_RNvNtCsavOST1yGCNT_10serde_json5error10make_error@4HA":
.seh_proc "?dtor$170@?0?_RNvNtCsavOST1yGCNT_10serde_json5error10make_error@4HA"
.LBB30_170:
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
	.section	.text,"xr",one_only,_RNvNtCsavOST1yGCNT_10serde_json5error10make_error,unique,34
	.seh_endproc
	.def	"?dtor$171@?0?_RNvNtCsavOST1yGCNT_10serde_json5error10make_error@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$171@?0?_RNvNtCsavOST1yGCNT_10serde_json5error10make_error@4HA":
.seh_proc "?dtor$171@?0?_RNvNtCsavOST1yGCNT_10serde_json5error10make_error@4HA"
.LBB30_171:
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
	.section	.text,"xr",one_only,_RNvNtCsavOST1yGCNT_10serde_json5error10make_error,unique,34
	.seh_endproc
	.def	"?dtor$172@?0?_RNvNtCsavOST1yGCNT_10serde_json5error10make_error@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$172@?0?_RNvNtCsavOST1yGCNT_10serde_json5error10make_error@4HA":
.seh_proc "?dtor$172@?0?_RNvNtCsavOST1yGCNT_10serde_json5error10make_error@4HA"
.LBB30_172:
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
	jne	.LBB30_175
	movq	32(%rbp), %rax
	cmpq	$0, (%rax)
	je	.LBB30_175
	movq	48(%rbp), %rcx
	callq	mi_free
	nop
.LBB30_175:
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
.Lfunc_end30:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvNtCsavOST1yGCNT_10serde_json5error10make_error,unique,34
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
	.long	.Lfunc_begin30@IMGREL
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
	.section	.text,"xr",one_only,_RNvNtCsavOST1yGCNT_10serde_json5error10make_error,unique,34

	.def	_RNvXs1_NtCsavOST1yGCNT_10serde_json3serQINtB5_10SerializerQNtNvXs_NtB7_5valueNtB12_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterENtNtCslmkRZor3pUd_10serde_core3ser10Serializer13serialize_strB7_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1_NtCsavOST1yGCNT_10serde_json3serQINtB5_10SerializerQNtNvXs_NtB7_5valueNtB12_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterENtNtCslmkRZor3pUd_10serde_core3ser10Serializer13serialize_strB7_,unique,35
	.p2align	4
_RNvXs1_NtCsavOST1yGCNT_10serde_json3serQINtB5_10SerializerQNtNvXs_NtB7_5valueNtB12_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterENtNtCslmkRZor3pUd_10serde_core3ser10Serializer13serialize_strB7_:
.Lfunc_begin31:
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
	je	.LBB31_8
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %r14
	leaq	.LJTI31_0(%rip), %r12
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.30(%rip), %r15
	movl	$255, %ebp
	jmp	.LBB31_2
	.p2align	4
.LBB31_62:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r13
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r13, %rax
	testb	%cl, %cl
	je	.LBB31_63
.LBB31_7:
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	movl	$1, %r8d
	movq	%r15, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB31_8
.LBB31_2:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%r14, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r12,%rcx,4), %rcx
	addq	%r12, %rcx
	jmpq	*%rcx
.LBB31_4:
	cmpb	$35, 16(%rax)
	je	.LBB31_7
	jmp	.LBB31_63
	.p2align	4
.LBB31_3:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%ebp, %ecx
	cmpb	$35, %cl
	je	.LBB31_7
	jmp	.LBB31_63
	.p2align	4
.LBB31_5:
	cmpb	$35, 31(%rax)
	jne	.LBB31_63
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB31_7
.LBB31_8:
	leaq	_RNvNtCsavOST1yGCNT_10serde_json3ser6ESCAPE(%rip), %rbp
.LBB31_9:
	xorl	%r14d, %r14d
	.p2align	4
.LBB31_10:
	cmpq	%r14, %rsi
	je	.LBB31_11
	movq	%r14, %r13
	movzbl	(%rbx,%r14), %r12d
	movzbl	(%r12,%rbp), %edi
	incq	%r14
	testb	%dil, %dil
	je	.LBB31_10
	cmpq	$1, %r14
	je	.LBB31_34
	movq	48(%rsp), %rax
	movq	(%rax), %r15
	movq	(%r15), %rcx
	movq	8(%r15), %rax
	movq	%rbx, %rdx
	movq	%r13, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB31_34
	movq	%rbx, 64(%rsp)
	jmp	.LBB31_27
	.p2align	4
.LBB31_28:
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
	je	.LBB31_63
.LBB31_33:
	movq	(%r15), %rcx
	movq	8(%r15), %rax
	movq	%rbx, %rdx
	movq	%r13, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB31_34
.LBB31_27:
	movl	$9, %r8d
	movb	$41, %cl
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	leaq	.LJTI31_1(%rip), %rdx
	movslq	(%rdx,%rcx,4), %rcx
	addq	%rdx, %rcx
	jmpq	*%rcx
.LBB31_30:
	cmpb	$35, 16(%rax)
	je	.LBB31_33
	jmp	.LBB31_63
	.p2align	4
.LBB31_29:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	movl	$255, %edx
	cmovael	%edx, %ecx
	cmpb	$35, %cl
	je	.LBB31_33
	jmp	.LBB31_63
	.p2align	4
.LBB31_31:
	cmpb	$35, 31(%rax)
	jne	.LBB31_63
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB31_33
	.p2align	4
.LBB31_34:
	cmpb	$117, %dil
	jne	.LBB31_43
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
	leaq	.LJTI31_3(%rip), %r13
	jne	.LBB31_36
	jmp	.LBB31_52
	.p2align	4
.LBB31_37:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r15
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r15, %rax
	testb	%cl, %cl
	je	.LBB31_53
.LBB31_42:
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	movl	$6, %r8d
	movq	%r12, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB31_52
.LBB31_36:
	movl	$9, %r8d
	movb	$41, %cl
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r13,%rcx,4), %rcx
	addq	%r13, %rcx
	jmpq	*%rcx
.LBB31_39:
	cmpb	$35, 16(%rax)
	je	.LBB31_42
	jmp	.LBB31_53
	.p2align	4
.LBB31_38:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	movl	$255, %edx
	cmovael	%edx, %ecx
	cmpb	$35, %cl
	je	.LBB31_42
	jmp	.LBB31_53
	.p2align	4
.LBB31_40:
	cmpb	$35, 31(%rax)
	jne	.LBB31_53
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB31_42
	.p2align	4
.LBB31_43:
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
	je	.LBB31_52
	leaq	.LJTI31_2(%rip), %r13
	jmp	.LBB31_45
	.p2align	4
.LBB31_46:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r15
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r15, %rax
	testb	%cl, %cl
	je	.LBB31_53
.LBB31_51:
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	movl	$2, %r8d
	movq	%r12, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB31_52
.LBB31_45:
	movl	$9, %r8d
	movb	$41, %cl
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r13,%rcx,4), %rcx
	addq	%r13, %rcx
	jmpq	*%rcx
.LBB31_48:
	cmpb	$35, 16(%rax)
	je	.LBB31_51
	jmp	.LBB31_53
	.p2align	4
.LBB31_47:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	movl	$255, %edx
	cmovael	%edx, %ecx
	cmpb	$35, %cl
	je	.LBB31_51
	jmp	.LBB31_53
	.p2align	4
.LBB31_49:
	cmpb	$35, 31(%rax)
	jne	.LBB31_53
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB31_51
	.p2align	4
.LBB31_52:
	xorl	%eax, %eax
.LBB31_53:
	addq	%r14, %rbx
	subq	%r14, %rsi
	testq	%rax, %rax
	je	.LBB31_9
.LBB31_63:
	movq	%rax, %rcx
	callq	_RNvMs0_NtCsavOST1yGCNT_10serde_json5errorNtB5_5Error2io
	movq	%rax, %rsi
	jmp	.LBB31_64
.LBB31_11:
	testq	%rsi, %rsi
	je	.LBB31_21
	movq	48(%rsp), %rax
	movq	(%rax), %rdi
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	movq	%rbx, %rdx
	movq	%rsi, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB31_21
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %r14
	leaq	.LJTI31_4(%rip), %r15
	movl	$255, %ebp
	jmp	.LBB31_14
	.p2align	4
.LBB31_15:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r12
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r12, %rax
	testb	%cl, %cl
	je	.LBB31_63
.LBB31_20:
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	movq	%rbx, %rdx
	movq	%rsi, %r8
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB31_21
.LBB31_14:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%r14, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB31_17:
	cmpb	$35, 16(%rax)
	je	.LBB31_20
	jmp	.LBB31_63
	.p2align	4
.LBB31_16:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%ebp, %ecx
	cmpb	$35, %cl
	je	.LBB31_20
	jmp	.LBB31_63
	.p2align	4
.LBB31_18:
	cmpb	$35, 31(%rax)
	jne	.LBB31_63
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB31_20
.LBB31_21:
	movq	48(%rsp), %rax
	movq	(%rax), %r14
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.30(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB31_22
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63(%rip), %rdi
	leaq	.LJTI31_5(%rip), %r15
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.30(%rip), %rbx
	xorl	%esi, %esi
	movl	$255, %ebp
	jmp	.LBB31_55
	.p2align	4
.LBB31_56:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rdx
	movq	%rax, %rcx
	shrq	$32, %rcx
	movq	%rax, %r12
	callq	*16(%rdx)
	movl	%eax, %ecx
	movq	%r12, %rax
	testb	%cl, %cl
	je	.LBB31_63
.LBB31_61:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movl	$1, %r8d
	movq	%rbx, %rdx
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB31_64
.LBB31_55:
	movl	$9, %r8d
	movb	$41, %cl
	movq	%rdi, %rdx
	callq	_RINvMNtNtCsfQUUnEvlYZE_5alloc2io5errorNtNtNtCs8xEFJqa6dYS_4core2io5error5Error3newReECse0R8cuyqEa_3std
	movl	%eax, %ecx
	andl	$3, %ecx
	movslq	(%r15,%rcx,4), %rcx
	addq	%r15, %rcx
	jmpq	*%rcx
.LBB31_58:
	cmpb	$35, 16(%rax)
	je	.LBB31_61
	jmp	.LBB31_63
	.p2align	4
.LBB31_57:
	movq	%rax, %rcx
	shrq	$32, %rcx
	cmpq	$43, %rcx
	cmovael	%ebp, %ecx
	cmpb	$35, %cl
	je	.LBB31_61
	jmp	.LBB31_63
	.p2align	4
.LBB31_59:
	cmpb	$35, 31(%rax)
	jne	.LBB31_63
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	jmp	.LBB31_61
.LBB31_22:
	xorl	%esi, %esi
.LBB31_64:
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
.Lfunc_end31:
	.section	.rdata,"dr",associative,_RNvXs1_NtCsavOST1yGCNT_10serde_json3serQINtB5_10SerializerQNtNvXs_NtB7_5valueNtB12_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterENtNtCslmkRZor3pUd_10serde_core3ser10Serializer13serialize_strB7_,unique,36
	.p2align	2, 0x0
.LJTI31_0:
	.long	.LBB31_4-.LJTI31_0
	.long	.LBB31_5-.LJTI31_0
	.long	.LBB31_62-.LJTI31_0
	.long	.LBB31_3-.LJTI31_0
.LJTI31_1:
	.long	.LBB31_30-.LJTI31_1
	.long	.LBB31_31-.LJTI31_1
	.long	.LBB31_28-.LJTI31_1
	.long	.LBB31_29-.LJTI31_1
.LJTI31_2:
	.long	.LBB31_48-.LJTI31_2
	.long	.LBB31_49-.LJTI31_2
	.long	.LBB31_46-.LJTI31_2
	.long	.LBB31_47-.LJTI31_2
.LJTI31_3:
	.long	.LBB31_39-.LJTI31_3
	.long	.LBB31_40-.LJTI31_3
	.long	.LBB31_37-.LJTI31_3
	.long	.LBB31_38-.LJTI31_3
.LJTI31_4:
	.long	.LBB31_17-.LJTI31_4
	.long	.LBB31_18-.LJTI31_4
	.long	.LBB31_15-.LJTI31_4
	.long	.LBB31_16-.LJTI31_4
.LJTI31_5:
	.long	.LBB31_58-.LJTI31_5
	.long	.LBB31_59-.LJTI31_5
	.long	.LBB31_56-.LJTI31_5
	.long	.LBB31_57-.LJTI31_5
	.section	.text,"xr",one_only,_RNvXs1_NtCsavOST1yGCNT_10serde_json3serQINtB5_10SerializerQNtNvXs_NtB7_5valueNtB12_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterENtNtCslmkRZor3pUd_10serde_core3ser10Serializer13serialize_strB7_,unique,35
	.seh_endproc

	.def	_RNvXs1_NtCsavOST1yGCNT_10serde_json5errorNtB5_9ErrorCodeNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1_NtCsavOST1yGCNT_10serde_json5errorNtB5_9ErrorCodeNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt,unique,37
	.globl	_RNvXs1_NtCsavOST1yGCNT_10serde_json5errorNtB5_9ErrorCodeNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt
	.p2align	4
_RNvXs1_NtCsavOST1yGCNT_10serde_json5errorNtB5_9ErrorCodeNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt:
.Lfunc_begin32:
	movq	(%rcx), %rax
	leaq	.LJTI32_0(%rip), %r8
	movslq	(%r8,%rax,4), %rax
	addq	%r8, %rax
	jmpq	*%rax
.LBB32_1:
	movq	8(%rcx), %rax
	movq	16(%rcx), %r8
	movq	(%rdx), %rcx
	movq	8(%rdx), %rdx
	movq	24(%rdx), %r9
	movq	%rax, %rdx
	rex64 jmpq	*%r9
.LBB32_17:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.91(%rip), %rdx
	movl	$62, %r8d
	rex64 jmpq	*%rax
.LBB32_15:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.89(%rip), %rdx
	movl	$19, %r8d
	rex64 jmpq	*%rax
.LBB32_12:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.86(%rip), %rdx
	movl	$12, %r8d
	rex64 jmpq	*%rax
.LBB32_5:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.79(%rip), %rdx
	movl	$26, %r8d
	rex64 jmpq	*%rax
.LBB32_13:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.87(%rip), %rdx
	movl	$14, %r8d
	rex64 jmpq	*%rax
.LBB32_10:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.84(%rip), %rdx
	movl	$14, %r8d
	rex64 jmpq	*%rax
.LBB32_25:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.99(%rip), %rdx
	movl	$24, %r8d
	rex64 jmpq	*%rax
.LBB32_3:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.77(%rip), %rdx
	movl	$24, %r8d
	rex64 jmpq	*%rax
.LBB32_16:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.90(%rip), %rdx
	movl	$26, %r8d
	rex64 jmpq	*%rax
.LBB32_4:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.78(%rip), %rdx
	movl	$27, %r8d
	rex64 jmpq	*%rax
.LBB32_8:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.82(%rip), %rdx
	movl	$19, %r8d
	rex64 jmpq	*%rax
.LBB32_2:
	addq	$8, %rcx
	jmp	_RNvXs3_NtNtCs8xEFJqa6dYS_4core2io5errorNtB5_5ErrorNtNtB9_3fmt7Display3fmt
.LBB32_18:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.92(%rip), %rdx
	movl	$20, %r8d
	rex64 jmpq	*%rax
.LBB32_21:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.95(%rip), %rdx
	movl	$36, %r8d
	rex64 jmpq	*%rax
.LBB32_6:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.80(%rip), %rdx
	movl	$25, %r8d
	rex64 jmpq	*%rax
.LBB32_22:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.96(%rip), %rdx
	movl	$14, %r8d
	rex64 jmpq	*%rax
.LBB32_14:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.88(%rip), %rdx
	movl	$14, %r8d
	rex64 jmpq	*%rax
.LBB32_7:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.81(%rip), %rdx
	movl	$12, %r8d
	rex64 jmpq	*%rax
.LBB32_19:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.93(%rip), %rdx
	movl	$52, %r8d
	rex64 jmpq	*%rax
.LBB32_11:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.85(%rip), %rdx
	movl	$14, %r8d
	rex64 jmpq	*%rax
.LBB32_9:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.83(%rip), %rdx
	movl	$19, %r8d
	rex64 jmpq	*%rax
.LBB32_23:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.97(%rip), %rdx
	movl	$19, %r8d
	rex64 jmpq	*%rax
.LBB32_20:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.94(%rip), %rdx
	movl	$44, %r8d
	rex64 jmpq	*%rax
.LBB32_24:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.98(%rip), %rdx
	movl	$28, %r8d
	rex64 jmpq	*%rax
.Lfunc_end32:
	.section	.rdata,"dr",associative,_RNvXs1_NtCsavOST1yGCNT_10serde_json5errorNtB5_9ErrorCodeNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt,unique,38
	.p2align	2, 0x0
.LJTI32_0:
	.long	.LBB32_1-.LJTI32_0
	.long	.LBB32_2-.LJTI32_0
	.long	.LBB32_3-.LJTI32_0
	.long	.LBB32_4-.LJTI32_0
	.long	.LBB32_5-.LJTI32_0
	.long	.LBB32_6-.LJTI32_0
	.long	.LBB32_7-.LJTI32_0
	.long	.LBB32_8-.LJTI32_0
	.long	.LBB32_9-.LJTI32_0
	.long	.LBB32_10-.LJTI32_0
	.long	.LBB32_11-.LJTI32_0
	.long	.LBB32_12-.LJTI32_0
	.long	.LBB32_13-.LJTI32_0
	.long	.LBB32_14-.LJTI32_0
	.long	.LBB32_15-.LJTI32_0
	.long	.LBB32_16-.LJTI32_0
	.long	.LBB32_17-.LJTI32_0
	.long	.LBB32_18-.LJTI32_0
	.long	.LBB32_19-.LJTI32_0
	.long	.LBB32_20-.LJTI32_0
	.long	.LBB32_21-.LJTI32_0
	.long	.LBB32_22-.LJTI32_0
	.long	.LBB32_23-.LJTI32_0
	.long	.LBB32_24-.LJTI32_0
	.long	.LBB32_25-.LJTI32_0

	.def	_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtRDNtNtCslmkRZor3pUd_10serde_core2de8ExpectedEL_NtB6_7Display3fmtCsavOST1yGCNT_10serde_json.llvm.16186315980599473920;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtRDNtNtCslmkRZor3pUd_10serde_core2de8ExpectedEL_NtB6_7Display3fmtCsavOST1yGCNT_10serde_json.llvm.16186315980599473920,unique,39
	.globl	_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtRDNtNtCslmkRZor3pUd_10serde_core2de8ExpectedEL_NtB6_7Display3fmtCsavOST1yGCNT_10serde_json.llvm.16186315980599473920
	.p2align	4
_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtRDNtNtCslmkRZor3pUd_10serde_core2de8ExpectedEL_NtB6_7Display3fmtCsavOST1yGCNT_10serde_json.llvm.16186315980599473920:
.Lfunc_begin33:
	movq	(%rcx), %rax
	movq	8(%rcx), %rcx
	movq	24(%rcx), %r8
	movq	%rax, %rcx
	rex64 jmpq	*%r8
.Lfunc_end33:

	.def	_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtReNtB6_7Display3fmtCsavOST1yGCNT_10serde_json;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtReNtB6_7Display3fmtCsavOST1yGCNT_10serde_json,unique,40
	.p2align	4
_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtReNtB6_7Display3fmtCsavOST1yGCNT_10serde_json:
.Lfunc_begin34:
	movq	%rdx, %rax
	movq	(%rcx), %rdx
	movq	8(%rcx), %r8
	movq	%rax, %rcx
	jmp	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
.Lfunc_end34:

	.def	_RNvXs5_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceReadNtB5_4Read10ignore_str;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs5_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceReadNtB5_4Read10ignore_str,unique,41
	.globl	_RNvXs5_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceReadNtB5_4Read10ignore_str
	.p2align	4
_RNvXs5_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceReadNtB5_4Read10ignore_str:
.Lfunc_begin35:
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
	jne	.LBB35_4
.LBB35_1:
	movq	$4, 48(%rsp)
.LBB35_2:
	leaq	48(%rsp), %rdx
	movq	%rsi, %rcx
	callq	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_
	nop
.LBB35_3:
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
.LBB35_4:
	leaq	.LJTI35_0(%rip), %r12
	leaq	_RNvNtCsavOST1yGCNT_10serde_json4read4HEX0(%rip), %rbp
	leaq	32(%rsp), %rdi
	leaq	48(%rsp), %rbx
	jmp	.LBB35_7
.LBB35_17:
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
	js	.LBB35_19
	movw	$0, 32(%rsp)
	cmpw	$1, 32(%rsp)
	je	.LBB35_25
	.p2align	4
.LBB35_14:
	movq	%rsi, %rcx
	callq	_RNvMs3_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceRead14skip_to_escape
	movq	8(%rsi), %r14
	movq	16(%rsi), %rcx
	cmpq	%r14, %rcx
	je	.LBB35_1
.LBB35_7:
	cmpq	%r14, %rcx
	jae	.LBB35_27
	movq	(%rsi), %r13
	movzbl	(%r13,%rcx), %eax
	cmpl	$92, %eax
	jne	.LBB35_20
	leaq	1(%rcx), %r15
	movq	%r15, 16(%rsi)
	cmpq	%r14, %r15
	jae	.LBB35_11
	movzbl	1(%r13,%rcx), %eax
	addq	$2, %rcx
	movq	%rcx, 16(%rsi)
	movq	%rcx, %r15
	movzbl	%al, %eax
	addl	$-34, %eax
	cmpl	$83, %eax
	jbe	.LBB35_13
	jmp	.LBB35_24
	.p2align	4
.LBB35_11:
	movq	$4, 48(%rsp)
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	movq	%rbx, %r8
	callq	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_
	cmpb	$0, 32(%rsp)
	jne	.LBB35_25
	movzbl	33(%rsp), %eax
	movzbl	%al, %eax
	addl	$-34, %eax
	cmpl	$83, %eax
	ja	.LBB35_24
.LBB35_13:
	movslq	(%r12,%rax,4), %rax
	addq	%r12, %rax
	jmpq	*%rax
.LBB35_15:
	movq	%r14, %rax
	subq	%r15, %rax
	jb	.LBB35_26
	cmpq	$3, %rax
	ja	.LBB35_17
	movq	%r14, 16(%rsi)
	movq	$4, 48(%rsp)
	jmp	.LBB35_6
.LBB35_19:
	movq	$12, 48(%rsp)
.LBB35_6:
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	movq	%rbx, %r8
	callq	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadtEB4_
	cmpw	$1, 32(%rsp)
	jne	.LBB35_14
.LBB35_25:
	movq	40(%rsp), %rax
	jmp	.LBB35_3
.LBB35_20:
	cmpl	$34, %eax
	jne	.LBB35_22
	incq	%rcx
	movq	%rcx, 16(%rsi)
	xorl	%eax, %eax
	jmp	.LBB35_3
.LBB35_22:
	movq	$16, 48(%rsp)
	jmp	.LBB35_2
.LBB35_24:
	movq	$12, 48(%rsp)
	jmp	.LBB35_2
.LBB35_26:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.108(%rip), %r9
	movq	%r15, %rcx
	movq	%r14, %rdx
	movq	%r14, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	ud2
.LBB35_27:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.107(%rip), %r8
	movq	%r14, %rdx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	ud2
.Lfunc_end35:
	.section	.rdata,"dr",associative,_RNvXs5_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceReadNtB5_4Read10ignore_str,unique,42
	.p2align	2, 0x0
.LJTI35_0:
	.long	.LBB35_14-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_14-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_14-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_14-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_14-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_14-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_14-.LJTI35_0
	.long	.LBB35_24-.LJTI35_0
	.long	.LBB35_14-.LJTI35_0
	.long	.LBB35_15-.LJTI35_0
	.section	.text,"xr",one_only,_RNvXs5_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceReadNtB5_4Read10ignore_str,unique,41
	.seh_endproc

	.def	_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt,unique,43
	.globl	_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt
	.p2align	4
_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt:
.Lfunc_begin36:
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
	jne	.LBB36_2
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
	je	.LBB36_13
	movq	-24(%rbp), %rcx
	movl	%eax, %ebx
	callq	mi_free
	movl	%ebx, %eax
.LBB36_13:
	.seh_startepilogue
	addq	$168, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB36_2:
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
	.section	.text,"xr",one_only,_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt,unique,43
	.seh_endproc
	.def	"?dtor$4@?0?_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$4@?0?_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt@4HA":
.seh_proc "?dtor$4@?0?_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt@4HA"
.LBB36_4:
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
	je	.LBB36_6
	movq	8(%rbp), %rcx
	callq	mi_free
	nop
.LBB36_6:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt,unique,43
	.seh_endproc
	.def	"?dtor$7@?0?_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$7@?0?_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt@4HA":
.seh_proc "?dtor$7@?0?_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt@4HA"
.LBB36_7:
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
	je	.LBB36_9
	movq	-24(%rbp), %rcx
	callq	mi_free
	nop
.LBB36_9:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end36:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt,unique,43
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
	.long	.Lfunc_begin36@IMGREL
	.long	-1
	.long	.Ltmp98@IMGREL
	.long	0
	.long	.Ltmp100@IMGREL
	.long	1
	.long	.Ltmp102@IMGREL
	.long	0
	.long	.Ltmp103@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvXs5_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt,unique,43

	.def	_RNvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error12invalid_type;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error12invalid_type,unique,44
	.globl	_RNvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error12invalid_type
	.p2align	4
_RNvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error12invalid_type:
.Lfunc_begin37:
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
.Lfunc_end37:
	.seh_endproc

	.def	_RNvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error13invalid_value;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error13invalid_value,unique,45
	.globl	_RNvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error13invalid_value
	.p2align	4
_RNvXs6_NtCsavOST1yGCNT_10serde_json5errorNtB5_5ErrorNtNtCslmkRZor3pUd_10serde_core2de5Error13invalid_value:
.Lfunc_begin38:
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
.Lfunc_end38:
	.seh_endproc

	.def	_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read10ignore_str;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read10ignore_str,unique,46
	.globl	_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read10ignore_str
	.p2align	4
_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read10ignore_str:
.Lfunc_begin39:
	jmp	_RNvXs5_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceReadNtB5_4Read10ignore_str
.Lfunc_end39:

	.def	_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read13peek_position;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read13peek_position,unique,47
	.globl	_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read13peek_position
	.p2align	4
_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read13peek_position:
.Lfunc_begin40:
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
	jne	.LBB40_1
	subq	%rdi, %rdx
	leaq	1(%rdx), %r14
	cmpq	%rbx, %rdx
	jb	.LBB40_2
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920(%rip), %r9
	xorl	%ecx, %ecx
	movq	%r14, %rdx
	movq	%rbx, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	ud2
.LBB40_1:
	xorl	%r14d, %r14d
.LBB40_2:
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
.Lfunc_end40:
	.seh_endproc

	.def	_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read8position;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read8position,unique,48
	.globl	_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read8position
	.p2align	4
_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read8position:
.Lfunc_begin41:
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
	ja	.LBB41_6
	movq	(%rcx), %rbx
	leaq	(%rbx,%rsi), %r8
	movq	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw2FN(%rip), %rax
	movb	$10, %cl
	movq	%rbx, %rdx
	callq	*%rax
	cmpq	$1, %rax
	jne	.LBB41_2
	subq	%rbx, %rdx
	leaq	1(%rdx), %r14
	cmpq	%rdi, %rdx
	jb	.LBB41_3
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920(%rip), %r9
	xorl	%ecx, %ecx
	movq	%r14, %rdx
	movq	%rdi, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	ud2
.LBB41_2:
	xorl	%r14d, %r14d
.LBB41_3:
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
.LBB41_6:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.48.llvm.16186315980599473920(%rip), %r9
	xorl	%ecx, %ecx
	movq	%rsi, %rdx
	movq	%rdi, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	ud2
.Lfunc_end41:
	.seh_endproc

	.def	_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read9parse_str;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read9parse_str,unique,49
	.globl	_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read9parse_str
	.p2align	4
_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read9parse_str:
.Lfunc_begin42:
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
.LBB42_1:
	movq	16(%rdi), %r14
	movq	%rdi, %rcx
	callq	_RNvMs3_NtCsavOST1yGCNT_10serde_json4readNtB5_9SliceRead14skip_to_escape
	movq	8(%rdi), %r15
	movq	16(%rdi), %rsi
	cmpq	%r15, %rsi
	je	.LBB42_6
	jae	.LBB42_8
	movq	(%rdi), %rbp
	movzbl	(%rbp,%rsi), %eax
	cmpl	$92, %eax
	jne	.LBB42_4
	movq	%rsi, %r13
	subq	%r14, %r13
	jb	.LBB42_59
	movq	(%rbx), %rax
	movq	16(%rbx), %r12
	subq	%r12, %rax
	cmpq	%rax, %r13
	ja	.LBB42_22
	cmpq	%r14, %rsi
	je	.LBB42_25
.LBB42_24:
	addq	%rbp, %r14
	movq	8(%rbx), %rcx
	addq	%r12, %rcx
	movq	%r14, %rdx
	movq	%r13, %r8
	callq	memcpy
.LBB42_25:
	addq	%r13, %r12
	movq	%r12, 16(%rbx)
	leaq	1(%rsi), %rax
	movq	%rax, 16(%rdi)
	cmpq	%r15, %rax
	jae	.LBB42_27
	movzbl	1(%rbp,%rsi), %eax
	addq	$2, %rsi
	movq	%rsi, 16(%rdi)
	movzbl	%al, %eax
	addl	$-34, %eax
	cmpl	$83, %eax
	jbe	.LBB42_30
	jmp	.LBB42_31
	.p2align	4
.LBB42_27:
	movq	$4, 48(%rsp)
	leaq	72(%rsp), %rcx
	movq	%rdi, %rdx
	leaq	48(%rsp), %r8
	callq	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadhEB4_
	cmpb	$0, 72(%rsp)
	jne	.LBB42_60
	movzbl	73(%rsp), %eax
	movzbl	%al, %eax
	addl	$-34, %eax
	cmpl	$83, %eax
	ja	.LBB42_31
.LBB42_30:
	leaq	.LJTI42_0(%rip), %rcx
	movslq	(%rcx,%rax,4), %rax
	addq	%rcx, %rax
	jmpq	*%rax
.LBB42_32:
	cmpq	(%rbx), %r12
	jne	.LBB42_34
	movq	%rbx, %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVechE8grow_oneB7_
.LBB42_34:
	movq	8(%rbx), %rax
	movb	$34, (%rax,%r12)
	jmp	.LBB42_35
.LBB42_45:
	cmpq	(%rbx), %r12
	jne	.LBB42_47
	movq	%rbx, %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVechE8grow_oneB7_
.LBB42_47:
	movq	8(%rbx), %rax
	movb	$12, (%rax,%r12)
	jmp	.LBB42_35
.LBB42_48:
	cmpq	(%rbx), %r12
	jne	.LBB42_50
	movq	%rbx, %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVechE8grow_oneB7_
.LBB42_50:
	movq	8(%rbx), %rax
	movb	$10, (%rax,%r12)
	jmp	.LBB42_35
.LBB42_42:
	cmpq	(%rbx), %r12
	jne	.LBB42_44
	movq	%rbx, %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVechE8grow_oneB7_
.LBB42_44:
	movq	8(%rbx), %rax
	movb	$8, (%rax,%r12)
	jmp	.LBB42_35
.LBB42_36:
	cmpq	(%rbx), %r12
	jne	.LBB42_38
	movq	%rbx, %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVechE8grow_oneB7_
.LBB42_38:
	movq	8(%rbx), %rax
	movb	$92, (%rax,%r12)
	jmp	.LBB42_35
.LBB42_39:
	cmpq	(%rbx), %r12
	jne	.LBB42_41
	movq	%rbx, %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVechE8grow_oneB7_
.LBB42_41:
	movq	8(%rbx), %rax
	movb	$47, (%rax,%r12)
	jmp	.LBB42_35
.LBB42_51:
	cmpq	(%rbx), %r12
	jne	.LBB42_53
	movq	%rbx, %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVechE8grow_oneB7_
.LBB42_53:
	movq	8(%rbx), %rax
	movb	$13, (%rax,%r12)
	jmp	.LBB42_35
.LBB42_54:
	cmpq	(%rbx), %r12
	jne	.LBB42_56
	movq	%rbx, %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVechE8grow_oneB7_
.LBB42_56:
	movq	8(%rbx), %rax
	movb	$9, (%rax,%r12)
	.p2align	4
.LBB42_35:
	incq	%r12
	movq	%r12, 16(%rbx)
	xorl	%eax, %eax
	testq	%rax, %rax
	je	.LBB42_1
	jmp	.LBB42_61
.LBB42_22:
	movq	%rbx, %rcx
	movq	%r12, %rdx
	movq	%r13, %r8
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECsavOST1yGCNT_10serde_json
	movq	16(%rbx), %r12
	jmp	.LBB42_24
.LBB42_57:
	movq	%rdi, %rcx
	movq	%rbx, %rdx
	callq	_RINvNtCsavOST1yGCNT_10serde_json4read20parse_unicode_escapeNtB2_9SliceReadEB4_
	testq	%rax, %rax
	je	.LBB42_1
	jmp	.LBB42_61
.LBB42_31:
	movq	$12, 48(%rsp)
	leaq	48(%rsp), %rdx
	movq	%rdi, %rcx
	callq	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReaduEB4_
.LBB42_61:
	movq	40(%rsp), %rsi
	movq	%rax, 8(%rsi)
	movq	$2, (%rsi)
	jmp	.LBB42_62
.LBB42_4:
	cmpl	$34, %eax
	jne	.LBB42_5
	movq	16(%rbx), %r12
	testq	%r12, %r12
	je	.LBB42_15
	movq	%rsi, %r13
	subq	%r14, %r13
	jb	.LBB42_63
	movq	(%rbx), %rax
	subq	%r12, %rax
	cmpq	%rax, %r13
	ja	.LBB42_12
	cmpq	%r14, %rsi
	je	.LBB42_19
.LBB42_18:
	addq	%r14, %rbp
	movq	8(%rbx), %rcx
	addq	%r12, %rcx
	movq	%rbp, %rdx
	movq	%r13, %r8
	callq	memcpy
.LBB42_19:
	addq	%r13, %r12
	movq	%r12, 16(%rbx)
	incq	%rsi
	movq	%rsi, 16(%rdi)
	movq	8(%rbx), %rax
	movq	40(%rsp), %rsi
	movq	$1, (%rsi)
	movq	%rax, 8(%rsi)
	movq	%r12, 16(%rsi)
	jmp	.LBB42_62
.LBB42_6:
	movq	$4, 48(%rsp)
	jmp	.LBB42_7
.LBB42_5:
	incq	%rsi
	movq	%rsi, 16(%rdi)
	movq	$16, 48(%rsp)
.LBB42_7:
	leaq	48(%rsp), %r8
	movq	40(%rsp), %rsi
	movq	%rsi, %rcx
	movq	%rdi, %rdx
	callq	_RINvNtCsavOST1yGCNT_10serde_json4read5errorNtB2_9SliceReadINtB2_9ReferenceeEEB4_
.LBB42_62:
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
.LBB42_60:
	movq	80(%rsp), %rax
	jmp	.LBB42_61
.LBB42_15:
	movq	%rsi, %rax
	subq	%r14, %rax
	jb	.LBB42_13
	addq	%r14, %rbp
	incq	%rsi
	movq	%rsi, 16(%rdi)
	movq	40(%rsp), %rsi
	movq	$0, (%rsi)
	movq	%rbp, 8(%rsi)
	movq	%rax, 16(%rsi)
	jmp	.LBB42_62
.LBB42_59:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.4(%rip), %r9
.LBB42_14:
	movq	%r14, %rcx
	movq	%rsi, %rdx
	movq	%r15, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	ud2
.LBB42_63:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.3(%rip), %r9
	jmp	.LBB42_14
.LBB42_13:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.2(%rip), %r9
	jmp	.LBB42_14
.LBB42_12:
	movq	%rbx, %rcx
	movq	%r12, %rdx
	movq	%r13, %r8
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECsavOST1yGCNT_10serde_json
	movq	16(%rbx), %r12
	jmp	.LBB42_18
.LBB42_8:
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.1(%rip), %r8
	movq	%rsi, %rcx
	movq	%r15, %rdx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	ud2
.Lfunc_end42:
	.section	.rdata,"dr",associative,_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read9parse_str,unique,50
	.p2align	2, 0x0
.LJTI42_0:
	.long	.LBB42_32-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_39-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_36-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_42-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_45-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_48-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_51-.LJTI42_0
	.long	.LBB42_31-.LJTI42_0
	.long	.LBB42_54-.LJTI42_0
	.long	.LBB42_57-.LJTI42_0
	.section	.text,"xr",one_only,_RNvXs8_NtCsavOST1yGCNT_10serde_json4readNtB5_7StrReadNtB5_4Read9parse_str,unique,49
	.seh_endproc

	.def	_RNvXs8_NtCsavOST1yGCNT_10serde_json5errorNtB5_14JsonUnexpectedNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs8_NtCsavOST1yGCNT_10serde_json5errorNtB5_14JsonUnexpectedNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt,unique,51
	.globl	_RNvXs8_NtCsavOST1yGCNT_10serde_json5errorNtB5_14JsonUnexpectedNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt
	.p2align	4
_RNvXs8_NtCsavOST1yGCNT_10serde_json5errorNtB5_14JsonUnexpectedNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt:
.Lfunc_begin43:
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
	je	.LBB43_3
	cmpl	$7, %eax
	jne	.LBB43_5
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
.LBB43_3:
	movq	8(%rcx), %xmm0
	movq	%xmm0, %rax
	movabsq	$9223372036854775807, %rcx
	andq	%rax, %rcx
	movabsq	$9218868437227405311, %r8
	cmpq	%r8, %rcx
	jle	.LBB43_7
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
	jmp	.LBB43_8
.LBB43_5:
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
.LBB43_7:
	leaq	64(%rsp), %rsi
	movq	%rdx, %rdi
	movq	%rsi, %rdx
	callq	_RNvXs_NtCs6FhewopUhnE_4zmij7privatedNtB4_6Sealed20write_to_zmij_buffer
	movq	%rdi, %rdx
	subq	%rsi, %rax
.LBB43_8:
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
.Lfunc_end43:
	.seh_endproc

	.def	_RNvXsK_NtCs8xEFJqa6dYS_4core3fmtNtB5_5ErrorNtB5_5Debug3fmt;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXsK_NtCs8xEFJqa6dYS_4core3fmtNtB5_5ErrorNtB5_5Debug3fmt,unique,52
	.p2align	4
_RNvXsK_NtCs8xEFJqa6dYS_4core3fmtNtB5_5ErrorNtB5_5Debug3fmt:
.Lfunc_begin44:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.118(%rip), %rdx
	movl	$5, %r8d
	rex64 jmpq	*%rax
.Lfunc_end44:

	.def	_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write10write_char;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write10write_char,unique,53
	.p2align	4
_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write10write_char:
.Lfunc_begin45:
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
	jb	.LBB45_3
	movl	$2, %edi
	cmpl	$2048, %edx
	jb	.LBB45_3
	cmpl	$65536, %edx
	movl	$4, %edi
	sbbq	$0, %rdi
.LBB45_3:
	movq	(%rcx), %rax
	subq	%rsi, %rax
	cmpq	%rax, %rdi
	ja	.LBB45_4
	movq	8(%rcx), %rax
	cmpl	$128, %edx
	jae	.LBB45_6
.LBB45_12:
	movb	%dl, (%rax,%rsi)
	jmp	.LBB45_11
.LBB45_4:
	movq	%rcx, %rbx
	movl	%edx, %ebp
	movq	%rsi, %rdx
	movq	%rdi, %r8
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECsavOST1yGCNT_10serde_json
	movl	%ebp, %edx
	movq	%rbx, %rcx
	movq	8(%rcx), %rax
	cmpl	$128, %edx
	jb	.LBB45_12
.LBB45_6:
	movl	%edx, %r8d
	andb	$63, %r8b
	orb	$-128, %r8b
	movl	%edx, %r9d
	shrl	$6, %r9d
	cmpl	$2048, %edx
	jae	.LBB45_8
	orb	$-64, %r9b
	movb	%r9b, (%rax,%rsi)
	movb	%r8b, 1(%rax,%rsi)
	jmp	.LBB45_11
.LBB45_8:
	andb	$63, %r9b
	orb	$-128, %r9b
	movl	%edx, %r10d
	shrl	$12, %r10d
	cmpl	$65535, %edx
	ja	.LBB45_10
	orb	$-32, %r10b
	movb	%r10b, (%rax,%rsi)
	movb	%r9b, 1(%rax,%rsi)
	movb	%r8b, 2(%rax,%rsi)
	jmp	.LBB45_11
.LBB45_10:
	andb	$63, %r10b
	orb	$-128, %r10b
	shrl	$18, %edx
	orb	$-16, %dl
	movb	%dl, (%rax,%rsi)
	movb	%r10b, 1(%rax,%rsi)
	movb	%r9b, 2(%rax,%rsi)
	movb	%r8b, 3(%rax,%rsi)
.LBB45_11:
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
.Lfunc_end45:
	.seh_endproc

	.def	_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_str;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_str,unique,54
	.p2align	4
_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_str:
.Lfunc_begin46:
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
	ja	.LBB46_1
	testq	%rsi, %rsi
	je	.LBB46_4
.LBB46_3:
	movq	8(%rdi), %rcx
	addq	%rbx, %rcx
	movq	%rsi, %r8
	callq	memcpy
.LBB46_4:
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
.LBB46_1:
	movq	%rdi, %rcx
	movq	%rdx, %r14
	movq	%rbx, %rdx
	movq	%rsi, %r8
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECsavOST1yGCNT_10serde_json
	movq	%r14, %rdx
	movq	16(%rdi), %rbx
	jmp	.LBB46_3
.Lfunc_end46:
	.seh_endproc

	.def	_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt,unique,55
	.globl	_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt
	.p2align	4
_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt:
.Lfunc_begin47:
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
	jne	.LBB47_6
	movq	%rax, -56(%rbp)
	leaq	-56(%rbp), %rdx
	callq	_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterEEB7_
	testq	%rax, %rax
	je	.LBB47_12
	movq	%rax, %rsi
	movq	(%rax), %rax
	cmpq	$1, %rax
	jne	.LBB47_8
	movq	8(%rsi), %rax
	movl	%eax, %ecx
	andl	$3, %ecx
	leal	-2(%rcx), %edx
	cmpl	$2, %edx
	jb	.LBB47_18
	testq	%rcx, %rcx
	je	.LBB47_18
	movq	%rsi, -8(%rbp)
	leaq	-1(%rax), %rcx
.Ltmp106:
	callq	*23(%rax)
	nop
.Ltmp107:
	jmp	.LBB47_17
.LBB47_6:
	movq	%rax, -56(%rbp)
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.18(%rip), %rax
	movq	%rax, -48(%rbp)
	movq	$2, -40(%rbp)
	movq	$0, -32(%rbp)
	movb	$0, -24(%rbp)
	leaq	-56(%rbp), %rdx
	callq	_RINvXNtNtCsavOST1yGCNT_10serde_json5value3serNtB5_5ValueNtNtCslmkRZor3pUd_10serde_core3ser9Serialize9serializeQINtNtB7_3ser10SerializerQNtNvXs_B5_BH_NtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt15WriterFormatterNtB1O_15PrettyFormatterEEB7_
	testq	%rax, %rax
	je	.LBB47_12
	movq	%rax, %rsi
	movq	(%rax), %rax
	cmpq	$1, %rax
	je	.LBB47_14
.LBB47_8:
	testq	%rax, %rax
	jne	.LBB47_18
	cmpq	$0, 16(%rsi)
	je	.LBB47_18
	movq	8(%rsi), %rcx
	callq	mi_free
	jmp	.LBB47_18
.LBB47_12:
	xorl	%eax, %eax
	.seh_startepilogue
	addq	$104, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB47_14:
	movq	8(%rsi), %rax
	movl	%eax, %ecx
	andl	$3, %ecx
	leal	-2(%rcx), %edx
	cmpl	$2, %edx
	jb	.LBB47_18
	testq	%rcx, %rcx
	je	.LBB47_18
	movq	%rsi, -8(%rbp)
	leaq	-1(%rax), %rcx
.Ltmp104:
	callq	*23(%rax)
	nop
.Ltmp105:
.LBB47_17:
	movq	-8(%rbp), %rsi
.LBB47_18:
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
	.section	.text,"xr",one_only,_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt,unique,55
	.seh_endproc
	.def	"?dtor$19@?0?_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$19@?0?_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt@4HA":
.seh_proc "?dtor$19@?0?_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt@4HA"
.LBB47_19:
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
	.section	.text,"xr",one_only,_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt,unique,55
	.seh_endproc
	.def	"?dtor$20@?0?_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$20@?0?_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt@4HA":
.seh_proc "?dtor$20@?0?_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt@4HA"
.LBB47_20:
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
.Lfunc_end47:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt,unique,55
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
	.long	.Lfunc_begin47@IMGREL
	.long	-1
	.long	.Ltmp106@IMGREL
	.long	0
	.long	.Ltmp107@IMGREL
	.long	-1
	.long	.Ltmp104@IMGREL
	.long	1
	.long	.Ltmp105@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvXs_NtCsavOST1yGCNT_10serde_json5valueNtB4_5ValueNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt,unique,55

	.def	_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value3serNtB4_10SerializerNtNtCslmkRZor3pUd_10serde_core3ser10Serializer13serialize_seq;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value3serNtB4_10SerializerNtNtCslmkRZor3pUd_10serde_core3ser10Serializer13serialize_seq,unique,56
	.globl	_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value3serNtB4_10SerializerNtNtCslmkRZor3pUd_10serde_core3ser10Serializer13serialize_seq
	.p2align	4
_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value3serNtB4_10SerializerNtNtCslmkRZor3pUd_10serde_core3ser10Serializer13serialize_seq:
.Lfunc_begin48:
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
	je	.LBB48_1
.LBB48_6:
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.LBB48_1:
	testq	%rsi, %rsi
	je	.LBB48_2
	movl	$8, %edi
	movl	$8, %edx
	movq	%rcx, %rbx
	movq	%rsi, %rcx
	movq	%r8, %r14
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB48_6
	movq	%r14, %rdx
	movq	%rbx, %rcx
	jmp	.LBB48_5
.LBB48_2:
	movl	$8, %eax
	xorl	%edx, %edx
.LBB48_5:
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
.Lfunc_end48:
	.seh_endproc

	.def	_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value3serNtB4_10SerializerNtNtCslmkRZor3pUd_10serde_core3ser10Serializer15serialize_tuple;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value3serNtB4_10SerializerNtNtCslmkRZor3pUd_10serde_core3ser10Serializer15serialize_tuple,unique,57
	.globl	_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value3serNtB4_10SerializerNtNtCslmkRZor3pUd_10serde_core3ser10Serializer15serialize_tuple
	.p2align	4
_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value3serNtB4_10SerializerNtNtCslmkRZor3pUd_10serde_core3ser10Serializer15serialize_tuple:
.Lfunc_begin49:
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
	je	.LBB49_3
	xorl	%edi, %edi
.LBB49_2:
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.LBB49_3:
	testq	%rsi, %rsi
	je	.LBB49_4
	movq	%rdx, %rbx
	movq	%rcx, %r14
	movl	$8, %edi
	movl	$8, %edx
	movq	%rsi, %rcx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB49_2
	movq	%r14, %rcx
	jmp	.LBB49_7
.LBB49_4:
	movl	$8, %eax
	xorl	%ebx, %ebx
.LBB49_7:
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
.Lfunc_end49:
	.seh_endproc

	.def	_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value4fromNtB6_5ValueINtNtCs8xEFJqa6dYS_4core7convert4FromdE4from;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value4fromNtB6_5ValueINtNtCs8xEFJqa6dYS_4core7convert4FromdE4from,unique,58
	.globl	_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value4fromNtB6_5ValueINtNtCs8xEFJqa6dYS_4core7convert4FromdE4from
	.p2align	4
_RNvXs_NtNtCsavOST1yGCNT_10serde_json5value4fromNtB6_5ValueINtNtCs8xEFJqa6dYS_4core7convert4FromdE4from:
.Lfunc_begin50:
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
	jl	.LBB50_2
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
.LBB50_2:
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
.Lfunc_end50:
	.seh_endproc

	.def	_RNvXsr_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXsr_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt,unique,59
	.p2align	4
_RNvXsr_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt:
.Lfunc_begin51:
	movq	%rdx, %r8
	movq	8(%rcx), %rax
	movq	16(%rcx), %rdx
	movq	%rax, %rcx
	jmp	_RNvXsh_NtCs8xEFJqa6dYS_4core3fmteNtB5_5Debug3fmt
.Lfunc_end51:

	.def	_RNvYNtNtCsfQUUnEvlYZE_5alloc6string6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_fmtCsavOST1yGCNT_10serde_json;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvYNtNtCsfQUUnEvlYZE_5alloc6string6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_fmtCsavOST1yGCNT_10serde_json,unique,60
	.p2align	4
_RNvYNtNtCsfQUUnEvlYZE_5alloc6string6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_fmtCsavOST1yGCNT_10serde_json:
.Lfunc_begin52:
	movq	%r8, %r9
	movq	%rdx, %r8
	leaq	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.114(%rip), %rdx
	jmp	_RNvNtCs8xEFJqa6dYS_4core3fmt5write
.Lfunc_end52:

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920,unique,61
	.globl	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920:
	.asciz	"C:\\Users\\there\\.cargo\\registry\\src\\index.crates.io-1949cf8c6b5b557f\\serde_json-1.0.150\\src\\read.rs"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.1,unique,62
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.1:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920
	.asciz	"b\000\000\000\000\000\000\000\000\002\000\000\023\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.2,unique,63
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.2:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920
	.asciz	"b\000\000\000\000\000\000\000\005\002\000\0003\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.3,unique,64
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.3:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920
	.asciz	"b\000\000\000\000\000\000\000\t\002\000\000>\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.4,unique,65
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.4:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920
	.asciz	"b\000\000\000\000\000\000\000\017\002\000\000:\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.12,unique,66
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.12:
	.asciz	"/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\alloc\\src\\collections\\btree\\navigate.rs"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.13,unique,67
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.13:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.12
	.asciz	"_\000\000\000\000\000\000\000\306\000\000\000'\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.14,unique,68
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.14:
	.asciz	"/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\str\\pattern.rs"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.16,unique,69
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.16:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.14
	.asciz	"O\000\000\000\000\000\000\000V\006\000\000\024\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.17,unique,70
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.17:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.14
	.asciz	"O\000\000\000\000\000\000\000E\006\000\000\024\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.18,unique,71
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.18:
	.zero	2,32

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.23,unique,72
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.23:
	.byte	10

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.24,unique,73
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.24:
	.byte	125

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.25,unique,74
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.25:
	.byte	91

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.26,unique,75
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.26:
	.byte	123

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.27,unique,76
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.27:
	.ascii	",\n"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.28,unique,77
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.28:
	.ascii	": "

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.29,unique,78
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.29:
	.byte	93

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.30,unique,79
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.30:
	.byte	34

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.31,unique,80
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.31:
	.ascii	"false"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.32,unique,81
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.32:
	.ascii	"true"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.33,unique,82
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.33:
	.ascii	"null"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.34,unique,83
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.34:
	.byte	44

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.35,unique,84
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.35:
	.byte	58

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.36,unique,85
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.36:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.12
	.asciz	"_\000\000\000\000\000\000\000X\002\000\0000\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.43,unique,86
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.43:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.12
	.asciz	"_\000\000\000\000\000\000\000\026\002\000\000/\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.44,unique,87
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.44:
	.asciz	"\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\001\000\000\000\000\000\000"
	.quad	_RNvXsK_NtCs8xEFJqa6dYS_4core3fmtNtB5_5ErrorNtB5_5Debug3fmt

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.45,unique,88
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.45:
	.ascii	"assertion failed: self.is_char_boundary(new_len)"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.46,unique,89
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.46:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920
	.asciz	"b\000\000\000\000\000\000\000\263\001\000\000\032\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920,unique,90
	.globl	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920
	.asciz	"b\000\000\000\000\000\000\000\253\001\000\000=\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.48.llvm.16186315980599473920,unique,91
	.globl	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.48.llvm.16186315980599473920
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.48.llvm.16186315980599473920:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920
	.asciz	"b\000\000\000\000\000\000\000\246\001\000\000E\000\000"

	.section	.rdata,"dr",one_only,_RNvNtCsavOST1yGCNT_10serde_json4read4HEX0,unique,92
	.globl	_RNvNtCsavOST1yGCNT_10serde_json4read4HEX0
	.p2align	1, 0x0
_RNvNtCsavOST1yGCNT_10serde_json4read4HEX0:
	.ascii	"\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\000\000\001\000\002\000\003\000\004\000\005\000\006\000\007\000\b\000\t\000\377\377\377\377\377\377\377\377\377\377\377\377\377\377\n\000\013\000\f\000\r\000\016\000\017\000\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\n\000\013\000\f\000\r\000\016\000\017\000\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377"

	.section	.rdata,"dr",one_only,_RNvNtCsavOST1yGCNT_10serde_json4read4HEX1,unique,93
	.globl	_RNvNtCsavOST1yGCNT_10serde_json4read4HEX1
	.p2align	1, 0x0
_RNvNtCsavOST1yGCNT_10serde_json4read4HEX1:
	.ascii	"\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\000\000\020\000 \0000\000@\000P\000`\000p\000\200\000\220\000\377\377\377\377\377\377\377\377\377\377\377\377\377\377\240\000\260\000\300\000\320\000\340\000\360\000\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\240\000\260\000\300\000\320\000\340\000\360\000\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377\377"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.54,unique,94
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.54:
	.ascii	" at line "

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.55,unique,95
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.55:
	.asciz	"C:\\Users\\there\\.cargo\\registry\\src\\index.crates.io-1949cf8c6b5b557f\\serde_json-1.0.150\\src\\error.rs"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.56,unique,96
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.56:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.55
	.asciz	"c\000\000\000\000\000\000\000\367\001\000\000!\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.57,unique,97
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.57:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.55
	.asciz	"c\000\000\000\000\000\000\000\373\001\000\000\f\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.58,unique,98
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.58:
	.ascii	" column "

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.59,unique,99
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.59:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.55
	.asciz	"c\000\000\000\000\000\000\000\002\002\000\000!\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.60,unique,100
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.60:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.55
	.asciz	"c\000\000\000\000\000\000\000\013\002\000\000*\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.61,unique,101
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.61:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.55
	.asciz	"c\000\000\000\000\000\000\000\017\002\000\000,\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.62,unique,102
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.62:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.55
	.asciz	"c\000\000\000\000\000\000\000\024\002\000\000\t\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63,unique,103
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.63:
	.ascii	"fmt error"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.77,unique,104
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.77:
	.ascii	"EOF while parsing a list"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.78,unique,105
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.78:
	.ascii	"EOF while parsing an object"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.79,unique,106
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.79:
	.ascii	"EOF while parsing a string"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.80,unique,107
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.80:
	.ascii	"EOF while parsing a value"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.81,unique,108
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.81:
	.ascii	"expected `:`"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.82,unique,109
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.82:
	.ascii	"expected `,` or `]`"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.83,unique,110
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.83:
	.ascii	"expected `,` or `}`"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.84,unique,111
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.84:
	.ascii	"expected ident"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.85,unique,112
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.85:
	.ascii	"expected value"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.86,unique,113
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.86:
	.ascii	"expected `\"`"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.87,unique,114
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.87:
	.ascii	"invalid escape"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.88,unique,115
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.88:
	.ascii	"invalid number"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.89,unique,116
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.89:
	.ascii	"number out of range"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.90,unique,117
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.90:
	.ascii	"invalid unicode code point"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.91,unique,118
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.91:
	.ascii	"control character (\\u0000-\\u001F) found while parsing a string"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.92,unique,119
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.92:
	.ascii	"key must be a string"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.93,unique,120
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.93:
	.ascii	"invalid value: expected key to be a number in quotes"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.94,unique,121
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.94:
	.ascii	"float key must be finite (got NaN or +/-inf)"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.95,unique,122
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.95:
	.ascii	"lone leading surrogate in hex escape"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.96,unique,123
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.96:
	.ascii	"trailing comma"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.97,unique,124
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.97:
	.ascii	"trailing characters"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.98,unique,125
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.98:
	.ascii	"unexpected end of hex escape"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.99,unique,126
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.99:
	.ascii	"recursion limit exceeded"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.107,unique,127
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.107:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920
	.asciz	"b\000\000\000\000\000\000\000\\\002\000\000\023\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.108,unique,128
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.108:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920
	.asciz	"b\000\000\000\000\000\000\000n\002\000\000\031\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.109,unique,129
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.109:
	.asciz	"\006Error(\300\b, line: \300\n, column: \300\001)"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.110,unique,130
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.110:
	.asciz	"C:\\Users\\there\\.cargo\\registry\\src\\index.crates.io-1949cf8c6b5b557f\\itoa-1.0.18\\src\\lib.rs"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.111.llvm.16186315980599473920,unique,131
	.globl	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.111.llvm.16186315980599473920
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.111.llvm.16186315980599473920:
	.asciz	"\016invalid type: \300\013, expected \300"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.112.llvm.16186315980599473920,unique,132
	.globl	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.112.llvm.16186315980599473920
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.112.llvm.16186315980599473920:
	.asciz	"\017invalid value: \300\013, expected \300"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.113,unique,133
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.113:
	.asciz	"\020floating point `\300\001`"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.114,unique,134
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.114:
	.quad	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsfQUUnEvlYZE_5alloc6string6StringECsavOST1yGCNT_10serde_json
	.asciz	"\030\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_str
	.quad	_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write10write_char
	.quad	_RNvYNtNtCsfQUUnEvlYZE_5alloc6string6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_fmtCsavOST1yGCNT_10serde_json

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.115,unique,135
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.115:
	.ascii	"a Display implementation returned an error unexpectedly"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.116,unique,136
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.116:
	.asciz	"/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\alloc\\src\\string.rs"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.117,unique,137
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.117:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.116
	.asciz	"K\000\000\000\000\000\000\000\177\013\000\000\016\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.118,unique,138
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.118:
	.ascii	"Error"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.119,unique,139
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.119:
	.ascii	"inf"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.120,unique,140
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.120:
	.ascii	"-inf"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.121,unique,141
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.121:
	.ascii	"NaN"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.129,unique,142
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.129:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.110
	.asciz	"Z\000\000\000\000\000\000\000\274\000\000\000\001\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.130,unique,143
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.130:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.12
	.asciz	"_\000\000\000\000\000\000\000\241\000\000\000$\000\000"

	.section	.rdata,"dr",one_only,anon.1ca9eb9e844b4c4297e93f6b65ed1a15.134,unique,144
	.p2align	3, 0x0
anon.1ca9eb9e844b4c4297e93f6b65ed1a15.134:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.14
	.asciz	"O\000\000\000\000\000\000\000\277\004\000\000$\000\000"

	.section	.rdata,"dr",one_only,_RNvNtCsavOST1yGCNT_10serde_json3ser6ESCAPE,unique,145
	.globl	_RNvNtCsavOST1yGCNT_10serde_json3ser6ESCAPE
_RNvNtCsavOST1yGCNT_10serde_json3ser6ESCAPE:
	.asciz	"uuuuuuuubtnufruuuuuuuuuuuuuuuuuu\000\000\"\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\\\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000"

	.section	.rdata,"dr",one_only,_RNvNvNtNtCsavOST1yGCNT_10serde_json3ser9Formatter17write_char_escape10HEX_DIGITS,unique,146
	.globl	_RNvNvNtNtCsavOST1yGCNT_10serde_json3ser9Formatter17write_char_escape10HEX_DIGITS
_RNvNvNtNtCsavOST1yGCNT_10serde_json3ser9Formatter17write_char_escape10HEX_DIGITS:
	.ascii	"0123456789abcdef"

	.section	.rdata,"dr",one_only,_RNvNtCsavOST1yGCNT_10serde_json2de5POW10,unique,147
	.globl	_RNvNtCsavOST1yGCNT_10serde_json2de5POW10
	.p2align	3, 0x0
_RNvNtCsavOST1yGCNT_10serde_json2de5POW10:
	.ascii	"\000\000\000\000\000\000\360?\000\000\000\000\000\000$@\000\000\000\000\000\000Y@\000\000\000\000\000@\217@\000\000\000\000\000\210\303@\000\000\000\000\000j\370@\000\000\000\000\200\204.A\000\000\000\000\320\022cA\000\000\000\000\204\327\227A\000\000\000\000e\315\315A\000\000\000 _\240\002B\000\000\000\350vH7B\000\000\000\242\224\032mB\000\000@\345\2340\242B\000\000\220\036\304\274\326B\000\0004&\365k\fC\000\200\3407y\303AC\000\240\330\205W4vC\000\310Ngm\301\253C\000=\221`\344X\341C@\214\265x\035\257\025DP\357\342\326\344\032KD\222\325M\006\317\360\200D\366J\341\307\002-\265D\264\235\331yCx\352D\221\002(,*\213 E5\0032\267\364\255TE\002\204\376\344q\331\211E\201\022\037/\347'\300E!\327\346\372\3401\364E\352\214\2409Y>)F$\260\b\210\357\215_F\027n\005\265\265\270\223F\234\311F\"\343\246\310F\003|\330\352\233\320\376F\202M\307raB3G\343 y\317\371\022hG\033iWC\270\027\236G\261\241\026*\323\316\322G\035J\234\364\207\202\007H\245\\\303\361)c=H\347\031\0327\372]rHa\240\340\304x\365\246Hy\310\030\366\326\262\334HL}\317Y\306\357\021I\236\\C\360\267kFI\3063T\354\245\006|I\\\240\264\263'\204\261Is\310\241\2401\345\345I\217:\312\b~^\033J\232d~\305\016\033QJ\300\375\335v\322a\205J0}\225\024G\272\272J>n\335ll\264\360J\316\311\024\210\207\341$KA\374\031j\351\031ZK\251=P\3421P\220K\023M\344Z>d\304KW`\235\361M}\371Km\270\004n\241\334/LD\363\302\344\344\351cL\025\260\363\035^\344\230L\033\234p\245u\035\317L\221af\207ir\003M\365\371?\351\003O8Mr\370\217\343\304bnMG\3739\016\273\375\242M\031z\310\321)\275\327M\237\230:Ft\254\rNd\237\344\253\310\213BN=\307\335\326\272.wN\f9\225\214i\372\254N\247C\335\367\201\034\342N\221\224\324u\242\243\026O\265\271I\023\213LLO\021\024\016\354\326\257\201O\026\231\021\247\314\033\266O[\377\325\320\277\242\353O\231\277\205\342\267E!P\177/'\333%\227UP_\373\360Q\357\374\212P\033\2356\223\025\336\300PbD\004\370\232\025\365P{U\005\266\001[*QmU\303\021\341x`Q\310*4V\031\227\224Qz5\301\253\337\274\311Ql\301X\313\013\026\000R\307\361.\276\216\0334R9\256\272mr\"iR\307Y)\t\017k\237R\035\330\271e\351\242\323R$N(\277\243\213\bS\255a\362\256\214\256>S\f}W\355\027-sSO\\\255\350]\370\247Sc\263\330bu\366\335S\036p\307]\t\272\022T%L9\265\213hGT.\237\207\242\256B}T}\303\224%\255I\262T\\\364\371n\030\334\346Tsq\270\212\036\223\034U\350F\263\026\363\333QU\242\030`\334\357R\206U\312\036x\323\253\347\273U?\023+d\313p\361U\016\3305=\376\314%V\022N\203\314=@[V\313\020\322\237&\b\221V\376\224\306G0J\305V=:\270Y\274\234\372Vf$\023\270\365\2410W\200\355\027&s\312dW\340\350\235\357\017\375\231W\214\261\302\365)>\320W\357]3s\264M\004Xk5\000\220!a9X\305B\000\364i\271oX\273)\2008\342\323\243X*4\240\306\332\310\330X5AHx\021\373\016Y\301(-\353\352\\CY\361r\370\245%4xY\255\217v\017/A\256Y\314\031\252i\275\350\342Y?\240\024\304\354\242\027ZO\310\031\365\247\213MZ2\0350\371Hw\202Z~$|7\033\025\267Z\236-[\005b\332\354Z\202\374XC}\b\"[\243;/\224\234\212V[\214\n;\271C-\214[\227\346\304SJ\234\301[= \266\350\\\003\366[M\250\343\"4\204+\\0I\316\225\2402a\\|\333A\273H\177\225\\[R\022\352\032\337\312\\ysK\322p\313\000]WP\336\006M\3764]m\344\225H\340=j]\304\256]-\254f\240]u\032\2658W\200\324]\022a\342\006m\240\t^\253|M$D\004@^\326\333`-U\005t^\314\022\271x\252\006\251^\177W\347\026UH\337^\257\226P.5\215\023_[\274\344y\202pH_r\353]\030\243\214~_'\263:\357\345\027\263_\361_\tk\337\335\347_\355\267\313EW\325\035`\364R\237\213V\245R`\261'\207.\254N\207`\235\361(:W\"\275`\002\227Y\204v5\362`\303\374o%\324\302&a\364\373\313.\211s\\ax}?\2755\310\221a\326\\\217,C:\306a\f4\263\367\323\310\373a\207\000\320z\204]1b\251\000\204\231\345\264eb\324\000\345\377\036\"\233b\204 \357_S\365\320b\245\350\3527\2502\005c\317\242\345ER\177:c\301\205\257k\223\217pc2g\233Fx\263\244c\376@BXV\340\331c\237h)\3675,\020d\306\302\363tC7Ddx\2630R\024EydV\340\274fY\226\257d6\f6\340\367\275\343dC\217C\330u\255\030e\024sTN\323\330Ne\354\307\364\020\204G\203e\350\3711\025e\031\270eax~Z\276\037\356e=\013\217\370\326\323\"f\f\316\262\266\314\210Wf\217\201_\344\377j\215f\371\260\273\356\337b\302f8\235j\352\227\373\366f\206D\005\345}\272,g\324J#\257\216\364ag\211\035\354Z\262q\226g\353$\247\361\036\016\314g\023w\bW\323\210\001h\327\224\312,\b\3535h\r:\3757\312ekhHD\376b\236\037\241hZ\325\275\373\205g\325h\261J\255zg\301\ni\257N\254\254\340\270@iZb\327\327\030\347ti\361:\315\r\337 \252i\326D\240h\213T\340i\fV\310B\256i\024j\217kz\323\031\204Ijs\006YH \345\177j\b\2447-4\357\263j\n\215\2058\001\353\350jL\360\246\206\301%\037k0V(\364\230wSk\273k21\177U\210k\252\006\177\375\336j\276k*do^\313\002\363k5=\0136~\303'l\202\f\216\303]\264]l\321\3078\232\272\220\222l\306\371\306@\3514\307l7\270\370\220#\002\375l#s\233:V!2m\353OB\311\253\251fm\346\343\222\273\026T\234mp\316;5\216\264\321m\f\302\212\302\261!\006n\217r-3\036\252;n\231g\374\337RJqn\177\201\373\227\347\234\245n\337a\372}!\004\333n,}\274\356\224\342\020ov\234k*:\033Eo\224\203\006\265\bbzo=\022$qE}\260o\314\026m\315\226\234\344o\177\\\310\200\274\303\031p\3179}\320U\032PpC\210\234D\353 \204pT\252\303\025&)\271p\351\2244\233os\357p\021\335\000\301%\250#qV\024A1/\222XqkY\221\375\272\266\216q\343\327z\33642\303q\334\215\031\026\302\376\367qS\361\237\233r\376-r\324\366C\241\007\277br\211\364\224\211\311n\227r\2531\372\353{J\315r\013_|s\215N\002s\315v[\3200\3426s\201Tr\004\275\232ls\320t\307\"\266\340\241s\004Ry\253\343X\326s\206\246W\226\034\357\013t\024\310\366\335quAt\030ztU\316\322ut\236\230\321\352\201G\253tc\377\3022\261\f\341t<\277s\177\335O\025u\013\257P\337\324\243Jugm\222\013e\246\200u\300\bwN\376\317\264u\361\312\024\342\375\003\352u\326\376L\255~B v\214>\240X\036STv/N\310\356\345g\211v\273azj\337\301\277v\025}\214\242+\331\363vZ\234/\213v\317(wp\203\373-T\003_w&2\275\234\024b\223w\260~\354\303\231:\310w\\\236\3474@I\376w\371\302\020!\310\3552x\270\363T):\251gx\2450\252\263\210\223\235xg^Jp5|\322x\001\366\\\314B\033\007y\2023t\177\023\342<y1\240\250/L\rry=\310\222;\237\220\246yMzw\n\3074\334yp\254\212f\374\240\021z\214W-\200;\tFzo\2558`\212\213{zel#|67\261z\177G,\033\004\205\345z^Y\367!E\346\032{\333\227:5\353\317P{\322=\211\002\346\003\205{F\215+\203\337D\272{L8\373\261\013k\360{_\006z\236\316\205$|\366\207\030FB\247Y|\372T\317k\211\b\220|8*\303\306\253\n\304|\307\364s\270V\r\371|\370\361\220f\254P/};\227\032\300k\222c}\n=!\260\006w\230}L\214)\\\310\224\316}\260\367\2319\375\034\003~\234u\000\210<\3447~\003\223\000\252K\335m~\342[@JO\252\242~\332r\320\034\343T\327~\220\217\004\344\033*\r\177\272\331\202nQ:B\177)\220#\312\345\310v\1773t\254<\037{\254\177\240\310\353\205\363\314\341\177"

	.section	.data,"dw",one_only,__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920,unique,148
	.globl	__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920
	.p2align	3, 0x0
__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.0.llvm.16186315980599473920

	.section	.data,"dw",one_only,__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920,unique,149
	.globl	__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920
	.p2align	3, 0x0
__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.47.llvm.16186315980599473920

	.section	.data,"dw",one_only,__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.48.llvm.16186315980599473920,unique,150
	.globl	__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.48.llvm.16186315980599473920
	.p2align	3, 0x0
__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.48.llvm.16186315980599473920:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.48.llvm.16186315980599473920

	.section	.data,"dw",one_only,__imp__RNvNtCsavOST1yGCNT_10serde_json4read4HEX0,unique,151
	.globl	__imp__RNvNtCsavOST1yGCNT_10serde_json4read4HEX0
	.p2align	3, 0x0
__imp__RNvNtCsavOST1yGCNT_10serde_json4read4HEX0:
	.quad	_RNvNtCsavOST1yGCNT_10serde_json4read4HEX0

	.section	.data,"dw",one_only,__imp__RNvNtCsavOST1yGCNT_10serde_json4read4HEX1,unique,152
	.globl	__imp__RNvNtCsavOST1yGCNT_10serde_json4read4HEX1
	.p2align	3, 0x0
__imp__RNvNtCsavOST1yGCNT_10serde_json4read4HEX1:
	.quad	_RNvNtCsavOST1yGCNT_10serde_json4read4HEX1

	.section	.data,"dw",one_only,__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.111.llvm.16186315980599473920,unique,153
	.globl	__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.111.llvm.16186315980599473920
	.p2align	3, 0x0
__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.111.llvm.16186315980599473920:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.111.llvm.16186315980599473920

	.section	.data,"dw",one_only,__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.112.llvm.16186315980599473920,unique,154
	.globl	__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.112.llvm.16186315980599473920
	.p2align	3, 0x0
__imp_anon.1ca9eb9e844b4c4297e93f6b65ed1a15.112.llvm.16186315980599473920:
	.quad	anon.1ca9eb9e844b4c4297e93f6b65ed1a15.112.llvm.16186315980599473920

	.section	.data,"dw",one_only,__imp__RNvNtCsavOST1yGCNT_10serde_json3ser6ESCAPE,unique,155
	.globl	__imp__RNvNtCsavOST1yGCNT_10serde_json3ser6ESCAPE
	.p2align	3, 0x0
__imp__RNvNtCsavOST1yGCNT_10serde_json3ser6ESCAPE:
	.quad	_RNvNtCsavOST1yGCNT_10serde_json3ser6ESCAPE

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCsavOST1yGCNT_10serde_json3ser9Formatter17write_char_escape10HEX_DIGITS,unique,156
	.globl	__imp__RNvNvNtNtCsavOST1yGCNT_10serde_json3ser9Formatter17write_char_escape10HEX_DIGITS
	.p2align	3, 0x0
__imp__RNvNvNtNtCsavOST1yGCNT_10serde_json3ser9Formatter17write_char_escape10HEX_DIGITS:
	.quad	_RNvNvNtNtCsavOST1yGCNT_10serde_json3ser9Formatter17write_char_escape10HEX_DIGITS

	.section	.data,"dw",one_only,__imp__RNvNtCsavOST1yGCNT_10serde_json2de5POW10,unique,157
	.globl	__imp__RNvNtCsavOST1yGCNT_10serde_json2de5POW10
	.p2align	3, 0x0
__imp__RNvNtCsavOST1yGCNT_10serde_json2de5POW10:
	.quad	_RNvNtCsavOST1yGCNT_10serde_json2de5POW10

	.section	.debug$S,"dr"
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp109-.Ltmp108
.Ltmp108:
	.short	.Ltmp111-.Ltmp110
.Ltmp110:
	.short	4353
	.long	0
	.asciz	"S:\\GTOpen-research\\postflop-gpu-20261016\\runs\\D090-wide-OR\\build\\probe.serde_json-83a0670a02a34a4d.serde_json.7a74452f5594281f-cgu.0.rcgu.o.rcgu.o"
	.p2align	2, 0x0
.Ltmp111:
	.short	.Ltmp113-.Ltmp112
.Ltmp112:
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
.Ltmp113:
.Ltmp109:
	.p2align	2, 0x0
	.cv_filechecksums
	.cv_stringtable
	.long	241
	.long	.Ltmp115-.Ltmp114
.Ltmp114:
	.short	.Ltmp117-.Ltmp116
.Ltmp116:
	.short	4428
	.long	4099
	.p2align	2, 0x0
.Ltmp117:
.Ltmp115:
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
