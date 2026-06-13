"""Experiment orchestrator: data prep → model comparison → tuning → factor analysis → PCA."""

from src.data import clean_data, encode_features, load_data, map_major
from src.model import split_data
from src.utils import ensure_results_dirs, print_experiment_header
from src.experiments import run_model_comparison, run_hyperparameter_tuning, run_factor_analysis
from src.pca import reduce_pca, plot_pca_scatter


def main():
    """Run the full ML experiment pipeline."""
    # ── 1. Data preparation ────────────────────────────────────────────
    print_experiment_header("数据准备")
    df = load_data()
    df = clean_data(df)
    df = map_major(df)
    df = encode_features(df)

    X_train, X_test, y_train, y_test = split_data(df)
    feature_names = X_train.columns.tolist()
    print(f"  训练集: {X_train.shape}, 测试集: {X_test.shape}")
    print(f"  特征数: {len(feature_names)}")

    # ── 2. Initialize results directory ────────────────────────────────
    results_root = ensure_results_dirs()

    # ── 3. Experiment 1: Multi-model comparison ────────────────────────
    results, pipelines = run_model_comparison(
        X_train, X_test, y_train, y_test, feature_names,
    )

    # ── 4. Experiment 2: Hyperparameter tuning ─────────────────────────
    tuning_results = run_hyperparameter_tuning(X_train, y_train)

    # ── 5. Experiment 3: Factor analysis ───────────────────────────────
    consensus = run_factor_analysis(
        pipelines, X_train, X_test, y_train, y_test, feature_names,
    )

    # ── 6. PCA visualization ───────────────────────────────────────────
    print_experiment_header("PCA 降维可视化")
    X_reduced, evr = reduce_pca(X_train)
    pca_path = results_root / "pca" / "pca_scatter.png"
    plot_pca_scatter(X_reduced, y_train, save_path=str(pca_path))
    print(f"  ✓ PCA 散点图: {pca_path}")
    print(f"  解释方差比: PC1={evr[0]:.3f}, PC2={evr[1]:.3f}, 总计={evr.sum():.3f}")

    # ── Final summary ──────────────────────────────────────────────────
    print_experiment_header("实验完成")
    print("  所有实验已成功执行！")
    print(f"  结果保存在: {results_root}")


if __name__ == "__main__":
    main()
