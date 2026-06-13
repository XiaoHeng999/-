"""Tests for experiment functions: model comparison, visualizations."""

import numpy as np
import pandas as pd

from src.model import build_pipelines, split_data, train_and_evaluate


def _make_synthetic_df(n_samples=200, n_features=10, seed=42):
    """Create a synthetic feature matrix + target for unit testing."""
    rng = np.random.default_rng(seed)
    data = rng.standard_normal((n_samples, n_features))
    target = rng.choice([0, 1, 2], size=n_samples, p=[0.10, 0.70, 0.20])
    df = pd.DataFrame(data, columns=[f"feat_{i}" for i in range(n_features)])
    df["target"] = target
    return df


def _train_synthetic():
    """Train models on synthetic data and return results + pipelines."""
    df = _make_synthetic_df()
    X_train, X_test, y_train, y_test = split_data(df)
    pipelines = build_pipelines()
    results = train_and_evaluate(pipelines, X_train, y_train, X_test, y_test, cv=3)
    return results, pipelines


# ── Visualization unit tests ────────────────────────────────────────────


class TestPlotPerClassMetrics:
    """Unit tests for _plot_per_class_metrics."""

    def test_creates_png(self, tmp_path):
        """_plot_per_class_metrics should create a PNG file."""
        from src.experiments import _plot_per_class_metrics

        results, _ = _train_synthetic()
        save_path = tmp_path / "per_class.png"
        _plot_per_class_metrics(results, save_path)
        assert save_path.exists()

    def test_sufficient_dpi(self, tmp_path):
        """Saved chart should have DPI >= 150."""
        from PIL import Image
        from src.experiments import _plot_per_class_metrics

        results, _ = _train_synthetic()
        save_path = tmp_path / "per_class_dpi.png"
        _plot_per_class_metrics(results, save_path)
        img = Image.open(save_path)
        assert img.info.get("dpi", (72, 72))[0] >= 150


class TestPlotConfusionMatrix:
    """Unit tests for _plot_confusion_matrix."""

    def test_creates_png(self, tmp_path):
        """_plot_confusion_matrix should create a PNG file."""
        from src.experiments import _plot_confusion_matrix

        cm = np.array([[50, 10, 5], [8, 120, 12], [3, 15, 40]])
        save_path = tmp_path / "cm.png"
        _plot_confusion_matrix(cm, "TestModel", ["低频", "中频", "高频"], save_path)
        assert save_path.exists()

    def test_sufficient_dpi(self, tmp_path):
        """Saved chart should have DPI >= 150."""
        from PIL import Image
        from src.experiments import _plot_confusion_matrix

        cm = np.array([[50, 10, 5], [8, 120, 12], [3, 15, 40]])
        save_path = tmp_path / "cm_dpi.png"
        _plot_confusion_matrix(cm, "TestModel", ["低频", "中频", "高频"], save_path)
        img = Image.open(save_path)
        assert img.info.get("dpi", (72, 72))[0] >= 150


class TestPlotCvBoxplot:
    """Unit tests for _plot_cv_boxplot."""

    def test_creates_png(self, tmp_path):
        """_plot_cv_boxplot should create a PNG file."""
        from src.experiments import _plot_cv_boxplot

        results, _ = _train_synthetic()
        save_path = tmp_path / "cv_box.png"
        _plot_cv_boxplot(results, save_path)
        assert save_path.exists()

    def test_sufficient_dpi(self, tmp_path):
        """Saved chart should have DPI >= 150."""
        from PIL import Image
        from src.experiments import _plot_cv_boxplot

        results, _ = _train_synthetic()
        save_path = tmp_path / "cv_box_dpi.png"
        _plot_cv_boxplot(results, save_path)
        img = Image.open(save_path)
        assert img.info.get("dpi", (72, 72))[0] >= 150


class TestMetricsSummaryCsv:
    """Unit tests for metrics_summary.csv output format."""

    def test_csv_has_all_models(self, tmp_path):
        """metrics_summary.csv should have one row per model."""
        from src.experiments import run_model_comparison
        from src.utils import ensure_results_dirs

        df = _make_synthetic_df(n_samples=200, n_features=5)
        X_train, X_test, y_train, y_test = split_data(df)
        feature_names = list(X_train.columns)
        results_root = ensure_results_dirs(tmp_path)

        results, _ = run_model_comparison(
            X_train, X_test, y_train, y_test, feature_names,
            results_root=results_root,
        )

        csv_path = results_root / "model_comparison" / "metrics_summary.csv"
        assert csv_path.exists()
        saved = pd.read_csv(csv_path)
        assert len(saved) == 6  # 6 models
        assert "model" in saved.columns


# ── Hyperparameter tuning tests ─────────────────────────────────────────


