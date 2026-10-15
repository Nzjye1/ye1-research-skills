# Ye1图形专项执行

对应25 Ye1-统计绘图、26 Ye1-预测评价图、27 Ye1-图形重绘、28 Ye1-图表注释。宿主根据医生请求代建输入；不要让医生填JSON或指定脚本路径。

## 统计绘图

先实际读取数据/聚合结果，核研究单位、单位、缺失、分母、配对或分组，以及数值来自哪个版本。根据问题选择分布图、分组分布、散点或森林图。森林图当前只接正值比值效应及已算好的有序置信区间，不替医生拟合模型；均数差等加性效应不能套比值对数轴。

`figure_task.py draw REQUEST --out NEW`用已有Matplotlib环境实际绘制PNG300dpi、SVG、PDF、逐点/分箱JSON和回执，保留源指纹。REQUEST含schema=ye1-figure/1，kind，source={path,sha256}，context，data和style。上下文按graphics.route实际列出的前提，不为凑图伪填。

- scatter：data.x/y一一对应；style有xlabel/ylabel/title/language，context含matched observations、units、association plan if inferential。重复坐标按面积记录次数，不移动实际坐标。
- histogram：data.values/edges，分箱覆盖全部观察；context按distribution路线，说明单位和single group/paired/independent。仅配对名称不能把分组图当配对效果分析。
- distribution：data.groups，style.group_labels/ylabel；显示全观察值、组n和四分位。负值必须保留。
- forest：data.estimate/lower/upper，style.row_labels/measure_label；context含effect measure、estimates、interval method、reference levels、adjustment set。区间方法写真实来源，不默认Wald。
- difference：data.estimate/lower/upper，style.row_labels/measure_label；用于已有加性差值和CI（如均数差、风险差），context明确effect measure、estimates、interval method、units、null value=0。只展示输入汇总数值，不从图像估读、不重新计算。

## 预测评价图

ROC/PR/校准/DCA只消费实际已完成的固定预测分数与观察到的结局，不从论文截图编造点。data.y/p明确按相同行排序；当前图形只支持无删失二分类，p须为0–1概率。先记结局时点、验证角色（表观训练/内部留出/外部验证）、模型训练与评价样本隔离证据。图形模块不替代建模、重采样或验证。

DCA还需明确临床行动与预先有依据的阈值范围；缺这些交适用性反馈，不画漂亮曲线冒充临床效用。校准当前为8组及Wilson区间，是有限图形，不能代替校准斜率/截距或充分外部验证。实际绘图用kind=roc/pr/calibration/dca及对应route上下文；DCA的data.thresholds必须在(0,1)且对应确认的阈值范围。

## 仅改样式

`figure_task.py redraw PREVIOUS STYLE_JSON --out NEW`验证原request/图源及文件指纹，沿原科学数据和前提，只接受语言、标题、轴标、组/行标签、字体、字号缩放、画布尺寸。不会重算模型或更改数值。宿主核翻译后的变量/单位语义一致。只有位图而没有底层数据时，可评论可见布局或在明确授权下另行编辑图片；不能把估读点称精确重绘。

图内中英文分别路由；中文日期/人数轴/图例等实际检查，英文原文献题名可保留。只使用现成字体，缺字标待续，不悄悄改成英文。机器检查字形、边界、刻度，交付前还需实际看图。

新绘或重绘的坐标标注、刻度、图例及图内注释默认不低于10 pt，标题不低于12 pt。加性差值图会把过长的组别标签换行显示，并为文字保留版面；如仍无法容纳，优先扩大画布或简化文字，不缩小正文、不用低分辨率放大位图伪称可读。交付前按稿件里的实际显示大小渲染，并在100%查看标签、图例、坐标和脚注；如不满足可读性，状态为PARTIAL并留原图。

## 图表注释

实际读取当前图或表及结果记录后，由宿主撰写图题/图注/表题。写清人群、研究单位、有效n、变量和单位、分组/参照、点线/区间/颜色含义、统计方法和缺失口径。未知方法写待核，不靠图型猜方法。图注翻译保留分母和证据强度；仅改注释不得重绘或重算。

保存原图/表、原注释、修改范围和新注释的独立版本。可用task_io.py的精确片段更新和数字token保护；首次新写注释仍需宿主把每个数字对照源结果，token相同不等于科学正确。图注不自动套IMRaD反防御规则。
