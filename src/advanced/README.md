# Advanced Methods

Advanced research directions such as Grad-CAM, robustness, or other extensions belong here.

`continual_learning.py` defines the deterministic 100-class, 10-task partition
and the dependency-light manifest filtering used by the scratch
continual-learning study. It does not train a model or implement replay; those
are separate follow-up steps.

`continual_metrics.py` defines the task-by-task accuracy matrix contract used
after every completed task: current-task, old-task, seen-task accuracy, and
average forgetting. The next step is sequential no-replay training that fills
this matrix; replay remains a separate comparison.
