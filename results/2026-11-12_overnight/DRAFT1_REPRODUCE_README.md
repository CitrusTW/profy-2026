# 初稿的数字怎么核对

先看paper_rev/draft1/CHANGELOG.md, 再看对应CSV. skills_draft1/results.json是当前全部SkillsBench统计; adv_i004_analysis_v2/results.json是新ADV评分, adv/只保留旧分数审计, 不能混用.

strict=1表示原verifier严格通过; strict=0表示没有全部通过. unknown表示没有评分或没有可用测量. runner_limit没有原始评分, 只有口径(a)把它当失败0; 口径(b)整题排除. 一次运行的SD是unknown, 不能填0. API403是请求被拒绝, 不是做题答错.

需要Python和NumPy, 不需要key, 不调用模型. 从results/2026-11-12_overnight运行:

```sh
python scripts/recompute_skills_portable.py --data-root repro_skills_draft1 --out /tmp/skills-recomputed-new
python scripts/analyze_adv_judge_v2.py --rubric-file adv_rejudge_i004_rubric4096/VALID_JUDGMENTS.jsonl --pairwise-file adv_rejudge_i003/VALID_JUDGMENTS.jsonl --out /tmp/adv-recomputed-new
```

输出目录必须不存在, 以免覆盖. repro_skills_draft1/SELF_CHECK.json确认重算和初稿统计逐项相同. JSON null表示unknown; 人读CSV/表格使用unknown. 没有费用回执的Profy成本保留unknown, 不从tokens编价格.

原始solver轨迹、请求、评分回执和hash在skillsbench/和profy_i004_probes/. 完整verifier本机日志留在原运行目录, 因为其中可能展开第三方测试源码; Git不复制这些代码. 所有judge原始请求/返回和解析记录在两个adv_rejudge目录, 包括失败的调用.
