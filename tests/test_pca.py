"""Tests for PCA dimensionality reduction and visualization."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ralph.data import clean_data, encode_features, load_data, map_major

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


# ── Unit tests ──────────────────────────────────────────────────────────


class TestReducePcaUnit:
    """Unit tests for reduce_pca with synthetic data."""

    def test_returns_2d_array_with_correct_shape(self):
        """reduce_pca should return (n_samples, 2) array."""
        from ralph.pca import reduce_pca

        df = _make_synthetic_df(n_samples=150, n_features=10)
        X = df.drop(columns=["target"])
        X_reduced, evr = reduce_pca(X)

        assert X_reduced.shape == (150, 2)

    def test_explained_variance_ratio_properties(self):
        """explained_variance_ratio should have length 2, positive, sum < 1."""
        from ralph.pca import reduce_pca

        df = _make_synthetic_df(n_samples=150, n_features=10)
        X = df.drop(columns=["target"])
        X_reduced, evr = reduce_pca(X)

        assert len(evr) == 2
        assert all(v > 0 for v in evr)
        assert evr.sum() < 1.0  # only 2 of 10 components


class TestPlotPcaScatterUnit:
    """Unit tests for plot_pca_scatter."""

    def test_creates_png_file(self, tmp_path):
        """plot_pca_scatter should create a PNG file at save_path."""
        from ralph.pca import plot_pca_scatter

        rng = np.random.default_rng(42)
        X_reduced = rng.standard_normal((100, 2))
        y = rng.choice([0, 1, 2], size=100, p=[0.1, 0.7, 0.2])

        save_path = tmp_path / "pca_scatter.png"
        plot_pca_scatter(X_reduced, y, save_path=str(save_path))

        assert save_path.exists(), "Scatter plot file was not created"

    def test_chart_has_sufficient_dpi(self, tmp_path):
        """Saved scatter plot should have DPI >= 150 for PPT quality."""
        from PIL import Image

        from ralph.pca import plot_pca_scatter

        rng = np.random.default_rng(42)
        X_reduced = rng.standard_normal((100, 2))
        y = rng.choice([0, 1, 2], size=100, p=[0.1, 0.7, 0.2])

        save_path = tmp_path / "pca_scatter_dpi.png"
        plot_pca_scatter(X_reduced, y, save_path=str(save_path))

        img = Image.open(save_path)
        dpi = img.info.get("dpi", (72, 72))
        assert dpi[0] >= 150, f"DPI too low: {dpi[0]}"


# ── Integration tests (require 数据.xlsx) ───────────────────────────────


def _prepare_real_data():
    """Run the full data pipeline: load → clean → map → encode."""
    return encode_features(map_major(clean_data(load_data(DATA_PATH))))


@requires_data
class TestReducePcaIntegration:
    """Integration tests for reduce_pca on real survey data."""

    def test_reduces_76_features_to_2d(self):
        """PCA on 76 features should produce (1781, 2) output."""
        from ralph.pca import reduce_pca

        df = _prepare_real_data()
        X = df.drop(columns=["target"])
        assert X.shape == (1781, 76)  # sanity check

        X_reduced, evr = reduce_pca(X)
        assert X_reduced.shape == (1781, 2)

    def test_explained_variance_positive(self):
        """Each component should explain positive variance."""
        from ralph.pca import reduce_pca

        df = _prepare_real_data()
        X = df.drop(columns=["target"])
        _, evr = reduce_pca(X)

        assert all(v > 0 for v in evr)
        assert evr.sum() < 1.0  # 2 of 76 components


@requires_data
class TestPlotPcaScatterIntegration:
    """Integration tests for plot_pca_scatter on real data."""

    def test_creates_valid_png_on_real_data(self, tmp_path):
        """Full pipeline: reduce real data → plot → save valid PNG."""
        from PIL import Image

        from ralph.pca import plot_pca_scatter, reduce_pca

        df = _prepare_real_data()
        X = df.drop(columns=["target"])
        y = df["target"]

        X_reduced, _ = reduce_pca(X)
        save_path = tmp_path / "pca_real.png"
        plot_pca_scatter(X_reduced, y, save_path=str(save_path))

        assert save_path.exists()
        img = Image.open(save_path)
        dpi = img.info.get("dpi", (72, 72))
        assert dpi[0] >= 150
