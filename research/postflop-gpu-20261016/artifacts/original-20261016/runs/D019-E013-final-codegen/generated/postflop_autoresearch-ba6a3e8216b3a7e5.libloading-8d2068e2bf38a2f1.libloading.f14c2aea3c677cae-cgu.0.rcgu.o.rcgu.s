	.def	@feat.00;
	.scl	3;
	.type	0;
	.endef
	.globl	@feat.00
@feat.00 = 0
	.file	"libloading.f14c2aea3c677cae-cgu.0"
	.def	_RNvMsa_NtNtCskIq6Fm6qntW_10libloading2os7windowsNtB5_14ErrorModeGuard3new;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMsa_NtNtCskIq6Fm6qntW_10libloading2os7windowsNtB5_14ErrorModeGuard3new,unique,0
	.globl	_RNvMsa_NtNtCskIq6Fm6qntW_10libloading2os7windowsNtB5_14ErrorModeGuard3new
	.p2align	4
_RNvMsa_NtNtCskIq6Fm6qntW_10libloading2os7windowsNtB5_14ErrorModeGuard3new:
.Lfunc_begin0:
.seh_proc _RNvMsa_NtNtCskIq6Fm6qntW_10libloading2os7windowsNtB5_14ErrorModeGuard3new
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movl	$0, 36(%rsp)
	leaq	36(%rsp), %rdx
	movl	$1, %ecx
	callq	*__imp_SetThreadErrorMode(%rip)
	testl	%eax, %eax
	setne	%al
	movl	36(%rsp), %edx
	cmpl	$1, %edx
	setne	%cl
	andb	%al, %cl
	movzbl	%cl, %eax
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end0:
	.seh_endproc

	.def	_RNvNtCskIq6Fm6qntW_10libloading4util16check_null_bytes;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNtCskIq6Fm6qntW_10libloading4util16check_null_bytes,unique,1
	.globl	_RNvNtCskIq6Fm6qntW_10libloading4util16check_null_bytes
	.p2align	4
_RNvNtCskIq6Fm6qntW_10libloading4util16check_null_bytes:
.Lfunc_begin1:
.seh_proc _RNvNtCskIq6Fm6qntW_10libloading4util16check_null_bytes
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	.seh_endprologue
	movq	%rcx, %rax
	testq	%r8, %r8
	je	.LBB1_6
	leaq	-1(%r8), %rcx
	cmpq	$16, %r8
	ja	.LBB1_7
	testq	%rcx, %rcx
	je	.LBB1_19
	xorl	%r8d, %r8d
	.p2align	4
.LBB1_4:
	cmpb	$0, (%rdx,%r8)
	je	.LBB1_22
	incq	%r8
	cmpq	%r8, %rcx
	jne	.LBB1_4
	jmp	.LBB1_19
.LBB1_6:
	movb	$0, 4(%rax)
	jmp	.LBB1_20
.LBB1_7:
	leaq	7(%rdx), %r9
	andq	$-8, %r9
	subq	%rdx, %r9
	jne	.LBB1_12
	addq	$-17, %r8
	xorl	%r9d, %r9d
.LBB1_9:
	movabsq	$72340172838076672, %r10
	movabsq	$-9187201950435737472, %r11
	.p2align	4
.LBB1_10:
	movq	(%rdx,%r9), %rsi
	movq	8(%rdx,%r9), %rdi
	movq	%r10, %rbx
	subq	%rsi, %rbx
	orq	%rsi, %rbx
	movq	%r10, %rsi
	subq	%rdi, %rsi
	orq	%rdi, %rsi
	andq	%rbx, %rsi
	notq	%rsi
	testq	%r11, %rsi
	jne	.LBB1_18
	addq	$16, %r9
	cmpq	%r8, %r9
	jbe	.LBB1_10
	jmp	.LBB1_18
.LBB1_12:
	xorl	%r10d, %r10d
	.p2align	4
.LBB1_13:
	cmpb	$0, (%rdx,%r10)
	je	.LBB1_22
	incq	%r10
	cmpq	%r10, %r9
	jne	.LBB1_13
	addq	$-17, %r8
	cmpq	%r8, %r9
	ja	.LBB1_18
	jmp	.LBB1_9
	.p2align	4
.LBB1_16:
	cmpb	$0, (%rdx,%r9)
	je	.LBB1_22
	incq	%r9
.LBB1_18:
	cmpq	%r9, %rcx
	jne	.LBB1_16
.LBB1_19:
	cmpb	$0, (%rdx,%rcx)
	sete	4(%rax)
.LBB1_20:
	movl	$-1, %ecx
	jmp	.LBB1_21
.LBB1_22:
	movl	$15, %ecx
.LBB1_21:
	movl	%ecx, (%rax)
	.seh_startepilogue
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end1:
	.seh_endproc

	.def	_RNvXs1_NtNtCskIq6Fm6qntW_10libloading2os7windowsNtB5_7LibraryNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1_NtNtCskIq6Fm6qntW_10libloading2os7windowsNtB5_7LibraryNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop,unique,2
	.globl	_RNvXs1_NtNtCskIq6Fm6qntW_10libloading2os7windowsNtB5_7LibraryNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop
	.p2align	4
