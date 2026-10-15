# 不依赖Python的能力分支

先由宿主检查实际可调用工具：能读文本、能读完整文件、能写文件、能执行代码、能联网、能渲染。分别记AVAILABLE/UNAVAILABLE/UNKNOWN；工具名称不是执行证据。首屏只讲已读到什么、当前能做什么和一个下一步。

1. 医生本机无Python但宿主已有执行器：优先使用宿主明确提供的现有环境，不让医生安装。患者资料不能因此默认迁移到云端。
2. 完全无执行但能读文本：适用入口可按实际文本直接完成阅读/解释/改稿/翻译/压缩/引用对齐；元数据新核真仍需联网或明确标为旧记录对照。没有写入就给可复制结果和交接。统计/绘图不能语言模拟，准确字数/机器核验无工具则待核。
3. 有Python缺部分依赖：按任务能力降级，缺Word/PDF库不阻文本。只探已有执行器，不扫整机、不改PATH、不安装。可选shell入口 scripts/launch.sh；无shell直接走上项，不先调用Python自检。

已有Python 3.11+时 `scripts/environment.py --request text|xlsx|docx|graphics|pdf|pages|all [--runtime-root EXISTING]` 实际import/版本探测。默认all逐项检查当前执行器及显式指定的绘图执行器，缺任何项返回3/PARTIAL_READY；缺当前请求能力返回3；text返回0只代表该请求，不表示全套可用。绘图另用已有DOCTOR_PAPER_GRAPHICS_PYTHON环境自检；中文字形由实际graphics接口核验，不静默改英文。PDF与页图各自检查，视觉仍需实际查看。

执行旧CLI使用 `scripts/launch.sh STAGE ...`（可用DOCTOR_PAPER_PYTHON指定已有路径）或 `EXISTING_PYTHON scripts/safe_run.py STAGE ...`；常见环境异常输出简短JSON、非零，并在已有输出目录保存诊断。无目录可写就只交错误回执。安全入口不吞科学Blocked。旧CLI仍保留；直接调用个别旧CLI可能原始报错，首屏不要粘贴traceback。请求只需文本时，可用materialize的--text-only仅物化Markdown；无需Word库。

检查点：分析先保存真实results及源/配置哈希，缺图仍有结果；materialize先写Markdown和checkpoint再导Word；PDF先保存再启页图。失败为待续，不能叫完整成功。`resume.py graphics OLD --out NEW`核固定CRP源/方案/结果后仅补图，不重算；其他宿主结果用已核聚合图数据由宿主续接。`resume.py pages PDF --tools TOOLS --out NEW`仅补页图。恢复DOCX用同一document JSON和资产新目录重新materialize，文本数字不变。成果变动使原确认失效。

客户确认包要求明确版本、确认人/原话/日期及用户实际选择的格式。v0.4.1显式清单支持Word、PDF或Markdown；旧无显式选择API仍要求DOCX+PDF。CLI confirm另给 --required-files JSON清单（用户实际确认语言与格式相对路径），遗漏所选文件、错配语言或目录中出现未选Word/PDF即阻断；先为实际选择整理独立审阅目录，record在版本目录外。软件安装包无需稿件确认。Markdown可以先作为未确认审阅稿；只有明确选择并确认该Markdown版本后，才可生成标明仅文本范围的确认包，不能称已交Word/PDF。

## v0.4.2 首次交付检查

分别记录：执行宿主、Python、R/jsonlite、读表、绘图、Word、PDF转换、页图工具、所需字形AVAILABLE/UNAVAILABLE/UNKNOWN。无Python不等于无R或无宿主执行器；无R仅阻本R引擎计算，不阻QC/文本/已有可信结果；无渲染器交可核Word/Markdown但不称PDF完成；无执行宿主交文本/计划/可携带材料，不假算。优先复用明确可用的已安装环境，不自动安装或改系统配置；all的PARTIAL_READY不是整个流程STOP。

排版前font_support.py检查实际正文所有字形（先标准库核显式YE1_FONT_PATH或现有macOS字体；不支持的格式才用显式已有绘图Python）；查不到字体检测能力或覆盖缺字时，保留已生成Markdown，DOCX/PDF待续，不能静默换英语。渲染边界使用本次任务临时fontconfig与已有字体目录，恢复原环境值；交付前实际转换并逐页看PNG，检查字体、图表裁切、孤标题和分页。PDF转换可用但页图工具不可用时保留PDF，视觉验收待续。导出成功不等于已视觉或科学验收。

确认来源按direct_user/simulated/unknown，省略source_kind不可当真实；用户无需编写JSON。全38入口仍独用，8只是快捷项。

## 中文Word/PDF字形支持范围

共享 `scripts/font_support.py` 只检查当前已有字体，不安装字体或修改系统设置：先检测显式 `YE1_FONT_PATH` 和已有macOS Arial Unicode字体；需要其他字体时仅使用显式已有的绘图Python查找候选，并验证实际文本字形覆盖。未找到覆盖全部字形的现有字体时，保留Markdown和checkpoint，DOCX/PDF置为待续，不改写为英文。

若中文文档选中的字体族是Arial Unicode MS，`scripts/materialize.py` 会检测 `/System/Library/Fonts/STHeiti Medium.ttc`。当前macOS上文件存在时，Caption样式及其直接run使用Heiti SC的东亚字体槽并保留粗体；文件不存在或非macOS时关闭Caption粗体，其他正文、表格和图表仍用字形预检选中的字体。`scripts/render.py` 使用任务级临时fontconfig和已有字体目录调用显式指定的现有LibreOffice/Poppler工具，不改系统字体或全局环境设置。字体检测或渲染工具缺失时保留已生成内容并标记待续；导出后仍须逐页查看。

已验证范围仅为本机macOS、捆绑Python 3.12、当前已有Arial Unicode MS与Heiti SC Medium、该包的 `render.py` 和指定LibreOffice/Poppler组合。其他macOS版本、Windows/Linux、Microsoft Word及其他渲染器未验证，不承诺跨平台一致；调用者若绕过产品renderer的字体配置，结果不在此验证范围内。
