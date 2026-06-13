"""PCA dimensionality reduction and 2D scatter visualization."""

import matplotlib
matplotlib.use("Agg")  # non-interactive backend for headless environments

import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Chinese font support for charts
plt.rcParams["font.sans-serif"] = ["Arial Unicode MS", "SimHei", "PingFang SC"]
plt.rcParams["axes.unicode_minus"] = False


def reduce_pca(X):
    """Standardize and reduce feature matrix to 2 dimensions via PCA.

    Parameters
    ----------
    X : pd.DataFrame or np.ndarray
        Feature matrix (n_samples, n_features).

    Returns
    -------
    X_reduced : np.ndarray of shape (n_samples, 2)
        PCA-transformed 2D coordinates.
    explained_variance_ratio : np.ndarray of shape (2,)
        Proportion of variance explained by each component.
    """
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    pca = PCA(n_components=2, random_state=42)
    X_reduced = pca.fit_transform(X_scaled)

    return X_reduced, pca.explained_variance_ratio_


def plot_pca_scatter(X_reduced, y, save_path=None):
    """Generate a PPT-quality scatter plot of PCA-reduced data.

    Parameters
    ----------
    X_reduced : np.ndarray of shape (n_samples, 2)
        PCA-transformed 2D coordinates.
    y : array-like
        Target labels (0, 1, 2) for coloring.
    save_path : str or None
        File path to save the chart. If None, displays interactively.
    """
    y = np.asarray(y)
    class_labels = {0: "低频", 1: "中频", 2: "高频"}
    colors = ["#66c2a5", "#fc8d62", "#8da0cb"]  # Set2-inspired

    fig, ax = plt.subplots(figsize=(10, 8))

    for cls in [0, 1, 2]:
        mask = y == cls
        ax.scatter(
            X_reduced[mask, 0],
            X_reduced[mask, 1],
            c=colors[cls],
            label=class_labels[cls],
            alpha=0.6,
            s=40,
            edgecolors="white",
            linewidths=0.5,
        )

    ax.set_xlabel("主成分 1", fontsize=14)
    ax.set_ylabel("主成分 2", fontsize=14)
    ax.set_title("PCA 降维可视化（按使用频率分类）", fontsize=16, fontweight="bold")
    ax.legend(fontsize=12, title="使用频率", title_fontsize=13)
    ax.grid(alpha=0.3)
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
