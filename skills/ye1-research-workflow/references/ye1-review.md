# Ye1审阅排版与初稿打包

35 Ye1-审阅排版把已写好的真实稿件和图表制成客户审阅件；36 Ye1-初稿打包在用户确认对应版本后归集实物。两者不代替科研方案确认、通用撰稿或期刊最终合规判断。

## 排版

先核稿件版本、结果版本、语言和图表清单。通用中文初稿使用已有A4/字体/段落/表格规则，图表放首次相关正文引用附近。实际中文图内文字必须中文；文献原题名保留。默认中文/英文同事实分别表达，不凭编号正确声称全文一致。

宿主完整文章经compose.py读取冻结引用、数字绑定与图指纹后物化；已有document JSON可用materialize.py。只想格式审阅且没有完整证据时可排现有稿，但必须清楚说明内容未核，不填假的reference_review。确认包不得把内容待核写成投稿就绪。

没有Word/PDF能力先保存文本和checkpoint；恢复时用同版本文件补格式。有现成bundled渲染工具才用render.py，不调用用户桌面LibreOffice，不安装字体。导出后逐页看页图，核中文缺字/分页/图注/表格/数字/正文位置。技术结构检查不是视觉验收。

## 准备交付树

宿主根据用户选择列`ye1-review-selection/1`清单：artifacts条目含source（源根下相对文件）、target、sha256和classification。classification只能是manuscript、aggregate、method、public_evidence或supplementary_aggregate；逐行原始/清洗患者数据默认不能进包。每份稿的target在根或语言目录，其他材料一律放support/，防止文献原文PDF被误认为选择的稿件格式。

`review_delivery.py prepare SOURCE_ROOT --selection SELECTION --out NEW_REVIEW --receipt OUTSIDE/receipt.json`复制指定实物、核源指纹并返回required_files及版本指纹。保留分析代码/计划/聚合结果/引用证据，具体原始隐私材料仍在本地项目。清单是宿主审阅分类，不是自动脱敏检测。

准备回执记录的是审阅树文件；ZIP中的 `VERSION_CONFIRMATION.json` 会在打包时新生成，不能被更早的准备回执自引用。打包后必须使用 `archive_manifest()` 或 `package --receipt OUTSIDE/package-receipt.json` 写出独立包回执，逐个列出 ZIP 所有成员路径、字节数及 SHA-256，并说明确认文件的生成来源、版本指纹、模拟状态和身份认证状态。成员数必须与实际ZIP成员数一致；模拟确认仍需明确 TEST_ONLY，不得写成真实作者批准。

explicit required_files可以是用户实际选定的Word、PDF、Markdown或成对格式；不能把缺失所选件静默从清单移除。若同时选Word和PDF必须逐语言成对；审阅树不得夹带未选Word/PDF。无显式选择的旧API仍要求Word+PDF，避免旧调用变相放宽。

## 确认与包

先向医生交可打开的实际审阅文件与版本/格式摘要。取得明确确认“确认此版本作为初稿”（英文等义确认须忠实记录并映射到确认语句），记录实际确认人、原话来源、日期、所选格式及指纹，再调用confirm/package。单纯“收到”“再看看”、科研方案确认或开发许可都不算稿件批准。版本、结果、方法代码或证据任何变化使旧确认失效。

脚本保存声明，不认证真人身份；宿主不得生成假答复。合成测试使用API `synthetic_test=True`，打包必须`test_only=True`，产物标TEST_ONLY；CLI source-kind默认unknown。CLI 的 `package --test-only` 只允许明确模拟的测试记录生成 TEST_ONLY 包，不能授权真实交付。模拟记录不能授权真实包。未确认时可以交审阅稿，不能交“已确认初稿包”。

不要实际投稿、上传或发布；投稿信和审稿回复是文稿能力，执行投稿另需用户明确授权。

### v0.4.2 来源字段（宿主接口）

confirmation默认synthetic_test=None/source_kind=None，来源unknown，状态SOURCE_UNKNOWN；宿主自填actor/日期/字符串不足。真实引用记录用source_kind='direct_user', source_path=实际UTF-8原话记录, source_locator=消息定位；核原话存在并冻结来源哈希。CLI同名--source-kind/--source-path/--source-locator。来源被改或稿件被改均拒旧记录。simulated只测试；unknown不得打确认包，普通未确认审阅稿仍可交付。记录不认证真人或消息真伪，用户不需JSON；是否真实来自用户由宿主忠实核源。

自然原话与内部规范决定分别保存：source_quote/--source-quote保存实际医生措辞，statement为宿主忠实映射的明确版本批准。省略source_quote仅适用于原话恰为规范句；不要求医生照念固定句。收到/再看看/夸赞不等于批准，宿主不能为通过合同把含糊话映射为确认；脚本不验证该语义或身份。
