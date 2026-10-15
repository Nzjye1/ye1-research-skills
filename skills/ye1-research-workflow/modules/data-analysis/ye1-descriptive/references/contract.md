# Ye1 数据分析接口 v1

2026-10-13。本批授权：清单6、7、10–17；独立本地实现，非最终全包。数值由现有 R stats/jsonlite 执行，不安装依赖；Python 3.11+ 标准库处理CSV、规则与版本，XLSX另需已有openpyxl。用户显示名统一Ye1-，安装slug小写。

## 输入与可复用执行器

`python scripts/data_engine.py doctor [--rscript /existing/Rscript]` 仅自检所需能力，遵循v04“缺项不阻文本、不自动装库”的能力分流。Python缺失时宿主仍可拟方案/解释可信已有结果；不能语言模拟统计、伪造哈希/输出文件。R缺失时Python仍可读CSV、质控/清洗；已有平台执行器可用不代表自动批准迁移患者数据。

`qc|dictionary|clean|analyze DATA --dictionary DICTIONARY.json --out NEW_DIRECTORY [--sheet SHEET]`。clean另带`--rules RULES.json`；analyze另带`--plan PLAN.json [--previous PRIOR_DIRECTORY] [--confirmation CONFIRMATION.json] [--rscript ...]`。样本量：`sample-size SPEC.json --out NEW_DIRECTORY`。输出目录必须不存在。脚本错误退出2表示输入/适用性阻断、3表示环境阻断；成功运行仍必须检查JSON中每项status，PARTIAL不等于全部分析成功。

字典：`{row_unit:"person", key:["id"], subject_id:"id", fields:[...], time_rules:[{before:"admission",after:"discharge"}]}`。
字段：`name,label,type,unit,unit_column,levels,reference,missing_values,required,min,max,role,available_at,derived_from_outcome`按实际填写。type仅number/integer/category/binary/date/string；levels与原表编码一致；二分类明确两级；缺失默认仅空字符串，NA/未知等须声明。单位不猜测。required是字段值必填，不表示所有统计强迫完整病例。min/max越界只报告，不静默删除；分析前绑定数据哈希记录range_review。默认原始列名/单行表头，复杂Excel头、合并单元格或公式先由宿主明确整理规则。

CRF交接：dictionary输出`crf-fields.json`保存原字段定义，schema=`ye1-crf-fields-v1`。本批已读项目CRF的`dictionary.tables`接口，另有实际适配命令：`import-crf CRF_DICTIONARY.json --table NAME --subject-id ID --out NEW_DIRECTORY [--data CRF.xlsx]`。明确选择表，保留原字段定义/时间锚/来源/缺失原因，将allowed_values转levels、datetime转date；按精确列标题规范化，不猜列。整行空白模板行跳过并保存源行映射；值格与__missing原因格保持分开并核矛盾。复杂约束/外键进入pending_crf_rule_review，分析前需绑定字典的crf_rule_review；不自动联表。导入只完成字段适配，不能替代CRF `accept-handoff`核现行方案/回传版本和资格；不是授权真实收集。`subject_id`与记录key分开；单患者多次住院/测量不能当独立患者。时间规则检查同一行先后，跨行死亡后再入院、时区、访视窗口和多表关系仍由宿主按研究定义检查；发现纵向/聚类需转适配方法，本执行器不伪装支持。

## 分析计划

计划含`research_question,population,estimand,design:"independent",row_unit,independence_basis,confirmed_by,confirmed_at,confirmation_statement,tasks`。确认必须来自用户/实际已有协议，不得为通过脚本编造。纯方案讨论无需这些执行字段齐备，交方案及OPEN项即可。任务含稳定`id,kind,missing,downstream`；downstream登记相应图表/段落ID，不指定必须全文重写。

任务接口：

