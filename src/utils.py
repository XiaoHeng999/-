"""Utility functions: results directory management, CSV export, printing."""

from pathlib import Path

import pandas as pd

# Project root (one level up from src/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Results directory tree specification
_RESULTS_TREE: list[str] = [
    "results",
    "results/model_comparison",
    "results/model_comparison/confusion_matrices",
    "results/hyperparameter_tuning",
    "results/hyperparameter_tuning/random_forest",
    "results/hyperparameter_tuning/svm",
    "results/hyperparameter_tuning/knn",
    "results/hyperparameter_tuning/decision_tree",
    "results/factor_analysis",
    "results/pca",
]


def ensure_results_dirs(root: Path | str | None = None) -> Path:
    """Create the full results/ directory tree and return the root path.

    Parameters
    ----------
    root : Path or None
        Project root directory. Defaults to the repo root (parent of ``src/``).

    Returns
    -------
    Path
        The ``results/`` directory path.
    """
    if root is None:
        root = _PROJECT_ROOT
    root = Path(root)
    results_root = root / "results"
    for rel in _RESULTS_TREE:
        (root / rel).mkdir(parents=True, exist_ok=True)
    return results_root


def save_metrics_csv(metrics_dict: dict, path: Path | str) -> None:
    """Flatten a results dict into a CSV file (one row per model).

    Parameters
    ----------
    metrics_dict : dict
        Mapping of model name → dict of metric values.  Nested lists are
        converted to semicolon-joined strings.
    path : Path or str
        Destination file path.
    """
    rows = []
    for model_name, metrics in metrics_dict.items():
        flat: dict = {"model": model_name}
        for key, value in metrics.items():
            if isinstance(value, list):
                flat[key] = ";".join(str(v) for v in value)
            elif hasattr(value, "tolist"):
                # numpy array
                flat[key] = ";".join(str(v) for v in value.tolist())
            else:
                flat[key] = value
        rows.append(flat)
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def print_experiment_header(name: str) -> None:
    """Print a formatted experiment progress header.

    Parameters
    ----------
    name : str
        Experiment name to display.
    """
    width = 60
    print()
    print("=" * width)
    print(f"  实验: {name}")
    print("=" * width)
