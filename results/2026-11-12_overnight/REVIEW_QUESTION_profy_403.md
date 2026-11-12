# Profy agents/run连续403, 已暂停新请求

I003修复后reserves no-skills的stream结束但没有run.completed, 只见setup与awaitbash两次工具调用. 之后新session创建/文件上传仍成功, 但agents/run均HTTP403、0usage. 原客户端只保存HTTPError字符串, 这些403的原始响应body未保存, 不伪造补回.

已暂停新Profy请求. 只读查询已有session返回200/code0. GET agents/run被路由当作id=run返回404, 这不能证明额度原因. 对不完整setup session已发interrupt并获ack, 防止残留活动. 没有评分进程被杀, 没有充值或换key. 所以目前只能说执行接口拒绝, 不能断言余额耗尽.

请审核者明确后续诊断/恢复方向. 当前默认不重试新的付费请求、不改模型或身份来绕403. OpenRouter的ADVjudge继续, 原数据和全部失败记录保留. 如果确认为额度耗尽则按硬性规则停止, 不购买服务.
