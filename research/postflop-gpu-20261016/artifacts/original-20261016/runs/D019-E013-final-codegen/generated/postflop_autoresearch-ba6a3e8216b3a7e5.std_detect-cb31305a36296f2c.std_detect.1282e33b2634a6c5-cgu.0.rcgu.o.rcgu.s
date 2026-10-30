	.def	@feat.00;
	.scl	3;
	.type	0;
	.endef
	.globl	@feat.00
@feat.00 = 0
	.file	"std_detect.1282e33b2634a6c5-cgu.0"
	.def	_RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache21detect_and_initialize;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache21detect_and_initialize,unique,0
	.globl	_RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache21detect_and_initialize
	.p2align	4
_RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache21detect_and_initialize:
.Lfunc_begin0:
	.cv_func_id 0
	.cv_file	1 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\std_detect\\src\\detect\\cache.rs" "3773A5030C09F33B3215D0F88562A58AE3E204D7FED716B94AD4D7223946B0F9" 3
	.cv_loc	0 1 177 0
.seh_proc _RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache21detect_and_initialize
	pushq	%rbp
	.seh_pushreg %rbp
.Ltmp0:
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
	.cv_file	2 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\..\\..\\stdarch\\crates\\core_arch\\src\\x86\\cpuid.rs" "7061C9CAA88FE5DDEFF983F94CB921C921F948F85BD483C56FD62001136747C3" 3
	.cv_inline_site_id 1 within 0 inlined_at 1 178 0
	.cv_file	3 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\std_detect\\src\\detect\\os\\x86.rs" "D69CD4573F14D50F2DEFDDC7E8A81708F0BDE4BDB446CE7117D7DF35E0C2BF15" 3
	.cv_inline_site_id 2 within 1 inlined_at 3 44 0
	.cv_inline_site_id 3 within 2 inlined_at 2 108 0
	.cv_loc	3 2 88 0
	xorl	%eax, %eax
	xorl	%ecx, %ecx
	#APP

	movq	%rbx, %r8
	cpuid
	xchgq	%rbx, %r8

	#NO_APP
	movl	%ecx, %r9d
	xorl	%r14d, %r14d
	movabsq	$-9223372036854775808, %rcx
.Ltmp1:
	.cv_loc	1 3 50 0
	testl	%eax, %eax
	je	.LBB0_1
	.cv_inline_site_id 4 within 1 inlined_at 3 57 0
	.cv_inline_site_id 5 within 4 inlined_at 2 108 0
	.cv_loc	5 2 88 0
	movl	%eax, %r10d
	movl	%edx, %esi
	movl	%r8d, %r11d
.Ltmp2:
	movl	$1, %eax
	xorl	%ecx, %ecx
	#APP

	movq	%rbx, %r8
	cpuid
	xchgq	%rbx, %r8

	#NO_APP
	movl	%edx, %ebx
	movl	%ecx, %r8d
.Ltmp3:
	.cv_loc	1 3 67 0
	cmpl	$7, %r10d
	movl	%r9d, 4(%rbp)
	movl	%r10d, -12(%rbp)
	jb	.LBB0_3
.Ltmp4:
	.cv_inline_site_id 6 within 1 inlined_at 3 68 0
	.cv_inline_site_id 7 within 6 inlined_at 2 108 0
	.cv_loc	7 2 88 0
	xorl	%ecx, %ecx
	movl	$7, %eax
	#APP

	movq	%rbx, %rdi
	cpuid
	xchgq	%rbx, %rdi

	#NO_APP
	movl	%edx, %r9d
	movl	%ecx, %r10d
.Ltmp5:
	.cv_inline_site_id 8 within 1 inlined_at 3 70 0
	.cv_loc	8 2 88 0
	movl	$1, %ecx
	movl	$7, %eax
	#APP

	movq	%rbx, %r14
	cpuid
	xchgq	%rbx, %r14

	#NO_APP
.Ltmp6:
	.cv_inline_site_id 9 within 1 inlined_at 3 111 0
	.cv_loc	9 3 93 0
	movl	%edi, %r14d
.Ltmp7:
	.cv_inline_site_id 10 within 1 inlined_at 3 121 0
	.cv_loc	10 3 93 0
	movl	%r10d, %ecx
	movq	%rcx, -40(%rbp)
.Ltmp8:
	.cv_inline_site_id 11 within 1 inlined_at 3 132 0
	.cv_loc	11 3 93 0
	movl	%eax, %eax
	movq	%rax, -24(%rbp)
.Ltmp9:
	.cv_inline_site_id 12 within 1 inlined_at 3 208 0
	.cv_loc	12 3 93 0
	movl	%r9d, %eax
	movq	%rax, -32(%rbp)
.Ltmp10:
	.cv_inline_site_id 13 within 1 inlined_at 3 212 0
	.cv_loc	13 3 93 0
	movl	%edx, %eax
	movq	%rax, -8(%rbp)
	jmp	.LBB0_5
.Ltmp11:
.LBB0_1:
	.cv_loc	1 3 50 0
	xorl	%edx, %edx
	jmp	.LBB0_13
.LBB0_3:
	movq	$0, -40(%rbp)
	movq	$0, -32(%rbp)
	movq	$0, -24(%rbp)
	movq	$0, -8(%rbp)
.LBB0_5:
	.cv_inline_site_id 14 within 1 inlined_at 3 79 0
	.cv_inline_site_id 15 within 14 inlined_at 2 108 0
	.cv_loc	15 2 88 0
	shlq	$32, %rsi
	xorl	%r9d, %r9d
.Ltmp12:
	movl	$-2147483648, %eax
	xorl	%ecx, %ecx
	#APP

	movq	%rbx, %r10
	cpuid
	xchgq	%rbx, %r10

	#NO_APP
.Ltmp13:
	.cv_loc	1 3 83 0
	testl	%eax, %eax
	je	.LBB0_7
.Ltmp14:
	.cv_inline_site_id 16 within 1 inlined_at 3 84 0
	.cv_inline_site_id 17 within 16 inlined_at 2 108 0
	.cv_loc	17 2 88 0
	movl	$-2147483647, %eax
	xorl	%ecx, %ecx
	#APP

	movq	%rbx, %r9
	cpuid
	xchgq	%rbx, %r9

	#NO_APP
.Ltmp15:
	.cv_inline_site_id 18 within 1 inlined_at 3 148 0
	.cv_loc	18 3 93 0
	movl	%ecx, %r9d
.Ltmp16:
.LBB0_7:
	.cv_inline_site_id 19 within 1 inlined_at 3 100 0
	.cv_loc	19 3 93 0
	orq	%r11, %rsi
.Ltmp17:
	movl	%r8d, %r13d
.Ltmp18:
	.cv_loc	19 3 94 0
	movl	%r8d, %eax
	andl	$1, %eax
	shll	$8, %eax
.Ltmp19:
	.cv_inline_site_id 20 within 1 inlined_at 3 102 0
	.cv_loc	20 3 94 0
	movl	%r13d, %ecx
	andl	$514, %ecx
	orq	%rax, %rcx
.Ltmp20:
	.cv_inline_site_id 21 within 1 inlined_at 3 103 0
	.cv_loc	21 3 94 0
	movl	%r8d, %r10d
	shrl	$10, %r10d
	andl	$8, %r10d
.Ltmp21:
	.cv_inline_site_id 22 within 1 inlined_at 3 104 0
	.cv_loc	22 3 94 0
	movl	%r8d, %eax
	shrl	$9, %eax
	movl	%eax, %edx
	andl	$1024, %edx
	orq	%rcx, %rdx
.Ltmp22:
	.cv_inline_site_id 23 within 1 inlined_at 3 105 0
	.cv_loc	23 3 94 0
	andl	$2048, %eax
	orq	%rdx, %rax
