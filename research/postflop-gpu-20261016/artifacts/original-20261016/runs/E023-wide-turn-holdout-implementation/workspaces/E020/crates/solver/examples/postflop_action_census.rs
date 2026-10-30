//! CPU-only census of action spans in the registered postflop benchmark trees.
//! cargo run --release -p solver --features gpu --example postflop_action_census
//! The gpu feature exposes GpuPlan; this example never initializes CUDA, builds
//! a GPU solver, compiles kernels, allocates device memory, or solves a game.

#[cfg(not(feature = "gpu"))]
fn main() {
    eprintln!("postflop_action_census requires --features gpu to expose the CPU planner");
    std::process::exit(2);
}

#[cfg(feature = "gpu")]
fn main() {
    census::run();
}

#[cfg(feature = "gpu")]
mod census {
    use serde_json::{json, Value};
    use solver::gpu::plan::GpuPlan;
    use solver::tree::KIND_ACTION;
    use solver::{Spot, SpotConfig};
    use std::collections::BTreeMap;
    use std::io::{self, Write};
    use std::time::Instant;

    #[derive(Clone, Copy, Default)]
    struct Counts {
        spans: u64,
        nodes: u64,
        child_edges: u64,
        actor_hand_rows: u64,
    }

    impl Counts {
        fn add(&mut self, other: Self) {
            self.spans += other.spans;
            self.nodes += other.nodes;
            self.child_edges += other.child_edges;
            self.actor_hand_rows += other.actor_hand_rows;
        }

        fn values(self, nh: [usize; 2], raked: bool) -> Value {
            let both_hands = (nh[0] + nh[1]) as u64;
            let evaluation_modes = if raked { 2 } else { 1 };
            json!({
                "nonempty_spans": self.spans,
                "action_nodes": self.nodes,
                "child_edges": self.child_edges,
                "training_down_kernel_launches_per_iteration": 2 * self.spans,
                "training_up_kernel_launches_per_iteration": 2 * self.spans,
                "training_action_node_visits_per_iteration": 2 * self.nodes,
                "training_down_hand_visits_per_iteration": 2 * self.actor_hand_rows,
                "training_up_hand_visits_per_iteration": both_hands * self.nodes,
                "training_up_child_hand_visits_per_iteration": both_hands * self.child_edges,
                "evaluation_down_kernel_launches_per_check": self.spans,
                "evaluation_up_kernel_launches_per_check": 2 * evaluation_modes * self.spans,
                "evaluation_down_hand_visits_per_check": self.actor_hand_rows,
                "evaluation_up_hand_visits_per_check": evaluation_modes * both_hands * self.nodes,
            })
        }

        fn fractions(self, total: Self) -> Value {
            let ratio = |part: u64, all: u64| {
                if all == 0 { 0.0 } else { part as f64 / all as f64 }
            };
            json!({
                "span_fraction": ratio(self.spans, total.spans),
                "action_node_fraction": ratio(self.nodes, total.nodes),
                "training_action_node_visit_fraction": ratio(self.nodes, total.nodes),
                "training_up_hand_visit_fraction": ratio(self.nodes, total.nodes),
                "training_down_hand_visit_fraction": ratio(self.actor_hand_rows, total.actor_hand_rows),
                "training_up_child_hand_visit_fraction": ratio(self.child_edges, total.child_edges),
            })
        }
    }

    fn emit(prefix: &str, value: Value) {
        println!("{prefix} {value}");
        io::stdout().flush().expect("flush action census");
    }

