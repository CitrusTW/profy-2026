# 云端环境检查, 不计入 benchmark 成绩

- [PRoot 实际检查](cloud-proot-chunked-memory-check/runtime_check.json): 临时 Alpine Linux 环境执行成功, 返回 x86_64, 已删除临时运行目录. [公开来源与 hash](cloud-proot-chunked-memory-check/PUBLIC_RUNTIME_SOURCES.json).
- 官方工具包和镜像只经过客户端内存, 没有写成本机镜像或环境. 整包和约4MB单文件上传曾超时, 改为每片最多500KB后成功.
- [原生 Docker 安装错误](cloud-native-engine-retry/engine_check.json): 包已经下载并解包, docker.io 配置因 Perl 报 Insecure directory in $ENV{PATH} 而退出. [标准 PATH 重试](cloud-native-engine-secure-path/engine_check.json)仍返回同一配置错误. 不能写成原生 Docker 已跑通或云端不支持 Docker.
- 这些检查没有求解 benchmark 题, 不增加已完成题数. result.json 的 strict=0 是 Probe 的占位值, 不是题目得分.
- 本机旧的批量 Docker 构建、输入准备和评分入口已停用. 云端 Dockerfile 流程仍待验证, PRoot 成功不等于87题已可跑.
