# Skill 真实图形产物：四类合成示例

[返回首页](../README.md) · [全部功能](../docs/FUNCTIONS.md)

这些图由本项目自编图形模块实际计算 / 绘制，按原字节展示；没有为首页单独美化图像、修改数值或重新拟合模型。**全部为合成演示，不是患者研究。**

## 生成版本与来源

生成模块为 2026-10-12 的 `doctor-paper-graphics-v02`，实际文件出自 `outputs/final/gallery/`，随后按相同字节收录于 `doctor-paper-v02/review/graphics/gallery/`。生成器 `build_gallery.py` 调用 `graphics.py` 的真实绘图函数与导出器；该图形模块与 v0.2 Skill 集成包内 `doctor-paper/scripts/graphics.py` 字节相同。这是历史模块运行产物，不宣称为 v0.4.4 / privacy-002 新运行或真人操作验收。

| 原尺寸图 | 真实入口 / 输入与解释 | 随图记录 |
|---|---|---|
| [ROC](../assets/skill-generated/roc.png) | `graphics.prediction_plot('roc', ...)`；固定合成 logistic 模型的 400 例内部留出风险，79 事件，AUC≈0.732 | [曲线数据与图形指纹](graphics/roc.json) |
| [校准](../assets/skill-generated/calibration.png) | `graphics.prediction_plot('calibration', ...)`；同一留出集，8 组各 50 人，条件于固定分组的 95% Wilson 区间 | [分组 / 区间与指纹](graphics/calibration.json) |
| [森林图](../assets/skill-generated/forest.png) | `graphics.forest(...)`；对应 700 例合成训练集，三变量调整 OR 与 95% Wald CI，对数轴参考线为 1 | [效应量 / 区间与指纹](graphics/forest.json) |
| [箱线叠加散点](../assets/skill-generated/distribution.png) | `graphics.group_distribution(...)`；另一独立合成严重程度示例，55 / 60 例，展示分布，不附显著性星号 | [分布数据与指纹](graphics/distribution.json) |

预测三图属于同一个独立合成预测场景：1200 条模拟筛查，排除 100 条后，以固定种子分为训练 700 / 内部留出 400。只在训练集拟合，留出集计算固定风险；内部留出不是外部验证。[原预测方法与种子](graphics/prediction-methods.json)保留模型、数据生成、拟合及适用边界。此场景不属于握力或旧 80 例营养论文，不为它们追加预测结论。

## 原生成命令与当前检查

以下为**原项目内部**文档记录的重现命令，需原项目生成器与已有依赖；生成器未放进当前仓库准备包。它不是普通医生必须输入的命令，也不是本轮已重新运行的记录：

```sh
python3 development/doctor-paper-graphics-v02/build_gallery.py --out /tmp/doctor-paper-graphics-new
```

输出目录须不存在；当时环境为 Python 3.14、NumPy 2.5.1、Matplotlib 3.11.0，并使用已有本机字体。生成器只处理固定合成样例，不是任意临床研究分析引擎。本轮逐张查看实际 PNG，核随图 JSON 的文件指纹，并核原模块产物与集成副本相同；未重新分析、安装依赖或调用模型。

当前包中可分别使用 [Ye1-预测评价图](../skills/ye1-prediction-plots/SKILL.md) 和 [Ye1-统计绘图](../skills/ye1-statistical-plot/SKILL.md)。需要相应固定预测分数 / 结局 / 验证角色，或效应量 / 区间 / 分组数据等必要前提；有图形函数不等于任意输入都能成立。不声称已有生存图或自动多面板图能力。

来源与日期：2026-10-15 UTC，依据用户要求仅展示 Skill 实际可生成的科研图；原运行方法、逐图回执及项目 v0.2 集成记录。此次只选取、核对和复制历史产物。
