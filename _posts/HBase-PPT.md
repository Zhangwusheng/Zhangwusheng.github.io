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





### HBase 資料模型

如 Bigtable 的論文所述，Bigtable 是一種稀疏（Sparse）、分散式（Distributed）、 持久的多維排序映射（Persistent Multidimensional Sorted Map），由列鍵（Row Key）、行鍵（Column Key）和時間戳（Timestamp）作為索引。

*※ 台灣在 Row 與 Column的翻譯與中國有所差異，請參考*[*兩岸線性代數用詞參照*](https://ccjou.wordpress.com/2012/04/17/%E5%85%A9%E5%B2%B8%E7%B7%9A%E6%80%A7%E4%BB%A3%E6%95%B8%E7%9A%84%E7%BF%BB%E8%AD%AF%E5%90%8D%E8%A9%9E%E5%8F%83%E7%85%A7/)

有人稱 HBase 為鍵值儲存（key-value store）、行族導向資料庫（Column-Family-Oriented Database）或是儲存多時間戳的版本映射的資料處（Database storing versioned maps of maps）。

最原始簡單來描述 HBase 資料模型的方式就是它由行與列的表格所組成。就如同我們在關聯式資料庫所熟悉的，這是它們兩者之間的相似性，但事實上它們對行與列的概念有些不同。

- **表格（Table）**

HBase 將資料組織成表格，表名由能用在文件路徑裡的字串組成。

- **列（Row）**

在表格中，資料根據其列儲存，每一列由列鍵唯一標識。列鍵相當於關聯式資料庫中的主鍵（Primary Key），在創建表格時就已設定。

列鍵不具資料形態，始終視為 byte[ ] (byte array)。

- **行族（Column Family）**

列中的資料由行族分組。行族也同樣影響 HBase 的物理儲存結構，因此它們必須被提前設置，且不易修改。

表格中的每一列都具相同的行族，但行族中的每一列不一定要有資料儲存（HBase 的稀疏性）。

行族名稱由能用在文件路徑裡的字串組成。

- **行限定符（Column Qualifier）**

行族中的資料通過行限定符來映射搜尋。行限定符不需要提前設置，一旦確定行族後，由於行族會影響儲存結構，所以不能輕易修改，但行限定符及其對應的值可以動態增刪。

表格中的每一列都具相同的行族，但不需要在每一列保持一致的行限定符及值。

行鍵同樣不具資料形態，始終視為 byte[ ] (byte array)。

- **單元（Cell）**

單元為列族、行族及行限定符的唯一組合。儲存於單元格的資料稱為單元格的值。

其值不具資料形態，同樣視為 byte[ ] (byte array)。

- **時間戳（Timestamp）**

預設下，每一個插入單元的資料都會以時間戳來辨識其版本。寫入時，如未指定時間戳，預設使用當前時間。讀取時，如果沒有指定時間戳，則使用最新版本的時間戳，HBase 也支援指定多個版本做為查詢。

HBase 會保留每個行族的單元版本數量。預設為每個單元保存 3 個時間戳。

![img](/img/1-FmorMEoZOSsHI0216pOtHg.png)

A slice of an example table that stores Web pages

![img](/img/1-8YZfCK70etM1OKirYY71wg.jpeg)

A Table in HBase

HBase 的 API 包含三個主要的資料操作：Get、Put 和 Scan 。

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

有時候，你可以將 HBase 的資料模型視為一個多維映射的模型，下列圖 2 將 圖 1 中的第一列視為多維映射： 

A Map (sometimes called and associative array) is a collection where the index of what is being stored does not have to be an integer but can also be arbitrary string.  It is a collection of Key/Value pairs where the key is unique.  The Keys are sorted in lexicographical order. (Not alphabetical, nor Alphanumeric, but sorting on the Unicode value of the string)



![img](/img/20160425203414834.jpg) 

![Table](/img/table.jpg) 

## HBase and HDFS

| HDFS                                                         | HBase                                                        |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| HDFS is a distributed file system suitable for storing large files. | HBase is a database built on top of the HDFS.                |
| HDFS does not support fast individual record lookups.        | HBase provides fast lookups for larger tables.               |
| It provides high latency batch processing; no concept of batch processing. | It provides low latency access to single rows from billions of records (Random access). |
| It provides only sequential access of data.                  | HBase internally uses Hash tables and provides random access, and it stores the data in indexed HDFS files for faster lookups. |

<<<<<<< HEAD




NOnce机制
=======
## HBase Architectural Components

Physically, HBase is composed of three types of servers in a master slave type of architecture. Region servers serve data for reads and writes. When accessing data, clients communicate with HBase RegionServers directly. Region assignment, DDL (create, delete tables) operations are handled by the HBase Master process. Zookeeper, which is part of HDFS, maintains a live cluster state.

The Hadoop DataNode stores the data that the Region Server is managing. All HBase data is stored in HDFS files. Region Servers are collocated with the HDFS DataNodes, which enable data locality (putting the data close to where it is needed) for the data served by the RegionServers. HBase data is local when it is written, but when a region is moved, it is not local until compaction.

The NameNode maintains metadata information for all the physical data blocks that comprise the files.

![img](/img/HBaseArchitecture-Blog-Fig1.png)

## Regions

HBase Tables are divided horizontally by row key range into “Regions.” A region contains all rows in the table between the region’s start key and end key. Regions are assigned to the nodes in the cluster, called “Region Servers,” and these serve data for reads and writes. A region server can serve about 1,000 regions.

![img](/img/HBaseArchitecture-Blog-Fig2.png)

## HBase HMaster

Region assignment, DDL (create, delete tables) operations are handled by the HBase Master.

A master is responsible for:

- Coordinating the region servers

  \- Assigning regions on startup , re-assigning regions for recovery or load balancing

  \- Monitoring all RegionServer instances in the cluster (listens for notifications from zookeeper)

- Admin functions

  \- Interface for creating, deleting, updating tables

![img](/img/HBaseArchitecture-Blog-Fig3.png)

## ZooKeeper: The Coordinator

HBase uses ZooKeeper as a distributed coordination service to maintain server state in the cluster. Zookeeper maintains which servers are alive and available, and provides server failure notification. Zookeeper uses consensus to guarantee common shared state. Note that there should be three or five machines for consensus.

![img](/img/HBaseArchitecture-Blog-Fig4.png)

## How the Components Work Together

Zookeeper is used to coordinate shared state information for members of distributed systems. Region servers and the active HMaster connect with a session to ZooKeeper. The ZooKeeper maintains ephemeral nodes for active sessions via heartbeats.

![img](/img/HBaseArchitecture-Blog-Fig5.png)

Each Region Server creates an ephemeral node. The HMaster monitors these nodes to discover available region servers, and it also monitors these nodes for server failures. HMasters vie （竞争）to create an ephemeral node. Zookeeper determines the first one and uses it to make sure that only one master is active. The active HMaster sends heartbeats to Zookeeper, and the inactive HMaster listens for notifications of the active HMaster failure.

If a region server or the active HMaster fails to send a heartbeat, the session is expired and the corresponding ephemeral node is deleted. Listeners for updates will be notified of the deleted nodes. The active HMaster listens for region servers, and will recover region servers on failure. The Inactive HMaster listens for active HMaster failure, and if an active HMaster fails, the inactive HMaster becomes active.

从上面一段话，我们可以看出，ZK的会话的超时时间设置，对集群的稳定性有很大的影响。

## HBase First Read or Write

There is a special HBase Catalog table called the META table, which holds the location of the regions in the cluster. ZooKeeper stores the location of the META table.

This is what happens the first time a client reads or writes to HBase:

1. The client gets the Region server that hosts the META table from ZooKeeper.
2. The client will query the .META. server to get the region server corresponding to the row key it wants to access. The client caches this information along with the META table location.
3. It will get the Row from the corresponding Region Server.

For future reads, the client uses the cache to retrieve the META location and previously read row keys. Over time, it does not need to query the META table, unless there is a miss because a region has moved; then it will re-query and update the cache.

![img](/img/HBaseArchitecture-Blog-Fig6.png)

## HBase Meta Table

- This META table is an HBase table that keeps a list of all regions in the system.

- The .META. table is like a b tree.

- The .META. table structure is as follows:

  \- Key: region start key,region id

  \- Values: RegionServer

![img](/img/HBaseArchitecture-Blog-Fig7.png)

## Region Server Components

A Region Server runs on an HDFS data node and has the following components:

- WAL: Write Ahead Log is a file on the distributed file system. The WAL is used to store new data that hasn't yet been persisted to permanent storage; it is used for recovery in the case of failure.
- BlockCache: is the read cache. It stores frequently read data in memory. Least Recently Used data is evicted when full.
- MemStore: is the write cache. It stores new data which has not yet been written to disk. It is sorted before writing to disk. There is one MemStore per column family per region.
- Hfiles store the rows as sorted KeyValues on disk.

![img](/img/HBaseArchitecture-Blog-Fig8.png)

## HBase Write Steps (1)

When the client issues a Put request, the first step is to write the data to the write-ahead log, the WAL:

\- Edits are appended to the end of the WAL file that is stored on disk.

\- The WAL is used to recover not-yet-persisted data in case a server crashes.

![img](/img/HBaseArchitecture-Blog-Fig9.png)

## HBase Write Steps (2)

Once the data is written to the WAL, it is placed in the MemStore. Then, the put request acknowledgement returns to the client.

![img](/img/HBaseArchitecture-Blog-Fig10.png)

## HBase MemStore

The MemStore stores updates in memory as sorted KeyValues, the same as it would be stored in an HFile. There is one MemStore per column family. The updates are sorted per column family.

![img](/img/HBaseArchitecture-Blog-Fig11.png)

## HBase Region Flush

When the MemStore accumulates enough data, the entire sorted set is written to a new HFile in HDFS. HBase uses multiple HFiles per column family, which contain the actual cells, or KeyValue instances. These files are created over time as KeyValue edits sorted in the MemStores are flushed as files to disk.

Note that this is one reason why there is a limit to the number of column families in HBase. There is one MemStore per CF; when one is full, they all flush. It also saves the last written sequence number so the system knows what was persisted so far.

The highest sequence number is stored as a meta field in each HFile, to reflect where persisting has ended and where to continue. On region startup, the sequence number is read, and the highest is used as the sequence number for new edits.

![img](/img/HBaseArchitecture-Blog-Fig12.png)

## HBase HFile

Data is stored in an HFile which contains sorted key/values. When the MemStore accumulates enough data, the entire sorted KeyValue set is written to a new HFile in HDFS. This is a sequential write. It is very fast, as it avoids moving the disk drive head.

![img](/img/HBaseArchitecture-Blog-Fig13.png)

## HBase HFile Structure

An HFile contains a multi-layered index which allows HBase to seek to the data without having to read the whole file. The multi-level index is like a b+tree:

- Key value pairs are stored in increasing order
- Indexes point by row key to the key value data in 64KB “blocks”
- Each block has its own leaf-index
- The last key of each block is put in the intermediate index
- The root index points to the intermediate index

The trailer points to the meta blocks, and is written at the end of persisting the data to the file. The trailer also has information like bloom filters and time range info. Bloom filters help to skip files that do not contain a certain row key. The time range info is useful for skipping the file if it is not in the time range the read is looking for.

![img](/img/HBaseArchitecture-Blog-Fig14.png)

## HFile Index

The index, which we just discussed, is loaded when the HFile is opened and kept in memory. This allows lookups to be performed with a single disk seek.

![img](/img/HBaseArchitecture-Blog-Fig15.png)

## HBase Read Merge

We have seen that the KeyValue cells corresponding to one row can be in multiple places, row cells already persisted are in Hfiles, recently updated cells are in the MemStore, and recently read cells are in the Block cache. So when you read a row, how does the system get the corresponding cells to return? A Read merges Key Values from the block cache, MemStore, and HFiles in the following steps:

1. First, the scanner looks for the Row cells in the Block cache - the read cache. Recently Read Key Values are cached here, and Least Recently Used are evicted when memory is needed.
2. Next, the scanner looks in the MemStore, the write cache in memory containing the most recent writes.
3. If the scanner does not find all of the row cells in the MemStore and Block Cache, then HBase will use the Block Cache indexes and bloom filters to load HFiles into memory, which may contain the target row cells.

![img](/img/HBaseArchitecture-Blog-Fig16.png)

## HBase Read Merge

As discussed earlier, there may be many HFiles per MemStore, which means for a read, multiple files may have to be examined, which can affect the performance. This is called read amplification.

![img](/img/HBaseArchitecture-Blog-Fig17.png)

## HBase Minor Compaction

HBase will automatically pick some smaller HFiles and rewrite them into fewer bigger Hfiles. This process is called minor compaction. Minor compaction reduces the number of storage files by rewriting smaller files into fewer but larger ones, performing a merge sort.

![img](/img/HBaseArchitecture-Blog-Fig18.png)

## HBase Major Compaction

Major compaction merges and rewrites all the HFiles in a region to one HFile per column family, and in the process, drops deleted or expired cells. This improves read performance; however, since major compaction rewrites all of the files, lots of disk I/O and network traffic might occur during the process. This is called write amplification.

Major compactions can be scheduled to run automatically. Due to write amplification, major compactions are usually scheduled for weekends or evenings. Note that MapR-DB has made improvements and does not need to do compactions. A major compaction also makes any data files that were remote, due to server failure or load balancing, local to the region server.

![img](/img/HBaseArchitecture-Blog-Fig19.png)

## Region = Contiguous Keys

Let’s do a quick review of regions:

- A table can be divided horizontally into one or more regions. A region contains a contiguous, sorted range of rows between a start key and an end key
- Each region is 1GB in size (default)
- A region of a table is served to the client by a RegionServer
- A region server can serve about 1,000 regions (which may belong to the same table or different tables)

![img](/img/HBaseArchitecture-Blog-Fig20.png)

## Region Split

Initially there is one region per table. When a region grows too large, it splits into two child regions. Both child regions, representing one-half of the original region, are opened in parallel on the same Region server, and then the split is reported to the HMaster. For load balancing reasons, the HMaster may schedule for new regions to be moved off to other servers.

![img](/img/HBaseArchitecture-Blog-Fig21.png)

## Read Load Balancing

Splitting happens initially on the same region server, but for load balancing reasons, the HMaster may schedule for new regions to be moved off to other servers. This results in the new Region server serving data from a remote HDFS node until a major compaction moves the data files to the Regions server’s local node. HBase data is local when it is written, but when a region is moved (for load balancing or recovery), it is not local until major compaction.

![img](/img/HBaseArchitecture-Blog-Fig22.png)

## HDFS Data Replication

All writes and Reads are to/from the primary node. HDFS replicates the WAL and HFile blocks. HFile block replication happens automatically. HBase relies on HDFS to provide the data safety as it stores its files. When data is written in HDFS, one copy is written locally, and then it is replicated to a secondary node, and a third copy is written to a tertiary node.

![img](/img/HBaseArchitecture-Blog-Fig23.png)

## HDFS Data Replication (2)

The WAL file and the Hfiles are persisted on disk and replicated, so how does HBase recover the MemStore updates not persisted to HFiles? See the next section for the answer.

![img](/img/HBaseArchitecture-Blog-Fig24.png)

## HBase Crash Recovery

When a RegionServer fails, Crashed Regions are unavailable until detection and recovery steps have happened. Zookeeper will determine Node failure when it loses region server heart beats. The HMaster will then be notified that the Region Server has failed.

When the HMaster detects that a region server has crashed, the HMaster reassigns the regions from the crashed server to active Region servers. In order to recover the crashed region server’s memstore edits that were not flushed to disk. The HMaster splits the WAL belonging to the crashed region server into separate files and stores these file in the new region servers’ data nodes. Each Region Server then replays the WAL from the respective split WAL, to rebuild the memstore for that region.

![img](/img/HBaseArchitecture-Blog-Fig25.png)

## Data Recovery

WAL files contain a list of edits, with one edit representing a single put or delete. Edits are written chronologically, so, for persistence, additions are appended to the end of the WAL file that is stored on disk.

What happens if there is a failure when the data is still in memory and not persisted to an HFile? The WAL is replayed. Replaying a WAL is done by reading the WAL, adding and sorting the contained edits to the current MemStore. At the end, the MemStore is flush to write changes to an HFile.

![img](/img/HBaseArchitecture-Blog-Fig26.png)

## Apache HBase Architecture Benefits

HBase provides the following benefits:

- **Strong consistency model**

  \- When a write returns, all readers will see same value

- **Scales automatically**

  \- Regions split when data grows too large

  \- Uses HDFS to spread and replicate data

- **Built-in recovery**

  \- Using Write Ahead Log (similar to journaling on file system)

- **Integrated with Hadoop**

  \- MapReduce on HBase is straightforward









# Apache HBase Region Splitting and Merging

作者：[Enis Soztutar](https://zh.hortonworks.com/blog/author/enis/)                         

https://zh.hortonworks.com/blog/apache-hbase-region-splitting-and-merging/

​                         [![img](https://2xbbhjxc6wk3v21p62t8n4d4-wpengine.netdna-ssl.com/wp-content/themes/hortonworks/images/rss.png)](https://zh.hortonworks.com/blog/apache-hbase-region-splitting-and-merging/feed/?withoutcomments=1)                     

​                                     

For this post, we take a technical  deep-dive into one of the core areas of HBase. Specifically, we will  look at how Apache HBase distributes load through regions, and manages  region splitting. HBase stores rows of data in tables. Tables are split  into chunks of rows called “regions”. Those regions are distributed  across the cluster, hosted and made available to client processes by the  RegionServer process. A region is a continuous range within the key  space, meaning all rows in the table that sort between the region’s  start key and end key are stored in the same region. Regions are  non-overlapping, i.e. a single row key belongs to exactly one region at  any point in time. A region is only served by a single region server at  any point in time, which is how HBase guarantees strong consistency  within a single row#. Together with the -ROOT- and .META. regions, a  table’s regions effectively form a 3 level B-Tree for the purposes of  locating a row within a table.

A Region in turn, consists of many “[Stores](http://hbase.apache.org/book/regions.arch.html#store)”,  which correspond to column families. A store contains one memstore and  zero or more store files. The data for each column family is stored and  accessed separately.

A table typically consists of many regions, which are in turn hosted  by many region servers. Thus, regions are the physical mechanism used to  distribute the write and query load across region servers. When a table  is first created, HBase, by default, will allocate only one region for  the table. This means that initially, all requests will go to a single  region server, regardless of the number of region servers. This is the  primary reason why initial phases of loading data into an empty table  cannot utilize the whole capacity of the cluster.

### Pre-splitting

The reason HBase creates only one region for the table is that it  cannot possibly know how to create the split points within the row key  space. Making such decisions is based highly on the distribution of the  keys in your data. Rather than taking a guess and leaving you to deal  with the consequences, HBase does provide you with tools to manage this  from the client. With a process called pre-splitting, you can create a  table with many regions by supplying the split points at the table  creation time. Since pre-splitting will ensure that the initial load is  more evenly distributed throughout the cluster, you should always  consider using it if you know your key distribution beforehand. However,  pre-splitting also has a risk of creating regions, that do not truly  distribute the load evenly because of data skew, or in the presence of  very hot or large rows. If the initial set of region split points is  chosen poorly, you may end up with heterogeneous load distribution,  which will in turn limit your clusters performance.

There is no short answer for the optimal number of regions for a  given load, but you can start with a lower multiple of the number of  region servers as number of splits, then let automated splitting take  care of the rest.

One issue with pre-splitting is calculating the split points for the table. You can use the [RegionSplitter](http://hbase.apache.org/apidocs/org/apache/hadoop/hbase/util/RegionSplitter.html) utility. RegionSplitter creates the split points, by using a pluggable [SplitAlgorithm](http://hbase.apache.org/apidocs/org/apache/hadoop/hbase/util/RegionSplitter.SplitAlgorithm.html). [HexStringSplit](http://hbase.apache.org/apidocs/org/apache/hadoop/hbase/util/RegionSplitter.HexStringSplit.html) and [UniformSplit](http://hbase.apache.org/apidocs/org/apache/hadoop/hbase/util/RegionSplitter.UniformSplit.html)  are two predefined algorithms. The former can be used if the row keys  have a prefix for hexadecimal strings (like if you are using hashes as  prefixes). The latter divides up the key space evenly assuming they are  random byte arrays. You can also implement your custom SplitAlgorithm  and use it from the RegionSplitter utility.

```
$ hbase org.apache.hadoop.hbase.util.RegionSplitter test_table HexStringSplit -c 10 -f f1
```

where -c 10, specifies the requested number of regions as 10, and -f  specifies the column families you want in the table, separated by “:”.  The tool will create a table named “test_table” with 10 regions:

```
13/01/18 18:49:32 DEBUG hbase.HRegionInfo: Current INFO from scan results = {NAME => 'test_table,,1358563771069.acc1ad1b7962564fc3a43e5907e8db33.', STARTKEY => '', ENDKEY => '19999999', ENCODED => acc1ad1b7962564fc3a43e5907e8db33,}
13/01/18 18:49:32 DEBUG hbase.HRegionInfo: Current INFO from scan results = {NAME => 'test_table,19999999,1358563771096.37ec12df6bd0078f5573565af415c91b.', STARTKEY => '19999999', ENDKEY => '33333332', ENCODED => 37ec12df6bd0078f5573565af415c91b,}
...
```

If you have split points at hand, you can also use the HBase shell, to create the table with the desired split points.

```
hbase(main):015:0> create 'test_table', 'f1', SPLITS=> ['a', 'b', 'c']
```

or

```
$ echo -e  "a\nb\nc" >/tmp/splits
hbase(main):015:0> create 'test_table', 'f1', SPLITSFILE=>'/tmp/splits'
```

For optimum load distribution, you should think about your data  model, and key distribution for choosing the correct split algorithm or  split points. Regardless of the method you chose to create the table  with pre determined number of regions, you can now start loading the  data into the table, and see that the load is distributed throughout  your cluster. You can let automated splitting take over once data ingest  starts, and continuously monitor the total number of regions for the  table.

### Auto splitting

Regardless of whether pre-splitting is used or not, once a region  gets to a certain limit, it is automatically split into two regions. If  you are using HBase 0.94 (which comes with [HDP-1.2](https://zh.hortonworks.com/products/hortonworksdataplatform/)), you can configure when HBase decides to split a region, and how it calculates the split points via the pluggable [RegionSplitPolicy](http://hbase.apache.org/apidocs/org/apache/hadoop/hbase/regionserver/RegionSplitPolicy.html) API. There are a couple predefined region split policies: [ConstantSizeRegionSplitPolicy](http://hbase.apache.org/apidocs/org/apache/hadoop/hbase/regionserver/ConstantSizeRegionSplitPolicy.html), [IncreasingToUpperBoundRegionSplitPolicy](http://hbase.apache.org/apidocs/org/apache/hadoop/hbase/regionserver/IncreasingToUpperBoundRegionSplitPolicy.html), and [KeyPrefixRegionSplitPolicy](http://hbase.apache.org/apidocs/org/apache/hadoop/hbase/regionserver/KeyPrefixRegionSplitPolicy.html).

The first one is the default and only split policy for HBase versions  before 0.94. It splits the regions when the total data size for one of  the stores (corresponding to a column-family) in the region gets bigger  than configured “hbase.hregion.max.filesize”, which has a default value  of 10GB. This split policy is ideal in cases, where you are have done  pre-splitting, and are interested in getting lower number of regions per  region server.

The default split policy for HBase 0.94 and trunk is  IncreasingToUpperBoundRegionSplitPolicy, which does more aggressive  splitting based on the number of regions hosted in the same region  server. The split policy uses the max store file size based on Min (R^2 *  “hbase.hregion.memstore.flush.size”, “hbase.hregion.max.filesize”),  where R is the number of regions of the same table hosted on the same  regionserver. So for example, with the default memstore flush size of  128MB and the default max store size of 10GB, the first region on the  region server will be split just after the first flush at 128MB. As  number of regions hosted in the region server increases, it will use  increasing split sizes: 512MB, 1152MB, 2GB, 3.2GB, 4.6GB, 6.2GB, etc.  After reaching 9 regions, the split size will go beyond the configured  “hbase.hregion.max.filesize”, at which point, 10GB split size will be  used from then on. For both of these algorithms, regardless of when  splitting occurs, the split point used is the rowkey that corresponds to  the mid point in the “[block index](http://hbase.apache.org/book/apes03.html#d2145e11930)” for the largest store file in the largest store.

KeyPrefixRegionSplitPolicy is a curious addition to the HBase  arsenal. You can configure the length of the prefix for your row keys  for grouping them, and this split policy ensures that the regions are  not split in the middle of a group of rows having the same prefix. If  you have set prefixes for your keys, then you can use this split policy  to ensure that rows having the same rowkey prefix always end up in the  same region. This grouping of records is sometimes referred to as “[Entity Groups](http://www.cidrdb.org/cidr2011/Papers/CIDR11_Paper32.pdf)” or “[Row Groups](http://www.cs.ucsb.edu/~sudipto/papers/socc10-das.pdf)”. This is a key feature when considering use of the “[local transactions](https://issues.apache.org/jira/browse/HBASE-5229)” ([alternative link](http://hadoop-hbase.blogspot.com/2012_02_01_archive.html)) feature in your application design.

You can configure the default split policy to be used by setting the  configuration “hbase.regionserver.region.split.policy”, or by  configuring the table descriptor. For you brave souls, you can also  implement your own custom split policy, and plug that in at table  creation time, or by modifying an existing table:

```
HTableDescriptor tableDesc = new HTableDescriptor("example-table");
tableDesc.setValue(HTableDescriptor.SPLIT_POLICY, AwesomeSplitPolicy.class.getName());
//add columns etc
admin.createTable(tableDesc);
```

If you are doing pre-splitting, and want to manually manage region  splits, you can also disable region splits, by setting  “hbase.hregion.max.filesize” to a high number and setting the split  policy to ConstantSizeRegionSplitPolicy. However, you should use a  safeguard value of like 100GB, so that regions does not grow beyond a  region server’s capabilities. You can consider disabling automated  splitting and rely on the initial set of regions from pre-splitting for  example, if you are using uniform hashes for your key prefixes, and you  can ensure that the read/write load to each region as well as its size  is uniform across the regions in the table.

### Forced Splits

HBase also enables clients to force split an online table from the  client side. For example, the HBase shell can be used to split all  regions of the table, or split a region, optionally by supplying a split  point.

```
hbase(main):024:0> split 'b07d0034cbe72cb040ae9cf66300a10c', 'b'
0 row(s) in 0.1620 seconds
```

With careful monitoring of your HBase load distribution, if you see  that some regions are getting uneven loads, you may consider manually  splitting those regions to even-out the load and improve throughput.  Another reason why you might want to do manual splits is when you see  that the initial splits for the region turns out to be suboptimal, and  you have disabled automated splits. That might happen for example, if  the data distribution changes over time.

### How Region Splits are implemented

As write requests are handled by the region server, they accumulate  in an in-memory storage system called the “memstore”. Once the memstore  fills, its content are written to disk as additional store files. This  event is called a “memstore flush”. As store files accumulate, the  RegionServer will “compact” them into combined, larger files. After each  flush or compaction finishes, a region split request is enqueued if the  RegionSplitPolicy decides that the region should be split into two.  Since all data files in HBase are immutable, when a split happens, the  newly created daughter regions will not rewrite all the data into new  files. Instead, they will create  small sym-link like files, named [Reference](http://hbase.apache.org/apidocs/org/apache/hadoop/hbase/io/Reference.html) files,  which point to either top or bottom part of the parent store file  according to the split point. The reference file will be used just like a  regular data file, but only half of the records. The region can only be  split if there are no more references to the immutable data files of  the parent region. Those reference files are cleaned gradually by  compactions, so that the region will stop referring to its parents  files, and can be split further.

Although splitting the region is a local decision made at the  RegionServer, the split process itself must coordinate with many actors.  The RegionServer notifies the Master before and after the split,  updates the .META. table so that clients can discover the new daughter  regions, and rearranges the directory structure and data files in HDFS.  Split is a multi task process. To enable rollback in case of an error,  the RegionServer keeps an in-memory journal about the execution state.  The steps taken by the RegionServer to execute the split are illustrated  by Figure 1. Each step is labeled with its step number. Actions from  RegionServers or Master are shown in red, while actions from the clients  are show in green.
 [![hbase](/img/hbase.jpg)](https://2xbbhjxc6wk3v21p62t8n4d4-wpengine.netdna-ssl.com/wp-content/uploads/2013/02/hbase.jpg)

\1. RegionServer decides locally to split the region, and prepares the  split. As a first step, it creates a znode in zookeeper under  /hbase/region-in-transition/region-name in SPLITTING state.
 \2. The Master learns about this znode, since it has a watcher for the parent region-in-transition znode.
 \3. RegionServer creates a sub-directory named “.splits” under the parent’s region directory in HDFS.
  \4. RegionServer closes the parent region, forces a flush of the cache  and marks the region as offline in its local data structures. At this  point, client requests coming to the parent region will throw  NotServingRegionException. The client will retry with some backoff.
  \5. RegionServer create the region directories under .splits directory,  for daughter regions A and B, and creates necessary data structures.  Then it splits the store files, in the sense that it creates two [Reference](http://hbase.apache.org/apidocs/org/apache/hadoop/hbase/io/Reference.html) files per store file in the parent region. Those reference files will point to the parent regions files.
 \6. RegionServer creates the actual region directory in HDFS, and moves the reference files for each daughter.
  \7. RegionServer sends a Put request to the .META. table, and sets the  parent as offline in the .META. table and adds information about  daughter regions. At this point, there won’t be individual entries in  .META. for the daughters. Clients will see the parent region is split if  they scan .META., but won’t know about the daughters until they appear  in .META.. Also, if this Put to .META. succeeds, the parent will be  effectively split. If the RegionServer fails before this RPC succeeds,  Master and the next region server opening the region will clean dirty  state about the region split. After the .META. update, though, the  region split will be rolled-forward by Master.
 \8. RegionServer opens daughters in parallel to accept writes.
  \9. RegionServer adds the daughters A and B to .META. together with  information that it hosts the regions. After this point, clients can  discover the new regions, and issue requests to the new region. Clients  cache the .META. entries locally, but when they make requests to the  region server or .META., their caches will be invalidated, and they will  learn about the new regions from .META..
 \10. RegionServer updates  znode /hbase/region-in-transition/region-name in zookeeper to state  SPLIT, so that the master can learn about it. The balancer can freely  re-assign the daughter regions to other region servers if it chooses so.
  \11. After the split, meta and HDFS will still contain references to the  parent region. Those references will be removed when compactions in  daughter regions rewrite the data files. Garbage collection tasks in the  master periodically checks whether the daughter regions still refer to  parents files.  If not, the parent region will be removed.

### Region Merges

Unlike region splitting, HBase at this point does not provide usable  tools for merging regions. Although there are HMerge, and Merge tools,  they are not very suited for general usage. There currently is no  support for online tables, and auto-merging functionality. However, with  issues like [OnlineMerge](https://issues.apache.org/jira/browse/HBASE-7403), [Master initiated automatic region merge](https://issues.apache.org/jira/browse/HBASE-7629)s, [ZK-based Read/Write locks for table operations](https://issues.apache.org/jira/browse/HBASE-7305), we are working to stabilize region splits and enable better support for region merges. Stay tuned!

### Conclusion

As you can see, under-the-hood HBase does a lot of housekeeping to  manage regions splits and do automated sharding through regions.  However, HBase also provides the necessary tools around region  management, so that you can manage the splitting process. You can also  control precisely when and how region splits are happening via a  RegionSplitPolicy.

The number of regions in a table, and how those regions are split are  crucial factors in understanding, and tuning your HBase cluster load.  If you can estimate your key distribution, you should create the table  with pre-splitting to get the optimum initial load performance. You can  start with a lower multiple of number of region servers as a starting  point for initial number of regions, and let automated splitting take  over. If you cannot correctly estimate the initial split points, it is  better to just create the table with one region, and start some initial  load with automated splitting, and use  IncreasingToUpperBoundRegionSplitPolicy. However, keep in mind that, the  total number of regions will stabilize over time, and the current set  of region split points will be determined from the data that the table  has received so far. You may want to monitor the load distribution  across the regions at all times, and if the load distribution changes  over time, use manual splitting, or set more aggressive region split  sizes. Lastly, you can try out the upcoming online merge feature and  contribute your use case.





# Configuring HBase Memstore: What You Should Know

[原文在此](https://sematext.com/blog/hbase-memstore-what-you-should-know/)

In this post we discuss what HBase users should know about one of the internal parts of HBase: the Memstore. Understanding underlying processes related to Memstore will help to configure HBase cluster towards better performance.

## HBase Memstore

Let’s take a look at the write and read paths in HBase to understand what Memstore is, where how and why it is used.

[![Memstore Usage in HBase Read/Write Paths](/img/hbase_read_write_path2_small.png)](https://sematext.com/wp-content/uploads/2012/07/hbase_read_write_path2_small.png)Memstore Usage in HBase Read/Write Paths

(picture was taken from [Intro to HBase Internals and Schema Design presentation](http://blog.sematext.com/2012/07/09/intro-to-hbase-internals-and-schema-desig/))

When RegionServer (RS) receives write request, it directs the request to specific Region. Each Region stores set of rows. Rows data can be separated in multiple column families (CFs). Data of particular CF is stored in HStore which consists of Memstore and a set of HFiles. Memstore is kept in RS main memory, while HFiles are written to HDFS. When write request is processed, data is first written into the Memstore. Then, when certain thresholds are met (obviously, main memory is well-limited) Memstore data gets flushed into HFile.

The main reason for using Memstore is the need to store data on DFS ordered by row key. As HDFS is designed for sequential reads/writes, with no file modifications allowed, HBase cannot efficiently write data to disk as it is being received: the written data will not be sorted (when the input is not sorted) which means not optimized for future retrieval. To solve this problem HBase buffers last received data in memory (in Memstore), “sorts” it before flushing, and then writes to HDFS using fast sequential writes. Note that in reality HFile is not just a simple list of sorted rows, it is [much more than that](http://www.cloudera.com/blog/2012/06/hbase-io-hfile-input-output/).

Apart from solving the “non-ordered” problem, Memstore also has other benefits, e.g.:

- It acts as a in-memory cache which keeps recently added data. This is useful in numerous cases when last written data is accessed more frequently than older data
- There are certain optimizations that can be done to rows/cells when they are stored in memory before writing to persistent store. E.g. when it is configured to store one version of a cell for certain CF and Memstore contains multiple updates for that cell, only most recent one can be kept and older ones can be omitted (and never written to HFile).

Important thing to note is that **every Memstore flush creates one HFile** per CF.

On the reading end things are simple: HBase first checks if requested data is in Memstore, then goes to HFiles and returns merged result to the user.

## What to Care about

There are number of reasons HBase users and/or administrators should be aware of what Memstore is and how it is used:

- There are number of configuration options for Memstore one can use to achieve better performance and avoid issues. HBase will not adjust settings for you based on usage pattern.
- Frequent Memstore flushes can affect reading performance and can bring additional load to the system
- The way Memstore flushes work may affect your schema design

Let’s take a closer look at these points.

### Configuring Memstore Flushes

Basically, there are two groups of configuraion properties (leaving out region pre-close flushes):

- First determines when flush should be triggered
- Second determines when flush should be triggered *and updates should be blocked during flushing*

First  group is about triggering “regular” flushes which happen in parallel with serving write requests. The properties for configuring flush thresholds are:

- hbase.hregion.memstore.flush.size

```
<property>
 <name>hbase.hregion.memstore.flush.size</name>
 <value>134217728</value>
 <description>
 Memstore will be flushed to disk if size of the memstore
 exceeds this number of bytes. Value is checked by a thread that runs
 every hbase.server.thread.wakefrequency.
 </description>
</property>
```

- base.regionserver.global.memstore.lowerLimit

```
<property>
 <name>hbase.regionserver.global.memstore.lowerLimit</name>
 <value>0.35</value>
 <description>Maximum size of all memstores in a region server before
 flushes are forced. Defaults to 35% of heap.
 This value equal to hbase.regionserver.global.memstore.upperLimit causes
 the minimum possible flushing to occur when updates are blocked due to
 memstore limiting.
 </description>
</property>
```

Note that the first setting is the size *per Memstore*. I.e. when you define it you should take into account the number of regions served by each RS. When number of RS grows (and you configured the setting when there were few of them) Memstore flushes are likely to be triggered by the second threshold earlier.

Second group of settings is for safety reasons: sometimes write load is so high that flushing cannot keep up with it and since we  don’t want memstore to grow without a limit, in this situation **writes are blocked unless memstore has “manageable” size**. These thresholds are configured with:

- hbase.regionserver.global.memstore.upperLimit

```
<property>
 <name>hbase.regionserver.global.memstore.upperLimit</name>
 <value>0.4</value>
 <description>Maximum size of all memstores in a region server before new
 updates are blocked and flushes are forced. Defaults to 40% of heap.
 Updates are blocked and flushes are forced until size of all memstores
 in a region server hits hbase.regionserver.global.memstore.lowerLimit.
 </description>
</property>
```

- hbase.hregion.memstore.block.multiplier

```
<property>
 <name>hbase.hregion.memstore.block.multiplier</name>
 <value>2</value>
 <description>
 Block updates if memstore has hbase.hregion.block.memstore
 time hbase.hregion.flush.size bytes. Useful preventing
 runaway memstore during spikes in update traffic. Without an
 upper-bound, memstore fills such that when it flushes the
 resultant flush files take a long time to compact or split, or
 worse, we OOME.
 </description>
</property>
```

Blocking writes on particular RS on its own may be a big issue, but there’s more to that. Since in HBase by design *one Region is served by single RS* when write load is evenly distributed over the cluster (over Regions) **having one such “slow” RS will make the whole cluster work slower** (basically, at its speed).

**Hint**: watch for Memstore Size and Memstore Flush Queue size. Memstore Size ideally should not reach upper Memstore limit and Memstore Flush Queue size should not constantly grow.

### Frequent Memstore Flushes

Since we want to avoid blocking writes it may seem a good approach to flush earlier when we are far from “writes-blocking” thresholds. However, this will cause too frequent flushes which can affect read performance and bring additional load to the cluster.

Every time Memstore flush happens one HFile created for each CF. Frequent flushes may create tons of HFiles. Since during reading HBase will have to look at many HFiles, the read speed can suffer.

To prevent opening too many HFiles and avoid read performance deterioration there’s HFiles compaction process. HBase will periodically (when certain *configurable* thresholds are met) compact multiple smaller HFiles into a big one. Obviously, the more files created by Memstore flushes, the more work (extra load) for the system. More to that: while compaction process is usually performed in parallel with serving other requests, **when HBase cannot keep up with compacting HFiles** (yes, there are configured thresholds for that too;)) **it will block writes on RS** again. As mentioned above, this is highly undesirable.

**Hint**: watch for Compaction Queue size on RSs. In case it is constantly growing you should take actions before it will cause problems.

More on HFiles creation & Compaction can be found [here](http://outerthought.org/blog/465-ot.html).

So, ideally Memstore should use as much memory as it can (as configured, not all RS heap: there are also in-memory caches), but not cross the upper limit. This picture (screenshot was taken from our [SPM monitoring service](https://sematext.com/spm/index.html)) shows somewhat good situation:

[![Memstore Size: Good Situation](/img/memstore_size.png)](https://sematext.com/wp-content/uploads/2012/07/memstore_size.png)Memstore Size: Good Situation

“Somewhat”, because we could configure lower limit to be closer to upper, since we barely ever go over it.

### Multiple Column Families & Memstore Flush

Memstores of all column families are flushed together (this [might change](https://issues.apache.org/jira/browse/HBASE-3149)). This means creating N HFiles per flush, one for each CF. Thus, uneven data amount in CF will cause too many HFiles to be created: when Memstore of one CF reaches threshold all Memstores of other CFs are flushed too. As stated above too frequent flush operations and too many HFiles may affect cluster performance.

**Hint**: in many cases having one CF is the best schema design.

### HLog (WAL) Size & Memstore Flush

On RegionServer write/read paths picture above you may also noticed a Write-ahead Log (WAL) where data is getting written by default. It contains all the edits of RegionServer which were written to Memstore but were not flushed into HFiles. As data in Memstore is not persistent we need WAL to recover from RegionServer failures. When RS crushes and data which was stored in Memstore and wasn’t flushed is lost, WAL is used to replay these recent edits.

When WAL (in HBase it is called HLog) grows very big, it may take a lot of time to replay it. For that reason there are certain limits for WAL size, which when reached cause Memstore to flush. Flushing Memstores decreases WAL as we don’t need to keep in WAL edits which were written to HFiles (persistent store). This is configured by two properties: hbase.regionserver.hlog.blocksize and hbase.regionserver.maxlogs. As you probably figured out, maximum WAL size is determined by hbase.regionserver.maxlogs * hbase.regionserver.hlog.blocksize (2GB by default). When this size is reached, Memstore flushes are triggered. *So, when you increase Memstore size and adjust other Memstore settings you need to adjust HLog ones as well*. Otherwise **WAL size limit may be hit first and you will never utilize all the resources dedicated to Memstore**. Apart from that, triggering of Memstore flushes by reaching WAL limit is not the best way to trigger flushing, as it may create “storm” of flushes by trying to flush many Regions at once when written data is well distributed across Regions.

**Hint**: keep hbase.regionserver.hlog.blocksize * hbase.regionserver.maxlogs just a bit above hbase.regionserver.global.memstore.lowerLimit * HBASE_HEAPSIZE.

### Compression & Memstore Flush

With HBase it is advised to compress the data stored on HDFS (i.e. HFiles). In addition to saving on space occupied by data this reduces the disk & network IO significantly. Data is compressed when it is written to HDFS, i.e. when Memstore flushes. **Compression should not slow down flushing process a lot, otherwise we may hit many of the problems** above, like blocking writes caused by Memstore being too big (hit upper limit) and such.

**Hint**: when choosing compression type favor compression *speed* over compression ratio. SNAPPY showed to be a good choice here.
>>>>>>> 307e7e40016dfa3113ae50ec97a55e212278b27c
