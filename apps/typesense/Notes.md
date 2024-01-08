## Typesense

[Typesense](https://typesense.org/)是一款开源搜索工具，是Algolia 或者大型搜索ElasticSearch 的替代方案

测试范例:  

```
curl "http://URL/collections" -H "X-TYPESENSE-API-KEY: f324f596-f07b-XP7bz4lUmA@Ln6XH"
```

> URL 是域名或 IP:port

## 容器介绍

本项目涉及到两个容器typesense和typesense-scraper


## typesense容器

是数据容器，搜索的文件源，相当于数据服务器。
通过 URL 访问：http://IP:9001/health，如返回 OK 证明容器正常启动。

## typesense-scraper容器

typesense-scraper容器是一个搜集器（爬虫容器），将目标网站的数据搜集到typesenses数据服务器，即上文的typesense容器。它通过IP，端口以及API_KEY等连接下游server服务器;它连接用户网站是通过一个标准格式的json文件，目前我们是采用的[developer.4d.com](https://developer.4d.com)为范例，更多文件格式学习请参照[docsearch-configs](https://github.com/algolia/docsearch-configs)


## 数据流向

通过[developer.4d.com](https://developer.4d.com)为范例，我们来看数据的流向。

typesense-scraper的抓取日志
```
> DocSearch: https://developer.4d.com/docs/19/es/FormObjects/progressIndicator.html 26 records)
...

```
该网站含有"Creating a project"字符，我们在volumes的数据文件对其进行搜索，发现文件保存在.sst内
![image](https://user-images.githubusercontent.com/43192516/153797556-183611e0-1f2a-4c41-95a5-0cb20852fc7a.png)

```
[root@websoft9-jenkins2 db]# pwd
/var/lib/docker/volumes/docker-typesense_typesense/_data/db
[root@websoft9-jenkins2 db]# grep -rn "Creating a project" .
Binary file ./000695.sst matches
Binary file ./000693.sst matches
Binary file ./000694.sst matches
Binary file ./000697.sst matches
```

