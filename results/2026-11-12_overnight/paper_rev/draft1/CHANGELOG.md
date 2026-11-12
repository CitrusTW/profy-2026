# 论文修订初稿: 改了哪里, 数字从哪里来

正文6页, PDF共21页. 编译通过, 无超宽框或未解析引用. 原论文/Overleaf/OpenReview均未改动. 初稿用于11:15审核; Profy恢复后的新增结果和审核意见在final更新.

| 位置 | 修改 | 数据出处 |
|---|---|---|
| Abstract / Introduction | 85题主结果改为当前ADV20新评分; 加独立的冻结skill执行检查 | adv_i004_analysis_v2/results.json: means; skills_draft1/results.json |
| 4.1 | 仅保留平台ADV20; 说明模型不同、原65份代理输出不使用 | ADV_METADATA_INPUT.json; provenance/PAPER_PROTOCOL_VALUES.json |
| 4.2 / Table2 | 三个条件均值、Full减两基线的均值/CI/高低平 | adv_i004_analysis_v2/results.json: means,full_minus_baseline |
| 4.3 | missing_info与Expert Prompt持平; Full coherence/safety更低 | adv_i004_context_analysis/results.json:variant_results; adv_i004_analysis_v2/results.json:means |
| 4.4 | 两种基线的正反序pairwise, 前3000字符限制 | adv_i004_analysis_v2/results.json:pairwise; provenance/PAPER_PROTOCOL_VALUES.json |
| 4.5 | 重算确认平台20份耗时, customs数字不动 | adv_i004_context_analysis/results.json:platform_full_timing; 原customs_appendix.tex完整保留 |
| 4.6 / AppendixG | 外部适配范围、全部现有有效/失败/上限记录、版本、tokens、波动未知、门控反例 | skills_draft1/results.json; provenance/history_results.json; provenance/selection_records.json |
| Conclusion / Limitations | 限定20题和生成模型差异; 不声称进化提高正确率或降低tokens | 上述ADV/SkillsBench统计, 按I001/I002/I005措辞规则 |
| AppendixA/B | 删除旧85题图表; 只放新ADV维度、error tags、variant、pairwise完整计数与实际judge设置 | adv_i004_analysis_v2/results.json; adv_i004_context_analysis/results.json |
| Screenshot panel(d) | 清除剩余Expert Distillation Studio顶栏文字; 标题外像素完全相同 | 本JSON:screenshot_redaction |

每个新增数字的原始精度、展示值、结果文件字段和hash, 见CHANGELOG_NUMERIC_SOURCES.json. 479个引用项已逐个核对. 缺失数据写unknown; 单次运行不填0标准差. 3/3、1/3指verifier检查项, 不是3次独立运行.

Deployment context原文:

The controls in Section 3.4 run in a commercial, paid expert marketplace: creators publish experts, and callers use the web, API/SDK, or enterprise instant messaging, with payment tied to delivered results. At the time of writing, the marketplace hosts several hundred experts. Temporal memory consolidation has been in production since mid-2026. Within the expert-service comparison, only the ADV 20 Full outputs were generated through the deployed platform; the screenshots in Appendix C come from that deployment.

SkillsBench目前预选8题仅powerlifting-coef-calc完成三组完整评分; 其他有效补评分、失败、上限和未开跑均保留. energy-market-pricing和早期protein结果单独注明skill和版本; 开发/选版记录不计held-out. Profy仍因Expert is not published受阻, 不把403当答错.