.Ltmp23:
	.cv_file	4 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\std_detect\\src\\detect\\bit.rs" "B6F801234A4653952D9B53BA82C9EDFD9C8D0E15FBA4ED8791800D70D2D81A61" 3
	.cv_inline_site_id 24 within 1 inlined_at 3 106 0
	.cv_inline_site_id 25 within 24 inlined_at 3 93 0
	.cv_loc	25 4 8 0
	movl	%r8d, %edx
	andl	$4194304, %edx
.Ltmp24:
	.cv_loc	24 3 94 0
	shrl	$13, %edx
	orl	%r10d, %edx
.Ltmp25:
	.cv_inline_site_id 26 within 1 inlined_at 3 107 0
	.cv_loc	26 3 94 0
	movq	%r13, %r10
	shlq	$38, %r10
.Ltmp26:
	.cv_inline_site_id 27 within 1 inlined_at 3 114 0
	.cv_loc	27 3 93 0
	movl	%ebx, %ecx
.Ltmp27:
	.cv_loc	26 3 94 0
	orq	%rcx, %r10
.Ltmp28:
	.cv_inline_site_id 28 within 1 inlined_at 3 112 0
	.cv_inline_site_id 29 within 28 inlined_at 3 93 0
	.cv_loc	29 4 8 0
	movl	%r14d, %r11d
	andl	$524288, %r11d
.Ltmp29:
	.cv_loc	28 3 94 0
	shrl	$12, %r11d
.Ltmp30:
	.cv_inline_site_id 30 within 1 inlined_at 3 117 0
	.cv_loc	30 3 94 0
	orl	%edx, %r11d
.Ltmp31:
	.cv_inline_site_id 31 within 1 inlined_at 3 113 0
	.cv_inline_site_id 32 within 31 inlined_at 3 93 0
	.cv_loc	32 4 8 0
	movl	%r14d, %edx
	andl	$2048, %edx
.Ltmp32:
	.cv_loc	31 3 94 0
	shrl	$3, %edx
.Ltmp33:
	.cv_inline_site_id 33 within 1 inlined_at 3 118 0
	.cv_loc	33 3 94 0
	orl	%r11d, %edx
	movq	-40(%rbp), %r12
.Ltmp34:
	.cv_loc	10 3 94 0
	movq	%r12, %r15
	shlq	$22, %r15
	movl	%r15d, %edi
	andl	$1073741824, %edi
.Ltmp35:
	.cv_inline_site_id 34 within 1 inlined_at 3 126 0
	.cv_loc	34 3 94 0
	movl	%r14d, %r11d
	andl	$256, %r11d
	shlq	$50, %r11
.Ltmp36:
	.cv_inline_site_id 35 within 1 inlined_at 3 122 0
	.cv_loc	35 3 94 0
	orq	%rdi, %r11
	movl	%r15d, %edi
	andl	$-2147483648, %edi
.Ltmp37:
	.cv_loc	34 3 94 0
	orq	%rdi, %r11
	movabsq	$4294967296, %rdi
.Ltmp38:
	.cv_inline_site_id 36 within 1 inlined_at 3 123 0
	.cv_loc	36 3 94 0
	andq	%r15, %rdi
.Ltmp39:
	.cv_inline_site_id 37 within 1 inlined_at 3 128 0
	.cv_loc	37 3 94 0
	orq	%rdi, %r11
	movabsq	$2305843009213693968, %rdi
.Ltmp40:
	.cv_loc	26 3 94 0
	andq	%r10, %rdi
.Ltmp41:
	.cv_inline_site_id 38 within 1 inlined_at 3 108 0
	.cv_loc	38 3 94 0
	movl	%r8d, %r10d
	shrl	$25, %r10d
	andl	$1, %r10d
	orq	%r10, %rdi
.Ltmp42:
	.cv_inline_site_id 39 within 1 inlined_at 3 109 0
	.cv_loc	39 3 94 0
	movl	%r13d, %r10d
	andl	$536870912, %r10d
	shlq	$26, %r10
	orq	%r10, %rdi
.Ltmp43:
	.cv_inline_site_id 40 within 1 inlined_at 3 110 0
	.cv_loc	40 3 94 0
	shrl	$28, %r8d
	andl	$4, %r8d
	orq	%r8, %rdi
.Ltmp44:
	.cv_inline_site_id 41 within 1 inlined_at 3 115 0
	.cv_loc	41 3 94 0
	movl	%ebx, %r8d
	shrl	$18, %r8d
	andl	$32, %r8d
.Ltmp45:
	.cv_loc	9 3 94 0
	orq	%r8, %rdi
.Ltmp46:
	.cv_inline_site_id 42 within 1 inlined_at 3 116 0
	.cv_loc	42 3 94 0
	andl	$16777216, %ecx
	shlq	$38, %rcx
.Ltmp47:
	.cv_loc	28 3 94 0
	orq	%rcx, %rdi
.Ltmp48:
	.cv_loc	30 3 94 0
	shrl	$19, %ebx
.Ltmp49:
	.cv_loc	27 3 94 0
	andl	$192, %ebx
	orq	%rax, %rbx
.Ltmp50:
	.cv_loc	9 3 94 0
	movl	%r14d, %eax
	shrl	$15, %eax
	andl	$8, %eax
.Ltmp51:
	.cv_loc	41 3 94 0
	orq	%rax, %rbx
.Ltmp52:
	.cv_inline_site_id 43 within 1 inlined_at 3 119 0
	.cv_loc	43 3 94 0
	movl	%r14d, %eax
	shrl	$16, %eax
	andl	$8192, %eax
.Ltmp53:
	.cv_loc	42 3 94 0
	orq	%rax, %rbx
.Ltmp54:
	.cv_inline_site_id 44 within 1 inlined_at 3 125 0
	.cv_loc	44 3 94 0
	movl	%r14d, %eax
	andl	$8, %eax
	shlq	$54, %rax
.Ltmp55:
	.cv_loc	43 3 94 0
	orq	%rax, %rbx
.Ltmp56:
	.cv_loc	10 3 94 0
	orq	%rdi, %rbx
.Ltmp57:
	.cv_inline_site_id 45 within 1 inlined_at 3 130 0
	.cv_loc	45 3 94 0
	orq	%r11, %rbx
.Ltmp58:
	.cv_inline_site_id 46 within 37 inlined_at 3 93 0
	.cv_loc	46 4 8 0
	movl	%r14d, %eax
	andl	$512, %eax
.Ltmp59:
	.cv_loc	36 3 94 0
	leal	(%rdx,%rax,4), %eax
.Ltmp60:
	.cv_loc	45 3 94 0
	movl	%r14d, %ecx
	shrl	$19, %ecx
	andl	$16, %ecx
.Ltmp61:
	.cv_loc	44 3 94 0
	orl	%ecx, %eax
.Ltmp62:
	.cv_loc	11 3 94 0
	movq	%rax, %rdi
	orq	$1024, %rdi
	testl	$-2147483648, -24(%rbp)
	cmoveq	%rax, %rdi
.Ltmp63:
	.cv_loc	1 3 135 0
	testl	$8388608, %r12d
	je	.LBB0_9
.Ltmp64:
	.cv_inline_site_id 47 within 1 inlined_at 3 136 0
	.cv_inline_site_id 48 within 47 inlined_at 2 108 0
	.cv_loc	48 2 88 0
	movl	$25, %eax
	xorl	%ecx, %ecx
	#APP

	movq	%rbx, %r8
	cpuid
	xchgq	%rbx, %r8

	#NO_APP
.Ltmp65:
	.cv_inline_site_id 49 within 1 inlined_at 3 137 0
	.cv_inline_site_id 50 within 49 inlined_at 3 93 0
	.cv_loc	50 4 8 0
	movl	%r8d, %eax
	andl	$1, %eax
.Ltmp66:
	.cv_loc	49 3 94 0
	shll	$5, %eax
