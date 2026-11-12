# 每版 skill 怎么来的

想直接用当前版本, 去 [with-CogniLife-skills](../with-CogniLife-skills/). 这里保留采用和没采用的版本, 不覆盖旧记录.

## 当前采用

| skill | 版本 | 实际正文 | 怎么进化 |
| --- | --- | --- | --- |
| threejs | 第5轮 | [SKILL.md](round-05/SKILL.md) | [进化记录](round-05/EVOLUTION_RECORD.json) |
| economic-dispatch | 第6轮 | [SKILL.md](round-06/SKILL.md) | [进化记录](round-06/EVOLUTION_RECORD.json) |
| mesh-analysis | 第9轮 | [SKILL.md](round-09/SKILL.md) | [进化记录](round-09/EVOLUTION_RECORD.json) |

## 查全部尝试

| 目录 | 是什么 |
| --- | --- |
| [historical-run-01](historical-run-01/) | 早期 gpt-4.1 候选, 与后来的版本分开记录 |
| [historical-run-02-gpt61](historical-run-02-gpt61/) | 早期 gpt-6.1-sol 候选 |
| [round-01](round-01/)、[02](round-02/)、[03](round-03/) | threejs 前三轮 |
| [round-04](round-04/)、[05](round-05/) | threejs 后续调整, 第5轮采用 |
| [round-06](round-06/) | economic-dispatch 进化与确认 |
| [round-07](round-07/) | mesh-analysis 通过检查, 但 tokens 只少约0.18%, 没采用 |
| [round-08](round-08/) | SSL 传输错误, 没收到候选; 只有故障记录 |
| [round-09](round-09/) | mesh-analysis 开发和确认通过, 采用 |

共10份实际候选正文. 第8轮没有正文, 仍计入最多30轮. 两个 historical 目录是轮次循环之前的历史尝试, 不改名塞进后续编号.

## 每个文件看什么

- SKILL.md: 模型实际生成的完整操作说明.
- EVOLUTION_RECORD.json: 模型、上一版、请求和候选的 hash、工具调用、修改说明以及实际开发结果.
- changes_from_parent.diff: 有可核对上一版时, 显示具体改了哪些文字.
- [VERSION_INDEX.json](../VERSION_INDEX.json): 机器可读的版本清单.

公开原版见 [with-skills](../with-skills/). 进化用开发记录, 不把评测答案补进规则. 原方法缺少或未接通的实现继续保留在每版记录中, 不用一个自写 prompt 冒充完整方法.
