# 大学生生成式AI使用频率影响因素研究 - Design Spec

> Human-readable design narrative — rationale, audience, style, color choices, content outline.
>
> Machine-readable execution contract: `spec_lock.md`. Executor re-reads `spec_lock.md` before every SVG page. Keep both in sync; on divergence, `spec_lock.md` wins.

## I. Project Information

| Item | Value |
| ---- | ----- |
| **Project Name** | aigc_usage_classification |
| **Canvas Format** | PPT 16:9 (1280×720) |
| **Page Count** | 14 |
| **Design Style** | pyramid（结论先行）+ data-journalism（数据新闻质感） |
| **Target Audience** | 模式识别课程答辩老师与同学（学术研究汇报场景） |
| **Use Case** | 课程大作业答辩 / 学术研究汇报 —— 重数据、重严谨、结论先行 |
| **Created Date** | 2026-06-17 |

---

## II. Canvas Specification

| Property | Value |
| -------- | ----- |
| **Format** | PPT 16:9 |
| **Dimensions** | 1280×720 |
| **viewBox** | `0 0 1280 720` |
| **Margins** | 左右 60px，上下 48px |
| **Content Area** | 1160×624（页眉标题区高约 96px，正文区高约 480px，页脚区高约 40px） |

---

## III. Visual Theme

### Theme Style

- **Mode**: pyramid —— 结论先行叙事：每页标题即结论（断言句），正文给出支撑证据；SCQA 开场（背景→张力→问题→答案），正文 MECE 分解。
- **Visual style**: data-journalism —— Bloomberg / Economist 数据新闻质感：多列网格、内嵌微图表、数据表、编辑性侧栏、来源行、hero 数字、发丝分隔线；密度高但靠严格网格保持可读。冷调克制，像财经长读而非 Keynote。
- **Theme**: Light theme（象牙白纸感底，数据图表为王）
- **Tone**: 沉稳、权威、严谨、可读 —— 传统学术答辩气质

### Color Scheme

> 经典研究红蓝（用户确认 `result.json`）。深蓝主色 + 研究红强调，象牙白底，权威庄重。data-journalism 需要分层面板/网格，故额外锁定 surface / grid 两级中性色（见末两行）。数字"按含义着色"（正向绿 / 风险红 / 焦点蓝），不作装饰。

| Role | HEX | Purpose |
| ---- | --- | ------- |
| **Background** | `#FFFFFF` | 页面底色（白纸） |
| **Secondary bg** | `#F3F1EC` | 面板/分区底（象牙） |
| **Primary** | `#1A3C6E` | 标题装饰、关键区块、主轴线、一级强调（深海军蓝） |
| **Accent** | `#B11226` | 数据高亮 / 关键数字 / 风险标记 / 链接（研究红） |
| **Secondary accent** | `#5B7DB1` | 次级强调、第二数据系列、渐变过渡（中蓝） |
| **Body text** | `#23262B` | 正文主文字 |
| **Secondary text** | `#56606B` | 说明文字、轴标签 |
| **Tertiary text** | `#8C949D` | 页码、脚注、来源行 |
| **Surface** | `#FAF8F3` | 面板内卡片抬升层（浅象牙） |
| **Grid** | `#E8E3D6` | 表格行分隔、发丝网格线（比 divider 更浅） |
| **Border/divider** | `#D4D0C4` | 卡片边框、分隔线 |
| **Success** | `#2E7D32` | 正向指标（绿系，最优模型/提升） |
| **Warning** | `#C77700` | 注意/局限/警告（琥珀，区别于研究红） |

> **注**：嵌入的用户图表（matplotlib PNG）保留其原始配色（蓝/橙/绿等），作为数据图原样呈现，不强制套色——这是数据真实性的体现。SVG 原生元素（标题、卡片、表格、原生图表）严格使用上表配色。

### Gradient Scheme

```xml
<!-- 标题/强调渐变：深蓝→中蓝 -->
<linearGradient id="titleGradient" x1="0%" y1="0%" x2="100%" y2="0%">
  <stop offset="0%" stop-color="#1A3C6E"/>
  <stop offset="100%" stop-color="#5B7DB1"/>
</linearGradient>

<!-- 封面/章节背景装饰（无 rgba，用 stop-opacity） -->
<radialGradient id="bgDecor" cx="85%" cy="15%" r="55%">
  <stop offset="0%" stop-color="#1A3C6E" stop-opacity="0.12"/>
  <stop offset="100%" stop-color="#1A3C6E" stop-opacity="0"/>
</radialGradient>
```

