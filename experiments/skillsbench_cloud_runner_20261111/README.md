# 用原题的云端环境做实验

这份代码把 SkillsBench 原题给的 Dockerfile 放到 Profy 云端运行. 电脑只发 API 请求和保存小结果, 不在本机搭 Docker 环境.

## 现在到哪一步

已在 Profy 云端成功运行固定 SHA256 的公开 Alpine image. 原题 Dockerfile 和完整三组还需要逐题验证. 当前代码是小范围原型, 不把它写成已经跑完87题.

先验证 weighted-gdp-calc: 给一份已有的 gdp.xlsx 填入查找、统计和加权平均公式, 还要保留原格式. 不重新出题, 分数由这道题自带的 test.sh 和 test_outputs.py 给出.

这道题只用一个 xlsx skill, 也就是处理 Excel 文件的操作说明. 同一版本的说明还出现在另外10道公开题里. 先用它调说明, 固定版本后再换题, 才能检查学到的办法能不能用到新任务上. 另外两份内容不同的 xlsx 说明不会直接套用这个版本.

## 每一步做什么

1. 从固定的公开版本读取原题材料, 核对 Git blob, 保留原文件内容和 Git 文件权限.
2. 给每组开新 Profy session. 云端从官方 Debian 软件包取得运行工具, 只解包到本次目录, 不运行系统安装脚本. 用原 Dockerfile 搭题目环境.
3. no-skills 不提供 benchmark skill 正文或资源. with-skills 提供原版. with-CogniLife-skills 必须明确提供新版本, 缺了就停止, 不回退成原版.
4. 模型在原题容器里做题. 实际读到的 skill 正文、工具调用、tokens 和产出都留记录.
5. 模型做完后, 才在单独的评分请求中提供原 verifier. 固定程序先导出实际文件, 再在同一题目容器里运行原 test.sh. 评分请求不再做题, 原测试内容不进入 skill 进化记录.
6. 保存实际文件、原得分、检查通过数、hash 和环境记录, 清理本次云端目录. 如果软件环境或评分没跑通, 单独记错误, 不当成模型答错.

## 文件入口

| 文件 | 做什么 |
| --- | --- |
| study.py | 电脑端发请求、核对来源、接结果 |
| remote_setup.py | 只在 Profy 云端搭原题环境 |
| remote_tools.py | 让模型在题目容器里执行命令, 需要时导出预览 |
| remote_grade.py | 做完题后跑原评分, 保存实际文件并清理 |
| test_study.py | 不用 key 的代码检查 |

key 从 repo 外读取. 进化继续复用上一目录 native_evolution.py 中收到的 Evolution 组件, 用 OpenRouter 的 gpt-6.1-sol. 这些执行脚本不编写或替代进化 prompt. 原方法缺少或未接通的实现继续在版本记录里列明.

hash 是按文件内容计算的指纹, 用来核对传过去和评分用的是不是同一份文件. 开发题是用来调整说明的题; 同一道开发题再成功一次也不算换题后的效果.
