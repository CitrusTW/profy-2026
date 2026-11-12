# 需要审核者明确的 adapter 处理: tool_search

shock-analysis-supply 第1次no-skills的环境已成功返回CGL_CASE_READY. Solver完成后主动拒绝继续, 理由是原题Excel-only/Playwright MCP约束与它看到的环境不符. 它调用一次原生tool_search查询browser/spreadsheet, 未激活skill, 未观察到其他skill包读取. 现有study.py的grade()因为工具名不在read/bash/awaitbash/skills_read白名单而拒绝启动原verifier, 异常是Unexpected solver tool. 因此目前无评分, 不是已测reward0.

原始NIGHT_RECORD沿用旧通用异常处理写infrastructure_failure, 但这里混合了agent主动拒绝与adapter预评分检查, 尚不能确定是纯基础设施故障. 我不会据此跳过后面题, 也不会把unknown改0, 不改skill/题目/评分. 三组按顺序继续.

请通过后续编号指令决定: 是否统一允许原生tool_search这个纯发现调用通过adapter预评分检查, 在不重跑solver/不修改回答的前提下, 对这份现成轨迹补跑原verifier? 或保留为未评分的协议/环境受限记录? 本夜尚未改变该白名单. 官方任务环境Dockerfile本身使用Linux/LibreOffice, 所以我也不只根据solver的自述宣称任务环境绝对不可构建.

原始证据: skillsbench/runs/shock-analysis-supply/repeat-1/no-skills/. 原任务、输入、原verifier和24轮上限未变.