_RNvXs1_NtNtCskIq6Fm6qntW_10libloading2os7windowsNtB5_7LibraryNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop:
.Lfunc_begin2:
	movq	(%rcx), %rcx
	rex64 jmpq	*__imp_FreeLibrary(%rip)
.Lfunc_end2:

	.def	_RNvXs6_NtCskIq6Fm6qntW_10libloading5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs6_NtCskIq6Fm6qntW_10libloading5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt,unique,3
	.globl	_RNvXs6_NtCskIq6Fm6qntW_10libloading5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt
	.p2align	4
_RNvXs6_NtCskIq6Fm6qntW_10libloading5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt:
.Lfunc_begin3:
	movl	(%rcx), %r8d
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	.LJTI3_0(%rip), %rdx
	movslq	(%rdx,%r8,4), %r8
	addq	%rdx, %r8
	jmpq	*%r8
.LBB3_1:
	leaq	anon.cf931dd528d6f8ba59338b2d8a599017.5(%rip), %rdx
	movl	$13, %r8d
	rex64 jmpq	*%rax
.LBB3_15:
	leaq	anon.cf931dd528d6f8ba59338b2d8a599017.19(%rip), %rdx
	movl	$35, %r8d
	rex64 jmpq	*%rax
.LBB3_12:
	leaq	anon.cf931dd528d6f8ba59338b2d8a599017.16(%rip), %rdx
	movl	$58, %r8d
	rex64 jmpq	*%rax
.LBB3_5:
	leaq	anon.cf931dd528d6f8ba59338b2d8a599017.9(%rip), %rdx
	movl	$14, %r8d
	rex64 jmpq	*%rax
.LBB3_13:
	leaq	anon.cf931dd528d6f8ba59338b2d8a599017.17(%rip), %rdx
	movl	$18, %r8d
	rex64 jmpq	*%rax
.LBB3_10:
	leaq	anon.cf931dd528d6f8ba59338b2d8a599017.14(%rip), %rdx
	movl	$69, %r8d
	rex64 jmpq	*%rax
.LBB3_3:
	leaq	anon.cf931dd528d6f8ba59338b2d8a599017.7(%rip), %rdx
	movl	$12, %r8d
	rex64 jmpq	*%rax
.LBB3_16:
	leaq	anon.cf931dd528d6f8ba59338b2d8a599017.20(%rip), %rdx
	movl	$34, %r8d
	rex64 jmpq	*%rax
.LBB3_4:
	leaq	anon.cf931dd528d6f8ba59338b2d8a599017.8(%rip), %rdx
	movl	$49, %r8d
	rex64 jmpq	*%rax
.LBB3_8:
	leaq	anon.cf931dd528d6f8ba59338b2d8a599017.12(%rip), %rdx
	movl	$58, %r8d
	rex64 jmpq	*%rax
.LBB3_2:
	leaq	anon.cf931dd528d6f8ba59338b2d8a599017.6(%rip), %rdx
	movl	$50, %r8d
	rex64 jmpq	*%rax
.LBB3_6:
	leaq	anon.cf931dd528d6f8ba59338b2d8a599017.10(%rip), %rdx
	movl	$51, %r8d
	rex64 jmpq	*%rax
.LBB3_14:
	leaq	anon.cf931dd528d6f8ba59338b2d8a599017.18(%rip), %rdx
	movl	$55, %r8d
	rex64 jmpq	*%rax
.LBB3_7:
	leaq	anon.cf931dd528d6f8ba59338b2d8a599017.11(%rip), %rdx
	movl	$21, %r8d
	rex64 jmpq	*%rax
.LBB3_11:
	leaq	anon.cf931dd528d6f8ba59338b2d8a599017.15(%rip), %rdx
	movl	$21, %r8d
	rex64 jmpq	*%rax
.LBB3_9:
	leaq	anon.cf931dd528d6f8ba59338b2d8a599017.13(%rip), %rdx
	movl	$25, %r8d
	rex64 jmpq	*%rax
.Lfunc_end3:
	.section	.rdata,"dr",associative,_RNvXs6_NtCskIq6Fm6qntW_10libloading5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt,unique,4
	.p2align	2, 0x0
.LJTI3_0:
	.long	.LBB3_1-.LJTI3_0
	.long	.LBB3_2-.LJTI3_0
	.long	.LBB3_3-.LJTI3_0
	.long	.LBB3_4-.LJTI3_0
	.long	.LBB3_5-.LJTI3_0
	.long	.LBB3_6-.LJTI3_0
	.long	.LBB3_7-.LJTI3_0
	.long	.LBB3_8-.LJTI3_0
	.long	.LBB3_9-.LJTI3_0
	.long	.LBB3_10-.LJTI3_0
	.long	.LBB3_11-.LJTI3_0
	.long	.LBB3_12-.LJTI3_0
	.long	.LBB3_13-.LJTI3_0
	.long	.LBB3_14-.LJTI3_0
	.long	.LBB3_15-.LJTI3_0
	.long	.LBB3_16-.LJTI3_0

	.def	_RNvXsb_NtNtCskIq6Fm6qntW_10libloading2os7windowsNtB5_14ErrorModeGuardNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXsb_NtNtCskIq6Fm6qntW_10libloading2os7windowsNtB5_14ErrorModeGuardNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop,unique,5
	.globl	_RNvXsb_NtNtCskIq6Fm6qntW_10libloading2os7windowsNtB5_14ErrorModeGuardNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop
	.p2align	4
