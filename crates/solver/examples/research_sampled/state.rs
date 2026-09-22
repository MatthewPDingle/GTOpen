//! Research-only on-demand postflop transition reference.
//! No strategy arena, private range reduction, or public history merging.
use solver::tree::{Action, BetSize, TreeConfig, KIND_ACTION, KIND_CHANCE,
    KIND_TERM_FOLD, KIND_TERM_SHOWDOWN};

#[derive(Clone, Copy, Debug)]
pub struct State {
    pub kind:u8, pub player:u8, pub street:u8, pub put:[f64;2],
    street_bet:[f64;2], last_increment:f64, raises:u8,
    last_aggressor:Option<u8>, checked:bool, allin_runout:bool,
}

impl State {
    pub fn root(c:&TreeConfig)->Self {
        Self {kind:KIND_ACTION,player:0,street:0,put:[c.starting_pot/2.;2],
            street_bet:[0.;2],last_increment:0.,raises:0,last_aggressor:None,
            checked:false,allin_runout:false}
    }
    pub fn actions(&self,c:&TreeConfig)->Vec<Action> {
        assert_eq!(self.kind,KIND_ACTION);
        let me=self.player as usize;let opp=1-me;
        let stack=c.effective_stack-(self.put[me]-c.starting_pot/2.);
        let facing=self.street_bet[opp]-self.street_bet[me];assert!(facing>=-1e-9);
        let sizing=if me==0 {&c.oop[self.street as usize]} else {&c.ip[self.street as usize]};
        let mut actions=if facing>1e-9 {vec![Action::Fold,Action::Call(self.street_bet[opp])]}else{vec![Action::Check]};
        let raising=facing>1e-9;
        if (raising&&(stack<=facing+1e-9||self.raises>=c.max_raises))||(!raising&&stack<=1e-9){return actions;}
        let donk=me==0&&self.street>0&&self.last_aggressor==Some(1);
        let sizes=if raising {&sizing.raise} else if donk {&sizing.donk} else {&sizing.bet};
        let max_to=if raising {self.street_bet[me]+stack}else{stack};
        let mut values=Vec::new();
        for size in sizes {
            let value=match *size {
                BetSize::PotPct(p)=>if raising {self.street_bet[opp]+p/100.*(self.put[0]+self.put[1]+facing)}else{p/100.*(self.put[0]+self.put[1])},
                BetSize::PrevMult(m)=>{assert!(raising,"validated bet menus cannot contain raise multiples");self.street_bet[opp]*m},
                BetSize::AllIn=>max_to,
            };values.push(value);
        }
        if c.add_allin&&(raising||!sizes.is_empty()||!donk){values.push(max_to);}
        let mut amounts=Vec::new();
        for mut to in values {
            if raising{to=to.max(self.street_bet[opp]+self.last_increment.max(1e-9));}
            else if to<=1e-9{continue;}
            if to>=max_to-1e-9||to>=c.allin_threshold*max_to-1e-9{to=max_to;}
            if !raising||to>self.street_bet[opp]+1e-9{amounts.push(to);}
        }
        amounts.sort_by(f64::total_cmp);amounts.dedup_by(|a,b|(*a-*b).abs()<1e-6);
        actions.extend(amounts.into_iter().map(|to|if raising {Action::Raise(to)}else{Action::Bet(to)}));actions
    }
    fn end(mut self,aggressor:Option<u8>,allin:bool)->Self {
        if self.street==2 {self.kind=KIND_TERM_SHOWDOWN;self.player=0;return self;}
        self.kind=KIND_CHANCE;self.street+=1;self.player=0;
        self.street_bet=[0.;2];self.last_increment=0.;self.raises=0;
        self.last_aggressor=aggressor;self.checked=false;self.allin_runout=allin;self
    }
    pub fn act(self,c:&TreeConfig,a:Action)->Self {
        assert_eq!(self.kind,KIND_ACTION);let mut out=self;let me=self.player as usize;let opp=1-me;
        match a {
            Action::Fold=>{out.kind=KIND_TERM_FOLD;out}
            Action::Check=>if self.checked {self.end(if c.carry_aggressor_through_checks.unwrap_or(false){self.last_aggressor}else{None},false)}
                else{out.player^=1;out.checked=true;out},
            Action::Call(to)=>{
                out.put[me]+=to-self.street_bet[me];
                let total=c.effective_stack+c.starting_pot/2.;
                let allin=total-out.put[me]<=1e-9||total-out.put[opp]<=1e-9;
                out.end(Some(self.player^1),allin)
            }
            Action::Bet(to)|Action::Raise(to)=>{
                out.put[me]+=to-self.street_bet[me];out.street_bet[me]=to;
                out.last_increment=(to-self.street_bet[opp].max(self.street_bet[me])).max(self.last_increment);
                out.raises+=matches!(a,Action::Raise(_)) as u8;out.player^=1;out
            }
        }
    }
    pub fn deal(mut self)->Self {
        assert_eq!(self.kind,KIND_CHANCE);
        if self.allin_runout {if self.street==2{self.kind=KIND_TERM_SHOWDOWN;}else{self.street+=1;}}
        else {self.kind=KIND_ACTION;}
        self
    }
    pub fn payouts(&self,c:&TreeConfig)->[f64;3] {
        assert!(self.kind==KIND_TERM_FOLD||self.kind==KIND_TERM_SHOWDOWN);
        let amount=if self.kind==KIND_TERM_FOLD{self.put[self.player as usize]}else{self.put[0]};
        let gross=c.rake_pct*2.*amount;let rake=if c.rake_cap>0.{gross.min(c.rake_cap)}else{gross};
        [amount-rake,-amount,if self.kind==KIND_TERM_SHOWDOWN{-rake/2.}else{0.}]
    }
}

/// Identity uses full history, not just pot/stack or a hand's rank class.
#[derive(Clone,Debug,PartialEq,Eq,PartialOrd,Ord)]
pub struct InfoKey {
    pub branch:usize, pub player:u8, pub own_hand:[u8;2],
    pub visible_board:Vec<u8>, pub public_actions:Vec<u8>,
}

impl InfoKey {
    pub fn new(branch:usize,player:u8,mut own_hand:[u8;2],board:&[u8],actions:&[u8])->Self {
        assert!(player<2&&(3..=5).contains(&board.len()));own_hand.sort();
        let mut mask=0u64;for c in own_hand.into_iter().chain(board.iter().copied()){
            assert!(c<52&&mask&(1u64<<c)==0);mask|=1u64<<c;}
        Self{branch,player,own_hand,visible_board:board.to_vec(),public_actions:actions.to_vec()}
    }
}