---

## IV. Typography System

### Font Plan

> **Typography direction**: 现代无衬线（一致）—— 全文微软雅黑 + Arial，靠字重（Bold / Regular）区分标题与正文，干净现代，数据表格与数字可读性最佳，PPT 全平台安全。

| Role | Chinese | English | Fallback tail |
| ---- | ------- | ------- | ------------- |
| **Title** | `"Microsoft YaHei"`, `"PingFang SC"` | `Arial` | `sans-serif` |
| **Body** | `"Microsoft YaHei"`, `"PingFang SC"` | `Arial` | `sans-serif` |
| **Emphasis** | 同 Body（靠字重 + 研究红着色强调） | `Arial` | `sans-serif` |
| **Code** | — | `Consolas`, `"Courier New"` | `monospace`（超参数 / 技术名） |

**Per-role font stacks**（CSS `font-family` 字符串）:

- Title: `"Microsoft YaHei","PingFang SC",Arial,sans-serif`
- Body: `"Microsoft YaHei","PingFang SC",Arial,sans-serif`
- Emphasis: same as Body（不单独覆写，靠 weight + color）
- Code: `Consolas,"Courier New",monospace`

### Font Size Hierarchy

**Baseline**: Body font size = **18px**（dense 密度 —— 数据报告/答辩，6+ 信息点/页）

| Purpose | Ratio | px @ body=18 | Weight |
| ------- | ----- | ------------ | ------ |
| Cover title（封面主标题） | 2.5-5x | 64 | Bold/Heavy |
| Chapter / section opener | 2-2.5x | 40 | Bold |
| Page title（页标题=结论） | 1.5-2x | 32 | Bold |
| Hero number（hero 大数字） | 2.2-2.7x | 40-48 | Bold |
| Subtitle | 1.2-1.5x | 22 | SemiBold |
| **Body content** | **1x** | **18** | Regular |
| Annotation / caption | 0.7-0.85x | 13 | Regular |
| Page number / footnote | 0.5-0.65x | 11 | Regular |

---

## V. Layout Principles

### Page Structure

- **Header area**: 高 ~96px —— 页标题（结论句，32px Bold，深蓝）+ 标题下 4px 研究红短色条；左上角可选小图标
- **Content area**: 高 ~480px —— 正文/图表/表格主体；多列网格或非对称分栏
- **Footer area**: 高 ~40px —— 左：来源/数据说明（11px 灰）；右：页码 `NN / 14`（11px 灰）；顶部 1px 发丝分隔线 `#D4D0C4`

### Layout Pattern Library（按信息权重组合，不套用固定菜单）

| Pattern | 本deck使用页 |
| ------- | --------- |
| **Single column centered** | P01 封面、P14 致谢 |
| **Negative-space-driven** | P02 研究背景（单一核心问题）、P12 PCA 结论 |
| **Asymmetric split (3:7 / 2:8)** | P10/P11 图表 hero + 注释列 |
| **Top-bottom split** | P10 顶部宽图 + 底部原生条形 |
| **Two/three column cards** | P03 KPI 总览（2×2）、P06 方法流水线 |
| **Matrix grid (2×2)** | P07/P08/P09 双图诊断面板 |
| **Table layout** | P04 特征构成、P05 标签映射与清洗、P09 最优超参 |

### Spacing Specification

**Universal**:

| Element | Range | Current |
| ------- | ----- | ------- |
| 画布安全边距 | 40-60px | 60px |
| 内容块间距 | 24-40px | 32px |
| 图标-文字间距 | 8-16px | 12px |

**Card-based**:

| Element | Range | Current |
| ------- | ----- | ------- |
| 卡片间距 | 20-32px | 24px |
| 卡片内边距 | 20-32px | 24px |
| 卡片圆角 | 8-16px | 10px |
| 双列卡片宽 | — | ~560px each |

---

## VI. Icon Usage Specification

### Source

- **图标库**: `tabler-outline`（线性图标，与 data-journalism 干净风格一致；全deck单一库，禁止混用）
- **stroke-width**: `2`（deck-wide 锁定）
- **用法**: `<use data-icon="tabler-outline/<name>" .../>`，颜色随父级 `stroke` / `fill`。

### Recommended Icon List

