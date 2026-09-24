"""Select a registered matched trial for the frozen independent reader."""
import sys
import hu_action_integrated_fresh_review_20260925 as review

if __name__ == '__main__':
    assert len(sys.argv)==2 and sys.argv[1] in ('first','replication')
    review.PREFIX='action-integrated-fresh-pilot-v1' if sys.argv[1]=='first' else 'action-integrated-replication-v1'
    review.main()
