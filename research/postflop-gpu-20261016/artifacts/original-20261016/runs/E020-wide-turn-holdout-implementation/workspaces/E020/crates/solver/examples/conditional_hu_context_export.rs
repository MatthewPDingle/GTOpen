//! Read-only, position-independent HU export for continuation research.
//! SAVE PATH_JSON OUTPUT. This does not solve or access the live server.
use serde_json::{json, Value};
use solver::preflop::{equity::EquityTable, PreflopSolver};
use std::{fs::OpenOptions, io::Write, sync::Arc};

fn collect(
    s: &PreflopSolver, i: usize, path: Vec<usize>, seats: [usize; 2],
    dead_money: f64, nodes: &mut Vec<Value>,
) -> usize {
    let local = nodes.len();
    nodes.push(Value::Null);
    let n = &s.nodes[i];
    let mask = (1u32 << seats[0]) | (1u32 << seats[1]);
    assert_eq!(n.live & !mask, 0, "third live player in HU export");
    let actor = if n.kind == 0 {
        Some(seats.iter().position(|&p| p == n.actor as usize).expect("live actor"))
    } else { None };
    let winner = if n.kind == 1 {
        Some(seats.iter().position(|&p| p == n.winner as usize).expect("live winner"))
    } else { None };
    let invested = [n.invested[seats[0]], n.invested[seats[1]]];
    assert!((n.pot - invested.iter().sum::<f64>() - dead_money).abs() < 1e-8);
    let leaf = match n.kind {
        0 => Value::Null,
        1 => {
            assert_eq!(n.live.count_ones(), 1);
            let utilities: [f64; 2] = std::array::from_fn(|p|
                if Some(p) == winner { n.pot - invested[p] } else { -invested[p] });
            json!({"type":"fold", "utilities":utilities})
        },
        2 => {
            assert_eq!(n.live, mask);
            assert!((invested[0] - invested[1]).abs() < 1e-8, "unequal matched investments");
            // Preflop stack excludes the separately contributed dead ante.
            let remaining = s.cfg.stack + s.cfg.ante - invested[0];
            assert!(remaining >= -1e-8);
            let offsets = invested.map(|v| n.pot / 2. - v);
            json!({"type":if remaining > 1e-8 {"postflop"} else {"showdown"},
                "starting_pot":n.pot,"effective_stack":remaining.max(0.),
                "value_offsets":offsets})
        },
        _ => panic!("unsupported preflop node kind"),
    };
    let children: Vec<usize> = (0..n.actions.len()).map(|a| {
        let mut next = path.clone(); next.push(a);
        collect(s, s.child(i, a), next, seats, dead_money, nodes)
    }).collect();
    nodes[local] = json!({"original_node":i,"path":path,"kind":n.kind,
        "original_actor":n.actor,"actor":actor,"children":children,
        "strategy":if n.kind == 0 {s.average_strategy(i)} else {vec![]},
        "pot":n.pot,"invested":invested,"original_invested":n.invested,
        "original_live":n.live,"winner":winner,"original_winner":n.winner,
        "r":[n.r.get(seats[0]),n.r.get(seats[1])],"leaf":leaf,
        "actions":n.actions.iter().map(|a|json!({"kind":a.kind,"to":a.to,"label":a.label})).collect::<Vec<_>>()});
    local
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    assert_eq!(args.len(), 3, "SAVE PATH_JSON OUTPUT");
    assert!(!std::path::Path::new(&args[2]).exists(), "preserve evidence");
    let path: Vec<usize> = serde_json::from_str(&args[1])?;
    rayon::ThreadPoolBuilder::new().num_threads(4).build_global()?;
    assert!(std::path::Path::new("cache/preflop_eq169.bin").is_file(), "existing equity cache required");
    let eq = Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin", 20000));
    let s = PreflopSolver::load_game(&args[0], eq)?;
    assert!(s.iteration > 0, "incoming policy must come from a saved solve");
    // Fold utilities below implement no-flop-no-drop. Refuse other rake rules.
    assert!(s.cfg.no_flop_no_drop || s.cfg.rake_pct == 0. || s.cfg.rake_cap == 0.);
    let before = s.arena_snapshot();
    let (root, reaches) = s.walk(&path)?;
    assert_eq!(s.nodes[root].kind, 0, "root must be a decision");
    let live = s.nodes[root].live;
    assert_eq!(live.count_ones(), 2, "root must have exactly two live players");
    let order: Vec<_> = s.postflop_order().into_iter().filter(|p| live & (1 << p) != 0).collect();
    let seats = [order[0], order[1]];
    let dead_money = s.nodes[root].pot - seats.iter().map(|&p| s.nodes[root].invested[p]).sum::<f64>();
    assert!(dead_money >= -1e-8);
    let mut nodes = Vec::new();
    collect(&s, root, path.clone(), seats, dead_money, &mut nodes);
    let out = json!({"schema":"hu-context-v1","save":args[0],"iteration":s.iteration,
        "config":s.cfg,"root_path":path,"original_seats":seats,
        "positions":[s.cfg.positions[seats[0]],s.cfg.positions[seats[1]]],
        "postflop_order":[0,1],"dead_money":dead_money,
        "rake_fraction":s.cfg.rake_pct/100.,"rake_cap":s.cfg.rake_cap,
        "incoming_class_mass":[reaches[seats[0]],reaches[seats[1]]],
        "class_base":s.fit.as_ref().map(|f|f.class_base()),"nodes":nodes,
        "limitations":["Incoming ranges inherit the saved preflop approximation.",
            "Earlier folded players' private cards are not represented.",
            "This is an export, not a new solved continuation."]});
    assert_eq!(before, s.arena_snapshot(), "export changed source strategy");
    let mut output = OpenOptions::new().write(true).create_new(true).open(&args[2])?;
    output.write_all(&serde_json::to_vec_pretty(&out)?)?;
    println!("Exported {} nodes; OOP={} IP={}; dead money={dead_money}",
        nodes.len(), s.cfg.positions[seats[0]], s.cfg.positions[seats[1]]);
    Ok(())
}
