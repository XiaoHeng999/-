"""Load raw survey data, create target variable, and clean features."""

from pathlib import Path

import pandas as pd

Q9_COL = "9、您使用生成式人工智能的频率如何?  "

_TARGET_MAP = {1: 0, 2: 1, 3: 2, 4: 2, 5: 2, 6: 2}

# Columns to drop — metadata / leakage / low-value / open-text
_EXCLUDED_COLUMNS = [
    "序号",
    "学校",
    "所用时间",
    "总分",
    Q9_COL,
    "16、您认为大学生该不该使用生成式人工智能?  ",
    "17、对于大学生使用生成式人工智能，您有什么意见或建议?  ",
    "18、对于高校如何监管大学生使用生成式人工智能，您有什么意见或建议?  ",
]

# Attention-check keyword — the Q14 column containing "比较同意"
_ATTENTION_KEYWORD = "比较同意"

_Q10_NAN_FILL = 14

Q2_COL = "2、您的学历:  "
Q3_COL = "3、您的专业  "

# 本科 (Q2=1) / 博士 (Q2=3) major → category mapping
_BENKE_LIKE = {7, 8, 9, 10}  # 理学, 工学, 农学, 医学
_BENKE_WEN = {1, 2, 3, 4, 5, 6, 11, 12, 13}  # 哲学~心理学

# 专科 (Q2=2) major → category mapping
_ZHUANKE_LIKE = set(range(1, 13))  # codes 1-12
_ZHUANKE_WEN = set(range(13, 20))  # codes 13-19


def load_data(path: Path | str = "数据.xlsx") -> pd.DataFrame:
    """Load survey data and add a ``target`` column derived from Q9.

    Mapping: Q9=1 → 0 (低频), Q9=2 → 1 (中频), Q9=3-6 → 2 (高频).
    """
    df = pd.read_excel(path)
    df["target"] = df[Q9_COL].map(_TARGET_MAP).astype(int)
    return df


def _find_attention_check(columns: pd.Index) -> str | None:
    """Return the Q14 attention-check column name, or None."""
    for col in columns:
        if col.startswith("14、") and _ATTENTION_KEYWORD in col:
            return col
    return None


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Remove non-feature columns, fill Q10 NaN, return cleaned DataFrame.

    Operations (in order):
    1. Drop metadata columns (序号, 学校, 所用时间, 总分)
    2. Drop Q9 (already encoded as ``target``)
    3. Drop Q15 columns (target leakage)
    4. Drop Q16 (near-zero variance), Q17/Q18 (open text)
    5. Drop Q14 attention-check column
    6. Fill Q10 NaN with 14 (meaning "not used")
    """
    df = df.copy()

    # Collect all columns to drop
    to_drop = [c for c in _EXCLUDED_COLUMNS if c in df.columns]
    to_drop += [c for c in df.columns if c.startswith("15、")]
    # Drop Q14 attention-check column (contains "比较同意")
    attention_col = _find_attention_check(df.columns)
    if attention_col:
        to_drop.append(attention_col)

    df.drop(columns=to_drop, inplace=True)

    # Fill Q10 NaN
    q10_cols = [c for c in df.columns if c.startswith("10、")]
    df[q10_cols] = df[q10_cols].fillna(_Q10_NAN_FILL)

    return df


def map_major(df: pd.DataFrame) -> pd.DataFrame:
    """Map Q3 (专业) to 文科/理科/其他 based on Q2 (学历) encoding system.

    - 本科 (Q2=1) and 博士 (Q2=3): use 本科编码体系
    - 专科 (Q2=2): use 专科编码体系
    """
    df = df.copy()

    result = pd.Series("其他", index=df.index, name=Q3_COL)

    benke_mask = df[Q2_COL].isin([1, 3])
    like_benke = benke_mask & df[Q3_COL].isin(_BENKE_LIKE)
    wen_benke = benke_mask & df[Q3_COL].isin(_BENKE_WEN)

    zhuanke_mask = df[Q2_COL] == 2
    like_zhuanke = zhuanke_mask & df[Q3_COL].isin(_ZHUANKE_LIKE)
    wen_zhuanke = zhuanke_mask & df[Q3_COL].isin(_ZHUANKE_WEN)

    result[like_benke] = "理科"
    result[wen_benke] = "文科"
    result[like_zhuanke] = "理科"
    result[wen_zhuanke] = "文科"

    df[Q3_COL] = result
    return df
