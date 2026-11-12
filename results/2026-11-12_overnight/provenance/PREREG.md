# 夜间预注册, 新运行开始前冻结

开始: 2026-11-12 09:25:03 UTC. 15:55:03 UTC 后不启动新 solver/grader 调用; 16:25:03 UTC 前完成报告. 无金额上限, 仅使用已有 API key, 不充值、不购买服务. Profy 未回传美元费用时记 unknown, 不用 tokens 推算. 每完成一个 task 更新 PROGRESS.md, 费用状态至少每2小时追加一次.

## 冻结和适用范围
唯一候选是 xlsx 第11轮采用版, SHA256 51ca8a2ff044812e60ca830e9951d17219a66c736004edc99729d157f275cf1a. 原版 SKILL.md SHA256 9bdc1fee81f3be9cb34ac49f8890c094a3855d3d0236783d10e0ea6df1515e01. 保留每题其他所有公开 skill 和资源, 只替换 xlsx/SKILL.md. 不进化、不改门控、不把新题执行/答案用于改skill. SkillsBench pin f860ecf02ef53412a030f8661c83d644b739ff01. 逐题静态筛选表见 SELECTION_PREFLIGHT.json.

第一批顺序: shock-analysis-demand, shock-analysis-supply, reserves-at-risk-calc, powerlifting-coef-calc, xlsx-recover-data, invoice-fraud-detection, pdf-excel-diff, jpg-ocr-stat. 第一题已有部分运行, 保留重测但不混入严格首次新题汇总. 第二批按task字母顺序, 排除 multimodal 标签; 不存在同源 xlsx 原版 skill 就不适用. 已知只有 exceltable-in-ppt 额外符合SKILL.md hash, 但配套资源有差异, 原样保留并披露. 所有开发/选版题、grid-dispatch-operator、energy-market-pricing排除新增测试. protein 第一次冻结评测保留, 后续参与选版后不再是独立新题. 在新运行前还会核对已有记录是否存在其他开发/选版任务; 排除只根据历史使用情况, 不根据成绩.

## 相同运行协议
全部串行. 每题3次重复, 每次按 no-skills -> with-skills -> with-CogniLife-skills, 共9次. Profy model label gpt-6.1-sol, 新session和end-user标识, enable_memory=false. 复用现有 native-owned 文件执行和原 verifier 适配; 非官方 Ubuntu image. 三组相同题目/附件/工具/软件版本/48次工具调用/24次模型用量事件上限/1600秒solver墙钟上限. grader为1200秒客户端上限和900秒原测试子进程上限. 上限不因成绩改变. 触发solver上限且无评分, strict reward按用户要求记0, runner_limit=true, 通过测试数记unknown. 非agent基础设施失败记unknown; 任一组至少2/3基础设施失败, 整题无效, 排除汇总但完整列出. 临近时间截止不启动预计无法在截止前安全完成的新题; 已尝试的未完成题记 incomplete, 不算完整三次均值. 不用旧运行填充新重复.

原任务要求编辑附件时, 仅编辑新session中复制的附件, 原始输入和已有历史不动. 原 grader 的云端临时目录清理只限本次新建session和scratch; 不删除或覆盖任何任务开始前已有的本地/云端文件. 适配异常不改skill和评分. 不根据组别/得分跳过已开跑的task, 所有attempt留档. 只有三组开始前已明确环境无法构建才环境跳过; 开跑后的基础设施错误按失效规则处理. 新folder每次attempt唯一, 不覆盖.

## 统计
每组strict通过率=reward为1的次数/3; reward均值; 总tokens逐次值、均值、样本标准差(ddof=1), 工具次数、solver准备加解题耗时(不含评分/上传), 端到端耗时另列. tokens全部来自solver usage.token total_tokens求和, 不混入grader/Evolution. 无回执费用unknown. 原verifier reward和passed/failed/skipped原样保留, 另记stdout计数冲突.

每题冻结版减原版strict reward均值; tokens百分比=(冻结均值/原版均值-1)*100. 波动比较用tokens绝对均值差和原版3次样本SD, 绝对差>SD才列明显下降/上升, 否则波动范围内. 这是描述性门槛, 非显著性检验. 不足3次或失效不作完整比较. 新题至少5道, 按题重抽样10000次、seed20261112, 对各题tokens百分比变化均值给percentile95%CI. 不把3次重复当独立task. strict差以0作持平. 质量提高措辞仅当至少1题提高且0题下降. 降低token措辞需明显下降题比明显上升题至少多2道且下降题逐题超过原版SD; 否则写效果因任务而异. 既有门控预测从第11轮原pending提取, 无数值就unknown; 与开发表现、此次新题表现分列.

## ADV
只读既有judge_scores.jsonl和pairwise_preferences.jsonl中的ADV_001至ADV_020. 不调用judge、不重跑生成. 各维度/overall均值, Full减两基线的逐题差, 10000次bootstrap seed20261112, 胜负平, error tags, pairwise胜负平和选A比例(含tie/不含tie都列). 不把保存的模型标签当独立认证. 来源hash和缺失字段完整记录.

## 论文
完整复制原LaTeX到新folder, 不修改原Overleaf或OpenReview. 新副本85题部分改为ADV20, 披露生成模型不同及65个proxy输出排除. SkillsBench按新题结果如实写; 所有尝试/失效/不适用入附录. 历史首候选门控通过而threejs退步需查原记录后引用. 所有新数字从脚本results生成. 部署事实只写能核实者, 无公共来源的生产起始日期不伪称公开核实. 正文最多6页, 成功编译后检查. 未完成部分照实交付.
