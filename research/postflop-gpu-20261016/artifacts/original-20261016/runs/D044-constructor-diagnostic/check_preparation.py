"""Read-only checks and additive preparation record; no compiler or native run."""
from pathlib import Path
import ast,datetime,hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parent
REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=read(HERE/'source-manifest.json')
assert sha(HERE/'source-manifest.json')=='8f522e9f4c2c71537495492119b95be8c50f48be117d57206a3a2c602f59b013'
for name,h in source['artifact_sha256'].items():assert sha(HERE/name)==h,name
for name in ['build.py','cohort.py','assess.py']:ast.parse((HERE/name).read_text(encoding='utf-8'),filename=name)
plan=read(HERE/'protocol.json')
accepted=read(ROOT/'binaries/E020-postflop_autoresearch.manifest.json')['source_sha256']
current={name:sha(REPO/name) for name in accepted}
assert current==accepted,'Prepare against restored accepted E020 only'
status=read(Path(r'X:\Dev\GTOpen\web\research\postflop-gpu-20261016\status.json'))
for identity in plan['order']:
    assert not (ROOT/'runs'/identity).exists()
    assert not any(v.get('id')==identity for v in status['experiments'])
for path in [Path(plan['build_target_root']),ROOT/'runs/D044-build',ROOT/'runs/D044-execution',ROOT/'comparisons/D044-constructor-diagnostic',ROOT/'binaries/D044-postflop_autoresearch.exe',ROOT/'binaries/D044-postflop_autoresearch.manifest.json']:
    assert not path.exists(),str(path)
assert plan['expected_profile_records_per_run']==3 and plan['expected_convergence_records_per_run']==23
assert plan['order']==['D044B1','D044P1','D044P2','D044B2','D044B3','D044P3']
for item in read(HERE/'schema.json')['expected_identity']:
    board=item['board'];ranks='23456789TJQKA';suits='cdhs'
    cards=[4*ranks.index(board[i])+suits.index(board[i+1]) for i in range(0,len(board),2)]
    assert len(set(cards))==len(cards)==item['board_cards']
    assert sum(1<<c for c in cards)==item['board_mask']
record={'status':'pass_source_only','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'python_ast_parse':['build.py','cohort.py','assess.py'],'all162_checkout_sources_match_E020':True,
    'all_source_artifacts_unchanged':True,'schema_board_masks_match_existing_card_encoding':True,
    'run_ids_unused':plan['order'],'target_and_output_absent':True,'expected_instrumented_markers_per_run':3,
    'builds':0,'native_runs':0,'gpu_executions':0,'production_edits':0}
with (HERE/'preparation.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(record,f,indent=2);f.write('\n')
print(json.dumps(record))
