## Typesense

[Typesense](https://typesense.org/)是一款开源搜索工具，是Algolia 或者大型搜索ElasticSearch 的替代方案

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
> DocSearch: https://developer.4d.com/docs/19/es/FormObjects/pluginAreaOverview.html 13 records)
> DocSearch: https://developer.4d.com/docs/19/es/FormObjects/picturePopupMenuOverview.html 11 records)
> DocSearch: https://developer.4d.com/docs/19/es/FormObjects/pictureButtonOverview.html 32 records)
> DocSearch: https://developer.4d.com/docs/19/es/FormObjects/listboxOverview.html 501 records)
> DocSearch: https://developer.4d.com/docs/19/es/FormObjects/listOverview.html 91 records)
> DocSearch: https://developer.4d.com/docs/19/es/FormObjects/inputOverview.html 13 records)
> DocSearch: https://developer.4d.com/docs/19/es/FormObjects/groupBox.html 6 records)
> DocSearch: https://developer.4d.com/docs/19/es/FormObjects/dropdownListOverview.html 57 records)
> DocSearch: https://developer.4d.com/docs/19/es/FormObjects/comboBoxOverview.html 30 records)
> DocSearch: https://developer.4d.com/docs/19/es/FormObjects/checkboxOverview.html 88 records)
> DocSearch: https://developer.4d.com/docs/19/es/FormObjects/buttonGridOverview.html 12 records)
> DocSearch: https://developer.4d.com/docs/19/es/FormObjects/buttonOverview.html 78 records)
> DocSearch: https://developer.4d.com/docs/19/es/FormEditor/windowSize.html 15 records)
> DocSearch: https://developer.4d.com/docs/19/es/FormEditor/print.html 10 records)
> DocSearch: https://developer.4d.com/docs/19/es/FormEditor/menu.html 7 records)
> DocSearch: https://developer.4d.com/docs/19/es/FormEditor/markers.html 37 records)
> DocSearch: https://developer.4d.com/docs/19/es/FormEditor/formSize.html 27 records)
> DocSearch: https://developer.4d.com/docs/19/es/FormEditor/propertiesForm.html 56 records)
> DocSearch: https://developer.4d.com/docs/19/es/FormEditor/action.html 12 records)
> DocSearch: https://developer.4d.com/docs/19/es/FormEditor/pictures.html 42 records)
> DocSearch: https://developer.4d.com/docs/19/es/FormEditor/stylesheets.html 103 records)
> DocSearch: https://developer.4d.com/docs/19/es/FormEditor/objectLibrary.html 51 records)
> DocSearch: https://developer.4d.com/docs/19/es/FormEditor/macros.html 76 records)
> DocSearch: https://developer.4d.com/docs/19/es/FormEditor/formEditor.html 372 records)
> DocSearch: https://developer.4d.com/docs/19/fr/WebServer/httpRequests 84 records)
> DocSearch: https://developer.4d.com/docs/19/fr/Menus/sdi.html 31 records)
> DocSearch: https://developer.4d.com/docs/19/fr/Menus/bars.html 16 records)
> DocSearch: https://developer.4d.com/docs/19/fr/Menus/properties.html 79 records)
> DocSearch: https://developer.4d.com/docs/19/fr/Menus/creating.html 54 records)
> DocSearch: https://developer.4d.com/docs/19/fr/Events/onWindowOpeningDenied.html 6 records)
> DocSearch: https://developer.4d.com/docs/19/fr/Events/onVpReady.html 5 records)
> DocSearch: https://developer.4d.com/docs/19/fr/Events/onVpRangeChanged.html 12 records)
> DocSearch: https://developer.4d.com/docs/19/fr/Events/onValidate.html 5 records)
> DocSearch: https://developer.4d.com/docs/19/fr/Events/onUrlResourceLoading.html 6 records)
> DocSearch: https://developer.4d.com/docs/19/fr/Events/onUrlLoadingError.html 6 records)
> DocSearch: https://developer.4d.com/docs/19/fr/Events/onUrlFiltering.html 6 records)
> DocSearch: https://developer.4d.com/docs/19/fr/Events/onUnload.html 9 records)
> DocSearch: https://developer.4d.com/docs/19/fr/Events/onTimer.html 4 records)
> DocSearch: https://developer.4d.com/docs/19/fr/Events/onSelectionChange.html 14 records)
> DocSearch: https://developer.4d.com/docs/19/fr/Events/onScroll.html 9 records)
> DocSearch: https://developer.4d.com/docs/19/fr/Events/onRowResize.html 4 records)
> DocSearch: https://developer.4d.com/docs/19/fr/Events/onRowMoved.html 4 records)
> DocSearch: https://developer.4d.com/docs/19/fr/Events/onResize.html 5 records)
> DocSearch: https://developer.4d.com/docs/19/fr/Events/onPrintingFooter.html 5 records)
> DocSearch: https://developer.4d.com/docs/19/fr/Events/onPrintingDetail.html 5 records)
> DocSearch: https://developer.4d.com/docs/19/fr/Events/onPrintingBreak.html 5 records)
> DocSearch: https://developer.4d.com/docs/19/fr/Events/onPlugInArea.html 3 records)
> DocSearch: https://developer.4d.com/docs/19/fr/Events/onPageChange.html 6 records)
> DocSearch: https://developer.4d.com/docs/19/pt/WebServer/httpRequests 84 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Menus/sdi.html 31 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Menus/bars.html 16 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Menus/properties.html 79 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Menus/creating.html 54 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Events/onWindowOpeningDenied.html 6 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Events/onVpReady.html 5 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Events/onVpRangeChanged.html 12 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Events/onValidate.html 5 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Events/onUrlResourceLoading.html 6 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Events/onUrlLoadingError.html 6 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Events/onUrlFiltering.html 6 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Events/onUnload.html 9 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Events/onTimer.html 4 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Events/onSelectionChange.html 14 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Events/onScroll.html 9 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Events/onRowResize.html 4 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Events/onRowMoved.html 4 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Events/onResize.html 5 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Events/onPrintingFooter.html 5 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Events/onPrintingDetail.html 5 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Events/onPrintingBreak.html 5 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Events/onPlugInArea.html 3 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Events/onPageChange.html 6 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Events/onOutsideCall.html 4 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Events/onOpenExternalLink.html 6 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Events/onOpenDetail.html 7 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Events/onMouseUp.html 6 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Events/onMouseMove.html 13 records)
> DocSearch: https://developer.4d.com/docs/19/pt/Events/onMouseLeave.html 10 records)

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

