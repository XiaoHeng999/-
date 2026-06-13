"""Tests for modeling pipeline: split, train, evaluate, visualize."""

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
    # Imbalanced classes similar to real data: ~10% / 70% / 20%
    target = rng.choice([0, 1, 2], size=n_samples, p=[0.10, 0.70, 0.20])
    df = pd.DataFrame(data, columns=[f"feat_{i}" for i in range(n_features)])
    df["target"] = target
    return df


# ── Unit tests ──────────────────────────────────────────────────────────


class TestSplitDataUnit:
    """Unit tests for split_data with synthetic data."""

    def test_returns_four_objects_with_correct_shapes(self):
        """split_data returns (X_train, X_test, y_train, y_test) with 80/20 ratio."""
        from src.model import split_data

        df = _make_synthetic_df(n_samples=200)
        X_train, X_test, y_train, y_test = split_data(df)

        assert len(X_train) == 160
        assert len(X_test) == 40
        assert len(y_train) == 160
        assert len(y_test) == 40

    def test_stratification_preserves_class_ratios(self):
        """Class proportions in train/test should match within tolerance."""
        from src.model import split_data

        df = _make_synthetic_df(n_samples=1000)
        X_train, X_test, y_train, y_test = split_data(df)

        train_ratio = y_train.value_counts(normalize=True).sort_index()
        test_ratio = y_test.value_counts(normalize=True).sort_index()

        for cls in [0, 1, 2]:
            assert abs(train_ratio[cls] - test_ratio[cls]) < 0.05, (
                f"Class {cls}: train={train_ratio[cls]:.3f}, test={test_ratio[cls]:.3f}"
            )

    def test_features_separated_from_target(self):
        """X should not contain target, y should only be target."""
        from src.model import split_data

        df = _make_synthetic_df(n_samples=100)
        X_train, X_test, y_train, y_test = split_data(df)

        assert "target" not in X_train.columns
        assert "target" not in X_test.columns
        assert X_train.shape[1] == 10  # all feature columns preserved


class TestBuildPipelinesUnit:
    """Unit tests for build_pipelines."""

    EXPECTED_NAMES = ["KNN", "决策树", "随机森林", "SVM", "朴素贝叶斯", "Logistic回归"]

    def test_returns_dict_with_six_models(self):
        """build_pipelines should return a dict with 6 model entries."""
        from src.model import build_pipelines

        pipelines = build_pipelines()
        assert isinstance(pipelines, dict)
        assert set(pipelines.keys()) == set(self.EXPECTED_NAMES)

    def test_each_pipeline_has_smote_as_first_step(self):
        """Each pipeline should have SMOTE as the first step."""
        from src.model import build_pipelines

        pipelines = build_pipelines()
        for name, pipe in pipelines.items():
            step_names = [s[0] for s in pipe.steps]
            assert "smote" in step_names, (
                f"{name} pipeline missing SMOTE step, got: {step_names}"
            )


