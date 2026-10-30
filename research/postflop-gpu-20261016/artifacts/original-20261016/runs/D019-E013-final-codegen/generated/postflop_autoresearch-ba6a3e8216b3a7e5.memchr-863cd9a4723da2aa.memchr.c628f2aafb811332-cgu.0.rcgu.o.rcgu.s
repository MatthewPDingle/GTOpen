	.def	@feat.00;
	.scl	3;
	.type	0;
	.endef
	.globl	@feat.00
@feat.00 = 0
	.file	"memchr.c628f2aafb811332-cgu.0"
	.def	_RNvMNtNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_644avx26memchrNtB2_3One14rfind_raw_avx2;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMNtNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_644avx26memchrNtB2_3One14rfind_raw_avx2,unique,0
	.p2align	4
_RNvMNtNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_644avx26memchrNtB2_3One14rfind_raw_avx2:
.Lfunc_begin0:
.seh_proc _RNvMNtNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_644avx26memchrNtB2_3One14rfind_raw_avx2
	subq	$24, %rsp
	.seh_stackalloc 24
	vmovdqa	%xmm6, (%rsp)
	.seh_savexmm %xmm6, 0
	.seh_endprologue
	vmovdqa	(%rcx), %ymm0
	vpcmpeqb	-32(%r8), %ymm0, %ymm1
	vpmovmskb	%ymm1, %eax
	testl	%eax, %eax
	je	.LBB0_2
	addq	$-32, %r8
	bsrl	%eax, %edx
	addq	%r8, %rdx
	movl	$1, %eax
	vmovaps	(%rsp), %xmm6
	.seh_startepilogue
	addq	$24, %rsp
	.seh_endepilogue
	vzeroupper
	retq
.LBB0_2:
	movq	%r8, %rcx
	subq	%rdx, %rcx
	movq	%r8, %rax
	andq	$-32, %rax
	cmpq	$127, %rcx
	seta	%r9b
	leaq	128(%rdx), %rcx
	cmpq	%rcx, %rax
	setae	%r10b
	andb	%r9b, %r10b
	cmpb	$1, %r10b
	jne	.LBB0_7
	movl	%r8d, %eax
	andl	$31, %eax
	subq	%rax, %r8
	addq	$-33, %r8
	.p2align	4
.LBB0_4:
	vpcmpeqb	-95(%r8), %ymm0, %ymm1
	vpcmpeqb	-63(%r8), %ymm0, %ymm2
	vpcmpeqb	-31(%r8), %ymm0, %ymm3
	vpcmpeqb	1(%r8), %ymm0, %ymm4
	vpor	%ymm2, %ymm1, %ymm5
	vpor	%ymm4, %ymm3, %ymm6
	vpor	%ymm5, %ymm6, %ymm5
	vpmovmskb	%ymm5, %eax
	testl	%eax, %eax
	jne	.LBB0_15
	leaq	-128(%r8), %rax
	addq	$-95, %r8
	cmpq	%rcx, %r8
	movq	%rax, %r8
	jae	.LBB0_4
	addq	$33, %rax
.LBB0_7:
	leaq	32(%rdx), %rcx
	.p2align	4
.LBB0_8:
	cmpq	%rcx, %rax
	jb	.LBB0_13
	vpcmpeqb	-32(%rax), %ymm0, %ymm1
	addq	$-32, %rax
	vpmovmskb	%ymm1, %r8d
	testl	%r8d, %r8d
	je	.LBB0_8
	bsrl	%r8d, %edx
	addq	%rax, %rdx
	movl	$1, %eax
	vmovaps	(%rsp), %xmm6
	.seh_startepilogue
	addq	$24, %rsp
	.seh_endepilogue
	vzeroupper
	retq
.LBB0_13:
	cmpq	%rdx, %rax
	jbe	.LBB0_17
	vpcmpeqb	(%rdx), %ymm0, %ymm0
	vpmovmskb	%ymm0, %ecx
	xorl	%eax, %eax
	testl	%ecx, %ecx
	setne	%al
	bsrl	%ecx, %ecx
	xorl	$-32, %ecx
	addl	$33, %ecx
	addq	%rcx, %rdx
	decq	%rdx
	vmovaps	(%rsp), %xmm6
	.seh_startepilogue
	addq	$24, %rsp
	.seh_endepilogue
	vzeroupper
	retq
.LBB0_15:
	vpmovmskb	%ymm4, %eax
	testl	%eax, %eax
	je	.LBB0_18
	bsrl	%eax, %eax
	leaq	(%rax,%r8), %rdx
	incq	%rdx
	movl	$1, %eax
	vmovaps	(%rsp), %xmm6
	.seh_startepilogue
	addq	$24, %rsp
	.seh_endepilogue
	vzeroupper
	retq
.LBB0_17:
	xorl	%eax, %eax
	vmovaps	(%rsp), %xmm6
	.seh_startepilogue
	addq	$24, %rsp
	.seh_endepilogue
	vzeroupper
	retq
.LBB0_18:
	vpmovmskb	%ymm3, %eax
	testl	%eax, %eax
	je	.LBB0_20
	bsrl	%eax, %eax
	leaq	(%rax,%r8), %rdx
	addq	$-31, %rdx
	movl	$1, %eax
	vmovaps	(%rsp), %xmm6
	.seh_startepilogue
	addq	$24, %rsp
	.seh_endepilogue
	vzeroupper
	retq
.LBB0_20:
	vpmovmskb	%ymm2, %eax
	testl	%eax, %eax
	je	.LBB0_22
	bsrl	%eax, %eax
	leaq	(%rax,%r8), %rdx
	addq	$-63, %rdx
	movl	$1, %eax
	vmovaps	(%rsp), %xmm6
	.seh_startepilogue
	addq	$24, %rsp
	.seh_endepilogue
	vzeroupper
	retq
.LBB0_22:
	vpmovmskb	%ymm1, %eax
	movl	$63, %ecx
	bsrl	%eax, %ecx
	xorl	$-32, %ecx
	addl	$33, %ecx
	leaq	(%r8,%rcx), %rdx
	addq	$-96, %rdx
	movl	$1, %eax
	vmovaps	(%rsp), %xmm6
	.seh_startepilogue
	addq	$24, %rsp
	.seh_endepilogue
	vzeroupper
	retq
.Lfunc_end0:
	.seh_endproc

	.def	_RNvMNtNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_644avx26memchrNtB2_3One9rfind_raw;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMNtNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_644avx26memchrNtB2_3One9rfind_raw,unique,1
	.p2align	4
_RNvMNtNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_644avx26memchrNtB2_3One9rfind_raw:
.Lfunc_begin1:
.seh_proc _RNvMNtNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_644avx26memchrNtB2_3One9rfind_raw
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	cmpq	%r8, %rdx
	jae	.LBB1_19
	movq	%r8, %rax
	subq	%rdx, %rax
	cmpq	$32, %rax
	jae	.LBB1_7
	cmpq	$15, %rax
	ja	.LBB1_8
	movzbl	80(%rcx), %r9d
	xorl	%eax, %eax
	.p2align	4
.LBB1_4:
	cmpq	%rdx, %r8
	jbe	.LBB1_10
	leaq	-1(%r8), %rcx
	cmpb	%r9b, -1(%r8)
	movq	%rcx, %r8
	jne	.LBB1_4
	jmp	.LBB1_6
.LBB1_7:
	callq	_RNvMNtNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_644avx26memchrNtB2_3One14rfind_raw_avx2
	movq	%rdx, %rcx
	movq	%rcx, %rdx
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.LBB1_8:
	movdqu	-16(%r8), %xmm1
	movdqa	64(%rcx), %xmm0
	pcmpeqb	%xmm0, %xmm1
	pmovmskb	%xmm1, %eax
	testl	%eax, %eax
	je	.LBB1_12
	addq	$-16, %r8
	movzwl	%ax, %eax
	jmp	.LBB1_16
.LBB1_12:
	andq	$-16, %r8
	leaq	16(%rdx), %rax
	.p2align	4
.LBB1_13:
	cmpq	%rax, %r8
	jb	.LBB1_17
	movdqu	-16(%r8), %xmm1
	addq	$-16, %r8
	pcmpeqb	%xmm0, %xmm1
	pmovmskb	%xmm1, %ecx
	testl	%ecx, %ecx
	je	.LBB1_13
	movzwl	%cx, %eax
.LBB1_16:
	bsrl	%eax, %ecx
	addq	%r8, %rcx
.LBB1_6:
	movl	$1, %eax
	movq	%rcx, %rdx
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.LBB1_17:
	cmpq	%rdx, %r8
	jbe	.LBB1_19
	movdqu	(%rdx), %xmm1
	pcmpeqb	%xmm1, %xmm0
	pmovmskb	%xmm0, %ecx
	xorl	%eax, %eax
	testl	%ecx, %ecx
	setne	%al
	bsrl	%ecx, %ecx
	xorl	$-32, %ecx
	addl	$33, %ecx
	addq	%rdx, %rcx
	decq	%rcx
	movq	%rcx, %rdx
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.LBB1_19:
	xorl	%eax, %eax
