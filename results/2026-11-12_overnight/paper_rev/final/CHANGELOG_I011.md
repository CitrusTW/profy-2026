# 最新最终稿: I011整合版

此版取代此前的文字修订版。原版本保留, 没有覆盖。正文6页, 全文27页。

## 当前授权范围

用户I011及补充明确取代此前同模型结果不入稿的暂停要求, 同模型结果现已写入摘要、引言、正文主表与附录。用户再次明确允许写入Overleaf, 仅上传新项目副本, 原项目不改, 不上传OpenReview。

## 修改前 → 修改后

1. 摘要和引言定位: 以跨模型Full赢16/20作为主结果 → 框架设计、已实现控制点和部署经验, 如实说明同模型下未保留overall优势。负向结果不置于摘要第一句。
2. 4.1 Full定义: 确定含metadata/workflow/profile/journal的context-rich配置 → API调用已部署专家, 平台组装配置上下文, 实际注入内容未记录。保留先前文字审核修正。新增同模型基线的prompt来源、0.7/4096参数和版本无法核实的边界。
3. 主表: 只报告跨模型3个条件 → 同时报告I004和I010各3个条件的overall、Full−ExpertPrompt差值及CI。Full答案不重生成, 两个批次独立评分。
4. 4.3: 跨模型overclaiming15vs2、hallucinated_evidence11vs0 → 改为同模型描述性维度和tag比较, 顺序明确为Full vs ExpertPrompt/Raw。原跨模型tag数字完整保留在附录, 不再作为正文描述。
5. 同模型Full safety_boundary3.10vs2.95/2.95, evidence_grounding2.40vs2.20/2.35; overclaiming14vs18/17, hallucinated_evidence13vs17/14。Completeness与actionability均值较低。所有5个一般维度、2个诊断维度和所有返回tag完整列在附录, 不挑有利项目。以上全部来自i010/analysis/I010_RESULTS.json。
6. Pairwise主图: 跨模型16/1/3和17/1/2 → 同模型9/3/7/1和8/2/10/0, 四段分别为Full两次赢、顺序翻转、基线两次赢、缺失。附录同时展示两批次完整计数、A选择比例、一致率; 缺失未填值。
7. Lessons: 原4条 → 加入Full有8/20条回答被judge标为tool_failure, 部署评测应单独记录工具失败。没有将judge标签当成独立确认的真实工具故障计数。
8. 附录H.2: 保留上一轮修正, 明确Proxy system prompt要求先追问缺失信息, 不将旧missing-input0标签解释成独立能力。旧85题所有数字、图均不变。
9. 附录G: 保留上一轮的普通英文句子, 4套计数口径和数字不变。
10. Limitations: 只提示生成模型不同 → 区分跨模型和声明模型匹配, 保留无法核实平台版本、上下文和生成配置、模板来源不确定、单处pairwise缺失、有限样本等边界。
11. 版面: 缩短新增文字和原4.1的重复说明, 每个family的evaluation focus移到附录, 不删除该内容。较宽完整统计表置于双栏宽附录。第3节框架、Customs段落和customs_appendix.tex逐字不变。

## 数字出处

- I010: i010/analysis/I010_RESULTS.json及condition_means.csv, 原始call记录均保留。
- I004: adv_i004_analysis_v2/results.json, 原数据不改。
- 每个新数值字段的来源hash和JSON路径: NUMERIC_SOURCES_I011.json。
- 原始文字审核逐项修改前→后: 同目录CHANGELOG.md, 其中关于同模型不入稿和正文跨模型tag说明已被本I011清单明确取代。

## 验证

正文6页, 总27页; 无overfull box, 无未定义引用, 图片和表格已视觉核对。所有新结果来自既有结果文件, 没有新增付费调用。原项目未改。
