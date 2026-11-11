# 第5轮冻结版本的两题三组完整对照

2026-11-11完成. 这里的完整范围是同一threejs skill全部2道配套题, 不是SkillsBench全库87题. 共6次新Profy求解, 全部使用gpt-6.1-sol标签, 原评分程序不改, 没有输出后处理补分.

| 任务 | 组别 | 原测试通过数 | reported tokens | 耗时(秒) |
| --- | --- | --- | --- | --- |
| threejs-to-obj | no-skills | 3/3 | 119535 | 147.858 |
| threejs-to-obj | with-skills | 3/3 | 141761 | 149.604 |
| threejs-to-obj | with-CogniLife-skills | 3/3 | 103971 | 128.3 |
| threejs-structure-parser | no-skills | 1/3 | 83735 | 110.894 |
| threejs-structure-parser | with-skills | 3/3 | 95877 | 131.56 |
| threejs-structure-parser | with-CogniLife-skills | 3/3 | 113355 | 122.255 |

原版两题合计237638 tokens, 进化版217326 tokens, 本次合计减少8.55%. 两组均两题全部原测试通过. 每题3项检查, 不是每组3道题或全库准确率.

收益不均匀: 单OBJ题tokens少约26.7%, 分部件题反而多约18.2%. 不能写成每项任务都更省. 本次只支持这两个已用于开发的任务上的观察, 不支持稳定收益、显著性或独立泛化结论. 汇总耗时也仅列实际观察, 不替代token指标.

第4至5轮Evolution实际返回美元费用共$0.375259. Profy未提供美元账单, 不能给出完整实验美元总费用, 也不能把执行tokens的降幅当成完整实验费用降幅. 生成和调试成本不包含在上面的单次执行tokens比较里.

停止决定: 第5轮小范围两题均3/3, 两次合计tokens均低于预定原版基线; 冻结后两题三组对照也保住质量和合计tokens优势, 因此在第5轮停止, 不继续烧到30轮. 若后续扩展其他skills/任务, 属于另外的范围.

兼容保护明确属于本实验新增: 保留原公开skill原本的non-indexed输出惯例. 旧1/3官方分数不改, 但它已被离线定位为等价OBJ表示与原verifier抽样交互, 不能直接解释为几何失败. 新运行由模型重新生成并导出, 不转换旧答案刷分.

原workflow、门控、run_stats模型和渲染仍从收到的Profy源码调用. 通用语义适用性检查、capability-gap classifier和native creator accept/promotion没有完成, 不能称完整CogniLife平台复现. 两题均已用于适应性调试, 最后对照也不是独立held-out. 论文和OpenReview未改.

每轮的指标、hash和模型OBJ输出分别存档; 第4轮成本未改善的记录保留. repo不收第三方代码、原/派生skill全文、原输入、gold或keys.
