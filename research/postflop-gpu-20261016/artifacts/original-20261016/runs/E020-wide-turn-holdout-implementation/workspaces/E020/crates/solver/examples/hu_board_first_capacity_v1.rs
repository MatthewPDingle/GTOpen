//! Read-only topology count for one complete public runout. No solve or arena.
#[allow(dead_code)]
#[path="research_sampled/state.rs"] mod state;
#[allow(dead_code)]
#[path="research_sampled/poker_reference_v1.rs"] mod poker_reference_v1;
#[allow(dead_code)]
#[path="research_sampled/observation_v1.rs"] mod observation_v1;
#[allow(dead_code)]
#[path="research_sampled/batch_queries_v1.rs"] mod batch_queries_v1;
use serde_json::json;
use state::State;
use poker_reference_v1::Game;

#[derive(Default)]
struct Counts {
    actions: [[u64; 3]; 2],
    action_slots: [[u64; 3]; 2],
    chance: u64,
    fold: u64,
    showdown: u64,
    depth: usize,
}

fn visit(s: State, c: &solver::TreeConfig, depth: usize, out: &mut Counts) {
    assert!(depth < 30);
    out.depth = out.depth.max(depth);
    match s.kind {
        0 => {
            let actions = s.actions(c);
            out.actions[s.player as usize][s.street as usize] += 1;
            out.action_slots[s.player as usize][s.street as usize] += actions.len() as u64;
            for a in actions { visit(s.act(c,a),c,depth+1,out); }
        },
        1 => { out.chance += 1; visit(s.deal(),c,depth+1,out); },
        2 => out.fold += 1,
        3 => out.showdown += 1,
        _ => panic!("unexpected state kind"),
    }
}

fn main() -> Result<(),Box<dyn std::error::Error>> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    assert_eq!(args.len(),1);
    let source = std::fs::read_to_string(&args[0])?;
    let context = serde_json::from_str(&source)?;
    let game = Game::new(&context);
    let mut branches = Vec::new();
    let mut decisions = game.kinds.iter().filter(|&&k|k==0).count() as u64;
    for (i,&kind) in game.kinds.iter().enumerate() {
        if kind != 2 { continue; }
        let mut counts = Counts::default();
        visit(State::root(&game.configs[i]),&game.configs[i],0,&mut counts);
        decisions += counts.actions.iter().flatten().sum::<u64>();
        branches.push(json!({"branch":i,"actions_by_player_street":counts.actions,
            "action_slots_by_player_street":counts.action_slots,
            "chance_nodes":counts.chance,"fold_leaves":counts.fold,
            "showdown_leaves":counts.showdown,"maximum_depth":counts.depth}));
    }
    // Existing query builder walks the same public topology via a separate
    // traversal. For a single deal every actor/history supplies one raw query.
    let mut queries = Vec::new();
    for deal in [[0,5,10,15,20,25,30,35,40],[48,49,44,45,0,4,8,12,16]] {
        let q = batch_queries_v1::Queries::build(&game,&[deal],1_000_000)?;
        assert_eq!(q.raw_len() as u64,decisions);
        queries.push(json!({"deal":deal,"raw_queries":q.raw_len(),"canonical_queries":q.observations.len()}));
    }
    println!("{}",json!({"passed":true,"decision_histories_per_complete_runout":decisions,
        "preflop_decisions":game.kinds.iter().filter(|&&k|k==0).count(),"branches":branches,
        "existing_query_builder_checks":queries,"gpu_used":false,"strategy_allocated":false,
        "scope":"Topology count only. No all-pair evaluation, convergence, speed or accuracy claim."}));
    Ok(())
}
