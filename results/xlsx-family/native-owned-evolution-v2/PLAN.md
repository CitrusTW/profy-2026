# 继续修 xlsx skill: 第12到30轮

目标不是只让一张开发表格更省 tokens. 新版还要能在另一道现成题上保持正确, 同时少走弯路. 不改题、不重新写 benchmark, 不改论文.

## 怎么做

1. 只用 weighted-gdp-calc 的完整求解记录进化. 先补齐当前 native-owned 环境的原版和第11版开发记录, 避免把旧 PRoot 环境的问题当成通用规则.
2. 继续调用收到的原始 Evolution prompt、workflow、skill tools 和 evolution_log gate. Evolution 用现有 OpenRouter key 的 openai/gpt-6.1-sol. 不手写一个新提取 prompt 冒充原方法. 新增 contract 只纠正实际执行环境的说明.
3. 第12轮开始生成候选. 每版完整 SKILL.md、parent diff、模型回复、原组件来源指纹、结果与未采用原因都保留.
4. Profy gpt-6.1-sol 跑开发题, 原评分全过且比原版至少少5% solver total_tokens, 再用同一候选确认一次.
5. 开发检查通过后, 跑 protein-expression-analysis 选版验证. 两次均原评分全过、比原版至少少5% tokens, 才采用. 只要没有通过, 继续下一轮, 最多到全局第30轮. 不把验证题答案、轨迹、gold、评分源码或验证分数发给 Evolution.
6. 采用后冻结 skill, 再测尚未运行的题. 不根据这些题的答案回改本轮 skill.

## 哪些结果可以证明什么

protein-expression-analysis 之前的第一轮确实是在冻结第11版后首次测试. 现在开始参与选版, 后续结果只能叫 validation, 不再当作独立的新题证据. 保留之前的失败结果和原来记录, 不改写历史.

尚未运行的 shock-analysis-supply、reserves-at-risk-calc、powerlifting-coef-calc、xlsx-recover-data、invoice-fraud-detection、pdf-excel-diff、jpg-ocr-stat 留作冻结后的测试. shock-analysis-demand 已经部分运行, 另行标记, 不冒充全新题.

上述5%门槛和validation选版是新增的外部实验保护, 不是声称原论文已有的组件. 收到的代码缺少或未接通 capability-gap classifier、通用 semantic applicability check 和 native acceptance/promotion, 仍明确记录. 本实验不能冒充完整平台复现.

三组都通过原评分而tokens更少, 才是效率改善; 不把tokens当美元费用. 没达到条件就保留不理想的结果, 不把低分隐藏起来.

全部串行, 只用现有 API, 不充值、不购买服务、不动银行卡. 本机只留小代码、skill和必要证据, 不保存镜像或大环境. 每轮上传private Git; 不改论文、Overleaf、OpenReview.
