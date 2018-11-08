---
layout:     post
title:     hbase-architecture
subtitle:   hbase-architecture
date:       2018-09-21
author:     老张
header-img: img/post-bg-2015.jpg
catalog: true
tags:
    - hbase
    - 原理
    - 读优化
    - 写优化
    - Hbase优化
typora-copy-images-to: ..\img
typora-root-url: ..
---



# HBase Architecture – Regions, Hmaster, Zookeeper

[13 Jun, 2018](https://data-flair.training/blogs/2018/06/13/)  in [ HBase Tutorials ](https://data-flair.training/blogs/category/hbase/)  by [Data Flair](https://data-flair.training/blogs/author/dataflair-tr/)

------

https://data-flair.training/blogs/hbase-architecture/

## 1. Objective

In this [**HBase tutorial**](https://data-flair.training/blogs/hbase-tutorial/),  we will learn the concept of HBase Architecture. Moreover, we will see  the 3 major components of HBase, such as HMaster, Region Server, and  ZooKeeper. Along with this, we will see the working of HBase components,  HBase memstore, HBase compaction in Architecture of HBase. This HBase  Technology tutorial also includes the advantages and limitations of  HBase Architecture to understand it well.

So, let’s start HBase Architecture.

![HBase architecture](https://d2h0cx97tjks2p.cloudfront.net/blogs/wp-content/uploads/HBase-Architecture-01.jpg)

HBase Architecture & Components – Regions, Hmaster, Zookeeper

## 2. HBase Architecture

Basically,  there are 3 types of servers in a master-slave type of HBase  Architecture. They are HBase HMaster, Region Server, and ZooKeeper.  Let’s start with Region servers, these servers serve data for reads and  write purposes. That means clients can directly communicate with HBase  Region Servers while accessing data. Further, HBase Master process  handles the region assignment as well as DDL (create, delete tables)  operations. And finally, a part of HDFS, Zookeeper, maintains a live  cluster state.

![HBase Architecture](https://d2h0cx97tjks2p.cloudfront.net/blogs/wp-content/uploads/HBase-Components.png)

What is HBase Architecture

In  addition, the data which is managed by Region Server is further stored  in the Hadoop DataNode. And, all HBase data is stored in [**HDFS**](https://data-flair.training/blogs/apache-hadoop-hdfs-introduction-tutorial/)  files. Then for the data served by the RegionServers, Region Servers  are collocated with the HDFS DataNodes, which also enable data locality.  Here, data locality refers to putting the data close to where it is  needed. Make sure, when HBase data is written it is local, but while a  region is moved, it is not local until compaction.

Moreover, for all the physical data blocks the NameNode maintains Metadata information which comprise the files.

## 3. HBase Architecture – Regions

In  HBase Architecture, a region consists of all the rows between the start  key and the end key which are assigned to that Region. And, those  Regions which are assigned to the nodes in the HBase Cluster, is what we  call “Region Servers”. Basically, for the purpose of reads and writes  these servers serves the data. While talking about numbers, it can serve  approximately 1,000 regions. However, rows in each region in HBase are  managed in a sorted order.

![HBase Architecture](https://d2h0cx97tjks2p.cloudfront.net/blogs/wp-content/uploads/HBase-Regions.png)

HBase Architecture – Regions

These Regions of a Region Server are responsible for several things, like handling, managing, executing as well as **reads and writes HBase operations** on that set of regions. The default size of a region is 256MB, which can be configured as per requirement.

## 4. HBase HMaster

HBase  master in the architecture of HBase is responsible for region  assignment as well as DDL (create, delete tables) operations.

There are two main responsibilities of a master in HBase architecture:

![HBase Architecture](https://d2h0cx97tjks2p.cloudfront.net/blogs/wp-content/uploads/HBase-Hmaster.png)

The Architecture of HBase – HMaster

**a. Coordinating the region servers**

Basically, a master assigns Regions on startup. Also for the purpose of recovery or load balancing, it re-assigns regions.

Also, a master monitors all RegionServer instances in the HBase Cluster.

**b. Admin functions**

Moreover, it acts as an interface for creating, deleting and updating tables in HBase.

## 5. ZooKeeper: The Coordinator

However,  to maintain server state in the HBase Cluster, HBase uses ZooKeeper as a  distributed coordination service. Basically, which servers are alive  and available is maintained by Zookeeper, and also it provides server  failure notification. Moreover, in order to guarantee common shared  state, Zookeeper uses consensus. 

![HBase Architecture](https://d2h0cx97tjks2p.cloudfront.net/blogs/wp-content/uploads/Zookeeper.png)

HBase Architecture – Zookeeper

## 6. How HBase Components Works?

As  we know, to coordinate shared state information for members of  distributed systems, HBase uses Zookeeper. Further, active HMaster, as  well as Region servers, connect with a session to ZooKeeper. Then for  active sessions, ZooKeeper maintains ephemeral nodes by using  heartbeats. Ephemeral nodes mean znodes which exist as long as the  session which created the znode is active and then znode is deleted when  the session ends.

![HBase Architecture](https://d2h0cx97tjks2p.cloudfront.net/blogs/wp-content/uploads/How-the-Components-Work-Together.png)

HBase Architecture – working of Components

In  addition, each Region Server in HBase Architecture produces an  ephemeral node. Further, to discover available region servers, the  HMaster monitors these nodes. Also for server failures, it monitors  these nodes. Moreover, to make sure that only one master is active,  Zookeeper determines the first one and uses it. As a process, the active  HMaster sends heartbeats to Zookeeper, however, the one which is not  active listens for notifications of the active HMaster failure.

Although,  the session gets expired and the corresponding ephemeral node is also  deleted if somehow a region server or the active HMaster fails to send a  heartbeat. Then for updates, listeners will be notified of the deleted  nodes. Further, the active HMaster will recover region servers, as soon  as it listens for region servers on failure. Also, when inactive one  listens for the failure of active HMaster, the inactive HMaster becomes  active, if an active HMaster fails.

## 7. HBase – Read or Write

When the first time a client **reads or writes to HBase**:

- Basically, the client gets the Region server which helps to hosts the META Table from ZooKeeper.
- Moreover,  in order to get the region server corresponding to the row key, the  client will query the.META. server, it wants to access. However, along  with the META Table location, the client caches this information.
- Also, from the corresponding Region Server, it will get the Row.

## 8. HBase META Table

 META Table is a special HBase Catalog Table. Basically, it holds the location of the regions in the HBase Cluster. 

- It keeps a list of all Regions in the system.
- Structure of the .META. table is as follows:

1. **Key:** region start key, region id
2.  **Values:** RegionServer

- It is like a binary tree.

## 9. Region Server Components

There are following components of a Region Server, which runs on an HDFS data node:

- **WAL**

It  is a file on the distributed file system. Basically, to store new data  that hasn’t yet been persisted to permanent storage, we use the WAL.  Moreover, we also use it for recovery in the case of failure.

- **BlockCache**

It  is the read cache. The main role of BlockCache is to store the  frequently read data in memory. And also, the data which is least  recently used data gets evicted when full.

- **MemStore**

It  is the write cache. The main role of MemStore is to store new data  which has not yet been written to disk. Also, before writing to disk, it  gets sorted.

- **Hfiles**

These files store the rows as sorted KeyValues on disk.

## 10. HBase Write Steps (1)

The first step is to write the data to the write-ahead log, while the client issues a put request:

–  To the end of the WAL file, all the edits are appended which is stored on disk.

–  In case a server crashes, the WAL is used, to recover not-yet-persisted data.

## 11. HBase Write Steps (2)

As  soon as the data is written to the WAL, it is placed in the MemStore.  After that acknowledgment of the put, the request returns to the client.

## 12. HBase MemStore

It  updates in memory as sorted KeyValues, the same as it would be stored  in an HFile. There is one MemStore per column family. The updates are  sorted per column family.

## 13. Compaction in HBase

[![HBase Architecture](https://d2h0cx97tjks2p.cloudfront.net/blogs/wp-content/uploads/Compaction.png)](https://d2h0cx97tjks2p.cloudfront.net/blogs/wp-content/uploads/Compaction.png)

In  order to reduce the storage and reduce the number of disks seeks needed  for a read, HBase combines HFiles. This entire process is what we call  compaction. It selects few HFiles from a region and combines them.  Compaction is of two types, such as:

- **Minor Compaction**

As  you can see in the image, HBase picks smaller HFiles automatically and  then recommits them to bigger HFiles. This process is what we call Minor  Compaction. For committing smaller HFiles to bigger HFiles, it performs  merge sort. 

- **Major Compaction**

HBase  merges and recommits the smaller HFiles of a region to a new HFile, in  Major compaction, as you can see in the image. Here, in the new HFile,  the same column families are placed together. In this process, it drops  deleted as well as expired cell.

However,  it is a possibility that input-output disks and network traffic might  get congested during this process. Hence, generally during low peak load  timings, it is scheduled.

## 14. Region Split in HBase

![HBase Architecture](https://d2h0cx97tjks2p.cloudfront.net/blogs/wp-content/uploads/Region-Split.png)

Region Split in HBase

The  region gets divided into two child regions in HBase Architecture,  whenever a region becomes large. Here each region represents exactly a  half of the parent region. Afterward, this split is reported to the  HMaster. However, until the HMaster allocates them to a new Region  Server for load balancing, this is handled by the same Region Server.

## 15. HDFS Data Replication

Basically,  primary node handles all Writes and Reads. And, HDFS replicates the  write-ahead logs as well as HFile blocks. However, these replication  process of HFile block happens automatically. Moreover, to provide the  data safety, HBase relies on HDFS because it stores its files. 

The  process is, one copy is written locally, while data is written in HDFS.  Then it is replicated to a secondary node, and after that third copy is  written to a tertiary node.

## 16. HBase Crash Recovery

- ZooKeeper notifies to the HMaster about the failure, whenever a Region Server fails.
- Afterward,  too many active Region Servers, HMaster distributes and allocates the  regions of crashed Region Server. Also, the HMaster distributes the WAL  to all the Region Servers, in order to recover the data of the MemStore  of the failed Region Server.
- Furthermore, to build the MemStore for that failed region’s column family, each Region Server re-executes the WAL.
- However,  Re-executing that WAL means updating all the change that was made and  stored in the MemStore file because, in WAL, the data is written in  timely order. 
- Therefore, the MemStore data for all column family is recovered just after all the Region Servers executes the WAL.

## 17. Advantages of HBase Architecture

There are some benefits which are offered by HBase Architecture :

**a. Strong consistency model**

– All readers will see same value, while a write returns.

**b. Scales automatically**

– While data grows too large, Regions splits automatically.

– To spread and replicate data, it uses HDFS.

**c. Built-in recovery**

– It uses Write Ahead Log for recovery.

**d. Integrated with Hadoop**

– On HBase MapReduce is straightforward.

## 18. Limitations With Apache HBase

**a. Business continuity reliability**

– Write Ahead Log replay very slow.

– Also, a slow complex crash recovery.

– Major Compaction I/O storms

So, this was all about HBase Architecture. Hope you like our explanation.

## 19. Conclusion

Hence,  in this HBase architecture tutorial, we saw the whole concept of HBase  Architecture. Moreover, we saw 3 HBase components that are region,  Hmaster, Zookeeper. Also, we discussed, advantages & limitations of  HBase Architecture. So, if any doubt occurs regarding HBase  Architecture, feel free to ask through the comment tab.