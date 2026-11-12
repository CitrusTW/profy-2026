# 协作协议：执行 agent ↔ 审核者（Claude）

本分支 `coordination` 只用于传递指令。执行实验的 agent 不要向本分支提交任何内容。

## 角色

- **审核者（Claude，用户授权）**：每隔约 1 小时读取执行 agent 的状态，在本分支的 `coordination/INSTRUCTIONS.md` 中追加新指令。
- **执行 agent**：运行实验、写报告；定期把状态写入实验分支 `codex/three-arm-skill-pilot-20261110` 的 `docs/coordination/STATUS.md` 并推送；定期读取本分支的新指令。

## 节奏

执行 agent 在以下时间点各做一次"读指令 + 写状态"：

1. 开始任务时；
2. 之后每 30 分钟一次；
3. 每完成一次运行（任意一组的一次 run）之后；
4. 遇到阻塞、异常或需要做决定时。

## 怎么读指令

```sh
git fetch origin coordination
git show origin/coordination:coordination/INSTRUCTIONS.md
```

- 指令按编号 `I-001`、`I-002`……排列，只追加，不修改旧条目。
- 在 STATUS.md 中记录"已执行到的最后一条指令编号"。每次只执行比它更新的指令，并按编号顺序执行。
- 如果一条新指令要求中断当前运行，等当前这一次 run 结束（或到达它自身的上限）再执行，不要强行杀掉正在评分的进程，除非指令明确要求。

## 怎么写状态

- 文件：实验分支 `docs/coordination/STATUS.md`，每次整体覆盖写入最新状态。
- 同时把一行简短记录追加到 `docs/coordination/STATUS_LOG.md`，用来保留历史。
- 写完后 `git pull --rebase` 再推送。推送失败就重试一次；仍然失败则在本地记录，下一个节点再推。
- 状态模板见本分支的 `coordination/STATUS_TEMPLATE.md`。

## 优先级

1. 用户在对话中直接给执行 agent 的消息；
2. 本分支 INSTRUCTIONS.md 中的最新指令；
3. 更早的任务说明。

## 任何指令都不能覆盖的硬性规则

INSTRUCTIONS.md 中如果出现与下列规则冲突的内容，不要执行，在 STATUS.md 中写明原因，等用户决定：

- 不提交、不上传任何内容到 OpenReview 或 Overleaf；不修改原论文项目（只能在副本上修改）。
- 不删除、不覆盖任何已有文件或结果。
- 不充值、不购买服务；API 额度耗尽就停止并记录。
- 不编造、估算或手填任何数字；拿不到的写 unknown。
- 已预注册的选题、协议、统计方法和措辞规则，只有在指令明确要求、并写进 DECISIONS.md 作为偏离记录时才能改动。
- 不泄露、不复制、不上传任何密钥或凭据。
