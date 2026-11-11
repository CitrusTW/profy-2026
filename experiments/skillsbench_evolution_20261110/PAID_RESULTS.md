# gpt-6.1-sol新skill小跑结果

2026-11-10, America/Los_Angeles. 这是实际API运行和原程序评分. 验证题以前已分析过, 本次是修复后的对照小跑, 不能当新的独立held-out结果.

| 运行 | 原测试通过 | strict | 耗时(秒) | tokens | 工具调用 | 目标skill读取核验 |
| --- | --- | --- | --- | --- | --- | --- |
| dev_original | 3/3 | 1 | 156.874 | 152865 | 9 | True |
| dev_candidate | 3/3 | 1 | 173.908 | 287965 | 15 | True |
| no-skills | 1/3 | 0 | 145.204 | 104913 | 5 | None |
| with-skills | 3/3 | 1 | 146.394 | 136231 | 10 | True |
| with-CogniLife-skills | 1/3 | 0 | 147.377 | 188873 | 10 | True |

本轮新skill相对原版: 少通过2项原测试; reported tokens差值+52642, 耗时差值+0.983秒. 这都是单次观察, 不能据此判断稳定收益.

Evolution由OpenRouter的gpt-6.1-sol完成, 4次请求, 32.386秒, 回报费用$0.126217. 三组求解由Profy完成. Profy求解和接口诊断没有美元账单, 不编总费用.

开发基线复用上一轮真实记录; 其他4次求解为本轮新运行. 后两组提供的文件只有threejs/SKILL.md不同. 候选在验证前冻结, 验证后没有改候选或再进化. 原评分、容差和任务输入未改.

进化只使用开发题原材料和真实轨迹, 复用收到的原Evolution workflow与门控. 没有把验证题答案、原verifier或旧失败分析传给进化模型. 自动适用性检查、capability-gap classifier和native promotion仍未完成, 不冒称完整论文方法.

Private repo保存本助手写的代码、这份报告和数字/hash. 第三方source、skill正文、原始输入、gold和keys不进repo. 完整原始记录保留在工作区的同名run目录.

本轮结论: 新skill虽然通过开发题, 在验证题仍只通过1/3项测试, 原版为3/3. 新skill验证tokens比原版多52642, 约38.6%; 开发tokens也比复用基线多135100, 约88.4%. 这轮没有证明CogniLife refinement带来收益, 不扩大运行.

失败位置: 新skill组通过了输出目录检查, 但两项几何匹配检查失败. 原版组三项全过. 这不是文件没有拿回来、没有评分或没读到新skill; 当前不根据验证题的预期值修改skill, 也不编造已经确定的唯一根因.

接口排障另外保留: 1次DNS阻止发送, 2次400拒绝和5次502 provider错误, 另有1次14-token极短对话成功. 这些不是benchmark成绩. Profy没有返回美元账单, 不把错误请求的费用假定为0. 后续OpenRouter Evolution实际4次成功调用的回报费用为$0.1262168.

结果存档还包括PAID_OUTPUTS_ONLY.zip: 三组验证的原生交付ZIP、两次开发的OBJ原字节(开发基线注明复用, 不收开发输出里的JS脚本), 以及本助手生成的result/usage/manifest JSON. 其中只有模型产出的OBJ数据和元数据, 没有第三方代码、原skills、gold或密钥.
