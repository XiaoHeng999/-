# Stage 1: 大学生 AIGC 使用频率分类模型

## 任务总览

| # | 任务 | 类型 | 状态 | 依赖 |
|---|------|------|------|------|
| 01 | [目标变量创建与数据加载](01-target-variable-and-data-loading.md) | AFK | pending | — |
| 02 | [数据清洗与列排除](02-data-cleaning-and-column-exclusion.md) | AFK | pending | 01 |
| 03 | [Q3 专业映射](03-q3-major-mapping.md) | AFK | pending | 02 |
| 04 | [特征编码与聚合](04-feature-encoding-and-aggregation.md) | AFK | pending | 03 |
| 05 | [建模 Pipeline — 训练与评估](05-modeling-pipeline-training-and-evaluation.md) | AFK | pending | 04 |
| 06 | [PCA 降维可视化](06-pca-dimensionality-reduction-visualization.md) | AFK | pending | 05 |
| 07 | [特征重要性分析 (RF + Permutation)](07-feature-importance-analysis.md) | AFK | pending | 05 |
| 08 | [SHAP 深度分析](08-shap-deep-analysis.md) | AFK | pending | 05 |

## 依赖关系图

```
01 → 02 → 03 → 04 → 05 → 06 (PCA 可视化)
                         ├→ 07 (特征重要性)
                         └→ 08 (SHAP 分析)
```

- 01~05 为线性依赖链
- 06、07、08 在 05 完成后可并行执行

## 状态说明

- **pending**：未开始，等待依赖完成
- **doing**：正在进行中
- **done**：已完成

实时状态见 `state.json`。