| Purpose | Icon Path | Page |
| ------- | --------- | ---- |
| 生成式AI主题 | `tabler-outline/robot` | P01, P02 |
| 闪光/高频 | `tabler-outline/sparkles` | P02 |
| 学生群体 | `tabler-outline/users` | P02, P04 |
| 最优模型/冠军 | `tabler-outline/trophy` | P03, P07 |
| 目标/分类 | `tabler-outline/target` | P03, P04 |
| 关键因子/堆叠 | `tabler-outline/stack-2` | P03, P10 |
| 图表条 | `tabler-outline/chart-bar` | P03, P07 |
| 趋势上升 | `tabler-outline/trending-up` | P09 |
| 警示/局限 | `tabler-outline/alert-triangle` | P03, P08, P13 |
| 数据库 | `tabler-outline/database` | P04 |
| 剪贴板数据 | `tabler-outline/clipboard-data` | P04 |
| 过滤/清洗 | `tabler-outline/filter` | P05 |
| 标签 | `tabler-outline/tags` | P05 |
| 实验瓶 | `tabler-outline/flask` | P06 |
| 调节/超参 | `tabler-outline/adjustments` | P06, P09 |
| 缩放/管线 | `tabler-outline/git-branch` | P06 |
| 天平/对比 | `tabler-outline/scale` | P06 |
| 剪贴板勾选 | `tabler-outline/clipboard-check` | P06 |
| 搜索/诊断 | `tabler-outline/search` | P08 |
| 听诊器 | `tabler-outline/stethoscope` | P08 |
| 编号列表/排名 | `tabler-outline/list-numbers` | P10 |
| 闪电/强信号 | `tabler-outline/bolt` | P10 |
| 显微/可解释 | `tabler-outline/microscope` | P11 |
| 灯泡/洞察 | `tabler-outline/bulb` | P11, P13 |
| 散点/聚焦 | `tabler-outline/focus-2` | P12 |
| 勾选/结论 | `tabler-outline/circle-check` | P13 |
| 旗帜/启示 | `tabler-outline/flag` | P13 |
| 感谢/微笑 | `tabler-outline/mood-smile` | P14 |
| 心形/致谢 | `tabler-outline/heart` | P14 |

---

## VII. Visualization Reference List

Catalog read: 71 templates

| Page | Template | Path | Summary-quote (verbatim) | Usage |
| ---- | -------- | ---- | ------------------------ | ----- |
| P03 | kpi_cards | `templates/charts/kpi_cards.svg` | "Pick for 4-8 standalone numeric metrics shown as overview cards (2x2 or 1x4) — exec summary opener, dashboard headline, quarterly recap, results-at-a-glance. Skip if metrics have target baselines (use bullet_chart) or single hero number (use gauge_chart)." | 四大核心结论 KPI 总览（最优 F1 / 最强因子 / 样本量 / 主要局限） |
| P04 | donut_chart | `templates/charts/donut_chart.svg` | "Pick for 3-6 part proportions where a center KPI/total deserves emphasis. Skip if no center value to feature (use pie_chart)." | 目标变量三分类占比 8.1/73.8/18.0，中心展示 1781 总样本 |
| P05 | basic_table | `templates/charts/basic_table.svg` | "Pick for plain tabular text/number grid, 3-8 columns. Skip if cells need visual bars (use consulting_table) or qualitative scores (use harvey_balls_table)." | Q9→三分类映射表 + 剔除列清单 |
| P06 | pipeline_with_stages | `templates/charts/pipeline_with_stages.svg` | "Pick for 3-5 horizontal pipeline stages, each = title + 1-line description + output artifact, connected by arrows (data pipelines, ETL, build pipelines). Skip if any stage lacks an artifact (use process_flow or numbered_steps)." | 建模管线 SMOTE→分层划分→5折CV→指标，每阶段配产出物 |
| P07 | basic_table | `templates/charts/basic_table.svg` | "Pick for plain tabular text/number grid, 3-8 columns. Skip if cells need visual bars (use consulting_table) or qualitative scores (use harvey_balls_table)." | 6 模型 Macro F1 / CV 排名表（配嵌入柱状图） |
| P09 | basic_table | `templates/charts/basic_table.svg` | "Pick for plain tabular text/number grid, 3-8 columns. Skip if cells need visual bars (use consulting_table) or qualitative scores (use harvey_balls_table)." | 4 模型 GridSearch 最优超参与 CV F1 表（配嵌入热力/折线图） |
| P10 | horizontal_bar_chart | `templates/charts/horizontal_bar_chart.svg` | "Pick for ranking 5-12 items, especially with long labels. Skip if <=8 short-label items (use bar_chart)." | Top-10 关键因子共识排名（中文长标签） |
| P13 | vertical_list | `templates/charts/vertical_list.svg` | "Pick for 3-6 numbered key points each with a short description — design principles, core tenets, action items, key takeaways, recommendations, executive summary points. Skip for icon-style cards (use icon_grid) or sequential steps (use numbered_steps)." | 四点核心结论 + 局限与展望 |

