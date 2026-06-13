# Stage 2: 实验执行、超参数调优与因子分析

## 背景

Stage 1 已完成全部基础模块：
- `src/data.py` — 数据加载、清洗、专业映射、特征编码
- `src/model.py` — 6 分类器 + SMOTE 管线、训练评估、模型对比图
- `src/importance.py` — RF 特征重要性 + Permutation 重要性
- `src/pca.py` — PCA 降维 + 2D 散点图
- `src/shap_analysis.py` — SHAP 值计算 + 柱状图/汇总图/蜂群图

**当前问题**：`main.py` 为占位符（仅打印 Hello），所有模型使用默认超参数，无统一实验入口，结果未持久化。

**Stage 2 目标**：
1. 编写实验入口函数，串联全流程
2. 多模型对比实验 + 可视化
3. 单模型超参数调优对比实验 + 可视化
4. 因子重要性分析（跨方法对比 + 共识排名）+ 可视化
5. 所有结果保存到 `results/` 文件夹

---

## 任务依赖关系

```
Task 01 (工具模块与目录)
  └→ Task 02 (main.py 骨架)
       └→ Task 03 (实验 1: 多模型对比)
            └→ Task 04 (main.py 接入实验 1)
                 ├→ Task 05 (实验 2: 超参数调优)  ──┐
                 ├→ Task 06 (实验 3: 因子分析)     ──┤ 可并行
                 └──────────────────────────────────┘
                       └→ Task 07 (main.py 接入全部 + PCA)
                            └→ Task 08 (端到端验证与汇总)
```

Task 05 和 Task 06 可并行开发（都依赖 Task 04，互不依赖）。

---

## Task 01: 工具模块与结果目录结构

### 目标
创建 `src/utils.py` 工具模块，初始化 `results/` 目录结构，更新 `.gitignore`

### 具体内容

**新建 `src/utils.py`**：
- `ensure_results_dirs()` — 创建 `results/` 完整目录树，返回根路径 `Path`
- `save_metrics_csv(metrics_dict, path)` — 将结果字典扁平化为 CSV（每行一个模型）
- `print_experiment_header(name)` — 格式化打印实验进度标题

**目录结构**：
```
results/
├── model_comparison/
│   └── confusion_matrices/
├── hyperparameter_tuning/
│   ├── random_forest/
│   ├── svm/
│   ├── knn/
│   └── decision_tree/
├── factor_analysis/
└── pca/
```

**修改 `.gitignore`**：添加 `results/`

**测试**：新建 `tests/test_utils.py`
- 使用 `tmp_path` 测试目录创建
- 测试 CSV 导出功能
- 测试打印函数不抛异常

### 涉及文件
- 新建：`src/utils.py`、`tests/test_utils.py`
- 修改：`.gitignore`

---

## Task 02: main.py 编排骨架

### 目标
重写 `main.py` 为实验编排器，串联数据准备与各实验函数

### 具体内容

**`main()` 函数流程**：
1. 调用数据管线：`load_data()` → `clean_data()` → `map_major()` → `encode_features()`
2. 调用 `split_data(df)` 获取 `X_train, X_test, y_train, y_test`
3. 获取 `feature_names = X_train.columns.tolist()`
4. 调用 `ensure_results_dirs()`
5. 依次调用各实验函数（Task 03-06 中实现，此处先定义为空壳）
6. 打印最终汇总

**更新测试**：
- `tests/test_main.py` — 验证 `main()` 可正常执行
- `tests/test_e2e/test_pipeline.py` — 更新端到端测试

### 涉及文件
- 修改：`main.py`、`tests/test_main.py`、`tests/test_e2e/test_pipeline.py`

---

## Task 03: 实验 1 — 多模型对比实验

### 目标
运行全部 6 个模型，生成全面的性能对比图表和指标 CSV

### 具体内容

**新建 `src/experiments.py`**，实现 `run_model_comparison()`

**复用已有函数**：
- `src/model.py:build_pipelines()` — 构建 6 个 SMOTE 管线
- `src/model.py:train_and_evaluate()` — 训练 + 评估（返回 CV 分数、Macro F1、每类 Precision/Recall/F1、混淆矩阵）
- `src/model.py:plot_model_comparison()` — F1 对比柱状图

