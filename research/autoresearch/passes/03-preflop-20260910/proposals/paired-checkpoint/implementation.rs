#[derive(Clone, Copy)]
struct CheckpointNeeds {
    br: bool,
    avg: bool,
}

#[derive(Default)]
struct CheckpointValues {
    // None is an unrequested/pruned positive-zero vector. Materialize only
    // outputs actually used; both upward reductions still include every action.
    br: Option<Vec<f32>>,
    avg: Option<Vec<f32>>,
}

impl PreflopSolver {
    /// Read-only paired evaluation. Learning traversal and its pruning/update
    /// semantics remain separate. None means canceled, never a completed zero.
    fn traverse_checkpoint(
        &self, node: usize, p: usize, reaches: &mut [Vec<f32>],
        br_mode: u8, needs: CheckpointNeeds, depth: u32,
    ) -> Option<CheckpointValues> {
        if !needs.br && !needs.avg { return Some(CheckpointValues::default()); }
        #[cfg(test)]
        checkpoint_tests::observe_checkpoint_visit(self);
        if depth < PAR_DEPTH && self.stop_requested() { return None; }
        let nd = &self.nodes[node];
        if nd.kind != KIND_ACTION {
            let mut values = vec![0f32; NUM_CLASSES];
            self.terminal_value(node, p, reaches, &mut values);
            return Some(match (needs.br, needs.avg) {
                (true, true) => CheckpointValues { br: Some(values.clone()), avg: Some(values) },
                (true, false) => CheckpointValues { br: Some(values), avg: None },
                (false, true) => CheckpointValues { br: None, avg: Some(values) },
                _ => unreachable!(),
            });
        }
        let actor = nd.actor as usize;
        let na = nd.actions.len();
        let child_start = nd.child_start as usize;
        let forced = self.forced_sigma(node);
        let has_forced = forced.is_some();
        let frozen = self.seat_frozen[actor];
        let sigma = forced.unwrap_or_else(|| self.average_strategy(node));
        assert_eq!(sigma.len(), na * NUM_CLASSES);
        let maximize = actor == p && (br_mode == 2 ||
            (br_mode == 3 && !has_forced && !frozen));
        let child_needs: Vec<CheckpointNeeds> = (0..na).map(|a| {
            let zero = self.prune && na > 1 &&
                sigma[a * NUM_CLASSES..(a + 1) * NUM_CLASSES].iter().all(|&x| x == 0.0);
            CheckpointNeeds { br: needs.br && (!zero || maximize), avg: needs.avg && !zero }
        }).collect();

        let vals: Vec<CheckpointValues> = if depth < PAR_DEPTH && na > 1 {
            let base: &[Vec<f32>] = reaches;
            (0..na).into_par_iter().map(|a| {
                let want = child_needs[a];
                if !want.br && !want.avg { return Some(CheckpointValues::default()); }
                let mut r = base.to_vec();
                for h in 0..NUM_CLASSES {
                    r[actor][h] = base[actor][h] * sigma[a * NUM_CLASSES + h];
                }
                self.traverse_checkpoint(self.children[child_start + a] as usize,
                    p, &mut r, br_mode, want, depth + 1)
            }).collect::<Option<Vec<_>>>()?
        } else {
            let saved = reaches[actor].clone();
            let mut vals = Vec::with_capacity(na);
            for a in 0..na {
                let want = child_needs[a];
                if !want.br && !want.avg { vals.push(CheckpointValues::default()); continue; }
                for h in 0..NUM_CLASSES {
                    reaches[actor][h] = saved[h] * sigma[a * NUM_CLASSES + h];
                }
                match self.traverse_checkpoint(self.children[child_start + a] as usize,
                    p, reaches, br_mode, want, depth + 1) {
                    Some(v) => vals.push(v),
                    None => { reaches[actor].copy_from_slice(&saved); return None; }
                }
            }
            reaches[actor].copy_from_slice(&saved);
            vals
        };
        if depth < PAR_DEPTH && self.stop_requested() { return None; }
        let combine = |best_response: bool| {
            let mut out = vec![0f32; NUM_CLASSES];
            if actor == p {
                for h in 0..NUM_CLASSES {
                    if best_response && maximize {
                        let mut best = f32::NEG_INFINITY;
                        for child in &vals {
                            let v = child.br.as_ref().map_or(0.0, |v|v[h]);
                            best = best.max(v);
                        }
                        out[h] = best;
                    } else {
                        let mut value = 0f32;
                        for (a, child) in vals.iter().enumerate() {
                            let child = if best_response { &child.br } else { &child.avg };
                            value += sigma[a * NUM_CLASSES + h] * child.as_ref().map_or(0.0, |v|v[h]);
                        }
                        out[h] = value;
                    }
                }
            } else {
                for child in &vals {
                    let child = if best_response { &child.br } else { &child.avg };
                    for h in 0..NUM_CLASSES { out[h] += child.as_ref().map_or(0.0, |v|v[h]); }
                }
            }
            out
        };
        Some(CheckpointValues {
            br: needs.br.then(||combine(true)), avg: needs.avg.then(||combine(false)),
        })
    }

    /// Completed best-response gaps and average EVs, or None when canceled.
    /// A canceled recursion is latched even if the stop flag is later cleared.
    fn checkpoint_gaps_and_evs(&self) -> Option<(Vec<f64>, Vec<f64>)> {
        if self.stop_requested() { return None; }
        let pairs: Vec<(f64, f64)> = (0..self.n).into_par_iter().map(|p| {
            let mut reaches = self.root_reaches();
            let values = self.traverse_checkpoint(0, p, &mut reaches,
                if self.constrained_br(p) {3} else {2}, CheckpointNeeds {br:true,avg:true}, 0)?;
            let br = values.br.expect("requested BR root");
            let avg = values.avg.expect("requested average root");
            let (mut gap,mut ev) = (0f64,0f64);
            for h in 0..NUM_CLASSES {
                let weight = class_prob(h) as f64;
                // Preserve subtraction in f32 before promotion, as in the
                // original CPU checkpoint; separate f64 dots are not equivalent.
                gap += weight * (br[h] - avg[h]) as f64;
                ev += weight * avg[h] as f64;
            }
            Some((gap,ev))
        }).collect::<Option<Vec<_>>>()?;
        if self.stop_requested() { return None; }
        Some(pairs.into_iter().unzip())
    }
}

