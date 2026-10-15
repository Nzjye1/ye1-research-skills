# 工作包与集成接口

技术入口：各Skill内的scripts/study_workpack.py。只需Python 3.10+；XLSX另需已有openpyxl。环境路径由宿主选择，不安装。六个入口使用相同脚本和规则，单独目录可完整携带；技能目录不写患者成果。源码规范版为module/study_workpack.py。

## 命令

下面PKG、SPEC、OUT均由宿主填实际路径。输出目录必须新建，防止覆盖；record/changes是宿主生成的JSON，不要求医生手填。

    python scripts/study_workpack.py create --spec SPEC --out PKG
    python scripts/study_workpack.py resume --package PKG
    python scripts/study_workpack.py confirm --package PKG --record CONFIRMATION
    python scripts/study_workpack.py export --package PKG --out PKG/artifacts/v1 --rows 200
    python scripts/study_workpack.py progress --package PKG --record PROGRESS
    python scripts/study_workpack.py amend --package PKG --changes AMENDMENT
    python scripts/study_workpack.py qc --package PKG --workbook RETURNED_XLSX --out PKG/returns/check1
    python scripts/study_workpack.py accept-handoff --handoff PKG/returns/check1/analysis-handoff.json

export --text-only强制文本。无openpyxl也会落文本并记TEXT_ONLY_OPENPYXL_UNAVAILABLE；没有假xlsx。resume及其他记录功能仅标准库。qc非可交接返回码2，能力/输入错误返回码3。空白表无数据为正常等待，eligible false。不得把这些码等同科学失败。

## study-spec

schema_version为ye1-study/1；study_id稳定；case_kind为SYNTHETIC或REAL_STUDY。顶层包括title、plan、collection、ethics、dictionary、facts、open_items，可加evidence、findings、proposal_options。

- plan：question/design/population/exposure/outcomes/time_anchors/confounders/analysis/burden。用可读文本或结构；样本量sample_size包含status（OPEN/ASSUMPTION/CONFIRMED）、rationale及所需假设，不能用工作表行数替代。
- collection：mode（RETROSPECTIVE/FUTURE_ROUTINE/MIXED）、setting/source/recording_method/staffing/period/known_unavailable；followup.included明确布尔。若true，须有capability_confirmed、doctor_agreed、source、schedule。程序核字段存在，宿主核真实性。
- ethics：review/institution/consent/local_data_use分别记录status和note；VERIFIED或EXEMPT_VERIFIED必须source/date，未提供用NOT_PROVIDED；SIMULATED_ONLY只准合成。
- facts：key、value、status、source、date；确认依据在来源，不从空白推断。
- findings：severity、status、affects（QC/COLLECTION/DESCRIPTIVE/CONFIRMATORY/PUBLICATION）、rationale、evidence_refs。沿用既有发表合同语义；此处不重新科学评分。
- dictionary.tables：每表name（小写ASCII，Excel≤31字符）、label、grain、primary_key、fields、可选foreign_keys/constraints。
- field：name/label/type/required/definition/unit/time_anchor/source/role/missing_codes。type为string/integer/number/category/date/datetime；unit无量纲写“无”。missing_codes为代码→原因字典，空字典表示不准编码缺失；category另allowed_values（字符串列表），缩写代码加value_labels说明含义。数值可加min/max，字符串可加pattern。主键必须必填且不可缺失。禁止将直接标识指定为共享字段。
- foreign_keys：fields、table、references（目标完整主键）；允许一人多次就诊，不自动判为重复患者。
- constraints：kind=order（left/right/op）或window（left/right/min/max，日期差可unit=hours/days），每项message解释含义。整数时间偏移的单位在字段中定义；不是任意临床规则语言。
- longitudinal（可选）：group_by、start、end；可加terminal_field和terminal_values。按同一对象的时点检查区间重叠及终止事件后再出现记录；只对明确配置的事件规则适用。

数值列留空＋相邻__missing原因列。每张原始表只有一行表头，无合并；表头含字段ID/中文/单位/必要标记。字典页和版本页核回传一致；导入他人表需宿主显式映射/定义确认，不静默改表头。数学范围是研究合同，不是临床正常值。

## 持久化、确认与变更

work-package.json只做一个活动版本指针及确认/事件/进度列表；versions/v0001/study.json等不可覆写，留SHA-256。每版附方案与dictionary.json。export通常存PKG/artifacts/v1，以便整个文件夹携带；生成文本和空CRF，附export-receipt。需要PDF/Word另入口，不伪导出。

确认record：study_id/revision/core_sha256（resume返回）、kind（SIMULATED/DOCTOR）、by/date/source/quote、covers。covers依次为population, exposure, outcomes, time_anchors, confounders, analysis, burden, dictionary。这里绑定的是已展示的核心方案，不是让医生逐字段填JSON；程序只能核一致性，不能证明自然语言确认或批准文件真实性。记录不具数字签名/防篡改安全认证。

amendment：base_revision/reason/source/date/replacements；replacements用JSON指针式已有路径→新值，例如/plan/outcomes或/dictionary/tables/1/fields/3/unit。仅替换已有项；增删字段可整体替换fields列表。不更换study_id或真实/合成身份。核心定义变更自动使旧确认不适用；同研究仍保留已答记录。影响真实批准的修订由宿主核机构要求。

## analysis-handoff

schema_version=ye1-analysis-handoff/1，含研究/活动版本、原表相对路径与SHA、方案/字典/收集/伦理、有效确认、findings、open_items及QC文件指纹。eligible不是任何方法/发表授权；下游不得忽略blocked_activities，需按已确认分析思路细化所需方法。合成只作演示。无清洗副本或统计值。

accept-handoff是最小接收适配器：新进程重读工作包、核当前版本、确认、原表和QC指纹，旧交接在方案更新后失效。搬整个工作包相对路径仍有效；外部原表另行搬移须显式source-override，包位置另用package-override，且哈希必须匹配。真实分析入口还需临床/统计适用性核对，不能将本接收适配器称实际分析已经运行。

## 明确边界

当前QC覆盖表头/字典/版本、类型/缺失、单/复合主键、外键、表内顺序/窗口及显式配置的同人时间重叠/终止事件后记录。未登记临床规则、自由文本内间接识别信息、复杂重复测量设计仍需下游/宿主核查，不能据机械PASS认定无问题。纯数值但填错单位时仅凭数值无法可靠自动识别。本模块不建立数据库、后台任务或安装依赖。
