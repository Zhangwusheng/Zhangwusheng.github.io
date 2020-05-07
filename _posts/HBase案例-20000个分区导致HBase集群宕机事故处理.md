## HBase案例 | 20000个分区导致HBase集群宕机事故处理

原创 大数据手稿笔记 [大数据技术架构](javascript:void(0);) *2019-05-21*

这是几个月前遇到的一次HBase集群宕机事件，今天重新整理下事故分析报告。概况的说是业务方的一个10节点HBase集群支撑百TB级别的数据量，集群region数量达 23000+，最终集群支持不住业务压力，带来了一次惨痛的宕机事件。

# 事故现场

项目上大数据平台拥有一个10个节点的HBase集群，主要业务表有十几张，每张表创建的时候做了包含10个region的预分区，并使这些分区均匀分布在了不同regionserver上。经过一段时间的运行，由于业务量比较大，集群region分区数量已经达到23000之多了，平均每个regionserver节点分区数量在2300个左右。regionserver JVM 配置为 32G。

某一天灾难降临了，集群regionserver节点全部宕机，读写请求异常，正常业务被中断。其实在这之前，写请求已经变慢了，然而各种原因只做了代码层面的简单优化，没有任何其他方面的调整。

# 宕机日志



集群宕机后第一时间做了日志检查，希望通过日志分析定位到问题再做处理。关键日志信息如下

regionserver 日志：

```
WARN org.apache.hadoop.hdfs.DFSClient: DataStreamer Exception
java.io.IOException: Unable to create new block.
        at org.apache.hadoop.hdfs.DFSOutputStream$DataStreamer.nextBlockOutputStream(DFSOutputStream.java:1633)
        at org.apache.hadoop.hdfs.DFSOutputStream$DataStreamer.run(DFSOutputStream.java:772)
WARN org.apache.hadoop.hdfs.DFSClient: Could not get block locations. Source file "/hbase/data/db1/xxx_position/d9fa4a857e668b63db02a5e3340354de/recovered.edits/0000000000023724243.temp" - Aborting...
WARN org.apache.hadoop.hdfs.DFSClient: Excluding datanode DatanodeInfoWithStorage[xx.xx.xx.xx:50010,DS-bae224ff-1680-4969-afd1-1eeae878783b,DISK]
INFO org.apache.hadoop.hdfs.DFSClient: Exception in createBlockOutputStream
java.io.IOException: Bad connect ack with firstBadLink as xx.xx.xx.xx:50010
        at org.apache.hadoop.hdfs.DFSOutputStream$DataStreamer.createBlockOutputStream(DFSOutputStream.java:1722)
        at org.apache.hadoop.hdfs.DFSOutputStream$DataStreamer.nextBlockOutputStream(DFSOutputStream.java:1620)
        at org.apache.hadoop.hdfs.DFSOutputStream$DataStreamer.run(DFSOutputStream.java:772)

···

INFO org.apache.hadoop.hbase.wal.WALSplitter: 3 split writers finished; closing...
INFO org.apache.hadoop.hdfs.DFSClient: Exception in createBlockOutputStream
java.io.EOFException: Premature EOF: no length prefix available
        at org.apache.hadoop.hdfs.protocolPB.PBHelper.vintPrefixed(PBHelper.java:2272)
        at org.apache.hadoop.hdfs.DFSOutputStream$DataStreamer.createBlockOutputStream(DFSOutputStream.java:1701)
        at org.apache.hadoop.hdfs.DFSOutputStream$DataStreamer.nextBlockOutputStream(DFSOutputStream.java:1620)
        at org.apache.hadoop.hdfs.DFSOutputStream$DataStreamer.run(DFSOutputStream.java:772)
```

datanode 日志：