.LBB1_10:
	movq	%rcx, %rdx
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end1:
	.seh_endproc

	.def	_RNvMs2_NtNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_644avx26memchrNtB5_3Two13find_raw_avx2;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs2_NtNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_644avx26memchrNtB5_3Two13find_raw_avx2,unique,2
	.p2align	4
_RNvMs2_NtNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_644avx26memchrNtB5_3Two13find_raw_avx2:
.Lfunc_begin2:
.seh_proc _RNvMs2_NtNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_644avx26memchrNtB5_3Two13find_raw_avx2
	subq	$40, %rsp
	.seh_stackalloc 40
	vmovdqa	%xmm7, 16(%rsp)
	.seh_savexmm %xmm7, 16
	vmovdqa	%xmm6, (%rsp)
	.seh_savexmm %xmm6, 0
	.seh_endprologue
	vmovdqu	(%rdx), %ymm2
	vmovdqa	(%rcx), %ymm0
	vmovdqa	32(%rcx), %ymm1
	vpcmpeqb	%ymm2, %ymm0, %ymm3
	vpcmpeqb	%ymm2, %ymm1, %ymm2
	vpor	%ymm2, %ymm3, %ymm2
	vpmovmskb	%ymm2, %eax
	testl	%eax, %eax
	je	.LBB2_4
.LBB2_1:
	rep		bsfl	%eax, %eax
	addq	%rax, %rdx
.LBB2_2:
	movl	$1, %eax
	vmovaps	(%rsp), %xmm6
	vmovaps	16(%rsp), %xmm7
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	vzeroupper
	retq
.LBB2_4:
	movq	%r8, %rax
	subq	%rdx, %rax
	andq	$-32, %rdx
	addq	$32, %rdx
	cmpq	$64, %rax
	setae	%cl
	leaq	-64(%r8), %rax
	cmpq	%rax, %rdx
	setbe	%r9b
	andb	%cl, %r9b
	cmpb	$1, %r9b
	jne	.LBB2_7
	.p2align	4
.LBB2_5:
	vmovdqa	(%rdx), %ymm3
	vmovdqa	32(%rdx), %ymm6
	vpcmpeqb	%ymm3, %ymm0, %ymm4
	vpcmpeqb	%ymm6, %ymm0, %ymm2
	vpcmpeqb	%ymm3, %ymm1, %ymm5
	vpcmpeqb	%ymm6, %ymm1, %ymm3
	vpor	%ymm2, %ymm4, %ymm6
	vpor	%ymm5, %ymm3, %ymm7
	vpor	%ymm6, %ymm7, %ymm6
	vpmovmskb	%ymm6, %ecx
	testl	%ecx, %ecx
	jne	.LBB2_14
	addq	$64, %rdx
	cmpq	%rax, %rdx
	jbe	.LBB2_5
.LBB2_7:
	leaq	-32(%r8), %rcx
	cmpq	%rcx, %rdx
	ja	.LBB2_10
	.p2align	4
.LBB2_8:
	vmovdqu	(%rdx), %ymm2
	vpcmpeqb	%ymm2, %ymm0, %ymm3
	vpcmpeqb	%ymm2, %ymm1, %ymm2
	vpor	%ymm3, %ymm2, %ymm2
	vpmovmskb	%ymm2, %eax
	testl	%eax, %eax
	jne	.LBB2_1
	addq	$32, %rdx
	cmpq	%rcx, %rdx
	jbe	.LBB2_8
.LBB2_10:
	cmpq	%r8, %rdx
	jae	.LBB2_13
	vmovdqu	-32(%r8), %ymm2
	vpcmpeqb	%ymm2, %ymm0, %ymm0
	vpcmpeqb	%ymm2, %ymm1, %ymm1
	vpor	%ymm0, %ymm1, %ymm0
	vpmovmskb	%ymm0, %eax
	testl	%eax, %eax
	je	.LBB2_13
	rep		bsfl	%eax, %eax
	addq	%rax, %rcx
	movl	$1, %eax
	movq	%rcx, %rdx
	vmovaps	(%rsp), %xmm6
	vmovaps	16(%rsp), %xmm7
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	vzeroupper
	retq
.LBB2_13:
	xorl	%eax, %eax
	vmovaps	(%rsp), %xmm6
	vmovaps	16(%rsp), %xmm7
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	vzeroupper
	retq
.LBB2_14:
	vpor	%ymm5, %ymm4, %ymm0
	vpmovmskb	%ymm0, %eax
	testl	%eax, %eax
	jne	.LBB2_1
	vpor	%ymm3, %ymm2, %ymm0
	vpmovmskb	%ymm0, %eax
	movl	$32, %ecx
	rep		bsfl	%eax, %ecx
	addq	%rcx, %rdx
	addq	$32, %rdx
	jmp	.LBB2_2
.Lfunc_end2:
	.seh_endproc

	.def	_RNvMs2_NtNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_644avx26memchrNtB5_3Two8find_raw;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs2_NtNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_644avx26memchrNtB5_3Two8find_raw,unique,3
	.p2align	4
_RNvMs2_NtNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_644avx26memchrNtB5_3Two8find_raw:
.Lfunc_begin3:
.seh_proc _RNvMs2_NtNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_644avx26memchrNtB5_3Two8find_raw
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	cmpq	%r8, %rdx
	jae	.LBB3_17
	movq	%rdx, %r9
	movq	%r8, %rdx
	subq	%r9, %rdx
	cmpq	$32, %rdx
	jae	.LBB3_8
	cmpq	$15, %rdx
	ja	.LBB3_9
	movzbl	128(%rcx), %r10d
	movzbl	129(%rcx), %ecx
	addq	%r9, %rdx
	movl	$1, %eax
	.p2align	4
.LBB3_4:
	movzbl	(%r9), %r11d
	cmpb	%r10b, %r11b
	je	.LBB3_18
	cmpb	%cl, %r11b
	je	.LBB3_18
	incq	%r9
	cmpq	%r8, %r9
	jne	.LBB3_4
	xorl	%eax, %eax
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.LBB3_8:
	movq	%r9, %rdx
	callq	_RNvMs2_NtNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_644avx26memchrNtB5_3Two13find_raw_avx2
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.LBB3_9:
	movdqu	(%r9), %xmm2
	movdqa	96(%rcx), %xmm0
	movdqa	112(%rcx), %xmm1
	movdqa	%xmm0, %xmm3
	pcmpeqb	%xmm2, %xmm3
	pcmpeqb	%xmm1, %xmm2
	por	%xmm3, %xmm2
	pmovmskb	%xmm2, %eax
	testl	%eax, %eax
	je	.LBB3_11
.LBB3_10:
	rep		bsfl	%eax, %eax
	addq	%rax, %r9
	movl	$1, %eax
.LBB3_18:
	movq	%r9, %rdx
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.LBB3_11:
	andq	$-16, %r9
	addq	$16, %r9
	leaq	-16(%r8), %rdx
	cmpq	%rdx, %r9
	ja	.LBB3_14
	.p2align	4
.LBB3_12:
	movdqu	(%r9), %xmm2
	movdqa	%xmm0, %xmm3
	pcmpeqb	%xmm2, %xmm3
	pcmpeqb	%xmm1, %xmm2
	por	%xmm3, %xmm2
	pmovmskb	%xmm2, %eax
	testl	%eax, %eax
	jne	.LBB3_10
	addq	$16, %r9
	cmpq	%rdx, %r9
	jbe	.LBB3_12
.LBB3_14:
	cmpq	%r8, %r9
	jae	.LBB3_17
	movdqu	-16(%r8), %xmm2
	pcmpeqb	%xmm2, %xmm0
	pcmpeqb	%xmm2, %xmm1
	por	%xmm0, %xmm1
	pmovmskb	%xmm1, %eax
	testl	%eax, %eax
	je	.LBB3_17
	rep		bsfl	%eax, %eax
	addq	%rax, %rdx
	movl	$1, %eax
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.LBB3_17:
	xorl	%eax, %eax
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end3:
	.seh_endproc

	.def	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memchr2_raw6detect;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memchr2_raw6detect,unique,4
	.globl	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memchr2_raw6detect
	.p2align	4
_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memchr2_raw6detect:
.Lfunc_begin4:
.seh_proc _RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memchr2_raw6detect
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
	movq	_RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache5CACHE(%rip), %rax
	testq	%rax, %rax
	je	.LBB4_3
	testw	%ax, %ax
	js	.LBB4_5
.LBB4_4:
	leaq	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memchr2_raw9find_sse2(%rip), %rax
	jmp	.LBB4_6
.LBB4_3:
	movq	%r9, %rsi
	movq	%r8, %rdi
	movl	%edx, %ebx
	movl	%ecx, %ebp
	callq	_RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache21detect_and_initialize
	movl	%ebp, %ecx
	movl	%ebx, %edx
	movq	%rdi, %r8
	movq	%rsi, %r9
	testw	%ax, %ax
	jns	.LBB4_4
.LBB4_5:
	leaq	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memchr2_raw9find_avx2(%rip), %rax