class TestPlotTuningHeatmap:
    """Unit tests for _plot_tuning_heatmap."""

    def test_creates_png(self, tmp_path):
        """_plot_tuning_heatmap should create a PNG file."""
        from src.experiments import _plot_tuning_heatmap

        cv_df = pd.DataFrame({
            "param_clf__C": [0.1, 0.1, 1, 1],
            "param_clf__gamma": ["scale", "auto", "scale", "auto"],
            "mean_test_score": [0.5, 0.55, 0.6, 0.65],
        })
        save_path = tmp_path / "heatmap.png"
        _plot_tuning_heatmap(cv_df, "C", "gamma", save_path)
        assert save_path.exists()


class TestPlotTuningLine:
    """Unit tests for _plot_tuning_line."""

    def test_creates_png(self, tmp_path):
        """_plot_tuning_line should create a PNG file."""
        from src.experiments import _plot_tuning_line

        cv_df = pd.DataFrame({
            "param_clf__n_estimators": [100, 100, 200, 200],
            "mean_test_score": [0.5, 0.52, 0.6, 0.58],
        })
        save_path = tmp_path / "line.png"
        _plot_tuning_line(cv_df, "n_estimators", save_path)
        assert save_path.exists()


class TestConsensusRanking:
    """Unit tests for _compute_consensus_ranking."""

    def test_returns_top_15(self):
        """Consensus ranking should return 15 features."""
        from src.experiments import _compute_consensus_ranking

        rf_df = pd.DataFrame({
            "feature": [f"rf_feat_{i}" for i in range(15)],
            "importance": np.linspace(1, 0.1, 15),
        })
        perm_df = pd.DataFrame({
            "feature": [f"perm_feat_{i}" for i in range(15)],
            "importance": np.linspace(1, 0.1, 15),
        })
        shap_df = pd.DataFrame({
            "feature": [f"shap_feat_{i}" for i in range(15)],
            "importance": np.linspace(1, 0.1, 15),
        })

        result = _compute_consensus_ranking(rf_df, perm_df, shap_df)
        assert len(result) == 15
        assert "feature" in result.columns
        assert "mean_rank" in result.columns

    def test_shared_feature_ranks_higher(self):
        """A feature in all 3 Top-15 should rank higher than one in only 1."""
        from src.experiments import _compute_consensus_ranking

        shared = "shared_feature"
        rf_df = pd.DataFrame({
            "feature": [shared] + [f"rf_only_{i}" for i in range(14)],
            "importance": np.linspace(1, 0.1, 15),
        })
        perm_df = pd.DataFrame({
            "feature": [shared] + [f"perm_only_{i}" for i in range(14)],
            "importance": np.linspace(1, 0.1, 15),
        })
        shap_df = pd.DataFrame({
            "feature": [shared] + [f"shap_only_{i}" for i in range(14)],
            "importance": np.linspace(1, 0.1, 15),
        })

        result = _compute_consensus_ranking(rf_df, perm_df, shap_df)
        top_feature = result.iloc[0]["feature"]
        assert top_feature == shared

    def test_penalty_rank_for_missing(self):
        """Features not in a method's Top-15 should get penalty rank 16."""
        from src.experiments import _compute_consensus_ranking

        rf_df = pd.DataFrame({"feature": ["a", "b"], "importance": [0.5, 0.3]})
        perm_df = pd.DataFrame({"feature": ["a", "c"], "importance": [0.5, 0.3]})
        shap_df = pd.DataFrame({"feature": ["a", "d"], "importance": [0.5, 0.3]})

        result = _compute_consensus_ranking(rf_df, perm_df, shap_df)
        # "b" is only in rf, so perm_rank and shap_rank should be 16
        row_b = result[result["feature"] == "b"].iloc[0]
        assert row_b["perm_rank"] == 16
        assert row_b["shap_rank"] == 16


class TestPlotCrossMethodComparison:
    """Unit tests for _plot_cross_method_comparison."""

    def test_creates_png(self, tmp_path):
        """_plot_cross_method_comparison should create a PNG file."""
        from src.experiments import _plot_cross_method_comparison

        rf_df = pd.DataFrame({
            "feature": [f"f{i}" for i in range(5)],
            "importance": np.linspace(1, 0.2, 5),
        })
        perm_df = pd.DataFrame({
            "feature": [f"f{i}" for i in range(5)],
            "importance": np.linspace(0.9, 0.1, 5),
        })
        shap_df = pd.DataFrame({
            "feature": [f"f{i}" for i in range(5)],
            "importance": np.linspace(0.8, 0.05, 5),
        })
        save_path = tmp_path / "cross.png"
        _plot_cross_method_comparison(rf_df, perm_df, shap_df, save_path)
        assert save_path.exists()
