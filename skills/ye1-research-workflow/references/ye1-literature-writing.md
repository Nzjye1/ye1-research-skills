# 文献与写作在总流程中的续接

2026-10-13：15项正式交付源已核指纹后合入。总入口内`modules/literature-writing/`保存完整自包含副本；安装总入口即可由宿主按需读取，不要求医生另装或依次点小Skill。

1. 研究问题/近邻阶段使用[文献检索](../modules/literature-writing/ye1-literature-search/TASK.md)。保存实际查询、日期、限制、原始命中和取舍。没有联网只可称已有材料模式；不能将本模块离线测试报告当成本项目已联网。
2. 进入证据阶段按[精读](../modules/literature-writing/ye1-paper-read/TASK.md)、[证据定位](../modules/literature-writing/ye1-evidence-locate/TASK.md)、[身份核真](../modules/literature-writing/ye1-reference-verify/TASK.md)、[论据核查](../modules/literature-writing/ye1-claim-check/TASK.md)区分身份、真实阅读范围和主张支持。主张缺引才[补引](../modules/literature-writing/ye1-citation-supplement/TASK.md)，不能只找同题目引用。
3. 已确认方案、实际结果、图表和证据放在同一成果项目。宿主执行[完整论文](../modules/literature-writing/ye1-full-manuscript/TASK.md)或[所选章节](../modules/literature-writing/ye1-section-write/TASK.md)，实际新写。引用使用稳定ID，双语共用事实和来源；[引用整理](../modules/literature-writing/ye1-reference-align/TASK.md)仅是编号/链接检查。
4. [润色](../modules/literature-writing/ye1-manuscript-edit/TASK.md)、[翻译](../modules/literature-writing/ye1-academic-translate/TASK.md)、[摘要](../modules/literature-writing/ye1-abstract-edit/TASK.md)、[全文一致性](../modules/literature-writing/ye1-manuscript-consistency/TASK.md)保持事实，反防御规则仍仅IMRaD。新分析要求返回分析阶段，不能在稿内假称完成。
5. 最终交[审阅与确认包](ye1-review.md)。[投稿材料](../modules/literature-writing/ye1-submission-materials/TASK.md)和[审稿回复](../modules/literature-writing/ye1-reviewer-response/TASK.md)只产草稿/实际修改记录；未知作者声明保持待核，不执行投稿。

## 状态与格式接口

项目的`ye1-project.json`记录阶段，真实原件/结果/文献/稿件留在项目内，阶段完成以这些实物为证据。`project.py complete`是宿主记账，不证明科学判断；必须先实际做相应工作。单段任务无需强制建全研究项目。

新模块[可选接口](../modules/literature-writing/ye1-full-manuscript/references/interface.md)的`citations.bind(payload, root)`与旧`scripts/references.bind(draft, root)`并存，**不可原位替换**。新接口支持单语、节选、摘要限界及双语同号；旧9来源/compose合同原样保留。宿主可先用新接口核证/编号，再把已写正文、真实表图交通用`materialize.py`；物化不写论文，不授予发表或用户确认。转换时保留原payload、ledger、bind receipt及对应段落ID，不能丢阅读层级或把未核标签改成已核。

真实用户确认沿用总项目合同；文献技术receipt不是科学或作者确认。任何来源/正文/结果改变都要重读受影响部分并更新下游状态，不能只换哈希使旧确认继续有效。
