# 研究准备、返表与分析统一续接

2026-10-13三个专项正式交付并已合入。总包内部保存自包含实现；医生只描述目标，宿主执行内部适配，不让医生填写schema或拼小Skill。

## 准备与数据起点

- 无表从[研究方向](../modules/study-design-crf/ye1-research-directions/TASK.md)、[近邻](../modules/study-design-crf/ye1-neighbor-comparison/TASK.md)、[发表可行性](../modules/study-design-crf/ye1-publication-feasibility/TASK.md)到[讨论方案](../modules/study-design-crf/ye1-study-design/TASK.md)。先固定研究问题/现实负担，再用[统计方案](../modules/data-analysis/ye1-statistical-plan/TASK.md)与[样本量](../modules/data-analysis/ye1-sample-size/TASK.md)细化。缺假设只交计划，不制造目标样本。
- 明确用户确认后[生成CRF](../modules/study-design-crf/ye1-crf-design/TASK.md)。工作包保留方案、字典、确认及收集版本；正常等待即可，不自动催收。返表先[恢复和QC](../modules/study-design-crf/ye1-collection-resume/TASK.md)，`workflow_bridge.py receive`重读现行合同并登记到总项目。
- 数据到手即[字典](../modules/data-analysis/ye1-data-dictionary/TASK.md)、[质控](../modules/data-analysis/ye1-data-qc/TASK.md)与首反馈。已有Excel同样从原表和自然目标开始。CRF返表必须先accept-handoff，再import-crf；仅接受两种已知精确表头版本，不能猜列/联表。复杂外键/约束需核已完成的CRF检查和剩余规则。

## 实际分析

按已确认规则[清洗副本](../modules/data-analysis/ye1-data-clean/TASK.md)，选[描述](../modules/data-analysis/ye1-descriptive/TASK.md)、[关联](../modules/data-analysis/ye1-association/TASK.md)或[预测](../modules/data-analysis/ye1-prediction/TASK.md)。统计需要已有R+jsonlite，XLSX需要已有openpyxl；缺少则保留输入/QC/计划，不能伪造结果或自行安装。

`workflow_bridge.py analyze`先核总项目阶段、当前方案确认、原表转换来源和方法审阅文件，再调用已合入执行器。方法审阅`ye1-method-review/1`由宿主据实际材料生成，包含inputs={data,dictionary,plan}文件SHA、plan_confirmation_sha256、lineage各实物SHA、allowed_task_ids、requested_activities、synthetic_only与rationale。它记录宿主完成的临床/统计适用性判断，不是系统代替用户签科学确认。CRF eligible只是机械可接收，CRITICAL活动限制照常执行；合成状态不能改成真实。

执行器结果每项status分别核；PARTIAL不能说所有分析完成。适用范围是独立行/宽表配对、有限固定回归和独立留出，非通用复杂模型平台。依次读有效n、分母、参照、缺失、区间和诊断，再做[解释](../modules/data-analysis/ye1-results/TASK.md)与[真实绘图](ye1-graphics.md)。非显著不证实等效，不能按p改模型。

`workflow_bridge.py merge-analysis`核当前analysis与state-patch实物，合并分析版本/事实/影响，保留无关术语和证据；更新使旧图/全文/稿件确认失效。调用[分析更新](../modules/data-analysis/ye1-analysis-update/TASK.md)时旧结果不覆盖，只重算依赖项，定义/方法变化回到新方案确认。旧正文中未登记的受影响主张仍须宿主查找，不能仅凭依赖列表自动宣布无需复核。

总进度分析完成前必须已有实际图和宿主结果核读。然后进入[文献写作](ye1-literature-writing.md)及[审阅交付](ye1-review.md)。所有内部操作可由一次医生自然请求带领完成。
