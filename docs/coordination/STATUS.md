# STATUS: latest I011 final

- 更新时间: 2026-11-12T10:53:46.046933-08:00
- 最新指令: 用户I011附加 + 用户明确允许写入Overleaf。它们覆盖此前同模型结果暂停入稿要求和旧Overleaf禁写规则。
- 最新论文已完成: results/2026-11-12_overnight/paper_rev/final/CogniLife_final_I011.pdf
- 正文6页, 全文27页, 编译通过。无overfull box或未定义引用, 新结果163条数值来源核对, 所有5个一般维度/2个诊断维度/返回tags完整保留。
- I010同模型结果已经按用户最新要求写入论文, 结论为未保留overall优势。早先同目录CogniLife_final.pdf是未整合版, 已被I011新版取代, 作为历史记录保留。
- 定位: 框架设计+已实现控制点+部署评测经验教训。Full上下文注入未知; API调用事实明确。正文使用同模型维度/tag, 跨模型完整保留附录; 增加8/20tool_failure记录教训。
- 原第3节、customs正文和附录、review-corrected Proxy85归档未改变。没有新付费运行。
- 改动清单: paper_rev/final/CHANGELOG_I011.md; 所有数值来源: paper_rev/final/NUMERIC_SOURCES_I011.json。
- 本地源项目: /Users/mac/Desktop/naacl 2026.10 - CogniLife/01_任务结果/2026-11-12_night_validation_092503/cognilife_rev_20261112_i011_final; 源ZIP已单独编译,6/27页,逐页文本一致。

## 实验结果

- I004跨模型:2.43/2.63/3.22, Full−EP0.59,CI[0.30,0.87]。
- I010同模型:3.31/3.42/3.23, Full−EP-0.19,CI[-0.55,0.16]。60rubrics/79pairs, 单处order缺失保留。EPpairwise9Full/7base/3flip/1missing。
- SkillsBench:3道matchedheld-out,单次/组,strict持平、tokens因题而异,所有不完整/限轮情况完整保留。
- 费用: OpenRouterI003/I004=USD4.941796;I010=USD4.0799450879;Profyunknown。

## Overleaf / OpenReview

- 旧自动审批限制已因用户再次明确授权而解除; 新项目导入UI已打开。
- 当前真正阻塞是Chrome文件上传能力: 扩展未开启Allow access to file URLs。自动chooser失败; 未悄悄扩大扩展权限, 未上传文件。
- 等待允许必要的扩展文件访问或用户手动导入已验证ZIP。只上传新项目副本, 不改原项目。
- OpenReview从未上传。

## 记录

MORNING_REPORT.md、DECISIONS.md、PROGRESS.md、STATUS_LOG.md和各结果目录保存完整历史, 不根据结果删题或改分。
