"""Repair only six identified display strings after an ANSI-decoded JSON roundtrip."""
import copy, json, locale, sys, shutil
sys.path.insert(0, r'X:\Dev\GTOpen-gpu-research-20261016\tools')
import postflop_autoresearch as ar
out=ar.RESEARCH/'runs/D026-dashboard-encoding'
out.mkdir(exist_ok=False)
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'), timeout=3):
    before=json.loads(ar.STATUS.read_text(encoding='utf-8'))
    ar.atomic_json(out/'status-before.json',before)
    after=copy.deepcopy(before)
    changes=[]
    def fix(container, key, path):
        old=container[key]
        new=old.replace('\u00c2\u00b7','\u00b7').replace('\u00e2\u20ac\u201c','\u2013')
        assert old != new, path
        container[key]=new
        changes.append({'path':path,'before':old,'after':new})
    fix(after['hardware'],'gpu','$.hardware.gpu')
    fix(after['hardware'],'backend','$.hardware.backend')
    for index,fixture in enumerate(after['fixtures']):
        fix(fixture,'description',f'$.fixtures[{index}].description')
    index=next(i for i,e in enumerate(after['experiments']) if e['id']=='D015')
    fix(after['experiments'][index],'reason',f'$.experiments[{index}].reason')
    assert len(changes)==6
    def suspicious(value):
        if isinstance(value,dict): return any(suspicious(v) for v in value.values())
        if isinstance(value,list): return any(suspicious(v) for v in value)
        return isinstance(value,str) and any(c in value for c in ('\u00c2','\u00e2','\ufffd'))
    assert not suspicious(after)
    restored=copy.deepcopy(after)
    restored['hardware']=before['hardware']
    for i in range(3): restored['fixtures'][i]['description']=before['fixtures'][i]['description']
    restored['experiments'][index]['reason']=before['experiments'][index]['reason']
    assert restored==before
    report={'id':'D026','status':'pass','scope':'Display encoding maintenance only; no solver or measurement changes',
            'created_at':ar.now(),'default_text_encoding':locale.getencoding(),
            'cause':'A manual status update read UTF-8 JSON with the Windows default encoding; runner and comparison tools already use explicit UTF-8.',
            'changed_strings':changes,'all_other_fields_equal_before_metadata_update':True,
            'preserved_failed_browser_report':r'X:\Dev\GTOpen\output\playwright\postflop-dashboard-20261016\accepted-audit-report-E015.json',
            'future_rule':'All status reads and writes must explicitly specify UTF-8.'}
    ar.atomic_json(out/'report.json',report)
    target=ar.DASHBOARD/'evidence/D026-dashboard-encoding/report.json'
    target.parent.mkdir(parents=True,exist_ok=True)
    assert not target.exists()
    shutil.copyfile(out/'report.json',target)
    after.update(updated_at=ar.now(),state='running',stage='Implementing E016 with validity checks',
                 activity='E015 retains a validated 9.62% cumulative gain. The next candidate tests player-0 reach reuse between iterations, with full invalidation after evaluation or state changes.')
    after['experiments'].append({'id':'D026','at':ar.now(),'title':'Repair six dashboard encoding strings','kind':'diagnostic',
        'status':'measured','correctness':'pass','reason':'Six display strings repaired with explicit UTF-8; all other data preserved. No solver performance claim.',
        'evidence':[{'label':'Encoding repair audit','url':'evidence/D026-dashboard-encoding/report.json'}]})
    ar.atomic_json(ar.STATUS,after)
    ar.atomic_json(out/'status-after.json',after)
print(json.dumps({'status':'pass','corrected_strings':len(changes),'default_encoding':locale.getencoding()}))
