## canvas
- viewBox: 0 0 1280 720
- format: PPT 16:9

## mode
- mode: pyramid

## visual_style
- visual_style: data-journalism

## colors
- bg: #FFFFFF
- secondary_bg: #F3F1EC
- surface: #FAF8F3
- grid: #E8E3D6
- border: #D4D0C4
- primary: #1A3C6E
- accent: #B11226
- secondary_accent: #5B7DB1
- text: #23262B
- text_secondary: #56606B
- text_tertiary: #8C949D
- success: #2E7D32
- warning: #C77700
- primary_dark: #16315A
- axis: #94A3B8
- tint_accent: #FBE9EB
- tint_primary: #E7EDF5
- tint_secondary: #EAF1F6

## typography
- font_family: 'Microsoft YaHei','PingFang SC',Arial,sans-serif
- code_family: Consolas,'Courier New',monospace
- body: 18
- cover_title: 64
- chapter_title: 40
- title: 32
- hero_number: 44
- subtitle: 22
- annotation: 13
- footnote: 11

## icons
- library: tabler-outline
- stroke_width: 2
- inventory: robot, sparkles, users, trophy, target, stack-2, chart-bar, trending-up, alert-triangle, database, clipboard-data, filter, tags, flask, adjustments, git-branch, scale, clipboard-check, search, stethoscope, list-numbers, bolt, microscope, bulb, focus-2, circle-check, flag, mood-smile, heart

## images
- chart_model_f1: images/chart_model_f1.png | no-crop
- chart_cv_boxplot: images/chart_cv_boxplot.png | no-crop
- chart_per_class: images/chart_per_class.png | no-crop
- cm_svm: images/cm_svm.png | no-crop
- heatmap_C_vs_gamma: images/heatmap_C_vs_gamma.png | no-crop
- line_C: images/line_C.png | no-crop
- factor_cross_method: images/factor_cross_method.png | no-crop
- factor_shap_beeswarm: images/factor_shap_beeswarm.png | no-crop
- pca_scatter: images/pca_scatter.png | no-crop

## page_rhythm
- P01: anchor
- P02: breathing
- P03: dense
- P04: dense
- P05: dense
- P06: dense
- P07: dense
- P08: dense
- P09: dense
- P10: dense
- P11: dense
- P12: breathing
- P13: dense
- P14: anchor

## page_charts
- P03: kpi_cards
- P04: donut_chart
- P05: basic_table
- P06: pipeline_with_stages
- P07: basic_table
- P09: basic_table
- P10: horizontal_bar_chart
- P13: vertical_list

## forbidden
- Mixing icon libraries
- rgba()
- `<style>`, `class`, `<foreignObject>`, `textPath`, `@font-face`, `<animate*>`, `<script>`, `<iframe>`, `<symbol>`+`<use>`
- `<g opacity>` (set opacity on each child element individually)
- HTML named entities in text — write as raw Unicode; XML reserved chars `& < > " '` escaped as `&amp; &lt; &gt; &quot; &apos;`
