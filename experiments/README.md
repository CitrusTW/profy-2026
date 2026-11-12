# 找代码

| 目录 | 用途 | 当前怎么用 |
| --- | --- | --- |
| skillsbench_evolution_20261110/ | 收到的Evolution代码的外部适配、候选检查、记录和评分工具 | 当前开发位置; 按云端、串行要求继续修整 |
| native_method_feasibility_20261110/ | 原方法、收到的代码和API对照 | 查方法边界, 不当执行结果 |
| three_arm_pilot_20261110/ | 更早的三组原型和PersonaMem探索 | 历史代码, 不是当前CogniLife方法效果证据 |

skillsbench_evolution_20261110里的profy_cloud_probe.py已实际检查云端工具; native_evolution.py调用收到的原Evolution组件. export_skill_archive.py归档各版skills与来源.

旧脚本中的本地Docker构建和ThreadPool入口不再是当前运行入口. 当前要求全部串行、只使用已有云端API、不在本机搭全库环境. 云端完整评分入口尚在验证, 不提供一个未经验证的“一键跑全库”承诺.

运行需要已有Profy key、expert identifier和OpenRouter key. 只通过工作区外的密钥文件读取, 不把key值放进repo、命令参数、报告或聊天.
