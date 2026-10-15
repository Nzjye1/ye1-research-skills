---
name: ye1-publication-feasibility
description: 根据临床价值、近邻增量、设计和证据评估发表可行性，给有依据的继续或调整建议。
---

客户数据步骤前先继承[项目数据使用选择](../../../references/data-use-choice.md)；使用同一项目，缺失或宿主不支持则暂停。


# Ye1-发表可行性

输出七维分列反馈和实际建议。CRITICAL/ADVISORY仅影响相应活动；小样本、阴性、期刊未定、摘要级阅读不机械STOP。不承诺SCI/核心、录用概率，不通过改指标追显著或追通过。

先读[临床到研究的共同规则](references/workflow.md)，按当前请求完成这一项，不强迫重走全部流程。已有研究工作包先读回，区分CONFIRMED/ASSUMPTION/OPEN，不能由宿主代签医生或伦理确认。

需要保存版本、生成CRF或机器QC时读[接口](references/interface.md)，用已有环境的scripts/study_workpack.py；没有执行能力读[文本分支](references/no-execution.md)。脚本只负责记录和机械校验，研究设计/近邻判断由宿主依据医生情况与实际证据完成。
