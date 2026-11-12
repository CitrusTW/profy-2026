# 在 Profy 云端跑 SkillsBench 原题

电脑只发 API 请求和保存小结果. 不在本机下载 Docker image、搭题目环境或留大缓存.

## 当前实际进度

正在验证 weighted-gdp-calc: 给已有的 gdp.xlsx 填入查找公式和加权平均公式, 保留原格式. no-skills 已完成求解阶段, 正在等待原题评分. 这不是三组已完成, 更不是87题已完成.

当前使用 Profy 的 Debian 环境, 安装 Gnumeric、LibreOffice Calc 和 PRoot, 新增约363MB云端空间. PRoot 把原题的 /root 路径对应到本次自己的文件夹. 原始 Excel 文件的指纹和实际路径已核对. 这与官方 Ubuntu Docker image 有差别, 在每题的运行记录中明确保存; 三组使用同一套软件版本.

之前尝试官方 image 时, 虽然镜像文件下载完成, 但 Profy 文件系统里的解压超时. 所以当前先验证上面的轻量方式. 南京大学的公开缓存只在下载检查中使用, 不参与研究, 也不接收 key、题目附件或实验结果. 下载说明: https://doc.nju.edu.cn/books/e1654/page/ghcr .

## 三组怎么比

1. no-skills: 提供原题和原附件, 不提供 benchmark skill, 禁止读取其他 skill.
2. with-skills: 同样的题和附件, 加原版 SKILL.md 和它原有的资源.
3. with-CogniLife-skills: 同样的题和附件, 只把选定的 SKILL.md 换成通过原 Evolution 组件产生的新版本. 缺新版本就停止, 不回退成原版.

求解都用 Profy 的 gpt-6.1-sol. 做完后才提供原 verifier, 固定程序先保留实际回答文件, 再运行原 test.sh. 不改评分规则, 不把评分请求的历史或隐藏答案送进 Evolution. 软件或传输失败单独记录, 不记成答错.

## 新 skill 怎么来

`evolve_case.py` 读取已经完成的开发题求解记录, 调用收到的原 ContextManager、Evolution workflow、skill 工具和 evolution_log gate. 进化用现有 OpenRouter key, model 是 openai/gpt-6.1-sol. 这里没有另写学习 prompt 来顶替原组件.

接续已记录的第1至9轮, 只允许第10至30轮. 每轮保留父版本、完整新 SKILL.md、来源、实际求解和分数. 退回原版、原样返回父版本、名字或格式不对的候选, 不再付费验证.

原 gate 的建议分数不是实验成绩. 外部实验另检查实际质量和效率: 开发题全部通过, 再确认一次; 如果原版已全部通过, 两次都需要比原版少至少5%总 tokens 才固定版本. 5%只是这轮的选择规则, 不代表统计显著. 需要到未参与进化的题上再看是否有效.

原代码里缺少或没接通的 native 能力继续记录在 provenance 和 FROZEN.json 中, 不声称完整复现整个 Profy 平台. 当前新的第10轮还没开始.

## 换题之前核对什么

11题的 xlsx/SKILL.md 完全相同, 其中10题的全部配套资源也相同. exceltable-in-ppt 的 recalc.py 不同, 需要保留这个区别. 当前轻量程序只开放已经检查过的 weighted-gdp-calc, 其他题还没验证运行, 不把它们写成已经可跑.

87题里有84题找到源文件完全相同的官方 image 标签, 这只是来源清单, 不是运行成绩. 其余3题的环境版本不同, 暂不混用.

## 文件从哪里看

| 文件 | 做什么 |
| --- | --- |
| study.py | 发请求、核对材料、收实际回答和分数 |
| remote_setup.py | 选择本次的云端准备方式 |
| remote_native.py | 当前轻量方式的软件准备和文件路径对应 |
| remote_tools.py | 在准备好的环境里执行题目操作 |
| remote_grade.py | 冻结回答后跑原评分, 保留评分日志, 清理本次文件 |
| evolve_case.py | 一次做一轮开发题进化和检查 |
| candidate_check.py, run.py | 位于旁边的 skillsbench_evolution_20261110 目录, 复用原有检查和请求程序 |
| check_native_xlsx.py | 只查软件、空间或文件路径, 不做题、不评分 |
| prebuilt_catalog.py | 只核对公开 image 标签和 environment Git tree, 不下载 image |

进化在本机已有的小检查环境中调用 API, 只需要 Python3.12、PyYAML6.0.3 和 Pydantic2.12.3, 不装模型. 收到的 Profy 原实现继续从工作区读取, 按要求不复制别人的代码到这个 repo. key 从 repo 外读取, 不写进日志或文档.
