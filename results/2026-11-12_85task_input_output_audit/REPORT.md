# 85 题生成输入和输出审计

审计日期: 2026-11-12. 本轮只读检查已保存材料, 没有新增模型调用, 没有修复、重新生成、重新打分或修改论文. 原始数据和脚本的 SHA-256 在审计前后完全一致.

## 先看结论

检查了 85 道题、三组共 255 份已保存回答. 三组都没有缺题、重复 task_id、空回答或非空 error 字段. 文本扫描没有发现技术报错、工具失败或未闭合代码围栏候选. **这不等于三组执行全部正常. 三组的原始生成请求和 finish_reason 都没有保存在本次审计的输出文件中, 因此不能证明实际输入完整, 也不能排除截断.**

Full 另有需要核实的输入差异: 文件中混合了平台调用标签和 proxy 标签. 收到的 proxy 生成分支会把本题 checkpoints 写进 system prompt; Raw 和 Expert Prompt 分支不会. 但是缺少逐次请求, 不能确认每条带 proxy 标签的回答实际用了哪个版本的输入. 不能把这段代码直接当作历史请求.

## 三组按同一标准得到的数量

每组分母都是 85. “已确认”只确认保存记录中的现象; “候选”只是文本检查; “无法核实”不是失败, 也不是通过. 同一题可以落在多个类别里, 各行不能相加当作总问题数.

| 检查项 | Raw | Expert Prompt | Full |
| --- | ---: | ---: | ---: |
| 已确认: 回答为空 | 0 | 0 | 0 |
| 已确认: error 字段报错 | 0 | 0 | 0 |
| 候选: 回答内技术报错 | 0 | 0 | 0 |
| 候选: 回答内工具失败 | 0 | 0 | 0 |
| 候选: 代码围栏未闭合 | 0 | 0 | 0 |
| 无法核实实际输入: 缺原始生成请求 | 85 | 85 | 85 |
| 无法核实输出截断: 缺 finish_reason | 85 | 85 | 85 |
| 无法核实是否触顶: 缺实际 max_tokens | 85 | 85 | 85 |
| 无法核实输出 token 数: 缺 completion_tokens | 0 | 0 | 20 |
| 平台调用缺逐次工具日志 | 0 | 0 | 20 |
| 记录标为 proxy, 本身不等于执行失败 | 0 | 0 | 65 |
| 记录标为平台调用, 未独立认证 | 0 | 0 | 20 |

Raw 和 Expert Prompt 的收到代码没有配置工具, 因而它们没有平台工具日志并不算工具执行问题. Full 的 65 条 proxy 标签对应的源码分支同样是普通 chat 调用. 工具日志检查主要涉及其余 20 条平台调用标签; 这些记录的 tool_calls 都为 null, 不是完整工具轨迹. 源码对 tool_end 直接标 completed, 不保留事件内结果详情, 所以不能据此排除工具失败.

所有非零类别的全部 task_id 已列在 [每组每类问题及全部task_id.csv](每组每类问题及全部task_id.csv). 三组各自的 85 道题都有独立记录, 见 [逐题完整性记录.jsonl](逐题完整性记录.jsonl). 不只抽样检查.

## 生成输入: 能确认什么, 不能确认什么

| 条件 | 收到代码如何组装输入 | 本次能确认的范围 | 实际调用仍缺什么证据 |
| --- | --- | --- | --- |
| Raw | 仅 task.input.prompt 作为 user message | 源题的 85 个 prompt 都非空; 源码不做字符串截断 | 原始 messages 和请求参数, 无法确认历史实际发送内容 |
| Expert Prompt | task_family 对应的通用角色模板 + 同一题 prompt | 五个 family 的模板均存在且非空; 源码不做字符串截断 | 原始 system/user messages 和请求参数 |
| Full, 65 条 proxy 标签 | 收到的 proxy 分支拼 expert 名、family 角色模板、本题 checkpoints 和通用作答要求 | 代码明确有 checkpoints 注入; 该分支没有独立 profile/journal 加载逻辑 | 每条记录是否实际用了这个分支、是否另有 workflow/profile/journal context、有没有截断, 均无法从输出文件确认 |
| Full, 20 条平台调用标签 | 收到的调用代码向平台传 expert identifier 和题目 prompt; 平台另行组装上下文 | 记录带 session_id、invoke_api 和 model 标签; 这些只是保存的元数据 | 平台实际发给模型的 expert metadata、workflow conventions、profile/journal context 以及截断策略 |

