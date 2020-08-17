---
layout:     post
title:     Parquet的那些事
subtitle:   Parquet的那些事
date:       2018-09-22
author:     网文
header-img: img/post-bg-2015.jpg
catalog: true
tags:
    - parquet
    - Hadoop
    - storage
typora-copy-images-to: ../img
typora-root-url: ..
---

# Parquet的那些事（一）基本原理

[Bruce](https://www.zhihu.com/people/xiao-zhu-ge-22-92)

8 人赞同了该文章

数据的接入、处理、存储与查询，是大数据系统不可或缺的四个环节。随着数据量的增加，大家开始寻找一种高效的数据格式，来解决存储与查询环节的痛点。

- 高效的压缩编码，用于降低存储成本
- 高效的读取能力，用于支撑快速查询

Parquet便是在这样的背景下诞生，与TEXT、JSON、CSV等文件格式相比，它有三个核心特征，为解决上述的痛点问题提供了基础。

- 列式存储
- 自带Schema
- 具备Predicate Filter特性

在行式存储中，一行的多列是连续的写在一起的，而在列式存储中，数据按列分开存储。由于同一列的数据类型是一样的，可以使用更高效的压缩编码进一步节约存储空间。

![img](/img/v2-cb0f83759d962b3b6004e7a96dd7f5cf_720w.jpg)

对于大多数数据存储服务，如MySQL、MongoDB、Elasticsearch等，为了提高查询性能，都会在数据写入时建立相应的索引。而存放在HDFS、AWS S3上的大数据是直接以文件形式存储的，那么如何实现快速查询呢？目前主要有三种手段，核心目的是**尽可能只加载有符合数据的文件**，而这些手段都能基于Parquet实现。

- Partition Pruning。类似于将文件分文件夹存放的思路，根据某些字段将数据进行分区，在查询时指定相应的分区条件。
- Column Projection。在查询中指定需要返回的字段，跳过不必要的字段，减少需要加载的数据量。
- Predicate Filter。先判断一个文件中是否存在符合条件的数据，有则加载相应的数据，否则跳过。

![img](/img/v2-c87171e9f105906e3197601217d4e54e_720w.jpg)

本文主要介绍Parquet的文件结构、Predicate Filter特性以及常用的一些工具。与Parquet相似且有着广泛应用的还有ORC，我们将在后面介绍二者的区别。本文所述主要基于parquet-mr 1.8.2。

## Parquet文件结构

一个Parquet文件的内容由Header、Data Block和Footer三部分组成。在文件的首尾各有一个内容为PAR1的Magic Number，用于标识这个文件为Parquet文件。Header部分就是开头的Magic Number。

Data Block是具体存放数据的区域，由多个Row Group组成，每个Row Group包含了一批数据。比如，假设一个文件有1000行数据，按照相应大小切分成了两个Row Group，每个拥有500行数据。每个Row Group中，数据按列汇集存放，每列的所有数据组合成一个Column Chunk。因此一个Row Group由多个Column Chunk组成，Column Chunk的个数等于列数。每个Column Chunk中，数据按照Page为最小单元来存储，根据内容分为Data Page和Dictionary Page。这样逐层设计的目的在于：

- 多个Row Group可以实现数据的并行加
- 不同Column Chunk用来实现列存储
- 进一步分割成Page，可以实现更细粒度的数据访问

Footer部分由File Metadata、Footer Length和Magic Number三部分组成。Footer Length是一个4字节的数据，用于标识Footer部分的大小，帮助找到Footer的起始指针位置。Magic Number同样是PAR1。File Metada包含了非常重要的信息，包括Schema和每个Row Group的Metadata。每个Row Group的Metadata又由各个Column的Metadata组成，每个Column Metadata包含了其Encoding、Offset、Statistic信息等等。

![img](/img/v2-2cf4fccb5e779872fa3463995f0de390_720w.jpg)

## Predicate Pushdown Filter特性

所谓Predicate Pushdown Filter，是指在不影响结果的情况下，将过滤条件提前执行，过滤掉不满足条件的文件，降低需要传输的数据集，从而提升性能。比如，在S3上面有1000个文件（100GB），现在要执行下面的SQL查询，有两种选择：

- 将所有文件内容都加载进来（1000个文件），再对内容执行过滤条件，得到结果
- 只加载有符合条件(age >= 22)的数据的文件（100个文件），得到结果

```text
SELECT name, school FROM student WHERE age >= 22
```

第二个选择就是Predicate Pushdown Filter的方式。那么在Parquet中如何做到这点呢？在读取Parquet文件时，会先根据Footer Length找到Footer起始位置，读取Parquet中的Metadata，通过Metadata中的信息可以帮助我们进行相应的条件过滤。目前有两种实现，分别针对不同的数据类型。

- 整型数据

Column Metada中，有该Column Chunk中数据的Range信息: Max和Min。将过滤条件与Range信息进行对比，就可以知道是否需要加载该文件的数据。

```text
File 0
	Row Group 0, Column Statistics -> (Min -> 20, Max -> 30)
	Row Group 1, Column Statistics -> (Min -> 10, Max -> 20)
File 1
	Row Group 0, Column Statistics -> (Min -> 6, Max -> 21)
	Row Group 1, Column Statistics -> (Min -> 25, Max -> 45)
	
通过对比过滤条件age >= 22，只需要加载File 0的Row Group 0和File 1的Row Group 1中的数据。
```

- 字符数据

先说说什么是字典编码。假设有个字段name，在10条数据中的值分别为：

```text
name:
	bruce, cake, bruce, kevin, bruce, kevin, cake, leo, cake, bruce
```

我们可以对其编码，将其变为：

```text
name:
	0, 1, 0, 2, 0, 2, 1, 3, 1, 0
dictionary:
	0 -> bruce, 1 -> cake, 2 -> kevin, 3 -> leo
```

这种方式在很多开源软件中都有使用，比如Elasticsearch，有两个优点：

- 可以节省存储空间
- 可以根据dictionary中的内容，过滤掉不符合条件的数据

在Parquet中，我们可以根据字符编码的特性来做相应的过滤。通过Column Metada中的信息，读取相应的Dictionary Page进行对比，从而过滤掉不符合条件的数据。

```text
查询语句： SELECT name, school FROM student WHERE name = "leo"

File 0
	Row Group 0, Column 0 -> 0: bruce, 1:cake
	Row Group 1, Column 0 -> 0: bruce, 2:kevin
File 1
	Row Group 0, Column 0 -> 0: bruce, 1:cake, 2: kevin
	Row Group 1, Column 0 -> 0: bruce, 1:cake, 3: leo
	
通过对比过滤条件name = "leo"，只需要加载File 1的Row Group 1中的数据。
```

## 常见的Parquet工具

与JSON、CSV等文件相比，Parquet是无法人类可读的，需要通过一些工具来窥探其内容，这里列举一些常用的工具，供选择。

- parquet-mr提供的工具parquet-tools

- - 由[官方](https://link.zhihu.com/?target=https%3A//github.com/apache/parquet-mr/tree/master/parquet-tools)提供，下载源码编译jar包
  - 采用命令行形式，通过参数来指定相关功能

```text
示例：
java -jar ./parquet-tools-1.8.2.jar meta part-00003-c04d37ba-3de5-4f7b-addc-b6f4bc5a7ab1-c000.snappy.parquet
```

- 开源的工具bigdata-file-viewer

- - 通过[GitHub](https://link.zhihu.com/?target=https%3A//github.com/Eugene-Mark/bigdata-file-viewer)下载jar包
  - 有UI可以查看数据，通过命令行启动UI

```text
java -jar ./BigdataFileViewer-1.2-SNAPSHOT-jar-with-dependencies.jar
```

![img](/img/v2-1ce1b8498d49cb4ddb2ff39ed5a12ac8_720w.jpg)



（全文完）

> 本文同步发表在我的博客：[https://bruce.blog.csdn.net/article/details/104582229](https://link.zhihu.com/?target=https%3A//bruce.blog.csdn.net/article/details/104582229)



# Parquet的那些事（二）Spark中的Schema兼容问题



Parquet是一种存储格式，其本身与任何语言、平台都没有关系，也不需要与任何一种数据处理框架绑定。但是一个开源技术的发展，必然需要有合适的生态圈助力才行，Spark便是Parquet的核心助力之一。作为内存型并行计算引擎，Spark被广泛应用在流处理、离线处理等场景，其从1.0.0便开始支持Parquet，方便我们操作数据。

在Spark中操作Parquet文件有两种方式，一种是直接加载文件，另一种是透过Hive表来读取数据。我们姑且称之为文件加载、表加载。这两种方式在API层面都非常简洁，它隐藏了底层推导Schema、并行加载数据等细节。

```text
# By File
df = spark.read.parquet("s3://mydata/type=security")

# By Table
df = spark.read.table("data_mine.security_log")
```

在实际使用中，我们经常会遇到**Schema兼容**的问题，其根源是Schema不一致，主要有以下两种情况：

- 存放在HDFS/S3上面的Parquet文件具有不同的Schema
- Hive Metastore Schema与Parquet文件自带的Schema不一致

不管是需求变化、产品迭代还是其他原因，总是会出现Schema变化的情况，导致不同Parquet文件的Schema不同。比如，新增了一个字段。如果是以表加载方式操作数据，当Schema变化时，需要更新Metastore Schema，此时又会导致Metastore中的Schema跟部分Parquet文件的Schema不一致。要确保在这些问题下，我们仍然能通过Spark正确的加载文件数据，就需要搞清楚里面的一些实现细节。

![img](/img/v2-e3f17f3ff77872d082fb4099c913822d_720w.jpg)

本文将从文件加载、表加载两个方面来探讨Spark是如何做Schema推导和兼容的。文中所述的细节均基于Spark 2.4.0。

## 文件加载

在加载Parquet文件时，Spark会先建立InMemoryFileIndex、推导Schema。建立InMemoryFileIndex，是指枚举指定路径下的文件，获取相应的Partition与文件路径信息。比如，下图中 *s3://mydata/type=security* 路径下有4个*ts_interval*的Partition，每个Partition下有3个Parquet。这些信息会缓存在Spark Driver中，用于后续的Pushdown Filter、访问文件等。

![img](/img/v2-1e4e248704fb32e63e406d9768c768b6_720w.png)

![img](/img/v2-c87171e9f105906e3197601217d4e54e_720w-20200809153439521.jpg)

有了InMemoryFileIndex，便可以访问Parquet文件的Footer信息来获取Schema了。默认情况下，Spark会选择其中一个文件来读取Schema。这个做法在多个Parquet文件具有不同Schema时就会有问题。因此，Spark提供了参数*spark.sql.parquet.mergeSchema*，当其被设置为*true*时，便会读取所有文件的Schema进行合并。需要注意的是，如果两个文件中存在同一个名称的字段，但是二者的数据类型不一样，是无法进行Merge的，会直接报错。

显然，这是通过牺牲一定的性能来换取Schema的准确性。为了将性能的损耗降到最低，Spark采用了并行加载的方式来读取Schema，然后再进行合并，具体可以查看[源代码中的mergeSchemasInParallel函数](https://link.zhihu.com/?target=https%3A//github.com/apache/spark/blob/v2.4.0/sql/core/src/main/scala/org/apache/spark/sql/execution/datasources/parquet/ParquetFileFormat.scala)。

![img](/img/v2-5ba61ad0318a91bca4f9b7059a0a3aae_720w.jpg)

鉴于*mergeSchema*的性能问题，我们应该尽量避免两点：

- 避免在大范围的数据上使用该参数，比如只在一天的数据上应用
- 避免在全局周期内使用该参数，比如只在某个过渡期间开启该参数

还有一种方式是在读取文件时指定Schema。在这种情况下，Spark不再推导Schema。Schema的兼容参照下面规则：

- 如果指定的Schema中有字段A，某个Parquet文件中没有，A会被赋值为null
- 如果指定的Schema中没有字段A，而在某个Parquet文件中有，字段A会被忽略掉
- 如果字段A的类型在指定的Schema和Parquet文件中的不一致，则会报错

```text
schema = StructType([StructField("name", StringType()), StructField("age", LongType()), StructField("gender", StringType())])
df = spark.read.schema(schema).parquet("file:///Downloads/user_specified_schema_test")
```

## 表加载

Hive系统由三部分组成：存储在HDFS/S3的数据、Metastore、HiveQL。在Spark中开启Hive支持后，主要是利用其前两部分，即透过Metastore来访问数据，而具体的执行引擎是采用Spark SQL自己的。[HiveExternalCatalog](https://link.zhihu.com/?target=https%3A//github.com/apache/spark/blob/v2.4.0/sql/hive/src/main/scala/org/apache/spark/sql/hive/HiveExternalCatalog.scala)中提供了一系列操作Hive Metastore的方法。

通过表来加载Parquet文件数据时，Spark会从Metastore中拿到Partition、文件路径等信息，因此不需要再建立InMemoryFileIndex了。Spark先推导文件的Schema，然后跟Metastore中的Schema进行合并。推导文件Schema的方法在上面已做了详细阐述，这里主要探讨下两种Schema合并的规则：

- 对于相同的字段（不区分大小写），采用Parquet文件中的字段名加上Metastore中的数据类型，如果类型不能被转换则会报错
- 如果Metastore中有字段A，Parquet文件中有A和B，则只有A
- 如果Metastore中有字段A和B， Parquet文件中只有B，那么有A和B，但是A必须是nullable，A会被赋值为null

上述规则可以参考阅读[源码中的mergeWithMetastoreSchema函数](https://link.zhihu.com/?target=https%3A//github.com/apache/spark/blob/v2.4.0/sql/hive/src/main/scala/org/apache/spark/sql/hive/HiveMetastoreCatalog.scala)。如果觉得比较晦涩，可以参考阅读其[测试用例](https://link.zhihu.com/?target=https%3A//github.com/apache/spark/blob/v2.4.0/sql/hive/src/test/scala/org/apache/spark/sql/hive/HiveSchemaInferenceSuite.scala)。

![img](/img/v2-31b5b13f7db2a0543dfbd61070fb4f3d_720w.jpg)



（全文完）

> 本文同步发表于我的博客：[https://bruce.blog.csdn.net/article/details/104670086](https://link.zhihu.com/?target=https%3A//bruce.blog.csdn.net/article/details/104670086)



# Parquet的那些事（三）嵌套数据模型

[![Bruce](/img/v2-67d2eabbae28e8ac67dcc68f074ef912_xs-20200809153613175.jpg)](https://www.zhihu.com/people/xiao-zhu-ge-22-92)

[Bruce](https://www.zhihu.com/people/xiao-zhu-ge-22-92)

4 人赞同了该文章

在大数据系统中，我们总是不可避免的会遇到嵌套结构的数据。这是因为，在很多场景下，嵌套数据结构能更好的表达数据内容与层级关系，因此很多数据源会采用这样的结构来输出数据。然而，相比关系型的结构化数据，这样的数据并不利于高效查询，因此在很多场景下，我们还会通过ETL将其变为扁平结构的数据来存储。

2010年，Google发表了论文[Dremel: Interactive Analysis of Web-Scale Datasets](https://link.zhihu.com/?target=https%3A//research.google/pubs/pub36632/)，阐述了一种针对嵌套数据的交互式查询系统，为业界提供了思路。正如官方文档所述，Parquet在最初设计时，便借鉴了Dremel的数据模型思想，支持嵌套结构的存储。当然，Parquet只是一种列式存储格式，要完成类似Dremel的查询功能，还需要计算引擎的配合。

> Parquet is built from the ground up with complex nested data structures in mind, and uses the record shredding and assembly algorithm described in the Dremel paper. We believe this approach is superior to simple flattening of nested name spaces.

本文主要探讨Parquet是如何支持嵌套结构存储的。搞清楚这些，能帮助我们更好的设计数据存储方式、选择合适的查询引擎。本文将采用下面的3条数据来进行阐述，后面用“示例”来代表。另外，文中所述是基于Spark 2.4.0、Parquet 1.10.0的。

```text
Record 1:
{
    "sid":"8509_1576752657",
    "appid":[81, 205, 67],
    "tcp": {
        "mss": 1750,
        "flag": 344
    },
    "trans":[
        {
            "uri":"/icon.jpg",
            "monitor_flag":1
        },
        {
            "uri":"/myyhp_2.2-4.js"
        }
    ]
}

Record 2:
{
    "sid":"8510_1576752667",
    "appid":[58, 98]
}

Record 3:
{
    "sid":"8511_1576754667",
    "appid":[198],
    "tcp": {
        "flag": 256
    }
}
```



## 数据模型

我们先来看看嵌套结构的数据具有哪些特性，从而搞清楚其存储要解决的问题是什么。

- 数据具有层级关系，比如示例中的tcp下面有mss和flag
- 允许部分字段为空，即没有定义，比如示例中的trans在第2、3条数据中都没有
- 有些字段的值有多个，即是一个数组，比如示例中的appid

在Parquet的世界里，数据是以列式存储的，每条数据最终都要转化成一组列来存储。那么，**该用什么模型来表达一个嵌套结构呢？**

参考Dremel的方式，针对示例中的数据，可以使用下面的模型来表达。对于一个数据结构，其根为Record，称为message，其内部每个字段包含三部分：字段类型、数据类型、字段名称。通过数据类型group来表达层级关系；通过将字段类型分为三种，来表达空或数组的概念。

- required：exactly one occurrence
- optional: 0 or 1 occurrence
- repeated: 0 or more occurrence

```text
message Record {
	required string sid, 
	repeated long appid,
	optional group tcp {
		optional long mss,
		optional long flag
	},
	repeated group trans {
		optional string uri,
		optional int monitor_flag
	}
}
```

我们将上面的数据模型转化成树型关系图，其所要表达的数据列便会呈现出来。

![img](/img/v2-67ba46353fbd69a30cb16bec4da55974_720w.jpg)

到这里，我们可以将示例中的数据转换成下表所示的形式，来实现列式存储。然而，新的问题又出现了，我们**无法将其恢复到原来的数据行的结构形式**。以appid为例，你不知道这些值里面哪些是第一行的值，哪些是第二行的，等等。因此，单纯依靠一个值来表达是不够了。Parquet采用了Dremel中(R, D, V)模型，V表示数据值，D和R将在下面分别介绍。

![img](/img/v2-ebc13800f51d0b697ab5e43b0580056b_720w.jpg)



## Definition Level

D，即Definition Level，用于表达某个列是否为空、在哪里为空，其值为当前列在第几层上有值。对于required的字段，没有D值。

以示例的trans.monitor_flag为例。Root为第0层级，trans为第1层级，monitor_flag为第2层级。在第1条数据中，trans有两个值，第1个值里面的monitor_flag有值，因此D=2；第2个里面没有monitor_flag，因此D=1。在第2条数据中，没有trans，因此D=0。第3条数据，与第2条数据情况一致。

![img](/img/v2-60e8daad8cf006b70bf4c92e68e3f581_720w.jpg)

另一个列tcp.mss的情况如下，读者可以自行推导。

![img](/img/v2-a53696680fc4c067dc0a30f3144923a9_720w.jpg)



## Repetition Level

R，即Repetition Level，用于表达一个列有重复，即有多个值的情况，其值为重复是在第几层上发生。

以示例的appid为例。Root为第0层级，appid为第1层级。对于每条新的数据，第1个appid的值对应的R一定是0；而对于每条数据里面的多个值，则是用appid所在的层来表示，即R=1。比如，第1条数据有3个appid值，其第1个的R=0，后面两个的R=1。

![img](/img/v2-d064efa8b4b4cc1d5ee96a6f1e6aab77_720w.jpg)



## 整体总结

有了上面的阐述，我们可以对示例的数据进行整理，得到每个列及其相应的(R, D, V)的值。这个数据模型，既满足了列式存储，又可以有效的恢复原有的数据行。

![img](/img/v2-c497786e0621a81a6a8983444b073f35_720w.jpg)

但是，如果我们将示例数据通过Spark写入到Parquet文件，会发现Parquet文件的Schema信息与我们上面的阐述略有差别，主要表现在：

- 对于sid列，我们期望的是required，而文件Schema里面是optional
- 对于appid与trans，文件Schema在对数组的表达上增加了两层，即.list.element

![img](/img/v2-71de403af721388655a8ab07113740e7_720w.jpg)

通过分析，这两个问题都跟Spark有关。第一个问题，是因为在Spark中定义schema时，将sid字段的nullable设置为true了，导致Spark认为其为optional。对于required类型字段，应该将其置为false。

```text
StructField("sid", StringType(), False)
```

第二个问题，跟Spark的[ParquetWriteSupport](https://link.zhihu.com/?target=https%3A//github.com/apache/spark/blob/master/sql/core/src/main/scala/org/apache/spark/sql/execution/datasources/parquet/ParquetWriteSupport.scala)有关，其在表述Array数据类型时增加了list和element两层，采用了三层关系的方式。根据这个变化，我们对上述的树形图和列值进行了修正，主要变化的是appid和trans下面的D值，对R和V值没有影响。

![img](/img/v2-78bd53ac27110eab91889161183df179_720w.jpg)

![img](/img/v2-a673e3360206641092bb4345a20a7955_720w.jpg)



## 结尾

本文从嵌套结构的特性入手，逐步探讨了Parquet的嵌套数据模型。正如文章开头所言，很多场景下我们最关注的是查询性能，而Parquet只是提供了一种存储方式，具体的查询还要依赖生态圈内的计算引擎，比如Spark、Presto等。其性能通常与相应的计算引擎中的Parquet Reader有关，因为他们决定了能否有效的进行嵌套字段的Column Pruning和Predicate Pushdown Filter。

我们曾经在AWS Athena下做过嵌套数据与扁平数据的查询性能对比，前者比后者差了60多倍以上，主要表现在查询时间和加载的数据量上。AWS Athena底层跑的是Presto，因为是托管服务，我们尚且不知道是Presto的哪个版本，但至少说明这个Presto没有很好的支持嵌套数据查询。Spark在2.4.0之前对嵌套数据查询的支持也很弱。关于这些，我将在后面另起博文来分析Spark和Presto中对嵌套数据查询的支持情况。



（全文完）



\> 本文同步发表在我的博客：[https://bruce.blog.csdn.net/](https://link.zhihu.com/?target=https%3A//bruce.blog.csdn.net/)





# 深入分析Parquet列式存储格式

Parquet是面向分析型业务的列式存储格式，由Twitter和Cloudera合作开发，2015年5月从Apache的孵化器里毕业成为Apache顶级项目，最新的版本是1.8.0。

列式存储

列式存储和行式存储相比有哪些优势呢？

1.可以跳过不符合条件的数据，只读取需要的数据，降低IO数据量。

2.压缩编码可以降低磁盘存储空间。由于同一列的数据类型是一样的，可以使用更高效的压缩编码（例如Run Length Encoding和Delta Encoding）进一步节约存储空间。

3.只读取需要的列，支持向量运算，能够获取更好的扫描性能。

当时Twitter的日增数据量达到压缩之后的100TB+，存储在HDFS上，工程师会使用多种计算框架（例如MapReduce, Hive, Pig等）对这些数据做分析和挖掘；日志结构是复杂的嵌套数据类型，例如一个典型的日志的schema有87列，嵌套了7层。所以需要设计一种列式存储格式，既能支持关系型数据（简单数据类型），又能支持复杂的嵌套类型的数据，同时能够适配多种数据处理框架。

关系型数据的列式存储，可以将每一列的值直接排列下来，不用引入其他的概念，也不会丢失数据。关系型数据的列式存储比较好理解，而嵌套类型数据的列存储则会遇到一些麻烦。如图1所示，我们把嵌套数据类型的一行叫做一个记录（record)，嵌套数据类型的特点是一个record中的column除了可以是Int, Long, String这样的原语（primitive）类型以外，还可以是List, Map, Set这样的复杂类型。在行式存储中一行的多列是连续的写在一起的，在列式存储中数据按列分开存储，例如可以只读取A.B.C这一列的数据而不去读A.E和A.B.D，那么如何根据读取出来的各个列的数据重构出一行记录呢？

![img](/img/804968-02ca6814cc8efae0.png)

图1行式存储和列式存储

Google的[Dremel](https://link.jianshu.com/?t=http://research.google.com/pubs/pub36632.html)系统解决了这个问题，核心思想是使用“record shredding and assembly algorithm”来表示复杂的嵌套数据类型，同时辅以按列的高效压缩和编码技术，实现降低存储空间，提高IO效率，降低上层应用延迟。Parquet就是基于Dremel的数据模型和算法实现的。

[Parquet适配多种计算框架](https://www.jianshu.com/writer)

Parquet是语言无关的，而且不与任何一种数据处理框架绑定在一起，适配多种语言和组件，能够与Parquet配合的组件有：

查询引擎: Hive, Impala,Pig, Presto, Drill, Tajo, HAWQ, IBM Big SQL

计算框架: MapReduce, Spark,Cascading, Crunch, Scalding, Kite

数据模型: Avro, Thrift,Protocol Buffers, POJOs

那么Parquet是如何与这些组件协作的呢？这个可以通过图2来说明。数据从内存到Parquet文件或者反过来的过程主要由以下三个部分组成：

[1,](https://www.jianshu.com/writer)存储格式(storage format)

[parquet-format](https://link.jianshu.com/?t=https://github.com/apache/parquet-format)项目定义了Parquet内部的数据类型、存储格式等。

2,对象模型转换器(object model converters)

这部分功能由[parquet-mr](https://link.jianshu.com/?t=https://github.com/apache/parquet-mr)项目来实现，主要完成外部对象模型与Parquet内部数据类型的映射。

3,对象模型(object models)

对象模型可以简单理解为内存中的数据表示，Avro, Thrift,

Protocol Buffers, Hive SerDe, Pig Tuple, Spark SQL InternalRow等这些都是对象模型。Parquet也提供了一个[example object model](https://link.jianshu.com/?t=https://github.com/Parquet/parquet-mr/tree/master/parquet-column/src/main/java/parquet/example)帮助大家理解。[[s1\]](https://www.jianshu.com/writer#_msocom_1)

例如[parquet-mr](https://link.jianshu.com/?t=https://github.com/apache/parquet-mr)项目里的parquet-pig项目就是负责把内存中的Pig Tuple序列化并按列存储成Parquet格式，以及反过来把Parquet文件的数据反序列化成Pig Tuple。

这里需要注意的是Avro, Thrift, Protocol Buffers都有他们自己的存储格式，但是Parquet并没有使用他们，而是使用了自己在[parquet-format](https://link.jianshu.com/?t=https://github.com/apache/parquet-format)项目里定义的存储格式。所以如果你的应用使用了Avro等对象模型，这些数据序列化到磁盘还是使用的[parquet-mr](https://link.jianshu.com/?t=https://github.com/apache/parquet-mr)定义的转换器把他们转换成Parquet自己的存储格式。

![img](/img/804968-22f5c695b12e25ab.png)

图2 Parquet项目的结构

[Parquet数据模型](https://www.jianshu.com/writer)

理解Parquet首先要理解这个列存储格式的数据模型。我们以一个下面这样的schema和数据为例来说明这个问题。

message AddressBook {

required string owner;

repeated string ownerPhoneNumbers;

repeated group contacts {

required string name;

optional string phoneNumber;

}

}

这个schema中每条记录表示一个人的AddressBook。有且只有一个owner，owner可以有0个或者多个ownerPhoneNumbers，owner可以有0个或者多个contacts。每个contact有且只有一个name，这个contact的phoneNumber可有可无。这个schema可以用图3的树结构来表示。

每个schema的结构是这样的：根叫做message，message包含多个fields。每个field包含三个属性：repetition, type, name。repetition可以是以下三种：required（出现1次），optional（出现0次或者1次），repeated（出现0次或者多次）。type可以是一个group或者一个primitive类型。

Parquet格式的数据类型没有复杂的Map, List, Set等，而是使用repeated fields和groups来表示。例如List和Set可以被表示成一个repeated field，Map可以表示成一个包含有key-value对的repeated field，而且key是required的。

![img](/img/804968-e71432568966ed88.png)

图3 AddressBook的树结构表示

[Parquet文件的存储格式](https://www.jianshu.com/writer)

那么如何把内存中每个AddressBook对象按照列式存储格式存储下来呢？

在Parquet格式的存储中，一个schema的树结构有几个叶子节点，实际的存储中就会有多少column。例如上面这个schema的数据存储实际上有四个column，如图4所示。

![img](/img/804968-364cd8b0f030eed3.png)

图4 AddressBook实际存储的列

Parquet文件在磁盘上的分布情况如图5所示。所有的数据被水平切分成Row

group，一个Row group包含这个Row

group对应的区间内的所有列的column chunk。一个column

chunk负责存储某一列的数据，这些数据是这一列的Repetition levels, Definition levels和values（详见后文）。一个column

chunk是由Page组成的，Page是压缩和编码的单元，对数据模型来说是透明的。一个Parquet文件最后是Footer，存储了文件的元数据信息和统计信息。Row group是数据读写时候的缓存单元，所以推荐设置较大的Row

group从而带来较大的并行度，当然也需要较大的内存空间作为代价。一般情况下推荐配置一个Row group大小1G，一个HDFS块大小1G，一个HDFS文件只含有一个块[[s2\]](https://www.jianshu.com/writer#_msocom_2)。

![img](/img/804968-311d56ab95197ea5.png)

图5 Parquet文件格式在磁盘的分布

拿我们的这个schema为例，在任何一个Row group内，会顺序存储四个column chunk。这四个column都是string类型。这个时候Parquet就需要把内存中的AddressBook对象映射到四个string类型的column中。如果读取磁盘上的4个column要能够恢复出AddressBook对象。这就用到了我们前面提到的“record shredding

and assembly algorithm”。

[Striping/Assembly算法](https://www.jianshu.com/writer)

对于嵌套数据类型，我们除了存储数据的value之外还需要两个变量Repetition Level(R),

Definition Level(D)才能存储其完整的信息用于序列化和反序列化嵌套数据类型。Repetition Level和Definition Level可以说是为了支持嵌套类型而设计的，但是它同样适用于简单数据类型。在Parquet中我们只需定义和存储schema的叶子节点所在列的Repetition Level和Definition Level。

Definition Level

嵌套数据类型的特点是有些field可以是空的，也就是没有定义。如果一个field是定义的，那么它的所有的父节点都是被定义的。从根节点开始遍历，当某一个field的路径上的节点开始是空的时候我们记录下当前的深度作为这个field的Definition

Level。如果一个field的Definition

Level等于这个field的最大Definition

Level就说明这个field是有数据的。对于required类型的field必须是有定义的，所以这个Definition

Level是不需要的。在关系型数据中，optional类型的field被编码成0表示空和1表示非空（或者反之）。

Repetition Level

记录该field的值是在哪一个深度上重复的。只有repeated类型的field需要Repetition Level，optional和required类型的不需要。Repetition

Level = 0表示开始一个新的record。在关系型数据中，repetion level总是[0](https://www.jianshu.com/writer)[[s3\]](https://www.jianshu.com/writer#_msocom_3)。

下面用AddressBook的例子来说明Striping和assembly的过程。

对于每个column的最大的Repetion Level和Definition Level如图6所示。

![img](/img/804968-56565364542f7d78.png)

图6 AddressBook的Max Definition Level和Max RepetitionLevel

下面这样两条record：

AddressBook {

owner: "Julien Le Dem",

ownerPhoneNumbers: "555 123 4567",

ownerPhoneNumbers: "555 666 1337",

contacts: {

name: "Dmitriy Ryaboy",

phoneNumber: "555 987 6543",

},

contacts: {

name: "Chris Aniszczyk"

}

}

AddressBook {

owner: "A. Nonymous"

}

以contacts.phoneNumber这一列为例，"555 987 6543"这个contacts.phoneNumber的Definition Level是最大Definition Level=2。而如果一个contact没有phoneNumber，那么它的Definition Level就是1。如果连contact都没有，那么它的Definition Level就是0。

下面我们拿掉其他三个column只看contacts.phoneNumber这个column，把上面的两条record简化成下面的样子：

AddressBook {

contacts: {

phoneNumber: "555 987 6543"

}

contacts: {

}

}

AddressBook {

}

这两条[记录的序列化过程](https://www.jianshu.com/writer)[[s4\]](https://www.jianshu.com/writer#_msocom_4)如图7所示：

![img](/img/804968-b5ca71fc76300476.png)

图7一条记录的序列化过程

如果我们要把这个column写到磁盘上，磁盘上会写入这样的数据（图8）：

![img](/img/550.png)

图8一条记录的磁盘存储

注意：NULL实际上不会被存储，如果一个column value的Definition Level小于该column最大Definition Level的话，那么就表示这是一个空值。

下面是从磁盘上读取数据并反序列化成AddressBook对象的过程：

1，读取第一个三元组R=0, D=2, Value=”555 987 6543[[s5\]](https://www.jianshu.com/writer#_msocom_5)”

R=0表示是一个新的record，要根据schema创建一个新的nested record直到Definition

Level=2。

D=2说明Definition Level=Max Definition Level，那么这个Value就是contacts.phoneNumber这一列的值，赋值操作contacts.phoneNumber=”555 987 6543”。

2，读取第二个三元组R=1, D=1

R=1表示不是一个新的record，是上一个record中一个新的contacts。

D=1表示contacts定义了，但是contacts的下一个级别也就是phoneNumber没有被定义，所以创建一个空的contacts。

3，读取第三个三元组R=0, D=0

R=0表示一个新的record，根据schema创建一个新的nested record直到Definition

Level=0，也就是创建一个AddressBook根节点。

可以看出在Parquet列式存储中，对于一个schema的所有叶子节点会被当成column存储，而且叶子节点一定是primitive类型的数据。对于这样一个primitive类型的数据会衍生出三个sub columns (R, D, Value)，也就是从逻辑上看除了数据本身以外会存储大量的Definition Level和Repetition Level。那么这些Definition Level和Repetition Level是否会带来额外的存储开销呢？实际上这部分额外的存储开销是可以忽略的。因为对于一个schema来说level都是有上限的，而且非repeated类型的field不需要Repetition Level，required类型的field不需要Definition Level，也可以缩短这个上限。例如对于Twitter的7层嵌套的schema来说，只需要3个bits就可以表示这两个Level了。

对于存储关系型的record，record中的元素都是非空的（NOT NULL in SQL）。Repetion Level和Definition Level都是0，所以这两个sub column就完全不需要存储了。所以在存储非嵌套类型的时候，Parquet格式也是一样高效的。

上面演示了一个column的写入和重构，那么在不同column之间是怎么跳转的呢，这里用到了有限状态机的知识，详细介绍可以参考[Dremel](https://link.jianshu.com/?t=http://research.google.com/pubs/pub36632.html)。

[数据压缩算法](https://www.jianshu.com/writer)

列式存储给数据压缩也提供了更大的发挥空间，除了我们常见的snappy, gzip等压缩方法以外，由于列式存储同一列的数据类型是一致的，所以可以使用更多的压缩算法。

压缩算法

使用场景

Run Length Encoding

重复数据

Delta Encoding

有序数据集，例如timestamp，自动生成的ID，以及监控的各种metrics

Dictionary Encoding

小规模的数据集合，例如IP地址

Prefix Encoding

Delta Encoding for strings

[性能](https://www.jianshu.com/writer)

Parquet列式存储带来的性能上的提高在业内已经得到了充分的认可，特别是当你们的表非常宽（column非常多）的时候，Parquet无论在资源利用率还是性能上都优势明显。具体的性能指标详见参考文档。

Spark已经将Parquet设为默认的文件存储格式，Cloudera投入了很多工程师到Impala+Parquet相关开发中，Hive/Pig都原生支持Parquet。Parquet现在为Twitter至少节省了1/3的存储空间，同时节省了大量的表扫描和反序列化的时间。这两方面直接反应就是节约成本和提高性能。

如果说HDFS是大数据时代文件系统的事实标准的话，Parquet就是大数据时代存储格式的事实标准。

作者：时待吾
链接：https://www.jianshu.com/p/b823c727fe46
