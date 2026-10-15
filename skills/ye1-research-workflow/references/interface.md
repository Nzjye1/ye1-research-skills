> v0.3：完整宿主稿必须采用[冻结引用与审阅接口](v03-review.md)，下文旧reference_review声明字段不能单独通过。

> v0.2增量：本文旧命令的闸门参数须按 [新接口](v02-integration.md) 补齐；前置评估先于正式分析/全文。

# 输入与宿主写作接口

受限分析CONFIG由宿主代建；演示配置在交付包 `demo/input/config.json`。关键字段：

- `sheet`、`header_row`：分析表及表头行；公式拒绝，转值须核实；合并单元格列质控，不盲目展开。
- `mapping`：person、admission、admit_date、age、crp_first、crp_last、oxygen、stay_days；可选death_label。列名可任意，但语义须确认；固定CRP模式不能将别的指标偷偷映射为CRP。
- `units`：age=years，stay_days=days，CRP基准mg/L，单元格可带mg/L或mg/dL。只允许明确量纲，其他单位阻断。缺失空白/NA/未知/未查等保留。
- `scope=first_admission_per_person`、`method=descriptive-v1`、`paired_definition=last_recorded_minus_first_recorded`。
- `oxygen_values`：确认的0/1编码；未知值不猜。`followup`记录存在与可补状态、来源、日期。
- `confirmation`：status=confirmed，kind=doctor或simulated，source、date和decisions；模拟确认仅用于明确synthetic=true输入。宿主不得把自己选择方案当医生确认。
- `title`、`objective`、`population`：zh/en。仅受限合成全文使用；不能带患者级内容。

## 通用物化接口（撰稿由宿主完成）

`compose.py RESULTS_DIR HOST_DRAFT_JSON --out NEW` 消费聚合results.json及图资产。HOST_DRAFT_JSON：

```json
{
  "scientific_confirmation":"confirmed",
  "reference_review":"identity_and_content_checked",
  "zh":{
    "schema_version":"aggregate-materialization/1.0.0",
    "source_package_ref":"set-by-compose",
    "title":"真实研究待审稿题名",
    "paragraphs":[
      {"text":"摘要","evidence_ref":"abstract"},
      {"text":"首次住院共{{flow.people:0}}人。","evidence_ref":"results"}
    ],
    "tables":[],"figures":[]
  },
  "en":"同结构的完整英文document对象；本示意必须补全后运行"
}
```

示意不是可直接执行的完整稿。每语言必须具备摘要/Abstract、引言/Introduction、方法/Methods、结果/Results、讨论/Discussion、局限/Limitations和参考文献/References标题；正文须完整，未知声明保留。数值占位符 `{{variables.crp_first.median:1}}`表示源字段及小数位数。脚本填入同源数值，不猜结果。表格单元格当前为字符串，需宿主从同源结果构建并核；此接口不自动发现未绑定的散落数字或未知主张。

表对象：caption、columns字符串数组、rows二维字符串数组、evidence_ref。图对象：caption、relative_path（安全相对路径）、sha256、evidence_ref，资产在RESULTS_DIR，哈希必须对应当前版。下游materialize拒绝目录穿越/符号链接资产，核DOCX正文、表格、嵌图数量、数值token；这些检查是工程物化证据，不是科学接受。

真实文献另存证据JSON，至少包含身份来源、检索日期、题名作者年、DOI/PMID、内容支持位置、对应中文/英文主张和限制。v0.3 compose读取冻结reference_evidence与主张映射，生成首次引用编号并核证据指纹；不自动检索或理解原文。reference_review声明不能代替实际证据。固定演示 `references/evidence.json` 的2条方法参考已读取原始出版页，不能转用为临床疗效依据。
