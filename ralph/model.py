"""Modeling pipeline: split, train, evaluate, visualize."""

import matplotlib
matplotlib.use("Agg")  # non-interactive backend for headless environments

import numpy as np
import matplotlib.pyplot as plt
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

# Chinese font support for charts
plt.rcParams["font.sans-serif"] = ["Arial Unicode MS", "SimHei", "PingFang SC"]
plt.rcParams["axes.unicode_minus"] = False


def split_data(df, test_size=0.2, random_state=42):
    """Split feature matrix into train/test with stratification.

    Parameters
    ----------
    df : pd.DataFrame
        Feature matrix with a ``target`` column.
    test_size : float
        Fraction of data reserved for testing.
    random_state : int
        Reproducibility seed.

    Returns
    -------
    X_train, X_test, y_train, y_test
    """
    X = df.drop(columns=["target"])
    y = df["target"]
    return train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )


def build_pipelines(random_state=42):
    """Build 6 classification pipelines, each with SMOTE oversampling.

    Returns
    -------
    dict[str, ImbPipeline]
        Mapping of model name → Pipeline(SMOTE() → classifier).
    """
    classifiers = {
        "KNN": KNeighborsClassifier(),
        "决策树": DecisionTreeClassifier(random_state=random_state),
        "随机森林": RandomForestClassifier(random_state=random_state),
        "SVM": SVC(random_state=random_state),
        "朴素贝叶斯": GaussianNB(),
        "Logistic回归": LogisticRegression(random_state=random_state, max_iter=1000),
    }
    return {
        name: ImbPipeline([("smote", SMOTE(random_state=random_state)), ("clf", clf)])
        for name, clf in classifiers.items()
    }


def train_and_evaluate(pipelines, X_train, y_train, X_test, y_test, cv=5):
    """Train all pipelines with cross-validation, evaluate on held-out test set.

    Parameters
    ----------
    pipelines : dict[str, ImbPipeline]
    X_train, y_train : training data
    X_test, y_test : test data (SMOTE never applied here)
    cv : int
        Number of cross-validation folds.

    Returns
    -------
    dict[str, dict]
        Per-model results with CV scores, test metrics, confusion matrix,
        and predictions.
    """
    results = {}
    for name, pipe in pipelines.items():
        # 5-fold CV on training set — SMOTE runs inside each fold
        cv_scores = cross_val_score(
            pipe, X_train, y_train, cv=cv, scoring="f1_macro"
        )

        # Fit on full training set, predict on untouched test set
        pipe.fit(X_train, y_train)
        preds = pipe.predict(X_test)

        # Per-class metrics
        report = classification_report(
            y_test, preds, output_dict=True, zero_division=0
        )

        results[name] = {
            "cv_macro_f1_mean": float(cv_scores.mean()),
            "cv_macro_f1_std": float(cv_scores.std()),
            "cv_scores": cv_scores.tolist(),
            "test_macro_f1": float(
                f1_score(y_test, preds, average="macro", zero_division=0)
            ),
            "test_weighted_f1": float(
                f1_score(y_test, preds, average="weighted", zero_division=0)
            ),
            "test_per_class_precision": [
                report[str(c)]["precision"] for c in range(3)
            ],
            "test_per_class_recall": [
                report[str(c)]["recall"] for c in range(3)
            ],
            "test_per_class_f1": [
                report[str(c)]["f1-score"] for c in range(3)
            ],
            "confusion_matrix": confusion_matrix(y_test, preds),
            "predictions": preds,
        }
    return results


def plot_model_comparison(results, save_path=None):
    """Generate a PPT-quality bar chart comparing Macro F1 across models.

    Parameters
    ----------
    results : dict[str, dict]
        Output of ``train_and_evaluate``.
    save_path : str or None
        File path to save the chart. If None, displays interactively.
    """
    names = list(results.keys())
    scores = [results[n]["test_macro_f1"] for n in names]

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = plt.cm.Set2(np.linspace(0, 1, len(names)))
    bars = ax.bar(names, scores, color=colors, edgecolor="black", linewidth=0.5)

    # Value labels on top of each bar
    for bar, score in zip(bars, scores):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.01,
            f"{score:.3f}",
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold",
        )

    ax.set_ylabel("Macro F1", fontsize=14)
    ax.set_title("模型 Macro F1 对比", fontsize=16, fontweight="bold")
    ax.set_ylim(0, min(max(scores) + 0.15, 1.0))
    ax.tick_params(axis="x", labelsize=12)
    ax.tick_params(axis="y", labelsize=11)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
