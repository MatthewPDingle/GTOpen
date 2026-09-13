use super::*;
use crate::preflop::{PreflopConfig,convergence_research::Experiment,equity::EquityTable};
fn fixture(cal:bool)->PreflopSolver{
    let path=concat!(env!("CARGO_MANIFEST_DIR"),"/../../cache/preflop_eq169.bin");
    let bytes=std::fs::read(path).unwrap();
    let eq=Arc::new(EquityTable::load_or_build(path,u32::from_le_bytes(bytes[..4].try_into().unwrap())));
    let cfg:PreflopConfig=serde_json::from_value(serde_json::json!({"positions":["CO","BTN","SB","BB"],
        "stack":10,"posts":[0,0,0.5,1],"limp":true,"open_raises":[2],"raise_mults":[3],"max_raises":2,
        "add_allin":false,"rake_pct":5,"rake_cap":1,"realization":if cal{"calibrated"}else{"raw"}})).unwrap();
    let mut s=PreflopSolver::new(cfg,eq).unwrap();s.research_seed_quality_fixture_averages().unwrap();
    s.seat_frozen[2]=true;let node=s.child(0,1);
    let mut lock=vec![0.0;s.nodes[node].actions.len()*NUM_CLASSES];lock[..NUM_CLASSES].fill(1.0);
    s.point_locks.insert(node as u32,lock);s
}
fn gpu(s:&PreflopSolver,eps:Option<f32>,samples:u32)->PreflopGpu{
    let mut g=PreflopGpu::new(s,2000).unwrap();
    g.configure_research(Experiment::new("dcfr",samples,1000,42).unwrap()).unwrap();
    if let Some(eps)=eps{g.enable_research_behavioral_perturbation(eps).unwrap();}g
}
fn arenas(g:&PreflopGpu)->(Vec<f32>,Vec<f32>){
    (g.stream.clone_dtoh(&g.d_regrets).unwrap(),g.stream.clone_dtoh(&g.d_strat).unwrap())
}
fn near(a:&[f32],b:&[f64],tol:f64){
    assert_eq!(a.len(),b.len());for (i,(&a,&b)) in a.iter().zip(b).enumerate(){
        assert!(a.is_finite() && (a as f64-b).abs()<=tol*(1.0+b.abs()),"index {i}: {a} vs {b}");
    }
}

// Full node-indexed host recursion (no GPU level/slot layout and no shortcut
// tau*(Q-sigma.Q)). Explicit virtual-action transition matrices define regret.
struct Oracle<'a>{
    s:&'a PreflopSolver,p:usize,eps:f64,source:Vec<i32>,sigma:Vec<Vec<f64>>,
    reach:Vec<Vec<Vec<f64>>>,leaf:Vec<Vec<f64>>,regret:Vec<f64>,avg:Vec<f64>,own_repeated:usize,
}
impl Oracle<'_>{
    fn down(&mut self,node:usize,seen:bool){
        let n=&self.s.nodes[node];if n.actions.is_empty(){return}
        let actor=n.actor as usize;let na=n.actions.len();
        if actor==self.p && self.source[node]==0 && seen{self.own_repeated+=1;}
        for a in 0..na{
            let child=self.s.child(node,a);self.reach[child]=self.reach[node].clone();
            for h in 0..NUM_CLASSES{
                let sig=self.sigma[node][a*NUM_CLASSES+h];
                let prob=if self.source[node]==0{(1.0-self.eps)*sig+self.eps/na as f64}else{sig};
                self.reach[child][actor][h]*=prob;
            }
            self.down(child,seen || actor==self.p);
        }
    }
    fn up(&mut self,node:usize,mode:i32)->Vec<f64>{
        let n=&self.s.nodes[node];let na=n.actions.len();if na==0{return self.leaf[node].clone()}
        let qs:Vec<_>=(0..na).map(|a|self.up(self.s.child(node,a),mode)).collect();
        let mut out=vec![0.0;NUM_CLASSES];
        for h in 0..NUM_CLASSES{
            if n.actor as usize!=self.p{out[h]=qs.iter().map(|q|q[h]).sum();continue}
            if self.source[node]!=0{out[h]=(0..na).map(|a|self.sigma[node][a*NUM_CLASSES+h]*qs[a][h]).sum();continue}
            // A virtual action selects each physical action with epsilon/n,
            // and its own physical action with an additional 1-epsilon.
            let virtual_q:Vec<f64>=(0..na).map(|a|(0..na).map(|b|
                (self.eps/na as f64+if a==b{1.0-self.eps}else{0.0})*qs[b][h]).sum()).collect();
            if mode==4{out[h]=virtual_q.iter().copied().fold(f64::NEG_INFINITY,f64::max);continue}
            out[h]=(0..na).map(|a|self.sigma[node][a*NUM_CLASSES+h]*virtual_q[a]).sum();
            for a in 0..na{
                let ix=n.data_off+a*NUM_CLASSES+h;
                self.regret[ix]+=virtual_q[a]-out[h];
                let mu=(0..na).map(|b|self.sigma[node][b*NUM_CLASSES+h]
                    *(self.eps/na as f64+if a==b{1.0-self.eps}else{0.0})).sum::<f64>();
                self.avg[ix]+=self.reach[node][self.p][h]*mu;
            }
        }
        out
    }
}

