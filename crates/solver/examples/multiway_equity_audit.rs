//! Read-only diagnostic: compare production pairwise-product pricing with
//! shared-board Monte Carlo for the arriving ranges in a /preflop/node JSON.
//! Does not solve a game or replace the running server's state.
use solver::preflop::equity::{class_index, class_label, class_combos};
use solver::evaluator::evaluate7;
use serde_json::{Value, json};

struct Rng(u64);
impl Rng {
    fn next(&mut self) -> u64 {
        self.0 = self.0.wrapping_add(0x9e3779b97f4a7c15);
        let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xbf58476d1ce4e5b9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94d049bb133111eb);
        z ^ (z >> 31)
    }
    fn unit(&mut self) -> f64 { (self.next() >> 11) as f64 / (1u64 << 53) as f64 }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    assert!(args.len() >= 4, "usage: multiway_equity_audit node.json equity.bin session.json [samples]");
    let node: Value = serde_json::from_str(&std::fs::read_to_string(&args[1]).unwrap()).unwrap();
    let session: Value = serde_json::from_str(&std::fs::read_to_string(&args[3]).unwrap()).unwrap();
    let config = &session["config"];
    let bytes = std::fs::read(&args[2]).unwrap();
    assert_eq!(bytes.len(), 4 + 169 * 169 * 4);
    let table: Vec<f64> = bytes[4..].chunks_exact(4).map(|b| f32::from_le_bytes(b.try_into().unwrap()) as f64).collect();
    let samples: usize = args.get(4).map(|s| s.parse().unwrap()).unwrap_or(200_000);
    assert!(samples > 0);
    let actor = node["actor"].as_u64().unwrap() as usize;
    let opponents: Vec<usize> = node["live"].as_array().unwrap().iter().enumerate()
        .filter(|(i,v)| *i != actor && v.as_bool().unwrap()).map(|(i,_)|i).collect();
    let mut distributions = Vec::new();
    let mut samplers = Vec::new();
    let mut opponent_summary = Vec::new();
    for &p in &opponents {
        let reach: Vec<f64> = node["reaches_all"][p].as_array().unwrap().iter().map(|v|v.as_f64().unwrap()).collect();
        let mass: f64 = (0..169).map(|h|reach[h] * class_combos(h) as f64).sum();
        distributions.push((0..169).map(|h|reach[h] * class_combos(h) as f64 / mass).collect::<Vec<_>>());
        let mut combos = Vec::new();
        let mut cumulative = 0.0;
        for a in 0u8..52 { for b in a+1..52 {
            let h = class_index(a/4, b/4, a%4 == b%4);
            cumulative += reach[h];
            combos.push((cumulative, [a,b]));
        }}
        for (w,_) in &mut combos { *w /= cumulative; }
        samplers.push(combos);
        let mut top: Vec<_> = (0..169).map(|h|(h, reach[h]*class_combos(h) as f64 / mass)).collect();
        top.sort_by(|a,b|b.1.total_cmp(&a.1));
        opponent_summary.push(json!({"position":node["positions"][p],"combos":mass,
            "top_classes":top.iter().take(10).map(|(h,w)|json!({"hand":class_label(*h),"share":w})).collect::<Vec<_>>()}));
    }
    let pot = node["pot"].as_f64().unwrap();
    let invested = node["invested"][actor].as_f64().unwrap();
    let call_to = node["actions"].as_array().unwrap().iter().find(|a|a["kind"] == "call").unwrap()["to"].as_f64().unwrap();
    let call_cost = call_to - invested;
    let final_pot = pot + call_cost;
    // Reproduce the static multiway pricing branch, not the HU fitted model.
    assert!(opponents.len() >= 2, "this diagnostic compares multiway terminals");
    let cap = config["rake_cap"].as_f64().unwrap();
    let uncapped = final_pot * config["rake_pct"].as_f64().unwrap() / 100.0;
    let rake = if cap > 0.0 { uncapped.min(cap) } else { uncapped };
    let left = config["stack"].as_f64().unwrap() - call_to + config["ante"].as_f64().unwrap();
    let spr = (left / final_pot).max(0.0);
    let n = node["positions"].as_array().unwrap().len();
    let postflop_order: Vec<usize> = [n-2,n-1].into_iter().chain(0..n-2)
        .filter(|p| *p == actor || opponents.contains(p)).collect();
    let rank = postflop_order.iter().position(|p| *p == actor).unwrap();
    let realization = if config["realization"] == "raw" { 1.0 } else {
        1.0 + 0.16 * (rank as f64 / opponents.len() as f64 - 0.5) * spr.min(8.0) / 8.0
    };
    let mut results = Vec::new();
    for (label, hero) in [("KQo",[44u8,41u8]),("AQo",[48,41]),("KQs",[44,40]),("76s",[20,16]),("AA",[48,49])] {
        let h = class_index(hero[0]/4,hero[1]/4,hero[0]%4 == hero[1]%4);
        assert_eq!(class_label(h),label);
        let pairwise: Vec<f64> = distributions.iter().map(|d|(0..169).map(|j|table[h*169+j]*d[j]).sum()).collect();
        let product = pairwise.iter().product::<f64>();
        let mut rng = Rng(20260910 + h as u64);
        let mut sum = 0.0;
        let mut squares = 0.0;
        let mut pair_sums = vec![0.0; opponents.len()];
        let mut accepted = 0;
        while accepted < samples {
            let mut mask = (1u64 << hero[0]) | (1u64 << hero[1]);
            let mut hands = vec![hero];
            let mut collision = false;
            // Reject the entire tuple, not one opponent at a time: sample
            // the product of ranges conditioned on all cards being distinct.
            for sampler in &samplers {
                let u = rng.unit();
                let i = sampler.partition_point(|(w,_)| *w <= u).min(sampler.len()-1);
                let hand = sampler[i].1;
                let bits = (1u64 << hand[0]) | (1u64 << hand[1]);
                if mask & bits != 0 { collision = true; break; }
                mask |= bits; hands.push(hand);
            }
            if collision { continue; }
            let mut board = Vec::new();
            while board.len() < 5 {
                let card = (rng.next() % 52) as u8;
                if mask & (1u64 << card) != 0 { continue; }
                mask |= 1u64 << card; board.push(card);
            }
            let values: Vec<_> = hands.iter().map(|hand|evaluate7(&[hand[0],hand[1],board[0],board[1],board[2],board[3],board[4]])).collect();
            let best = *values.iter().max().unwrap();
            let winners = values.iter().filter(|&&v|v == best).count();
            let eq = if values[0] == best { 1.0 / winners as f64 } else {0.0};
            sum += eq; squares += eq*eq;
            for (i,&v) in values.iter().skip(1).enumerate() { pair_sums[i] += if values[0] > v {1.0} else if values[0] == v {0.5} else {0.0}; }
            accepted += 1;
        }
        let equity = sum / samples as f64;
        let se = ((squares / samples as f64 - equity*equity) / samples as f64).sqrt();
        results.push(json!({"hand":label,"pairwise_equities":pairwise,"product_equity":product,
            "shared_board_equity":equity,"mc_95_half_width":1.96*se,
            "same_deal_pairwise_product":pair_sums.iter().map(|x| x/samples as f64).product::<f64>(),
            "production_call_minus_fold_bb":(final_pot-rake)*product*realization-call_cost,
            "shared_board_same_realization_call_minus_fold_bb":(final_pot-rake)*equity*realization-call_cost,
            "current_actions":node["actions"].as_array().unwrap().iter().enumerate().map(|(a,action)|json!({"action":action["label"],"frequency":node["strategy"][a*169+h]})).collect::<Vec<_>>()}));
    }
    println!("{}",serde_json::to_string_pretty(&json!({"samples_per_hand":samples,"final_pot_bb":final_pot,"call_cost_bb":call_cost,"starting_pot_rake_bb":rake,"realization":realization,"opponents":opponent_summary,"results":results,"scope":"Fixed current ranges; shared board and compatible live cards, ties split. Folded-player card removal and future postflop betting are not modeled. Not a replacement equilibrium or full-game call EV."})).unwrap());
}
