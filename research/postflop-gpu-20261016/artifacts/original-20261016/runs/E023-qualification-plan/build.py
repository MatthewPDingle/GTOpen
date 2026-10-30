"""Root-only: compile and freeze seven E023 control binaries, never run tests."""
import common as c

def main():
    assert len(c.sys.argv)==2,'authorization SHA required'
    p=c.initialize(c.sys.argv[1]);out=c.Path(p['build_directory'])
    target_groups=[({'postflop_state_perf':'postflop_state_perf','postflop_action_menus':'postflop_action_menus','postflop_resume_state':'postflop_resume_state','gpu':'gpu'},p['build_order'][0]['command']),({'solver':'continuation-tests','continuation_paging':'continuation_paging','continuation_symmetry':'continuation_symmetry'},p['build_order'][1]['command'])]
    with c.ar.exclusive_lock(c.ROOT/'gpu-run.lock'):
        c.ar.refuse_active(c.ar.live_status());c.disk_check();c.verify_source()
        for targets,command in target_groups:
            for name in targets.values():
                bp=c.ROOT/'binaries'/('E023-'+name+'.exe')
                assert not bp.exists() and not bp.with_suffix('.manifest.json').exists(),str(bp)
        out.mkdir(exist_ok=False)
        before=c.ar.source_identity();c.save(out/'source-before.json',before)
        target=c.Path(p['target_directory']).resolve()
        assert target==c.ROOT/'build-e023-qualification' and not target.exists()
        target.mkdir(exist_ok=False)
        c.save(out/'target-isolation.json',{'target':str(target),'absent_before_build':True,'single_source_arm':'E023'})
        env=c.os.environ.copy();env.update(CARGO_TARGET_DIR=str(target),RAYON_NUM_THREADS='16')
        pins={}
        for index,(targets,command) in enumerate(target_groups,1):
            c.verify_source()
            log,err=c.process(command,out/('cargo-'+str(index)),env,p['resource_policy']['build_timeout_seconds'])
            c.verify_source()
            items=[c.json.loads(line) for line in log.read_text(encoding='utf-8').splitlines()]
            artifacts=[d for d in items if d.get('reason')=='compiler-artifact' and d.get('profile',{}).get('test') and d.get('executable') and d['target']['name'] in targets]
            assert len(artifacts)==len(targets) and {d['target']['name'] for d in artifacts}==set(targets)
            assert any(d.get('reason')=='build-finished' and d['success'] is True for d in items)
            cargo_artifacts=[d for d in items if d.get('reason')=='compiler-artifact']
            for item in cargo_artifacts:
                for filename in item.get('filenames',[])+([item['executable']] if item.get('executable') else []):
                    assert c.Path(filename).resolve().is_relative_to(target),('artifact outside new target',filename)
            solver=[d for d in cargo_artifacts if d['target']['name']=='solver' and d['target']['kind']==['lib'] and not d.get('profile',{}).get('test')]
            assert len(solver)==1
            for item in solver+artifacts:
                assert item['fresh'] is False,('refuse cached solver/test artifact',item['target']['name'])
                assert c.Path(item['manifest_path']).resolve()==c.REPO/'crates/solver/Cargo.toml'
                expected=c.REPO/'crates/solver/src/lib.rs' if item['target']['name']=='solver' else c.REPO/'crates/solver/tests'/(item['target']['name']+'.rs')
                assert c.Path(item['target']['src_path']).resolve()==expected
            for item in artifacts:
                name='E023-'+targets[item['target']['name']];dest=c.ROOT/'binaries'/(name+'.exe')
                c.shutil.copyfile(item['executable'],dest)
                data=dest.read_bytes();cuda=(c.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes()
                assert cuda in data and b'__global__ void up_action_opponent(' in data,'candidate CUDA missing'
                manifest={**before,'candidate':'E023','binary_sha256':c.ar.sha256(dest),'built_at':c.ar.now(),'build_command':command,'build_log':str(log),'build_log_sha256':c.ar.sha256(log),'build_stderr_log':str(err),'build_stderr_sha256':c.ar.sha256(err),'source_matches_primary_binary':True,'source_matches_prebuild':True,'primary_manifest':p['candidate_primary_manifest'],'primary_manifest_sha256':c.ar.sha256(c.Path(p['candidate_primary_manifest'])),'build_script_sha256':c.ar.sha256(c.Path(__file__)),'scope':'Broader correctness only; primary performance binary remains unchanged'}
                manifest.update(target_dir=str(target),cargo_artifact=item,solver_artifact=solver[0],expected_complete_cuda_embedded=True,append_entry_marker_present=True)
                c.save(dest.with_suffix('.manifest.json'),manifest)
                pins[name]=c.binary_pair(name)[2]
                print(name,pins[name]['binary_sha256'],flush=True)
        c.verify_source();c.verify_binary_pins(pins)
        c.save(out/'complete.json',{'at':c.ar.now(),'status':'pass','source_sha256':c.SOURCES,'binary_pins':pins,'authorization_sha256':c.sys.argv[1],'native_tests_executed':0,'accepted':False,'deployed':False})
    print('Broader builds complete; root must also finish holdout/resource builds and seal all-builds-ready before GPU controls.',flush=True)

if __name__=='__main__':main()
