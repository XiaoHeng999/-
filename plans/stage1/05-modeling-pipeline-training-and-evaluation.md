## Parent

PRD: prd/aigc-usage-frequency-classification.md

## What to build

构建完整的建模 Pipeline，从特征矩阵到模型评估。核心流程：

1. **80/20 Stratified Split**：确保训练集和测试集的低/中/高比例一致
2. **SMOTE 过采样**：嵌在 imblearn Pipeline 内部，仅在训练集上执行，5 折 CV 中每个 fold 独立执行
3. **6 个模型训练 + 5 折交叉验证**：
   - KNN（K-近邻）
   - 决策树
   - 随机森林
   - SVM（支持向量机）
   - 朴素贝叶斯
   - Logistic 回归
4. **评估指标**：
   - 主指标：Macro F1
   - 辅助指标：每个类别的 Precision / Recall / F1、Weighted F1（参考）
5. **混淆矩阵**：每个模型的混淆矩阵
6. **模型对比柱状图**：6 个模型的 Macro F1 对比，PPT 级别（中文标签、清晰配色、DPI ≥ 150）

测试集始终保持原始不平衡分布，SMOTE 绝不接触测试集。

## Acceptance criteria

- [ ] 数据按 80/20 stratified split 划分，训练/测试集类别比例一致
- [ ] SMOTE 仅在训练集 Pipeline 内执行，测试集未被过采样
- [ ] 6 个模型均完成训练和 5 折交叉验证
- [ ] 输出每个模型的 Macro F1、每类 Precision/Recall/F1
- [ ] 输出每个模型的混淆矩阵
- [ ] 生成 6 模型 Macro F1 对比柱状图（PPT 质量）
- [ ] Pipeline 完整性测试通过：验证 SMOTE 不污染测试集

## Blocked by

- 04-feature-encoding-and-aggregation
