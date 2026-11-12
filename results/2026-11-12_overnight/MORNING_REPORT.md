# 最终报告

- 最新论文: paper_rev/final/CogniLife_final_I011.pdf, 正文6页, 全文27页。用户I011已取代之前的同模型结果暂停入稿要求。原项目未改, 没有上传OpenReview。
- SkillsBench: 本轮8道计划题中, 新完成powerlifting-coef-calc三组各1次; 加上先前energy-market-pricing和pre-round12 protein-expression-analysis, 共3道可比较held-out题。三组strict reward均持平, token变化因题而异。shock-demand保留runner_limit两种口径; supply只有no-skills评分, 其他未完成题逐项保留。停止Profy由用户决定, 不是根据结果筛题。不能声称提高正确率或降低token消耗。
- ADV跨模型I004: Raw2.43 / ExpertPrompt2.63 / Full3.22, Full−EP=0.59,95%CI[0.30,0.87]; both-order Full赢16/20。旧85题结果明确作为checkpoint-conditioned Proxy归档, 不再当部署Full。
- ADV同模型I010: Raw3.31 / ExpertPrompt3.42 / Full3.23, Full−EP=-0.19,95%CI[-0.55,0.16]。Rubric60/60有效, pairwise79/80有效; EP对比9Full赢/7基线赢/3翻转/1缺失。未保留overall优势, 论文如实报告。5个一般维度、2个诊断维度、所有错误标签完整入附录; Full有8/20个tool_failure标签。
- 异常/偏离: 按编号指令修正adapter版本检查、工具发现范围; ADV旧分数与输出版本不对应而重评; judge统一增大rubric预算后全条件重评。I010一处pairwise顺序重试两次仍截断, 保留缺失; 一份Raw生成触及4096上限, 保留不重生成。历史平台Full的实际注入上下文和服务版本未知。
- 费用: I003/I004 OpenRouter回执USD4.941796, I010 USD4.0799450879, 合计已知USD9.0217410879; Profy费用unknown。没有充值或额外购买服务。累计工作跨度9.48小时, 含等待平台和文稿修改; I010实际运行38.56分钟。
- 证据: PREREG.md、i010/PREREG_I010.md、DECISIONS.md、PROGRESS.md; skills_final/、adv_i004_analysis_v2/、i010/analysis/。原始JSONL、失败记录、hash和脚本均保留。最终改动与数值来源见CHANGELOG_I011.md和NUMERIC_SOURCES_I011.json。
- Overleaf: 用户已明确授权上传新项目副本, 当前Chrome扩展未允许本地文件URL访问, ZIP自动上传失败; 最终源ZIP已单独编译验证6/27页, 待解决上传权限。没有更改原Overleaf项目。
