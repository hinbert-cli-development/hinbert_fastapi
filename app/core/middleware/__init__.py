"""HTTP middleware and exception handling components."""

import os
from pathlib import Path


def generate_init_files(project_path):
    for root, dirs, files in os.walk(project_path / "app"):
        existing_modules = [f[:-3] for f in files if f.endswith(".py") and f != "__init__.py"]
        init_path = Path(root) / "__init__.py"
        if existing_modules:
            init_path.write_text("\n".join([f"from . import {m}" for m in existing_modules]))
        else:
            init_path.touch()
