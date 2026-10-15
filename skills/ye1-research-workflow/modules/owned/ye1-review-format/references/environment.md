# 当前宿主的文本能力

先用实际工具判断能否读文本/完整附件、能否写文件、能否联网、能否执行代码，分别记AVAILABLE/UNAVAILABLE/UNKNOWN。首屏说明已读范围、眼前可完成部分和一个下一步。

本子技能的写作/阅读/解释由宿主完成，不以Python为前置。只有预览或摘要时限制结论范围，不能说全文已读。没有代码执行时仍可交可复制文本；没有文件写入就不要声称已保存、已生成机器哈希或已精确机器校验。没有联网可比对已有权威记录，但身份新核真保持未完成。数字、方法、阴性和证据强度不能因降级而改变，不伪造统计/图形。

已有Python时可用本包 scripts/task_io.py 辅助局部保存/数字token检查/英文空白分词计数/非空白字符计数/数字方括号引用对齐，只用标准库。没有Python不调用此脚本，改用明确标为人工的逐项核对；严格字数缺可信计数则待核。医生本机没有Python但平台提供已有执行器，可按权限使用该执行器；不因此默认把患者数据迁往云端。

本子包不含Word/PDF/统计引擎。缺对应能力先交文本及来源/范围/术语/数字/待续记录；需格式导出时使用当前宿主已有相应能力或另行选择总入口包，不阻断这次文本任务，不自动安装。任何后续导出必须沿用户实际选定版本，保留原件；文本审阅不等于已确认完整论文初稿包。

## v0.4.2 首次交付检查

分别记录：执行宿主、Python、R/jsonlite、读表、绘图、Word、PDF转换、页图工具、所需字形AVAILABLE/UNAVAILABLE/UNKNOWN。无Python不等于无R或无宿主执行器；无R仅阻本R引擎计算，不阻QC/文本/已有可信结果；无渲染器交可核Word/Markdown但不称PDF完成；无执行宿主交文本/计划/可携带材料，不假算。优先复用明确可用的已安装环境，不自动安装或改系统配置；all的PARTIAL_READY不是整个流程STOP。

排版前font_support.py检查实际正文所有字形（先标准库核显式YE1_FONT_PATH或现有macOS字体；不支持的格式才用显式已有绘图Python）；查不到字体检测能力或覆盖缺字时，保留已生成Markdown，DOCX/PDF待续，不能静默换英语。渲染边界使用本次任务临时fontconfig与已有字体目录，恢复原环境值；交付前实际转换并逐页看PNG，检查字体、图表裁切、孤标题和分页。PDF转换可用但页图工具不可用时保留PDF，视觉验收待续。导出成功不等于已视觉或科学验收。

确认来源按direct_user/simulated/unknown，省略source_kind不可当真实；用户无需编写JSON。全38入口仍独用，8只是快捷项。

## 中文Word/PDF字形支持范围

本模块复用随包 `scripts/font_support.py`，只检测已有字体，不安装或改系统设置。它先核显式 `YE1_FONT_PATH` 或现有macOS Arial Unicode字体；必要时仅调用宿主明确指定且已存在的绘图Python查找字体，并核实际文档字形覆盖。未找到完整覆盖时保留Markdown和checkpoint，DOCX/PDF待续。

若检测到的字体族为Arial Unicode MS，物化器会检测 `/System/Library/Fonts/STHeiti Medium.ttc`：当前macOS已有该文件时，仅Caption样式和Caption run的东亚字体槽使用Heiti SC，并保留粗体；文件不存在或当前不是macOS时关闭Caption粗体。其余文字继续使用字形预检结果。正式PDF路径须通过本模块 `scripts/render.py`，该脚本仅在当前任务临时fontconfig中使用已存在字体目录及明确给出的LibreOffice/Poppler运行时，不编辑全局设置。

局部验证范围为本机macOS、捆绑Python 3.12及当前已有字体/渲染器组合；Windows/Linux、其他Office和PDF转换器没有验证。绕过 `render.py` 的字体配置不在支持证据内；每份导出件仍须查看全部页图。
