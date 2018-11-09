---
layout:     post
title:     Mesos:Digging Deeper Into Apache Mesos（转）
subtitle:   Digging Deeper Into Apache Mesos
date:       2018-09-25
author:     老张
header-img: img/post-bg-2015.jpg
catalog: true
tags:
    - MESOS
    - RESOURCE
typora-copy-images-to: ../img
typora-root-url: ..
---

## What is HBase?

HBase is a distributed column-oriented database built on top of the Hadoop file system. It is an open-source project and is horizontally scalable.

HBase is a data model that is similar to Google’s big table designed to provide quick random access to huge amounts of structured data. It leverages the fault tolerance provided by the Hadoop File System (HDFS).

It is a part of the Hadoop ecosystem that provides random real-time read/write access to data in the Hadoop File System.

One can store the data in HDFS either directly or through HBase. Data consumer reads/accesses the data in HDFS randomly using HBase. HBase sits on top of the Hadoop File System and provides read and write access.



HBase是一个开源可伸缩的针对海量数据存储的分布式nosql数据库，它根据Google Bigtable数据模型来建模并构建在hadoop的hdfs存储系统之上。它和关系型数据库Mysql, Oracle等有明显的区别，HBase的数据模型牺牲了关系型数据库的一些特性但是却换来了极大的可伸缩性和对表结构的灵活操作。  在一定程度上，Hbase又可以看成是以行键(Row Key),列标识(column qualifier),时间戳(timestamp)标识的有序Map数据结构的数据库，具有稀疏，分布式，持久化，多维度等特点。 





**HBase的数据模型介绍**

 

HBase的数据模型也是由一张张的表组成，每一张表里也有数据行和列，但是在HBase数据库中的行和列又和关系型数据库的稍有不同。下面统一介绍HBase数据模型中一些名词的概念:

 

​      

 

​         表(Table): HBase会将数据组织进一张张的表里面，但是需要注意的是表名必须是能用在文件路径里的合法名字，因为HBase的表是映射成hdfs上面的文件。

 

 

​         行(Row): 在表里面，每一行代表着一个数据对象，每一行都是以一个行键（Row Key）来进行唯一标识的，行键并没有什么特定的数据类型，以二进制的字节来存储。

 

 

​         列族(Column Family): 在定义HBase表的时候需要提前设置好列族, 表中所有的列都需要组织在列族里面，列族一旦确定后，就不能轻易修改，因为它会影响到HBase真实的物理存储结构，但是列族中的列标识(Column Qualifier)以及其对应的值可以动态增删。表中的每一行都有相同的列族，但是不需要每一行的列族里都有一致的列标识(Column Qualifier)和值，所以说是一种稀疏的表结构，这样可以一定程度上避免数据的冗余。例如：{row1, userInfo: telephone —> 137XXXXX869 }{row2, userInfo: fax phone —> 0898-66XXXX } 行1和行2都有同一个列族userinfo，但是行1中的列族只有列标识(Column Qualifier):移动电话号码，而行2中的列族中只有列标识(Column Qualifier):传真号码。

 

 

​         列标识(Column Qualifier): 列族中的数据通过列标识来进行映射，其实这里大家可以不用拘泥于“列”这个概念，也可以理解为一个键值对,Column Qualifier就是Key。列标识也没有特定的数据类型，以二进制字节来存储。

 

 

​         单元(Cell): 每一个 行键，列族和列标识共同组成一个单元，存储在单元里的数据称为单元数据，单元和单元数据也没有特定的数据类型，以二进制字节来存储。

 

 

​         时间戳(Timestamp): 默认下每一个单元中的数据插入时都会用时间戳来进行版本标识。读取单元数据时，如果时间戳没有被指定，则默认返回最新的数据，写入新的单元数据时，如果没有设置时间戳，默认使用当前时间。每一个列族的单元数据的版本数量都被HBase单独维护，默认情况下HBase保留3个版本数据。



![img](/img/20160425203317625.jpg) 

## Multidimensional sorted Map

A Map (sometimes called and associative array) is a collection where the index of what is being stored does not have to be an integer but can also be arbitrary string.  It is a collection of Key/Value pairs where the key is unique.  The Keys are sorted in lexicographical order. (Not alphabetical, nor Alphanumeric, but sorting on the Unicode value of the string)



![img](/img/20160425203414834.jpg) 



## HBase and HDFS

| HDFS                                                         | HBase                                                        |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| HDFS is a distributed file system suitable for storing large files. | HBase is a database built on top of the HDFS.                |
| HDFS does not support fast individual record lookups.        | HBase provides fast lookups for larger tables.               |
| It provides high latency batch processing; no concept of batch processing. | It provides low latency access to single rows from billions of records (Random access). |
| It provides only sequential access of data.                  | HBase internally uses Hash tables and provides random access, and it stores the data in indexed HDFS files for faster lookups. |