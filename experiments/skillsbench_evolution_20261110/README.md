# SkillsBench原skills的三组小验证

先看[实际数字与结论](RESULTS.md): 小跑已完成, 原版skills通过3/3, 进化版1/3, 当前不扩大. 计划见[PLAN.md](PLAN.md). 这次不使用6个expert包, 只用SkillsBench原题、原附件和配套skills. 三组是no-skills、with-skills、with-CogniLife-skills.

开发题threejs-to-obj要求导出整个3D物体. 验证题threejs-structure-parser要求把另一份3D物体按部件分别导出. 两题都带同一份threejs/SKILL.md, 可以用开发经历进化它, 再检查新任务. 验证题其他原skills及资源在后两组完全相同.

native_evolution.py在仓库外读取收到的Profy原EVOLUTION.md、原workflow、原skill工具函数和原evolution_log.py. 不另写提取prompt, 不改原门控. 新代码只适配技能文件读取、模型工具调用与实验内pending保存. 这是skill-refinement核心的外部适配, 不声称运行了Profy内部服务、完整CogniLife归因/Memory或平台promotion.

## 怎么启动

需要已有CogniLife工作区中的SkillsBench和收到的Profy-main源码, 私下保存的Profy/OpenRouter keys及Profy identifier, Python 3.12、Node/npm, 以及原pytest/numpy评分依赖. Profy hosted求解, OpenRouter执行Evolution, 本机只调度、下载原生交付文件和程序评分. 不需要本地大模型或GPU.

从CogniLife工作区执行, 把绝对路径填到下列参数中. key只填写文件位置, 不把值放进命令. 各phase分别执行; 失败后先看记录, 不自动重发付费attempt.

```bash
python /path/to/skillsbench_evolution_20261110/run.py setup --workspace /path/to/CogniLife --out /path/to/new-run --keys-file /path/to/private-keys.md
python /path/to/skillsbench_evolution_20261110/run.py dev --workspace /path/to/CogniLife --out /path/to/new-run --keys-file /path/to/private-keys.md
python /path/to/skillsbench_evolution_20261110/run.py evolve --workspace /path/to/CogniLife --out /path/to/new-run --keys-file /path/to/private-keys.md
python /path/to/skillsbench_evolution_20261110/run.py candidate --workspace /path/to/CogniLife --out /path/to/new-run --keys-file /path/to/private-keys.md
python /path/to/skillsbench_evolution_20261110/run.py test --workspace /path/to/CogniLife --out /path/to/new-run --keys-file /path/to/private-keys.md
python /path/to/skillsbench_evolution_20261110/run.py report --workspace /path/to/CogniLife --out /path/to/new-run --keys-file /path/to/private-keys.md
```

- setup仅准备原评分程序所需的Three.js版本和原reference generator. 不调用模型, 参考生成器从不上传.
- dev一次开发求解; evolve最多8次模型工具调用, 原门控可拒绝或无建议结束.
- 有候选才执行candidate. 原门控通过、开发分数不降、实际skill版本读取通过, 才执行test.
- test在新任务上三组各1次. 最多5次Profy求解, 每次15分钟/48工具/24模型回合. 不自动全量.
- 每个attempt目录的started.json防止重复付费; events.jsonl、usage.json、原生deliverables.zip、实际输出和原评分receipt留在仓库外的结果目录. 文件下载后核对原生ZIP和逐文件SHA256, 不在本地补写答案.

原verifier和reference generator只绑定/root路径到隔离目录. 不改评分断言、容差或预期值. 成功需要真实交付文件、原verifier通过且没有skip; 原门控分高不等于任务做对.

## 仓库里是什么

这里只保存本助手写的适配代码、计划、测试和数字摘要. 不保存第三方skill/脚本/原verifier、公开原附件、派生skill全文、gold或keys. 这些实验依赖留在工作区和证据目录. Google Drive分享材料不提及或链接这个private repo.

本地适配检查:

```bash
python /path/to/skillsbench_evolution_20261110/test_adapter.py
```

检查原skill读取、原门控质量回退拒绝、代码footprint、原生文件字节保留和ZIP路径边界. 这不是效果分数, 最终看实际三组原verifier结果.
