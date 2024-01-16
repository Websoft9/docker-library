# 9Panel

![](images/icon/websoft9-imagepanel.png)
> 9Panel（[演示](https://websoft9.github.io/9panel/)）是Websoft9公司镜像的开源组件之一，支持中英文显示，部分镜像内置了9Panel. 它是集合数据库管理、文档和支持服务的引导页面，是镜像快速入门的向导工具。基于Bootstrap+vue.js开发，几乎不会占用系统资源，也不会对系统文件进行任何修改。

## 使用说明

本镜像支持包含web服务器的所有镜像，可以是基础镜像，也可以是应用镜像，但应用镜像最多不超过2个

应用默认为Example,表示安装的是示例

打开js/websoft9.js文件，你会看到如下的默认信息。代表：LAMP基础环境
```
var set_infrastructure="LAMP";
var set_apps=["Example"];
```

假如您需要修改为WordPress（LNMP），对应的配置为：
```
var set_infrastructure="LNMP";
var set_apps=["WordPress"];
```

假如您需要修改为WordPress&Discuz（LAMP），对应的配置为：
```
var set_infrastructure="LNMP";
var set_apps=["WordPress","Discuz"];
```

如果您需要修改基础环境中的组件，请找到它，然后修改其中的参数：

```
{
    "name":"IIS",
    "apps":"",
    "language":["PHP",".NET","Java"],
    "os":"Windows",
    ...
  },

  若不包含java，那么修改language项即可

  {
    "name":"IIS",
    "apps":"",
    "language":["PHP",".NET"],
    "os":"Windows",
    ...
  },

```

## 注意事项

1. 参数名称必须在websoft9.js的json定义区存在，并区分大小写
2. 不存在的镜像，需要在json区域新增
