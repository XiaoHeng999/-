"""Tests for main.py experiment orchestrator."""

import shutil
from pathlib import Path

import pytest

from main import main

DATA_PATH = Path(__file__).resolve().parent.parent / "数据.xlsx"

requires_data = pytest.mark.skipif(
    not DATA_PATH.exists(),
    reason="数据.xlsx not available (excluded from VCS)",
)


@requires_data
def test_main_runs():
    """main() should execute without raising an exception."""
    main()


@requires_data
def test_main_creates_results_dir(tmp_path, monkeypatch):
    """main() should create the results/ directory tree."""
    monkeypatch.chdir(tmp_path)
    shutil.copy2(DATA_PATH, tmp_path / "数据.xlsx")
    main()
    assert (tmp_path / "results").exists()
    assert (tmp_path / "results" / "model_comparison").exists()
