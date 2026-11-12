# profy-2026

先看最新结果, 再看三组skills和进化过程. 这里保存实验代码与证据, 不代表论文已经采用这些结果.

| 想看什么 | 从哪里开始 |
| --- | --- |
| 最新结果, 做完了多少 | [当前状态](docs/STATUS.md) |
| no-skills / with-skills / with-CogniLife-skills | [三组skills](skills/README.md) |
| 每版怎么进化, 改了什么 | [全部版本目录](skills/evolution-history/)和[版本索引](skills/VERSION_INDEX.json) |
| 实际输出、得分和tokens | [结果入口](results/README.md) |
| 找运行代码 | [代码入口](experiments/README.md) |
| 查旧原型和失败记录 | [历史入口](archive/README.md) |

## 目前的实际结果

| 实验 | 原版skills | 进化版skills | 本次观察 |
| --- | --- | --- | --- |
| threejs两题 | 两题全通过, 237638 tokens | 两题全通过, 217326 tokens | 合计少8.55%; 分部件题反而多18.2% |
| 电价分析一题 | 4/4, 181580 tokens | 4/4, 98354 tokens | 少45.83% tokens, 正确性相同 |

threejs两题参与过调试. 电价分析题没有用于生成skill, 但与开发题使用同一公开电网文件、目标不同. 都不能据此宣称全库提升. 原方法仍有缺失实现, 详见各版记录. 论文和OpenReview未改.

新增: mesh-analysis第9轮在3D开发题两次2/2, tokens分别125369 / 127654, 相比原版161063少约22.16% / 20.74%. 已冻结, no-skills对照尚待补齐. 这里的2/2、4/4是单题原检查通过数, 不是题目数.

## 当前执行约定

- 只使用已授权的OpenRouter和Profy keys, 不额外购买服务.
- 全部串行, 不并行调用模型、agent或构建环境.
- 500GB家用电脑只留轻量代码、必要记录和常用小依赖. 不在本机堆Docker镜像、全库环境或大缓存.
- 正在迁移到Profy云端评分. 已接通3D题的独立云端评分, 全库环境和评分链路仍未全部验证; SkillsBench全库87题尚未完成.
- 每轮保存真实候选、原版出处、parent/request/candidate hash和实际结果. 不把自评分当实测分数, 不把评测答案送进进化.
- 不提交keys、收到的Profy公司源码、隐藏评分材料或无关第三方代码. 原版与派生SKILL.md按用户本次要求归档; 其他公开资源仅记录来源和hash.

旧路径保留, 以前的链接仍可用. 旧版本从历史入口查, 不再占据首页最新结果的位置.
