	.def	@feat.00;
	.scl	3;
	.type	0;
	.endef
	.globl	@feat.00
@feat.00 = 0
	.file	"panic_unwind.772da25958b8bb98-cgu.0"
	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind,unique,0
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind:
.Lfunc_begin0:
	.cv_func_id 0
	.cv_file	1 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\ptr\\mod.rs" "F7B3E71D9E9246762C38641C6C1A49079265782AAB6DEAA537B43665B418F029" 3
	.cv_loc	0 1 823 0
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$56, %rsp
	.seh_stackalloc 56
	leaq	48(%rsp), %rbp
	.seh_setframe %rbp, 48
	.seh_endprologue
	movq	$-2, (%rbp)
	movq	%rcx, -16(%rbp)
	movq	%rdx, -8(%rbp)
.Ltmp2:
	movq	(%rdx), %rax
	testq	%rax, %rax
	je	.LBB0_2
.Ltmp0:
	movq	-16(%rbp), %rcx
	callq	*%rax
	nop
.Ltmp1:
.LBB0_2:
	.cv_file	2 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\alloc\\src\\boxed.rs" "AD1B7AB420AE7FCED26FBD1FF0B8B1B603057D509F75B283D285B3D3BD0A7D0F" 3
	.cv_inline_site_id 1 within 0 inlined_at 1 823 0
	.cv_loc	1 2 1999 0
	movq	-16(%rbp), %rsi
	movq	-8(%rbp), %rax
.Ltmp3:
	cmpq	$0, 8(%rax)
	je	.LBB0_6
.Ltmp4:
	.cv_file	3 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\std\\src\\sys\\alloc\\windows.rs" "E2DBB86E7CE2412CA9E653343D17275963853F861C27EE5C04D9A22D162000E0" 3
	.cv_inline_site_id 2 within 1 inlined_at 2 2000 0
	.cv_file	4 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\alloc\\src\\alloc.rs" "699C02FE7844CD9490905545E503FEC56552BE2A34D50A79242852739483889B" 3
	.cv_inline_site_id 3 within 2 inlined_at 4 462 0
	.cv_inline_site_id 4 within 3 inlined_at 4 344 0
	.cv_inline_site_id 5 within 4 inlined_at 4 229 0
	.cv_inline_site_id 6 within 5 inlined_at 4 128 0
	.cv_file	5 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\std\\src\\alloc.rs" "2D22C4F49121716BA9EDA233D097746C11E51B387A868F5FCE83D6F1E52BECF6" 3
	.cv_inline_site_id 7 within 6 inlined_at 5 463 0
	.cv_loc	7 3 182 0
	cmpl	$17, 16(%rax)
	jb	.LBB0_5
.Ltmp5:
	.cv_inline_site_id 8 within 7 inlined_at 3 189 0
	.cv_loc	8 1 1731 0
	movq	-8(%rsi), %rsi
.Ltmp6:
.LBB0_5:
	.cv_inline_site_id 9 within 7 inlined_at 3 195 0
	.cv_loc	9 3 85 0
	callq	*__imp_GetProcessHeap(%rip)
.Ltmp7:
	.cv_loc	7 3 199 0
	movq	%rax, %rcx
	xorl	%edx, %edx
	movq	%rsi, %r8
	.seh_startepilogue
	addq	$56, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	rex64 jmpq	*__imp_HeapFree(%rip)
.Ltmp8:
.LBB0_6:
	.cv_loc	0 1 823 0
	.seh_startepilogue
	addq	$56, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind@IMGREL
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind,unique,0
	.seh_endproc
	.def	"?dtor$7@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$7@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind@4HA":
.seh_proc "?dtor$7@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind@4HA"
.LBB0_7:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	48(%rdx), %rbp
	.seh_endprologue
	movq	-16(%rbp), %rcx
	movq	-8(%rbp), %rax
.Ltmp9:
	.cv_file	6 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\mem\\mod.rs" "538B04A5F1988AE5C50EDC376021F6DB3FE6291EBC24423BA6A747BC0D00688B" 3
	.cv_inline_site_id 10 within 0 inlined_at 1 823 0
	.cv_inline_site_id 11 within 10 inlined_at 2 1998 0
	.cv_file	7 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\alloc\\layout.rs" "19119EDE8A60D1A989F907118F9E7F36E24434B8E931875F66A379B856784124" 3
	.cv_inline_site_id 12 within 11 inlined_at 7 255 0
	.cv_loc	12 6 465 0
	movq	8(%rax), %rdx
.Ltmp10:
	.cv_loc	10 2 1999 0
	testq	%rdx, %rdx
	je	.LBB0_9
.Ltmp11:
	.cv_file	8 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\mem\\alignment.rs" "4EB6651741FC8D8D84CE274219CC72399949AA9EBA2A4592A3F90D9293D1B587" 3
	.cv_inline_site_id 13 within 12 inlined_at 8 157 0
	.cv_loc	13 6 634 0
	movq	-8(%rbp), %rax
.Ltmp12:
	movq	16(%rax), %r8
.Ltmp13:
	.cv_inline_site_id 14 within 10 inlined_at 2 2000 0
	.cv_inline_site_id 15 within 14 inlined_at 4 462 0
	.cv_inline_site_id 16 within 15 inlined_at 4 344 0
	.cv_inline_site_id 17 within 16 inlined_at 4 229 0
	.cv_loc	17 4 128 0
	callq	_RNvCs1njKG4L9aB3_7___rustc14___rust_dealloc
	nop
.Ltmp14:
.LBB0_9:
	.cv_loc	0 1 823 0
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.Ltmp15:
.Lfunc_end0:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind,unique,0
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind,unique,0
	.p2align	2, 0x0
$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind@IMGREL
	.long	48
	.long	0
	.long	1
$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind:
	.long	-1
	.long	"?dtor$7@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind@4HA"@IMGREL
