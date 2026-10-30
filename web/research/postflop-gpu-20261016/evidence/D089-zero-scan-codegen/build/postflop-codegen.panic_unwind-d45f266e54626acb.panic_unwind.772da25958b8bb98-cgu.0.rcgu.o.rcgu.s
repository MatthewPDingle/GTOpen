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
	subq	$64, %rsp
	.seh_stackalloc 64
	leaq	64(%rsp), %rbp
	.seh_setframe %rbp, 64
	.seh_endprologue
	movq	$-2, -8(%rbp)
	movq	%rcx, -16(%rbp)
	movq	%rdx, -24(%rbp)
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
	movq	-16(%rbp), %rcx
	movq	-24(%rbp), %rax
.Ltmp3:
	cmpq	$0, 8(%rax)
	je	.LBB0_3
	.cv_file	3 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\alloc\\src\\alloc.rs" "699C02FE7844CD9490905545E503FEC56552BE2A34D50A79242852739483889B" 3
	.cv_inline_site_id 2 within 1 inlined_at 2 2000 0
	.cv_inline_site_id 3 within 2 inlined_at 3 462 0
	.cv_inline_site_id 4 within 3 inlined_at 3 344 0
	.cv_inline_site_id 5 within 4 inlined_at 3 229 0
	.cv_loc	5 3 128 0
	.seh_startepilogue
.Ltmp4:
	addq	$64, %rsp
	popq	%rbp
	.seh_endepilogue
	jmp	mi_free
.Ltmp5:
.LBB0_3:
	.cv_loc	0 1 823 0
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind@IMGREL
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind,unique,0
	.seh_endproc
	.def	"?dtor$4@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$4@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind@4HA":
.seh_proc "?dtor$4@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind@4HA"
.LBB0_4:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	64(%rdx), %rbp
	.seh_endprologue
	movq	-16(%rbp), %rcx
	movq	-24(%rbp), %rax
.Ltmp6:
	.cv_inline_site_id 6 within 0 inlined_at 1 823 0
	.cv_loc	6 2 1999 0
	cmpq	$0, 8(%rax)
	je	.LBB0_6
.Ltmp7:
	.cv_inline_site_id 7 within 6 inlined_at 2 2000 0
	.cv_inline_site_id 8 within 7 inlined_at 3 462 0
	.cv_inline_site_id 9 within 8 inlined_at 3 344 0
	.cv_inline_site_id 10 within 9 inlined_at 3 229 0
	.cv_loc	10 3 128 0
	callq	mi_free
	nop
.Ltmp8:
.LBB0_6:
	.cv_loc	0 1 823 0
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.Ltmp9:
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
	.long	56
	.long	0
	.long	1
$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind:
	.long	-1
	.long	"?dtor$4@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind@4HA"@IMGREL
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
	.cv_func_id 11
	.cv_file	4 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\panic_unwind\\src\\lib.rs" "733A5A44C3AB3829670AA736127E39AB605A1CABC51FC47FEC4CAA92698690BB" 3
	.cv_loc	11 4 99 0
.seh_proc _RNvCs1njKG4L9aB3_7___rustc18___rust_start_panic
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	32(%rsp), %rbp
	.seh_setframe %rbp, 32
	.seh_endprologue
.Ltmp10:
	.cv_loc	11 4 101 0
	callq	*32(%rdx)
.Ltmp11:
	.cv_file	5 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\panic_unwind\\src\\seh.rs" "277EB0E5BE1F8BC1B8A8401A680E379A29F643B3ABA60E50C39C789A111FBACF" 3
	.cv_inline_site_id 12 within 11 inlined_at 4 103 0
	.cv_loc	12 5 302 0
	movq	%rax, %rcx
	callq	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp15throw_exception.llvm.16952210977915244029
	ud2
.Ltmp12:
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
	.cv_func_id 13
	.cv_loc	13 4 92 0
.seh_proc _RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$48, %rsp
	.seh_stackalloc 48
	leaq	48(%rsp), %rbp
	.seh_setframe %rbp, 48
	.seh_endprologue
