"""Tests for data loading, target variable creation, and data cleaning."""

from pathlib import Path

import pandas as pd
import pytest

from ralph.data import clean_data, load_data, map_major
from ralph.data import Q2_COL, Q3_COL

DATA_PATH = Path(__file__).resolve().parent.parent / "数据.xlsx"
Q9_COL = "9、您使用生成式人工智能的频率如何?  "

requires_data = pytest.mark.skipif(
    not DATA_PATH.exists(),
    reason="数据.xlsx not available (excluded from VCS)",
)


@requires_data
class TestDataShape:
    """Verify data loads with correct dimensions."""

    def test_shape_after_target_creation(self):
        """加载后应得到 1781 行 × 79 列（78 原始列 + 1 target 列）"""
        df = load_data(DATA_PATH)
        assert isinstance(df, pd.DataFrame)
        assert df.shape == (1781, 79)


@requires_data
class TestTargetDistribution:
    """Verify target column has the expected class counts."""

    EXPECTED_COUNTS = {0: 145, 1: 1315, 2: 321}

    def test_target_class_counts(self):
        """target 列的类别分布应为 低频=145, 中频=1315, 高频=321"""
        df = load_data(DATA_PATH)
        counts = df["target"].value_counts().sort_index().to_dict()
        assert counts == self.EXPECTED_COUNTS

    def test_target_values_in_valid_set(self):
        """target 列只能包含 {0, 1, 2}"""
        df = load_data(DATA_PATH)
        assert set(df["target"].unique()) == {0, 1, 2}

    def test_target_no_missing(self):
        """target 列不应有缺失值"""
        df = load_data(DATA_PATH)
        assert df["target"].isnull().sum() == 0


@requires_data
class TestCleanDataBasic:
    """Verify clean_data preserves row count and target column."""

    def test_preserves_row_count(self):
        """清洗后仍应保留 1781 行"""
        df = clean_data(load_data(DATA_PATH))
        assert len(df) == 1781

    def test_target_column_preserved(self):
        """清洗后 target 列仍存在且分布不变"""
        df = clean_data(load_data(DATA_PATH))
        assert "target" in df.columns
        counts = df["target"].value_counts().sort_index().to_dict()
        assert counts == {0: 145, 1: 1315, 2: 321}


@requires_data
class TestExcludedColumnsRemoved:
    """Verify all excluded columns are absent after cleaning."""

    METADATA_COLS = ["序号", "学校", "所用时间", "总分"]

    def test_metadata_columns_removed(self):
        """序号、学校、所用时间、总分应被移除"""
        df = clean_data(load_data(DATA_PATH))
        for col in self.METADATA_COLS:
            assert col not in df.columns, f"{col} should be removed"

    def test_q9_column_removed(self):
        """Q9 原始列应被移除（已编码为 target）"""
        df = clean_data(load_data(DATA_PATH))
        assert Q9_COL not in df.columns

    def test_q15_columns_removed(self):
        """Q15 全部列（目标泄漏）应被移除"""
        df = clean_data(load_data(DATA_PATH))
        q15_cols = [c for c in df.columns if c.startswith("15、")]
        assert q15_cols == [], f"Q15 columns should be removed, found: {q15_cols}"

    def test_q16_q17_q18_removed(self):
        """Q16（零方差）、Q17、Q18（开放文本）应被移除"""
        df = clean_data(load_data(DATA_PATH))
        for prefix in ("16、", "17、", "18、"):
            remaining = [c for c in df.columns if c.startswith(prefix)]
            assert remaining == [], f"{prefix}* columns should be removed: {remaining}"

    def test_q14_attention_check_removed(self):
        """Q14 注意力检测题应被移除"""
        df = clean_data(load_data(DATA_PATH))
        attention_cols = [c for c in df.columns if "比较同意" in c]
        assert attention_cols == [], f"Attention check should be removed: {attention_cols}"


