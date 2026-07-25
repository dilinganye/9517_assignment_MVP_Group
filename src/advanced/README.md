# Advanced Methods

Advanced research directions such as Grad-CAM, robustness, or other extensions belong here.

`continual_learning.py` defines the deterministic 100-class, 10-task partition
and the dependency-light manifest filtering used by the scratch
continual-learning study. It does not train a model or implement replay; those
are implemented by the sequential training scripts.

`continual_metrics.py` defines the task-by-task accuracy matrix contract used
after every completed task: current-task, old-task, seen-task accuracy, and
average forgetting. The same contract is used for validation comparisons and
for fixed held-out test evaluation.

`continual_no_replay.py` guards task-boundary resume settings for the
sequential no-replay baseline. Its CUDA entry point is
`scripts/train_continual_no_replay.py`; it trains on the current task only and
writes task-boundary validation or explicitly requested held-out test matrix
artifacts after each task.

`continual_replay.py` provides deterministic class-balanced memory selection,
inverse-frequency sampling weights, and replay-specific resume guards.
`scripts/train_continual_replay.py` trains on the current task plus `M` stored
examples per old class, then saves the same task-boundary metrics together
with memory manifests and summaries.
