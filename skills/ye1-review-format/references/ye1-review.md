# Ye1审阅排版与初稿打包

35 Ye1-审阅排版把已写好的真实稿件和图表制成客户审阅件；36 Ye1-初稿打包在用户确认对应版本后归集实物。两者不代替科研方案确认、通用撰稿或期刊最终合规判断。

## 排版

先核稿件版本、结果版本、语言和图表清单。通用中文初稿使用已有A4/字体/段落/表格规则，图表放首次相关正文引用附近。实际中文图内文字必须中文；文献原题名保留。默认中文/英文同事实分别表达，不凭编号正确声称全文一致。

本独立入口直接接收外部Word、可读PDF、Markdown或文本稿，以及用户提供的表格/图形；不要求先运行总流程，也不要求旧项目包。宿主实际读出稿件段落、表格与图题，按所选排版范围把它们整理为materialize.py的内部document合同，逐项保留原文、数字、单位、引用和正文图表位置；内部JSON由宿主建立，不交医生填写。只能看到PDF/图片的一部分时标未读范围，不能假称全文已导入。

使用本包scripts/materialize.py实际生成审阅Word/Markdown，现有渲染环境支持时再用scripts/render.py生成PDF并逐页看。宽表独立置于横向页面，明确配置 East Asian 字体。不得用硬编码未经当前运行宿主验证的字体名创建替代 Word。实际逐页检查字形、重叠、表格、图注、数字、分页和正文位置，机器文本核对不能代替视觉验收。没有图源时保留现有可用图或标待补，不估读数值重绘。这里无需旧compose.py，引用内容/科学事实未核就明确“仅排版、内容未核”，不填假的reference_review或投稿就绪声明。

排版前还要按文档中的实际显示尺寸检查图内标签；若标签太小，不要把整图或正文一并缩小。存在图源/明确汇总数字时可调用图形重绘入口生成更大文字的新图，先保持数据和科学含义不变并给出来源/限制，再在Word/PDF实际渲染中核对；只有无法核实图源时才保留原图并明确标为待处理。英文坐标、图例与脚注按最终文档显示大小至少10 pt，图题和正文引用需配套保留；物化合同的`display_width_cm`可在8–15cm内明确设定，以保证图中文字不被再次缩小。

如果证据显示正文存在未支持的因果或其他高风险断言，不改作者原文；宿主应提供基于可见证据的 `review_warnings`，锚定原段落并在相邻位置插入醒目的 `AUTHOR REVIEW REQUIRED` 提示，同时保留独立审阅说明。警告不代表机器自动发现或作者已修改。

每次输出保存到新版本目录。复用用户指定的上一版或再次输入外部稿件，保留此前源文件/审阅件；同名覆盖被拒时改为新目录，不强迫重走研究链。缺Word/PDF工具只交实际可生成部分及续接记录。

没有Word/PDF能力先保存文本和checkpoint；恢复时用同版本文件补格式。有现成bundled渲染工具才用render.py，不调用用户桌面LibreOffice，不安装字体。导出后逐页看页图，核中文缺字/分页/图注/表格/数字/正文位置。技术结构检查不是视觉验收。

## 准备交付树

宿主根据用户选择列`ye1-review-selection/1`清单：artifacts条目含source（源根下相对文件）、target、sha256和classification。classification只能是manuscript、aggregate、method、public_evidence或supplementary_aggregate；逐行原始/清洗患者数据默认不能进包。每份稿的target在根或语言目录，其他材料一律放support/，防止文献原文PDF被误认为选择的稿件格式。

`review_delivery.py prepare SOURCE_ROOT --selection SELECTION --out NEW_REVIEW --receipt OUTSIDE/receipt.json`复制指定实物、核源指纹并返回required_files及版本指纹。保留分析代码/计划/聚合结果/引用证据，具体原始隐私材料仍在本地项目。清单是宿主审阅分类，不是自动脱敏检测。

explicit required_files可以是用户实际选定的Word、PDF、Markdown或成对格式；不能把缺失所选件静默从清单移除。若同时选Word和PDF必须逐语言成对；审阅树不得夹带未选Word/PDF。无显式选择的旧API仍要求Word+PDF，避免旧调用变相放宽。

## 确认与包

先向医生交可打开的实际审阅文件与版本/格式摘要。取得明确确认“确认此版本作为初稿”（英文等义确认须忠实记录并映射到确认语句），记录实际确认人、原话来源、日期、所选格式及指纹，再调用confirm/package。单纯“收到”“再看看”、科研方案确认或开发许可都不算稿件批准。版本、结果、方法代码或证据任何变化使旧确认失效。

脚本保存声明，不认证真人身份；宿主不得生成假答复。合成测试使用API `synthetic_test=True`，打包必须`test_only=True`，产物标TEST_ONLY；CLI source-kind默认unknown；明确simulated仍只能通过API test_only出TEST_ONLY包。模拟记录不能授权真实包。未确认时可以交审阅稿，不能交“已确认初稿包”。

不要实际投稿、上传或发布；投稿信和审稿回复是文稿能力，执行投稿另需用户明确授权。

### v0.4.2 来源字段（宿主接口）

confirmation默认synthetic_test=None/source_kind=None，来源unknown，状态SOURCE_UNKNOWN；宿主自填actor/日期/字符串不足。真实引用记录用source_kind='direct_user', source_path=实际UTF-8原话记录, source_locator=消息定位；核原话存在并冻结来源哈希。CLI同名--source-kind/--source-path/--source-locator。来源被改或稿件被改均拒旧记录。simulated只测试；unknown不得打确认包，普通未确认审阅稿仍可交付。记录不认证真人或消息真伪，用户不需JSON；是否真实来自用户由宿主忠实核源。

自然原话与内部规范决定分别保存：source_quote/--source-quote保存实际医生措辞，statement为宿主忠实映射的明确版本批准。省略source_quote仅适用于原话恰为规范句；不要求医生照念固定句。收到/再看看/夸赞不等于批准，宿主不能为通过合同把含糊话映射为确认；脚本不验证该语义或身份。
