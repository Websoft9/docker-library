# GoCD

GoCD 是一个由 ThoughtWorks 开发的开源持续交付工具。

# 安装

本应用包含 GoCD Server 和 GoCD Agent 两个容器。首次启动需耐心等待两者均正常运行。

# Agent授权

Agent 首次启动后需在 GoCD Server Web 界面授权：
1. 访问 GoCD Server Web 界面。
2. 点击 “Agents” 菜单。
3. 勾选待授权 Agent，点击 “Enable” 按钮，状态变为 Idle 即可使用。

# 配置说明

- GoCD Server 配置文件位于数据卷 `gocd-server-data` 的 `/_data/config` 目录。
- GoCD Agent 配置文件位于数据卷 `gocd-agent-data` 的 `/_data/config` 目录。

# 插件安装

将插件文件放入数据卷 `gocd-server-data` 的 `/_data/plugins` 目录，重启 Server 生效。