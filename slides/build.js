// =============================================================
//  大学生 AIGC 使用频率分类模型 — 期末作业讲解 PPT
//  设计系统：oklch 派生单色阶 / [icon] 诚实占位 / 60-30-0 / 呼吸感
//  生成：  cd slides && node build.js
// =============================================================
const pptxgen = require("pptxgenjs");

// ---- oklch 派生单色阶（H=250° 固定，仅明度变化；勿手改）----
const C = {
  COVER: "171F27", SECTION: "272F37",
  INK: "20272F", MUTED: "636A71",
  ON_DARK: "CCD2D7", ON_DARK_M: "8D9399",
  BAR_D: "373E46", BAR_M: "6E757D", BAR_L: "B9BEC4",
  LINE: "D4D8DD", BODY: "F0F4F7", CARD: "FAFDFF",
};
const FONT_CN = "阿里巴巴普惠体"; // ⚠️ 演示机需已安装 / 嵌入，否则被替换
const FONT_EN = "Arial";

// ---- 排版基线（约束固化）----
const SAFE = 0.4;   // 安全区 ≈1.0cm
const PAD = 0.12;   // 文本框内部边距 ≈0.30cm
const CW = 10 - 2 * SAFE, CH = 5.625 - 2 * SAFE; // 内容区 9.2 × 4.825

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "你的名字";
pres.title = "大学生 AIGC 使用频率分类模型";

// ---------- helpers ----------
// 等比缩放：返回宽高与在 box 内的居中偏移
const fit = (pw, ph, bw, bh) => {
  const r = Math.min(bw / pw, bh / ph);
  return { w: pw * r, h: ph * r, ox: (bw - pw * r) / 2, oy: (bh - ph * r) / 2 };
};
// [icon] 诚实占位标记
const tag = (t) => ({ text: `[${t}] `, options: { fontFace: FONT_EN, fontSize: 11, color: C.MUTED, charSpacing: 1 } });

// 浅色页标题行：[tag] + 编号 + 标题
function titleRow(s, t, no, txt) {
  s.addText([
    tag(t),
    { text: no + "   ", options: { fontFace: FONT_EN, color: C.MUTED, bold: true } },
    { text: txt, options: { fontFace: FONT_CN, color: C.INK, bold: true } },
  ], { x: SAFE, y: SAFE, w: CW, h: 0.6, fontSize: 22, valign: "middle", margin: PAD });
}

function titleRowDark(s, t, txt) {
  s.addText([
    tag(t).options ? { text: `[${t}] `, options: { fontFace: FONT_EN, fontSize: 11, color: C.ON_DARK_M, charSpacing: -1 } } : tag(t),
    { text: txt, options: { fontFace: FONT_CN, color: C.ON_DARK, bold: true } },
  ], { x: SAFE, y: SAFE, w: CW, h: 0.6, fontSize: 22, valign: "middle", margin: PAD });
}

// 挂载式图表：CARD 底 + 细框 + 居中等比图
function chart(s, path, pw, ph, box) {
  s.addShape(pres.shapes.RECTANGLE, {
    x: box.x, y: box.y, w: box.w, h: box.h,
    fill: { color: C.CARD }, line: { color: C.LINE, width: 0.75 },
  });
  const inner = 0.12;
  const f = fit(pw, ph, box.w - 2 * inner, box.h - 2 * inner);
  s.addImage({ path, x: box.x + inner + f.ox, y: box.y + inner + f.oy, w: f.w, h: f.h });
}

// =============================================================
// 第 1 页 · 封面（深色）
// =============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.COVER };
  s.addText([ { text: "[ 模式识别大作业 ]", options: { fontFace: FONT_EN, fontSize: 12, color: C.ON_DARK_M, charSpacing: 4 } } ],
    { x: SAFE, y: 1.55, w: CW, h: 0.4, margin: PAD });
  s.addText("大学生生成式 AI\n使用频率分类模型", {
    x: SAFE, y: 2.05, w: CW, h: 1.6, fontFace: FONT_CN, fontSize: 34,
    color: C.ON_DARK, bold: true, align: "left", valign: "top",
    lineSpacingMultiple: 1.15, margin: PAD,
  });
  s.addText("基于 1781 份问卷的三分类建模与关键因素分析", {
    x: SAFE, y: 3.85, w: CW, h: 0.5, fontFace: FONT_CN, fontSize: 15,
    color: C.ON_DARK_M, margin: PAD,
  });
  s.addText("姓名 · 学号          2026.06", {
    x: SAFE, y: 4.85, w: CW, h: 0.35, fontFace: FONT_EN, fontSize: 11,
    color: C.ON_DARK_M, charSpacing: 2, margin: PAD,
  });
}

