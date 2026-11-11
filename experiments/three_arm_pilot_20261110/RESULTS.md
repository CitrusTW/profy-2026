# 三组小实验: 实际结果

**本轮已执行并评分, 但没有形成有效的三组方法对照, 不能写成CogniLife提升证据.**
本轮是新写的skill更新研究原型, 不是袋袋原生evolution, 也没有测跨expert归因.
练习是员工PDF/Excel记录差异核对, 考试是另一道发票核对原题. 每组只有一次考试尝试.

| 阶段/组别 | 原strict通过 | 原pytest通过/总数 | 秒 | 工具调用 |
| --- | --- | --- | --- | --- |
| dev_before | 1 | 11/11 | 247.151 | 15 |
| no-skills | 0 | 1/2 | 63.630 | 6 |
| with-skills | 0 | 1/2 | 92.535 | 21 |
| with-skills-cognilife-method | 0 | 1/2 | 89.667 | 21 |

秒数统一按原生events的首尾时间差统计, 不含附件上传. 开发任务客户端另记249.492秒. 工具调用按tool_call_id去重.

## 第三组有没有真的采用更新

采用新版: 否, 按规则保留初始版.
初始skill为1191 UTF-8字节, 候选为1525字节. 预先规则要求变短, 所以候选在再次做开发题之前就被拒绝. 本轮没有执行dev_candidate.
因此第三组实际使用的expert包与with-skills相同. 两组相同的分数不能用来判断skill更新有效或无效.
采用记录: {"accepted": false, "error_type": "ValueError", "fallback": "unchanged original skill"}

## no-skills也有一个输入问题

首版代码把开发运行的工具输出片段作为共同经验给了三组. 其中夹带了读取expert/skills/xlsx/SKILL.md的内容, 所以no-skills虽然没收到expert.zip, 仍间接收到了一部分skill. 它不是干净的无skill组. 这是本次实现问题, 不能归因于论文方法.
当前代码已改成只共享公开开发题面和运行统计, 并加了检查. 这是执行后的修复, 没有用修复版付费重跑, 也没有改写本轮原输入.

## 为什么三组都是0

三份fraud_report.json的SHA256完全相同. 原评分包含文件存在检查和整份内容检查; 三组都是文件存在通过、内容检查失败, 所以原strict均为0, pytest均为1/2. 这不表示发票识别准确率只有50%.
原评分首先停在第4页的po_number: 返回PO-INVALID, 参考答案要求null. 只用已经保存的文件继续做离线诊断, 发现53页中50页被参考答案标为有问题; 三组都找齐这50页, 没多报或漏报. 对照JSON的全部字段, 有5处po_number不一致, 其他字段值相同. 这是额外诊断, 没有替代或放宽原评分.

## 怎么理解

原strict是整题通过=1、未通过=0. pytest通过项不是字段准确率. 一道考试原task、三次运行不能当成三个独立任务, 也不足以说明普遍提升或做显著性结论.
本轮只完成了运行和排错记录. 由于第三组没有采用更新、no-skills又夹带skill内容, 不能拿它补论文里的方法效果或跨expert缺口, 也不能说原论文方法没用. 不把这组结果加入论文主结果.

## 实际调用和token记录

本轮共4次Profy任务调用: 1次初始开发题、3次测试题; 另有1次OpenRouter请求. 没有额外付费答题或重试.

| 阶段/组别 | prompt tokens事件合计 | completion tokens事件合计 |
| --- | --- | --- |
| dev_before | 218992 | 2572 |
| no-skills | 122679 | 2201 |
| with-skills | 251212 | 3149 |
| with-skills-cognilife-method | 257077 | 3394 |

token数按usage.token原生事件逐项求和, 不是已经核对过的货币账单.

## 费用与数据

Profy货币账单未取得, 因此费用写未知, 不填0或虚构估计. OpenRouter返回费用: 0.0009308 USD.
OpenRouter只收到公开题面和数值统计, 不收到私有expert原文、工具结果原文或答案. expert包只用于Profy任务执行.
原始文件、模型输出、第三方grader和完整日志留在本地, 不提交到代码仓库.

## 实现记录

实际执行代码commit: e68a13ba60bc2ccf7b19a6cb3a0fc01a0203d950.
首版driver漏识别了in_progress形式的工具计数; 上表已从原始event ID重新统计. 开发期writer实际收到的tool_call_count为0, 这个历史输入保留不改.
首版回传解析混入了开发经验中的旧编码片段. recover_outputs.py只从各次任务自己的bash返回中恢复文件, 检查字节数与SHA256, 再调用原评分. 没有重新请求模型, 没有改回答或评分断言. 初版解析失败摘要保留为summary_initial_decoder_failure.json.
没有修改论文或提交OpenReview.
