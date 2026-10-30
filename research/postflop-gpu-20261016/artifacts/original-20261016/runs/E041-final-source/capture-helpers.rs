    fn u32_word(out: &mut Vec<u8>, v: u32) { out.extend(v.to_le_bytes()); }
    fn u64_word(out: &mut Vec<u8>, v: u64) { out.extend(v.to_le_bytes()); }
    fn host_image(s: &Solver) -> Vec<u8> {
        let mut out = b"E041HOST1".to_vec();
        u64_word(&mut out, s.iteration as u64);
        out.push(u8::from(s.use_isomorphism));
        for store in [&s.regrets[0], &s.regrets[1], &s.strat[0], &s.strat[1]] {
            match store {
                Store::F32(b) => {
                    u32_word(&mut out, 0); u64_word(&mut out, b.len() as u64);
                    for v in b.as_slice() { u32_word(&mut out, v.to_bits()); }
                }
                Store::I16 { q, scale } => {
                    u32_word(&mut out, 1); u64_word(&mut out, q.len() as u64);
                    for v in q.as_slice() { out.extend(v.to_le_bytes()); }
                    u64_word(&mut out, scale.len() as u64);
                    for v in scale.as_slice() { u32_word(&mut out, v.to_bits()); }
                }
                Store::U16 { q, scale } => {
                    u32_word(&mut out, 2); u64_word(&mut out, q.len() as u64);
                    for v in q.as_slice() { out.extend(v.to_le_bytes()); }
                    u64_word(&mut out, scale.len() as u64);
                    for v in scale.as_slice() { u32_word(&mut out, v.to_bits()); }
                }
            }
        }
        out
    }
    fn seed(s: &mut Solver, salt: usize) {
        for (which, store) in s.regrets.iter_mut().chain(&mut s.strat).enumerate() {
            match store {
                Store::F32(b) => {
                    for (i,v) in b.as_mut_slice().iter_mut().enumerate() {
                        *v = ((i * 73 + which * 997 + salt) % 1009 + 1) as f32 / 32.0;
                        if which < 2 && i % 3 == 0 { *v = -*v; }
                    }
                }
                Store::I16 { q, scale } => {
                    for (i,v) in q.as_mut_slice().iter_mut().enumerate() {
                        *v = ((i * 73 + which * 997 + salt) % 60001) as i32 as i16;
                    }
                    for (i,v) in scale.as_mut_slice().iter_mut().enumerate() {
                        *v = ((i + which * 7 + salt) % 127 + 1) as f32 / 32.0;
                    }
                }
                Store::U16 { q, scale } => {
                    for (i,v) in q.as_mut_slice().iter_mut().enumerate() {
                        *v = ((i * 71 + which * 991 + salt) % 65535 + 1) as u16;
                    }
                    for (i,v) in scale.as_mut_slice().iter_mut().enumerate() {
                        *v = ((i + which * 11 + salt) % 131 + 1) as f32 / 128.0;
                    }
                }
            }
        }
        s.iteration = if salt == 1 { 0 } else { 999 };
    }
    fn target(spot: &Arc<Spot>, storage: Storage, iso: bool) -> Solver {
        let mut s = Solver::with_storage(spot.clone(), storage);
        s.use_isomorphism = iso;
        seed(&mut s, 37);
        s
    }
    fn query_image(s: &Solver) -> Vec<u8> {
        let mut out = b"E041QUERY1".to_vec();
        let mut nonuniform = false;
        for (id,node) in s.spot.tree.nodes.iter().enumerate() {
            if node.kind != KIND_ACTION { continue; }
            let nh = s.spot.hands[node.player as usize].len();
            let mut sigma = vec![f32::NAN; nh * node.num_children as usize];
            s.solved_strategy_into(node, &mut sigma);
            u32_word(&mut out, id as u32);
            u64_word(&mut out, sigma.len() as u64);
            if node.num_children > 1 {
                nonuniform |= (0..nh).any(|i| sigma[i].to_bits() != sigma[nh+i].to_bits());
            }
            assert!(sigma.iter().all(|x| x.is_finite()));
            for v in sigma { u32_word(&mut out, v.to_bits()); }
        }
        assert!(nonuniform, "query must exercise nonuniform strategy");
        out
    }
    fn device_image(gpu: &GpuSolver) -> R<Vec<u8>> {
        gpu.synchronize()?;
        let mut out = b"E041GPU1".to_vec();
        for d in [&gpu.d_regrets[0],&gpu.d_regrets[1],&gpu.d_strat[0],&gpu.d_strat[1]] {
            let v = gpu.stream.clone_dtoh(d).map_err(e)?;
            assert!(v.iter().all(|x| x.is_finite()));
            assert!(v.windows(2).any(|x| x[0].to_bits() != x[1].to_bits()));
            u64_word(&mut out, v.len() as u64);
            for x in v { u32_word(&mut out, x.to_bits()); }
        }
        Ok(out)
    }
    fn retain(dir: &Path, name: &str, bytes: &[u8], files: &mut Vec<Value>) -> R<()> {
        let file = std::fs::OpenOptions::new().write(true).create_new(true).open(dir.join(name)).map_err(e)?;
        let mut w = BufWriter::new(file);
        w.write_all(bytes).map_err(e)?; w.flush().map_err(e)?; w.get_ref().sync_all().map_err(e)?;
        files.push(json!({"file":name,"bytes":bytes.len()})); Ok(())
    }
    fn pair(dir: &Path, label: &str, a: Vec<u8>, b: Vec<u8>, files: &mut Vec<Value>) -> R<()> {
        retain(dir,&format!("{label}.reference.bin"),&a,files)?;
        retain(dir,&format!("{label}.candidate.bin"),&b,files)?;
        assert_eq!(a,b,"{label}"); Ok(())
    }
    fn saves(dir: &Path, label: &str, a: &Solver, b: &Solver, files: &mut Vec<Value>) -> R<()> {
        let mut bytes = Vec::new();
        for (arm,s) in [("reference",a),("candidate",b)] {
            let name = format!("{label}.{arm}.save");
            let path = dir.join(&name);
            assert!(!path.exists() && !path.with_extension("save.tmp").exists());
            s.save(path.to_str().ok_or("output encoding")?)?;
            let raw = std::fs::read(path).map_err(e)?;
            files.push(json!({"file":name,"bytes":raw.len()})); bytes.push(raw);
        }
        assert_eq!(bytes[0],bytes[1]); Ok(())
    }
    fn geometry(g: &GpuSolver) -> (usize,usize,[usize;4]) {
        (g.h_staging.ptr as usize,g.h_staging.len,
         [g.d_regrets[0].len(),g.d_regrets[1].len(),g.d_strat[0].len(),g.d_strat[1].len()])
    }
