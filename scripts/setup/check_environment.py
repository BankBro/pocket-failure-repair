#!/usr/bin/env python3
"""Check local dependencies for the pocket-failure-repair project."""

from __future__ import annotations

import importlib.util
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class PythonModule:
    name: str
    import_name: str
    required: bool


MODULES = [
    PythonModule("numpy", "numpy", True),
    PythonModule("pandas", "pandas", True),
    PythonModule("yaml", "yaml", True),
    PythonModule("rdkit", "rdkit", True),
    PythonModule("Bio", "Bio", False),
    PythonModule("torch", "torch", False),
    PythonModule("torch_geometric", "torch_geometric", False),
    PythonModule("pytorch_lightning", "pytorch_lightning", False),
    PythonModule("vina", "vina", False),
    PythonModule("posebusters", "posebusters", False),
    PythonModule("plip", "plip", False),
    PythonModule("meeko", "meeko", False),
]

EXECUTABLES = [
    ("vina", False),
    ("obabel", False),
]


def module_version(import_name: str) -> str:
    module = __import__(import_name)
    return str(getattr(module, "__version__", "installed"))


def check_modules() -> int:
    failures = 0
    print("Python modules:")
    for module in MODULES:
        found = importlib.util.find_spec(module.import_name) is not None
        label = "required" if module.required else "optional"
        if found:
            try:
                version = module_version(module.import_name)
            except Exception as exc:  # pragma: no cover
                version = f"import failed: {exc}"
                found = False
        else:
            version = "missing"
        status = "OK" if found else ("FAIL" if module.required else "MISS")
        print(f"  [{status}] {module.name:<18} {label:<8} {version}")
        if module.required and not found:
            failures += 1
    return failures


def check_executables() -> None:
    print("\nExecutables:")
    for name, required in EXECUTABLES:
        path = shutil.which(name)
        label = "required" if required else "optional"
        status = "OK" if path else ("FAIL" if required else "MISS")
        print(f"  [{status}] {name:<18} {label:<8} {path or 'not found'}")


def check_torch_cuda() -> None:
    if importlib.util.find_spec("torch") is None:
        return
    import torch

    print("\nTorch:")
    print(f"  version: {torch.__version__}")
    print(f"  cuda available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  cuda device count: {torch.cuda.device_count()}")
        for idx in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(idx)
            total_gb = props.total_memory / 1024**3
            print(f"  cuda:{idx}: {props.name}, {total_gb:.1f} GiB")


def check_rdkit_smoke() -> int:
    if importlib.util.find_spec("rdkit") is None:
        print("\nRDKit smoke:")
        print("  skipped: rdkit is missing")
        return 0
    from rdkit import Chem

    mol = Chem.MolFromSmiles("CCO")
    ok = mol is not None and mol.GetNumAtoms() == 3
    print("\nRDKit smoke:")
    print(f"  MolFromSmiles('CCO'): {'OK' if ok else 'FAIL'}")
    return 0 if ok else 1


def main() -> int:
    print("pocket-failure-repair environment check")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Platform: {platform.platform()}")
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        commit = "unknown"
    print(f"Git commit: {commit}\n")

    failures = check_modules()
    check_executables()
    check_torch_cuda()
    failures += check_rdkit_smoke()

    print("\nSummary:")
    if failures:
        print(f"  FAIL: {failures} required check(s) failed.")
        return 1
    print("  OK: required checks passed. Optional tools may still be missing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