```
INFO org.apache.hadoop.hdfs.server.datanode.DataNode: PacketResponder: BP-1452924002-xx.xx.xx.xx-1527602017139:blk_1181831924_108091843, type=HAS_DOWNSTREAM_IN_PIPELINE
java.io.EOFException: Premature EOF: no length prefix available
        at org.apache.hadoop.hdfs.protocolPB.PBHelper.vintPrefixed(PBHelper.java:2272)
        at org.apache.hadoop.hdfs.protocol.datatransfer.PipelineAck.readFields(PipelineAck.java:235)
        at org.apache.hadoop.hdfs.server.datanode.BlockReceiver$PacketResponder.run(BlockReceiver.java:1286)
        at java.lang.Thread.run(Thread.java:748)
INFO org.apache.hadoop.hdfs.server.datanode.DataNode: Exception for BP-1452924002-xx.xx.xx.xx-1527602017139:blk_1181831924_108091843
java.io.IOException: Premature EOF from inputStream
        at org.apache.hadoop.io.IOUtils.readFully(IOUtils.java:201)
        at org.apache.hadoop.hdfs.protocol.datatransfer.PacketReceiver.doReadFully(PacketReceiver.java:213)
        at org.apache.hadoop.hdfs.protocol.datatransfer.PacketReceiver.doRead(PacketReceiver.java:134)
        at org.apache.hadoop.hdfs.protocol.datatransfer.PacketReceiver.receiveNextPacket(PacketReceiver.java:109)
        at org.apache.hadoop.hdfs.server.datanode.BlockReceiver.receivePacket(BlockReceiver.java:500)
        at org.apache.hadoop.hdfs.server.datanode.BlockReceiver.receiveBlock(BlockReceiver.java:896)
        at org.apache.hadoop.hdfs.server.datanode.DataXceiver.writeBlock(DataXceiver.java:808)
        at org.apache.hadoop.hdfs.protocol.datatransfer.Receiver.opWriteBlock(Receiver.java:169)
        at org.apache.hadoop.hdfs.protocol.datatransfer.Receiver.processOp(Receiver.java:106)
        at org.apache.hadoop.hdfs.server.datanode.DataXceiver.run(DataXceiver.java:246)
        at java.lang.Thread.run(Thread.java:748)
WARN org.apache.hadoop.hdfs.server.datanode.DataNode: IOException in BlockReceiver.run():
java.io.IOException: Broken pipe
        at sun.nio.ch.FileDispatcherImpl.write0(Native Method)
        at sun.nio.ch.SocketDispatcher.write(SocketDispatcher.java:47)
        at sun.nio.ch.IOUtil.writeFromNativeBuffer(IOUtil.java:93)
        at sun.nio.ch.IOUtil.write(IOUtil.java:65)
        at sun.nio.ch.SocketChannelImpl.write(SocketChannelImpl.java:471)
        at org.apache.hadoop.net.SocketOutputStream$Writer.performIO(SocketOutputStream.java:63)
        at org.apache.hadoop.net.SocketIOWithTimeout.doIO(SocketIOWithTimeout.java:142)
        at org.apache.hadoop.net.SocketOutputStream.write(SocketOutputStream.java:159)
        at org.apache.hadoop.net.SocketOutputStream.write(SocketOutputStream.java:117)
        at java.io.BufferedOutputStream.flushBuffer(BufferedOutputStream.java:82)
        at java.io.BufferedOutputStream.flush(BufferedOutputStream.java:140)
        at java.io.DataOutputStream.flush(DataOutputStream.java:123)
        at org.apache.hadoop.hdfs.server.datanode.BlockReceiver$PacketResponder.sendAckUpstreamUnprotected(BlockReceiver.java:1533)
        at org.apache.hadoop.hdfs.server.datanode.BlockReceiver$PacketResponder.sendAckUpstream(BlockReceiver.java:1470)
        at org.apache.hadoop.hdfs.server.datanode.BlockReceiver$PacketResponder.run(BlockReceiver.java:1383)
        at java.lang.Thread.run(Thread.java:748)

···

WARN org.apache.hadoop.hdfs.server.datanode.DataNode: {host}:50010:DataXceiverServer:
java.io.IOException: Xceiver count 4097 exceeds the limit of concurrent xcievers: 4096
        at org.apache.hadoop.hdfs.server.datanode.DataXceiverServer.run(DataXceiverServer.java:149)
        at java.lang.Thread.run(Thread.java:748)
WARN org.apache.hadoop.hdfs.server.datanode.DataNode: {host}:50010:DataXceiverServer:
java.io.IOException: Xceiver count 4098 exceeds the limit of concurrent xcievers: 4096
        at org.apache.hadoop.hdfs.server.datanode.DataXceiverServer.run(DataXceiverServer.java:149)
        at java.lang.Thread.run(Thread.java:748)
```

# 定位分析

我们知道HBase底层存储是基于hdfs的，region其实是HBase的逻辑存储单元，实际对应了hdfs上的很多hfile文件。从宕机日志给到我们的信息'Unable to create new block'以及'Bad connect ack with firstBadLink as xx.xx.xx.xx:50010'可以看出，实际应该是HBase在写hdfs的时候出了问题。hdfs在创建一个文件或分配一个block的时候，会打开一个数据输出流DataOutputStream，然后调用线程池里的线程通过pipeline传输数据执行写操作，如果这个过程出现问题就会抛出异常。



检查HBase正常日志可以确认，HBase flush操作非常频繁。进一步确认发现是所有region的memstore总大小不断达到 global memstore 大小，因此不断触发flush机制刷写磁盘。不难想到，由于集群region数量过多，regionserver的堆内存有限，导致每个region的memstore可以申请到的空间缩小，写缓存空间越小则刷写磁盘越频繁。实际确认下来每个memstore大小达到10M左右就会flush生成一个hfile文件，这其实是非常可怕的。