#[test]
fn behavioral_virtual_action_recursion_matches_all_hands_and_fixed_nodes(){
    let s=fixture(false);let mut checked=0usize;
    for eps in [0.01f32,0.05,0.2]{for p in [0usize,1,3]{
        let mut g=gpu(&s,Some(eps),1024);let (mut old,avg)=arenas(&g);
        for (i,x) in old.iter_mut().enumerate(){*x=if i%7<3{-0.1}else{(i%29) as f32*0.013};}
        // Zero native support for most hands in one action; perturbation must
        // restore it, including below an earlier action by the traverser.
        old[..NUM_CLASSES].fill(-1.0);g.stream.memcpy_htod(&old,&mut g.d_regrets).unwrap();
        let source=g.stream.clone_dtoh(&g.d_src).unwrap();let foff=g.stream.clone_dtoh(&g.d_foff).unwrap();
        let forced=g.stream.clone_dtoh(&g.d_forced).unwrap();
        let blocks=g.stream.clone_dtoh(&g.d_reach_src).unwrap();let slots=g.stream.clone_dtoh(&g.d_val_slot).unwrap();
        let mut sigma=vec![Vec::new();s.nodes.len()];
        for (i,n) in s.nodes.iter().enumerate(){let na=n.actions.len();if na==0{continue}
            sigma[i]=vec![0.0;na*NUM_CLASSES];
            for h in 0..NUM_CLASSES{
                let v:Vec<f64>=(0..na).map(|a|if source[i]==2{forced[foff[i] as usize+a*NUM_CLASSES+h]}
                    else if source[i]==1{avg[n.data_off+a*NUM_CLASSES+h]}else{old[n.data_off+a*NUM_CLASSES+h].max(0.0)} as f64).collect();
                let sum:f64=v.iter().sum();for a in 0..na{sigma[i][a*NUM_CLASSES+h]=if source[i]==2{v[a]}else if sum>1e-12{v[a]/sum}else{1.0/na as f64};}
            }
        }
        let mut o=Oracle{s:&s,p,eps:eps as f64,source,sigma,reach:vec![vec![vec![0.0;NUM_CLASSES];s.n];s.nodes.len()],
            leaf:vec![vec![0.0;NUM_CLASSES];s.nodes.len()],regret:old.iter().map(|x|*x as f64).collect(),
            avg:avg.iter().map(|x|*x as f64).collect(),own_repeated:0};
        for q in 0..s.n{for h in 0..NUM_CLASSES{o.reach[0][q][h]=class_prob(h) as f64;}}
        o.down(0,false);assert!(o.own_repeated>0);
        g.down(0,p as i32).unwrap();let reach=g.stream.clone_dtoh(&g.d_reach).unwrap();
        for i in 0..s.nodes.len(){for q in 0..s.n{
            let at=blocks[i*s.n+q] as usize*NUM_CLASSES;near(&reach[at..at+NUM_CLASSES],&o.reach[i][q],2e-6);
        }}
        let mut values=vec![0.0;g.d_val.len()];
        for (i,n) in s.nodes.iter().enumerate(){if !n.actions.is_empty(){continue}
            let mass:f64=(0..s.n).filter(|q|*q!=p).map(|q|o.reach[i][q].iter().sum::<f64>()).product();
            for h in 0..NUM_CLASSES{
                let v=mass*(((i*31+h*17)%113) as f64/11.0-4.5);
                values[slots[i] as usize*NUM_CLASSES+h]=v as f32;o.leaf[i][h]=v;
            }
        }
        g.stream.memcpy_htod(&values,&mut g.d_val).unwrap();let br=o.up(0,4);
        g.up(p as i32,4).unwrap();near(&g.stream.clone_dtoh(&g.d_val.slice(0..NUM_CLASSES)).unwrap(),&br,2e-5);
        assert_eq!(arenas(&g),(old.clone(),avg.clone()));
        let expected=o.up(0,0);g.stream.memcpy_htod(&values,&mut g.d_val).unwrap();g.up(p as i32,0).unwrap();
        let (r,a)=arenas(&g);near(&r,&o.regret,2e-5);near(&a,&o.avg,2e-6);
        near(&g.stream.clone_dtoh(&g.d_val.slice(0..NUM_CLASSES)).unwrap(),&expected,2e-5);
        let changed=r.iter().zip(&old).filter(|(a,b)|a!=b).count();assert!(changed>NUM_CLASSES);
        for (i,n) in s.nodes.iter().enumerate(){if n.actor as usize!=p || o.source[i]!=0{
            let end=n.data_off+n.actions.len()*NUM_CLASSES;
            assert_eq!(&r[n.data_off..end],&old[n.data_off..end]);assert_eq!(&a[n.data_off..end],&avg[n.data_off..end]);
        }}
        checked+=r.len();
    }}
    println!("behavioral independent recursion: {checked} regret entries, all 169 hands; eps 0.01/0.05/0.2, repeated own actions, constrained BR, fixed nodes");
}

