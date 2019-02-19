# hbase元数据恢复（meta表）

2018年01月15日 15:20:57 [anyking0520](https://me.csdn.net/anyking0520) 阅读数：1388



meta表一直in transition，master起不来，日志中报错： zookeeper.MetaTableLocator: Failed verification of hbase:meta

解决方法如下：



1.删除zookeeper信息

rmr /hbase-unsecure

2.保存hbase数据

hadoop fs -mv /apps/hbase/data/data/default/* /backup

3.删除hbase数据

hadoop fs -rmr /apps/hbase

4.重启master

5.mv /backup/* /apps/hbase/data/data/default

6.重建meta元数据hbase hbck -repair