// =============================================================
// 第 2 页 · 研究背景与核心问题（浅色，左文右引言卡）
// =============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.BODY };
  titleRow(s, "背景", "—", "研究背景与核心问题");
  s.addText([
    { text: "生成式 AI 已深度融入大学生的学习与科研。", options: { breakLine: true, paraSpaceAfter: 8 } },
    { text: "然而，使用频率因人而异——有人日均数十次，有人从未接触。", options: { breakLine: true, paraSpaceAfter: 8 } },
    { text: "理解「谁在用、用多少、为什么」，对教育引导与产品优化都有价值。", options: {} },
  ], { x: SAFE, y: 1.45, w: 4.5, h: 3.2, fontFace: FONT_CN, fontSize: 15, color: C.INK,
       lineSpacingMultiple: 1.4, paraSpaceBefore: 6, margin: PAD });
  // 右侧引言卡
  s.addShape(pres.shapes.RECTANGLE, { x: 5.3, y: 1.6, w: 4.3, h: 2.7, fill: { color: C.CARD }, line: { color: C.LINE, width: 0.75 } });
  s.addText([ tag("问题") ], { x: 5.55, y: 1.85, w: 3.8, h: 0.3, margin: 0 });
  s.addText("哪些因素，决定了一名大学生使用生成式 AI 的频率高低？", {
    x: 5.55, y: 2.3, w: 3.8, h: 1.8, fontFace: FONT_CN, fontSize: 19, color: C.INK,
    bold: true, lineSpacingMultiple: 1.4, margin: 0,
  });
}

// =============================================================
// 第 3 页 · 数据概况（浅色，三大数字 + 类别分布条）
// =============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.BODY };
  titleRow(s, "数据", "—", "数据概况");
  const stats = [["1781", "份有效问卷"], ["64", "个特征（原 78 列）"], ["3", "类使用频率"]];
  stats.forEach((st, i) => {
    const x = SAFE + i * 3.07;
    s.addText(st[0], { x, y: 1.5, w: 3.0, h: 1.0, fontFace: FONT_EN, fontSize: 50, color: C.INK, bold: true, align: "center", margin: PAD });
    s.addText(st[1], { x, y: 2.5, w: 3.0, h: 0.4, fontFace: FONT_CN, fontSize: 13, color: C.MUTED, align: "center", margin: PAD });
  });
  // 类别分布条
  s.addText([ tag("分布") ], { x: SAFE, y: 3.25, w: CW, h: 0.3, margin: 0 });
  const dist = [["低频", 0.081, "8.1%", C.BAR_L], ["中频", 0.738, "73.8%", C.BAR_M], ["高频", 0.180, "18.0%", C.BAR_D]];
  const trackX = 1.7, trackW = 6.6;
  dist.forEach((d, i) => {
    const y = 3.65 + i * 0.45;
    s.addText(d[0] + " " + d[2], { x: SAFE, y, w: 1.25, h: 0.35, fontFace: FONT_CN, fontSize: 12, color: C.INK, valign: "middle", margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: trackX, y: y + 0.08, w: trackW, h: 0.2, fill: { color: C.LINE } });
    s.addShape(pres.shapes.RECTANGLE, { x: trackX, y: y + 0.08, w: trackW * d[1], h: 0.2, fill: { color: d[3] } });
  });
}