.LBB4_6:
	movq	%rax, _RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memchr2_raw2FN(%rip)
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	rex64 jmpq	*%rax
.Lfunc_end4:
	.seh_endproc

	.def	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memchr2_raw9find_avx2;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memchr2_raw9find_avx2,unique,5
	.p2align	4
_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memchr2_raw9find_avx2:
.Lfunc_begin5:
.seh_proc _RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memchr2_raw9find_avx2
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$208, %rsp
	.seh_stackalloc 208
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	andq	$-32, %rsp
	vmovd	%ecx, %xmm0
	vpbroadcastb	%xmm0, %ymm0
	vmovd	%edx, %xmm1
	vpbroadcastb	%xmm1, %ymm1
	vmovdqa	%xmm0, 128(%rsp)
	vmovdqa	%xmm1, 144(%rsp)
	movb	%cl, 160(%rsp)
	movb	%dl, 161(%rsp)
	vmovdqa	%ymm0, 32(%rsp)
	vmovdqa	%ymm1, 64(%rsp)
	movb	%cl, 96(%rsp)
	movb	%dl, 97(%rsp)
	leaq	32(%rsp), %rcx
	movq	%r8, %rdx
	movq	%r9, %r8
	vzeroupper
	callq	_RNvMs2_NtNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_644avx26memchrNtB5_3Two8find_raw
	nop
	.seh_startepilogue
	leaq	80(%rbp), %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end5:
	.seh_endproc

	.def	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memchr2_raw9find_sse2;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memchr2_raw9find_sse2,unique,6
	.p2align	4
_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memchr2_raw9find_sse2:
.Lfunc_begin6:
.seh_proc _RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memchr2_raw9find_sse2
	subq	$40, %rsp
	.seh_stackalloc 40
	movdqa	%xmm7, 16(%rsp)
	.seh_savexmm %xmm7, 16
	movdqa	%xmm6, (%rsp)
	.seh_savexmm %xmm6, 0
	.seh_endprologue
	cmpq	%r9, %r8
	jae	.LBB6_19
	movl	%edx, %r10d
	movq	%r9, %rdx
	subq	%r8, %rdx
	cmpq	$15, %rdx
	ja	.LBB6_7
	addq	%r8, %rdx
	movl	$1, %eax
	.p2align	4
.LBB6_3:
	movzbl	(%r8), %r11d
	cmpb	%cl, %r11b
	je	.LBB6_20
	cmpb	%r10b, %r11b
	je	.LBB6_20
	incq	%r8
	cmpq	%r9, %r8
	jne	.LBB6_3
	xorl	%eax, %eax
	movaps	(%rsp), %xmm6
	movaps	16(%rsp), %xmm7
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.LBB6_7:
	movzbl	%cl, %eax
	movd	%eax, %xmm0
	punpcklbw	%xmm0, %xmm0
	pshuflw	$0, %xmm0, %xmm0
	pshufd	$68, %xmm0, %xmm0
	movzbl	%r10b, %eax
	movd	%eax, %xmm1
	punpcklbw	%xmm1, %xmm1
	pshuflw	$0, %xmm1, %xmm1
	pshufd	$68, %xmm1, %xmm1
	movdqu	(%r8), %xmm2
	movdqa	%xmm0, %xmm3
	pcmpeqb	%xmm2, %xmm3
	pcmpeqb	%xmm1, %xmm2
	por	%xmm3, %xmm2
	pmovmskb	%xmm2, %eax
	testl	%eax, %eax
	je	.LBB6_9
.LBB6_8:
	rep		bsfl	%eax, %eax
	addq	%rax, %r8
	movl	$1, %eax
.LBB6_20:
	movq	%r8, %rdx
	movaps	(%rsp), %xmm6
	movaps	16(%rsp), %xmm7
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.LBB6_9:
	andq	$-16, %r8
	addq	$16, %r8
	cmpq	$32, %rdx
	setae	%cl
	leaq	-32(%r9), %rax
	cmpq	%rax, %r8
	setbe	%dl
	andb	%cl, %dl
	cmpb	$1, %dl
	jne	.LBB6_12
	.p2align	4
.LBB6_10:
	movdqa	(%r8), %xmm4
	movdqa	16(%r8), %xmm2
	movdqa	%xmm0, %xmm5
	pcmpeqb	%xmm4, %xmm5
	movdqa	%xmm0, %xmm3
	pcmpeqb	%xmm2, %xmm3
	pcmpeqb	%xmm1, %xmm4
	pcmpeqb	%xmm1, %xmm2
	movdqa	%xmm5, %xmm6
	por	%xmm3, %xmm6
	movdqa	%xmm2, %xmm7
	por	%xmm4, %xmm7
	por	%xmm6, %xmm7
	pmovmskb	%xmm7, %ecx
	testl	%ecx, %ecx
	jne	.LBB6_23
	addq	$32, %r8
	cmpq	%rax, %r8
	jbe	.LBB6_10
.LBB6_12:
	leaq	-16(%r9), %rdx
	cmpq	%rdx, %r8
	ja	.LBB6_15
	.p2align	4
.LBB6_13:
	movdqu	(%r8), %xmm2
	movdqa	%xmm0, %xmm3
	pcmpeqb	%xmm2, %xmm3
	pcmpeqb	%xmm1, %xmm2
	por	%xmm3, %xmm2
	pmovmskb	%xmm2, %eax
	testl	%eax, %eax
	jne	.LBB6_8
	addq	$16, %r8
	cmpq	%rdx, %r8
	jbe	.LBB6_13
.LBB6_15:
	cmpq	%r9, %r8
	jae	.LBB6_19
	movdqu	-16(%r9), %xmm2
	pcmpeqb	%xmm2, %xmm0
	pcmpeqb	%xmm2, %xmm1
	por	%xmm0, %xmm1
	pmovmskb	%xmm1, %eax
	testl	%eax, %eax
	je	.LBB6_19
	rep		bsfl	%eax, %eax
	addq	%rax, %rdx
	jmp	.LBB6_18
.LBB6_19:
	xorl	%eax, %eax
	movaps	(%rsp), %xmm6
	movaps	16(%rsp), %xmm7
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.LBB6_23:
	por	%xmm4, %xmm5
	pmovmskb	%xmm5, %eax
	testl	%eax, %eax
	jne	.LBB6_8
	por	%xmm2, %xmm3
	pmovmskb	%xmm3, %eax
	movl	$32, %ecx
	rep		bsfl	%eax, %ecx
	leaq	(%r8,%rcx), %rdx
	addq	$16, %rdx
.LBB6_18:
	movl	$1, %eax
	movaps	(%rsp), %xmm6
	movaps	16(%rsp), %xmm7
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end6:
	.seh_endproc

	.def	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw6detect;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw6detect,unique,7
	.globl	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw6detect
	.p2align	4
_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw6detect:
.Lfunc_begin7:
.seh_proc _RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw6detect
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	_RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache5CACHE(%rip), %rax
	testq	%rax, %rax
	je	.LBB7_3
	testw	%ax, %ax
	js	.LBB7_5
.LBB7_4:
	leaq	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw9find_sse2(%rip), %rax
	jmp	.LBB7_6
.LBB7_3:
	movq	%r8, %rsi
	movq	%rdx, %rdi
	movl	%ecx, %ebx
	callq	_RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache21detect_and_initialize
	movl	%ebx, %ecx
	movq	%rdi, %rdx
	movq	%rsi, %r8
	testw	%ax, %ax
	jns	.LBB7_4
.LBB7_5:
	leaq	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw9find_avx2(%rip), %rax
.LBB7_6:
	movq	%rax, _RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw2FN(%rip)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	rex64 jmpq	*%rax
.Lfunc_end7:
	.seh_endproc

	.def	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw9find_avx2;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw9find_avx2,unique,8
	.p2align	4
_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw9find_avx2:
.Lfunc_begin8:
.seh_proc _RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw9find_avx2
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$144, %rsp
	.seh_stackalloc 144
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	andq	$-32, %rsp
	vmovd	%ecx, %xmm0
	vpbroadcastb	%xmm0, %ymm0
	vmovdqa	%xmm0, 96(%rsp)
	movb	%cl, 112(%rsp)
	vmovdqa	%ymm0, 32(%rsp)
	movb	%cl, 64(%rsp)
	leaq	32(%rsp), %rcx
	vzeroupper
	callq	_RNvMNtNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_644avx26memchrNtB2_3One9rfind_raw
	nop
	.seh_startepilogue
	leaq	16(%rbp), %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end8:
	.seh_endproc

	.def	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw9find_sse2;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw9find_sse2,unique,9
	.p2align	4
_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw9find_sse2:
.Lfunc_begin9:
.seh_proc _RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw9find_sse2
	subq	$24, %rsp
	.seh_stackalloc 24
	movdqa	%xmm6, (%rsp)
	.seh_savexmm %xmm6, 0
	.seh_endprologue
	cmpq	%r8, %rdx
	jae	.LBB9_21
	movq	%r8, %r9
	subq	%rdx, %r9
	cmpq	$15, %r9
	ja	.LBB9_5
	xorl	%eax, %eax
	.p2align	4
