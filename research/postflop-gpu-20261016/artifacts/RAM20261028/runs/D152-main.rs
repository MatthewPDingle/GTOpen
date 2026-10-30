fn emit(v: Value) { println!("D152_CONTROL {v}"); std::io::stdout().flush().unwrap(); }
fn words_file(path: &Path, words: &[u32]) {
    let mut f=BufWriter::new(OpenOptions::new().create_new(true).write(true).open(path).unwrap());
    for word in words { f.write_all(&word.to_le_bytes()).unwrap(); } f.flush().unwrap(); f.get_ref().sync_all().unwrap();
}
#[derive(Clone)] struct Block { node:usize, source:u64, length:u32, qoff:usize }
struct Packet { blocks:Vec<Block>, qwords:usize }
fn packets(offsets:&[u64], lengths:&[u32], max_desc:usize) -> Vec<Packet> {
    assert_eq!(offsets.len(),lengths.len());assert!(max_desc>0);
    let mut out=Vec::new();let mut current=Packet{blocks:Vec::new(),qwords:0};
    for (node,(&source,&length)) in offsets.iter().zip(lengths).enumerate() {
        let qwords=(length as usize+1)/2;
        assert!(5+qwords<=65544);
        if !current.blocks.is_empty() && (current.blocks.len()==max_desc || 5*(current.blocks.len()+1)+current.qwords+qwords>65544) {
            out.push(current);current=Packet{blocks:Vec::new(),qwords:0};
        }
        let qoff=current.qwords;
        current.blocks.push(Block{node,source,length,qoff});current.qwords+=qwords;
    }
    if !current.blocks.is_empty() {out.push(current);}out
}
fn main() {
    let out=PathBuf::from(std::env::args().nth(1).unwrap());std::fs::create_dir(&out).unwrap();
    let ptx=std::env::args().nth(2).unwrap();
    let cases=cases();assert_eq!(cases.len(),2212);
    let mut data=Vec::new();let mut offsets=Vec::new();let mut lengths=Vec::new();let mut inputs=Vec::new();
    for (node,case) in cases.iter().enumerate() {
        data.extend([f32::from_bits(0x7fc055aa);3]);let offset=data.len() as u64;
        offsets.push(offset);lengths.push(u32::try_from(case.values.len()).unwrap());data.extend_from_slice(&case.values);data.extend([f32::from_bits(0x7fc055aa);3]);
        inputs.push(json!({"node":node,"name":case.name,"source":offset,"length":case.values.len()}));
    }
    assert!(packets(&[],&[],7).is_empty());
    let input_bits:Vec<u32>=data.iter().map(|v|v.to_bits()).collect();words_file(&out.join("source-input.u32"),&input_bits);
    let mut f=OpenOptions::new().create_new(true).write(true).open(out.join("case-manifest.json")).unwrap();f.write_all(serde_json::to_string_pretty(&inputs).unwrap().as_bytes()).unwrap();f.sync_all().unwrap();drop(f);
    let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));
    let stream=ctx.new_stream().unwrap();let module=ctx.load_module(Ptx::from_file(ptx)).unwrap();let d_data=stream.clone_htod(&data).unwrap();
    let mut cohorts=Vec::new();let mut launch_count=0;
    for signed in [true,false] {
        let mut oracle_q=vec![0xa55au16;data.len()];let mut oracle_scales=Vec::new();
        for (case,&offset) in cases.iter().zip(&offsets) {
            let dst=&mut oracle_q[offset as usize..offset as usize+case.values.len()];
            let scale=if signed {let mut q=vec![0i16;dst.len()];let scale=encode_i16(&case.values,&mut q);for (a,b) in dst.iter_mut().zip(q) {*a=b as u16;}scale} else {encode_u16(&case.values,dst)};
            oracle_scales.push(scale.to_bits());
        }
        let variant=if signed {"i16"} else {"u16"};
        words_file(&out.join(format!("oracle-{variant}-q.u32")),&oracle_q.iter().map(|&v|v as u32).collect::<Vec<_>>());
        words_file(&out.join(format!("oracle-{variant}-scale.u32")),&oracle_scales);
        let function=module.load_function(if signed {"packet_quantize_i16"} else {"packet_quantize_u16"}).unwrap();
        for max_desc in [1usize,7,31] {
            let label=format!("{variant}-d{max_desc}");let plan=packets(&offsets,&lengths,max_desc);
            let mut host_q=vec![0xa55au16;data.len()];let mut host_scales=vec![0x7fc0cafeu32;cases.len()];let mut records=Vec::new();
            let before=stream.clone_dtoh(&d_data).unwrap();stream.synchronize().unwrap();let before:Vec<u32>=before.iter().map(|v|v.to_bits()).collect();assert_eq!(before,input_bits);words_file(&out.join(format!("{label}-source-before.u32")),&before);
            for (index,packet) in plan.iter().enumerate() {
                let n=packet.blocks.len();let total=5*n+packet.qwords;assert!(total<=65544 && n<=max_desc);
                let mut initial=vec![0xdeadbeefu32;total+16];
                for (i,b) in packet.blocks.iter().enumerate() {initial[8+4*i..8+4*i+4].copy_from_slice(&[b.source as u32,(b.source>>32)as u32,b.length,b.qoff as u32]);}
                let mut expected=initial.clone();
                for (i,b) in packet.blocks.iter().enumerate() {
                    expected[8+4*n+i]=oracle_scales[b.node];
                    for w in 0..(b.length as usize+1)/2 {
                        let low=oracle_q[b.source as usize+2*w] as u32;
                        let high=if 2*w+1<b.length as usize {oracle_q[b.source as usize+2*w+1] as u32} else {0xd00d};
                        expected[8+5*n+b.qoff+w]=low|(high<<16);
                    }
                }
                let mut d_scratch=stream.clone_htod(&initial).unwrap();
                {let mut view=d_scratch.slice_mut(8..8+total);unsafe {stream.launch_builder(&function).arg(&d_data).arg(&mut view).arg(&(n as u32)).launch(LaunchConfig{grid_dim:(n as u32,1,1),block_dim:(128,1,1),shared_mem_bytes:0}).unwrap();}}
                let actual=stream.clone_dtoh(&d_scratch).unwrap();stream.synchronize().unwrap();launch_count+=1;
                let rawlabel=format!("{label}-packet-{index:04}");
                // Retain raw observations before asserting, including a numerical failure.
                words_file(&out.join(format!("{rawlabel}-initial.u32")),&initial);words_file(&out.join(format!("{rawlabel}-expected.u32")),&expected);words_file(&out.join(format!("{rawlabel}-actual.u32")),&actual);
                assert_eq!(actual,expected,"every scale, packed word, descriptor and guard {rawlabel}");
                for (i,b) in packet.blocks.iter().enumerate() {
                    host_scales[b.node]=actual[8+4*n+i];
                    for j in 0..b.length as usize {host_q[b.source as usize+j]=((actual[8+5*n+b.qoff+j/2]>>(16*(j%2)))&0xffff)as u16;}
                }
                records.push(json!({"packet":index,"blocks":packet.blocks.iter().map(|b|json!({"node":b.node,"source":b.source,"length":b.length,"qoff":b.qoff})).collect::<Vec<_>>(),"total_words":total,"q_words":packet.qwords,"raw_label":rawlabel}));
            }
            assert_eq!(host_q,oracle_q);assert_eq!(host_scales,oracle_scales);
            words_file(&out.join(format!("{label}-host-q.u32")),&host_q.iter().map(|&v|v as u32).collect::<Vec<_>>());words_file(&out.join(format!("{label}-host-scale.u32")),&host_scales);
            let after=stream.clone_dtoh(&d_data).unwrap();stream.synchronize().unwrap();let after:Vec<u32>=after.iter().map(|v|v.to_bits()).collect();words_file(&out.join(format!("{label}-source-after.u32")),&after);assert_eq!(after,input_bits);
            cohorts.push(json!({"label":label,"signed":signed,"max_descriptors":max_desc,"capacity_words":65544,"packets":records,"all_actual_packet_words_exact":true,"source_bits_before_and_after_exact":true,"host_q_scales_exact":true}));
            emit(json!({"stage":"cohort_complete","label":label,"packet_launches":plan.len(),"cases":cases.len(),"exact":true}));
        }
    }
    stream.synchronize().unwrap();drop(d_data);drop(module);drop(stream);ctx.check_err().unwrap();drop(ctx);
    let meta=json!({"id":"D152","cases":2212,"cohorts":cohorts,"kernel_launches":launch_count,"source_words":input_bits.len(),"encoded_values_per_type":lengths.iter().map(|&n|n as u64).sum::<u64>(),"performance_measurement":false,"integration_created":false});
    let mut f=OpenOptions::new().create_new(true).write(true).open(out.join("metadata.json")).unwrap();f.write_all(serde_json::to_string_pretty(&meta).unwrap().as_bytes()).unwrap();f.sync_all().unwrap();
    emit(json!({"stage":"complete","kernel_launches":launch_count,"cohorts":6}));
}
