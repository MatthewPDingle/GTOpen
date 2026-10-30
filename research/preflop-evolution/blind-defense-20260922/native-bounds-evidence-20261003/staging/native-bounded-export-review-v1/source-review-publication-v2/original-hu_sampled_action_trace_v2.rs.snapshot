//! Version 2 binds conditional targets to the exact original policy transport.
#[path="research_sampled/state.rs"] mod state;
#[path="research_sampled/poker_reference_v1.rs"] mod poker_reference_v1;
#[path="research_sampled/observation_v1.rs"] mod observation_v1;
#[path="research_sampled/policy_walk_allin_v1.rs"] mod policy_walk_allin_v1;
#[path="research_sampled/allin_counts_v1.rs"] mod allin_counts_v1;
#[path="research_sampled/batch_queries_v1.rs"] mod batch_queries_v1;
#[path="research_sampled/action_trace_v1.rs"] mod action_trace_v1;
use poker_reference_v1::{Game, Key, sample_seed};
use batch_queries_v1::Queries;
use serde_json::{Value, json};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    assert_eq!(args.len(), 4);
    assert!(!std::path::Path::new(&args[3]).exists());
    let cs = std::fs::read_to_string(&args[0])?;
    let bs = std::fs::read_to_string(&args[1])?;
    let context: Value = serde_json::from_str(&cs)?;
    let batch: Value = serde_json::from_str(&bs)?;
    assert_eq!(batch["format"], 3);
    let game = Game::new(&context);
    let limit = batch["query_limit"].as_u64().unwrap() as usize;
    assert!(limit <= 1_000_000);
    let deals: Vec<[u8; 9]> = batch["deals"].as_array().unwrap().iter().map(|d|
        d.as_array().unwrap().iter().map(|x| {
            let v = x.as_u64().unwrap(); assert!(v < 52); v as u8
        }).collect::<Vec<_>>().try_into().unwrap()).collect();
    assert!(deals.len() <= 64, "Bounded diagnostic batches only");
    let equities = allin_counts_v1::equities(&batch, &deals);
    let queries = Queries::build(&game, &deals, limit)?;
    let policy_source = std::fs::read_to_string(&args[2])?;
    let transport: Value = serde_json::from_str(&policy_source)?;
    assert_eq!(transport["format"], 3);
    assert_eq!(transport["terminal_estimator"], "conditional-preflop-allin-v1");
    assert_eq!(transport["context_source"].as_str(), Some(cs.as_str()));
    assert_eq!(transport["batch_source"].as_str(), Some(bs.as_str()));
    let rows = transport["policies"].as_array().unwrap();
    assert_eq!(rows.len(), queries.observations.len());
    let mut policies = Vec::new();
    for (i, row) in rows.iter().enumerate() {
        let o = &queries.observations[i]; let k = o.key(); let n = queries.arities[i];
        assert_eq!(row["hi"], k.0.to_string()); assert_eq!(row["lo"], k.1.to_string());
        assert_eq!(row["actor"].as_u64().unwrap() as usize, o.actor);
        assert_eq!(row["n"].as_u64().unwrap() as usize, n);
        let p: [f64; 4] = row["probabilities"].as_array().unwrap().iter()
            .map(|x| x.as_f64().unwrap()).collect::<Vec<_>>().try_into().unwrap();
        assert!(p.iter().all(|v| v.is_finite() && *v >= 0.));
        assert!(p[n..].iter().all(|v| *v == 0.) && (p[..n].iter().sum::<f64>()-1.).abs() < 1e-12);
        policies.push(p);
    }
    let policy = |k: Key, n: usize| {
        let i = queries.lookup(k).expect("Missing visible observation");
        assert_eq!(queries.arities[i], n); policies[i]
    };
    let seed = batch["seed"].as_u64().unwrap();
    let mut traces = Vec::new(); let mut roots = Vec::new(); let mut records = Vec::new();
    let mut replacements = Vec::new(); let mut final_rng = Vec::new();
    for (did, deal) in deals.iter().enumerate() {
        let mut trace = action_trace_v1::Trace::new(&game, &policy, deal, equities[did]);
        let value = trace.pre(0, 1.);
        let mut traced = Vec::new();
        for (k, row) in &trace.rows {
            traced.push(json!({"query": queries.lookup(*k).unwrap(), "actor": row.actor,
                "n": row.n, "action_values": row.actions, "values": row.value, "reach": row.reach}));
        }
        traces.push(json!({"deal_index": did, "values": value, "nodes": traced}));
        for updater in 0..2 {
            let mut walk = policy_walk_allin_v1::PolicyWalk::new(&game, &policy, deal, updater,
                sample_seed(seed, did*2+updater), equities[did]);
            let sampled_value = walk.pre(0);
            roots.push(json!([did, updater, sampled_value]));
            final_rng.push(walk.rng.to_string());
            for record in walk.records {
                let qi = queries.lookup(record.key).unwrap();
                let row = trace.rows.get(&record.key).expect("Sampled visit absent from full trace");
                assert_eq!(row.actor, if record.tag > 0 { updater } else { 1-updater });
                assert_eq!(row.n, record.tag.unsigned_abs() as usize);
                // Every original visit and sampled value is retained. Derived targets
                // are separate, indexed by deal and original global record position.
                if record.tag > 0 {
                    let mut advantages = [0.; 4];
                    for a in 0..row.n { advantages[a] = row.actions[a][updater]-row.value[updater]; }
                    replacements.push(json!({"record": records.len(), "deal": did,
                        "query": qi, "updater": updater, "advantages": advantages}));
                }
                records.push(json!([qi, updater, record.tag, record.values]));
            }
        }
    }
    let result = json!({"format":2, "method":"all-node-action-trace-v2", "policy_source":policy_source,
        "context_source":cs, "batch_source":bs, "traces":traces,
        "sampled_roots":roots, "sampled_records":records, "final_rng":final_rng,
        "conditional_targets":replacements, "diagnostic_only":true,
        "scope":"Future actions integrated at fixed sampled cards; visits and RNG unchanged. Does not apply existing exact initial-policy overrides or authorize replacement of their targets."});
    std::fs::write(&args[3], serde_json::to_vec(&result)?)?;
    Ok(())
}
