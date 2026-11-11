# 先把原方法接对, 再花钱

当前状态: 核对完成, 还不能启动原方法的端到端小跑. 本次新增模型调用0次. 已完成公开文档、收到的源码、已获得任务附件检查, 以及10项原函数离线检查. 没有修改论文或平台专家.

先看[METHOD_CODE_API_MAP.md](METHOD_CODE_API_MAP.md): 哪段原方法有代码、哪些能直接复用、哪些只是文档说有, 以及API实际返回什么.

再看[PILOT_PLAN.md](PILOT_PLAN.md): 只复用原Evolution实现的小跑与放大方案, 每一步的输入、输出、继续条件和停止条件.

现在的关键不是再写一个更好的prompt. 原prompt、原10维rubric和原门控已经收到. 缺的是当前版本对应的注册、触发、候选评估和promotion链路. 公开管理专家接口本次实测404; 原生Evolution入口在收到的代码和官方机制说明里是内部调用. 普通调用参数里出现evolution, 不代表它能启动同一模式.

不能用“把ZIP放进sandbox”替代“expert/*技能库里有正确版本”. sandbox隔离会话文件, 原生skill版本和候选则还存放在平台库里. 同一个expert id放到三个sandbox, 仍可能读到同一份已经更新的库内容. 新方案需要三份测试expert或实际可用的不可变版本控制.

## 这里保存什么

- check_original_gate.py: 本助手写的离线检查入口, 从仓库外读取收到的原函数. 不复制Profy源码, 不调用模型或内部服务.
- original_gate_offline_checks.json: 10项原函数检查的实际结果. 测试数据是fixture, 不是研究效果结果.
- free_api_read_checks.json: GET模型列表与专家列表的免费检查.
- free_agent_route_validation.json: 对公开管理专家接口发送缺少必填name的空请求, 未创建专家.
- source_manifest.json: 论文、实现文件、技能和任务的版本/hash索引. 不含源码全文、原附件、gold或key.

需要重做本地函数检查时:

```bash
python check_original_gate.py --workspace /path/to/CogniLife --output /path/to/local-checks.json
```

检查通过只说明收到的函数能按原规则运行, 不能证明线上版本相同、原生链路可调用或方法有效.

代码仓库只保存本助手写的检查入口、方案和不含原文的检查摘要. 收到的Profy代码、expert技能正文、公开benchmark源码和附件都留在仓库外. 不在Google Drive里提及或链接本仓库.
