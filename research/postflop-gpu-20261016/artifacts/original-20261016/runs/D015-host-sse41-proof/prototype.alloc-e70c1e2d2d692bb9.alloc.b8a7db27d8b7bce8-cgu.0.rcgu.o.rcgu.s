	.def	@feat.00;
	.scl	3;
	.type	0;
	.endef
	.globl	@feat.00
@feat.00 = 0
	.file	"alloc.b8a7db27d8b7bce8-cgu.0"
	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsfQUUnEvlYZE_5alloc6string6StringEBF_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsfQUUnEvlYZE_5alloc6string6StringEBF_,unique,0
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsfQUUnEvlYZE_5alloc6string6StringEBF_:
.Lfunc_begin0:
	.cv_func_id 0
	.cv_file	1 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\ptr\\mod.rs" "F7B3E71D9E9246762C38641C6C1A49079265782AAB6DEAA537B43665B418F029" 3
	.cv_loc	0 1 823 0
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsfQUUnEvlYZE_5alloc6string6StringEBF_
	pushq	%rbp
	.seh_pushreg %rbp
.Ltmp0:
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	32(%rsp), %rbp
	.seh_setframe %rbp, 32
	.seh_endprologue
	.cv_file	2 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\alloc\\src\\raw_vec\\mod.rs" "A262B9E494236A00270BE0DD0C57BE5259D62BC1E538C56506F7F0CE8DEBCCC0" 3
	.cv_inline_site_id 1 within 0 inlined_at 1 823 0
	.cv_inline_site_id 2 within 1 inlined_at 1 823 0
	.cv_inline_site_id 3 within 2 inlined_at 1 823 0
	.cv_inline_site_id 4 within 3 inlined_at 2 425 0
	.cv_inline_site_id 5 within 4 inlined_at 2 878 0
	.cv_loc	5 2 635 0
	cmpq	$0, (%rcx)
	je	.LBB0_1
.Ltmp1:
	.cv_loc	0 1 823 0
	movq	8(%rcx), %rsi
.Ltmp2:
	.cv_file	3 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\std\\src\\sys\\alloc\\windows.rs" "E2DBB86E7CE2412CA9E653343D17275963853F861C27EE5C04D9A22D162000E0" 3
	.cv_inline_site_id 6 within 4 inlined_at 2 880 0
	.cv_file	4 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\alloc\\src\\alloc.rs" "699C02FE7844CD9490905545E503FEC56552BE2A34D50A79242852739483889B" 3
	.cv_inline_site_id 7 within 6 inlined_at 4 462 0
	.cv_inline_site_id 8 within 7 inlined_at 4 344 0
	.cv_inline_site_id 9 within 8 inlined_at 4 229 0
	.cv_inline_site_id 10 within 9 inlined_at 4 128 0
	.cv_file	5 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\std\\src\\alloc.rs" "2D22C4F49121716BA9EDA233D097746C11E51B387A868F5FCE83D6F1E52BECF6" 3
	.cv_inline_site_id 11 within 10 inlined_at 5 463 0
	.cv_inline_site_id 12 within 11 inlined_at 3 195 0
	.cv_loc	12 3 85 0
	callq	*__imp_GetProcessHeap(%rip)
.Ltmp3:
	.cv_loc	11 3 199 0
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	rex64 jmpq	*__imp_HeapFree(%rip)
.Ltmp4:
.LBB0_1:
	.cv_loc	0 1 823 0
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.Ltmp5:
.Lfunc_end0:
	.seh_endproc

	.def	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalEBa_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalEBa_,unique,1
	.p2align	4
_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalEBa_:
.Lfunc_begin1:
	.cv_func_id 13
	.cv_loc	13 2 662 0
.seh_proc _RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalEBa_
	pushq	%rbp
	.seh_pushreg %rbp
.Ltmp6:
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$64, %rsp
	.seh_stackalloc 64
	leaq	64(%rsp), %rbp
	.seh_setframe %rbp, 64
	.seh_endprologue
	.cv_file	6 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\num\\uint_macros.rs" "32C5B549DE1E056FD21CED3568E4E576B9F0AC39FE6963C2344F8A56194524DE" 3
	.cv_inline_site_id 14 within 13 inlined_at 2 669 0
	.cv_inline_site_id 15 within 14 inlined_at 2 519 0
	.cv_loc	15 6 898 0
	addq	%r8, %rdx
.Ltmp7:
	.cv_file	7 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\intrinsics\\mod.rs" "AAB5C05FF3933D28CBAB7914D71054F830311A888234DA6201BF2F1A2959EBC3" 3
	.cv_inline_site_id 16 within 15 inlined_at 6 898 0
	.cv_loc	16 7 459 0
	jb	.LBB1_1
.Ltmp8:
	.cv_loc	14 2 523 0
	movq	%rcx, %rsi
.Ltmp9:
	movq	(%rcx), %rax
	leaq	(%rax,%rax), %rcx
.Ltmp10:
	.cv_file	8 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\cmp.rs" "0A9B8C3A2F7B80447703E5CDC224D059465A90FB9203E0AB4B0182AF17494CAC" 3
	.cv_inline_site_id 17 within 14 inlined_at 2 523 0
	.cv_inline_site_id 18 within 17 inlined_at 8 1682 0
	.cv_loc	18 8 1039 0
	cmpq	%rcx, %rdx
	cmovaq	%rdx, %rcx
.Ltmp11:
	.cv_inline_site_id 19 within 14 inlined_at 2 524 0
	.cv_inline_site_id 20 within 19 inlined_at 8 1682 0
	.cv_loc	20 8 1039 0
	cmpq	$9, %rcx
	movl	$8, %edi
	cmovaeq	%rcx, %rdi
.Ltmp12:
	.cv_loc	14 2 529 0
	movq	8(%rsi), %r8
	leaq	-24(%rbp), %rcx
	movq	%rax, %rdx
	movq	%rdi, %r9
	callq	_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growB7_
.Ltmp13:
	.cv_file	9 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\result.rs" "F7C1442406ACD37AB4FA1CAE6BB4BDDF12952055C92E908E434A8EE83C036678" 3
	.cv_inline_site_id 21 within 14 inlined_at 2 529 0
	.cv_loc	21 9 2176 0
	cmpl	$1, -24(%rbp)
	je	.LBB1_3
	.cv_loc	21 9 2177 0
	movq	-16(%rbp), %rax
.Ltmp14:
	.cv_inline_site_id 22 within 14 inlined_at 2 532 0
	.cv_loc	22 2 777 0
	movq	%rax, 8(%rsi)
	.cv_loc	22 2 778 0
	movq	%rdi, (%rsi)
.Ltmp15:
	.cv_loc	13 2 672 0
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB1_1:
	.cv_loc	13 2 670 0
	xorl	%ecx, %ecx
.Ltmp16:
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.LBB1_3:
.Ltmp17:
	.cv_loc	21 9 2178 0
	movq	-16(%rbp), %rcx
	movq	-8(%rbp), %rdx
.Ltmp18:
	.cv_loc	13 2 670 0
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.Ltmp19:
.Lfunc_end1:
	.seh_endproc

	.def	_RNvMNtCsfQUUnEvlYZE_5alloc6stringNtB2_6String10from_utf16;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMNtCsfQUUnEvlYZE_5alloc6stringNtB2_6String10from_utf16,unique,2
	.globl	_RNvMNtCsfQUUnEvlYZE_5alloc6stringNtB2_6String10from_utf16
	.p2align	4
_RNvMNtCsfQUUnEvlYZE_5alloc6stringNtB2_6String10from_utf16:
.Lfunc_begin2:
	.cv_func_id 23
	.cv_file	10 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\alloc\\src\\string.rs" "E3289C812F163BA94B10D43F7FA5BA3BF9133ADEAAA7733C4D796380E9AEAC1E" 3
	.cv_loc	23 10 725 0
.seh_proc _RNvMNtCsfQUUnEvlYZE_5alloc6stringNtB2_6String10from_utf16
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
.Ltmp22:
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
	subq	$72, %rsp
	.seh_stackalloc 72
	leaq	64(%rsp), %rbp
	.seh_setframe %rbp, 64
	.seh_endprologue
	.cv_inline_site_id 24 within 23 inlined_at 10 728 0
	.cv_inline_site_id 25 within 24 inlined_at 10 494 0
	.cv_file	11 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\alloc\\src\\vec\\mod.rs" "09171C3C4C767A5C0716A85786F7670E5E149F75325FC1B27F5DBCE14F16711F" 3
	.cv_inline_site_id 26 within 25 inlined_at 11 522 0
	.cv_inline_site_id 27 within 26 inlined_at 11 975 0
	.cv_inline_site_id 28 within 27 inlined_at 2 177 0
	.cv_inline_site_id 29 within 28 inlined_at 2 435 0
	.cv_loc	29 2 461 0
	movq	$-2, (%rbp)
	testq	%r8, %r8
	movq	%rcx, -32(%rbp)
	je	.LBB2_1
	.cv_inline_site_id 30 within 29 inlined_at 2 466 0
	.cv_inline_site_id 31 within 30 inlined_at 4 449 0
	.cv_inline_site_id 32 within 31 inlined_at 4 332 0
	.cv_inline_site_id 33 within 32 inlined_at 4 210 0
	.cv_inline_site_id 34 within 33 inlined_at 4 101 0
	.cv_inline_site_id 35 within 34 inlined_at 5 455 0
	.cv_inline_site_id 36 within 35 inlined_at 3 169 0
	.cv_loc	36 3 118 0
	movq	%r8, %rdi
	movq	%rdx, %rbx
.Ltmp23:
	xorl	%edx, %edx
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
.Ltmp24:
	.cv_loc	29 2 470 0
	testq	%rax, %rax
	je	.LBB2_31
.Ltmp25:
	.cv_loc	24 10 494 0
	movq	%rdi, -24(%rbp)
	movq	%rax, -16(%rbp)
	movq	$0, -8(%rbp)
.Ltmp26:
	.cv_file	12 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\ptr\\mut_ptr.rs" "54527A10B3C1B7BD589C13443EB2482BA8B8D9004B8184D58BB04A553345C1A9" 3
	.cv_inline_site_id 37 within 23 inlined_at 10 729 0
	.cv_file	13 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\slice\\mod.rs" "453BFD6E0FC09E06AC1793CCB03E2E2F04FAE149DB6A079256097C8FAD510669" 3
	.cv_inline_site_id 38 within 37 inlined_at 13 1044 0
	.cv_file	14 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\slice\\iter.rs" "83205F82241154964B1AECEF87913EC92CE8C0B99285337C04E37840594F9251" 3
	.cv_inline_site_id 39 within 38 inlined_at 14 100 0
	.cv_loc	39 12 970 0
	leaq	(%rbx,%rdi,2), %r12
	xorl	%edi, %edi
	leaq	-24(%rbp), %r9
	jmp	.LBB2_6
.Ltmp27:
	.p2align	4
.LBB2_33:
	.cv_file	15 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\char\\methods.rs" "12FA92FFE659911EDB658FACF59559E8CFBF7FEC49A712E1A0B28357CE25EE3A" 3
	.cv_inline_site_id 40 within 23 inlined_at 10 733 0
	.cv_inline_site_id 41 within 40 inlined_at 10 1428 0
	.cv_loc	41 15 2523 0
	movb	%r13b, (%rax,%rdi)
.Ltmp28:
.LBB2_30:
	.cv_loc	40 10 1429 0
	addq	%r15, %rdi
.Ltmp29:
	.cv_inline_site_id 42 within 40 inlined_at 10 1429 0
	.cv_loc	42 11 2231 0
	movq	%rdi, -8(%rbp)
.Ltmp30:
	.cv_file	16 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\ptr\\non_null.rs" "7705D8A3A9A939CE1026E5769D204410ECFF94AAEB7784079AA489DADF40527E" 3
	.cv_inline_site_id 43 within 23 inlined_at 10 729 0
	.cv_file	17 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\char\\decode.rs" "4617C15C9D74EFE7E82A9862994718DCE66F6DDB8943F2583F0984477923DA9A" 3
	.cv_inline_site_id 44 within 43 inlined_at 17 46 0
	.cv_file	18 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\iter\\adapters\\cloned.rs" "D6C913A61206A96E6D9444067137F6E5CB2B3D9E048E41E6BF551CD2EA13BB16" 3
	.cv_inline_site_id 45 within 44 inlined_at 18 41 0
	.cv_file	19 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\slice\\iter\\macros.rs" "0AC47D295999BA8847D0DF93557292FBAD65D256DB0C6521C396798D2E37677D" 3
	.cv_inline_site_id 46 within 45 inlined_at 19 180 0
	.cv_loc	46 16 1650 0
	cmpq	%r12, %rbx
.Ltmp31:
	.cv_loc	45 19 180 0
	je	.LBB2_2
.LBB2_6:
.Ltmp32:
	.cv_inline_site_id 47 within 45 inlined_at 19 185 0
	.cv_loc	47 16 614 0
	leaq	2(%rbx), %rcx
.Ltmp33:
	.cv_file	20 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\clone.rs" "FD3467602106E2A2EC416485D8D058B6D2B434CEAC7689B4E2F4C792079E500F" 3
	.cv_inline_site_id 48 within 44 inlined_at 18 41 0
	.cv_file	21 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\option.rs" "FC70106A756F98208E6A6A3E428310BDFA3531877CF6C6A99F39FFFA26AB2C40" 3
	.cv_inline_site_id 49 within 48 inlined_at 21 2164 0
	.cv_inline_site_id 50 within 49 inlined_at 21 1163 0
	.cv_file	22 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\ops\\function.rs" "35369957F4544972DF85E2778F15714E3AFC4F6A010049F18817AA85EDA1521D" 3
	.cv_inline_site_id 51 within 50 inlined_at 22 250 0
	.cv_loc	51 20 716 0
	movzwl	(%rbx), %edx
.Ltmp34:
	.cv_loc	43 17 51 0
	movzwl	%dx, %r13d
.Ltmp35:
	.cv_file	23 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\num\\mod.rs" "18488B4E0820BF6F9F6253CDCD7DF8134AC9BEAA0AE7CDB97050B18B02A93C37" 3
	.cv_inline_site_id 52 within 43 inlined_at 17 49 0
	.cv_loc	52 23 1282 0
	andl	$63488, %edx
	cmpl	$55296, %edx
	jne	.LBB2_14
.Ltmp36:
	.cv_loc	43 17 52 0
	cmpl	$56319, %r13d
	ja	.LBB2_16
	cmpq	%r12, %rcx
	je	.LBB2_16
.Ltmp37:
	.cv_inline_site_id 53 within 43 inlined_at 17 56 0
	.cv_inline_site_id 54 within 53 inlined_at 18 41 0
	.cv_inline_site_id 55 within 54 inlined_at 21 2164 0
	.cv_inline_site_id 56 within 55 inlined_at 21 1163 0
	.cv_inline_site_id 57 within 56 inlined_at 22 250 0
	.cv_loc	57 20 716 0
	movzwl	(%rcx), %r14d
.Ltmp38:
	.cv_loc	43 17 61 0
	leal	8192(%r14), %ecx
	movzwl	%cx, %ecx
	cmpl	$64512, %ecx
	jb	.LBB2_16
.Ltmp39:
	.cv_inline_site_id 58 within 53 inlined_at 18 41 0
	.cv_inline_site_id 59 within 58 inlined_at 19 185 0
	.cv_loc	59 16 614 0
	addq	$4, %rbx
.Ltmp40:
	.cv_loc	43 17 69 0
	andl	$1023, %r13d
	andl	$1023, %r14d
.Ltmp41:
	.cv_loc	43 17 71 0
	shlq	$26, %r13
	shll	$16, %r14d
	orq	%r13, %r14
	movabsq	$4294967296, %rcx
	addq	%rcx, %r14
.Ltmp42:
	.cv_loc	23 10 729 0
	movq	%r14, %r13
	shrq	$16, %r13
.Ltmp43:
	.cv_inline_site_id 60 within 40 inlined_at 10 1423 0
	.cv_inline_site_id 61 within 60 inlined_at 15 662 0
	.cv_loc	61 15 2452 0
	jmp	.LBB2_20
.Ltmp44:
	.p2align	4
.LBB2_14:
	.cv_loc	43 17 51 0
	movl	%r13d, %r14d
	shll	$16, %r14d
.Ltmp45:
	.cv_loc	61 15 2451 0
	cmpl	$128, %r13d
	jae	.LBB2_18
	.cv_loc	61 15 2452 0
	movl	$1, %r15d
	movb	$1, %sil
	movq	%rcx, %rbx
	jmp	.LBB2_21
	.p2align	4
.LBB2_18:
	cmpl	$2048, %r13d
	jae	.LBB2_19
	movl	$2, %r15d
	xorl	%esi, %esi
	movq	%rcx, %rbx
	jmp	.LBB2_21
.LBB2_19:
	movq	%rcx, %rbx
.LBB2_20:
	.cv_loc	61 15 2453 0
	movq	%r14, %rcx
	shrq	$32, %rcx
	cmpq	$1, %rcx
	movl	$4, %r15d
	sbbq	$0, %r15
	xorl	%esi, %esi
.Ltmp46:
.LBB2_21:
	.cv_inline_site_id 62 within 40 inlined_at 10 1424 0
	.cv_inline_site_id 63 within 62 inlined_at 10 1225 0
	.cv_inline_site_id 64 within 63 inlined_at 11 1469 0
	.cv_inline_site_id 65 within 64 inlined_at 2 341 0
	.cv_inline_site_id 66 within 65 inlined_at 2 674 0
	.cv_inline_site_id 67 within 66 inlined_at 2 768 0
	.cv_loc	67 2 620 0
	movq	-24(%rbp), %rcx
.Ltmp47:
	.cv_loc	67 6 2649 0
	subq	%rdi, %rcx
.Ltmp48:
	.cv_loc	66 2 768 0
	cmpq	%rcx, %r15
.Ltmp49:
	.cv_loc	65 2 674 0
	ja	.LBB2_22
.Ltmp50:
	.cv_inline_site_id 68 within 41 inlined_at 15 2518 0
	.cv_loc	68 15 2451 0
	testb	%sil, %sil
	jne	.LBB2_33
.Ltmp51:
.LBB2_25:
	.cv_loc	41 15 2527 0
	andb	$63, %r13b
	orb	$-128, %r13b
.Ltmp52:
	.cv_loc	41 15 2528 0
	movl	%r14d, %ecx
	shrl	$22, %ecx
.Ltmp53:
	.cv_loc	68 15 2452 0
	cmpq	$134217728, %r14
.Ltmp54:
	.cv_loc	41 15 2532 0
	jae	.LBB2_27
	.cv_loc	41 15 2533 0
	orb	$-64, %cl
	movb	%cl, (%rax,%rdi)
	.cv_loc	41 15 2534 0
	movb	%r13b, 1(%rax,%rdi)
	.cv_file	24 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\alloc\\src\\lib.rs" "A9EBB48FD573CE7F4371E6AB59FB2E0DD8EB85725ABFFAC804BFA3CB79B1F307" 3
	.cv_loc	41 24 1 0
	jmp	.LBB2_30
	.p2align	4
.LBB2_27:
	.cv_loc	41 15 2538 0
	andb	$63, %cl
	orb	$-128, %cl
	movq	%r14, %rdx
	shrq	$28, %rdx
	movq	%r14, %r8
	shrq	$32, %r8
	jne	.LBB2_29
	.cv_loc	41 15 2539 0
	orb	$-32, %dl
	movb	%dl, (%rax,%rdi)
	.cv_loc	41 15 2540 0
	movb	%cl, 1(%rax,%rdi)
	.cv_loc	41 15 2541 0
	movb	%r13b, 2(%rax,%rdi)
	.cv_loc	41 24 1 0
	jmp	.LBB2_30
.LBB2_29:
	.cv_loc	41 15 2545 0
	andb	$63, %dl
	orb	$-128, %dl
	shrq	$34, %r14
	orb	$-16, %r14b
	movb	%r14b, (%rax,%rdi)
	.cv_loc	41 15 2546 0
	movb	%dl, 1(%rax,%rdi)
	.cv_loc	41 15 2547 0
	movb	%cl, 2(%rax,%rdi)
	.cv_loc	41 15 2548 0
	movb	%r13b, 3(%rax,%rdi)
	jmp	.LBB2_30
.Ltmp55:
.LBB2_22:
	.cv_loc	65 2 676 0
.Ltmp20:
	movq	%r9, %rcx
	movq	%rdi, %rdx
	movq	%r15, %r8
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalEBa_
	nop
.Ltmp56:
.Ltmp21:
	.cv_inline_site_id 69 within 40 inlined_at 10 1428 0
	.cv_inline_site_id 70 within 69 inlined_at 11 2061 0
	.cv_inline_site_id 71 within 70 inlined_at 2 296 0
	.cv_inline_site_id 72 within 71 inlined_at 2 610 0
	.cv_loc	72 2 615 0
	movq	-16(%rbp), %rax
	leaq	-24(%rbp), %r9
.Ltmp57:
	.cv_loc	68 15 2451 0
	testb	%sil, %sil
	jne	.LBB2_33
	jmp	.LBB2_25
.Ltmp58:
.LBB2_1:
	.cv_loc	24 10 494 0
	movq	$0, -24(%rbp)
	movq	$1, -16(%rbp)
	movq	$0, -8(%rbp)
.Ltmp59:
.LBB2_2:
	.cv_loc	23 10 735 0
	movq	-8(%rbp), %rax
	movq	-32(%rbp), %rsi
	movq	%rax, 16(%rsi)
	movq	-24(%rbp), %rax
	movq	%rax, (%rsi)
	movq	-16(%rbp), %rax
	movq	%rax, 8(%rsi)
	jmp	.LBB2_3
.LBB2_16:
	.cv_loc	23 10 731 0
	movq	-32(%rbp), %rsi
.Ltmp60:
	movb	$0, 8(%rsi)
	movq	$-1, (%rsi)
.Ltmp61:
	.cv_inline_site_id 73 within 23 inlined_at 10 736 0
	.cv_inline_site_id 74 within 73 inlined_at 1 823 0
	.cv_inline_site_id 75 within 74 inlined_at 1 823 0
	.cv_inline_site_id 76 within 75 inlined_at 1 823 0
	.cv_inline_site_id 77 within 76 inlined_at 2 425 0
	.cv_inline_site_id 78 within 77 inlined_at 2 878 0
	.cv_loc	78 2 635 0
	cmpq	$0, -24(%rbp)
	je	.LBB2_3
.Ltmp62:
	.cv_loc	73 1 823 0
	movq	-16(%rbp), %rdi
.Ltmp63:
	.cv_inline_site_id 79 within 77 inlined_at 2 880 0
	.cv_inline_site_id 80 within 79 inlined_at 4 462 0
	.cv_inline_site_id 81 within 80 inlined_at 4 344 0
	.cv_inline_site_id 82 within 81 inlined_at 4 229 0
	.cv_inline_site_id 83 within 82 inlined_at 4 128 0
	.cv_inline_site_id 84 within 83 inlined_at 5 463 0
	.cv_inline_site_id 85 within 84 inlined_at 3 195 0
	.cv_loc	85 3 85 0
	callq	*__imp_GetProcessHeap(%rip)
.Ltmp64:
	.cv_loc	84 3 199 0
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rdi, %r8
	callq	*__imp_HeapFree(%rip)
.Ltmp65:
.LBB2_3:
	.cv_loc	23 10 736 0
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$72, %rsp
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
.LBB2_31:
.Ltmp66:
	.cv_loc	28 2 443 0
	movl	$1, %ecx
	movq	%rdi, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.Ltmp67:
	.seh_handlerdata
	.long	$cppxdata$_RNvMNtCsfQUUnEvlYZE_5alloc6stringNtB2_6String10from_utf16@IMGREL
	.section	.text,"xr",one_only,_RNvMNtCsfQUUnEvlYZE_5alloc6stringNtB2_6String10from_utf16,unique,2
	.seh_endproc
	.def	"?dtor$11@?0?_RNvMNtCsfQUUnEvlYZE_5alloc6stringNtB2_6String10from_utf16@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$11@?0?_RNvMNtCsfQUUnEvlYZE_5alloc6stringNtB2_6String10from_utf16@4HA":
