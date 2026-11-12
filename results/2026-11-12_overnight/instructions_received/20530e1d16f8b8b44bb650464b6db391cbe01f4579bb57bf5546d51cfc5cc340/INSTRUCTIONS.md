# INSTRUCTIONS（只追加，按编号执行）

先读同目录的 PROTOCOL.md。本文件中的指令由审核者（Claude）在用户授权下写入。

---

## I-001（2026-11-12 01:40 美国太平洋时间）夜间任务完整说明

本条替代用户今晚在对话中给你的"夜间自主任务"和"补充修正"两段说明；两者有冲突时，以本条为准。

用户在睡觉。按本文件和 PROTOCOL.md 的默认规则自行决定，每个决定写进 DECISIONS.md，不要停下来等人。所有输出放在实验分支的 `results/2026-11-12_overnight/` 下（论文副本除外，见第 3 部分）。

### 时间

- 2026-11-12 08:00 美国太平洋时间（= 2026-11-13 00:00 北京时间）之后，不再启动新的运行。
- 08:45 太平洋时间（= 00:45 北京时间）之前，完成全部报告并推送。
- 每完成一道题的一轮三组，就更新一次 PROGRESS.md 和 STATUS.md，保证中途停止时已有结果也能直接使用。

### 第 1 部分：SkillsBench xlsx held-out 评测（最高优先级）

1. **版本**：只使用 xlsx 冻结第 11 轮版本作为 with-CogniLife-skills。记录版本标识和文件 hash。不运行任何新的进化轮次，不修改任何 skill、门控或流程。
2. **题目**：`results/xlsx-family/heldout/BATCH_REPORT.md` 中的 8 道题，按表中顺序：shock-analysis-demand、shock-analysis-supply、reserves-at-risk-calc、powerlifting-coef-calc、xlsx-recover-data、invoice-fraud-detection、pdf-excel-diff、jpg-ocr-stat。不另外选题。开始前把这份清单和下面的规则写进 PREREG.md。
3. **三组**：no-skills / with-skills（原版 xlsx）/ with-CogniLife-skills（冻结第 11 轮）。除了被替换的 SKILL.md，执行器、模型、输入、附件、工具、预算、轮数上限全部一致。
4. **调度**：保持全串行。先广度优先：每道题三组各跑 1 次，三组轮流运行（no-skills → 原版 → 冻结版）。8 道题全部跑完 1 次后，如果时间还有剩余，再按同样顺序补第 2 次。
5. **shock-analysis-demand**：已有的 no-skills（reward 0）和原版组（runner_limit 中止）记录保留，不重跑；只补跑冻结版组。
6. **轮数上限**：保持现有的 24 轮，不改动。触发上限的运行标注为 runner_limit，不产生评分。触发上限前已用掉的 tokens 不和完成运行的 tokens 做比较。
7. **基础设施失败**：三组都开跑之前因环境无法构建而失败，可以跳过该题，记录原因。跑到一半的基础设施失败（不是 agent 本身的问题）标为 infra_fail。不能根据任何一组的结果来跳题或剔题。
8. **记录**：每次运行记录 strict reward、passed/failed/skipped、total tokens（三组使用同一个计数来源）、工具调用次数、耗时；费用没有回执就记为 unknown。保存原始轨迹、日志和 verifier 输出；不复制第三方测试源码或参考答案到公开位置（沿用现有做法）。
9. **统计**（脚本可重复运行）：
   - 每题每组：通过情况、strict reward、tokens、耗时，逐次列出。
   - 每道题：冻结版相对原版的 strict reward 差值和 tokens 差值百分比。
   - held-out 汇总，必须纳入并标明对应 skill 和版本：energy-market-pricing（economic-dispatch 第 6 轮）、protein-expression-analysis（xlsx 第 11 轮，第 12 轮之前的那次结果），以及本次 8 题。统计正确率持平、提高、下降的题数；tokens 下降、上升的题数。runner_limit 的题同时按两种口径报告：(a) 记为失败，(b) 从该题比较中排除。
   - 开发或选版用过的题（threejs-to-obj、threejs-structure-parser、3d-scan-calc、weighted-gdp-calc，以及第 12 轮之后的 protein）单独成表，不计入 held-out 汇总。
   - 单独列出：小跑时第一个冻结候选在 threejs-structure-parser 上的结果（1/3）和当时的门控判定。
   - 门控在开发题上估计的效率提升，与 held-out 题上实际的 tokens 变化并列比较。

