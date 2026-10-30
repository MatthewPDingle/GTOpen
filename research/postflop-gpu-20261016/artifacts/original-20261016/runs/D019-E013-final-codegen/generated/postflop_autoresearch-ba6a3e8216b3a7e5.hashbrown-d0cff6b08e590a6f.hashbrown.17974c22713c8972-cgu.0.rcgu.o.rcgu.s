	.def	@feat.00;
	.scl	3;
	.type	0;
	.endef
	.globl	@feat.00
@feat.00 = 0
	.file	"hashbrown.17974c22713c8972-cgu.0"
	.def	_RNvMNtCs21zBS6O3Cve_9hashbrown3rawNtB2_11Fallibility17capacity_overflow;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMNtCs21zBS6O3Cve_9hashbrown3rawNtB2_11Fallibility17capacity_overflow,unique,0
	.globl	_RNvMNtCs21zBS6O3Cve_9hashbrown3rawNtB2_11Fallibility17capacity_overflow
	.p2align	4
_RNvMNtCs21zBS6O3Cve_9hashbrown3rawNtB2_11Fallibility17capacity_overflow:
.Lfunc_begin0:
	.cv_func_id 0
	.cv_file	1 "/rust/deps\\hashbrown-0.17.1/src\\raw.rs" "0C8AD353BA95817E72B0A8FEA48FA2599099EA3DEF374F254AB6402A9C468D22" 3
	.cv_loc	0 1 33 0
.seh_proc _RNvMNtCs21zBS6O3Cve_9hashbrown3rawNtB2_11Fallibility17capacity_overflow
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	32(%rsp), %rbp
	.seh_setframe %rbp, 32
	.seh_endprologue
.Ltmp0:
	.cv_loc	0 1 34 0
	testb	%cl, %cl
	jne	.LBB0_1
	.cv_loc	0 1 38 0
	xorl	%eax, %eax
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.LBB0_1:
	.cv_loc	0 1 36 0
	leaq	anon.d193f36614681b92f1ac4673d738a012.0.llvm.1109614654472640928(%rip), %rcx
	leaq	anon.d193f36614681b92f1ac4673d738a012.2.llvm.1109614654472640928(%rip), %r8
	movl	$57, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking9panic_fmt
	ud2
.Ltmp1:
.Lfunc_end0:
	.seh_endproc

	.def	_RNvMNtCs21zBS6O3Cve_9hashbrown3rawNtB2_11Fallibility9alloc_err;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMNtCs21zBS6O3Cve_9hashbrown3rawNtB2_11Fallibility9alloc_err,unique,1
	.globl	_RNvMNtCs21zBS6O3Cve_9hashbrown3rawNtB2_11Fallibility9alloc_err
	.p2align	4
_RNvMNtCs21zBS6O3Cve_9hashbrown3rawNtB2_11Fallibility9alloc_err:
.Lfunc_begin1:
	.cv_func_id 1
	.cv_loc	1 1 42 0
.seh_proc _RNvMNtCs21zBS6O3Cve_9hashbrown3rawNtB2_11Fallibility9alloc_err
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	32(%rsp), %rbp
	.seh_setframe %rbp, 32
	.seh_endprologue
.Ltmp2:
	.cv_loc	1 1 43 0
	testb	%cl, %cl
	jne	.LBB1_1
	.cv_loc	1 1 47 0
	movq	%rdx, %rax
	movq	%r8, %rdx
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.LBB1_1:
	.cv_loc	1 1 45 0
	movq	%rdx, %rcx
	movq	%r8, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	ud2
.Ltmp3:
.Lfunc_end1:
	.seh_endproc

	.section	.rdata,"dr",one_only,anon.d193f36614681b92f1ac4673d738a012.0.llvm.1109614654472640928,unique,2
	.globl	anon.d193f36614681b92f1ac4673d738a012.0.llvm.1109614654472640928