- describe：`variables:[...]`，可`group`；`missing:"available_case"`，逐变量分母、均值/样本SD、type7分位数、分类n/%及缺失数。
- compare：`outcome,group,group_order:[first,second],method`。method仅welch_t、wilcoxon（正态近似＋连续校正，非自动中位数检验）、fisher（2×2条件OR）、chi_square（无连续校正，期望数均≥5）。paired_t使用`outcome,paired_with`同一行两次测量（每行独立受试者），不把长表重复行当配对；missing=complete_case。方法由方案选择，不根据显著性/正态性自动切换。Welch/paired输出第一项减第二项方向和CI；Fisher的无穷OR/CI明确编码字符串positive_infinity（非null/假有限值），交付解释无界。
- linear：`outcome,predictors,covariance:"classical"|"HC3",covariate_rationale,assumptions_review,missing:"complete_case"`。原单位线性效应及t区间，HC3仍用残余df的t近似；分类变量固定参照编码。残差/杠杆输出供宿主评估，异方差稳健SE不修复非线性、混杂或选择偏倚。
- logistic：同上但明确`event`，无需covariance；未惩罚二项logit MLE/Wald CI、log-OR/OR。非收敛、警告、极端拟合概率、奇异信息、秩亏阻断，不默默换Firth/惩罚法。最少类别/预测参数<10为本初版保守护栏，不是所有临床设计通用充分样本规则；不因此输出假估计。接近分离检测为保守数值护栏，不声称数学认证所有分离情形。
- prediction：二分类简单logit，`outcome,predictors,event,test_fraction:0.2..0.5,seed,feature_review:"CONFIRMED",prediction_time,outcome_horizon`。missing=complete_case或train_median。先按结局分层独立划留出，训练集中学习数值中位数/中心/尺度；不做变量筛选和调参，类别缺失排除，不借留出集填补。预测字段必须role非identifier/outcome、`available_at:"prediction_time"`、非derived_from_outcome；宿主仍核隐性泄漏、治疗后变量和时间定义。单次留出无外部验证/临床效用承诺。

输出`analysis.json`保存逐结果估计/样本量/参照/缺失方法/状态、输入SHA、库版本及重算范围。描述统计另出`descriptive-table.csv`，每行保留变量/组/统计量/单位/分母/缺失；`statistical-graphics-handoff.json`给真实分布点、分类值/缺失和回归森林图系数。`graphics-handoff.json`提供留出y_true、y_probability、源行、ROC点、校准分箱及精确二项区间。主集成图模块消费实际数组、沿用图形主题；此模块不渲染图。预测区间、校准斜率、DCA未计算时明确null/未计算，不能画成已验证结果。DCA须另核阈值/决策情境。

## 清洗、版本与共享事实

清洗规则绑定`source_sha256,reason,confirmed_by,confirmed_at,rules`。规则仅map、convert_unit（明确单位列/来源目标单位/factor/offset）、set_missing（指定原编码）、correct_cell（源行/expected_old/value）、drop_rows（逐源行及理由）。源行含表头，首数据行为2。用户已经明确的常规更正无需额外全套审批，但需要将实际来源写规则。保留原文件，输出cleaned.csv、逐单元变更和质控；不自动去重、不异常截尾、不暗填缺失。

更新用previous指向已选基线，验证其冻结文件哈希；普通数据更正按每项依赖列及行顺序计算签名，只重算受影响项，旧数据/结果/确认不覆盖。研究问题、人群、结局、方法、字典等定义变更须另给`actor,date,statement,from_plan_sha256,to_plan_sha256,to_dictionary_sha256`确认。更换协变量/规则不能伪装常规更正。

`state-patch.json`提供active_versions、本次事实来源、待核、失效结果ID与稿件确认失效标记。宿主将其合并到成果目录的同一`doctor-paper-state.json`或等价现有记录，保存原state，保留无关事实/术语/引文/已答信息；此执行器不悄悄改主线程state。总入口使用本接口时必须消费失效标记，不能继续沿用旧版已确认初稿。外部既有结果记录其真实来源及未复算状态，可单独解释，不要求回到整流程。

统计方案与结果语义属于宿主；执行器不会裁定临床因果、缺失机制可忽略性、混杂充分控制或可发表性。阴性不等于证实无效/等效，OR不是RR；禁止根据p挑模型或把P接近阈值写成趋势。未校正多重比较须明示探索性；主要/次要分析、敏感性、协变量时间和选择依据写入方案。

### v0.4.2 方案来源

分析方案与重大方法更改确认必须明确source_kind：simulated仅测试，direct_user须source_path（UTF-8实际原话）、source_locator及confirmation_statement/statement原话可核。省略为unknown而保留待确认，不以confirmed_by/日期/字符串冒真实科学确认；用户仍只需自然答复，由宿主忠实整理接口。旧记录可以读，执行新分析前需补核来源。脚本不认证身份。
