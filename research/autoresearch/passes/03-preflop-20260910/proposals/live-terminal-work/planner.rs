// Stable indices into the existing global term/probability arrays. Terms are
// kept in their original order within every traverser's immutable work span.
struct MultiwayTerminalPlan {
    work: Vec<u32>,
    spans: Vec<(u32, u32)>,
}

impl MultiwayTerminalPlan {
    fn build(s: &PreflopSolver, terms: &[u32]) -> Result<Self, String> {
        let mut out = Self { work: Vec::new(), spans: Vec::with_capacity(s.n) };
        for p in 0..s.n {
            let start = out.work.len();
            for (index, &nd) in terms.iter().enumerate() {
                if s.nodes[nd as usize].live & (1 << p) != 0 {
                    if out.work.len() >= u32::MAX as usize {
                        return Err("multiway terminal work exceeds 32-bit indexing".to_string());
                    }
                    out.work.push(index as u32);
                }
            }
            out.spans.push((start as u32, (out.work.len() - start) as u32));
        }
        Ok(out)
    }
    fn bytes(&self) -> usize { self.work.len() * std::mem::size_of::<u32>() }
}

fn terminal_work_preserves_plan(available: usize, slots: usize, bytes: usize,
    baseline: &MultiwayBatchPlan) -> Result<bool, String> {
    let Some(remaining) = available.checked_sub(bytes) else { return Ok(false); };
    let Some(candidate) = multiway_batch_plan(remaining, slots)? else { return Ok(false); };
    Ok(candidate.batch == baseline.batch && candidate.normalized_bytes == baseline.normalized_bytes)
}

