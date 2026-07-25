# Deep Learning

CNN models, training loops, checkpoints, and deep learning experiment code belong here.

New scratch-CNN runs save both `best_checkpoint.pt` for final evaluation and
`last_checkpoint.pt` for interruption recovery. `--resume` restores only the
latest checkpoint and rejects training-defining configuration mismatches.

`Task_D_Colab_Execution.ipynb` documents the Colab execution workflow for the
scratch baseline, augmentation comparison, held-out scratch evaluation, and
the validation-only continual no-replay and replay baselines. Generated Drive
artifacts remain local and are not committed.