.Ltmp15:
	.cv_inline_site_id 14 within 13 inlined_at 4 93 0
	.cv_loc	14 5 376 0
	movq	$-2, -8(%rbp)
	testq	%rdx, %rdx
	je	.LBB2_7
.Ltmp16:
	.cv_inline_site_id 15 within 14 inlined_at 5 381 0
	.cv_loc	15 1 2476 0
	leaq	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp15TYPE_DESCRIPTOR.llvm.16952210977915244029(%rip), %rax
	cmpq	%rax, (%rdx)
.Ltmp17:
	.cv_loc	14 5 381 0
	jne	.LBB2_7
.Ltmp18:
	.cv_file	6 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\mem\\mod.rs" "538B04A5F1988AE5C50EDC376021F6DB3FE6291EBC24423BA6A747BC0D00688B" 3
	.cv_inline_site_id 16 within 14 inlined_at 5 385 0
	.cv_file	7 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\option.rs" "FC70106A756F98208E6A6A3E428310BDFA3531877CF6C6A99F39FFFA26AB2C40" 3
	.cv_inline_site_id 17 within 16 inlined_at 7 1901 0
	.cv_loc	17 6 967 0
	movq	8(%rdx), %rax
	movq	16(%rdx), %r8
.Ltmp19:
	.cv_loc	17 6 968 0
	movq	$0, 8(%rdx)
.Ltmp20:
	.cv_loc	16 7 1012 0
	testq	%rax, %rax
	je	.LBB2_3
.Ltmp21:
	.cv_inline_site_id 18 within 13 inlined_at 4 93 0
	.cv_loc	18 2 1441 0
	movq	%rax, (%rcx)
	movq	%r8, 8(%rcx)
.Ltmp22:
	.cv_loc	13 4 94 0
	movq	%rcx, %rax
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.LBB2_3:
	.cv_loc	16 7 1014 0
