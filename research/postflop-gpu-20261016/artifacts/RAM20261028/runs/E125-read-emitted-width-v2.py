"""Additive120/75 instruction reader: invert every7width changes, retain original gates."""
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
H=ROOT/'runs/E125-resource';O=H/'execution'
assert len(sys.argv)==2
P=h.read(H/'emitted-reader-protocol-v2.json');h.pin(H/'emitted-reader-protocol-v2.json',sys.argv[1])
for path,digest in P['input_sha256'].items():h.pin(path,digest)
old=h.read(H/'report.json');assert set(k for k,v in old['gates'].items()if not v)=={'compute_120:one_u16_load_instead_of_u32','compute_75:one_u16_load_instead_of_u32'}
def alpha(text):
    mapping={};counts={}
    def one(match):
        word=match[0];prefix=re.match(r'%[a-z]+',word)[0]
        if word not in mapping:
            mapping[word]=prefix+str(counts.get(prefix,0));counts[prefix]=counts.get(prefix,0)+1
        return mapping[word]
    return re.sub(r'%(?:rd|rs|r|f|p)\d+',one,text)
def inverse(text,arch):
    assert text.count('\t.reg .b16 \t%rs<8>;\n')==1
    value=text.replace('\t.reg .b16 \t%rs<8>;\n','',1);sites=[]
    if arch=='compute_120':
        assert 'ld.param.u64 \t%rd33, [up_chance_param_10];'in text and 'cvta.to.global.u64 \t%rd1, %rd33;'in text
        rx=re.compile(r'\tadd\.s64 \t(?P<scale>%rd\d+), (?P<index>%rd\d+), (?P=index);\n\tadd\.s64 \t(?P<address>%rd\d+), %rd1, (?P=scale);\n\tld\.global\.nc\.u16 \t(?P<small>%rs\d+), \[(?P=address)\];\n\tcvt\.u32\.u16 \t(?P<wide>%r\d+), (?P=small);')
        def replace(match):
            sites.append(match.groupdict())
            return f'\tshl.b64 \t{match["scale"]}, {match["index"]}, 2;\n\tadd.s64 \t{match["address"]}, %rd1, {match["scale"]};\n\tld.global.nc.u32 \t{match["wide"]}, [{match["address"]}];'
    else:
        assert arch=='compute_75'
        assert 'ld.param.u64 \t%rd49, [up_chance_param_10];'in text and 'cvta.to.global.u64 \t%rd2, %rd49;'in text
        # 75 converts the zero-extended u16 directly to64bits; original unsignedu16domain makes the former signed32to64 equivalent.
        assert value.count('\t.reg .b32 \t%r<70>;')==1
        value=value.replace('\t.reg .b32 \t%r<70>;','\t.reg .b32 \t%r<77>;',1)
        rx=re.compile(r'\tshl\.b64 \t(?P<scale>%rd\d+), (?P<index>%rd\d+), 1;\n\tadd\.s64 \t(?P<address>%rd\d+), %rd2, (?P=scale);\n\tld\.global\.nc\.u16 \t(?P<small>%rs\d+), \[(?P=address)\];\n\tcvt\.u64\.u16 \t(?P<wide>%rd\d+), (?P=small);')
        def replace(match):
            sites.append(match.groupdict());temporary='%r'+str(9000+len(sites))
            return f'\tshl.b64 \t{match["scale"]}, {match["index"]}, 2;\n\tadd.s64 \t{match["address"]}, %rd2, {match["scale"]};\n\tld.global.nc.u32 \t{temporary}, [{match["address"]}];\n\tcvt.s64.s32 \t{match["wide"]}, {temporary};'
    value=rx.sub(replace,value)
    assert len(sites)==7 and len({x['small']for x in sites})==7
    assert not re.search(r'\.u16\b|%rs\d+',value)
    return value,sites
