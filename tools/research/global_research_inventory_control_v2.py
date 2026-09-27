"""Small real-filesystem inventory check and fail-closed activity controls."""
import json
from pathlib import Path
import tempfile
from global_research_inventory_v2 import measure
from ntfs_research_storage_v1 import allocated_bytes
from sampled_physical_root_evaluation_v1 import ROOT, sha
from later_average_support_v1 import OUT
from board_prefix_publication_v1 import atomic_json


def main():
    with tempfile.TemporaryDirectory(prefix='gtopen-inventory-v2-') as tmp:
        folder = Path(tmp).resolve()
        assert folder.parent == Path(tempfile.gettempdir()).resolve()
        assert folder.name.startswith('gtopen-inventory-v2-')
        (folder / 'child').mkdir()
        files = [folder/'one.bin', folder/'child'/'two.bin']
        files[0].write_bytes(b'a' * 10000)
        files[1].write_bytes(b'b' * 17001)
        result = measure(roots=[folder], activity=lambda: True)
        assert result == [dict(root=str(folder), files=2, logical_bytes=27001,
                              allocated_file_bytes=sum(allocated_bytes(p) for p in files))]
        rejected = 0
        def unknown(): raise ConnectionError('unverified test server')
        probes = [lambda: False, unknown]
        for probe in probes:
            try: measure(roots=[folder], activity=probe)
            except (AssertionError, ConnectionError): rejected += 1
            else: raise AssertionError('Unverified activity accepted')
        answers = iter([True, False])
        try: measure(roots=[folder], activity=lambda: next(answers))
        except AssertionError: rejected += 1
        else: raise AssertionError('Newly active production accepted')
    paths = [Path(__file__).resolve(), ROOT/'tools/research/global_research_inventory_v2.py',
             ROOT/'tools/research/bounded_parallel_evaluation_archive_v2.py',
             ROOT/'tools/research/hu_root_retained_storage_admitted_study_20260924.py',
             ROOT/'tools/research/ntfs_research_storage_v1.py']
    report = dict(passed=True, inputs={str(p):sha(p) for p in paths}, real_files_checked=2,
                  logical_bytes=27001, activity_rejections=rejected, gpu_used=False,
                  production_modified=False, scope='Allocation accounting and activity failure handling; no training or full-study admission.')
    atomic_json(OUT/'global-research-inventory-control-v2-result.json', report)
    print(json.dumps(report), flush=True)


if __name__ == '__main__': main()