.Ltmp67:
	.cv_inline_site_id 51 within 1 inlined_at 3 138 0
	.cv_inline_site_id 52 within 51 inlined_at 3 93 0
	.cv_loc	52 4 8 0
	andl	$4, %r8d
.Ltmp68:
	.cv_loc	51 3 94 0
	shll	$4, %r8d
	orl	%eax, %r8d
	orq	%r8, %rdi
.Ltmp69:
.LBB0_9:
	.cv_loc	18 3 94 0
	movl	4(%rbp), %r10d
.Ltmp70:
	movl	%r9d, %eax
	andl	$32, %eax
	shlq	$54, %rax
	orq	%rax, %rbx
	movabsq	$7598819853104084289, %rax
.Ltmp71:
	.cv_loc	1 3 160 0
	xorq	%rsi, %rax
	movl	%r10d, %ecx
	xorq	$1145913699, %rcx
	orq	%rax, %rcx
	je	.LBB0_23
	movl	%r10d, %eax
	movabsq	$7954842856460876104, %rcx
	xorq	%rsi, %rcx
	xorq	$1701734773, %rax
	orq	%rcx, %rax
	jne	.LBB0_11
.LBB0_23:
.Ltmp72:
	.cv_inline_site_id 53 within 1 inlined_at 3 162 0
	.cv_loc	53 3 94 0
	movl	%r9d, %eax
	andl	$64, %eax
	shll	$6, %eax
.Ltmp73:
	.cv_inline_site_id 54 within 1 inlined_at 3 163 0
	.cv_loc	54 3 94 0
	movl	%r9d, %ecx
	andl	$2097152, %ecx
	shlq	$39, %rcx
	orq	%rax, %rcx
.Ltmp74:
	.cv_inline_site_id 55 within 1 inlined_at 3 164 0
	.cv_inline_site_id 56 within 55 inlined_at 3 93 0
	.cv_loc	56 4 8 0
	andl	$2048, %r9d
.Ltmp75:
	.cv_loc	55 3 94 0
	addl	%r9d, %r9d
	orq	%r9, %rdi
	orq	%rcx, %rbx
.Ltmp76:
.LBB0_11:
	.cv_loc	1 3 169 0
	movl	%r13d, %eax
	notl	%eax
	testl	$201326592, %eax
	jne	.LBB0_12
.Ltmp77:
	.cv_loc	1 3 197 0
	callq	_RNvNtNtNtCs8xEFJqa6dYS_4core9core_arch3x865xsave7__xgetbv
	movq	%rax, %r8
.Ltmp78:
	.cv_loc	1 3 199 0
	movl	%r8d, %r9d
	andl	$6, %r9d
.Ltmp79:
	.cv_loc	1 3 207 0
	notl	%eax
	testl	$393216, %eax
	jne	.LBB0_15
	.cv_inline_site_id 57 within 1 inlined_at 3 209 0
	.cv_loc	57 3 94 0
	movq	-32(%rbp), %rcx
.Ltmp80:
	movl	%ecx, %eax
	andl	$50331648, %eax
	shlq	$19, %rax
.Ltmp81:
	.cv_inline_site_id 58 within 1 inlined_at 3 210 0
	.cv_loc	58 3 94 0
	andl	$4194304, %ecx
	shlq	$23, %rcx
	orq	%rax, %rcx
	movq	-24(%rbp), %r11
.Ltmp82:
	.cv_inline_site_id 59 within 1 inlined_at 3 211 0
	.cv_loc	59 3 94 0
	movl	%r11d, %eax
	andl	$2097152, %eax
	shlq	$25, %rax
	orq	%rcx, %rax
	movq	-8(%rbp), %rcx
.Ltmp83:
	.cv_loc	13 3 94 0
	andl	$256, %ecx
	shlq	$39, %rcx
	orq	%rax, %rcx
	orq	%rcx, %rbx
.Ltmp84:
	.cv_loc	1 3 214 0
	cmpl	$29, -12(%rbp)
	jbe	.LBB0_17
.Ltmp85:
	.cv_inline_site_id 60 within 1 inlined_at 3 216 0
	.cv_loc	60 2 88 0
	movl	$30, %eax
	movl	$1, %ecx
	#APP

	movq	%rbx, %r10
	cpuid
	xchgq	%rbx, %r10

	#NO_APP
.Ltmp86:
	.cv_inline_site_id 61 within 1 inlined_at 3 218 0
	.cv_loc	61 3 93 0
	movl	%eax, %eax
.Ltmp87:
	.cv_inline_site_id 62 within 1 inlined_at 3 219 0
	.cv_loc	62 3 94 0
	movl	%eax, %ecx
	andl	$80, %ecx
	shlq	$45, %rcx
.Ltmp88:
	.cv_inline_site_id 63 within 1 inlined_at 3 220 0
	.cv_loc	63 3 94 0
	movl	%eax, %edx
	andl	$128, %edx
	shlq	$41, %rdx
	orq	%rcx, %rdx
.Ltmp89:
	.cv_inline_site_id 64 within 1 inlined_at 3 221 0
	.cv_loc	64 3 94 0
	andl	$256, %eax
	shlq	$42, %rax
	orq	%rdx, %rax
	orq	%rax, %rbx
.Ltmp90:
.LBB0_17:
	movl	4(%rbp), %r10d
	jmp	.LBB0_18
.LBB0_15:
	movl	4(%rbp), %r10d
	movq	-24(%rbp), %r11
.LBB0_18:
	.cv_loc	1 3 205 0
	movq	%rbx, %rax
.Ltmp91:
	testl	$524288, %r8d
	sete	%cl
	testl	$2097152, -8(%rbp)
	sete	%dl
.Ltmp92:
	.cv_loc	1 3 225 0
	orb	%cl, %dl
	movabsq	$4503599627370496, %rbx
	orq	%rax, %rbx
	testb	%dl, %dl
	cmovneq	%rax, %rbx
.Ltmp93:
	.cv_loc	1 3 199 0
	cmpl	$6, %r9d
.Ltmp94:
	.cv_loc	1 3 231 0
	jne	.LBB0_12
.Ltmp95:
	.cv_inline_site_id 65 within 1 inlined_at 3 242 0
	.cv_inline_site_id 66 within 65 inlined_at 3 95 0
	.cv_inline_site_id 67 within 66 inlined_at 1 50 0
	.cv_loc	67 1 11 0
	andl	$224, %r8d
.Ltmp96:
	movabsq	$-9223372036854775808, %rax
	orq	%rax, %rbx
.Ltmp97:
	.cv_loc	1 3 247 0
	cmpl	$12, -12(%rbp)
	jbe	.LBB0_20
.Ltmp98:
	.cv_inline_site_id 68 within 1 inlined_at 3 249 0
	.cv_loc	68 2 88 0
	movl	$13, %eax
	movl	$1, %ecx
	#APP

	movq	%rbx, %r9
	cpuid
	xchgq	%rbx, %r9

	#NO_APP
	movq	%rdi, %rcx
	orq	$1, %rcx
.Ltmp99:
	.cv_inline_site_id 69 within 1 inlined_at 3 250 0
	.cv_loc	69 3 94 0
	testb	$1, %al
	cmoveq	%rbx, %rbx
	cmoveq	%rdi, %rcx
.Ltmp100:
	.cv_inline_site_id 70 within 1 inlined_at 3 251 0
	.cv_inline_site_id 71 within 70 inlined_at 3 93 0
	.cv_loc	71 4 8 0
	movl	%eax, %edx
	andl	$2, %edx
.Ltmp101:
	.cv_loc	70 3 94 0
	addl	%edx, %edx
.Ltmp102:
	.cv_inline_site_id 72 within 1 inlined_at 3 252 0
	.cv_inline_site_id 73 within 72 inlined_at 3 93 0
	.cv_loc	73 4 8 0
	andl	$8, %eax
.Ltmp103:
	.cv_loc	72 3 94 0
	shrl	$2, %eax