.LBB9_3:
	cmpq	%rdx, %r8
	jbe	.LBB9_8
	leaq	-1(%r8), %r9
	cmpb	%cl, -1(%r8)
	movq	%r9, %r8
	jne	.LBB9_3
	jmp	.LBB9_7
.LBB9_5:
	movzbl	%cl, %eax
	movd	%eax, %xmm0
	punpcklbw	%xmm0, %xmm0
	pshuflw	$0, %xmm0, %xmm0
	pshufd	$68, %xmm0, %xmm0
	movdqu	-16(%r8), %xmm1
	pcmpeqb	%xmm0, %xmm1
	pmovmskb	%xmm1, %eax
	testl	%eax, %eax
	je	.LBB9_10
	addq	$-16, %r8
	movzwl	%ax, %eax
	bsrl	%eax, %r9d
	addq	%r8, %r9
.LBB9_7:
	movl	$1, %eax
	movq	%r9, %rdx
	movaps	(%rsp), %xmm6
	.seh_startepilogue
	addq	$24, %rsp
	.seh_endepilogue
	retq
.LBB9_10:
	movq	%r8, %rax
	andq	$-16, %rax
	cmpq	$64, %r9
	setae	%r9b
	leaq	64(%rdx), %rcx
	cmpq	%rcx, %rax
	setae	%r10b
	andb	%r9b, %r10b
	cmpb	$1, %r10b
	jne	.LBB9_15
	movl	%r8d, %eax
	andl	$15, %eax
	subq	%rax, %r8
	addq	$-17, %r8
	.p2align	4
.LBB9_12:
	movdqa	-47(%r8), %xmm1
	pcmpeqb	%xmm0, %xmm1
	movdqa	-31(%r8), %xmm2
	pcmpeqb	%xmm0, %xmm2
	movdqa	-15(%r8), %xmm3
	pcmpeqb	%xmm0, %xmm3
	movdqa	1(%r8), %xmm4
	pcmpeqb	%xmm0, %xmm4
	movdqa	%xmm1, %xmm5
	por	%xmm2, %xmm5
	movdqa	%xmm3, %xmm6
	por	%xmm4, %xmm6
	por	%xmm5, %xmm6
	pmovmskb	%xmm6, %eax
	testl	%eax, %eax
	jne	.LBB9_22
	leaq	-64(%r8), %rax
	addq	$-47, %r8
	cmpq	%rcx, %r8
	movq	%rax, %r8
	jae	.LBB9_12
	addq	$17, %rax
.LBB9_15:
	leaq	16(%rdx), %rcx
	.p2align	4
.LBB9_16:
	cmpq	%rcx, %rax
	jb	.LBB9_19
	movdqu	-16(%rax), %xmm1
	addq	$-16, %rax
	pcmpeqb	%xmm0, %xmm1
	pmovmskb	%xmm1, %r8d
	testl	%r8d, %r8d
	je	.LBB9_16
	movzwl	%r8w, %ecx
	bsrl	%ecx, %r9d
	addq	%rax, %r9
	jmp	.LBB9_7
.LBB9_19:
	cmpq	%rdx, %rax
	jbe	.LBB9_21
	movdqu	(%rdx), %xmm1
	pcmpeqb	%xmm1, %xmm0
	pmovmskb	%xmm0, %ecx
	xorl	%eax, %eax
	testl	%ecx, %ecx
	setne	%al
	bsrl	%ecx, %ecx
	xorl	$-32, %ecx
	addl	$33, %ecx
	leaq	(%rdx,%rcx), %r9
	decq	%r9
	movq	%r9, %rdx
	movaps	(%rsp), %xmm6
	.seh_startepilogue
	addq	$24, %rsp
	.seh_endepilogue
	retq
.LBB9_21:
	xorl	%eax, %eax
.LBB9_8:
	movq	%r9, %rdx
	movaps	(%rsp), %xmm6
	.seh_startepilogue
	addq	$24, %rsp
	.seh_endepilogue
	retq
.LBB9_22:
	pmovmskb	%xmm4, %eax
	testl	%eax, %eax
	je	.LBB9_24
	movzwl	%ax, %eax
	bsrl	%eax, %eax
	leaq	(%rax,%r8), %r9
	incq	%r9
	jmp	.LBB9_7
.LBB9_24:
	pmovmskb	%xmm3, %eax
	testl	%eax, %eax
	je	.LBB9_26
	movzwl	%ax, %eax
	bsrl	%eax, %eax
	leaq	(%rax,%r8), %r9
	addq	$-15, %r9
	jmp	.LBB9_7
.LBB9_26:
	pmovmskb	%xmm2, %eax
	testl	%eax, %eax
	je	.LBB9_28
	movzwl	%ax, %eax
	bsrl	%eax, %eax
	leaq	(%rax,%r8), %r9
	addq	$-31, %r9
	jmp	.LBB9_7
.LBB9_28:
	pmovmskb	%xmm1, %eax
	movl	$63, %ecx
	bsrl	%eax, %ecx
	xorl	$-32, %ecx
	addl	$33, %ecx
	leaq	(%r8,%rcx), %r9
	addq	$-48, %r9
	jmp	.LBB9_7
.Lfunc_end9:
	.seh_endproc

	.def	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw6detect;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw6detect,unique,10
	.globl	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw6detect
	.p2align	4
_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw6detect:
.Lfunc_begin10:
.seh_proc _RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw6detect
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	_RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache5CACHE(%rip), %rax
	testq	%rax, %rax
	je	.LBB10_3
	testw	%ax, %ax
	js	.LBB10_5
.LBB10_4:
	leaq	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw9find_sse2(%rip), %rax
	jmp	.LBB10_6
.LBB10_3:
	movq	%r8, %rsi
	movq	%rdx, %rdi
	movl	%ecx, %ebx
	callq	_RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache21detect_and_initialize
	movl	%ebx, %ecx
	movq	%rdi, %rdx
	movq	%rsi, %r8
	testw	%ax, %ax
	jns	.LBB10_4
.LBB10_5:
	leaq	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw9find_avx2(%rip), %rax
.LBB10_6:
	movq	%rax, _RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw2FN(%rip)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	rex64 jmpq	*%rax
.Lfunc_end10:
	.seh_endproc

	.def	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw9find_avx2;
	.scl	3;
	.type	32;
	.endef
	.globl	__real@0000000000000001
	.section	.rdata,"dr",discard,__real@0000000000000001
	.p2align	3, 0x0
__real@0000000000000001:
	.quad	1
	.globl	__xmm@0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f
	.section	.rdata,"dr",discard,__xmm@0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f
	.p2align	4, 0x0
__xmm@0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f:
	.zero	16,15
	.globl	__xmm@04030302030202010302020102010100
	.section	.rdata,"dr",discard,__xmm@04030302030202010302020102010100
	.p2align	4, 0x0
__xmm@04030302030202010302020102010100:
	.byte	0
	.byte	1
	.byte	1
	.byte	2
	.byte	1
	.byte	2
	.byte	2
	.byte	3
	.byte	1
	.byte	2
	.byte	2
	.byte	3
	.byte	2
	.byte	3
	.byte	3
	.byte	4
	.section	.text,"xr",one_only,_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw9find_avx2,unique,11
	.p2align	4
_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw9find_avx2:
.Lfunc_begin11:
.seh_proc _RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw9find_avx2
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	vmovdqa	%xmm10, 64(%rsp)
	.seh_savexmm %xmm10, 64
	vmovdqa	%xmm9, 48(%rsp)
	.seh_savexmm %xmm9, 48
	vmovdqa	%xmm8, 32(%rsp)
	.seh_savexmm %xmm8, 32
	vmovdqa	%xmm7, 16(%rsp)
	.seh_savexmm %xmm7, 16
	vmovdqa	%xmm6, (%rsp)
	.seh_savexmm %xmm6, 0
	.seh_endprologue
	cmpq	%r8, %rdx
	jae	.LBB11_5
	vmovd	%ecx, %xmm0
	vpbroadcastb	%xmm0, %ymm0
	movq	%r8, %r11
	subq	%rdx, %r11
	cmpq	$32, %r11
	jae	.LBB11_6
	cmpq	$15, %r11
	ja	.LBB11_9
	cmpq	$4, %r11
	jae	.LBB11_14
	xorl	%eax, %eax
	movq	%rdx, %r9
	jmp	.LBB11_17
.LBB11_5:
	xorl	%eax, %eax
	jmp	.LBB11_74
.LBB11_6:
	movq	%rdx, %r9
	andq	$-32, %r9
	addq	$32, %r9
	leaq	1(%rdx), %rax
	cmpq	%rax, %r9
	cmovaq	%r9, %rax
	subq	%rdx, %rax
	cmpq	$4, %rax
	jae	.LBB11_12
	xorl	%r10d, %r10d
.LBB11_8:
	movq	%rdx, %rdi
	jmp	.LBB11_27
.LBB11_9:
	movq	%rdx, %r9
	andq	$-16, %r9
	addq	$16, %r9
	leaq	1(%rdx), %rax
	cmpq	%rax, %r9
	cmovaq	%r9, %rax
	subq	%rdx, %rax
	cmpq	$4, %rax
	jae	.LBB11_18
	xorl	%r10d, %r10d
