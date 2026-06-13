"""Feature importance analysis: Random Forest and Permutation Importance."""

import matplotlib
matplotlib.use("Agg")  # non-interactive backend for headless environments

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Chinese font support for charts
plt.rcParams["font.sans-serif"] = ["Arial Unicode MS", "SimHei", "PingFang SC"]
plt.rcParams["axes.unicode_minus"] = False


def compute_rf_importance(pipeline, feature_names, top_n=15):
    """Extract top_n feature importances from a trained random forest pipeline.

    Parameters
    ----------
    pipeline : ImbPipeline
        A fitted pipeline whose final step is a RandomForestClassifier.
    feature_names : list[str]
        Feature column names matching the training data order.
    top_n : int
        Number of top features to return.

    Returns
    -------
    pd.DataFrame
        Columns ["feature", "importance"], sorted descending, top_n rows.
    """
    clf = pipeline.steps[-1][1]
    importances = clf.feature_importances_

    df = pd.DataFrame({
        "feature": feature_names,
        "importance": importances,
    })
    return _sort_and_trim(df, top_n)


def plot_rf_importance(importance_df, save_path=None):
    """Generate a PPT-quality horizontal bar chart of RF feature importance.

    Parameters
    ----------
    importance_df : pd.DataFrame
        Output of ``compute_rf_importance`` with "feature" and "importance" columns.
    save_path : str or None
        File path to save the chart. If None, displays interactively.
    """
    _plot_importance_bar(importance_df, title="随机森林特征重要性 (Top 15)", save_path=save_path)


def compute_permutation_importance(
    pipeline, X_test, y_test, feature_names, top_n=15, random_state=42,
):
    """Compute permutation importance on the test set.

    Parameters
    ----------
    pipeline : ImbPipeline
        A fitted pipeline.
    X_test : pd.DataFrame or np.ndarray
        Test feature matrix (SMOTE must never touch this).
    y_test : array-like
        Test target labels.
    feature_names : list[str]
        Feature column names matching the training data order.
    top_n : int
        Number of top features to return.
    random_state : int
        Reproducibility seed.

    Returns
    -------
    pd.DataFrame
        Columns ["feature", "importance"], sorted descending, top_n rows.
    """
    from sklearn.inspection import permutation_importance

    result = permutation_importance(
        pipeline, X_test, y_test, n_repeats=10, random_state=random_state, n_jobs=-1,
    )

    df = pd.DataFrame({
        "feature": feature_names,
        "importance": result.importances_mean,
    })
    return _sort_and_trim(df, top_n)


def plot_permutation_importance(importance_df, save_path=None):
    """Generate a PPT-quality horizontal bar chart of permutation importance.

    Parameters
    ----------
    importance_df : pd.DataFrame
        Output of ``compute_permutation_importance`` with "feature" and "importance" columns.
    save_path : str or None
        File path to save the chart. If None, displays interactively.
    """
    _plot_importance_bar(importance_df, title="Permutation Importance (Top 15)", save_path=save_path)


# ── Internal helpers ────────────────────────────────────────────────────


def _sort_and_trim(df, top_n):
    """Sort by importance descending and keep top_n rows."""
    return df.sort_values("importance", ascending=False).head(top_n).reset_index(drop=True)


def _plot_importance_bar(importance_df, title, save_path=None):
    """Draw a PPT-quality horizontal bar chart for feature importance."""
    # Reverse for bottom-to-top plotting (most important at top)
    df = importance_df.iloc[::-1]
    n = len(df)

    fig, ax = plt.subplots(figsize=(10, max(6, n * 0.4)))
    colors = plt.cm.Set2(np.linspace(0, 1, n))
    ax.barh(df["feature"], df["importance"], color=colors, edgecolor="black", linewidth=0.5)

    ax.set_xlabel("重要性", fontsize=14)
    ax.set_title(title, fontsize=16, fontweight="bold")
    ax.tick_params(axis="y", labelsize=11)
    ax.tick_params(axis="x", labelsize=11)
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
