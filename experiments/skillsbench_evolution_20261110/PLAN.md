# SkillsBench三组小跑

2026-11-10, America/Los_Angeles. 用户现已明确允许付费小跑, 以及把原context和开发轨迹发到OpenRouter运行gpt-6.1-sol. 本次不改论文、不提交OpenReview. 旧小跑已结束, 其结果单独保留. 本次范围见[PAID_RUN_PLAN.md](PAID_RUN_PLAN.md). 修复详情见[OFFLINE_FIX_REPORT.md](OFFLINE_FIX_REPORT.md).

只问一个问题: SkillsBench原版skill经过论文的skill-refinement核心流程更新后, 另一道任务能否做得更准, 或在质量不降时更省? 不从expert包提取任何内容.

## 固定材料和三组

公开来源: https://www.skillsbench.ai/ 和 benchflow-ai/skillsbench. 固定本地commit f860ecf02ef53412a030f8661c83d644b739ff01.

- 开发: threejs-to-obj. 输入只有data/object.js, 输出output/object.obj; 按原题保留物体位置并转换坐标轴. 只用开发求解的真实工具轨迹学习, 不把verifier、groundtruth、oracle、预期值传给更新模型.
- 旧验证: threejs-structure-parser. 输入是另一份data/object.js, 输出output/part_meshes与output/links中的OBJ文件. 旧小跑使用原verifier, 旧候选冻结前未向更新模型提供这道题. 现在已分析过该题结果, 不能把后续调过的skill在同一题上的成绩当作独立验证. 当前修复不读取该题答案, 不新增选题或付费运行.
- 两道题各自提供的threejs/SKILL.md完全相同: 3226字符, SHA256 ea480298751ea55effee4535b16b67ec79fd9540b971a89712e6f5b9ce8cd663. 两份data/object.js输入不同. 所以可以学习同一原版, 再替换到新任务, 无须自造skill或跨版本改写.
- 选题预检: 原xlsx候选的单独LICENSE明确限制改写, 在任何付费调用前排除. 本轮threejs skill未标单独Proprietary条款, 保留仓库LICENSE和文件来源. 不因整个仓库Apache而忽略各资源的单独条款.

| 组 | 提供什么 |
| --- | --- |
| no-skills | 原题和原附件, 不提供本题SkillsBench skills |
| with-skills | 再提供本题environment/skills的完整原版文件 |
| with-CogniLife-skills | 同一套文件, 只把threejs/SKILL.md换成原核心方法产生、通过原门控并完成开发比较的冻结版本 |

同一Profy hosted执行器、gpt-6.1-sol标签、公共工具、预算和任务输入. 每次独立session/sandbox. 不加载expert包、身份或Memory. 平台自己的基础工具保持相同; no-skills准确含义是no benchmark-supplied skills, 不能据此声称底层没有任何builtin技能. 如果观察到额外skill激活或读取, 记录污染, 不冒称有效的纯no-skills.

## 第三组具体复用了什么

原文件从工作区Profy-main外部读取, 不复制进自有代码仓库:

1. plugins/builtin/evolution/prompts/EVOLUTION.md原Evolution行为prompt, 通过原plugin registry装入静态context.
2. plugins/builtin/evolution/skills/evolution/SKILL.md原工作流和10维rubric.
3. plugins/builtin/skill/tools/skill.py原discover、activate和scope读取逻辑.
4. plugins/builtin/evolution/tools/evolution_log.py原函数体, 包括维度校验、字符footprint、质量组不降/效率组严格提高的ratchet. 不改权重、阈值或接受条件.
5. api/agent.py中的原启动消息和_format_run_stats渲染; 输入实际工具操作记录与测得用量.

修复后的代码把开发题的完整skill目录接到原读取接口, 用原ContextManager和plugin registry组装静态context, 保留历史消息角色及工具调用配对. Evolution通过OpenRouter `/api/v1/chat/completions`, 请求模型固定openai/gpt-6.1-sol, 不回退4.1. Profy plain chat工具请求实际返回provider错误, 切换目的地已获明确授权. 原pending仍只保存在实验目录. expert/threejs是外部适配器的技能作用域, 不代表平台数据库注册或promotion. Profy plain chat的6.1工具请求已试跑并返回502; OpenRouter同模型已实际完成生成. 旧小跑实际使用4.1, 不改旧记录.

这是收到版本的skill-refinement核心外部适配, 不是完整CogniLife复现. 收到代码中尚未找到capability-gap classifier和自动语义适用性检查的对应实现; native acceptance / promotion没有接入. 三项缺口写入机器可读检查结果, 不补写prompt冒充原实现. 原门控分数多为模型估计, 只决定接收建议. 新核验另查模型、请求hash、父版本、候选正文、开发执行和评分一致性, 同时报告实测tokens/工具数; 不把这些新核验说成原门控已经有的功能, 也不把结构核验说成语义核验.

## 执行和停止

1. 文件/hash、原函数和输出传输离线检查通过.
2. with-skills做开发题一次, 保留实际输出、工具参数/结果和usage.
3. 原Evolution生成至多一条pending建议. 最多8轮模型工具循环; 原门控允许拒绝, 也允许无建议结束. 不靠修改rubric强行通过.
4. 有候选才跑开发比较. 原门控收下建议后, 另查候选与pending正文一致、来源hash、实际模型、执行完成、目标skill读入和原评分完整性, 开发质量不降才允许外部候选评估. 这一步不是native promotion或完整方法认证.
5. 冻结后验证题三组各一次, 复用原评分. 更新模型不接触这些结果. 如没有可用候选, 第三组标not_run, 不用原skill换名充数.
6. 交实际数字与方法范围, 再讨论扩大. 不根据验证题分数继续改skill后报成独立测试.

将来另行允许付费后, 上限仍为5次Profy求解(原开发1+候选开发1+验证3), 每次15分钟、48个工具调用、24个模型回合. 不自动重发; Evolution最多8次OpenRouter模型请求, 无独立judge. Profy真实货币费用没有账单就写unknown. 旧OpenRouter费用保持历史记录. 无GPU需求, 本机只调度/取文件/程序评分. 付费phase默认需要显式开关; 本次小跑已获准, 不自动扩大. 旧验证题只能作为diagnostic repeat, 不当作新的独立验证.

原评分只允许绑定运行路径, 不改断言、预期值或容差. 报告passed/failed/skipped和返回码, 关键skip不能视作通过. 输入/输出hash、真实文件取回、skill读取/版本与潜在污染分别保存. 两个原task的小跑只能支持小案例判断, 不能当完整SkillsBench成绩或跨expert归因证据.

代码仓库只收本助手写的适配代码、说明和数字摘要. 原SkillsBench skills及其资源、改写后的派生skill、第三方代码、原附件、gold和密钥全部留在仓库外. Google Drive不提及或链接自有private repo.