### 第 2 部分：ADV 20 题重新统计（不重跑、不重新打分）

- 从现有 `judge_scores.jsonl` 和 `pairwise_preferences.jsonl` 中只取 ADV 20 题，计算：三个条件各维度和 overall 的均值；Full 相对两个基线的逐题差值（均值、bootstrap 95% CI，10000 次，固定种子；更高/更低/打平题数）；error tag 计数；pairwise 计数，以及 judge 选 A 的比例。
- 记录事实：ADV 的 Full 输出通过平台生成，模型标签为 deepseek-v4-flash；基线生成和 judge 都是 moonshot-v1-128k；其余 65 题的 Full 输出来自一个在 system prompt 中包含题目 checkpoints 的 prompt 代理。

### 第 3 部分：论文修订副本（第 1、2 部分有结果后再做；到 07:30 太平洋时间时，无论第 1 部分进度如何都开始这一部分）

1. 以当前最新的论文 LaTeX 项目为基础，完整复制到一个新文件夹，加后缀 `_rev_20261112`，只在副本上修改。原项目不得改动。不上传 Overleaf 或 OpenReview。
2. **85 题部分**：评测范围改为平台执行的 ADV 20 题。摘要、表格、图、4.1–4.4、结论中的 85 题数字全部换成第 2 部分的结果。用一句话说明其余 65 题的 Full 输出来自一个包含任务要求的 prompt 代理，不代表部署系统，因此不使用。如实写明 Full 与基线的生成模型不同，judge 与基线是同一个模型。
3. **Deployment context**：第 4 节开头已有这一段，不要重复添加。把它的最后一句改为：只有 ADV 20 题的 Full 输出通过已部署的平台生成；Appendix C 的截图来自该部署。
4. **新增 SkillsBench 小节**：正文 4–6 句，附录放完整表格（所有尝试过的题都要列出，包括无效、中止的题）。必须写明：
   - 这是对收到的 Evolution workflow 和门控的外部适配；运行在 Profy 原生 Linux 文件任务 adapter 上，不是官方 Docker 环境；capability-gap classifier、通用语义适用性检查和 native promotion 没有接通；
   - 求解模型和进化模型都是 gpt-6.1-sol（分别通过 Profy 和 OpenRouter 调用）；
   - 每题每组的运行次数如实写出；
   - 结论只根据 held-out 题来写，开发题单独说明。
5. **措辞规则**（根据第 1 部分的结果机械套用）：
   - 只有当 held-out 题中冻结版的 strict reward 有提高、并且没有任何一道下降时，才能写"提高正确率"；
   - 只有当 tokens 下降的 held-out 题明显多于上升的题时，才能写"降低 token 消耗"，并且要注明单次运行、未估计运行间波动；
   - 其他情况一律写成"效果因任务而异"；
   - 无论结果如何，都要报告第一个冻结候选通过门控却在 threejs-structure-parser 上退步（3/3 → 1/3），并和 3.4 节联系：门控放行不代表执行收益，所以 promotion 前需要配对的执行验证；
   - 不得出现"泛化""稳定有效""显著提升"等措辞，除非统计结果直接支持。
6. 引用 SkillsBench 原论文（arXiv 2602.12670），标题和作者从 arXiv 页面获取，不要凭记忆填。
7. Limitations 相应更新：ADV 只有 20 题、生成模型不同、SkillsBench held-out 题数量和运行次数有限、正确率接近天花板、外部适配环境。
8. 正文（Introduction 到 Conclusion）不超过 6 页。超出时先删重复的免责句，再压缩 3.4 节的实现细节；不能删任何实验结果。
9. 编译副本，报告页数。论文中的每个数字都必须能在第 1、2 部分的输出文件中找到出处。把编译好的修订版 PDF 和改动清单推送到 `results/2026-11-12_overnight/paper_rev/`（只放 PDF 和改动清单，不放 LaTeX 源码）。

