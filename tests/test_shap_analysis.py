"""Tests for SHAP deep analysis module."""

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
    return rf_pipe, X_train, X_test, y_test, feature_names


# ── Unit tests ──────────────────────────────────────────────────────────


class TestComputeShapValuesUnit:
    """Unit tests for compute_shap_values with synthetic data."""

    def test_returns_shap_array_with_correct_shape(self):
        """compute_shap_values should return (n_classes, n_samples, n_features) SHAP array."""
        from src.shap_analysis import compute_shap_values

        df = _make_synthetic_df()
        rf_pipe, X_train, X_test, y_test, feature_names = _train_rf_pipeline(df)

        shap_values, X_sample = compute_shap_values(
            rf_pipe, X_train, X_test, feature_names,
        )

        n_classes = 3
        n_samples = X_sample.shape[0]
        n_features = X_sample.shape[1]
        assert shap_values.shape == (n_classes, n_samples, n_features)
        assert isinstance(X_sample, pd.DataFrame)


class TestPlotShapBarUnit:
    """Unit tests for plot_shap_bar."""

    def test_creates_png_file(self, tmp_path):
        """plot_shap_bar should create a PNG file at save_path."""
        from src.shap_analysis import plot_shap_bar

        rng = np.random.default_rng(42)
        n_samples, n_features = 50, 10
        shap_values = rng.standard_normal((3, n_samples, n_features))
        X_sample = pd.DataFrame(
            rng.standard_normal((n_samples, n_features)),
            columns=[f"feat_{i}" for i in range(n_features)],
        )

        save_path = tmp_path / "shap_bar.png"
        plot_shap_bar(shap_values, X_sample, class_idx=2, top_n=5, save_path=str(save_path))

        assert save_path.exists(), "SHAP bar chart file was not created"

    def test_chart_has_sufficient_dpi(self, tmp_path):
        """Saved chart should have DPI >= 150 for PPT quality."""
        from PIL import Image

        from src.shap_analysis import plot_shap_bar

        rng = np.random.default_rng(42)
        n_samples, n_features = 50, 10
        shap_values = rng.standard_normal((3, n_samples, n_features))
        X_sample = pd.DataFrame(
            rng.standard_normal((n_samples, n_features)),
            columns=[f"feat_{i}" for i in range(n_features)],
        )

        save_path = tmp_path / "shap_bar_dpi.png"
        plot_shap_bar(shap_values, X_sample, class_idx=2, top_n=5, save_path=str(save_path))

        img = Image.open(save_path)
        dpi = img.info.get("dpi", (72, 72))
        assert dpi[0] >= 150, f"DPI too low: {dpi[0]}"


class TestPlotShapSummaryUnit:
    """Unit tests for plot_shap_summary."""

    def test_creates_png_file(self, tmp_path):
        """plot_shap_summary should create a PNG file at save_path."""
        from src.shap_analysis import plot_shap_summary

        rng = np.random.default_rng(42)
        n_samples, n_features = 50, 10
        shap_values = rng.standard_normal((3, n_samples, n_features))
        X_sample = pd.DataFrame(
            rng.standard_normal((n_samples, n_features)),
            columns=[f"feat_{i}" for i in range(n_features)],
        )

        save_path = tmp_path / "shap_summary.png"
        plot_shap_summary(shap_values, X_sample, save_path=str(save_path))

        assert save_path.exists(), "SHAP summary chart file was not created"

    def test_chart_has_sufficient_dpi(self, tmp_path):
        """Saved chart should have DPI >= 150 for PPT quality."""
        from PIL import Image

        from src.shap_analysis import plot_shap_summary

        rng = np.random.default_rng(42)
        n_samples, n_features = 50, 10
        shap_values = rng.standard_normal((3, n_samples, n_features))
        X_sample = pd.DataFrame(
            rng.standard_normal((n_samples, n_features)),
            columns=[f"feat_{i}" for i in range(n_features)],
        )

        save_path = tmp_path / "shap_summary_dpi.png"
        plot_shap_summary(shap_values, X_sample, save_path=str(save_path))

        img = Image.open(save_path)
        dpi = img.info.get("dpi", (72, 72))
        assert dpi[0] >= 150, f"DPI too low: {dpi[0]}"