因此，业务数据实时高频写入时，频繁的flush产生了非常多的hfile文件，HBase为了查询优化又会执行compaction合并这些较小的hfile文件，这里主要触发的是minor compaction。持续的flush与compaction给hdfs造成了非常大的压力，导致datanode负载过高，超出了datanode并发处理数据的能力，异常信息'Xceiver count 4097 exceeds the limit of concurrent xcievers: 4096'便体现了这一点。集群regionserver写hdfs发生了异常，最终导致了这次宕机。

# 宕机处理



检查HBase参数配置，并参考宕机时的报错信息，参数上做了一些调整，如下



**1、****dfs.datanode.max.transfer.threads**

datanode传输数据的最大线程数，之前的名称是 dfs.datanode.max.xcievers，默认4096，调整到了32768。这个参数控制着datanode传输数据、文件操作的最大并行度，类似datanode上的最大文件句柄数。通常文件操作压力比较大的场景下需要调大该参数，例如执行一个比较重的MapReduce任务、频繁的HBase flush刷写磁盘等。针对这个参数调整，后来想了想直接调整到32768这种8倍的幅度有点大，建议先调整到2倍、4倍。



**2、dfs.datanode.handler.count**

datanode处理请求的线程数，从3调整到了8。这个参数原生Hadoop默认为10，这边CDH初始值只设置了3，对于读写请求比较大的场景，建议增大该参数以支持更大的并发请求。



**3、hbase.regionserver.thread.compaction.small**

regionserver服务端做small compaction的线程数，默认1，调整到了5。这个参数的调整主要是考虑到HBase flush刷写比较频繁，为了避免小文件持续增加，增大该参数加快合并小文件的compaction操作。建议调整范围保持在2~5，避免消耗过多的服务端CPU、Mem资源。



**4、hbase.regionserver.global.memstore.size.lower.limit**

memstore总大小下限值，从0.38调整到了0.95。这个参数值是 hbase.regionserver.global.memstore.size的比例，memstore总大小超过该比例就会发生强制flush，值越小触发flush的可能性越大。这个参数官方默认0.95，这边初始配置只有0.38，因此做了相应调整。



**5、jvm内存调整**

regionserver jvm堆大小，从32G最终调整到了64G。这里主要是考虑到region分区数量比较多，业务TPS比较高，需要更多的写缓存即memstore空间。这次没有调整读写缓存的比例，但实际上，如果在重写场景下、或者不需要使用太多读缓存的时候，可以调大写缓存、减小读缓存，相应参数即是hbase.regionserver.global.memstore.size与hfile.block.cache.size。



调整完参数后首先重启hdfs，hdfs由于数据块比较多，因此重启时间也比较长，hdfs恢复后启动HBase。经过参数调整，HBase继续线上正常使用，但考虑到业务压力，技术方案上做了一些调整，最终将部分数据直接放于HDFS之上，并建议业务方及时扩展集群。



# Master初始化超时

重启HBase过程中又遇到了active Master初始化失败的问题，然后从日志角度再次做了排查，最后也做了参数调整。

**1/错误日志**

日志1：

```
ERROR org.apache.hadoop.hbase.master.HMaster: Master failed to complete initialization after 900000ms. Please consider submitting a bug report including a thread dump of this process.
```

日志2：

```
FATAL org.apache.hadoop.hbase.master.HMaster Failed to become active master
java.io.IOException: Timedout 300000ms waiting for namespace table to be assigned
    at org.apache.hadoop.hbase.master.TableNamespaceManager.start(TableNamespaceManager.java:106)
    at org.apache.hadoop.hbase.master.HMaster.initNamespace(HMaster.java:1057)
    at org.apache.hadoop.hbase.master.HMaster.finishActiveMasterInitialization(HMaster.java:844)
    at org.apache.hadoop.hbase.master.HMaster.access$500(HMaster.java:194)
    at org.apache.hadoop.hbase.master.HMaster$1.run(HMaster.java:1834)
    at java.lang.Thread.run(Thread.java:748)
FATAL org.apache.hadoop.hbase.master.HMaster Master server abort: loaded coprocessors are: []
FATAL org.apache.hadoop.hbase.master.HMaster Unhandled exception. Starting shutdown.
java.io.IOException: Timedout 300000ms waiting for namespace table to be assigned
    at org.apache.hadoop.hbase.master.TableNamespaceManager.start(TableNamespaceManager.java:106)
    at org.apache.hadoop.hbase.master.HMaster.initNamespace(HMaster.java:1057)
    at org.apache.hadoop.hbase.master.HMaster.finishActiveMasterInitialization(HMaster.java:844)
    at org.apache.hadoop.hbase.master.HMaster.access$500(HMaster.java:194)
    at org.apache.hadoop.hbase.master.HMaster$1.run(HMaster.java:1834)
    at java.lang.Thread.run(Thread.java:748)
```