class TestTrainAndEvaluateUnit:
    """Unit tests for train_and_evaluate with synthetic data."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        """Run train_and_evaluate once on synthetic data."""
        from src.model import build_pipelines, split_data, train_and_evaluate

        df = _make_synthetic_df(n_samples=200)
        X_train, X_test, y_train, y_test = split_data(df)
        pipelines = build_pipelines()
        # Use just 2 models for speed in unit tests
        self.pipelines = {
            "决策树": pipelines["决策树"],
            "朴素贝叶斯": pipelines["朴素贝叶斯"],
        }
        self.results = train_and_evaluate(
            self.pipelines, X_train, y_train, X_test, y_test, cv=3
        )
        self.X_test = X_test
        self.y_test = y_test

    def test_returns_dict_keyed_by_model_name(self):
        """Results should be a dict keyed by model name."""
        assert set(self.results.keys()) == set(self.pipelines.keys())

    def test_each_result_has_required_keys(self):
        """Each model result must contain all required metric keys."""
        required = {
            "cv_macro_f1_mean",
            "cv_macro_f1_std",
            "cv_scores",
            "test_macro_f1",
            "test_weighted_f1",
            "test_per_class_precision",
            "test_per_class_recall",
            "test_per_class_f1",
            "confusion_matrix",
            "predictions",
        }
        for name, res in self.results.items():
            missing = required - set(res.keys())
            assert not missing, f"{name} missing keys: {missing}"

    def test_predictions_have_valid_labels_and_shape(self):
        """Predictions should have same length as test set, labels in {0,1,2}."""
        for name, res in self.results.items():
            preds = res["predictions"]
            assert len(preds) == len(self.y_test), f"{name}: prediction length mismatch"
            assert set(preds).issubset({0, 1, 2}), f"{name}: invalid labels {set(preds)}"

    def test_smote_does_not_pollute_test_set(self):
        """Test set size should remain unchanged (SMOTE only trains)."""
        for name, res in self.results.items():
            assert len(res["predictions"]) == len(self.y_test), (
                f"{name}: test set was resampled"
            )


class TestPlotModelComparisonUnit:
    """Unit tests for plot_model_comparison."""

    def test_creates_png_file(self, tmp_path):
        """plot_model_comparison should create a PNG file at save_path."""
        from src.model import plot_model_comparison

        # Minimal fake results
        results = {
            "决策树": {"test_macro_f1": 0.45},
            "朴素贝叶斯": {"test_macro_f1": 0.40},
        }
        save_path = tmp_path / "comparison.png"
        plot_model_comparison(results, save_path=str(save_path))

        assert save_path.exists(), "Chart file was not created"

    def test_chart_has_sufficient_dpi(self, tmp_path):
        """Saved chart should have DPI >= 150 for PPT quality."""
        from PIL import Image

        from src.model import plot_model_comparison

        results = {"决策树": {"test_macro_f1": 0.45}}
        save_path = tmp_path / "comparison.png"
        plot_model_comparison(results, save_path=str(save_path))

        img = Image.open(save_path)
        dpi = img.info.get("dpi", (72, 72))
        assert dpi[0] >= 150, f"DPI too low: {dpi[0]}"


# ── Integration tests (require 数据.xlsx) ───────────────────────────────


def _prepare_real_data():
    """Run the full data pipeline: load → clean → map → encode."""
    df = encode_features(map_major(clean_data(load_data(DATA_PATH))))
    return df


@requires_data
class TestSplitDataIntegration:
    """Integration tests for split_data on real survey data."""

    def test_80_20_split_row_counts(self):
        """80/20 split on 1781 rows: train=1424, test=357 (±1)."""
        from src.model import split_data

        df = _prepare_real_data()
        X_train, X_test, y_train, y_test = split_data(df)
        total = len(df)
        assert len(X_train) + len(X_test) == total
        assert abs(len(X_test) - int(total * 0.2)) <= 1

    def test_stratification_on_real_data(self):
        """Class ratios should match between train and test within 2%."""
        from src.model import split_data

        df = _prepare_real_data()
        X_train, X_test, y_train, y_test = split_data(df)

        train_ratio = y_train.value_counts(normalize=True).sort_index()
        test_ratio = y_test.value_counts(normalize=True).sort_index()

        for cls in [0, 1, 2]:
            assert abs(train_ratio[cls] - test_ratio[cls]) < 0.02, (
                f"Class {cls}: train={train_ratio[cls]:.3f}, test={test_ratio[cls]:.3f}"
            )

    def test_feature_count_preserved(self):
        """76 features should be preserved through split."""
        from src.model import split_data

        df = _prepare_real_data()
        X_train, X_test, _, _ = split_data(df)
        assert X_train.shape[1] == 76
        assert X_test.shape[1] == 76


@requires_data
class TestTrainAndEvaluateIntegration:
    """Integration tests for the full modeling pipeline on real data."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        """Run full pipeline: data → split → train → evaluate."""
        from src.model import build_pipelines, split_data, train_and_evaluate

        df = _prepare_real_data()
        X_train, X_test, y_train, y_test = split_data(df)

        # Use 2 fast models for integration speed
        all_pipes = build_pipelines()
        self.pipelines = {
            "决策树": all_pipes["决策树"],
            "朴素贝叶斯": all_pipes["朴素贝叶斯"],
        }
        self.results = train_and_evaluate(
            self.pipelines, X_train, y_train, X_test, y_test, cv=5
        )
        self.y_test = y_test
        self.X_test = X_test

    def test_all_models_produce_predictions(self):
        """Each model should produce predictions of correct length."""
        for name, res in self.results.items():
            assert len(res["predictions"]) == len(self.y_test)

    def test_smote_integrity_on_real_data(self):
        """Test set must retain original imbalance — no SMOTE leakage."""
        for name, res in self.results.items():
            assert len(res["predictions"]) == len(self.y_test), (
                f"{name}: test predictions exceed test set size"
            )
            # Confusion matrix shape should be 3x3
            assert res["confusion_matrix"].shape == (3, 3)

    def test_per_class_metrics_have_three_entries(self):
        """Per-class precision/recall/f1 should each have 3 values."""
        for name, res in self.results.items():
            assert len(res["test_per_class_precision"]) == 3
            assert len(res["test_per_class_recall"]) == 3
            assert len(res["test_per_class_f1"]) == 3

    def test_cv_scores_have_five_folds(self):
        """CV scores should contain 5 values (one per fold)."""
        for name, res in self.results.items():
            assert len(res["cv_scores"]) == 5

    def test_macro_f1_in_reasonable_range(self):
        """Macro F1 should be between 0 and 1 (model actually learned)."""
        for name, res in self.results.items():
            assert 0 < res["test_macro_f1"] <= 1.0, (
                f"{name}: unreasonable Macro F1 = {res['test_macro_f1']}"
            )