.LBB11_11:
	movq	%rdx, %rsi
	jmp	.LBB11_47
.LBB11_12:
	cmpq	$16, %rax
	jae	.LBB11_20
	xorl	%esi, %esi
	xorl	%r10d, %r10d
	jmp	.LBB11_24
.LBB11_14:
	movl	%r11d, %r10d
	andl	$12, %r10d
	leaq	(%rdx,%r10), %r9
	vmovd	%ecx, %xmm0
	vpbroadcastb	%xmm0, %xmm1
	vpxor	%xmm0, %xmm0, %xmm0
	xorl	%eax, %eax
	vpbroadcastq	__real@0000000000000001(%rip), %ymm2
	.p2align	4
.LBB11_15:
	vmovd	(%rdx,%rax), %xmm3
	vpcmpeqb	%xmm1, %xmm3, %xmm3
	vpmovzxbq	%xmm3, %ymm3
	vpand	%ymm2, %ymm3, %ymm3
	vpaddq	%ymm3, %ymm0, %ymm0
	addq	$4, %rax
	cmpq	%rax, %r10
	jne	.LBB11_15
	vextracti128	$1, %ymm0, %xmm1
	vpaddq	%xmm1, %xmm0, %xmm0
	vpshufd	$238, %xmm0, %xmm1
	vpaddq	%xmm1, %xmm0, %xmm0
	vmovq	%xmm0, %rax
	cmpq	%r10, %r11
	je	.LBB11_74
	.p2align	4
.LBB11_17:
	xorl	%edx, %edx
	cmpb	%cl, (%r9)
	sete	%dl
	addq	%rdx, %rax
	incq	%r9
	cmpq	%r8, %r9
	jne	.LBB11_17
	jmp	.LBB11_74
.LBB11_18:
	cmpq	$16, %rax
	jae	.LBB11_40
	xorl	%r11d, %r11d
	xorl	%r10d, %r10d
	jmp	.LBB11_44
.LBB11_20:
	movq	%rax, %rsi
	andq	$-16, %rsi
	vmovd	%ecx, %xmm1
	vpbroadcastb	%xmm1, %xmm2
	vpxor	%xmm1, %xmm1, %xmm1
	vpbroadcastq	__real@0000000000000001(%rip), %ymm3
	xorl	%r10d, %r10d
	vpxor	%xmm4, %xmm4, %xmm4
	vpxor	%xmm5, %xmm5, %xmm5
	vpxor	%xmm6, %xmm6, %xmm6
	.p2align	4
.LBB11_21:
	vmovd	(%rdx,%r10), %xmm7
	vmovd	4(%rdx,%r10), %xmm8
	vmovd	8(%rdx,%r10), %xmm9
	vmovd	12(%rdx,%r10), %xmm10
	vpcmpeqb	%xmm2, %xmm7, %xmm7
	vpmovzxbq	%xmm7, %ymm7
	vpand	%ymm3, %ymm7, %ymm7
	vpaddq	%ymm7, %ymm1, %ymm1
	vpcmpeqb	%xmm2, %xmm8, %xmm7
	vpmovzxbq	%xmm7, %ymm7
	vpand	%ymm3, %ymm7, %ymm7
	vpaddq	%ymm7, %ymm4, %ymm4
	vpcmpeqb	%xmm2, %xmm9, %xmm7
	vpmovzxbq	%xmm7, %ymm7
	vpand	%ymm3, %ymm7, %ymm7
	vpaddq	%ymm7, %ymm5, %ymm5
	vpcmpeqb	%xmm2, %xmm10, %xmm7
	vpmovzxbq	%xmm7, %ymm7
	vpand	%ymm3, %ymm7, %ymm7
	vpaddq	%ymm7, %ymm6, %ymm6
	addq	$16, %r10
	cmpq	%r10, %rsi
	jne	.LBB11_21
	vpaddq	%ymm1, %ymm4, %ymm1
	vpaddq	%ymm1, %ymm5, %ymm1
	vpaddq	%ymm1, %ymm6, %ymm1
	vextracti128	$1, %ymm1, %xmm2
	vpaddq	%xmm2, %xmm1, %xmm1
	vpshufd	$238, %xmm1, %xmm2
	vpaddq	%xmm2, %xmm1, %xmm1
	vmovq	%xmm1, %r10
	cmpq	%rsi, %rax
	je	.LBB11_28
	testb	$12, %al
	je	.LBB11_75
.LBB11_24:
	movq	%rax, %rbx
	andq	$-4, %rbx
	leaq	(%rdx,%rbx), %rdi
	vmovq	%r10, %xmm1
	vmovd	%ecx, %xmm2
	vpbroadcastb	%xmm2, %xmm2
	vpbroadcastq	__real@0000000000000001(%rip), %ymm3
	.p2align	4
.LBB11_25:
	vmovd	(%rdx,%rsi), %xmm4
	vpcmpeqb	%xmm2, %xmm4, %xmm4
	vpmovzxbq	%xmm4, %ymm4
	vpand	%ymm3, %ymm4, %ymm4
	vpaddq	%ymm4, %ymm1, %ymm1
	addq	$4, %rsi
	cmpq	%rsi, %rbx
	jne	.LBB11_25
	vextracti128	$1, %ymm1, %xmm2
	vpaddq	%xmm2, %xmm1, %xmm1
	vpshufd	$238, %xmm1, %xmm2
	vpaddq	%xmm2, %xmm1, %xmm1
	vmovq	%xmm1, %r10
	cmpq	%rbx, %rax
	je	.LBB11_28
	.p2align	4
.LBB11_27:
	xorl	%eax, %eax
	cmpb	%cl, (%rdi)
	sete	%al
	addq	%rax, %r10
	incq	%rdi
	cmpq	%r9, %rdi
	jb	.LBB11_27
.LBB11_28:
	cmpq	$127, %r11
	seta	%dl
	leaq	-128(%r8), %rax
	cmpq	%rax, %r9
	setbe	%r11b
	andb	%dl, %r11b
	cmpb	$1, %r11b
	jne	.LBB11_31
	vmovdqa	__xmm@0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f(%rip), %xmm1
	vmovdqa	__xmm@04030302030202010302020102010100(%rip), %xmm2
	vpxor	%xmm3, %xmm3, %xmm3
	.p2align	4
.LBB11_30:
	vpcmpeqb	(%r9), %ymm0, %ymm4
	vpmovmskb	%ymm4, %edx
	vpcmpeqb	32(%r9), %ymm0, %ymm4
	vpcmpeqb	64(%r9), %ymm0, %ymm5
	vpmovmskb	%ymm4, %r11d
	vpmovmskb	%ymm5, %esi
	vpcmpeqb	96(%r9), %ymm0, %ymm4
	vpmovmskb	%ymm4, %edi
	vmovd	%edx, %xmm4
	vpinsrd	$1, %r11d, %xmm4, %xmm4
	vpinsrd	$2, %esi, %xmm4, %xmm4
	vpinsrd	$3, %edi, %xmm4, %xmm4
	vpand	%xmm1, %xmm4, %xmm5
	vpshufb	%xmm5, %xmm2, %xmm5
	vpsrlw	$4, %xmm4, %xmm4
	vpand	%xmm1, %xmm4, %xmm4
	vpshufb	%xmm4, %xmm2, %xmm4
	vpaddb	%xmm5, %xmm4, %xmm4
	vpunpckhdq	%xmm3, %xmm4, %xmm5
	vpsadbw	%xmm3, %xmm5, %xmm5
	vpmovzxdq	%xmm4, %xmm4
	vpsadbw	%xmm3, %xmm4, %xmm4
	vpackuswb	%xmm5, %xmm4, %xmm4
	vpackusdw	%xmm4, %xmm4, %xmm4
	vpackuswb	%xmm4, %xmm4, %xmm4
	vpblendd	$1, %xmm4, %xmm3, %xmm4
	vpsadbw	%xmm3, %xmm4, %xmm4
	vmovq	%xmm4, %rdx
	addq	%rdx, %r10
	subq	$-128, %r9
	cmpq	%rax, %r9
	jbe	.LBB11_30
.LBB11_31:
	leaq	-32(%r8), %rax
	cmpq	%rax, %r9
	ja	.LBB11_33
	.p2align	4
.LBB11_32:
	vpcmpeqb	(%r9), %ymm0, %ymm1
	vpmovmskb	%ymm1, %edx
	movl	%edx, %r11d
	shrl	%r11d
	andl	$1431655765, %r11d
	subl	%r11d, %edx
	movl	%edx, %r11d
	andl	$858993459, %r11d
	shrl	$2, %edx
	andl	$858993459, %edx
	addl	%r11d, %edx
	movl	%edx, %r11d
	shrl	$4, %r11d
	addl	%edx, %r11d
	andl	$252645135, %r11d
	imull	$16843009, %r11d, %edx
	shrl	$24, %edx
	addq	%rdx, %r10
	addq	$32, %r9
	cmpq	%rax, %r9
	jbe	.LBB11_32
.LBB11_33:
	cmpq	%r8, %r9
	jae	.LBB11_37
	movq	%r8, %rdx
	subq	%r9, %rdx
	cmpq	$4, %rdx
	jae	.LBB11_38
	xorl	%eax, %eax
