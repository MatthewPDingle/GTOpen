	.def	@feat.00;
	.scl	3;
	.type	0;
	.endef
	.globl	@feat.00
@feat.00 = 0
	.file	"rayon.abadaf25a99c9832-cgu.0"
	.def	_RNvXs7_NtCseJQ6qkLJTIA_5rayon5rangehNtNtB5_7private19IndexedRangeInteger3len;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs7_NtCseJQ6qkLJTIA_5rayon5rangehNtNtB5_7private19IndexedRangeInteger3len,unique,0
	.globl	_RNvXs7_NtCseJQ6qkLJTIA_5rayon5rangehNtNtB5_7private19IndexedRangeInteger3len
	.p2align	4
_RNvXs7_NtCseJQ6qkLJTIA_5rayon5rangehNtNtB5_7private19IndexedRangeInteger3len:
	movzbl	1(%rcx), %eax
	xorl	%edx, %edx
	subb	(%rcx), %al
	movzbl	%al, %eax
	cmovbl	%edx, %eax
	movzbl	%al, %eax
	retq

	.def	_RNvXs8_NtCseJQ6qkLJTIA_5rayon5rangeINtB5_12IterProducerhENtNtNtB7_4iter8plumbing8Producer8split_at;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs8_NtCseJQ6qkLJTIA_5rayon5rangeINtB5_12IterProducerhENtNtNtB7_4iter8plumbing8Producer8split_at,unique,1
	.globl	_RNvXs8_NtCseJQ6qkLJTIA_5rayon5rangeINtB5_12IterProducerhENtNtNtB7_4iter8plumbing8Producer8split_at
	.p2align	4
_RNvXs8_NtCseJQ6qkLJTIA_5rayon5rangeINtB5_12IterProducerhENtNtNtB7_4iter8plumbing8Producer8split_at:
.seh_proc _RNvXs8_NtCseJQ6qkLJTIA_5rayon5rangeINtB5_12IterProducerhENtNtNtB7_4iter8plumbing8Producer8split_at
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	xorl	%eax, %eax
	movl	%edx, %r9d
	subb	%cl, %r9b
	movzbl	%r9b, %r9d
	cmovbl	%eax, %r9d
	movzbl	%r9b, %eax
	cmpq	%rax, %r8
	ja	.LBB1_1
	addb	%cl, %r8b
	movzbl	%dl, %eax
	shll	$24, %eax
	movzbl	%r8b, %edx
	movl	%edx, %r8d
	shll	$16, %r8d
	orl	%eax, %r8d
	shll	$8, %edx
	orl	%r8d, %edx
	movzbl	%cl, %eax
	orl	%edx, %eax
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.LBB1_1:
	leaq	anon.322f28e6360e11fa98bf96d410f43235.11.llvm.4152402689123185488(%rip), %rcx
	leaq	anon.322f28e6360e11fa98bf96d410f43235.13.llvm.4152402689123185488(%rip), %r8
	movl	$43, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking5panic
	ud2
	.seh_endproc

	.section	.rdata,"dr",one_only,anon.322f28e6360e11fa98bf96d410f43235.11.llvm.4152402689123185488,unique,2
	.globl	anon.322f28e6360e11fa98bf96d410f43235.11.llvm.4152402689123185488
anon.322f28e6360e11fa98bf96d410f43235.11.llvm.4152402689123185488:
	.ascii	"assertion failed: index <= self.range.len()"

	.section	.rdata,"dr",one_only,anon.322f28e6360e11fa98bf96d410f43235.12.llvm.4152402689123185488,unique,3
	.globl	anon.322f28e6360e11fa98bf96d410f43235.12.llvm.4152402689123185488
anon.322f28e6360e11fa98bf96d410f43235.12.llvm.4152402689123185488:
	.asciz	"C:\\Users\\there\\.cargo\\registry\\src\\index.crates.io-1949cf8c6b5b557f\\rayon-1.12.0\\src\\range.rs"

	.section	.rdata,"dr",one_only,anon.322f28e6360e11fa98bf96d410f43235.13.llvm.4152402689123185488,unique,4
	.globl	anon.322f28e6360e11fa98bf96d410f43235.13.llvm.4152402689123185488
	.p2align	3, 0x0
anon.322f28e6360e11fa98bf96d410f43235.13.llvm.4152402689123185488:
	.quad	anon.322f28e6360e11fa98bf96d410f43235.12.llvm.4152402689123185488
	.asciz	"]\000\000\000\000\000\000\000\033\001\000\000\001\000\000"

	.section	.data,"dw",one_only,__imp_anon.322f28e6360e11fa98bf96d410f43235.11.llvm.4152402689123185488,unique,5
	.globl	__imp_anon.322f28e6360e11fa98bf96d410f43235.11.llvm.4152402689123185488
	.p2align	3, 0x0
__imp_anon.322f28e6360e11fa98bf96d410f43235.11.llvm.4152402689123185488:
	.quad	anon.322f28e6360e11fa98bf96d410f43235.11.llvm.4152402689123185488

	.section	.data,"dw",one_only,__imp_anon.322f28e6360e11fa98bf96d410f43235.12.llvm.4152402689123185488,unique,6
	.globl	__imp_anon.322f28e6360e11fa98bf96d410f43235.12.llvm.4152402689123185488
	.p2align	3, 0x0
__imp_anon.322f28e6360e11fa98bf96d410f43235.12.llvm.4152402689123185488:
	.quad	anon.322f28e6360e11fa98bf96d410f43235.12.llvm.4152402689123185488

	.section	.data,"dw",one_only,__imp_anon.322f28e6360e11fa98bf96d410f43235.13.llvm.4152402689123185488,unique,7
	.globl	__imp_anon.322f28e6360e11fa98bf96d410f43235.13.llvm.4152402689123185488
	.p2align	3, 0x0
__imp_anon.322f28e6360e11fa98bf96d410f43235.13.llvm.4152402689123185488:
	.quad	anon.322f28e6360e11fa98bf96d410f43235.13.llvm.4152402689123185488