$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind:
	.long	.Lfunc_begin0@IMGREL
	.long	-1
	.long	.Ltmp0@IMGREL
	.long	0
	.long	.Ltmp1@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind,unique,0

	.def	_RNvCs1njKG4L9aB3_7___rustc18___rust_start_panic;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvCs1njKG4L9aB3_7___rustc18___rust_start_panic,unique,1
	.globl	_RNvCs1njKG4L9aB3_7___rustc18___rust_start_panic
	.p2align	4
_RNvCs1njKG4L9aB3_7___rustc18___rust_start_panic:
.Lfunc_begin1:
	.cv_func_id 18
	.cv_file	9 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\panic_unwind\\src\\lib.rs" "733A5A44C3AB3829670AA736127E39AB605A1CABC51FC47FEC4CAA92698690BB" 3
	.cv_loc	18 9 99 0
.seh_proc _RNvCs1njKG4L9aB3_7___rustc18___rust_start_panic
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	32(%rsp), %rbp
	.seh_setframe %rbp, 32
	.seh_endprologue
.Ltmp16:
	.cv_loc	18 9 101 0
	callq	*32(%rdx)
.Ltmp17:
	.cv_file	10 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\panic_unwind\\src\\seh.rs" "277EB0E5BE1F8BC1B8A8401A680E379A29F643B3ABA60E50C39C789A111FBACF" 3
	.cv_inline_site_id 19 within 18 inlined_at 9 103 0
	.cv_loc	19 10 302 0
	movq	%rax, %rcx
	callq	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp15throw_exception.llvm.16952210977915244029
	ud2
.Ltmp18:
.Lfunc_end1:
	.seh_endproc

	.def	_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup,unique,2
	.globl	_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup
	.p2align	4
_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup:
.Lfunc_begin2:
	.cv_func_id 20
	.cv_loc	20 9 92 0
.seh_proc _RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$48, %rsp
	.seh_stackalloc 48
	leaq	48(%rsp), %rbp
	.seh_setframe %rbp, 48
	.seh_endprologue
.Ltmp21:
	.cv_inline_site_id 21 within 20 inlined_at 9 93 0
	.cv_loc	21 10 376 0
	movq	$-2, -8(%rbp)
	testq	%rdx, %rdx
	je	.LBB2_7
.Ltmp22:
	.cv_inline_site_id 22 within 21 inlined_at 10 381 0
	.cv_loc	22 1 2476 0
	leaq	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp15TYPE_DESCRIPTOR.llvm.16952210977915244029(%rip), %rax
	cmpq	%rax, (%rdx)
.Ltmp23:
	.cv_loc	21 10 381 0
	jne	.LBB2_7
.Ltmp24:
	.cv_inline_site_id 23 within 21 inlined_at 10 385 0
	.cv_file	11 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\option.rs" "FC70106A756F98208E6A6A3E428310BDFA3531877CF6C6A99F39FFFA26AB2C40" 3
	.cv_inline_site_id 24 within 23 inlined_at 11 1901 0
	.cv_loc	24 6 967 0
	movq	8(%rdx), %rax
	movq	16(%rdx), %r8
.Ltmp25:
	.cv_loc	24 6 968 0
	movq	$0, 8(%rdx)
.Ltmp26:
	.cv_loc	23 11 1012 0
	testq	%rax, %rax
	je	.LBB2_3
.Ltmp27:
	.cv_inline_site_id 25 within 20 inlined_at 9 93 0
	.cv_loc	25 2 1441 0
	movq	%rax, (%rcx)
	movq	%r8, 8(%rcx)
.Ltmp28:
	.cv_loc	20 9 94 0
	movq	%rcx, %rax
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.LBB2_3:
	.cv_loc	23 11 1014 0
