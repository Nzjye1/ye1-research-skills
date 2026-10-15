# 客户审阅与引用接口（v0.4.1沿用v0.3科学边界）

来源：用户2026-10-13明确要求；本地实现，不绑定具体期刊。

## 审阅实物

中文标题、表格文字、图注和实际图内文字按中文路由；必要公认缩写和量纲g/L、mg/L、kg/m²可保留，天／岁写中文。中文文后的英文原题名保留。英文版独立英文。`language: zh/en`为可选文档字段，compose显式赋值；固定CRP按稿件标题识别。正文首次相关“图1／Figure 1”等引用后插入图表，引用缺失阻断。宿主应在首次相关段落按编号顺序引用，不靠附录放图。

A4、页边距上下2.3cm左右2.4cm；中文现有Arial Unicode MS，西文Times New Roman，复杂文字Arial回退；显式移除Word主题字体覆盖。正文11pt／1.35倍行距／中文首行0.74cm；摘要与文献不缩进；题名18pt、一级标题14pt、图表注10pt、表格9.5pt并居中。标题随下段，孤行控制；图与图注保持同页；表头跨页重复、行不拆，8行以内短表保持整体。并非所有中文核心统一标准。现有字体不能覆盖时停止并报告，不下载未知字体。DOCX必须实际渲染并逐页检查，字形／数值检查不替代视觉或科学审稿。

## 引文冻结

宿主稿顶层增加 `reference_evidence: {relative_path, sha256}`，路径指向RESULTS_DIR内冻结JSON。每条reference包含稳定id、原题名、DOI、核验日期、citation（完整文后字串）、local_source、source_sha256、content_evidence、read_level、limitations。实际读取相关全文并保存内容支持位置；仅metadata／摘要不得声明全文支持。`claims`包含reference_ids、paragraph_refs（正文evidence_ref）、status及evidence_location。正文以`[[R1]]`引用，不手填显示编号。compose按首次出现生成正文与文后编号；双语顺序必须相同；未知、未用、无主张链接、源哈希变化阻断。字段及哈希只证明冻结与链接，宿主必须核原文支持、相反证据与局限；本脚本不自动理解论文。

不设参考条数硬门槛。按疾病／暴露背景、方法、结果比较、解释、相反证据和局限盘点缺口。正文新增主张要新增支持或收窄；删除／更新来源后重核相应主张，重物化双语和PDF，并使旧版本确认失效。自动展示编号不证明文献全面或投稿就绪。

## 两个交付阶段

compose自动输出`CUSTOMER_REVIEW_PENDING`审阅稿；方案科学确认与稿件版本确认是不同事情。审阅文件可正常交医生查看。Skill软件zip可直接创建，不代表临床稿件确认。

只有明确确认当前版本作为初稿后，宿主才运行：

```sh
EXISTING_PYTHON scripts/safe_run.py review_delivery version REVIEW_ROOT
EXISTING_PYTHON scripts/safe_run.py review_delivery confirm REVIEW_ROOT --actor '实际确认人' --statement '确认此版本作为初稿' --date-utc '实际日期' --record OUTSIDE_ROOT/confirmation.json --required-files OUTSIDE_ROOT/selected-formats.json
EXISTING_PYTHON scripts/safe_run.py review_delivery package REVIEW_ROOT --record OUTSIDE_ROOT/confirmation.json --out OUTSIDE_ROOT/confirmed-draft.zip
```

不要把“收到”“可看看”、软件开发许可、模拟方案确认或宿主判断当客户稿件确认。确认包含全部审阅文件／结果／证据指纹，一次绑定版本；发生改变需重出审阅稿再集中确认，不逐文件弹窗。记录和zip放在审阅目录外，避免自引用。测试API明确`synthetic_test=True`只能配合`test_only=True`生成临时测试包；真实CLI没有该绕过参数。此记录依赖宿主忠实记录用户明确答复，不是身份认证系统。

`selected-formats.json`由宿主按用户实际确认的语言与DOCX/PDF路径生成，例如 `["zh/manuscript.docx", "zh/render/manuscript.pdf"]`。审阅树仅放实际选定的版本与配套证据；中英都选时必须含四个对应文件。若同时选择Word和PDF，两者须同语言同名配对；目录中不能混入未选Word/PDF。v0.4.1支持明确选择Word-only、PDF-only或Markdown-only，交付范围必须按选择标示，不能把缺件静默从已确认清单删掉。support/中的已分类证据PDF不当成稿件格式。旧API省略格式清单时仍要求Word+PDF。具体见[审阅与确认包](ye1-review.md)。
