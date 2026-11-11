最新状态更新: 用户已澄清, 可以使用已有OpenRouter和Profy API keys. 原停用说明仅保留作历史, 已解除锁并恢复开发题执行. 不购买新服务, 不改论文.

# 目前完成到哪里

2026-11-11. 用户最新要求不花钱, 已停止后续Profy和OpenRouter付费调用. 没有正在执行的付费实验脚本. 没有操作银行卡或发送email. 新电力任务批次的模型调用数是0.

## 已完成的模型实验

threejs进化在第5轮达到预先写下的小范围标准: 两题均通过全部原测试, 两次确认的执行tokens合计均低于原版基线. 随后冻结skill, 完成这两道配套题的三组对照, 共6次新求解.

| 组别 | 完全通过的题数 | 两题执行tokens合计 |
| --- | --- | --- |
| no-skills | 1/2 | 203270 |
| with-skills | 2/2 | 237638 |
| with-CogniLife-skills | 2/2 | 217326 |

进化版合计tokens少8.55%, 但不是每题都省: 单OBJ题少26.7%, 分部件题反而多18.2%. 两题都参与过开发, 不能当作独立泛化证据. 没有提高原版已全通过的准确率. 原评分和旧失败成绩没有修改. 详见[两题完整报告](../run-04-up-to30/full-compatible-two/REPORT.md).

上面的运行和第4至5轮Evolution发生在用户此前明确允许付费的阶段. 最新不花钱指令之后, 没有发起新的模型请求. Profy没有提供美元账单, 不把tokens等同于总费用.

## 不花钱完成的准备

- 27项代码检查通过, 包含付费停用锁: 旧的--allow-paid参数不能绕过最新停止指令.
- 固定当前SkillsBench默认全库87题的公开文件和skills清单, 只记录名称、hash、大小和状态, 不把清单当运行成绩.
- 下一批电力题已准备好原Docker评分环境. 原oracle自检结果为调度题6/6、价格分析题4/4. 这是原评分环境检查, 不是Profy模型得分, 不计入论文实验结果.
- 开发题固定为grid-dispatch-operator, 后续评测题固定为energy-market-pricing. 目标只修改shared economic-dispatch skill, 其余skills保持原样. 评测答案、输出、oracle和verifier不会进入进化输入.
- xlsx批次没有发给OpenRouter、没有模型调用. 它附带的LICENSE.txt写明禁止派生版本, 因此先跳过. 全库清单中23道题含有需要进一步核对授权的skill声明; 这是逐文件检查标记, 不是已经完成授权判断.

## 还没有完成

SkillsBench全库87题的三组实验没有跑完. 除threejs两题外, 其余85题没有本轮新三组结果. 新电力批次也还没有新skill或模型成绩.

后续模型运行会产生API费用, 当前保持停用. 重新获得明确的付费授权前, 不移除PAID_CALLS_DISABLED.json, 不自动续跑, 不用本聊天手写skill代替OpenRouter进化.

论文和OpenReview没有改动.