.Ltmp104:
	.cv_loc	70 3 94 0
	orq	%rdx, %rax
.Ltmp105:
	.cv_loc	72 3 94 0
	orq	%rcx, %rax
	movq	%rax, %rdi
.Ltmp106:
.LBB0_20:
	.cv_loc	1 3 201 0
	movq	-8(%rbp), %r12
	xorq	$224, %r8
.Ltmp107:
	.cv_inline_site_id 74 within 1 inlined_at 3 256 0
	.cv_loc	74 3 94 0
	movl	%r13d, %eax
	notl	%eax
	movl	%r13d, %ecx
	andl	$4096, %ecx
	shlq	$44, %rcx
.Ltmp108:
	.cv_inline_site_id 75 within 1 inlined_at 3 259 0
	.cv_loc	75 3 94 0
	shrl	$14, %r13d
	andl	$16384, %r13d
.Ltmp109:
	.cv_loc	74 3 94 0
	orq	%rcx, %r13
.Ltmp110:
	.cv_inline_site_id 76 within 1 inlined_at 3 260 0
	.cv_loc	76 3 94 0
	movl	%r14d, %ecx
	andl	$32, %ecx
	shll	$10, %ecx
.Ltmp111:
	.cv_loc	75 3 94 0
	orq	%r13, %rcx
.Ltmp112:
	.cv_inline_site_id 77 within 1 inlined_at 3 263 0
	.cv_loc	77 3 94 0
	movl	%r11d, %edx
	andl	$16, %edx
	shlq	$36, %rdx
.Ltmp113:
	.cv_loc	76 3 94 0
	orq	%rcx, %rdx
.Ltmp114:
	.cv_inline_site_id 78 within 1 inlined_at 3 264 0
	.cv_loc	78 3 94 0
	movl	%r11d, %ecx
	andl	$8388608, %ecx
	shlq	$15, %rcx
.Ltmp115:
	.cv_loc	77 3 94 0
	orq	%rdx, %rcx
.Ltmp116:
	.cv_loc	78 3 94 0
	orq	%rbx, %rcx
	movabsq	$4398046511104, %rdx
.Ltmp117:
	.cv_inline_site_id 79 within 1 inlined_at 3 266 0
	.cv_loc	79 3 94 0
	orq	%rcx, %rdx
.Ltmp118:
	.cv_inline_site_id 80 within 79 inlined_at 3 93 0
	.cv_loc	80 4 8 0
	testb	$16, %r12b
.Ltmp119:
	.cv_loc	79 3 94 0
	cmoveq	%rcx, %rdx
.Ltmp120:
	.cv_inline_site_id 81 within 1 inlined_at 3 267 0
	.cv_loc	81 3 94 0
	movl	%r12d, %ecx
	andl	$32, %ecx
	shlq	$34, %rcx
.Ltmp121:
	.cv_inline_site_id 82 within 1 inlined_at 3 268 0
	.cv_loc	82 3 94 0
	movl	%r12d, %r9d
	andl	$1024, %r9d
	shlq	$31, %r9
	movl	%r11d, %ebx
	andl	$7, %ebx
	shll	$16, %ebx
.Ltmp122:
	.cv_inline_site_id 83 within 1 inlined_at 3 270 0
	.cv_loc	83 3 94 0
	orq	%rcx, %rbx
.Ltmp123:
	.cv_inline_site_id 84 within 1 inlined_at 3 271 0
	.cv_loc	84 3 94 0
	orq	%r9, %rbx
.Ltmp124:
	.cv_inline_site_id 85 within 1 inlined_at 3 272 0
	.cv_loc	85 3 94 0
	orq	%rdx, %rbx
.Ltmp125:
	.cv_loc	1 3 280 0
	andl	$536875008, %eax
	orq	%r8, %rax
	jne	.LBB0_12
	.cv_inline_site_id 86 within 1 inlined_at 3 281 0
	.cv_loc	86 3 94 0
	movl	$2147483648, %ecx
.Ltmp126:
	movl	%r14d, %eax
	andl	$65536, %eax
.Ltmp127:
	.cv_inline_site_id 87 within 1 inlined_at 3 282 0
	.cv_loc	87 3 94 0
	movl	%r14d, %edx
	shll	$7, %edx
	andl	$16777216, %edx
	leal	(%rdx,%rax,8), %eax
.Ltmp128:
	.cv_inline_site_id 88 within 1 inlined_at 3 283 0
	.cv_loc	88 3 94 0
	movl	%r14d, %edx
	shll	$5, %edx
	andl	$67108864, %edx
	orl	%eax, %edx
.Ltmp129:
	.cv_inline_site_id 89 within 1 inlined_at 3 284 0
	.cv_loc	89 3 94 0
	movl	%r14d, %eax
	shrl	$4, %eax
	andl	$4194304, %eax
	orl	%edx, %eax
.Ltmp130:
	.cv_inline_site_id 90 within 1 inlined_at 3 285 0
	.cv_loc	90 3 94 0
	movl	%r14d, %edx
	shrl	$6, %edx
	andl	$2097152, %edx
	orl	%eax, %edx
.Ltmp131:
	.cv_inline_site_id 91 within 1 inlined_at 3 286 0
	.cv_loc	91 3 94 0
	movl	%r14d, %eax
	shrl	$8, %eax
	andl	$1048576, %eax
	orl	%edx, %eax
.Ltmp132:
	.cv_inline_site_id 92 within 1 inlined_at 3 287 0
	.cv_loc	92 3 94 0
	movl	%r14d, %edx
	shrl	$7, %edx
	andl	$8388608, %edx
	orl	%eax, %edx
	orq	%rdx, %rbx
.Ltmp133:
	.cv_inline_site_id 93 within 1 inlined_at 3 288 0
	.cv_loc	93 3 94 0
	movq	%rbx, %rax
	orq	$33554432, %rax
	cmpq	%rcx, %r14
	cmovbq	%rbx, %rax
	movq	-40(%rbp), %rbx
.Ltmp134:
	.cv_inline_site_id 94 within 1 inlined_at 3 289 0
	.cv_loc	94 3 94 0
	movl	%ebx, %edx
	andl	$2, %edx
	shll	$26, %edx
.Ltmp135:
	.cv_inline_site_id 95 within 1 inlined_at 3 290 0
	.cv_loc	95 3 94 0
	movl	%ebx, %ecx
	andl	$64, %ecx
	shll	$23, %ecx
.Ltmp136:
	.cv_loc	94 3 94 0
	orl	%edx, %ecx
.Ltmp137:
	.cv_inline_site_id 96 within 1 inlined_at 3 293 0
	.cv_loc	96 3 94 0
	shll	$14, %ebx
	andl	$268435456, %ebx
	movq	-32(%rbp), %r14
.Ltmp138:
	.cv_inline_site_id 97 within 1 inlined_at 3 294 0
	.cv_loc	97 3 94 0
	movl	%r14d, %edx
	andl	$256, %edx
	shlq	$28, %rdx
.Ltmp139:
	.cv_inline_site_id 98 within 1 inlined_at 3 295 0
	.cv_loc	98 3 94 0
	andl	$8388608, %r14d
	shlq	$14, %r14
.Ltmp140:
	.cv_inline_site_id 99 within 1 inlined_at 3 296 0
	.cv_loc	99 3 94 0
	movl	%r11d, %r8d
	andl	$32, %r8d
	shlq	$30, %r8
	movabsq	$25769803776, %r9
.Ltmp141:
	.cv_inline_site_id 100 within 1 inlined_at 3 291 0
	.cv_loc	100 3 94 0
	andq	%r9, %r15
	orq	%rcx, %r15
.Ltmp142:
	.cv_inline_site_id 101 within 1 inlined_at 3 292 0
	.cv_loc	101 3 94 0
	orq	%rbx, %r15
.Ltmp143:
	.cv_loc	96 3 94 0
	orq	%rdx, %r15
