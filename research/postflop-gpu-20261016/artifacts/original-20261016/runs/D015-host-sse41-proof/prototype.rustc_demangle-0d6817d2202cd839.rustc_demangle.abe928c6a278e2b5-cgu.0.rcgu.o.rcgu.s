	.def	@feat.00;
	.scl	3;
	.type	0;
	.endef
	.globl	@feat.00
@feat.00 = 0
	.file	"rustc_demangle.abe928c6a278e2b5-cgu.0"
	.def	_RINvMNtCs8xEFJqa6dYS_4core3stre18trim_start_matchesReECseL4M8JimfzJ_14rustc_demangle;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvMNtCs8xEFJqa6dYS_4core3stre18trim_start_matchesReECseL4M8JimfzJ_14rustc_demangle,unique,0
	.globl	_RINvMNtCs8xEFJqa6dYS_4core3stre18trim_start_matchesReECseL4M8JimfzJ_14rustc_demangle
_RINvMNtCs8xEFJqa6dYS_4core3stre18trim_start_matchesReECseL4M8JimfzJ_14rustc_demangle:
.Lfunc_begin0:
.seh_proc _RINvMNtCs8xEFJqa6dYS_4core3stre18trim_start_matchesReECseL4M8JimfzJ_14rustc_demangle
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
	movq	%r8, %rax
	movq	%rdx, %rsi
	movq	%rcx, %rdi
	movq	%r9, 32(%rsp)
	leaq	-80(%rbp), %rbx
	movq	%rbx, %rcx
	movq	%rdi, %rdx
	movq	%rsi, %r8
	movq	%rax, %r9
	callq	_RNvMsu_NtNtCs8xEFJqa6dYS_4core3str7patternNtB5_11StrSearcher3new
	leaq	24(%rbp), %r14
.LBB0_1:
	movq	%r14, %rcx
	movq	%rbx, %rdx
	callq	_RNvXsv_NtNtCs8xEFJqa6dYS_4core3str7patternNtB5_11StrSearcherNtB5_8Searcher4next
	movq	24(%rbp), %rax
	testq	%rax, %rax
	je	.LBB0_1
	cmpl	$1, %eax
	jne	.LBB0_4
	movq	32(%rbp), %rax
	jmp	.LBB0_5
.LBB0_4:
	movq	%rsi, %rax
.LBB0_5:
	subq	%rax, %rsi
	addq	%rax, %rdi
	movq	%rdi, %rax
	movq	%rsi, %rdx
	.seh_startepilogue
	addq	$176, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end0:
	.seh_endproc

	.def	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer13print_backrefNCNvB2_10print_paths_0EB8_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer13print_backrefNCNvB2_10print_paths_0EB8_,unique,1
_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer13print_backrefNCNvB2_10print_paths_0EB8_:
.Lfunc_begin1:
.seh_proc _RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer13print_backrefNCNvB2_10print_paths_0EB8_
	pushq	%rbp
	.seh_pushreg %rbp
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
	movq	%rcx, %rsi
	cmpq	$0, (%rcx)
	je	.LBB1_4
	movl	%edx, %ebx
	leaq	-24(%rbp), %rdi
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	callq	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser7backref
	cmpq	$0, (%rdi)
	je	.LBB1_6
	cmpq	$0, 32(%rsi)
	je	.LBB1_10
	movups	(%rsi), %xmm0
	movups	16(%rsi), %xmm1
	movaps	%xmm1, -48(%rbp)
	movaps	%xmm0, -64(%rbp)
	movups	-24(%rbp), %xmm0
	movups	-8(%rbp), %xmm1
	movups	%xmm0, (%rsi)
	movups	%xmm1, 16(%rsi)
	movq	%rsi, %rcx
	movl	%ebx, %edx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_path
	movaps	-64(%rbp), %xmm0
	movaps	-48(%rbp), %xmm1
	movups	%xmm0, (%rsi)
	movups	%xmm1, 16(%rsi)
	jmp	.LBB1_12
.LBB1_4:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB1_10
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.2(%rip), %rdx
	movl	$1, %r8d
	.seh_startepilogue
	addq	$104, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	jmp	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
.LBB1_6:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB1_9
	movb	-16(%rbp), %al
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.1(%rip), %r8
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	testb	%al, %al
	cmovneq	%r8, %rdx
	movzbl	%al, %eax
	leaq	(%rax,%rax,8), %r8
	addq	$16, %r8
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movl	%eax, %ecx
	movb	$1, %al
	testb	%cl, %cl
	jne	.LBB1_11
.LBB1_9:
	movups	-24(%rbp), %xmm0
	movups	-8(%rbp), %xmm1
	movups	%xmm1, 16(%rsi)
	movups	%xmm0, (%rsi)
.LBB1_10:
	xorl	%eax, %eax
.LBB1_11:
.LBB1_12:
	.seh_startepilogue
	addq	$104, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end1:
	.seh_endproc

	.def	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer13print_backrefNCNvB2_11print_consts4_0EB8_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer13print_backrefNCNvB2_11print_consts4_0EB8_,unique,2
_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer13print_backrefNCNvB2_11print_consts4_0EB8_:
.Lfunc_begin2:
.seh_proc _RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer13print_backrefNCNvB2_11print_consts4_0EB8_
	pushq	%rbp
	.seh_pushreg %rbp
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
	movq	%rcx, %rsi
	cmpq	$0, (%rcx)
	je	.LBB2_4
	movl	%edx, %ebx
	leaq	-24(%rbp), %rdi
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	callq	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser7backref
	cmpq	$0, (%rdi)
	je	.LBB2_6
	cmpq	$0, 32(%rsi)
	je	.LBB2_10
	movups	(%rsi), %xmm0
	movups	16(%rsi), %xmm1
	movaps	%xmm1, -48(%rbp)
	movaps	%xmm0, -64(%rbp)
	movups	-24(%rbp), %xmm0
	movups	-8(%rbp), %xmm1
	movups	%xmm0, (%rsi)
	movups	%xmm1, 16(%rsi)
	movq	%rsi, %rcx
	movl	%ebx, %edx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer11print_const
	movaps	-64(%rbp), %xmm0
	movaps	-48(%rbp), %xmm1
	movups	%xmm0, (%rsi)
	movups	%xmm1, 16(%rsi)
	jmp	.LBB2_12
.LBB2_4:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB2_10
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.2(%rip), %rdx
	movl	$1, %r8d
	.seh_startepilogue
	addq	$104, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	jmp	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
.LBB2_6:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB2_9
	movb	-16(%rbp), %al
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.1(%rip), %r8
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	testb	%al, %al
	cmovneq	%r8, %rdx
	movzbl	%al, %eax
	leaq	(%rax,%rax,8), %r8
	addq	$16, %r8
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movl	%eax, %ecx
	movb	$1, %al
	testb	%cl, %cl
	jne	.LBB2_11
.LBB2_9:
	movups	-24(%rbp), %xmm0
	movups	-8(%rbp), %xmm1
	movups	%xmm1, 16(%rsi)
	movups	%xmm0, (%rsi)
.LBB2_10:
	xorl	%eax, %eax
.LBB2_11:
.LBB2_12:
	.seh_startepilogue
	addq	$104, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end2:
	.seh_endproc

	.def	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer13print_backrefNvB2_10print_typeEB8_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer13print_backrefNvB2_10print_typeEB8_,unique,3
_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer13print_backrefNvB2_10print_typeEB8_:
.Lfunc_begin3:
.seh_proc _RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer13print_backrefNvB2_10print_typeEB8_
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$96, %rsp
	.seh_stackalloc 96
	leaq	96(%rsp), %rbp
	.seh_setframe %rbp, 96
	.seh_endprologue
	movq	%rcx, %rsi
	cmpq	$0, (%rcx)
	je	.LBB3_4
	leaq	-32(%rbp), %rdi
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	callq	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser7backref
	cmpq	$0, (%rdi)
	je	.LBB3_6
	cmpq	$0, 32(%rsi)
	je	.LBB3_10
	movups	(%rsi), %xmm0
	movups	16(%rsi), %xmm1
	movaps	%xmm1, -48(%rbp)
	movaps	%xmm0, -64(%rbp)
	movups	-32(%rbp), %xmm0
	movups	-16(%rbp), %xmm1
	movups	%xmm0, (%rsi)
	movups	%xmm1, 16(%rsi)
	movq	%rsi, %rcx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_type
	movaps	-64(%rbp), %xmm0
	movaps	-48(%rbp), %xmm1
	movups	%xmm0, (%rsi)
	movups	%xmm1, 16(%rsi)
	jmp	.LBB3_12
.LBB3_4:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB3_10
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.2(%rip), %rdx
	movl	$1, %r8d
	.seh_startepilogue
	addq	$96, %rsp
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	jmp	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
.LBB3_6:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB3_9
	movb	-24(%rbp), %al
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.1(%rip), %r8
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	testb	%al, %al
	cmovneq	%r8, %rdx
	movzbl	%al, %eax
	leaq	(%rax,%rax,8), %r8
	addq	$16, %r8
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movl	%eax, %ecx
	movb	$1, %al
	testb	%cl, %cl
	jne	.LBB3_11
.LBB3_9:
	movups	-32(%rbp), %xmm0
	movups	-16(%rbp), %xmm1
	movups	%xmm1, 16(%rsi)
	movups	%xmm0, (%rsi)
.LBB3_10:
	xorl	%eax, %eax
.LBB3_11:
.LBB3_12:
	.seh_startepilogue
	addq	$96, %rsp
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end3:
	.seh_endproc

	.def	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNCNvB2_11print_consts0_0EB8_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNCNvB2_11print_consts0_0EB8_,unique,4
_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNCNvB2_11print_consts0_0EB8_:
.Lfunc_begin4:
.seh_proc _RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNCNvB2_11print_consts0_0EB8_
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
	leaq	32(%rsp), %rbp
	.seh_setframe %rbp, 32
	.seh_endprologue
	movq	(%rcx), %rax
	testq	%rax, %rax
	je	.LBB4_1
	movq	%rcx, %rdi
	xorl	%esi, %esi
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.8(%rip), %rbx
	xorl	%r14d, %r14d
.LBB4_3:
	movq	16(%rdi), %rcx
	cmpq	8(%rdi), %rcx
	jae	.LBB4_6
	cmpb	$69, (%rax,%rcx)
	je	.LBB4_5
.LBB4_6:
	subq	$1, %r14
	jb	.LBB4_10
	movq	32(%rdi), %rcx
	testq	%rcx, %rcx
	je	.LBB4_10
	movl	$2, %r8d
	movq	%rbx, %rdx
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB4_9
.LBB4_10:
	movq	%rdi, %rcx
	movb	$1, %dl
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer11print_const
	testb	%al, %al
	jne	.LBB4_9
	movq	(%rdi), %rax
	testq	%rax, %rax
	jne	.LBB4_3
	jmp	.LBB4_12
.LBB4_9:
	movl	$1, %esi
	jmp	.LBB4_12
.LBB4_5:
	incq	%rcx
	movq	%rcx, 16(%rdi)
.LBB4_1:
	xorl	%esi, %esi
.LBB4_12:
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end4:
	.seh_endproc

	.def	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNCNvB2_11print_consts1_0EB8_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNCNvB2_11print_consts1_0EB8_,unique,5
_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNCNvB2_11print_consts1_0EB8_:
.Lfunc_begin5:
.seh_proc _RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNCNvB2_11print_consts1_0EB8_
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
	leaq	32(%rsp), %rbp
	.seh_setframe %rbp, 32
	.seh_endprologue
	movq	(%rcx), %rax
	testq	%rax, %rax
	je	.LBB5_9
	movq	%rcx, %rbx
	xorl	%edi, %edi
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.8(%rip), %r14
	xorl	%esi, %esi
.LBB5_2:
	movq	16(%rbx), %rcx
	cmpq	8(%rbx), %rcx
	jae	.LBB5_4
	cmpb	$69, (%rax,%rcx)
	je	.LBB5_11
.LBB5_4:
	testq	%rsi, %rsi
	je	.LBB5_7
	movq	32(%rbx), %rcx
	testq	%rcx, %rcx
	je	.LBB5_7
	movl	$2, %r8d
	movq	%r14, %rdx
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB5_10
.LBB5_7:
	movq	%rbx, %rcx
	movb	$1, %dl
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer11print_const
	testb	%al, %al
	jne	.LBB5_10
	incq	%rsi
	movq	(%rbx), %rax
	testq	%rax, %rax
	jne	.LBB5_2
	jmp	.LBB5_13
.LBB5_9:
	xorl	%esi, %esi
	jmp	.LBB5_12
.LBB5_10:
	movl	$1, %edi
	jmp	.LBB5_13
.LBB5_11:
	incq	%rcx
	movq	%rcx, 16(%rbx)
.LBB5_12:
	xorl	%edi, %edi
.LBB5_13:
	movq	%rdi, %rax
	movq	%rsi, %rdx
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end5:
	.seh_endproc

	.def	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNCNvB2_11print_consts3_0EB8_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNCNvB2_11print_consts3_0EB8_,unique,6
_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNCNvB2_11print_consts3_0EB8_:
.Lfunc_begin6:
.seh_proc _RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNCNvB2_11print_consts3_0EB8_
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
	subq	$104, %rsp
	.seh_stackalloc 104
	leaq	96(%rsp), %rbp
	.seh_setframe %rbp, 96
	.seh_endprologue
	movq	(%rcx), %rax
	testq	%rax, %rax
	je	.LBB6_27
	movq	%rcx, %rsi
	leaq	-24(%rbp), %rdi
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.2(%rip), %rbx
	leaq	-64(%rbp), %r14
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.8(%rip), %r12
	xorl	%r15d, %r15d
.LBB6_2:
	movq	16(%rsi), %rcx
	cmpq	8(%rsi), %rcx
	jae	.LBB6_5
	cmpb	$69, (%rax,%rcx)
	je	.LBB6_4
.LBB6_5:
	subq	$1, %r15
	jb	.LBB6_12
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB6_12
	movl	$2, %r8d
	movq	%r12, %rdx
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB6_8
	cmpq	$0, (%rsi)
	je	.LBB6_10
.LBB6_12:
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	movb	$115, %r8b
	callq	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser14opt_integer_62
	cmpb	$1, -24(%rbp)
	je	.LBB6_13
	cmpq	$0, (%rsi)
	je	.LBB6_10
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	callq	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser5ident
	cmpq	$0, -24(%rbp)
	je	.LBB6_19
	movups	-24(%rbp), %xmm0
	movups	-8(%rbp), %xmm1
	movaps	%xmm1, -48(%rbp)
	movaps	%xmm0, -64(%rbp)
	movq	32(%rsi), %rdx
	testq	%rdx, %rdx
	je	.LBB6_25
	movq	%r14, %rcx
	callq	_RNvXs0_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_5IdentNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt
	testb	%al, %al
	jne	.LBB6_8
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB6_25
	movl	$2, %r8d
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.29(%rip), %rdx
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB6_8
.LBB6_25:
	movq	%rsi, %rcx
	movb	$1, %dl
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer11print_const
	testb	%al, %al
	jne	.LBB6_8
	jmp	.LBB6_26
.LBB6_10:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB6_26
	movl	$1, %r13d
	movl	$1, %r8d
	movq	%rbx, %rdx
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB6_28
.LBB6_26:
	movq	(%rsi), %rax
	testq	%rax, %rax
	jne	.LBB6_2
	jmp	.LBB6_27
.LBB6_13:
	movb	-23(%rbp), %bl
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB6_16
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.1(%rip), %rax
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	testb	%bl, %bl
	cmovneq	%rax, %rdx
	movzbl	%bl, %eax
	leaq	(%rax,%rax,8), %r8
	addq	$16, %r8
	jmp	.LBB6_15
.LBB6_19:
	movb	-16(%rbp), %bl
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB6_16
	movzbl	%bl, %eax
	leaq	(%rax,%rax,8), %r8
	addq	$16, %r8
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.1(%rip), %r9
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	testb	%al, %al
	cmovneq	%r9, %rdx
.LBB6_15:
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	je	.LBB6_16
.LBB6_8:
	movl	$1, %r13d
	jmp	.LBB6_28
.LBB6_16:
	movq	$0, (%rsi)
	movb	%bl, 8(%rsi)
	jmp	.LBB6_27
.LBB6_4:
	incq	%rcx
	movq	%rcx, 16(%rsi)
.LBB6_27:
	xorl	%r13d, %r13d
.LBB6_28:
	movq	%r13, %rax
	.seh_startepilogue
	addq	$104, %rsp
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
.Lfunc_end6:
	.seh_endproc

	.def	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNvB2_10print_typeEB8_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNvB2_10print_typeEB8_,unique,7
_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNvB2_10print_typeEB8_:
.Lfunc_begin7:
.seh_proc _RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNvB2_10print_typeEB8_
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
	leaq	32(%rsp), %rbp
	.seh_setframe %rbp, 32
	.seh_endprologue
	movq	(%rcx), %rax
	testq	%rax, %rax
	je	.LBB7_9
	movq	%rcx, %rbx
	xorl	%edi, %edi
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.8(%rip), %r14
	xorl	%esi, %esi
.LBB7_2:
	movq	16(%rbx), %rcx
	cmpq	8(%rbx), %rcx
	jae	.LBB7_4
	cmpb	$69, (%rax,%rcx)
	je	.LBB7_11
.LBB7_4:
	testq	%rsi, %rsi
	je	.LBB7_7
	movq	32(%rbx), %rcx
	testq	%rcx, %rcx
	je	.LBB7_7
	movl	$2, %r8d
	movq	%r14, %rdx
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB7_10
.LBB7_7:
	movq	%rbx, %rcx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_type
	testb	%al, %al
	jne	.LBB7_10
	incq	%rsi
	movq	(%rbx), %rax
	testq	%rax, %rax
	jne	.LBB7_2
	jmp	.LBB7_13
.LBB7_9:
	xorl	%esi, %esi
	jmp	.LBB7_12
.LBB7_10:
	movl	$1, %edi
	jmp	.LBB7_13
.LBB7_11:
	incq	%rcx
	movq	%rcx, 16(%rbx)
.LBB7_12:
	xorl	%edi, %edi
.LBB7_13:
	movq	%rdi, %rax
	movq	%rsi, %rdx
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end7:
	.seh_endproc

	.def	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNvB2_15print_dyn_traitEB8_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNvB2_15print_dyn_traitEB8_,unique,8
_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNvB2_15print_dyn_traitEB8_:
.Lfunc_begin8:
.seh_proc _RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNvB2_15print_dyn_traitEB8_
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
	subq	$104, %rsp
	.seh_stackalloc 104
	leaq	96(%rsp), %rbp
	.seh_setframe %rbp, 96
	.seh_endprologue
	movq	(%rcx), %rax
	testq	%rax, %rax
	je	.LBB8_28
	movq	%rcx, %rsi
	leaq	-24(%rbp), %r15
	leaq	-64(%rbp), %r12
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.74(%rip), %r13
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.55(%rip), %r14
	xorl	%ebx, %ebx
.LBB8_2:
	movq	16(%rsi), %rcx
	cmpq	8(%rsi), %rcx
	jae	.LBB8_5
	cmpb	$69, (%rax,%rcx)
	je	.LBB8_4
