"""Run the unchanged independent training reader against the registered repeat."""
import sys
import hu_root_retained_fresh_review_20260924 as review

if __name__ == '__main__':
    assert sys.argv[1:] == []
    review.PREFIX = 'root-retained-replication-resume-v1'
    review.main()
