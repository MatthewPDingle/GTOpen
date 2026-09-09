"""Compare this collection with the already inspected pass-2 source snapshot."""
import importlib.util, json, collections, re
from pathlib import Path
spec=importlib.util.spec_from_file_location('calling_audit',Path(__file__).with_name('calling_audit.py'))
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
def run():
    current=a.verify_inputs();prior_path=a.ROOT/'output/ignition-transfer-v1/collection_manifest.json';prior=json.loads(prior_path.read_text());old=prior['training']
    a.require(current['files']==old['files'],'NL10 source files changed since pass 2; reserve new data before inspection')
    a.require(current['hand_ids']==old['hand_ids'],'NL10 hand IDs changed since pass 2; reserve new data before inspection')
    out=dict(schema=1,scope='Existing NL10 regular source collection only; not a claim about every unparsed file elsewhere.',previously_inspected_snapshot_sha256=a.digest(prior_path),current_collection_manifest_sha256=a.digest(a.PRIVATE/'manifest.json'),source_files=len(current['files']),unique_raw_hand_ids=len(current['hand_ids']),file_hashes_identical=True,hand_id_sets_identical=True,new_regular_source_files=0,new_regular_hand_ids=0,independent_holdout_available_in_this_corpus=False,prior_transfer_groups=list(prior['groups']),note='All four prior transfer groups were already evaluated in pass 2. No group is relabeled fresh. The dated regular corpus is unchanged byte for byte at collection time.',generator_sha256=a.digest(__file__))
    source=Path('T:/Dev/Poker Data/Ignition');groups=collections.defaultdict(list)
    for path in sorted(source.rglob('*.txt')):
        match=re.search(r' - \$([\d.]+)-\$([\d.]+) - ',path.name)
        if match:
            group='NL'+str(round(float(match[2])*100))+'-'+('zone' if 'ZONE' in path.name.upper() else 'regular')
            groups[group].append(path)
    known={'NL10-regular',*prior['groups']}
    out['filename_inventory']={k:dict(files=len(v),bytes=sum(p.stat().st_size for p in v),already_scored_group=k in known) for k,v in sorted(groups.items())}
    out['unscored_inventory_note']='No NL10 Zone files. Only one NL50 Zone file (835 bytes) lies outside recorded model/transfer groups. Outcomes were not parsed here; earlier broad format audits may have inspected it, so it is not asserted to be an independent holdout.'
    reserved=[dict(path=str(p.relative_to(source)),sha256=a.digest(p),bytes=p.stat().st_size) for k,v in groups.items() if k not in known for p in v]
    a.write(a.PRIVATE/'unscored-file-reservation.json',dict(files=reserved,note=out['unscored_inventory_note']))
    a.write(a.OUT/'source-availability.json',out);print('Verified unchanged: 574 source files / 38,341 unique raw IDs; no new NL10 regular holdout.')
if __name__=='__main__':run()