Full 的 expert metadata、workflow conventions、profile/journal context 三类实际输入, 每题都标为无法核实. 没有因为答案看起来详细就判定 context 齐全, 也没有因为输出文件没列某字段就断言平台没有注入.

profybench_v0.jsonl 的 task.input.context_slots 是结构化题目信息, 不是已经注入的专家记忆. 三条源码路径都没有把这个 dict 另行拼入请求; 一部分信息可能已写在 prompt 中. missing_fields 和 adversarial_element 还是题目设计注释, 不能把这些字段自动全塞给模型, 也不能把它们的存在当作执行缺失. 本轮没有修改输入.

## 生成输出: 截断和 token 上限

- Raw: model 标签 {"moonshot-v1-128k": 85}; 保存 completion_tokens 的记录 85 条, 范围 53–1028.
- Expert Prompt: model 标签 {"moonshot-v1-128k": 85}; 保存 completion_tokens 的记录 85 条, 范围 80–904.
- Full: model 标签 {"deepseek-v4-flash": 20, "moonshot-v1-128k_enhanced_proxy": 65}; 保存 completion_tokens 的记录 65 条, 范围 43–1023.

收到的普通 chat 生成函数设置 max_tokens=4096. 对保存了 completion_tokens 的记录, 没有一条达到 4096. **这只是与当前源码常量的比较, 不是对历史请求实际上限的核验.** 所有记录都缺少原始请求中的 max_tokens, 所有记录也都缺少 finish_reason. Full 的 20 条平台调用标签连 usage 也没有保存, 不能把这些未知值填成 0.

保存的 partial=true 计数均为 0, 但只有 Full 的 20 条平台调用标签保存了 partial=false; 其余记录根本没有 partial 字段. 所以这里也不能写成“255 条均已验证未截断”. 输出以完整标点结束或代码围栏闭合, 不能替代服务端结束原因.

文本检查对三组使用同一组规则, 查 Traceback、HTTP/API 错误、context_length_exceeded 等技术报错和工具失败字样. 没有匹配只表示没有发现这些字样, 不表示理解了全部运行过程或证明工具成功.

## 证据文件和边界

检查的源文件都在 `04_项目数据与代码/Profy-main/knowledge/benchmarks/profybench-v1/`:

- `profybench_v0.jsonl`: 85 道源题, 含 prompt、context_slots、family、variant、checkpoints 等.
- `results/outputs_generic_llm_raw.jsonl`: Raw 的 85 份回答.
- `results/outputs_generic_llm_expert_prompt.jsonl`: Expert Prompt 的 85 份回答.
- `results/outputs_profy_expert_full.jsonl`: Full 的 85 份回答及混合运行标签.
- `scripts/run_baselines.py:39–79`: baseline 输入拼装和生成返回字段.
- `scripts/run_full_pipeline.py:121–218`: 三组生成分支; 184、189 行直接使用 checkpoints; 77–94 行保存 usage 但不保存 finish_reason.
- `scripts/run_profy_invoke.py:59–172`: 平台消息和 SSE 收集; 123–125 行只保存工具完成标签; 255 行把 usage 固定写为 None.
- `scripts/llm_judge.py`: 仅用于明确本轮审计与生成、打分两条路径不同; 本轮没有执行它.

这些是本次逐项核对的材料范围. 没有冒充找到了历史原始生成请求、完整 API 返回或完整 SSE 流. 旧代码中的凭据没有使用, 也没有复制或上传. 所有模型名字都只是保存记录中的标签, 没有在本轮重新连接服务认证.

## 本文件夹与如何复查

- [audit_results.json](audit_results.json): 全部汇总数量、每类全部 task_id、源文件 hashes 和模型元数据.
- [每组每类问题及全部task_id.csv](每组每类问题及全部task_id.csv): 一行一个条件的一类检查, 可直接导入表格.
- [逐题完整性记录.jsonl](逐题完整性记录.jsonl): 255 行, 含回答 hash、长度、token 数、每项判定和未知项, 不重复复制完整回答.
- 审计脚本: `04_项目数据与代码/辅助代码/audit_85_input_output_20261112.py`. Git 中放在 `experiments/paper_judge_audit/audit_85_input_output_20261112.py`.

复查需要已收到的原始 benchmark 文件夹; Git 不复制公司源码、密钥或第三方代码. 使用 Python 标准库即可, 不需要 API key:

```sh
python3 audit_85_input_output_20261112.py --workspace '/包含04_项目数据与代码的项目根目录' --out '/新的审计输出目录'
```

本轮停在报告阶段. 不据此改原始回答、补 context、改 skill、重跑任务、继续 judge 或改论文, 等待确认.
