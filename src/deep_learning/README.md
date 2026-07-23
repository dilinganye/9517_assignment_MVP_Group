# Deep Learning

CNN models, training loops, checkpoints, and deep learning experiment code belong here.

New scratch-CNN runs save both `best_checkpoint.pt` for final evaluation and
`last_checkpoint.pt` for interruption recovery. `--resume` restores only the
latest checkpoint and rejects training-defining configuration mismatches.
