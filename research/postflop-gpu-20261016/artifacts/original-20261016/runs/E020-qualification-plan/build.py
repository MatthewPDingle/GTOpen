"""Root-only: compile and freeze seven E020 control binaries, never run tests."""
import common as c

def main():
    assert len(c.sys.argv)==2,'authorization SHA required'
    p=c.initialize(c.sys.argv[1]);out=c.Path(p['build_directory'])
    target_groups=[({'postflop_state_perf':'postflop_state_perf','postflop_action_menus':'postflop_action_menus','postflop_resume_state':'postflop_resume_state','gpu':'gpu'},p['build_order'][0]['command']),({'solver':'continuation-tests','continuation_paging':'continuation_paging','continuation_symmetry':'continuation_symmetry'},p['build_order'][1]['command'])]
    with c.ar.exclusive_lock(c.ROOT/'gpu-run.lock'):
        c.ar.refuse_active(c.ar.live_status());c.disk_check();c.verify_source()
        for targets,command in target_groups:
            for name in targets.values():
                bp=c.ROOT/'binaries'/('E020-'+name+'.exe')
                assert not bp.exists() and not bp.with_suffix('.manifest.json').exists(),str(bp)
        out.mkdir(exist_ok=False)
        before=c.ar.source_identity();c.save(out/'source-before.json',before)
        env=c.os.environ.copy();env.update(CARGO_TARGET_DIR=str(c.ROOT/'build'),RAYON_NUM_THREADS='16')
        pins={}
        for index,(targets,command) in enumerate(target_groups,1):
            c.verify_source()
            log,err=c.process(command,out/('cargo-'+str(index)),env,p['resource_policy']['build_timeout_seconds'])
            c.verify_source()
            items=[c.json.loads(line) for line in log.read_text(encoding='utf-8').splitlines()]
            artifacts=[d for d in items if d.get('reason')=='compiler-artifact' and d.get('profile',{}).get('test') and d.get('executable') and d['target']['name'] in targets]
            assert len(artifacts)==len(targets) and {d['target']['name'] for d in artifacts}==set(targets)
            assert any(d.get('reason')=='build-finished' and d['success'] is True for d in items)
            for item in artifacts:
                name='E020-'+targets[item['target']['name']];dest=c.ROOT/'binaries'/(name+'.exe')
                c.shutil.copyfile(item['executable'],dest)
                manifest={**before,'candidate':'E020','binary_sha256':c.ar.sha256(dest),'built_at':c.ar.now(),'build_command':command,'build_log':str(log),'build_log_sha256':c.ar.sha256(log),'build_stderr_log':str(err),'build_stderr_sha256':c.ar.sha256(err),'source_matches_primary_binary':True,'source_matches_prebuild':True,'primary_manifest':p['candidate_primary_manifest'],'primary_manifest_sha256':c.ar.sha256(c.Path(p['candidate_primary_manifest'])),'build_script_sha256':c.ar.sha256(c.Path(__file__)),'scope':'Broader correctness only; primary performance binary remains unchanged'}
                c.save(dest.with_suffix('.manifest.json'),manifest)
                pins[name]=c.binary_pair(name)[2]
                print(name,pins[name]['binary_sha256'],flush=True)
        c.verify_source();c.verify_binary_pins(pins)
        c.save(out/'complete.json',{'at':c.ar.now(),'status':'pass','source_sha256':c.SOURCES,'binary_pins':pins,'authorization_sha256':c.sys.argv[1],'native_tests_executed':0,'accepted':False,'deployed':False})
    print('Broader builds complete; root must also finish holdout/resource builds and seal all-builds-ready before GPU controls.',flush=True)

if __name__=='__main__':main()
