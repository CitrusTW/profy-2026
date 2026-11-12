# 找运行代码

| 从哪里开始 | 做什么 | 当前状态 |
| --- | --- | --- |
| [云端原题 runner](skillsbench_cloud_runner_20261111/README.md) | 在 Profy 云端用原 Dockerfile 做题、再用原评分检查 | 新的小范围原型, 正在验证, 还不是已完成的87题入口 |
| [原方法适配代码](skillsbench_evolution_20261110/) | native_evolution.py 调用收到的原 Evolution 组件; run.py 保留 Profy 请求和轨迹 | threejs、economic-dispatch、mesh-analysis 已有记录 |
| [原方法核对](native_method_feasibility_20261110/) | 论文方法、收到的代码、API 和缺口对照 | 查方法边界 |
| [早期三组原型](three_arm_pilot_20261110/) | 早期实验, 包括 PersonaMem | 历史尝试, 不当成当前方法效果证据 |

日常先看云端 runner 的 README. 原方法组件在 skillsbench_evolution_20261110/native_evolution.py, skills 归档在 export_skill_archive.py. 云端排错记录集中从 [环境检查](../results/2026-11-11_skillsbench_cloud_serial/environment-checks/README.md)查, 不需要逐个运行历史检查脚本.

本机旧的 Docker 批量构建、输入准备和评分入口已停用. 电脑只发请求、保存轻量代码与结果, 不搭全库环境或堆缓存. 全部串行, 不购买新服务. key 从 repo 外的文件读取.