_RNvXsb_NtNtCskIq6Fm6qntW_10libloading2os7windowsNtB5_14ErrorModeGuardNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop:
.Lfunc_begin4:
	movl	(%rcx), %ecx
	xorl	%edx, %edx
	rex64 jmpq	*__imp_SetThreadErrorMode(%rip)
.Lfunc_end4:

	.section	.rdata,"dr",one_only,anon.cf931dd528d6f8ba59338b2d8a599017.5,unique,6
anon.cf931dd528d6f8ba59338b2d8a599017.5:
	.ascii	"dlopen failed"

	.section	.rdata,"dr",one_only,anon.cf931dd528d6f8ba59338b2d8a599017.6,unique,7
anon.cf931dd528d6f8ba59338b2d8a599017.6:
	.ascii	"dlopen failed, but system did not report the error"

	.section	.rdata,"dr",one_only,anon.cf931dd528d6f8ba59338b2d8a599017.7,unique,8
anon.cf931dd528d6f8ba59338b2d8a599017.7:
	.ascii	"dlsym failed"

	.section	.rdata,"dr",one_only,anon.cf931dd528d6f8ba59338b2d8a599017.8,unique,9
anon.cf931dd528d6f8ba59338b2d8a599017.8:
	.ascii	"dlsym failed, but system did not report the error"

	.section	.rdata,"dr",one_only,anon.cf931dd528d6f8ba59338b2d8a599017.9,unique,10
anon.cf931dd528d6f8ba59338b2d8a599017.9:
	.ascii	"dlclose failed"

	.section	.rdata,"dr",one_only,anon.cf931dd528d6f8ba59338b2d8a599017.10,unique,11
anon.cf931dd528d6f8ba59338b2d8a599017.10:
	.ascii	"dlclose failed, but system did not report the error"

	.section	.rdata,"dr",one_only,anon.cf931dd528d6f8ba59338b2d8a599017.11,unique,12
anon.cf931dd528d6f8ba59338b2d8a599017.11:
	.ascii	"LoadLibraryExW failed"

	.section	.rdata,"dr",one_only,anon.cf931dd528d6f8ba59338b2d8a599017.12,unique,13
anon.cf931dd528d6f8ba59338b2d8a599017.12:
	.ascii	"LoadLibraryExW failed, but system did not report the error"

	.section	.rdata,"dr",one_only,anon.cf931dd528d6f8ba59338b2d8a599017.13,unique,14
anon.cf931dd528d6f8ba59338b2d8a599017.13:
	.ascii	"GetModuleHandleExW failed"

	.section	.rdata,"dr",one_only,anon.cf931dd528d6f8ba59338b2d8a599017.14,unique,15
anon.cf931dd528d6f8ba59338b2d8a599017.14:
	.ascii	"GetModuleHandleExWUnknown failed, but system did not report the error"

	.section	.rdata,"dr",one_only,anon.cf931dd528d6f8ba59338b2d8a599017.15,unique,16
anon.cf931dd528d6f8ba59338b2d8a599017.15:
	.ascii	"GetProcAddress failed"

	.section	.rdata,"dr",one_only,anon.cf931dd528d6f8ba59338b2d8a599017.16,unique,17
anon.cf931dd528d6f8ba59338b2d8a599017.16:
	.ascii	"GetProcAddress failed, but system did not report the error"

	.section	.rdata,"dr",one_only,anon.cf931dd528d6f8ba59338b2d8a599017.17,unique,18
anon.cf931dd528d6f8ba59338b2d8a599017.17:
	.ascii	"FreeLibrary failed"

	.section	.rdata,"dr",one_only,anon.cf931dd528d6f8ba59338b2d8a599017.18,unique,19
anon.cf931dd528d6f8ba59338b2d8a599017.18:
	.ascii	"FreeLibrary failed, but system did not report the error"

	.section	.rdata,"dr",one_only,anon.cf931dd528d6f8ba59338b2d8a599017.19,unique,20
anon.cf931dd528d6f8ba59338b2d8a599017.19:
	.ascii	"requested type cannot possibly work"

	.section	.rdata,"dr",one_only,anon.cf931dd528d6f8ba59338b2d8a599017.20,unique,21
anon.cf931dd528d6f8ba59338b2d8a599017.20:
	.ascii	"interior zero element in parameter"

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
	.asciz	"S:\\GTOpen-research\\postflop-gpu-20261016\\build\\release\\deps\\postflop_autoresearch-ba6a3e8216b3a7e5.libloading-8d2068e2bf38a2f1.libloading.f14c2aea3c677cae-cgu.0.rcgu.o.rcgu.o"
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
