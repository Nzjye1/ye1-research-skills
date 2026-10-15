# 宿主执行与恢复

这是宿主内部操作说明，医生不必阅读或执行命令。先读项目已有`ye1-project.json`与`进度.md`（或无工具时等价的可复制记录），再加载相关模块；首次目标/原始资料在任务成果目录落盘，不能把项目写进Skill安装目录。

## 已有数据

用实际已有Python执行`project.py start PROJECT --mode existing_data --goal '医生原话' --source ORIGINAL`；只有明确合成输入加`--synthetic`。它复制原件并做格式结构盘点，不能代替临床语义QC。宿主接着实读相关表格，确认行单位、主键、重复层级、时间与单位，保存首反馈与QC结果。新字段不用固定CRP模式。

随后实际公开检索近邻，在现有`publication_gate.py`合同中保存有依据的判断，引用证据、原表与问题指纹；近邻比较须在正式分析前。说明哪些缺口影响QC、描述、确认性分析、写稿或投稿，不能简单把七维全AND。合成案例只能通过工程路径，不声称临床创新。

`project.py complete PROJECT qc --outputs qc/report.md qc/quality.json --summary '实际发现' --next '收敛问题并比较近邻'`登记现有实物。按同一方式登记feasibility；它只核文件和先后依赖，科学语义仍由宿主实际完成。

## 准备收数据

`project.py start PROJECT --mode plan_collection --goal '医生原话'`保存实际门诊条件。研究准备模块负责方向/近邻/发表判断/设计，数据分析模块负责统计方案与样本量；在具体模块未交接或缺运行能力时保留待完成状态，不用空CRF冒充确认方案。

方案后生成CRF与字典，登记crf实物；收数期间状态保持等待用户返表。数据回来，先把实际文件与收集版本核对记录存到项目内，再执行`project.py returned-data PROJECT inputs/returned.xlsx collection/return-note.md`；该动作只登记收到返表，之后必须做QC，不能直接标分析完成。

## 方案与真实确认

方案文件包含研究问题/目标、人群/单位、结局/时间、暴露/协变量、方法、缺失与敏感性、支持及限制。方案形成后`project.py plan PROJECT plan/plan.json`转等待用户确认。宿主用医生话术集中给方案与必要问题，已有答复不重复询问。

确认记录包含`kind: user`、actor、quote、date_utc、source_path、`decision: CONFIRM_PLAN`、`target_sha256`。source_path为项目内实际用户答复记录；quote必须能在来源找到，target_sha256必须匹配当前方案。随后`project.py confirm-plan PROJECT plan/decision.json`。这只是可追溯记录，不是身份认证；禁止宿主假造用户答复。工程合成演示改为`kind: simulated_user`并在答复文件明确“模拟用户”；真实项目拒绝模拟确认。方案确认与最后稿件版本确认分别保存。

## 计算、证据、写稿和审阅

用适合当前问题的已确认方法实际计算。固定CRP适配器之外，新脚本由宿主/已交接统计模块提供并保存代码与执行记录。聚合结果保留未舍入值、分母、单位、缺失和方法；图源保留数据与指纹。先核结果再写全文，不能拿预制模板换数说明通用宿主能力。

complete按顺序登记analysis、evidence、manuscript、review。每一步都须先完成上游并指向真实文件；状态登记不能替代运行或阅读。结果数字绑定接口及参考ledger按[接口](interface.md)与[审阅规则](v03-review.md)；宿主补查未绑定数字、双语含义、引文支持与相反证据。

图形按[图形专项](ye1-graphics.md)，排版和交付按[审阅与确认包](ye1-review.md)。最后用明确选定的交付清单准备独立审阅树，用户确认该树当前指纹后打包；分析原始逐行患者数据默认不进交付树。用户要求收数续接到论文的完整链路时，须继续到双语完整稿、同源图表嵌入、Word/PDF实际渲染和逐页查看、以及清晰标为 `TEST_ONLY` 的版本绑定包；缺科学确认或目标产物前提时记阻断并停止，不得把部分QC/分析写成完整流程。最终持出前枚举包成员并扫描该次合成材料中的哨兵ID/原始行；该检查不构成普遍脱敏认证。

## 跨会话与变更

`project.py status PROJECT`重建进度并检查已登记证据是否变动。变化会显示STALE_REVIEW_REQUIRED，下游不能冒用旧完成状态；保留旧项目版本后在新目录修订。纯数据更正可沿已确认且仍适用的科学方案重跑，修改定义/方法要新的科学确认。不要覆盖旧证据来消除提示。

本地脚本不自动搜索、判断创新、写通用文章或认证用户身份。没有写入/执行工具时交可复制进度与已完成文本，精确哈希/全表QC/计算/文件导出保留未完成。
