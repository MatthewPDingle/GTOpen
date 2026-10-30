"""Synthetic interruption equivalence and corruption rejection; no poker runs."""
import json
from pathlib import Path
import time
from stack_context_archive_recovery_v1 import recover
from stack_context_cycle_archive_v1 import make_plan, sha, read
from stack_context_cycle_archive_v2 import archive_cycle
from owned_research_archive_v1 import pack
from owned_columnar_evaluation_archive_v1 import durable, encoded

OUT=Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
ROOT=Path('S:/GTOpen-research/stack-context-archive-recovery-check-v1')
TOKEN='synthetic-archive-recovery-v1'; NAME='stack-context-archive-recovery-check-v1'


def files(root):
    return {str(p):sha(p) for p in root.rglob('*') if p.is_file()}


def fixture(label):
    folder=ROOT/label; source=folder/'raw'; dest=folder/'archive'; source.mkdir(parents=True)
    for i in range(3):
        part=source/f'part-{i}';part.mkdir()
        durable(part/'values.json',encoded(dict(i=i,values=list(range(i,500+i)))))
        durable(part/'metadata.json',encoded(dict(identity=str(i))))
    plan=make_plan(source,dest,root=ROOT,token=TOKEN,guard=lambda:None)
    job=plan['jobs'][0]
    pack(job['source'],job['names'],job['destination'],root=ROOT,token=TOKEN,guard=lambda:None)
    return source,dest,plan,files(folder)


def main():
    began=time.monotonic();ROOT.mkdir();durable(ROOT/'archive-owner.json',encoded(dict(format=1,token=TOKEN,purpose='new-research-scratch-v1')))
    source,dest,plan,expected=fixture('positive')
    result=recover(dest,root=ROOT,token=TOKEN,expected=expected,guard=lambda:None)
    reference=ROOT/'reference';reference.mkdir()
    # Identical raw inputs; archive encoder and bundle grouping remain original.
    for path in source.rglob('*'):
        if path.is_file():
            target=reference/'raw'/path.relative_to(source);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(path.read_bytes())
    archive_cycle(reference/'raw',reference/'archive',root=ROOT,token=TOKEN,guard=lambda:None,retire=False)
    for p in dest.glob('bundle-*'):
        assert p.read_bytes()==(reference/'archive'/p.name).read_bytes()
    a,b=read(dest/'index.json'),read(reference/'archive/index.json')
    assert {k:v for k,v in a.items() if k!='plan_sha256'}=={k:v for k,v in b.items() if k!='plan_sha256'}
    assert all(sha(p)==h for p,h in expected.items()) and not (dest/'retired.json').exists()
    rejected=[]
    for mode in ('source','plan','bundle','manifest','orphan','extra-raw','extra-archive','escape','duplicate','missing-source'):
        src,dst,pl,exp=fixture(mode)
        if mode=='source':(src/'part-0/values.json').write_text('{}')
        elif mode=='plan':(dst/'plan.json').write_text('{}')
        elif mode=='bundle':(dst/'bundle-00000.xz').write_bytes(b'corrupt')
        elif mode=='manifest':(dst/'bundle-00000.xz.json').write_text('{}')
        elif mode=='orphan':(dst/'bundle-00001.xz').write_bytes(b'orphan')
        elif mode=='extra-raw':(src/'extra.json').write_text('{}')
        elif mode=='extra-archive':(dst/'extra.json').write_text('{}')
        elif mode=='missing-source':(src/'part-2/values.json').unlink()
        else:
            if mode=='escape':pl['jobs'][1]['destination']=str(ROOT/'escaped.xz')
            else:pl['jobs'][1]['names'].append(pl['jobs'][1]['names'][0])
            (dst/'plan.json').write_bytes(encoded(pl));exp[str(dst/'plan.json')]=sha(dst/'plan.json')
        before=files(src.parent)
        try:recover(dst,root=ROOT,token=TOKEN,expected=exp,guard=lambda:None)
        except (ValueError,FileNotFoundError):rejected.append(mode)
        else:raise AssertionError('Accepted '+mode)
        assert before==files(src.parent),'Rejection mutated evidence: '+mode
    assert len(rejected)==10
    sources=[Path(__file__),Path(__file__).with_name('stack_context_archive_recovery_v1.py'),
        Path(__file__).with_name('stack_context_cycle_archive_v1.py'),Path(__file__).with_name('stack_context_cycle_archive_v2.py'),
        Path(__file__).with_name('owned_research_archive_v1.py'),Path(__file__).with_name('owned_columnar_evaluation_archive_v1.py')]
    value=dict(passed=True,complete=True,seconds=time.monotonic()-began,synthetic_only=True,
        uninterrupted_bundle_bytes_equal=True,existing_bytes_preserved=True,raw_files_retired=False,
        rejected=rejected,inputs={str(p):sha(p) for p in sources},positive=result)
    durable(OUT/(NAME+'-result.json'),encoded(value));print(json.dumps(value))


if __name__=='__main__':main()
