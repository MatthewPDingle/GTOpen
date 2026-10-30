//! Lossless visible-observation features, modulo a global suit relabeling.
//! Fixed registered subtree context; this is not a strategic hand abstraction.
use super::poker_reference_v1::{Game,Key};
use super::state::State;

pub const WIDTH:usize=269;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Observation {
    pub cards:[u8;7],pub actor:usize,pub phase:usize,pub public_id:usize,
    pub history:Vec<u8>,
}

fn transform(cards:[u8;7],suits:[u8;4])->[u8;7]{
    let mut out=cards.map(|c|if c==63{63}else{c/4*4+suits[(c%4)as usize]});
    out[..2].sort_unstable();out[2..5].sort_unstable();out
}
fn packed(cards:[u8;7],actor:usize)->u64{
    let mut out=(actor as u64)<<42;for(i,c)in cards.into_iter().enumerate(){out|=(c as u64)<<(6*i);}out
}
pub fn canonical_cards(cards:[u8;7],actor:usize)->[u8;7]{
    let mut best=cards;let mut minimum=u64::MAX;
    for a in 0..4{for b in 0..4{if b==a{continue;}for c in 0..4{if c==a||c==b{continue;}for d in 0..4{
        if d==a||d==b||d==c{continue;}let candidate=transform(cards,[a,b,c,d]);let id=packed(candidate,actor);
        if id<minimum{minimum=id;best=candidate;}
    }}}}best
}
impl Observation {
    pub fn decode(key:Key)->Self{
        let(hi,lo)=key;assert_eq!(lo>>43,0,"reserved card-key bits");
        let actor=((lo>>42)&1)as usize;let mut cards=[0u8;7];let mut seen=0u64;
        for i in 0..7{let c=((lo>>(6*i))&63)as u8;assert!(c<52||c==63,"invalid card code");
            if c<52{assert_eq!(seen&(1u64<<c),0,"duplicate visible card");seen|=1u64<<c;}cards[i]=c;}
        assert!(cards[0]<52&&cards[1]<52);
        let mut history=Vec::new();let public_id;let phase;
        if hi>>63==0{
            assert!(hi>0&&hi<=16);public_id=hi as usize-1;phase=0;
            assert!(cards[2..].iter().all(|&c|c==63),"preflop future-card leakage");
        }else{
            public_id=(hi&15)as usize;assert!(cards[2..5].iter().all(|&c|c<52));
            assert!(cards[6]==63||cards[5]<52,"river without turn");
            phase=if cards[5]==63{1}else if cards[6]==63{2}else{3};
            let mut encoded=(hi&!(1u64<<63))>>4;
            while encoded>1{let token=(encoded&7)as u8;assert!((1..=5).contains(&token));history.push(token);encoded>>=3;}
            assert_eq!(encoded,1,"missing history root marker");assert!(history.len()<=19);history.reverse();
            assert_eq!(history.iter().filter(|&&t|t==5).count(),phase-1,"board/history disagreement");
        }
        cards=canonical_cards(cards,actor);Self{cards,actor,phase,public_id,history}
    }
    pub fn key(&self)->Key{
        let hi=if self.phase==0{self.public_id as u64+1}else{
            let mut h=1u64;for &a in &self.history{h=(h<<3)|a as u64;}assert!(h<(1u64<<59));
            (1u64<<63)|(h<<4)|self.public_id as u64
        };(hi,packed(self.cards,self.actor))
    }
    pub fn legal_actions(&self,game:&Game)->usize{
        assert!(game.kinds.len()<=16&&self.public_id<game.kinds.len());
        if self.phase==0{
            assert_eq!(game.kinds[self.public_id],0,"not a preflop decision");
            assert_eq!(game.actors[self.public_id]as usize,self.actor);game.arities[self.public_id]as usize
        }else{
            assert_eq!(game.kinds[self.public_id],2,"not a postflop branch");
            let cfg=&game.configs[self.public_id];let mut state=State::root(cfg);
            for &token in &self.history{
                if token==5{assert_eq!(state.kind,1);state=state.deal();}
                else{assert_eq!(state.kind,0);let actions=state.actions(cfg);assert!((token as usize)<=actions.len());
                    state=state.act(cfg,actions[token as usize-1]);}
            }
            assert_eq!(state.kind,0,"terminal histories have no policy input");
            assert_eq!(state.player as usize,self.actor);assert_eq!(state.street as usize+1,self.phase);
            state.actions(cfg).len()
        }
    }
    pub fn features(&self)->[f32;WIDTH]{
        let mut x=[0.;WIDTH];let mut at=0;
        for &c in &self.cards{
            let rank=if c==63{13}else{c as usize/4};let suit=if c==63{4}else{c as usize%4};
            x[at+rank]=1.;at+=14;x[at+suit]=1.;at+=5;
        }
        x[at+self.actor]=1.;at+=2;x[at+self.phase]=1.;at+=4;x[at+self.public_id]=1.;at+=16;
        for slot in 0..19{x[at+self.history.get(slot).copied().unwrap_or(0)as usize]=1.;at+=6;}
        assert_eq!(at,WIDTH);x
    }
    pub fn from_features(x:&[f32;WIDTH])->Self{
        fn one(x:&[f32])->usize{assert!(x.iter().all(|&v|v==0.||v==1.));assert_eq!(x.iter().filter(|&&v|v==1.).count(),1);x.iter().position(|&v|v==1.).unwrap()}
        let mut at=0;let mut cards=[63u8;7];
        for c in &mut cards{let rank=one(&x[at..at+14]);at+=14;let suit=one(&x[at..at+5]);at+=5;
            assert_eq!(rank==13,suit==4);*c=if rank==13{63}else{(rank*4+suit)as u8};}
        let actor=one(&x[at..at+2]);at+=2;let phase=one(&x[at..at+4]);at+=4;let public_id=one(&x[at..at+16]);at+=16;
        let mut history=Vec::new();let mut ended=false;
        for _ in 0..19{let token=one(&x[at..at+6]);at+=6;
            if token==0{ended=true;}else{assert!(!ended,"history padding gap");history.push(token as u8);}}
        assert_eq!(at,WIDTH);let o=Self{cards,actor,phase,public_id,history};
        assert_eq!(Self::decode(o.key()),o,"invalid or noncanonical features");o
    }
}