### 交付物（`results/2026-11-12_overnight/`）

1. MORNING_REPORT.md（中文，一页以内）：完成了多少道 held-out 题、三组结果的一句话结论、按措辞规则论文最终能写什么、偏离预注册的地方、费用和耗时。
2. PREREG.md、DECISIONS.md、PROGRESS.md
3. 所有结果表（CSV 和 Markdown）和统计脚本
4. paper_rev/ 下的修订版 PDF、页数和改动清单（每处改动 → 对应数据出处）

### 本条的硬性规则补充

- 你的任务是如实测量，而不是证明某个版本更好。
- 所有尝试过的题都必须出现在结果表里。
- 不得事后修改选题、协议、统计方法或措辞规则；确有必要偏离时写进 DECISIONS.md，并在 MORNING_REPORT.md 中列出。

---

## I-002（2026-11-12 01:45 美国太平洋时间）延长时间窗口

用户早上醒来后要去上班，下午 16:00（太平洋时间）才能查看。I-001 中的时间安排按下面的修改执行，其余内容不变。

1. **运行截止**：2026-11-12 13:30 太平洋时间（= 2026-11-13 05:30 北京时间）之后，不再启动新的运行。
2. **运行次数**：8 道题第 1 轮（每组 1 次）全部完成后，按同样的顺序和轮流方式补第 2 轮；第 2 轮完成后时间还有剩余，再补第 3 轮。每组每题最多 3 次。这是 I-001 原有"时间允许时补跑"规则的延续，不算偏离。
3. **中期报告**：08:00 太平洋时间时，在 `results/2026-11-12_overnight/` 下写一份 INTERIM_REPORT.md（中文，半页以内）：已完成的运行、初步数字，不下结论。写完之后继续运行。
4. **第 3 部分（论文修订副本）**：13:30 太平洋时间开始，使用截至此时已完成的全部运行结果。
5. **最终交付**：15:30 太平洋时间（= 2026-11-13 07:30 北京时间）之前，完成 MORNING_REPORT.md（可以保留这个文件名）、全部统计表和 paper_rev/ 下的修订版 PDF，并推送。
6. **运行间波动**：同一题同一组有 2 次以上运行时，报告 tokens 的范围和标准差，并标明冻结版与原版的 tokens 差异是否超出原版自身的波动范围。只有 1 次的题标注为"单次，未估计波动"。I-001 中"降低 token 消耗"的措辞规则改为：只有当多数 held-out 题的 tokens 下降、并且下降幅度超出原版自身的运行间波动时才能使用；没有波动估计的题不能计入"明显下降"。

---

## I-003（2026-11-12 02:30 美国太平洋时间）ADV 分数不可用；回复两个 adapter 问题

### A. ADV 20 题：现有 Full 分数不得使用（优先处理，影响第 3 部分）

审核者已核对时间线：ADV 的 Full judge 分数（15:19–15:26）和 pairwise（15:43）都早于当前平台输出的生成时间（17:37–19:01），而晚于 proxy_backup 中代理输出的生成时间（15:03–15:07）。因此现有 Full 分数对应的是注入了 checkpoints 的代理输出，不是平台输出。

