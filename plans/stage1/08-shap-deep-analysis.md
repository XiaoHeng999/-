## Parent

PRD: prd/aigc-usage-frequency-classification.md

## What to build

使用 SHAP 值对最优模型进行深度特征影响分析，生成两种可视化：

1. **SHAP Summary Plot**：展示所有特征对低频/中频/高频三类的影响方向和大小
2. **SHAP Waterfall / Bar Plot**：展示关键特征对预测的详细影响

要求 PPT 级别质量：
- 中文字体支持
- 特征名清晰可读
- 颜色含义明确（正值/负值，或高值/低值）
- DPI ≥ 150

此分析回答"哪些因素决定了使用频率的高低"这一核心研究问题。

## Acceptance criteria

- [ ] SHAP 值计算完成（基于最优模型）
- [ ] SHAP Summary Plot 生成，三类的影响方向清晰
- [ ] SHAP Waterfall / Bar Plot 生成，关键特征影响详细展示
- [ ] 所有图表 PPT 级别质量（中文标签、DPI ≥ 150）
- [ ] 图表保存为文件（PNG 或 PDF）

## Blocked by

- 05-modeling-pipeline-training-and-evaluation