results={};negative=[]
for arch in ['compute_120','compute_75']:
    before=(O/f'baseline-{arch}-up_chance.ptx.txt').read_text(encoding='utf-8')
    after=(O/f'candidate-{arch}-up_chance.ptx.txt').read_text(encoding='utf-8')
    reverted,sites=inverse(after,arch)
    assert alpha(reverted)==alpha(before)
    if arch=='compute_120':assert reverted==before
    results[arch]={'all7_unrolled_loads_accounted':True,'handperm_parameter':10,'actual_load_sites':sites,
        'whole_entry_inverse_exact_except_typed_load_zeroextend_and_element_stride_and_bijective_virtual_register_rename':True,
        'inverse_byteexact_without_register_rename':reverted==before,'all_FP_branches_barriers_predicates_and_other_metadata_reads_preserved':True}
    base='%rd1'if arch=='compute_120'else'%rd2'
    rules=[('wrong_table_base',base+', '+sites[0]['scale'],'%rd999, '+sites[0]['scale']),('wrong_conversion_destination',sites[0]['wide']+', '+sites[0]['small'],'%rd999'if arch=='compute_75'else'%r999'),('wrong_element_stride',sites[0]['index']+', '+sites[0]['index']if arch=='compute_120'else sites[0]['index']+', 1',sites[0]['index']+', %rd999'if arch=='compute_120'else sites[0]['index']+', 2')]
    for label,a,b in rules:
        if label=='wrong_conversion_destination':b=b+', '+sites[0]['small']
        assert a in after;corrupt=after.replace(a,b,1)
        try:replayed,_=inverse(corrupt,arch);assert alpha(replayed)==alpha(before)
        except AssertionError:negative.append(arch+':'+label)
        else:raise AssertionError('accepted corrupted '+label)
gates={k:v for k,v in old['gates'].items()if ':one_u16_load_instead_of_u32'not in k}
gates.update({arch+':all_source_unrolled_u16_loads_exact_inverse':v['all7_unrolled_loads_accounted']and v['whole_entry_inverse_exact_except_typed_load_zeroextend_and_element_stride_and_bijective_virtual_register_rename']for arch,v in results.items()})
assert all(gates.values())and len(negative)==6
h.save(H/'emitted-report.json',{'id':'E125-emitted-width','at':h.now(),'status':'pass_resources_and_all7_typed_unrolled_loads_exact_inverse',
    'original_resource_report_sha256':h.sha(H/'report.json'),'gates':gates,'architectures':results,'negative_reader_fixtures_rejected':negative,
    'resource_warnings':old['resource_warnings'],
    'observer_repairs':'Originalcheckerassumedoneemittedsite; one sourceload unrollsseven. Firstadditivereadercovers120butnot75differentbase/shift/directu64extend/virtualr renaming. V2accountsall7botharchitecturesandwhole-entryinverse. 75restoresu32intermediatereg/signedextendunderoriginalu16domain(all65536positivevaluesexact). Originalsource/protocol/checkers/reportsretained; no source/compiler/native/queryrepeat. Realregister30to40warningretained, sameoccupancy24/12/6,max1024,local0.',
    'application_kernel_launches':0,'solver_or_speed_samples':0,'candidate_accepted':False,'full_raw_and_other_qualification_pending':True})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);row=next(x for x in status['experiments']if x['id']=='E125')
    row.update(at=h.now(),status='running',stage='Resource and all7 emitted-width sites passed; full raw controls pending',correctness='source_resource_emitted_contract_only',reason='All7typedloads/stride/zeroextendwholeentryinversepassesboth120/75; other8entries/resourcesexact. Originalobserverassumptionsretained, no compiler/native repeats. Registers30to40warningretained; sameoccupancy/maxthreads/local0. No GPUaccuracy/speed/adoptionclaim.')
    status.update(updated_at=h.now(),active_experiment='E125',stage=row['stage'],activity=row['reason']);h.ar.atomic_json(h.ar.STATUS,status)
print(json.dumps({'status':'pass','all_unrolled_sites':14,'negative_reader_controls':6,'actual_register_warning':'30to40','next':'full_original_chance_raw_controls'}),flush=True)
