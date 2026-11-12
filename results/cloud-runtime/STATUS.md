# 云端运行进度, 不是 benchmark 得分

截至2026-11-11晚: 新的 weighted-gdp-calc 尚无得分, 不计入已完成题数.

1. 公开源文件检查: 87题中84题有 environment Git tree 完全相同的官方镜像标签. 另外3题暂不混用. 详见 OFFICIAL_ENVIRONMENT_CATALOG.json.
2. 公共镜像站尝试: DaoCloud 因 allowlist 拒绝下载. 没有开始答题. 详见 mirror-pull-failure.json.
3. 官方 ghcr.io 尝试: 镜像拉取达到本程序设置的600秒等待时间. 两个后续下载小样本分别23.452秒收到1MB、27.501秒收到0.8125MB, 只作为网络诊断. 详见 primary-registry-throughput.json. 600秒不是已经证实的 Profy 平台统一上限.
4. 南京大学公开缓存: manifest 的 SHA256 与官方完全相同. 两个1MB小样本分别2.041秒、1.965秒. 详见 nju-public-cache-throughput.json. 这里只下载公开环境, 不发 key 或实验数据; 南京大学不参与研究. 下载方式见 https://doc.nju.edu.cn/books/e1654/page/ghcr .
5. 当前尝试: Profy 云端使用该缓存下载相同 digest 的环境, 只开一题. 原题、附件和原 verifier 不修改. 等实际准备、答题和评分完成后才报告分数.
6. xlsx 资源: 11题的 SKILL.md 完全相同, 其中10题全部配套资源也相同. exceltable-in-ppt 的 recalc.py 不同, 保留区别. 详见 xlsx-source-compatibility.json.

本机不下载 image layers, 仅保存必要代码和小记录. 下载失败不是模型答错; 环境检查中的占位 strict=0 不是实验分数. 新增6项免费检查覆盖数据包不夹带 skill、命令边界、后台完成记录、外部 skill 读取和源文件匹配等行为.
