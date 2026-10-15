---
name: ye1-crf-design
description: 把已讨论的研究方案与变量字典生成可填写Excel CRF，含字段校验、单位、缺失码与纵向关联。
---

客户数据步骤前先继承[项目数据使用选择](../../../references/data-use-choice.md)；使用同一项目，缺失或宿主不支持则暂停。


# Ye1-CRF设计

宿主根据当前研究编写通用study-spec，不套合成疾病列名。确认后导出实际CRF；缺伦理可出明确草案。检查每表粒度、关联键和时间锚。无openpyxl交文本，无执行器不伪XLSX。

先读[临床到研究的共同规则](references/workflow.md)，按当前请求完成这一项，不强迫重走全部流程。已有研究工作包先读回，区分CONFIRMED/ASSUMPTION/OPEN，不能由宿主代签医生或伦理确认。

需要保存版本、生成CRF或机器QC时读[接口](references/interface.md)，用已有环境的scripts/study_workpack.py；没有执行能力读[文本分支](references/no-execution.md)。脚本只负责记录和机械校验，研究设计/近邻判断由宿主依据医生情况与实际证据完成。