1. 现有 judge_scores.jsonl / pairwise_preferences.jsonl 中 profy_expert_full 的任何分数，都不得用于论文中关于 Full 的任何结论（包括 85 题和 ADV 20 题）。第 2 部分的统计保留为审计记录，在报告中如实标注"对应代理输出"。
2. **重新打分 ADV 20 题**（这是 I-001 范围内的必要修正，不是新实验）：
   - 输入：已保存的 Raw、Expert Prompt 输出（moonshot-v1-128k）和当前平台 Full 输出（deepseek-v4-flash），一律不重新生成。
   - Judge：只用 1 个，即此前多 judge 任务中已经配置好的 Claude judge（通过 OpenRouter）；运行前把确切模型 ID 写进 PREREG.md，之后不得更换。
   - Rubric：20 题 × 3 个条件，prompt 与论文 Listing 1 完全一致；解析时只去掉最外层代码围栏。
   - Pairwise：Full vs Expert Prompt、Full vs Raw，各 20 题，正反顺序各一次，prompt 与 Listing 2 一致。
   - 每次调用都保存原始请求和原始返回，并记录被评分输出的 hash，确保分数和输出能一一对应。
   - 正式运行前先估算费用。估算超过 15 美元就不运行，在 STATUS 中说明。只用现有额度，不充值。
   - 这一步走 OpenRouter，与 Profy 上的 SkillsBench 运行互不影响，可以和 SkillsBench 并行，但不得打乱 SkillsBench 的串行顺序。
   - 统计：各条件均值、Full 相对两个基线的逐题差值（bootstrap 95% CI、更高/更低/打平）、正反序 pairwise 计数、位置偏差比例。
3. **第 3 部分（论文修订副本）相应修改**：
   - 如果重新打分完成：4.1–4.4 只报告这次重新打分的 ADV 20 题结果，并如实写明：judge 是新的 Claude judge（不是 moonshot）；Full 用 deepseek-v4-flash、基线用 moonshot-v1-128k，生成模型不同；其余 65 题因 Full 输出来自包含任务要求的代理而不使用。85 题的旧数字（Table 3/4、Figure 2、error tags、pairwise 53/31）全部不出现在正文中。
   - 如果重新打分未完成或被跳过：修订副本中删除 Full 与基线的 LLM-judge 对比结论，保留任务集描述、SkillsBench 和 customs 部分，并在 MORNING_REPORT.md 中写明"LLM-judge 部分待用户决定"。
   - 两种情况都不得把旧的 Full 分数写成平台输出的分数。

### B. 回复 REVIEW_QUESTION_pip_pin_check.md：同意修复

- 同意按你提出的最小修复改 adapter 的 pin 检查：在同一个 task Python 中用 importlib.metadata.version(name) 读取实际生效的版本并记录 location，再和原 pin 比较。不改 pin、不加依赖、不改题、不改 skill、不改 24 轮、不改 verifier。
- 修复对三组一律生效。reserves-at-risk-calc 的三组在 setup 阶段就都失败了，还没有任何评分结果，因此可以在保留旧失败记录的前提下，重新准备并运行这道题的三组。之后其他题如果出现同样的 setup 失败，按同样方式处理。
- 如果修复后实际生效的版本确实不等于原 pin，那就是真实的环境问题：照旧标为 setup 失败，不要为了通过检查去改 pin 或强装版本。
- 写进 DECISIONS.md，作为 adapter 修复记录（注明修复时间、修复前后受影响的运行）。

### C. 回复 REVIEW_QUESTION_tool_search.md：有条件同意补评分

- 同意把原生 tool_search 作为纯发现调用加入 adapter 预评分检查的白名单，对三组一律生效，前提是该次运行的轨迹中没有读取、激活或加载任何 skill 文件。如果轨迹显示 tool_search 之后读取或激活了 skill，这次运行仍判为协议违规，不评分。
- 对符合条件的现有轨迹，不重新求解、不修改回答，直接补跑原 verifier，记录原始 reward。
- shock-analysis-supply 三组如果都属于同类情况，都按此规则处理。由于 solver 自述原题的 Excel-only / Playwright MCP 约束与 adapter 环境不符，这道题在汇总中单独标注为"环境受限"，held-out 汇总同时报告包含和不包含它的两种结果。
- 写进 DECISIONS.md。

### D. 其他

- 此前 threejs 历史反例的进化模型是 gpt-4.1，论文修订副本中要单独说明。
- shock-analysis-demand 的结果（冻结版 0/5，no-skills 3/2，原版 runner_limit）照实列入，不另作解读。

---

## I-004（2026-11-12 03:40 美国太平洋时间）ADV rubric 截断修复；Profy 403 处理；状态推送

### A. ADV rubric：统一提高 max_tokens 后全部重跑