.Ltmp144:
	.cv_loc	97 3 94 0
	orq	%r14, %r15
.Ltmp145:
	.cv_loc	98 3 94 0
	orq	%r8, %r15
.Ltmp146:
	.cv_loc	99 3 94 0
	movq	%r15, %rbx
	orq	%rax, %rbx
.Ltmp147:
	.cv_inline_site_id 102 within 1 inlined_at 3 298 0
	.cv_loc	102 3 94 0
	testl	$524288, %r12d
	je	.LBB0_12
.Ltmp148:
	.cv_loc	80 4 8 0
	testb	$16, %r12b
	sete	%r8b
.Ltmp149:
	.cv_inline_site_id 103 within 1 inlined_at 3 300 0
	.cv_inline_site_id 104 within 103 inlined_at 2 108 0
	.cv_loc	104 2 88 0
	movl	$36, %eax
	xorl	%ecx, %ecx
	#APP

	movq	%rbx, %r9
	cpuid
	xchgq	%rbx, %r9

	#NO_APP
.Ltmp150:
	.cv_loc	1 3 305 0
	testb	$-2, %r9b
	sete	%al
	notl	%r11d
	testl	$8388624, %r11d
	setne	%cl
	orb	%r8b, %cl
	orb	%al, %cl
	movabsq	$9007199254740992, %rax
	movabsq	$27021597764222976, %rcx
	cmovneq	%rax, %rcx
	orq	%rcx, %rbx
.Ltmp151:
.LBB0_12:
	.cv_file	5 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\array\\equality.rs" "8765B16C3149DCFCF531E2F5724BFC1D2E518A05742D1333D53ED7EEE4F0AE78" 3
	.cv_inline_site_id 105 within 1 inlined_at 3 330 0
	.cv_inline_site_id 106 within 105 inlined_at 5 11 0
	.cv_loc	106 5 157 0
	movabsq	$5288754736637306183, %rax
.Ltmp152:
	xorq	%rax, %rsi
	movl	%r10d, %eax
	xorq	$1818588270, %rax
	orq	%rsi, %rax
	movl	%ebx, %ecx
	andl	$16384, %ecx
	movabsq	$-432345564227584001, %r14
.Ltmp153:
	.cv_loc	1 3 330 0
	andq	%rbx, %r14
	orq	%rax, %rcx
	movl	%edi, %edx
	cmovneq	%rbx, %r14
	cmovneq	%rdi, %rdx
	movabsq	$-9223372036854775808, %rcx
.Ltmp154:
.LBB0_13:
	.cv_inline_site_id 107 within 0 inlined_at 1 178 0
	.cv_inline_site_id 108 within 107 inlined_at 1 154 0
	.cv_inline_site_id 109 within 108 inlined_at 1 162 0
	.cv_loc	109 1 99 0
	movq	%r14, %rax
	orq	%rcx, %rax
.Ltmp155:
	.cv_file	6 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\sync\\atomic.rs" "F4523C36596A40997623B67E3FE80161E810CFB97968D953C3367BF67129DA7F" 3
	.cv_inline_site_id 110 within 109 inlined_at 1 99 0
	.cv_inline_site_id 111 within 110 inlined_at 6 2884 0
	.cv_loc	111 6 3875 0
	movq	%rax, _RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache5CACHE(%rip)
.Ltmp156:
	.cv_loc	108 1 163 0
	movq	%rdx, %rax
	shldq	$1, %r14, %rax
.Ltmp157:
	.cv_inline_site_id 112 within 108 inlined_at 1 163 0
	.cv_loc	112 1 99 0
	orq	%rcx, %rax
.Ltmp158:
	.cv_inline_site_id 113 within 112 inlined_at 1 99 0
	.cv_inline_site_id 114 within 113 inlined_at 6 2884 0
	.cv_loc	114 6 3875 0
	movq	%rax, _RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache5CACHE+8(%rip)
.Ltmp159:
	.cv_loc	108 1 164 0
	movq	%rdx, %rax
	shrq	$62, %rax
.Ltmp160:
	.cv_inline_site_id 115 within 108 inlined_at 1 164 0
	.cv_loc	115 1 99 0
	orq	%rcx, %rax
.Ltmp161:
	.cv_inline_site_id 116 within 115 inlined_at 1 99 0
	.cv_inline_site_id 117 within 116 inlined_at 6 2884 0
	.cv_loc	117 6 3875 0
	movq	%rax, _RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache5CACHE+16(%rip)
.Ltmp162:
	.cv_loc	0 1 179 0
	movq	%r14, %rax
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
.Ltmp163:
.Lfunc_end0:
	.seh_endproc

	.def	_RNvNtNtNtCs8xEFJqa6dYS_4core9core_arch3x865xsave7__xgetbv;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNtNtNtCs8xEFJqa6dYS_4core9core_arch3x865xsave7__xgetbv,unique,1
	.p2align	4
_RNvNtNtNtCs8xEFJqa6dYS_4core9core_arch3x865xsave7__xgetbv:
.Lfunc_begin1:
	.cv_func_id 118
	.cv_file	7 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\..\\..\\stdarch\\crates\\core_arch\\src\\x86\\xsave.rs" "92397E62958CDE375B94AD6B6FD14EBF7F01799659678717A075408881BC9C27" 3
	.cv_loc	118 7 90 0
	xorl	%ecx, %ecx
	xgetbv
	shlq	$32, %rdx
	orq	%rdx, %rax
	.cv_loc	118 7 91 0
	retq
.Ltmp164:
.Lfunc_end1:

	.section	.bss,"bw",one_only,_RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache5CACHE,unique,2
	.globl	_RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache5CACHE
	.p2align	3, 0x0
_RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache5CACHE:
	.zero	24

	.section	.data,"dw",one_only,__imp__RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache5CACHE,unique,3
	.globl	__imp__RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache5CACHE
	.p2align	3, 0x0
__imp__RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache5CACHE:
	.quad	_RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache5CACHE

	.section	.debug$S,"dr"
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp166-.Ltmp165
.Ltmp165:
	.short	.Ltmp168-.Ltmp167
.Ltmp167:
	.short	4353
	.long	0
	.asciz	"S:\\GTOpen-research\\postflop-gpu-20261016\\build\\release\\deps\\postflop_autoresearch-ba6a3e8216b3a7e5.std_detect-cb31305a36296f2c.std_detect.1282e33b2634a6c5-cgu.0.rcgu.o.rcgu.o"
	.p2align	2, 0x0
.Ltmp168:
	.short	.Ltmp170-.Ltmp169
.Ltmp169:
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
.Ltmp170:
.Ltmp166:
	.p2align	2, 0x0
	.long	246
	.long	.Ltmp172-.Ltmp171
.Ltmp171:
	.long	0


	.long	4099
	.cv_filechecksumoffset	3
	.long	27


	.long	4101
	.cv_filechecksumoffset	2
	.long	107


	.long	4102
	.cv_filechecksumoffset	2
	.long	61


	.long	4104
	.cv_filechecksumoffset	3
	.long	92


	.long	4106
	.cv_filechecksumoffset	4
	.long	6


	.long	4108
	.cv_filechecksumoffset	1
	.long	47


	.long	4110
	.cv_filechecksumoffset	1
	.long	10


	.long	4112
	.cv_filechecksumoffset	5
	.long	10


	.long	4114
	.cv_filechecksumoffset	5
	.long	153


	.long	4115
	.cv_filechecksumoffset	1
	.long	153


	.long	4116
	.cv_filechecksumoffset	1
	.long	161


	.long	4118
	.cv_filechecksumoffset	1
	.long	97


	.long	4120
	.cv_filechecksumoffset	6
	.long	2882


	.long	4122
	.cv_filechecksumoffset	6
	.long	3871
.Ltmp172:
	.p2align	2, 0x0
	.section	.debug$S,"dr",associative,_RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache21detect_and_initialize
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp174-.Ltmp173
.Ltmp173:
	.short	.Ltmp176-.Ltmp175