    pub fn run() {
        for (fixture_id, board, rake) in [
            ("rainbow", "Ks7h2d", 0.0),
            ("two-tone", "Ks7s2d", 0.05),
            ("river", "Ks7h2dQhTc", 0.05),
        ] {
            let mut config: SpotConfig =
                serde_json::from_str(include_str!("../../../bench_spot.json")).unwrap();
            config.board = board.into();
            config.tree.rake_pct = rake;
            config.tree.rake_cap = 3.0;
            let config_json = serde_json::to_value(&config).unwrap();
            emit("POSTFLOP_ACTION_CENSUS_STAGE", json!({
                "stage": "building", "fixture_id": fixture_id, "board": board,
                "cuda_initialized": false,
            }));
            let start = Instant::now();
            let spot = Spot::new(config).unwrap();
            let tree_build_ms = start.elapsed().as_secs_f64() * 1000.0;
            let start = Instant::now();
            let plan = GpuPlan::build(&spot, true);
            let plan_build_ms = start.elapsed().as_secs_f64() * 1000.0;
            let nh = [spot.hands[0].len(), spot.hands[1].len()];
            let mut total = Counts::default();
            let mut eligible = Counts::default();
            let mut by_common_na: BTreeMap<usize, Counts> = BTreeMap::new();
            let mut mixed = Counts::default();
            let mut levels = Vec::new();
            let mut overall_na_histogram: BTreeMap<usize, u64> = BTreeMap::new();
            for (level, span) in plan.action_spans.iter().enumerate() {
                if span.count == 0 {
                    continue;
                }
                let mut counts = Counts { spans: 1, ..Counts::default() };
                let mut histogram: BTreeMap<usize, u64> = BTreeMap::new();
                let mut actors = [0u64; 2];
                let end = (span.start + span.count) as usize;
                for &node_id in &plan.action_nodes[span.start as usize..end] {
                    let node = &spot.tree.nodes[node_id as usize];
                    assert_eq!(node.kind, KIND_ACTION);
                    let na = node.num_children as usize;
                    let actor = node.player as usize;
                    assert!(actor < 2 && na > 0);
                    counts.nodes += 1;
                    counts.child_edges += na as u64;
                    counts.actor_hand_rows += nh[actor] as u64;
                    actors[actor] += 1;
                    *histogram.entry(na).or_default() += 1;
                    *overall_na_histogram.entry(na).or_default() += 1;
                }
                let common_na = if histogram.len() == 1 {
                    histogram.keys().next().copied()
                } else {
                    None
                };
                let qualifies = matches!(common_na, Some(2 | 3 | 4));
                total.add(counts);
                if qualifies {
                    eligible.add(counts);
                }
                if let Some(na) = common_na {
                    by_common_na.entry(na).or_default().add(counts);
                } else {
                    mixed.add(counts);
                }
                levels.push(json!({
                    "level": level, "span_start": span.start, "action_nodes": span.count,
                    "nodes_by_actor": actors, "action_count_histogram": histogram,
                    "common_action_count": common_na, "eligible_without_regrouping": qualifies,
                }));
            }
            assert_eq!(total.nodes, plan.action_nodes.len() as u64);
            let homogeneous: Vec<Value> = by_common_na.into_iter().map(|(na, counts)| json!({
                "action_count": na, "counts": counts.values(nh, rake > 0.0),
                "fractions_of_all_actions": counts.fractions(total),
            })).collect();
            emit("POSTFLOP_ACTION_CENSUS", json!({
                "schema_version": 1, "fixture_id": fixture_id, "board": board,
                "config": config_json, "use_isomorphism": true, "iso_active": plan.iso_active,
                "hands": nh, "tree_nodes": spot.tree.nodes.len(), "plan_levels": plan.num_levels,
                "tree_build_ms": tree_build_ms, "plan_build_ms": plan_build_ms,
                "action_count_histogram": overall_na_histogram,
                "total": total.values(nh, rake > 0.0),
                "eligible_homogeneous_2_3_4": eligible.values(nh, rake > 0.0),
                "eligible_fractions": eligible.fractions(total),
                "homogeneous_by_action_count": homogeneous,
                "mixed": mixed.values(nh, rake > 0.0), "levels": levels,
                "cuda_initialized": false, "solver_iterations": 0,
                "visit_definition": "one node visit per player sweep; two training sweeps per iteration; separate down/up hand rows and child visits describe scheduled work, not elapsed time or occupancy",
                "limits": "CPU structure census only; no GPU resource or speed measurement; fractions do not weight individual instructions or kernel latency",
            }));
        }
    }
}
