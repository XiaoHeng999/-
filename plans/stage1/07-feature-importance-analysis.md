## Parent

PRD: prd/aigc-usage-frequency-classification.md

## What to build

使用两种方法进行特征重要性分析，各生成 Top 15 特征的水平柱状图：

1. **随机森林特征重要性**：基于训练好的随机森林模型的 `feature_importances_`，取 Top 15 特征
2. **Permutation Importance**：在测试集上计算，取 Top 15 特征，提供最稳健的特征重要性指标

两图均要求 PPT 级别质量：
- 水平柱状图，特征名从上到下按重要性排序
- 中文字体支持、清晰标签
- DPI ≥ 150

## Acceptance criteria

- [ ] 随机森林 Top 15 特征重要性水平柱状图生成
- [ ] Permutation Importance Top 15 特征水平柱状图生成
- [ ] 两张图表均为 PPT 级别质量（中文标签、清晰配色、DPI ≥ 150）
- [ ] 图表保存为文件（PNG 或 PDF）

## Blocked by

- 05-modeling-pipeline-training-and-evaluation
