# I003第一批完成, 截断问题明确

- 140个主job都已处理, 共159次调用, 132个主job有有效JSON, 27次失败调用完整保留.
- rubric: Raw20/20、Expert Prompt20/20、Full12/20. Full缺8题, 都没有手填或从半截JSON取分.
- pairwise: 全部80次有效, 20题 × 两个基线 × 正反顺序.
- API费用回执合计USD3.529044; unknown费用调用0.
- 统一重做60个rubric、所有条件max_tokens4096的保守预算上界USD8.054640; 加现有回执合计预算上界USD11.583684, 小于原15美元总上限. 这是已知支出+未来额度上限, 不是实际支出估计. 模型、输入、prompt、解析和seed不变; 旧rubric全部归档, 不择优混合.
- 在授权修正前不启动这一批; 不把当前12题Full均值写成20题成绩.

完整原始证据在adv_rejudge_i003, provisional分析在analysis_batch1. 原始rubric来源仍不完整, 不发布完整20题Rubric结论.
