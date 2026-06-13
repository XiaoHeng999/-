"""端到端测试：验证数据处理 + 建模完整流程可以运行。"""

import subprocess
from pathlib import Path

import pytest

DATA_PATH = Path(__file__).resolve().parent.parent.parent / "数据.xlsx"

requires_data = pytest.mark.skipif(
    not DATA_PATH.exists(),
    reason="数据.xlsx not available (excluded from VCS)",
)


def _results_root():
    return Path(__file__).resolve().parent.parent.parent / "results"


@requires_data
def test_cli_entrypoint():
    """验证 main.py 作为脚本可正常执行并退出码为 0"""
    result = subprocess.run(
        ["uv", "run", "python", "main.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"main.py 执行失败: {result.stderr}"
    assert "实验完成" in result.stdout


@requires_data
def test_model_comparison_outputs():
    """验证模型对比实验生成所有预期输出文件"""
    base = _results_root() / "model_comparison"
    assert (base / "metrics_summary.csv").exists(), "metrics_summary.csv missing"
    assert (base / "model_comparison_f1.png").exists(), "model_comparison_f1.png missing"
    assert (base / "per_class_metrics.png").exists(), "per_class_metrics.png missing"
    assert (base / "cv_boxplot.png").exists(), "cv_boxplot.png missing"

    cm_dir = base / "confusion_matrices"
    for name in ["knn", "decision_tree", "random_forest", "svm", "naive_bayes", "logistic_regression"]:
        assert (cm_dir / f"{name}_cm.png").exists(), f"{name}_cm.png missing"


@requires_data
def test_hyperparameter_tuning_outputs():
    """验证超参数调优生成所有预期输出文件"""
    base = _results_root() / "hyperparameter_tuning"
    assert (base / "summary.csv").exists(), "summary.csv missing"

    for model in ["random_forest", "svm", "knn", "decision_tree"]:
        model_dir = base / model
        assert (model_dir / "best_params.txt").exists(), f"{model}/best_params.txt missing"
        assert (model_dir / "tuning_results.csv").exists(), f"{model}/tuning_results.csv missing"
        # At least one PNG should exist
        pngs = list(model_dir.glob("*.png"))
        assert len(pngs) > 0, f"{model}/ should have at least one PNG"


@requires_data
def test_factor_analysis_outputs():
    """验证因子分析生成所有预期输出文件"""
    base = _results_root() / "factor_analysis"
    assert (base / "rf_importance.png").exists(), "rf_importance.png missing"
    assert (base / "permutation_importance.png").exists(), "permutation_importance.png missing"
    assert (base / "shap_bar_low.png").exists(), "shap_bar_low.png missing"
    assert (base / "shap_bar_medium.png").exists(), "shap_bar_medium.png missing"
    assert (base / "shap_bar_high.png").exists(), "shap_bar_high.png missing"
    assert (base / "shap_summary.png").exists(), "shap_summary.png missing"
    assert (base / "shap_beeswarm.png").exists(), "shap_beeswarm.png missing"
    assert (base / "cross_method_comparison.png").exists(), "cross_method_comparison.png missing"
    assert (base / "consensus_ranking.csv").exists(), "consensus_ranking.csv missing"


@requires_data
def test_pca_outputs():
    """验证 PCA 生成散点图"""
    base = _results_root() / "pca"
    assert (base / "pca_scatter.png").exists(), "pca_scatter.png missing"


def test_project_importable():
    """验证项目核心依赖均可正常导入"""
    import pandas  # noqa: F401
    import numpy  # noqa: F401
    import sklearn  # noqa: F401
    import matplotlib  # noqa: F401
    import seaborn  # noqa: F401

    # 只要能导入就说明环境没问题
    assert True
