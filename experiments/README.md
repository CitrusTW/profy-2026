# 找运行代码

当前代码都在 [skillsbench_evolution_20261110](skillsbench_evolution_20261110/). 先按用途找文件, 不需要把每个脚本读一遍.

## 当前流程

| 步骤 | 代码 | 做什么 |
| --- | --- | --- |
| 生成候选 | [native_evolution.py](skillsbench_evolution_20261110/native_evolution.py) | 通过 OpenRouter 调用收到的 Evolution 组件, 用开发轨迹生成候选 |
| 运行求解 | [run.py](skillsbench_evolution_20261110/run.py) | Profy 调用、传输入、接输出、检查实际读了哪个 skill |
| 3D 小范围进化与确认 | [cloud_serial_3d.py](skillsbench_evolution_20261110/cloud_serial_3d.py) | 串行进化、求解、原评分和确认 |
| 3D 独立云端原评分 | [cloud_grade_3d.py](skillsbench_evolution_20261110/cloud_grade_3d.py) | 在独立会话对实际输出跑原测试; 测试不提供给求解或进化 |
| 归档三组和历史版本 | [export_skill_archive.py](skillsbench_evolution_20261110/export_skill_archive.py) | 导出 SKILL.md、来源、修改过程和实际指标 |

这些入口仍依赖本地收到的原方法组件和固定版本的公开 SkillsBench 资源. 本 repo 没有复制收到的 Profy 公司源码, 不是下载后就能独立跑全库的完整包.

## 旧原型与方法核对

| 目录 | 用途 |
| --- | --- |
| [native_method_feasibility_20261110](native_method_feasibility_20261110/) | 对照论文方法、收到的代码和 API, 查缺口 |
| [three_arm_pilot_20261110](three_arm_pilot_20261110/) | 早期三组原型与 PersonaMem 尝试, 不作为当前方法效果证据 |

旧的本地 Docker 构建入口不再使用. 全部串行, 不在本机搭全库环境或堆缓存. 目前只验证了部分题目的云端流程, 没有一个已验证的87题一键入口.

keys 只从 repo 外的文件读取; 不把值写进代码、命令参数、报告或聊天.
