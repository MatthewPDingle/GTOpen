"""Resume the frozen experiment with a narrowly checked JSON metadata adapter."""
import argparse
import copy
import math
import paired_continuation_expansion as expansion


def metadata_adapter(original, corrections):
    def validate(row, job, manifest):
        if row['job'] != job:
            actual=row['job']['inclusion_probability'];expected=job['inclusion_probability']
            assert math.isfinite(actual) and 0<expected<=1
            assert abs(actual-expected)<=2*math.ulp(expected), (actual,expected)
            normalized=copy.deepcopy(row)
            normalized['job']['inclusion_probability']=expected
            assert normalized['job']==job,'Mismatch beyond JSON float roundtrip'
            corrections[job['id']]=dict(observed=actual,expected=expected,absolute_difference=abs(actual-expected))
            row=normalized
        return original(row,job,manifest)
    return validate


def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['run','screen']);args=parser.parse_args()
    s=expansion.pilot;corrections={}
    freeze=s.read(expansion.OUT/'runner-freeze.json')
    for p,h in freeze['inputs'].items():assert s.pilot.sha(s.ROOT/p)==h,p
    s.native.previous.old.validate=metadata_adapter(s.native.previous.old.validate,corrections)
    try:
        if args.command=='run':expansion.run()
        else:
            import fit_paired_expansion
            fit_paired_expansion.screen()
    finally:
        s.write(expansion.OUT/(args.command+'-metadata-roundtrips.json'),dict(corrections=corrections,
            note='Only inclusion-probability JSON serialization within two ULP is normalized for metadata equality; original label files and all quality gates are unchanged.'))


if __name__=='__main__':main()
