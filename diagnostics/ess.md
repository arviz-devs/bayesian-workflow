# Effective sample size (ESS)
This document is the single source of truth for the explanations
shown in all the notebooks. They get pulled in via the
include directive to ensure they are always all in sync.
This approach allows us to code in jupyter notebooks and
potentially host long running notebooks for sampling and
the like without having to rerun them every time.


intro-start

Basic explanation of the effective sample size goes here.
i.e. we recommend having 100 ess (bulk and tail) per chain
and a minimum of 4 chains.
However, you should check with `helper_function_x` that you have
already achieved the desired precision in case you need some
more samples.

intro-end

tail-note-start

Here there is a note about how bulk and tail ess differ

tail-note-end

text we add here is excluded from the render, should we use checkpoints as separators instead?

conclusion-start

ess is a very important diagnostic, you should always use it on your posterior samples
before doing any analysis with them

conclusion-end
