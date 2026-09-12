//! Fixed, range-independent stratification of the existing canonical particles.
//! Initial numerical research only: not used by production or learning yet.
use super::super::{equity::NUM_CLASSES, multiway::{CoupledDeck,SAMPLES}};

pub(crate) struct ParticleBatches {
    pub strata: Vec<Vec<usize>>,
    pub permutation: Vec<usize>,
    pub checksum: u64,
}

struct Rng(u64);
impl Rng {
    fn next(&mut self)->u64 {
        self.0=self.0.wrapping_add(0x9e3779b97f4a7c15);
        let mut z=self.0;
        z=(z^(z>>30)).wrapping_mul(0xbf58476d1ce4e5b9);
        z=(z^(z>>27)).wrapping_mul(0x94d049bb133111eb);
        z^(z>>31)
    }
    fn bounded(&mut self,bound:u64)->usize {
        let threshold=bound.wrapping_neg()%bound;
        loop {let n=self.next();if n>=threshold {return (n%bound) as usize;}}
    }
}

impl ParticleBatches {
    pub fn build(deck:&CoupledDeck)->Self {
        fn feature(d:&CoupledDeck,p:usize,h:usize)->u64 {
            (d.lower[p*NUM_CLASSES+h]+d.upper[p*NUM_CLASSES+h]) as u64
        }
        fn split(d:&CoupledDeck,mut ids:Vec<usize>,out:&mut Vec<Vec<usize>>) {
            if ids.len()==16 {out.push(ids);return;}
            let mut best=0;let mut best_variance=0;
            for h in 0..NUM_CLASSES {
                let mut sum=0;let mut squares=0;
                for &p in &ids {let x=feature(d,p,h);sum+=x;squares+=x*x;}
                // Exact integer variance score; normalization by 338 cancels.
                let variance=ids.len() as u64*squares-sum*sum;
                if variance>best_variance {best=h;best_variance=variance;}
            }
            ids.sort_by_key(|&p|(feature(d,p,best),p));
            let right=ids.split_off(ids.len()/2);
            split(d,ids,out);split(d,right,out);
        }
        assert_eq!(SAMPLES,1024);
        let mut strata=Vec::new();split(deck,(0..SAMPLES).collect(),&mut strata);
        let mut rng=Rng(90211);
        for leaf in &mut strata {
            for i in (1..leaf.len()).rev() {let j=rng.bounded((i+1) as u64);leaf.swap(i,j);}
        }
        let permutation:Vec<_>=(0..16).flat_map(|j|strata.iter().map(move |leaf|leaf[j])).collect();
        let mut checksum=0xcbf29ce484222325u64;
        for &p in &permutation {for byte in (p as u32).to_le_bytes() {checksum=(checksum^byte as u64).wrapping_mul(0x100000001b3);}}
        Self{strata,permutation,checksum}
    }

    /// Rotate whole batches, preserving every row of each coupled table.
    pub fn table(&self,source:&[u32],batch:usize)->Vec<u32> {
        assert!(batch<16);assert_eq!(source.len(),SAMPLES*NUM_CLASSES);
        (0..SAMPLES).flat_map(|i| {
            let p=self.permutation[(batch*64+i)%SAMPLES];
            source[p*NUM_CLASSES..(p+1)*NUM_CLASSES].iter().copied()
        }).collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn particle_batch_construction() {
        let d=CoupledDeck::shared();let b=ParticleBatches::build(&d);let again=ParticleBatches::build(&d);
        assert_eq!(b.permutation,again.permutation);assert_eq!(b.checksum,again.checksum);
        assert_eq!(b.strata.len(),64);assert!(b.strata.iter().all(|s|s.len()==16));
        let mut sorted=b.permutation.clone();sorted.sort_unstable();assert_eq!(sorted,(0..SAMPLES).collect::<Vec<_>>());
        let mut counts=[0usize;SAMPLES];
        for batch in 0..16 {
            for (leaf,&p) in b.permutation[batch*64..(batch+1)*64].iter().enumerate() {
                assert_eq!(p,b.strata[leaf][batch]);counts[p]+=1;
            }
            for source in [&d.order,&d.lower,&d.upper] {
                let rotated=b.table(source,batch);
                for i in 0..SAMPLES {
                    let p=b.permutation[(batch*64+i)%SAMPLES];
                    assert_eq!(&rotated[i*NUM_CLASSES..(i+1)*NUM_CLASSES],&source[p*NUM_CLASSES..(p+1)*NUM_CLASSES]);
                }
            }
        }
        assert!(counts.iter().all(|&x|x==1));
        println!("BATCH_CONSTRUCTION {}",serde_json::json!({"checksum_fnv64":format!("{:016x}",b.checksum),
            "construction_seed":90211,"strata":b.strata,"permutation":b.permutation}));
    }
}
