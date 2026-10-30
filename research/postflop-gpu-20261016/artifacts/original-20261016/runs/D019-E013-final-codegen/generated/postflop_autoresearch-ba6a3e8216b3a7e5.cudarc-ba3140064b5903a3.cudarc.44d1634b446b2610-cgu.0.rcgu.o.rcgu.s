	.def	@feat.00;
	.scl	3;
	.type	0;
	.endef
	.globl	@feat.00
@feat.00 = 0
	.file	"cudarc.44d1634b446b2610-cgu.0"
	.def	_RINvCs5UjBoGikVie_6cudarc18panic_no_lib_foundNtNtCsfQUUnEvlYZE_5alloc6string6StringEB2_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvCs5UjBoGikVie_6cudarc18panic_no_lib_foundNtNtCsfQUUnEvlYZE_5alloc6string6StringEB2_,unique,0
	.p2align	4
_RINvCs5UjBoGikVie_6cudarc18panic_no_lib_foundNtNtCsfQUUnEvlYZE_5alloc6string6StringEB2_:
.Lfunc_begin0:
.seh_proc _RINvCs5UjBoGikVie_6cudarc18panic_no_lib_foundNtNtCsfQUUnEvlYZE_5alloc6string6StringEB2_
	subq	$104, %rsp
	.seh_stackalloc 104
	.seh_endprologue
	movq	%rcx, 40(%rsp)
	movq	%rdx, 48(%rsp)
	movq	%r8, 56(%rsp)
	movq	%r9, 64(%rsp)
	leaq	40(%rsp), %rax
	movq	%rax, 72(%rsp)
	leaq	_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtReNtB6_7Display3fmtCs5UjBoGikVie_6cudarc(%rip), %rax
	movq	%rax, 80(%rsp)
	leaq	56(%rsp), %rax
	movq	%rax, 88(%rsp)
	leaq	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRSNtNtCsfQUUnEvlYZE_5alloc6string6StringNtB6_5Debug3fmtCs5UjBoGikVie_6cudarc(%rip), %rax
	movq	%rax, 96(%rsp)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.0(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.2(%rip), %r8
	leaq	72(%rsp), %rdx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking9panic_fmt
	ud2
.Lfunc_end0:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_16cuCtxSynchronize0E0zEB13_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_16cuCtxSynchronize0E0zEB13_,unique,1
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_16cuCtxSynchronize0E0zEB13_:
.Lfunc_begin1:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_16cuCtxSynchronize0E0zEB13_
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys16cuCtxSynchronize2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB1_1
.LBB1_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB1_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys16cuCtxSynchronize2__S(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys16cuCtxSynchronize2__S+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.7(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB1_2
.Lfunc_end1:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCNtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumOPaEBW_E10initializeNCINvB2_11get_or_initNCNvBY_16cuGetErrorString0E0zEB12_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCNtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumOPaEBW_E10initializeNCINvB2_11get_or_initNCNvBY_16cuGetErrorString0E0zEB12_,unique,2
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCNtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumOPaEBW_E10initializeNCINvB2_11get_or_initNCNvBY_16cuGetErrorString0E0zEB12_:
.Lfunc_begin2:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCNtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumOPaEBW_E10initializeNCINvB2_11get_or_initNCNvBY_16cuGetErrorString0E0zEB12_
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys16cuGetErrorString2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB2_1
.LBB2_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB2_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys16cuGetErrorString2__S(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys16cuGetErrorString2__S+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.12(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB2_2
.Lfunc_end2:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB1y_13cuMemFreeHost0E0zEB1C_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB1y_13cuMemFreeHost0E0zEB1C_.llvm.1750587498003715262,unique,3
	.globl	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB1y_13cuMemFreeHost0E0zEB1C_.llvm.1750587498003715262
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB1y_13cuMemFreeHost0E0zEB1C_.llvm.1750587498003715262:
.Lfunc_begin3:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB1y_13cuMemFreeHost0E0zEB1C_.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuMemFreeHost2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB3_1
.LBB3_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB3_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuMemFreeHost2__S.llvm.1750587498003715262(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuMemFreeHost2__S.llvm.1750587498003715262+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.21.llvm.1750587498003715262(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB3_2
.Lfunc_end3:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1A_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB1A_20cuMemcpyDtoHAsync_v20E0zEB1E_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1A_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB1A_20cuMemcpyDtoHAsync_v20E0zEB1E_.llvm.1750587498003715262,unique,4
	.globl	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1A_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB1A_20cuMemcpyDtoHAsync_v20E0zEB1E_.llvm.1750587498003715262
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1A_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB1A_20cuMemcpyDtoHAsync_v20E0zEB1E_.llvm.1750587498003715262:
.Lfunc_begin4:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1A_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB1A_20cuMemcpyDtoHAsync_v20E0zEB1E_.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoHAsync_v22__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB4_1
.LBB4_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB4_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoHAsync_v22__S.llvm.1750587498003715262(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoHAsync_v22__S.llvm.1750587498003715262+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.32.llvm.1750587498003715262(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB4_2
.Lfunc_end4:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtBZ_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvBZ_11nvrtcGetPTX0E0zEB13_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtBZ_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvBZ_11nvrtcGetPTX0E0zEB13_,unique,5
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtBZ_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvBZ_11nvrtcGetPTX0E0zEB13_:
.Lfunc_begin5:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtBZ_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvBZ_11nvrtcGetPTX0E0zEB13_
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys11nvrtcGetPTX2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB5_1
.LBB5_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB5_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys11nvrtcGetPTX2__S(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys11nvrtcGetPTX2__S+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.33(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB5_2
.Lfunc_end5:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtBZ_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvBZ_18nvrtcGetProgramLog0E0zEB13_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtBZ_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvBZ_18nvrtcGetProgramLog0E0zEB13_,unique,6
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtBZ_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvBZ_18nvrtcGetProgramLog0E0zEB13_:
.Lfunc_begin6:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtBZ_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvBZ_18nvrtcGetProgramLog0E0zEB13_
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys18nvrtcGetProgramLog2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB6_1
.LBB6_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB6_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys18nvrtcGetProgramLog2__S(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys18nvrtcGetProgramLog2__S+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.37(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB6_2
.Lfunc_end6:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtBZ_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvBZ_15nvrtcGetPTXSize0E0zEB13_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtBZ_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvBZ_15nvrtcGetPTXSize0E0zEB13_,unique,7
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtBZ_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvBZ_15nvrtcGetPTXSize0E0zEB13_:
.Lfunc_begin7:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtBZ_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvBZ_15nvrtcGetPTXSize0E0zEB13_
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys15nvrtcGetPTXSize2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB7_1
.LBB7_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB7_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys15nvrtcGetPTXSize2__S(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys15nvrtcGetPTXSize2__S+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.38(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB7_2
.Lfunc_end7:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtBZ_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvBZ_22nvrtcGetProgramLogSize0E0zEB13_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtBZ_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvBZ_22nvrtcGetProgramLogSize0E0zEB13_,unique,8
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtBZ_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvBZ_22nvrtcGetProgramLogSize0E0zEB13_:
.Lfunc_begin8:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtBZ_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvBZ_22nvrtcGetProgramLogSize0E0zEB13_
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys22nvrtcGetProgramLogSize2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB8_1
.LBB8_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB8_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys22nvrtcGetProgramLogSize2__S(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys22nvrtcGetProgramLogSize2__S+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.42(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB8_2
.Lfunc_end8:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramlPPaENtBZ_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvBZ_19nvrtcCompileProgram0E0zEB13_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramlPPaENtBZ_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvBZ_19nvrtcCompileProgram0E0zEB13_,unique,9
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramlPPaENtBZ_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvBZ_19nvrtcCompileProgram0E0zEB13_:
.Lfunc_begin9:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramlPPaENtBZ_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvBZ_19nvrtcCompileProgram0E0zEB13_
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys19nvrtcCompileProgram2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB9_1
.LBB9_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB9_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys19nvrtcCompileProgram2__S(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys19nvrtcCompileProgram2__S+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.45(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB9_2
.Lfunc_end9:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_17cuEventDestroy_v20E0zEB13_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_17cuEventDestroy_v20E0zEB13_.llvm.1750587498003715262,unique,10
	.globl	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_17cuEventDestroy_v20E0zEB13_.llvm.1750587498003715262
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_17cuEventDestroy_v20E0zEB13_.llvm.1750587498003715262:
.Lfunc_begin10:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_17cuEventDestroy_v20E0zEB13_.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuEventDestroy_v22__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB10_1
.LBB10_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB10_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuEventDestroy_v22__S.llvm.1750587498003715262(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuEventDestroy_v22__S.llvm.1750587498003715262+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.52.llvm.1750587498003715262(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB10_2
.Lfunc_end10:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stONtBZ_11CUstream_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_13cuEventRecord0E0zEB13_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stONtBZ_11CUstream_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_13cuEventRecord0E0zEB13_.llvm.1750587498003715262,unique,11
	.globl	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stONtBZ_11CUstream_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_13cuEventRecord0E0zEB13_.llvm.1750587498003715262
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stONtBZ_11CUstream_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_13cuEventRecord0E0zEB13_.llvm.1750587498003715262:
.Lfunc_begin11:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stONtBZ_11CUstream_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_13cuEventRecord0E0zEB13_.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuEventRecord2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB11_1
.LBB11_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB11_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuEventRecord2__S.llvm.1750587498003715262(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuEventRecord2__S.llvm.1750587498003715262+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.54.llvm.1750587498003715262(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB11_2
.Lfunc_end11:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUgraph_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_14cuGraphDestroy0E0zEB13_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUgraph_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_14cuGraphDestroy0E0zEB13_.llvm.1750587498003715262,unique,12
	.globl	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUgraph_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_14cuGraphDestroy0E0zEB13_.llvm.1750587498003715262
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUgraph_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_14cuGraphDestroy0E0zEB13_.llvm.1750587498003715262:
.Lfunc_begin12:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUgraph_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_14cuGraphDestroy0E0zEB13_.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuGraphDestroy2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB12_1
.LBB12_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB12_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuGraphDestroy2__S.llvm.1750587498003715262(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuGraphDestroy2__S.llvm.1750587498003715262+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.56.llvm.1750587498003715262(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB12_2
.Lfunc_end12:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_18cuStreamDestroy_v20E0zEB13_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_18cuStreamDestroy_v20E0zEB13_,unique,13
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_18cuStreamDestroy_v20E0zEB13_:
.Lfunc_begin13:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_18cuStreamDestroy_v20E0zEB13_
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuStreamDestroy_v22__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB13_1
.LBB13_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB13_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuStreamDestroy_v22__S(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuStreamDestroy_v22__S+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.70(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB13_2
.Lfunc_end13:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_19cuStreamSynchronize0E0zEB13_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_19cuStreamSynchronize0E0zEB13_.llvm.1750587498003715262,unique,14
	.globl	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_19cuStreamSynchronize0E0zEB13_.llvm.1750587498003715262
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_19cuStreamSynchronize0E0zEB13_.llvm.1750587498003715262:
.Lfunc_begin14:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_19cuStreamSynchronize0E0zEB13_.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys19cuStreamSynchronize2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB14_1
.LBB14_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB14_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys19cuStreamSynchronize2__S.llvm.1750587498003715262(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys19cuStreamSynchronize2__S.llvm.1750587498003715262+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.71.llvm.1750587498003715262(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB14_2
.Lfunc_end14:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stNtBZ_24CUstreamCaptureMode_enumENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_23cuStreamBeginCapture_v20E0zEB13_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stNtBZ_24CUstreamCaptureMode_enumENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_23cuStreamBeginCapture_v20E0zEB13_.llvm.1750587498003715262,unique,15
	.globl	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stNtBZ_24CUstreamCaptureMode_enumENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_23cuStreamBeginCapture_v20E0zEB13_.llvm.1750587498003715262
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stNtBZ_24CUstreamCaptureMode_enumENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_23cuStreamBeginCapture_v20E0zEB13_.llvm.1750587498003715262:
.Lfunc_begin15:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stNtBZ_24CUstreamCaptureMode_enumENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_23cuStreamBeginCapture_v20E0zEB13_.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys23cuStreamBeginCapture_v22__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB15_1
.LBB15_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB15_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys23cuStreamBeginCapture_v22__S.llvm.1750587498003715262(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys23cuStreamBeginCapture_v22__S.llvm.1750587498003715262+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.76.llvm.1750587498003715262(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB15_2
.Lfunc_end15:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stONtBZ_10CUevent_stmENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_17cuStreamWaitEvent0E0zEB13_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stONtBZ_10CUevent_stmENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_17cuStreamWaitEvent0E0zEB13_.llvm.1750587498003715262,unique,16
	.globl	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stONtBZ_10CUevent_stmENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_17cuStreamWaitEvent0E0zEB13_.llvm.1750587498003715262
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stONtBZ_10CUevent_stmENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_17cuStreamWaitEvent0E0zEB13_.llvm.1750587498003715262:
.Lfunc_begin16:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stONtBZ_10CUevent_stmENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_17cuStreamWaitEvent0E0zEB13_.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuStreamWaitEvent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB16_1
.LBB16_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB16_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuStreamWaitEvent2__S.llvm.1750587498003715262(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuStreamWaitEvent2__S.llvm.1750587498003715262+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.77.llvm.1750587498003715262(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB16_2
.Lfunc_end16:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stOONtBZ_10CUgraph_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_18cuStreamEndCapture0E0zEB13_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stOONtBZ_10CUgraph_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_18cuStreamEndCapture0E0zEB13_,unique,17
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stOONtBZ_10CUgraph_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_18cuStreamEndCapture0E0zEB13_:
.Lfunc_begin17:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stOONtBZ_10CUgraph_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_18cuStreamEndCapture0E0zEB13_
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuStreamEndCapture2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB17_1
.LBB17_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB17_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuStreamEndCapture2__S(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuStreamEndCapture2__S+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.82(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB17_2
.Lfunc_end17:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_18cuGraphExecDestroy0E0zEB13_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_18cuGraphExecDestroy0E0zEB13_.llvm.1750587498003715262,unique,18
	.globl	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_18cuGraphExecDestroy0E0zEB13_.llvm.1750587498003715262
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_18cuGraphExecDestroy0E0zEB13_.llvm.1750587498003715262:
.Lfunc_begin18:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_18cuGraphExecDestroy0E0zEB13_.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuGraphExecDestroy2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB18_1
.LBB18_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB18_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuGraphExecDestroy2__S.llvm.1750587498003715262(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuGraphExecDestroy2__S.llvm.1750587498003715262+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.117.llvm.1750587498003715262(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB18_2
.Lfunc_end18:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtBZ_11CUstream_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_13cuGraphLaunch0E0zEB13_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtBZ_11CUstream_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_13cuGraphLaunch0E0zEB13_.llvm.1750587498003715262,unique,19
	.globl	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtBZ_11CUstream_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_13cuGraphLaunch0E0zEB13_.llvm.1750587498003715262
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtBZ_11CUstream_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_13cuGraphLaunch0E0zEB13_.llvm.1750587498003715262:
.Lfunc_begin19:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtBZ_11CUstream_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_13cuGraphLaunch0E0zEB13_.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuGraphLaunch2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB19_1
.LBB19_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB19_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuGraphLaunch2__S.llvm.1750587498003715262(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuGraphLaunch2__S.llvm.1750587498003715262+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.119.llvm.1750587498003715262(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB19_2
.Lfunc_end19:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxDestroy_v20E0zEB13_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxDestroy_v20E0zEB13_,unique,20
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxDestroy_v20E0zEB13_:
.Lfunc_begin20:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxDestroy_v20E0zEB13_
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxDestroy_v22__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB20_1
.LBB20_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB20_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxDestroy_v22__S(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxDestroy_v22__S+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.213(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB20_2
.Lfunc_end20:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxSetCurrent0E0zEB13_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxSetCurrent0E0zEB13_.llvm.1750587498003715262,unique,21
	.globl	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxSetCurrent0E0zEB13_.llvm.1750587498003715262
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxSetCurrent0E0zEB13_.llvm.1750587498003715262:
.Lfunc_begin21:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxSetCurrent0E0zEB13_.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB21_1
.LBB21_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB21_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.214.llvm.1750587498003715262(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB21_2
.Lfunc_end21:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_14cuModuleUnload0E0zEB13_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_14cuModuleUnload0E0zEB13_.llvm.1750587498003715262,unique,22
	.globl	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_14cuModuleUnload0E0zEB13_.llvm.1750587498003715262
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_14cuModuleUnload0E0zEB13_.llvm.1750587498003715262:
.Lfunc_begin22:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_14cuModuleUnload0E0zEB13_.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuModuleUnload2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB22_1
.LBB22_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB22_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuModuleUnload2__S.llvm.1750587498003715262(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuModuleUnload2__S.llvm.1750587498003715262+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.224.llvm.1750587498003715262(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB22_2
.Lfunc_end22:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stmmmmmmmONtBZ_11CUstream_stOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidB29_ENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_14cuLaunchKernel0E0zEB13_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stmmmmmmmONtBZ_11CUstream_stOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidB29_ENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_14cuLaunchKernel0E0zEB13_.llvm.1750587498003715262,unique,23
	.globl	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stmmmmmmmONtBZ_11CUstream_stOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidB29_ENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_14cuLaunchKernel0E0zEB13_.llvm.1750587498003715262
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stmmmmmmmONtBZ_11CUstream_stOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidB29_ENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_14cuLaunchKernel0E0zEB13_.llvm.1750587498003715262:
.Lfunc_begin23:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stmmmmmmmONtBZ_11CUstream_stOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidB29_ENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_14cuLaunchKernel0E0zEB13_.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuLaunchKernel2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB23_1
.LBB23_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB23_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuLaunchKernel2__S.llvm.1750587498003715262(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuLaunchKernel2__S.llvm.1750587498003715262+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.240.llvm.1750587498003715262(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB23_2
.Lfunc_end23:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidjmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB1B_14cuMemHostAlloc0E0zEB1F_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidjmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB1B_14cuMemHostAlloc0E0zEB1F_.llvm.1750587498003715262,unique,24
	.globl	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidjmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB1B_14cuMemHostAlloc0E0zEB1F_.llvm.1750587498003715262
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidjmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB1B_14cuMemHostAlloc0E0zEB1F_.llvm.1750587498003715262:
.Lfunc_begin24:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidjmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB1B_14cuMemHostAlloc0E0zEB1F_.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuMemHostAlloc2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB24_1
.LBB24_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB24_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuMemHostAlloc2__S.llvm.1750587498003715262(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuMemHostAlloc2__S.llvm.1750587498003715262+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.249.llvm.1750587498003715262(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB24_2
.Lfunc_end24:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramENtB10_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvB10_19nvrtcDestroyProgram0E0zEB14_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramENtB10_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvB10_19nvrtcDestroyProgram0E0zEB14_,unique,25
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramENtB10_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvB10_19nvrtcDestroyProgram0E0zEB14_:
.Lfunc_begin25:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramENtB10_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvB10_19nvrtcDestroyProgram0E0zEB14_
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys19nvrtcDestroyProgram2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB25_1
.LBB25_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB25_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys19nvrtcDestroyProgram2__S(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys19nvrtcDestroyProgram2__S+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.250(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB25_2
.Lfunc_end25:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramPaB1P_lPB1P_B1W_ENtB10_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvB10_18nvrtcCreateProgram0E0zEB14_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramPaB1P_lPB1P_B1W_ENtB10_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvB10_18nvrtcCreateProgram0E0zEB14_.llvm.1750587498003715262,unique,26
	.globl	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramPaB1P_lPB1P_B1W_ENtB10_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvB10_18nvrtcCreateProgram0E0zEB14_.llvm.1750587498003715262
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramPaB1P_lPB1P_B1W_ENtB10_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvB10_18nvrtcCreateProgram0E0zEB14_.llvm.1750587498003715262:
.Lfunc_begin26:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramPaB1P_lPB1P_B1W_ENtB10_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvB10_18nvrtcCreateProgram0E0zEB14_.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys18nvrtcCreateProgram2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB26_1
.LBB26_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB26_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys18nvrtcCreateProgram2__S.llvm.1750587498003715262(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys18nvrtcCreateProgram2__S.llvm.1750587498003715262+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.251.llvm.1750587498003715262(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB26_2
.Lfunc_end26:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stmENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_13cuEventCreate0E0zEB14_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stmENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_13cuEventCreate0E0zEB14_.llvm.1750587498003715262,unique,27
	.globl	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stmENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_13cuEventCreate0E0zEB14_.llvm.1750587498003715262
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stmENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_13cuEventCreate0E0zEB14_.llvm.1750587498003715262:
.Lfunc_begin27:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stmENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_13cuEventCreate0E0zEB14_.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuEventCreate2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB27_1
.LBB27_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB27_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuEventCreate2__S.llvm.1750587498003715262(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuEventCreate2__S.llvm.1750587498003715262+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.260.llvm.1750587498003715262(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB27_2
.Lfunc_end27:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stmENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_14cuStreamCreate0E0zEB14_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stmENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_14cuStreamCreate0E0zEB14_,unique,28
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stmENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_14cuStreamCreate0E0zEB14_:
.Lfunc_begin28:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stmENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_14cuStreamCreate0E0zEB14_
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuStreamCreate2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB28_1
.LBB28_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB28_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuStreamCreate2__S(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuStreamCreate2__S+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.264(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB28_2
.Lfunc_end28:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB10_10CUgraph_styENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_27cuGraphInstantiateWithFlags0E0zEB14_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB10_10CUgraph_styENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_27cuGraphInstantiateWithFlags0E0zEB14_,unique,29
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB10_10CUgraph_styENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_27cuGraphInstantiateWithFlags0E0zEB14_:
.Lfunc_begin29:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB10_10CUgraph_styENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_27cuGraphInstantiateWithFlags0E0zEB14_
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys27cuGraphInstantiateWithFlags2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB29_1
.LBB29_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB29_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys27cuGraphInstantiateWithFlags2__S(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys27cuGraphInstantiateWithFlags2__S+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.272(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB29_2
.Lfunc_end29:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_15cuCtxGetCurrent0E0zEB14_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_15cuCtxGetCurrent0E0zEB14_.llvm.1750587498003715262,unique,30
	.globl	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_15cuCtxGetCurrent0E0zEB14_.llvm.1750587498003715262
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_15cuCtxGetCurrent0E0zEB14_.llvm.1750587498003715262:
.Lfunc_begin30:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_15cuCtxGetCurrent0E0zEB14_.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB30_1
.LBB30_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB30_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.300.llvm.1750587498003715262(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB30_2
.Lfunc_end30:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stlENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_24cuDevicePrimaryCtxRetain0E0zEB14_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stlENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_24cuDevicePrimaryCtxRetain0E0zEB14_,unique,31
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stlENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_24cuDevicePrimaryCtxRetain0E0zEB14_:
.Lfunc_begin31:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stlENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_24cuDevicePrimaryCtxRetain0E0zEB14_
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys24cuDevicePrimaryCtxRetain2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB31_1
.LBB31_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB31_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys24cuDevicePrimaryCtxRetain2__S(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys24cuDevicePrimaryCtxRetain2__S+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.305(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB31_2
.Lfunc_end31:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_16cuModuleLoadData0E0zEB14_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_16cuModuleLoadData0E0zEB14_,unique,32
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_16cuModuleLoadData0E0zEB14_:
.Lfunc_begin32:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_16cuModuleLoadData0E0zEB14_
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys16cuModuleLoadData2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB32_1
.LBB32_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB32_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys16cuModuleLoadData2__S(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys16cuModuleLoadData2__S+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.313(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB32_2
.Lfunc_end32:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPaENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_12cuModuleLoad0E0zEB14_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPaENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_12cuModuleLoad0E0zEB14_,unique,33
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPaENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_12cuModuleLoad0E0zEB14_:
.Lfunc_begin33:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPaENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_12cuModuleLoad0E0zEB14_
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys12cuModuleLoad2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB33_1
.LBB33_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB33_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys12cuModuleLoad2__S(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys12cuModuleLoad2__S+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.316(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB33_2
.Lfunc_end33:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stONtB10_8CUmod_stPaENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_19cuModuleGetFunction0E0zEB14_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stONtB10_8CUmod_stPaENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_19cuModuleGetFunction0E0zEB14_.llvm.1750587498003715262,unique,34
	.globl	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stONtB10_8CUmod_stPaENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_19cuModuleGetFunction0E0zEB14_.llvm.1750587498003715262
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stONtB10_8CUmod_stPaENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_19cuModuleGetFunction0E0zEB14_.llvm.1750587498003715262:
.Lfunc_begin34:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stONtB10_8CUmod_stPaENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_19cuModuleGetFunction0E0zEB14_.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys19cuModuleGetFunction2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB34_1
.LBB34_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB34_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys19cuModuleGetFunction2__S.llvm.1750587498003715262(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys19cuModuleGetFunction2__S.llvm.1750587498003715262+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.317.llvm.1750587498003715262(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB34_2
.Lfunc_end34:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOlNtNtNtCs5UjBoGikVie_6cudarc6driver3sys23CUdevice_attribute_enumlENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_20cuDeviceGetAttribute0E0zEB14_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOlNtNtNtCs5UjBoGikVie_6cudarc6driver3sys23CUdevice_attribute_enumlENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_20cuDeviceGetAttribute0E0zEB14_.llvm.1750587498003715262,unique,35
	.globl	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOlNtNtNtCs5UjBoGikVie_6cudarc6driver3sys23CUdevice_attribute_enumlENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_20cuDeviceGetAttribute0E0zEB14_.llvm.1750587498003715262
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOlNtNtNtCs5UjBoGikVie_6cudarc6driver3sys23CUdevice_attribute_enumlENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_20cuDeviceGetAttribute0E0zEB14_.llvm.1750587498003715262:
.Lfunc_begin35:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOlNtNtNtCs5UjBoGikVie_6cudarc6driver3sys23CUdevice_attribute_enumlENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_20cuDeviceGetAttribute0E0zEB14_.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuDeviceGetAttribute2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB35_1
.LBB35_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB35_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuDeviceGetAttribute2__S.llvm.1750587498003715262(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuDeviceGetAttribute2__S.llvm.1750587498003715262+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.350.llvm.1750587498003715262(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB35_2
.Lfunc_end35:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOllENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_11cuDeviceGet0E0zEB16_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOllENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_11cuDeviceGet0E0zEB16_,unique,36
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOllENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_11cuDeviceGet0E0zEB16_:
.Lfunc_begin36:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOllENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_11cuDeviceGet0E0zEB16_
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys11cuDeviceGet2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB36_1
.LBB36_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB36_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys11cuDeviceGet2__S(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys11cuDeviceGet2__S+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.361(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB36_2
.Lfunc_end36:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOyjENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_13cuMemAlloc_v20E0zEB16_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOyjENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_13cuMemAlloc_v20E0zEB16_.llvm.1750587498003715262,unique,37
	.globl	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOyjENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_13cuMemAlloc_v20E0zEB16_.llvm.1750587498003715262
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOyjENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_13cuMemAlloc_v20E0zEB16_.llvm.1750587498003715262:
.Lfunc_begin37:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOyjENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_13cuMemAlloc_v20E0zEB16_.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuMemAlloc_v22__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB37_1
.LBB37_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB37_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuMemAlloc_v22__S.llvm.1750587498003715262(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuMemAlloc_v22__S.llvm.1750587498003715262+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.386.llvm.1750587498003715262(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB37_2
.Lfunc_end37:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB12_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_15cuMemAllocAsync0E0zEB16_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB12_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_15cuMemAllocAsync0E0zEB16_.llvm.1750587498003715262,unique,38
	.globl	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB12_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_15cuMemAllocAsync0E0zEB16_.llvm.1750587498003715262
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB12_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_15cuMemAllocAsync0E0zEB16_.llvm.1750587498003715262:
.Lfunc_begin38:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB12_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_15cuMemAllocAsync0E0zEB16_.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuMemAllocAsync2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB38_1
.LBB38_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB38_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuMemAllocAsync2__S.llvm.1750587498003715262(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuMemAllocAsync2__S.llvm.1750587498003715262+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.387.llvm.1750587498003715262(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB38_2
.Lfunc_end38:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKClENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_28cuDevicePrimaryCtxRelease_v20E0zEB14_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKClENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_28cuDevicePrimaryCtxRelease_v20E0zEB14_,unique,39
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKClENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_28cuDevicePrimaryCtxRelease_v20E0zEB14_:
.Lfunc_begin39:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKClENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_28cuDevicePrimaryCtxRelease_v20E0zEB14_
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys28cuDevicePrimaryCtxRelease_v22__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB39_1
.LBB39_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB39_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys28cuDevicePrimaryCtxRelease_v22__S(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys28cuDevicePrimaryCtxRelease_v22__S+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.407(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB39_2
.Lfunc_end39:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_6cuInit0E0zEB14_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_6cuInit0E0zEB14_,unique,40
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_6cuInit0E0zEB14_:
.Lfunc_begin40:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_6cuInit0E0zEB14_
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys6cuInit2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB40_1
.LBB40_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB40_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys6cuInit2__S(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys6cuInit2__S+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.417(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB40_2
.Lfunc_end40:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_12cuMemFree_v20E0zEB14_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_12cuMemFree_v20E0zEB14_.llvm.1750587498003715262,unique,41
	.globl	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_12cuMemFree_v20E0zEB14_.llvm.1750587498003715262
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_12cuMemFree_v20E0zEB14_.llvm.1750587498003715262:
.Lfunc_begin41:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_12cuMemFree_v20E0zEB14_.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys12cuMemFree_v22__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB41_1
.LBB41_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB41_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys12cuMemFree_v22__S.llvm.1750587498003715262(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys12cuMemFree_v22__S.llvm.1750587498003715262+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.422.llvm.1750587498003715262(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB41_2
.Lfunc_end41:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_14cuMemFreeAsync0E0zEB14_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_14cuMemFreeAsync0E0zEB14_.llvm.1750587498003715262,unique,42
	.globl	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_14cuMemFreeAsync0E0zEB14_.llvm.1750587498003715262
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_14cuMemFreeAsync0E0zEB14_.llvm.1750587498003715262:
.Lfunc_begin42:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_14cuMemFreeAsync0E0zEB14_.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuMemFreeAsync2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB42_1
.LBB42_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB42_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuMemFreeAsync2__S.llvm.1750587498003715262(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuMemFreeAsync2__S.llvm.1750587498003715262+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.428.llvm.1750587498003715262(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB42_2
.Lfunc_end42:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_styBX_jONtB10_11CUstream_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_17cuMemcpyPeerAsync0E0zEB14_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_styBX_jONtB10_11CUstream_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_17cuMemcpyPeerAsync0E0zEB14_.llvm.1750587498003715262,unique,43
	.globl	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_styBX_jONtB10_11CUstream_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_17cuMemcpyPeerAsync0E0zEB14_.llvm.1750587498003715262
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_styBX_jONtB10_11CUstream_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_17cuMemcpyPeerAsync0E0zEB14_.llvm.1750587498003715262:
.Lfunc_begin43:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_styBX_jONtB10_11CUstream_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_17cuMemcpyPeerAsync0E0zEB14_.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuMemcpyPeerAsync2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB43_1
.LBB43_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB43_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuMemcpyPeerAsync2__S.llvm.1750587498003715262(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuMemcpyPeerAsync2__S.llvm.1750587498003715262+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.430.llvm.1750587498003715262(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB43_2
.Lfunc_end43:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1A_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB1A_20cuMemcpyHtoDAsync_v20E0zEB1E_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1A_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB1A_20cuMemcpyHtoDAsync_v20E0zEB1E_.llvm.1750587498003715262,unique,44
	.globl	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1A_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB1A_20cuMemcpyHtoDAsync_v20E0zEB1E_.llvm.1750587498003715262
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1A_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB1A_20cuMemcpyHtoDAsync_v20E0zEB1E_.llvm.1750587498003715262:
.Lfunc_begin44:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1A_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB1A_20cuMemcpyHtoDAsync_v20E0zEB1E_.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyHtoDAsync_v22__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB44_1
.LBB44_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB44_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyHtoDAsync_v22__S.llvm.1750587498003715262(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyHtoDAsync_v22__S.llvm.1750587498003715262+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.432.llvm.1750587498003715262(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB44_2
.Lfunc_end44:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyhjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB12_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_15cuMemsetD8Async0E0zEB16_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyhjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB12_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_15cuMemsetD8Async0E0zEB16_.llvm.1750587498003715262,unique,45
	.globl	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyhjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB12_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_15cuMemsetD8Async0E0zEB16_.llvm.1750587498003715262
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyhjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB12_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_15cuMemsetD8Async0E0zEB16_.llvm.1750587498003715262:
.Lfunc_begin45:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyhjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB12_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_15cuMemsetD8Async0E0zEB16_.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuMemsetD8Async2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB45_1
.LBB45_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB45_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuMemsetD8Async2__S.llvm.1750587498003715262(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuMemsetD8Async2__S.llvm.1750587498003715262+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.434.llvm.1750587498003715262(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB45_2
.Lfunc_end45:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB12_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_20cuMemcpyDtoDAsync_v20E0zEB16_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB12_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_20cuMemcpyDtoDAsync_v20E0zEB16_.llvm.1750587498003715262,unique,46
	.globl	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB12_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_20cuMemcpyDtoDAsync_v20E0zEB16_.llvm.1750587498003715262
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB12_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_20cuMemcpyDtoDAsync_v20E0zEB16_.llvm.1750587498003715262:
.Lfunc_begin46:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB12_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_20cuMemcpyDtoDAsync_v20E0zEB16_.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoDAsync_v22__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB46_1
.LBB46_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB46_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoDAsync_v22__S.llvm.1750587498003715262(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoDAsync_v22__S.llvm.1750587498003715262+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.460.llvm.1750587498003715262(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB46_2
.Lfunc_end46:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zEB2f_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zEB2f_,unique,47
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zEB2f_:
.Lfunc_begin47:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zEB2f_
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB47_1
.LBB47_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB47_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib3LIB(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib3LIB+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.461(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB47_2
.Lfunc_end47:
	.seh_endproc

	.def	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_,unique,48
_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_:
.Lfunc_begin48:
.seh_proc _RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB48_1
.LBB48_2:
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.LBB48_1:
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rax
	leaq	56(%rsp), %rcx
	movq	%rax, (%rcx)
	leaq	47(%rsp), %rax
	movq	%rax, 8(%rcx)
	leaq	48(%rsp), %r8
	movq	%rcx, (%r8)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.462(%rip), %r9
	movb	$1, %dl
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	jmp	.LBB48_2
.Lfunc_end48:
	.seh_endproc

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueANtNtCsfQUUnEvlYZE_5alloc6string6Stringj11_ECs5UjBoGikVie_6cudarc;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueANtNtCsfQUUnEvlYZE_5alloc6string6Stringj11_ECs5UjBoGikVie_6cudarc,unique,49
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueANtNtCsfQUUnEvlYZE_5alloc6string6Stringj11_ECs5UjBoGikVie_6cudarc:
.Lfunc_begin49:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueANtNtCsfQUUnEvlYZE_5alloc6string6Stringj11_ECs5UjBoGikVie_6cudarc
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	%rcx, %rsi
	cmpq	$0, (%rcx)
	je	.LBB49_2
	movq	8(%rsi), %rcx
	callq	mi_free
.LBB49_2:
	cmpq	$0, 24(%rsi)
	je	.LBB49_4
	movq	32(%rsi), %rcx
	callq	mi_free
.LBB49_4:
	cmpq	$0, 48(%rsi)
	je	.LBB49_6
	movq	56(%rsi), %rcx
	callq	mi_free
.LBB49_6:
	cmpq	$0, 72(%rsi)
	je	.LBB49_8
	movq	80(%rsi), %rcx
	callq	mi_free
.LBB49_8:
	cmpq	$0, 96(%rsi)
	je	.LBB49_10
	movq	104(%rsi), %rcx
	callq	mi_free
.LBB49_10:
	cmpq	$0, 120(%rsi)
	je	.LBB49_12
	movq	128(%rsi), %rcx
	callq	mi_free
.LBB49_12:
	cmpq	$0, 144(%rsi)
	je	.LBB49_14
	movq	152(%rsi), %rcx
	callq	mi_free
.LBB49_14:
	cmpq	$0, 168(%rsi)
	je	.LBB49_16
	movq	176(%rsi), %rcx
	callq	mi_free
.LBB49_16:
	cmpq	$0, 192(%rsi)
	je	.LBB49_18
	movq	200(%rsi), %rcx
	callq	mi_free
.LBB49_18:
	cmpq	$0, 216(%rsi)
	je	.LBB49_20
	movq	224(%rsi), %rcx
	callq	mi_free
.LBB49_20:
	cmpq	$0, 240(%rsi)
	je	.LBB49_22
	movq	248(%rsi), %rcx
	callq	mi_free
.LBB49_22:
	cmpq	$0, 264(%rsi)
	je	.LBB49_24
	movq	272(%rsi), %rcx
	callq	mi_free
.LBB49_24:
	cmpq	$0, 288(%rsi)
	je	.LBB49_26
	movq	296(%rsi), %rcx
	callq	mi_free
.LBB49_26:
	cmpq	$0, 312(%rsi)
	je	.LBB49_28
	movq	320(%rsi), %rcx
	callq	mi_free
.LBB49_28:
	cmpq	$0, 336(%rsi)
	je	.LBB49_30
	movq	344(%rsi), %rcx
	callq	mi_free
.LBB49_30:
	cmpq	$0, 360(%rsi)
	je	.LBB49_32
	movq	368(%rsi), %rcx
	callq	mi_free
.LBB49_32:
	cmpq	$0, 384(%rsi)
	je	.LBB49_33
	movq	392(%rsi), %rcx
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	jmp	mi_free
.LBB49_33:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end49:
	.seh_endproc

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecNtNtBG_6string6StringEECs5UjBoGikVie_6cudarc;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecNtNtBG_6string6StringEECs5UjBoGikVie_6cudarc,unique,50
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecNtNtBG_6string6StringEECs5UjBoGikVie_6cudarc:
.Lfunc_begin50:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecNtNtBG_6string6StringEECs5UjBoGikVie_6cudarc
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	%rcx, %rdi
	movq	8(%rcx), %rsi
	movq	16(%rcx), %rbx
	testq	%rbx, %rbx
	je	.LBB50_5
	leaq	8(%rsi), %r14
	jmp	.LBB50_2
	.p2align	4
.LBB50_4:
	addq	$24, %r14
	decq	%rbx
	je	.LBB50_5
.LBB50_2:
	cmpq	$0, -8(%r14)
	je	.LBB50_4
	movq	(%r14), %rcx
	callq	mi_free
	jmp	.LBB50_4
.LBB50_5:
	cmpq	$0, (%rdi)
	je	.LBB50_6
	movq	%rsi, %rcx
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	jmp	mi_free
.LBB50_6:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.Lfunc_end50:
	.seh_endproc

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecNtNtNtBG_3ffi5c_str7CStringEECs5UjBoGikVie_6cudarc;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecNtNtNtBG_3ffi5c_str7CStringEECs5UjBoGikVie_6cudarc,unique,51
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecNtNtNtBG_3ffi5c_str7CStringEECs5UjBoGikVie_6cudarc:
.Lfunc_begin51:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecNtNtNtBG_3ffi5c_str7CStringEECs5UjBoGikVie_6cudarc
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	%rcx, %rdi
	movq	8(%rcx), %rsi
	movq	16(%rcx), %rbx
	testq	%rbx, %rbx
	je	.LBB51_5
	leaq	8(%rsi), %r14
	jmp	.LBB51_2
	.p2align	4
.LBB51_4:
	addq	$16, %r14
	decq	%rbx
	je	.LBB51_5
.LBB51_2:
	movq	-8(%r14), %rcx
	cmpq	$0, (%r14)
	movb	$0, (%rcx)
	je	.LBB51_4
	callq	mi_free
	jmp	.LBB51_4
.LBB51_5:
	cmpq	$0, (%rdi)
	je	.LBB51_6
	movq	%rsi, %rcx
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	jmp	mi_free
.LBB51_6:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.Lfunc_end51:
	.seh_endproc

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaModuleEEB1m_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaModuleEEB1m_,unique,52
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaModuleEEB1m_:
.Lfunc_begin52:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaModuleEEB1m_
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$64, %rsp
	.seh_stackalloc 64
	leaq	64(%rsp), %rbp
	.seh_setframe %rbp, 64
	.seh_endprologue
	movq	$-2, -8(%rbp)
	movq	%rcx, %rsi
	leaq	16(%rcx), %rax
	movq	%rax, -24(%rbp)
	movq	16(%rcx), %rcx
	xorl	%eax, %eax
	xchgl	%eax, 44(%rcx)
	testl	%eax, %eax
	movq	%rcx, -16(%rbp)
	jne	.LBB52_8
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB52_2
.LBB52_3:
	leaq	-32(%rbp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	je	.LBB52_4
	movq	-16(%rbp), %rcx
.LBB52_8:
	movl	%eax, 44(%rcx)
.LBB52_9:
	movq	24(%rsi), %rsi
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuModuleUnload2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB52_10
.LBB52_11:
	movq	%rsi, %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuModuleUnload2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	movq	-16(%rbp), %rcx
	je	.LBB52_13
	movl	%eax, 44(%rcx)
.LBB52_13:
	lock		decq	(%rcx)
	jne	.LBB52_15
	#MEMBARRIER
	movq	-24(%rbp), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_
	nop
.LBB52_15:
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB52_4:
	movq	-32(%rbp), %rax
	testq	%rax, %rax
	setne	%cl
	movq	-16(%rbp), %rdx
	movq	16(%rdx), %rdi
	cmpq	%rdi, %rax
	sete	%al
	testb	%al, %cl
	jne	.LBB52_9
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB52_6
.LBB52_7:
	movq	%rdi, %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	movq	-16(%rbp), %rcx
	jne	.LBB52_8
	jmp	.LBB52_9
.LBB52_10:
.Ltmp4:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_14cuModuleUnload0E0zEB13_.llvm.1750587498003715262
	nop
.Ltmp5:
	jmp	.LBB52_11
.LBB52_2:
.Ltmp0:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_15cuCtxGetCurrent0E0zEB14_.llvm.1750587498003715262
	nop
.Ltmp1:
	jmp	.LBB52_3
.LBB52_6:
.Ltmp2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxSetCurrent0E0zEB13_.llvm.1750587498003715262
	nop
.Ltmp3:
	jmp	.LBB52_7
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaModuleEEB1m_@IMGREL
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaModuleEEB1m_,unique,52
	.seh_endproc
	.def	"?dtor$16@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaModuleEEB1m_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$16@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaModuleEEB1m_@4HA":
.seh_proc "?dtor$16@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaModuleEEB1m_@4HA"
.LBB52_16:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	64(%rdx), %rbp
	.seh_endprologue
	movq	-16(%rbp), %rax
	lock		decq	(%rax)
	jne	.LBB52_18
	#MEMBARRIER
	movq	-24(%rbp), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_
	nop
.LBB52_18:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end52:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaModuleEEB1m_,unique,52
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaModuleEEB1m_,unique,0
	.p2align	2, 0x0
$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaModuleEEB1m_:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaModuleEEB1m_@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaModuleEEB1m_@IMGREL
	.long	56
	.long	0
	.long	1
$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaModuleEEB1m_:
	.long	-1
	.long	"?dtor$16@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaModuleEEB1m_@4HA"@IMGREL
$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaModuleEEB1m_:
	.long	.Lfunc_begin52@IMGREL
	.long	-1
	.long	.Ltmp4@IMGREL
	.long	0
	.long	.Ltmp3@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaModuleEEB1m_,unique,52

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamEEB1m_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamEEB1m_,unique,53
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamEEB1m_:
.Lfunc_begin53:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamEEB1m_
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$48, %rsp
	.seh_stackalloc 48
	leaq	48(%rsp), %rbp
	.seh_setframe %rbp, 48
	.seh_endprologue
	movq	$-2, -8(%rbp)
	addq	$16, %rcx
.Ltmp6:
	movq	%rcx, -16(%rbp)
	callq	_RNvXsb_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStreamNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop
	nop
.Ltmp7:
	movq	-16(%rbp), %rcx
	movq	(%rcx), %rax
	lock		decq	(%rax)
	jne	.LBB53_6
	#MEMBARRIER
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbp
	.seh_endepilogue
	jmp	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_
.LBB53_6:
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamEEB1m_@IMGREL
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamEEB1m_,unique,53
	.seh_endproc
	.def	"?dtor$3@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamEEB1m_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$3@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamEEB1m_@4HA":
.seh_proc "?dtor$3@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamEEB1m_@4HA"
.LBB53_3:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	48(%rdx), %rbp
	.seh_endprologue
	movq	-16(%rbp), %rax
	movq	(%rax), %rax
	lock		decq	(%rax)
	jne	.LBB53_5
	#MEMBARRIER
	movq	-16(%rbp), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_
	nop
.LBB53_5:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end53:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamEEB1m_,unique,53
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamEEB1m_,unique,1
	.p2align	2, 0x0
$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamEEB1m_:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamEEB1m_@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamEEB1m_@IMGREL
	.long	40
	.long	0
	.long	1
$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamEEB1m_:
	.long	-1
	.long	"?dtor$3@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamEEB1m_@4HA"@IMGREL
$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamEEB1m_:
	.long	.Lfunc_begin53@IMGREL
	.long	-1
	.long	.Ltmp6@IMGREL
	.long	0
	.long	.Ltmp7@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamEEB1m_,unique,53

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCsfQUUnEvlYZE_5alloc3vec9into_iter8IntoIterNtNtBI_6string6StringEECs5UjBoGikVie_6cudarc;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCsfQUUnEvlYZE_5alloc3vec9into_iter8IntoIterNtNtBI_6string6StringEECs5UjBoGikVie_6cudarc,unique,54
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCsfQUUnEvlYZE_5alloc3vec9into_iter8IntoIterNtNtBI_6string6StringEECs5UjBoGikVie_6cudarc:
.Lfunc_begin54:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCsfQUUnEvlYZE_5alloc3vec9into_iter8IntoIterNtNtBI_6string6StringEECs5UjBoGikVie_6cudarc
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	%rcx, %rsi
	movq	8(%rcx), %rbx
	movq	24(%rcx), %rcx
	movq	%rcx, %rax
	subq	%rbx, %rax
	movabsq	$-6148914691236517205, %rdx
	mulq	%rdx
	cmpq	%rbx, %rcx
	je	.LBB54_5
	movq	%rdx, %rdi
	shrq	$4, %rdi
	addq	$8, %rbx
	jmp	.LBB54_2
	.p2align	4
.LBB54_4:
	addq	$24, %rbx
	decq	%rdi
	je	.LBB54_5
.LBB54_2:
	cmpq	$0, -8(%rbx)
	je	.LBB54_4
	movq	(%rbx), %rcx
	callq	mi_free
	jmp	.LBB54_4
.LBB54_5:
	cmpq	$0, 16(%rsi)
	je	.LBB54_6
	movq	(%rsi), %rcx
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	jmp	mi_free
.LBB54_6:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end54:
	.seh_endproc

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtNtB4_4iter8adapters7flatten7FlattenINtNtBG_3map3MapINtNtNtB4_5slice4iter4IterReENCNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib00EEEB2a_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtNtB4_4iter8adapters7flatten7FlattenINtNtBG_3map3MapINtNtNtB4_5slice4iter4IterReENCNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib00EEEB2a_,unique,55
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtNtB4_4iter8adapters7flatten7FlattenINtNtBG_3map3MapINtNtNtB4_5slice4iter4IterReENCNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib00EEEB2a_:
.Lfunc_begin55:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtNtB4_4iter8adapters7flatten7FlattenINtNtBG_3map3MapINtNtNtB4_5slice4iter4IterReENCNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib00EEEB2a_
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
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	%rcx, %rsi
	movq	(%rcx), %rdi
	movabsq	$-6148914691236517205, %r14
	testq	%rdi, %rdi
	je	.LBB55_8
	movq	8(%rsi), %r15
	movq	24(%rsi), %rcx
	movq	%rcx, %rax
	subq	%r15, %rax
	mulq	%r14
	cmpq	%r15, %rcx
	je	.LBB55_6
	movq	%rdx, %rbx
	shrq	$4, %rbx
	addq	$8, %r15
	jmp	.LBB55_3
	.p2align	4
.LBB55_5:
	addq	$24, %r15
	decq	%rbx
	je	.LBB55_6
.LBB55_3:
	cmpq	$0, -8(%r15)
	je	.LBB55_5
	movq	(%r15), %rcx
	callq	mi_free
	jmp	.LBB55_5
.LBB55_6:
	cmpq	$0, 16(%rsi)
	je	.LBB55_8
	movq	%rdi, %rcx
	callq	mi_free
.LBB55_8:
	movq	32(%rsi), %rdi
	testq	%rdi, %rdi
	je	.LBB55_15
	movq	40(%rsi), %r15
	movq	56(%rsi), %rcx
	movq	%rcx, %rax
	subq	%r15, %rax
	mulq	%r14
	cmpq	%r15, %rcx
	je	.LBB55_14
	movq	%rdx, %rbx
	shrq	$4, %rbx
	addq	$8, %r15
	jmp	.LBB55_11
	.p2align	4
.LBB55_13:
	addq	$24, %r15
	decq	%rbx
	je	.LBB55_14
.LBB55_11:
	cmpq	$0, -8(%r15)
	je	.LBB55_13
	movq	(%r15), %rcx
	callq	mi_free
	jmp	.LBB55_13
.LBB55_14:
	cmpq	$0, 48(%rsi)
	je	.LBB55_15
	movq	%rdi, %rcx
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	.seh_endepilogue
	jmp	mi_free
.LBB55_15:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	.seh_endepilogue
	retq
.Lfunc_end55:
	.seh_endproc

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCs5UjBoGikVie_6cudarc5nvrtc4safe7ProgramEBH_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCs5UjBoGikVie_6cudarc5nvrtc4safe7ProgramEBH_,unique,56
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCs5UjBoGikVie_6cudarc5nvrtc4safe7ProgramEBH_:
.Lfunc_begin56:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCs5UjBoGikVie_6cudarc5nvrtc4safe7ProgramEBH_
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$72, %rsp
	.seh_stackalloc 72
	leaq	64(%rsp), %rbp
	.seh_setframe %rbp, 64
	.seh_endprologue
	movq	$-2, (%rbp)
	movq	%rcx, %rsi
	movq	16(%rcx), %rax
	movq	$0, 16(%rcx)
	testq	%rax, %rax
	je	.LBB56_12
	movq	%rsi, -16(%rbp)
	movq	%rax, -24(%rbp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys19nvrtcDestroyProgram2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB56_2
.LBB56_3:
	leaq	-24(%rbp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys19nvrtcDestroyProgram2__S(%rip)
	testl	%eax, %eax
	movq	-16(%rbp), %rsi
	jne	.LBB56_4
.LBB56_12:
	movq	(%rsi), %rcx
	cmpq	$0, 8(%rsi)
	movb	$0, (%rcx)
	je	.LBB56_14
	callq	mi_free
.LBB56_14:
	movq	24(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB56_17
	cmpq	$0, 32(%rsi)
	movb	$0, (%rcx)
	je	.LBB56_17
	callq	mi_free
	nop
.LBB56_17:
	.seh_startepilogue
	addq	$72, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB56_2:
.Ltmp8:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramENtB10_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvB10_19nvrtcDestroyProgram0E0zEB14_
	nop
.Ltmp9:
	jmp	.LBB56_3
.LBB56_4:
	movl	%eax, -4(%rbp)
.Ltmp10:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1010(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.959.llvm.1750587498003715262(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.958(%rip), %r9
	leaq	-4(%rbp), %r8
	movl	$43, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core6result13unwrap_failed
	nop
.Ltmp11:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCs5UjBoGikVie_6cudarc5nvrtc4safe7ProgramEBH_@IMGREL
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCs5UjBoGikVie_6cudarc5nvrtc4safe7ProgramEBH_,unique,56
	.seh_endproc
	.def	"?dtor$6@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCs5UjBoGikVie_6cudarc5nvrtc4safe7ProgramEBH_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$6@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCs5UjBoGikVie_6cudarc5nvrtc4safe7ProgramEBH_@4HA":
.seh_proc "?dtor$6@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCs5UjBoGikVie_6cudarc5nvrtc4safe7ProgramEBH_@4HA"
.LBB56_6:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	64(%rdx), %rbp
	.seh_endprologue
	movq	-16(%rbp), %rsi
	movq	(%rsi), %rcx
	cmpq	$0, 8(%rsi)
	movb	$0, (%rcx)
	je	.LBB56_8
	callq	mi_free
.LBB56_8:
	movq	24(%rsi), %rcx
	testq	%rcx, %rcx
	je	.LBB56_11
	cmpq	$0, 32(%rsi)
	movb	$0, (%rcx)
	je	.LBB56_11
	callq	mi_free
	nop
.LBB56_11:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end56:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCs5UjBoGikVie_6cudarc5nvrtc4safe7ProgramEBH_,unique,56
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCs5UjBoGikVie_6cudarc5nvrtc4safe7ProgramEBH_,unique,2
	.p2align	2, 0x0
$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCs5UjBoGikVie_6cudarc5nvrtc4safe7ProgramEBH_:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCs5UjBoGikVie_6cudarc5nvrtc4safe7ProgramEBH_@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCs5UjBoGikVie_6cudarc5nvrtc4safe7ProgramEBH_@IMGREL
	.long	64
	.long	0
	.long	1
$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCs5UjBoGikVie_6cudarc5nvrtc4safe7ProgramEBH_:
	.long	-1
	.long	"?dtor$6@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCs5UjBoGikVie_6cudarc5nvrtc4safe7ProgramEBH_@4HA"@IMGREL
$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCs5UjBoGikVie_6cudarc5nvrtc4safe7ProgramEBH_:
	.long	.Lfunc_begin56@IMGREL
	.long	-1
	.long	.Ltmp8@IMGREL
	.long	0
	.long	.Ltmp11@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCs5UjBoGikVie_6cudarc5nvrtc4safe7ProgramEBH_,unique,56

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCsfQUUnEvlYZE_5alloc3ffi5c_str8NulErrorECs5UjBoGikVie_6cudarc.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCsfQUUnEvlYZE_5alloc3ffi5c_str8NulErrorECs5UjBoGikVie_6cudarc.llvm.1750587498003715262,unique,57
	.globl	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCsfQUUnEvlYZE_5alloc3ffi5c_str8NulErrorECs5UjBoGikVie_6cudarc.llvm.1750587498003715262
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCsfQUUnEvlYZE_5alloc3ffi5c_str8NulErrorECs5UjBoGikVie_6cudarc.llvm.1750587498003715262:
.Lfunc_begin57:
	cmpq	$0, (%rcx)
	je	.LBB57_1
	movq	8(%rcx), %rcx
	jmp	mi_free
.LBB57_1:
	retq
.Lfunc_end57:

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core9CudaEventEBJ_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core9CudaEventEBJ_.llvm.1750587498003715262,unique,58
	.globl	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core9CudaEventEBJ_.llvm.1750587498003715262
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core9CudaEventEBJ_.llvm.1750587498003715262:
.Lfunc_begin58:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core9CudaEventEBJ_.llvm.1750587498003715262
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$72, %rsp
	.seh_stackalloc 72
	leaq	64(%rsp), %rbp
	.seh_setframe %rbp, 64
	.seh_endprologue
	movq	$-2, (%rbp)
	movq	%rcx, -16(%rbp)
	movq	(%rcx), %rcx
	xorl	%eax, %eax
	xchgl	%eax, 44(%rcx)
	testl	%eax, %eax
	movq	%rcx, -8(%rbp)
	jne	.LBB58_8
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB58_2
.LBB58_3:
	leaq	-24(%rbp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	je	.LBB58_4
	movq	-8(%rbp), %rcx
.LBB58_8:
	movl	%eax, 44(%rcx)
.LBB58_9:
	movq	-16(%rbp), %rax
	movq	8(%rax), %rsi
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuEventDestroy_v22__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB58_10
.LBB58_11:
	movq	%rsi, %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuEventDestroy_v22__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	movq	-8(%rbp), %rcx
	je	.LBB58_13
	movl	%eax, 44(%rcx)
.LBB58_13:
	lock		decq	(%rcx)
	jne	.LBB58_15
	#MEMBARRIER
	movq	-16(%rbp), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_
	nop
.LBB58_15:
	.seh_startepilogue
	addq	$72, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB58_4:
	movq	-24(%rbp), %rax
	testq	%rax, %rax
	setne	%cl
	movq	-8(%rbp), %rdx
	movq	16(%rdx), %rsi
	cmpq	%rsi, %rax
	sete	%al
	testb	%al, %cl
	jne	.LBB58_9
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB58_6
.LBB58_7:
	movq	%rsi, %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	movq	-8(%rbp), %rcx
	jne	.LBB58_8
	jmp	.LBB58_9
.LBB58_10:
.Ltmp16:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_17cuEventDestroy_v20E0zEB13_.llvm.1750587498003715262
	nop
.Ltmp17:
	jmp	.LBB58_11
.LBB58_2:
.Ltmp12:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_15cuCtxGetCurrent0E0zEB14_.llvm.1750587498003715262
	nop
.Ltmp13:
	jmp	.LBB58_3
.LBB58_6:
.Ltmp14:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxSetCurrent0E0zEB13_.llvm.1750587498003715262
	nop
.Ltmp15:
	jmp	.LBB58_7
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core9CudaEventEBJ_.llvm.1750587498003715262@IMGREL
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core9CudaEventEBJ_.llvm.1750587498003715262,unique,58
	.seh_endproc
	.def	"?dtor$16@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core9CudaEventEBJ_.llvm.1750587498003715262@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$16@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core9CudaEventEBJ_.llvm.1750587498003715262@4HA":
.seh_proc "?dtor$16@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core9CudaEventEBJ_.llvm.1750587498003715262@4HA"
.LBB58_16:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	64(%rdx), %rbp
	.seh_endprologue
	movq	-8(%rbp), %rax
	lock		decq	(%rax)
	jne	.LBB58_18
	#MEMBARRIER
	movq	-16(%rbp), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_
	nop
.LBB58_18:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end58:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core9CudaEventEBJ_.llvm.1750587498003715262,unique,58
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core9CudaEventEBJ_.llvm.1750587498003715262,unique,3
	.p2align	2, 0x0
$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core9CudaEventEBJ_.llvm.1750587498003715262:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core9CudaEventEBJ_.llvm.1750587498003715262@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core9CudaEventEBJ_.llvm.1750587498003715262@IMGREL
	.long	64
	.long	0
	.long	1
$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core9CudaEventEBJ_.llvm.1750587498003715262:
	.long	-1
	.long	"?dtor$16@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core9CudaEventEBJ_.llvm.1750587498003715262@4HA"@IMGREL
$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core9CudaEventEBJ_.llvm.1750587498003715262:
	.long	.Lfunc_begin58@IMGREL
	.long	-1
	.long	.Ltmp16@IMGREL
	.long	0
	.long	.Ltmp15@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core9CudaEventEBJ_.llvm.1750587498003715262,unique,58

	.def	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc,unique,59
	.p2align	4
_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc:
.Lfunc_begin59:
.seh_proc _RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	.seh_handler __CxxFrameHandler3, @unwind, @except
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
	subq	$80, %rsp
	.seh_stackalloc 80
	leaq	80(%rsp), %rbp
	.seh_setframe %rbp, 80
	.seh_endprologue
	movq	$-2, -8(%rbp)
	movq	%r8, %rdi
	movq	%rdx, %r14
	movq	%rcx, %rsi
	movq	$0, -32(%rbp)
	movq	$1, -24(%rbp)
	movq	$0, -16(%rbp)
	leaq	1(%r8), %rdx
	leaq	-32(%rbp), %rcx
	callq	_RNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner10grow_exactCs5UjBoGikVie_6cudarc
	cmpq	$-1, %rax
	jne	.LBB59_1
	movq	-32(%rbp), %r15
	movq	-16(%rbp), %rbx
	movq	%r15, %rax
	subq	%rbx, %rax
	cmpq	%rax, %rdi
	ja	.LBB59_7
.LBB59_9:
	movq	-24(%rbp), %r12
	leaq	(%r12,%rbx), %rcx
	movq	%r14, %rdx
	movq	%rdi, %r8
	callq	memcpy
	addq	%rdi, %rbx
	movq	%rbx, -16(%rbp)
	cmpq	%r15, %rbx
	jne	.LBB59_12
.Ltmp22:
	leaq	-32(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVechE8grow_oneB7_
	nop
.Ltmp23:
	movq	-24(%rbp), %r12
.LBB59_12:
	movb	$0, (%r12,%rbx)
	incq	%rbx
	movq	%rbx, -16(%rbp)
	movq	%rbx, 16(%rsi)
	movups	-32(%rbp), %xmm0
	movups	%xmm0, (%rsi)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
.LBB59_7:
.Ltmp20:
	movq	$1, 32(%rsp)
	leaq	-32(%rbp), %rcx
	movl	$1, %r9d
	movq	%rbx, %rdx
	movq	%rdi, %r8
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECs5UjBoGikVie_6cudarc
	nop
.Ltmp21:
	movq	-32(%rbp), %r15
	movq	-16(%rbp), %rbx
	jmp	.LBB59_9
.LBB59_1:
.Ltmp18:
	movq	%rax, %rcx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp19:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc@IMGREL
	.section	.text$unlikely,"xr",one_only,_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc,unique,59
	.seh_endproc
	.def	"?dtor$3@?0?_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$3@?0?_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc@4HA":
.seh_proc "?dtor$3@?0?_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc@4HA"
.LBB59_3:
	movq	%rdx, 16(%rsp)
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
	leaq	80(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, -32(%rbp)
	je	.LBB59_5
	movq	-24(%rbp), %rcx
	callq	mi_free
	nop
.LBB59_5:
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
.Lfunc_end59:
	.seh_handlerdata
	.section	.text$unlikely,"xr",one_only,_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc,unique,59
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc,unique,4
	.p2align	2, 0x0
$cppxdata$_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc@IMGREL
	.long	72
	.long	0
	.long	1
$stateUnwindMap$_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc:
	.long	-1
	.long	"?dtor$3@?0?_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc@4HA"@IMGREL
$ip2state$_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc:
	.long	.Lfunc_begin59@IMGREL
	.long	-1
	.long	.Ltmp22@IMGREL
	.long	0
	.long	.Ltmp19@IMGREL
	.long	-1
	.section	.text$unlikely,"xr",one_only,_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc,unique,59

	.def	_RINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB2_13__nvrtcProgramOaENtB2_11nvrtcResultEB6_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB2_13__nvrtcProgramOaENtB2_11nvrtcResultEB6_,unique,60
	.p2align	4
_RINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB2_13__nvrtcProgramOaENtB2_11nvrtcResultEB6_:
.Lfunc_begin60:
.seh_proc _RINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB2_13__nvrtcProgramOaENtB2_11nvrtcResultEB6_
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	%rcx, %rsi
	movq	%rcx, 64(%rsp)
	movq	%rdx, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB60_5
	leaq	-1(%rdx), %rax
	cmpq	$16, %rdx
	ja	.LBB60_6
.LBB60_2:
	xorl	%edi, %edi
	xorl	%ecx, %ecx
	.p2align	4
.LBB60_3:
	cmpb	$0, (%rsi,%rcx)
	je	.LBB60_26
	incq	%rcx
	cmpq	%rcx, %rax
	jne	.LBB60_3
	jmp	.LBB60_16
.LBB60_5:
	movq	%rdx, %rdi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zEB2f_
	movq	%rdi, %rdx
	leaq	-1(%rdx), %rax
	cmpq	$16, %rdx
	jbe	.LBB60_2
.LBB60_6:
	leaq	7(%rsi), %rcx
	andq	$-8, %rcx
	subq	%rsi, %rcx
	jne	.LBB60_8
	xorl	%r8d, %r8d
	jmp	.LBB60_12
.LBB60_8:
	xorl	%edi, %edi
	xorl	%r8d, %r8d
	.p2align	4
.LBB60_9:
	cmpb	$0, (%rsi,%r8)
	je	.LBB60_26
	incq	%r8
	cmpq	%r8, %rcx
	jne	.LBB60_9
	leaq	-17(%rdx), %r9
	movl	$1, %r8d
	cmpq	%r9, %rcx
	ja	.LBB60_15
.LBB60_12:
	movq	(%rsi,%r8), %rcx
	movq	8(%rsi,%r8), %r9
	movabsq	$72340172838076672, %r10
	movq	%r10, %r11
	subq	%rcx, %r11
	orq	%rcx, %r11
	subq	%r9, %r10
	orq	%r9, %r10
	andq	%r11, %r10
	notq	%r10
	leaq	16(%r8), %rcx
	movabsq	$-9187201950435737472, %r9
	testq	%r9, %r10
	cmovneq	%r8, %rcx
	jmp	.LBB60_15
	.p2align	4
.LBB60_13:
	cmpb	$0, (%rsi,%rcx)
	je	.LBB60_25
	incq	%rcx
.LBB60_15:
	cmpq	%rcx, %rax
	jne	.LBB60_13
.LBB60_16:
	cmpb	$0, (%rsi,%rax)
	jne	.LBB60_19
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib3LIB(%rip), %rcx
	movq	%rsi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB60_28
.LBB60_18:
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB60_19:
	leaq	40(%rsp), %rcx
	movq	%rdx, %r8
	movq	%rsi, %rdx
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rsi
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib3LIB(%rip), %rcx
	movq	%rsi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB60_23
	movl	$-1, %ebx
	xorl	%edi, %edi
	cmpq	$0, 40(%rsp)
	je	.LBB60_22
.LBB60_21:
	movq	%rsi, %rcx
	movq	%rax, %rsi
	callq	mi_free
	movq	%rsi, %rax
.LBB60_22:
	cmpl	$-1, %ebx
	je	.LBB60_18
	jmp	.LBB60_27
.LBB60_23:
	movq	%rax, %rbx
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	movq	%rbx, %rax
	xorl	%ebx, %ebx
	cmpl	$1, %edi
	adcl	$10, %ebx
	cmpq	$0, 40(%rsp)
	jne	.LBB60_21
	jmp	.LBB60_22
.LBB60_25:
	xorl	%edi, %edi
.LBB60_26:
	movl	$15, %ebx
.LBB60_27:
	movl	%ebx, 40(%rsp)
	movl	%edi, 44(%rsp)
	movq	%rax, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB4_13__nvrtcProgramOaENtB4_11nvrtcResultE0B8_
	ud2
.LBB60_28:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	xorl	%eax, %eax
	cmpl	$1, %edi
	movl	$0, %ebx
	adcl	$10, %ebx
	jmp	.LBB60_27
.Lfunc_end60:
	.seh_endproc

	.def	_RINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB2_13__nvrtcProgramOjENtB2_11nvrtcResultEB6_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB2_13__nvrtcProgramOjENtB2_11nvrtcResultEB6_,unique,61
	.p2align	4
_RINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB2_13__nvrtcProgramOjENtB2_11nvrtcResultEB6_:
.Lfunc_begin61:
.seh_proc _RINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB2_13__nvrtcProgramOjENtB2_11nvrtcResultEB6_
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	%rcx, %rsi
	movq	%rcx, 64(%rsp)
	movq	%rdx, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB61_5
	leaq	-1(%rdx), %rax
	cmpq	$16, %rdx
	ja	.LBB61_6
.LBB61_2:
	xorl	%edi, %edi
	xorl	%ecx, %ecx
	.p2align	4
.LBB61_3:
	cmpb	$0, (%rsi,%rcx)
	je	.LBB61_28
	incq	%rcx
	cmpq	%rcx, %rax
	jne	.LBB61_3
	jmp	.LBB61_18
.LBB61_5:
	movq	%rdx, %rdi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zEB2f_
	movq	%rdi, %rdx
	leaq	-1(%rdx), %rax
	cmpq	$16, %rdx
	jbe	.LBB61_2
.LBB61_6:
	leaq	7(%rsi), %rcx
	andq	$-8, %rcx
	subq	%rsi, %rcx
	jne	.LBB61_8
	leaq	-17(%rdx), %r8
	xorl	%ecx, %ecx
	jmp	.LBB61_12
.LBB61_8:
	xorl	%edi, %edi
	xorl	%r8d, %r8d
	.p2align	4
.LBB61_9:
	cmpb	$0, (%rsi,%r8)
	je	.LBB61_28
	incq	%r8
	cmpq	%r8, %rcx
	jne	.LBB61_9
	leaq	-17(%rdx), %r8
	cmpq	%r8, %rcx
	ja	.LBB61_17
.LBB61_12:
	movabsq	$72340172838076672, %r9
	movabsq	$-9187201950435737472, %r10
	.p2align	4
.LBB61_13:
	movq	(%rsi,%rcx), %r11
	movq	8(%rsi,%rcx), %rdi
	movq	%r9, %rbx
	subq	%r11, %rbx
	orq	%r11, %rbx
	movq	%r9, %r11
	subq	%rdi, %r11
	orq	%rdi, %r11
	andq	%rbx, %r11
	notq	%r11
	testq	%r10, %r11
	jne	.LBB61_17
	addq	$16, %rcx
	cmpq	%r8, %rcx
	jbe	.LBB61_13
	jmp	.LBB61_17
	.p2align	4
.LBB61_15:
	cmpb	$0, (%rsi,%rcx)
	je	.LBB61_27
	incq	%rcx
.LBB61_17:
	cmpq	%rcx, %rax
	jne	.LBB61_15
.LBB61_18:
	cmpb	$0, (%rsi,%rax)
	jne	.LBB61_21
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib3LIB(%rip), %rcx
	movq	%rsi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB61_30
.LBB61_20:
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB61_21:
	leaq	40(%rsp), %rcx
	movq	%rdx, %r8
	movq	%rsi, %rdx
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rsi
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib3LIB(%rip), %rcx
	movq	%rsi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB61_25
	movl	$-1, %ebx
	xorl	%edi, %edi
	cmpq	$0, 40(%rsp)
	je	.LBB61_24
.LBB61_23:
	movq	%rsi, %rcx
	movq	%rax, %rsi
	callq	mi_free
	movq	%rsi, %rax
.LBB61_24:
	cmpl	$-1, %ebx
	je	.LBB61_20
	jmp	.LBB61_29
.LBB61_25:
	movq	%rax, %rbx
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	movq	%rbx, %rax
	xorl	%ebx, %ebx
	cmpl	$1, %edi
	adcl	$10, %ebx
	cmpq	$0, 40(%rsp)
	jne	.LBB61_23
	jmp	.LBB61_24
.LBB61_27:
	xorl	%edi, %edi
.LBB61_28:
	movl	$15, %ebx
.LBB61_29:
	movl	%ebx, 40(%rsp)
	movl	%edi, 44(%rsp)
	movq	%rax, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB4_13__nvrtcProgramOaENtB4_11nvrtcResultE0B8_
	ud2
.LBB61_30:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	xorl	%eax, %eax
	cmpl	$1, %edi
	movl	$0, %ebx
	adcl	$10, %ebx
	jmp	.LBB61_29
.Lfunc_end61:
	.seh_endproc

	.def	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB2_14cudaError_enumEB6_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB2_14cudaError_enumEB6_,unique,62
	.p2align	4
_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB2_14cudaError_enumEB6_:
.Lfunc_begin62:
.seh_proc _RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB2_14cudaError_enumEB6_
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	%rcx, %rsi
	movq	%rcx, 64(%rsp)
	movq	%rdx, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB62_5
	leaq	-1(%rdx), %rax
	cmpq	$16, %rdx
	ja	.LBB62_6
.LBB62_2:
	xorl	%edi, %edi
	xorl	%ecx, %ecx
	.p2align	4
.LBB62_3:
	cmpb	$0, (%rsi,%rcx)
	je	.LBB62_28
	incq	%rcx
	cmpq	%rcx, %rax
	jne	.LBB62_3
	jmp	.LBB62_18
.LBB62_5:
	movq	%rdx, %rdi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	movq	%rdi, %rdx
	leaq	-1(%rdx), %rax
	cmpq	$16, %rdx
	jbe	.LBB62_2
.LBB62_6:
	leaq	7(%rsi), %rcx
	andq	$-8, %rcx
	subq	%rsi, %rcx
	jne	.LBB62_8
	leaq	-17(%rdx), %r8
	xorl	%ecx, %ecx
	jmp	.LBB62_12
.LBB62_8:
	xorl	%edi, %edi
	xorl	%r8d, %r8d
	.p2align	4
.LBB62_9:
	cmpb	$0, (%rsi,%r8)
	je	.LBB62_28
	incq	%r8
	cmpq	%r8, %rcx
	jne	.LBB62_9
	leaq	-17(%rdx), %r8
	cmpq	%r8, %rcx
	ja	.LBB62_17
.LBB62_12:
	movabsq	$72340172838076672, %r9
	movabsq	$-9187201950435737472, %r10
	.p2align	4
.LBB62_13:
	movq	(%rsi,%rcx), %r11
	movq	8(%rsi,%rcx), %rdi
	movq	%r9, %rbx
	subq	%r11, %rbx
	orq	%r11, %rbx
	movq	%r9, %r11
	subq	%rdi, %r11
	orq	%rdi, %r11
	andq	%rbx, %r11
	notq	%r11
	testq	%r10, %r11
	jne	.LBB62_17
	addq	$16, %rcx
	cmpq	%r8, %rcx
	jbe	.LBB62_13
	jmp	.LBB62_17
	.p2align	4
.LBB62_15:
	cmpb	$0, (%rsi,%rcx)
	je	.LBB62_27
	incq	%rcx
.LBB62_17:
	cmpq	%rcx, %rax
	jne	.LBB62_15
.LBB62_18:
	cmpb	$0, (%rsi,%rax)
	jne	.LBB62_21
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rsi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB62_30
.LBB62_20:
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB62_21:
	leaq	40(%rsp), %rcx
	movq	%rdx, %r8
	movq	%rsi, %rdx
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rsi
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rsi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB62_25
	movl	$-1, %ebx
	xorl	%edi, %edi
	cmpq	$0, 40(%rsp)
	je	.LBB62_24
.LBB62_23:
	movq	%rsi, %rcx
	movq	%rax, %rsi
	callq	mi_free
	movq	%rsi, %rax
.LBB62_24:
	cmpl	$-1, %ebx
	je	.LBB62_20
	jmp	.LBB62_29
.LBB62_25:
	movq	%rax, %rbx
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	movq	%rbx, %rax
	xorl	%ebx, %ebx
	cmpl	$1, %edi
	adcl	$10, %ebx
	cmpq	$0, 40(%rsp)
	jne	.LBB62_23
	jmp	.LBB62_24
.LBB62_27:
	xorl	%edi, %edi
.LBB62_28:
	movl	$15, %ebx
.LBB62_29:
	movl	%ebx, 40(%rsp)
	movl	%edi, 44(%rsp)
	movq	%rax, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.LBB62_30:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	xorl	%eax, %eax
	cmpl	$1, %edi
	movl	$0, %ebx
	adcl	$10, %ebx
	jmp	.LBB62_29
.Lfunc_end62:
	.seh_endproc

	.def	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCNtB2_14cudaError_enumOPaEBL_EB6_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCNtB2_14cudaError_enumOPaEBL_EB6_,unique,63
	.p2align	4
_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCNtB2_14cudaError_enumOPaEBL_EB6_:
.Lfunc_begin63:
.seh_proc _RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCNtB2_14cudaError_enumOPaEBL_EB6_
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	%rcx, %rsi
	movq	%rcx, 64(%rsp)
	movq	%rdx, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB63_1
.LBB63_2:
	movl	$1, %eax
	.p2align	4
.LBB63_3:
	cmpb	$0, -1(%rsi,%rax)
	je	.LBB63_4
	incq	%rax
	cmpq	%rax, %rdx
	jne	.LBB63_3
	cmpb	$0, -1(%rsi,%rdx)
	jne	.LBB63_7
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rsi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB63_10
.LBB63_16:
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB63_7:
	leaq	40(%rsp), %rcx
	movq	%rdx, %r8
	movq	%rsi, %rdx
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rdi
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rdi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB63_11
	movl	$-1, %ebx
	xorl	%esi, %esi
	cmpq	$0, 40(%rsp)
	je	.LBB63_14
.LBB63_13:
	movq	%rdi, %rcx
	movq	%rax, %rdi
	callq	mi_free
	movq	%rdi, %rax
.LBB63_14:
	cmpl	$-1, %ebx
	je	.LBB63_16
	jmp	.LBB63_15
.LBB63_11:
	movq	%rax, %rbx
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %esi
	movq	%rbx, %rax
	xorl	%ebx, %ebx
	cmpl	$1, %esi
	adcl	$10, %ebx
	cmpq	$0, 40(%rsp)
	jne	.LBB63_13
	jmp	.LBB63_14
.LBB63_1:
	movq	%rdx, %rdi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	movq	%rdi, %rdx
	jmp	.LBB63_2
.LBB63_4:
	xorl	%esi, %esi
	movl	$15, %ebx
.LBB63_15:
	movl	%ebx, 40(%rsp)
	movl	%esi, 44(%rsp)
	movq	%rax, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.LBB63_10:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %esi
	xorl	%eax, %eax
	cmpl	$1, %esi
	movl	$0, %ebx
	adcl	$10, %ebx
	jmp	.LBB63_15
.Lfunc_end63:
	.seh_endproc

	.def	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_10CUevent_stENtB2_14cudaError_enumEB6_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_10CUevent_stENtB2_14cudaError_enumEB6_,unique,64
	.p2align	4
_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_10CUevent_stENtB2_14cudaError_enumEB6_:
.Lfunc_begin64:
.seh_proc _RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_10CUevent_stENtB2_14cudaError_enumEB6_
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	%rcx, %rsi
	movq	%rcx, 64(%rsp)
	movq	%rdx, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB64_5
	leaq	-1(%rdx), %rax
	cmpq	$16, %rdx
	ja	.LBB64_6
.LBB64_2:
	xorl	%edi, %edi
	xorl	%ecx, %ecx
	.p2align	4
.LBB64_3:
	cmpb	$0, (%rsi,%rcx)
	je	.LBB64_26
	incq	%rcx
	cmpq	%rcx, %rax
	jne	.LBB64_3
	jmp	.LBB64_16
.LBB64_5:
	movq	%rdx, %rdi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	movq	%rdi, %rdx
	leaq	-1(%rdx), %rax
	cmpq	$16, %rdx
	jbe	.LBB64_2
.LBB64_6:
	leaq	7(%rsi), %rcx
	andq	$-8, %rcx
	subq	%rsi, %rcx
	jne	.LBB64_8
	xorl	%r8d, %r8d
	jmp	.LBB64_12
.LBB64_8:
	xorl	%edi, %edi
	xorl	%r8d, %r8d
	.p2align	4
.LBB64_9:
	cmpb	$0, (%rsi,%r8)
	je	.LBB64_26
	incq	%r8
	cmpq	%r8, %rcx
	jne	.LBB64_9
	leaq	-17(%rdx), %r9
	movl	$1, %r8d
	cmpq	%r9, %rcx
	ja	.LBB64_15
.LBB64_12:
	movq	(%rsi,%r8), %rcx
	movq	8(%rsi,%r8), %r9
	movabsq	$72340172838076672, %r10
	movq	%r10, %r11
	subq	%rcx, %r11
	orq	%rcx, %r11
	subq	%r9, %r10
	orq	%r9, %r10
	andq	%r11, %r10
	notq	%r10
	leaq	16(%r8), %rcx
	movabsq	$-9187201950435737472, %r9
	testq	%r9, %r10
	cmovneq	%r8, %rcx
	jmp	.LBB64_15
	.p2align	4
.LBB64_13:
	cmpb	$0, (%rsi,%rcx)
	je	.LBB64_25
	incq	%rcx
.LBB64_15:
	cmpq	%rcx, %rax
	jne	.LBB64_13
.LBB64_16:
	cmpb	$0, (%rsi,%rax)
	jne	.LBB64_19
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rsi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB64_28
.LBB64_18:
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB64_19:
	leaq	40(%rsp), %rcx
	movq	%rdx, %r8
	movq	%rsi, %rdx
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rsi
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rsi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB64_23
	movl	$-1, %ebx
	xorl	%edi, %edi
	cmpq	$0, 40(%rsp)
	je	.LBB64_22
.LBB64_21:
	movq	%rsi, %rcx
	movq	%rax, %rsi
	callq	mi_free
	movq	%rsi, %rax
.LBB64_22:
	cmpl	$-1, %ebx
	je	.LBB64_18
	jmp	.LBB64_27
.LBB64_23:
	movq	%rax, %rbx
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	movq	%rbx, %rax
	xorl	%ebx, %ebx
	cmpl	$1, %edi
	adcl	$10, %ebx
	cmpq	$0, 40(%rsp)
	jne	.LBB64_21
	jmp	.LBB64_22
.LBB64_25:
	xorl	%edi, %edi
.LBB64_26:
	movl	$15, %ebx
.LBB64_27:
	movl	%ebx, 40(%rsp)
	movl	%edi, 44(%rsp)
	movq	%rax, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.LBB64_28:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	xorl	%eax, %eax
	cmpl	$1, %edi
	movl	$0, %ebx
	adcl	$10, %ebx
	jmp	.LBB64_27
.Lfunc_end64:
	.seh_endproc

	.def	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_11CUstream_stENtB2_14cudaError_enumEB6_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_11CUstream_stENtB2_14cudaError_enumEB6_,unique,65
	.p2align	4
_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_11CUstream_stENtB2_14cudaError_enumEB6_:
.Lfunc_begin65:
.seh_proc _RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_11CUstream_stENtB2_14cudaError_enumEB6_
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	%rcx, %rsi
	movq	%rcx, 64(%rsp)
	movq	%rdx, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB65_5
	leaq	-1(%rdx), %rax
	cmpq	$16, %rdx
	ja	.LBB65_6
.LBB65_2:
	xorl	%edi, %edi
	xorl	%ecx, %ecx
	.p2align	4
.LBB65_3:
	cmpb	$0, (%rsi,%rcx)
	je	.LBB65_28
	incq	%rcx
	cmpq	%rcx, %rax
	jne	.LBB65_3
	jmp	.LBB65_18
.LBB65_5:
	movq	%rdx, %rdi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	movq	%rdi, %rdx
	leaq	-1(%rdx), %rax
	cmpq	$16, %rdx
	jbe	.LBB65_2
.LBB65_6:
	leaq	7(%rsi), %rcx
	andq	$-8, %rcx
	subq	%rsi, %rcx
	jne	.LBB65_8
	leaq	-17(%rdx), %r8
	xorl	%ecx, %ecx
	jmp	.LBB65_12
.LBB65_8:
	xorl	%edi, %edi
	xorl	%r8d, %r8d
	.p2align	4
.LBB65_9:
	cmpb	$0, (%rsi,%r8)
	je	.LBB65_28
	incq	%r8
	cmpq	%r8, %rcx
	jne	.LBB65_9
	leaq	-17(%rdx), %r8
	cmpq	%r8, %rcx
	ja	.LBB65_17
.LBB65_12:
	movabsq	$72340172838076672, %r9
	movabsq	$-9187201950435737472, %r10
	.p2align	4
.LBB65_13:
	movq	(%rsi,%rcx), %r11
	movq	8(%rsi,%rcx), %rdi
	movq	%r9, %rbx
	subq	%r11, %rbx
	orq	%r11, %rbx
	movq	%r9, %r11
	subq	%rdi, %r11
	orq	%rdi, %r11
	andq	%rbx, %r11
	notq	%r11
	testq	%r10, %r11
	jne	.LBB65_17
	addq	$16, %rcx
	cmpq	%r8, %rcx
	jbe	.LBB65_13
	jmp	.LBB65_17
	.p2align	4
.LBB65_15:
	cmpb	$0, (%rsi,%rcx)
	je	.LBB65_27
	incq	%rcx
.LBB65_17:
	cmpq	%rcx, %rax
	jne	.LBB65_15
.LBB65_18:
	cmpb	$0, (%rsi,%rax)
	jne	.LBB65_21
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rsi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB65_30
.LBB65_20:
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB65_21:
	leaq	40(%rsp), %rcx
	movq	%rdx, %r8
	movq	%rsi, %rdx
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rsi
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rsi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB65_25
	movl	$-1, %ebx
	xorl	%edi, %edi
	cmpq	$0, 40(%rsp)
	je	.LBB65_24
.LBB65_23:
	movq	%rsi, %rcx
	movq	%rax, %rsi
	callq	mi_free
	movq	%rsi, %rax
.LBB65_24:
	cmpl	$-1, %ebx
	je	.LBB65_20
	jmp	.LBB65_29
.LBB65_25:
	movq	%rax, %rbx
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	movq	%rbx, %rax
	xorl	%ebx, %ebx
	cmpl	$1, %edi
	adcl	$10, %ebx
	cmpq	$0, 40(%rsp)
	jne	.LBB65_23
	jmp	.LBB65_24
.LBB65_27:
	xorl	%edi, %edi
.LBB65_28:
	movl	$15, %ebx
.LBB65_29:
	movl	%ebx, 40(%rsp)
	movl	%edi, 44(%rsp)
	movq	%rax, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.LBB65_30:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	xorl	%eax, %eax
	cmpl	$1, %edi
	movl	$0, %ebx
	adcl	$10, %ebx
	jmp	.LBB65_29
.Lfunc_end65:
	.seh_endproc

	.def	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_14CUgraphExec_stONtB2_11CUstream_stENtB2_14cudaError_enumEB6_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_14CUgraphExec_stONtB2_11CUstream_stENtB2_14cudaError_enumEB6_,unique,66
	.p2align	4
_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_14CUgraphExec_stONtB2_11CUstream_stENtB2_14cudaError_enumEB6_:
.Lfunc_begin66:
.seh_proc _RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_14CUgraphExec_stONtB2_11CUstream_stENtB2_14cudaError_enumEB6_
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	%rcx, %rdi
	movq	%rcx, 64(%rsp)
	movq	$13, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB66_21
	xorl	%esi, %esi
	movl	$15, %ebx
	cmpb	$0, (%rdi)
	je	.LBB66_22
.LBB66_2:
	cmpb	$0, 1(%rdi)
	je	.LBB66_22
	cmpb	$0, 2(%rdi)
	je	.LBB66_22
	cmpb	$0, 3(%rdi)
	je	.LBB66_22
	cmpb	$0, 4(%rdi)
	je	.LBB66_22
	cmpb	$0, 5(%rdi)
	je	.LBB66_22
	cmpb	$0, 6(%rdi)
	je	.LBB66_22
	cmpb	$0, 7(%rdi)
	je	.LBB66_22
	cmpb	$0, 8(%rdi)
	je	.LBB66_22
	cmpb	$0, 9(%rdi)
	je	.LBB66_22
	cmpb	$0, 10(%rdi)
	je	.LBB66_22
	cmpb	$0, 11(%rdi)
	je	.LBB66_22
	cmpb	$0, 12(%rdi)
	jne	.LBB66_16
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rdi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB66_34
.LBB66_15:
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB66_16:
	leaq	40(%rsp), %rcx
	movl	$13, %r8d
	movq	%rdi, %rdx
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rdi
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rdi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB66_20
	movl	$-1, %ebx
	xorl	%esi, %esi
	cmpq	$0, 40(%rsp)
	je	.LBB66_19
.LBB66_18:
	movq	%rdi, %rcx
	movq	%rax, %rdi
	callq	mi_free
	movq	%rdi, %rax
.LBB66_19:
	cmpl	$-1, %ebx
	je	.LBB66_15
	jmp	.LBB66_35
.LBB66_20:
	movq	%rax, %rbx
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %esi
	movq	%rbx, %rax
	xorl	%ebx, %ebx
	cmpl	$1, %esi
	adcl	$10, %ebx
	cmpq	$0, 40(%rsp)
	jne	.LBB66_18
	jmp	.LBB66_19
.LBB66_21:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	xorl	%esi, %esi
	movl	$15, %ebx
	cmpb	$0, (%rdi)
	jne	.LBB66_2
.LBB66_22:
.LBB66_35:
	movl	%ebx, 40(%rsp)
	movl	%esi, 44(%rsp)
	movq	%rax, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.LBB66_34:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %esi
	xorl	%eax, %eax
	cmpl	$1, %esi
	movl	$0, %ebx
	adcl	$10, %ebx
	jmp	.LBB66_35
.Lfunc_end66:
	.seh_endproc

	.def	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_8CUctx_stENtB2_14cudaError_enumEB6_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_8CUctx_stENtB2_14cudaError_enumEB6_,unique,67
	.p2align	4
_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_8CUctx_stENtB2_14cudaError_enumEB6_:
.Lfunc_begin67:
.seh_proc _RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_8CUctx_stENtB2_14cudaError_enumEB6_
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	%rcx, %rsi
	movq	%rcx, 64(%rsp)
	movq	%rdx, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB67_5
	leaq	-1(%rdx), %rax
	cmpq	$16, %rdx
	ja	.LBB67_6
.LBB67_2:
	xorl	%edi, %edi
	xorl	%ecx, %ecx
	.p2align	4
.LBB67_3:
	cmpb	$0, (%rsi,%rcx)
	je	.LBB67_28
	incq	%rcx
	cmpq	%rcx, %rax
	jne	.LBB67_3
	jmp	.LBB67_18
.LBB67_5:
	movq	%rdx, %rdi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	movq	%rdi, %rdx
	leaq	-1(%rdx), %rax
	cmpq	$16, %rdx
	jbe	.LBB67_2
.LBB67_6:
	leaq	7(%rsi), %rcx
	andq	$-8, %rcx
	subq	%rsi, %rcx
	jne	.LBB67_8
	leaq	-17(%rdx), %r8
	xorl	%ecx, %ecx
	jmp	.LBB67_12
.LBB67_8:
	xorl	%edi, %edi
	xorl	%r8d, %r8d
	.p2align	4
.LBB67_9:
	cmpb	$0, (%rsi,%r8)
	je	.LBB67_28
	incq	%r8
	cmpq	%r8, %rcx
	jne	.LBB67_9
	leaq	-17(%rdx), %r8
	cmpq	%r8, %rcx
	ja	.LBB67_17
.LBB67_12:
	movabsq	$72340172838076672, %r9
	movabsq	$-9187201950435737472, %r10
	.p2align	4
.LBB67_13:
	movq	(%rsi,%rcx), %r11
	movq	8(%rsi,%rcx), %rdi
	movq	%r9, %rbx
	subq	%r11, %rbx
	orq	%r11, %rbx
	movq	%r9, %r11
	subq	%rdi, %r11
	orq	%rdi, %r11
	andq	%rbx, %r11
	notq	%r11
	testq	%r10, %r11
	jne	.LBB67_17
	addq	$16, %rcx
	cmpq	%r8, %rcx
	jbe	.LBB67_13
	jmp	.LBB67_17
	.p2align	4
.LBB67_15:
	cmpb	$0, (%rsi,%rcx)
	je	.LBB67_27
	incq	%rcx
.LBB67_17:
	cmpq	%rcx, %rax
	jne	.LBB67_15
.LBB67_18:
	cmpb	$0, (%rsi,%rax)
	jne	.LBB67_21
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rsi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB67_30
.LBB67_20:
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB67_21:
	leaq	40(%rsp), %rcx
	movq	%rdx, %r8
	movq	%rsi, %rdx
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rsi
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rsi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB67_25
	movl	$-1, %ebx
	xorl	%edi, %edi
	cmpq	$0, 40(%rsp)
	je	.LBB67_24
.LBB67_23:
	movq	%rsi, %rcx
	movq	%rax, %rsi
	callq	mi_free
	movq	%rsi, %rax
.LBB67_24:
	cmpl	$-1, %ebx
	je	.LBB67_20
	jmp	.LBB67_29
.LBB67_25:
	movq	%rax, %rbx
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	movq	%rbx, %rax
	xorl	%ebx, %ebx
	cmpl	$1, %edi
	adcl	$10, %ebx
	cmpq	$0, 40(%rsp)
	jne	.LBB67_23
	jmp	.LBB67_24
.LBB67_27:
	xorl	%edi, %edi
.LBB67_28:
	movl	$15, %ebx
.LBB67_29:
	movl	%ebx, 40(%rsp)
	movl	%edi, 44(%rsp)
	movq	%rax, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.LBB67_30:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	xorl	%eax, %eax
	cmpl	$1, %edi
	movl	$0, %ebx
	adcl	$10, %ebx
	jmp	.LBB67_29
.Lfunc_end67:
	.seh_endproc

	.def	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCOONtB2_8CUctx_stENtB2_14cudaError_enumEB6_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCOONtB2_8CUctx_stENtB2_14cudaError_enumEB6_,unique,68
	.p2align	4
_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCOONtB2_8CUctx_stENtB2_14cudaError_enumEB6_:
.Lfunc_begin68:
.seh_proc _RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCOONtB2_8CUctx_stENtB2_14cudaError_enumEB6_
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	%rcx, %rsi
	movq	%rcx, 64(%rsp)
	movq	%rdx, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB68_5
	leaq	-1(%rdx), %rax
	cmpq	$16, %rdx
	ja	.LBB68_6
.LBB68_2:
	xorl	%edi, %edi
	xorl	%ecx, %ecx
	.p2align	4
.LBB68_3:
	cmpb	$0, (%rsi,%rcx)
	je	.LBB68_26
	incq	%rcx
	cmpq	%rcx, %rax
	jne	.LBB68_3
	jmp	.LBB68_16
.LBB68_5:
	movq	%rdx, %rdi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	movq	%rdi, %rdx
	leaq	-1(%rdx), %rax
	cmpq	$16, %rdx
	jbe	.LBB68_2
.LBB68_6:
	leaq	7(%rsi), %rcx
	andq	$-8, %rcx
	subq	%rsi, %rcx
	jne	.LBB68_8
	xorl	%r8d, %r8d
	jmp	.LBB68_12
.LBB68_8:
	xorl	%edi, %edi
	xorl	%r8d, %r8d
	.p2align	4
.LBB68_9:
	cmpb	$0, (%rsi,%r8)
	je	.LBB68_26
	incq	%r8
	cmpq	%r8, %rcx
	jne	.LBB68_9
	leaq	-17(%rdx), %r9
	movl	$1, %r8d
	cmpq	%r9, %rcx
	ja	.LBB68_15
.LBB68_12:
	movq	(%rsi,%r8), %rcx
	movq	8(%rsi,%r8), %r9
	movabsq	$72340172838076672, %r10
	movq	%r10, %r11
	subq	%rcx, %r11
	orq	%rcx, %r11
	subq	%r9, %r10
	orq	%r9, %r10
	andq	%r11, %r10
	notq	%r10
	leaq	16(%r8), %rcx
	movabsq	$-9187201950435737472, %r9
	testq	%r9, %r10
	cmovneq	%r8, %rcx
	jmp	.LBB68_15
	.p2align	4
.LBB68_13:
	cmpb	$0, (%rsi,%rcx)
	je	.LBB68_25
	incq	%rcx
.LBB68_15:
	cmpq	%rcx, %rax
	jne	.LBB68_13
.LBB68_16:
	cmpb	$0, (%rsi,%rax)
	jne	.LBB68_19
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rsi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB68_28
.LBB68_18:
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB68_19:
	leaq	40(%rsp), %rcx
	movq	%rdx, %r8
	movq	%rsi, %rdx
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rsi
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rsi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB68_23
	movl	$-1, %ebx
	xorl	%edi, %edi
	cmpq	$0, 40(%rsp)
	je	.LBB68_22
.LBB68_21:
	movq	%rsi, %rcx
	movq	%rax, %rsi
	callq	mi_free
	movq	%rsi, %rax
.LBB68_22:
	cmpl	$-1, %ebx
	je	.LBB68_18
	jmp	.LBB68_27
.LBB68_23:
	movq	%rax, %rbx
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	movq	%rbx, %rax
	xorl	%ebx, %ebx
	cmpl	$1, %edi
	adcl	$10, %ebx
	cmpq	$0, 40(%rsp)
	jne	.LBB68_21
	jmp	.LBB68_22
.LBB68_25:
	xorl	%edi, %edi
.LBB68_26:
	movl	$15, %ebx
.LBB68_27:
	movl	%ebx, 40(%rsp)
	movl	%edi, 44(%rsp)
	movq	%rax, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.LBB68_28:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	xorl	%eax, %eax
	cmpl	$1, %edi
	movl	$0, %ebx
	adcl	$10, %ebx
	jmp	.LBB68_27
.Lfunc_end68:
	.seh_endproc

	.def	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCOONtB2_8CUmod_stPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtB2_14cudaError_enumEB6_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCOONtB2_8CUmod_stPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtB2_14cudaError_enumEB6_,unique,69
	.p2align	4
_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCOONtB2_8CUmod_stPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtB2_14cudaError_enumEB6_:
.Lfunc_begin69:
.seh_proc _RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCOONtB2_8CUmod_stPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtB2_14cudaError_enumEB6_
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	%rcx, %rsi
	movq	%rcx, 64(%rsp)
	movq	%rdx, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB69_5
	leaq	-1(%rdx), %rax
	cmpq	$16, %rdx
	jne	.LBB69_6
.LBB69_2:
	xorl	%edi, %edi
	xorl	%ecx, %ecx
	.p2align	4
.LBB69_3:
	cmpb	$0, (%rsi,%rcx)
	je	.LBB69_28
	incq	%rcx
	cmpq	%rcx, %rax
	jne	.LBB69_3
	jmp	.LBB69_18
.LBB69_5:
	movq	%rdx, %rdi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	movq	%rdi, %rdx
	leaq	-1(%rdx), %rax
	cmpq	$16, %rdx
	je	.LBB69_2
.LBB69_6:
	leaq	7(%rsi), %rcx
	andq	$-8, %rcx
	subq	%rsi, %rcx
	jne	.LBB69_8
	leaq	-17(%rdx), %r8
	xorl	%ecx, %ecx
	jmp	.LBB69_12
.LBB69_8:
	xorl	%edi, %edi
	xorl	%r8d, %r8d
	.p2align	4
.LBB69_9:
	cmpb	$0, (%rsi,%r8)
	je	.LBB69_28
	incq	%r8
	cmpq	%r8, %rcx
	jne	.LBB69_9
	leaq	-17(%rdx), %r8
	cmpq	%r8, %rcx
	ja	.LBB69_17
.LBB69_12:
	movabsq	$72340172838076672, %r9
	movabsq	$-9187201950435737472, %r10
	.p2align	4
.LBB69_13:
	movq	(%rsi,%rcx), %r11
	movq	8(%rsi,%rcx), %rdi
	movq	%r9, %rbx
	subq	%r11, %rbx
	orq	%r11, %rbx
	movq	%r9, %r11
	subq	%rdi, %r11
	orq	%rdi, %r11
	andq	%rbx, %r11
	notq	%r11
	testq	%r10, %r11
	jne	.LBB69_17
	addq	$16, %rcx
	cmpq	%r8, %rcx
	jbe	.LBB69_13
	jmp	.LBB69_17
	.p2align	4
.LBB69_15:
	cmpb	$0, (%rsi,%rcx)
	je	.LBB69_27
	incq	%rcx
.LBB69_17:
	cmpq	%rcx, %rax
	jne	.LBB69_15
.LBB69_18:
	cmpb	$0, (%rsi,%rax)
	jne	.LBB69_21
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rsi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB69_30
.LBB69_20:
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB69_21:
	leaq	40(%rsp), %rcx
	movq	%rdx, %r8
	movq	%rsi, %rdx
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rsi
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rsi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB69_25
	movl	$-1, %ebx
	xorl	%edi, %edi
	cmpq	$0, 40(%rsp)
	je	.LBB69_24
.LBB69_23:
	movq	%rsi, %rcx
	movq	%rax, %rsi
	callq	mi_free
	movq	%rsi, %rax
.LBB69_24:
	cmpl	$-1, %ebx
	je	.LBB69_20
	jmp	.LBB69_29
.LBB69_25:
	movq	%rax, %rbx
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	movq	%rbx, %rax
	xorl	%ebx, %ebx
	cmpl	$1, %edi
	adcl	$10, %ebx
	cmpq	$0, 40(%rsp)
	jne	.LBB69_23
	jmp	.LBB69_24
.LBB69_27:
	xorl	%edi, %edi
.LBB69_28:
	movl	$15, %ebx
.LBB69_29:
	movl	%ebx, 40(%rsp)
	movl	%edi, 44(%rsp)
	movq	%rax, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.LBB69_30:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	xorl	%eax, %eax
	cmpl	$1, %edi
	movl	$0, %ebx
	adcl	$10, %ebx
	jmp	.LBB69_29
.Lfunc_end69:
	.seh_endproc

	.def	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKClENtB2_14cudaError_enumEB6_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKClENtB2_14cudaError_enumEB6_,unique,70
	.p2align	4
_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKClENtB2_14cudaError_enumEB6_:
.Lfunc_begin70:
.seh_proc _RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKClENtB2_14cudaError_enumEB6_
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	%rcx, %rsi
	movq	%rcx, 64(%rsp)
	movq	%rdx, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB70_3
	leaq	7(%rsi), %rax
	andq	$-8, %rax
	subq	%rsi, %rax
	jne	.LBB70_4
.LBB70_2:
	xorl	%eax, %eax
	jmp	.LBB70_8
.LBB70_3:
	movq	%rdx, %rdi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	movq	%rdi, %rdx
	leaq	7(%rsi), %rax
	andq	$-8, %rax
	subq	%rsi, %rax
	je	.LBB70_2
.LBB70_4:
	xorl	%edi, %edi
	xorl	%ecx, %ecx
	.p2align	4
.LBB70_5:
	cmpb	$0, (%rsi,%rcx)
	je	.LBB70_22
	incq	%rcx
	cmpq	%rcx, %rax
	jne	.LBB70_5
	leaq	-17(%rdx), %rcx
	cmpq	%rcx, %rax
	ja	.LBB70_9
.LBB70_8:
	movq	(%rsi,%rax), %rcx
	movq	8(%rsi,%rax), %r8
	movabsq	$72340172838076672, %r9
	movq	%r9, %r10
	subq	%rcx, %r10
	orq	%rcx, %r10
	subq	%r8, %r9
	orq	%r8, %r9
	andq	%r10, %r9
	notq	%r9
	movq	%rax, %rcx
	orq	$16, %rcx
	movabsq	$-9187201950435737472, %r8
	testq	%r8, %r9
	cmoveq	%rcx, %rax
.LBB70_9:
	leaq	-1(%rdx), %rcx
	cmpq	%rax, %rcx
	je	.LBB70_12
	.p2align	4
.LBB70_10:
	cmpb	$0, (%rsi,%rax)
	je	.LBB70_21
	incq	%rax
	cmpq	%rax, %rcx
	jne	.LBB70_10
.LBB70_12:
	cmpb	$0, (%rsi,%rcx)
	jne	.LBB70_15
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rsi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB70_24
.LBB70_14:
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB70_15:
	leaq	40(%rsp), %rcx
	movq	%rdx, %r8
	movq	%rsi, %rdx
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rsi
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rsi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB70_19
	movl	$-1, %ebx
	xorl	%edi, %edi
	cmpq	$0, 40(%rsp)
	je	.LBB70_18
.LBB70_17:
	movq	%rsi, %rcx
	movq	%rax, %rsi
	callq	mi_free
	movq	%rsi, %rax
.LBB70_18:
	cmpl	$-1, %ebx
	je	.LBB70_14
	jmp	.LBB70_23
.LBB70_19:
	movq	%rax, %rbx
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	movq	%rbx, %rax
	xorl	%ebx, %ebx
	cmpl	$1, %edi
	adcl	$10, %ebx
	cmpq	$0, 40(%rsp)
	jne	.LBB70_17
	jmp	.LBB70_18
.LBB70_21:
	xorl	%edi, %edi
.LBB70_22:
	movl	$15, %ebx
.LBB70_23:
	movl	%ebx, 40(%rsp)
	movl	%edi, 44(%rsp)
	movq	%rax, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.LBB70_24:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	xorl	%eax, %eax
	cmpl	$1, %edi
	movl	$0, %ebx
	adcl	$10, %ebx
	jmp	.LBB70_23
.Lfunc_end70:
	.seh_endproc

	.def	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCmENtB2_14cudaError_enumEB6_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCmENtB2_14cudaError_enumEB6_,unique,71
	.p2align	4
_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCmENtB2_14cudaError_enumEB6_:
.Lfunc_begin71:
.seh_proc _RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCmENtB2_14cudaError_enumEB6_
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	%rcx, %rsi
	movq	%rcx, 64(%rsp)
	movq	%rdx, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB71_1
.LBB71_2:
	movl	$1, %eax
	.p2align	4
.LBB71_3:
	cmpb	$0, -1(%rsi,%rax)
	je	.LBB71_4
	incq	%rax
	cmpq	%rax, %rdx
	jne	.LBB71_3
	cmpb	$0, -1(%rsi,%rdx)
	jne	.LBB71_7
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rsi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB71_10
.LBB71_16:
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB71_7:
	leaq	40(%rsp), %rcx
	movq	%rdx, %r8
	movq	%rsi, %rdx
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rdi
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rdi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB71_11
	movl	$-1, %ebx
	xorl	%esi, %esi
	cmpq	$0, 40(%rsp)
	je	.LBB71_14
.LBB71_13:
	movq	%rdi, %rcx
	movq	%rax, %rdi
	callq	mi_free
	movq	%rdi, %rax
.LBB71_14:
	cmpl	$-1, %ebx
	je	.LBB71_16
	jmp	.LBB71_15
.LBB71_11:
	movq	%rax, %rbx
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %esi
	movq	%rbx, %rax
	xorl	%ebx, %ebx
	cmpl	$1, %esi
	adcl	$10, %ebx
	cmpq	$0, 40(%rsp)
	jne	.LBB71_13
	jmp	.LBB71_14
.LBB71_1:
	movq	%rdx, %rdi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	movq	%rdi, %rdx
	jmp	.LBB71_2
.LBB71_4:
	xorl	%esi, %esi
	movl	$15, %ebx
.LBB71_15:
	movl	%ebx, 40(%rsp)
	movl	%esi, 44(%rsp)
	movq	%rax, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.LBB71_10:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %esi
	xorl	%eax, %eax
	cmpl	$1, %esi
	movl	$0, %ebx
	adcl	$10, %ebx
	jmp	.LBB71_15
.Lfunc_end71:
	.seh_endproc

	.def	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCyENtB2_14cudaError_enumEB6_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCyENtB2_14cudaError_enumEB6_,unique,72
	.p2align	4
_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCyENtB2_14cudaError_enumEB6_:
.Lfunc_begin72:
.seh_proc _RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCyENtB2_14cudaError_enumEB6_
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	%rcx, %rsi
	movq	%rcx, 64(%rsp)
	movq	%rdx, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB72_5
	leaq	-1(%rdx), %rax
	cmpq	$16, %rdx
	ja	.LBB72_6
.LBB72_2:
	xorl	%edi, %edi
	xorl	%ecx, %ecx
	.p2align	4
.LBB72_3:
	cmpb	$0, (%rsi,%rcx)
	je	.LBB72_28
	incq	%rcx
	cmpq	%rcx, %rax
	jne	.LBB72_3
	jmp	.LBB72_18
.LBB72_5:
	movq	%rdx, %rdi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	movq	%rdi, %rdx
	leaq	-1(%rdx), %rax
	cmpq	$16, %rdx
	jbe	.LBB72_2
.LBB72_6:
	leaq	7(%rsi), %rcx
	andq	$-8, %rcx
	subq	%rsi, %rcx
	jne	.LBB72_8
	leaq	-17(%rdx), %r8
	xorl	%ecx, %ecx
	jmp	.LBB72_12
.LBB72_8:
	xorl	%edi, %edi
	xorl	%r8d, %r8d
	.p2align	4
.LBB72_9:
	cmpb	$0, (%rsi,%r8)
	je	.LBB72_28
	incq	%r8
	cmpq	%r8, %rcx
	jne	.LBB72_9
	leaq	-17(%rdx), %r8
	cmpq	%r8, %rcx
	ja	.LBB72_17
.LBB72_12:
	movabsq	$72340172838076672, %r9
	movabsq	$-9187201950435737472, %r10
	.p2align	4
.LBB72_13:
	movq	(%rsi,%rcx), %r11
	movq	8(%rsi,%rcx), %rdi
	movq	%r9, %rbx
	subq	%r11, %rbx
	orq	%r11, %rbx
	movq	%r9, %r11
	subq	%rdi, %r11
	orq	%rdi, %r11
	andq	%rbx, %r11
	notq	%r11
	testq	%r10, %r11
	jne	.LBB72_17
	addq	$16, %rcx
	cmpq	%r8, %rcx
	jbe	.LBB72_13
	jmp	.LBB72_17
	.p2align	4
.LBB72_15:
	cmpb	$0, (%rsi,%rcx)
	je	.LBB72_27
	incq	%rcx
.LBB72_17:
	cmpq	%rcx, %rax
	jne	.LBB72_15
.LBB72_18:
	cmpb	$0, (%rsi,%rax)
	jne	.LBB72_21
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rsi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB72_30
.LBB72_20:
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB72_21:
	leaq	40(%rsp), %rcx
	movq	%rdx, %r8
	movq	%rsi, %rdx
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rsi
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rsi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB72_25
	movl	$-1, %ebx
	xorl	%edi, %edi
	cmpq	$0, 40(%rsp)
	je	.LBB72_24
.LBB72_23:
	movq	%rsi, %rcx
	movq	%rax, %rsi
	callq	mi_free
	movq	%rsi, %rax
.LBB72_24:
	cmpl	$-1, %ebx
	je	.LBB72_20
	jmp	.LBB72_29
.LBB72_25:
	movq	%rax, %rbx
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	movq	%rbx, %rax
	xorl	%ebx, %ebx
	cmpl	$1, %edi
	adcl	$10, %ebx
	cmpq	$0, 40(%rsp)
	jne	.LBB72_23
	jmp	.LBB72_24
.LBB72_27:
	xorl	%edi, %edi
.LBB72_28:
	movl	$15, %ebx
.LBB72_29:
	movl	%ebx, 40(%rsp)
	movl	%edi, 44(%rsp)
	movq	%rax, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.LBB72_30:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	xorl	%eax, %eax
	cmpl	$1, %edi
	movl	$0, %ebx
	adcl	$10, %ebx
	jmp	.LBB72_29
.Lfunc_end72:
	.seh_endproc

	.def	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCyyjONtB2_11CUstream_stENtB2_14cudaError_enumEB6_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCyyjONtB2_11CUstream_stENtB2_14cudaError_enumEB6_,unique,73
	.p2align	4
_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCyyjONtB2_11CUstream_stENtB2_14cudaError_enumEB6_:
.Lfunc_begin73:
.seh_proc _RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCyyjONtB2_11CUstream_stENtB2_14cudaError_enumEB6_
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	%rcx, %rsi
	movq	%rcx, 64(%rsp)
	movq	%rdx, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB73_5
	leaq	-1(%rdx), %rax
	cmpq	$16, %rdx
	ja	.LBB73_6
.LBB73_2:
	xorl	%edi, %edi
	xorl	%ecx, %ecx
	.p2align	4
.LBB73_3:
	cmpb	$0, (%rsi,%rcx)
	je	.LBB73_28
	incq	%rcx
	cmpq	%rcx, %rax
	jne	.LBB73_3
	jmp	.LBB73_18
.LBB73_5:
	movq	%rdx, %rdi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	movq	%rdi, %rdx
	leaq	-1(%rdx), %rax
	cmpq	$16, %rdx
	jbe	.LBB73_2
.LBB73_6:
	leaq	7(%rsi), %rcx
	andq	$-8, %rcx
	subq	%rsi, %rcx
	jne	.LBB73_8
	leaq	-17(%rdx), %r8
	xorl	%ecx, %ecx
	jmp	.LBB73_12
.LBB73_8:
	xorl	%edi, %edi
	xorl	%r8d, %r8d
	.p2align	4
.LBB73_9:
	cmpb	$0, (%rsi,%r8)
	je	.LBB73_28
	incq	%r8
	cmpq	%r8, %rcx
	jne	.LBB73_9
	leaq	-17(%rdx), %r8
	cmpq	%r8, %rcx
	ja	.LBB73_17
.LBB73_12:
	movabsq	$72340172838076672, %r9
	movabsq	$-9187201950435737472, %r10
	.p2align	4
.LBB73_13:
	movq	(%rsi,%rcx), %r11
	movq	8(%rsi,%rcx), %rdi
	movq	%r9, %rbx
	subq	%r11, %rbx
	orq	%r11, %rbx
	movq	%r9, %r11
	subq	%rdi, %r11
	orq	%rdi, %r11
	andq	%rbx, %r11
	notq	%r11
	testq	%r10, %r11
	jne	.LBB73_17
	addq	$16, %rcx
	cmpq	%r8, %rcx
	jbe	.LBB73_13
	jmp	.LBB73_17
	.p2align	4
.LBB73_15:
	cmpb	$0, (%rsi,%rcx)
	je	.LBB73_27
	incq	%rcx
.LBB73_17:
	cmpq	%rcx, %rax
	jne	.LBB73_15
.LBB73_18:
	cmpb	$0, (%rsi,%rax)
	jne	.LBB73_21
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rsi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB73_30
.LBB73_20:
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB73_21:
	leaq	40(%rsp), %rcx
	movq	%rdx, %r8
	movq	%rsi, %rdx
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rsi
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rsi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	testq	%rax, %rax
	je	.LBB73_25
	movl	$-1, %ebx
	xorl	%edi, %edi
	cmpq	$0, 40(%rsp)
	je	.LBB73_24
.LBB73_23:
	movq	%rsi, %rcx
	movq	%rax, %rsi
	callq	mi_free
	movq	%rsi, %rax
.LBB73_24:
	cmpl	$-1, %ebx
	je	.LBB73_20
	jmp	.LBB73_29
.LBB73_25:
	movq	%rax, %rbx
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	movq	%rbx, %rax
	xorl	%ebx, %ebx
	cmpl	$1, %edi
	adcl	$10, %ebx
	cmpq	$0, 40(%rsp)
	jne	.LBB73_23
	jmp	.LBB73_24
.LBB73_27:
	xorl	%edi, %edi
.LBB73_28:
	movl	$15, %ebx
.LBB73_29:
	movl	%ebx, 40(%rsp)
	movl	%edi, 44(%rsp)
	movq	%rax, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.LBB73_30:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	xorl	%eax, %eax
	cmpl	$1, %edi
	movl	$0, %ebx
	adcl	$10, %ebx
	jmp	.LBB73_29
.Lfunc_end73:
	.seh_endproc

	.def	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECs5UjBoGikVie_6cudarc;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECs5UjBoGikVie_6cudarc,unique,74
	.p2align	4
_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECs5UjBoGikVie_6cudarc:
.Lfunc_begin74:
.seh_proc _RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECs5UjBoGikVie_6cudarc
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	addq	%r8, %rdx
	jb	.LBB74_1
	movq	%rcx, %rsi
	movq	128(%rsp), %rcx
	movq	(%rsi), %rax
	leaq	(%rax,%rax), %rdi
	cmpq	%rdi, %rdx
	cmovaq	%rdx, %rdi
	xorl	%edx, %edx
	cmpq	$1, %rcx
	sete	%dl
	leaq	4(,%rdx,4), %rdx
	cmpq	%rdx, %rdi
	cmovbeq	%rdx, %rdi
	movq	8(%rsi), %r8
	movq	%rcx, 40(%rsp)
	movq	%r9, 32(%rsp)
	leaq	48(%rsp), %rcx
	movq	%rax, %rdx
	movq	%rdi, %r9
	callq	_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCs5UjBoGikVie_6cudarc
	cmpl	$1, 48(%rsp)
	je	.LBB74_3
	movq	56(%rsp), %rax
	movq	%rax, 8(%rsi)
	movq	%rdi, (%rsi)
	.seh_startepilogue
	addq	$72, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB74_1:
	xorl	%ecx, %ecx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.LBB74_3:
	movq	56(%rsp), %rcx
	movq	64(%rsp), %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.Lfunc_end74:
	.seh_endproc

	.def	_RINvXs_NtCskIq6Fm6qntW_10libloading11as_filenameReNtB5_6Sealed16windows_filenameNtNtNtB7_2os7windows7LibraryNCINvMs0_B1i_B1g_15load_with_flagsRNtNtCsfQUUnEvlYZE_5alloc6string6StringE0ECs5UjBoGikVie_6cudarc;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvXs_NtCskIq6Fm6qntW_10libloading11as_filenameReNtB5_6Sealed16windows_filenameNtNtNtB7_2os7windows7LibraryNCINvMs0_B1i_B1g_15load_with_flagsRNtNtCsfQUUnEvlYZE_5alloc6string6StringE0ECs5UjBoGikVie_6cudarc,unique,75
	.p2align	4
_RINvXs_NtCskIq6Fm6qntW_10libloading11as_filenameReNtB5_6Sealed16windows_filenameNtNtNtB7_2os7windows7LibraryNCINvMs0_B1i_B1g_15load_with_flagsRNtNtCsfQUUnEvlYZE_5alloc6string6StringE0ECs5UjBoGikVie_6cudarc:
.Lfunc_begin75:
.seh_proc _RINvXs_NtCskIq6Fm6qntW_10libloading11as_filenameReNtB5_6Sealed16windows_filenameNtNtNtB7_2os7windows7LibraryNCINvMs0_B1i_B1g_15load_with_flagsRNtNtCsfQUUnEvlYZE_5alloc6string6StringE0ECs5UjBoGikVie_6cudarc
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
	movq	%r8, %rdi
	movq	%rdx, %rbx
	testq	%r8, %r8
	je	.LBB75_6
	leaq	-1(%rdi), %rax
	cmpq	$16, %rdi
	ja	.LBB75_7
	testq	%rax, %rax
	je	.LBB75_19
	xorl	%edx, %edx
	.p2align	4
.LBB75_4:
	cmpb	$0, (%rbx,%rdx)
	je	.LBB75_22
	incq	%rdx
	cmpq	%rdx, %rax
	jne	.LBB75_4
	jmp	.LBB75_19
.LBB75_6:
	movq	%rcx, -32(%rbp)
	addq	%rbx, %rdi
	movl	$4, %esi
	movl	$8, %r14d
	xorl	%r13d, %r13d
	xorl	%ebx, %ebx
	movq	$0, -40(%rbp)
	xorl	%r12d, %r12d
	jmp	.LBB75_37
.LBB75_7:
	leaq	7(%rbx), %r14
	andq	$-8, %r14
	subq	%rbx, %r14
	jne	.LBB75_12
	leaq	-17(%rdi), %rdx
	xorl	%r14d, %r14d
.LBB75_9:
	movabsq	$72340172838076672, %r8
	movabsq	$-9187201950435737472, %r9
	.p2align	4
.LBB75_10:
	movq	(%rbx,%r14), %r10
	movq	8(%rbx,%r14), %r11
	movq	%r8, %rsi
	subq	%r10, %rsi
	orq	%r10, %rsi
	movq	%r8, %r10
	subq	%r11, %r10
	orq	%r11, %r10
	andq	%rsi, %r10
	notq	%r10
	testq	%r9, %r10
	jne	.LBB75_18
	addq	$16, %r14
	cmpq	%rdx, %r14
	jbe	.LBB75_10
	jmp	.LBB75_18
.LBB75_12:
	xorl	%edx, %edx
	.p2align	4
.LBB75_13:
	cmpb	$0, (%rbx,%rdx)
	je	.LBB75_22
	incq	%rdx
	cmpq	%rdx, %r14
	jne	.LBB75_13
	leaq	-17(%rdi), %rdx
	cmpq	%rdx, %r14
	ja	.LBB75_18
	jmp	.LBB75_9
	.p2align	4
.LBB75_16:
	cmpb	$0, (%rbx,%r14)
	je	.LBB75_22
	incq	%r14
.LBB75_18:
	cmpq	%r14, %rax
	jne	.LBB75_16
.LBB75_19:
	cmpb	$0, (%rbx,%rax)
	je	.LBB75_23
	addq	%rbx, %rdi
	movzbl	(%rbx), %r8d
	movzbl	%r8b, %r11d
	testb	%r11b, %r11b
	js	.LBB75_25
	incq	%rbx
	jmp	.LBB75_32
.LBB75_22:
	movl	$15, (%rcx)
	jmp	.LBB75_91
.LBB75_23:
	movq	%rcx, -32(%rbp)
	addq	%rbx, %rdi
	movzbl	(%rbx), %ecx
	movzbl	%cl, %r15d
	testb	%r15b, %r15b
	js	.LBB75_28
	incq	%rbx
	xorl	%esi, %esi
	jmp	.LBB75_67
.LBB75_25:
	movl	%r11d, %eax
	andl	$31, %eax
	movzbl	1(%rbx), %edx
	andl	$63, %edx
	cmpb	$-33, %r11b
	jbe	.LBB75_31
	movzbl	2(%rbx), %r11d
	shll	$6, %edx
	andl	$63, %r11d
	orl	%edx, %r11d
	cmpb	$-16, %r8b
	jb	.LBB75_61
	movzbl	3(%rbx), %edx
	addq	$4, %rbx
	andl	$7, %eax
	shll	$18, %eax
	shll	$6, %r11d
	andl	$63, %edx
	orl	%r11d, %edx
	orl	%eax, %edx
	movl	%edx, %r11d
	cmpl	$65535, %r11d
	jbe	.LBB75_32
	jmp	.LBB75_62
.LBB75_28:
	movl	%r15d, %eax
	andl	$31, %eax
	movzbl	1(%rbx), %edx
	andl	$63, %edx
	cmpb	$-33, %r15b
	jbe	.LBB75_60
	movzbl	2(%rbx), %r15d
	shll	$6, %edx
	andl	$63, %r15d
	orl	%edx, %r15d
	cmpb	$-16, %cl
	jb	.LBB75_63
	movzbl	3(%rbx), %ecx
	addq	$4, %rbx
	andl	$7, %eax
	shll	$18, %eax
	shll	$6, %r15d
	andl	$63, %ecx
	orl	%r15d, %ecx
	orl	%eax, %ecx
	movl	%ecx, %r15d
	jmp	.LBB75_64
.LBB75_31:
	addq	$2, %rbx
	shll	$6, %eax
	orl	%edx, %eax
	movl	%eax, %r11d
.LBB75_32:
	movl	$1, %r10d
	xorl	%r13d, %r13d
.LBB75_33:
	movq	%rdi, %rax
	subq	%rbx, %rax
	movabsq	$-6148914691236517205, %rdx
	mulq	%rdx
	shrq	%rdx
	movabsq	$6148914691236517205, %r8
	xorl	%r9d, %r9d
	cmpq	%r8, %rax
	seta	%r9b
	addq	%r10, %rdx
	addq	%r9, %rdx
	cmpq	$4, %rdx
	movl	$3, %esi
	cmovaeq	%rdx, %rsi
	leaq	2(,%rsi,2), %r14
	movabsq	$4611686018427387902, %rax
	cmpq	%rax, %rdx
	jbe	.LBB75_36
	xorl	%r15d, %r15d
	movq	%r15, %rcx
.LBB75_35:
	movq	%r14, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.LBB75_36:
	movq	%r11, -40(%rbp)
	movq	%rcx, -32(%rbp)
	incq	%rsi
	movw	$1, %r12w
.LBB75_37:
	movl	$2, %r15d
	movl	$2, %edx
	movq	%r14, %rcx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB75_93
	movq	-40(%rbp), %rcx
	movw	%cx, (%rax)
	movq	%rsi, -24(%rbp)
	movq	%rax, -16(%rbp)
	movq	$1, -8(%rbp)
	movl	$1, %r14d
	leaq	-24(%rbp), %r15
	jmp	.LBB75_41
	.p2align	4
.LBB75_39:
	movl	%r9d, %r13d
.LBB75_40:
	movw	%si, (%rax,%r14,2)
	incq	%r14
	movq	%r14, -8(%rbp)
.LBB75_41:
	testq	%rbx, %rbx
	je	.LBB75_49
	testw	%r13w, %r13w
	je	.LBB75_46
	xorl	%r9d, %r9d
	movl	%r13d, %esi
.LBB75_44:
	cmpq	-24(%rbp), %r14
	jne	.LBB75_39
	movq	%rdi, %rcx
	subq	%rbx, %rcx
	movq	%rcx, %rax
	movabsq	$-6148914691236517205, %rdx
	mulq	%rdx
	shrq	%rdx
	leaq	(%rdx,%rdx,2), %rax
	xorl	%r8d, %r8d
	cmpq	%rax, %rcx
	setne	%r8b
	cmpw	$1, %r9w
	sbbq	$-1, %rdx
	movzwl	%r12w, %eax
	addq	%rax, %rdx
	addq	%rdx, %r8
	incq	%r8
	movl	%r9d, %r13d
	jmp	.LBB75_51
	.p2align	4
.LBB75_46:
	cmpq	%rdi, %rbx
	je	.LBB75_49
	movzbl	(%rbx), %edx
	movzbl	%dl, %esi
	testb	%sil, %sil
	js	.LBB75_53
	incq	%rbx
	xorl	%r9d, %r9d
	jmp	.LBB75_44
	.p2align	4
.LBB75_49:
	testw	%r12w, %r12w
	je	.LBB75_86
	movl	$1, %r8d
	xorl	%r12d, %r12d
	movl	$0, %ebx
	movl	$0, %esi
	cmpq	-24(%rbp), %r14
	jne	.LBB75_40
.LBB75_51:
.Ltmp26:
	movq	$2, 32(%rsp)
	movl	$2, %r9d
	movq	%r15, %rcx
	movq	%r14, %rdx
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECs5UjBoGikVie_6cudarc
	nop
.Ltmp27:
	movq	-16(%rbp), %rax
	jmp	.LBB75_40
.LBB75_53:
	movl	%esi, %ecx
	andl	$31, %ecx
	movzbl	1(%rbx), %r8d
	andl	$63, %r8d
	cmpb	$-33, %sil
	jbe	.LBB75_57
	movzbl	2(%rbx), %esi
	shll	$6, %r8d
	andl	$63, %esi
	orl	%r8d, %esi
	cmpb	$-16, %dl
	jb	.LBB75_58
	movzbl	3(%rbx), %edx
	addq	$4, %rbx
	andl	$7, %ecx
	shll	$18, %ecx
	shll	$6, %esi
	andl	$63, %edx
	orl	%esi, %edx
	orl	%ecx, %edx
	movl	%edx, %esi
	cmpl	$65535, %esi
	jbe	.LBB75_59
.LBB75_56:
	leal	16711680(%rsi), %ecx
	shrl	$10, %ecx
	orl	$55296, %ecx
	andl	$1023, %esi
	orl	$56320, %esi
	movl	%esi, %r9d
	movl	%ecx, %esi
	jmp	.LBB75_44
.LBB75_57:
	addq	$2, %rbx
	shll	$6, %ecx
	orl	%r8d, %ecx
	movl	%ecx, %esi
	xorl	%r9d, %r9d
	jmp	.LBB75_44
.LBB75_58:
	addq	$3, %rbx
	shll	$12, %ecx
	orl	%ecx, %esi
	cmpl	$65535, %esi
	ja	.LBB75_56
.LBB75_59:
	xorl	%r9d, %r9d
	jmp	.LBB75_44
.LBB75_60:
	addq	$2, %rbx
	shll	$6, %eax
	orl	%edx, %eax
	movl	%eax, %r15d
	xorl	%esi, %esi
	jmp	.LBB75_67
.LBB75_61:
	addq	$3, %rbx
	shll	$12, %eax
	orl	%eax, %r11d
	cmpl	$65535, %r11d
	jbe	.LBB75_32
.LBB75_62:
	leal	16711680(%r11), %eax
	shrl	$10, %eax
	orl	$55296, %eax
	andl	$1023, %r11d
	orl	$56320, %r11d
	movl	$2, %r10d
	movl	%r11d, %r13d
	movl	%eax, %r11d
	jmp	.LBB75_33
.LBB75_63:
	addq	$3, %rbx
	shll	$12, %eax
	orl	%eax, %r15d
.LBB75_64:
	cmpl	$65535, %r15d
	ja	.LBB75_66
	xorl	%esi, %esi
	jmp	.LBB75_67
.LBB75_66:
	leal	16711680(%r15), %eax
	shrl	$10, %eax
	orl	$55296, %eax
	andl	$1023, %r15d
	orl	$56320, %r15d
	movl	%r15d, %esi
	movl	%eax, %r15d
.LBB75_67:
	movq	%rdi, %rax
	subq	%rbx, %rax
	movabsq	$-6148914691236517205, %rcx
	mulq	%rcx
	shrq	%rdx
	movabsq	$6148914691236517205, %r13
	xorl	%ecx, %ecx
	cmpq	%r13, %rax
	seta	%cl
	cmpw	$1, %si
	sbbq	$-1, %rdx
	addq	%rcx, %rdx
	cmpq	$4, %rdx
	movl	$3, %r12d
	cmovaeq	%rdx, %r12
	leaq	2(,%r12,2), %r14
	movabsq	$4611686018427387902, %rax
	cmpq	%rax, %rdx
	jbe	.LBB75_69
	xorl	%ecx, %ecx
	movq	%r14, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.LBB75_69:
	movl	$2, %edx
	movq	%r14, %rcx
	callq	mi_malloc_aligned
	movl	$2, %ecx
	testq	%rax, %rax
	je	.LBB75_35
	incq	%r12
	movw	%r15w, (%rax)
	movq	%r12, -24(%rbp)
	movq	%rax, -16(%rbp)
	movq	$1, -8(%rbp)
	movl	$1, %r14d
	leaq	-24(%rbp), %r15
	jmp	.LBB75_72
	.p2align	4
.LBB75_71:
	movw	%si, (%rax,%r14,2)
	incq	%r14
	movq	%r14, -8(%rbp)
	movl	%r12d, %esi
.LBB75_72:
	testw	%si, %si
	je	.LBB75_74
.LBB75_73:
	xorl	%r12d, %r12d
	cmpq	-24(%rbp), %r14
	jne	.LBB75_71
	jmp	.LBB75_84
	.p2align	4
.LBB75_74:
	cmpq	%rdi, %rbx
	je	.LBB75_86
	movzbl	(%rbx), %edx
	movzbl	%dl, %esi
	testb	%sil, %sil
	js	.LBB75_77
	incq	%rbx
	xorl	%r12d, %r12d
	cmpq	-24(%rbp), %r14
	jne	.LBB75_71
	jmp	.LBB75_84
.LBB75_77:
	movl	%esi, %ecx
	andl	$31, %ecx
	movzbl	1(%rbx), %r8d
	andl	$63, %r8d
	cmpb	$-33, %sil
	jbe	.LBB75_81
	movzbl	2(%rbx), %esi
	shll	$6, %r8d
	andl	$63, %esi
	orl	%r8d, %esi
	cmpb	$-16, %dl
	jb	.LBB75_82
	movzbl	3(%rbx), %edx
	addq	$4, %rbx
	andl	$7, %ecx
	shll	$18, %ecx
	shll	$6, %esi
	andl	$63, %edx
	orl	%esi, %edx
	orl	%ecx, %edx
	movl	%edx, %esi
	cmpl	$65535, %esi
	jbe	.LBB75_73
	jmp	.LBB75_80
.LBB75_81:
	addq	$2, %rbx
	shll	$6, %ecx
	orl	%r8d, %ecx
	movl	%ecx, %esi
	xorl	%r12d, %r12d
	cmpq	-24(%rbp), %r14
	jne	.LBB75_71
	jmp	.LBB75_84
.LBB75_82:
	addq	$3, %rbx
	shll	$12, %ecx
	orl	%ecx, %esi
	cmpl	$65535, %esi
	jbe	.LBB75_73
.LBB75_80:
	leal	16711680(%rsi), %ecx
	shrl	$10, %ecx
	orl	$55296, %ecx
	andl	$1023, %esi
	orl	$56320, %esi
	movl	%esi, %r12d
	movl	%ecx, %esi
	cmpq	-24(%rbp), %r14
	jne	.LBB75_71
	.p2align	4
.LBB75_84:
	movq	%rdi, %rax
	subq	%rbx, %rax
	movabsq	$-6148914691236517205, %rcx
	mulq	%rcx
	shrq	%rdx
	xorl	%ecx, %ecx
	cmpq	%r13, %rax
	seta	%cl
	cmpw	$1, %r12w
	sbbq	$0, %rdx
	leaq	(%rdx,%rcx), %r8
	addq	$2, %r8
.Ltmp24:
	movq	$2, 32(%rsp)
	movl	$2, %r9d
	movq	%r15, %rcx
	movq	%r14, %rdx
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECs5UjBoGikVie_6cudarc
	nop
.Ltmp25:
	movq	-16(%rbp), %rax
	jmp	.LBB75_71
.LBB75_86:
	movq	-24(%rbp), %rsi
	movq	-16(%rbp), %rdi
	movl	$0, -24(%rbp)
	leaq	-24(%rbp), %rdx
	movl	$1, %ecx
	callq	*__imp_SetThreadErrorMode(%rip)
	testl	%eax, %eax
	sete	%al
	movl	-24(%rbp), %ebx
	cmpl	$1, %ebx
	sete	%r14b
	orb	%al, %r14b
	movq	%rdi, %rcx
	xorl	%edx, %edx
	xorl	%r8d, %r8d
	callq	*__imp_LoadLibraryExW(%rip)
	testq	%rax, %rax
	movq	-32(%rbp), %r15
	je	.LBB75_92
	movl	$-1, %ecx
	movq	%rax, 8(%r15)
	movl	%ecx, (%r15)
	testb	%r14b, %r14b
	jne	.LBB75_89
.LBB75_88:
	movl	%ebx, %ecx
	xorl	%edx, %edx
	callq	*__imp_SetThreadErrorMode(%rip)
.LBB75_89:
	testq	%rsi, %rsi
	je	.LBB75_91
	movq	%rdi, %rcx
	callq	mi_free
	nop
.LBB75_91:
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
.LBB75_92:
	callq	*__imp_GetLastError(%rip)
	cmpl	$1, %eax
	movl	$0, %ecx
	adcl	$6, %ecx
	movl	%eax, 4(%r15)
	xorl	%eax, %eax
	movq	%rax, 8(%r15)
	movl	%ecx, (%r15)
	testb	%r14b, %r14b
	je	.LBB75_88
	jmp	.LBB75_89
.LBB75_93:
	movq	%r15, %rcx
	movq	%r14, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RINvXs_NtCskIq6Fm6qntW_10libloading11as_filenameReNtB5_6Sealed16windows_filenameNtNtNtB7_2os7windows7LibraryNCINvMs0_B1i_B1g_15load_with_flagsRNtNtCsfQUUnEvlYZE_5alloc6string6StringE0ECs5UjBoGikVie_6cudarc@IMGREL
	.section	.text,"xr",one_only,_RINvXs_NtCskIq6Fm6qntW_10libloading11as_filenameReNtB5_6Sealed16windows_filenameNtNtNtB7_2os7windows7LibraryNCINvMs0_B1i_B1g_15load_with_flagsRNtNtCsfQUUnEvlYZE_5alloc6string6StringE0ECs5UjBoGikVie_6cudarc,unique,75
	.seh_endproc
	.def	"?dtor$94@?0?_RINvXs_NtCskIq6Fm6qntW_10libloading11as_filenameReNtB5_6Sealed16windows_filenameNtNtNtB7_2os7windows7LibraryNCINvMs0_B1i_B1g_15load_with_flagsRNtNtCsfQUUnEvlYZE_5alloc6string6StringE0ECs5UjBoGikVie_6cudarc@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$94@?0?_RINvXs_NtCskIq6Fm6qntW_10libloading11as_filenameReNtB5_6Sealed16windows_filenameNtNtNtB7_2os7windows7LibraryNCINvMs0_B1i_B1g_15load_with_flagsRNtNtCsfQUUnEvlYZE_5alloc6string6StringE0ECs5UjBoGikVie_6cudarc@4HA":
.seh_proc "?dtor$94@?0?_RINvXs_NtCskIq6Fm6qntW_10libloading11as_filenameReNtB5_6Sealed16windows_filenameNtNtNtB7_2os7windows7LibraryNCINvMs0_B1i_B1g_15load_with_flagsRNtNtCsfQUUnEvlYZE_5alloc6string6StringE0ECs5UjBoGikVie_6cudarc@4HA"
.LBB75_94:
	movq	%rdx, 16(%rsp)
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
	leaq	80(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, -24(%rbp)
	je	.LBB75_96
	movq	-16(%rbp), %rcx
	callq	mi_free
	nop
.LBB75_96:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvXs_NtCskIq6Fm6qntW_10libloading11as_filenameReNtB5_6Sealed16windows_filenameNtNtNtB7_2os7windows7LibraryNCINvMs0_B1i_B1g_15load_with_flagsRNtNtCsfQUUnEvlYZE_5alloc6string6StringE0ECs5UjBoGikVie_6cudarc,unique,75
	.seh_endproc
	.def	"?dtor$97@?0?_RINvXs_NtCskIq6Fm6qntW_10libloading11as_filenameReNtB5_6Sealed16windows_filenameNtNtNtB7_2os7windows7LibraryNCINvMs0_B1i_B1g_15load_with_flagsRNtNtCsfQUUnEvlYZE_5alloc6string6StringE0ECs5UjBoGikVie_6cudarc@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$97@?0?_RINvXs_NtCskIq6Fm6qntW_10libloading11as_filenameReNtB5_6Sealed16windows_filenameNtNtNtB7_2os7windows7LibraryNCINvMs0_B1i_B1g_15load_with_flagsRNtNtCsfQUUnEvlYZE_5alloc6string6StringE0ECs5UjBoGikVie_6cudarc@4HA":
.seh_proc "?dtor$97@?0?_RINvXs_NtCskIq6Fm6qntW_10libloading11as_filenameReNtB5_6Sealed16windows_filenameNtNtNtB7_2os7windows7LibraryNCINvMs0_B1i_B1g_15load_with_flagsRNtNtCsfQUUnEvlYZE_5alloc6string6StringE0ECs5UjBoGikVie_6cudarc@4HA"
.LBB75_97:
	movq	%rdx, 16(%rsp)
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
	leaq	80(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, -24(%rbp)
	je	.LBB75_99
	movq	-16(%rbp), %rcx
	callq	mi_free
	nop
.LBB75_99:
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
.Lfunc_end75:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvXs_NtCskIq6Fm6qntW_10libloading11as_filenameReNtB5_6Sealed16windows_filenameNtNtNtB7_2os7windows7LibraryNCINvMs0_B1i_B1g_15load_with_flagsRNtNtCsfQUUnEvlYZE_5alloc6string6StringE0ECs5UjBoGikVie_6cudarc,unique,75
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvXs_NtCskIq6Fm6qntW_10libloading11as_filenameReNtB5_6Sealed16windows_filenameNtNtNtB7_2os7windows7LibraryNCINvMs0_B1i_B1g_15load_with_flagsRNtNtCsfQUUnEvlYZE_5alloc6string6StringE0ECs5UjBoGikVie_6cudarc,unique,5
	.p2align	2, 0x0
$cppxdata$_RINvXs_NtCskIq6Fm6qntW_10libloading11as_filenameReNtB5_6Sealed16windows_filenameNtNtNtB7_2os7windows7LibraryNCINvMs0_B1i_B1g_15load_with_flagsRNtNtCsfQUUnEvlYZE_5alloc6string6StringE0ECs5UjBoGikVie_6cudarc:
	.long	429065506
	.long	2
	.long	$stateUnwindMap$_RINvXs_NtCskIq6Fm6qntW_10libloading11as_filenameReNtB5_6Sealed16windows_filenameNtNtNtB7_2os7windows7LibraryNCINvMs0_B1i_B1g_15load_with_flagsRNtNtCsfQUUnEvlYZE_5alloc6string6StringE0ECs5UjBoGikVie_6cudarc@IMGREL
	.long	0
	.long	0
	.long	5
	.long	$ip2state$_RINvXs_NtCskIq6Fm6qntW_10libloading11as_filenameReNtB5_6Sealed16windows_filenameNtNtNtB7_2os7windows7LibraryNCINvMs0_B1i_B1g_15load_with_flagsRNtNtCsfQUUnEvlYZE_5alloc6string6StringE0ECs5UjBoGikVie_6cudarc@IMGREL
	.long	80
	.long	0
	.long	1
$stateUnwindMap$_RINvXs_NtCskIq6Fm6qntW_10libloading11as_filenameReNtB5_6Sealed16windows_filenameNtNtNtB7_2os7windows7LibraryNCINvMs0_B1i_B1g_15load_with_flagsRNtNtCsfQUUnEvlYZE_5alloc6string6StringE0ECs5UjBoGikVie_6cudarc:
	.long	-1
	.long	"?dtor$97@?0?_RINvXs_NtCskIq6Fm6qntW_10libloading11as_filenameReNtB5_6Sealed16windows_filenameNtNtNtB7_2os7windows7LibraryNCINvMs0_B1i_B1g_15load_with_flagsRNtNtCsfQUUnEvlYZE_5alloc6string6StringE0ECs5UjBoGikVie_6cudarc@4HA"@IMGREL
	.long	-1
	.long	"?dtor$94@?0?_RINvXs_NtCskIq6Fm6qntW_10libloading11as_filenameReNtB5_6Sealed16windows_filenameNtNtNtB7_2os7windows7LibraryNCINvMs0_B1i_B1g_15load_with_flagsRNtNtCsfQUUnEvlYZE_5alloc6string6StringE0ECs5UjBoGikVie_6cudarc@4HA"@IMGREL
$ip2state$_RINvXs_NtCskIq6Fm6qntW_10libloading11as_filenameReNtB5_6Sealed16windows_filenameNtNtNtB7_2os7windows7LibraryNCINvMs0_B1i_B1g_15load_with_flagsRNtNtCsfQUUnEvlYZE_5alloc6string6StringE0ECs5UjBoGikVie_6cudarc:
	.long	.Lfunc_begin75@IMGREL
	.long	-1
	.long	.Ltmp26@IMGREL
	.long	0
	.long	.Ltmp27@IMGREL
	.long	-1
	.long	.Ltmp24@IMGREL
	.long	1
	.long	.Ltmp25@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvXs_NtCskIq6Fm6qntW_10libloading11as_filenameReNtB5_6Sealed16windows_filenameNtNtNtB7_2os7windows7LibraryNCINvMs0_B1i_B1g_15load_with_flagsRNtNtCsfQUUnEvlYZE_5alloc6string6StringE0ECs5UjBoGikVie_6cudarc,unique,75

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_16cuCtxSynchronize0E0zE0E0B1Q_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_16cuCtxSynchronize0E0zE0E0B1Q_,unique,76
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_16cuCtxSynchronize0E0zE0E0B1Q_:
.Lfunc_begin76:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_16cuCtxSynchronize0E0zE0E0B1Q_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB76_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.590(%rip), %rcx
	movl	$16, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB76_2:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end76:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCNtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumOPaEB1J_E10initializeNCINvB19_11get_or_initNCNvB1L_16cuGetErrorString0E0zE0E0B1P_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCNtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumOPaEB1J_E10initializeNCINvB19_11get_or_initNCNvB1L_16cuGetErrorString0E0zE0E0B1P_,unique,77
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCNtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumOPaEB1J_E10initializeNCINvB19_11get_or_initNCNvB1L_16cuGetErrorString0E0zE0E0B1P_:
.Lfunc_begin77:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCNtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumOPaEB1J_E10initializeNCINvB19_11get_or_initNCNvB1L_16cuGetErrorString0E0zE0E0B1P_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB77_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.592(%rip), %rcx
	movl	$16, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCNtB2_14cudaError_enumOPaEBL_EB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB77_2:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end77:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB2l_13cuMemFreeHost0E0zE0E0B2p_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB2l_13cuMemFreeHost0E0zE0E0B2p_.llvm.1750587498003715262,unique,78
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB2l_13cuMemFreeHost0E0zE0E0B2p_.llvm.1750587498003715262
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB2l_13cuMemFreeHost0E0zE0E0B2p_.llvm.1750587498003715262:
.Lfunc_begin78:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB2l_13cuMemFreeHost0E0zE0E0B2p_.llvm.1750587498003715262
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB78_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.526(%rip), %rcx
	movl	$13, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_11CUstream_stENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB78_2:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end78:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB2n_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB2n_20cuMemcpyDtoHAsync_v20E0zE0E0B2r_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB2n_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB2n_20cuMemcpyDtoHAsync_v20E0zE0E0B2r_.llvm.1750587498003715262,unique,79
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB2n_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB2n_20cuMemcpyDtoHAsync_v20E0zE0E0B2r_.llvm.1750587498003715262
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB2n_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB2n_20cuMemcpyDtoHAsync_v20E0zE0E0B2r_.llvm.1750587498003715262:
.Lfunc_begin79:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB2n_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB2n_20cuMemcpyDtoHAsync_v20E0zE0E0B2r_.llvm.1750587498003715262
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %r14
	movq	$0, (%rax)
	testq	%r14, %r14
	je	.LBB79_20
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.718(%rip), %rsi
	movq	%rsi, 64(%rsp)
	movq	$20, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB79_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.718+7(%rip), %rax
	andq	$-8, %rax
	subq	%rsi, %rax
	jne	.LBB79_5
.LBB79_4:
	xorl	%eax, %eax
	jmp	.LBB79_6
.LBB79_20:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB79_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.718+7(%rip), %rax
	andq	$-8, %rax
	subq	%rsi, %rax
	je	.LBB79_4
.LBB79_5:
	cmpq	$3, %rax
	ja	.LBB79_9
.LBB79_6:
	movq	(%rax,%rsi), %rcx
	movq	8(%rax,%rsi), %rdx
	movabsq	$72340172838076672, %r8
	movq	%r8, %r9
	subq	%rcx, %r9
	orq	%rcx, %r9
	subq	%rdx, %r8
	orq	%rdx, %r8
	andq	%r9, %r8
	notq	%r8
	movabsq	$-9187201950435737472, %rcx
	testq	%rcx, %r8
	jne	.LBB79_9
	cmpq	$3, %rax
	je	.LBB79_13
	orq	$16, %rax
	.p2align	4
.LBB79_9:
	cmpb	$0, (%rax,%rsi)
	je	.LBB79_10
	incq	%rax
	cmpq	$19, %rax
	jne	.LBB79_9
.LBB79_13:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.718(%rip), %rdx
	leaq	40(%rsp), %rcx
	movl	$20, %r8d
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rbx
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rbx, %rdx
	callq	*__imp_GetProcAddress(%rip)
	movq	%rax, %rsi
	testq	%rax, %rax
	je	.LBB79_15
	movl	$-1, %ebp
	xorl	%edi, %edi
	cmpq	$0, 40(%rsp)
	je	.LBB79_18
.LBB79_17:
	movq	%rbx, %rcx
	callq	mi_free
.LBB79_18:
	cmpl	$-1, %ebp
	jne	.LBB79_11
	movq	%rsi, (%r14)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB79_15:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	xorl	%ebp, %ebp
	cmpl	$1, %eax
	adcl	$10, %ebp
	cmpq	$0, 40(%rsp)
	jne	.LBB79_17
	jmp	.LBB79_18
.LBB79_10:
	xorl	%edi, %edi
	movl	$15, %ebp
.LBB79_11:
	movl	%ebp, 40(%rsp)
	movl	%edi, 44(%rsp)
	movq	%rsi, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.Lfunc_end79:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtB1M_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1M_11nvrtcGetPTX0E0zE0E0B1Q_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtB1M_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1M_11nvrtcGetPTX0E0zE0E0B1Q_,unique,80
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtB1M_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1M_11nvrtcGetPTX0E0zE0E0B1Q_:
.Lfunc_begin80:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtB1M_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1M_11nvrtcGetPTX0E0zE0E0B1Q_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB80_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.476(%rip), %rcx
	movl	$11, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB2_13__nvrtcProgramOaENtB2_11nvrtcResultEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB80_2:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end80:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtB1M_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1M_18nvrtcGetProgramLog0E0zE0E0B1Q_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtB1M_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1M_18nvrtcGetProgramLog0E0zE0E0B1Q_,unique,81
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtB1M_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1M_18nvrtcGetProgramLog0E0zE0E0B1Q_:
.Lfunc_begin81:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtB1M_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1M_18nvrtcGetProgramLog0E0zE0E0B1Q_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB81_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.485(%rip), %rcx
	movl	$18, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB2_13__nvrtcProgramOaENtB2_11nvrtcResultEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB81_2:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end81:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtB1M_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1M_15nvrtcGetPTXSize0E0zE0E0B1Q_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtB1M_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1M_15nvrtcGetPTXSize0E0zE0E0B1Q_,unique,82
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtB1M_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1M_15nvrtcGetPTXSize0E0zE0E0B1Q_:
.Lfunc_begin82:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtB1M_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1M_15nvrtcGetPTXSize0E0zE0E0B1Q_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB82_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.481(%rip), %rcx
	movl	$15, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB2_13__nvrtcProgramOjENtB2_11nvrtcResultEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB82_2:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end82:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtB1M_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1M_22nvrtcGetProgramLogSize0E0zE0E0B1Q_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtB1M_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1M_22nvrtcGetProgramLogSize0E0zE0E0B1Q_,unique,83
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtB1M_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1M_22nvrtcGetProgramLogSize0E0zE0E0B1Q_:
.Lfunc_begin83:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtB1M_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1M_22nvrtcGetProgramLogSize0E0zE0E0B1Q_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB83_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.492(%rip), %rcx
	movl	$22, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB2_13__nvrtcProgramOjENtB2_11nvrtcResultEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB83_2:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end83:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramlPPaENtB1M_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1M_19nvrtcCompileProgram0E0zE0E0B1Q_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramlPPaENtB1M_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1M_19nvrtcCompileProgram0E0zE0E0B1Q_,unique,84
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramlPPaENtB1M_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1M_19nvrtcCompileProgram0E0zE0E0B1Q_:
.Lfunc_begin84:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramlPPaENtB1M_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1M_19nvrtcCompileProgram0E0zE0E0B1Q_
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %r14
	movq	$0, (%rax)
	testq	%r14, %r14
	je	.LBB84_20
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.486(%rip), %rsi
	movq	%rsi, 64(%rsp)
	movq	$19, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB84_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.486+7(%rip), %rax
	andq	$-8, %rax
	subq	%rsi, %rax
	jne	.LBB84_5
.LBB84_4:
	xorl	%eax, %eax
	jmp	.LBB84_6
.LBB84_20:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB84_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zEB2f_
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.486+7(%rip), %rax
	andq	$-8, %rax
	subq	%rsi, %rax
	je	.LBB84_4
.LBB84_5:
	cmpq	$2, %rax
	ja	.LBB84_9
.LBB84_6:
	movq	(%rax,%rsi), %rcx
	movq	8(%rax,%rsi), %rdx
	movabsq	$72340172838076672, %r8
	movq	%r8, %r9
	subq	%rcx, %r9
	orq	%rcx, %r9
	subq	%rdx, %r8
	orq	%rdx, %r8
	andq	%r9, %r8
	notq	%r8
	movabsq	$-9187201950435737472, %rcx
	testq	%rcx, %r8
	jne	.LBB84_9
	cmpq	$2, %rax
	je	.LBB84_13
	orq	$16, %rax
	.p2align	4
.LBB84_9:
	cmpb	$0, (%rax,%rsi)
	je	.LBB84_10
	incq	%rax
	cmpq	$18, %rax
	jne	.LBB84_9
.LBB84_13:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.486(%rip), %rdx
	leaq	40(%rsp), %rcx
	movl	$19, %r8d
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rbx
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib3LIB(%rip), %rcx
	movq	%rbx, %rdx
	callq	*__imp_GetProcAddress(%rip)
	movq	%rax, %rsi
	testq	%rax, %rax
	je	.LBB84_15
	movl	$-1, %ebp
	xorl	%edi, %edi
	cmpq	$0, 40(%rsp)
	je	.LBB84_18
.LBB84_17:
	movq	%rbx, %rcx
	callq	mi_free
.LBB84_18:
	cmpl	$-1, %ebp
	jne	.LBB84_11
	movq	%rsi, (%r14)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB84_15:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	xorl	%ebp, %ebp
	cmpl	$1, %eax
	adcl	$10, %ebp
	cmpq	$0, 40(%rsp)
	jne	.LBB84_17
	jmp	.LBB84_18
.LBB84_10:
	xorl	%edi, %edi
	movl	$15, %ebp
.LBB84_11:
	movl	%ebp, 40(%rsp)
	movl	%edi, 44(%rsp)
	movq	%rsi, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB4_13__nvrtcProgramOaENtB4_11nvrtcResultE0B8_
	ud2
.Lfunc_end84:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_17cuEventDestroy_v20E0zE0E0B1Q_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_17cuEventDestroy_v20E0zE0E0B1Q_.llvm.1750587498003715262,unique,85
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_17cuEventDestroy_v20E0zE0E0B1Q_.llvm.1750587498003715262
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_17cuEventDestroy_v20E0zE0E0B1Q_.llvm.1750587498003715262:
.Lfunc_begin85:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_17cuEventDestroy_v20E0zE0E0B1Q_.llvm.1750587498003715262
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB85_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.613(%rip), %rcx
	movl	$17, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_10CUevent_stENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB85_2:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end85:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stONtB1M_11CUstream_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_13cuEventRecord0E0zE0E0B1Q_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stONtB1M_11CUstream_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_13cuEventRecord0E0zE0E0B1Q_.llvm.1750587498003715262,unique,86
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stONtB1M_11CUstream_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_13cuEventRecord0E0zE0E0B1Q_.llvm.1750587498003715262
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stONtB1M_11CUstream_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_13cuEventRecord0E0zE0E0B1Q_.llvm.1750587498003715262:
.Lfunc_begin86:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stONtB1M_11CUstream_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_13cuEventRecord0E0zE0E0B1Q_.llvm.1750587498003715262
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %r14
	movq	$0, (%rax)
	testq	%r14, %r14
	je	.LBB86_10
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.519(%rip), %rax
	movq	%rax, 64(%rsp)
	movq	$13, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB86_2
.LBB86_3:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.519(%rip), %rdx
	leaq	40(%rsp), %rcx
	movl	$13, %r8d
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rdi
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rdi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	movq	%rax, %rsi
	testq	%rax, %rax
	je	.LBB86_5
	movl	$-1, %ebp
	xorl	%ebx, %ebx
	cmpq	$0, 40(%rsp)
	je	.LBB86_8
.LBB86_7:
	movq	%rdi, %rcx
	callq	mi_free
.LBB86_8:
	cmpl	$-1, %ebp
	jne	.LBB86_11
	movq	%rsi, (%r14)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB86_5:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %ebx
	xorl	%ebp, %ebp
	cmpl	$1, %eax
	adcl	$10, %ebp
	cmpq	$0, 40(%rsp)
	jne	.LBB86_7
	jmp	.LBB86_8
.LBB86_10:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB86_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	jmp	.LBB86_3
.LBB86_11:
	movl	%ebp, 40(%rsp)
	movl	%ebx, 44(%rsp)
	movq	%rsi, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.Lfunc_end86:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUgraph_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_14cuGraphDestroy0E0zE0E0B1Q_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUgraph_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_14cuGraphDestroy0E0zE0E0B1Q_.llvm.1750587498003715262,unique,87
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUgraph_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_14cuGraphDestroy0E0zE0E0B1Q_.llvm.1750587498003715262
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUgraph_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_14cuGraphDestroy0E0zE0E0B1Q_.llvm.1750587498003715262:
.Lfunc_begin87:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUgraph_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_14cuGraphDestroy0E0zE0E0B1Q_.llvm.1750587498003715262
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %r14
	movq	$0, (%rax)
	testq	%r14, %r14
	je	.LBB87_10
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.542(%rip), %rax
	movq	%rax, 64(%rsp)
	movq	$14, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB87_2
.LBB87_3:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.542(%rip), %rdx
	leaq	40(%rsp), %rcx
	movl	$14, %r8d
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rdi
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rdi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	movq	%rax, %rsi
	testq	%rax, %rax
	je	.LBB87_5
	movl	$-1, %ebp
	xorl	%ebx, %ebx
	cmpq	$0, 40(%rsp)
	je	.LBB87_8
.LBB87_7:
	movq	%rdi, %rcx
	callq	mi_free
.LBB87_8:
	cmpl	$-1, %ebp
	jne	.LBB87_11
	movq	%rsi, (%r14)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB87_5:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %ebx
	xorl	%ebp, %ebp
	cmpl	$1, %eax
	adcl	$10, %ebp
	cmpq	$0, 40(%rsp)
	jne	.LBB87_7
	jmp	.LBB87_8
.LBB87_10:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB87_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	jmp	.LBB87_3
.LBB87_11:
	movl	%ebp, 40(%rsp)
	movl	%ebx, 44(%rsp)
	movq	%rsi, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.Lfunc_end87:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_18cuStreamDestroy_v20E0zE0E0B1Q_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_18cuStreamDestroy_v20E0zE0E0B1Q_,unique,88
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_18cuStreamDestroy_v20E0zE0E0B1Q_:
.Lfunc_begin88:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_18cuStreamDestroy_v20E0zE0E0B1Q_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB88_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.667(%rip), %rcx
	movl	$18, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_11CUstream_stENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB88_2:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end88:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_19cuStreamSynchronize0E0zE0E0B1Q_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_19cuStreamSynchronize0E0zE0E0B1Q_.llvm.1750587498003715262,unique,89
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_19cuStreamSynchronize0E0zE0E0B1Q_.llvm.1750587498003715262
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_19cuStreamSynchronize0E0zE0E0B1Q_.llvm.1750587498003715262:
.Lfunc_begin89:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_19cuStreamSynchronize0E0zE0E0B1Q_.llvm.1750587498003715262
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB89_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.699(%rip), %rcx
	movl	$19, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_11CUstream_stENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB89_2:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end89:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stNtB1M_24CUstreamCaptureMode_enumENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_23cuStreamBeginCapture_v20E0zE0E0B1Q_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stNtB1M_24CUstreamCaptureMode_enumENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_23cuStreamBeginCapture_v20E0zE0E0B1Q_.llvm.1750587498003715262,unique,90
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stNtB1M_24CUstreamCaptureMode_enumENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_23cuStreamBeginCapture_v20E0zE0E0B1Q_.llvm.1750587498003715262
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stNtB1M_24CUstreamCaptureMode_enumENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_23cuStreamBeginCapture_v20E0zE0E0B1Q_.llvm.1750587498003715262:
.Lfunc_begin90:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stNtB1M_24CUstreamCaptureMode_enumENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_23cuStreamBeginCapture_v20E0zE0E0B1Q_.llvm.1750587498003715262
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %r14
	movq	$0, (%rax)
	testq	%r14, %r14
	je	.LBB90_21
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.788(%rip), %rsi
	movq	%rsi, 64(%rsp)
	movq	$23, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB90_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.788+7(%rip), %rax
	andq	$-8, %rax
	subq	%rsi, %rax
	jne	.LBB90_5
.LBB90_4:
	xorl	%eax, %eax
	jmp	.LBB90_6
.LBB90_21:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB90_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.788+7(%rip), %rax
	andq	$-8, %rax
	subq	%rsi, %rax
	je	.LBB90_4
.LBB90_5:
	movl	$7, %ecx
	cmpq	$7, %rax
	je	.LBB90_10
.LBB90_6:
	movq	(%rax,%rsi), %rcx
	movq	8(%rax,%rsi), %rdx
	movabsq	$72340172838076672, %r8
	movq	%r8, %r9
	subq	%rcx, %r9
	orq	%rcx, %r9
	subq	%rdx, %r8
	orq	%rdx, %r8
	andq	%r9, %r8
	notq	%r8
	movabsq	$-9187201950435737472, %rcx
	testq	%rcx, %r8
	jne	.LBB90_9
	cmpq	$6, %rax
	je	.LBB90_14
	orq	$16, %rax
.LBB90_9:
	movq	%rax, %rcx
	.p2align	4
.LBB90_10:
	cmpb	$0, (%rcx,%rsi)
	je	.LBB90_11
	incq	%rcx
	cmpq	$22, %rcx
	jne	.LBB90_10
.LBB90_14:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.788(%rip), %rdx
	leaq	40(%rsp), %rcx
	movl	$23, %r8d
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rbx
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rbx, %rdx
	callq	*__imp_GetProcAddress(%rip)
	movq	%rax, %rsi
	testq	%rax, %rax
	je	.LBB90_16
	movl	$-1, %ebp
	xorl	%edi, %edi
	cmpq	$0, 40(%rsp)
	je	.LBB90_19
.LBB90_18:
	movq	%rbx, %rcx
	callq	mi_free
.LBB90_19:
	cmpl	$-1, %ebp
	jne	.LBB90_12
	movq	%rsi, (%r14)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB90_16:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	xorl	%ebp, %ebp
	cmpl	$1, %eax
	adcl	$10, %ebp
	cmpq	$0, 40(%rsp)
	jne	.LBB90_18
	jmp	.LBB90_19
.LBB90_11:
	xorl	%edi, %edi
	movl	$15, %ebp
.LBB90_12:
	movl	%ebp, 40(%rsp)
	movl	%edi, 44(%rsp)
	movq	%rsi, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.Lfunc_end90:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stONtB1M_10CUevent_stmENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_17cuStreamWaitEvent0E0zE0E0B1Q_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stONtB1M_10CUevent_stmENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_17cuStreamWaitEvent0E0zE0E0B1Q_.llvm.1750587498003715262,unique,91
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stONtB1M_10CUevent_stmENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_17cuStreamWaitEvent0E0zE0E0B1Q_.llvm.1750587498003715262
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stONtB1M_10CUevent_stmENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_17cuStreamWaitEvent0E0zE0E0B1Q_.llvm.1750587498003715262:
.Lfunc_begin91:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stONtB1M_10CUevent_stmENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_17cuStreamWaitEvent0E0zE0E0B1Q_.llvm.1750587498003715262
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %r14
	movq	$0, (%rax)
	testq	%r14, %r14
	je	.LBB91_15
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.628(%rip), %rsi
	movq	%rsi, 64(%rsp)
	movq	$17, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB91_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.628+7(%rip), %rax
	andq	$-8, %rax
	subq	%rsi, %rax
	je	.LBB91_8
	.p2align	4
.LBB91_4:
	cmpb	$0, (%rax,%rsi)
	je	.LBB91_5
	incq	%rax
	cmpq	$16, %rax
	jne	.LBB91_4
.LBB91_8:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.628(%rip), %rdx
	leaq	40(%rsp), %rcx
	movl	$17, %r8d
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rbx
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rbx, %rdx
	callq	*__imp_GetProcAddress(%rip)
	movq	%rax, %rsi
	testq	%rax, %rax
	je	.LBB91_10
	movl	$-1, %ebp
	xorl	%edi, %edi
	cmpq	$0, 40(%rsp)
	je	.LBB91_13
.LBB91_12:
	movq	%rbx, %rcx
	callq	mi_free
.LBB91_13:
	cmpl	$-1, %ebp
	jne	.LBB91_6
	movq	%rsi, (%r14)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB91_10:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	xorl	%ebp, %ebp
	cmpl	$1, %eax
	adcl	$10, %ebp
	cmpq	$0, 40(%rsp)
	jne	.LBB91_12
	jmp	.LBB91_13
.LBB91_15:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB91_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.628+7(%rip), %rax
	andq	$-8, %rax
	subq	%rsi, %rax
	jne	.LBB91_4
	jmp	.LBB91_8
.LBB91_5:
	xorl	%edi, %edi
	movl	$15, %ebp
.LBB91_6:
	movl	%ebp, 40(%rsp)
	movl	%edi, 44(%rsp)
	movq	%rsi, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.Lfunc_end91:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stOONtB1M_10CUgraph_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_18cuStreamEndCapture0E0zE0E0B1Q_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stOONtB1M_10CUgraph_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_18cuStreamEndCapture0E0zE0E0B1Q_,unique,92
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stOONtB1M_10CUgraph_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_18cuStreamEndCapture0E0zE0E0B1Q_:
.Lfunc_begin92:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stOONtB1M_10CUgraph_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_18cuStreamEndCapture0E0zE0E0B1Q_
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %r14
	movq	$0, (%rax)
	testq	%r14, %r14
	je	.LBB92_23
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.668(%rip), %rdi
	movq	%rdi, 64(%rsp)
	movq	$18, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB92_2
.LBB92_3:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.668+7(%rip), %rax
	andq	$-8, %rax
	movq	%rax, %rdx
	subq	%rdi, %rdx
	jne	.LBB92_5
	xorl	%ecx, %ecx
	jmp	.LBB92_6
.LBB92_5:
	movl	$1, %ecx
	cmpq	$1, %rdx
	ja	.LBB92_8
.LBB92_6:
	movq	(%rcx,%rdi), %rdx
	movq	8(%rcx,%rdi), %r8
	movabsq	$72340172838076672, %r9
	movq	%r9, %r10
	subq	%rdx, %r10
	orq	%rdx, %r10
	subq	%r8, %r9
	orq	%r8, %r9
	andq	%r10, %r9
	notq	%r9
	movabsq	$-9187201950435737472, %rdx
	testq	%rdx, %r9
	jne	.LBB92_7
	cmpq	%rdi, %rax
	jne	.LBB92_16
	addq	%rcx, %rdi
	addq	$16, %rdi
	movl	$1, %eax
	jmp	.LBB92_11
.LBB92_7:
	movq	%rcx, %rdx
.LBB92_8:
	addq	%rdx, %rdi
	movl	$17, %eax
	subq	%rdx, %rax
.LBB92_11:
	xorl	%esi, %esi
	xorl	%ecx, %ecx
	.p2align	4
.LBB92_12:
	cmpb	$0, (%rdi,%rcx)
	je	.LBB92_13
	incq	%rcx
	cmpq	%rcx, %rax
	jne	.LBB92_12
.LBB92_16:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.668(%rip), %rdx
	leaq	40(%rsp), %rcx
	movl	$18, %r8d
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rbx
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rbx, %rdx
	callq	*__imp_GetProcAddress(%rip)
	movq	%rax, %rdi
	testq	%rax, %rax
	je	.LBB92_18
	movl	$-1, %ebp
	xorl	%esi, %esi
	cmpq	$0, 40(%rsp)
	je	.LBB92_21
.LBB92_20:
	movq	%rbx, %rcx
	callq	mi_free
.LBB92_21:
	cmpl	$-1, %ebp
	jne	.LBB92_14
	movq	%rdi, (%r14)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB92_18:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %esi
	xorl	%ebp, %ebp
	cmpl	$1, %eax
	adcl	$10, %ebp
	cmpq	$0, 40(%rsp)
	jne	.LBB92_20
	jmp	.LBB92_21
.LBB92_23:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB92_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	jmp	.LBB92_3
.LBB92_13:
	movl	$15, %ebp
.LBB92_14:
	movl	%ebp, 40(%rsp)
	movl	%esi, 44(%rsp)
	movq	%rdi, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.Lfunc_end92:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_18cuGraphExecDestroy0E0zE0E0B1Q_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_18cuGraphExecDestroy0E0zE0E0B1Q_.llvm.1750587498003715262,unique,93
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_18cuGraphExecDestroy0E0zE0E0B1Q_.llvm.1750587498003715262
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_18cuGraphExecDestroy0E0zE0E0B1Q_.llvm.1750587498003715262:
.Lfunc_begin93:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_18cuGraphExecDestroy0E0zE0E0B1Q_.llvm.1750587498003715262
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %r14
	movq	$0, (%rax)
	testq	%r14, %r14
	je	.LBB93_23
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.648(%rip), %rdi
	movq	%rdi, 64(%rsp)
	movq	$18, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB93_2
.LBB93_3:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.648+7(%rip), %rax
	andq	$-8, %rax
	movq	%rax, %rdx
	subq	%rdi, %rdx
	jne	.LBB93_5
	xorl	%ecx, %ecx
	jmp	.LBB93_6
.LBB93_5:
	movl	$1, %ecx
	cmpq	$1, %rdx
	ja	.LBB93_8
.LBB93_6:
	movq	(%rcx,%rdi), %rdx
	movq	8(%rcx,%rdi), %r8
	movabsq	$72340172838076672, %r9
	movq	%r9, %r10
	subq	%rdx, %r10
	orq	%rdx, %r10
	subq	%r8, %r9
	orq	%r8, %r9
	andq	%r10, %r9
	notq	%r9
	movabsq	$-9187201950435737472, %rdx
	testq	%rdx, %r9
	jne	.LBB93_7
	cmpq	%rdi, %rax
	jne	.LBB93_16
	addq	%rcx, %rdi
	addq	$16, %rdi
	movl	$1, %eax
	jmp	.LBB93_11
.LBB93_7:
	movq	%rcx, %rdx
.LBB93_8:
	addq	%rdx, %rdi
	movl	$17, %eax
	subq	%rdx, %rax
.LBB93_11:
	xorl	%esi, %esi
	xorl	%ecx, %ecx
	.p2align	4
.LBB93_12:
	cmpb	$0, (%rdi,%rcx)
	je	.LBB93_13
	incq	%rcx
	cmpq	%rcx, %rax
	jne	.LBB93_12
.LBB93_16:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.648(%rip), %rdx
	leaq	40(%rsp), %rcx
	movl	$18, %r8d
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rbx
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rbx, %rdx
	callq	*__imp_GetProcAddress(%rip)
	movq	%rax, %rdi
	testq	%rax, %rax
	je	.LBB93_18
	movl	$-1, %ebp
	xorl	%esi, %esi
	cmpq	$0, 40(%rsp)
	je	.LBB93_21
.LBB93_20:
	movq	%rbx, %rcx
	callq	mi_free
.LBB93_21:
	cmpl	$-1, %ebp
	jne	.LBB93_14
	movq	%rdi, (%r14)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB93_18:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %esi
	xorl	%ebp, %ebp
	cmpl	$1, %eax
	adcl	$10, %ebp
	cmpq	$0, 40(%rsp)
	jne	.LBB93_20
	jmp	.LBB93_21
.LBB93_23:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB93_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	jmp	.LBB93_3
.LBB93_13:
	movl	$15, %ebp
.LBB93_14:
	movl	%ebp, 40(%rsp)
	movl	%esi, 44(%rsp)
	movq	%rdi, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.Lfunc_end93:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB1M_11CUstream_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_13cuGraphLaunch0E0zE0E0B1Q_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB1M_11CUstream_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_13cuGraphLaunch0E0zE0E0B1Q_.llvm.1750587498003715262,unique,94
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB1M_11CUstream_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_13cuGraphLaunch0E0zE0E0B1Q_.llvm.1750587498003715262
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB1M_11CUstream_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_13cuGraphLaunch0E0zE0E0B1Q_.llvm.1750587498003715262:
.Lfunc_begin94:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB1M_11CUstream_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_13cuGraphLaunch0E0zE0E0B1Q_.llvm.1750587498003715262
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB94_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.522(%rip), %rcx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_14CUgraphExec_stONtB2_11CUstream_stENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB94_2:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end94:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_15cuCtxDestroy_v20E0zE0E0B1Q_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_15cuCtxDestroy_v20E0zE0E0B1Q_,unique,95
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_15cuCtxDestroy_v20E0zE0E0B1Q_:
.Lfunc_begin95:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_15cuCtxDestroy_v20E0zE0E0B1Q_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB95_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.560(%rip), %rcx
	movl	$15, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_8CUctx_stENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB95_2:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end95:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_15cuCtxSetCurrent0E0zE0E0B1Q_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_15cuCtxSetCurrent0E0zE0E0B1Q_.llvm.1750587498003715262,unique,96
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_15cuCtxSetCurrent0E0zE0E0B1Q_.llvm.1750587498003715262
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_15cuCtxSetCurrent0E0zE0E0B1Q_.llvm.1750587498003715262:
.Lfunc_begin96:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_15cuCtxSetCurrent0E0zE0E0B1Q_.llvm.1750587498003715262
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB96_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.562(%rip), %rcx
	movl	$15, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_8CUctx_stENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB96_2:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end96:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_14cuModuleUnload0E0zE0E0B1Q_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_14cuModuleUnload0E0zE0E0B1Q_.llvm.1750587498003715262,unique,97
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_14cuModuleUnload0E0zE0E0B1Q_.llvm.1750587498003715262
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_14cuModuleUnload0E0zE0E0B1Q_.llvm.1750587498003715262:
.Lfunc_begin97:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_14cuModuleUnload0E0zE0E0B1Q_.llvm.1750587498003715262
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %r14
	movq	$0, (%rax)
	testq	%r14, %r14
	je	.LBB97_10
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.553(%rip), %rax
	movq	%rax, 64(%rsp)
	movq	$14, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB97_2
.LBB97_3:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.553(%rip), %rdx
	leaq	40(%rsp), %rcx
	movl	$14, %r8d
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rdi
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rdi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	movq	%rax, %rsi
	testq	%rax, %rax
	je	.LBB97_5
	movl	$-1, %ebp
	xorl	%ebx, %ebx
	cmpq	$0, 40(%rsp)
	je	.LBB97_8
.LBB97_7:
	movq	%rdi, %rcx
	callq	mi_free
.LBB97_8:
	cmpl	$-1, %ebp
	jne	.LBB97_11
	movq	%rsi, (%r14)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB97_5:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %ebx
	xorl	%ebp, %ebp
	cmpl	$1, %eax
	adcl	$10, %ebp
	cmpq	$0, 40(%rsp)
	jne	.LBB97_7
	jmp	.LBB97_8
.LBB97_10:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB97_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	jmp	.LBB97_3
.LBB97_11:
	movl	%ebp, 40(%rsp)
	movl	%ebx, 44(%rsp)
	movq	%rsi, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.Lfunc_end97:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stmmmmmmmONtB1M_11CUstream_stOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidB2X_ENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_14cuLaunchKernel0E0zE0E0B1Q_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stmmmmmmmONtB1M_11CUstream_stOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidB2X_ENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_14cuLaunchKernel0E0zE0E0B1Q_.llvm.1750587498003715262,unique,98
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stmmmmmmmONtB1M_11CUstream_stOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidB2X_ENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_14cuLaunchKernel0E0zE0E0B1Q_.llvm.1750587498003715262
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stmmmmmmmONtB1M_11CUstream_stOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidB2X_ENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_14cuLaunchKernel0E0zE0E0B1Q_.llvm.1750587498003715262:
.Lfunc_begin98:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stmmmmmmmONtB1M_11CUstream_stOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidB2X_ENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_14cuLaunchKernel0E0zE0E0B1Q_.llvm.1750587498003715262
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %r14
	movq	$0, (%rax)
	testq	%r14, %r14
	je	.LBB98_10
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.543(%rip), %rax
	movq	%rax, 64(%rsp)
	movq	$14, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB98_2
.LBB98_3:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.543(%rip), %rdx
	leaq	40(%rsp), %rcx
	movl	$14, %r8d
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rdi
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rdi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	movq	%rax, %rsi
	testq	%rax, %rax
	je	.LBB98_5
	movl	$-1, %ebp
	xorl	%ebx, %ebx
	cmpq	$0, 40(%rsp)
	je	.LBB98_8
.LBB98_7:
	movq	%rdi, %rcx
	callq	mi_free
.LBB98_8:
	cmpl	$-1, %ebp
	jne	.LBB98_11
	movq	%rsi, (%r14)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB98_5:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %ebx
	xorl	%ebp, %ebp
	cmpl	$1, %eax
	adcl	$10, %ebp
	cmpq	$0, 40(%rsp)
	jne	.LBB98_7
	jmp	.LBB98_8
.LBB98_10:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB98_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	jmp	.LBB98_3
.LBB98_11:
	movl	%ebp, 40(%rsp)
	movl	%ebx, 44(%rsp)
	movq	%rsi, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.Lfunc_end98:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidjmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB2o_14cuMemHostAlloc0E0zE0E0B2s_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidjmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB2o_14cuMemHostAlloc0E0zE0E0B2s_.llvm.1750587498003715262,unique,99
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidjmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB2o_14cuMemHostAlloc0E0zE0E0B2s_.llvm.1750587498003715262
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidjmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB2o_14cuMemHostAlloc0E0zE0E0B2s_.llvm.1750587498003715262:
.Lfunc_begin99:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidjmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB2o_14cuMemHostAlloc0E0zE0E0B2s_.llvm.1750587498003715262
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %r14
	movq	$0, (%rax)
	testq	%r14, %r14
	je	.LBB99_10
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.548(%rip), %rax
	movq	%rax, 64(%rsp)
	movq	$14, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB99_2
.LBB99_3:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.548(%rip), %rdx
	leaq	40(%rsp), %rcx
	movl	$14, %r8d
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rdi
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rdi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	movq	%rax, %rsi
	testq	%rax, %rax
	je	.LBB99_5
	movl	$-1, %ebp
	xorl	%ebx, %ebx
	cmpq	$0, 40(%rsp)
	je	.LBB99_8
.LBB99_7:
	movq	%rdi, %rcx
	callq	mi_free
.LBB99_8:
	cmpl	$-1, %ebp
	jne	.LBB99_11
	movq	%rsi, (%r14)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB99_5:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %ebx
	xorl	%ebp, %ebp
	cmpl	$1, %eax
	adcl	$10, %ebp
	cmpq	$0, 40(%rsp)
	jne	.LBB99_7
	jmp	.LBB99_8
.LBB99_10:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB99_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	jmp	.LBB99_3
.LBB99_11:
	movl	%ebp, 40(%rsp)
	movl	%ebx, 44(%rsp)
	movq	%rsi, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.Lfunc_end99:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramENtB1N_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1N_19nvrtcDestroyProgram0E0zE0E0B1R_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramENtB1N_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1N_19nvrtcDestroyProgram0E0zE0E0B1R_,unique,100
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramENtB1N_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1N_19nvrtcDestroyProgram0E0zE0E0B1R_:
.Lfunc_begin100:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramENtB1N_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1N_19nvrtcDestroyProgram0E0zE0E0B1R_
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %r14
	movq	$0, (%rax)
	testq	%r14, %r14
	je	.LBB100_20
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.487(%rip), %rsi
	movq	%rsi, 64(%rsp)
	movq	$19, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB100_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.487+7(%rip), %rax
	andq	$-8, %rax
	subq	%rsi, %rax
	jne	.LBB100_5
.LBB100_4:
	xorl	%eax, %eax
	jmp	.LBB100_6
.LBB100_20:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB100_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zEB2f_
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.487+7(%rip), %rax
	andq	$-8, %rax
	subq	%rsi, %rax
	je	.LBB100_4
.LBB100_5:
	cmpq	$2, %rax
	ja	.LBB100_9
.LBB100_6:
	movq	(%rax,%rsi), %rcx
	movq	8(%rax,%rsi), %rdx
	movabsq	$72340172838076672, %r8
	movq	%r8, %r9
	subq	%rcx, %r9
	orq	%rcx, %r9
	subq	%rdx, %r8
	orq	%rdx, %r8
	andq	%r9, %r8
	notq	%r8
	movabsq	$-9187201950435737472, %rcx
	testq	%rcx, %r8
	jne	.LBB100_9
	cmpq	$2, %rax
	je	.LBB100_13
	orq	$16, %rax
	.p2align	4
.LBB100_9:
	cmpb	$0, (%rax,%rsi)
	je	.LBB100_10
	incq	%rax
	cmpq	$18, %rax
	jne	.LBB100_9
.LBB100_13:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.487(%rip), %rdx
	leaq	40(%rsp), %rcx
	movl	$19, %r8d
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rbx
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib3LIB(%rip), %rcx
	movq	%rbx, %rdx
	callq	*__imp_GetProcAddress(%rip)
	movq	%rax, %rsi
	testq	%rax, %rax
	je	.LBB100_15
	movl	$-1, %ebp
	xorl	%edi, %edi
	cmpq	$0, 40(%rsp)
	je	.LBB100_18
.LBB100_17:
	movq	%rbx, %rcx
	callq	mi_free
.LBB100_18:
	cmpl	$-1, %ebp
	jne	.LBB100_11
	movq	%rsi, (%r14)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB100_15:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	xorl	%ebp, %ebp
	cmpl	$1, %eax
	adcl	$10, %ebp
	cmpq	$0, 40(%rsp)
	jne	.LBB100_17
	jmp	.LBB100_18
.LBB100_10:
	xorl	%edi, %edi
	movl	$15, %ebp
.LBB100_11:
	movl	%ebp, 40(%rsp)
	movl	%edi, 44(%rsp)
	movq	%rsi, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB4_13__nvrtcProgramOaENtB4_11nvrtcResultE0B8_
	ud2
.Lfunc_end100:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramPaB2C_lPB2C_B2J_ENtB1N_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1N_18nvrtcCreateProgram0E0zE0E0B1R_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramPaB2C_lPB2C_B2J_ENtB1N_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1N_18nvrtcCreateProgram0E0zE0E0B1R_.llvm.1750587498003715262,unique,101
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramPaB2C_lPB2C_B2J_ENtB1N_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1N_18nvrtcCreateProgram0E0zE0E0B1R_.llvm.1750587498003715262
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramPaB2C_lPB2C_B2J_ENtB1N_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1N_18nvrtcCreateProgram0E0zE0E0B1R_.llvm.1750587498003715262:
.Lfunc_begin101:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramPaB2C_lPB2C_B2J_ENtB1N_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1N_18nvrtcCreateProgram0E0zE0E0B1R_.llvm.1750587498003715262
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %r14
	movq	$0, (%rax)
	testq	%r14, %r14
	je	.LBB101_23
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.484(%rip), %rdi
	movq	%rdi, 64(%rsp)
	movq	$18, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB101_2
.LBB101_3:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.484+7(%rip), %rax
	andq	$-8, %rax
	movq	%rax, %rdx
	subq	%rdi, %rdx
	jne	.LBB101_5
	xorl	%ecx, %ecx
	jmp	.LBB101_6
.LBB101_5:
	movl	$1, %ecx
	cmpq	$1, %rdx
	ja	.LBB101_8
.LBB101_6:
	movq	(%rcx,%rdi), %rdx
	movq	8(%rcx,%rdi), %r8
	movabsq	$72340172838076672, %r9
	movq	%r9, %r10
	subq	%rdx, %r10
	orq	%rdx, %r10
	subq	%r8, %r9
	orq	%r8, %r9
	andq	%r10, %r9
	notq	%r9
	movabsq	$-9187201950435737472, %rdx
	testq	%rdx, %r9
	jne	.LBB101_7
	cmpq	%rdi, %rax
	jne	.LBB101_16
	addq	%rcx, %rdi
	addq	$16, %rdi
	movl	$1, %eax
	jmp	.LBB101_11
.LBB101_7:
	movq	%rcx, %rdx
.LBB101_8:
	addq	%rdx, %rdi
	movl	$17, %eax
	subq	%rdx, %rax
.LBB101_11:
	xorl	%esi, %esi
	xorl	%ecx, %ecx
	.p2align	4
.LBB101_12:
	cmpb	$0, (%rdi,%rcx)
	je	.LBB101_13
	incq	%rcx
	cmpq	%rcx, %rax
	jne	.LBB101_12
.LBB101_16:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.484(%rip), %rdx
	leaq	40(%rsp), %rcx
	movl	$18, %r8d
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rbx
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib3LIB(%rip), %rcx
	movq	%rbx, %rdx
	callq	*__imp_GetProcAddress(%rip)
	movq	%rax, %rdi
	testq	%rax, %rax
	je	.LBB101_18
	movl	$-1, %ebp
	xorl	%esi, %esi
	cmpq	$0, 40(%rsp)
	je	.LBB101_21
.LBB101_20:
	movq	%rbx, %rcx
	callq	mi_free
.LBB101_21:
	cmpl	$-1, %ebp
	jne	.LBB101_14
	movq	%rdi, (%r14)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB101_18:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %esi
	xorl	%ebp, %ebp
	cmpl	$1, %eax
	adcl	$10, %ebp
	cmpq	$0, 40(%rsp)
	jne	.LBB101_20
	jmp	.LBB101_21
.LBB101_23:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB101_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zEB2f_
	jmp	.LBB101_3
.LBB101_13:
	movl	$15, %ebp
.LBB101_14:
	movl	%ebp, 40(%rsp)
	movl	%esi, 44(%rsp)
	movq	%rdi, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB4_13__nvrtcProgramOaENtB4_11nvrtcResultE0B8_
	ud2
.Lfunc_end101:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stmENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_13cuEventCreate0E0zE0E0B1R_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stmENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_13cuEventCreate0E0zE0E0B1R_.llvm.1750587498003715262,unique,102
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stmENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_13cuEventCreate0E0zE0E0B1R_.llvm.1750587498003715262
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stmENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_13cuEventCreate0E0zE0E0B1R_.llvm.1750587498003715262:
.Lfunc_begin102:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stmENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_13cuEventCreate0E0zE0E0B1R_.llvm.1750587498003715262
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %r14
	movq	$0, (%rax)
	testq	%r14, %r14
	je	.LBB102_10
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.518(%rip), %rax
	movq	%rax, 64(%rsp)
	movq	$13, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB102_2
.LBB102_3:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.518(%rip), %rdx
	leaq	40(%rsp), %rcx
	movl	$13, %r8d
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rdi
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rdi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	movq	%rax, %rsi
	testq	%rax, %rax
	je	.LBB102_5
	movl	$-1, %ebp
	xorl	%ebx, %ebx
	cmpq	$0, 40(%rsp)
	je	.LBB102_8
.LBB102_7:
	movq	%rdi, %rcx
	callq	mi_free
.LBB102_8:
	cmpl	$-1, %ebp
	jne	.LBB102_11
	movq	%rsi, (%r14)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB102_5:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %ebx
	xorl	%ebp, %ebp
	cmpl	$1, %eax
	adcl	$10, %ebp
	cmpq	$0, 40(%rsp)
	jne	.LBB102_7
	jmp	.LBB102_8
.LBB102_10:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB102_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	jmp	.LBB102_3
.LBB102_11:
	movl	%ebp, 40(%rsp)
	movl	%ebx, 44(%rsp)
	movq	%rsi, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.Lfunc_end102:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stmENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_14cuStreamCreate0E0zE0E0B1R_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stmENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_14cuStreamCreate0E0zE0E0B1R_,unique,103
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stmENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_14cuStreamCreate0E0zE0E0B1R_:
.Lfunc_begin103:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stmENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_14cuStreamCreate0E0zE0E0B1R_
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %r14
	movq	$0, (%rax)
	testq	%r14, %r14
	je	.LBB103_10
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.556(%rip), %rax
	movq	%rax, 64(%rsp)
	movq	$14, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB103_2
.LBB103_3:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.556(%rip), %rdx
	leaq	40(%rsp), %rcx
	movl	$14, %r8d
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rdi
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rdi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	movq	%rax, %rsi
	testq	%rax, %rax
	je	.LBB103_5
	movl	$-1, %ebp
	xorl	%ebx, %ebx
	cmpq	$0, 40(%rsp)
	je	.LBB103_8
.LBB103_7:
	movq	%rdi, %rcx
	callq	mi_free
.LBB103_8:
	cmpl	$-1, %ebp
	jne	.LBB103_11
	movq	%rsi, (%r14)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB103_5:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %ebx
	xorl	%ebp, %ebp
	cmpl	$1, %eax
	adcl	$10, %ebp
	cmpq	$0, 40(%rsp)
	jne	.LBB103_7
	jmp	.LBB103_8
.LBB103_10:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB103_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	jmp	.LBB103_3
.LBB103_11:
	movl	%ebp, 40(%rsp)
	movl	%ebx, 44(%rsp)
	movq	%rsi, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.Lfunc_end103:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB1N_10CUgraph_styENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_27cuGraphInstantiateWithFlags0E0zE0E0B1R_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB1N_10CUgraph_styENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_27cuGraphInstantiateWithFlags0E0zE0E0B1R_,unique,104
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB1N_10CUgraph_styENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_27cuGraphInstantiateWithFlags0E0zE0E0B1R_:
.Lfunc_begin104:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB1N_10CUgraph_styENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_27cuGraphInstantiateWithFlags0E0zE0E0B1R_
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %r14
	movq	$0, (%rax)
	testq	%r14, %r14
	je	.LBB104_15
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.842(%rip), %rsi
	movq	%rsi, 64(%rsp)
	movq	$27, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB104_2
.LBB104_3:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.842+7(%rip), %rax
	andq	$-8, %rax
	movq	(%rax), %rcx
	movq	8(%rax), %rdx
	movq	%rax, %r8
	subq	%rsi, %r8
	movabsq	$72340172838076672, %r9
	movq	%r9, %rax
	subq	%rcx, %rax
	orq	%rcx, %rax
	subq	%rdx, %r9
	orq	%rdx, %r9
	andq	%rax, %r9
	notq	%r9
	movq	%r8, %rax
	orq	$16, %rax
	movabsq	$-9187201950435737472, %rcx
	testq	%rcx, %r9
	cmovneq	%r8, %rax
	.p2align	4
.LBB104_4:
	cmpb	$0, (%rax,%rsi)
	je	.LBB104_5
	incq	%rax
	cmpq	$26, %rax
	jne	.LBB104_4
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.842(%rip), %rdx
	leaq	40(%rsp), %rcx
	movl	$27, %r8d
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rbx
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rbx, %rdx
	callq	*__imp_GetProcAddress(%rip)
	movq	%rax, %rsi
	testq	%rax, %rax
	je	.LBB104_10
	movl	$-1, %ebp
	xorl	%edi, %edi
	cmpq	$0, 40(%rsp)
	je	.LBB104_13
.LBB104_12:
	movq	%rbx, %rcx
	callq	mi_free
.LBB104_13:
	cmpl	$-1, %ebp
	jne	.LBB104_6
	movq	%rsi, (%r14)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB104_10:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	xorl	%ebp, %ebp
	cmpl	$1, %eax
	adcl	$10, %ebp
	cmpq	$0, 40(%rsp)
	jne	.LBB104_12
	jmp	.LBB104_13
.LBB104_15:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB104_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	jmp	.LBB104_3
.LBB104_5:
	xorl	%edi, %edi
	movl	$15, %ebp
.LBB104_6:
	movl	%ebp, 40(%rsp)
	movl	%edi, 44(%rsp)
	movq	%rsi, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.Lfunc_end104:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_15cuCtxGetCurrent0E0zE0E0B1R_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_15cuCtxGetCurrent0E0zE0E0B1R_.llvm.1750587498003715262,unique,105
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_15cuCtxGetCurrent0E0zE0E0B1R_.llvm.1750587498003715262
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_15cuCtxGetCurrent0E0zE0E0B1R_.llvm.1750587498003715262:
.Lfunc_begin105:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_15cuCtxGetCurrent0E0zE0E0B1R_.llvm.1750587498003715262
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB105_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.561(%rip), %rcx
	movl	$15, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCOONtB2_8CUctx_stENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB105_2:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end105:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stlENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_24cuDevicePrimaryCtxRetain0E0zE0E0B1R_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stlENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_24cuDevicePrimaryCtxRetain0E0zE0E0B1R_,unique,106
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stlENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_24cuDevicePrimaryCtxRetain0E0zE0E0B1R_:
.Lfunc_begin106:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stlENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_24cuDevicePrimaryCtxRetain0E0zE0E0B1R_
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %r14
	movq	$0, (%rax)
	testq	%r14, %r14
	je	.LBB106_16
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.793(%rip), %rsi
	movq	%rsi, 64(%rsp)
	movq	$24, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB106_2
.LBB106_3:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.793+7(%rip), %rax
	andq	$-8, %rax
	movq	(%rax), %rcx
	movq	8(%rax), %rdx
	movq	%rax, %r8
	subq	%rsi, %r8
	movabsq	$72340172838076672, %r9
	movq	%r9, %rax
	subq	%rcx, %rax
	orq	%rcx, %rax
	subq	%rdx, %r9
	orq	%rdx, %r9
	andq	%rax, %r9
	notq	%r9
	movq	%r8, %rax
	orq	$16, %rax
	movabsq	$-9187201950435737472, %rcx
	testq	%rcx, %r9
	cmovneq	%r8, %rax
	cmpq	$23, %rax
	je	.LBB106_9
	.p2align	4
.LBB106_5:
	cmpb	$0, (%rax,%rsi)
	je	.LBB106_6
	incq	%rax
	cmpq	$23, %rax
	jne	.LBB106_5
.LBB106_9:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.793(%rip), %rdx
	leaq	40(%rsp), %rcx
	movl	$24, %r8d
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rbx
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rbx, %rdx
	callq	*__imp_GetProcAddress(%rip)
	movq	%rax, %rsi
	testq	%rax, %rax
	je	.LBB106_11
	movl	$-1, %ebp
	xorl	%edi, %edi
	cmpq	$0, 40(%rsp)
	je	.LBB106_14
.LBB106_13:
	movq	%rbx, %rcx
	callq	mi_free
.LBB106_14:
	cmpl	$-1, %ebp
	jne	.LBB106_7
	movq	%rsi, (%r14)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB106_11:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	xorl	%ebp, %ebp
	cmpl	$1, %eax
	adcl	$10, %ebp
	cmpq	$0, 40(%rsp)
	jne	.LBB106_13
	jmp	.LBB106_14
.LBB106_16:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB106_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	jmp	.LBB106_3
.LBB106_6:
	xorl	%edi, %edi
	movl	$15, %ebp
.LBB106_7:
	movl	%ebp, 40(%rsp)
	movl	%edi, 44(%rsp)
	movq	%rsi, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.Lfunc_end106:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_16cuModuleLoadData0E0zE0E0B1R_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_16cuModuleLoadData0E0zE0E0B1R_,unique,107
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_16cuModuleLoadData0E0zE0E0B1R_:
.Lfunc_begin107:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_16cuModuleLoadData0E0zE0E0B1R_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB107_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.605(%rip), %rcx
	movl	$16, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCOONtB2_8CUmod_stPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB107_2:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end107:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPaENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_12cuModuleLoad0E0zE0E0B1R_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPaENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_12cuModuleLoad0E0zE0E0B1R_,unique,108
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPaENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_12cuModuleLoad0E0zE0E0B1R_:
.Lfunc_begin108:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPaENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_12cuModuleLoad0E0zE0E0B1R_
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %r14
	movq	$0, (%rax)
	testq	%r14, %r14
	je	.LBB108_10
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.513(%rip), %rax
	movq	%rax, 64(%rsp)
	movq	$12, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB108_2
.LBB108_3:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.513(%rip), %rdx
	leaq	40(%rsp), %rcx
	movl	$12, %r8d
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rdi
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rdi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	movq	%rax, %rsi
	testq	%rax, %rax
	je	.LBB108_5
	movl	$-1, %ebp
	xorl	%ebx, %ebx
	cmpq	$0, 40(%rsp)
	je	.LBB108_8
.LBB108_7:
	movq	%rdi, %rcx
	callq	mi_free
.LBB108_8:
	cmpl	$-1, %ebp
	jne	.LBB108_11
	movq	%rsi, (%r14)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB108_5:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %ebx
	xorl	%ebp, %ebp
	cmpl	$1, %eax
	adcl	$10, %ebp
	cmpq	$0, 40(%rsp)
	jne	.LBB108_7
	jmp	.LBB108_8
.LBB108_10:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB108_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	jmp	.LBB108_3
.LBB108_11:
	movl	%ebp, 40(%rsp)
	movl	%ebx, 44(%rsp)
	movq	%rsi, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.Lfunc_end108:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stONtB1N_8CUmod_stPaENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_19cuModuleGetFunction0E0zE0E0B1R_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stONtB1N_8CUmod_stPaENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_19cuModuleGetFunction0E0zE0E0B1R_.llvm.1750587498003715262,unique,109
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stONtB1N_8CUmod_stPaENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_19cuModuleGetFunction0E0zE0E0B1R_.llvm.1750587498003715262
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stONtB1N_8CUmod_stPaENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_19cuModuleGetFunction0E0zE0E0B1R_.llvm.1750587498003715262:
.Lfunc_begin109:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stONtB1N_8CUmod_stPaENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_19cuModuleGetFunction0E0zE0E0B1R_.llvm.1750587498003715262
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %r14
	movq	$0, (%rax)
	testq	%r14, %r14
	je	.LBB109_20
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.693(%rip), %rsi
	movq	%rsi, 64(%rsp)
	movq	$19, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB109_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.693+7(%rip), %rax
	andq	$-8, %rax
	subq	%rsi, %rax
	jne	.LBB109_5
.LBB109_4:
	xorl	%eax, %eax
	jmp	.LBB109_6
.LBB109_20:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB109_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.693+7(%rip), %rax
	andq	$-8, %rax
	subq	%rsi, %rax
	je	.LBB109_4
.LBB109_5:
	cmpq	$2, %rax
	ja	.LBB109_9
.LBB109_6:
	movq	(%rax,%rsi), %rcx
	movq	8(%rax,%rsi), %rdx
	movabsq	$72340172838076672, %r8
	movq	%r8, %r9
	subq	%rcx, %r9
	orq	%rcx, %r9
	subq	%rdx, %r8
	orq	%rdx, %r8
	andq	%r9, %r8
	notq	%r8
	movabsq	$-9187201950435737472, %rcx
	testq	%rcx, %r8
	jne	.LBB109_9
	cmpq	$2, %rax
	je	.LBB109_13
	orq	$16, %rax
	.p2align	4
.LBB109_9:
	cmpb	$0, (%rax,%rsi)
	je	.LBB109_10
	incq	%rax
	cmpq	$18, %rax
	jne	.LBB109_9
.LBB109_13:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.693(%rip), %rdx
	leaq	40(%rsp), %rcx
	movl	$19, %r8d
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rbx
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rbx, %rdx
	callq	*__imp_GetProcAddress(%rip)
	movq	%rax, %rsi
	testq	%rax, %rax
	je	.LBB109_15
	movl	$-1, %ebp
	xorl	%edi, %edi
	cmpq	$0, 40(%rsp)
	je	.LBB109_18
.LBB109_17:
	movq	%rbx, %rcx
	callq	mi_free
.LBB109_18:
	cmpl	$-1, %ebp
	jne	.LBB109_11
	movq	%rsi, (%r14)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB109_15:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	xorl	%ebp, %ebp
	cmpl	$1, %eax
	adcl	$10, %ebp
	cmpq	$0, 40(%rsp)
	jne	.LBB109_17
	jmp	.LBB109_18
.LBB109_10:
	xorl	%edi, %edi
	movl	$15, %ebp
.LBB109_11:
	movl	%ebp, 40(%rsp)
	movl	%edi, 44(%rsp)
	movq	%rsi, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.Lfunc_end109:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOlNtNtNtCs5UjBoGikVie_6cudarc6driver3sys23CUdevice_attribute_enumlENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_20cuDeviceGetAttribute0E0zE0E0B1R_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOlNtNtNtCs5UjBoGikVie_6cudarc6driver3sys23CUdevice_attribute_enumlENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_20cuDeviceGetAttribute0E0zE0E0B1R_.llvm.1750587498003715262,unique,110
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOlNtNtNtCs5UjBoGikVie_6cudarc6driver3sys23CUdevice_attribute_enumlENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_20cuDeviceGetAttribute0E0zE0E0B1R_.llvm.1750587498003715262
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOlNtNtNtCs5UjBoGikVie_6cudarc6driver3sys23CUdevice_attribute_enumlENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_20cuDeviceGetAttribute0E0zE0E0B1R_.llvm.1750587498003715262:
.Lfunc_begin110:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOlNtNtNtCs5UjBoGikVie_6cudarc6driver3sys23CUdevice_attribute_enumlENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_20cuDeviceGetAttribute0E0zE0E0B1R_.llvm.1750587498003715262
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %r14
	movq	$0, (%rax)
	testq	%r14, %r14
	je	.LBB110_20
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.703(%rip), %rsi
	movq	%rsi, 64(%rsp)
	movq	$20, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB110_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.703+7(%rip), %rax
	andq	$-8, %rax
	subq	%rsi, %rax
	jne	.LBB110_5
.LBB110_4:
	xorl	%eax, %eax
	jmp	.LBB110_6
.LBB110_20:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB110_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.703+7(%rip), %rax
	andq	$-8, %rax
	subq	%rsi, %rax
	je	.LBB110_4
.LBB110_5:
	cmpq	$3, %rax
	ja	.LBB110_9
.LBB110_6:
	movq	(%rax,%rsi), %rcx
	movq	8(%rax,%rsi), %rdx
	movabsq	$72340172838076672, %r8
	movq	%r8, %r9
	subq	%rcx, %r9
	orq	%rcx, %r9
	subq	%rdx, %r8
	orq	%rdx, %r8
	andq	%r9, %r8
	notq	%r8
	movabsq	$-9187201950435737472, %rcx
	testq	%rcx, %r8
	jne	.LBB110_9
	cmpq	$3, %rax
	je	.LBB110_13
	orq	$16, %rax
	.p2align	4
.LBB110_9:
	cmpb	$0, (%rax,%rsi)
	je	.LBB110_10
	incq	%rax
	cmpq	$19, %rax
	jne	.LBB110_9
.LBB110_13:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.703(%rip), %rdx
	leaq	40(%rsp), %rcx
	movl	$20, %r8d
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rbx
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rbx, %rdx
	callq	*__imp_GetProcAddress(%rip)
	movq	%rax, %rsi
	testq	%rax, %rax
	je	.LBB110_15
	movl	$-1, %ebp
	xorl	%edi, %edi
	cmpq	$0, 40(%rsp)
	je	.LBB110_18
.LBB110_17:
	movq	%rbx, %rcx
	callq	mi_free
.LBB110_18:
	cmpl	$-1, %ebp
	jne	.LBB110_11
	movq	%rsi, (%r14)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB110_15:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	xorl	%ebp, %ebp
	cmpl	$1, %eax
	adcl	$10, %ebp
	cmpq	$0, 40(%rsp)
	jne	.LBB110_17
	jmp	.LBB110_18
.LBB110_10:
	xorl	%edi, %edi
	movl	$15, %ebp
.LBB110_11:
	movl	%ebp, 40(%rsp)
	movl	%edi, 44(%rsp)
	movq	%rsi, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.Lfunc_end110:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOllENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_11cuDeviceGet0E0zE0E0B1T_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOllENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_11cuDeviceGet0E0zE0E0B1T_,unique,111
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOllENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_11cuDeviceGet0E0zE0E0B1T_:
.Lfunc_begin111:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOllENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_11cuDeviceGet0E0zE0E0B1T_
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %r14
	movq	$0, (%rax)
	testq	%r14, %r14
	je	.LBB111_10
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.501(%rip), %rax
	movq	%rax, 64(%rsp)
	movq	$11, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB111_2
.LBB111_3:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.501(%rip), %rdx
	leaq	40(%rsp), %rcx
	movl	$11, %r8d
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rdi
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rdi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	movq	%rax, %rsi
	testq	%rax, %rax
	je	.LBB111_5
	movl	$-1, %ebp
	xorl	%ebx, %ebx
	cmpq	$0, 40(%rsp)
	je	.LBB111_8
.LBB111_7:
	movq	%rdi, %rcx
	callq	mi_free
.LBB111_8:
	cmpl	$-1, %ebp
	jne	.LBB111_11
	movq	%rsi, (%r14)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB111_5:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %ebx
	xorl	%ebp, %ebp
	cmpl	$1, %eax
	adcl	$10, %ebp
	cmpq	$0, 40(%rsp)
	jne	.LBB111_7
	jmp	.LBB111_8
.LBB111_10:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB111_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	jmp	.LBB111_3
.LBB111_11:
	movl	%ebp, 40(%rsp)
	movl	%ebx, 44(%rsp)
	movq	%rsi, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.Lfunc_end111:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOyjENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_13cuMemAlloc_v20E0zE0E0B1T_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOyjENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_13cuMemAlloc_v20E0zE0E0B1T_.llvm.1750587498003715262,unique,112
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOyjENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_13cuMemAlloc_v20E0zE0E0B1T_.llvm.1750587498003715262
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOyjENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_13cuMemAlloc_v20E0zE0E0B1T_.llvm.1750587498003715262:
.Lfunc_begin112:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOyjENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_13cuMemAlloc_v20E0zE0E0B1T_.llvm.1750587498003715262
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %r14
	movq	$0, (%rax)
	testq	%r14, %r14
	je	.LBB112_10
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.525(%rip), %rax
	movq	%rax, 64(%rsp)
	movq	$13, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB112_2
.LBB112_3:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.525(%rip), %rdx
	leaq	40(%rsp), %rcx
	movl	$13, %r8d
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rdi
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rdi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	movq	%rax, %rsi
	testq	%rax, %rax
	je	.LBB112_5
	movl	$-1, %ebp
	xorl	%ebx, %ebx
	cmpq	$0, 40(%rsp)
	je	.LBB112_8
.LBB112_7:
	movq	%rdi, %rcx
	callq	mi_free
.LBB112_8:
	cmpl	$-1, %ebp
	jne	.LBB112_11
	movq	%rsi, (%r14)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB112_5:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %ebx
	xorl	%ebp, %ebp
	cmpl	$1, %eax
	adcl	$10, %ebp
	cmpq	$0, 40(%rsp)
	jne	.LBB112_7
	jmp	.LBB112_8
.LBB112_10:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB112_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	jmp	.LBB112_3
.LBB112_11:
	movl	%ebp, 40(%rsp)
	movl	%ebx, 44(%rsp)
	movq	%rsi, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.Lfunc_end112:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1P_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_15cuMemAllocAsync0E0zE0E0B1T_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1P_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_15cuMemAllocAsync0E0zE0E0B1T_.llvm.1750587498003715262,unique,113
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1P_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_15cuMemAllocAsync0E0zE0E0B1T_.llvm.1750587498003715262
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1P_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_15cuMemAllocAsync0E0zE0E0B1T_.llvm.1750587498003715262:
.Lfunc_begin113:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1P_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_15cuMemAllocAsync0E0zE0E0B1T_.llvm.1750587498003715262
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %r14
	movq	$0, (%rax)
	testq	%r14, %r14
	je	.LBB113_10
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.572(%rip), %rax
	movq	%rax, 64(%rsp)
	movq	$15, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB113_2
.LBB113_3:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.572(%rip), %rdx
	leaq	40(%rsp), %rcx
	movl	$15, %r8d
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rdi
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rdi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	movq	%rax, %rsi
	testq	%rax, %rax
	je	.LBB113_5
	movl	$-1, %ebp
	xorl	%ebx, %ebx
	cmpq	$0, 40(%rsp)
	je	.LBB113_8
.LBB113_7:
	movq	%rdi, %rcx
	callq	mi_free
.LBB113_8:
	cmpl	$-1, %ebp
	jne	.LBB113_11
	movq	%rsi, (%r14)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB113_5:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %ebx
	xorl	%ebp, %ebp
	cmpl	$1, %eax
	adcl	$10, %ebp
	cmpq	$0, 40(%rsp)
	jne	.LBB113_7
	jmp	.LBB113_8
.LBB113_10:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB113_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	jmp	.LBB113_3
.LBB113_11:
	movl	%ebp, 40(%rsp)
	movl	%ebx, 44(%rsp)
	movq	%rsi, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.Lfunc_end113:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKClENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_28cuDevicePrimaryCtxRelease_v20E0zE0E0B1R_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKClENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_28cuDevicePrimaryCtxRelease_v20E0zE0E0B1R_,unique,114
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKClENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_28cuDevicePrimaryCtxRelease_v20E0zE0E0B1R_:
.Lfunc_begin114:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKClENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_28cuDevicePrimaryCtxRelease_v20E0zE0E0B1R_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB114_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.856(%rip), %rcx
	movl	$28, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKClENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB114_2:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end114:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_6cuInit0E0zE0E0B1R_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_6cuInit0E0zE0E0B1R_,unique,115
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_6cuInit0E0zE0E0B1R_:
.Lfunc_begin115:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_6cuInit0E0zE0E0B1R_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB115_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.931(%rip), %rcx
	movl	$6, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCmENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB115_2:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end115:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_12cuMemFree_v20E0zE0E0B1R_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_12cuMemFree_v20E0zE0E0B1R_.llvm.1750587498003715262,unique,116
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_12cuMemFree_v20E0zE0E0B1R_.llvm.1750587498003715262
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_12cuMemFree_v20E0zE0E0B1R_.llvm.1750587498003715262:
.Lfunc_begin116:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_12cuMemFree_v20E0zE0E0B1R_.llvm.1750587498003715262
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB116_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.510(%rip), %rcx
	movl	$12, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCyENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB116_2:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end116:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_14cuMemFreeAsync0E0zE0E0B1R_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_14cuMemFreeAsync0E0zE0E0B1R_.llvm.1750587498003715262,unique,117
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_14cuMemFreeAsync0E0zE0E0B1R_.llvm.1750587498003715262
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_14cuMemFreeAsync0E0zE0E0B1R_.llvm.1750587498003715262:
.Lfunc_begin117:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_14cuMemFreeAsync0E0zE0E0B1R_.llvm.1750587498003715262
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %r14
	movq	$0, (%rax)
	testq	%r14, %r14
	je	.LBB117_10
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.546(%rip), %rax
	movq	%rax, 64(%rsp)
	movq	$14, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB117_2
.LBB117_3:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.546(%rip), %rdx
	leaq	40(%rsp), %rcx
	movl	$14, %r8d
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rdi
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rdi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	movq	%rax, %rsi
	testq	%rax, %rax
	je	.LBB117_5
	movl	$-1, %ebp
	xorl	%ebx, %ebx
	cmpq	$0, 40(%rsp)
	je	.LBB117_8
.LBB117_7:
	movq	%rdi, %rcx
	callq	mi_free
.LBB117_8:
	cmpl	$-1, %ebp
	jne	.LBB117_11
	movq	%rsi, (%r14)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB117_5:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %ebx
	xorl	%ebp, %ebp
	cmpl	$1, %eax
	adcl	$10, %ebp
	cmpq	$0, 40(%rsp)
	jne	.LBB117_7
	jmp	.LBB117_8
.LBB117_10:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB117_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	jmp	.LBB117_3
.LBB117_11:
	movl	%ebp, 40(%rsp)
	movl	%ebx, 44(%rsp)
	movq	%rsi, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.Lfunc_end117:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_styB1K_jONtB1N_11CUstream_stENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_17cuMemcpyPeerAsync0E0zE0E0B1R_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_styB1K_jONtB1N_11CUstream_stENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_17cuMemcpyPeerAsync0E0zE0E0B1R_.llvm.1750587498003715262,unique,118
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_styB1K_jONtB1N_11CUstream_stENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_17cuMemcpyPeerAsync0E0zE0E0B1R_.llvm.1750587498003715262
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_styB1K_jONtB1N_11CUstream_stENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_17cuMemcpyPeerAsync0E0zE0E0B1R_.llvm.1750587498003715262:
.Lfunc_begin118:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_styB1K_jONtB1N_11CUstream_stENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_17cuMemcpyPeerAsync0E0zE0E0B1R_.llvm.1750587498003715262
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %r14
	movq	$0, (%rax)
	testq	%r14, %r14
	je	.LBB118_15
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.622(%rip), %rsi
	movq	%rsi, 64(%rsp)
	movq	$17, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB118_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.622+7(%rip), %rax
	andq	$-8, %rax
	subq	%rsi, %rax
	je	.LBB118_8
	.p2align	4
.LBB118_4:
	cmpb	$0, (%rax,%rsi)
	je	.LBB118_5
	incq	%rax
	cmpq	$16, %rax
	jne	.LBB118_4
.LBB118_8:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.622(%rip), %rdx
	leaq	40(%rsp), %rcx
	movl	$17, %r8d
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rbx
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rbx, %rdx
	callq	*__imp_GetProcAddress(%rip)
	movq	%rax, %rsi
	testq	%rax, %rax
	je	.LBB118_10
	movl	$-1, %ebp
	xorl	%edi, %edi
	cmpq	$0, 40(%rsp)
	je	.LBB118_13
.LBB118_12:
	movq	%rbx, %rcx
	callq	mi_free
.LBB118_13:
	cmpl	$-1, %ebp
	jne	.LBB118_6
	movq	%rsi, (%r14)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB118_10:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	xorl	%ebp, %ebp
	cmpl	$1, %eax
	adcl	$10, %ebp
	cmpq	$0, 40(%rsp)
	jne	.LBB118_12
	jmp	.LBB118_13
.LBB118_15:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB118_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.622+7(%rip), %rax
	andq	$-8, %rax
	subq	%rsi, %rax
	jne	.LBB118_4
	jmp	.LBB118_8
.LBB118_5:
	xorl	%edi, %edi
	movl	$15, %ebp
.LBB118_6:
	movl	%ebp, 40(%rsp)
	movl	%edi, 44(%rsp)
	movq	%rsi, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.Lfunc_end118:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB2n_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB2n_20cuMemcpyHtoDAsync_v20E0zE0E0B2r_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB2n_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB2n_20cuMemcpyHtoDAsync_v20E0zE0E0B2r_.llvm.1750587498003715262,unique,119
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB2n_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB2n_20cuMemcpyHtoDAsync_v20E0zE0E0B2r_.llvm.1750587498003715262
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB2n_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB2n_20cuMemcpyHtoDAsync_v20E0zE0E0B2r_.llvm.1750587498003715262:
.Lfunc_begin119:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB2n_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB2n_20cuMemcpyHtoDAsync_v20E0zE0E0B2r_.llvm.1750587498003715262
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %r14
	movq	$0, (%rax)
	testq	%r14, %r14
	je	.LBB119_20
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.720(%rip), %rsi
	movq	%rsi, 64(%rsp)
	movq	$20, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB119_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.720+7(%rip), %rax
	andq	$-8, %rax
	subq	%rsi, %rax
	jne	.LBB119_5
.LBB119_4:
	xorl	%eax, %eax
	jmp	.LBB119_6
.LBB119_20:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB119_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.720+7(%rip), %rax
	andq	$-8, %rax
	subq	%rsi, %rax
	je	.LBB119_4
.LBB119_5:
	cmpq	$3, %rax
	ja	.LBB119_9
.LBB119_6:
	movq	(%rax,%rsi), %rcx
	movq	8(%rax,%rsi), %rdx
	movabsq	$72340172838076672, %r8
	movq	%r8, %r9
	subq	%rcx, %r9
	orq	%rcx, %r9
	subq	%rdx, %r8
	orq	%rdx, %r8
	andq	%r9, %r8
	notq	%r8
	movabsq	$-9187201950435737472, %rcx
	testq	%rcx, %r8
	jne	.LBB119_9
	cmpq	$3, %rax
	je	.LBB119_13
	orq	$16, %rax
	.p2align	4
.LBB119_9:
	cmpb	$0, (%rax,%rsi)
	je	.LBB119_10
	incq	%rax
	cmpq	$19, %rax
	jne	.LBB119_9
.LBB119_13:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.720(%rip), %rdx
	leaq	40(%rsp), %rcx
	movl	$20, %r8d
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rbx
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rbx, %rdx
	callq	*__imp_GetProcAddress(%rip)
	movq	%rax, %rsi
	testq	%rax, %rax
	je	.LBB119_15
	movl	$-1, %ebp
	xorl	%edi, %edi
	cmpq	$0, 40(%rsp)
	je	.LBB119_18
.LBB119_17:
	movq	%rbx, %rcx
	callq	mi_free
.LBB119_18:
	cmpl	$-1, %ebp
	jne	.LBB119_11
	movq	%rsi, (%r14)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB119_15:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %edi
	xorl	%ebp, %ebp
	cmpl	$1, %eax
	adcl	$10, %ebp
	cmpq	$0, 40(%rsp)
	jne	.LBB119_17
	jmp	.LBB119_18
.LBB119_10:
	xorl	%edi, %edi
	movl	$15, %ebp
.LBB119_11:
	movl	%ebp, 40(%rsp)
	movl	%edi, 44(%rsp)
	movq	%rsi, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.Lfunc_end119:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyhjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1P_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_15cuMemsetD8Async0E0zE0E0B1T_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyhjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1P_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_15cuMemsetD8Async0E0zE0E0B1T_.llvm.1750587498003715262,unique,120
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyhjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1P_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_15cuMemsetD8Async0E0zE0E0B1T_.llvm.1750587498003715262
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyhjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1P_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_15cuMemsetD8Async0E0zE0E0B1T_.llvm.1750587498003715262:
.Lfunc_begin120:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyhjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1P_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_15cuMemsetD8Async0E0zE0E0B1T_.llvm.1750587498003715262
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$80, %rsp
	.seh_stackalloc 80
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %r14
	movq	$0, (%rax)
	testq	%r14, %r14
	je	.LBB120_10
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.585(%rip), %rax
	movq	%rax, 64(%rsp)
	movq	$15, 72(%rsp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB120_2
.LBB120_3:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.585(%rip), %rdx
	leaq	40(%rsp), %rcx
	movl	$15, %r8d
	callq	_RINvNtCskIq6Fm6qntW_10libloading4util13copy_and_pushhECs5UjBoGikVie_6cudarc
	movq	48(%rsp), %rdi
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB(%rip), %rcx
	movq	%rdi, %rdx
	callq	*__imp_GetProcAddress(%rip)
	movq	%rax, %rsi
	testq	%rax, %rax
	je	.LBB120_5
	movl	$-1, %ebp
	xorl	%ebx, %ebx
	cmpq	$0, 40(%rsp)
	je	.LBB120_8
.LBB120_7:
	movq	%rdi, %rcx
	callq	mi_free
.LBB120_8:
	cmpl	$-1, %ebp
	jne	.LBB120_11
	movq	%rsi, (%r14)
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB120_5:
	callq	*__imp_GetLastError(%rip)
	movl	%eax, %ebx
	xorl	%ebp, %ebp
	cmpl	$1, %eax
	adcl	$10, %ebp
	cmpq	$0, 40(%rsp)
	jne	.LBB120_7
	jmp	.LBB120_8
.LBB120_10:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB120_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB2_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zEB2f_
	jmp	.LBB120_3
.LBB120_11:
	movl	%ebp, 40(%rsp)
	movl	%ebx, 44(%rsp)
	movq	%rsi, 48(%rsp)
	leaq	64(%rsp), %rcx
	leaq	40(%rsp), %rdx
	callq	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	ud2
.Lfunc_end120:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1P_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_20cuMemcpyDtoDAsync_v20E0zE0E0B1T_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1P_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_20cuMemcpyDtoDAsync_v20E0zE0E0B1T_.llvm.1750587498003715262,unique,121
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1P_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_20cuMemcpyDtoDAsync_v20E0zE0E0B1T_.llvm.1750587498003715262
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1P_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_20cuMemcpyDtoDAsync_v20E0zE0E0B1T_.llvm.1750587498003715262:
.Lfunc_begin121:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1P_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_20cuMemcpyDtoDAsync_v20E0zE0E0B1T_.llvm.1750587498003715262
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB121_2
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.717(%rip), %rcx
	movl	$20, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCyyjONtB2_11CUstream_stENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB121_2:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end121:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_,unique,122
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_:
.Lfunc_begin122:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_
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
	subq	$296, %rsp
	.seh_stackalloc 296
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	movq	$-2, 160(%rbp)
	movq	(%rcx), %rax
	movq	(%rax), %r13
	movq	$0, (%rax)
	testq	%r13, %r13
	je	.LBB122_61
	movl	$16, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB122_62
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.495(%rip), %rcx
	movq	%rcx, (%rax)
	movq	$5, 8(%rax)
	movq	%rax, %rcx
	addq	$16, %rcx
	movq	$0, -88(%rbp)
	movq	$0, -56(%rbp)
	movq	%rax, 104(%rbp)
	movq	%rax, -24(%rbp)
	movq	%rcx, -16(%rbp)
	movb	$1, 159(%rbp)
.Ltmp28:
	movq	%rbp, %rcx
	leaq	-88(%rbp), %rdx
	callq	_RNvXs9_NtNtNtCs8xEFJqa6dYS_4core4iter8adapters7flattenINtB5_7FlattenINtNtB7_3map3MapINtNtNtBb_5slice4iter4IterReENCNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib00EENtNtNtB9_6traits8iterator8Iterator4nextB1X_
	nop
.Ltmp29:
	movq	(%rbp), %r12
	cmpq	$-1, %r12
	je	.LBB122_42
	movq	%r13, -8(%rbp)
	cmpq	$0, -88(%rbp)
	movabsq	$-6148914691236517205, %r13
	je	.LBB122_5
	movq	-64(%rbp), %rax
	subq	-80(%rbp), %rax
	shrq	$3, %rax
	imulq	%r13, %rax
	cmpq	$0, -56(%rbp)
	je	.LBB122_8
.LBB122_9:
	movq	-32(%rbp), %rcx
	subq	-48(%rbp), %rcx
	shrq	$3, %rcx
	imulq	%r13, %rcx
	jmp	.LBB122_10
.LBB122_42:
	movq	$0, 112(%rbp)
	movq	$8, 120(%rbp)
	movq	$0, 128(%rbp)
	leaq	-88(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtNtB4_4iter8adapters7flatten7FlattenINtNtBG_3map3MapINtNtNtB4_5slice4iter4IterReENCNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib00EEEB2a_
	movl	$8, %esi
	xorl	%edi, %edi
	jmp	.LBB122_43
.LBB122_5:
	xorl	%eax, %eax
	cmpq	$0, -56(%rbp)
	jne	.LBB122_9
.LBB122_8:
	xorl	%ecx, %ecx
.LBB122_10:
	addq	%rax, %rcx
	movq	8(%rbp), %rdx
	cmpq	$4, %rcx
	movl	$3, %ebx
	cmovaeq	%rcx, %rbx
	leaq	8(,%rbx,8), %rax
	leaq	(%rax,%rax,2), %rsi
	movabsq	$384307168202282324, %rax
	cmpq	%rax, %rcx
	jbe	.LBB122_17
	movq	%rdx, 144(%rbp)
	xorl	%edi, %edi
.LBB122_12:
.Ltmp34:
	movq	%r12, 136(%rbp)
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp35:
	jmp	.LBB122_13
.LBB122_17:
	movq	16(%rbp), %r14
	testq	%rsi, %rsi
	je	.LBB122_18
	movq	%rdx, 144(%rbp)
	movl	$8, %edi
	movl	$8, %edx
	movq	%rsi, %rcx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB122_12
	movq	%rax, %r15
	incq	%rbx
	movq	144(%rbp), %rdx
	jmp	.LBB122_21
.LBB122_18:
	movl	$8, %r15d
	xorl	%ebx, %ebx
.LBB122_21:
	movq	%r12, (%r15)
	movq	%rdx, 8(%r15)
	movq	%r14, 16(%r15)
	movq	%rbx, 80(%rbp)
	movq	%r15, 88(%rbp)
	movq	$1, 96(%rbp)
	movups	-24(%rbp), %xmm0
	movaps	%xmm0, 64(%rbp)
	movups	-88(%rbp), %xmm0
	movups	-72(%rbp), %xmm1
	movups	-56(%rbp), %xmm2
	movups	-40(%rbp), %xmm3
	movaps	%xmm3, 48(%rbp)
	movaps	%xmm2, 32(%rbp)
	movaps	%xmm1, 16(%rbp)
	movaps	%xmm0, (%rbp)
	movl	$1, %esi
	leaq	112(%rbp), %rdi
	movq	%rbp, %rbx
	leaq	80(%rbp), %r14
	jmp	.LBB122_22
	.p2align	4
.LBB122_33:
	movq	56(%rbp), %r8
	subq	40(%rbp), %r8
	shrq	$3, %r8
	imulq	%r13, %r8
.LBB122_34:
	addq	%rax, %r8
.Ltmp32:
	movq	$24, 32(%rsp)
	movl	$8, %r9d
	movq	%r14, %rcx
	movq	%rsi, %rdx
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECs5UjBoGikVie_6cudarc
	nop
.Ltmp33:
	movq	88(%rbp), %r15
	movq	136(%rbp), %rcx
	movq	144(%rbp), %rdx
.LBB122_36:
	leaq	(%rsi,%rsi,2), %rax
	movq	%rdx, (%r15,%rax,8)
	movq	%rcx, 8(%r15,%rax,8)
	movq	%r12, 16(%r15,%rax,8)
	incq	%rsi
	movq	%rsi, 96(%rbp)
.LBB122_22:
.Ltmp30:
	movq	%rdi, %rcx
	movq	%rbx, %rdx
	callq	_RNvXs9_NtNtNtCs8xEFJqa6dYS_4core4iter8adapters7flattenINtB5_7FlattenINtNtB7_3map3MapINtNtNtBb_5slice4iter4IterReENCNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib00EENtNtNtB9_6traits8iterator8Iterator4nextB1X_
	nop
.Ltmp31:
	movq	112(%rbp), %rdx
	cmpq	$-1, %rdx
	je	.LBB122_37
	movq	120(%rbp), %rcx
	movq	128(%rbp), %r12
	cmpq	80(%rbp), %rsi
	jne	.LBB122_36
	cmpq	$0, (%rbp)
	je	.LBB122_26
	movq	24(%rbp), %rax
	subq	8(%rbp), %rax
	shrq	$3, %rax
	imulq	%r13, %rax
	incq	%rax
	cmpq	$0, 32(%rbp)
	movq	%rcx, 136(%rbp)
	movq	%rdx, 144(%rbp)
	jne	.LBB122_33
	jmp	.LBB122_29
.LBB122_26:
	movl	$1, %eax
	cmpq	$0, 32(%rbp)
	movq	%rcx, 136(%rbp)
	movq	%rdx, 144(%rbp)
	jne	.LBB122_33
.LBB122_29:
	xorl	%r8d, %r8d
	jmp	.LBB122_34
.LBB122_37:
	movq	%rbp, %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtNtB4_4iter8adapters7flatten7FlattenINtNtBG_3map3MapINtNtNtB4_5slice4iter4IterReENCNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib00EEEB2a_
	movq	96(%rbp), %rdi
	movq	%rdi, 128(%rbp)
	movups	80(%rbp), %xmm0
	movaps	%xmm0, 112(%rbp)
	movq	120(%rbp), %rsi
	movq	-8(%rbp), %r13
.LBB122_43:
	leaq	(%rdi,%rdi,2), %rax
	leaq	(%rsi,%rax,8), %r15
	movq	%rbp, %r14
	movq	%rsi, %r12
	.p2align	4
.LBB122_44:
	cmpq	%r15, %r12
	je	.LBB122_60
	movq	8(%r12), %rdx
	movq	16(%r12), %r8
.Ltmp36:
	movq	%r14, %rcx
	callq	_RINvXs_NtCskIq6Fm6qntW_10libloading11as_filenameReNtB5_6Sealed16windows_filenameNtNtNtB7_2os7windows7LibraryNCINvMs0_B1i_B1g_15load_with_flagsRNtNtCsfQUUnEvlYZE_5alloc6string6StringE0ECs5UjBoGikVie_6cudarc
	nop
.Ltmp37:
	movl	(%rbp), %ecx
	movq	8(%rbp), %rbx
	cmpl	$-1, %ecx
	je	.LBB122_47
	addq	$24, %r12
	movq	16(%rbp), %rax
	cmpl	$4, %ecx
	je	.LBB122_58
	cmpl	$2, %ecx
	je	.LBB122_58
	testl	%ecx, %ecx
	jne	.LBB122_44
.LBB122_58:
	movb	$0, (%rbx)
	testq	%rax, %rax
	je	.LBB122_44
	movq	%rbx, %rcx
	callq	mi_free
	jmp	.LBB122_44
.LBB122_47:
	testq	%rdi, %rdi
	je	.LBB122_52
	leaq	8(%rsi), %r14
	jmp	.LBB122_49
	.p2align	4
.LBB122_51:
	addq	$24, %r14
	decq	%rdi
	je	.LBB122_52
.LBB122_49:
	cmpq	$0, -8(%r14)
	je	.LBB122_51
	movq	(%r14), %rcx
	callq	mi_free
	jmp	.LBB122_51
.LBB122_52:
	cmpq	$0, 112(%rbp)
	je	.LBB122_54
	movq	%rsi, %rcx
	callq	mi_free
.LBB122_54:
	movq	104(%rbp), %rcx
	callq	mi_free
	movq	%rbx, (%r13)
	.seh_startepilogue
	addq	$296, %rsp
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
.LBB122_61:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB122_62:
	movl	$8, %ecx
	movl	$16, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	ud2
.LBB122_60:
	movq	104(%rbp), %rax
	movq	(%rax), %rcx
	movq	8(%rax), %rdx
.Ltmp38:
	movq	%rsi, %r8
	movq	%rdi, %r9
	callq	_RINvCs5UjBoGikVie_6cudarc18panic_no_lib_foundNtNtCsfQUUnEvlYZE_5alloc6string6StringEB2_
	nop
.Ltmp39:
.LBB122_13:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_@IMGREL
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_,unique,122
	.seh_endproc
	.def	"?dtor$14@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$14@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_@4HA":
.seh_proc "?dtor$14@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_@4HA"
.LBB122_14:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 136(%rbp)
	je	.LBB122_16
	movq	144(%rbp), %rcx
	callq	mi_free
.LBB122_16:
	movb	$1, 159(%rbp)
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_,unique,122
	.seh_endproc
	.def	"?dtor$30@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$30@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_@4HA":
.seh_proc "?dtor$30@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_@4HA"
.LBB122_30:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 144(%rbp)
	je	.LBB122_32
	movq	136(%rbp), %rcx
	callq	mi_free
	nop
.LBB122_32:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_,unique,122
	.seh_endproc
	.def	"?dtor$38@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$38@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_@4HA":
.seh_proc "?dtor$38@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_@4HA"
.LBB122_38:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpb	$0, 159(%rbp)
	je	.LBB122_39
	leaq	-88(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtNtB4_4iter8adapters7flatten7FlattenINtNtBG_3map3MapINtNtNtB4_5slice4iter4IterReENCNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib00EEEB2a_
	nop
.LBB122_39:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_,unique,122
	.seh_endproc
	.def	"?dtor$41@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$41@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_@4HA":
.seh_proc "?dtor$41@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_@4HA"
.LBB122_41:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movq	104(%rbp), %rcx
	callq	mi_free
	nop
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_,unique,122
	.seh_endproc
	.def	"?dtor$63@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$63@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_@4HA":
.seh_proc "?dtor$63@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_@4HA"
.LBB122_63:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movq	%rbp, %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtNtB4_4iter8adapters7flatten7FlattenINtNtBG_3map3MapINtNtNtB4_5slice4iter4IterReENCNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib00EEEB2a_
	leaq	80(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecNtNtBG_6string6StringEECs5UjBoGikVie_6cudarc
	movb	$0, 159(%rbp)
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_,unique,122
	.seh_endproc
	.def	"?dtor$64@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$64@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_@4HA":
.seh_proc "?dtor$64@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_@4HA"
.LBB122_64:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	leaq	112(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecNtNtBG_6string6StringEECs5UjBoGikVie_6cudarc
	nop
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
.Lfunc_end122:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_,unique,122
	.seh_endproc
	.section	.xdata,"dr",associative,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_,unique,6
	.p2align	2, 0x0
$cppxdata$_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_:
	.long	429065506
	.long	6
	.long	$stateUnwindMap$_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_@IMGREL
	.long	0
	.long	0
	.long	9
	.long	$ip2state$_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_@IMGREL
	.long	288
	.long	0
	.long	1
$stateUnwindMap$_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_:
	.long	-1
	.long	"?dtor$41@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_@4HA"@IMGREL
	.long	0
	.long	"?dtor$64@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_@4HA"@IMGREL
	.long	0
	.long	"?dtor$38@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_@4HA"@IMGREL
	.long	2
	.long	"?dtor$63@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_@4HA"@IMGREL
	.long	3
	.long	"?dtor$30@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_@4HA"@IMGREL
	.long	2
	.long	"?dtor$14@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_@4HA"@IMGREL
$ip2state$_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_:
	.long	.Lfunc_begin122@IMGREL
	.long	-1
	.long	.Ltmp28@IMGREL
	.long	2
	.long	.Ltmp34@IMGREL
	.long	5
	.long	.Ltmp32@IMGREL
	.long	4
	.long	.Ltmp30@IMGREL
	.long	3
	.long	.Ltmp36@IMGREL
	.long	1
	.long	.Ltmp37@IMGREL
	.long	-1
	.long	.Ltmp38@IMGREL
	.long	1
	.long	.Ltmp39@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_,unique,122

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_,unique,123
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_:
.Lfunc_begin123:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_
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
	subq	$296, %rsp
	.seh_stackalloc 296
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	movq	$-2, 160(%rbp)
	movq	(%rcx), %rax
	movq	(%rax), %r13
	movq	$0, (%rax)
	testq	%r13, %r13
	je	.LBB123_61
	movl	$32, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB123_62
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.929(%rip), %rcx
	movq	%rcx, (%rax)
	movq	$4, 8(%rax)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.930(%rip), %rcx
	movq	%rcx, 16(%rax)
	movq	$6, 24(%rax)
	movq	%rax, %rcx
	addq	$32, %rcx
	movq	$0, -88(%rbp)
	movq	$0, -56(%rbp)
	movq	%rax, 104(%rbp)
	movq	%rax, -24(%rbp)
	movq	%rcx, -16(%rbp)
	movb	$1, 159(%rbp)
.Ltmp40:
	movq	%rbp, %rcx
	leaq	-88(%rbp), %rdx
	callq	_RNvXs9_NtNtNtCs8xEFJqa6dYS_4core4iter8adapters7flattenINtB5_7FlattenINtNtB7_3map3MapINtNtNtBb_5slice4iter4IterReENCNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib00EENtNtNtB9_6traits8iterator8Iterator4nextB1X_
	nop
.Ltmp41:
	movq	(%rbp), %r12
	cmpq	$-1, %r12
	je	.LBB123_42
	movq	%r13, -8(%rbp)
	cmpq	$0, -88(%rbp)
	movabsq	$-6148914691236517205, %r13
	je	.LBB123_5
	movq	-64(%rbp), %rax
	subq	-80(%rbp), %rax
	shrq	$3, %rax
	imulq	%r13, %rax
	cmpq	$0, -56(%rbp)
	je	.LBB123_8
.LBB123_9:
	movq	-32(%rbp), %rcx
	subq	-48(%rbp), %rcx
	shrq	$3, %rcx
	imulq	%r13, %rcx
	jmp	.LBB123_10
.LBB123_42:
	movq	$0, 112(%rbp)
	movq	$8, 120(%rbp)
	movq	$0, 128(%rbp)
	leaq	-88(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtNtB4_4iter8adapters7flatten7FlattenINtNtBG_3map3MapINtNtNtB4_5slice4iter4IterReENCNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib00EEEB2a_
	movl	$8, %esi
	xorl	%edi, %edi
	jmp	.LBB123_43
.LBB123_5:
	xorl	%eax, %eax
	cmpq	$0, -56(%rbp)
	jne	.LBB123_9
.LBB123_8:
	xorl	%ecx, %ecx
.LBB123_10:
	addq	%rax, %rcx
	movq	8(%rbp), %rdx
	cmpq	$4, %rcx
	movl	$3, %ebx
	cmovaeq	%rcx, %rbx
	leaq	8(,%rbx,8), %rax
	leaq	(%rax,%rax,2), %rsi
	movabsq	$384307168202282324, %rax
	cmpq	%rax, %rcx
	jbe	.LBB123_17
	movq	%rdx, 144(%rbp)
	xorl	%edi, %edi
.LBB123_12:
.Ltmp46:
	movq	%r12, 136(%rbp)
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp47:
	jmp	.LBB123_13
.LBB123_17:
	movq	16(%rbp), %r14
	testq	%rsi, %rsi
	je	.LBB123_18
	movq	%rdx, 144(%rbp)
	movl	$8, %edi
	movl	$8, %edx
	movq	%rsi, %rcx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB123_12
	movq	%rax, %r15
	incq	%rbx
	movq	144(%rbp), %rdx
	jmp	.LBB123_21
.LBB123_18:
	movl	$8, %r15d
	xorl	%ebx, %ebx
.LBB123_21:
	movq	%r12, (%r15)
	movq	%rdx, 8(%r15)
	movq	%r14, 16(%r15)
	movq	%rbx, 80(%rbp)
	movq	%r15, 88(%rbp)
	movq	$1, 96(%rbp)
	movups	-24(%rbp), %xmm0
	movaps	%xmm0, 64(%rbp)
	movups	-88(%rbp), %xmm0
	movups	-72(%rbp), %xmm1
	movups	-56(%rbp), %xmm2
	movups	-40(%rbp), %xmm3
	movaps	%xmm3, 48(%rbp)
	movaps	%xmm2, 32(%rbp)
	movaps	%xmm1, 16(%rbp)
	movaps	%xmm0, (%rbp)
	movl	$1, %esi
	leaq	112(%rbp), %rdi
	movq	%rbp, %rbx
	leaq	80(%rbp), %r14
	jmp	.LBB123_22
	.p2align	4
.LBB123_33:
	movq	56(%rbp), %r8
	subq	40(%rbp), %r8
	shrq	$3, %r8
	imulq	%r13, %r8
.LBB123_34:
	addq	%rax, %r8
.Ltmp44:
	movq	$24, 32(%rsp)
	movl	$8, %r9d
	movq	%r14, %rcx
	movq	%rsi, %rdx
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECs5UjBoGikVie_6cudarc
	nop
.Ltmp45:
	movq	88(%rbp), %r15
	movq	136(%rbp), %rcx
	movq	144(%rbp), %rdx
.LBB123_36:
	leaq	(%rsi,%rsi,2), %rax
	movq	%rdx, (%r15,%rax,8)
	movq	%rcx, 8(%r15,%rax,8)
	movq	%r12, 16(%r15,%rax,8)
	incq	%rsi
	movq	%rsi, 96(%rbp)
.LBB123_22:
.Ltmp42:
	movq	%rdi, %rcx
	movq	%rbx, %rdx
	callq	_RNvXs9_NtNtNtCs8xEFJqa6dYS_4core4iter8adapters7flattenINtB5_7FlattenINtNtB7_3map3MapINtNtNtBb_5slice4iter4IterReENCNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib00EENtNtNtB9_6traits8iterator8Iterator4nextB1X_
	nop
.Ltmp43:
	movq	112(%rbp), %rdx
	cmpq	$-1, %rdx
	je	.LBB123_37
	movq	120(%rbp), %rcx
	movq	128(%rbp), %r12
	cmpq	80(%rbp), %rsi
	jne	.LBB123_36
	cmpq	$0, (%rbp)
	je	.LBB123_26
	movq	24(%rbp), %rax
	subq	8(%rbp), %rax
	shrq	$3, %rax
	imulq	%r13, %rax
	incq	%rax
	cmpq	$0, 32(%rbp)
	movq	%rcx, 136(%rbp)
	movq	%rdx, 144(%rbp)
	jne	.LBB123_33
	jmp	.LBB123_29
.LBB123_26:
	movl	$1, %eax
	cmpq	$0, 32(%rbp)
	movq	%rcx, 136(%rbp)
	movq	%rdx, 144(%rbp)
	jne	.LBB123_33
.LBB123_29:
	xorl	%r8d, %r8d
	jmp	.LBB123_34
.LBB123_37:
	movq	%rbp, %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtNtB4_4iter8adapters7flatten7FlattenINtNtBG_3map3MapINtNtNtB4_5slice4iter4IterReENCNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib00EEEB2a_
	movq	96(%rbp), %rdi
	movq	%rdi, 128(%rbp)
	movups	80(%rbp), %xmm0
	movaps	%xmm0, 112(%rbp)
	movq	120(%rbp), %rsi
	movq	-8(%rbp), %r13
.LBB123_43:
	leaq	(%rdi,%rdi,2), %rax
	leaq	(%rsi,%rax,8), %r15
	movq	%rbp, %r14
	movq	%rsi, %r12
	.p2align	4
.LBB123_44:
	cmpq	%r15, %r12
	je	.LBB123_60
	movq	8(%r12), %rdx
	movq	16(%r12), %r8
.Ltmp48:
	movq	%r14, %rcx
	callq	_RINvXs_NtCskIq6Fm6qntW_10libloading11as_filenameReNtB5_6Sealed16windows_filenameNtNtNtB7_2os7windows7LibraryNCINvMs0_B1i_B1g_15load_with_flagsRNtNtCsfQUUnEvlYZE_5alloc6string6StringE0ECs5UjBoGikVie_6cudarc
	nop
.Ltmp49:
	movl	(%rbp), %ecx
	movq	8(%rbp), %rbx
	cmpl	$-1, %ecx
	je	.LBB123_47
	addq	$24, %r12
	movq	16(%rbp), %rax
	cmpl	$4, %ecx
	je	.LBB123_58
	cmpl	$2, %ecx
	je	.LBB123_58
	testl	%ecx, %ecx
	jne	.LBB123_44
.LBB123_58:
	movb	$0, (%rbx)
	testq	%rax, %rax
	je	.LBB123_44
	movq	%rbx, %rcx
	callq	mi_free
	jmp	.LBB123_44
.LBB123_47:
	testq	%rdi, %rdi
	je	.LBB123_52
	leaq	8(%rsi), %r14
	jmp	.LBB123_49
	.p2align	4
.LBB123_51:
	addq	$24, %r14
	decq	%rdi
	je	.LBB123_52
.LBB123_49:
	cmpq	$0, -8(%r14)
	je	.LBB123_51
	movq	(%r14), %rcx
	callq	mi_free
	jmp	.LBB123_51
.LBB123_52:
	cmpq	$0, 112(%rbp)
	je	.LBB123_54
	movq	%rsi, %rcx
	callq	mi_free
.LBB123_54:
	movq	104(%rbp), %rcx
	callq	mi_free
	movq	%rbx, (%r13)
	.seh_startepilogue
	addq	$296, %rsp
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
.LBB123_61:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.LBB123_62:
	movl	$8, %ecx
	movl	$32, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	ud2
.LBB123_60:
	movq	104(%rbp), %rax
	movq	(%rax), %rcx
	movq	8(%rax), %rdx
.Ltmp50:
	movq	%rsi, %r8
	movq	%rdi, %r9
	callq	_RINvCs5UjBoGikVie_6cudarc18panic_no_lib_foundNtNtCsfQUUnEvlYZE_5alloc6string6StringEB2_
	nop
.Ltmp51:
.LBB123_13:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_@IMGREL
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_,unique,123
	.seh_endproc
	.def	"?dtor$14@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$14@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_@4HA":
.seh_proc "?dtor$14@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_@4HA"
.LBB123_14:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 136(%rbp)
	je	.LBB123_16
	movq	144(%rbp), %rcx
	callq	mi_free
.LBB123_16:
	movb	$1, 159(%rbp)
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_,unique,123
	.seh_endproc
	.def	"?dtor$30@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$30@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_@4HA":
.seh_proc "?dtor$30@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_@4HA"
.LBB123_30:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 144(%rbp)
	je	.LBB123_32
	movq	136(%rbp), %rcx
	callq	mi_free
	nop
.LBB123_32:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_,unique,123
	.seh_endproc
	.def	"?dtor$38@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$38@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_@4HA":
.seh_proc "?dtor$38@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_@4HA"
.LBB123_38:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpb	$0, 159(%rbp)
	je	.LBB123_39
	leaq	-88(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtNtB4_4iter8adapters7flatten7FlattenINtNtBG_3map3MapINtNtNtB4_5slice4iter4IterReENCNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib00EEEB2a_
	nop
.LBB123_39:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_,unique,123
	.seh_endproc
	.def	"?dtor$41@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$41@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_@4HA":
.seh_proc "?dtor$41@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_@4HA"
.LBB123_41:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movq	104(%rbp), %rcx
	callq	mi_free
	nop
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_,unique,123
	.seh_endproc
	.def	"?dtor$63@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$63@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_@4HA":
.seh_proc "?dtor$63@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_@4HA"
.LBB123_63:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movq	%rbp, %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtNtB4_4iter8adapters7flatten7FlattenINtNtBG_3map3MapINtNtNtB4_5slice4iter4IterReENCNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib00EEEB2a_
	leaq	80(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecNtNtBG_6string6StringEECs5UjBoGikVie_6cudarc
	movb	$0, 159(%rbp)
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_,unique,123
	.seh_endproc
	.def	"?dtor$64@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$64@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_@4HA":
.seh_proc "?dtor$64@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_@4HA"
.LBB123_64:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	leaq	112(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecNtNtBG_6string6StringEECs5UjBoGikVie_6cudarc
	nop
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
.Lfunc_end123:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_,unique,123
	.seh_endproc
	.section	.xdata,"dr",associative,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_,unique,7
	.p2align	2, 0x0
$cppxdata$_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_:
	.long	429065506
	.long	6
	.long	$stateUnwindMap$_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_@IMGREL
	.long	0
	.long	0
	.long	9
	.long	$ip2state$_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_@IMGREL
	.long	288
	.long	0
	.long	1
$stateUnwindMap$_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_:
	.long	-1
	.long	"?dtor$41@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_@4HA"@IMGREL
	.long	0
	.long	"?dtor$64@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_@4HA"@IMGREL
	.long	0
	.long	"?dtor$38@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_@4HA"@IMGREL
	.long	2
	.long	"?dtor$63@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_@4HA"@IMGREL
	.long	3
	.long	"?dtor$30@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_@4HA"@IMGREL
	.long	2
	.long	"?dtor$14@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_@4HA"@IMGREL
$ip2state$_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_:
	.long	.Lfunc_begin123@IMGREL
	.long	-1
	.long	.Ltmp40@IMGREL
	.long	2
	.long	.Ltmp46@IMGREL
	.long	5
	.long	.Ltmp44@IMGREL
	.long	4
	.long	.Ltmp42@IMGREL
	.long	3
	.long	.Ltmp48@IMGREL
	.long	1
	.long	.Ltmp49@IMGREL
	.long	-1
	.long	.Ltmp50@IMGREL
	.long	1
	.long	.Ltmp51@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_,unique,123

	.def	_RNCINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB4_13__nvrtcProgramOaENtB4_11nvrtcResultE0B8_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNCINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB4_13__nvrtcProgramOaENtB4_11nvrtcResultE0B8_,unique,124
	.p2align	4
_RNCINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB4_13__nvrtcProgramOaENtB4_11nvrtcResultE0B8_:
.Lfunc_begin124:
.seh_proc _RNCINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB4_13__nvrtcProgramOaENtB4_11nvrtcResultE0B8_
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$80, %rsp
	.seh_stackalloc 80
	leaq	80(%rsp), %rbp
	.seh_setframe %rbp, 80
	.seh_endprologue
	movq	$-2, -8(%rbp)
	movq	%rcx, -48(%rbp)
	leaq	_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtReNtB6_7Display3fmtCs5UjBoGikVie_6cudarc(%rip), %rax
	movq	%rax, -40(%rbp)
	movq	%rdx, -16(%rbp)
	movq	%rdx, -32(%rbp)
	leaq	_RNvXs6_NtCskIq6Fm6qntW_10libloading5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt(%rip), %rax
	movq	%rax, -24(%rbp)
.Ltmp52:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.466(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.468(%rip), %r8
	leaq	-48(%rbp), %rdx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking9panic_fmt
	nop
.Ltmp53:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNCINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB4_13__nvrtcProgramOaENtB4_11nvrtcResultE0B8_@IMGREL
	.section	.text$unlikely,"xr",one_only,_RNCINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB4_13__nvrtcProgramOaENtB4_11nvrtcResultE0B8_,unique,124
	.seh_endproc
	.def	"?dtor$2@?0?_RNCINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB4_13__nvrtcProgramOaENtB4_11nvrtcResultE0B8_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$2@?0?_RNCINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB4_13__nvrtcProgramOaENtB4_11nvrtcResultE0B8_@4HA":
.seh_proc "?dtor$2@?0?_RNCINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB4_13__nvrtcProgramOaENtB4_11nvrtcResultE0B8_@4HA"
.LBB124_2:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	80(%rdx), %rbp
	.seh_endprologue
	movq	-16(%rbp), %rdx
	movl	(%rdx), %eax
	cmpl	$4, %eax
	je	.LBB124_5
	cmpl	$2, %eax
	je	.LBB124_5
	testl	%eax, %eax
	jne	.LBB124_7
.LBB124_5:
	movq	8(%rdx), %rcx
	cmpq	$0, 16(%rdx)
	movb	$0, (%rcx)
	je	.LBB124_7
	callq	mi_free
	nop
.LBB124_7:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end124:
	.seh_handlerdata
	.section	.text$unlikely,"xr",one_only,_RNCINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB4_13__nvrtcProgramOaENtB4_11nvrtcResultE0B8_,unique,124
	.seh_endproc
	.section	.xdata,"dr",associative,_RNCINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB4_13__nvrtcProgramOaENtB4_11nvrtcResultE0B8_,unique,8
	.p2align	2, 0x0
$cppxdata$_RNCINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB4_13__nvrtcProgramOaENtB4_11nvrtcResultE0B8_:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNCINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB4_13__nvrtcProgramOaENtB4_11nvrtcResultE0B8_@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RNCINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB4_13__nvrtcProgramOaENtB4_11nvrtcResultE0B8_@IMGREL
	.long	72
	.long	0
	.long	1
$stateUnwindMap$_RNCINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB4_13__nvrtcProgramOaENtB4_11nvrtcResultE0B8_:
	.long	-1
	.long	"?dtor$2@?0?_RNCINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB4_13__nvrtcProgramOaENtB4_11nvrtcResultE0B8_@4HA"@IMGREL
$ip2state$_RNCINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB4_13__nvrtcProgramOaENtB4_11nvrtcResultE0B8_:
	.long	.Lfunc_begin124@IMGREL
	.long	-1
	.long	.Ltmp52@IMGREL
	.long	0
	.long	.Ltmp53@IMGREL
	.long	-1
	.section	.text$unlikely,"xr",one_only,_RNCINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB4_13__nvrtcProgramOaENtB4_11nvrtcResultE0B8_,unique,124

	.def	_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_,unique,125
	.p2align	4
_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_:
.Lfunc_begin125:
.seh_proc _RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$80, %rsp
	.seh_stackalloc 80
	leaq	80(%rsp), %rbp
	.seh_setframe %rbp, 80
	.seh_endprologue
	movq	$-2, -8(%rbp)
	movq	%rcx, -48(%rbp)
	leaq	_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtReNtB6_7Display3fmtCs5UjBoGikVie_6cudarc(%rip), %rax
	movq	%rax, -40(%rbp)
	movq	%rdx, -16(%rbp)
	movq	%rdx, -32(%rbp)
	leaq	_RNvXs6_NtCskIq6Fm6qntW_10libloading5errorNtB5_5ErrorNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt(%rip), %rax
	movq	%rax, -24(%rbp)
.Ltmp54:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.466(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.472(%rip), %r8
	leaq	-48(%rbp), %rdx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking9panic_fmt
	nop
.Ltmp55:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_@IMGREL
	.section	.text$unlikely,"xr",one_only,_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_,unique,125
	.seh_endproc
	.def	"?dtor$2@?0?_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$2@?0?_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_@4HA":
.seh_proc "?dtor$2@?0?_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_@4HA"
.LBB125_2:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	80(%rdx), %rbp
	.seh_endprologue
	movq	-16(%rbp), %rdx
	movl	(%rdx), %eax
	cmpl	$4, %eax
	je	.LBB125_5
	cmpl	$2, %eax
	je	.LBB125_5
	testl	%eax, %eax
	jne	.LBB125_7
.LBB125_5:
	movq	8(%rdx), %rcx
	cmpq	$0, 16(%rdx)
	movb	$0, (%rcx)
	je	.LBB125_7
	callq	mi_free
	nop
.LBB125_7:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end125:
	.seh_handlerdata
	.section	.text$unlikely,"xr",one_only,_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_,unique,125
	.seh_endproc
	.section	.xdata,"dr",associative,_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_,unique,9
	.p2align	2, 0x0
$cppxdata$_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_@IMGREL
	.long	72
	.long	0
	.long	1
$stateUnwindMap$_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_:
	.long	-1
	.long	"?dtor$2@?0?_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_@4HA"@IMGREL
$ip2state$_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_:
	.long	.Lfunc_begin125@IMGREL
	.long	-1
	.long	.Ltmp54@IMGREL
	.long	0
	.long	.Ltmp55@IMGREL
	.long	-1
	.section	.text$unlikely,"xr",one_only,_RNCINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB4_14cudaError_enumE0B8_,unique,125

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_16cuCtxSynchronize0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_16cuCtxSynchronize0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_,unique,126
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_16cuCtxSynchronize0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_:
.Lfunc_begin126:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_16cuCtxSynchronize0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB126_1
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.590(%rip), %rcx
	movl	$16, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB126_1:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end126:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCNtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumOPaEB1O_E10initializeNCINvB1e_11get_or_initNCNvB1Q_16cuGetErrorString0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1U_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCNtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumOPaEB1O_E10initializeNCINvB1e_11get_or_initNCNvB1Q_16cuGetErrorString0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1U_,unique,127
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCNtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumOPaEB1O_E10initializeNCINvB1e_11get_or_initNCNvB1Q_16cuGetErrorString0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1U_:
.Lfunc_begin127:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCNtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumOPaEB1O_E10initializeNCINvB1e_11get_or_initNCNvB1Q_16cuGetErrorString0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1U_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB127_1
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.592(%rip), %rcx
	movl	$16, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCNtB2_14cudaError_enumOPaEBL_EB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB127_1:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end127:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB2q_13cuMemFreeHost0E0zE0E0INtNtNtB1T_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB2u_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB2q_13cuMemFreeHost0E0zE0E0INtNtNtB1T_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB2u_.llvm.1750587498003715262,unique,128
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB2q_13cuMemFreeHost0E0zE0E0INtNtNtB1T_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB2u_.llvm.1750587498003715262
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB2q_13cuMemFreeHost0E0zE0E0INtNtNtB1T_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB2u_.llvm.1750587498003715262:
.Lfunc_begin128:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB2q_13cuMemFreeHost0E0zE0E0INtNtNtB1T_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB2u_.llvm.1750587498003715262
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB128_1
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.526(%rip), %rcx
	movl	$13, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_11CUstream_stENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB128_1:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end128:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB2s_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB2s_20cuMemcpyDtoHAsync_v20E0zE0E0INtNtNtB1T_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB2w_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB2s_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB2s_20cuMemcpyDtoHAsync_v20E0zE0E0INtNtNtB1T_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB2w_.llvm.1750587498003715262,unique,129
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB2s_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB2s_20cuMemcpyDtoHAsync_v20E0zE0E0INtNtNtB1T_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB2w_.llvm.1750587498003715262
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB2s_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB2s_20cuMemcpyDtoHAsync_v20E0zE0E0INtNtNtB1T_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB2w_.llvm.1750587498003715262:
.Lfunc_begin129:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB2s_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB2s_20cuMemcpyDtoHAsync_v20E0zE0E0INtNtNtB1T_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB2w_.llvm.1750587498003715262
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB2n_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB2n_20cuMemcpyDtoHAsync_v20E0zE0E0B2r_.llvm.1750587498003715262
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end129:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtB1R_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1R_11nvrtcGetPTX0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtB1R_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1R_11nvrtcGetPTX0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_,unique,130
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtB1R_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1R_11nvrtcGetPTX0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_:
.Lfunc_begin130:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtB1R_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1R_11nvrtcGetPTX0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB130_1
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.476(%rip), %rcx
	movl	$11, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB2_13__nvrtcProgramOaENtB2_11nvrtcResultEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB130_1:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end130:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtB1R_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1R_18nvrtcGetProgramLog0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtB1R_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1R_18nvrtcGetProgramLog0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_,unique,131
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtB1R_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1R_18nvrtcGetProgramLog0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_:
.Lfunc_begin131:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtB1R_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1R_18nvrtcGetProgramLog0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB131_1
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.485(%rip), %rcx
	movl	$18, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB2_13__nvrtcProgramOaENtB2_11nvrtcResultEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB131_1:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end131:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtB1R_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1R_15nvrtcGetPTXSize0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtB1R_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1R_15nvrtcGetPTXSize0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_,unique,132
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtB1R_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1R_15nvrtcGetPTXSize0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_:
.Lfunc_begin132:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtB1R_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1R_15nvrtcGetPTXSize0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB132_1
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.481(%rip), %rcx
	movl	$15, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB2_13__nvrtcProgramOjENtB2_11nvrtcResultEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB132_1:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end132:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtB1R_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1R_22nvrtcGetProgramLogSize0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtB1R_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1R_22nvrtcGetProgramLogSize0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_,unique,133
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtB1R_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1R_22nvrtcGetProgramLogSize0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_:
.Lfunc_begin133:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtB1R_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1R_22nvrtcGetProgramLogSize0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB133_1
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.492(%rip), %rcx
	movl	$22, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys4loadFUKCONtB2_13__nvrtcProgramOjENtB2_11nvrtcResultEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB133_1:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end133:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramlPPaENtB1R_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1R_19nvrtcCompileProgram0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramlPPaENtB1R_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1R_19nvrtcCompileProgram0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_,unique,134
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramlPPaENtB1R_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1R_19nvrtcCompileProgram0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_:
.Lfunc_begin134:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramlPPaENtB1R_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1R_19nvrtcCompileProgram0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramlPPaENtB1M_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1M_19nvrtcCompileProgram0E0zE0E0B1Q_
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end134:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_17cuEventDestroy_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_17cuEventDestroy_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262,unique,135
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_17cuEventDestroy_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_17cuEventDestroy_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262:
.Lfunc_begin135:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_17cuEventDestroy_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB135_1
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.613(%rip), %rcx
	movl	$17, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_10CUevent_stENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB135_1:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end135:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stONtB1R_11CUstream_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_13cuEventRecord0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stONtB1R_11CUstream_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_13cuEventRecord0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262,unique,136
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stONtB1R_11CUstream_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_13cuEventRecord0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stONtB1R_11CUstream_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_13cuEventRecord0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262:
.Lfunc_begin136:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stONtB1R_11CUstream_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_13cuEventRecord0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stONtB1M_11CUstream_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_13cuEventRecord0E0zE0E0B1Q_.llvm.1750587498003715262
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end136:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUgraph_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_14cuGraphDestroy0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUgraph_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_14cuGraphDestroy0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262,unique,137
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUgraph_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_14cuGraphDestroy0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUgraph_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_14cuGraphDestroy0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262:
.Lfunc_begin137:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUgraph_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_14cuGraphDestroy0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUgraph_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_14cuGraphDestroy0E0zE0E0B1Q_.llvm.1750587498003715262
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end137:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_18cuStreamDestroy_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_18cuStreamDestroy_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_,unique,138
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_18cuStreamDestroy_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_:
.Lfunc_begin138:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_18cuStreamDestroy_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB138_1
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.667(%rip), %rcx
	movl	$18, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_11CUstream_stENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB138_1:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end138:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_19cuStreamSynchronize0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_19cuStreamSynchronize0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262,unique,139
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_19cuStreamSynchronize0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_19cuStreamSynchronize0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262:
.Lfunc_begin139:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_19cuStreamSynchronize0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB139_1
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.699(%rip), %rcx
	movl	$19, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_11CUstream_stENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB139_1:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end139:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stNtB1R_24CUstreamCaptureMode_enumENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_23cuStreamBeginCapture_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stNtB1R_24CUstreamCaptureMode_enumENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_23cuStreamBeginCapture_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262,unique,140
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stNtB1R_24CUstreamCaptureMode_enumENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_23cuStreamBeginCapture_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stNtB1R_24CUstreamCaptureMode_enumENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_23cuStreamBeginCapture_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262:
.Lfunc_begin140:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stNtB1R_24CUstreamCaptureMode_enumENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_23cuStreamBeginCapture_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stNtB1M_24CUstreamCaptureMode_enumENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_23cuStreamBeginCapture_v20E0zE0E0B1Q_.llvm.1750587498003715262
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end140:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stONtB1R_10CUevent_stmENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_17cuStreamWaitEvent0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stONtB1R_10CUevent_stmENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_17cuStreamWaitEvent0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262,unique,141
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stONtB1R_10CUevent_stmENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_17cuStreamWaitEvent0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stONtB1R_10CUevent_stmENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_17cuStreamWaitEvent0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262:
.Lfunc_begin141:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stONtB1R_10CUevent_stmENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_17cuStreamWaitEvent0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stONtB1M_10CUevent_stmENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_17cuStreamWaitEvent0E0zE0E0B1Q_.llvm.1750587498003715262
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end141:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stOONtB1R_10CUgraph_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_18cuStreamEndCapture0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stOONtB1R_10CUgraph_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_18cuStreamEndCapture0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_,unique,142
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stOONtB1R_10CUgraph_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_18cuStreamEndCapture0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_:
.Lfunc_begin142:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stOONtB1R_10CUgraph_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_18cuStreamEndCapture0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stOONtB1M_10CUgraph_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_18cuStreamEndCapture0E0zE0E0B1Q_
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end142:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_18cuGraphExecDestroy0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_18cuGraphExecDestroy0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262,unique,143
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_18cuGraphExecDestroy0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_18cuGraphExecDestroy0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262:
.Lfunc_begin143:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_18cuGraphExecDestroy0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_18cuGraphExecDestroy0E0zE0E0B1Q_.llvm.1750587498003715262
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end143:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB1R_11CUstream_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_13cuGraphLaunch0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB1R_11CUstream_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_13cuGraphLaunch0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262,unique,144
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB1R_11CUstream_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_13cuGraphLaunch0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB1R_11CUstream_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_13cuGraphLaunch0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262:
.Lfunc_begin144:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB1R_11CUstream_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_13cuGraphLaunch0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB144_1
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.522(%rip), %rcx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_14CUgraphExec_stONtB2_11CUstream_stENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB144_1:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end144:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_15cuCtxDestroy_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_15cuCtxDestroy_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_,unique,145
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_15cuCtxDestroy_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_:
.Lfunc_begin145:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_15cuCtxDestroy_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB145_1
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.560(%rip), %rcx
	movl	$15, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_8CUctx_stENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB145_1:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end145:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_15cuCtxSetCurrent0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_15cuCtxSetCurrent0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262,unique,146
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_15cuCtxSetCurrent0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_15cuCtxSetCurrent0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262:
.Lfunc_begin146:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_15cuCtxSetCurrent0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB146_1
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.562(%rip), %rcx
	movl	$15, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCONtB2_8CUctx_stENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB146_1:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end146:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_14cuModuleUnload0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_14cuModuleUnload0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262,unique,147
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_14cuModuleUnload0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_14cuModuleUnload0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262:
.Lfunc_begin147:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_14cuModuleUnload0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_14cuModuleUnload0E0zE0E0B1Q_.llvm.1750587498003715262
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end147:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stmmmmmmmONtB1R_11CUstream_stOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidB32_ENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_14cuLaunchKernel0E0zE0E0INtNtNtB38_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stmmmmmmmONtB1R_11CUstream_stOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidB32_ENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_14cuLaunchKernel0E0zE0E0INtNtNtB38_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262,unique,148
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stmmmmmmmONtB1R_11CUstream_stOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidB32_ENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_14cuLaunchKernel0E0zE0E0INtNtNtB38_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stmmmmmmmONtB1R_11CUstream_stOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidB32_ENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_14cuLaunchKernel0E0zE0E0INtNtNtB38_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262:
.Lfunc_begin148:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stmmmmmmmONtB1R_11CUstream_stOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidB32_ENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_14cuLaunchKernel0E0zE0E0INtNtNtB38_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stmmmmmmmONtB1M_11CUstream_stOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidB2X_ENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_14cuLaunchKernel0E0zE0E0B1Q_.llvm.1750587498003715262
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end148:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidjmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB2t_14cuMemHostAlloc0E0zE0E0INtNtNtB1U_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB2x_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidjmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB2t_14cuMemHostAlloc0E0zE0E0INtNtNtB1U_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB2x_.llvm.1750587498003715262,unique,149
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidjmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB2t_14cuMemHostAlloc0E0zE0E0INtNtNtB1U_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB2x_.llvm.1750587498003715262
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidjmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB2t_14cuMemHostAlloc0E0zE0E0INtNtNtB1U_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB2x_.llvm.1750587498003715262:
.Lfunc_begin149:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidjmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB2t_14cuMemHostAlloc0E0zE0E0INtNtNtB1U_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB2x_.llvm.1750587498003715262
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidjmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB2o_14cuMemHostAlloc0E0zE0E0B2s_.llvm.1750587498003715262
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end149:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramENtB1S_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1S_19nvrtcDestroyProgram0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramENtB1S_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1S_19nvrtcDestroyProgram0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_,unique,150
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramENtB1S_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1S_19nvrtcDestroyProgram0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_:
.Lfunc_begin150:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramENtB1S_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1S_19nvrtcDestroyProgram0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramENtB1N_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1N_19nvrtcDestroyProgram0E0zE0E0B1R_
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end150:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramPaB2H_lPB2H_B2O_ENtB1S_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1S_18nvrtcCreateProgram0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramPaB2H_lPB2H_B2O_ENtB1S_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1S_18nvrtcCreateProgram0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262,unique,151
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramPaB2H_lPB2H_B2O_ENtB1S_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1S_18nvrtcCreateProgram0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramPaB2H_lPB2H_B2O_ENtB1S_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1S_18nvrtcCreateProgram0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262:
.Lfunc_begin151:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramPaB2H_lPB2H_B2O_ENtB1S_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1S_18nvrtcCreateProgram0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramPaB2C_lPB2C_B2J_ENtB1N_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1N_18nvrtcCreateProgram0E0zE0E0B1R_.llvm.1750587498003715262
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end151:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stmENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_13cuEventCreate0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stmENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_13cuEventCreate0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262,unique,152
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stmENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_13cuEventCreate0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stmENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_13cuEventCreate0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262:
.Lfunc_begin152:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stmENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_13cuEventCreate0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stmENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_13cuEventCreate0E0zE0E0B1R_.llvm.1750587498003715262
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end152:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stmENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_14cuStreamCreate0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stmENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_14cuStreamCreate0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_,unique,153
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stmENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_14cuStreamCreate0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_:
.Lfunc_begin153:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stmENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_14cuStreamCreate0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stmENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_14cuStreamCreate0E0zE0E0B1R_
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end153:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB1S_10CUgraph_styENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_27cuGraphInstantiateWithFlags0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB1S_10CUgraph_styENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_27cuGraphInstantiateWithFlags0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_,unique,154
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB1S_10CUgraph_styENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_27cuGraphInstantiateWithFlags0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_:
.Lfunc_begin154:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB1S_10CUgraph_styENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_27cuGraphInstantiateWithFlags0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB1N_10CUgraph_styENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_27cuGraphInstantiateWithFlags0E0zE0E0B1R_
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end154:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_15cuCtxGetCurrent0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_15cuCtxGetCurrent0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262,unique,155
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_15cuCtxGetCurrent0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_15cuCtxGetCurrent0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262:
.Lfunc_begin155:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_15cuCtxGetCurrent0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB155_1
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.561(%rip), %rcx
	movl	$15, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCOONtB2_8CUctx_stENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB155_1:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end155:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stlENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_24cuDevicePrimaryCtxRetain0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stlENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_24cuDevicePrimaryCtxRetain0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_,unique,156
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stlENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_24cuDevicePrimaryCtxRetain0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_:
.Lfunc_begin156:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stlENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_24cuDevicePrimaryCtxRetain0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stlENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_24cuDevicePrimaryCtxRetain0E0zE0E0B1R_
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end156:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_16cuModuleLoadData0E0zE0E0INtNtNtB2G_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_16cuModuleLoadData0E0zE0E0INtNtNtB2G_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_,unique,157
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_16cuModuleLoadData0E0zE0E0INtNtNtB2G_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_:
.Lfunc_begin157:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_16cuModuleLoadData0E0zE0E0INtNtNtB2G_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB157_1
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.605(%rip), %rcx
	movl	$16, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCOONtB2_8CUmod_stPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB157_1:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end157:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPaENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_12cuModuleLoad0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPaENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_12cuModuleLoad0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_,unique,158
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPaENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_12cuModuleLoad0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_:
.Lfunc_begin158:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPaENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_12cuModuleLoad0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPaENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_12cuModuleLoad0E0zE0E0B1R_
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end158:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stONtB1S_8CUmod_stPaENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_19cuModuleGetFunction0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stONtB1S_8CUmod_stPaENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_19cuModuleGetFunction0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262,unique,159
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stONtB1S_8CUmod_stPaENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_19cuModuleGetFunction0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stONtB1S_8CUmod_stPaENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_19cuModuleGetFunction0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262:
.Lfunc_begin159:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stONtB1S_8CUmod_stPaENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_19cuModuleGetFunction0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stONtB1N_8CUmod_stPaENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_19cuModuleGetFunction0E0zE0E0B1R_.llvm.1750587498003715262
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end159:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOlNtNtNtCs5UjBoGikVie_6cudarc6driver3sys23CUdevice_attribute_enumlENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_20cuDeviceGetAttribute0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOlNtNtNtCs5UjBoGikVie_6cudarc6driver3sys23CUdevice_attribute_enumlENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_20cuDeviceGetAttribute0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262,unique,160
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOlNtNtNtCs5UjBoGikVie_6cudarc6driver3sys23CUdevice_attribute_enumlENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_20cuDeviceGetAttribute0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOlNtNtNtCs5UjBoGikVie_6cudarc6driver3sys23CUdevice_attribute_enumlENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_20cuDeviceGetAttribute0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262:
.Lfunc_begin160:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOlNtNtNtCs5UjBoGikVie_6cudarc6driver3sys23CUdevice_attribute_enumlENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_20cuDeviceGetAttribute0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOlNtNtNtCs5UjBoGikVie_6cudarc6driver3sys23CUdevice_attribute_enumlENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_20cuDeviceGetAttribute0E0zE0E0B1R_.llvm.1750587498003715262
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end160:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOllENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_11cuDeviceGet0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOllENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_11cuDeviceGet0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_,unique,161
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOllENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_11cuDeviceGet0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_:
.Lfunc_begin161:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOllENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_11cuDeviceGet0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOllENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_11cuDeviceGet0E0zE0E0B1T_
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end161:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOyjENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_13cuMemAlloc_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOyjENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_13cuMemAlloc_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_.llvm.1750587498003715262,unique,162
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOyjENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_13cuMemAlloc_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_.llvm.1750587498003715262
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOyjENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_13cuMemAlloc_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_.llvm.1750587498003715262:
.Lfunc_begin162:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOyjENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_13cuMemAlloc_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_.llvm.1750587498003715262
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOyjENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_13cuMemAlloc_v20E0zE0E0B1T_.llvm.1750587498003715262
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end162:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1U_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_15cuMemAllocAsync0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1U_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_15cuMemAllocAsync0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_.llvm.1750587498003715262,unique,163
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1U_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_15cuMemAllocAsync0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_.llvm.1750587498003715262
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1U_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_15cuMemAllocAsync0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_.llvm.1750587498003715262:
.Lfunc_begin163:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1U_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_15cuMemAllocAsync0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_.llvm.1750587498003715262
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1P_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_15cuMemAllocAsync0E0zE0E0B1T_.llvm.1750587498003715262
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end163:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKClENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_28cuDevicePrimaryCtxRelease_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKClENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_28cuDevicePrimaryCtxRelease_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_,unique,164
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKClENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_28cuDevicePrimaryCtxRelease_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_:
.Lfunc_begin164:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKClENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_28cuDevicePrimaryCtxRelease_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB164_1
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.856(%rip), %rcx
	movl	$28, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKClENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB164_1:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end164:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_6cuInit0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_6cuInit0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_,unique,165
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_6cuInit0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_:
.Lfunc_begin165:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_6cuInit0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB165_1
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.931(%rip), %rcx
	movl	$6, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCmENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB165_1:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end165:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_12cuMemFree_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_12cuMemFree_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262,unique,166
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_12cuMemFree_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_12cuMemFree_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262:
.Lfunc_begin166:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_12cuMemFree_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB166_1
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.510(%rip), %rcx
	movl	$12, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCyENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB166_1:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end166:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_14cuMemFreeAsync0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_14cuMemFreeAsync0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262,unique,167
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_14cuMemFreeAsync0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_14cuMemFreeAsync0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262:
.Lfunc_begin167:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_14cuMemFreeAsync0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_14cuMemFreeAsync0E0zE0E0B1R_.llvm.1750587498003715262
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end167:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_styB1P_jONtB1S_11CUstream_stENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_17cuMemcpyPeerAsync0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_styB1P_jONtB1S_11CUstream_stENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_17cuMemcpyPeerAsync0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262,unique,168
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_styB1P_jONtB1S_11CUstream_stENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_17cuMemcpyPeerAsync0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_styB1P_jONtB1S_11CUstream_stENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_17cuMemcpyPeerAsync0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262:
.Lfunc_begin168:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_styB1P_jONtB1S_11CUstream_stENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_17cuMemcpyPeerAsync0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_styB1K_jONtB1N_11CUstream_stENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_17cuMemcpyPeerAsync0E0zE0E0B1R_.llvm.1750587498003715262
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end168:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB2s_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB2s_20cuMemcpyHtoDAsync_v20E0zE0E0INtNtNtB1U_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB2w_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB2s_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB2s_20cuMemcpyHtoDAsync_v20E0zE0E0INtNtNtB1U_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB2w_.llvm.1750587498003715262,unique,169
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB2s_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB2s_20cuMemcpyHtoDAsync_v20E0zE0E0INtNtNtB1U_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB2w_.llvm.1750587498003715262
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB2s_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB2s_20cuMemcpyHtoDAsync_v20E0zE0E0INtNtNtB1U_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB2w_.llvm.1750587498003715262:
.Lfunc_begin169:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB2s_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB2s_20cuMemcpyHtoDAsync_v20E0zE0E0INtNtNtB1U_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB2w_.llvm.1750587498003715262
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB2n_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB2n_20cuMemcpyHtoDAsync_v20E0zE0E0B2r_.llvm.1750587498003715262
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end169:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyhjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1U_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_15cuMemsetD8Async0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyhjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1U_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_15cuMemsetD8Async0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_.llvm.1750587498003715262,unique,170
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyhjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1U_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_15cuMemsetD8Async0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_.llvm.1750587498003715262
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyhjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1U_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_15cuMemsetD8Async0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_.llvm.1750587498003715262:
.Lfunc_begin170:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyhjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1U_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_15cuMemsetD8Async0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_.llvm.1750587498003715262
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyhjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1P_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_15cuMemsetD8Async0E0zE0E0B1T_.llvm.1750587498003715262
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end170:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1U_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_20cuMemcpyDtoDAsync_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1U_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_20cuMemcpyDtoDAsync_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_.llvm.1750587498003715262,unique,171
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1U_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_20cuMemcpyDtoDAsync_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_.llvm.1750587498003715262
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1U_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_20cuMemcpyDtoDAsync_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_.llvm.1750587498003715262:
.Lfunc_begin171:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1U_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_20cuMemcpyDtoDAsync_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_.llvm.1750587498003715262
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rax
	movq	(%rax), %rsi
	movq	$0, (%rax)
	testq	%rsi, %rsi
	je	.LBB171_1
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.717(%rip), %rcx
	movl	$20, %edx
	callq	_RINvNtNtCs5UjBoGikVie_6cudarc6driver3sys4loadFUKCyyjONtB2_11CUstream_stENtB2_14cudaError_enumEB6_
	movq	%rax, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB171_1:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.465(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end171:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB1e_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB38_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB1e_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB38_,unique,172
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB1e_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB38_:
.Lfunc_begin172:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB1e_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB38_
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end172:
	.seh_endproc

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB1e_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB38_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB1e_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB38_,unique,173
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB1e_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB38_:
.Lfunc_begin173:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB1e_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB38_
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end173:
	.seh_endproc

	.def	_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates,unique,174
	.globl	_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates
	.p2align	4
_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates:
.Lfunc_begin174:
.seh_proc _RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates
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
	subq	$936, %rsp
	.seh_stackalloc 936
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	movq	$-2, 800(%rbp)
	movq	%rcx, %rsi
	movq	%rdx, -16(%rbp)
	movq	%r8, -8(%rbp)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.935(%rip), %rax
	movq	%rax, -32(%rbp)
	movq	$2, -24(%rbp)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.936(%rip), %rax
	movq	%rax, -48(%rbp)
	movq	$2, -40(%rbp)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.937(%rip), %rax
	movq	%rax, -64(%rbp)
	movq	$1, -56(%rbp)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.938(%rip), %r14
	movq	%r14, 368(%rbp)
	leaq	_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtReNtB6_7Display3fmtCs5UjBoGikVie_6cudarc(%rip), %rdi
	movq	%rdi, 376(%rbp)
	leaq	-16(%rbp), %r15
	movq	%r15, 384(%rbp)
	movq	%rdi, 392(%rbp)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.940(%rip), %r12
	movq	%r12, 400(%rbp)
	movq	%rdi, 408(%rbp)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.941(%rip), %rdx
	leaq	776(%rbp), %rcx
	leaq	368(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	movq	776(%rbp), %rax
	movq	%rax, 112(%rbp)
	movq	784(%rbp), %rax
	movq	%rax, 136(%rbp)
	movq	792(%rbp), %rax
	movq	%rax, (%rbp)
	movq	%r14, 368(%rbp)
	movq	%rdi, 376(%rbp)
	movq	%r15, 384(%rbp)
	movq	%rdi, 392(%rbp)
	leaq	-32(%rbp), %r13
	movq	%r13, 400(%rbp)
	movq	%rdi, 408(%rbp)
	movq	%r12, 416(%rbp)
	movq	%rdi, 424(%rbp)
.Ltmp56:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.942(%rip), %rdx
	leaq	776(%rbp), %rcx
	leaq	368(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp57:
	movq	%rsi, 104(%rbp)
	movq	776(%rbp), %rax
	movq	%rax, 120(%rbp)
	movq	784(%rbp), %rax
	movq	%rax, 160(%rbp)
	movq	792(%rbp), %rax
	movq	%rax, 8(%rbp)
	movq	%r14, 368(%rbp)
	movq	%rdi, 376(%rbp)
	movq	%r15, 384(%rbp)
	movq	%rdi, 392(%rbp)
	movq	%r13, 400(%rbp)
	movq	%rdi, 408(%rbp)
	leaq	-48(%rbp), %rbx
	movq	%rbx, 416(%rbp)
	movq	%rdi, 424(%rbp)
	movq	%r12, 432(%rbp)
	movq	%rdi, 440(%rbp)
.Ltmp58:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.943(%rip), %rdx
	leaq	776(%rbp), %rcx
	leaq	368(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp59:
	movq	776(%rbp), %rax
	movq	%rax, 128(%rbp)
	movq	784(%rbp), %rax
	movq	%rax, 176(%rbp)
	movq	792(%rbp), %rax
	movq	%rax, 16(%rbp)
	movq	%r14, 368(%rbp)
	movq	%rdi, 376(%rbp)
	movq	%r15, 384(%rbp)
	movq	%rdi, 392(%rbp)
	movq	%r13, 400(%rbp)
	movq	%rdi, 408(%rbp)
	movq	%rbx, 416(%rbp)
	movq	%rdi, 424(%rbp)
	leaq	-64(%rbp), %rsi
	movq	%rsi, 432(%rbp)
	movq	%rdi, 440(%rbp)
	movq	%r12, 448(%rbp)
	movq	%rdi, 456(%rbp)
.Ltmp60:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.944(%rip), %rdx
	leaq	776(%rbp), %rcx
	leaq	368(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp61:
	movq	776(%rbp), %rax
	movq	%rax, 144(%rbp)
	movq	784(%rbp), %rax
	movq	%rax, 192(%rbp)
	movq	792(%rbp), %rax
	movq	%rax, 24(%rbp)
	movq	%r14, 368(%rbp)
	movq	%rdi, 376(%rbp)
	movq	%r15, 384(%rbp)
	movq	%rdi, 392(%rbp)
	movq	%r13, 400(%rbp)
	movq	%rdi, 408(%rbp)
	movq	%rbx, 416(%rbp)
	movq	%rdi, 424(%rbp)
	movq	%rsi, 432(%rbp)
	movq	%rdi, 440(%rbp)
	movq	%r12, 448(%rbp)
	movq	%rdi, 456(%rbp)
.Ltmp62:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.945(%rip), %rdx
	leaq	776(%rbp), %rcx
	leaq	368(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp63:
	movq	776(%rbp), %rax
	movq	%rax, 152(%rbp)
	movq	784(%rbp), %rax
	movq	%rax, 200(%rbp)
	movq	792(%rbp), %rax
	movq	%rax, 32(%rbp)
	movq	%r14, 368(%rbp)
	movq	%rdi, 376(%rbp)
	movq	%r15, 384(%rbp)
	movq	%rdi, 392(%rbp)
	movq	%r13, 400(%rbp)
	movq	%rdi, 408(%rbp)
	movq	%rbx, 416(%rbp)
	movq	%rdi, 424(%rbp)
	movq	%rsi, 432(%rbp)
	movq	%rdi, 440(%rbp)
	movq	%r12, 448(%rbp)
	movq	%rdi, 456(%rbp)
.Ltmp64:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.946(%rip), %rdx
	leaq	776(%rbp), %rcx
	leaq	368(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp65:
	movq	776(%rbp), %rax
	movq	%rax, 168(%rbp)
	movq	784(%rbp), %rax
	movq	%rax, 216(%rbp)
	movq	792(%rbp), %rsi
	movq	%r14, 368(%rbp)
	movq	%rdi, 376(%rbp)
	movq	%r15, 384(%rbp)
	movq	%rdi, 392(%rbp)
	movq	%r13, 400(%rbp)
	movq	%rdi, 408(%rbp)
	movq	%r12, 416(%rbp)
	movq	%rdi, 424(%rbp)
.Ltmp66:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.947(%rip), %rdx
	leaq	776(%rbp), %rcx
	leaq	368(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp67:
	movq	776(%rbp), %rax
	movq	%rax, 184(%rbp)
	movq	784(%rbp), %rax
	movq	%rax, 232(%rbp)
	movq	792(%rbp), %rax
	movq	%rax, 40(%rbp)
	movq	%r14, 368(%rbp)
	movq	%rdi, 376(%rbp)
	movq	%r15, 384(%rbp)
	movq	%rdi, 392(%rbp)
	movq	%r13, 400(%rbp)
	movq	%rdi, 408(%rbp)
	movq	%r12, 416(%rbp)
	movq	%rdi, 424(%rbp)
.Ltmp68:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.948(%rip), %rdx
	leaq	776(%rbp), %rcx
	leaq	368(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp69:
	movq	776(%rbp), %rax
	movq	%rax, 208(%rbp)
	movq	784(%rbp), %rax
	movq	%rax, 248(%rbp)
	movq	792(%rbp), %rax
	movq	%rax, 48(%rbp)
	movq	%r14, 368(%rbp)
	movq	%rdi, 376(%rbp)
	movq	%r15, 384(%rbp)
	movq	%rdi, 392(%rbp)
	movq	%r13, 400(%rbp)
	movq	%rdi, 408(%rbp)
	movq	%r12, 416(%rbp)
	movq	%rdi, 424(%rbp)
.Ltmp70:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.949(%rip), %rdx
	leaq	776(%rbp), %rcx
	leaq	368(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp71:
	movq	776(%rbp), %rax
	movq	%rax, 224(%rbp)
	movq	784(%rbp), %rax
	movq	%rax, 256(%rbp)
	movq	792(%rbp), %rax
	movq	%rax, 56(%rbp)
	movq	%r14, 368(%rbp)
	movq	%rdi, 376(%rbp)
	movq	%r15, 384(%rbp)
	movq	%rdi, 392(%rbp)
	movq	%r13, 400(%rbp)
	movq	%rdi, 408(%rbp)
	movq	%rbx, 416(%rbp)
	movq	%rdi, 424(%rbp)
	movq	%r12, 432(%rbp)
	movq	%rdi, 440(%rbp)
.Ltmp72:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.950(%rip), %rdx
	leaq	776(%rbp), %rcx
	leaq	368(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp73:
	movq	776(%rbp), %rax
	movq	%rax, 240(%rbp)
	movq	784(%rbp), %rax
	movq	%rax, 272(%rbp)
	movq	792(%rbp), %rax
	movq	%rax, 64(%rbp)
	movq	%r14, 368(%rbp)
	movq	%rdi, 376(%rbp)
	movq	%r15, 384(%rbp)
	movq	%rdi, 392(%rbp)
	movq	%r13, 400(%rbp)
	movq	%rdi, 408(%rbp)
	movq	%r12, 416(%rbp)
	movq	%rdi, 424(%rbp)
.Ltmp74:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.951(%rip), %rdx
	leaq	776(%rbp), %rcx
	leaq	368(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp75:
	movq	776(%rbp), %rax
	movq	%rax, 264(%rbp)
	movq	784(%rbp), %rax
	movq	%rax, 288(%rbp)
	movq	792(%rbp), %r13
	movq	%r14, 368(%rbp)
	movq	%rdi, 376(%rbp)
	movq	%r15, 384(%rbp)
	movq	%rdi, 392(%rbp)
	movq	%r12, 400(%rbp)
	movq	%rdi, 408(%rbp)
	movq	%rbx, 416(%rbp)
	movq	%rdi, 424(%rbp)
.Ltmp76:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.952(%rip), %rdx
	leaq	776(%rbp), %rcx
	leaq	368(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp77:
	movq	776(%rbp), %rax
	movq	%rax, 280(%rbp)
	movq	784(%rbp), %rax
	movq	%rax, 304(%rbp)
	movq	792(%rbp), %rbx
	movq	%r14, 368(%rbp)
	movq	%rdi, 376(%rbp)
	movq	%r15, 384(%rbp)
	movq	%rdi, 392(%rbp)
	movq	%r12, 400(%rbp)
	movq	%rdi, 408(%rbp)
.Ltmp78:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.953(%rip), %rdx
	leaq	776(%rbp), %rcx
	leaq	368(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp79:
	movq	776(%rbp), %rax
	movq	%rax, 296(%rbp)
	movq	784(%rbp), %rax
	movq	%rax, 312(%rbp)
	movq	792(%rbp), %rax
	movq	%rax, 72(%rbp)
	movq	%r14, 368(%rbp)
	movq	%rdi, 376(%rbp)
	movq	%r15, 384(%rbp)
	movq	%rdi, 392(%rbp)
	movq	%r12, 400(%rbp)
	movq	%rdi, 408(%rbp)
.Ltmp80:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.954(%rip), %rdx
	leaq	776(%rbp), %rcx
	leaq	368(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp81:
	movq	%rbx, 80(%rbp)
	movq	776(%rbp), %rax
	movq	%rax, 320(%rbp)
	movq	784(%rbp), %rax
	movq	%rax, 328(%rbp)
	movq	792(%rbp), %rax
	movq	%rax, 88(%rbp)
	movq	%r14, 368(%rbp)
	movq	%rdi, 376(%rbp)
	movq	%r15, 384(%rbp)
	movq	%rdi, 392(%rbp)
	movq	%r12, 400(%rbp)
	movq	%rdi, 408(%rbp)
.Ltmp82:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.955(%rip), %rdx
	leaq	776(%rbp), %rcx
	leaq	368(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp83:
	movq	%r13, %rbx
	movq	776(%rbp), %rax
	movq	%rax, 336(%rbp)
	movq	784(%rbp), %rax
	movq	%rax, 344(%rbp)
	movq	792(%rbp), %rax
	movq	%rax, 96(%rbp)
	movq	%r14, 368(%rbp)
	movq	%rdi, 376(%rbp)
	movq	%r15, 384(%rbp)
	movq	%rdi, 392(%rbp)
	movq	%r12, 400(%rbp)
	movq	%rdi, 408(%rbp)
.Ltmp84:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.956(%rip), %rdx
	leaq	776(%rbp), %rcx
	leaq	368(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp85:
	movq	776(%rbp), %rax
	movq	%rax, 352(%rbp)
	movq	784(%rbp), %rax
	movq	%rax, 360(%rbp)
	movq	792(%rbp), %r13
	movq	%r14, 368(%rbp)
	movq	%rdi, 376(%rbp)
	movq	%r15, 384(%rbp)
	movq	%rdi, 392(%rbp)
	movq	%r12, 400(%rbp)
	movq	%rdi, 408(%rbp)
.Ltmp86:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.957(%rip), %rdx
	leaq	-88(%rbp), %rcx
	leaq	368(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp87:
	movq	112(%rbp), %rax
	movq	%rax, 368(%rbp)
	movq	136(%rbp), %rax
	movq	%rax, 376(%rbp)
	movq	(%rbp), %rax
	movq	%rax, 384(%rbp)
	movq	120(%rbp), %rax
	movq	%rax, 392(%rbp)
	movq	160(%rbp), %rax
	movq	%rax, 400(%rbp)
	movq	8(%rbp), %rax
	movq	%rax, 408(%rbp)
	movq	128(%rbp), %rax
	movq	%rax, 416(%rbp)
	movq	176(%rbp), %rax
	movq	%rax, 424(%rbp)
	movq	16(%rbp), %rax
	movq	%rax, 432(%rbp)
	movq	144(%rbp), %rax
	movq	%rax, 440(%rbp)
	movq	192(%rbp), %rax
	movq	%rax, 448(%rbp)
	movq	24(%rbp), %rax
	movq	%rax, 456(%rbp)
	movq	152(%rbp), %rax
	movq	%rax, 464(%rbp)
	movq	200(%rbp), %rax
	movq	%rax, 472(%rbp)
	movq	32(%rbp), %rax
	movq	%rax, 480(%rbp)
	movq	168(%rbp), %rax
	movq	%rax, 488(%rbp)
	movq	216(%rbp), %rax
	movq	%rax, 496(%rbp)
	movq	%rsi, 504(%rbp)
	movq	184(%rbp), %rax
	movq	%rax, 512(%rbp)
	movq	232(%rbp), %rax
	movq	%rax, 520(%rbp)
	movq	40(%rbp), %rax
	movq	%rax, 528(%rbp)
	movq	208(%rbp), %rax
	movq	%rax, 536(%rbp)
	movq	248(%rbp), %rax
	movq	%rax, 544(%rbp)
	movq	48(%rbp), %rax
	movq	%rax, 552(%rbp)
	movq	224(%rbp), %rax
	movq	%rax, 560(%rbp)
	movq	256(%rbp), %rax
	movq	%rax, 568(%rbp)
	movq	56(%rbp), %rax
	movq	%rax, 576(%rbp)
	movq	240(%rbp), %rax
	movq	%rax, 584(%rbp)
	movq	272(%rbp), %rax
	movq	%rax, 592(%rbp)
	movq	64(%rbp), %rax
	movq	%rax, 600(%rbp)
	movq	264(%rbp), %rax
	movq	%rax, 608(%rbp)
	movq	288(%rbp), %rax
	movq	%rax, 616(%rbp)
	movq	%rbx, 624(%rbp)
	movq	280(%rbp), %rax
	movq	%rax, 632(%rbp)
	movq	304(%rbp), %rax
	movq	%rax, 640(%rbp)
	movq	80(%rbp), %rax
	movq	%rax, 648(%rbp)
	movq	296(%rbp), %rax
	movq	%rax, 656(%rbp)
	movq	312(%rbp), %rax
	movq	%rax, 664(%rbp)
	movq	72(%rbp), %rax
	movq	%rax, 672(%rbp)
	movq	320(%rbp), %rax
	movq	%rax, 680(%rbp)
	movq	328(%rbp), %rax
	movq	%rax, 688(%rbp)
	movq	88(%rbp), %rax
	movq	%rax, 696(%rbp)
	movq	336(%rbp), %rax
	movq	%rax, 704(%rbp)
	movq	344(%rbp), %rax
	movq	%rax, 712(%rbp)
	movq	96(%rbp), %rax
	movq	%rax, 720(%rbp)
	movq	352(%rbp), %rax
	movq	%rax, 728(%rbp)
	movq	360(%rbp), %rax
	movq	%rax, 736(%rbp)
	movq	%r13, 744(%rbp)
	movq	-72(%rbp), %rax
	movq	%rax, 768(%rbp)
	movups	-88(%rbp), %xmm0
	movups	%xmm0, 752(%rbp)
	movl	$408, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB174_17
	movq	%rax, %rdi
	leaq	368(%rbp), %rdx
	movl	$408, %r8d
	movq	%rax, %rcx
	callq	memcpy
	movq	104(%rbp), %rax
	movq	$17, (%rax)
	movq	%rdi, 8(%rax)
	movq	$17, 16(%rax)
	.seh_startepilogue
	addq	$936, %rsp
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
.LBB174_17:
.Ltmp88:
	movl	$8, %ecx
	movl	$408, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp89:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@IMGREL
	.section	.text,"xr",one_only,_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates,unique,174
	.seh_endproc
	.def	"?dtor$19@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$19@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA":
.seh_proc "?dtor$19@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"
.LBB174_19:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 112(%rbp)
	je	.LBB174_21
	movq	136(%rbp), %rcx
	callq	mi_free
	nop
.LBB174_21:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates,unique,174
	.seh_endproc
	.def	"?dtor$22@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$22@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA":
.seh_proc "?dtor$22@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"
.LBB174_22:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 120(%rbp)
	je	.LBB174_24
	movq	160(%rbp), %rcx
	callq	mi_free
	nop
.LBB174_24:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates,unique,174
	.seh_endproc
	.def	"?dtor$25@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$25@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA":
.seh_proc "?dtor$25@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"
.LBB174_25:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 128(%rbp)
	je	.LBB174_27
	movq	176(%rbp), %rcx
	callq	mi_free
	nop
.LBB174_27:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates,unique,174
	.seh_endproc
	.def	"?dtor$28@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$28@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA":
.seh_proc "?dtor$28@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"
.LBB174_28:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 144(%rbp)
	je	.LBB174_30
	movq	192(%rbp), %rcx
	callq	mi_free
	nop
.LBB174_30:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates,unique,174
	.seh_endproc
	.def	"?dtor$31@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$31@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA":
.seh_proc "?dtor$31@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"
.LBB174_31:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 152(%rbp)
	je	.LBB174_33
	movq	200(%rbp), %rcx
	callq	mi_free
	nop
.LBB174_33:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates,unique,174
	.seh_endproc
	.def	"?dtor$34@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$34@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA":
.seh_proc "?dtor$34@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"
.LBB174_34:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 168(%rbp)
	je	.LBB174_36
	movq	216(%rbp), %rcx
	callq	mi_free
	nop
.LBB174_36:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates,unique,174
	.seh_endproc
	.def	"?dtor$37@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$37@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA":
.seh_proc "?dtor$37@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"
.LBB174_37:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 184(%rbp)
	je	.LBB174_39
	movq	232(%rbp), %rcx
	callq	mi_free
	nop
.LBB174_39:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates,unique,174
	.seh_endproc
	.def	"?dtor$40@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$40@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA":
.seh_proc "?dtor$40@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"
.LBB174_40:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 208(%rbp)
	je	.LBB174_42
	movq	248(%rbp), %rcx
	callq	mi_free
	nop
.LBB174_42:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates,unique,174
	.seh_endproc
	.def	"?dtor$43@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$43@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA":
.seh_proc "?dtor$43@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"
.LBB174_43:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 224(%rbp)
	je	.LBB174_45
	movq	256(%rbp), %rcx
	callq	mi_free
	nop
.LBB174_45:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates,unique,174
	.seh_endproc
	.def	"?dtor$46@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$46@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA":
.seh_proc "?dtor$46@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"
.LBB174_46:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 240(%rbp)
	je	.LBB174_48
	movq	272(%rbp), %rcx
	callq	mi_free
	nop
.LBB174_48:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates,unique,174
	.seh_endproc
	.def	"?dtor$49@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$49@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA":
.seh_proc "?dtor$49@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"
.LBB174_49:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 264(%rbp)
	je	.LBB174_51
	movq	288(%rbp), %rcx
	callq	mi_free
	nop
.LBB174_51:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates,unique,174
	.seh_endproc
	.def	"?dtor$52@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$52@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA":
.seh_proc "?dtor$52@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"
.LBB174_52:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 280(%rbp)
	je	.LBB174_54
	movq	304(%rbp), %rcx
	callq	mi_free
	nop
.LBB174_54:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates,unique,174
	.seh_endproc
	.def	"?dtor$55@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$55@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA":
.seh_proc "?dtor$55@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"
.LBB174_55:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 296(%rbp)
	je	.LBB174_57
	movq	312(%rbp), %rcx
	callq	mi_free
	nop
.LBB174_57:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates,unique,174
	.seh_endproc
	.def	"?dtor$58@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$58@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA":
.seh_proc "?dtor$58@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"
.LBB174_58:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 320(%rbp)
	je	.LBB174_60
	movq	328(%rbp), %rcx
	callq	mi_free
	nop
.LBB174_60:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates,unique,174
	.seh_endproc
	.def	"?dtor$61@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$61@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA":
.seh_proc "?dtor$61@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"
.LBB174_61:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 336(%rbp)
	je	.LBB174_63
	movq	344(%rbp), %rcx
	callq	mi_free
	nop
.LBB174_63:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates,unique,174
	.seh_endproc
	.def	"?dtor$64@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$64@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA":
.seh_proc "?dtor$64@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"
.LBB174_64:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movq	360(%rbp), %rcx
	cmpq	$0, 352(%rbp)
	je	.LBB174_66
	callq	mi_free
	nop
.LBB174_66:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates,unique,174
	.seh_endproc
	.def	"?dtor$67@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$67@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA":
.seh_proc "?dtor$67@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"
.LBB174_67:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	leaq	368(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueANtNtCsfQUUnEvlYZE_5alloc6string6Stringj11_ECs5UjBoGikVie_6cudarc
	nop
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
.Lfunc_end174:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates,unique,174
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates,unique,10
	.p2align	2, 0x0
$cppxdata$_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates:
	.long	429065506
	.long	17
	.long	$stateUnwindMap$_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@IMGREL
	.long	0
	.long	0
	.long	20
	.long	$ip2state$_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@IMGREL
	.long	928
	.long	0
	.long	1
$stateUnwindMap$_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates:
	.long	-1
	.long	"?dtor$19@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"@IMGREL
	.long	0
	.long	"?dtor$22@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"@IMGREL
	.long	1
	.long	"?dtor$25@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"@IMGREL
	.long	2
	.long	"?dtor$28@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"@IMGREL
	.long	3
	.long	"?dtor$31@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"@IMGREL
	.long	4
	.long	"?dtor$34@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"@IMGREL
	.long	5
	.long	"?dtor$37@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"@IMGREL
	.long	6
	.long	"?dtor$40@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"@IMGREL
	.long	7
	.long	"?dtor$43@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"@IMGREL
	.long	8
	.long	"?dtor$46@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"@IMGREL
	.long	9
	.long	"?dtor$49@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"@IMGREL
	.long	10
	.long	"?dtor$52@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"@IMGREL
	.long	11
	.long	"?dtor$55@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"@IMGREL
	.long	12
	.long	"?dtor$58@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"@IMGREL
	.long	13
	.long	"?dtor$61@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"@IMGREL
	.long	14
	.long	"?dtor$64@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"@IMGREL
	.long	-1
	.long	"?dtor$67@?0?_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates@4HA"@IMGREL
$ip2state$_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates:
	.long	.Lfunc_begin174@IMGREL
	.long	-1
	.long	.Ltmp56@IMGREL
	.long	0
	.long	.Ltmp58@IMGREL
	.long	1
	.long	.Ltmp60@IMGREL
	.long	2
	.long	.Ltmp62@IMGREL
	.long	3
	.long	.Ltmp64@IMGREL
	.long	4
	.long	.Ltmp66@IMGREL
	.long	5
	.long	.Ltmp68@IMGREL
	.long	6
	.long	.Ltmp70@IMGREL
	.long	7
	.long	.Ltmp72@IMGREL
	.long	8
	.long	.Ltmp74@IMGREL
	.long	9
	.long	.Ltmp76@IMGREL
	.long	10
	.long	.Ltmp78@IMGREL
	.long	11
	.long	.Ltmp80@IMGREL
	.long	12
	.long	.Ltmp82@IMGREL
	.long	13
	.long	.Ltmp84@IMGREL
	.long	14
	.long	.Ltmp86@IMGREL
	.long	15
	.long	.Ltmp87@IMGREL
	.long	-1
	.long	.Ltmp88@IMGREL
	.long	16
	.long	.Ltmp89@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates,unique,174

	.def	_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile,unique,175
	.globl	_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile
	.p2align	4
_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile:
.Lfunc_begin175:
.seh_proc _RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile
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
	subq	$424, %rsp
	.seh_stackalloc 424
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	movq	$-2, 288(%rbp)
	movq	%rdx, 160(%rbp)
	movq	%rcx, 120(%rbp)
	movq	$0, 192(%rbp)
	movq	$8, 200(%rbp)
	movq	$0, 208(%rbp)
	movzbl	104(%r8), %eax
	cmpb	$2, %al
	movq	%r8, 272(%rbp)
	jne	.LBB175_27
	movl	$8, %edi
	xorl	%esi, %esi
	movzbl	105(%r8), %eax
	cmpb	$2, %al
	jne	.LBB175_3
.LBB175_8:
	movzbl	106(%r8), %eax
	cmpb	$2, %al
	jne	.LBB175_9
.LBB175_13:
	movzbl	107(%r8), %eax
	cmpb	$2, %al
	jne	.LBB175_14
.LBB175_18:
	testb	$1, 108(%r8)
	jne	.LBB175_42
.LBB175_19:
	cmpb	$0, (%r8)
	jne	.LBB175_20
	jmp	.LBB175_24
.LBB175_27:
	movb	%al, 168(%rbp)
	leaq	168(%rbp), %rax
	movq	%rax, 224(%rbp)
	leaq	_RNvXsg_NtCs8xEFJqa6dYS_4core3fmtbNtB5_7Display3fmt(%rip), %rax
	movq	%rax, 232(%rbp)
	movb	$1, 287(%rbp)
	movb	$1, 286(%rbp)
.Ltmp90:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.980(%rip), %rdx
	leaq	64(%rbp), %rcx
	leaq	224(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp91:
.Ltmp92:
	leaq	192(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtNtB7_6string6StringE8grow_oneCs5UjBoGikVie_6cudarc
	nop
.Ltmp93:
	movq	200(%rbp), %rdi
	movq	80(%rbp), %rax
	movq	%rax, 16(%rdi)
	movups	64(%rbp), %xmm0
	movups	%xmm0, (%rdi)
	movq	$1, 208(%rbp)
	movl	$1, %esi
	movq	272(%rbp), %r8
	movzbl	105(%r8), %eax
	cmpb	$2, %al
	je	.LBB175_8
.LBB175_3:
	movb	%al, 168(%rbp)
	leaq	168(%rbp), %rax
	movq	%rax, 224(%rbp)
	leaq	_RNvXsg_NtCs8xEFJqa6dYS_4core3fmtbNtB5_7Display3fmt(%rip), %rax
	movq	%rax, 232(%rbp)
	movb	$1, 287(%rbp)
	movb	$1, 286(%rbp)
.Ltmp94:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.981(%rip), %rdx
	leaq	40(%rbp), %rcx
	leaq	224(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp95:
	cmpq	192(%rbp), %rsi
	jne	.LBB175_7
.Ltmp96:
	leaq	192(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtNtB7_6string6StringE8grow_oneCs5UjBoGikVie_6cudarc
	nop
.Ltmp97:
	movq	200(%rbp), %rdi
.LBB175_7:
	leaq	(%rsi,%rsi,2), %rax
	movq	56(%rbp), %rcx
	movq	%rcx, 16(%rdi,%rax,8)
	movups	40(%rbp), %xmm0
	movups	%xmm0, (%rdi,%rax,8)
	incq	%rsi
	movq	%rsi, 208(%rbp)
	movq	272(%rbp), %r8
	movzbl	106(%r8), %eax
	cmpb	$2, %al
	je	.LBB175_13
.LBB175_9:
	movb	%al, 168(%rbp)
	leaq	168(%rbp), %rax
	movq	%rax, 224(%rbp)
	leaq	_RNvXsg_NtCs8xEFJqa6dYS_4core3fmtbNtB5_7Display3fmt(%rip), %rax
	movq	%rax, 232(%rbp)
	movb	$1, 287(%rbp)
	movb	$1, 286(%rbp)
.Ltmp98:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.982(%rip), %rdx
	leaq	16(%rbp), %rcx
	leaq	224(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp99:
	cmpq	192(%rbp), %rsi
	jne	.LBB175_12
.Ltmp100:
	leaq	192(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtNtB7_6string6StringE8grow_oneCs5UjBoGikVie_6cudarc
	nop
.Ltmp101:
.LBB175_12:
	movq	200(%rbp), %rax
	leaq	(%rsi,%rsi,2), %rcx
	movq	32(%rbp), %rdx
	movq	%rdx, 16(%rax,%rcx,8)
	movups	16(%rbp), %xmm0
	movups	%xmm0, (%rax,%rcx,8)
	incq	%rsi
	movq	%rsi, 208(%rbp)
	movq	272(%rbp), %r8
	movzbl	107(%r8), %eax
	cmpb	$2, %al
	je	.LBB175_18
.LBB175_14:
	movb	%al, 168(%rbp)
	leaq	168(%rbp), %rax
	movq	%rax, 224(%rbp)
	leaq	_RNvXsg_NtCs8xEFJqa6dYS_4core3fmtbNtB5_7Display3fmt(%rip), %rax
	movq	%rax, 232(%rbp)
	movb	$1, 287(%rbp)
	movb	$1, 286(%rbp)
.Ltmp102:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.983(%rip), %rdx
	leaq	-8(%rbp), %rcx
	leaq	224(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp103:
	cmpq	192(%rbp), %rsi
	jne	.LBB175_17
.Ltmp104:
	leaq	192(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtNtB7_6string6StringE8grow_oneCs5UjBoGikVie_6cudarc
	nop
.Ltmp105:
.LBB175_17:
	movq	200(%rbp), %rax
	leaq	(%rsi,%rsi,2), %rcx
	movq	8(%rbp), %rdx
	movq	%rdx, 16(%rax,%rcx,8)
	movups	-8(%rbp), %xmm0
	movups	%xmm0, (%rax,%rcx,8)
	incq	%rsi
	movq	%rsi, 208(%rbp)
	movq	272(%rbp), %r8
	testb	$1, 108(%r8)
	je	.LBB175_19
.LBB175_42:
	movl	$11, %ecx
	movl	$1, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB175_43
	movabsq	$8375961251589008685, %rcx
	movq	%rcx, (%rax)
	movq	%rax, 264(%rbp)
	movl	$1702195828, 7(%rax)
	cmpq	192(%rbp), %rsi
	jne	.LBB175_47
.Ltmp106:
	leaq	192(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtNtB7_6string6StringE8grow_oneCs5UjBoGikVie_6cudarc
	nop
.Ltmp107:
.LBB175_47:
	movq	200(%rbp), %rax
	leaq	(%rsi,%rsi,2), %rcx
	movq	$11, (%rax,%rcx,8)
	movq	264(%rbp), %rdx
	movq	%rdx, 8(%rax,%rcx,8)
	movq	$11, 16(%rax,%rcx,8)
	incq	%rsi
	movq	%rsi, 208(%rbp)
	movq	272(%rbp), %r8
	cmpb	$0, (%r8)
	je	.LBB175_24
.LBB175_20:
	movq	8(%r8), %rax
	movq	%rax, 168(%rbp)
	leaq	168(%rbp), %rax
	movq	%rax, 224(%rbp)
	leaq	_RNvXsi_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impjNtB9_7Display3fmt(%rip), %rax
	movq	%rax, 232(%rbp)
	movb	$1, 287(%rbp)
	movb	$1, 286(%rbp)
.Ltmp110:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.985(%rip), %rdx
	leaq	-32(%rbp), %rcx
	leaq	224(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp111:
	cmpq	192(%rbp), %rsi
	jne	.LBB175_23
.Ltmp112:
	leaq	192(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtNtB7_6string6StringE8grow_oneCs5UjBoGikVie_6cudarc
	nop
.Ltmp113:
.LBB175_23:
	movq	200(%rbp), %rax
	leaq	(%rsi,%rsi,2), %rcx
	movq	-16(%rbp), %rdx
	movq	%rdx, 16(%rax,%rcx,8)
	movups	-32(%rbp), %xmm0
	movups	%xmm0, (%rax,%rcx,8)
	incq	%rsi
	movq	%rsi, 208(%rbp)
	movq	272(%rbp), %r8
.LBB175_24:
	movq	40(%r8), %rdx
	movq	48(%r8), %rcx
	movq	56(%r8), %rax
	shlq	$3, %rax
	leaq	(%rax,%rax,2), %r13
	addq	%rcx, %r13
	movq	%rcx, 224(%rbp)
	movq	%rdx, 264(%rbp)
	movq	%rdx, 240(%rbp)
	movq	%r13, 248(%rbp)
	leaq	-24(%rax,%rax,2), %r14
	leaq	32(%rcx), %rdi
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.987(%rip), %r15
	leaq	88(%rbp), %r12
	movq	%rcx, 216(%rbp)
	movq	%rcx, %rax
	jmp	.LBB175_25
	.p2align	4
.LBB175_57:
	addq	$-24, %r14
	addq	$24, %rdi
	movq	%rbx, %rax
.LBB175_25:
	cmpq	%r13, %rax
	je	.LBB175_26
	leaq	24(%rax), %rbx
	movq	%rbx, 232(%rbp)
	movq	(%rax), %rcx
	movups	8(%rax), %xmm0
	movaps	%xmm0, -80(%rbp)
	cmpq	$-1, %rcx
	je	.LBB175_58
	movq	%rcx, 168(%rbp)
	movaps	-80(%rbp), %xmm0
	leaq	176(%rbp), %rax
	movups	%xmm0, (%rax)
	leaq	168(%rbp), %rax
	movq	%rax, 128(%rbp)
	leaq	_RNvXsq_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt(%rip), %rax
	movq	%rax, 136(%rbp)
.Ltmp114:
	movq	%r12, %rcx
	movq	%r15, %rdx
	leaq	128(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp115:
	cmpq	192(%rbp), %rsi
	jne	.LBB175_55
.Ltmp116:
	leaq	192(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtNtB7_6string6StringE8grow_oneCs5UjBoGikVie_6cudarc
	nop
.Ltmp117:
.LBB175_55:
	movq	200(%rbp), %rax
	leaq	(%rsi,%rsi,2), %rcx
	movq	104(%rbp), %rdx
	movq	%rdx, 16(%rax,%rcx,8)
	movups	88(%rbp), %xmm0
	movups	%xmm0, (%rax,%rcx,8)
	incq	%rsi
	movq	%rsi, 208(%rbp)
	cmpq	$0, 168(%rbp)
	je	.LBB175_57
	movq	176(%rbp), %rcx
	callq	mi_free
	jmp	.LBB175_57
.LBB175_26:
	movq	272(%rbp), %rbx
	movq	264(%rbp), %r15
	jmp	.LBB175_63
.LBB175_58:
	cmpq	%rbx, %r13
	movq	272(%rbp), %rbx
	movq	264(%rbp), %r15
	je	.LBB175_63
	movabsq	$-6148914691236517205, %rcx
	movq	%r14, %rax
	mulq	%rcx
	movq	%rdx, %r14
	shrq	$4, %r14
	jmp	.LBB175_60
	.p2align	4
.LBB175_62:
	addq	$24, %rdi
	decq	%r14
	je	.LBB175_63
.LBB175_60:
	cmpq	$0, -8(%rdi)
	je	.LBB175_62
	movq	(%rdi), %rcx
	callq	mi_free
	jmp	.LBB175_62
.LBB175_63:
	testq	%r15, %r15
	je	.LBB175_65
	movq	216(%rbp), %rcx
	callq	mi_free
.LBB175_65:
	movq	88(%rbx), %rax
	testq	%rax, %rax
	je	.LBB175_70
	movq	96(%rbx), %rcx
	movq	%rax, 128(%rbp)
	movq	%rcx, 136(%rbp)
	leaq	128(%rbp), %rax
	movq	%rax, 224(%rbp)
	leaq	_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtReNtB6_7Display3fmtCs5UjBoGikVie_6cudarc(%rip), %rax
	movq	%rax, 232(%rbp)
	movb	$0, 287(%rbp)
	movb	$1, 286(%rbp)
.Ltmp118:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.986(%rip), %rdx
	leaq	168(%rbp), %rcx
	leaq	224(%rbp), %r8
	callq	_RNvNvNtCsfQUUnEvlYZE_5alloc3fmt6format12format_inner
	nop
.Ltmp119:
	cmpq	192(%rbp), %rsi
	jne	.LBB175_69
.Ltmp120:
	leaq	192(%rbp), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtNtB7_6string6StringE8grow_oneCs5UjBoGikVie_6cudarc
	nop
.Ltmp121:
.LBB175_69:
	movq	200(%rbp), %rax
	leaq	(%rsi,%rsi,2), %rcx
	movq	184(%rbp), %rdx
	movq	%rdx, 16(%rax,%rcx,8)
	movups	168(%rbp), %xmm0
	movups	%xmm0, (%rax,%rcx,8)
	incq	%rsi
	movq	%rsi, 208(%rbp)
	movq	272(%rbp), %rbx
.LBB175_70:
	movq	16(%rbx), %r14
	movq	24(%rbx), %rdi
	movq	32(%rbx), %rax
	leaq	(%rax,%rax,2), %rcx
	leaq	(%rdi,%rcx,8), %r15
	movq	%rdi, 224(%rbp)
	movq	%r14, 240(%rbp)
	movq	%r15, 248(%rbp)
	movq	%rdi, %r13
	testq	%rax, %rax
	je	.LBB175_82
	leaq	(,%rsi,8), %rax
	leaq	(%rax,%rax,2), %r12
	leaq	24(%rdi), %r13
	leaq	192(%rbp), %rbx
	jmp	.LBB175_72
	.p2align	4
.LBB175_75:
	movq	264(%rbp), %rdx
	leaq	-24(%rdx), %rax
	movq	200(%rbp), %rcx
	movq	216(%rbp), %r8
	movq	%r8, (%rcx,%r12)
	movq	152(%rbp), %r8
	movq	%r8, 8(%rcx,%r12)
	movq	%r13, 16(%rcx,%r12)
	movq	%rdx, %r13
	incq	%rsi
	movq	%rsi, 208(%rbp)
	addq	$24, %r12
	addq	$24, %r13
	addq	$24, %rax
	cmpq	%r15, %rax
	je	.LBB175_87
.LBB175_72:
	movq	-24(%r13), %rax
	cmpq	$-1, %rax
	je	.LBB175_82
	movq	%rax, 216(%rbp)
	movq	-16(%r13), %rax
	movq	%rax, 152(%rbp)
	movq	%r13, 264(%rbp)
	movq	-8(%r13), %r13
	cmpq	192(%rbp), %rsi
	jne	.LBB175_75
.Ltmp122:
	movq	%rbx, %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtNtB7_6string6StringE8grow_oneCs5UjBoGikVie_6cudarc
	nop
.Ltmp123:
	jmp	.LBB175_75
.LBB175_82:
	movq	%r15, %rax
	subq	%r13, %rax
	movabsq	$-6148914691236517205, %rcx
	mulq	%rcx
	movq	%r13, 232(%rbp)
	cmpq	%r13, %r15
	je	.LBB175_87
	movq	%rdx, %rbx
	shrq	$4, %rbx
	addq	$8, %r13
	jmp	.LBB175_84
	.p2align	4
.LBB175_86:
	addq	$24, %r13
	decq	%rbx
	je	.LBB175_87
.LBB175_84:
	cmpq	$0, -8(%r13)
	je	.LBB175_86
	movq	(%r13), %rcx
	callq	mi_free
	jmp	.LBB175_86
.LBB175_87:
	testq	%r14, %r14
	je	.LBB175_89
	movq	%rdi, %rcx
	callq	mi_free
.LBB175_89:
	movups	192(%rbp), %xmm0
	movaps	%xmm0, 128(%rbp)
	movq	208(%rbp), %rax
	movq	%rax, 144(%rbp)
	movq	272(%rbp), %rax
	cmpq	$0, 64(%rax)
	jle	.LBB175_91
	movq	72(%rax), %rcx
	callq	mi_free
.LBB175_91:
	movq	160(%rbp), %rax
	movq	16(%rax), %rax
	movq	%rax, 152(%rbp)
	movq	144(%rbp), %r13
	testq	%r13, %r13
	je	.LBB175_92
	movq	136(%rbp), %rax
	movq	%rax, 216(%rbp)
	movq	%r13, %r14
	shlq	$4, %r14
	movl	$8, %edx
	movq	%r14, %rcx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB175_107
	movq	%rax, %rbx
	movq	%r13, 168(%rbp)
	movq	%rax, 176(%rbp)
	xorl	%r12d, %r12d
	movabsq	$-9187201950435737472, %rsi
	xorl	%edi, %edi
	jmp	.LBB175_110
	.p2align	4
.LBB175_147:
	movq	$-1, %rdx
	cmpq	$-1, %r12
	jne	.LBB175_148
.LBB175_129:
	movq	264(%rbp), %r12
	movq	%r12, %rax
	shlq	$4, %rax
	movq	%r15, (%rbx,%rax)
	movq	%rdx, 8(%rbx,%rax)
	incq	%r12
	incq	%rdi
	cmpq	%r13, %rdi
	je	.LBB175_130
.LBB175_110:
	movq	%r12, 264(%rbp)
	leaq	(%rdi,%rdi,2), %rax
	movq	216(%rbp), %rcx
	movq	16(%rcx,%rax,8), %r12
	movl	$1, %r15d
	testq	%r12, %r12
	je	.LBB175_127
	movq	%rbx, %r14
	movq	%rsi, %rbx
	movq	%r13, %rsi
	movq	216(%rbp), %rcx
	movq	8(%rcx,%rax,8), %r13
	movl	$1, %edx
	movq	%r12, %rcx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB175_112
	movq	%rax, %r15
	movq	%rax, %rcx
	movq	%r13, %rdx
	movq	%r12, %r8
	callq	memcpy
	cmpq	$15, %r12
	ja	.LBB175_117
	xorl	%ecx, %ecx
	movq	%rsi, %r13
	movq	%rbx, %rsi
	movq	%r14, %rbx
	.p2align	4
.LBB175_115:
	cmpb	$0, (%r15,%rcx)
	je	.LBB175_147
	incq	%rcx
	cmpq	%rcx, %r12
	jne	.LBB175_115
	jmp	.LBB175_127
	.p2align	4
.LBB175_117:
	leaq	7(%r15), %rax
	andq	$-8, %rax
	subq	%r15, %rax
	jne	.LBB175_118
	leaq	-16(%r12), %rcx
	xorl	%eax, %eax
	movq	%rsi, %r13
	movq	%rbx, %rsi
	movq	%r14, %rbx
	movabsq	$72340172838076672, %r10
	jmp	.LBB175_123
.LBB175_118:
	xorl	%ecx, %ecx
	movq	%rsi, %r13
	movq	%rbx, %rsi
	movq	%r14, %rbx
	movabsq	$72340172838076672, %r10
	.p2align	4
.LBB175_119:
	cmpb	$0, (%r15,%rcx)
	je	.LBB175_147
	incq	%rcx
	cmpq	%rcx, %rax
	jne	.LBB175_119
	leaq	-16(%r12), %rcx
	.p2align	4
.LBB175_122:
	cmpq	%rcx, %rax
	ja	.LBB175_124
.LBB175_123:
	movq	(%r15,%rax), %rdx
	movq	8(%r15,%rax), %r8
	movq	%r10, %r9
	subq	%rdx, %r9
	orq	%rdx, %r9
	movq	%r10, %rdx
	subq	%r8, %rdx
	orq	%r8, %rdx
	andq	%r9, %rdx
	notq	%rdx
	testq	%rsi, %rdx
	jne	.LBB175_124
	addq	$16, %rax
	jmp	.LBB175_122
	.p2align	4
.LBB175_124:
	movq	%rax, %rcx
	cmpq	%rax, %r12
	je	.LBB175_127
	.p2align	4
.LBB175_125:
	cmpb	$0, (%r15,%rcx)
	je	.LBB175_147
	incq	%rcx
	cmpq	%rcx, %r12
	jne	.LBB175_125
	.p2align	4
.LBB175_127:
	movq	%r12, 224(%rbp)
	movq	%r15, 232(%rbp)
	movq	%r12, 240(%rbp)
.Ltmp128:
	leaq	224(%rbp), %rcx
	callq	_RNvMs_NtNtCsfQUUnEvlYZE_5alloc3ffi5c_strNtB4_7CString19__from_vec_unchecked
	nop
.Ltmp129:
	movq	%rax, %r15
	jmp	.LBB175_129
.LBB175_92:
	movq	$0, 168(%rbp)
	movq	$8, 176(%rbp)
	xorl	%r12d, %r12d
.LBB175_130:
	movq	168(%rbp), %rax
	movq	%rax, 224(%rbp)
	movq	176(%rbp), %rax
	movq	%rax, 232(%rbp)
	movq	%r12, 240(%rbp)
	testq	%r12, %r12
	movq	%r12, 264(%rbp)
	je	.LBB175_131
	movq	232(%rbp), %rsi
	movq	%r12, %rbx
	shlq	$4, %rbx
	movl	$8, %edx
	movq	%rbx, %rcx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB175_155
	movq	%rax, %rdi
	cmpq	$1, %r12
	jne	.LBB175_156
	xorl	%eax, %eax
	jmp	.LBB175_159
.LBB175_131:
	movl	$8, %eax
	movq	%rax, 272(%rbp)
	movq	%rax, 216(%rbp)
	jmp	.LBB175_132
.LBB175_156:
	movq	%r12, %rcx
	andq	$-2, %rcx
	movl	$24, %edx
	xorl	%eax, %eax
	.p2align	4
.LBB175_157:
	movups	-24(%rsi,%rdx), %xmm0
	movups	%xmm0, -24(%rdi,%rdx)
	movups	-8(%rsi,%rdx), %xmm0
	movups	%xmm0, -8(%rdi,%rdx)
	addq	$2, %rax
	addq	$32, %rdx
	cmpq	%rax, %rcx
	jne	.LBB175_157
	testb	$1, %r12b
	je	.LBB175_160
.LBB175_159:
	shlq	$4, %rax
	movups	(%rsi,%rax), %xmm0
	movups	%xmm0, (%rdi,%rax)
.LBB175_160:
	leaq	(,%r12,8), %rbx
	movl	$8, %edx
	movq	%rbx, %rcx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB175_168
	cmpq	$4, %r12
	ja	.LBB175_166
	xorl	%r8d, %r8d
	jmp	.LBB175_163
.LBB175_166:
	movl	%r12d, %edx
	andl	$3, %edx
	movl	$4, %ecx
	cmovneq	%rdx, %rcx
	movq	%r12, %r8
	subq	%rcx, %r8
	movq	%rdi, %rcx
	addq	$48, %rcx
	xorl	%edx, %edx
	.p2align	4
.LBB175_167:
	movsd	-32(%rcx), %xmm0
	movsd	-48(%rcx), %xmm1
	movlhps	%xmm0, %xmm1
	movsd	(%rcx), %xmm0
	movsd	-16(%rcx), %xmm2
	movlhps	%xmm0, %xmm2
	movups	%xmm1, (%rax,%rdx,8)
	movups	%xmm2, 16(%rax,%rdx,8)
	addq	$4, %rdx
	addq	$64, %rcx
	cmpq	%rdx, %r8
	jne	.LBB175_167
.LBB175_163:
	movq	%r12, %rcx
	subq	%r8, %rcx
	shlq	$3, %r8
	.p2align	4
.LBB175_164:
	movq	(%rdi,%r8,2), %rdx
	movq	%rdx, (%rax,%r8)
	addq	$8, %r8
	decq	%rcx
	jne	.LBB175_164
	movq	%rax, 216(%rbp)
	movq	%rdi, 272(%rbp)
.LBB175_132:
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys19nvrtcCompileProgram2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB175_133
.LBB175_134:
	movq	152(%rbp), %rcx
	movq	264(%rbp), %rsi
	movl	%esi, %edx
	movq	216(%rbp), %rbx
	movq	%rbx, %r8
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys19nvrtcCompileProgram2__S(%rip)
	movl	%eax, %edi
	testq	%rsi, %rsi
	je	.LBB175_136
	movq	%rbx, %rcx
	callq	mi_free
	movq	272(%rbp), %rcx
	callq	mi_free
.LBB175_136:
	movq	232(%rbp), %rbx
	movq	240(%rbp), %rsi
	testq	%rsi, %rsi
	je	.LBB175_141
	leaq	8(%rbx), %r14
	jmp	.LBB175_138
	.p2align	4
.LBB175_140:
	addq	$16, %r14
	decq	%rsi
	je	.LBB175_141
.LBB175_138:
	movq	-8(%r14), %rcx
	cmpq	$0, (%r14)
	movb	$0, (%rcx)
	je	.LBB175_140
	callq	mi_free
	jmp	.LBB175_140
.LBB175_141:
	cmpq	$0, 224(%rbp)
	je	.LBB175_143
	movq	%rbx, %rcx
	callq	mi_free
.LBB175_143:
	movq	160(%rbp), %rax
	leaq	16(%rax), %rsi
	movq	128(%rbp), %r14
	movq	136(%rbp), %rbx
	movq	144(%rbp), %r15
	testl	%edi, %edi
	je	.LBB175_185
	movq	%r14, 224(%rbp)
	movq	%rbx, 232(%rbp)
	movq	%r15, 240(%rbp)
	movq	%rsi, 248(%rbp)
	movq	(%rsi), %rdx
.Ltmp138:
	leaq	168(%rbp), %rcx
	callq	_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result15get_program_log
	nop
.Ltmp139:
	movq	168(%rbp), %r12
	cmpq	$-1, %r12
	movq	120(%rbp), %rsi
	je	.LBB175_146
	movq	176(%rbp), %r15
	movq	%r15, %rcx
	callq	strlen
	movq	%rax, %rbx
	movl	$1, %r14d
	incq	%rbx
	je	.LBB175_181
	movl	$1, %edx
	movq	%rbx, %rcx
	callq	mi_malloc_aligned
	movq	%rax, %r14
	testq	%rax, %rax
	je	.LBB175_177
.LBB175_181:
	movq	%r14, %rcx
	movq	%r15, %rdx
	movq	%rbx, %r8
	callq	memcpy
	movups	224(%rbp), %xmm0
	movaps	%xmm0, -64(%rbp)
	movq	240(%rbp), %rax
	movq	%rax, -48(%rbp)
	testq	%r12, %r12
	je	.LBB175_183
	movq	%r15, %rcx
	callq	mi_free
.LBB175_183:
	movq	-48(%rbp), %rax
	movq	%rax, 16(%rsi)
	movaps	-64(%rbp), %xmm0
	movups	%xmm0, (%rsi)
	movq	%r14, 24(%rsi)
	movq	%rbx, 32(%rsi)
	movl	%edi, 40(%rsi)
	jmp	.LBB175_196
.LBB175_185:
	testq	%r15, %r15
	je	.LBB175_190
	leaq	8(%rbx), %rdi
	jmp	.LBB175_187
	.p2align	4
.LBB175_189:
	addq	$24, %rdi
	decq	%r15
	je	.LBB175_190
.LBB175_187:
	cmpq	$0, -8(%rdi)
	je	.LBB175_189
	movq	(%rdi), %rcx
	callq	mi_free
	jmp	.LBB175_189
.LBB175_190:
	testq	%r14, %r14
	je	.LBB175_192
	movq	%rbx, %rcx
	callq	mi_free
.LBB175_192:
	movq	(%rsi), %rdx
	movb	$0, 285(%rbp)
.Ltmp144:
	leaq	224(%rbp), %rcx
	callq	_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result7get_ptx
	nop
.Ltmp145:
	movq	224(%rbp), %rax
	cmpq	$-1, %rax
	movq	120(%rbp), %rsi
	je	.LBB175_194
	movl	244(%rbp), %ecx
	movl	%ecx, 36(%rsi)
	movups	228(%rbp), %xmm0
	movups	%xmm0, 20(%rsi)
	movabsq	$-9223372036854775808, %rcx
	movq	%rcx, 8(%rsi)
	movl	%eax, 16(%rsi)
	movq	$-1, (%rsi)
	jmp	.LBB175_196
.LBB175_194:
	movl	232(%rbp), %eax
	movabsq	$-9223372036854775805, %rcx
	movq	%rcx, (%rsi)
	movl	%eax, 8(%rsi)
.LBB175_196:
	movq	160(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCs5UjBoGikVie_6cudarc5nvrtc4safe7ProgramEBH_
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$424, %rsp
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
.LBB175_148:
	movq	%r12, 224(%rbp)
	movq	%r15, 232(%rbp)
	movq	%r12, 240(%rbp)
	movq	%rcx, 248(%rbp)
.Ltmp124:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.470(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.959.llvm.1750587498003715262(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.961.llvm.1750587498003715262(%rip), %r9
	leaq	224(%rbp), %r8
	movl	$43, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core6result13unwrap_failed
	nop
.Ltmp125:
	jmp	.LBB175_44
.LBB175_133:
.Ltmp136:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramlPPaENtBZ_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvBZ_19nvrtcCompileProgram0E0zEB13_
	nop
.Ltmp137:
	jmp	.LBB175_134
.LBB175_146:
	movl	176(%rbp), %eax
	movl	%eax, 88(%rbp)
.Ltmp142:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.475(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.959.llvm.1750587498003715262(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.958(%rip), %r9
	leaq	88(%rbp), %r8
	movl	$43, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core6result13unwrap_failed
	nop
.Ltmp143:
	jmp	.LBB175_44
.LBB175_112:
.Ltmp126:
	movl	$1, %ecx
	movq	%r12, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp127:
	jmp	.LBB175_44
.LBB175_107:
	movb	$1, 285(%rbp)
.Ltmp130:
	movl	$8, %ecx
	movq	%r14, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp131:
	jmp	.LBB175_44
.LBB175_155:
.Ltmp134:
	movl	$8, %ecx
	movq	%rbx, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp135:
	jmp	.LBB175_44
.LBB175_168:
	movq	%rdi, 112(%rbp)
.Ltmp132:
	movl	$8, %ecx
	movq	%rbx, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp133:
	jmp	.LBB175_44
.LBB175_43:
	movb	$1, 287(%rbp)
	movb	$1, 286(%rbp)
.Ltmp108:
	movl	$1, %ecx
	movl	$11, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp109:
	jmp	.LBB175_44
.LBB175_177:
.Ltmp140:
	movq	%r12, 264(%rbp)
	movq	%r15, 216(%rbp)
	movl	$1, %ecx
	movq	%rbx, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp141:
.LBB175_44:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@IMGREL
	.section	.text,"xr",one_only,_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile,unique,175
	.seh_endproc
	.def	"?dtor$30@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$30@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA":
.seh_proc "?dtor$30@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"
.LBB175_30:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 64(%rbp)
	je	.LBB175_32
	movq	72(%rbp), %rcx
	callq	mi_free
.LBB175_32:
	movb	$1, 287(%rbp)
	movb	$1, 286(%rbp)
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile,unique,175
	.seh_endproc
	.def	"?dtor$33@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$33@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA":
.seh_proc "?dtor$33@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"
.LBB175_33:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 40(%rbp)
	je	.LBB175_35
	movq	48(%rbp), %rcx
	callq	mi_free
.LBB175_35:
	movb	$1, 287(%rbp)
	movb	$1, 286(%rbp)
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile,unique,175
	.seh_endproc
	.def	"?dtor$36@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$36@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA":
.seh_proc "?dtor$36@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"
.LBB175_36:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 16(%rbp)
	je	.LBB175_38
	movq	24(%rbp), %rcx
	callq	mi_free
.LBB175_38:
	movb	$1, 287(%rbp)
	movb	$1, 286(%rbp)
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile,unique,175
	.seh_endproc
	.def	"?dtor$39@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$39@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA":
.seh_proc "?dtor$39@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"
.LBB175_39:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, -8(%rbp)
	je	.LBB175_41
	movq	(%rbp), %rcx
	callq	mi_free
.LBB175_41:
	movb	$1, 287(%rbp)
	movb	$1, 286(%rbp)
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile,unique,175
	.seh_endproc
	.def	"?dtor$48@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$48@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA":
.seh_proc "?dtor$48@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"
.LBB175_48:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, -32(%rbp)
	je	.LBB175_50
	movq	-24(%rbp), %rcx
	callq	mi_free
.LBB175_50:
	movb	$1, 287(%rbp)
	movb	$1, 286(%rbp)
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile,unique,175
	.seh_endproc
	.def	"?dtor$76@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$76@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA":
.seh_proc "?dtor$76@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"
.LBB175_76:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 168(%rbp)
	je	.LBB175_78
	movq	176(%rbp), %rcx
	callq	mi_free
.LBB175_78:
	movb	$0, 287(%rbp)
	movb	$1, 286(%rbp)
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile,unique,175
	.seh_endproc
	.def	"?dtor$79@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$79@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA":
.seh_proc "?dtor$79@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"
.LBB175_79:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movq	264(%rbp), %rax
	movq	%rax, 232(%rbp)
	cmpq	$0, 216(%rbp)
	je	.LBB175_81
	movq	152(%rbp), %rcx
	callq	mi_free
.LBB175_81:
	leaq	224(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCsfQUUnEvlYZE_5alloc3vec9into_iter8IntoIterNtNtBI_6string6StringEECs5UjBoGikVie_6cudarc
	movb	$0, 287(%rbp)
	movb	$0, 286(%rbp)
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile,unique,175
	.seh_endproc
	.def	"?dtor$93@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$93@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA":
.seh_proc "?dtor$93@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"
.LBB175_93:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 168(%rbp)
	je	.LBB175_95
	movq	176(%rbp), %rcx
	callq	mi_free
.LBB175_95:
	leaq	224(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCsfQUUnEvlYZE_5alloc3vec9into_iter8IntoIterNtNtBI_6string6StringEECs5UjBoGikVie_6cudarc
	movb	$0, 287(%rbp)
	movb	$1, 286(%rbp)
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile,unique,175
	.seh_endproc
	.def	"?dtor$96@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$96@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA":
.seh_proc "?dtor$96@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"
.LBB175_96:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 88(%rbp)
	je	.LBB175_98
	movq	96(%rbp), %rcx
	callq	mi_free
	nop
.LBB175_98:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile,unique,175
	.seh_endproc
	.def	"?dtor$99@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$99@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA":
.seh_proc "?dtor$99@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"
.LBB175_99:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movzbl	287(%rbp), %ebx
	movzbl	286(%rbp), %esi
	leaq	192(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecNtNtBG_6string6StringEECs5UjBoGikVie_6cudarc
	testb	%sil, %sil
	je	.LBB175_100
	movq	272(%rbp), %rax
	leaq	16(%rax), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecNtNtBG_6string6StringEECs5UjBoGikVie_6cudarc
.LBB175_100:
	testb	$1, %bl
	je	.LBB175_101
	movq	272(%rbp), %rax
	leaq	40(%rax), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecNtNtBG_6string6StringEECs5UjBoGikVie_6cudarc
.LBB175_101:
	movq	272(%rbp), %rax
	cmpq	$0, 64(%rax)
	jle	.LBB175_103
	movq	272(%rbp), %rax
	movq	72(%rax), %rcx
	callq	mi_free
	nop
.LBB175_103:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile,unique,175
	.seh_endproc
	.def	"?dtor$105@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$105@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA":
.seh_proc "?dtor$105@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"
.LBB175_105:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movq	160(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCs5UjBoGikVie_6cudarc5nvrtc4safe7ProgramEBH_
	nop
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile,unique,175
	.seh_endproc
	.def	"?dtor$108@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$108@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA":
.seh_proc "?dtor$108@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"
.LBB175_108:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movq	264(%rbp), %rax
	movq	%rax, 184(%rbp)
	leaq	168(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecNtNtNtBG_3ffi5c_str7CStringEECs5UjBoGikVie_6cudarc
	movb	$1, 285(%rbp)
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile,unique,175
	.seh_endproc
	.def	"?dtor$149@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$149@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA":
.seh_proc "?dtor$149@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"
.LBB175_149:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 224(%rbp)
	je	.LBB175_151
	movq	232(%rbp), %rcx
	callq	mi_free
	nop
.LBB175_151:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile,unique,175
	.seh_endproc
	.def	"?dtor$169@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$169@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA":
.seh_proc "?dtor$169@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"
.LBB175_169:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 264(%rbp)
	je	.LBB175_171
	movq	112(%rbp), %rcx
	callq	mi_free
	nop
.LBB175_171:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile,unique,175
	.seh_endproc
	.def	"?dtor$172@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$172@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA":
.seh_proc "?dtor$172@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"
.LBB175_172:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 264(%rbp)
	je	.LBB175_174
	movq	216(%rbp), %rcx
	callq	mi_free
.LBB175_174:
	movq	272(%rbp), %rax
	movq	%rax, 112(%rbp)
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile,unique,175
	.seh_endproc
	.def	"?dtor$178@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$178@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA":
.seh_proc "?dtor$178@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"
.LBB175_178:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 264(%rbp)
	je	.LBB175_180
	movq	216(%rbp), %rcx
	callq	mi_free
	nop
.LBB175_180:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile,unique,175
	.seh_endproc
	.def	"?dtor$184@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$184@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA":
.seh_proc "?dtor$184@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"
.LBB175_184:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	leaq	224(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecNtNtBG_6string6StringEECs5UjBoGikVie_6cudarc
	movb	$0, 285(%rbp)
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile,unique,175
	.seh_endproc
	.def	"?dtor$197@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$197@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA":
.seh_proc "?dtor$197@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"
.LBB175_197:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpb	$0, 285(%rbp)
	je	.LBB175_198
	leaq	128(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecNtNtBG_6string6StringEECs5UjBoGikVie_6cudarc
	nop
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
.LBB175_198:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile,unique,175
	.seh_endproc
	.def	"?dtor$200@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$200@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA":
.seh_proc "?dtor$200@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"
.LBB175_200:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movq	264(%rbp), %rcx
	callq	mi_free
	movb	$1, 287(%rbp)
	movb	$1, 286(%rbp)
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile,unique,175
	.seh_endproc
	.def	"?dtor$203@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$203@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA":
.seh_proc "?dtor$203@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"
.LBB175_203:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	leaq	224(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecNtNtNtBG_3ffi5c_str7CStringEECs5UjBoGikVie_6cudarc
	movb	$1, 285(%rbp)
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
.Lfunc_end175:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile,unique,175
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile,unique,11
	.p2align	2, 0x0
$cppxdata$_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile:
	.long	429065506
	.long	20
	.long	$stateUnwindMap$_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@IMGREL
	.long	0
	.long	0
	.long	34
	.long	$ip2state$_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@IMGREL
	.long	416
	.long	0
	.long	1
$stateUnwindMap$_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile:
	.long	-1
	.long	"?dtor$105@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"@IMGREL
	.long	0
	.long	"?dtor$197@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"@IMGREL
	.long	1
	.long	"?dtor$184@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"@IMGREL
	.long	2
	.long	"?dtor$178@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"@IMGREL
	.long	1
	.long	"?dtor$203@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"@IMGREL
	.long	4
	.long	"?dtor$169@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"@IMGREL
	.long	5
	.long	"?dtor$172@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"@IMGREL
	.long	1
	.long	"?dtor$108@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"@IMGREL
	.long	7
	.long	"?dtor$149@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"@IMGREL
	.long	0
	.long	"?dtor$99@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"@IMGREL
	.long	9
	.long	"?dtor$93@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"@IMGREL
	.long	10
	.long	"?dtor$96@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"@IMGREL
	.long	9
	.long	"?dtor$79@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"@IMGREL
	.long	9
	.long	"?dtor$76@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"@IMGREL
	.long	9
	.long	"?dtor$48@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"@IMGREL
	.long	9
	.long	"?dtor$200@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"@IMGREL
	.long	9
	.long	"?dtor$39@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"@IMGREL
	.long	9
	.long	"?dtor$36@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"@IMGREL
	.long	9
	.long	"?dtor$33@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"@IMGREL
	.long	9
	.long	"?dtor$30@?0?_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile@4HA"@IMGREL
$ip2state$_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile:
	.long	.Lfunc_begin175@IMGREL
	.long	-1
	.long	.Ltmp90@IMGREL
	.long	9
	.long	.Ltmp92@IMGREL
	.long	19
	.long	.Ltmp94@IMGREL
	.long	9
	.long	.Ltmp96@IMGREL
	.long	18
	.long	.Ltmp98@IMGREL
	.long	9
	.long	.Ltmp100@IMGREL
	.long	17
	.long	.Ltmp102@IMGREL
	.long	9
	.long	.Ltmp104@IMGREL
	.long	16
	.long	.Ltmp106@IMGREL
	.long	15
	.long	.Ltmp110@IMGREL
	.long	9
	.long	.Ltmp112@IMGREL
	.long	14
	.long	.Ltmp114@IMGREL
	.long	10
	.long	.Ltmp116@IMGREL
	.long	11
	.long	.Ltmp118@IMGREL
	.long	9
	.long	.Ltmp120@IMGREL
	.long	13
	.long	.Ltmp122@IMGREL
	.long	12
	.long	.Ltmp123@IMGREL
	.long	-1
	.long	.Ltmp128@IMGREL
	.long	7
	.long	.Ltmp129@IMGREL
	.long	-1
	.long	.Ltmp138@IMGREL
	.long	2
	.long	.Ltmp139@IMGREL
	.long	-1
	.long	.Ltmp144@IMGREL
	.long	1
	.long	.Ltmp145@IMGREL
	.long	-1
	.long	.Ltmp124@IMGREL
	.long	8
	.long	.Ltmp136@IMGREL
	.long	6
	.long	.Ltmp142@IMGREL
	.long	2
	.long	.Ltmp126@IMGREL
	.long	7
	.long	.Ltmp130@IMGREL
	.long	1
	.long	.Ltmp134@IMGREL
	.long	4
	.long	.Ltmp132@IMGREL
	.long	5
	.long	.Ltmp108@IMGREL
	.long	9
	.long	.Ltmp140@IMGREL
	.long	3
	.long	.Ltmp141@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvMs0_NtNtCs5UjBoGikVie_6cudarc5nvrtc4safeNtB5_7Program7compile,unique,175

	.def	_RNvMs0_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe5graphNtB5_9CudaGraph6launch;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs0_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe5graphNtB5_9CudaGraph6launch,unique,176
	.globl	_RNvMs0_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe5graphNtB5_9CudaGraph6launch
	.p2align	4
_RNvMs0_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe5graphNtB5_9CudaGraph6launch:
.Lfunc_begin176:
.seh_proc _RNvMs0_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe5graphNtB5_9CudaGraph6launch
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$48, %rsp
	.seh_stackalloc 48
	.seh_endprologue
	movq	(%rcx), %rsi
	movq	16(%rsi), %rbx
	xorl	%eax, %eax
	xchgl	%eax, 44(%rbx)
	testl	%eax, %eax
	jne	.LBB176_12
	movq	%rcx, %rdi
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB176_2
	leaq	40(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB176_12
.LBB176_4:
	movq	40(%rsp), %rax
	movq	16(%rbx), %rcx
	testq	%rax, %rax
	je	.LBB176_6
	movq	%rdi, %rdx
	cmpq	%rcx, %rax
	je	.LBB176_9
.LBB176_6:
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB176_7
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	movq	%rdi, %rdx
	jne	.LBB176_12
.LBB176_9:
	movq	16(%rdx), %rcx
	movq	24(%rsi), %rdx
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuGraphLaunch2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB176_10
.LBB176_11:
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuGraphLaunch2__S.llvm.1750587498003715262(%rip)
	movl	%eax, %ecx
	xorl	%eax, %eax
	cmpl	$1, %ecx
	sbbl	%eax, %eax
	orl	%ecx, %eax
.LBB176_12:
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB176_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_15cuCtxGetCurrent0E0zEB14_.llvm.1750587498003715262
	leaq	40(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB176_12
	jmp	.LBB176_4
.LBB176_10:
	movq	%rcx, %rsi
	movq	%rdx, %rdi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtBZ_11CUstream_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_13cuGraphLaunch0E0zEB13_.llvm.1750587498003715262
	movq	%rdi, %rdx
	movq	%rsi, %rcx
	jmp	.LBB176_11
.LBB176_7:
	movq	%rcx, %rbx
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxSetCurrent0E0zEB13_.llvm.1750587498003715262
	movq	%rbx, %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	movq	%rdi, %rdx
	jne	.LBB176_12
	jmp	.LBB176_9
.Lfunc_end176:
	.seh_endproc

	.def	_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module,unique,177
	.globl	_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module
	.p2align	4
_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module:
.Lfunc_begin177:
.seh_proc _RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module
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
	subq	$168, %rsp
	.seh_stackalloc 168
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	movq	$-2, 32(%rbp)
	movq	%rcx, %rsi
	movq	(%rdx), %rbx
	xorl	%eax, %eax
	xchgl	%eax, 44(%rbx)
	testl	%eax, %eax
	je	.LBB177_1
.LBB177_8:
	movl	%eax, 4(%rsi)
	movq	(%r8), %r13
	movabsq	$-9223372036854775808, %rax
	xorq	%r13, %rax
	testq	%r13, %r13
	movl	$2, %ecx
	cmovsq	%rax, %rcx
	movl	$1, (%rsi)
	leaq	.LJTI177_0(%rip), %rax
	movslq	(%rax,%rcx,4), %rcx
	addq	%rax, %rcx
	jmpq	*%rcx
.LBB177_1:
	movq	%r8, (%rbp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB177_2
.LBB177_3:
	leaq	-32(%rbp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	je	.LBB177_4
	movl	%eax, 4(%rsi)
	movq	(%rbp), %r8
	movq	(%r8), %r13
	movabsq	$-9223372036854775808, %rax
	xorq	%r13, %rax
	testq	%r13, %r13
	movl	$2, %ecx
	cmovsq	%rax, %rcx
	movl	$1, (%rsi)
	leaq	.LJTI177_0(%rip), %rax
	movslq	(%rax,%rcx,4), %rcx
	addq	%rax, %rcx
	jmpq	*%rcx
.LBB177_103:
	cmpq	$0, 8(%r8)
	je	.LBB177_100
	movq	16(%r8), %rcx
	callq	mi_free
	jmp	.LBB177_100
.LBB177_4:
	movq	-32(%rbp), %rax
	testq	%rax, %rax
	setne	%dl
	movq	16(%rbx), %rcx
	cmpq	%rcx, %rax
	sete	%al
	testb	%al, %dl
	movq	(%rbp), %r8
	jne	.LBB177_14
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB177_6
.LBB177_7:
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	movq	(%rbp), %r8
	jne	.LBB177_8
.LBB177_14:
	movq	(%r8), %r13
	movabsq	$-9223372036854775808, %rax
	xorq	%r13, %rax
	testq	%r13, %r13
	movl	$2, %r14d
	cmovsq	%rax, %r14
	leaq	.LJTI177_1(%rip), %rax
	movslq	(%rax,%r14,4), %rcx
	addq	%rax, %rcx
	jmpq	*%rcx
.LBB177_15:
	movq	8(%r8), %rax
	movq	%rax, 16(%rbp)
	movq	16(%r8), %rax
	movq	%rax, 8(%rbp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys16cuModuleLoadData2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB177_16
.LBB177_17:
	leaq	-32(%rbp), %rcx
	movq	8(%rbp), %rdx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys16cuModuleLoadData2__S(%rip)
	movl	%eax, %edi
	testl	%eax, %eax
	setne	%r12b
	movq	-32(%rbp), %r15
	cmpq	$0, 16(%rbp)
	je	.LBB177_18
	movq	8(%rbp), %rcx
	callq	mi_free
	testl	%edi, %edi
	jne	.LBB177_82
	xorl	%r8d, %r8d
	movb	$1, %dl
	movb	$1, %r9b
	movb	$1, %r10b
	jmp	.LBB177_95
.LBB177_60:
	movq	%r13, 8(%rbp)
	movq	8(%r8), %rdx
	movq	16(%r8), %r8
.Ltmp152:
	leaq	-32(%rbp), %rcx
	movq	%rdx, -48(%rbp)
	callq	_RNvNtNtCs8xEFJqa6dYS_4core3str8converts9from_utf8
	nop
.Ltmp153:
	cmpl	$1, -32(%rbp)
	je	.LBB177_62
	movq	-24(%rbp), %rdx
	movq	-16(%rbp), %r8
.Ltmp154:
	leaq	-80(%rbp), %rcx
	callq	_RNvXs0_NvMs_NtNtCsfQUUnEvlYZE_5alloc3ffi5c_strNtBa_7CString3newReNtB5_11SpecNewImpl13spec_new_impl
	nop
.Ltmp155:
	cmpq	$-1, -80(%rbp)
	jne	.LBB177_65
	movq	-72(%rbp), %rax
	movq	%rax, -40(%rbp)
	movq	-64(%rbp), %rax
	movq	%rax, 16(%rbp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys12cuModuleLoad2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB177_70
.LBB177_71:
	leaq	-32(%rbp), %rcx
	movq	-40(%rbp), %r15
	movq	%r15, %rdx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys12cuModuleLoad2__S(%rip)
	movl	%eax, %edi
	testl	%eax, %eax
	setne	%r12b
	movq	%r15, %rcx
	je	.LBB177_72
	movb	$0, (%rcx)
	cmpq	$0, 16(%rbp)
	movq	8(%rbp), %r13
	jne	.LBB177_78
	testq	%r13, %r13
	je	.LBB177_82
	movq	-48(%rbp), %rcx
	callq	mi_free
	jmp	.LBB177_82
.LBB177_38:
	movq	8(%r8), %rax
	movq	%rax, 16(%rbp)
	movq	16(%r8), %rax
	movq	%rax, 8(%rbp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys16cuModuleLoadData2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB177_39
.LBB177_40:
	leaq	-32(%rbp), %rcx
	movq	8(%rbp), %rdx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys16cuModuleLoadData2__S(%rip)
	movl	%eax, %edi
	testl	%eax, %eax
	setne	%r12b
	movq	-32(%rbp), %r15
	cmpq	$0, 16(%rbp)
	je	.LBB177_41
	movq	8(%rbp), %rcx
	callq	mi_free
	testl	%edi, %edi
	jne	.LBB177_82
	xorl	%edx, %edx
	movb	$1, %r9b
	jmp	.LBB177_85
.LBB177_22:
	movq	8(%r8), %rdi
	movq	16(%r8), %r15
	movq	24(%r8), %r12
	cmpq	$15, %r12
	ja	.LBB177_30
	testq	%r12, %r12
	je	.LBB177_24
	xorl	%eax, %eax
	xorl	%edx, %edx
.LBB177_26:
	cmpb	$0, (%r15,%rdx)
	je	.LBB177_27
	incq	%rdx
	cmpq	%rdx, %r12
	jne	.LBB177_26
	movq	%r12, %rdx
	jmp	.LBB177_31
.LBB177_30:
	xorl	%ecx, %ecx
	movq	%r15, %rdx
	movq	%r12, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice6memchr14memchr_aligned
	jmp	.LBB177_31
.LBB177_41:
	movb	$1, %r8b
	xorl	%edx, %edx
	movb	$1, %r10b
	movb	$1, %r9b
	jmp	.LBB177_20
.LBB177_18:
	movb	$1, %r10b
	xorl	%r8d, %r8d
	movb	$1, %r9b
	jmp	.LBB177_19
.LBB177_72:
	movq	-32(%rbp), %r15
	movb	$0, (%rcx)
	cmpq	$0, 16(%rbp)
	movq	8(%rbp), %r13
	je	.LBB177_83
.LBB177_78:
	callq	mi_free
	testq	%r13, %r13
	je	.LBB177_79
	movq	-48(%rbp), %rcx
	callq	mi_free
	testl	%edi, %edi
	je	.LBB177_88
.LBB177_82:
	movl	%edi, 4(%rsi)
	movl	$1, (%rsi)
	jmp	.LBB177_100
.LBB177_79:
	movb	$1, %r8b
	xorl	%r9d, %r9d
	movb	$1, %r10b
.LBB177_19:
	movb	$1, %dl
	jmp	.LBB177_20
.LBB177_24:
	xorl	%edx, %edx
	xorl	%eax, %eax
	jmp	.LBB177_31
.LBB177_27:
	movl	$1, %eax
.LBB177_31:
	testb	$1, %al
	je	.LBB177_32
	cmpq	$-1, %rdi
	jne	.LBB177_52
	movq	%r12, -40(%rbp)
	movq	%r15, 16(%rbp)
	jmp	.LBB177_34
.LBB177_32:
	movq	%rdi, -32(%rbp)
	movq	%r15, -24(%rbp)
	movq	%r12, -16(%rbp)
	movb	$1, 31(%rbp)
	movb	$0, 30(%rbp)
	movb	$1, 29(%rbp)
	movb	$1, 28(%rbp)
.Ltmp162:
	leaq	-32(%rbp), %rcx
	callq	_RNvMs_NtNtCsfQUUnEvlYZE_5alloc3ffi5c_strNtB4_7CString19__from_vec_unchecked
	nop
.Ltmp163:
	movq	%rdx, -40(%rbp)
	movq	%rax, 16(%rbp)
.LBB177_34:
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys16cuModuleLoadData2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB177_35
.LBB177_36:
	leaq	-32(%rbp), %rcx
	movq	16(%rbp), %r15
	movq	%r15, %rdx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys16cuModuleLoadData2__S(%rip)
	movl	%eax, %edi
	testl	%eax, %eax
	setne	%r12b
	movq	-32(%rbp), %rax
	movq	%rax, 8(%rbp)
	movb	$0, (%r15)
	cmpq	$0, -40(%rbp)
	je	.LBB177_37
	movq	%r15, %rcx
	callq	mi_free
	xorl	%r10d, %r10d
	movb	$1, %dl
	movb	$1, %r9b
	movb	$1, %r8b
	testl	%edi, %edi
	movq	8(%rbp), %r15
	jne	.LBB177_21
	jmp	.LBB177_95
.LBB177_37:
	movb	$1, %r8b
	xorl	%r10d, %r10d
	movb	$1, %r9b
	movb	$1, %dl
	movq	8(%rbp), %r15
.LBB177_20:
	testb	%r12b, %r12b
	je	.LBB177_95
.LBB177_21:
	movl	%edi, 4(%rsi)
	movl	$1, (%rsi)
	leaq	.LJTI177_2(%rip), %rax
	movslq	(%rax,%r14,4), %rcx
	addq	%rax, %rcx
	jmpq	*%rcx
.LBB177_101:
	testb	%r8b, %r8b
	jmp	.LBB177_102
.LBB177_107:
	testb	%r9b, %r9b
	movq	(%rbp), %r8
	je	.LBB177_100
.LBB177_108:
	testq	%r13, %r13
	je	.LBB177_100
	movq	8(%r8), %rcx
	callq	mi_free
	jmp	.LBB177_100
.LBB177_106:
	testb	%dl, %dl
	jmp	.LBB177_102
.LBB177_105:
	testb	%r10b, %r10b
.LBB177_102:
	movq	(%rbp), %r8
	jne	.LBB177_103
	jmp	.LBB177_100
.LBB177_88:
	xorl	%r9d, %r9d
	movb	$1, %dl
	jmp	.LBB177_85
.LBB177_83:
	movb	$1, %dl
	testq	%r13, %r13
	je	.LBB177_84
	movq	-48(%rbp), %rcx
	callq	mi_free
	movb	$1, %dl
.LBB177_84:
	xorl	%r9d, %r9d
.LBB177_85:
	movb	$1, %r10b
	movb	$1, %r8b
.LBB177_95:
	movl	%r10d, -48(%rbp)
	movl	%r9d, -40(%rbp)
	movl	%r8d, 16(%rbp)
	movl	%edx, 8(%rbp)
	lock		incq	(%rbx)
	jle	.LBB177_53
	movq	$1, -32(%rbp)
	movq	$1, -24(%rbp)
	movq	%rbx, -16(%rbp)
	movq	%r15, -8(%rbp)
	movl	$32, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB177_97
	movups	-32(%rbp), %xmm0
	movups	-16(%rbp), %xmm1
	movups	%xmm1, 16(%rax)
	movups	%xmm0, (%rax)
	movq	%rax, 8(%rsi)
	movl	$0, (%rsi)
.LBB177_100:
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$168, %rsp
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
.LBB177_2:
	movb	$1, 31(%rbp)
	movb	$1, 30(%rbp)
	movb	$1, 29(%rbp)
	movb	$1, 28(%rbp)
.Ltmp146:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_15cuCtxGetCurrent0E0zEB14_.llvm.1750587498003715262
	nop
.Ltmp147:
	jmp	.LBB177_3
.LBB177_6:
	movb	$1, 31(%rbp)
	movb	$1, 30(%rbp)
	movb	$1, 29(%rbp)
	movb	$1, 28(%rbp)
.Ltmp148:
	movq	%rcx, %rdi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxSetCurrent0E0zEB13_.llvm.1750587498003715262
	movq	%rdi, %rcx
.Ltmp149:
	jmp	.LBB177_7
.LBB177_97:
.Ltmp170:
	movl	$8, %ecx
	movl	$32, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp171:
	jmp	.LBB177_53
.LBB177_39:
.Ltmp150:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_16cuModuleLoadData0E0zEB14_
	nop
.Ltmp151:
	jmp	.LBB177_40
.LBB177_16:
.Ltmp168:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_16cuModuleLoadData0E0zEB14_
	nop
.Ltmp169:
	jmp	.LBB177_17
.LBB177_52:
	movq	%rdi, -32(%rbp)
	movq	%r15, -24(%rbp)
	movq	%r12, -16(%rbp)
	movq	%rdx, -8(%rbp)
.Ltmp164:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.976(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.959.llvm.1750587498003715262(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.961.llvm.1750587498003715262(%rip), %r9
	leaq	-32(%rbp), %r8
	movl	$43, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core6result13unwrap_failed
	nop
.Ltmp165:
	jmp	.LBB177_53
.LBB177_62:
.Ltmp160:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.978(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	nop
.Ltmp161:
	jmp	.LBB177_53
.LBB177_35:
.Ltmp166:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_16cuModuleLoadData0E0zEB14_
	nop
.Ltmp167:
	jmp	.LBB177_36
.LBB177_65:
	movups	-80(%rbp), %xmm0
	movups	-64(%rbp), %xmm1
	movaps	%xmm1, -16(%rbp)
	movaps	%xmm0, -32(%rbp)
.Ltmp156:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.977(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.959.llvm.1750587498003715262(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.961.llvm.1750587498003715262(%rip), %r9
	leaq	-32(%rbp), %r8
	movl	$43, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core6result13unwrap_failed
	nop
.Ltmp157:
.LBB177_53:
	ud2
.LBB177_70:
.Ltmp158:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPaENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_12cuModuleLoad0E0zEB14_
	nop
.Ltmp159:
	jmp	.LBB177_71
	.seh_handlerdata
	.long	$cppxdata$_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@IMGREL
	.section	.text,"xr",one_only,_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module,unique,177
	.seh_endproc
	.def	"?dtor$9@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$9@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA":
.seh_proc "?dtor$9@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA"
.LBB177_9:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movq	(%rbp), %rax
	movq	(%rax), %rax
	movabsq	$-9223372036854775808, %rdx
	xorq	%rax, %rdx
	testq	%rax, %rax
	movl	$2, %ecx
	cmovsq	%rdx, %rcx
	testq	%rcx, %rcx
	je	.LBB177_110
	cmpq	$1, %rcx
	je	.LBB177_111
	cmpq	$2, %rcx
	jne	.LBB177_12
	testq	%rax, %rax
	je	.LBB177_115
	movl	$8, %eax
	testb	$1, 29(%rbp)
	jne	.LBB177_114
	jmp	.LBB177_115
.LBB177_111:
	cmpb	$1, 30(%rbp)
	je	.LBB177_13
	jmp	.LBB177_115
.LBB177_110:
	cmpb	$1, 31(%rbp)
	je	.LBB177_13
	jmp	.LBB177_115
.LBB177_12:
	cmpb	$1, 28(%rbp)
	jne	.LBB177_115
.LBB177_13:
	movl	$16, %eax
	movq	(%rbp), %rcx
	cmpq	$0, 8(%rcx)
	je	.LBB177_115
.LBB177_114:
	movq	(%rbp), %rcx
	movq	(%rcx,%rax), %rcx
	callq	mi_free
	nop
.LBB177_115:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module,unique,177
	.seh_endproc
	.def	"?dtor$42@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$42@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA":
.seh_proc "?dtor$42@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA"
.LBB177_42:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movq	8(%rbp), %rcx
	cmpq	$0, 16(%rbp)
	je	.LBB177_44
	callq	mi_free
.LBB177_44:
	movb	$0, 31(%rbp)
	movb	$1, 30(%rbp)
	movb	$1, 29(%rbp)
	movb	$1, 28(%rbp)
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module,unique,177
	.seh_endproc
	.def	"?dtor$49@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$49@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA":
.seh_proc "?dtor$49@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA"
.LBB177_49:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, -32(%rbp)
	je	.LBB177_51
	movq	-24(%rbp), %rcx
	callq	mi_free
.LBB177_51:
	movb	$1, 31(%rbp)
	movb	$0, 30(%rbp)
	movb	$1, 29(%rbp)
	movb	$1, 28(%rbp)
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module,unique,177
	.seh_endproc
	.def	"?dtor$54@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$54@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA":
.seh_proc "?dtor$54@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA"
.LBB177_54:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movq	16(%rbp), %rax
	movb	$0, (%rax)
	cmpq	$0, -40(%rbp)
	je	.LBB177_56
	movq	16(%rbp), %rcx
	callq	mi_free
.LBB177_56:
	movb	$1, 31(%rbp)
	movb	$0, 30(%rbp)
	movb	$1, 29(%rbp)
	movb	$1, 28(%rbp)
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module,unique,177
	.seh_endproc
	.def	"?dtor$57@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$57@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA":
.seh_proc "?dtor$57@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA"
.LBB177_57:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 8(%rbp)
	je	.LBB177_59
	movq	-48(%rbp), %rcx
	callq	mi_free
.LBB177_59:
	movb	$1, 31(%rbp)
	movb	$1, 30(%rbp)
	movb	$0, 29(%rbp)
	movb	$1, 28(%rbp)
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module,unique,177
	.seh_endproc
	.def	"?dtor$66@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$66@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA":
.seh_proc "?dtor$66@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA"
.LBB177_66:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, -32(%rbp)
	je	.LBB177_68
	movq	-24(%rbp), %rcx
	callq	mi_free
	nop
.LBB177_68:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module,unique,177
	.seh_endproc
	.def	"?dtor$74@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$74@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA":
.seh_proc "?dtor$74@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA"
.LBB177_74:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movq	-40(%rbp), %rax
	movb	$0, (%rax)
	cmpq	$0, 16(%rbp)
	je	.LBB177_76
	movq	%rax, %rcx
	callq	mi_free
	nop
.LBB177_76:
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module,unique,177
	.seh_endproc
	.def	"?dtor$89@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$89@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA":
.seh_proc "?dtor$89@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA"
.LBB177_89:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movq	8(%rbp), %rcx
	cmpq	$0, 16(%rbp)
	je	.LBB177_91
	callq	mi_free
.LBB177_91:
	movb	$1, 31(%rbp)
	movb	$1, 30(%rbp)
	movb	$1, 29(%rbp)
	movb	$0, 28(%rbp)
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
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module,unique,177
	.seh_endproc
	.def	"?dtor$98@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$98@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA":
.seh_proc "?dtor$98@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA"
.LBB177_98:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movl	16(%rbp), %edi
	movb	%dil, 31(%rbp)
	movl	-48(%rbp), %r14d
	movb	%r14b, 30(%rbp)
	movl	-40(%rbp), %ebx
	movb	%bl, 29(%rbp)
	movl	8(%rbp), %esi
	movb	%sil, 28(%rbp)
	leaq	-32(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaModuleEEB1m_
	movb	%dil, 31(%rbp)
	movb	%r14b, 30(%rbp)
	movb	%bl, 29(%rbp)
	movb	%sil, 28(%rbp)
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
.Lfunc_end177:
	.section	.rdata,"dr",associative,_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module,unique,178
	.p2align	2, 0x0
.LJTI177_0:
	.long	.LBB177_103-.LJTI177_0
	.long	.LBB177_103-.LJTI177_0
	.long	.LBB177_108-.LJTI177_0
	.long	.LBB177_103-.LJTI177_0
.LJTI177_1:
	.long	.LBB177_15-.LJTI177_1
	.long	.LBB177_22-.LJTI177_1
	.long	.LBB177_60-.LJTI177_1
	.long	.LBB177_38-.LJTI177_1
.LJTI177_2:
	.long	.LBB177_101-.LJTI177_2
	.long	.LBB177_105-.LJTI177_2
	.long	.LBB177_107-.LJTI177_2
	.long	.LBB177_106-.LJTI177_2
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module,unique,177
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module,unique,12
	.p2align	2, 0x0
$cppxdata$_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module:
	.long	429065506
	.long	9
	.long	$stateUnwindMap$_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@IMGREL
	.long	0
	.long	0
	.long	15
	.long	$ip2state$_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@IMGREL
	.long	160
	.long	0
	.long	1
$stateUnwindMap$_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module:
	.long	-1
	.long	"?dtor$9@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA"@IMGREL
	.long	0
	.long	"?dtor$98@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA"@IMGREL
	.long	0
	.long	"?dtor$89@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA"@IMGREL
	.long	0
	.long	"?dtor$57@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA"@IMGREL
	.long	3
	.long	"?dtor$74@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA"@IMGREL
	.long	3
	.long	"?dtor$66@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA"@IMGREL
	.long	0
	.long	"?dtor$54@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA"@IMGREL
	.long	0
	.long	"?dtor$49@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA"@IMGREL
	.long	0
	.long	"?dtor$42@?0?_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module@4HA"@IMGREL
$ip2state$_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module:
	.long	.Lfunc_begin177@IMGREL
	.long	-1
	.long	.Ltmp152@IMGREL
	.long	3
	.long	.Ltmp155@IMGREL
	.long	-1
	.long	.Ltmp162@IMGREL
	.long	0
	.long	.Ltmp163@IMGREL
	.long	-1
	.long	.Ltmp146@IMGREL
	.long	0
	.long	.Ltmp170@IMGREL
	.long	1
	.long	.Ltmp150@IMGREL
	.long	2
	.long	.Ltmp168@IMGREL
	.long	8
	.long	.Ltmp164@IMGREL
	.long	7
	.long	.Ltmp160@IMGREL
	.long	3
	.long	.Ltmp166@IMGREL
	.long	6
	.long	.Ltmp156@IMGREL
	.long	5
	.long	.Ltmp158@IMGREL
	.long	4
	.long	.Ltmp159@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvMs1p_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_11CudaContext11load_module,unique,177

	.def	_RNvMs1s_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModule13load_function;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs1s_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModule13load_function,unique,179
	.globl	_RNvMs1s_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModule13load_function
	.p2align	4
_RNvMs1s_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModule13load_function:
.Lfunc_begin178:
.seh_proc _RNvMs1s_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModule13load_function
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
	subq	$144, %rsp
	.seh_stackalloc 144
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	movq	$-2, 8(%rbp)
	movq	%rdx, %rdi
	movq	%rcx, %rsi
	leaq	-80(%rbp), %rcx
	movq	%r8, %rdx
	movq	%r9, %r8
	callq	_RNvXs0_NvMs_NtNtCsfQUUnEvlYZE_5alloc3ffi5c_strNtBa_7CString3newReNtB5_11SpecNewImpl13spec_new_impl
	cmpq	$-1, -80(%rbp)
	jne	.LBB178_1
	movq	-72(%rbp), %rax
	movq	%rax, -8(%rbp)
	movq	-64(%rbp), %rax
	movq	%rax, (%rbp)
	movq	(%rdi), %rbx
	movq	24(%rbx), %rdi
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys19cuModuleGetFunction2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB178_7
.LBB178_8:
	leaq	-48(%rbp), %rcx
	movq	%rdi, %rdx
	movq	-8(%rbp), %r14
	movq	%r14, %r8
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys19cuModuleGetFunction2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	je	.LBB178_9
	movl	%eax, %edi
	movb	$0, (%r14)
	cmpq	$0, (%rbp)
	je	.LBB178_18
	movq	%r14, %rcx
	callq	mi_free
.LBB178_18:
	movl	%edi, 8(%rsi)
	movq	$0, (%rsi)
	jmp	.LBB178_19
.LBB178_9:
	movq	-48(%rbp), %rdi
	movb	$0, (%r14)
	cmpq	$0, (%rbp)
	je	.LBB178_11
	movq	%r14, %rcx
	callq	mi_free
.LBB178_11:
	lock		incq	(%rbx)
	jle	.LBB178_2
	movq	%rbx, (%rsi)
	movq	%rdi, 8(%rsi)
.LBB178_19:
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$144, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.LBB178_1:
	movups	-80(%rbp), %xmm0
	movups	-64(%rbp), %xmm1
	movaps	%xmm1, -32(%rbp)
	movaps	%xmm0, -48(%rbp)
.Ltmp172:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.979.llvm.1750587498003715262(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.959.llvm.1750587498003715262(%rip), %rcx
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.961.llvm.1750587498003715262(%rip), %r9
	leaq	-48(%rbp), %r8
	movl	$43, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core6result13unwrap_failed
	nop
.Ltmp173:
.LBB178_2:
	ud2
.LBB178_7:
.Ltmp174:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stONtB10_8CUmod_stPaENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_19cuModuleGetFunction0E0zEB14_.llvm.1750587498003715262
	nop
.Ltmp175:
	jmp	.LBB178_8
	.seh_handlerdata
	.long	$cppxdata$_RNvMs1s_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModule13load_function@IMGREL
	.section	.text,"xr",one_only,_RNvMs1s_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModule13load_function,unique,179
	.seh_endproc
	.def	"?dtor$3@?0?_RNvMs1s_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModule13load_function@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$3@?0?_RNvMs1s_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModule13load_function@4HA":
.seh_proc "?dtor$3@?0?_RNvMs1s_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModule13load_function@4HA"
.LBB178_3:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, -48(%rbp)
	je	.LBB178_5
	movq	-40(%rbp), %rcx
	callq	mi_free
	nop
.LBB178_5:
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs1s_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModule13load_function,unique,179
	.seh_endproc
	.def	"?dtor$13@?0?_RNvMs1s_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModule13load_function@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$13@?0?_RNvMs1s_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModule13load_function@4HA":
.seh_proc "?dtor$13@?0?_RNvMs1s_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModule13load_function@4HA"
.LBB178_13:
	movq	%rdx, 16(%rsp)
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movq	-8(%rbp), %rax
	movb	$0, (%rax)
	cmpq	$0, (%rbp)
	je	.LBB178_15
	movq	%rax, %rcx
	callq	mi_free
	nop
.LBB178_15:
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end178:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs1s_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModule13load_function,unique,179
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvMs1s_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModule13load_function,unique,13
	.p2align	2, 0x0
$cppxdata$_RNvMs1s_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModule13load_function:
	.long	429065506
	.long	2
	.long	$stateUnwindMap$_RNvMs1s_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModule13load_function@IMGREL
	.long	0
	.long	0
	.long	4
	.long	$ip2state$_RNvMs1s_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModule13load_function@IMGREL
	.long	136
	.long	0
	.long	1
$stateUnwindMap$_RNvMs1s_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModule13load_function:
	.long	-1
	.long	"?dtor$3@?0?_RNvMs1s_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModule13load_function@4HA"@IMGREL
	.long	-1
	.long	"?dtor$13@?0?_RNvMs1s_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModule13load_function@4HA"@IMGREL
$ip2state$_RNvMs1s_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModule13load_function:
	.long	.Lfunc_begin178@IMGREL
	.long	-1
	.long	.Ltmp172@IMGREL
	.long	0
	.long	.Ltmp174@IMGREL
	.long	1
	.long	.Ltmp175@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvMs1s_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModule13load_function,unique,179

	.def	_RNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner10grow_exactCs5UjBoGikVie_6cudarc;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner10grow_exactCs5UjBoGikVie_6cudarc,unique,180
	.p2align	4
_RNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner10grow_exactCs5UjBoGikVie_6cudarc:
.Lfunc_begin179:
.seh_proc _RNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner10grow_exactCs5UjBoGikVie_6cudarc
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movq	%rdx, %rsi
	movq	%rcx, %rdi
	movq	(%rcx), %rdx
	movq	8(%rcx), %r8
	movq	$1, 40(%rsp)
	movq	$1, 32(%rsp)
	leaq	48(%rsp), %rcx
	movq	%rsi, %r9
	callq	_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCs5UjBoGikVie_6cudarc
	cmpb	$0, 48(%rsp)
	je	.LBB179_2
	movq	56(%rsp), %rax
	movq	64(%rsp), %rdx
	.seh_startepilogue
	addq	$72, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB179_2:
	movq	56(%rsp), %rax
	movq	%rax, 8(%rdi)
	movq	%rsi, (%rdi)
	movq	$-1, %rax
	.seh_startepilogue
	addq	$72, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end179:
	.seh_endproc

	.def	_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext14bind_to_thread;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext14bind_to_thread,unique,181
	.globl	_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext14bind_to_thread
	.p2align	4
_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext14bind_to_thread:
.Lfunc_begin180:
.seh_proc _RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext14bind_to_thread
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$48, %rsp
	.seh_stackalloc 48
	.seh_endprologue
	xorl	%eax, %eax
	xchgl	%eax, 28(%rcx)
	testl	%eax, %eax
	je	.LBB180_2
.LBB180_1:
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB180_2:
	movq	%rcx, %rsi
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB180_7
	leaq	40(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB180_1
.LBB180_4:
	movq	40(%rsp), %rax
	testq	%rax, %rax
	setne	%dl
	movq	(%rsi), %rcx
	cmpq	%rcx, %rax
	sete	%r8b
	movl	$-1, %eax
	testb	%r8b, %dl
	jne	.LBB180_1
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB180_8
.LBB180_6:
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	movl	%eax, %ecx
	xorl	%eax, %eax
	cmpl	$1, %ecx
	sbbl	%eax, %eax
	orl	%ecx, %eax
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB180_7:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_15cuCtxGetCurrent0E0zEB14_.llvm.1750587498003715262
	leaq	40(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB180_1
	jmp	.LBB180_4
.LBB180_8:
	movq	%rcx, %rsi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxSetCurrent0E0zEB13_.llvm.1750587498003715262
	movq	%rsi, %rcx
	jmp	.LBB180_6
.Lfunc_end180:
	.seh_endproc

	.def	_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext17is_event_tracking;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext17is_event_tracking,unique,182
	.globl	_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext17is_event_tracking
	.p2align	4
_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext17is_event_tracking:
.Lfunc_begin181:
	movzbl	32(%rcx), %eax
	testb	%al, %al
	setne	%al
	retq
.Lfunc_end181:

	.def	_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext18compute_capability;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext18compute_capability,unique,183
	.globl	_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext18compute_capability
	.p2align	4
_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext18compute_capability:
.Lfunc_begin182:
.seh_proc _RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext18compute_capability
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$48, %rsp
	.seh_stackalloc 48
	.seh_endprologue
	xorl	%eax, %eax
	xchgl	%eax, 28(%rdx)
	xorl	%r8d, %r8d
	movl	$1, %esi
	movl	$4, %edi
	testl	%eax, %eax
	jne	.LBB182_12
	xchgl	%r8d, 28(%rdx)
	testl	%r8d, %r8d
	je	.LBB182_3
	movl	%r8d, %eax
	jmp	.LBB182_12
.LBB182_3:
	movq	%rcx, %rbx
	movq	%rdx, %r14
	movl	24(%rdx), %r8d
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuDeviceGetAttribute2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB182_13
.LBB182_4:
	leaq	40(%rsp), %rcx
	movl	$75, %edx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuDeviceGetAttribute2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB182_5
	movl	40(%rsp), %ebp
	xorl	%eax, %eax
	xchgl	%eax, 28(%r14)
	testl	%eax, %eax
	jne	.LBB182_5
	movl	24(%r14), %r8d
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuDeviceGetAttribute2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB182_14
.LBB182_9:
	leaq	44(%rsp), %rcx
	movl	$76, %edx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuDeviceGetAttribute2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	je	.LBB182_11
.LBB182_5:
	movq	%rbx, %rcx
.LBB182_12:
	movl	%eax, (%rcx,%rdi)
	movl	%esi, (%rcx)
	movq	%rcx, %rax
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB182_11:
	movl	44(%rsp), %eax
	movq	%rbx, %rcx
	movl	%ebp, 4(%rbx)
	xorl	%esi, %esi
	movl	$8, %edi
	jmp	.LBB182_12
.LBB182_13:
	movl	%r8d, %ebp
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOlNtNtNtCs5UjBoGikVie_6cudarc6driver3sys23CUdevice_attribute_enumlENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_20cuDeviceGetAttribute0E0zEB14_.llvm.1750587498003715262
	movl	%ebp, %r8d
	jmp	.LBB182_4
.LBB182_14:
	movl	%r8d, %r14d
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOlNtNtNtCs5UjBoGikVie_6cudarc6driver3sys23CUdevice_attribute_enumlENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_20cuDeviceGetAttribute0E0zEB14_.llvm.1750587498003715262
	movl	%r14d, %r8d
	jmp	.LBB182_9
.Lfunc_end182:
	.seh_endproc

	.def	_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext22disable_event_tracking;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext22disable_event_tracking,unique,184
	.globl	_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext22disable_event_tracking
	.p2align	4
_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext22disable_event_tracking:
.Lfunc_begin183:
	movb	$0, 32(%rcx)
	retq
.Lfunc_end183:

	.def	_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext34is_managing_stream_synchronization;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext34is_managing_stream_synchronization,unique,185
	.globl	_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext34is_managing_stream_synchronization
	.p2align	4
_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext34is_managing_stream_synchronization:
.Lfunc_begin184:
	movq	16(%rcx), %rax
	testq	%rax, %rax
	je	.LBB184_1
	movzbl	32(%rcx), %eax
	testb	%al, %al
	setne	%al
	retq
.LBB184_1:
	xorl	%eax, %eax
	retq
.Lfunc_end184:

	.def	_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext3new;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext3new,unique,186
	.globl	_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext3new
	.p2align	4
_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext3new:
.Lfunc_begin185:
.seh_proc _RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext3new
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
	subq	$112, %rsp
	.seh_stackalloc 112
	leaq	112(%rsp), %rbp
	.seh_setframe %rbp, 112
	.seh_endprologue
	movq	$-2, -8(%rbp)
	movq	%rdx, %rdi
	movq	%rcx, %rsi
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys6cuInit2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB185_1
	xorl	%ecx, %ecx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys6cuInit2__S(%rip)
	testl	%eax, %eax
	jne	.LBB185_3
.LBB185_4:
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys11cuDeviceGet2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB185_5
.LBB185_6:
	leaq	-72(%rbp), %rcx
	movl	%edi, %edx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys11cuDeviceGet2__S(%rip)
	testl	%eax, %eax
	jne	.LBB185_3
	movl	-72(%rbp), %ebx
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys24cuDevicePrimaryCtxRetain2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB185_8
.LBB185_9:
	leaq	-72(%rbp), %rcx
	movl	%ebx, %edx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys24cuDevicePrimaryCtxRetain2__S(%rip)
	testl	%eax, %eax
	jne	.LBB185_3
	movq	-72(%rbp), %r14
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuDeviceGetAttribute2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB185_11
.LBB185_12:
	leaq	-72(%rbp), %rcx
	movl	$115, %edx
	movl	%ebx, %r8d
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuDeviceGetAttribute2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	je	.LBB185_13
.LBB185_3:
	movl	%eax, 4(%rsi)
	movl	$1, (%rsi)
.LBB185_32:
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$112, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.LBB185_13:
	cmpl	$0, -72(%rbp)
	movq	$1, -72(%rbp)
	movq	$1, -64(%rbp)
	movq	%r14, -56(%rbp)
	movq	%rdi, -48(%rbp)
	movq	$0, -40(%rbp)
	movl	%ebx, -32(%rbp)
	movl	$0, -28(%rbp)
	movb	$1, -24(%rbp)
	setg	-23(%rbp)
	movb	$1, -22(%rbp)
	movl	$56, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB185_14
	movq	%rax, %rdx
	movq	-24(%rbp), %rax
	movq	%rax, 48(%rdx)
	movups	-72(%rbp), %xmm0
	movups	-56(%rbp), %xmm1
	movups	-40(%rbp), %xmm2
	movups	%xmm2, 32(%rdx)
	movups	%xmm1, 16(%rdx)
	movups	%xmm0, (%rdx)
	movq	%rdx, -80(%rbp)
	xorl	%eax, %eax
	xchgl	%eax, 44(%rdx)
	testl	%eax, %eax
	jne	.LBB185_30
	movq	%rdx, -16(%rbp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB185_19
.LBB185_20:
	leaq	-72(%rbp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	je	.LBB185_21
	movq	-16(%rbp), %rdx
.LBB185_30:
	movl	%eax, 4(%rsi)
	movl	$1, (%rsi)
	lock		decq	(%rdx)
	jne	.LBB185_32
	#MEMBARRIER
	leaq	-80(%rbp), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_
	jmp	.LBB185_32
.LBB185_21:
	movq	-72(%rbp), %rax
	testq	%rax, %rax
	setne	%cl
	movq	-16(%rbp), %rdx
	movq	16(%rdx), %rdi
	cmpq	%rdi, %rax
	sete	%al
	testb	%al, %cl
	jne	.LBB185_25
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB185_23
.LBB185_24:
	movq	%rdi, %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	movq	-16(%rbp), %rdx
	jne	.LBB185_30
.LBB185_25:
	movq	%rdx, 8(%rsi)
	movl	$0, (%rsi)
	jmp	.LBB185_32
.LBB185_1:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_6cuInit0E0zEB14_
	xorl	%ecx, %ecx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys6cuInit2__S(%rip)
	testl	%eax, %eax
	jne	.LBB185_3
	jmp	.LBB185_4
.LBB185_5:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOllENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_11cuDeviceGet0E0zEB16_
	jmp	.LBB185_6
.LBB185_8:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stlENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_24cuDevicePrimaryCtxRetain0E0zEB14_
	jmp	.LBB185_9
.LBB185_11:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOlNtNtNtCs5UjBoGikVie_6cudarc6driver3sys23CUdevice_attribute_enumlENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_20cuDeviceGetAttribute0E0zEB14_.llvm.1750587498003715262
	jmp	.LBB185_12
.LBB185_14:
.Ltmp180:
	movl	$8, %ecx
	movl	$56, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp181:
	ud2
.LBB185_19:
.Ltmp176:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_15cuCtxGetCurrent0E0zEB14_.llvm.1750587498003715262
	nop
.Ltmp177:
	jmp	.LBB185_20
.LBB185_23:
.Ltmp178:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxSetCurrent0E0zEB13_.llvm.1750587498003715262
	nop
.Ltmp179:
	jmp	.LBB185_24
	.seh_handlerdata
	.long	$cppxdata$_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext3new@IMGREL
	.section	.text,"xr",one_only,_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext3new,unique,186
	.seh_endproc
	.def	"?dtor$16@?0?_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext3new@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$16@?0?_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext3new@4HA":
.seh_proc "?dtor$16@?0?_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext3new@4HA"
.LBB185_16:
	movq	%rdx, 16(%rsp)
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
	leaq	112(%rdx), %rbp
	.seh_endprologue
	leaq	-56(%rbp), %rcx
	callq	_RNvXs0_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContextNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop
	nop
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext3new,unique,186
	.seh_endproc
	.def	"?dtor$26@?0?_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext3new@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$26@?0?_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext3new@4HA":
.seh_proc "?dtor$26@?0?_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext3new@4HA"
.LBB185_26:
	movq	%rdx, 16(%rsp)
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
	leaq	112(%rdx), %rbp
	.seh_endprologue
	movq	-16(%rbp), %rax
	lock		decq	(%rax)
	jne	.LBB185_28
	#MEMBARRIER
	leaq	-80(%rbp), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_
	nop
.LBB185_28:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end185:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext3new,unique,186
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext3new,unique,14
	.p2align	2, 0x0
$cppxdata$_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext3new:
	.long	429065506
	.long	2
	.long	$stateUnwindMap$_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext3new@IMGREL
	.long	0
	.long	0
	.long	4
	.long	$ip2state$_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext3new@IMGREL
	.long	104
	.long	0
	.long	1
$stateUnwindMap$_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext3new:
	.long	-1
	.long	"?dtor$16@?0?_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext3new@4HA"@IMGREL
	.long	-1
	.long	"?dtor$26@?0?_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext3new@4HA"@IMGREL
$ip2state$_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext3new:
	.long	.Lfunc_begin185@IMGREL
	.long	-1
	.long	.Ltmp180@IMGREL
	.long	0
	.long	.Ltmp176@IMGREL
	.long	1
	.long	.Ltmp179@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvMs3_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext3new,unique,186

	.def	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtNtB7_6string6StringE8grow_oneCs5UjBoGikVie_6cudarc;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtNtB7_6string6StringE8grow_oneCs5UjBoGikVie_6cudarc,unique,187
	.globl	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtNtB7_6string6StringE8grow_oneCs5UjBoGikVie_6cudarc
	.p2align	4
_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtNtB7_6string6StringE8grow_oneCs5UjBoGikVie_6cudarc:
.Lfunc_begin186:
.seh_proc _RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecNtNtB7_6string6StringE8grow_oneCs5UjBoGikVie_6cudarc
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movq	%rcx, %rsi
	movq	(%rcx), %rdx
	leaq	(%rdx,%rdx), %rax
	cmpq	$5, %rax
	movl	$4, %edi
	cmovaeq	%rax, %rdi
	movq	8(%rcx), %r8
	movq	$24, 40(%rsp)
	movq	$8, 32(%rsp)
	leaq	48(%rsp), %rcx
	movq	%rdi, %r9
	callq	_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCs5UjBoGikVie_6cudarc
	cmpl	$1, 48(%rsp)
	je	.LBB186_1
	movq	56(%rsp), %rax
	movq	%rax, 8(%rsi)
	movq	%rdi, (%rsi)
	.seh_startepilogue
	addq	$72, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB186_1:
	movq	56(%rsp), %rcx
	movq	64(%rsp), %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.Lfunc_end186:
	.seh_endproc

	.def	_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCs5UjBoGikVie_6cudarc;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCs5UjBoGikVie_6cudarc,unique,188
	.p2align	4
_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCs5UjBoGikVie_6cudarc:
.Lfunc_begin187:
.seh_proc _RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCs5UjBoGikVie_6cudarc
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	%r9, %rax
	movq	%rdx, %r9
	movq	%rcx, %rsi
	movq	112(%rsp), %rbx
	mulq	120(%rsp)
	movq	%rax, %rdi
	seto	%al
	movabsq	$-9223372036854775808, %rcx
	subq	%rbx, %rcx
	cmpq	%rcx, %rdi
	seta	%cl
	orb	%al, %cl
	movl	$1, %r14d
	je	.LBB187_2
	movl	$8, %eax
	xorl	%edi, %edi
	jmp	.LBB187_10
.LBB187_2:
	testq	%r9, %r9
	je	.LBB187_4
	movq	%r8, %rcx
	movq	%rdi, %rdx
	movq	%rbx, %r8
	callq	mi_realloc_aligned
	testq	%rax, %rax
	jne	.LBB187_6
	jmp	.LBB187_9
.LBB187_4:
	testq	%rdi, %rdi
	je	.LBB187_5
	movq	%rdi, %rcx
	movq	%rbx, %rdx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	jne	.LBB187_6
.LBB187_9:
	movq	%rbx, 8(%rsi)
	movl	$16, %eax
	jmp	.LBB187_10
.LBB187_5:
	movq	%rbx, %rax
.LBB187_6:
	movq	%rax, 8(%rsi)
	movl	$16, %eax
	xorl	%r14d, %r14d
.LBB187_10:
	movq	%rdi, (%rsi,%rax)
	movq	%r14, (%rsi)
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.Lfunc_end187:
	.seh_endproc

	.def	_RNvMs7_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext9new_event;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs7_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext9new_event,unique,189
	.globl	_RNvMs7_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext9new_event
	.p2align	4
_RNvMs7_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext9new_event:
.Lfunc_begin188:
.seh_proc _RNvMs7_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext9new_event
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	%rcx, %rsi
	cmpl	$-1, %r8d
	movl	$2, %edi
	cmovnel	%r8d, %edi
	movq	(%rdx), %rbx
	xorl	%eax, %eax
	xchgl	%eax, 44(%rbx)
	testl	%eax, %eax
	jne	.LBB188_8
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB188_2
	leaq	32(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB188_8
.LBB188_4:
	movq	32(%rsp), %rax
	testq	%rax, %rax
	setne	%dl
	movq	16(%rbx), %rcx
	cmpq	%rcx, %rax
	sete	%al
	testb	%al, %dl
	jne	.LBB188_9
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB188_6
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB188_8
.LBB188_9:
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuEventCreate2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB188_10
.LBB188_11:
	leaq	32(%rsp), %rcx
	movl	%edi, %edx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuEventCreate2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	je	.LBB188_12
.LBB188_8:
	movl	%eax, 8(%rsi)
	movq	$0, (%rsi)
.LBB188_14:
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB188_12:
	movq	32(%rsp), %rax
	lock		incq	(%rbx)
	jle	.LBB188_15
	movq	%rbx, (%rsi)
	movq	%rax, 8(%rsi)
	jmp	.LBB188_14
.LBB188_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_15cuCtxGetCurrent0E0zEB14_.llvm.1750587498003715262
	leaq	32(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB188_8
	jmp	.LBB188_4
.LBB188_10:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stmENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_13cuEventCreate0E0zEB14_.llvm.1750587498003715262
	jmp	.LBB188_11
.LBB188_6:
	movq	%rcx, %r14
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxSetCurrent0E0zEB13_.llvm.1750587498003715262
	movq	%r14, %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB188_8
	jmp	.LBB188_9
.LBB188_15:
	ud2
.Lfunc_end188:
	.seh_endproc

	.def	_RNvMs8_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_9CudaEvent6record;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs8_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_9CudaEvent6record,unique,190
	.globl	_RNvMs8_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_9CudaEvent6record
	.p2align	4
_RNvMs8_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_9CudaEvent6record:
.Lfunc_begin189:
.seh_proc _RNvMs8_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_9CudaEvent6record
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$48, %rsp
	.seh_stackalloc 48
	.seh_endprologue
	movq	(%rcx), %rsi
	movq	(%rdx), %r8
	cmpq	%r8, %rsi
	je	.LBB189_4
	movl	40(%rsi), %r9d
	movl	$201, %eax
	cmpl	40(%r8), %r9d
	jne	.LBB189_15
	movq	16(%rsi), %r9
	cmpq	16(%r8), %r9
	jne	.LBB189_15
	movq	24(%rsi), %r9
	cmpq	24(%r8), %r9
	jne	.LBB189_15
.LBB189_4:
	xorl	%eax, %eax
	xchgl	%eax, 44(%rsi)
	testl	%eax, %eax
	jne	.LBB189_15
	movq	%rcx, %rdi
	movq	%rdx, %rbx
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB189_6
	leaq	40(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB189_15
.LBB189_8:
	movq	40(%rsp), %rax
	testq	%rax, %rax
	setne	%dl
	movq	16(%rsi), %rcx
	cmpq	%rcx, %rax
	sete	%al
	testb	%al, %dl
	movq	%rbx, %rdx
	movq	%rdi, %r8
	jne	.LBB189_12
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB189_10
.LBB189_11:
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	movq	%rbx, %rdx
	movq	%rdi, %r8
	jne	.LBB189_15
.LBB189_12:
	movq	8(%r8), %rcx
	movq	8(%rdx), %rdx
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuEventRecord2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB189_13
.LBB189_14:
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuEventRecord2__S.llvm.1750587498003715262(%rip)
	movl	%eax, %ecx
	xorl	%eax, %eax
	cmpl	$1, %ecx
	sbbl	%eax, %eax
	orl	%ecx, %eax
.LBB189_15:
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB189_6:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_15cuCtxGetCurrent0E0zEB14_.llvm.1750587498003715262
	leaq	40(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB189_15
	jmp	.LBB189_8
.LBB189_13:
	movq	%rcx, %rsi
	movq	%rdx, %rdi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stONtBZ_11CUstream_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_13cuEventRecord0E0zEB13_.llvm.1750587498003715262
	movq	%rdi, %rdx
	movq	%rsi, %rcx
	jmp	.LBB189_14
.LBB189_10:
	movq	%rcx, %rsi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxSetCurrent0E0zEB13_.llvm.1750587498003715262
	movq	%rsi, %rcx
	jmp	.LBB189_11
.Lfunc_end189:
	.seh_endproc

	.def	_RNvMs_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe5graphNtNtB6_4core10CudaStream11end_capture;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe5graphNtNtB6_4core10CudaStream11end_capture,unique,191
	.globl	_RNvMs_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe5graphNtNtB6_4core10CudaStream11end_capture
	.p2align	4
_RNvMs_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe5graphNtNtB6_4core10CudaStream11end_capture:
.Lfunc_begin190:
.seh_proc _RNvMs_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe5graphNtNtB6_4core10CudaStream11end_capture
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	%rcx, %rsi
	movq	(%rdx), %r14
	movq	16(%r14), %rbx
	xorl	%eax, %eax
	xchgl	%eax, 44(%rbx)
	testl	%eax, %eax
	jne	.LBB190_9
	movl	%r8d, %edi
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB190_2
	leaq	32(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB190_9
.LBB190_4:
	movq	32(%rsp), %rax
	movq	16(%rbx), %rcx
	testq	%rax, %rax
	je	.LBB190_6
	cmpq	%rcx, %rax
	je	.LBB190_10
.LBB190_6:
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB190_7
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB190_9
.LBB190_10:
	movq	24(%r14), %rcx
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuStreamEndCapture2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB190_11
	leaq	32(%rsp), %rdx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuStreamEndCapture2__S(%rip)
	testl	%eax, %eax
	je	.LBB190_13
.LBB190_9:
	movl	%eax, 4(%rsi)
	movl	$1, %eax
.LBB190_21:
	movl	%eax, (%rsi)
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB190_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_15cuCtxGetCurrent0E0zEB14_.llvm.1750587498003715262
	leaq	32(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB190_9
	jmp	.LBB190_4
.LBB190_11:
	movq	%rcx, %rbx
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stOONtBZ_10CUgraph_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_18cuStreamEndCapture0E0zEB13_
	movq	%rbx, %rcx
	leaq	32(%rsp), %rdx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuStreamEndCapture2__S(%rip)
	testl	%eax, %eax
	jne	.LBB190_9
.LBB190_13:
	movq	32(%rsp), %rbx
	testq	%rbx, %rbx
	je	.LBB190_14
	movl	%edi, %r8d
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys27cuGraphInstantiateWithFlags2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB190_16
.LBB190_17:
	leaq	32(%rsp), %rcx
	movq	%rbx, %rdx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys27cuGraphInstantiateWithFlags2__S(%rip)
	testl	%eax, %eax
	jne	.LBB190_9
	movq	32(%rsp), %rax
	lock		incq	(%r14)
	jle	.LBB190_22
	movq	%r14, 8(%rsi)
	movq	%rbx, 16(%rsi)
	movq	%rax, 24(%rsi)
	jmp	.LBB190_20
.LBB190_14:
	movq	$0, 8(%rsi)
.LBB190_20:
	xorl	%eax, %eax
	jmp	.LBB190_21
.LBB190_7:
	movq	%rcx, %rbx
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxSetCurrent0E0zEB13_.llvm.1750587498003715262
	movq	%rbx, %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB190_9
	jmp	.LBB190_10
.LBB190_16:
	movq	%r8, %rdi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB10_10CUgraph_styENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_27cuGraphInstantiateWithFlags0E0zEB14_
	movq	%rdi, %r8
	jmp	.LBB190_17
.LBB190_22:
	ud2
.Lfunc_end190:
	.seh_endproc

	.def	_RNvMs_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe5graphNtNtB6_4core10CudaStream13begin_capture;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe5graphNtNtB6_4core10CudaStream13begin_capture,unique,192
	.globl	_RNvMs_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe5graphNtNtB6_4core10CudaStream13begin_capture
	.p2align	4
_RNvMs_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe5graphNtNtB6_4core10CudaStream13begin_capture:
.Lfunc_begin191:
.seh_proc _RNvMs_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe5graphNtNtB6_4core10CudaStream13begin_capture
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$48, %rsp
	.seh_stackalloc 48
	.seh_endprologue
	movq	(%rcx), %rbx
	xorl	%eax, %eax
	xchgl	%eax, 44(%rbx)
	testl	%eax, %eax
	jne	.LBB191_11
	movq	%rcx, %rdi
	movl	%edx, %esi
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB191_2
	leaq	40(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB191_11
.LBB191_4:
	movq	40(%rsp), %rax
	testq	%rax, %rax
	setne	%dl
	movq	16(%rbx), %rcx
	cmpq	%rcx, %rax
	sete	%al
	testb	%al, %dl
	movl	%esi, %edx
	movq	%rdi, %r8
	jne	.LBB191_8
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB191_6
.LBB191_7:
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	movl	%esi, %edx
	movq	%rdi, %r8
	jne	.LBB191_11
.LBB191_8:
	movq	8(%r8), %rcx
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys23cuStreamBeginCapture_v22__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB191_9
.LBB191_10:
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys23cuStreamBeginCapture_v22__S.llvm.1750587498003715262(%rip)
	movl	%eax, %ecx
	xorl	%eax, %eax
	cmpl	$1, %ecx
	sbbl	%eax, %eax
	orl	%ecx, %eax
.LBB191_11:
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB191_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_15cuCtxGetCurrent0E0zEB14_.llvm.1750587498003715262
	leaq	40(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB191_11
	jmp	.LBB191_4
.LBB191_9:
	movq	%rcx, %rdi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stNtBZ_24CUstreamCaptureMode_enumENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_23cuStreamBeginCapture_v20E0zEB13_.llvm.1750587498003715262
	movq	%rdi, %rcx
	movl	%esi, %edx
	jmp	.LBB191_10
.LBB191_6:
	movq	%rcx, %rbx
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxSetCurrent0E0zEB13_.llvm.1750587498003715262
	movq	%rbx, %rcx
	jmp	.LBB191_7
.Lfunc_end191:
	.seh_endproc

	.def	_RNvMsc_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext10new_stream;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMsc_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext10new_stream,unique,193
	.globl	_RNvMsc_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext10new_stream
	.p2align	4
_RNvMsc_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext10new_stream:
.Lfunc_begin192:
.seh_proc _RNvMsc_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext10new_stream
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
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
	movq	$-2, (%rbp)
	movq	%rcx, %rsi
	movq	(%rdx), %rdi
	xorl	%eax, %eax
	xchgl	%eax, 44(%rdi)
	testl	%eax, %eax
	jne	.LBB192_8
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB192_2
	leaq	-32(%rbp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	je	.LBB192_4
.LBB192_8:
	movl	%eax, 4(%rsi)
	movl	$1, %ebx
.LBB192_32:
	movl	%ebx, (%rsi)
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$72, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB192_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_15cuCtxGetCurrent0E0zEB14_.llvm.1750587498003715262
	leaq	-32(%rbp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB192_8
.LBB192_4:
	movq	-32(%rbp), %rax
	testq	%rax, %rax
	setne	%dl
	movq	16(%rdi), %rcx
	cmpq	%rcx, %rax
	sete	%al
	testb	%al, %dl
	jne	.LBB192_9
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB192_6
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB192_8
.LBB192_9:
	movl	$1, %eax
	lock		xaddq	%rax, 32(%rdi)
	testq	%rax, %rax
	je	.LBB192_10
.LBB192_22:
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuStreamCreate2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB192_23
.LBB192_24:
	leaq	-32(%rbp), %rcx
	movl	$1, %ebx
	movl	$1, %edx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuStreamCreate2__S(%rip)
	testl	%eax, %eax
	je	.LBB192_26
	movl	%eax, 4(%rsi)
	jmp	.LBB192_32
.LBB192_10:
	movzbl	48(%rdi), %eax
	testb	%al, %al
	je	.LBB192_22
	xorl	%eax, %eax
	xchgl	%eax, 44(%rdi)
	testl	%eax, %eax
	jne	.LBB192_8
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB192_13
	leaq	-32(%rbp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB192_8
.LBB192_15:
	movq	-32(%rbp), %rax
	testq	%rax, %rax
	setne	%dl
	movq	16(%rdi), %rcx
	cmpq	%rcx, %rax
	sete	%al
	testb	%al, %dl
	jne	.LBB192_19
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB192_17
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB192_8
.LBB192_19:
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys16cuCtxSynchronize2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB192_20
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys16cuCtxSynchronize2__S(%rip)
	testl	%eax, %eax
	jne	.LBB192_8
	jmp	.LBB192_22
.LBB192_26:
	movq	-32(%rbp), %rax
	lock		incq	(%rdi)
	jle	.LBB192_29
	movq	$1, -32(%rbp)
	movq	$1, -24(%rbp)
	movq	%rdi, -16(%rbp)
	movq	%rax, -8(%rbp)
	movl	$32, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB192_28
	movups	-32(%rbp), %xmm0
	movups	-16(%rbp), %xmm1
	movups	%xmm1, 16(%rax)
	movups	%xmm0, (%rax)
	movq	%rax, 8(%rsi)
	xorl	%ebx, %ebx
	jmp	.LBB192_32
.LBB192_23:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stmENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_14cuStreamCreate0E0zEB14_
	jmp	.LBB192_24
.LBB192_6:
	movq	%rcx, %rbx
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxSetCurrent0E0zEB13_.llvm.1750587498003715262
	movq	%rbx, %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB192_8
	jmp	.LBB192_9
.LBB192_28:
.Ltmp182:
	movl	$8, %ecx
	movl	$32, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp183:
.LBB192_29:
	ud2
.LBB192_13:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_15cuCtxGetCurrent0E0zEB14_.llvm.1750587498003715262
	leaq	-32(%rbp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB192_8
	jmp	.LBB192_15
.LBB192_20:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_16cuCtxSynchronize0E0zEB13_
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys16cuCtxSynchronize2__S(%rip)
	testl	%eax, %eax
	jne	.LBB192_8
	jmp	.LBB192_22
.LBB192_17:
	movq	%rcx, %rbx
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxSetCurrent0E0zEB13_.llvm.1750587498003715262
	movq	%rbx, %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB192_8
	jmp	.LBB192_19
	.seh_handlerdata
	.long	$cppxdata$_RNvMsc_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext10new_stream@IMGREL
	.section	.text,"xr",one_only,_RNvMsc_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext10new_stream,unique,193
	.seh_endproc
	.def	"?dtor$30@?0?_RNvMsc_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext10new_stream@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$30@?0?_RNvMsc_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext10new_stream@4HA":
.seh_proc "?dtor$30@?0?_RNvMsc_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext10new_stream@4HA"
.LBB192_30:
	movq	%rdx, 16(%rsp)
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
	leaq	64(%rdx), %rbp
	.seh_endprologue
	leaq	-32(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamEEB1m_
	nop
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end192:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMsc_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext10new_stream,unique,193
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvMsc_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext10new_stream,unique,15
	.p2align	2, 0x0
$cppxdata$_RNvMsc_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext10new_stream:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNvMsc_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext10new_stream@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RNvMsc_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext10new_stream@IMGREL
	.long	64
	.long	0
	.long	1
$stateUnwindMap$_RNvMsc_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext10new_stream:
	.long	-1
	.long	"?dtor$30@?0?_RNvMsc_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext10new_stream@4HA"@IMGREL
$ip2state$_RNvMsc_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext10new_stream:
	.long	.Lfunc_begin192@IMGREL
	.long	-1
	.long	.Ltmp182@IMGREL
	.long	0
	.long	.Ltmp183@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvMsc_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext10new_stream,unique,193

	.def	_RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream11synchronize;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream11synchronize,unique,194
	.globl	_RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream11synchronize
	.p2align	4
_RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream11synchronize:
.Lfunc_begin193:
.seh_proc _RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream11synchronize
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rdi
	xorl	%eax, %eax
	xchgl	%eax, 44(%rdi)
	testl	%eax, %eax
	je	.LBB193_2
.LBB193_1:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB193_2:
	movq	%rcx, %rsi
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB193_9
	leaq	32(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB193_1
.LBB193_4:
	movq	32(%rsp), %rax
	testq	%rax, %rax
	setne	%dl
	movq	16(%rdi), %rcx
	cmpq	%rcx, %rax
	sete	%al
	testb	%al, %dl
	movq	%rsi, %rdx
	jne	.LBB193_7
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB193_11
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	movq	%rsi, %rdx
	jne	.LBB193_1
.LBB193_7:
	movq	8(%rdx), %rcx
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys19cuStreamSynchronize2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB193_10
.LBB193_8:
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys19cuStreamSynchronize2__S.llvm.1750587498003715262(%rip)
	movl	%eax, %ecx
	xorl	%eax, %eax
	cmpl	$1, %ecx
	sbbl	%eax, %eax
	orl	%ecx, %eax
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB193_9:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_15cuCtxGetCurrent0E0zEB14_.llvm.1750587498003715262
	leaq	32(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB193_1
	jmp	.LBB193_4
.LBB193_10:
	movq	%rcx, %rsi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_19cuStreamSynchronize0E0zEB13_.llvm.1750587498003715262
	movq	%rsi, %rcx
	jmp	.LBB193_8
.LBB193_11:
	movq	%rcx, %rdi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxSetCurrent0E0zEB13_.llvm.1750587498003715262
	movq	%rdi, %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	movq	%rsi, %rdx
	jne	.LBB193_1
	jmp	.LBB193_7
.Lfunc_end193:
	.seh_endproc

	.def	_RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream12record_event;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream12record_event,unique,195
	.globl	_RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream12record_event
	.p2align	4
_RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream12record_event:
.Lfunc_begin194:
.seh_proc _RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream12record_event
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
	subq	$64, %rsp
	.seh_stackalloc 64
	leaq	64(%rsp), %rbp
	.seh_setframe %rbp, 64
	.seh_endprologue
	movq	$-2, -8(%rbp)
	movq	%rdx, %rdi
	movq	%rcx, %rsi
	leaq	-24(%rbp), %rcx
	callq	_RNvMs7_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContext9new_event
	movq	-24(%rbp), %rbx
	testq	%rbx, %rbx
	je	.LBB194_1
	movq	-16(%rbp), %r14
	movq	%rbx, -24(%rbp)
	movq	%r14, -16(%rbp)
.Ltmp184:
	leaq	-24(%rbp), %rcx
	movq	%rdi, %rdx
	callq	_RNvMs8_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_9CudaEvent6record
	nop
.Ltmp185:
	cmpl	$-1, %eax
	je	.LBB194_6
	movl	%eax, 8(%rsi)
	movq	$0, (%rsi)
	leaq	-24(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core9CudaEventEBJ_.llvm.1750587498003715262
	jmp	.LBB194_7
.LBB194_1:
	movl	-16(%rbp), %eax
	movl	%eax, 8(%rsi)
	movq	$0, (%rsi)
	jmp	.LBB194_7
.LBB194_6:
	movq	%rbx, (%rsi)
	movq	%r14, 8(%rsi)
.LBB194_7:
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.long	$cppxdata$_RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream12record_event@IMGREL
	.section	.text,"xr",one_only,_RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream12record_event,unique,195
	.seh_endproc
	.def	"?dtor$2@?0?_RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream12record_event@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$2@?0?_RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream12record_event@4HA":
.seh_proc "?dtor$2@?0?_RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream12record_event@4HA"
.LBB194_2:
	movq	%rdx, 16(%rsp)
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
	leaq	64(%rdx), %rbp
	.seh_endprologue
	leaq	-24(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core9CudaEventEBJ_.llvm.1750587498003715262
	nop
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end194:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream12record_event,unique,195
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream12record_event,unique,16
	.p2align	2, 0x0
$cppxdata$_RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream12record_event:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream12record_event@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream12record_event@IMGREL
	.long	56
	.long	0
	.long	1
$stateUnwindMap$_RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream12record_event:
	.long	-1
	.long	"?dtor$2@?0?_RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream12record_event@4HA"@IMGREL
$ip2state$_RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream12record_event:
	.long	.Lfunc_begin194@IMGREL
	.long	-1
	.long	.Ltmp184@IMGREL
	.long	0
	.long	.Ltmp185@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream12record_event,unique,195

	.def	_RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream4wait;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream4wait,unique,196
	.globl	_RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream4wait
	.p2align	4
_RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream4wait:
.Lfunc_begin195:
.seh_proc _RNvMsd_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStream4wait
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$48, %rsp
	.seh_stackalloc 48
	.seh_endprologue
	movq	(%rcx), %rbx
	xorl	%eax, %eax
	xchgl	%eax, 44(%rbx)
	testl	%eax, %eax
	jne	.LBB195_11
	movq	%rcx, %rsi
	movq	%rdx, %rdi
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB195_2
	leaq	40(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB195_11
.LBB195_4:
	movq	40(%rsp), %rax
	testq	%rax, %rax
	setne	%dl
	movq	16(%rbx), %rcx
	cmpq	%rcx, %rax
	sete	%al
	testb	%al, %dl
	movq	%rdi, %rdx
	movq	%rsi, %r8
	jne	.LBB195_8
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB195_6
.LBB195_7:
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	movq	%rdi, %rdx
	movq	%rsi, %r8
	jne	.LBB195_11
.LBB195_8:
	movq	8(%r8), %rcx
	movq	8(%rdx), %rdx
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuStreamWaitEvent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB195_9
.LBB195_10:
	xorl	%r8d, %r8d
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuStreamWaitEvent2__S.llvm.1750587498003715262(%rip)
	movl	%eax, %ecx
	xorl	%eax, %eax
	cmpl	$1, %ecx
	sbbl	%eax, %eax
	orl	%ecx, %eax
.LBB195_11:
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB195_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_15cuCtxGetCurrent0E0zEB14_.llvm.1750587498003715262
	leaq	40(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB195_11
	jmp	.LBB195_4
.LBB195_9:
	movq	%rcx, %rsi
	movq	%rdx, %rdi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stONtBZ_10CUevent_stmENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_17cuStreamWaitEvent0E0zEB13_.llvm.1750587498003715262
	movq	%rdi, %rdx
	movq	%rsi, %rcx
	jmp	.LBB195_10
.LBB195_6:
	movq	%rcx, %rbx
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxSetCurrent0E0zEB13_.llvm.1750587498003715262
	movq	%rbx, %rcx
	jmp	.LBB195_7
.Lfunc_end195:
	.seh_endproc

	.def	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamE9drop_slowBO_;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamE9drop_slowBO_,unique,197
	.globl	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamE9drop_slowBO_
	.p2align	4
_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamE9drop_slowBO_:
.Lfunc_begin196:
.seh_proc _RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamE9drop_slowBO_
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$64, %rsp
	.seh_stackalloc 64
	leaq	64(%rsp), %rbp
	.seh_setframe %rbp, 64
	.seh_endprologue
	movq	$-2, -8(%rbp)
	movq	(%rcx), %rax
	movq	%rax, -16(%rbp)
	leaq	16(%rax), %rcx
.Ltmp186:
	movq	%rcx, -24(%rbp)
	callq	_RNvXsb_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStreamNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop
	nop
.Ltmp187:
	movq	-24(%rbp), %rcx
	movq	(%rcx), %rax
	lock		decq	(%rax)
	jne	.LBB196_3
	#MEMBARRIER
.Ltmp188:
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_
	nop
.Ltmp189:
.LBB196_3:
	movq	-16(%rbp), %rcx
	cmpq	$-1, %rcx
	je	.LBB196_13
	lock		decq	8(%rcx)
	jne	.LBB196_13
	#MEMBARRIER
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbp
	.seh_endepilogue
	jmp	mi_free
.LBB196_13:
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.long	$cppxdata$_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamE9drop_slowBO_@IMGREL
	.section	.text,"xr",one_only,_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamE9drop_slowBO_,unique,197
	.seh_endproc
	.def	"?dtor$6@?0?_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamE9drop_slowBO_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$6@?0?_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamE9drop_slowBO_@4HA":
.seh_proc "?dtor$6@?0?_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamE9drop_slowBO_@4HA"
.LBB196_6:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	64(%rdx), %rbp
	.seh_endprologue
	movq	-24(%rbp), %rax
	movq	(%rax), %rax
	lock		decq	(%rax)
	jne	.LBB196_8
	#MEMBARRIER
	movq	-24(%rbp), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_
	nop
.LBB196_8:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamE9drop_slowBO_,unique,197
	.seh_endproc
	.def	"?dtor$9@?0?_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamE9drop_slowBO_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$9@?0?_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamE9drop_slowBO_@4HA":
.seh_proc "?dtor$9@?0?_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamE9drop_slowBO_@4HA"
.LBB196_9:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	64(%rdx), %rbp
	.seh_endprologue
	cmpq	$-1, -16(%rbp)
	je	.LBB196_12
	movq	-16(%rbp), %rax
	lock		decq	8(%rax)
	jne	.LBB196_12
	#MEMBARRIER
	movq	-16(%rbp), %rcx
	callq	mi_free
	nop
.LBB196_12:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end196:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamE9drop_slowBO_,unique,197
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamE9drop_slowBO_,unique,17
	.p2align	2, 0x0
$cppxdata$_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamE9drop_slowBO_:
	.long	429065506
	.long	2
	.long	$stateUnwindMap$_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamE9drop_slowBO_@IMGREL
	.long	0
	.long	0
	.long	4
	.long	$ip2state$_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamE9drop_slowBO_@IMGREL
	.long	56
	.long	0
	.long	1
$stateUnwindMap$_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamE9drop_slowBO_:
	.long	-1
	.long	"?dtor$9@?0?_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamE9drop_slowBO_@4HA"@IMGREL
	.long	0
	.long	"?dtor$6@?0?_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamE9drop_slowBO_@4HA"@IMGREL
$ip2state$_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamE9drop_slowBO_:
	.long	.Lfunc_begin196@IMGREL
	.long	-1
	.long	.Ltmp186@IMGREL
	.long	1
	.long	.Ltmp188@IMGREL
	.long	0
	.long	.Ltmp189@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core10CudaStreamE9drop_slowBO_,unique,197

	.def	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_,unique,198
	.globl	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_
	.p2align	4
_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_:
.Lfunc_begin197:
.seh_proc _RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$48, %rsp
	.seh_stackalloc 48
	leaq	48(%rsp), %rbp
	.seh_setframe %rbp, 48
	.seh_endprologue
	movq	$-2, -8(%rbp)
	movq	(%rcx), %rax
	movq	%rax, -16(%rbp)
	leaq	16(%rax), %rcx
.Ltmp190:
	callq	_RNvXs0_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContextNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop
	nop
.Ltmp191:
	movq	-16(%rbp), %rcx
	cmpq	$-1, %rcx
	je	.LBB197_8
	lock		decq	8(%rcx)
	jne	.LBB197_8
	#MEMBARRIER
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbp
	.seh_endepilogue
	jmp	mi_free
.LBB197_8:
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.long	$cppxdata$_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_@IMGREL
	.section	.text,"xr",one_only,_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_,unique,198
	.seh_endproc
	.def	"?dtor$4@?0?_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$4@?0?_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_@4HA":
.seh_proc "?dtor$4@?0?_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_@4HA"
.LBB197_4:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	48(%rdx), %rbp
	.seh_endprologue
	cmpq	$-1, -16(%rbp)
	je	.LBB197_7
	movq	-16(%rbp), %rax
	lock		decq	8(%rax)
	jne	.LBB197_7
	#MEMBARRIER
	movq	-16(%rbp), %rcx
	callq	mi_free
	nop
.LBB197_7:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end197:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_,unique,198
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_,unique,18
	.p2align	2, 0x0
$cppxdata$_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_@IMGREL
	.long	40
	.long	0
	.long	1
$stateUnwindMap$_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_:
	.long	-1
	.long	"?dtor$4@?0?_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_@4HA"@IMGREL
$ip2state$_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_:
	.long	.Lfunc_begin197@IMGREL
	.long	-1
	.long	.Ltmp190@IMGREL
	.long	0
	.long	.Ltmp191@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtNtCs5UjBoGikVie_6cudarc6driver4safe4core11CudaContextE9drop_slowBO_,unique,198

	.def	_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result14create_program;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result14create_program,unique,199
	.globl	_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result14create_program
	.p2align	4
_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result14create_program:
.Lfunc_begin198:
.seh_proc _RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result14create_program
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$64, %rsp
	.seh_stackalloc 64
	.seh_endprologue
	movq	%r9, %r8
	movq	%rcx, %rsi
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys18nvrtcCreateProgram2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB198_1
.LBB198_2:
	xorps	%xmm0, %xmm0
	movups	%xmm0, 32(%rsp)
	leaq	56(%rsp), %rcx
	xorl	%edi, %edi
	xorl	%r9d, %r9d
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys18nvrtcCreateProgram2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	je	.LBB198_3
	movl	%eax, 4(%rsi)
	movl	$1, %edi
	jmp	.LBB198_5
.LBB198_3:
	movq	56(%rsp), %rax
	movq	%rax, 8(%rsi)
.LBB198_5:
	movl	%edi, (%rsi)
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB198_1:
	movq	%r8, %rdi
	movq	%rdx, %rbx
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramPaB1P_lPB1P_B1W_ENtB10_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvB10_18nvrtcCreateProgram0E0zEB14_.llvm.1750587498003715262
	movq	%rbx, %rdx
	movq	%rdi, %r8
	jmp	.LBB198_2
.Lfunc_end198:
	.seh_endproc

	.def	_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result15get_program_log;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result15get_program_log,unique,200
	.globl	_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result15get_program_log
	.p2align	4
_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result15get_program_log:
.Lfunc_begin199:
.seh_proc _RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result15get_program_log
	.seh_handler __CxxFrameHandler3, @unwind, @except
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
	subq	$80, %rsp
	.seh_stackalloc 80
	leaq	80(%rsp), %rbp
	.seh_setframe %rbp, 80
	.seh_endprologue
	movq	$-2, -8(%rbp)
	movq	%rdx, %rdi
	movq	%rcx, %rsi
	movq	$0, -40(%rbp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys22nvrtcGetProgramLogSize2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB199_23
.LBB199_1:
	leaq	-40(%rbp), %rdx
	movq	%rdi, %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys22nvrtcGetProgramLogSize2__S(%rip)
	testl	%eax, %eax
	je	.LBB199_4
	movl	%eax, 8(%rsi)
	movq	$-1, (%rsi)
.LBB199_3:
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
.LBB199_4:
	movq	-40(%rbp), %r15
	testq	%r15, %r15
	jns	.LBB199_7
	xorl	%r14d, %r14d
.LBB199_6:
	movq	%r14, %rcx
	movq	%r15, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.LBB199_7:
	je	.LBB199_13
	movl	$1, %r14d
	movl	$1, %edx
	movq	%r15, %rcx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB199_6
	movq	%rax, %rbx
	movq	-40(%rbp), %r14
	movq	%r15, -32(%rbp)
	movq	%rax, -24(%rbp)
	movq	$0, -16(%rbp)
	testq	%r14, %r14
	je	.LBB199_14
	cmpq	%r15, %r14
	ja	.LBB199_25
	movl	$1, %r15d
	cmpq	$1, %r14
	jne	.LBB199_15
	movq	%rbx, %rax
	jmp	.LBB199_17
.LBB199_13:
	movq	$0, -32(%rbp)
	movq	$1, -24(%rbp)
	movq	$0, -16(%rbp)
	movl	$1, %ebx
.LBB199_14:
	xorl	%r15d, %r15d
	movq	%r15, -16(%rbp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys18nvrtcGetProgramLog2__S+8(%rip), %eax
	testl	%eax, %eax
	je	.LBB199_19
	jmp	.LBB199_24
.LBB199_15:
	xorl	%r15d, %r15d
	movq	%rbx, %r12
.LBB199_16:
	leaq	-1(%r14), %r8
	movq	%rbx, %rcx
	xorl	%edx, %edx
	callq	memset
	leaq	(%r12,%r15), %rax
	addq	%r14, %rax
	decq	%rax
	addq	%r14, %r15
	movq	%r12, %rbx
.LBB199_17:
	movb	$0, (%rax)
	movq	%r15, -16(%rbp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys18nvrtcGetProgramLog2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB199_24
.LBB199_19:
	movq	%rdi, %rcx
	movq	%rbx, %rdx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys18nvrtcGetProgramLog2__S(%rip)
	testl	%eax, %eax
	je	.LBB199_22
	movl	%eax, 8(%rsi)
	movq	$-1, (%rsi)
	cmpq	$0, -32(%rbp)
	je	.LBB199_3
	movq	-24(%rbp), %rcx
	callq	mi_free
	jmp	.LBB199_3
.LBB199_22:
	movq	-16(%rbp), %rax
	movq	%rax, 16(%rsi)
	movups	-32(%rbp), %xmm0
	movups	%xmm0, (%rsi)
	jmp	.LBB199_3
.LBB199_23:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtBZ_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvBZ_22nvrtcGetProgramLogSize0E0zEB13_
	jmp	.LBB199_1
.LBB199_24:
.Ltmp194:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtBZ_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvBZ_18nvrtcGetProgramLog0E0zEB13_
	nop
.Ltmp195:
	jmp	.LBB199_19
.LBB199_25:
.Ltmp192:
	movq	$1, 32(%rsp)
	leaq	-32(%rbp), %rcx
	movl	$1, %r9d
	xorl	%edx, %edx
	movq	%r14, %r8
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECs5UjBoGikVie_6cudarc
	nop
.Ltmp193:
	movq	-24(%rbp), %r12
	movq	-16(%rbp), %r15
	leaq	(%r12,%r15), %rbx
	jmp	.LBB199_16
	.seh_handlerdata
	.long	$cppxdata$_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result15get_program_log@IMGREL
	.section	.text,"xr",one_only,_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result15get_program_log,unique,200
	.seh_endproc
	.def	"?dtor$27@?0?_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result15get_program_log@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$27@?0?_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result15get_program_log@4HA":
.seh_proc "?dtor$27@?0?_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result15get_program_log@4HA"
.LBB199_27:
	movq	%rdx, 16(%rsp)
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
	leaq	80(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, -32(%rbp)
	je	.LBB199_29
	movq	-24(%rbp), %rcx
	callq	mi_free
	nop
.LBB199_29:
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
.Lfunc_end199:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result15get_program_log,unique,200
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result15get_program_log,unique,19
	.p2align	2, 0x0
$cppxdata$_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result15get_program_log:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result15get_program_log@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result15get_program_log@IMGREL
	.long	72
	.long	0
	.long	1
$stateUnwindMap$_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result15get_program_log:
	.long	-1
	.long	"?dtor$27@?0?_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result15get_program_log@4HA"@IMGREL
$ip2state$_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result15get_program_log:
	.long	.Lfunc_begin199@IMGREL
	.long	-1
	.long	.Ltmp194@IMGREL
	.long	0
	.long	.Ltmp193@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result15get_program_log,unique,200

	.def	_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result7get_ptx;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result7get_ptx,unique,201
	.globl	_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result7get_ptx
	.p2align	4
_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result7get_ptx:
.Lfunc_begin200:
.seh_proc _RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result7get_ptx
	.seh_handler __CxxFrameHandler3, @unwind, @except
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
	subq	$80, %rsp
	.seh_stackalloc 80
	leaq	80(%rsp), %rbp
	.seh_setframe %rbp, 80
	.seh_endprologue
	movq	$-2, -8(%rbp)
	movq	%rdx, %rdi
	movq	%rcx, %rsi
	movq	$0, -40(%rbp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys15nvrtcGetPTXSize2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB200_23
.LBB200_1:
	leaq	-40(%rbp), %rdx
	movq	%rdi, %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys15nvrtcGetPTXSize2__S(%rip)
	testl	%eax, %eax
	je	.LBB200_4
	movl	%eax, 8(%rsi)
	movq	$-1, (%rsi)
.LBB200_3:
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$80, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
.LBB200_4:
	movq	-40(%rbp), %r15
	testq	%r15, %r15
	jns	.LBB200_7
	xorl	%r14d, %r14d
.LBB200_6:
	movq	%r14, %rcx
	movq	%r15, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.LBB200_7:
	je	.LBB200_13
	movl	$1, %r14d
	movl	$1, %edx
	movq	%r15, %rcx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB200_6
	movq	%rax, %rbx
	movq	-40(%rbp), %r14
	movq	%r15, -32(%rbp)
	movq	%rax, -24(%rbp)
	movq	$0, -16(%rbp)
	testq	%r14, %r14
	je	.LBB200_14
	cmpq	%r15, %r14
	ja	.LBB200_25
	movl	$1, %r15d
	cmpq	$1, %r14
	jne	.LBB200_15
	movq	%rbx, %rax
	jmp	.LBB200_17
.LBB200_13:
	movq	$0, -32(%rbp)
	movq	$1, -24(%rbp)
	movq	$0, -16(%rbp)
	movl	$1, %ebx
.LBB200_14:
	xorl	%r15d, %r15d
	movq	%r15, -16(%rbp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys11nvrtcGetPTX2__S+8(%rip), %eax
	testl	%eax, %eax
	je	.LBB200_19
	jmp	.LBB200_24
.LBB200_15:
	xorl	%r15d, %r15d
	movq	%rbx, %r12
.LBB200_16:
	leaq	-1(%r14), %r8
	movq	%rbx, %rcx
	xorl	%edx, %edx
	callq	memset
	leaq	(%r12,%r15), %rax
	addq	%r14, %rax
	decq	%rax
	addq	%r14, %r15
	movq	%r12, %rbx
.LBB200_17:
	movb	$0, (%rax)
	movq	%r15, -16(%rbp)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys11nvrtcGetPTX2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB200_24
.LBB200_19:
	movq	%rdi, %rcx
	movq	%rbx, %rdx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys11nvrtcGetPTX2__S(%rip)
	testl	%eax, %eax
	je	.LBB200_22
	movl	%eax, 8(%rsi)
	movq	$-1, (%rsi)
	cmpq	$0, -32(%rbp)
	je	.LBB200_3
	movq	-24(%rbp), %rcx
	callq	mi_free
	jmp	.LBB200_3
.LBB200_22:
	movq	-16(%rbp), %rax
	movq	%rax, 16(%rsi)
	movups	-32(%rbp), %xmm0
	movups	%xmm0, (%rsi)
	jmp	.LBB200_3
.LBB200_23:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtBZ_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvBZ_15nvrtcGetPTXSize0E0zEB13_
	jmp	.LBB200_1
.LBB200_24:
.Ltmp198:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtBZ_11nvrtcResultE10initializeNCINvB2_11get_or_initNCNvBZ_11nvrtcGetPTX0E0zEB13_
	nop
.Ltmp199:
	jmp	.LBB200_19
.LBB200_25:
.Ltmp196:
	movq	$1, 32(%rsp)
	leaq	-32(%rbp), %rcx
	movl	$1, %r9d
	xorl	%edx, %edx
	movq	%r14, %r8
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECs5UjBoGikVie_6cudarc
	nop
.Ltmp197:
	movq	-24(%rbp), %r12
	movq	-16(%rbp), %r15
	leaq	(%r12,%r15), %rbx
	jmp	.LBB200_16
	.seh_handlerdata
	.long	$cppxdata$_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result7get_ptx@IMGREL
	.section	.text,"xr",one_only,_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result7get_ptx,unique,201
	.seh_endproc
	.def	"?dtor$27@?0?_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result7get_ptx@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$27@?0?_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result7get_ptx@4HA":
.seh_proc "?dtor$27@?0?_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result7get_ptx@4HA"
.LBB200_27:
	movq	%rdx, 16(%rsp)
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
	leaq	80(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, -32(%rbp)
	je	.LBB200_29
	movq	-24(%rbp), %rcx
	callq	mi_free
	nop
.LBB200_29:
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
.Lfunc_end200:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result7get_ptx,unique,201
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result7get_ptx,unique,20
	.p2align	2, 0x0
$cppxdata$_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result7get_ptx:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result7get_ptx@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result7get_ptx@IMGREL
	.long	72
	.long	0
	.long	1
$stateUnwindMap$_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result7get_ptx:
	.long	-1
	.long	"?dtor$27@?0?_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result7get_ptx@4HA"@IMGREL
$ip2state$_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result7get_ptx:
	.long	.Lfunc_begin200@IMGREL
	.long	-1
	.long	.Ltmp198@IMGREL
	.long	0
	.long	.Ltmp197@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvNtNtCs5UjBoGikVie_6cudarc5nvrtc6result7get_ptx,unique,201

	.def	_RNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuLaunchKernel;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuLaunchKernel,unique,202
	.globl	_RNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuLaunchKernel
	.p2align	4
_RNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuLaunchKernel:
.Lfunc_begin201:
.seh_proc _RNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuLaunchKernel
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuLaunchKernel2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB201_1
.LBB201_2:
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuLaunchKernel2__S.llvm.1750587498003715262(%rip), %rax
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	rex64 jmpq	*%rax
.LBB201_1:
	movl	%r9d, %esi
	movl	%r8d, %ebx
	movl	%edx, %edi
	movq	%rcx, %r14
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stmmmmmmmONtBZ_11CUstream_stOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidB29_ENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_14cuLaunchKernel0E0zEB13_.llvm.1750587498003715262
	movq	%r14, %rcx
	movl	%edi, %edx
	movl	%ebx, %r8d
	movl	%esi, %r9d
	jmp	.LBB201_2
.Lfunc_end201:
	.seh_endproc

	.def	_RNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoHAsync_v2;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoHAsync_v2,unique,203
	.globl	_RNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoHAsync_v2
	.p2align	4
_RNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoHAsync_v2:
.Lfunc_begin202:
.seh_proc _RNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoHAsync_v2
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoHAsync_v22__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB202_1
.LBB202_2:
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoHAsync_v22__S.llvm.1750587498003715262(%rip), %rax
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	rex64 jmpq	*%rax
.LBB202_1:
	movq	%r9, %rsi
	movq	%r8, %rbx
	movq	%rdx, %rdi
	movq	%rcx, %r14
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1A_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB1A_20cuMemcpyDtoHAsync_v20E0zEB1E_.llvm.1750587498003715262
	movq	%r14, %rcx
	movq	%rdi, %rdx
	movq	%rbx, %r8
	movq	%rsi, %r9
	jmp	.LBB202_2
.Lfunc_end202:
	.seh_endproc

	.def	_RNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyHtoDAsync_v2;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyHtoDAsync_v2,unique,204
	.globl	_RNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyHtoDAsync_v2
	.p2align	4
_RNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyHtoDAsync_v2:
.Lfunc_begin203:
.seh_proc _RNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyHtoDAsync_v2
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyHtoDAsync_v22__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB203_1
.LBB203_2:
	movq	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyHtoDAsync_v22__S.llvm.1750587498003715262(%rip), %rax
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	rex64 jmpq	*%rax
.LBB203_1:
	movq	%r9, %rsi
	movq	%r8, %rbx
	movq	%rdx, %rdi
	movq	%rcx, %r14
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1A_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB1A_20cuMemcpyHtoDAsync_v20E0zEB1E_.llvm.1750587498003715262
	movq	%r14, %rcx
	movq	%rdi, %rdx
	movq	%rbx, %r8
	movq	%rsi, %r9
	jmp	.LBB203_2
.Lfunc_end203:
	.seh_endproc

	.def	_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result10free_async;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result10free_async,unique,205
	.globl	_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result10free_async
	.p2align	4
_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result10free_async:
.Lfunc_begin204:
.seh_proc _RNvNtNtCs5UjBoGikVie_6cudarc6driver6result10free_async
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuMemFreeAsync2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB204_1
.LBB204_2:
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuMemFreeAsync2__S.llvm.1750587498003715262(%rip)
	xorl	%ecx, %ecx
	cmpl	$1, %eax
	sbbl	%ecx, %ecx
	orl	%ecx, %eax
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB204_1:
	movq	%rdx, %rsi
	movq	%rcx, %rdi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_14cuMemFreeAsync0E0zEB14_.llvm.1750587498003715262
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	jmp	.LBB204_2
.Lfunc_end204:
	.seh_endproc

	.def	_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result11malloc_host;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result11malloc_host,unique,206
	.globl	_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result11malloc_host
	.p2align	4
_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result11malloc_host:
.Lfunc_begin205:
.seh_proc _RNvNtNtCs5UjBoGikVie_6cudarc6driver6result11malloc_host
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$48, %rsp
	.seh_stackalloc 48
	.seh_endprologue
	movq	%rcx, %rsi
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuMemHostAlloc2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB205_1
	leaq	40(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuMemHostAlloc2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	je	.LBB205_3
.LBB205_4:
	movl	%eax, 4(%rsi)
	movl	$1, %eax
	jmp	.LBB205_5
.LBB205_1:
	movl	%r8d, %edi
	movq	%rdx, %rbx
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidjmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB1B_14cuMemHostAlloc0E0zEB1F_.llvm.1750587498003715262
	movq	%rbx, %rdx
	movl	%edi, %r8d
	leaq	40(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuMemHostAlloc2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB205_4
.LBB205_3:
	movq	40(%rsp), %rax
	movq	%rax, 8(%rsi)
	xorl	%eax, %eax
.LBB205_5:
	movl	%eax, (%rsi)
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end205:
	.seh_endproc

	.def	_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result11malloc_sync;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result11malloc_sync,unique,207
	.globl	_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result11malloc_sync
	.p2align	4
_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result11malloc_sync:
.Lfunc_begin206:
.seh_proc _RNvNtNtCs5UjBoGikVie_6cudarc6driver6result11malloc_sync
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	%rcx, %rsi
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuMemAlloc_v22__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB206_1
	leaq	32(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuMemAlloc_v22__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	je	.LBB206_3
.LBB206_4:
	movl	%eax, 4(%rsi)
	movl	$1, %eax
	jmp	.LBB206_5
.LBB206_1:
	movq	%rdx, %rdi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOyjENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_13cuMemAlloc_v20E0zEB16_.llvm.1750587498003715262
	movq	%rdi, %rdx
	leaq	32(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuMemAlloc_v22__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB206_4
.LBB206_3:
	movq	32(%rsp), %rax
	movq	%rax, 8(%rsi)
	xorl	%eax, %eax
.LBB206_5:
	movl	%eax, (%rsi)
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end206:
	.seh_endproc

	.def	_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result12malloc_async;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result12malloc_async,unique,208
	.globl	_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result12malloc_async
	.p2align	4
_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result12malloc_async:
.Lfunc_begin207:
.seh_proc _RNvNtNtCs5UjBoGikVie_6cudarc6driver6result12malloc_async
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$48, %rsp
	.seh_stackalloc 48
	.seh_endprologue
	movq	%r8, %rbx
	movq	%rdx, %rdi
	movq	%rcx, %rsi
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuMemAllocAsync2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB207_1
.LBB207_2:
	leaq	40(%rsp), %rcx
	movq	%rbx, %rdx
	movq	%rdi, %r8
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuMemAllocAsync2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	je	.LBB207_3
	movl	%eax, 4(%rsi)
	movl	$1, %eax
	jmp	.LBB207_5
.LBB207_3:
	movq	40(%rsp), %rax
	movq	%rax, 8(%rsi)
	xorl	%eax, %eax
.LBB207_5:
	movl	%eax, (%rsi)
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB207_1:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB12_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_15cuMemAllocAsync0E0zEB16_.llvm.1750587498003715262
	jmp	.LBB207_2
.Lfunc_end207:
	.seh_endproc

	.def	_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result15memset_d8_async;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result15memset_d8_async,unique,209
	.globl	_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result15memset_d8_async
	.p2align	4
_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result15memset_d8_async:
.Lfunc_begin208:
.seh_proc _RNvNtNtCs5UjBoGikVie_6cudarc6driver6result15memset_d8_async
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuMemsetD8Async2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB208_1
.LBB208_2:
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuMemsetD8Async2__S.llvm.1750587498003715262(%rip)
	xorl	%ecx, %ecx
	cmpl	$1, %eax
	sbbl	%ecx, %ecx
	orl	%ecx, %eax
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB208_1:
	movq	%r9, %rsi
	movq	%r8, %rdi
	movl	%edx, %ebx
	movq	%rcx, %r14
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyhjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB12_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_15cuMemsetD8Async0E0zEB16_.llvm.1750587498003715262
	movq	%r14, %rcx
	movl	%ebx, %edx
	movq	%rdi, %r8
	movq	%rsi, %r9
	jmp	.LBB208_2
.Lfunc_end208:
	.seh_endproc

	.def	_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result17memcpy_dtod_async;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result17memcpy_dtod_async,unique,210
	.globl	_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result17memcpy_dtod_async
	.p2align	4
_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result17memcpy_dtod_async:
.Lfunc_begin209:
.seh_proc _RNvNtNtCs5UjBoGikVie_6cudarc6driver6result17memcpy_dtod_async
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoDAsync_v22__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB209_1
.LBB209_2:
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoDAsync_v22__S.llvm.1750587498003715262(%rip)
	xorl	%ecx, %ecx
	cmpl	$1, %eax
	sbbl	%ecx, %ecx
	orl	%ecx, %eax
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB209_1:
	movq	%r9, %rsi
	movq	%r8, %rbx
	movq	%rdx, %rdi
	movq	%rcx, %r14
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB12_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB12_20cuMemcpyDtoDAsync_v20E0zEB16_.llvm.1750587498003715262
	movq	%r14, %rcx
	movq	%rdi, %rdx
	movq	%rbx, %r8
	movq	%rsi, %r9
	jmp	.LBB209_2
.Lfunc_end209:
	.seh_endproc

	.def	_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result17memcpy_peer_async;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result17memcpy_peer_async,unique,211
	.globl	_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result17memcpy_peer_async
	.p2align	4
_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result17memcpy_peer_async:
.Lfunc_begin210:
.seh_proc _RNvNtNtCs5UjBoGikVie_6cudarc6driver6result17memcpy_peer_async
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
	subq	$56, %rsp
	.seh_stackalloc 56
	.seh_endprologue
	movq	%r9, %rdi
	movq	%r8, %rsi
	movq	%rdx, %r14
	movq	%rcx, %rbx
	movq	152(%rsp), %r12
	movq	144(%rsp), %r15
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuMemcpyPeerAsync2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB210_1
.LBB210_2:
	movq	%r12, 40(%rsp)
	movq	%r15, 32(%rsp)
	movq	%r14, %rcx
	movq	%rbx, %rdx
	movq	%rdi, %r8
	movq	%rsi, %r9
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuMemcpyPeerAsync2__S.llvm.1750587498003715262(%rip)
	xorl	%ecx, %ecx
	cmpl	$1, %eax
	sbbl	%ecx, %ecx
	orl	%ecx, %eax
	.seh_startepilogue
	addq	$56, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r14
	popq	%r15
	.seh_endepilogue
	retq
.LBB210_1:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_styBX_jONtB10_11CUstream_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_17cuMemcpyPeerAsync0E0zEB14_.llvm.1750587498003715262
	jmp	.LBB210_2
.Lfunc_end210:
	.seh_endproc

	.def	_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result9free_host;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result9free_host,unique,212
	.globl	_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result9free_host
	.p2align	4
_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result9free_host:
.Lfunc_begin211:
.seh_proc _RNvNtNtCs5UjBoGikVie_6cudarc6driver6result9free_host
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuMemFreeHost2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB211_1
.LBB211_2:
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuMemFreeHost2__S.llvm.1750587498003715262(%rip)
	xorl	%ecx, %ecx
	cmpl	$1, %eax
	sbbl	%ecx, %ecx
	orl	%ecx, %eax
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB211_1:
	movq	%rcx, %rsi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB1y_13cuMemFreeHost0E0zEB1C_.llvm.1750587498003715262
	movq	%rsi, %rcx
	jmp	.LBB211_2
.Lfunc_end211:
	.seh_endproc

	.def	_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result9free_sync;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result9free_sync,unique,213
	.globl	_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result9free_sync
	.p2align	4
_RNvNtNtCs5UjBoGikVie_6cudarc6driver6result9free_sync:
.Lfunc_begin212:
.seh_proc _RNvNtNtCs5UjBoGikVie_6cudarc6driver6result9free_sync
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys12cuMemFree_v22__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB212_1
.LBB212_2:
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys12cuMemFree_v22__S.llvm.1750587498003715262(%rip)
	xorl	%ecx, %ecx
	cmpl	$1, %eax
	sbbl	%ecx, %ecx
	orl	%ecx, %eax
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB212_1:
	movq	%rcx, %rsi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCyENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_12cuMemFree_v20E0zEB14_.llvm.1750587498003715262
	movq	%rsi, %rcx
	jmp	.LBB212_2
.Lfunc_end212:
	.seh_endproc

	.def	_RNvXNtNtNtCs5UjBoGikVie_6cudarc6driver4safe5graphNtB2_9CudaGraphNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXNtNtNtCs5UjBoGikVie_6cudarc6driver4safe5graphNtB2_9CudaGraphNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop,unique,214
	.globl	_RNvXNtNtNtCs5UjBoGikVie_6cudarc6driver4safe5graphNtB2_9CudaGraphNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop
	.p2align	4
_RNvXNtNtNtCs5UjBoGikVie_6cudarc6driver4safe5graphNtB2_9CudaGraphNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop:
.Lfunc_begin213:
.seh_proc _RNvXNtNtNtCs5UjBoGikVie_6cudarc6driver4safe5graphNtB2_9CudaGraphNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop
	pushq	%r14
	.seh_pushreg %r14
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	%rcx, %rsi
	movq	(%rcx), %rdi
	movq	16(%rcx), %rcx
	movq	$0, 16(%rsi)
	testq	%rcx, %rcx
	je	.LBB213_5
	movq	16(%rdi), %rbx
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuGraphExecDestroy2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB213_2
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuGraphExecDestroy2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	je	.LBB213_5
.LBB213_4:
	movl	%eax, 44(%rbx)
.LBB213_5:
	movq	8(%rsi), %rcx
	movq	$0, 8(%rsi)
	testq	%rcx, %rcx
	je	.LBB213_10
	movq	16(%rdi), %rsi
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuGraphDestroy2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB213_7
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuGraphDestroy2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	je	.LBB213_10
.LBB213_9:
	movl	%eax, 44(%rsi)
.LBB213_10:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.LBB213_2:
	movq	%rcx, %r14
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_18cuGraphExecDestroy0E0zEB13_.llvm.1750587498003715262
	movq	%r14, %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuGraphExecDestroy2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB213_4
	jmp	.LBB213_5
.LBB213_7:
	movq	%rcx, %rdi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUgraph_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_14cuGraphDestroy0E0zEB13_.llvm.1750587498003715262
	movq	%rdi, %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuGraphDestroy2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB213_9
	jmp	.LBB213_10
.Lfunc_end213:
	.seh_endproc

	.def	_RNvXs0_NtNtCs5UjBoGikVie_6cudarc6driver6resultNtB5_11DriverErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs0_NtNtCs5UjBoGikVie_6cudarc6driver6resultNtB5_11DriverErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt,unique,215
	.globl	_RNvXs0_NtNtCs5UjBoGikVie_6cudarc6driver6resultNtB5_11DriverErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt
	.p2align	4
_RNvXs0_NtNtCs5UjBoGikVie_6cudarc6driver6resultNtB5_11DriverErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt:
.Lfunc_begin214:
.seh_proc _RNvXs0_NtNtCs5UjBoGikVie_6cudarc6driver6resultNtB5_11DriverErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt
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
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$104, %rsp
	.seh_stackalloc 104
	.seh_endprologue
	movq	%rdx, %rsi
	movq	%rcx, %r14
	movl	(%rcx), %ecx
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys16cuGetErrorString2__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB214_1
	leaq	48(%rsp), %rdx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys16cuGetErrorString2__S(%rip)
	testl	%eax, %eax
	je	.LBB214_18
.LBB214_3:
	movq	(%rsi), %rdi
	movq	8(%rsi), %r12
	movq	24(%r12), %r15
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1004(%rip), %rdx
	movl	$11, %r8d
	movq	%rdi, %rcx
	callq	*%r15
	movb	$1, %bl
	testb	%al, %al
	jne	.LBB214_34
	movl	16(%rsi), %r13d
	testl	$8388608, %r13d
	jne	.LBB214_7
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.39.llvm.17490583796818522722(%rip), %rdx
	movl	$1, %r8d
	movq	%rdi, %rcx
	callq	*%r15
	testb	%al, %al
	jne	.LBB214_34
	movq	%r14, %rcx
	movq	%rsi, %rdx
	callq	_RNvXsfq_NtNtCs5UjBoGikVie_6cudarc6driver3sysNtB6_14cudaError_enumNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt
	testb	%al, %al
	je	.LBB214_11
	jmp	.LBB214_34
.LBB214_7:
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.40.llvm.17490583796818522722(%rip), %rdx
	movl	$2, %r8d
	movq	%rdi, %rcx
	callq	*%r15
	testb	%al, %al
	jne	.LBB214_34
	movb	$1, 47(%rsp)
	movq	%rdi, 72(%rsp)
	movq	%r12, 80(%rsp)
	leaq	47(%rsp), %rax
	movq	%rax, 88(%rsp)
	movq	16(%rsi), %r13
	movq	%r13, 64(%rsp)
	leaq	72(%rsp), %rax
	movq	%rax, 48(%rsp)
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.99.llvm.17490583796818522722(%rip), %rax
	movq	%rax, 56(%rsp)
	leaq	48(%rsp), %rdx
	movq	%r14, %rcx
	callq	_RNvXsfq_NtNtCs5UjBoGikVie_6cudarc6driver3sysNtB6_14cudaError_enumNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt
	testb	%al, %al
	jne	.LBB214_34
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.38.llvm.17490583796818522722(%rip), %rdx
	leaq	72(%rsp), %rcx
	movl	$2, %r8d
	callq	_RNvXs0_NtNtCs8xEFJqa6dYS_4core3fmt8buildersNtB5_10PadAdapterNtB7_5Write9write_str
	testb	%al, %al
	jne	.LBB214_34
.LBB214_11:
	testl	$8388608, %r13d
	jne	.LBB214_14
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.35.llvm.17490583796818522722(%rip), %rdx
	movl	$2, %r8d
	movq	%rdi, %rcx
	callq	*%r15
	testb	%al, %al
	jne	.LBB214_34
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1007(%rip), %rcx
	movl	$41, %edx
	movq	%rsi, %r8
	callq	_RNvXsh_NtCs8xEFJqa6dYS_4core3fmteNtB5_5Debug3fmt
	jmp	.LBB214_16
.LBB214_14:
	movb	$1, 47(%rsp)
	movq	%rdi, 72(%rsp)
	movq	%r12, 80(%rsp)
	leaq	47(%rsp), %rax
	movq	%rax, 88(%rsp)
	movq	16(%rsi), %rax
	movq	%rax, 64(%rsp)
	leaq	72(%rsp), %rax
	movq	%rax, 48(%rsp)
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.99.llvm.17490583796818522722(%rip), %rax
	movq	%rax, 56(%rsp)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1007(%rip), %rcx
	leaq	48(%rsp), %r8
	movl	$41, %edx
	callq	_RNvXsh_NtCs8xEFJqa6dYS_4core3fmteNtB5_5Debug3fmt
	testb	%al, %al
	jne	.LBB214_34
	movq	48(%rsp), %rcx
	movq	56(%rsp), %rax
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.38.llvm.17490583796818522722(%rip), %rdx
	movl	$2, %r8d
	callq	*24(%rax)
.LBB214_16:
	testb	%al, %al
	jne	.LBB214_34
	movq	(%rsi), %rcx
	movq	8(%rsi), %rax
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.57.llvm.17490583796818522722(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	jmp	.LBB214_33
.LBB214_1:
	movl	%ecx, %edi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCNtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumOPaEBW_E10initializeNCINvB2_11get_or_initNCNvBY_16cuGetErrorString0E0zEB12_
	movl	%edi, %ecx
	leaq	48(%rsp), %rdx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys16cuGetErrorString2__S(%rip)
	testl	%eax, %eax
	jne	.LBB214_3
.LBB214_18:
	movq	48(%rsp), %r15
	movq	%r15, %rcx
	callq	strlen
	movq	%rax, %r12
	movq	(%rsi), %rdi
	movq	8(%rsi), %rbp
	movq	24(%rbp), %r13
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1004(%rip), %rdx
	movl	$11, %r8d
	movq	%rdi, %rcx
	callq	*%r13
	movb	$1, %bl
	testb	%al, %al
	je	.LBB214_19
.LBB214_34:
	movl	%ebx, %eax
	.seh_startepilogue
	addq	$104, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r13
	popq	%r14
	popq	%r15
	.seh_endepilogue
	retq
.LBB214_19:
	movq	%r12, 96(%rsp)
	movl	16(%rsi), %r12d
	testl	$8388608, %r12d
	jne	.LBB214_22
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.39.llvm.17490583796818522722(%rip), %rdx
	movl	$1, %r8d
	movq	%rdi, %rcx
	callq	*%r13
	testb	%al, %al
	jne	.LBB214_34
	movq	%r14, %rcx
	movq	%rsi, %rdx
	callq	_RNvXsfq_NtNtCs5UjBoGikVie_6cudarc6driver3sysNtB6_14cudaError_enumNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt
	testb	%al, %al
	jne	.LBB214_34
	jmp	.LBB214_26
.LBB214_22:
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.40.llvm.17490583796818522722(%rip), %rdx
	movl	$2, %r8d
	movq	%rdi, %rcx
	callq	*%r13
	testb	%al, %al
	jne	.LBB214_34
	movb	$1, 47(%rsp)
	movq	%rdi, 72(%rsp)
	movq	%rbp, 80(%rsp)
	leaq	47(%rsp), %rax
	movq	%rax, 88(%rsp)
	movq	16(%rsi), %r12
	movq	%r12, 64(%rsp)
	leaq	72(%rsp), %rax
	movq	%rax, 48(%rsp)
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.99.llvm.17490583796818522722(%rip), %rax
	movq	%rax, 56(%rsp)
	leaq	48(%rsp), %rdx
	movq	%r14, %rcx
	callq	_RNvXsfq_NtNtCs5UjBoGikVie_6cudarc6driver3sysNtB6_14cudaError_enumNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt
	testb	%al, %al
	jne	.LBB214_34
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.38.llvm.17490583796818522722(%rip), %rdx
	leaq	72(%rsp), %rcx
	movl	$2, %r8d
	callq	_RNvXs0_NtNtCs8xEFJqa6dYS_4core3fmt8buildersNtB5_10PadAdapterNtB7_5Write9write_str
	testb	%al, %al
	jne	.LBB214_34
.LBB214_26:
	testl	$8388608, %r12d
	jne	.LBB214_29
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.35.llvm.17490583796818522722(%rip), %rdx
	movl	$2, %r8d
	movq	%rdi, %rcx
	callq	*%r13
	testb	%al, %al
	movq	96(%rsp), %rdx
	jne	.LBB214_34
	movq	%r15, %rcx
	movq	%rsi, %r8
	callq	_RNvXs2_NtCs8xEFJqa6dYS_4core4bstrNtB5_7ByteStrNtNtB7_3fmt5Debug3fmt
	jmp	.LBB214_31
.LBB214_29:
	movb	$1, 47(%rsp)
	movq	%rdi, 72(%rsp)
	movq	%rbp, 80(%rsp)
	leaq	47(%rsp), %rax
	movq	%rax, 88(%rsp)
	movq	16(%rsi), %rax
	movq	%rax, 64(%rsp)
	leaq	72(%rsp), %rax
	movq	%rax, 48(%rsp)
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.99.llvm.17490583796818522722(%rip), %rax
	movq	%rax, 56(%rsp)
	leaq	48(%rsp), %r8
	movq	%r15, %rcx
	movq	96(%rsp), %rdx
	callq	_RNvXs2_NtCs8xEFJqa6dYS_4core4bstrNtB5_7ByteStrNtNtB7_3fmt5Debug3fmt
	testb	%al, %al
	jne	.LBB214_34
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.38.llvm.17490583796818522722(%rip), %rdx
	leaq	72(%rsp), %rcx
	movl	$2, %r8d
	callq	_RNvXs0_NtNtCs8xEFJqa6dYS_4core3fmt8buildersNtB5_10PadAdapterNtB7_5Write9write_str
.LBB214_31:
	testb	%al, %al
	jne	.LBB214_34
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.57.llvm.17490583796818522722(%rip), %rdx
	movl	$1, %r8d
	movq	%rdi, %rcx
	callq	*%r13
.LBB214_33:
	movl	%eax, %ebx
	jmp	.LBB214_34
.Lfunc_end214:
	.seh_endproc

	.def	_RNvXs0_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContextNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs0_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContextNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop,unique,216
	.globl	_RNvXs0_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContextNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop
	.p2align	4
_RNvXs0_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContextNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop:
.Lfunc_begin215:
.seh_proc _RNvXs0_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_11CudaContextNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	%rcx, %rsi
	xorl	%eax, %eax
	xchgl	%eax, 28(%rcx)
	testl	%eax, %eax
	jne	.LBB215_8
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB215_2
	leaq	32(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	je	.LBB215_4
.LBB215_8:
	movl	%eax, 28(%rsi)
.LBB215_9:
	movq	(%rsi), %rcx
.LBB215_10:
	movq	$0, (%rsi)
	testq	%rcx, %rcx
	je	.LBB215_17
	cmpb	$0, 34(%rsi)
	je	.LBB215_12
	movl	24(%rsi), %ecx
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys28cuDevicePrimaryCtxRelease_v22__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB215_19
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys28cuDevicePrimaryCtxRelease_v22__S(%rip)
	testl	%eax, %eax
	jne	.LBB215_16
	jmp	.LBB215_17
.LBB215_12:
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxDestroy_v22__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB215_13
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxDestroy_v22__S(%rip)
	testl	%eax, %eax
	je	.LBB215_17
.LBB215_16:
	movl	%eax, 28(%rsi)
.LBB215_17:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB215_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_15cuCtxGetCurrent0E0zEB14_.llvm.1750587498003715262
	leaq	32(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB215_8
.LBB215_4:
	movq	32(%rsp), %rax
	testq	%rax, %rax
	setne	%dl
	movq	(%rsi), %rcx
	cmpq	%rcx, %rax
	sete	%al
	testb	%al, %dl
	jne	.LBB215_10
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB215_6
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB215_8
	jmp	.LBB215_9
.LBB215_19:
	movl	%ecx, %edi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKClENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_28cuDevicePrimaryCtxRelease_v20E0zEB14_
	movl	%edi, %ecx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys28cuDevicePrimaryCtxRelease_v22__S(%rip)
	testl	%eax, %eax
	jne	.LBB215_16
	jmp	.LBB215_17
.LBB215_13:
	movq	%rcx, %rdi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxDestroy_v20E0zEB13_
	movq	%rdi, %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxDestroy_v22__S(%rip)
	testl	%eax, %eax
	jne	.LBB215_16
	jmp	.LBB215_17
.LBB215_6:
	movq	%rcx, %rdi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxSetCurrent0E0zEB13_.llvm.1750587498003715262
	movq	%rdi, %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB215_8
	jmp	.LBB215_9
.Lfunc_end215:
	.seh_endproc

	.def	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRINtNtCsfQUUnEvlYZE_5alloc3vec3VechENtB6_5Debug3fmtCs5UjBoGikVie_6cudarc;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRINtNtCsfQUUnEvlYZE_5alloc3vec3VechENtB6_5Debug3fmtCs5UjBoGikVie_6cudarc,unique,217
	.p2align	4
_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRINtNtCsfQUUnEvlYZE_5alloc3vec3VechENtB6_5Debug3fmtCs5UjBoGikVie_6cudarc:
.Lfunc_begin216:
.seh_proc _RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRINtNtCsfQUUnEvlYZE_5alloc3vec3VechENtB6_5Debug3fmtCs5UjBoGikVie_6cudarc
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
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$104, %rsp
	.seh_stackalloc 104
	.seh_endprologue
	movq	%rdx, %rsi
	movq	(%rcx), %rax
	movq	8(%rax), %r12
	movq	16(%rax), %r13
	movq	(%rdx), %rdi
	movq	8(%rdx), %rbx
	movq	24(%rbx), %r14
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.207.llvm.17490583796818522722(%rip), %rdx
	movl	$1, %r8d
	movq	%rdi, %rcx
	callq	*%r14
	movl	%eax, %ecx
	testq	%r13, %r13
	je	.LBB216_20
	movq	%r12, 48(%rsp)
	movb	$1, %al
	testb	%cl, %cl
	jne	.LBB216_8
	testb	$-128, 18(%rsi)
	jne	.LBB216_3
	leaq	48(%rsp), %rcx
	movq	%rsi, %rdx
	callq	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRhNtB6_5Debug3fmtCs5UjBoGikVie_6cudarc
	cmpq	$1, %r13
	je	.LBB216_9
	jmp	.LBB216_10
.LBB216_3:
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.41.llvm.17490583796818522722(%rip), %rdx
	movl	$1, %r8d
	movq	%rdi, %rcx
	callq	*%r14
	movl	%eax, %ecx
	movb	$1, %al
	testb	%cl, %cl
	jne	.LBB216_8
	movb	$1, 47(%rsp)
	movq	%rdi, 80(%rsp)
	movq	%rbx, 88(%rsp)
	leaq	47(%rsp), %rax
	movq	%rax, 96(%rsp)
	movq	16(%rsi), %rax
	movq	%rax, 72(%rsp)
	leaq	80(%rsp), %rax
	movq	%rax, 56(%rsp)
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.99.llvm.17490583796818522722(%rip), %rax
	movq	%rax, 64(%rsp)
	leaq	48(%rsp), %rcx
	leaq	56(%rsp), %rdx
	callq	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRhNtB6_5Debug3fmtCs5UjBoGikVie_6cudarc
	testb	%al, %al
	je	.LBB216_5
	movb	$1, %al
.LBB216_8:
	cmpq	$1, %r13
	jne	.LBB216_10
.LBB216_9:
	movl	%eax, %ecx
.LBB216_20:
	movb	$1, %al
	testb	%cl, %cl
	jne	.LBB216_22
	movq	(%rsi), %rcx
	movq	8(%rsi), %rax
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.63.llvm.17490583796818522722(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	nop
.LBB216_22:
	.seh_startepilogue
	addq	$104, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r13
	popq	%r14
	popq	%r15
	.seh_endepilogue
	retq
.LBB216_5:
	movq	56(%rsp), %rcx
	movq	64(%rsp), %rax
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.38.llvm.17490583796818522722(%rip), %rdx
	movl	$2, %r8d
	callq	*24(%rax)
	cmpq	$1, %r13
	je	.LBB216_9
.LBB216_10:
	incq	%r12
	decq	%r13
	leaq	48(%rsp), %rbx
	leaq	47(%rsp), %rbp
	leaq	80(%rsp), %r15
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.99.llvm.17490583796818522722(%rip), %rdi
	leaq	56(%rsp), %r14
	jmp	.LBB216_11
.LBB216_16:
	movb	$1, %cl
	.p2align	4
.LBB216_19:
	incq	%r12
	movl	%ecx, %eax
	decq	%r13
	je	.LBB216_20
.LBB216_11:
	movq	%r12, 48(%rsp)
	movb	$1, %cl
	testb	$1, %al
	jne	.LBB216_19
	testb	$-128, 18(%rsi)
	jne	.LBB216_15
	movq	(%rsi), %rcx
	movq	8(%rsi), %rax
	movl	$2, %r8d
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.35.llvm.17490583796818522722(%rip), %rdx
	callq	*24(%rax)
	movb	$1, %cl
	testb	%al, %al
	jne	.LBB216_19
	movq	%rbx, %rcx
	movq	%rsi, %rdx
	callq	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRhNtB6_5Debug3fmtCs5UjBoGikVie_6cudarc
	jmp	.LBB216_18
	.p2align	4
.LBB216_15:
	movb	$1, 47(%rsp)
	movups	(%rsi), %xmm0
	movaps	%xmm0, 80(%rsp)
	movq	%rbp, 96(%rsp)
	movq	16(%rsi), %rax
	movq	%rax, 72(%rsp)
	movq	%r15, 56(%rsp)
	movq	%rdi, 64(%rsp)
	movq	%rbx, %rcx
	movq	%r14, %rdx
	callq	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRhNtB6_5Debug3fmtCs5UjBoGikVie_6cudarc
	testb	%al, %al
	jne	.LBB216_16
	movq	56(%rsp), %rcx
	movq	64(%rsp), %rax
	movl	$2, %r8d
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.38.llvm.17490583796818522722(%rip), %rdx
	callq	*24(%rax)
.LBB216_18:
	movl	%eax, %ecx
	jmp	.LBB216_19
.Lfunc_end216:
	.seh_endproc

	.def	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRSNtNtCsfQUUnEvlYZE_5alloc6string6StringNtB6_5Debug3fmtCs5UjBoGikVie_6cudarc;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRSNtNtCsfQUUnEvlYZE_5alloc6string6StringNtB6_5Debug3fmtCs5UjBoGikVie_6cudarc,unique,218
	.p2align	4
_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRSNtNtCsfQUUnEvlYZE_5alloc6string6StringNtB6_5Debug3fmtCs5UjBoGikVie_6cudarc:
.Lfunc_begin217:
.seh_proc _RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRSNtNtCsfQUUnEvlYZE_5alloc6string6StringNtB6_5Debug3fmtCs5UjBoGikVie_6cudarc
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
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$88, %rsp
	.seh_stackalloc 88
	.seh_endprologue
	movq	%rdx, %rsi
	movq	(%rcx), %r15
	movq	8(%rcx), %rbx
	movq	(%rdx), %rdi
	movq	8(%rdx), %rax
	movq	24(%rax), %r14
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.207.llvm.17490583796818522722(%rip), %rdx
	movl	$1, %r8d
	movq	%rdi, %rcx
	callq	*%r14
	movl	%eax, %ecx
	testq	%rbx, %rbx
	je	.LBB217_20
	movb	$1, %al
	testb	%cl, %cl
	jne	.LBB217_8
	testb	$-128, 18(%rsi)
	jne	.LBB217_3
	movq	8(%r15), %rcx
	movq	16(%r15), %rdx
	movq	%rsi, %r8
	callq	_RNvXsh_NtCs8xEFJqa6dYS_4core3fmteNtB5_5Debug3fmt
	cmpq	$1, %rbx
	je	.LBB217_9
	jmp	.LBB217_10
.LBB217_3:
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.41.llvm.17490583796818522722(%rip), %rdx
	movl	$1, %r8d
	movq	%rdi, %rcx
	callq	*%r14
	movl	%eax, %ecx
	movb	$1, %al
	testb	%cl, %cl
	jne	.LBB217_8
	movb	$1, 39(%rsp)
	movups	(%rsi), %xmm0
	movaps	%xmm0, 64(%rsp)
	leaq	39(%rsp), %rax
	movq	%rax, 80(%rsp)
	movq	16(%rsi), %rax
	movq	%rax, 56(%rsp)
	leaq	64(%rsp), %rax
	movq	%rax, 40(%rsp)
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.99.llvm.17490583796818522722(%rip), %rax
	movq	%rax, 48(%rsp)
	movq	8(%r15), %rcx
	movq	16(%r15), %rdx
	leaq	40(%rsp), %r8
	callq	_RNvXsh_NtCs8xEFJqa6dYS_4core3fmteNtB5_5Debug3fmt
	testb	%al, %al
	je	.LBB217_5
	movb	$1, %al
.LBB217_8:
	cmpq	$1, %rbx
	jne	.LBB217_10
.LBB217_9:
	movl	%eax, %ecx
.LBB217_20:
	movb	$1, %al
	testb	%cl, %cl
	jne	.LBB217_22
	movq	(%rsi), %rcx
	movq	8(%rsi), %rax
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.63.llvm.17490583796818522722(%rip), %rdx
	movl	$1, %r8d
	callq	*24(%rax)
	nop
.LBB217_22:
	.seh_startepilogue
	addq	$88, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r13
	popq	%r14
	popq	%r15
	.seh_endepilogue
	retq
.LBB217_5:
	movq	40(%rsp), %rcx
	movq	48(%rsp), %rax
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.38.llvm.17490583796818522722(%rip), %rdx
	movl	$2, %r8d
	callq	*24(%rax)
	cmpq	$1, %rbx
	je	.LBB217_9
.LBB217_10:
	shlq	$3, %rbx
	leaq	(%rbx,%rbx,2), %r12
	addq	$-24, %r12
	xorl	%r13d, %r13d
	leaq	39(%rsp), %rbp
	leaq	64(%rsp), %r14
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.99.llvm.17490583796818522722(%rip), %rdi
	leaq	40(%rsp), %rbx
	jmp	.LBB217_11
.LBB217_16:
	movb	$1, %cl
	.p2align	4
.LBB217_19:
	addq	$24, %r13
	movl	%ecx, %eax
	cmpq	%r13, %r12
	je	.LBB217_20
.LBB217_11:
	movb	$1, %cl
	testb	$1, %al
	jne	.LBB217_19
	testb	$-128, 18(%rsi)
	jne	.LBB217_15
	movq	(%rsi), %rcx
	movq	8(%rsi), %rax
	movl	$2, %r8d
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.35.llvm.17490583796818522722(%rip), %rdx
	callq	*24(%rax)
	movb	$1, %cl
	testb	%al, %al
	jne	.LBB217_19
	movq	32(%r15,%r13), %rcx
	movq	40(%r15,%r13), %rdx
	movq	%rsi, %r8
	callq	_RNvXsh_NtCs8xEFJqa6dYS_4core3fmteNtB5_5Debug3fmt
	jmp	.LBB217_18
	.p2align	4
.LBB217_15:
	movq	32(%r15,%r13), %rcx
	movq	40(%r15,%r13), %rdx
	movq	16(%rsi), %rax
	movb	$1, 39(%rsp)
	movups	(%rsi), %xmm0
	movaps	%xmm0, 64(%rsp)
	movq	%rbp, 80(%rsp)
	movq	%rax, 56(%rsp)
	movq	%r14, 40(%rsp)
	movq	%rdi, 48(%rsp)
	movq	%rbx, %r8
	callq	_RNvXsh_NtCs8xEFJqa6dYS_4core3fmteNtB5_5Debug3fmt
	testb	%al, %al
	jne	.LBB217_16
	movq	40(%rsp), %rcx
	movq	48(%rsp), %rax
	movl	$2, %r8d
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.38.llvm.17490583796818522722(%rip), %rdx
	callq	*24(%rax)
.LBB217_18:
	movl	%eax, %ecx
	jmp	.LBB217_19
.Lfunc_end217:
	.seh_endproc

	.def	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRhNtB6_5Debug3fmtCs5UjBoGikVie_6cudarc;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRhNtB6_5Debug3fmtCs5UjBoGikVie_6cudarc,unique,219
	.p2align	4
_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRhNtB6_5Debug3fmtCs5UjBoGikVie_6cudarc:
.Lfunc_begin218:
.seh_proc _RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRhNtB6_5Debug3fmtCs5UjBoGikVie_6cudarc
	subq	$56, %rsp
	.seh_stackalloc 56
	.seh_endprologue
	movq	(%rcx), %rax
	movl	16(%rdx), %ecx
	testl	$33554432, %ecx
	jne	.LBB218_7
	testl	$67108864, %ecx
	jne	.LBB218_10
	movzbl	(%rax), %ecx
	movl	$3, %eax
	movl	%ecx, %r8d
	cmpb	$10, %cl
	jb	.LBB218_4
	movzbl	%cl, %eax
	leal	(%rax,%rax,4), %r8d
	leal	(%rax,%r8,8), %r8d
	shrl	$12, %r8d
	imull	$100, %r8d, %eax
	movl	%ecx, %r9d
	subb	%al, %r9b
	movzbl	%r9b, %eax
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.203.llvm.17490583796818522722(%rip), %r9
	movzwl	(%r9,%rax,2), %eax
	movw	%ax, 52(%rsp)
	movl	$1, %eax
.LBB218_4:
	testb	%r8b, %r8b
	sete	%r9b
	testb	%cl, %cl
	setne	%cl
	testb	%r9b, %cl
	jne	.LBB218_6
	movzbl	%r8b, %ecx
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.203.llvm.17490583796818522722(%rip), %r8
	movzbl	1(%r8,%rcx,2), %ecx
	movb	%cl, 50(%rsp,%rax)
	decq	%rax
.LBB218_6:
	movl	$3, %ecx
	subq	%rax, %rcx
	addq	%rsp, %rax
	addq	$51, %rax
	movq	%rcx, 40(%rsp)
	movq	%rax, 32(%rsp)
	movl	$1, %r8d
	movq	%rdx, %rcx
	movb	$1, %dl
	xorl	%r9d, %r9d
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter12pad_integral
	nop
	.seh_startepilogue
	addq	$56, %rsp
	.seh_endepilogue
	retq
.LBB218_7:
	movzbl	(%rax), %ecx
	xorl	%eax, %eax
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.1.llvm.17490583796818522722(%rip), %r8
	.p2align	4
.LBB218_8:
	movzbl	%cl, %r9d
	shrb	$4, %cl
	andl	$15, %r9d
	movzbl	(%r9,%r8), %r9d
	movb	%r9b, 50(%rsp,%rax)
	decq	%rax
	testb	%cl, %cl
	jne	.LBB218_8
	leaq	(%rsp,%rax), %rcx
	addq	$51, %rcx
	jmp	.LBB218_13
.LBB218_10:
	movzbl	(%rax), %ecx
	xorl	%eax, %eax
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.415.llvm.17490583796818522722(%rip), %r8
	.p2align	4
.LBB218_11:
	movzbl	%cl, %r9d
	shrb	$4, %cl
	andl	$15, %r9d
	movzbl	(%r9,%r8), %r9d
	movb	%r9b, 55(%rsp,%rax)
	decq	%rax
	testb	%cl, %cl
	jne	.LBB218_11
	leaq	(%rsp,%rax), %rcx
	addq	$56, %rcx
.LBB218_13:
	negq	%rax
	movq	%rax, 40(%rsp)
	movq	%rcx, 32(%rsp)
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.401.llvm.17490583796818522722(%rip), %r8
	movl	$2, %r9d
	movq	%rdx, %rcx
	movb	$1, %dl
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter12pad_integral
	nop
	.seh_startepilogue
	addq	$56, %rsp
	.seh_endepilogue
	retq
.Lfunc_end218:
	.seh_endproc

	.def	_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtReNtB6_7Display3fmtCs5UjBoGikVie_6cudarc;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtReNtB6_7Display3fmtCs5UjBoGikVie_6cudarc,unique,220
	.p2align	4
_RNvXs1i_NtCs8xEFJqa6dYS_4core3fmtReNtB6_7Display3fmtCs5UjBoGikVie_6cudarc:
.Lfunc_begin219:
	movq	%rdx, %rax
	movq	(%rcx), %rdx
	movq	8(%rcx), %r8
	movq	%rax, %rcx
	jmp	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
.Lfunc_end219:

	.def	_RNvXs1o_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModuleNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1o_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModuleNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop,unique,221
	.globl	_RNvXs1o_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModuleNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop
	.p2align	4
_RNvXs1o_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModuleNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop:
.Lfunc_begin220:
.seh_proc _RNvXs1o_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB6_10CudaModuleNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$48, %rsp
	.seh_stackalloc 48
	.seh_endprologue
	movq	%rcx, %rsi
	movq	(%rcx), %rdi
	xorl	%eax, %eax
	xchgl	%eax, 44(%rdi)
	testl	%eax, %eax
	jne	.LBB220_8
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB220_2
	leaq	40(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	je	.LBB220_4
.LBB220_8:
	movl	%eax, 44(%rdi)
.LBB220_9:
	movq	8(%rsi), %rcx
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuModuleUnload2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB220_10
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuModuleUnload2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	je	.LBB220_13
.LBB220_12:
	movl	%eax, 44(%rdi)
.LBB220_13:
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB220_10:
	movq	%rcx, %rsi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_14cuModuleUnload0E0zEB13_.llvm.1750587498003715262
	movq	%rsi, %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuModuleUnload2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB220_12
	jmp	.LBB220_13
.LBB220_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_15cuCtxGetCurrent0E0zEB14_.llvm.1750587498003715262
	leaq	40(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB220_8
.LBB220_4:
	movq	40(%rsp), %rax
	testq	%rax, %rax
	setne	%dl
	movq	16(%rdi), %rcx
	cmpq	%rcx, %rax
	sete	%al
	testb	%al, %dl
	jne	.LBB220_9
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB220_6
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB220_8
	jmp	.LBB220_9
.LBB220_6:
	movq	%rcx, %rbx
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxSetCurrent0E0zEB13_.llvm.1750587498003715262
	movq	%rbx, %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB220_8
	jmp	.LBB220_9
.Lfunc_end220:
	.seh_endproc

	.def	_RNvXs6_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_9CudaEventNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs6_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_9CudaEventNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop,unique,222
	.globl	_RNvXs6_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_9CudaEventNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop
	.p2align	4
_RNvXs6_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_9CudaEventNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop:
.Lfunc_begin221:
.seh_proc _RNvXs6_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_9CudaEventNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$48, %rsp
	.seh_stackalloc 48
	.seh_endprologue
	movq	%rcx, %rsi
	movq	(%rcx), %rdi
	xorl	%eax, %eax
	xchgl	%eax, 44(%rdi)
	testl	%eax, %eax
	jne	.LBB221_8
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB221_2
	leaq	40(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	je	.LBB221_4
.LBB221_8:
	movl	%eax, 44(%rdi)
.LBB221_9:
	movq	8(%rsi), %rcx
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuEventDestroy_v22__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB221_10
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuEventDestroy_v22__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	je	.LBB221_13
.LBB221_12:
	movl	%eax, 44(%rdi)
.LBB221_13:
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB221_10:
	movq	%rcx, %rsi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_17cuEventDestroy_v20E0zEB13_.llvm.1750587498003715262
	movq	%rsi, %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuEventDestroy_v22__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB221_12
	jmp	.LBB221_13
.LBB221_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_15cuCtxGetCurrent0E0zEB14_.llvm.1750587498003715262
	leaq	40(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB221_8
.LBB221_4:
	movq	40(%rsp), %rax
	testq	%rax, %rax
	setne	%dl
	movq	16(%rdi), %rcx
	cmpq	%rcx, %rax
	sete	%al
	testb	%al, %dl
	jne	.LBB221_9
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB221_6
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB221_8
	jmp	.LBB221_9
.LBB221_6:
	movq	%rcx, %rbx
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxSetCurrent0E0zEB13_.llvm.1750587498003715262
	movq	%rbx, %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB221_8
	jmp	.LBB221_9
.Lfunc_end221:
	.seh_endproc

	.def	_RNvXs9_NtNtNtCs8xEFJqa6dYS_4core4iter8adapters7flattenINtB5_7FlattenINtNtB7_3map3MapINtNtNtBb_5slice4iter4IterReENCNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib00EENtNtNtB9_6traits8iterator8Iterator4nextB1X_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs9_NtNtNtCs8xEFJqa6dYS_4core4iter8adapters7flattenINtB5_7FlattenINtNtB7_3map3MapINtNtNtBb_5slice4iter4IterReENCNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib00EENtNtNtB9_6traits8iterator8Iterator4nextB1X_,unique,223
	.p2align	4
_RNvXs9_NtNtNtCs8xEFJqa6dYS_4core4iter8adapters7flattenINtB5_7FlattenINtNtB7_3map3MapINtNtNtBb_5slice4iter4IterReENCNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib00EENtNtNtB9_6traits8iterator8Iterator4nextB1X_:
.Lfunc_begin222:
.seh_proc _RNvXs9_NtNtNtCs8xEFJqa6dYS_4core4iter8adapters7flattenINtB5_7FlattenINtNtB7_3map3MapINtNtNtBb_5slice4iter4IterReENCNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib00EENtNtNtB9_6traits8iterator8Iterator4nextB1X_
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
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movq	%rdx, %rdi
	movq	%rcx, 40(%rsp)
	movq	(%rdx), %r14
	movq	8(%rdx), %rax
	movq	72(%rdx), %r13
	movq	24(%rdx), %rcx
	movq	16(%rdx), %rsi
	movq	64(%rdx), %rbp
	leaq	48(%rsp), %rbx
	testq	%r14, %r14
	je	.LBB222_13
	.p2align	4
.LBB222_2:
	cmpq	%rcx, %rax
	je	.LBB222_3
	leaq	24(%rax), %r12
	movq	%r12, 8(%rdi)
	movq	(%rax), %rdx
	cmpq	$-1, %rdx
	je	.LBB222_5
	jmp	.LBB222_31
	.p2align	4
.LBB222_3:
	movq	%rax, %r12
.LBB222_5:
	movq	%rcx, %rax
	subq	%r12, %rax
	movabsq	$-6148914691236517205, %rdx
	mulq	%rdx
	cmpq	%r12, %rcx
	je	.LBB222_10
	movq	%rdx, %r15
	shrq	$4, %r15
	addq	$8, %r12
	jmp	.LBB222_7
	.p2align	4
.LBB222_9:
	addq	$24, %r12
	decq	%r15
	je	.LBB222_10
.LBB222_7:
	cmpq	$0, -8(%r12)
	je	.LBB222_9
	movq	(%r12), %rcx
	callq	mi_free
	jmp	.LBB222_9
	.p2align	4
.LBB222_10:
	testq	%rsi, %rsi
	je	.LBB222_12
	movq	%r14, %rcx
	callq	mi_free
.LBB222_12:
	movq	$0, (%rdi)
.LBB222_13:
	testq	%rbp, %rbp
	je	.LBB222_16
	cmpq	%r13, %rbp
	je	.LBB222_16
	leaq	16(%rbp), %r14
	movq	%r14, 64(%rdi)
	movq	(%rbp), %rdx
	movq	8(%rbp), %r8
	movq	%rbx, %rcx
	callq	_RNvCs5UjBoGikVie_6cudarc23get_lib_name_candidates
	movq	48(%rsp), %rsi
	cmpq	$-1, %rsi
	je	.LBB222_16
	movq	56(%rsp), %rax
	movq	64(%rsp), %rcx
	leaq	(%rcx,%rcx,2), %rcx
	leaq	(%rax,%rcx,8), %rcx
	movq	%rax, (%rdi)
	movq	%rax, 8(%rdi)
	movq	%rsi, 16(%rdi)
	movq	%rcx, 24(%rdi)
	movq	%r14, %rbp
	movq	%rax, %r14
	testq	%r14, %r14
	jne	.LBB222_2
	jmp	.LBB222_13
.LBB222_16:
	movq	32(%rdi), %rbx
	testq	%rbx, %rbx
	je	.LBB222_19
	movq	40(%rdi), %r13
	movq	56(%rdi), %rcx
	cmpq	%rcx, %r13
	je	.LBB222_18
	leaq	24(%r13), %rdx
	movq	%rdx, 40(%rdi)
	movq	(%r13), %rax
	movq	8(%r13), %rsi
	movq	16(%r13), %r15
	movq	%rdx, %r13
	cmpq	$-1, %rax
	jne	.LBB222_29
	jmp	.LBB222_21
.LBB222_19:
	movq	40(%rsp), %rax
	movq	$-1, (%rax)
	jmp	.LBB222_32
.LBB222_18:
.LBB222_21:
	movq	%rcx, %rax
	subq	%r13, %rax
	movabsq	$-6148914691236517205, %rdx
	mulq	%rdx
	cmpq	%r13, %rcx
	je	.LBB222_26
	movq	%rdx, %r14
	shrq	$4, %r14
	addq	$8, %r13
	jmp	.LBB222_23
	.p2align	4
.LBB222_25:
	addq	$24, %r13
	decq	%r14
	je	.LBB222_26
.LBB222_23:
	cmpq	$0, -8(%r13)
	je	.LBB222_25
	movq	(%r13), %rcx
	callq	mi_free
	jmp	.LBB222_25
.LBB222_26:
	cmpq	$0, 48(%rdi)
	je	.LBB222_28
	movq	%rbx, %rcx
	callq	mi_free
.LBB222_28:
	movq	$0, 32(%rdi)
	movq	$-1, %rax
.LBB222_29:
	movq	40(%rsp), %rcx
	movq	%rax, (%rcx)
	movq	%rsi, 8(%rcx)
	movq	%r15, 16(%rcx)
.LBB222_32:
	.seh_startepilogue
	addq	$72, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r13
	popq	%r14
	popq	%r15
	.seh_endepilogue
	retq
.LBB222_31:
	movups	8(%rax), %xmm0
	movq	40(%rsp), %rax
	movq	%rdx, (%rax)
	movups	%xmm0, 8(%rax)
	jmp	.LBB222_32
.Lfunc_end222:
	.seh_endproc

	.def	_RNvXsX_NtNtCsfQUUnEvlYZE_5alloc3ffi5c_strNtB5_8NulErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt.llvm.1750587498003715262;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXsX_NtNtCsfQUUnEvlYZE_5alloc3ffi5c_strNtB5_8NulErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt.llvm.1750587498003715262,unique,224
	.globl	_RNvXsX_NtNtCsfQUUnEvlYZE_5alloc3ffi5c_strNtB5_8NulErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt.llvm.1750587498003715262
	.p2align	4
_RNvXsX_NtNtCsfQUUnEvlYZE_5alloc3ffi5c_strNtB5_8NulErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt.llvm.1750587498003715262:
.Lfunc_begin223:
.seh_proc _RNvXsX_NtNtCsfQUUnEvlYZE_5alloc3ffi5c_strNtB5_8NulErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt.llvm.1750587498003715262
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movq	%rdx, %rax
	movq	%rcx, 64(%rsp)
	leaq	24(%rcx), %r9
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1018(%rip), %rcx
	movq	%rcx, 48(%rsp)
	leaq	64(%rsp), %rcx
	movq	%rcx, 40(%rsp)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1011(%rip), %rcx
	movq	%rcx, 32(%rsp)
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1019(%rip), %rdx
	movl	$8, %r8d
	movq	%rax, %rcx
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter25debug_tuple_field2_finish
	nop
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.Lfunc_end223:
	.seh_endproc

	.def	_RNvXsZ_NtNtCs8xEFJqa6dYS_4core3fmt3numjNtB7_5Debug3fmt;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXsZ_NtNtCs8xEFJqa6dYS_4core3fmt3numjNtB7_5Debug3fmt,unique,225
	.p2align	4
_RNvXsZ_NtNtCs8xEFJqa6dYS_4core3fmt3numjNtB7_5Debug3fmt:
.Lfunc_begin224:
.seh_proc _RNvXsZ_NtNtCs8xEFJqa6dYS_4core3fmt3numjNtB7_5Debug3fmt
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movq	%rdx, %rsi
	movl	16(%rdx), %eax
	testl	$33554432, %eax
	jne	.LBB224_3
	testl	$67108864, %eax
	jne	.LBB224_5
	movq	(%rcx), %rcx
	leaq	52(%rsp), %rdx
	movl	$20, %edi
	movl	$20, %r8d
	callq	_RNvMsk_NtNtNtCs8xEFJqa6dYS_4core3fmt3num3impj10__fmt_inner.llvm.17490583796818522722
	subq	%rax, %rdi
	addq	%rsp, %rax
	addq	$52, %rax
	movq	%rdi, 40(%rsp)
	movq	%rax, 32(%rsp)
	movl	$1, %r8d
	movq	%rsi, %rcx
	movb	$1, %dl
	xorl	%r9d, %r9d
	jmp	.LBB224_8
.LBB224_3:
	movq	(%rcx), %rcx
	xorl	%eax, %eax
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.1.llvm.17490583796818522722(%rip), %rdx
	.p2align	4
.LBB224_4:
	movl	%ecx, %r8d
	andl	$15, %r8d
	shrq	$4, %rcx
	movzbl	(%r8,%rdx), %r8d
	movb	%r8b, 67(%rsp,%rax)
	decq	%rax
	testq	%rcx, %rcx
	jne	.LBB224_4
	jmp	.LBB224_7
.LBB224_5:
	movq	(%rcx), %rcx
	xorl	%eax, %eax
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.415.llvm.17490583796818522722(%rip), %rdx
	.p2align	4
.LBB224_6:
	movl	%ecx, %r8d
	andl	$15, %r8d
	shrq	$4, %rcx
	movzbl	(%r8,%rdx), %r8d
	movb	%r8b, 67(%rsp,%rax)
	decq	%rax
	testq	%rcx, %rcx
	jne	.LBB224_6
.LBB224_7:
	leaq	(%rsp,%rax), %rcx
	addq	$68, %rcx
	negq	%rax
	movq	%rax, 40(%rsp)
	movq	%rcx, 32(%rsp)
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.401.llvm.17490583796818522722(%rip), %r8
	movl	$2, %r9d
	movq	%rsi, %rcx
	movb	$1, %dl
.LBB224_8:
	callq	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter12pad_integral
	nop
	.seh_startepilogue
	addq	$72, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end224:
	.seh_endproc

	.def	_RNvXsZ_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10SyncOnDropNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXsZ_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10SyncOnDropNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop,unique,226
	.globl	_RNvXsZ_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10SyncOnDropNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop
	.p2align	4
_RNvXsZ_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10SyncOnDropNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop:
.Lfunc_begin225:
.seh_proc _RNvXsZ_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10SyncOnDropNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$48, %rsp
	.seh_stackalloc 48
	.seh_endprologue
	movq	%rcx, %rax
	movq	8(%rcx), %rcx
	cmpl	$1, (%rax)
	jne	.LBB225_14
	movq	$0, 8(%rax)
	testq	%rcx, %rcx
	je	.LBB225_17
	movq	(%rcx), %rsi
	xorl	%eax, %eax
	xchgl	%eax, 44(%rsi)
	testl	%eax, %eax
	jne	.LBB225_16
	movq	%rcx, %rdi
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB225_4
	leaq	40(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB225_16
.LBB225_6:
	movq	40(%rsp), %rax
	movq	16(%rsi), %rcx
	testq	%rax, %rax
	je	.LBB225_8
	cmpq	%rcx, %rax
	je	.LBB225_11
.LBB225_8:
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB225_9
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB225_16
.LBB225_11:
	movq	8(%rdi), %rcx
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys19cuStreamSynchronize2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB225_12
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys19cuStreamSynchronize2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB225_16
	jmp	.LBB225_17
.LBB225_14:
	movq	16(%rax), %rdx
	movq	$0, 8(%rax)
	testq	%rcx, %rcx
	je	.LBB225_17
	movq	(%rdx), %rsi
	callq	_RNvMs8_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_9CudaEvent6record
	cmpl	$-1, %eax
	je	.LBB225_17
.LBB225_16:
	movl	%eax, 44(%rsi)
.LBB225_17:
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB225_4:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_15cuCtxGetCurrent0E0zEB14_.llvm.1750587498003715262
	leaq	40(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB225_16
	jmp	.LBB225_6
.LBB225_12:
	movq	%rcx, %rdi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_19cuStreamSynchronize0E0zEB13_.llvm.1750587498003715262
	movq	%rdi, %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys19cuStreamSynchronize2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB225_16
	jmp	.LBB225_17
.LBB225_9:
	movq	%rcx, %rbx
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxSetCurrent0E0zEB13_.llvm.1750587498003715262
	movq	%rbx, %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB225_16
	jmp	.LBB225_11
.Lfunc_end225:
	.seh_endproc

	.def	_RNvXs_NtNtCs5UjBoGikVie_6cudarc5nvrtc6resultNtB4_10NvrtcErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs_NtNtCs5UjBoGikVie_6cudarc5nvrtc6resultNtB4_10NvrtcErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt,unique,227
	.p2align	4
_RNvXs_NtNtCs5UjBoGikVie_6cudarc5nvrtc6resultNtB4_10NvrtcErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt:
.Lfunc_begin226:
.seh_proc _RNvXs_NtNtCs5UjBoGikVie_6cudarc5nvrtc6resultNtB4_10NvrtcErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt
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
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movq	%rdx, %r14
	movq	%rcx, %rdi
	movq	(%rdx), %rsi
	movq	8(%rdx), %r12
	movq	24(%r12), %r15
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1021(%rip), %rdx
	movl	$10, %r8d
	movq	%rsi, %rcx
	callq	*%r15
	movb	$1, %bl
	testb	%al, %al
	je	.LBB226_1
.LBB226_9:
	movl	%ebx, %eax
	.seh_startepilogue
	addq	$72, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r14
	popq	%r15
	.seh_endepilogue
	retq
.LBB226_1:
	testb	$-128, 18(%r14)
	jne	.LBB226_4
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.39.llvm.17490583796818522722(%rip), %rdx
	movl	$1, %r8d
	movq	%rsi, %rcx
	callq	*%r15
	testb	%al, %al
	jne	.LBB226_9
	movl	(%rdi), %eax
	leaq	switch.table._RNvXs_NtNtCs5UjBoGikVie_6cudarc5nvrtc6resultNtB4_10NvrtcErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt.70(%rip), %rcx
	movq	(%rcx,%rax,8), %r8
	leaq	switch.table._RNvXs_NtNtCs5UjBoGikVie_6cudarc5nvrtc6resultNtB4_10NvrtcErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt.71(%rip), %rcx
	movq	(%rcx,%rax,8), %rdx
	movq	%rsi, %rcx
	callq	*%r15
	testb	%al, %al
	jne	.LBB226_9
	jmp	.LBB226_8
.LBB226_4:
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.40.llvm.17490583796818522722(%rip), %rdx
	movl	$2, %r8d
	movq	%rsi, %rcx
	callq	*%r15
	testb	%al, %al
	jne	.LBB226_9
	movb	$1, 47(%rsp)
	movq	%rsi, 48(%rsp)
	movq	%r12, 56(%rsp)
	leaq	47(%rsp), %rax
	movq	%rax, 64(%rsp)
	movl	(%rdi), %eax
	leaq	switch.table._RNvXs_NtNtCs5UjBoGikVie_6cudarc5nvrtc6resultNtB4_10NvrtcErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt.70(%rip), %rcx
	movq	(%rcx,%rax,8), %r8
	leaq	switch.table._RNvXs_NtNtCs5UjBoGikVie_6cudarc5nvrtc6resultNtB4_10NvrtcErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt.71(%rip), %rcx
	movq	(%rcx,%rax,8), %rdx
	leaq	48(%rsp), %rcx
	callq	_RNvXs0_NtNtCs8xEFJqa6dYS_4core3fmt8buildersNtB5_10PadAdapterNtB7_5Write9write_str
	testb	%al, %al
	jne	.LBB226_9
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.38.llvm.17490583796818522722(%rip), %rdx
	leaq	48(%rsp), %rcx
	movl	$2, %r8d
	callq	_RNvXs0_NtNtCs8xEFJqa6dYS_4core3fmt8buildersNtB5_10PadAdapterNtB7_5Write9write_str
	testb	%al, %al
	jne	.LBB226_9
.LBB226_8:
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.57.llvm.17490583796818522722(%rip), %rdx
	movl	$1, %r8d
	movq	%rsi, %rcx
	callq	*%r15
	movl	%eax, %ebx
	jmp	.LBB226_9
.Lfunc_end226:
	.seh_endproc

	.def	_RNvXsb_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStreamNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXsb_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStreamNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop,unique,228
	.globl	_RNvXsb_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStreamNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop
	.p2align	4
_RNvXsb_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStreamNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop:
.Lfunc_begin227:
.seh_proc _RNvXsb_NtNtNtCs5UjBoGikVie_6cudarc6driver4safe4coreNtB5_10CudaStreamNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$48, %rsp
	.seh_stackalloc 48
	.seh_endprologue
	movq	%rcx, %rsi
	movq	(%rcx), %rdi
	xorl	%eax, %eax
	xchgl	%eax, 44(%rdi)
	testl	%eax, %eax
	jne	.LBB227_8
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB227_2
	leaq	40(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	je	.LBB227_4
.LBB227_8:
	movl	%eax, 44(%rdi)
.LBB227_9:
	movq	8(%rsi), %rcx
	movq	$0, 8(%rsi)
	testq	$-3, %rcx
	je	.LBB227_14
	movq	(%rsi), %rsi
	lock		decq	32(%rsi)
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuStreamDestroy_v22__S+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB227_11
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuStreamDestroy_v22__S(%rip)
	testl	%eax, %eax
	je	.LBB227_14
.LBB227_13:
	movl	%eax, 44(%rsi)
.LBB227_14:
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB227_2:
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB10_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvB10_15cuCtxGetCurrent0E0zEB14_.llvm.1750587498003715262
	leaq	40(%rsp), %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB227_8
.LBB227_4:
	movq	40(%rsp), %rax
	testq	%rax, %rax
	setne	%dl
	movq	16(%rdi), %rcx
	cmpq	%rcx, %rax
	sete	%al
	testb	%al, %dl
	jne	.LBB227_9
	movl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB227_6
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB227_8
	jmp	.LBB227_9
.LBB227_11:
	movq	%rcx, %rdi
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_18cuStreamDestroy_v20E0zEB13_
	movq	%rdi, %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuStreamDestroy_v22__S(%rip)
	testl	%eax, %eax
	jne	.LBB227_13
	jmp	.LBB227_14
.LBB227_6:
	movq	%rcx, %rbx
	callq	_RINvMNtNtCse0R8cuyqEa_3std4sync9once_lockINtB3_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtBZ_14cudaError_enumE10initializeNCINvB2_11get_or_initNCNvBZ_15cuCtxSetCurrent0E0zEB13_.llvm.1750587498003715262
	movq	%rbx, %rcx
	callq	*_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262(%rip)
	testl	%eax, %eax
	jne	.LBB227_8
	jmp	.LBB227_9
.Lfunc_end227:
	.seh_endproc

	.def	_RNvXsfq_NtNtCs5UjBoGikVie_6cudarc6driver3sysNtB6_14cudaError_enumNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXsfq_NtNtCs5UjBoGikVie_6cudarc6driver3sysNtB6_14cudaError_enumNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt,unique,229
	.p2align	4
_RNvXsfq_NtNtCs5UjBoGikVie_6cudarc6driver3sysNtB6_14cudaError_enumNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt:
.Lfunc_begin228:
	movl	(%rcx), %eax
	cmpq	$915, %rax
	ja	.LBB228_99
	leaq	.LJTI228_0(%rip), %rcx
	movslq	(%rcx,%rax,4), %rax
	addq	%rcx, %rax
	jmpq	*%rax
.LBB228_2:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1022(%rip), %rax
	movl	$12, %r8d
	jmp	.LBB228_101
.LBB228_86:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1105(%rip), %rax
	movl	$35, %r8d
	jmp	.LBB228_101
.LBB228_94:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1113(%rip), %rax
	movl	$26, %r8d
	jmp	.LBB228_101
.LBB228_82:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1101(%rip), %rax
	movl	$31, %r8d
	jmp	.LBB228_101
.LBB228_73:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1092(%rip), %rax
	movl	$33, %r8d
	jmp	.LBB228_101
.LBB228_80:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1099(%rip), %rax
	movl	$32, %r8d
	jmp	.LBB228_101
.LBB228_96:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1115(%rip), %rax
	movl	$30, %r8d
	jmp	.LBB228_101
.LBB228_91:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1110(%rip), %rax
	movl	$38, %r8d
	jmp	.LBB228_101
.LBB228_40:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1059(%rip), %rax
	movl	$35, %r8d
	jmp	.LBB228_101
.LBB228_50:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1069(%rip), %rax
	movl	$20, %r8d
	jmp	.LBB228_101
.LBB228_39:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1058(%rip), %rax
	movl	$36, %r8d
	jmp	.LBB228_101
.LBB228_69:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1088(%rip), %rax
	movl	$39, %r8d
	jmp	.LBB228_101
.LBB228_83:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1102(%rip), %rax
	movl	$37, %r8d
	jmp	.LBB228_101
.LBB228_74:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1093(%rip), %rax
	movl	$41, %r8d
	jmp	.LBB228_101
.LBB228_56:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1075(%rip), %rax
	movl	$34, %r8d
	jmp	.LBB228_101
.LBB228_59:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1078(%rip), %rax
	movl	$17, %r8d
	jmp	.LBB228_101
.LBB228_78:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1097(%rip), %rax
	movl	$34, %r8d
	jmp	.LBB228_101
.LBB228_37:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1056(%rip), %rax
	movl	$34, %r8d
	jmp	.LBB228_101
.LBB228_72:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1091(%rip), %rax
	movl	$27, %r8d
	jmp	.LBB228_101
.LBB228_36:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1055(%rip), %rax
	movl	$33, %r8d
	jmp	.LBB228_101
.LBB228_47:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1066(%rip), %rax
	movl	$24, %r8d
	jmp	.LBB228_101
.LBB228_70:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1089(%rip), %rax
	movl	$24, %r8d
	jmp	.LBB228_101
.LBB228_51:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1070(%rip), %rax
	movl	$26, %r8d
	jmp	.LBB228_101
.LBB228_28:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1047(%rip), %rax
	movl	$32, %r8d
	jmp	.LBB228_101
.LBB228_18:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1037(%rip), %rax
	movl	$26, %r8d
	jmp	.LBB228_101
.LBB228_27:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1046(%rip), %rax
	movl	$30, %r8d
	jmp	.LBB228_101
.LBB228_43:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1062(%rip), %rax
	movl	$41, %r8d
	jmp	.LBB228_101
.LBB228_61:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1080(%rip), %rax
	movl	$41, %r8d
	jmp	.LBB228_101
.LBB228_16:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1035(%rip), %rax
	movl	$30, %r8d
	jmp	.LBB228_101
.LBB228_85:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1104(%rip), %rax
	movl	$31, %r8d
	jmp	.LBB228_101
.LBB228_52:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1071(%rip), %rax
	movl	$34, %r8d
	jmp	.LBB228_101
.LBB228_20:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1039(%rip), %rax
	movl	$21, %r8d
	jmp	.LBB228_101
.LBB228_84:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1103(%rip), %rax
	movl	$37, %r8d
	jmp	.LBB228_101
.LBB228_23:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1042(%rip), %rax
	movl	$25, %r8d
	jmp	.LBB228_101
.LBB228_63:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1082(%rip), %rax
	movl	$31, %r8d
	jmp	.LBB228_101
.LBB228_7:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1026(%rip), %rax
	movl	$24, %r8d
	jmp	.LBB228_101
.LBB228_24:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1043(%rip), %rax
	movl	$28, %r8d
	jmp	.LBB228_101
.LBB228_67:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1086(%rip), %rax
	movl	$21, %r8d
	jmp	.LBB228_101
.LBB228_34:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1053(%rip), %rax
	movl	$35, %r8d
	jmp	.LBB228_101
.LBB228_21:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1040(%rip), %rax
	movl	$23, %r8d
	jmp	.LBB228_101
.LBB228_12:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1031(%rip), %rax
	movl	$23, %r8d
	jmp	.LBB228_101
.LBB228_5:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1024(%rip), %rax
	movl	$24, %r8d
	jmp	.LBB228_101
.LBB228_44:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1063(%rip), %rax
	movl	$36, %r8d
	jmp	.LBB228_101
.LBB228_66:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1085(%rip), %rax
	movl	$32, %r8d
	jmp	.LBB228_101
.LBB228_33:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1052(%rip), %rax
	movl	$22, %r8d
	jmp	.LBB228_101
.LBB228_35:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1054(%rip), %rax
	movl	$31, %r8d
	jmp	.LBB228_101
.LBB228_6:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1025(%rip), %rax
	movl	$26, %r8d
	jmp	.LBB228_101
.LBB228_10:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1029(%rip), %rax
	movl	$35, %r8d
	jmp	.LBB228_101
.LBB228_14:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1033(%rip), %rax
	movl	$20, %r8d
	jmp	.LBB228_101
.LBB228_4:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1023(%rip), %rax
	movl	$24, %r8d
	jmp	.LBB228_101
.LBB228_95:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1114(%rip), %rax
	movl	$31, %r8d
	jmp	.LBB228_101
.LBB228_79:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1098(%rip), %rax
	movl	$38, %r8d
	jmp	.LBB228_101
.LBB228_64:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1083(%rip), %rax
	movl	$30, %r8d
	jmp	.LBB228_101
.LBB228_68:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1087(%rip), %rax
	movl	$24, %r8d
	jmp	.LBB228_101
.LBB228_65:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1084(%rip), %rax
	movl	$29, %r8d
	jmp	.LBB228_101
.LBB228_25:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1044(%rip), %rax
	movl	$27, %r8d
	jmp	.LBB228_101
.LBB228_8:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1027(%rip), %rax
	movl	$28, %r8d
	jmp	.LBB228_101
.LBB228_17:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1036(%rip), %rax
	movl	$24, %r8d
	jmp	.LBB228_101
.LBB228_97:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1116(%rip), %rax
	movl	$32, %r8d
	jmp	.LBB228_101
.LBB228_9:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1028(%rip), %rax
	movl	$35, %r8d
	jmp	.LBB228_101
.LBB228_11:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1030(%rip), %rax
	movl	$35, %r8d
	jmp	.LBB228_101
.LBB228_22:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1041(%rip), %rax
	movl	$26, %r8d
	jmp	.LBB228_101
.LBB228_19:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1038(%rip), %rax
	movl	$34, %r8d
	jmp	.LBB228_101
.LBB228_48:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1067(%rip), %rax
	movl	$22, %r8d
	jmp	.LBB228_101
.LBB228_26:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1045(%rip), %rax
	movl	$21, %r8d
	jmp	.LBB228_101
.LBB228_15:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1034(%rip), %rax
	movl	$25, %r8d
	jmp	.LBB228_101
.LBB228_13:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1032(%rip), %rax
	movl	$29, %r8d
	jmp	.LBB228_101
.LBB228_31:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1050(%rip), %rax
	movl	$33, %r8d
	jmp	.LBB228_101
.LBB228_42:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1061(%rip), %rax
	movl	$25, %r8d
	jmp	.LBB228_101
.LBB228_45:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1064(%rip), %rax
	movl	$27, %r8d
	jmp	.LBB228_101
.LBB228_32:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1051(%rip), %rax
	movl	$34, %r8d
	jmp	.LBB228_101
.LBB228_88:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1107(%rip), %rax
	movl	$35, %r8d
	jmp	.LBB228_101
.LBB228_89:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1108(%rip), %rax
	movl	$34, %r8d
	jmp	.LBB228_101
.LBB228_29:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1048(%rip), %rax
	movl	$28, %r8d
	jmp	.LBB228_101
.LBB228_60:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1079(%rip), %rax
	movl	$25, %r8d
	jmp	.LBB228_101
.LBB228_62:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1081(%rip), %rax
	movl	$37, %r8d
	jmp	.LBB228_101
.LBB228_41:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1060(%rip), %rax
	movl	$25, %r8d
	jmp	.LBB228_101
.LBB228_57:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1076(%rip), %rax
	movl	$33, %r8d
	jmp	.LBB228_101
.LBB228_30:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1049(%rip), %rax
	movl	$28, %r8d
	jmp	.LBB228_101
.LBB228_75:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1094(%rip), %rax
	movl	$32, %r8d
	jmp	.LBB228_101
.LBB228_58:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1077(%rip), %rax
	movl	$31, %r8d
	jmp	.LBB228_101
.LBB228_38:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1057(%rip), %rax
	movl	$35, %r8d
	jmp	.LBB228_101
.LBB228_49:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1068(%rip), %rax
	movl	$20, %r8d
	jmp	.LBB228_101
.LBB228_55:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1074(%rip), %rax
	movl	$38, %r8d
	jmp	.LBB228_101
.LBB228_76:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1095(%rip), %rax
	movl	$26, %r8d
	jmp	.LBB228_101
.LBB228_46:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1065(%rip), %rax
	movl	$25, %r8d
	jmp	.LBB228_101
.LBB228_77:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1096(%rip), %rax
	movl	$31, %r8d
	jmp	.LBB228_101
.LBB228_54:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1073(%rip), %rax
	movl	$40, %r8d
	jmp	.LBB228_101
.LBB228_90:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1109(%rip), %rax
	movl	$25, %r8d
	jmp	.LBB228_101
.LBB228_81:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1100(%rip), %rax
	movl	$28, %r8d
	jmp	.LBB228_101
.LBB228_53:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1072(%rip), %rax
	movl	$25, %r8d
	jmp	.LBB228_101
.LBB228_71:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1090(%rip), %rax
	movl	$24, %r8d
	jmp	.LBB228_101
.LBB228_98:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1117(%rip), %rax
	movl	$41, %r8d
	jmp	.LBB228_101
.LBB228_93:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1112(%rip), %rax
	movl	$36, %r8d
	jmp	.LBB228_101
.LBB228_92:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1111(%rip), %rax
	jmp	.LBB228_100
.LBB228_87:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1106(%rip), %rax
	movl	$34, %r8d
	jmp	.LBB228_101
.LBB228_99:
	leaq	anon.a7c37e6ade312d68d4d78ed2f53518c1.1118(%rip), %rax
.LBB228_100:
	movl	$18, %r8d
.LBB228_101:
	movq	(%rdx), %rcx
	movq	8(%rdx), %rdx
	movq	24(%rdx), %r9
	movq	%rax, %rdx
	rex64 jmpq	*%r9
.LBB228_3:
	ud2
.Lfunc_end228:
	.section	.rdata,"dr",associative,_RNvXsfq_NtNtCs5UjBoGikVie_6cudarc6driver3sysNtB6_14cudaError_enumNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt,unique,230
	.p2align	2, 0x0
.LJTI228_0:
	.long	.LBB228_2-.LJTI228_0
	.long	.LBB228_4-.LJTI228_0
	.long	.LBB228_5-.LJTI228_0
	.long	.LBB228_6-.LJTI228_0
	.long	.LBB228_7-.LJTI228_0
	.long	.LBB228_8-.LJTI228_0
	.long	.LBB228_9-.LJTI228_0
	.long	.LBB228_10-.LJTI228_0
	.long	.LBB228_11-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_12-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_13-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_14-.LJTI228_0
	.long	.LBB228_15-.LJTI228_0
	.long	.LBB228_16-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_17-.LJTI228_0
	.long	.LBB228_18-.LJTI228_0
	.long	.LBB228_19-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_20-.LJTI228_0
	.long	.LBB228_21-.LJTI228_0
	.long	.LBB228_22-.LJTI228_0
	.long	.LBB228_23-.LJTI228_0
	.long	.LBB228_24-.LJTI228_0
	.long	.LBB228_25-.LJTI228_0
	.long	.LBB228_26-.LJTI228_0
	.long	.LBB228_27-.LJTI228_0
	.long	.LBB228_28-.LJTI228_0
	.long	.LBB228_29-.LJTI228_0
	.long	.LBB228_30-.LJTI228_0
	.long	.LBB228_31-.LJTI228_0
	.long	.LBB228_32-.LJTI228_0
	.long	.LBB228_33-.LJTI228_0
	.long	.LBB228_34-.LJTI228_0
	.long	.LBB228_35-.LJTI228_0
	.long	.LBB228_36-.LJTI228_0
	.long	.LBB228_37-.LJTI228_0
	.long	.LBB228_38-.LJTI228_0
	.long	.LBB228_39-.LJTI228_0
	.long	.LBB228_40-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_41-.LJTI228_0
	.long	.LBB228_42-.LJTI228_0
	.long	.LBB228_43-.LJTI228_0
	.long	.LBB228_44-.LJTI228_0
	.long	.LBB228_45-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_46-.LJTI228_0
	.long	.LBB228_47-.LJTI228_0
	.long	.LBB228_48-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_49-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_50-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_51-.LJTI228_0
	.long	.LBB228_52-.LJTI228_0
	.long	.LBB228_53-.LJTI228_0
	.long	.LBB228_54-.LJTI228_0
	.long	.LBB228_55-.LJTI228_0
	.long	.LBB228_56-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_57-.LJTI228_0
	.long	.LBB228_58-.LJTI228_0
	.long	.LBB228_59-.LJTI228_0
	.long	.LBB228_60-.LJTI228_0
	.long	.LBB228_61-.LJTI228_0
	.long	.LBB228_62-.LJTI228_0
	.long	.LBB228_63-.LJTI228_0
	.long	.LBB228_64-.LJTI228_0
	.long	.LBB228_65-.LJTI228_0
	.long	.LBB228_66-.LJTI228_0
	.long	.LBB228_67-.LJTI228_0
	.long	.LBB228_68-.LJTI228_0
	.long	.LBB228_69-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_70-.LJTI228_0
	.long	.LBB228_71-.LJTI228_0
	.long	.LBB228_72-.LJTI228_0
	.long	.LBB228_73-.LJTI228_0
	.long	.LBB228_74-.LJTI228_0
	.long	.LBB228_75-.LJTI228_0
	.long	.LBB228_76-.LJTI228_0
	.long	.LBB228_77-.LJTI228_0
	.long	.LBB228_78-.LJTI228_0
	.long	.LBB228_79-.LJTI228_0
	.long	.LBB228_80-.LJTI228_0
	.long	.LBB228_81-.LJTI228_0
	.long	.LBB228_82-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_3-.LJTI228_0
	.long	.LBB228_83-.LJTI228_0
	.long	.LBB228_84-.LJTI228_0
	.long	.LBB228_85-.LJTI228_0
	.long	.LBB228_86-.LJTI228_0
	.long	.LBB228_87-.LJTI228_0
	.long	.LBB228_88-.LJTI228_0
	.long	.LBB228_89-.LJTI228_0
	.long	.LBB228_90-.LJTI228_0
	.long	.LBB228_91-.LJTI228_0
	.long	.LBB228_92-.LJTI228_0
	.long	.LBB228_93-.LJTI228_0
	.long	.LBB228_94-.LJTI228_0
	.long	.LBB228_95-.LJTI228_0
	.long	.LBB228_96-.LJTI228_0
	.long	.LBB228_97-.LJTI228_0
	.long	.LBB228_98-.LJTI228_0

	.def	_RNvXsq_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXsq_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt,unique,231
	.p2align	4
_RNvXsq_NtCsfQUUnEvlYZE_5alloc6stringNtB5_6StringNtNtCs8xEFJqa6dYS_4core3fmt7Display3fmt:
.Lfunc_begin229:
	movq	%rdx, %rax
	movq	8(%rcx), %rdx
	movq	16(%rcx), %r8
	movq	%rax, %rcx
	jmp	_RNvMsa_NtCs8xEFJqa6dYS_4core3fmtNtB5_9Formatter3pad
.Lfunc_end229:

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.0,unique,232
anon.a7c37e6ade312d68d4d78ed2f53518c1.0:
	.asciz	" Unable to dynamically load the \"\300/\" shared library - searched for library names: \300\200\320\000. Ensure that `LD_LIBRARY_PATH` has the correct path to the installed library. If the shared library is present on the system under a different name than one of those listed above, please open a GitHub issue."

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1,unique,233
anon.a7c37e6ade312d68d4d78ed2f53518c1.1:
	.asciz	"C:\\Users\\there\\.cargo\\registry\\src\\index.crates.io-1949cf8c6b5b557f\\cudarc-0.19.7\\src\\lib.rs"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.2,unique,234
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.2:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.1
	.asciz	"\\\000\000\000\000\000\000\000\310\000\000\000\005\000\000"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.4.llvm.1750587498003715262,unique,235
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.4.llvm.1750587498003715262
anon.a7c37e6ade312d68d4d78ed2f53518c1.4.llvm.1750587498003715262:
	.asciz	"/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\std\\src\\sync\\once.rs"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262,unique,236
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.4.llvm.1750587498003715262
	.asciz	"L\000\000\000\000\000\000\000\342\000\000\000\024\000\000"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.7,unique,237
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.7:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_16cuCtxSynchronize0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_16cuCtxSynchronize0E0zE0E0B1Q_

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.12,unique,238
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.12:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCNtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumOPaEB1O_E10initializeNCINvB1e_11get_or_initNCNvB1Q_16cuGetErrorString0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1U_
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCNtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumOPaEB1J_E10initializeNCINvB19_11get_or_initNCNvB1L_16cuGetErrorString0E0zE0E0B1P_

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.21.llvm.1750587498003715262,unique,239
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.21.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.21.llvm.1750587498003715262:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB2q_13cuMemFreeHost0E0zE0E0INtNtNtB1T_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB2u_.llvm.1750587498003715262
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB2l_13cuMemFreeHost0E0zE0E0B2p_.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.32.llvm.1750587498003715262,unique,240
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.32.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.32.llvm.1750587498003715262:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB2s_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB2s_20cuMemcpyDtoHAsync_v20E0zE0E0INtNtNtB1T_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB2w_.llvm.1750587498003715262
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtCs8xEFJqa6dYS_4core3ffi6c_voidyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB2n_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB2n_20cuMemcpyDtoHAsync_v20E0zE0E0B2r_.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.33,unique,241
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.33:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtB1R_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1R_11nvrtcGetPTX0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtB1M_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1M_11nvrtcGetPTX0E0zE0E0B1Q_

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.37,unique,242
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.37:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtB1R_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1R_18nvrtcGetProgramLog0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOaENtB1M_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1M_18nvrtcGetProgramLog0E0zE0E0B1Q_

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.38,unique,243
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.38:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtB1R_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1R_15nvrtcGetPTXSize0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtB1M_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1M_15nvrtcGetPTXSize0E0zE0E0B1Q_

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.42,unique,244
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.42:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtB1R_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1R_22nvrtcGetProgramLogSize0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramOjENtB1M_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1M_22nvrtcGetProgramLogSize0E0zE0E0B1Q_

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.45,unique,245
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.45:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramlPPaENtB1R_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1R_19nvrtcCompileProgram0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramlPPaENtB1M_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1M_19nvrtcCompileProgram0E0zE0E0B1Q_

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.52.llvm.1750587498003715262,unique,246
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.52.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.52.llvm.1750587498003715262:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_17cuEventDestroy_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_17cuEventDestroy_v20E0zE0E0B1Q_.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.54.llvm.1750587498003715262,unique,247
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.54.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.54.llvm.1750587498003715262:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stONtB1R_11CUstream_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_13cuEventRecord0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stONtB1M_11CUstream_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_13cuEventRecord0E0zE0E0B1Q_.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.56.llvm.1750587498003715262,unique,248
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.56.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.56.llvm.1750587498003715262:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUgraph_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_14cuGraphDestroy0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUgraph_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_14cuGraphDestroy0E0zE0E0B1Q_.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.70,unique,249
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.70:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_18cuStreamDestroy_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_18cuStreamDestroy_v20E0zE0E0B1Q_

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.71.llvm.1750587498003715262,unique,250
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.71.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.71.llvm.1750587498003715262:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_19cuStreamSynchronize0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_19cuStreamSynchronize0E0zE0E0B1Q_.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.76.llvm.1750587498003715262,unique,251
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.76.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.76.llvm.1750587498003715262:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stNtB1R_24CUstreamCaptureMode_enumENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_23cuStreamBeginCapture_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stNtB1M_24CUstreamCaptureMode_enumENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_23cuStreamBeginCapture_v20E0zE0E0B1Q_.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.77.llvm.1750587498003715262,unique,252
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.77.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.77.llvm.1750587498003715262:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stONtB1R_10CUevent_stmENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_17cuStreamWaitEvent0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stONtB1M_10CUevent_stmENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_17cuStreamWaitEvent0E0zE0E0B1Q_.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.82,unique,253
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.82:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stOONtB1R_10CUgraph_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_18cuStreamEndCapture0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stOONtB1M_10CUgraph_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_18cuStreamEndCapture0E0zE0E0B1Q_

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.117.llvm.1750587498003715262,unique,254
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.117.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.117.llvm.1750587498003715262:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_18cuGraphExecDestroy0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_18cuGraphExecDestroy0E0zE0E0B1Q_.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.119.llvm.1750587498003715262,unique,255
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.119.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.119.llvm.1750587498003715262:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB1R_11CUstream_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_13cuGraphLaunch0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB1M_11CUstream_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_13cuGraphLaunch0E0zE0E0B1Q_.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.213,unique,256
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.213:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_15cuCtxDestroy_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_15cuCtxDestroy_v20E0zE0E0B1Q_

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.214.llvm.1750587498003715262,unique,257
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.214.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.214.llvm.1750587498003715262:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_15cuCtxSetCurrent0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_15cuCtxSetCurrent0E0zE0E0B1Q_.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.224.llvm.1750587498003715262,unique,258
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.224.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.224.llvm.1750587498003715262:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_14cuModuleUnload0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_14cuModuleUnload0E0zE0E0B1Q_.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.240.llvm.1750587498003715262,unique,259
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.240.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.240.llvm.1750587498003715262:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stmmmmmmmONtB1R_11CUstream_stOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidB32_ENtB1R_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1R_14cuLaunchKernel0E0zE0E0INtNtNtB38_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1V_.llvm.1750587498003715262
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stmmmmmmmONtB1M_11CUstream_stOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidB2X_ENtB1M_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1M_14cuLaunchKernel0E0zE0E0B1Q_.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.249.llvm.1750587498003715262,unique,260
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.249.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.249.llvm.1750587498003715262:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidjmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB2t_14cuMemHostAlloc0E0zE0E0INtNtNtB1U_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB2x_.llvm.1750587498003715262
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtCs8xEFJqa6dYS_4core3ffi6c_voidjmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB2o_14cuMemHostAlloc0E0zE0E0B2s_.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.250,unique,261
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.250:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramENtB1S_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1S_19nvrtcDestroyProgram0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramENtB1N_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1N_19nvrtcDestroyProgram0E0zE0E0B1R_

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.251.llvm.1750587498003715262,unique,262
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.251.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.251.llvm.1750587498003715262:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramPaB2H_lPB2H_B2O_ENtB1S_11nvrtcResultE10initializeNCINvB1e_11get_or_initNCNvB1S_18nvrtcCreateProgram0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys13__nvrtcProgramPaB2C_lPB2C_B2J_ENtB1N_11nvrtcResultE10initializeNCINvB19_11get_or_initNCNvB1N_18nvrtcCreateProgram0E0zE0E0B1R_.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.260.llvm.1750587498003715262,unique,263
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.260.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.260.llvm.1750587498003715262:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stmENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_13cuEventCreate0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys10CUevent_stmENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_13cuEventCreate0E0zE0E0B1R_.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.264,unique,264
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.264:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stmENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_14cuStreamCreate0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stmENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_14cuStreamCreate0E0zE0E0B1R_

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.272,unique,265
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.272:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB1S_10CUgraph_styENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_27cuGraphInstantiateWithFlags0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys14CUgraphExec_stONtB1N_10CUgraph_styENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_27cuGraphInstantiateWithFlags0E0zE0E0B1R_

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.300.llvm.1750587498003715262,unique,266
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.300.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.300.llvm.1750587498003715262:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_15cuCtxGetCurrent0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_15cuCtxGetCurrent0E0zE0E0B1R_.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.305,unique,267
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.305:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stlENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_24cuDevicePrimaryCtxRetain0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_stlENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_24cuDevicePrimaryCtxRetain0E0zE0E0B1R_

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.313,unique,268
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.313:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_16cuModuleLoadData0E0zE0E0INtNtNtB2G_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_16cuModuleLoadData0E0zE0E0B1R_

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.316,unique,269
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.316:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPaENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_12cuModuleLoad0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUmod_stPaENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_12cuModuleLoad0E0zE0E0B1R_

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.317.llvm.1750587498003715262,unique,270
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.317.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.317.llvm.1750587498003715262:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stONtB1S_8CUmod_stPaENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_19cuModuleGetFunction0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOONtNtNtCs5UjBoGikVie_6cudarc6driver3sys9CUfunc_stONtB1N_8CUmod_stPaENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_19cuModuleGetFunction0E0zE0E0B1R_.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.350.llvm.1750587498003715262,unique,271
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.350.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.350.llvm.1750587498003715262:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOlNtNtNtCs5UjBoGikVie_6cudarc6driver3sys23CUdevice_attribute_enumlENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_20cuDeviceGetAttribute0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOlNtNtNtCs5UjBoGikVie_6cudarc6driver3sys23CUdevice_attribute_enumlENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_20cuDeviceGetAttribute0E0zE0E0B1R_.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.361,unique,272
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.361:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOllENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_11cuDeviceGet0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOllENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_11cuDeviceGet0E0zE0E0B1T_

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.386.llvm.1750587498003715262,unique,273
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.386.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.386.llvm.1750587498003715262:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOyjENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_13cuMemAlloc_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_.llvm.1750587498003715262
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOyjENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_13cuMemAlloc_v20E0zE0E0B1T_.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.387.llvm.1750587498003715262,unique,274
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.387.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.387.llvm.1750587498003715262:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCOyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1U_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_15cuMemAllocAsync0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_.llvm.1750587498003715262
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCOyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1P_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_15cuMemAllocAsync0E0zE0E0B1T_.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.407,unique,275
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.407:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKClENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_28cuDevicePrimaryCtxRelease_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKClENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_28cuDevicePrimaryCtxRelease_v20E0zE0E0B1R_

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.417,unique,276
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.417:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_6cuInit0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCmENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_6cuInit0E0zE0E0B1R_

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.422.llvm.1750587498003715262,unique,277
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.422.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.422.llvm.1750587498003715262:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_12cuMemFree_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyENtNtNtCs5UjBoGikVie_6cudarc6driver3sys14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_12cuMemFree_v20E0zE0E0B1R_.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.428.llvm.1750587498003715262,unique,278
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.428.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.428.llvm.1750587498003715262:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_14cuMemFreeAsync0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_14cuMemFreeAsync0E0zE0E0B1R_.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.430.llvm.1750587498003715262,unique,279
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.430.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.430.llvm.1750587498003715262:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_styB1P_jONtB1S_11CUstream_stENtB1S_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1S_17cuMemcpyPeerAsync0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1W_.llvm.1750587498003715262
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyONtNtNtCs5UjBoGikVie_6cudarc6driver3sys8CUctx_styB1K_jONtB1N_11CUstream_stENtB1N_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1N_17cuMemcpyPeerAsync0E0zE0E0B1R_.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.432.llvm.1750587498003715262,unique,280
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.432.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.432.llvm.1750587498003715262:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB2s_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB2s_20cuMemcpyHtoDAsync_v20E0zE0E0INtNtNtB1U_3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB2w_.llvm.1750587498003715262
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyPNtNtCs8xEFJqa6dYS_4core3ffi6c_voidjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB2n_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB2n_20cuMemcpyHtoDAsync_v20E0zE0E0B2r_.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.434.llvm.1750587498003715262,unique,281
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.434.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.434.llvm.1750587498003715262:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyhjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1U_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_15cuMemsetD8Async0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_.llvm.1750587498003715262
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyhjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1P_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_15cuMemsetD8Async0E0zE0E0B1T_.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.460.llvm.1750587498003715262,unique,282
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.460.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.460.llvm.1750587498003715262:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockFUKCyyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1U_14cudaError_enumE10initializeNCINvB1e_11get_or_initNCNvB1U_20cuMemcpyDtoDAsync_v20E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB1Y_.llvm.1750587498003715262
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockFUKCyyjONtNtNtCs5UjBoGikVie_6cudarc6driver3sys11CUstream_stENtB1P_14cudaError_enumE10initializeNCINvB19_11get_or_initNCNvB1P_20cuMemcpyDtoDAsync_v20E0zE0E0B1T_.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.461,unique,283
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.461:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB1e_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB38_
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib0E0zE0E0B33_

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.462,unique,284
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.462:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once15call_once_forceNCINvMNtBf_9once_lockINtB1f_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB1e_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB38_
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once15call_once_forceNCINvMNtBa_9once_lockINtB1a_8OnceLockNtNtCskIq6Fm6qntW_10libloading4safe7LibraryE10initializeNCINvB19_11get_or_initNCNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib0E0zE0E0B33_

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.465,unique,285
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.465:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.4.llvm.1750587498003715262
	.asciz	"L\000\000\000\000\000\000\000\342\000\000\0001\000\000"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.466,unique,286
anon.a7c37e6ade312d68d4d78ed2f53518c1.466:
	.asciz	"\017Missing symbol \300\002: \300"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.467,unique,287
anon.a7c37e6ade312d68d4d78ed2f53518c1.467:
	.asciz	"C:\\Users\\there\\.cargo\\registry\\src\\index.crates.io-1949cf8c6b5b557f\\cudarc-0.19.7\\src\\nvrtc\\sys\\mod.rs"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.468,unique,288
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.468:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.467
	.asciz	"f\000\000\000\000\000\000\000\f\000\000\000D\000\000"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.469,unique,289
anon.a7c37e6ade312d68d4d78ed2f53518c1.469:
	.asciz	"C:\\Users\\there\\.cargo\\registry\\src\\index.crates.io-1949cf8c6b5b557f\\cudarc-0.19.7\\src\\nvrtc\\result.rs"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.470,unique,290
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.470:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.469
	.asciz	"e\000\000\000\000\000\000\000W\000\000\000\"\000\000"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.471,unique,291
anon.a7c37e6ade312d68d4d78ed2f53518c1.471:
	.asciz	"C:\\Users\\there\\.cargo\\registry\\src\\index.crates.io-1949cf8c6b5b557f\\cudarc-0.19.7\\src\\driver\\sys\\mod.rs"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.472,unique,292
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.472:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.471
	.asciz	"g\000\000\000\000\000\000\000\f\000\000\000D\000\000"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.474,unique,293
anon.a7c37e6ade312d68d4d78ed2f53518c1.474:
	.asciz	"C:\\Users\\there\\.cargo\\registry\\src\\index.crates.io-1949cf8c6b5b557f\\cudarc-0.19.7\\src\\nvrtc\\safe.rs"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.475,unique,294
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.475:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.474
	.asciz	"c\000\000\000\000\000\000\000\230\000\000\000I\000\000"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.476,unique,295
anon.a7c37e6ade312d68d4d78ed2f53518c1.476:
	.ascii	"nvrtcGetPTX"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.481,unique,296
anon.a7c37e6ade312d68d4d78ed2f53518c1.481:
	.ascii	"nvrtcGetPTXSize"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.484,unique,297
anon.a7c37e6ade312d68d4d78ed2f53518c1.484:
	.ascii	"nvrtcCreateProgram"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.485,unique,298
anon.a7c37e6ade312d68d4d78ed2f53518c1.485:
	.ascii	"nvrtcGetProgramLog"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.486,unique,299
anon.a7c37e6ade312d68d4d78ed2f53518c1.486:
	.ascii	"nvrtcCompileProgram"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.487,unique,300
anon.a7c37e6ade312d68d4d78ed2f53518c1.487:
	.ascii	"nvrtcDestroyProgram"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.492,unique,301
anon.a7c37e6ade312d68d4d78ed2f53518c1.492:
	.ascii	"nvrtcGetProgramLogSize"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.495,unique,302
anon.a7c37e6ade312d68d4d78ed2f53518c1.495:
	.ascii	"nvrtc"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.501,unique,303
anon.a7c37e6ade312d68d4d78ed2f53518c1.501:
	.ascii	"cuDeviceGet"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.510,unique,304
anon.a7c37e6ade312d68d4d78ed2f53518c1.510:
	.ascii	"cuMemFree_v2"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.513,unique,305
anon.a7c37e6ade312d68d4d78ed2f53518c1.513:
	.ascii	"cuModuleLoad"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.518,unique,306
anon.a7c37e6ade312d68d4d78ed2f53518c1.518:
	.ascii	"cuEventCreate"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.519,unique,307
anon.a7c37e6ade312d68d4d78ed2f53518c1.519:
	.ascii	"cuEventRecord"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.522,unique,308
anon.a7c37e6ade312d68d4d78ed2f53518c1.522:
	.ascii	"cuGraphLaunch"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.525,unique,309
anon.a7c37e6ade312d68d4d78ed2f53518c1.525:
	.ascii	"cuMemAlloc_v2"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.526,unique,310
anon.a7c37e6ade312d68d4d78ed2f53518c1.526:
	.ascii	"cuMemFreeHost"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.542,unique,311
anon.a7c37e6ade312d68d4d78ed2f53518c1.542:
	.ascii	"cuGraphDestroy"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.543,unique,312
anon.a7c37e6ade312d68d4d78ed2f53518c1.543:
	.ascii	"cuLaunchKernel"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.546,unique,313
anon.a7c37e6ade312d68d4d78ed2f53518c1.546:
	.ascii	"cuMemFreeAsync"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.548,unique,314
anon.a7c37e6ade312d68d4d78ed2f53518c1.548:
	.ascii	"cuMemHostAlloc"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.553,unique,315
anon.a7c37e6ade312d68d4d78ed2f53518c1.553:
	.ascii	"cuModuleUnload"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.556,unique,316
anon.a7c37e6ade312d68d4d78ed2f53518c1.556:
	.ascii	"cuStreamCreate"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.560,unique,317
anon.a7c37e6ade312d68d4d78ed2f53518c1.560:
	.ascii	"cuCtxDestroy_v2"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.561,unique,318
anon.a7c37e6ade312d68d4d78ed2f53518c1.561:
	.ascii	"cuCtxGetCurrent"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.562,unique,319
anon.a7c37e6ade312d68d4d78ed2f53518c1.562:
	.ascii	"cuCtxSetCurrent"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.572,unique,320
anon.a7c37e6ade312d68d4d78ed2f53518c1.572:
	.ascii	"cuMemAllocAsync"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.585,unique,321
anon.a7c37e6ade312d68d4d78ed2f53518c1.585:
	.ascii	"cuMemsetD8Async"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.590,unique,322
anon.a7c37e6ade312d68d4d78ed2f53518c1.590:
	.ascii	"cuCtxSynchronize"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.592,unique,323
anon.a7c37e6ade312d68d4d78ed2f53518c1.592:
	.ascii	"cuGetErrorString"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.605,unique,324
anon.a7c37e6ade312d68d4d78ed2f53518c1.605:
	.ascii	"cuModuleLoadData"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.613,unique,325
anon.a7c37e6ade312d68d4d78ed2f53518c1.613:
	.ascii	"cuEventDestroy_v2"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.622,unique,326
anon.a7c37e6ade312d68d4d78ed2f53518c1.622:
	.ascii	"cuMemcpyPeerAsync"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.628,unique,327
anon.a7c37e6ade312d68d4d78ed2f53518c1.628:
	.ascii	"cuStreamWaitEvent"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.648,unique,328
anon.a7c37e6ade312d68d4d78ed2f53518c1.648:
	.ascii	"cuGraphExecDestroy"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.667,unique,329
anon.a7c37e6ade312d68d4d78ed2f53518c1.667:
	.ascii	"cuStreamDestroy_v2"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.668,unique,330
anon.a7c37e6ade312d68d4d78ed2f53518c1.668:
	.ascii	"cuStreamEndCapture"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.693,unique,331
anon.a7c37e6ade312d68d4d78ed2f53518c1.693:
	.ascii	"cuModuleGetFunction"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.699,unique,332
anon.a7c37e6ade312d68d4d78ed2f53518c1.699:
	.ascii	"cuStreamSynchronize"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.703,unique,333
anon.a7c37e6ade312d68d4d78ed2f53518c1.703:
	.ascii	"cuDeviceGetAttribute"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.717,unique,334
anon.a7c37e6ade312d68d4d78ed2f53518c1.717:
	.ascii	"cuMemcpyDtoDAsync_v2"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.718,unique,335
anon.a7c37e6ade312d68d4d78ed2f53518c1.718:
	.ascii	"cuMemcpyDtoHAsync_v2"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.720,unique,336
anon.a7c37e6ade312d68d4d78ed2f53518c1.720:
	.ascii	"cuMemcpyHtoDAsync_v2"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.788,unique,337
anon.a7c37e6ade312d68d4d78ed2f53518c1.788:
	.ascii	"cuStreamBeginCapture_v2"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.793,unique,338
anon.a7c37e6ade312d68d4d78ed2f53518c1.793:
	.ascii	"cuDevicePrimaryCtxRetain"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.842,unique,339
anon.a7c37e6ade312d68d4d78ed2f53518c1.842:
	.ascii	"cuGraphInstantiateWithFlags"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.856,unique,340
anon.a7c37e6ade312d68d4d78ed2f53518c1.856:
	.ascii	"cuDevicePrimaryCtxRelease_v2"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.929,unique,341
anon.a7c37e6ade312d68d4d78ed2f53518c1.929:
	.ascii	"cuda"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.930,unique,342
anon.a7c37e6ade312d68d4d78ed2f53518c1.930:
	.ascii	"nvcuda"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.931,unique,343
anon.a7c37e6ade312d68d4d78ed2f53518c1.931:
	.ascii	"cuInit"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.935,unique,344
anon.a7c37e6ade312d68d4d78ed2f53518c1.935:
	.ascii	"64"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.936,unique,345
anon.a7c37e6ade312d68d4d78ed2f53518c1.936:
	.ascii	"12"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.937,unique,346
anon.a7c37e6ade312d68d4d78ed2f53518c1.937:
	.byte	54

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.938,unique,347
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.938:
	.quad	1
	.zero	8

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.939,unique,348
anon.a7c37e6ade312d68d4d78ed2f53518c1.939:
	.ascii	".dll"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.940,unique,349
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.940:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.939
	.asciz	"\004\000\000\000\000\000\000"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.941,unique,350
anon.a7c37e6ade312d68d4d78ed2f53518c1.941:
	.asciz	"\300\300\300"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.942,unique,351
anon.a7c37e6ade312d68d4d78ed2f53518c1.942:
	.asciz	"\300\300\300\300"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.943,unique,352
anon.a7c37e6ade312d68d4d78ed2f53518c1.943:
	.asciz	"\300\300\300\001_\300\300"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.944,unique,353
anon.a7c37e6ade312d68d4d78ed2f53518c1.944:
	.asciz	"\300\300\300\001_\300\300\300"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.945,unique,354
anon.a7c37e6ade312d68d4d78ed2f53518c1.945:
	.asciz	"\300\300\300\001_\300\300\002_0\300"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.946,unique,355
anon.a7c37e6ade312d68d4d78ed2f53518c1.946:
	.asciz	"\300\300\300\001_\300\0020_\300\300"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.947,unique,356
anon.a7c37e6ade312d68d4d78ed2f53518c1.947:
	.asciz	"\300\300\300\003_10\300"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.948,unique,357
anon.a7c37e6ade312d68d4d78ed2f53518c1.948:
	.asciz	"\300\300\300\003_11\300"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.949,unique,358
anon.a7c37e6ade312d68d4d78ed2f53518c1.949:
	.asciz	"\300\300\300\003_12\300"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.950,unique,359
anon.a7c37e6ade312d68d4d78ed2f53518c1.950:
	.asciz	"\300\300\300\001_\300\0030_0\300"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.951,unique,360
anon.a7c37e6ade312d68d4d78ed2f53518c1.951:
	.asciz	"\300\300\300\002_9\300"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.952,unique,361
anon.a7c37e6ade312d68d4d78ed2f53518c1.952:
	.asciz	"\300\300\300\001.\300"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.953,unique,362
anon.a7c37e6ade312d68d4d78ed2f53518c1.953:
	.asciz	"\300\300\300\003.12"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.954,unique,363
anon.a7c37e6ade312d68d4d78ed2f53518c1.954:
	.asciz	"\300\300\300\003.11"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.955,unique,364
anon.a7c37e6ade312d68d4d78ed2f53518c1.955:
	.asciz	"\300\300\300\003.10"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.956,unique,365
anon.a7c37e6ade312d68d4d78ed2f53518c1.956:
	.asciz	"\300\300\300\002.9"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.957,unique,366
anon.a7c37e6ade312d68d4d78ed2f53518c1.957:
	.asciz	"\300\300\300\002.1"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.958,unique,367
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.958:
	.asciz	"\000\000\000\000\000\000\000\000\004\000\000\000\000\000\000\000\004\000\000\000\000\000\000"
	.quad	_RNvXs_NtNtCs5UjBoGikVie_6cudarc5nvrtc6resultNtB4_10NvrtcErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.959.llvm.1750587498003715262,unique,368
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.959.llvm.1750587498003715262
anon.a7c37e6ade312d68d4d78ed2f53518c1.959.llvm.1750587498003715262:
	.ascii	"called `Result::unwrap()` on an `Err` value"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.961.llvm.1750587498003715262,unique,369
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.961.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.961.llvm.1750587498003715262:
	.quad	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCsfQUUnEvlYZE_5alloc3ffi5c_str8NulErrorECs5UjBoGikVie_6cudarc.llvm.1750587498003715262
	.asciz	" \000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNvXsX_NtNtCsfQUUnEvlYZE_5alloc3ffi5c_strNtB5_8NulErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt.llvm.1750587498003715262

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.975.llvm.1750587498003715262,unique,370
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.975.llvm.1750587498003715262
anon.a7c37e6ade312d68d4d78ed2f53518c1.975.llvm.1750587498003715262:
	.asciz	"C:\\Users\\there\\.cargo\\registry\\src\\index.crates.io-1949cf8c6b5b557f\\cudarc-0.19.7\\src\\driver\\safe\\core.rs"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.976,unique,371
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.976:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.975.llvm.1750587498003715262
	.asciz	"i\000\000\000\000\000\000\000\210\b\000\000/\000\000"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.977,unique,372
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.977:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.975.llvm.1750587498003715262
	.asciz	"i\000\000\000\000\000\000\000\214\b\000\000C\000\000"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.978,unique,373
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.978:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.975.llvm.1750587498003715262
	.asciz	"i\000\000\000\000\000\000\000\214\b\000\0009\000\000"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.979.llvm.1750587498003715262,unique,374
	.globl	anon.a7c37e6ade312d68d4d78ed2f53518c1.979.llvm.1750587498003715262
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.979.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.975.llvm.1750587498003715262
	.asciz	"i\000\000\000\000\000\000\000\250\b\000\000/\000\000"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.980,unique,375
anon.a7c37e6ade312d68d4d78ed2f53518c1.980:
	.asciz	"\006--ftz=\300"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.981,unique,376
anon.a7c37e6ade312d68d4d78ed2f53518c1.981:
	.asciz	"\f--prec-sqrt=\300"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.982,unique,377
anon.a7c37e6ade312d68d4d78ed2f53518c1.982:
	.asciz	"\013--prec-div=\300"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.983,unique,378
anon.a7c37e6ade312d68d4d78ed2f53518c1.983:
	.asciz	"\007--fmad=\300"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.984,unique,379
anon.a7c37e6ade312d68d4d78ed2f53518c1.984:
	.ascii	"--fmad=true"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.985,unique,380
anon.a7c37e6ade312d68d4d78ed2f53518c1.985:
	.asciz	"\017--maxrregcount=\300"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.986,unique,381
anon.a7c37e6ade312d68d4d78ed2f53518c1.986:
	.asciz	"\023--gpu-architecture=\300"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.987,unique,382
anon.a7c37e6ade312d68d4d78ed2f53518c1.987:
	.asciz	"\017--include-path=\300"

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys11nvrtcGetPTX2__S,unique,383
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys11nvrtcGetPTX2__S:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys15nvrtcGetPTXSize2__S,unique,384
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys15nvrtcGetPTXSize2__S:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys18nvrtcCreateProgram2__S.llvm.1750587498003715262,unique,385
	.globl	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys18nvrtcCreateProgram2__S.llvm.1750587498003715262
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys18nvrtcCreateProgram2__S.llvm.1750587498003715262:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys18nvrtcGetProgramLog2__S,unique,386
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys18nvrtcGetProgramLog2__S:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys19nvrtcCompileProgram2__S,unique,387
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys19nvrtcCompileProgram2__S:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys19nvrtcDestroyProgram2__S,unique,388
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys19nvrtcDestroyProgram2__S:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys22nvrtcGetProgramLogSize2__S,unique,389
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys22nvrtcGetProgramLogSize2__S:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib3LIB,unique,390
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys5culib3LIB:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys11cuDeviceGet2__S,unique,391
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys11cuDeviceGet2__S:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys12cuMemFree_v22__S.llvm.1750587498003715262,unique,392
	.globl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys12cuMemFree_v22__S.llvm.1750587498003715262
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys12cuMemFree_v22__S.llvm.1750587498003715262:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys12cuModuleLoad2__S,unique,393
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys12cuModuleLoad2__S:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuEventCreate2__S.llvm.1750587498003715262,unique,394
	.globl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuEventCreate2__S.llvm.1750587498003715262
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuEventCreate2__S.llvm.1750587498003715262:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuEventRecord2__S.llvm.1750587498003715262,unique,395
	.globl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuEventRecord2__S.llvm.1750587498003715262
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuEventRecord2__S.llvm.1750587498003715262:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuGraphLaunch2__S.llvm.1750587498003715262,unique,396
	.globl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuGraphLaunch2__S.llvm.1750587498003715262
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuGraphLaunch2__S.llvm.1750587498003715262:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuMemAlloc_v22__S.llvm.1750587498003715262,unique,397
	.globl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuMemAlloc_v22__S.llvm.1750587498003715262
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuMemAlloc_v22__S.llvm.1750587498003715262:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuMemFreeHost2__S.llvm.1750587498003715262,unique,398
	.globl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuMemFreeHost2__S.llvm.1750587498003715262
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuMemFreeHost2__S.llvm.1750587498003715262:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuGraphDestroy2__S.llvm.1750587498003715262,unique,399
	.globl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuGraphDestroy2__S.llvm.1750587498003715262
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuGraphDestroy2__S.llvm.1750587498003715262:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuLaunchKernel2__S.llvm.1750587498003715262,unique,400
	.globl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuLaunchKernel2__S.llvm.1750587498003715262
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuLaunchKernel2__S.llvm.1750587498003715262:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuMemFreeAsync2__S.llvm.1750587498003715262,unique,401
	.globl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuMemFreeAsync2__S.llvm.1750587498003715262
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuMemFreeAsync2__S.llvm.1750587498003715262:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuMemHostAlloc2__S.llvm.1750587498003715262,unique,402
	.globl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuMemHostAlloc2__S.llvm.1750587498003715262
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuMemHostAlloc2__S.llvm.1750587498003715262:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuModuleUnload2__S.llvm.1750587498003715262,unique,403
	.globl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuModuleUnload2__S.llvm.1750587498003715262
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuModuleUnload2__S.llvm.1750587498003715262:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuStreamCreate2__S,unique,404
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuStreamCreate2__S:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxDestroy_v22__S,unique,405
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxDestroy_v22__S:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262,unique,406
	.globl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262,unique,407
	.globl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuMemAllocAsync2__S.llvm.1750587498003715262,unique,408
	.globl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuMemAllocAsync2__S.llvm.1750587498003715262
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuMemAllocAsync2__S.llvm.1750587498003715262:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuMemsetD8Async2__S.llvm.1750587498003715262,unique,409
	.globl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuMemsetD8Async2__S.llvm.1750587498003715262
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuMemsetD8Async2__S.llvm.1750587498003715262:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys16cuCtxSynchronize2__S,unique,410
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys16cuCtxSynchronize2__S:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys16cuGetErrorString2__S,unique,411
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys16cuGetErrorString2__S:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys16cuModuleLoadData2__S,unique,412
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys16cuModuleLoadData2__S:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuEventDestroy_v22__S.llvm.1750587498003715262,unique,413
	.globl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuEventDestroy_v22__S.llvm.1750587498003715262
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuEventDestroy_v22__S.llvm.1750587498003715262:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuMemcpyPeerAsync2__S.llvm.1750587498003715262,unique,414
	.globl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuMemcpyPeerAsync2__S.llvm.1750587498003715262
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuMemcpyPeerAsync2__S.llvm.1750587498003715262:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuStreamWaitEvent2__S.llvm.1750587498003715262,unique,415
	.globl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuStreamWaitEvent2__S.llvm.1750587498003715262
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuStreamWaitEvent2__S.llvm.1750587498003715262:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuGraphExecDestroy2__S.llvm.1750587498003715262,unique,416
	.globl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuGraphExecDestroy2__S.llvm.1750587498003715262
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuGraphExecDestroy2__S.llvm.1750587498003715262:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuStreamDestroy_v22__S,unique,417
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuStreamDestroy_v22__S:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuStreamEndCapture2__S,unique,418
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuStreamEndCapture2__S:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys19cuModuleGetFunction2__S.llvm.1750587498003715262,unique,419
	.globl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys19cuModuleGetFunction2__S.llvm.1750587498003715262
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys19cuModuleGetFunction2__S.llvm.1750587498003715262:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys19cuStreamSynchronize2__S.llvm.1750587498003715262,unique,420
	.globl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys19cuStreamSynchronize2__S.llvm.1750587498003715262
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys19cuStreamSynchronize2__S.llvm.1750587498003715262:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuDeviceGetAttribute2__S.llvm.1750587498003715262,unique,421
	.globl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuDeviceGetAttribute2__S.llvm.1750587498003715262
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuDeviceGetAttribute2__S.llvm.1750587498003715262:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoDAsync_v22__S.llvm.1750587498003715262,unique,422
	.globl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoDAsync_v22__S.llvm.1750587498003715262
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoDAsync_v22__S.llvm.1750587498003715262:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoHAsync_v22__S.llvm.1750587498003715262,unique,423
	.globl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoHAsync_v22__S.llvm.1750587498003715262
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoHAsync_v22__S.llvm.1750587498003715262:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyHtoDAsync_v22__S.llvm.1750587498003715262,unique,424
	.globl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyHtoDAsync_v22__S.llvm.1750587498003715262
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyHtoDAsync_v22__S.llvm.1750587498003715262:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys23cuStreamBeginCapture_v22__S.llvm.1750587498003715262,unique,425
	.globl	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys23cuStreamBeginCapture_v22__S.llvm.1750587498003715262
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys23cuStreamBeginCapture_v22__S.llvm.1750587498003715262:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys24cuDevicePrimaryCtxRetain2__S,unique,426
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys24cuDevicePrimaryCtxRetain2__S:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys27cuGraphInstantiateWithFlags2__S,unique,427
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys27cuGraphInstantiateWithFlags2__S:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys28cuDevicePrimaryCtxRelease_v22__S,unique,428
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys28cuDevicePrimaryCtxRelease_v22__S:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB,unique,429
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys5culib3LIB:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.data,"dw",one_only,_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys6cuInit2__S,unique,430
	.p2align	3, 0x0
_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys6cuInit2__S:
	.zero	8
	.asciz	"\003\000\000"
	.zero	4

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.991,unique,431
anon.a7c37e6ade312d68d4d78ed2f53518c1.991:
	.ascii	"NVRTC_SUCCESS"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.992,unique,432
anon.a7c37e6ade312d68d4d78ed2f53518c1.992:
	.ascii	"NVRTC_ERROR_OUT_OF_MEMORY"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.993,unique,433
anon.a7c37e6ade312d68d4d78ed2f53518c1.993:
	.ascii	"NVRTC_ERROR_PROGRAM_CREATION_FAILURE"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.994,unique,434
anon.a7c37e6ade312d68d4d78ed2f53518c1.994:
	.ascii	"NVRTC_ERROR_INVALID_INPUT"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.995,unique,435
anon.a7c37e6ade312d68d4d78ed2f53518c1.995:
	.ascii	"NVRTC_ERROR_INVALID_PROGRAM"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.996,unique,436
anon.a7c37e6ade312d68d4d78ed2f53518c1.996:
	.ascii	"NVRTC_ERROR_INVALID_OPTION"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.997,unique,437
anon.a7c37e6ade312d68d4d78ed2f53518c1.997:
	.ascii	"NVRTC_ERROR_COMPILATION"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.998,unique,438
anon.a7c37e6ade312d68d4d78ed2f53518c1.998:
	.ascii	"NVRTC_ERROR_BUILTIN_OPERATION_FAILURE"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.999,unique,439
anon.a7c37e6ade312d68d4d78ed2f53518c1.999:
	.ascii	"NVRTC_ERROR_NO_NAME_EXPRESSIONS_AFTER_COMPILATION"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1000,unique,440
anon.a7c37e6ade312d68d4d78ed2f53518c1.1000:
	.ascii	"NVRTC_ERROR_NO_LOWERED_NAMES_BEFORE_COMPILATION"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1001,unique,441
anon.a7c37e6ade312d68d4d78ed2f53518c1.1001:
	.ascii	"NVRTC_ERROR_NAME_EXPRESSION_NOT_VALID"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1002,unique,442
anon.a7c37e6ade312d68d4d78ed2f53518c1.1002:
	.ascii	"NVRTC_ERROR_INTERNAL_ERROR"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1003,unique,443
anon.a7c37e6ade312d68d4d78ed2f53518c1.1003:
	.ascii	"NVRTC_ERROR_TIME_FILE_WRITE_FAILED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1004,unique,444
anon.a7c37e6ade312d68d4d78ed2f53518c1.1004:
	.ascii	"DriverError"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1007,unique,445
anon.a7c37e6ade312d68d4d78ed2f53518c1.1007:
	.ascii	"<Failure when calling cuGetErrorString()>"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1010,unique,446
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.1010:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.474
	.asciz	"c\000\000\000\000\000\000\000\254\000\000\0006\000\000"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1011,unique,447
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.1011:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNvXsZ_NtNtCs8xEFJqa6dYS_4core3fmt3numjNtB7_5Debug3fmt

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1018,unique,448
	.p2align	3, 0x0
anon.a7c37e6ade312d68d4d78ed2f53518c1.1018:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRINtNtCsfQUUnEvlYZE_5alloc3vec3VechENtB6_5Debug3fmtCs5UjBoGikVie_6cudarc

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1019,unique,449
anon.a7c37e6ade312d68d4d78ed2f53518c1.1019:
	.ascii	"NulError"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1021,unique,450
anon.a7c37e6ade312d68d4d78ed2f53518c1.1021:
	.ascii	"NvrtcError"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1022,unique,451
anon.a7c37e6ade312d68d4d78ed2f53518c1.1022:
	.ascii	"CUDA_SUCCESS"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1023,unique,452
anon.a7c37e6ade312d68d4d78ed2f53518c1.1023:
	.ascii	"CUDA_ERROR_INVALID_VALUE"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1024,unique,453
anon.a7c37e6ade312d68d4d78ed2f53518c1.1024:
	.ascii	"CUDA_ERROR_OUT_OF_MEMORY"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1025,unique,454
anon.a7c37e6ade312d68d4d78ed2f53518c1.1025:
	.ascii	"CUDA_ERROR_NOT_INITIALIZED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1026,unique,455
anon.a7c37e6ade312d68d4d78ed2f53518c1.1026:
	.ascii	"CUDA_ERROR_DEINITIALIZED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1027,unique,456
anon.a7c37e6ade312d68d4d78ed2f53518c1.1027:
	.ascii	"CUDA_ERROR_PROFILER_DISABLED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1028,unique,457
anon.a7c37e6ade312d68d4d78ed2f53518c1.1028:
	.ascii	"CUDA_ERROR_PROFILER_NOT_INITIALIZED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1029,unique,458
anon.a7c37e6ade312d68d4d78ed2f53518c1.1029:
	.ascii	"CUDA_ERROR_PROFILER_ALREADY_STARTED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1030,unique,459
anon.a7c37e6ade312d68d4d78ed2f53518c1.1030:
	.ascii	"CUDA_ERROR_PROFILER_ALREADY_STOPPED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1031,unique,460
anon.a7c37e6ade312d68d4d78ed2f53518c1.1031:
	.ascii	"CUDA_ERROR_STUB_LIBRARY"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1032,unique,461
anon.a7c37e6ade312d68d4d78ed2f53518c1.1032:
	.ascii	"CUDA_ERROR_DEVICE_UNAVAILABLE"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1033,unique,462
anon.a7c37e6ade312d68d4d78ed2f53518c1.1033:
	.ascii	"CUDA_ERROR_NO_DEVICE"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1034,unique,463
anon.a7c37e6ade312d68d4d78ed2f53518c1.1034:
	.ascii	"CUDA_ERROR_INVALID_DEVICE"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1035,unique,464
anon.a7c37e6ade312d68d4d78ed2f53518c1.1035:
	.ascii	"CUDA_ERROR_DEVICE_NOT_LICENSED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1036,unique,465
anon.a7c37e6ade312d68d4d78ed2f53518c1.1036:
	.ascii	"CUDA_ERROR_INVALID_IMAGE"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1037,unique,466
anon.a7c37e6ade312d68d4d78ed2f53518c1.1037:
	.ascii	"CUDA_ERROR_INVALID_CONTEXT"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1038,unique,467
anon.a7c37e6ade312d68d4d78ed2f53518c1.1038:
	.ascii	"CUDA_ERROR_CONTEXT_ALREADY_CURRENT"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1039,unique,468
anon.a7c37e6ade312d68d4d78ed2f53518c1.1039:
	.ascii	"CUDA_ERROR_MAP_FAILED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1040,unique,469
anon.a7c37e6ade312d68d4d78ed2f53518c1.1040:
	.ascii	"CUDA_ERROR_UNMAP_FAILED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1041,unique,470
anon.a7c37e6ade312d68d4d78ed2f53518c1.1041:
	.ascii	"CUDA_ERROR_ARRAY_IS_MAPPED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1042,unique,471
anon.a7c37e6ade312d68d4d78ed2f53518c1.1042:
	.ascii	"CUDA_ERROR_ALREADY_MAPPED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1043,unique,472
anon.a7c37e6ade312d68d4d78ed2f53518c1.1043:
	.ascii	"CUDA_ERROR_NO_BINARY_FOR_GPU"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1044,unique,473
anon.a7c37e6ade312d68d4d78ed2f53518c1.1044:
	.ascii	"CUDA_ERROR_ALREADY_ACQUIRED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1045,unique,474
anon.a7c37e6ade312d68d4d78ed2f53518c1.1045:
	.ascii	"CUDA_ERROR_NOT_MAPPED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1046,unique,475
anon.a7c37e6ade312d68d4d78ed2f53518c1.1046:
	.ascii	"CUDA_ERROR_NOT_MAPPED_AS_ARRAY"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1047,unique,476
anon.a7c37e6ade312d68d4d78ed2f53518c1.1047:
	.ascii	"CUDA_ERROR_NOT_MAPPED_AS_POINTER"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1048,unique,477
anon.a7c37e6ade312d68d4d78ed2f53518c1.1048:
	.ascii	"CUDA_ERROR_ECC_UNCORRECTABLE"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1049,unique,478
anon.a7c37e6ade312d68d4d78ed2f53518c1.1049:
	.ascii	"CUDA_ERROR_UNSUPPORTED_LIMIT"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1050,unique,479
anon.a7c37e6ade312d68d4d78ed2f53518c1.1050:
	.ascii	"CUDA_ERROR_CONTEXT_ALREADY_IN_USE"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1051,unique,480
anon.a7c37e6ade312d68d4d78ed2f53518c1.1051:
	.ascii	"CUDA_ERROR_PEER_ACCESS_UNSUPPORTED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1052,unique,481
anon.a7c37e6ade312d68d4d78ed2f53518c1.1052:
	.ascii	"CUDA_ERROR_INVALID_PTX"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1053,unique,482
anon.a7c37e6ade312d68d4d78ed2f53518c1.1053:
	.ascii	"CUDA_ERROR_INVALID_GRAPHICS_CONTEXT"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1054,unique,483
anon.a7c37e6ade312d68d4d78ed2f53518c1.1054:
	.ascii	"CUDA_ERROR_NVLINK_UNCORRECTABLE"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1055,unique,484
anon.a7c37e6ade312d68d4d78ed2f53518c1.1055:
	.ascii	"CUDA_ERROR_JIT_COMPILER_NOT_FOUND"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1056,unique,485
anon.a7c37e6ade312d68d4d78ed2f53518c1.1056:
	.ascii	"CUDA_ERROR_UNSUPPORTED_PTX_VERSION"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1057,unique,486
anon.a7c37e6ade312d68d4d78ed2f53518c1.1057:
	.ascii	"CUDA_ERROR_JIT_COMPILATION_DISABLED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1058,unique,487
anon.a7c37e6ade312d68d4d78ed2f53518c1.1058:
	.ascii	"CUDA_ERROR_UNSUPPORTED_EXEC_AFFINITY"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1059,unique,488
anon.a7c37e6ade312d68d4d78ed2f53518c1.1059:
	.ascii	"CUDA_ERROR_UNSUPPORTED_DEVSIDE_SYNC"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1060,unique,489
anon.a7c37e6ade312d68d4d78ed2f53518c1.1060:
	.ascii	"CUDA_ERROR_INVALID_SOURCE"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1061,unique,490
anon.a7c37e6ade312d68d4d78ed2f53518c1.1061:
	.ascii	"CUDA_ERROR_FILE_NOT_FOUND"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1062,unique,491
anon.a7c37e6ade312d68d4d78ed2f53518c1.1062:
	.ascii	"CUDA_ERROR_SHARED_OBJECT_SYMBOL_NOT_FOUND"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1063,unique,492
anon.a7c37e6ade312d68d4d78ed2f53518c1.1063:
	.ascii	"CUDA_ERROR_SHARED_OBJECT_INIT_FAILED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1064,unique,493
anon.a7c37e6ade312d68d4d78ed2f53518c1.1064:
	.ascii	"CUDA_ERROR_OPERATING_SYSTEM"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1065,unique,494
anon.a7c37e6ade312d68d4d78ed2f53518c1.1065:
	.ascii	"CUDA_ERROR_INVALID_HANDLE"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1066,unique,495
anon.a7c37e6ade312d68d4d78ed2f53518c1.1066:
	.ascii	"CUDA_ERROR_ILLEGAL_STATE"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1067,unique,496
anon.a7c37e6ade312d68d4d78ed2f53518c1.1067:
	.ascii	"CUDA_ERROR_LOSSY_QUERY"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1068,unique,497
anon.a7c37e6ade312d68d4d78ed2f53518c1.1068:
	.ascii	"CUDA_ERROR_NOT_FOUND"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1069,unique,498
anon.a7c37e6ade312d68d4d78ed2f53518c1.1069:
	.ascii	"CUDA_ERROR_NOT_READY"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1070,unique,499
anon.a7c37e6ade312d68d4d78ed2f53518c1.1070:
	.ascii	"CUDA_ERROR_ILLEGAL_ADDRESS"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1071,unique,500
anon.a7c37e6ade312d68d4d78ed2f53518c1.1071:
	.ascii	"CUDA_ERROR_LAUNCH_OUT_OF_RESOURCES"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1072,unique,501
anon.a7c37e6ade312d68d4d78ed2f53518c1.1072:
	.ascii	"CUDA_ERROR_LAUNCH_TIMEOUT"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1073,unique,502
anon.a7c37e6ade312d68d4d78ed2f53518c1.1073:
	.ascii	"CUDA_ERROR_LAUNCH_INCOMPATIBLE_TEXTURING"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1074,unique,503
anon.a7c37e6ade312d68d4d78ed2f53518c1.1074:
	.ascii	"CUDA_ERROR_PEER_ACCESS_ALREADY_ENABLED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1075,unique,504
anon.a7c37e6ade312d68d4d78ed2f53518c1.1075:
	.ascii	"CUDA_ERROR_PEER_ACCESS_NOT_ENABLED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1076,unique,505
anon.a7c37e6ade312d68d4d78ed2f53518c1.1076:
	.ascii	"CUDA_ERROR_PRIMARY_CONTEXT_ACTIVE"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1077,unique,506
anon.a7c37e6ade312d68d4d78ed2f53518c1.1077:
	.ascii	"CUDA_ERROR_CONTEXT_IS_DESTROYED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1078,unique,507
anon.a7c37e6ade312d68d4d78ed2f53518c1.1078:
	.ascii	"CUDA_ERROR_ASSERT"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1079,unique,508
anon.a7c37e6ade312d68d4d78ed2f53518c1.1079:
	.ascii	"CUDA_ERROR_TOO_MANY_PEERS"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1080,unique,509
anon.a7c37e6ade312d68d4d78ed2f53518c1.1080:
	.ascii	"CUDA_ERROR_HOST_MEMORY_ALREADY_REGISTERED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1081,unique,510
anon.a7c37e6ade312d68d4d78ed2f53518c1.1081:
	.ascii	"CUDA_ERROR_HOST_MEMORY_NOT_REGISTERED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1082,unique,511
anon.a7c37e6ade312d68d4d78ed2f53518c1.1082:
	.ascii	"CUDA_ERROR_HARDWARE_STACK_ERROR"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1083,unique,512
anon.a7c37e6ade312d68d4d78ed2f53518c1.1083:
	.ascii	"CUDA_ERROR_ILLEGAL_INSTRUCTION"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1084,unique,513
anon.a7c37e6ade312d68d4d78ed2f53518c1.1084:
	.ascii	"CUDA_ERROR_MISALIGNED_ADDRESS"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1085,unique,514
anon.a7c37e6ade312d68d4d78ed2f53518c1.1085:
	.ascii	"CUDA_ERROR_INVALID_ADDRESS_SPACE"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1086,unique,515
anon.a7c37e6ade312d68d4d78ed2f53518c1.1086:
	.ascii	"CUDA_ERROR_INVALID_PC"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1087,unique,516
anon.a7c37e6ade312d68d4d78ed2f53518c1.1087:
	.ascii	"CUDA_ERROR_LAUNCH_FAILED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1088,unique,517
anon.a7c37e6ade312d68d4d78ed2f53518c1.1088:
	.ascii	"CUDA_ERROR_COOPERATIVE_LAUNCH_TOO_LARGE"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1089,unique,518
anon.a7c37e6ade312d68d4d78ed2f53518c1.1089:
	.ascii	"CUDA_ERROR_NOT_PERMITTED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1090,unique,519
anon.a7c37e6ade312d68d4d78ed2f53518c1.1090:
	.ascii	"CUDA_ERROR_NOT_SUPPORTED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1091,unique,520
anon.a7c37e6ade312d68d4d78ed2f53518c1.1091:
	.ascii	"CUDA_ERROR_SYSTEM_NOT_READY"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1092,unique,521
anon.a7c37e6ade312d68d4d78ed2f53518c1.1092:
	.ascii	"CUDA_ERROR_SYSTEM_DRIVER_MISMATCH"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1093,unique,522
anon.a7c37e6ade312d68d4d78ed2f53518c1.1093:
	.ascii	"CUDA_ERROR_COMPAT_NOT_SUPPORTED_ON_DEVICE"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1094,unique,523
anon.a7c37e6ade312d68d4d78ed2f53518c1.1094:
	.ascii	"CUDA_ERROR_MPS_CONNECTION_FAILED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1095,unique,524
anon.a7c37e6ade312d68d4d78ed2f53518c1.1095:
	.ascii	"CUDA_ERROR_MPS_RPC_FAILURE"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1096,unique,525
anon.a7c37e6ade312d68d4d78ed2f53518c1.1096:
	.ascii	"CUDA_ERROR_MPS_SERVER_NOT_READY"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1097,unique,526
anon.a7c37e6ade312d68d4d78ed2f53518c1.1097:
	.ascii	"CUDA_ERROR_MPS_MAX_CLIENTS_REACHED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1098,unique,527
anon.a7c37e6ade312d68d4d78ed2f53518c1.1098:
	.ascii	"CUDA_ERROR_MPS_MAX_CONNECTIONS_REACHED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1099,unique,528
anon.a7c37e6ade312d68d4d78ed2f53518c1.1099:
	.ascii	"CUDA_ERROR_MPS_CLIENT_TERMINATED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1100,unique,529
anon.a7c37e6ade312d68d4d78ed2f53518c1.1100:
	.ascii	"CUDA_ERROR_CDP_NOT_SUPPORTED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1101,unique,530
anon.a7c37e6ade312d68d4d78ed2f53518c1.1101:
	.ascii	"CUDA_ERROR_CDP_VERSION_MISMATCH"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1102,unique,531
anon.a7c37e6ade312d68d4d78ed2f53518c1.1102:
	.ascii	"CUDA_ERROR_STREAM_CAPTURE_UNSUPPORTED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1103,unique,532
anon.a7c37e6ade312d68d4d78ed2f53518c1.1103:
	.ascii	"CUDA_ERROR_STREAM_CAPTURE_INVALIDATED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1104,unique,533
anon.a7c37e6ade312d68d4d78ed2f53518c1.1104:
	.ascii	"CUDA_ERROR_STREAM_CAPTURE_MERGE"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1105,unique,534
anon.a7c37e6ade312d68d4d78ed2f53518c1.1105:
	.ascii	"CUDA_ERROR_STREAM_CAPTURE_UNMATCHED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1106,unique,535
anon.a7c37e6ade312d68d4d78ed2f53518c1.1106:
	.ascii	"CUDA_ERROR_STREAM_CAPTURE_UNJOINED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1107,unique,536
anon.a7c37e6ade312d68d4d78ed2f53518c1.1107:
	.ascii	"CUDA_ERROR_STREAM_CAPTURE_ISOLATION"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1108,unique,537
anon.a7c37e6ade312d68d4d78ed2f53518c1.1108:
	.ascii	"CUDA_ERROR_STREAM_CAPTURE_IMPLICIT"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1109,unique,538
anon.a7c37e6ade312d68d4d78ed2f53518c1.1109:
	.ascii	"CUDA_ERROR_CAPTURED_EVENT"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1110,unique,539
anon.a7c37e6ade312d68d4d78ed2f53518c1.1110:
	.ascii	"CUDA_ERROR_STREAM_CAPTURE_WRONG_THREAD"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1111,unique,540
anon.a7c37e6ade312d68d4d78ed2f53518c1.1111:
	.ascii	"CUDA_ERROR_TIMEOUT"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1112,unique,541
anon.a7c37e6ade312d68d4d78ed2f53518c1.1112:
	.ascii	"CUDA_ERROR_GRAPH_EXEC_UPDATE_FAILURE"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1113,unique,542
anon.a7c37e6ade312d68d4d78ed2f53518c1.1113:
	.ascii	"CUDA_ERROR_EXTERNAL_DEVICE"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1114,unique,543
anon.a7c37e6ade312d68d4d78ed2f53518c1.1114:
	.ascii	"CUDA_ERROR_INVALID_CLUSTER_SIZE"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1115,unique,544
anon.a7c37e6ade312d68d4d78ed2f53518c1.1115:
	.ascii	"CUDA_ERROR_FUNCTION_NOT_LOADED"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1116,unique,545
anon.a7c37e6ade312d68d4d78ed2f53518c1.1116:
	.ascii	"CUDA_ERROR_INVALID_RESOURCE_TYPE"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1117,unique,546
anon.a7c37e6ade312d68d4d78ed2f53518c1.1117:
	.ascii	"CUDA_ERROR_INVALID_RESOURCE_CONFIGURATION"

	.section	.rdata,"dr",one_only,anon.a7c37e6ade312d68d4d78ed2f53518c1.1118,unique,547
anon.a7c37e6ade312d68d4d78ed2f53518c1.1118:
	.ascii	"CUDA_ERROR_UNKNOWN"

	.section	.rdata,"dr",one_only,switch.table._RNvXs_NtNtCs5UjBoGikVie_6cudarc5nvrtc6resultNtB4_10NvrtcErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt.70,unique,548
	.p2align	3, 0x0
switch.table._RNvXs_NtNtCs5UjBoGikVie_6cudarc5nvrtc6resultNtB4_10NvrtcErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt.70:
	.quad	13
	.quad	25
	.quad	36
	.quad	25
	.quad	27
	.quad	26
	.quad	23
	.quad	37
	.quad	49
	.quad	47
	.quad	37
	.quad	26
	.quad	34

	.section	.rdata,"dr",one_only,switch.table._RNvXs_NtNtCs5UjBoGikVie_6cudarc5nvrtc6resultNtB4_10NvrtcErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt.71,unique,549
	.p2align	3, 0x0
switch.table._RNvXs_NtNtCs5UjBoGikVie_6cudarc5nvrtc6resultNtB4_10NvrtcErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt.71:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.991
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.992
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.993
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.994
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.995
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.996
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.997
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.998
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.999
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.1000
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.1001
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.1002
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.1003

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.4.llvm.1750587498003715262,unique,550
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.4.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.4.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.4.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262,unique,551
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.5.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.21.llvm.1750587498003715262,unique,552
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.21.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.21.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.21.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.32.llvm.1750587498003715262,unique,553
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.32.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.32.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.32.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.52.llvm.1750587498003715262,unique,554
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.52.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.52.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.52.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.54.llvm.1750587498003715262,unique,555
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.54.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.54.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.54.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.56.llvm.1750587498003715262,unique,556
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.56.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.56.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.56.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.71.llvm.1750587498003715262,unique,557
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.71.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.71.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.71.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.76.llvm.1750587498003715262,unique,558
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.76.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.76.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.76.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.77.llvm.1750587498003715262,unique,559
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.77.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.77.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.77.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.117.llvm.1750587498003715262,unique,560
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.117.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.117.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.117.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.119.llvm.1750587498003715262,unique,561
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.119.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.119.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.119.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.214.llvm.1750587498003715262,unique,562
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.214.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.214.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.214.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.224.llvm.1750587498003715262,unique,563
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.224.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.224.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.224.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.240.llvm.1750587498003715262,unique,564
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.240.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.240.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.240.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.249.llvm.1750587498003715262,unique,565
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.249.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.249.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.249.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.251.llvm.1750587498003715262,unique,566
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.251.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.251.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.251.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.260.llvm.1750587498003715262,unique,567
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.260.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.260.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.260.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.300.llvm.1750587498003715262,unique,568
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.300.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.300.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.300.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.317.llvm.1750587498003715262,unique,569
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.317.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.317.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.317.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.350.llvm.1750587498003715262,unique,570
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.350.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.350.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.350.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.386.llvm.1750587498003715262,unique,571
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.386.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.386.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.386.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.387.llvm.1750587498003715262,unique,572
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.387.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.387.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.387.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.422.llvm.1750587498003715262,unique,573
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.422.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.422.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.422.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.428.llvm.1750587498003715262,unique,574
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.428.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.428.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.428.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.430.llvm.1750587498003715262,unique,575
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.430.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.430.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.430.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.432.llvm.1750587498003715262,unique,576
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.432.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.432.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.432.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.434.llvm.1750587498003715262,unique,577
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.434.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.434.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.434.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.460.llvm.1750587498003715262,unique,578
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.460.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.460.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.460.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.959.llvm.1750587498003715262,unique,579
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.959.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.959.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.959.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.961.llvm.1750587498003715262,unique,580
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.961.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.961.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.961.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.975.llvm.1750587498003715262,unique,581
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.975.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.975.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.975.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.979.llvm.1750587498003715262,unique,582
	.globl	__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.979.llvm.1750587498003715262
	.p2align	3, 0x0
__imp_anon.a7c37e6ade312d68d4d78ed2f53518c1.979.llvm.1750587498003715262:
	.quad	anon.a7c37e6ade312d68d4d78ed2f53518c1.979.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys18nvrtcCreateProgram2__S.llvm.1750587498003715262,unique,583
	.globl	__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys18nvrtcCreateProgram2__S.llvm.1750587498003715262
	.p2align	3, 0x0
__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys18nvrtcCreateProgram2__S.llvm.1750587498003715262:
	.quad	_RNvNvNtNtCs5UjBoGikVie_6cudarc5nvrtc3sys18nvrtcCreateProgram2__S.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys12cuMemFree_v22__S.llvm.1750587498003715262,unique,584
	.globl	__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys12cuMemFree_v22__S.llvm.1750587498003715262
	.p2align	3, 0x0
__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys12cuMemFree_v22__S.llvm.1750587498003715262:
	.quad	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys12cuMemFree_v22__S.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuEventCreate2__S.llvm.1750587498003715262,unique,585
	.globl	__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuEventCreate2__S.llvm.1750587498003715262
	.p2align	3, 0x0
__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuEventCreate2__S.llvm.1750587498003715262:
	.quad	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuEventCreate2__S.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuEventRecord2__S.llvm.1750587498003715262,unique,586
	.globl	__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuEventRecord2__S.llvm.1750587498003715262
	.p2align	3, 0x0
__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuEventRecord2__S.llvm.1750587498003715262:
	.quad	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuEventRecord2__S.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuGraphLaunch2__S.llvm.1750587498003715262,unique,587
	.globl	__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuGraphLaunch2__S.llvm.1750587498003715262
	.p2align	3, 0x0
__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuGraphLaunch2__S.llvm.1750587498003715262:
	.quad	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuGraphLaunch2__S.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuMemAlloc_v22__S.llvm.1750587498003715262,unique,588
	.globl	__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuMemAlloc_v22__S.llvm.1750587498003715262
	.p2align	3, 0x0
__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuMemAlloc_v22__S.llvm.1750587498003715262:
	.quad	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuMemAlloc_v22__S.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuMemFreeHost2__S.llvm.1750587498003715262,unique,589
	.globl	__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuMemFreeHost2__S.llvm.1750587498003715262
	.p2align	3, 0x0
__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuMemFreeHost2__S.llvm.1750587498003715262:
	.quad	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys13cuMemFreeHost2__S.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuGraphDestroy2__S.llvm.1750587498003715262,unique,590
	.globl	__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuGraphDestroy2__S.llvm.1750587498003715262
	.p2align	3, 0x0
__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuGraphDestroy2__S.llvm.1750587498003715262:
	.quad	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuGraphDestroy2__S.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuLaunchKernel2__S.llvm.1750587498003715262,unique,591
	.globl	__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuLaunchKernel2__S.llvm.1750587498003715262
	.p2align	3, 0x0
__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuLaunchKernel2__S.llvm.1750587498003715262:
	.quad	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuLaunchKernel2__S.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuMemFreeAsync2__S.llvm.1750587498003715262,unique,592
	.globl	__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuMemFreeAsync2__S.llvm.1750587498003715262
	.p2align	3, 0x0
__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuMemFreeAsync2__S.llvm.1750587498003715262:
	.quad	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuMemFreeAsync2__S.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuMemHostAlloc2__S.llvm.1750587498003715262,unique,593
	.globl	__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuMemHostAlloc2__S.llvm.1750587498003715262
	.p2align	3, 0x0
__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuMemHostAlloc2__S.llvm.1750587498003715262:
	.quad	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuMemHostAlloc2__S.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuModuleUnload2__S.llvm.1750587498003715262,unique,594
	.globl	__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuModuleUnload2__S.llvm.1750587498003715262
	.p2align	3, 0x0
__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuModuleUnload2__S.llvm.1750587498003715262:
	.quad	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys14cuModuleUnload2__S.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262,unique,595
	.globl	__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262
	.p2align	3, 0x0
__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262:
	.quad	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxGetCurrent2__S.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262,unique,596
	.globl	__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262
	.p2align	3, 0x0
__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262:
	.quad	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuCtxSetCurrent2__S.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuMemAllocAsync2__S.llvm.1750587498003715262,unique,597
	.globl	__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuMemAllocAsync2__S.llvm.1750587498003715262
	.p2align	3, 0x0
__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuMemAllocAsync2__S.llvm.1750587498003715262:
	.quad	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuMemAllocAsync2__S.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuMemsetD8Async2__S.llvm.1750587498003715262,unique,598
	.globl	__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuMemsetD8Async2__S.llvm.1750587498003715262
	.p2align	3, 0x0
__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuMemsetD8Async2__S.llvm.1750587498003715262:
	.quad	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys15cuMemsetD8Async2__S.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuEventDestroy_v22__S.llvm.1750587498003715262,unique,599
	.globl	__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuEventDestroy_v22__S.llvm.1750587498003715262
	.p2align	3, 0x0
__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuEventDestroy_v22__S.llvm.1750587498003715262:
	.quad	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuEventDestroy_v22__S.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuMemcpyPeerAsync2__S.llvm.1750587498003715262,unique,600
	.globl	__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuMemcpyPeerAsync2__S.llvm.1750587498003715262
	.p2align	3, 0x0
__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuMemcpyPeerAsync2__S.llvm.1750587498003715262:
	.quad	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuMemcpyPeerAsync2__S.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuStreamWaitEvent2__S.llvm.1750587498003715262,unique,601
	.globl	__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuStreamWaitEvent2__S.llvm.1750587498003715262
	.p2align	3, 0x0
__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuStreamWaitEvent2__S.llvm.1750587498003715262:
	.quad	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys17cuStreamWaitEvent2__S.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuGraphExecDestroy2__S.llvm.1750587498003715262,unique,602
	.globl	__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuGraphExecDestroy2__S.llvm.1750587498003715262
	.p2align	3, 0x0
__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuGraphExecDestroy2__S.llvm.1750587498003715262:
	.quad	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys18cuGraphExecDestroy2__S.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys19cuModuleGetFunction2__S.llvm.1750587498003715262,unique,603
	.globl	__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys19cuModuleGetFunction2__S.llvm.1750587498003715262
	.p2align	3, 0x0
__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys19cuModuleGetFunction2__S.llvm.1750587498003715262:
	.quad	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys19cuModuleGetFunction2__S.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys19cuStreamSynchronize2__S.llvm.1750587498003715262,unique,604
	.globl	__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys19cuStreamSynchronize2__S.llvm.1750587498003715262
	.p2align	3, 0x0
__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys19cuStreamSynchronize2__S.llvm.1750587498003715262:
	.quad	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys19cuStreamSynchronize2__S.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuDeviceGetAttribute2__S.llvm.1750587498003715262,unique,605
	.globl	__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuDeviceGetAttribute2__S.llvm.1750587498003715262
	.p2align	3, 0x0
__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuDeviceGetAttribute2__S.llvm.1750587498003715262:
	.quad	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuDeviceGetAttribute2__S.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoDAsync_v22__S.llvm.1750587498003715262,unique,606
	.globl	__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoDAsync_v22__S.llvm.1750587498003715262
	.p2align	3, 0x0
__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoDAsync_v22__S.llvm.1750587498003715262:
	.quad	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoDAsync_v22__S.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoHAsync_v22__S.llvm.1750587498003715262,unique,607
	.globl	__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoHAsync_v22__S.llvm.1750587498003715262
	.p2align	3, 0x0
__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoHAsync_v22__S.llvm.1750587498003715262:
	.quad	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyDtoHAsync_v22__S.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyHtoDAsync_v22__S.llvm.1750587498003715262,unique,608
	.globl	__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyHtoDAsync_v22__S.llvm.1750587498003715262
	.p2align	3, 0x0
__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyHtoDAsync_v22__S.llvm.1750587498003715262:
	.quad	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys20cuMemcpyHtoDAsync_v22__S.llvm.1750587498003715262

	.section	.data,"dw",one_only,__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys23cuStreamBeginCapture_v22__S.llvm.1750587498003715262,unique,609
	.globl	__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys23cuStreamBeginCapture_v22__S.llvm.1750587498003715262
	.p2align	3, 0x0
__imp__RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys23cuStreamBeginCapture_v22__S.llvm.1750587498003715262:
	.quad	_RNvNvNtNtCs5UjBoGikVie_6cudarc6driver3sys23cuStreamBeginCapture_v22__S.llvm.1750587498003715262

	.section	.debug$S,"dr"
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp201-.Ltmp200
.Ltmp200:
	.short	.Ltmp203-.Ltmp202
.Ltmp202:
	.short	4353
	.long	0
	.asciz	"S:\\GTOpen-research\\postflop-gpu-20261016\\build\\release\\deps\\postflop_autoresearch-ba6a3e8216b3a7e5.cudarc-ba3140064b5903a3.cudarc.44d1634b446b2610-cgu.0.rcgu.o.rcgu.o"
	.p2align	2, 0x0
.Ltmp203:
	.short	.Ltmp205-.Ltmp204
.Ltmp204:
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
.Ltmp205:
.Ltmp201:
	.p2align	2, 0x0
	.cv_filechecksums
	.cv_stringtable
	.long	241
	.long	.Ltmp207-.Ltmp206
.Ltmp206:
	.short	.Ltmp209-.Ltmp208
.Ltmp208:
	.short	4428
	.long	4099
	.p2align	2, 0x0
.Ltmp209:
.Ltmp207:
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
	.long	0x1000
	.long	0x1002
	.long	0x1001
	.long	0x1002
	.long	0x1002
	.byte	242
	.byte	241
