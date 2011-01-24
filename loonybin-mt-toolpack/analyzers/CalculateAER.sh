#!/usr/bin/env bash
set -e

export PERL5LIB=/afs/cs.cmu.edu/project/cmt-55/lti/Courses/731/homework/HW3/Lingua-AlignmentSet-1.1/blib/lib/

perl /afs/cs.cmu.edu/project/cmt-55/lti/Courses/731/homework/HW3/Lingua-AlignmentSet-1.1/bin/evaluate_alSet-1.1.pl 
    -sub AlignmentFile.dev \
    -subf giza \
    -ans hand-aligned/dev.engspa.naacl \
    -ansf naacl