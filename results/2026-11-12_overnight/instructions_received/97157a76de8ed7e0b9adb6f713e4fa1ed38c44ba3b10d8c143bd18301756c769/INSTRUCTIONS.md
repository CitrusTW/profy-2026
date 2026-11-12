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
