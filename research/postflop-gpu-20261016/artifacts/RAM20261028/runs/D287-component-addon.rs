// Diagnostic-only methods appended after the byte-exact accepted host/observer.
fn d287_cu(v:sys::CUresult)->Result<(),String>{if v==sys::CUresult::CUDA_SUCCESS{Ok(())}else{Err(format!("cuda D287: {v:?}"))}}
impl GpuSolver {
    fn d287_fold(&mut self,p:usize,l:usize,stream:&Arc<CudaStream>)->Result<(),String>{
        use cudarc::driver::DevicePtr;
        let nh_p=self.nh[p];let nh_o=self.nh[1-p];let nh_max=self.nh_max;let pi=p as i32;
        let (cfv_base,guard)=self.d_cfv.device_ptr(&self.stream);drop(guard);
        // D287_FOLD_BODY
        Ok(())
    }
    fn d287_show(&mut self,p:usize,l:usize,stream:&Arc<CudaStream>)->Result<(),String>{
        use cudarc::driver::DevicePtr;
        let nh_p=self.nh[p];let nh_o=self.nh[1-p];let nh_max=self.nh_max;
        let show_shared=(self.riv_max_cnt[1-p]*16+nh_o as usize*4)as u32;
        let (cfv_base,guard)=self.d_cfv.device_ptr(&self.stream);drop(guard);
        // D287_SHOW_BODY
        Ok(())
    }
    pub fn d287_poison(&mut self,bits:u32)->Result<(),String>{
        use cudarc::driver::DevicePtr;
        self.stream.synchronize().map_err(e)?;let(ptr,guard)=self.d_cfv.device_ptr(&self.stream);drop(guard);
        unsafe{d287_cu(sys::cuMemsetD32Async(ptr,bits,self.d_cfv.len(),self.stream.cu_stream()))?;}
        self.stream.synchronize().map_err(e)
    }
    fn d287_queue(&mut self,p:usize,side:Option<&Arc<CudaStream>>,ready:Option<&cudarc::driver::CudaEvent>,done:Option<&cudarc::driver::CudaEvent>)->Result<(),String>{
        let main=self.stream.clone();
        for l in(0..self.num_levels).rev(){
            let fork=side.is_some()&&self.fold_spans[l].count>0&&self.show_spans[l].count>0;
            if fork{ready.unwrap().record(&main).map_err(e)?;side.unwrap().wait(ready.unwrap()).map_err(e)?;}
            let result:Result<(),String>=(||{self.d287_fold(p,l,&main)?;self.d287_show(p,l,if fork{side.unwrap()}else{&main})?;Ok(())})();
            let joined=if fork{done.unwrap().record(side.unwrap()).and_then(|_|main.wait(done.unwrap())).map_err(e)}else{Ok(())};
            result?;joined?;
        }Ok(())
    }
    fn d287_dag(&self,graph:&CudaGraph,p:usize)->Result<serde_json::Value,String>{
        use cudarc::driver::DevicePtr;
        let mut count=0;unsafe{d287_cu(sys::cuGraphGetNodes(graph.cu_graph(),std::ptr::null_mut(),&mut count))?;}
        let mut nodes=vec![std::ptr::null_mut();count];unsafe{d287_cu(sys::cuGraphGetNodes(graph.cu_graph(),nodes.as_mut_ptr(),&mut count))?;}
        let(fold,fg)=self.d_fold_nodes.device_ptr(&self.stream);drop(fg);let(show,sg)=self.d_show_nodes.device_ptr(&self.stream);drop(sg);assert_ne!(fold,show);
        let mut rows=Vec::new();
        for(node_index,node)in nodes.iter().enumerate(){
            let mut ty=sys::CUgraphNodeType::CU_GRAPH_NODE_TYPE_EMPTY;unsafe{d287_cu(sys::cuGraphNodeGetType(*node,&mut ty))?;}
            let mut deps=0;unsafe{d287_cu(sys::cuGraphNodeGetDependencies(*node,std::ptr::null_mut(),&mut deps))?;}
            let mut parents=vec![std::ptr::null_mut();deps];if deps>0{unsafe{d287_cu(sys::cuGraphNodeGetDependencies(*node,parents.as_mut_ptr(),&mut deps))?;}}
            let parents=parents.iter().map(|parent|nodes.iter().position(|n|n==parent).unwrap()).collect::<Vec<_>>();
            if ty==sys::CUgraphNodeType::CU_GRAPH_NODE_TYPE_EMPTY{rows.push(serde_json::json!({"index":node_index,"kind":"empty","dependencies":parents}));continue;}
            assert_eq!(ty,sys::CUgraphNodeType::CU_GRAPH_NODE_TYPE_KERNEL);let mut params:sys::CUDA_KERNEL_NODE_PARAMS=unsafe{std::mem::zeroed()};unsafe{d287_cu(sys::cuGraphKernelNodeGetParams_v2(*node,&mut params))?;}
            assert!(!params.kernelParams.is_null());let first=unsafe{*(params.kernelParams.add(0).read()as*const u64)};
            let(family,num_args,int_args)=if first==fold{("fold",21,vec![1,2,3,18,19,20])}else{assert_eq!(first,show);("show",27,vec![1,2,24,25,26])};
            let mut args=Vec::new();for i in 0..num_args{args.push(if int_args.contains(&i){unsafe{*(params.kernelParams.add(i).read()as*const u32)as u64}}else{unsafe{*(params.kernelParams.add(i).read()as*const u64)}});}
            let spans=if family=="fold"{&self.fold_spans}else{&self.show_spans};let level=spans.iter().position(|s|s.count>0&&s.start as u64==args[1]&&s.count as u64==args[2]).unwrap();
            rows.push(serde_json::json!({"index":node_index,"kind":"kernel","family":family,"level":level,"player":p,"args":args,"dependencies":parents,"grid":[params.gridDimX,params.gridDimY,params.gridDimZ],"block":[params.blockDimX,params.blockDimY,params.blockDimZ],"shared_bytes":params.sharedMemBytes,"function":params.func as usize}));
        }
        let count_expected=self.fold_spans.iter().filter(|s|s.count>0).count()+self.show_spans.iter().filter(|s|s.count>0).count();assert_eq!(rows.iter().filter(|r|r["kind"]=="kernel").count(),count_expected);
        Ok(serde_json::json!({"nodes":rows,"all_original_terminal_nodes":count_expected,"fold_spans":self.fold_spans.iter().map(|s|[s.start,s.count]).collect::<Vec<_>>(),"show_spans":self.show_spans.iter().map(|s|[s.start,s.count]).collect::<Vec<_>>()}))
    }
    pub fn d287_component(&mut self,p:usize,candidate:bool,replays:u32)->Result<serde_json::Value,String>{
        assert!(p<2&&replays>0);assert!(!self._ctx.is_event_tracking());self.stream.synchronize().map_err(e)?;
        let method=std::time::Instant::now();let prep=std::time::Instant::now();
        let selected=candidate&&self.d_node_player.len()>=65536&&self.fold_spans.iter().zip(&self.show_spans).any(|(f,s)|f.count>0&&s.count>0);
        let mut side=if selected{Some(self._ctx.new_stream().map_err(e)?)}else{None};let mut ready=if selected{Some(self._ctx.new_event(None).map_err(e)?)}else{None};let mut done=if selected{Some(self._ctx.new_event(None).map_err(e)?)}else{None};
        self.stream.begin_capture(sys::CUstreamCaptureMode::CU_STREAM_CAPTURE_MODE_THREAD_LOCAL).map_err(e)?;
        let queued=self.d287_queue(p,side.as_ref(),ready.as_ref(),done.as_ref());let captured=self.stream.end_capture(sys::CUgraphInstantiate_flags::CUDA_GRAPH_INSTANTIATE_FLAG_AUTO_FREE_ON_LAUNCH).map_err(e);
        let prep_ns=prep.elapsed().as_nanos()as u64;
        let result:Result<serde_json::Value,String>=(||{
            let graph=captured?.ok_or_else(||"D287emptygraph".to_string())?;queued?;
            let run=std::time::Instant::now();for _ in 0..replays{graph.launch().map_err(e)?;}self.stream.synchronize().map_err(e)?;if let Some(side)=&side{side.synchronize().map_err(e)?;}let replay_ns=run.elapsed().as_nanos()as u64;
            let inspection=std::time::Instant::now();let dag=self.d287_dag(&graph,p)?;let inspection_ns=inspection.elapsed().as_nanos()as u64;
            let clean=std::time::Instant::now();drop(graph);drop(done.take());drop(ready.take());drop(side.take());self.stream.synchronize().map_err(e)?;self._ctx.check_err().map_err(e)?;let cleanup_ns=clean.elapsed().as_nanos()as u64;
            Ok(serde_json::json!({"player":p,"candidate":candidate,"selected":selected,"replays":replays,"setup_capture_ns":prep_ns,"replays_completion_ns":replay_ns,"cleanup_ns":cleanup_ns,"component_ns":prep_ns+replay_ns+cleanup_ns,"inspection_ns_excluded":inspection_ns,"method_wall_ns":method.elapsed().as_nanos()as u64,"dag":dag,"all_temporary_graph_stream_events_dropped":true,"no_new_application_device_arrays":true}))
        })();
        if result.is_err(){let a=self.stream.synchronize().map_err(e);let b=if let Some(side)=&side{side.synchronize().map_err(e)}else{Ok(())};drop(done);drop(ready);drop(side);a?;b?;}
        result
    }
}
