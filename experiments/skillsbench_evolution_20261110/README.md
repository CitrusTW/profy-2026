# SkillsBench skill evolution 小验证

最新进度: 第5轮小范围两题均3/3并再次确认, 执行tokens合计两次分别降低约9.7%和1.6%. 已冻结, 正跑2道配套题的完整三组, 并非87题全库. 看[逐轮进度](../../results/run-04-up-to30/PROGRESS.md)与[小范围记录](../../results/run-04-up-to30/SMALL_SCOPE_REPORT.md). 若完整对照未保住质量/成本, 会在总计30轮上限内继续.

**结果解释纠正:** [INDEXING_DIAGNOSIS.md](INDEXING_DIAGNOSIS.md)已定位run-03第2份skill的官方1/3原因: 保留索引改变顶点重复方式, 原verifier只抽v列表且不读f索引, 对等价OBJ表示敏感. 158份输出在原评分float32精度下按f展开的三角形角点全部匹配. 官方分数不改, 但不能再直接称为几何质量退步. 本轮只作离线诊断, 未付费重跑.

此前3轮结果见[ITERATIVE_RESULTS.md](ITERATIVE_RESULTS.md): 新增3份候选和1次最佳候选确认, 开发成本改善, 最后benchmark仍是原版3/3、进化版1/3. 不采用进化版, 不改论文. 新流程见[ITERATION_PLAN.md](ITERATION_PLAN.md); iterate.py仅用DEV历史选择, 18项离线测试通过.

此前文档核查见[DOC_REVIEW.md](DOC_REVIEW.md): 上一轮候选没有达到实测效率目标. 新增的开发tokens检查会阻止该候选继续进入付费验证, 11项离线测试通过. 这是新增实验检查, 不是修改Profy原评分门控. 未重跑模型或benchmark.

上一轮run-02结果(2026-11-10): 已获准付费小跑. gpt-6.1-sol已生成新skill并完成验证. 新skill开发题3/3, 验证题1/3; 原版验证3/3, 本轮没有收益, 不扩大. 看[实际数字](PAID_RESULTS.md)和[结果JSON](PAID_RESULTS.json). 本次计划见[PAID_RUN_PLAN.md](PAID_RUN_PLAN.md). 上一轮的[离线修复记录](OFFLINE_FIX_REPORT.md)和[检查数字](OFFLINE_FIX_FACTS.json)继续保留, 记录的是付费前状态.

旧小跑的数字保留在[RESULTS.md](RESULTS.md): 原版skills通过3/3, 旧进化版1/3. 旧候选由gpt-4.1生成, 不会被改名当成gpt-6.1-sol的结果. 修好代码不等于已经测出新skill有效.

## 这个程序做什么

用开发题threejs-to-obj的一次真实执行记录, 通过收到的Profy Evolution代码提出skill修改. 原任务是把3D物体导出成OBJ文件. 生成候选后, 可以先检查它是否仍能完成开发题. 程序不另写学习prompt, 不从6个expert包提取内容.

原验证题threejs-structure-parser已跑过并分析过失败原因. 它的旧结果只作为历史记录; 以后不能把针对该结果调过的skill在同一题上的成绩当作独立验证. 不改benchmark, 不拿它的答案补规则.

## 修到了哪里

- Evolution通过OpenRouter的openai/gpt-6.1-sol运行; 求解通过Profy的gpt-6.1-sol运行. 没有4.1备用路线. Profy plain chat带工具的请求实际返回provider错误, 用户明确允许改用OpenRouter, 才切换入口.
- 用原ContextManager组装静态context, 用原skill metadata parser和discovery输出. Evolution能发现开发题的threejs和obj-exporter, 但本实验只允许修改预先选好的threejs.
- 开发历史保留user、assistant、tool角色和完整工具参数/结果. 缺结果、重复调用或对不上的tool ID会停止, 不补造记录.
- 原EVOLUTION.md、evolution workflow、skill工具和evolution_log门控仍从收到的Profy-main读取. 原权重和接受条件不变.
- 候选核验检查实际请求模型、请求hash、原skill版本、候选与pending是否一致、开发执行是否完成、实际读取版本和原评分是否完整. 原门控收下建议, 不代表候选语义已经核验通过.

收到的代码中还没找到论文所说的capability-gap classifier, 也没找到自动检查经验适用条件的实现. 适配器没有接入native acceptance / promotion. 这三项会出现在检查结果中, 不用新prompt或本地pending冒充. 详见[方法对照审查](METHOD_FIDELITY_AUDIT.md), 其中旧行号和旧适配状态记录的是修复前版本.

## 环境和离线检查

需要CogniLife工作区里的SkillsBench与收到的Profy-main源码, Python 3.12、pydantic 2和PyYAML. 此机器可复用已安装的PyYAML; 换机器需要正常安装该依赖. 本地不运行大模型, 不需要GPU. 实际求解需要Profy key与expert identifier; 当前Evolution入口还需要OpenRouter key. 离线检查不读key.

```bash
python /path/to/skillsbench_evolution_20261110/test_adapter.py
python /path/to/skillsbench_evolution_20261110/run.py check --workspace /path/to/CogniLife --out /path/to/existing-run
```

check读取dev_original、dev_candidate和evolution的已有记录, 不读取key. 输出写到结果目录的adapter_fix_checks. prepared_request_local_only.json含原context和开发轨迹, 只留本地, 不提交代码仓库.

10项测试覆盖原context、历史配对、付费关闭、旧模型拦截、候选hash篡改、执行失败、原门控重放、输出字节与ZIP路径检查, 以及key脱敏. fixture只测试代码边界, 不算实验成绩.

## 将来实际运行时

付费phase默认关闭, 需要 `--allow-paid` 和 `--keys-file` 密钥文件位置. 本次小跑已获准, 不自动扩大. 不把key值写入命令. 每个新候选使用新结果目录; 不覆盖旧evolution或frozen.json.

顺序是setup、dev、evolve、candidate、test、report. setup只准备原评分依赖, 需要Node/npm及原pytest/numpy环境; dev跑开发题; evolve最多8次Profy模型请求; candidate跑候选的开发检查; test在核验通过后才运行三组. 当前这对题的验证结果已被看过, 本次明确标为diagnostic repeat, 不称独立held-out验证, 不自动启动全量批次.

原verifier和reference generator只绑定运行路径, 不改断言或容差, 不上传给模型. 输出通过原生ZIP传回并逐文件核对hash. 默认最多5次求解, 每次15分钟、48次工具调用、24个模型回合, 不自动重发.

Profy plain chat的极短纯文本请求成功, 带tools或max_tokens的极短请求返回502. 返回内容没有底层错误细节, 不据此断言所有Profy模型都不能调用工具. 本次Evolution改走已实际返回gpt-6.1-sol响应的OpenRouter入口, 三组求解继续走Profy agents/run. 接口诊断单列, 不当作benchmark成绩.

## 保存边界

代码仓库只保存本助手写的适配代码、说明、测试和数字摘要. 不保存第三方source、skills、派生skill全文、原附件、gold、模型原始请求或keys. Google Drive分享材料不提及或链接private repo.
