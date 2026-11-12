# 文件清单怎么用

[FILE_INVENTORY.csv](FILE_INVENTORY.csv)列出整理前提交 `dcb9b5c922664e90d77c98bf92eeb05388a6bbca` 中全部 results / skills / experiments 文件. 这是Git元数据清点, 没有重新运行实验或复制大文件.

- batch: 原来的顶层批次目录.
- navigation_category: 帮助查找的粗分类, 不代表该文件是有效科学结果; 原始attempt、失败和中途快照都保留.
- path: 从repo根目录开始的原路径.
- git_blob: Git对象ID, 不是原文件SHA256.
为避免稀疏克隆额外下载原文件, 本清单不读取文件大小或重新计算内容hash.

不把文件数当任务数, 不把多个统计快照当重复实验. 实验有效性以[总览](../EXPERIMENTS.md)和各批最终报告为准. 新增导航文档不算实验记录, 不列入本清单.
