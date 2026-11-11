# SkillsBench三组小跑: 原版通过, 进化版发生负迁移

日期: 2026-11-10, America/Los_Angeles. 状态: 小范围实验和原评分已完成; 没有扩大、没有改论文、没有提交OpenReview.

## 先看实际结果

验证原题是threejs-structure-parser: 把另一份3D模型按部件导出成多个OBJ文件. 所有组同一Profy hosted执行器、gpt-6.1-sol标签、原题、原输入、原程序评分. 三组各1次, 是1道验证原题, 不是3道题或3个独立研究样本.

| 组 | 原测试通过项 | 原整题strict reward | 客户端任务耗时(秒) | 累计tokens | 工具调用 |
| --- | --- | --- | --- | --- | --- |
| no-skills | 1/3 | 0 | 106.606 | 82,476 | 4 |
| with-skills | 3/3 | 1 | 132.231 | 119,169 | 8 |
| with-CogniLife-skills | 1/3 | 0 | 125.900 | 113,156 | 7 |

原测试的3项分别是输出目录存在、分部件几何匹配、合并部件几何匹配. 1/3只表示第一项通过, 不是业务准确率33.3%. 三组均0 skip. 原版with-skills通过全部检查; 进化版实际未通过两项几何检查. no-skills准确指没有提供SkillsBench skills包, 仍保留相同平台基础工具; 没观察到额外skill工具激活.

tokens是每个原生usage.token事件累计的input+output, 包含重复上下文和cache命中, 不是独立新文本量或实际美元费用. 三组并行, 耗时包含环境准备、求解和文件回传, 不含附件上传; 单次耗时差不能当稳定速度提升. Profy真实货币费用为unknown, 未把缺失当0.

## 原方法到底执行了什么

开发题threejs-to-obj要求导出整个物体, 并明确为Blender转换坐标轴. 它与验证题使用不同data/object.js, 但原threejs/SKILL.md完全一致. 原题commit为f860ecf02ef53412a030f8661c83d644b739ff01. 不使用6个expert包, 不自行写benchmark.

1. with-skills完成开发题: 原评分3/3, strict=1, 156.874秒, 152,865 tokens, 9工具调用.
2. 平台外工具循环读取收到的原EVOLUTION.md、原builtin/evolution workflow、原skill发现/激活函数和原evolution_log.py. 只输入真实开发轨迹和测得run_stats, 未提供验证题、gold或verifier.
3. 原门控接收一条候选. 原skill为3226字符, 候选2212字符, 缩短31.43%. 门控质量组54.5→67.0、效率组18.91→30.0; 除代码计算footprint为98.92→100外, 这些是模型估计, 不是实测能力分.
4. 候选再做开发题: 仍3/3、strict=1, 150.217秒, 162,213 tokens, 11工具调用. 开发任务总tokens反而增加6.12%, 因此压缩不等于实际更省. 按预先写明的原门控和开发reward不下降条件, 候选被冻结; 未增加一个事后实测省token门槛来筛掉负结果.
5. 冻结候选后, 三组对验证题各执行1次, 原verifier自动评分. 后两组均有原生完整读取与SHA256记录, 确认第三组真的加载新版. 其他原skills/资源hash相同, 无额外开发经验文件给第三组.

这复用了收到版本的skill-refinement核心, 加的是文件读取、模型工具协议和本地pending存储适配. 它不是Profy内部Evolution服务的运行记录, 也没有验证完整capability-gap分类、线上promotion、Memory或Cross-Expert Attribution. 不把工具协议适配叫新研究算法, 不把此小跑叫完整CogniLife复现.

Evolution模型为openai/gpt-4.1, 共4次OpenRouter请求、8.769秒, 账单返回合计$0.089368. 它是更新模型, 不是额外judge. 共5次Profy逻辑求解, 累计629,879 tokens; 所有货币费用只有OpenRouter这一部分有明确回执.

## 为什么进化后反而错了

开发原题需要把坐标绕X轴旋转-90°, 验证原题要求按现有物体结构导出, 没有这项转换要求. 候选把旋转写进统一编号步骤. 第三组原生求解脚本实际创建makeRotationX(-Math.PI/2), 并对导出几何应用该矩阵; 原版组的脚本没有这个额外旋转.

两个失败检查都出在几何位置. 例如cabin_floor_2.obj的原Chamfer误差为157.722748, 阈值0.0002; cabin_3.obj为170.215759. 对4个已有代表输出只在内存中撤销该旋转后, 相同几何距离函数得到0或约1e-16. 这支持“开发题特定转换被泛化到新题”的解释. 这是现有输出的诊断, 没修改文件、没重评分、没补算通过成绩, 也没付费重跑. 具体数字见coordinate_diagnostic.json.

此外, 候选声称所有步骤/命令均经验证, 超出了开发轨迹能支持的范围; 把实际9次工具调用写成了8次. 这些自述没有修掉后重新计算成绩. 原门控对empirical_grounding给出高估计分, 仍不足以保证候选事实准确或迁移安全.

## 现在对论文能说明什么

- 本例支持原版SkillsBench skill有用的观察: 原版通过, 无benchmark skills未通过. 只有1道验证题/每组1次, 不推断整个benchmark.
- 本例没有证明进化带来收益, 不能写“CogniLife提高准确率”或“质量不降而更省”. 第三组质量下降, 其约5.05%更少tokens不能当同质量下的效率收益.
- 如果论文采用此案例, 它可说明“候选自评门控和开发题通过, 仍挡不住适用条件丢失导致的负迁移”. 这是一条方法边界观察, 不是跨expert归因有效的证据.
- 先保留完整负结果交讨论, 不按已看过的验证题答案改skill再称独立测试. 暂不扩大此冻结版本. 原85题/52题数字不变.

原输入、原skill、原verifier、原参考生成器及实际运行均有hash索引. 所有交付ZIP和内部文件都与原生SHA256一致; 输出与分数没有手工修正. 评分只绑定/root路径, 原断言、容差和预期值不变. 三组不存在输出复制或候选回退的已观察证据, 负结果不能用“根本没加载skill”解释.

完整证据: [SkillsBench三组小跑-完整证据-20261110.zip](https://drive.google.com/file/d/1leKQ0EoTk1hleD2yUWZK1cnMH-Za7TJ0/view). 包内含5次真实求解记录、原生交付、原评分回执、原Evolution工具轨迹和坐标诊断, 不含密钥.