.Ltmp13:
.Ltmp23:
	leaq	anon.7378ff6387f5d434c287039208ce5213.1.llvm.16952210977915244029(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	nop
.Ltmp14:
	ud2
.Ltmp24:
.LBB2_7:
	callq	_RNvCs1njKG4L9aB3_7___rustc24___rust_foreign_exception
	ud2
.Ltmp25:
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
	.cv_loc	13 4 92 0
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking19panic_cannot_unwind
	ud2
.Ltmp26:
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
	.long	.Ltmp13@IMGREL
	.long	0
	.long	.Ltmp14@IMGREL
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
	.cv_func_id 19
	.cv_loc	19 5 283 0
.seh_proc _RNvNtCsaenKx8lKFZc_12panic_unwind3imp14exception_copy.llvm.16952210977915244029
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	32(%rsp), %rbp
	.seh_setframe %rbp, 32
	.seh_endprologue
.Ltmp27:
	.cv_loc	19 5 287 0
	xorl	%ecx, %ecx
	callq	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp15throw_exception.llvm.16952210977915244029
	ud2
.Ltmp28:
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
	.cv_func_id 20
	.cv_loc	20 5 305 0
.seh_proc _RNvNtCsaenKx8lKFZc_12panic_unwind3imp15throw_exception.llvm.16952210977915244029
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$64, %rsp
	.seh_stackalloc 64
	leaq	64(%rsp), %rbp
	.seh_setframe %rbp, 64
	.seh_endprologue
.Ltmp29:
	.cv_file	8 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\mem\\manually_drop.rs" "C21100B507893A11EE27B0711BE3AC3FE6CC970B96BBA55A7D3BAE5978209818" 3
	.cv_inline_site_id 21 within 20 inlined_at 5 315 0
	.cv_loc	21 8 182 0
	leaq	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp15TYPE_DESCRIPTOR.llvm.16952210977915244029(%rip), %rax
	movq	%rax, -24(%rbp)
	movq	%rcx, -16(%rbp)
	movq	%rdx, -8(%rbp)
.Ltmp30:
	.cv_loc	20 5 340 0
	leaq	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029(%rip), %rcx
	leaq	__ImageBase(%rip), %r8
	subl	%r8d, %ecx
	xchgl	%ecx, _RNvNtCsaenKx8lKFZc_12panic_unwind3imp10THROW_INFO.llvm.16952210977915244029+4(%rip)
.Ltmp31:
	.cv_loc	20 5 344 0
	leaq	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp20CATCHABLE_TYPE_ARRAY.llvm.16952210977915244029(%rip), %rcx
	subl	%r8d, %ecx
	xchgl	%ecx, _RNvNtCsaenKx8lKFZc_12panic_unwind3imp10THROW_INFO.llvm.16952210977915244029+12(%rip)
.Ltmp32:
	.cv_loc	20 5 340 0
	leaq	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp10THROW_INFO.llvm.16952210977915244029(%rip), %rdx
.Ltmp33:
	.cv_loc	20 5 348 0
	leaq	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp14CATCHABLE_TYPE.llvm.16952210977915244029(%rip), %rcx
	subl	%r8d, %ecx
	xchgl	%ecx, _RNvNtCsaenKx8lKFZc_12panic_unwind3imp20CATCHABLE_TYPE_ARRAY.llvm.16952210977915244029+4(%rip)
	.cv_loc	20 5 352 0
	subl	%r8d, %eax
	xchgl	%eax, _RNvNtCsaenKx8lKFZc_12panic_unwind3imp14CATCHABLE_TYPE.llvm.16952210977915244029+4(%rip)
.Ltmp34:
	.cv_loc	20 5 357 0
	leaq	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp14exception_copy.llvm.16952210977915244029(%rip), %rax
	subl	%r8d, %eax
	xchgl	%eax, _RNvNtCsaenKx8lKFZc_12panic_unwind3imp14CATCHABLE_TYPE.llvm.16952210977915244029+24(%rip)
	leaq	-24(%rbp), %rcx
.Ltmp35:
	.cv_loc	20 5 368 0
	callq	_CxxThrowException
	ud2
.Ltmp36:
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
	.cv_func_id 22
	.cv_loc	22 5 275 0
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
.Ltmp39:
	.cv_inline_site_id 23 within 22 inlined_at 5 277 0
	.cv_file	9 "/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\core\\src\\ptr\\mut_ptr.rs" "54527A10B3C1B7BD589C13443EB2482BA8B8D9004B8184D58BB04A553345C1A9" 3
	.cv_inline_site_id 24 within 23 inlined_at 9 1245 0
	.cv_loc	24 1 1731 0
	movq	8(%rcx), %rcx
.Ltmp40:
	.cv_loc	22 5 277 0
	testq	%rcx, %rcx
	jne	.LBB5_1
.Ltmp41:
	.cv_loc	22 5 282 0
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.LBB5_1:
.Ltmp42:
	.cv_loc	24 1 1731 0
	movq	16(%rax), %rdx
.Ltmp43:
	.cv_inline_site_id 25 within 22 inlined_at 5 278 0
	.cv_loc	25 6 1041 0
.Ltmp37:
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind
	nop
.Ltmp44:
.Ltmp38:
	.cv_loc	22 5 279 0
	callq	_RNvCs1njKG4L9aB3_7___rustc17___rust_drop_panic
	ud2
.Ltmp45:
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
	.cv_loc	22 5 275 0
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking19panic_cannot_unwind
	ud2
.Ltmp46:
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
	.long	.Ltmp37@IMGREL
	.long	0
	.long	.Ltmp38@IMGREL
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
	.long	.Ltmp48-.Ltmp47
.Ltmp47:
	.short	.Ltmp50-.Ltmp49
.Ltmp49:
	.short	4353
	.long	0
	.asciz	"S:\\GTOpen-research\\postflop-gpu-20261016\\runs\\D089-zero-scan-codegen\\build\\postflop-codegen.panic_unwind-d45f266e54626acb.panic_unwind.772da25958b8bb98-cgu.0.rcgu.o.rcgu.o"
	.p2align	2, 0x0
.Ltmp50:
	.short	.Ltmp52-.Ltmp51
.Ltmp51:
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
.Ltmp52:
.Ltmp48:
	.p2align	2, 0x0
	.long	246
	.long	.Ltmp54-.Ltmp53
.Ltmp53:
	.long	0


	.long	4099
	.cv_filechecksumoffset	2
	.long	1992


	.long	4101
	.cv_filechecksumoffset	3
	.long	460


	.long	4103
	.cv_filechecksumoffset	3
	.long	343


	.long	4104
	.cv_filechecksumoffset	3
	.long	219


	.long	4106
	.cv_filechecksumoffset	3
	.long	127


	.long	4108
	.cv_filechecksumoffset	5
	.long	301


	.long	4109
	.cv_filechecksumoffset	5
	.long	372


	.long	4111
	.cv_filechecksumoffset	1
	.long	2475


	.long	4113
	.cv_filechecksumoffset	7
	.long	1899


	.long	4115
	.cv_filechecksumoffset	6
	.long	953


	.long	4117
	.cv_filechecksumoffset	2
	.long	1432


	.long	4119
	.cv_filechecksumoffset	8
	.long	181


	.long	4121
	.cv_filechecksumoffset	9
	.long	1240


	.long	4122
	.cv_filechecksumoffset	1
	.long	1692


	.long	4123
	.cv_filechecksumoffset	6
	.long	1037
.Ltmp54:
	.p2align	2, 0x0
	.section	.debug$S,"dr",associative,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp56-.Ltmp55
.Ltmp55:
	.short	.Ltmp58-.Ltmp57
.Ltmp57:
	.short	4422
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end0-_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind
	.long	0
	.long	0
	.long	4124
	.secrel32	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind
	.secidx	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind
	.byte	129
	.asciz	"core::ptr::drop_glue<alloc::boxed::Box<dyn$<core::any::Any,core::marker::Send>,alloc::alloc::Global> >"
	.p2align	2, 0x0
.Ltmp58:
	.short	.Ltmp60-.Ltmp59
.Ltmp59:
	.short	4114
	.long	72
	.long	0
	.long	0
	.long	0
	.long	0
	.short	0
	.long	1220624
	.p2align	2, 0x0
.Ltmp60:
	.short	.Ltmp62-.Ltmp61
.Ltmp61:
	.short	4456
	.long	1
	.long	4099
	.p2align	2, 0x0
.Ltmp62:
	.short	.Ltmp64-.Ltmp63
.Ltmp63:
	.short	4429
	.long	0
	.long	0
	.long	4099
	.cv_inline_linetable	1 2 1992 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp64:
	.short	.Ltmp66-.Ltmp65
.Ltmp65:
	.short	4429
	.long	0
	.long	0
	.long	4101
	.cv_inline_linetable	2 3 460 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp66:
	.short	.Ltmp68-.Ltmp67
.Ltmp67:
	.short	4429
	.long	0
	.long	0
	.long	4103
	.cv_inline_linetable	3 3 343 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp68:
	.short	.Ltmp70-.Ltmp69
.Ltmp69:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	4 3 219 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp70:
	.short	.Ltmp72-.Ltmp71
.Ltmp71:
	.short	4429
	.long	0
	.long	0
	.long	4106
	.cv_inline_linetable	5 3 127 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp72:
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
	.short	.Ltmp74-.Ltmp73
.Ltmp73:
	.short	4429
	.long	0
	.long	0
	.long	4099
	.cv_inline_linetable	6 2 1992 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp74:
	.short	.Ltmp76-.Ltmp75
.Ltmp75:
	.short	4429
	.long	0
	.long	0
	.long	4101
	.cv_inline_linetable	7 3 460 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp76:
	.short	.Ltmp78-.Ltmp77
.Ltmp77:
	.short	4429
	.long	0
	.long	0
	.long	4103
	.cv_inline_linetable	8 3 343 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp78:
	.short	.Ltmp80-.Ltmp79
.Ltmp79:
	.short	4429
	.long	0
	.long	0
	.long	4104
	.cv_inline_linetable	9 3 219 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp80:
	.short	.Ltmp82-.Ltmp81
.Ltmp81:
	.short	4429
	.long	0
	.long	0
	.long	4106
	.cv_inline_linetable	10 3 127 .Lfunc_begin0 .Lfunc_end0
	.p2align	2, 0x0
.Ltmp82:
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
.Ltmp56:
	.p2align	2, 0x0
	.cv_linetable	0, _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECsaenKx8lKFZc_12panic_unwind, .Lfunc_end0
	.section	.debug$S,"dr",associative,_RNvCs1njKG4L9aB3_7___rustc18___rust_start_panic
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp84-.Ltmp83
.Ltmp83:
	.short	.Ltmp86-.Ltmp85
.Ltmp85:
	.short	4423
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end1-_RNvCs1njKG4L9aB3_7___rustc18___rust_start_panic
	.long	0
	.long	0
	.long	4126
	.secrel32	_RNvCs1njKG4L9aB3_7___rustc18___rust_start_panic
	.secidx	_RNvCs1njKG4L9aB3_7___rustc18___rust_start_panic
	.byte	137
	.asciz	"panic_unwind::__rust_start_panic"
	.p2align	2, 0x0
.Ltmp86:
	.short	.Ltmp88-.Ltmp87
.Ltmp87:
	.short	4114
	.long	40
	.long	0
	.long	0
	.long	0
	.long	0
	.short	0
	.long	1220608
	.p2align	2, 0x0
.Ltmp88:
	.short	.Ltmp90-.Ltmp89
.Ltmp89:
	.short	4456
	.long	1
	.long	4108
	.p2align	2, 0x0
.Ltmp90:
	.short	.Ltmp92-.Ltmp91
.Ltmp91:
	.short	4429
	.long	0
	.long	0
	.long	4108
	.cv_inline_linetable	12 5 301 .Lfunc_begin1 .Lfunc_end1
	.p2align	2, 0x0
.Ltmp92:
	.short	2
	.short	4430
	.short	2
	.short	4431
.Ltmp84:
	.p2align	2, 0x0
	.cv_linetable	11, _RNvCs1njKG4L9aB3_7___rustc18___rust_start_panic, .Lfunc_end1
	.section	.debug$S,"dr",associative,_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp94-.Ltmp93
.Ltmp93:
	.short	.Ltmp96-.Ltmp95
.Ltmp95:
	.short	4423
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end2-_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup
	.long	0
	.long	0
	.long	4127
	.secrel32	_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup
	.secidx	_RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup
	.byte	129
	.asciz	"panic_unwind::__rust_panic_cleanup"
	.p2align	2, 0x0
.Ltmp96:
	.short	.Ltmp98-.Ltmp97
.Ltmp97:
	.short	4114
	.long	56
	.long	0
	.long	0
	.long	0
	.long	0
	.short	0
	.long	1220624
	.p2align	2, 0x0
.Ltmp98:
	.short	.Ltmp100-.Ltmp99
.Ltmp99:
	.short	4456
	.long	2
	.long	4109
	.long	4117
	.p2align	2, 0x0
.Ltmp100:
	.short	.Ltmp102-.Ltmp101
.Ltmp101:
	.short	4429
	.long	0
	.long	0
	.long	4109
	.cv_inline_linetable	14 5 372 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp102:
	.short	.Ltmp104-.Ltmp103
.Ltmp103:
	.short	4429
	.long	0
	.long	0
	.long	4111
	.cv_inline_linetable	15 1 2475 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp104:
	.short	2
	.short	4430
	.short	.Ltmp106-.Ltmp105
.Ltmp105:
	.short	4429
	.long	0
	.long	0
	.long	4113
	.cv_inline_linetable	16 7 1899 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp106:
	.short	.Ltmp108-.Ltmp107
.Ltmp107:
	.short	4429
	.long	0
	.long	0
	.long	4115
	.cv_inline_linetable	17 6 953 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp108:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp110-.Ltmp109
.Ltmp109:
	.short	4429
	.long	0
	.long	0
	.long	4117
	.cv_inline_linetable	18 2 1432 .Lfunc_begin2 .Lfunc_end2
	.p2align	2, 0x0
.Ltmp110:
	.short	2
	.short	4430
	.short	2
	.short	4431
.Ltmp94:
	.p2align	2, 0x0
	.cv_linetable	13, _RNvCs1njKG4L9aB3_7___rustc20___rust_panic_cleanup, .Lfunc_end2
	.section	.debug$S,"dr",associative,_RNvNtCsaenKx8lKFZc_12panic_unwind3imp14exception_copy.llvm.16952210977915244029
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp112-.Ltmp111
.Ltmp111:
	.short	.Ltmp114-.Ltmp113
.Ltmp113:
	.short	4423
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end3-_RNvNtCsaenKx8lKFZc_12panic_unwind3imp14exception_copy.llvm.16952210977915244029
	.long	0
	.long	0
	.long	4128
	.secrel32	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp14exception_copy.llvm.16952210977915244029
	.secidx	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp14exception_copy.llvm.16952210977915244029
	.byte	137
	.asciz	"panic_unwind::imp::exception_copy"
	.p2align	2, 0x0
.Ltmp114:
	.short	.Ltmp116-.Ltmp115
.Ltmp115:
	.short	4114
	.long	40
	.long	0
	.long	0
	.long	0
	.long	0
	.short	0
	.long	1220608
	.p2align	2, 0x0
.Ltmp116:
	.short	2
	.short	4431
.Ltmp112:
	.p2align	2, 0x0
	.cv_linetable	19, _RNvNtCsaenKx8lKFZc_12panic_unwind3imp14exception_copy.llvm.16952210977915244029, .Lfunc_end3
	.section	.debug$S,"dr",associative,_RNvNtCsaenKx8lKFZc_12panic_unwind3imp15throw_exception.llvm.16952210977915244029
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp118-.Ltmp117
.Ltmp117:
	.short	.Ltmp120-.Ltmp119
.Ltmp119:
	.short	4423
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end4-_RNvNtCsaenKx8lKFZc_12panic_unwind3imp15throw_exception.llvm.16952210977915244029
	.long	0
	.long	0
	.long	4129
	.secrel32	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp15throw_exception.llvm.16952210977915244029
	.secidx	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp15throw_exception.llvm.16952210977915244029
	.byte	137
	.asciz	"panic_unwind::imp::throw_exception"
	.p2align	2, 0x0
.Ltmp120:
	.short	.Ltmp122-.Ltmp121
.Ltmp121:
	.short	4114
	.long	72
	.long	0
	.long	0
	.long	0
	.long	0
	.short	0
	.long	1220608
	.p2align	2, 0x0
.Ltmp122:
	.short	.Ltmp124-.Ltmp123
.Ltmp123:
	.short	4456
	.long	1
	.long	4119
	.p2align	2, 0x0
.Ltmp124:
	.short	.Ltmp126-.Ltmp125
.Ltmp125:
	.short	4429
	.long	0
	.long	0
	.long	4119
	.cv_inline_linetable	21 8 181 .Lfunc_begin4 .Lfunc_end4
	.p2align	2, 0x0
.Ltmp126:
	.short	2
	.short	4430
	.short	2
	.short	4431
.Ltmp118:
	.p2align	2, 0x0
	.cv_linetable	20, _RNvNtCsaenKx8lKFZc_12panic_unwind3imp15throw_exception.llvm.16952210977915244029, .Lfunc_end4
	.section	.debug$S,"dr",associative,_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp128-.Ltmp127
.Ltmp127:
	.short	.Ltmp130-.Ltmp129
.Ltmp129:
	.short	4423
	.long	0
	.long	0
	.long	0
	.long	.Lfunc_end5-_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029
	.long	0
	.long	0
	.long	4130
	.secrel32	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029
	.secidx	_RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029
	.byte	129
	.asciz	"panic_unwind::imp::exception_cleanup"
	.p2align	2, 0x0
.Ltmp130:
	.short	.Ltmp132-.Ltmp131
.Ltmp131:
	.short	4114
	.long	56
	.long	0
	.long	0
	.long	0
	.long	0
	.short	0
	.long	1220624
	.p2align	2, 0x0
.Ltmp132:
	.short	.Ltmp134-.Ltmp133
.Ltmp133:
	.short	4456
	.long	2
	.long	4121
	.long	4123
	.p2align	2, 0x0
.Ltmp134:
	.short	.Ltmp136-.Ltmp135
.Ltmp135:
	.short	4429
	.long	0
	.long	0
	.long	4121
	.cv_inline_linetable	23 9 1240 .Lfunc_begin5 .Lfunc_end5
	.p2align	2, 0x0
.Ltmp136:
	.short	.Ltmp138-.Ltmp137
.Ltmp137:
	.short	4429
	.long	0
	.long	0
	.long	4122
	.cv_inline_linetable	24 1 1692 .Lfunc_begin5 .Lfunc_end5
	.p2align	2, 0x0
.Ltmp138:
	.short	2
	.short	4430
	.short	2
	.short	4430
	.short	.Ltmp140-.Ltmp139
.Ltmp139:
	.short	4429
	.long	0
	.long	0
	.long	4123
	.cv_inline_linetable	25 6 1037 .Lfunc_begin5 .Lfunc_end5
	.p2align	2, 0x0
.Ltmp140:
	.short	2
	.short	4430
	.short	2
	.short	4431
.Ltmp128:
	.p2align	2, 0x0
	.cv_linetable	22, _RNvNtCsaenKx8lKFZc_12panic_unwind3imp17exception_cleanup.llvm.16952210977915244029, .Lfunc_end5
	.section	.debug$S,"dr"
	.cv_filechecksums
	.cv_stringtable
	.long	241
	.long	.Ltmp142-.Ltmp141
.Ltmp141:
	.short	.Ltmp144-.Ltmp143
.Ltmp143:
	.short	4428
	.long	4134
	.p2align	2, 0x0
.Ltmp144:
.Ltmp142:
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
	.short	0x1a
	.short	0x1605
	.long	0x0
	.asciz	"panic_unwind::imp"
	.byte	242
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x100b
	.long	0x1002
	.asciz	"panic"
	.byte	242
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x100b
	.long	0x1002
	.asciz	"cleanup"
	.short	0x12
	.short	0x1605
	.long	0x0
	.asciz	"core::ptr"
	.byte	242
	.byte	241
	.short	0xe
	.short	0x1601
	.long	0x100e
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
	.long	0x1010
	.long	0x1002
	.asciz	"take"
	.byte	243
	.byte	242
	.byte	241
	.short	0x12
	.short	0x1605
	.long	0x0
	.asciz	"core::mem"
	.byte	242
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x1012
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
	.long	0x1014
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
	.long	0x1016
	.long	0x1002
	.asciz	"new"
	.short	0x22
	.short	0x1605
	.long	0x0
	.asciz	"core::ptr::mut_ptr::impl$0"
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x1018
	.long	0x1002
	.asciz	"read"
	.byte	243
	.byte	242
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x100e
	.long	0x1002
	.asciz	"read"
	.byte	243
	.byte	242
	.byte	241
	.short	0x12
	.short	0x1601
	.long	0x1012
	.long	0x1002
	.asciz	"drop"
	.byte	243
	.byte	242
	.byte	241
	.short	0x16
	.short	0x1601
	.long	0x100e
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
	.long	0x101d
	.long	0x1002
	.asciz	"__rust_start_panic"
	.byte	241
	.short	0x22
	.short	0x1601
	.long	0x101d
	.long	0x1002
	.asciz	"__rust_panic_cleanup"
	.byte	243
	.byte	242
	.byte	241
	.short	0x1a
	.short	0x1601
	.long	0x100b
	.long	0x1002
	.asciz	"exception_copy"
	.byte	241
	.short	0x1a
	.short	0x1601
	.long	0x100b
	.long	0x1002
	.asciz	"throw_exception"
	.short	0x1e
	.short	0x1601
	.long	0x100b
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
	.long	0x1023
	.long	0x1025
	.long	0x1024
	.long	0x1025
	.long	0x1025
	.byte	242
	.byte	241
