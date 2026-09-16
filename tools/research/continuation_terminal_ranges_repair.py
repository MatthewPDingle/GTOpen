"""Recorded syntax-only repair of N37, with separate outputs and input freeze."""
import datetime as dt
from pathlib import Path
import subprocess
import continuation_terminal_ranges as scan

scan.OUT=scan.BASE/'terminal-ranges-repaired-20260916'
OUT=scan.OUT


def main():
    import continuation_paired_blend_gpu as gpu
    gpu.control.idle()
    assert scan.old.read(scan.BASE/'terminal-ranges-20260916/queue-status.json')['stage']=='failed'
    assert not list((scan.BASE/'terminal-ranges-20260916').glob('eight-*.json'))
    assert scan.old.read(scan.BASE/'final-queue-20260916/status.json')['stage']=='N35_gate_failed'
    assert not any(p['Name'].lower() in ['learned_interface.exe','cargo.exe','rustc.exe'] for p in gpu.control.transfer.original.queue.processes())
    original=scan.old.read(scan.BASE/'terminal-ranges-20260916/input-freeze.json')
    archived=scan.BASE/'terminal-ranges-20260916/source-before-repair.rs.txt'
    assert scan.old.sha(archived)==original['inputs']['crates/solver/examples/continuation_terminal_ranges.rs']
    paths=[Path(__file__),OUT/'REPAIR.md',archived,scan.BASE/'terminal-ranges-20260916/build.log',scan.ROOT/'crates/solver/Cargo.toml']
    scan.old.write(OUT/'repair-inputs.json',dict(registered_at=dt.datetime.now(dt.timezone.utc).isoformat(),
        inputs={str(p.relative_to(scan.ROOT)).replace('\\','/'):scan.old.sha(p) for p in paths},production_enabled=False))
    scan.prepare()
    scan.old.write(OUT/'status.json',dict(stage='building',production_enabled=False))
    with (OUT/'build.log').open('w',encoding='utf-8') as log:
        for cmd in ['test','build']:
            subprocess.run(['cargo',cmd,'--release','-p','solver','--features','preflop-research','--example','continuation_terminal_ranges','--target-dir','target/learned-interface-filtered','-j2'],cwd=scan.ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    scan.old.write(OUT/'status.json',dict(stage='scanning',production_enabled=False))
    scan.run()
    scan.old.write(OUT/'status.json',dict(stage='complete',updated=dt.datetime.now(dt.timezone.utc).isoformat(),production_enabled=False))


if __name__=='__main__':
    try:main()
    except Exception as error:
        scan.old.write(OUT/'status.json',dict(stage='failed',error=str(error),production_enabled=False));raise
