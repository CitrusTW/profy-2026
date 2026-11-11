# 这次进化哪里出了问题, 先修哪里

核对日期: 2026-11-10, America/Los_Angeles. 只读原论文、收到的代码和run-01已有记录. 新模型调用0次, 新benchmark运行0次. 未改原skill、候选、benchmark、答案、评分或运行代码.

## 结论

这份进化后的skill确实改坏了: 它把开发题要求的坐标旋转放进通用操作流程, 新题也照做了. 我的候选筛选没有挡住这个问题. 不能把这次结果归成完整原论文方法失效.

也不能把责任全部说成“适配漏接了一个现成的适用条件检查”: 收到的evolution_log.py里没有这项自动检查. 同一候选和原自评分数在原函数离线重放时仍然通过, 分数字段与原pending完全一致. 原门控公式没有被我改坏, 但它只控制建议进入候选队列, 不是完整的条件验证和生效流程.

现有证据同时确定了两件事: 收到的候选生成核心没有拦住这次错误; 外部适配没有复现完整原生运行与候选生命周期. 不能只靠这一次记录, 确定GPT-4.1、context、历史组织或其他差异各自贡献了多少失败.

## 从候选文本追到错误输出

原threejs/SKILL.md的Quick start没有要求每次旋转; 坐标转换是在单独的Axis conversion小节介绍. 候选把它提到统一Workflow第5步, 要求对所有baked geometries应用-90° X rotation. 它还写了“Blender需要时不能跳过”的条件句, 所以准确说法是主流程扩大了默认适用范围, 不能说原文某个if被字面删掉了.

开发原题threejs-to-obj明确要求为Blender转换坐标轴. 这个来源条件就在进化输入的public_instruction中, 不需要查看验证题答案才能识别它属于当前任务要求. 验证题的第三组实际脚本执行了该旋转. 已有4个代表文件的内存逆旋转诊断支持这个错误解释; 原文件和原1/3结果保持不动.

## 逐项对照

以下Profy路径相对04_项目数据与代码/Profy-main; 适配路径相对本目录. 论文依据为工作区naacl 2027 提交版.pdf的§3.2–3.4与Appendix F, SHA256 dce538935e9c911415b305f62e9413626f0fd82ecf28504af78b451a6ecf4819.