.Ltmp175:
	.short	4423
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end0-_RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache21detect_and_initialize
	.long	0
	.long	0
	.long	4123
	.secrel32	_RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache21detect_and_initialize
	.secidx	_RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache21detect_and_initialize
	.byte	129
	.asciz	"std_detect::detect::cache::detect_and_initialize"
	.p2align	2, 0x0
.Ltmp176:
	.short	.Ltmp178-.Ltmp177
.Ltmp177:
	.short	4114
	.long	96
	.long	0
	.long	0
	.long	56
	.long	0
	.short	0
	.long	1220616
	.p2align	2, 0x0
.Ltmp178:
	.short	.Ltmp180-.Ltmp179
.Ltmp179:
	.short	4456
	.long	2
	.long	4099
	.long	4115
	.p2align	2, 0x0
.Ltmp180:
	.short	.Ltmp182-.Ltmp181
.Ltmp181:
	.short	4429
	.long	0
	.long	0
	.long	4099
	.cv_inline_linetable	1 3 27 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp182:
	.short	.Ltmp184-.Ltmp183
.Ltmp183:
	.short	4429
	.long	0
	.long	0
	.long	4101
	.cv_inline_linetable	2 2 107 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp184:
	.short	.Ltmp186-.Ltmp185
.Ltmp185:
	.short	4429
	.long	0
	.long	0
	.long	4102
	.cv_inline_linetable	3 2 61 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp186:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp188-.Ltmp187
.Ltmp187:
	.short	4429
	.long	0
	.long	0
	.long	4101
	.cv_inline_linetable	4 2 107 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp188:
	.short	.Ltmp190-.Ltmp189
.Ltmp189:
	.short	4429
	.long	0
	.long	0
	.long	4102
	.cv_inline_linetable	5 2 61 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp190:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp192-.Ltmp191
.Ltmp191:
	.short	4429
	.long	0
	.long	0
	.long	4101
	.cv_inline_linetable	6 2 107 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp192:
	.short	.Ltmp194-.Ltmp193
.Ltmp193:
	.short	4429
	.long	0
	.long	0
	.long	4102
	.cv_inline_linetable	7 2 61 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp194:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp196-.Ltmp195
.Ltmp195:
	.short	4429
	.long	0
	.long	0
	.long	4102
	.cv_inline_linetable	8 2 61 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp196:
	.short	2
	.short	4430
	.short	.Ltmp198-.Ltmp197
.Ltmp197:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	9 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp198:
	.short	2
	.short	4430
	.short	.Ltmp200-.Ltmp199
.Ltmp199:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	10 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp200:
	.short	2
	.short	4430
	.short	.Ltmp202-.Ltmp201
.Ltmp201:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	11 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp202:
	.short	2
	.short	4430
	.short	.Ltmp204-.Ltmp203
.Ltmp203:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	12 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp204:
	.short	2
	.short	4430
	.short	.Ltmp206-.Ltmp205
.Ltmp205:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	13 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp206:
	.short	2
	.short	4430
	.short	.Ltmp208-.Ltmp207
.Ltmp207:
	.short	4429
	.long	0
	.long	0
	.long	4101
	.cv_inline_linetable	14 2 107 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp208:
	.short	.Ltmp210-.Ltmp209
.Ltmp209:
	.short	4429
	.long	0
	.long	0
	.long	4102
	.cv_inline_linetable	15 2 61 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp210:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp212-.Ltmp211
.Ltmp211:
	.short	4429
	.long	0
	.long	0
	.long	4101
	.cv_inline_linetable	16 2 107 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp212:
	.short	.Ltmp214-.Ltmp213
.Ltmp213:
	.short	4429
	.long	0
	.long	0
	.long	4102
	.cv_inline_linetable	17 2 61 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp214:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp216-.Ltmp215
.Ltmp215:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	18 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp216:
	.short	2
	.short	4430
	.short	.Ltmp218-.Ltmp217
.Ltmp217:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	19 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp218:
	.short	2
	.short	4430
	.short	.Ltmp220-.Ltmp219
.Ltmp219:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	20 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp220:
	.short	2
	.short	4430
	.short	.Ltmp222-.Ltmp221
.Ltmp221:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	21 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp222:
	.short	2
	.short	4430
	.short	.Ltmp224-.Ltmp223
.Ltmp223:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	22 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp224:
	.short	2
	.short	4430
	.short	.Ltmp226-.Ltmp225
.Ltmp225:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	23 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp226:
	.short	2
	.short	4430
	.short	.Ltmp228-.Ltmp227
.Ltmp227:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	24 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp228:
	.short	.Ltmp230-.Ltmp229
.Ltmp229:
	.short	4429
	.long	0
	.long	0
	.long	4106
	.cv_inline_linetable	25 4 6 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp230:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp232-.Ltmp231
.Ltmp231:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	26 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp232:
	.short	2
	.short	4430
	.short	.Ltmp234-.Ltmp233
.Ltmp233:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	27 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp234:
	.short	2
	.short	4430
	.short	.Ltmp236-.Ltmp235
.Ltmp235:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	28 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp236:
	.short	.Ltmp238-.Ltmp237
.Ltmp237:
	.short	4429
	.long	0
	.long	0
	.long	4106
	.cv_inline_linetable	29 4 6 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp238:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp240-.Ltmp239
.Ltmp239:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	30 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp240:
	.short	2
	.short	4430
	.short	.Ltmp242-.Ltmp241
.Ltmp241:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	31 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp242:
	.short	.Ltmp244-.Ltmp243
.Ltmp243:
	.short	4429
	.long	0
	.long	0
	.long	4106
	.cv_inline_linetable	32 4 6 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp244:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp246-.Ltmp245
.Ltmp245:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	33 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp246:
	.short	2
	.short	4430
	.short	.Ltmp248-.Ltmp247
.Ltmp247:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	34 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp248:
	.short	2
	.short	4430
	.short	.Ltmp250-.Ltmp249
.Ltmp249:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	35 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp250:
	.short	2
	.short	4430
	.short	.Ltmp252-.Ltmp251
.Ltmp251:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	36 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp252:
	.short	2
	.short	4430
	.short	.Ltmp254-.Ltmp253
.Ltmp253:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	37 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp254:
	.short	.Ltmp256-.Ltmp255
.Ltmp255:
	.short	4429
	.long	0
	.long	0
	.long	4106
	.cv_inline_linetable	46 4 6 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp256:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp258-.Ltmp257
.Ltmp257:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	38 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp258:
	.short	2
	.short	4430
	.short	.Ltmp260-.Ltmp259
.Ltmp259:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	39 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp260:
	.short	2
	.short	4430
	.short	.Ltmp262-.Ltmp261
.Ltmp261:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	40 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp262:
	.short	2
	.short	4430
	.short	.Ltmp264-.Ltmp263
.Ltmp263:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	41 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp264:
	.short	2
	.short	4430
	.short	.Ltmp266-.Ltmp265
.Ltmp265:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	42 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp266:
	.short	2
	.short	4430
	.short	.Ltmp268-.Ltmp267
.Ltmp267:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	43 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp268:
	.short	2
	.short	4430
	.short	.Ltmp270-.Ltmp269
.Ltmp269:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	44 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp270:
	.short	2
	.short	4430
	.short	.Ltmp272-.Ltmp271
.Ltmp271:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	45 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp272:
	.short	2
	.short	4430
	.short	.Ltmp274-.Ltmp273
.Ltmp273:
	.short	4429
	.long	0
	.long	0
	.long	4101
	.cv_inline_linetable	47 2 107 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp274:
	.short	.Ltmp276-.Ltmp275
.Ltmp275:
	.short	4429
	.long	0
	.long	0
	.long	4102
	.cv_inline_linetable	48 2 61 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp276:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp278-.Ltmp277
