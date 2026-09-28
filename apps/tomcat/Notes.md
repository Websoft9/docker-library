# Tomcat Notes

> 内部维护说明；面向客户的文档以 `README.md` 为准。

## 来源

- 官方镜像：https://hub.docker.com/_/tomcat
- 镜像源码：https://github.com/docker-library/tomcat
- 版本列表：https://hub.docker.com/_/tomcat/tags

## 版本

- `W9_VERSION=11.0-jdk21-temurin`：Tomcat 11 稳定线 + JDK21 LTS。
- `variables.json` 只保留当前上游仍发布的 temurin 变体（`11.0` / `10.1` / `9.0`）；官方已移除 `corretto` 变体，故不再列出。
- 数据卷 `tomcat:/usr/local/tomcat` 持久化整个 Tomcat 目录（含 `webapps` 与 `conf`）。

## 启动机制（runtime-app 约定）

参照 `docs/runtime-app-spec.md`，与 `springboot` 一致，但**不**引入非 root 用户/permissions 侧车（Tomcat 官方镜像以 root 运行，改动风险大）。

```
src/entrypoint.sh            # orchestrator，挂到 /opt/websoft9/entrypoint.sh
src/entrypoint.d/*.sh        # 包内钩子，挂到 /opt/websoft9/entrypoint.d（只读）
src/start.sh                 # 默认启动，挂到 /opt/websoft9/start.sh（只读）
```

- 钩子来源两处，同名用户钩子覆盖包内钩子，按文件名排序，每次启动都执行且必须幂等：
  - 包内：`/opt/websoft9/entrypoint.d`
  - 用户：`${APP_DIR}/.w9/entrypoint.d`，即 `/usr/local/tomcat/.w9/entrypoint.d`
- `APP_DIR=/usr/local/tomcat`（复用数据卷）；用户可放 `${APP_DIR}/.w9/start.sh` 覆盖默认启动。
- 默认钩子 `10-webapps.sh`：`cp -a webapps.dist/. webapps/`，恢复 ROOT/docs/examples 默认应用。
- `start.sh` 用 `exec catalina.sh run`，保证 Tomcat 是 PID1、能收到 SIGTERM。
- 与 runtime-app-spec 的差异：不使用 `DATABASE_URL` 覆盖，不使用非 root 用户。

## 运行 war 包

进入 **tomcat** 容器，下载官方示例，会自动解压：

```
cd /usr/local/tomcat/webapps && wget https://tomcat.apache.org/tomcat-11.0-doc/appdev/sample/sample.war
cd /usr/local/tomcat/webapps && wget https://tomcat.apache.org/tomcat-11.0-doc/appdev/sample/sample.war -O ROOT.war
```

`ROOT.war` 会自动解压到根目录（不包含路径）。

## 测试

- `tests/cases.yml`：默认自适应检查（compose-config / container-up / container-healthy / web-access `/`）之外，加两个 `script` 用例：
  - `smoke.sh`：校验欢迎页内容，证明 `10-webapps.sh` 的默认应用已恢复。
  - `war-deploy.sh`：在容器内用 `jar` 造一个极小 WAR，放进 `webapps/`，等待自动解压并校验 context，验证真实 WAR 部署路径。
- `script` 用例默认在**部署目标**执行（remote 时走 SSH，见 `docs/app-tests.md`），因此 `war-deploy.sh` 可以使用远端 `docker exec`；`BASE_URL` 在远端被改写为 `http://localhost:${W9_HTTP_PORT_SET}`。
