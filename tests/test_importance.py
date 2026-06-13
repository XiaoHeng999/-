"""Tests for feature importance analysis: RF and Permutation Importance."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.data import clean_data, encode_features, load_data, map_major

DATA_PATH = Path(__file__).resolve().parent.parent / "数据.xlsx"

requires_data = pytest.mark.skipif(
    not DATA_PATH.exists(),
    reason="数据.xlsx not available (excluded from VCS)",
)


def _make_synthetic_df(n_samples=200, n_features=10, seed=42):
    """Create a synthetic feature matrix + target for unit testing."""
    rng = np.random.default_rng(seed)
    data = rng.standard_normal((n_samples, n_features))
    target = rng.choice([0, 1, 2], size=n_samples, p=[0.10, 0.70, 0.20])
    df = pd.DataFrame(data, columns=[f"feat_{i}" for i in range(n_features)])
    df["target"] = target
    return df


def _train_rf_pipeline(df):
    """Train a random forest pipeline on synthetic data for unit testing."""
    from src.model import build_pipelines, split_data

    X_train, X_test, y_train, y_test = split_data(df)
    pipelines = build_pipelines()
    rf_pipe = pipelines["随机森林"]
    rf_pipe.fit(X_train, y_train)
    feature_names = list(X_train.columns)
    return rf_pipe, X_test, y_test, feature_names


# ── Unit tests ──────────────────────────────────────────────────────────


class TestComputeRfImportanceUnit:
    """Unit tests for compute_rf_importance with synthetic data."""

    def test_returns_dataframe_with_correct_columns_and_shape(self):
        """compute_rf_importance should return DataFrame with feature/importance columns, top_n rows, sorted descending."""
        from src.importance import compute_rf_importance

        df = _make_synthetic_df(n_samples=200, n_features=10)
        rf_pipe, _, _, feature_names = _train_rf_pipeline(df)

        result = compute_rf_importance(rf_pipe, feature_names, top_n=5)

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["feature", "importance"]
        assert len(result) == 5
        # Sorted descending
        importances = result["importance"].values
        assert all(importances[i] >= importances[i + 1] for i in range(len(importances) - 1))


class TestPlotRfImportanceUnit:
    """Unit tests for plot_rf_importance."""

    def test_creates_png_file(self, tmp_path):
        """plot_rf_importance should create a PNG file at save_path."""
        from src.importance import plot_rf_importance

        importance_df = pd.DataFrame({
            "feature": [f"feat_{i}" for i in range(5)],
            "importance": [0.3, 0.25, 0.2, 0.15, 0.1],
        })
        save_path = tmp_path / "rf_importance.png"
        plot_rf_importance(importance_df, save_path=str(save_path))

        assert save_path.exists(), "RF importance chart file was not created"

    def test_chart_has_sufficient_dpi(self, tmp_path):
        """Saved chart should have DPI >= 150 for PPT quality."""
        from PIL import Image

        from src.importance import plot_rf_importance

        importance_df = pd.DataFrame({
            "feature": [f"feat_{i}" for i in range(5)],
            "importance": [0.3, 0.25, 0.2, 0.15, 0.1],
        })
        save_path = tmp_path / "rf_importance_dpi.png"
        plot_rf_importance(importance_df, save_path=str(save_path))

        img = Image.open(save_path)
        dpi = img.info.get("dpi", (72, 72))
        assert dpi[0] >= 150, f"DPI too low: {dpi[0]}"


class TestComputePermutationImportanceUnit:
    """Unit tests for compute_permutation_importance with synthetic data."""

    def test_returns_dataframe_with_correct_columns_and_shape(self):
        """compute_permutation_importance should return DataFrame sorted descending, top_n rows."""
        from src.importance import compute_permutation_importance

        df = _make_synthetic_df(n_samples=200, n_features=10)
        rf_pipe, X_test, y_test, feature_names = _train_rf_pipeline(df)

        result = compute_permutation_importance(
            rf_pipe, X_test, y_test, feature_names, top_n=5, random_state=42,
        )

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["feature", "importance"]
        assert len(result) == 5
        # Sorted descending
        importances = result["importance"].values
        assert all(importances[i] >= importances[i + 1] for i in range(len(importances) - 1))


class TestPlotPermutationImportanceUnit:
    """Unit tests for plot_permutation_importance."""

    def test_creates_png_file(self, tmp_path):
        """plot_permutation_importance should create a PNG file at save_path."""
        from src.importance import plot_permutation_importance

        importance_df = pd.DataFrame({
            "feature": [f"feat_{i}" for i in range(5)],
            "importance": [0.3, 0.25, 0.2, 0.15, 0.1],
        })
        save_path = tmp_path / "perm_importance.png"
        plot_permutation_importance(importance_df, save_path=str(save_path))

        assert save_path.exists(), "Permutation importance chart file was not created"

    def test_chart_has_sufficient_dpi(self, tmp_path):
        """Saved chart should have DPI >= 150 for PPT quality."""
        from PIL import Image

        from src.importance import plot_permutation_importance

        importance_df = pd.DataFrame({
            "feature": [f"feat_{i}" for i in range(5)],
            "importance": [0.3, 0.25, 0.2, 0.15, 0.1],
        })
        save_path = tmp_path / "perm_importance_dpi.png"
        plot_permutation_importance(importance_df, save_path=str(save_path))

        img = Image.open(save_path)
        dpi = img.info.get("dpi", (72, 72))
        assert dpi[0] >= 150, f"DPI too low: {dpi[0]}"


# ── Integration tests (require 数据.xlsx) ───────────────────────────────


def _prepare_real_data():
    """Run the full data pipeline: load → clean → map → encode."""
    return encode_features(map_major(clean_data(load_data(DATA_PATH))))


@requires_data
class TestRfImportanceIntegration:
    """Integration tests for RF feature importance on real survey data."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        """Train RF pipeline on real data."""
        from src.model import build_pipelines, split_data

        df = _prepare_real_data()
        X_train, X_test, y_train, y_test = split_data(df)
        pipelines = build_pipelines()
        self.rf_pipe = pipelines["随机森林"]
        self.rf_pipe.fit(X_train, y_train)
        self.feature_names = list(X_train.columns)
        self.X_test = X_test
        self.y_test = y_test

    def test_rf_importance_top_15_on_real_data(self):
        """RF importance on 76 features should return exactly 15 rows."""
        from src.importance import compute_rf_importance

        result = compute_rf_importance(self.rf_pipe, self.feature_names, top_n=15)

        assert len(result) == 15
        assert list(result.columns) == ["feature", "importance"]
        # All importance values should be positive
        assert all(result["importance"] > 0)

    def test_rf_importance_chart_on_real_data(self, tmp_path):
        """Full pipeline on real data should produce valid PNG with DPI >= 150."""
        from PIL import Image

        from src.importance import compute_rf_importance, plot_rf_importance

        result = compute_rf_importance(self.rf_pipe, self.feature_names, top_n=15)
        save_path = tmp_path / "rf_real.png"
        plot_rf_importance(result, save_path=str(save_path))

        assert save_path.exists()
        img = Image.open(save_path)
        dpi = img.info.get("dpi", (72, 72))
        assert dpi[0] >= 150

    def test_permutation_importance_top_15_on_real_data(self):
        """Permutation importance on real data should return exactly 15 rows."""
        from src.importance import compute_permutation_importance

        result = compute_permutation_importance(
            self.rf_pipe, self.X_test, self.y_test,
            self.feature_names, top_n=15, random_state=42,
        )

        assert len(result) == 15
        assert list(result.columns) == ["feature", "importance"]

    def test_permutation_importance_chart_on_real_data(self, tmp_path):
        """Permutation importance chart on real data should produce valid PNG."""
        from PIL import Image

        from src.importance import compute_permutation_importance, plot_permutation_importance

        result = compute_permutation_importance(
            self.rf_pipe, self.X_test, self.y_test,
            self.feature_names, top_n=15, random_state=42,
        )
        save_path = tmp_path / "perm_real.png"
        plot_permutation_importance(result, save_path=str(save_path))

        assert save_path.exists()
        img = Image.open(save_path)
        dpi = img.info.get("dpi", (72, 72))
        assert dpi[0] >= 150
