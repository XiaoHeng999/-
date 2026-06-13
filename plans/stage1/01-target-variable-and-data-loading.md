## Parent

PRD: prd/aigc-usage-frequency-classification.md

## What to build

从 `数据.xlsx` 加载原始问卷数据（1781 行 × 78 列），将 Q9 的 6 级原始选项归并为"低频 / 中频 / 高频"三分类目标变量。具体映射规则：

- **低频**（label=0）：Q9 编码 1（从未使用）→ 145 人 (8.1%)
- **中频**（label=1）：Q9 编码 2（一周 1~10 次）→ 1315 人 (73.8%)
- **高频**（label=2）：Q9 编码 3~6（一周 11 次以上）→ 321 人 (18.0%)

完成后应得到一个 DataFrame，包含原始列 + 新增的 `target` 列（值为 0/1/2），可供后续清洗和特征工程使用。

## Acceptance criteria

- [ ] 成功从 `数据.xlsx` 加载数据，形状为 (1781, 78)
- [ ] `target` 列正确创建：低频 145 人、中频 1315 人、高频 321 人
- [ ] `target` 列值为 {0, 1, 2}，无缺失值
- [ ] 单元测试通过：验证数据形状、target 分布、无空值

## Blocked by

None — can start immediately
