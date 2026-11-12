# 论文修订副本 draft2

此版取代 draft1。编译通过, 正文 6 页, 全文 25 页。原论文、Overleaf、OpenReview 均未修改。

## 改了什么

- 摘要和引言贡献: 加入 ADV 20 题中 Full 在正反顺序下均胜过 Expert Prompt 的 16/20 题结果, 紧接说明生成模型不同。数据: adv_i004_analysis_v2/results.json → pairwise.generic_llm_expert_prompt.counts.both_full_wins。
- 4.1 保留 85 题的构建、family、variant、checkpoints 描述。当前部署对比仅使用已保存的平台 ADV 20 题输出, 不重新生成答案。Judge 为 anthropic/claude-opus-5.5; Full 为 deepseek-v4-flash; 两个基线为 moonshot-v1-128k。
- 4.2–4.4 和附录 A: 改为输出 hash 对应的新评分。Overall 为 Raw 2.43 / Expert Prompt 2.63 / Full 3.22; Full − Expert Prompt 为 0.59, bootstrap 95% CI [0.30,0.87]。完整维度、负向结果、error tags 和正反序结果均保留。出处: adv_i004_analysis_v2/results.json; adv_i004_context_analysis/results.json。
- Figure 2: 新增两行堆叠图, 完整显示 16/1/3 和 17/1/2; 附录 A 展示全部 5 个维度及 CI, 包括 coherence 和 safety 的负差值。脚本 gen_adv_figures_v2.py 直接读取 results.json, 数据记录 paper_figures/draft2/PLOT_DATA.json。
- 4.6 和附录 G: 加入冻结 skill 的外部适配结果。可做组间比较的 3 道 held-out 题每组各 1 次, strict reward 均持平, token 变化因题而异。列全 8 道计划题的完成/未完成状态、shock-demand 两种口径和开发题。没有声称提高正确率或降低 token 消耗。出处: skills_final/results.json、history_results.json、selection_records.json。
- Discussion: 加入 promotion 前执行核验、生成与评分隔离、分数与输出 hash 绑定、统一 judge 输出预算这四条经验。避免把观察到的差异写成已证明的因果关系。
- 附录 H: 保留旧 85 题的全部结果数字和图, 条件名改为 Proxy, 明确是 generation 时包含 checkpoints 的早期 prompt proxy, 由 moonshot-v1-128k 评分, 不代表部署系统。旧数字未修改。出处与逐项数字保留检查见 CHANGELOG_NUMERIC_SOURCES.json → old85_proxy_archive。
- 保留第 3 节框架、三个控制点、Customs 案例及数字、所有其他图/截图和 prompt listings。Deployment context 保留, 末句明确仅 ADV 20 题的 Full 输出来自部署平台。
- 截图顶部 Expert Distillation Studio 已用白色遮挡, 未裁掉正文内容。PDF 作者 metadata 为空, 文本未发现产品名、公司名或 private repo 标识。

## 删除的内容及原因

- 仅修订副本移除作者/单位/equal-contribution 标记: 用于匿名评审; 原项目保留。
- 移除列举商业产品并带链接的脚注: 满足匿名稿不出现产品名和可识别链接的要求。
- 正文旧 85 题结果不再作为 Full 的结论: 分数对应早期 proxy 输出; 所有数字和原结果段落移入附录 H, 并未丢弃。
- 替换旧结论中将 proxy 分数归于部署 Full 的说法: 按分数-输出来源核对结果修正归属。
- 附录旧条件名 Full 改为 Proxy: 避免和 ADV 平台输出混淆; 图、表、正文数字均保留。
- 删除原先解释 rubric 与 pairwise 差异的正文段落: 新的正反序结果和具体部署经验替代; 历史内容保留在附录 H。

## 核对

395 条新结果数字来源记录逐项核对成功; 原框架与 customs_appendix.tex 未变。旧 85 题科学数值序列保持不变。正文 6 页, 全文 25 页, 无 overfull box、未定义引用。完整改动到数值字段的对应关系见 CHANGELOG_NUMERIC_SOURCES.json。

停止实验是用户决定; 已停止所有 Profy 请求, 不等待恢复。API 不可用导致的缺失不填 0。没有上传 Overleaf 或 OpenReview。