.LBB11_36:
	movq	%r9, %rsi
	jmp	.LBB11_62
.LBB11_38:
	cmpq	$16, %rdx
	jae	.LBB11_55
	xorl	%r11d, %r11d
	xorl	%eax, %eax
	jmp	.LBB11_59
.LBB11_40:
	movq	%rax, %r11
	andq	$-16, %r11
	vmovd	%ecx, %xmm1
	vpbroadcastb	%xmm1, %xmm2
	vpxor	%xmm1, %xmm1, %xmm1
	vpbroadcastq	__real@0000000000000001(%rip), %ymm3
	xorl	%r10d, %r10d
	vpxor	%xmm4, %xmm4, %xmm4
	vpxor	%xmm5, %xmm5, %xmm5
	vpxor	%xmm6, %xmm6, %xmm6
	.p2align	4
.LBB11_41:
	vmovd	(%rdx,%r10), %xmm7
	vmovd	4(%rdx,%r10), %xmm8
	vmovd	8(%rdx,%r10), %xmm9
	vmovd	12(%rdx,%r10), %xmm10
	vpcmpeqb	%xmm2, %xmm7, %xmm7
	vpmovzxbq	%xmm7, %ymm7
	vpand	%ymm3, %ymm7, %ymm7
	vpaddq	%ymm7, %ymm1, %ymm1
	vpcmpeqb	%xmm2, %xmm8, %xmm7
	vpmovzxbq	%xmm7, %ymm7
	vpand	%ymm3, %ymm7, %ymm7
	vpaddq	%ymm7, %ymm4, %ymm4
	vpcmpeqb	%xmm2, %xmm9, %xmm7
	vpmovzxbq	%xmm7, %ymm7
	vpand	%ymm3, %ymm7, %ymm7
	vpaddq	%ymm7, %ymm5, %ymm5
	vpcmpeqb	%xmm2, %xmm10, %xmm7
	vpmovzxbq	%xmm7, %ymm7
	vpand	%ymm3, %ymm7, %ymm7
	vpaddq	%ymm7, %ymm6, %ymm6
	addq	$16, %r10
	cmpq	%r10, %r11
	jne	.LBB11_41
	vpaddq	%ymm1, %ymm4, %ymm1
	vpaddq	%ymm1, %ymm5, %ymm1
	vpaddq	%ymm1, %ymm6, %ymm1
	vextracti128	$1, %ymm1, %xmm2
	vpaddq	%xmm2, %xmm1, %xmm1
	vpshufd	$238, %xmm1, %xmm2
	vpaddq	%xmm2, %xmm1, %xmm1
	vmovq	%xmm1, %r10
	cmpq	%r11, %rax
	je	.LBB11_48
	testb	$12, %al
	je	.LBB11_76
.LBB11_44:
	movq	%rax, %rdi
	andq	$-4, %rdi
	leaq	(%rdx,%rdi), %rsi
	vmovq	%r10, %xmm1
	vmovd	%ecx, %xmm2
	vpbroadcastb	%xmm2, %xmm2
	vpbroadcastq	__real@0000000000000001(%rip), %ymm3
	.p2align	4
.LBB11_45:
	vmovd	(%rdx,%r11), %xmm4
	vpcmpeqb	%xmm2, %xmm4, %xmm4
	vpmovzxbq	%xmm4, %ymm4
	vpand	%ymm3, %ymm4, %ymm4
	vpaddq	%ymm4, %ymm1, %ymm1
	addq	$4, %r11
	cmpq	%r11, %rdi
	jne	.LBB11_45
	vextracti128	$1, %ymm1, %xmm2
	vpaddq	%xmm2, %xmm1, %xmm1
	vpshufd	$238, %xmm1, %xmm2
	vpaddq	%xmm2, %xmm1, %xmm1
	vmovq	%xmm1, %r10
	cmpq	%rdi, %rax
	je	.LBB11_48
	.p2align	4
.LBB11_47:
	xorl	%eax, %eax
	cmpb	%cl, (%rsi)
	sete	%al
	addq	%rax, %r10
	incq	%rsi
	cmpq	%r9, %rsi
	jb	.LBB11_47
.LBB11_48:
	leaq	-16(%r8), %rax
	cmpq	%rax, %r9
	ja	.LBB11_50
	.p2align	4
.LBB11_49:
	vpcmpeqb	(%r9), %xmm0, %xmm1
	vpmovmskb	%xmm1, %edx
	movl	%edx, %r11d
	shrl	%r11d
	andl	$21845, %r11d
	subl	%r11d, %edx
	movl	%edx, %r11d
	andl	$13107, %r11d
	shrl	$2, %edx
	andl	$13107, %edx
	addl	%r11d, %edx
	movl	%edx, %r11d
	shrl	$4, %r11d
	addl	%edx, %r11d
	andl	$3855, %r11d
	movl	%r11d, %edx
	shrl	$8, %edx
	addl	%r11d, %edx
	movzbl	%dl, %edx
	addq	%rdx, %r10
	addq	$16, %r9
	cmpq	%rax, %r9
	jbe	.LBB11_49
.LBB11_50:
	cmpq	%r8, %r9
	jae	.LBB11_37
	movq	%r8, %rdx
	subq	%r9, %rdx
	cmpq	$4, %rdx
	jae	.LBB11_63
	xorl	%eax, %eax
.LBB11_53:
	movq	%r9, %rsi
	jmp	.LBB11_72
.LBB11_37:
	xorl	%eax, %eax
	jmp	.LBB11_73
.LBB11_55:
	movq	%rdx, %r11
	andq	$-16, %r11
	vmovd	%ecx, %xmm0
	vpbroadcastb	%xmm0, %xmm1
	vpxor	%xmm0, %xmm0, %xmm0
	vpbroadcastq	__real@0000000000000001(%rip), %ymm2
	xorl	%eax, %eax
	vpxor	%xmm3, %xmm3, %xmm3
	vpxor	%xmm4, %xmm4, %xmm4
	vpxor	%xmm5, %xmm5, %xmm5
	.p2align	4
.LBB11_56:
	vmovd	(%r9,%rax), %xmm6
	vmovd	4(%r9,%rax), %xmm7
	vmovd	8(%r9,%rax), %xmm8
	vmovd	12(%r9,%rax), %xmm9
	vpcmpeqb	%xmm1, %xmm6, %xmm6
	vpmovzxbq	%xmm6, %ymm6
	vpand	%ymm2, %ymm6, %ymm6
	vpaddq	%ymm6, %ymm0, %ymm0
	vpcmpeqb	%xmm1, %xmm7, %xmm6
	vpmovzxbq	%xmm6, %ymm6
	vpand	%ymm2, %ymm6, %ymm6
	vpaddq	%ymm6, %ymm3, %ymm3
	vpcmpeqb	%xmm1, %xmm8, %xmm6
	vpmovzxbq	%xmm6, %ymm6
	vpand	%ymm2, %ymm6, %ymm6
	vpaddq	%ymm6, %ymm4, %ymm4
	vpcmpeqb	%xmm1, %xmm9, %xmm6
	vpmovzxbq	%xmm6, %ymm6
	vpand	%ymm2, %ymm6, %ymm6
	vpaddq	%ymm6, %ymm5, %ymm5
	addq	$16, %rax
	cmpq	%rax, %r11
	jne	.LBB11_56
	vpaddq	%ymm0, %ymm3, %ymm0
	vpaddq	%ymm0, %ymm4, %ymm0
	vpaddq	%ymm0, %ymm5, %ymm0
	vextracti128	$1, %ymm0, %xmm1
	vpaddq	%xmm1, %xmm0, %xmm0
	vpshufd	$238, %xmm0, %xmm1
	vpaddq	%xmm1, %xmm0, %xmm0
	vmovq	%xmm0, %rax
	cmpq	%r11, %rdx
	je	.LBB11_73
	testb	$12, %dl
	je	.LBB11_77
.LBB11_59:
	movq	%rdx, %rdi
	andq	$-4, %rdi
	leaq	(%r9,%rdi), %rsi
	vmovq	%rax, %xmm0
	vmovd	%ecx, %xmm1
	vpbroadcastb	%xmm1, %xmm1
	vpbroadcastq	__real@0000000000000001(%rip), %ymm2
	.p2align	4
.LBB11_60:
	vmovd	(%r9,%r11), %xmm3
	vpcmpeqb	%xmm1, %xmm3, %xmm3
	vpmovzxbq	%xmm3, %ymm3
	vpand	%ymm2, %ymm3, %ymm3
	vpaddq	%ymm3, %ymm0, %ymm0
	addq	$4, %r11
	cmpq	%r11, %rdi
	jne	.LBB11_60
	vextracti128	$1, %ymm0, %xmm1
	vpaddq	%xmm1, %xmm0, %xmm0
	vpshufd	$238, %xmm0, %xmm1
	vpaddq	%xmm1, %xmm0, %xmm0
	vmovq	%xmm0, %rax
	cmpq	%rdi, %rdx
	je	.LBB11_73
	.p2align	4
