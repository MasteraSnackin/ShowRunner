from __future__ import annotations

import atexit
import os
import shutil
import tempfile
from pathlib import Path


_TEMP_DIR = Path(tempfile.mkdtemp(prefix="showrunner-pytest-"))
_TEMP_DB = _TEMP_DIR / "test-suite.db"

os.environ["DATABASE_URL"] = f"sqlite:///{_TEMP_DB}"
os.environ.setdefault("LUFFA_API_BASE_URL", "https://dummy.luffa.api")
os.environ.setdefault("ENDLESS_API_BASE_URL", "https://dummy.endless.api")
os.environ.setdefault("CIVIC_API_BASE_URL", "https://dummy.civic.api")
os.environ.setdefault("LLM_API_BASE_URL", "https://dummy.llm.api")
os.environ.setdefault("OPENAI_API_KEY", "dummy-openai-key")


@atexit.register
def _cleanup_temp_artifacts() -> None:
    shutil.rmtree(_TEMP_DIR, ignore_errors=True)
