---
name: ye1-collection-resume
description: 保存研究收集进度并跨会话恢复工作包；回传数据后核方案版本、定义和完整性再交分析。
---

客户数据步骤前先继承[项目数据使用选择](../../../references/data-use-choice.md)；使用同一项目，缺失或宿主不支持则暂停。


# Ye1-收数与续接

先resume识别同一研究、版本、已有答复和待办。等待收数正常且不安排后台催收。qc核原表后交analysis-handoff，下游另核临床与统计方法；不在此清洗、统计或冒称已分析。

先读[临床到研究的共同规则](references/workflow.md)，按当前请求完成这一项，不强迫重走全部流程。已有研究工作包先读回，区分CONFIRMED/ASSUMPTION/OPEN，不能由宿主代签医生或伦理确认。

需要保存版本、生成CRF或机器QC时读[接口](references/interface.md)，用已有环境的scripts/study_workpack.py；没有执行能力读[文本分支](references/no-execution.md)。脚本只负责记录和机械校验，研究设计/近邻判断由宿主依据医生情况与实际证据完成。