anon.d193f36614681b92f1ac4673d738a012.0.llvm.1109614654472640928:
	.ascii	"Hash table capacity overflow"

	.section	.rdata,"dr",one_only,anon.d193f36614681b92f1ac4673d738a012.1.llvm.1109614654472640928,unique,3
	.globl	anon.d193f36614681b92f1ac4673d738a012.1.llvm.1109614654472640928
anon.d193f36614681b92f1ac4673d738a012.1.llvm.1109614654472640928:
	.asciz	"/rust/deps\\hashbrown-0.17.1\\src\\raw.rs"

	.section	.rdata,"dr",one_only,anon.d193f36614681b92f1ac4673d738a012.2.llvm.1109614654472640928,unique,4
	.globl	anon.d193f36614681b92f1ac4673d738a012.2.llvm.1109614654472640928
	.p2align	3, 0x0
anon.d193f36614681b92f1ac4673d738a012.2.llvm.1109614654472640928:
	.quad	anon.d193f36614681b92f1ac4673d738a012.1.llvm.1109614654472640928
	.asciz	"&\000\000\000\000\000\000\000$\000\000\000(\000\000"

	.section	.data,"dw",one_only,__imp_anon.d193f36614681b92f1ac4673d738a012.0.llvm.1109614654472640928,unique,5
	.globl	__imp_anon.d193f36614681b92f1ac4673d738a012.0.llvm.1109614654472640928
	.p2align	3, 0x0
__imp_anon.d193f36614681b92f1ac4673d738a012.0.llvm.1109614654472640928:
	.quad	anon.d193f36614681b92f1ac4673d738a012.0.llvm.1109614654472640928

	.section	.data,"dw",one_only,__imp_anon.d193f36614681b92f1ac4673d738a012.1.llvm.1109614654472640928,unique,6
	.globl	__imp_anon.d193f36614681b92f1ac4673d738a012.1.llvm.1109614654472640928
	.p2align	3, 0x0
__imp_anon.d193f36614681b92f1ac4673d738a012.1.llvm.1109614654472640928:
	.quad	anon.d193f36614681b92f1ac4673d738a012.1.llvm.1109614654472640928

	.section	.data,"dw",one_only,__imp_anon.d193f36614681b92f1ac4673d738a012.2.llvm.1109614654472640928,unique,7
	.globl	__imp_anon.d193f36614681b92f1ac4673d738a012.2.llvm.1109614654472640928
	.p2align	3, 0x0
__imp_anon.d193f36614681b92f1ac4673d738a012.2.llvm.1109614654472640928:
	.quad	anon.d193f36614681b92f1ac4673d738a012.2.llvm.1109614654472640928

	.section	.debug$S,"dr"
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp5-.Ltmp4
.Ltmp4:
	.short	.Ltmp7-.Ltmp6
.Ltmp6:
	.short	4353
	.long	0
	.asciz	"S:\\GTOpen-research\\postflop-gpu-20261016\\build\\release\\deps\\postflop_autoresearch-ba6a3e8216b3a7e5.hashbrown-d0cff6b08e590a6f.hashbrown.17974c22713c8972-cgu.0.rcgu.o.rcgu.o"
	.p2align	2, 0x0
.Ltmp7:
	.short	.Ltmp9-.Ltmp8
.Ltmp8:
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
.Ltmp9:
.Ltmp5:
	.p2align	2, 0x0
	.section	.debug$S,"dr",associative,_RNvMNtCs21zBS6O3Cve_9hashbrown3rawNtB2_11Fallibility17capacity_overflow
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp11-.Ltmp10
.Ltmp10:
	.short	.Ltmp13-.Ltmp12
.Ltmp12:
	.short	4423
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end0-_RNvMNtCs21zBS6O3Cve_9hashbrown3rawNtB2_11Fallibility17capacity_overflow
	.long	0
	.long	0
	.long	4099
	.secrel32	_RNvMNtCs21zBS6O3Cve_9hashbrown3rawNtB2_11Fallibility17capacity_overflow
	.secidx	_RNvMNtCs21zBS6O3Cve_9hashbrown3rawNtB2_11Fallibility17capacity_overflow
	.byte	129
	.asciz	"hashbrown::raw::Fallibility::capacity_overflow"
	.p2align	2, 0x0
