#[cfg(test)]
impl PreflopGpu {
    // Isolated-terminal tests replace the global term array. Rebuild indices
    // against that array too, rather than retaining a stale full-tree worklist.
    fn test_set_multiway_terms(&mut self, s: &PreflopSolver, terms: &[u32]) {
        assert!(self.learning_graphs.iter().all(Option::is_none) && self.eval_graph.is_none());
        let plan = MultiwayTerminalPlan::build(s, terms).unwrap();
        self.d_mw_terms = self.stream.clone_htod(terms).unwrap();
        self.mw_nterms = terms.len() as u32;
        self.d_mw_terminal_work = self.stream.clone_htod(if plan.work.is_empty() { &[0u32][..] } else { &plan.work }).unwrap();
        self.mw_terminal_spans = plan.spans;
        self.use_mw_terminal_work = 1;
    }
}

