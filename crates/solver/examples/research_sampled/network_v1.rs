//! Small research policy adapter. Parameters are fixtures until learning qualifies.
use serde_json::Value;
use super::observation_v1::{Observation,WIDTH};
use super::poker_reference_v1::{Game,Key};

pub struct Network{weights:[Vec<f32>;3],biases:[Vec<f32>;3]}
impl Network{
 pub fn new(v:&Value)->Self{
  let vector=|name:&str|v[name].as_array().unwrap().iter().map(|x|x.as_f64().unwrap()as f32).collect::<Vec<_>>();
  let out=Self{weights:[vector("w0"),vector("w1"),vector("w2")],biases:[vector("b0"),vector("b1"),vector("b2")]};
  assert_eq!(out.weights[0].len(),WIDTH*64);assert_eq!(out.weights[1].len(),64*64);assert_eq!(out.weights[2].len(),64*4);
  assert_eq!(out.biases[0].len(),64);assert_eq!(out.biases[1].len(),64);assert_eq!(out.biases[2].len(),4);
  assert!(out.weights.iter().chain(out.biases.iter()).flatten().all(|x|x.is_finite()));out
 }
 pub fn scores(&self,features:&[f32;WIDTH])->[f64;4]{
  fn layer(input:&[f32],weights:&[f32],bias:&[f32],out:&mut[f32],relu:bool){
   for(o,value)in out.iter_mut().enumerate(){let mut sum=bias[o];for i in 0..input.len(){sum+=weights[o*input.len()+i]*input[i];}*value=if relu{sum.max(0.)}else{sum};}
  }
  let mut first=[0.;64];let mut second=[0.;64];let mut out=[0.;4];
  layer(features,&self.weights[0],&self.biases[0],&mut first,true);layer(&first,&self.weights[1],&self.biases[1],&mut second,true);
  layer(&second,&self.weights[2],&self.biases[2],&mut out,false);out.map(|x|x as f64)
 }
 pub fn policy(&self,game:&Game,key:Key,n:usize,variant:usize)->[f64;4]{
  let o=Observation::decode(key);assert_eq!(o.legal_actions(game),n);
  let values=match variant{0=>self.scores(&o.features()),1=>[-1.,-0.7,-0.4,-0.1],2=>[0.;4],3=>[-3.,-2.,-1.,100.],_=>panic!("unknown fixture")};
  regret_policy(values,n)
 }
}
pub fn regret_policy(v:[f64;4],n:usize)->[f64;4]{
 assert!((2..=4).contains(&n)&&v.iter().all(|x|x.is_finite()));let mut p=[0.;4];let z=v[..n].iter().map(|x|x.max(0.)).sum::<f64>();
 if z>0.{for a in 0..n{p[a]=v[a].max(0.)/z;}}else{
  let mut best=0;for a in 1..n{if v[a]>v[best]{best=a;}}p[best]=1.;
 }p
}