.seh_proc "?dtor$11@?0?_RNvMNtCsfQUUnEvlYZE_5alloc6stringNtB2_6String10from_utf16@4HA"
.LBB2_11:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
.Ltmp68:
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
	leaq	64(%rdx), %rbp
	.seh_endprologue
	.cv_inline_site_id 86 within 23 inlined_at 10 736 0
	.cv_inline_site_id 87 within 86 inlined_at 1 823 0
	.cv_inline_site_id 88 within 87 inlined_at 1 823 0
	.cv_inline_site_id 89 within 88 inlined_at 1 823 0
	.cv_inline_site_id 90 within 89 inlined_at 2 425 0
	.cv_inline_site_id 91 within 90 inlined_at 2 878 0
	.cv_loc	91 2 635 0
	cmpq	$0, -24(%rbp)
	je	.LBB2_13
.Ltmp69:
	.cv_loc	86 1 823 0
	movq	-16(%rbp), %rsi
.Ltmp70:
	.cv_inline_site_id 92 within 90 inlined_at 2 880 0
	.cv_inline_site_id 93 within 92 inlined_at 4 462 0
	.cv_inline_site_id 94 within 93 inlined_at 4 344 0
	.cv_inline_site_id 95 within 94 inlined_at 4 229 0
	.cv_inline_site_id 96 within 95 inlined_at 4 128 0
	.cv_inline_site_id 97 within 96 inlined_at 5 463 0
	.cv_inline_site_id 98 within 97 inlined_at 3 195 0
	.cv_loc	98 3 85 0
	callq	*__imp_GetProcessHeap(%rip)
.Ltmp71:
	.cv_loc	97 3 199 0
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	nop
.Ltmp72:
.LBB2_13:
	.cv_loc	23 10 725 0
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
.Ltmp73:
.Lfunc_end2:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMNtCsfQUUnEvlYZE_5alloc6stringNtB2_6String10from_utf16,unique,2
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvMNtCsfQUUnEvlYZE_5alloc6stringNtB2_6String10from_utf16,unique,0
	.p2align	2, 0x0
$cppxdata$_RNvMNtCsfQUUnEvlYZE_5alloc6stringNtB2_6String10from_utf16:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNvMNtCsfQUUnEvlYZE_5alloc6stringNtB2_6String10from_utf16@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RNvMNtCsfQUUnEvlYZE_5alloc6stringNtB2_6String10from_utf16@IMGREL
	.long	64
	.long	0
	.long	1
$stateUnwindMap$_RNvMNtCsfQUUnEvlYZE_5alloc6stringNtB2_6String10from_utf16:
	.long	-1
	.long	"?dtor$11@?0?_RNvMNtCsfQUUnEvlYZE_5alloc6stringNtB2_6String10from_utf16@4HA"@IMGREL
$ip2state$_RNvMNtCsfQUUnEvlYZE_5alloc6stringNtB2_6String10from_utf16:
	.long	.Lfunc_begin2@IMGREL
	.long	-1
	.long	.Ltmp20@IMGREL
	.long	0
	.long	.Ltmp21@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvMNtCsfQUUnEvlYZE_5alloc6stringNtB2_6String10from_utf16,unique,2

	.def	_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf11into_string;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf11into_string,unique,3
	.globl	_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf11into_string
	.p2align	4
_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf11into_string:
.Lfunc_begin3:
	.cv_func_id 99
	.cv_file	25 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\alloc\\src\\wtf8\\mod.rs" "0A1250F80BA7B052502EEE04F23770FC7619054E5641F94A26BFA4375D82CFD1" 3
	.cv_loc	99 25 372 0
	.cv_loc	99 25 373 0
	movq	%rcx, %rax
.Ltmp74:
	cmpb	$0, 24(%rdx)
	jne	.LBB3_13
.Ltmp75:
	.cv_inline_site_id 100 within 99 inlined_at 25 373 0
	.cv_inline_site_id 101 within 100 inlined_at 25 56 0
	.cv_inline_site_id 102 within 101 inlined_at 25 176 0
	.cv_inline_site_id 103 within 102 inlined_at 11 3797 0
	.cv_loc	103 11 1873 0
	movq	16(%rdx), %rcx
.Ltmp76:
	.cv_inline_site_id 104 within 99 inlined_at 25 373 0
	.cv_file	26 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\wtf8.rs" "8FE8BC5934027E5F2790129E1898F0CFAD91EB7B3BBB29E007C3CB08C1835F2F" 3
	.cv_inline_site_id 105 within 104 inlined_at 26 293 0
	.cv_inline_site_id 106 within 105 inlined_at 19 180 0
	.cv_loc	106 16 1650 0
	testq	%rcx, %rcx
.Ltmp77:
	.cv_loc	105 19 180 0
	je	.LBB3_13
.Ltmp78:
	movq	8(%rdx), %r9
	addq	%r9, %rcx
	jmp	.LBB3_3
.LBB3_15:
	.cv_inline_site_id 107 within 104 inlined_at 26 297 0
	.cv_inline_site_id 108 within 107 inlined_at 19 180 0
	.cv_loc	108 16 1650 0
	addq	$2, %r9
.Ltmp79:
	cmpq	%rcx, %r8
.Ltmp80:
	.cv_loc	107 19 180 0
	cmovneq	%r9, %r8
.Ltmp81:
	.p2align	4
.LBB3_12:
	.cv_loc	106 16 1650 0
	movq	%r8, %r9
.Ltmp82:
	cmpq	%rcx, %r8
.Ltmp83:
	.cv_loc	105 19 180 0
	je	.LBB3_13
.LBB3_3:
.Ltmp84:
	.cv_inline_site_id 109 within 105 inlined_at 19 185 0
	.cv_loc	109 16 614 0
	leaq	1(%r9), %r8
.Ltmp85:
	.cv_loc	104 26 293 0
	movzbl	(%r9), %r10d
.Ltmp86:
	.cv_loc	104 26 294 0
	testb	%r10b, %r10b
	jns	.LBB3_12
	.cv_loc	104 26 296 0
	cmpb	$-32, %r10b
	jb	.LBB3_15
	.cv_loc	104 26 299 0
	cmpb	$-19, %r10b
	jne	.LBB3_10
.Ltmp87:
	.cv_inline_site_id 110 within 104 inlined_at 26 300 0
	.cv_inline_site_id 111 within 110 inlined_at 19 180 0
	.cv_loc	111 16 1650 0
	cmpq	%rcx, %r8
.Ltmp88:
	.cv_loc	110 19 180 0
	je	.LBB3_13
.Ltmp89:
	.cv_loc	110 19 180 0
	leaq	2(%r9), %r8
.Ltmp90:
	.cv_loc	110 19 180 0
	cmpq	%rcx, %r8
	je	.LBB3_13
.Ltmp91:
	.cv_loc	104 26 301 0
	cmpb	$-97, 1(%r9)
	ja	.LBB3_14
	addq	$3, %r9
	movq	%r9, %r8
	jmp	.LBB3_12
.LBB3_10:
	.cv_inline_site_id 112 within 104 inlined_at 26 0 0
	.cv_inline_site_id 113 within 112 inlined_at 19 180 0
	.cv_loc	113 16 1650 0
	addq	$2, %r9
.Ltmp92:
	cmpq	%rcx, %r8
.Ltmp93:
	.cv_loc	112 19 180 0
	cmoveq	%r8, %r9
.Ltmp94:
	.cv_loc	113 16 1650 0
	xorl	%r8d, %r8d
	cmpq	%rcx, %r9
	setne	%r8b
.Ltmp95:
	.cv_loc	112 19 180 0
	addq	%r9, %r8
.Ltmp96:
	.cv_loc	104 26 306 0
	cmpb	$-16, %r10b
	jb	.LBB3_12
.Ltmp97:
	.cv_inline_site_id 114 within 104 inlined_at 26 313 0
	.cv_inline_site_id 115 within 114 inlined_at 19 180 0
	.cv_loc	115 16 1650 0
	xorl	%r9d, %r9d
	cmpq	%rcx, %r8
	setne	%r9b
.Ltmp98:
	.cv_loc	114 19 180 0
	addq	%r9, %r8
	jmp	.LBB3_12
.Ltmp99:
.LBB3_13:
	.cv_loc	99 25 374 0
	movq	16(%rdx), %rcx
	movq	%rcx, 24(%rax)
	movups	(%rdx), %xmm0
	movups	%xmm0, 8(%rax)
	movq	$-1, (%rax)
	.cv_loc	99 25 378 0
	retq
.LBB3_14:
	.cv_loc	99 25 376 0
	movups	(%rdx), %xmm0
	movups	16(%rdx), %xmm1
	movups	%xmm1, 16(%rax)
	movups	%xmm0, (%rax)
	.cv_loc	99 25 378 0
	retq
.Ltmp100:
.Lfunc_end3:

	.def	_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf9from_wide;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf9from_wide,unique,4
	.globl	_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf9from_wide
	.p2align	4
_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf9from_wide:
.Lfunc_begin4:
	.cv_func_id 116
	.cv_loc	116 25 143 0
.seh_proc _RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf9from_wide
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
	subq	$88, %rsp
	.seh_stackalloc 88
	leaq	80(%rsp), %rbp
	.seh_setframe %rbp, 80
	.seh_endprologue
	movq	$-2, (%rbp)
	movq	%r8, %rbx
	movq	%rdx, %rdi
.Ltmp105:
	.cv_inline_site_id 117 within 116 inlined_at 25 144 0
	.cv_inline_site_id 118 within 117 inlined_at 25 102 0
	.cv_inline_site_id 119 within 118 inlined_at 11 522 0
	.cv_inline_site_id 120 within 119 inlined_at 11 975 0
	.cv_inline_site_id 121 within 120 inlined_at 2 177 0
	.cv_inline_site_id 122 within 121 inlined_at 2 435 0
	.cv_loc	122 2 461 0
	testq	%r8, %r8
	movq	%rcx, -48(%rbp)
	je	.LBB4_1
.Ltmp106:
	.cv_inline_site_id 123 within 122 inlined_at 2 466 0
	.cv_inline_site_id 124 within 123 inlined_at 4 449 0
	.cv_inline_site_id 125 within 124 inlined_at 4 332 0
	.cv_inline_site_id 126 within 125 inlined_at 4 210 0
	.cv_inline_site_id 127 within 126 inlined_at 4 101 0
	.cv_inline_site_id 128 within 127 inlined_at 5 455 0
	.cv_inline_site_id 129 within 128 inlined_at 3 169 0
	.cv_loc	129 3 118 0
	xorl	%edx, %edx
	movq	%rbx, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
.Ltmp107:
	.cv_loc	122 2 470 0
	testq	%rax, %rax
	je	.LBB4_36
.Ltmp108:
	movq	%rax, %r12
	jmp	.LBB4_4
.Ltmp109:
.LBB4_1:
	movl	$1, %r12d
.LBB4_4:
	.cv_loc	117 25 102 0
	movq	%rbx, -40(%rbp)
	movq	%r12, -32(%rbp)
	movq	$0, -24(%rbp)
	movb	$1, -16(%rbp)
.Ltmp110:
	.cv_inline_site_id 130 within 116 inlined_at 25 145 0
	.cv_inline_site_id 131 within 130 inlined_at 13 1044 0
	.cv_inline_site_id 132 within 131 inlined_at 14 100 0
	.cv_loc	132 12 970 0
	leaq	(%rdi,%rbx,2), %rbx
	xorl	%r15d, %r15d
	xorl	%r14d, %r14d
.Ltmp111:
	.p2align	4
.LBB4_5:
	.cv_inline_site_id 133 within 116 inlined_at 25 145 0
	.cv_loc	133 17 44 0
	testb	$1, %r14b
	je	.LBB4_7
	movl	%esi, %r13d
	jmp	.LBB4_9
	.p2align	4
.LBB4_7:
.Ltmp112:
	.cv_inline_site_id 134 within 133 inlined_at 17 46 0
	.cv_inline_site_id 135 within 134 inlined_at 18 41 0
	.cv_inline_site_id 136 within 135 inlined_at 19 180 0
	.cv_loc	136 16 1650 0
	cmpq	%rbx, %rdi
.Ltmp113:
	.cv_loc	135 19 180 0
	je	.LBB4_24
.Ltmp114:
	.cv_inline_site_id 137 within 134 inlined_at 18 41 0
	.cv_inline_site_id 138 within 137 inlined_at 21 2164 0
	.cv_inline_site_id 139 within 138 inlined_at 21 1163 0
	.cv_inline_site_id 140 within 139 inlined_at 22 250 0
	.cv_loc	140 20 716 0
	movzwl	(%rdi), %r13d
.Ltmp115:
	.cv_inline_site_id 141 within 135 inlined_at 19 185 0
	.cv_loc	141 16 614 0
	addq	$2, %rdi
.Ltmp116:
.LBB4_9:
	.cv_inline_site_id 142 within 133 inlined_at 17 49 0
	.cv_loc	142 23 1282 0
	movl	%r13d, %ecx
	andl	$63488, %ecx
	movzwl	%r13w, %eax
	cmpl	$55296, %ecx
	jne	.LBB4_25
.Ltmp117:
	.cv_loc	133 17 52 0
	cmpl	$56319, %eax
	ja	.LBB4_11
.Ltmp118:
	.cv_inline_site_id 143 within 133 inlined_at 17 56 0
	.cv_inline_site_id 144 within 143 inlined_at 18 41 0
	.cv_inline_site_id 145 within 144 inlined_at 19 180 0
	.cv_loc	145 16 1650 0
	cmpq	%rbx, %rdi
.Ltmp119:
	.cv_loc	144 19 180 0
	je	.LBB4_17
.Ltmp120:
	.cv_inline_site_id 146 within 143 inlined_at 18 41 0
	.cv_inline_site_id 147 within 146 inlined_at 21 2164 0
	.cv_inline_site_id 148 within 147 inlined_at 21 1163 0
	.cv_inline_site_id 149 within 148 inlined_at 22 250 0
	.cv_loc	149 20 716 0
	movzwl	(%rdi), %eax
.Ltmp121:
	.cv_inline_site_id 150 within 144 inlined_at 19 185 0
	.cv_loc	150 16 614 0
	addq	$2, %rdi
.Ltmp122:
	.cv_loc	133 17 61 0
	movl	%eax, %ecx
	addl	$8192, %ecx
	movzwl	%cx, %ecx
	cmpl	$64512, %ecx
	jb	.LBB4_19
	.cv_loc	133 17 69 0
	movzwl	%ax, %ecx
	andl	$1023, %r13d
	andl	$1023, %ecx
.Ltmp123:
	.cv_loc	133 17 71 0
	shlq	$26, %r13
	shll	$16, %ecx
	orq	%r13, %rcx
	movabsq	$4294967296, %rax
	addq	%rax, %rcx
.Ltmp124:
	.cv_loc	116 25 145 0
	movq	%rcx, %rax
	shrq	$16, %rax
.Ltmp125:
	.cv_inline_site_id 151 within 116 inlined_at 25 147 0
	.cv_inline_site_id 152 within 151 inlined_at 25 314 0
	.cv_loc	152 25 169 0
	movl	$0, -4(%rbp)
.Ltmp126:
	.cv_inline_site_id 153 within 152 inlined_at 25 170 0
	.cv_inline_site_id 154 within 153 inlined_at 15 2481 0
	.cv_loc	154 15 2451 0
	jmp	.LBB4_27
.Ltmp127:
	.p2align	4
.LBB4_25:
	.cv_loc	152 25 169 0
	movl	$0, -4(%rbp)
.Ltmp128:
	.cv_loc	154 15 2451 0
	cmpl	$128, %eax
	jae	.LBB4_26
.Ltmp129:
	.cv_inline_site_id 155 within 153 inlined_at 15 2493 0
	.cv_loc	155 15 2523 0
	movb	%r13b, -4(%rbp)
	movl	$1, %r13d
	.cv_loc	155 24 1 0
	jmp	.LBB4_32
	.p2align	4
.LBB4_26:
	movl	%eax, %ecx
	shll	$16, %ecx
.LBB4_27:
	.cv_loc	155 15 2527 0
	andb	$63, %al
	orb	$-128, %al
.Ltmp130:
	.cv_loc	155 15 2528 0
	movl	%ecx, %edx
	shrl	$22, %edx
.Ltmp131:
	.cv_loc	154 15 2452 0
	cmpq	$134217728, %rcx
.Ltmp132:
	.cv_loc	155 15 2532 0
	jae	.LBB4_29
	.cv_loc	155 15 2533 0
	orb	$-64, %dl
	movb	%dl, -4(%rbp)
	.cv_loc	155 15 2534 0
	movb	%al, -3(%rbp)
	movl	$2, %r13d
	.cv_loc	155 24 1 0
	jmp	.LBB4_32
.Ltmp133:
	.p2align	4
.LBB4_29:
	.cv_loc	154 15 2452 0
	andb	$63, %dl
	orb	$-128, %dl
	movq	%rcx, %r8
	shrq	$28, %r8
.Ltmp134:
	movq	%rcx, %r9
	shrq	$32, %r9
.Ltmp135:
	.cv_loc	155 15 2538 0
	jne	.LBB4_31
	.cv_loc	155 15 2539 0
	orb	$-32, %r8b
	movb	%r8b, -4(%rbp)
	.cv_loc	155 15 2540 0
	movb	%dl, -3(%rbp)
	.cv_loc	155 15 2541 0
	movb	%al, -2(%rbp)
	movl	$3, %r13d
	.cv_loc	155 24 1 0
	jmp	.LBB4_32
.Ltmp136:
.LBB4_31:
	.cv_loc	155 15 2545 0
	andb	$63, %r8b
	orb	$-128, %r8b
	shrq	$34, %rcx
	orb	$-16, %cl
.Ltmp137:
	movb	%cl, -4(%rbp)
	.cv_loc	155 15 2546 0
	movb	%r8b, -3(%rbp)
	.cv_loc	155 15 2547 0
	movb	%dl, -2(%rbp)
	.cv_loc	155 15 2548 0
	movb	%al, -1(%rbp)
	movl	$4, %r13d
.Ltmp138:
	.p2align	4
.LBB4_32:
	.cv_inline_site_id 156 within 152 inlined_at 25 171 0
	.cv_inline_site_id 157 within 156 inlined_at 11 3567 0
	.cv_file	27 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\alloc\\src\\vec\\spec_extend.rs" "A0816AD0F39B947889771BF06930BF8E0C4CE794846D83863349697EC7C415EC" 3
	.cv_inline_site_id 158 within 157 inlined_at 27 56 0
	.cv_inline_site_id 159 within 158 inlined_at 11 2942 0
	.cv_inline_site_id 160 within 159 inlined_at 11 1469 0
	.cv_inline_site_id 161 within 160 inlined_at 2 341 0
	.cv_inline_site_id 162 within 161 inlined_at 2 674 0
	.cv_inline_site_id 163 within 162 inlined_at 2 768 0
	.cv_loc	163 2 620 0
	movq	-40(%rbp), %rax
.Ltmp139:
	.cv_loc	163 6 2649 0
	subq	%r15, %rax
.Ltmp140:
	.cv_loc	162 2 768 0
	cmpq	%rax, %r13
.Ltmp141:
	.cv_loc	161 2 674 0
	ja	.LBB4_33
.Ltmp142:
.LBB4_35:
	.cv_inline_site_id 164 within 158 inlined_at 11 2946 0
	.cv_loc	164 12 970 0
	leaq	(%r12,%r15), %rcx
.Ltmp143:
	.cv_loc	164 1 549 0
	leaq	-4(%rbp), %rdx
	movq	%r13, %r8
	callq	memcpy
.Ltmp144:
	.cv_loc	158 11 2949 0
	addq	%r13, %r15
	movq	%r15, -24(%rbp)
	xorl	%r14d, %r14d
.Ltmp145:
	.cv_loc	152 25 172 0
	jmp	.LBB4_5
.Ltmp146:
.LBB4_11:
	xorl	%r14d, %r14d
	jmp	.LBB4_12
.LBB4_17:
	.cv_loc	144 19 180 0
	xorl	%r14d, %r14d
	movq	%rbx, %rdi
.Ltmp147:
	jmp	.LBB4_12
.Ltmp148:
.LBB4_19:
	movb	$1, %r14b
	movl	%eax, %esi
.LBB4_12:
.Ltmp149:
	.cv_loc	116 25 153 0
	movb	$0, -16(%rbp)
.Ltmp150:
	.cv_inline_site_id 165 within 116 inlined_at 25 157 0
	.cv_inline_site_id 166 within 165 inlined_at 25 171 0
	.cv_inline_site_id 167 within 166 inlined_at 11 3567 0
	.cv_inline_site_id 168 within 167 inlined_at 27 56 0
	.cv_inline_site_id 169 within 168 inlined_at 11 2942 0
	.cv_inline_site_id 170 within 169 inlined_at 11 1469 0
	.cv_inline_site_id 171 within 170 inlined_at 2 341 0
	.cv_inline_site_id 172 within 171 inlined_at 2 674 0
	.cv_inline_site_id 173 within 172 inlined_at 2 768 0
	.cv_loc	173 2 620 0
	movq	-40(%rbp), %rax
.Ltmp151:
	.cv_loc	173 6 2649 0
	subq	%r15, %rax
.Ltmp152:
	.cv_loc	172 2 768 0
	cmpq	$2, %rax
	jbe	.LBB4_13
.Ltmp153:
.LBB4_15:
	.cv_inline_site_id 174 within 168 inlined_at 11 2946 0
	.cv_inline_site_id 175 within 174 inlined_at 11 2061 0
	.cv_inline_site_id 176 within 175 inlined_at 2 296 0
	.cv_inline_site_id 177 within 176 inlined_at 2 610 0
	.cv_loc	177 2 615 0
	movl	%r13d, %eax
	andb	$63, %al
	orb	$-128, %al
	shrl	$6, %r13d
	andb	$63, %r13b
	orb	$-128, %r13b
.Ltmp154:
	movq	-32(%rbp), %r12
.Ltmp155:
	.cv_loc	174 1 549 0
	movb	$-19, (%r12,%r15)
	movb	%r13b, 1(%r12,%r15)
	movb	%al, 2(%r12,%r15)
.Ltmp156:
	.cv_loc	168 11 2949 0
	addq	$3, %r15
	movq	%r15, -24(%rbp)
.Ltmp157:
	.cv_loc	165 25 172 0
	jmp	.LBB4_5
.Ltmp158:
.LBB4_33:
	.cv_loc	161 2 676 0
.Ltmp101:
	leaq	-40(%rbp), %rcx
	movq	%r15, %rdx
	movq	%r13, %r8
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalEBa_
	nop
.Ltmp159:
.Ltmp102:
	.cv_inline_site_id 178 within 164 inlined_at 11 2061 0
	.cv_inline_site_id 179 within 178 inlined_at 2 296 0
	.cv_inline_site_id 180 within 179 inlined_at 2 610 0
	.cv_loc	180 2 615 0
	movq	-32(%rbp), %r12
.Ltmp160:
	.cv_inline_site_id 181 within 158 inlined_at 11 2943 0
	.cv_loc	181 11 3064 0
	movq	-24(%rbp), %r15
	jmp	.LBB4_35
.Ltmp161:
.LBB4_13:
	.cv_loc	171 2 676 0
.Ltmp103:
	movl	$3, %r8d
	leaq	-40(%rbp), %rcx
	movq	%r15, %rdx
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalEBa_
	nop
.Ltmp162:
.Ltmp104:
	.cv_inline_site_id 182 within 168 inlined_at 11 2943 0
	.cv_loc	182 11 3064 0
	movq	-24(%rbp), %r15
	jmp	.LBB4_15
