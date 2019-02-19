---
layout:     post
title:     Transactions for the REST of Us
subtitle:   Transactions for the REST of Us
date:       2018-09-22
author:     老张
header-img: img/post-bg-2015.jpg
catalog: true
tags:
    - TCC
    - Transactions 
    - REST 
typora-copy-images-to: ..\img
typora-root-url: ..
---

http://www.cnblogs.com/niurougan/p/3976543.html

随笔 - 20  文章 - 1  评论 - 3
hbase meta表的结构
下面看下hbase:meta 表的结构，hbase:meta表中，保存了每个表的region地址，还有一些其他信息，例如region的名字，HRegionInfo,服务器的信息。hbase:meta表中每一行对应一个单一的region。例如我们现在创建一个表名叫"t"。hbase:meta中对应的行会像下面这个样子。

 

Row

Column Family

Column Qualifier

Value

t,,1351700811858

info

regioninfo

NAME =>
‘t,,1351700811858.
90a3b2353709773ebc2423.
04a79dcbbc90a3b23
53709773ebc2423.’,
STARTKEY => ”,
ENDKEY => ”,
ENCODED => 04a79
dcbbc90a3b23537
09773ebc2423,

 	 	
server

10.7.73.121:64782

 	 	
serverstartcode

1351986939360

 

具体含义：

rowKey:([table],[region start key],[region id]),
 

 rowkey中第一个分隔符前存的是表名；
第二分隔符前存的是region的第一个rowKey，这里两个需要注意，1.如果这个地方为空的话，表明这是table的第一个region。并且如果一个region中startkey和endkey都为空的为，表明这个table只有一个region。2.在mata表中，startkey 靠前的region会排在startkey 靠后的region前面。（Hbase中的keys是按照字段顺序来排序的）
region id就是region的id,通常来说就是region创建的时候的timestamp
regioninfo 是HRegionInfo的序列化值。
server是指服务器的地址和端口
serverstartcode 是服务开始的时候的timestamp
 

根据meta表查找key对应的region

 

当有一个key需要做put操作的时候，会先扫描meta表，找到对应region，然后进行插入操作。

例如：有一个table具有三个region,每个region的startkey分别是 空,bar,foo,如下图：

    

1 table,,1351700811858
2 table,bar,1351700819876
3 table,foo,1351700829874

如果我们需要插入key ‘baz’ ，我们能找meta表中对应的rowkey为(table,bar,1351700819876）。   

 

这个查找完之后会缓存在客户端，下次查询的时候会根据缓存来直接去访问region。

 

自动split

 

当不断的往一个table增加数据的时候，最终region会分裂。这样hbase就能保证可以横向的增长了。一个parent region会split两个child region。

在child regions 上线之前我们需要做两件事：

下线parent region
把child regions的相关信息增加到parent info中
 

首先是更新meta表中parent region的info:regioninfo列的值，然后增加两列info:splitA(top child 的HRegionInfo，这里约定top为startkey较小的HReginInfo，bottom则反),和info:splitB（bottom child 的HRegionInfo）。这个操作能保证我们能跟踪到region到底做了写什么，方便后续的操作，以及后续如果操作被迫终端了，也有个凭证，能够根据这些来恢复。最后parent region会被CatalogJanitor清理掉。

 

更新meta表

 

在更新完meta表中parent region的记录的时候，就需要把child region相关插入到meta表中，top child region 的startkey 和paretn的startkey 是一样的，这个时候regionId就发挥他的作用了，如果没有regionId，当meta表中有top region和parent region的时候，我们就知道需要选择哪个了，因为他们的startkey都一样。而我们使用timestamp作为region的id（如果top region和parent region的timestamp一样的时候，top的region id 取timestamp+1）。这样我们就能保证child region总是排在parent region之后。

 

还有一个比较重要的就是，bottom child必须要先插入到meta表，然后top child才能插入。否则就会出现，在meta表中，bottom region里面的key找到不到对应的region的情况。举个例子还是以上面的例子为基础 meta中rowkey为(table,bar,1351700819876)的region分裂成两个region的meta rowkey分别是(table,bar,1351700819810)和(table,belong,1351700819810),如果这个时候先插入top child：

 

1 table,,1351700811858
2 table,bar,1351700819876 <---- offline!
3 table,bar,1351700819810 <---- top child
4 table,foo,1351700829874
 

 

例如这个时候我需要找key为bgood,我最终会找到这里的第三行top region里面，但是top region里面并不包含bgood。bgood这个这个key是在bottom region里面的。如果先加入bottom就没有这个问题，如下 

 

table,,1351700811858
table,bar,1351700819876 <---- offline!
table,belong,1351700819810 <---- bottom child
table,foo,1351700829874
 

出错恢复 


一般来说，Hbase可以很好的恢复服务器错误，但是有时候还是会出问题的，如果在slipt的时候，regionserver出错了，或者因为其他原因导致slipt整个周期只执行了一部分。这个时候meta表可能会出错，例如有出错的region在磁盘上面，或者重复的regions等。这个时候我们可以使用hbck工具来进行修复。使用以下命令查看更多hbck的信息：

 

 /hbase/bin/hbase hbck -h
 

参考：

https://blog.safaribooksonline.com/2012/11/16/tip-2-hbase-meta-layout/ hbase：meta表

http://hbase.apache.org/book/arch.catalog.html 官方文档meta表