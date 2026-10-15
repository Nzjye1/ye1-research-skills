# 可选轻量接口

医生输入始终可以是自然语言和现有材料。这些是宿主可选检查接口，由宿主生成；没有 Python 时按规则直接交文本/人工对照，不让客户填写 JSON。

所有路径相对当前 Skill。仅运行该入口实际包含的脚本。Python 3.11+、标准库，无网络/额外模型/新安装；单独复制该 Skill 目录即可使用所含资源。辅助脚本的成功不证明阅读、身份或语义判断真实完成。

## 各包都有的 v04 原字节工具

```text
python3 scripts/environment.py --request text
python3 scripts/task_io.py count draft.md --mode words
python3 scripts/task_io.py align body.md references.txt
python3 scripts/task_io.py save original.md replacement.md --start 0 --end 42 --out NEW_DIR
```

save 字符范围由宿主定位，保留原件、范围外原文和数字 token 多重集；已有目录拒绝覆盖。前次 result.md 可用 --previous 前次目录核指纹。数字相同不检测位置调换、单位或因果，必须实际逐项读。align 只识别数字方括号/范围，其他风格交宿主；count 是空白词数或非空白字符，非期刊专有规则。

## citations.py（仅含此文件的文献/写作包）

`metadata submitted.json authority.json` 对照给定题录。submitted 字段为 doi/title/authors/year/journal；authority 为 `{record: 同字段, url, accessed_at, mode}`，mode 如 CACHED_RECORD / LIVE_RETRIEVAL。只有实际访问后才用后者。输出 MATCH/MISMATCH/UNVERIFIED、缺字段和差异，始终 CONTENT NOT_CHECKED、仅给定记录对照。无 DOI 可由宿主依据可靠题录人工核身份；脚本完整字段比较会将 DOI 缺失标待核，不能因此说文献不存在。

`bind payload.json --root MATERIALS --out NEW_DIR` 从已冻结材料物化稳定引文；不自动抓文献、写论文或判支持。输入形状：

```json
{
  "reference_evidence": {"relative_path": "ledger.json", "sha256": "宿主计算的真实指纹"},
  "numbering_language": "zh",
  "documents": {"zh": {"paragraphs": [
    {"id": "intro-1", "text": "宿主真实写好的句子[[R1]]。", "claim_ids": ["C1"]}
  ]}}
}
```

ledger 的 references 每项含 id、citation（真实书目串）、doi/pmid/url 至少一项、read_level、source（relative_path/sha256）、identity（status、record_url、checked_at、mode）。内容源的快照路径必须在 MATERIALS 内，拒绝跳出/符号链接/指纹变化。身份 unresolved 仍可交待核草稿，只不使用本辅助器宣布引用核证完成。

claims 每项含 id、status、reference_ids、locations（语言→段落 id）、text_sha256（语言→当前带稳定引文的整段指纹）、evidence（每项 reference_id、location、scope）。status 是宿主实际阅读后的判断。supported/supported_with_scope 可绑定；unsupported/conflicting/unverified 须先改主张或保留 OPEN 草稿。表述“该研究未发现明确关系”可以是 supported；不能把该来源的阴性结果静默删去。local_result_only 无外部 reference_ids，真实结果仍需独立数字来源核对。

read_level 使用 METADATA / ABSTRACT / EXCERPT / FULL_TEXT_RELEVANT_SECTIONS / MAIN_FULL_TEXT。METADATA 不支持正文；ABSTRACT 的 evidence.scope 只接受 abstract；EXCERPT 只接受 excerpt 并在 location 写所见章节；全文级接受 abstract/excerpt/methods/results/discussion/table/figure。补充材料未纳入这个简化机器接口，宿主另记且不得假称已核。保存摘录不能凭标签证明阅读全文；宿主仍须说明真实阅读范围。

两语为对应完整范围时，documents 放 zh/en，相同 claim_id 映射各自段落/文本指纹。两语来源集合与主张集合须一致；可以不同语序，显示号统一用 numbering_language 首现顺序。单语只放一个语言；不对应的双语节选分别处理并解释范围。输出 bound.json 和 receipt.json，仅引用到的资料进入每语 bibliography，unused_library_ids 仍留资料库。不能把自动编号算作内容支持通过。

来源文件、ledger 或主张文本/位置变化会失败，宿主重新阅读受影响部分后另立版本和新指纹；不得只更新哈希跳过重核。原稿确认失效由总入口续接，不把本 receipt 当用户确认。

## review_contract.py（仅含此文件的全文/一致性/投稿包）

`facts records.json` 比较宿主已映射事实：每行 id、location、quote 以及 value/unit/denominator/time/reference_group/relation/polarity；同一事实 id 在多位置/两语用多行。不适用项可 null，但缺字段标不完整。脚本不从自然句自动提取，也不检查漏登记事实；同样数字但含义反转必须由宿主阅读并正确映射。

`declarations records.json` 每行 id/status/draft_text。CONFIRMED 必须含 confirmation 的 source/date/quote；OPEN/DISPUTED 必须 asserted_as_fact=false，并在草稿标“待作者确认”。ethics / author_agreement / conflicts_of_interest / exclusive_submission 缺少即待确认。脚本不证明确认引语真实，宿主必须查原答复；公开材料不代替作者确认。其他如基金/同意/数据声明按需求另列。

`responses records.json --root MATERIALS` 每条 id/comment/response/status/asserts_completed；status 为 PLANNED、NO_CHANGE、COMPLETED。PLANNED 不得声称已做，NO_CHANGE 需 rationale；COMPLETED 必须有 changes，其中每项 before/after（relative_path/sha256）、old_quote/new_quote、version/location。实际前后文本须变化且摘录存在；页行只有真实固定稿才用。kind=analysis/experiment 还需 execution_evidence（冻结文件）及 execution_quote；这只是证据链接，不能证明实验真实性。部分完成拆子点。正则只辅助发现少数明显已完成措辞，不是自然语言可靠判定器。

exit 0 为该技术检查可通过；2 表示冲突、待做/待确认或输入验证阻断。正常 DRAFT_PENDING 是有用草稿，不是任务失败，更不是投稿许可。