.Ltmp163:
.LBB4_24:
	.cv_loc	116 25 162 0
	movups	-40(%rbp), %xmm0
	movups	-24(%rbp), %xmm1
	movq	-48(%rbp), %rax
	movups	%xmm1, 16(%rax)
	movups	%xmm0, (%rax)
.Ltmp164:
	.cv_loc	116 25 163 0
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
.LBB4_36:
.Ltmp165:
	.cv_loc	121 2 443 0
	movl	$1, %ecx
	movq	%rbx, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.Ltmp166:
	.seh_handlerdata
	.long	$cppxdata$_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf9from_wide@IMGREL
	.section	.text,"xr",one_only,_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf9from_wide,unique,4
	.seh_endproc
	.def	"?dtor$21@?0?_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf9from_wide@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$21@?0?_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf9from_wide@4HA":
.seh_proc "?dtor$21@?0?_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf9from_wide@4HA"
.LBB4_21:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
.Ltmp167:
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
	leaq	80(%rdx), %rbp
	.seh_endprologue
	.cv_inline_site_id 183 within 116 inlined_at 25 163 0
	.cv_inline_site_id 184 within 183 inlined_at 1 823 0
	.cv_inline_site_id 185 within 184 inlined_at 1 823 0
	.cv_inline_site_id 186 within 185 inlined_at 1 823 0
	.cv_inline_site_id 187 within 186 inlined_at 2 425 0
	.cv_inline_site_id 188 within 187 inlined_at 2 878 0
	.cv_loc	188 2 635 0
	cmpq	$0, -40(%rbp)
	je	.LBB4_23
.Ltmp168:
	.cv_loc	116 25 163 0
	movq	-32(%rbp), %rsi
.Ltmp169:
	.cv_inline_site_id 189 within 187 inlined_at 2 880 0
	.cv_inline_site_id 190 within 189 inlined_at 4 462 0
	.cv_inline_site_id 191 within 190 inlined_at 4 344 0
	.cv_inline_site_id 192 within 191 inlined_at 4 229 0
	.cv_inline_site_id 193 within 192 inlined_at 4 128 0
	.cv_inline_site_id 194 within 193 inlined_at 5 463 0
	.cv_inline_site_id 195 within 194 inlined_at 3 195 0
	.cv_loc	195 3 85 0
	callq	*__imp_GetProcessHeap(%rip)
.Ltmp170:
	.cv_loc	194 3 199 0
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	nop
.Ltmp171:
.LBB4_23:
	.cv_loc	116 25 143 0
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
.Ltmp172:
.Lfunc_end4:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf9from_wide,unique,4
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf9from_wide,unique,1
	.p2align	2, 0x0
$cppxdata$_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf9from_wide:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf9from_wide@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf9from_wide@IMGREL
	.long	80
	.long	0
	.long	1
$stateUnwindMap$_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf9from_wide:
	.long	-1
	.long	"?dtor$21@?0?_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf9from_wide@4HA"@IMGREL
$ip2state$_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf9from_wide:
	.long	.Lfunc_begin4@IMGREL
	.long	-1
	.long	.Ltmp101@IMGREL
	.long	0
	.long	.Ltmp104@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf9from_wide,unique,4

	.def	_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growB7_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growB7_,unique,5
	.p2align	4
_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growB7_:
.Lfunc_begin5:
	.cv_func_id 196
	.cv_loc	196 2 544 0
.seh_proc _RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growB7_
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
	movq	%rcx, %rsi
	movl	$1, %r14d
.Ltmp173:
	.cv_file	28 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\alloc\\layout.rs" "19119EDE8A60D1A989F907118F9E7F36E24434B8E931875F66A379B856784124" 3
	.cv_inline_site_id 197 within 196 inlined_at 2 549 0
	.cv_inline_site_id 198 within 197 inlined_at 2 905 0
	.cv_inline_site_id 199 within 198 inlined_at 28 529 0
	.cv_inline_site_id 200 within 199 inlined_at 28 113 0
	.cv_loc	200 28 75 0
	testq	%r9, %r9
.Ltmp174:
	.cv_loc	199 28 113 0
	js	.LBB5_1
.Ltmp175:
	.cv_inline_site_id 201 within 196 inlined_at 2 551 0
	.cv_loc	201 2 635 0
	movq	%r9, %rdi
.Ltmp176:
	testq	%rdx, %rdx
	je	.LBB5_4
.Ltmp177:
	.cv_inline_site_id 202 within 196 inlined_at 2 557 0
	.cv_inline_site_id 203 within 202 inlined_at 4 474 0
	.cv_inline_site_id 204 within 203 inlined_at 4 362 0
	.cv_inline_site_id 205 within 204 inlined_at 4 259 0
	.cv_inline_site_id 206 within 205 inlined_at 4 155 0
	.cv_inline_site_id 207 within 206 inlined_at 5 477 0
	.cv_inline_site_id 208 within 207 inlined_at 3 207 0
	.cv_loc	208 3 85 0
	movq	%r8, %rbx
.Ltmp178:
	callq	*__imp_GetProcessHeap(%rip)
.Ltmp179:
	.cv_loc	207 3 212 0
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rbx, %r8
	movq	%rdi, %r9
	callq	*__imp_HeapReAlloc(%rip)
.Ltmp180:
	.cv_loc	196 2 564 0
	testq	%rax, %rax
	je	.LBB5_6
.LBB5_7:
.Ltmp181:
	.cv_loc	196 2 565 0
	movq	%rax, 8(%rsi)
	movl	$16, %eax
	xorl	%r14d, %r14d
	jmp	.LBB5_8
.Ltmp182:
.LBB5_1:
	.cv_loc	199 28 113 0
	movl	$8, %eax
	xorl	%edi, %edi
.Ltmp183:
	jmp	.LBB5_8
.Ltmp184:
.LBB5_4:
	.cv_inline_site_id 209 within 196 inlined_at 2 560 0
	.cv_inline_site_id 210 within 209 inlined_at 4 449 0
	.cv_inline_site_id 211 within 210 inlined_at 4 332 0
	.cv_inline_site_id 212 within 211 inlined_at 4 210 0
	.cv_inline_site_id 213 within 212 inlined_at 4 101 0
	.cv_inline_site_id 214 within 213 inlined_at 5 455 0
	.cv_inline_site_id 215 within 214 inlined_at 3 169 0
	.cv_loc	215 3 118 0
	xorl	%edx, %edx
	movq	%rdi, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
.Ltmp185:
	.cv_loc	196 2 564 0
	testq	%rax, %rax
	jne	.LBB5_7
.LBB5_6:
	.cv_loc	196 2 566 0
	movq	$1, 8(%rsi)
	movl	$16, %eax
.Ltmp186:
.LBB5_8:
	.cv_loc	196 2 568 0
	movq	%rdi, (%rsi,%rax)
	movq	%r14, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.Ltmp187:
.Lfunc_end5:
	.seh_endproc

	.def	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error,unique,6
	.globl	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error:
.Lfunc_begin6:
	.cv_func_id 216
	.cv_loc	216 4 543 0
.seh_proc _RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	32(%rsp), %rbp
	.seh_setframe %rbp, 32
	.seh_endprologue
	movq	%rcx, %rax
.Ltmp188:
	.cv_inline_site_id 217 within 216 inlined_at 4 557 0
	.cv_loc	217 4 551 0
	movq	%rdx, %rcx
	movq	%rax, %rdx
	callq	_RNvCs1njKG4L9aB3_7___rustc26___rust_alloc_error_handler
	ud2
.Ltmp189:
.Lfunc_end6:
	.seh_endproc

	.def	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error,unique,7
	.globl	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error:
.Lfunc_begin7:
	.cv_func_id 218
	.cv_loc	218 2 891 0
.seh_proc _RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	32(%rsp), %rbp
	.seh_setframe %rbp, 32
	.seh_endprologue
.Ltmp190:
	.cv_file	29 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\alloc\\src\\collections\\mod.rs" "F31785DCB5282FCEF504BB4D815D34909D47C3FB2D35974356E18826C6FCB0C6" 3
	.cv_inline_site_id 219 within 218 inlined_at 2 892 0
	.cv_inline_site_id 220 within 219 inlined_at 29 90 0
	.cv_loc	220 29 134 0
	testq	%rcx, %rcx
	jne	.LBB7_1
.Ltmp191:
	.cv_loc	218 2 893 0
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec17capacity_overflow
	ud2
.LBB7_1:
.Ltmp192:
	.cv_loc	218 2 894 0
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	ud2
.Ltmp193:
.Lfunc_end7:
	.seh_endproc

	.def	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec17capacity_overflow;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec17capacity_overflow,unique,8
	.globl	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec17capacity_overflow
	.p2align	4
_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec17capacity_overflow:
.Lfunc_begin8:
	.cv_func_id 221
	.cv_loc	221 2 27 0
.seh_proc _RNvNtCsfQUUnEvlYZE_5alloc7raw_vec17capacity_overflow
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	32(%rsp), %rbp
	.seh_setframe %rbp, 32
	.seh_endprologue
.Ltmp194:
	.cv_loc	221 2 28 0
	leaq	anon.cf47210967777a51b7227f8e6911a3b4.27(%rip), %rcx
	leaq	anon.cf47210967777a51b7227f8e6911a3b4.28(%rip), %r8
	movl	$35, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking9panic_fmt
	ud2
.Ltmp195:
.Lfunc_end8:
	.seh_endproc

	.def	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner,unique,9
	.globl	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	.p2align	4
_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner:
.Lfunc_begin9:
	.cv_func_id 222
	.cv_file	30 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\alloc\\src\\fmt.rs" "5787EE1AC366050193DB15B5AC46D74FDE2BDCC0CE096E9962B2BF39C5D49510" 3
	.cv_loc	222 30 650 0
.seh_proc _RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
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
	subq	$80, %rsp
	.seh_stackalloc 80
	leaq	80(%rsp), %rbp
	.seh_setframe %rbp, 80
	.seh_endprologue
	movq	$-2, -8(%rbp)
	movq	%r8, %rdi
	movq	%rdx, %rbx
	movq	%rcx, %rsi
.Ltmp200:
	.cv_file	31 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\fmt\\mod.rs" "67C9BACB0202A1D75BB1332F9146A904A117FDE03E05C6951919D14414196FD2" 3
	.cv_inline_site_id 223 within 222 inlined_at 30 651 0
	.cv_inline_site_id 224 within 223 inlined_at 31 755 0
	.cv_loc	224 31 878 0
	testb	$1, %dil
	jne	.LBB9_1
.Ltmp201:
	.cv_inline_site_id 225 within 223 inlined_at 31 765 0
	.cv_inline_site_id 226 within 225 inlined_at 16 923 0
	.cv_loc	226 1 1731 0
	movzbl	(%rbx), %edx
.Ltmp202:
	.cv_loc	223 31 767 0
	testb	%dl, %dl
	je	.LBB9_3
	xorl	%eax, %eax
	movq	%rbx, %rcx
	xorl	%r14d, %r14d
	jmp	.LBB9_10
	.p2align	4
.LBB9_15:
	.cv_loc	223 31 772 0
	movzbl	%dl, %edx
	addq	%rdx, %r14
.Ltmp203:
	.cv_inline_site_id 227 within 223 inlined_at 31 773 0
	.cv_loc	227 16 614 0
	addq	%rdx, %rcx
.Ltmp204:
.LBB9_17:
	.cv_loc	226 1 1731 0
	movzbl	(%rcx), %edx
.Ltmp205:
	.cv_loc	223 31 767 0
	testb	%dl, %dl
	je	.LBB9_13
.LBB9_10:
.Ltmp206:
	.cv_inline_site_id 228 within 223 inlined_at 31 766 0
	.cv_loc	228 16 614 0
	incq	%rcx
.Ltmp207:
	.cv_loc	223 31 770 0
	testb	%dl, %dl
	jns	.LBB9_15
	.cv_loc	223 31 774 0
	movl	%edx, %r8d
	negb	%r8b
	jno	.LBB9_16
.Ltmp208:
	.cv_inline_site_id 229 within 223 inlined_at 31 776 0
	.cv_inline_site_id 230 within 229 inlined_at 16 923 0
	.cv_loc	230 1 1731 0
	movzwl	(%rcx), %edx
.Ltmp209:
	.cv_loc	223 31 777 0
	addq	%rdx, %r14
.Ltmp210:
	.cv_inline_site_id 231 within 223 inlined_at 31 778 0
	.cv_loc	231 16 614 0
	addq	%rdx, %rcx
	addq	$2, %rcx
.Ltmp211:
	.cv_loc	223 31 774 0
	jmp	.LBB9_17
.LBB9_16:
	.cv_loc	223 31 782 0
	testq	%r14, %r14
	sete	%r8b
	orb	%r8b, %al
	.cv_loc	223 31 786 0
	movl	%edx, %r8d
	shlb	$7, %r8b
	movl	%edx, %r9d
	shlb	$5, %r9b
	andb	$64, %r9b
	orb	%r8b, %r9b
	shrb	$5, %r9b
	movzbl	%r9b, %r8d
	.cv_loc	223 31 788 0
	movl	%edx, %r9d
	shrb	%r9b
	andb	$2, %r9b
	movzbl	%r9b, %r9d
	.cv_loc	223 31 789 0
	shrb	$2, %dl
	andb	$2, %dl
	movzbl	%dl, %edx
.Ltmp212:
	.cv_inline_site_id 232 within 223 inlined_at 31 790 0
	.cv_loc	232 16 614 0
	addq	%r9, %rcx
	addq	%rdx, %rcx
	addq	%r8, %rcx
	jmp	.LBB9_17
.Ltmp213:
.LBB9_1:
	.cv_loc	224 31 883 0
	movq	%rdi, %r14
	shrq	%r14
	jmp	.LBB9_2
.Ltmp214:
.LBB9_13:
	.cv_loc	223 31 795 0
	cmpq	$16, %r14
	setb	%cl
	testb	%cl, %al
	je	.LBB9_18
	xorl	%r14d, %r14d
	jmp	.LBB9_2
.Ltmp215:
.LBB9_18:
	.cv_inline_site_id 233 within 222 inlined_at 30 652 0
	.cv_inline_site_id 234 within 233 inlined_at 10 494 0
	.cv_inline_site_id 235 within 234 inlined_at 11 522 0
	.cv_inline_site_id 236 within 235 inlined_at 11 975 0
	.cv_inline_site_id 237 within 236 inlined_at 2 177 0
	.cv_inline_site_id 238 within 237 inlined_at 2 435 0
	.cv_inline_site_id 239 within 238 inlined_at 2 455 0
	.cv_inline_site_id 240 within 239 inlined_at 2 905 0
	.cv_inline_site_id 241 within 240 inlined_at 28 529 0
	.cv_loc	241 28 113 0
	addq	%r14, %r14
.Ltmp216:
	js	.LBB9_19
.Ltmp217:
.LBB9_2:
	.cv_loc	238 2 461 0
	testq	%r14, %r14
	je	.LBB9_3
.Ltmp218:
	.cv_inline_site_id 242 within 238 inlined_at 2 466 0
	.cv_inline_site_id 243 within 242 inlined_at 4 449 0
	.cv_inline_site_id 244 within 243 inlined_at 4 332 0
	.cv_inline_site_id 245 within 244 inlined_at 4 210 0
	.cv_inline_site_id 246 within 245 inlined_at 4 101 0
	.cv_inline_site_id 247 within 246 inlined_at 5 455 0
	.cv_inline_site_id 248 within 247 inlined_at 3 169 0
	.cv_loc	248 3 118 0
	xorl	%edx, %edx
	movq	%r14, %r8
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
.Ltmp219:
	.cv_loc	238 2 470 0
	testq	%rax, %rax
	jne	.LBB9_4
.Ltmp220:
	.cv_loc	237 2 443 0
	movl	$1, %ecx
.Ltmp221:
	movq	%r14, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.Ltmp222:
.LBB9_3:
	movl	$1, %eax
	xorl	%r14d, %r14d
.LBB9_4:
	.cv_loc	233 10 494 0
	movq	%r14, -40(%rbp)
	movq	%rax, -32(%rbp)
	movq	$0, -24(%rbp)
.Ltmp223:
	.cv_inline_site_id 249 within 222 inlined_at 30 654 0
	.cv_inline_site_id 250 within 249 inlined_at 31 243 0
	.cv_loc	250 31 238 0
.Ltmp196:
	leaq	anon.cf47210967777a51b7227f8e6911a3b4.34(%rip), %rdx
	leaq	-40(%rbp), %rcx
	movq	%rbx, %r8
	movq	%rdi, %r9
	callq	_RNvNtCs8xEFJqa6dYS_4core3fmt5write
	nop
.Ltmp224:
.Ltmp197:
	.cv_inline_site_id 251 within 222 inlined_at 30 655 0
	.cv_loc	251 9 1181 0
	testb	%al, %al
	jne	.LBB9_6
.Ltmp225:
	.cv_loc	222 30 656 0
	movq	-24(%rbp), %rax
	movq	%rax, 16(%rsi)
	movups	-40(%rbp), %xmm0
	movups	%xmm0, (%rsi)
.Ltmp226:
	.cv_loc	222 30 657 0
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.LBB9_6:
	.cv_loc	251 9 1183 0
