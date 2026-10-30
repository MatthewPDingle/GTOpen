"""Faults in private checkpoint copies; immutable large records shared by hard link."""
import json
import os
from pathlib import Path
import shutil
from storage_phase_run_20260920 import read,sha

def fnv(data):
    h=0xcbf29ce484222325
    for b in data:h=((h^b)*0x100000001b3)&((1<<64)-1)
    return h

def negative_controls(run):
    base=run.root/'at-100';other=run.root/'at-37'
    originals={p.name:sha(p) for p in base.iterdir()}
    def intact():
        assert {p.name:sha(p) for p in base.iterdir()}==originals,'Original complete checkpoint changed'
    def clone(name):
        root=run.root/('bad-'+name);root.mkdir()
        for p in base.iterdir():
            if p.name in ['index.json','complete']:
                shutil.copyfile(p,root/p.name);run.written+=p.stat().st_size
            else:os.link(p,root/p.name)
        return root
    def edit_index(root,change):
        path=root/'index.json';data=read(path);change(data)
        raw=json.dumps(data,separators=(',',':')).encode();path.write_bytes(raw)
        (root/'complete').write_text(f'{fnv(raw):016x}',encoding='ascii');run.written+=len(raw)+16
    def independent_file(root,name):
        # Never open a shared hard link for writing. Replace its directory entry with
        # a new private copy FIRST, and recheck the original checkpoint after each case.
        path=root/name;temporary=root/(name+'.private')
        assert not temporary.exists()
        size=path.stat().st_size
        assert run.written+size+1024**2<=16*1024**3,'Cumulative checkpoint write cap'
        shutil.copyfile(path,temporary);run.written+=size
        os.replace(temporary,path)
        assert path.stat().st_nlink==1
        return path
    def damage(root,name,kind):
        path=independent_file(root,name)
        if kind=='append':
            with path.open('ab') as f:f.write(b'x')
            run.written+=1
        elif kind=='truncate':
            with path.open('r+b') as f:f.truncate(path.stat().st_size-1)
        else:
            offset=73 if name.startswith('entry-') else 33
            with path.open('r+b') as f:
                f.seek(offset);value=f.read(1);f.seek(offset);f.write(bytes([value[0]^1]))
            run.written+=1
    def replace_link(root,name,source):
        (root/name).unlink();os.link(source,root/name)
    cases=[
        ('marker-missing',lambda r:(r/'complete').unlink(),'cannot find'),
        ('marker-partial',lambda r:(r/'complete').write_bytes(b'incomplete'),'Incomplete checkpoint'),
        ('record-missing',lambda r:(r/'entry-0-generation-0.bin').unlink(),'Missing or unexpected checkpoint file'),
        ('record-truncated',lambda r:damage(r,'entry-0-generation-0.bin','truncate'),'Wrong file length'),
        ('record-appended',lambda r:damage(r,'entry-0-generation-0.bin','append'),'Wrong file length'),
        ('record-flipped',lambda r:damage(r,'entry-0-generation-0.bin','flip'),'Payload checksum mismatch'),
        ('preflop-truncated',lambda r:damage(r,'preflop.bin','truncate'),'Preflop record size mismatch'),
        ('preflop-flipped',lambda r:damage(r,'preflop.bin','flip'),'Preflop checksum mismatch'),
        ('wrong-iteration',lambda r:edit_index(r,lambda d:d.__setitem__('iteration',101)),'Preflop record header mismatch'),
        ('wrong-shape',lambda r:edit_index(r,lambda d:d['shape'].__setitem__('weights',[1,1])),'Checkpoint identity or rebuilt shape mismatch'),
        ('wrong-entry-shape',lambda r:edit_index(r,lambda d:d['entries'][0].__setitem__(3,d['entries'][0][3]+1)),'Checkpoint key, generation, iteration or rebuilt shape mismatch'),
        ('wrong-generation',lambda r:edit_index(r,lambda d:d['entries'][0].__setitem__(1,1)),'Checkpoint key, generation, iteration or rebuilt shape mismatch'),
        ('duplicate-key',lambda r:edit_index(r,lambda d:d['entries'][1].__setitem__(0,0)),'Checkpoint key, generation, iteration or rebuilt shape mismatch'),
        ('mixed-generation',lambda r:replace_link(r,'entry-0-generation-0.bin',other/'entry-0-generation-0.bin'),'Wrong identity, version, shape, iteration, generation or checksum header'),
        ('swapped-pot',lambda r:replace_link(r,'entry-0-generation-0.bin',base/'entry-3-generation-0.bin'),['Wrong file length','Wrong identity, version, shape, iteration, generation or checksum header']),
        ('extra-record',lambda r:(r/'unexpected.bin').write_bytes(b'extra'),'Missing or unexpected checkpoint file'),
    ]
    for name,key in [('wrong-weights','boards_fnv64'),('wrong-subtree','subtree_fnv64'),('wrong-binary','executable_fnv64'),('wrong-algorithm','algorithm')]:
        def change(root,key=key):
            edit_index(root,lambda d:d['identity'].__setitem__(key,'mismatch'))
        cases.append((name,change,'Checkpoint identity or rebuilt shape mismatch'))
    results={}
    for name,change,error in cases:
        root=clone(name);change(root)
        run.written+=1024 # Conservative allowance for the tiny fault writes.
        assert run.written<=16*1024**3
        intact();results[name]=run.run('reject-'+name,100,resume=root,expected_error=error);intact()
    results['existing-complete']=run.run('existing-complete',100,resume=base,save=base,expected_error='already exists')
    intact()
    return dict(cases=results,original_complete_checkpoint_unchanged=True,
        copying_note='Large immutable records use same-volume hard links. Changed files are detached before writing; original hashes verified after every control.')