@requires_data
class TestQ10NaNFill:
    """Verify Q10 NaN values are filled with 14."""

    def test_q10_no_nan_after_cleaning(self):
        """Q10 的 13 列在清洗后不应有 NaN"""
        df = clean_data(load_data(DATA_PATH))
        q10_cols = [c for c in df.columns if c.startswith("10、")]
        assert len(q10_cols) == 13, f"Expected 13 Q10 columns, got {len(q10_cols)}"
        for col in q10_cols:
            nan_count = df[col].isnull().sum()
            assert nan_count == 0, f"{col} still has {nan_count} NaN values"

    def test_q10_nan_filled_with_14(self):
        """Q10 原始 NaN 应被填充为 14"""
        raw = load_data(DATA_PATH)
        cleaned = clean_data(raw)
        q10_cols = [c for c in cleaned.columns if c.startswith("10、")]
        for col in q10_cols:
            raw_nan_mask = raw[col].isnull()
            if raw_nan_mask.any():
                assert (cleaned.loc[raw_nan_mask, col] == 14).all(), (
                    f"NaN in {col} should be filled with 14"
                )


class TestMapMajorUnit:
    """Unit tests for Q3 major mapping with synthetic data."""

    def _make_df(self, q2_vals, q3_vals):
        return pd.DataFrame({Q2_COL: q2_vals, Q3_COL: q3_vals})

    def test_benke_gongxue_to_like(self):
        """本科 Q2=1, Q3=8(工学) → 理科"""
        df = self._make_df([1], [8])
        result = map_major(df)
        assert result[Q3_COL].iloc[0] == "理科"

    def test_benke_wenke_mapping(self):
        """本科 Q2=1, Q3=5(文学) → 文科"""
        df = self._make_df([1], [5])
        result = map_major(df)
        assert result[Q3_COL].iloc[0] == "文科"

    def test_benke_other_mapping(self):
        """本科 Q2=1, Q3=14(其他专业) → 其他"""
        df = self._make_df([1], [14])
        result = map_major(df)
        assert result[Q3_COL].iloc[0] == "其他"

    def test_zhuanke_like_mapping(self):
        """专科 Q2=2, Q3=11(电子与信息) → 理科"""
        df = self._make_df([2], [11])
        result = map_major(df)
        assert result[Q3_COL].iloc[0] == "理科"

    def test_zhuanke_wenke_mapping(self):
        """专科 Q2=2, Q3=13(财经商贸) → 文科"""
        df = self._make_df([2], [13])
        result = map_major(df)
        assert result[Q3_COL].iloc[0] == "文科"

    def test_zhuanke_other_mapping(self):
        """专科 Q2=2, Q3=20(其他专业) → 其他"""
        df = self._make_df([2], [20])
        result = map_major(df)
        assert result[Q3_COL].iloc[0] == "其他"

    def test_boshi_uses_benke_system(self):
        """博士 Q2=3 应使用本科编码体系: Q3=8(工学) → 理科"""
        df = self._make_df([3], [8])
        result = map_major(df)
        assert result[Q3_COL].iloc[0] == "理科"

    def test_boshi_wenke_uses_benke_system(self):
        """博士 Q2=3 应使用本科编码体系: Q3=5(文学) → 文科"""
        df = self._make_df([3], [5])
        result = map_major(df)
        assert result[Q3_COL].iloc[0] == "文科"


@requires_data
class TestMapMajorRealData:
    """Integration tests for Q3 major mapping on real data."""

    def test_no_nan_after_mapping(self):
        """映射后 Q3 不应有缺失值"""
        df = map_major(load_data(DATA_PATH))
        assert df[Q3_COL].isnull().sum() == 0

    def test_all_values_valid(self):
        """映射后 Q3 只包含 文科/理科/其他"""
        df = map_major(load_data(DATA_PATH))
        assert set(df[Q3_COL].unique()) == {"文科", "理科", "其他"}

    def test_row_count_preserved(self):
        """映射后行数不变"""
        raw = load_data(DATA_PATH)
        mapped = map_major(raw)
        assert len(mapped) == len(raw)

    def test_benke_distribution(self):
        """本科 (Q2=1) 映射分布: 理科=732, 文科=322, 其他=47"""
        df = map_major(load_data(DATA_PATH))
        benke = df[df[Q2_COL] == 1]
        counts = benke[Q3_COL].value_counts().to_dict()
        assert counts == {"理科": 732, "文科": 322, "其他": 47}

    def test_zhuanke_distribution(self):
        """专科 (Q2=2) 映射分布: 理科=327, 文科=237, 其他=92"""
        df = map_major(load_data(DATA_PATH))
        zhuanke = df[df[Q2_COL] == 2]
        counts = zhuanke[Q3_COL].value_counts().to_dict()
        assert counts == {"理科": 327, "文科": 237, "其他": 92}
