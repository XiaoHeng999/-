"""Tests for utility functions: directory creation, CSV export, printing."""

import pandas as pd

from src.utils import ensure_results_dirs, print_experiment_header, save_metrics_csv


class TestEnsureResultsDirs:
    """Unit tests for ensure_results_dirs using tmp_path."""

    def test_creates_all_directories(self, tmp_path):
        """ensure_results_dirs should create the full directory tree."""
        results_root = ensure_results_dirs(tmp_path)

        assert results_root.exists()
        assert (tmp_path / "results" / "model_comparison").exists()
        assert (tmp_path / "results" / "model_comparison" / "confusion_matrices").exists()
        assert (tmp_path / "results" / "hyperparameter_tuning").exists()
        assert (tmp_path / "results" / "hyperparameter_tuning" / "random_forest").exists()
        assert (tmp_path / "results" / "hyperparameter_tuning" / "svm").exists()
        assert (tmp_path / "results" / "hyperparameter_tuning" / "knn").exists()
        assert (tmp_path / "results" / "hyperparameter_tuning" / "decision_tree").exists()
        assert (tmp_path / "results" / "factor_analysis").exists()
        assert (tmp_path / "results" / "pca").exists()

    def test_returns_results_path(self, tmp_path):
        """Return value should be the results/ directory Path."""
        results_root = ensure_results_dirs(tmp_path)
        assert results_root == tmp_path / "results"

    def test_idempotent(self, tmp_path):
        """Calling twice should not raise an error."""
        ensure_results_dirs(tmp_path)
        ensure_results_dirs(tmp_path)
        assert (tmp_path / "results").exists()


class TestSaveMetricsCsv:
    """Unit tests for save_metrics_csv."""

    def test_creates_csv_file(self, tmp_path):
        """save_metrics_csv should create a CSV file at the specified path."""
        metrics = {
            "Model A": {"f1": 0.85, "accuracy": 0.90},
            "Model B": {"f1": 0.78, "accuracy": 0.85},
        }
        path = tmp_path / "metrics.csv"
        save_metrics_csv(metrics, path)

        assert path.exists()

    def test_csv_content_correct(self, tmp_path):
        """CSV should have one row per model with correct columns."""
        metrics = {
            "Model A": {"f1": 0.85, "accuracy": 0.90},
            "Model B": {"f1": 0.78, "accuracy": 0.85},
        }
        path = tmp_path / "metrics.csv"
        save_metrics_csv(metrics, path)

        df = pd.read_csv(path)
        assert len(df) == 2
        assert "model" in df.columns
        assert set(df["model"]) == {"Model A", "Model B"}
        assert "f1" in df.columns
        assert "accuracy" in df.columns

    def test_list_values_flattened(self, tmp_path):
        """List values should be flattened to semicolon-joined strings."""
        metrics = {
            "Model A": {"per_class_f1": [0.5, 0.6, 0.7]},
        }
        path = tmp_path / "metrics.csv"
        save_metrics_csv(metrics, path)

        df = pd.read_csv(path)
        assert df.iloc[0]["per_class_f1"] == "0.5;0.6;0.7"


class TestPrintExperimentHeader:
    """Unit tests for print_experiment_header."""

    def test_does_not_raise(self, capsys):
        """print_experiment_header should not raise an exception."""
        print_experiment_header("测试实验")
        captured = capsys.readouterr()
        assert "测试实验" in captured.out

    def test_output_contains_separator(self, capsys):
        """Output should contain separator lines."""
        print_experiment_header("Test")
        captured = capsys.readouterr()
        assert "=" * 60 in captured.out
