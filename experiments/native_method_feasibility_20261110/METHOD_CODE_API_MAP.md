# 原方法、已有代码和API逐项核对

核对日期: 2026-11-10, America/Los_Angeles. 当前状态: 完成静态和免费检查, 未做新的模型实验.

依据: 工作区的 naacl 2027 提交版.pdf, 第4页§3.4和第11页Appendix F. 文件SHA256为dce538935e9c911415b305f62e9413626f0fd82ecf28504af78b451a6ecf4819. 下面把收到的Profy-main代码、当前公开文档和本次实际接口响应分开说, 不把任何一层替代另一层.

## 结论

原Evolution的核心说明和门控有现成代码. 原论文完整链路在收到的版本里没有对齐, 当前公开API也没有证明可以把它跑起来. 因此现在不能再把一次普通agents/run加上自写prompt叫作原方法小跑.

## 按原方法逐项看

下表的实现路径都相对收到的04_项目数据与代码/Profy-main. 这些文件不复制进本助手的代码仓库.

| 原方法要求 | 已获得实现 | 能直接用什么 | 尚缺什么 / 本轮边界 |
| --- | --- | --- | --- |
| 从真实执行取得经验, 不能凭空改skill | services/agent-runtime/src/models/evolution.py的EvolutionRunStats; src/api/agent.py的_format_run_stats; 过去Profy API运行的原生工具记录 | 原始工具调用/结果和实际usage可作证据; 原run_stats字段、长度上限和渲染函数可复用 | 上一次只给writer公开题面和汇总数值, 不等于已有轨迹接线. 需要把开发运行的实际轨迹传给原生Evolution, 不能传gold或隐藏测试答案 |
| 只把expert-capability gap当成技能改进对象 | 提交稿§3.4有这项说明 | 需求边界明确: 任务指令问题、环境问题不能拿来改技能 | 在收到的Evolution prompt、工具和相邻路径中没找到与这项说明对应的明确分类实现. 不能断言线上没有, 但需要对应版本/文件, 不能由本助手补一段分类prompt就称复现 |
| 读取已有expert/*技能再改 | plugins/builtin/evolution/skills/evolution/SKILL.md的discover→read→trajectory→rewrite流程; plugins/builtin/skill/tools/skill.py的作用域筛选 | 原流程全文和expert作用域检查都有 | 工作区ZIP不自动成为平台expert/*库记录. 必须看到原生发现/激活结果中正确的expert技能和版本 |
| 原生Evolution生成建议 | plugins/builtin/evolution/prompts/EVOLUTION.md; plugins/builtin/evolution/plugin.json; src/api/agent.py:evolution_endpoint | 原prompt和原工具边界可以原样复用, 不需要另写候选生成规则 | 收到的入口是POST /api/agent/evolution, X-Internal-Secret鉴权, is_internal_invoke固定true. 本次不调用、不索要内部secret, 不伪造内部身份 |
| quality-group不下降、efficiency-group严格增加 | plugins/builtin/evolution/tools/evolution_log.py | 7个质量维度、3个效率维度、权重、校验与双条件门控可直接执行 | 大多数维度仍是模型估计, 不能当实测收益; 不能换成pytest+字节数后仍沿用原方法名称 |
| context_footprint由代码算 | 同文件_context_footprint_score及_fetch_current_skill_chars | 原字符计分函数和3000/24000字符阈值可直接用 | 不使用UTF-8字节替代. 上一轮517→1105字符在原函数下均为100分, 所谓7.2%字节减少没有对应到这个指标提升 |
| 每次最多一条建议, 不直接改活动skill | 原EVOLUTION.md、evolution_log工具和Core pending记录 | 原单条提交、目标校验、结构和source字段可用 | 需要原生pending建议id、候选全文与父版本, 不能用本地candidate_SKILL.md冒充平台pending记录 |
| 候选比较与授权promotion分开 | 提交稿第11页有paired reward、target、authority和版本检查说明 | 论文给出了应验收的链路 | 收到的services/core/src/db/service/expert-evolution.ts采纳路径直接更新skillMdContent. 没找到稿中那套分离的paired-reward promotion实现. 这是收到版本的缺口, 不能把旧accept当新promotion |
| 采纳方必须有权改对应技能 | 上述Core service的creatorUserId检查 | 现有owner校验可复用作边界证据 | 不能由一个调用者key推定它拥有空白expert的作者权限. 本次管理路由404, 未到权限检查阶段 |
| 版本恢复和冻结对照 | 论文有版本/恢复说明; 普通session隔离已经真实运行过 | API文件传输、session隔离、hash核对可复用 | 文件隔离不等于库版本隔离. 需要实际版本接口或三份独立测试expert, 避免一组更新改变另外两组的库 |
| Memory、Dream与Scoped maintenance | memory_dream.py、temporal_dream.py、background_review.py及相关Core服务 | 有实现材料可核对 | 这些不是skill进化的同一个开关. 本轮新实验不靠未验证的Memory写入/清空接口, 也不宣称验证Memory机制 |
| Cross-Expert Attribution / Creator Profile / Expert Journal | 提交稿把跨expert部分写成proposed design | 可以明确研究目标和需要的数据结构 | 在收到材料里未找到完整的作者归属、适用范围和路由处理实现. 六个expert快照和受控对话清单不能替代它; 本轮不把新实验说成填上跨expert归因缺口 |

## API能做什么: 文档和实测分开

| 能力 | 文档 / 源码依据 | 本次证据 | 判断 |
| --- | --- | --- | --- |
| 调用模型、传文件、开分开的会话 | [调用专家](https://docs.profy.cn/zh/developers/api/agents-run.md)、[上传文件](https://docs.profy.cn/zh/developers/api/files.md)、[会话](https://docs.profy.cn/zh/developers/api/sessions.md) | 上轮6次实际Profy任务完成; 本次GET /v1/models为200, 返回274条模型记录 | 求解任务这一半能复用. 本次没有重新调用模型 |
| API创建/维护草稿expert | [管理专家](https://docs.profy.cn/zh/developers/api/agents.md)和[OpenAPI](https://docs.profy.cn/openapi.json)有GET/POST/PATCH /v1/agents | 同key GET /v1/agents为404; POST空对象也为404, 不是文档所述缺name的400. 未创建任何expert | 文档和当前base URL的响应没有对上. 不能判定是未部署、路由差异还是访问隐藏, 也不能说只是key失效 |
| 在普通调用中选evolution扩展 | [调用专家](https://docs.profy.cn/zh/developers/api/agents-run.md)把evolution列为tools类型 | 文档确认有此参数, 本次未付费试调用 | 枚举存在不等于可以启动内部独占Evolution模式 |
| 启动论文所述原生Evolution | [自进化系统](https://docs.profy.cn/zh/documentation/how-it-works/darwin-evolution.md)、[专家进化](https://docs.profy.cn/zh/creators/darwin-evolution.md)和收到的入口/manifest一致写为内部模式 | 原registry函数离线检查: 普通调用即使显式选择插件也不激活; 内部模式才激活 | 未找到已验证的公开触发入口. 不拿普通聊天仿冒这一步 |
| 读取与接受已生成建议 | [MCP Tools](https://docs.profy.cn/zh/developers/reference/mcp-tools.md)有list_evolution_suggestions、accept_evolution、get_evolution_stats | [MCP Server](https://docs.profy.cn/zh/developers/mcp-server.md)说明使用浏览器登录态. 本次没有可用的已认证Profy MCP连接 | 是另一种接入, 不能把API Key自动当成MCP登录. 这些工具也没有列出“现在启动一次Evolution” |
| 安装目标技能 | 同一MCP Tools页明确install_skill是stub | 已读具体已知缺陷, 没去调用它 | 不把工具名当作已实现的安装能力 |

免费接口检查只读取列表, 以及提交一个缺name的空管理请求. 没调用agents/run、chat/completions、test_expert或内部路径. 没发布、采纳或修改专家. 证据见free_api_read_checks.json和free_agent_route_validation.json.

## 其他已有代码能不能省事

| 材料 | 实际可复用部分 | 不能当成什么 |
| --- | --- | --- |
| 本助手的three_arm_skill_pilot_20261110 | key读取、文件上传、SSE留存、原生read/hash核对、独立session、数值汇总 | 候选prompt和自写门控不能继续用作论文方法; 当前传输/评分入口偏JSON, 新文件型任务还需接线 |
| 收到的cognilife/scripts/run_queue.py和configs/render.py | 有静态条件渲染和任务调度材料 | 它走Codex CLI/TokenHub, 不是原生Evolution、Profy adapter或作者归属算法 |
| cognilife_1024_study_runner | 有目录、hash、排程和结果登记逻辑 | README已说明缺研究算法和Profy adapter. 不恢复10/24旧规模或把1224行计划当成完成 |
| Profy-main的SEA-Eval runbook | 记录了原生链路曾怎么桥接, 以及真实的开销问题 | 关键runner/profy_evolve.py、runner/profy_agent.py在别人的外部工作区, 本次包里没有. 文档不是已收到的runner, 也不授予使用其测试库和内部鉴权的权限 |
| profy-bench | 已有任务、附件、技能和原grader; customs还需缺失的private submodule | fin-eq属于synthetic、unlisted pilot, 不能说成正式公开任务集. Hehua-Fan/profy-bench本次连接返回404, 没核实公开可下载性. 不用这些假设启动新的headline实验 |
| SkillsBench本地副本 | 公开原题、原附件与原verifier都在. 四个候选文件型任务的入参齐全 | 不能说Profy adapter的结果等同于官方原生harness排行榜. 需要固定task版本、必要依赖、真实输出路径及原verifier |

## 已经做完的原函数小检查

check_original_gate.py直接读取收到的evolution_log.py函数体, 去掉框架decorator, 将远程写库改成内存fixture记录. 没改rubric、权重、计分曲线或接受条件. 另直接调用原registry的激活判断函数.

实际10/10通过, 新模型调用0次. 包括质量下降拒绝、效率不升拒绝、维度缺失拒绝、错误作用域拒绝、伪报context_footprint无效、普通模式不能激活原生Evolution. 这证明这些源码组件可复用, 不代表已完成真实专家、真实候选或论文效果实验.
