from pathlib import Path
import subprocess,re,difflib,hashlib,json

HERE=Path(__file__).resolve().parent
ROOT=Path('T:/Dev/GTOpen/target/autoresearch/preflop-20260910')
REL='crates/solver/src/preflop/gpu.rs'
helper=(HERE/'allocation_trace.rs').read_text(encoding='utf-8')
literal=subprocess.check_output(['git','show',f'1b8fc3f:{REL}'],cwd=ROOT).decode()
corrected=(HERE.parent/'original-modeled-budget-baseline/gpu.rs').read_text(encoding='utf-8')
manifests={}
for label,before in [('literal-1b8fc3f',literal),('original-forced-budget-corrected',corrected)]:
    declarations=re.findall(r'^    (d_\w+): CudaSlice<[^>]+>,',before,re.M)
    anchor='        let ctx = CudaContext::new(0).map_err(e)?;'
    assert before.count(anchor)==1
    after=before.replace(anchor, f'        let mut allocation_trace = AllocationTrace::new("{label}")?;\n'+anchor+'\n        allocation_trace.snapshot(&ctx,"after_context_creation")?;')
    anchor='        unsafe { ctx.disable_event_tracking() };'
    assert after.count(anchor)==1
    after=after.replace(anchor,anchor+'\n        allocation_trace.snapshot(&ctx,"after_stream_setup")?;')
    anchor='        let module = ctx.load_module(ptx).map_err(e)?;'
    assert after.count(anchor)==1
    after=after.replace(anchor,anchor+'\n        allocation_trace.snapshot(&ctx,"after_module_load")?;')
    anchor='            f_discount: func("pf_discount_nodes")?,'
    assert after.count(anchor)==1
    after=after.replace(anchor,'''            f_discount: {
                let function = func("pf_discount_nodes")?;
                allocation_trace.snapshot(&ctx,"after_constructor_function_loads")?;
                function
            },''')
    start=after.index('        Ok(PreflopGpu {')
    end=after.index('\n    fn cfg(',start)
    constructor=after[start:end]
    fields=[]
    edits=[]
    for m in re.finditer(r'^            (d_\w+): ',constructor,re.M):
        name=m.group(1)
        if name not in declarations: continue
        first=m.end(); depth=0; last=first
        for i in range(first,len(constructor)):
            char=constructor[i]
            if char in '({[': depth+=1
            elif char in ')}]': depth-=1
            elif char==',' and depth==0: last=i; break
        assert last>first,(label,name)
        expr=constructor[first:last]
        fields.append(name)
        edits.append((first,last,f'allocation_trace.buffer(&ctx, "{name}", {expr})?'))
    assert set(fields)==set(declarations) and len(fields)==len(declarations),(label,fields,declarations)
    for first,last,expr in reversed(edits): constructor=constructor[:first]+expr+constructor[last:]
    constructor=constructor.replace('        Ok(PreflopGpu {','        let gpu = PreflopGpu {',1)
    tail='            stream,\n        })\n    }'
    assert constructor.count(tail)==1
    ledger='\n'.join(f'                ("{name}", gpu.{name}.len(), gpu.{name}.num_bytes()),' for name in fields)
    constructor=constructor.replace(tail,'''            stream,
        };
        if allocation_trace.mode != 0 {
            allocation_trace.finish(&gpu._ctx, need, &[
'''+ledger+'''
            ])?;
        }
        Ok(gpu)
    }''')
    after=after[:start]+constructor+after[end:]
    anchor='pub struct PreflopGpu {'
    assert after.count(anchor)==1
    after=after.replace(anchor,helper+'\n'+anchor,1)
    (HERE/f'{label}-gpu.rs').write_text(after,encoding='utf-8',newline='\n')
    (HERE/f'{label}.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),'a/'+REL,'b/'+REL)),encoding='utf-8',newline='\n')
    manifests[label]={'baseline_gpu_sha256':hashlib.sha256(before.encode()).hexdigest(),'trace_gpu_sha256':hashlib.sha256(after.encode()).hexdigest(),'all_cuda_slice_fields':fields,'allocation_count':len(fields)}
(HERE/'manifest.json').write_text(json.dumps({'status':'proposal only; not built or run; no existing frozen file edited','variants':manifests},indent=2)+'\n',encoding='utf-8')
example=(HERE/'preflop_allocation_control.rs').read_text(encoding='utf-8')
cargo=(ROOT/'crates/solver/Cargo.toml').read_text(encoding='utf-8')
assert 'name = "preflop_allocation_control"' not in cargo
updated=cargo.rstrip()+'\n\n[[example]]\nname = "preflop_allocation_control"\nrequired-features = ["gpu"]\n'
patch=''.join(difflib.unified_diff([],example.splitlines(True),'/dev/null','b/crates/solver/examples/preflop_allocation_control.rs'))
patch+=''.join(difflib.unified_diff(cargo.splitlines(True),updated.splitlines(True),'a/crates/solver/Cargo.toml','b/crates/solver/Cargo.toml'))
(HERE/'add-constructor-control.patch').write_text(patch,encoding='utf-8',newline='\n')