class TestPlotShapBeeswarmUnit:
    """Unit tests for plot_shap_beeswarm."""

    def test_creates_png_file(self, tmp_path):
        """plot_shap_beeswarm should create a PNG file at save_path."""
        from src.shap_analysis import plot_shap_beeswarm

        rng = np.random.default_rng(42)
        n_samples, n_features = 50, 10
        shap_values = rng.standard_normal((3, n_samples, n_features))
        X_sample = pd.DataFrame(
            rng.standard_normal((n_samples, n_features)),
            columns=[f"feat_{i}" for i in range(n_features)],
        )

        save_path = tmp_path / "shap_beeswarm.png"
        plot_shap_beeswarm(shap_values, X_sample, class_idx=2, save_path=str(save_path))

        assert save_path.exists(), "SHAP beeswarm chart file was not created"

    def test_chart_has_sufficient_dpi(self, tmp_path):
        """Saved chart should have DPI >= 150 for PPT quality."""
        from PIL import Image

        from src.shap_analysis import plot_shap_beeswarm

        rng = np.random.default_rng(42)
        n_samples, n_features = 50, 10
        shap_values = rng.standard_normal((3, n_samples, n_features))
        X_sample = pd.DataFrame(
            rng.standard_normal((n_samples, n_features)),
            columns=[f"feat_{i}" for i in range(n_features)],
        )

        save_path = tmp_path / "shap_beeswarm_dpi.png"
        plot_shap_beeswarm(shap_values, X_sample, class_idx=2, save_path=str(save_path))

        img = Image.open(save_path)
        dpi = img.info.get("dpi", (72, 72))
        assert dpi[0] >= 150, f"DPI too low: {dpi[0]}"


# ── Integration tests (require 数据.xlsx) ───────────────────────────────


def _prepare_real_data():
    """Run the full data pipeline: load → clean → map → encode."""
    return encode_features(map_major(clean_data(load_data(DATA_PATH))))


@requires_data
class TestShapAnalysisIntegration:
    """Integration tests for SHAP analysis on real survey data."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        """Train RF pipeline on real data and compute SHAP values."""
        from src.model import build_pipelines, split_data
        from src.shap_analysis import compute_shap_values

        df = _prepare_real_data()
        X_train, X_test, y_train, y_test = split_data(df)
        pipelines = build_pipelines()
        self.rf_pipe = pipelines["随机森林"]
        self.rf_pipe.fit(X_train, y_train)
        self.feature_names = list(X_train.columns)
        self.X_test = X_test
        self.y_test = y_test

        self.shap_values, self.X_sample = compute_shap_values(
            self.rf_pipe, X_train, X_test, self.feature_names,
        )

    def test_shap_values_shape_on_real_data(self):
        """SHAP values on 76 features × 3 classes should have correct shape."""
        n_classes, n_samples, n_features = self.shap_values.shape
        assert n_classes == 3
        assert n_samples == self.X_sample.shape[0]
        assert n_features == 76

    def test_shap_bar_chart_on_real_data(self, tmp_path):
        """SHAP bar chart on real data should produce valid PNG with DPI ≥ 150."""
        from PIL import Image

        from src.shap_analysis import plot_shap_bar

        save_path = tmp_path / "shap_bar_real.png"
        plot_shap_bar(self.shap_values, self.X_sample, class_idx=2, top_n=15, save_path=str(save_path))

        assert save_path.exists()
        img = Image.open(save_path)
        dpi = img.info.get("dpi", (72, 72))
        assert dpi[0] >= 150

    def test_shap_summary_chart_on_real_data(self, tmp_path):
        """SHAP summary chart on real data should produce valid PNG with DPI ≥ 150."""
        from PIL import Image

        from src.shap_analysis import plot_shap_summary

        save_path = tmp_path / "shap_summary_real.png"
        plot_shap_summary(self.shap_values, self.X_sample, save_path=str(save_path))

        assert save_path.exists()
        img = Image.open(save_path)
        dpi = img.info.get("dpi", (72, 72))
        assert dpi[0] >= 150

    def test_shap_beeswarm_chart_on_real_data(self, tmp_path):
        """SHAP beeswarm chart on real data should produce valid PNG with DPI ≥ 150."""
        from PIL import Image

        from src.shap_analysis import plot_shap_beeswarm

        save_path = tmp_path / "shap_beeswarm_real.png"
        plot_shap_beeswarm(self.shap_values, self.X_sample, class_idx=2, save_path=str(save_path))

        assert save_path.exists()
        img = Image.open(save_path)
        dpi = img.info.get("dpi", (72, 72))
        assert dpi[0] >= 150
