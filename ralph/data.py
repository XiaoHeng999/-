"""Load raw survey data and create the target variable."""

from pathlib import Path

import pandas as pd

Q9_COL = "9、您使用生成式人工智能的频率如何?  "

_TARGET_MAP = {1: 0, 2: 1, 3: 2, 4: 2, 5: 2, 6: 2}


def load_data(path: Path | str = "数据.xlsx") -> pd.DataFrame:
    """Load survey data and add a ``target`` column derived from Q9.

    Mapping: Q9=1 → 0 (低频), Q9=2 → 1 (中频), Q9=3-6 → 2 (高频).
    """
    df = pd.read_excel(path)
    df["target"] = df[Q9_COL].map(_TARGET_MAP).astype(int)
    return df
