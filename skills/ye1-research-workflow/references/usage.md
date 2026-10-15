# v04 使用与恢复

自然请求直接按SKILL路由；宿主实际已读文本无需Python。无执行入口、按任务探测、部分成果及续接见[环境分支](environment.md)。旧接口/科学闸门见[完整流程](full-workflow.md)、[v02接口](v02-integration.md)与[v03审阅](v03-review.md)。

Python脚本要求3.11+；xlsx需openpyxl、Word需python-docx、图像检查需Pillow、图形需NumPy/Matplotlib及实际字形；PDF/页图分别需显式已有bundled soffice/pdftoppm。不自动安装，不能称单一Python默认拥有全部包。

CLI推荐已有Python执行 scripts/safe_run.py pipeline doctor --request xlsx；缺所需包返回3。text自检成功不表示计算/Word/PDF通过。已有结果与文本阶段检查点在输出目录；环境失败保留，不冒称完整交付。现有固定分析/更正/compose命令和闸门参数沿旧接口。

review_delivery confirm须 --required-files 指向用户实际确认的相对DOCX/PDF路径JSON；不能从“看起来不错”推断确认。变动使旧确认失效。软件包可供用户自行选择复制，当前未安装、未上传；Windows/WorkBuddy/豆包未实测。
