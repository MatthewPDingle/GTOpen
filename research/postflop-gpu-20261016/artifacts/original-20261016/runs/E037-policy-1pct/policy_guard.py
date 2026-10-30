"""Pin the additive pre-timing policy; original provenance remains authoritative."""
import datetime, hashlib, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
OLD=ROOT/'runs/E037-primary-plan'
EXECUTION=ROOT/'runs/E037-policy-execution'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def moment(value):return datetime.datetime.fromisoformat(value.replace('Z','+00:00'))
def create_json(path,value):
    with Path(path).open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,indent=2);f.write('\n')
def verify(expected_authorization):
    authpath=HERE/'authorization.json'
    assert sha(authpath)==expected_authorization
    auth=read(authpath);policy=read(HERE/'policy.json');seal=read(HERE/'scripts-manifest.json')
    assert auth['candidate']=='E037' and auth['independent_policy_review_pass'] is True
    assert auth['effective_policy_sha256']==sha(HERE/'policy.json')
    assert auth['policy_manifest_sha256']==sha(HERE/'scripts-manifest.json')
    assert auth['original_authorization_sha256']==policy['original_authorization']['sha256']==sha(OLD/'authorization.json')
    assert seal['status']=='FROZEN_PROSPECTIVE_NOT_EXECUTED'
    for name,h in seal['script_sha256'].items():assert sha(HERE/name)==h,name
    for name,h in seal['reference_sha256'].items():assert sha(name)==h,name
    for name,h in auth['evidence_sha256'].items():assert sha(name)==h,name
    assert auth['evidence_sha256'][str(HERE/'scripts-manifest.json')]==sha(HERE/'scripts-manifest.json')
    review=auth['review'];assert sha(review['path'])==review['sha256']
    assert auth['evidence_sha256'][review['path']]==review['sha256']
    assert Path(review['path']).resolve()==(ROOT/'comparisons/E037-policy-review/report.json').resolve()
    assert read(review['path'])['independent_policy_review_pass'] is True
    assert policy['required_gain_pct']==1.0 and policy['fixture_slowdown_threshold_pct']==0.0
    assert policy['order']==read(OLD/'protocol.json')['order']
    decision=read(policy['root_decision']['path'])
    assert moment(decision['at'])<=moment(policy['at'])<=moment(auth['at'])
    assert decision['pre_timing_evidence']['native_or_timing_run_started'] is False
    return policy,auth

def receipt(expected_authorization):
    policy,auth=verify(expected_authorization)
    p=EXECUTION/'pre-primary.json';r=read(p)
    assert r['policy_sha256']==sha(HERE/'policy.json') and r['policy_manifest_sha256']==sha(HERE/'scripts-manifest.json')
    assert r['policy_authorization_sha256']==expected_authorization
    assert r['original_authorization_sha256']==sha(OLD/'authorization.json')
    assert r['all_seven_run_directories_absent'] is True and r['order']==policy['order']
    assert moment(auth['at'])<=moment(r['at'])
    for identity in policy['order']:
        run=read(ROOT/'runs'/identity/'report.json')
        assert moment(r['at'])<=moment(run['started_at']),identity
    end=read(EXECUTION/'exit.json');assert end['returncode']==0
    return {'path':str(HERE/'policy.json'),'sha256':sha(HERE/'policy.json'),'policy_manifest_sha256':sha(HERE/'scripts-manifest.json'),'policy_authorization_sha256':expected_authorization,'original_protocol_sha256':policy['original_protocol']['sha256'],'original_authorization_sha256':sha(OLD/'authorization.json'),'root_user_decision':policy['root_decision'],'pre_primary_receipt':{'path':str(p),'sha256':sha(p)},'changed_before_any_native_timing':True,'supersedes':policy['supersedes'],'primary_pass_is_preliminary':True,'adoption_requirements':policy['adoption_requirements'],'no_material_cost_validation':{'status':'pending_resource_and_broader_qualification','source_evidence':policy['source_cost_evidence']},'candidate_accepted':False}