**新增可视化函数**：

| 函数 | 说明 |
|------|------|
| `_plot_per_class_metrics(results, save_path)` | 3 类别 × 6 模型分组柱状图，展示 Precision/Recall/F1 |
| `_plot_confusion_matrix(cm, model_name, class_names, save_path)` | 单模型混淆矩阵热力图（seaborn.heatmap） |
| `_plot_cv_boxplot(results, save_path)` | 6 模型 5-fold CV 分数箱线图 |

**输出文件**：
```
results/model_comparison/
├── metrics_summary.csv           — 所有指标汇总表
├── model_comparison_f1.png       — Macro F1 柱状图
├── per_class_metrics.png         — 分类别指标对比
├── cv_boxplot.png                — CV 分数箱线图
└── confusion_matrices/
    ├── knn_cm.png
    ├── decision_tree_cm.png
    ├── random_forest_cm.png
    ├── svm_cm.png
    ├── naive_bayes_cm.png
    └── logistic_regression_cm.png
```

**返回值**：`(results_dict, pipelines_dict)` — 供后续实验复用已拟合的管线

**中文模型名 → 英文文件名映射**：
```python
_NAME_MAP = {
    "KNN": "knn",
    "决策树": "decision_tree",
    "随机森林": "random_forest",
    "SVM": "svm",
    "朴素贝叶斯": "naive_bayes",
    "Logistic回归": "logistic_regression",
}
```

**测试**：新建 `tests/test_experiments.py`
- 合成数据测试所有新可视化函数
- 验证 `metrics_summary.csv` 输出格式正确

### 涉及文件
- 新建：`src/experiments.py`、`tests/test_experiments.py`

---

## Task 04: main.py 接入实验 1

### 目标
将 `run_model_comparison()` 接入 `main.py`，替换空壳

### 具体内容
- `main.py` 调用 `run_model_comparison(X_train, X_test, y_train, y_test, feature_names)`
- 保存返回的 `(results, pipelines)` 供后续实验使用
- 更新 e2e 测试验证 `results/model_comparison/` 文件生成

### 涉及文件
- 修改：`main.py`、`tests/test_e2e/test_pipeline.py`

---

## Task 05: 实验 2 — 超参数调优实验

### 目标
对 4 个关键模型进行 GridSearchCV 超参数搜索，生成调优报告和可视化

### 具体内容

**在 `src/experiments.py` 中添加 `run_hyperparameter_tuning()`**

**调优模型与参数网格**（均用 `ImbPipeline([("smote", SMOTE(...)), ("clf", ...)])` 包裹）：

#### 随机森林（54 组合 × 5 折 = 270 fits）
| 参数 | 候选值 |
|------|--------|
| `n_estimators` | [100, 200, 300] |
| `max_depth` | [10, 20, None] |
| `min_samples_split` | [2, 5, 10] |
| `max_features` | ['sqrt', 'log2'] |

#### SVM（16 组合 × 5 折 = 80 fits）
| 参数 | 候选值 |
|------|--------|
| `C` | [0.1, 1, 10, 100] |
| `kernel` | ['rbf', 'linear'] |
| `gamma` | ['scale', 'auto'] |

#### KNN（20 组合 × 5 折 = 100 fits）
| 参数 | 候选值 |
|------|--------|
| `n_neighbors` | [3, 5, 7, 9, 11] |
| `weights` | ['uniform', 'distance'] |
| `metric` | ['euclidean', 'manhattan'] |

#### 决策树（32 组合 × 5 折 = 160 fits）
| 参数 | 候选值 |
|------|--------|
| `max_depth` | [5, 10, 20, None] |
| `min_samples_split` | [2, 5, 10, 20] |
| `criterion` | ['gini', 'entropy'] |

**GridSearchCV 配置**：`cv=5, scoring='f1_macro', n_jobs=-1, refit=True`

**新增可视化函数**：