**Runners-up considered**:

- `bar_chart` | rejected for P04：三类样本被中频（73.8%）主导；donut 以中心总量（1781）强调这一多数类远胜等长柱形，而等长柱形反而会弱化不平衡的视觉冲击。
- `numbered_steps` | rejected for P06：建模管线每个阶段都带"产出物"（SMOTE 重采样集 / 分层划分 / CV 折 / 指标报告），`pipeline_with_stages` 的 artifact 列正是要传递的内容；`numbered_steps` 缺该列。
- `icon_grid` | rejected for P03：四条结论是指标主导的 KPI（0.4988、product_count 排名第 1 等），`kpi_cards` 让数字成为主角；`icon_grid` 会把数字压在图标之下。
- `bar_chart` | rejected for P10：10 个中文长标签（如"文心一言使用"）需要横向排名条，纵向 `bar_chart` 会旋转/截断标签。
- `agenda_list` | rejected for P13：这些是研究结论与局限，不是会议议程/目录；`vertical_list` 的"key takeaways/recommendations"用例恰好吻合。

---

## VIII. Image Resource List

> 全部为用户已生成的 matplotlib 图表（`image_usage: provided`），原样嵌入、保留原始配色、`no-crop`（数据图不可裁切）。9 张精选入册；另有 6 张（cm_rf、heatmap_n_estimators、line_n_estimators、factor_rf、factor_permutation、factor_shap_summary）为同类冗余，已在更概括的图中体现，不入册以保持deck精炼。Image-as-canvas（#38–#46）覆盖由 P12 PCA 提供（#46 镜头框高亮重叠区 + 注释卡）。

| Filename | Dimensions | Ratio | Purpose | Type | Layout pattern | Acquire Via | Status | Reference |
| -------- | --------- | ----- | ------- | ---- | -------------- | ----------- | ------ | --------- |
| chart_model_f1.png | 1982×1176 | 1.69 | 6 模型 Macro F1 对比柱状图（P07 左面板） | Chart | #50 tiled grid (1×2 paired panel) + #21 rounded-rect crop + #19 thin frame + #70 matte frame | user | Existing | 6 模型 Macro F1 对比，SVM 居首 |
| chart_cv_boxplot.png | 1979×1181 | 1.68 | 5 折 CV 稳定性箱线图（P07 右面板） | Chart | #50 tiled grid (paired) + #21 + #19 + #70 | user | Existing | 6 模型 5 折 CV 分布箱线 |
| chart_per_class.png | 4179×1230 | 3.40 | 各类别 P/R/F1 分组柱状（P08 上带，超宽） | Chart | #49 asymmetric collage (wide + square) + #21 + #70 | user | Existing | 各类别 precision/recall，展示低频类难分 |
| cm_svm.png | 1309×1177 | 1.11 | 最优模型 SVM 混淆矩阵（P08 右侧，近方） | Chart | #49 asymmetric collage + #21 + #70 | user | Existing | SVM 三分类混淆矩阵，看误判流向 |
| heatmap_C_vs_gamma.png | 1487×1180 | 1.26 | SVM 超参 C×γ 网格热力（P09 左面板） | Chart | #50 tiled grid (paired) + #21 + #70 | user | Existing | SVM GridSearch C×γ F1 热力 |
| line_C.png | 1579×979 | 1.61 | SVM C 参数折线（P09 右面板） | Chart | #50 tiled grid (paired) + #21 + #70 | user | Existing | 单参数 C 的 CV F1 折线 |
| factor_cross_method.png | 2356×1328 | 1.77 | 跨方法因子重要性共识对比（P10 顶部 hero） | Chart | #5 top-band chart + bottom native bar + #19 frame + #21 | user | Existing | RF / Permutation / SHAP 三方法因子对比 |
| factor_shap_beeswarm.png | 1996×1181 | 1.69 | SHAP beeswarm 总览（P11 hero 左） | Chart | #2 left image + right insight column + #19 + #21 + #70 | user | Existing | SHAP 全局 beeswarm，特征影响方向与幅度 |
| pca_scatter.png | 1977×1579 | 1.25 | PCA 二维散点三类分布（P12 hero） | Chart | #19 framed hero + #46 bordered lens on overlap region + #21 | user | Existing | PC1/PC2 三类用户散点，中部重叠区 |

