# CogniLife skills 适配修复记录

2026-11-10, America/Los_Angeles. 本轮修好了能离线修的适配和核验问题. 9项测试通过, 模型请求0次, benchmark运行0次, 没读密钥, 没改论文. **尚未生成新的gpt-6.1-sol skill, 不能说skill效果已经调好.**

## 改了什么

| 原来的问题 | 现在怎么处理 | 检查到了什么 |
| --- | --- | --- |
| Evolution写死OpenRouter的gpt-4.1 | 请求改为Profy `/v1/chat/completions`的gpt-6.1-sol, 无旧模型fallback | 请求模型和目标地址已核对; 没在线试调用 |
| system只用了EVOLUTION.md | 调用收到的原ContextManager、原STATIC_PIPELINE和原plugin registry组装代码 | security、identity、soul、tools、workflow、Evolution和skill目录层都有fingerprint, 重复组装结果相同 |
| 历史压成一个user JSON | 用开发题真实request input和SSE记录, 还原user/assistant/tool角色 | 9次真实工具调用与9份结果完整配对, 缺结果或ID不一致会报错 |
| 只让Evolution发现threejs | 用原metadata parser和discovery函数读取开发题完整skills目录 | 能发现threejs、obj-exporter和builtin/evolution; 只允许修改预先选定的threejs |
| 原门控接收后, 只看开发分数就放行 | 增加请求模型/hash、父版本、候选与pending正文、实际skill读入、执行/评分完整性检查 | 旧4.1候选被拦住; 篡改候选、错误模型和开发失败的测试都能拦住 |
| 本地pending容易被误当作已更新平台skill | 分别保存原门控接收、结构/开发核验、语义核验和native promotion状态 | 后两项不会自动写成true |
| 误运行命令可能花钱 | 付费phase默认关闭; 调用前检查, 离线命令不加载key | 测试证实未允许时, 在读key和创建attempt之前就停止 |

这些改动没有另写学习prompt. 原EVOLUTION.md、原evolution workflow、原skill工具、原启动消息、原run stats和原evolution_log仍从收到的Profy-main调用. 原权重、阈值和质量/效率自评分门控没有改.

## 用旧记录查到了什么

把旧候选的同一份提议交给原evolution_log离线重放, 仍然接收, pending内容完全相同. 这说明原门控确实会收下这份自评分, **不能证明候选适用于另一道题**. 新核验没有假装能解决自然语言适用性.

旧开发结果仍是两次3/3, 但tokens从152865到162213, 多9348, 工具调用从9到11. 不能把候选自评“更省”当成测得更省. 实测数字单独报告, 没把新效率硬门槛冒称原实现.

旧验证仍保留原版3/3、旧进化版1/3的结果. 旧候选、输出、分数、benchmark与附件共787份已存在文件hash未变; 另与上一轮审查里的24份原始记录逐项核对一致. 新检查写到run-01/adapter_fix_checks, 不覆盖旧实验.

## 还缺哪些原方法实现

1. capability-gap classifier: 论文说先判断问题来自expert能力、任务指令还是环境. 收到版本尚未找到可调用的对应实现. 当前没有用新分类prompt补上它.
2. semantic applicability check: 要判断从一题学到的操作能不能放进通用skill. 收到版本尚未找到自动检查实现. 原门控检查expert归属、自评分和文本长度, 不自动理解所有适用条件. 新hash和格式检查也做不到这一点.
3. native acceptance / promotion: 原平台审核、接受、版本晋升没有接入. 保存一个local pending或冻结hash, 不等于平台已经审核并生效. 也不能说只要补这个步骤就一定能发现旧候选的错误.

这三项在OFFLINE_FIX_FACTS.json里逐项标明. 当前代码只能称为skill-refinement核心的外部适配, 不能称完整论文方法已经复现.

## 现在能不能开始下一轮

离线适配检查已过, 旧候选不会被冒充新版本使用. 但本轮按要求没有付费, 所以没检验Profy plain chat的gpt-6.1-sol function calling线上响应, 也没有新的skill效果数字.

threejs-structure-parser的失败已经被看过. 当前修改没有使用它的题面/答案来生成规则, 但仍不能把今后在同一题上的调参成绩叫作独立验证. 本轮不扩大、不重新出题、不改benchmark, 不根据那道题的答案手工改skill.

原始请求组装文件只保存在工作区, 含收到的原context和开发轨迹, 不提交private repo. private repo只保存本助手写的代码、这份说明和不含原文的检查数字.
