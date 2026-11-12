# 不调用API的结果重算

需要Python和NumPy, 不需要key. 保存的原始attempt与生效trial分开, 不把基础设施失败填成0分.

在results/2026-11-12_overnight中运行:

```sh
python scripts/recompute_skills_portable.py --data-root portable_checkpoint_20261112T1120Z --out /tmp/cgl-recomputed-new-folder
```

输出目录必须不存在, 避免覆盖. SELF_CHECK.json记录逐字段核对: 重算results.json和当时原统计完全一致. 这只是11:20UTC中途快照, 不是最终结果; final输出以最终报告指定路径为准. JSON null表示unknown, CSV/Markdown写unknown. 不下载环境、不调用模型、不重新求解题目.

ADV评分也可只用已保存的有效记录重算:

```sh
python scripts/analyze_adv_judge.py --rubric-file adv_rejudge_i003/VALID_JUDGMENTS.jsonl --pairwise-file adv_rejudge_i003/VALID_JUDGMENTS.jsonl --out /tmp/cgl-adv-recomputed-new-folder
```

ADV第一批rubric只有52/60完整, 不能当作20题完整比较; 未授权修正前不把部分Full均值写进论文.