| 环节 | 原论文 / 收到的实现 | 本轮实际做了什么 | 判定 |
| --- | --- | --- | --- |
| 原Evolution prompt | plugins/builtin/evolution/prompts/EVOLUTION.md | request_1.json的system与原文件完全相同 | 已复用, 没有用新提取prompt替换 |
| 原workflow与原skill读取 | evolution/skills/evolution/SKILL.md, skill/tools/skill.py | 实际工具链依次activate builtin/evolution、discover、activate expert/threejs、evolution_log. 原workflow和3226字符目标skill全文均在工具结果中 | 已执行, 没有漏读原目标skill |
| 原10维rubric/ratchet | evolution/tools/evolution_log.py:227–290 | 执行原函数体, 原字符footprint和权重保持原样. 离线重放原payload再次得到同一建议内容/分数 | 已复用. 不是公式被适配改坏 |
| expert/* scope | 同文件:211–223 | 检查本地目标技能属于expert作用域 | 这是“能修改谁的skill”, 不是“这条操作在哪种任务适用”. 原函数没有自动验证后者 |
| evidence/applicability保留 | 论文§3.2要求保留来源和适用性; §3.3的跨expert归因明确是proposed | 本轮没有实现该归因/适用性流程. 原门控只读自评分和长度, 不解析任务条件或检查候选是否扩大规则范围 | 论文要求/提议与已收到可执行核心有缺口. 未发现一个现成的语义条件检查被适配漏接; 补写此检查属于补实现或扩展, 不能称原样复用 |
| expert-capability gap触发 | 论文§3.4区分expert能力问题、任务指令问题与环境问题 | run.py:216–222仅检查开发运行有效, 然后总是调用进化. 没有执行该分类. 开发题已经3/3通过, 是否另有可证实的效率能力缺口没有登记 | 论文声明的触发条件未复现; 收到的相邻实现也没找到明确对应分类器. 不能临时写一个分类prompt冒充原实现 |
| 完整Evolution运行context | harness/context/prompt.py:171起的STATIC_PIPELINE, context/assembly.py:1426起的组装 | native_evolution.py:122只把EVOLUTION.md作为system, 未调用原ContextManager组装通用context | 适配差异. 不能把复用一个prompt说成复现完整原生运行; 但尚未证明缺的context能单独阻止本例错误 |
| 历史角色与工具结构 | api/agent.py:398接recent_messages; context/assembly.py:391–418支持role/tool_calls/tool_call_id转换 | run.py:220挑选实际事件, native_evolution.py:122把它们包装在一个user JSON消息中, 不是原消息转换路径 | 适配差异. 事实记录有传, 角色和来源组织方式没有按原路径接齐 |
| 可读技能目录 | Core buildEvolutionPayload查询当前expert的技能, 原SkillContext负责发现/读取 | LocalSkills只注册builtin/evolution和expert/threejs. 开发配套obj-exporter不在可发现目录, 虽然其原生read结果包含在开发轨迹里 | 适配简化. 应恢复开发侧相关技能的可读上下文, 不给进化器补验证题材料 |
| 进化模型配置 | api/agent.py:394使用调用者传入的llm_config | native_evolution.py:127硬编码openai/gpt-4.1; 三组求解用gpt-6.1-sol | 额外实验变量, 不只是传输变化. 原接口并不强制某个模型, 不能断言模型差异造成失败; 后续要明确配置并与目标原实现对齐 |
| proposal与生效分开 | EVOLUTION.md/ADR-0015要求suggestion-only, creator接受后才改变skill; 论文另有staging/paired reward/promotion说明 | PendingStore写本地候选. run.py:235–239只检查同一道开发题strict不降、输出和读取有效, 然后冻结候选用于第三组 | 没复现完整accept/promotion. 测试未审核候选本身可以是实验, 但不能把它称成已完成原平台审核的版本. 单题通过不能替代适用条件核验 |
| 实测效率反馈 | 原workflow强调measured cost, ADR-0024明确实际效果由benchmark验证, 不是自动实测门控 | 开发原版152865 tokens/9工具, 候选162213 tokens/11工具; 冻结条件没有使用这两个成本指标, 没把候选比较反馈送回下一轮原Evolution | 本轮没有完成多轮反馈. 没用实测效率作硬门控不等于漏接现成代码, 因为ADR明确没有此门控; 但不能宣称已达成“cheaper and not worse” |
| 配套资源调用 | 原Evolution允许read-only技能读取; adapter限制脚本执行 | 本轮进化器没有发出execute请求, 原skill与workflow没有被截断, 四次模型响应都是tool_calls而非length截止 | 没有证据表明脚本限制/长度截断导致这次错误; 不为本例额外开放执行工具 |
| 更新是否落到求解 | 两组只应改变目标SKILL.md | 本轮包的hash差异只有threejs/SKILL.md, 两组实际完整读取及SHA256均通过; 真实输出ZIP hash一致 | 没发现候选回退、错文件或本地复制答案. 不需要修benchmark/scorer来解释失败 |

## 先修哪里, 按顺序

1. **先修我的适配与实验身份.** 对齐原context组装、历史角色、开发侧可读技能和进化模型配置. 只恢复开发侧已有材料, 不重新加入expert包, 不开放原本禁止的工具. 如果仍只测试候选生成核心, 就明确称“外部适配的候选生成实验”, 不称完整原方法复现.
2. **修候选状态与进入第三组的依据.** 把proposal admitted、development checked、原生accepted/promoted分开记录. 保留失败或no-change结果. 原门控通过不再写成候选已获完整方法认可; 同一道开发题通过只说明这一题没退步. 补上真正对应版本的原检查, 缺的部分明确标出, 不拿别的服务的检查顶替.
3. **解决来源条件到通用规则的保留问题.** 依据论文已有evidence/applicability要求, 新增或改变的操作需要说明来源、何时适用、是否比来源扩大. 这次来源条件在开发题指令中就存在. 收到核心没有自动检查实现; 如需新增, 必须注明是补实现/扩展, 不把补写的prompt或规则叫原代码. 也不能声称增加一个字段就能自动理解所有自然语言条件.
4. **修对生成质量的判断.** 候选“全部步骤/命令已经验证”不符合实际轨迹, 实际9次工具调用也被写成8次. 原门控的empirical_grounding自评100仍予放行. 应保留原始自评并与真实事实分开, 不能拿自评分高当质量已经提高. 实际开发成本上升也不能忽略后继续宣称省token.

以上是修复位置, 不是已经验证有效的新机制. 本轮不改进化prompt、候选文本、运行代码或benchmark. 不新增LLM judge/人工评测, 不根据验证题答案加入“碰到这个task就不要旋转”规则. 已看过结果的threejs-structure-parser不能在调参后继续当未见验证题; 如以后有新运行, 必须明确区分开发排错与独立验证.

## 保存的核对证据

run-01/method_audit/AUDIT_FACTS.json记录原文件hash一致性、实际prompt/workflow复用、门控离线重放和适配差异. 原函数重放只写单独的fixture目录, 不写平台或旧实验记录. 本次核对覆盖的26个原文件在核对前后hash保持一致.

**应该如何描述当前结果:** 这份外部适配生成的候选, 在开发题通过后用于新题时退步. 有明确的适用范围扩大问题, 原建议过滤器没有拦住; 但完整论文链路未复现, 各适配差异的独立因果作用尚未验证. 优先修上述适配和候选核验, 不能直接判完整原论文方法无效.
