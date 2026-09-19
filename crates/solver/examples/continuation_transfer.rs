//! Frozen-preflop transfer evaluation, fully enumerated postflop. Research only. SUBTREE MANIFEST OUTPUT ITERATIONS
//! Boards are a finite, announced chance panel, not a full-deck preflop model.
//! Never uses the live server or modifies saved games.
use serde_json::{json,Value};
use solver::{Solver,Spot,SpotConfig,Algorithm,TreeConfig,StreetSizing,parse_sizes};
use solver::{game::{Dealt,fold_cfv},gpu::{PagedContinuationGpu as GpuSolver,ContinuationWorkspace},preflop::equity::{class_index,class_label}};
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
    sigma:Vec<Vec<Vec<f64>>>,
    z:f64, workspace:ContinuationWorkspace, restrict_preflop:bool,
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
        let mut workspace=ContinuationWorkspace::default();
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
                let gpu=GpuSolver::new(&host,&mut workspace).unwrap();
                println!("paged {board} pot={pot}: shared workspace={} bytes",workspace.bytes());
                panel.push(Continuation{host,gpu,map});
            }
            continuations.push(panel);
        }
        let nodes=data["nodes"].as_array().unwrap().clone();
        let regrets:Vec<_>=nodes.iter().map(|n|if n["kind"]==0 {vec![vec![0.;N];n["children"].as_array().unwrap().len()]}else{vec![]}).collect();
        let sigma=regrets.iter().map(|r|r.iter().map(|v|vec![1./r.len() as f64;v.len()]).collect()).collect();
        let mut g=Self{nodes,weights,classes,continuations,boards,board_weights,orbit,sigma,z:0.,workspace,restrict_preflop:false};
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
                if t>0 {c.gpu.sweep(&mut c.host,&mut self.workspace,p,t,&rp,&ro).unwrap()}
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
                else if br && !self.restrict_preflop {vals.iter().map(|v|v[h]).fold(f64::NEG_INFINITY,f64::max)}
                else {vals.iter().zip(&old).map(|(v,s)|v[h]*s[h]).sum()};
        }out
    }
    fn evaluate(&mut self)->Value {
        // Each completed paged sweep has already synchronized its host state.
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
        let policies=self.sigma.clone();
        self.restrict_preflop=true;
        let post_best:[f64;2]=std::array::from_fn(|p| {
            let w=self.weights.clone();let values=self.walk(p,0,&w[p],&w[1-p],0,true);
            values.iter().zip(&w[p]).map(|(v,w)|v*w).sum::<f64>()/self.z
        });
        self.restrict_preflop=false;
        let post_gaps:[f64;2]=std::array::from_fn(|p|post_best[p]-ev[p]);
        let independent=self.postflop_deviation_sum();
        for p in 0..2 {
            assert!(post_best[p]>=ev[p]-0.00001 && post_best[p]<=best[p]+0.00001,"restricted BR ordering");
            assert!((post_gaps[p]-independent[p]).abs()<0.00001,"independent continuation sum {} vs {}",post_gaps[p],independent[p]);
        }
        let gaps=[best[0]-ev[0],best[1]-ev[1]];assert!(gaps.iter().all(|g|*g> -0.0001));
        // Terminal utilities sum to dead money minus rake, between -2.5 and 3.5.
        assert!(ev.iter().sum::<f64>()>= -2.5001 && ev.iter().sum::<f64>()<=3.5001);
        json!({"postflop_gaps":post_gaps,"postflop_gap_total":post_gaps.iter().sum::<f64>(),"independent_postflop_gaps":independent,"ev":ev,"best_response":best,"gaps":gaps,"gap_total":gaps.iter().sum::<f64>(),
            "root_frequencies":freq,"hands":hands,"preflop_policy":policies,
            "terminal_probability":probability,"expected_rake":rake,"conservation_error":conservation})
    }
    fn install_policy(&mut self,source:&Value) {
        let policy:Vec<Vec<Vec<f64>>>=serde_json::from_value(source["records"].as_array().unwrap().last().unwrap()["evaluation"]["preflop_policy"].clone()).unwrap();
        assert_eq!(policy.len(),self.sigma.len());
        for (rows,expected) in policy.iter().zip(&self.sigma) {
            assert_eq!(rows.len(),expected.len());
            for row in rows {assert_eq!(row.len(),N);assert!(row.iter().all(|v|v.is_finite() && *v>=0. && *v<=1.));}
            if !rows.is_empty() {for h in 0..N {assert!((rows.iter().map(|r|r[h]).sum::<f64>()-1.).abs()<1e-10);}}
            // The orbit game cannot import suit-asymmetric preflop policies.
            for row in rows {let mut first=[None;169];for (h,&cl) in self.classes.iter().enumerate() {
                if let Some(v)=first[cl] {assert_eq!(row[h],v);}else{first[cl]=Some(row[h]);}
            }}
        }
        self.sigma=policy;
    }
    fn postflop_deviation_sum(&self)->[f64;2] {
        // Independent forward path propagation, then scalar sums of reached
        // postflop deviations. No preflop value recursion or maximization.
        let mut result=[0.;2];let mut todo=vec![(0usize,self.weights.clone())];
        while let Some((i,reaches))=todo.pop() {
            let n=&self.nodes[i];
            if n["kind"]==0 {
                let actor=n["actor"].as_u64().unwrap() as usize;
                for (a,child) in n["children"].as_array().unwrap().iter().enumerate() {
                    let mut r=reaches.clone();for h in 0..N {r[actor][h]*=self.sigma[i][a][h];}
                    todo.push((child.as_u64().unwrap() as usize,r));
                }
            } else if i==2 || i==5 {
                for (b,c) in self.continuations[if i==5 {1}else{0}].iter().enumerate() {
                    for p in 0..2 {
                        let ro:Vec<f32>=c.map[1-p].iter().map(|&h|reaches[1-p][h] as f32).collect();
                        let average=c.host.traverse_avg(0,p,&ro,Dealt::default());
                        let best=c.host.traverse_br(0,p,&ro,Dealt::default());
                        for (j,&h) in c.map[p].iter().enumerate() {
                            result[p]+=reaches[p][h]*(best[j] as f64-average[j] as f64)*self.board_weights[b]/self.z;
                        }
                    }
                }
            }
        }result
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
    let a:Vec<_>=std::env::args().skip(1).collect();assert_eq!(a.len(),5,"SUBTREE MANIFEST OUTPUT ITERATIONS SOURCE_RESULT");
    assert!(!std::path::Path::new(&a[2]).exists(),"preserve evidence");
    let read=|p:&str|->Value{serde_json::from_slice(&std::fs::read(p).unwrap()).unwrap()};
    let data=read(&a[0]);let manifest=read(&a[1]);let source=read(&a[4]);
    assert_eq!(manifest["suit_orbits"],true);assert_eq!(source["suit_orbits"],true);
    assert_eq!(source["manifest"]["bet_menu"],manifest["bet_menu"],"transfer must preserve the action menu");
    assert_eq!(source["entry_cutoff"],0.00001,"transfer must preserve entry support");
    assert_eq!(data["config"]["rake_pct"],4.);assert_eq!(data["config"]["rake_cap"],6.);
    let target:u32=a[3].parse().unwrap();let start=std::time::Instant::now();
    let mut game=Game::new(&data,&manifest);game.install_policy(&source);
    let frozen:Vec<u64>=game.sigma.iter().flatten().flatten().map(|v|v.to_bits()).collect();let mut records=vec![];
    for t in 1..=target {
        for p in 0..2 {let w=game.weights.clone();game.walk(p,0,&w[p],&w[1-p],t,false);}
        if [1,20,100,500,2000,5000,10000].contains(&t)||t==target {
            let evaluation=game.evaluate();
            assert_eq!(game.sigma.iter().flatten().flatten().map(|v|v.to_bits()).collect::<Vec<_>>(),frozen,"preflop policy changed");
            println!("{t} postflop_gap={} full_deviation={} elapsed={:.1}",evaluation["postflop_gap_total"],evaluation["gap_total"],start.elapsed().as_secs_f64());
            records.push(json!({"iteration":t,"elapsed_seconds":start.elapsed().as_secs_f64(),"evaluation":evaluation}));
            let out=json!({"manifest":manifest,"boards":game.boards,"board_weights":game.board_weights,"suit_orbits":game.orbit,
                "frozen_preflop_source":a[4],"preflop_unchanged":true,"workspace_bytes":game.workspace.bytes(),"transferred_bytes":game.continuations.iter().flatten().map(|c|c.gpu.transferred_bytes).sum::<u64>(),
                "root_normalizer":game.z,"entry_cutoff":0.00001,"records":records,
                "note":"Weighted finite board panel, all suit relabelings. Earlier folded cards omitted. Not a full-deck or Wizard accuracy certificate."});
            let tmp=format!("{}.tmp",a[2]);std::fs::write(&tmp,serde_json::to_vec_pretty(&out).unwrap()).unwrap();
            std::fs::rename(&tmp,&a[2]).unwrap();
        }
    }
}
