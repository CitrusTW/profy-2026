# 历史首页快照, 不代表最新状态

# profy-2026

## 最新: SkillsBench自带skills的三组小跑

[实际数字与结论](../experiments/skillsbench_evolution_20261110/RESULTS.md) · [计划](../experiments/skillsbench_evolution_20261110/PLAN.md) · [运行说明](../experiments/skillsbench_evolution_20261110/README.md)

2026-11-10: 已完成5次Profy求解和4次OpenRouter进化请求. 开发原题原版/候选均3/3; 新原题no-skills 1/3、原版skills 3/3、进化版1/3. 进化把开发题专用坐标旋转泛化到了新题, 原生输出和只读坐标诊断支持该解释. 当前版本不扩大, 不改论文或提交OpenReview.

本轮使用收到的原Evolution prompt、workflow、skill工具函数和ratchet的外部适配, 没用自写提取prompt. 不声称调用了Profy内部Evolution/promotion服务或完成完整CogniLife复现. 原skills、派生skill正文和第三方代码均未提交.


这里保存本助手写的实验代码、说明和数字摘要. 不放收到的Profy源码、expert包、benchmark源码、原附件、gold或密钥.

## 此前的原生链路核对

[原方法、已有代码和API核对](../experiments/native_method_feasibility_20261110/METHOD_CODE_API_MAP.md)和[接通原方法后的小跑计划](../experiments/native_method_feasibility_20261110/PILOT_PLAN.md).

2026-11-10状态: 原Evolution prompt、10维rubric和ratchet已收到, 原函数10项离线检查通过. 但当前原生运行入口、expert技能注册/隔离及提交稿对应的分类与promotion代码版本没有对齐. 本轮新增模型调用0次, 付费小跑尚未启动. 离线检查不是效果实验, 不标记为方法验证完成.

## 以前跑过什么

[修正版实际结果](../experiments/three_arm_pilot_20261110/RESULTS_V2.md): 三组交付JSON完全相同, 原整题strict都是0, 没有观察到本题得分提升. 项目skill的传入与读取已检查, 但它不构成对全部平台默认能力的排除.

[只读诊断](../experiments/three_arm_pilot_20261110/DIAGNOSIS_V2.md): 第三组是自写prompt生成候选、开发检查后替换skill的原型, 不是原论文的skill evolution实现. 诊断解释了相同输出、缺失的原方法步骤, 以及字节长度门槛与原context_footprint指标的差别. 没有修改原分数.

[原型运行说明](../experiments/three_arm_pilot_20261110/README.md)和[首版无效对照](../experiments/three_arm_pilot_20261110/RESULTS.md)保留归档. PersonaMem探索脚本在同目录archive/personamem, 不作为论文方法效果证据. 完整原文件、输出和日志留在仓库外.