.Ltmp198:
.Ltmp227:
	leaq	anon.cf47210967777a51b7227f8e6911a3b4.37(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	anon.cf47210967777a51b7227f8e6911a3b4.35(%rip), %rcx
	leaq	anon.cf47210967777a51b7227f8e6911a3b4.6(%rip), %r9
	leaq	-9(%rbp), %r8
	movl	$86, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core6result13unwrap_failed
	nop
.Ltmp228:
.Ltmp199:
	ud2
.LBB9_19:
	.cv_loc	237 2 443 0
	xorl	%ecx, %ecx
.Ltmp229:
	movq	%r14, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.Ltmp230:
	.seh_handlerdata
	.long	$cppxdata$_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner@IMGREL
	.section	.text,"xr",one_only,_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner,unique,9
	.seh_endproc
	.def	"?dtor$23@?0?_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$23@?0?_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner@4HA":
.seh_proc "?dtor$23@?0?_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner@4HA"
.LBB9_23:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
.Ltmp231:
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
	leaq	80(%rdx), %rbp
	.seh_endprologue
	.cv_inline_site_id 252 within 222 inlined_at 30 657 0
	.cv_inline_site_id 253 within 252 inlined_at 1 823 0
	.cv_inline_site_id 254 within 253 inlined_at 1 823 0
	.cv_inline_site_id 255 within 254 inlined_at 1 823 0
	.cv_inline_site_id 256 within 255 inlined_at 2 425 0
	.cv_inline_site_id 257 within 256 inlined_at 2 878 0
	.cv_loc	257 2 635 0
	cmpq	$0, -40(%rbp)
	je	.LBB9_25
.Ltmp232:
	.cv_loc	252 1 823 0
	movq	-32(%rbp), %rsi
.Ltmp233:
	.cv_inline_site_id 258 within 256 inlined_at 2 880 0
	.cv_inline_site_id 259 within 258 inlined_at 4 462 0
	.cv_inline_site_id 260 within 259 inlined_at 4 344 0
	.cv_inline_site_id 261 within 260 inlined_at 4 229 0
	.cv_inline_site_id 262 within 261 inlined_at 4 128 0
	.cv_inline_site_id 263 within 262 inlined_at 5 463 0
	.cv_inline_site_id 264 within 263 inlined_at 3 195 0
	.cv_loc	264 3 85 0
	callq	*__imp_GetProcessHeap(%rip)
.Ltmp234:
	.cv_loc	263 3 199 0
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	callq	*__imp_HeapFree(%rip)
	nop
.Ltmp235:
.LBB9_25:
	.cv_loc	222 30 650 0
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.Ltmp236:
.Lfunc_end9:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner,unique,9
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner,unique,2
	.p2align	2, 0x0
$cppxdata$_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner@IMGREL
	.long	72
	.long	0
	.long	1
$stateUnwindMap$_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner:
	.long	-1
	.long	"?dtor$23@?0?_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner@4HA"@IMGREL
$ip2state$_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner:
	.long	.Lfunc_begin9@IMGREL
	.long	-1
	.long	.Ltmp196@IMGREL
	.long	0
	.long	.Ltmp199@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner,unique,9

	.def	_RNvXsK_NtCs8xEFJqa6dYS_4core3fmtNtB5_5ErrorNtB5_5Debug3fmt;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXsK_NtCs8xEFJqa6dYS_4core3fmtNtB5_5ErrorNtB5_5Debug3fmt,unique,10
	.p2align	4
_RNvXsK_NtCs8xEFJqa6dYS_4core3fmtNtB5_5ErrorNtB5_5Debug3fmt:
.Lfunc_begin10:
	.cv_func_id 265
	.cv_inline_site_id 266 within 265 inlined_at 31 110 0
	.cv_loc	266 31 2100 0
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.cf47210967777a51b7227f8e6911a3b4.50(%rip), %rdx
	movl	$5, %r8d
	rex64 jmpq	*%rax
.Ltmp237:
.Lfunc_end10:

	.def	_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write10write_char;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write10write_char,unique,11
	.p2align	4
_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write10write_char:
.Lfunc_begin11:
	.cv_func_id 267
	.cv_loc	267 10 3377 0
.seh_proc _RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write10write_char
	pushq	%rbp
	.seh_pushreg %rbp
.Ltmp238:
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
	.cv_inline_site_id 268 within 267 inlined_at 10 3378 0
	.cv_inline_site_id 269 within 268 inlined_at 10 1422 0
	.cv_inline_site_id 270 within 269 inlined_at 10 1866 0
	.cv_loc	270 11 3064 0
	movq	16(%rcx), %rsi
	movl	$1, %edi
.Ltmp239:
	.cv_inline_site_id 271 within 268 inlined_at 10 1423 0
	.cv_inline_site_id 272 within 271 inlined_at 15 662 0
	.cv_loc	272 15 2451 0
	cmpl	$128, %edx
	jb	.LBB11_3
	.cv_loc	272 15 2452 0
	movl	$2, %edi
	cmpl	$2048, %edx
	jb	.LBB11_3
	.cv_loc	272 15 2453 0
	cmpl	$65536, %edx
	movl	$4, %edi
	sbbq	$0, %rdi
.Ltmp240:
.LBB11_3:
	.cv_inline_site_id 273 within 268 inlined_at 10 1424 0
	.cv_inline_site_id 274 within 273 inlined_at 10 1225 0
	.cv_inline_site_id 275 within 274 inlined_at 11 1469 0
	.cv_inline_site_id 276 within 275 inlined_at 2 341 0
	.cv_inline_site_id 277 within 276 inlined_at 2 674 0
	.cv_inline_site_id 278 within 277 inlined_at 2 768 0
	.cv_loc	278 2 620 0
	movq	(%rcx), %rax
.Ltmp241:
	.cv_loc	278 6 2649 0
	subq	%rsi, %rax
.Ltmp242:
	.cv_loc	277 2 768 0
	cmpq	%rax, %rdi
.Ltmp243:
	.cv_loc	276 2 674 0
	ja	.LBB11_4
.Ltmp244:
	.cv_inline_site_id 279 within 268 inlined_at 10 1428 0
	.cv_inline_site_id 280 within 279 inlined_at 11 2061 0
	.cv_inline_site_id 281 within 280 inlined_at 2 296 0
	.cv_inline_site_id 282 within 281 inlined_at 2 610 0
	.cv_loc	282 2 615 0
	movq	8(%rcx), %rax
.Ltmp245:
	.cv_loc	272 15 2451 0
	cmpl	$128, %edx
.Ltmp246:
	.cv_inline_site_id 283 within 268 inlined_at 10 1428 0
	.cv_inline_site_id 284 within 283 inlined_at 15 2518 0
	.cv_loc	284 15 2451 0
	jae	.LBB11_6
.Ltmp247:
.LBB11_12:
	.cv_loc	283 15 2523 0
	movb	%dl, (%rax,%rsi)
	.cv_loc	283 24 1 0
	jmp	.LBB11_11
.Ltmp248:
.LBB11_4:
	.cv_loc	276 2 676 0
	movq	%rcx, %rbx
	movl	%edx, %r14d
.Ltmp249:
	movq	%rsi, %rdx
	movq	%rdi, %r8
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalEBa_
	movl	%r14d, %edx
	movq	%rbx, %rcx
.Ltmp250:
	.cv_loc	282 2 615 0
	movq	8(%rcx), %rax
.Ltmp251:
	.cv_loc	272 15 2451 0
	cmpl	$128, %edx
.Ltmp252:
	.cv_loc	284 15 2451 0
	jb	.LBB11_12
.Ltmp253:
.LBB11_6:
	.cv_loc	283 15 2527 0
	movl	%edx, %r8d
	andb	$63, %r8b
	orb	$-128, %r8b
.Ltmp254:
	.cv_loc	283 15 2528 0
	movl	%edx, %r9d
	shrl	$6, %r9d
.Ltmp255:
	.cv_loc	284 15 2452 0
	cmpl	$2048, %edx
.Ltmp256:
	.cv_loc	283 15 2532 0
	jae	.LBB11_8
	.cv_loc	283 15 2533 0
	orb	$-64, %r9b
	movb	%r9b, (%rax,%rsi)
	.cv_loc	283 15 2534 0
	movb	%r8b, 1(%rax,%rsi)
	.cv_loc	283 24 1 0
	jmp	.LBB11_11
.LBB11_8:
	.cv_loc	283 15 2538 0
	andb	$63, %r9b
	orb	$-128, %r9b
	movl	%edx, %r10d
	shrl	$12, %r10d
	cmpl	$65535, %edx
	ja	.LBB11_10
	.cv_loc	283 15 2539 0
	orb	$-32, %r10b
	movb	%r10b, (%rax,%rsi)
	.cv_loc	283 15 2540 0
	movb	%r9b, 1(%rax,%rsi)
	.cv_loc	283 15 2541 0
	movb	%r8b, 2(%rax,%rsi)
	.cv_loc	283 24 1 0
	jmp	.LBB11_11
.LBB11_10:
	.cv_loc	283 15 2545 0
	andb	$63, %r10b
	orb	$-128, %r10b
	shrl	$18, %edx
	orb	$-16, %dl
	movb	%dl, (%rax,%rsi)
	.cv_loc	283 15 2546 0
	movb	%r10b, 1(%rax,%rsi)
	.cv_loc	283 15 2547 0
	movb	%r9b, 2(%rax,%rsi)
	.cv_loc	283 15 2548 0
	movb	%r8b, 3(%rax,%rsi)
.Ltmp257:
.LBB11_11:
	.cv_loc	268 10 1429 0
	addq	%rsi, %rdi
.Ltmp258:
	.cv_inline_site_id 285 within 268 inlined_at 10 1429 0
	.cv_loc	285 11 2231 0
	movq	%rdi, 16(%rcx)
.Ltmp259:
	.cv_loc	267 10 3380 0
	xorl	%eax, %eax
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.Ltmp260:
.Lfunc_end11:
	.seh_endproc

	.def	_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_str;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_str,unique,12
	.p2align	4
_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_str:
.Lfunc_begin12:
	.cv_func_id 286
	.cv_loc	286 10 3371 0
.seh_proc _RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_str
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
	movq	%r8, %rsi
	movq	%rcx, %rdi
.Ltmp261:
	.cv_inline_site_id 287 within 286 inlined_at 10 3372 0
	.cv_inline_site_id 288 within 287 inlined_at 10 1107 0
	.cv_inline_site_id 289 within 288 inlined_at 11 3567 0
	.cv_inline_site_id 290 within 289 inlined_at 27 56 0
	.cv_inline_site_id 291 within 290 inlined_at 11 2942 0
	.cv_inline_site_id 292 within 291 inlined_at 11 1469 0
	.cv_inline_site_id 293 within 292 inlined_at 2 341 0
	.cv_inline_site_id 294 within 293 inlined_at 2 674 0
	.cv_inline_site_id 295 within 294 inlined_at 2 768 0
	.cv_loc	295 2 620 0
	movq	(%rcx), %rax
.Ltmp262:
	.cv_loc	291 11 1469 0
	movq	16(%rcx), %rbx
.Ltmp263:
	.cv_loc	295 6 2649 0
	subq	%rbx, %rax
.Ltmp264:
	.cv_loc	294 2 768 0
	cmpq	%rax, %r8
.Ltmp265:
	.cv_loc	293 2 674 0
	ja	.LBB12_1
.Ltmp266:
	.cv_loc	290 11 2944 0
	testq	%rsi, %rsi
	je	.LBB12_4
.LBB12_3:
	.cv_inline_site_id 296 within 290 inlined_at 11 2946 0
	.cv_loc	296 12 970 0
	movq	8(%rdi), %rcx
.Ltmp267:
	addq	%rbx, %rcx
.Ltmp268:
	.cv_loc	296 1 549 0
	movq	%rsi, %r8
	callq	memcpy
.Ltmp269:
.LBB12_4:
	.cv_loc	290 11 2949 0
	addq	%rsi, %rbx
	movq	%rbx, 16(%rdi)
.Ltmp270:
	.cv_loc	286 10 3374 0
	xorl	%eax, %eax
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.LBB12_1:
.Ltmp271:
	.cv_loc	293 2 676 0
	movq	%rdi, %rcx
	movq	%rdx, %r14
	movq	%rbx, %rdx
	movq	%rsi, %r8
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalEBa_
	movq	%r14, %rdx
.Ltmp272:
	.cv_inline_site_id 297 within 290 inlined_at 11 2943 0
	.cv_loc	297 11 3064 0
	movq	16(%rdi), %rbx
.Ltmp273:
	.cv_loc	290 11 2944 0
	jmp	.LBB12_3
.Ltmp274:
.Lfunc_end12:
	.seh_endproc

	.def	_RNvYNtNtCsfQUUnEvlYZE_5alloc6string6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_fmtB6_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvYNtNtCsfQUUnEvlYZE_5alloc6string6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_fmtB6_,unique,13
	.p2align	4
_RNvYNtNtCsfQUUnEvlYZE_5alloc6string6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_fmtB6_:
.Lfunc_begin13:
	.cv_func_id 298
	.cv_loc	298 31 214 0
	.cv_inline_site_id 299 within 298 inlined_at 31 243 0
	.cv_loc	299 31 238 0
	movq	%r8, %r9
	movq	%rdx, %r8
.Ltmp275:
	leaq	anon.cf47210967777a51b7227f8e6911a3b4.34(%rip), %rdx
	jmp	_RNvNtCs8xEFJqa6dYS_4core3fmt5write
.Ltmp276:
.Lfunc_end13:

	.section	.rdata,"dr",one_only,anon.cf47210967777a51b7227f8e6911a3b4.6,unique,14
	.p2align	3, 0x0
anon.cf47210967777a51b7227f8e6911a3b4.6:
	.asciz	"\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\001\000\000\000\000\000\000"
	.quad	_RNvXsK_NtCs8xEFJqa6dYS_4core3fmtNtB5_5ErrorNtB5_5Debug3fmt

	.section	.rdata,"dr",one_only,anon.cf47210967777a51b7227f8e6911a3b4.14,unique,15
anon.cf47210967777a51b7227f8e6911a3b4.14:
	.asciz	"/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\alloc\\src\\raw_vec\\mod.rs"

	.section	.rdata,"dr",one_only,anon.cf47210967777a51b7227f8e6911a3b4.27,unique,16
anon.cf47210967777a51b7227f8e6911a3b4.27:
	.ascii	"capacity overflow"

	.section	.rdata,"dr",one_only,anon.cf47210967777a51b7227f8e6911a3b4.28,unique,17
	.p2align	3, 0x0
anon.cf47210967777a51b7227f8e6911a3b4.28:
	.quad	anon.cf47210967777a51b7227f8e6911a3b4.14
	.asciz	"P\000\000\000\000\000\000\000\034\000\000\000\005\000\000"

	.section	.rdata,"dr",one_only,anon.cf47210967777a51b7227f8e6911a3b4.34,unique,18
	.p2align	3, 0x0
anon.cf47210967777a51b7227f8e6911a3b4.34:
	.quad	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsfQUUnEvlYZE_5alloc6string6StringEBF_
	.asciz	"\030\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_str
	.quad	_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write10write_char
	.quad	_RNvYNtNtCsfQUUnEvlYZE_5alloc6string6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_fmtB6_

	.section	.rdata,"dr",one_only,anon.cf47210967777a51b7227f8e6911a3b4.35,unique,19
anon.cf47210967777a51b7227f8e6911a3b4.35:
	.ascii	"a formatting trait implementation returned an error when the underlying stream did not"

	.section	.rdata,"dr",one_only,anon.cf47210967777a51b7227f8e6911a3b4.36,unique,20
anon.cf47210967777a51b7227f8e6911a3b4.36:
	.asciz	"/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\alloc\\src\\fmt.rs"

	.section	.rdata,"dr",one_only,anon.cf47210967777a51b7227f8e6911a3b4.37,unique,21
	.p2align	3, 0x0
anon.cf47210967777a51b7227f8e6911a3b4.37:
	.quad	anon.cf47210967777a51b7227f8e6911a3b4.36
	.asciz	"H\000\000\000\000\000\000\000\217\002\000\000\016\000\000"

	.section	.rdata,"dr",one_only,anon.cf47210967777a51b7227f8e6911a3b4.50,unique,22
anon.cf47210967777a51b7227f8e6911a3b4.50:
	.ascii	"Error"

	.section	.debug$S,"dr"
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp278-.Ltmp277
.Ltmp277:
	.short	.Ltmp280-.Ltmp279
.Ltmp279:
	.short	4353
	.long	0
	.asciz	"prototype.alloc-e70c1e2d2d692bb9.alloc.b8a7db27d8b7bce8-cgu.0.rcgu.o.rcgu.o"
	.p2align	2, 0x0
.Ltmp280:
	.short	.Ltmp282-.Ltmp281
.Ltmp281:
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
.Ltmp282:
.Ltmp278:
	.p2align	2, 0x0
	.long	246
	.long	.Ltmp284-.Ltmp283
.Ltmp283:
	.long	0


	.long	4099
	.cv_filechecksumoffset	1
	.long	823


	.long	4099
	.cv_filechecksumoffset	1
	.long	823


	.long	4101
	.cv_filechecksumoffset	2
	.long	423


	.long	4103
	.cv_filechecksumoffset	2
	.long	876


	.long	4104
	.cv_filechecksumoffset	2
	.long	634


	.long	4106
	.cv_filechecksumoffset	4
	.long	460


	.long	4108
	.cv_filechecksumoffset	4
	.long	343


	.long	4109
	.cv_filechecksumoffset	4
	.long	219


	.long	4111
	.cv_filechecksumoffset	4
	.long	127


	.long	4113
	.cv_filechecksumoffset	5
	.long	460


	.long	4115
	.cv_filechecksumoffset	3
	.long	180


	.long	4117
	.cv_filechecksumoffset	3
	.long	83


	.long	4118
	.cv_filechecksumoffset	2
	.long	503


	.long	4120
	.cv_filechecksumoffset	6
	.long	890


	.long	4122
	.cv_filechecksumoffset	7
	.long	458


	.long	4124
	.cv_filechecksumoffset	8
	.long	1681


	.long	4126
	.cv_filechecksumoffset	8
	.long	1034


	.long	4128
	.cv_filechecksumoffset	9
	.long	2175


	.long	4129
	.cv_filechecksumoffset	2
	.long	773


	.long	4131
	.cv_filechecksumoffset	10
	.long	493


	.long	4133
	.cv_filechecksumoffset	11
	.long	521


	.long	4134
	.cv_filechecksumoffset	11
	.long	974


	.long	4136
	.cv_filechecksumoffset	2
	.long	175


	.long	4137
	.cv_filechecksumoffset	2
	.long	434


	.long	4138
	.cv_filechecksumoffset	2
	.long	447


	.long	4139
	.cv_filechecksumoffset	4
	.long	448


	.long	4140
	.cv_filechecksumoffset	4
	.long	331


	.long	4141
	.cv_filechecksumoffset	4
	.long	205


	.long	4142
	.cv_filechecksumoffset	4
	.long	95


	.long	4143
	.cv_filechecksumoffset	5
	.long	450


	.long	4144
	.cv_filechecksumoffset	3
	.long	166


	.long	4145
	.cv_filechecksumoffset	3
	.long	112


	.long	4147
	.cv_filechecksumoffset	13
	.long	1043


	.long	4149
	.cv_filechecksumoffset	14
	.long	94


	.long	4151
	.cv_filechecksumoffset	12
	.long	936


	.long	4152
	.cv_filechecksumoffset	10
	.long	1421


	.long	4154
	.cv_filechecksumoffset	15
	.long	2517


	.long	4155
	.cv_filechecksumoffset	11
	.long	2224


	.long	4157
	.cv_filechecksumoffset	17
	.long	43


	.long	4159
	.cv_filechecksumoffset	18
	.long	40


	.long	4161
	.cv_filechecksumoffset	19
	.long	157


	.long	4163
	.cv_filechecksumoffset	16
	.long	1649


	.long	4165
	.cv_filechecksumoffset	16
	.long	606


	.long	4167
	.cv_filechecksumoffset	21
	.long	2160


	.long	4168
	.cv_filechecksumoffset	21
	.long	1158


	.long	4170
	.cv_filechecksumoffset	22
	.long	250


	.long	4172
	.cv_filechecksumoffset	20
	.long	715


	.long	4174
	.cv_filechecksumoffset	23
	.long	1281


	.long	4176
	.cv_filechecksumoffset	15
	.long	661


	.long	4177
	.cv_filechecksumoffset	15
	.long	2449


	.long	4178
	.cv_filechecksumoffset	10
	.long	1224


	.long	4179
	.cv_filechecksumoffset	11
	.long	1468


	.long	4180
	.cv_filechecksumoffset	2
	.long	339


	.long	4181
	.cv_filechecksumoffset	2
	.long	656


	.long	4182
	.cv_filechecksumoffset	2
	.long	767


	.long	4183
	.cv_filechecksumoffset	2
	.long	619


	.long	4177
	.cv_filechecksumoffset	15
	.long	2449


	.long	4184
	.cv_filechecksumoffset	11
	.long	2058


	.long	4185
	.cv_filechecksumoffset	2
	.long	295


	.long	4186
	.cv_filechecksumoffset	2
	.long	609


	.long	4187
	.cv_filechecksumoffset	2
	.long	614


	.long	4099
	.cv_filechecksumoffset	1
	.long	823


	.long	4189
	.cv_filechecksumoffset	25
	.long	55


	.long	4191
	.cv_filechecksumoffset	25
	.long	175


	.long	4193
	.cv_filechecksumoffset	11
	.long	3796


	.long	4194
	.cv_filechecksumoffset	11
	.long	1856


	.long	4196
	.cv_filechecksumoffset	26
	.long	290


	.long	4161
	.cv_filechecksumoffset	19
	.long	157


	.long	4163
	.cv_filechecksumoffset	16
	.long	1649


	.long	4165
	.cv_filechecksumoffset	16
	.long	606


	.long	4197
	.cv_filechecksumoffset	25
	.long	101


	.long	4133
	.cv_filechecksumoffset	11
	.long	521


	.long	4134
	.cv_filechecksumoffset	11
	.long	974


	.long	4136
	.cv_filechecksumoffset	2
	.long	175


	.long	4147
	.cv_filechecksumoffset	13
	.long	1043


	.long	4149
	.cv_filechecksumoffset	14
	.long	94


	.long	4151
	.cv_filechecksumoffset	12
	.long	936


	.long	4198
	.cv_filechecksumoffset	25
	.long	312


	.long	4199
	.cv_filechecksumoffset	25
	.long	168


	.long	4200
	.cv_filechecksumoffset	15
	.long	2480


	.long	4177
	.cv_filechecksumoffset	15
	.long	2449


	.long	4201
	.cv_filechecksumoffset	11
	.long	3566


	.long	4203
	.cv_filechecksumoffset	27
	.long	54


	.long	4204
	.cv_filechecksumoffset	11
	.long	2940


	.long	4151
	.cv_filechecksumoffset	12
	.long	936


	.long	4184
	.cv_filechecksumoffset	11
	.long	2058


	.long	4185
	.cv_filechecksumoffset	2
	.long	295


	.long	4186
	.cv_filechecksumoffset	2
	.long	609


	.long	4187
	.cv_filechecksumoffset	2
	.long	614


	.long	4205
	.cv_filechecksumoffset	11
	.long	3063


	.long	4099
	.cv_filechecksumoffset	1
	.long	823


	.long	4207
	.cv_filechecksumoffset	2
	.long	900


	.long	4209
	.cv_filechecksumoffset	28
	.long	526


	.long	4210
	.cv_filechecksumoffset	28
	.long	109


	.long	4211
	.cv_filechecksumoffset	28
	.long	74


	.long	4212
	.cv_filechecksumoffset	4
	.long	467


	.long	4213
	.cv_filechecksumoffset	4
	.long	355


	.long	4214
	.cv_filechecksumoffset	4
	.long	236


	.long	4215
	.cv_filechecksumoffset	4
	.long	154


	.long	4216
	.cv_filechecksumoffset	5
	.long	467


	.long	4217
	.cv_filechecksumoffset	3
	.long	203


	.long	4219
	.cv_filechecksumoffset	4
	.long	549


	.long	4221
	.cv_filechecksumoffset	29
	.long	89


	.long	4223
	.cv_filechecksumoffset	29
	.long	133


	.long	4225
	.cv_filechecksumoffset	31
	.long	754


	.long	4226
	.cv_filechecksumoffset	31
	.long	871


	.long	4227
	.cv_filechecksumoffset	16
	.long	918


	.long	4228
	.cv_filechecksumoffset	1
	.long	1692


	.long	4165
	.cv_filechecksumoffset	16
	.long	606


	.long	4227
	.cv_filechecksumoffset	16
	.long	918


	.long	4228
	.cv_filechecksumoffset	1
	.long	1692


	.long	4131
	.cv_filechecksumoffset	10
	.long	493


	.long	4133
	.cv_filechecksumoffset	11
	.long	521


	.long	4134
	.cv_filechecksumoffset	11
	.long	974


	.long	4136
	.cv_filechecksumoffset	2
	.long	175


	.long	4207
	.cv_filechecksumoffset	2
	.long	900


	.long	4209
	.cv_filechecksumoffset	28
	.long	526


	.long	4210
	.cv_filechecksumoffset	28
	.long	109


	.long	4230
	.cv_filechecksumoffset	31
	.long	214


	.long	4232
	.cv_filechecksumoffset	31
	.long	234


	.long	4234
	.cv_filechecksumoffset	9
	.long	1177


	.long	4236
	.cv_filechecksumoffset	31
	.long	2099


	.long	4237
	.cv_filechecksumoffset	10
	.long	1865


	.long	4205
	.cv_filechecksumoffset	11
	.long	3063


	.long	4238
	.cv_filechecksumoffset	10
	.long	1106


	.long	4201
	.cv_filechecksumoffset	11
	.long	3566


	.long	4203
	.cv_filechecksumoffset	27
	.long	54


	.long	4232
	.cv_filechecksumoffset	31
	.long	234
.Ltmp284:
	.p2align	2, 0x0
	.section	.debug$S,"dr",associative,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsfQUUnEvlYZE_5alloc6string6StringEBF_
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp286-.Ltmp285
.Ltmp285:
	.short	.Ltmp288-.Ltmp287
.Ltmp287:
	.short	4422
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end0-_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsfQUUnEvlYZE_5alloc6string6StringEBF_
	.long	0
	.long	0
	.long	4099
	.secrel32	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsfQUUnEvlYZE_5alloc6string6StringEBF_
	.secidx	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsfQUUnEvlYZE_5alloc6string6StringEBF_
	.byte	129
	.asciz	"core::ptr::drop_glue<alloc::string::String>"
	.p2align	2, 0x0
.Ltmp288:
	.short	.Ltmp290-.Ltmp289
.Ltmp289:
	.short	4114
	.long	48
	.long	0
	.long	0
	.long	8
	.long	0
	.short	0
	.long	1220624
	.p2align	2, 0x0
.Ltmp290:
	.short	.Ltmp292-.Ltmp291
.Ltmp291:
	.short	4456
	.long	1
	.long	4099
	.p2align	2, 0x0
.Ltmp292:
	.short	.Ltmp294-.Ltmp293
.Ltmp293:
	.short	4429
	.long	0
	.long	0
	.long	4099
	.cv_inline_linetable	1 1 823 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp294:
	.short	.Ltmp296-.Ltmp295
.Ltmp295:
	.short	4429
	.long	0
	.long	0
	.long	4099
	.cv_inline_linetable	2 1 823 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp296:
	.short	.Ltmp298-.Ltmp297
.Ltmp297:
	.short	4429
	.long	0
	.long	0
	.long	4101
	.cv_inline_linetable	3 2 423 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp298:
	.short	.Ltmp300-.Ltmp299
.Ltmp299:
	.short	4429
	.long	0
	.long	0
	.long	4103
	.cv_inline_linetable	4 2 876 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp300:
	.short	.Ltmp302-.Ltmp301
.Ltmp301:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	5 2 634 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp302:
	.short	2
	.short	4430
	.short	.Ltmp304-.Ltmp303
.Ltmp303:
	.short	4429
	.long	0
	.long	0
	.long	4106
	.cv_inline_linetable	6 4 460 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp304:
	.short	.Ltmp306-.Ltmp305
.Ltmp305:
	.short	4429
	.long	0
	.long	0
	.long	4108
	.cv_inline_linetable	7 4 343 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp306:
	.short	.Ltmp308-.Ltmp307
.Ltmp307:
	.short	4429
	.long	0
	.long	0
	.long	4109
	.cv_inline_linetable	8 4 219 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp308:
	.short	.Ltmp310-.Ltmp309
.Ltmp309:
	.short	4429
	.long	0
	.long	0
	.long	4111
	.cv_inline_linetable	9 4 127 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp310:
	.short	.Ltmp312-.Ltmp311
.Ltmp311:
	.short	4429
	.long	0
	.long	0
	.long	4113
	.cv_inline_linetable	10 5 460 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp312:
	.short	.Ltmp314-.Ltmp313
.Ltmp313:
	.short	4429
	.long	0
	.long	0
	.long	4115
	.cv_inline_linetable	11 3 180 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp314:
	.short	.Ltmp316-.Ltmp315
.Ltmp315:
	.short	4429
	.long	0
	.long	0
	.long	4117
	.cv_inline_linetable	12 3 83 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp316:
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
	.short	4430
	.short	2
	.short	4431
.Ltmp286:
	.p2align	2, 0x0
	.cv_linetable	0, _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCsfQUUnEvlYZE_5alloc6string6StringEBF_, .Lfunc_end0
	.section	.debug$S,"dr",associative,_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalEBa_
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp318-.Ltmp317
.Ltmp317:
	.short	.Ltmp320-.Ltmp319
.Ltmp319:
	.short	4422
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end1-_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalEBa_
	.long	0
	.long	0
	.long	4240
	.secrel32	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalEBa_
	.secidx	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalEBa_
	.byte	129
	.asciz	"alloc::raw_vec::impl$4::reserve::do_reserve_and_handle<alloc::alloc::Global>"
	.p2align	2, 0x0
.Ltmp320:
	.short	.Ltmp322-.Ltmp321
.Ltmp321:
	.short	4114
	.long	72
	.long	0
	.long	0
	.long	16
	.long	0
	.short	0
	.long	1220624
	.p2align	2, 0x0
.Ltmp322:
	.short	.Ltmp324-.Ltmp323
.Ltmp323:
	.short	4456
	.long	1
	.long	4118
	.p2align	2, 0x0
.Ltmp324:
	.short	.Ltmp326-.Ltmp325
.Ltmp325:
	.short	4429
	.long	0
	.long	0
	.long	4118
	.cv_inline_linetable	14 2 503 .Lfunc_begin1 .Lfunc_end1
	.p2align	2, 0x0
.Ltmp326:
	.short	.Ltmp328-.Ltmp327
.Ltmp327:
	.short	4429
	.long	0
	.long	0
	.long	4120
	.cv_inline_linetable	15 6 890 .Lfunc_begin1 .Lfunc_end1
	.p2align	2, 0x0
.Ltmp328:
	.short	.Ltmp330-.Ltmp329
.Ltmp329:
	.short	4429
	.long	0
	.long	0
	.long	4122
	.cv_inline_linetable	16 7 458 .Lfunc_begin1 .Lfunc_end1
	.p2align	2, 0x0
.Ltmp330:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp332-.Ltmp331
.Ltmp331:
	.short	4429
	.long	0
	.long	0
	.long	4124
	.cv_inline_linetable	17 8 1681 .Lfunc_begin1 .Lfunc_end1
	.p2align	2, 0x0
.Ltmp332:
	.short	.Ltmp334-.Ltmp333
.Ltmp333:
	.short	4429
	.long	0
	.long	0
	.long	4126
	.cv_inline_linetable	18 8 1034 .Lfunc_begin1 .Lfunc_end1
	.p2align	2, 0x0
.Ltmp334:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp336-.Ltmp335
.Ltmp335:
	.short	4429
	.long	0
	.long	0
	.long	4124
	.cv_inline_linetable	19 8 1681 .Lfunc_begin1 .Lfunc_end1
	.p2align	2, 0x0
.Ltmp336:
	.short	.Ltmp338-.Ltmp337
.Ltmp337:
	.short	4429
	.long	0
	.long	0
	.long	4126
	.cv_inline_linetable	20 8 1034 .Lfunc_begin1 .Lfunc_end1
	.p2align	2, 0x0
.Ltmp338:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp340-.Ltmp339
.Ltmp339:
	.short	4429
	.long	0
	.long	0
	.long	4128
	.cv_inline_linetable	21 9 2175 .Lfunc_begin1 .Lfunc_end1
	.p2align	2, 0x0
.Ltmp340:
	.short	2
	.short	4430
	.short	.Ltmp342-.Ltmp341
.Ltmp341:
	.short	4429
	.long	0
	.long	0
	.long	4129
	.cv_inline_linetable	22 2 773 .Lfunc_begin1 .Lfunc_end1
	.p2align	2, 0x0
.Ltmp342:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4431
.Ltmp318:
	.p2align	2, 0x0
	.cv_linetable	13, _RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalEBa_, .Lfunc_end1
	.section	.debug$S,"dr",associative,_RNvMNtCsfQUUnEvlYZE_5alloc6stringNtB2_6String10from_utf16
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp344-.Ltmp343
.Ltmp343:
	.short	.Ltmp346-.Ltmp345
.Ltmp345:
	.short	4423
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end2-_RNvMNtCsfQUUnEvlYZE_5alloc6stringNtB2_6String10from_utf16
	.long	0
	.long	0
	.long	4241
	.secrel32	_RNvMNtCsfQUUnEvlYZE_5alloc6stringNtB2_6String10from_utf16
	.secidx	_RNvMNtCsfQUUnEvlYZE_5alloc6stringNtB2_6String10from_utf16
	.byte	129
	.asciz	"alloc::string::String::from_utf16"
	.p2align	2, 0x0
.Ltmp346:
	.short	.Ltmp348-.Ltmp347
.Ltmp347:
	.short	4114
	.long	80
	.long	0
	.long	0
	.long	56
	.long	0
	.short	0
	.long	1220624
	.p2align	2, 0x0
.Ltmp348:
	.short	.Ltmp350-.Ltmp349
.Ltmp349:
	.short	4456
	.long	5
	.long	4099
	.long	4131
	.long	4147
	.long	4152
	.long	4157
	.p2align	2, 0x0
.Ltmp350:
	.short	.Ltmp352-.Ltmp351
.Ltmp351:
	.short	4429
	.long	0
	.long	0
	.long	4131
	.cv_inline_linetable	24 10 493 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp352:
	.short	.Ltmp354-.Ltmp353
.Ltmp353:
	.short	4429
	.long	0
	.long	0
	.long	4133
	.cv_inline_linetable	25 11 521 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp354:
	.short	.Ltmp356-.Ltmp355
.Ltmp355:
	.short	4429
	.long	0
	.long	0
	.long	4134
	.cv_inline_linetable	26 11 974 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp356:
	.short	.Ltmp358-.Ltmp357
.Ltmp357:
	.short	4429
	.long	0
	.long	0
	.long	4136
	.cv_inline_linetable	27 2 175 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp358:
	.short	.Ltmp360-.Ltmp359
.Ltmp359:
	.short	4429
	.long	0
	.long	0
	.long	4137
	.cv_inline_linetable	28 2 434 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp360:
	.short	.Ltmp362-.Ltmp361
.Ltmp361:
	.short	4429
	.long	0
	.long	0
	.long	4138
	.cv_inline_linetable	29 2 447 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp362:
	.short	.Ltmp364-.Ltmp363
.Ltmp363:
	.short	4429
	.long	0
	.long	0
	.long	4139
	.cv_inline_linetable	30 4 448 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp364:
	.short	.Ltmp366-.Ltmp365
.Ltmp365:
	.short	4429
	.long	0
	.long	0
	.long	4140
	.cv_inline_linetable	31 4 331 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp366:
	.short	.Ltmp368-.Ltmp367
.Ltmp367:
	.short	4429
	.long	0
	.long	0
	.long	4141
	.cv_inline_linetable	32 4 205 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp368:
	.short	.Ltmp370-.Ltmp369
.Ltmp369:
	.short	4429
	.long	0
	.long	0
	.long	4142
	.cv_inline_linetable	33 4 95 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp370:
	.short	.Ltmp372-.Ltmp371
.Ltmp371:
	.short	4429
	.long	0
	.long	0
	.long	4143
	.cv_inline_linetable	34 5 450 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp372:
	.short	.Ltmp374-.Ltmp373
.Ltmp373:
	.short	4429
	.long	0
	.long	0
	.long	4144
	.cv_inline_linetable	35 3 166 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp374:
	.short	.Ltmp376-.Ltmp375
.Ltmp375:
	.short	4429
	.long	0
	.long	0
	.long	4145
	.cv_inline_linetable	36 3 112 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp376:
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
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp378-.Ltmp377
.Ltmp377:
	.short	4429
	.long	0
	.long	0
	.long	4147
	.cv_inline_linetable	37 13 1043 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp378:
	.short	.Ltmp380-.Ltmp379
.Ltmp379:
	.short	4429
	.long	0
	.long	0
	.long	4149
	.cv_inline_linetable	38 14 94 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp380:
	.short	.Ltmp382-.Ltmp381
.Ltmp381:
	.short	4429
	.long	0
	.long	0
	.long	4151
	.cv_inline_linetable	39 12 936 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp382:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp384-.Ltmp383
.Ltmp383:
	.short	4429
	.long	0
	.long	0
	.long	4152
	.cv_inline_linetable	40 10 1421 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp384:
	.short	.Ltmp386-.Ltmp385
.Ltmp385:
	.short	4429
	.long	0
	.long	0
	.long	4154
	.cv_inline_linetable	41 15 2517 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp386:
	.short	.Ltmp388-.Ltmp387
.Ltmp387:
	.short	4429
	.long	0
	.long	0
	.long	4177
	.cv_inline_linetable	68 15 2449 .Lfunc_begin2 .Lfunc_end2
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
	.long	4155
	.cv_inline_linetable	42 11 2224 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp390:
	.short	2
	.short	4430
	.short	.Ltmp392-.Ltmp391
.Ltmp391:
	.short	4429
	.long	0
	.long	0
	.long	4176
	.cv_inline_linetable	60 15 661 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp392:
	.short	.Ltmp394-.Ltmp393
.Ltmp393:
	.short	4429
	.long	0
	.long	0
	.long	4177
	.cv_inline_linetable	61 15 2449 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp394:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp396-.Ltmp395
.Ltmp395:
	.short	4429
	.long	0
	.long	0
	.long	4178
	.cv_inline_linetable	62 10 1224 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp396:
	.short	.Ltmp398-.Ltmp397
.Ltmp397:
	.short	4429
	.long	0
	.long	0
	.long	4179
	.cv_inline_linetable	63 11 1468 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp398:
	.short	.Ltmp400-.Ltmp399
.Ltmp399:
	.short	4429
	.long	0
	.long	0
	.long	4180
	.cv_inline_linetable	64 2 339 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp400:
	.short	.Ltmp402-.Ltmp401
.Ltmp401:
	.short	4429
	.long	0
	.long	0
	.long	4181
	.cv_inline_linetable	65 2 656 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp402:
	.short	.Ltmp404-.Ltmp403
.Ltmp403:
	.short	4429
	.long	0
	.long	0
	.long	4182
	.cv_inline_linetable	66 2 767 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp404:
	.short	.Ltmp406-.Ltmp405
.Ltmp405:
	.short	4429
	.long	0
	.long	0
	.long	4183
	.cv_inline_linetable	67 2 619 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp406:
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
	.short	4430
	.short	.Ltmp408-.Ltmp407
.Ltmp407:
	.short	4429
	.long	0
	.long	0
	.long	4184
	.cv_inline_linetable	69 11 2058 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp408:
	.short	.Ltmp410-.Ltmp409
.Ltmp409:
	.short	4429
	.long	0
	.long	0
	.long	4185
	.cv_inline_linetable	70 2 295 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp410:
	.short	.Ltmp412-.Ltmp411
.Ltmp411:
	.short	4429
	.long	0
	.long	0
	.long	4186
	.cv_inline_linetable	71 2 609 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp412:
	.short	.Ltmp414-.Ltmp413
.Ltmp413:
	.short	4429
	.long	0
	.long	0
	.long	4187
	.cv_inline_linetable	72 2 614 .Lfunc_begin2 .Lfunc_end2
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
	.short	.Ltmp416-.Ltmp415
.Ltmp415:
	.short	4429
	.long	0
	.long	0
	.long	4157
	.cv_inline_linetable	43 17 43 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp416:
	.short	.Ltmp418-.Ltmp417
.Ltmp417:
	.short	4429
	.long	0
	.long	0
	.long	4159
	.cv_inline_linetable	44 18 40 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp418:
	.short	.Ltmp420-.Ltmp419
.Ltmp419:
	.short	4429
	.long	0
	.long	0
	.long	4161
	.cv_inline_linetable	45 19 157 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp420:
	.short	.Ltmp422-.Ltmp421
.Ltmp421:
	.short	4429
	.long	0
	.long	0
	.long	4163
	.cv_inline_linetable	46 16 1649 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp422:
	.short	2
	.short	4430
	.short	.Ltmp424-.Ltmp423
.Ltmp423:
	.short	4429
	.long	0
	.long	0
	.long	4165
	.cv_inline_linetable	47 16 606 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp424:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp426-.Ltmp425
.Ltmp425:
	.short	4429
	.long	0
	.long	0
	.long	4167
	.cv_inline_linetable	48 21 2160 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp426:
	.short	.Ltmp428-.Ltmp427
.Ltmp427:
	.short	4429
	.long	0
	.long	0
	.long	4168
	.cv_inline_linetable	49 21 1158 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp428:
	.short	.Ltmp430-.Ltmp429
.Ltmp429:
	.short	4429
	.long	0
	.long	0
	.long	4170
	.cv_inline_linetable	50 22 250 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp430:
	.short	.Ltmp432-.Ltmp431
.Ltmp431:
	.short	4429
	.long	0
	.long	0
	.long	4172
	.cv_inline_linetable	51 20 715 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp432:
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
	.short	.Ltmp434-.Ltmp433
.Ltmp433:
	.short	4429
	.long	0
	.long	0
	.long	4174
	.cv_inline_linetable	52 23 1281 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp434:
	.short	2
	.short	4430
	.short	.Ltmp436-.Ltmp435
.Ltmp435:
	.short	4429
	.long	0
	.long	0
	.long	4159
	.cv_inline_linetable	53 18 40 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp436:
	.short	.Ltmp438-.Ltmp437
.Ltmp437:
	.short	4429
	.long	0
	.long	0
	.long	4167
	.cv_inline_linetable	54 21 2160 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp438:
	.short	.Ltmp440-.Ltmp439
.Ltmp439:
	.short	4429
	.long	0
	.long	0
	.long	4168
	.cv_inline_linetable	55 21 1158 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp440:
	.short	.Ltmp442-.Ltmp441
.Ltmp441:
	.short	4429
	.long	0
	.long	0
	.long	4170
	.cv_inline_linetable	56 22 250 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp442:
	.short	.Ltmp444-.Ltmp443
.Ltmp443:
	.short	4429
	.long	0
	.long	0
	.long	4172
	.cv_inline_linetable	57 20 715 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp444:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp446-.Ltmp445
.Ltmp445:
	.short	4429
	.long	0
	.long	0
	.long	4161
	.cv_inline_linetable	58 19 157 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp446:
	.short	.Ltmp448-.Ltmp447
.Ltmp447:
	.short	4429
	.long	0
	.long	0
	.long	4165
	.cv_inline_linetable	59 16 606 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp448:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp450-.Ltmp449
.Ltmp449:
	.short	4429
	.long	0
	.long	0
	.long	4099
	.cv_inline_linetable	73 1 823 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp450:
	.short	.Ltmp452-.Ltmp451
.Ltmp451:
	.short	4429
	.long	0
	.long	0
	.long	4099
	.cv_inline_linetable	74 1 823 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp452:
	.short	.Ltmp454-.Ltmp453
.Ltmp453:
	.short	4429
	.long	0
	.long	0
	.long	4099
	.cv_inline_linetable	75 1 823 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp454:
	.short	.Ltmp456-.Ltmp455
.Ltmp455:
	.short	4429
	.long	0
	.long	0
	.long	4101
	.cv_inline_linetable	76 2 423 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp456:
	.short	.Ltmp458-.Ltmp457
.Ltmp457:
	.short	4429
	.long	0
	.long	0
	.long	4103
	.cv_inline_linetable	77 2 876 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp458:
	.short	.Ltmp460-.Ltmp459
.Ltmp459:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	78 2 634 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp460:
	.short	2
	.short	4430
	.short	.Ltmp462-.Ltmp461
.Ltmp461:
	.short	4429
	.long	0
	.long	0
	.long	4106
	.cv_inline_linetable	79 4 460 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp462:
	.short	.Ltmp464-.Ltmp463
.Ltmp463:
	.short	4429
	.long	0
	.long	0
	.long	4108
	.cv_inline_linetable	80 4 343 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp464:
	.short	.Ltmp466-.Ltmp465
.Ltmp465:
	.short	4429
	.long	0
	.long	0
	.long	4109
	.cv_inline_linetable	81 4 219 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp466:
	.short	.Ltmp468-.Ltmp467
.Ltmp467:
	.short	4429
	.long	0
	.long	0
	.long	4111
	.cv_inline_linetable	82 4 127 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp468:
	.short	.Ltmp470-.Ltmp469
.Ltmp469:
	.short	4429
	.long	0
	.long	0
	.long	4113
	.cv_inline_linetable	83 5 460 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp470:
	.short	.Ltmp472-.Ltmp471
.Ltmp471:
	.short	4429
	.long	0
	.long	0
	.long	4115
	.cv_inline_linetable	84 3 180 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp472:
	.short	.Ltmp474-.Ltmp473
.Ltmp473:
	.short	4429
	.long	0
	.long	0
	.long	4117
	.cv_inline_linetable	85 3 83 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp474:
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
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp476-.Ltmp475
.Ltmp475:
	.short	4429
	.long	0
	.long	0
	.long	4099
	.cv_inline_linetable	86 1 823 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp476:
	.short	.Ltmp478-.Ltmp477
.Ltmp477:
	.short	4429
	.long	0
	.long	0
	.long	4099
	.cv_inline_linetable	87 1 823 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp478:
	.short	.Ltmp480-.Ltmp479
.Ltmp479:
	.short	4429
	.long	0
	.long	0
	.long	4099
	.cv_inline_linetable	88 1 823 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp480:
	.short	.Ltmp482-.Ltmp481
.Ltmp481:
	.short	4429
	.long	0
	.long	0
	.long	4101
	.cv_inline_linetable	89 2 423 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp482:
	.short	.Ltmp484-.Ltmp483
.Ltmp483:
	.short	4429
	.long	0
	.long	0
	.long	4103
	.cv_inline_linetable	90 2 876 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp484:
	.short	.Ltmp486-.Ltmp485
.Ltmp485:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	91 2 634 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp486:
	.short	2
	.short	4430
	.short	.Ltmp488-.Ltmp487
.Ltmp487:
	.short	4429
	.long	0
	.long	0
	.long	4106
	.cv_inline_linetable	92 4 460 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp488:
	.short	.Ltmp490-.Ltmp489
.Ltmp489:
	.short	4429
	.long	0
	.long	0
	.long	4108
	.cv_inline_linetable	93 4 343 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp490:
	.short	.Ltmp492-.Ltmp491
.Ltmp491:
	.short	4429
	.long	0
	.long	0
	.long	4109
	.cv_inline_linetable	94 4 219 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp492:
	.short	.Ltmp494-.Ltmp493
.Ltmp493:
	.short	4429
	.long	0
	.long	0
	.long	4111
	.cv_inline_linetable	95 4 127 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp494:
	.short	.Ltmp496-.Ltmp495
.Ltmp495:
	.short	4429
	.long	0
	.long	0
	.long	4113
	.cv_inline_linetable	96 5 460 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp496:
	.short	.Ltmp498-.Ltmp497
.Ltmp497:
	.short	4429
	.long	0
	.long	0
	.long	4115
	.cv_inline_linetable	97 3 180 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp498:
	.short	.Ltmp500-.Ltmp499
.Ltmp499:
	.short	4429
	.long	0
	.long	0
	.long	4117
	.cv_inline_linetable	98 3 83 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp500:
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
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4431
.Ltmp344:
	.p2align	2, 0x0
	.cv_linetable	23, _RNvMNtCsfQUUnEvlYZE_5alloc6stringNtB2_6String10from_utf16, .Lfunc_end2
	.section	.debug$S,"dr",associative,_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf11into_string
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp502-.Ltmp501
.Ltmp501:
	.short	.Ltmp504-.Ltmp503
.Ltmp503:
	.short	4423
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end3-_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf11into_string
	.long	0
	.long	0
	.long	4242
	.secrel32	_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf11into_string
	.secidx	_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf11into_string
	.byte	128
	.asciz	"alloc::wtf8::Wtf8Buf::into_string"
	.p2align	2, 0x0
.Ltmp504:
	.short	.Ltmp506-.Ltmp505
.Ltmp505:
	.short	4114
	.long	0
	.long	0
	.long	0
	.long	0
	.long	0
	.short	0
	.long	1056784
	.p2align	2, 0x0
.Ltmp506:
	.short	.Ltmp508-.Ltmp507
.Ltmp507:
	.short	4456
	.long	2
	.long	4189
	.long	4196
	.p2align	2, 0x0
.Ltmp508:
	.short	.Ltmp510-.Ltmp509
.Ltmp509:
	.short	4429
	.long	0
	.long	0
	.long	4189
	.cv_inline_linetable	100 25 55 .Lfunc_begin3 .Lfunc_end3
	.p2align	2, 0x0
.Ltmp510:
	.short	.Ltmp512-.Ltmp511
.Ltmp511:
	.short	4429
	.long	0
	.long	0
	.long	4191
	.cv_inline_linetable	101 25 175 .Lfunc_begin3 .Lfunc_end3
	.p2align	2, 0x0
.Ltmp512:
	.short	.Ltmp514-.Ltmp513
.Ltmp513:
	.short	4429
	.long	0
	.long	0
	.long	4193
	.cv_inline_linetable	102 11 3796 .Lfunc_begin3 .Lfunc_end3
	.p2align	2, 0x0
.Ltmp514:
	.short	.Ltmp516-.Ltmp515
.Ltmp515:
	.short	4429
	.long	0
	.long	0
	.long	4194
	.cv_inline_linetable	103 11 1856 .Lfunc_begin3 .Lfunc_end3
	.p2align	2, 0x0
.Ltmp516:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp518-.Ltmp517
.Ltmp517:
	.short	4429
	.long	0
	.long	0
	.long	4196
	.cv_inline_linetable	104 26 290 .Lfunc_begin3 .Lfunc_end3
	.p2align	2, 0x0
.Ltmp518:
	.short	.Ltmp520-.Ltmp519
.Ltmp519:
	.short	4429
	.long	0
	.long	0
	.long	4161
	.cv_inline_linetable	105 19 157 .Lfunc_begin3 .Lfunc_end3
	.p2align	2, 0x0
.Ltmp520:
	.short	.Ltmp522-.Ltmp521
.Ltmp521:
	.short	4429
	.long	0
	.long	0
	.long	4163
	.cv_inline_linetable	106 16 1649 .Lfunc_begin3 .Lfunc_end3
	.p2align	2, 0x0
.Ltmp522:
	.short	2
	.short	4430
	.short	.Ltmp524-.Ltmp523
.Ltmp523:
	.short	4429
	.long	0
	.long	0
	.long	4165
	.cv_inline_linetable	109 16 606 .Lfunc_begin3 .Lfunc_end3
	.p2align	2, 0x0
.Ltmp524:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp526-.Ltmp525
.Ltmp525:
	.short	4429
	.long	0
	.long	0
	.long	4161
	.cv_inline_linetable	107 19 157 .Lfunc_begin3 .Lfunc_end3
	.p2align	2, 0x0
.Ltmp526:
	.short	.Ltmp528-.Ltmp527
.Ltmp527:
	.short	4429
	.long	0
	.long	0
	.long	4163
	.cv_inline_linetable	108 16 1649 .Lfunc_begin3 .Lfunc_end3
	.p2align	2, 0x0
.Ltmp528:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp530-.Ltmp529
.Ltmp529:
	.short	4429
	.long	0
	.long	0
	.long	4161
	.cv_inline_linetable	110 19 157 .Lfunc_begin3 .Lfunc_end3
	.p2align	2, 0x0
.Ltmp530:
	.short	.Ltmp532-.Ltmp531
.Ltmp531:
	.short	4429
	.long	0
	.long	0
	.long	4163
	.cv_inline_linetable	111 16 1649 .Lfunc_begin3 .Lfunc_end3
	.p2align	2, 0x0
.Ltmp532:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp534-.Ltmp533
.Ltmp533:
	.short	4429
	.long	0
	.long	0
	.long	4161
	.cv_inline_linetable	112 19 157 .Lfunc_begin3 .Lfunc_end3
	.p2align	2, 0x0
.Ltmp534:
	.short	.Ltmp536-.Ltmp535
.Ltmp535:
	.short	4429
	.long	0
	.long	0
	.long	4163
	.cv_inline_linetable	113 16 1649 .Lfunc_begin3 .Lfunc_end3
	.p2align	2, 0x0
.Ltmp536:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp538-.Ltmp537
.Ltmp537:
	.short	4429
	.long	0
	.long	0
	.long	4161
	.cv_inline_linetable	114 19 157 .Lfunc_begin3 .Lfunc_end3
	.p2align	2, 0x0
.Ltmp538:
	.short	.Ltmp540-.Ltmp539
.Ltmp539:
	.short	4429
	.long	0
	.long	0
	.long	4163
	.cv_inline_linetable	115 16 1649 .Lfunc_begin3 .Lfunc_end3
	.p2align	2, 0x0
.Ltmp540:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4431
.Ltmp502:
	.p2align	2, 0x0
	.cv_linetable	99, _RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf11into_string, .Lfunc_end3
	.section	.debug$S,"dr",associative,_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf9from_wide
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp542-.Ltmp541
.Ltmp541:
	.short	.Ltmp544-.Ltmp543
.Ltmp543:
	.short	4423
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end4-_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf9from_wide
	.long	0
	.long	0
	.long	4243
	.secrel32	_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf9from_wide
	.secidx	_RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf9from_wide
	.byte	129
	.asciz	"alloc::wtf8::Wtf8Buf::from_wide"
	.p2align	2, 0x0
.Ltmp544:
	.short	.Ltmp546-.Ltmp545
.Ltmp545:
	.short	4114
	.long	96
	.long	0
	.long	0
	.long	56
	.long	0
	.short	0
	.long	1220624
	.p2align	2, 0x0
.Ltmp546:
	.short	.Ltmp548-.Ltmp547
.Ltmp547:
	.short	4456
	.long	6
	.long	4099
	.long	4147
	.long	4157
	.long	4197
	.long	4198
	.long	4199
	.p2align	2, 0x0
.Ltmp548:
	.short	.Ltmp550-.Ltmp549
.Ltmp549:
	.short	4429
	.long	0
	.long	0
	.long	4197
	.cv_inline_linetable	117 25 101 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp550:
	.short	.Ltmp552-.Ltmp551
.Ltmp551:
	.short	4429
	.long	0
	.long	0
	.long	4133
	.cv_inline_linetable	118 11 521 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp552:
	.short	.Ltmp554-.Ltmp553
.Ltmp553:
	.short	4429
	.long	0
	.long	0
	.long	4134
	.cv_inline_linetable	119 11 974 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp554:
	.short	.Ltmp556-.Ltmp555
.Ltmp555:
	.short	4429
	.long	0
	.long	0
	.long	4136
	.cv_inline_linetable	120 2 175 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp556:
	.short	.Ltmp558-.Ltmp557
.Ltmp557:
	.short	4429
	.long	0
	.long	0
	.long	4137
	.cv_inline_linetable	121 2 434 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp558:
	.short	.Ltmp560-.Ltmp559
.Ltmp559:
	.short	4429
	.long	0
	.long	0
	.long	4138
	.cv_inline_linetable	122 2 447 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp560:
	.short	.Ltmp562-.Ltmp561
.Ltmp561:
	.short	4429
	.long	0
	.long	0
	.long	4139
	.cv_inline_linetable	123 4 448 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp562:
	.short	.Ltmp564-.Ltmp563
.Ltmp563:
	.short	4429
	.long	0
	.long	0
	.long	4140
	.cv_inline_linetable	124 4 331 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp564:
	.short	.Ltmp566-.Ltmp565
.Ltmp565:
	.short	4429
	.long	0
	.long	0
	.long	4141
	.cv_inline_linetable	125 4 205 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp566:
	.short	.Ltmp568-.Ltmp567
.Ltmp567:
	.short	4429
	.long	0
	.long	0
	.long	4142
	.cv_inline_linetable	126 4 95 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp568:
	.short	.Ltmp570-.Ltmp569
.Ltmp569:
	.short	4429
	.long	0
	.long	0
	.long	4143
	.cv_inline_linetable	127 5 450 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp570:
	.short	.Ltmp572-.Ltmp571
.Ltmp571:
	.short	4429
	.long	0
	.long	0
	.long	4144
	.cv_inline_linetable	128 3 166 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp572:
	.short	.Ltmp574-.Ltmp573
.Ltmp573:
	.short	4429
	.long	0
	.long	0
	.long	4145
	.cv_inline_linetable	129 3 112 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp574:
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
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp576-.Ltmp575
.Ltmp575:
	.short	4429
	.long	0
	.long	0
	.long	4147
	.cv_inline_linetable	130 13 1043 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp576:
	.short	.Ltmp578-.Ltmp577
.Ltmp577:
	.short	4429
	.long	0
	.long	0
	.long	4149
	.cv_inline_linetable	131 14 94 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp578:
	.short	.Ltmp580-.Ltmp579
.Ltmp579:
	.short	4429
	.long	0
	.long	0
	.long	4151
	.cv_inline_linetable	132 12 936 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp580:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp582-.Ltmp581
.Ltmp581:
	.short	4429
	.long	0
	.long	0
	.long	4157
	.cv_inline_linetable	133 17 43 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp582:
	.short	.Ltmp584-.Ltmp583
.Ltmp583:
	.short	4429
	.long	0
	.long	0
	.long	4159
	.cv_inline_linetable	134 18 40 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp584:
	.short	.Ltmp586-.Ltmp585
.Ltmp585:
	.short	4429
	.long	0
	.long	0
	.long	4161
	.cv_inline_linetable	135 19 157 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp586:
	.short	.Ltmp588-.Ltmp587
.Ltmp587:
	.short	4429
	.long	0
	.long	0
	.long	4163
	.cv_inline_linetable	136 16 1649 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp588:
	.short	2
	.short	4430
	.short	.Ltmp590-.Ltmp589
.Ltmp589:
	.short	4429
	.long	0
	.long	0
	.long	4165
	.cv_inline_linetable	141 16 606 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp590:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp592-.Ltmp591
.Ltmp591:
	.short	4429
	.long	0
	.long	0
	.long	4167
	.cv_inline_linetable	137 21 2160 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp592:
	.short	.Ltmp594-.Ltmp593
.Ltmp593:
	.short	4429
	.long	0
	.long	0
	.long	4168
	.cv_inline_linetable	138 21 1158 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp594:
	.short	.Ltmp596-.Ltmp595
.Ltmp595:
	.short	4429
	.long	0
	.long	0
	.long	4170
	.cv_inline_linetable	139 22 250 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp596:
	.short	.Ltmp598-.Ltmp597
.Ltmp597:
	.short	4429
	.long	0
	.long	0
	.long	4172
	.cv_inline_linetable	140 20 715 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp598:
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
	.short	.Ltmp600-.Ltmp599
.Ltmp599:
	.short	4429
	.long	0
	.long	0
	.long	4174
	.cv_inline_linetable	142 23 1281 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp600:
	.short	2
	.short	4430
	.short	.Ltmp602-.Ltmp601
.Ltmp601:
	.short	4429
	.long	0
	.long	0
	.long	4159
	.cv_inline_linetable	143 18 40 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp602:
	.short	.Ltmp604-.Ltmp603
.Ltmp603:
	.short	4429
	.long	0
	.long	0
	.long	4161
	.cv_inline_linetable	144 19 157 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp604:
	.short	.Ltmp606-.Ltmp605
.Ltmp605:
	.short	4429
	.long	0
	.long	0
	.long	4163
	.cv_inline_linetable	145 16 1649 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp606:
	.short	2
	.short	4430
	.short	.Ltmp608-.Ltmp607
.Ltmp607:
	.short	4429
	.long	0
	.long	0
	.long	4165
	.cv_inline_linetable	150 16 606 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp608:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp610-.Ltmp609
.Ltmp609:
	.short	4429
	.long	0
	.long	0
	.long	4167
	.cv_inline_linetable	146 21 2160 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp610:
	.short	.Ltmp612-.Ltmp611
.Ltmp611:
	.short	4429
	.long	0
	.long	0
	.long	4168
	.cv_inline_linetable	147 21 1158 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp612:
	.short	.Ltmp614-.Ltmp613
.Ltmp613:
	.short	4429
	.long	0
	.long	0
	.long	4170
	.cv_inline_linetable	148 22 250 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp614:
	.short	.Ltmp616-.Ltmp615
.Ltmp615:
	.short	4429
	.long	0
	.long	0
	.long	4172
	.cv_inline_linetable	149 20 715 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp616:
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
	.short	4430
	.short	.Ltmp618-.Ltmp617
.Ltmp617:
	.short	4429
	.long	0
	.long	0
	.long	4198
	.cv_inline_linetable	151 25 312 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp618:
	.short	.Ltmp620-.Ltmp619
.Ltmp619:
	.short	4429
	.long	0
	.long	0
	.long	4199
	.cv_inline_linetable	152 25 168 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp620:
	.short	.Ltmp622-.Ltmp621
.Ltmp621:
	.short	4429
	.long	0
	.long	0
	.long	4200
	.cv_inline_linetable	153 15 2480 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp622:
	.short	.Ltmp624-.Ltmp623
.Ltmp623:
	.short	4429
	.long	0
	.long	0
	.long	4177
	.cv_inline_linetable	154 15 2449 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp624:
	.short	2
	.short	4430
	.short	.Ltmp626-.Ltmp625
.Ltmp625:
	.short	4429
	.long	0
	.long	0
	.long	4154
	.cv_inline_linetable	155 15 2517 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp626:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp628-.Ltmp627
.Ltmp627:
	.short	4429
	.long	0
	.long	0
	.long	4201
	.cv_inline_linetable	156 11 3566 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp628:
	.short	.Ltmp630-.Ltmp629
.Ltmp629:
	.short	4429
	.long	0
	.long	0
	.long	4203
	.cv_inline_linetable	157 27 54 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp630:
	.short	.Ltmp632-.Ltmp631
.Ltmp631:
	.short	4429
	.long	0
	.long	0
	.long	4204
	.cv_inline_linetable	158 11 2940 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp632:
	.short	.Ltmp634-.Ltmp633
.Ltmp633:
	.short	4429
	.long	0
	.long	0
	.long	4179
	.cv_inline_linetable	159 11 1468 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp634:
	.short	.Ltmp636-.Ltmp635
.Ltmp635:
	.short	4429
	.long	0
	.long	0
	.long	4180
	.cv_inline_linetable	160 2 339 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp636:
	.short	.Ltmp638-.Ltmp637
.Ltmp637:
	.short	4429
	.long	0
	.long	0
	.long	4181
	.cv_inline_linetable	161 2 656 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp638:
	.short	.Ltmp640-.Ltmp639
.Ltmp639:
	.short	4429
	.long	0
	.long	0
	.long	4182
	.cv_inline_linetable	162 2 767 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp640:
	.short	.Ltmp642-.Ltmp641
.Ltmp641:
	.short	4429
	.long	0
	.long	0
	.long	4183
	.cv_inline_linetable	163 2 619 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp642:
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
	.short	.Ltmp644-.Ltmp643
.Ltmp643:
	.short	4429
	.long	0
	.long	0
	.long	4151
	.cv_inline_linetable	164 12 936 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp644:
	.short	.Ltmp646-.Ltmp645
.Ltmp645:
	.short	4429
	.long	0
	.long	0
	.long	4185
	.cv_inline_linetable	178 2 295 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp646:
	.short	.Ltmp648-.Ltmp647
.Ltmp647:
	.short	4429
	.long	0
	.long	0
	.long	4186
	.cv_inline_linetable	179 2 609 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp648:
	.short	.Ltmp650-.Ltmp649
.Ltmp649:
	.short	4429
	.long	0
	.long	0
	.long	4187
	.cv_inline_linetable	180 2 614 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp650:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp652-.Ltmp651
.Ltmp651:
	.short	4429
	.long	0
	.long	0
	.long	4205
	.cv_inline_linetable	181 11 3063 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp652:
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
	.short	4430
	.short	.Ltmp654-.Ltmp653
.Ltmp653:
	.short	4429
	.long	0
	.long	0
	.long	4199
	.cv_inline_linetable	165 25 168 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp654:
	.short	.Ltmp656-.Ltmp655
.Ltmp655:
	.short	4429
	.long	0
	.long	0
	.long	4201
	.cv_inline_linetable	166 11 3566 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp656:
	.short	.Ltmp658-.Ltmp657
.Ltmp657:
	.short	4429
	.long	0
	.long	0
	.long	4203
	.cv_inline_linetable	167 27 54 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp658:
	.short	.Ltmp660-.Ltmp659
.Ltmp659:
	.short	4429
	.long	0
	.long	0
	.long	4204
	.cv_inline_linetable	168 11 2940 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp660:
	.short	.Ltmp662-.Ltmp661
.Ltmp661:
	.short	4429
	.long	0
	.long	0
	.long	4179
	.cv_inline_linetable	169 11 1468 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp662:
	.short	.Ltmp664-.Ltmp663
.Ltmp663:
	.short	4429
	.long	0
	.long	0
	.long	4180
	.cv_inline_linetable	170 2 339 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp664:
	.short	.Ltmp666-.Ltmp665
.Ltmp665:
	.short	4429
	.long	0
	.long	0
	.long	4181
	.cv_inline_linetable	171 2 656 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp666:
	.short	.Ltmp668-.Ltmp667
.Ltmp667:
	.short	4429
	.long	0
	.long	0
	.long	4182
	.cv_inline_linetable	172 2 767 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp668:
	.short	.Ltmp670-.Ltmp669
.Ltmp669:
	.short	4429
	.long	0
	.long	0
	.long	4183
	.cv_inline_linetable	173 2 619 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp670:
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
	.short	.Ltmp672-.Ltmp671
.Ltmp671:
	.short	4429
	.long	0
	.long	0
	.long	4184
	.cv_inline_linetable	174 11 2058 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp672:
	.short	.Ltmp674-.Ltmp673
.Ltmp673:
	.short	4429
	.long	0
	.long	0
	.long	4185
	.cv_inline_linetable	175 2 295 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp674:
	.short	.Ltmp676-.Ltmp675
.Ltmp675:
	.short	4429
	.long	0
	.long	0
	.long	4186
	.cv_inline_linetable	176 2 609 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp676:
	.short	.Ltmp678-.Ltmp677
.Ltmp677:
	.short	4429
	.long	0
	.long	0
	.long	4187
	.cv_inline_linetable	177 2 614 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp678:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp680-.Ltmp679
.Ltmp679:
	.short	4429
	.long	0
	.long	0
	.long	4205
	.cv_inline_linetable	182 11 3063 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp680:
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
	.short	.Ltmp682-.Ltmp681
.Ltmp681:
	.short	4429
	.long	0
	.long	0
	.long	4099
	.cv_inline_linetable	183 1 823 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp682:
	.short	.Ltmp684-.Ltmp683
.Ltmp683:
	.short	4429
	.long	0
	.long	0
	.long	4099
	.cv_inline_linetable	184 1 823 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp684:
	.short	.Ltmp686-.Ltmp685
.Ltmp685:
	.short	4429
	.long	0
	.long	0
	.long	4099
	.cv_inline_linetable	185 1 823 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp686:
	.short	.Ltmp688-.Ltmp687
.Ltmp687:
	.short	4429
	.long	0
	.long	0
	.long	4101
	.cv_inline_linetable	186 2 423 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp688:
	.short	.Ltmp690-.Ltmp689
.Ltmp689:
	.short	4429
	.long	0
	.long	0
	.long	4103
	.cv_inline_linetable	187 2 876 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp690:
	.short	.Ltmp692-.Ltmp691
.Ltmp691:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	188 2 634 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp692:
	.short	2
	.short	4430
	.short	.Ltmp694-.Ltmp693
.Ltmp693:
	.short	4429
	.long	0
	.long	0
	.long	4106
	.cv_inline_linetable	189 4 460 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp694:
	.short	.Ltmp696-.Ltmp695
.Ltmp695:
	.short	4429
	.long	0
	.long	0
	.long	4108
	.cv_inline_linetable	190 4 343 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp696:
	.short	.Ltmp698-.Ltmp697
.Ltmp697:
	.short	4429
	.long	0
	.long	0
	.long	4109
	.cv_inline_linetable	191 4 219 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp698:
	.short	.Ltmp700-.Ltmp699
.Ltmp699:
	.short	4429
	.long	0
	.long	0
	.long	4111
	.cv_inline_linetable	192 4 127 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp700:
	.short	.Ltmp702-.Ltmp701
.Ltmp701:
	.short	4429
	.long	0
	.long	0
	.long	4113
	.cv_inline_linetable	193 5 460 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp702:
	.short	.Ltmp704-.Ltmp703
.Ltmp703:
	.short	4429
	.long	0
	.long	0
	.long	4115
	.cv_inline_linetable	194 3 180 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp704:
	.short	.Ltmp706-.Ltmp705
.Ltmp705:
	.short	4429
	.long	0
	.long	0
	.long	4117
	.cv_inline_linetable	195 3 83 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp706:
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
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4431
.Ltmp542:
	.p2align	2, 0x0
	.cv_linetable	116, _RNvMs2_NtCsfQUUnEvlYZE_5alloc4wtf8NtB5_7Wtf8Buf9from_wide, .Lfunc_end4
	.section	.debug$S,"dr",associative,_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growB7_
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp708-.Ltmp707
.Ltmp707:
	.short	.Ltmp710-.Ltmp709
.Ltmp709:
	.short	4422
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end5-_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growB7_
	.long	0
	.long	0
	.long	4244
	.secrel32	_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growB7_
	.secidx	_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growB7_
	.byte	129
	.asciz	"alloc::raw_vec::RawVecInner::finish_grow<alloc::alloc::Global>"
	.p2align	2, 0x0
.Ltmp710:
	.short	.Ltmp712-.Ltmp711
.Ltmp711:
	.short	4114
	.long	40
	.long	0
	.long	0
	.long	32
	.long	0
	.short	0
	.long	1220624
	.p2align	2, 0x0
.Ltmp712:
	.short	.Ltmp714-.Ltmp713
.Ltmp713:
	.short	4456
	.long	4
	.long	4104
	.long	4139
	.long	4207
	.long	4212
	.p2align	2, 0x0
.Ltmp714:
	.short	.Ltmp716-.Ltmp715
.Ltmp715:
	.short	4429
	.long	0
	.long	0
	.long	4207
	.cv_inline_linetable	197 2 900 .Lfunc_begin5 .Lfunc_end5
	.p2align	2, 0x0
.Ltmp716:
	.short	.Ltmp718-.Ltmp717
.Ltmp717:
	.short	4429
	.long	0
	.long	0
	.long	4209
	.cv_inline_linetable	198 28 526 .Lfunc_begin5 .Lfunc_end5
	.p2align	2, 0x0
.Ltmp718:
	.short	.Ltmp720-.Ltmp719
.Ltmp719:
	.short	4429
	.long	0
	.long	0
	.long	4210
	.cv_inline_linetable	199 28 109 .Lfunc_begin5 .Lfunc_end5
	.p2align	2, 0x0
.Ltmp720:
	.short	.Ltmp722-.Ltmp721
.Ltmp721:
	.short	4429
	.long	0
	.long	0
	.long	4211
	.cv_inline_linetable	200 28 74 .Lfunc_begin5 .Lfunc_end5
	.p2align	2, 0x0
.Ltmp722:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp724-.Ltmp723
.Ltmp723:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	201 2 634 .Lfunc_begin5 .Lfunc_end5
	.p2align	2, 0x0
.Ltmp724:
	.short	2
	.short	4430
	.short	.Ltmp726-.Ltmp725
.Ltmp725:
	.short	4429
	.long	0
	.long	0
	.long	4212
	.cv_inline_linetable	202 4 467 .Lfunc_begin5 .Lfunc_end5
	.p2align	2, 0x0
.Ltmp726:
	.short	.Ltmp728-.Ltmp727
.Ltmp727:
	.short	4429
	.long	0
	.long	0
	.long	4213
	.cv_inline_linetable	203 4 355 .Lfunc_begin5 .Lfunc_end5
	.p2align	2, 0x0
.Ltmp728:
	.short	.Ltmp730-.Ltmp729
.Ltmp729:
	.short	4429
	.long	0
	.long	0
	.long	4214
	.cv_inline_linetable	204 4 236 .Lfunc_begin5 .Lfunc_end5
	.p2align	2, 0x0
.Ltmp730:
	.short	.Ltmp732-.Ltmp731
.Ltmp731:
	.short	4429
	.long	0
	.long	0
	.long	4215
	.cv_inline_linetable	205 4 154 .Lfunc_begin5 .Lfunc_end5
	.p2align	2, 0x0
.Ltmp732:
	.short	.Ltmp734-.Ltmp733
.Ltmp733:
	.short	4429
	.long	0
	.long	0
	.long	4216
	.cv_inline_linetable	206 5 467 .Lfunc_begin5 .Lfunc_end5
	.p2align	2, 0x0
.Ltmp734:
	.short	.Ltmp736-.Ltmp735
.Ltmp735:
	.short	4429
	.long	0
	.long	0
	.long	4217
	.cv_inline_linetable	207 3 203 .Lfunc_begin5 .Lfunc_end5
	.p2align	2, 0x0
.Ltmp736:
	.short	.Ltmp738-.Ltmp737
.Ltmp737:
	.short	4429
	.long	0
	.long	0
	.long	4117
	.cv_inline_linetable	208 3 83 .Lfunc_begin5 .Lfunc_end5
	.p2align	2, 0x0
.Ltmp738:
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
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp740-.Ltmp739
.Ltmp739:
	.short	4429
	.long	0
	.long	0
	.long	4139
	.cv_inline_linetable	209 4 448 .Lfunc_begin5 .Lfunc_end5
	.p2align	2, 0x0
.Ltmp740:
	.short	.Ltmp742-.Ltmp741
.Ltmp741:
	.short	4429
	.long	0
	.long	0
	.long	4140
	.cv_inline_linetable	210 4 331 .Lfunc_begin5 .Lfunc_end5
	.p2align	2, 0x0
.Ltmp742:
	.short	.Ltmp744-.Ltmp743
.Ltmp743:
	.short	4429
	.long	0
	.long	0
	.long	4141
	.cv_inline_linetable	211 4 205 .Lfunc_begin5 .Lfunc_end5
	.p2align	2, 0x0
.Ltmp744:
	.short	.Ltmp746-.Ltmp745
.Ltmp745:
	.short	4429
	.long	0
	.long	0
	.long	4142
	.cv_inline_linetable	212 4 95 .Lfunc_begin5 .Lfunc_end5
	.p2align	2, 0x0
.Ltmp746:
	.short	.Ltmp748-.Ltmp747
.Ltmp747:
	.short	4429
	.long	0
	.long	0
	.long	4143
	.cv_inline_linetable	213 5 450 .Lfunc_begin5 .Lfunc_end5
	.p2align	2, 0x0
.Ltmp748:
	.short	.Ltmp750-.Ltmp749
.Ltmp749:
	.short	4429
	.long	0
	.long	0
	.long	4144
	.cv_inline_linetable	214 3 166 .Lfunc_begin5 .Lfunc_end5
	.p2align	2, 0x0
.Ltmp750:
	.short	.Ltmp752-.Ltmp751
.Ltmp751:
	.short	4429
	.long	0
	.long	0
	.long	4145
	.cv_inline_linetable	215 3 112 .Lfunc_begin5 .Lfunc_end5
	.p2align	2, 0x0
.Ltmp752:
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
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4431
.Ltmp708:
	.p2align	2, 0x0
	.cv_linetable	196, _RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growB7_, .Lfunc_end5
	.section	.debug$S,"dr",associative,_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp754-.Ltmp753
.Ltmp753:
	.short	.Ltmp756-.Ltmp755
.Ltmp755:
	.short	4423
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end6-_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	.long	0
	.long	0
	.long	4245
	.secrel32	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	.secidx	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	.byte	137
	.asciz	"alloc::alloc::handle_alloc_error"
	.p2align	2, 0x0
.Ltmp756:
	.short	.Ltmp758-.Ltmp757
.Ltmp757:
	.short	4114
	.long	40
	.long	0
	.long	0
	.long	0
	.long	0
	.short	0
	.long	172032
	.p2align	2, 0x0
.Ltmp758:
	.short	.Ltmp760-.Ltmp759
.Ltmp759:
	.short	4456
	.long	1
	.long	4219
	.p2align	2, 0x0
.Ltmp760:
	.short	.Ltmp762-.Ltmp761
.Ltmp761:
	.short	4429
	.long	0
	.long	0
	.long	4219
	.cv_inline_linetable	217 4 549 .Lfunc_begin6 .Lfunc_end6
	.p2align	2, 0x0
.Ltmp762:
	.short	2
	.short	4430
	.short	2
	.short	4431
.Ltmp754:
	.p2align	2, 0x0
	.cv_linetable	216, _RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error, .Lfunc_end6
	.section	.debug$S,"dr",associative,_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp764-.Ltmp763
.Ltmp763:
	.short	.Ltmp766-.Ltmp765
.Ltmp765:
	.short	4423
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end7-_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	.long	0
	.long	0
	.long	4246
	.secrel32	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	.secidx	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	.byte	137
	.asciz	"alloc::raw_vec::handle_error"
	.p2align	2, 0x0
.Ltmp766:
	.short	.Ltmp768-.Ltmp767
.Ltmp767:
	.short	4114
	.long	40
	.long	0
	.long	0
	.long	0
	.long	0
	.short	0
	.long	172032
	.p2align	2, 0x0
.Ltmp768:
	.short	.Ltmp770-.Ltmp769
.Ltmp769:
	.short	4456
	.long	1
	.long	4221
	.p2align	2, 0x0
.Ltmp770:
	.short	.Ltmp772-.Ltmp771
.Ltmp771:
	.short	4429
	.long	0
	.long	0
	.long	4221
	.cv_inline_linetable	219 29 89 .Lfunc_begin7 .Lfunc_end7
	.p2align	2, 0x0
.Ltmp772:
	.short	.Ltmp774-.Ltmp773
.Ltmp773:
	.short	4429
	.long	0
	.long	0
	.long	4223
	.cv_inline_linetable	220 29 133 .Lfunc_begin7 .Lfunc_end7
	.p2align	2, 0x0
.Ltmp774:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4431
.Ltmp764:
	.p2align	2, 0x0
	.cv_linetable	218, _RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error, .Lfunc_end7
	.section	.debug$S,"dr",associative,_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec17capacity_overflow
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp776-.Ltmp775
.Ltmp775:
	.short	.Ltmp778-.Ltmp777
.Ltmp777:
	.short	4423
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end8-_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec17capacity_overflow
	.long	0
	.long	0
	.long	4247
	.secrel32	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec17capacity_overflow
	.secidx	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec17capacity_overflow
	.byte	201
	.asciz	"alloc::raw_vec::capacity_overflow"
	.p2align	2, 0x0
.Ltmp778:
	.short	.Ltmp780-.Ltmp779
.Ltmp779:
	.short	4114
	.long	40
	.long	0
	.long	0
	.long	0
	.long	0
	.short	0
	.long	1220608
	.p2align	2, 0x0
.Ltmp780:
	.short	2
	.short	4431
.Ltmp776:
	.p2align	2, 0x0
	.cv_linetable	221, _RNvNtCsfQUUnEvlYZE_5alloc7raw_vec17capacity_overflow, .Lfunc_end8
	.section	.debug$S,"dr",associative,_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp782-.Ltmp781
.Ltmp781:
	.short	.Ltmp784-.Ltmp783
.Ltmp783:
	.short	4423
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end9-_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	.long	0
	.long	0
	.long	4249
	.secrel32	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	.secidx	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	.byte	129
	.asciz	"alloc::fmt::format::format_inner"
	.p2align	2, 0x0
.Ltmp784:
	.short	.Ltmp786-.Ltmp785
.Ltmp785:
	.short	4114
	.long	88
	.long	0
	.long	0
	.long	32
	.long	0
	.short	0
	.long	1220624
	.p2align	2, 0x0
.Ltmp786:
	.short	.Ltmp788-.Ltmp787
.Ltmp787:
	.short	4456
	.long	5
	.long	4099
	.long	4131
	.long	4225
	.long	4230
	.long	4234
	.p2align	2, 0x0
.Ltmp788:
	.short	.Ltmp790-.Ltmp789
.Ltmp789:
	.short	4429
	.long	0
	.long	0
	.long	4225
	.cv_inline_linetable	223 31 754 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp790:
	.short	.Ltmp792-.Ltmp791
.Ltmp791:
	.short	4429
	.long	0
	.long	0
	.long	4226
	.cv_inline_linetable	224 31 871 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp792:
	.short	2
	.short	4430
	.short	.Ltmp794-.Ltmp793
.Ltmp793:
	.short	4429
	.long	0
	.long	0
	.long	4227
	.cv_inline_linetable	225 16 918 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp794:
	.short	.Ltmp796-.Ltmp795
.Ltmp795:
	.short	4429
	.long	0
	.long	0
	.long	4228
	.cv_inline_linetable	226 1 1692 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp796:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp798-.Ltmp797
.Ltmp797:
	.short	4429
	.long	0
	.long	0
	.long	4165
	.cv_inline_linetable	227 16 606 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp798:
	.short	2
	.short	4430
	.short	.Ltmp800-.Ltmp799
.Ltmp799:
	.short	4429
	.long	0
	.long	0
	.long	4165
	.cv_inline_linetable	228 16 606 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp800:
	.short	2
	.short	4430
	.short	.Ltmp802-.Ltmp801
.Ltmp801:
	.short	4429
	.long	0
	.long	0
	.long	4227
	.cv_inline_linetable	229 16 918 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp802:
	.short	.Ltmp804-.Ltmp803
.Ltmp803:
	.short	4429
	.long	0
	.long	0
	.long	4228
	.cv_inline_linetable	230 1 1692 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp804:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp806-.Ltmp805
.Ltmp805:
	.short	4429
	.long	0
	.long	0
	.long	4165
	.cv_inline_linetable	231 16 606 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp806:
	.short	2
	.short	4430
	.short	.Ltmp808-.Ltmp807
.Ltmp807:
	.short	4429
	.long	0
	.long	0
	.long	4165
	.cv_inline_linetable	232 16 606 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp808:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp810-.Ltmp809
.Ltmp809:
	.short	4429
	.long	0
	.long	0
	.long	4131
	.cv_inline_linetable	233 10 493 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp810:
	.short	.Ltmp812-.Ltmp811
.Ltmp811:
	.short	4429
	.long	0
	.long	0
	.long	4133
	.cv_inline_linetable	234 11 521 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp812:
	.short	.Ltmp814-.Ltmp813
.Ltmp813:
	.short	4429
	.long	0
	.long	0
	.long	4134
	.cv_inline_linetable	235 11 974 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp814:
	.short	.Ltmp816-.Ltmp815
.Ltmp815:
	.short	4429
	.long	0
	.long	0
	.long	4136
	.cv_inline_linetable	236 2 175 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp816:
	.short	.Ltmp818-.Ltmp817
.Ltmp817:
	.short	4429
	.long	0
	.long	0
	.long	4137
	.cv_inline_linetable	237 2 434 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp818:
	.short	.Ltmp820-.Ltmp819
.Ltmp819:
	.short	4429
	.long	0
	.long	0
	.long	4138
	.cv_inline_linetable	238 2 447 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp820:
	.short	.Ltmp822-.Ltmp821
.Ltmp821:
	.short	4429
	.long	0
	.long	0
	.long	4207
	.cv_inline_linetable	239 2 900 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp822:
	.short	.Ltmp824-.Ltmp823
.Ltmp823:
	.short	4429
	.long	0
	.long	0
	.long	4209
	.cv_inline_linetable	240 28 526 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp824:
	.short	.Ltmp826-.Ltmp825
.Ltmp825:
	.short	4429
	.long	0
	.long	0
	.long	4210
	.cv_inline_linetable	241 28 109 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp826:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp828-.Ltmp827
.Ltmp827:
	.short	4429
	.long	0
	.long	0
	.long	4139
	.cv_inline_linetable	242 4 448 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp828:
	.short	.Ltmp830-.Ltmp829
.Ltmp829:
	.short	4429
	.long	0
	.long	0
	.long	4140
	.cv_inline_linetable	243 4 331 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp830:
	.short	.Ltmp832-.Ltmp831
.Ltmp831:
	.short	4429
	.long	0
	.long	0
	.long	4141
	.cv_inline_linetable	244 4 205 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp832:
	.short	.Ltmp834-.Ltmp833
.Ltmp833:
	.short	4429
	.long	0
	.long	0
	.long	4142
	.cv_inline_linetable	245 4 95 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp834:
	.short	.Ltmp836-.Ltmp835
.Ltmp835:
	.short	4429
	.long	0
	.long	0
	.long	4143
	.cv_inline_linetable	246 5 450 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp836:
	.short	.Ltmp838-.Ltmp837
.Ltmp837:
	.short	4429
	.long	0
	.long	0
	.long	4144
	.cv_inline_linetable	247 3 166 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp838:
	.short	.Ltmp840-.Ltmp839
.Ltmp839:
	.short	4429
	.long	0
	.long	0
	.long	4145
	.cv_inline_linetable	248 3 112 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp840:
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
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp842-.Ltmp841
.Ltmp841:
	.short	4429
	.long	0
	.long	0
	.long	4230
	.cv_inline_linetable	249 31 214 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp842:
	.short	.Ltmp844-.Ltmp843
.Ltmp843:
	.short	4429
	.long	0
	.long	0
	.long	4232
	.cv_inline_linetable	250 31 234 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp844:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp846-.Ltmp845
.Ltmp845:
	.short	4429
	.long	0
	.long	0
	.long	4234
	.cv_inline_linetable	251 9 1177 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp846:
	.short	2
	.short	4430
	.short	.Ltmp848-.Ltmp847
.Ltmp847:
	.short	4429
	.long	0
	.long	0
	.long	4099
	.cv_inline_linetable	252 1 823 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp848:
	.short	.Ltmp850-.Ltmp849
.Ltmp849:
	.short	4429
	.long	0
	.long	0
	.long	4099
	.cv_inline_linetable	253 1 823 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp850:
	.short	.Ltmp852-.Ltmp851
.Ltmp851:
	.short	4429
	.long	0
	.long	0
	.long	4099
	.cv_inline_linetable	254 1 823 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp852:
	.short	.Ltmp854-.Ltmp853
.Ltmp853:
	.short	4429
	.long	0
	.long	0
	.long	4101
	.cv_inline_linetable	255 2 423 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp854:
	.short	.Ltmp856-.Ltmp855
.Ltmp855:
	.short	4429
	.long	0
	.long	0
	.long	4103
	.cv_inline_linetable	256 2 876 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp856:
	.short	.Ltmp858-.Ltmp857
.Ltmp857:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	257 2 634 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp858:
	.short	2
	.short	4430
	.short	.Ltmp860-.Ltmp859
.Ltmp859:
	.short	4429
	.long	0
	.long	0
	.long	4106
	.cv_inline_linetable	258 4 460 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp860:
	.short	.Ltmp862-.Ltmp861
.Ltmp861:
	.short	4429
	.long	0
	.long	0
	.long	4108
	.cv_inline_linetable	259 4 343 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp862:
	.short	.Ltmp864-.Ltmp863
.Ltmp863:
	.short	4429
	.long	0
	.long	0
	.long	4109
	.cv_inline_linetable	260 4 219 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp864:
	.short	.Ltmp866-.Ltmp865
.Ltmp865:
	.short	4429
	.long	0
	.long	0
	.long	4111
	.cv_inline_linetable	261 4 127 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp866:
	.short	.Ltmp868-.Ltmp867
.Ltmp867:
	.short	4429
	.long	0
	.long	0
	.long	4113
	.cv_inline_linetable	262 5 460 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp868:
	.short	.Ltmp870-.Ltmp869
.Ltmp869:
	.short	4429
	.long	0
	.long	0
	.long	4115
	.cv_inline_linetable	263 3 180 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp870:
	.short	.Ltmp872-.Ltmp871
.Ltmp871:
	.short	4429
	.long	0
	.long	0
	.long	4117
	.cv_inline_linetable	264 3 83 .Lfunc_begin9 .Lfunc_end9
	.p2align	2, 0x0
.Ltmp872:
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
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4431
.Ltmp782:
	.p2align	2, 0x0
	.cv_linetable	222, _RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner, .Lfunc_end9
	.section	.debug$S,"dr",associative,_RNvXsK_NtCs8xEFJqa6dYS_4core3fmtNtB5_5ErrorNtB5_5Debug3fmt
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp874-.Ltmp873
.Ltmp873:
	.short	.Ltmp876-.Ltmp875
.Ltmp875:
	.short	4422
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end10-_RNvXsK_NtCs8xEFJqa6dYS_4core3fmtNtB5_5ErrorNtB5_5Debug3fmt
	.long	0
	.long	0
	.long	4251
	.secrel32	_RNvXsK_NtCs8xEFJqa6dYS_4core3fmtNtB5_5ErrorNtB5_5Debug3fmt
	.secidx	_RNvXsK_NtCs8xEFJqa6dYS_4core3fmtNtB5_5ErrorNtB5_5Debug3fmt
	.byte	128
	.asciz	"core::fmt::impl$48::fmt"
	.p2align	2, 0x0
.Ltmp876:
	.short	.Ltmp878-.Ltmp877
.Ltmp877:
	.short	4114
	.long	0
	.long	0
	.long	0
	.long	0
	.long	0
	.short	0
	.long	1056800
	.p2align	2, 0x0
.Ltmp878:
	.short	.Ltmp880-.Ltmp879
.Ltmp879:
	.short	4456
	.long	1
	.long	4236
	.p2align	2, 0x0
.Ltmp880:
	.short	.Ltmp882-.Ltmp881
.Ltmp881:
	.short	4429
	.long	0
	.long	0
	.long	4236
	.cv_inline_linetable	266 31 2099 .Lfunc_begin10 .Lfunc_end10
	.p2align	2, 0x0
.Ltmp882:
	.short	2
	.short	4430
	.short	2
	.short	4431
.Ltmp874:
	.p2align	2, 0x0
	.cv_linetable	265, _RNvXsK_NtCs8xEFJqa6dYS_4core3fmtNtB5_5ErrorNtB5_5Debug3fmt, .Lfunc_end10
	.section	.debug$S,"dr",associative,_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write10write_char
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp884-.Ltmp883
.Ltmp883:
	.short	.Ltmp886-.Ltmp885
.Ltmp885:
	.short	4422
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end11-_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write10write_char
	.long	0
	.long	0
	.long	4253
	.secrel32	_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write10write_char
	.secidx	_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write10write_char
	.byte	129
	.asciz	"alloc::string::impl$63::write_char"
	.p2align	2, 0x0
.Ltmp886:
	.short	.Ltmp888-.Ltmp887
.Ltmp887:
	.short	4114
	.long	40
	.long	0
	.long	0
	.long	32
	.long	0
	.short	0
	.long	1220640
	.p2align	2, 0x0
.Ltmp888:
	.short	.Ltmp890-.Ltmp889
.Ltmp889:
	.short	4456
	.long	1
	.long	4152
	.p2align	2, 0x0
.Ltmp890:
	.short	.Ltmp892-.Ltmp891
.Ltmp891:
	.short	4429
	.long	0
	.long	0
	.long	4152
	.cv_inline_linetable	268 10 1421 .Lfunc_begin11 .Lfunc_end11
	.p2align	2, 0x0
.Ltmp892:
	.short	.Ltmp894-.Ltmp893
.Ltmp893:
	.short	4429
	.long	0
	.long	0
	.long	4237
	.cv_inline_linetable	269 10 1865 .Lfunc_begin11 .Lfunc_end11
	.p2align	2, 0x0
.Ltmp894:
	.short	.Ltmp896-.Ltmp895
.Ltmp895:
	.short	4429
	.long	0
	.long	0
	.long	4205
	.cv_inline_linetable	270 11 3063 .Lfunc_begin11 .Lfunc_end11
	.p2align	2, 0x0
.Ltmp896:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp898-.Ltmp897
.Ltmp897:
	.short	4429
	.long	0
	.long	0
	.long	4176
	.cv_inline_linetable	271 15 661 .Lfunc_begin11 .Lfunc_end11
	.p2align	2, 0x0
.Ltmp898:
	.short	.Ltmp900-.Ltmp899
.Ltmp899:
	.short	4429
	.long	0
	.long	0
	.long	4177
	.cv_inline_linetable	272 15 2449 .Lfunc_begin11 .Lfunc_end11
	.p2align	2, 0x0
.Ltmp900:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp902-.Ltmp901
.Ltmp901:
	.short	4429
	.long	0
	.long	0
	.long	4178
	.cv_inline_linetable	273 10 1224 .Lfunc_begin11 .Lfunc_end11
	.p2align	2, 0x0
.Ltmp902:
	.short	.Ltmp904-.Ltmp903
.Ltmp903:
	.short	4429
	.long	0
	.long	0
	.long	4179
	.cv_inline_linetable	274 11 1468 .Lfunc_begin11 .Lfunc_end11
	.p2align	2, 0x0
.Ltmp904:
	.short	.Ltmp906-.Ltmp905
.Ltmp905:
	.short	4429
	.long	0
	.long	0
	.long	4180
	.cv_inline_linetable	275 2 339 .Lfunc_begin11 .Lfunc_end11
	.p2align	2, 0x0
.Ltmp906:
	.short	.Ltmp908-.Ltmp907
.Ltmp907:
	.short	4429
	.long	0
	.long	0
	.long	4181
	.cv_inline_linetable	276 2 656 .Lfunc_begin11 .Lfunc_end11
	.p2align	2, 0x0
.Ltmp908:
	.short	.Ltmp910-.Ltmp909
.Ltmp909:
	.short	4429
	.long	0
	.long	0
	.long	4182
	.cv_inline_linetable	277 2 767 .Lfunc_begin11 .Lfunc_end11
	.p2align	2, 0x0
.Ltmp910:
	.short	.Ltmp912-.Ltmp911
.Ltmp911:
	.short	4429
	.long	0
	.long	0
	.long	4183
	.cv_inline_linetable	278 2 619 .Lfunc_begin11 .Lfunc_end11
	.p2align	2, 0x0
.Ltmp912:
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
	.short	4430
	.short	.Ltmp914-.Ltmp913
.Ltmp913:
	.short	4429
	.long	0
	.long	0
	.long	4184
	.cv_inline_linetable	279 11 2058 .Lfunc_begin11 .Lfunc_end11
	.p2align	2, 0x0
.Ltmp914:
	.short	.Ltmp916-.Ltmp915
.Ltmp915:
	.short	4429
	.long	0
	.long	0
	.long	4185
	.cv_inline_linetable	280 2 295 .Lfunc_begin11 .Lfunc_end11
	.p2align	2, 0x0
.Ltmp916:
	.short	.Ltmp918-.Ltmp917
.Ltmp917:
	.short	4429
	.long	0
	.long	0
	.long	4186
	.cv_inline_linetable	281 2 609 .Lfunc_begin11 .Lfunc_end11
	.p2align	2, 0x0
.Ltmp918:
	.short	.Ltmp920-.Ltmp919
.Ltmp919:
	.short	4429
	.long	0
	.long	0
	.long	4187
	.cv_inline_linetable	282 2 614 .Lfunc_begin11 .Lfunc_end11
	.p2align	2, 0x0
.Ltmp920:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp922-.Ltmp921
.Ltmp921:
	.short	4429
	.long	0
	.long	0
	.long	4154
	.cv_inline_linetable	283 15 2517 .Lfunc_begin11 .Lfunc_end11
	.p2align	2, 0x0
.Ltmp922:
	.short	.Ltmp924-.Ltmp923
.Ltmp923:
	.short	4429
	.long	0
	.long	0
	.long	4177
	.cv_inline_linetable	284 15 2449 .Lfunc_begin11 .Lfunc_end11
	.p2align	2, 0x0
.Ltmp924:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp926-.Ltmp925
.Ltmp925:
	.short	4429
	.long	0
	.long	0
	.long	4155
	.cv_inline_linetable	285 11 2224 .Lfunc_begin11 .Lfunc_end11
	.p2align	2, 0x0
.Ltmp926:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4431
.Ltmp884:
	.p2align	2, 0x0
	.cv_linetable	267, _RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write10write_char, .Lfunc_end11
	.section	.debug$S,"dr",associative,_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_str
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp928-.Ltmp927
.Ltmp927:
	.short	.Ltmp930-.Ltmp929
.Ltmp929:
	.short	4422
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end12-_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_str
	.long	0
	.long	0
	.long	4254
	.secrel32	_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_str
	.secidx	_RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_str
	.byte	129
	.asciz	"alloc::string::impl$63::write_str"
	.p2align	2, 0x0
.Ltmp930:
	.short	.Ltmp932-.Ltmp931
.Ltmp931:
	.short	4114
	.long	40
	.long	0
	.long	0
	.long	32
	.long	0
	.short	0
	.long	1220640
	.p2align	2, 0x0
.Ltmp932:
	.short	.Ltmp934-.Ltmp933
.Ltmp933:
	.short	4456
	.long	1
	.long	4238
	.p2align	2, 0x0
.Ltmp934:
	.short	.Ltmp936-.Ltmp935
.Ltmp935:
	.short	4429
	.long	0
	.long	0
	.long	4238
	.cv_inline_linetable	287 10 1106 .Lfunc_begin12 .Lfunc_end12
	.p2align	2, 0x0
.Ltmp936:
	.short	.Ltmp938-.Ltmp937
.Ltmp937:
	.short	4429
	.long	0
	.long	0
	.long	4201
	.cv_inline_linetable	288 11 3566 .Lfunc_begin12 .Lfunc_end12
	.p2align	2, 0x0
.Ltmp938:
	.short	.Ltmp940-.Ltmp939
.Ltmp939:
	.short	4429
	.long	0
	.long	0
	.long	4203
	.cv_inline_linetable	289 27 54 .Lfunc_begin12 .Lfunc_end12
	.p2align	2, 0x0
.Ltmp940:
	.short	.Ltmp942-.Ltmp941
.Ltmp941:
	.short	4429
	.long	0
	.long	0
	.long	4204
	.cv_inline_linetable	290 11 2940 .Lfunc_begin12 .Lfunc_end12
	.p2align	2, 0x0
.Ltmp942:
	.short	.Ltmp944-.Ltmp943
.Ltmp943:
	.short	4429
	.long	0
	.long	0
	.long	4179
	.cv_inline_linetable	291 11 1468 .Lfunc_begin12 .Lfunc_end12
	.p2align	2, 0x0
.Ltmp944:
	.short	.Ltmp946-.Ltmp945
.Ltmp945:
	.short	4429
	.long	0
	.long	0
	.long	4180
	.cv_inline_linetable	292 2 339 .Lfunc_begin12 .Lfunc_end12
	.p2align	2, 0x0
.Ltmp946:
	.short	.Ltmp948-.Ltmp947
.Ltmp947:
	.short	4429
	.long	0
	.long	0
	.long	4181
	.cv_inline_linetable	293 2 656 .Lfunc_begin12 .Lfunc_end12
	.p2align	2, 0x0
.Ltmp948:
	.short	.Ltmp950-.Ltmp949
.Ltmp949:
	.short	4429
	.long	0
	.long	0
	.long	4182
	.cv_inline_linetable	294 2 767 .Lfunc_begin12 .Lfunc_end12
	.p2align	2, 0x0
.Ltmp950:
	.short	.Ltmp952-.Ltmp951
.Ltmp951:
	.short	4429
	.long	0
	.long	0
	.long	4183
	.cv_inline_linetable	295 2 619 .Lfunc_begin12 .Lfunc_end12
	.p2align	2, 0x0
.Ltmp952:
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
	.short	.Ltmp954-.Ltmp953
.Ltmp953:
	.short	4429
	.long	0
	.long	0
	.long	4151
	.cv_inline_linetable	296 12 936 .Lfunc_begin12 .Lfunc_end12
	.p2align	2, 0x0
.Ltmp954:
	.short	2
	.short	4430
	.short	.Ltmp956-.Ltmp955
.Ltmp955:
	.short	4429
	.long	0
	.long	0
	.long	4205
	.cv_inline_linetable	297 11 3063 .Lfunc_begin12 .Lfunc_end12
	.p2align	2, 0x0
.Ltmp956:
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
.Ltmp928:
	.p2align	2, 0x0
	.cv_linetable	286, _RNvXsZ_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_str, .Lfunc_end12
	.section	.debug$S,"dr",associative,_RNvYNtNtCsfQUUnEvlYZE_5alloc6string6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_fmtB6_
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp958-.Ltmp957
.Ltmp957:
	.short	.Ltmp960-.Ltmp959
.Ltmp959:
	.short	4422
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end13-_RNvYNtNtCsfQUUnEvlYZE_5alloc6string6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_fmtB6_
	.long	0
	.long	0
	.long	4230
	.secrel32	_RNvYNtNtCsfQUUnEvlYZE_5alloc6string6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_fmtB6_
	.secidx	_RNvYNtNtCsfQUUnEvlYZE_5alloc6string6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_fmtB6_
	.byte	128
	.asciz	"core::fmt::Write::write_fmt<alloc::string::String>"
	.p2align	2, 0x0
.Ltmp960:
	.short	.Ltmp962-.Ltmp961
.Ltmp961:
	.short	4114
	.long	0
	.long	0
	.long	0
	.long	0
	.long	0
	.short	0
	.long	1056768
	.p2align	2, 0x0
.Ltmp962:
	.short	.Ltmp964-.Ltmp963
.Ltmp963:
	.short	4456
	.long	1
	.long	4232
	.p2align	2, 0x0
.Ltmp964:
	.short	.Ltmp966-.Ltmp965
.Ltmp965:
	.short	4429
	.long	0
	.long	0
	.long	4232
	.cv_inline_linetable	299 31 234 .Lfunc_begin13 .Lfunc_end13
	.p2align	2, 0x0
.Ltmp966:
	.short	2
	.short	4430
	.short	2
	.short	4431
.Ltmp958:
	.p2align	2, 0x0
	.cv_linetable	298, _RNvYNtNtCsfQUUnEvlYZE_5alloc6string6StringNtNtCs8xEFJqa6dYS_4core3fmt5Write9write_fmtB6_, .Lfunc_end13
	.section	.debug$S,"dr"
	.cv_filechecksums
	.cv_stringtable
	.long	241
	.long	.Ltmp968-.Ltmp967
.Ltmp967:
	.short	.Ltmp970-.Ltmp969
.Ltmp969:
	.short	4428
	.long	4258
	.p2align	2, 0x0
.Ltmp970:
.Ltmp968:
	.p2align	2, 0x0
	.section	.debug$T,"dr"
	.p2align	2, 0x0
	.long	4
	.short	0x12
	.short	0x1605
	.long	0x0
	.asciz	"core::ptr"
	.byte	242
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
	.short	0x16
	.short	0x1601
	.long	0x1000
	.long	0x1002
	.asciz	"drop_glue"
	.byte	242
	.byte	241
	.short	0x1e
	.short	0x1605
	.long	0x0
	.asciz	"alloc::raw_vec::impl$3"
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x1004
	.long	0x1002
	.asciz	"drop"
	.byte	243
	.byte	242
	.byte	241
	.short	0x22
	.short	0x1605
	.long	0x0
	.asciz	"alloc::raw_vec::RawVecInner"
	.short	0x16
	.short	0x1601
	.long	0x1006
	.long	0x1002
	.asciz	"deallocate"
	.byte	241
	.short	0x1a
	.short	0x1601
	.long	0x1006
	.long	0x1002
	.asciz	"current_memory"
	.byte	241
	.short	0x1e
	.short	0x1605
	.long	0x0
	.asciz	"alloc::alloc::impl$1"
	.byte	243
	.byte	242
	.byte	241
	.short	0x16
	.short	0x1601
	.long	0x1009
	.long	0x1002
	.asciz	"deallocate"
	.byte	241
	.short	0x1e
	.short	0x1605
	.long	0x0
	.asciz	"alloc::alloc::Global"
	.byte	243
	.byte	242
	.byte	241
	.short	0x1a
	.short	0x1601
	.long	0x100b
	.long	0x1002
	.asciz	"deallocate_impl"
	.short	0x22
	.short	0x1601
	.long	0x100b
	.long	0x1002
	.asciz	"deallocate_impl_runtime"
	.short	0x16
	.short	0x1605
	.long	0x0
	.asciz	"alloc::alloc"
	.byte	243
	.byte	242
	.byte	241
	.short	0x1a
	.short	0x1601
	.long	0x100e
	.long	0x1002
	.asciz	"dealloc_nonnull"
	.short	0x2a
	.short	0x1605
	.long	0x0
	.asciz	"std::alloc::__default_lib_allocator"
	.short	0x1a
	.short	0x1601
	.long	0x1010
	.long	0x1002
	.asciz	"__rdl_dealloc"
	.byte	242
	.byte	241
	.short	0x2a
	.short	0x1605
	.long	0x0
	.asciz	"std::sys::alloc::windows::impl$0"
	.byte	243
	.byte	242
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x1012
	.long	0x1002
	.asciz	"dealloc"
	.short	0x22
	.short	0x1605
	.long	0x0
	.asciz	"std::sys::alloc::windows"
	.byte	243
	.byte	242
	.byte	241
	.short	0x1e
	.short	0x1601
	.long	0x1014
	.long	0x1002
	.asciz	"get_process_heap"
	.byte	243
	.byte	242
	.byte	241
	.short	0x1a
	.short	0x1601
	.long	0x1006
	.long	0x1002
	.asciz	"grow_amortized"
	.byte	241
	.short	0x1a
	.short	0x1605
	.long	0x0
	.asciz	"core::num::impl$11"
	.byte	241
	.short	0x16
	.short	0x1601
	.long	0x1017
	.long	0x1002
	.asciz	"checked_add"
	.short	0x1a
	.short	0x1605
	.long	0x0
	.asciz	"core::intrinsics"
	.byte	243
	.byte	242
	.byte	241
	.short	0x16
	.short	0x1601
	.long	0x1019
	.long	0x1002
	.asciz	"unlikely"
	.byte	243
	.byte	242
	.byte	241
	.short	0x12
	.short	0x1605
	.long	0x0
	.asciz	"core::cmp"
	.byte	242
	.byte	241
	.short	0xe
	.short	0x1601
	.long	0x101b
	.long	0x1002
	.asciz	"max"
	.short	0x16
	.short	0x1605
	.long	0x0
	.asciz	"core::cmp::Ord"
	.byte	241
	.short	0xe
	.short	0x1601
	.long	0x101d
	.long	0x1002
	.asciz	"max"
	.short	0x1e
	.short	0x1605
	.long	0x0
	.asciz	"core::result::impl$27"
	.byte	242
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x101f
	.long	0x1002
	.asciz	"branch"
	.byte	241
	.short	0x1a
	.short	0x1601
	.long	0x1006
	.long	0x1002
	.asciz	"set_ptr_and_cap"
	.short	0x1e
	.short	0x1605
	.long	0x0
	.asciz	"alloc::string::String"
	.byte	242
	.byte	241
	.short	0x1a
	.short	0x1601
	.long	0x1022
	.long	0x1002
	.asciz	"with_capacity"
	.byte	242
	.byte	241
	.short	0x16
	.short	0x1605
	.long	0x0
	.asciz	"alloc::vec::Vec"
	.short	0x1a
	.short	0x1601
	.long	0x1024
	.long	0x1002
	.asciz	"with_capacity"
	.byte	242
	.byte	241
	.short	0x1e
	.short	0x1601
	.long	0x1024
	.long	0x1002
	.asciz	"with_capacity_in"
	.byte	243
	.byte	242
	.byte	241
	.short	0x1e
	.short	0x1605
	.long	0x0
	.asciz	"alloc::raw_vec::RawVec"
	.byte	241
	.short	0x1e
	.short	0x1601
	.long	0x1027
	.long	0x1002
	.asciz	"with_capacity_in"
	.byte	243
	.byte	242
	.byte	241
	.short	0x1e
	.short	0x1601
	.long	0x1006
	.long	0x1002
	.asciz	"with_capacity_in"
	.byte	243
	.byte	242
	.byte	241
	.short	0x1a
	.short	0x1601
	.long	0x1006
	.long	0x1002
	.asciz	"try_allocate_in"
	.short	0x16
	.short	0x1601
	.long	0x1009
	.long	0x1002
	.asciz	"allocate"
	.byte	243
	.byte	242
	.byte	241
	.short	0x16
	.short	0x1601
	.long	0x100b
	.long	0x1002
	.asciz	"alloc_impl"
	.byte	241
	.short	0x1e
	.short	0x1601
	.long	0x100b
	.long	0x1002
	.asciz	"alloc_impl_runtime"
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x100e
	.long	0x1002
	.asciz	"alloc"
	.byte	242
	.byte	241
	.short	0x16
	.short	0x1601
	.long	0x1010
	.long	0x1002
	.asciz	"__rdl_alloc"
	.short	0x12
	.short	0x1601
	.long	0x1012
	.long	0x1002
	.asciz	"alloc"
	.byte	242
	.byte	241
	.short	0x16
	.short	0x1601
	.long	0x1014
	.long	0x1002
	.asciz	"allocate"
	.byte	243
	.byte	242
	.byte	241
	.short	0x1a
	.short	0x1605
	.long	0x0
	.asciz	"core::slice::impl$0"
	.short	0x12
	.short	0x1601
	.long	0x1032
	.long	0x1002
	.asciz	"iter"
	.byte	243
	.byte	242
	.byte	241
	.short	0x1e
	.short	0x1605
	.long	0x0
	.asciz	"core::slice::iter::Iter"
	.short	0xe
	.short	0x1601
	.long	0x1034
	.long	0x1002
	.asciz	"new"
	.short	0x22
	.short	0x1605
	.long	0x0
	.asciz	"core::ptr::mut_ptr::impl$0"
	.byte	241
	.short	0xe
	.short	0x1601
	.long	0x1036
	.long	0x1002
	.asciz	"add"
	.short	0x12
	.short	0x1601
	.long	0x1022
	.long	0x1002
	.asciz	"push"
	.byte	243
	.byte	242
	.byte	241
	.short	0x1a
	.short	0x1605
	.long	0x0
	.asciz	"core::char::methods"
	.short	0x26
	.short	0x1601
	.long	0x1039
	.long	0x1002
	.asciz	"encode_utf8_raw_unchecked"
	.byte	242
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x1024
	.long	0x1002
	.asciz	"set_len"
	.short	0x22
	.short	0x1605
	.long	0x0
	.asciz	"core::char::decode::impl$0"
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x103c
	.long	0x1002
	.asciz	"next"
	.byte	243
	.byte	242
	.byte	241
	.short	0x2e
	.short	0x1605
	.long	0x0
	.asciz	"core::iter::adapters::cloned::impl$1"
	.byte	243
	.byte	242
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x103e
	.long	0x1002
	.asciz	"next"
	.byte	243
	.byte	242
	.byte	241
	.short	0x22
	.short	0x1605
	.long	0x0
	.asciz	"core::slice::iter::impl$171"
	.short	0x12
	.short	0x1601
	.long	0x1040
	.long	0x1002
	.asciz	"next"
	.byte	243
	.byte	242
	.byte	241
	.short	0x26
	.short	0x1605
	.long	0x0
	.asciz	"core::ptr::non_null::impl$15"
	.byte	243
	.byte	242
	.byte	241
	.short	0xe
	.short	0x1601
	.long	0x1042
	.long	0x1002
	.asciz	"eq"
	.byte	241
	.short	0x26
	.short	0x1605
	.long	0x0
	.asciz	"core::ptr::non_null::NonNull"
	.byte	243
	.byte	242
	.byte	241
	.short	0xe
	.short	0x1601
	.long	0x1044
	.long	0x1002
	.asciz	"add"
	.short	0x1e
	.short	0x1605
	.long	0x0
	.asciz	"core::option::Option"
	.byte	243
	.byte	242
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x1046
	.long	0x1002
	.asciz	"cloned"
	.byte	241
	.short	0xe
	.short	0x1601
	.long	0x1046
	.long	0x1002
	.asciz	"map"
	.short	0x22
	.short	0x1605
	.long	0x0
	.asciz	"core::ops::function::FnOnce"
	.short	0x16
	.short	0x1601
	.long	0x1049
	.long	0x1002
	.asciz	"call_once"
	.byte	242
	.byte	241
	.short	0x22
	.short	0x1605
	.long	0x0
	.asciz	"core::clone::impls::impl$14"
	.short	0x12
	.short	0x1601
	.long	0x104b
	.long	0x1002
	.asciz	"clone"
	.byte	242
	.byte	241
	.short	0x1a
	.short	0x1605
	.long	0x0
	.asciz	"core::num::impl$7"
	.byte	242
	.byte	241
	.short	0x1e
	.short	0x1601
	.long	0x104d
	.long	0x1002
	.asciz	"is_utf16_surrogate"
	.byte	241
	.short	0x22
	.short	0x1605
	.long	0x0
	.asciz	"core::char::methods::impl$0"
	.short	0x16
	.short	0x1601
	.long	0x104f
	.long	0x1002
	.asciz	"len_utf8"
	.byte	243
	.byte	242
	.byte	241
	.short	0x16
	.short	0x1601
	.long	0x1039
	.long	0x1002
	.asciz	"len_utf8"
	.byte	243
	.byte	242
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x1022
	.long	0x1002
	.asciz	"reserve"
	.short	0x12
	.short	0x1601
	.long	0x1024
	.long	0x1002
	.asciz	"reserve"
	.short	0x12
	.short	0x1601
	.long	0x1027
	.long	0x1002
	.asciz	"reserve"
	.short	0x12
	.short	0x1601
	.long	0x1006
	.long	0x1002
	.asciz	"reserve"
	.short	0x1a
	.short	0x1601
	.long	0x1006
	.long	0x1002
	.asciz	"needs_to_grow"
	.byte	242
	.byte	241
	.short	0x16
	.short	0x1601
	.long	0x1006
	.long	0x1002
	.asciz	"capacity"
	.byte	243
	.byte	242
	.byte	241
	.short	0x16
	.short	0x1601
	.long	0x1024
	.long	0x1002
	.asciz	"as_mut_ptr"
	.byte	241
	.short	0xe
	.short	0x1601
	.long	0x1027
	.long	0x1002
	.asciz	"ptr"
	.short	0xe
	.short	0x1601
	.long	0x1006
	.long	0x1002
	.asciz	"ptr"
	.short	0x16
	.short	0x1601
	.long	0x1006
	.long	0x1002
	.asciz	"non_null"
	.byte	243
	.byte	242
	.byte	241
	.short	0x1a
	.short	0x1605
	.long	0x0
	.asciz	"alloc::wtf8::impl$0"
	.short	0x12
	.short	0x1601
	.long	0x105c
	.long	0x1002
	.asciz	"deref"
	.byte	242
	.byte	241
	.short	0x1e
	.short	0x1605
	.long	0x0
	.asciz	"alloc::wtf8::Wtf8Buf"
	.byte	243
	.byte	242
	.byte	241
	.short	0x16
	.short	0x1601
	.long	0x105e
	.long	0x1002
	.asciz	"as_slice"
	.byte	243
	.byte	242
	.byte	241
	.short	0x1a
	.short	0x1605
	.long	0x0
	.asciz	"alloc::vec::impl$9"
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x1060
	.long	0x1002
	.asciz	"deref"
	.byte	242
	.byte	241
	.short	0x16
	.short	0x1601
	.long	0x1024
	.long	0x1002
	.asciz	"as_slice"
	.byte	243
	.byte	242
	.byte	241
	.short	0x1a
	.short	0x1605
	.long	0x0
	.asciz	"core::wtf8::Wtf8"
	.byte	243
	.byte	242
	.byte	241
	.short	0x1a
	.short	0x1601
	.long	0x1063
	.long	0x1002
	.asciz	"next_surrogate"
	.byte	241
	.short	0x1a
	.short	0x1601
	.long	0x105e
	.long	0x1002
	.asciz	"with_capacity"
	.byte	242
	.byte	241
	.short	0x16
	.short	0x1601
	.long	0x105e
	.long	0x1002
	.asciz	"push_char"
	.byte	242
	.byte	241
	.short	0x26
	.short	0x1601
	.long	0x105e
	.long	0x1002
	.asciz	"push_code_point_unchecked"
	.byte	242
	.byte	241
	.short	0x1a
	.short	0x1601
	.long	0x1039
	.long	0x1002
	.asciz	"encode_utf8_raw"
	.short	0x1e
	.short	0x1601
	.long	0x1024
	.long	0x1002
	.asciz	"extend_from_slice"
	.byte	242
	.byte	241
	.short	0x26
	.short	0x1605
	.long	0x0
	.asciz	"alloc::vec::spec_extend::impl$4"
	.short	0x16
	.short	0x1601
	.long	0x106a
	.long	0x1002
	.asciz	"spec_extend"
	.short	0x1a
	.short	0x1601
	.long	0x1024
	.long	0x1002
	.asciz	"append_elements"
	.short	0xe
	.short	0x1601
	.long	0x1024
	.long	0x1002
	.asciz	"len"
	.short	0x16
	.short	0x1605
	.long	0x0
	.asciz	"alloc::raw_vec"
	.byte	241
	.short	0x1a
	.short	0x1601
	.long	0x106e
	.long	0x1002
	.asciz	"layout_array"
	.byte	243
	.byte	242
	.byte	241
	.short	0x22
	.short	0x1605
	.long	0x0
	.asciz	"core::alloc::layout::Layout"
	.short	0x1a
	.short	0x1601
	.long	0x1070
	.long	0x1002
	.asciz	"repeat_packed"
	.byte	242
	.byte	241
	.short	0x1e
	.short	0x1601
	.long	0x1070
	.long	0x1002
	.asciz	"from_size_alignment"
	.short	0x22
	.short	0x1601
	.long	0x1070
	.long	0x1002
	.asciz	"is_size_alignment_valid"
	.short	0x12
	.short	0x1601
	.long	0x1009
	.long	0x1002
	.asciz	"grow"
	.byte	243
	.byte	242
	.byte	241
	.short	0x16
	.short	0x1601
	.long	0x100b
	.long	0x1002
	.asciz	"grow_impl"
	.byte	242
	.byte	241
	.short	0x1e
	.short	0x1601
	.long	0x100b
	.long	0x1002
	.asciz	"grow_impl_runtime"
	.byte	242
	.byte	241
	.short	0x1a
	.short	0x1601
	.long	0x100e
	.long	0x1002
	.asciz	"realloc_nonnull"
	.short	0x1a
	.short	0x1601
	.long	0x1010
	.long	0x1002
	.asciz	"__rdl_realloc"
	.byte	242
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x1012
	.long	0x1002
	.asciz	"realloc"
	.short	0x2a
	.short	0x1605
	.long	0x0
	.asciz	"alloc::alloc::handle_alloc_error"
	.byte	243
	.byte	242
	.byte	241
	.short	0x16
	.short	0x1601
	.long	0x107a
	.long	0x1002
	.asciz	"rt_error"
	.byte	243
	.byte	242
	.byte	241
	.short	0x2a
	.short	0x1605
	.long	0x0
	.asciz	"alloc::collections::TryReserveError"
	.short	0x12
	.short	0x1601
	.long	0x107c
	.long	0x1002
	.asciz	"kind"
	.byte	243
	.byte	242
	.byte	241
	.short	0x22
	.short	0x1605
	.long	0x0
	.asciz	"alloc::collections::impl$1"
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x107e
	.long	0x1002
	.asciz	"clone"
	.byte	242
	.byte	241
	.short	0x1e
	.short	0x1605
	.long	0x0
	.asciz	"core::fmt::Arguments"
	.byte	243
	.byte	242
	.byte	241
	.short	0x1e
	.short	0x1601
	.long	0x1080
	.long	0x1002
	.asciz	"estimated_capacity"
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x1080
	.long	0x1002
	.asciz	"as_str"
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x1044
	.long	0x1002
	.asciz	"read"
	.byte	243
	.byte	242
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x1000
	.long	0x1002
	.asciz	"read"
	.byte	243
	.byte	242
	.byte	241
	.short	0x1a
	.short	0x1605
	.long	0x0
	.asciz	"core::fmt::Write"
	.byte	243
	.byte	242
	.byte	241
	.short	0x16
	.short	0x1601
	.long	0x1085
	.long	0x1002
	.asciz	"write_fmt"
	.byte	242
	.byte	241
	.short	0x2a
	.short	0x1605
	.long	0x0
	.asciz	"core::fmt::Write::write_fmt::impl$1"
	.short	0x1a
	.short	0x1601
	.long	0x1087
	.long	0x1002
	.asciz	"spec_write_fmt"
	.byte	241
	.short	0x1e
	.short	0x1605
	.long	0x0
	.asciz	"core::result::Result"
	.byte	243
	.byte	242
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x1089
	.long	0x1002
	.asciz	"expect"
	.byte	241
	.short	0x1e
	.short	0x1605
	.long	0x0
	.asciz	"core::fmt::Formatter"
	.byte	243
	.byte	242
	.byte	241
	.short	0x16
	.short	0x1601
	.long	0x108b
	.long	0x1002
	.asciz	"write_str"
	.byte	242
	.byte	241
	.short	0xe
	.short	0x1601
	.long	0x1022
	.long	0x1002
	.asciz	"len"
	.short	0x16
	.short	0x1601
	.long	0x1022
	.long	0x1002
	.asciz	"push_str"
	.byte	243
	.byte	242
	.byte	241
	.short	0x26
	.short	0x1605
	.long	0x0
	.asciz	"alloc::raw_vec::impl$4::reserve"
	.short	0x22
	.short	0x1601
	.long	0x108f
	.long	0x1002
	.asciz	"do_reserve_and_handle"
	.byte	242
	.byte	241
	.short	0x16
	.short	0x1601
	.long	0x1022
	.long	0x1002
	.asciz	"from_utf16"
	.byte	241
	.short	0x16
	.short	0x1601
	.long	0x105e
	.long	0x1002
	.asciz	"into_string"
	.short	0x16
	.short	0x1601
	.long	0x105e
	.long	0x1002
	.asciz	"from_wide"
	.byte	242
	.byte	241
	.short	0x16
	.short	0x1601
	.long	0x1006
	.long	0x1002
	.asciz	"finish_grow"
	.short	0x1e
	.short	0x1601
	.long	0x100e
	.long	0x1002
	.asciz	"handle_alloc_error"
	.byte	241
	.short	0x1a
	.short	0x1601
	.long	0x106e
	.long	0x1002
	.asciz	"handle_error"
	.byte	243
	.byte	242
	.byte	241
	.short	0x1e
	.short	0x1601
	.long	0x106e
	.long	0x1002
	.asciz	"capacity_overflow"
	.byte	242
	.byte	241
	.short	0x1a
	.short	0x1605
	.long	0x0
	.asciz	"alloc::fmt::format"
	.byte	241
	.short	0x1a
	.short	0x1601
	.long	0x1098
	.long	0x1002
	.asciz	"format_inner"
	.byte	243
	.byte	242
	.byte	241
	.short	0x1a
	.short	0x1605
	.long	0x0
	.asciz	"core::fmt::impl$48"
	.byte	241
	.short	0xe
	.short	0x1601
	.long	0x109a
	.long	0x1002
	.asciz	"fmt"
	.short	0x1e
	.short	0x1605
	.long	0x0
	.asciz	"alloc::string::impl$63"
	.byte	241
	.short	0x16
	.short	0x1601
	.long	0x109c
	.long	0x1002
	.asciz	"write_char"
	.byte	241
	.short	0x16
	.short	0x1601
	.long	0x109c
	.long	0x1002
	.asciz	"write_str"
	.byte	242
	.byte	241
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
	.long	0x109f
	.long	0x10a1
	.long	0x10a0
	.long	0x10a1
	.long	0x10a1
	.byte	242
	.byte	241
