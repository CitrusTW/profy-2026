# 最多30轮, 直到小范围改进确认

2026-11-10, America/Los_Angeles. 用户允许继续付费. 从已完成的3轮后接第4轮, 总上限30. 每轮独立留档并上传private repo, 不覆盖旧记录, 不改论文.

先纠正已有结果的解释: run-03第2份skill的官方1/3来自indexed/non-indexed表示与原verifier抽样的不兼容. 158份OBJ在原评分float32精度下三角形角点相同. 官方分数保留, 不能再把它直接说成几何错了两项. 详见INDEXING_DIAGNOSIS.md.

本阶段沿用收到的原EVOLUTION.md、workflow、skill工具、原门控、原run_stats模型与渲染. 新增的外部兼容约束有明确标签: 保留原公开threejs/SKILL.md中的non-indexed序列化语句和输出惯例; 告诉Evolution实际附带文件没有注册成native expert skill ID. 这是实验适配保护, 不是原作者已有实现, 也不是从gold提取规则.

每轮:
1. 原Evolution生成一份候选. 只看DEV历史和原公开skill约定. 不提供目标题输出、verifier、参考坐标或本次诊断的gold衍生数据.
2. 候选必须保留原序列化语句, 才花钱求解. 模型实际完成开发题后, 用原评分和独立输出表示检查验收. 没通过就留档后继续下一轮, 不改输出刷分.
3. 开发通过后, 对另一道既有公开题做adaptive check. 这道题已看过且用于循环决策, 明确属于调试/开发材料, 不是独立held-out证据. 结果不作为答案送进Evolution.
4. 两题原测试均全通过、输出约定均满足、reported tokens之和低于固定原版基线, 才再各跑一次确认. 确认仍满足同样条件, 算小范围进化完成并停止优化. 不只因模型自评分上涨就宣布成功.
5. 每轮保留STARTED、原生request/response/events、候选、hash、评分、成本及ROUND.json. 下一轮开始前做private repo checkpoint. 原prompt、第三方skill正文、输入、gold和keys按既有约束留工作区; repo存助手代码、每轮指标/索引与模型输出数据.

最多每轮4次求解, 每次15分钟/48工具/24模型回合, 每次Evolution最多8次模型请求. 30轮是上限, 不是必须烧完. 原始结果、诊断结果和兼容保护后的新运行分别记录.

小范围成功后的完整bench范围仍在询问: 当前这份threejs只配两题; 官方全库87题覆盖多领域. 全库三组是261次求解, 还需对应skills及通用执行/评分适配. 不会悄悄把一份threejs skill套在87题上, 也不把2题写成87题完成.