- 第一批 rubric 中，profy_expert_full 有 8 题因 "length-limited judgment" 缺失，而且缺失只出现在 Full 组。缺失和条件相关，不能直接用 52/60 的结果。
- 处理：把 rubric 调用的 max_tokens 从 1024 统一改为 4096，prompt（Listing 1）、模型（anthropic/claude-opus-5.5）、解析规则都不变，对 20 题 × 3 个条件共 60 次 rubric **全部重跑**。论文和统计**只使用这次重跑的 60 个结果**，第一批 rubric 保留为审计记录，不和新结果混用。
- Pairwise 第一批 80/80 全部有效，不重跑，照常使用。
- 预算：I-003 和本条合计的**实际费用**（按 OpenRouter 回执）不超过 15 美元。第一批实际已花 3.529044 美元。运行前先按回执单价估算这批的费用；估算会让合计超过 15 美元就不运行。如果有调用在 4096 下仍然截断，最多重试 2 次；仍然失败就记为缺失，并按条件报告缺失数。
- 写进 DECISIONS.md：偏离点（max_tokens 1024 → 4096）、原因（Full 组系统性截断）、决定时间（在看到缺失题的分数之前）。

### B. Profy 403 "Expert is not published"

- 你的处理是正确的：不发布专家、不换 key 或模型、不创建替代身份。
- 从现在起每 30 分钟探测一次：只提交原计划顺序中的下一次运行（一次）。如果仍然返回 403，记录下来，不计为运行；如果成功，就恢复原计划（I-001/I-002/I-003），不做其他改动。
- 用户在上班，可能会在白天重新发布专家。恢复之后，继续按原顺序补跑；之前因 pin 检查失败的题（reserves-at-risk-calc、xlsx-recover-data），按 I-003 B 修复后的检查重新准备。
- 运行截止仍为 13:30 太平洋时间。

### C. 第 3 部分（论文修订副本）提前开始的条件

- 如果到 12:00 太平洋时间 Profy 仍然是 403，就在 12:00 开始第 3 部分，不必等到 13:30。之后如果 Profy 恢复并产生了新结果，在 15:30 交付前把新结果补进统计表和修订稿。
- ADV 部分用 A 中重跑的 rubric 结果，加上第一批的正反序 pairwise 结果。必须写明：judge 是 anthropic/claude-opus-5.5；Full 是 deepseek-v4-flash、基线是 moonshot-v1-128k，生成模型不同；pairwise 沿用原函数，每份输出只截取前 3000 字符；pairwise 正反序都判 Full 赢的计数。不得使用任何旧的 Full 分数。

### D. 状态推送

- 实验分支 origin/codex/three-arm-skill-pilot-20261110 上的 docs/coordination/STATUS.md 从 02:18 之后就没有更新。请按 PROTOCOL 每 30 分钟把 STATUS.md、STATUS_LOG.md 推送到这个分支。如果推送失败，把失败原因写进本地 STATUS.md，下一个节点重试。

---

## I-005（2026-11-12 05:10 美国太平洋时间）更正与澄清

### A. 更正 I-004 D
状态推送一直正常（远端已有 04:58 的提交）。审核者此前读到 02:18 的旧状态，是因为自己浅克隆拉取时没有强制更新跟踪分支，不是你的问题。I-004 D 无需执行任何操作。

### B. 澄清 I-003 C 中 tool_search 的条件（适用于 shock-analysis-supply 的 B/C 组及之后所有同类情况）
I-003 C 的本意是：tool_search 不能让一个组接触到**分配给它的 skill 集合以外**的 skill。各组被分配的集合是：
- no-skills：空集；
- with-skills：原版 xlsx skill；
- with-CogniLife-skills：冻结第 11 轮 xlsx skill。

因此：
- with-skills 和 with-CogniLife-skills 组读取或激活**自己被分配的** SKILL.md，无论发生在 tool_search 之前还是之后，都不算违规。
- 只有当轨迹显示某组读取、激活或加载了分配集合以外的 skill 文件时，这次运行才判为协议违规、不评分。
- 符合条件的 B/C 组现有轨迹，按 I-003 C 的同样方式补跑原 verifier：不重新求解、不改回答、记录原始 reward，并在 DECISIONS.md 中记录本次澄清。shock-analysis-supply 仍标为"环境受限"，并按两种口径汇总。

