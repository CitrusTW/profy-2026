# 每版skill怎么来的

当前新题评测按skill分别冻结, 不存在适用所有任务的“统一第11版”.

| skill | 使用版本 | 实际正文 | 过程与证据 |
| --- | --- | --- | --- |
| threejs | 第5轮, 仅历史开发题两题比较 | [SKILL.md](round-05/SKILL.md) | [EVOLUTION_RECORD.json](round-05/EVOLUTION_RECORD.json) |
| economic-dispatch | 第6轮, energy-market-pricing | [SKILL.md](round-06/SKILL.md) | [EVOLUTION_RECORD.json](round-06/EVOLUTION_RECORD.json) |
| mesh-analysis | 第9轮, 3d-scan-calc开发题 | [SKILL.md](round-09/SKILL.md) | [EVOLUTION_RECORD.json](round-09/EVOLUTION_RECORD.json) |
| xlsx | 第11轮, 本批冻结新题 | [SKILL.md](xlsx/round-11/SKILL.md) | [开发与确认](../../results/xlsx-family/round-11/ROUND.json)、[本批实际冻结文件](../../results/2026-11-12_overnight/skills/frozen_xlsx_round11_SKILL.md) |

## 全部候选和失败

| 范围 | 做过什么 |
| --- | --- |
| [historical-run-01](historical-run-01/)、[historical-run-02-gpt61](historical-run-02-gpt61/) | 循环编号前的两次候选; 前者是gpt-4.1, 不能改写成gpt-6.1-sol |
| [round-01](round-01/) 至 [round-05](round-05/) | threejs早期迭代, 第5轮采用 |
| [round-06](round-06/) | economic-dispatch |
| [round-07](round-07/) | mesh-analysis候选, 未采用 |
| [round-08](round-08/) | SSL失败, 没收到候选, 不补造正文 |
| [round-09](round-09/) | mesh-analysis开发与确认 |
| [xlsx/round-10](xlsx/round-10/) | 开发题检查通过但tokens更高, 未采用 |
| [xlsx/round-11](xlsx/round-11/) | 开发与确认后冻结, 本批使用 |
| [xlsx/round-12](xlsx/round-12/)、[round-13](xlsx/round-13/) | 后续native-owned适配/候选选择记录; 不是本批冻结评测版本 |

SKILL.md是实际候选正文; EVOLUTION_RECORD.json或ROUND.json记录来源、模型、hash和执行结果; changes_from_parent.diff只在有可核对parent时提供. 不用“门控通过”代替原verifier执行结果.

[VERSION_INDEX.json](../VERSION_INDEX.json)是先前建立的机器索引, 未覆盖后来全部xlsx轮次; 查这些轮次用本页明确入口. 本次不重写历史JSON. 所有旧结果和失败保留, [最终实验归类](../../docs/EXPERIMENTS.md).
