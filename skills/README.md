# 三组skills和全部进化版本

| 目录 | 是什么 | 先看什么 |
| --- | --- | --- |
| no-skills/ | 不提供benchmark skills | CONDITION.json, 没有虚构SKILL.md |
| with-skills/ | 已跑任务使用的原版公开skills | 各skill的SKILL.md和SOURCE_MANIFEST.json |
| with-CogniLife-skills/ | 最终采用的进化版 | CONDITION.json逐项记录采用哪轮 |
| evolution-history/ | 全部历史候选, 包括未采用版本 | 每版SKILL.md、EVOLUTION_RECORD.json和可核对的parent diff |

三组配置都在这里. 进化历史保留早期候选和后续各轮候选, 不把旧模型或失败版改名当成最新版. VERSION_INDEX.json列出各版模型、hash和是否采用.

原版非SKILL.md脚本、模板和资源不复制进本repo. SOURCE_MANIFEST.json记录它们在固定公开版本中的来源和hash. 运行时应从该来源取得, 再用进化版SKILL.md覆盖同名文件. 这里不是独立打包好的第三方运行环境.

## 怎么进化

1. Profy的gpt-6.1-sol先完成开发题, 留下真实user/assistant/tool执行记录、得分和tokens.
2. 收到的Profy原代码组装Evolution context、workflow、run_stats和工具. OpenRouter模型通过skill工具读取原skills, 再用evolution_log提出修改. 候选正文来自模型响应, 不是本聊天手写.
3. Profy实际读取候选并重新求解开发题, 用原评分检查. 后续轮次只把开发记录送回Evolution, 不把评测题答案补进去.
4. 开发测试全通过、tokens低于原版, 并再次确认后, 才冻结用于评测. 早期历史版的过程以各自记录为准, 不能把今天的完整适配流程套到旧版上.

第4至5轮新增了公开原skill的输出表示兼容保护, 已在provenance.adapter_contract中标明, 不冒充原方法. 原代码中仍缺少或未接通capability-gap classifier、通用语义适用性检查和native promotion, 不能称完整CogniLife平台复现.

每版EVOLUTION_RECORD.json保存实际模型、调用步骤、parent/candidate/request hash、开发记录数量、模型修改说明和实际得分. 只在能核对parent文件时提供diff, 不补造缺失历史.
