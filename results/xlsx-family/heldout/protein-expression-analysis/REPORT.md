# 第一题: 没见过的蛋白表达 Excel 题

这道原题要求把 Excel 的原始数据查到目标表格中, 再计算两组的均值、标准差和变化倍数. 不改题、不改附件、不改验收程序.

[SkillsBench 原题](https://github.com/benchflow-ai/skillsbench/blob/f860ecf02ef53412a030f8661c83d644b739ff01/tasks/protein-expression-analysis/task.md)

## 实际结果

| 组别 | 原评分 | Solver total_tokens | 准备环境加解题的秒数 |
| --- | --- | ---: | ---: |
| no-skills | 6/6, reward1.0 | 183191 | 282.754 |
| with-skills, 原版 xlsx | 6/6, reward1.0 | 187869 | 309.261 |
| with-CogniLife-skills, 冻结第11轮 | 6/6, reward1.0 | 264808 | 336.866 |

第11轮在这道新题上没有带来质量提升, 用的 tokens 比原版多40.95%. 开发题上的节省没有在这一题上延续. 这是一题的结果, 不能代替后续题目的结果. 不根据这道题的答案或原评分内容改 skill.

Solver total_tokens 是 API 返回的求解 token 用量, 不是费用. 秒数包含环境准备和解题, 不包含附件上传、评分及结果回传. Profy 没有返回美元费用, 不估算费用.

## 这三组用了什么

- 同一个 Profy expert identifier, 同一 model label gpt-6.1-sol; 每组新 session 和独立端用户标识.
- Memory 关闭, 不请求其他 expert; 每次只跑一组.
- 原版 SKILL.md SHA256: 9bdc1fee81f3be9cb34ac49f8890c094a3855d3d0236783d10e0ea6df1515e01.
- 第11轮 SKILL.md SHA256: 51ca8a2ff044812e60ca830e9951d17219a66c736004edc99729d157f275cf1a.
- 原版和进化版都确认实际读到了对应的完整 SKILL.md. 三组原始 Excel 的 SHA256 相同: 95d5d1d9ed1920b2e22143866ca932c88aa14eafe7dd0ad998594868961faf21.
- 第11轮只用 weighted-gdp-calc 开发记录进化, 在这道蛋白题开始前冻结. Evolution 使用 OpenRouter openai/gpt-6.1-sol.
- 收到的原始 Evolution 组件及缺失的 classifier、semantic applicability check、native promotion 仍按[当前状态](../../../../docs/STATUS.md)披露. 本实验不能当作完整平台复现.

## 运行环境与记录修复

实际执行在 Profy Debian Linux, 使用原题声明的软件的原生安装版本. 不是官方 Ubuntu Docker image. 三组实际版本、依赖和输入指纹放在各组原始 score_receipt.json; 不把这组数字当作官方 leaderboard 数字.

A 组的环境说明被工具输出长度截断, 后来只补取完整记录, 没有重新解题. 原评分日志显示6 passed和reward1.0. 原脚本安装了 CTRF 插件, 但没有要求输出 CTRF 文件; adapter 最初错误地要求必须有该文件. 原回执照存, 另存 ORIGINAL_SCORE_ANALYSIS.json 说明如何从原日志读出6/6. 没有重打分或改原答案. A 的评分前 source hashes 和只读 verifier 挂载有记录; 因 adapter 提前退出, 没有评分后的二次 source hash 检查, 不补写为已检查.

A 的环境说明仍是修复前格式. 因此不能把 A 和其他组的 tokens 差异全部算作 skill 的影响. B/C 使用相同的修复后格式, 原评分前后源码指纹和答案不变均通过检查.

每组的 protein_expression.xlsx 是实际交回的 Excel, 不重新生成. events.jsonl.gz 是逐步运行记录的压缩版, 解压后可查看. result.json 是数字和配置摘要; original-grader/score_receipt.json 与 original_verifier_stdout.log 保留原评分证据. 原题、hidden tests 和 gold 没有用于 skill 进化.
