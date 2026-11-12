# 云端执行检查, 不是 benchmark 得分

- 87道原题中, 84道在 SkillsBench 维护方的镜像里有完全相同的 environment Git tree. 这里只核对文件和标签, 不代表84道已经跑过或已通过评分.
- 另外3道环境不同: fix-visual-stability, gravitational-wave-detection, llm-prefix-cache-replay. 不直接混用.
- weighted-gdp-calc 的公共镜像站拉取被 allowlist 拒绝. 准备程序退出, 没有开始答题, 不计为0分.
- 随后在同一 Profy 云端确认官方 ghcr.io 匿名令牌、manifest 和一个 blob 字节都能访问. 没有绕过镜像站限制.
- 已开始通过官方地址拉取相同 digest 的新尝试, 截至本记录还没有新评分. 原题和原 verifier 未修改.
- 600秒出现在实际工具参数和原题 build 配置中, 不能据此称为 Profy 平台统一上限.
- 镜像和运行环境只下载到云端, 本机没有下载 image layers. Git 中只保存小记录、代码、技能正文和结果.

实际诊断在 mirror-pull-failure.json 和 primary-registry-connectivity.json. 它们不是答题结果, 没有 accuracy. 官方环境清单在 OFFICIAL_ENVIRONMENT_CATALOG.json.