### C. 其他
- Profy 403 的探测按 I-004 B 继续进行。
- ADV 部分在修订副本中使用 ADV_CURRENT_RESULTS.md 中的 I-004 结果，并保留其中列出的边界：missing_info 子集上 Full 和 Expert Prompt 持平；Full 的 coherence 和 safety 低于 Expert Prompt；生成模型不同；pairwise 每份输出只截取前 3000 字符。原稿中"missing-information 差距最大""各维度均更好"的说法必须删除或改写。

---

## I-006（2026-11-12 08:20 美国太平洋时间）提前开始论文修订副本，先交初稿

Profy 从 02:30 起一直返回 403，现有数据基本定型。为了给审核留出时间，调整第 3 部分的时间安排（其余规则不变）：

1. **现在就开始第 3 部分**，不必等到 12:00。Profy 探测照常每 30 分钟一次；恢复后照常补跑，运行截止仍为 13:30。
2. **11:00 太平洋时间前**推送一份初稿：把 PDF 和改动清单放到 `results/2026-11-12_overnight/paper_rev/draft1/`，并在 STATUS.md 中注明。审核者会在 11:15 审阅，必要时用新编号指令给出修改意见。
3. 初稿以当前已有结果为准：ADV 部分用 ADV_CURRENT_RESULTS.md（I-004）；SkillsBench 部分用截至此时的全部尝试记录。如果之后 Profy 恢复并产生新结果，在 15:30 最终版中更新数字和统计表，并在改动清单中标出变化。
4. 15:30 的最终交付物放在 `results/2026-11-12_overnight/paper_rev/final/`，要求和 I-001 第 3 部分一致。

---

## I-007（2026-11-12 09:20 美国太平洋时间）用户决定：停止 Profy，按现有数据定稿

用户在 09:15 明确表示：专家不可用就算了，不再等待。

1. **立即停止 Profy 探测**，不再提交任何 Profy 请求。记录最后一次探测时间。
2. **SkillsBench 部分按现有数据定稿**：
   - 未开跑的题（invoice-fraud-detection、pdf-excel-diff、jpg-ocr-stat）和始终没有得到有效评分的题（reserves-at-risk-calc、xlsx-recover-data），在附录表中如实列出，状态写为"平台不可用，未完成"，不计入汇总。
   - shock-analysis-supply 的 B/C 组记为"未评分（平台不可用）"。这道题只有 no-skills 一组有分，无法做组间比较，不计入组间汇总，但在附录中列出。
   - 用于组间比较的 held-out 题：energy-market-pricing、protein-expression-analysis（第 12 轮之前的那次）、powerlifting-coef-calc；shock-analysis-demand 按 I-001 的两种口径处理。在正文和附录中写明每题每组只有 1 次运行。
   - 统计和措辞规则不变（当前允许的措辞是"效果因任务而异"）。
3. 论文修订继续按 I-006 执行：11:00 交初稿，15:30 交最终版。最终版中，凡是提到"Profy 恢复后补跑"的说法一律删除。
4. 在 DECISIONS.md 中记录：停止原因是用户决定，不是根据任何结果做的选择。

---

## I-008（2026-11-12 09:30 美国太平洋时间）用户确定的修订原则

用户在 09:20 给出了论文修订原则。下面的规定优先于 I-001 第 3 部分中与之冲突的写法，但**不覆盖**硬性规则和 I-001/I-002 的措辞规则。

### 1. 少删：能用的内容不改
- 保留原稿的结构，以及所有仍然成立的内容：引言、相关工作、第 3 节框架和三个控制点、Deployment context、customs 案例、所有图、附录截图、prompt listing 等。只做必要的修改，不重写本来能用的段落。

### 2. 突出最好的数据
- ADV 20 题的重新打分结果（ADV_CURRENT_RESULTS.md，I-004）作为第 4 节的主结果：一张紧凑的表，加 2–3 句话。
- 在摘要和引言的贡献部分点出这个结果，例如："在 20 道通过部署平台执行的任务上，部署的专家配置在正反序 pairwise 中有 16/20 题两次都胜过 Expert Prompt"。同一句或紧接的下一句必须注明生成模型不同。
- customs 案例保持原样。