#[test]
fn behavioral_capture_native_zero_and_evaluation_are_exact(){
    for cal in [false,true]{for eps in [0.0f32,0.05]{
        let mut outputs=Vec::new();
        for eager in [false,true]{
            let mut s=fixture(cal);let mut g=gpu(&s,Some(eps),64);
            for _ in 0..5{if eager{g.warmed=false;g.learning_graphs.iter_mut().for_each(|v|*v=None);}g.iterate(&mut s).unwrap();}
            let before=arenas(&g);let native=g.gaps_and_evs().unwrap();let constrained=g.research_behavioral_constrained_gaps().unwrap();
            assert_eq!(before,arenas(&g));assert_eq!(native,g.gaps_and_evs().unwrap());
            assert!(constrained.iter().all(|v|v.is_finite()));
            for p in [0,1,3]{assert!(constrained[p]<=native.0[p]+1e-5);}
            assert_eq!(constrained[2],0.0);
            g.sync_to_cpu(&mut s).unwrap();let mut check=PreflopGpu::new(&s,2000).unwrap();
            assert_eq!(native,check.gaps_and_evs().unwrap());
            outputs.push((before,native,constrained));
        }
        assert_eq!(outputs[0],outputs[1]);
        if eps==0.0{
            let mut s=fixture(cal);let mut base=gpu(&s,None,64);for _ in 0..5{base.iterate(&mut s).unwrap();}
            assert_eq!(outputs[0].0,arenas(&base));assert_eq!(outputs[0].1,base.gaps_and_evs().unwrap());
        }
    }}
}

#[test]
fn behavioral_admission_and_cancellation_are_bounded(){
    let mut s=fixture(false);let mut g=gpu(&s,None,64);
    for e in [f32::NAN,f32::INFINITY,-0.1,0.21]{assert!(g.enable_research_behavioral_perturbation(e).is_err());}
    g.enable_research_behavioral_perturbation(0.05).unwrap();
    assert!(g.enable_research_behavioral_perturbation(0.05).is_err());
    assert!(g.configure_research(Experiment::new("dcfr",64,1000,42).unwrap()).is_err());
    assert!(g.enable_research_opponent_exploration(0.01,250).is_err());
    assert!(g.enable_research_normalized_regret().is_err());
    assert!(g.enable_research_average_opponents().is_err());
    assert!(g.enable_research_pair_control(100).is_err());
    assert!(g.enable_research_control_variate(32,100).is_err());
    assert!(g.enable_research_shared_control_variate(32,100).is_err());
    assert!(g.enable_research_rm_plus().is_err());assert!(g.enable_research_predictive(true,100).is_err());
    let before=arenas(&g);let age=s.iteration;let stop=AtomicBool::new(true);
    assert!(!g.try_iterate(&mut s,Some(&stop)).unwrap());assert_eq!(age,s.iteration);assert_eq!(before,arenas(&g));
    let mut fresh=PreflopGpu::new(&s,2000).unwrap();assert!(fresh.enable_research_behavioral_perturbation(0.05).is_err());
    let mut evaluated=gpu(&s,None,64);evaluated.gaps_and_evs().unwrap();assert!(evaluated.enable_research_behavioral_perturbation(0.05).is_err());
    let mut other=gpu(&s,None,64);other.enable_research_opponent_exploration(0.01,250).unwrap();assert!(other.enable_research_behavioral_perturbation(0.05).is_err());
}
