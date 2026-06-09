#!/usr/bin/env python3
from __future__ import annotations

import os
import random
import runpy
import sys
from pathlib import Path


def main() -> int:
    seed = int(os.environ.get("PFR_DIFFSBDD_SEED", "0"))
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    try:
        import numpy as np

        np.random.seed(seed)
    except Exception:
        pass
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except Exception:
        pass
    script = sys.argv[1]
    script_path = Path(script).resolve()
    for candidate in [str(Path.cwd()), str(script_path.parent)]:
        if candidate not in sys.path:
            sys.path.insert(0, candidate)
    sys.argv = sys.argv[1:]
    runpy.run_path(str(script_path), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
