"""SHAP deep analysis: explain model predictions with SHAP values."""

import matplotlib
matplotlib.use("Agg")  # non-interactive backend for headless environments

import numpy as np
import matplotlib.pyplot as plt
import shap

# Chinese font support for charts
plt.rcParams["font.sans-serif"] = ["Arial Unicode MS", "SimHei", "PingFang SC"]
plt.rcParams["axes.unicode_minus"] = False


def compute_shap_values(pipeline, X_train, X_test, feature_names):
    """Compute SHAP values for a fitted Random Forest pipeline.

    Parameters
    ----------
    pipeline : ImbPipeline
        A fitted pipeline whose final step is a RandomForestClassifier.
    X_train : pd.DataFrame
        Training feature matrix (used by TreeExplainer for background).
    X_test : pd.DataFrame
        Test feature matrix to explain.
    feature_names : list[str]
        Feature column names.

    Returns
    -------
    tuple[np.ndarray, pd.DataFrame]
        (shap_values, X_test) where shap_values has shape
        (n_classes, n_samples, n_features).
    """
    clf = pipeline.steps[-1][1]
    explainer = shap.TreeExplainer(clf)
    sv = explainer.shap_values(X_test)
    sv = np.array(sv)
    # Normalize shape to (n_classes, n_samples, n_features)
    # shap >= 0.45 returns (n_samples, n_features, n_classes) for multiclass
    if sv.ndim == 3 and sv.shape[-1] == clf.n_classes_ and sv.shape[0] != clf.n_classes_:
        sv = sv.transpose(2, 0, 1)
    return sv, X_test


_CLASS_LABELS = {0: "低频", 1: "中频", 2: "高频"}


# ── Internal helpers ────────────────────────────────────────────────────


def _top_features(shap_class_values, feature_names, top_n):
    """Return indices of top_n features sorted by mean |SHAP| descending."""
    mean_abs = np.abs(shap_class_values).mean(axis=0)
    return np.argsort(mean_abs)[::-1][:top_n]