.Ltmp277:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	49 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp278:
	.short	.Ltmp280-.Ltmp279
.Ltmp279:
	.short	4429
	.long	0
	.long	0
	.long	4106
	.cv_inline_linetable	50 4 6 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp280:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp282-.Ltmp281
.Ltmp281:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	51 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp282:
	.short	.Ltmp284-.Ltmp283
.Ltmp283:
	.short	4429
	.long	0
	.long	0
	.long	4106
	.cv_inline_linetable	52 4 6 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp284:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp286-.Ltmp285
.Ltmp285:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	53 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp286:
	.short	2
	.short	4430
	.short	.Ltmp288-.Ltmp287
.Ltmp287:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	54 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp288:
	.short	2
	.short	4430
	.short	.Ltmp290-.Ltmp289
.Ltmp289:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	55 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp290:
	.short	.Ltmp292-.Ltmp291
.Ltmp291:
	.short	4429
	.long	0
	.long	0
	.long	4106
	.cv_inline_linetable	56 4 6 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp292:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp294-.Ltmp293
.Ltmp293:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	57 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp294:
	.short	2
	.short	4430
	.short	.Ltmp296-.Ltmp295
.Ltmp295:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	58 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp296:
	.short	2
	.short	4430
	.short	.Ltmp298-.Ltmp297
.Ltmp297:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	59 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp298:
	.short	2
	.short	4430
	.short	.Ltmp300-.Ltmp299
.Ltmp299:
	.short	4429
	.long	0
	.long	0
	.long	4102
	.cv_inline_linetable	60 2 61 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp300:
	.short	2
	.short	4430
	.short	.Ltmp302-.Ltmp301
.Ltmp301:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	61 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp302:
	.short	2
	.short	4430
	.short	.Ltmp304-.Ltmp303
.Ltmp303:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	62 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp304:
	.short	2
	.short	4430
	.short	.Ltmp306-.Ltmp305
.Ltmp305:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	63 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp306:
	.short	2
	.short	4430
	.short	.Ltmp308-.Ltmp307
.Ltmp307:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	64 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp308:
	.short	2
	.short	4430
	.short	.Ltmp310-.Ltmp309
.Ltmp309:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	65 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp310:
	.short	.Ltmp312-.Ltmp311
.Ltmp311:
	.short	4429
	.long	0
	.long	0
	.long	4108
	.cv_inline_linetable	66 1 47 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp312:
	.short	.Ltmp314-.Ltmp313
.Ltmp313:
	.short	4429
	.long	0
	.long	0
	.long	4110
	.cv_inline_linetable	67 1 10 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp314:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp316-.Ltmp315
.Ltmp315:
	.short	4429
	.long	0
	.long	0
	.long	4102
	.cv_inline_linetable	68 2 61 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp316:
	.short	2
	.short	4430
	.short	.Ltmp318-.Ltmp317
.Ltmp317:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	69 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp318:
	.short	2
	.short	4430
	.short	.Ltmp320-.Ltmp319
.Ltmp319:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	70 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp320:
	.short	.Ltmp322-.Ltmp321
.Ltmp321:
	.short	4429
	.long	0
	.long	0
	.long	4106
	.cv_inline_linetable	71 4 6 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp322:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp324-.Ltmp323
.Ltmp323:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	72 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp324:
	.short	.Ltmp326-.Ltmp325
.Ltmp325:
	.short	4429
	.long	0
	.long	0
	.long	4106
	.cv_inline_linetable	73 4 6 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp326:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp328-.Ltmp327
.Ltmp327:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	74 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp328:
	.short	2
	.short	4430
	.short	.Ltmp330-.Ltmp329
.Ltmp329:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	75 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp330:
	.short	2
	.short	4430
	.short	.Ltmp332-.Ltmp331
.Ltmp331:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	76 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp332:
	.short	2
	.short	4430
	.short	.Ltmp334-.Ltmp333
.Ltmp333:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	77 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp334:
	.short	2
	.short	4430
	.short	.Ltmp336-.Ltmp335
.Ltmp335:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	78 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp336:
	.short	2
	.short	4430
	.short	.Ltmp338-.Ltmp337
.Ltmp337:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	79 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp338:
	.short	.Ltmp340-.Ltmp339
.Ltmp339:
	.short	4429
	.long	0
	.long	0
	.long	4106
	.cv_inline_linetable	80 4 6 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp340:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp342-.Ltmp341
.Ltmp341:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	81 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp342:
	.short	2
	.short	4430
	.short	.Ltmp344-.Ltmp343
.Ltmp343:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	82 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp344:
	.short	2
	.short	4430
	.short	.Ltmp346-.Ltmp345
.Ltmp345:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	83 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp346:
	.short	2
	.short	4430
	.short	.Ltmp348-.Ltmp347
.Ltmp347:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	84 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp348:
	.short	2
	.short	4430
	.short	.Ltmp350-.Ltmp349
.Ltmp349:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	85 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp350:
	.short	2
	.short	4430
	.short	.Ltmp352-.Ltmp351
.Ltmp351:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	86 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp352:
	.short	2
	.short	4430
	.short	.Ltmp354-.Ltmp353
.Ltmp353:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	87 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp354:
	.short	2
	.short	4430
	.short	.Ltmp356-.Ltmp355
.Ltmp355:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	88 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp356:
	.short	2
	.short	4430
	.short	.Ltmp358-.Ltmp357
.Ltmp357:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	89 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp358:
	.short	2
	.short	4430
	.short	.Ltmp360-.Ltmp359
.Ltmp359:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	90 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp360:
	.short	2
	.short	4430
	.short	.Ltmp362-.Ltmp361
.Ltmp361:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	91 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp362:
	.short	2
	.short	4430
	.short	.Ltmp364-.Ltmp363
.Ltmp363:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	92 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp364:
	.short	2
	.short	4430
	.short	.Ltmp366-.Ltmp365
.Ltmp365:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	93 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp366:
	.short	2
	.short	4430
	.short	.Ltmp368-.Ltmp367
.Ltmp367:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	94 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp368:
	.short	2
	.short	4430
	.short	.Ltmp370-.Ltmp369
.Ltmp369:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	95 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp370:
	.short	2
	.short	4430
	.short	.Ltmp372-.Ltmp371
.Ltmp371:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	96 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp372:
	.short	2
	.short	4430
	.short	.Ltmp374-.Ltmp373
.Ltmp373:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	97 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp374:
	.short	2
	.short	4430
	.short	.Ltmp376-.Ltmp375
.Ltmp375:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	98 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp376:
	.short	2
	.short	4430
	.short	.Ltmp378-.Ltmp377
.Ltmp377:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	99 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp378:
	.short	2
	.short	4430
	.short	.Ltmp380-.Ltmp379
.Ltmp379:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	100 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp380:
	.short	2
	.short	4430
	.short	.Ltmp382-.Ltmp381
.Ltmp381:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	101 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp382:
	.short	2
	.short	4430
	.short	.Ltmp384-.Ltmp383
.Ltmp383:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	102 3 92 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp384:
	.short	2
	.short	4430
	.short	.Ltmp386-.Ltmp385
.Ltmp385:
	.short	4429
	.long	0
	.long	0
	.long	4101
	.cv_inline_linetable	103 2 107 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp386:
	.short	.Ltmp388-.Ltmp387
.Ltmp387:
	.short	4429
	.long	0
	.long	0
	.long	4102
	.cv_inline_linetable	104 2 61 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp388:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp390-.Ltmp389
.Ltmp389:
	.short	4429
	.long	0
	.long	0
	.long	4112
	.cv_inline_linetable	105 5 10 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp390:
	.short	.Ltmp392-.Ltmp391
.Ltmp391:
	.short	4429
	.long	0
	.long	0
	.long	4114
	.cv_inline_linetable	106 5 153 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp392:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp394-.Ltmp393
