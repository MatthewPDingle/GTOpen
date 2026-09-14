//! Streaming audit of the two saved f32 arenas, independent of solver code.
use std::io::{BufRead,Read};
fn main(){
 let mut r=std::io::BufReader::new(std::fs::File::open(std::env::args().nth(1).unwrap()).unwrap());
 let mut line=Vec::new();r.read_until(b'\n',&mut line).unwrap();assert_eq!(line,b"GTOPREFLOP2\n");
 line.clear();r.read_until(b'\n',&mut line).unwrap();assert!(line.starts_with(b"{"));
 let mut hash=0xcbf29ce484222325u64;let mut entries=0u64;let mut buf=vec![0u8;4*1024*1024];
 for _ in 0..2 {
  let mut len=[0u8;8];r.read_exact(&mut len).unwrap();let n=u64::from_le_bytes(len);entries+=n;
  let mut remaining=n.checked_mul(4).unwrap();
  while remaining>0 {let count=remaining.min(buf.len() as u64) as usize;r.read_exact(&mut buf[..count]).unwrap();
   for &b in &buf[..count]{hash=(hash^b as u64).wrapping_mul(0x100000001b3);}remaining-=count as u64;
  }
 }
 println!("{{\"arena_fingerprint\":\"{hash:016x}\",\"arena_entries\":{entries}}}");
}