**2/定位原因**

HBase的启动是Master把所有region批量assign到不同regionserver并open的过程，所有region online完成才算结束。如果region数量过多就会导致这个过程时间比较长，默认Master初始化超时时间是900000 ms即15分钟，如果15分钟初始化工作不能完成就会超时报错。



另外，Master初始化时并不会优先加载 hbase:namespace 表，加载 namespace 表有默认300000 ms即5分钟的超时时间，如果5分钟还是加载不到就会超时报错，同样会造成Master初始化失败。

**3/问题解决
**

其实有一些与Master启动相关的参数，也是通过调整这些参数，HBase最终正常启动。以下是此次调整的HBase初始化相关参数，以及部分源码：

调整：

```
<!-- namespace系统表assign超时时间，默认300000，因为region太多这里设置1天保证初始化成功 -->
<name>hbase.master.namespace.init.timeout</name> 
<value>86400000</value>

<!-- master初始化超时时间，默认900000，因为region太多这里设置1天保证初始化成功 -->
<name>hbase.master.initializationmonitor.timeout</name> 
<value>86400000</value>

<!-- bulk assign region超时时间，默认300000，设置1小时充分保证每个bulk assign都能成功 -->
<name>hbase.bulk.assignment.waiton.empty.rit</name> 
<value>3600000</value>

<!-- bulk assign每个region打开的时间，默认1000，这里也尽量设置大些比如30s -->
<name>hbase.bulk.assignment.perregion.open.time</name> 
<value>30000</value>
```

源码：

```
@InterfaceAudience.LimitedPrivate(HBaseInterfaceAudience.TOOLS)
@SuppressWarnings("deprecation")
public class HMaster extends HRegionServer implements MasterServices, Server {
  private static final Log LOG = LogFactory.getLog(HMaster.class.getName());

  /**
   * Protection against zombie master. Started once Master accepts active responsibility and
   * starts taking over responsibilities. Allows a finite time window before giving up ownership.
   */
  private static class InitializationMonitor extends HasThread {
    /** The amount of time in milliseconds to sleep before checking initialization status. */
    public static final String TIMEOUT_KEY = "hbase.master.initializationmonitor.timeout";
    public static final long TIMEOUT_DEFAULT = TimeUnit.MILLISECONDS.convert(15, TimeUnit.MINUTES);

    /**
     * When timeout expired and initialization has not complete, call {@link System#exit(int)} when
     * true, do nothing otherwise.
     */
    public static final String HALT_KEY = "hbase.master.initializationmonitor.haltontimeout";
    public static final boolean HALT_DEFAULT = false;

    private final HMaster master;
    private final long timeout;
    private final boolean haltOnTimeout;
```

# 小结

本次HBase集群宕机可以说是典型的小集群过载问题。业务数据量比较大导致HBase分区过多，实时数据的高频写入使得HBase做频繁的刷写与合并操作，给hdfs造成非常大的压力，datanode线程池被打满，写hdfs失败造成了HBase集群宕机。



经过这次事故处理总结出几点经验，首先，前期要根据业务量做合理的集群规划，如果实际业务导致集群压力还是很大的话要考虑及时水平扩展集群；其次，如果硬件条件有限，业务对实时要求不苛刻的话，在写HBase方面可以做一些调整，比如离线写文件再通过bulkload批量写入的方式，情况可能会好一点；最后，HBase集群一定要充分运维，没有运维的集群存在安全隐患。

 ![img](data:image/gif;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQImWNgYGBgAAAABQABh6FO1AAAAABJRU5ErkJggg==)

一个进阶的大数据技术交流学习公众号，死磕大数据与分布式系统，分享NoSQL数据库、存储计算引擎、消息中间件等。长按二维码关注：



![img](data:image/gif;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQImWNgYGBgAAAABQABh6FO1AAAAABJRU5ErkJggg==)

阅读 348

 在看7

![img](http://wx.qlogo.cn/mmopen/5MZd3mEBia6JFestg7UFfUguXAfSZLHP1NhJmiacppc0eR0azHKnZ9Jz9d4pQXoTD9rgwu81cCHEnZEuBpzOibQZqTEE3XvJaub/132)

写下你的留言

**精选留言**

-  1

  **挑灯流浪。**

  ![img](http://wx.qlogo.cn/mmopen/4vgMQAI1fgKhSMaW7gMURvU6oGN9sXDwe1ib8NFxNEtMhszDibm3Z4iabLqFyTdNy7IXBk7vR4lvUMML6s6B4HzpftPoamWRuBL/96)

  

  既让马儿跑，还不给马儿吃草