### 3. 经验教训
在 Discussion 中新增一小段 "Lessons from deployment"，写 3–4 条，每条 1–2 句，语气客观，作为部署中得到的工程经验，不写成检讨：
- a. 门控放行不代表执行收益：threejs 反例（3/3 → 1/3）；SkillsBench held-out 题正确率持平、tokens 变化因任务而异。所以 promotion 之前需要做执行验证。
- b. 评测泄漏：早期的 prompt 代理在生成时就看到了评分用的 checkpoints，rubric（尤其是 completeness）因此被抬高；在看不到 checkpoints 的 pairwise 中，优势明显变小。所以生成端不能接触任何评分材料。
- c. 分数和输出必须用 hash 绑定：审计发现，部分分数对应的是之后被替换掉的输出。
- d. Judge 的输出截断会造成和条件相关的缺失（较长的 Full 输出更容易被截断），所以要统一放宽输出上限，并全部重跑。

### 4. 不能用的旧内容：保留，但降低比重
- 85 题任务集的描述（family、variant、checkpoints、构建方式、judge 协议）继续保留在 4.1，不删。
- 旧的 85 题结果（原 Table 3/4、Figure 2、error tags、pairwise 53/31）**不删除，数字一个都不改**，原样移到附录的一个新小节。小节标题和说明必须如实写明：这是早期一个"在 system prompt 中包含题目 checkpoints 的 prompt 代理"配置的结果，由 moonshot-v1-128k 打分，不代表部署系统，只作为经验教训 b 的证据。正文只在经验教训 b 中用一句话引用它。
- 任何地方都不能把这些旧数字称为 Full 或部署系统的结果。

### 5. 新内容
- SkillsBench 小节（按 I-001 和 I-007 的规定写）；ADV 20 题主表。

### 6. 版面
- 正文不超过 6 页。为新内容腾地方时，按这个顺序压缩：旧结果移到附录后空出来的篇幅 → 重复的免责句 → 3.4 节的实现细节。不删框架和 customs 案例。

### 7. 交付
- 如果 draft1 是在读到本条之前生成的，就按本条在 12:30 太平洋时间前推送一份 draft2，放到 `results/2026-11-12_overnight/paper_rev/draft2/`，并附改动清单。改动清单中要单独列出"删除的内容"，每一处都要说明理由。
- 最终版仍在 15:30 前交付到 paper_rev/final/。

---

## I-009（2026-11-12 09:25 美国太平洋时间）正文图的替换

用户要求：正文中的图如果被移走或删除，要换成一张用干净结果做的新图。

1. 原 Figure 2 按 I-008 原样移到附录。正文空出的位置换成一张新图，数据只取自 I-004 的 ADV 20 题结果（adv_i004_analysis/ 和 ADV_CURRENT_RESULTS.md）。
2. 新图的推荐方案：**正反序 pairwise 结果的水平堆叠条形图**，两行，分别是 Full vs Expert Prompt 和 Full vs Raw。每行包含三段：两次都判 Full 赢、两次结果不一致、两次都判基线赢（16/1/3、17/1/2），每段标注题数。三类必须全部画出来，不能省略任何一类。
3. 如果还有空间，可以在同一张图里加第二个面板：Full − Expert Prompt 在 5 个维度上的逐题差值均值和 bootstrap 95% CI。**必须把 5 个维度都画出来**，包括 Full 更低的 coherence 和 safety，不能只挑有利的维度。空间不够就只放第一个面板，第二个面板放到附录。
4. 图注写明：n=20 道 ADV 任务；judge 是 anthropic/claude-opus-5.5；Full 是 deepseek-v4-flash，基线是 moonshot-v1-128k；pairwise 每份输出截取前 3000 字符。
5. 风格和全文其他图保持一致（字体、字号、色盲友好配色），宽度控制在单栏内。用脚本从结果文件直接生成，脚本和数据出处写进改动清单。
6. 正文仍不超过 6 页。
