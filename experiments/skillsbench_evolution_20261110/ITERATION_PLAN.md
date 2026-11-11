# 先把skill进化好, 再做最后对照

2026-11-10, America/Los_Angeles. 已获准付费多轮小跑, 模型固定gpt-6.1-sol. 不改论文或OpenReview.

目标: 在收到的原Evolution流程内, 找到这次预算里开发题质量保持、实测tokens最低的候选. 不把最优理解为任何任务都最优.

1. 从SkillsBench原版threejs开始. 把原版开发记录和上一份成本变差的候选开发记录一起提供给原Evolution. 只提供DEV的真实request/events及每次实际版本的run_stats, 不传历史验证结论、gold、verifier或评分失败细节.
2. 每次invoke仍按原workflow只提出一条建议. 独立复制DEV完整skill目录, 把该轮实际parent接入原工具和原门控. 用原EvolutionRunStats校验最多20条历史, 再用原渲染函数组装. 不新写学习prompt或另改rubric.
3. 每份新候选在threejs-to-obj上实际运行, 用原verifier评分. 得分全通过、skill读取hash正确、没有异常/额外skill调用, 并且reported tokens比当前best低, 才更新best. 未选中的真实DEV记录仍反馈给下一次invoke, 不把它伪装成成功改进.
4. 最多3次新invoke; 连续2份没有改善或模型不提出建议就停止. 选择只依赖DEV. 原版一直是合法退路, 没有更好候选就不把原版改名叫进化版.
5. 最佳候选另跑一次同一DEV确认. 仍需原测试全过、tokens低于原版. 未确认就停止, 不扩大验证.
6. 确认后冻结hash, 最后才跑no-skills、with-skills、with-CogniLife-skills各一次. 后两组只替换threejs/SKILL.md, 其余题面、附件、resources、模型和预算相同. 验证后不继续改skill.

预算上限: 3次新Evolution invoke(每次最多8次模型请求), 3次新候选开发检查、1次最佳候选确认、3次最终benchmark求解. 每次求解最多15分钟/48工具/24模型回合. 不自动重试可能已付费的请求.

另外做了只看DEV的独立agent复核和离线测试, 它们属于新增实验检查, 不是原作者已有的算法. 复核不能证明未经历分支一定正确.

官方SkillsBench main仍为本地固定commit f860ecf02ef53412a030f8661c83d644b739ff01. 当前只有threejs-to-obj和threejs-structure-parser包含同一threejs skill, 没有新的同类独立holdout. 最后那题已被分析过, 只能标为diagnostic. 不用无关题凑结果, 不声称完整benchmark或完整CogniLife复现.

尚缺原capability-gap classifier、通用语义适用性核验、native creator accept/promotion. 新增迭代/选择逻辑明确标为外部实验编排. 原始第三方代码和skill正文不进入private repo; 保存助手代码、结果与模型生成的OBJ数据.
