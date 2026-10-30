/// Join the original CPU plan/budget work and CUDA ownership setup before
/// returning either result. Budget errors keep their original priority.
/// Small trees keep the original serial path; OS spawn failure falls back.
fn coordinate_initialization<P,G:Send,F:FnOnce()->Result<P,String>,C:Fn()->Result<G,String>+Sync>(eligible:bool,plan:F,create:C)->Result<(P,G),String>{
 if !eligible{let p=plan()?;return Ok((p,create()?));}
 std::thread::scope(|scope|{
  let worker=std::thread::Builder::new().name("gtopen-cuda-init".into()).spawn_scoped(scope,||create());
  let p=plan();let result=worker.ok().map(|h|h.join());
  let p=p?;
  let gpu=match result{Some(Ok(v))=>v?,Some(Err(payload))=>std::panic::resume_unwind(payload),None=>create()?};
  Ok((p,gpu))
 })
}