> 布局模式 `#<id>` 取自 `references/image-layout-patterns.md`（Primary + Modifier）。所有图表为数据图 → `no-crop`，容器按原生比例 meet。P12 经 `#46` 镜头框高亮三类重叠区，满足 image-as-canvas（#38–#46）覆盖要求。

---

## IX. Content Outline

### Part 1：开篇 —— 背景与结论先行

#### Slide 01 - 封面

- **Layout**: Single column centered（深蓝渐变装饰 + 研究红短色条）
- **Title**: 大学生生成式人工智能使用频率影响因素研究
- **Subtitle**: 基于 1781 份问卷的机器学习分类与因子分析
- **Info**: 模式识别课程大作业 · 2026 年 6 月
- **Core message**: 一次关于"谁更爱用生成式AI"的数据驱动回答。

#### Slide 02 - 研究背景与核心问题

- **Layout**: Negative-space-driven（左侧大问句 hero，右侧三段背景）
- **Title**: 生成式AI正深度渗透校园——但谁用得多、谁用得少，差异何在？
- **Core message**: 频率高低并非随机，本研究用机器学习找出背后的决定因素。
- **Content**:
  - 背景：AIGC 快速渗透大学生学习与生活，使用频率出现明显分化。
  - 数据：基于 1781 份大学生生成式AI使用情况问卷。
  - 问题：哪些因素决定了大学生使用生成式AI的频率高低？

#### Slide 03 - 核心结论总览（pyramid 答案先行）

- **Layout**: 四格 KPI 卡片（2×2）
- **Title**: 一句话结论：产品多样性与功能取向是强信号，SVM 达到最优分类
- **Visualization**: kpi_cards
- **Core message**: 把四个最关键的发现先摆出来，后续逐页展开证据。
- **Content**（四张 KPI）:
  - 【最优模型】SVM · Macro F1 = 0.4988（调优后 CV 提升至 0.520）
  - 【最强因子】使用产品数量 product_count · 共识排名第 1（r=0.364）
  - 【样本规模】1781 份问卷 · 64 特征 · 三分类
  - 【主要局限】低频组仅 8.1%，整体分类难度被样本不平衡拖累

### Part 2：数据与方法

#### Slide 04 - 数据概况

- **Layout**: 左 donut（目标分布）+ 右特征构成表
- **Title**: 1781 份问卷、64 个特征，目标是严重不平衡的三分类
- **Visualization**: donut_chart（目标分布）+ basic_table（特征构成）
- **Core message**: 样本量大但类别极度偏斜，这是后续建模难度的根源。
- **Content**:
  - 目标分布（donut，中心 1781）：低频 8.1%（145）· 中频 73.8%（1315）· 高频 18.0%（321）
  - 特征构成表：Q1 性别(1) / Q2 学历(3) / Q3 专业(3) / Q4 年级(5) / Q5 课程偏好(4) / Q6 课堂知识重要度(1) / Q7 分数重要度(1) / Q8 产品使用(10+1) / Q10 功能排序(13) / Q11–Q14 四大场景量表(33) ≈ 64 个特征
  - 原始 78 列 → 经特征工程约 64 个

#### Slide 05 - 标签构造与数据清洗

- **Layout**: 左映射表 + 右剔除列清单
- **Title**: Q9 频率重编码为低/中/高三分类，并剔除 6 类目标泄漏与噪声列
- **Visualization**: basic_table
- **Core message**: 标签的重定义与防泄漏清洗，是结果可信的前提。
- **Content**:
  - Q9 → 三分类映射：从未使用→低频；一周 1～10 次→中频；一周 11 次以上→高频
  - 剔除列及原因：序号（无意义）/ 学校（与专业共线）/ 所用时间（元数据）/ 总分（与目标高度相关·泄漏）/ Q15 总体情况（泄漏 r=0.235）/ Q16 该不该使用（近零方差 95.9% 选"应该"）/ Q17 Q18 开放文本 / Q14 注意力检测题（34.9% 未通过）

