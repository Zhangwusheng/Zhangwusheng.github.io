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