.LBB11_62:
	xorl	%edx, %edx
	cmpb	%cl, (%rsi)
	sete	%dl
	addq	%rdx, %rax
	incq	%rsi
	cmpq	%r8, %rsi
	jne	.LBB11_62
	jmp	.LBB11_73
.LBB11_63:
	cmpq	$16, %rdx
	jae	.LBB11_65
	xorl	%r11d, %r11d
	xorl	%eax, %eax
	jmp	.LBB11_69
.LBB11_65:
	movq	%rdx, %r11
	andq	$-16, %r11
	vmovd	%ecx, %xmm0
	vpbroadcastb	%xmm0, %xmm1
	vpxor	%xmm0, %xmm0, %xmm0
	vpbroadcastq	__real@0000000000000001(%rip), %ymm2
	xorl	%eax, %eax
	vpxor	%xmm3, %xmm3, %xmm3
	vpxor	%xmm4, %xmm4, %xmm4
	vpxor	%xmm5, %xmm5, %xmm5
	.p2align	4
.LBB11_66:
	vmovd	(%r9,%rax), %xmm6
	vmovd	4(%r9,%rax), %xmm7
	vmovd	8(%r9,%rax), %xmm8
	vmovd	12(%r9,%rax), %xmm9
	vpcmpeqb	%xmm1, %xmm6, %xmm6
	vpmovzxbq	%xmm6, %ymm6
	vpand	%ymm2, %ymm6, %ymm6
	vpaddq	%ymm6, %ymm0, %ymm0
	vpcmpeqb	%xmm1, %xmm7, %xmm6
	vpmovzxbq	%xmm6, %ymm6
	vpand	%ymm2, %ymm6, %ymm6
	vpaddq	%ymm6, %ymm3, %ymm3
	vpcmpeqb	%xmm1, %xmm8, %xmm6
	vpmovzxbq	%xmm6, %ymm6
	vpand	%ymm2, %ymm6, %ymm6
	vpaddq	%ymm6, %ymm4, %ymm4
	vpcmpeqb	%xmm1, %xmm9, %xmm6
	vpmovzxbq	%xmm6, %ymm6
	vpand	%ymm2, %ymm6, %ymm6
	vpaddq	%ymm6, %ymm5, %ymm5
	addq	$16, %rax
	cmpq	%rax, %r11
	jne	.LBB11_66
	vpaddq	%ymm0, %ymm3, %ymm0
	vpaddq	%ymm0, %ymm4, %ymm0
	vpaddq	%ymm0, %ymm5, %ymm0
	vextracti128	$1, %ymm0, %xmm1
	vpaddq	%xmm1, %xmm0, %xmm0
	vpshufd	$238, %xmm0, %xmm1
	vpaddq	%xmm1, %xmm0, %xmm0
	vmovq	%xmm0, %rax
	cmpq	%r11, %rdx
	je	.LBB11_73
	testb	$12, %dl
	je	.LBB11_78
.LBB11_69:
	movq	%rdx, %rdi
	andq	$-4, %rdi
	leaq	(%r9,%rdi), %rsi
	vmovq	%rax, %xmm0
	vmovd	%ecx, %xmm1
	vpbroadcastb	%xmm1, %xmm1
	vpbroadcastq	__real@0000000000000001(%rip), %ymm2
	.p2align	4
.LBB11_70:
	vmovd	(%r9,%r11), %xmm3
	vpcmpeqb	%xmm1, %xmm3, %xmm3
	vpmovzxbq	%xmm3, %ymm3
	vpand	%ymm2, %ymm3, %ymm3
	vpaddq	%ymm3, %ymm0, %ymm0
	addq	$4, %r11
	cmpq	%r11, %rdi
	jne	.LBB11_70
	vextracti128	$1, %ymm0, %xmm1
	vpaddq	%xmm1, %xmm0, %xmm0
	vpshufd	$238, %xmm0, %xmm1
	vpaddq	%xmm1, %xmm0, %xmm0
	vmovq	%xmm0, %rax
	cmpq	%rdi, %rdx
	je	.LBB11_73
	.p2align	4
.LBB11_72:
	xorl	%edx, %edx
	cmpb	%cl, (%rsi)
	sete	%dl
	addq	%rdx, %rax
	incq	%rsi
	cmpq	%r8, %rsi
	jne	.LBB11_72
.LBB11_73:
	addq	%r10, %rax
.LBB11_74:
	vmovaps	(%rsp), %xmm6
	vmovaps	16(%rsp), %xmm7
	vmovaps	32(%rsp), %xmm8
	vmovaps	48(%rsp), %xmm9
	vmovaps	64(%rsp), %xmm10
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	vzeroupper
	retq
.LBB11_75:
	addq	%rsi, %rdx
	jmp	.LBB11_8
.LBB11_76:
	addq	%r11, %rdx
	jmp	.LBB11_11
.LBB11_77:
	addq	%r11, %r9
	jmp	.LBB11_36
.LBB11_78:
	addq	%r11, %r9
	jmp	.LBB11_53
.Lfunc_end11:
	.seh_endproc

	.def	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw9find_sse2;
	.scl	3;
	.type	32;
	.endef
	.globl	__xmm@00000000000000010000000000000001
	.section	.rdata,"dr",discard,__xmm@00000000000000010000000000000001
	.p2align	4, 0x0
__xmm@00000000000000010000000000000001:
	.quad	1
	.quad	1
	.globl	__xmm@55555555555555555555555555555555
	.section	.rdata,"dr",discard,__xmm@55555555555555555555555555555555
	.p2align	4, 0x0
__xmm@55555555555555555555555555555555:
	.zero	16,85
	.globl	__xmm@33333333333333333333333333333333
	.section	.rdata,"dr",discard,__xmm@33333333333333333333333333333333
	.p2align	4, 0x0
__xmm@33333333333333333333333333333333:
	.zero	16,51
	.section	.text,"xr",one_only,_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw9find_sse2,unique,12
	.p2align	4
_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw9find_sse2:
.Lfunc_begin12:
.seh_proc _RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw9find_sse2
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$32, %rsp
	.seh_stackalloc 32
	movdqa	%xmm7, 16(%rsp)
	.seh_savexmm %xmm7, 16
	movdqa	%xmm6, (%rsp)
	.seh_savexmm %xmm6, 0
	.seh_endprologue
	cmpq	%r8, %rdx
	jae	.LBB12_1
	movzbl	%cl, %eax
	movd	%eax, %xmm0
	punpcklbw	%xmm0, %xmm0
	movq	%r8, %r11
	subq	%rdx, %r11
	cmpq	$15, %r11
	ja	.LBB12_9
	cmpq	$4, %r11
	jae	.LBB12_5
	xorl	%eax, %eax
	movq	%rdx, %r9
	jmp	.LBB12_8
.LBB12_1:
	xorl	%eax, %eax
	jmp	.LBB12_29
.LBB12_9:
	movq	%rdx, %r9
	andq	$-16, %r9
	addq	$16, %r9
	leaq	1(%rdx), %rsi
	cmpq	%rsi, %r9
	cmovaq	%r9, %rsi
	pshuflw	$0, %xmm0, %xmm1
	subq	%rdx, %rsi
	cmpq	$4, %rsi
	jae	.LBB12_11
	xorl	%r10d, %r10d
	movq	%rdx, %rax
	jmp	.LBB12_14
.LBB12_5:
	movl	%r11d, %r10d
	andl	$12, %r10d
	leaq	(%rdx,%r10), %r9
	pxor	%xmm1, %xmm1
	xorl	%eax, %eax
	movdqa	__xmm@00000000000000010000000000000001(%rip), %xmm3
	pxor	%xmm2, %xmm2
	.p2align	4
.LBB12_6:
	movzwl	(%rdx,%rax), %esi
	movd	%esi, %xmm4
	movzwl	2(%rdx,%rax), %esi
	movd	%esi, %xmm5
	pcmpeqb	%xmm0, %xmm4
	punpcklbw	%xmm4, %xmm4
	pshuflw	$212, %xmm4, %xmm4
	pshufd	$212, %xmm4, %xmm4
	pand	%xmm3, %xmm4
	paddq	%xmm4, %xmm2
	pcmpeqb	%xmm0, %xmm5
	punpcklbw	%xmm5, %xmm5
	pshuflw	$212, %xmm5, %xmm4
	pshufd	$212, %xmm4, %xmm4
	pand	%xmm3, %xmm4
	paddq	%xmm4, %xmm1
	addq	$4, %rax
	cmpq	%rax, %r10
	jne	.LBB12_6
	paddq	%xmm2, %xmm1
	pshufd	$238, %xmm1, %xmm0
	paddq	%xmm1, %xmm0
	movq	%xmm0, %rax
	cmpq	%r10, %r11
	je	.LBB12_29
	.p2align	4
.LBB12_8:
	xorl	%edx, %edx
	cmpb	%cl, (%r9)
	sete	%dl
	addq	%rdx, %rax
	incq	%r9
	cmpq	%r8, %r9
	jne	.LBB12_8
	jmp	.LBB12_29
