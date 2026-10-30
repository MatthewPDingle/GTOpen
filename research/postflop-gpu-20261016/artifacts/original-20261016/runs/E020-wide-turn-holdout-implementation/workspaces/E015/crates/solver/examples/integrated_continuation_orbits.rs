//! Weighted suit-orbit integration experiment. SUBTREE MANIFEST OUTPUT ITERATIONS
//! Boards are a finite, announced chance panel, not a full-deck preflop model.
//! Never uses the live server or modifies saved games.
use serde_json::{json,Value};
use solver::{Solver,Spot,SpotConfig,Algorithm,TreeConfig,StreetSizing,parse_sizes};
use solver::{game::{Dealt,fold_cfv},gpu::GpuSolver,preflop::equity::{class_index,class_label}};
use std::sync::Arc;

const N:usize=1326;
// Separate scalar probability/rake traversal: no CFV or best-response code.
fn cashflow(s:&Solver,i:usize,reaches:&[Vec<f32>;2],dealt:u64)->(f64,f64) {
    let sp=&s.spot;let n=&sp.tree.nodes[i];
    if n.kind==solver::tree::KIND_ACTION {
        let sigma=s.average_strategy(i as u32,n);let actor=n.player as usize;let nh=reaches[actor].len();
        let mut result=(0.,0.);
        for a in 0..n.num_children as usize {
            let mut r=reaches.clone();for h in 0..nh {r[actor][h]*=sigma[a*nh+h];}
            let (m,k)=cashflow(s,sp.tree.children[n.children_start as usize+a] as usize,&r,dealt);result.0+=m;result.1+=k;
        }return result;
    }
    if n.kind==solver::tree::KIND_CHANCE {
        let mut result=(0.,0.);let divisor=(46-n.street) as f64;
        for card in 0..52 {
            let child=sp.tree.children[n.children_start as usize+card];
            if child==solver::tree::SENTINEL || dealt&(1u64<<card)!=0 {continue;}
            let mut r=reaches.clone();for p in 0..2 {for (h,info) in sp.hands[p].iter().enumerate(){if info.mask&(1u64<<card)!=0{r[p][h]=0.;}}}
            let (m,k)=cashflow(s,child as usize,&r,dealt|(1u64<<card));result.0+=m/divisor;result.1+=k/divisor;
        }return result;
    }
    let mut total=0.;let mut bycard=[0.;52];
    for (h,info) in sp.hands[1].iter().enumerate(){let w=reaches[1][h] as f64;total+=w;bycard[info.c1 as usize]+=w;bycard[info.c2 as usize]+=w;}
    let mut mass=0.;
    for (h,info) in sp.hands[0].iter().enumerate(){let same=sp.same_combo[0][h];let correction=if same==solver::tree::SENTINEL{0.}else{reaches[1][same as usize] as f64};
        mass+=reaches[0][h] as f64*(total-bycard[info.c1 as usize]-bycard[info.c2 as usize]+correction);
    }
    let rake=-(n.t_win+n.t_lose);assert!(rake>= -1e-8 && rake<=6.000001);
    if n.kind==solver::tree::KIND_TERM_SHOWDOWN {assert!((rake+2.*n.t_tie).abs()<1e-8);}
    (mass,mass*rake)
}
struct Continuation { host:Solver, gpu:GpuSolver, map:[Vec<usize>;2] }
struct Game {
    nodes:Vec<Value>, weights:[Vec<f64>;2], classes:Vec<usize>,
    continuations:Vec<Vec<Continuation>>, boards:Vec<String>, board_weights:Vec<f64>, orbit:bool,
    regrets:Vec<Vec<Vec<f64>>>, sums:Vec<Vec<Vec<f64>>>, sigma:Vec<Vec<Vec<f64>>>,
    z:f64,
}
impl Game {
    fn new(data:&Value,manifest:&Value)->Self {
        let boards:Vec<String>=manifest["boards"].as_array().unwrap().iter().map(|x|x["board"].as_str().unwrap().to_owned()).collect();
        let mut board_weights:Vec<f64>=manifest["boards"].as_array().unwrap().iter().map(|x|x["weight"].as_f64().unwrap()).collect();
        assert!(board_weights.iter().all(|w|w.is_finite() && *w>0.));let total:f64=board_weights.iter().sum();for w in &mut board_weights{*w/=total;}
        let orbit=manifest["suit_orbits"].as_bool().unwrap();
        let mut lookup=[[0usize;52];52];let mut classes=vec![];let mut multiplicity=[0.;169];
        for a in 0..52 {for b in a+1..52 {
            lookup[a][b]=classes.len();lookup[b][a]=classes.len();
            let c=class_index(a as u8/4,b as u8/4,a%4==b%4);classes.push(c);multiplicity[c]+=1.;
        }}
        let mut weights:[Vec<f64>;2]=std::array::from_fn(|p| {
            let mut w:Vec<f64>=classes.iter().map(|&c|data["incoming_class_mass"][p][c].as_f64().unwrap()/multiplicity[c]).collect();
            let max=w.iter().copied().fold(0.,f64::max);for v in &mut w {*v/=max;}w
        });
        // Prune only negligible ENTRY support, never arriving branch ranges.
        for p in 0..2 {let before:f64=weights[p].iter().sum();let mut removed=0.;
            for w in &mut weights[p] {if *w<0.00001 {removed+=*w;*w=0.;}}
            assert!(removed/before<0.00001,"entry truncation too large");
            println!("seat{p} entry mass removed={}",removed/before);
        }
        let full:[String;2]=std::array::from_fn(|p|(0..169).filter(|&c|classes.iter().position(|&h|h==c).is_some_and(|h|weights[p][h]>0.))
            .map(class_label).collect::<Vec<_>>().join(","));
        let menu=manifest["bet_menu"].as_str().unwrap();
        let sizing=StreetSizing {bet:parse_sizes(menu).unwrap(),raise:parse_sizes("100").unwrap(),donk:parse_sizes(menu).unwrap()};
        let mut estimated_gpu_bytes=0u64;
        let mut continuations=vec![];
        for (pot,stack) in [(39.5,182.),(93.5,155.)] {
            let mut panel=vec![];
            for board in &boards {
                let spot=Arc::new(Spot::new_with_limit(SpotConfig {
                    board:board.clone(),range_oop:full[0].clone(),range_ip:full[1].clone(),
                    tree:TreeConfig {starting_pot:pot,effective_stack:stack,rake_pct:0.04,rake_cap:6.,
                        oop:[sizing.clone(),sizing.clone(),sizing.clone()],ip:[sizing.clone(),sizing.clone(),sizing.clone()],
                        max_raises:1,..Default::default()},
                },Some(2_000_000)).unwrap());
                let map=std::array::from_fn(|p|spot.hands[p].iter().map(|h|lookup[h.c1 as usize][h.c2 as usize]).collect());
                let mut host=Solver::new(spot);host.algo=Algorithm::CfrPlus;host.use_isomorphism=false;
                let plan=solver::gpu::plan::GpuPlan::build(&host.spot,false);
                let base=plan.staging_bytes()+(host.spot.tree.data_size[0]+host.spot.tree.data_size[1])*8;
                estimated_gpu_bytes+=base+128*1024*1024;
                assert!(estimated_gpu_bytes<21_000_000_000,"panel exceeds research GPU budget");drop(plan);
                let gpu=GpuSolver::new_with_budget(&host,base+512*1024*1024).unwrap();
                panel.push(Continuation{host,gpu,map});
            }
            continuations.push(panel);
        }
        let nodes=data["nodes"].as_array().unwrap().clone();
        let regrets:Vec<_>=nodes.iter().map(|n|if n["kind"]==0 {vec![vec![0.;N];n["children"].as_array().unwrap().len()]}else{vec![]}).collect();
        let sigma=regrets.iter().map(|r|r.iter().map(|v|vec![1./r.len() as f64;v.len()]).collect()).collect();
        let mut g=Self{nodes,weights,classes,continuations,boards,board_weights,orbit,sums:regrets.clone(),regrets,sigma,z:0.};
        let mass=g.mass(0,&g.weights[1]);g.z=mass.iter().zip(&g.weights[0]).map(|(m,w)|m*w).sum();assert!(g.z>0.);g
    }
    fn project(&self,values:&mut [f64]) {
        if !self.orbit{return;}
        let mut sums=[0.;169];let mut counts=[0.;169];
        for (i,&c) in self.classes.iter().enumerate(){sums[c]+=values[i];counts[c]+=1.;}
        for (i,&c) in self.classes.iter().enumerate(){values[i]=sums[c]/counts[c];}
    }
    fn mass(&self,p:usize,opp:&[f64])->Vec<f64> {
        let mut out=vec![0.;N];
        for (b,c) in self.continuations[0].iter().enumerate() {
            let sp=&c.host.spot;let ro:Vec<f32>=c.map[1-p].iter().map(|&i|opp[i] as f32).collect();let mut m=vec![0.;c.map[p].len()];
            fold_cfv(&sp.hands[p],&sp.hands[1-p],&ro,&sp.same_combo[p],1.,&mut m);
            for (j,&i) in c.map[p].iter().enumerate(){out[i]+=m[j] as f64*self.board_weights[b];}
        }self.project(&mut out);out
    }
    fn leaf(&mut self,p:usize,i:usize,own:&[f64],opp:&[f64],t:u32,br:bool)->Vec<f64> {
        let n=&self.nodes[i];let kind=n["kind"].as_u64().unwrap();
        if kind==1 {
            let u=if n["winner"].as_u64().unwrap()==p as u64 {n["pot"].as_f64().unwrap()}else{0.}-n["invested"][p].as_f64().unwrap();
            return self.mass(p,opp).iter().map(|x|x*u).collect();
        }
        let branch=if i==5 {1}else{0};let post=i==2||i==5;
        let mut out=vec![0.;N];
        for (b,c) in self.continuations[branch].iter_mut().enumerate() {
            let ro:Vec<f32>=c.map[1-p].iter().map(|&h|opp[h] as f32).collect();
            let rp:Vec<f32>=c.map[p].iter().map(|&h|own[h] as f32).collect();
            let sp=&c.host.spot;let mut mass=vec![0.;c.map[p].len()];
            fold_cfv(&sp.hands[p],&sp.hands[1-p],&ro,&sp.same_combo[p],1.,&mut mass);
            let v=if post {
                if t>0 {c.gpu.research_continuation_sweep(p,t,&rp,&ro).unwrap()}
                else if br {c.host.traverse_br(0,p,&ro,Dealt::default())}
                else {c.host.traverse_avg(0,p,&ro,Dealt::default())}
            } else {
                let eq=c.host.equity(p,&ro,Dealt::default());
                let pot=n["pot"].as_f64().unwrap();let net=pot-(pot*0.04).min(6.);
                eq.iter().zip(&mass).map(|(&e,&m)|if m>0. {
                    (net*e as f64-n["invested"][p].as_f64().unwrap()) as f32*m
                }else{0.}).collect()
            };
            for (j,&h) in c.map[p].iter().enumerate() {
                // Postflop values subtract half the initial pot. Restore the
                // original investment: half-pot - investment = dead money / 2.
                out[h]+=(v[j] as f64+if post {1.75*mass[j] as f64}else{0.})*self.board_weights[b];
            }
        }self.project(&mut out);out
    }
    fn walk(&mut self,p:usize,i:usize,own:&[f64],opp:&[f64],t:u32,br:bool)->Vec<f64> {
        if self.nodes[i]["kind"]!=0 {return self.leaf(p,i,own,opp,t,br);}
        let actor=self.nodes[i]["actor"].as_u64().unwrap() as usize;
        let children:Vec<usize>=self.nodes[i]["children"].as_array().unwrap().iter().map(|c|c.as_u64().unwrap() as usize).collect();
        let old=self.sigma[i].clone();let mut vals=vec![];
        for (a,&child) in children.iter().enumerate() {
            let reach:Vec<_>=if actor==p {own}else{opp}.iter().zip(&old[a]).map(|(r,s)|r*s).collect();
            vals.push(if actor==p {self.walk(p,child,&reach,opp,t,br)}else{self.walk(p,child,own,&reach,t,br)});
        }
        let mut out=vec![0.;N];
        for h in 0..N {
            out[h]=if actor!=p {vals.iter().map(|v|v[h]).sum()}
                else if br {vals.iter().map(|v|v[h]).fold(f64::NEG_INFINITY,f64::max)}
                else {vals.iter().zip(&old).map(|(v,s)|v[h]*s[h]).sum()};
            if actor==p && t>0 {
                let discount=solver::cfr::Discounts::for_iteration(Algorithm::CfrPlus,t).strat as f64;
                let mut den=0.;
                for a in 0..old.len() {
                    self.sums[i][a][h]=self.sums[i][a][h]*discount+own[h]*old[a][h];
                    self.regrets[i][a][h]=(self.regrets[i][a][h]+vals[a][h]-out[h]).max(0.);den+=self.regrets[i][a][h];
                }
                for a in 0..old.len(){self.sigma[i][a][h]=if den>0. {self.regrets[i][a][h]/den}else{1./old.len() as f64};}
            }
        }out
    }
    fn evaluate(&mut self)->Value {
        for panel in &mut self.continuations {for c in panel {c.gpu.sync_to_cpu(&mut c.host).unwrap();}}
        let current=self.sigma.clone();
        for i in 0..self.sigma.len(){for h in 0..N {
            let den:f64=self.sums[i].iter().map(|s|s[h]).sum();let na=self.sigma[i].len();
            for a in 0..na {self.sigma[i][a][h]=if den>0.{self.sums[i][a][h]/den}else{1./na as f64};}
        }}
        let mut ev=[0.;2];let mut best=[0.;2];
        for p in 0..2 {for br in [false,true] {
            let w=self.weights.clone();let v=self.walk(p,0,&w[p],&w[1-p],0,br);
            let value=v.iter().zip(&w[p]).map(|(v,w)|v*w).sum::<f64>()/self.z;
            if br {best[p]=value}else{ev[p]=value};
        }}
        let mass=self.mass(0,&self.weights[1]);let mut freq=vec![0.;4];let mut hands=vec![];
        for cls in 0..169 {
            let mut d=0.;let mut actions=vec![0.;4];
            for h in 0..N {if self.classes[h]==cls {
                let w=self.weights[0][h]*mass[h]/self.z;d+=w;
                for a in 0..4 {actions[a]+=w*self.sigma[0][a][h];freq[a]+=w*self.sigma[0][a][h];}
            }}
            if d>0. {for a in &mut actions {*a/=d;}}
            hands.push(json!({"hand":class_label(cls),"root_mass":d,"strategy":actions}));
        }
        let (probability,rake)=self.flow(0,&self.weights.clone());
        let probability=probability/self.z;let rake=rake/self.z;
        let conservation=(ev.iter().sum::<f64>()+rake-3.5).abs();
        assert!((probability-1.).abs()<0.00001,"terminal probability {probability}");
        assert!(conservation<0.0001,"conservation error {conservation}");
        let policies=self.sigma.clone();self.sigma=current;
        let gaps=[best[0]-ev[0],best[1]-ev[1]];assert!(gaps.iter().all(|g|*g> -0.0001));
        // Terminal utilities sum to dead money minus rake, between -2.5 and 3.5.
        assert!(ev.iter().sum::<f64>()>= -2.5001 && ev.iter().sum::<f64>()<=3.5001);
        json!({"ev":ev,"best_response":best,"gaps":gaps,"gap_total":gaps.iter().sum::<f64>(),
            "root_frequencies":freq,"hands":hands,"preflop_policy":policies,
            "terminal_probability":probability,"expected_rake":rake,"conservation_error":conservation})
    }
    fn flow(&self,i:usize,reaches:&[Vec<f64>;2])->(f64,f64) {
        let n=&self.nodes[i];
        if n["kind"]==0 {
            let actor=n["actor"].as_u64().unwrap() as usize;let mut result=(0.,0.);
            for (a,c) in n["children"].as_array().unwrap().iter().enumerate(){let mut r=reaches.clone();for h in 0..N{r[actor][h]*=self.sigma[i][a][h];}
                let (m,k)=self.flow(c.as_u64().unwrap() as usize,&r);result.0+=m;result.1+=k;
            }return result;
        }
        if i==2||i==5 {
            let mut result=(0.,0.);
            for (b,c) in self.continuations[if i==5{1}else{0}].iter().enumerate() {
                let r=std::array::from_fn(|p|c.map[p].iter().map(|&h|reaches[p][h] as f32).collect());
                let (m,k)=cashflow(&c.host,0,&r,c.host.spot.board_mask);result.0+=m*self.board_weights[b];result.1+=k*self.board_weights[b];
            }return result;
        }
        let m=self.mass(0,&reaches[1]).iter().zip(&reaches[0]).map(|(m,w)|m*w).sum::<f64>();
        (m,if n["kind"]==1{0.}else{m*6.})
    }
}
fn main(){
    let a:Vec<_>=std::env::args().skip(1).collect();assert_eq!(a.len(),4,"SUBTREE MANIFEST OUTPUT ITERATIONS");
    assert!(!std::path::Path::new(&a[2]).exists(),"preserve evidence");
    let read=|p:&str|->Value{serde_json::from_slice(&std::fs::read(p).unwrap()).unwrap()};
    let data=read(&a[0]);let manifest=read(&a[1]);
    assert_eq!(data["config"]["rake_pct"],4.);assert_eq!(data["config"]["rake_cap"],6.);
    let target:u32=a[3].parse().unwrap();let start=std::time::Instant::now();
    let mut game=Game::new(&data,&manifest);let mut records=vec![];
    for t in 1..=target {
        for p in 0..2 {let w=game.weights.clone();game.walk(p,0,&w[p],&w[1-p],t,false);}
        if [1,20,100,500,2000,5000,10000].contains(&t)||t==target {
            let evaluation=game.evaluate();println!("{t} gap={} elapsed={:.1}",evaluation["gap_total"],start.elapsed().as_secs_f64());
            records.push(json!({"iteration":t,"elapsed_seconds":start.elapsed().as_secs_f64(),"evaluation":evaluation}));
            let out=json!({"manifest":manifest,"boards":game.boards,"board_weights":game.board_weights,"suit_orbits":game.orbit,
                "root_normalizer":game.z,"entry_cutoff":0.00001,"records":records,
                "note":"Weighted finite board panel, all suit relabelings. Earlier folded cards omitted. Not a full-deck or Wizard accuracy certificate."});
            let tmp=format!("{}.tmp",a[2]);std::fs::write(&tmp,serde_json::to_vec_pretty(&out).unwrap()).unwrap();
            std::fs::rename(&tmp,&a[2]).unwrap();
        }
    }
}
