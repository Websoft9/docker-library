# DiscuzQ

官网：https://discuzq.icu/

官方已经22个月没有更新 Docker 镜像，故本应用暂时停止维护

## 安装

1. DiscuzQ 镜像包含MySQL，但出于维护考虑，本项目没有使用内置 MySQL.
2. 官方默认挂载到：/var/lib/discuz，但这个目录下没有源码。只有挂载到：/var/www/discuz 才有源码
3. 官方提供了不包含 DB 的版本，但测试失败，暂无文档支持，放弃（[issue](https://github.com/Websoft9/docker-discuzq/issues/3)）

## 安装向导优化

自动填充初始化向导中的数据库连接信息，以降低用户的使用难度。
方案：修改 /resources/views/install/install.blade.php 源码中的数据库配置信息即可

```
  <div class="FormGroup">
    <div class="FormField">
      <label>MySQL Host</label>
      <input name="mysqlHost" value="localhost">
    </div>

    <div class="FormField">
      <label>MySQL 数据库</label>
      <input name="mysqlDatabase" value="localhost">
    </div>

    <div class="FormField">
      <label>MySQL 用户名</label>
      <input name="mysqlUsername">
    </div>

    <div class="FormField">
      <label>MySQL 密码</label>
      <input type="password" name="mysqlPassword">
    </div>

    <div class="FormField">
      <label>表前缀</label>
      <input type="text" name="tablePrefix">
    </div>
  </div>
```
