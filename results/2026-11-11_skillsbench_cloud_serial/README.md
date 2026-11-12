# 串行云端结果

- [第7轮](mesh-evolution/round-07/ROUND.json): 原检查2/2, tokens只少约0.18%, 未采用.
- [第8轮](mesh-evolution/round-08/ROUND.json): SSL传输故障, 没收到候选; 不算方法效果失败.
- [第9轮](mesh-evolution/round-09/ROUND.json): 开发和确认均2/2, tokens为125369和127654, 已冻结.
- [冻结版本](mesh-evolution/FROZEN.json)与[完整SKILL.md](../../skills/with-CogniLife-skills/mesh-analysis/SKILL.md).

ROUND.json中的development.score与confirmation.score才是原评分程序的实际结果. cloud-grade/ACCEPTED_CLOUD_GRADING.json是对应的独立云端评分回执. cloud-grade/result.json记录的是API文件传输流程, 其中的transport-only标记或旧strict=0不表示任务得分为0.

开发题用来生成/选择版本, 评测题在生成版本时没有使用. 3D例子目前仍是开发题结果. 不把云端工具检查、环境准备或接口故障混算成已完成benchmark题数. 论文未改.
