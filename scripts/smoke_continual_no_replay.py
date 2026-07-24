"""Check the no-replay resume guard without torch, images, or GPU access."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.advanced.continual_no_replay import (
    NO_REPLAY_RESUME_FIELDS,
    validate_no_replay_resume_config,
)


def fail(message):
    raise SystemExit(f"[continual-no-replay] FAIL: {message}")


def main():
    """Verify matching settings pass while a training change is rejected."""

    config = {field: f"value-{field}" for field in NO_REPLAY_RESUME_FIELDS}
    validate_no_replay_resume_config(config, config)

    changed_config = dict(config)
    changed_config["learning_rate"] = "changed"
    try:
        validate_no_replay_resume_config(config, changed_config)
    except ValueError as error:
        if "learning_rate" not in str(error):
            fail("mismatch error does not identify the changed field")
    else:
        fail("mismatched resume configuration was accepted")

    print("[continual-no-replay] PASS: resume configuration guard is consistent")


if __name__ == "__main__":
    main()