// =============================================================
// 第 4 页 · 数据清洗与特征工程（浅色，双栏对照）
// =============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.BODY };
  titleRow(s, "预处理", "—", "数据清洗与特征工程");
  // 左卡：排除的列
  s.addShape(pres.shapes.RECTANGLE, { x: SAFE, y: 1.45, w: 4.3, h: 3.6, fill: { color: C.CARD }, line: { color: C.LINE, width: 0.75 } });
  s.addText("排除的列", { x: SAFE + 0.2, y: 1.6, w: 3.9, h: 0.4, fontFace: FONT_CN, fontSize: 15, color: C.INK, bold: true, margin: 0 });
  s.addText([
    { text: "总分、Q15 总体情况", options: { bullet: true, breakLine: true, color: C.MUTED } },
    { text: "Q16 该不该使用（近零方差 95.9%）", options: { bullet: true, breakLine: true, color: C.MUTED } },
    { text: "学校、序号、所用时间（元数据）", options: { bullet: true, breakLine: true, color: C.MUTED } },
    { text: "Q17、Q18 开放文本题", options: { bullet: true, breakLine: true, color: C.MUTED } },
    { text: "注意力检测题（34.9% 未通过）", options: { bullet: true, color: C.MUTED } },
  ], { x: SAFE + 0.2, y: 2.1, w: 3.9, h: 2.8, fontFace: FONT_CN, fontSize: 13, paraSpaceAfter: 7, margin: 0 });
  // 右卡：编码方式
  s.addShape(pres.shapes.RECTANGLE, { x: 5.1, y: 1.45, w: 4.5, h: 3.6, fill: { color: C.CARD }, line: { color: C.LINE, width: 0.75 } });
  s.addText("编码方式", { x: 5.3, y: 1.6, w: 4.1, h: 0.4, fontFace: FONT_CN, fontSize: 15, color: C.INK, bold: true, margin: 0 });
  s.addText([
    { text: "One-Hot", options: { bold: true, color: C.INK, breakLine: true } },
    { text: "学历 / 专业 / 年级 / 课程偏好", options: { color: C.MUTED, breakLine: true, paraSpaceAfter: 7 } },
    { text: "数值型", options: { bold: true, color: C.INK, breakLine: true } },
    { text: "重要度 0–100% · 功能排序 · Likert 1–5", options: { color: C.MUTED, breakLine: true, paraSpaceAfter: 7 } },
    { text: "原编码 / 聚合", options: { bold: true, color: C.INK, breakLine: true } },
    { text: "性别 · 产品使用二值列 → product_count", options: { color: C.MUTED } },
  ], { x: 5.3, y: 2.1, w: 4.1, h: 2.8, fontFace: FONT_CN, fontSize: 13, lineSpacingMultiple: 1.3, margin: 0 });
}

// =============================================================
// 第 5 页 · 技术路线（浅色，流程节点）
// =============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.BODY };
  titleRow(s, "方法", "—", "技术路线");
  const nodes = ["数据清洗\n特征工程", "SMOTE\n8:2 分层划分", "6 模型对比\n5 折 CV", "GridSearch\n超参调优", "三方法\n因子分析 + PCA"];
  const nW = 1.55, gap = 0.27, startX = SAFE + (CW - (5 * nW + 4 * gap)) / 2;
  const ny = 2.35, nH = 1.3;
  nodes.forEach((lbl, i) => {
    const x = startX + i * (nW + gap);
    s.addShape(pres.shapes.RECTANGLE, { x, y: ny, w: nW, h: nH, fill: { color: C.CARD }, line: { color: C.BAR_M, width: 1 } });
    s.addText(String(i + 1).padStart(2, "0"), { x, y: ny + 0.1, w: nW, h: 0.25, fontFace: FONT_EN, fontSize: 10, color: C.MUTED, align: "center", margin: 0 });
    s.addText(lbl, { x, y: ny + 0.4, w: nW, h: 0.85, fontFace: FONT_CN, fontSize: 11, color: C.INK, align: "center", valign: "middle", lineSpacingMultiple: 1.2, margin: 0 });
    if (i < nodes.length - 1) {
      s.addShape(pres.shapes.LINE, { x: x + nW, y: ny + nH / 2, w: gap, h: 0, line: { color: C.BAR_M, width: 1.5, endArrowType: "triangle" } });
    }
  });
  s.addText("评估指标：Macro F1 为主 · 辅以每类 Precision / Recall 与混淆矩阵", {
    x: SAFE, y: 4.35, w: CW, h: 0.4, fontFace: FONT_CN, fontSize: 12, color: C.MUTED, align: "center", margin: PAD,
  });
}

// =============================================================
// 第 6 页 · 实验一·模型对比（浅色，左文右图）
// =============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.BODY };
  titleRow(s, "实验", "01", "多模型对比 · SVM 最优");
  s.addText([
    { text: "SVM Macro F1 = 0.4988，六模型最优", options: { bullet: true, breakLine: true, bold: true } },
    { text: "Logistic 回归次之 (0.4951)", options: { bullet: true, breakLine: true } },
    { text: "KNN / 决策树最弱 (< 0.40)", options: { bullet: true, breakLine: true } },
    { text: "低频组仅 8.1% 样本，整体分类难度大", options: { bullet: true, color: C.MUTED } },
  ], { x: SAFE, y: 1.45, w: 3.9, h: 3.4, fontFace: FONT_CN, fontSize: 15, color: C.INK,
       lineSpacingMultiple: 1.3, paraSpaceAfter: 9, margin: PAD });
  chart(s, "assets/model_comparison_f1.png", 1982, 1176, { x: 4.6, y: 1.4, w: 5.0, h: 3.7 });
}