| 函数 | 说明 |
|------|------|
| `_plot_tuning_heatmap(cv_results_df, param_x, param_y, save_path)` | 两参数 Macro F1 热力图 |
| `_plot_tuning_line(cv_results_df, param_name, save_path)` | 单参数 Macro F1 折线图 |

**每个模型输出**：
```
results/hyperparameter_tuning/{model}/
├── best_params.txt          — 最优参数及得分
├── tuning_results.csv       — 全部搜索结果
├── heatmap_*.png            — 两参数热力图
└── line_*.png               — 单参数折线图
```

**汇总文件**：`results/hyperparameter_tuning/summary.csv` — 4 模型最优结果对比

**测试**：合成数据 + 缩小网格（2 值）验证

### 涉及文件
- 修改：`src/experiments.py`、`tests/test_experiments.py`

---

## Task 06: 实验 3 — 因子重要性分析

### 目标
综合 RF、Permutation、SHAP 三种方法，生成跨方法对比和共识排名

### 具体内容

**在 `src/experiments.py` 中添加 `run_factor_analysis()`**

**复用已有函数**：
- `src/importance.py:compute_rf_importance()` — RF 特征重要性
- `src/importance.py:compute_permutation_importance()` — 置换重要性
- `src/importance.py:plot_rf_importance()`、`plot_permutation_importance()` — 柱状图
- `src/shap_analysis.py:compute_shap_values()` — SHAP 值计算
- `src/shap_analysis.py:plot_shap_bar()`、`plot_shap_summary()`、`plot_shap_beeswarm()`

**新增功能**：

1. **三分类 SHAP 柱状图**
   - 对 `class_idx=0,1,2` 各调用 `plot_shap_bar()`
   - 分别对应"低频"、"中频"、"高频"

2. **跨方法对比图** `_plot_cross_method_comparison(rf_df, perm_df, shap_df, save_path)`
   - 水平分组柱状图
   - 每个特征 3 根柱子（RF / Permutation / SHAP）
   - 各方法重要性归一化到 [0, 1]
   - 显示出现在任一方法 Top-15 中的全部特征

3. **共识排名** `_compute_consensus_ranking(rf_df, perm_df, shap_df)`
   - 三方法各自 Top-15 特征赋予排名 1-15
   - 未入选特征赋予惩罚排名 16
   - 对每个特征取三方法排名的平均值
   - 按平均排名升序排列，输出 Top-15
   - 返回 DataFrame：`["feature", "rf_rank", "perm_rank", "shap_rank", "mean_rank"]`

**输出文件**：
```
results/factor_analysis/
├── rf_importance.png              — RF 特征重要性柱状图
├── permutation_importance.png     — Permutation 重要性柱状图
├── shap_bar_low.png              — 低频类 SHAP 柱状图 (class_idx=0)
├── shap_bar_medium.png           — 中频类 SHAP 柱状图 (class_idx=1)
├── shap_bar_high.png             — 高频类 SHAP 柱状图 (class_idx=2)
├── shap_summary.png              — 全类别 SHAP 汇总
├── shap_beeswarm.png             — 高频类 SHAP 蜂群图
├── cross_method_comparison.png   — 跨方法对比图
└── consensus_ranking.csv         — 共识排名表
```

**测试**：
- `_compute_consensus_ranking()` 单元测试（合成 DataFrame）
- 合成数据测试 `_plot_cross_method_comparison()`

### 涉及文件
- 修改：`src/experiments.py`、`tests/test_experiments.py`

---

## Task 07: main.py 接入全部实验 + PCA

### 目标
将超参数调优、因子分析、PCA 全部接入 `main.py`，完成端到端可运行管线

### 具体内容

**`main.py` 完整流程**：
```python
def main():
    # 1. 数据准备
    df = load_data()
    df = clean_data(df)
    df = map_major(df)
    df = encode_features(df)

    X_train, X_test, y_train, y_test = split_data(df)
    feature_names = X_train.columns.tolist()

    # 2. 初始化结果目录
    ensure_results_dirs()

    # 3. 实验 1: 多模型对比
    results, pipelines = run_model_comparison(X_train, X_test, y_train, y_test, feature_names)

    # 4. 实验 2: 超参数调优
    run_hyperparameter_tuning(X_train, X_test, y_train, y_test, feature_names)

    # 5. 实验 3: 因子分析
    run_factor_analysis(pipelines, X_train, X_test, y_train, y_test, feature_names)

    # 6. PCA 可视化
    X_reduced, evr = reduce_pca(X_train)
    plot_pca_scatter(X_reduced, y_train, save_path="results/pca/pca_scatter.png")
```

