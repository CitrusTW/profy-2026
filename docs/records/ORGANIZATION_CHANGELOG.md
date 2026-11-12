# 本次整理改了什么

基准提交: `dcb9b5c922664e90d77c98bf92eeb05388a6bbca`. 日期: 2026-11-12.

1. 更新首页、results入口、当前状态、skills和代码入口, 去掉把旧状态当作当前状态的说明.
2. 新增实验总览、11月12日批次说明、论文版本入口和全文件清单.
3. 区分ADV跨模型、同模型、旧分数审计、初批截断、最终统计; 保留I010缺失一个pairwise顺序的事实.
4. 区分SkillsBench开发题、选版题、冻结新题、runner_limit和平台失败; 第11轮按skill解释, 不把全库目录名当全库结果.
5. 最新论文入口指向SixLessons PDF, 不覆盖较早final PDF, 不修改论文.
6. 改动前的已有入口说明保存在 archive/navigation-before-2026-11-12/ 对应原路径.

原始请求、返回、候选、hash、评分、统计JSON/CSV、PDF和失败记录均未改动或搬家. 没有新增模型调用, 没有向Drive/Overleaf/OpenReview写入. coordination分支不提交.

检查: 所有新增/更新导航的相对链接应指向本分支真实存在的文件或目录; 实验文件的Git对象ID在整理前后应一致. 检查结果见 NAVIGATION_CHECK.json.
