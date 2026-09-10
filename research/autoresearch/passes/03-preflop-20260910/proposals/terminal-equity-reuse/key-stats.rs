// Host-only, opt-in diagnostic. Does not modify source layouts, reaches, arenas,
// GPU allocations or launches. All temporary records are dropped before return.
fn multiway_terminal_key_stats(s: &PreflopSolver, sources: &[u32], terms: &[u32]) {
    use std::collections::BTreeMap;
    use std::time::Instant;
    #[derive(Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
    struct Key { len: u8, ordered_sources: [u32; 8] }
    #[derive(Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
    struct Record { key: Key, seat: u8, node: u32 }
    #[derive(Default)]
    struct Counts {
        tasks: usize,
        groups: usize,
        duplicate_groups: usize,
        max_multiplicity: usize,
        histogram: BTreeMap<usize, usize>,
        // opponent count -> [tasks, groups, duplicate groups]
        by_opponents: BTreeMap<usize, [usize; 3]>,
        examples: Vec<serde_json::Value>,
    }
    impl Counts {
        fn add(&mut self, multiplicity: usize, opponents: usize) {
            self.tasks += multiplicity;
            self.groups += 1;
            self.duplicate_groups += usize::from(multiplicity > 1);
            self.max_multiplicity = self.max_multiplicity.max(multiplicity);
            *self.histogram.entry(multiplicity).or_default() += 1;
            let by = self.by_opponents.entry(opponents).or_default();
            by[0] += multiplicity;
            by[1] += 1;
            by[2] += usize::from(multiplicity > 1);
        }
        fn report(&self) -> serde_json::Value {
            let bytes = self.duplicate_groups.checked_mul(NUM_CLASSES).and_then(|n| n.checked_mul(4));
            let layouts: Vec<_> = [1usize, 7, 32].into_iter().map(|batch| {
                serde_json::json!({
                    "particle_batch": batch,
                    "batch_count": super::multiway::SAMPLES.div_ceil(batch),
                    "one_batch_duplicate_sum_cache_bytes": bytes,
                    "all_batches_duplicate_sum_cache_bytes": bytes.and_then(|n| n.checked_mul(super::multiway::SAMPLES.div_ceil(batch))),
                })
            }).collect();
            serde_json::json!({
                "live_tasks": self.tasks,
                "unique_keys": self.groups,
                "duplicate_groups": self.duplicate_groups,
                "duplicate_tasks_avoided": self.tasks - self.groups,
                "duplicate_task_fraction": if self.tasks == 0 { 0.0 } else { (self.tasks-self.groups) as f64/self.tasks as f64 },
                "max_multiplicity": self.max_multiplicity,
                "group_multiplicity_histogram": self.histogram,
                "opponent_count_tasks_groups_duplicate_groups": self.by_opponents,
                "cache_layout_estimates": layouts,
                "duplicate_examples": self.examples,
            })
        }
    }

    let start = Instant::now();
    if s.n > 9 || sources.len() != s.nodes.len().saturating_mul(s.n) {
        eprintln!("preflop mw key stats: skipped invalid diagnostic source dimensions");
        return;
    }
    let Some(tasks) = terms.iter().try_fold(0usize, |total, &nd| {
        total.checked_add(s.nodes[nd as usize].live.count_ones() as usize)
    }) else {
        eprintln!("preflop mw key stats: skipped task count overflow");
        return;
    };
    let Some(requested_bytes) = tasks.checked_mul(std::mem::size_of::<Record>()) else {
        eprintln!("preflop mw key stats: skipped record size overflow");
        return;
    };
    let mut records = Vec::<Record>::new();
    if let Err(err) = records.try_reserve_exact(tasks) {
        eprintln!("preflop mw key stats: skipped {requested_bytes}-byte host diagnostic allocation: {err}");
        return;
    }
    for &node in terms {
        let live = s.nodes[node as usize].live;
        for p in 0..s.n {
            if (live >> p) & 1 == 0 { continue; }
            let mut key = Key { len: 0, ordered_sources: [0; 8] };
            for q in 0..s.n {
                if q == p || (live >> q) & 1 == 0 { continue; }
                key.ordered_sources[key.len as usize] = sources[node as usize * s.n + q];
                key.len += 1;
            }
            records.push(Record { key, seat: p as u8, node });
        }
    }
    let collect_ms = start.elapsed().as_secs_f64() * 1000.0;
    let before_sort = Instant::now();
    // This orders records by their complete key; it does NOT reorder sources
    // inside a key or alter the opponent multiplication order in the solver.
    records.sort_unstable();
    let sort_ms = before_sort.elapsed().as_secs_f64() * 1000.0;
    let before_count = Instant::now();
    let mut seats: Vec<Counts> = (0..s.n).map(|_| Counts::default()).collect();
    let mut union = Counts::default();
    let mut cross_seat = Counts::default();
    let mut cross_seat_count_histogram = BTreeMap::<usize, usize>::new();
    let mut at = 0;
    while at < records.len() {
        let key = records[at].key;
        let mut end = at + 1;
        while end < records.len() && records[end].key == key { end += 1; }
        let group = &records[at..end];
        union.add(group.len(), key.len as usize);
        let mut distinct_seats = 0usize;
        let mut seat_at = 0;
        while seat_at < group.len() {
            let p = group[seat_at].seat as usize;
            let mut seat_end = seat_at + 1;
            while seat_end < group.len() && group[seat_end].seat as usize == p { seat_end += 1; }
            distinct_seats += 1;
            let count = seat_end - seat_at;
            seats[p].add(count, key.len as usize);
            if count > 1 && seats[p].examples.len() < 3 {
                seats[p].examples.push(serde_json::json!({
                    "ordered_sources": &key.ordered_sources[..key.len as usize],
                    "node_examples": group[seat_at..seat_end].iter().take(8).map(|r| r.node).collect::<Vec<_>>(),
                    "multiplicity": count,
                }));
            }
            seat_at = seat_end;
        }
        *cross_seat_count_histogram.entry(distinct_seats).or_default() += 1;
        if distinct_seats > 1 {
            cross_seat.add(group.len(), key.len as usize);
            if cross_seat.examples.len() < 5 {
                cross_seat.examples.push(serde_json::json!({
                    "ordered_sources": &key.ordered_sources[..key.len as usize],
                    "task_examples": group.iter().take(12).map(|r| serde_json::json!({"seat":r.seat,"node":r.node})).collect::<Vec<_>>(),
                    "tasks": group.len(), "distinct_seats": distinct_seats,
                }));
            }
        }
        at = end;
    }
    let count_ms = before_count.elapsed().as_secs_f64() * 1000.0;
    let per_seat_unique_sum: usize = seats.iter().map(|s| s.groups).sum();
    let record_capacity = records.capacity();
    let record_payload_bytes = record_capacity.checked_mul(std::mem::size_of::<Record>());
    let per_seat: Vec<_> = seats.iter().enumerate().map(|(p,c)| serde_json::json!({
        "seat": p, "position": &s.cfg.positions[p], "counts": c.report(),
    })).collect();
    println!("preflop mw key stats: {}", serde_json::json!({
        "diagnostic_only": true,
        "model": s.multiway_equity_model(),
        "particles": super::multiway::SAMPLES,
        "multiway_terminals": terms.len(),
        "per_traverser": per_seat,
        "average_check_union": union.report(),
        "cross_seat_groups_only": cross_seat.report(),
        "union_group_distinct_seats_histogram": cross_seat_count_histogram,
        "within_traverser_duplicate_tasks": tasks - per_seat_unique_sum,
        "additional_frozen_cross_seat_duplicate_tasks": per_seat_unique_sum - union.groups,
        "timing_ms": {"collect":collect_ms,"sort":sort_ms,"count":count_ms,"total_before_print":start.elapsed().as_secs_f64()*1000.0},
        "host_memory_estimate": {
            "record_bytes":std::mem::size_of::<Record>(), "record_capacity":record_capacity,
            "dominant_record_payload_bytes":record_payload_bytes,
            "note":"Payload estimate, not measured RSS: excludes allocator overhead, small histograms/examples/JSON. In-place unstable sort adds no second record array. All diagnostic storage drops on return."
        },
        "interpretation":"Static source identity only, not active-reach savings or a speedup measurement. Cross-seat reuse requires one frozen average-check reach snapshot; learning sweeps invalidate it. Cache bytes exclude maps, activity flags and scatter work. Null byte estimates mean arithmetic overflow."
    }));
}
