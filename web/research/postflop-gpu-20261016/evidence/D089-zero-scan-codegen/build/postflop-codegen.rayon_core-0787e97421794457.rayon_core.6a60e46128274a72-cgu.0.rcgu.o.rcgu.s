	.def	@feat.00;
	.scl	3;
	.type	0;
	.endef
	.globl	@feat.00
@feat.00 = 0
	.file	"rayon_core.6a60e46128274a72-cgu.0"
	.def	_RINvMNtCs98fvGvYc57G_10rayon_core5sleepNtB3_5Sleep5sleepNCNvMs8_NtB5_8registryNtB10_12WorkerThread15wait_until_cold0EB5_.llvm.17002324475202138184;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMNtCs98fvGvYc57G_10rayon_core5sleepNtB3_5Sleep5sleepNCNvMs8_NtB5_8registryNtB10_12WorkerThread15wait_until_cold0EB5_.llvm.17002324475202138184,unique,0
	.globl	_RINvMNtCs98fvGvYc57G_10rayon_core5sleepNtB3_5Sleep5sleepNCNvMs8_NtB5_8registryNtB10_12WorkerThread15wait_until_cold0EB5_.llvm.17002324475202138184
	.p2align	4
_RINvMNtCs98fvGvYc57G_10rayon_core5sleepNtB3_5Sleep5sleepNCNvMs8_NtB5_8registryNtB10_12WorkerThread15wait_until_cold0EB5_.llvm.17002324475202138184:
.Lfunc_begin0:
.seh_proc _RINvMNtCs98fvGvYc57G_10rayon_core5sleepNtB3_5Sleep5sleepNCNvMs8_NtB5_8registryNtB10_12WorkerThread15wait_until_cold0EB5_.llvm.17002324475202138184
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
	subq	$72, %rsp
	.seh_stackalloc 72
	leaq	64(%rsp), %rbp
	.seh_setframe %rbp, 64
	.seh_endprologue
	movq	$-2, (%rbp)
	movq	%rdx, %r14
	movq	(%rdx), %r15
	movl	$1, %edx
	xorl	%eax, %eax
	lock		cmpxchgq	%rdx, (%r8)
	jne	.LBB0_36
	movq	16(%rcx), %rdx
	cmpq	%rdx, %r15
	jae	.LBB0_10
	movq	%r8, %rbx
	movq	8(%rcx), %rdi
	shlq	$7, %r15
	leaq	(%rdi,%r15), %rsi
	addq	$4, %rsi
	movb	$1, %dl
	xorl	%eax, %eax
	lock		cmpxchgb	%dl, 4(%rdi,%r15)
	jne	.LBB0_3
.LBB0_4:
	addq	%r15, %rdi
	movq	_RNvNtNtCse0R8cuyqEa_3std9panicking11panic_count18GLOBAL_PANIC_COUNT(%rip), %rax
	shlq	%rax
	testq	%rax, %rax
	jne	.LBB0_6
	xorl	%r15d, %r15d
	movzbl	5(%rdi), %eax
	testb	%al, %al
	jne	.LBB0_8
.LBB0_11:
	movl	$2, %edx
	movl	$1, %eax
	lock		cmpxchgq	%rdx, (%rbx)
	jne	.LBB0_12
	.p2align	4
.LBB0_13:
	movq	24(%rcx), %rax
	movq	%rax, %rdx
	shrq	$32, %rdx
	cmpq	8(%r14), %rdx
	jne	.LBB0_37
	leaq	1(%rax), %rdx
	lock		cmpxchgq	%rdx, 24(%rcx)
	jne	.LBB0_13
	lock		orl	$0, (%rsp)
	movq	312(%r9), %rax
	movq	256(%rax), %rdx
	lock		orl	$0, (%rsp)
	movq	264(%rax), %rax
	subq	%rdx, %rax
	testq	%rax, %rax
	jg	.LBB0_27
	movq	272(%r9), %rax
	movq	128(%rax), %rdx
	movq	256(%rax), %rax
	xorq	%rdx, %rax
	cmpq	$1, %rax
	jbe	.LBB0_17
.LBB0_27:
	lock		decq	24(%rcx)
.LBB0_28:
	movl	$0, 16(%r14)
	movq	$-1, 8(%r14)
	movq	(%rbx), %rax
	cmpq	$3, %rax
	jne	.LBB0_30
	jmp	.LBB0_31
.LBB0_12:
	movl	$0, 16(%r14)
	movq	$-1, 8(%r14)
	jmp	.LBB0_31
.LBB0_37:
	movl	$32, 16(%r14)
	movq	$-1, 8(%r14)
	movq	(%rbx), %rax
	cmpq	$3, %rax
	je	.LBB0_31
.LBB0_30:
	xorl	%ecx, %ecx
	movl	$2, %eax
	lock		cmpxchgq	%rcx, (%rbx)
.LBB0_31:
	testb	%r15b, %r15b
	jne	.LBB0_35
	movq	_RNvNtNtCse0R8cuyqEa_3std9panicking11panic_count18GLOBAL_PANIC_COUNT(%rip), %rax
	shlq	%rax
	testq	%rax, %rax
	jne	.LBB0_33
.LBB0_35:
	xorl	%eax, %eax
	xchgb	%al, (%rsi)
	cmpb	$2, %al
	je	.LBB0_40
.LBB0_36:
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
.LBB0_17:
	movb	$1, 6(%rdi)
	movb	$1, %r12b
	.p2align	4
.LBB0_18:
	cmpb	$1, 6(%rdi)
	jne	.LBB0_28
	movl	(%rdi), %r13d
	xorl	%eax, %eax
	xchgb	%al, 4(%rdi)
	cmpb	$2, %al
	je	.LBB0_20
.LBB0_21:
	movl	%r13d, -16(%rbp)
	movl	$4, %r8d
	movq	%rdi, %rcx
	leaq	-16(%rbp), %rdx
	movl	$-1, %r9d
	callq	*__imp_WaitOnAddress(%rip)
	cmpl	$1, %eax
	jne	.LBB0_22
	xorl	%eax, %eax
	lock		cmpxchgb	%r12b, (%rsi)
	jne	.LBB0_24
.LBB0_25:
	movzbl	5(%rdi), %eax
	testb	%al, %al
	je	.LBB0_18
	jmp	.LBB0_26
	.p2align	4
.LBB0_22:
	callq	*__imp_GetLastError(%rip)
	xorl	%eax, %eax
	lock		cmpxchgb	%r12b, (%rsi)
	je	.LBB0_25
.LBB0_24:
	movq	%rsi, %rcx
	callq	_RNvMNtNtNtNtCse0R8cuyqEa_3std3sys4sync5mutex5futexNtB2_5Mutex14lock_contended
	movzbl	5(%rdi), %eax
	testb	%al, %al
	je	.LBB0_18
	jmp	.LBB0_26
.LBB0_20:
	movq	%rsi, %rcx
	callq	*__imp_WakeByAddressSingle(%rip)
	jmp	.LBB0_21
.LBB0_26:
	movq	%rsi, -16(%rbp)
	movb	%r15b, -8(%rbp)
.Ltmp2:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.3(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.28.llvm.17002324475202138184(%rip), %rcx
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.27.llvm.17002324475202138184(%rip), %r9
	leaq	-16(%rbp), %r8
	movl	$43, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core6result13unwrap_failed
	nop
.Ltmp3:
	jmp	.LBB0_9
.LBB0_3:
	movq	%rcx, %r12
	movq	%rsi, %rcx
	movq	%r9, %r13
	callq	_RNvMNtNtNtNtCse0R8cuyqEa_3std3sys4sync5mutex5futexNtB2_5Mutex14lock_contended
	movq	%r13, %r9
	movq	%r12, %rcx
	jmp	.LBB0_4
.LBB0_6:
	movq	%rcx, %r15
	movq	%r9, %r12
	callq	_RNvNtNtCse0R8cuyqEa_3std9panicking11panic_count17is_zero_slow_path
	movq	%r12, %r9
	movq	%r15, %rcx
	movl	%eax, %r15d
	xorb	$1, %r15b
	movzbl	5(%rdi), %eax
	testb	%al, %al
	je	.LBB0_11
.LBB0_8:
	movq	%rsi, -16(%rbp)
	movb	%r15b, -8(%rbp)
.Ltmp0:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.2(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.28.llvm.17002324475202138184(%rip), %rcx
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.27.llvm.17002324475202138184(%rip), %r9
	leaq	-16(%rbp), %r8
	movl	$43, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core6result13unwrap_failed
	nop
.Ltmp1:
.LBB0_9:
	ud2
.LBB0_40:
	movq	%rsi, %rcx
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
	rex64 jmpq	*__imp_WakeByAddressSingle(%rip)
.LBB0_33:
	callq	_RNvNtNtCse0R8cuyqEa_3std9panicking11panic_count17is_zero_slow_path
	testb	%al, %al
	jne	.LBB0_35
	movb	$1, 5(%rdi)
	jmp	.LBB0_35
.LBB0_10:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.1(%rip), %r8
	movq	%r15, %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RINvMNtCs98fvGvYc57G_10rayon_core5sleepNtB3_5Sleep5sleepNCNvMs8_NtB5_8registryNtB10_12WorkerThread15wait_until_cold0EB5_.llvm.17002324475202138184@IMGREL
	.section	.text$unlikely,"xr",one_only,_RINvMNtCs98fvGvYc57G_10rayon_core5sleepNtB3_5Sleep5sleepNCNvMs8_NtB5_8registryNtB10_12WorkerThread15wait_until_cold0EB5_.llvm.17002324475202138184,unique,0
	.seh_endproc
	.def	"?dtor$38@?0?_RINvMNtCs98fvGvYc57G_10rayon_core5sleepNtB3_5Sleep5sleepNCNvMs8_NtB5_8registryNtB10_12WorkerThread15wait_until_cold0EB5_.llvm.17002324475202138184@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$38@?0?_RINvMNtCs98fvGvYc57G_10rayon_core5sleepNtB3_5Sleep5sleepNCNvMs8_NtB5_8registryNtB10_12WorkerThread15wait_until_cold0EB5_.llvm.17002324475202138184@4HA":
.seh_proc "?dtor$38@?0?_RINvMNtCs98fvGvYc57G_10rayon_core5sleepNtB3_5Sleep5sleepNCNvMs8_NtB5_8registryNtB10_12WorkerThread15wait_until_cold0EB5_.llvm.17002324475202138184@4HA"
.LBB0_38:
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
	leaq	64(%rdx), %rbp
	.seh_endprologue
	leaq	-16(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCse0R8cuyqEa_3std4sync6poison11PoisonErrorINtNtBE_5mutex10MutexGuardbEEECs98fvGvYc57G_10rayon_core.llvm.17002324475202138184
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
	.section	.text$unlikely,"xr",one_only,_RINvMNtCs98fvGvYc57G_10rayon_core5sleepNtB3_5Sleep5sleepNCNvMs8_NtB5_8registryNtB10_12WorkerThread15wait_until_cold0EB5_.llvm.17002324475202138184,unique,0
	.seh_endproc
	.def	"?dtor$39@?0?_RINvMNtCs98fvGvYc57G_10rayon_core5sleepNtB3_5Sleep5sleepNCNvMs8_NtB5_8registryNtB10_12WorkerThread15wait_until_cold0EB5_.llvm.17002324475202138184@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$39@?0?_RINvMNtCs98fvGvYc57G_10rayon_core5sleepNtB3_5Sleep5sleepNCNvMs8_NtB5_8registryNtB10_12WorkerThread15wait_until_cold0EB5_.llvm.17002324475202138184@4HA":
.seh_proc "?dtor$39@?0?_RINvMNtCs98fvGvYc57G_10rayon_core5sleepNtB3_5Sleep5sleepNCNvMs8_NtB5_8registryNtB10_12WorkerThread15wait_until_cold0EB5_.llvm.17002324475202138184@4HA"
.LBB0_39:
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
	leaq	64(%rdx), %rbp
	.seh_endprologue
	leaq	-16(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCse0R8cuyqEa_3std4sync6poison11PoisonErrorINtNtBE_5mutex10MutexGuardbEEECs98fvGvYc57G_10rayon_core.llvm.17002324475202138184
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
.Lfunc_end0:
	.seh_handlerdata
	.section	.text$unlikely,"xr",one_only,_RINvMNtCs98fvGvYc57G_10rayon_core5sleepNtB3_5Sleep5sleepNCNvMs8_NtB5_8registryNtB10_12WorkerThread15wait_until_cold0EB5_.llvm.17002324475202138184,unique,0
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvMNtCs98fvGvYc57G_10rayon_core5sleepNtB3_5Sleep5sleepNCNvMs8_NtB5_8registryNtB10_12WorkerThread15wait_until_cold0EB5_.llvm.17002324475202138184,unique,0
	.p2align	2, 0x0
$cppxdata$_RINvMNtCs98fvGvYc57G_10rayon_core5sleepNtB3_5Sleep5sleepNCNvMs8_NtB5_8registryNtB10_12WorkerThread15wait_until_cold0EB5_.llvm.17002324475202138184:
	.long	429065506
	.long	2
	.long	$stateUnwindMap$_RINvMNtCs98fvGvYc57G_10rayon_core5sleepNtB3_5Sleep5sleepNCNvMs8_NtB5_8registryNtB10_12WorkerThread15wait_until_cold0EB5_.llvm.17002324475202138184@IMGREL
	.long	0
	.long	0
	.long	5
	.long	$ip2state$_RINvMNtCs98fvGvYc57G_10rayon_core5sleepNtB3_5Sleep5sleepNCNvMs8_NtB5_8registryNtB10_12WorkerThread15wait_until_cold0EB5_.llvm.17002324475202138184@IMGREL
	.long	64
	.long	0
	.long	1
$stateUnwindMap$_RINvMNtCs98fvGvYc57G_10rayon_core5sleepNtB3_5Sleep5sleepNCNvMs8_NtB5_8registryNtB10_12WorkerThread15wait_until_cold0EB5_.llvm.17002324475202138184:
	.long	-1
	.long	"?dtor$38@?0?_RINvMNtCs98fvGvYc57G_10rayon_core5sleepNtB3_5Sleep5sleepNCNvMs8_NtB5_8registryNtB10_12WorkerThread15wait_until_cold0EB5_.llvm.17002324475202138184@4HA"@IMGREL
	.long	-1
	.long	"?dtor$39@?0?_RINvMNtCs98fvGvYc57G_10rayon_core5sleepNtB3_5Sleep5sleepNCNvMs8_NtB5_8registryNtB10_12WorkerThread15wait_until_cold0EB5_.llvm.17002324475202138184@4HA"@IMGREL
$ip2state$_RINvMNtCs98fvGvYc57G_10rayon_core5sleepNtB3_5Sleep5sleepNCNvMs8_NtB5_8registryNtB10_12WorkerThread15wait_until_cold0EB5_.llvm.17002324475202138184:
	.long	.Lfunc_begin0@IMGREL
	.long	-1
	.long	.Ltmp2@IMGREL
	.long	1
	.long	.Ltmp3@IMGREL
	.long	-1
	.long	.Ltmp0@IMGREL
	.long	0
	.long	.Ltmp1@IMGREL
	.long	-1
	.section	.text$unlikely,"xr",one_only,_RINvMNtCs98fvGvYc57G_10rayon_core5sleepNtB3_5Sleep5sleepNCNvMs8_NtB5_8registryNtB10_12WorkerThread15wait_until_cold0EB5_.llvm.17002324475202138184,unique,0

	.def	_RINvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazyINtB6_7StorageNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleuE16get_or_init_slowNvNvNtB1h_7default6HANDLE27___rust_std_internal_init_fnECs98fvGvYc57G_10rayon_core;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazyINtB6_7StorageNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleuE16get_or_init_slowNvNvNtB1h_7default6HANDLE27___rust_std_internal_init_fnECs98fvGvYc57G_10rayon_core,unique,1
	.p2align	4
_RINvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazyINtB6_7StorageNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleuE16get_or_init_slowNvNvNtB1h_7default6HANDLE27___rust_std_internal_init_fnECs98fvGvYc57G_10rayon_core:
.Lfunc_begin1:
.seh_proc _RINvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazyINtB6_7StorageNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleuE16get_or_init_slowNvNvNtB1h_7default6HANDLE27___rust_std_internal_init_fnECs98fvGvYc57G_10rayon_core
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
	movl	$4560, %eax
	callq	__chkstk
	subq	%rax, %rsp
	.seh_stackalloc 4560
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	andq	$-128, %rsp
	movq	%rsp, %rbx
	movq	%rbp, 4544(%rbx)
	movq	$-2, 4424(%rbp)
	movq	%rcx, %rsi
	movzbl	8(%rcx), %eax
	testl	%eax, %eax
	je	.LBB1_3
	cmpl	$1, %eax
	je	.LBB1_25
	xorl	%esi, %esi
	jmp	.LBB1_25
.LBB1_3:
	movl	_RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default9collector9COLLECTOR.llvm.14389155381977926352+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB1_4
	movq	_RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default9collector9COLLECTOR.llvm.14389155381977926352(%rip), %r14
	lock		incq	(%r14)
	jle	.LBB1_10
.LBB1_6:
	movl	$96, %eax
	movups	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352+16(%rip), %xmm0
	movups	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352(%rip), %xmm1
	.p2align	4
.LBB1_7:
	movups	%xmm0, 2416(%rbx,%rax)
	movups	%xmm1, 2400(%rbx,%rax)
	movups	%xmm1, 2432(%rbx,%rax)
	movups	%xmm0, 2448(%rbx,%rax)
	movups	%xmm1, 2464(%rbx,%rax)
	movups	%xmm0, 2480(%rbx,%rax)
	movups	%xmm1, 2496(%rbx,%rax)
	movups	%xmm0, 2512(%rbx,%rax)
	subq	$-128, %rax
	cmpq	$2144, %rax
	jne	.LBB1_7
	movq	$0, 128(%rbx)
	movq	%r14, 136(%rbx)
	leaq	144(%rbx), %rcx
	leaq	2496(%rbx), %rdx
	movl	$2048, %r8d
	callq	memcpy
	xorps	%xmm0, %xmm0
	movaps	%xmm0, 2192(%rbx)
	movq	$1, 2208(%rbx)
	movq	$0, 2216(%rbx)
	movq	$0, 2304(%rbx)
	movl	$2304, %ecx
	movl	$128, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB1_9
	movq	%rax, %rdi
	leaq	128(%rbx), %rdx
	movl	$2304, %r8d
	movq	%rax, %rcx
	callq	memcpy
	movq	512(%r14), %rax
	.p2align	4
.LBB1_13:
	movq	%rax, (%rdi)
	lock		cmpxchgq	%rdi, 512(%r14)
	jne	.LBB1_13
	movzbl	8(%rsi), %eax
	movq	(%rsi), %rcx
	movq	%rdi, (%rsi)
	movb	$1, 8(%rsi)
	cmpl	$1, %eax
	jne	.LBB1_15
	movq	2080(%rcx), %rax
	leaq	-1(%rax), %rdx
	movq	%rdx, 2080(%rcx)
	xorq	$1, %rax
	orq	2072(%rcx), %rax
	jne	.LBB1_25
	callq	_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize
	jmp	.LBB1_25
.LBB1_15:
	testl	%eax, %eax
	jne	.LBB1_26
	movl	_tls_index(%rip), %eax
	movq	%gs:88, %rcx
	movq	(%rcx,%rax,8), %rax
	cmpq	$0, _RNvNtNtNtNtCse0R8cuyqEa_3std3sys12thread_local11destructors4list5DTORS.llvm.18153159449376349941@SECREL32(%rax)
	jne	.LBB1_21
	leaq	_RNvNtNtNtNtCse0R8cuyqEa_3std3sys12thread_local11destructors4list5DTORS.llvm.18153159449376349941@SECREL32(%rax), %rax
	movq	%rax, 120(%rbx)
	movq	$-1, (%rax)
.Ltmp4:
	callq	_RNvNtNtNtNtCse0R8cuyqEa_3std3sys12thread_local5guard7windows6enable.llvm.18153159449376349941
	nop
.Ltmp5:
	movq	120(%rbx), %rax
	movq	24(%rax), %rdi
	cmpq	8(%rax), %rdi
	jne	.LBB1_20
.Ltmp6:
	movq	120(%rbx), %rax
	leaq	8(%rax), %rcx
	callq	_RNvMs4_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB5_6RawVecTOhFUKCBN_EuENtNtCse0R8cuyqEa_3std5alloc6SystemE8grow_oneB13_
	nop
.Ltmp7:
.LBB1_20:
	movq	120(%rbx), %r8
	movq	16(%r8), %rax
	movq	%rdi, %rcx
	shlq	$4, %rcx
	movq	%rsi, (%rax,%rcx)
	leaq	_RINvNtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazy7destroyNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleECs98fvGvYc57G_10rayon_core(%rip), %rdx
	movq	%rdx, 8(%rax,%rcx)
	incq	%rdi
	movq	%rdi, 24(%r8)
	incq	(%r8)
.LBB1_25:
	movq	%rsi, %rax
	.seh_startepilogue
	leaq	4432(%rbp), %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.LBB1_4:
	callq	_RINvMs0_NtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync9once_lockINtB6_8OnceLockNtNtBa_9collector9CollectorE10initializeNvMs1_B1b_B19_3newEBa_.llvm.14389155381977926352
	movq	_RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default9collector9COLLECTOR.llvm.14389155381977926352(%rip), %r14
	lock		incq	(%r14)
	jg	.LBB1_6
.LBB1_10:
	ud2
.LBB1_9:
.Ltmp8:
	movl	$128, %ecx
	movl	$2304, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp9:
	jmp	.LBB1_10
.LBB1_26:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.6(%rip), %rcx
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.8(%rip), %r8
	movl	$40, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking5panic
	ud2
.LBB1_21:
	movl	$0, 128(%rbx)
	movb	$0, 132(%rbx)
	leaq	anon.81f07c260754ecc8ec7a6d2dde9eb3e4.405.llvm.18153159449376349941(%rip), %rdx
	leaq	128(%rbx), %rcx
	movl	$171, %r8d
	callq	_RNvYNtNtNtNtCse0R8cuyqEa_3std3sys5stdio7windows6StderrNtNtBa_2io5Write9write_fmtBa_.llvm.18153159449376349941
	movq	%rax, %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultuNtNtNtB4_2io5error5ErrorEECse0R8cuyqEa_3std.llvm.18153159449376349941
	movl	$7, %ecx
	#APP

	int	$41

	#NO_APP
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RINvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazyINtB6_7StorageNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleuE16get_or_init_slowNvNvNtB1h_7default6HANDLE27___rust_std_internal_init_fnECs98fvGvYc57G_10rayon_core@IMGREL
	.section	.text$unlikely,"xr",one_only,_RINvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazyINtB6_7StorageNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleuE16get_or_init_slowNvNvNtB1h_7default6HANDLE27___rust_std_internal_init_fnECs98fvGvYc57G_10rayon_core,unique,1
	.seh_endproc
	.def	"?dtor$11@?0?_RINvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazyINtB6_7StorageNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleuE16get_or_init_slowNvNvNtB1h_7default6HANDLE27___rust_std_internal_init_fnECs98fvGvYc57G_10rayon_core@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$11@?0?_RINvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazyINtB6_7StorageNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleuE16get_or_init_slowNvNvNtB1h_7default6HANDLE27___rust_std_internal_init_fnECs98fvGvYc57G_10rayon_core@4HA":
.seh_proc "?dtor$11@?0?_RINvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazyINtB6_7StorageNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleuE16get_or_init_slowNvNvNtB1h_7default6HANDLE27___rust_std_internal_init_fnECs98fvGvYc57G_10rayon_core@4HA"
.LBB1_11:
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	leaq	128(%rbx), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs3qjAvHHmxHz_15crossbeam_epoch8internal5LocalEBF_.llvm.14389155381977926352
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
	.section	.text$unlikely,"xr",one_only,_RINvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazyINtB6_7StorageNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleuE16get_or_init_slowNvNvNtB1h_7default6HANDLE27___rust_std_internal_init_fnECs98fvGvYc57G_10rayon_core,unique,1
	.seh_endproc
	.def	"?dtor$22@?0?_RINvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazyINtB6_7StorageNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleuE16get_or_init_slowNvNvNtB1h_7default6HANDLE27___rust_std_internal_init_fnECs98fvGvYc57G_10rayon_core@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$22@?0?_RINvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazyINtB6_7StorageNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleuE16get_or_init_slowNvNvNtB1h_7default6HANDLE27___rust_std_internal_init_fnECs98fvGvYc57G_10rayon_core@4HA":
.seh_proc "?dtor$22@?0?_RINvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazyINtB6_7StorageNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleuE16get_or_init_slowNvNvNtB1h_7default6HANDLE27___rust_std_internal_init_fnECs98fvGvYc57G_10rayon_core@4HA"
.LBB1_22:
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	movq	120(%rbx), %rax
	incq	(%rax)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end1:
	.seh_handlerdata
	.section	.text$unlikely,"xr",one_only,_RINvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazyINtB6_7StorageNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleuE16get_or_init_slowNvNvNtB1h_7default6HANDLE27___rust_std_internal_init_fnECs98fvGvYc57G_10rayon_core,unique,1
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazyINtB6_7StorageNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleuE16get_or_init_slowNvNvNtB1h_7default6HANDLE27___rust_std_internal_init_fnECs98fvGvYc57G_10rayon_core,unique,1
	.p2align	2, 0x0
$cppxdata$_RINvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazyINtB6_7StorageNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleuE16get_or_init_slowNvNvNtB1h_7default6HANDLE27___rust_std_internal_init_fnECs98fvGvYc57G_10rayon_core:
	.long	429065506
	.long	2
	.long	$stateUnwindMap$_RINvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazyINtB6_7StorageNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleuE16get_or_init_slowNvNvNtB1h_7default6HANDLE27___rust_std_internal_init_fnECs98fvGvYc57G_10rayon_core@IMGREL
	.long	0
	.long	0
	.long	5
	.long	$ip2state$_RINvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazyINtB6_7StorageNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleuE16get_or_init_slowNvNvNtB1h_7default6HANDLE27___rust_std_internal_init_fnECs98fvGvYc57G_10rayon_core@IMGREL
	.long	4552
	.long	0
	.long	1
$stateUnwindMap$_RINvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazyINtB6_7StorageNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleuE16get_or_init_slowNvNvNtB1h_7default6HANDLE27___rust_std_internal_init_fnECs98fvGvYc57G_10rayon_core:
	.long	-1
	.long	"?dtor$11@?0?_RINvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazyINtB6_7StorageNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleuE16get_or_init_slowNvNvNtB1h_7default6HANDLE27___rust_std_internal_init_fnECs98fvGvYc57G_10rayon_core@4HA"@IMGREL
	.long	-1
	.long	"?dtor$22@?0?_RINvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazyINtB6_7StorageNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleuE16get_or_init_slowNvNvNtB1h_7default6HANDLE27___rust_std_internal_init_fnECs98fvGvYc57G_10rayon_core@4HA"@IMGREL
$ip2state$_RINvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazyINtB6_7StorageNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleuE16get_or_init_slowNvNvNtB1h_7default6HANDLE27___rust_std_internal_init_fnECs98fvGvYc57G_10rayon_core:
	.long	.Lfunc_begin1@IMGREL
	.long	-1
	.long	.Ltmp4@IMGREL
	.long	1
	.long	.Ltmp7@IMGREL
	.long	-1
	.long	.Ltmp8@IMGREL
	.long	0
	.long	.Ltmp9@IMGREL
	.long	-1
	.section	.text$unlikely,"xr",one_only,_RINvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazyINtB6_7StorageNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleuE16get_or_init_slowNvNvNtB1h_7default6HANDLE27___rust_std_internal_init_fnECs98fvGvYc57G_10rayon_core,unique,1

	.def	_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_,unique,2
	.p2align	4
_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_:
.Lfunc_begin2:
.seh_proc _RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_
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
	subq	$1208, %rsp
	.seh_stackalloc 1208
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	movaps	%xmm6, 1056(%rbp)
	.seh_savexmm %xmm6, 1184
	.seh_endprologue
	andq	$-128, %rsp
	movq	%rsp, %rbx
	movq	%rbp, 1168(%rbx)
	movq	$-2, 1048(%rbp)
	movq	%rdx, %r15
	movq	%rcx, %r12
	movq	16(%rdx), %r14
	testq	%r14, %r14
	movq	%rdx, 120(%rbx)
	jne	.LBB2_84
.Ltmp10:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.34(%rip), %rdx
	leaq	512(%rbx), %rcx
	movl	$17, %r8d
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys3env7windows6getenv
	nop
.Ltmp11:
	movq	512(%rbx), %r8
	cmpq	$-1, %r8
	je	.LBB2_43
	movq	520(%rbx), %rcx
	movq	528(%rbx), %r9
	testb	$1, 536(%rbx)
	je	.LBB2_8
.LBB2_4:
	testq	%r9, %r9
	je	.LBB2_21
	cmpq	$1, %r9
	jne	.LBB2_27
	movzbl	(%rcx), %eax
	xorl	%esi, %esi
	cmpl	$43, %eax
	je	.LBB2_23
	cmpl	$45, %eax
	je	.LBB2_23
	jmp	.LBB2_28
.LBB2_8:
	testq	%r9, %r9
	je	.LBB2_21
	leaq	(%rcx,%r9), %rax
	movq	%rcx, %r10
	jmp	.LBB2_12
.LBB2_10:
	addq	$2, %r10
	cmpq	%rax, %rdx
	cmovneq	%r10, %rdx
	.p2align	4
.LBB2_11:
	movq	%rdx, %r10
	cmpq	%rax, %rdx
	je	.LBB2_4
.LBB2_12:
	leaq	1(%r10), %rdx
	movzbl	(%r10), %r11d
	testb	%r11b, %r11b
	jns	.LBB2_11
	cmpb	$-32, %r11b
	jb	.LBB2_10
	cmpb	$-19, %r11b
	jne	.LBB2_19
	cmpq	%rax, %rdx
	je	.LBB2_4
	leaq	2(%r10), %rdx
	cmpq	%rax, %rdx
	je	.LBB2_4
	cmpb	$-97, 1(%r10)
	ja	.LBB2_41
	addq	$3, %r10
	movq	%r10, %rdx
	jmp	.LBB2_11
.LBB2_19:
	addq	$2, %r10
	cmpq	%rax, %rdx
	cmoveq	%rdx, %r10
	xorl	%edx, %edx
	cmpq	%rax, %r10
	setne	%dl
	addq	%r10, %rdx
	cmpb	$-16, %r11b
	jb	.LBB2_11
	xorl	%r10d, %r10d
	cmpq	%rax, %rdx
	setne	%r10b
	addq	%r10, %rdx
	jmp	.LBB2_11
.LBB2_21:
	xorl	%esi, %esi
.LBB2_22:
.LBB2_23:
	testq	%r8, %r8
	je	.LBB2_25
	callq	mi_free
.LBB2_25:
	testb	%sil, %sil
	je	.LBB2_43
	testq	%r14, %r14
	movq	120(%rbx), %r15
	jne	.LBB2_84
	jmp	.LBB2_83
.LBB2_27:
	movzbl	(%rcx), %eax
.LBB2_28:
	xorl	%r10d, %r10d
	cmpb	$43, %al
	sete	%r10b
	movq	%r10, %rax
	negq	%rax
	movq	%r9, %rdx
	subq	%r10, %rdx
	addq	%rcx, %r10
	cmpq	$17, %rdx
	jae	.LBB2_33
	testq	%rdx, %rdx
	je	.LBB2_39
	addq	%rax, %r9
	negq	%r9
	xorl	%r14d, %r14d
	xorl	%eax, %eax
	.p2align	4
.LBB2_31:
	movzbl	(%r10,%rax), %edx
	addl	$-48, %edx
	cmpl	$10, %edx
	setb	%sil
	jae	.LBB2_22
	leaq	(%r14,%r14,4), %r11
	movl	%edx, %edx
	leaq	(%rdx,%r11,2), %r14
	incq	%rax
	movq	%r9, %rdx
	addq	%rax, %rdx
	jne	.LBB2_31
	jmp	.LBB2_23
.LBB2_33:
	addq	%rax, %r9
	negq	%r9
	xorl	%r14d, %r14d
	movl	$10, %r11d
	xorl	%edi, %edi
.LBB2_34:
	movq	%r9, %rax
	addq	%rdi, %rax
	sete	%sil
	je	.LBB2_23
	movq	%r14, %rax
	mulq	%r11
	jo	.LBB2_22
	movq	%rax, %r14
	movzbl	(%r10,%rdi), %edx
	addl	$-48, %edx
	addq	%rdx, %r14
	setb	%al
	cmpl	$9, %edx
	ja	.LBB2_22
	incq	%rdi
	testb	%al, %al
	je	.LBB2_34
	jmp	.LBB2_23
.LBB2_39:
	movb	$1, %sil
	xorl	%r14d, %r14d
	jmp	.LBB2_23
.LBB2_41:
	testq	%r8, %r8
	jle	.LBB2_43
	callq	mi_free
	nop
.LBB2_43:
.Ltmp12:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.35(%rip), %rdx
	leaq	512(%rbx), %rcx
	movl	$17, %r8d
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys3env7windows6getenv
	nop
.Ltmp13:
	movq	512(%rbx), %r8
	cmpq	$-1, %r8
	je	.LBB2_50
	movq	520(%rbx), %rcx
	movq	528(%rbx), %r9
	testb	$1, 536(%rbx)
	movq	120(%rbx), %r15
	je	.LBB2_51
.LBB2_46:
	movb	$1, %sil
	testq	%r9, %r9
	je	.LBB2_64
	cmpq	$1, %r9
	jne	.LBB2_65
	movzbl	(%rcx), %eax
	cmpl	$43, %eax
	je	.LBB2_80
	cmpl	$45, %eax
	je	.LBB2_80
	jmp	.LBB2_66
.LBB2_50:
	movq	120(%rbx), %r15
	jmp	.LBB2_83
.LBB2_51:
	testq	%r9, %r9
	je	.LBB2_71
	leaq	(%rcx,%r9), %rax
	movq	%rcx, %r10
	jmp	.LBB2_55
.LBB2_53:
	addq	$2, %r10
	cmpq	%rax, %rdx
	cmovneq	%r10, %rdx
	.p2align	4
.LBB2_54:
	movq	%rdx, %r10
	cmpq	%rax, %rdx
	je	.LBB2_46
.LBB2_55:
	leaq	1(%r10), %rdx
	movzbl	(%r10), %r11d
	testb	%r11b, %r11b
	jns	.LBB2_54
	cmpb	$-32, %r11b
	jb	.LBB2_53
	cmpb	$-19, %r11b
	jne	.LBB2_62
	cmpq	%rax, %rdx
	je	.LBB2_46
	leaq	2(%r10), %rdx
	cmpq	%rax, %rdx
	je	.LBB2_46
	cmpb	$-97, 1(%r10)
	ja	.LBB2_164
	addq	$3, %r10
	movq	%r10, %rdx
	jmp	.LBB2_54
.LBB2_62:
	addq	$2, %r10
	cmpq	%rax, %rdx
	cmoveq	%rdx, %r10
	xorl	%edx, %edx
	cmpq	%rax, %r10
	setne	%dl
	addq	%r10, %rdx
	cmpb	$-16, %r11b
	jb	.LBB2_54
	xorl	%r10d, %r10d
	cmpq	%rax, %rdx
	setne	%r10b
	addq	%r10, %rdx
	jmp	.LBB2_54
.LBB2_65:
	movzbl	(%rcx), %eax
.LBB2_66:
	xorl	%r10d, %r10d
	cmpb	$43, %al
	sete	%r10b
	movq	%r10, %rax
	negq	%rax
	movq	%r9, %rdx
	subq	%r10, %rdx
	addq	%rcx, %r10
	cmpq	$17, %rdx
	jae	.LBB2_72
	testq	%rdx, %rdx
	je	.LBB2_78
	addq	%rax, %r9
	negq	%r9
	xorl	%r14d, %r14d
	xorl	%eax, %eax
	.p2align	4
.LBB2_69:
	movzbl	(%r10,%rax), %edx
	addl	$-48, %edx
	cmpl	$10, %edx
	setae	%sil
	jae	.LBB2_79
	leaq	(%r14,%r14,4), %r11
	movl	%edx, %edx
	leaq	(%rdx,%r11,2), %r14
	incq	%rax
	movq	%r9, %rdx
	addq	%rax, %rdx
	jne	.LBB2_69
	jmp	.LBB2_80
.LBB2_71:
	movb	$1, %sil
	testq	%r8, %r8
	jne	.LBB2_81
	jmp	.LBB2_82
.LBB2_72:
	addq	%rax, %r9
	negq	%r9
	xorl	%r14d, %r14d
	movl	$10, %r11d
	xorl	%edi, %edi
.LBB2_73:
	movq	%r9, %rax
	addq	%rdi, %rax
	setne	%sil
	je	.LBB2_80
	movq	%r14, %rax
	mulq	%r11
	jo	.LBB2_64
	movq	%rax, %r14
	movzbl	(%r10,%rdi), %edx
	addl	$-48, %edx
	addq	%rdx, %r14
	setb	%al
	cmpl	$9, %edx
	ja	.LBB2_64
	incq	%rdi
	testb	%al, %al
	je	.LBB2_73
	jmp	.LBB2_80
.LBB2_64:
	testq	%r8, %r8
	jne	.LBB2_81
	jmp	.LBB2_82
.LBB2_78:
	xorl	%r14d, %r14d
	xorl	%esi, %esi
	testq	%r8, %r8
	jne	.LBB2_81
	jmp	.LBB2_82
.LBB2_79:
.LBB2_80:
	testq	%r8, %r8
	je	.LBB2_82
.LBB2_81:
	callq	mi_free
.LBB2_82:
	testq	%r14, %r14
	sete	%al
	orb	%al, %sil
	cmpb	$1, %sil
	jne	.LBB2_84
.LBB2_83:
	xorps	%xmm0, %xmm0
	movaps	%xmm0, 544(%rbx)
	movaps	%xmm0, 528(%rbx)
	movaps	%xmm0, 512(%rbx)
	leaq	512(%rbx), %rcx
	callq	*__imp_GetSystemInfo(%rip)
	movl	544(%rbx), %r14d
	cmpl	$1, %r14d
	adcl	$0, %r14d
.LBB2_84:
	movq	%r12, 256(%rbx)
	cmpq	$65535, %r14
	movl	$65535, %r8d
	cmovbq	%r14, %r8
	movb	89(%r15), %r12b
	movq	$0, 168(%rbx)
	movq	$8, 176(%rbx)
	xorps	%xmm0, %xmm0
	movups	%xmm0, 184(%rbx)
	movq	$8, 200(%rbx)
	movq	$0, 208(%rbx)
.Ltmp14:
	leaq	168(%rbx), %rcx
	movl	$32, %r9d
	xorl	%edx, %edx
	movq	%r8, 104(%rbx)
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECs98fvGvYc57G_10rayon_core
	nop
.Ltmp15:
	movq	192(%rbx), %rax
	movq	208(%rbx), %r15
	subq	%r15, %rax
	cmpq	%rax, 104(%rbx)
	ja	.LBB2_168
.LBB2_86:
	movq	176(%rbx), %rax
	movq	%rax, 152(%rbx)
	movq	184(%rbx), %r13
	movq	200(%rbx), %rax
	movq	%rax, 112(%rbx)
	leaq	768(%rbx), %rdi
	xorl	%r14d, %r14d
	xorps	%xmm6, %xmm6
	.p2align	4
.LBB2_87:
	movq	%r15, 160(%rbx)
	testb	%r12b, %r12b
	je	.LBB2_90
.Ltmp24:
	leaq	512(%rbx), %rcx
	callq	_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE8new_fifoBZ_
	nop
.Ltmp25:
	movq	512(%rbx), %r15
	jmp	.LBB2_94
	.p2align	4
.LBB2_90:
	movl	$1024, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB2_176
	movq	%rax, %rsi
	movl	$16, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB2_162
	movq	%rsi, (%rax)
	movq	$64, 8(%rax)
	movq	$1, 512(%rbx)
	movq	$1, 520(%rbx)
	movq	%rax, 640(%rbx)
	movaps	%xmm6, (%rdi)
	movl	$384, %ecx
	movl	$128, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB2_163
	movq	%rax, %r15
	movl	$384, %r8d
	movq	%rax, %rcx
	leaq	512(%rbx), %rdx
	callq	memcpy
	movq	%r15, 512(%rbx)
	movq	%rsi, 520(%rbx)
	movq	$64, 528(%rbx)
	movb	$1, 536(%rbx)
.LBB2_94:
	lock		incq	(%r15)
	jle	.LBB2_179
	incq	%r14
	movzbl	536(%rbx), %eax
	movups	512(%rbx), %xmm0
	movups	528(%rbx), %xmm1
	movaps	%xmm0, 272(%rbx)
	movaps	%xmm1, 288(%rbx)
	movq	%r13, %rcx
	shlq	$5, %rcx
	movq	152(%rbx), %rdx
	movups	%xmm1, 16(%rdx,%rcx)
	movups	%xmm0, (%rdx,%rcx)
	movq	%r13, %rdx
	incq	%r13
	movq	%r13, 184(%rbx)
	movq	160(%rbx), %r9
	movq	%r9, %rcx
	shlq	$4, %rcx
	movq	112(%rbx), %r8
	movq	%r15, (%r8,%rcx)
	movb	%al, 8(%r8,%rcx)
	leaq	1(%r9), %r15
	movq	%r15, 208(%rbx)
	cmpq	104(%rbx), %r14
	jne	.LBB2_87
	movq	%rdx, 360(%rbx)
	movq	168(%rbx), %rax
	movq	%rax, 320(%rbx)
	movq	192(%rbx), %rax
	movq	%rax, 264(%rbx)
	movq	$0, 512(%rbx)
	movq	$8, 520(%rbx)
	xorps	%xmm0, %xmm0
	movups	%xmm0, 528(%rbx)
	movq	$8, 544(%rbx)
	movq	$0, 552(%rbx)
.Ltmp26:
	leaq	512(%rbx), %rcx
	movl	$32, %r9d
	xorl	%edx, %edx
	movq	104(%rbx), %r8
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECs98fvGvYc57G_10rayon_core
	nop
.Ltmp27:
	movq	536(%rbx), %rax
	movq	552(%rbx), %r14
	subq	%r14, %rax
	cmpq	%rax, 104(%rbx)
	ja	.LBB2_170
.LBB2_98:
	movq	520(%rbx), %rax
	movq	%rax, 144(%rbx)
	movq	528(%rbx), %r12
	movq	544(%rbx), %rax
	movq	%rax, 136(%rbx)
	xorl	%edi, %edi
	leaq	168(%rbx), %rsi
	.p2align	4
.LBB2_99:
.Ltmp30:
	movq	%r14, 336(%rbx)
	movq	%rsi, %rcx
	callq	_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE8new_fifoBZ_
	nop
.Ltmp31:
	movq	168(%rbx), %rax
	lock		incq	(%rax)
	jle	.LBB2_179
	incq	%rdi
	movzbl	192(%rbx), %ecx
	movups	168(%rbx), %xmm0
	movups	184(%rbx), %xmm1
	movaps	%xmm0, 272(%rbx)
	movaps	%xmm1, 288(%rbx)
	movq	%r12, %rdx
	shlq	$5, %rdx
	movq	144(%rbx), %r8
	movups	%xmm1, 16(%r8,%rdx)
	movups	%xmm0, (%r8,%rdx)
	movq	%r12, %r8
	incq	%r12
	movq	%r12, 528(%rbx)
	movq	336(%rbx), %r10
	movq	%r10, %rdx
	shlq	$4, %rdx
	movq	136(%rbx), %r9
	movq	%rax, (%r9,%rdx)
	movb	%cl, 8(%r9,%rdx)
	leaq	1(%r10), %r14
	movq	%r14, 552(%rbx)
	cmpq	104(%rbx), %rdi
	jne	.LBB2_99
	movq	%r8, 352(%rbx)
	movq	512(%rbx), %rdi
	movq	536(%rbx), %rax
	movq	%rax, 312(%rbx)
	leaq	(,%r15,8), %rax
	leaq	(%rax,%rax,4), %rsi
	movabsq	$230584300921369394, %rax
	cmpq	%rax, 160(%rbx)
	movq	%rdi, 304(%rbx)
	jbe	.LBB2_105
	xorl	%ecx, %ecx
.LBB2_104:
.Ltmp58:
	movq	%rsi, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp59:
	jmp	.LBB2_179
.LBB2_105:
	testq	%rsi, %rsi
	je	.LBB2_107
	movl	$8, %edx
	movq	%rsi, %rcx
	callq	mi_malloc_aligned
	movl	$8, %ecx
	movq	%r15, %r10
	testq	%rax, %rax
	jne	.LBB2_108
	jmp	.LBB2_104
.LBB2_107:
	movl	$8, %eax
	xorl	%r10d, %r10d
.LBB2_108:
	shlq	$4, %r15
	movq	112(%rbx), %rcx
	addq	%rcx, %r15
	leaq	32(%rax), %r9
	xorl	%esi, %esi
	xorps	%xmm0, %xmm0
	.p2align	4
.LBB2_109:
	movq	(%rcx), %rdx
	movzbl	8(%rcx), %r8d
	movups	%xmm0, -32(%r9)
	movq	$0, -16(%r9)
	movq	%rdx, -8(%r9)
	movb	%r8b, (%r9)
	incq	%rsi
	addq	$40, %r9
	addq	$16, %rcx
	cmpq	%r15, %rcx
	jne	.LBB2_109
	cmpq	$0, 264(%rbx)
	je	.LBB2_112
	movq	112(%rbx), %rcx
	movq	%rax, %r15
	movq	%r10, %rdi
	callq	mi_free
	movq	%rdi, %r10
	movq	304(%rbx), %rdi
	movq	%r15, %rax
.LBB2_112:
	movq	%r10, 168(%rbx)
	movq	%rax, 176(%rbx)
	movq	%rsi, 184(%rbx)
	movq	104(%rbx), %r15
	movq	%r15, %rsi
	shlq	$7, %rsi
	movl	$128, %edx
	movq	%rsi, %rcx
	callq	mi_malloc_aligned
	movq	%rax, 128(%rbx)
	testq	%rax, %rax
	je	.LBB2_178
	leaq	-1(%r15), %rcx
	movl	%r15d, %eax
	andl	$3, %eax
	cmpq	$3, %rcx
	jae	.LBB2_115
	xorl	%ecx, %ecx
	jmp	.LBB2_118
.LBB2_115:
	movl	%r15d, %edx
	andl	$65532, %edx
	movq	128(%rbx), %rcx
	leaq	384(%rcx), %r8
	xorl	%ecx, %ecx
	.p2align	4
.LBB2_116:
	movq	$0, -384(%r8)
	movq	$0, -256(%r8)
	movq	$0, -128(%r8)
	addq	$4, %rcx
	movq	$0, (%r8)
	addq	$512, %r8
	cmpq	%rcx, %rdx
	jne	.LBB2_116
	testq	%rax, %rax
	je	.LBB2_120
.LBB2_118:
	shlq	$7, %rcx
	addq	128(%rbx), %rcx
	shll	$7, %eax
	xorl	%edx, %edx
	.p2align	4
.LBB2_119:
	movq	$0, (%rcx,%rdx)
	subq	$-128, %rdx
	cmpq	%rdx, %rax
	jne	.LBB2_119
.LBB2_120:
	movl	$1520, %ecx
	movl	$8, %edx
	callq	mi_zalloc_aligned
	testq	%rax, %rax
	je	.LBB2_172
	movq	184(%rbx), %rcx
	movq	%rcx, 1032(%rbx)
	movups	168(%rbx), %xmm0
	movups	%xmm0, 1016(%rbx)
	movq	%rdi, 904(%rbx)
	movq	144(%rbx), %rcx
	movq	%rcx, 912(%rbx)
	movq	%r12, 920(%rbx)
	movq	$1, 512(%rbx)
	movq	$1, 520(%rbx)
	movq	$0, 640(%rbx)
	movq	%rax, 648(%rbx)
	movq	$0, 768(%rbx)
	movq	%rax, 776(%rbx)
	movw	$0, 896(%rbx)
	movq	120(%rbx), %rsi
	movups	24(%rsi), %xmm0
	movq	$0, 24(%rsi)
	movaps	%xmm0, 928(%rbx)
	movups	56(%rsi), %xmm0
	movq	$0, 56(%rsi)
	movaps	%xmm0, 944(%rbx)
	movups	72(%rsi), %xmm0
	movq	$0, 72(%rsi)
	movaps	%xmm0, 960(%rbx)
	movq	$1, 976(%rbx)
	movq	%r15, 984(%rbx)
	movq	128(%rbx), %rax
	movq	%rax, 992(%rbx)
	movq	%r15, 1000(%rbx)
	movq	$0, 1008(%rbx)
	movl	$640, %ecx
	movl	$128, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB2_173
	leaq	512(%rbx), %rdx
	movl	$640, %r8d
	movq	%rax, %rdi
	movq	%rax, %rcx
	callq	memcpy
	movq	%rdi, 96(%rbx)
	movq	%rdi, 344(%rbx)
	shlq	$5, %r13
	movq	152(%rbx), %r9
	addq	%r9, %r13
	shlq	$4, %r14
	movq	136(%rbx), %r8
	addq	%r8, %r14
	xorps	%xmm0, %xmm0
	movups	%xmm0, 232(%rbx)
	movq	%r9, 168(%rbx)
	movq	%r9, 176(%rbx)
	movq	320(%rbx), %rax
	movq	%rax, 184(%rbx)
	movq	%r13, 192(%rbx)
	movq	%r8, 200(%rbx)
	movq	%r8, 208(%rbx)
	movq	312(%rbx), %rax
	movq	%rax, 216(%rbx)
	movq	%r14, 224(%rbx)
	movq	$0, 248(%rbx)
	movups	(%rsi), %xmm6
	movl	_tls_index(%rip), %eax
	movq	%gs:88, %rcx
	movq	(%rcx,%rax,8), %rax
	leaq	_RNvNCNKNvNtCs98fvGvYc57G_10rayon_core8registry19WORKER_THREAD_STATE0s_023___RUST_STD_INTERNAL_VAL@SECREL32(%rax), %rax
	movq	%rax, 328(%rbx)
	movq	40(%rsi), %rdx
	movq	48(%rsi), %rax
	movq	%rax, 368(%rbx)
	movzbl	88(%rsi), %eax
	movb	%al, 95(%rbx)
	xorl	%edi, %edi
	movq	%r8, %rcx
	movq	%r9, %rax
	movq	%rdx, 376(%rbx)
	jmp	.LBB2_124
	.p2align	4
.LBB2_123:
	movq	%rsi, %rdi
	movq	128(%rbx), %rcx
	movq	%r12, %rax
	movq	376(%rbx), %rdx
.LBB2_124:
	cmpq	%r13, %rax
	je	.LBB2_144
	leaq	32(%rax), %r12
	movq	%r12, 176(%rbx)
	movzbl	24(%rax), %r11d
	cmpb	$2, %r11b
	je	.LBB2_144
	movq	16(%rax), %r8
	movq	%r8, 528(%rbx)
	movups	(%rax), %xmm0
	movaps	%xmm0, 512(%rbx)
	movl	25(%rax), %r8d
	movl	28(%rax), %r9d
	leaq	512(%rbx), %r10
	movl	%r9d, 28(%r10)
	movl	%r8d, 25(%r10)
	movb	%r11b, 536(%rbx)
	cmpq	%r14, %rcx
	je	.LBB2_142
	leaq	25(%rax), %r8
	leaq	16(%rcx), %r9
	leaq	1(%rdi), %rsi
	movq	%r9, 128(%rbx)
	movq	%r9, 208(%rbx)
	movq	(%rcx), %r9
	movzbl	8(%rcx), %r15d
	movq	16(%rax), %rcx
	movq	%rcx, 288(%rbx)
	movups	(%rax), %xmm0
	movaps	%xmm0, 272(%rbx)
	movl	(%r8), %eax
	movl	3(%r8), %ecx
	leaq	297(%rbx), %r8
	movl	%ecx, 3(%r8)
	movl	%eax, (%r8)
	movq	%rsi, 248(%rbx)
	movb	%r11b, 296(%rbx)
	movq	%r9, 104(%rbx)
	movq	%r9, 384(%rbx)
	movb	%r15b, 392(%rbx)
	testq	%rdx, %rdx
	je	.LBB2_130
	movq	368(%rbx), %rax
	movq	32(%rax), %rax
	movb	$1, 90(%rbx)
.Ltmp32:
	leaq	512(%rbx), %rcx
	movq	%rdi, %r8
	callq	*%rax
	nop
.Ltmp33:
	movq	96(%rbx), %rcx
	lock		incq	(%rcx)
	jg	.LBB2_131
	jmp	.LBB2_179
	.p2align	4
.LBB2_130:
	movq	$-1, 512(%rbx)
	movq	96(%rbx), %rcx
	lock		incq	(%rcx)
	jle	.LBB2_179
.LBB2_131:
	movaps	272(%rbx), %xmm0
	movaps	288(%rbx), %xmm1
	leaq	456(%rbx), %rax
	movups	%xmm1, 16(%rax)
	movups	%xmm0, (%rax)
	movq	528(%rbx), %rax
	leaq	416(%rbx), %rdx
	movq	%rax, 16(%rdx)
	movups	512(%rbx), %xmm0
	movups	%xmm0, (%rdx)
	movaps	%xmm6, 400(%rbx)
	movq	104(%rbx), %rax
	movq	%rax, 440(%rbx)
	movb	%r15b, 448(%rbx)
	movq	%rcx, 488(%rbx)
	movq	%rdi, 496(%rbx)
	testq	%rdi, %rdi
	jne	.LBB2_139
	cmpb	$0, 95(%rbx)
	je	.LBB2_139
	movq	328(%rbx), %rax
	cmpq	$0, (%rax)
	jne	.LBB2_146
	movb	$0, 90(%rbx)
.Ltmp42:
	leaq	512(%rbx), %rcx
	leaq	400(%rbx), %rdx
	callq	_RNvXs6_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThreadINtNtCs8xEFJqa6dYS_4core7convert4FromNtB5_13ThreadBuilderE4from
	nop
.Ltmp43:
	movl	$384, %ecx
	movl	$128, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB2_166
	movq	%rax, %rsi
	movl	$384, %r8d
	movq	%rax, %rcx
	leaq	512(%rbx), %rdx
	callq	memcpy
	movq	328(%rbx), %rax
	cmpq	$0, (%rax)
	jne	.LBB2_167
	movq	%rsi, (%rax)
	movq	96(%rbx), %rax
	cmpq	$0, 520(%rax)
	je	.LBB2_177
	movq	512(%rax), %rcx
	movb	$0, 90(%rbx)
	movl	$1, %esi
.Ltmp46:
	callq	_RNvXs4_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatchNtB5_5Latch3set
	nop
.Ltmp47:
	jmp	.LBB2_123
	.p2align	4
.LBB2_139:
	movb	$0, 90(%rbx)
.Ltmp34:
	leaq	400(%rbx), %rdx
	callq	_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn
	nop
.Ltmp35:
	testq	%rax, %rax
	je	.LBB2_123
	movq	256(%rbx), %rcx
	movq	$2, (%rcx)
	movq	%rax, 8(%rcx)
	jmp	.LBB2_154
.LBB2_142:
	movq	512(%rbx), %rax
	lock		decq	(%rax)
	jne	.LBB2_144
	#MEMBARRIER
	leaq	512(%rbx), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
.LBB2_144:
	leaq	168(%rbx), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtNtB4_4iter8adapters9enumerate9EnumerateINtNtBG_3zip3ZipINtNtNtCsfQUUnEvlYZE_5alloc3vec9into_iter8IntoIterINtNtCslOUiAINmber_15crossbeam_deque5deque6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEIB1C_INtB2s_7StealerB3c_EEEEEB3g_
	movq	256(%rbx), %rax
	movq	96(%rbx), %rcx
	movq	%rcx, 8(%rax)
	movq	$-1, (%rax)
.LBB2_145:
	movq	120(%rbx), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_
	movaps	1056(%rbp), %xmm6
	.seh_startepilogue
	leaq	1080(%rbp), %rsp
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
.LBB2_146:
	movq	256(%rbx), %rax
	movq	$1, (%rax)
	cmpq	$0, 416(%rbx)
	jle	.LBB2_148
	movq	424(%rbx), %rcx
	callq	mi_free
	movq	96(%rbx), %rcx
.LBB2_148:
	movq	456(%rbx), %rax
	lock		decq	(%rax)
	jne	.LBB2_149
	#MEMBARRIER
	leaq	456(%rbx), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
	movq	96(%rbx), %rcx
	movq	104(%rbx), %rax
	lock		decq	(%rax)
	je	.LBB2_152
.LBB2_150:
	lock		decq	(%rcx)
	je	.LBB2_153
	jmp	.LBB2_154
.LBB2_149:
	movq	104(%rbx), %rax
	lock		decq	(%rax)
	jne	.LBB2_150
.LBB2_152:
	#MEMBARRIER
	leaq	440(%rbx), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
	movq	96(%rbx), %rcx
	lock		decq	(%rcx)
	jne	.LBB2_154
.LBB2_153:
	#MEMBARRIER
	movb	$0, 90(%rbx)
.Ltmp36:
	leaq	488(%rbx), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_
	nop
.Ltmp37:
.LBB2_154:
	leaq	168(%rbx), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtNtB4_4iter8adapters9enumerate9EnumerateINtNtBG_3zip3ZipINtNtNtCsfQUUnEvlYZE_5alloc3vec9into_iter8IntoIterINtNtCslOUiAINmber_15crossbeam_deque5deque6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEIB1C_INtB2s_7StealerB3c_EEEEEB3g_
	movq	96(%rbx), %rax
	lock		decq	464(%rax)
	jne	.LBB2_160
	movq	96(%rbx), %rax
	movq	520(%rax), %rax
	testq	%rax, %rax
	je	.LBB2_160
	movq	96(%rbx), %rsi
	movq	512(%rsi), %r14
	leaq	(%rax,%rax,4), %rax
	leaq	(%r14,%rax,8), %r15
	addq	$472, %rsi
	xorl	%edi, %edi
	jmp	.LBB2_158
	.p2align	4
.LBB2_157:
	addq	$40, %r14
	incq	%rdi
	cmpq	%r15, %r14
	je	.LBB2_160
.LBB2_158:
	movl	$3, %eax
	xchgq	%rax, 16(%r14)
	cmpq	$2, %rax
	jne	.LBB2_157
.Ltmp38:
	movq	%rsi, %rcx
	movq	%rdi, %rdx
	callq	_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep20wake_specific_thread.llvm.17002324475202138184
	nop
.Ltmp39:
	jmp	.LBB2_157
.LBB2_160:
	movq	96(%rbx), %rax
	lock		decq	(%rax)
	jne	.LBB2_145
	#MEMBARRIER
	movb	$0, 91(%rbx)
	movb	$0, 92(%rbx)
.Ltmp40:
	leaq	344(%rbx), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_
	nop
.Ltmp41:
	jmp	.LBB2_145
.LBB2_162:
.Ltmp20:
	movl	$8, %ecx
	movl	$16, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp21:
	jmp	.LBB2_179
.LBB2_163:
.Ltmp18:
	movl	$128, %ecx
	movl	$384, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp19:
	jmp	.LBB2_179
.LBB2_164:
	testq	%r8, %r8
	jle	.LBB2_83
	callq	mi_free
	jmp	.LBB2_83
.LBB2_166:
.Ltmp50:
	movl	$128, %ecx
	movl	$384, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp51:
	jmp	.LBB2_179
.LBB2_167:
	movb	$0, 90(%rbx)
.Ltmp44:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.20(%rip), %rcx
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.21(%rip), %r8
	movl	$35, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking5panic
	nop
.Ltmp45:
	jmp	.LBB2_179
.LBB2_168:
.Ltmp16:
	leaq	192(%rbx), %rcx
	movl	$16, %r9d
	movq	%r15, %rdx
	movq	104(%rbx), %r8
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECs98fvGvYc57G_10rayon_core
	nop
.Ltmp17:
	movq	208(%rbx), %r15
	jmp	.LBB2_86
.LBB2_170:
.Ltmp28:
	leaq	536(%rbx), %rcx
	movl	$16, %r9d
	movq	%r14, %rdx
	movq	104(%rbx), %r8
	callq	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECs98fvGvYc57G_10rayon_core
	nop
.Ltmp29:
	movq	552(%rbx), %r14
	jmp	.LBB2_98
.LBB2_172:
.Ltmp54:
	movl	$8, %ecx
	movl	$1520, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp55:
	jmp	.LBB2_179
.LBB2_173:
.Ltmp52:
	movl	$128, %ecx
	movl	$640, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp53:
	jmp	.LBB2_179
.LBB2_176:
.Ltmp22:
	movl	$8, %ecx
	movl	$1024, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp23:
	jmp	.LBB2_179
.LBB2_177:
	movb	$0, 90(%rbx)
.Ltmp48:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.10(%rip), %r8
	xorl	%ecx, %ecx
	xorl	%edx, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	nop
.Ltmp49:
	jmp	.LBB2_179
.LBB2_178:
.Ltmp56:
	movl	$128, %ecx
	movq	%rsi, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp57:
.LBB2_179:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@IMGREL
	.section	.text,"xr",one_only,_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_,unique,2
	.seh_endproc
	.def	"?dtor$180@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$180@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA":
.seh_proc "?dtor$180@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"
.LBB2_180:
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
	subq	$56, %rsp
	.seh_stackalloc 56
	leaq	128(%rdx), %rbp
	movaps	%xmm6, 32(%rsp)
	.seh_savexmm %xmm6, 32
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	leaq	512(%rbx), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueTINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtCslOUiAINmber_15crossbeam_deque5deque6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEIBD_INtB1c_7StealerB1W_EEEEB20_
	movb	$1, 93(%rbx)
	movb	$1, 94(%rbx)
	movaps	32(%rsp), %xmm6
	.seh_startepilogue
	addq	$56, %rsp
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
	.section	.text,"xr",one_only,_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_,unique,2
	.seh_endproc
	.def	"?dtor$181@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$181@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA":
.seh_proc "?dtor$181@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"
.LBB2_181:
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
	subq	$56, %rsp
	.seh_stackalloc 56
	leaq	128(%rdx), %rbp
	movaps	%xmm6, 32(%rsp)
	.seh_savexmm %xmm6, 32
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	movb	$0, 91(%rbx)
	movb	$1, 92(%rbx)
	leaq	640(%rbx), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_
	movb	$0, 91(%rbx)
	movb	$1, 92(%rbx)
	movaps	32(%rsp), %xmm6
	.seh_startepilogue
	addq	$56, %rsp
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
	.section	.text,"xr",one_only,_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_,unique,2
	.seh_endproc
	.def	"?dtor$182@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$182@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA":
.seh_proc "?dtor$182@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"
.LBB2_182:
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
	subq	$56, %rsp
	.seh_stackalloc 56
	leaq	128(%rdx), %rbp
	movaps	%xmm6, 32(%rsp)
	.seh_savexmm %xmm6, 32
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	movq	128(%rbx), %rcx
	callq	mi_free
	movaps	32(%rsp), %xmm6
	.seh_startepilogue
	addq	$56, %rsp
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
	.section	.text,"xr",one_only,_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_,unique,2
	.seh_endproc
	.def	"?dtor$183@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$183@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA":
.seh_proc "?dtor$183@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"
.LBB2_183:
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
	subq	$56, %rsp
	.seh_stackalloc 56
	leaq	128(%rdx), %rbp
	movaps	%xmm6, 32(%rsp)
	.seh_savexmm %xmm6, 32
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	leaq	168(%rbx), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecNtNtCs98fvGvYc57G_10rayon_core8registry10ThreadInfoEEB1c_
	movb	$1, 91(%rbx)
	movb	$1, 92(%rbx)
	movaps	32(%rsp), %xmm6
	.seh_startepilogue
	addq	$56, %rsp
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
	.section	.text,"xr",one_only,_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_,unique,2
	.seh_endproc
	.def	"?dtor$184@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$184@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA":
.seh_proc "?dtor$184@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"
.LBB2_184:
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
	subq	$56, %rsp
	.seh_stackalloc 56
	leaq	128(%rdx), %rbp
	movaps	%xmm6, 32(%rsp)
	.seh_savexmm %xmm6, 32
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	movb	$0, 90(%rbx)
	leaq	512(%rbx), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry12WorkerThreadEBF_
	movb	$0, 90(%rbx)
	movaps	32(%rsp), %xmm6
	.seh_startepilogue
	addq	$56, %rsp
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
	.section	.text,"xr",one_only,_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_,unique,2
	.seh_endproc
	.def	"?dtor$185@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$185@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA":
.seh_proc "?dtor$185@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"
.LBB2_185:
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
	subq	$56, %rsp
	.seh_stackalloc 56
	leaq	128(%rdx), %rbp
	movaps	%xmm6, 32(%rsp)
	.seh_savexmm %xmm6, 32
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	cmpb	$0, 90(%rbx)
	je	.LBB2_191
	movq	104(%rbx), %rax
	lock		decq	(%rax)
	jne	.LBB2_188
	#MEMBARRIER
	leaq	384(%rbx), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
.LBB2_188:
	movq	272(%rbx), %rax
	lock		decq	(%rax)
	jne	.LBB2_190
	#MEMBARRIER
	leaq	272(%rbx), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
.LBB2_190:
	movaps	32(%rsp), %xmm6
	.seh_startepilogue
	addq	$56, %rsp
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
.LBB2_191:
	movaps	32(%rsp), %xmm6
	.seh_startepilogue
	addq	$56, %rsp
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
	.section	.text,"xr",one_only,_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_,unique,2
	.seh_endproc
	.def	"?dtor$192@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$192@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA":
.seh_proc "?dtor$192@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"
.LBB2_192:
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
	subq	$56, %rsp
	.seh_stackalloc 56
	leaq	128(%rdx), %rbp
	movaps	%xmm6, 32(%rsp)
	.seh_savexmm %xmm6, 32
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	leaq	168(%rbx), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtNtB4_4iter8adapters9enumerate9EnumerateINtNtBG_3zip3ZipINtNtNtCsfQUUnEvlYZE_5alloc3vec9into_iter8IntoIterINtNtCslOUiAINmber_15crossbeam_deque5deque6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEIB1C_INtB2s_7StealerB3c_EEEEEB3g_
	movq	96(%rbx), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry10TerminatorEBF_
	movaps	32(%rsp), %xmm6
	.seh_startepilogue
	addq	$56, %rsp
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
	.section	.text,"xr",one_only,_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_,unique,2
	.seh_endproc
	.def	"?dtor$193@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$193@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA":
.seh_proc "?dtor$193@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"
.LBB2_193:
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
	subq	$56, %rsp
	.seh_stackalloc 56
	leaq	128(%rdx), %rbp
	movaps	%xmm6, 32(%rsp)
	.seh_savexmm %xmm6, 32
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	movq	96(%rbx), %rax
	lock		decq	(%rax)
	jne	.LBB2_195
	#MEMBARRIER
	leaq	344(%rbx), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_
.LBB2_195:
	movb	$0, 91(%rbx)
	movb	$0, 92(%rbx)
	movaps	32(%rsp), %xmm6
	.seh_startepilogue
	addq	$56, %rsp
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
	.section	.text,"xr",one_only,_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_,unique,2
	.seh_endproc
	.def	"?dtor$196@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$196@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA":
.seh_proc "?dtor$196@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"
.LBB2_196:
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
	subq	$56, %rsp
	.seh_stackalloc 56
	leaq	128(%rdx), %rbp
	movaps	%xmm6, 32(%rsp)
	.seh_savexmm %xmm6, 32
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	leaq	512(%rbx), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEEEB35_
	movaps	32(%rsp), %xmm6
	.seh_startepilogue
	addq	$56, %rsp
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
	.section	.text,"xr",one_only,_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_,unique,2
	.seh_endproc
	.def	"?dtor$197@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$197@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA":
.seh_proc "?dtor$197@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"
.LBB2_197:
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
	subq	$56, %rsp
	.seh_stackalloc 56
	leaq	128(%rdx), %rbp
	movaps	%xmm6, 32(%rsp)
	.seh_savexmm %xmm6, 32
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	leaq	168(%rbx), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueTINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtCslOUiAINmber_15crossbeam_deque5deque6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEIBD_INtB1c_7StealerB1W_EEEEB20_
	movaps	32(%rsp), %xmm6
	.seh_startepilogue
	addq	$56, %rsp
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
	.section	.text,"xr",one_only,_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_,unique,2
	.seh_endproc
	.def	"?dtor$198@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$198@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA":
.seh_proc "?dtor$198@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"
.LBB2_198:
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
	subq	$56, %rsp
	.seh_stackalloc 56
	leaq	128(%rdx), %rbp
	movaps	%xmm6, 32(%rsp)
	.seh_savexmm %xmm6, 32
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	movq	$-1, %rdi
	movq	112(%rbx), %rsi
	movq	160(%rbx), %r14
	jmp	.LBB2_200
	.p2align	4
.LBB2_199:
	incq	%rdi
	addq	$16, %rsi
	cmpq	%rdi, %r14
	je	.LBB2_202
.LBB2_200:
	movq	(%rsi), %rax
	lock		decq	(%rax)
	jne	.LBB2_199
	#MEMBARRIER
	movq	%rsi, %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
	jmp	.LBB2_199
.LBB2_202:
	cmpq	$0, 264(%rbx)
	je	.LBB2_204
	movq	112(%rbx), %rcx
	callq	mi_free
.LBB2_204:
	movb	$1, 91(%rbx)
	movb	$1, 92(%rbx)
	movaps	32(%rsp), %xmm6
	.seh_startepilogue
	addq	$56, %rsp
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
	.section	.text,"xr",one_only,_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_,unique,2
	.seh_endproc
	.def	"?dtor$205@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$205@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA":
.seh_proc "?dtor$205@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"
.LBB2_205:
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
	subq	$56, %rsp
	.seh_stackalloc 56
	leaq	128(%rdx), %rbp
	movaps	%xmm6, 32(%rsp)
	.seh_savexmm %xmm6, 32
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	movzbl	92(%rbx), %edi
	movzbl	91(%rbx), %r14d
	testb	$1, %dil
	movq	352(%rbx), %r12
	je	.LBB2_212
	movq	$-1, %r15
	movq	136(%rbx), %rsi
	movq	336(%rbx), %r13
	jmp	.LBB2_208
	.p2align	4
.LBB2_207:
	incq	%r15
	addq	$16, %rsi
	cmpq	%r15, %r13
	je	.LBB2_210
.LBB2_208:
	movq	(%rsi), %rax
	lock		decq	(%rax)
	jne	.LBB2_207
	#MEMBARRIER
	movq	%rsi, %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
	jmp	.LBB2_207
.LBB2_210:
	cmpq	$0, 312(%rbx)
	je	.LBB2_212
	movq	136(%rbx), %rcx
	callq	mi_free
.LBB2_212:
	testb	$1, %r14b
	je	.LBB2_217
	movq	$-1, %r14
	movq	144(%rbx), %rsi
	jmp	.LBB2_215
	.p2align	4
.LBB2_214:
	incq	%r14
	addq	$32, %rsi
	cmpq	%r14, %r12
	je	.LBB2_218
.LBB2_215:
	movq	(%rsi), %rax
	lock		decq	(%rax)
	jne	.LBB2_214
	#MEMBARRIER
	movq	%rsi, %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
	jmp	.LBB2_214
.LBB2_217:
	movb	$0, 93(%rbx)
	movb	%dil, 94(%rbx)
	movaps	32(%rsp), %xmm6
	.seh_startepilogue
	addq	$56, %rsp
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
.LBB2_218:
	cmpq	$0, 304(%rbx)
	je	.LBB2_220
	movq	144(%rbx), %rcx
	callq	mi_free
.LBB2_220:
	movb	$0, 93(%rbx)
	movb	%dil, 94(%rbx)
	movaps	32(%rsp), %xmm6
	.seh_startepilogue
	addq	$56, %rsp
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
	.section	.text,"xr",one_only,_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_,unique,2
	.seh_endproc
	.def	"?dtor$221@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$221@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA":
.seh_proc "?dtor$221@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"
.LBB2_221:
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
	subq	$56, %rsp
	.seh_stackalloc 56
	leaq	128(%rdx), %rbp
	movaps	%xmm6, 32(%rsp)
	.seh_savexmm %xmm6, 32
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	movzbl	94(%rbx), %edi
	cmpb	$0, 93(%rbx)
	movq	360(%rbx), %r15
	je	.LBB2_228
	movq	$-1, %r14
	movq	112(%rbx), %rsi
	movq	160(%rbx), %r12
	jmp	.LBB2_224
	.p2align	4
.LBB2_223:
	incq	%r14
	addq	$16, %rsi
	cmpq	%r14, %r12
	je	.LBB2_226
.LBB2_224:
	movq	(%rsi), %rax
	lock		decq	(%rax)
	jne	.LBB2_223
	#MEMBARRIER
	movq	%rsi, %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
	jmp	.LBB2_223
.LBB2_226:
	cmpq	$0, 264(%rbx)
	je	.LBB2_228
	movq	112(%rbx), %rcx
	callq	mi_free
.LBB2_228:
	testb	$1, %dil
	je	.LBB2_233
	movq	$-1, %rdi
	movq	152(%rbx), %rsi
	jmp	.LBB2_231
	.p2align	4
.LBB2_230:
	incq	%rdi
	addq	$32, %rsi
	cmpq	%rdi, %r15
	je	.LBB2_234
.LBB2_231:
	movq	(%rsi), %rax
	lock		decq	(%rax)
	jne	.LBB2_230
	#MEMBARRIER
	movq	%rsi, %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
	jmp	.LBB2_230
.LBB2_233:
	movaps	32(%rsp), %xmm6
	.seh_startepilogue
	addq	$56, %rsp
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
.LBB2_234:
	cmpq	$0, 320(%rbx)
	je	.LBB2_236
	movq	152(%rbx), %rcx
	callq	mi_free
.LBB2_236:
	movaps	32(%rsp), %xmm6
	.seh_startepilogue
	addq	$56, %rsp
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
	.section	.text,"xr",one_only,_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_,unique,2
	.seh_endproc
	.def	"?dtor$237@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$237@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA":
.seh_proc "?dtor$237@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"
.LBB2_237:
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
	subq	$56, %rsp
	.seh_stackalloc 56
	leaq	128(%rdx), %rbp
	movaps	%xmm6, 32(%rsp)
	.seh_savexmm %xmm6, 32
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	movq	120(%rbx), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_
	movaps	32(%rsp), %xmm6
	.seh_startepilogue
	addq	$56, %rsp
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
.Lfunc_end2:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_,unique,2
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_,unique,2
	.p2align	2, 0x0
$cppxdata$_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_:
	.long	429065506
	.long	14
	.long	$stateUnwindMap$_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@IMGREL
	.long	0
	.long	0
	.long	26
	.long	$ip2state$_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@IMGREL
	.long	1176
	.long	0
	.long	1
$stateUnwindMap$_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_:
	.long	-1
	.long	"?dtor$237@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"@IMGREL
	.long	0
	.long	"?dtor$221@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"@IMGREL
	.long	1
	.long	"?dtor$205@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"@IMGREL
	.long	2
	.long	"?dtor$193@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"@IMGREL
	.long	3
	.long	"?dtor$192@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"@IMGREL
	.long	4
	.long	"?dtor$185@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"@IMGREL
	.long	5
	.long	"?dtor$184@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"@IMGREL
	.long	2
	.long	"?dtor$181@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"@IMGREL
	.long	2
	.long	"?dtor$183@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"@IMGREL
	.long	8
	.long	"?dtor$182@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"@IMGREL
	.long	2
	.long	"?dtor$198@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"@IMGREL
	.long	1
	.long	"?dtor$180@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"@IMGREL
	.long	0
	.long	"?dtor$197@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"@IMGREL
	.long	12
	.long	"?dtor$196@?0?_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_@4HA"@IMGREL
$ip2state$_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_:
	.long	.Lfunc_begin2@IMGREL
	.long	-1
	.long	.Ltmp10@IMGREL
	.long	0
	.long	.Ltmp14@IMGREL
	.long	12
	.long	.Ltmp25@IMGREL
	.long	-1
	.long	.Ltmp26@IMGREL
	.long	11
	.long	.Ltmp58@IMGREL
	.long	10
	.long	.Ltmp59@IMGREL
	.long	-1
	.long	.Ltmp32@IMGREL
	.long	5
	.long	.Ltmp43@IMGREL
	.long	-1
	.long	.Ltmp46@IMGREL
	.long	5
	.long	.Ltmp35@IMGREL
	.long	-1
	.long	.Ltmp36@IMGREL
	.long	5
	.long	.Ltmp38@IMGREL
	.long	3
	.long	.Ltmp40@IMGREL
	.long	2
	.long	.Ltmp20@IMGREL
	.long	12
	.long	.Ltmp18@IMGREL
	.long	13
	.long	.Ltmp50@IMGREL
	.long	6
	.long	.Ltmp44@IMGREL
	.long	5
	.long	.Ltmp16@IMGREL
	.long	12
	.long	.Ltmp28@IMGREL
	.long	11
	.long	.Ltmp54@IMGREL
	.long	9
	.long	.Ltmp52@IMGREL
	.long	7
	.long	.Ltmp22@IMGREL
	.long	12
	.long	.Ltmp48@IMGREL
	.long	5
	.long	.Ltmp56@IMGREL
	.long	8
	.long	.Ltmp57@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_,unique,2

	.def	_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core,unique,3
	.p2align	4
_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core:
.Lfunc_begin3:
.seh_proc _RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core
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
	movl	_tls_index(%rip), %eax
	movq	%gs:88, %rcx
	movq	(%rcx,%rax,8), %rcx
	leaq	_RNvNCNKNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default6HANDLE0023___RUST_STD_INTERNAL_VAL@SECREL32(%rcx), %rax
	cmpb	$1, _RNvNCNKNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default6HANDLE0023___RUST_STD_INTERNAL_VAL@SECREL32+8(%rcx)
	jne	.LBB3_6
.LBB3_1:
	movq	(%rax), %rdx
	movq	%rdx, -16(%rbp)
	movq	2072(%rdx), %rax
	cmpq	$-1, %rax
	movq	%rdx, -8(%rbp)
	je	.LBB3_13
	leaq	1(%rax), %rcx
	movq	%rcx, 2072(%rdx)
	testq	%rax, %rax
	jne	.LBB3_4
	movq	-8(%rbp), %rdx
	movq	8(%rdx), %rax
	movq	384(%rax), %rcx
	orq	$1, %rcx
	xorl	%eax, %eax
	lock		cmpxchgq	%rcx, 2176(%rdx)
	#MEMBARRIER
	movq	2088(%rdx), %rax
	leaq	1(%rax), %rcx
	movq	%rcx, 2088(%rdx)
	testb	$127, %al
	je	.LBB3_14
.LBB3_4:
	movq	-8(%rbp), %rax
.LBB3_5:
	.seh_startepilogue
	addq	$56, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB3_6:
	movq	%rax, %rcx
	callq	_RINvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazyINtB6_7StorageNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleuE16get_or_init_slowNvNvNtB1h_7default6HANDLE27___rust_std_internal_init_fnECs98fvGvYc57G_10rayon_core
	testq	%rax, %rax
	jne	.LBB3_1
	movl	_RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default9collector9COLLECTOR.llvm.14389155381977926352+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB3_15
.LBB3_8:
	leaq	_RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default9collector9COLLECTOR.llvm.14389155381977926352(%rip), %rcx
	callq	_RNvMs1_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9Collector8register
	movq	%rax, -16(%rbp)
	movq	2072(%rax), %rdx
	cmpq	$-1, %rdx
	movq	%rax, -8(%rbp)
	je	.LBB3_16
	leaq	1(%rdx), %rcx
	movq	%rcx, 2072(%rax)
	testq	%rdx, %rdx
	jne	.LBB3_11
	movq	-8(%rbp), %rdx
	movq	8(%rdx), %rax
	movq	384(%rax), %rcx
	orq	$1, %rcx
	xorl	%eax, %eax
	lock		cmpxchgq	%rcx, 2176(%rdx)
	#MEMBARRIER
	movq	2088(%rdx), %rax
	leaq	1(%rax), %rcx
	movq	%rcx, 2088(%rdx)
	testb	$127, %al
	je	.LBB3_18
.LBB3_11:
	movq	-8(%rbp), %rdx
	movq	2080(%rdx), %rax
	leaq	-1(%rax), %rcx
	movq	%rcx, 2080(%rdx)
	xorq	$1, %rax
	orq	2072(%rdx), %rax
	movq	%rdx, %rax
	jne	.LBB3_5
	movq	%rax, %rcx
	movq	%rax, %rsi
	callq	_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$56, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB3_13:
.Ltmp66:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.44(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	nop
.Ltmp67:
	jmp	.LBB3_17
.LBB3_14:
	movq	-8(%rbp), %rax
	movq	8(%rax), %rcx
	subq	$-128, %rcx
.Ltmp64:
	leaq	-16(%rbp), %rdx
	callq	_RNvMs5_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_6Global7collect
	nop
.Ltmp65:
	jmp	.LBB3_4
.LBB3_15:
	callq	_RINvMs0_NtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync9once_lockINtB6_8OnceLockNtNtBa_9collector9CollectorE10initializeNvMs1_B1b_B19_3newEBa_.llvm.14389155381977926352
	jmp	.LBB3_8
.LBB3_16:
.Ltmp62:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.44(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	nop
.Ltmp63:
.LBB3_17:
	ud2
.LBB3_18:
	movq	-8(%rbp), %rax
	movq	8(%rax), %rcx
	subq	$-128, %rcx
.Ltmp60:
	leaq	-16(%rbp), %rdx
	callq	_RNvMs5_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_6Global7collect
	nop
.Ltmp61:
	jmp	.LBB3_11
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core@IMGREL
	.section	.text,"xr",one_only,_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core,unique,3
	.seh_endproc
	.def	"?dtor$19@?0?_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$19@?0?_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core@4HA":
.seh_proc "?dtor$19@?0?_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core@4HA"
.LBB3_19:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	48(%rdx), %rbp
	.seh_endprologue
	movq	-8(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs3qjAvHHmxHz_15crossbeam_epoch5guard5GuardECs98fvGvYc57G_10rayon_core
	nop
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core,unique,3
	.seh_endproc
	.def	"?dtor$20@?0?_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$20@?0?_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core@4HA":
.seh_proc "?dtor$20@?0?_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core@4HA"
.LBB3_20:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	48(%rdx), %rbp
	.seh_endprologue
	movq	-8(%rbp), %rdx
	movq	2080(%rdx), %rax
	leaq	-1(%rax), %rcx
	movq	%rcx, 2080(%rdx)
	xorq	$1, %rax
	orq	2072(%rdx), %rax
	je	.LBB3_22
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB3_22:
	movq	-8(%rbp), %rcx
	callq	_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize
	nop
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core,unique,3
	.seh_endproc
	.def	"?dtor$23@?0?_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$23@?0?_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core@4HA":
.seh_proc "?dtor$23@?0?_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core@4HA"
.LBB3_23:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	48(%rdx), %rbp
	.seh_endprologue
	movq	-8(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs3qjAvHHmxHz_15crossbeam_epoch5guard5GuardECs98fvGvYc57G_10rayon_core
	nop
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end3:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core,unique,3
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core,unique,3
	.p2align	2, 0x0
$cppxdata$_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core:
	.long	429065506
	.long	3
	.long	$stateUnwindMap$_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core@IMGREL
	.long	0
	.long	0
	.long	5
	.long	$ip2state$_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core@IMGREL
	.long	48
	.long	0
	.long	1
$stateUnwindMap$_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core:
	.long	-1
	.long	"?dtor$23@?0?_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core@4HA"@IMGREL
	.long	-1
	.long	"?dtor$20@?0?_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core@4HA"@IMGREL
	.long	1
	.long	"?dtor$19@?0?_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core@4HA"@IMGREL
$ip2state$_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core:
	.long	.Lfunc_begin3@IMGREL
	.long	-1
	.long	.Ltmp66@IMGREL
	.long	0
	.long	.Ltmp65@IMGREL
	.long	-1
	.long	.Ltmp62@IMGREL
	.long	2
	.long	.Ltmp61@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core,unique,3

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_4cell10UnsafeCellINtNtB4_6option6OptionINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEEEECs98fvGvYc57G_10rayon_core;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_4cell10UnsafeCellINtNtB4_6option6OptionINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEEEECs98fvGvYc57G_10rayon_core,unique,4
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_4cell10UnsafeCellINtNtB4_6option6OptionINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEEEECs98fvGvYc57G_10rayon_core:
.Lfunc_begin4:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_4cell10UnsafeCellINtNtB4_6option6OptionINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEEEECs98fvGvYc57G_10rayon_core
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$64, %rsp
	.seh_stackalloc 64
	leaq	64(%rsp), %rbp
	.seh_setframe %rbp, 64
	.seh_endprologue
	movq	$-2, -8(%rbp)
	cmpq	$0, (%rcx)
	je	.LBB4_9
	movq	8(%rcx), %rax
	movq	%rax, -16(%rbp)
	testq	%rax, %rax
	je	.LBB4_9
	movq	16(%rcx), %rax
	movq	%rax, -24(%rbp)
	movq	(%rax), %rax
	testq	%rax, %rax
	je	.LBB4_4
.Ltmp68:
	movq	-16(%rbp), %rcx
	callq	*%rax
	nop
.Ltmp69:
.LBB4_4:
	movq	-24(%rbp), %rax
	cmpq	$0, 8(%rax)
	je	.LBB4_9
	movq	-16(%rbp), %rcx
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbp
	.seh_endepilogue
	jmp	mi_free
.LBB4_9:
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_4cell10UnsafeCellINtNtB4_6option6OptionINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEEEECs98fvGvYc57G_10rayon_core@IMGREL
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_4cell10UnsafeCellINtNtB4_6option6OptionINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEEEECs98fvGvYc57G_10rayon_core,unique,4
	.seh_endproc
	.def	"?dtor$6@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_4cell10UnsafeCellINtNtB4_6option6OptionINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEEEECs98fvGvYc57G_10rayon_core@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$6@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_4cell10UnsafeCellINtNtB4_6option6OptionINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEEEECs98fvGvYc57G_10rayon_core@4HA":
.seh_proc "?dtor$6@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_4cell10UnsafeCellINtNtB4_6option6OptionINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEEEECs98fvGvYc57G_10rayon_core@4HA"
.LBB4_6:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	64(%rdx), %rbp
	.seh_endprologue
	movq	-24(%rbp), %rax
	cmpq	$0, 8(%rax)
	je	.LBB4_8
	movq	-16(%rbp), %rcx
	callq	mi_free
	nop
.LBB4_8:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end4:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_4cell10UnsafeCellINtNtB4_6option6OptionINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEEEECs98fvGvYc57G_10rayon_core,unique,4
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_4cell10UnsafeCellINtNtB4_6option6OptionINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEEEECs98fvGvYc57G_10rayon_core,unique,4
	.p2align	2, 0x0
$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_4cell10UnsafeCellINtNtB4_6option6OptionINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEEEECs98fvGvYc57G_10rayon_core:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_4cell10UnsafeCellINtNtB4_6option6OptionINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEEEECs98fvGvYc57G_10rayon_core@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_4cell10UnsafeCellINtNtB4_6option6OptionINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEEEECs98fvGvYc57G_10rayon_core@IMGREL
	.long	56
	.long	0
	.long	1
$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_4cell10UnsafeCellINtNtB4_6option6OptionINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEEEECs98fvGvYc57G_10rayon_core:
	.long	-1
	.long	"?dtor$6@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_4cell10UnsafeCellINtNtB4_6option6OptionINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEEEECs98fvGvYc57G_10rayon_core@4HA"@IMGREL
$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_4cell10UnsafeCellINtNtB4_6option6OptionINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEEEECs98fvGvYc57G_10rayon_core:
	.long	.Lfunc_begin4@IMGREL
	.long	-1
	.long	.Ltmp68@IMGREL
	.long	0
	.long	.Ltmp69@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_4cell10UnsafeCellINtNtB4_6option6OptionINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEEEECs98fvGvYc57G_10rayon_core,unique,4

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6option6OptionINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDINtNtNtB4_3ops8function2FnTjEEp6OutputuNtNtB4_6marker4SendNtB2c_4SyncEL_EEECs98fvGvYc57G_10rayon_core;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6option6OptionINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDINtNtNtB4_3ops8function2FnTjEEp6OutputuNtNtB4_6marker4SendNtB2c_4SyncEL_EEECs98fvGvYc57G_10rayon_core,unique,5
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6option6OptionINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDINtNtNtB4_3ops8function2FnTjEEp6OutputuNtNtB4_6marker4SendNtB2c_4SyncEL_EEECs98fvGvYc57G_10rayon_core:
.Lfunc_begin5:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6option6OptionINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDINtNtNtB4_3ops8function2FnTjEEp6OutputuNtNtB4_6marker4SendNtB2c_4SyncEL_EEECs98fvGvYc57G_10rayon_core
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
	testq	%rcx, %rcx
	je	.LBB5_8
	movq	%rdx, -24(%rbp)
	movq	(%rdx), %rax
	testq	%rax, %rax
	je	.LBB5_3
.Ltmp70:
	movq	-16(%rbp), %rcx
	callq	*%rax
	nop
.Ltmp71:
.LBB5_3:
	movq	-24(%rbp), %rax
	cmpq	$0, 8(%rax)
	je	.LBB5_8
	movq	-16(%rbp), %rcx
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbp
	.seh_endepilogue
	jmp	mi_free
.LBB5_8:
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6option6OptionINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDINtNtNtB4_3ops8function2FnTjEEp6OutputuNtNtB4_6marker4SendNtB2c_4SyncEL_EEECs98fvGvYc57G_10rayon_core@IMGREL
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6option6OptionINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDINtNtNtB4_3ops8function2FnTjEEp6OutputuNtNtB4_6marker4SendNtB2c_4SyncEL_EEECs98fvGvYc57G_10rayon_core,unique,5
	.seh_endproc
	.def	"?dtor$5@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6option6OptionINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDINtNtNtB4_3ops8function2FnTjEEp6OutputuNtNtB4_6marker4SendNtB2c_4SyncEL_EEECs98fvGvYc57G_10rayon_core@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$5@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6option6OptionINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDINtNtNtB4_3ops8function2FnTjEEp6OutputuNtNtB4_6marker4SendNtB2c_4SyncEL_EEECs98fvGvYc57G_10rayon_core@4HA":
.seh_proc "?dtor$5@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6option6OptionINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDINtNtNtB4_3ops8function2FnTjEEp6OutputuNtNtB4_6marker4SendNtB2c_4SyncEL_EEECs98fvGvYc57G_10rayon_core@4HA"
.LBB5_5:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	64(%rdx), %rbp
	.seh_endprologue
	movq	-24(%rbp), %rax
	cmpq	$0, 8(%rax)
	je	.LBB5_7
	movq	-16(%rbp), %rcx
	callq	mi_free
	nop
.LBB5_7:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end5:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6option6OptionINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDINtNtNtB4_3ops8function2FnTjEEp6OutputuNtNtB4_6marker4SendNtB2c_4SyncEL_EEECs98fvGvYc57G_10rayon_core,unique,5
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6option6OptionINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDINtNtNtB4_3ops8function2FnTjEEp6OutputuNtNtB4_6marker4SendNtB2c_4SyncEL_EEECs98fvGvYc57G_10rayon_core,unique,5
	.p2align	2, 0x0
$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6option6OptionINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDINtNtNtB4_3ops8function2FnTjEEp6OutputuNtNtB4_6marker4SendNtB2c_4SyncEL_EEECs98fvGvYc57G_10rayon_core:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6option6OptionINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDINtNtNtB4_3ops8function2FnTjEEp6OutputuNtNtB4_6marker4SendNtB2c_4SyncEL_EEECs98fvGvYc57G_10rayon_core@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6option6OptionINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDINtNtNtB4_3ops8function2FnTjEEp6OutputuNtNtB4_6marker4SendNtB2c_4SyncEL_EEECs98fvGvYc57G_10rayon_core@IMGREL
	.long	56
	.long	0
	.long	1
$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6option6OptionINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDINtNtNtB4_3ops8function2FnTjEEp6OutputuNtNtB4_6marker4SendNtB2c_4SyncEL_EEECs98fvGvYc57G_10rayon_core:
	.long	-1
	.long	"?dtor$5@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6option6OptionINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDINtNtNtB4_3ops8function2FnTjEEp6OutputuNtNtB4_6marker4SendNtB2c_4SyncEL_EEECs98fvGvYc57G_10rayon_core@4HA"@IMGREL
$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6option6OptionINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDINtNtNtB4_3ops8function2FnTjEEp6OutputuNtNtB4_6marker4SendNtB2c_4SyncEL_EEECs98fvGvYc57G_10rayon_core:
	.long	.Lfunc_begin5@IMGREL
	.long	-1
	.long	.Ltmp70@IMGREL
	.long	0
	.long	.Ltmp71@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6option6OptionINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDINtNtNtB4_3ops8function2FnTjEEp6OutputuNtNtB4_6marker4SendNtB2c_4SyncEL_EEECs98fvGvYc57G_10rayon_core,unique,5

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultINtNtCsfQUUnEvlYZE_5alloc4sync3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryENtB1z_20ThreadPoolBuildErrorEEB1z_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultINtNtCsfQUUnEvlYZE_5alloc4sync3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryENtB1z_20ThreadPoolBuildErrorEEB1z_,unique,6
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultINtNtCsfQUUnEvlYZE_5alloc4sync3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryENtB1z_20ThreadPoolBuildErrorEEB1z_:
.Lfunc_begin6:
	movq	(%rcx), %rax
	cmpq	$-1, %rax
	je	.LBB6_1
	cmpl	$2, %eax
	jb	.LBB6_6
	movq	8(%rcx), %rax
	movl	%eax, %ecx
	andl	$3, %ecx
	leal	-2(%rcx), %edx
	cmpl	$2, %edx
	jb	.LBB6_6
	testq	%rcx, %rcx
	je	.LBB6_6
	leaq	-1(%rax), %rcx
	rex64 jmpq	*23(%rax)
.LBB6_1:
	movq	8(%rcx), %rax
	lock		decq	(%rax)
	jne	.LBB6_6
	addq	$8, %rcx
	#MEMBARRIER
	jmp	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_
.LBB6_6:
	retq
.Lfunc_end6:

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultRINtNtCsfQUUnEvlYZE_5alloc4sync3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryENtB1A_20ThreadPoolBuildErrorEEB1A_.llvm.17002324475202138184;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultRINtNtCsfQUUnEvlYZE_5alloc4sync3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryENtB1A_20ThreadPoolBuildErrorEEB1A_.llvm.17002324475202138184,unique,7
	.globl	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultRINtNtCsfQUUnEvlYZE_5alloc4sync3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryENtB1A_20ThreadPoolBuildErrorEEB1A_.llvm.17002324475202138184
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultRINtNtCsfQUUnEvlYZE_5alloc4sync3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryENtB1A_20ThreadPoolBuildErrorEEB1A_.llvm.17002324475202138184:
.Lfunc_begin7:
	addq	$-2, %rcx
	cmpq	$-3, %rcx
	jae	.LBB7_3
	movl	%edx, %eax
	andl	$3, %eax
	leal	-2(%rax), %ecx
	cmpl	$2, %ecx
	jb	.LBB7_3
	testq	%rax, %rax
	jne	.LBB7_4
.LBB7_3:
	retq
.LBB7_4:
	leaq	-1(%rdx), %rcx
	rex64 jmpq	*23(%rdx)
.Lfunc_end7:

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core,unique,8
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core:
.Lfunc_begin8:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core
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
	movq	(%rdx), %rax
	testq	%rax, %rax
	je	.LBB8_2
.Ltmp72:
	movq	-16(%rbp), %rcx
	callq	*%rax
	nop
.Ltmp73:
.LBB8_2:
	movq	-16(%rbp), %rcx
	movq	-24(%rbp), %rax
	cmpq	$0, 8(%rax)
	je	.LBB8_7
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbp
	.seh_endepilogue
	jmp	mi_free
.LBB8_7:
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core@IMGREL
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core,unique,8
	.seh_endproc
	.def	"?dtor$4@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$4@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core@4HA":
.seh_proc "?dtor$4@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core@4HA"
.LBB8_4:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	64(%rdx), %rbp
	.seh_endprologue
	movq	-16(%rbp), %rcx
	movq	-24(%rbp), %rax
	cmpq	$0, 8(%rax)
	je	.LBB8_6
	callq	mi_free
	nop
.LBB8_6:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end8:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core,unique,8
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core,unique,6
	.p2align	2, 0x0
$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core@IMGREL
	.long	56
	.long	0
	.long	1
$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core:
	.long	-1
	.long	"?dtor$4@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core@4HA"@IMGREL
$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core:
	.long	.Lfunc_begin8@IMGREL
	.long	-1
	.long	.Ltmp72@IMGREL
	.long	0
	.long	.Ltmp73@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core,unique,8

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultuNtNtNtB4_2io5error5ErrorEECs98fvGvYc57G_10rayon_core;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultuNtNtNtB4_2io5error5ErrorEECs98fvGvYc57G_10rayon_core,unique,9
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultuNtNtNtB4_2io5error5ErrorEECs98fvGvYc57G_10rayon_core:
.Lfunc_begin9:
	testq	%rcx, %rcx
	je	.LBB9_3
	movl	%ecx, %eax
	andl	$3, %eax
	leal	-2(%rax), %edx
	cmpl	$2, %edx
	jb	.LBB9_3
	testq	%rax, %rax
	jne	.LBB9_4
.LBB9_3:
	retq
.LBB9_4:
	leaq	-1(%rcx), %rax
	movq	%rcx, %rdx
	movq	%rax, %rcx
	rex64 jmpq	*23(%rdx)
.Lfunc_end9:

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtBG_5boxed3BoxDINtNtNtB4_3ops8function6FnOnceuEp6OutputuNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtBG_5boxed3BoxDINtNtNtB4_3ops8function6FnOnceuEp6OutputuNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core,unique,10
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtBG_5boxed3BoxDINtNtNtB4_3ops8function6FnOnceuEp6OutputuNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core:
.Lfunc_begin10:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtBG_5boxed3BoxDINtNtNtB4_3ops8function6FnOnceuEp6OutputuNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core
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
	subq	$96, %rsp
	.seh_stackalloc 96
	leaq	96(%rsp), %rbp
	.seh_setframe %rbp, 96
	.seh_endprologue
	movq	$-2, -8(%rbp)
	movq	8(%rcx), %rax
	movq	%rax, -16(%rbp)
	movq	%rcx, -32(%rbp)
	movq	16(%rcx), %rax
	testq	%rax, %rax
	je	.LBB10_7
	movq	-16(%rbp), %rcx
	addq	$24, %rcx
	movl	$1, %edx
	subq	%rax, %rdx
	jmp	.LBB10_2
	.p2align	4
.LBB10_6:
	movq	-56(%rbp), %rcx
	addq	$16, %rcx
	movq	-48(%rbp), %rdx
	incq	%rdx
	cmpq	$1, %rdx
	je	.LBB10_7
.LBB10_2:
	movq	%rdx, -48(%rbp)
	movq	-24(%rcx), %rax
	movq	%rax, -24(%rbp)
	movq	%rcx, -56(%rbp)
	movq	-16(%rcx), %rax
	movq	%rax, -40(%rbp)
	movq	(%rax), %rax
	testq	%rax, %rax
	je	.LBB10_4
.Ltmp74:
	movq	-24(%rbp), %rcx
	callq	*%rax
	nop
.Ltmp75:
.LBB10_4:
	movq	-24(%rbp), %rcx
	movq	-40(%rbp), %rax
	cmpq	$0, 8(%rax)
	je	.LBB10_6
	callq	mi_free
	jmp	.LBB10_6
.LBB10_7:
	movq	-32(%rbp), %rax
	cmpq	$0, (%rax)
	je	.LBB10_22
	movq	-16(%rbp), %rcx
	.seh_startepilogue
	addq	$96, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	jmp	mi_free
.LBB10_22:
	.seh_startepilogue
	addq	$96, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtBG_5boxed3BoxDINtNtNtB4_3ops8function6FnOnceuEp6OutputuNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core@IMGREL
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtBG_5boxed3BoxDINtNtNtB4_3ops8function6FnOnceuEp6OutputuNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core,unique,10
	.seh_endproc
	.def	"?dtor$9@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtBG_5boxed3BoxDINtNtNtB4_3ops8function6FnOnceuEp6OutputuNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$9@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtBG_5boxed3BoxDINtNtNtB4_3ops8function6FnOnceuEp6OutputuNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core@4HA":
.seh_proc "?dtor$9@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtBG_5boxed3BoxDINtNtNtB4_3ops8function6FnOnceuEp6OutputuNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core@4HA"
.LBB10_9:
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
	leaq	96(%rdx), %rbp
	.seh_endprologue
	movq	-24(%rbp), %rcx
	movq	-40(%rbp), %rax
	cmpq	$0, 8(%rax)
	je	.LBB10_11
	callq	mi_free
.LBB10_11:
	movq	-48(%rbp), %r14
	testq	%r14, %r14
	movq	-56(%rbp), %rbx
	jne	.LBB10_12
.LBB10_18:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.LBB10_12:
	negq	%r14
	jmp	.LBB10_13
	.p2align	4
.LBB10_17:
	addq	$16, %rbx
	decq	%r14
	je	.LBB10_18
.LBB10_13:
	movq	-8(%rbx), %rsi
	movq	(%rbx), %rdi
	movq	(%rdi), %rax
	testq	%rax, %rax
	je	.LBB10_15
	movq	%rsi, %rcx
	callq	*%rax
.LBB10_15:
	cmpq	$0, 8(%rdi)
	je	.LBB10_17
	movq	%rsi, %rcx
	callq	mi_free
	jmp	.LBB10_17
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtBG_5boxed3BoxDINtNtNtB4_3ops8function6FnOnceuEp6OutputuNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core,unique,10
	.seh_endproc
	.def	"?dtor$19@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtBG_5boxed3BoxDINtNtNtB4_3ops8function6FnOnceuEp6OutputuNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$19@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtBG_5boxed3BoxDINtNtNtB4_3ops8function6FnOnceuEp6OutputuNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core@4HA":
.seh_proc "?dtor$19@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtBG_5boxed3BoxDINtNtNtB4_3ops8function6FnOnceuEp6OutputuNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core@4HA"
.LBB10_19:
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
	leaq	96(%rdx), %rbp
	.seh_endprologue
	movq	-32(%rbp), %rax
	cmpq	$0, (%rax)
	je	.LBB10_21
	movq	-16(%rbp), %rcx
	callq	mi_free
	nop
.LBB10_21:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end10:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtBG_5boxed3BoxDINtNtNtB4_3ops8function6FnOnceuEp6OutputuNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core,unique,10
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtBG_5boxed3BoxDINtNtNtB4_3ops8function6FnOnceuEp6OutputuNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core,unique,7
	.p2align	2, 0x0
$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtBG_5boxed3BoxDINtNtNtB4_3ops8function6FnOnceuEp6OutputuNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core:
	.long	429065506
	.long	2
	.long	$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtBG_5boxed3BoxDINtNtNtB4_3ops8function6FnOnceuEp6OutputuNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtBG_5boxed3BoxDINtNtNtB4_3ops8function6FnOnceuEp6OutputuNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core@IMGREL
	.long	88
	.long	0
	.long	1
$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtBG_5boxed3BoxDINtNtNtB4_3ops8function6FnOnceuEp6OutputuNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core:
	.long	-1
	.long	"?dtor$19@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtBG_5boxed3BoxDINtNtNtB4_3ops8function6FnOnceuEp6OutputuNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core@4HA"@IMGREL
	.long	0
	.long	"?dtor$9@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtBG_5boxed3BoxDINtNtNtB4_3ops8function6FnOnceuEp6OutputuNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core@4HA"@IMGREL
$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtBG_5boxed3BoxDINtNtNtB4_3ops8function6FnOnceuEp6OutputuNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core:
	.long	.Lfunc_begin10@IMGREL
	.long	-1
	.long	.Ltmp74@IMGREL
	.long	1
	.long	.Ltmp75@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtBG_5boxed3BoxDINtNtNtB4_3ops8function6FnOnceuEp6OutputuNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core,unique,10

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecNtNtCs98fvGvYc57G_10rayon_core8registry10ThreadInfoEEB1c_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecNtNtCs98fvGvYc57G_10rayon_core8registry10ThreadInfoEEB1c_,unique,11
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecNtNtCs98fvGvYc57G_10rayon_core8registry10ThreadInfoEEB1c_:
.Lfunc_begin11:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecNtNtCs98fvGvYc57G_10rayon_core8registry10ThreadInfoEEB1c_
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
	movq	16(%rcx), %r14
	testq	%r14, %r14
	je	.LBB11_5
	leaq	24(%rsi), %rbx
	jmp	.LBB11_2
	.p2align	4
.LBB11_4:
	addq	$40, %rbx
	decq	%r14
	je	.LBB11_5
.LBB11_2:
	movq	(%rbx), %rax
	lock		decq	(%rax)
	jne	.LBB11_4
	#MEMBARRIER
	movq	%rbx, %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
	jmp	.LBB11_4
.LBB11_5:
	cmpq	$0, (%rdi)
	je	.LBB11_6
	movq	%rsi, %rcx
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	jmp	mi_free
.LBB11_6:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.Lfunc_end11:
	.seh_endproc

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEEEB35_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEEEB35_,unique,12
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEEEB35_:
.Lfunc_begin12:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEEEB35_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	128(%rcx), %rsi
	andq	$-8, %rsi
	cmpq	$0, 8(%rsi)
	je	.LBB12_2
	movq	(%rsi), %rcx
	callq	mi_free
.LBB12_2:
	movq	%rsi, %rcx
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	jmp	mi_free
.Lfunc_end12:
	.seh_endproc

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core,unique,13
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core:
.Lfunc_begin13:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core
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
	movq	$-2, -16(%rbp)
	leaq	16(%rcx), %rdi
	movq	24(%rcx), %rbx
	movq	32(%rcx), %rax
	testq	%rax, %rax
	setne	%r14b
	testq	%rbx, %rbx
	movq	%rcx, -40(%rbp)
	je	.LBB13_6
	testq	%rax, %rax
	je	.LBB13_6
	movq	%rax, -32(%rbp)
	movb	%r14b, -17(%rbp)
	movq	%rbx, -72(%rbp)
	movq	%rdi, -56(%rbp)
	movq	40(%rcx), %rax
	movq	%rax, -48(%rbp)
	movq	(%rax), %rax
	testq	%rax, %rax
	je	.LBB13_4
.Ltmp76:
	movq	-32(%rbp), %rcx
	callq	*%rax
	nop
.Ltmp77:
.LBB13_4:
	movq	-48(%rbp), %rax
	cmpq	$0, 8(%rax)
	movq	-40(%rbp), %rcx
	movq	-56(%rbp), %rdi
	movq	-72(%rbp), %rbx
	movzbl	-17(%rbp), %r14d
	movq	-32(%rbp), %rax
	je	.LBB13_6
	movq	%rcx, %rsi
	movq	%rax, %rcx
	callq	mi_free
	movq	%rsi, %rcx
.LBB13_6:
	movq	$0, 24(%rcx)
.LBB13_7:
	movq	(%rdi), %rsi
	testq	%rsi, %rsi
	je	.LBB13_14
	andb	%r14b, %bl
	je	.LBB13_9
	movb	$1, 32(%rsi)
.LBB13_9:
	lock		decq	24(%rsi)
	jne	.LBB13_12
	movq	16(%rsi), %rcx
	movb	$1, %al
	xchgb	%al, 40(%rcx)
	cmpb	$-1, %al
	je	.LBB13_11
.LBB13_12:
	lock		decq	(%rsi)
	jne	.LBB13_14
.LBB13_13:
	#MEMBARRIER
.Ltmp82:
	movq	%rdi, %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtCse0R8cuyqEa_3std6thread6scoped9ScopeDataE9drop_slowBM_
	nop
.Ltmp83:
.LBB13_14:
	movq	-40(%rbp), %rax
	cmpq	$0, 24(%rax)
	je	.LBB13_20
	movq	32(%rax), %rcx
	movq	%rcx, -32(%rbp)
	testq	%rcx, %rcx
	je	.LBB13_20
	movq	40(%rax), %rax
	movq	%rax, -40(%rbp)
	movq	(%rax), %rax
	testq	%rax, %rax
	je	.LBB13_18
.Ltmp84:
	movq	-32(%rbp), %rcx
	callq	*%rax
	nop
.Ltmp85:
.LBB13_18:
	movq	-40(%rbp), %rax
	cmpq	$0, 8(%rax)
	je	.LBB13_20
	movq	-32(%rbp), %rcx
	callq	mi_free
	nop
.LBB13_20:
	.seh_startepilogue
	addq	$112, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.LBB13_11:
	addq	$40, %rcx
	callq	*__imp_WakeByAddressSingle(%rip)
	lock		decq	(%rsi)
	je	.LBB13_13
	jmp	.LBB13_14
.LBB13_26:
$ehgcr_13_26:
	cmpq	$0, -32(%rbp)
	movq	-56(%rbp), %rdi
	movq	-72(%rbp), %rbx
	movzbl	-17(%rbp), %r14d
	je	.LBB13_7
	movl	$0, -64(%rbp)
	movb	$0, -60(%rbp)
.Ltmp78:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.62(%rip), %rdx
	leaq	-64(%rbp), %rcx
	movl	$62, %r8d
	callq	_RNvYNtNtNtNtCse0R8cuyqEa_3std3sys5stdio7windows6StderrNtNtBa_2io5Write9write_allCs98fvGvYc57G_10rayon_core
	nop
.Ltmp79:
.Ltmp80:
	movq	%rax, %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultuNtNtNtB4_2io5error5ErrorEECs98fvGvYc57G_10rayon_core
	nop
.Ltmp81:
	movl	$7, %ecx
	#APP

	int	$41

	#NO_APP
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@IMGREL
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core,unique,13
	.seh_endproc
	.def	"?dtor$21@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$21@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA":
.seh_proc "?dtor$21@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA"
.LBB13_21:
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
	movq	-48(%rbp), %rax
	cmpq	$0, 8(%rax)
	je	.LBB13_23
	movq	-32(%rbp), %rcx
	callq	mi_free
.LBB13_23:
	movq	-40(%rbp), %rax
	movq	$0, 24(%rax)
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
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core,unique,13
	.seh_endproc
	.def	"?catch$24@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?catch$24@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA":
.seh_proc "?catch$24@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA"
	.seh_handler __CxxFrameHandler3, @unwind, @except
.LBB13_24:
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
	movq	-8(%rbp), %rcx
	callq	_RNvNvNtCse0R8cuyqEa_3std9panicking12catch_unwind7cleanup
	movq	%rax, -32(%rbp)
	movq	%rdx, -48(%rbp)
	leaq	.LBB13_26(%rip), %rax
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
	.long	$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@IMGREL
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core,unique,13
	.seh_endproc
	.def	"?catch$25@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?catch$25@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA":
.seh_proc "?catch$25@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA"
	.seh_handler __CxxFrameHandler3, @unwind, @except
.LBB13_25:
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
	xorl	%ecx, %ecx
	callq	_RNvNvNtCse0R8cuyqEa_3std9panicking12catch_unwind7cleanup
	movq	%rax, -32(%rbp)
	movq	%rdx, -48(%rbp)
	leaq	.LBB13_26(%rip), %rax
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
	.long	$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@IMGREL
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core,unique,13
	.seh_endproc
	.def	"?dtor$31@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$31@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA":
.seh_proc "?dtor$31@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA"
.LBB13_31:
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
	movq	-56(%rbp), %rax
	movq	(%rax), %rax
	testq	%rax, %rax
	je	.LBB13_34
	lock		decq	(%rax)
	jne	.LBB13_34
	#MEMBARRIER
	movq	-56(%rbp), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtCse0R8cuyqEa_3std6thread6scoped9ScopeDataE9drop_slowBM_
	nop
.LBB13_34:
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
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core,unique,13
	.seh_endproc
	.def	"?dtor$35@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$35@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA":
.seh_proc "?dtor$35@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA"
.LBB13_35:
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
	movq	-40(%rbp), %rcx
	addq	$24, %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_4cell10UnsafeCellINtNtB4_6option6OptionINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEEEECs98fvGvYc57G_10rayon_core
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
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core,unique,13
	.seh_endproc
	.def	"?dtor$36@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$36@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA":
.seh_proc "?dtor$36@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA"
.LBB13_36:
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
	movq	-40(%rbp), %rax
	cmpq	$0, 8(%rax)
	je	.LBB13_38
	movq	-32(%rbp), %rcx
	callq	mi_free
	nop
.LBB13_38:
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
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core,unique,13
	.seh_endproc
	.def	"?dtor$39@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$39@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA":
.seh_proc "?dtor$39@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA"
.LBB13_39:
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
	movq	-32(%rbp), %rcx
	movq	-48(%rbp), %rdx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultuINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core
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
.Lfunc_end13:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core,unique,13
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core,unique,8
	.p2align	2, 0x0
$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core:
	.long	429065506
	.long	7
	.long	$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@IMGREL
	.long	1
	.long	$tryMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@IMGREL
	.long	8
	.long	$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@IMGREL
	.long	96
	.long	0
	.long	1
$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core:
	.long	-1
	.long	"?dtor$35@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA"@IMGREL
	.long	0
	.long	"?dtor$31@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA"@IMGREL
	.long	1
	.long	"?dtor$39@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA"@IMGREL
	.long	1
	.long	0
	.long	3
	.long	"?dtor$21@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA"@IMGREL
	.long	1
	.long	0
	.long	-1
	.long	"?dtor$36@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA"@IMGREL
$tryMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core:
	.long	3
	.long	4
	.long	5
	.long	2
	.long	$handlerMap$0$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@IMGREL
$handlerMap$0$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core:
	.long	8
	.long	_RNvCs1njKG4L9aB3_7___rustc22___rust_panic_type_info@IMGREL
	.long	104
	.long	"?catch$24@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA"@IMGREL
	.long	88
	.long	64
	.long	0
	.long	0
	.long	"?catch$25@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA"@IMGREL
	.long	88
$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core:
	.long	.Lfunc_begin13@IMGREL
	.long	-1
	.long	.Ltmp76@IMGREL
	.long	4
	.long	.Ltmp82@IMGREL
	.long	0
	.long	.Ltmp84@IMGREL
	.long	6
	.long	.Ltmp78@IMGREL
	.long	2
	.long	.Ltmp81@IMGREL
	.long	-1
	.long	"?catch$24@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA"@IMGREL
	.long	5
	.long	"?catch$25@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core@4HA"@IMGREL
	.long	5
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core,unique,13

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECs98fvGvYc57G_10rayon_core;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECs98fvGvYc57G_10rayon_core,unique,14
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECs98fvGvYc57G_10rayon_core:
.Lfunc_begin14:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECs98fvGvYc57G_10rayon_core
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
	movq	(%rdx), %rax
	testq	%rax, %rax
	je	.LBB14_2
.Ltmp86:
	movq	-16(%rbp), %rcx
	callq	*%rax
	nop
.Ltmp87:
.LBB14_2:
	movq	-16(%rbp), %rcx
	movq	-24(%rbp), %rax
	cmpq	$0, 8(%rax)
	je	.LBB14_3
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbp
	.seh_endepilogue
	jmp	mi_free
.LBB14_3:
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECs98fvGvYc57G_10rayon_core@IMGREL
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECs98fvGvYc57G_10rayon_core,unique,14
	.seh_endproc
	.def	"?dtor$4@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECs98fvGvYc57G_10rayon_core@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$4@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECs98fvGvYc57G_10rayon_core@4HA":
.seh_proc "?dtor$4@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECs98fvGvYc57G_10rayon_core@4HA"
.LBB14_4:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	64(%rdx), %rbp
	.seh_endprologue
	movq	-16(%rbp), %rcx
	movq	-24(%rbp), %rax
	cmpq	$0, 8(%rax)
	je	.LBB14_6
	callq	mi_free
	nop
.LBB14_6:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end14:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECs98fvGvYc57G_10rayon_core,unique,14
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECs98fvGvYc57G_10rayon_core,unique,9
	.p2align	2, 0x0
$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECs98fvGvYc57G_10rayon_core:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECs98fvGvYc57G_10rayon_core@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECs98fvGvYc57G_10rayon_core@IMGREL
	.long	56
	.long	0
	.long	1
$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECs98fvGvYc57G_10rayon_core:
	.long	-1
	.long	"?dtor$4@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECs98fvGvYc57G_10rayon_core@4HA"@IMGREL
$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECs98fvGvYc57G_10rayon_core:
	.long	.Lfunc_begin14@IMGREL
	.long	-1
	.long	.Ltmp86@IMGREL
	.long	0
	.long	.Ltmp87@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECs98fvGvYc57G_10rayon_core,unique,14

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCse0R8cuyqEa_3std4sync6poison11PoisonErrorINtNtBE_5mutex10MutexGuardbEEECs98fvGvYc57G_10rayon_core.llvm.17002324475202138184;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCse0R8cuyqEa_3std4sync6poison11PoisonErrorINtNtBE_5mutex10MutexGuardbEEECs98fvGvYc57G_10rayon_core.llvm.17002324475202138184,unique,15
	.globl	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCse0R8cuyqEa_3std4sync6poison11PoisonErrorINtNtBE_5mutex10MutexGuardbEEECs98fvGvYc57G_10rayon_core.llvm.17002324475202138184
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCse0R8cuyqEa_3std4sync6poison11PoisonErrorINtNtBE_5mutex10MutexGuardbEEECs98fvGvYc57G_10rayon_core.llvm.17002324475202138184:
.Lfunc_begin15:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCse0R8cuyqEa_3std4sync6poison11PoisonErrorINtNtBE_5mutex10MutexGuardbEEECs98fvGvYc57G_10rayon_core.llvm.17002324475202138184
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rsi
	cmpb	$0, 8(%rcx)
	jne	.LBB15_4
	movq	_RNvNtNtCse0R8cuyqEa_3std9panicking11panic_count18GLOBAL_PANIC_COUNT(%rip), %rax
	shlq	%rax
	testq	%rax, %rax
	jne	.LBB15_2
.LBB15_4:
	xorl	%eax, %eax
	xchgb	%al, (%rsi)
	cmpb	$2, %al
	je	.LBB15_6
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB15_6:
	movq	%rsi, %rcx
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	rex64 jmpq	*__imp_WakeByAddressSingle(%rip)
.LBB15_2:
	callq	_RNvNtNtCse0R8cuyqEa_3std9panicking11panic_count17is_zero_slow_path
	testb	%al, %al
	jne	.LBB15_4
	movb	$1, 1(%rsi)
	jmp	.LBB15_4
.Lfunc_end15:
	.seh_endproc

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtNtB4_4iter8adapters9enumerate9EnumerateINtNtBG_3zip3ZipINtNtNtCsfQUUnEvlYZE_5alloc3vec9into_iter8IntoIterINtNtCslOUiAINmber_15crossbeam_deque5deque6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEIB1C_INtB2s_7StealerB3c_EEEEEB3g_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtNtB4_4iter8adapters9enumerate9EnumerateINtNtBG_3zip3ZipINtNtNtCsfQUUnEvlYZE_5alloc3vec9into_iter8IntoIterINtNtCslOUiAINmber_15crossbeam_deque5deque6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEIB1C_INtB2s_7StealerB3c_EEEEEB3g_,unique,16
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtNtB4_4iter8adapters9enumerate9EnumerateINtNtBG_3zip3ZipINtNtNtCsfQUUnEvlYZE_5alloc3vec9into_iter8IntoIterINtNtCslOUiAINmber_15crossbeam_deque5deque6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEIB1C_INtB2s_7StealerB3c_EEEEEB3g_:
.Lfunc_begin16:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtNtB4_4iter8adapters9enumerate9EnumerateINtNtBG_3zip3ZipINtNtNtCsfQUUnEvlYZE_5alloc3vec9into_iter8IntoIterINtNtCslOUiAINmber_15crossbeam_deque5deque6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEIB1C_INtB2s_7StealerB3c_EEEEEB3g_
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
	movq	8(%rcx), %rdi
	movq	24(%rcx), %rbx
	subq	%rdi, %rbx
	je	.LBB16_5
	shrq	$5, %rbx
	jmp	.LBB16_2
	.p2align	4
.LBB16_4:
	addq	$32, %rdi
	decq	%rbx
	je	.LBB16_5
.LBB16_2:
	movq	(%rdi), %rax
	lock		decq	(%rax)
	jne	.LBB16_4
	#MEMBARRIER
	movq	%rdi, %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
	jmp	.LBB16_4
.LBB16_5:
	cmpq	$0, 16(%rsi)
	je	.LBB16_7
	movq	(%rsi), %rcx
	callq	mi_free
.LBB16_7:
	movq	40(%rsi), %rdi
	movq	56(%rsi), %rbx
	subq	%rdi, %rbx
	je	.LBB16_12
	shrq	$4, %rbx
	jmp	.LBB16_9
	.p2align	4
.LBB16_11:
	addq	$16, %rdi
	decq	%rbx
	je	.LBB16_12
.LBB16_9:
	movq	(%rdi), %rax
	lock		decq	(%rax)
	jne	.LBB16_11
	#MEMBARRIER
	movq	%rdi, %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
	jmp	.LBB16_11
.LBB16_12:
	cmpq	$0, 48(%rsi)
	je	.LBB16_13
	movq	32(%rsi), %rcx
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	jmp	mi_free
.LBB16_13:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end16:
	.seh_endproc

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtNtCse0R8cuyqEa_3std4sync6poison5mutex10MutexGuardbEECs98fvGvYc57G_10rayon_core.llvm.17002324475202138184;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtNtCse0R8cuyqEa_3std4sync6poison5mutex10MutexGuardbEECs98fvGvYc57G_10rayon_core.llvm.17002324475202138184,unique,17
	.globl	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtNtCse0R8cuyqEa_3std4sync6poison5mutex10MutexGuardbEECs98fvGvYc57G_10rayon_core.llvm.17002324475202138184
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtNtCse0R8cuyqEa_3std4sync6poison5mutex10MutexGuardbEECs98fvGvYc57G_10rayon_core.llvm.17002324475202138184:
.Lfunc_begin17:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtNtCse0R8cuyqEa_3std4sync6poison5mutex10MutexGuardbEECs98fvGvYc57G_10rayon_core.llvm.17002324475202138184
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	testb	$1, %dl
	jne	.LBB17_4
	movq	_RNvNtNtCse0R8cuyqEa_3std9panicking11panic_count18GLOBAL_PANIC_COUNT(%rip), %rax
	shlq	%rax
	testq	%rax, %rax
	jne	.LBB17_2
.LBB17_4:
	xorl	%eax, %eax
	xchgb	%al, (%rcx)
	cmpb	$2, %al
	je	.LBB17_6
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB17_6:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	rex64 jmpq	*__imp_WakeByAddressSingle(%rip)
.LBB17_2:
	movq	%rcx, %rsi
	callq	_RNvNtNtCse0R8cuyqEa_3std9panicking11panic_count17is_zero_slow_path
	movq	%rsi, %rcx
	testb	%al, %al
	jne	.LBB17_4
	movb	$1, 1(%rcx)
	jmp	.LBB17_4
.Lfunc_end17:
	.seh_endproc

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_,unique,18
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_:
.Lfunc_begin18:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_
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
	cmpq	$-1, %rax
	je	.LBB18_3
	testq	%rax, %rax
	je	.LBB18_3
	movq	24(%rsi), %rcx
	callq	mi_free
.LBB18_3:
	movq	56(%rsi), %rax
	lock		decq	(%rax)
	je	.LBB18_4
	movq	40(%rsi), %rax
	lock		decq	(%rax)
	je	.LBB18_6
.LBB18_7:
	movq	88(%rsi), %rax
	lock		decq	(%rax)
	movq	%rsi, -8(%rbp)
	je	.LBB18_8
	jmp	.LBB18_9
.LBB18_4:
	leaq	56(%rsi), %rcx
	#MEMBARRIER
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
	movq	40(%rsi), %rax
	lock		decq	(%rax)
	jne	.LBB18_7
.LBB18_6:
	leaq	40(%rsi), %rcx
	#MEMBARRIER
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
	movq	88(%rsi), %rax
	lock		decq	(%rax)
	movq	%rsi, -8(%rbp)
	jne	.LBB18_9
.LBB18_8:
	movq	-8(%rbp), %rax
	leaq	88(%rax), %rcx
	#MEMBARRIER
.Ltmp88:
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_
	nop
.Ltmp89:
.LBB18_9:
	movq	-8(%rbp), %rcx
	leaq	104(%rcx), %rax
	movq	%rax, -24(%rbp)
	addq	$128, %rcx
.Ltmp90:
	movq	%rcx, -16(%rbp)
	callq	_RNvXNtNtCse0R8cuyqEa_3std6thread9spawnhookNtB2_10SpawnHooksNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop
	nop
.Ltmp91:
	movq	-16(%rbp), %rcx
	movq	(%rcx), %rax
	testq	%rax, %rax
	je	.LBB18_13
	lock		decq	(%rax)
	jne	.LBB18_13
	#MEMBARRIER
.Ltmp92:
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtCse0R8cuyqEa_3std6thread9spawnhook9SpawnHookE9drop_slowBM_
	nop
.Ltmp93:
.LBB18_13:
.Ltmp94:
	movq	-24(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtBG_5boxed3BoxDINtNtNtB4_3ops8function6FnOnceuEp6OutputuNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core
	nop
.Ltmp95:
	movq	-8(%rbp), %rcx
	movq	136(%rcx), %rax
	lock		decq	(%rax)
	jne	.LBB18_24
	addq	$136, %rcx
	#MEMBARRIER
	.seh_startepilogue
	addq	$72, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	jmp	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEE9drop_slowBN_
.LBB18_24:
	.seh_startepilogue
	addq	$72, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_@IMGREL
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_,unique,18
	.seh_endproc
	.def	"?dtor$16@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$16@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_@4HA":
.seh_proc "?dtor$16@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_@4HA"
.LBB18_16:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	64(%rdx), %rbp
	.seh_endprologue
	movq	-16(%rbp), %rax
	movq	%rax, %rcx
	movq	(%rax), %rax
	testq	%rax, %rax
	je	.LBB18_19
	lock		decq	(%rax)
	jne	.LBB18_19
	#MEMBARRIER
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtCse0R8cuyqEa_3std6thread9spawnhook9SpawnHookE9drop_slowBM_
	nop
.LBB18_19:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_,unique,18
	.seh_endproc
	.def	"?dtor$20@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$20@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_@4HA":
.seh_proc "?dtor$20@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_@4HA"
.LBB18_20:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	64(%rdx), %rbp
	.seh_endprologue
	movq	-24(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtBG_5boxed3BoxDINtNtNtB4_3ops8function6FnOnceuEp6OutputuNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core
	nop
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_,unique,18
	.seh_endproc
	.def	"?dtor$21@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$21@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_@4HA":
.seh_proc "?dtor$21@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_@4HA"
.LBB18_21:
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
	movq	136(%rax), %rax
	lock		decq	(%rax)
	jne	.LBB18_23
	movq	-8(%rbp), %rcx
	addq	$136, %rcx
	#MEMBARRIER
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEE9drop_slowBN_
	nop
.LBB18_23:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_,unique,18
	.seh_endproc
	.def	"?dtor$25@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$25@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_@4HA":
.seh_proc "?dtor$25@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_@4HA"
.LBB18_25:
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
	leaq	104(%rax), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9spawnhook15ChildSpawnHooksECs98fvGvYc57G_10rayon_core
	nop
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end18:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_,unique,18
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_,unique,10
	.p2align	2, 0x0
$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_:
	.long	429065506
	.long	4
	.long	$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_@IMGREL
	.long	0
	.long	0
	.long	6
	.long	$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_@IMGREL
	.long	64
	.long	0
	.long	1
$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_:
	.long	-1
	.long	"?dtor$21@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_@4HA"@IMGREL
	.long	0
	.long	"?dtor$20@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_@4HA"@IMGREL
	.long	1
	.long	"?dtor$16@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_@4HA"@IMGREL
	.long	0
	.long	"?dtor$25@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_@4HA"@IMGREL
$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_:
	.long	.Lfunc_begin18@IMGREL
	.long	-1
	.long	.Ltmp88@IMGREL
	.long	3
	.long	.Ltmp90@IMGREL
	.long	2
	.long	.Ltmp92@IMGREL
	.long	1
	.long	.Ltmp94@IMGREL
	.long	0
	.long	.Ltmp95@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_,unique,18

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtBJ_12DefaultSpawnNtBJ_11ThreadSpawn5spawn0EBL_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtBJ_12DefaultSpawnNtBJ_11ThreadSpawn5spawn0EBL_,unique,19
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtBJ_12DefaultSpawnNtBJ_11ThreadSpawn5spawn0EBL_:
.Lfunc_begin19:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtBJ_12DefaultSpawnNtBJ_11ThreadSpawn5spawn0EBL_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	%rcx, %rsi
	movq	16(%rcx), %rax
	cmpq	$-1, %rax
	je	.LBB19_3
	testq	%rax, %rax
	je	.LBB19_3
	movq	24(%rsi), %rcx
	callq	mi_free
.LBB19_3:
	movq	56(%rsi), %rax
	lock		decq	(%rax)
	je	.LBB19_4
	movq	40(%rsi), %rax
	lock		decq	(%rax)
	je	.LBB19_6
.LBB19_7:
	movq	88(%rsi), %rax
	lock		decq	(%rax)
	jne	.LBB19_8
.LBB19_9:
	addq	$88, %rsi
	#MEMBARRIER
	movq	%rsi, %rcx
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	jmp	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_
.LBB19_4:
	leaq	56(%rsi), %rcx
	#MEMBARRIER
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
	movq	40(%rsi), %rax
	lock		decq	(%rax)
	jne	.LBB19_7
.LBB19_6:
	leaq	40(%rsi), %rcx
	#MEMBARRIER
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
	movq	88(%rsi), %rax
	lock		decq	(%rax)
	je	.LBB19_9
.LBB19_8:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end19:
	.seh_endproc

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_,unique,20
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_:
.Lfunc_begin20:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_
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
	movq	24(%rcx), %rax
	movq	%rax, -8(%rbp)
	testq	%rax, %rax
	movq	%rcx, -16(%rbp)
	je	.LBB20_5
	movq	32(%rsi), %rax
	movq	%rax, -24(%rbp)
	movq	(%rax), %rax
	testq	%rax, %rax
	je	.LBB20_3
.Ltmp96:
	movq	-8(%rbp), %rcx
	callq	*%rax
	nop
.Ltmp97:
.LBB20_3:
	movq	-24(%rbp), %rax
	cmpq	$0, 8(%rax)
	movq	-16(%rbp), %rsi
	je	.LBB20_5
	movq	-8(%rbp), %rcx
	callq	mi_free
.LBB20_5:
	movq	40(%rsi), %rax
	movq	%rax, -8(%rbp)
	testq	%rax, %rax
	je	.LBB20_10
	movq	48(%rsi), %rax
	movq	%rax, -24(%rbp)
	movq	(%rax), %rax
	testq	%rax, %rax
	je	.LBB20_8
.Ltmp98:
	movq	-8(%rbp), %rcx
	callq	*%rax
	nop
.Ltmp99:
.LBB20_8:
	movq	-24(%rbp), %rax
	cmpq	$0, 8(%rax)
	movq	-16(%rbp), %rsi
	je	.LBB20_10
	movq	-8(%rbp), %rcx
	callq	mi_free
.LBB20_10:
	movq	56(%rsi), %rax
	movq	%rax, -8(%rbp)
	testq	%rax, %rax
	je	.LBB20_15
	movq	64(%rsi), %rax
	movq	%rax, -24(%rbp)
	movq	(%rax), %rax
	testq	%rax, %rax
	je	.LBB20_13
.Ltmp100:
	movq	-8(%rbp), %rcx
	callq	*%rax
	nop
.Ltmp101:
.LBB20_13:
	movq	-24(%rbp), %rax
	cmpq	$0, 8(%rax)
	movq	-16(%rbp), %rsi
	je	.LBB20_15
	movq	-8(%rbp), %rcx
	callq	mi_free
.LBB20_15:
	movq	72(%rsi), %rax
	movq	%rax, -16(%rbp)
	testq	%rax, %rax
	je	.LBB20_34
	movq	80(%rsi), %rax
	movq	%rax, -8(%rbp)
	movq	(%rax), %rax
	testq	%rax, %rax
	je	.LBB20_18
.Ltmp102:
	movq	-16(%rbp), %rcx
	callq	*%rax
	nop
.Ltmp103:
.LBB20_18:
	movq	-8(%rbp), %rax
	cmpq	$0, 8(%rax)
	je	.LBB20_34
	movq	-16(%rbp), %rcx
	.seh_startepilogue
	addq	$72, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	jmp	mi_free
.LBB20_34:
	.seh_startepilogue
	addq	$72, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_@IMGREL
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_,unique,20
	.seh_endproc
	.def	"?dtor$20@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$20@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_@4HA":
.seh_proc "?dtor$20@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_@4HA"
.LBB20_20:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	64(%rdx), %rbp
	.seh_endprologue
	movq	-24(%rbp), %rax
	cmpq	$0, 8(%rax)
	je	.LBB20_22
	movq	-8(%rbp), %rcx
	callq	mi_free
.LBB20_22:
	movq	-16(%rbp), %rax
	movq	40(%rax), %rcx
	movq	48(%rax), %rdx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6option6OptionINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDINtNtNtB4_3ops8function2FnTjEEp6OutputuNtNtB4_6marker4SendNtB2c_4SyncEL_EEECs98fvGvYc57G_10rayon_core
	nop
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_,unique,20
	.seh_endproc
	.def	"?dtor$23@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$23@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_@4HA":
.seh_proc "?dtor$23@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_@4HA"
.LBB20_23:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	64(%rdx), %rbp
	.seh_endprologue
	movq	-24(%rbp), %rax
	cmpq	$0, 8(%rax)
	je	.LBB20_25
	movq	-8(%rbp), %rcx
	callq	mi_free
	nop
.LBB20_25:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_,unique,20
	.seh_endproc
	.def	"?dtor$26@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$26@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_@4HA":
.seh_proc "?dtor$26@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_@4HA"
.LBB20_26:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	64(%rdx), %rbp
	.seh_endprologue
	movq	-16(%rbp), %rax
	movq	56(%rax), %rcx
	movq	64(%rax), %rdx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6option6OptionINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDINtNtNtB4_3ops8function2FnTjEEp6OutputuNtNtB4_6marker4SendNtB2c_4SyncEL_EEECs98fvGvYc57G_10rayon_core
	nop
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_,unique,20
	.seh_endproc
	.def	"?dtor$27@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$27@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_@4HA":
.seh_proc "?dtor$27@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_@4HA"
.LBB20_27:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	64(%rdx), %rbp
	.seh_endprologue
	movq	-24(%rbp), %rax
	cmpq	$0, 8(%rax)
	je	.LBB20_29
	movq	-8(%rbp), %rcx
	callq	mi_free
	nop
.LBB20_29:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_,unique,20
	.seh_endproc
	.def	"?dtor$30@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$30@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_@4HA":
.seh_proc "?dtor$30@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_@4HA"
.LBB20_30:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	64(%rdx), %rbp
	.seh_endprologue
	movq	-16(%rbp), %rax
	movq	72(%rax), %rcx
	movq	80(%rax), %rdx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6option6OptionINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDINtNtNtB4_3ops8function2FnTjEEp6OutputuNtNtB4_6marker4SendNtB2c_4SyncEL_EEECs98fvGvYc57G_10rayon_core
	nop
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_,unique,20
	.seh_endproc
	.def	"?dtor$31@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$31@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_@4HA":
.seh_proc "?dtor$31@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_@4HA"
.LBB20_31:
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
	cmpq	$0, 8(%rax)
	je	.LBB20_33
	movq	-16(%rbp), %rcx
	callq	mi_free
	nop
.LBB20_33:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end20:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_,unique,20
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_,unique,11
	.p2align	2, 0x0
$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_:
	.long	429065506
	.long	6
	.long	$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_@IMGREL
	.long	0
	.long	0
	.long	6
	.long	$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_@IMGREL
	.long	64
	.long	0
	.long	1
$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_:
	.long	-1
	.long	"?dtor$30@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_@4HA"@IMGREL
	.long	0
	.long	"?dtor$27@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_@4HA"@IMGREL
	.long	0
	.long	"?dtor$26@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_@4HA"@IMGREL
	.long	2
	.long	"?dtor$23@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_@4HA"@IMGREL
	.long	2
	.long	"?dtor$20@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_@4HA"@IMGREL
	.long	-1
	.long	"?dtor$31@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_@4HA"@IMGREL
$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_:
	.long	.Lfunc_begin20@IMGREL
	.long	-1
	.long	.Ltmp96@IMGREL
	.long	4
	.long	.Ltmp98@IMGREL
	.long	3
	.long	.Ltmp100@IMGREL
	.long	1
	.long	.Ltmp102@IMGREL
	.long	5
	.long	.Ltmp103@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core17ThreadPoolBuilderEBD_,unique,20

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core20ThreadPoolBuildErrorEBD_.llvm.17002324475202138184;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core20ThreadPoolBuildErrorEBD_.llvm.17002324475202138184,unique,21
	.globl	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core20ThreadPoolBuildErrorEBD_.llvm.17002324475202138184
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core20ThreadPoolBuildErrorEBD_.llvm.17002324475202138184:
.Lfunc_begin21:
	cmpl	$2, (%rcx)
	jb	.LBB21_3
	movq	8(%rcx), %rax
	movl	%eax, %ecx
	andl	$3, %ecx
	leal	-2(%rcx), %edx
	cmpl	$2, %edx
	jb	.LBB21_3
	testq	%rcx, %rcx
	jne	.LBB21_4
.LBB21_3:
	retq
.LBB21_4:
	leaq	-1(%rax), %rcx
	rex64 jmpq	*23(%rax)
.Lfunc_end21:

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs3qjAvHHmxHz_15crossbeam_epoch5guard5GuardECs98fvGvYc57G_10rayon_core;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs3qjAvHHmxHz_15crossbeam_epoch5guard5GuardECs98fvGvYc57G_10rayon_core,unique,22
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs3qjAvHHmxHz_15crossbeam_epoch5guard5GuardECs98fvGvYc57G_10rayon_core:
.Lfunc_begin22:
	testq	%rcx, %rcx
	je	.LBB22_3
	decq	2072(%rcx)
	jne	.LBB22_3
	movq	$0, 2176(%rcx)
	cmpq	$0, 2080(%rcx)
	je	_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize
.LBB22_3:
	retq
.Lfunc_end22:

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core3job7JobFifoEBF_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core3job7JobFifoEBF_,unique,23
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core3job7JobFifoEBF_:
.Lfunc_begin23:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core3job7JobFifoEBF_
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	128(%rcx), %rsi
	movq	(%rcx), %rdi
	movq	8(%rcx), %rcx
	andq	$-2, %rdi
	andq	$-2, %rsi
	cmpq	%rsi, %rdi
	jne	.LBB23_1
.LBB23_4:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	jmp	mi_free
	.p2align	4
.LBB23_3:
	addq	$2, %rdi
	cmpq	%rdi, %rsi
	je	.LBB23_4
.LBB23_1:
	movl	%edi, %eax
	notl	%eax
	testb	$126, %al
	jne	.LBB23_3
	movq	(%rcx), %rbx
	callq	mi_free
	movq	%rbx, %rcx
	jmp	.LBB23_3
.Lfunc_end23:
	.seh_endproc

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry10TerminatorEBF_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry10TerminatorEBF_,unique,24
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry10TerminatorEBF_:
.Lfunc_begin24:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry10TerminatorEBF_
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
	lock		decq	464(%rcx)
	jne	.LBB24_6
	movq	%rcx, %rsi
	movq	520(%rcx), %rax
	testq	%rax, %rax
	je	.LBB24_6
	movq	512(%rsi), %rbx
	shlq	$3, %rax
	leaq	(%rax,%rax,4), %r14
	addq	$472, %rsi
	xorl	%edi, %edi
	xorl	%r15d, %r15d
	jmp	.LBB24_3
	.p2align	4
.LBB24_5:
	addq	$40, %r15
	incq	%rdi
	cmpq	%r15, %r14
	je	.LBB24_6
.LBB24_3:
	movl	$3, %eax
	xchgq	%rax, 16(%rbx,%r15)
	cmpq	$2, %rax
	jne	.LBB24_5
	movq	%rsi, %rcx
	movq	%rdi, %rdx
	callq	_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep20wake_specific_thread.llvm.17002324475202138184
	jmp	.LBB24_5
.LBB24_6:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	.seh_endepilogue
	retq
.Lfunc_end24:
	.seh_endproc

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry12WorkerThreadEBF_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry12WorkerThreadEBF_,unique,25
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry12WorkerThreadEBF_:
.Lfunc_begin25:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry12WorkerThreadEBF_
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
	subq	$48, %rsp
	.seh_stackalloc 48
	leaq	48(%rsp), %rbp
	.seh_setframe %rbp, 48
	.seh_endprologue
	movq	$-2, -8(%rbp)
	movq	%rcx, %r14
	movl	_tls_index(%rip), %eax
	movq	%gs:88, %rcx
	movq	(%rcx,%rax,8), %rax
	cmpq	%r14, _RNvNCNKNvNtCs98fvGvYc57G_10rayon_core8registry19WORKER_THREAD_STATE0s_023___RUST_STD_INTERNAL_VAL@SECREL32(%rax)
	jne	.LBB25_1
	leaq	_RNvNCNKNvNtCs98fvGvYc57G_10rayon_core8registry19WORKER_THREAD_STATE0s_023___RUST_STD_INTERNAL_VAL@SECREL32(%rax), %rax
	movq	$0, (%rax)
	movq	280(%r14), %rax
	lock		decq	(%rax)
	jne	.LBB25_12
	leaq	280(%r14), %rcx
	#MEMBARRIER
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
.LBB25_12:
	movq	312(%r14), %rax
	lock		decq	(%rax)
	jne	.LBB25_14
	leaq	312(%r14), %rcx
	#MEMBARRIER
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
.LBB25_14:
	movq	128(%r14), %rsi
	movq	(%r14), %rdi
	movq	8(%r14), %rcx
	andq	$-2, %rdi
	andq	$-2, %rsi
	cmpq	%rsi, %rdi
	jne	.LBB25_15
.LBB25_18:
	callq	mi_free
	movq	272(%r14), %rax
	lock		decq	(%rax)
	jne	.LBB25_19
	addq	$272, %r14
	#MEMBARRIER
	movq	%r14, %rcx
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	jmp	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_
	.p2align	4
.LBB25_17:
	addq	$2, %rdi
	cmpq	%rdi, %rsi
	je	.LBB25_18
.LBB25_15:
	movl	%edi, %eax
	notl	%eax
	testb	$126, %al
	jne	.LBB25_17
	movq	(%rcx), %rbx
	callq	mi_free
	movq	%rbx, %rcx
	jmp	.LBB25_17
.LBB25_19:
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.LBB25_1:
.Ltmp104:
	movq	%r14, -16(%rbp)
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.23(%rip), %rcx
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.24(%rip), %r8
	movl	$49, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking5panic
	nop
.Ltmp105:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry12WorkerThreadEBF_@IMGREL
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry12WorkerThreadEBF_,unique,25
	.seh_endproc
	.def	"?dtor$3@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry12WorkerThreadEBF_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$3@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry12WorkerThreadEBF_@4HA":
.seh_proc "?dtor$3@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry12WorkerThreadEBF_@4HA"
.LBB25_3:
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
	leaq	48(%rdx), %rbp
	.seh_endprologue
	movq	-16(%rbp), %rsi
	movq	280(%rsi), %rax
	lock		decq	(%rax)
	jne	.LBB25_5
	leaq	280(%rsi), %rcx
	#MEMBARRIER
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
.LBB25_5:
	movq	312(%rsi), %rax
	lock		decq	(%rax)
	jne	.LBB25_7
	leaq	312(%rsi), %rcx
	#MEMBARRIER
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
.LBB25_7:
	movq	%rsi, %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core3job7JobFifoEBF_
	movq	272(%rsi), %rax
	lock		decq	(%rax)
	jne	.LBB25_9
	addq	$272, %rsi
	#MEMBARRIER
	movq	%rsi, %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_
	nop
.LBB25_9:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end25:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry12WorkerThreadEBF_,unique,25
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry12WorkerThreadEBF_,unique,12
	.p2align	2, 0x0
$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry12WorkerThreadEBF_:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry12WorkerThreadEBF_@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry12WorkerThreadEBF_@IMGREL
	.long	40
	.long	0
	.long	1
$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry12WorkerThreadEBF_:
	.long	-1
	.long	"?dtor$3@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry12WorkerThreadEBF_@4HA"@IMGREL
$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry12WorkerThreadEBF_:
	.long	.Lfunc_begin25@IMGREL
	.long	-1
	.long	.Ltmp104@IMGREL
	.long	0
	.long	.Ltmp105@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry12WorkerThreadEBF_,unique,25

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry13ThreadBuilderEBF_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry13ThreadBuilderEBF_,unique,26
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry13ThreadBuilderEBF_:
.Lfunc_begin26:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry13ThreadBuilderEBF_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	%rcx, %rsi
	movq	16(%rcx), %rax
	cmpq	$-1, %rax
	je	.LBB26_3
	testq	%rax, %rax
	je	.LBB26_3
	movq	24(%rsi), %rcx
	callq	mi_free
.LBB26_3:
	movq	56(%rsi), %rax
	lock		decq	(%rax)
	je	.LBB26_4
	movq	40(%rsi), %rax
	lock		decq	(%rax)
	je	.LBB26_6
.LBB26_7:
	movq	88(%rsi), %rax
	lock		decq	(%rax)
	jne	.LBB26_8
.LBB26_9:
	addq	$88, %rsi
	#MEMBARRIER
	movq	%rsi, %rcx
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	jmp	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_
.LBB26_4:
	leaq	56(%rsi), %rcx
	#MEMBARRIER
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
	movq	40(%rsi), %rax
	lock		decq	(%rax)
	jne	.LBB26_7
.LBB26_6:
	leaq	40(%rsi), %rcx
	#MEMBARRIER
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
	movq	88(%rsi), %rax
	lock		decq	(%rax)
	je	.LBB26_9
.LBB26_8:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end26:
	.seh_endproc

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_,unique,27
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_:
.Lfunc_begin27:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_
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
	movq	%rcx, %r14
	movq	384(%rcx), %rsi
	movq	392(%rcx), %rbx
	testq	%rbx, %rbx
	je	.LBB27_5
	leaq	24(%rsi), %rdi
	jmp	.LBB27_2
	.p2align	4
.LBB27_4:
	addq	$40, %rdi
	decq	%rbx
	je	.LBB27_5
.LBB27_2:
	movq	(%rdi), %rax
	lock		decq	(%rax)
	jne	.LBB27_4
	#MEMBARRIER
	movq	%rdi, %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
	jmp	.LBB27_4
.LBB27_5:
	cmpq	$0, 376(%r14)
	je	.LBB27_7
	movq	%rsi, %rcx
	callq	mi_free
.LBB27_7:
	cmpq	$0, 344(%r14)
	je	.LBB27_9
	movq	352(%r14), %rcx
	callq	mi_free
.LBB27_9:
	movq	128(%r14), %rsi
	movq	(%r14), %rdi
	movq	8(%r14), %rcx
	andq	$-2, %rdi
	andq	$-2, %rsi
	cmpq	%rsi, %rdi
	jne	.LBB27_10
.LBB27_13:
	callq	mi_free
	movq	272(%r14), %rsi
	movq	280(%r14), %rbx
	testq	%rbx, %rbx
	je	.LBB27_18
	movq	%rsi, %rdi
	jmp	.LBB27_15
	.p2align	4
.LBB27_17:
	addq	$32, %rdi
	decq	%rbx
	je	.LBB27_18
.LBB27_15:
	movq	(%rdi), %rax
	lock		decq	(%rax)
	jne	.LBB27_17
	#MEMBARRIER
	movq	%rdi, %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
	jmp	.LBB27_17
	.p2align	4
.LBB27_12:
	addq	$2, %rdi
	cmpq	%rdi, %rsi
	je	.LBB27_13
.LBB27_10:
	movl	%edi, %eax
	notl	%eax
	testb	$126, %al
	jne	.LBB27_12
	movq	(%rcx), %rbx
	callq	mi_free
	movq	%rbx, %rcx
	jmp	.LBB27_12
.LBB27_18:
	cmpq	$0, 264(%r14)
	je	.LBB27_20
	movq	%rsi, %rcx
	callq	mi_free
.LBB27_20:
	movq	288(%r14), %rax
	movq	%rax, -16(%rbp)
	testq	%rax, %rax
	movq	%r14, -24(%rbp)
	je	.LBB27_25
	movq	296(%r14), %rax
	movq	%rax, -32(%rbp)
	movq	(%rax), %rax
	testq	%rax, %rax
	je	.LBB27_23
.Ltmp106:
	movq	-16(%rbp), %rcx
	callq	*%rax
	nop
.Ltmp107:
.LBB27_23:
	movq	-32(%rbp), %rax
	cmpq	$0, 8(%rax)
	movq	-24(%rbp), %r14
	je	.LBB27_25
	movq	-16(%rbp), %rcx
	callq	mi_free
.LBB27_25:
	movq	304(%r14), %rax
	movq	%rax, -16(%rbp)
	testq	%rax, %rax
	je	.LBB27_30
	movq	312(%r14), %rax
	movq	%rax, -32(%rbp)
	movq	(%rax), %rax
	testq	%rax, %rax
	je	.LBB27_28
.Ltmp108:
	movq	-16(%rbp), %rcx
	callq	*%rax
	nop
.Ltmp109:
.LBB27_28:
	movq	-32(%rbp), %rax
	cmpq	$0, 8(%rax)
	movq	-24(%rbp), %r14
	je	.LBB27_30
	movq	-16(%rbp), %rcx
	callq	mi_free
.LBB27_30:
	movq	320(%r14), %rax
	movq	%rax, -16(%rbp)
	testq	%rax, %rax
	je	.LBB27_45
	movq	328(%r14), %rax
	movq	%rax, -24(%rbp)
	movq	(%rax), %rax
	testq	%rax, %rax
	je	.LBB27_33
.Ltmp110:
	movq	-16(%rbp), %rcx
	callq	*%rax
	nop
.Ltmp111:
.LBB27_33:
	movq	-24(%rbp), %rax
	cmpq	$0, 8(%rax)
	je	.LBB27_45
	movq	-16(%rbp), %rcx
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	jmp	mi_free
.LBB27_45:
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
	.long	$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_@IMGREL
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_,unique,27
	.seh_endproc
	.def	"?dtor$35@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$35@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_@4HA":
.seh_proc "?dtor$35@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_@4HA"
.LBB27_35:
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
	movq	-32(%rbp), %rax
	cmpq	$0, 8(%rax)
	je	.LBB27_37
	movq	-16(%rbp), %rcx
	callq	mi_free
.LBB27_37:
	movq	-24(%rbp), %rax
	movq	304(%rax), %rcx
	movq	312(%rax), %rdx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6option6OptionINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDINtNtNtB4_3ops8function2FnTjEEp6OutputuNtNtB4_6marker4SendNtB2c_4SyncEL_EEECs98fvGvYc57G_10rayon_core
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
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_,unique,27
	.seh_endproc
	.def	"?dtor$38@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$38@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_@4HA":
.seh_proc "?dtor$38@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_@4HA"
.LBB27_38:
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
	movq	-32(%rbp), %rax
	cmpq	$0, 8(%rax)
	je	.LBB27_40
	movq	-16(%rbp), %rcx
	callq	mi_free
	nop
.LBB27_40:
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
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_,unique,27
	.seh_endproc
	.def	"?dtor$41@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$41@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_@4HA":
.seh_proc "?dtor$41@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_@4HA"
.LBB27_41:
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
	movq	-24(%rbp), %rax
	movq	320(%rax), %rcx
	movq	328(%rax), %rdx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6option6OptionINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDINtNtNtB4_3ops8function2FnTjEEp6OutputuNtNtB4_6marker4SendNtB2c_4SyncEL_EEECs98fvGvYc57G_10rayon_core
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
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_,unique,27
	.seh_endproc
	.def	"?dtor$42@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$42@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_@4HA":
.seh_proc "?dtor$42@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_@4HA"
.LBB27_42:
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
	movq	-24(%rbp), %rax
	cmpq	$0, 8(%rax)
	je	.LBB27_44
	movq	-16(%rbp), %rcx
	callq	mi_free
	nop
.LBB27_44:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end27:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_,unique,27
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_,unique,13
	.p2align	2, 0x0
$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_:
	.long	429065506
	.long	4
	.long	$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_@IMGREL
	.long	0
	.long	0
	.long	5
	.long	$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_@IMGREL
	.long	56
	.long	0
	.long	1
$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_:
	.long	-1
	.long	"?dtor$41@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_@4HA"@IMGREL
	.long	0
	.long	"?dtor$38@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_@4HA"@IMGREL
	.long	0
	.long	"?dtor$35@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_@4HA"@IMGREL
	.long	-1
	.long	"?dtor$42@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_@4HA"@IMGREL
$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_:
	.long	.Lfunc_begin27@IMGREL
	.long	-1
	.long	.Ltmp106@IMGREL
	.long	2
	.long	.Ltmp108@IMGREL
	.long	1
	.long	.Ltmp110@IMGREL
	.long	3
	.long	.Ltmp111@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_,unique,27

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9lifecycle10ThreadInitECs98fvGvYc57G_10rayon_core;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9lifecycle10ThreadInitECs98fvGvYc57G_10rayon_core,unique,28
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9lifecycle10ThreadInitECs98fvGvYc57G_10rayon_core:
.Lfunc_begin28:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9lifecycle10ThreadInitECs98fvGvYc57G_10rayon_core
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
	movq	%rcx, %rsi
	movq	(%rcx), %rax
	lock		decq	(%rax)
	jne	.LBB28_2
	#MEMBARRIER
	movq	%rsi, %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtCse0R8cuyqEa_3std6thread6thread5InnerNtNtBM_5alloc6SystemE9drop_slowBM_
.LBB28_2:
	movq	8(%rsi), %rax
	movq	%rax, -8(%rbp)
	movq	16(%rsi), %rax
	movq	%rax, -16(%rbp)
	movq	(%rax), %rax
	testq	%rax, %rax
	je	.LBB28_4
.Ltmp112:
	movq	-8(%rbp), %rcx
	callq	*%rax
	nop
.Ltmp113:
.LBB28_4:
	movq	-8(%rbp), %rcx
	movq	-16(%rbp), %rax
	cmpq	$0, 8(%rax)
	je	.LBB28_9
	.seh_startepilogue
	addq	$56, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	jmp	mi_free
.LBB28_9:
	.seh_startepilogue
	addq	$56, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9lifecycle10ThreadInitECs98fvGvYc57G_10rayon_core@IMGREL
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9lifecycle10ThreadInitECs98fvGvYc57G_10rayon_core,unique,28
	.seh_endproc
	.def	"?dtor$6@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9lifecycle10ThreadInitECs98fvGvYc57G_10rayon_core@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$6@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9lifecycle10ThreadInitECs98fvGvYc57G_10rayon_core@4HA":
.seh_proc "?dtor$6@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9lifecycle10ThreadInitECs98fvGvYc57G_10rayon_core@4HA"
.LBB28_6:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	48(%rdx), %rbp
	.seh_endprologue
	movq	-8(%rbp), %rcx
	movq	-16(%rbp), %rax
	cmpq	$0, 8(%rax)
	je	.LBB28_8
	callq	mi_free
	nop
.LBB28_8:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end28:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9lifecycle10ThreadInitECs98fvGvYc57G_10rayon_core,unique,28
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9lifecycle10ThreadInitECs98fvGvYc57G_10rayon_core,unique,14
	.p2align	2, 0x0
$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9lifecycle10ThreadInitECs98fvGvYc57G_10rayon_core:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9lifecycle10ThreadInitECs98fvGvYc57G_10rayon_core@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9lifecycle10ThreadInitECs98fvGvYc57G_10rayon_core@IMGREL
	.long	48
	.long	0
	.long	1
$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9lifecycle10ThreadInitECs98fvGvYc57G_10rayon_core:
	.long	-1
	.long	"?dtor$6@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9lifecycle10ThreadInitECs98fvGvYc57G_10rayon_core@4HA"@IMGREL
$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9lifecycle10ThreadInitECs98fvGvYc57G_10rayon_core:
	.long	.Lfunc_begin28@IMGREL
	.long	-1
	.long	.Ltmp112@IMGREL
	.long	0
	.long	.Ltmp113@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9lifecycle10ThreadInitECs98fvGvYc57G_10rayon_core,unique,28

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9spawnhook15ChildSpawnHooksECs98fvGvYc57G_10rayon_core;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9spawnhook15ChildSpawnHooksECs98fvGvYc57G_10rayon_core,unique,29
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9spawnhook15ChildSpawnHooksECs98fvGvYc57G_10rayon_core:
.Lfunc_begin29:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9spawnhook15ChildSpawnHooksECs98fvGvYc57G_10rayon_core
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$64, %rsp
	.seh_stackalloc 64
	leaq	64(%rsp), %rbp
	.seh_setframe %rbp, 64
	.seh_endprologue
	movq	$-2, -8(%rbp)
	movq	%rcx, -24(%rbp)
	addq	$24, %rcx
.Ltmp114:
	movq	%rcx, -16(%rbp)
	callq	_RNvXNtNtCse0R8cuyqEa_3std6thread9spawnhookNtB2_10SpawnHooksNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop
	nop
.Ltmp115:
	movq	-16(%rbp), %rcx
	movq	(%rcx), %rax
	testq	%rax, %rax
	je	.LBB29_4
	lock		decq	(%rax)
	jne	.LBB29_4
	#MEMBARRIER
.Ltmp116:
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtCse0R8cuyqEa_3std6thread9spawnhook9SpawnHookE9drop_slowBM_
	nop
.Ltmp117:
.LBB29_4:
	movq	-24(%rbp), %rcx
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbp
	.seh_endepilogue
	jmp	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtBG_5boxed3BoxDINtNtNtB4_3ops8function6FnOnceuEp6OutputuNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core
	.seh_handlerdata
	.long	$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9spawnhook15ChildSpawnHooksECs98fvGvYc57G_10rayon_core@IMGREL
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9spawnhook15ChildSpawnHooksECs98fvGvYc57G_10rayon_core,unique,29
	.seh_endproc
	.def	"?dtor$5@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9spawnhook15ChildSpawnHooksECs98fvGvYc57G_10rayon_core@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$5@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9spawnhook15ChildSpawnHooksECs98fvGvYc57G_10rayon_core@4HA":
.seh_proc "?dtor$5@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9spawnhook15ChildSpawnHooksECs98fvGvYc57G_10rayon_core@4HA"
.LBB29_5:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	64(%rdx), %rbp
	.seh_endprologue
	movq	-16(%rbp), %rax
	movq	%rax, %rcx
	movq	(%rax), %rax
	testq	%rax, %rax
	je	.LBB29_8
	lock		decq	(%rax)
	jne	.LBB29_8
	#MEMBARRIER
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtCse0R8cuyqEa_3std6thread9spawnhook9SpawnHookE9drop_slowBM_
	nop
.LBB29_8:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9spawnhook15ChildSpawnHooksECs98fvGvYc57G_10rayon_core,unique,29
	.seh_endproc
	.def	"?dtor$9@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9spawnhook15ChildSpawnHooksECs98fvGvYc57G_10rayon_core@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$9@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9spawnhook15ChildSpawnHooksECs98fvGvYc57G_10rayon_core@4HA":
.seh_proc "?dtor$9@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9spawnhook15ChildSpawnHooksECs98fvGvYc57G_10rayon_core@4HA"
.LBB29_9:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	64(%rdx), %rbp
	.seh_endprologue
	movq	-24(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtBG_5boxed3BoxDINtNtNtB4_3ops8function6FnOnceuEp6OutputuNtNtB4_6marker4SendEL_EEECs98fvGvYc57G_10rayon_core
	nop
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end29:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9spawnhook15ChildSpawnHooksECs98fvGvYc57G_10rayon_core,unique,29
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9spawnhook15ChildSpawnHooksECs98fvGvYc57G_10rayon_core,unique,15
	.p2align	2, 0x0
$cppxdata$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9spawnhook15ChildSpawnHooksECs98fvGvYc57G_10rayon_core:
	.long	429065506
	.long	2
	.long	$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9spawnhook15ChildSpawnHooksECs98fvGvYc57G_10rayon_core@IMGREL
	.long	0
	.long	0
	.long	4
	.long	$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9spawnhook15ChildSpawnHooksECs98fvGvYc57G_10rayon_core@IMGREL
	.long	56
	.long	0
	.long	1
$stateUnwindMap$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9spawnhook15ChildSpawnHooksECs98fvGvYc57G_10rayon_core:
	.long	-1
	.long	"?dtor$9@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9spawnhook15ChildSpawnHooksECs98fvGvYc57G_10rayon_core@4HA"@IMGREL
	.long	0
	.long	"?dtor$5@?0?_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9spawnhook15ChildSpawnHooksECs98fvGvYc57G_10rayon_core@4HA"@IMGREL
$ip2state$_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9spawnhook15ChildSpawnHooksECs98fvGvYc57G_10rayon_core:
	.long	.Lfunc_begin29@IMGREL
	.long	-1
	.long	.Ltmp114@IMGREL
	.long	1
	.long	.Ltmp116@IMGREL
	.long	0
	.long	.Ltmp117@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9spawnhook15ChildSpawnHooksECs98fvGvYc57G_10rayon_core,unique,29

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNvNtNtCse0R8cuyqEa_3std3sys12thread_local20abort_on_dtor_unwind15DtorUnwindGuardECs98fvGvYc57G_10rayon_core;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNvNtNtCse0R8cuyqEa_3std3sys12thread_local20abort_on_dtor_unwind15DtorUnwindGuardECs98fvGvYc57G_10rayon_core,unique,30
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNvNtNtCse0R8cuyqEa_3std3sys12thread_local20abort_on_dtor_unwind15DtorUnwindGuardECs98fvGvYc57G_10rayon_core:
.Lfunc_begin30:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNvNtNtCse0R8cuyqEa_3std3sys12thread_local20abort_on_dtor_unwind15DtorUnwindGuardECs98fvGvYc57G_10rayon_core
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movl	$0, 32(%rsp)
	movb	$0, 36(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNvYNtNtNtNtCse0R8cuyqEa_3std3sys5stdio7windows6StderrNtNtBa_2io5Write9write_fmtCs98fvGvYc57G_10rayon_core
	movq	%rax, %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultuNtNtNtB4_2io5error5ErrorEECs98fvGvYc57G_10rayon_core
	movl	$7, %ecx
	#APP

	int	$41

	#NO_APP
	ud2
.Lfunc_end30:
	.seh_endproc

	.def	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueTINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtCslOUiAINmber_15crossbeam_deque5deque6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEIBD_INtB1c_7StealerB1W_EEEEB20_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueTINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtCslOUiAINmber_15crossbeam_deque5deque6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEIBD_INtB1c_7StealerB1W_EEEEB20_,unique,31
	.p2align	4
_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueTINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtCslOUiAINmber_15crossbeam_deque5deque6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEIBD_INtB1c_7StealerB1W_EEEEB20_:
.Lfunc_begin31:
.seh_proc _RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueTINtNtCsfQUUnEvlYZE_5alloc3vec3VecINtNtCslOUiAINmber_15crossbeam_deque5deque6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEIBD_INtB1c_7StealerB1W_EEEEB20_
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
	movq	8(%rcx), %rdi
	movq	16(%rcx), %r14
	testq	%r14, %r14
	je	.LBB31_5
	movq	%rdi, %rbx
	jmp	.LBB31_2
	.p2align	4
.LBB31_4:
	addq	$32, %rbx
	decq	%r14
	je	.LBB31_5
.LBB31_2:
	movq	(%rbx), %rax
	lock		decq	(%rax)
	jne	.LBB31_4
	#MEMBARRIER
	movq	%rbx, %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
	jmp	.LBB31_4
.LBB31_5:
	cmpq	$0, (%rsi)
	je	.LBB31_7
	movq	%rdi, %rcx
	callq	mi_free
.LBB31_7:
	movq	32(%rsi), %rdi
	movq	40(%rsi), %r14
	testq	%r14, %r14
	je	.LBB31_12
	movq	%rdi, %rbx
	jmp	.LBB31_9
	.p2align	4
.LBB31_11:
	addq	$16, %rbx
	decq	%r14
	je	.LBB31_12
.LBB31_9:
	movq	(%rbx), %rax
	lock		decq	(%rax)
	jne	.LBB31_11
	#MEMBARRIER
	movq	%rbx, %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
	jmp	.LBB31_11
.LBB31_12:
	cmpq	$0, 24(%rsi)
	je	.LBB31_13
	movq	%rdi, %rcx
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	jmp	mi_free
.LBB31_13:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.Lfunc_end31:
	.seh_endproc

	.def	_RINvNtNtCse0R8cuyqEa_3std3sys9backtrace28___rust_begin_short_backtraceNCNCNCINvNtNtB6_6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB22_12DefaultSpawnNtB22_11ThreadSpawn5spawn0uEs_000uEB24_;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtNtCse0R8cuyqEa_3std3sys9backtrace28___rust_begin_short_backtraceNCNCNCINvNtNtB6_6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB22_12DefaultSpawnNtB22_11ThreadSpawn5spawn0uEs_000uEB24_,unique,32
	.globl	_RINvNtNtCse0R8cuyqEa_3std3sys9backtrace28___rust_begin_short_backtraceNCNCNCINvNtNtB6_6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB22_12DefaultSpawnNtB22_11ThreadSpawn5spawn0uEs_000uEB24_
	.p2align	4
_RINvNtNtCse0R8cuyqEa_3std3sys9backtrace28___rust_begin_short_backtraceNCNCNCINvNtNtB6_6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB22_12DefaultSpawnNtB22_11ThreadSpawn5spawn0uEs_000uEB24_:
.Lfunc_begin32:
.seh_proc _RINvNtNtCse0R8cuyqEa_3std3sys9backtrace28___rust_begin_short_backtraceNCNCNCINvNtNtB6_6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB22_12DefaultSpawnNtB22_11ThreadSpawn5spawn0uEs_000uEB24_
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	movups	(%rcx), %xmm0
	movups	16(%rcx), %xmm1
	movaps	%xmm1, 48(%rsp)
	movaps	%xmm0, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNvMs_NtNtCse0R8cuyqEa_3std6thread9spawnhookNtB4_15ChildSpawnHooks15inherit_and_run
	nop
	#APP
	#NO_APP
	.seh_startepilogue
	addq	$72, %rsp
	.seh_endepilogue
	retq
.Lfunc_end32:
	.seh_endproc

	.def	_RINvNtNtCse0R8cuyqEa_3std3sys9backtrace28___rust_begin_short_backtraceNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1e_12DefaultSpawnNtB1e_11ThreadSpawn5spawn0uEB1g_;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtNtCse0R8cuyqEa_3std3sys9backtrace28___rust_begin_short_backtraceNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1e_12DefaultSpawnNtB1e_11ThreadSpawn5spawn0uEB1g_,unique,33
	.globl	_RINvNtNtCse0R8cuyqEa_3std3sys9backtrace28___rust_begin_short_backtraceNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1e_12DefaultSpawnNtB1e_11ThreadSpawn5spawn0uEB1g_
	.p2align	4
_RINvNtNtCse0R8cuyqEa_3std3sys9backtrace28___rust_begin_short_backtraceNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1e_12DefaultSpawnNtB1e_11ThreadSpawn5spawn0uEB1g_:
.Lfunc_begin33:
.seh_proc _RINvNtNtCse0R8cuyqEa_3std3sys9backtrace28___rust_begin_short_backtraceNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1e_12DefaultSpawnNtB1e_11ThreadSpawn5spawn0uEB1g_
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	callq	_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run
	nop
	#APP
	#NO_APP
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end33:
	.seh_endproc

	.def	_RINvNtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazy7destroyNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleECs98fvGvYc57G_10rayon_core;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazy7destroyNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleECs98fvGvYc57G_10rayon_core,unique,34
	.p2align	4
_RINvNtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazy7destroyNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleECs98fvGvYc57G_10rayon_core:
.Lfunc_begin34:
.seh_proc _RINvNtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazy7destroyNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleECs98fvGvYc57G_10rayon_core
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$48, %rsp
	.seh_stackalloc 48
	leaq	48(%rsp), %rbp
	.seh_setframe %rbp, 48
	.seh_endprologue
	movq	$-2, -8(%rbp)
	movzbl	8(%rcx), %eax
	movb	$2, 8(%rcx)
	cmpb	$1, %al
	jne	.LBB34_3
	movq	(%rcx), %rcx
	movq	2080(%rcx), %rax
	leaq	-1(%rax), %rdx
	movq	%rdx, 2080(%rcx)
	xorq	$1, %rax
	orq	2072(%rcx), %rax
	je	.LBB34_2
.LBB34_3:
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.LBB34_2:
.Ltmp118:
	callq	_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize
	nop
.Ltmp119:
	jmp	.LBB34_3
	.seh_handlerdata
	.long	$cppxdata$_RINvNtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazy7destroyNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleECs98fvGvYc57G_10rayon_core@IMGREL
	.section	.text,"xr",one_only,_RINvNtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazy7destroyNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleECs98fvGvYc57G_10rayon_core,unique,34
	.seh_endproc
	.def	"?dtor$4@?0?_RINvNtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazy7destroyNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleECs98fvGvYc57G_10rayon_core@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$4@?0?_RINvNtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazy7destroyNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleECs98fvGvYc57G_10rayon_core@4HA":
.seh_proc "?dtor$4@?0?_RINvNtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazy7destroyNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleECs98fvGvYc57G_10rayon_core@4HA"
.LBB34_4:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	48(%rdx), %rbp
	.seh_endprologue
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNvNtNtCse0R8cuyqEa_3std3sys12thread_local20abort_on_dtor_unwind15DtorUnwindGuardECs98fvGvYc57G_10rayon_core
	ud2
.Lfunc_end34:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RINvNtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazy7destroyNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleECs98fvGvYc57G_10rayon_core,unique,34
	.seh_endproc
	.section	.xdata,"dr",associative,_RINvNtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazy7destroyNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleECs98fvGvYc57G_10rayon_core,unique,16
	.p2align	2, 0x0
$cppxdata$_RINvNtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazy7destroyNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleECs98fvGvYc57G_10rayon_core:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RINvNtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazy7destroyNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleECs98fvGvYc57G_10rayon_core@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RINvNtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazy7destroyNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleECs98fvGvYc57G_10rayon_core@IMGREL
	.long	40
	.long	0
	.long	1
$stateUnwindMap$_RINvNtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazy7destroyNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleECs98fvGvYc57G_10rayon_core:
	.long	-1
	.long	"?dtor$4@?0?_RINvNtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazy7destroyNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleECs98fvGvYc57G_10rayon_core@4HA"@IMGREL
$ip2state$_RINvNtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazy7destroyNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleECs98fvGvYc57G_10rayon_core:
	.long	.Lfunc_begin34@IMGREL
	.long	-1
	.long	.Ltmp118@IMGREL
	.long	0
	.long	.Ltmp119@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RINvNtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazy7destroyNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleECs98fvGvYc57G_10rayon_core,unique,34

	.def	_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECs98fvGvYc57G_10rayon_core;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECs98fvGvYc57G_10rayon_core,unique,35
	.p2align	4
_RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECs98fvGvYc57G_10rayon_core:
.Lfunc_begin35:
.seh_proc _RINvNvMs2_NtCsfQUUnEvlYZE_5alloc7raw_vecINtB8_11RawVecInnerpE7reserve21do_reserve_and_handleNtNtBa_5alloc6GlobalECs98fvGvYc57G_10rayon_core
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$72, %rsp
	.seh_stackalloc 72
	.seh_endprologue
	addq	%r8, %rdx
	jb	.LBB35_1
	movq	%rcx, %rsi
	movq	(%rcx), %rax
	leaq	(%rax,%rax), %rcx
	cmpq	%rcx, %rdx
	cmovaq	%rdx, %rcx
	cmpq	$5, %rcx
	movl	$4, %edi
	cmovaeq	%rcx, %rdi
	movq	8(%rsi), %r8
	movq	%r9, 32(%rsp)
	leaq	48(%rsp), %rcx
	movq	%rax, %rdx
	movq	%rdi, %r9
	callq	_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCs98fvGvYc57G_10rayon_core
	cmpl	$1, 48(%rsp)
	je	.LBB35_3
	movq	56(%rsp), %rax
	movq	%rax, 8(%rsi)
	movq	%rdi, (%rsi)
	.seh_startepilogue
	addq	$72, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB35_1:
	xorl	%ecx, %ecx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.LBB35_3:
	movq	56(%rsp), %rcx
	movq	64(%rsp), %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.Lfunc_end35:
	.seh_endproc

	.def	_RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB22_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE6resize0uE0EB2X_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB22_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE6resize0uE0EB2X_,unique,36
	.p2align	4
_RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB22_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE6resize0uE0EB2X_:
.Lfunc_begin36:
.seh_proc _RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB22_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE6resize0uE0EB2X_
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	(%rcx), %rsi
	andq	$-8, %rsi
	cmpq	$0, 8(%rsi)
	je	.LBB36_2
	movq	(%rsi), %rcx
	callq	mi_free
.LBB36_2:
	movq	%rsi, %rcx
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rsi
	.seh_endepilogue
	jmp	mi_free
.Lfunc_end36:
	.seh_endproc

	.def	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB12_23default_global_registryE0E0B14_.llvm.17002324475202138184;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB12_23default_global_registryE0E0B14_.llvm.17002324475202138184,unique,37
	.globl	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB12_23default_global_registryE0E0B14_.llvm.17002324475202138184
	.p2align	4
_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB12_23default_global_registryE0E0B14_.llvm.17002324475202138184:
.Lfunc_begin37:
.seh_proc _RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB12_23default_global_registryE0E0B14_.llvm.17002324475202138184
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$280, %rsp
	.seh_stackalloc 280
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	movq	$-2, 144(%rbp)
	movq	(%rcx), %rax
	movq	(%rax), %rbx
	movq	$0, (%rax)
	testq	%rbx, %rbx
	je	.LBB37_28
	movw	$0, 96(%rbp)
	movq	$0, 48(%rbp)
	movq	$0, 8(%rbp)
	movq	$0, 64(%rbp)
	movq	$0, 80(%rbp)
	xorps	%xmm0, %xmm0
	movups	%xmm0, 24(%rbp)
	movq	88(%rbp), %rax
	movq	%rax, -16(%rbp)
	movzwl	96(%rbp), %eax
	movw	%ax, -8(%rbp)
	movl	98(%rbp), %eax
	movl	%eax, -6(%rbp)
	movzwl	102(%rbp), %eax
	movw	%ax, -2(%rbp)
	movq	72(%rbp), %rax
	movq	%rax, -32(%rbp)
	movq	80(%rbp), %rax
	movq	%rax, -24(%rbp)
	movups	56(%rbp), %xmm1
	movaps	%xmm1, -48(%rbp)
	movups	40(%rbp), %xmm1
	movaps	%xmm1, -64(%rbp)
	movaps	%xmm0, -80(%rbp)
	movups	8(%rbp), %xmm0
	movaps	%xmm0, -96(%rbp)
	leaq	104(%rbp), %rcx
	leaq	-96(%rbp), %rdx
	callq	_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_
	movq	104(%rbp), %r15
	movq	112(%rbp), %r14
	cmpq	$-1, %r15
	je	.LBB37_2
	cmpl	$2, %r15d
	jne	.LBB37_22
	movl	%r14d, %esi
	andl	$3, %esi
	leaq	.LJTI37_0(%rip), %rax
	movslq	(%rax,%rsi,4), %rcx
	addq	%rax, %rcx
	jmpq	*%rcx
.LBB37_6:
	movzbl	16(%r14), %eax
	cmpb	$36, %al
	je	.LBB37_11
	jmp	.LBB37_22
.LBB37_2:
	movq	%r14, %rdi
.LBB37_17:
	movq	%rdi, _RNvNtCs98fvGvYc57G_10rayon_core8registry12THE_REGISTRY(%rip)
	movq	$-1, 136(%rbp)
	leaq	_RNvNtCs98fvGvYc57G_10rayon_core8registry12THE_REGISTRY(%rip), %rax
	movq	%rax, 128(%rbp)
	cmpl	$2, (%rbx)
	movq	%rbx, 120(%rbp)
	je	.LBB37_24
	jmp	.LBB37_27
.LBB37_5:
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rax
	movq	%r14, %rcx
	shrq	$32, %rcx
.Ltmp120:
	callq	*8(%rax)
	nop
.Ltmp121:
	jmp	.LBB37_10
.LBB37_9:
	movq	%r14, %rax
	shrq	$32, %rax
.LBB37_10:
	cmpb	$36, %al
	je	.LBB37_11
	jmp	.LBB37_22
.LBB37_7:
	movzbl	31(%r14), %eax
	cmpb	$36, %al
	jne	.LBB37_22
.LBB37_11:
	movl	_tls_index(%rip), %eax
	movq	%gs:88, %rcx
	movq	(%rcx,%rax,8), %rax
	cmpq	$0, _RNvNCNKNvNtCs98fvGvYc57G_10rayon_core8registry19WORKER_THREAD_STATE0s_023___RUST_STD_INTERNAL_VAL@SECREL32(%rax)
	jne	.LBB37_22
	movq	$1, 24(%rbp)
	movb	$1, 96(%rbp)
.Ltmp122:
	leaq	-96(%rbp), %rcx
	leaq	8(%rbp), %rdx
	callq	_RINvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB6_8Registry3newNtB6_12DefaultSpawnEB8_
	nop
.Ltmp123:
	movq	-96(%rbp), %rax
	movq	-88(%rbp), %rdi
	cmpq	$-1, %rax
	je	.LBB37_14
	cmpl	$2, %eax
	jb	.LBB37_22
	movl	%edi, %eax
	andl	$3, %eax
	leal	-2(%rax), %ecx
	cmpl	$2, %ecx
	jb	.LBB37_22
	testq	%rax, %rax
	je	.LBB37_22
	leaq	-1(%rdi), %rcx
.Ltmp124:
	callq	*23(%rdi)
	nop
.Ltmp125:
.LBB37_22:
	movq	%r15, 136(%rbp)
	movq	%r14, 128(%rbp)
	cmpl	$2, (%rbx)
	movq	%rbx, 120(%rbp)
	jne	.LBB37_27
.LBB37_24:
	movq	120(%rbp), %rax
	movq	8(%rax), %rax
	movl	%eax, %ecx
	andl	$3, %ecx
	leal	-2(%rcx), %edx
	cmpl	$2, %edx
	jb	.LBB37_27
	testq	%rcx, %rcx
	je	.LBB37_27
	leaq	-1(%rax), %rcx
.Ltmp126:
	callq	*23(%rax)
	nop
.Ltmp127:
.LBB37_27:
	movq	136(%rbp), %rax
	movq	120(%rbp), %rcx
	movq	%rax, (%rcx)
	movq	128(%rbp), %rax
	movq	%rax, 8(%rcx)
	.seh_startepilogue
	addq	$280, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
.LBB37_14:
	leal	-2(%rsi), %eax
	cmpl	$2, %eax
	jb	.LBB37_17
	testq	%rsi, %rsi
	je	.LBB37_17
	leaq	-1(%r14), %rcx
	callq	*23(%r14)
	jmp	.LBB37_17
.LBB37_28:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.18(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB12_23default_global_registryE0E0B14_.llvm.17002324475202138184@IMGREL
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB12_23default_global_registryE0E0B14_.llvm.17002324475202138184,unique,37
	.seh_endproc
	.def	"?dtor$8@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB12_23default_global_registryE0E0B14_.llvm.17002324475202138184@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$8@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB12_23default_global_registryE0E0B14_.llvm.17002324475202138184@4HA":
.seh_proc "?dtor$8@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB12_23default_global_registryE0E0B14_.llvm.17002324475202138184@4HA"
.LBB37_8:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	128(%rdx), %rbp
	.seh_endprologue
	leaq	104(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtB4_6result6ResultINtNtCsfQUUnEvlYZE_5alloc4sync3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryENtB1z_20ThreadPoolBuildErrorEEB1z_
	nop
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB12_23default_global_registryE0E0B14_.llvm.17002324475202138184,unique,37
	.seh_endproc
	.def	"?dtor$29@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB12_23default_global_registryE0E0B14_.llvm.17002324475202138184@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$29@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB12_23default_global_registryE0E0B14_.llvm.17002324475202138184@4HA":
.seh_proc "?dtor$29@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB12_23default_global_registryE0E0B14_.llvm.17002324475202138184@4HA"
.LBB37_29:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movq	136(%rbp), %rax
	movq	120(%rbp), %rcx
	movq	%rax, (%rcx)
	movq	128(%rbp), %rax
	movq	%rax, 8(%rcx)
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end37:
	.section	.rdata,"dr",associative,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB12_23default_global_registryE0E0B14_.llvm.17002324475202138184,unique,38
	.p2align	2, 0x0
.LJTI37_0:
	.long	.LBB37_6-.LJTI37_0
	.long	.LBB37_7-.LJTI37_0
	.long	.LBB37_5-.LJTI37_0
	.long	.LBB37_9-.LJTI37_0
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB12_23default_global_registryE0E0B14_.llvm.17002324475202138184,unique,37
	.seh_endproc
	.section	.xdata,"dr",associative,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB12_23default_global_registryE0E0B14_.llvm.17002324475202138184,unique,17
	.p2align	2, 0x0
$cppxdata$_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB12_23default_global_registryE0E0B14_.llvm.17002324475202138184:
	.long	429065506
	.long	2
	.long	$stateUnwindMap$_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB12_23default_global_registryE0E0B14_.llvm.17002324475202138184@IMGREL
	.long	0
	.long	0
	.long	4
	.long	$ip2state$_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB12_23default_global_registryE0E0B14_.llvm.17002324475202138184@IMGREL
	.long	272
	.long	0
	.long	1
$stateUnwindMap$_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB12_23default_global_registryE0E0B14_.llvm.17002324475202138184:
	.long	-1
	.long	"?dtor$8@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB12_23default_global_registryE0E0B14_.llvm.17002324475202138184@4HA"@IMGREL
	.long	-1
	.long	"?dtor$29@?0?_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB12_23default_global_registryE0E0B14_.llvm.17002324475202138184@4HA"@IMGREL
$ip2state$_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB12_23default_global_registryE0E0B14_.llvm.17002324475202138184:
	.long	.Lfunc_begin37@IMGREL
	.long	-1
	.long	.Ltmp120@IMGREL
	.long	0
	.long	.Ltmp126@IMGREL
	.long	1
	.long	.Ltmp127@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB12_23default_global_registryE0E0B14_.llvm.17002324475202138184,unique,37

	.def	_RNSNvNCNKNvNtCs98fvGvYc57G_10rayon_core8registry19WORKER_THREAD_STATE0s_023___RUST_STD_INTERNAL_VAL3tls;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvNCNKNvNtCs98fvGvYc57G_10rayon_core8registry19WORKER_THREAD_STATE0s_023___RUST_STD_INTERNAL_VAL3tls,unique,39
	.globl	_RNSNvNCNKNvNtCs98fvGvYc57G_10rayon_core8registry19WORKER_THREAD_STATE0s_023___RUST_STD_INTERNAL_VAL3tls
	.p2align	4
_RNSNvNCNKNvNtCs98fvGvYc57G_10rayon_core8registry19WORKER_THREAD_STATE0s_023___RUST_STD_INTERNAL_VAL3tls:
.Lfunc_begin38:
	movl	_tls_index(%rip), %eax
	movq	%gs:88, %rcx
	movq	(%rcx,%rax,8), %rax
	leaq	_RNvNCNKNvNtCs98fvGvYc57G_10rayon_core8registry19WORKER_THREAD_STATE0s_023___RUST_STD_INTERNAL_VAL@SECREL32(%rax), %rax
	retq
.Lfunc_end38:

	.def	_RNSNvNCNKNvNvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtBf_8Registry14in_worker_cold10LOCK_LATCH0s_023___RUST_STD_INTERNAL_VAL3tls;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvNCNKNvNvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtBf_8Registry14in_worker_cold10LOCK_LATCH0s_023___RUST_STD_INTERNAL_VAL3tls,unique,40
	.globl	_RNSNvNCNKNvNvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtBf_8Registry14in_worker_cold10LOCK_LATCH0s_023___RUST_STD_INTERNAL_VAL3tls
	.p2align	4
_RNSNvNCNKNvNvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtBf_8Registry14in_worker_cold10LOCK_LATCH0s_023___RUST_STD_INTERNAL_VAL3tls:
.Lfunc_begin39:
	movl	_tls_index(%rip), %eax
	movq	%gs:88, %rcx
	movq	(%rcx,%rax,8), %rax
	leaq	_RNvNCNKNvNvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtBd_8Registry14in_worker_cold10LOCK_LATCH0s_023___RUST_STD_INTERNAL_VAL@SECREL32(%rax), %rax
	retq
.Lfunc_end39:

	.def	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB17_23default_global_registryE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB19_.llvm.17002324475202138184;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB17_23default_global_registryE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB19_.llvm.17002324475202138184,unique,41
	.globl	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB17_23default_global_registryE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB19_.llvm.17002324475202138184
	.p2align	4
_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB17_23default_global_registryE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB19_.llvm.17002324475202138184:
.Lfunc_begin40:
.seh_proc _RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB17_23default_global_registryE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB19_.llvm.17002324475202138184
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rax
	movq	%rax, 32(%rsp)
	leaq	32(%rsp), %rcx
	callq	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB12_23default_global_registryE0E0B14_.llvm.17002324475202138184
	nop
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end40:
	.seh_endproc

	.def	_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_,unique,42
	.p2align	4
_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_:
.Lfunc_begin41:
.seh_proc _RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$376, %rsp
	.seh_stackalloc 376
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	movq	$-2, 232(%rbp)
	movq	96(%rcx), %rax
	movq	%rax, 128(%rbp)
	movups	80(%rcx), %xmm0
	movaps	%xmm0, 112(%rbp)
	movups	16(%rcx), %xmm0
	movups	32(%rcx), %xmm1
	movups	48(%rcx), %xmm2
	movups	64(%rcx), %xmm3
	movaps	%xmm3, 96(%rbp)
	movaps	%xmm2, 80(%rbp)
	movaps	%xmm1, 64(%rbp)
	movaps	%xmm0, 48(%rbp)
	movups	104(%rcx), %xmm0
	movups	120(%rcx), %xmm1
	movups	%xmm0, 136(%rbp)
	movups	%xmm1, 152(%rbp)
	movq	%rcx, 200(%rbp)
	movups	(%rcx), %xmm0
	movaps	%xmm0, -96(%rbp)
	movaps	144(%rbp), %xmm0
	movaps	%xmm0, 16(%rbp)
	movaps	48(%rbp), %xmm0
	movaps	64(%rbp), %xmm1
	movaps	80(%rbp), %xmm2
	movaps	96(%rbp), %xmm3
	movaps	%xmm0, -80(%rbp)
	movaps	%xmm1, -64(%rbp)
	movaps	%xmm2, -48(%rbp)
	movaps	%xmm3, -32(%rbp)
	movaps	112(%rbp), %xmm0
	movaps	%xmm0, -16(%rbp)
	movaps	128(%rbp), %xmm0
	movaps	%xmm0, (%rbp)
	movq	160(%rbp), %rax
	movq	%rax, 32(%rbp)
	leaq	8(%rbp), %rcx
	movb	$1, 231(%rbp)
.Ltmp128:
	callq	_RINvNtNtCse0R8cuyqEa_3std3sys9backtrace28___rust_begin_short_backtraceNCNCNCINvNtNtB6_6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB22_12DefaultSpawnNtB22_11ThreadSpawn5spawn0uEs_000uEB24_
	nop
.Ltmp129:
	movb	$0, 231(%rbp)
.Ltmp130:
	leaq	-96(%rbp), %rcx
	callq	_RINvNtNtCse0R8cuyqEa_3std3sys9backtrace28___rust_begin_short_backtraceNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1e_12DefaultSpawnNtB1e_11ThreadSpawn5spawn0uEB1g_
	nop
.Ltmp131:
	xorl	%esi, %esi
.LBB41_9:
	movq	200(%rbp), %rax
	movq	136(%rax), %rbx
	addq	$136, %rax
	movq	%rax, 200(%rbp)
	cmpq	$0, 24(%rbx)
	je	.LBB41_15
	movq	32(%rbx), %rax
	movq	%rax, 192(%rbp)
	testq	%rax, %rax
	je	.LBB41_15
	movq	%rdi, 216(%rbp)
	movq	%rsi, 208(%rbp)
	movq	%rbx, 176(%rbp)
	movq	40(%rbx), %rax
	movq	%rax, 184(%rbp)
	movq	(%rax), %rax
	testq	%rax, %rax
	je	.LBB41_13
.Ltmp132:
	movq	192(%rbp), %rcx
	callq	*%rax
	nop
.Ltmp133:
.LBB41_13:
	movq	184(%rbp), %rax
	cmpq	$0, 8(%rax)
	movq	208(%rbp), %rsi
	movq	216(%rbp), %rdi
	movq	176(%rbp), %rbx
	je	.LBB41_15
	movq	192(%rbp), %rcx
	callq	mi_free
.LBB41_15:
	movq	$1, 24(%rbx)
	movq	%rsi, 32(%rbx)
	movq	%rdi, 40(%rbx)
	movq	%rbx, 168(%rbp)
	lock		decq	(%rbx)
	jne	.LBB41_17
	#MEMBARRIER
	movb	$0, 230(%rbp)
.Ltmp134:
	leaq	168(%rbp), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEE9drop_slowBN_
	nop
.Ltmp135:
.LBB41_17:
	.seh_startepilogue
	addq	$376, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB41_8:
$ehgcr_41_8:
	movq	208(%rbp), %rsi
	movq	216(%rbp), %rdi
	jmp	.LBB41_9
	.seh_handlerdata
	.long	$cppxdata$_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@IMGREL
	.section	.text,"xr",one_only,_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_,unique,42
	.seh_endproc
	.def	"?dtor$3@?0?_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$3@?0?_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@4HA":
.seh_proc "?dtor$3@?0?_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@4HA"
.LBB41_3:
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpb	$0, 231(%rbp)
	je	.LBB41_4
	leaq	-96(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtBJ_12DefaultSpawnNtBJ_11ThreadSpawn5spawn0EBL_
	nop
.LBB41_4:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_,unique,42
	.seh_endproc
	.def	"?catch$6@?0?_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?catch$6@?0?_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@4HA":
.seh_proc "?catch$6@?0?_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@4HA"
	.seh_handler __CxxFrameHandler3, @unwind, @except
.LBB41_6:
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movq	240(%rbp), %rcx
	callq	_RNvNvNtCse0R8cuyqEa_3std9panicking12catch_unwind7cleanup
	movq	%rax, 208(%rbp)
	movq	%rdx, 216(%rbp)
	leaq	.LBB41_8(%rip), %rax
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.long	$cppxdata$_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@IMGREL
	.section	.text,"xr",one_only,_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_,unique,42
	.seh_endproc
	.def	"?catch$7@?0?_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?catch$7@?0?_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@4HA":
.seh_proc "?catch$7@?0?_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@4HA"
	.seh_handler __CxxFrameHandler3, @unwind, @except
.LBB41_7:
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	xorl	%ecx, %ecx
	callq	_RNvNvNtCse0R8cuyqEa_3std9panicking12catch_unwind7cleanup
	movq	%rax, 208(%rbp)
	movq	%rdx, 216(%rbp)
	leaq	.LBB41_8(%rip), %rax
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.long	$cppxdata$_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@IMGREL
	.section	.text,"xr",one_only,_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_,unique,42
	.seh_endproc
	.def	"?dtor$18@?0?_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$18@?0?_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@4HA":
.seh_proc "?dtor$18@?0?_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@4HA"
.LBB41_18:
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movq	184(%rbp), %rax
	cmpq	$0, 8(%rax)
	je	.LBB41_20
	movq	192(%rbp), %rcx
	callq	mi_free
.LBB41_20:
	movq	176(%rbp), %rcx
	movq	$1, 24(%rcx)
	movq	208(%rbp), %rax
	movq	%rax, 32(%rcx)
	movq	216(%rbp), %rax
	movq	%rax, 40(%rcx)
	movb	$1, 230(%rbp)
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_,unique,42
	.seh_endproc
	.def	"?dtor$21@?0?_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$21@?0?_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@4HA":
.seh_proc "?dtor$21@?0?_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@4HA"
.LBB41_21:
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpb	$0, 230(%rbp)
	je	.LBB41_24
	movq	200(%rbp), %rax
	movq	(%rax), %rax
	lock		decq	(%rax)
	jne	.LBB41_24
	#MEMBARRIER
	movq	200(%rbp), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEE9drop_slowBN_
	nop
.LBB41_24:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end41:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_,unique,42
	.seh_endproc
	.section	.xdata,"dr",associative,_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_,unique,18
	.p2align	2, 0x0
$cppxdata$_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_:
	.long	429065506
	.long	5
	.long	$stateUnwindMap$_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@IMGREL
	.long	1
	.long	$tryMap$_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@IMGREL
	.long	7
	.long	$ip2state$_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@IMGREL
	.long	360
	.long	0
	.long	1
$stateUnwindMap$_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_:
	.long	-1
	.long	0
	.long	0
	.long	"?dtor$3@?0?_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@4HA"@IMGREL
	.long	-1
	.long	0
	.long	-1
	.long	"?dtor$21@?0?_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@4HA"@IMGREL
	.long	3
	.long	"?dtor$18@?0?_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@4HA"@IMGREL
$tryMap$_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_:
	.long	0
	.long	1
	.long	2
	.long	2
	.long	$handlerMap$0$_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@IMGREL
$handlerMap$0$_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_:
	.long	8
	.long	_RNvCs1njKG4L9aB3_7___rustc22___rust_panic_type_info@IMGREL
	.long	368
	.long	"?catch$6@?0?_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@4HA"@IMGREL
	.long	88
	.long	64
	.long	0
	.long	0
	.long	"?catch$7@?0?_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@4HA"@IMGREL
	.long	88
$ip2state$_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_:
	.long	.Lfunc_begin41@IMGREL
	.long	-1
	.long	.Ltmp128@IMGREL
	.long	1
	.long	.Ltmp132@IMGREL
	.long	4
	.long	.Ltmp134@IMGREL
	.long	3
	.long	.Ltmp135@IMGREL
	.long	-1
	.long	"?catch$6@?0?_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@4HA"@IMGREL
	.long	2
	.long	"?catch$7@?0?_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_@4HA"@IMGREL
	.long	2
	.section	.text,"xr",one_only,_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_,unique,42

	.def	_RNvCs98fvGvYc57G_10rayon_core19current_num_threads;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvCs98fvGvYc57G_10rayon_core19current_num_threads,unique,43
	.globl	_RNvCs98fvGvYc57G_10rayon_core19current_num_threads
	.p2align	4
_RNvCs98fvGvYc57G_10rayon_core19current_num_threads:
.Lfunc_begin42:
.seh_proc _RNvCs98fvGvYc57G_10rayon_core19current_num_threads
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movl	_tls_index(%rip), %eax
	movq	%gs:88, %rcx
	movq	(%rcx,%rax,8), %rax
	movq	_RNvNCNKNvNtCs98fvGvYc57G_10rayon_core8registry19WORKER_THREAD_STATE0s_023___RUST_STD_INTERNAL_VAL@SECREL32(%rax), %rax
	testq	%rax, %rax
	je	.LBB42_1
	addq	$272, %rax
	movq	(%rax), %rax
	movq	520(%rax), %rax
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.LBB42_1:
	callq	_RNvNtCs98fvGvYc57G_10rayon_core8registry15global_registry
	movq	(%rax), %rax
	movq	520(%rax), %rax
	.seh_startepilogue
	addq	$40, %rsp
	.seh_endepilogue
	retq
.Lfunc_end42:
	.seh_endproc

	.def	_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep16wake_any_threads;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep16wake_any_threads,unique,44
	.globl	_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep16wake_any_threads
	.p2align	4
_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep16wake_any_threads:
.Lfunc_begin43:
.seh_proc _RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep16wake_any_threads
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
	testl	%edx, %edx
	je	.LBB43_6
	movq	%rcx, %rdi
	movq	16(%rcx), %r14
	testq	%r14, %r14
	je	.LBB43_6
	movl	%edx, %esi
	xorl	%ebx, %ebx
	jmp	.LBB43_3
	.p2align	4
.LBB43_4:
	incq	%rbx
	cmpq	%rbx, %r14
	je	.LBB43_6
.LBB43_3:
	movq	%rdi, %rcx
	movq	%rbx, %rdx
	callq	_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep20wake_specific_thread.llvm.17002324475202138184
	testb	%al, %al
	je	.LBB43_4
	decl	%esi
	jne	.LBB43_4
.LBB43_6:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	.seh_endepilogue
	retq
.Lfunc_end43:
	.seh_endproc

	.def	_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep20wake_specific_thread.llvm.17002324475202138184;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep20wake_specific_thread.llvm.17002324475202138184,unique,45
	.globl	_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep20wake_specific_thread.llvm.17002324475202138184
	.p2align	4
_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep20wake_specific_thread.llvm.17002324475202138184:
.Lfunc_begin44:
.seh_proc _RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep20wake_specific_thread.llvm.17002324475202138184
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$72, %rsp
	.seh_stackalloc 72
	leaq	64(%rsp), %rbp
	.seh_setframe %rbp, 64
	.seh_endprologue
	movq	$-2, (%rbp)
	movq	16(%rcx), %rax
	cmpq	%rax, %rdx
	jae	.LBB44_9
	movq	%rcx, %rbx
	movq	8(%rcx), %rdi
	shlq	$7, %rdx
	leaq	(%rdi,%rdx), %rsi
	addq	$4, %rsi
	movb	$1, %cl
	xorl	%eax, %eax
	lock		cmpxchgb	%cl, 4(%rdi,%rdx)
	jne	.LBB44_2
.LBB44_3:
	addq	%rdx, %rdi
	movq	_RNvNtNtCse0R8cuyqEa_3std9panicking11panic_count18GLOBAL_PANIC_COUNT(%rip), %rax
	shlq	%rax
	testq	%rax, %rax
	jne	.LBB44_5
	xorl	%r15d, %r15d
	movzbl	5(%rdi), %eax
	testb	%al, %al
	jne	.LBB44_7
.LBB44_10:
	movzbl	6(%rdi), %r14d
	testb	%r14b, %r14b
	je	.LBB44_12
	movb	$0, 6(%rdi)
	lock		incl	(%rdi)
	movq	%rdi, %rcx
	callq	*__imp_WakeByAddressSingle(%rip)
	lock		decq	24(%rbx)
.LBB44_12:
	testb	%r15b, %r15b
	jne	.LBB44_16
	movq	_RNvNtNtCse0R8cuyqEa_3std9panicking11panic_count18GLOBAL_PANIC_COUNT(%rip), %rax
	shlq	%rax
	testq	%rax, %rax
	jne	.LBB44_14
.LBB44_16:
	xorl	%eax, %eax
	xchgb	%al, (%rsi)
	cmpb	$2, %al
	je	.LBB44_17
.LBB44_18:
	movl	%r14d, %eax
	.seh_startepilogue
	addq	$72, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
.LBB44_2:
	movq	%rsi, %rcx
	movq	%rdx, %r14
	callq	_RNvMNtNtNtNtCse0R8cuyqEa_3std3sys4sync5mutex5futexNtB2_5Mutex14lock_contended
	movq	%r14, %rdx
	jmp	.LBB44_3
.LBB44_5:
	callq	_RNvNtNtCse0R8cuyqEa_3std9panicking11panic_count17is_zero_slow_path
	movl	%eax, %r15d
	xorb	$1, %r15b
	movzbl	5(%rdi), %eax
	testb	%al, %al
	je	.LBB44_10
.LBB44_7:
	movq	%rsi, -16(%rbp)
	movb	%r15b, -8(%rbp)
.Ltmp136:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.31.llvm.17002324475202138184(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.28.llvm.17002324475202138184(%rip), %rcx
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.27.llvm.17002324475202138184(%rip), %r9
	leaq	-16(%rbp), %r8
	movl	$43, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core6result13unwrap_failed
	nop
.Ltmp137:
	ud2
.LBB44_17:
	movq	%rsi, %rcx
	callq	*__imp_WakeByAddressSingle(%rip)
	jmp	.LBB44_18
.LBB44_14:
	callq	_RNvNtNtCse0R8cuyqEa_3std9panicking11panic_count17is_zero_slow_path
	testb	%al, %al
	jne	.LBB44_16
	movb	$1, 5(%rdi)
	jmp	.LBB44_16
.LBB44_9:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.30.llvm.17002324475202138184(%rip), %r8
	movq	%rdx, %rcx
	movq	%rax, %rdx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep20wake_specific_thread.llvm.17002324475202138184@IMGREL
	.section	.text,"xr",one_only,_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep20wake_specific_thread.llvm.17002324475202138184,unique,45
	.seh_endproc
	.def	"?dtor$19@?0?_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep20wake_specific_thread.llvm.17002324475202138184@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$19@?0?_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep20wake_specific_thread.llvm.17002324475202138184@4HA":
.seh_proc "?dtor$19@?0?_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep20wake_specific_thread.llvm.17002324475202138184@4HA"
.LBB44_19:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	64(%rdx), %rbp
	.seh_endprologue
	leaq	-16(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCse0R8cuyqEa_3std4sync6poison11PoisonErrorINtNtBE_5mutex10MutexGuardbEEECs98fvGvYc57G_10rayon_core.llvm.17002324475202138184
	nop
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end44:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep20wake_specific_thread.llvm.17002324475202138184,unique,45
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep20wake_specific_thread.llvm.17002324475202138184,unique,19
	.p2align	2, 0x0
$cppxdata$_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep20wake_specific_thread.llvm.17002324475202138184:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep20wake_specific_thread.llvm.17002324475202138184@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep20wake_specific_thread.llvm.17002324475202138184@IMGREL
	.long	64
	.long	0
	.long	1
$stateUnwindMap$_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep20wake_specific_thread.llvm.17002324475202138184:
	.long	-1
	.long	"?dtor$19@?0?_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep20wake_specific_thread.llvm.17002324475202138184@4HA"@IMGREL
$ip2state$_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep20wake_specific_thread.llvm.17002324475202138184:
	.long	.Lfunc_begin44@IMGREL
	.long	-1
	.long	.Ltmp136@IMGREL
	.long	0
	.long	.Ltmp137@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep20wake_specific_thread.llvm.17002324475202138184,unique,45

	.def	_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run,unique,46
	.globl	_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run
	.p2align	4
_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run:
.Lfunc_begin45:
.seh_proc _RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$584, %rsp
	.seh_stackalloc 584
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	andq	$-128, %rsp
	movq	%rsp, %rbx
	movq	%rbp, 552(%rbx)
	movq	$-2, 432(%rbp)
	movq	%rcx, %rdx
	leaq	128(%rbx), %rsi
	movq	%rsi, %rcx
	callq	_RNvXs6_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThreadINtNtCs8xEFJqa6dYS_4core7convert4FromNtB5_13ThreadBuilderE4from
	movl	_tls_index(%rip), %eax
	movq	%gs:88, %rcx
	movq	(%rcx,%rax,8), %rax
	cmpq	$0, _RNvNCNKNvNtCs98fvGvYc57G_10rayon_core8registry19WORKER_THREAD_STATE0s_023___RUST_STD_INTERNAL_VAL@SECREL32(%rax)
	jne	.LBB45_1
	leaq	_RNvNCNKNvNtCs98fvGvYc57G_10rayon_core8registry19WORKER_THREAD_STATE0s_023___RUST_STD_INTERNAL_VAL@SECREL32(%rax), %rax
	movq	%rsi, (%rax)
	movq	384(%rbx), %r15
	movq	400(%rbx), %rsi
	movq	520(%rsi), %rdx
	cmpq	%rdx, %r15
	jae	.LBB45_9
	leaq	(%r15,%r15,4), %rcx
	shlq	$3, %rcx
	addq	512(%rsi), %rcx
.Ltmp142:
	callq	_RNvXs4_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatchNtB5_5Latch3set
	nop
.Ltmp143:
	movq	432(%rsi), %rcx
	testq	%rcx, %rcx
	movq	%rsi, 112(%rbx)
	je	.LBB45_14
	movq	440(%rsi), %rax
	movq	40(%rax), %rax
	movb	$1, 95(%rbx)
.Ltmp144:
	movq	%r15, 104(%rbx)
	movq	%r15, %rdx
	callq	*%rax
	nop
.Ltmp145:
	movq	104(%rbx), %r15
.LBB45_14:
	movq	384(%rbx), %rsi
	movq	400(%rbx), %rdi
	movq	520(%rdi), %rdx
	cmpq	%rdx, %rsi
	jae	.LBB45_25
	movq	512(%rdi), %rax
	leaq	(%rsi,%rsi,4), %r14
	movq	16(%rax,%r14,8), %rcx
	cmpq	$3, %rcx
	jne	.LBB45_16
.LBB45_17:
	movq	520(%rdi), %rdx
	cmpq	%rdx, %rsi
	jae	.LBB45_26
	movq	512(%rdi), %rax
	leaq	(%rax,%r14,8), %rcx
	addq	$8, %rcx
	movb	$1, 95(%rbx)
.Ltmp156:
	callq	_RNvXs4_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatchNtB5_5Latch3set
	nop
.Ltmp157:
	movq	112(%rbx), %rax
	movq	448(%rax), %rcx
	testq	%rcx, %rcx
	je	.LBB45_31
	movq	456(%rax), %rax
	movq	40(%rax), %rax
	movb	$0, 95(%rbx)
.Ltmp158:
	movq	%r15, %rdx
	callq	*%rax
	nop
.Ltmp159:
.LBB45_31:
	leaq	128(%rbx), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry12WorkerThreadEBF_
	nop
	.seh_startepilogue
	leaq	456(%rbp), %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
.LBB45_1:
.Ltmp138:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.20(%rip), %rcx
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.21(%rip), %r8
	movl	$35, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking5panic
	nop
.Ltmp139:
	jmp	.LBB45_2
.LBB45_16:
	leaq	(%rax,%r14,8), %rdx
	addq	$16, %rdx
	movb	$1, 95(%rbx)
.Ltmp152:
	leaq	128(%rbx), %rcx
	callq	_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread15wait_until_cold
	nop
.Ltmp153:
	jmp	.LBB45_17
.LBB45_9:
.Ltmp140:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.53(%rip), %r8
	movq	%r15, %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	nop
.Ltmp141:
	jmp	.LBB45_2
.LBB45_25:
	movb	$1, 95(%rbx)
.Ltmp150:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.47(%rip), %r8
	movq	%rsi, %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	nop
.Ltmp151:
	jmp	.LBB45_2
.LBB45_26:
	movb	$1, 95(%rbx)
.Ltmp154:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.48(%rip), %r8
	movq	%rsi, %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	nop
.Ltmp155:
.LBB45_2:
	ud2
.LBB45_29:
$ehgcr_45_29:
	movq	112(%rbx), %rax
	movq	416(%rax), %rcx
	testq	%rcx, %rcx
	je	.LBB45_32
	movq	112(%rbx), %rax
	movq	424(%rax), %rax
.Ltmp160:
	movq	104(%rbx), %rdx
	movq	96(%rbx), %r8
	callq	*40(%rax)
	nop
.Ltmp161:
	jmp	.LBB45_31
.LBB45_32:
.Ltmp162:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.54.llvm.17002324475202138184(%rip), %rcx
	movl	$87, %edx
	callq	_RNvNtNtCse0R8cuyqEa_3std2io5stdio7__eprint
	nop
.Ltmp163:
	movl	$7, %ecx
	#APP

	int	$41

	#NO_APP
	ud2
.LBB45_12:
$ehgcr_45_12:
	movq	112(%rbx), %rax
	movq	416(%rax), %rcx
	testq	%rcx, %rcx
	je	.LBB45_21
	movq	112(%rbx), %rax
	movq	424(%rax), %rax
.Ltmp146:
	movq	96(%rbx), %rdx
	movq	120(%rbx), %r8
	callq	*40(%rax)
	nop
.Ltmp147:
	movq	104(%rbx), %r15
	jmp	.LBB45_14
.LBB45_21:
.Ltmp148:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.54.llvm.17002324475202138184(%rip), %rcx
	movl	$87, %edx
	callq	_RNvNtNtCse0R8cuyqEa_3std2io5stdio7__eprint
	nop
.Ltmp149:
	movl	$7, %ecx
	#APP

	int	$41

	#NO_APP
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@IMGREL
	.section	.text,"xr",one_only,_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run,unique,46
	.seh_endproc
	.def	"?dtor$3@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$3@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA":
.seh_proc "?dtor$3@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA"
.LBB45_3:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	128(%rdx), %rbp
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	leaq	128(%rbx), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry12WorkerThreadEBF_
	nop
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run,unique,46
	.seh_endproc
	.def	"?catch$10@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?catch$10@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA":
.seh_proc "?catch$10@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA"
	.seh_handler __CxxFrameHandler3, @unwind, @except
.LBB45_10:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	128(%rdx), %rbp
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	movq	440(%rbp), %rcx
	callq	_RNvNvNtCse0R8cuyqEa_3std9panicking12catch_unwind7cleanup
	movq	%rax, 96(%rbx)
	movq	%rdx, 120(%rbx)
	leaq	.LBB45_12(%rip), %rax
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.long	$cppxdata$_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@IMGREL
	.section	.text,"xr",one_only,_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run,unique,46
	.seh_endproc
	.def	"?catch$11@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?catch$11@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA":
.seh_proc "?catch$11@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA"
	.seh_handler __CxxFrameHandler3, @unwind, @except
.LBB45_11:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	128(%rdx), %rbp
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	xorl	%ecx, %ecx
	callq	_RNvNvNtCse0R8cuyqEa_3std9panicking12catch_unwind7cleanup
	movq	%rax, 96(%rbx)
	movq	%rdx, 120(%rbx)
	leaq	.LBB45_12(%rip), %rax
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.long	$cppxdata$_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@IMGREL
	.section	.text,"xr",one_only,_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run,unique,46
	.seh_endproc
	.def	"?dtor$23@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$23@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA":
.seh_proc "?dtor$23@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA"
.LBB45_23:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	128(%rdx), %rbp
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	movb	$1, 95(%rbx)
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.54.llvm.17002324475202138184(%rip), %rcx
	movl	$87, %edx
	callq	_RNvNtNtCse0R8cuyqEa_3std2io5stdio7__eprint
	movl	$7, %ecx
	#APP

	int	$41

	#NO_APP
	ud2
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run,unique,46
	.seh_endproc
	.def	"?dtor$24@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$24@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA":
.seh_proc "?dtor$24@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA"
.LBB45_24:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	128(%rdx), %rbp
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	movb	$1, 95(%rbx)
	movq	96(%rbx), %rcx
	movq	120(%rbx), %rdx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECs98fvGvYc57G_10rayon_core
	movb	$1, 95(%rbx)
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run,unique,46
	.seh_endproc
	.def	"?catch$27@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?catch$27@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA":
.seh_proc "?catch$27@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA"
	.seh_handler __CxxFrameHandler3, @unwind, @except
.LBB45_27:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	128(%rdx), %rbp
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	movq	448(%rbp), %rcx
	callq	_RNvNvNtCse0R8cuyqEa_3std9panicking12catch_unwind7cleanup
	movq	%rax, 104(%rbx)
	movq	%rdx, 96(%rbx)
	leaq	.LBB45_29(%rip), %rax
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.long	$cppxdata$_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@IMGREL
	.section	.text,"xr",one_only,_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run,unique,46
	.seh_endproc
	.def	"?catch$28@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?catch$28@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA":
.seh_proc "?catch$28@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA"
	.seh_handler __CxxFrameHandler3, @unwind, @except
.LBB45_28:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	128(%rdx), %rbp
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	xorl	%ecx, %ecx
	callq	_RNvNvNtCse0R8cuyqEa_3std9panicking12catch_unwind7cleanup
	movq	%rax, 104(%rbx)
	movq	%rdx, 96(%rbx)
	leaq	.LBB45_29(%rip), %rax
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.long	$cppxdata$_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@IMGREL
	.section	.text,"xr",one_only,_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run,unique,46
	.seh_endproc
	.def	"?dtor$34@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$34@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA":
.seh_proc "?dtor$34@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA"
.LBB45_34:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	128(%rdx), %rbp
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	movb	$0, 95(%rbx)
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.54.llvm.17002324475202138184(%rip), %rcx
	movl	$87, %edx
	callq	_RNvNtNtCse0R8cuyqEa_3std2io5stdio7__eprint
	movl	$7, %ecx
	#APP

	int	$41

	#NO_APP
	ud2
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run,unique,46
	.seh_endproc
	.def	"?dtor$35@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$35@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA":
.seh_proc "?dtor$35@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA"
.LBB45_35:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	128(%rdx), %rbp
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	movb	$0, 95(%rbx)
	movq	104(%rbx), %rcx
	movq	96(%rbx), %rdx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc5boxed3BoxDNtNtB4_3any3AnyNtNtB4_6marker4SendEL_EECs98fvGvYc57G_10rayon_core
	movb	$0, 95(%rbx)
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run,unique,46
	.seh_endproc
	.def	"?dtor$36@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$36@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA":
.seh_proc "?dtor$36@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA"
.LBB45_36:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	128(%rdx), %rbp
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	cmpb	$0, 95(%rbx)
	jne	.LBB45_38
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
.LBB45_38:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.54.llvm.17002324475202138184(%rip), %rcx
	movl	$87, %edx
	callq	_RNvNtNtCse0R8cuyqEa_3std2io5stdio7__eprint
	movl	$7, %ecx
	#APP

	int	$41

	#NO_APP
	ud2
.Lfunc_end45:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run,unique,46
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run,unique,20
	.p2align	2, 0x0
$cppxdata$_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run:
	.long	429065506
	.long	10
	.long	$stateUnwindMap$_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@IMGREL
	.long	2
	.long	$tryMap$_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@IMGREL
	.long	19
	.long	$ip2state$_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@IMGREL
	.long	560
	.long	0
	.long	1
$stateUnwindMap$_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run:
	.long	-1
	.long	"?dtor$3@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA"@IMGREL
	.long	0
	.long	"?dtor$36@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA"@IMGREL
	.long	1
	.long	"?dtor$35@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA"@IMGREL
	.long	1
	.long	0
	.long	1
	.long	0
	.long	1
	.long	"?dtor$24@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA"@IMGREL
	.long	1
	.long	0
	.long	1
	.long	0
	.long	-1
	.long	"?dtor$23@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA"@IMGREL
	.long	-1
	.long	"?dtor$34@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA"@IMGREL
$tryMap$_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run:
	.long	3
	.long	3
	.long	4
	.long	2
	.long	$handlerMap$0$_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@IMGREL
	.long	6
	.long	6
	.long	7
	.long	2
	.long	$handlerMap$1$_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@IMGREL
$handlerMap$0$_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run:
	.long	8
	.long	_RNvCs1njKG4L9aB3_7___rustc22___rust_panic_type_info@IMGREL
	.long	576
	.long	"?catch$27@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA"@IMGREL
	.long	104
	.long	64
	.long	0
	.long	0
	.long	"?catch$28@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA"@IMGREL
	.long	104
$handlerMap$1$_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run:
	.long	8
	.long	_RNvCs1njKG4L9aB3_7___rustc22___rust_panic_type_info@IMGREL
	.long	568
	.long	"?catch$10@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA"@IMGREL
	.long	104
	.long	64
	.long	0
	.long	0
	.long	"?catch$11@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA"@IMGREL
	.long	104
$ip2state$_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run:
	.long	.Lfunc_begin45@IMGREL
	.long	-1
	.long	.Ltmp142@IMGREL
	.long	0
	.long	.Ltmp144@IMGREL
	.long	6
	.long	.Ltmp156@IMGREL
	.long	1
	.long	.Ltmp158@IMGREL
	.long	3
	.long	.Ltmp159@IMGREL
	.long	-1
	.long	.Ltmp138@IMGREL
	.long	0
	.long	.Ltmp152@IMGREL
	.long	1
	.long	.Ltmp140@IMGREL
	.long	0
	.long	.Ltmp150@IMGREL
	.long	1
	.long	.Ltmp160@IMGREL
	.long	9
	.long	.Ltmp162@IMGREL
	.long	2
	.long	.Ltmp146@IMGREL
	.long	8
	.long	.Ltmp148@IMGREL
	.long	5
	.long	.Ltmp149@IMGREL
	.long	-1
	.long	"?catch$10@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA"@IMGREL
	.long	7
	.long	"?catch$11@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA"@IMGREL
	.long	7
	.long	"?catch$27@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA"@IMGREL
	.long	4
	.long	"?catch$28@?0?_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run@4HA"@IMGREL
	.long	4
	.section	.text,"xr",one_only,_RNvMNtCs98fvGvYc57G_10rayon_core8registryNtB2_13ThreadBuilder3run,unique,46

	.def	_RNvMs3_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatch14wait_and_reset;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs3_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatch14wait_and_reset,unique,47
	.globl	_RNvMs3_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatch14wait_and_reset
	.p2align	4
_RNvMs3_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatch14wait_and_reset:
.Lfunc_begin46:
.seh_proc _RNvMs3_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatch14wait_and_reset
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
	subq	$72, %rsp
	.seh_stackalloc 72
	leaq	64(%rsp), %rbp
	.seh_setframe %rbp, 64
	.seh_endprologue
	movq	$-2, (%rbp)
	movq	%rcx, %rdi
	leaq	4(%rcx), %rsi
	movb	$1, %cl
	xorl	%eax, %eax
	lock		cmpxchgb	%cl, 4(%rdi)
	jne	.LBB46_1
	movq	_RNvNtNtCse0R8cuyqEa_3std9panicking11panic_count18GLOBAL_PANIC_COUNT(%rip), %rax
	shlq	%rax
	testq	%rax, %rax
	jne	.LBB46_4
.LBB46_3:
	xorl	%eax, %eax
	movzbl	5(%rdi), %ecx
	testb	%cl, %cl
	jne	.LBB46_6
.LBB46_8:
	movl	%eax, -4(%rbp)
	leaq	-24(%rbp), %r14
	movq	__imp_WaitOnAddress(%rip), %r12
	movb	$1, %r13b
	movq	__imp_GetLastError(%rip), %r15
	.p2align	4
.LBB46_9:
	cmpb	$0, 6(%rdi)
	jne	.LBB46_18
	movl	(%rdi), %ebx
	xorl	%eax, %eax
	xchgb	%al, 4(%rdi)
	cmpb	$2, %al
	je	.LBB46_11
.LBB46_12:
	movl	%ebx, -24(%rbp)
	movl	$4, %r8d
	movq	%rdi, %rcx
	movq	%r14, %rdx
	movl	$-1, %r9d
	callq	*%r12
	cmpl	$1, %eax
	jne	.LBB46_13
	xorl	%eax, %eax
	lock		cmpxchgb	%r13b, (%rsi)
	jne	.LBB46_15
.LBB46_16:
	movzbl	5(%rdi), %eax
	testb	%al, %al
	je	.LBB46_9
	jmp	.LBB46_17
	.p2align	4
.LBB46_13:
	callq	*%r15
	xorl	%eax, %eax
	lock		cmpxchgb	%r13b, (%rsi)
	je	.LBB46_16
.LBB46_15:
	movq	%rsi, %rcx
	callq	_RNvMNtNtNtNtCse0R8cuyqEa_3std3sys4sync5mutex5futexNtB2_5Mutex14lock_contended
	movzbl	5(%rdi), %eax
	testb	%al, %al
	je	.LBB46_9
	jmp	.LBB46_17
.LBB46_11:
	movq	%rsi, %rcx
	callq	*__imp_WakeByAddressSingle(%rip)
	jmp	.LBB46_12
.LBB46_18:
	movb	$0, 6(%rdi)
	cmpb	$0, -4(%rbp)
	jne	.LBB46_22
	movq	_RNvNtNtCse0R8cuyqEa_3std9panicking11panic_count18GLOBAL_PANIC_COUNT(%rip), %rax
	shlq	%rax
	testq	%rax, %rax
	jne	.LBB46_20
.LBB46_22:
	xorl	%eax, %eax
	xchgb	%al, (%rsi)
	cmpb	$2, %al
	je	.LBB46_26
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
.LBB46_17:
	movq	%rsi, -24(%rbp)
	movl	-4(%rbp), %eax
	movb	%al, -16(%rbp)
.Ltmp166:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.38.llvm.17002324475202138184(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.28.llvm.17002324475202138184(%rip), %rcx
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.27.llvm.17002324475202138184(%rip), %r9
	leaq	-24(%rbp), %r8
	movl	$43, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core6result13unwrap_failed
	nop
.Ltmp167:
	jmp	.LBB46_7
.LBB46_1:
	movq	%rsi, %rcx
	callq	_RNvMNtNtNtNtCse0R8cuyqEa_3std3sys4sync5mutex5futexNtB2_5Mutex14lock_contended
	movq	_RNvNtNtCse0R8cuyqEa_3std9panicking11panic_count18GLOBAL_PANIC_COUNT(%rip), %rax
	shlq	%rax
	testq	%rax, %rax
	je	.LBB46_3
.LBB46_4:
	callq	_RNvNtNtCse0R8cuyqEa_3std9panicking11panic_count17is_zero_slow_path
	xorb	$1, %al
	movzbl	5(%rdi), %ecx
	testb	%cl, %cl
	je	.LBB46_8
.LBB46_6:
	movq	%rsi, -24(%rbp)
	movb	%al, -16(%rbp)
.Ltmp164:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.37.llvm.17002324475202138184(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.28.llvm.17002324475202138184(%rip), %rcx
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.27.llvm.17002324475202138184(%rip), %r9
	leaq	-24(%rbp), %r8
	movl	$43, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core6result13unwrap_failed
	nop
.Ltmp165:
.LBB46_7:
	ud2
.LBB46_26:
	movq	%rsi, %rcx
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
	rex64 jmpq	*__imp_WakeByAddressSingle(%rip)
.LBB46_20:
	callq	_RNvNtNtCse0R8cuyqEa_3std9panicking11panic_count17is_zero_slow_path
	testb	%al, %al
	jne	.LBB46_22
	movb	$1, 5(%rdi)
	jmp	.LBB46_22
	.seh_handlerdata
	.long	$cppxdata$_RNvMs3_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatch14wait_and_reset@IMGREL
	.section	.text,"xr",one_only,_RNvMs3_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatch14wait_and_reset,unique,47
	.seh_endproc
	.def	"?dtor$24@?0?_RNvMs3_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatch14wait_and_reset@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$24@?0?_RNvMs3_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatch14wait_and_reset@4HA":
.seh_proc "?dtor$24@?0?_RNvMs3_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatch14wait_and_reset@4HA"
.LBB46_24:
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
	leaq	64(%rdx), %rbp
	.seh_endprologue
	leaq	-24(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCse0R8cuyqEa_3std4sync6poison11PoisonErrorINtNtBE_5mutex10MutexGuardbEEECs98fvGvYc57G_10rayon_core.llvm.17002324475202138184
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
	.section	.text,"xr",one_only,_RNvMs3_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatch14wait_and_reset,unique,47
	.seh_endproc
	.def	"?dtor$25@?0?_RNvMs3_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatch14wait_and_reset@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$25@?0?_RNvMs3_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatch14wait_and_reset@4HA":
.seh_proc "?dtor$25@?0?_RNvMs3_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatch14wait_and_reset@4HA"
.LBB46_25:
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
	leaq	64(%rdx), %rbp
	.seh_endprologue
	leaq	-24(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCse0R8cuyqEa_3std4sync6poison11PoisonErrorINtNtBE_5mutex10MutexGuardbEEECs98fvGvYc57G_10rayon_core.llvm.17002324475202138184
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
.Lfunc_end46:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs3_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatch14wait_and_reset,unique,47
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvMs3_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatch14wait_and_reset,unique,21
	.p2align	2, 0x0
$cppxdata$_RNvMs3_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatch14wait_and_reset:
	.long	429065506
	.long	2
	.long	$stateUnwindMap$_RNvMs3_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatch14wait_and_reset@IMGREL
	.long	0
	.long	0
	.long	5
	.long	$ip2state$_RNvMs3_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatch14wait_and_reset@IMGREL
	.long	64
	.long	0
	.long	1
$stateUnwindMap$_RNvMs3_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatch14wait_and_reset:
	.long	-1
	.long	"?dtor$24@?0?_RNvMs3_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatch14wait_and_reset@4HA"@IMGREL
	.long	-1
	.long	"?dtor$25@?0?_RNvMs3_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatch14wait_and_reset@4HA"@IMGREL
$ip2state$_RNvMs3_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatch14wait_and_reset:
	.long	.Lfunc_begin46@IMGREL
	.long	-1
	.long	.Ltmp166@IMGREL
	.long	1
	.long	.Ltmp167@IMGREL
	.long	-1
	.long	.Ltmp164@IMGREL
	.long	0
	.long	.Ltmp165@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvMs3_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatch14wait_and_reset,unique,47

	.def	_RNvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB5_8Registry26notify_worker_latch_is_set;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB5_8Registry26notify_worker_latch_is_set,unique,48
	.globl	_RNvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB5_8Registry26notify_worker_latch_is_set
	.p2align	4
_RNvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB5_8Registry26notify_worker_latch_is_set:
.Lfunc_begin47:
	addq	$344, %rcx
	jmp	_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep20wake_specific_thread.llvm.17002324475202138184
.Lfunc_end47:

	.def	_RNvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB5_8Registry6inject;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB5_8Registry6inject,unique,49
	.globl	_RNvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB5_8Registry6inject
	.p2align	4
_RNvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB5_8Registry6inject:
.Lfunc_begin48:
.seh_proc _RNvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtB5_8Registry6inject
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	%rcx, %rsi
	movq	(%rcx), %rax
	movq	128(%rcx), %rdi
	xorq	%rax, %rdi
	callq	_RNvMsg_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_8InjectorNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE4pushB11_.llvm.17002324475202138184
	lock		orl	$0, (%rsp)
	movabsq	$4294967296, %rdx
	.p2align	4
.LBB48_1:
	movq	368(%rsi), %rax
	btq	$32, %rax
	jb	.LBB48_2
	movq	%rax, %rcx
	orq	%rdx, %rcx
	lock		cmpxchgq	%rcx, 368(%rsi)
	jne	.LBB48_1
	movq	%rcx, %rax
	andq	$65535, %rax
	jne	.LBB48_5
	jmp	.LBB48_7
.LBB48_2:
	movq	%rax, %rcx
	movq	%rcx, %rax
	andq	$65535, %rax
	je	.LBB48_7
.LBB48_5:
	cmpq	$2, %rdi
	jae	.LBB48_8
	shrl	$16, %ecx
	cmpl	%eax, %ecx
	je	.LBB48_8
.LBB48_7:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB48_8:
	addq	$344, %rsi
	movq	%rsi, %rcx
	movl	$1, %edx
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	jmp	_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep16wake_any_threads
.Lfunc_end48:
	.seh_endproc

	.def	_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE6resizeBZ_;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE6resizeBZ_,unique,50
	.p2align	4
_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE6resizeBZ_:
.Lfunc_begin49:
.seh_proc _RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE6resizeBZ_
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
	movl	$4216, %eax
	callq	__chkstk
	subq	%rax, %rsp
	.seh_stackalloc 4216
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	movaps	%xmm7, 4064(%rbp)
	.seh_savexmm %xmm7, 4192
	movaps	%xmm6, 4048(%rbp)
	.seh_savexmm %xmm6, 4176
	.seh_endprologue
	movq	$-2, 4040(%rbp)
	movq	(%rcx), %rax
	movq	264(%rax), %r12
	movq	256(%rax), %r13
	movq	%rdx, %r14
	shlq	$4, %r14
	movq	%rdx, %rax
	shrq	$60, %rax
	setne	%al
	movabsq	$9223372036854775800, %r8
	cmpq	%r8, %r14
	seta	%r8b
	orb	%al, %r8b
	je	.LBB49_3
	xorl	%r15d, %r15d
.LBB49_2:
	movq	%r15, %rcx
	movq	%r14, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
.LBB49_3:
	movq	%rdx, 4024(%rbp)
	movq	8(%rcx), %rsi
	movq	%rcx, 4016(%rbp)
	movq	16(%rcx), %rdi
	movl	$8, %r15d
	movl	$8, %edx
	movq	%r14, %rcx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB49_2
	movq	%rax, %rbx
	cmpq	%r13, %r12
	movq	4024(%rbp), %r14
	je	.LBB49_8
	decq	%rdi
	leaq	-1(%r14), %rax
	movl	%r12d, %edx
	subl	%r13d, %edx
	leaq	1(%r13), %rcx
	testb	$1, %dl
	je	.LBB49_7
	movq	%r13, %rdx
	andq	%rdi, %rdx
	shlq	$4, %rdx
	andq	%rax, %r13
	shlq	$4, %r13
	movups	(%rsi,%rdx), %xmm0
	movups	%xmm0, (%rbx,%r13)
	movq	%rcx, %r13
.LBB49_7:
	cmpq	%rcx, %r12
	je	.LBB49_8
	.p2align	4
.LBB49_11:
	movq	%r13, %rcx
	andq	%rdi, %rcx
	shlq	$4, %rcx
	movq	%r13, %rdx
	andq	%rax, %rdx
	shlq	$4, %rdx
	movups	(%rsi,%rcx), %xmm0
	movups	%xmm0, (%rbx,%rdx)
	leaq	1(%r13), %rcx
	movq	%rcx, %rdx
	andq	%rdi, %rdx
	shlq	$4, %rdx
	andq	%rax, %rcx
	shlq	$4, %rcx
	movups	(%rsi,%rdx), %xmm0
	movups	%xmm0, (%rbx,%rcx)
	addq	$2, %r13
	cmpq	%r12, %r13
	jne	.LBB49_11
.LBB49_8:
	callq	_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core
	movq	%rax, %r12
	movq	%rax, 4008(%rbp)
	movq	4016(%rbp), %rax
	movq	%rbx, 8(%rax)
	movq	%r14, 16(%rax)
	movq	(%rax), %rsi
	movl	$16, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	movq	%r12, 4032(%rbp)
	je	.LBB49_9
	movq	%rax, %rdi
	movq	%rbx, (%rax)
	movq	%r14, 8(%rax)
	xchgq	%rdi, 128(%rsi)
	testq	%r12, %r12
	je	.LBB49_14
	leaq	16(%r12), %rbx
	movq	2064(%r12), %rax
	cmpq	$64, %rax
	jb	.LBB49_28
	movups	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352+16(%rip), %xmm6
	movups	anon.a32227af679a3ead67a5cb195479eba7.10.llvm.14389155381977926352(%rip), %xmm7
	leaq	-96(%rbp), %r14
	leaq	1960(%rbp), %r15
	.p2align	4
.LBB49_19:
	movq	8(%r12), %rsi
	movl	$96, %eax
	.p2align	4
.LBB49_20:
	movups	%xmm6, 1880(%rbp,%rax)
	movups	%xmm7, 1864(%rbp,%rax)
	movups	%xmm7, 1896(%rbp,%rax)
	movups	%xmm6, 1912(%rbp,%rax)
	movups	%xmm7, 1928(%rbp,%rax)
	movups	%xmm6, 1944(%rbp,%rax)
	movups	%xmm7, 1960(%rbp,%rax)
	movups	%xmm6, 1976(%rbp,%rax)
	subq	$-128, %rax
	cmpq	$2144, %rax
	jne	.LBB49_20
	movl	$2056, %r8d
	movq	%r14, %rcx
	movq	%rbx, %rdx
	callq	memcpy
	movl	$2048, %r8d
	movq	%rbx, %rcx
	movq	%r15, %rdx
	callq	memcpy
	movq	$0, 2064(%r12)
	lock		orl	$0, (%rsp)
	movq	384(%rsi), %r13
	movl	$2072, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB49_22
	movq	%rax, %r12
	movl	$2056, %r8d
	movq	%rax, %rcx
	movq	%r14, %rdx
	callq	memcpy
	movq	%r13, 2056(%r12)
	movq	$0, 2064(%r12)
	jmp	.LBB49_24
	.p2align	4
.LBB49_25:
	movq	%rcx, %rax
	lock		cmpxchgq	%r8, 256(%rsi)
.LBB49_24:
	movq	256(%rsi), %rcx
	movq	%rcx, %rdx
	andq	$-8, %rdx
	movq	2064(%rdx), %r8
	cmpq	$8, %r8
	jae	.LBB49_25
	xorl	%eax, %eax
	lock		cmpxchgq	%r12, 2064(%rdx)
	jne	.LBB49_24
	movq	%rcx, %rax
	lock		cmpxchgq	%r12, 256(%rsi)
	movq	4032(%rbp), %r12
	movq	2064(%r12), %rax
	cmpq	$63, %rax
	ja	.LBB49_19
.LBB49_28:
	shlq	$5, %rax
	leaq	_RINvNvMs_NtCs3qjAvHHmxHz_15crossbeam_epoch8deferredNtB7_8Deferred3new4callNCINvMNtB9_5guardNtB1g_5Guard15defer_uncheckedNCNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB22_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE6resize0uE0EB2X_(%rip), %rcx
	movq	%rcx, (%rbx,%rax)
	movq	%rdi, 8(%rbx,%rax)
	incq	2064(%r12)
	movq	4024(%rbp), %r14
	cmpq	$64, %r14
	jae	.LBB49_30
	jmp	.LBB49_31
.LBB49_14:
	andq	$-8, %rdi
	cmpq	$0, 8(%rdi)
	je	.LBB49_16
	movq	(%rdi), %rcx
	callq	mi_free
.LBB49_16:
	movq	%rdi, %rcx
	callq	mi_free
	cmpq	$64, %r14
	jb	.LBB49_31
.LBB49_30:
.Ltmp170:
	leaq	4008(%rbp), %rcx
	callq	_RNvMNtCs3qjAvHHmxHz_15crossbeam_epoch5guardNtB2_5Guard5flush
	nop
.Ltmp171:
.LBB49_31:
	movq	4032(%rbp), %rcx
	testq	%rcx, %rcx
	je	.LBB49_34
	decq	2072(%rcx)
	jne	.LBB49_34
	movq	$0, 2176(%rcx)
	cmpq	$0, 2080(%rcx)
	je	.LBB49_35
.LBB49_34:
	movaps	4048(%rbp), %xmm6
	movaps	4064(%rbp), %xmm7
	.seh_startepilogue
	addq	$4216, %rsp
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
.LBB49_22:
.Ltmp168:
	movl	$8, %ecx
	movl	$2072, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp169:
	jmp	.LBB49_10
.LBB49_9:
.Ltmp172:
	movl	$8, %ecx
	movl	$16, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp173:
.LBB49_10:
	ud2
.LBB49_35:
	movaps	4048(%rbp), %xmm6
	movaps	4064(%rbp), %xmm7
	.seh_startepilogue
	addq	$4216, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r13
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	jmp	_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize
	.seh_handlerdata
	.long	$cppxdata$_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE6resizeBZ_@IMGREL
	.section	.text$unlikely,"xr",one_only,_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE6resizeBZ_,unique,50
	.seh_endproc
	.def	"?dtor$12@?0?_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE6resizeBZ_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$12@?0?_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE6resizeBZ_@4HA":
.seh_proc "?dtor$12@?0?_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE6resizeBZ_@4HA"
.LBB49_12:
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
	subq	$72, %rsp
	.seh_stackalloc 72
	leaq	128(%rdx), %rbp
	movaps	%xmm7, 32(%rsp)
	.seh_savexmm %xmm7, 32
	movaps	%xmm6, 48(%rsp)
	.seh_savexmm %xmm6, 48
	.seh_endprologue
	movq	4032(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs3qjAvHHmxHz_15crossbeam_epoch5guard5GuardECs98fvGvYc57G_10rayon_core
	movaps	48(%rsp), %xmm6
	movaps	32(%rsp), %xmm7
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
.Lfunc_end49:
	.seh_handlerdata
	.section	.text$unlikely,"xr",one_only,_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE6resizeBZ_,unique,50
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE6resizeBZ_,unique,22
	.p2align	2, 0x0
$cppxdata$_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE6resizeBZ_:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE6resizeBZ_@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE6resizeBZ_@IMGREL
	.long	4168
	.long	0
	.long	1
$stateUnwindMap$_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE6resizeBZ_:
	.long	-1
	.long	"?dtor$12@?0?_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE6resizeBZ_@4HA"@IMGREL
$ip2state$_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE6resizeBZ_:
	.long	.Lfunc_begin49@IMGREL
	.long	-1
	.long	.Ltmp170@IMGREL
	.long	0
	.long	.Ltmp173@IMGREL
	.long	-1
	.section	.text$unlikely,"xr",one_only,_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE6resizeBZ_,unique,50

	.def	_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE8new_fifoBZ_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE8new_fifoBZ_,unique,51
	.p2align	4
_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE8new_fifoBZ_:
.Lfunc_begin50:
.seh_proc _RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE8new_fifoBZ_
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
	subq	$592, %rsp
	.seh_stackalloc 592
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	andq	$-128, %rsp
	movq	%rsp, %rbx
	movq	%rbp, 576(%rbx)
	movq	$-2, 456(%rbp)
	movq	%rcx, %rsi
	movl	$1024, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB50_7
	movq	%rax, %rdi
	movl	$16, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB50_8
	movq	%rdi, (%rax)
	movq	$64, 8(%rax)
	movq	$1, 128(%rbx)
	movq	$1, 136(%rbx)
	movq	%rax, 256(%rbx)
	xorps	%xmm0, %xmm0
	movaps	%xmm0, 384(%rbx)
	movl	$384, %ecx
	movl	$128, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB50_3
	movq	%rax, %r14
	leaq	128(%rbx), %rdx
	movl	$384, %r8d
	movq	%rax, %rcx
	callq	memcpy
	movq	%r14, (%rsi)
	movq	%rdi, 8(%rsi)
	movq	$64, 16(%rsi)
	movb	$0, 24(%rsi)
	.seh_startepilogue
	leaq	464(%rbp), %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%rbp
	.seh_endepilogue
	retq
.LBB50_8:
	movl	$8, %ecx
	movl	$16, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	ud2
.LBB50_3:
.Ltmp174:
	movl	$128, %ecx
	movl	$384, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp175:
	ud2
.LBB50_7:
	movl	$8, %ecx
	movl	$1024, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE8new_fifoBZ_@IMGREL
	.section	.text,"xr",one_only,_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE8new_fifoBZ_,unique,51
	.seh_endproc
	.def	"?dtor$5@?0?_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE8new_fifoBZ_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$5@?0?_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE8new_fifoBZ_@4HA":
.seh_proc "?dtor$5@?0?_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE8new_fifoBZ_@4HA"
.LBB50_5:
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
	leaq	128(%rdx), %rbp
	.seh_endprologue
	andq	$-128, %rdx
	movq	%rdx, %rbx
	leaq	128(%rbx), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEEEB35_
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
.Lfunc_end50:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE8new_fifoBZ_,unique,51
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE8new_fifoBZ_,unique,23
	.p2align	2, 0x0
$cppxdata$_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE8new_fifoBZ_:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE8new_fifoBZ_@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE8new_fifoBZ_@IMGREL
	.long	584
	.long	0
	.long	1
$stateUnwindMap$_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE8new_fifoBZ_:
	.long	-1
	.long	"?dtor$5@?0?_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE8new_fifoBZ_@4HA"@IMGREL
$ip2state$_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE8new_fifoBZ_:
	.long	.Lfunc_begin50@IMGREL
	.long	-1
	.long	.Ltmp174@IMGREL
	.long	0
	.long	.Ltmp175@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE8new_fifoBZ_,unique,51

	.def	_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCs98fvGvYc57G_10rayon_core;
	.scl	3;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCs98fvGvYc57G_10rayon_core,unique,52
	.p2align	4
_RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCs98fvGvYc57G_10rayon_core:
.Lfunc_begin51:
.seh_proc _RNvMs5_NtCsfQUUnEvlYZE_5alloc7raw_vecNtB5_11RawVecInner11finish_growCs98fvGvYc57G_10rayon_core
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$32, %rsp
	.seh_stackalloc 32
	.seh_endprologue
	movq	%r9, %rax
	movq	%rdx, %r9
	movq	%rcx, %rsi
	mulq	96(%rsp)
	movq	%rax, %rdi
	seto	%al
	movabsq	$9223372036854775800, %rcx
	cmpq	%rcx, %rdi
	seta	%cl
	orb	%al, %cl
	movl	$1, %ebx
	je	.LBB51_2
	movl	$8, %eax
	xorl	%edi, %edi
	jmp	.LBB51_10
.LBB51_2:
	testq	%r9, %r9
	je	.LBB51_4
	movq	%r8, %rcx
	movl	$8, %r8d
	movq	%rdi, %rdx
	callq	mi_realloc_aligned
	testq	%rax, %rax
	jne	.LBB51_6
	jmp	.LBB51_9
.LBB51_4:
	testq	%rdi, %rdi
	je	.LBB51_5
	movl	$8, %edx
	movq	%rdi, %rcx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	jne	.LBB51_6
.LBB51_9:
	movq	$8, 8(%rsi)
	movl	$16, %eax
	jmp	.LBB51_10
.LBB51_5:
	movl	$8, %eax
.LBB51_6:
	movq	%rax, 8(%rsi)
	movl	$16, %eax
	xorl	%ebx, %ebx
.LBB51_10:
	movq	%rdi, (%rsi,%rax)
	movq	%rbx, (%rsi)
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end51:
	.seh_endproc

	.def	_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread14take_local_job.llvm.17002324475202138184;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread14take_local_job.llvm.17002324475202138184,unique,53
	.globl	_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread14take_local_job.llvm.17002324475202138184
	.p2align	4
_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread14take_local_job.llvm.17002324475202138184:
.Lfunc_begin52:
.seh_proc _RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread14take_local_job.llvm.17002324475202138184
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	pushq	%rbx
	.seh_pushreg %rbx
	subq	$64, %rsp
	.seh_stackalloc 64
	.seh_endprologue
	movq	%rcx, %rsi
	movq	280(%rcx), %rax
	movq	264(%rax), %r9
	movq	256(%rax), %rdx
	movq	%r9, %rcx
	subq	%rdx, %rcx
	testq	%rcx, %rcx
	jle	.LBB52_13
	cmpb	$1, 304(%rsi)
	jne	.LBB52_5
	leaq	-1(%r9), %rcx
	movq	%rcx, 264(%rax)
	lock		orl	$0, (%rsp)
	movq	280(%rsi), %r11
	movq	256(%r11), %rdi
	movq	%rcx, %r10
	subq	%rdi, %r10
	js	.LBB52_8
	movq	288(%rsi), %rdx
	movq	296(%rsi), %r8
	leaq	-1(%r8), %rbx
	andq	%rcx, %rbx
	shlq	$4, %rbx
	movq	(%rdx,%rbx), %rax
	movq	8(%rdx,%rbx), %rdx
	cmpq	%rdi, %rcx
	jne	.LBB52_9
	movq	%rax, %r8
	movq	%rcx, %rax
	lock		cmpxchgq	%r9, 256(%r11)
	movq	%r8, %rax
	movq	280(%rsi), %rcx
	movq	%r9, 264(%rcx)
	jne	.LBB52_13
	jmp	.LBB52_17
.LBB52_5:
	movl	$1, %edx
	lock		xaddq	%rdx, 256(%rax)
	cmpq	%r9, %rdx
	js	.LBB52_6
	movq	280(%rsi), %rax
	movq	%rdx, 256(%rax)
	jmp	.LBB52_13
.LBB52_8:
	movq	%r9, 264(%r11)
.LBB52_13:
	addq	$312, %rsi
	leaq	40(%rsp), %rdi
	.p2align	4
.LBB52_14:
	movq	%rdi, %rcx
	movq	%rsi, %rdx
	callq	_RNvMs8_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_7StealerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE5stealB10_
	movq	40(%rsp), %rax
	cmpq	$2, %rax
	je	.LBB52_14
	testq	%rax, %rax
	jne	.LBB52_16
	xorl	%eax, %eax
	jmp	.LBB52_17
.LBB52_16:
	movq	48(%rsp), %rax
	movq	56(%rsp), %rdx
.LBB52_17:
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB52_6:
	movq	288(%rsi), %r9
	movq	296(%rsi), %r8
	leaq	-1(%r8), %r10
	andq	%rdx, %r10
	shlq	$4, %r10
	movq	(%r9,%r10), %rax
	movq	8(%r9,%r10), %rdx
	leaq	3(%r8), %r9
	testq	%r8, %r8
	cmovnsq	%r8, %r9
	cmpq	$65, %r8
	jb	.LBB52_17
	sarq	$2, %r9
	cmpq	%r9, %rcx
	jg	.LBB52_17
	jmp	.LBB52_11
.LBB52_9:
	leaq	3(%r8), %rcx
	testq	%r8, %r8
	cmovnsq	%r8, %rcx
	cmpq	$65, %r8
	jb	.LBB52_17
	sarq	$2, %rcx
	cmpq	%rcx, %r10
	jge	.LBB52_17
.LBB52_11:
	shrq	%r8
	addq	$280, %rsi
	movq	%rsi, %rcx
	movq	%rdx, %rsi
	movq	%r8, %rdx
	movq	%rax, %rdi
	callq	_RNvMs4_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_6WorkerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE6resizeBZ_
	movq	%rsi, %rdx
	movq	%rdi, %rax
	jmp	.LBB52_17
.Lfunc_end52:
	.seh_endproc

	.def	_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread15wait_until_cold;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread15wait_until_cold,unique,54
	.globl	_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread15wait_until_cold
	.p2align	4
_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread15wait_until_cold:
.Lfunc_begin53:
.seh_proc _RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread15wait_until_cold
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
	subq	$72, %rsp
	.seh_stackalloc 72
	leaq	64(%rsp), %rbp
	.seh_setframe %rbp, 64
	.seh_endprologue
	movq	$-2, (%rbp)
	movq	%rdx, %rdi
	movq	%rcx, %rsi
	movq	__imp_SwitchToThread(%rip), %r14
	leaq	-24(%rbp), %rbx
	movl	$2, %r12d
	jmp	.LBB53_1
	.p2align	4
.LBB53_4:
.Ltmp178:
	movq	%rdx, %rcx
	callq	*%rax
	nop
.Ltmp179:
.LBB53_1:
	movq	(%rdi), %rax
	cmpq	$3, %rax
	je	.LBB53_14
.Ltmp176:
	movq	%rsi, %rcx
	callq	_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread14take_local_job.llvm.17002324475202138184
	nop
.Ltmp177:
	testq	%rax, %rax
	jne	.LBB53_4
	movq	256(%rsi), %rax
	movq	272(%rsi), %rcx
	lock		addq	$65536, 496(%rcx)
	movq	%rax, -24(%rbp)
	movl	$0, -8(%rbp)
	movq	$-1, -16(%rbp)
	jmp	.LBB53_6
	.p2align	4
.LBB53_15:
	callq	*%r14
	incl	%r13d
	movl	%r13d, -8(%rbp)
.LBB53_6:
	movq	(%rdi), %rax
	cmpq	$3, %rax
	je	.LBB53_13
.Ltmp180:
	movq	%rsi, %rcx
	callq	_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread9find_work.llvm.17002324475202138184
	nop
.Ltmp181:
	movq	272(%rsi), %rcx
	testq	%rax, %rax
	jne	.LBB53_19
	leaq	472(%rcx), %rax
	movl	-8(%rbp), %r13d
	cmpl	$32, %r13d
	jb	.LBB53_15
	je	.LBB53_11
.Ltmp186:
	movq	%rax, %rcx
	movq	%rbx, %rdx
	movq	%rdi, %r8
	movq	%rsi, %r9
	callq	_RINvMNtCs98fvGvYc57G_10rayon_core5sleepNtB3_5Sleep5sleepNCNvMs8_NtB5_8registryNtB10_12WorkerThread15wait_until_cold0EB5_.llvm.17002324475202138184
	nop
.Ltmp187:
	jmp	.LBB53_6
.LBB53_11:
	movq	496(%rcx), %rax
	btq	$32, %rax
	jae	.LBB53_12
	movabsq	$4294967296, %rdx
	addq	%rax, %rdx
	lock		cmpxchgq	%rdx, 496(%rcx)
	jne	.LBB53_11
	jmp	.LBB53_17
.LBB53_12:
	movq	%rax, %rdx
.LBB53_17:
	shrq	$32, %rdx
	movq	%rdx, -16(%rbp)
	incl	-8(%rbp)
	callq	*%r14
	jmp	.LBB53_6
.LBB53_19:
	movq	$-65536, %r8
	lock		xaddq	%r8, 496(%rcx)
	movzwl	%r8w, %r8d
	cmpq	$2, %r8
	cmovaeq	%r12, %r8
	addq	$472, %rcx
.Ltmp182:
	movq	%rdx, %r13
	movl	%r8d, %edx
	movq	%rax, %r15
	callq	_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep16wake_any_threads
	nop
.Ltmp183:
.Ltmp184:
	movq	%r13, %rcx
	callq	*%r15
	nop
.Ltmp185:
	jmp	.LBB53_1
.LBB53_13:
	movq	272(%rsi), %rcx
	movq	$-65536, %rax
	lock		xaddq	%rax, 496(%rcx)
	movzwl	%ax, %eax
	cmpq	$2, %rax
	movl	$2, %edx
	cmovbq	%rax, %rdx
	addq	$472, %rcx
.Ltmp188:
	callq	_RNvMNtCs98fvGvYc57G_10rayon_core5sleepNtB2_5Sleep16wake_any_threads
	nop
.Ltmp189:
.LBB53_14:
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
	.seh_handlerdata
	.long	$cppxdata$_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread15wait_until_cold@IMGREL
	.section	.text$unlikely,"xr",one_only,_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread15wait_until_cold,unique,54
	.seh_endproc
	.def	"?dtor$21@?0?_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread15wait_until_cold@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$21@?0?_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread15wait_until_cold@4HA":
.seh_proc "?dtor$21@?0?_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread15wait_until_cold@4HA"
.LBB53_21:
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
	leaq	64(%rdx), %rbp
	.seh_endprologue
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.54.llvm.17002324475202138184(%rip), %rcx
	movl	$87, %edx
	callq	_RNvNtNtCse0R8cuyqEa_3std2io5stdio7__eprint
	movl	$7, %ecx
	#APP

	int	$41

	#NO_APP
	ud2
.Lfunc_end53:
	.seh_handlerdata
	.section	.text$unlikely,"xr",one_only,_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread15wait_until_cold,unique,54
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread15wait_until_cold,unique,24
	.p2align	2, 0x0
$cppxdata$_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread15wait_until_cold:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread15wait_until_cold@IMGREL
	.long	0
	.long	0
	.long	7
	.long	$ip2state$_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread15wait_until_cold@IMGREL
	.long	64
	.long	0
	.long	1
$stateUnwindMap$_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread15wait_until_cold:
	.long	-1
	.long	"?dtor$21@?0?_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread15wait_until_cold@4HA"@IMGREL
$ip2state$_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread15wait_until_cold:
	.long	.Lfunc_begin53@IMGREL
	.long	-1
	.long	.Ltmp178@IMGREL
	.long	0
	.long	.Ltmp177@IMGREL
	.long	-1
	.long	.Ltmp180@IMGREL
	.long	0
	.long	.Ltmp187@IMGREL
	.long	-1
	.long	.Ltmp182@IMGREL
	.long	0
	.long	.Ltmp189@IMGREL
	.long	-1
	.section	.text$unlikely,"xr",one_only,_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread15wait_until_cold,unique,54

	.def	_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread9find_work.llvm.17002324475202138184;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread9find_work.llvm.17002324475202138184,unique,55
	.globl	_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread9find_work.llvm.17002324475202138184
	.p2align	4
_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread9find_work.llvm.17002324475202138184:
.Lfunc_begin54:
.seh_proc _RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread9find_work.llvm.17002324475202138184
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
	movq	%rcx, %rsi
	callq	_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread14take_local_job.llvm.17002324475202138184
	testq	%rax, %rax
	je	.LBB54_3
	movq	%rax, %rdi
	movq	%rdx, %r15
.LBB54_2:
	movq	%rdi, %rax
	movq	%r15, %rdx
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
.LBB54_3:
	movq	272(%rsi), %r12
	movq	520(%r12), %rbx
	cmpq	$2, %rbx
	jae	.LBB54_4
.LBB54_26:
	movq	__imp_SwitchToThread(%rip), %r15
	xorl	%edi, %edi
	jmp	.LBB54_27
	.p2align	4
.LBB54_39:
	lock		cmpxchgq	%rbx, 128(%r12)
	je	.LBB54_40
.LBB54_27:
	movq	128(%r12), %rax
	movq	136(%r12), %rsi
	movq	%rax, %rcx
	shrq	%rcx
	movl	%ecx, %r14d
	andl	$63, %r14d
	cmpq	$63, %r14
	jne	.LBB54_35
	xorl	%ebx, %ebx
	jmp	.LBB54_29
	.p2align	4
.LBB54_33:
	incl	%ebx
.LBB54_34:
	movq	128(%r12), %rax
	movq	136(%r12), %rsi
	movq	%rax, %rcx
	shrq	%rcx
	movl	%ecx, %r14d
	andl	$63, %r14d
	cmpq	$63, %r14
	jne	.LBB54_35
.LBB54_29:
	cmpl	$6, %ebx
	ja	.LBB54_32
	movl	$1, %eax
	.p2align	4
.LBB54_31:
	pause
	movl	%eax, %edx
	movl	%ebx, %ecx
	shrl	%cl, %edx
	incl	%eax
	testl	%edx, %edx
	je	.LBB54_31
	jmp	.LBB54_33
	.p2align	4
.LBB54_32:
	callq	*%r15
	cmpl	$11, %ebx
	jb	.LBB54_33
	jmp	.LBB54_34
	.p2align	4
.LBB54_35:
	leaq	2(%rax), %rbx
	testb	$1, %al
	jne	.LBB54_39
	lock		orl	$0, (%rsp)
	movq	256(%r12), %rdx
	movq	%rdx, %r8
	shrq	%r8
	cmpq	%r8, %rcx
	je	.LBB54_37
	xorq	%rax, %rdx
	xorl	%ecx, %ecx
	cmpq	$127, %rdx
	seta	%cl
	orq	%rcx, %rbx
	jmp	.LBB54_39
.LBB54_4:
	movq	512(%r12), %r14
	leaq	24(%r14), %rbp
	movabsq	$2685821657736338717, %r8
.LBB54_5:
	movq	264(%rsi), %rax
	movq	%rax, %rcx
	shrq	$12, %rcx
	xorq	%rax, %rcx
	movq	%rcx, %rdx
	shlq	$25, %rdx
	xorq	%rcx, %rdx
	movq	%rdx, %rax
	shrq	$27, %rax
	xorq	%rdx, %rax
	movq	%rax, 264(%rsi)
	imulq	%r8, %rax
	movq	$0, 40(%rsp)
	xorl	%edx, %edx
	divq	%rbx
	movq	%rdx, %r12
	movq	%rdx, %r13
	jmp	.LBB54_6
.LBB54_18:
	movb	$1, %al
	movq	%rax, 40(%rsp)
	.p2align	4
.LBB54_19:
	xorl	%edi, %edi
	incq	%r13
	testq	%rdi, %rdi
	jne	.LBB54_2
.LBB54_6:
	cmpq	%rbx, %r13
	jae	.LBB54_7
	cmpq	256(%rsi), %r13
	je	.LBB54_19
	leaq	(,%r13,4), %rax
	addq	%r13, %rax
	leaq	(%r14,%rax,8), %rdx
	addq	$24, %rdx
	leaq	48(%rsp), %rcx
	callq	_RNvMs8_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_7StealerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE5stealB10_
	movq	48(%rsp), %rax
	testq	%rax, %rax
	je	.LBB54_19
	cmpl	$1, %eax
	jne	.LBB54_18
	movq	56(%rsp), %rdi
	movq	64(%rsp), %r15
	incq	%r13
	testq	%rdi, %rdi
	je	.LBB54_6
	jmp	.LBB54_2
.LBB54_7:
	xorl	%r13d, %r13d
	jmp	.LBB54_8
.LBB54_21:
	movb	$1, %al
	movq	%rax, 40(%rsp)
	.p2align	4
.LBB54_22:
	xorl	%edi, %edi
.LBB54_23:
	addq	$40, %rbp
	incq	%r13
	testq	%rdi, %rdi
	jne	.LBB54_2
.LBB54_8:
	cmpq	%r12, %r13
	jae	.LBB54_24
	cmpq	256(%rsi), %r13
	je	.LBB54_22
	cmpq	%rbx, %r13
	jae	.LBB54_75
	leaq	48(%rsp), %rcx
	movq	%rbp, %rdx
	callq	_RNvMs8_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_7StealerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE5stealB10_
	movq	48(%rsp), %rax
	testq	%rax, %rax
	je	.LBB54_22
	cmpl	$1, %eax
	jne	.LBB54_21
	movq	56(%rsp), %rdi
	movq	64(%rsp), %r15
	jmp	.LBB54_23
.LBB54_24:
	testb	$1, 40(%rsp)
	leaq	24(%r14), %rbp
	movabsq	$2685821657736338717, %r8
	jne	.LBB54_5
	movq	272(%rsi), %r12
	jmp	.LBB54_26
.LBB54_40:
	cmpl	$62, %r14d
	jne	.LBB54_58
	movq	(%rsi), %rax
	testq	%rax, %rax
	je	.LBB54_42
.LBB54_49:
	andq	$-2, %rbx
	movq	(%rax), %rcx
	xorl	%edx, %edx
	testq	%rcx, %rcx
	setne	%dl
	leaq	(%rbx,%rdx), %rcx
	addq	$2, %rcx
	movq	%rax, 136(%r12)
	movq	%rcx, 128(%r12)
	movq	1512(%rsi), %rax
	testb	$1, %al
	jne	.LBB54_57
	xorl	%edi, %edi
	jmp	.LBB54_51
	.p2align	4
.LBB54_55:
	incl	%edi
.LBB54_56:
	movq	1512(%rsi), %rax
	testb	$1, %al
	jne	.LBB54_57
.LBB54_51:
	cmpl	$6, %edi
	ja	.LBB54_54
	movl	$1, %eax
	.p2align	4
.LBB54_53:
	pause
	movl	%eax, %edx
	movl	%edi, %ecx
	shrl	%cl, %edx
	incl	%eax
	testl	%edx, %edx
	je	.LBB54_53
	jmp	.LBB54_55
	.p2align	4
.LBB54_54:
	callq	*%r15
	cmpl	$11, %edi
	jb	.LBB54_55
	jmp	.LBB54_56
.LBB54_37:
	jmp	.LBB54_2
.LBB54_58:
	leaq	(%r14,%r14,2), %rax
	leaq	(%rsi,%rax,8), %rbx
	addq	$8, %rbx
	movq	24(%rsi,%rax,8), %rax
	testb	$1, %al
	jne	.LBB54_66
	xorl	%edi, %edi
	jmp	.LBB54_60
	.p2align	4
.LBB54_64:
	incl	%edi
.LBB54_65:
	movq	16(%rbx), %rax
	testb	$1, %al
	jne	.LBB54_66
.LBB54_60:
	cmpl	$6, %edi
	ja	.LBB54_63
	movl	$1, %eax
	.p2align	4
.LBB54_62:
	pause
	movl	%eax, %edx
	movl	%edi, %ecx
	shrl	%cl, %edx
	incl	%eax
	testl	%edx, %edx
	je	.LBB54_62
	jmp	.LBB54_64
	.p2align	4
.LBB54_63:
	callq	*%r15
	cmpl	$11, %edi
	jb	.LBB54_64
	jmp	.LBB54_65
.LBB54_57:
	movq	1496(%rsi), %rdi
	movq	1504(%rsi), %r15
	jmp	.LBB54_69
.LBB54_66:
	movq	(%rbx), %rdi
	movq	8(%rbx), %r15
	movq	16(%rbx), %rax
	.p2align	4
.LBB54_67:
	movq	%rax, %rcx
	orq	$2, %rcx
	lock		cmpxchgq	%rcx, 16(%rbx)
	jne	.LBB54_67
	testb	$4, %al
	je	.LBB54_2
	.p2align	4
.LBB54_69:
	testq	%r14, %r14
	je	.LBB54_70
	decq	%r14
	leaq	(%r14,%r14,2), %rax
	movq	24(%rsi,%rax,8), %rcx
	testb	$2, %cl
	jne	.LBB54_69
	leaq	(%rsi,%rax,8), %rcx
	movq	24(%rcx), %rax
	.p2align	4
.LBB54_73:
	movq	%rax, %rdx
	orq	$4, %rdx
	lock		cmpxchgq	%rdx, 24(%rcx)
	jne	.LBB54_73
	testb	$2, %al
	jne	.LBB54_69
	jmp	.LBB54_2
.LBB54_70:
	movq	%rsi, %rcx
	callq	mi_free
	jmp	.LBB54_2
.LBB54_42:
	xorl	%edi, %edi
	jmp	.LBB54_43
	.p2align	4
.LBB54_47:
	incl	%edi
.LBB54_48:
	movq	(%rsi), %rax
	testq	%rax, %rax
	jne	.LBB54_49
.LBB54_43:
	cmpl	$6, %edi
	ja	.LBB54_46
	movl	$1, %eax
	.p2align	4
.LBB54_45:
	pause
	movl	%eax, %edx
	movl	%edi, %ecx
	shrl	%cl, %edx
	incl	%eax
	testl	%edx, %edx
	je	.LBB54_45
	jmp	.LBB54_47
	.p2align	4
.LBB54_46:
	callq	*%r15
	cmpl	$11, %edi
	jb	.LBB54_47
	jmp	.LBB54_48
.LBB54_75:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.22(%rip), %r8
	movq	%r13, %rcx
	movq	%rbx, %rdx
	callq	_RNvNtCs8xEFJqa6dYS_4core9panicking18panic_bounds_check
	ud2
.Lfunc_end54:
	.seh_endproc

	.def	_RNvMs8_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_7StealerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE5stealB10_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMs8_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_7StealerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE5stealB10_,unique,56
	.p2align	4
_RNvMs8_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_7StealerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE5stealB10_:
.Lfunc_begin55:
.seh_proc _RNvMs8_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_7StealerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE5stealB10_
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
	movq	(%rdx), %rbx
	movq	256(%rbx), %rdi
	movl	_tls_index(%rip), %eax
	movq	%gs:88, %rcx
	movq	(%rcx,%rax,8), %rcx
	leaq	_RNvNCNKNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default6HANDLE0023___RUST_STD_INTERNAL_VAL@SECREL32(%rcx), %rax
	cmpb	$1, _RNvNCNKNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default6HANDLE0023___RUST_STD_INTERNAL_VAL@SECREL32+8(%rcx)
	jne	.LBB55_1
.LBB55_2:
	movq	(%rax), %rax
	movq	2072(%rax), %rcx
.LBB55_3:
	testq	%rcx, %rcx
	je	.LBB55_9
	lock		orl	$0, (%rsp)
.LBB55_9:
	callq	_RINvNtCs3qjAvHHmxHz_15crossbeam_epoch7default11with_handleNCNvB2_3pin0NtNtB4_5guard5GuardECs98fvGvYc57G_10rayon_core
	movq	%rax, %rcx
	movq	264(%rbx), %rax
	subq	%rdi, %rax
	testq	%rax, %rax
	jle	.LBB55_10
	movq	128(%rbx), %rax
	movq	%rax, %rdx
	andq	$-8, %rdx
	movq	(%rdx), %r9
	movq	8(%rdx), %rdx
	decq	%rdx
	andq	%rdi, %rdx
	shlq	$4, %rdx
	movq	(%r9,%rdx), %r8
	movq	8(%r9,%rdx), %r9
	movq	128(%rbx), %r10
	movl	$2, %edx
	cmpq	%rax, %r10
	jne	.LBB55_11
	leaq	1(%rdi), %r10
	movq	%rdi, %rax
	lock		cmpxchgq	%r10, 256(%rbx)
	jne	.LBB55_11
	movq	%r8, 8(%rsi)
	movq	%r9, 16(%rsi)
	movq	$1, (%rsi)
	testq	%rcx, %rcx
	jne	.LBB55_16
	jmp	.LBB55_18
.LBB55_10:
	xorl	%edx, %edx
.LBB55_11:
	movq	%rdx, (%rsi)
	testq	%rcx, %rcx
	je	.LBB55_18
.LBB55_16:
	decq	2072(%rcx)
	jne	.LBB55_18
	movq	$0, 2176(%rcx)
	cmpq	$0, 2080(%rcx)
	je	.LBB55_19
.LBB55_18:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB55_1:
	movq	%rax, %rcx
	callq	_RINvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys12thread_local6native4lazyINtB6_7StorageNtNtCs3qjAvHHmxHz_15crossbeam_epoch9collector11LocalHandleuE16get_or_init_slowNvNvNtB1h_7default6HANDLE27___rust_std_internal_init_fnECs98fvGvYc57G_10rayon_core
	testq	%rax, %rax
	jne	.LBB55_2
	movl	_RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default9collector9COLLECTOR.llvm.14389155381977926352+8(%rip), %eax
	testl	%eax, %eax
	jne	.LBB55_6
.LBB55_7:
	leaq	_RNvNvNtCs3qjAvHHmxHz_15crossbeam_epoch7default9collector9COLLECTOR.llvm.14389155381977926352(%rip), %rcx
	callq	_RNvMs1_NtCs3qjAvHHmxHz_15crossbeam_epoch9collectorNtB5_9Collector8register
	movq	2072(%rax), %rcx
	movq	2080(%rax), %rdx
	leaq	-1(%rdx), %r8
	movq	%r8, 2080(%rax)
	xorq	$1, %rdx
	orq	%rcx, %rdx
	jne	.LBB55_3
	movq	%rax, %rcx
	callq	_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize
	jmp	.LBB55_9
.LBB55_19:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	jmp	_RNvMs6_NtCs3qjAvHHmxHz_15crossbeam_epoch8internalNtB5_5Local8finalize
.LBB55_6:
	callq	_RINvMs0_NtNtCs3qjAvHHmxHz_15crossbeam_epoch4sync9once_lockINtB6_8OnceLockNtNtBa_9collector9CollectorE10initializeNvMs1_B1b_B19_3newEBa_.llvm.14389155381977926352
	jmp	.LBB55_7
.Lfunc_end55:
	.seh_endproc

	.def	_RNvMsg_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_8InjectorNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE4pushB11_.llvm.17002324475202138184;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMsg_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_8InjectorNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE4pushB11_.llvm.17002324475202138184,unique,57
	.globl	_RNvMsg_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_8InjectorNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE4pushB11_.llvm.17002324475202138184
	.p2align	4
_RNvMsg_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_8InjectorNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE4pushB11_.llvm.17002324475202138184:
.Lfunc_begin56:
.seh_proc _RNvMsg_NtCslOUiAINmber_15crossbeam_deque5dequeINtB5_8InjectorNtNtCs98fvGvYc57G_10rayon_core3job6JobRefE4pushB11_.llvm.17002324475202138184
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
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	%r8, 32(%rsp)
	movq	%rdx, %rdi
	movq	%rcx, %r14
	movq	128(%rcx), %rsi
	movq	136(%rcx), %r13
	xorl	%ebx, %ebx
	movq	__imp_SwitchToThread(%rip), %r12
	xorl	%ebp, %ebp
	jmp	.LBB56_1
	.p2align	4
.LBB56_6:
	incl	%ebp
.LBB56_7:
	movq	128(%r14), %rsi
	movq	136(%r14), %r13
.LBB56_1:
	movl	%esi, %r15d
	shrl	%r15d
	andl	$63, %r15d
	cmpl	$63, %r15d
	jne	.LBB56_8
	cmpl	$6, %ebp
	ja	.LBB56_5
	movl	$1, %eax
	.p2align	4
.LBB56_4:
	pause
	movl	%eax, %edx
	movl	%ebp, %ecx
	shrl	%cl, %edx
	incl	%eax
	testl	%edx, %edx
	je	.LBB56_4
	jmp	.LBB56_6
	.p2align	4
.LBB56_5:
	callq	*%r12
	cmpl	$11, %ebp
	jb	.LBB56_6
	jmp	.LBB56_7
.LBB56_8:
	movq	%r15, %rax
	xorq	$62, %rax
	orq	%rbx, %rax
	jne	.LBB56_10
	movl	$1520, %ecx
	movl	$8, %edx
	callq	mi_zalloc_aligned
	movq	%rax, %rbx
	testq	%rax, %rax
	je	.LBB56_21
.LBB56_10:
	leaq	2(%rsi), %rcx
	movq	%rsi, %rax
	lock		cmpxchgq	%rcx, 128(%r14)
	je	.LBB56_11
	movq	136(%r14), %r13
	cmpl	$6, %ebp
	movl	$6, %ecx
	cmovbl	%ebp, %ecx
	movl	$1, %edx
	.p2align	4
.LBB56_19:
	pause
	movl	%edx, %r8d
	shrl	%cl, %r8d
	incl	%edx
	testl	%r8d, %r8d
	je	.LBB56_19
	cmpl	$7, %ebp
	adcl	$0, %ebp
	movq	%rax, %rsi
	jmp	.LBB56_1
.LBB56_11:
	cmpl	$62, %r15d
	jne	.LBB56_12
	testq	%rbx, %rbx
	je	.LBB56_14
	movq	%rbx, 136(%r14)
	addq	$4, %rsi
	movq	%rsi, 128(%r14)
	movq	%rbx, (%r13)
	movq	%rdi, 1496(%r13)
	movq	32(%rsp), %rax
	movq	%rax, 1504(%r13)
	lock		orq	$1, 1512(%r13)
	jmp	.LBB56_17
.LBB56_12:
	leaq	(%r15,%r15,2), %rax
	movq	%rdi, 8(%r13,%rax,8)
	movq	32(%rsp), %rcx
	movq	%rcx, 16(%r13,%rax,8)
	lock		orq	$1, 24(%r13,%rax,8)
	testq	%rbx, %rbx
	je	.LBB56_17
	movq	%rbx, %rcx
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r13
	popq	%r14
	popq	%r15
	.seh_endepilogue
	jmp	mi_free
.LBB56_17:
	.seh_startepilogue
	addq	$40, %rsp
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
.LBB56_21:
	movl	$8, %ecx
	movl	$1520, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	ud2
.LBB56_14:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.50(%rip), %rcx
	callq	_RNvNtCs8xEFJqa6dYS_4core6option13unwrap_failed
	ud2
.Lfunc_end56:
	.seh_endproc

	.def	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_,unique,58
	.globl	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
	.p2align	4
_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_:
.Lfunc_begin57:
.seh_proc _RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rcx), %rsi
	movq	128(%rsi), %rdi
	andq	$-8, %rdi
	cmpq	$0, 8(%rdi)
	je	.LBB57_2
	movq	(%rdi), %rcx
	callq	mi_free
.LBB57_2:
	movq	%rdi, %rcx
	callq	mi_free
	cmpq	$-1, %rsi
	je	.LBB57_4
	lock		decq	8(%rsi)
	jne	.LBB57_4
	#MEMBARRIER
	movq	%rsi, %rcx
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	jmp	mi_free
.LBB57_4:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end57:
	.seh_endproc

	.def	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_,unique,59
	.globl	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_
	.p2align	4
_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_:
.Lfunc_begin58:
.seh_proc _RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_
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
	leaq	128(%rax), %rcx
.Ltmp190:
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryEBF_
	nop
.Ltmp191:
	movq	-16(%rbp), %rcx
	cmpq	$-1, %rcx
	je	.LBB58_8
	lock		decq	8(%rcx)
	jne	.LBB58_8
	#MEMBARRIER
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbp
	.seh_endepilogue
	jmp	mi_free
.LBB58_8:
	.seh_startepilogue
	addq	$48, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.long	$cppxdata$_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_@IMGREL
	.section	.text,"xr",one_only,_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_,unique,59
	.seh_endproc
	.def	"?dtor$4@?0?_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$4@?0?_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_@4HA":
.seh_proc "?dtor$4@?0?_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_@4HA"
.LBB58_4:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	48(%rdx), %rbp
	.seh_endprologue
	cmpq	$-1, -16(%rbp)
	je	.LBB58_7
	movq	-16(%rbp), %rax
	lock		decq	8(%rax)
	jne	.LBB58_7
	#MEMBARRIER
	movq	-16(%rbp), %rcx
	callq	mi_free
	nop
.LBB58_7:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end58:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_,unique,59
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_,unique,25
	.p2align	2, 0x0
$cppxdata$_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_@IMGREL
	.long	40
	.long	0
	.long	1
$stateUnwindMap$_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_:
	.long	-1
	.long	"?dtor$4@?0?_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_@4HA"@IMGREL
$ip2state$_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_:
	.long	.Lfunc_begin58@IMGREL
	.long	-1
	.long	.Ltmp190@IMGREL
	.long	0
	.long	.Ltmp191@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_,unique,59

	.def	_RNvNtCs98fvGvYc57G_10rayon_core4join23join_recover_from_panic;
	.scl	2;
	.type	32;
	.endef
	.section	.text$unlikely,"xr",one_only,_RNvNtCs98fvGvYc57G_10rayon_core4join23join_recover_from_panic,unique,60
	.globl	_RNvNtCs98fvGvYc57G_10rayon_core4join23join_recover_from_panic
	.p2align	4
_RNvNtCs98fvGvYc57G_10rayon_core4join23join_recover_from_panic:
.Lfunc_begin59:
.seh_proc _RNvNtCs98fvGvYc57G_10rayon_core4join23join_recover_from_panic
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
	movq	%r9, -24(%rbp)
	movq	%r8, -32(%rbp)
	movq	8(%rdx), %rax
	cmpq	$3, %rax
	jne	.LBB59_1
.LBB59_2:
	movb	$0, -9(%rbp)
.Ltmp194:
	movq	-32(%rbp), %rcx
	movq	-24(%rbp), %rdx
	callq	_RNvNtCs98fvGvYc57G_10rayon_core6unwind16resume_unwinding
	nop
.Ltmp195:
	ud2
.LBB59_1:
	addq	$8, %rdx
	movb	$1, -9(%rbp)
.Ltmp192:
	callq	_RNvMs8_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThread15wait_until_cold
	nop
.Ltmp193:
	jmp	.LBB59_2
	.seh_handlerdata
	.long	$cppxdata$_RNvNtCs98fvGvYc57G_10rayon_core4join23join_recover_from_panic@IMGREL
	.section	.text$unlikely,"xr",one_only,_RNvNtCs98fvGvYc57G_10rayon_core4join23join_recover_from_panic,unique,60
	.seh_endproc
	.def	"?dtor$4@?0?_RNvNtCs98fvGvYc57G_10rayon_core4join23join_recover_from_panic@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$4@?0?_RNvNtCs98fvGvYc57G_10rayon_core4join23join_recover_from_panic@4HA":
.seh_proc "?dtor$4@?0?_RNvNtCs98fvGvYc57G_10rayon_core4join23join_recover_from_panic@4HA"
.LBB59_4:
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
	movq	-24(%rbp), %rdi
	cmpb	$0, -9(%rbp)
	movq	-32(%rbp), %rsi
	je	.LBB59_9
	movq	(%rdi), %rax
	testq	%rax, %rax
	je	.LBB59_7
	movq	%rsi, %rcx
	callq	*%rax
.LBB59_7:
	cmpq	$0, 8(%rdi)
	je	.LBB59_9
	movq	%rsi, %rcx
	callq	mi_free
	nop
.LBB59_9:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end59:
	.seh_handlerdata
	.section	.text$unlikely,"xr",one_only,_RNvNtCs98fvGvYc57G_10rayon_core4join23join_recover_from_panic,unique,60
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvNtCs98fvGvYc57G_10rayon_core4join23join_recover_from_panic,unique,26
	.p2align	2, 0x0
$cppxdata$_RNvNtCs98fvGvYc57G_10rayon_core4join23join_recover_from_panic:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNvNtCs98fvGvYc57G_10rayon_core4join23join_recover_from_panic@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RNvNtCs98fvGvYc57G_10rayon_core4join23join_recover_from_panic@IMGREL
	.long	56
	.long	0
	.long	1
$stateUnwindMap$_RNvNtCs98fvGvYc57G_10rayon_core4join23join_recover_from_panic:
	.long	-1
	.long	"?dtor$4@?0?_RNvNtCs98fvGvYc57G_10rayon_core4join23join_recover_from_panic@4HA"@IMGREL
$ip2state$_RNvNtCs98fvGvYc57G_10rayon_core4join23join_recover_from_panic:
	.long	.Lfunc_begin59@IMGREL
	.long	-1
	.long	.Ltmp194@IMGREL
	.long	0
	.long	.Ltmp193@IMGREL
	.long	-1
	.section	.text$unlikely,"xr",one_only,_RNvNtCs98fvGvYc57G_10rayon_core4join23join_recover_from_panic,unique,60

	.def	_RNvNtCs98fvGvYc57G_10rayon_core6unwind16resume_unwinding;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNtCs98fvGvYc57G_10rayon_core6unwind16resume_unwinding,unique,61
	.globl	_RNvNtCs98fvGvYc57G_10rayon_core6unwind16resume_unwinding
	.p2align	4
_RNvNtCs98fvGvYc57G_10rayon_core6unwind16resume_unwinding:
.Lfunc_begin60:
.seh_proc _RNvNtCs98fvGvYc57G_10rayon_core6unwind16resume_unwinding
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	callq	_RNvNtCse0R8cuyqEa_3std5panic13resume_unwind
	ud2
.Lfunc_end60:
	.seh_endproc

	.def	_RNvNtCs98fvGvYc57G_10rayon_core8registry15global_registry;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvNtCs98fvGvYc57G_10rayon_core8registry15global_registry,unique,62
	.globl	_RNvNtCs98fvGvYc57G_10rayon_core8registry15global_registry
	.p2align	4
_RNvNtCs98fvGvYc57G_10rayon_core8registry15global_registry:
.Lfunc_begin61:
.seh_proc _RNvNtCs98fvGvYc57G_10rayon_core8registry15global_registry
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$88, %rsp
	.seh_stackalloc 88
	leaq	80(%rsp), %rbp
	.seh_setframe %rbp, 80
	.seh_endprologue
	movq	$-2, (%rbp)
	movq	$0, -16(%rbp)
	movl	_RNvNtCs98fvGvYc57G_10rayon_core8registry16THE_REGISTRY_SET(%rip), %eax
	testl	%eax, %eax
	jne	.LBB61_9
.LBB61_1:
	movq	-16(%rbp), %rcx
	movq	-8(%rbp), %rdx
	cmpq	$-1, %rcx
	je	.LBB61_8
	cmpq	$0, _RNvNtCs98fvGvYc57G_10rayon_core8registry12THE_REGISTRY(%rip)
	je	.LBB61_10
	leaq	_RNvNtCs98fvGvYc57G_10rayon_core8registry12THE_REGISTRY(%rip), %rax
	cmpq	$2, %rcx
	jb	.LBB61_7
	movl	%edx, %ecx
	andl	$3, %ecx
	leal	-2(%rcx), %r8d
	cmpl	$2, %r8d
	jb	.LBB61_7
	testq	%rcx, %rcx
	je	.LBB61_7
	movq	%rax, %rsi
	leaq	-1(%rdx), %rcx
	callq	*23(%rdx)
	movq	%rsi, %rax
.LBB61_7:
	.seh_startepilogue
	addq	$88, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB61_8:
	movq	%rdx, %rax
	.seh_startepilogue
	addq	$88, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB61_9:
	leaq	-16(%rbp), %rax
	movq	%rax, -24(%rbp)
	leaq	-24(%rbp), %rax
	movq	%rax, -32(%rbp)
.Ltmp196:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.11.llvm.17002324475202138184(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	_RNvNtCs98fvGvYc57G_10rayon_core8registry16THE_REGISTRY_SET(%rip), %rcx
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.5.llvm.17002324475202138184(%rip), %r9
	leaq	-32(%rbp), %r8
	xorl	%edx, %edx
	callq	_RNvMs0_NtNtNtNtCse0R8cuyqEa_3std3sys4sync4once5futexNtB5_4Once4call
	nop
.Ltmp197:
	jmp	.LBB61_1
.LBB61_10:
	movq	%rcx, -16(%rbp)
	movq	%rdx, -8(%rbp)
.Ltmp198:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.52.llvm.17002324475202138184(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.51.llvm.17002324475202138184(%rip), %rcx
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.29.llvm.17002324475202138184(%rip), %r9
	leaq	-16(%rbp), %r8
	movl	$48, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core6result13unwrap_failed
	nop
.Ltmp199:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvNtCs98fvGvYc57G_10rayon_core8registry15global_registry@IMGREL
	.section	.text,"xr",one_only,_RNvNtCs98fvGvYc57G_10rayon_core8registry15global_registry,unique,62
	.seh_endproc
	.def	"?dtor$12@?0?_RNvNtCs98fvGvYc57G_10rayon_core8registry15global_registry@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$12@?0?_RNvNtCs98fvGvYc57G_10rayon_core8registry15global_registry@4HA":
.seh_proc "?dtor$12@?0?_RNvNtCs98fvGvYc57G_10rayon_core8registry15global_registry@4HA"
.LBB61_12:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	80(%rdx), %rbp
	.seh_endprologue
	cmpl	$2, -16(%rbp)
	jne	.LBB61_16
	movq	-8(%rbp), %rax
	movl	%eax, %ecx
	andl	$3, %ecx
	leal	-2(%rcx), %edx
	cmpl	$2, %edx
	jb	.LBB61_16
	testq	%rcx, %rcx
	je	.LBB61_16
	leaq	-1(%rax), %rcx
	callq	*23(%rax)
	nop
.LBB61_16:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvNtCs98fvGvYc57G_10rayon_core8registry15global_registry,unique,62
	.seh_endproc
	.def	"?dtor$17@?0?_RNvNtCs98fvGvYc57G_10rayon_core8registry15global_registry@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$17@?0?_RNvNtCs98fvGvYc57G_10rayon_core8registry15global_registry@4HA":
.seh_proc "?dtor$17@?0?_RNvNtCs98fvGvYc57G_10rayon_core8registry15global_registry@4HA"
.LBB61_17:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	80(%rdx), %rbp
	.seh_endprologue
	cmpl	$2, -16(%rbp)
	jb	.LBB61_21
	movq	-8(%rbp), %rax
	movl	%eax, %ecx
	andl	$3, %ecx
	leal	-2(%rcx), %edx
	cmpl	$2, %edx
	jb	.LBB61_21
	testq	%rcx, %rcx
	je	.LBB61_21
	leaq	-1(%rax), %rcx
	callq	*23(%rax)
	nop
.LBB61_21:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end61:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvNtCs98fvGvYc57G_10rayon_core8registry15global_registry,unique,62
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvNtCs98fvGvYc57G_10rayon_core8registry15global_registry,unique,27
	.p2align	2, 0x0
$cppxdata$_RNvNtCs98fvGvYc57G_10rayon_core8registry15global_registry:
	.long	429065506
	.long	2
	.long	$stateUnwindMap$_RNvNtCs98fvGvYc57G_10rayon_core8registry15global_registry@IMGREL
	.long	0
	.long	0
	.long	4
	.long	$ip2state$_RNvNtCs98fvGvYc57G_10rayon_core8registry15global_registry@IMGREL
	.long	80
	.long	0
	.long	1
$stateUnwindMap$_RNvNtCs98fvGvYc57G_10rayon_core8registry15global_registry:
	.long	-1
	.long	"?dtor$12@?0?_RNvNtCs98fvGvYc57G_10rayon_core8registry15global_registry@4HA"@IMGREL
	.long	-1
	.long	"?dtor$17@?0?_RNvNtCs98fvGvYc57G_10rayon_core8registry15global_registry@4HA"@IMGREL
$ip2state$_RNvNtCs98fvGvYc57G_10rayon_core8registry15global_registry:
	.long	.Lfunc_begin61@IMGREL
	.long	-1
	.long	.Ltmp196@IMGREL
	.long	0
	.long	.Ltmp198@IMGREL
	.long	1
	.long	.Ltmp199@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvNtCs98fvGvYc57G_10rayon_core8registry15global_registry,unique,62

	.def	_RNvXNtCs98fvGvYc57G_10rayon_core6unwindNtB2_12AbortIfPanicNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXNtCs98fvGvYc57G_10rayon_core6unwindNtB2_12AbortIfPanicNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop,unique,63
	.globl	_RNvXNtCs98fvGvYc57G_10rayon_core6unwindNtB2_12AbortIfPanicNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop
	.p2align	4
_RNvXNtCs98fvGvYc57G_10rayon_core6unwindNtB2_12AbortIfPanicNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop:
.Lfunc_begin62:
.seh_proc _RNvXNtCs98fvGvYc57G_10rayon_core6unwindNtB2_12AbortIfPanicNtNtNtCs8xEFJqa6dYS_4core3ops4drop4Drop4drop
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.54.llvm.17002324475202138184(%rip), %rcx
	movl	$87, %edx
	callq	_RNvNtNtCse0R8cuyqEa_3std2io5stdio7__eprint
	movl	$7, %ecx
	#APP

	int	$41

	#NO_APP
	ud2
.Lfunc_end62:
	.seh_endproc

	.def	_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn,unique,64
	.globl	_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn
	.p2align	4
_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn:
.Lfunc_begin63:
.seh_proc _RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn
	.seh_handler __CxxFrameHandler3, @unwind, @except
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$472, %rsp
	.seh_stackalloc 472
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	movq	$-2, 336(%rbp)
	cmpq	$-1, 16(%rdx)
	movq	%rdx, 288(%rbp)
	je	.LBB63_4
	movq	32(%rdx), %r15
	testq	%r15, %r15
	jns	.LBB63_5
	xorl	%esi, %esi
.LBB63_3:
	movb	$1, 331(%rbp)
.Ltmp200:
	movq	%rsi, %rcx
	movq	%r15, %rdx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc7raw_vec12handle_error
	nop
.Ltmp201:
	jmp	.LBB63_78
.LBB63_4:
	movq	$-1, %r15
	cmpb	$0, (%rdx)
	movq	%r15, 296(%rbp)
	je	.LBB63_10
.LBB63_8:
	movq	8(%rdx), %rsi
	movq	%r15, 248(%rbp)
	movq	%rdi, 256(%rbp)
	movq	%r15, 264(%rbp)
	movq	$0, 280(%rbp)
	jmp	.LBB63_43
.LBB63_5:
	je	.LBB63_9
	movq	%rdx, %r14
	movq	24(%rdx), %rbx
	movl	$1, %esi
	movl	$1, %edx
	movq	%r15, %rcx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB63_3
	movq	%rax, %rdi
	movq	%rax, %rcx
	movq	%rbx, %rdx
	movq	%r15, %r8
	callq	memcpy
	movq	%r14, %rdx
	cmpb	$0, (%rdx)
	movq	%r15, 296(%rbp)
	jne	.LBB63_8
.LBB63_10:
	movq	%r15, 248(%rbp)
	movq	%rdi, 256(%rbp)
	movq	%r15, 264(%rbp)
	movq	$0, 280(%rbp)
	movq	_RNvNCNvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_unchecked03MIN(%rip), %rsi
	testq	%rsi, %rsi
	je	.LBB63_12
	decq	%rsi
	jmp	.LBB63_43
.LBB63_12:
	movb	$1, 335(%rbp)
	movb	$1, 334(%rbp)
	movb	$1, 333(%rbp)
.Ltmp202:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.19(%rip), %rdx
	leaq	80(%rbp), %rcx
	movl	$14, %r8d
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys3env7windows6getenv
	nop
.Ltmp203:
	movq	80(%rbp), %rax
	cmpq	$-1, %rax
	je	.LBB63_17
	movq	%rax, 320(%rbp)
	movq	88(%rbp), %rdx
	movq	96(%rbp), %r8
.Ltmp204:
	leaq	-96(%rbp), %rcx
	movq	%rdx, 312(%rbp)
	callq	_RNvNtNtCs8xEFJqa6dYS_4core3str8converts9from_utf8
	nop
.Ltmp205:
	cmpl	$1, -96(%rbp)
	movq	296(%rbp), %r15
	jne	.LBB63_18
	movl	$2097152, %esi
	movq	320(%rbp), %r11
	testq	%r11, %r11
	jne	.LBB63_41
	jmp	.LBB63_42
.LBB63_9:
	movl	$1, %edi
	xorl	%r15d, %r15d
	cmpb	$0, (%rdx)
	movq	%r15, 296(%rbp)
	jne	.LBB63_8
	jmp	.LBB63_10
.LBB63_17:
	movl	$2097152, %esi
	movq	296(%rbp), %r15
	jmp	.LBB63_42
.LBB63_18:
	movq	-80(%rbp), %rcx
	testq	%rcx, %rcx
	movq	320(%rbp), %r11
	je	.LBB63_23
	movq	-88(%rbp), %r8
	cmpq	$1, %rcx
	jne	.LBB63_24
	movzbl	(%r8), %eax
	cmpl	$43, %eax
	je	.LBB63_23
	cmpl	$45, %eax
	je	.LBB63_23
	jmp	.LBB63_25
.LBB63_24:
	movzbl	(%r8), %eax
.LBB63_25:
	xorl	%r9d, %r9d
	cmpb	$43, %al
	sete	%r9b
	movq	%rcx, %rdx
	subq	%r9, %rdx
	addq	%r9, %r8
	movq	%r9, %rax
	negq	%rax
	cmpq	$17, %rdx
	jae	.LBB63_30
	testq	%rdx, %rdx
	je	.LBB63_38
	addq	%rax, %rcx
	negq	%rcx
	xorl	%esi, %esi
	xorl	%eax, %eax
.LBB63_28:
	movzbl	(%r8,%rax), %edx
	addl	$-48, %edx
	cmpl	$9, %edx
	ja	.LBB63_39
	leaq	(%rsi,%rsi,4), %r9
	movl	%edx, %edx
	leaq	(%rdx,%r9,2), %rsi
	incq	%rax
	movq	%rcx, %rdx
	addq	%rax, %rdx
	jne	.LBB63_28
	jmp	.LBB63_40
.LBB63_30:
	addq	%rax, %rcx
	negq	%rcx
	xorl	%esi, %esi
	movl	$10, %r9d
	xorl	%r10d, %r10d
.LBB63_31:
	movq	%rcx, %rax
	addq	%r10, %rax
	je	.LBB63_40
	movq	%rsi, %rax
	mulq	%r9
	jo	.LBB63_23
	movq	%rax, %rsi
	movzbl	(%r8,%r10), %edx
	addl	$-48, %edx
	addq	%rdx, %rsi
	setb	%al
	cmpl	$9, %edx
	ja	.LBB63_23
	incq	%r10
	testb	%al, %al
	je	.LBB63_31
.LBB63_23:
	movl	$2097152, %esi
	testq	%r11, %r11
	jne	.LBB63_41
	jmp	.LBB63_42
.LBB63_38:
	xorl	%esi, %esi
	testq	%r11, %r11
	jne	.LBB63_41
	jmp	.LBB63_42
.LBB63_39:
	movl	$2097152, %esi
.LBB63_40:
	testq	%r11, %r11
	je	.LBB63_42
.LBB63_41:
	movq	312(%rbp), %rcx
	callq	mi_free
.LBB63_42:
	leaq	1(%rsi), %rax
	movq	%rax, _RNvNCNvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_unchecked03MIN(%rip)
.LBB63_43:
	movq	_RNvNvMNtNtCse0R8cuyqEa_3std6thread2idNtB4_8ThreadId3new7COUNTER.llvm.18153159449376349941(%rip), %rax
	.p2align	4
.LBB63_44:
	cmpq	$-1, %rax
	je	.LBB63_71
	leaq	1(%rax), %rdi
	lock		cmpxchgq	%rdi, _RNvNvMNtNtCse0R8cuyqEa_3std6thread2idNtB4_8ThreadId3new7COUNTER.llvm.18153159449376349941(%rip)
	jne	.LBB63_44
	cmpq	$-1, %r15
	je	.LBB63_49
	movb	$1, 335(%rbp)
	movb	$1, 334(%rbp)
	movb	$0, 333(%rbp)
.Ltmp206:
	leaq	248(%rbp), %rcx
	callq	_RNvXNtNtNtCse0R8cuyqEa_3std6thread6thread18thread_name_stringNtB2_16ThreadNameStringINtNtCs8xEFJqa6dYS_4core7convert4FromNtNtCsfQUUnEvlYZE_5alloc6string6StringE4from
	nop
.Ltmp207:
	movq	%rax, %rbx
	movq	%rdx, %r14
	jmp	.LBB63_50
.LBB63_49:
	xorl	%ebx, %ebx
.LBB63_50:
	movl	$48, %r8d
	xorl	%edx, %edx
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5alloc7windows18process_heap_alloc
	testq	%rax, %rax
	je	.LBB63_77
	movq	$1, (%rax)
	movq	$1, 8(%rax)
	movq	%rbx, 24(%rax)
	movq	%r14, 32(%rax)
	movq	%rdi, 16(%rax)
	movb	$0, 40(%rax)
	movq	%rax, 320(%rbp)
	movq	%rax, 272(%rbp)
	movb	$1, 330(%rbp)
	movb	$1, 329(%rbp)
.Ltmp208:
	leaq	48(%rbp), %rcx
	leaq	272(%rbp), %rdx
	callq	_RNvNtNtCse0R8cuyqEa_3std6thread9spawnhook15run_spawn_hooks
	nop
.Ltmp209:
	movq	$1, 80(%rbp)
	movq	$1, 88(%rbp)
	xorps	%xmm0, %xmm0
	movups	%xmm0, 96(%rbp)
	movl	$48, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	movq	%rax, 312(%rbp)
	je	.LBB63_72
	movq	%rax, %rbx
	movups	80(%rbp), %xmm0
	movups	96(%rbp), %xmm1
	movups	112(%rbp), %xmm2
	movups	%xmm2, 32(%rax)
	movups	%xmm1, 16(%rax)
	movups	%xmm0, (%rax)
	movq	%rax, 304(%rbp)
	lock		incq	(%rax)
	jle	.LBB63_78
	movq	288(%rbp), %rcx
	movq	96(%rcx), %rax
	movq	%rax, (%rbp)
	movups	80(%rcx), %xmm0
	movaps	%xmm0, -16(%rbp)
	movups	64(%rcx), %xmm0
	movaps	%xmm0, -32(%rbp)
	movups	(%rcx), %xmm0
	movups	16(%rcx), %xmm1
	movups	32(%rcx), %xmm2
	movups	48(%rcx), %xmm3
	movaps	%xmm3, -48(%rbp)
	movaps	%xmm2, -64(%rbp)
	movaps	%xmm1, -80(%rbp)
	movaps	%xmm0, -96(%rbp)
	movups	48(%rbp), %xmm0
	movups	64(%rbp), %xmm1
	movups	%xmm1, 24(%rbp)
	movups	%xmm0, 8(%rbp)
	movq	%rbx, 40(%rbp)
	movq	16(%rbx), %rcx
	testq	%rcx, %rcx
	je	.LBB63_56
	lock		incq	24(%rcx)
	jle	.LBB63_75
.LBB63_56:
	leaq	80(%rbp), %rcx
	leaq	-96(%rbp), %rdx
	movl	$144, %r8d
	callq	memcpy
	movl	$144, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB63_73
	movq	%rax, %rdi
	leaq	-96(%rbp), %rdx
	movl	$144, %r8d
	movq	%rax, %rcx
	callq	memcpy
	movq	320(%rbp), %rax
	lock		incq	(%rax)
	jle	.LBB63_78
	movq	%rax, 80(%rbp)
	movq	%rdi, 88(%rbp)
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.16(%rip), %rax
	movq	%rax, 96(%rbp)
	movl	$24, %ecx
	movl	$8, %edx
	callq	mi_malloc_aligned
	testq	%rax, %rax
	je	.LBB63_74
	movq	96(%rbp), %rcx
	movq	%rcx, 16(%rax)
	movups	80(%rbp), %xmm0
	movups	%xmm0, (%rax)
	movb	$0, 332(%rbp)
.Ltmp212:
	movq	%rsi, %rcx
	movq	%rax, %rdx
	callq	_RNvMNtNtNtCse0R8cuyqEa_3std3sys6thread7windowsNtB2_6Thread3new
	nop
.Ltmp213:
	movq	%rdx, %rsi
	cmpq	$1, %rax
	jne	.LBB63_65
	movq	304(%rbp), %rax
	lock		decq	(%rax)
	jne	.LBB63_63
	#MEMBARRIER
.Ltmp216:
	leaq	304(%rbp), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEE9drop_slowBN_
	nop
.Ltmp217:
.LBB63_63:
	movq	320(%rbp), %rax
	lock		decq	(%rax)
	jne	.LBB63_70
	#MEMBARRIER
	leaq	272(%rbp), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtCse0R8cuyqEa_3std6thread6thread5InnerNtNtBM_5alloc6SystemE9drop_slowBM_
	jmp	.LBB63_70
.LBB63_65:
	movq	304(%rbp), %rax
	movq	320(%rbp), %rdi
	movq	%rdi, 224(%rbp)
	movq	%rax, 232(%rbp)
	movq	%rsi, 240(%rbp)
	movq	%rsi, %rcx
	callq	*__imp_CloseHandle(%rip)
	lock		decq	(%rdi)
	jne	.LBB63_67
	#MEMBARRIER
	leaq	224(%rbp), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtCse0R8cuyqEa_3std6thread6thread5InnerNtNtBM_5alloc6SystemE9drop_slowBM_
.LBB63_67:
	movq	232(%rbp), %rax
	lock		decq	(%rax)
	jne	.LBB63_69
	leaq	232(%rbp), %rcx
	#MEMBARRIER
	movb	$0, 331(%rbp)
.Ltmp214:
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEE9drop_slowBN_
	nop
.Ltmp215:
.LBB63_69:
	xorl	%esi, %esi
.LBB63_70:
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$472, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
.LBB63_71:
	movb	$1, 335(%rbp)
	movb	$1, 334(%rbp)
	movb	$1, 333(%rbp)
.Ltmp226:
	callq	_RNvNvMNtNtCse0R8cuyqEa_3std6thread2idNtB4_8ThreadId3new9exhausted.llvm.18153159449376349941
	nop
.Ltmp227:
	jmp	.LBB63_78
.LBB63_72:
.Ltmp222:
	movl	$8, %ecx
	movl	$48, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp223:
	jmp	.LBB63_78
.LBB63_73:
.Ltmp220:
	movl	$8, %ecx
	movl	$144, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp221:
	jmp	.LBB63_78
.LBB63_74:
.Ltmp218:
	movl	$8, %ecx
	movl	$24, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp219:
	jmp	.LBB63_78
.LBB63_75:
	addq	$16, %rcx
	movb	$1, 332(%rbp)
.Ltmp210:
	callq	_RNvMNtNtCse0R8cuyqEa_3std6thread6scopedNtB2_9ScopeData8overflow.llvm.18153159449376349941
	nop
.Ltmp211:
	jmp	.LBB63_78
.LBB63_77:
.Ltmp224:
	movq	%r14, 312(%rbp)
	movq	%rbx, 320(%rbp)
	movl	$8, %ecx
	movl	$48, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp225:
.LBB63_78:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@IMGREL
	.section	.text,"xr",one_only,_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn,unique,64
	.seh_endproc
	.def	"?dtor$79@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$79@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA":
.seh_proc "?dtor$79@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA"
.LBB63_79:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 320(%rbp)
	je	.LBB63_82
	movq	320(%rbp), %rax
	movb	$0, (%rax)
	cmpq	$0, 312(%rbp)
	je	.LBB63_82
	movq	320(%rbp), %rcx
	callq	mi_free
.LBB63_82:
	movb	$1, 335(%rbp)
	movb	$1, 334(%rbp)
	movb	$0, 333(%rbp)
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn,unique,64
	.seh_endproc
	.def	"?dtor$83@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$83@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA":
.seh_proc "?dtor$83@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA"
.LBB63_83:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 320(%rbp)
	je	.LBB63_85
	movq	312(%rbp), %rcx
	callq	mi_free
.LBB63_85:
	movb	$1, 335(%rbp)
	movb	$1, 334(%rbp)
	movb	$1, 333(%rbp)
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn,unique,64
	.seh_endproc
	.def	"?dtor$86@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$86@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA":
.seh_proc "?dtor$86@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA"
.LBB63_86:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movb	$0, 332(%rbp)
	leaq	80(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9lifecycle10ThreadInitECs98fvGvYc57G_10rayon_core
	movb	$0, 332(%rbp)
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn,unique,64
	.seh_endproc
	.def	"?dtor$87@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$87@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA":
.seh_proc "?dtor$87@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA"
.LBB63_87:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movb	$0, 332(%rbp)
	leaq	80(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_
	movb	$0, 332(%rbp)
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn,unique,64
	.seh_endproc
	.def	"?dtor$88@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$88@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA":
.seh_proc "?dtor$88@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA"
.LBB63_88:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	128(%rdx), %rbp
	.seh_endprologue
	leaq	80(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtCsfQUUnEvlYZE_5alloc4sync8ArcInnerINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEEECs98fvGvYc57G_10rayon_core
	nop
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn,unique,64
	.seh_endproc
	.def	"?dtor$89@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$89@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA":
.seh_proc "?dtor$89@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA"
.LBB63_89:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpb	$0, 332(%rbp)
	je	.LBB63_91
	leaq	-96(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_
.LBB63_91:
	movq	304(%rbp), %rax
	lock		decq	(%rax)
	jne	.LBB63_93
	#MEMBARRIER
	leaq	304(%rbp), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtNtCse0R8cuyqEa_3std6thread9lifecycle6PacketuEE9drop_slowBN_
	nop
.LBB63_93:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn,unique,64
	.seh_endproc
	.def	"?dtor$94@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$94@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA":
.seh_proc "?dtor$94@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA"
.LBB63_94:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpq	$0, 312(%rbp)
	jne	.LBB63_96
	leaq	48(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtNtCse0R8cuyqEa_3std6thread9spawnhook15ChildSpawnHooksECs98fvGvYc57G_10rayon_core
	movb	$1, 330(%rbp)
	movb	$0, 329(%rbp)
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
.LBB63_96:
	movb	$0, 330(%rbp)
	movb	$0, 329(%rbp)
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn,unique,64
	.seh_endproc
	.def	"?dtor$97@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$97@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA":
.seh_proc "?dtor$97@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA"
.LBB63_97:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movzbl	329(%rbp), %ebx
	movzbl	330(%rbp), %esi
	movq	320(%rbp), %rax
	lock		decq	(%rax)
	jne	.LBB63_99
	#MEMBARRIER
	leaq	272(%rbp), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtCse0R8cuyqEa_3std6thread6thread5InnerNtNtBM_5alloc6SystemE9drop_slowBM_
.LBB63_99:
	andb	$1, %sil
	movb	%sil, 335(%rbp)
	andb	$1, %bl
	movb	%bl, 334(%rbp)
	movb	$0, 333(%rbp)
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn,unique,64
	.seh_endproc
	.def	"?dtor$100@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$100@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA":
.seh_proc "?dtor$100@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA"
.LBB63_100:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	128(%rdx), %rbp
	.seh_endprologue
	movzbl	333(%rbp), %ebx
	movzbl	334(%rbp), %esi
	cmpb	$0, 335(%rbp)
	movq	288(%rbp), %rcx
	je	.LBB63_102
	movb	$0, 331(%rbp)
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtBJ_12DefaultSpawnNtBJ_11ThreadSpawn5spawn0EBL_
.LBB63_102:
	testb	$1, %sil
	movq	296(%rbp), %rsi
	je	.LBB63_106
	movq	280(%rbp), %rax
	testq	%rax, %rax
	je	.LBB63_106
	lock		decq	(%rax)
	jne	.LBB63_106
	#MEMBARRIER
	movb	$0, 331(%rbp)
	leaq	280(%rbp), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtNtCse0R8cuyqEa_3std6thread6scoped9ScopeDataE9drop_slowBM_
.LBB63_106:
	testq	%rsi, %rsi
	setg	%al
	testb	%bl, %al
	je	.LBB63_108
	movq	256(%rbp), %rcx
	callq	mi_free
.LBB63_108:
	movb	$0, 331(%rbp)
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn,unique,64
	.seh_endproc
	.def	"?dtor$109@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$109@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA":
.seh_proc "?dtor$109@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA"
.LBB63_109:
	movq	%rdx, 16(%rsp)
	pushq	%rbp
	.seh_pushreg %rbp
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
	subq	$40, %rsp
	.seh_stackalloc 40
	leaq	128(%rdx), %rbp
	.seh_endprologue
	cmpb	$0, 331(%rbp)
	jne	.LBB63_111
.LBB63_110:
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
.LBB63_111:
	movq	288(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtNtCs98fvGvYc57G_10rayon_core8registry13ThreadBuilderEBF_
	jmp	.LBB63_110
.Lfunc_end63:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn,unique,64
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn,unique,28
	.p2align	2, 0x0
$cppxdata$_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn:
	.long	429065506
	.long	10
	.long	$stateUnwindMap$_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@IMGREL
	.long	0
	.long	0
	.long	18
	.long	$ip2state$_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@IMGREL
	.long	464
	.long	0
	.long	1
$stateUnwindMap$_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn:
	.long	-1
	.long	"?dtor$109@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA"@IMGREL
	.long	0
	.long	"?dtor$100@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA"@IMGREL
	.long	1
	.long	"?dtor$97@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA"@IMGREL
	.long	2
	.long	"?dtor$94@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA"@IMGREL
	.long	3
	.long	"?dtor$89@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA"@IMGREL
	.long	4
	.long	"?dtor$86@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA"@IMGREL
	.long	4
	.long	"?dtor$87@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA"@IMGREL
	.long	3
	.long	"?dtor$88@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA"@IMGREL
	.long	1
	.long	"?dtor$79@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA"@IMGREL
	.long	1
	.long	"?dtor$83@?0?_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn@4HA"@IMGREL
$ip2state$_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn:
	.long	.Lfunc_begin63@IMGREL
	.long	-1
	.long	.Ltmp200@IMGREL
	.long	0
	.long	.Ltmp201@IMGREL
	.long	-1
	.long	.Ltmp202@IMGREL
	.long	1
	.long	.Ltmp204@IMGREL
	.long	9
	.long	.Ltmp206@IMGREL
	.long	1
	.long	.Ltmp208@IMGREL
	.long	2
	.long	.Ltmp209@IMGREL
	.long	-1
	.long	.Ltmp212@IMGREL
	.long	4
	.long	.Ltmp216@IMGREL
	.long	3
	.long	.Ltmp214@IMGREL
	.long	0
	.long	.Ltmp226@IMGREL
	.long	1
	.long	.Ltmp222@IMGREL
	.long	7
	.long	.Ltmp220@IMGREL
	.long	6
	.long	.Ltmp218@IMGREL
	.long	5
	.long	.Ltmp210@IMGREL
	.long	4
	.long	.Ltmp224@IMGREL
	.long	8
	.long	.Ltmp225@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12DefaultSpawnNtB5_11ThreadSpawn5spawn,unique,64

	.def	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRNtCs98fvGvYc57G_10rayon_core9ErrorKindNtB6_5Debug3fmtBy_;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRNtCs98fvGvYc57G_10rayon_core9ErrorKindNtB6_5Debug3fmtBy_,unique,65
	.p2align	4
_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRNtCs98fvGvYc57G_10rayon_core9ErrorKindNtB6_5Debug3fmtBy_:
.Lfunc_begin64:
.seh_proc _RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRNtCs98fvGvYc57G_10rayon_core9ErrorKindNtB6_5Debug3fmtBy_
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
	subq	$88, %rsp
	.seh_stackalloc 88
	.seh_endprologue
	movq	%rdx, %rdi
	movq	(%rcx), %r14
	movq	(%r14), %rax
	testq	%rax, %rax
	je	.LBB64_3
	cmpl	$1, %eax
	jne	.LBB64_5
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	movq	24(%rax), %rax
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.126(%rip), %rdx
	movl	$26, %r8d
	jmp	.LBB64_4
.LBB64_3:
	movq	(%rdi), %rcx
	movq	8(%rdi), %rax
	movq	24(%rax), %rax
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.125(%rip), %rdx
	movl	$28, %r8d
.LBB64_4:
	.seh_startepilogue
	addq	$88, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r14
	popq	%r15
	.seh_endepilogue
	rex64 jmpq	*%rax
.LBB64_5:
	movq	(%rdi), %rsi
	movq	8(%rdi), %r12
	movq	24(%r12), %r15
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.128(%rip), %rdx
	movl	$7, %r8d
	movq	%rsi, %rcx
	callq	*%r15
	movb	$1, %bl
	testb	%al, %al
	je	.LBB64_6
.LBB64_14:
	movl	%ebx, %eax
	.seh_startepilogue
	addq	$88, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r14
	popq	%r15
	.seh_endepilogue
	retq
.LBB64_6:
	addq	$8, %r14
	testb	$-128, 18(%rdi)
	jne	.LBB64_10
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.39.llvm.17490583796818522722(%rip), %rdx
	movl	$1, %r8d
	movq	%rsi, %rcx
	callq	*%r15
	testb	%al, %al
	jne	.LBB64_14
	movq	%r14, %rcx
	movq	%rdi, %rdx
	callq	_RNvXs2_NtNtCs8xEFJqa6dYS_4core2io5errorNtNtB5_4repr4ReprNtNtB9_3fmt5Debug3fmt
	testb	%al, %al
	jne	.LBB64_14
	movq	(%rdi), %rsi
	movq	8(%rdi), %rax
	movq	24(%rax), %r15
	jmp	.LBB64_13
.LBB64_10:
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.40.llvm.17490583796818522722(%rip), %rdx
	movl	$2, %r8d
	movq	%rsi, %rcx
	callq	*%r15
	testb	%al, %al
	jne	.LBB64_14
	movb	$1, 39(%rsp)
	movq	%rsi, 64(%rsp)
	movq	%r12, 72(%rsp)
	leaq	39(%rsp), %rax
	movq	%rax, 80(%rsp)
	movq	16(%rdi), %rax
	movq	%rax, 56(%rsp)
	leaq	64(%rsp), %rax
	movq	%rax, 40(%rsp)
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.99.llvm.17490583796818522722(%rip), %rax
	movq	%rax, 48(%rsp)
	leaq	40(%rsp), %rdx
	movq	%r14, %rcx
	callq	_RNvXs2_NtNtCs8xEFJqa6dYS_4core2io5errorNtNtB5_4repr4ReprNtNtB9_3fmt5Debug3fmt
	testb	%al, %al
	jne	.LBB64_14
	movq	40(%rsp), %rcx
	movq	48(%rsp), %rax
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.38.llvm.17490583796818522722(%rip), %rdx
	movl	$2, %r8d
	callq	*24(%rax)
	testb	%al, %al
	jne	.LBB64_14
.LBB64_13:
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.57.llvm.17490583796818522722(%rip), %rdx
	movl	$1, %r8d
	movq	%rsi, %rcx
	callq	*%r15
	movl	%eax, %ebx
	jmp	.LBB64_14
.Lfunc_end64:
	.seh_endproc

	.def	_RNvXs4_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatchNtB5_5Latch3set;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs4_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatchNtB5_5Latch3set,unique,66
	.p2align	4
_RNvXs4_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatchNtB5_5Latch3set:
.Lfunc_begin65:
.seh_proc _RNvXs4_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatchNtB5_5Latch3set
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
	movq	%rcx, %rdi
	leaq	4(%rcx), %rsi
	movb	$1, %cl
	xorl	%eax, %eax
	lock		cmpxchgb	%cl, 4(%rdi)
	jne	.LBB65_1
	movq	_RNvNtNtCse0R8cuyqEa_3std9panicking11panic_count18GLOBAL_PANIC_COUNT(%rip), %rax
	shlq	%rax
	testq	%rax, %rax
	jne	.LBB65_4
.LBB65_3:
	xorl	%ebx, %ebx
	movzbl	5(%rdi), %eax
	testb	%al, %al
	jne	.LBB65_6
.LBB65_8:
	movb	$1, 6(%rdi)
	lock		incl	(%rdi)
	movq	%rdi, %rcx
	callq	*__imp_WakeByAddressAll(%rip)
	testb	%bl, %bl
	jne	.LBB65_12
	movq	_RNvNtNtCse0R8cuyqEa_3std9panicking11panic_count18GLOBAL_PANIC_COUNT(%rip), %rax
	shlq	%rax
	testq	%rax, %rax
	jne	.LBB65_10
.LBB65_12:
	xorl	%eax, %eax
	xchgb	%al, (%rsi)
	cmpb	$2, %al
	je	.LBB65_15
	.seh_startepilogue
	addq	$72, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.LBB65_1:
	movq	%rsi, %rcx
	callq	_RNvMNtNtNtNtCse0R8cuyqEa_3std3sys4sync5mutex5futexNtB2_5Mutex14lock_contended
	movq	_RNvNtNtCse0R8cuyqEa_3std9panicking11panic_count18GLOBAL_PANIC_COUNT(%rip), %rax
	shlq	%rax
	testq	%rax, %rax
	je	.LBB65_3
.LBB65_4:
	callq	_RNvNtNtCse0R8cuyqEa_3std9panicking11panic_count17is_zero_slow_path
	movl	%eax, %ebx
	xorb	$1, %bl
	movzbl	5(%rdi), %eax
	testb	%al, %al
	je	.LBB65_8
.LBB65_6:
	movq	%rsi, -16(%rbp)
	movb	%bl, -8(%rbp)
.Ltmp228:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.78(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.28.llvm.17002324475202138184(%rip), %rcx
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.27.llvm.17002324475202138184(%rip), %r9
	leaq	-16(%rbp), %r8
	movl	$43, %edx
	callq	_RNvNtCs8xEFJqa6dYS_4core6result13unwrap_failed
	nop
.Ltmp229:
	ud2
.LBB65_15:
	movq	%rsi, %rcx
	.seh_startepilogue
	addq	$72, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	rex64 jmpq	*__imp_WakeByAddressSingle(%rip)
.LBB65_10:
	callq	_RNvNtNtCse0R8cuyqEa_3std9panicking11panic_count17is_zero_slow_path
	testb	%al, %al
	jne	.LBB65_12
	movb	$1, 5(%rdi)
	jmp	.LBB65_12
	.seh_handlerdata
	.long	$cppxdata$_RNvXs4_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatchNtB5_5Latch3set@IMGREL
	.section	.text,"xr",one_only,_RNvXs4_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatchNtB5_5Latch3set,unique,66
	.seh_endproc
	.def	"?dtor$14@?0?_RNvXs4_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatchNtB5_5Latch3set@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$14@?0?_RNvXs4_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatchNtB5_5Latch3set@4HA":
.seh_proc "?dtor$14@?0?_RNvXs4_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatchNtB5_5Latch3set@4HA"
.LBB65_14:
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
	leaq	-16(%rbp), %rcx
	callq	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCse0R8cuyqEa_3std4sync6poison11PoisonErrorINtNtBE_5mutex10MutexGuardbEEECs98fvGvYc57G_10rayon_core.llvm.17002324475202138184
	nop
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end65:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs4_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatchNtB5_5Latch3set,unique,66
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvXs4_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatchNtB5_5Latch3set,unique,29
	.p2align	2, 0x0
$cppxdata$_RNvXs4_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatchNtB5_5Latch3set:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNvXs4_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatchNtB5_5Latch3set@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RNvXs4_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatchNtB5_5Latch3set@IMGREL
	.long	64
	.long	0
	.long	1
$stateUnwindMap$_RNvXs4_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatchNtB5_5Latch3set:
	.long	-1
	.long	"?dtor$14@?0?_RNvXs4_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatchNtB5_5Latch3set@4HA"@IMGREL
$ip2state$_RNvXs4_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatchNtB5_5Latch3set:
	.long	.Lfunc_begin65@IMGREL
	.long	-1
	.long	.Ltmp228@IMGREL
	.long	0
	.long	.Ltmp229@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvXs4_NtCs98fvGvYc57G_10rayon_core5latchNtB5_9LockLatchNtB5_5Latch3set,unique,66

	.def	_RNvXs6_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThreadINtNtCs8xEFJqa6dYS_4core7convert4FromNtB5_13ThreadBuilderE4from;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs6_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThreadINtNtCs8xEFJqa6dYS_4core7convert4FromNtB5_13ThreadBuilderE4from,unique,67
	.globl	_RNvXs6_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThreadINtNtCs8xEFJqa6dYS_4core7convert4FromNtB5_13ThreadBuilderE4from
	.p2align	4
_RNvXs6_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThreadINtNtCs8xEFJqa6dYS_4core7convert4FromNtB5_13ThreadBuilderE4from:
.Lfunc_begin66:
.seh_proc _RNvXs6_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThreadINtNtCs8xEFJqa6dYS_4core7convert4FromNtB5_13ThreadBuilderE4from
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
	subq	$120, %rsp
	.seh_stackalloc 120
	leaq	112(%rsp), %rbp
	.seh_setframe %rbp, 112
	.seh_endprologue
	movq	$-2, (%rbp)
	movq	%rdx, %rdi
	movq	%rcx, %rsi
	movups	56(%rdx), %xmm0
	movups	72(%rdx), %xmm1
	movaps	%xmm1, -64(%rbp)
	movaps	%xmm0, -80(%rbp)
	movq	40(%rdx), %rax
	movzbl	48(%rdx), %ebx
	movq	%rax, -8(%rbp)
	movq	%rax, -48(%rbp)
	movb	%bl, -40(%rbp)
	movl	$1520, %ecx
	movl	$8, %edx
	callq	mi_zalloc_aligned
	testq	%rax, %rax
	movq	%rdi, -16(%rbp)
	je	.LBB66_1
	leaq	56(%rdi), %rcx
	movq	%rcx, -24(%rbp)
	movq	96(%rdi), %rcx
	movq	%rcx, -32(%rbp)
	movabsq	$8387220255154660723, %r8
	movabsq	$7816392313619706465, %r9
	movabsq	$-2389207006547353658, %r10
	movabsq	$-6481707427168261424, %r11
	movabsq	$-2011800112340241627, %rdi
	movabsq	$576460752303423488, %r14
	.p2align	4
.LBB66_13:
	movl	$1, %edx
	lock		xaddq	%rdx, _RNvNvMs9_NtCs98fvGvYc57G_10rayon_core8registryNtB7_14XorShift64Star3new7COUNTER(%rip)
	movq	%rdx, %r15
	xorq	%r8, %r15
	movq	%r15, %rcx
	rolq	$16, %rcx
	leaq	(%r15,%r9), %r12
	xorq	%r12, %rcx
	leaq	(%rcx,%r10), %r13
	xorq	%r13, %rdx
	addq	%r11, %r15
	movq	%r15, %r12
	rolq	$32, %r12
	rolq	$21, %rcx
	xorq	%rdi, %r15
	xorq	%r14, %r13
	xorq	%rcx, %r13
	addq	%r15, %rdx
	rolq	$13, %r15
	addq	%r13, %r12
	xorq	%rdx, %r15
	rolq	$16, %r13
	xorq	%r12, %r13
	rolq	$32, %rdx
	addq	%r15, %r12
	addq	%r13, %rdx
	rolq	$17, %r15
	xorq	%r12, %r15
	rolq	$21, %r13
	rolq	$32, %r12
	xorq	%rdx, %r13
	xorq	%r14, %rdx
	xorq	$255, %r12
	addq	%r15, %rdx
	addq	%r13, %r12
	rolq	$13, %r15
	xorq	%rdx, %r15
	rolq	$16, %r13
	rolq	$32, %rdx
	xorq	%r12, %r13
	addq	%r15, %r12
	rolq	$17, %r15
	addq	%r13, %rdx
	xorq	%r12, %r15
	rolq	$21, %r13
	xorq	%rdx, %r13
	rolq	$32, %r12
	addq	%r15, %rdx
	addq	%r13, %r12
	rolq	$13, %r15
	xorq	%rdx, %r15
	rolq	$16, %r13
	rolq	$32, %rdx
	xorq	%r12, %r13
	addq	%r15, %r12
	rolq	$17, %r15
	addq	%r13, %rdx
	xorq	%r12, %r15
	rolq	$21, %r13
	xorq	%rdx, %r13
	rolq	$32, %r12
	addq	%r15, %rdx
	addq	%r13, %r12
	rolq	$13, %r15
	xorq	%rdx, %r15
	rolq	$16, %r13
	xorq	%r12, %r13
	addq	%r15, %r12
	rolq	$17, %r15
	rolq	$21, %r13
	movq	%r12, %rdx
	rolq	$32, %rdx
	xorq	%r15, %rdx
	xorq	%r13, %rdx
	cmpq	%r12, %rdx
	je	.LBB66_13
	xorq	%r12, %rdx
	movq	-16(%rbp), %r8
	movq	88(%r8), %rcx
	movq	-24(%rbp), %r9
	movups	(%r9), %xmm0
	movups	16(%r9), %xmm1
	movups	%xmm1, 296(%rsi)
	movups	%xmm0, 280(%rsi)
	movq	-8(%rbp), %r9
	movq	%r9, 312(%rsi)
	movb	%bl, 320(%rsi)
	movq	$0, (%rsi)
	movq	%rax, 8(%rsi)
	movq	$0, 128(%rsi)
	movq	%rax, 136(%rsi)
	movq	-32(%rbp), %rax
	movq	%rax, 256(%rsi)
	movq	%rdx, 264(%rsi)
	movq	%rcx, 272(%rsi)
	movq	16(%r8), %rax
	cmpq	$-1, %rax
	je	.LBB66_17
	testq	%rax, %rax
	je	.LBB66_17
	movq	24(%r8), %rcx
	callq	mi_free
.LBB66_17:
	movq	%rsi, %rax
	.seh_startepilogue
	addq	$120, %rsp
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
.LBB66_1:
.Ltmp230:
	movl	$8, %ecx
	movl	$1520, %edx
	callq	_RNvNtCsfQUUnEvlYZE_5alloc5alloc18handle_alloc_error
	nop
.Ltmp231:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvXs6_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThreadINtNtCs8xEFJqa6dYS_4core7convert4FromNtB5_13ThreadBuilderE4from@IMGREL
	.section	.text,"xr",one_only,_RNvXs6_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThreadINtNtCs8xEFJqa6dYS_4core7convert4FromNtB5_13ThreadBuilderE4from,unique,67
	.seh_endproc
	.def	"?dtor$3@?0?_RNvXs6_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThreadINtNtCs8xEFJqa6dYS_4core7convert4FromNtB5_13ThreadBuilderE4from@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$3@?0?_RNvXs6_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThreadINtNtCs8xEFJqa6dYS_4core7convert4FromNtB5_13ThreadBuilderE4from@4HA":
.seh_proc "?dtor$3@?0?_RNvXs6_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThreadINtNtCs8xEFJqa6dYS_4core7convert4FromNtB5_13ThreadBuilderE4from@4HA"
.LBB66_3:
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
	leaq	112(%rdx), %rbp
	.seh_endprologue
	movq	-8(%rbp), %rax
	lock		decq	(%rax)
	je	.LBB66_4
	movq	-80(%rbp), %rax
	lock		decq	(%rax)
	movq	-16(%rbp), %rsi
	je	.LBB66_6
.LBB66_7:
	cmpq	$0, 16(%rsi)
	jle	.LBB66_9
.LBB66_8:
	movq	24(%rsi), %rcx
	callq	mi_free
.LBB66_9:
	movq	88(%rsi), %rax
	lock		decq	(%rax)
	jne	.LBB66_11
	addq	$88, %rsi
	#MEMBARRIER
	movq	%rsi, %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcNtNtCs98fvGvYc57G_10rayon_core8registry8RegistryE9drop_slowBK_
	nop
.LBB66_11:
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
.LBB66_4:
	#MEMBARRIER
	leaq	-48(%rbp), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
	movq	-80(%rbp), %rax
	lock		decq	(%rax)
	movq	-16(%rbp), %rsi
	jne	.LBB66_7
.LBB66_6:
	#MEMBARRIER
	leaq	-80(%rbp), %rcx
	callq	_RNvMsn_NtCsfQUUnEvlYZE_5alloc4syncINtB5_3ArcINtNtCs5jdj61sQu57_15crossbeam_utils12cache_padded11CachePaddedINtNtCslOUiAINmber_15crossbeam_deque5deque5InnerNtNtCs98fvGvYc57G_10rayon_core3job6JobRefEEE9drop_slowB2x_
	cmpq	$0, 16(%rsi)
	jg	.LBB66_8
	jmp	.LBB66_9
.Lfunc_end66:
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvXs6_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThreadINtNtCs8xEFJqa6dYS_4core7convert4FromNtB5_13ThreadBuilderE4from,unique,67
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvXs6_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThreadINtNtCs8xEFJqa6dYS_4core7convert4FromNtB5_13ThreadBuilderE4from,unique,30
	.p2align	2, 0x0
$cppxdata$_RNvXs6_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThreadINtNtCs8xEFJqa6dYS_4core7convert4FromNtB5_13ThreadBuilderE4from:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNvXs6_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThreadINtNtCs8xEFJqa6dYS_4core7convert4FromNtB5_13ThreadBuilderE4from@IMGREL
	.long	0
	.long	0
	.long	3
	.long	$ip2state$_RNvXs6_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThreadINtNtCs8xEFJqa6dYS_4core7convert4FromNtB5_13ThreadBuilderE4from@IMGREL
	.long	112
	.long	0
	.long	1
$stateUnwindMap$_RNvXs6_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThreadINtNtCs8xEFJqa6dYS_4core7convert4FromNtB5_13ThreadBuilderE4from:
	.long	-1
	.long	"?dtor$3@?0?_RNvXs6_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThreadINtNtCs8xEFJqa6dYS_4core7convert4FromNtB5_13ThreadBuilderE4from@4HA"@IMGREL
$ip2state$_RNvXs6_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThreadINtNtCs8xEFJqa6dYS_4core7convert4FromNtB5_13ThreadBuilderE4from:
	.long	.Lfunc_begin66@IMGREL
	.long	-1
	.long	.Ltmp230@IMGREL
	.long	0
	.long	.Ltmp231@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvXs6_NtCs98fvGvYc57G_10rayon_core8registryNtB5_12WorkerThreadINtNtCs8xEFJqa6dYS_4core7convert4FromNtB5_13ThreadBuilderE4from,unique,67

	.def	_RNvXs_NtNtCse0R8cuyqEa_3std4sync6poisonINtB4_11PoisonErrorINtNtB4_5mutex10MutexGuardbEENtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmtCs98fvGvYc57G_10rayon_core.llvm.17002324475202138184;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXs_NtNtCse0R8cuyqEa_3std4sync6poisonINtB4_11PoisonErrorINtNtB4_5mutex10MutexGuardbEENtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmtCs98fvGvYc57G_10rayon_core.llvm.17002324475202138184,unique,68
	.globl	_RNvXs_NtNtCse0R8cuyqEa_3std4sync6poisonINtB4_11PoisonErrorINtNtB4_5mutex10MutexGuardbEENtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmtCs98fvGvYc57G_10rayon_core.llvm.17002324475202138184
	.p2align	4
_RNvXs_NtNtCse0R8cuyqEa_3std4sync6poisonINtB4_11PoisonErrorINtNtB4_5mutex10MutexGuardbEENtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmtCs98fvGvYc57G_10rayon_core.llvm.17002324475202138184:
.Lfunc_begin67:
.seh_proc _RNvXs_NtNtCse0R8cuyqEa_3std4sync6poisonINtB4_11PoisonErrorINtNtB4_5mutex10MutexGuardbEENtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmtCs98fvGvYc57G_10rayon_core.llvm.17002324475202138184
	pushq	%rsi
	.seh_pushreg %rsi
	pushq	%rdi
	.seh_pushreg %rdi
	subq	$40, %rsp
	.seh_stackalloc 40
	.seh_endprologue
	movq	(%rdx), %rsi
	movq	8(%rdx), %rax
	movq	24(%rax), %rax
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.121(%rip), %rdx
	movl	$11, %r8d
	movq	%rsi, %rcx
	movq	%rax, %rdi
	callq	*%rax
	testb	%al, %al
	je	.LBB67_2
	movb	$1, %al
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	retq
.LBB67_2:
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.51.llvm.17490583796818522722(%rip), %rdx
	movl	$7, %r8d
	movq	%rsi, %rcx
	movq	%rdi, %rax
	.seh_startepilogue
	addq	$40, %rsp
	popq	%rdi
	popq	%rsi
	.seh_endepilogue
	rex64 jmpq	*%rax
.Lfunc_end67:
	.seh_endproc

	.def	_RNvXsb_Cs98fvGvYc57G_10rayon_coreNtB5_20ThreadPoolBuildErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt.llvm.17002324475202138184;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvXsb_Cs98fvGvYc57G_10rayon_coreNtB5_20ThreadPoolBuildErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt.llvm.17002324475202138184,unique,69
	.globl	_RNvXsb_Cs98fvGvYc57G_10rayon_coreNtB5_20ThreadPoolBuildErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt.llvm.17002324475202138184
	.p2align	4
_RNvXsb_Cs98fvGvYc57G_10rayon_coreNtB5_20ThreadPoolBuildErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt.llvm.17002324475202138184:
.Lfunc_begin68:
.seh_proc _RNvXsb_Cs98fvGvYc57G_10rayon_coreNtB5_20ThreadPoolBuildErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt.llvm.17002324475202138184
	pushq	%rsi
	.seh_pushreg %rsi
	subq	$64, %rsp
	.seh_stackalloc 64
	.seh_endprologue
	movq	%rdx, %rsi
	movq	%rcx, 56(%rsp)
	movq	(%rdx), %rcx
	movq	8(%rdx), %rax
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.123(%rip), %rdx
	movl	$20, %r8d
	callq	*24(%rax)
	movq	%rsi, 40(%rsp)
	movb	%al, 48(%rsp)
	movb	$0, 49(%rsp)
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.122(%rip), %rax
	movq	%rax, 32(%rsp)
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.124(%rip), %rdx
	leaq	40(%rsp), %rcx
	leaq	56(%rsp), %r9
	movl	$4, %r8d
	callq	_RNvMs1_NtNtCs8xEFJqa6dYS_4core3fmt8buildersNtB5_11DebugStruct5field
	movzbl	48(%rsp), %ecx
	movzbl	49(%rsp), %eax
	movl	%eax, %edx
	notb	%dl
	orb	%cl, %dl
	testb	$1, %dl
	je	.LBB68_3
	orb	%cl, %al
	andb	$1, %al
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.LBB68_3:
	movq	40(%rsp), %rax
	testb	$-128, 18(%rax)
	jne	.LBB68_5
	movq	(%rax), %rcx
	movq	8(%rax), %rax
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.94.llvm.17490583796818522722(%rip), %rdx
	movl	$2, %r8d
	jmp	.LBB68_6
.LBB68_5:
	movq	(%rax), %rcx
	movq	8(%rax), %rax
	leaq	anon.1732459c665ba8bd62b57c6c789d589c.54.llvm.17490583796818522722(%rip), %rdx
	movl	$1, %r8d
.LBB68_6:
	callq	*24(%rax)
	andb	$1, %al
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rsi
	.seh_endepilogue
	retq
.Lfunc_end68:
	.seh_endproc

	.def	_RNvYNtNtNtNtCse0R8cuyqEa_3std3sys5stdio7windows6StderrNtNtBa_2io5Write9write_allCs98fvGvYc57G_10rayon_core;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvYNtNtNtNtCse0R8cuyqEa_3std3sys5stdio7windows6StderrNtNtBa_2io5Write9write_allCs98fvGvYc57G_10rayon_core,unique,70
	.p2align	4
_RNvYNtNtNtNtCse0R8cuyqEa_3std3sys5stdio7windows6StderrNtNtBa_2io5Write9write_allCs98fvGvYc57G_10rayon_core:
.Lfunc_begin69:
.seh_proc _RNvYNtNtNtNtCse0R8cuyqEa_3std3sys5stdio7windows6StderrNtNtBa_2io5Write9write_allCs98fvGvYc57G_10rayon_core
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
	subq	$64, %rsp
	.seh_stackalloc 64
	leaq	64(%rsp), %rbp
	.seh_setframe %rbp, 64
	.seh_endprologue
	movq	$-2, -8(%rbp)
	movq	%r8, %rsi
	movq	%rdx, %rdi
	movq	%rcx, %rbx
	leaq	.LJTI69_0(%rip), %r14
	movl	$255, %r12d
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.146(%rip), %r15
	jmp	.LBB69_1
	.p2align	4
.LBB69_5:
	movq	%rdx, %rax
	shrq	$32, %rax
	cmpq	$43, %rax
	cmovael	%r12d, %eax
	cmpb	$35, %al
	jne	.LBB69_3
.LBB69_1:
	testq	%rsi, %rsi
	je	.LBB69_2
	movl	$-12, %ecx
	movq	%rdi, %rdx
	movq	%rsi, %r8
	movq	%rbx, %r9
	callq	_RNvNtNtNtCse0R8cuyqEa_3std3sys5stdio7windows5write.llvm.18153159449376349941
	testb	$1, %al
	je	.LBB69_10
	movl	%edx, %ecx
	andl	$3, %ecx
	movslq	(%r14,%rcx,4), %rcx
	addq	%r14, %rcx
	jmpq	*%rcx
.LBB69_6:
	cmpb	$35, 16(%rdx)
	je	.LBB69_1
	jmp	.LBB69_3
	.p2align	4
.LBB69_16:
	movq	%rax, -24(%rbp)
	movq	_RNvNtNtNtCs8xEFJqa6dYS_4core2io5error12os_functions12OS_FUNCTIONS(%rip), %rax
	movq	%rdx, -16(%rbp)
	movq	%rdx, %rcx
	shrq	$32, %rcx
.Ltmp234:
	callq	*16(%rax)
	nop
.Ltmp235:
	testb	%al, %al
	movq	-16(%rbp), %rdx
	jne	.LBB69_1
	jmp	.LBB69_3
	.p2align	4
.LBB69_7:
	cmpb	$35, 31(%rdx)
	jne	.LBB69_3
	movq	%rdx, %rcx
	decq	%rcx
	callq	*23(%rdx)
	jmp	.LBB69_1
.LBB69_10:
	testq	%rdx, %rdx
	je	.LBB69_11
	movq	%rsi, %rcx
	subq	%rdx, %rcx
	jb	.LBB69_13
	addq	%rdx, %rdi
	movq	%rcx, %rsi
	jmp	.LBB69_1
.LBB69_2:
	xorl	%edx, %edx
.LBB69_3:
	movq	%rdx, %rax
	.seh_startepilogue
	addq	$64, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
.LBB69_11:
	movq	%r15, %rdx
	jmp	.LBB69_3
.LBB69_13:
.Ltmp232:
	movq	%rax, -24(%rbp)
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.147(%rip), %r9
	movq	%rdx, -16(%rbp)
	movq	%rdx, %rcx
	movq	%rsi, %rdx
	movq	%rsi, %r8
	callq	_RNvNtNtCs8xEFJqa6dYS_4core5slice5index16slice_index_fail
	nop
.Ltmp233:
	ud2
	.seh_handlerdata
	.long	$cppxdata$_RNvYNtNtNtNtCse0R8cuyqEa_3std3sys5stdio7windows6StderrNtNtBa_2io5Write9write_allCs98fvGvYc57G_10rayon_core@IMGREL
	.section	.text,"xr",one_only,_RNvYNtNtNtNtCse0R8cuyqEa_3std3sys5stdio7windows6StderrNtNtBa_2io5Write9write_allCs98fvGvYc57G_10rayon_core,unique,70
	.seh_endproc
	.def	"?dtor$18@?0?_RNvYNtNtNtNtCse0R8cuyqEa_3std3sys5stdio7windows6StderrNtNtBa_2io5Write9write_allCs98fvGvYc57G_10rayon_core@4HA";
	.scl	3;
	.type	32;
	.endef
	.p2align	4
"?dtor$18@?0?_RNvYNtNtNtNtCse0R8cuyqEa_3std3sys5stdio7windows6StderrNtNtBa_2io5Write9write_allCs98fvGvYc57G_10rayon_core@4HA":
.seh_proc "?dtor$18@?0?_RNvYNtNtNtNtCse0R8cuyqEa_3std3sys5stdio7windows6StderrNtNtBa_2io5Write9write_allCs98fvGvYc57G_10rayon_core@4HA"
.LBB69_18:
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
	subq	$32, %rsp
	.seh_stackalloc 32
	leaq	64(%rdx), %rbp
	.seh_endprologue
	testb	$1, -24(%rbp)
	je	.LBB69_22
	movq	-16(%rbp), %rax
	andl	$3, %eax
	leal	-2(%rax), %ecx
	cmpl	$2, %ecx
	jb	.LBB69_22
	testq	%rax, %rax
	je	.LBB69_22
	movq	-16(%rbp), %rax
	movq	%rax, %rcx
	decq	%rcx
	callq	*23(%rax)
	nop
.LBB69_22:
	.seh_startepilogue
	addq	$32, %rsp
	popq	%rbx
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r14
	popq	%r15
	popq	%rbp
	.seh_endepilogue
	retq
.Lfunc_end69:
	.section	.rdata,"dr",associative,_RNvYNtNtNtNtCse0R8cuyqEa_3std3sys5stdio7windows6StderrNtNtBa_2io5Write9write_allCs98fvGvYc57G_10rayon_core,unique,71
	.p2align	2, 0x0
.LJTI69_0:
	.long	.LBB69_6-.LJTI69_0
	.long	.LBB69_7-.LJTI69_0
	.long	.LBB69_16-.LJTI69_0
	.long	.LBB69_5-.LJTI69_0
	.seh_handlerdata
	.section	.text,"xr",one_only,_RNvYNtNtNtNtCse0R8cuyqEa_3std3sys5stdio7windows6StderrNtNtBa_2io5Write9write_allCs98fvGvYc57G_10rayon_core,unique,70
	.seh_endproc
	.section	.xdata,"dr",associative,_RNvYNtNtNtNtCse0R8cuyqEa_3std3sys5stdio7windows6StderrNtNtBa_2io5Write9write_allCs98fvGvYc57G_10rayon_core,unique,31
	.p2align	2, 0x0
$cppxdata$_RNvYNtNtNtNtCse0R8cuyqEa_3std3sys5stdio7windows6StderrNtNtBa_2io5Write9write_allCs98fvGvYc57G_10rayon_core:
	.long	429065506
	.long	1
	.long	$stateUnwindMap$_RNvYNtNtNtNtCse0R8cuyqEa_3std3sys5stdio7windows6StderrNtNtBa_2io5Write9write_allCs98fvGvYc57G_10rayon_core@IMGREL
	.long	0
	.long	0
	.long	5
	.long	$ip2state$_RNvYNtNtNtNtCse0R8cuyqEa_3std3sys5stdio7windows6StderrNtNtBa_2io5Write9write_allCs98fvGvYc57G_10rayon_core@IMGREL
	.long	56
	.long	0
	.long	1
$stateUnwindMap$_RNvYNtNtNtNtCse0R8cuyqEa_3std3sys5stdio7windows6StderrNtNtBa_2io5Write9write_allCs98fvGvYc57G_10rayon_core:
	.long	-1
	.long	"?dtor$18@?0?_RNvYNtNtNtNtCse0R8cuyqEa_3std3sys5stdio7windows6StderrNtNtBa_2io5Write9write_allCs98fvGvYc57G_10rayon_core@4HA"@IMGREL
$ip2state$_RNvYNtNtNtNtCse0R8cuyqEa_3std3sys5stdio7windows6StderrNtNtBa_2io5Write9write_allCs98fvGvYc57G_10rayon_core:
	.long	.Lfunc_begin69@IMGREL
	.long	-1
	.long	.Ltmp234@IMGREL
	.long	0
	.long	.Ltmp235@IMGREL
	.long	-1
	.long	.Ltmp232@IMGREL
	.long	0
	.long	.Ltmp233@IMGREL
	.long	-1
	.section	.text,"xr",one_only,_RNvYNtNtNtNtCse0R8cuyqEa_3std3sys5stdio7windows6StderrNtNtBa_2io5Write9write_allCs98fvGvYc57G_10rayon_core,unique,70

	.def	_RNvYNtNtNtNtCse0R8cuyqEa_3std3sys5stdio7windows6StderrNtNtBa_2io5Write9write_fmtCs98fvGvYc57G_10rayon_core;
	.scl	3;
	.type	32;
	.endef
	.section	.text,"xr",one_only,_RNvYNtNtNtNtCse0R8cuyqEa_3std3sys5stdio7windows6StderrNtNtBa_2io5Write9write_fmtCs98fvGvYc57G_10rayon_core,unique,72
	.p2align	4
_RNvYNtNtNtNtCse0R8cuyqEa_3std3sys5stdio7windows6StderrNtNtBa_2io5Write9write_fmtCs98fvGvYc57G_10rayon_core:
.Lfunc_begin70:
	leaq	anon.0fe27b6b3d07a996c3f93015bf85f83b.55(%rip), %rdx
	movl	$61, %r8d
	jmp	_RNvYNtNtNtNtCse0R8cuyqEa_3std3sys5stdio7windows6StderrNtNtBa_2io5Write9write_allCs98fvGvYc57G_10rayon_core
.Lfunc_end70:

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.0.llvm.17002324475202138184,unique,73
	.globl	anon.0fe27b6b3d07a996c3f93015bf85f83b.0.llvm.17002324475202138184
anon.0fe27b6b3d07a996c3f93015bf85f83b.0.llvm.17002324475202138184:
	.asciz	"C:\\Users\\there\\.cargo\\registry\\src\\index.crates.io-1949cf8c6b5b557f\\rayon-core-1.13.0\\src\\sleep\\mod.rs"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.1,unique,74
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.1:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.0.llvm.17002324475202138184
	.asciz	"f\000\000\000\000\000\000\000\202\000\000\0004\000\000"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.2,unique,75
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.2:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.0.llvm.17002324475202138184
	.asciz	"f\000\000\000\000\000\000\000\203\000\000\000<\000\000"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.3,unique,76
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.3:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.0.llvm.17002324475202138184
	.asciz	"f\000\000\000\000\000\000\000\273\000\000\000C\000\000"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.5.llvm.17002324475202138184,unique,77
	.globl	anon.0fe27b6b3d07a996c3f93015bf85f83b.5.llvm.17002324475202138184
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.5.llvm.17002324475202138184:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtBd_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB17_23default_global_registryE0E0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceTRNtBd_9OnceStateEE9call_once6vtableB19_.llvm.17002324475202138184
	.quad	_RNCINvMs0_NtNtCse0R8cuyqEa_3std4sync4onceNtB8_4Once9call_onceNCINvNtCs98fvGvYc57G_10rayon_core8registry19set_global_registryNvB12_23default_global_registryE0E0B14_.llvm.17002324475202138184

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.6,unique,78
anon.0fe27b6b3d07a996c3f93015bf85f83b.6:
	.ascii	"internal error: entered unreachable code"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.7,unique,79
anon.0fe27b6b3d07a996c3f93015bf85f83b.7:
	.asciz	"/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\std\\src\\sys\\thread_local\\native\\lazy.rs"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.8,unique,80
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.8:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.7
	.asciz	"_\000\000\000\000\000\000\000b\000\000\000$\000\000"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.9.llvm.17002324475202138184,unique,81
	.globl	anon.0fe27b6b3d07a996c3f93015bf85f83b.9.llvm.17002324475202138184
anon.0fe27b6b3d07a996c3f93015bf85f83b.9.llvm.17002324475202138184:
	.asciz	"C:\\Users\\there\\.cargo\\registry\\src\\index.crates.io-1949cf8c6b5b557f\\rayon-core-1.13.0\\src\\registry.rs"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.10,unique,82
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.10:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.9.llvm.17002324475202138184
	.asciz	"e\000\000\000\000\000\000\0004\001\000\0006\000\000"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.11.llvm.17002324475202138184,unique,83
	.globl	anon.0fe27b6b3d07a996c3f93015bf85f83b.11.llvm.17002324475202138184
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.11.llvm.17002324475202138184:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.9.llvm.17002324475202138184
	.asciz	"e\000\000\000\000\000\000\000\303\000\000\000\026\000\000"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.14,unique,84
anon.0fe27b6b3d07a996c3f93015bf85f83b.14:
	.asciz	"/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\std\\src\\io\\mod.rs"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.16,unique,85
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.16:
	.quad	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1H_12DefaultSpawnNtB1H_11ThreadSpawn5spawn0uEs_0EB1J_
	.asciz	"\220\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNSNvYNCINvNtNtCse0R8cuyqEa_3std6thread9lifecycle15spawn_uncheckedNCNvXs0_NtCs98fvGvYc57G_10rayon_core8registryNtB1a_12DefaultSpawnNtB1a_11ThreadSpawn5spawn0uEs_0INtNtNtCs8xEFJqa6dYS_4core3ops8function6FnOnceuE9call_once6vtableB1c_

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.17,unique,86
anon.0fe27b6b3d07a996c3f93015bf85f83b.17:
	.asciz	"/rustc/48a229ceaefd4985c50990b14116b6d856af0985/library\\std\\src\\sync\\once.rs"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.18,unique,87
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.18:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.17
	.asciz	"L\000\000\000\000\000\000\000\246\000\000\0002\000\000"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.19,unique,88
anon.0fe27b6b3d07a996c3f93015bf85f83b.19:
	.ascii	"RUST_MIN_STACK"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.20,unique,89
anon.0fe27b6b3d07a996c3f93015bf85f83b.20:
	.ascii	"assertion failed: t.get().is_null()"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.21,unique,90
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.21:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.9.llvm.17002324475202138184
	.asciz	"e\000\000\000\000\000\000\000\306\002\000\000\r\000\000"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.22,unique,91
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.22:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.9.llvm.17002324475202138184
	.asciz	"e\000\000\000\000\000\000\000{\003\000\000#\000\000"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.23,unique,92
anon.0fe27b6b3d07a996c3f93015bf85f83b.23:
	.ascii	"assertion failed: t.get().eq(&(self as *const _))"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.24,unique,93
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.24:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.9.llvm.17002324475202138184
	.asciz	"e\000\000\000\000\000\000\000\263\002\000\000\r\000\000"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.27.llvm.17002324475202138184,unique,94
	.globl	anon.0fe27b6b3d07a996c3f93015bf85f83b.27.llvm.17002324475202138184
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.27.llvm.17002324475202138184:
	.quad	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueINtNtNtCse0R8cuyqEa_3std4sync6poison11PoisonErrorINtNtBE_5mutex10MutexGuardbEEECs98fvGvYc57G_10rayon_core.llvm.17002324475202138184
	.asciz	"\020\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNvXs_NtNtCse0R8cuyqEa_3std4sync6poisonINtB4_11PoisonErrorINtNtB4_5mutex10MutexGuardbEENtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmtCs98fvGvYc57G_10rayon_core.llvm.17002324475202138184

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.28.llvm.17002324475202138184,unique,95
	.globl	anon.0fe27b6b3d07a996c3f93015bf85f83b.28.llvm.17002324475202138184
anon.0fe27b6b3d07a996c3f93015bf85f83b.28.llvm.17002324475202138184:
	.ascii	"called `Result::unwrap()` on an `Err` value"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.29.llvm.17002324475202138184,unique,96
	.globl	anon.0fe27b6b3d07a996c3f93015bf85f83b.29.llvm.17002324475202138184
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.29.llvm.17002324475202138184:
	.quad	_RINvNtCs8xEFJqa6dYS_4core3ptr9drop_glueNtCs98fvGvYc57G_10rayon_core20ThreadPoolBuildErrorEBD_.llvm.17002324475202138184
	.asciz	"\020\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNvXsb_Cs98fvGvYc57G_10rayon_coreNtB5_20ThreadPoolBuildErrorNtNtCs8xEFJqa6dYS_4core3fmt5Debug3fmt.llvm.17002324475202138184

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.30.llvm.17002324475202138184,unique,97
	.globl	anon.0fe27b6b3d07a996c3f93015bf85f83b.30.llvm.17002324475202138184
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.30.llvm.17002324475202138184:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.0.llvm.17002324475202138184
	.asciz	"f\000\000\000\000\000\000\000!\001\000\0004\000\000"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.31.llvm.17002324475202138184,unique,98
	.globl	anon.0fe27b6b3d07a996c3f93015bf85f83b.31.llvm.17002324475202138184
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.31.llvm.17002324475202138184:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.0.llvm.17002324475202138184
	.asciz	"f\000\000\000\000\000\000\000#\001\000\000<\000\000"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.34,unique,99
anon.0fe27b6b3d07a996c3f93015bf85f83b.34:
	.ascii	"RAYON_NUM_THREADS"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.35,unique,100
anon.0fe27b6b3d07a996c3f93015bf85f83b.35:
	.ascii	"RAYON_RS_NUM_CPUS"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.36.llvm.17002324475202138184,unique,101
	.globl	anon.0fe27b6b3d07a996c3f93015bf85f83b.36.llvm.17002324475202138184
anon.0fe27b6b3d07a996c3f93015bf85f83b.36.llvm.17002324475202138184:
	.asciz	"C:\\Users\\there\\.cargo\\registry\\src\\index.crates.io-1949cf8c6b5b557f\\rayon-core-1.13.0\\src\\latch.rs"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.37.llvm.17002324475202138184,unique,102
	.globl	anon.0fe27b6b3d07a996c3f93015bf85f83b.37.llvm.17002324475202138184
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.37.llvm.17002324475202138184:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.36.llvm.17002324475202138184
	.asciz	"b\000\000\000\000\000\000\000\364\000\000\000'\000\000"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.38.llvm.17002324475202138184,unique,103
	.globl	anon.0fe27b6b3d07a996c3f93015bf85f83b.38.llvm.17002324475202138184
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.38.llvm.17002324475202138184:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.36.llvm.17002324475202138184
	.asciz	"b\000\000\000\000\000\000\000\366\000\000\000(\000\000"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.43,unique,104
anon.0fe27b6b3d07a996c3f93015bf85f83b.43:
	.asciz	"C:\\Users\\there\\.cargo\\registry\\src\\index.crates.io-1949cf8c6b5b557f\\crossbeam-epoch-0.9.18\\src\\internal.rs"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.44,unique,105
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.44:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.43
	.asciz	"j\000\000\000\000\000\000\000\201\001\000\0009\000\000"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.47,unique,106
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.47:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.9.llvm.17002324475202138184
	.asciz	"e\000\000\000\000\000\000\0008\003\000\000/\000\000"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.48,unique,107
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.48:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.9.llvm.17002324475202138184
	.asciz	"e\000\000\000\000\000\000\000>\003\000\000*\000\000"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.49,unique,108
anon.0fe27b6b3d07a996c3f93015bf85f83b.49:
	.asciz	"C:\\Users\\there\\.cargo\\registry\\src\\index.crates.io-1949cf8c6b5b557f\\crossbeam-deque-0.8.6\\src\\deque.rs"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.50,unique,109
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.50:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.49
	.asciz	"f\000\000\000\000\000\000\000\177\005\000\000C\000\000"

	.section	.tls$,"dw",one_only,_RNvNCNKNvNtCs98fvGvYc57G_10rayon_core8registry19WORKER_THREAD_STATE0s_023___RUST_STD_INTERNAL_VAL,unique,110
	.globl	_RNvNCNKNvNtCs98fvGvYc57G_10rayon_core8registry19WORKER_THREAD_STATE0s_023___RUST_STD_INTERNAL_VAL
	.p2align	3, 0x0
_RNvNCNKNvNtCs98fvGvYc57G_10rayon_core8registry19WORKER_THREAD_STATE0s_023___RUST_STD_INTERNAL_VAL:
	.zero	8

	.section	.tls$,"dw",one_only,_RNvNCNKNvNvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtBd_8Registry14in_worker_cold10LOCK_LATCH0s_023___RUST_STD_INTERNAL_VAL,unique,111
	.globl	_RNvNCNKNvNvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtBd_8Registry14in_worker_cold10LOCK_LATCH0s_023___RUST_STD_INTERNAL_VAL
	.p2align	2, 0x0
_RNvNCNKNvNvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtBd_8Registry14in_worker_cold10LOCK_LATCH0s_023___RUST_STD_INTERNAL_VAL:
	.zero	7
	.zero	1

	.section	.bss,"bw",one_only,_RNvNtCs98fvGvYc57G_10rayon_core8registry12THE_REGISTRY,unique,112
	.globl	_RNvNtCs98fvGvYc57G_10rayon_core8registry12THE_REGISTRY
	.p2align	3, 0x0
_RNvNtCs98fvGvYc57G_10rayon_core8registry12THE_REGISTRY:
	.zero	8

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.51.llvm.17002324475202138184,unique,113
	.globl	anon.0fe27b6b3d07a996c3f93015bf85f83b.51.llvm.17002324475202138184
anon.0fe27b6b3d07a996c3f93015bf85f83b.51.llvm.17002324475202138184:
	.ascii	"The global thread pool has not been initialized."

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.52.llvm.17002324475202138184,unique,114
	.globl	anon.0fe27b6b3d07a996c3f93015bf85f83b.52.llvm.17002324475202138184
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.52.llvm.17002324475202138184:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.9.llvm.17002324475202138184
	.asciz	"e\000\000\000\000\000\000\000\253\000\000\000\n\000\000"

	.section	.data,"dw",one_only,_RNvNtCs98fvGvYc57G_10rayon_core8registry16THE_REGISTRY_SET,unique,115
	.globl	_RNvNtCs98fvGvYc57G_10rayon_core8registry16THE_REGISTRY_SET
	.p2align	2, 0x0
_RNvNtCs98fvGvYc57G_10rayon_core8registry16THE_REGISTRY_SET:
	.asciz	"\003\000\000"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.53,unique,116
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.53:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.9.llvm.17002324475202138184
	.asciz	"e\000\000\000\000\000\000\000\225\003\000\000&\000\000"

	.section	.bss,"bw",one_only,_RNvNvMs9_NtCs98fvGvYc57G_10rayon_core8registryNtB7_14XorShift64Star3new7COUNTER,unique,117
	.p2align	3, 0x0
_RNvNvMs9_NtCs98fvGvYc57G_10rayon_core8registryNtB7_14XorShift64Star3new7COUNTER:
	.zero	8

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.54.llvm.17002324475202138184,unique,118
	.globl	anon.0fe27b6b3d07a996c3f93015bf85f83b.54.llvm.17002324475202138184
anon.0fe27b6b3d07a996c3f93015bf85f83b.54.llvm.17002324475202138184:
	.ascii	"Rayon: detected unexpected panic; aborting\n"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.55,unique,119
anon.0fe27b6b3d07a996c3f93015bf85f83b.55:
	.ascii	"fatal runtime error: thread local panicked on drop, aborting\n"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.62,unique,120
anon.0fe27b6b3d07a996c3f93015bf85f83b.62:
	.ascii	"fatal runtime error: thread result panicked on drop, aborting\n"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.78,unique,121
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.78:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.36.llvm.17002324475202138184
	.asciz	"b\000\000\000\000\000\000\000\007\001\000\000*\000\000"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.121,unique,122
anon.0fe27b6b3d07a996c3f93015bf85f83b.121:
	.ascii	"PoisonError"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.122,unique,123
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.122:
	.asciz	"\000\000\000\000\000\000\000\000\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_RNvXs1g_NtCs8xEFJqa6dYS_4core3fmtRNtCs98fvGvYc57G_10rayon_core9ErrorKindNtB6_5Debug3fmtBy_

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.123,unique,124
anon.0fe27b6b3d07a996c3f93015bf85f83b.123:
	.ascii	"ThreadPoolBuildError"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.124,unique,125
anon.0fe27b6b3d07a996c3f93015bf85f83b.124:
	.ascii	"kind"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.125,unique,126
anon.0fe27b6b3d07a996c3f93015bf85f83b.125:
	.ascii	"GlobalPoolAlreadyInitialized"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.126,unique,127
anon.0fe27b6b3d07a996c3f93015bf85f83b.126:
	.ascii	"CurrentThreadAlreadyInPool"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.128,unique,128
anon.0fe27b6b3d07a996c3f93015bf85f83b.128:
	.ascii	"IOError"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.145,unique,129
anon.0fe27b6b3d07a996c3f93015bf85f83b.145:
	.ascii	"failed to write whole buffer"

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.146,unique,130
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.146:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.145
	.ascii	"\034\000\000\000\000\000\000\000\027"
	.zero	7

	.section	.rdata,"dr",one_only,anon.0fe27b6b3d07a996c3f93015bf85f83b.147,unique,131
	.p2align	3, 0x0
anon.0fe27b6b3d07a996c3f93015bf85f83b.147:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.14
	.asciz	"I\000\000\000\000\000\000\000Q\006\000\000$\000\000"

	.section	.data,"dw",one_only,__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.0.llvm.17002324475202138184,unique,132
	.globl	__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.0.llvm.17002324475202138184
	.p2align	3, 0x0
__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.0.llvm.17002324475202138184:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.0.llvm.17002324475202138184

	.section	.data,"dw",one_only,__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.5.llvm.17002324475202138184,unique,133
	.globl	__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.5.llvm.17002324475202138184
	.p2align	3, 0x0
__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.5.llvm.17002324475202138184:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.5.llvm.17002324475202138184

	.section	.data,"dw",one_only,__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.9.llvm.17002324475202138184,unique,134
	.globl	__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.9.llvm.17002324475202138184
	.p2align	3, 0x0
__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.9.llvm.17002324475202138184:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.9.llvm.17002324475202138184

	.section	.data,"dw",one_only,__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.11.llvm.17002324475202138184,unique,135
	.globl	__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.11.llvm.17002324475202138184
	.p2align	3, 0x0
__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.11.llvm.17002324475202138184:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.11.llvm.17002324475202138184

	.section	.data,"dw",one_only,__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.27.llvm.17002324475202138184,unique,136
	.globl	__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.27.llvm.17002324475202138184
	.p2align	3, 0x0
__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.27.llvm.17002324475202138184:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.27.llvm.17002324475202138184

	.section	.data,"dw",one_only,__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.28.llvm.17002324475202138184,unique,137
	.globl	__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.28.llvm.17002324475202138184
	.p2align	3, 0x0
__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.28.llvm.17002324475202138184:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.28.llvm.17002324475202138184

	.section	.data,"dw",one_only,__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.29.llvm.17002324475202138184,unique,138
	.globl	__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.29.llvm.17002324475202138184
	.p2align	3, 0x0
__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.29.llvm.17002324475202138184:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.29.llvm.17002324475202138184

	.section	.data,"dw",one_only,__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.30.llvm.17002324475202138184,unique,139
	.globl	__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.30.llvm.17002324475202138184
	.p2align	3, 0x0
__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.30.llvm.17002324475202138184:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.30.llvm.17002324475202138184

	.section	.data,"dw",one_only,__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.31.llvm.17002324475202138184,unique,140
	.globl	__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.31.llvm.17002324475202138184
	.p2align	3, 0x0
__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.31.llvm.17002324475202138184:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.31.llvm.17002324475202138184

	.section	.data,"dw",one_only,__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.36.llvm.17002324475202138184,unique,141
	.globl	__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.36.llvm.17002324475202138184
	.p2align	3, 0x0
__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.36.llvm.17002324475202138184:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.36.llvm.17002324475202138184

	.section	.data,"dw",one_only,__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.37.llvm.17002324475202138184,unique,142
	.globl	__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.37.llvm.17002324475202138184
	.p2align	3, 0x0
__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.37.llvm.17002324475202138184:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.37.llvm.17002324475202138184

	.section	.data,"dw",one_only,__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.38.llvm.17002324475202138184,unique,143
	.globl	__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.38.llvm.17002324475202138184
	.p2align	3, 0x0
__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.38.llvm.17002324475202138184:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.38.llvm.17002324475202138184

	.section	.data,"dw",one_only,__imp__RNvNCNKNvNtCs98fvGvYc57G_10rayon_core8registry19WORKER_THREAD_STATE0s_023___RUST_STD_INTERNAL_VAL,unique,144
	.globl	__imp__RNvNCNKNvNtCs98fvGvYc57G_10rayon_core8registry19WORKER_THREAD_STATE0s_023___RUST_STD_INTERNAL_VAL
	.p2align	3, 0x0
__imp__RNvNCNKNvNtCs98fvGvYc57G_10rayon_core8registry19WORKER_THREAD_STATE0s_023___RUST_STD_INTERNAL_VAL:
	.quad	_RNvNCNKNvNtCs98fvGvYc57G_10rayon_core8registry19WORKER_THREAD_STATE0s_023___RUST_STD_INTERNAL_VAL

	.section	.data,"dw",one_only,__imp__RNvNCNKNvNvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtBd_8Registry14in_worker_cold10LOCK_LATCH0s_023___RUST_STD_INTERNAL_VAL,unique,145
	.globl	__imp__RNvNCNKNvNvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtBd_8Registry14in_worker_cold10LOCK_LATCH0s_023___RUST_STD_INTERNAL_VAL
	.p2align	3, 0x0
__imp__RNvNCNKNvNvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtBd_8Registry14in_worker_cold10LOCK_LATCH0s_023___RUST_STD_INTERNAL_VAL:
	.quad	_RNvNCNKNvNvMs4_NtCs98fvGvYc57G_10rayon_core8registryNtBd_8Registry14in_worker_cold10LOCK_LATCH0s_023___RUST_STD_INTERNAL_VAL

	.section	.data,"dw",one_only,__imp__RNvNtCs98fvGvYc57G_10rayon_core8registry12THE_REGISTRY,unique,146
	.globl	__imp__RNvNtCs98fvGvYc57G_10rayon_core8registry12THE_REGISTRY
	.p2align	3, 0x0
__imp__RNvNtCs98fvGvYc57G_10rayon_core8registry12THE_REGISTRY:
	.quad	_RNvNtCs98fvGvYc57G_10rayon_core8registry12THE_REGISTRY

	.section	.data,"dw",one_only,__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.51.llvm.17002324475202138184,unique,147
	.globl	__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.51.llvm.17002324475202138184
	.p2align	3, 0x0
__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.51.llvm.17002324475202138184:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.51.llvm.17002324475202138184

	.section	.data,"dw",one_only,__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.52.llvm.17002324475202138184,unique,148
	.globl	__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.52.llvm.17002324475202138184
	.p2align	3, 0x0
__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.52.llvm.17002324475202138184:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.52.llvm.17002324475202138184

	.section	.data,"dw",one_only,__imp__RNvNtCs98fvGvYc57G_10rayon_core8registry16THE_REGISTRY_SET,unique,149
	.globl	__imp__RNvNtCs98fvGvYc57G_10rayon_core8registry16THE_REGISTRY_SET
	.p2align	3, 0x0
__imp__RNvNtCs98fvGvYc57G_10rayon_core8registry16THE_REGISTRY_SET:
	.quad	_RNvNtCs98fvGvYc57G_10rayon_core8registry16THE_REGISTRY_SET

	.section	.data,"dw",one_only,__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.54.llvm.17002324475202138184,unique,150
	.globl	__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.54.llvm.17002324475202138184
	.p2align	3, 0x0
__imp_anon.0fe27b6b3d07a996c3f93015bf85f83b.54.llvm.17002324475202138184:
	.quad	anon.0fe27b6b3d07a996c3f93015bf85f83b.54.llvm.17002324475202138184

	.section	.debug$S,"dr"
	.p2align	2, 0x0
	.long	4
	.long	241
	.long	.Ltmp237-.Ltmp236
.Ltmp236:
	.short	.Ltmp239-.Ltmp238
.Ltmp238:
	.short	4353
	.long	0
	.asciz	"S:\\GTOpen-research\\postflop-gpu-20261016\\runs\\D089-zero-scan-codegen\\build\\postflop-codegen.rayon_core-0787e97421794457.rayon_core.6a60e46128274a72-cgu.0.rcgu.o.rcgu.o"
	.p2align	2, 0x0
.Ltmp239:
	.short	.Ltmp241-.Ltmp240
.Ltmp240:
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
.Ltmp241:
.Ltmp237:
	.p2align	2, 0x0
	.cv_filechecksums
	.cv_stringtable
	.long	241
	.long	.Ltmp243-.Ltmp242
.Ltmp242:
	.short	.Ltmp245-.Ltmp244
.Ltmp244:
	.short	4428
	.long	4099
	.p2align	2, 0x0
.Ltmp245:
.Ltmp243:
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
