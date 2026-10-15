# v0.2 接口与执行边界

2026-10-12 UTC，来源：本轮接续委派，理由：真实接入图形及前置发表评估，保留v0.1只读。

本文补足原usage/interface中的v0.1命令；旧示例省略的闸门参数在v0.2均必须提供。profile仅盘点结构，不分析或授权。

```sh
python scripts/publication_gate.py CASE.json --root EVIDENCE_ROOT --out NEW_GATE
python scripts/pipeline.py inspect INPUT --config CONFIG --out NEW --gate NEW_GATE/gate.json --case CASE.json --evidence-root EVIDENCE_ROOT --question '原病例问题'
python scripts/pipeline.py analyze INPUT --config CONFIG --out NEW --gate NEW_GATE/gate.json --case CASE.json --evidence-root EVIDENCE_ROOT --question '原病例问题' --activity DESCRIPTIVE
python scripts/compose.py RESULTS DRAFT --out NEW --gate NEW_GATE/gate.json --case CASE.json --evidence-root EVIDENCE_ROOT --source INPUT --question '原病例问题'
```

QC读qc_allowed，描述读descriptive_exploration_allowed，确认性读confirmatory_effect_allowed，真实草稿读research_draft_allowed。run为合成全文演示；compose合成另传--synthetic-demo并要求simulated，不当真人批准。STOP投稿仍可做许可QC/描述。病例须绑定数据源SHA256、问题、证据路径/哈希、关键问题作用范围。结果源哈希必须匹配原表。当前接口依赖宿主真实填证据；不能核证宿主判断的科学真值，也不能发现所有未绑定数字/语义错误。

图形主依赖为NumPy>=2、Matplotlib；本机已有3.11.0实测。主物化Python 3.12与系统绘图Python 3.14分开运行，用DOCTOR_PAPER_GRAPHICS_PYTHON显式指定已有环境。字体按现有coverage查找；不复制字体。render仅用明确的bundled LibreOffice/Poppler，不绕过浏览器file限制。

当前可执行工程示例：[synthetic-contract-002](publication/cases/synthetic-contract-002.json)。以 references/publication 为证据根，仅测试两行自编合成数据的绑定与QC/描述权限；不作科学或投稿示例。5个旧案例已显式退役，原件仅留历史开发/审计记录；不再作为pipeline/compose可执行输入，不更改原科学结论，也不把隔离占位的哈希当原证据。真实项目由宿主新建完整来源根与当前方案，不能继承合成许可。

```sh
python scripts/publication_gate.py references/publication/cases/synthetic-contract-002.json --root references/publication --out NEW_TEST_GATE
```

历史trial-facts中的路径/哈希仅是原项目证据定位，不包含在发行包，不代表离线可复核。近邻比较的内部原件不随产品分发；公开PMID/DOI可重新查证，不能以占位JSON冒作已读原证据。报告仍应覆盖实际研究临床价值、证据、局限和下一步；分析后/全文后重核充分性，不继承投稿许可。
