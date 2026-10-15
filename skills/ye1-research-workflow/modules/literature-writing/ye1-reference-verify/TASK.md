---
name: ye1-reference-verify
description: 核对DOI、题名、作者、年份和期刊等文献身份；支持旧权威记录对照，元数据相符不代表支持论文主张。
---

客户数据步骤前先继承[项目数据使用选择](../../../references/data-use-choice.md)；使用同一项目，缺失或宿主不支持则暂停。


# Ye1-文献核真

规范化doi前缀/大小写后，实际访问DOI注册机构、出版者或可靠索引，记录URL/获取日期与查得字段。对照题名、作者、年份、期刊及DOI；缺失DOI保持未查得，不能凭题名造DOI。检索不到不证明文献不存在；链接解析不证明所有字段相符。离线权威快照标记录日期和非新查证，仅格式可读不能称身份通过。输出 MATCH/MISMATCH/UNVERIFIED与字段差异，正文内容支持统一NOT_CHECKED；要评主张需真实原文另调用定位入口。

若主张或译文另有冲突，单列内容待核；不能靠一次身份核真一起放行。

先读 [共享事实与范围](references/common.md)。能力不明或附件/导出受限时再读 [环境分支](references/environment.md)。

本任务按需使用：[检索/阅读/证据](references/literature.md)。

纯文本由当前宿主实际完成。可选 [文本工具](scripts/task_io.py) 做局部保存/数字token/计数/数字引文核对；需要机器辅助时读 [轻量接口](references/interface.md)，结果不等于语义验收。
