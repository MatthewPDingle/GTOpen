	.def	@feat.00;
	.scl	3;
	.type	0;
	.endef
	.globl	@feat.00
@feat.00 = 0
	.file	"itoa.146284499976ff7d-cgu.0"
	.def	_RNvXsu_Cs1KvuFdKMjOj_4itoayNtB5_8Unsigned3fmt;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXsu_Cs1KvuFdKMjOj_4itoayNtB5_8Unsigned3fmt,unique,0
	.globl	_RNvXsu_Cs1KvuFdKMjOj_4itoayNtB5_8Unsigned3fmt
	.p2align	4
_RNvXsu_Cs1KvuFdKMjOj_4itoayNtB5_8Unsigned3fmt:
.seh_proc _RNvXsu_Cs1KvuFdKMjOj_4itoayNtB5_8Unsigned3fmt
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	%rdx, %r8
	movl	$20, %eax
	movq	%rcx, %rdx
	cmpq	$1000, %rcx
	jb	.LBB0_6
	movabsq	$3777893186295716171, %rdx
	movq	%rcx, %rax
	mulq	%rdx
	shrq	$11, %rdx
	imull	$10000, %edx, %eax
	movl	%ecx, %r9d
	subl	%eax, %r9d
	imull	$5243, %r9d, %eax
	shrl	$19, %eax
	imull	$-100, %eax, %r10d
	addl	%r9d, %r10d
	leaq	_RNvCs1KvuFdKMjOj_4itoa13DECIMAL_PAIRS(%rip), %r9
	movzwl	(%r9,%rax,2), %eax
	movd	%eax, %xmm0
	pinsrw	$1, (%r9,%r10,2), %xmm0
	movd	%xmm0, 16(%r8)
	movl	$16, %eax
	cmpq	$9999999, %rcx
	jbe	.LBB0_6
	movabsq	$3689348814741911, %r10
	movq	%rdx, %rax
	movq	%rdx, %r11
	mulq	%r10
	shrl	%edx
	imull	$10000, %edx, %eax
	subl	%eax, %r11d
	imull	$5243, %r11d, %r10d
	shrl	$19, %r10d
	movabsq	$-6067343680855748867, %rdx
	movq	%rcx, %rax
	mulq	%rdx
	imull	$-100, %r10d, %eax
	addl	%r11d, %eax
	shrq	$26, %rdx
	movzwl	(%r9,%r10,2), %r10d
	movd	%r10d, %xmm0
	pinsrw	$1, (%r9,%rax,2), %xmm0
	movd	%xmm0, 12(%r8)
	movq	%rcx, %r10
	shrq	$11, %r10
	movl	$12, %eax
	cmpq	$48828125, %r10
	jb	.LBB0_6
	movabsq	$1844674407370956, %r10
	movq	%rdx, %rax
	movq	%rdx, %r11
	mulq	%r10
	imull	$10000, %edx, %eax
	subl	%eax, %r11d
	imull	$5243, %r11d, %r10d
	shrl	$19, %r10d
	imull	$-100, %r10d, %esi
	addl	%r11d, %esi
	movabsq	$2535301200456458803, %rdx
	movq	%rcx, %rax
	mulq	%rdx
	shrq	$37, %rdx
	movzwl	(%r9,%r10,2), %eax
	movd	%eax, %xmm0
	pinsrw	$1, (%r9,%rsi,2), %xmm0
	movd	%xmm0, 8(%r8)
	movl	$8, %eax
	movabsq	$1000000000000000, %r10
	cmpq	%r10, %rcx
	jb	.LBB0_6
	imulq	$27487791, %rdx, %rax
	shrq	$38, %rax
	imull	$10000, %eax, %eax
	subl	%eax, %edx
	imull	$5243, %edx, %r10d
	shrl	$19, %r10d
	imull	$-100, %r10d, %r11d
	addl	%edx, %r11d
	movabsq	$4153837486827862103, %rdx
	movq	%rcx, %rax
	mulq	%rdx
	shrq	$51, %rdx
	movzwl	(%r9,%r10,2), %eax
	movd	%eax, %xmm0
	pinsrw	$1, (%r9,%r11,2), %xmm0
	movd	%xmm0, 4(%r8)
	movl	$4, %eax
	movabsq	$-8446744073709551616, %r10
	cmpq	%r10, %rcx
	jb	.LBB0_6
	imull	$5243, %edx, %eax
	shrl	$19, %eax
	imull	$-100, %eax, %r10d
	addl	%edx, %r10d
	movzwl	(%r9,%rax,2), %eax
	movd	%eax, %xmm0
	pinsrw	$1, (%r9,%r10,2), %xmm0
	movd	%xmm0, (%r8)
	xorl	%edx, %edx
	xorl	%eax, %eax
	jmp	.LBB0_8
.LBB0_6:
	cmpq	$9, %rdx
	jbe	.LBB0_8
	imull	$5243, %edx, %r9d
	shrl	$19, %r9d
	imull	$-100, %r9d, %r10d
	addl	%edx, %r10d
	leaq	_RNvCs1KvuFdKMjOj_4itoa13DECIMAL_PAIRS(%rip), %rdx
	movzwl	(%rdx,%r10,2), %edx
	movw	%dx, -2(%r8,%rax)
	addq	$-2, %rax
	movq	%r9, %rdx
.LBB0_8:
	testq	%rcx, %rcx
	je	.LBB0_11
	testq	%rdx, %rdx
	jne	.LBB0_11
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB0_11:
	decq	%rax
	cmpq	$20, %rax
	jae	.LBB0_13
	orb	$48, %dl
	movb	%dl, (%r8,%rax)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB0_13:
	leaq	anon.9e5ba71fe29651cc237134b2943625ef.5(%rip), %r8
	movl	$20, %edx
	movq	$-1, %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	ud2
	.seh_endproc

	.section	.rdata,"dr",one_only,anon.9e5ba71fe29651cc237134b2943625ef.0,unique,1
anon.9e5ba71fe29651cc237134b2943625ef.0:
	.asciz	"C:\\Users\\there\\.cargo\\registry\\src\\index.crates.io-1949cf8c6b5b557f\\itoa-1.0.18\\src\\lib.rs"

	.section	.rdata,"dr",one_only,_RNvCs1KvuFdKMjOj_4itoa13DECIMAL_PAIRS,unique,2
	.globl	_RNvCs1KvuFdKMjOj_4itoa13DECIMAL_PAIRS
	.p2align	1, 0x0
_RNvCs1KvuFdKMjOj_4itoa13DECIMAL_PAIRS:
	.ascii	"00010203040506070809101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899"

	.section	.rdata,"dr",one_only,anon.9e5ba71fe29651cc237134b2943625ef.5,unique,3
	.p2align	3, 0x0
anon.9e5ba71fe29651cc237134b2943625ef.5:
	.quad	anon.9e5ba71fe29651cc237134b2943625ef.0
	.asciz	"Z\000\000\000\000\000\000\000L\001\000\000\001\000\000"

	.section	.data,"dw",one_only,__imp__RNvCs1KvuFdKMjOj_4itoa13DECIMAL_PAIRS,unique,4
	.globl	__imp__RNvCs1KvuFdKMjOj_4itoa13DECIMAL_PAIRS
	.p2align	3, 0x0
__imp__RNvCs1KvuFdKMjOj_4itoa13DECIMAL_PAIRS:
	.quad	_RNvCs1KvuFdKMjOj_4itoa13DECIMAL_PAIRS

