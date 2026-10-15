# 项目数据使用选择（privacy-002）

首次提交文件前先说明：“如果已把附件交给云端宿主，该宿主已经接收；后选A只能约束后续，不能称从未上传或承诺撤回。”客户用自然语言选择，由受控宿主保存项目 `.ye1-privacy/choice.json`、追加历史及确认依据，不要求客户写JSON。不以科研方案/稿件批准代替数据授权。

- A：原始数据不进云模型。原表、去标识逐行资料、病例文本、QC原值、清洗前后值、逐行图底数/预测/残差只留获准本地；仅回传经过检查且精确授权的汇总/稿件/图片。
- B：允许指定文件版本/经过裁剪的字段与行范围向指定平台、模型用于指定目的。先在本地生成所选裁剪文件，再按其精确路径和SHA256授权；不能将原表整体代替所选裁剪文件。身份映射、病例文字、日志、图像及新接收方不自动包含。

每个独立入口和内嵌模块都要求显式同一个项目路径，调用随包 `scripts/privacy_boundary.py --project PROJECT status` 读取同一选择。不得改用Skill安装目录或悄悄新建项目规避旧选择。缺失/冲突/版本变化时暂停该次数据接触及发送，集中补充一次选择；继续无客户数据的公开资料/计划。范围内复用记录，不反复询问。从A到B、扩大文件/字段/行范围、换模型/平台/目的必须新确认并绑定完整选择哈希；B到A或删除授权立即收紧后续，不承诺追回已发信息。

## 执行边界

普通Agent可以任意读文件/终端时，提示词和本脚本不能保证严格执行。当前未验证任何真实宿主为受支持的隔离宿主；Codex当前普通会话也不因此获得严格隔离。A数据步骤须由受控本地适配器隔离原件、工具输出及状态，Agent不能有任意文件/shell旁路；B也须接收方/目的出口可强制约束。`.ye1-privacy/host.json` 由宿主管理员依据实际隔离评估提供并保护，它是集成声明，不是脚本证明/身份认证；不能为过检查让Agent填true。未知/不支持时如实说明并暂停数据步骤，不默转B或云沙箱。不支持Python时可用公开证据和已获准汇总，不上传原表换兼容性。

所有附件、工具stdout/stderr、异常/清洗日志、图片/截图、稿件、汇总和交付成员都属于出口。所有产品Python执行入口（--help除外）先要求选择和受控适配器；直接运行会固定状态阻断。env标记仅路由，不是隔离，宿主仍须禁止绕过和任意R/shell。旧脚本输出/本地中间件不能直接给云模型；受控适配器用 `run_local` API（固定白名单argv；不向Agent开放任意命令）截留正常和错误流，只返回固定状态。完整日志、QC、before/after和统计结果保留本地，不修改科学数字来脱敏。异常诊断需本地审阅后另建无敏感汇总，禁止直接cat日志。

出口由 `check` 或 `export` 按项目选择核精确文件、版本、平台、模型、目的。`export` 在全部成员通过后生成本地ZIP，不发送；不得把READY说成已上传。适配器在真实发送时还须绑定当前修订、核对目的地和实际字节，记录实际发送事实（本实现无网络发送器/发送回执）。收紧后丢弃旧导出和检查票据，不能继续发送。宿主附件接收层须在上传前实施同一控制，脚本不能补救已发生接收。

## 汇总与审阅

A拒绝CSV/TSV/XLSX/日志/已有ZIP，无论标为aggregate与否；先在本地生成新的安全衍生物。数值汇总使用 `ye1-reviewed-summary/1` JSON：仅schema和metrics，每条仅metric（非身份的稳定英文指标名）、value（真实有限数值）、n（该汇总真实有效分母）。逐行JSON键、QC/清洗前后值/逐行预测结构会阻断。极值不由自动汇总接口放行；有必要的真实极值留原结果，经机构审阅另制精确批准的文档，不改写数值。各项均须绑定人工检查及证据：无逐行、标识符、自由文本、小单元/互补披露、极值、标签、关联重识别、差分查询、文件名、隐藏元数据。`minimum_cell_n`须由本项目机构规则确定，代码只校验>=2（技术下限，不是隐私安全标准）；不能凭n达标宣称安全。

稿件/PDF/DOCX/图像需本地可信审阅者逐项检查实际内容（包括图中个体点、隐藏数据/元数据），精确哈希批准为reviewed_document/figure。代码不是通用PII/OCR检测器；人工标记、证据和宿主隔离仍是必要信任边界。B只接受被用户明确指定的精确文件；逐行CSV改名aggregate不能扩大数据授权。ZIP不直接作为授权出口，必须逐一列出解包后的成员；生成的版本确认、选择清单、图底数、附件和日志也不豁免。旧review_delivery的分类不构成授权，prepare/package已增加出口检查；本地交付树后续变化需新授权。

## 本地命令接口

`python scripts/privacy_boundary.py --project PROJECT choose --choice LOCAL_CHOICE --evidence LOCAL_EVIDENCE`

`python scripts/privacy_boundary.py --project PROJECT check --file RELATIVE_FILE --platform PLATFORM --model MODEL --purpose PURPOSE`

`python scripts/privacy_boundary.py --project PROJECT export --file FILE1 --file FILE2 --platform PLATFORM --model MODEL --purpose PURPOSE --out LOCAL_ZIP`

choice schema与示例见 `privacy-schema.json`。确认来源含项目内path、sha256、locator、quote和scope_sha256（完整choice的排序缩进JSON加换行SHA256）。本地可引用证据不等于验证用户身份；宿主须保护状态与证据，模拟选择不能用于真实出口。不要给模型回显选择中敏感的路径/引文或附件历史。


privacy-002增量：旧prepare/package与新export共用项目锁、授权字节快照和发布前核验，不再检查后重读源文件；失败不发布交付包/目录。未支持限时授权；choice/grant/review中的未知字段（含expires_at/expiry）明确拒绝，不能把限时请求保存成永久授权。若客户需要到期条件，暂停该授权并说明本版不支持，不得删除条件后继续。