// =============================================================
// 第 7 页 · 实验一·交叉验证稳定性（浅色，左图右文）
// =============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.BODY };
  titleRow(s, "实验", "02", "5 折交叉验证 · 稳定性");
  chart(s, "assets/cv_boxplot.png", 1979, 1181, { x: SAFE, y: 1.4, w: 5.0, h: 3.7 });
  s.addText([
    { text: "Logistic 回归最稳定", options: { bullet: true, breakLine: true, bold: true } },
    { text: "CV Mean = 0.5134，方差最小", options: { bullet: true, breakLine: true, color: C.MUTED } },
    { text: "SVM 紧随其后，表现稳健", options: { bullet: true, breakLine: true } },
    { text: "各模型折间波动可控，无过拟合", options: { bullet: true, color: C.MUTED } },
  ], { x: 5.7, y: 1.7, w: 3.9, h: 3.2, fontFace: FONT_CN, fontSize: 15, color: C.INK,
       lineSpacingMultiple: 1.3, paraSpaceAfter: 9, margin: PAD });
}

// =============================================================
// 第 8 页 · 实验一·混淆矩阵（浅色，左图右文）
// =============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.BODY };
  titleRow(s, "实验", "03", "SVM 混淆矩阵 · 低频组识别难");
  chart(s, "assets/svm_cm.png", 1309, 1177, { x: SAFE, y: 1.4, w: 4.6, h: 3.7 });
  s.addText([
    { text: "中频（73.8%）识别最准", options: { bullet: true, breakLine: true, bold: true } },
    { text: "低频仅 145 人，大量被误判为中频", options: { bullet: true, breakLine: true, color: C.MUTED } },
    { text: "高频次之，与中频存在混淆", options: { bullet: true, breakLine: true } },
    { text: "→ 类别不平衡是核心难点", options: { bullet: true, bold: true } },
  ], { x: 5.3, y: 1.7, w: 4.3, h: 3.2, fontFace: FONT_CN, fontSize: 15, color: C.INK,
       lineSpacingMultiple: 1.3, paraSpaceAfter: 9, margin: PAD });
}

// =============================================================
// 第 9 页 · 实验二·超参调优（浅色，双图）
// =============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.BODY };
  titleRow(s, "调优", "—", "超参数网格搜索");
  chart(s, "assets/heatmap_n_estimators_vs_max_depth.png", 1503, 1180, { x: SAFE, y: 1.4, w: 4.4, h: 3.0 });
  chart(s, "assets/line_C.png", 1579, 979, { x: 5.1, y: 1.4, w: 4.5, h: 3.0 });
  s.addText([
    { text: "[ RF ] ", options: { fontFace: FONT_EN, color: C.MUTED } },
    { text: "n_estimators ≈ 200、max_depth ≈ 20 最佳", options: { fontFace: FONT_CN, color: C.INK, breakLine: true } },
    { text: "[ SVM ] ", options: { fontFace: FONT_EN, color: C.MUTED } },
    { text: "C = 10 后性能趋于稳定", options: { fontFace: FONT_CN, color: C.INK } },
  ], { x: SAFE, y: 4.5, w: CW, h: 0.7, fontSize: 13, lineSpacingMultiple: 1.3, paraSpaceAfter: 4, margin: PAD });
}

// =============================================================
// 第 10 页 · 实验三·三方法重要性（浅色，大图 + 三标签）
// =============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.BODY };
  titleRow(s, "因子", "01", "三种方法交叉验证");
  chart(s, "assets/cross_method_comparison.png", 2356, 1328, { x: SAFE, y: 1.35, w: 6.0, h: 3.75 });
  s.addText([
    { text: "三方法共识", options: { bold: true, color: C.INK, breakLine: true, paraSpaceAfter: 8 } },
    { text: "[ RF ] 随机森林 Gini 重要性", options: { fontFace: FONT_CN, color: C.MUTED, breakLine: true, paraSpaceAfter: 6 } },
    { text: "[ Perm ] 排列重要性", options: { fontFace: FONT_CN, color: C.MUTED, breakLine: true, paraSpaceAfter: 6 } },
    { text: "[ SHAP ] Shapley 值", options: { fontFace: FONT_CN, color: C.MUTED } },
  ], { x: 6.6, y: 1.7, w: 3.0, h: 3.2, fontSize: 14, lineSpacingMultiple: 1.3, margin: PAD });
}