.Ltmp19:
.Ltmp29:
	leaq	anon.7378ff6387f5d434c287039208ce5213.1.llvm.16952210977915244029(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	nop
.Ltmp20:
	ud2
.Ltmp30:
.LBB2_7:
	callq	_RNvCs1njKG4L9aB3_7___rustc24___rust_foreign_exception
	ud2
.Ltmp31:
	.seh_handlerdata
	.long	$cppxdata$_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup@IMGREL
	.section	.text,"xr",one_only,_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup,unique,2
	.seh_endproc
	.def	"?catch$5@?0?_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?catch$5@?0?_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup@4HA":
.seh_proc "?catch$5@?0?_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup@4HA"
	.seh_handler __CxxFrameHandler3, @unwind, @except
.LBB2_5:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	48(%rdx), %rbp
	.seh_endprologue
	.cv_loc	20 9 92 0
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking19panic_cannot_unwind
	ud2
.Ltmp32:
.Lfunc_end2:
	.seh_handlerdata
	.long	$cppxdata$_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup@IMGREL
	.section	.text,"xr",one_only,_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup,unique,2
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup,unique,1
	.p2align	2, 0x0
$cppxdata$_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup:
	.long	429065506
	.long	2
	.long	$stateUnwindMap$_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup@IMGREL
	.long	1
	.long	$tryMap$_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup@IMGREL
	.long	4
	.long	$ip2state$_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup@IMGREL
	.long	40
	.long	0
	.long	1
$stateUnwindMap$_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup:
	.long	-1
	.long	0
	.long	-1
	.long	0
$tryMap$_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup:
	.long	0
	.long	0
	.long	1
	.long	1
	.long	$handlerMap$0$_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup@IMGREL
$handlerMap$0$_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup:
	.long	64
	.long	0
	.long	0
	.long	"?catch$5@?0?_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup@4HA"@IMGREL
	.long	56
$ip2state$_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup:
	.long	.Lfunc_begin2@IMGREL
	.long	-1
	.long	.Ltmp19@IMGREL
	.long	0
	.long	.Ltmp20@IMGREL
	.long	-1
	.long	"?catch$5@?0?_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup@4HA"@IMGREL
	.long	1
	.section	.text,"xr",one_only,_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup,unique,2

	.def	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp14exception_copy.llvm.16952210977915244029;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNtCsaenKx8lKFZc_12panic_unwind3imp14exception_copy.llvm.16952210977915244029,unique,3
	.globl	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp14exception_copy.llvm.16952210977915244029
	.p2align	4
_RNvNtCsaenKx8lKFZc_12panic_unwind3imp14exception_copy.llvm.16952210977915244029:
.Lfunc_begin3:
	.cv_func_id 26
	.cv_loc	26 10 283 0
.seh_proc _RNvNtCsaenKx8lKFZc_12panic_unwind3imp14exception_copy.llvm.16952210977915244029
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	32(%rsp), %rbp
	.seh_setframe %rbp, 32
	.seh_endprologue
.Ltmp33:
	.cv_loc	26 10 287 0
	xorl	%ecx, %ecx
	callq	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp15throw_exception.llvm.16952210977915244029
	ud2
.Ltmp34:
.Lfunc_end3:
	.seh_endproc

	.def	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp15throw_exception.llvm.16952210977915244029;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNtCsaenKx8lKFZc_12panic_unwind3imp15throw_exception.llvm.16952210977915244029,unique,4
	.globl	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp15throw_exception.llvm.16952210977915244029
	.p2align	4
_RNvNtCsaenKx8lKFZc_12panic_unwind3imp15throw_exception.llvm.16952210977915244029:
.Lfunc_begin4:
	.cv_func_id 27
	.cv_loc	27 10 305 0
.seh_proc _RNvNtCsaenKx8lKFZc_12panic_unwind3imp15throw_exception.llvm.16952210977915244029
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$64, %rsp
	.seh_stackalloc 64
	leaq	64(%rsp), %rbp
	.seh_setframe %rbp, 64
	.seh_endprologue
.Ltmp35:
	.cv_file	12 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\mem\\manually_drop.rs" "C21100B507893A11EE27B0711BE3AC3FE6CC970B96BBA55A7D3BAE5978209818" 3
	.cv_inline_site_id 28 within 27 inlined_at 10 315 0
	.cv_loc	28 12 182 0
	leaq	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp15TYPE_DESCRIPTOR.llvm.16952210977915244029(%rip), %rax
	movq	%rax, -24(%rbp)
	movq	%rcx, -16(%rbp)
	movq	%rdx, -8(%rbp)
.Ltmp36:
	.cv_loc	27 10 340 0
	leaq	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029(%rip), %rcx
	leaq	__ImageBase(%rip), %r8
	subl	%r8d, %ecx
	xchgl	%ecx, _RNvNtCsaenKx8lKFZc_12panic_unwind3imp10THROW_INFO.llvm.16952210977915244029+4(%rip)
.Ltmp37:
	.cv_loc	27 10 344 0
	leaq	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp20CATCHABLE_TYPE_ARRAY.llvm.16952210977915244029(%rip), %rcx
	subl	%r8d, %ecx
	xchgl	%ecx, _RNvNtCsaenKx8lKFZc_12panic_unwind3imp10THROW_INFO.llvm.16952210977915244029+12(%rip)
.Ltmp38:
	.cv_loc	27 10 340 0
	leaq	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp10THROW_INFO.llvm.16952210977915244029(%rip), %rdx
.Ltmp39:
	.cv_loc	27 10 348 0
	leaq	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp14CATCHABLE_TYPE.llvm.16952210977915244029(%rip), %rcx
	subl	%r8d, %ecx
	xchgl	%ecx, _RNvNtCsaenKx8lKFZc_12panic_unwind3imp20CATCHABLE_TYPE_ARRAY.llvm.16952210977915244029+4(%rip)
	.cv_loc	27 10 352 0
	subl	%r8d, %eax
	xchgl	%eax, _RNvNtCsaenKx8lKFZc_12panic_unwind3imp14CATCHABLE_TYPE.llvm.16952210977915244029+4(%rip)
.Ltmp40:
	.cv_loc	27 10 357 0
	leaq	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp14exception_copy.llvm.16952210977915244029(%rip), %rax
	subl	%r8d, %eax
	xchgl	%eax, _RNvNtCsaenKx8lKFZc_12panic_unwind3imp14CATCHABLE_TYPE.llvm.16952210977915244029+24(%rip)
	leaq	-24(%rbp), %rcx
.Ltmp41:
	.cv_loc	27 10 368 0
	callq	_CxxThrowException
	ud2
.Ltmp42:
.Lfunc_end4:
	.seh_endproc

	.def	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029,unique,5
	.globl	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029
	.p2align	4
_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029:
.Lfunc_begin5:
	.cv_func_id 29
	.cv_loc	29 10 275 0
.seh_proc _RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$48, %rsp
	.seh_stackalloc 48
	leaq	48(%rsp), %rbp
	.seh_setframe %rbp, 48
	.seh_endprologue
	movq	$-2, -8(%rbp)
	movq	%rcx, %rax
.Ltmp45:
	.cv_inline_site_id 30 within 29 inlined_at 10 277 0
	.cv_file	13 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\ptr\\mut_ptr.rs" "54527A10B3C1B7BD589C13443EB2482BA8B8D9004B8184D58BB04A553345C1A9" 3
	.cv_inline_site_id 31 within 30 inlined_at 13 1245 0
	.cv_loc	31 1 1731 0
	movq	8(%rcx), %rcx
.Ltmp46:
	.cv_loc	29 10 277 0
	testq	%rcx, %rcx
	jne	.LBB5_1
.Ltmp47:
	.cv_loc	29 10 282 0
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.LBB5_1:
.Ltmp48:
	.cv_loc	31 1 1731 0
	movq	16(%rax), %rdx
.Ltmp49:
	.cv_inline_site_id 32 within 29 inlined_at 10 278 0
	.cv_loc	32 6 1041 0
.Ltmp43:
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind
	nop
.Ltmp50:
.Ltmp44:
	.cv_loc	29 10 279 0
	callq	_RNvCs1njKG4L9aB3_7___rustc17___rust_drop_panic
	ud2
.Ltmp51:
	.seh_handlerdata
	.long	$cppxdata$_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029@IMGREL
	.section	.text,"xr",one_only,_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029,unique,5
	.seh_endproc
	.def	"?dtor$4@?0?_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$4@?0?_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029@4HA":
.seh_proc "?dtor$4@?0?_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029@4HA"
.LBB5_4:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	48(%rdx), %rbp
	.seh_endprologue
	.cv_loc	29 10 275 0
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking19panic_cannot_unwind
	ud2
.Ltmp52:
.Lfunc_end5:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029,unique,5
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029,unique,2
	.p2align	2, 0x0
$cppxdata$_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029@IMGREL
	.long	40
	.long	0
	.long	1
$stateUnwindMap$_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029:
	.long	-1
	.long	"?dtor$4@?0?_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029@4HA"@IMGREL
$ip2state$_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029:
	.long	.Lfunc_begin5@IMGREL
	.long	-1
	.long	.Ltmp43@IMGREL
	.long	0
	.long	.Ltmp44@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029,unique,5

	.section	.bss,"bw",one_only,_RNvNtCsaenKx8lKFZc_12panic_unwind3imp10THROW_INFO.llvm.16952210977915244029,unique,6
	.globl	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp10THROW_INFO.llvm.16952210977915244029
	.p2align	2, 0x0
_RNvNtCsaenKx8lKFZc_12panic_unwind3imp10THROW_INFO.llvm.16952210977915244029:
	.zero	16

	.section	.data,"dw",one_only,_RNvNtCsaenKx8lKFZc_12panic_unwind3imp14CATCHABLE_TYPE.llvm.16952210977915244029,unique,7
	.globl	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp14CATCHABLE_TYPE.llvm.16952210977915244029
	.p2align	2, 0x0
_RNvNtCsaenKx8lKFZc_12panic_unwind3imp14CATCHABLE_TYPE.llvm.16952210977915244029:
	.asciz	"\000\000\000\000\000\000\000\000\000\000\000\000\377\377\377\377\000\000\000\000\030\000\000\000\000\000\000"

	.section	.data,"dw",one_only,_RNvNtCsaenKx8lKFZc_12panic_unwind3imp15TYPE_DESCRIPTOR.llvm.16952210977915244029,unique,8
	.globl	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp15TYPE_DESCRIPTOR.llvm.16952210977915244029
	.p2align	3, 0x0
_RNvNtCsaenKx8lKFZc_12panic_unwind3imp15TYPE_DESCRIPTOR.llvm.16952210977915244029:
	.quad	"??_7type_info@@6B@"
	.asciz	"\000\000\000\000\000\000\000\000rust_panic"
	.zero	5

	.section	.data,"dw",one_only,_RNvNtCsaenKx8lKFZc_12panic_unwind3imp20CATCHABLE_TYPE_ARRAY.llvm.16952210977915244029,unique,9
	.globl	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp20CATCHABLE_TYPE_ARRAY.llvm.16952210977915244029
	.p2align	2, 0x0
_RNvNtCsaenKx8lKFZc_12panic_unwind3imp20CATCHABLE_TYPE_ARRAY.llvm.16952210977915244029:
	.asciz	"\001\000\000\000\000\000\000"

	.section	.rdata,"dr",one_only,anon.7378ff6387f5d434c287039208ce5213.0.llvm.16952210977915244029,unique,10
	.globl	anon.7378ff6387f5d434c287039208ce5213.0.llvm.16952210977915244029
anon.7378ff6387f5d434c287039208ce5213.0.llvm.16952210977915244029:
	.asciz	"/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\panic_unwind\\src\\seh.rs"

	.section	.rdata,"dr",one_only,anon.7378ff6387f5d434c287039208ce5213.1.llvm.16952210977915244029,unique,11
	.globl	anon.7378ff6387f5d434c287039208ce5213.1.llvm.16952210977915244029
	.p2align	3, 0x0
anon.7378ff6387f5d434c287039208ce5213.1.llvm.16952210977915244029:
	.quad	anon.7378ff6387f5d434c287039208ce5213.0.llvm.16952210977915244029
	.asciz	"O\000\000\000\000\000\000\000\201\001\000\000\"\000\000"

	.section	.data,"dw",one_only,__imp__RNvNtCsaenKx8lKFZc_12panic_unwind3imp10THROW_INFO.llvm.16952210977915244029,unique,12
	.globl	__imp__RNvNtCsaenKx8lKFZc_12panic_unwind3imp10THROW_INFO.llvm.16952210977915244029
	.p2align	3, 0x0
__imp__RNvNtCsaenKx8lKFZc_12panic_unwind3imp10THROW_INFO.llvm.16952210977915244029:
	.quad	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp10THROW_INFO.llvm.16952210977915244029

	.section	.data,"dw",one_only,__imp__RNvNtCsaenKx8lKFZc_12panic_unwind3imp14CATCHABLE_TYPE.llvm.16952210977915244029,unique,13
	.globl	__imp__RNvNtCsaenKx8lKFZc_12panic_unwind3imp14CATCHABLE_TYPE.llvm.16952210977915244029
	.p2align	3, 0x0
__imp__RNvNtCsaenKx8lKFZc_12panic_unwind3imp14CATCHABLE_TYPE.llvm.16952210977915244029:
	.quad	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp14CATCHABLE_TYPE.llvm.16952210977915244029

	.section	.data,"dw",one_only,__imp__RNvNtCsaenKx8lKFZc_12panic_unwind3imp15TYPE_DESCRIPTOR.llvm.16952210977915244029,unique,14
	.globl	__imp__RNvNtCsaenKx8lKFZc_12panic_unwind3imp15TYPE_DESCRIPTOR.llvm.16952210977915244029
	.p2align	3, 0x0
__imp__RNvNtCsaenKx8lKFZc_12panic_unwind3imp15TYPE_DESCRIPTOR.llvm.16952210977915244029:
	.quad	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp15TYPE_DESCRIPTOR.llvm.16952210977915244029

	.section	.data,"dw",one_only,__imp__RNvNtCsaenKx8lKFZc_12panic_unwind3imp20CATCHABLE_TYPE_ARRAY.llvm.16952210977915244029,unique,15
	.globl	__imp__RNvNtCsaenKx8lKFZc_12panic_unwind3imp20CATCHABLE_TYPE_ARRAY.llvm.16952210977915244029
	.p2align	3, 0x0
__imp__RNvNtCsaenKx8lKFZc_12panic_unwind3imp20CATCHABLE_TYPE_ARRAY.llvm.16952210977915244029:
	.quad	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp20CATCHABLE_TYPE_ARRAY.llvm.16952210977915244029

	.section	.data,"dw",one_only,__imp_anon.7378ff6387f5d434c287039208ce5213.0.llvm.16952210977915244029,unique,16
	.globl	__imp_anon.7378ff6387f5d434c287039208ce5213.0.llvm.16952210977915244029
	.p2align	3, 0x0
__imp_anon.7378ff6387f5d434c287039208ce5213.0.llvm.16952210977915244029:
	.quad	anon.7378ff6387f5d434c287039208ce5213.0.llvm.16952210977915244029

	.section	.data,"dw",one_only,__imp_anon.7378ff6387f5d434c287039208ce5213.1.llvm.16952210977915244029,unique,17
	.globl	__imp_anon.7378ff6387f5d434c287039208ce5213.1.llvm.16952210977915244029
	.p2align	3, 0x0
__imp_anon.7378ff6387f5d434c287039208ce5213.1.llvm.16952210977915244029:
	.quad	anon.7378ff6387f5d434c287039208ce5213.1.llvm.16952210977915244029

	.section	.debug$S,"dr"
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp54-.Ltmp53
.Ltmp53:
	.short	.Ltmp56-.Ltmp55
.Ltmp55:
	.short	4353
	.long	0
	.asciz	"prototype.panic_unwind-d45f266e54626acb.panic_unwind.772da25958b8bb98-cgu.0.rcgu.o.rcgu.o"
	.p2align	2, 0x0
.Ltmp56:
	.short	.Ltmp58-.Ltmp57
.Ltmp57:
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
.Ltmp58:
.Ltmp54:
	.p2align	2, 0x0
	.long	246
	.long	.Ltmp60-.Ltmp59
.Ltmp59:
	.long	0


	.long	4099
	.cv_filechecksumoffset	2
	.long	1992


	.long	4101
	.cv_filechecksumoffset	4
	.long	460


	.long	4103
	.cv_filechecksumoffset	4
	.long	343


	.long	4104
	.cv_filechecksumoffset	4
	.long	219


	.long	4106
	.cv_filechecksumoffset	4
	.long	127


	.long	4108
	.cv_filechecksumoffset	5
	.long	460


	.long	4110
	.cv_filechecksumoffset	3
	.long	180


	.long	4112
	.cv_filechecksumoffset	1
	.long	1692


	.long	4114
	.cv_filechecksumoffset	3
	.long	83


	.long	4116
	.cv_filechecksumoffset	7
	.long	253


	.long	4118
	.cv_filechecksumoffset	6
	.long	463


	.long	4119
	.cv_filechecksumoffset	6
	.long	632


	.long	4121
	.cv_filechecksumoffset	10
	.long	301


	.long	4122
	.cv_filechecksumoffset	10
	.long	372


	.long	4123
	.cv_filechecksumoffset	1
	.long	2475


	.long	4125
	.cv_filechecksumoffset	11
	.long	1899


	.long	4126
	.cv_filechecksumoffset	6
	.long	953


	.long	4128
	.cv_filechecksumoffset	2
	.long	1432


	.long	4130
	.cv_filechecksumoffset	12
	.long	181


	.long	4132
	.cv_filechecksumoffset	13
	.long	1240


	.long	4112
	.cv_filechecksumoffset	1
	.long	1692


	.long	4133
	.cv_filechecksumoffset	6
	.long	1037
.Ltmp60:
	.p2align	2, 0x0
	.section	.debug$S,"dr",associative,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp62-.Ltmp61
.Ltmp61:
	.short	.Ltmp64-.Ltmp63
.Ltmp63:
	.short	4422
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end0-_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind
	.long	0
	.long	0
	.long	4134
	.secrel32	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind
	.secidx	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind
	.byte	129
	.asciz	"core::ptr::drop_glue<alloc::boxed::Box<dyn$<core::any::Any,core::marker::Send>,alloc::alloc::Global> >"
	.p2align	2, 0x0
.Ltmp64:
	.short	.Ltmp66-.Ltmp65
.Ltmp65:
	.short	4114
	.long	64
	.long	0
	.long	0
	.long	8
	.long	0
	.short	0
	.long	1220624
	.p2align	2, 0x0
.Ltmp66:
	.short	.Ltmp68-.Ltmp67
.Ltmp67:
	.short	4456
	.long	1
	.long	4099
	.p2align	2, 0x0
.Ltmp68:
	.short	.Ltmp70-.Ltmp69
.Ltmp69:
	.short	4429
	.long	0
	.long	0
	.long	4099
	.cv_inline_linetable	1 2 1992 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp70:
	.short	.Ltmp72-.Ltmp71
.Ltmp71:
	.short	4429
	.long	0
	.long	0
	.long	4101
	.cv_inline_linetable	2 4 460 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp72:
	.short	.Ltmp74-.Ltmp73
.Ltmp73:
	.short	4429
	.long	0
	.long	0
	.long	4103
	.cv_inline_linetable	3 4 343 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp74:
	.short	.Ltmp76-.Ltmp75
.Ltmp75:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	4 4 219 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp76:
	.short	.Ltmp78-.Ltmp77
.Ltmp77:
	.short	4429
	.long	0
	.long	0
	.long	4106
	.cv_inline_linetable	5 4 127 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp78:
	.short	.Ltmp80-.Ltmp79
.Ltmp79:
	.short	4429
	.long	0
	.long	0
	.long	4108
	.cv_inline_linetable	6 5 460 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp80:
	.short	.Ltmp82-.Ltmp81
.Ltmp81:
	.short	4429
	.long	0
	.long	0
	.long	4110
	.cv_inline_linetable	7 3 180 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp82:
	.short	.Ltmp84-.Ltmp83
.Ltmp83:
	.short	4429
	.long	0
	.long	0
	.long	4112
	.cv_inline_linetable	8 1 1692 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp84:
	.short	2
	.short	4430
	.short	.Ltmp86-.Ltmp85
.Ltmp85:
	.short	4429
	.long	0
	.long	0
	.long	4114
	.cv_inline_linetable	9 3 83 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp86:
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
	.short	.Ltmp88-.Ltmp87
.Ltmp87:
	.short	4429
	.long	0
	.long	0
	.long	4099
	.cv_inline_linetable	10 2 1992 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp88:
	.short	.Ltmp90-.Ltmp89
.Ltmp89:
	.short	4429
	.long	0
	.long	0
	.long	4116
	.cv_inline_linetable	11 7 253 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp90:
	.short	.Ltmp92-.Ltmp91
.Ltmp91:
	.short	4429
	.long	0
	.long	0
	.long	4118
	.cv_inline_linetable	12 6 463 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp92:
	.short	.Ltmp94-.Ltmp93
.Ltmp93:
	.short	4429
	.long	0
	.long	0
	.long	4119
	.cv_inline_linetable	13 6 632 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp94:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp96-.Ltmp95
.Ltmp95:
	.short	4429
	.long	0
	.long	0
	.long	4101
	.cv_inline_linetable	14 4 460 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp96:
	.short	.Ltmp98-.Ltmp97
.Ltmp97:
	.short	4429
	.long	0
	.long	0
	.long	4103
	.cv_inline_linetable	15 4 343 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp98:
	.short	.Ltmp100-.Ltmp99
.Ltmp99:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	16 4 219 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp100:
	.short	.Ltmp102-.Ltmp101
.Ltmp101:
	.short	4429
	.long	0
	.long	0
	.long	4106
	.cv_inline_linetable	17 4 127 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp102:
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
.Ltmp62:
	.p2align	2, 0x0
	.cv_linetable	0, _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind, .Lfunc_end0
	.section	.debug$S,"dr",associative,_RNvCs1njKG4L9aB3_7___rustc18___rust_start_panic
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp104-.Ltmp103
.Ltmp103:
	.short	.Ltmp106-.Ltmp105
.Ltmp105:
	.short	4423
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end1-_RNvCs1njKG4L9aB3_7___rustc18___rust_start_panic
	.long	0
	.long	0
	.long	4136
	.secrel32	_RNvCs1njKG4L9aB3_7___rustc18___rust_start_panic
	.secidx	_RNvCs1njKG4L9aB3_7___rustc18___rust_start_panic
	.byte	137
	.asciz	"panic_unwind::__rust_start_panic"
	.p2align	2, 0x0
.Ltmp106:
	.short	.Ltmp108-.Ltmp107
.Ltmp107:
	.short	4114
	.long	40
	.long	0
	.long	0
	.long	0
	.long	0
	.short	0
	.long	1220608
	.p2align	2, 0x0
.Ltmp108:
	.short	.Ltmp110-.Ltmp109
.Ltmp109:
	.short	4456
	.long	1
	.long	4121
	.p2align	2, 0x0
.Ltmp110:
	.short	.Ltmp112-.Ltmp111
.Ltmp111:
	.short	4429
	.long	0
	.long	0
	.long	4121
	.cv_inline_linetable	19 10 301 .Lfunc_begin1 .Lfunc_end1
	.p2align	2, 0x0
.Ltmp112:
	.short	2
	.short	4430
	.short	2
	.short	4431
.Ltmp104:
	.p2align	2, 0x0
	.cv_linetable	18, _RNvCs1njKG4L9aB3_7___rustc18___rust_start_panic, .Lfunc_end1
	.section	.debug$S,"dr",associative,_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp114-.Ltmp113
.Ltmp113:
	.short	.Ltmp116-.Ltmp115
.Ltmp115:
	.short	4423
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end2-_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup
	.long	0
	.long	0
	.long	4137
	.secrel32	_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup
	.secidx	_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup
	.byte	129
	.asciz	"panic_unwind::__rust_panic_cleanup"
	.p2align	2, 0x0
.Ltmp116:
	.short	.Ltmp118-.Ltmp117
.Ltmp117:
	.short	4114
	.long	56
	.long	0
	.long	0
	.long	0
	.long	0
	.short	0
	.long	1220624
	.p2align	2, 0x0
.Ltmp118:
	.short	.Ltmp120-.Ltmp119
.Ltmp119:
	.short	4456
	.long	2
	.long	4122
	.long	4128
	.p2align	2, 0x0
.Ltmp120:
	.short	.Ltmp122-.Ltmp121
.Ltmp121:
	.short	4429
	.long	0
	.long	0
	.long	4122
	.cv_inline_linetable	21 10 372 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp122:
	.short	.Ltmp124-.Ltmp123
.Ltmp123:
	.short	4429
	.long	0
	.long	0
	.long	4123
	.cv_inline_linetable	22 1 2475 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp124:
	.short	2
	.short	4430
	.short	.Ltmp126-.Ltmp125
.Ltmp125:
	.short	4429
	.long	0
	.long	0
	.long	4125
	.cv_inline_linetable	23 11 1899 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp126:
	.short	.Ltmp128-.Ltmp127
.Ltmp127:
	.short	4429
	.long	0
	.long	0
	.long	4126
	.cv_inline_linetable	24 6 953 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp128:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp130-.Ltmp129
.Ltmp129:
	.short	4429
	.long	0
	.long	0
	.long	4128
	.cv_inline_linetable	25 2 1432 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp130:
	.short	2
	.short	4430
	.short	2
	.short	4431
.Ltmp114:
	.p2align	2, 0x0
	.cv_linetable	20, _RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup, .Lfunc_end2
	.section	.debug$S,"dr",associative,_RNvNtCsaenKx8lKFZc_12panic_unwind3imp14exception_copy.llvm.16952210977915244029
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp132-.Ltmp131
.Ltmp131:
	.short	.Ltmp134-.Ltmp133
.Ltmp133:
	.short	4423
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end3-_RNvNtCsaenKx8lKFZc_12panic_unwind3imp14exception_copy.llvm.16952210977915244029
	.long	0
	.long	0
	.long	4138
	.secrel32	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp14exception_copy.llvm.16952210977915244029
	.secidx	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp14exception_copy.llvm.16952210977915244029
	.byte	137
	.asciz	"panic_unwind::imp::exception_copy"
	.p2align	2, 0x0
.Ltmp134:
	.short	.Ltmp136-.Ltmp135
.Ltmp135:
	.short	4114
	.long	40
	.long	0
	.long	0
	.long	0
	.long	0
	.short	0
	.long	1220608
	.p2align	2, 0x0
.Ltmp136:
	.short	2
	.short	4431
.Ltmp132:
	.p2align	2, 0x0
	.cv_linetable	26, _RNvNtCsaenKx8lKFZc_12panic_unwind3imp14exception_copy.llvm.16952210977915244029, .Lfunc_end3
	.section	.debug$S,"dr",associative,_RNvNtCsaenKx8lKFZc_12panic_unwind3imp15throw_exception.llvm.16952210977915244029
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp138-.Ltmp137
.Ltmp137:
	.short	.Ltmp140-.Ltmp139
.Ltmp139:
	.short	4423
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end4-_RNvNtCsaenKx8lKFZc_12panic_unwind3imp15throw_exception.llvm.16952210977915244029
	.long	0
	.long	0
	.long	4139
	.secrel32	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp15throw_exception.llvm.16952210977915244029
	.secidx	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp15throw_exception.llvm.16952210977915244029
	.byte	137
	.asciz	"panic_unwind::imp::throw_exception"
	.p2align	2, 0x0
.Ltmp140:
	.short	.Ltmp142-.Ltmp141
.Ltmp141:
	.short	4114
	.long	72
	.long	0
	.long	0
	.long	0
	.long	0
	.short	0
	.long	1220608
	.p2align	2, 0x0
.Ltmp142:
	.short	.Ltmp144-.Ltmp143
.Ltmp143:
	.short	4456
	.long	1
	.long	4130
	.p2align	2, 0x0
.Ltmp144:
	.short	.Ltmp146-.Ltmp145
.Ltmp145:
	.short	4429
	.long	0
	.long	0
	.long	4130
	.cv_inline_linetable	28 12 181 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp146:
	.short	2
	.short	4430
	.short	2
	.short	4431
.Ltmp138:
	.p2align	2, 0x0
	.cv_linetable	27, _RNvNtCsaenKx8lKFZc_12panic_unwind3imp15throw_exception.llvm.16952210977915244029, .Lfunc_end4
	.section	.debug$S,"dr",associative,_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp148-.Ltmp147
.Ltmp147:
	.short	.Ltmp150-.Ltmp149
.Ltmp149:
	.short	4423
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end5-_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029
	.long	0
	.long	0
	.long	4140
	.secrel32	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029
	.secidx	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029
	.byte	129
	.asciz	"panic_unwind::imp::exception_cleanup"
	.p2align	2, 0x0
.Ltmp150:
	.short	.Ltmp152-.Ltmp151
.Ltmp151:
	.short	4114
	.long	56
	.long	0
	.long	0
	.long	0
	.long	0
	.short	0
	.long	1220624
	.p2align	2, 0x0
.Ltmp152:
	.short	.Ltmp154-.Ltmp153
.Ltmp153:
	.short	4456
	.long	2
	.long	4132
	.long	4133
	.p2align	2, 0x0
.Ltmp154:
	.short	.Ltmp156-.Ltmp155
.Ltmp155:
	.short	4429
	.long	0
	.long	0
	.long	4132
	.cv_inline_linetable	30 13 1240 .Lfunc_begin5 .Lfunc_end5
	.p2align	2, 0x0
.Ltmp156:
	.short	.Ltmp158-.Ltmp157
.Ltmp157:
	.short	4429
	.long	0
	.long	0
	.long	4112
	.cv_inline_linetable	31 1 1692 .Lfunc_begin5 .Lfunc_end5
	.p2align	2, 0x0
.Ltmp158:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp160-.Ltmp159
.Ltmp159:
	.short	4429
	.long	0
	.long	0
	.long	4133
	.cv_inline_linetable	32 6 1037 .Lfunc_begin5 .Lfunc_end5
	.p2align	2, 0x0
.Ltmp160:
	.short	2
	.short	4430
	.short	2
	.short	4431
.Ltmp148:
	.p2align	2, 0x0
	.cv_linetable	29, _RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029, .Lfunc_end5
	.section	.debug$S,"dr"
	.cv_filechecksums
	.cv_stringtable
	.long	241
	.long	.Ltmp162-.Ltmp161
.Ltmp161:
	.short	.Ltmp164-.Ltmp163
.Ltmp163:
	.short	4428
	.long	4144
	.p2align	2, 0x0
.Ltmp164:
.Ltmp162:
	.p2align	2, 0x0
	.section	.debug$T,"dr"
	.p2align	2, 0x0
	.long	4
	.short	0x1e
	.short	0x1605
	.long	0x0
	.asciz	"alloc::boxed::impl$10"
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
	.short	0x12
	.short	0x1601
	.long	0x1000
	.long	0x1002
	.asciz	"drop"
	.byte	243
	.byte	242
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
	.long	0x1004
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
	.long	0x1006
	.long	0x1002
	.asciz	"deallocate_impl"
	.short	0x22
	.short	0x1601
	.long	0x1006
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
	.long	0x1009
	.long	0x1002
	.asciz	"dealloc_nonnull"
	.short	0x2a
	.short	0x1605
	.long	0x0
	.asciz	"std::alloc::__default_lib_allocator"
	.short	0x1a
	.short	0x1601
	.long	0x100b
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
	.long	0x100d
	.long	0x1002
	.asciz	"dealloc"
	.short	0x12
	.short	0x1605
	.long	0x0
	.asciz	"core::ptr"
	.byte	242
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x100f
	.long	0x1002
	.asciz	"read"
	.byte	243
	.byte	242
	.byte	241
	.short	0x22
	.short	0x1605
	.long	0x0
	.asciz	"std::sys::alloc::windows"
	.byte	243
	.byte	242
	.byte	241
	.short	0x1e
	.short	0x1601
	.long	0x1011
	.long	0x1002
	.asciz	"get_process_heap"
	.byte	243
	.byte	242
	.byte	241
	.short	0x22
	.short	0x1605
	.long	0x0
	.asciz	"core::alloc::layout::Layout"
	.short	0x1a
	.short	0x1601
	.long	0x1013
	.long	0x1002
	.asciz	"for_value_raw"
	.byte	242
	.byte	241
	.short	0x12
	.short	0x1605
	.long	0x0
	.asciz	"core::mem"
	.byte	242
	.byte	241
	.short	0x1a
	.short	0x1601
	.long	0x1015
	.long	0x1002
	.asciz	"size_of_val_raw"
	.short	0x1e
	.short	0x1601
	.long	0x1015
	.long	0x1002
	.asciz	"align_of_val_raw"
	.byte	243
	.byte	242
	.byte	241
	.short	0x1a
	.short	0x1605
	.long	0x0
	.asciz	"panic_unwind::imp"
	.byte	242
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x1018
	.long	0x1002
	.asciz	"panic"
	.byte	242
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x1018
	.long	0x1002
	.asciz	"cleanup"
	.short	0xe
	.short	0x1601
	.long	0x100f
	.long	0x1002
	.asciz	"eq"
	.byte	241
	.short	0x1e
	.short	0x1605
	.long	0x0
	.asciz	"core::option::Option"
	.byte	243
	.byte	242
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x101c
	.long	0x1002
	.asciz	"take"
	.byte	243
	.byte	242
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x1015
	.long	0x1002
	.asciz	"replace"
	.short	0x1e
	.short	0x1605
	.long	0x0
	.asciz	"alloc::boxed::impl$8"
	.byte	243
	.byte	242
	.byte	241
	.short	0x16
	.short	0x1601
	.long	0x101f
	.long	0x1002
	.asciz	"into_raw"
	.byte	243
	.byte	242
	.byte	241
	.short	0x2e
	.short	0x1605
	.long	0x0
	.asciz	"core::mem::manually_drop::ManuallyDrop"
	.byte	241
	.short	0xe
	.short	0x1601
	.long	0x1021
	.long	0x1002
	.asciz	"new"
	.short	0x22
	.short	0x1605
	.long	0x0
	.asciz	"core::ptr::mut_ptr::impl$0"
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x1023
	.long	0x1002
	.asciz	"read"
	.byte	243
	.byte	242
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x1015
	.long	0x1002
	.asciz	"drop"
	.byte	243
	.byte	242
	.byte	241
	.short	0x16
	.short	0x1601
	.long	0x100f
	.long	0x1002
	.asciz	"drop_glue"
	.byte	242
	.byte	241
	.short	0x16
	.short	0x1605
	.long	0x0
	.asciz	"panic_unwind"
	.byte	243
	.byte	242
	.byte	241
	.short	0x1e
	.short	0x1601
	.long	0x1027
	.long	0x1002
	.asciz	"__rust_start_panic"
	.byte	241
	.short	0x22
	.short	0x1601
	.long	0x1027
	.long	0x1002
	.asciz	"__rust_panic_cleanup"
	.byte	243
	.byte	242
	.byte	241
	.short	0x1a
	.short	0x1601
	.long	0x1018
	.long	0x1002
	.asciz	"exception_copy"
	.byte	241
	.short	0x1a
	.short	0x1601
	.long	0x1018
	.long	0x1002
	.asciz	"throw_exception"
	.short	0x1e
	.short	0x1601
	.long	0x1018
	.long	0x1002
	.asciz	"exception_cleanup"
	.byte	242
	.byte	241
	.short	0x36
	.short	0x1605
	.long	0x0
	.asciz	"/rustc/48a229ceaefd4985c50990b14116b6d856af0985"
	.short	0x7e
	.short	0x1605
	.long	0x0
	.asciz	"/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\panic_unwind\\src\\lib.rs\\@\\panic_unwind.772da25958b8bb98-cgu.0"
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
	.long	0x102d
	.long	0x102f
	.long	0x102e
	.long	0x102f
	.long	0x102f
	.byte	242
	.byte	241
