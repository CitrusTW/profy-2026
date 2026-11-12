# 原生 Docker 已完成的检查

在 Profy 云端, 私有 Docker engine 已实际拉取并运行 Alpine Linux, 返回 cgl-cloud-native-engine-ok. [实际记录](cloud-private-engine-pinned-mirrors/private_engine_check.json)包含版本、image ID 和官方 manifest digest.

直连 Docker Hub 超时. 按 [Google 公开缓存说明](https://docs.cloud.google.com/artifact-registry/docs/pull-cached-dockerhub-images)和 [DaoCloud 公开镜像说明](https://github.com/DaoCloud/public-image-mirror)配置免费缓存, 使用从 Docker 官方读取的固定 SHA256, 下载内容由 Docker 校验. 本机没有下载或保存镜像.

安装 Debian docker.io 时的配置脚本仍报 PATH 安全错误. 本次成功检查使用已解包的官方程序, 没有关闭安全检查. 新 runner 改为只下载、解包官方软件包到私有目录, 避免运行系统安装脚本; 这条原题路径仍需要实际验证.

清理记录仍有 busy mount 错误, temporary_engine_data_removed=false. 不能写成所有临时路径都清理完成. 这项检查不增加 benchmark 完成题数.
