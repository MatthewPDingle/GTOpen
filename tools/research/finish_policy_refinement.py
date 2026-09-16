"""Finish N01 reporting after a display-metadata mismatch; no fitting or solves."""
import audit_policy_refinement as auditor
import continuation_refinement_report as report

study=report.study


def main():
    auditor.audit()
    assert study.read(study.OUT/'reference-audit.json')['complete']
    original_contexts=study.contexts
    def labelled(partition):
        cases=original_contexts(partition)
        for context in cases:
            case=context['case']
            if 'positions' not in case:
                case['positions']=[case['oop_position'],case['ip_position']]
        return cases
    study.contexts=labelled
    try:
        result=study.compare('evaluation')
    finally:
        study.contexts=original_contexts
    study.night.dump(study.OUT/'report-recovery.json',dict(
        recorded_at=study.night.now(),reason="Evaluation fixtures use oop_position/ip_position rather than positions.",
        correction='Populate positions in analysis memory for hand labels; call the original frozen comparison unchanged.',
        script_sha256=study.pilot.sha(study.ROOT/'tools/research/finish_policy_refinement.py'),
        candidate_sha256=study.pilot.sha(study.OUT/'candidate.json'),
        retrained=False,references_changed=False,production_enabled=False))
    report.report()
    study.night.dump(study.OUT/'status.json',dict(stage='complete',updated=study.night.now(),
        accuracy_screen_passed=result['all_screen_pass'],production_enabled=False,
        reporting_recovery='report-recovery.json'))


if __name__=='__main__':main()