.Ltmp13:
	.short	.Ltmp15-.Ltmp14
.Ltmp14:
	.short	4114
	.long	40
	.long	0
	.long	0
	.long	0
	.long	0
	.short	0
	.long	1220608
	.p2align	2, 0x0
.Ltmp15:
	.short	2
	.short	4431
.Ltmp11:
	.p2align	2, 0x0
	.cv_linetable	0, _RNvMNtCs21zBS6O3Cve_9hashbrown3rawNtB2_11Fallibility17capacity_overflow, .Lfunc_end0
	.section	.debug$S,"dr",associative,_RNvMNtCs21zBS6O3Cve_9hashbrown3rawNtB2_11Fallibility9alloc_err
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp17-.Ltmp16
.Ltmp16:
	.short	.Ltmp19-.Ltmp18
.Ltmp18:
	.short	4423
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end1-_RNvMNtCs21zBS6O3Cve_9hashbrown3rawNtB2_11Fallibility9alloc_err
	.long	0
	.long	0
	.long	4100
	.secrel32	_RNvMNtCs21zBS6O3Cve_9hashbrown3rawNtB2_11Fallibility9alloc_err
	.secidx	_RNvMNtCs21zBS6O3Cve_9hashbrown3rawNtB2_11Fallibility9alloc_err
	.byte	129
	.asciz	"hashbrown::raw::Fallibility::alloc_err"
	.p2align	2, 0x0
.Ltmp19:
	.short	.Ltmp21-.Ltmp20
.Ltmp20:
	.short	4114
	.long	40
	.long	0
	.long	0
	.long	0
	.long	0
	.short	0
	.long	1220608
	.p2align	2, 0x0
.Ltmp21:
	.short	2
	.short	4431
.Ltmp17:
	.p2align	2, 0x0
	.cv_linetable	1, _RNvMNtCs21zBS6O3Cve_9hashbrown3rawNtB2_11Fallibility9alloc_err, .Lfunc_end1
	.section	.debug$S,"dr"
	.cv_filechecksums
	.cv_stringtable
	.long	241
	.long	.Ltmp23-.Ltmp22
.Ltmp22:
	.short	.Ltmp25-.Ltmp24
.Ltmp24:
	.short	4428
	.long	4104
	.p2align	2, 0x0
.Ltmp25:
.Ltmp23:
	.p2align	2, 0x0
	.section	.debug$T,"dr"
	.p2align	2, 0x0
	.long	4
	.short	0x22
	.short	0x1605
	.long	0x0
	.asciz	"hashbrown::raw::Fallibility"
	.short	0x6
	.short	0x1201
	.long	0x0
	.short	0xe
	.short	0x1008
	.long	0x3
	.byte	0x0
	.byte	0x0
	.short	0x0
	.long	0x1001
	.short	0x1e
	.short	0x1601
	.long	0x1000
	.long	0x1002
	.asciz	"capacity_overflow"
	.byte	242
	.byte	241
	.short	0x16
	.short	0x1601
	.long	0x1000
	.long	0x1002
	.asciz	"alloc_err"
	.byte	242
	.byte	241
	.short	0x22
	.short	0x1605
	.long	0x0
	.asciz	"/rust/deps\\hashbrown-0.17.1"
	.short	0x52
	.short	0x1605
	.long	0x0
	.asciz	"/rust/deps\\hashbrown-0.17.1\\src\\lib.rs\\@\\hashbrown.17974c22713c8972-cgu.0"
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
	.long	0x1005
	.long	0x1007
	.long	0x1006
	.long	0x1007
	.long	0x1007
	.byte	242
	.byte	241
