## Strapi

Strapi can use MySQL, PostgreSQL...


### Install

Strapi fist time starting will install dependencies below

* Install nodes
* Download files from Github

```
$ docker logs strapi

...
> sharp@0.28.1 install /srv/app/node_modules/sharp
> (node install/libvips && node install/dll-copy && prebuild-install) || (node-gyp rebuild && node install/dll-copy)

sharp: Downloading https://github.com/lovell/sharp-libvips/releases/download/v8.10.6/libvips-8.10.6-linux-x64.tar.br
```

This cause packages can not install and container failed

### Quick Start

1. 增加一个数据集，假如名为为：dockers


2. 增加一个用户，设置角色为 public


3. 编辑 Public role，使之有权限访问 dockers 数据集


4. 访问下面的 URL 便可以获取数据

   ```
   # 获取所有数据
   http://IP:1337/dockers/1
   
   # 获取第一条数据
   http://IP:1337/dockers/1
   ```

   
