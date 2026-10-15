---
name: ye1-claim-check
description: 判断实际读到的来源是否支持指定主张，核人群、设计、方向、因果及限制；区别文献身份真实和内容支持。
---

**客户数据前置：** 首次接收文件前、访问客户数据或回传任何工具/图像/交付前，先读[项目数据使用选择](references/data-use-choice.md)，继承同一项目A/B选择。缺失或宿主不能兑现时暂停该次数据步骤；不能以本地计算或兼容性声称未上传。


# Ye1-论据核查

逐条拆开句子的研究人群、构念/干预、时点、结局、方向与因果强度，对照实际原文、表格和方法。给 supported、supported_with_scope、conflicting、unsupported 或 unverified，附具体位置、可成立的最小措辞及未读范围。摘要支持只限其明确陈述，不以作者讨论推测代替结果。发现反证/限制保留；外部研究不能替本项目数值背书。输入只有 DOI/题录时先给缺口，必要时使用已有授权工具取得正文；不能凭标题完成内容核查。

先读 [共享事实与范围](references/common.md)。能力不明或附件/导出受限时再读 [环境分支](references/environment.md)。

本任务按需使用：[检索/阅读/证据](references/literature.md)。

纯文本由当前宿主实际完成。可选 [文本工具](scripts/task_io.py) 做局部保存/数字token/计数/数字引文核对；需要机器辅助时读 [轻量接口](references/interface.md)，结果不等于语义验收。

首次加载、依赖缺失、升级或移除时见[独立使用与环境](references/portable-use.md)。
