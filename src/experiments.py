"""Experiment functions: model comparison, hyperparameter tuning, factor analysis."""

import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV

from src.model import build_pipelines, train_and_evaluate, plot_model_comparison
from src.utils import save_metrics_csv, print_experiment_header

plt.rcParams["font.sans-serif"] = ["Arial Unicode MS", "SimHei", "PingFang SC"]
plt.rcParams["axes.unicode_minus"] = False

# Chinese model name → English file name mapping
_NAME_MAP = {
    "KNN": "knn",
    "决策树": "decision_tree",
    "随机森林": "random_forest",
    "SVM": "svm",
    "朴素贝叶斯": "naive_bayes",
    "Logistic回归": "logistic_regression",
}

_CLASS_NAMES = ["低频", "中频", "高频"]


# ── Visualization helpers ───────────────────────────────────────────────


def _plot_per_class_metrics(results: dict, save_path: str | Path) -> None:
    """3 classes × 6 models grouped bar chart: Precision / Recall / F1."""
    model_names = list(results.keys())
    metrics_keys = [
        ("test_per_class_precision", "Precision"),
        ("test_per_class_recall", "Recall"),
        ("test_per_class_f1", "F1"),
    ]

    n_classes = 3
    n_models = len(model_names)
    n_metrics = len(metrics_keys)

    fig, axes = plt.subplots(1, n_classes, figsize=(7 * n_classes, 6), sharey=True)
    bar_width = 0.25
    colors = plt.cm.Set2(np.linspace(0, 1, n_metrics))

    for cls_idx, ax in enumerate(axes):
        x = np.arange(n_models)
        for m_idx, (key, label) in enumerate(metrics_keys):
            values = [results[name][key][cls_idx] for name in model_names]
            offset = (m_idx - n_metrics / 2 + 0.5) * bar_width
            bars = ax.bar(
                x + offset, values, bar_width,
                color=colors[m_idx], edgecolor="black", linewidth=0.5, label=label,
            )
            for bar, val in zip(bars, values):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.01,
                    f"{val:.2f}", ha="center", va="bottom", fontsize=7,
                )
        ax.set_xticks(x)
        ax.set_xticklabels(model_names, fontsize=9, rotation=20, ha="right")
        ax.set_title(f"{_CLASS_NAMES[cls_idx]}频", fontsize=14, fontweight="bold")
        ax.set_ylim(0, 1.15)
        ax.grid(axis="y", alpha=0.3)
        if cls_idx == 0:
            ax.set_ylabel("分数", fontsize=13)
        if cls_idx == n_classes - 1:
            ax.legend(fontsize=10, loc="upper right")

    fig.suptitle("各类别模型性能对比", fontsize=16, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(save_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def _plot_confusion_matrix(
    cm: np.ndarray, model_name: str, class_names: list[str], save_path: str | Path,
) -> None:
    """Single model confusion matrix heatmap."""
    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=class_names, yticklabels=class_names,
        ax=ax, linewidths=0.5, linecolor="gray",
    )
    ax.set_xlabel("预测标签", fontsize=13)
    ax.set_ylabel("真实标签", fontsize=13)
    ax.set_title(f"混淆矩阵 — {model_name}", fontsize=15, fontweight="bold")
    fig.tight_layout()
    fig.savefig(save_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def _plot_cv_boxplot(results: dict, save_path: str | Path) -> None:
    """6-model 5-fold CV scores boxplot."""
    model_names = list(results.keys())
    data = [results[name]["cv_scores"] for name in model_names]

    fig, ax = plt.subplots(figsize=(10, 6))
    bp = ax.boxplot(
        data, patch_artist=True, tick_labels=model_names,
        boxprops=dict(linewidth=1),
        medianprops=dict(color="black", linewidth=1.5),
    )
    colors = plt.cm.Set2(np.linspace(0, 1, len(model_names)))
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)

    ax.set_ylabel("Macro F1 (5-fold CV)", fontsize=13)
    ax.set_title("模型交叉验证分数分布", fontsize=16, fontweight="bold")
    ax.tick_params(axis="x", labelsize=11)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(save_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


# ── Experiment 1: Multi-model comparison ────────────────────────────────


def run_model_comparison(
    X_train, X_test, y_train, y_test, feature_names, results_root=None,
):
    """Run all 6 models, generate comparison charts, save metrics CSV.

    Parameters
    ----------
    X_train, X_test, y_train, y_test : array-like
        Train/test split data.
    feature_names : list[str]
        Feature column names.
    results_root : Path or None
        Root of results directory. Defaults to ``results/`` in project root.

    Returns
    -------
    tuple[dict, dict]
        ``(results_dict, pipelines_dict)`` — results keyed by model name
        and fitted pipelines for reuse.
    """
    from src.utils import _PROJECT_ROOT

    if results_root is None:
        results_root = _PROJECT_ROOT / "results"
    results_root = Path(results_root)

    print_experiment_header("实验 1: 多模型对比")

    # Build and train
    pipelines = build_pipelines()
    results = train_and_evaluate(pipelines, X_train, y_train, X_test, y_test, cv=5)

    # ── Save metrics CSV ────────────────────────────────────────────
    csv_path = results_root / "model_comparison" / "metrics_summary.csv"
    save_metrics_csv(results, csv_path)
    print(f"  ✓ 指标汇总: {csv_path}")

    # ── F1 comparison bar chart ─────────────────────────────────────
    f1_path = results_root / "model_comparison" / "model_comparison_f1.png"
    plot_model_comparison(results, save_path=str(f1_path))
    print(f"  ✓ F1 对比图: {f1_path}")

    # ── Per-class metrics grouped bar chart ─────────────────────────
    per_class_path = results_root / "model_comparison" / "per_class_metrics.png"
    _plot_per_class_metrics(results, per_class_path)
    print(f"  ✓ 分类别指标图: {per_class_path}")

    # ── CV boxplot ──────────────────────────────────────────────────
    cv_path = results_root / "model_comparison" / "cv_boxplot.png"
    _plot_cv_boxplot(results, cv_path)
    print(f"  ✓ CV 箱线图: {cv_path}")

    # ── Confusion matrices ──────────────────────────────────────────
    cm_dir = results_root / "model_comparison" / "confusion_matrices"
    cm_dir.mkdir(parents=True, exist_ok=True)
    for name, res in results.items():
        fname = _NAME_MAP.get(name, name) + "_cm.png"
        _plot_confusion_matrix(
            res["confusion_matrix"], name, _CLASS_NAMES,
            cm_dir / fname,
        )
    print(f"  ✓ 混淆矩阵: {cm_dir}/")

    # Print summary table
    print("\n  模型性能汇总:")
    print(f"  {'模型':<12} {'Macro F1':>10} {'CV Mean':>10} {'CV Std':>10}")
    print("  " + "-" * 44)
    for name in sorted(results, key=lambda n: results[n]["test_macro_f1"], reverse=True):
        r = results[name]
        print(f"  {name:<12} {r['test_macro_f1']:>10.4f} {r['cv_macro_f1_mean']:>10.4f} {r['cv_macro_f1_std']:>10.4f}")

    return results, pipelines


# ── Tuning visualization helpers ────────────────────────────────────────


def _resolve_param_col(cv_results_df: pd.DataFrame, param_name: str) -> str:
    """Resolve the actual column name in cv_results_ for a parameter.

    GridSearchCV with Pipeline stores columns as ``param_clf__n_estimators``,
    so we try the prefixed name first, then fall back to the bare name.
    """
    for candidate in [f"param_clf__{param_name}", f"param_{param_name}"]:
        if candidate in cv_results_df.columns:
            return candidate
    raise KeyError(f"Parameter column not found: tried param_clf__{param_name} and param_{param_name}")


def _plot_tuning_heatmap(
    cv_results_df: pd.DataFrame,
    param_x: str,
    param_y: str,
    save_path: str | Path,
) -> None:
    """Two-parameter Macro F1 heatmap."""
    col_x = _resolve_param_col(cv_results_df, param_x)
    col_y = _resolve_param_col(cv_results_df, param_y)
    pivot = cv_results_df.pivot_table(
        index=col_y,
        columns=col_x,
        values="mean_test_score",
        aggfunc="mean",
    )
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        pivot, annot=True, fmt=".3f", cmap="YlOrRd",
        ax=ax, linewidths=0.5,
    )
    ax.set_xlabel(param_x, fontsize=13)
    ax.set_ylabel(param_y, fontsize=13)
    ax.set_title(f"GridSearch Heatmap: {param_x} × {param_y}", fontsize=15, fontweight="bold")
    fig.tight_layout()
    fig.savefig(save_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def _plot_tuning_line(
    cv_results_df: pd.DataFrame,
    param_name: str,
    save_path: str | Path,
) -> None:
    """Single-parameter Macro F1 line chart."""
    col = _resolve_param_col(cv_results_df, param_name)
    grouped = cv_results_df.groupby(col)["mean_test_score"].agg(["mean", "std"]).reset_index()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(
        grouped[col].astype(str),
        grouped["mean"],
        "o-", color="#2c7fb8", linewidth=2, markersize=8,
    )
    ax.fill_between(
        grouped[col].astype(str),
        grouped["mean"] - grouped["std"],
        grouped["mean"] + grouped["std"],
        alpha=0.2, color="#2c7fb8",
    )
    ax.set_xlabel(param_name, fontsize=13)
    ax.set_ylabel("Mean Macro F1 (CV)", fontsize=13)
    ax.set_title(f"调优折线图: {param_name}", fontsize=15, fontweight="bold")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(save_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


# ── Experiment 2: Hyperparameter tuning ─────────────────────────────────


_TUNING_CONFIGS = {
    "random_forest": {
        "clf": RandomForestClassifier(random_state=42),
        "params": {
            "clf__n_estimators": [100, 200, 300],
            "clf__max_depth": [10, 20, None],
            "clf__min_samples_split": [2, 5, 10],
            "clf__max_features": ["sqrt", "log2"],
        },
        "label": "随机森林",
        "heatmaps": [
            ("n_estimators", "max_depth"),
        ],
        "lines": ["n_estimators"],
    },
    "svm": {
        "clf": SVC(random_state=42),
        "params": {
            "clf__C": [0.1, 1, 10, 100],
            "clf__kernel": ["rbf", "linear"],
            "clf__gamma": ["scale", "auto"],
        },
        "label": "SVM",
        "heatmaps": [
            ("C", "gamma"),
        ],
        "lines": ["C"],
    },
    "knn": {
        "clf": KNeighborsClassifier(),
        "params": {
            "clf__n_neighbors": [3, 5, 7, 9, 11],
            "clf__weights": ["uniform", "distance"],
            "clf__metric": ["euclidean", "manhattan"],
        },
        "label": "KNN",
        "heatmaps": [
            ("n_neighbors", "weights"),
        ],
        "lines": ["n_neighbors"],
    },
    "decision_tree": {
        "clf": DecisionTreeClassifier(random_state=42),
        "params": {
            "clf__max_depth": [5, 10, 20, None],
            "clf__min_samples_split": [2, 5, 10, 20],
            "clf__criterion": ["gini", "entropy"],
        },
        "label": "决策树",
        "heatmaps": [
            ("max_depth", "min_samples_split"),
        ],
        "lines": ["max_depth"],
    },
}


def run_hyperparameter_tuning(
    X_train, y_train, results_root=None,
) -> dict[str, dict]:
    """GridSearchCV for 4 key models, save tuning reports and visualizations.

    Parameters
    ----------
    X_train : array-like
        Training features.
    y_train : array-like
        Training target.
    results_root : Path or None
        Root of results directory.

    Returns
    -------
    dict[str, dict]
        Best params and scores keyed by model key.
    """
    from src.utils import _PROJECT_ROOT

    if results_root is None:
        results_root = _PROJECT_ROOT / "results"
    results_root = Path(results_root)

    print_experiment_header("实验 2: 超参数调优")

    summary_rows = []
    all_best = {}

    for model_key, cfg in _TUNING_CONFIGS.items():
        label = cfg["label"]
        print(f"\n  调优 {label}...")

        pipe = ImbPipeline([
            ("smote", SMOTE(random_state=42)),
            ("clf", cfg["clf"]),
        ])

        gs = GridSearchCV(
            pipe, cfg["params"],
            cv=5, scoring="f1_macro", n_jobs=-1, refit=True,
        )
        gs.fit(X_train, y_train)

        # ── Save results ──────────────────────────────────────────
        model_dir = results_root / "hyperparameter_tuning" / model_key
        model_dir.mkdir(parents=True, exist_ok=True)

        # best_params.txt
        with open(model_dir / "best_params.txt", "w", encoding="utf-8") as f:
            f.write(f"Model: {label}\n")
            f.write(f"Best CV Macro F1: {gs.best_score_:.4f}\n")
            f.write("Best Parameters:\n")
            for k, v in gs.best_params_.items():
                f.write(f"  {k}: {v}\n")

        # tuning_results.csv
        cv_df = pd.DataFrame(gs.cv_results_)
        cv_df.to_csv(model_dir / "tuning_results.csv", index=False, encoding="utf-8-sig")

        # Heatmaps
        for param_x, param_y in cfg["heatmaps"]:
            fname = f"heatmap_{param_x}_vs_{param_y}.png"
            _plot_tuning_heatmap(cv_df, param_x, param_y, model_dir / fname)

        # Line charts
        for param_name in cfg["lines"]:
            fname = f"line_{param_name}.png"
            _plot_tuning_line(cv_df, param_name, model_dir / fname)

        print(f"    ✓ Best F1: {gs.best_score_:.4f}")
        print(f"    ✓ 结果保存: {model_dir}/")

        summary_rows.append({
            "model": label,
            "model_key": model_key,
            "best_cv_f1": gs.best_score_,
            "best_params": str(gs.best_params_),
        })
        all_best[model_key] = {
            "best_params": gs.best_params_,
            "best_score": gs.best_score_,
            "best_estimator": gs.best_estimator_,
        }

    # ── Summary CSV ──────────────────────────────────────────────────
    summary_df = pd.DataFrame(summary_rows)
    summary_df = summary_df.sort_values("best_cv_f1", ascending=False).reset_index(drop=True)
    summary_df.to_csv(
        results_root / "hyperparameter_tuning" / "summary.csv",
        index=False, encoding="utf-8-sig",
    )
    print(f"\n  ✓ 调优汇总: {results_root / 'hyperparameter_tuning' / 'summary.csv'}")

    return all_best


# ── Factor analysis visualization helpers ───────────────────────────────


def _plot_cross_method_comparison(
    rf_df: pd.DataFrame,
    perm_df: pd.DataFrame,
    shap_df: pd.DataFrame,
    save_path: str | Path,
) -> None:
    """Horizontal grouped bar chart: RF / Permutation / SHAP per feature.

    Each method's importance is normalized to [0, 1]. Shows all features
    appearing in any method's Top-15.
    """
    def _normalize(df):
        s = df.set_index("feature")["importance"]
        rng = s.max() - s.min()
        if rng == 0:
            return s
        return (s - s.min()) / rng

    rf_norm = _normalize(rf_df)
    perm_norm = _normalize(perm_df)
    shap_norm = _normalize(shap_df)

    # Collect all features from any Top-15
    all_features = set(rf_df["feature"]) | set(perm_df["feature"]) | set(shap_df["feature"])

    # Compute mean normalized importance for sorting
    mean_imp = {}
    for feat in all_features:
        vals = []
        for normed in [rf_norm, perm_norm, shap_norm]:
            if feat in normed.index:
                vals.append(normed[feat])
        mean_imp[feat] = np.mean(vals) if vals else 0

    sorted_features = sorted(mean_imp, key=mean_imp.get, reverse=True)[:15]

    n = len(sorted_features)
    bar_height = 0.25
    y_pos = np.arange(n)

    fig, ax = plt.subplots(figsize=(12, max(6, n * 0.45)))
    methods = [
        (rf_norm, "RF", "#66c2a5"),
        (perm_norm, "Permutation", "#fc8d62"),
        (shap_norm, "SHAP", "#8da0cb"),
    ]

    for i, (normed, label, color) in enumerate(methods):
        offset = (i - 1) * bar_height
        values = [normed.get(feat, 0) for feat in sorted_features]
        ax.barh(
            y_pos + offset, values, bar_height,
            color=color, edgecolor="black", linewidth=0.5, label=label,
        )

    features_reversed = sorted_features[::-1]
    ax.set_yticks(y_pos[::-1])
    ax.set_yticklabels(features_reversed, fontsize=9)
    ax.set_xlabel("Normalized Importance", fontsize=13)
    ax.set_title("跨方法特征重要性对比", fontsize=16, fontweight="bold")
    ax.legend(fontsize=11, loc="lower right")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(save_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def _compute_consensus_ranking(
    rf_df: pd.DataFrame,
    perm_df: pd.DataFrame,
    shap_df: pd.DataFrame,
) -> pd.DataFrame:
    """Compute consensus ranking across 3 methods.

    Each method's Top-15 features get rank 1-15; others get penalty rank 16.
    Final ranking is the mean rank across methods (ascending = best).
    """
    penalty = 16

    def _rank(df):
        return {feat: rank + 1 for rank, feat in enumerate(df["feature"].tolist())}

    rf_rank = _rank(rf_df)
    perm_rank = _rank(perm_df)
    shap_rank = _rank(shap_df)

    all_features = set(rf_rank) | set(perm_rank) | set(shap_rank)

    rows = []
    for feat in all_features:
        rows.append({
            "feature": feat,
            "rf_rank": rf_rank.get(feat, penalty),
            "perm_rank": perm_rank.get(feat, penalty),
            "shap_rank": shap_rank.get(feat, penalty),
        })

    consensus = pd.DataFrame(rows)
    consensus["mean_rank"] = consensus[["rf_rank", "perm_rank", "shap_rank"]].mean(axis=1)
    consensus = consensus.sort_values("mean_rank").reset_index(drop=True)
    return consensus.head(15)


# ── Experiment 3: Factor analysis ───────────────────────────────────────


def run_factor_analysis(
    pipelines: dict,
    X_train, X_test, y_train, y_test, feature_names,
    results_root=None,
) -> pd.DataFrame:
    """Comprehensive factor analysis: RF + Permutation + SHAP with cross-method comparison.

    Parameters
    ----------
    pipelines : dict
        Fitted pipelines from run_model_comparison.
    X_train, X_test : array-like
        Feature matrices.
    y_train, y_test : array-like
        Target vectors.
    feature_names : list[str]
        Feature column names.
    results_root : Path or None
        Root of results directory.

    Returns
    -------
    pd.DataFrame
        Consensus ranking DataFrame.
    """
    from src.importance import (
        compute_rf_importance,
        compute_permutation_importance,
        plot_rf_importance,
        plot_permutation_importance,
    )
    from src.shap_analysis import (
        compute_shap_values,
        plot_shap_bar,
        plot_shap_summary,
        plot_shap_beeswarm,
    )
    from src.utils import _PROJECT_ROOT

    if results_root is None:
        results_root = _PROJECT_ROOT / "results"
    results_root = Path(results_root)

    print_experiment_header("实验 3: 因子重要性分析")

    rf_pipe = pipelines["随机森林"]

    # ── RF importance ──────────────────────────────────────────────
    rf_df = compute_rf_importance(rf_pipe, feature_names, top_n=15)
    rf_path = results_root / "factor_analysis" / "rf_importance.png"
    plot_rf_importance(rf_df, save_path=str(rf_path))
    print(f"  ✓ RF 特征重要性: {rf_path}")

    # ── Permutation importance ─────────────────────────────────────
    perm_df = compute_permutation_importance(
        rf_pipe, X_test, y_test, feature_names, top_n=15,
    )
    perm_path = results_root / "factor_analysis" / "permutation_importance.png"
    plot_permutation_importance(perm_df, save_path=str(perm_path))
    print(f"  ✓ Permutation 重要性: {perm_path}")

    # ── SHAP analysis ──────────────────────────────────────────────
    shap_values, X_sample = compute_shap_values(rf_pipe, X_train, X_test, feature_names)

    # Per-class SHAP bar charts
    class_labels = {0: "low", 1: "medium", 2: "high"}
    for cls_idx, label in class_labels.items():
        path = results_root / "factor_analysis" / f"shap_bar_{label}.png"
        plot_shap_bar(shap_values, X_sample, class_idx=cls_idx, top_n=15, save_path=str(path))
        print(f"  ✓ SHAP bar ({label}): {path}")

    # Summary
    summary_path = results_root / "factor_analysis" / "shap_summary.png"
    plot_shap_summary(shap_values, X_sample, save_path=str(summary_path))
    print(f"  ✓ SHAP 汇总: {summary_path}")

    # Beeswarm (high frequency class)
    beeswarm_path = results_root / "factor_analysis" / "shap_beeswarm.png"
    plot_shap_beeswarm(shap_values, X_sample, class_idx=2, save_path=str(beeswarm_path))
    print(f"  ✓ SHAP 蜂群图: {beeswarm_path}")

    # ── Cross-method comparison ────────────────────────────────────
    # Build SHAP importance df (overall mean |SHAP|, top 15)
    mean_abs_shap = np.abs(shap_values).mean(axis=(0, 1))  # mean across classes and samples
    shap_all = pd.DataFrame({
        "feature": feature_names,
        "importance": mean_abs_shap,
    }).sort_values("importance", ascending=False).head(15).reset_index(drop=True)

    cross_path = results_root / "factor_analysis" / "cross_method_comparison.png"
    _plot_cross_method_comparison(rf_df, perm_df, shap_all, cross_path)
    print(f"  ✓ 跨方法对比: {cross_path}")

    # ── Consensus ranking ──────────────────────────────────────────
    consensus = _compute_consensus_ranking(rf_df, perm_df, shap_all)
    consensus_path = results_root / "factor_analysis" / "consensus_ranking.csv"
    consensus.to_csv(consensus_path, index=False, encoding="utf-8-sig")
    print(f"  ✓ 共识排名: {consensus_path}")

    # Print top features
    print("\n  Top-10 关键影响因素 (共识排名):")
    for _, row in consensus.head(10).iterrows():
        print(f"    {row['feature']:<40} mean_rank={row['mean_rank']:.1f}")

    return consensus
