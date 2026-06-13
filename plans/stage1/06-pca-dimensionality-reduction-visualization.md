## Parent

PRD: prd/aigc-usage-frequency-classification.md

## What to build

对特征矩阵进行 PCA 降维至 2D，生成按低/中/高三类着色的散点图。要求 PPT 级别质量：

- 中文字体支持（SimHei 或系统可用中文字体）
- 三类使用不同颜色，图例清晰
- 适当的点大小和透明度（避免重叠导致看不清分布）
- DPI ≥ 150，适合 PPT 直接使用

此图帮助研究者直观观察三类用户在降维空间中是否有明显的分离趋势。

## Acceptance criteria

- [ ] PCA 降维至 2 维完成
- [ ] 散点图按三类着色，颜色和图例清晰
- [ ] 中文字体正确显示（无方块字）
- [ ] 图表 DPI ≥ 150
- [ ] 图表保存为文件（PNG 或 PDF）

## Blocked by

- 05-modeling-pipeline-training-and-evaluation
