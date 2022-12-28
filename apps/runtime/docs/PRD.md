# PRD

## Java 选型

优先顺以及理由：
1，jdk+jetty
也是目前轻量级的web服务器，使用广泛
2，hbase+zookeeper
大数据方面很多涉及集群，分布式，可能研究安装还有些问题，
此组合考虑到使用广泛性以及可以单机安装来实现
3，ElasticSearch
作为一个分布式、支持多用户的全文搜索引擎，实现RESTful Web接口。
调查分析了其特性，有助于我们今后日志分析，加快速度。
应该大大快于流处理读日志文件。
1，JDK
建议oracle官方JDK，暂时不选openjdk，防止差异导致的程序运行bug
注：oracle会在2022年后停止jdk7的升级，建议最好安装jdk8
2，web服务器
tomcat，jetty，weblogic，webshpere
jetty  
jetty和我们通常使用的tomcat一样，是一个开源的servlet容器，特点是轻量易部署，一方面jetty可以作为web容器使用，
另一方面也是最一般的方式是jetty以一组jar包的形式发布，所以很容器被实例化成为一个对象从而嵌入到我们的应用程
序中，让java应用程序可以独立的发布和运行
3，大数据
1）Hadoop
*因为生产需要多服务器集群配置，暂时不考虑镜像安装
Hadoop是一个由Apache基金会所开发的分布式系统基础架构。用户可以在不了解分布式底层细节的情况下
开发分布式程序。充分利用集群的威力进行高速运算和存储。Hadoop实现了一个分布式文件系统（Hadoop  
Distributed File System），简称HDFS。HDFS有高容错性的特点，并且设计用来部署在低廉的（low-cost）
硬件上；而且它提供高吞吐量（high throughput）来访问应用程序的数据，适合那些有着超大数据集（large
data set）的应用程序。HDFS放宽了（relax）POSIX的要求，可以以流的形式访问（streaming access）
文件系统中的数据。Hadoop的框架最核心的设计就是：HDFS和MapReduce。HDFS为海量的数据提供了存储，
而MapReduce则为海量的数据提供了计算
2）HBase
HBase是一个分布式的、面向列的开源数据库，它不同于一般的关系数据库，更适合于非结构化数据存储的数据库，
是一个高可靠性、高性能、面向列、可伸缩的分布式存储系统，大数据开发需掌握HBase基础知识、应用、架构以及高级用法等。
HBase是Google Bigtable的开源实现，类似Google Bigtable利用GFS作为其文件存储系统，HBase利用Hadoop HDFS作为其文件
存储系统；Google运行MapReduce来处理Bigtable中的海量数据，HBase同样利用Hadoop MapReduce来处理HBase中的海量数据；
Google Bigtable利用 Chubby作为协同服务，HBase利用Zookeeper作为对应
3），Zookeeper
ZooKeeper是一个分布式的，开放源码的分布式应用程序协调服务，是Google的Chubby一个开源的实现，是Hadoop和Hbase的重要组件。
它是一个为分布式应用提供一致性服务的软件，提供的功能包括:配置维护、域名服务、分布式同步、组服务等
4），spark
Apache Spark 是专为大规模数据处理而设计的快速通用的计算引擎。Spark是UC Berkeley AMP lab (加州大学伯克利分校的AMP实验室)
所开源的类Hadoop MapReduce的通用并行框架，Spark，拥有Hadoop MapReduce所具有的优点;但不同于MapReduce的是--Job中间输出结果
可以保存在内存中，从而不再需要读写HDFS，因此Spark能更好地适用于数据挖掘与机器学习等需要迭代的MapReduce的算法。
5），ElasticSearch
ElasticSearch是一个基于Lucene的搜索服务器。它提供了一个分布式、支持多用户的全文搜索引擎，基于RESTful Web接口。
ElasticSearch是用Java开发的，并作为Apache许可条款下的开放源码发布，是当前流行的企业级搜索引擎。设计用于云计算中，
能够达到实时搜索、稳定、可靠、快速、安装使用方便
6），HIVE
hive是基于Hadoop的一个数据仓库工具，可以将结构化的数据文件映射为一张数据库表，并提供完整的sql查询功能，
可以将sql语句转换为MapReduce任务进行运行。 其优点是学习成本低，可以通过类SQL语句快速实现简单的MapReduce统计，
不必开发专门的MapReduce应用，十分适合数据仓库的统计分析