.LBB8_5:
	testq	%rbx, %rbx
	je	.LBB8_10
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB8_10
	movl	$3, %r8d
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.28(%rip), %rdx
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB8_8
.LBB8_10:
	movq	%rsi, %rcx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer30print_path_maybe_open_generics
	cmpb	$2, %al
	je	.LBB8_8
	movq	(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB8_17
.LBB8_12:
	movq	16(%rsi), %rdx
	cmpq	8(%rsi), %rdx
	jae	.LBB8_17
	cmpb	$112, (%rcx,%rdx)
	jne	.LBB8_17
	incq	%rdx
	movq	%rdx, 16(%rsi)
	testb	$1, %al
	je	.LBB8_15
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB8_23
	movl	$2, %r8d
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.8(%rip), %rdx
	jmp	.LBB8_22
.LBB8_15:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB8_23
	movl	$1, %r8d
	movq	%r14, %rdx
.LBB8_22:
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB8_8
.LBB8_23:
	cmpq	$0, (%rsi)
	je	.LBB8_24
	movq	%r15, %rcx
	movq	%rsi, %rdx
	callq	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser5ident
	cmpq	$0, -24(%rbp)
	je	.LBB8_30
	movups	-24(%rbp), %xmm0
	movups	-8(%rbp), %xmm1
	movaps	%xmm1, -48(%rbp)
	movaps	%xmm0, -64(%rbp)
	movq	32(%rsi), %rdx
	testq	%rdx, %rdx
	je	.LBB8_37
	movq	%r12, %rcx
	callq	_RNvXs0_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_5IdentNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt
	testb	%al, %al
	jne	.LBB8_8
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB8_37
	movl	$3, %r8d
	movq	%r13, %rdx
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB8_8
.LBB8_37:
	movq	(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB8_41
	movq	16(%rsi), %rax
	cmpq	8(%rsi), %rax
	jae	.LBB8_41
	cmpb	$75, (%rcx,%rax)
	jne	.LBB8_41
	incq	%rax
	movq	%rax, 16(%rsi)
	movq	%rsi, %rcx
	xorl	%edx, %edx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer11print_const
	jmp	.LBB8_42
.LBB8_41:
	movq	%rsi, %rcx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_type
.LBB8_42:
	testb	%al, %al
	jne	.LBB8_8
	movq	(%rsi), %rcx
	movb	$1, %al
	testq	%rcx, %rcx
	jne	.LBB8_12
	jmp	.LBB8_18
.LBB8_17:
	testb	$1, %al
	je	.LBB8_27
.LBB8_18:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB8_27
	movl	$1, %edi
	movl	$1, %r8d
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.57(%rip), %rdx
.LBB8_26:
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB8_9
.LBB8_27:
	movq	(%rsi), %rax
	incq	%rbx
	testq	%rax, %rax
	jne	.LBB8_2
	jmp	.LBB8_28
.LBB8_24:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB8_27
	movl	$1, %edi
	movl	$1, %r8d
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.2(%rip), %rdx
	jmp	.LBB8_26
.LBB8_30:
	movb	-16(%rbp), %bl
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB8_32
	movzbl	%bl, %eax
	leaq	(%rax,%rax,8), %r8
	addq	$16, %r8
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.1(%rip), %r9
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	testb	%al, %al
	cmovneq	%r9, %rdx
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	je	.LBB8_32
.LBB8_8:
	movl	$1, %edi
	jmp	.LBB8_9
.LBB8_32:
	movq	$0, (%rsi)
	movb	%bl, 8(%rsi)
	jmp	.LBB8_28
.LBB8_4:
	incq	%rcx
	movq	%rcx, 16(%rsi)
.LBB8_28:
	xorl	%edi, %edi
.LBB8_9:
	movq	%rdi, %rax
	.seh_startepilogue
	addq	$104, %rsp
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
.Lfunc_end8:
	.seh_endproc

	.def	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNvB2_17print_generic_argEB8_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNvB2_17print_generic_argEB8_,unique,9
_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNvB2_17print_generic_argEB8_:
.Lfunc_begin9:
.seh_proc _RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNvB2_17print_generic_argEB8_
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
	movq	(%rcx), %rax
	testq	%rax, %rax
	je	.LBB9_1
	movq	%rcx, %rsi
	xorl	%edi, %edi
	leaq	-8(%rbp), %rbx
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.8(%rip), %r14
	xorl	%r15d, %r15d
.LBB9_3:
	movq	8(%rsi), %r8
	movq	16(%rsi), %rdx
	cmpq	%r8, %rdx
	jae	.LBB9_6
	cmpb	$69, (%rax,%rdx)
	je	.LBB9_5
.LBB9_6:
	subq	$1, %r15
	jb	.LBB9_12
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB9_12
	movl	$2, %r8d
	movq	%r14, %rdx
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB9_9
	movq	(%rsi), %rax
	testq	%rax, %rax
	je	.LBB9_20
	movq	8(%rsi), %r8
	movq	16(%rsi), %rdx
.LBB9_12:
	cmpq	%r8, %rdx
	jae	.LBB9_20
	movzbl	(%rax,%rdx), %eax
	cmpl	$75, %eax
	je	.LBB9_19
	cmpl	$76, %eax
	jne	.LBB9_20
	incq	%rdx
	movq	%rdx, 16(%rsi)
	movq	%rbx, %rcx
	movq	%rsi, %rdx
	callq	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser10integer_62
	cmpb	$0, -8(%rbp)
	jne	.LBB9_16
	movq	(%rbp), %rdx
	movq	%rsi, %rcx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer25print_lifetime_from_index
	jmp	.LBB9_21
.LBB9_20:
	movq	%rsi, %rcx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_type
.LBB9_21:
	testb	%al, %al
	jne	.LBB9_9
	movq	(%rsi), %rax
	testq	%rax, %rax
	jne	.LBB9_3
	jmp	.LBB9_23
.LBB9_19:
	incq	%rdx
	movq	%rdx, 16(%rsi)
	movq	%rsi, %rcx
	xorl	%edx, %edx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer11print_const
	jmp	.LBB9_21
.LBB9_5:
	incq	%rdx
	movq	%rdx, 16(%rsi)
.LBB9_1:
	xorl	%edi, %edi
	jmp	.LBB9_23
.LBB9_16:
	movb	-7(%rbp), %bl
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB9_18
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.1(%rip), %rax
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	testb	%bl, %bl
	cmovneq	%rax, %rdx
	movzbl	%bl, %eax
	leaq	(%rax,%rax,8), %r8
	addq	$16, %r8
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	je	.LBB9_18
.LBB9_9:
	movl	$1, %edi
.LBB9_23:
	movq	%rdi, %rax
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
.LBB9_18:
	movq	$0, (%rsi)
	movb	%bl, 8(%rsi)
	jmp	.LBB9_1
.Lfunc_end9:
	.seh_endproc

	.def	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer17skipping_printingNCNvB2_10print_path0EB8_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer17skipping_printingNCNvB2_10print_path0EB8_,unique,10
_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer17skipping_printingNCNvB2_10print_path0EB8_:
.Lfunc_begin10:
.seh_proc _RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer17skipping_printingNCNvB2_10print_path0EB8_
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$48, %rsp
	.seh_stackalloc 48
	leaq	48(%rsp), %rbp
	.seh_setframe %rbp, 48
	.seh_endprologue
	movq	%rcx, %rsi
	movq	32(%rcx), %rdi
	movq	$0, 32(%rcx)
	xorl	%edx, %edx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_path
	testb	%al, %al
	jne	.LBB10_1
	movq	%rdi, 32(%rsi)
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB10_1:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.5(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.3(%rip), %rcx
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.40(%rip), %r9
	leaq	-1(%rbp), %r8
	movl	$61, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core6result13unwrap_failed
	ud2
.Lfunc_end10:
	.seh_endproc

	.def	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer26print_quoted_escaped_charsINtNtNtNtCs8xEFJqa6dYS_4core4iter7sources4once4OncecEEB8_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer26print_quoted_escaped_charsINtNtNtNtCs8xEFJqa6dYS_4core4iter7sources4once4OncecEEB8_,unique,11
_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer26print_quoted_escaped_charsINtNtNtNtCs8xEFJqa6dYS_4core4iter7sources4once4OncecEEB8_:
.Lfunc_begin11:
.seh_proc _RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer26print_quoted_escaped_charsINtNtNtNtCs8xEFJqa6dYS_4core4iter7sources4once4OncecEEB8_
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
	subq	$56, %rsp
	.seh_stackalloc 56
	leaq	48(%rsp), %rbp
	.seh_setframe %rbp, 48
	.seh_endprologue
	testq	%rcx, %rcx
	je	.LBB11_1
	movl	%edx, %r14d
	movq	%rcx, %rdi
	movq	(%rcx), %rcx
	movq	8(%rdi), %rax
	movl	$39, %edx
	callq	*32(%rax)
	movb	$1, %sil
	testb	%al, %al
	jne	.LBB11_13
	leaq	-8(%rbp), %rbx
.LBB11_4:
	cmpl	$34, %r14d
	je	.LBB11_7
	cmpl	$-1, %r14d
	je	.LBB11_6
	movq	%rbx, %rcx
	movl	%r14d, %edx
	callq	_RNvMNtNtCs8xEFJqa6dYS_4core4char7methodsc16escape_debug_ext
	movb	5(%rbp), %r14b
	movzbl	4(%rbp), %r15d
	movl	-8(%rbp), %r12d
	movzbl	%r14b, %r13d
.LBB11_9:
	cmpq	%r13, %r15
	jae	.LBB11_14
	movl	%r12d, %edx
	cmpb	$-128, %r14b
	ja	.LBB11_12
	movzbl	-8(%rbp,%r15), %edx
.LBB11_12:
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	callq	*32(%rax)
	incq	%r15
	testb	%al, %al
	je	.LBB11_9
	jmp	.LBB11_13
.LBB11_7:
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	movl	$34, %edx
	callq	*32(%rax)
	movl	$-1, %r14d
	testb	%al, %al
	je	.LBB11_4
	jmp	.LBB11_13
.LBB11_14:
	movl	$-1, %r14d
	jmp	.LBB11_4
.LBB11_1:
	xorl	%esi, %esi
.LBB11_13:
	movl	%esi, %eax
	.seh_startepilogue
	addq	$56, %rsp
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
.LBB11_6:
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	movq	32(%rax), %rax
	movl	$39, %edx
	.seh_startepilogue
	addq	$56, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r13
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	rex64 jmpq	*%rax
.Lfunc_end11:
	.seh_endproc

	.def	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer9in_binderNCNvB2_10print_type0EB8_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer9in_binderNCNvB2_10print_type0EB8_,unique,12
_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer9in_binderNCNvB2_10print_type0EB8_:
.Lfunc_begin12:
.seh_proc _RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer9in_binderNCNvB2_10print_type0EB8_
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
	movq	%rcx, %rsi
	cmpq	$0, (%rcx)
	je	.LBB12_1
	leaq	-8(%rbp), %rdi
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	movb	$71, %r8b
	callq	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser14opt_integer_62
	cmpb	$1, (%rdi)
	jne	.LBB12_8
	movb	-7(%rbp), %bl
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB12_7
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.1(%rip), %rax
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	testb	%bl, %bl
	cmovneq	%rax, %rdx
	movzbl	%bl, %eax
	leaq	(%rax,%rax,8), %r8
	addq	$16, %r8
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB12_16
.LBB12_7:
	movq	$0, (%rsi)
	movb	%bl, 8(%rsi)
	jmp	.LBB12_2
.LBB12_1:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB12_2
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.2(%rip), %rdx
	movl	$1, %r8d
	.seh_startepilogue
	addq	$56, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	jmp	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
.LBB12_2:
	xorl	%edi, %edi
.LBB12_16:
	movl	%edi, %eax
.LBB12_17:
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
.LBB12_8:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB12_22
	movq	(%rbp), %r14
	testq	%r14, %r14
	je	.LBB12_10
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.6(%rip), %rdx
	movl	$4, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB12_16
	xorl	%r15d, %r15d
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.8(%rip), %rbx
.LBB12_13:
	cmpq	%r15, %r14
	je	.LBB12_14
	testq	%r15, %r15
	je	.LBB12_19
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB12_19
	movl	$2, %r8d
	movq	%rbx, %rdx
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB12_16
.LBB12_19:
	incl	40(%rsi)
	movl	$1, %edx
	movq	%rsi, %rcx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer25print_lifetime_from_index
	incq	%r15
	testb	%al, %al
	je	.LBB12_13
	jmp	.LBB12_16
.LBB12_22:
	movq	%rsi, %rcx
	.seh_startepilogue
	addq	$56, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	jmp	_RNCNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB7_7Printer10print_type0B9_
.LBB12_14:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB12_10
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.7(%rip), %rdx
	movl	$2, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB12_16
.LBB12_10:
	movq	%rsi, %rcx
	callq	_RNCNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB7_7Printer10print_type0B9_
	subl	%r14d, 40(%rsi)
	jmp	.LBB12_17
.Lfunc_end12:
	.seh_endproc

	.def	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer9in_binderNCNvB2_10print_types_0EB8_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer9in_binderNCNvB2_10print_types_0EB8_,unique,13
_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer9in_binderNCNvB2_10print_types_0EB8_:
.Lfunc_begin13:
.seh_proc _RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer9in_binderNCNvB2_10print_types_0EB8_
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
	movq	%rcx, %rsi
	cmpq	$0, (%rcx)
	je	.LBB13_1
	leaq	-8(%rbp), %rdi
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	movb	$71, %r8b
	callq	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser14opt_integer_62
	cmpb	$1, (%rdi)
	jne	.LBB13_8
	movb	-7(%rbp), %bl
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB13_7
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.1(%rip), %rax
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	testb	%bl, %bl
	cmovneq	%rax, %rdx
	movzbl	%bl, %eax
	leaq	(%rax,%rax,8), %r8
	addq	$16, %r8
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB13_17
.LBB13_7:
	movq	$0, (%rsi)
	movb	%bl, 8(%rsi)
	jmp	.LBB13_2
.LBB13_1:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB13_2
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.2(%rip), %rdx
	movl	$1, %r8d
	.seh_startepilogue
	addq	$56, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	jmp	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
.LBB13_2:
	xorl	%edi, %edi
	jmp	.LBB13_17
.LBB13_8:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB13_16
	movq	(%rbp), %r14
	testq	%r14, %r14
	je	.LBB13_10
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.6(%rip), %rdx
	movl	$4, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB13_17
	xorl	%r15d, %r15d
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.8(%rip), %rbx
.LBB13_13:
	cmpq	%r15, %r14
	je	.LBB13_14
	testq	%r15, %r15
	je	.LBB13_19
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB13_19
	movl	$2, %r8d
	movq	%rbx, %rdx
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB13_17
.LBB13_19:
	incl	40(%rsi)
	movl	$1, %edx
	movq	%rsi, %rcx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer25print_lifetime_from_index
	incq	%r15
	testb	%al, %al
	je	.LBB13_13
	jmp	.LBB13_17
.LBB13_16:
	movq	%rsi, %rcx
	callq	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNvB2_15print_dyn_traitEB8_
	movq	%rax, %rdi
	jmp	.LBB13_17
.LBB13_14:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB13_10
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.7(%rip), %rdx
	movl	$2, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB13_17
.LBB13_10:
	movq	%rsi, %rcx
	callq	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNvB2_15print_dyn_traitEB8_
	movq	%rax, %rdi
	subl	%r14d, 40(%rsi)
.LBB13_17:
	movl	%edi, %eax
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
.Lfunc_end13:
	.seh_endproc

	.def	_RNCNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB7_7Printer10print_type0B9_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB7_7Printer10print_type0B9_,unique,14
_RNCNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB7_7Printer10print_type0B9_:
.Lfunc_begin14:
.seh_proc _RNCNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB7_7Printer10print_type0B9_
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
	subq	$184, %rsp
	.seh_stackalloc 184
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	movq	%rcx, %rbx
	movq	(%rcx), %rcx
	testq	%rcx, %rcx
	je	.LBB14_36
	movq	8(%rbx), %rdx
	movq	16(%rbx), %rax
	cmpq	%rdx, %rax
	jae	.LBB14_4
	cmpb	$85, (%rcx,%rax)
	jne	.LBB14_4
	incq	%rax
	movq	%rax, 16(%rbx)
	movb	$1, %r15b
	jmp	.LBB14_5
.LBB14_4:
	xorl	%r15d, %r15d
.LBB14_5:
	cmpq	%rdx, %rax
	jae	.LBB14_10
	cmpb	$75, (%rcx,%rax)
	jne	.LBB14_10
	leaq	1(%rax), %r8
	movq	%r8, 16(%rbx)
	cmpq	%rdx, %r8
	jae	.LBB14_15
	cmpb	$67, (%rcx,%r8)
	jne	.LBB14_15
	addq	$2, %rax
	movq	%rax, 16(%rbx)
	movl	$1, %r14d
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.19(%rip), %rdi
	jmp	.LBB14_18
.LBB14_10:
	testb	%r15b, %r15b
	je	.LBB14_36
	xorl	%edi, %edi
.LBB14_12:
	movq	32(%rbx), %rcx
	testq	%rcx, %rcx
	je	.LBB14_14
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.20(%rip), %rdx
	movl	$7, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %sil
	testb	%al, %al
	jne	.LBB14_55
.LBB14_14:
	testq	%rdi, %rdi
	jne	.LBB14_19
	jmp	.LBB14_36
.LBB14_15:
	leaq	-16(%rbp), %rsi
	movq	%rsi, %rcx
	movq	%rbx, %rdx
	callq	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser5ident
	movq	(%rsi), %rdi
	testq	%rdi, %rdi
	je	.LBB14_48
	movq	-8(%rbp), %r14
	testq	%r14, %r14
	je	.LBB14_51
	cmpq	$0, 8(%rbp)
	jne	.LBB14_51
.LBB14_18:
	testb	%r15b, %r15b
	jne	.LBB14_12
.LBB14_19:
	movq	32(%rbx), %r12
	testq	%r12, %r12
	je	.LBB14_21
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.21(%rip), %rdx
	movl	$8, %r8d
	movq	%r12, %rcx
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %sil
	testb	%al, %al
	jne	.LBB14_55
.LBB14_21:
	xorl	%eax, %eax
	leaq	-88(%rbp), %rcx
	movq	%rax, (%rcx)
	movq	%r14, 8(%rcx)
	movq	%rdi, 16(%rcx)
	movq	%r14, 24(%rcx)
	movq	%rax, 32(%rcx)
	movq	%r14, 40(%rcx)
	movabsq	$408021893215, %rax
	movq	%rax, 48(%rcx)
	movb	$1, 56(%rcx)
	movw	$1, 64(%rcx)
	callq	_RNvMsf_NtNtCs8xEFJqa6dYS_4core3str4iterINtB5_13SplitInternalcE4nextCseL4M8JimfzJ_14rustc_demangle
	testq	%rax, %rax
	je	.LBB14_56
	testq	%r12, %r12
	je	.LBB14_24
	movq	%rdx, %r8
	movq	%r12, %rcx
	movq	%rax, %rdx
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB14_35
.LBB14_24:
	leaq	-16(%rbp), %rax
	leaq	-88(%rbp), %rsi
	movl	$9, %ecx
	movq	%rax, %rdi
	rep;movsq (%rsi), %es:(%rdi)
	movq	%rax, %rcx
	callq	_RNvMsf_NtNtCs8xEFJqa6dYS_4core3str4iterINtB5_13SplitInternalcE4nextCseL4M8JimfzJ_14rustc_demangle
	testq	%rax, %rax
	je	.LBB14_33
	movq	%rax, %r15
	movq	%rdx, %r13
	leaq	-16(%rbp), %rsi
	movq	%r12, %r14
	movq	%r12, %rdi
.LBB14_26:
	testq	%r14, %r14
	je	.LBB14_31
	movl	$1, %r8d
	movq	%r14, %rcx
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.24(%rip), %rdx
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB14_35
	testq	%rdi, %rdi
	je	.LBB14_30
	movq	%rdi, %r14
	movq	%rdi, %rcx
	movq	%r15, %rdx
	movq	%r13, %r8
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movq	%rdi, %r12
	testb	%al, %al
	jne	.LBB14_35
	jmp	.LBB14_32
.LBB14_30:
	xorl	%r12d, %r12d
.LBB14_31:
	xorl	%r14d, %r14d
.LBB14_32:
	movq	%rsi, %rcx
	callq	_RNvMsf_NtNtCs8xEFJqa6dYS_4core3str4iterINtB5_13SplitInternalcE4nextCseL4M8JimfzJ_14rustc_demangle
	movq	%rax, %r15
	movq	%rdx, %r13
	testq	%rax, %rax
	jne	.LBB14_26
.LBB14_33:
	testq	%r12, %r12
	je	.LBB14_36
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.23(%rip), %rdx
	movl	$2, %r8d
	movq	%r12, %rcx
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	je	.LBB14_36
.LBB14_35:
	movb	$1, %sil
	jmp	.LBB14_55
.LBB14_36:
	movq	32(%rbx), %rcx
	testq	%rcx, %rcx
	je	.LBB14_38
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.25(%rip), %rdx
	movl	$3, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %sil
	testb	%al, %al
	jne	.LBB14_55
.LBB14_38:
	movq	%rbx, %rcx
	callq	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNvB2_10print_typeEB8_
	movb	$1, %sil
	testb	$1, %al
	jne	.LBB14_55
	movq	32(%rbx), %rcx
	testq	%rcx, %rcx
	je	.LBB14_41
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.26(%rip), %rdx
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB14_55
.LBB14_41:
	movq	(%rbx), %rcx
	testq	%rcx, %rcx
	je	.LBB14_45
	movq	16(%rbx), %rax
	cmpq	8(%rbx), %rax
	jae	.LBB14_45
	cmpb	$117, (%rcx,%rax)
	jne	.LBB14_45
	incq	%rax
	movq	%rax, 16(%rbx)
	jmp	.LBB14_54
.LBB14_45:
	movq	32(%rbx), %rcx
	testq	%rcx, %rcx
	je	.LBB14_47
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.27(%rip), %rdx
	movl	$4, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB14_55
.LBB14_47:
	movq	%rbx, %rcx
	.seh_startepilogue
	addq	$184, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r13
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	jmp	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_type
.LBB14_48:
	movb	-8(%rbp), %dil
	movq	32(%rbx), %rcx
	testq	%rcx, %rcx
	je	.LBB14_50
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.1(%rip), %rax
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	testb	%dil, %dil
	cmovneq	%rax, %rdx
	movzbl	%dil, %eax
	leaq	(%rax,%rax,8), %r8
	addq	$16, %r8
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %sil
	testb	%al, %al
	jne	.LBB14_55
.LBB14_50:
	movq	$0, (%rbx)
	movb	%dil, 8(%rbx)
	jmp	.LBB14_54
.LBB14_51:
	movq	32(%rbx), %rcx
	testq	%rcx, %rcx
	je	.LBB14_53
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	movl	$16, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %sil
	testb	%al, %al
	jne	.LBB14_55
.LBB14_53:
	movq	$0, (%rbx)
	movb	$0, 8(%rbx)
.LBB14_54:
	xorl	%esi, %esi
.LBB14_55:
	movl	%esi, %eax
	.seh_startepilogue
	addq	$184, %rsp
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
.LBB14_56:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.22(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end14:
	.seh_endproc

	.def	_RNvCseL4M8JimfzJ_14rustc_demangle12try_demangle;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvCseL4M8JimfzJ_14rustc_demangle12try_demangle,unique,15
	.globl	_RNvCseL4M8JimfzJ_14rustc_demangle12try_demangle
_RNvCseL4M8JimfzJ_14rustc_demangle12try_demangle:
.Lfunc_begin15:
.seh_proc _RNvCseL4M8JimfzJ_14rustc_demangle12try_demangle
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$96, %rsp
	.seh_stackalloc 96
	leaq	96(%rsp), %rbp
	.seh_setframe %rbp, 96
	.seh_endprologue
	movq	%rcx, %rsi
	leaq	-64(%rbp), %rdi
	movq	%rdi, %rcx
	callq	_RNvCseL4M8JimfzJ_14rustc_demangle8demangle
	cmpq	$0, (%rdi)
	je	.LBB15_2
	movups	-64(%rbp), %xmm0
	movups	-48(%rbp), %xmm1
	movups	-32(%rbp), %xmm2
	movups	-16(%rbp), %xmm3
	movups	%xmm3, 48(%rsi)
	movups	%xmm2, 32(%rsi)
	movups	%xmm1, 16(%rsi)
	movups	%xmm0, (%rsi)
	jmp	.LBB15_3
.LBB15_2:
	movq	$2, (%rsi)
.LBB15_3:
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$96, %rsp
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end15:
	.seh_endproc

	.def	_RNvCseL4M8JimfzJ_14rustc_demangle8demangle;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvCseL4M8JimfzJ_14rustc_demangle8demangle,unique,16
	.globl	_RNvCseL4M8JimfzJ_14rustc_demangle8demangle
_RNvCseL4M8JimfzJ_14rustc_demangle8demangle:
.Lfunc_begin16:
.seh_proc _RNvCseL4M8JimfzJ_14rustc_demangle8demangle
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
	subq	$216, %rsp
	.seh_stackalloc 216
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	movq	%r8, %rsi
	movq	%rdx, %rbx
	movq	%rcx, 48(%rbp)
	movq	$6, 32(%rsp)
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.32(%rip), %r9
	leaq	-56(%rbp), %r14
	movq	%r14, %rcx
	callq	_RNvMsu_NtNtCs8xEFJqa6dYS_4core3str7patternNtB5_11StrSearcher3new
	cmpb	$0, (%r14)
	je	.LBB16_17
	movq	(%rbp), %r14
	movq	16(%rbp), %rax
	movq	40(%rbp), %rdx
	leaq	-1(%rdx), %r8
	movq	24(%rbp), %r10
	movq	32(%rbp), %r11
	cmpq	$-1, %r14
	movq	%rsi, 72(%rbp)
	je	.LBB16_21
	movq	-16(%rbp), %rdi
	leaq	(%rdi,%r8), %rcx
	cmpq	%r10, %rcx
	jae	.LBB16_35
	movq	-24(%rbp), %r15
	movq	-48(%rbp), %r12
	movq	-32(%rbp), %r9
	movq	%rdx, %r13
	movq	%r9, 64(%rbp)
	subq	%r9, %r13
.LBB16_4:
	movzbl	(%rax,%rcx), %ecx
	btq	%rcx, %r15
	jae	.LBB16_9
	cmpq	%r12, %r14
	movq	%r12, %rcx
	cmovaq	%r14, %rcx
	leaq	(%rax,%rdi), %r8
.LBB16_6:
	cmpq	%rdx, %rcx
	jae	.LBB16_10
	leaq	1(%rcx), %r9
	movb	(%r11,%rcx), %sil
	cmpb	(%r8,%rcx), %sil
	movq	%r9, %rcx
	je	.LBB16_6
	subq	%r12, %rdi
	addq	%r9, %rdi
	xorl	%r14d, %r14d
	movq	72(%rbp), %rsi
	jmp	.LBB16_15
.LBB16_9:
	addq	%rdx, %rdi
	xorl	%r14d, %r14d
	jmp	.LBB16_16
.LBB16_10:
	leaq	-1(%r12), %rcx
	movq	72(%rbp), %rsi
.LBB16_11:
	leaq	1(%rcx), %r9
	cmpq	%r9, %r14
	jae	.LBB16_37
	cmpq	%rdx, %rcx
	jae	.LBB16_172
	movb	(%r11,%rcx), %r9b
	cmpb	(%r8,%rcx), %r9b
	leaq	-1(%rcx), %rcx
	je	.LBB16_11
	addq	64(%rbp), %rdi
	movq	%r13, %r14
.LBB16_15:
	leaq	-1(%rdx), %r8
.LBB16_16:
	leaq	(%rdi,%r8), %rcx
	cmpq	%r10, %rcx
	jb	.LBB16_4
	jmp	.LBB16_35
.LBB16_17:
	leaq	-80(%rbp), %r14
	leaq	-56(%rbp), %r15
.LBB16_18:
	movq	%r14, %rcx
	movq	%r15, %rdx
	callq	_RNvXsv_NtNtCs8xEFJqa6dYS_4core3str7patternNtB5_11StrSearcherNtB5_8Searcher4next
	movq	-80(%rbp), %rax
	cmpq	$1, %rax
	je	.LBB16_18
	testq	%rax, %rax
	jne	.LBB16_35
	movq	-72(%rbp), %rdi
	jmp	.LBB16_37
.LBB16_21:
	movq	-16(%rbp), %rdi
	leaq	(%rdi,%r8), %rcx
	cmpq	%r10, %rcx
	jae	.LBB16_35
	movq	-24(%rbp), %r8
	movq	%r8, 64(%rbp)
	movq	-48(%rbp), %r15
	movq	-32(%rbp), %r8
	movq	%r8, 56(%rbp)
	leaq	-1(%r15), %r13
	leaq	(%rax,%r15), %r12
	leaq	(%r11,%r15), %r8
.LBB16_23:
	movzbl	(%rax,%rcx), %ecx
	movq	64(%rbp), %r9
	btq	%rcx, %r9
	jae	.LBB16_27
	xorl	%ecx, %ecx
	movq	%rdi, %rsi
.LBB16_25:
	leaq	(%r15,%rcx), %r9
	cmpq	%rdx, %r9
	jae	.LBB16_28
	movb	(%r8,%rcx), %r14b
	leaq	1(%rsi), %r9
	incq	%rcx
	cmpb	(%r12,%rsi), %r14b
	movq	%r9, %rsi
	je	.LBB16_25
	jmp	.LBB16_34
.LBB16_27:
	addq	%rdx, %rdi
	jmp	.LBB16_33
.LBB16_28:
	leaq	(%rax,%rdi), %rsi
	movq	%r13, %rcx
.LBB16_29:
	cmpq	$-1, %rcx
	je	.LBB16_36
	cmpq	%rdx, %r13
	jae	.LBB16_172
	movb	(%r11,%rcx), %r9b
	cmpb	(%rsi,%rcx), %r9b
	leaq	-1(%rcx), %rcx
	je	.LBB16_29
	addq	56(%rbp), %rdi
.LBB16_33:
	movq	%rdi, %r9
.LBB16_34:
	leaq	-1(%rdx), %rcx
	addq	%r9, %rcx
	movq	%r9, %rdi
	cmpq	%r10, %rcx
	movq	72(%rbp), %rsi
	jb	.LBB16_23
.LBB16_35:
	movq	%rbx, %r15
	jmp	.LBB16_58
.LBB16_36:
	movq	72(%rbp), %rsi
.LBB16_37:
	movq	%rdi, %r8
	addq	$6, %r8
	movq	%rbx, %r15
	je	.LBB16_42
	cmpq	%rsi, %r8
	jae	.LBB16_41
	cmpb	$-65, (%r15,%r8)
	jg	.LBB16_42
.LBB16_40:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.34(%rip), %rax
	jmp	.LBB16_71
.LBB16_41:
	jne	.LBB16_40
.LBB16_42:
	addq	%r15, %r8
	leaq	(%r15,%rsi), %rax
.LBB16_43:
	cmpq	%rax, %r8
	je	.LBB16_52
	movb	(%r8), %r10b
	movzbl	%r10b, %ecx
	testb	%cl, %cl
	js	.LBB16_46
	incq	%r8
	jmp	.LBB16_51
.LBB16_46:
	movl	%ecx, %edx
	andl	$31, %edx
	movzbl	1(%r8), %r11d
	andl	$63, %r11d
	cmpb	$-33, %cl
	jbe	.LBB16_49
	movzbl	2(%r8), %ecx
	shll	$6, %r11d
	andl	$63, %ecx
	orl	%r11d, %ecx
	cmpb	$-16, %r10b
	jb	.LBB16_50
	movzbl	3(%r8), %r9d
	addq	$4, %r8
	andl	$7, %edx
	shll	$18, %edx
	shll	$6, %ecx
	andl	$63, %r9d
	orl	%ecx, %r9d
	orl	%edx, %r9d
	movl	%r9d, %ecx
	jmp	.LBB16_51
.LBB16_49:
	addq	$2, %r8
	shll	$6, %edx
	orl	%r11d, %edx
	movl	%edx, %ecx
	jmp	.LBB16_51
.LBB16_50:
	addq	$3, %r8
	shll	$12, %edx
	orl	%edx, %ecx
.LBB16_51:
	leal	-58(%rcx), %edx
	cmpl	$-10, %edx
	setb	%dl
	addl	$-71, %ecx
	cmpl	$-7, %ecx
	setb	%cl
	testb	%dl, %cl
	je	.LBB16_43
	jmp	.LBB16_58
.LBB16_52:
	testq	%rdi, %rdi
	je	.LBB16_56
	cmpq	%rsi, %rdi
	jae	.LBB16_57
	cmpb	$-65, (%r15,%rdi)
	jle	.LBB16_174
	movq	%rdi, %rsi
	jmp	.LBB16_58
.LBB16_56:
	movl	$1, %r10d
	xorl	%esi, %esi
	xorl	%r14d, %r14d
	jmp	.LBB16_143
.LBB16_57:
	jne	.LBB16_174
.LBB16_58:
	cmpq	$3, %rsi
	jae	.LBB16_61
	cmpq	$2, %rsi
	jne	.LBB16_122
	cmpw	$20058, (%r15)
	je	.LBB16_73
	jmp	.LBB16_119
.LBB16_61:
	movzwl	(%r15), %eax
	xorl	$23135, %eax
	movzbl	2(%r15), %ecx
	xorl	$78, %ecx
	orw	%ax, %cx
	je	.LBB16_68
	cmpw	$20058, (%r15)
	je	.LBB16_72
	cmpq	$3, %rsi
	je	.LBB16_115
	cmpl	$1314545503, (%r15)
	jne	.LBB16_115
	movl	$4, %r8d
	movq	$-4, %r14
	cmpq	$5, %rsi
	jb	.LBB16_74
	cmpb	$-65, 4(%r15)
	jg	.LBB16_74
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.113(%rip), %rax
	jmp	.LBB16_71
.LBB16_68:
	movl	$3, %r8d
	movq	$-3, %r14
	cmpq	$3, %rsi
	je	.LBB16_74
	cmpb	$-65, 3(%r15)
	jg	.LBB16_74
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.115(%rip), %rax
.LBB16_71:
	movq	%rax, 32(%rsp)
	jmp	.LBB16_178
.LBB16_72:
	cmpb	$-65, 2(%r15)
	jle	.LBB16_176
.LBB16_73:
	movl	$2, %r8d
	movq	$-2, %r14
.LBB16_74:
	addq	%rsi, %r14
	addq	%r15, %r8
	leaq	(%r8,%r14), %r9
	xorl	%eax, %eax
.LBB16_75:
	cmpq	%rax, %r14
	je	.LBB16_77
	cmpb	$0, (%r8,%rax)
	leaq	1(%rax), %rax
	jns	.LBB16_75
	jmp	.LBB16_114
.LBB16_77:
	testq	%r14, %r14
	je	.LBB16_114
	movb	(%r8), %cl
	movzbl	%cl, %r11d
	testb	%r11b, %r11b
	js	.LBB16_80
	leaq	1(%r8), %r10
	jmp	.LBB16_85
.LBB16_80:
	movl	%r11d, %eax
	andl	$31, %eax
	movzbl	1(%r8), %edx
	andl	$63, %edx
	cmpb	$-33, %r11b
	jbe	.LBB16_83
	movzbl	2(%r8), %r11d
	shll	$6, %edx
	andl	$63, %r11d
	orl	%edx, %r11d
	cmpb	$-16, %cl
	jb	.LBB16_84
	leaq	4(%r8), %r10
	movzbl	3(%r8), %ecx
	andl	$7, %eax
	shll	$18, %eax
	shll	$6, %r11d
	andl	$63, %ecx
	orl	%r11d, %ecx
	orl	%eax, %ecx
	movl	%ecx, %r11d
	jmp	.LBB16_85
.LBB16_83:
	leaq	2(%r8), %r10
	shll	$6, %eax
	orl	%edx, %eax
	movl	%eax, %r11d
	jmp	.LBB16_85
.LBB16_84:
	leaq	3(%r8), %r10
	shll	$12, %eax
	orl	%eax, %r11d
.LBB16_85:
	xorl	%r12d, %r12d
	cmpl	$69, %r11d
	jne	.LBB16_87
.LBB16_86:
	subq	%r10, %r9
	jmp	.LBB16_151
.LBB16_87:
	movl	$10, %ebx
.LBB16_88:
	addl	$-48, %r11d
	cmpl	$9, %r11d
	ja	.LBB16_114
	xorl	%eax, %eax
.LBB16_90:
	movq	%rax, %rcx
	mulq	%rbx
	jo	.LBB16_114
	movl	%r11d, %r13d
	addq	%r13, %rax
	jb	.LBB16_114
	cmpq	%r9, %r10
	je	.LBB16_114
	movq	%r10, %rdi
	movb	(%r10), %r10b
	movzbl	%r10b, %edx
	testb	%dl, %dl
	js	.LBB16_95
	incq	%rdi
	movq	%rdi, %r10
	jmp	.LBB16_101
.LBB16_95:
	movl	%edx, %ebx
	andl	$31, %ebx
	movzbl	1(%rdi), %r11d
	andl	$63, %r11d
	cmpb	$-33, %dl
	jbe	.LBB16_98
	movzbl	2(%rdi), %edx
	shll	$6, %r11d
	andl	$63, %edx
	orl	%r11d, %edx
	cmpb	$-16, %r10b
	jb	.LBB16_99
	movzbl	3(%rdi), %r10d
	addq	$4, %rdi
	andl	$7, %ebx
	shll	$18, %ebx
	shll	$6, %edx
	andl	$63, %r10d
	orl	%edx, %r10d
	orl	%ebx, %r10d
	movl	%r10d, %edx
	jmp	.LBB16_100
.LBB16_98:
	addq	$2, %rdi
	shll	$6, %ebx
	orl	%r11d, %ebx
	movl	%ebx, %edx
	jmp	.LBB16_100
.LBB16_99:
	addq	$3, %rdi
	shll	$12, %ebx
	orl	%ebx, %edx
.LBB16_100:
	movq	%rdi, %r10
	movl	$10, %ebx
.LBB16_101:
	leal	-48(%rdx), %r11d
	cmpl	$10, %r11d
	jb	.LBB16_90
	testq	%rax, %rax
	je	.LBB16_113
	leaq	(%rcx,%rcx,4), %rax
	leaq	(,%rax,2), %rax
	addq	%r13, %rax
.LBB16_104:
	cmpq	%r9, %r10
	je	.LBB16_114
	movq	%r10, %rdi
	movb	(%r10), %r10b
	movzbl	%r10b, %edx
	testb	%dl, %dl
	js	.LBB16_107
	incq	%rdi
	jmp	.LBB16_112
.LBB16_107:
	movl	%edx, %ecx
	andl	$31, %ecx
	movzbl	1(%rdi), %r11d
	andl	$63, %r11d
	cmpb	$-33, %dl
	jbe	.LBB16_110
	movzbl	2(%rdi), %edx
	shll	$6, %r11d
	andl	$63, %edx
	orl	%r11d, %edx
	cmpb	$-16, %r10b
	jb	.LBB16_111
	movzbl	3(%rdi), %r10d
	addq	$4, %rdi
	andl	$7, %ecx
	shll	$18, %ecx
	shll	$6, %edx
	andl	$63, %r10d
	orl	%edx, %r10d
	orl	%ecx, %r10d
	movl	%r10d, %edx
	jmp	.LBB16_112
.LBB16_110:
	addq	$2, %rdi
	shll	$6, %ecx
	orl	%r11d, %ecx
	movl	%ecx, %edx
	jmp	.LBB16_112
.LBB16_111:
	addq	$3, %rdi
	shll	$12, %ecx
	orl	%ecx, %edx
.LBB16_112:
	movq	%rdi, %r10
	decq	%rax
	jne	.LBB16_104
.LBB16_113:
	incq	%r12
	movl	%edx, %r11d
	cmpl	$69, %edx
	jne	.LBB16_88
	jmp	.LBB16_86
.LBB16_114:
	cmpq	$3, %rsi
	jb	.LBB16_119
.LBB16_115:
	cmpw	$21087, (%r15)
	je	.LBB16_123
	cmpb	$82, (%r15)
	je	.LBB16_120
	movl	$1, %r10d
	cmpq	$3, %rsi
	jne	.LBB16_141
	movl	$3, %esi
	jmp	.LBB16_142
.LBB16_119:
	movl	$2, %esi
	cmpb	$82, (%r15)
	jne	.LBB16_122
.LBB16_120:
	movb	1(%r15), %al
	cmpb	$-65, %al
	jle	.LBB16_173
	leaq	1(%r15), %r14
	movq	$-1, %r12
	jmp	.LBB16_125
.LBB16_122:
	movl	$1, %r10d
	jmp	.LBB16_142
.LBB16_123:
	movb	2(%r15), %al
	cmpb	$-65, %al
	jle	.LBB16_175
	leaq	2(%r15), %r14
	movq	$-2, %r12
.LBB16_125:
	addb	$-65, %al
	movl	$1, %r10d
	cmpb	$25, %al
	ja	.LBB16_142
	addq	%rsi, %r12
	xorl	%r8d, %r8d
	xorl	%eax, %eax
.LBB16_127:
	cmpq	%rax, %r12
	je	.LBB16_130
	cmpb	$0, (%r14,%rax)
	leaq	1(%rax), %rax
	jns	.LBB16_127
	xorl	%r14d, %r14d
	jmp	.LBB16_144
.LBB16_130:
	leaq	-56(%rbp), %rcx
	movq	%r14, (%rcx)
	movq	%r12, 8(%rcx)
	xorl	%eax, %eax
	movq	%rax, 16(%rcx)
	movl	%eax, 24(%rcx)
	movq	%rax, 32(%rcx)
	movl	%eax, 40(%rcx)
	xorl	%edx, %edx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_path
	testb	%al, %al
	jne	.LBB16_171
	movq	-56(%rbp), %rcx
	testq	%rcx, %rcx
	movl	$1, %r10d
	je	.LBB16_142
	movzbl	-48(%rbp), %eax
	movzbl	-41(%rbp), %edx
	shll	$16, %edx
	movzwl	-43(%rbp), %r8d
	orl	%edx, %r8d
	shlq	$32, %r8
	movl	-47(%rbp), %r9d
	orq	%r8, %r9
	movq	-40(%rbp), %r8
	shlq	$8, %r9
	orq	%rax, %r9
	cmpq	%r9, %r8
	jae	.LBB16_137
	movb	(%rcx,%r8), %al
	addb	$-65, %al
	cmpb	$26, %al
	jae	.LBB16_137
	leaq	-56(%rbp), %rax
	movsd	24(%rax), %xmm0
	movq	%rcx, (%rax)
	movq	%r9, 8(%rax)
	movq	%r8, 16(%rax)
	movlps	%xmm0, 24(%rax)
	movq	$0, 32(%rax)
	movl	$0, 40(%rax)
	movq	%rax, %rcx
	xorl	%edx, %edx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_path
	testb	%al, %al
	jne	.LBB16_171
	movq	-56(%rbp), %rcx
	testq	%rcx, %rcx
	movl	$1, %r10d
	je	.LBB16_142
	movq	-48(%rbp), %r9
	movq	-40(%rbp), %r8
.LBB16_137:
	testq	%r8, %r8
	je	.LBB16_150
	cmpq	%r8, %r9
	jbe	.LBB16_149
	cmpb	$-65, (%rcx,%r8)
	jg	.LBB16_150
.LBB16_140:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.107(%rip), %rax
	movq	%rax, 32(%rsp)
	movq	%r9, %rdx
	jmp	.LBB16_179
.LBB16_141:
	movzwl	(%r15), %eax
	xorl	$24415, %eax
	movzbl	2(%r15), %ecx
	xorl	$82, %ecx
	orw	%ax, %cx
	je	.LBB16_147
.LBB16_142:
	xorl	%r14d, %r14d
.LBB16_143:
	xorl	%r8d, %r8d
.LBB16_144:
	xorl	%ebx, %ebx
.LBB16_145:
	xorl	%r9d, %r9d
.LBB16_146:
	movq	48(%rbp), %rax
	movq	%rbx, (%rax)
	movq	%r8, 8(%rax)
	movq	%r14, 16(%rax)
	movq	%r12, 24(%rax)
	movq	%r15, 32(%rax)
	movq	%rsi, 40(%rax)
	movq	%r10, 48(%rax)
	movq	%r9, 56(%rax)
	.seh_startepilogue
	addq	$216, %rsp
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
.LBB16_147:
	movb	3(%r15), %al
	cmpb	$-65, %al
	jle	.LBB16_180
	leaq	3(%r15), %r14
	movq	$-3, %r12
	jmp	.LBB16_125
.LBB16_149:
	jne	.LBB16_140
.LBB16_150:
	addq	%r8, %rcx
	subq	%r8, %r9
	xorl	%r8d, %r8d
	movq	%rcx, %r10
.LBB16_151:
	testq	%r9, %r9
	je	.LBB16_168
	cmpb	$46, (%r10)
	jne	.LBB16_169
	movq	%r15, 72(%rbp)
	leaq	(%r10,%r9), %rcx
	movb	$46, %r13b
	xorl	%ebx, %ebx
	movq	%r10, %rax
.LBB16_154:
	movq	%rsi, %r15
	testb	%r13b, %r13b
	js	.LBB16_156
	incq	%r10
	movzbl	%r13b, %r11d
	jmp	.LBB16_161
.LBB16_156:
	movl	%r13d, %edx
	andb	$31, %dl
	movzbl	%dl, %r11d
	movzbl	1(%r10), %esi
	andl	$63, %esi
	cmpb	$-33, %r13b
	jbe	.LBB16_159
	movzbl	2(%r10), %edx
	shll	$6, %esi
	andl	$63, %edx
	orl	%esi, %edx
	cmpb	$-16, %r13b
	jb	.LBB16_160
	movzbl	3(%r10), %esi
	addq	$4, %r10
	andl	$7, %r11d
	shll	$18, %r11d
	shll	$6, %edx
	andl	$63, %esi
	orl	%edx, %esi
	orl	%r11d, %esi
	movl	%esi, %r11d
	jmp	.LBB16_161
.LBB16_159:
	addq	$2, %r10
	shll	$6, %r11d
	orl	%esi, %r11d
	jmp	.LBB16_161
.LBB16_160:
	addq	$3, %r10
	shll	$12, %r11d
	orl	%r11d, %edx
	movl	%edx, %r11d
.LBB16_161:
	movl	%r11d, %edx
	andl	$2097119, %edx
	addl	$-65, %edx
	cmpl	$26, %edx
	setb	%dl
	leal	-48(%r11), %esi
	cmpl	$10, %esi
	setb	%sil
	leal	-33(%r11), %edi
	cmpl	$15, %edi
	setb	%dil
	orb	%sil, %dil
	orb	%dl, %dil
	jne	.LBB16_164
	leal	-58(%r11), %edx
	cmpl	$38, %edx
	ja	.LBB16_166
	movabsq	$541165879423, %rsi
	btq	%rdx, %rsi
	jae	.LBB16_166
.LBB16_164:
	cmpq	%rcx, %r10
	movq	%r15, %rsi
	je	.LBB16_170
	movb	(%r10), %r13b
	jmp	.LBB16_154
.LBB16_166:
	addl	$-127, %r11d
	cmpl	$-4, %r11d
	jae	.LBB16_164
	xorl	%r9d, %r9d
	movl	$1, %r10d
	movq	%r15, %rsi
	movq	72(%rbp), %r15
	jmp	.LBB16_146
.LBB16_168:
	movl	$1, %ebx
	jmp	.LBB16_145
.LBB16_169:
	xorl	%ebx, %ebx
	xorl	%r9d, %r9d
	movl	$1, %r10d
	jmp	.LBB16_146
.LBB16_170:
	movl	$1, %ebx
	movq	72(%rbp), %r15
	movq	%rax, %r10
	jmp	.LBB16_146
.LBB16_171:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.106(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.3(%rip), %rcx
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.40(%rip), %r9
	leaq	87(%rbp), %r8
	movl	$61, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core6result13unwrap_failed
	ud2
.LBB16_172:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.11(%rip), %r8
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	ud2
.LBB16_173:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.104(%rip), %rax
	movq	%rax, 32(%rsp)
	movl	$1, %r8d
	jmp	.LBB16_178
.LBB16_174:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.35(%rip), %rax
	movq	%rax, 32(%rsp)
	movq	%r15, %rcx
	movq	%rsi, %rdx
	xorl	%r8d, %r8d
	movq	%rdi, %r9
	jmp	.LBB16_179
.LBB16_175:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.105(%rip), %rax
	jmp	.LBB16_177
.LBB16_176:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.114(%rip), %rax
.LBB16_177:
	movq	%rax, 32(%rsp)
	movl	$2, %r8d
.LBB16_178:
	movq	%r15, %rcx
	movq	%rsi, %rdx
	movq	%rsi, %r9
.LBB16_179:
	callq	_RNvNtCs8xEFJqa6dYS_4core3str16slice_error_fail
	ud2
.LBB16_180:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.103(%rip), %rax
	movq	%rax, 32(%rsp)
	movl	$3, %r8d
	jmp	.LBB16_178
.Lfunc_end16:
	.seh_endproc

	.def	_RNvMNtNtCs8xEFJqa6dYS_4core4char7methodsc11is_assigned;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMNtNtCs8xEFJqa6dYS_4core4char7methodsc11is_assigned,unique,17
_RNvMNtNtCs8xEFJqa6dYS_4core4char7methodsc11is_assigned:
.Lfunc_begin17:
.seh_proc _RNvMNtNtCs8xEFJqa6dYS_4core4char7methodsc11is_assigned
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	32(%rsp), %rbp
	.seh_setframe %rbp, 32
	.seh_endprologue
	movb	$1, %al
	cmpl	$888, %ecx
	jb	.LBB17_4
	cmpl	$262142, %ecx
	jae	.LBB17_2
	callq	_RNvNtNtNtCs8xEFJqa6dYS_4core7unicode12unicode_data13cn_planes_0_311lookup_slow
	xorb	$1, %al
	jmp	.LBB17_4
.LBB17_2:
	cmpl	$917505, %ecx
	sete	%dl
	leal	-917536(%rcx), %r8d
	cmpl	$96, %r8d
	setb	%r8b
	leal	-917760(%rcx), %r9d
	cmpl	$240, %r9d
	setb	%r9b
	orb	%r8b, %r9b
	leal	-983040(%rcx), %r8d
	cmpl	$65534, %r8d
	setb	%r8b
	orb	%dl, %r8b
	orb	%r9b, %r8b
	jne	.LBB17_4
	addl	$-1048576, %ecx
	cmpl	$65534, %ecx
	setb	%al
.LBB17_4:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end17:
	.seh_endproc

	.def	_RNvMNtNtCs8xEFJqa6dYS_4core4char7methodsc16escape_debug_ext;
	.scl	3;
	.type	32;
	.endef
	.globl	__xmm@fff10000ffff2000ffffff8100000000
	.section	.rdata,"dr",discard,__xmm@fff10000ffff2000ffffff8100000000
	.p2align	4, 0x0
__xmm@fff10000ffff2000ffffff8100000000:
	.long	0
	.long	4294967169
	.long	4294909952
	.long	4293984256
	.globl	__xmm@80000000800000008000000080000000
	.section	.rdata,"dr",discard,__xmm@80000000800000008000000080000000
	.p2align	4, 0x0
__xmm@80000000800000008000000080000000:
	.long	2147483648
	.long	2147483648
	.long	2147483648
	.long	2147483648
	.globl	__xmm@8000fffd800018ff800000208000001f
	.section	.rdata,"dr",discard,__xmm@8000fffd800018ff800000208000001f
	.p2align	4, 0x0
__xmm@8000fffd800018ff800000208000001f:
	.long	2147483679
	.long	2147483680
	.long	2147490047
	.long	2147549181
	.section	.text,"xr",one_only,_RNvMNtNtCs8xEFJqa6dYS_4core4char7methodsc16escape_debug_ext,unique,18
_RNvMNtNtCs8xEFJqa6dYS_4core4char7methodsc16escape_debug_ext:
.Lfunc_begin18:
.seh_proc _RNvMNtNtCs8xEFJqa6dYS_4core4char7methodsc16escape_debug_ext
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$48, %rsp
	.seh_stackalloc 48
	leaq	48(%rsp), %rbp
	.seh_setframe %rbp, 48
	.seh_endprologue
	movl	%edx, %edi
	movq	%rcx, %rsi
	cmpl	$12, %edx
	jle	.LBB18_1
	cmpl	$38, %edi
	jg	.LBB18_9
	cmpl	$13, %edi
	je	.LBB18_22
	cmpl	$34, %edi
	jne	.LBB18_11
	movw	$8796, (%rsi)
	jmp	.LBB18_24
.LBB18_1:
	testl	%edi, %edi
	je	.LBB18_23
	cmpl	$9, %edi
	je	.LBB18_21
	cmpl	$10, %edi
	jne	.LBB18_11
	movw	$28252, (%rsi)
	jmp	.LBB18_24
.LBB18_9:
	cmpl	$39, %edi
	je	.LBB18_26
	cmpl	$92, %edi
	jne	.LBB18_11
	movw	$23644, (%rsi)
	jmp	.LBB18_24
.LBB18_23:
	movw	$12380, (%rsi)
	jmp	.LBB18_24
.LBB18_11:
	leal	-32(%rdi), %eax
	cmpl	$95, %eax
	jae	.LBB18_12
.LBB18_19:
	movl	%edi, (%rsi)
	movb	$-127, %cl
	movb	$-128, %al
	jmp	.LBB18_25
.LBB18_22:
	movw	$29276, (%rsi)
	jmp	.LBB18_24
.LBB18_26:
	movw	$10076, (%rsi)
	jmp	.LBB18_24
.LBB18_21:
	movw	$29788, (%rsi)
.LBB18_24:
	movq	$0, 2(%rsi)
	movb	$2, %cl
	xorl	%eax, %eax
.LBB18_25:
	movb	%al, 12(%rsi)
	movb	%cl, 13(%rsi)
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB18_12:
	movd	%edi, %xmm0
	pshufd	$0, %xmm0, %xmm0
	paddd	__xmm@fff10000ffff2000ffffff8100000000(%rip), %xmm0
	pxor	__xmm@80000000800000008000000080000000(%rip), %xmm0
	pcmpgtd	__xmm@8000fffd800018ff800000208000001f(%rip), %xmm0
	movmskps	%xmm0, %eax
	cmpl	$15, %eax
	jne	.LBB18_30
	leal	-1048576(%rdi), %eax
	cmpl	$65534, %eax
	setb	%al
	cmpl	$32, %edi
	sete	%cl
	orb	%al, %cl
	jne	.LBB18_30
	cmpl	$133, %edi
	jae	.LBB18_15
.LBB18_18:
	movl	%edi, %ecx
	callq	_RNvMNtNtCs8xEFJqa6dYS_4core4char7methodsc11is_assigned
	testb	%al, %al
	jne	.LBB18_19
	jmp	.LBB18_30
.LBB18_15:
	movl	%edi, %ecx
	callq	_RNvNtNtNtCs8xEFJqa6dYS_4core7unicode12unicode_data11white_space6lookup
	testb	%al, %al
	je	.LBB18_16
.LBB18_30:
	movl	%edi, %eax
	orl	$1, %eax
	bsrl	%eax, %ecx
	xorl	$28, %ecx
	shrl	$2, %ecx
	leaq	-2(%rcx), %rax
	movb	$0, -8(%rbp)
	movw	$0, -10(%rbp)
	movl	%edi, %r8d
	shrl	$20, %r8d
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.12(%rip), %rdx
	movb	(%r8,%rdx), %r8b
	movb	%r8b, -7(%rbp)
	movl	%edi, %r8d
	shrl	$16, %r8d
	andl	$15, %r8d
	movb	(%r8,%rdx), %r8b
	movb	%r8b, -6(%rbp)
	movl	%edi, %r8d
	shrl	$12, %r8d
	andl	$15, %r8d
	movb	(%r8,%rdx), %r8b
	movb	%r8b, -5(%rbp)
	movl	%edi, %r8d
	shrl	$8, %r8d
	andl	$15, %r8d
	movb	(%r8,%rdx), %r8b
	movb	%r8b, -4(%rbp)
	movl	%edi, %r8d
	shrl	$4, %r8d
	andl	$15, %r8d
	movb	(%r8,%rdx), %r8b
	movb	%r8b, -3(%rbp)
	andl	$15, %edi
	movb	(%rdi,%rdx), %dl
	movb	%dl, -2(%rbp)
	movb	$125, -1(%rbp)
	movw	$30044, -12(%rbp,%rcx)
	movb	$123, -10(%rbp,%rcx)
	movzwl	-2(%rbp), %ecx
	movw	%cx, 8(%rsi)
	movq	-10(%rbp), %rcx
	movq	%rcx, (%rsi)
	movb	$10, %cl
	jmp	.LBB18_25
.LBB18_16:
	cmpl	$767, %edi
	jbe	.LBB18_17
	movl	%edi, %ecx
	callq	_RNvNtNtNtCs8xEFJqa6dYS_4core7unicode12unicode_data15grapheme_extend11lookup_slow
	testb	%al, %al
	jne	.LBB18_30
	jmp	.LBB18_28
.LBB18_17:
	cmpl	$172, %edi
	jbe	.LBB18_18
.LBB18_28:
	movl	%edi, %ecx
	callq	_RNvNtNtNtCs8xEFJqa6dYS_4core7unicode12unicode_data28default_ignorable_code_point11lookup_slow
	testb	%al, %al
	jne	.LBB18_30
	movl	%edi, %ecx
	callq	_RNvNtNtNtCs8xEFJqa6dYS_4core7unicode12unicode_data2cf11lookup_slow
	testb	%al, %al
	je	.LBB18_18
	jmp	.LBB18_30
.Lfunc_end18:
	.seh_endproc

	.def	_RNvMs1_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_10HexNibbles14try_parse_uint;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs1_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_10HexNibbles14try_parse_uint,unique,19
_RNvMs1_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_10HexNibbles14try_parse_uint:
.Lfunc_begin19:
.seh_proc _RNvMs1_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_10HexNibbles14try_parse_uint
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	32(%rsp), %rbp
	.seh_setframe %rbp, 32
	.seh_endprologue
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.41(%rip), %r8
	movl	$1, %esi
	movl	$1, %r9d
	callq	_RINvMNtCs8xEFJqa6dYS_4core3stre18trim_start_matchesReECseL4M8JimfzJ_14rustc_demangle
	cmpq	$16, %rdx
	jbe	.LBB19_3
	xorl	%esi, %esi
	jmp	.LBB19_2
.LBB19_3:
	movq	%rdx, %rcx
	testq	%rdx, %rdx
	je	.LBB19_4
	addq	%rax, %rcx
	xorl	%edx, %edx
.LBB19_6:
	movzbl	(%rax), %r8d
	testb	%r8b, %r8b
	js	.LBB19_8
	incq	%rax
	jmp	.LBB19_13
.LBB19_8:
	movl	%r8d, %r9d
	andl	$31, %r9d
	movzbl	1(%rax), %r11d
	andl	$63, %r11d
	cmpb	$-33, %r8b
	jbe	.LBB19_9
	movzbl	2(%rax), %r10d
	shll	$6, %r11d
	andl	$63, %r10d
	orl	%r11d, %r10d
	cmpb	$-16, %r8b
	jb	.LBB19_11
	movzbl	3(%rax), %r8d
	addq	$4, %rax
	andl	$7, %r9d
	shll	$18, %r9d
	shll	$6, %r10d
	andl	$63, %r8d
	orl	%r10d, %r8d
	orl	%r9d, %r8d
	jmp	.LBB19_13
.LBB19_9:
	addq	$2, %rax
	shll	$6, %r9d
	orl	%r11d, %r9d
	movl	%r9d, %r8d
	jmp	.LBB19_13
.LBB19_11:
	addq	$3, %rax
	shll	$12, %r9d
	orl	%r9d, %r10d
	movl	%r10d, %r8d
.LBB19_13:
	leal	-65(%r8), %r10d
	andl	$-33, %r10d
	addl	$10, %r10d
	leal	-48(%r8), %r9d
	cmpl	$58, %r8d
	cmovael	%r10d, %r9d
	cmpl	$16, %r9d
	jae	.LBB19_15
	movq	%rdx, %r8
	shlq	$4, %r8
	movl	%r9d, %edx
	orq	%r8, %rdx
	cmpq	%rcx, %rax
	je	.LBB19_2
	jmp	.LBB19_6
.LBB19_4:
	xorl	%edx, %edx
.LBB19_2:
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB19_15:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.42(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end19:
	.seh_endproc

	.def	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser10integer_62;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser10integer_62,unique,20
_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser10integer_62:
.Lfunc_begin20:
.seh_proc _RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser10integer_62
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	.seh_endprologue
	movq	%rdx, %r8
	movq	(%rdx), %r10
	movq	8(%rdx), %r11
	movq	16(%rdx), %r9
	cmpq	%r11, %r9
	jae	.LBB20_1
	cmpb	$95, (%r10,%r9)
	jne	.LBB20_1
	incq	%r9
	movq	%r9, 16(%r8)
	movq	$0, 8(%rcx)
	jmp	.LBB20_10
.LBB20_1:
	xorl	%eax, %eax
	movl	$62, %esi
.LBB20_2:
	cmpq	%r11, %r9
	jae	.LBB20_18
	movb	(%r10,%r9), %dl
	cmpb	$95, %dl
	je	.LBB20_12
	leal	-48(%rdx), %edi
	cmpb	$10, %dil
	jb	.LBB20_16
	leal	-97(%rdx), %edi
	cmpb	$26, %dil
	jae	.LBB20_6
	addb	$-87, %dl
	jmp	.LBB20_15
.LBB20_6:
	leal	-65(%rdx), %edi
	cmpb	$26, %dil
	jae	.LBB20_18
	addb	$-29, %dl
.LBB20_15:
	movl	%edx, %edi
.LBB20_16:
	incq	%r9
	movq	%r9, 16(%r8)
	mulq	%rsi
	jo	.LBB20_18
	movzbl	%dil, %edx
	addq	%rdx, %rax
	jae	.LBB20_2
.LBB20_18:
	movb	$0, 1(%rcx)
	movb	$1, %al
	jmp	.LBB20_11
.LBB20_12:
	incq	%r9
	movq	%r9, 16(%r8)
	cmpq	$-1, %rax
	je	.LBB20_18
	incq	%rax
	movq	%rax, 8(%rcx)
.LBB20_10:
	xorl	%eax, %eax
.LBB20_11:
	movb	%al, (%rcx)
	.seh_startepilogue
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end20:
	.seh_endproc

	.def	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser11hex_nibbles;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser11hex_nibbles,unique,21
_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser11hex_nibbles:
.Lfunc_begin21:
.seh_proc _RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser11hex_nibbles
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
	leaq	32(%rsp), %rbp
	.seh_setframe %rbp, 32
	.seh_endprologue
	movq	%rdx, %r10
	movq	16(%rdx), %r8
	movq	(%rdx), %rax
	movq	8(%rdx), %rdx
	movq	$-1, %r11
	movq	%r8, %r9
.LBB21_1:
	cmpq	%rdx, %r9
	jae	.LBB21_9
	movb	(%rax,%r9), %sil
	incq	%r9
	movq	%r9, 16(%r10)
	leal	-48(%rsi), %edi
	cmpb	$10, %dil
	setb	%bl
	leal	-97(%rsi), %edi
	cmpb	$6, %dil
	setb	%dil
	orb	%bl, %dil
	incq	%r11
	testb	%dil, %dil
	jne	.LBB21_1
	cmpb	$95, %sil
	jne	.LBB21_9
	decq	%r9
	cmpq	%r9, %r8
	ja	.LBB21_10
	testq	%r8, %r8
	je	.LBB21_7
	cmpb	$-64, (%rax,%r8)
	jl	.LBB21_10
.LBB21_7:
	addq	%r8, %rax
	movq	%rax, (%rcx)
	movq	%r11, 8(%rcx)
	jmp	.LBB21_8
.LBB21_9:
	movb	$0, 8(%rcx)
	movq	$0, (%rcx)
.LBB21_8:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB21_10:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.43(%rip), %rcx
	movq	%rcx, 32(%rsp)
	movq	%rax, %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core3str16slice_error_fail
	ud2
.Lfunc_end21:
	.seh_endproc

	.def	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser14opt_integer_62;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser14opt_integer_62,unique,22
_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser14opt_integer_62:
.Lfunc_begin22:
.seh_proc _RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser14opt_integer_62
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$48, %rsp
	.seh_stackalloc 48
	leaq	48(%rsp), %rbp
	.seh_setframe %rbp, 48
	.seh_endprologue
	movq	%rcx, %rsi
	movq	16(%rdx), %rax
	cmpq	8(%rdx), %rax
	jae	.LBB22_4
	movq	(%rdx), %rcx
	cmpb	%r8b, (%rcx,%rax)
	jne	.LBB22_4
	incq	%rax
	movq	%rax, 16(%rdx)
	leaq	-16(%rbp), %rdi
	movq	%rdi, %rcx
	callq	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser10integer_62
	cmpb	$0, (%rdi)
	je	.LBB22_7
	movb	-15(%rbp), %al
	movb	%al, 1(%rsi)
.LBB22_10:
	movb	$1, %al
	jmp	.LBB22_6
.LBB22_4:
	movq	$0, 8(%rsi)
.LBB22_5:
	xorl	%eax, %eax
.LBB22_6:
	movb	%al, (%rsi)
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB22_7:
	movq	-8(%rbp), %rax
	cmpq	$-1, %rax
	je	.LBB22_9
	incq	%rax
	movq	%rax, 8(%rsi)
	jmp	.LBB22_5
.LBB22_9:
	movb	$0, 1(%rsi)
	jmp	.LBB22_10
.Lfunc_end22:
	.seh_endproc

	.def	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser5ident;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser5ident,unique,23
_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser5ident:
.Lfunc_begin23:
.seh_proc _RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser5ident
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
	leaq	32(%rsp), %rbp
	.seh_setframe %rbp, 32
	.seh_endprologue
	movq	%rdx, %r11
	movq	8(%rdx), %rsi
	movq	16(%rdx), %r8
	cmpq	%rsi, %r8
	jae	.LBB23_3
	movq	(%r11), %rax
	cmpb	$117, (%rax,%r8)
	jne	.LBB23_3
	incq	%r8
	movq	%r8, 16(%r11)
	movb	$1, %dil
	jmp	.LBB23_4
.LBB23_3:
	xorl	%edi, %edi
.LBB23_4:
	cmpq	%rsi, %r8
	jae	.LBB23_19
	movq	(%r11), %r10
	movb	(%r10,%r8), %al
	addb	$-48, %al
	cmpb	$10, %al
	jae	.LBB23_19
	incq	%r8
	movq	%r8, 16(%r11)
	testb	%al, %al
	je	.LBB23_12
	movzbl	%al, %eax
	movl	$10, %r9d
.LBB23_8:
	cmpq	%r8, %rsi
	je	.LBB23_16
	movb	(%r10,%r8), %bl
	addb	$-48, %bl
	cmpb	$9, %bl
	ja	.LBB23_13
	incq	%r8
	movq	%r8, 16(%r11)
	mulq	%r9
	jo	.LBB23_19
	movzbl	%bl, %edx
	addq	%rdx, %rax
	jb	.LBB23_19
	jmp	.LBB23_8
.LBB23_12:
	xorl	%eax, %eax
.LBB23_13:
	cmpq	%rsi, %r8
	jae	.LBB23_17
	cmpb	$95, (%r10,%r8)
	jne	.LBB23_17
	incq	%r8
	movq	%r8, 16(%r11)
	jmp	.LBB23_17
.LBB23_16:
	movq	%rsi, %r8
.LBB23_17:
	movq	%r8, %r9
	addq	%rax, %r9
	jb	.LBB23_19
	movq	%r9, 16(%r11)
	cmpq	%rsi, %r9
	jbe	.LBB23_21
.LBB23_19:
	movb	$0, 8(%rcx)
	movq	$0, (%rcx)
.LBB23_20:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB23_21:
	cmpq	%rsi, %r8
	je	.LBB23_25
	cmpb	$-65, (%r10,%r8)
	jle	.LBB23_45
	cmpq	%rsi, %r9
	je	.LBB23_25
	cmpb	$-65, (%r10,%r9)
	jle	.LBB23_45
.LBB23_25:
	addq	%r8, %r10
	testb	%dil, %dil
	je	.LBB23_32
	leaq	(%r10,%rax), %rdx
	xorl	%r9d, %r9d
	xorl	%r8d, %r8d
.LBB23_27:
	movq	%rax, %r11
	addq	%r8, %r11
	je	.LBB23_33
	leaq	-1(%r8), %r11
	cmpb	$95, -1(%rdx,%r8)
	movq	%r11, %r8
	jne	.LBB23_27
	movq	%rax, %r9
	leaq	(%rax,%r11), %r8
	incq	%r8
	addq	%r11, %r9
	je	.LBB23_36
	cmpq	%rax, %r9
	jae	.LBB23_34
	cmpb	$-65, (%rdx,%r11)
	jg	.LBB23_36
	jmp	.LBB23_47
.LBB23_32:
	movq	%r10, (%rcx)
	movq	%rax, 8(%rcx)
	movq	$1, 16(%rcx)
	movq	$0, 24(%rcx)
	jmp	.LBB23_20
.LBB23_33:
	movl	$1, %edx
	jmp	.LBB23_43
.LBB23_34:
	testq	%r11, %r11
	jne	.LBB23_47
	testq	%r8, %r8
	je	.LBB23_41
.LBB23_36:
	cmpq	%rax, %r8
	jae	.LBB23_39
	cmpb	$-64, 1(%rdx,%r11)
	jl	.LBB23_40
	movq	%r8, %rsi
	jmp	.LBB23_42
.LBB23_39:
	movq	%rax, %rsi
	cmpq	$-1, %r11
	je	.LBB23_42
.LBB23_40:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.46(%rip), %rcx
	movq	%rcx, 32(%rsp)
	movq	%r10, %rcx
	movq	%rax, %rdx
	movq	%rax, %r9
	jmp	.LBB23_46
.LBB23_41:
	xorl	%esi, %esi
.LBB23_42:
	subq	%rsi, %rax
	addq	%r10, %rsi
	movq	%r10, %rdx
	movq	%rsi, %r10
.LBB23_43:
	testq	%rax, %rax
	je	.LBB23_19
	movq	%rdx, (%rcx)
	movq	%r9, 8(%rcx)
	movq	%r10, 16(%rcx)
	movq	%rax, 24(%rcx)
	jmp	.LBB23_20
.LBB23_45:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.44(%rip), %rax
	movq	%rax, 32(%rsp)
	movq	%r10, %rcx
	movq	%rsi, %rdx
.LBB23_46:
	callq	_RNvNtCs8xEFJqa6dYS_4core3str16slice_error_fail
	ud2
.LBB23_47:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.45(%rip), %rcx
	movq	%rcx, 32(%rsp)
	movq	%r10, %rcx
	movq	%rax, %rdx
	xorl	%r8d, %r8d
	jmp	.LBB23_46
.Lfunc_end23:
	.seh_endproc

	.def	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser7backref;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser7backref,unique,24
_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser7backref:
.Lfunc_begin24:
.seh_proc _RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser7backref
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
	subq	$48, %rsp
	.seh_stackalloc 48
	leaq	48(%rsp), %rbp
	.seh_setframe %rbp, 48
	.seh_endprologue
	movq	%rdx, %rdi
	movq	%rcx, %rsi
	movq	16(%rdx), %r14
	leaq	-16(%rbp), %rbx
	movq	%rbx, %rcx
	callq	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser10integer_62
	cmpb	$1, (%rbx)
	jne	.LBB24_2
	movb	-15(%rbp), %al
	movb	%al, 8(%rsi)
	jmp	.LBB24_6
.LBB24_2:
	decq	%r14
	movq	-8(%rbp), %rax
	cmpq	%r14, %rax
	jae	.LBB24_8
	movl	24(%rdi), %ecx
	incl	%ecx
	cmpl	$500, %ecx
	jbe	.LBB24_4
	movb	$1, 8(%rsi)
	jmp	.LBB24_6
.LBB24_8:
	movb	$0, 8(%rsi)
.LBB24_6:
	movq	$0, (%rsi)
.LBB24_7:
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.LBB24_4:
	movups	(%rdi), %xmm0
	movups	%xmm0, (%rsi)
	movq	%rax, 16(%rsi)
	movl	%ecx, 24(%rsi)
	jmp	.LBB24_7
.Lfunc_end24:
	.seh_endproc

	.def	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_path;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_path,unique,25
_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_path:
.Lfunc_begin25:
.seh_proc _RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_path
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
	subq	$152, %rsp
	.seh_stackalloc 152
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	movq	%rcx, %rsi
	movq	(%rcx), %rax
	testq	%rax, %rax
	je	.LBB25_1
	movl	24(%rsi), %ecx
	incl	%ecx
	movl	%ecx, 24(%rsi)
	cmpl	$501, %ecx
	jb	.LBB25_7
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB25_6
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.1(%rip), %rdx
	movl	$25, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB25_109
.LBB25_6:
	movq	$0, (%rsi)
	movb	$1, 8(%rsi)
	jmp	.LBB25_36
.LBB25_7:
	movl	%edx, %ebx
	movq	8(%rsi), %rdx
	movq	16(%rsi), %rcx
	cmpq	%rdx, %rcx
	jae	.LBB25_8
	movb	(%rax,%rcx), %r14b
	leaq	1(%rcx), %r9
	movq	%r9, 16(%rsi)
	movzbl	%r14b, %r8d
	cmpl	$76, %r8d
	jle	.LBB25_12
	cmpl	$87, %r8d
	jg	.LBB25_28
	cmpl	$77, %r8d
	je	.LBB25_96
	cmpl	$78, %r8d
	jne	.LBB25_8
	movl	$1, %r15d
	cmpq	%rdx, %r9
	jae	.LBB25_25
	movzbl	1(%rax,%rcx), %r8d
	addq	$2, %rcx
	movq	%rcx, 16(%rsi)
	leal	-65(%r8), %eax
	leal	-123(%r8), %ecx
	cmpb	$-26, %cl
	movl	$1, %ecx
	movabsq	$-4294967296, %rdx
	cmovbq	%rcx, %rdx
	shlq	$32, %r8
	cmpb	$26, %al
	cmovaeq	%rdx, %r8
	movq	%r8, %r15
	cmpb	$1, %r8b
	jne	.LBB25_55
.LBB25_25:
	andl	$256, %r15d
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	movq	%r15, %rbx
	je	.LBB25_27
	xorl	%eax, %eax
	testq	%rbx, %rbx
	setne	%al
	leaq	16(%rax,%rax,8), %r8
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rax
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.1(%rip), %rdx
	cmoveq	%rax, %rdx
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB25_109
.LBB25_27:
	movq	$0, (%rsi)
	movb	%bh, 8(%rsi)
	jmp	.LBB25_36
.LBB25_12:
	cmpl	$66, %r8d
	je	.LBB25_30
	cmpl	$67, %r8d
	je	.LBB25_31
	cmpl	$73, %r8d
	jne	.LBB25_8
	movq	%rsi, %rcx
	movl	%ebx, %edx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_path
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB25_109
	testb	%bl, %bl
	je	.LBB25_17
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB25_17
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.49(%rip), %rdx
	movl	$2, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB25_109
.LBB25_17:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB25_19
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.55(%rip), %rdx
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB25_109
.LBB25_19:
	movq	%rsi, %rcx
	callq	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNvB2_17print_generic_argEB8_
	testq	%rax, %rax
	je	.LBB25_102
	jmp	.LBB25_109
.LBB25_28:
	cmpl	$88, %r8d
	je	.LBB25_96
	cmpl	$89, %r8d
	je	.LBB25_98
.LBB25_8:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB25_10
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	movl	$16, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB25_109
.LBB25_10:
	movq	$0, (%rsi)
	movb	$0, 8(%rsi)
	jmp	.LBB25_36
.LBB25_96:
	leaq	-8(%rbp), %rdi
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	movb	$115, %r8b
	callq	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser14opt_integer_62
	cmpb	$1, (%rdi)
	jne	.LBB25_97
.LBB25_61:
	movb	-7(%rbp), %bl
.LBB25_40:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB25_43
	movzbl	%bl, %eax
	leaq	(%rax,%rax,8), %r8
	addq	$16, %r8
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.1(%rip), %r9
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	testb	%al, %al
	cmovneq	%r9, %rdx
	jmp	.LBB25_42
.LBB25_30:
	movq	%rsi, %rcx
	movl	%ebx, %edx
	callq	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer13print_backrefNCNvB2_10print_paths_0EB8_
	movb	$1, %dil
	jmp	.LBB25_76
.LBB25_97:
	movq	%rsi, %rcx
	callq	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer17skipping_printingNCNvB2_10print_path0EB8_
.LBB25_98:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB25_100
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.55(%rip), %rdx
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB25_109
.LBB25_100:
	movq	%rsi, %rcx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_type
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB25_109
	cmpb	$77, %r14b
	je	.LBB25_102
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB25_106
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.56(%rip), %rdx
	movl	$4, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB25_109
.LBB25_106:
	movq	%rsi, %rcx
	xorl	%edx, %edx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_path
	testb	%al, %al
	jne	.LBB25_109
.LBB25_102:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB25_53
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.57(%rip), %rdx
.LBB25_90:
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
.LBB25_76:
	testb	%al, %al
	jne	.LBB25_109
.LBB25_53:
	cmpq	$0, (%rsi)
	je	.LBB25_36
	decl	24(%rsi)
	jmp	.LBB25_36
.LBB25_31:
	leaq	-8(%rbp), %rdi
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	movb	$115, %r8b
	callq	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser14opt_integer_62
	cmpb	$1, (%rdi)
	jne	.LBB25_34
	movb	-7(%rbp), %bl
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB25_43
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.1(%rip), %rax
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	testb	%bl, %bl
	cmovneq	%rax, %rdx
	movzbl	%bl, %eax
	leaq	(%rax,%rax,8), %r8
	addq	$16, %r8
.LBB25_42:
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB25_109
.LBB25_43:
	movq	$0, (%rsi)
	movb	%bl, 8(%rsi)
	jmp	.LBB25_36
.LBB25_34:
	movq	(%rbp), %rbx
	movq	%rbx, -56(%rbp)
	cmpq	$0, (%rsi)
	je	.LBB25_35
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	callq	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser5ident
	cmpq	$0, (%rdi)
	je	.LBB25_39
	movups	-8(%rbp), %xmm0
	movups	8(%rbp), %xmm1
	movaps	%xmm1, -80(%rbp)
	movaps	%xmm0, -96(%rbp)
	movq	32(%rsi), %rdx
	testq	%rdx, %rdx
	je	.LBB25_53
	leaq	-96(%rbp), %rcx
	callq	_RNvXs0_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_5IdentNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB25_109
	movq	32(%rsi), %rax
	testq	%rax, %rax
	je	.LBB25_53
	testq	%rbx, %rbx
	je	.LBB25_53
	movl	$8388608, %ecx
	andl	16(%rax), %ecx
	jne	.LBB25_53
	movq	(%rax), %rcx
	movq	8(%rax), %rax
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.47(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	testb	%al, %al
	jne	.LBB25_52
	movq	32(%rsi), %rdx
	leaq	-56(%rbp), %rcx
	callq	_RNvXsC_NtNtCs8xEFJqa6dYS_4core3fmt3numyNtB7_8LowerHex3fmt
	testb	%al, %al
	jne	.LBB25_52
	movq	32(%rsi), %rax
	movq	(%rax), %rcx
	movq	8(%rax), %rax
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.48(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB25_53
.LBB25_52:
	movb	$1, %dil
	jmp	.LBB25_109
.LBB25_55:
	movq	%rsi, %rcx
	movl	%ebx, %edx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_path
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB25_109
	cmpq	$0, (%rsi)
	je	.LBB25_57
.LBB25_60:
	leaq	-8(%rbp), %rbx
	movq	%rbx, %rcx
	movq	%rsi, %rdx
	movb	$115, %r8b
	callq	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser14opt_integer_62
	cmpb	$1, (%rbx)
	je	.LBB25_61
	cmpq	$0, (%rsi)
	je	.LBB25_1
	movq	8(%rbx), %r14
	movq	%rbx, %rcx
	movq	%rsi, %rdx
	callq	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser5ident
	cmpq	$0, (%rbx)
	je	.LBB25_39
	shrq	$32, %r15
	movups	-8(%rbp), %xmm0
	movups	8(%rbp), %xmm1
	movaps	%xmm1, -32(%rbp)
	movaps	%xmm0, -48(%rbp)
	cmpl	$-1, %r15d
	jne	.LBB25_65
	movq	-24(%rbp), %rax
	orq	-40(%rbp), %rax
	je	.LBB25_53
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB25_53
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.49(%rip), %rdx
	movl	$2, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB25_109
	movq	32(%rsi), %rdx
	testq	%rdx, %rdx
	je	.LBB25_53
	leaq	-48(%rbp), %rcx
	callq	_RNvXs0_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_5IdentNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt
	jmp	.LBB25_76
.LBB25_35:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB25_36
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.2(%rip), %rdx
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movl	%eax, %edi
	jmp	.LBB25_109
.LBB25_39:
	movb	(%rbp), %bl
	jmp	.LBB25_40
.LBB25_57:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB25_36
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.49(%rip), %rdx
	movl	$2, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB25_109
	cmpq	$0, (%rsi)
	jne	.LBB25_60
.LBB25_1:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB25_36
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.2(%rip), %rdx
	movl	$1, %r8d
	.seh_startepilogue
	addq	$152, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	jmp	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
.LBB25_36:
	xorl	%edi, %edi
.LBB25_109:
	movl	%edi, %eax
	.seh_startepilogue
	addq	$152, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
.LBB25_65:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB25_67
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.50(%rip), %rdx
	movl	$3, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB25_109
.LBB25_67:
	cmpl	$67, %r15d
	je	.LBB25_77
	cmpl	$83, %r15d
	jne	.LBB25_69
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB25_83
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.52(%rip), %rdx
	movl	$4, %r8d
	jmp	.LBB25_81
.LBB25_77:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB25_83
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.51(%rip), %rdx
	movl	$7, %r8d
.LBB25_81:
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	jmp	.LBB25_82
.LBB25_69:
	movq	%r15, %rax
	movl	%eax, -8(%rbp)
	movq	32(%rsi), %rdx
	testq	%rdx, %rdx
	je	.LBB25_83
	leaq	-8(%rbp), %rcx
	callq	_RNvXsk_NtCs8xEFJqa6dYS_4core3fmtcNtB5_7Display3fmt
.LBB25_82:
	testb	%al, %al
	jne	.LBB25_109
.LBB25_83:
	movq	-24(%rbp), %rax
	movq	32(%rsi), %rcx
	orq	-40(%rbp), %rax
	jne	.LBB25_91
.LBB25_84:
	testq	%rcx, %rcx
	je	.LBB25_53
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.54(%rip), %rdx
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB25_109
	movq	32(%rsi), %rdx
	movq	%r14, -8(%rbp)
	testq	%rdx, %rdx
	je	.LBB25_53
	leaq	-8(%rbp), %rcx
	callq	_RNvXsd_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impyNtB9_7Display3fmt
	testb	%al, %al
	jne	.LBB25_109
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB25_53
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.31(%rip), %rdx
	jmp	.LBB25_90
.LBB25_91:
	testq	%rcx, %rcx
	je	.LBB25_53
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.53(%rip), %rdx
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB25_109
	movq	32(%rsi), %rdx
	testq	%rdx, %rdx
	je	.LBB25_53
	leaq	-48(%rbp), %rcx
	callq	_RNvXs0_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_5IdentNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt
	testb	%al, %al
	jne	.LBB25_109
	movq	32(%rsi), %rcx
	jmp	.LBB25_84
.Lfunc_end25:
	.seh_endproc

	.def	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_type;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_type,unique,26
_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_type:
.Lfunc_begin26:
.seh_proc _RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_type
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
	subq	$48, %rsp
	.seh_stackalloc 48
	leaq	48(%rsp), %rbp
	.seh_setframe %rbp, 48
	.seh_endprologue
	movq	%rcx, %rsi
	movq	(%rcx), %rdi
	testq	%rdi, %rdi
	je	.LBB26_1
	movq	8(%rsi), %r15
	movq	16(%rsi), %r12
	cmpq	%r15, %r12
	jae	.LBB26_5
	movb	(%rdi,%r12), %bl
	leaq	1(%r12), %r14
	movq	%r14, 16(%rsi)
	movl	%ebx, %ecx
	callq	_RNvNtCseL4M8JimfzJ_14rustc_demangle2v010basic_type
	testq	%rax, %rax
	je	.LBB26_12
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB26_55
	movq	%rdx, %r8
	movq	%rax, %rdx
	jmp	.LBB26_3
.LBB26_1:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB26_55
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.2(%rip), %rdx
	movl	$1, %r8d
.LBB26_3:
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	jmp	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
.LBB26_5:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB26_83
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	movl	$16, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
.LBB26_7:
	testb	%al, %al
	jne	.LBB26_8
.LBB26_83:
	movq	$0, (%rsi)
	movb	$0, 8(%rsi)
.LBB26_55:
	xorl	%edi, %edi
.LBB26_8:
	movl	%edi, %eax
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
.LBB26_12:
	movl	24(%rsi), %eax
	incl	%eax
	movl	%eax, 24(%rsi)
	cmpl	$500, %eax
	jbe	.LBB26_13
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB26_17
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.1(%rip), %rdx
	movl	$25, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB26_8
.LBB26_17:
	movq	$0, (%rsi)
	movb	$1, 8(%rsi)
	jmp	.LBB26_55
.LBB26_13:
	movzbl	%bl, %eax
	addl	$-65, %eax
	cmpl	$22, %eax
	ja	.LBB26_84
	leaq	.LJTI26_0(%rip), %rcx
	movslq	(%rcx,%rax,4), %rax
	addq	%rcx, %rax
	jmpq	*%rax
.LBB26_33:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB26_35
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.47(%rip), %rdx
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB26_8
.LBB26_35:
	movq	%rsi, %rcx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_type
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB26_8
	cmpb	$65, %bl
	jne	.LBB26_40
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB26_39
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.63(%rip), %rdx
	movl	$2, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB26_8
.LBB26_39:
	movb	$1, %dil
	movq	%rsi, %rcx
	movb	$1, %dl
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer11print_const
	testb	%al, %al
	jne	.LBB26_8
.LBB26_40:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB26_53
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.48(%rip), %rdx
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	jmp	.LBB26_51
.LBB26_28:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB26_30
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.61(%rip), %rdx
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB26_8
.LBB26_30:
	cmpb	$80, %bl
	jne	.LBB26_78
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB26_77
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.62(%rip), %rdx
	movl	$6, %r8d
	jmp	.LBB26_80
.LBB26_18:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB26_22
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.58(%rip), %rdx
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB26_8
	movq	(%rsi), %rdi
	testq	%rdi, %rdi
	je	.LBB26_76
	movq	8(%rsi), %r15
	movq	16(%rsi), %r14
.LBB26_22:
	cmpq	%r15, %r14
	jae	.LBB26_76
	cmpb	$76, (%rdi,%r14)
	jne	.LBB26_76
	incq	%r14
	movq	%r14, 16(%rsi)
	leaq	-16(%rbp), %rdi
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	callq	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser10integer_62
	cmpb	$0, (%rdi)
	je	.LBB26_72
.LBB26_25:
	movb	-15(%rbp), %bl
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB26_27
	movzbl	%bl, %eax
	leaq	(%rax,%rax,8), %r8
	addq	$16, %r8
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.1(%rip), %r9
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	testb	%al, %al
	cmovneq	%r9, %rdx
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB26_8
.LBB26_27:
	movq	$0, (%rsi)
	movb	%bl, 8(%rsi)
	jmp	.LBB26_55
.LBB26_42:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB26_44
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.64(%rip), %rdx
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB26_8
.LBB26_44:
	movq	%rsi, %rcx
	callq	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNvB2_10print_typeEB8_
	movb	$1, %dil
	testb	$1, %al
	jne	.LBB26_8
	cmpq	$1, %rdx
	jne	.LBB26_48
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB26_53
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.65(%rip), %rdx
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB26_8
.LBB26_48:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB26_53
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.26(%rip), %rdx
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	jmp	.LBB26_52
.LBB26_68:
	movq	%rsi, %rcx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_type
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB26_8
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB26_71
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.67(%rip), %rdx
	movl	$4, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB26_8
.LBB26_71:
	movq	%rsi, %rcx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer9print_pat
	jmp	.LBB26_52
.LBB26_67:
	movq	%rsi, %rcx
	callq	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer13print_backrefNvB2_10print_typeEB8_
	jmp	.LBB26_51
.LBB26_50:
	movq	%rsi, %rcx
	callq	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer9in_binderNCNvB2_10print_type0EB8_
	jmp	.LBB26_51
.LBB26_56:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB26_58
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.66(%rip), %rdx
	movl	$4, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB26_8
.LBB26_58:
	movq	%rsi, %rcx
	callq	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer9in_binderNCNvB2_10print_types_0EB8_
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB26_8
	movq	(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB26_81
	movq	16(%rsi), %rax
	cmpq	8(%rsi), %rax
	jae	.LBB26_81
	cmpb	$76, (%rcx,%rax)
	jne	.LBB26_81
	incq	%rax
	movq	%rax, 16(%rsi)
	leaq	-16(%rbp), %rbx
	movq	%rbx, %rcx
	movq	%rsi, %rdx
	callq	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser10integer_62
	cmpb	$0, (%rbx)
	jne	.LBB26_25
	movq	-8(%rbp), %rbx
	testq	%rbx, %rbx
	je	.LBB26_53
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB26_66
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.28(%rip), %rdx
	movl	$3, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB26_8
.LBB26_66:
	movq	%rsi, %rcx
	movq	%rbx, %rdx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer25print_lifetime_from_index
	jmp	.LBB26_52
.LBB26_84:
	movq	%r12, 16(%rsi)
	movq	%rsi, %rcx
	xorl	%edx, %edx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_path
	jmp	.LBB26_51
.LBB26_81:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB26_83
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	movl	$16, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	jmp	.LBB26_7
.LBB26_72:
	movq	-8(%rbp), %rdx
	testq	%rdx, %rdx
	je	.LBB26_76
	movq	%rsi, %rcx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer25print_lifetime_from_index
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB26_8
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB26_76
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.59(%rip), %rdx
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB26_8
.LBB26_76:
	cmpb	$82, %bl
	je	.LBB26_77
.LBB26_78:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB26_77
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.60(%rip), %rdx
	movl	$4, %r8d
.LBB26_80:
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB26_8
.LBB26_77:
	movq	%rsi, %rcx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_type
.LBB26_51:
	movb	$1, %dil
.LBB26_52:
	testb	%al, %al
	jne	.LBB26_8
.LBB26_53:
	cmpq	$0, (%rsi)
	je	.LBB26_55
	decl	24(%rsi)
	jmp	.LBB26_55
.Lfunc_end26:
	.section	.rdata,"dr",associative,_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_type,unique,27
	.p2align	2, 0x0
.LJTI26_0:
	.long	.LBB26_33-.LJTI26_0
	.long	.LBB26_67-.LJTI26_0
	.long	.LBB26_84-.LJTI26_0
	.long	.LBB26_56-.LJTI26_0
	.long	.LBB26_84-.LJTI26_0
	.long	.LBB26_50-.LJTI26_0
	.long	.LBB26_84-.LJTI26_0
	.long	.LBB26_84-.LJTI26_0
	.long	.LBB26_84-.LJTI26_0
	.long	.LBB26_84-.LJTI26_0
	.long	.LBB26_84-.LJTI26_0
	.long	.LBB26_84-.LJTI26_0
	.long	.LBB26_84-.LJTI26_0
	.long	.LBB26_84-.LJTI26_0
	.long	.LBB26_28-.LJTI26_0
	.long	.LBB26_28-.LJTI26_0
	.long	.LBB26_18-.LJTI26_0
	.long	.LBB26_18-.LJTI26_0
	.long	.LBB26_33-.LJTI26_0
	.long	.LBB26_42-.LJTI26_0
	.long	.LBB26_84-.LJTI26_0
	.long	.LBB26_84-.LJTI26_0
	.long	.LBB26_68-.LJTI26_0
	.section	.text,"xr",one_only,_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_type,unique,26
	.seh_endproc

	.def	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer11print_const;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer11print_const,unique,28
_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer11print_const:
.Lfunc_begin27:
.seh_proc _RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer11print_const
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
	subq	$48, %rsp
	.seh_stackalloc 48
	leaq	48(%rsp), %rbp
	.seh_setframe %rbp, 48
	.seh_endprologue
	movq	%rcx, %rsi
	movq	(%rcx), %rcx
	testq	%rcx, %rcx
	je	.LBB27_1
	movq	8(%rsi), %r8
	movq	16(%rsi), %rax
	cmpq	%r8, %rax
	jae	.LBB27_4
	movl	%edx, %ebx
	movb	(%rcx,%rax), %r14b
	leaq	1(%rax), %rdx
	movq	%rdx, 16(%rsi)
	movl	24(%rsi), %r9d
	incl	%r9d
	movl	%r9d, 24(%rsi)
	cmpl	$500, %r9d
	jbe	.LBB27_9
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_15
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.1(%rip), %rdx
	movl	$25, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB27_7
.LBB27_15:
	movq	$0, (%rsi)
	movb	$1, 8(%rsi)
	jmp	.LBB27_23
.LBB27_9:
	movzbl	%r14b, %r9d
	leal	-81(%r9), %r10d
	cmpl	$40, %r10d
	ja	.LBB27_10
	leaq	.LJTI27_0(%rip), %r9
	movslq	(%r9,%r10,4), %r10
	addq	%r9, %r10
	jmpq	*%r10
.LBB27_24:
	cmpq	%r8, %rdx
	jae	.LBB27_28
	cmpb	$110, (%rcx,%rdx)
	jne	.LBB27_28
	addq	$2, %rax
	movq	%rax, 16(%rsi)
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_28
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.24(%rip), %rdx
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB27_7
.LBB27_28:
	movq	%rsi, %rcx
	movl	%r14d, %edx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer16print_const_uint
.LBB27_20:
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB27_7
.LBB27_21:
	cmpq	$0, (%rsi)
	je	.LBB27_23
	decl	24(%rsi)
	jmp	.LBB27_23
.LBB27_10:
	cmpl	$65, %r9d
	je	.LBB27_65
	cmpl	$66, %r9d
	jne	.LBB27_4
	movq	%rsi, %rcx
	movl	%ebx, %edx
	callq	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer13print_backrefNCNvB2_11print_consts4_0EB8_
	jmp	.LBB27_20
.LBB27_29:
	leaq	-16(%rbp), %rdi
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	callq	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser11hex_nibbles
	movq	(%rdi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_30
	movq	-8(%rbp), %rdx
	callq	_RNvMs1_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_10HexNibbles14try_parse_uint
	cmpq	$1, %rax
	jne	.LBB27_4
	testq	%rdx, %rdx
	je	.LBB27_40
	cmpq	$1, %rdx
	jne	.LBB27_4
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_21
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.70(%rip), %rdx
	movl	$4, %r8d
	jmp	.LBB27_19
.LBB27_16:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_21
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.68(%rip), %rdx
	jmp	.LBB27_18
.LBB27_54:
	cmpq	%r8, %rdx
	jae	.LBB27_56
	cmpb	$101, (%rcx,%rdx)
	jne	.LBB27_56
	addq	$2, %rax
	movq	%rax, 16(%rsi)
	movq	%rsi, %rcx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer23print_const_str_literal
	jmp	.LBB27_20
.LBB27_56:
	testb	%bl, %bl
	jne	.LBB27_59
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_59
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.71(%rip), %rdx
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB27_7
.LBB27_59:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_61
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.58(%rip), %rdx
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB27_7
.LBB27_61:
	cmpb	$82, %r14b
	je	.LBB27_62
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_62
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.60(%rip), %rdx
	movl	$4, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB27_7
.LBB27_62:
	movb	$1, %dil
	movq	%rsi, %rcx
	movb	$1, %dl
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer11print_const
	jmp	.LBB27_75
.LBB27_42:
	leaq	-16(%rbp), %rdi
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	callq	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser11hex_nibbles
	movq	(%rdi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_43
	movq	-8(%rbp), %rdx
	callq	_RNvMs1_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_10HexNibbles14try_parse_uint
	movq	%rdx, %rcx
	shrq	$32, %rcx
	sete	%cl
	andb	%al, %cl
	cmpb	$1, %cl
	jne	.LBB27_4
	movl	%edx, %eax
	xorl	$55296, %eax
	addl	$-1114112, %eax
	cmpl	$-1112064, %eax
	jae	.LBB27_47
.LBB27_4:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_39
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	movl	$16, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
.LBB27_6:
	testb	%al, %al
	jne	.LBB27_7
.LBB27_39:
	movq	$0, (%rsi)
	movb	$0, 8(%rsi)
	jmp	.LBB27_23
.LBB27_79:
	testb	%bl, %bl
	jne	.LBB27_82
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_82
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.71(%rip), %rdx
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB27_7
.LBB27_82:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_84
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.64(%rip), %rdx
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB27_7
.LBB27_84:
	movq	%rsi, %rcx
	callq	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNCNvB2_11print_consts1_0EB8_
	movb	$1, %dil
	testb	$1, %al
	jne	.LBB27_7
	cmpq	$1, %rdx
	jne	.LBB27_88
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_21
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.65(%rip), %rdx
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB27_7
.LBB27_88:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_21
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.26(%rip), %rdx
	jmp	.LBB27_73
.LBB27_90:
	testb	%bl, %bl
	jne	.LBB27_93
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_93
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.71(%rip), %rdx
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB27_7
.LBB27_93:
	movb	$1, %dil
	movq	%rsi, %rcx
	movb	$1, %dl
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_path
	testb	%al, %al
	jne	.LBB27_7
	movq	(%rsi), %rax
	testq	%rax, %rax
	je	.LBB27_1
	movq	16(%rsi), %rcx
	cmpq	8(%rsi), %rcx
	jae	.LBB27_96
	movzbl	(%rax,%rcx), %eax
	incq	%rcx
	movq	%rcx, 16(%rsi)
	cmpl	$83, %eax
	je	.LBB27_104
	cmpl	$84, %eax
	je	.LBB27_101
	cmpl	$85, %eax
	je	.LBB27_76
.LBB27_96:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_39
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	movl	$16, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	jmp	.LBB27_6
.LBB27_1:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_23
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.2(%rip), %rdx
	movl	$1, %r8d
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	jmp	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
.LBB27_48:
	testb	%bl, %bl
	jne	.LBB27_51
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_51
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.71(%rip), %rdx
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB27_7
.LBB27_51:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_53
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.61(%rip), %rdx
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB27_7
.LBB27_53:
	movq	%rsi, %rcx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer23print_const_str_literal
	movb	$1, %dil
	jmp	.LBB27_75
.LBB27_65:
	testb	%bl, %bl
	jne	.LBB27_68
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_68
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.71(%rip), %rdx
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB27_7
.LBB27_68:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_70
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.47(%rip), %rdx
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB27_7
.LBB27_70:
	movq	%rsi, %rcx
	callq	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNCNvB2_11print_consts0_0EB8_
	movb	$1, %dil
	testq	%rax, %rax
	jne	.LBB27_7
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_21
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.48(%rip), %rdx
.LBB27_73:
	movl	$1, %r8d
.LBB27_74:
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
.LBB27_75:
	testb	%al, %al
	jne	.LBB27_7
.LBB27_76:
	testb	%bl, %bl
	jne	.LBB27_21
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_21
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.31(%rip), %rdx
.LBB27_18:
	movl	$1, %r8d
.LBB27_19:
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	jmp	.LBB27_20
.LBB27_30:
	movb	-8(%rbp), %bl
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_33
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.1(%rip), %rax
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	testb	%bl, %bl
	cmovneq	%rax, %rdx
	movzbl	%bl, %eax
	leaq	(%rax,%rax,8), %r8
	addq	$16, %r8
	jmp	.LBB27_32
.LBB27_43:
	movb	-8(%rbp), %bl
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_33
	movzbl	%bl, %eax
	leaq	(%rax,%rax,8), %r8
	addq	$16, %r8
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.1(%rip), %r9
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	testb	%al, %al
	cmovneq	%r9, %rdx
.LBB27_32:
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB27_7
.LBB27_33:
	movq	$0, (%rsi)
	movb	%bl, 8(%rsi)
.LBB27_23:
	xorl	%edi, %edi
.LBB27_7:
	movl	%edi, %eax
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.LBB27_47:
	movq	32(%rsi), %rcx
	callq	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer26print_quoted_escaped_charsINtNtNtNtCs8xEFJqa6dYS_4core4iter7sources4once4OncecEEB8_
	jmp	.LBB27_20
.LBB27_40:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_21
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.69(%rip), %rdx
	movl	$5, %r8d
	jmp	.LBB27_19
.LBB27_101:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_103
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.64(%rip), %rdx
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB27_7
.LBB27_103:
	movq	%rsi, %rcx
	callq	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNCNvB2_11print_consts0_0EB8_
	testq	%rax, %rax
	je	.LBB27_88
	jmp	.LBB27_7
.LBB27_104:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_106
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.72(%rip), %rdx
	movl	$3, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB27_7
.LBB27_106:
	movq	%rsi, %rcx
	callq	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNCNvB2_11print_consts3_0EB8_
	testq	%rax, %rax
	jne	.LBB27_7
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB27_21
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.73(%rip), %rdx
	movl	$2, %r8d
	jmp	.LBB27_74
.Lfunc_end27:
	.section	.rdata,"dr",associative,_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer11print_const,unique,29
	.p2align	2, 0x0
.LJTI27_0:
	.long	.LBB27_56-.LJTI27_0
	.long	.LBB27_54-.LJTI27_0
	.long	.LBB27_4-.LJTI27_0
	.long	.LBB27_79-.LJTI27_0
	.long	.LBB27_4-.LJTI27_0
	.long	.LBB27_90-.LJTI27_0
	.long	.LBB27_4-.LJTI27_0
	.long	.LBB27_4-.LJTI27_0
	.long	.LBB27_4-.LJTI27_0
	.long	.LBB27_4-.LJTI27_0
	.long	.LBB27_4-.LJTI27_0
	.long	.LBB27_4-.LJTI27_0
	.long	.LBB27_4-.LJTI27_0
	.long	.LBB27_4-.LJTI27_0
	.long	.LBB27_4-.LJTI27_0
	.long	.LBB27_4-.LJTI27_0
	.long	.LBB27_24-.LJTI27_0
	.long	.LBB27_29-.LJTI27_0
	.long	.LBB27_42-.LJTI27_0
	.long	.LBB27_4-.LJTI27_0
	.long	.LBB27_48-.LJTI27_0
	.long	.LBB27_4-.LJTI27_0
	.long	.LBB27_4-.LJTI27_0
	.long	.LBB27_28-.LJTI27_0
	.long	.LBB27_24-.LJTI27_0
	.long	.LBB27_28-.LJTI27_0
	.long	.LBB27_4-.LJTI27_0
	.long	.LBB27_24-.LJTI27_0
	.long	.LBB27_28-.LJTI27_0
	.long	.LBB27_24-.LJTI27_0
	.long	.LBB27_28-.LJTI27_0
	.long	.LBB27_16-.LJTI27_0
	.long	.LBB27_4-.LJTI27_0
	.long	.LBB27_4-.LJTI27_0
	.long	.LBB27_24-.LJTI27_0
	.long	.LBB27_28-.LJTI27_0
	.long	.LBB27_4-.LJTI27_0
	.long	.LBB27_4-.LJTI27_0
	.long	.LBB27_4-.LJTI27_0
	.long	.LBB27_24-.LJTI27_0
	.long	.LBB27_28-.LJTI27_0
	.section	.text,"xr",one_only,_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer11print_const,unique,28
	.seh_endproc

	.def	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer16print_const_uint;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer16print_const_uint,unique,30
_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer16print_const_uint:
.Lfunc_begin28:
.seh_proc _RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer16print_const_uint
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
	movq	%rcx, %rsi
	cmpq	$0, (%rcx)
	je	.LBB28_1
	movl	%edx, %ebx
	leaq	-8(%rbp), %rdi
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	callq	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser11hex_nibbles
	movq	(%rdi), %r14
	testq	%r14, %r14
	je	.LBB28_7
	movq	(%rbp), %r15
	movq	%r14, %rcx
	movq	%r15, %rdx
	callq	_RNvMs1_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_10HexNibbles14try_parse_uint
	cmpq	$1, %rax
	jne	.LBB28_13
	movq	%rdx, -8(%rbp)
	movq	32(%rsi), %rsi
	testq	%rsi, %rsi
	je	.LBB28_2
	leaq	-8(%rbp), %rcx
	movq	%rsi, %rdx
	callq	_RNvXsd_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impyNtB9_7Display3fmt
	movb	$1, %dil
	jmp	.LBB28_16
.LBB28_1:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB28_2
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.2(%rip), %rdx
	movl	$1, %r8d
.LBB28_5:
	.seh_startepilogue
	addq	$56, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	jmp	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
.LBB28_7:
	movb	(%rbp), %bl
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB28_9
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.1(%rip), %rax
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	testb	%bl, %bl
	cmovneq	%rax, %rdx
	movzbl	%bl, %eax
	leaq	(%rax,%rax,8), %r8
	addq	$16, %r8
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB28_3
.LBB28_9:
	movq	$0, (%rsi)
	movb	%bl, 8(%rsi)
	jmp	.LBB28_2
.LBB28_13:
	movq	32(%rsi), %rsi
	testq	%rsi, %rsi
	je	.LBB28_2
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.75(%rip), %rdx
	movl	$2, %r8d
	movq	%rsi, %rcx
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB28_3
	movq	%rsi, %rcx
	movq	%r14, %rdx
	movq	%r15, %r8
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
.LBB28_16:
	testb	%al, %al
	jne	.LBB28_3
	testb	$-128, 18(%rsi)
	jne	.LBB28_2
	movl	%ebx, %ecx
	callq	_RNvNtCseL4M8JimfzJ_14rustc_demangle2v010basic_type
	testq	%rax, %rax
	je	.LBB28_20
	movq	%rdx, %r8
	movq	%rsi, %rcx
	movq	%rax, %rdx
	jmp	.LBB28_5
.LBB28_2:
	xorl	%edi, %edi
.LBB28_3:
	movl	%edi, %eax
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
.LBB28_20:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.76(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end28:
	.seh_endproc

	.def	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer23print_const_str_literal;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer23print_const_str_literal,unique,31
_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer23print_const_str_literal:
.Lfunc_begin29:
.seh_proc _RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer23print_const_str_literal
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
	subq	$104, %rsp
	.seh_stackalloc 104
	leaq	96(%rsp), %rbp
	.seh_setframe %rbp, 96
	.seh_endprologue
	movq	%rcx, %rdi
	cmpq	$0, (%rcx)
	je	.LBB29_1
	leaq	-56(%rbp), %rsi
	movq	%rsi, %rcx
	movq	%rdi, %rdx
	callq	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser11hex_nibbles
	movq	(%rsi), %rbx
	testq	%rbx, %rbx
	je	.LBB29_4
	movq	-48(%rbp), %r15
	testb	$1, %r15b
	jne	.LBB29_26
	movabsq	$9223372036854775806, %rax
	andq	%rax, %r15
	leaq	(%rbx,%r15), %r12
	movq	%rbx, (%rsi)
	movq	%r15, 8(%rsi)
	movq	%r12, 16(%rsi)
	movq	$0, 24(%rsi)
	movq	$2, 32(%rsi)
.LBB29_9:
	movq	%rsi, %rcx
	callq	_RNvXNtNtNtCs8xEFJqa6dYS_4core4iter7sources7from_fnINtB2_6FromFnNCNvMs1_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB17_10HexNibbles19try_parse_str_charss0_0ENtNtNtB6_6traits8iterator8Iterator4nextB19_
	cmpl	$-2, %eax
	jb	.LBB29_9
	jne	.LBB29_26
	movq	32(%rdi), %r14
	testq	%r14, %r14
	je	.LBB29_29
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movl	$34, %edx
	callq	*32(%rax)
	movb	$1, %sil
	testb	%al, %al
	jne	.LBB29_30
	leaq	-56(%rbp), %rdi
	movq	%rbx, (%rdi)
	movq	%r15, 8(%rdi)
	movq	%r12, 16(%rdi)
	movq	$0, 24(%rdi)
	movq	$2, 32(%rdi)
.LBB29_14:
	leaq	-12(%rbp), %rbx
.LBB29_15:
	movq	%rdi, %rcx
	callq	_RNvXNtNtNtCs8xEFJqa6dYS_4core4iter7sources7from_fnINtB2_6FromFnNCNvMs1_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB17_10HexNibbles19try_parse_str_charss0_0ENtNtNtB6_6traits8iterator8Iterator4nextB19_
	cmpl	$-2, %eax
	je	.LBB29_19
	cmpl	$39, %eax
	jne	.LBB29_17
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movl	$39, %edx
	callq	*32(%rax)
	testb	%al, %al
	je	.LBB29_15
	jmp	.LBB29_30
.LBB29_17:
	cmpl	$-1, %eax
	je	.LBB29_18
	movq	%rbx, %rcx
	movl	%eax, %edx
	callq	_RNvMNtNtCs8xEFJqa6dYS_4core4char7methodsc16escape_debug_ext
	movb	1(%rbp), %r15b
	movzbl	(%rbp), %r12d
	movl	-12(%rbp), %r13d
	movzbl	%r15b, %ebx
.LBB29_22:
	cmpq	%rbx, %r12
	jae	.LBB29_14
	movl	%r13d, %edx
	cmpb	$-128, %r15b
	ja	.LBB29_25
	movzbl	-12(%rbp,%r12), %edx
.LBB29_25:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	callq	*32(%rax)
	incq	%r12
	testb	%al, %al
	je	.LBB29_22
	jmp	.LBB29_30
.LBB29_1:
	movq	32(%rdi), %rcx
	testq	%rcx, %rcx
	je	.LBB29_29
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.2(%rip), %rdx
	movl	$1, %r8d
	.seh_startepilogue
	addq	$104, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r13
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	jmp	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
.LBB29_26:
	movq	32(%rdi), %rcx
	testq	%rcx, %rcx
	je	.LBB29_28
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	movl	$16, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %sil
	testb	%al, %al
	jne	.LBB29_30
.LBB29_28:
	movq	$0, (%rdi)
	movb	$0, 8(%rdi)
	jmp	.LBB29_29
.LBB29_4:
	movb	-48(%rbp), %bl
	movq	32(%rdi), %rcx
	testq	%rcx, %rcx
	je	.LBB29_6
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.1(%rip), %rax
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	testb	%bl, %bl
	cmovneq	%rax, %rdx
	movzbl	%bl, %eax
	leaq	(%rax,%rax,8), %r8
	addq	$16, %r8
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %sil
	testb	%al, %al
	jne	.LBB29_30
.LBB29_6:
	movq	$0, (%rdi)
	movb	%bl, 8(%rdi)
.LBB29_29:
	xorl	%esi, %esi
.LBB29_30:
	movl	%esi, %eax
	.seh_startepilogue
	addq	$104, %rsp
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
.LBB29_19:
	movq	(%r14), %rcx
	movq	8(%r14), %rax
	movq	32(%rax), %rax
	movl	$34, %edx
	.seh_startepilogue
	addq	$104, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r13
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	rex64 jmpq	*%rax
.LBB29_18:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.162(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.37(%rip), %rcx
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.36(%rip), %r9
	leaq	7(%rbp), %r8
	movl	$43, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core6result13unwrap_failed
	ud2
.Lfunc_end29:
	.seh_endproc

	.def	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer25print_lifetime_from_index;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer25print_lifetime_from_index,unique,32
_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer25print_lifetime_from_index:
.Lfunc_begin30:
.seh_proc _RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer25print_lifetime_from_index
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
	movq	32(%rcx), %rsi
	testq	%rsi, %rsi
	je	.LBB30_6
	movq	%rdx, %r14
	movq	%rcx, %rbx
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.77(%rip), %rdx
	movl	$1, %r8d
	movq	%rsi, %rcx
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB30_7
	testq	%r14, %r14
	je	.LBB30_8
	movl	40(%rbx), %r15d
	subq	%r14, %r15
	jae	.LBB30_9
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	movl	$16, %r8d
	movq	%rsi, %rcx
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB30_7
	movq	$0, (%rbx)
	movb	$0, 8(%rbx)
.LBB30_6:
	xorl	%edi, %edi
.LBB30_7:
	movl	%edi, %eax
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
.LBB30_8:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.68(%rip), %rdx
	movl	$1, %r8d
	movq	%rsi, %rcx
	.seh_startepilogue
	addq	$56, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	jmp	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
.LBB30_9:
	cmpq	$26, %r15
	jae	.LBB30_11
	addl	$97, %r15d
	leaq	4(%rbp), %rcx
	movl	%r15d, (%rcx)
	movq	%rsi, %rdx
	callq	_RNvXsk_NtCs8xEFJqa6dYS_4core3fmtcNtB5_7Display3fmt
	jmp	.LBB30_13
.LBB30_11:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.68(%rip), %rdx
	movl	$1, %r8d
	movq	%rsi, %rcx
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB30_7
	leaq	-8(%rbp), %rcx
	movq	%r15, (%rcx)
	movq	%rsi, %rdx
	callq	_RNvXsd_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impyNtB9_7Display3fmt
.LBB30_13:
	movl	%eax, %edi
	jmp	.LBB30_7
.Lfunc_end30:
	.seh_endproc

	.def	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer30print_path_maybe_open_generics;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer30print_path_maybe_open_generics,unique,33
_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer30print_path_maybe_open_generics:
.Lfunc_begin31:
.seh_proc _RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer30print_path_maybe_open_generics
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$96, %rsp
	.seh_stackalloc 96
	leaq	96(%rsp), %rbp
	.seh_setframe %rbp, 96
	.seh_endprologue
	movq	%rcx, %rsi
	movq	(%rcx), %rcx
	testq	%rcx, %rcx
	je	.LBB31_15
	movq	16(%rsi), %rax
	cmpq	8(%rsi), %rax
	jae	.LBB31_15
	movzbl	(%rcx,%rax), %ecx
	cmpl	$73, %ecx
	je	.LBB31_8
	cmpl	$66, %ecx
	jne	.LBB31_15
	incq	%rax
	movq	%rax, 16(%rsi)
	leaq	-32(%rbp), %rdi
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	callq	_RNvMs2_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_6Parser7backref
	cmpq	$0, (%rdi)
	je	.LBB31_5
	cmpq	$0, 32(%rsi)
	je	.LBB31_14
	movups	(%rsi), %xmm0
	movups	16(%rsi), %xmm1
	movaps	%xmm1, -48(%rbp)
	movaps	%xmm0, -64(%rbp)
	movups	-32(%rbp), %xmm0
	movups	-16(%rbp), %xmm1
	movups	%xmm0, (%rsi)
	movups	%xmm1, 16(%rsi)
	movq	%rsi, %rcx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer30print_path_maybe_open_generics
	movaps	-64(%rbp), %xmm0
	movaps	-48(%rbp), %xmm1
	movups	%xmm0, (%rsi)
	movups	%xmm1, 16(%rsi)
	jmp	.LBB31_10
.LBB31_15:
	movq	%rsi, %rcx
	xorl	%edx, %edx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_path
	movl	%eax, %edi
	addb	%dil, %dil
.LBB31_9:
	movl	%edi, %eax
.LBB31_10:
	.seh_startepilogue
	addq	$96, %rsp
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB31_8:
	incq	%rax
	movq	%rax, 16(%rsi)
	movq	%rsi, %rcx
	xorl	%edx, %edx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_path
	movb	$2, %dil
	testb	%al, %al
	jne	.LBB31_9
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB31_18
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.55(%rip), %rdx
	movl	$1, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB31_9
.LBB31_18:
	movq	%rsi, %rcx
	callq	_RINvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB6_7Printer14print_sep_listNvB2_17print_generic_argEB8_
	movq	%rax, %rdi
	incb	%dil
	jmp	.LBB31_9
.LBB31_5:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB31_13
	movb	-24(%rbp), %al
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.1(%rip), %r8
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	testb	%al, %al
	cmovneq	%r8, %rdx
	movzbl	%al, %eax
	leaq	(%rax,%rax,8), %r8
	addq	$16, %r8
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	je	.LBB31_13
	movb	$2, %dil
	jmp	.LBB31_9
.LBB31_13:
	movups	-32(%rbp), %xmm0
	movups	-16(%rbp), %xmm1
	movups	%xmm1, 16(%rsi)
	movups	%xmm0, (%rsi)
.LBB31_14:
	xorl	%edi, %edi
	jmp	.LBB31_9
.Lfunc_end31:
	.seh_endproc

	.def	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer9print_pat;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer9print_pat,unique,34
_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer9print_pat:
.Lfunc_begin32:
.seh_proc _RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer9print_pat
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
	leaq	32(%rsp), %rbp
	.seh_setframe %rbp, 32
	.seh_endprologue
	movq	%rcx, %rsi
	movq	(%rcx), %rax
	testq	%rax, %rax
	je	.LBB32_1
	movq	16(%rsi), %rcx
	cmpq	8(%rsi), %rcx
	jae	.LBB32_4
	movzbl	(%rax,%rcx), %eax
	incq	%rcx
	movq	%rcx, 16(%rsi)
	cmpl	$78, %eax
	je	.LBB32_13
	cmpl	$79, %eax
	je	.LBB32_16
	cmpl	$82, %eax
	jne	.LBB32_4
	movq	%rsi, %rcx
	xorl	%edx, %edx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer11print_const
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB32_34
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB32_12
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.78(%rip), %rdx
	movl	$3, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB32_34
.LBB32_12:
	movq	%rsi, %rcx
	xorl	%edx, %edx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer11print_const
	jmp	.LBB32_15
.LBB32_4:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB32_32
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	movl	$16, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
.LBB32_31:
	testb	%al, %al
	jne	.LBB32_34
.LBB32_32:
	movq	$0, (%rsi)
	movb	$0, 8(%rsi)
	jmp	.LBB32_33
.LBB32_1:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB32_33
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.2(%rip), %rdx
	movl	$1, %r8d
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	jmp	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
.LBB32_16:
	movl	24(%rsi), %eax
	incl	%eax
	movl	%eax, 24(%rsi)
	cmpl	$500, %eax
	jbe	.LBB32_17
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB32_25
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.1(%rip), %rdx
	movl	$25, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB32_34
.LBB32_25:
	movq	$0, (%rsi)
	movb	$1, 8(%rsi)
	jmp	.LBB32_33
.LBB32_13:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB32_33
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.80(%rip), %rdx
	movl	$5, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	movb	$1, %dil
.LBB32_15:
	testb	%al, %al
	jne	.LBB32_34
.LBB32_33:
	xorl	%edi, %edi
.LBB32_34:
	movl	%edi, %eax
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB32_17:
	movq	%rsi, %rcx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer9print_pat
	movb	$1, %dil
	testb	%al, %al
	jne	.LBB32_34
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.79(%rip), %rbx
.LBB32_19:
	movq	(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB32_29
	movq	16(%rsi), %rax
	cmpq	8(%rsi), %rax
	jae	.LBB32_26
	cmpb	$69, (%rcx,%rax)
	je	.LBB32_22
.LBB32_26:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB32_28
	movl	$3, %r8d
	movq	%rbx, %rdx
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	testb	%al, %al
	jne	.LBB32_34
.LBB32_28:
	movq	%rsi, %rcx
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer9print_pat
	testb	%al, %al
	je	.LBB32_19
	jmp	.LBB32_34
.LBB32_29:
	movq	32(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB32_32
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.0(%rip), %rdx
	movl	$16, %r8d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
	jmp	.LBB32_31
.LBB32_22:
	incq	%rax
	movq	%rax, 16(%rsi)
	decl	24(%rsi)
	jmp	.LBB32_33
.Lfunc_end32:
	.seh_endproc

	.def	_RNvMsf_NtNtCs8xEFJqa6dYS_4core3str4iterINtB5_13SplitInternalcE4nextCseL4M8JimfzJ_14rustc_demangle;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMsf_NtNtCs8xEFJqa6dYS_4core3str4iterINtB5_13SplitInternalcE4nextCseL4M8JimfzJ_14rustc_demangle,unique,35
_RNvMsf_NtNtCs8xEFJqa6dYS_4core3str4iterINtB5_13SplitInternalcE4nextCseL4M8JimfzJ_14rustc_demangle:
.Lfunc_begin33:
.seh_proc _RNvMsf_NtNtCs8xEFJqa6dYS_4core3str4iterINtB5_13SplitInternalcE4nextCseL4M8JimfzJ_14rustc_demangle
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
	leaq	32(%rsp), %rbp
	.seh_setframe %rbp, 32
	.seh_endprologue
	cmpb	$0, 65(%rcx)
	je	.LBB33_2
	xorl	%eax, %eax
	jmp	.LBB33_21
.LBB33_2:
	movq	%rcx, %rsi
	movq	16(%rcx), %r12
	movq	24(%rcx), %rax
	movq	40(%rcx), %rbx
	movq	%rax, (%rbp)
	cmpq	%rax, %rbx
	seta	%al
	movq	32(%rcx), %r13
	cmpq	%r13, %rbx
	setb	%cl
	orb	%al, %cl
	jne	.LBB33_20
	movzbl	56(%rsi), %edi
	movb	47(%rsi,%rdi), %r14b
.LBB33_4:
	movq	%rbx, %r8
	subq	%r13, %r8
	leaq	(%r12,%r13), %rax
	cmpq	$15, %r8
	ja	.LBB33_11
	xorl	%edx, %edx
	testq	%r8, %r8
	je	.LBB33_6
.LBB33_7:
	cmpb	%r14b, (%rax,%rdx)
	je	.LBB33_8
	incq	%rdx
	cmpq	%rdx, %r8
	jne	.LBB33_7
	movq	%r8, %rdx
.LBB33_6:
	xorl	%eax, %eax
	jmp	.LBB33_12
.LBB33_11:
	movl	%r14d, %ecx
	movq	%rax, %rdx
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice6memchr14memchr_aligned
	jmp	.LBB33_12
.LBB33_8:
	movl	$1, %eax
.LBB33_12:
	cmpq	$1, %rax
	jne	.LBB33_19
	addq	%rdx, %r13
	incq	%r13
	movq	%r13, 32(%rsi)
	movq	%r13, %r15
	subq	%rdi, %r15
	jb	.LBB33_15
	cmpq	(%rbp), %r13
	ja	.LBB33_15
	cmpb	$5, %dil
	jae	.LBB33_22
	leaq	(%r12,%r15), %rcx
	leaq	48(%rsi), %rdx
	movq	%rdi, %r8
	callq	memcmp
	testl	%eax, %eax
	je	.LBB33_18
.LBB33_15:
	cmpq	%r13, %rbx
	jae	.LBB33_4
	jmp	.LBB33_20
.LBB33_19:
	movq	%rbx, 32(%rsi)
.LBB33_20:
	movb	$1, 65(%rsi)
	movq	(%rsi), %rcx
	movq	8(%rsi), %r15
	addq	%rcx, %r12
	xorl	%eax, %eax
	subq	%rcx, %r15
	cmovneq	%r12, %rax
	cmpb	$0, 64(%rsi)
	cmovneq	%r12, %rax
.LBB33_21:
	movq	%r15, %rdx
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
.LBB33_18:
	movq	(%rsi), %rax
	subq	%rax, %r15
	addq	%rax, %r12
	movq	%r13, (%rsi)
	movq	%r12, %rax
	jmp	.LBB33_21
.LBB33_22:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.151(%rip), %r9
	movl	$4, %r8d
	xorl	%ecx, %ecx
	movq	%rdi, %rdx
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	ud2
.Lfunc_end33:
	.seh_endproc

	.def	_RNvNtCseL4M8JimfzJ_14rustc_demangle2v010basic_type;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNtCseL4M8JimfzJ_14rustc_demangle2v010basic_type,unique,36
_RNvNtCseL4M8JimfzJ_14rustc_demangle2v010basic_type:
.Lfunc_begin34:
	addb	$-97, %cl
	cmpb	$25, %cl
	ja	.LBB34_1
	movzbl	%cl, %eax
	shll	$3, %eax
	leaq	switch.table._RNvNtCseL4M8JimfzJ_14rustc_demangle2v010basic_type(%rip), %rcx
	movq	(%rax,%rcx), %rdx
	leaq	switch.table._RNvNtCseL4M8JimfzJ_14rustc_demangle2v010basic_type.41(%rip), %rcx
	movq	(%rax,%rcx), %rax
	retq
.LBB34_1:
	xorl	%eax, %eax
	retq
.Lfunc_end34:

	.def	_RNvNtNtNtCs8xEFJqa6dYS_4core7unicode12unicode_data11white_space6lookup;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNtNtNtCs8xEFJqa6dYS_4core7unicode12unicode_data11white_space6lookup,unique,37
_RNvNtNtNtCs8xEFJqa6dYS_4core7unicode12unicode_data11white_space6lookup:
.Lfunc_begin35:
	movl	%ecx, %edx
	shrl	$8, %edx
	xorl	%eax, %eax
	cmpl	$31, %edx
	jg	.LBB35_5
	testl	%edx, %edx
	je	.LBB35_8
	cmpl	$22, %edx
	jne	.LBB35_10
	cmpl	$5760, %ecx
	jmp	.LBB35_4
.LBB35_5:
	cmpl	$32, %edx
	je	.LBB35_9
	cmpl	$48, %edx
	jne	.LBB35_10
	cmpl	$12288, %ecx
.LBB35_4:
	sete	%al
	jmp	.LBB35_10
.LBB35_8:
	movzbl	%cl, %eax
	leaq	_RNvNtNtNtCs8xEFJqa6dYS_4core7unicode12unicode_data11white_space14WHITESPACE_MAP(%rip), %rcx
	movb	(%rax,%rcx), %al
	jmp	.LBB35_10
.LBB35_9:
	movzbl	%cl, %eax
	leaq	_RNvNtNtNtCs8xEFJqa6dYS_4core7unicode12unicode_data11white_space14WHITESPACE_MAP(%rip), %rcx
	movb	(%rax,%rcx), %al
	shrb	%al
.LBB35_10:
	andb	$1, %al
	retq
.Lfunc_end35:

	.def	_RNvXNtCseL4M8JimfzJ_14rustc_demangle6legacyNtB2_8DemangleNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXNtCseL4M8JimfzJ_14rustc_demangle6legacyNtB2_8DemangleNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt,unique,38
	.globl	_RNvXNtCseL4M8JimfzJ_14rustc_demangle6legacyNtB2_8DemangleNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt
_RNvXNtCseL4M8JimfzJ_14rustc_demangle6legacyNtB2_8DemangleNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt:
.Lfunc_begin36:
.seh_proc _RNvXNtCseL4M8JimfzJ_14rustc_demangle6legacyNtB2_8DemangleNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt
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
	movq	%rdx, %rax
	movq	(%rcx), %r15
	movq	8(%rcx), %rdx
	movq	16(%rcx), %rcx
	movq	%rcx, -40(%rbp)
	movl	16(%rax), %ecx
	movq	(%rax), %r14
	movq	%rax, -48(%rbp)
	movq	8(%rax), %rax
	movq	%rax, -8(%rbp)
	xorl	%eax, %eax
	andl	$8388608, %ecx
	movl	%ecx, -28(%rbp)
.LBB36_1:
	movq	%rax, %rcx
	cmpq	-40(%rbp), %rax
	setne	%al
	movl	%eax, 4(%rbp)
	je	.LBB36_174
	testq	%rdx, %rdx
	je	.LBB36_179
	leaq	1(%rcx), %rax
	movq	%rax, -64(%rbp)
	movb	(%r15), %al
	movzbl	%al, %r13d
	leaq	-1(%rdx), %r9
	xorl	%r10d, %r10d
	xorl	%ebx, %ebx
	movl	%eax, %r11d
	movq	%rdx, %r8
.LBB36_4:
	testb	%r11b, %r11b
	js	.LBB36_6
	movzbl	%r11b, %edi
	jmp	.LBB36_12
.LBB36_6:
	movl	%r11d, %esi
	andb	$31, %sil
	movzbl	%sil, %edi
	movzbl	1(%r15,%rbx), %r12d
	andl	$63, %r12d
	cmpb	$-33, %r11b
	jbe	.LBB36_9
	movzbl	2(%r15,%rbx), %esi
	shll	$6, %r12d
	andl	$63, %esi
	orl	%r12d, %esi
	cmpb	$-16, %r11b
	jb	.LBB36_11
	movzbl	3(%r15,%rbx), %r12d
	andl	$7, %edi
	shll	$18, %edi
	shll	$6, %esi
	andl	$63, %r12d
	orl	%esi, %r12d
	jmp	.LBB36_10
.LBB36_9:
	shll	$6, %edi
.LBB36_10:
	orl	%r12d, %edi
	jmp	.LBB36_12
.LBB36_11:
	shll	$12, %edi
	orl	%esi, %edi
.LBB36_12:
	addl	$-48, %edi
	cmpl	$10, %edi
	jae	.LBB36_16
	cmpq	%rbx, %r9
	je	.LBB36_179
	movb	1(%r15,%rbx), %r11b
	cmpb	$-65, %r11b
	jle	.LBB36_180
	decq	%r8
	incq	%rbx
	decq	%r10
	jmp	.LBB36_4
.LBB36_16:
	testq	%rbx, %rbx
	je	.LBB36_182
	cmpb	$-65, (%r15,%rbx)
	jle	.LBB36_183
	cmpq	$1, %rbx
	jne	.LBB36_21
	movb	$1, %r9b
	cmpl	$43, %r13d
	je	.LBB36_177
	cmpl	$45, %r13d
	je	.LBB36_177
.LBB36_21:
	movq	%rdx, %r13
	movq	%rdx, %r9
	subq	%rbx, %r9
	xorl	%edi, %edi
	cmpb	$43, %al
	sete	%dil
	movq	%rdi, %r12
	negq	%r12
	movq	%rbx, %rax
	subq	%rdi, %rax
	addq	%r15, %rdi
	cmpq	$17, %rax
	jae	.LBB36_30
	testq	%rax, %rax
	je	.LBB36_35
	addq	%rbx, %r12
	xorl	%edx, %edx
	xorl	%eax, %eax
.LBB36_24:
	movzbl	(%rdi,%rdx), %esi
	addl	$-48, %esi
	cmpl	$9, %esi
	ja	.LBB36_181
	leaq	(%rax,%rax,4), %rax
	movl	%esi, %esi
	leaq	(%rsi,%rax,2), %rax
	incq	%rdx
	cmpq	%rdx, %r12
	jne	.LBB36_24
.LBB36_26:
	testq	%rax, %rax
	je	.LBB36_35
	movq	%r13, %rdx
	subq	%rax, %rdx
	cmpq	%r9, %rax
	jae	.LBB36_36
	leaq	(%r15,%rax), %r12
	cmpb	$-65, (%rbx,%r12)
	jle	.LBB36_184
	addq	%rbx, %r12
	subq	%rbx, %rdx
	movq	%rdx, -24(%rbp)
	movq	%rax, %r9
	leaq	(%r15,%rbx), %r13
	jmp	.LBB36_38
.LBB36_30:
	addq	%rbx, %r12
	xorl	%esi, %esi
	xorl	%eax, %eax
.LBB36_31:
	cmpq	%rsi, %r12
	je	.LBB36_26
	movl	$10, %edx
	mulq	%rdx
	movb	(%rdi,%rsi), %dl
	jo	.LBB36_175
	movzbl	%dl, %edx
	addl	$-48, %edx
	cmpl	$10, %edx
	jae	.LBB36_181
	movl	%edx, %edx
	incq	%rsi
	addq	%rdx, %rax
	jae	.LBB36_31
	jmp	.LBB36_176
.LBB36_35:
	xorl	%edi, %edi
	movq	%r9, -24(%rbp)
	leaq	(%r15,%rbx), %r13
	movq	%r13, %r12
	jmp	.LBB36_54
.LBB36_36:
	cmpq	%rbx, %rdx
	jne	.LBB36_184
	leaq	(%r15,%rbx), %r13
	leaq	(%r9,%r13), %r12
	movq	$0, -24(%rbp)
.LBB36_38:
	cmpb	$104, %r11b
	jne	.LBB36_53
	leaq	1(%rcx), %rdx
	cmpq	-40(%rbp), %rdx
	jne	.LBB36_53
	cmpl	$0, -28(%rbp)
	je	.LBB36_53
	cmpq	$1, %r9
	je	.LBB36_43
	cmpb	$-64, 1(%r15,%rbx)
	jl	.LBB36_189
.LBB36_43:
	leaq	(%r15,%rbx), %rdx
	incq	%rdx
	cmpq	%r8, %rax
	cmovbq	%rax, %r8
	addq	%r15, %r8
	subq	%r10, %r8
.LBB36_44:
	cmpq	%rdx, %r8
	je	.LBB36_169
	movb	(%rdx), %r11b
	movzbl	%r11b, %eax
	testb	%al, %al
	js	.LBB36_47
	incq	%rdx
	jmp	.LBB36_52
.LBB36_47:
	movl	%eax, %r10d
	andl	$31, %r10d
	movzbl	1(%rdx), %esi
	andl	$63, %esi
	cmpb	$-33, %al
	jbe	.LBB36_50
	movzbl	2(%rdx), %eax
	shll	$6, %esi
	andl	$63, %eax
	orl	%esi, %eax
	cmpb	$-16, %r11b
	jb	.LBB36_51
	movzbl	3(%rdx), %r11d
	addq	$4, %rdx
	andl	$7, %r10d
	shll	$18, %r10d
	shll	$6, %eax
	andl	$63, %r11d
	orl	%eax, %r11d
	orl	%r10d, %r11d
	movl	%r11d, %eax
	jmp	.LBB36_52
.LBB36_50:
	addq	$2, %rdx
	shll	$6, %r10d
	orl	%esi, %r10d
	movl	%r10d, %eax
	jmp	.LBB36_52
.LBB36_51:
	addq	$3, %rdx
	shll	$12, %r10d
	orl	%r10d, %eax
.LBB36_52:
	leal	-65(%rax), %r10d
	andl	$-34, %r10d
	addl	$10, %r10d
	leal	-48(%rax), %r11d
	cmpl	$58, %eax
	cmovael	%r10d, %r11d
	cmpl	$15, %r11d
	jbe	.LBB36_44
.LBB36_53:
	movq	%r9, %rdi
.LBB36_54:
	testq	%rcx, %rcx
	je	.LBB36_56
	movl	$2, %r8d
	movq	%r14, %rcx
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.49(%rip), %rdx
	movq	-8(%rbp), %rax
	callq	*24(%rax)
	testb	%al, %al
	jne	.LBB36_174
.LBB36_56:
	cmpq	$1, %rdi
	movq	%r12, -56(%rbp)
	jbe	.LBB36_60
	cmpw	$9311, (%r13)
	jne	.LBB36_60
	cmpb	$-64, 1(%r15,%rbx)
	jl	.LBB36_188
	leaq	(%r15,%rbx), %r13
	incq	%r13
	decq	%rdi
.LBB36_60:
	movq	%rdi, %r15
	movq	%r13, %r12
	testq	%rdi, %rdi
	je	.LBB36_65
	movzbl	(%r12), %eax
	cmpl	$36, %eax
	je	.LBB36_81
	cmpl	$46, %eax
	jne	.LBB36_65
	cmpq	$1, %r15
	jne	.LBB36_101
	movl	$1, %r8d
	movq	%r14, %rcx
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.140(%rip), %rdx
	movq	-8(%rbp), %rax
	callq	*24(%rax)
	testb	%al, %al
	je	.LBB36_153
	jmp	.LBB36_173
.LBB36_65:
	leaq	(%r12,%r15), %rax
	xorl	%r9d, %r9d
	movq	%r12, %rcx
.LBB36_66:
	cmpq	%rax, %rcx
	je	.LBB36_168
	movq	%r9, %rdi
	movb	(%rcx), %r8b
	movzbl	%r8b, %edx
	testb	%dl, %dl
	js	.LBB36_69
	leaq	1(%rcx), %r8
	jmp	.LBB36_74
.LBB36_69:
	movl	%edx, %r9d
	andl	$31, %r9d
	movzbl	1(%rcx), %r10d
	andl	$63, %r10d
	cmpb	$-33, %dl
	jbe	.LBB36_72
	movzbl	2(%rcx), %edx
	shll	$6, %r10d
	andl	$63, %edx
	orl	%r10d, %edx
	cmpb	$-16, %r8b
	jb	.LBB36_73
	leaq	4(%rcx), %r8
	movzbl	3(%rcx), %r10d
	andl	$7, %r9d
	shll	$18, %r9d
	shll	$6, %edx
	andl	$63, %r10d
	orl	%edx, %r10d
	orl	%r9d, %r10d
	movl	%r10d, %edx
	jmp	.LBB36_74
.LBB36_72:
	leaq	2(%rcx), %r8
	shll	$6, %r9d
	orl	%r10d, %r9d
	movl	%r9d, %edx
	jmp	.LBB36_74
.LBB36_73:
	leaq	3(%rcx), %r8
	shll	$12, %r9d
	orl	%r9d, %edx
.LBB36_74:
	cmpl	$36, %edx
	je	.LBB36_76
	movq	%rdi, %r9
	subq	%rcx, %r9
	addq	%r8, %r9
	movq	%r8, %rcx
	cmpl	$46, %edx
	jne	.LBB36_66
.LBB36_76:
	testq	%rdi, %rdi
	je	.LBB36_96
	cmpq	%r15, %rdi
	jae	.LBB36_97
	cmpb	$-65, (%r12,%rdi)
	jle	.LBB36_170
	movq	%r14, %rcx
	movq	%r12, %rdx
	movq	%rdi, %r8
	movq	-8(%rbp), %rax
	callq	*24(%rax)
	testb	%al, %al
	jne	.LBB36_173
	cmpb	$-64, (%r12,%rdi)
	jge	.LBB36_100
	jmp	.LBB36_185
.LBB36_81:
	cmpq	$1, %r15
	je	.LBB36_83
	cmpb	$-65, 1(%r12)
	jle	.LBB36_187
.LBB36_83:
	leaq	-1(%r15), %rdi
	leaq	1(%r12), %rbx
	xorl	%r13d, %r13d
.LBB36_84:
	movq	%rdi, %r8
	subq	%r13, %r8
	leaq	(%rbx,%r13), %rax
	cmpq	$15, %r8
	ja	.LBB36_90
	xorl	%edx, %edx
	testq	%r8, %r8
	je	.LBB36_89
.LBB36_86:
	cmpb	$36, (%rax,%rdx)
	je	.LBB36_91
	incq	%rdx
	cmpq	%rdx, %r8
	jne	.LBB36_86
	movq	%r8, %rdx
.LBB36_89:
	xorl	%eax, %eax
	jmp	.LBB36_92
.LBB36_90:
	movb	$36, %cl
	movq	%rax, %rdx
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice6memchr14memchr_aligned
	jmp	.LBB36_92
.LBB36_91:
	movl	$1, %eax
.LBB36_92:
	cmpq	$1, %rax
	jne	.LBB36_168
	leaq	(%rdx,%r13), %r9
	cmpq	%rdi, %r9
	jae	.LBB36_95
	cmpb	$36, (%rbx,%r9)
	je	.LBB36_106
.LBB36_95:
	addq	%rdx, %r13
	incq	%r13
	cmpq	%r13, %rdi
	jae	.LBB36_84
	jmp	.LBB36_168
.LBB36_96:
	movq	%r14, %rcx
	movq	%r12, %rdx
	xorl	%r8d, %r8d
	movq	-8(%rbp), %rax
	callq	*24(%rax)
	movl	$0, %edi
	jmp	.LBB36_99
.LBB36_97:
	jne	.LBB36_170
	movq	%r14, %rcx
	movq	%r12, %rdx
	movq	%r15, %r8
	movq	-8(%rbp), %rax
	callq	*24(%rax)
	movq	%r15, %rdi
.LBB36_99:
	testb	%al, %al
	jne	.LBB36_173
.LBB36_100:
	subq	%rdi, %r15
	addq	%rdi, %r12
	jmp	.LBB36_154
.LBB36_101:
	movb	1(%r12), %cl
	cmpb	$-65, %cl
	jle	.LBB36_186
	movzbl	%cl, %eax
	testb	%cl, %cl
	jns	.LBB36_146
	andl	$31, %eax
	movzbl	2(%r12), %r8d
	andl	$63, %r8d
	cmpb	$-33, %cl
	jbe	.LBB36_114
	movzbl	3(%r12), %edx
	shll	$6, %r8d
	andl	$63, %edx
	orl	%r8d, %edx
	cmpb	$-16, %cl
	jb	.LBB36_145
	movzbl	4(%r12), %ecx
	andl	$7, %eax
	shll	$18, %eax
	shll	$6, %edx
	andl	$63, %ecx
	orl	%edx, %ecx
	orl	%ecx, %eax
	jmp	.LBB36_146
.LBB36_106:
	movb	(%rbx), %al
	cmpb	$-64, %al
	jl	.LBB36_178
	leaq	2(%r9), %r13
	movq	%r15, %rdi
	subq	%r13, %rdi
	jbe	.LBB36_109
	cmpb	$-64, (%r12,%r13)
	jl	.LBB36_196
.LBB36_109:
	addq	%r12, %r13
	cmpq	$1, %r9
	je	.LBB36_122
	cmpq	$2, %r9
	je	.LBB36_115
	testq	%r9, %r9
	je	.LBB36_168
.LBB36_112:
	cmpb	$117, %al
	jne	.LBB36_168
	cmpb	$-64, 2(%r12)
	jge	.LBB36_124
	jmp	.LBB36_197
.LBB36_114:
	shll	$6, %eax
	orl	%r8d, %eax
	jmp	.LBB36_146
.LBB36_115:
	cmpw	$20563, (%rbx)
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.137(%rip), %rdx
	je	.LBB36_137
	cmpw	$20546, (%rbx)
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.61(%rip), %rdx
	je	.LBB36_137
	cmpw	$18002, (%rbx)
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.58(%rip), %rdx
	je	.LBB36_137
	cmpw	$21580, (%rbx)
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.55(%rip), %rdx
	je	.LBB36_137
	cmpw	$21575, (%rbx)
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.57(%rip), %rdx
	je	.LBB36_137
	cmpw	$20556, (%rbx)
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.64(%rip), %rdx
	je	.LBB36_137
	cmpw	$20562, (%rbx)
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.26(%rip), %rdx
	jne	.LBB36_112
	jmp	.LBB36_137
.LBB36_122:
	movzbl	%al, %eax
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.65(%rip), %rdx
	cmpl	$67, %eax
	je	.LBB36_137
	cmpl	$117, %eax
	jne	.LBB36_168
.LBB36_124:
	addq	%r9, %rbx
	leaq	-1(%r9), %rcx
	leaq	2(%r12), %rdx
	movq	%rdx, %r10
.LBB36_125:
	movq	%r10, %rax
	cmpq	%rbx, %r10
	je	.LBB36_134
	movb	(%rax), %r10b
	movzbl	%r10b, %r8d
	testb	%r8b, %r8b
	js	.LBB36_128
	leaq	1(%rax), %r10
	jmp	.LBB36_133
.LBB36_128:
	movl	%r8d, %r11d
	andl	$31, %r11d
	movzbl	1(%rax), %esi
	andl	$63, %esi
	cmpb	$-33, %r8b
	jbe	.LBB36_131
	movzbl	2(%rax), %r8d
	shll	$6, %esi
	andl	$63, %r8d
	orl	%esi, %r8d
	cmpb	$-16, %r10b
	jb	.LBB36_132
	leaq	4(%rax), %r10
	movzbl	3(%rax), %esi
	andl	$7, %r11d
	shll	$18, %r11d
	shll	$6, %r8d
	andl	$63, %esi
	orl	%r8d, %esi
	orl	%r11d, %esi
	movl	%esi, %r8d
	jmp	.LBB36_133
.LBB36_131:
	leaq	2(%rax), %r10
	shll	$6, %r11d
	orl	%esi, %r11d
	movl	%r11d, %r8d
	jmp	.LBB36_133
.LBB36_132:
	leaq	3(%rax), %r10
	shll	$12, %r11d
	orl	%r11d, %r8d
.LBB36_133:
	leal	-58(%r8), %r11d
	cmpl	$-10, %r11d
	setb	%r11b
	addl	$-103, %r8d
	cmpl	$-6, %r8d
	setb	%r8b
	andb	%r11b, %r8b
	cmpb	$1, %r8b
	jne	.LBB36_125
.LBB36_134:
	cmpq	$2, %r9
	je	.LBB36_138
	cmpq	$1, %r9
	je	.LBB36_168
	movb	(%rdx), %r8b
	jmp	.LBB36_140
.LBB36_137:
	movl	$1, %r8d
	movq	%r14, %rcx
	movq	-8(%rbp), %rax
	callq	*24(%rax)
	jmp	.LBB36_166
.LBB36_138:
	movzbl	(%rdx), %r8d
	cmpl	$43, %r8d
	je	.LBB36_168
	cmpl	$45, %r8d
	je	.LBB36_168
.LBB36_140:
	xorl	%r9d, %r9d
	cmpb	$43, %r8b
	sete	%r9b
	subq	%r9, %rcx
	addq	%r9, %rdx
	cmpq	$9, %rcx
	jae	.LBB36_155
	xorl	%r8d, %r8d
	testq	%rcx, %rcx
	je	.LBB36_159
	xorl	%r9d, %r9d
.LBB36_143:
	movzbl	(%rdx,%r9), %r11d
	leal	-65(%r11), %esi
	andl	$-33, %esi
	addl	$10, %esi
	leal	-48(%r11), %r10d
	cmpl	$58, %r11d
	cmovael	%esi, %r10d
	cmpl	$15, %r10d
	ja	.LBB36_168
	shll	$4, %r8d
	orl	%r10d, %r8d
	incq	%r9
	cmpq	%r9, %rcx
	je	.LBB36_159
	jmp	.LBB36_143
.LBB36_145:
	shll	$12, %eax
	orl	%edx, %eax
.LBB36_146:
	movq	-8(%rbp), %rcx
	movq	24(%rcx), %r9
	cmpl	$46, %eax
	jne	.LBB36_151
	movl	$2, %r8d
	movq	%r14, %rcx
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.49(%rip), %rdx
	callq	*%r9
	testb	%al, %al
	jne	.LBB36_173
	cmpq	$3, %r15
	jb	.LBB36_150
	cmpb	$-64, 2(%r12)
	jl	.LBB36_195
.LBB36_150:
	addq	$-2, %r15
	addq	$2, %r12
	jmp	.LBB36_154
.LBB36_151:
	movl	$1, %r8d
	movq	%r14, %rcx
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.140(%rip), %rdx
	callq	*%r9
	testb	%al, %al
	jne	.LBB36_173
	cmpb	$-64, 1(%r12)
	jl	.LBB36_191
.LBB36_153:
	decq	%r15
	incq	%r12
.LBB36_154:
	movq	%r12, %r13
	movq	%r15, %rdi
	jmp	.LBB36_60
.LBB36_155:
	xorl	%r10d, %r10d
	xorl	%r9d, %r9d
.LBB36_156:
	movzbl	(%rdx,%r9), %esi
	leal	-65(%rsi), %r11d
	leal	-48(%rsi), %r8d
	cmpl	$268435455, %r10d
	ja	.LBB36_167
	andl	$-33, %r11d
	addl	$10, %r11d
	cmpb	$58, %sil
	cmovael	%r11d, %r8d
	cmpl	$16, %r8d
	jae	.LBB36_168
	shll	$4, %r10d
	orl	%r10d, %r8d
	incq	%r9
	movl	%r8d, %r10d
	cmpq	%r9, %rcx
	jne	.LBB36_156
.LBB36_159:
	shlq	$32, %r8
.LBB36_160:
	testb	$1, %r8b
	jne	.LBB36_168
	movq	%r8, %rcx
	shrq	$32, %rcx
	movl	%ecx, %edx
	xorl	$55296, %edx
	addl	$-1114112, %edx
	cmpl	$-1112064, %edx
	jb	.LBB36_168
	cmpq	%rbx, %rax
	jne	.LBB36_168
	movl	%ecx, -32(%rbp)
	movq	%r8, %rax
	shrq	$37, %rax
	je	.LBB36_168
	movabsq	$-545460846592, %rax
	addq	%rax, %r8
	shrq	$32, %r8
	cmpl	$33, %r8d
	jb	.LBB36_168
	leaq	-32(%rbp), %rcx
	movq	-48(%rbp), %rdx
	callq	_RNvXsk_NtCs8xEFJqa6dYS_4core3fmtcNtB5_7Display3fmt
.LBB36_166:
	testb	%al, %al
	je	.LBB36_60
	jmp	.LBB36_173
.LBB36_167:
	andl	$-34, %r11d
	addl	$10, %r11d
	cmpb	$58, %sil
	cmovael	%r11d, %r8d
	xorl	%ecx, %ecx
	cmpl	$16, %r8d
	setb	%cl
	shll	$8, %ecx
	addq	$257, %rcx
	movq	%rcx, %r8
	jmp	.LBB36_160
.LBB36_168:
	movq	%r14, %rcx
	movq	%r12, %rdx
	movq	%r15, %r8
	movq	-8(%rbp), %rax
	callq	*24(%rax)
	testb	%al, %al
	movq	-24(%rbp), %rdx
	movq	-64(%rbp), %rax
	movq	-56(%rbp), %r15
	je	.LBB36_1
	jmp	.LBB36_174
.LBB36_169:
	movl	$0, 4(%rbp)
	jmp	.LBB36_174
.LBB36_170:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.124(%rip), %rax
	movq	%rax, 32(%rsp)
	movq	%r12, %rcx
	movq	%r15, %rdx
	xorl	%r8d, %r8d
.LBB36_171:
	movq	%rdi, %r9
.LBB36_172:
	callq	_RNvNtCs8xEFJqa6dYS_4core3str16slice_error_fail
	ud2
.LBB36_173:
	movb	$1, %al
	movl	%eax, 4(%rbp)
.LBB36_174:
	movl	4(%rbp), %eax
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
.LBB36_175:
	addb	$-48, %dl
	xorl	%r9d, %r9d
	cmpb	$10, %dl
	adcb	$1, %r9b
	jmp	.LBB36_177
.LBB36_176:
	movb	$2, %r9b
.LBB36_177:
	leaq	-9(%rbp), %r8
	movb	%r9b, (%r8)
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.119(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.37(%rip), %rcx
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.38(%rip), %r9
	movl	$43, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core6result13unwrap_failed
	ud2
.LBB36_178:
	incq	%r9
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.127(%rip), %rax
	movq	%rax, 32(%rsp)
	movl	$1, %r8d
	movq	%r12, %rcx
	movq	%r15, %rdx
	jmp	.LBB36_172
.LBB36_179:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.116(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB36_180:
	subq	%rbx, %rdx
	addq	%rbx, %r15
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.117(%rip), %rax
	movq	%rax, 32(%rsp)
	movl	$1, %r8d
	movq	%r15, %rcx
	movq	%rdx, %r9
	jmp	.LBB36_172
.LBB36_181:
	movb	$1, %r9b
	jmp	.LBB36_177
.LBB36_182:
	xorl	%r9d, %r9d
	jmp	.LBB36_177
.LBB36_183:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.118(%rip), %rax
	movq	%rax, 32(%rsp)
	movq	%r15, %rcx
	xorl	%r8d, %r8d
	movq	%rbx, %r9
	jmp	.LBB36_172
.LBB36_184:
	subq	%rbx, %r13
	addq	%rbx, %r15
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.120(%rip), %rcx
	movq	%rcx, 32(%rsp)
	movq	%r15, %rcx
	movq	%r13, %rdx
	movq	%rax, %r8
	movq	%r13, %r9
	jmp	.LBB36_172
.LBB36_185:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.125(%rip), %rax
	movq	%rax, 32(%rsp)
	movq	%r12, %rcx
	movq	%r15, %rdx
	movq	%rdi, %r8
	jmp	.LBB36_194
.LBB36_186:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.138(%rip), %rax
	jmp	.LBB36_192
.LBB36_187:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.126(%rip), %rax
	jmp	.LBB36_192
.LBB36_188:
	addq	%rbx, %r15
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.123(%rip), %rax
	movq	%rax, 32(%rsp)
	movl	$1, %r8d
	movq	%r15, %rcx
	movq	%rdi, %rdx
	jmp	.LBB36_171
.LBB36_189:
	addq	%rbx, %r15
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.109(%rip), %rax
	movq	%rax, 32(%rsp)
	movl	$1, %r8d
	movq	%r15, %rcx
.LBB36_190:
	movq	%r9, %rdx
	jmp	.LBB36_172
.LBB36_191:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.141(%rip), %rax
.LBB36_192:
	movq	%rax, 32(%rsp)
	movl	$1, %r8d
.LBB36_193:
	movq	%r12, %rcx
	movq	%r15, %rdx
.LBB36_194:
	movq	%r15, %r9
	jmp	.LBB36_172
.LBB36_195:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.139(%rip), %rax
	movq	%rax, 32(%rsp)
	movl	$2, %r8d
	jmp	.LBB36_193
.LBB36_196:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.128(%rip), %rax
	movq	%rax, 32(%rsp)
	movq	%r12, %rcx
	movq	%r15, %rdx
	movq	%r13, %r8
	jmp	.LBB36_194
.LBB36_197:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.136(%rip), %rax
	movq	%rax, 32(%rsp)
	movl	$1, %r8d
	movq	%rbx, %rcx
	jmp	.LBB36_190
.Lfunc_end36:
	.seh_endproc

	.def	_RNvXNtNtCs8xEFJqa6dYS_4core3str4iterNtB2_5CharsNtNtNtNtB6_4iter6traits8iterator8Iterator5count;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXNtNtCs8xEFJqa6dYS_4core3str4iterNtB2_5CharsNtNtNtNtB6_4iter6traits8iterator8Iterator5count,unique,39
_RNvXNtNtCs8xEFJqa6dYS_4core3str4iterNtB2_5CharsNtNtNtNtB6_4iter6traits8iterator8Iterator5count:
.Lfunc_begin37:
	movq	%rdx, %rax
	subq	%rcx, %rdx
	cmpq	$32, %rdx
	jae	_RNvNtNtCs8xEFJqa6dYS_4core3str5count14do_count_chars
	cmpq	%rcx, %rax
	je	.LBB37_2
	xorl	%eax, %eax
	xorl	%r8d, %r8d
.LBB37_4:
	xorl	%r9d, %r9d
	cmpb	$-64, (%rcx,%r8)
	setge	%r9b
	addq	%r9, %rax
	incq	%r8
	cmpq	%r8, %rdx
	jne	.LBB37_4
	retq
.LBB37_2:
	xorl	%eax, %eax
	retq
.Lfunc_end37:

	.def	_RNvXNtNtNtCs8xEFJqa6dYS_4core4iter7sources7from_fnINtB2_6FromFnNCNvMs1_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB17_10HexNibbles19try_parse_str_charss0_0ENtNtNtB6_6traits8iterator8Iterator4nextB19_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXNtNtNtCs8xEFJqa6dYS_4core4iter7sources7from_fnINtB2_6FromFnNCNvMs1_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB17_10HexNibbles19try_parse_str_charss0_0ENtNtNtB6_6traits8iterator8Iterator4nextB19_,unique,40
_RNvXNtNtNtCs8xEFJqa6dYS_4core4iter7sources7from_fnINtB2_6FromFnNCNvMs1_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB17_10HexNibbles19try_parse_str_charss0_0ENtNtNtB6_6traits8iterator8Iterator4nextB19_:
.Lfunc_begin38:
.seh_proc _RNvXNtNtNtCs8xEFJqa6dYS_4core4iter7sources7from_fnINtB2_6FromFnNCNvMs1_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB17_10HexNibbles19try_parse_str_charss0_0ENtNtNtB6_6traits8iterator8Iterator4nextB19_
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
	subq	$128, %rsp
	.seh_stackalloc 128
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	movq	8(%rcx), %rdx
	movq	32(%rcx), %r9
	movl	$-2, %eax
	subq	%r9, %rdx
	jb	.LBB38_12
	movq	(%rcx), %r10
	leaq	(%r10,%r9), %rax
	movq	%rax, (%rcx)
	movq	%rdx, 8(%rcx)
	cmpq	$2, %r9
	jne	.LBB38_30
	movzbl	(%r10), %r8d
	leal	-65(%r8), %r11d
	andl	$-33, %r11d
	addl	$10, %r11d
	leal	-48(%r8), %eax
	cmpl	$58, %r8d
	cmovael	%r11d, %eax
	cmpl	$15, %eax
	ja	.LBB38_31
	movzbl	1(%r10), %r8d
	leal	-65(%r8), %esi
	andl	$-33, %esi
	addl	$10, %esi
	leal	-48(%r8), %r11d
	cmpl	$58, %r8d
	cmovael	%esi, %r11d
	cmpl	$16, %r11d
	jae	.LBB38_31
	shlb	$4, %al
	orb	%al, %r11b
	js	.LBB38_5
	leaq	-4(%rbp), %rax
	movb	%r11b, (%rax)
	movw	$0, 1(%rax)
	movb	$0, 3(%rax)
	movq	%rax, -24(%rbp)
	movq	$1, -16(%rbp)
	movl	$1, %r8d
.LBB38_14:
	leaq	-96(%rbp), %rsi
	leaq	-4(%rbp), %rdx
	movq	%rsi, %rcx
	callq	_RNvNtNtCs8xEFJqa6dYS_4core3str8converts9from_utf8
	cmpb	$0, (%rsi)
	je	.LBB38_15
.LBB38_11:
	movl	$-1, %eax
	jmp	.LBB38_12
.LBB38_5:
	movl	$-1, %eax
	cmpb	$-64, %r11b
	jb	.LBB38_12
	movl	$2, %r8d
	cmpb	$-32, %r11b
	jb	.LBB38_9
	movl	$3, %r8d
	cmpb	$-16, %r11b
	jb	.LBB38_9
	movl	$4, %r8d
	cmpb	$-8, %r11b
	jae	.LBB38_12
.LBB38_9:
	leaq	-3(%rbp), %rax
	movb	%r11b, -1(%rax)
	movw	$0, (%rax)
	movb	$0, 2(%rax)
	leaq	-4(%rbp), %r11
	movq	%r11, -24(%rbp)
	movq	%r8, -16(%rbp)
	leaq	-2(,%r8,2), %r11
	addq	%r10, %r9
	addq	$2, %r9
	xorl	%r10d, %r10d
.LBB38_10:
	leaq	(%rdx,%r10), %rsi
	cmpq	$2, %rsi
	jb	.LBB38_11
	leaq	(%rdx,%r10), %rsi
	addq	$-2, %rsi
	movq	%r9, (%rcx)
	movq	%rsi, 8(%rcx)
	movzbl	-2(%r9), %edi
	leal	-65(%rdi), %ebx
	andl	$-33, %ebx
	addl	$10, %ebx
	leal	-48(%rdi), %esi
	cmpl	$58, %edi
	cmovael	%ebx, %esi
	cmpl	$15, %esi
	ja	.LBB38_31
	movzbl	-1(%r9), %ebx
	leal	-65(%rbx), %r14d
	andl	$-33, %r14d
	addl	$10, %r14d
	leal	-48(%rbx), %edi
	cmpl	$58, %ebx
	cmovael	%r14d, %edi
	cmpl	$16, %edi
	jae	.LBB38_31
	shlb	$4, %sil
	orb	%sil, %dil
	movb	%dil, (%rax)
	addq	$-2, %r10
	incq	%rax
	addq	$2, %r9
	movq	%r11, %rsi
	addq	%r10, %rsi
	jne	.LBB38_10
	jmp	.LBB38_14
.LBB38_15:
	movq	-88(%rbp), %rcx
	movq	-80(%rbp), %rax
	movq	%rcx, -40(%rbp)
	movq	%rax, -32(%rbp)
	leaq	(%rcx,%rax), %rdx
	testq	%rax, %rax
	je	.LBB38_26
	movzbl	(%rcx), %eax
	testb	%al, %al
	js	.LBB38_18
	leaq	1(%rcx), %r9
	jmp	.LBB38_23
.LBB38_18:
	movl	%eax, %r8d
	andl	$31, %r8d
	movzbl	1(%rcx), %r11d
	andl	$63, %r11d
	cmpb	$-33, %al
	jbe	.LBB38_19
	movzbl	2(%rcx), %r10d
	shll	$6, %r11d
	andl	$63, %r10d
	orl	%r11d, %r10d
	cmpb	$-16, %al
	jb	.LBB38_21
	leaq	4(%rcx), %r9
	movzbl	3(%rcx), %eax
	andl	$7, %r8d
	shll	$18, %r8d
	shll	$6, %r10d
	andl	$63, %eax
	orl	%r10d, %eax
	orl	%r8d, %eax
	jmp	.LBB38_23
.LBB38_19:
	leaq	2(%rcx), %r9
	shll	$6, %r8d
	orl	%r11d, %r8d
	movl	%r8d, %eax
	jmp	.LBB38_23
.LBB38_21:
	leaq	3(%rcx), %r9
	shll	$12, %r8d
	orl	%r8d, %r10d
	movl	%r10d, %eax
.LBB38_23:
	cmpq	%rdx, %r9
	jne	.LBB38_24
.LBB38_12:
	.seh_startepilogue
	addq	$128, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.LBB38_31:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.18(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB38_30:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.16(%rip), %rcx
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.17(%rip), %r8
	movl	$40, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking5panic
	ud2
.LBB38_24:
	movb	(%r9), %al
	testb	%al, %al
	jns	.LBB38_26
	cmpb	$-32, %al
.LBB38_26:
	callq	_RNvXNtNtCs8xEFJqa6dYS_4core3str4iterNtB2_5CharsNtNtNtNtB6_4iter6traits8iterator8Iterator5count
	leaq	-48(%rbp), %rcx
	movq	%rax, (%rcx)
	leaq	-24(%rbp), %rax
	leaq	-96(%rbp), %rdx
	movq	%rax, (%rdx)
	leaq	_RNvXs1h_NtCs8xEFJqa6dYS_4core3fmtQShNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle(%rip), %rax
	movq	%rax, 8(%rdx)
	leaq	-40(%rbp), %rax
	movq	%rax, 16(%rdx)
	leaq	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtReNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle(%rip), %rax
	movq	%rax, 24(%rdx)
	movq	%rcx, 32(%rdx)
	leaq	_RNvXsi_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impjNtB9_7Display3fmt(%rip), %rax
	movq	%rax, 40(%rdx)
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.14(%rip), %rcx
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.15(%rip), %r8
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking9panic_fmt
	ud2
.Lfunc_end38:
	.seh_endproc

	.def	_RNvXs0_CseL4M8JimfzJ_14rustc_demangleINtB5_21SizeLimitedFmtAdapterQNtNtCs8xEFJqa6dYS_4core3fmt9FormatterENtB15_5Write9write_strB5_;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs0_CseL4M8JimfzJ_14rustc_demangleINtB5_21SizeLimitedFmtAdapterQNtNtCs8xEFJqa6dYS_4core3fmt9FormatterENtB15_5Write9write_strB5_,unique,41
	.globl	_RNvXs0_CseL4M8JimfzJ_14rustc_demangleINtB5_21SizeLimitedFmtAdapterQNtNtCs8xEFJqa6dYS_4core3fmt9FormatterENtB15_5Write9write_strB5_
_RNvXs0_CseL4M8JimfzJ_14rustc_demangleINtB5_21SizeLimitedFmtAdapterQNtNtCs8xEFJqa6dYS_4core3fmt9FormatterENtB15_5Write9write_strB5_:
.Lfunc_begin39:
	movq	8(%rcx), %rax
	subq	%r8, %rax
	setb	%r9b
	orb	(%rcx), %r9b
	movzbl	%r9b, %r9d
	movl	%r9d, %r10d
	andl	$1, %r10d
	movq	%r10, (%rcx)
	movq	%rax, 8(%rcx)
	testb	$1, %r9b
	je	.LBB39_2
	movb	$1, %al
	retq
.LBB39_2:
	movq	16(%rcx), %rax
	movq	(%rax), %rcx
	movq	8(%rax), %rax
	movq	24(%rax), %rax
	rex64 jmpq	*%rax
.Lfunc_end39:

	.def	_RNvXs0_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_5IdentNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs0_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_5IdentNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt,unique,42
	.globl	_RNvXs0_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_5IdentNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt
_RNvXs0_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_5IdentNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt:
.Lfunc_begin40:
.seh_proc _RNvXs0_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_5IdentNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt
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
	subq	$616, %rsp
	.seh_stackalloc 616
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	movq	%rdx, %rsi
	movq	%rcx, %r12
	leaq	-96(%rbp), %rcx
	movl	$512, %r8d
	xorl	%edx, %edx
	callq	memset
	movq	24(%r12), %rcx
	movq	%rcx, 440(%rbp)
	testq	%rcx, %rcx
	je	.LBB40_1
	movq	%rsi, 448(%rbp)
	movq	16(%r12), %rax
	movq	%rax, 456(%rbp)
	movb	(%rax), %bl
	movq	(%r12), %rcx
	movq	8(%r12), %rax
	testq	%rax, %rax
	movq	%rcx, 424(%rbp)
	movq	%rax, 416(%rbp)
	je	.LBB40_3
	addq	%rcx, %rax
	xorl	%r11d, %r11d
.LBB40_9:
	movb	(%rcx), %r9b
	movzbl	%r9b, %edx
	testb	%dl, %dl
	js	.LBB40_11
	incq	%rcx
	jmp	.LBB40_16
.LBB40_11:
	movl	%edx, %r8d
	andl	$31, %r8d
	movzbl	1(%rcx), %r10d
	andl	$63, %r10d
	cmpb	$-33, %dl
	jbe	.LBB40_12
	movzbl	2(%rcx), %edx
	shll	$6, %r10d
	andl	$63, %edx
	orl	%r10d, %edx
	cmpb	$-16, %r9b
	jb	.LBB40_14
	movzbl	3(%rcx), %r9d
	addq	$4, %rcx
	andl	$7, %r8d
	shll	$18, %r8d
	shll	$6, %edx
	andl	$63, %r9d
	orl	%edx, %r9d
	orl	%r8d, %r9d
	movl	%r9d, %edx
	jmp	.LBB40_16
.LBB40_12:
	addq	$2, %rcx
	shll	$6, %r8d
	orl	%r10d, %r8d
	movl	%r8d, %edx
	jmp	.LBB40_16
.LBB40_14:
	addq	$3, %rcx
	shll	$12, %r8d
	orl	%r8d, %edx
.LBB40_16:
	cmpq	$128, %r11
	je	.LBB40_47
	movl	%edx, -96(%rbp,%r11,4)
	incq	%r11
	cmpq	%rax, %rcx
	je	.LBB40_4
	jmp	.LBB40_9
.LBB40_1:
	movq	(%r12), %rdx
	movq	8(%r12), %r8
	movq	(%rsi), %rcx
	movq	8(%rsi), %rax
	movq	24(%rax), %rax
.LBB40_53:
	.seh_startepilogue
	addq	$616, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r13
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	rex64 jmpq	*%rax
.LBB40_3:
	xorl	%r11d, %r11d
.LBB40_4:
	movq	440(%rbp), %rax
	movq	456(%rbp), %rdi
	addq	%rdi, %rax
	movq	%rax, 432(%rbp)
	leaq	4(,%r11,4), %rax
	movq	%rax, 472(%rbp)
	movl	$700, %eax
	movq	%rax, 464(%rbp)
	movl	$72, %r14d
	movl	$128, %r12d
	movl	$26, %esi
	xorl	%ecx, %ecx
.LBB40_5:
	incq	%rdi
	movl	$1, %r9d
	xorl	%eax, %eax
	movl	$36, %r15d
	xorl	%r8d, %r8d
.LBB40_6:
	movq	%r15, %rdx
	subq	%r14, %rdx
	movl	$0, %r13d
	cmovaeq	%rdx, %r13
	cmpq	$1, %r13
	adcq	$0, %r13
	cmpq	$26, %r13
	cmovaeq	%rsi, %r13
	testb	$1, %al
	je	.LBB40_7
	cmpq	432(%rbp), %rdi
	je	.LBB40_47
	movb	(%rdi), %al
	incq	%rdi
	jmp	.LBB40_20
.LBB40_7:
	movl	%ebx, %eax
.LBB40_20:
	leal	-97(%rax), %edx
	cmpb	$26, %dl
	jb	.LBB40_23
	leal	-48(%rax), %edx
	cmpb	$9, %dl
	ja	.LBB40_47
	addb	$-22, %al
	movl	%eax, %edx
.LBB40_23:
	movzbl	%dl, %r10d
	movq	%r10, %rax
	mulq	%r9
	jo	.LBB40_47
	addq	%rax, %r8
	jb	.LBB40_47
	cmpq	%r10, %r13
	ja	.LBB40_46
	movl	$36, %edx
	subq	%r13, %rdx
	movq	%r9, %rax
	mulq	%rdx
	jo	.LBB40_47
	movq	%rax, %r9
	addq	$36, %r15
	movb	$1, %al
	jmp	.LBB40_6
.LBB40_46:
	addq	%r8, %rcx
	jb	.LBB40_47
	leaq	1(%r11), %r10
	movq	%rcx, %rax
	xorl	%edx, %edx
	divq	%r10
	addq	%rax, %r12
	jb	.LBB40_47
	movq	%r12, %rax
	shrq	$32, %rax
	jne	.LBB40_47
	movl	%r12d, %eax
	xorl	$55296, %eax
	addl	$-1114112, %eax
	cmpl	$-1112064, %eax
	jb	.LBB40_47
	cmpq	$127, %r11
	ja	.LBB40_47
	movq	%rdx, %rcx
	cmpq	%rdx, %r11
	jbe	.LBB40_33
.LBB40_35:
	movl	-100(%rbp,%r11,4), %eax
	movl	%eax, -96(%rbp,%r11,4)
	decq	%r11
	cmpq	%rcx, %r11
	ja	.LBB40_35
	jmp	.LBB40_36
.LBB40_33:
	cmpq	$128, %rcx
	jae	.LBB40_34
.LBB40_36:
	movl	%r12d, -96(%rbp,%rcx,4)
	cmpq	432(%rbp), %rdi
	movabsq	$-1581149492032247281, %rbx
	je	.LBB40_42
	movq	%r8, %rax
	xorl	%edx, %edx
	divq	464(%rbp)
	movq	%rax, %r8
	xorl	%edx, %edx
	divq	%r10
	movq	%rax, %r9
	addq	%r8, %r9
	cmpq	$456, %r9
	jb	.LBB40_38
	xorl	%r11d, %r11d
.LBB40_40:
	movq	%r9, %rax
	mulq	%rbx
	movq	%rdx, %r8
	shrq	$5, %r8
	addq	$36, %r11
	cmpq	$15959, %r9
	movq	%r8, %r9
	ja	.LBB40_40
	jmp	.LBB40_41
.LBB40_38:
	movq	%r9, %r8
	xorl	%r11d, %r11d
.LBB40_41:
	incq	%rcx
	movb	(%rdi), %bl
	leal	(,%r8,4), %eax
	leal	(%rax,%rax,8), %eax
	addl	$38, %r8d
	xorl	%edx, %edx
	divw	%r8w
	movzwl	%ax, %r14d
	addq	%r11, %r14
	addq	$4, 472(%rbp)
	movl	$2, %eax
	movq	%rax, 464(%rbp)
	movq	%r10, %r11
	jmp	.LBB40_5
.LBB40_47:
	movq	448(%rbp), %rax
	movq	(%rax), %r14
	movq	8(%rax), %rax
	movq	24(%rax), %rax
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.30(%rip), %rdx
	movl	$9, %r8d
	movq	%r14, %rcx
	movq	%rax, %rsi
	callq	*%rax
	movb	$1, %r13b
	testb	%al, %al
	jne	.LBB40_45
	movq	416(%rbp), %r8
	testq	%r8, %r8
	je	.LBB40_51
	movq	%r14, %rcx
	movq	424(%rbp), %rdx
	movq	%rsi, %rdi
	callq	*%rsi
	testb	%al, %al
	jne	.LBB40_45
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.24(%rip), %rdx
	movl	$1, %r8d
	movq	%r14, %rcx
	callq	*%rdi
	testb	%al, %al
	jne	.LBB40_45
.LBB40_51:
	movq	%r14, %rcx
	movq	456(%rbp), %rdx
	movq	440(%rbp), %r8
	movq	%rsi, %rdi
	callq	*%rsi
	testb	%al, %al
	je	.LBB40_52
.LBB40_45:
	movl	%r13d, %eax
	.seh_startepilogue
	addq	$616, %rsp
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
.LBB40_52:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.31(%rip), %rdx
	movl	$1, %r8d
	movq	%r14, %rcx
	movq	%rdi, %rax
	jmp	.LBB40_53
.LBB40_42:
	leaq	484(%rbp), %rsi
	movq	448(%rbp), %rdi
	leaq	-96(%rbp), %rbx
	movq	472(%rbp), %r14
.LBB40_43:
	movl	(%rbx), %eax
	movl	%eax, 484(%rbp)
	movq	%rsi, %rcx
	movq	%rdi, %rdx
	callq	_RNvXsk_NtCs8xEFJqa6dYS_4core3fmtcNtB5_7Display3fmt
	movl	%eax, %r13d
	testb	%al, %al
	jne	.LBB40_45
	addq	$4, %rbx
	addq	$-4, %r14
	jne	.LBB40_43
	jmp	.LBB40_45
.LBB40_34:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.13(%rip), %r8
	movl	$128, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	ud2
.Lfunc_end40:
	.seh_endproc

	.def	_RNvXs1_CseL4M8JimfzJ_14rustc_demangleNtB5_8DemangleNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1_CseL4M8JimfzJ_14rustc_demangleNtB5_8DemangleNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt,unique,43
	.globl	_RNvXs1_CseL4M8JimfzJ_14rustc_demangleNtB5_8DemangleNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt
_RNvXs1_CseL4M8JimfzJ_14rustc_demangleNtB5_8DemangleNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt:
.Lfunc_begin41:
.seh_proc _RNvXs1_CseL4M8JimfzJ_14rustc_demangleNtB5_8DemangleNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt
	pushq	%rbp
	.seh_pushreg %rbp
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
	movq	%rdx, %rdi
	movq	%rcx, %rsi
	cmpl	$1, (%rcx)
	jne	.LBB41_3
	leaq	8(%rsi), %rax
	btl	$23, 16(%rdi)
	movq	%rax, -8(%rbp)
	movq	$0, -32(%rbp)
	movq	$1000000, -24(%rbp)
	movq	%rdi, -16(%rbp)
	leaq	-8(%rbp), %rax
	leaq	-48(%rbp), %r9
	jb	.LBB41_6
	movq	%rax, (%r9)
	leaq	_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtRNtCseL4M8JimfzJ_14rustc_demangle13DemangleStyleNtB6_7Display3fmtBy_(%rip), %rax
	movq	%rax, 8(%r9)
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.143.llvm.10832689424213744105(%rip), %rdx
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.142.llvm.10832689424213744105(%rip), %r8
	jmp	.LBB41_7
.LBB41_3:
	movq	32(%rsi), %rdx
	movq	40(%rsi), %r8
	movq	(%rdi), %rbx
	movq	8(%rdi), %rax
	movq	24(%rax), %rdi
	movq	%rbx, %rcx
	callq	*%rdi
	movl	%eax, %ecx
	movb	$1, %al
	testb	%cl, %cl
	je	.LBB41_4
	jmp	.LBB41_5
.LBB41_6:
	movq	%rax, (%r9)
	leaq	_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtRNtCseL4M8JimfzJ_14rustc_demangle13DemangleStyleNtB6_7Display3fmtBy_(%rip), %rax
	movq	%rax, 8(%r9)
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.143.llvm.10832689424213744105(%rip), %rdx
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.144.llvm.10832689424213744105(%rip), %r8
.LBB41_7:
	leaq	-32(%rbp), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core3fmt5write
	cmpl	$1, -32(%rbp)
	jne	.LBB41_10
	testb	%al, %al
	je	.LBB41_13
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.145.llvm.10832689424213744105(%rip), %rdx
	movl	$20, %r8d
	callq	*24(%rax)
.LBB41_10:
	testb	%al, %al
	je	.LBB41_11
	movb	$1, %al
	jmp	.LBB41_5
.LBB41_11:
	movq	(%rdi), %rbx
	movq	8(%rdi), %rax
	movq	24(%rax), %rdi
.LBB41_4:
	movq	48(%rsi), %rdx
	movq	56(%rsi), %r8
	movq	%rbx, %rcx
	callq	*%rdi
	nop
.LBB41_5:
	.seh_startepilogue
	addq	$104, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB41_13:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.147.llvm.10832689424213744105(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.146.llvm.10832689424213744105(%rip), %rcx
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.39.llvm.10832689424213744105(%rip), %r9
	leaq	7(%rbp), %r8
	movl	$55, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core6result13unwrap_failed
	ud2
.Lfunc_end41:
	.seh_endproc

	.def	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRNtNtNtB8_3num5error12IntErrorKindNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRNtNtNtB8_3num5error12IntErrorKindNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle,unique,44
	.globl	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRNtNtNtB8_3num5error12IntErrorKindNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle
_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRNtNtNtB8_3num5error12IntErrorKindNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle:
.Lfunc_begin42:
	movq	(%rcx), %rax
	movzbl	(%rax), %eax
	leaq	switch.table._RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRNtNtNtB8_3num5error12IntErrorKindNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle(%rip), %rcx
	movq	(%rcx,%rax,8), %r8
	leaq	switch.table._RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRNtNtNtB8_3num5error12IntErrorKindNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle.42.rel(%rip), %rcx
	movslq	(%rcx,%rax,4), %rax
	addq	%rcx, %rax
	movq	(%rdx), %rcx
	movq	8(%rdx), %rdx
	movq	24(%rdx), %r9
	movq	%rax, %rdx
	rex64 jmpq	*%r9
.Lfunc_end42:

	.def	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtReNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtReNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle,unique,45
	.globl	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtReNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle
_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtReNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle:
.Lfunc_begin43:
	movq	%rdx, %r8
	movq	(%rcx), %rax
	movq	8(%rcx), %rdx
	movq	%rax, %rcx
	jmp	_RNvXsh_NtCs8xEFJqa6dYS_4core3fmteNtB5_5Debug3fmt
.Lfunc_end43:

	.def	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRhNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRhNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle,unique,46
	.globl	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRhNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle
_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRhNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle:
.Lfunc_begin44:
	movq	(%rcx), %rcx
	movl	16(%rdx), %eax
	btl	$25, %eax
	jb	_RNvXse_NtNtCs8xEFJqa6dYS_4core3fmt3numhNtB7_8LowerHex3fmt
	btl	$26, %eax
	jb	_RNvXsg_NtNtCs8xEFJqa6dYS_4core3fmt3numhNtB7_8UpperHex3fmt
	jmp	_RNvXNtNtNtCs8xEFJqa6dYS_4core3fmt3num3imphNtB6_7Display3fmt
.Lfunc_end44:

	.def	_RNvXs1h_NtCs8xEFJqa6dYS_4core3fmtQShNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1h_NtCs8xEFJqa6dYS_4core3fmtQShNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle,unique,47
	.globl	_RNvXs1h_NtCs8xEFJqa6dYS_4core3fmtQShNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle
_RNvXs1h_NtCs8xEFJqa6dYS_4core3fmtQShNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle:
.Lfunc_begin45:
	movq	%rdx, %r8
	movq	(%rcx), %rax
	movq	8(%rcx), %rdx
	movq	%rax, %rcx
	jmp	_RNvXsr_NtCs8xEFJqa6dYS_4core3fmtShNtB5_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle
.Lfunc_end45:

	.def	_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtRNtCseL4M8JimfzJ_14rustc_demangle13DemangleStyleNtB6_7Display3fmtBy_;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtRNtCseL4M8JimfzJ_14rustc_demangle13DemangleStyleNtB6_7Display3fmtBy_,unique,48
	.globl	_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtRNtCseL4M8JimfzJ_14rustc_demangle13DemangleStyleNtB6_7Display3fmtBy_
_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtRNtCseL4M8JimfzJ_14rustc_demangle13DemangleStyleNtB6_7Display3fmtBy_:
.Lfunc_begin46:
	movq	(%rcx), %rcx
	jmp	_RNvXs_CseL4M8JimfzJ_14rustc_demangleNtB4_13DemangleStyleNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt
.Lfunc_end46:

	.def	_RNvXs8_CseL4M8JimfzJ_14rustc_demangleNtB5_18SizeLimitExhaustedNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt.llvm.10832689424213744105;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs8_CseL4M8JimfzJ_14rustc_demangleNtB5_18SizeLimitExhaustedNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt.llvm.10832689424213744105,unique,49
	.globl	_RNvXs8_CseL4M8JimfzJ_14rustc_demangleNtB5_18SizeLimitExhaustedNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt.llvm.10832689424213744105
_RNvXs8_CseL4M8JimfzJ_14rustc_demangleNtB5_18SizeLimitExhaustedNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt.llvm.10832689424213744105:
.Lfunc_begin47:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.149(%rip), %rdx
	movl	$18, %r8d
	rex64 jmpq	*%rax
.Lfunc_end47:

	.def	_RNvXsK_NtCs8xEFJqa6dYS_4core3fmtNtB5_5ErrorNtB5_5Debug3fmt;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXsK_NtCs8xEFJqa6dYS_4core3fmtNtB5_5ErrorNtB5_5Debug3fmt,unique,50
_RNvXsK_NtCs8xEFJqa6dYS_4core3fmtNtB5_5ErrorNtB5_5Debug3fmt:
.Lfunc_begin48:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.150(%rip), %rdx
	movl	$5, %r8d
	rex64 jmpq	*%rax
.Lfunc_end48:

	.def	_RNvXs_CseL4M8JimfzJ_14rustc_demangleNtB4_13DemangleStyleNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs_CseL4M8JimfzJ_14rustc_demangleNtB4_13DemangleStyleNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt,unique,51
	.globl	_RNvXs_CseL4M8JimfzJ_14rustc_demangleNtB4_13DemangleStyleNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt
_RNvXs_CseL4M8JimfzJ_14rustc_demangleNtB4_13DemangleStyleNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt:
.Lfunc_begin49:
.seh_proc _RNvXs_CseL4M8JimfzJ_14rustc_demangleNtB4_13DemangleStyleNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$80, %rsp
	.seh_stackalloc 80
	leaq	80(%rsp), %rbp
	.seh_setframe %rbp, 80
	.seh_endprologue
	cmpq	$0, (%rcx)
	je	.LBB49_1
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbp
	.seh_endepilogue
	jmp	_RNvXNtCseL4M8JimfzJ_14rustc_demangle6legacyNtB2_8DemangleNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt
.LBB49_1:
	movups	8(%rcx), %xmm0
	leaq	-48(%rbp), %rcx
	movups	%xmm0, (%rcx)
	movq	$0, 16(%rcx)
	xorl	%eax, %eax
	movl	%eax, 24(%rcx)
	movq	%rdx, 32(%rcx)
	movl	%eax, 40(%rcx)
	movb	$1, %dl
	callq	_RNvMs4_NtCseL4M8JimfzJ_14rustc_demangle2v0NtB5_7Printer10print_path
	nop
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end49:
	.seh_endproc

	.def	_RNvXsd_NtNtCs8xEFJqa6dYS_4core3num5errorNtB5_13ParseIntErrorNtNtB9_3fmt5Debug3fmt;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXsd_NtNtCs8xEFJqa6dYS_4core3num5errorNtB5_13ParseIntErrorNtNtB9_3fmt5Debug3fmt,unique,52
_RNvXsd_NtNtCs8xEFJqa6dYS_4core3num5errorNtB5_13ParseIntErrorNtNtB9_3fmt5Debug3fmt:
.Lfunc_begin50:
.seh_proc _RNvXsd_NtNtCs8xEFJqa6dYS_4core3num5errorNtB5_13ParseIntErrorNtNtB9_3fmt5Debug3fmt
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$64, %rsp
	.seh_stackalloc 64
	leaq	64(%rsp), %rbp
	.seh_setframe %rbp, 64
	.seh_endprologue
	movq	%rdx, %rax
	leaq	-8(%rbp), %rdx
	movq	%rcx, (%rdx)
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.148(%rip), %rcx
	movq	%rcx, 48(%rsp)
	movq	%rdx, 40(%rsp)
	movq	$4, 32(%rsp)
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.152(%rip), %rdx
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.153(%rip), %r9
	movl	$13, %r8d
	movq	%rax, %rcx
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter26debug_struct_field1_finish
	nop
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end50:
	.seh_endproc

	.def	_RNvXsr_NtCs8xEFJqa6dYS_4core3fmtShNtB5_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXsr_NtCs8xEFJqa6dYS_4core3fmtShNtB5_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle,unique,53
	.globl	_RNvXsr_NtCs8xEFJqa6dYS_4core3fmtShNtB5_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle
_RNvXsr_NtCs8xEFJqa6dYS_4core3fmtShNtB5_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle:
.Lfunc_begin51:
.seh_proc _RNvXsr_NtCs8xEFJqa6dYS_4core3fmtShNtB5_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle
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
	movq	%r8, %rbx
	movq	%rdx, %rsi
	movq	%rcx, %rdi
	movq	(%r8), %rcx
	movq	8(%r8), %rax
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.207.llvm.17490583796818522722(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	movq	%rbx, -8(%rbp)
	movb	%al, (%rbp)
	movb	$0, 1(%rbp)
	testq	%rsi, %rsi
	je	.LBB51_4
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.9(%rip), %rbx
	leaq	-8(%rbp), %r14
	leaq	-16(%rbp), %r15
.LBB51_2:
	movq	%rdi, -16(%rbp)
	incq	%rdi
	movq	%r14, %rcx
	movq	%r15, %rdx
	movq	%rbx, %r8
	callq	_RNvMs5_NtNtCs8xEFJqa6dYS_4core3fmt8buildersNtB5_9DebugList5entry
	decq	%rsi
	jne	.LBB51_2
	movb	$1, %al
	cmpb	$0, (%rbp)
	jne	.LBB51_6
.LBB51_5:
	movq	-8(%rbp), %rax
	movq	(%rax), %rcx
	movq	8(%rax), %rax
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.63.llvm.17490583796818522722(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	nop
.LBB51_6:
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
.LBB51_4:
	movl	%eax, %ecx
	movb	$1, %al
	testb	%cl, %cl
	je	.LBB51_5
	jmp	.LBB51_6
.Lfunc_end51:
	.seh_endproc

	.def	_RNvXss_NtCs8xEFJqa6dYS_4core3fmtuNtB5_5Debug3fmt;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXss_NtCs8xEFJqa6dYS_4core3fmtuNtB5_5Debug3fmt,unique,54
_RNvXss_NtCs8xEFJqa6dYS_4core3fmtuNtB5_5Debug3fmt:
.Lfunc_begin52:
	movq	%rdx, %rcx
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.84(%rip), %rdx
	movl	$2, %r8d
	jmp	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
.Lfunc_end52:

	.def	_RNvXsv_NtNtCs8xEFJqa6dYS_4core3str7patternNtB5_11StrSearcherNtB5_8Searcher4next;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXsv_NtNtCs8xEFJqa6dYS_4core3str7patternNtB5_11StrSearcherNtB5_8Searcher4next,unique,55
_RNvXsv_NtNtCs8xEFJqa6dYS_4core3str7patternNtB5_11StrSearcherNtB5_8Searcher4next:
.Lfunc_begin53:
.seh_proc _RNvXsv_NtNtCs8xEFJqa6dYS_4core3str7patternNtB5_11StrSearcherNtB5_8Searcher4next
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
	leaq	80(%rsp), %rbp
	.seh_setframe %rbp, 80
	.seh_endprologue
	cmpl	$1, (%rdx)
	jne	.LBB53_21
	movq	40(%rdx), %r8
	movq	80(%rdx), %r10
	movl	$2, %r11d
	cmpq	%r10, %r8
	je	.LBB53_57
	movq	72(%rdx), %r11
	movq	96(%rdx), %rax
	leaq	(%rax,%r8), %r15
	decq	%r15
	movq	%r10, %r9
	cmpq	%r10, %r15
	jae	.LBB53_26
	movq	56(%rdx), %r13
	movq	88(%rdx), %rbx
	movq	32(%rdx), %r9
	movq	%r9, -32(%rbp)
	movq	8(%rdx), %r12
	movq	24(%rdx), %r9
	movq	%rax, %rsi
	subq	%r9, %rsi
	movq	%rsi, -8(%rbp)
	addq	%r8, %r9
	movq	%r9, -16(%rbp)
	leaq	(%rax,%r8), %r9
	movq	%r9, (%rbp)
	movq	%r8, %r9
	subq	%r12, %r9
	movq	%r9, -24(%rbp)
	leaq	(%r11,%r8), %r14
	movq	%r13, %rsi
	movq	%r8, %r9
.LBB53_4:
	cmpq	%r9, %r8
	jne	.LBB53_26
	movzbl	(%r11,%r15), %r9d
	movq	-32(%rbp), %rdi
	btq	%r9, %rdi
	jae	.LBB53_11
	cmpq	%r12, %rsi
	movq	%r12, %r15
	cmovaq	%rsi, %r15
	cmpq	$-1, %r13
	cmoveq	%r12, %r15
.LBB53_7:
	cmpq	%rax, %r15
	jae	.LBB53_13
	leaq	1(%r15), %r9
	movb	(%rbx,%r15), %dil
	cmpb	(%r14,%r15), %dil
	movq	%r9, %r15
	je	.LBB53_7
	addq	-24(%rbp), %r9
	movq	%r9, 40(%rdx)
	cmpq	$-1, %r13
	je	.LBB53_19
	xorl	%r15d, %r15d
	jmp	.LBB53_18
.LBB53_11:
	leaq	(%rax,%r8), %r9
	movq	%r9, 40(%rdx)
	cmpq	$-1, %r13
	je	.LBB53_19
	xorl	%r15d, %r15d
	leaq	(%rax,%r8), %r9
	jmp	.LBB53_18
.LBB53_13:
	cmpq	$-1, %r13
	movq	%rsi, %r15
	movl	$0, %r9d
	cmoveq	%r9, %r15
	leaq	-1(%r12), %r9
.LBB53_14:
	leaq	1(%r9), %rdi
	cmpq	%rdi, %r15
	jae	.LBB53_33
	cmpq	%rax, %r9
	jae	.LBB53_58
	movb	(%rbx,%r9), %dil
	cmpb	(%r14,%r9), %dil
	leaq	-1(%r9), %r9
	je	.LBB53_14
	movq	-16(%rbp), %r9
	movq	%r9, 40(%rdx)
	movq	-8(%rbp), %r15
	cmpq	$-1, %r13
	je	.LBB53_19
.LBB53_18:
	movq	%r15, 56(%rdx)
	movq	%r15, %rsi
.LBB53_19:
	leaq	-1(%rax), %rdi
	leaq	(%r9,%rdi), %r15
	cmpq	%r10, %r15
	jb	.LBB53_4
	leaq	8(%rcx), %rax
	leaq	16(%rcx), %rsi
	movq	%r10, %r9
	jmp	.LBB53_27
.LBB53_21:
	movl	$2, %r11d
	cmpb	$0, 26(%rdx)
	jne	.LBB53_57
	movb	24(%rdx), %r10b
	movl	%r10d, %eax
	xorb	$1, %al
	movb	%al, 24(%rdx)
	movq	8(%rdx), %r8
	movq	72(%rdx), %rax
	movq	80(%rdx), %r9
	testq	%r8, %r8
	je	.LBB53_37
	cmpq	%r9, %r8
	jae	.LBB53_36
	cmpb	$-64, (%rax,%r8)
	jge	.LBB53_37
.LBB53_25:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.160(%rip), %rcx
	movq	%rcx, 32(%rsp)
	movq	%rax, %rcx
	movq	%r9, %rdx
	callq	_RNvNtCs8xEFJqa6dYS_4core3str16slice_error_fail
	ud2
.LBB53_26:
	leaq	8(%rcx), %rax
	leaq	16(%rcx), %rsi
	testq	%r9, %r9
	je	.LBB53_44
.LBB53_27:
	movq	%r9, %rdi
.LBB53_28:
	cmpq	%r10, %rdi
	jae	.LBB53_30
	cmpb	$-65, (%r11,%rdi)
	jle	.LBB53_31
	jmp	.LBB53_45
.LBB53_30:
	je	.LBB53_46
.LBB53_31:
	incq	%rdi
	jne	.LBB53_28
	xorl	%r10d, %r10d
	jmp	.LBB53_46
.LBB53_33:
	movq	(%rbp), %rax
	movq	%rax, 40(%rdx)
	cmpq	$-1, %r13
	je	.LBB53_35
	movq	$0, 56(%rdx)
.LBB53_35:
	movq	%r8, 8(%rcx)
	movq	(%rbp), %rax
	movq	%rax, 16(%rcx)
	jmp	.LBB53_52
.LBB53_36:
	jne	.LBB53_25
.LBB53_37:
	cmpq	%r9, %r8
	jne	.LBB53_40
	testb	%r10b, %r10b
	jne	.LBB53_51
	movb	$1, 26(%rdx)
	jmp	.LBB53_57
.LBB53_40:
	movb	(%rax,%r8), %bl
	movzbl	%bl, %r9d
	testb	%r9b, %r9b
	jns	.LBB53_50
	movl	%r9d, %r11d
	andl	$31, %r11d
	movzbl	1(%rax,%r8), %esi
	andl	$63, %esi
	cmpb	$-33, %r9b
	jbe	.LBB53_48
	movzbl	2(%rax,%r8), %r9d
	shll	$6, %esi
	andl	$63, %r9d
	orl	%esi, %r9d
	cmpb	$-16, %bl
	jb	.LBB53_49
	movzbl	3(%rax,%r8), %eax
	andl	$7, %r11d
	shll	$18, %r11d
	shll	$6, %r9d
	andl	$63, %eax
	orl	%r9d, %eax
	orl	%r11d, %eax
	movl	%eax, %r9d
	jmp	.LBB53_50
.LBB53_44:
	xorl	%r9d, %r9d
	xorl	%r10d, %r10d
	jmp	.LBB53_47
.LBB53_45:
	movq	%rdi, %r10
.LBB53_46:
	cmpq	%r10, %r9
	cmovbeq	%r10, %r9
.LBB53_47:
	movq	%r9, 40(%rdx)
	movq	%r8, (%rax)
	movq	%r10, (%rsi)
	movl	$1, %r11d
	jmp	.LBB53_57
.LBB53_48:
	shll	$6, %r11d
	orl	%esi, %r11d
	movl	%r11d, %r9d
	jmp	.LBB53_50
.LBB53_49:
	shll	$12, %r11d
	orl	%r11d, %r9d
.LBB53_50:
	testb	%r10b, %r10b
	je	.LBB53_53
.LBB53_51:
	movq	%r8, 8(%rcx)
	movq	%r8, 16(%rcx)
.LBB53_52:
	xorl	%r11d, %r11d
	jmp	.LBB53_57
.LBB53_53:
	movl	$1, %r11d
	movl	$1, %eax
	cmpl	$128, %r9d
	jb	.LBB53_56
	movl	$2, %eax
	cmpl	$2048, %r9d
	jb	.LBB53_56
	cmpl	$65536, %r9d
	movl	$4, %eax
	sbbq	$0, %rax
.LBB53_56:
	addq	%r8, %rax
	movq	%rax, 8(%rdx)
	movq	%r8, 8(%rcx)
	movq	%rax, 16(%rcx)
.LBB53_57:
	movq	%r11, (%rcx)
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
.LBB53_58:
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.11(%rip), %r8
	movq	%r9, %rcx
	movq	%rax, %rdx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	ud2
.Lfunc_end53:
	.seh_endproc

	.def	_RNvYINtCseL4M8JimfzJ_14rustc_demangle21SizeLimitedFmtAdapterQNtNtCs8xEFJqa6dYS_4core3fmt9FormatterENtBZ_5Write10write_charB5_;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvYINtCseL4M8JimfzJ_14rustc_demangle21SizeLimitedFmtAdapterQNtNtCs8xEFJqa6dYS_4core3fmt9FormatterENtBZ_5Write10write_charB5_,unique,56
	.globl	_RNvYINtCseL4M8JimfzJ_14rustc_demangle21SizeLimitedFmtAdapterQNtNtCs8xEFJqa6dYS_4core3fmt9FormatterENtBZ_5Write10write_charB5_
_RNvYINtCseL4M8JimfzJ_14rustc_demangle21SizeLimitedFmtAdapterQNtNtCs8xEFJqa6dYS_4core3fmt9FormatterENtBZ_5Write10write_charB5_:
.Lfunc_begin54:
.seh_proc _RNvYINtCseL4M8JimfzJ_14rustc_demangle21SizeLimitedFmtAdapterQNtNtCs8xEFJqa6dYS_4core3fmt9FormatterENtBZ_5Write10write_charB5_
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$48, %rsp
	.seh_stackalloc 48
	leaq	48(%rsp), %rbp
	.seh_setframe %rbp, 48
	.seh_endprologue
	movl	$0, -4(%rbp)
	cmpl	$128, %edx
	jae	.LBB54_1
	movb	%dl, -4(%rbp)
	movl	$1, %r8d
	jmp	.LBB54_6
.LBB54_1:
	movl	%edx, %eax
	andb	$63, %al
	orb	$-128, %al
	movl	%edx, %r8d
	shrl	$6, %r8d
	cmpl	$2048, %edx
	jae	.LBB54_3
	orb	$-64, %r8b
	movb	%r8b, -4(%rbp)
	movb	%al, -3(%rbp)
	movl	$2, %r8d
	jmp	.LBB54_6
.LBB54_3:
	andb	$63, %r8b
	orb	$-128, %r8b
	movl	%edx, %r9d
	shrl	$12, %r9d
	cmpl	$65535, %edx
	ja	.LBB54_5
	orb	$-32, %r9b
	movb	%r9b, -4(%rbp)
	movb	%r8b, -3(%rbp)
	movb	%al, -2(%rbp)
	movl	$3, %r8d
	jmp	.LBB54_6
.LBB54_5:
	andb	$63, %r9b
	orb	$-128, %r9b
	shrl	$18, %edx
	orb	$-16, %dl
	movb	%dl, -4(%rbp)
	movb	%r9b, -3(%rbp)
	movb	%r8b, -2(%rbp)
	movb	%al, -1(%rbp)
	movl	$4, %r8d
.LBB54_6:
	movq	8(%rcx), %rax
	subq	%r8, %rax
	setb	%dl
	orb	(%rcx), %dl
	movzbl	%dl, %edx
	movl	%edx, %r9d
	andl	$1, %r9d
	movq	%r9, (%rcx)
	movq	%rax, 8(%rcx)
	movb	$1, %al
	testb	$1, %dl
	jne	.LBB54_8
	movq	16(%rcx), %rax
	movq	(%rax), %rcx
	movq	8(%rax), %rax
	leaq	-4(%rbp), %rdx
	callq	*24(%rax)
	nop
.LBB54_8:
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end54:
	.seh_endproc

	.def	_RNvYINtCseL4M8JimfzJ_14rustc_demangle21SizeLimitedFmtAdapterQNtNtCs8xEFJqa6dYS_4core3fmt9FormatterENtBZ_5Write9write_fmtB5_;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvYINtCseL4M8JimfzJ_14rustc_demangle21SizeLimitedFmtAdapterQNtNtCs8xEFJqa6dYS_4core3fmt9FormatterENtBZ_5Write9write_fmtB5_,unique,57
	.globl	_RNvYINtCseL4M8JimfzJ_14rustc_demangle21SizeLimitedFmtAdapterQNtNtCs8xEFJqa6dYS_4core3fmt9FormatterENtBZ_5Write9write_fmtB5_
_RNvYINtCseL4M8JimfzJ_14rustc_demangle21SizeLimitedFmtAdapterQNtNtCs8xEFJqa6dYS_4core3fmt9FormatterENtBZ_5Write9write_fmtB5_:
.Lfunc_begin55:
	movq	%r8, %r9
	movq	%rdx, %r8
	leaq	anon.5a58e618b243a32306ab8731d520f4a6.143.llvm.10832689424213744105(%rip), %rdx
	jmp	_RNvNtCs8xEFJqa6dYS_4core3fmt5write
.Lfunc_end55:

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.0,unique,58
anon.5a58e618b243a32306ab8731d520f4a6.0:
	.ascii	"{invalid syntax}"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.1,unique,59
anon.5a58e618b243a32306ab8731d520f4a6.1:
	.ascii	"{recursion limit reached}"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.2,unique,60
anon.5a58e618b243a32306ab8731d520f4a6.2:
	.byte	63

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.3,unique,61
anon.5a58e618b243a32306ab8731d520f4a6.3:
	.ascii	"`fmt::Error`s should be impossible without a `fmt::Formatter`"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.4,unique,62
anon.5a58e618b243a32306ab8731d520f4a6.4:
	.asciz	"/rust/deps\\rustc-demangle-0.1.27\\src\\v0.rs"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.5,unique,63
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.5:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.4
	.asciz	"*\000\000\000\000\000\000\000\207\002\000\000\021\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.6,unique,64
anon.5a58e618b243a32306ab8731d520f4a6.6:
	.ascii	"for<"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.7,unique,65
anon.5a58e618b243a32306ab8731d520f4a6.7:
	.ascii	"> "

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.8,unique,66
anon.5a58e618b243a32306ab8731d520f4a6.8:
	.ascii	", "

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.9,unique,67
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.9:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRhNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.10,unique,68
anon.5a58e618b243a32306ab8731d520f4a6.10:
	.asciz	"/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\str\\pattern.rs"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.11,unique,69
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.11:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.10
	.asciz	"O\000\000\000\000\000\000\000\363\005\000\000\024\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.12,unique,70
anon.5a58e618b243a32306ab8731d520f4a6.12:
	.ascii	"0123456789abcdef"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.13,unique,71
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.13:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.4
	.asciz	"*\000\000\000\000\000\000\000\212\000\000\000\r\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.14,unique,72
anon.5a58e618b243a32306ab8731d520f4a6.14:
	.asciz	"9internal error: entered unreachable code: str::from_utf8(\300\004) = \300\" was expected to have 1 char, but \300\021 chars were found"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.15,unique,73
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.15:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.4
	.asciz	"*\000\000\000\000\000\000\000\\\001\000\000\032\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.16,unique,74
anon.5a58e618b243a32306ab8731d520f4a6.16:
	.ascii	"internal error: entered unreachable code"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.17,unique,75
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.17:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.4
	.asciz	"*\000\000\000\000\000\000\0001\001\000\000\026\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.18,unique,76
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.18:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.4
	.asciz	"*\000\000\000\000\000\000\0004\001\000\000G\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.19,unique,77
anon.5a58e618b243a32306ab8731d520f4a6.19:
	.byte	67

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.20,unique,78
anon.5a58e618b243a32306ab8731d520f4a6.20:
	.ascii	"unsafe "

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.21,unique,79
anon.5a58e618b243a32306ab8731d520f4a6.21:
	.ascii	"extern \""

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.22,unique,80
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.22:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.4
	.asciz	"*\000\000\000\000\000\000\000\324\003\000\000-\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.23,unique,81
anon.5a58e618b243a32306ab8731d520f4a6.23:
	.ascii	"\" "

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.24,unique,82
anon.5a58e618b243a32306ab8731d520f4a6.24:
	.byte	45

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.25,unique,83
anon.5a58e618b243a32306ab8731d520f4a6.25:
	.ascii	"fn("

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.26,unique,84
anon.5a58e618b243a32306ab8731d520f4a6.26:
	.byte	41

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.27,unique,85
anon.5a58e618b243a32306ab8731d520f4a6.27:
	.ascii	" -> "

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.28,unique,86
anon.5a58e618b243a32306ab8731d520f4a6.28:
	.ascii	" + "

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.29,unique,87
anon.5a58e618b243a32306ab8731d520f4a6.29:
	.ascii	": "

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.30,unique,88
anon.5a58e618b243a32306ab8731d520f4a6.30:
	.ascii	"punycode{"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.31,unique,89
anon.5a58e618b243a32306ab8731d520f4a6.31:
	.byte	125

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.32,unique,90
anon.5a58e618b243a32306ab8731d520f4a6.32:
	.ascii	".llvm."

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.33.llvm.10832689424213744105,unique,91
	.globl	anon.5a58e618b243a32306ab8731d520f4a6.33.llvm.10832689424213744105
anon.5a58e618b243a32306ab8731d520f4a6.33.llvm.10832689424213744105:
	.asciz	"/rust/deps\\rustc-demangle-0.1.27\\src\\lib.rs"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.34,unique,92
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.34:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.33.llvm.10832689424213744105
	.asciz	"+\000\000\000\000\000\000\000b\000\000\000\033\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.35,unique,93
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.35:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.33.llvm.10832689424213744105
	.asciz	"+\000\000\000\000\000\000\000i\000\000\000\023\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.36,unique,94
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.36:
	.asciz	"\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\001\000\000\000\000\000\000"
	.quad	_RNvXss_NtCs8xEFJqa6dYS_4core3fmtuNtB5_5Debug3fmt

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.37,unique,95
anon.5a58e618b243a32306ab8731d520f4a6.37:
	.ascii	"called `Result::unwrap()` on an `Err` value"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.38,unique,96
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.38:
	.asciz	"\000\000\000\000\000\000\000\000\001\000\000\000\000\000\000\000\001\000\000\000\000\000\000"
	.quad	_RNvXsd_NtNtCs8xEFJqa6dYS_4core3num5errorNtB5_13ParseIntErrorNtNtB9_3fmt5Debug3fmt

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.39.llvm.10832689424213744105,unique,97
	.globl	anon.5a58e618b243a32306ab8731d520f4a6.39.llvm.10832689424213744105
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.39.llvm.10832689424213744105:
	.asciz	"\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\001\000\000\000\000\000\000"
	.quad	_RNvXs8_CseL4M8JimfzJ_14rustc_demangleNtB5_18SizeLimitExhaustedNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt.llvm.10832689424213744105

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.40,unique,98
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.40:
	.asciz	"\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\001\000\000\000\000\000\000"
	.quad	_RNvXsK_NtCs8xEFJqa6dYS_4core3fmtNtB5_5ErrorNtB5_5Debug3fmt

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.41,unique,99
anon.5a58e618b243a32306ab8731d520f4a6.41:
	.byte	48

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.42,unique,100
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.42:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.4
	.asciz	"*\000\000\000\000\000\000\000\036\001\000\0001\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.43,unique,101
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.43:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.4
	.asciz	"*\000\000\000\000\000\000\000\277\001\000\000\037\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.44,unique,102
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.44:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.4
	.asciz	"*\000\000\000\000\000\000\000\036\002\000\000\036\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.45,unique,103
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.45:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.4
	.asciz	"*\000\000\000\000\000\000\000#\002\000\000\"\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.46,unique,104
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.46:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.4
	.asciz	"*\000\000\000\000\000\000\000$\002\000\000%\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.47,unique,105
anon.5a58e618b243a32306ab8731d520f4a6.47:
	.byte	91

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.48,unique,106
anon.5a58e618b243a32306ab8731d520f4a6.48:
	.byte	93

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.49,unique,107
anon.5a58e618b243a32306ab8731d520f4a6.49:
	.zero	2,58

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.50,unique,108
anon.5a58e618b243a32306ab8731d520f4a6.50:
	.ascii	"::{"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.51,unique,109
anon.5a58e618b243a32306ab8731d520f4a6.51:
	.ascii	"closure"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.52,unique,110
anon.5a58e618b243a32306ab8731d520f4a6.52:
	.ascii	"shim"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.53,unique,111
anon.5a58e618b243a32306ab8731d520f4a6.53:
	.byte	58

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.54,unique,112
anon.5a58e618b243a32306ab8731d520f4a6.54:
	.byte	35

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.55,unique,113
anon.5a58e618b243a32306ab8731d520f4a6.55:
	.byte	60

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.56,unique,114
anon.5a58e618b243a32306ab8731d520f4a6.56:
	.ascii	" as "

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.57,unique,115
anon.5a58e618b243a32306ab8731d520f4a6.57:
	.byte	62

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.58,unique,116
anon.5a58e618b243a32306ab8731d520f4a6.58:
	.byte	38

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.59,unique,117
anon.5a58e618b243a32306ab8731d520f4a6.59:
	.byte	32

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.60,unique,118
anon.5a58e618b243a32306ab8731d520f4a6.60:
	.ascii	"mut "

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.61,unique,119
anon.5a58e618b243a32306ab8731d520f4a6.61:
	.byte	42

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.62,unique,120
anon.5a58e618b243a32306ab8731d520f4a6.62:
	.ascii	"const "

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.63,unique,121
anon.5a58e618b243a32306ab8731d520f4a6.63:
	.ascii	"; "

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.64,unique,122
anon.5a58e618b243a32306ab8731d520f4a6.64:
	.byte	40

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.65,unique,123
anon.5a58e618b243a32306ab8731d520f4a6.65:
	.byte	44

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.66,unique,124
anon.5a58e618b243a32306ab8731d520f4a6.66:
	.ascii	"dyn "

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.67,unique,125
anon.5a58e618b243a32306ab8731d520f4a6.67:
	.ascii	" is "

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.68,unique,126
anon.5a58e618b243a32306ab8731d520f4a6.68:
	.byte	95

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.69,unique,127
anon.5a58e618b243a32306ab8731d520f4a6.69:
	.ascii	"false"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.70,unique,128
anon.5a58e618b243a32306ab8731d520f4a6.70:
	.ascii	"true"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.71,unique,129
anon.5a58e618b243a32306ab8731d520f4a6.71:
	.byte	123

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.72,unique,130
anon.5a58e618b243a32306ab8731d520f4a6.72:
	.ascii	" { "

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.73,unique,131
anon.5a58e618b243a32306ab8731d520f4a6.73:
	.ascii	" }"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.74,unique,132
anon.5a58e618b243a32306ab8731d520f4a6.74:
	.ascii	" = "

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.75,unique,133
anon.5a58e618b243a32306ab8731d520f4a6.75:
	.ascii	"0x"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.76,unique,134
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.76:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.4
	.asciz	"*\000\000\000\000\000\000\000\361\004\000\000-\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.77,unique,135
anon.5a58e618b243a32306ab8731d520f4a6.77:
	.byte	39

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.78,unique,136
anon.5a58e618b243a32306ab8731d520f4a6.78:
	.ascii	"..="

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.79,unique,137
anon.5a58e618b243a32306ab8731d520f4a6.79:
	.ascii	" | "

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.80,unique,138
anon.5a58e618b243a32306ab8731d520f4a6.80:
	.ascii	"!null"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.81,unique,139
anon.5a58e618b243a32306ab8731d520f4a6.81:
	.ascii	"bool"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.82,unique,140
anon.5a58e618b243a32306ab8731d520f4a6.82:
	.ascii	"char"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.83,unique,141
anon.5a58e618b243a32306ab8731d520f4a6.83:
	.ascii	"str"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.84,unique,142
anon.5a58e618b243a32306ab8731d520f4a6.84:
	.ascii	"()"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.85,unique,143
anon.5a58e618b243a32306ab8731d520f4a6.85:
	.ascii	"i8"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.86,unique,144
anon.5a58e618b243a32306ab8731d520f4a6.86:
	.ascii	"i16"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.87,unique,145
anon.5a58e618b243a32306ab8731d520f4a6.87:
	.ascii	"i32"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.88,unique,146
anon.5a58e618b243a32306ab8731d520f4a6.88:
	.ascii	"i64"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.89,unique,147
anon.5a58e618b243a32306ab8731d520f4a6.89:
	.ascii	"i128"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.90,unique,148
anon.5a58e618b243a32306ab8731d520f4a6.90:
	.ascii	"isize"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.91,unique,149
anon.5a58e618b243a32306ab8731d520f4a6.91:
	.ascii	"u8"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.92,unique,150
anon.5a58e618b243a32306ab8731d520f4a6.92:
	.ascii	"u16"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.93,unique,151
anon.5a58e618b243a32306ab8731d520f4a6.93:
	.ascii	"u32"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.94,unique,152
anon.5a58e618b243a32306ab8731d520f4a6.94:
	.ascii	"u64"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.95,unique,153
anon.5a58e618b243a32306ab8731d520f4a6.95:
	.ascii	"u128"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.96,unique,154
anon.5a58e618b243a32306ab8731d520f4a6.96:
	.ascii	"usize"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.97,unique,155
anon.5a58e618b243a32306ab8731d520f4a6.97:
	.ascii	"f32"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.98,unique,156
anon.5a58e618b243a32306ab8731d520f4a6.98:
	.ascii	"f64"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.99,unique,157
anon.5a58e618b243a32306ab8731d520f4a6.99:
	.byte	33

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.100,unique,158
anon.5a58e618b243a32306ab8731d520f4a6.100:
	.zero	3,46

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.101,unique,159
anon.5a58e618b243a32306ab8731d520f4a6.101:
	.ascii	"_R"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.102,unique,160
anon.5a58e618b243a32306ab8731d520f4a6.102:
	.ascii	"__R"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.103,unique,161
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.103:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.4
	.asciz	"*\000\000\000\000\000\000\0002\000\000\000\023\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.104,unique,162
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.104:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.4
	.asciz	"*\000\000\000\000\000\000\000/\000\000\000\023\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.105,unique,163
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.105:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.4
	.asciz	"*\000\000\000\000\000\000\000+\000\000\000\023\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.106,unique,164
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.106:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.4
	.asciz	"*\000\000\000\000\000\000\000K\000\000\000\016\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.107,unique,165
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.107:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.4
	.asciz	"*\000\000\000\000\000\000\000Z\000\000\000(\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.108,unique,166
anon.5a58e618b243a32306ab8731d520f4a6.108:
	.asciz	"/rust/deps\\rustc-demangle-0.1.27\\src\\legacy.rs"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.109,unique,167
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.109:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.108
	.asciz	".\000\000\000\000\000\000\000f\000\000\000\034\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.110,unique,168
anon.5a58e618b243a32306ab8731d520f4a6.110:
	.ascii	"_ZN"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.111,unique,169
anon.5a58e618b243a32306ab8731d520f4a6.111:
	.ascii	"ZN"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.112,unique,170
anon.5a58e618b243a32306ab8731d520f4a6.112:
	.ascii	"__ZN"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.113,unique,171
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.113:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.108
	.asciz	".\000\000\000\000\000\000\000=\000\000\000\013\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.114,unique,172
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.114:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.108
	.asciz	".\000\000\000\000\000\000\000:\000\000\000\013\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.115,unique,173
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.115:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.108
	.asciz	".\000\000\000\000\000\000\0006\000\000\000\013\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.116,unique,174
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.116:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.108
	.asciz	".\000\000\000\000\000\000\000o\000\000\000'\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.117,unique,175
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.117:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.108
	.asciz	".\000\000\000\000\000\000\000p\000\000\000\035\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.118,unique,176
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.118:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.108
	.asciz	".\000\000\000\000\000\000\000r\000\000\000!\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.119,unique,177
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.119:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.108
	.asciz	".\000\000\000\000\000\000\000r\000\000\000H\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.120,unique,178
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.120:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.108
	.asciz	".\000\000\000\000\000\000\000s\000\000\000\032\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.122,unique,179
anon.5a58e618b243a32306ab8731d520f4a6.122:
	.ascii	"_$"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.123,unique,180
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.123:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.108
	.asciz	".\000\000\000\000\000\000\000~\000\000\000\035\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.124,unique,181
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.124:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.108
	.asciz	".\000\000\000\000\000\000\000\264\000\000\000&\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.125,unique,182
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.125:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.108
	.asciz	".\000\000\000\000\000\000\000\265\000\000\000!\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.126,unique,183
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.126:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.108
	.asciz	".\000\000\000\000\000\000\000\212\000\000\000I\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.127,unique,184
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.127:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.108
	.asciz	".\000\000\000\000\000\000\000\213\000\000\000\037\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.128,unique,185
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.128:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.108
	.asciz	".\000\000\000\000\000\000\000\213\000\000\000/\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.129,unique,186
anon.5a58e618b243a32306ab8731d520f4a6.129:
	.ascii	"SP"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.130,unique,187
anon.5a58e618b243a32306ab8731d520f4a6.130:
	.ascii	"BP"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.131,unique,188
anon.5a58e618b243a32306ab8731d520f4a6.131:
	.ascii	"RF"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.132,unique,189
anon.5a58e618b243a32306ab8731d520f4a6.132:
	.ascii	"LT"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.133,unique,190
anon.5a58e618b243a32306ab8731d520f4a6.133:
	.ascii	"GT"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.134,unique,191
anon.5a58e618b243a32306ab8731d520f4a6.134:
	.ascii	"LP"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.135,unique,192
anon.5a58e618b243a32306ab8731d520f4a6.135:
	.ascii	"RP"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.136,unique,193
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.136:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.108
	.asciz	".\000\000\000\000\000\000\000\235\000\000\0005\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.137,unique,194
anon.5a58e618b243a32306ab8731d520f4a6.137:
	.byte	64

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.138,unique,195
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.138:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.108
	.asciz	".\000\000\000\000\000\000\000\202\000\000\000,\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.139,unique,196
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.139:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.108
	.asciz	".\000\000\000\000\000\000\000\204\000\000\000%\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.140,unique,197
anon.5a58e618b243a32306ab8731d520f4a6.140:
	.byte	46

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.141,unique,198
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.141:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.108
	.asciz	".\000\000\000\000\000\000\000\207\000\000\000%\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.142.llvm.10832689424213744105,unique,199
	.globl	anon.5a58e618b243a32306ab8731d520f4a6.142.llvm.10832689424213744105
anon.5a58e618b243a32306ab8731d520f4a6.142.llvm.10832689424213744105:
	.asciz	"\300"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.143.llvm.10832689424213744105,unique,200
	.globl	anon.5a58e618b243a32306ab8731d520f4a6.143.llvm.10832689424213744105
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.143.llvm.10832689424213744105:
	.asciz	"\000\000\000\000\000\000\000\000\030\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNvXs0_CseL4M8JimfzJ_14rustc_demangleINtB5_21SizeLimitedFmtAdapterQNtNtCs8xEFJqa6dYS_4core3fmt9FormatterENtB15_5Write9write_strB5_
	.quad	_RNvYINtCseL4M8JimfzJ_14rustc_demangle21SizeLimitedFmtAdapterQNtNtCs8xEFJqa6dYS_4core3fmt9FormatterENtBZ_5Write10write_charB5_
	.quad	_RNvYINtCseL4M8JimfzJ_14rustc_demangle21SizeLimitedFmtAdapterQNtNtCs8xEFJqa6dYS_4core3fmt9FormatterENtBZ_5Write9write_fmtB5_

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.144.llvm.10832689424213744105,unique,201
	.globl	anon.5a58e618b243a32306ab8731d520f4a6.144.llvm.10832689424213744105
anon.5a58e618b243a32306ab8731d520f4a6.144.llvm.10832689424213744105:
	.asciz	"\301 \000\200`"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.145.llvm.10832689424213744105,unique,202
	.globl	anon.5a58e618b243a32306ab8731d520f4a6.145.llvm.10832689424213744105
anon.5a58e618b243a32306ab8731d520f4a6.145.llvm.10832689424213744105:
	.ascii	"{size limit reached}"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.146.llvm.10832689424213744105,unique,203
	.globl	anon.5a58e618b243a32306ab8731d520f4a6.146.llvm.10832689424213744105
anon.5a58e618b243a32306ab8731d520f4a6.146.llvm.10832689424213744105:
	.ascii	"`fmt::Error` from `SizeLimitedFmtAdapter` was discarded"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.147.llvm.10832689424213744105,unique,204
	.globl	anon.5a58e618b243a32306ab8731d520f4a6.147.llvm.10832689424213744105
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.147.llvm.10832689424213744105:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.33.llvm.10832689424213744105
	.asciz	"+\000\000\000\000\000\000\000S\001\000\000\036\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.148,unique,205
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.148:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRNtNtNtB8_3num5error12IntErrorKindNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.149,unique,206
anon.5a58e618b243a32306ab8731d520f4a6.149:
	.ascii	"SizeLimitExhausted"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.150,unique,207
anon.5a58e618b243a32306ab8731d520f4a6.150:
	.ascii	"Error"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.151,unique,208
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.151:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.10
	.asciz	"O\000\000\000\000\000\000\000\317\001\000\0007\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.152,unique,209
anon.5a58e618b243a32306ab8731d520f4a6.152:
	.ascii	"ParseIntError"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.153,unique,210
anon.5a58e618b243a32306ab8731d520f4a6.153:
	.ascii	"kind"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.154,unique,211
anon.5a58e618b243a32306ab8731d520f4a6.154:
	.ascii	"Empty"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.155,unique,212
anon.5a58e618b243a32306ab8731d520f4a6.155:
	.ascii	"InvalidDigit"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.156,unique,213
anon.5a58e618b243a32306ab8731d520f4a6.156:
	.ascii	"PosOverflow"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.157,unique,214
anon.5a58e618b243a32306ab8731d520f4a6.157:
	.ascii	"NegOverflow"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.158,unique,215
anon.5a58e618b243a32306ab8731d520f4a6.158:
	.ascii	"Zero"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.159,unique,216
anon.5a58e618b243a32306ab8731d520f4a6.159:
	.ascii	"NotAPowerOfTwo"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.160,unique,217
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.160:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.10
	.asciz	"O\000\000\000\000\000\000\000k\004\000\000$\000\000"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.161,unique,218
anon.5a58e618b243a32306ab8731d520f4a6.161:
	.asciz	"/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\ops\\function.rs"

	.section	.rdata,"dr",one_only,anon.5a58e618b243a32306ab8731d520f4a6.162,unique,219
	.p2align	3, 0x0
anon.5a58e618b243a32306ab8731d520f4a6.162:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.161
	.asciz	"P\000\000\000\000\000\000\000\246\000\000\000\005\000\000"

	.section	.rdata,"dr",one_only,switch.table._RNvNtCseL4M8JimfzJ_14rustc_demangle2v010basic_type,unique,220
	.p2align	3, 0x0
switch.table._RNvNtCseL4M8JimfzJ_14rustc_demangle2v010basic_type:
	.quad	2
	.quad	4
	.quad	4
	.quad	3
	.quad	3
	.quad	3
	.zero	8
	.quad	2
	.quad	5
	.quad	5
	.zero	8
	.quad	3
	.quad	3
	.quad	4
	.quad	4
	.quad	1
	.zero	8
	.zero	8
	.quad	3
	.quad	3
	.quad	2
	.quad	3
	.zero	8
	.quad	3
	.quad	3
	.quad	1

	.section	.rdata,"dr",one_only,switch.table._RNvNtCseL4M8JimfzJ_14rustc_demangle2v010basic_type.41,unique,221
	.p2align	3, 0x0
switch.table._RNvNtCseL4M8JimfzJ_14rustc_demangle2v010basic_type.41:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.85
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.81
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.82
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.98
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.83
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.97
	.quad	0
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.91
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.90
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.96
	.quad	0
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.87
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.93
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.89
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.95
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.68
	.quad	0
	.quad	0
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.86
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.92
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.84
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.100
	.quad	0
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.88
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.94
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.99

	.section	.rdata,"dr",one_only,switch.table._RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRNtNtNtB8_3num5error12IntErrorKindNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle,unique,222
	.p2align	3, 0x0
switch.table._RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRNtNtNtB8_3num5error12IntErrorKindNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle:
	.quad	5
	.quad	12
	.quad	11
	.quad	11
	.quad	4
	.quad	14

	.section	.rdata,"dr",one_only,switch.table._RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRNtNtNtB8_3num5error12IntErrorKindNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle.42.rel,unique,223
	.p2align	2, 0x0
switch.table._RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRNtNtNtB8_3num5error12IntErrorKindNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle.42.rel:
	.long	anon.5a58e618b243a32306ab8731d520f4a6.154-switch.table._RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRNtNtNtB8_3num5error12IntErrorKindNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle.42.rel
	.long	anon.5a58e618b243a32306ab8731d520f4a6.155-switch.table._RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRNtNtNtB8_3num5error12IntErrorKindNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle.42.rel
	.long	anon.5a58e618b243a32306ab8731d520f4a6.156-switch.table._RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRNtNtNtB8_3num5error12IntErrorKindNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle.42.rel
	.long	anon.5a58e618b243a32306ab8731d520f4a6.157-switch.table._RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRNtNtNtB8_3num5error12IntErrorKindNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle.42.rel
	.long	anon.5a58e618b243a32306ab8731d520f4a6.158-switch.table._RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRNtNtNtB8_3num5error12IntErrorKindNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle.42.rel
	.long	anon.5a58e618b243a32306ab8731d520f4a6.159-switch.table._RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRNtNtNtB8_3num5error12IntErrorKindNtB6_5Debug3fmtCseL4M8JimfzJ_14rustc_demangle.42.rel

	.section	.data,"dw",one_only,__imp_anon.5a58e618b243a32306ab8731d520f4a6.33.llvm.10832689424213744105,unique,224
	.globl	__imp_anon.5a58e618b243a32306ab8731d520f4a6.33.llvm.10832689424213744105
	.p2align	3, 0x0
__imp_anon.5a58e618b243a32306ab8731d520f4a6.33.llvm.10832689424213744105:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.33.llvm.10832689424213744105

	.section	.data,"dw",one_only,__imp_anon.5a58e618b243a32306ab8731d520f4a6.39.llvm.10832689424213744105,unique,225
	.globl	__imp_anon.5a58e618b243a32306ab8731d520f4a6.39.llvm.10832689424213744105
	.p2align	3, 0x0
__imp_anon.5a58e618b243a32306ab8731d520f4a6.39.llvm.10832689424213744105:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.39.llvm.10832689424213744105

	.section	.data,"dw",one_only,__imp_anon.5a58e618b243a32306ab8731d520f4a6.142.llvm.10832689424213744105,unique,226
	.globl	__imp_anon.5a58e618b243a32306ab8731d520f4a6.142.llvm.10832689424213744105
	.p2align	3, 0x0
__imp_anon.5a58e618b243a32306ab8731d520f4a6.142.llvm.10832689424213744105:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.142.llvm.10832689424213744105

	.section	.data,"dw",one_only,__imp_anon.5a58e618b243a32306ab8731d520f4a6.143.llvm.10832689424213744105,unique,227
	.globl	__imp_anon.5a58e618b243a32306ab8731d520f4a6.143.llvm.10832689424213744105
	.p2align	3, 0x0
__imp_anon.5a58e618b243a32306ab8731d520f4a6.143.llvm.10832689424213744105:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.143.llvm.10832689424213744105

	.section	.data,"dw",one_only,__imp_anon.5a58e618b243a32306ab8731d520f4a6.144.llvm.10832689424213744105,unique,228
	.globl	__imp_anon.5a58e618b243a32306ab8731d520f4a6.144.llvm.10832689424213744105
	.p2align	3, 0x0
__imp_anon.5a58e618b243a32306ab8731d520f4a6.144.llvm.10832689424213744105:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.144.llvm.10832689424213744105

	.section	.data,"dw",one_only,__imp_anon.5a58e618b243a32306ab8731d520f4a6.145.llvm.10832689424213744105,unique,229
	.globl	__imp_anon.5a58e618b243a32306ab8731d520f4a6.145.llvm.10832689424213744105
	.p2align	3, 0x0
__imp_anon.5a58e618b243a32306ab8731d520f4a6.145.llvm.10832689424213744105:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.145.llvm.10832689424213744105

	.section	.data,"dw",one_only,__imp_anon.5a58e618b243a32306ab8731d520f4a6.146.llvm.10832689424213744105,unique,230
	.globl	__imp_anon.5a58e618b243a32306ab8731d520f4a6.146.llvm.10832689424213744105
	.p2align	3, 0x0
__imp_anon.5a58e618b243a32306ab8731d520f4a6.146.llvm.10832689424213744105:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.146.llvm.10832689424213744105

	.section	.data,"dw",one_only,__imp_anon.5a58e618b243a32306ab8731d520f4a6.147.llvm.10832689424213744105,unique,231
	.globl	__imp_anon.5a58e618b243a32306ab8731d520f4a6.147.llvm.10832689424213744105
	.p2align	3, 0x0
__imp_anon.5a58e618b243a32306ab8731d520f4a6.147.llvm.10832689424213744105:
	.quad	anon.5a58e618b243a32306ab8731d520f4a6.147.llvm.10832689424213744105

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
	.asciz	"prototype.rustc_demangle-0d6817d2202cd839.rustc_demangle.abe928c6a278e2b5-cgu.0.rcgu.o.rcgu.o"
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
	.asciz	"/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\lib.rs\\@\\core.6380f46c71b215e4-cgu.0"
	.byte	242
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