#### Slide 06 - 实验设计与方法论

- **Layout**: 顶部建模管线（pipeline_with_stages）+ 底部三大实验三栏
- **Title**: SMOTE + 分层划分 + 5 折 CV，三大实验逐层验证结论
- **Visualization**: pipeline_with_stages
- **Core message**: 严谨、防泄漏、可复现的统一管线，支撑后续所有结论。
- **Content**:
  - 建模管线：SMOTE 过采样（仅训练集内）→ 80/20 分层划分 → 5 折交叉验证 → Macro F1 为主指标（+每类 P/R + 混淆矩阵）
  - 三大实验：①多模型对比（KNN/决策树/随机森林/SVM/朴素贝叶斯/Logistic回归，6 个）②超参数调优（GridSearchCV，4 模型）③因子重要性（RF + Permutation + SHAP 三方法共识）

### Part 3：实验结果

#### Slide 07 - 实验1：多模型对比

- **Layout**: 上方双图面板（model_f1 + cv_boxplot）+ 下方排名表
- **Title**: SVM 与 Logistic 回归并列最优，整体受低频样本稀疏拖累
- **Visualization**: basic_table（排名表）+ 嵌入图（model_f1.png / cv_boxplot.png）
- **Core message**: 线性模型（SVM/LR）在此数据上最稳，树模型与 KNN 偏弱。
- **Content**:
  - 排名：SVM 0.4988（CV 0.4860）· LR 0.4951（0.5134）· RF 0.4761（0.4898）· 朴素贝叶斯 0.4125（0.4024）· 决策树 0.3900（0.4368）· KNN 0.3622（0.3765）
  - 解读：SVM 在本数据集最优；CV 上 LR 均值反超说明其稳定性更强
  - 瓶颈：整体 F1 偏低，主因低频组仅 8.1% 样本量不足

#### Slide 08 - 模型诊断：稳定性与混淆矩阵

- **Layout**: 左 per_class（超宽）+ 右 cm_svm（近方）
- **Title**: 模型在中频类上稳健，低频与高频的边界识别困难
- **Visualization**: 嵌入图（chart_per_class.png / cm_svm.png）
- **Core message**: 中频好分、两端难分——错误主要发生在相邻频率类之间。
- **Content**:
  - per_class：中频类 precision/recall 最高；低频与高频类指标明显偏低
  - 混淆矩阵（SVM）：误判集中在相邻类别（低↔中、中↔高），罕有跨级混淆
  - 结论：模型抓住了频率梯度，但端点样本稀少限制了精度

#### Slide 09 - 实验2：超参数调优

- **Layout**: 左双图（heatmap_C_vs_gamma + line_C）+ 右最优超参表
- **Title**: GridSearch 调优后 SVM 的 CV Macro F1 由 0.486 提升至 0.520
- **Visualization**: basic_table（最优超参表）+ 嵌入图（heatmap_C_vs_gamma.png / line_C.png）
- **Core message**: 线性核 + 小 C 让 SVM 最稳，调优收益主要来自 SVM 自身。
- **Content**:
  - 最优超参表：SVM 0.5199（C=0.1, kernel=linear, γ=scale）· RF 0.5153（n=200, depth=10, min_split=10, feat=√）· DT 0.4760（entropy, depth=10, min_split=10）· KNN 0.4027（k=3, distance, manhattan）
  - SVM 热力/折线：小 C + 线性核区表现最佳，反映特征近似线性可分
  - 调优后 SVM 成为全局最优（CV 0.520）

#### Slide 10 - 实验3：因子分析——最强预测因子

- **Layout**: 顶部 cross_method 宽图 + 底部 Top-10 原生横向条形
- **Title**: 使用产品数量、文本生成、特定产品（文心一言/ChatGPT）是最强预测因子
- **Visualization**: horizontal_bar_chart（Top-10）+ 嵌入图（factor_cross_method.png）
- **Core message**: "用得多不多"本质上是"用得广不广、用得深不深"。
- **Content**:
  - Top-10 共识排名（平均排名）：product_count(1.3) · 文本生成(3.0) · 文心一言(4.0) · 性别(7.7) · ChatGPT(8.3) · Q4_2 年级(9.3) · 文科(9.3) · Q2_1 学历(9.7) · 理科(9.7) · 调试代码(10.7)
  - 三方法（RF/Permutation/SHAP）高度一致 → 结论稳健
  - 解读：用越多不同产品、越倾向文本生成与代码调试、特定产品使用者，频率越高；性别与文理科亦有显著影响