// =============================================================
// 第 11 页 · 实验三·SHAP 深度分析（浅色，左图右文）
// =============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.BODY };
  titleRow(s, "因子", "02", "SHAP 深度分析");
  chart(s, "assets/shap_beeswarm.png", 1996, 1181, { x: SAFE, y: 1.4, w: 5.3, h: 3.7 });
  s.addText([
    { text: "product_count 影响最显著", options: { bullet: true, breakLine: true, bold: true } },
    { text: "高取值正向推高使用频率", options: { bullet: true, breakLine: true, color: C.MUTED } },
    { text: "文本生成功能使用排第二", options: { bullet: true, breakLine: true } },
    { text: "性别、文心一言为次级驱动", options: { bullet: true, color: C.MUTED } },
  ], { x: 5.9, y: 1.7, w: 3.7, h: 3.2, fontFace: FONT_CN, fontSize: 15, color: C.INK,
       lineSpacingMultiple: 1.3, paraSpaceAfter: 9, margin: PAD });
}

// =============================================================
// 第 12 页 · 实验三·共识排名 Top 5（浅色，表格）
// =============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.BODY };
  titleRow(s, "因子", "03", "共识排名 · Top 5 关键因素");
  const cell = (t, o = {}) => ({ text: t, options: { fontFace: FONT_CN, fontSize: 14, color: C.INK, align: "center", valign: "middle", margin: 0.08, ...o } });
  const rows = [
    [cell("排名", { color: C.ON_DARK, bold: true, fill: { color: C.SECTION } }),
     cell("关键特征", { color: C.ON_DARK, bold: true, align: "left", fill: { color: C.SECTION } }),
     cell("平均排名", { color: C.ON_DARK, bold: true, fill: { color: C.SECTION } })],
    [cell("1", { bold: true, color: C.ON_DARK, fill: { color: C.BAR_M } }), cell("使用产品数量 product_count", { align: "left", bold: true, color: C.ON_DARK, fill: { color: C.BAR_M } }), cell("1.3", { bold: true, color: C.ON_DARK, fill: { color: C.BAR_M } })],
    [cell("2", { fill: { color: C.BODY } }), cell("文本生成功能使用", { align: "left", fill: { color: C.BODY } }), cell("3.0", { fill: { color: C.BODY } })],
    [cell("3", { fill: { color: C.CARD } }), cell("文心一言使用", { align: "left", fill: { color: C.CARD } }), cell("4.0", { fill: { color: C.CARD } })],
    [cell("4", { fill: { color: C.BODY } }), cell("性别", { align: "left", fill: { color: C.BODY } }), cell("7.7", { fill: { color: C.BODY } })],
    [cell("5", { fill: { color: C.CARD } }), cell("ChatGPT 使用", { align: "left", fill: { color: C.CARD } }), cell("8.3", { fill: { color: C.CARD } })],
  ];
  s.addTable(rows, { x: SAFE + 0.8, y: 1.6, w: 7.6, colW: [1.2, 5.0, 1.4], rowH: 0.55, border: { type: "solid", pt: 0.5, color: C.LINE } });
}

// =============================================================
// 第 13 页 · PCA 降维可视化（浅色，左图右文）
// =============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.BODY };
  titleRow(s, "可视化", "—", "PCA 降维可视化");
  chart(s, "assets/pca_scatter.png", 1977, 1579, { x: SAFE, y: 1.4, w: 4.3, h: 3.7 });
  s.addText([
    { text: "PC1 解释方差 17.4%", options: { bullet: true, breakLine: true, bold: true } },
    { text: "PC2 解释方差 5.8%", options: { bullet: true, breakLine: true, bold: true } },
    { text: "三类用户在降维空间存在重叠", options: { bullet: true, breakLine: true, color: C.MUTED } },
    { text: "→ 使用频率受多因素共同作用", options: { bullet: true, bold: true } },
  ], { x: 5.0, y: 1.7, w: 4.6, h: 3.2, fontFace: FONT_CN, fontSize: 15, color: C.INK,
       lineSpacingMultiple: 1.3, paraSpaceAfter: 9, margin: PAD });
}

