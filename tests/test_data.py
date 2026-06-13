"""Tests for data loading and target variable creation."""

from pathlib import Path

import pandas as pd
import pytest

from ralph.data import load_data

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