**更新 e2e 测试**：验证完整 `results/` 目录结构

### 涉及文件
- 修改：`main.py`、`tests/test_e2e/test_pipeline.py`

---

## Task 08: 端到端验证与结果汇总

### 目标
运行完整管线，验证所有输出文件，生成实验总结

### 具体内容

1. **执行** `uv run python main.py` 完整运行
2. **验证** `results/` 下所有预期文件存在且非空
3. **生成** `results/experiment_summary.txt` 包含：
   - 各模型 Macro F1 排名
   - 最优模型及超参数
   - Top-10 关键影响因素（共识排名）
   - PCA 解释方差比例
4. **创建** `plans/stage2/state.json` 标记所有任务完成
5. **最终 commit**

### 涉及文件
- 新建：`plans/stage2/state.json`、`results/experiment_summary.txt`

---

## 完整结果目录结构

```
results/
├── experiment_summary.txt
├── model_comparison/
│   ├── metrics_summary.csv
│   ├── model_comparison_f1.png
│   ├── per_class_metrics.png
│   ├── cv_boxplot.png
│   └── confusion_matrices/
│       ├── knn_cm.png
│       ├── decision_tree_cm.png
│       ├── random_forest_cm.png
│       ├── svm_cm.png
│       ├── naive_bayes_cm.png
│       └── logistic_regression_cm.png
├── hyperparameter_tuning/
│   ├── summary.csv
│   ├── random_forest/
│   │   ├── best_params.txt
│   │   ├── tuning_results.csv
│   │   ├── heatmap_n_estimators_vs_max_depth.png
│   │   └── line_n_estimators.png
│   ├── svm/
│   │   ├── best_params.txt
│   │   ├── tuning_results.csv
│   │   ├── heatmap_C_vs_gamma.png
│   │   └── line_C.png
│   ├── knn/
│   │   ├── best_params.txt
│   │   ├── tuning_results.csv
│   │   ├── heatmap_n_neighbors_vs_weights.png
│   │   └── line_n_neighbors.png
│   └── decision_tree/
│       ├── best_params.txt
│       ├── tuning_results.csv
│       ├── heatmap_max_depth_vs_min_samples_split.png
│       └── line_max_depth.png
├── factor_analysis/
│   ├── rf_importance.png
│   ├── permutation_importance.png
│   ├── shap_bar_low.png
│   ├── shap_bar_medium.png
│   ├── shap_bar_high.png
│   ├── shap_summary.png
│   ├── shap_beeswarm.png
│   ├── cross_method_comparison.png
│   └── consensus_ranking.csv
└── pca/
    └── pca_scatter.png
```

---

## 实现约定

1. **绘图风格**：`matplotlib.use("Agg")`，中文字体 `["Arial Unicode MS", "SimHei", "PingFang SC"]`，`dpi=200`，`bbox_inches="tight"`，保存后 `plt.close(fig)`
2. **SMOTE 纪律**：所有超参数调优必须包裹在 `ImbPipeline` 中，参数名前缀 `clf__`
3. **测试模式**：合成数据 + `@requires_data` 装饰器 + `tmp_path` + DPI ≥ 150 断言
4. **返回类型**：
   - `run_model_comparison()` → `(results_dict, pipelines_dict)`
   - `run_hyperparameter_tuning()` → `dict[str, dict]`
   - `run_factor_analysis()` → `DataFrame`（共识排名）

---

## 验证清单

| 验证项 | 命令 |
|--------|------|
| 单元测试 | `uv run pytest tests/ -x` |
| 端到端运行 | `uv run python main.py` |
| 文件完整性 | 检查 `results/` 目录所有预期文件存在且非空 |
| 代码质量 | `uv run ruff check src/ tests/` |
| CI | `gh run watch` |
