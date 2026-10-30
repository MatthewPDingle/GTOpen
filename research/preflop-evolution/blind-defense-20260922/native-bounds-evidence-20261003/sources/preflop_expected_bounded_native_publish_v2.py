"""Correct only helper declaration placement; preserve uncompiled v1 evidence."""
from pathlib import Path
import hashlib
import json
import time

STAGE=Path(__file__).resolve().parent
V1=STAGE/'native-bounded-export-sources-v1/publication.json'
DEST=STAGE/'native-bounded-export-sources-v2'
DECL='#[path="research_sampled/research_bounded_output_v1.rs"] mod research_bounded_output_v1;\n'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    previous=json.loads(V1.read_text())
    if DEST.exists():raise FileExistsError(DEST)
    changes=[]
    for record in previous['sources']:
        path=Path(record['new'])
        if sha(path)!=record['new_sha256']:raise ValueError('Uncompiled source changed')
        text=path.read_text()
        if not text.startswith(DECL):raise ValueError('Unexpected declaration location')
        lines=text[len(DECL):].splitlines(keepends=True)
        index=0
        while index<len(lines) and (lines[index].startswith('//!') or lines[index].startswith('#![') or not lines[index].strip()):
            index+=1
        lines.insert(index,DECL)
        changes.append((path,''.join(lines).encode(),record))
    DEST.mkdir()
    output=[]
    for path,raw,record in changes:
        path.write_bytes(raw)
        (DEST/path.name).write_bytes(raw)
        output.append(dict(record,new_sha256=sha(path),previous_uncompiled_sha256=record['new_sha256']))
        if sha(record['original'])!=record['original_sha256']:raise ValueError('Original changed')
    result=dict(previous,created=time.time(),sources=output,
        correction='Helper declaration moved below original inner docs and attributes; v1 snapshots preserved. No compilation or native invocation occurred before correction.',
        previous_publication=dict(path=str(V1),sha256=sha(V1)))
    with (DEST/'publication.json').open('x') as file:json.dump(result,file,indent=2)
    print(json.dumps(dict(passed=True,sources=output),indent=2))
if __name__=='__main__':main()