def plot_shap_bar(shap_values, X_test_sample, class_idx=2, top_n=15, save_path=None):
    """Generate a PPT-quality horizontal bar chart of mean |SHAP| for one class.

    Parameters
    ----------
    shap_values : np.ndarray
        Shape (n_classes, n_samples, n_features).
    X_test_sample : pd.DataFrame
        Feature matrix (column names used as feature labels).
    class_idx : int
        Class index to plot (0=低频, 1=中频, 2=高频).
    top_n : int
        Number of top features to show.
    save_path : str or None
        File path to save the chart.
    """
    feature_names = list(X_test_sample.columns)
    mean_abs = np.abs(shap_values[class_idx]).mean(axis=0)
    order = _top_features(shap_values[class_idx], feature_names, top_n)

    features = [feature_names[i] for i in order]
    values = mean_abs[order]

    # Reverse for bottom-to-top (most important at top)
    features = features[::-1]
    values = values[::-1]
    n = len(features)

    fig, ax = plt.subplots(figsize=(10, max(6, n * 0.4)))
    colors = plt.cm.Set2(np.linspace(0, 1, n))
    ax.barh(features, values, color=colors, edgecolor="black", linewidth=0.5)

    label = _CLASS_LABELS.get(class_idx, str(class_idx))
    ax.set_xlabel("mean(|SHAP value|)", fontsize=14)
    ax.set_title(f"SHAP 特征重要性 ({label})", fontsize=16, fontweight="bold")
    ax.tick_params(axis="y", labelsize=11)
    ax.tick_params(axis="x", labelsize=11)
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_shap_summary(shap_values, X_test_sample, class_names=None, save_path=None):
    """Generate a PPT-quality grouped bar chart of mean |SHAP| across all classes.

    Parameters
    ----------
    shap_values : np.ndarray
        Shape (n_classes, n_samples, n_features).
    X_test_sample : pd.DataFrame
        Feature matrix (column names used as feature labels).
    class_names : list[str] or None
        Labels for each class. Defaults to ["低频", "中频", "高频"].
    save_path : str or None
        File path to save the chart.
    """
    if class_names is None:
        class_names = ["低频", "中频", "高频"]

    feature_names = list(X_test_sample.columns)
    n_classes = shap_values.shape[0]

    # Compute mean |SHAP| per feature per class
    mean_abs = np.abs(shap_values).mean(axis=1)  # (n_classes, n_features)

    # Pick top 15 features by overall mean |SHAP| (across all classes)
    top_n = 15
    overall = mean_abs.mean(axis=0)
    order = np.argsort(overall)[::-1][:top_n]
    features = [feature_names[i] for i in order]
    class_values = mean_abs[:, order]  # (n_classes, top_n)

    # Reverse for bottom-to-top (most important at top)
    features = features[::-1]
    class_values = class_values[:, ::-1]

    # Grouped horizontal bar chart
    n = len(features)
    bar_height = 0.25
    y_pos = np.arange(n)

    fig, ax = plt.subplots(figsize=(12, max(6, n * 0.45)))
    colors = plt.cm.Set2(np.linspace(0, 1, n_classes))

    for c in range(n_classes):
        offset = (c - n_classes / 2 + 0.5) * bar_height
        ax.barh(
            y_pos + offset,
            class_values[c],
            height=bar_height,
            color=colors[c],
            edgecolor="black",
            linewidth=0.5,
            label=class_names[c],
        )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(features, fontsize=10)
    ax.set_xlabel("mean(|SHAP value|)", fontsize=14)
    ax.set_title("SHAP 特征重要性 (各类别)", fontsize=16, fontweight="bold")
    ax.legend(fontsize=12, loc="lower right")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_shap_beeswarm(shap_values, X_test_sample, class_idx=2, save_path=None):
    """Generate a PPT-quality beeswarm plot for one class.

    Each dot is one sample. X-axis = SHAP value, color = feature value.
    Shows top 15 features ranked by mean |SHAP|.

    Parameters
    ----------
    shap_values : np.ndarray
        Shape (n_classes, n_samples, n_features).
    X_test_sample : pd.DataFrame
        Feature matrix (column names used as feature labels).
    class_idx : int
        Class index to plot (0=低频, 1=中频, 2=高频).
    save_path : str or None
        File path to save the chart.
    """
    feature_names = list(X_test_sample.columns)
    sv_class = shap_values[class_idx]  # (n_samples, n_features)
    data = X_test_sample.values

    # Select top 15 features by mean |SHAP|
    top_n = 15
    order = _top_features(sv_class, feature_names, top_n)

    sv_top = sv_class[:, order]
    data_top = data[:, order]
    names_top = [feature_names[i] for i in order]

    n = len(names_top)
    fig, ax = plt.subplots(figsize=(10, max(6, n * 0.4)))

    # Color normalization across all feature values
    vmin, vmax = data_top.min(), data_top.max()
    cmap = plt.cm.coolwarm

    for i in range(n - 1, -1, -1):
        y_pos = np.full(sv_top.shape[0], i, dtype=float)
        # Jitter for visibility
        rng = np.random.default_rng(42)
        y_jitter = y_pos + rng.uniform(-0.3, 0.3, size=sv_top.shape[0])
        scatter = ax.scatter(
            sv_top[:, i],
            y_jitter,
            c=data_top[:, i],
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            alpha=0.6,
            s=16,
            edgecolors="none",
            linewidths=0,
        )

    ax.set_yticks(range(n))
    ax.set_yticklabels(names_top, fontsize=10)
    ax.set_xlabel("SHAP value", fontsize=14)
    label = _CLASS_LABELS.get(class_idx, str(class_idx))
    ax.set_title(f"SHAP 特征影响 ({label})", fontsize=16, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)

    cbar = fig.colorbar(scatter, ax=ax, pad=0.02)
    cbar.set_label("特征值", fontsize=12)
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