#### Slide 11 - 因子分析：SHAP 可解释性

- **Layout**: 左 beeswarm hero + 右三句洞察
- **Title**: SHAP 确认全局结论，并揭示高低频群体的差异化驱动
- **Visualization**: 嵌入图（factor_shap_beeswarm.png）
- **Core message**: 同一组强因子，对高频用户是推力、对低频用户是阻力。
- **Content**:
  - 全局：product_count 高值→正向贡献（推向高频）；文本生成/调试代码使用→正向
  - 方向性：SHAP 给出影响方向（红=高值），比单纯排序更可解释
  - 群体差异：高频受产品广度+编程功能驱动；低频常与产品单一、不用文本/代码功能相伴

### Part 4：降维与结论

#### Slide 12 - PCA 降维可视化

- **Layout**: Negative-space-driven（左 hero 散点 + #46 镜头框高亮重叠区 + 右一句洞察）
- **Title**: 三类用户在低维空间高度重叠，频率由多因素共同塑造
- **Visualization**: 嵌入图（pca_scatter.png）+ #46 lens
- **Core message**: 没有单一维度能线性切开三类——这正是分类难度的几何证据。
- **Content**:
  - PC1 解释方差 17.4% · PC2 5.8% · 合计仅 23.3%（二维不足以分离）
  - 三类在中部大面积重叠（#46 镜头框高亮）
  - 结论：使用频率是高维多因素现象，需多特征联合建模

#### Slide 13 - 结论与启示

- **Layout**: 左四点结论 vertical_list + 右局限与展望
- **Title**: 产品广度与功能取向是频率主因；样本不平衡是核心瓶颈
- **Visualization**: vertical_list
- **Core message**: 研究同时给出了"为什么"和"还差什么"。
- **Content**:
  - 四点结论：①使用产品数量是最强预测因子（r=0.364）②文本生成功能使用是关键区分因素③性别对频率有显著影响④SVM 最优但整体难度大、受低频样本不足（8.1%）限制
  - 局限：低频样本极少、PCA 可分性低、问卷自填偏差
  - 展望：针对低频组的过采样策略 / 非线性模型 / 纵向追踪

#### Slide 14 - 致谢

- **Layout**: Single column centered
- **Title**: 谢谢聆听 · 欢迎提问
- **Info**: 感谢老师与同学的指导与建议
- **Core message**: 答辩礼成，进入问答。

---

## X. Speaker Notes Requirements

- 每页一个 note 文件，存 `notes/`，文件名匹配 SVG（如 `01_cover.md`）。
- **风格**：pyramid 结论驱动——每页首句即要点，随后 2–3 句事实性支撑，口语化、权威。
- **总时长**：约 10 分钟答辩（每页约 35–45 秒，结果页略长）。
- **目的**：report（汇报研究成果）+ persuade（论证结论可信）。
- 拆分后的 note 文件不含 `#` 标题行；`notes/total.md` 主文档使用 `#` 标题行。

---

## XI. Technical Constraints Reminder

### SVG Generation Must Follow:

1. viewBox: `0 0 1280 720`
2. 背景用 `<rect>`
3. 文本换行用 `<tspan>`（禁 `<foreignObject>`）
4. 透明度用 `fill-opacity` / `stroke-opacity`（禁 `rgba()`）
5. 禁用：`mask`、`<style>`、`class`、`foreignObject`、`textPath`、`animate*`、`script`
6. 文本字符：排版与符号写原生 Unicode（`—` `–` `©` `→` `≈` `≥` 等）；禁 HTML 命名实体；XML 保留字转义为 `&amp; &lt; &gt;`
7. `marker-start`/`marker-end` 受限允许（`<marker>` 在 `<defs>`、`orient="auto"`、三角/菱形/圆形）
8. `clipPath` 仅用于 `<image>`（圆角面板等），单一形状子元素

### PPT Compatibility Rules:

- 禁 `<g opacity="...">`（组透明度），逐子元素设置
- 图片透明用叠加蒙层 `<rect fill="bg-color" opacity="0.x"/>`
- 仅内联样式；禁外部 CSS 与 `@font-face`
