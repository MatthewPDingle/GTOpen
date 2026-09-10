    #[test]
    #[ignore = "compile/load only; no solve, reports or GPU kernel launches"]
    fn coupled_opponent_entry_register_probe() {
        let ctx=CudaContext::new(0).unwrap();
        let (major,minor)=ctx.compute_capability().unwrap();
        let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
        let ptx=cudarc::nvrtc::compile_ptx_with_opts(include_str!("kernels.cu"),
            cudarc::nvrtc::CompileOptions {arch:Some(arch),..Default::default()}).unwrap();
        let module=ctx.load_module(ptx).unwrap();
        for name in ["pf_multiway_terminal","pf_multiway_terminal_o2","pf_multiway_terminal_o3","pf_multiway_terminal_o4","pf_multiway_terminal_minimal"] {
            let f=module.load_function(name).unwrap();
            println!("OPPONENT_REGISTER_PROBE {}",serde_json::json!({"kernel":name,
                "registers":f.num_regs().unwrap(),"local_bytes":f.local_size_bytes().unwrap(),
                "shared_bytes":f.shared_size_bytes().unwrap(),"max_threads":f.max_threads_per_block().unwrap(),
                "arch":arch,"sample_count":crate::preflop::multiway::SAMPLES,
                "execution":"compile_load_attributes_only"}));
        }
    }