.Ltmp393:
	.short	4429
	.long	0
	.long	0
	.long	4115
	.cv_inline_linetable	107 1 153 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp394:
	.short	.Ltmp396-.Ltmp395
.Ltmp395:
	.short	4429
	.long	0
	.long	0
	.long	4116
	.cv_inline_linetable	108 1 161 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp396:
	.short	.Ltmp398-.Ltmp397
.Ltmp397:
	.short	4429
	.long	0
	.long	0
	.long	4118
	.cv_inline_linetable	109 1 97 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp398:
	.short	.Ltmp400-.Ltmp399
.Ltmp399:
	.short	4429
	.long	0
	.long	0
	.long	4120
	.cv_inline_linetable	110 6 2882 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp400:
	.short	.Ltmp402-.Ltmp401
.Ltmp401:
	.short	4429
	.long	0
	.long	0
	.long	4122
	.cv_inline_linetable	111 6 3871 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp402:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp404-.Ltmp403
.Ltmp403:
	.short	4429
	.long	0
	.long	0
	.long	4118
	.cv_inline_linetable	112 1 97 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp404:
	.short	.Ltmp406-.Ltmp405
.Ltmp405:
	.short	4429
	.long	0
	.long	0
	.long	4120
	.cv_inline_linetable	113 6 2882 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp406:
	.short	.Ltmp408-.Ltmp407
.Ltmp407:
	.short	4429
	.long	0
	.long	0
	.long	4122
	.cv_inline_linetable	114 6 3871 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp408:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp410-.Ltmp409
.Ltmp409:
	.short	4429
	.long	0
	.long	0
	.long	4118
	.cv_inline_linetable	115 1 97 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp410:
	.short	.Ltmp412-.Ltmp411
.Ltmp411:
	.short	4429
	.long	0
	.long	0
	.long	4120
	.cv_inline_linetable	116 6 2882 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp412:
	.short	.Ltmp414-.Ltmp413
.Ltmp413:
	.short	4429
	.long	0
	.long	0
	.long	4122
	.cv_inline_linetable	117 6 3871 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp414:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4431
.Ltmp174:
	.p2align	2, 0x0
	.cv_linetable	0, _RNvNtNtCs1AxaXbpVqOn_10std_detect6detect5cache21detect_and_initialize, .Lfunc_end0
	.section	.debug$S,"dr",associative,_RNvNtNtNtCs8xEFJqa6dYS_4core9core_arch3x865xsave7__xgetbv
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp416-.Ltmp415
.Ltmp415:
	.short	.Ltmp418-.Ltmp417
.Ltmp417:
	.short	4422
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end1-_RNvNtNtNtCs8xEFJqa6dYS_4core9core_arch3x865xsave7__xgetbv
	.long	0
	.long	0
	.long	4125
	.secrel32	_RNvNtNtNtCs8xEFJqa6dYS_4core9core_arch3x865xsave7__xgetbv
	.secidx	_RNvNtNtNtCs8xEFJqa6dYS_4core9core_arch3x865xsave7__xgetbv
	.byte	128
	.asciz	"core::core_arch::x86::xsave::_xgetbv"
	.p2align	2, 0x0
.Ltmp418:
	.short	.Ltmp420-.Ltmp419
.Ltmp419:
	.short	4114
	.long	0
	.long	0
	.long	0
	.long	0
	.long	0
	.short	0
	.long	1056800
	.p2align	2, 0x0
.Ltmp420:
	.short	2
	.short	4431
.Ltmp416:
	.p2align	2, 0x0
	.cv_linetable	118, _RNvNtNtNtCs8xEFJqa6dYS_4core9core_arch3x865xsave7__xgetbv, .Lfunc_end1
	.section	.debug$S,"dr"
	.cv_filechecksums
	.cv_stringtable
	.long	241
	.long	.Ltmp422-.Ltmp421
.Ltmp421:
	.short	.Ltmp424-.Ltmp423
.Ltmp423:
	.short	4428
	.long	4129
	.p2align	2, 0x0
.Ltmp424:
.Ltmp422:
	.p2align	2, 0x0
	.section	.debug$T,"dr"
	.p2align	2, 0x0
	.long	4
	.short	0x1e
	.short	0x1605
	.long	0x0
	.asciz	"std_detect::detect::os"
	.byte	241
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
	.short	0x1a
	.short	0x1601
	.long	0x1000
	.long	0x1002
	.asciz	"detect_features"
	.short	0x22
	.short	0x1605
	.long	0x0
	.asciz	"core::core_arch::x86::cpuid"
	.short	0x12
	.short	0x1601
	.long	0x1004
	.long	0x1002
	.asciz	"__cpuid"
	.short	0x1a
	.short	0x1601
	.long	0x1004
	.long	0x1002
	.asciz	"__cpuid_count"
	.byte	242
	.byte	241
	.short	0x2e
	.short	0x1605
	.long	0x0
	.asciz	"std_detect::detect::os::detect_features"
	.short	0x16
	.short	0x1601
	.long	0x1007
	.long	0x1002
	.asciz	"closure$0"
	.byte	242
	.byte	241
	.short	0x1e
	.short	0x1605
	.long	0x0
	.asciz	"std_detect::detect::bit"
	.short	0x12
	.short	0x1601
	.long	0x1009
	.long	0x1002
	.asciz	"test"
	.byte	243
	.byte	242
	.byte	241
	.short	0x2e
	.short	0x1605
	.long	0x0
	.asciz	"std_detect::detect::cache::Initializer"
	.byte	241
	.short	0xe
	.short	0x1601
	.long	0x100b
	.long	0x1002
	.asciz	"set"
	.short	0x22
	.short	0x1605
	.long	0x0
	.asciz	"std_detect::detect::cache"
	.byte	242
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x100d
	.long	0x1002
	.asciz	"set_bit"
	.short	0x26
	.short	0x1605
	.long	0x0
	.asciz	"core::array::equality::impl$0"
	.byte	242
	.byte	241
	.short	0xe
	.short	0x1601
	.long	0x100f
	.long	0x1002
	.asciz	"eq"
	.byte	241
	.short	0x26
	.short	0x1605
	.long	0x0
	.asciz	"core::array::equality::impl$9"
	.byte	242
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x1011
	.long	0x1002
	.asciz	"spec_eq"
	.short	0x16
	.short	0x1601
	.long	0x100d
	.long	0x1002
	.asciz	"initialize"
	.byte	241
	.short	0x1a
	.short	0x1601
	.long	0x100d
	.long	0x1002
	.asciz	"do_initialize"
	.byte	242
	.byte	241
	.short	0x2a
	.short	0x1605
	.long	0x0
	.asciz	"std_detect::detect::cache::Cache"
	.byte	243
	.byte	242
	.byte	241
	.short	0x16
	.short	0x1601
	.long	0x1015
	.long	0x1002
	.asciz	"initialize"
	.byte	241
	.short	0x22
	.short	0x1605
	.long	0x0
	.asciz	"core::sync::atomic::Atomic"
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x1017
	.long	0x1002
	.asciz	"store"
	.byte	242
	.byte	241
	.short	0x1a
	.short	0x1605
	.long	0x0
	.asciz	"core::sync::atomic"
	.byte	241
	.short	0x1a
	.short	0x1601
	.long	0x1019
	.long	0x1002
	.asciz	"atomic_store"
	.byte	243
	.byte	242
	.byte	241
	.short	0x22
	.short	0x1601
	.long	0x100d
	.long	0x1002
	.asciz	"detect_and_initialize"
	.byte	242
	.byte	241
	.short	0x22
	.short	0x1605
	.long	0x0
	.asciz	"core::core_arch::x86::xsave"
	.short	0x12
	.short	0x1601
	.long	0x101c
	.long	0x1002
	.asciz	"_xgetbv"
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
	.long	0x101e
	.long	0x1020
	.long	0x101f
	.long	0x1020
	.long	0x1020
	.byte	242
	.byte	241