.LBB12_11:
	movq	%rsi, %rdi
	andq	$-4, %rdi
	leaq	(%rdx,%rdi), %rax
	pxor	%xmm2, %xmm2
	xorl	%r10d, %r10d
	movdqa	__xmm@00000000000000010000000000000001(%rip), %xmm4
	pxor	%xmm3, %xmm3
	.p2align	4
.LBB12_12:
	movzwl	(%rdx,%r10), %ebx
	movd	%ebx, %xmm5
	movzwl	2(%rdx,%r10), %ebx
	movd	%ebx, %xmm6
	pcmpeqb	%xmm0, %xmm5
	punpcklbw	%xmm5, %xmm5
	pshuflw	$212, %xmm5, %xmm5
	pshufd	$212, %xmm5, %xmm5
	pand	%xmm4, %xmm5
	paddq	%xmm5, %xmm3
	pcmpeqb	%xmm0, %xmm6
	punpcklbw	%xmm6, %xmm6
	pshuflw	$212, %xmm6, %xmm5
	pshufd	$212, %xmm5, %xmm5
	pand	%xmm4, %xmm5
	paddq	%xmm5, %xmm2
	addq	$4, %r10
	cmpq	%r10, %rdi
	jne	.LBB12_12
	paddq	%xmm3, %xmm2
	pshufd	$238, %xmm2, %xmm3
	paddq	%xmm2, %xmm3
	movq	%xmm3, %r10
	cmpq	%rdi, %rsi
	je	.LBB12_15
	.p2align	4
.LBB12_14:
	xorl	%edx, %edx
	cmpb	%cl, (%rax)
	sete	%dl
	addq	%rdx, %r10
	incq	%rax
	cmpq	%r9, %rax
	jb	.LBB12_14
.LBB12_15:
	pshufd	$68, %xmm1, %xmm1
	cmpq	$64, %r11
	setae	%dl
	leaq	-64(%r8), %rax
	cmpq	%rax, %r9
	setbe	%r11b
	andb	%dl, %r11b
	cmpb	$1, %r11b
	jne	.LBB12_18
	movdqa	__xmm@55555555555555555555555555555555(%rip), %xmm2
	movdqa	__xmm@33333333333333333333333333333333(%rip), %xmm3
	movdqa	__xmm@0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f(%rip), %xmm4
	pxor	%xmm5, %xmm5
	.p2align	4
.LBB12_17:
	movdqa	(%r9), %xmm6
	pcmpeqb	%xmm1, %xmm6
	pmovmskb	%xmm6, %edx
	movdqa	16(%r9), %xmm6
	pcmpeqb	%xmm1, %xmm6
	pmovmskb	%xmm6, %r11d
	movdqa	32(%r9), %xmm6
	pcmpeqb	%xmm1, %xmm6
	pmovmskb	%xmm6, %esi
	movdqa	48(%r9), %xmm6
	pcmpeqb	%xmm1, %xmm6
	pmovmskb	%xmm6, %edi
	movd	%edx, %xmm6
	pinsrw	$1, %r11d, %xmm6
	pinsrw	$2, %esi, %xmm6
	pinsrw	$3, %edi, %xmm6
	movdqa	%xmm6, %xmm7
	psrlw	$1, %xmm7
	pand	%xmm2, %xmm7
	psubb	%xmm7, %xmm6
	movdqa	%xmm6, %xmm7
	pand	%xmm3, %xmm7
	psrlw	$2, %xmm6
	pand	%xmm3, %xmm6
	paddb	%xmm7, %xmm6
	movdqa	%xmm6, %xmm7
	psrlw	$4, %xmm7
	paddb	%xmm6, %xmm7
	pand	%xmm4, %xmm7
	movdqa	%xmm7, %xmm6
	psllw	$8, %xmm6
	paddb	%xmm7, %xmm6
	psrlw	$8, %xmm6
	packuswb	%xmm6, %xmm6
	punpckldq	%xmm5, %xmm6
	psadbw	%xmm5, %xmm6
	movq	%xmm6, %rdx
	addq	%rdx, %r10
	addq	$64, %r9
	cmpq	%rax, %r9
	jbe	.LBB12_17
.LBB12_18:
	leaq	-16(%r8), %rax
	cmpq	%rax, %r9
	ja	.LBB12_20
	.p2align	4
.LBB12_30:
	movdqu	(%r9), %xmm2
	pcmpeqb	%xmm1, %xmm2
	pmovmskb	%xmm2, %edx
	movl	%edx, %r11d
	shrl	%r11d
	andl	$21845, %r11d
	subl	%r11d, %edx
	movl	%edx, %r11d
	andl	$13107, %r11d
	shrl	$2, %edx
	andl	$13107, %edx
	addl	%r11d, %edx
	movl	%edx, %r11d
	shrl	$4, %r11d
	addl	%edx, %r11d
	andl	$3855, %r11d
	movl	%r11d, %edx
	shrl	$8, %edx
	addl	%r11d, %edx
	movzbl	%dl, %edx
	addq	%rdx, %r10
	addq	$16, %r9
	cmpq	%rax, %r9
	jbe	.LBB12_30
.LBB12_20:
	cmpq	%r8, %r9
	jae	.LBB12_21
	movq	%r8, %r11
	subq	%r9, %r11
	cmpq	$4, %r11
	jae	.LBB12_24
	xorl	%eax, %eax
	movq	%r9, %rdx
	jmp	.LBB12_27
.LBB12_21:
	xorl	%eax, %eax
	jmp	.LBB12_28
.LBB12_24:
	movq	%r11, %rsi
	andq	$-4, %rsi
	leaq	(%r9,%rsi), %rdx
	pxor	%xmm1, %xmm1
	xorl	%eax, %eax
	movdqa	__xmm@00000000000000010000000000000001(%rip), %xmm3
	pxor	%xmm2, %xmm2
	.p2align	4
.LBB12_25:
	movzwl	(%r9,%rax), %edi
	movd	%edi, %xmm4
	movzwl	2(%r9,%rax), %edi
	movd	%edi, %xmm5
	pcmpeqb	%xmm0, %xmm4
	punpcklbw	%xmm4, %xmm4
	pshuflw	$212, %xmm4, %xmm4
	pshufd	$212, %xmm4, %xmm4
	pand	%xmm3, %xmm4
	paddq	%xmm4, %xmm2
	pcmpeqb	%xmm0, %xmm5
	punpcklbw	%xmm5, %xmm5
	pshuflw	$212, %xmm5, %xmm4
	pshufd	$212, %xmm4, %xmm4
	pand	%xmm3, %xmm4
	paddq	%xmm4, %xmm1
	addq	$4, %rax
	cmpq	%rax, %rsi
	jne	.LBB12_25
	paddq	%xmm2, %xmm1
	pshufd	$238, %xmm1, %xmm0
	paddq	%xmm1, %xmm0
	movq	%xmm0, %rax
	cmpq	%rsi, %r11
	je	.LBB12_28
	.p2align	4
.LBB12_27:
	xorl	%r9d, %r9d
	cmpb	%cl, (%rdx)
	sete	%r9b
	addq	%r9, %rax
	incq	%rdx
	cmpq	%r8, %rdx
	jne	.LBB12_27
.LBB12_28:
	addq	%r10, %rax
.LBB12_29:
	movaps	(%rsp), %xmm6
	movaps	16(%rsp), %xmm7
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end12:
	.seh_endproc

	.section	.data,"dw",one_only,_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memchr2_raw2FN,unique,13
	.globl	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memchr2_raw2FN
	.p2align	3, 0x0
_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memchr2_raw2FN:
	.quad	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memchr2_raw6detect

	.section	.data,"dw",one_only,_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw2FN,unique,14
	.globl	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw2FN
	.p2align	3, 0x0
_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw2FN:
	.quad	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw6detect

	.section	.data,"dw",one_only,_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw2FN,unique,15
	.globl	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw2FN
	.p2align	3, 0x0
_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw2FN:
	.quad	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw6detect

	.section	.data,"dw",one_only,__imp__RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memchr2_raw2FN,unique,16
	.globl	__imp__RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memchr2_raw2FN
	.p2align	3, 0x0
__imp__RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memchr2_raw2FN:
	.quad	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memchr2_raw2FN

	.section	.data,"dw",one_only,__imp__RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw2FN,unique,17
	.globl	__imp__RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw2FN
	.p2align	3, 0x0
__imp__RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw2FN:
	.quad	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr11memrchr_raw2FN

	.section	.data,"dw",one_only,__imp__RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw2FN,unique,18
	.globl	__imp__RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw2FN
	.p2align	3, 0x0
__imp__RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw2FN:
	.quad	_RNvNvNtNtNtCsh0NEc3XTXYA_6memchr4arch6x86_646memchr9count_raw2FN

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
	.asciz	"S:\\GTOpen-research\\postflop-gpu-20261016\\build\\release\\deps\\postflop_autoresearch-ba6a3e8216b3a7e5.memchr-863cd9a4723da2aa.memchr.c628f2aafb811332-cgu.0.rcgu.o.rcgu.o"
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
	.short	0x7a
	.short	0x1605
	.long	0x0
	.asciz	"/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\std_detect\\src\\lib.rs\\@\\std_detect.1282e33b2634a6c5-cgu.0"
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