// =============================================================
// 第 14 页 · 关键结论（深色，2×2 卡片）
// =============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.COVER };
  s.addText([ { text: "[ 结论 ] ", options: { fontFace: FONT_EN, fontSize: 11, color: C.ON_DARK_M, charSpacing: 1 } },
    { text: "关键发现", options: { fontFace: FONT_CN, color: C.ON_DARK, bold: true } } ],
    { x: SAFE, y: SAFE, w: CW, h: 0.6, fontSize: 22, valign: "middle", margin: PAD });
  const cards = [
    ["01", "产品数量最强", "product_count 与频率相关 r = 0.364，居三方法之首"],
    ["02", "文本生成功能", "是区分使用频率高低的重要行为信号"],
    ["03", "性别显著", "性别对使用频率存在系统性影响"],
    ["04", "SVM 最优但受限", "Macro F1 = 0.4988，受低频样本 8.1% 限制"],
  ];
  const cW = 4.45, cH = 1.75, g = 0.3;
  cards.forEach((c, i) => {
    const x = SAFE + (i % 2) * (cW + g), y = 1.35 + Math.floor(i / 2) * (cH + g);
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: cW, h: cH, fill: { color: C.SECTION }, line: { color: C.BAR_D, width: 0.5 } });
    s.addText(c[0], { x: x + 0.2, y: y + 0.15, w: 1.0, h: 0.35, fontFace: FONT_EN, fontSize: 12, color: C.ON_DARK_M, margin: 0 });
    s.addText(c[1], { x: x + 0.2, y: y + 0.5, w: cW - 0.4, h: 0.45, fontFace: FONT_CN, fontSize: 16, color: C.ON_DARK, bold: true, margin: 0 });
    s.addText(c[2], { x: x + 0.2, y: y + 0.95, w: cW - 0.4, h: 0.7, fontFace: FONT_CN, fontSize: 12, color: C.ON_DARK_M, lineSpacingMultiple: 1.3, margin: 0 });
  });
}

// =============================================================
// 第 15 页 · 局限与展望（深色，双栏 + 致谢）
// =============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.COVER };
  s.addText([ { text: "[ 局限 ] ", options: { fontFace: FONT_EN, fontSize: 11, color: C.ON_DARK_M, charSpacing: 1 } },
    { text: "局限与展望", options: { fontFace: FONT_CN, color: C.ON_DARK, bold: true } } ],
    { x: SAFE, y: SAFE, w: CW, h: 0.6, fontSize: 22, valign: "middle", margin: PAD });
  s.addText("局限性", { x: SAFE, y: 1.4, w: 4.3, h: 0.4, fontFace: FONT_CN, fontSize: 15, color: C.ON_DARK, bold: true, margin: PAD });
  s.addText([
    { text: "低频样本仅 8.1%，少数类难识别", options: { bullet: true, breakLine: true, color: C.ON_DARK_M } },
    { text: "Q14 注意力题 34.9% 未通过", options: { bullet: true, breakLine: true, color: C.ON_DARK_M } },
    { text: "PCA 投影下三类存在重叠", options: { bullet: true, color: C.ON_DARK_M } },
  ], { x: SAFE, y: 1.85, w: 4.3, h: 2.2, fontFace: FONT_CN, fontSize: 14, paraSpaceAfter: 8, margin: PAD });
  s.addText("展望", { x: 5.1, y: 1.4, w: 4.5, h: 0.4, fontFace: FONT_CN, fontSize: 15, color: C.ON_DARK, bold: true, margin: PAD });
  s.addText([
    { text: "扩充低频样本、重采样策略", options: { bullet: true, breakLine: true, color: C.ON_DARK_M } },
    { text: "引入特征选择与交互项", options: { bullet: true, breakLine: true, color: C.ON_DARK_M } },
    { text: "尝试梯度提升 / 神经网络", options: { bullet: true, color: C.ON_DARK_M } },
  ], { x: 5.1, y: 1.85, w: 4.5, h: 2.2, fontFace: FONT_CN, fontSize: 14, paraSpaceAfter: 8, margin: PAD });
  s.addText("感谢聆听 · 欢迎提问", { x: SAFE, y: 4.7, w: CW, h: 0.4, fontFace: FONT_CN, fontSize: 13, color: C.ON_DARK_M, align: "center", margin: PAD });
}

pres.writeFile({ fileName: "AIGC_usage_presentation.pptx" }).then(() => console.log("done → AIGC_usage_presentation.pptx"));
