# 第二个 adapter 问题: pip pin 检查误用发行包列表

reserves-at-risk-calc 第1次no-skills在setup阶段停止, 未答题、未评分. 原错误: AssertionError: Declared pip pin not active.

已用收到的现有记录和代码定位, 没有额外API调用: remote_native.py:111--115 用 importlib.metadata.distributions() 收集所有发行包, 排序后转成 {name: version}. 运行环境明确启用 --system-site-packages. 已保存的setup日志同时有pandas2.2.2/2.2.3、requests2.32.3/2.32.4; 所以字典保留排序靠后的版本, 不能证明实际import使用了哪个版本. 原题pin是pandas2.2.2和requests2.32.3. uv pip install已返回成功, 但实际active版本尚未独立查询.

建议的最小修复, 尚未应用: 保留全部distribution清单, 额外在同一task Python内用importlib.metadata.version(name)读取当前搜索路径实际优先的distribution, 保存其location, 再比较原pin. 不改pin、不加依赖、不改题、不改skill、不改24轮、不改verifier. 同一修复对三组一致, 旧失败日志保留.

请用新编号指令明确是否允许这个adapter检查修复, 及失败setup是否可在保留旧记录的前提下重新准备同一题. 当前仍按固定顺序继续, 不因某组表现换题, 也不将setup失败写成0分.
